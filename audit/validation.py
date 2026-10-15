# SPDX-License-Identifier: Apache-2.0
"""Validation against known discrepancies, by location and type rather than wording.

A target in audit.toml ([[validation]]) names a paper item, the Lean declaration, the Lean lines where the
known discrepancy sits, and the difference types that count. A sample "hits" the target when it reported a
difference of one of those types whose cited Lean lines overlap the target lines, and whose Lean quote is
actually found at those lines of the declaration's own file (an unplaceable quote is not a hit). The result is counted per sample (k of 3), so it doesn't depend on how report.py groups differences,
and no wording is involved.

The control runs the same check everywhere else: over every other extracted pair, a window of the same
number of lines slides along the declaration's statement, and fires when all samples reported a difference
of the allowed types overlapping it. The share of windows (and of pairs) that fire is the base rate a
target hit should be compared with.
"""
import sqlite3
from collections import defaultdict

import config as C
from report_util import lean_match_file, lines_of
from static_checks import full_statement


def _deltas(con, pair_id):
    return [dict(r) for r in con.execute(
        "SELECT sample, type, lean_lines, lean_quote, description FROM extract_deltas WHERE pair_id=?", (pair_id,))]


def _overlaps(a, b):
    return a and b and a[0] <= b[1] and b[0] <= a[1]


def _own_file(con, deltas, decl, decl_file):
    """Keep deltas whose Lean quote is found at the cited lines of the declaration's own file."""
    import extract as E
    shown = E.lean_context(con, decl)[1]
    out = []
    for d in deltas:
        f = lean_match_file(d["lean_quote"], d["lean_lines"], shown, decl_file)
        if f == decl_file:
            out.append(d)
    return out


def samples_at(deltas, lines, types):
    """Samples that reported a difference of an allowed type overlapping `lines`."""
    return sorted({d["sample"] for d in deltas
                   if d["type"] in types and _overlaps(lines_of(d["lean_lines"]), lines)})


def statement_lines(con, decl):
    r = con.execute("SELECT file, decl_line, line_end FROM lean_decls WHERE name=?", (decl,)).fetchone()
    if not r:
        return None
    d = dict(file=r[0], decl_line=r[1], line_end=r[2])
    return r[1], r[1] + full_statement(d).count("\n")


def check(con, v):
    """{target, samples (list), k, hits (deltas), control: {...}} for one validation entry."""
    con.row_factory = sqlite3.Row
    lines = lines_of(v["lines"])
    types = set(v["types"])
    pairs = [dict(r) for r in con.execute("SELECT pair_id, item, decl, decl_file FROM extract_pairs")]
    target = next((p for p in pairs if p["item"] == v["item"] and p["decl"] == v["decl"]), None)
    res = dict(target=v, samples=[], k=0, hits=[], extracted=target is not None)
    if target:
        ds = _own_file(con, _deltas(con, target["pair_id"]), target["decl"], target["decl_file"])
        res["samples"] = samples_at(ds, lines, types)
        res["k"] = len(res["samples"])
        res["hits"] = [d for d in ds if d["sample"] in res["samples"] and d["type"] in types
                       and _overlaps(lines_of(d["lean_lines"]), lines)]
    # control: same check, same window width, every other pair's statement
    width = lines[1] - lines[0] + 1
    windows = fired = pairs_fired = n_pairs = 0
    for p in pairs:
        if target and p["pair_id"] == target["pair_id"]:
            continue
        span = statement_lines(con, p["decl"])
        if not span:
            continue
        ds = _own_file(con, _deltas(con, p["pair_id"]), p["decl"], p["decl_file"])
        n_pairs += 1
        any_fire = False
        a, b = span
        for start in range(a, max(a, b - width + 1) + 1):
            windows += 1
            if len(samples_at(ds, (start, start + width - 1), types)) >= 3:
                fired += 1
                any_fire = True
        pairs_fired += any_fire
    res["control"] = dict(windows=windows, fired=fired, pairs=n_pairs, pairs_fired=pairs_fired,
                          window_rate=fired / windows if windows else 0.0,
                          pair_rate=pairs_fired / n_pairs if n_pairs else 0.0)
    return res


def check_all(con):
    return [check(con, v) for v in C.VALIDATION]


def describe(r):
    v, c = r["target"], r["control"]
    where = f"{v['decl'].split('.', 1)[-1]}, line{'s' if '-' in str(v['lines']) else ''} {v['lines']}"
    if not r["extracted"]:
        return f"{v['item']}: not extracted"
    return (f"{v['item']}: {r['k']} of 3 samples reported a {' / '.join(sorted(v['types']))} difference at "
            f"{where}. Control: the same check fires on {c['pairs_fired']} of the other {c['pairs']} pairs, "
            f"and on {c['fired']} of {c['windows']} windows ({c['window_rate']:.1%}) along their statements.")


if __name__ == "__main__":
    con = sqlite3.connect(C.DB)
    for r in check_all(con):
        print(describe(r))
