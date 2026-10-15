# SPDX-License-Identifier: Apache-2.0
"""Which proof text goes into prompts, and whether each prompt's paper context is complete.

Every item has two versions of its proof: the PDF text layer (paper_index.py; complete, but displayed math
is garbled) and the OCR'd LaTeX (ocr_attach.py; readable math, but its block boundaries can end a proof
early or let it run on). choose_proof() uses the OCR version only when it is not materially shorter than the
text layer and ends where a proof ends; otherwise it falls back to the text layer. Every case where the two
disagree in length by more than MARGIN is logged in the table paper_proof_choice.

  python audit/paper_text.py     # writes paper_proof_choice and prints the completeness check
"""
import re
import sqlite3

import config as C
from ocr_attach import PROOF_END

MARGIN = 0.10           # the OCR proof may be this much shorter than the text layer (LaTeX markup varies)
TEXT_END = re.compile(r"[□∎]\s*$")
CONTEXT_UNAVAILABLE = "context unavailable"


def choose_proof(it):
    """(proof text, source, reason) for a paper_items row (dict)."""
    ocr, txt = (it.get("proof_latex") or "").strip(), (it.get("proof") or "").strip()
    if not ocr:
        return txt, "text layer", "no OCR proof"
    if not txt:
        return ocr, "OCR", "no text-layer proof"
    if len(ocr) < (1 - MARGIN) * len(txt):
        return txt, "text layer", f"OCR proof {len(ocr)} chars vs text layer {len(txt)}"
    if not PROOF_END.search(ocr) and TEXT_END.search(txt):
        return txt, "text layer", "OCR proof does not end at a proof-end marker"
    return ocr, "OCR", "OCR proof complete"


def ends_complete(text):
    """Whether a proof text ends at a proof-end marker (either version's)."""
    t = (text or "").strip()
    return bool(PROOF_END.search(t) or TEXT_END.search(t))


def log_choices(con):
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute("SELECT * FROM paper_items WHERE has_proof=1")]
    con.row_factory = None
    out = []
    for it in rows:
        text, src, why = choose_proof(it)
        lo, lt = len((it.get("proof_latex") or "").strip()), len((it.get("proof") or "").strip())
        if lo and lt and abs(lo - lt) > MARGIN * lt or src == "text layer":
            out.append((it["label"], lt, lo, src, why, int(ends_complete(text))))
    con.execute("DROP TABLE IF EXISTS paper_proof_choice")
    con.execute("CREATE TABLE paper_proof_choice (label, text_layer_chars, ocr_chars, chosen, reason, ends_at_marker)")
    con.executemany("INSERT INTO paper_proof_choice VALUES (?,?,?,?,?,?)", out)
    con.commit()
    return out


def context_check(con, cap):
    """For every extracted pair: does its paper context end at a proof-end marker (or, without a proof, at the
    statement's end; for a proof step, is its surrounding proof text available)? Returns the failing items."""
    con.row_factory = sqlite3.Row
    items = {r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_items")}
    steps = {}
    if con.execute("SELECT name FROM sqlite_master WHERE name='paper_steps'").fetchone():
        steps = {r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_steps")}
    con.row_factory = None
    bad = []
    for (item,) in con.execute("SELECT DISTINCT item FROM extract_pairs"):
        if item in steps:
            if (steps[item].get("context") or "ok") != "ok":
                bad.append((item, CONTEXT_UNAVAILABLE))
            continue
        it = items.get(item)
        if not it or not it["has_proof"]:
            continue
        text = choose_proof(it)[0]
        if len(text) > cap:
            bad.append((item, f"proof longer than the {cap}-character cap"))
        elif not ends_complete(text):
            bad.append((item, "proof text does not end at a proof-end marker"))
    return bad


if __name__ == "__main__":
    con = sqlite3.connect(C.DB)
    rows = log_choices(con)
    print(f"proofs where the text layer is used or the versions differ by >{MARGIN:.0%}: {len(rows)}")
    for r in rows:
        print(f"  {r[0]}: text {r[1]}, OCR {r[2]} -> {r[3]} ({r[4]}){'' if r[5] else '  [no end marker]'}")
