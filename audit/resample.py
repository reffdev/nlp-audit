# SPDX-License-Identifier: Apache-2.0
"""Resampling-noise measurement for locating.

Reruns only the locating step (file candidates, then the multi-round search) for the targets in
data/resample_targets.json, with the v0.2 prompts unchanged and three fresh samples (sample indices 3-5, so new
seeds and new cache entries). It runs in a copy of the database (data/audit_resample.db), so the v0.2 results
are untouched, and reports how many targets end on a different top declaration than in v0.2, with the tokens
and time used.

  python audit/resample.py [--compare-only]
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time

import config as C

COPY = C.DATA / "audit_resample.db"
TARGETS = C.DATA / "resample_targets.json"
OFFSET = "3"


def found(db):
    con = sqlite3.connect(db)
    out = {r[0]: (r[1], r[2], {c["decl"]: c["agreement"] for c in json.loads(r[3] or "[]")})
           for r in con.execute("SELECT item, status, found_decl, found_all FROM search_status")}
    con.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare-only", action="store_true")
    a = ap.parse_args()
    sel = json.loads(TARGETS.read_text())
    items = sel["moved"] + sel["unchanged"]
    t0 = time.time()
    if not a.compare_only:
        shutil.copy(C.DB, COPY)
        env = dict(os.environ, AUDIT_DB=str(COPY), AUDIT_LLM_SAMPLE_OFFSET=OFFSET, PYTHONIOENCODING="utf-8")
        here = C.ROOT / "audit"
        for args in (["xref_llm.py", "files", "--items", ",".join(items)],
                     ["xref_search.py", "--items", ",".join(items)]):
            subprocess.run([sys.executable, "-u", str(here / args[0]), *args[1:]], env=env, check=True)
    t1 = time.time()
    v2, rs = found(C.DB), found(COPY)
    rows, diff = [], 0
    for grp in ("moved", "unchanged"):
        for it in sel[grp]:
            a_, b_ = v2[it], rs[it]
            changed = a_[1] != b_[1]
            diff += changed
            rows.append(dict(group=grp, item=it, v02=a_[1], resample=b_[1], v02_status=a_[0], resample_status=b_[0],
                             top_changed=changed, v02_top_in_resample_agreed=a_[1] in b_[2],
                             agreed_overlap=bool(set(a_[2]) & set(b_[2]))))
    # tokens and time: responses logged since the run started, at the offset sample indices
    tin = tout = n = 0
    if not a.compare_only:
        for line in open(C.DATA / "llm_raw.jsonl", encoding="utf-8"):
            r = json.loads(line)
            if r.get("t", 0) >= t0 and r.get("sample", 0) >= int(OFFSET):
                u = r.get("usage") or {}
                tin += u.get("prompt_tokens", 0)
                tout += u.get("completion_tokens", 0)
                n += 1
    res = dict(targets=len(items), top_changed=diff,
               moved_group_changed=sum(r["top_changed"] for r in rows if r["group"] == "moved"),
               unchanged_group_changed=sum(r["top_changed"] for r in rows if r["group"] == "unchanged"),
               calls=n, input_tokens=tin, output_tokens=tout, minutes=round((t1 - t0) / 60, 1), rows=rows)
    (C.DATA / "resample_result.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
