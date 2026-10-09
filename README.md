# Navier–Stokes paper vs. Lean: correspondence audit

> **Status: v0.1, preliminary.** Nothing here has yet been reviewed by a mathematician. Every listed difference
> is a difference in how the paper and the Lean code state something, not a claimed error. See
> [Known weaknesses](#known-weaknesses).

Tooling that compares OpenAI's paper *Finite time blowup for Navier–Stokes*
([PDF](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)) with its Lean 4
formalization ([openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler)), and lists where the
two state things differently.

## What this is, and what it is not

The formalization's two top-level theorems are machine-checked, and their statements are compared against
independent reference statements (the repository's Comparator challenges, built on Google DeepMind's
[formal-conjectures](https://github.com/google-deepmind/formal-conjectures)). What is not checked by machine is
whether the many intermediate lemmas, and the route of the proof, are the ones the paper describes. Bastounis,
Circelli and Hansen showed concrete mismatches of that kind in this formalization (*Navier-Stokes lost in
translation: Why Lean verification of AI autoformalisation does not guarantee correct natural language proofs*,
[arXiv:2610.08144](https://arxiv.org/abs/2610.08144)). This project looks for such mismatches systematically.

- It **does not** assess whether the main theorem is true. That is what the Lean proof establishes.
- It **does** ask, result by result, whether what the paper states is what the Lean code proves, and lists every
  difference it finds, with a verbatim quote from the paper (page) and the Lean source (file and line).
- It **does not** decide whether a difference matters. A difference may be a harmless reformulation, or the paper
  may claim more than was formaliz-ed. That judgment is left to experts. See [METHODOLOGY.md](METHODOLOGY.md).

## Outputs

All results are in [`out/`](out/).

| File | Contents |
|---|---|
| [`review_shortlist.md`](out/review_shortlist.md) | Differences selected mechanically for expert review. Part A: differences in what is estimated (8 entries). Part B: differences in how size is measured (13 entries). Each entry carries both quotes and links to the PDF page and the Lean line. |
| `report.html` | Every pair and every difference on one static page with filters, together with the tables below. Rendered locally; GitHub displays the source. |
| [`paper_lean_map.csv`](out/paper_lean_map.csv) | The paper-to-Lean map: one row per paper result or proof step searched (88 rows), with the located declaration, its file and lines, how many of the 3 samples agreed, and the search round. Further declarations all samples agreed on are in `other_agreed_decls`. |
| [`audit_table.csv`](out/audit_table.csv) | One row per extracted (paper item, Lean declaration) pair (58 rows): membership of the main proof path, difference types reported, most severe agreed difference. |
| [`differences.csv`](out/differences.csv) | One row per grouped difference (1,014 rows): type, agreement, both sides' claims, verbatim paper and Lean quotes with verification flags, page and Lean lines, every sample's wording. |
| [`paper_items_not_matched.csv`](out/paper_items_not_matched.csv) | Targets without a 3-of-3 location (4 rows). |
| [`lean_theorems_without_paper_counterpart.csv`](out/lean_theorems_without_paper_counterpart.csv) | Theorems in the extracted pairs' files not located for any paper item (1,945 rows), with the number of other files using each. |

[METHODOLOGY.md](METHODOLOGY.md) describes the method, its checks and its limitations.

The working database (`data/audit.db`) and the raw model log (`data/llm_raw.jsonl`) are not included because they
contain the full paper text. The CSVs are sufficient to recompute every number in this README, and every quote can
be checked against the paper and the Lean source at the pinned commit.

## Results so far

- **Paper ↔ Lean map, whole paper.** For 77 of the paper's 80 numbered results, the tool located a Lean declaration
  that all 3 independent samples agreed on; 3 are weak matches (2 of 3 samples); none were left unlocated. The
  formalization has no blueprint, and the paper references in its comments follow an earlier draft's numbering, so
  this map is new. A decoy test suggests at least 1 in 10 confident locations may point at the wrong declaration.
- **Differences, pilot.** Section 8, Lemma 10.5, and 8 numbered steps inside the proofs of Lemmas 8.2, 8.6 and 10.5:
  58 (paper result or step, Lean declaration) pairs, 1,014 grouped differences, 322 reported by all 3 samples. Many are
  naming or explicit conditions that the paper leaves implicit; the shortlist separates differences in what is
  estimated (Part A, 8 entries) from differences in how size is measured (Part B, 13 entries, mostly notation).
  Only 17 of the 58 pairs lie on the dependency path to the two main theorems that the tool could detect.
- **Validation.** Both discrepancies identified by Bastounis et al. were reported by all 3 samples: Lemma 8.6 (m+4
  derivatives in the paper, m+5 in the Lean) and eq. (10.19) inside the proof of Lemma 10.5 (the first term of the
  pressure-flux bound has a different form). Lemma 8.6 and Lemma 10.5 were put on the target list *because* that
  paper had flagged them; the model prompts never mention the discrepancies, the derivative counts or the bound.
  The Lean docstring of the Lemma 8.6 theorem itself says "five torus derivatives lost", so the difference is
  documented on the Lean side and only unflagged relative to the paper.
- **Eq. (8.10), followed up by hand.** The first shortlist entry: (8.10), in the proof of Lemma 8.2, needs p+3
  derivatives; its Lean counterpart, a general multiplier lemma, needs l+4. A manual reading after the run
  (not pipeline output, not reviewed by a mathematician) finds that the Lean proves Lemma 8.6 by applying
  that general lemma with l = 1, which is where its m+5 comes from, whereas the paper proves Lemma 8.6
  separately and does not use (8.10). The two differences share one cause in the Lean but not in the paper.
  The Lean lemma is also more general than (8.10) in other respects. Details in
  [METHODOLOGY.md](METHODOLOGY.md#manual-follow-up-of-the-810-entry).

## Known weaknesses

- **Matching is by resemblance.** A Lean declaration is matched to a paper result because its statement looks
  like the paper's, not because it plays the same role in the proof. For (8.10), the declaration all 3 samples
  chose is not used by the main proof; the one the proof uses was chosen by 2 of 3.
- **There is no paper-side dependency graph.** The tool cannot see when the paper and the Lean prove something
  by different routes; the (8.10) finding above came from reading, not from the tool.
- **The Lean index is parsed from source**, not read from Lean's elaborated environment, and its accuracy has
  not been measured against Lean.

A second version would build the Lean index and dependency graph from Lean itself, build the matching graph on
the paper side, match on structure as well as resemblance, and output a machine-inferred blueprint that people
can correct. See [METHODOLOGY.md](METHODOLOGY.md#planned-fixes).

## Versions audited

| Source | Version |
|---|---|
| Paper | PDF as downloaded 2026-10-07, SHA-256 `0e779481c4da40bd28d1e642e1d8ca57447d129610df28dfa5a11e9af8ae228f` |
| Lean | `openai/NavierStokesAndEuler` at commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, `NavierStokes/` only |
| Model | `nvidia/Qwen3.8-27B-NVFP4` (open weights), served locally with vLLM, 128k context, reasoning enabled |

## How it was made

The analysis is done by a language model, run locally on open weights; every model response is logged and
cached, and every quoted passage is checked mechanically against its source. The code and documentation were
written with an AI coding assistant (Claude, by Anthropic) under the author's direction.

## Running it

Requirements:

- Python 3.12 or newer with `pip install -r requirements.txt`, plus `pdftotext` (poppler or xpdf) and `git` on PATH.
- For the OCR step only: `pip install -r requirements-ocr.txt` in a separate Python 3.12 environment with a CUDA
  build of PyTorch (Marker). The OCR output is a JSON file; everything else runs in the main environment.
- A model server with an OpenAI-compatible chat API that returns JSON, with a context window of about 128k tokens
  (prompts peak near 67k) and, ideally, reasoning enabled. Configure with `AUDIT_LLM_BASE_URL`, `AUDIT_LLM_MODEL`,
  `AUDIT_LLM_API_KEY` and `AUDIT_LLM_MAX_CONCURRENCY`.

Inputs (the paper is hash-checked; the Lean repository is fetched at the pinned commit; neither is redistributed):

```bash
python audit/fetch.py
```

OCR, in the OCR environment:

```bash
python audit/fetch.py --ocr
```

Indexes:

```bash
python audit/paper_index.py && python audit/ocr_attach.py && python audit/lean_index.py && python audit/xref_cheap.py
```

A single result end to end, a few model calls:

```bash
python audit/xref_llm.py files --items "Lemma 10.5" && python audit/xref_search.py --items "Lemma 10.5" && python audit/extract.py --section 10 --items "Lemma 10.5" && python audit/report.py
```

The full sequence is in [METHODOLOGY.md](METHODOLOGY.md#reproducing). Model responses are cached by prompt in
`data/llm_raw.jsonl`, so an interrupted run resumes where it stopped.

## Token usage and cost

Measured from the raw model log of the published run: 1,313 calls, 3 samples per prompt; output tokens include
the model's reasoning.

| Stage | What drives it | Calls | Input tokens | Output tokens | Per call |
|---|---|---|---|---|---|
| File selection (catalog, neighbours, retry rounds) | targets × catalog size (816 files ≈ 47k tokens) × 3 samples × rounds | 339 | 15.5M | 4.3M | ~46k in, ~13k out |
| Declaration reading | targets × declarations in the candidate files, in chunks of ~50k tokens | 693 | 35.3M | 9.4M | ~51k in, ~14k out |
| Decoy test (21 targets) | same as declaration reading, one round | 63 | 3.0M | 0.4M | ~47k in, ~6k out |
| Extraction (58 pairs) | pairs × 3 samples; short prompts, long structured output | 218 | 0.8M | 5.8M | ~3.6k in, ~27k out |
| **Total** (88 targets located, 58 pairs extracted) | | **1,313** | **54.6M** | **19.9M** | |

Locating dominates: about 620k input tokens per target, almost all of it the file catalog and declaration text sent
three times. Extraction is cheap on input and expensive on output, about 90k output tokens per pair. Extending
extraction to all 80 results would add roughly 3 to 5 times the extraction row; locating is already whole-paper.
Prompt caching on an API that offers it would cut the input side substantially, since the same catalog and
declaration chunks are sent for every sample and round.

At list prices as of October 2026, the run above costs about $310 on a model priced at $2 per million input and
$10 per million output tokens (Claude Sonnet 5.5), about $620 at $4 and $20 (Claude Opus 5.5), and half that
with batch pricing. Output token counts will differ on another model, since most of them are reasoning. On the
local open-weights model the run took about 18 hours of wall time on one 96 GB GPU (RTX PRO 6000 Blackwell) at
14 concurrent requests.

## Using it on another paper

Everything specific to this paper and this Lean repository is in [`audit.toml`](audit.toml): the paper's URL and
hash, the patterns of its running heads and result numbers, the Lean repository, commit and subdirectory, the
names of the top-level theorems, which results form the pilot, and the known discrepancies used as validation
targets. The scripts in `audit/` read it through `audit/config.py` and contain nothing else about the target.
To audit a different paper, copy `audit.toml`, edit the values, set `AUDIT_CONFIG` to the copy, and run the same
commands. The stages are separate scripts with the SQLite database as their only interface:

| Stage | Script | Reads | Writes |
|---|---|---|---|
| Fetch | `fetch.py` | `audit.toml` | `data/*.pdf`, `repo/`, text layer, page images |
| Paper index | `paper_index.py`, `ocr_attach.py` | text layer, OCR JSON | `paper_*` tables |
| Lean index | `lean_index.py`, `xref_cheap.py` | `repo/<subdir>` | `lean_*`, `xref_*` tables |
| Locate | `xref_llm.py`, `xref_search.py`, `proof_steps.py`, `decoy_test.py` | both indexes, the model | `search_*`, `decoy_*` tables |
| Extract | `extract.py` | located pairs, the model | `extract_*` tables |
| Report | `report.py` | all of the above | `out/` |

What the paper index assumes: a PDF with a text layer, a table of contents before the body, section headers that
repeat the contents line, numbered results of the form "Lemma 8.6." at the start of a paragraph, and numbered
displayed equations with their label at the right margin. Papers typeset differently will need changes in
`paper_index.py`. The Lean index assumes Lean 4 source files and needs no build.

## License

- Code (`audit/`): [Apache License 2.0](LICENSE).
- Documentation and data (`out/`, `METHODOLOGY.md`, this README): [CC BY 4.0](LICENSE-CC-BY-4.0.md).
- Short excerpts quoted from the paper (OpenAI) and from the Lean source (openai/NavierStokesAndEuler, Apache-2.0)
  remain under their original terms; they are included only to identify the passages compared.
