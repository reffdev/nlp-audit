# SPDX-License-Identifier: Apache-2.0
"""Clear the tables a run derives from model output, so a rerun starts clean. The indexes (paper_*, lean_*,
ocr_blocks, xref_candidates, ...) are kept. Model responses stay cached in data/llm_raw.jsonl, so prompts
whose text has not changed are answered from the cache rather than resampled.

  python audit/reset_run.py
"""
import sqlite3

import config as C

TABLES = ["xref_llm_files", "xref_llm_decls", "search_files", "search_decls", "search_rounds", "search_status",
          "decoy_decls", "decoy_summary", "paper_steps", "extract_pairs", "extract_fields", "extract_deltas",
          "paper_downstream", "adjudication"]

if __name__ == "__main__":
    con = sqlite3.connect(C.DB)
    for t in TABLES:
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.commit()
    print("cleared:", ", ".join(TABLES))
