# SPDX-License-Identifier: Apache-2.0
"""Phase 2a: cheap candidate mapping from paper items to Lean declarations (no LLM).

Signals, all stored separately so they can be inspected:
  doc_sim    TF-IDF cosine between the paper item (statement + proof + titles) and the decl docstring
  name_sim   ... and the decl's name + statement identifiers (camelCase/underscore split)
  file_sim   ... and the decl's file: module docstring + file name
  title_sim  section/subsection title vs file name
  explicit   decl docstring or file module doc cites this item's label (old numbering is common,
             so `label_in_paper` records whether a cited label exists in the published paper)
Structural columns: reachable (from the main theorems, a lower bound), xfile_in (number of other
files referencing the decl), kind.

The combined score is only a ranking heuristic for choosing what the LLM stage looks at.
Output: tables xref_candidates (top theorems and top defs per item), xref_files, lean_reach,
lean_explicit_refs.
"""
import re
import sqlite3
from collections import defaultdict, deque
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "audit.db"
TOP_THM, TOP_DEF, TOP_FILES, NEIGHBOURS, POOL_MAX = 15, 10, 35, 3, 60
W = dict(doc=0.35, name=0.25, file=0.30, title=0.10)
EXPLICIT_BONUS = 0.15
MAIN_SUFFIXES = ("navier_stokes_breakdown_R3", "navier_stokes_breakdown_periodic")
LABEL = re.compile(r"\b(Lemma|Proposition|Theorem|Corollary|Definition|Remark)\s+((?:\d+|[A-C])\.\d+)")
STOP = set("""the and for with that this from are its any all each every which there then when where into onto
than such some also only both over under same used uses using give gives given let our their these those one two
theorem lemma proof def fun exact simp intro have show by obtain refine calc rfl apply rw only at hf hp""".split())


def words(s):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s or "")
    s = re.sub(r"[_.'`\\/]", " ", s).lower()
    out = []
    for w in re.findall(r"[a-z]{3,}", s):
        if w in STOP:
            continue
        if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.append(w)
    return out


def ident_text(statement):
    return " ".join(re.findall(r"[A-Za-z][A-Za-z0-9_.']+", statement or ""))


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    items = [dict(r) for r in con.execute("SELECT * FROM paper_items")]
    decls = [dict(r) for r in con.execute(
        "SELECT name, short_name, kind, file, line_start, line_end, docstring, statement FROM lean_decls "
        "WHERE kind != 'instance' AND name NOT LIKE '<anon%'")]
    files = {r["file"]: dict(r) for r in con.execute("SELECT * FROM lean_files")}
    labels_now = {it["label"] for it in items}

    # --- reachability (lower bound: misses implicit simp/instance use) ---
    g = defaultdict(set)
    for s, t in con.execute("SELECT source, target FROM lean_refs"):
        g[s].add(t)
    roots = [d["name"] for d in decls if d["name"].endswith(MAIN_SUFFIXES)]
    reach = set(roots)
    q = deque(roots)
    while q:
        for y in g[q.popleft()]:
            if y not in reach:
                reach.add(y)
                q.append(y)
    decl_file = {d["name"]: d["file"] for d in decls}
    xfile_in = defaultdict(set)
    for s, t in con.execute("SELECT source, target FROM lean_refs"):
        if s in decl_file and t in decl_file and decl_file[s] != decl_file[t]:
            xfile_in[t].add(decl_file[s])
    con.execute("DROP TABLE IF EXISTS lean_reach")
    con.execute("CREATE TABLE lean_reach (name, reachable, xfile_in)")
    con.executemany("INSERT INTO lean_reach VALUES (?,?,?)",
                    [(d["name"], int(d["name"] in reach), len(xfile_in[d["name"]])) for d in decls])

    # --- explicit label citations in Lean docs ---
    explicit = []
    for d in con.execute("SELECT name, file, decl_line, docstring FROM lean_decls WHERE docstring IS NOT NULL"):
        for m in LABEL.finditer(d["docstring"]):
            explicit.append((f"{m.group(1)} {m.group(2)}", "decl", d["name"], d["file"], d["decl_line"]))
    for f in files.values():
        for m in LABEL.finditer(f["module_doc"] or ""):
            explicit.append((f"{m.group(1)} {m.group(2)}", "module", None, f["file"], None))
    con.execute("DROP TABLE IF EXISTS lean_explicit_refs")
    con.execute("CREATE TABLE lean_explicit_refs (label, scope, decl, file, line, label_in_paper)")
    con.executemany("INSERT INTO lean_explicit_refs VALUES (?,?,?,?,?,?)",
                    [(*e, int(e[0] in labels_now)) for e in explicit])
    cited_decl = defaultdict(set)
    cited_file = defaultdict(set)
    for label, scope, dn, fn, _ in explicit:
        (cited_decl[label].add(dn) if scope == "decl" else cited_file[label].add(fn))

    # --- TF-IDF ---
    def j(ws):
        return " ".join(ws)
    item_stmt = [j(words(it["statement"])) for it in items]
    item_proof = [j(words(it["proof"] or "")) for it in items]
    item_title = [j(words(f"{it['title'] or ''} {it['section_title'] or ''} {it['subsection_title'] or ''}"))
                  for it in items]
    fnames = sorted(files)
    file_txt = [j(words(Path(f).stem) * 3 + words(files[f]["module_doc"])) for f in fnames]
    file_name_txt = [j(words(Path(f).stem)) for f in fnames]
    doc_txt = [j(words(d["docstring"])) for d in decls]
    name_txt = [j(words(d["short_name"]) * 2 + words(ident_text(d["statement"]))) for d in decls]

    vec = TfidfVectorizer(analyzer=str.split, sublinear_tf=True, min_df=2, max_df=0.3)
    vec.fit(item_stmt + item_proof + file_txt + doc_txt + name_txt)
    T = lambda xs: vec.transform(xs)
    item_v = normalize(T(item_stmt) + 0.5 * T(item_proof) + 0.5 * T(item_title))
    title_v = normalize(T(item_title))
    doc_sim = (item_v @ normalize(T(doc_txt)).T).toarray()
    name_sim = (item_v @ normalize(T(name_txt)).T).toarray()
    # File level gets its own vocabulary: IDF over the 36k declarations distorts file-text weights,
    # and section-title words pull toward generically named files.
    fvec = TfidfVectorizer(analyzer=str.split, sublinear_tf=True, min_df=2, max_df=0.3)
    fvec.fit(file_txt + item_stmt)
    fsim = (normalize(fvec.transform([f"{a} {b}" for a, b in zip(item_stmt, item_proof)]))
            @ normalize(fvec.transform(file_txt)).T).toarray()
    tsim = (title_v @ normalize(T(file_name_txt)).T).toarray()
    fidx = {f: k for k, f in enumerate(fnames)}
    mod_file = {Path(f).with_suffix("").as_posix().replace("/", "."): f for f in fnames}
    imports_nb = defaultdict(set)
    for f in fnames:
        for mod in (files[f]["imports"] or "").split():
            if mod in mod_file:
                imports_nb[f].add(mod_file[mod])
                imports_nb[mod_file[mod]].add(f)
    dfile = np.array([fidx[d["file"]] for d in decls])
    file_sim, title_sim = fsim[:, dfile], tsim[:, dfile]
    score = W["doc"] * doc_sim + W["name"] * name_sim + W["file"] * file_sim + W["title"] * title_sim

    is_thm = np.array([d["kind"] == "theorem" for d in decls])
    rows, frows = [], []
    for i, it in enumerate(items):
        exp = np.array([d["name"] in cited_decl[it["label"]] or d["file"] in cited_file[it["label"]] for d in decls])
        s = score[i] + EXPLICIT_BONUS * exp
        for group, mask, k in (("theorem", is_thm, TOP_THM), ("def", ~is_thm, TOP_DEF)):
            idx = np.where(mask)[0]
            for rank, di in enumerate(idx[np.argsort(-s[idx])[:k]], start=1):
                d = decls[di]
                rows.append((it["label"], it["section"], group, rank, d["name"], d["kind"], d["file"],
                             d["line_start"], d["line_end"], round(float(s[di]), 4),
                             round(float(doc_sim[i, di]), 4), round(float(name_sim[i, di]), 4),
                             round(float(file_sim[i, di]), 4), round(float(title_sim[i, di]), 4),
                             int(exp[di]), int(d["name"] in reach), len(xfile_in[d["name"]]),
                             int(d["docstring"] is not None)))
        # file-level ranking: file text, title, best decl doc match inside the file. Paper items are
        # usually formalized as a chain of files importing each other, so the pool for the LLM stage
        # is the top text matches plus their direct import neighbours.
        best_doc = np.zeros(len(fnames))
        np.maximum.at(best_doc, dfile, doc_sim[i])
        fs = 0.85 * fsim[i] + 0.15 * best_doc
        order = list(np.argsort(-fs))
        pool = {fi: ("text", r) for r, fi in enumerate(order[:TOP_FILES], start=1)}
        for r, fi in enumerate(order[:TOP_FILES], start=1):
            for nb in sorted(imports_nb[fnames[fi]], key=lambda f: -fs[fidx[f]])[:NEIGHBOURS]:
                if fidx[nb] not in pool and len(pool) < POOL_MAX:
                    pool[fidx[nb]] = ("import-neighbour", order.index(fidx[nb]) + 1)
        for fi, (via, rank) in pool.items():
            frows.append((it["label"], rank, fnames[fi], via, round(float(fs[fi]), 4), round(float(fsim[i, fi]), 4),
                          round(float(tsim[i, fi]), 4), round(float(best_doc[fi]), 4),
                          int(fnames[fi] in cited_file[it["label"]])))

    con.execute("DROP TABLE IF EXISTS xref_candidates")
    con.execute("""CREATE TABLE xref_candidates (item, section, grp, rank, decl, kind, file, line_start, line_end,
                   score, doc_sim, name_sim, file_sim, title_sim, explicit, reachable, xfile_in, has_doc)""")
    con.executemany(f"INSERT INTO xref_candidates VALUES ({','.join('?' * 18)})", rows)
    con.execute("DROP TABLE IF EXISTS xref_files")
    con.execute("CREATE TABLE xref_files (item, text_rank, file, via, score, file_sim, title_sim, best_doc_sim, "
                "explicit)")
    con.executemany("INSERT INTO xref_files VALUES (?,?,?,?,?,?,?,?,?)", frows)
    con.commit()
    print(f"decls={len(decls)} reachable={len(reach)} explicit_refs={len(explicit)} "
          f"(valid labels now: {sum(e[0] in labels_now for e in explicit)}) candidates={len(rows)}")


if __name__ == "__main__":
    main()
