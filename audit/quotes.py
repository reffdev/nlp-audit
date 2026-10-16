# SPDX-License-Identifier: Apache-2.0
"""Normalization and checks for quotes from the paper.

Each paper quote gets a status against a given text:
  exact            the quote occurs verbatim once whitespace is ignored
  normalized       it occurs after norm(): LaTeX commands become the characters they stand for (\\le -> ≤,
                   \\alpha -> α) or, without a single character, a token such as ⟨frac⟩; presentational
                   commands (\\left, \\mathrm, spacing) and dollar signs are dropped; braces are kept as grouping,
                   except around a single symbol, so x^{n} matches x^n but x^{n+1} does not match x^n+1; case is
                   kept. So `x \\ge y` and `x \\le y` differ, as they did not in v0.1.
  unresolved-OCR   neither; the text it was checked against is partly OCR'd and partly a garbled PDF text layer,
                   so this does not by itself show that the quote is wrong.
A quote is checked against the text of the page its citation points to (the PDF text layer of that page plus
the OCR'd LaTeX of that page) and against the paper context the model was shown (paper_text.Context).
"""
import logging
import re
import sqlite3
import unicodedata
from functools import lru_cache

import config as C

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
EXACT, NORMALIZED, UNRESOLVED = "exact", "normalized", "unresolved-OCR"
SHORT = 3  # normalized quotes this short match almost anywhere


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


_SINGLE = re.compile(r"\{(⟨[A-Za-z]+⟩|[^{}⟨⟩])\}")


def norm(s):
    s = unicodedata.normalize("NFC", s or "")
    s = re.sub(r"\\([a-zA-Z]+)", lambda m: _macro(m.group(1)), s)
    s = re.sub(r"\\[,;:!> ]", "", s)              # LaTeX spacing
    s = re.sub(r"\\([{}$%&_#|])", r"\1", s)       # escaped characters stand for themselves
    s = re.sub(r"[$\s]", "", s)
    s = s.translate(SAME)
    while True:                                   # braces around a single symbol carry no grouping
        t = _SINGLE.sub(r"\1", s)
        if t == s:
            return s
        s = t


def status(quote, text):
    """exact / normalized / unresolved-OCR for a quote against a text; None if there is no quote or text."""
    if not quote or text is None:
        return None
    if re.sub(r"\s+", "", quote) in re.sub(r"\s+", "", text):
        return EXACT
    q = norm(quote)
    if q and q in norm(text):
        return NORMALIZED
    return UNRESOLVED


def found(quote, text):
    return status(quote, text) in (EXACT, NORMALIZED)


def too_short(quote):
    return bool(quote) and len(norm(quote)) <= SHORT


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


def check(quote, context_text, printed_page):
    """(status on the cited page, status in the paper context the model was shown)."""
    return status(quote, page_text(printed_page)), status(quote, context_text)
