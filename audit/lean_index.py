"""Phase 1: index of Lean declarations under NavierStokes/.

Source reading only (no elaboration). For every declaration records name (fully qualified
by namespace), kind, file, line range, docstring, statement text (keyword through the
top-level `:=` / `where` / first match arm), the `variable`s in scope (implicit hypotheses),
prefix commands (`omit ... in`, `open ... in`), and the NavierStokes declarations its text
references. Also records each file's module docstring (`/-! ... -/`).

Output: SQLite tables lean_files, lean_decls, lean_refs in data/audit.db, plus JSONL mirrors.
"""
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "repo"
SRC = REPO / "NavierStokes"
DB = ROOT / "data" / "audit.db"

KW = r"theorem|lemma|def|abbrev|structure|class|instance|inductive|example|opaque|axiom|irreducible_def"
MODS = r"(?:(?:private|protected|noncomputable|nonrec|partial|unsafe|scoped)\s+)*"
DECL = re.compile(rf"^(@\[[^\]]*\]\s*)?{MODS}({KW})\b\s*([^\s:(\[{{⦃]*)")
IDENT = re.compile(r"[A-Za-z_À-ɏͰ-Ͽᴀ-ᶿ℀-⅏][\w'!?À-ɏͰ-Ͽᴀ-ᶿ₀-ₜ℀-⅏.]*")
OPEN_BR, CLOSE_BR = "([{⟨⦃", ")]}⟩⦄"
CONTINUATION_COL0 = ("termination_by", "decreasing_by", "where", "|", "deriving", ")", "]", "}")


def strip_comments(text):
    """Blank out comments (keeping line structure) so bracket/:= scanning is not fooled."""
    out, i, n, depth = [], 0, len(text), 0
    while i < n:
        if text.startswith("/-", i):
            depth += 1
            out.append("  ")
            i += 2
        elif depth and text.startswith("-/", i):
            depth -= 1
            out.append("  ")
            i += 2
        elif depth:
            out.append("\n" if text[i] == "\n" else " ")
            i += 1
        elif text.startswith("--", i):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def statement_end(code, start):
    """Index just past the statement: first depth-0 `:=`, ` where`, or newline-`|` after start."""
    depth, i, n = 0, start, len(code)
    while i < n:
        c = code[i]
        if c in OPEN_BR:
            depth += 1
        elif c in CLOSE_BR:
            depth = max(0, depth - 1)
        elif depth == 0:
            if code.startswith(":=", i):
                return i + 2
            if code.startswith("where", i) and code[i - 1].isspace() and (i + 5 >= n or not code[i + 5].isalnum()):
                return i + 5
            if c == "|" and code[:i].rstrip(" ").endswith("\n"):
                return i
        i += 1
    return n


def parse_file(path):
    rel = path.relative_to(REPO).as_posix()
    raw = path.read_text(encoding="utf-8")
    raw_lines = raw.splitlines()
    code = strip_comments(raw)
    lines = code.splitlines()
    line_off = [0]
    for ln in raw.splitlines(keepends=True):
        line_off.append(line_off[-1] + len(ln))

    mod_docs = [m.group(1).strip() for m in re.finditer(r"/-!(.*?)-/", raw, re.S)]
    imports = [m.group(1) for m in re.finditer(r"^import\s+(\S+)", raw, re.M)]

    # scope stack: (kind, name, [variable texts])
    scopes = [("file", "", [])]
    opens = []
    decls = []
    i, n = 0, len(lines)
    pending_prefix = []
    while i < n:
        ln = lines[i]
        if not ln.strip() or ln[0].isspace():
            i += 1
            continue
        s = ln.strip()
        m_ns = re.match(r"^(namespace|section|noncomputable section)\b\s*(\S*)", s)
        if m_ns:
            kind = "namespace" if m_ns.group(1) == "namespace" else "section"
            scopes.append((kind, m_ns.group(2) if kind == "namespace" else "", []))
            i += 1
            continue
        if re.match(r"^end\b", s):
            if len(scopes) > 1:
                scopes.pop()
            i += 1
            continue
        # gather the full command (col-0 line + indented continuation lines)
        j = i + 1
        while j < n and (not lines[j].strip() or lines[j][0].isspace()
                         or lines[j].startswith(CONTINUATION_COL0)):
            j += 1
        # trim trailing blank lines
        k = j
        while k > i + 1 and not lines[k - 1].strip():
            k -= 1
        if s.startswith("variable"):
            scopes[-1][2].append("\n".join(raw_lines[i:k]).strip())
            i = j
            continue
        if s.startswith("open ") and not re.search(r"\bin\s*$", s):
            opens.append(s)
            i = j
            continue
        if re.match(r"^(omit|include|open|set_option)\b.*\bin\s*$", s):
            pending_prefix.append(s)
            i = j
            continue
        m = DECL.match(s)
        if m:
            kind, name = m.group(2), m.group(3)
            ns = ".".join(sc[1] for sc in scopes if sc[0] == "namespace" and sc[1])
            if kind in ("instance", "example") and (not name or name.startswith(("(", "[", "{", ":"))):
                name = ""
            full = name[1:] if name.startswith("_root_.") else (f"{ns}.{name}" if ns and name else name)
            start_off = line_off[i]
            end_off = line_off[k]
            st_end = statement_end(code, start_off + m.end())
            st_end = min(st_end, end_off)
            statement = raw[start_off:st_end].strip()
            body = code[st_end:end_off]
            # docstring immediately above (allowing attributes/prefix lines between)
            doc, doc_line = None, None
            b = i - 1
            while b >= 0 and (raw_lines[b].startswith(("@[", "omit", "include", "open", "set_option"))
                              and raw_lines[b].rstrip().endswith((" in", "]")) or not raw_lines[b].strip()):
                if not raw_lines[b].strip():
                    break
                b -= 1
            if b >= 0 and raw_lines[b].rstrip().endswith("-/"):
                e = b
                while e >= 0 and "/--" not in raw_lines[e]:
                    if "/-!" in raw_lines[e] or (raw_lines[e].lstrip().startswith("/-") and e != b):
                        e = -1
                        break
                    e -= 1
                if e >= 0:
                    doc = "\n".join(raw_lines[e:b + 1]).strip()
                    doc = re.sub(r"^/--\s?|\s?-/$", "", doc).strip()
                    doc_line = e + 1
            # `@[...]` on its own line(s) above
            attrs = []
            b2 = i - 1
            while b2 >= 0 and raw_lines[b2].startswith("@["):
                attrs.insert(0, raw_lines[b2].strip())
                b2 -= 1
            if m.group(1):
                attrs.append(m.group(1).strip())
            decls.append(dict(
                name=full or f"<anon {kind} {rel}:{i+1}>", short_name=name, kind=kind, file=rel,
                line_start=(doc_line or i + 1), decl_line=i + 1, line_end=k,
                docstring=doc, attributes=" ".join(attrs) or None,
                prefix=" ; ".join(pending_prefix) or None,
                namespace=ns or None,
                variables="\n".join(v for sc in scopes for v in sc[2]) or None,
                opens=" ; ".join(opens) or None,
                statement=statement, _body=body, _statement_code=code[start_off:st_end],
            ))
            pending_prefix = []
            i = j
            continue
        pending_prefix = []
        i = j
    return dict(file=rel, n_lines=len(raw_lines), module_doc="\n\n".join(mod_docs) or None,
                imports=" ".join(imports)), decls


def resolve_refs(all_decls):
    by_full = {d["name"]: d for d in all_decls}
    by_suffix = {}
    for full in by_full:
        parts = full.split(".")
        for s in range(len(parts)):
            by_suffix.setdefault(".".join(parts[s:]), set()).add(full)
    refs = []
    for d in all_decls:
        ns_parts = (d["namespace"] or "").split(".") if d["namespace"] else []
        opened = re.findall(r"\b([A-Z][\w.]*)", d["opens"] or "") + re.findall(r"\b([A-Z][\w.]*)", d["prefix"] or "")
        seen = set()
        for where, text in (("statement", d["_statement_code"]), ("body", d["_body"])):
            for tok in set(IDENT.findall(text)):
                tok = tok.rstrip(".")
                cands = by_suffix.get(tok)
                if not cands:
                    continue
                target = None
                for p in range(len(ns_parts), -1, -1):  # innermost namespace first
                    c = ".".join(ns_parts[:p] + [tok])
                    if c in by_full:
                        target = c
                        break
                if target is None:
                    for o in opened:
                        for p in range(len(ns_parts), -1, -1):
                            c = ".".join(ns_parts[:p] + [o, tok])
                            if c in by_full:
                                target = c
                                break
                        if target:
                            break
                if target is None and len(cands) == 1 and "." in tok:
                    target = next(iter(cands))
                if target is None and len(cands) == 1 and tok in by_full:
                    target = tok
                if target is None or target == d["name"] or (target, where) in seen:
                    continue
                seen.add((target, where))
                refs.append(dict(source=d["name"], target=target, location=where))
    return refs


def main():
    files, decls = [], []
    for path in sorted(SRC.rglob("*.lean")):
        f, ds = parse_file(path)
        files.append(f)
        decls.extend(ds)
    refs = resolve_refs(decls)
    out_decls = [{k: v for k, v in d.items() if not k.startswith("_")} for d in decls]
    con = sqlite3.connect(DB)
    for name, rows in [("lean_files", files), ("lean_decls", out_decls), ("lean_refs", refs)]:
        con.execute(f"DROP TABLE IF EXISTS {name}")
        cols = list(rows[0].keys())
        con.execute(f"CREATE TABLE {name} ({', '.join(cols)})")
        con.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})",
                        [tuple(r[c] for c in cols) for r in rows])
        with open(ROOT / "data" / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    con.execute("CREATE INDEX IF NOT EXISTS lean_refs_src ON lean_refs(source)")
    con.execute("CREATE INDEX IF NOT EXISTS lean_refs_tgt ON lean_refs(target)")
    con.commit()
    print(f"files={len(files)} decls={len(decls)} refs={len(refs)}")


if __name__ == "__main__":
    main()
