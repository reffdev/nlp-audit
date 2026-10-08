# SPDX-License-Identifier: Apache-2.0
"""Progress of a running LLM stage, read from data/llm_raw.jsonl (each response is logged as it lands).

  python audit/progress.py            # file stage (catalog pass)
  python audit/progress.py decls      # declaration stage
"""
import json
import sys
import time
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "llm_raw.jsonl"
SAMPLES = 3


def main(stage="files"):
    prefix = {"files": "files-catalog:", "decls": "decls:"}[stage]
    rows = [json.loads(line) for line in RAW.read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r["tag"].startswith(prefix) and r.get("thinking", True)]
    ok = [r for r in rows if r.get("ok")]
    units = {r["tag"].removeprefix(prefix).removesuffix(":retry-long") for r in ok}
    recent = [r for r in rows if r["t"] > time.time() - 3 * 3600]
    print(f"{stage}: {len(ok)} responses ok, {sum(not r.get('ok') for r in recent)} failed in the last 3h; "
          f"{len(units)} {'items' if stage == 'files' else 'chunks'} with at least one sample")
    if stage == "files":
        print(f"  target: 80 items x {SAMPLES} samples = {80 * SAMPLES} responses ({100 * len(ok) / (80 * SAMPLES):.0f}%)")
    if recent:
        last = max(r["t"] + r.get("seconds", 0) for r in recent)
        secs = sorted(r.get("seconds", 0) for r in recent if r.get("seconds"))
        print(f"  last response {int(time.time() - last)}s ago; median call {secs[len(secs) // 2]:.0f}s")


if __name__ == "__main__":
    main(*sys.argv[1:])
