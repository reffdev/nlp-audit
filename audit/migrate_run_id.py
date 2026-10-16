# SPDX-License-Identifier: Apache-2.0
"""One-time migration: add the run id to the `model` column of every model-derived row written before run ids
existed ("<model>|thinking=1" -> "<model>|thinking=1|run=<id>"). Idempotent.

  python audit/migrate_run_id.py v0.2                         # data/audit.db
  AUDIT_DB=data/audit_v0.1.db python audit/migrate_run_id.py v0.1
"""
import sqlite3
import sys

import config as C

TABLES = ["xref_llm_files", "xref_llm_decls", "search_files", "search_decls", "search_rounds", "search_status",
          "decoy_decls", "decoy_summary", "extract_pairs", "extract_fields", "extract_deltas", "adjudication"]

if __name__ == "__main__":
    run = sys.argv[1]
    con = sqlite3.connect(C.DB)
    have = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for t in TABLES:
        if t in have:
            n = con.execute(f"UPDATE {t} SET model = model || ? WHERE model IS NOT NULL AND model NOT LIKE '%|run=%'",
                            (f"|run={run}",)).rowcount
            print(f"{t}: {n} rows tagged run={run}")
    con.commit()
