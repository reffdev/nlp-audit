# Using the tool

How to run the audit yourself, what it costs, and how to point it at a different paper. For what the tool found, start with the [README](README.md); for how it works and how far to trust it, see [METHODOLOGY.md](METHODOLOGY.md).

## Requirements

- Python 3.12+ with `pip install -r requirements.txt`, and `pdftotext` (poppler or xpdf) and `git` on your PATH.
- For the OCR step, a separate Python 3.12 environment with `pip install -r requirements-ocr.txt` and a CUDA build of PyTorch. Its output is a JSON file; everything else runs in the main environment.
- A model server with an OpenAI-compatible chat API that can return JSON, with about 128k tokens of context (prompts peak around 67k). Reasoning helps. Point the scripts at it with `AUDIT_LLM_BASE_URL`, `AUDIT_LLM_MODEL`, `AUDIT_LLM_API_KEY` and `AUDIT_LLM_MAX_CONCURRENCY`.

No Lean installation is needed. The tool reads the Lean source files; nothing is compiled.

## Running it

Fetch the inputs. The paper is checked against its hash and the Lean repo is fetched at the pinned commit; neither is redistributed in this repo.

```bash
python audit/fetch.py
```

OCR, in the OCR environment:

```bash
python audit/fetch.py --ocr
```

Build the indexes:

```bash
python audit/paper_index.py && python audit/ocr_attach.py && python audit/lean_index.py && python audit/xref_cheap.py
```

Try a single result end to end (a few model calls):

```bash
python audit/xref_llm.py files --items "Lemma 10.5" && python audit/xref_search.py --items "Lemma 10.5" && python audit/extract.py --section 10 --items "Lemma 10.5" && python audit/report.py
```

The full sequence for the published run is in [METHODOLOGY.md](METHODOLOGY.md#reproducing). Responses are cached by prompt in `data/llm_raw.jsonl`, so if a run gets interrupted it picks up where it left off. Responses are cached by a key covering the model name, the reasoning setting, temperature, token budget and the prompt. To reuse the published responses, download `llm_raw.jsonl.gz` from the v0.2 release (it holds the v0.1 and v0.2 runs) and unzip it to `data/llm_raw.jsonl`. Those responses were logged under an older key that didn't include temperature and budget, so set `AUDIT_LLM_LEGACY_CACHE=1` to reuse them, with `AUDIT_LLM_MODEL` set to exactly `nvidia/Qwen3.8-27B-NVFP4` and reasoning left on (`AUDIT_LLM_THINKING` unset or `1`). A rerun with the same inputs then reads from the cache instead of calling the model; any other model name or setting misses it. Set `AUDIT_RUN_ID` to label a new run; reports read only the current run's rows.

## How the pieces fit

Each stage is a separate script, and they only talk to each other through a SQLite database (`data/audit.db`):

| Stage | Script | Reads | Writes |
|---|---|---|---|
| Fetch | `fetch.py` | `audit.toml` | `data/*.pdf`, `repo/`, text layer, page images |
| Paper index | `paper_index.py`, `ocr_attach.py` | text layer, OCR JSON | `paper_*` tables |
| Lean index | `lean_index.py`, `xref_cheap.py` | `repo/<subdir>` | `lean_*`, `xref_*` tables |
| Locate | `xref_llm.py`, `xref_search.py`, `proof_steps.py`, `decoy_test.py` | both indexes, the model | `search_*`, `decoy_*` tables |
| Extract | `extract.py` | located pairs, the model | `extract_*` tables |
| Static checks | `static_checks.py` | `repo/`, Lean index | `static_*` tables, `out/source_scan.csv`, `out/duplicate_statements.csv`, `out/external_imports.csv` |
| Report | `report.py` | all of the above | `out/` |

## Tokens and cost

Cost depends on three things: how many paper targets you locate, how many (paper result, Lean declaration) pairs you compare, and how big the Lean repository is. These per-unit figures come from the published run (88 targets located in a repository of 816 files, 58 pairs compared, 3 samples per prompt). Output tokens include the model's reasoning, so another model will produce a different number of them.

| Unit | What drives it | Input per unit | Output per unit | At $2 / $10 per M tokens |
|---|---|---|---|---|
| Locating one target | the file catalog (≈ 47k tokens for 816 files) and the declarations in the candidate files, × 3 samples × up to 3 rounds | ~580k | ~155k | ~$2.70 |
| Comparing one pair | short prompts, long structured answers, × 3 samples | ~14k | ~100k | ~$1.00 |
| One decoy target (optional check) | as locating, one round | ~140k | ~17k | ~$0.45 |

So a rough estimate is targets × $2.70 + pairs × $1.00 at those prices, and twice that at $4 / $20. Locating scales with the size of the Lean repository: a formalization a tenth the size would cost far less per target, since both the catalog and the candidate files shrink. An API with prompt caching cuts the input side a lot, because the same catalog and declaration chunks go out for every sample and round. What this paper's run cost in total is in the [README](README.md#cost).

## Using it on another paper

Everything specific to this paper and this Lean repo lives in [`audit.toml`](audit.toml): the paper's URL and hash, the patterns for its running heads and result numbers, the Lean repo, commit and folder, the names of the top-level theorems, the pilot targets, and the known discrepancies used for validation. The scripts in `audit/` read it through `audit/config.py` and know nothing else about the target. To point it at a different paper, copy `audit.toml`, edit it, set `AUDIT_CONFIG` to the copy, and run the same commands.

The paper index expects a PDF with a text layer, a table of contents up front, section headers that repeat their contents line, numbered results like "Lemma 8.6." at the start of a paragraph, and equation numbers at the right margin. A paper typeset differently will need changes to `paper_index.py`. The Lean side only needs Lean 4 source files.
