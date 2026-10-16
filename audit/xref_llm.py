# SPDX-License-Identifier: Apache-2.0
"""Phase 2b: LLM candidate generation, paper item -> Lean files -> Lean declarations.

The model locates candidates; it never says whether anything matches correctly. Each call runs
3 independent samples; all samples are stored, never merged. Every `shared_terms` entry is checked
mechanically: it must occur (case-insensitively) in the paper item text and in the cited Lean text,
else it is marked unverified.

  python audit/xref_llm.py files --dry-run          # print prompt sizes, no calls
  python audit/xref_llm.py files [--items "Lemma 8.6,Lemma 10.5"]
  python audit/xref_llm.py decls [--items ...]      # needs the files stage first

Output tables: xref_llm_files, xref_llm_decls (one row per sample x candidate).
"""
import argparse
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor, as_completed

import config as C
import llm
import paper_text as PT

ROOT = Path(__file__).resolve().parent.parent
DB = C.DB
SAMPLES = 3
ITEM_WORKERS = 5         # items in flight; total requests are capped by llm.AUDIT_LLM_MAX_CONCURRENCY
DOC_CHARS = 280          # module-doc excerpt per file in the catalog
NEIGHBOUR_DOC_CHARS = 700  # longer excerpt in the (much shorter) neighbour pass
STMT_CHARS = 3500        # paper statement
PROOF_CHARS = 15000      # full proof (longest is ~12k chars)
PROOF_EQ_CHARS = 3000    # numbered equations from the proof
DECL_STMT_CHARS = 350
DECL_CHUNK_TOKENS = 60000  # rough-count tokens per declaration chunk (~40k real)

SYSTEM = """You help index a Lean 4 formalization of a mathematics paper. Your job is to LOCATE where
content of a paper item is formalized. You never judge whether the formalization is correct,
faithful, complete or equivalent; do not comment on that. Return only JSON matching the requested
schema. Cite only identifiers that appear in the provided text."""

FILE_SIGNALS = ["same_concept_in_module_doc", "shared_notation_or_symbol", "shared_operator_or_object_name",
                "file_name_matches_topic", "explicit_paper_reference", "other"]
DECL_SIGNALS = ["docstring_describes_same_statement", "same_objects_in_statement", "same_bound_shape",
                "same_hypotheses_shape", "name_matches_concept", "explicit_paper_reference", "other"]

FILES_TASK = """Below is a catalog of every file in the formalization (id | path | start of its module
docstring), then one item from the paper. List up to 10 catalog files most likely to contain the Lean
formalization of this paper item's statement or of its proof's main steps. A paper item is often
spread over several files.

Return JSON:
{"candidates": [{"file_id": "F12", "signals": [...], "shared_terms": ["terms appearing in BOTH the paper
item and that file's catalog entry"], "confidence": "high" | "medium" | "low"}],
 "paper_concepts_not_found": ["key concepts of the item you could not find in any catalog entry"]}
Allowed signals: %s
If nothing plausible exists, return an empty candidates list.""" % ", ".join(FILE_SIGNALS)

NEIGHBOURS_TASK = """Some files were already identified as likely containing the Lean formalization of the paper
item below. Listed above are files connected to them by imports. List those that ALSO likely contain
formalization of this item's statement or of its proof's main steps (for example a key estimate from the
proof's numbered equations). Use the same JSON schema, with "file_id" values like "N3":
{"candidates": [{"file_id": "N3", "signals": [...], "shared_terms": [...], "confidence": "high" | "medium" | "low"}],
 "paper_concepts_not_found": [...]}
Allowed signals: %s
If none of them do, return an empty candidates list.""" % ", ".join(FILE_SIGNALS)

DECLS_TASK = """Below are declarations from Lean files that may formalize a paper item (id | kind name |
file:lines | docstring | statement start), then the paper item. List up to 12 declarations that most
likely formalize the item's statement, or a main step of its proof. Mark role "statement" for a
declaration that plays the role of the item's main conclusion, "proof_step" for a supporting result,
"definition" for a definition the item relies on.

Return JSON:
{"candidates": [{"decl_id": "D7", "role": "statement" | "proof_step" | "definition",
 "signals": [...], "shared_terms": ["terms appearing in BOTH the paper item and that declaration"],
 "confidence": "high" | "medium" | "low"}]}
Allowed signals: %s
If nothing plausible exists, return an empty candidates list.""" % ", ".join(DECL_SIGNALS)


def run_tag():
    """Model, the settings that change its output, and the run id; stored in the `model` column of every
    model-derived row, so runs coexist and reports can read one run only."""
    return f"{llm.client()[1]}|thinking={int(llm.THINKING)}|run={C.RUN_ID}"


def norm(s):
    return re.sub(r"\s+", " ", (s or "").lower())


def paper_block(it):
    stmt = (it["statement_latex"] or it["statement"])[:STMT_CHARS]
    proof = (PT.choose_proof(it)[0] if it.get("kind") != "ProofStep" else "")[:PROOF_CHARS]
    # Key proof steps often sit deep in long proofs (e.g. (10.19) in Lemma 10.5), so every numbered
    # equation of the proof is listed too.
    eqs, budget = [], PROOF_EQ_CHARS
    for label, latex in _proof_equations.get(it["label"], []):
        tex = re.sub(r"\s+", " ", re.sub(r"\$\$|\\tag\{[^}]*\}", "", latex or "")).strip()[:400]
        if budget - len(tex) < 0:
            break
        budget -= len(tex)
        eqs.append(f"{label}: {tex}")
    return (f"PAPER ITEM: {it['label']}" + (f" ({it['title']})" if it["title"] else "") +
            f"\nSection {it['section']}: {it['section_title']}; subsection {it['subsection']}: "
            f"{it['subsection_title']}\nSTATEMENT:\n{stmt}\n" + (f"PROOF:\n{proof}\n" if proof else "") +
            ("NUMBERED EQUATIONS IN THE PROOF:\n" + "\n".join(eqs) + "\n" if eqs else ""))


_proof_equations = defaultdict(list)
_nb = defaultdict(set)  # import neighbours, filled in main()


def catalog(con):
    rows = con.execute("SELECT file, module_doc FROM lean_files ORDER BY file").fetchall()
    ids, lines = {}, []
    for k, (f, doc) in enumerate(rows):
        fid = f"F{k}"
        ids[fid] = (f, doc or "")
        d = re.sub(r"^#+\s*", "", re.sub(r"\s+", " ", doc or "")).strip()[:DOC_CHARS]
        lines.append(f"{fid} | {C.rel(f)} | {d}")
    return ids, "\n".join(lines)


def verify_terms(terms, paper_text, lean_text):
    p, l = norm(paper_text), norm(lean_text)
    return [dict(term=t, in_paper=norm(t) in p, in_lean=norm(t) in l) for t in terms or [] if isinstance(t, str)]


def load_items(con, wanted):
    con.row_factory = sqlite3.Row
    items = [dict(r) for r in con.execute("SELECT * FROM paper_items ORDER BY rowid")]
    con.row_factory = None
    return [it for it in items if not wanted or it["label"] in wanted]


def import_neighbours(con):
    files = dict(con.execute("SELECT file, imports FROM lean_files").fetchall())
    mod = {Path(f).with_suffix("").as_posix().replace("/", "."): f for f in files}
    nb = defaultdict(set)
    for f, imp in files.items():
        for m in (imp or "").split():
            if m in mod:
                nb[f].add(mod[m])
                nb[mod[m]].add(f)
    return nb


def _files_pass(con, jobs, pass_name):
    """jobs: label -> (item, paper_block, prompt, ids). Runs all items, stores rows for this pass."""
    with ThreadPoolExecutor(ITEM_WORKERS) as ex:
        futs = {ex.submit(llm.complete_json, SYSTEM, j[2], SAMPLES, tag=f"files-{pass_name}:{label}"): label
                for label, j in jobs.items()}
        done = [(futs[f], f.result()) for f in as_completed(futs)]
    for label, res in done:
        it, pb, _, ids = jobs[label]
        con.execute("DELETE FROM xref_llm_files WHERE item=? AND model=? AND pass=?", (label, run_tag(), pass_name))
        for s, r in enumerate(res):
            if r is None:
                con.execute("INSERT INTO xref_llm_files (item, sample, file, model, pass) VALUES (?,?,?,?,?)",
                            (label, s, "<invalid-json>", run_tag(), pass_name))
                continue
            for c in r.get("candidates", []) or []:
                fid = c.get("file_id")
                f, doc = ids.get(fid, (f"<unknown id {fid}>", ""))
                v = verify_terms(c.get("shared_terms"), pb, f + " " + doc)
                con.execute("INSERT INTO xref_llm_files VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (label, s, f, json.dumps(c.get("signals")), json.dumps(c.get("shared_terms")),
                             sum(x["in_paper"] and x["in_lean"] for x in v), c.get("confidence"),
                             json.dumps(r.get("paper_concepts_not_found")), run_tag(), pass_name))
        con.commit()
        print(f"{pass_name} {label}", [len((r or {}).get("candidates", []) or []) for r in res])


def stage_files(con, items, dry, neighbour_pass=False, robust_pool=False):
    """Pass 1: whole catalog. Pass 2: import neighbours of everything pass 1 chose (any sample), since
    paper items are formalized as chains of files and catalog one-liners often miss chain members."""
    ids, cat = catalog(con)
    prefix = f"FILE CATALOG ({len(ids)} files):\n{cat}\n\n"  # identical across items -> prefix cache
    if dry:
        sizes = [llm.approx_tokens(prefix + paper_block(it)) for it in items]
        print(f"catalog ~{llm.approx_tokens(prefix)} tokens; per-item prompt ~{min(sizes)}-{max(sizes)} tokens; "
              f"{len(items)} items x {SAMPLES} samples x 2 passes")
        return
    con.execute("""CREATE TABLE IF NOT EXISTS xref_llm_files (item, sample, file, signals, shared_terms,
                   terms_verified, confidence, not_found, model, pass)""")
    if "pass" not in [r[1] for r in con.execute("PRAGMA table_info(xref_llm_files)")]:
        con.execute("ALTER TABLE xref_llm_files ADD COLUMN pass")
        con.execute("UPDATE xref_llm_files SET pass='catalog'")
    jobs = {}
    for it in items:
        pb = paper_block(it)
        jobs[it["label"]] = (it, pb, prefix + FILES_TASK + "\n\n" + pb, ids)
    _files_pass(con, jobs, "catalog")

    if not neighbour_pass:
        return
    nb = import_neighbours(con)
    docs = dict(con.execute("SELECT file, module_doc FROM lean_files").fetchall())
    jobs = {}
    for it in items:
        chosen = {f for (f,) in con.execute("SELECT DISTINCT file FROM xref_llm_files WHERE item=? AND model=? "
                                            "AND file NOT LIKE '<%'", (it["label"], run_tag()))}
        cand = sorted(set().union(*(nb[f] for f in chosen)) - chosen) if chosen else []
        if not cand:
            continue
        nids, lines = {}, []
        for k, f in enumerate(cand):
            d = re.sub(r"^#+\s*", "", re.sub(r"\s+", " ", docs.get(f) or "")).strip()[:NEIGHBOUR_DOC_CHARS]
            nids[f"N{k}"] = (f, docs.get(f) or "")
            lines.append(f"N{k} | {C.rel(f)} | {d}")
        pb = paper_block(it)
        chosen_txt = "\n".join(sorted(C.rel(f) for f in chosen))
        prompt = (f"FILES ALREADY IDENTIFIED for this paper item:\n{chosen_txt}\n\n"
                  f"FILES THAT IMPORT OR ARE IMPORTED BY THEM ({len(cand)}):\n" + "\n".join(lines) + "\n\n" +
                  NEIGHBOURS_TASK + "\n\n" + pb)
        jobs[it["label"]] = (it, pb, prompt, nids)
    if jobs:
        _files_pass(con, jobs, "neighbours")


def stage_decls(con, items, dry, neighbour_pass=False, robust_pool=False):
    """Every declaration of every chosen file is shown, split into chunks of DECL_CHUNK_TOKENS (one call
    per chunk x SAMPLES) instead of truncating; most-voted files come first."""
    jobs = {}
    for it in items:
        # file votes: distinct samples (over both passes) that chose the file, high confidence counting double
        votes = dict(con.execute(
            "SELECT file, COUNT(DISTINCT pass || sample) + SUM(confidence = 'high') FROM xref_llm_files "
            "WHERE item=? AND model=? AND file NOT LIKE '<%' GROUP BY file", (it["label"], run_tag())).fetchall())
        if robust_pool:
            # The file stage ranks, it does not gate: add every import neighbour of the catalog-pass picks
            # (votes 0, so they come after the picked files). Catalog one-liners miss chain members.
            picked = {f for (f,) in con.execute("SELECT DISTINCT file FROM xref_llm_files WHERE item=? AND model=? "
                                                "AND pass='catalog' AND file NOT LIKE '<%'", (it["label"], run_tag()))}
            for f in set().union(*(_nb[f] for f in picked)) if picked else ():
                votes.setdefault(f, 0)
        files = sorted(votes)
        if not files:
            print(it["label"], "no files from files stage; skipping")
            continue
        rows = con.execute(
            f"SELECT d.name, d.kind, d.file, d.line_start, d.line_end, d.docstring, d.statement, r.reachable "
            f"FROM lean_decls d LEFT JOIN lean_reach r ON r.name=d.name WHERE d.file IN ({','.join('?' * len(files))}) "
            f"AND d.kind IN ('theorem','def','structure','abbrev','inductive') ORDER BY d.file, d.line_start",
            files).fetchall()
        rows = sorted(rows, key=lambda r: (-votes[r[2]], r[2], r[3]))
        chunks, cur, size = [], [], 0
        for row in rows:
            name, kind, f, a_, b_, doc, stmt, _ = row
            line = (f"{kind} {name} | {C.rel(f)}:{a_}-{b_} | "
                    f"{re.sub(r'\s+', ' ', doc or '')[:300]} | {re.sub(r'\s+', ' ', stmt or '')[:DECL_STMT_CHARS]}")
            t = llm.approx_tokens(line)
            if cur and size + t > DECL_CHUNK_TOKENS:
                chunks.append(cur)
                cur, size = [], 0
            cur.append((row, line))
            size += t
        if cur:
            chunks.append(cur)
        pb = paper_block(it)
        for ci, chunk in enumerate(chunks):
            ids = {f"D{k}": (r[0], r[2], r[3], r[4], (r[5] or "") + " " + (r[6] or "")) for k, (r, _) in enumerate(chunk)}
            listing = "\n".join(f"D{k} | {line}" for k, (_, line) in enumerate(chunk))
            prompt = (f"DECLARATIONS (part {ci + 1} of {len(chunks)}; {len(chunk)} of {len(rows)} declarations "
                      f"from the candidate files):\n{listing}\n\n{DECLS_TASK}\n\n{pb}")
            jobs[(it["label"], ci)] = (it, pb, prompt, ids, len(chunks))
        if dry:
            print(f"{it['label']}: {len(files)} files, {len(rows)} decls in {len(chunks)} chunk(s) of "
                  f"~{max(llm.approx_tokens(j[2]) for k, j in jobs.items() if k[0] == it['label'])} tokens max")
    if dry or not jobs:
        return
    cols = [r[1] for r in con.execute("PRAGMA table_info(xref_llm_decls)")]
    if cols and "chunk" not in cols:  # keep results from the earlier truncating version
        con.execute("ALTER TABLE xref_llm_decls RENAME TO xref_llm_decls_v1")
    con.execute("""CREATE TABLE IF NOT EXISTS xref_llm_decls (item, sample, chunk, n_chunks, decl, file, line_start,
                   line_end, role, signals, shared_terms, terms_verified, confidence, model)""")
    with ThreadPoolExecutor(ITEM_WORKERS) as ex:
        futs = {ex.submit(llm.complete_json, SYSTEM, j[2], SAMPLES, tag=f"decls:{key[0]}:{key[1]}"): key
                for key, j in jobs.items()}
        done = [(futs[f], f.result()) for f in as_completed(futs)]
    for label in {k[0] for k in jobs}:
        con.execute("DELETE FROM xref_llm_decls WHERE item=? AND model=?", (label, run_tag()))
    for (label, ci), res in sorted(done):
        it, pb, prompt, ids, n_chunks = jobs[(label, ci)]
        for s, r in enumerate(res):
            if r is None:
                con.execute("INSERT INTO xref_llm_decls (item, sample, chunk, n_chunks, decl, model) "
                            "VALUES (?,?,?,?,?,?)", (label, s, ci, n_chunks, "<invalid-json>", run_tag()))
                continue
            for c in r.get("candidates", []) or []:
                name, f, a_, b_, text = ids.get(c.get("decl_id"),
                                                (f"<unknown id {c.get('decl_id')}>", None, None, None, ""))
                v = verify_terms(c.get("shared_terms"), pb, f"{name} {text}")
                con.execute("INSERT INTO xref_llm_decls VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (label, s, ci, n_chunks, name, f, a_, b_, c.get("role"), json.dumps(c.get("signals")),
                             json.dumps(c.get("shared_terms")), sum(x["in_paper"] and x["in_lean"] for x in v),
                             c.get("confidence"), run_tag()))
        con.commit()
        print(f"{label} chunk {ci + 1}/{n_chunks}", [len((r or {}).get("candidates", []) or []) for r in res])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["files", "decls"])
    ap.add_argument("--items", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--neighbour-pass", action="store_true", help="files: also run the LLM neighbour pass")
    ap.add_argument("--robust-pool", action="store_true",
                    help="decls: pool = files chosen in the catalog pass + ALL their import neighbours")
    a = ap.parse_args()
    con = sqlite3.connect(DB)
    for item, label, latex in con.execute("SELECT in_item, label, latex FROM paper_equations "
                                          "WHERE in_part='proof' ORDER BY line"):
        _proof_equations[item].append((label, latex))
    _nb.update(import_neighbours(con))
    items = load_items(con, {s.strip() for s in a.items.split(",") if s.strip()})
    (stage_files if a.stage == "files" else stage_decls)(con, items, a.dry_run, a.neighbour_pass, a.robust_pool)


if __name__ == "__main__":
    main()
