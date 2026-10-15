# SPDX-License-Identifier: Apache-2.0
"""Normalization and checks for quotes from the paper.

norm() makes a quote comparable with the paper's text whether either is written in LaTeX or in Unicode,
without throwing information away: a LaTeX command becomes the character it stands for (\\le -> ≤,
\\alpha -> α) or, when it has no single character, a token such as ⟨frac⟩; presentational commands (\\left,
\\mathrm, spacing) are dropped; braces, dollar signs and whitespace are removed; case is kept. So `x \\ge y`
and `x \\le y` no longer normalize to the same string, as they did in v0.1.

A paper quote is checked twice: against the text of the page its citation points to (the PDF text layer of
that page plus the OCR'd LaTeX of that page), and against the whole text of the item the model was shown.
"""
import re
import sqlite3
import unicodedata
from functools import lru_cache

import config as C

import logging

logging.getLogger("pylatexenc").setLevel(logging.ERROR)
try:
    from pylatexenc.latex2text import LatexNodes2Text
    _L2T = LatexNodes2Text()
except ImportError:  # pragma: no cover
    _L2T = None

DROP = {"left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr", "Bigl", "Bigr", "biggl", "biggr", "Biggl",
        "Biggr", "middle", "displaystyle", "textstyle", "scriptstyle", "mathrm", "operatorname", "text", "textrm",
        "rm", "mathit", "it", "limits", "nolimits", "quad", "qquad", "tag", "nonumber", "notag"}
SAME = str.maketrans({"∆": "Δ", "Ω": "Ω", "-": "−", "–": "−", "—": "−", "‐": "−", "·": "⋅", "∶": ":",
                      "ϵ": "ε", "ϕ": "φ", "ϑ": "θ", "≦": "≤", "≧": "≥", "П": "", "□": "", "∎": ""})


@lru_cache(maxsize=None)
def _macro(name):
    if name in DROP:
        return ""
    u = ""
    if _L2T is not None:
        try:
            u = _L2T.latex_to_text("\\" + name).strip()
        except Exception:
            u = ""
    if u and not u.startswith("\\") and len(u) <= 2:
        return u
    return f"⟨{name}⟩"


def norm(s):
    s = unicodedata.normalize("NFC", s or "")
    s = re.sub(r"\\([a-zA-Z]+)", lambda m: _macro(m.group(1)), s)
    s = re.sub(r"\\[,;:!> ]", "", s)              # LaTeX spacing
    s = re.sub(r"\\([{}$%&_#|])", r"\1", s)       # escaped characters stand for themselves
    s = re.sub(r"[{}$\s]", "", s)
    return s.translate(SAME)


def found(quote, text):
    q = norm(quote)
    return bool(q) and q in norm(text)


@lru_cache(maxsize=None)
def _layout_pages():
    return (C.LAYOUT_TXT.read_text(encoding="utf-8")).split("\f")


@lru_cache(maxsize=None)
def page_text(printed_page):
    """Text of a printed page: its PDF text-layer page plus the OCR'd LaTeX blocks of that page."""
    if printed_page in (None, ""):
        return None
    con = sqlite3.connect(C.DB)
    pdf_pages = {r[0] for r in con.execute(
        "SELECT pdf_page FROM paper_items WHERE printed_page=? UNION SELECT pdf_page FROM paper_equations "
        "WHERE printed_page=?", (printed_page, printed_page))}
    if not pdf_pages:
        try:
            pdf_pages = {int(printed_page)}
        except (TypeError, ValueError):
            return None
    pages = _layout_pages()
    parts = [pages[p - 1] for p in sorted(pdf_pages) if 0 < p <= len(pages)]
    parts += [r[0] or "" for r in con.execute(
        f"SELECT text FROM ocr_blocks WHERE pdf_page IN ({','.join('?' * len(pdf_pages))}) ORDER BY seq",
        sorted(pdf_pages))]
    con.close()
    return "\n".join(parts)


def check(quote, item_text, printed_page):
    """(found on the cited page: 1/0/None if the page is unknown, found anywhere in the item text: 1/0)."""
    pt = page_text(printed_page)
    return (None if pt is None else int(found(quote, pt))), int(found(quote, item_text))
