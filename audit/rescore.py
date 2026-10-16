# SPDX-License-Identifier: Apache-2.0
"""Re-score stored outputs: recompute every paper-quote check against the corrected context (no model calls).

v0.2's extraction rendered the prompt from paper_text.choose_proof() but verified paper quotes against a
different concatenation of texts. This recomputes, for every paper quote in extract_deltas and extract_fields:
  status in the paper context the model was shown (paper_text.Context): exact / normalized / unresolved-OCR
  status on the cited page
and stores them (paper_status_context, paper_status_page), updates the 0/1 flags from them, and writes
data/rescore_result.json with how many statuses changed.

  python audit/rescore.py
"""
import json
import sqlite3
from collections import Counter

import config as C
import extract as E
import paper_text as PT
import quotes as Q


def contexts(con):
    con.row_factory = sqlite3.Row
    items = {r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_items")}
    items.update({r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_steps")})
    pair_item = dict(con.execute("SELECT pair_id, item FROM extract_pairs").fetchall())
    con.row_factory = None
    return {pid: PT.context(items[it], E.PROOF_CAP).text for pid, it in pair_item.items() if it in items}


def main():
    con = sqlite3.connect(C.DB)
    ctx = contexts(con)
    res = {}
    for table, quote_col, ok_col, page_col in (("extract_deltas", "paper_quote", "paper_cite_ok", "paper_on_page"),
                                              ("extract_fields", "quote", "cite_ok", "on_page")):
        for col in ("paper_status_context", "paper_status_page"):
            try:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass
        where = "" if table == "extract_deltas" else " WHERE side='paper' AND field!='proof_route'"
        rows = con.execute(f"SELECT rowid, pair_id, {quote_col}, page, {ok_col}, {page_col} FROM {table}{where}").fetchall()
        con.commit()  # quotes.page_text reads through its own connection
        changed_ctx = changed_page = n = 0
        st_ctx, st_page = Counter(), Counter()
        updates = []
        for rowid, pid, quote, page, ok_old, page_old in rows:
            if not quote:
                continue
            n += 1
            sp, sc = Q.check(quote, ctx.get(pid, ""), page)
            ok_new = int(sc in (Q.EXACT, Q.NORMALIZED))
            page_new = None if sp is None else int(sp in (Q.EXACT, Q.NORMALIZED))
            changed_ctx += (ok_old if ok_old is not None else -1) != ok_new
            changed_page += page_old != page_new
            st_ctx[sc] += 1
            st_page[sp] += 1
            updates.append((ok_new, page_new, sc, sp, rowid))
        con.executemany(f"UPDATE {table} SET {ok_col}=?, {page_col}=?, paper_status_context=?, paper_status_page=? "
                        f"WHERE rowid=?", updates)
        res[table] = dict(quotes=n, context_flag_changed=changed_ctx, page_flag_changed=changed_page,
                          context_status=dict(st_ctx), page_status={str(k): v for k, v in st_page.items()})
    con.commit()
    (C.DATA / "rescore_result.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
