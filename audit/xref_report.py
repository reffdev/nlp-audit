# SPDX-License-Identifier: Apache-2.0
"""Phase 2 coverage: how many paper items got a plausible Lean candidate, from sample agreement alone.

Per item, over the 3 independent samples of the declaration stage (no verdicts involved):
  strong    some declaration given role "statement" by all 3 samples, with >= 1 verified shared term
  moderate  ... by 2 of 3 samples
  weak      "statement" by 1 sample only, or only proof-step/definition candidates agreed by >= 2 samples
  none      nothing above (includes items the pipeline has not reached)
File level (all items), over the catalog-pass samples: strong = some file chosen by all 3 samples with
>= 1 verified shared term; moderate = by 2; weak = by 1; none.
Writes table xref_coverage and prints both distributions. Declaration-level numbers are split into the
random sample (the paper-wide estimate), the pilot section and the anchors (data/phase2_sample.json).
"""
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import config as C

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "audit.db"


def main(model_like="%thinking=1"):
    con = sqlite3.connect(DB)
    items = con.execute("SELECT label, kind, section FROM paper_items ORDER BY rowid").fetchall()
    rows = []
    for label, kind, section in items:
        agg = con.execute(
            "SELECT decl, role, COUNT(DISTINCT sample) n, MAX(terms_verified) tv FROM xref_llm_decls "
            "WHERE item=? AND model LIKE ? AND decl NOT LIKE '<%' GROUP BY decl, role", (label, model_like)).fetchall()
        reached = con.execute("SELECT COUNT(*) FROM xref_llm_decls WHERE item=? AND model LIKE ?",
                              (label, model_like)).fetchone()[0] > 0
        stmt = sorted(((n, tv, d) for d, role, n, tv in agg if role == "statement"), reverse=True)
        best_n = max((n for n, tv, _ in stmt if tv > 0), default=0)
        other2 = [d for d, role, n, tv in agg if role != "statement" and n >= 2]
        if not reached:
            level = "not-run"
        elif best_n >= 3:
            level = "strong"
        elif best_n == 2:
            level = "moderate"
        elif stmt or other2:
            level = "weak"
        else:
            level = "none"
        top = [d for n, tv, d in stmt if n == (stmt[0][0] if stmt else 0)][:3]
        rows.append((label, kind, section, level, best_n, len(other2), "; ".join(top)))
    con.execute("DROP TABLE IF EXISTS xref_coverage")
    con.execute("CREATE TABLE xref_coverage (item, kind, section, level, statement_agreement, "
                "agreed_support_decls, top_statement_candidates)")
    con.executemany("INSERT INTO xref_coverage VALUES (?,?,?,?,?,?,?)", rows)
    con.commit()
    # file level, all items
    flev = {}
    for label, kind, section in items:
        agg = con.execute("SELECT file, COUNT(DISTINCT sample), MAX(terms_verified) FROM xref_llm_files "
                          "WHERE item=? AND model LIKE ? AND pass='catalog' AND file NOT LIKE '<%' GROUP BY file",
                          (label, model_like)).fetchall()
        if not agg:
            flev[label] = "not-run"
            continue
        best = max((n for _, n, tv in agg if tv and tv > 0), default=0)
        flev[label] = {3: "strong", 2: "moderate", 1: "weak"}.get(best, "none")
    fr = [v for v in flev.values() if v != "not-run"]
    fc = Counter(fr)
    print(f"FILE LEVEL: items run {len(fr)}/{len(items)}  " +
          " ".join(f"{lv}={fc[lv]} ({100 * fc[lv] / max(1, len(fr)):.0f}%)" for lv in ("strong", "moderate", "weak", "none")))
    con.execute("DROP TABLE IF EXISTS xref_file_coverage")
    con.execute("CREATE TABLE xref_file_coverage (item, level)")
    con.executemany("INSERT INTO xref_file_coverage VALUES (?,?)", list(flev.items()))
    con.commit()

    plan_path = C.PLAN
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        groups = {"random sample": set(plan["random_sample"]),
                  "pilot": set(plan["pilot"]) - set(plan["anchors"]),
                  "anchors": set(plan["anchors"])}
        print("DECLARATION LEVEL:")
        for g, members in groups.items():
            gr = [r for r in rows if r[0] in members and r[3] != "not-run"]
            gc = Counter(r[3] for r in gr)
            print(f"  {g:14s} run {len(gr)}/{len(members)}  " +
                  " ".join(f"{lv}={gc[lv]}" for lv in ("strong", "moderate", "weak", "none")))
    run = [r for r in rows if r[3] != "not-run"]
    c = Counter(r[3] for r in run)
    print(f"items run: {len(run)}/{len(rows)}")
    for lv in ("strong", "moderate", "weak", "none"):
        print(f"  {lv:9s} {c[lv]:3d}  ({100 * c[lv] / max(1, len(run)):.0f}%)")
    print("plausible (strong+moderate):", c["strong"] + c["moderate"])
    for key, idx in (("section", 2), ("kind", 1)):
        print(f"by {key}:")
        for v in sorted({r[idx] for r in run}, key=str):
            cc = Counter(r[3] for r in run if r[idx] == v)
            print(f"  {v:12s} " + " ".join(f"{lv}={cc[lv]}" for lv in ("strong", "moderate", "weak", "none")))


if __name__ == "__main__":
    main(*sys.argv[1:])
