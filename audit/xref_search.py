"""Phase 2c: multi-round search for each paper item's Lean counterpart, with a full audit trail.

Round 1   declaration pool = the files the model picked from the whole catalog (xref_llm.py files).
Round 2,3 only for items not yet found. A fresh file-selection prompt shows the catalog MINUS every file
          already examined, with hint files listed first, then the model reads the newly picked files.
          Hints come from the paper's own structure, and only rank files (they never exclude any):
            - files matched to neighbouring items of the same section (+-2 items)
            - files matched to items this item cites, or that cite it
            - import neighbours of files this item's samples agreed on (>= 2 of 3)
          "Matched" means the found declaration's file if that item is already found, otherwise the
          files its catalog-pass samples agreed on (>= 2 of 3).
Found     some declaration given role "statement" (or "definition", for Definition items) by >= 2 of
          the 3 samples (see below), confidence high or medium, with >= 1 verified shared term. This is about
          LOCATING a counterpart only; it says nothing about whether it matches the paper. Found requires
          all 3 samples; agreement of 2 of 3 is kept as a weak candidate and the search continues.
Stop      found, or MAX_ROUNDS rounds tried -> "weak match (2 of 3 samples) after N rounds" or
          "not found after N rounds".
Declarations that are routine helpers (simp lemmas, private, undocumented names ending in _smooth,
_apply, _nonneg, ...) are left out of every pool; see TRIVIAL below.

Tables: search_files, search_decls (every sample's candidates, per round), search_rounds (one row per
item x round: what was offered, excluded, hinted, examined, and the outcome), search_status (one row
per item: rounds tried and final status).

  python audit/xref_search.py --group pilot      # Section 8 + anchors
  python audit/xref_search.py --group random     # the 12 random items
  python audit/xref_search.py --group pilot --dry-run
"""
import argparse
import json
import re
import sqlite3
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import llm
import xref_llm as X

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "audit.db"
PLAN = ROOT / "data" / "phase2_sample.json"
MAX_ROUNDS = 3
MAX_HINTS = 25
JOB_WORKERS = 5          # chunks in flight (x 3 samples); total requests capped by llm's semaphore
TRIVIAL_SUFFIX = re.compile(
    r"_(smooth|apply|def|eq|contDiff\w*|continuous\w*|measurable\w*|integrable\w*|differentiable\w*|nonneg|pos|"
    r"ne_zero|mono|comm|symm|zero|one|add|sub|neg|smul|mul)$")

RETRY_TASK = """This is search round %d for the paper item below. Files already examined in earlier rounds
have been REMOVED from the catalog because no confident counterpart was located in them. HINT FILES are
files that the paper's structure suggests (neighbouring or citing/cited items were located there, or they
are linked by imports to files examined earlier); they are only suggestions. List up to 10 catalog files
(hints or not) most likely to contain the Lean formalization of this paper item's statement or of its
proof's main steps. Return the same JSON schema as before:
{"candidates": [{"file_id": "F12", "signals": [...], "shared_terms": ["terms appearing in BOTH the paper
item and that file's catalog entry"], "confidence": "high" | "medium" | "low"}],
 "paper_concepts_not_found": [...]}
Allowed signals: %s
If nothing plausible remains, return an empty candidates list."""


def trivial(name, attributes, statement, doc):
    short = name.split(".")[-1]
    return ("simp" in (attributes or "") or (statement or "").startswith("private") or short.startswith("_")
            or (doc is None and bool(TRIVIAL_SUFFIX.search(short))))


def setup(con):
    con.execute("""CREATE TABLE IF NOT EXISTS search_files (item, round, sample, file, signals, shared_terms,
                   terms_verified, confidence, model)""")
    con.execute("""CREATE TABLE IF NOT EXISTS search_decls (item, round, sample, chunk, n_chunks, decl, file,
                   line_start, line_end, role, signals, shared_terms, terms_verified, confidence, model)""")
    con.execute("""CREATE TABLE IF NOT EXISTS search_rounds (item, round, files_offered, files_excluded,
                   hint_files, files_examined, n_decls, n_trivial_skipped, n_chunks, found, found_decl,
                   found_agreement, started, finished, model, found_all)""")
    con.execute("""CREATE TABLE IF NOT EXISTS search_status (item, kind, section, rounds_tried, status,
                   found_round, found_decl, found_file, found_agreement, files_examined_total, model, found_all)""")


def found_decl(con, item, kind, rnd):
    roles = ("statement", "definition") if kind == "Definition" else ("statement",)
    rows = con.execute(
        f"SELECT decl, file, COUNT(DISTINCT sample) n, MAX(terms_verified) FROM search_decls WHERE item=? AND round=? "
        f"AND model=? AND role IN ({','.join('?' * len(roles))}) AND confidence IN ('high','medium') "
        f"AND decl NOT LIKE '<%' GROUP BY decl ORDER BY n DESC", (item, rnd, X.run_tag(), *roles)).fetchall()
    agreed = [(decl, file, n) for decl, file, n, tv in rows if n >= 2 and tv and tv > 0]
    if not agreed:
        return None
    # top candidate first, plus every declaration the samples agreed on (a paper item is often split
    # over several Lean theorems, e.g. Lemma 8.6's inverse bound and its physical update)
    return agreed[0][0], agreed[0][1], agreed[0][2], [dict(decl=d, file=f, agreement=n) for d, f, n in agreed]


def decl_jobs(con, it, rnd, files, votes):
    """Chunked declaration prompts over all non-trivial declarations of `files` (most-voted files first)."""
    if not files:
        return [], 0, 0
    rows = con.execute(
        f"SELECT name, kind, file, line_start, line_end, docstring, statement, attributes FROM lean_decls "
        f"WHERE file IN ({','.join('?' * len(files))}) AND kind IN ('theorem','def','structure','abbrev','inductive')",
        sorted(files)).fetchall()
    keep = [r for r in rows if not trivial(r[0], r[7], r[6], r[5])]
    keep.sort(key=lambda r: (-votes.get(r[2], 0), r[2], r[3]))
    chunks, cur, size = [], [], 0
    for r in keep:
        line = (f"{r[1]} {r[0]} | {r[2].removeprefix('NavierStokes/')}:{r[3]}-{r[4]} | "
                f"{re.sub(r'\s+', ' ', r[5] or '')[:300]} | {re.sub(r'\s+', ' ', r[6] or '')[:X.DECL_STMT_CHARS]}")
        t = llm.approx_tokens(line)
        if cur and size + t > X.DECL_CHUNK_TOKENS:
            chunks.append(cur)
            cur, size = [], 0
        cur.append((r, line))
        size += t
    if cur:
        chunks.append(cur)
    pb = X.paper_block(it)
    jobs = []
    for ci, chunk in enumerate(chunks):
        ids = {f"D{k}": (r[0], r[2], r[3], r[4], (r[5] or "") + " " + (r[6] or "")) for k, (r, _) in enumerate(chunk)}
        listing = "\n".join(f"D{k} | {line}" for k, (_, line) in enumerate(chunk))
        prompt = (f"DECLARATIONS (part {ci + 1} of {len(chunks)}; {len(chunk)} of {len(keep)} declarations from the "
                  f"candidate files):\n{listing}\n\n{X.DECLS_TASK}\n\n{pb}")
        jobs.append(dict(item=it["label"], round=rnd, chunk=ci, n_chunks=len(chunks), prompt=prompt, ids=ids, pb=pb))
    return jobs, len(keep), len(rows) - len(keep)


def run_decl_jobs(con, jobs):
    with ThreadPoolExecutor(JOB_WORKERS) as ex:
        futs = {ex.submit(llm.complete_json, X.SYSTEM, j["prompt"], X.SAMPLES,
                          tag=f"search-decls:r{j['round']}:{j['item']}:{j['chunk']}"): j for j in jobs}
        for n_done, f in enumerate(as_completed(futs), start=1):
            j, res = futs[f], f.result()
            for s, r in enumerate(res):
                if r is None:
                    con.execute("INSERT INTO search_decls (item, round, sample, chunk, n_chunks, decl, model) "
                                "VALUES (?,?,?,?,?,?,?)", (j["item"], j["round"], s, j["chunk"], j["n_chunks"],
                                                           "<invalid-json>", X.run_tag()))
                    continue
                for c in r.get("candidates", []) or []:
                    name, file, a, b, text = j["ids"].get(c.get("decl_id"),
                                                          (f"<unknown id {c.get('decl_id')}>", None, None, None, ""))
                    v = X.verify_terms(c.get("shared_terms"), j["pb"], f"{name} {text}")
                    con.execute("INSERT INTO search_decls VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                (j["item"], j["round"], s, j["chunk"], j["n_chunks"], name, file, a, b, c.get("role"),
                                 json.dumps(c.get("signals")), json.dumps(c.get("shared_terms")),
                                 sum(x["in_paper"] and x["in_lean"] for x in v), c.get("confidence"), X.run_tag()))
            con.commit()
            print(f"  [{time.strftime('%H:%M:%S')}] {n_done}/{len(jobs)} chunks done "
                  f"({j['item']} round {j['round']} chunk {j['chunk'] + 1}/{j['n_chunks']})", flush=True)


def run_file_round(con, items, rnd, ids, cat_lines, hints, examined):
    """Fresh file-selection prompt per item: catalog minus examined files, hints first."""
    path_to_id = {f: fid for fid, (f, _) in ids.items()}
    jobs = {}
    for it in items:
        lab = it["label"]
        ex = examined[lab]
        hint_lines = [f"{path_to_id[f]} | {f.removeprefix('NavierStokes/')} | HINT: {why}"
                      for f, why in hints[lab] if f in path_to_id]
        cat = [ln for fid, ln in cat_lines if ids[fid][0] not in ex]
        prompt = (f"HINT FILES ({len(hint_lines)}):\n" + "\n".join(hint_lines) +
                  f"\n\nFILE CATALOG ({len(cat)} files; {len(ex)} already examined and removed):\n" + "\n".join(cat) +
                  "\n\n" + RETRY_TASK % (rnd, ", ".join(X.FILE_SIGNALS)) + "\n\n" + X.paper_block(it))
        jobs[lab] = (it, prompt, len(cat))
    picked = defaultdict(Counter)
    with ThreadPoolExecutor(JOB_WORKERS) as exr:
        futs = {exr.submit(llm.complete_json, X.SYSTEM, p, X.SAMPLES, tag=f"search-files:r{rnd}:{lab}"): lab
                for lab, (_, p, _) in jobs.items()}
        for f in as_completed(futs):
            lab = futs[f]
            it = jobs[lab][0]
            pb = X.paper_block(it)
            for s, r in enumerate(f.result()):
                if r is None:
                    con.execute("INSERT INTO search_files (item, round, sample, file, model) VALUES (?,?,?,?,?)",
                                (lab, rnd, s, "<invalid-json>", X.run_tag()))
                    continue
                for c in r.get("candidates", []) or []:
                    file, doc = ids.get(c.get("file_id"), (f"<unknown id {c.get('file_id')}>", ""))
                    if file in examined[lab]:
                        continue  # should not happen (removed from catalog), but never re-examine
                    v = X.verify_terms(c.get("shared_terms"), pb, file + " " + doc)
                    con.execute("INSERT INTO search_files VALUES (?,?,?,?,?,?,?,?,?)",
                                (lab, rnd, s, file, json.dumps(c.get("signals")), json.dumps(c.get("shared_terms")),
                                 sum(x["in_paper"] and x["in_lean"] for x in v), c.get("confidence"), X.run_tag()))
                    if not file.startswith("<"):
                        picked[lab][file] += 1 + (c.get("confidence") == "high")
            con.commit()
            print(f"  [{time.strftime('%H:%M:%S')}] round {rnd} files picked for {lab}: {len(picked[lab])}", flush=True)
    return picked, {lab: j[2] for lab, j in jobs.items()}


def classify(f):
    """strong = all 3 samples agreed on a statement-role declaration; weak = 2 of 3; None = neither."""
    if not f:
        return None
    return "strong" if f[2] >= 3 else "weak"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", choices=["pilot", "random", "sample", "rest", "all"], required=True)
    ap.add_argument("--resume", action="store_true",
                    help="continue items that already have search rounds instead of restarting them")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    plan = json.loads(PLAN.read_text())
    sample = plan["section8"] + plan["anchors"] + plan["random_sample"]

    con = sqlite3.connect(DB)
    for item, label, latex in con.execute("SELECT in_item, label, latex FROM paper_equations "
                                          "WHERE in_part='proof' ORDER BY line"):
        X._proof_equations[item].append((label, latex))
    nb = X.import_neighbours(con)
    all_items = X.load_items(con, set())
    order = [it["label"] for it in all_items]
    by_label = {it["label"]: it for it in all_items}
    labels = {"pilot": plan["section8"] + plan["anchors"], "random": plan["random_sample"], "sample": sample,
              "rest": [lab for lab in order if lab not in sample], "all": order}[a.group]
    labels = list(dict.fromkeys(labels))
    items = [by_label[lab] for lab in labels]
    setup(con)
    tag = X.run_tag()

    # links from the paper's structure: neighbours (same section, +-2) and citations either way
    links = defaultdict(dict)
    for lab in labels:
        it = by_label[lab]
        i = order.index(lab)
        for j in range(max(0, i - 2), min(len(order), i + 3)):
            if j != i and by_label[order[j]]["section"] == it["section"]:
                links[lab][order[j]] = "neighbouring item"
        for (t,) in con.execute("SELECT DISTINCT target FROM paper_refs WHERE from_item=?", (lab,)):
            if t in by_label and t != lab:
                links[lab].setdefault(t, f"cited by {lab}")
        for (src,) in con.execute("SELECT DISTINCT from_item FROM paper_refs WHERE target=? AND from_item IS NOT NULL",
                                  (lab,)):
            if src in by_label and src != lab:
                links[lab].setdefault(src, f"cites {lab}")

    def agreed_catalog_files(lab):
        return {f for (f,) in con.execute(
            "SELECT file FROM xref_llm_files WHERE item=? AND model=? AND pass='catalog' AND file NOT LIKE '<%' "
            "GROUP BY file HAVING COUNT(DISTINCT sample) >= 2", (lab, tag))}

    def located_files(lab):
        row = con.execute("SELECT found_file FROM search_status WHERE item=? AND model=? AND found_file IS NOT NULL "
                          "AND found_agreement >= 3", (lab, tag)).fetchone()
        return ({row[0]}, "located") if row else (agreed_catalog_files(lab), "agreed catalog pick")

    examined = defaultdict(set)
    last_round = {}
    best = {}  # lab -> (round, f): best candidate so far; strong beats weak, earlier round wins ties

    def record_best(lab, rnd, f):
        c = classify(f)
        if c and (lab not in best or (c == "strong" and classify(best[lab][1]) != "strong")):
            best[lab] = (rnd, f)

    def is_strong(lab):
        return lab in best and classify(best[lab][1]) == "strong"

    def write_status(lab, rnd, final=False):
        it = by_label[lab]
        b = best.get(lab)
        if is_strong(lab):
            st = f"found in round {b[0]}"
        elif final:
            st = f"weak match (2 of 3 samples) after {rnd} rounds" if b else f"not found after {rnd} rounds"
        else:
            st = "searching"
        f = b[1] if b else None
        con.execute("DELETE FROM search_status WHERE item=? AND model=?", (lab, tag))
        con.execute("INSERT INTO search_status VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (lab, it["kind"], it["section"], rnd, st, b[0] if b else None, f[0] if f else None,
                     f[1] if f else None, f[2] if f else None, len(examined[lab]), tag,
                     json.dumps(f[3]) if f else None))

    # ---------- resume: rebuild state from stored rounds (no model calls) ----------
    resumed = set()
    if a.resume:
        for it in items:
            lab = it["label"]
            rows = con.execute("SELECT round, files_examined FROM search_rounds WHERE item=? AND model=? ORDER BY round",
                               (lab, tag)).fetchall()
            if not rows:
                continue
            resumed.add(lab)
            for rnd, fe in rows:
                examined[lab] |= set(json.loads(fe or "[]"))
                record_best(lab, rnd, found_decl(con, lab, it["kind"], rnd))
            last_round[lab] = rows[-1][0]
            write_status(lab, last_round[lab])
        con.commit()
        print(f"resumed {len(resumed)} items: " + ", ".join(
            f"{lab}={classify(best[lab][1]) if lab in best else 'none'}" for lab in sorted(resumed)))

    # ---------- round 1 for fresh items ----------
    fresh = [it for it in items if it["label"] not in resumed]
    jobs, meta = [], {}
    n_catalog = len(X.catalog(con)[0])
    for it in fresh:
        lab = it["label"]
        votes = dict(con.execute(
            "SELECT file, COUNT(DISTINCT sample) + SUM(confidence='high') FROM xref_llm_files WHERE item=? AND model=? "
            "AND pass='catalog' AND file NOT LIKE '<%' GROUP BY file", (lab, tag)).fetchall())
        j, n_keep, n_triv = decl_jobs(con, it, 1, set(votes), votes)
        jobs += j
        meta[lab] = dict(files_offered=n_catalog, files_examined=sorted(votes), n_decls=n_keep,
                         n_trivial_skipped=n_triv, n_chunks=len(j))
    print(f"round 1: {len(fresh)} fresh items, {len(jobs)} chunks, {3 * len(jobs)} calls")
    if a.dry_run:
        for lab, m in meta.items():
            print(f"  {lab}: {len(m['files_examined'])} files, {m['n_decls']} decls "
                  f"(+{m['n_trivial_skipped']} trivial skipped), {m['n_chunks']} chunks")
        todo2 = [lab for lab in resumed if not is_strong(lab) and last_round[lab] < MAX_ROUNDS]
        print(f"would continue to the next round: {todo2}")
        return
    for it in fresh:
        for t in ("search_files", "search_decls", "search_rounds", "search_status"):
            con.execute(f"DELETE FROM {t} WHERE item=? AND model=?", (it["label"], tag))
    con.commit()
    if jobs:
        started = time.strftime("%Y-%m-%d %H:%M:%S")
        run_decl_jobs(con, jobs)
        for it in fresh:
            lab = it["label"]
            m = meta[lab]
            examined[lab] |= set(m["files_examined"])
            f = found_decl(con, lab, it["kind"], 1)
            record_best(lab, 1, f)
            last_round[lab] = 1
            con.execute("INSERT INTO search_rounds VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (lab, 1, m["files_offered"], 0, "[]", json.dumps(m["files_examined"]), m["n_decls"],
                         m["n_trivial_skipped"], m["n_chunks"], int(classify(f) == "strong"),
                         f[0] if f else None, f[2] if f else None, started, time.strftime("%Y-%m-%d %H:%M:%S"),
                         tag, json.dumps(f[3]) if f else None))
            write_status(lab, 1)
        con.commit()
        print("round 1 strong:", sum(is_strong(it["label"]) for it in fresh), "/", len(fresh))

    # ---------- rounds 2..MAX for items without a strong match ----------
    ids, _ = X.catalog(con)
    cat_lines = []
    for fid, (f, doc) in ids.items():
        d = re.sub(r"^#+\s*", "", re.sub(r"\s+", " ", doc or "")).strip()[:X.DOC_CHARS]
        cat_lines.append((fid, f"{fid} | {f.removeprefix('NavierStokes/')} | {d}"))
    for rnd in range(2, MAX_ROUNDS + 1):
        todo = [it for it in items if last_round.get(it["label"]) == rnd - 1 and not is_strong(it["label"])]
        if not todo:
            continue
        hints = {}
        for it in todo:
            lab = it["label"]
            score, why = Counter(), defaultdict(list)
            for other, rel in links[lab].items():
                files, how = located_files(other)
                for f in files:
                    score[f] += 2 if how == "located" else 1
                    why[f].append(f"{rel} {other} ({how})")
            for f in agreed_catalog_files(lab):
                for g in nb[f]:
                    score[g] += 1
                    why[g].append(f"imports/imported by {f.removeprefix('NavierStokes/')}")
            ranked = [f for f, _ in score.most_common() if f not in examined[lab]][:MAX_HINTS]
            hints[lab] = [(f, "; ".join(dict.fromkeys(why[f]))[:300]) for f in ranked]
        started = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"round {rnd}: {len(todo)} items searching: " + ", ".join(it["label"] for it in todo))
        picked, offered = run_file_round(con, todo, rnd, ids, cat_lines, hints, examined)
        jobs = []
        for it in todo:
            lab = it["label"]
            files = set(picked[lab])
            j, n_keep, n_triv = decl_jobs(con, it, rnd, files, picked[lab])
            jobs += j
            meta[lab] = dict(files_offered=offered[lab], files_excluded=len(examined[lab]),
                             hint_files=[f for f, _ in hints[lab]], files_examined=sorted(files),
                             n_decls=n_keep, n_trivial_skipped=n_triv, n_chunks=len(j))
            examined[lab] |= files
        print(f"round {rnd}: {len(jobs)} chunks, {3 * len(jobs)} calls")
        if jobs:
            run_decl_jobs(con, jobs)
        for it in todo:
            lab = it["label"]
            f = found_decl(con, lab, it["kind"], rnd)
            record_best(lab, rnd, f)
            last_round[lab] = rnd
            m = meta[lab]
            con.execute("INSERT INTO search_rounds VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (lab, rnd, m["files_offered"], m["files_excluded"], json.dumps(m["hint_files"]),
                         json.dumps(m["files_examined"]), m["n_decls"], m["n_trivial_skipped"], m["n_chunks"],
                         int(classify(f) == "strong"), f[0] if f else None, f[2] if f else None, started,
                         time.strftime("%Y-%m-%d %H:%M:%S"), tag, json.dumps(f[3]) if f else None))
            write_status(lab, rnd)
        con.commit()
        print(f"round {rnd} strong:", sum(is_strong(it["label"]) for it in todo), "/", len(todo))

    for it in items:
        write_status(it["label"], last_round.get(it["label"], 0), final=True)
    con.commit()
    for row in con.execute("SELECT item, rounds_tried, status, found_decl, found_agreement FROM search_status "
                           f"WHERE model=? AND item IN ({','.join('?' * len(labels))})", (tag, *labels)):
        print(" ", row)


if __name__ == "__main__":
    main()
