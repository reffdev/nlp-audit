# SPDX-License-Identifier: Apache-2.0
"""Proof-level targets: numbered equations inside proofs, located and extracted like paper results.

Statement-level extraction misses differences inside proofs (e.g. eq. (10.19), inside the proof of
Lemma 10.5). Here every numbered equation in the proof of a chosen paper result becomes its own target
"(n) in proof of <result>", described by the parent's statement plus the proof text around the equation.

Locating, per target (same bar as xref_search: all 3 samples name the same declaration):
  round 1   declarations in the parent's examined files, plus import neighbours of the files of the
            parent's agreed declarations (a proof step usually lives next to the result it serves)
  round 2,3 fresh file selection from the whole catalogue minus examined files, hints first
Extraction then runs through extract.py (--steps).

Tables: paper_steps (the targets); search_* rows use the target label and kind 'ProofStep'.
  python audit/proof_steps.py --items "Lemma 8.2,Lemma 10.5" [--dry-run]
"""
import argparse
import json
import re
import sqlite3
import time
from collections import Counter, defaultdict

import config as C
import llm  # noqa: F401  (configures the shared request limit)
import paper_text as PT
import xref_llm as X
import xref_search as S

MAX_ROUNDS = 3
CONTEXT_BEFORE, CONTEXT_AFTER = 1500, 400


def build_steps(con, parents):
    con.execute("""CREATE TABLE IF NOT EXISTS paper_steps (label, parent, number, printed_page, section, section_title,
                   subsection, subsection_title, statement_latex, ocr_flagged_blocks)""")
    try:
        con.execute("ALTER TABLE paper_steps ADD COLUMN context")
    except sqlite3.OperationalError:
        pass
    steps, unavailable = [], []
    for parent in parents:
        con.row_factory = sqlite3.Row
        p = dict(con.execute("SELECT * FROM paper_items WHERE label=?", (parent,)).fetchone())
        con.row_factory = None
        proof = PT.choose_proof(p)[0]
        for num, page, latex in con.execute("SELECT number, printed_page, latex FROM paper_equations WHERE in_item=? "
                                            "AND in_part='proof' ORDER BY line", (parent,)):
            m = re.search(rf"\\tag\{{\s*{re.escape(num)}\s*\}}|\(\s*{re.escape(num)}\s*\)", proof)
            label = f"({num}) in proof of {parent}"
            if not m:
                # no silent fallback to the bare equation: a step prompt without its proof text is not sent
                print(f"!! {label}: equation not found in the proof text; recorded as '{PT.CONTEXT_UNAVAILABLE}'")
                unavailable.append(label)
                con.execute("DELETE FROM paper_steps WHERE label=?", (label,))
                con.execute("INSERT INTO paper_steps (label, parent, number, printed_page, context) VALUES (?,?,?,?,?)",
                            (label, parent, num, page, PT.CONTEXT_UNAVAILABLE))
                continue
            ctx = proof[max(0, m.start() - CONTEXT_BEFORE): m.end() + CONTEXT_AFTER]
            p_ = (p["section"], p["section_title"], p["subsection"], p["subsection_title"], p["statement_latex"],
                  None, p["ocr_flagged_blocks"])
            text = (f"A numbered step inside the proof of {parent} (page {page}). The target is equation ({num}).\n"
                    f"STATEMENT OF {parent} (context):\n{(p_[4] or p['statement'] or '')[:2500]}\n\n"
                    f"THE STEP ({num}), WITH THE SURROUNDING PROOF TEXT:\n...{ctx}...")
            steps.append(dict(label=label, parent=parent, number=num, printed_page=page, section=p_[0],
                              section_title=p_[1], subsection=p_[2], subsection_title=p_[3], statement_latex=text,
                              ocr_flagged_blocks=p_[6], context="ok"))
    for s in steps:
        con.execute("DELETE FROM paper_steps WHERE label=?", (s["label"],))
        con.execute("INSERT INTO paper_steps (label, parent, number, printed_page, section, section_title, subsection, "
                    "subsection_title, statement_latex, ocr_flagged_blocks, context) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    tuple(s[k] for k in ("label", "parent", "number", "printed_page", "section", "section_title",
                                         "subsection", "subsection_title", "statement_latex", "ocr_flagged_blocks",
                                         "context")))
    con.commit()
    # fields X.paper_block / extract.paper_context expect
    for s in steps:
        s.update(kind="ProofStep", title=None, statement=s["statement_latex"], proof_latex=None, proof=None)
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    parents = [s.strip() for s in a.items.split(",") if s.strip()]
    con = sqlite3.connect(S.DB)
    S.setup(con)
    tag = X.run_tag()
    nb = X.import_neighbours(con)
    steps = build_steps(con, parents)
    by_label = {s["label"]: s for s in steps}

    def parent_files(parent):
        files = set()
        for (fe,) in con.execute("SELECT files_examined FROM search_rounds WHERE item=? AND model=?", (parent, tag)):
            files |= set(json.loads(fe or "[]"))
        agreed = {f for (f,) in con.execute(
            "SELECT file FROM search_decls WHERE item=? AND model=? AND file IS NOT NULL AND decl NOT LIKE '<%' "
            "GROUP BY decl HAVING COUNT(DISTINCT sample) >= 2", (parent, tag))}
        return files | agreed | set().union(*(nb[f] for f in agreed)) if agreed else files

    examined, best, last = defaultdict(set), {}, {}
    jobs, meta = [], {}
    for s in steps:
        files = parent_files(s["parent"])
        votes = {f: 1 for f in files}
        j, n_keep, n_triv = S.decl_jobs(con, s, 1, files, votes)
        jobs += j
        meta[s["label"]] = dict(files=sorted(files), n_decls=n_keep, n_triv=n_triv, n_chunks=len(j))
    print(f"{len(steps)} proof-step targets; round 1: {len(jobs)} chunks, {3 * len(jobs)} calls")
    for lab, m in meta.items():
        print(f"  {lab}: {len(m['files'])} files, {m['n_decls']} decls, {m['n_chunks']} chunks")
    if a.dry_run:
        return
    for s in steps:
        for t in ("search_files", "search_decls", "search_rounds", "search_status"):
            con.execute(f"DELETE FROM {t} WHERE item=? AND model=?", (s["label"], tag))
    con.commit()

    def write_status(lab, rnd, final=False):
        s = by_label[lab]
        b = best.get(lab)
        strong = b and S.classify(b[1]) == "strong"
        st = (f"found in round {b[0]}" if strong else
              (f"weak match (2 of 3 samples) after {rnd} rounds" if b else f"not found after {rnd} rounds")
              if final else "searching")
        f = b[1] if b else None
        con.execute("DELETE FROM search_status WHERE item=? AND model=?", (lab, tag))
        con.execute("INSERT INTO search_status VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (lab, "ProofStep", s["section"], rnd, st, b[0] if b else None, f[0] if f else None,
                     f[1] if f else None, f[2] if f else None, len(examined[lab]), tag, json.dumps(f[3]) if f else None))

    def record(lab, rnd, f):
        c = S.classify(f)
        if c and (lab not in best or (c == "strong" and S.classify(best[lab][1]) != "strong")):
            best[lab] = (rnd, f)

    def finish_round(rnd, labels, started):
        for lab in labels:
            m = meta[lab]
            f = S.found_decl(con, lab, "ProofStep", rnd)
            record(lab, rnd, f)
            last[lab] = rnd
            con.execute("INSERT INTO search_rounds VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (lab, rnd, m.get("offered", 0), m.get("excluded", 0), json.dumps(m.get("hints", [])),
                         json.dumps(m["files"]), m["n_decls"], m["n_triv"], m["n_chunks"], int(S.classify(f) == "strong"),
                         f[0] if f else None, f[2] if f else None, started, time.strftime("%Y-%m-%d %H:%M:%S"), tag,
                         json.dumps(f[3]) if f else None))
            write_status(lab, rnd)
        con.commit()

    started = time.strftime("%Y-%m-%d %H:%M:%S")
    S.run_decl_jobs(con, jobs)
    for s in steps:
        examined[s["label"]] |= set(meta[s["label"]]["files"])
    finish_round(1, [s["label"] for s in steps], started)
    print("round 1 strong:", sum(S.classify(best.get(s["label"], (0, None))[1]) == "strong" for s in steps), "/", len(steps))

    ids, _ = X.catalog(con)
    cat_lines = []
    for fid, (f, doc) in ids.items():
        d = re.sub(r"^#+\s*", "", re.sub(r"\s+", " ", doc or "")).strip()[:X.DOC_CHARS]
        cat_lines.append((fid, f"{fid} | {C.rel(f)} | {d}"))
    for rnd in range(2, MAX_ROUNDS + 1):
        todo = [s for s in steps if last.get(s["label"]) == rnd - 1
                and not (s["label"] in best and S.classify(best[s["label"]][1]) == "strong")]
        if not todo:
            continue
        hints = {}
        for s in todo:
            score = Counter()
            for f in parent_files(s["parent"]):
                for g in nb[f]:
                    score[g] += 1
            hints[s["label"]] = [(f, f"imports/imported by a file of {s['parent']}") for f, _ in score.most_common()
                                 if f not in examined[s["label"]]][:S.MAX_HINTS]
        started = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"round {rnd}: {len(todo)} targets searching")
        picked, offered = S.run_file_round(con, todo, rnd, ids, cat_lines, hints, examined)
        jobs = []
        for s in todo:
            lab = s["label"]
            files = set(picked[lab])
            j, n_keep, n_triv = S.decl_jobs(con, s, rnd, files, picked[lab])
            jobs += j
            meta[lab] = dict(files=sorted(files), n_decls=n_keep, n_triv=n_triv, n_chunks=len(j), offered=offered[lab],
                             excluded=len(examined[lab]), hints=[f for f, _ in hints[lab]])
            examined[lab] |= files
        if jobs:
            S.run_decl_jobs(con, jobs)
        finish_round(rnd, [s["label"] for s in todo], started)
    for s in steps:
        write_status(s["label"], last.get(s["label"], 0), final=True)
    con.commit()
    for row in con.execute("SELECT item, rounds_tried, status, found_decl, found_agreement FROM search_status "
                           "WHERE kind='ProofStep' AND model=?", (tag,)):
        print(" ", row)


if __name__ == "__main__":
    main()
