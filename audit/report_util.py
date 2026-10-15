# SPDX-License-Identifier: Apache-2.0
"""Small helpers shared by report.py and validation.py."""
import hashlib
import json
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


def group_deltas(rows):
    """rows: dicts of one pair & type, ordered by sample. Returns groups holding at most one delta per sample,
    in which every two members match directly: cited Lean lines share at least one line (adjacent lines are
    not merged, since a statement's hypotheses and conclusion sit on consecutive lines), or, when neither
    cites Lean lines, the same paper citation. Each delta joins the group it overlaps most, so groups never
    chain through a middle member."""
    def overlap(a, b):
        la, lb = lines_of(a["lean_lines"]), lines_of(b["lean_lines"])
        if la and lb:
            return max(0, min(la[1], lb[1]) - max(la[0], lb[0]) + 1)
        if not la and not lb and (a["paper_cite"] or "").strip() == (b["paper_cite"] or "").strip():
            return 1
        return 0

    groups = []
    for r in rows:
        best, best_ov = None, 0
        for g in groups:
            if any(m["sample"] == r["sample"] for m in g):
                continue
            ovs = [overlap(r, m) for m in g]
            if min(ovs) > 0 and sum(ovs) > best_ov:
                best, best_ov = g, sum(ovs)
        if best is None:
            groups.append([r])
        else:
            best.append(r)
    return groups


def group_key(members):
    """Stable identifier of a group of deltas, independent of database row order."""
    return hashlib.sha256(json.dumps(sorted((m["sample"], m["type"], str(m["lean_lines"]), m["description"] or "")
                                            for m in members)).encode()).hexdigest()[:16]
