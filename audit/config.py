# SPDX-License-Identifier: Apache-2.0
"""Target configuration, read from audit.toml (or the file named by AUDIT_CONFIG).

Every script in audit/ gets its paper- and repository-specific values from here: where the paper and
the Lean sources live, how the paper's running heads and result numbers look, which Lean theorems are
the roots of the main proof path, and what the report should call things. The scripts themselves are
target-independent.

Layout (relative to the repository root):
  data/       inputs and working files: the PDF, its text layer, page images, OCR output, audit.db
  repo/       the Lean repository at the pinned commit (created by audit/fetch.py)
  out/        published tables and the report
"""
import os
import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(os.environ.get("AUDIT_CONFIG") or ROOT / "audit.toml")
with open(CONFIG_PATH, "rb") as _f:
    CFG = tomllib.load(_f)

DATA = ROOT / "data"
OUT = ROOT / "out"
REPO = ROOT / "repo"
DB = DATA / "audit.db"

PAPER = CFG["paper"]
LEAN = CFG["lean"]
PLAN_CFG = CFG.get("plan", {})
REPORT = CFG.get("report", {})
VALIDATION = CFG.get("validation", [])

# --- paper ---
PDF = ROOT / PAPER["file"]
STEM = PDF.stem
LAYOUT_TXT = DATA / "paper_layout.txt"
PAGES = DATA / "pages"
OCR_JSON = DATA / "ocr" / STEM / f"{STEM}.json"
KINDS = "|".join(PAPER["kinds"])
NUM = PAPER["number"]
RUNNING_HEADS = [re.compile(p) for p in PAPER.get("running_heads", [])]
PRINTED_PAGE = [re.compile(p) for p in PAPER.get("printed_page", [r"^\s+(\d+)\s*$"])]

# --- Lean ---
SRC = REPO / LEAN["subdir"]
PREFIX = LEAN["subdir"].strip("/") + "/"
MAIN_SUFFIXES = tuple(LEAN["main_theorems"])
REPO_BLOB_URL = LEAN["repo_url"].rstrip("/") + "/blob"
REPO_LABEL = LEAN["repo_url"].rstrip("/").removeprefix("https://github.com/")

# --- plan / report ---
PLAN = ROOT / PLAN_CFG.get("file", "data/phase2_sample.json")
PILOT_SECTION = str(PLAN_CFG.get("pilot_section", ""))


def rel(path):
    """A Lean file path as shown to the model and in the report: relative to the indexed subdirectory."""
    return path.removeprefix(PREFIX)


def running_head(line):
    return any(p.match(line) for p in RUNNING_HEADS)


def printed_page(line):
    """The printed page number if `line` is a running head or bare page number, else None."""
    for p in PRINTED_PAGE:
        m = p.match(line)
        if m:
            return int(m.group(1))
    return None


def repo_commit():
    """The commit of the local Lean checkout, or the pinned commit if there is no checkout."""
    if (REPO / ".git").exists():
        r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return LEAN["commit"]


def validation_patterns():
    """[(entry, compiled patterns, allowed types or None)] for the configured validation targets."""
    out = []
    for v in VALIDATION:
        out.append((v, [re.compile(p, re.I) for p in v["patterns"]], set(v.get("types") or []) or None))
    return out
