# SPDX-License-Identifier: Apache-2.0
"""Phase 3: structured extraction for (paper item, Lean declaration) pairs. Facts only, never verdicts.

For each pair, 3 independent samples return strict JSON: paper hypotheses/conclusions, Lean
hypotheses/conclusions, paper parts this declaration does not cover, typed differences ("deltas"),
and a short proof-route summary per side. Every field quotes the text it relies on; quotes are
checked mechanically against the cited Lean lines / paper text, and paper pages are attached from
the index rather than taken from the model. Downstream uses come from the paper's own citations.

The prompts never mention any specific lemma or known discrepancy; `--validate` checks afterwards
whether the validation targets listed in audit.toml were reported.

  python audit/extract.py --section 8 --dry-run      # --section defaults to [plan].pilot_section
  python audit/extract.py --section 8
  python audit/extract.py --validate
Tables: extract_pairs, extract_fields, extract_deltas, paper_downstream.
"""
import argparse
import json
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import config as C
import llm
import paper_text as PT
import xref_llm as X

ROOT = Path(__file__).resolve().parent.parent
DB = C.DB
REPO = C.REPO
SAMPLES = 3
JOB_WORKERS = 5
MAX_DECL_LINES = 160
MAX_REF_DECLS = 10
MAX_REF_LINES = 40
# Extraction outputs are long (many quoted fields); prompts are only ~4k tokens, so the budget can be large.
# Retries get double this (see llm.complete_json).
EXTRACT_MAX_TOKENS = 48000

DELTA_TYPES = {
    "extra-hypothesis": "the paper assumes something that the Lean declaration does not assume",
    "missing-hypothesis": "the Lean declaration assumes something that the paper's statement does not state",
    "stronger-bound": "the paper states a stronger estimate than the Lean declaration proves (e.g. a better "
                      "rate or exponent, a stronger norm on the left, a weaker norm or less regularity "
                      "required on the right, a smaller or more explicit constant)",
    "weaker-bound": "the paper states a weaker estimate than the Lean declaration proves",
    "different-norm": "the two sides measure size with different norms, seminorms or function classes",
    "missing-supremum": "one side takes a supremum, maximum, or uniformity over a parameter that the other does not",
    "different-domain": "the two sides are stated on different sets, spaces, time intervals or parameter ranges",
    "other": "any other difference in what is assumed or concluded",
}
VERDICT_WORDS = re.compile(r"\b(harmless|benign|equivalent|innocuous|immaterial|insignificant|negligible|"
                           r"correct|incorrect|wrong|error|mistake|bug|fine|acceptable|minor|serious|severe|"
                           r"critical|faithful|unfaithful|matches|consistent)\b", re.I)

SYSTEM = """You compare a statement from a mathematics paper with a Lean 4 declaration, and you EXTRACT FACTS.
You never judge: do not say whether a difference matters, is harmless, is an error, or whether the two are
equivalent, faithful, correct or consistent. Describe what each side says and list the differences.
Every extracted item must quote, verbatim, the text it is based on. Return only JSON."""

TASK = """Extract the following from the PAPER ITEM and the LEAN DECLARATION above. The paper item may be split
over several Lean declarations (the others are listed for context only); compare this declaration only with the
parts of the paper item it addresses, and list the paper parts it does not address under "paper_parts_not_covered".

Lean hypotheses include the declaration's explicit arguments and hypotheses, implicit and instance arguments,
and the section `variable`s in scope (shown separately), minus anything removed by `omit`. Use the definitions
shown to interpret what the Lean statement says.

Quoting rules: "quote" must be copied verbatim (a short fragment is enough). For the paper, "cite" is the item
label or an equation number like "(8.12)". For Lean, "lines" is a line range like "1059-1061" from the numbers
shown at the left of the Lean source, and the quote must appear on those lines.

Difference types (direction always compares the PAPER with the LEAN):
%s

Return JSON:
{"paper": {"hypotheses": [{"text": "...", "cite": "...", "quote": "..."}],
           "conclusions": [{"text": "...", "cite": "...", "quote": "..."}],
           "proof_route": "at most 3 sentences on how the paper proves it"},
 "lean":  {"hypotheses": [{"text": "...", "lines": "a-b", "quote": "..."}],
           "conclusions": [{"text": "...", "lines": "a-b", "quote": "..."}],
           "proof_route": "at most 3 sentences on how the Lean proof proceeds (which results it uses)"},
 "paper_parts_not_covered": [{"text": "...", "cite": "...", "quote": "..."}],
 "deltas": [{"type": "<one of the types above>", "paper_side": "what the paper says", "lean_side": "what the Lean says",
             "paper_cite": "...", "paper_quote": "...", "lean_lines": "a-b", "lean_quote": "...",
             "description": "one or two neutral sentences describing the difference"}]}
List every difference you can find, including small ones. An empty list is allowed only if there are none."""


def numbered(file, a, b):
    lines = (REPO / file).read_text(encoding="utf-8").splitlines()
    a, b = max(1, a), min(len(lines), b)
    return "\n".join(f"{k:5d} | {lines[k - 1]}" for k in range(a, b + 1)), (a, b)


def lean_context(con, decl):
    name, file, ls, dl, le, prefix, in_scope = con.execute(
        "SELECT name, file, line_start, decl_line, line_end, prefix, variables FROM lean_decls WHERE name=?",
        (decl,)).fetchone()
    in_scope = re.sub(r"\s+", " ", in_scope or "")
    shown = []  # (file, a, b) ranges shown, for citation checks
    a = ls - (1 if prefix else 0)
    b = min(le, a + MAX_DECL_LINES)
    txt, rng = numbered(file, a, b)
    shown.append((file, *rng))
    parts = [f"LEAN DECLARATION {name}\nFILE {file}" + (" (truncated)" if b < le else "") + f"\n{txt}"]
    # section variables in scope: every column-0 `variable` command above the declaration
    src = (REPO / file).read_text(encoding="utf-8").splitlines()
    var_lines = []
    for k in range(dl - 1):
        if src[k].startswith("variable"):
            j = k
            while j + 1 < len(src) and src[j + 1].startswith((" ", "\t")) and src[j + 1].strip():
                j += 1
            # keep only variables still in scope (closed sections drop theirs; the index tracks scope)
            if re.sub(r"\s+", " ", " ".join(src[k:j + 1])).strip() in in_scope:
                var_lines.append((k + 1, j + 1))
    if var_lines:
        vt = "\n".join(numbered(file, x, y)[0] for x, y in var_lines)
        shown += [(file, x, y) for x, y in var_lines]
        parts.append(f"SECTION VARIABLES IN SCOPE (same file; they are hypotheses of the declaration unless "
                     f"omitted)\n{vt}")
    refs = [t for (t,) in con.execute("SELECT target FROM lean_refs WHERE source=? AND location='statement'", (decl,))]
    defs = []
    for t in refs[:MAX_REF_DECLS]:
        r = con.execute("SELECT file, line_start, line_end, kind FROM lean_decls WHERE name=?", (t,)).fetchone()
        if not r:
            continue
        f2, a2, b2, kind = r
        tx, rng2 = numbered(f2, a2, min(b2, a2 + MAX_REF_LINES))
        shown.append((f2, *rng2))
        defs.append(f"-- {kind} {t}  ({f2})\n{tx}")
    if defs:
        parts.append("DEFINITIONS AND RESULTS USED IN THE STATEMENT\n" + "\n\n".join(defs))
    return "\n\n".join(parts), shown


PROOF_CAP = 20000  # characters of proof text in a comparison prompt; paper_text.context_check reports overruns


def paper_context(it, page_of):
    stmt = it["statement_latex"] or it["statement"]
    proof = PT.choose_proof(it)[0] if it.get("kind") != "ProofStep" else ""
    flagged = it["ocr_flagged_blocks"] or 0
    return (f"PAPER ITEM {it['label']} (page {it['printed_page']}; Section {it['section']} "
            f"'{it['section_title']}', subsection {it['subsection']} '{it['subsection_title']}')\n"
            + (f"[{flagged} block(s) of this item were flagged by the OCR cross-check; symbols may be misread]\n"
               if flagged else "")
            + f"STATEMENT:\n{stmt}\n\nPROOF:\n{proof[:PROOF_CAP]}")


def norm(s):
    s = re.sub(r"\\[a-zA-Z]+|[{}$\\]", " ", s or "")
    return re.sub(r"\s+", "", s).lower()


def check_lean(quote, lines, shown):
    m = re.match(r"\s*(\d+)\s*(?:-\s*(\d+))?", str(lines or ""))
    if not m or not quote:
        return 0
    a, b = int(m.group(1)), int(m.group(2) or m.group(1))
    for f, x, y in shown:
        if x <= a <= y or x <= b <= y:
            src = (REPO / f).read_text(encoding="utf-8").splitlines()
            seg = "".join(src[max(a, x) - 1:min(b, y)])
            if re.sub(r"\s+", "", quote) in re.sub(r"\s+", "", seg):
                return 1
    return 0


def check_paper(quote, paper_text):
    q = norm(quote)
    return int(bool(q) and q in norm(paper_text))


def page_for(cite, it, con):
    m = re.search(r"\(((?:\d+|[A-C])\.\d+)\)", cite or "")
    if m:
        r = con.execute("SELECT printed_page FROM paper_equations WHERE number=?", (m.group(1),)).fetchone()
        if r:
            return r[0]
    m = re.search(r"(Lemma|Proposition|Theorem|Corollary|Definition|Remark)\s+((?:\d+|[A-C])\.\d+)", cite or "")
    if m:
        r = con.execute("SELECT printed_page FROM paper_items WHERE label=?", (f"{m.group(1)} {m.group(2)}",)).fetchone()
        if r:
            return r[0]
    return it["printed_page"]


def setup(con):
    con.execute("""CREATE TABLE IF NOT EXISTS extract_pairs (pair_id, item, decl, decl_file, decl_lines, reachable,
                   other_candidates, samples_ok, model)""")
    con.execute("""CREATE TABLE IF NOT EXISTS extract_fields (pair_id, sample, side, field, text, cite, quote,
                   cite_ok, page, model)""")
    con.execute("""CREATE TABLE IF NOT EXISTS extract_deltas (pair_id, sample, type, paper_side, lean_side, paper_cite,
                   paper_quote, paper_cite_ok, page, lean_lines, lean_quote, lean_cite_ok, description,
                   verdict_words, model)""")
    con.execute("""CREATE TABLE IF NOT EXISTS paper_downstream (item, cited_from, part, page, line)""")


def downstream(con):
    con.execute("DELETE FROM paper_downstream")
    con.execute("""INSERT INTO paper_downstream SELECT r.target, COALESCE(r.from_item, 'text of section ' ||
                   COALESCE(r.subsection, r.section)), r.from_part, r.pdf_page, r.line FROM paper_refs r
                   WHERE r.target IN (SELECT label FROM paper_items)""")


def store(con, pair_id, it, res, shown, paper_text):
    tag = X.run_tag()
    for s, r in enumerate(res):
        if r is None:
            con.execute("INSERT INTO extract_fields (pair_id, sample, side, field, model) VALUES (?,?,?,?,?)",
                        (pair_id, s, "-", "<invalid-json>", tag))
            continue
        for side in ("paper", "lean"):
            blk = r.get(side) or {}
            for field in ("hypotheses", "conclusions"):
                for e in blk.get(field) or []:
                    if not isinstance(e, dict):
                        continue
                    if side == "paper":
                        cite, ok, page = e.get("cite"), check_paper(e.get("quote"), paper_text), page_for(e.get("cite"), it, con)
                    else:
                        cite, ok, page = e.get("lines"), check_lean(e.get("quote"), e.get("lines"), shown), None
                    con.execute("INSERT INTO extract_fields VALUES (?,?,?,?,?,?,?,?,?,?)",
                                (pair_id, s, side, field, e.get("text"), str(cite), e.get("quote"), ok, page, tag))
            con.execute("INSERT INTO extract_fields VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (pair_id, s, side, "proof_route", blk.get("proof_route"), None, None, None, None, tag))
        for e in r.get("paper_parts_not_covered") or []:
            if isinstance(e, dict):
                con.execute("INSERT INTO extract_fields VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (pair_id, s, "paper", "not_covered", e.get("text"), e.get("cite"), e.get("quote"),
                             check_paper(e.get("quote"), paper_text), page_for(e.get("cite"), it, con), tag))
        for d in r.get("deltas") or []:
            if not isinstance(d, dict):
                continue
            text = " ".join(str(d.get(k) or "") for k in ("paper_side", "lean_side", "description"))
            con.execute("INSERT INTO extract_deltas VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (pair_id, s, d.get("type") if d.get("type") in DELTA_TYPES else f"invalid:{d.get('type')}",
                         d.get("paper_side"), d.get("lean_side"), d.get("paper_cite"), d.get("paper_quote"),
                         check_paper(d.get("paper_quote"), paper_text), page_for(d.get("paper_cite"), it, con),
                         str(d.get("lean_lines")), d.get("lean_quote"),
                         check_lean(d.get("lean_quote"), d.get("lean_lines"), shown), d.get("description"),
                         ", ".join(sorted({w.lower() for w in VERDICT_WORDS.findall(text)})) or None, tag))


def validate(con):
    """Check the validation targets in audit.toml ([[validation]]) by location and type (validation.py):
    how many samples reported a difference of an allowed type at the target's Lean lines, against how often
    the same check fires elsewhere."""
    import validation as V
    if not C.VALIDATION:
        print("no validation targets configured")
        return True
    ok = True
    for r in V.check_all(con):
        print(V.describe(r))
        for d in r["hits"]:
            print(f"    sample {d['sample']} [{d['type']}] lines {d['lean_lines']}: {d['description']}")
        ok = ok and r["k"] > 0
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", default=C.PILOT_SECTION)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--steps", action="store_true", help="extract proof-step targets instead of paper results")
    ap.add_argument("--items", default="", help="comma-separated results (with --steps: their parent results)")
    a = ap.parse_args()
    con = sqlite3.connect(DB)
    setup(con)
    if a.validate:
        validate(con)
        return
    con.row_factory = sqlite3.Row
    tag = X.run_tag()
    wanted = {x.strip() for x in a.items.split(",") if x.strip()}
    if a.steps:
        # proof-step targets (audit/proof_steps.py): the step's text plays the role of the statement
        items = {r["label"]: dict(r, statement=r["statement_latex"], proof_latex=None, proof=None)
                 for r in con.execute("SELECT * FROM paper_steps")}
        targets = con.execute("SELECT item, found_all FROM search_status WHERE kind='ProofStep' AND model=?",
                              (tag,)).fetchall()
    else:
        items = {r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_items WHERE section=?", (a.section,))}
        targets = con.execute("SELECT item, found_all FROM search_status WHERE section=? AND kind != 'ProofStep' "
                              "AND model=?", (a.section, tag)).fetchall()
    con.row_factory = None
    task = TASK % "\n".join(f"  {k}: {v}" for k, v in DELTA_TYPES.items())
    jobs = []
    for item, fa in targets:
        if wanted and item not in wanted and not any(item.endswith(f"of {w}") for w in wanted):
            continue
        cands = [c["decl"] for c in json.loads(fa or "[]")]
        it = items[item]
        pctx = paper_context(it, None)
        paper_text = (it["statement_latex"] or "") + " " + (it["proof_latex"] or "") + " " + (it["statement"] or "")
        for decl in cands:
            lctx, shown = lean_context(con, decl)
            others = [c for c in cands if c != decl]
            prompt = (f"{pctx}\n\n{lctx}\n\nOTHER LEAN DECLARATIONS LOCATED FOR THIS PAPER ITEM (context only): "
                      f"{', '.join(others) or 'none'}\n\n{task}")
            pair_id = f"{item} || {decl}"
            jobs.append(dict(pair_id=pair_id, item=item, decl=decl, prompt=prompt, shown=shown, it=it,
                             paper_text=paper_text, others=others))
    sizes = [llm.approx_tokens(SYSTEM + j["prompt"]) for j in jobs]
    print(f"{len(jobs)} pairs x {SAMPLES} samples = {SAMPLES * len(jobs)} calls; prompt ~{min(sizes)}-{max(sizes)} "
          f"rough tokens (~0.63x real)")
    if a.dry_run:
        j = next((j for j in jobs if j["decl"].endswith("inverse_finiteJets")), jobs[0])
        print("\n----- sample prompt:", j["pair_id"], "-----\n", j["prompt"][:200], "\n...\n", j["prompt"][-4500:-3000])
        return
    downstream(con)
    for j in jobs:
        for t in ("extract_pairs", "extract_fields", "extract_deltas"):
            con.execute(f"DELETE FROM {t} WHERE pair_id=? AND model=?", (j["pair_id"], tag))
    con.commit()
    with ThreadPoolExecutor(JOB_WORKERS) as ex:
        futs = {ex.submit(llm.complete_json, SYSTEM, j["prompt"], SAMPLES, max_tokens=EXTRACT_MAX_TOKENS,
                          tag=f"extract:{j['pair_id']}"): j
                for j in jobs}
        for n, f in enumerate(as_completed(futs), start=1):
            j, res = futs[f], f.result()
            row = con.execute("SELECT file, line_start, line_end FROM lean_decls WHERE name=?", (j["decl"],)).fetchone()
            reach = con.execute("SELECT reachable FROM lean_reach WHERE name=?", (j["decl"],)).fetchone()
            con.execute("INSERT INTO extract_pairs VALUES (?,?,?,?,?,?,?,?,?)",
                        (j["pair_id"], j["item"], j["decl"], row[0], f"{row[1]}-{row[2]}", reach[0] if reach else None,
                         json.dumps(j["others"]), sum(r is not None for r in res), tag))
            store(con, j["pair_id"], j["it"], res, j["shown"], j["paper_text"])
            con.commit()
            print(f"  [{time.strftime('%H:%M:%S')}] {n}/{len(jobs)} {j['pair_id']}: "
                  f"{[len((r or {}).get('deltas') or []) for r in res]} deltas per sample", flush=True)
    validate(con)


if __name__ == "__main__":
    main()
