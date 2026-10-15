# SPDX-License-Identifier: Apache-2.0
"""Phase 0b: attach OCR'd LaTeX to the paper index, cross-checked against the PDF text layer.

Marker (data/ocr/<stem>/<stem>.json, see audit/fetch.py --ocr) gives layout-aware LaTeX per block, with a
bounding box in PDF points. The PDF's own text layer gives the exact typeset glyphs in that box
but loses layout. For every block we compare the multiset of significant symbols (letters,
digits, Greek, a few operators, hat/tilde accents) on both sides. Any difference flags the block;
flagged blocks should be read from the page image (data/pages/pNNN.png).

Blind spot: a symbol present on both sides but in the wrong position (e.g. sub- vs superscript)
is not caught.

Output: table ocr_blocks; new columns on paper_items (statement_latex, proof_latex,
ocr_flagged_blocks) and paper_equations (latex, ocr_block, ocr_flagged, ocr_pdf_only, ocr_ocr_only).
"""
import html
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from pathlib import Path

import pdfplumber
from pylatexenc.latex2text import LatexNodes2Text

import config as C

ROOT = Path(__file__).resolve().parent.parent
DB = C.DB
OCR = C.OCR_JSON
PDF = C.PDF

SKIP = {"PageHeader", "PageFooter", "TableOfContents", "Figure", "Picture"}
GROUPS = {"ListGroup", "TableGroup", "FigureGroup", "PictureGroup"}
KINDS = C.KINDS
L2T = LatexNodes2Text()
OPS = set("∂∇∑∫∞≤≥=+−∈⊂×≠")
ACCENTS = {"̂": "^", "ˆ": "^", "̃": "~", "˜": "~"}
# Same symbol, different code points (PDF increment sign vs OCR Greek Delta, dash variants).
# П/□ are the end-of-proof box, which OCR often reads as Cyrillic Pe.
SAME = str.maketrans({"∆": "Δ", "Ω": "Ω", "-": "−", "–": "−", "—": "−",
                      "‐": "−", "П": None, "□": None})


def tokens(s, casefold=False):
    """Multiset of significant symbols in already-unicode text."""
    s = re.sub(r"[︀-️]", "", s)
    s = s.replace("̸=", "≠").replace("≠", "≠")  # PDF draws ≠ as overlay stroke + "="
    s = re.sub(r"[−-]+(?=[→⟶])", "", s)  # long arrows are typeset as minus + arrow
    s = re.sub(r"=+(?=[⇒⟹])", "", s)  # ...and long double arrows as "=" + ⇒
    if casefold:  # prose blocks: small caps in the PDF are lower-case glyphs
        s = s.casefold()
    out = Counter()
    for ch in s.translate(SAME):
        if ch == "≠":
            out[ch] += 1
            continue
        for c in unicodedata.normalize("NFKD", ch):
            if c in ACCENTS:
                out[ACCENTS[c]] += 1
            elif c.isalnum() or c in OPS:
                out[c.translate(SAME)] += 1
    return out


def latex_to_unicode(tex):
    # Marker sometimes leaves literal "\n" in the LaTeX; keep real macros (\nabla, \nu, \neq, ...)
    tex = re.sub(r"\\n(?!abla|u\b|u[_^\s\\{}]|eq|e\b|ot|olimits|i\b|eg|less|mid|parallel|earrow|warrow)", " ", tex)
    # operator names that the LaTeX-to-text converter drops
    tex = re.sub(r"\\(det|max|min|sup|inf|log|exp|lim|limsup|liminf|sin|cos|tan|arg|deg|dim|ker|tr|Re|Im)\b",
                 r" \1 ", tex)
    tex = re.sub(r"\\[bp]?mod\b", " mod ", tex)
    tex = re.sub(r"\\(?:widehat|hat)\s*", r"\\hat ", tex)
    tex = re.sub(r"\\(?:widetilde|tilde)\s*", r"\\tilde ", tex)
    tex = re.sub(r"\\\||\\[lr]?Vert\b", "∥", tex)
    tex = re.sub(r"\\tag\{([^}]*)\}", r"(\1)", tex)
    tex = re.sub(r"\\(?:operatorname|text|mathrm|textrm)\s*\{", "{", tex)
    try:
        return L2T.latex_to_text(tex)
    except Exception:
        return tex


def block_text(h):
    """(markdown-ish text with $latex$, unicode text) for a block's HTML."""
    h = re.sub(r"<span id=\"[^\"]*\"></span>", "", h)
    md, uni = [], []
    for part in re.split(r"(<math[^>]*>.*?</math>)", h, flags=re.S):
        m = re.match(r"<math([^>]*)>(.*?)</math>", part, re.S)
        if m:
            tex = html.unescape(m.group(2)).strip()
            disp = "block" in m.group(1)
            md.append(f"$${tex}$$" if disp else f"${tex}$")
            uni.append(latex_to_unicode(tex))
        else:
            t = html.unescape(re.sub(r"<[^>]+>", "", part))
            md.append(t)
            uni.append(t)
    return re.sub(r"[ \t]+", " ", "".join(md)).strip(), "".join(uni)


def flatten(page):
    for b in page.get("children") or []:
        if b["block_type"] in GROUPS:
            for c in b.get("children") or []:
                yield c
        elif b["block_type"] not in SKIP:
            yield b


# End of a proof as OCR writes it: a box glyph (or a misread П), or a LaTeX box command, at the end of a block.
PROOF_END = re.compile(r"(?:[□П∎]|\\(?:Box|square|qed|blacksquare)\b)\s*\$*\s*$")


def main():
    doc = json.loads(OCR.read_text(encoding="utf-8"))
    pdf = pdfplumber.open(PDF)
    blocks = []
    for pi, page in enumerate(doc["children"]):
        chars = pdf.pages[pi].chars
        for b in flatten(page):
            x0, y0, x1, y1 = b["bbox"]
            md, uni = block_text(b["html"])
            pdf_txt = "".join(c["text"] for c in chars
                              if x0 - 1 <= (c["x0"] + c["x1"]) / 2 <= x1 + 1
                              and y0 - 1 <= (c["top"] + c["bottom"]) / 2 <= y1 + 1)
            prose = b["block_type"] in ("Text", "Caption", "SectionHeader")
            tp, to = tokens(pdf_txt, prose), tokens(uni, prose)
            pdf_only, ocr_only = tp - to, to - tp
            blocks.append(dict(
                id=b["id"], pdf_page=pi + 1, block_type=b["block_type"],
                bbox=json.dumps([round(v, 1) for v in b["bbox"]]), text=md, pdf_text=pdf_txt,
                pdf_only="".join(sorted(pdf_only.elements())) or None,
                ocr_only="".join(sorted(ocr_only.elements())) or None,
                flagged=int(bool(md) and bool(pdf_only or ocr_only)),  # empty = mislabelled running head
                n_symbols=sum(tp.values()),
            ))

    con = sqlite3.connect(DB)
    con.execute("DROP TABLE IF EXISTS ocr_blocks")
    cols = list(blocks[0])
    con.execute(f"CREATE TABLE ocr_blocks (seq INTEGER, {', '.join(cols)})")
    con.executemany(f"INSERT INTO ocr_blocks VALUES (?, {', '.join('?' * len(cols))})",
                    [(i, *[b[c] for c in cols]) for i, b in enumerate(blocks)])

    # --- segment items in OCR reading order ---
    hdr = re.compile(rf"^\**\s*({KINDS})\s+((?:\d+|[A-C])\.\d+)\b")
    item_rows = {r[0]: r for r in con.execute("SELECT label, has_proof FROM paper_items")}
    starts = []
    for i, b in enumerate(blocks):
        m = hdr.match(b["text"])
        if m and f"{m.group(1)} {m.group(2)}" in item_rows and b["block_type"] != "SectionHeader":
            label = f"{m.group(1)} {m.group(2)}"
            if label not in [s[1] for s in starts]:
                starts.append((i, label))
    # A block ends an item only if it is a real section or subsection heading. Marker labels the running
    # heads ("FINITE TIME BLOWUP ...", "OPENAI", or empty) and proof-step titles ("Step 2: ...") as
    # SectionHeader too; treating those as stops cut proofs off at page boundaries.
    known = {str(r[0]) for r in con.execute("SELECT number FROM paper_sections")}
    known |= {str(r[0]) for r in con.execute("SELECT DISTINCT subsection FROM paper_items WHERE subsection IS NOT NULL")}
    head = re.compile(r"^[#\s*]*(?:appendix\s+([A-C])\b|((?:\d+|[A-C])(?:\.\d+)?)\.\s|references\b)", re.I)

    def real_heading(b):
        m = head.match(b["text"] or "")
        if not m:
            return False
        num = m.group(1) or m.group(2)
        return num is None or num.upper() in known or num in known

    hard_stops = {i for i, b in enumerate(blocks)
                  if (b["block_type"] == "SectionHeader" and real_heading(b))
                  or re.match(r"^\**\s*(?:\d+|[A-C])\.\d+\.\s", b["text"])}
    hard_stops |= {s[0] for s in starts}
    for col in ("statement_latex", "proof_latex", "ocr_statement_blocks", "ocr_proof_blocks",
                "ocr_flagged_blocks"):
        try:
            con.execute(f"ALTER TABLE paper_items ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    found = set()
    for i, label in starts:
        end = min([s for s in hard_stops if s > i] + [len(blocks)])
        stmt, proof, in_proof = [], [], False
        for j in range(i, end):
            t = blocks[j]["text"]
            if not in_proof and j > i and re.match(r"^\**\s*\*?Proof\b", t):
                in_proof = True
            if in_proof:
                proof.append(j)
                if PROOF_END.search(t):
                    break
            elif item_rows[label][1] or j == i or blocks[j]["block_type"] in ("Equation", "ListItem") \
                    or not stmt or blocks[stmt[-1]]["block_type"] == "Equation":
                stmt.append(j)  # no-proof items: stop at the first plain paragraph after the statement
            else:
                break
        if item_rows[label][1] and not proof:
            stmt = stmt[:]  # proof marker not found in OCR; keep what we have
        flagged = sum(blocks[j]["flagged"] for j in stmt + proof)
        con.execute("UPDATE paper_items SET statement_latex=?, proof_latex=?, ocr_statement_blocks=?, "
                    "ocr_proof_blocks=?, ocr_flagged_blocks=? WHERE label=?",
                    ("\n\n".join(blocks[j]["text"] for j in stmt),
                     "\n\n".join(blocks[j]["text"] for j in proof) or None,
                     json.dumps([blocks[j]["id"] for j in stmt]),
                     json.dumps([blocks[j]["id"] for j in proof]), flagged, label))
        found.add(label)

    # --- equations: label as \tag{} or "(8.19)" after the math ---
    for col in ("latex", "ocr_block", "ocr_flagged", "ocr_pdf_only", "ocr_ocr_only"):
        try:
            con.execute(f"ALTER TABLE paper_equations ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass
    eq_nums = {r[0] for r in con.execute("SELECT number FROM paper_equations")}
    eq_found = set()
    for b in blocks:
        if b["block_type"] not in ("Equation", "TextInlineMath", "Text", "ListItem"):
            continue
        for m in re.finditer(r"\\tag\{\s*((?:\d+|[A-C])\.\d+)\s*\}|\$\$\s*\(((?:\d+|[A-C])\.\d+)\)\s*$|"
                             r"\$\$\s*\(((?:\d+|[A-C])\.\d+)\)", b["text"]):
            num = m.group(1) or m.group(2) or m.group(3)
            if num not in eq_nums or num in eq_found:
                continue
            eq_found.add(num)
            con.execute("UPDATE paper_equations SET latex=?, ocr_block=?, ocr_flagged=?, ocr_pdf_only=?, "
                        "ocr_ocr_only=? WHERE number=?",
                        (b["text"], b["id"], b["flagged"], b["pdf_only"], b["ocr_only"], num))
    # fallback: label written somewhere unusual; take the math block on the same page that mentions it
    for num, page in con.execute("SELECT number, pdf_page FROM paper_equations").fetchall():
        if num in eq_found:
            continue
        for b in blocks:
            if b["pdf_page"] == page and b["block_type"] in ("Equation", "TextInlineMath") \
                    and re.search(rf"[({{]\s*{re.escape(num)}\s*[)}}]", b["text"]):
                eq_found.add(num)
                con.execute("UPDATE paper_equations SET latex=?, ocr_block=?, ocr_flagged=?, ocr_pdf_only=?, "
                            "ocr_ocr_only=? WHERE number=?",
                            (b["text"], b["id"], b["flagged"], b["pdf_only"], b["ocr_only"], num))
                break
    con.commit()

    n = len(blocks)
    by = Counter((b["block_type"], b["flagged"]) for b in blocks)
    print(f"blocks={n} flagged={sum(b['flagged'] for b in blocks)}")
    for t in sorted({b['block_type'] for b in blocks}):
        print(f"  {t:16s} {by[(t,1)]:4d}/{by[(t,0)]+by[(t,1)]:4d} flagged")
    print(f"items matched in OCR: {len(found)}/{len(item_rows)}; missing: {sorted(set(item_rows) - found)}")
    print(f"equations matched in OCR: {len(eq_found)}/{len(eq_nums)}")


if __name__ == "__main__":
    main()
