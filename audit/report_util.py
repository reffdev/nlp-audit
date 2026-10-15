# SPDX-License-Identifier: Apache-2.0
"""Small helpers shared by report.py and validation.py."""
import re

import config as C


def lines_of(s):
    m = re.match(r"\s*(\d+)\s*(?:-\s*(\d+))?", str(s or ""))
    return (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None


def lean_match_file(quote, lines, shown, decl_file):
    """The file whose shown lines contain the Lean quote at the cited line numbers (extract.check_lean's
    test), preferring the declaration's own file; None if no shown range contains it."""
    ln = lines_of(lines)
    if not ln or not quote:
        return None
    q = re.sub(r"\s+", "", quote)
    hits = []
    for f, x, y in shown:
        if x <= ln[0] <= y or x <= ln[1] <= y:
            src = (C.REPO / f).read_text(encoding="utf-8").splitlines()
            if q in re.sub(r"\s+", "", "".join(src[max(ln[0], x) - 1:min(ln[1], y)])):
                hits.append(f)
    return decl_file if decl_file in hits else (hits[0] if hits else None)
