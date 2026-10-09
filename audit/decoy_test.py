# SPDX-License-Identifier: Apache-2.0
"""Decoy test: does a confident "found" mean anything?

For each sampled paper item, show the declaration stage a pool that is unrelated by construction: the
round-1 files of a donor item from a DIFFERENT section, sharing no file (and no direct import link)
with the item's own round-1 files. Same prompt, same 3 samples, first chunk only. If the model still
reports a "statement" candidate agreed by 3 of 3 (strong) or 2 of 3 (weak), that is a false positive
of the found criterion in xref_search.py. Compare with the real round-1 rates.

Tables: decoy_decls (every sample's candidates), decoy_summary (one row per item).
  python audit/decoy_test.py [--dry-run]
"""
import argparse
import json
import sqlite3
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import llm
import xref_llm as X
import xref_search as S

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "audit.db"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    plan = json.loads(S.PLAN.read_text())
    labels = list(dict.fromkeys(plan["pilot"] + plan["anchors"] + plan["random_sample"]))
    con = sqlite3.connect(DB)
    for item, label, latex in con.execute("SELECT in_item, label, latex FROM paper_equations "
                                          "WHERE in_part='proof' ORDER BY line"):
        X._proof_equations[item].append((label, latex))
    nb = X.import_neighbours(con)
    by_label = {it["label"]: it for it in X.load_items(con, set())}
    tag = X.run_tag()
    files1 = {}
    for lab in labels:
        row = con.execute("SELECT files_examined FROM search_rounds WHERE item=? AND round=1 AND model=?",
                          (lab, tag)).fetchone()
        files1[lab] = set(json.loads(row[0])) if row else set()

    jobs, donors = [], {}
    for i, lab in enumerate(labels):
        own = files1[lab] | set().union(*(nb[f] for f in files1[lab]))
        for k in range(1, len(labels)):
            d = labels[(i + k) % len(labels)]
            if by_label[d]["section"] != by_label[lab]["section"] and files1[d] and not (files1[d] & own):
                donors[lab] = d
                break
        if lab not in donors:
            print(f"no clean donor for {lab}; skipped")
            continue
        d = donors[lab]
        votes = dict(con.execute(
            "SELECT file, COUNT(DISTINCT sample) + SUM(confidence='high') FROM xref_llm_files WHERE item=? AND model=? "
            "AND pass='catalog' AND file NOT LIKE '<%' GROUP BY file", (d, tag)).fetchall())
        j, _, _ = S.decl_jobs(con, by_label[lab], 0, files1[d], votes)
        if j:
            jobs.append((lab, d, j[0]))
    print(f"decoy test: {len(jobs)} items, {3 * len(jobs)} calls")
    for lab, d, j in jobs:
        print(f"  {lab}  <- pool of {d} ({by_label[d]['section']}), {len(j['ids'])} declarations")
    if a.dry_run:
        return

    con.execute("""CREATE TABLE IF NOT EXISTS decoy_decls (item, donor, sample, decl, role, confidence,
                   terms_verified, model)""")
    con.execute("""CREATE TABLE IF NOT EXISTS decoy_summary (item, donor, samples_with_statement, strong, weak,
                   top_decl, top_agreement, model)""")
    for lab, _, _ in jobs:
        con.execute("DELETE FROM decoy_decls WHERE item=? AND model=?", (lab, tag))
        con.execute("DELETE FROM decoy_summary WHERE item=? AND model=?", (lab, tag))
    with ThreadPoolExecutor(S.JOB_WORKERS) as ex:
        futs = {ex.submit(llm.complete_json, X.SYSTEM, j["prompt"], X.SAMPLES, tag=f"decoy:{lab}"): (lab, d, j)
                for lab, d, j in jobs}
        for n_done, f in enumerate(as_completed(futs), start=1):
            lab, d, j = futs[f]
            stmt_samples, agree = set(), defaultdict(set)
            for s, r in enumerate(f.result()):
                for c in (r or {}).get("candidates", []) or []:
                    name, file, _, _, text = j["ids"].get(c.get("decl_id"), (f"<unknown {c.get('decl_id')}>",
                                                                              None, None, None, ""))
                    v = X.verify_terms(c.get("shared_terms"), j["pb"], f"{name} {text}")
                    tv = sum(x["in_paper"] and x["in_lean"] for x in v)
                    con.execute("INSERT INTO decoy_decls VALUES (?,?,?,?,?,?,?,?)",
                                (lab, d, s, name, c.get("role"), c.get("confidence"), tv, tag))
                    roles = ("statement", "definition") if by_label[lab]["kind"] == "Definition" else ("statement",)
                    if c.get("role") in roles:
                        stmt_samples.add(s)
                        if c.get("confidence") in ("high", "medium") and tv > 0:
                            agree[name].add(s)
            top = max(agree.items(), key=lambda kv: len(kv[1]), default=(None, set()))
            n = len(top[1])
            con.execute("INSERT INTO decoy_summary VALUES (?,?,?,?,?,?,?,?)",
                        (lab, d, len(stmt_samples), int(n >= 3), int(n == 2), top[0], n, tag))
            con.commit()
            print(f"  [{time.strftime('%H:%M:%S')}] {n_done}/{len(jobs)} {lab}: top decoy agreement {n}/3", flush=True)

    rows = con.execute("SELECT SUM(strong), SUM(weak), COUNT(*) FROM decoy_summary WHERE model=?", (tag,)).fetchone()
    real = con.execute("SELECT SUM(found_agreement >= 3), SUM(found_agreement = 2), COUNT(*) FROM search_rounds "
                       f"WHERE round=1 AND model=? AND item IN ({','.join('?' * len(labels))})", (tag, *labels)).fetchone()
    print(f"DECOY: strong (false 'found') {rows[0]}/{rows[2]}, weak {rows[1]}/{rows[2]}")
    print(f"REAL round 1: strong {real[0]}/{real[2]}, weak {real[1]}/{real[2]}")


if __name__ == "__main__":
    main()
