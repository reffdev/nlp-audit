"""Phase 0: structured index of the Navier-Stokes paper.

Reads `pdftotext -enc UTF-8 -layout` output (pages separated by form feeds) and
records every numbered Lemma/Proposition/Theorem/Corollary/Definition/Remark and
every numbered displayed equation, with section, page, statement and proof text.
Also records every in-text reference to an item or equation (for downstream-use counts).

Output: SQLite tables paper_sections, paper_items, paper_equations, paper_refs
in data/audit.db, plus JSONL mirrors in data/.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TXT = ROOT / "data" / "paper_layout.txt"
DB = ROOT / "data" / "audit.db"

KINDS = "Lemma|Proposition|Theorem|Corollary|Definition|Remark"
NUM = r"(?:\d+|[A-C])\.\d+"
ITEM_HDR = re.compile(rf"^\s{{0,4}}({KINDS})\s+({NUM})(\s*\([^)]*\)?)?\.\s")
SUBSEC_HDR = re.compile(r"^\s{0,4}((?:\d+|[A-C])\.\d+)\.\s+(\S.*?)\.(\s|$)")
# Equation label at the right margin: whitespace, then (8.19), nothing after. Labels are sometimes
# only one or two spaces after the display, so short gaps are accepted unless the label reads as prose
# ("... given in (8.19)").
EQ_LABEL = re.compile(rf"(\s+)\(({NUM})\)\s*$")
PROSE_BEFORE = re.compile(
    r"(?:^|\s)(in|by|of|and|or|from|see|to|with|Equation|Equations|as|the|via|using|under|gives?|yields?|"
    r"satisf(?:y|ies)|into|for|that|then|on|is|are|also|both|which|than|after|before|follows?|proves?|"
    r"bounds?|identity|identities|estimates?|constraints?|equation|equations|condition|conditions|"
    r"formula|system|problem|definition)\s*$", re.IGNORECASE)


def eq_label(ln):
    """Return the equation number if `ln` ends in a displayed-equation label, else None."""
    m = EQ_LABEL.search(ln)
    if not m:
        return None
    before = ln[:m.start()]
    if len(m.group(1)) < 3:
        if PROSE_BEFORE.search(before) or not re.search(r"[=≤≥<>∥∫∑≍∈⊂→⊆]", before):
            return None
    return m.group(2)
PROOF_START = re.compile(r"^\s{0,4}Proof\b[^.]*\.")
QED = "□"
REF = re.compile(
    rf"\b({KINDS}|Equations?|Eq\.)\s+({NUM})(\([ivx]+\))?|\(({NUM})\)")
RUNNING_HEAD = re.compile(r"^\s*(\d+\s+OPENAI|FINITE TIME BLOWUP FOR NAVIER–STOKES\s+\d+)\s*$")


def load_lines():
    text = TXT.read_text(encoding="utf-8")
    pages = text.split("\f")
    lines = []  # (pdf_page, printed_page, text)
    for pi, page in enumerate(pages, start=1):
        printed = None
        for ln in page.splitlines()[:3] + page.splitlines()[-3:]:
            m = re.match(r"^\s*(\d+)\s+OPENAI\s*$", ln) or re.match(
                r"^\s*FINITE TIME BLOWUP FOR NAVIER–STOKES\s+(\d+)\s*$", ln) or re.match(r"^\s+(\d+)\s*$", ln)
            if m:
                printed = int(m.group(1))
                break
        for ln in page.splitlines():
            lines.append((pi, printed, ln))
    return lines


def clean(block):
    """Join lines, drop running heads and bare page numbers, collapse blank runs."""
    out = []
    for _, _, ln in block:
        if RUNNING_HEAD.match(ln) or re.match(r"^\s+\d+\s*$", ln):
            continue
        out.append(ln.rstrip())
    txt = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def main():
    lines = load_lines()
    n = len(lines)

    # --- sections, from the table of contents ---
    toc = []
    for i in range(60):
        m = re.match(r"^((\d+)|Appendix ([A-C]))\.\s+(.+?)\s{3,}(\d+)\s*$", lines[i][2])
        if m:
            toc.append((m.group(2) or m.group(3), m.group(4).strip(), int(m.group(5))))
    toc_end = max(i for i in range(60) if lines[i][2].startswith("References")) + 1
    sec_starts = []
    for num, title, _ in toc:
        for i in range(toc_end, n):
            s = lines[i][2].strip()
            if s in (f"{num}. {title}", f"Appendix {num}. {title}"):
                sec_starts.append((i, num, title))
                break
        else:
            print(f"WARN: section {num} header not found", file=sys.stderr)
    refs_start = next(i for i in range(toc_end, n) if lines[i][2].strip() == "References")
    sec_starts.sort()

    def section_at(i):
        cur = (None, None)
        for s, num, title in sec_starts:
            if s <= i:
                cur = (num, title)
        return cur

    subsecs = []
    for i in range(toc_end, refs_start):
        m = SUBSEC_HDR.match(lines[i][2])
        if m and m.group(1).split(".")[0] == section_at(i)[0]:
            subsecs.append((i, m.group(1), m.group(2)))

    def subsection_at(i):
        cur = (None, None)
        for s, num, title in subsecs:
            if s <= i:
                cur = (num, title)
        return cur

    # --- item headers ---
    headers = []
    seen = {}
    for i in range(toc_end, refs_start):
        m = ITEM_HDR.match(lines[i][2].replace("√", ""))
        if not m:
            continue
        kind, num = m.group(1), m.group(2)
        sec = section_at(i)[0]
        if num.split(".")[0] != sec:
            continue  # a reference to an item from another section that wrapped to line start
        prev = next((lines[j][2] for j in range(i - 1, toc_end, -1)
                     if not RUNNING_HEAD.match(lines[j][2])), "")
        if prev.strip() and lines[i - 1][0] == lines[i][0]:
            continue  # real headers start a paragraph; this is prose that wrapped onto "Lemma X.Y."
        if num in seen:
            print(f"WARN: duplicate header {kind} {num} at lines {seen[num]+1},{i+1}", file=sys.stderr)
            continue
        seen[num] = i
        title = (m.group(3) or "").strip().strip("()") or None
        headers.append((i, kind, num, title))

    # boundaries: next item header, subsection header, section header, or references
    boundaries = sorted({h[0] for h in headers} | {s[0] for s in subsecs}
                        | {s[0] for s in sec_starts} | {refs_start})

    def next_boundary(i):
        return next(b for b in boundaries if b > i)

    items = []
    for i, kind, num, title in headers:
        end = next_boundary(i)
        proof_i = next((j for j in range(i + 1, end) if PROOF_START.match(lines[j][2])), None)
        stmt_end = proof_i if proof_i is not None else end
        if proof_i is None:
            # No proof: body-text paragraphs are indented exactly three spaces, statement continuation
            # lines by 0, 4 or 5. End the statement at the first body paragraph.
            stmt_end = next((j for j in range(i + 1, end) if re.match(r"^ {3}(?!\()\S", lines[j][2])), end)
        proof_block, proof_end = [], None
        if proof_i is not None:
            for j in range(proof_i, end):
                proof_block.append(lines[j])
                if QED in lines[j][2]:
                    proof_end = j
                    break
            if proof_end is None:
                proof_end = end - 1
        sec_num, sec_title = section_at(i)
        sub_num, sub_title = subsection_at(i)
        items.append(dict(
            label=f"{kind} {num}", kind=kind, number=num, title=title,
            section=sec_num, section_title=sec_title,
            subsection=sub_num, subsection_title=sub_title,
            pdf_page=lines[i][0], printed_page=lines[i][1],
            line_start=i + 1, stmt_line_end=stmt_end,
            proof_line_start=(proof_i + 1) if proof_i is not None else None,
            proof_line_end=(proof_end + 1) if proof_end is not None else None,
            proof_pdf_page_end=lines[proof_end][0] if proof_end is not None else None,
            has_proof=proof_i is not None,
            proof_has_qed=bool(proof_block) and QED in proof_block[-1][2],
            statement=clean(lines[i:stmt_end]),
            proof=clean(proof_block) if proof_block else None,
        ))

    def item_at(i):
        best = None
        for it in items:
            lo = it["line_start"] - 1
            hi = (it["proof_line_end"] or it["stmt_line_end"]) - 1
            if lo <= i <= hi:
                part = "statement" if i < it["stmt_line_end"] else "proof"
                best = (it["label"], part)
        return best

    # --- equations ---
    equations, eq_seen = [], {}
    for i in range(toc_end, refs_start):
        num = eq_label(lines[i][2])
        if not num:
            continue
        if num.split(".")[0] != section_at(i)[0]:
            continue  # right-margin citation (e.g. the Section 3 summary table), not a label
        if num in eq_seen:
            print(f"WARN: duplicate equation ({num}) at lines {eq_seen[num]+1},{i+1}", file=sys.stderr)
            continue
        eq_seen[num] = i
        # display block: contiguous non-prose lines around the label (stop at blank-then-prose)
        lo = i
        while lo - 1 > toc_end and lines[lo - 1][2].strip() and not re.match(r"^\S", lines[lo - 1][2]) \
                and not eq_label(lines[lo - 1][2]) and i - lo < 6:
            lo -= 1
        hi = i
        while hi + 1 < refs_start and lines[hi + 1][2].strip() and not re.match(r"^\S", lines[hi + 1][2]) \
                and not eq_label(lines[hi + 1][2]) and hi - i < 6:
            hi += 1
        ctx_lo, ctx_hi = max(toc_end, i - 4), min(refs_start, i + 3)
        owner = item_at(i)
        equations.append(dict(
            label=f"({num})", number=num, section=section_at(i)[0],
            subsection=subsection_at(i)[0], pdf_page=lines[i][0], printed_page=lines[i][1],
            line=i + 1, in_item=owner[0] if owner else None, in_part=owner[1] if owner else "prose",
            display=clean(lines[lo:hi + 1]), context=clean(lines[ctx_lo:ctx_hi + 1]),
        ))

    # --- references (for downstream-use counts) ---
    eq_line = {e["number"]: e["line"] - 1 for e in equations}
    refs = []
    for i in range(toc_end, refs_start):
        ln = lines[i][2]
        for m in REF.finditer(ln):
            if m.group(4):  # bare (8.19)
                num, target = m.group(4), f"({m.group(4)})"
                if eq_line.get(num) == i and eq_label(ln) == num:
                    continue  # the label itself
            elif m.group(1).startswith("Eq"):
                target = f"({m.group(2)})"
            else:
                target = f"{m.group(1)} {m.group(2)}"
            owner = item_at(i)
            if owner and owner[0] == target:
                continue
            refs.append(dict(target=target, part=(m.group(3) or None), from_item=owner[0] if owner else None,
                             from_part=owner[1] if owner else "prose", section=section_at(i)[0],
                             subsection=subsection_at(i)[0], pdf_page=lines[i][0], line=i + 1))

    sections = [dict(number=num, title=t, line_start=s + 1, pdf_page=lines[s][0]) for s, num, t in sec_starts]
    sections += [dict(number=num, title=t, line_start=s + 1, pdf_page=lines[s][0]) for s, num, t in subsecs]
    write(sections, items, equations, refs)


def write(sections, items, equations, refs):
    con = sqlite3.connect(DB)
    for name, rows in [("paper_sections", sections), ("paper_items", items),
                       ("paper_equations", equations), ("paper_refs", refs)]:
        con.execute(f"DROP TABLE IF EXISTS {name}")
        cols = list(rows[0].keys())
        con.execute(f"CREATE TABLE {name} ({', '.join(cols)})")
        con.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})",
                        [tuple(r[c] for c in cols) for r in rows])
        with open(ROOT / "data" / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    con.commit()
    print(f"sections+subsections={len(sections)} items={len(items)} equations={len(equations)} refs={len(refs)}")


if __name__ == "__main__":
    main()
