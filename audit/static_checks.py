# SPDX-License-Identifier: Apache-2.0
"""Static, source-level checks on the Lean repository (no elaboration, no build).

1. Escape-hatch scan: counts of `axiom`, `sorry`, `admit`, `native_decide`, `unsafe` (plus `opaque`,
   `implemented_by`, `extern`, `debug.skipKernelTC`) in every .lean file of the repository, outside comments
   and string literals; and every imported module whose root is neither Mathlib nor this repository.
2. Near-duplicate theorem statements under the audited subdirectory: statements are normalized (theorem name
   dropped, comments and universe levels removed, bound variables renamed in order of appearance, repository
   names resolved to their full names; statements re-read from source, see full_statement) and clustered by
   exact hash, then by a fuzzy match on the normalized text that accepts only formatting differences
   (whitespace, parentheses). For each member: how many other declarations reference it, and whether it is on
   the main proof path.
3. Definitional depth: for each theorem, the longest chain of repository `def`/`abbrev`/`structure`/
   `inductive`/`class` declarations between its statement and names from outside the repository (for a
   definition, the chain starting at itself).

Reads lean_decls, lean_refs, lean_reach. Writes tables static_scan, static_imports, static_dupes,
lean_def_depth, and out/source_scan.csv, out/external_imports.csv, out/duplicate_statements.csv.
"""
import csv
import hashlib
import re
import sqlite3
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

import config as C
from lean_index import IDENT, strip_comments

TOKENS = ["axiom", "sorry", "admit", "native_decide", "unsafe", "opaque", "implemented_by", "extern",
          "debug.skipKernelTC"]
PRIMARY = TOKENS[:5]
DEF_KINDS = {"def", "abbrev", "structure", "inductive", "class"}
FUZZY_MIN_LEN, FUZZY_COS, FUZZY_RATIO = 40, 0.9, 0.97
LET = re.compile(r"(?:let|have|set)\s")
BINDER_GROUP = re.compile(r"[(\{⦃]\s*([^:()\[\]{}⦃⦄]+?)\s*:")
BINDER_QUANT = re.compile(r"(?:∀|∃!?|∑|∏|⨆|⨅|⋃|⋂|∫|fun|λ)\s+((?:[^\W\d][\w'₀-₉]*\s*)+)")


def strip_strings(code):
    return re.sub(r'"(?:\\.|[^"\\])*"', '""', code)


_files = {}


def full_statement(d):
    """Theorem statement up to the `:=` that starts its proof, re-read from source. lean_index's statement_end
    cuts two kinds of statement short: it stops at a line starting with `|` (meant for match arms; here it is
    an absolute value), and at the `:=` of a `let` inside the statement."""
    if d["file"] not in _files:
        raw = (C.REPO / d["file"]).read_text(encoding="utf-8")
        _files[d["file"]] = (strip_comments(raw), [0] + [m.end() for m in re.finditer("\n", raw)])
    code, off = _files[d["file"]]
    a, b = off[d["decl_line"] - 1], off[min(d["line_end"], len(off) - 1)]
    depth, lets = 0, 0
    for i in range(a, b):
        c = code[i]
        if c in "([{⟨⦃":
            depth += 1
        elif c in ")]}⟩⦄":
            depth = max(0, depth - 1)
        elif depth == 0 and LET.match(code, i) and not (code[i - 1].isalnum() or code[i - 1] in "_.'"):
            lets += 1  # `let x := v` inside the statement: its `:=` does not end the statement
        elif depth == 0 and code.startswith(":=", i):
            if lets:
                lets -= 1
                continue
            return code[a:i + 2]
    return code[a:b]


# ---------------------------------------------------------------- 1. escape hatches
def scan(con):
    own_roots = {p.name for p in C.REPO.iterdir() if p.is_dir() and not p.name.startswith(".")}
    own_roots |= {p.stem for p in C.REPO.glob("*.lean")}
    rows, imports = [], defaultdict(set)
    for path in sorted(C.REPO.rglob("*.lean")):
        rel = path.relative_to(C.REPO).as_posix()
        if rel.startswith(".lake/"):
            continue
        raw = path.read_text(encoding="utf-8")
        code = strip_strings(strip_comments(raw))
        counts = {t: len(re.findall(rf"(?<![\w.]){re.escape(t)}(?![\w'])", code)) for t in TOKENS}
        rows.append(dict(file=rel, in_audit_scope=int(rel.startswith(C.PREFIX)), **counts))
        for m in re.finditer(r"^import\s+(\S+)", raw, re.M):
            root = m.group(1).split(".")[0]
            if root != "Mathlib" and root not in own_roots:
                imports[m.group(1)].add(rel)
    con.execute("DROP TABLE IF EXISTS static_scan")
    con.execute(f"CREATE TABLE static_scan (file, in_audit_scope, {', '.join(t.replace('.', '_') for t in TOKENS)})")
    con.executemany(f"INSERT INTO static_scan VALUES ({','.join('?' * (len(TOKENS) + 2))})",
                    [(r["file"], r["in_audit_scope"], *[r[t] for t in TOKENS]) for r in rows])
    con.execute("DROP TABLE IF EXISTS static_imports")
    con.execute("CREATE TABLE static_imports (module, n_files, files)")
    con.executemany("INSERT INTO static_imports VALUES (?,?,?)",
                    [(m, len(fs), " ".join(sorted(fs))) for m, fs in sorted(imports.items())])
    cols = ["file", "in_audit_scope", *TOKENS]
    tot_all = {t: sum(r[t] for r in rows) for t in TOKENS}
    tot_scope = {t: sum(r[t] for r in rows if r["in_audit_scope"]) for t in TOKENS}
    with open(C.OUT / "source_scan.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerow(dict(file=f"TOTAL ({C.PREFIX})", in_audit_scope=1, **tot_scope))
        w.writerow(dict(file="TOTAL (whole repository)", in_audit_scope="", **tot_all))
        w.writerows(rows)
    with open(C.OUT / "external_imports.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["module", "n_files", "files"])
        for m, fs in sorted(imports.items()):
            w.writerow([m, len(fs), " ".join(sorted(fs))])
    n_scope = sum(r["in_audit_scope"] for r in rows)
    print(f"scan: {len(rows)} files ({n_scope} in {C.PREFIX}); totals in scope "
          + ", ".join(f"{t}={tot_scope[t]}" for t in TOKENS) + "; whole repo "
          + ", ".join(f"{t}={tot_all[t]}" for t in TOKENS if tot_all[t]) + f"; external imports: {sorted(imports)}")
    return tot_scope, tot_all, imports


# ---------------------------------------------------------------- shared: name resolution
class Resolver:
    """The resolution rules of lean_index.resolve_refs, returning token -> full name."""

    def __init__(self, decls):
        self.full = {d["name"] for d in decls}
        self.suffix = defaultdict(set)
        for f in self.full:
            parts = f.split(".")
            for s in range(len(parts)):
                self.suffix[".".join(parts[s:])].add(f)

    def __call__(self, tok, d):
        cands = self.suffix.get(tok)
        if not cands:
            return None
        ns = (d["namespace"] or "").split(".") if d["namespace"] else []
        for p in range(len(ns), -1, -1):
            c = ".".join(ns[:p] + [tok])
            if c in self.full:
                return c
        for o in re.findall(r"\b([A-Z][\w.]*)", (d["opens"] or "") + " " + (d["prefix"] or "")):
            for p in range(len(ns), -1, -1):
                c = ".".join(ns[:p] + [o, tok])
                if c in self.full:
                    return c
        if len(cands) == 1 and ("." in tok or tok in self.full):
            return next(iter(cands))
        return None


# ---------------------------------------------------------------- 2. near-duplicate statements
def normalize(d, resolve):
    s = d["full_statement"]
    s = re.sub(rf"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|nonrec)\s+)*(?:theorem|lemma)\s+\S+", "", s)
    s = re.sub(r":=\s*$", "", s.strip())
    s = re.sub(r"\.\{[^}]*\}", "", s)
    s = re.sub(r"\b(Sort|Type)\s+(?:\*|_|\w+|\([^)]*\))", r"\1 _", s)
    s = re.sub(r"\bType\*", "Type _", s)
    binders = []
    for m in BINDER_GROUP.finditer(s):
        binders += [t for t in m.group(1).split() if IDENT.fullmatch(t)]
    for m in BINDER_QUANT.finditer(s):
        binders += m.group(1).split()
    binders = set(binders) - {"_"}
    rename = {}

    def sub(m):
        tok = m.group(0)
        head, dot, rest = tok.partition(".")
        if head in binders:
            rename.setdefault(head, f"v{len(rename) + 1}")
            return rename[head] + dot + rest
        parts = tok.rstrip(".").split(".")
        for k in range(len(parts), 0, -1):  # `radialVector.1`, `x.foo`: resolve the longest known prefix
            target = resolve(".".join(parts[:k]), d)
            if target:
                return ".".join([target] + parts[k:])
        return tok

    s = IDENT.sub(sub, s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"\s*([(){}\[\]⦃⦄,:])\s*", r"\1", s)


def dupes(con, decls, resolve):
    thms = [d for d in decls if d["kind"] == "theorem" and d["file"].startswith(C.PREFIX)
            and not d["name"].startswith("<anon")]
    norm = [normalize(d, resolve) for d in thms]
    idents = [Counter(IDENT.findall(x)) for x in norm]
    parent = list(range(len(thms)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    by_hash = defaultdict(list)
    for i, s in enumerate(norm):
        by_hash[hashlib.sha1(s.encode()).hexdigest()].append(i)
    for idx in by_hash.values():
        for j in idx[1:]:
            parent[find(j)] = find(idx[0])
    # fuzzy: one representative per exact group, char 3-gram cosine, then a sequence ratio check
    reps = [idx[0] for idx in by_hash.values() if len(norm[idx[0]]) >= FUZZY_MIN_LEN]
    vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 3), sublinear_tf=True)
    X = vec.fit_transform([norm[i] for i in reps])
    fuzzy_pairs = variants = 0
    for a in range(0, len(reps), 2000):
        S = (X[a:a + 2000] @ X.T).tocoo()
        for r, c, v in zip(S.row, S.col, S.data):
            i, j = reps[a + r], reps[c]
            if v < FUZZY_COS or i >= j:
                continue
            if idents[i] != idents[j]:
                continue
            if SequenceMatcher(None, norm[i], norm[j], autojunk=False).ratio() < FUZZY_RATIO:
                continue
            # Accept only formatting differences. A different operator, numeral or order (add/sub/mul siblings,
            # n + 4 vs n + 5) is a different statement, and such pairs dominate the fuzzy candidates.
            if re.sub(r"[\s()]", "", norm[i]) == re.sub(r"[\s()]", "", norm[j]):
                parent[find(j)] = find(i)
                fuzzy_pairs += 1
            else:
                variants += 1
    clusters = defaultdict(list)
    for i in range(len(thms)):
        clusters[find(i)].append(i)
    clusters = sorted((c for c in clusters.values() if len(c) > 1), key=lambda c: (-len(c), thms[c[0]]["name"]))

    inbound = Counter()
    for s, t in con.execute("SELECT DISTINCT source, target FROM lean_refs"):
        if s != t:
            inbound[t] += 1
    reach = dict(con.execute("SELECT name, reachable FROM lean_reach"))
    rows = []
    for k, c in enumerate(clusters, start=1):
        exact = len({hashlib.sha1(norm[i].encode()).hexdigest() for i in c}) == 1
        members = sorted(c, key=lambda i: (thms[i]["file"], thms[i]["decl_line"]))
        for i in members:
            d = thms[i]
            ref = norm[members[0]]
            diff = "" if norm[i] == ref else "; ".join(
                f"{ref[a1:a2]!r}->{norm[i][b1:b2]!r}" for op, a1, a2, b1, b2 in
                SequenceMatcher(None, ref, norm[i], autojunk=False).get_opcodes() if op != "equal")
            rows.append(dict(cluster=k, cluster_size=len(c), match="exact" if exact else "near",
                             decl=d["name"], file=d["file"], line=d["decl_line"],
                             referenced_by=inbound[d["name"]], on_main_proof_path=int(bool(reach.get(d["name"]))),
                             simp=int("simp" in (d["attributes"] or "")), differs_from_first=diff,
                             normalized_statement=norm[i]))
    cols = list(rows[0]) if rows else []
    con.execute("DROP TABLE IF EXISTS static_dupes")
    con.execute(f"CREATE TABLE static_dupes ({', '.join(cols)})")
    con.executemany(f"INSERT INTO static_dupes VALUES ({','.join('?' * len(cols))})", [tuple(r.values()) for r in rows])
    with open(C.OUT / "duplicate_statements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    members = len(rows)
    orphans = sum(1 for r in rows if r["referenced_by"] == 0)
    all_orphan = sum(1 for k in {r["cluster"] for r in rows}
                     if all(r["referenced_by"] == 0 for r in rows if r["cluster"] == k))
    print(f"dupes: {len(thms)} theorems; {len(clusters)} clusters "
          f"({len({r['cluster'] for r in rows if r['match'] == 'exact'})} exact), "
          f"{members} members, {orphans} unreferenced members, {all_orphan} clusters with no member referenced; "
          f"fuzzy pairs accepted {fuzzy_pairs}, rejected as variants {variants}")
    return clusters, rows


# ---------------------------------------------------------------- 3. definitional depth
def def_depth(con, decls, resolve):
    kind = {d["name"]: d["kind"] for d in decls}
    stmt_refs, all_refs = defaultdict(set), defaultdict(set)
    for s, t in con.execute("SELECT source, target FROM lean_refs"):
        if kind.get(t) in DEF_KINDS:
            all_refs[s].add(t)
    for d in decls:
        if d["kind"] == "theorem":
            for tok in set(IDENT.findall(d["full_statement"])):
                t = resolve(tok.rstrip("."), d)
                if kind.get(t) in DEF_KINDS:
                    stmt_refs[d["name"]].add(t)
    memo, onstack = {}, set()

    def depth(n):  # (depth, chain) for a definition, counting itself as one layer
        if n in memo:
            return memo[n]
        if n in onstack:
            return 0, []
        onstack.add(n)
        best = (0, [])
        for c in sorted(all_refs[n]):
            best = max(best, depth(c), key=lambda x: x[0])
        onstack.discard(n)
        memo[n] = (best[0] + 1, [n] + best[1])
        return memo[n]

    rows = []
    for d in decls:
        if d["kind"] in DEF_KINDS:  # a definition matched to a paper result counts itself as one layer
            dd, chain = depth(d["name"])
            reached, stack = set(), [d["name"]]
            while stack:
                x = stack.pop()
                if x not in reached:
                    reached.add(x)
                    stack.extend(all_refs[x])
            rows.append((d["name"], dd, " > ".join(chain), len(reached)))
            continue
        if d["kind"] != "theorem":
            continue
        best, reached = (0, []), set()
        for c in sorted(stmt_refs[d["name"]]):
            best = max(best, depth(c), key=lambda x: x[0])
        stack = list(stmt_refs[d["name"]])
        while stack:
            x = stack.pop()
            if x not in reached:
                reached.add(x)
                stack.extend(all_refs[x])
        rows.append((d["name"], best[0], " > ".join(best[1]), len(reached)))
    con.execute("DROP TABLE IF EXISTS lean_def_depth")
    con.execute("CREATE TABLE lean_def_depth (name, def_depth, def_chain, n_defs_reached)")
    con.executemany("INSERT INTO lean_def_depth VALUES (?,?,?,?)", rows)
    print(f"def depth: {len(rows)} theorems and definitions; max {max(r[1] for r in rows)}")


def unindexed(con):
    """Theorems the Lean index misses: lean_index only reads declarations starting at column 0."""
    rows = []
    for path in sorted(C.SRC.rglob("*.lean")):
        code = strip_comments(path.read_text(encoding="utf-8"))
        for k, line in enumerate(code.splitlines(), start=1):
            m = re.match(r"^[ 	]+(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s+(\S+)", line)
            if m:
                rows.append((path.relative_to(C.REPO).as_posix(), k, m.group(1)))
    con.execute("DROP TABLE IF EXISTS static_unindexed")
    con.execute("CREATE TABLE static_unindexed (file, line, name)")
    con.executemany("INSERT INTO static_unindexed VALUES (?,?,?)", rows)
    print(f"indented theorems the index misses: {len(rows)} in {len({r[0] for r in rows})} file(s)")


def main():
    con = sqlite3.connect(C.DB)
    con.row_factory = sqlite3.Row
    decls = [dict(r) for r in con.execute("SELECT * FROM lean_decls")]
    con.row_factory = None
    cut, cut_rows = Counter(), []
    for d in decls:
        if d["kind"] == "theorem":
            d["full_statement"] = full_statement(d)
            if len(re.sub(r"\s", "", d["full_statement"])) > len(re.sub(r"\s", "", strip_comments(d["statement"]))):
                why = "let" if d["statement"].rstrip().endswith(":=") else "bar"
                cut[why] += 1
                cut_rows.append((d["name"], why))
    print(f"theorem statements cut short by lean_index: {sum(cut.values())} ({dict(cut)})")
    con.execute("DROP TABLE IF EXISTS static_statement_cut")
    con.execute("CREATE TABLE static_statement_cut (name, reason)")
    con.executemany("INSERT INTO static_statement_cut VALUES (?,?)", cut_rows)
    resolve = Resolver(decls)
    scan(con)
    unindexed(con)
    dupes(con, decls, resolve)
    def_depth(con, decls, resolve)
    con.commit()


if __name__ == "__main__":
    main()
