# SPDX-License-Identifier: Apache-2.0
"""Fetch the inputs named in audit.toml and derive the files the other stages read.

  python audit/fetch.py          # paper PDF (SHA-256 checked), Lean repository at the pinned commit,
                                 # text layer (pdftotext -layout), page images (data/pages/pNNN.png)
  python audit/fetch.py --ocr    # also run Marker on the PDF (needs `marker_single` on PATH, i.e. the
                                 # OCR environment from requirements-ocr.txt); output data/ocr/<stem>/

Nothing fetched here is redistributed by this repository; data/ and repo/ are ignored by git.
Each step is skipped when its output already exists, so the script is safe to rerun.
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
import urllib.request

import config as C


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_paper(allow_mismatch):
    C.DATA.mkdir(exist_ok=True)
    if not C.PDF.exists():
        print(f"downloading {C.PAPER['url']} -> {C.PDF}")
        tmp = C.PDF.with_suffix(".part")
        urllib.request.urlretrieve(C.PAPER["url"], tmp)
        tmp.replace(C.PDF)
    digest = sha256(C.PDF)
    expected = C.PAPER.get("sha256")
    if expected and digest != expected:
        msg = f"SHA-256 mismatch for {C.PDF}: expected {expected}, got {digest}"
        if not allow_mismatch:
            sys.exit(msg + "\nThe published PDF may have changed. Pass --allow-hash-mismatch to proceed, "
                           "and record the new hash in audit.toml.")
        print("WARNING: " + msg)
    print(f"paper: {C.PDF} sha256={digest}")


def fetch_lean():
    url, commit = C.LEAN["repo_url"], C.LEAN["commit"]
    git = ["git", "-C", str(C.REPO)]
    if (C.REPO / ".git").exists():
        head = subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        if head == commit:
            print(f"lean: {C.REPO} already at {commit[:12]}")
            return
        print(f"lean: {C.REPO} is at {head[:12]}, checking out {commit[:12]}")
    else:
        C.REPO.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", str(C.REPO)], check=True)
        subprocess.run(git + ["remote", "add", "origin", url], check=True)
    # Fetch just the pinned commit (GitHub serves reachable commits by hash), not the whole history.
    subprocess.run(git + ["fetch", "-q", "--depth", "1", "origin", commit], check=True)
    subprocess.run(git + ["checkout", "-q", "--detach", "FETCH_HEAD"], check=True)
    print(f"lean: {C.REPO} at {commit[:12]} ({url})")
    if not C.SRC.is_dir():
        sys.exit(f"{C.SRC} does not exist: check [lean].subdir in {C.CONFIG_PATH}")


def text_layer():
    if C.LAYOUT_TXT.exists():
        print(f"text layer: {C.LAYOUT_TXT} exists")
        return
    if not shutil.which("pdftotext"):
        sys.exit("pdftotext not found on PATH (install poppler or xpdf)")
    subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(C.PDF), str(C.LAYOUT_TXT)], check=True)
    print(f"text layer: {C.LAYOUT_TXT}")


def page_images(scale):
    import pypdfium2 as pdfium
    C.PAGES.mkdir(exist_ok=True)
    pdf = pdfium.PdfDocument(str(C.PDF))
    n, made = len(pdf), 0
    for i in range(n):
        out = C.PAGES / f"p{i + 1:03d}.png"
        if out.exists():
            continue
        pdf[i].render(scale=scale).to_pil().save(out)
        made += 1
    print(f"page images: {n} pages in {C.PAGES} ({made} rendered)")


def ocr():
    if C.OCR_JSON.exists():
        print(f"ocr: {C.OCR_JSON} exists")
        return
    if not shutil.which("marker_single"):
        sys.exit("marker_single not found on PATH. Activate the OCR environment (requirements-ocr.txt), or run:\n"
                 f"  marker_single {C.PDF} --output_format json --output_dir {C.DATA / 'ocr'}")
    subprocess.run(["marker_single", str(C.PDF), "--output_format", "json",
                    "--output_dir", str(C.DATA / "ocr")], check=True)
    if not C.OCR_JSON.exists():
        sys.exit(f"Marker finished but {C.OCR_JSON} was not produced")
    print(f"ocr: {C.OCR_JSON}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ocr", action="store_true", help="also run Marker on the PDF")
    ap.add_argument("--allow-hash-mismatch", action="store_true")
    ap.add_argument("--page-scale", type=float, default=2.0, help="render scale for page images (1 = 72 dpi)")
    a = ap.parse_args()
    print(f"config: {C.CONFIG_PATH}")
    fetch_paper(a.allow_hash_mismatch)
    fetch_lean()
    text_layer()
    page_images(a.page_scale)
    if a.ocr:
        ocr()
    elif not C.OCR_JSON.exists():
        print(f"ocr: not run. Run `python audit/fetch.py --ocr` in the OCR environment, or\n"
              f"  marker_single {C.PDF} --output_format json --output_dir {C.DATA / 'ocr'}")
    print("next: python audit/paper_index.py && python audit/ocr_attach.py && python audit/lean_index.py")


if __name__ == "__main__":
    main()
