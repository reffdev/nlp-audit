# SPDX-License-Identifier: Apache-2.0
"""Phase 4: aggregate the Phase 3 extractions into tables (CSV + one static HTML page).

Differences from the 3 independent samples are GROUPED, never voted: two deltas of the same pair and
type are the same difference when their cited Lean lines overlap (within 1 line), or, when neither
cites Lean lines, when they cite the same paper location. Each group keeps its agreement (how many of
the 3 samples reported it) and every sample's wording. Nothing here judges whether a difference matters.

Outputs (out/):
  paper_lean_map.csv                       one row per located target: paper result or proof step -> Lean declaration
  audit_table.csv                          one row per (paper item, Lean declaration) pair
  differences.csv                          one row per grouped difference
  paper_items_not_matched.csv              paper items without a confident Lean counterpart (all sections)
  lean_theorems_without_paper_counterpart.csv  theorems in the pilot files not located for any paper item
  report.html                              everything above on one static page
  summary.md                               a GitHub-readable summary of the above
"""
import csv
import html
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config as C  # noqa: E402
from xref_search import trivial  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DB = C.DB
OUT = C.OUT
REPO_URL = C.REPO_BLOB_URL
PAPER_URL = C.PAPER["url"]
SEVERITY = ["stronger-bound", "missing-hypothesis", "different-norm", "missing-supremum", "different-domain",
            "extra-hypothesis", "weaker-bound", "other"]
RANK = {t: i for i, t in enumerate(SEVERITY)}


def lines_of(s):
    m = re.match(r"\s*(\d+)\s*(?:-\s*(\d+))?", str(s or ""))
    return (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None


def group_deltas(rows):
    """rows: dicts of one pair & type. Union deltas from different samples that cite overlapping Lean lines
    (or, without Lean lines, the same paper citation). Overlap means sharing at least one line; adjacent
    lines are not merged, since a statement's hypotheses and conclusion sit on consecutive lines."""
    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(rows):
        for j in range(i + 1, len(rows)):
            b = rows[j]
            la, lb = lines_of(a["lean_lines"]), lines_of(b["lean_lines"])
            same = (la and lb and la[0] <= lb[1] and lb[0] <= la[1]) or \
                   (not la and not lb and (a["paper_cite"] or "").strip() == (b["paper_cite"] or "").strip())
            if same:
                parent[find(i)] = find(j)
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        groups[find(i)].append(r)
    return list(groups.values())


def main():
    OUT.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    repo_commit = C.repo_commit()
    items = {r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_items")}
    if con.execute("SELECT name FROM sqlite_master WHERE name='paper_steps'").fetchone():
        items.update({r["label"]: dict(r) for r in con.execute("SELECT * FROM paper_steps")})
    downstream = Counter(r[0] for r in con.execute("SELECT item FROM paper_downstream"))
    downstream_where = defaultdict(list)
    for r in con.execute("SELECT item, cited_from, part, page FROM paper_downstream ORDER BY line"):
        downstream_where[r[0]].append(f"{r[1]} ({r[2]}, p.{r[3]})")
    pairs = [dict(r) for r in con.execute("SELECT * FROM extract_pairs ORDER BY rowid")]

    # ---- grouped differences ----
    diffs = []
    for p in pairs:
        rows = [dict(r) for r in con.execute("SELECT * FROM extract_deltas WHERE pair_id=? ORDER BY sample, rowid",
                                             (p["pair_id"],))]
        by_type = defaultdict(list)
        for r in rows:
            by_type[r["type"]].append(r)
        for t, rs in by_type.items():
            for g in group_deltas(rs):
                samples = sorted({r["sample"] for r in g})
                rep = g[0]
                ln = lines_of(rep["lean_lines"])
                diffs.append(dict(
                    item=p["item"], decl=p["decl"], type=t, agreement=len(samples), samples=samples,
                    severity=RANK.get(t, len(SEVERITY)),
                    summary=rep["description"], paper_side=rep["paper_side"], lean_side=rep["lean_side"],
                    paper_cite=rep["paper_cite"], page=rep["page"], paper_quote=rep["paper_quote"],
                    paper_quote_verified=all(r["paper_cite_ok"] for r in g if r["paper_quote"]),
                    lean_file=p["decl_file"],
                    lean_lines=(str(ln[0]) if ln[0] == ln[1] else f"{ln[0]}-{ln[1]}") if ln else "",
                    lean_quote=rep["lean_quote"], lean_quote_verified=all(r["lean_cite_ok"] for r in g if r["lean_quote"]),
                    verdict_words=", ".join(sorted({w for r in g for w in (r["verdict_words"] or "").split(", ") if w})),
                    all_wordings=[f"[sample {r['sample']}] {r['description']}" for r in g]))
    diffs.sort(key=lambda d: (d["severity"], -d["agreement"], d["item"], d["decl"]))

    # ---- static, source-level checks (audit/static_checks.py), if run ----
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    depth = ({r[0]: (r[1], r[2]) for r in con.execute("SELECT name, def_depth, def_chain FROM lean_def_depth")}
             if "lean_def_depth" in tables else {})
    hatches = ({r[0]: sum(r[1:]) for r in con.execute(
        "SELECT file, axiom, sorry, admit, native_decide, unsafe FROM static_scan")} if "static_scan" in tables else {})

    def static_cols(decl, file):
        dd = depth.get(decl)
        return dict(def_depth=dd[0] if dd else "", def_chain=dd[1] if dd else "",
                    file_axiom_sorry_admit_native_decide_unsafe=hatches.get(file, ""))

    # ---- pair table ----
    table = []
    for p in pairs:
        ds = [d for d in diffs if d["item"] == p["item"] and d["decl"] == p["decl"]]
        agreed = [d for d in ds if d["agreement"] >= 2]
        top = min(agreed or ds, key=lambda d: (d["severity"], -d["agreement"]), default=None)
        counts = Counter(d["type"] for d in ds if d["agreement"] == 3)
        it = items[p["item"]]
        table.append(dict(
            section=it["section"], item=p["item"], page=it["printed_page"], lean_decl=p["decl"],
            lean_location=f"{p['decl_file']}:{p['decl_lines']}", on_main_proof_path="yes" if p["reachable"] else "not found",
            delta_types_3of3=", ".join(f"{t} x{counts[t]}" for t in SEVERITY if counts[t]),
            delta_types_any=", ".join(sorted({d["type"] for d in ds}, key=lambda t: RANK.get(t, 99))),
            n_differences=len(ds), n_agreed_3of3=sum(d["agreement"] == 3 for d in ds),
            top_difference=(f"[{top['type']}, {top['agreement']}/3] {top['summary']}" if top else ""),
            top_severity=top["severity"] if top else 99, top_agreement=top["agreement"] if top else 0,
            downstream_uses=downstream[p["item"]], samples_valid=p["samples_ok"],
            **static_cols(p["decl"], p["decl_file"])))
    table.sort(key=lambda r: (r["top_severity"], -r["top_agreement"], r["item"]))

    # ---- paper -> Lean map (every located target, whole paper) ----
    decl_loc = {r[0]: f"{r[1]}:{r[2]}-{r[3]}" for r in con.execute(
        "SELECT name, file, line_start, line_end FROM lean_decls")}
    lean_map = []
    for r in con.execute("SELECT * FROM search_status"):
        it = items.get(r["item"], {})
        others = [c["decl"] for c in json.loads(r["found_all"] or "[]") if c["decl"] != r["found_decl"]]
        lean_map.append(dict(
            item=r["item"], kind=r["kind"], section=r["section"], page=it.get("printed_page"),
            status=r["status"], lean_decl=r["found_decl"] or "",
            lean_location=decl_loc.get(r["found_decl"], r["found_file"] or ""),
            agreement=r["found_agreement"] or 0, found_round=r["found_round"] or "",
            rounds_tried=r["rounds_tried"], files_examined=r["files_examined_total"],
            other_agreed_decls="; ".join(others), **static_cols(r["found_decl"], r["found_file"])))
    order = {lab: i for i, lab in enumerate(items)}
    lean_map.sort(key=lambda m: order.get(m["item"], 10**6))

    # ---- unmatched paper items (whole paper) ----
    unmatched = [dict(item=r["item"], section=r["section"], rounds_tried=r["rounds_tried"], status=r["status"],
                      best_candidate=r["found_decl"] or "", candidate_agreement=r["found_agreement"] or 0)
                 for r in con.execute("SELECT * FROM search_status WHERE status NOT LIKE 'found%' ORDER BY item")]

    # ---- Lean theorems in the pilot files with no paper counterpart ----
    located = set()
    for (fa,) in con.execute("SELECT found_all FROM search_status WHERE found_all IS NOT NULL"):
        located |= {c["decl"] for c in json.loads(fa)}
    pilot_files = sorted({p["decl_file"] for p in pairs})
    orphans = []
    for r in con.execute(f"SELECT d.name, d.file, d.line_start, d.line_end, d.docstring, d.statement, d.attributes, "
                         f"l.reachable, l.xfile_in FROM lean_decls d LEFT JOIN lean_reach l ON l.name=d.name "
                         f"WHERE d.kind='theorem' AND d.file IN ({','.join('?' * len(pilot_files))})", pilot_files):
        if r["name"] in located or trivial(r["name"], r["attributes"], r["statement"], r["docstring"]):
            continue
        orphans.append(dict(lean_decl=r["name"], location=f"{r['file']}:{r['line_start']}-{r['line_end']}",
                            used_by_other_files=r["xfile_in"] or 0, on_main_proof_path="yes" if r["reachable"] else "not found",
                            docstring=re.sub(r"\s+", " ", r["docstring"] or "")[:200]))
    orphans.sort(key=lambda r: (-r["used_by_other_files"], r["lean_decl"]))

    # ---- CSVs ----
    def write_csv(name, rows, cols):
        with open(OUT / name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({k: (" | ".join(v) if isinstance(v, list) and k == "all_wordings" else v) for k, v in r.items()})
    write_csv("audit_table.csv", table, ["section", "item", "page", "lean_decl", "lean_location", "on_main_proof_path",
                                         "delta_types_3of3", "delta_types_any", "n_differences", "n_agreed_3of3",
                                         "top_difference", "downstream_uses", "samples_valid", "def_depth",
                                         "def_chain", "file_axiom_sorry_admit_native_decide_unsafe"])
    write_csv("differences.csv", diffs, ["item", "decl", "type", "agreement", "summary", "paper_side", "lean_side",
                                         "paper_cite", "page", "paper_quote", "paper_quote_verified", "lean_file",
                                         "lean_lines", "lean_quote", "lean_quote_verified", "verdict_words", "all_wordings"])
    write_csv("paper_lean_map.csv", lean_map, ["item", "kind", "section", "page", "status", "lean_decl", "lean_location",
                                              "agreement", "found_round", "rounds_tried", "files_examined",
                                              "other_agreed_decls", "def_depth", "def_chain",
                                              "file_axiom_sorry_admit_native_decide_unsafe"])
    write_csv("paper_items_not_matched.csv", unmatched, ["item", "section", "rounds_tried", "status", "best_candidate",
                                                          "candidate_agreement"])
    write_csv("lean_theorems_without_paper_counterpart.csv", orphans,
              ["lean_decl", "location", "used_by_other_files", "on_main_proof_path", "docstring"])

    # ---- HTML ----
    gate = []  # differences that reproduce the validation targets in audit.toml
    for v, pats, types in C.validation_patterns():
        gate += [d for d in diffs if d["item"] == v["item"] and (not types or d["type"] in types)
                 and all(p.search(" ".join(d["all_wordings"])) for p in pats)]
    write_html(table, diffs, unmatched, orphans, gate, repo_commit, downstream_where, items, pilot_files)
    write_shortlist(diffs, gate, repo_commit, items)
    write_summary(table, diffs, lean_map, unmatched, orphans, gate, repo_commit, pilot_files, con)
    print(f"pairs={len(table)} differences={len(diffs)} (3/3: {sum(d['agreement'] == 3 for d in diffs)}) "
          f"unmatched_items={len(unmatched)} orphan_theorems={len(orphans)} -> {OUT}")


SHORTLIST_TYPES = ("stronger-bound", "weaker-bound", "missing-supremum")
SHORTLIST_TIER_B = ("different-norm",)


def write_shortlist(diffs, gate, commit, items):
    """A short list for expert review: differences reported by all 3 samples whose type concerns what is
    estimated (bounds, norms, uniformity), plus the validation hits. Naming and explicit-hypothesis
    differences are left to the full tables."""
    picked = [d for d in diffs if d["agreement"] == 3 and d["type"] in SHORTLIST_TYPES]
    for g in gate:
        if g not in picked:
            picked.append(g)
    picked.sort(key=lambda d: (d["severity"], d["item"], d["decl"]))
    tier_b = [d for d in diffs if d["agreement"] == 3 and d["type"] in SHORTLIST_TIER_B and d not in picked]
    tier_b.sort(key=lambda d: (d["item"], d["decl"]))
    gate_ids = {id(g) for g in gate}
    out = ["# Review shortlist", "",
           "Differences between the paper and the Lean that are probably most worth an expert's time, picked by a "
           "fixed rule rather than by judgment. **No mathematician has reviewed these yet. Each one is a place "
           "where the two say different things, not a claimed error.** All the data is in `out/differences.csv`, "
           "and the method is in `METHODOLOGY.md`.", "",
           *([C.REPORT["target_note"], ""] if C.REPORT.get("target_note") else []),
           "## Part A: differences in what is estimated", "",
           "Every difference that all 3 samples reported as stronger-bound, weaker-bound or missing-supremum"
           + (", plus the known discrepancies used to validate the tool (marked **validation**)." if gate else ".")
           , ""]

    def entry(k, d):
        ln = lines_of(d["lean_lines"])
        url = (f"{REPO_URL}/{commit}/{d['lean_file']}#L{ln[0]}" + (f"-L{ln[1]}" if ln and ln[1] != ln[0] else "")
               if ln else f"{REPO_URL}/{commit}/{d['lean_file']}")
        tag = " · **validation**" if id(d) in gate_ids else ""
        return [f"## {k}. {d['item']} · `{d['decl'].split('.', 1)[-1]}`{tag}", "",
                f"- **Type:** {d['type']} · reported by {d['agreement']}/3 samples",
                f"- **Difference:** {d['summary']}",
                f"- **Paper** ([p.{d['page']}]({PAPER_URL}#page={d['page']}), {d['paper_cite']}): {d['paper_side']}",
                f"  - quote{'' if d['paper_quote_verified'] else ' (not verified)'}: `{d['paper_quote']}`",
                f"- **Lean** ([{d['lean_file'].removeprefix(C.PREFIX)}:{d['lean_lines']}]({url})): {d['lean_side']}",
                f"  - quote{'' if d['lean_quote_verified'] else ' (not verified)'}: `{d['lean_quote']}`", ""]

    k = 0
    for d in picked:
        k += 1
        out += entry(k, d)
    out += ["## Part B: differences in how size is measured", "",
            "Every difference that all 3 samples reported as different-norm. Most of these are the Lean writing a "
            "norm or function class another way (for example a C^m norm as a bound on iterated derivatives). "
            "They're here because the rule picks them up, not because anyone has judged them to matter.", ""]
    for d in tier_b:
        k += 1
        out += entry(k, d)
    (OUT / "review_shortlist.md").write_text("\n".join(out), encoding="utf-8")
    print(f"review shortlist: {len(picked)} entries in part A, {len(tier_b)} in part B")


def md(s, limit=None):
    """Plain text made safe for a GitHub Markdown table cell."""
    s = re.sub(r"\s+", " ", str(s if s is not None else "")).strip()
    if limit and len(s) > limit:
        s = s[:limit - 1].rstrip() + "…"
    return s.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def md_lean(commit, file, lines, label=None):
    ln = lines_of(lines)
    anchor = (f"#L{ln[0]}" + (f"-L{ln[1]}" if ln[1] != ln[0] else "")) if ln else ""
    return f"[{label or file.removeprefix(C.PREFIX) + (':' + lines if lines else '')}]({REPO_URL}/{commit}/{file}{anchor})"


def md_paper(page, label):
    return f"[{md(label)}, p.{page}]({PAPER_URL}#page={page})" if page else md(label)


def write_summary(table, diffs, lean_map, unmatched, orphans, gate, commit, pilot_files, con):
    """out/summary.md: the report in a form GitHub renders, for a first look before the CSVs and report.html."""
    n3 = sum(d["agreement"] == 3 for d in diffs)
    found = [m for m in lean_map if m["status"].startswith("found")]
    results = [m for m in lean_map if m["kind"] != "ProofStep"]
    out = [f"# {C.REPORT.get('short_title', 'Paper vs. Lean audit')}: summary", "",
           "**Preliminary. No mathematician has reviewed any of this yet.** Every entry is a place where the paper "
           "and the Lean say different things, not a claimed error. This page is generated by `audit/report.py`; "
           "the full data is in the CSVs next to it, and `report.html` (download it and open it locally) has every "
           "difference with quotes. How it works: [METHODOLOGY.md](../METHODOLOGY.md).", "",
           f"Paper: [{C.PDF.name}]({PAPER_URL}) · Lean: [{C.REPO_LABEL}]({C.LEAN['repo_url']}) at "
           f"`{commit[:12]}`", "",
           "## At a glance", "",
           f"- **Paper → Lean map:** {sum(1 for m in results if m['status'].startswith('found'))} of {len(results)} "
           f"numbered results matched by all 3 samples; {len(unmatched)} targets without a 3-of-3 match "
           f"(results and proof steps together). A decoy test suggests at least 1 in 10 confident matches could be wrong.",
           f"- **Compared in detail:** {len(table)} (paper result or proof step, Lean declaration) pairs from the "
           f"{C.REPORT.get('pilot_label', 'pilot')} pilot, Lemma 10.5 and selected proof steps.",
           f"- **Differences:** {len(diffs):,} grouped, {n3} of them reported by all 3 samples. Most are naming, or "
           "the Lean spelling out conditions the paper leaves implicit.",
           f"- **Validation:** {len({d['item'] for d in gate})} of {len(C.VALIDATION)} published discrepancies "
           "reported by all 3 samples (see below).",
           "- **Start with** [review_shortlist.md](review_shortlist.md): the differences most worth an expert's time.",
           ""]
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "static_scan" in tables and "static_dupes" in tables:
        hatch = con.execute("SELECT sum(axiom+sorry+admit+native_decide+unsafe), count(*) FROM static_scan "
                            "WHERE in_audit_scope=1").fetchone()
        groups, copies, unref = con.execute("SELECT count(DISTINCT cluster), count(*), sum(referenced_by=0) "
                                            "FROM static_dupes").fetchone()
        out[-2:-2] = [f"- **Static checks** (source text only, nothing compiled): {hatch[0]} uses of `sorry`, "
                      f"`axiom`, `admit`, `native_decide` or `unsafe` in the {hatch[1]} files under "
                      f"`{C.PREFIX}`; {copies} theorems are copies of each other in {groups} groups "
                      f"({unref} copies unreferenced). See [duplicate_statements.csv](duplicate_statements.csv)."]

    if C.VALIDATION:
        out += ["## Validation", "",
                "The two discrepancies Bastounis, Circelli and Hansen published "
                "([arXiv:2610.08144](https://arxiv.org/abs/2610.08144)). These results were put on the target list "
                "because of that paper; the prompts never describe the discrepancies.", ""]
        for d in gate:
            out.append(f"- **{md(d['item'])}** · `{d['decl'].split('.', 1)[-1]}` · {d['agreement']}/3 samples · "
                       f"{md_paper(d['page'], d['paper_cite'] or 'paper')} · "
                       f"{md_lean(commit, d['lean_file'], d['lean_lines'])}: {md(d['summary'])}")
        out.append("")

    by_type = defaultdict(Counter)
    for d in diffs:
        by_type[d["type"]][d["agreement"]] += 1
    out += ["## Differences by type", "",
            "Types always read from the paper towards the Lean, e.g. `stronger-bound` means the paper states a "
            "stronger estimate than the Lean proves. Ordered roughly by how much they could matter.", "",
            "| Type | All 3 samples | 2 of 3 | 1 of 3 | Total |", "|---|--:|--:|--:|--:|"]
    for t in SEVERITY:
        if by_type[t]:
            c = by_type[t]
            out.append(f"| `{t}` | {c[3]} | {c[2]} | {c[1]} | {sum(c.values())} |")
    out += [f"| **Total** | **{n3}** | **{sum(d['agreement'] == 2 for d in diffs)}** | "
            f"**{sum(d['agreement'] == 1 for d in diffs)}** | **{len(diffs)}** |", ""]

    out += ["## Pairs compared", "",
            "Most severe difference first. *Agreed* counts differences reported by all 3 samples. *Main path*: the "
            "declaration is on the detected dependency path of the main theorems (\"not found\" doesn't mean unused). "
            "*Depth*: layers of the formalization's own definitions under the statement.", "",
            "| Paper | Lean declaration | Main path | Agreed / all | Depth | Most severe agreed difference |",
            "|---|---|---|--:|--:|---|"]
    for r in table:
        file, lines = r["lean_location"].rsplit(":", 1)
        out.append(f"| {md_paper(r['page'], r['item'])} | "
                   f"{md_lean(commit, file, lines, '`' + r['lean_decl'].split('.', 1)[-1] + '`')} | "
                   f"{r['on_main_proof_path']} | {r['n_agreed_3of3']} / {r['n_differences']} | {r['def_depth']} | "
                   f"{md(r['top_difference'], 220)} |")
    out.append("")

    out += ["## Paper → Lean map", "",
            f"Every numbered result and proof step that was searched ({len(lean_map)} targets, {len(found)} found). "
            "*Round*: the search round in which all 3 samples agreed (up to 3 rounds, each excluding the files "
            "already read).", "", "<details><summary>Show the map</summary>", "",
            "| Paper | Status | Lean declaration | Agreement | Round | Depth |", "|---|---|---|--:|--:|--:|"]
    for m in lean_map:
        loc = m["lean_location"]
        decl = m["lean_decl"].split(".", 1)[-1]
        cell = (md_lean(commit, *loc.rsplit(":", 1), "`" + decl + "`") if decl and ":" in loc
                else (f"`{decl}`" if decl else ""))
        out.append(f"| {md_paper(m['page'], m['item'])} | {md(m['status'])} | {cell} | {m['agreement']}/3 | "
                   f"{m['found_round']} | {m['def_depth']} |")
    out += ["", "</details>", ""]

    out += ["## Without a 3-of-3 match", "", "| Paper | Status | Rounds | Best candidate |", "|---|---|--:|---|"]
    for u in unmatched:
        out.append(f"| {md(u['item'])} | {md(u['status'])} | {u['rounds_tried']} | "
                   f"`{u['best_candidate'].split('.', 1)[-1]}` ({u['candidate_agreement']}/3) |")
    out += ["", "## Everything else", "",
            f"- [lean_theorems_without_paper_counterpart.csv](lean_theorems_without_paper_counterpart.csv): "
            f"{len(orphans)} theorems in the {len(pilot_files)} compared files not matched to anything in the paper, "
            "mostly supporting steps.",
            "- [differences.csv](differences.csv): every difference with both quotes, pages, Lean lines and each "
            "sample's wording.",
            "- [audit_table.csv](audit_table.csv), [paper_lean_map.csv](paper_lean_map.csv): the two tables above, "
            "with more columns.",
            "- [source_scan.csv](source_scan.csv), [external_imports.csv](external_imports.csv): the static scan.", ""]
    (OUT / "summary.md").write_text("\n".join(out), encoding="utf-8")


def esc(s):
    return html.escape(str(s if s is not None else ""))


def lean_link(commit, file, lines):
    ln = lines_of(lines)
    if not ln:
        return esc(file)
    anchor = f"#L{ln[0]}" + (f"-L{ln[1]}" if ln[1] != ln[0] else "")
    return f'<a href="{REPO_URL}/{commit}/{esc(file)}{anchor}">{esc(file.removeprefix(C.PREFIX))}:{esc(lines)}</a>'


def paper_link(page, label):
    return f'<a href="{PAPER_URL}#page={esc(page)}">{esc(label)}, p.{esc(page)}</a>' if page else esc(label)


def write_html(table, diffs, unmatched, orphans, gate, commit, downstream_where, items, pilot_files):
    by_pair = defaultdict(list)
    for d in diffs:
        by_pair[(d["item"], d["decl"])].append(d)
    types = Counter(d["type"] for d in diffs)
    rows = []
    for r in table:
        ds = by_pair[(r["item"], r["lean_decl"])]
        file, lines = r["lean_location"].rsplit(":", 1)
        det = []
        for d in ds:
            det.append(
                f'<tr class="d" data-type="{esc(d["type"])}" data-agree="{d["agreement"]}">'
                f'<td><span class="t t-{esc(d["type"])}">{esc(d["type"])}</span></td>'
                f'<td class="ag ag{d["agreement"]}">{d["agreement"]}/3</td>'
                f'<td>{esc(d["summary"])}<details><summary>sides, quotes, all wordings</summary>'
                f'<p><b>Paper:</b> {esc(d["paper_side"])}<br><b>Lean:</b> {esc(d["lean_side"])}</p>'
                f'<p><b>Paper quote</b> ({paper_link(d["page"], d["paper_cite"])}'
                f'{"" if d["paper_quote_verified"] else ", <em>not verified</em>"}): <code>{esc(d["paper_quote"])}</code></p>'
                f'<p><b>Lean quote</b> ({lean_link(commit, d["lean_file"], d["lean_lines"])}'
                f'{"" if d["lean_quote_verified"] else ", <em>not verified</em>"}): <code>{esc(d["lean_quote"])}</code></p>'
                + (f'<p class="warn">Judgment words used: {esc(d["verdict_words"])}</p>' if d["verdict_words"] else "")
                + "<ul>" + "".join(f"<li>{esc(w)}</li>" for w in d["all_wordings"]) + "</ul></details></td></tr>")
        uses = downstream_where.get(r["item"], [])
        rows.append(
            f'<tbody class="pair"><tr class="p">'
            f'<td>{esc(r["item"])}<div class="sub">{paper_link(r["page"], "paper")}</div></td>'
            f'<td><code>{esc(r["lean_decl"].split(".", 1)[-1])}</code>'
            f'<div class="sub">{lean_link(commit, file, lines)} · main proof path: {esc(r["on_main_proof_path"])}</div></td>'
            f'<td>{esc(r["top_difference"])}</td>'
            f'<td class="num">{r["n_agreed_3of3"]} / {r["n_differences"]}</td>'
            f'<td class="num" title="{esc("; ".join(uses))}">{r["downstream_uses"]}</td></tr>'
            f'<tr><td colspan="5"><details><summary>{len(ds)} differences</summary>'
            f'<table class="inner"><thead><tr><th>type</th><th>agree</th><th>difference</th></tr></thead>'
            f'<tbody>{"".join(det)}</tbody></table></details></td></tr></tbody>')
    gate_html = "".join(f"<li>{esc(d['item'])}: <code>{esc(d['decl'].split('.', 1)[-1])}</code>, {d['agreement']}/3 samples, "
                        f"{lean_link(commit, d['lean_file'], d['lean_lines'])}: {esc(d['summary'])}</li>" for d in gate)
    gate_card = (f'<div class="card gate">{C.REPORT.get("validation_intro", "<b>Validation targets</b>")}'
                 f'<ul>{gate_html or "<li>not found</li>"}</ul></div>') if C.VALIDATION else ""
    pilot_label = C.REPORT.get("pilot_label", "pilot")
    un_html = "".join(f"<tr><td>{esc(u['item'])}</td><td>{esc(u['status'])}</td><td>{u['rounds_tried']}</td>"
                      f"<td><code>{esc(u['best_candidate'])}</code> ({u['candidate_agreement']}/3)</td></tr>" for u in unmatched)
    orph_html = "".join(f"<tr><td><code>{esc(o['lean_decl'].split('.', 1)[-1])}</code></td>"
                        f"<td>{lean_link(commit, *o['location'].rsplit(':', 1))}</td><td class='num'>{o['used_by_other_files']}</td>"
                        f"<td>{esc(o['on_main_proof_path'])}</td><td>{esc(o['docstring'])}</td></tr>" for o in orphans)
    type_btns = "".join(f'<label><input type="checkbox" class="tf" value="{t}" checked> {t} ({types[t]})</label>'
                        for t in SEVERITY if types[t])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(C.REPORT.get('short_title', 'Paper vs. Lean audit'))}</title>
<style>
:root {{ --bg:#fbfbf9; --fg:#1d1d1b; --muted:#6b6b66; --line:#e3e2dc; --card:#ffffff; --accent:#2f5d8a;
  --sb:#b42318; --mh:#b54708; --nm:#6941c6; --oth:#667085; --ok:#067647; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#141413; --fg:#ecebe6; --muted:#a3a29b;
  --line:#2e2d2a; --card:#1c1c1a; --accent:#8db4dc; --sb:#f97066; --mh:#fdb022; --nm:#b692f6; --oth:#98a2b3; --ok:#47cd89; }} }}
:root[data-theme="dark"] {{ --bg:#141413; --fg:#ecebe6; --muted:#a3a29b; --line:#2e2d2a; --card:#1c1c1a; --accent:#8db4dc;
  --sb:#f97066; --mh:#fdb022; --nm:#b692f6; --oth:#98a2b3; --ok:#47cd89; }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  margin:0; padding:24px 16px 64px; }}
main {{ max-width:1200px; margin:0 auto; }}
h1 {{ font-size:24px; margin:0 0 4px; }} h2 {{ font-size:18px; margin:36px 0 8px; }}
p.lead {{ color:var(--muted); margin:0 0 16px; max-width:820px; }}
a {{ color:var(--accent); }} code {{ font-size:13px; word-break:break-word; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 16px; margin:12px 0; }}
.gate {{ border-left:4px solid var(--ok); }}
.wrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; }}
th, td {{ text-align:left; vertical-align:top; padding:6px 8px; border-bottom:1px solid var(--line); }}
th {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }}
tr.p td {{ border-bottom:none; padding-top:12px; }}
.sub {{ font-size:12px; color:var(--muted); }}
.num {{ text-align:right; white-space:nowrap; }}
table.inner td {{ font-size:14px; }}
.t {{ font-size:12px; font-weight:600; white-space:nowrap; color:var(--oth); }}
.t-stronger-bound {{ color:var(--sb); }} .t-missing-hypothesis {{ color:var(--mh); }}
.t-different-norm, .t-missing-supremum, .t-different-domain {{ color:var(--nm); }}
.ag {{ white-space:nowrap; font-variant-numeric:tabular-nums; }} .ag3 {{ font-weight:700; }} .ag1 {{ color:var(--muted); }}
details summary {{ cursor:pointer; color:var(--accent); font-size:13px; }}
.warn {{ color:var(--mh); }}
.filters label {{ margin-right:14px; font-size:13px; white-space:nowrap; }}
</style></head><body><main>
<h1>{esc(C.REPORT.get('title', 'Paper vs. Lean audit'))}</h1>
<p class="lead">Where the paper and its Lean formalization state things differently, extracted by a local model
(3 independent samples per pair, kept separate) with every claim quoted and the quotes checked against the sources.
This page lists differences. It does not say whether any difference matters. See METHODOLOGY.md.
Paper: <a href="{PAPER_URL}">{esc(C.PDF.name)}</a> · Lean: {esc(C.REPO_LABEL)} at <code>{esc(commit[:12])}</code></p>
{gate_card}

<h2>Pairs (paper item × Lean declaration), most severe first</h2>
<p class="lead">Severity order: {", ".join(SEVERITY)}. "Agreed" = reported by all 3 samples at the same Lean lines.
Downstream uses = places the paper cites the item (hover for the list).</p>
<div class="filters card">Show differences of type: {type_btns}<br>
<label><input type="checkbox" id="only3"> only differences reported by all 3 samples</label></div>
<div class="wrap"><table>
<thead><tr><th>Paper item</th><th>Lean declaration</th><th>Most severe agreed difference</th><th class="num">agreed / all</th>
<th class="num">uses</th></tr></thead>
{"".join(rows)}</table></div>

<h2>Paper items without a confident Lean counterpart (whole paper)</h2>
<p class="lead">After up to 3 search rounds. "Weak" means only 2 of 3 samples agreed on the candidate.</p>
<div class="wrap"><table><thead><tr><th>Item</th><th>Status</th><th>Rounds</th><th>Best candidate</th></tr></thead>
<tbody>{un_html or "<tr><td colspan=4>none</td></tr>"}</tbody></table></div>

<h2>Lean theorems in the {esc(pilot_label)} files not located for any paper item</h2>
<p class="lead">{len(orphans)} theorems in the {len(pilot_files)} files of the {esc(pilot_label)} pairs, excluding routine helpers
(simp lemmas, private, undocumented smoothness/arithmetic one-liners). Most are supporting steps; sorted by how many
other files use them.</p>
<details><summary>show {len(orphans)} theorems</summary><div class="wrap"><table>
<thead><tr><th>Theorem</th><th>Location</th><th class="num">used by files</th><th>main proof path</th><th>Docstring</th></tr></thead>
<tbody>{orph_html}</tbody></table></div></details>
</main>
<script>
function apply() {{
  const on = new Set([...document.querySelectorAll('.tf:checked')].map(x => x.value));
  const only3 = document.getElementById('only3').checked;
  document.querySelectorAll('tr.d').forEach(r => {{
    r.style.display = on.has(r.dataset.type) && (!only3 || r.dataset.agree === '3') ? '' : 'none';
  }});
}}
document.querySelectorAll('.tf, #only3').forEach(x => x.addEventListener('change', apply));
</script></body></html>"""
    (OUT / "report.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
