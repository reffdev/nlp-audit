# SPDX-License-Identifier: Apache-2.0
"""Summary of the multi-round search: status per item and the overall distribution.

  python audit/search_summary.py
"""
import json
import sqlite3
from collections import Counter
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "audit.db"


def main():
    con = sqlite3.connect(DB)
    plan = json.loads((DB.parent / "phase2_sample.json").read_text())
    rows = con.execute("SELECT s.item, s.rounds_tried, s.status, s.found_decl, s.found_agreement "
                       "FROM search_status s JOIN paper_items p ON p.label = s.item ORDER BY p.rowid").fetchall()
    total = con.execute("SELECT COUNT(*) FROM paper_items").fetchone()[0]

    def bucket(status):
        return "found" if status.startswith("found") else "weak" if status.startswith("weak") else \
            "not found" if status.startswith("not found") else "in progress"

    for name, members in (("all items", None), ("random sample", set(plan["random_sample"])),
                          ("section 8", set(plan["section8"]))):
        sel = [r for r in rows if members is None or r[0] in members]
        c = Counter(bucket(r[2]) for r in sel)
        rounds = Counter(r[1] for r in sel if bucket(r[2]) == "found")
        print(f"{name}: {len(sel)} searched" + (f" of {total}" if members is None else "") + " | " +
              " ".join(f"{k}={c[k]}" for k in ("found", "weak", "not found", "in progress")) +
              " | found by round: " + " ".join(f"r{k}={v}" for k, v in sorted(rounds.items())))
    print()
    for item, rounds, status, decl, agree in rows:
        print(f"  {item:18s} rounds={rounds}  {status:45s} {decl or ''} ({agree or 0}/3)")
    d = con.execute("SELECT SUM(strong), SUM(weak), COUNT(*) FROM decoy_summary").fetchone() \
        if con.execute("SELECT name FROM sqlite_master WHERE name='decoy_summary'").fetchone() else None
    if d and d[2]:
        print(f"\nDECOY TEST: false 'found' (3/3) on unrelated code {d[0]}/{d[2]}; weak (2/3) {d[1]}/{d[2]}")


if __name__ == "__main__":
    main()
