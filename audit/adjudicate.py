# SPDX-License-Identifier: Apache-2.0
"""Adjudication: do the differences grouped together actually say the same thing?

report.py groups differences from the 3 extraction samples by overlapping Lean citations
(`overlapping_citations`, 1-3). Overlap is not agreement: two samples can cite the same lines for different
points. For every group with 2 or more members this script asks the model, in 3 independent samples, only
whether the descriptions assert the same difference (yes/no). Nothing is voted: the table keeps how many of
the 3 adjudication samples said yes, and report.py counts a group's agreement only when all 3 did.

  python audit/adjudicate.py [--dry-run]
Writes table adjudication (group_key, pair_id, type, n_members, yes, no, invalid, model).
"""
import argparse
import time
import sqlite3
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import config as C
import llm
import xref_llm as X
from report_util import group_deltas, group_key

SAMPLES = 3
WORKERS = 5
MAX_TOKENS = 8000

SYSTEM = """You compare short descriptions of a difference between a mathematics paper and a Lean formalization.
Each description was written independently. Decide ONLY whether all of them assert the same difference: the same
thing differs, in the same way. Different wording of the same point counts as the same. Do not judge whether the
difference matters or which side is right.
Answer with strict JSON: {"same": "yes"} or {"same": "no"}."""


def groups(con):
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM extract_deltas ORDER BY pair_id, sample, rowid")]
    con.row_factory = None
    by = defaultdict(list)
    for r in rows:
        by[(r["pair_id"], r["type"])].append(r)
    for (pair_id, t), rs in by.items():
        for g in group_deltas(rs):
            yield pair_id, t, g


def prompt(g):
    parts = [f"Description {k} (independent sample):\n  paper side: {m['paper_side']}\n  Lean side: {m['lean_side']}\n"
             f"  the difference: {m['description']}\n  cited Lean lines: {m['lean_lines']}"
             for k, m in enumerate(g, start=1)]
    return (f"{len(g)} descriptions of a difference of type '{g[0]['type']}':\n\n" + "\n\n".join(parts) +
            f"\n\nDo these {len(g)} descriptions assert the same difference? Answer yes or no as JSON.")


PAUSE_FLAG = C.DATA / "PAUSE_ADJUDICATION"  # while this file exists, adjudication waits before starting


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if PAUSE_FLAG.exists() and not a.dry_run:
        print(f"paused: waiting for {PAUSE_FLAG} to be removed", flush=True)
        while PAUSE_FLAG.exists():
            time.sleep(30)
        print("resumed", flush=True)
    con = sqlite3.connect(C.DB)
    con.execute("""CREATE TABLE IF NOT EXISTS adjudication (group_key, pair_id, type, n_members, yes, no, invalid,
                   model)""")
    jobs = [(pid, t, g) for pid, t, g in groups(con) if len({m["sample"] for m in g}) >= 2]
    if a.dry_run:  # needs no model server
        print(f"groups with 2 or more samples: {len(jobs)}")
        if jobs:
            print(SYSTEM + "\n---\n" + prompt(jobs[0][2]))
        return
    done = {r[0] for r in con.execute("SELECT group_key FROM adjudication WHERE model=?", (X.run_tag(),))}
    jobs = [j for j in jobs if group_key(j[2]) not in done]
    print(f"groups to adjudicate: {len(jobs)}")

    def run(job):
        pid, t, g = job
        res = llm.complete_json(SYSTEM, prompt(g), samples=SAMPLES, max_tokens=MAX_TOKENS, tag="adjudicate")
        ans = [str((r or {}).get("same", "")).strip().lower() for r in res]
        return pid, t, g, sum(x == "yes" for x in ans), sum(x == "no" for x in ans), \
            sum(x not in ("yes", "no") for x in ans)

    with ThreadPoolExecutor(WORKERS) as ex:
        for n, (pid, t, g, yes, no, bad) in enumerate(ex.map(run, jobs), start=1):
            con.execute("INSERT INTO adjudication VALUES (?,?,?,?,?,?,?,?)",
                        (group_key(g), pid, t, len(g), yes, no, bad, X.run_tag()))
            con.commit()
            if n % 50 == 0:
                print(f"  {n}/{len(jobs)}")


if __name__ == "__main__":
    main()
