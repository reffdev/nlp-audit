# Navier–Stokes: paper vs. Lean

**v0.1, preliminary. No mathematician has reviewed any of this yet.**

OpenAI's paper *Finite time blowup for Navier–Stokes*
([PDF](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)) comes with a Lean 4
formalization, [openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler). Lean checks the
proofs of the two main theorems, and the repo's Comparator challenges check their statements against reference
versions built on Google DeepMind's [formal-conjectures](https://github.com/google-deepmind/formal-conjectures).
What nothing checks is whether the many intermediate lemmas in the Lean are the ones in the paper. Bastounis,
Circelli and Hansen found places where they aren't
([arXiv:2610.08144](https://arxiv.org/abs/2610.08144)).

This repo tries to make that comparison for the whole paper. For each numbered result, a language model finds
the Lean declarations that formalize it, writes down what each side assumes and proves, and lists the
differences. Every difference comes with a quote from the paper (with page) and from the Lean (with file and
line), and the quotes are checked against the sources by ordinary code.

It doesn't tell you whether the main theorem is true. That's the Lean proof's job. It also doesn't tell you
whether a difference matters. Many are harmless rewordings; some might mean the paper claims more than the Lean
proves. Sorting those out takes a mathematician, and I'm not one.

## Where to start

For an overview of all the results on one page, read [`out/summary.md`](out/summary.md): the headline numbers,
the validation hits, a table of every pair compared, and the full paper-to-Lean map.

For the differences themselves, start with [`out/review_shortlist.md`](out/review_shortlist.md). It has 21 differences, picked mechanically
as the ones most worth an expert's time. Part A (8 entries) is about what is being estimated. Part B (13) is
about how size is measured, and is mostly notation. Each entry has both quotes and links to the PDF page and
the Lean line.

The rest of `out/`:

| File | What's in it |
|---|---|
| [`summary.md`](out/summary.md) | The overview above, readable on GitHub. |
| `report.html` | Everything on one page, with filters. Download it and open it locally; GitHub only shows the source. |
| [`paper_lean_map.csv`](out/paper_lean_map.csv) | The paper-to-Lean map: each paper result or proof step searched (88 rows), the Lean declaration found, file and lines, how many of the 3 samples agreed, which search round. |
| [`audit_table.csv`](out/audit_table.csv) | One row per (paper result, Lean declaration) pair that was compared (58 rows). |
| [`differences.csv`](out/differences.csv) | Every grouped difference (1,014 rows): type, agreement, both quotes and whether they checked out, page and lines, and each sample's own wording. |
| [`paper_items_not_matched.csv`](out/paper_items_not_matched.csv) | Targets without a 3-of-3 match (4 rows). |
| [`lean_theorems_without_paper_counterpart.csv`](out/lean_theorems_without_paper_counterpart.csv) | Theorems in the compared files that weren't matched to anything in the paper (1,945 rows), mostly supporting steps. |
| [`source_scan.csv`](out/source_scan.csv) | Counts of `sorry`, `axiom`, `admit`, `native_decide`, `unsafe` and a few rarer escape hatches, per Lean file. All zero outside the Comparator challenge files. |
| [`duplicate_statements.csv`](out/duplicate_statements.csv) | Theorems under `NavierStokes/` whose statements are copies of each other (187 groups), with file and line for each copy and what uses it. |
| [`external_imports.csv`](out/external_imports.csv) | Imports from anything other than Mathlib and the repo itself. There are none. |

How it all works, and what was done to check it, is in [METHODOLOGY.md](METHODOLOGY.md).

I haven't included the working database (`data/audit.db`) or the raw model log (`data/llm_raw.jsonl`)
because both contain the full text of the paper. You don't need them to check anything here: the CSVs
are enough to recompute every number, and every quote can be looked up in the paper and in the Lean at the
pinned commit.

## Results so far

**The map.** 77 of the paper's 80 numbered results got a Lean match that all 3 samples agreed on. The other
3 got 2 out of 3, and none came up empty. There's no blueprint for this formalization, and the paper
references in the Lean comments use an older draft's numbering, so I don't know of another map like this. A
decoy test suggests at least 1 in 10 of the confident matches could be wrong.

**The differences** (pilot only: Section 8, Lemma 10.5, and the numbered equations inside the proofs of
Lemmas 8.2, 8.6 and 10.5). That's 58 paper/Lean pairs and 1,014 grouped differences, 322 of which all 3
samples reported. Most are noise: different names, or the Lean spelling out conditions the paper leaves
implicit. Only 17 of the 58 pairs are on the path to the main theorems that the tool could detect.

**Validation.** Both discrepancies from Bastounis et al. showed up in all 3 samples: Lemma 8.6 (m+4
derivatives in the paper, m+5 in the Lean) and eq. (10.19) in the proof of Lemma 10.5 (the first term of the
pressure-flux bound has a different form). That's weaker evidence than it sounds. I put Lemmas 8.6 and 10.5
on the target list because of their paper. The prompts never mention the discrepancies, but the tool didn't
pick where to look. And the Lean docstring for the Lemma 8.6 theorem says "five torus derivatives lost", so
the Lean was never hiding it.

**Eq. (8.10)**, the first shortlist entry. The paper needs p+3 derivatives there; the Lean version, a general
multiplier lemma, needs l+4. I followed this one up by hand after the run, with Claude's help; a
mathematician still needs to look at it. The Lean gets its Lemma 8.6 bound by plugging l = 1 into that general
lemma, which is where the m+5 comes from. The paper proves Lemma 8.6 on its own and never uses (8.10). So in
the Lean the two differences have one cause, and in the paper they're unrelated. The Lean lemma also differs
from (8.10) in a few other ways. Details are in
[METHODOLOGY.md](METHODOLOGY.md#810-followed-up-by-hand).

**Static checks on the Lean source** (text only, nothing compiled). No `sorry`, `axiom`, `admit`,
`native_decide` or `unsafe` anywhere under `NavierStokes/`; the only `sorry`s in the repo are the intended
placeholders in the Comparator challenge files. That matches what the repo says about itself, though only Lean
can confirm which axioms a proof actually uses. 474 theorems turn out to be copies of each other, in 187
groups, mostly the same small fact proved again in another file; one of them is restated 83 times. And for
each matched result there's now a `def_depth` column: how many layers of the formalization's own definitions
sit under its statement before you reach Mathlib. It ranges from 0 to 55, and the deep ones are where a human
read is most worth having. Details are in [METHODOLOGY.md](METHODOLOGY.md#static-checks-on-the-lean-source).

## Known weaknesses

The biggest one is that matches are made on resemblance. A Lean declaration gets matched to a paper result
because its statement looks like the paper's, not because the proof uses it where the paper uses that result.
(8.10) shows why that's a problem: the declaration all 3 samples picked isn't used by the main proof at all,
and the one the proof does use got 2 votes out of 3.

There's also no dependency graph on the paper side, so the tool can't see when the paper and the Lean take
different routes to the same result. The (8.10) finding came from reading the code, not from the tool.

Finally, the Lean index comes from parsing the `.lean` files rather than from Lean itself. The static
checks found one way it goes wrong: 3.4% of theorem statements were cut off partway, and while it was looking
for matches the model saw 3.3% of the statements it read without their full conclusion. Extraction wasn't
affected. Comparing against Lean itself would need a
build, which I haven't done.

A version 2 would fix all three: build the Lean index and dependency graph from Lean, build the matching
graph for the paper, match on structure as well as resemblance, and produce a machine-inferred blueprint that
people can correct. There's a sketch in [METHODOLOGY.md](METHODOLOGY.md#planned-fixes).

## Versions audited

| | |
|---|---|
| Paper | PDF downloaded 2026-10-07, SHA-256 `0e779481c4da40bd28d1e642e1d8ca57447d129610df28dfa5a11e9af8ae228f` |
| Lean | `openai/NavierStokesAndEuler` at `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, `NavierStokes/` only |
| Model | `nvidia/Qwen3.8-27B-NVFP4` (open weights) on vLLM, 128k context, reasoning on |

## How it was made

The reading and comparing is done by an open-weights model running on my own GPU. Every response is logged and
cached. The code and these docs were written with Claude (Anthropic's coding assistant), at my direction.

## Running it

You'll need:

- Python 3.12+ with `pip install -r requirements.txt`, and `pdftotext` (poppler or xpdf) and `git` on your PATH.
- For the OCR step, a separate Python 3.12 environment with `pip install -r requirements-ocr.txt` and a CUDA
  build of PyTorch. Its output is a JSON file; everything else runs in the main environment.
- A model server with an OpenAI-compatible chat API that can return JSON, with about 128k tokens of context
  (prompts peak around 67k). Reasoning helps. Point the scripts at it with `AUDIT_LLM_BASE_URL`,
  `AUDIT_LLM_MODEL`, `AUDIT_LLM_API_KEY` and `AUDIT_LLM_MAX_CONCURRENCY`.

Fetch the inputs. The paper is checked against its hash and the Lean repo is fetched at the pinned commit;
neither is redistributed here.

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

The full sequence is in [METHODOLOGY.md](METHODOLOGY.md#reproducing). Responses are cached by prompt in
`data/llm_raw.jsonl`, so if a run gets interrupted it picks up where it left off.

## Tokens and cost

From the raw log of the published run: 1,313 calls, 3 samples per prompt. Output tokens include the model's
reasoning.

| Stage | Scales with | Calls | Input | Output | Per call |
|---|---|---|---|---|---|
| Picking files (catalog, neighbours, retry rounds) | targets × catalog (816 files ≈ 47k tokens) × 3 × rounds | 339 | 15.5M | 4.3M | ~46k in, ~13k out |
| Reading declarations | targets × declarations in the candidate files, in ~50k-token chunks | 693 | 35.3M | 9.4M | ~51k in, ~14k out |
| Decoy test (21 targets) | as above, one round | 63 | 3.0M | 0.4M | ~47k in, ~6k out |
| Extraction (58 pairs) | pairs × 3; short prompts, long answers | 218 | 0.8M | 5.8M | ~3.6k in, ~27k out |
| **Total** (88 targets located, 58 pairs compared) | | **1,313** | **54.6M** | **19.9M** | |

Finding the Lean counterparts is the expensive part, about 620k input tokens per target, nearly all of it
the file catalog and declaration text sent three times over. Extraction is cheap on input but heavy on output,
about 90k output tokens per pair. Running extraction on all 80 results would add roughly 3 to 5 times the
extraction row; locating already covers the whole paper. An API with prompt caching would cut the input side a
lot, since the same catalog and chunks go out for every sample and round.

At October 2026 list prices this run would cost about $310 on a model at $2/$10 per million input/output
tokens (Claude Sonnet 5.5), about $620 at $4/$20 (Claude Opus 5.5), and half that with batch pricing. Another
model will produce a different number of output tokens, since most of them are reasoning. Locally it took about
18 hours on one RTX PRO 6000 Blackwell (96 GB) at 14 concurrent requests.

## Using it on another paper

Everything specific to this paper and this Lean repo lives in [`audit.toml`](audit.toml): the paper's URL and
hash, the patterns for its running heads and result numbers, the Lean repo, commit and folder, the names of the
top-level theorems, the pilot targets, and the known discrepancies used for validation. The scripts in
`audit/` read it through `audit/config.py` and know nothing else about the target. To point it at a different
paper, copy `audit.toml`, edit it, set `AUDIT_CONFIG` to the copy, and run the same commands.

Each stage is a separate script, and they only talk to each other through the SQLite database:

| Stage | Script | Reads | Writes |
|---|---|---|---|
| Fetch | `fetch.py` | `audit.toml` | `data/*.pdf`, `repo/`, text layer, page images |
| Paper index | `paper_index.py`, `ocr_attach.py` | text layer, OCR JSON | `paper_*` tables |
| Lean index | `lean_index.py`, `xref_cheap.py` | `repo/<subdir>` | `lean_*`, `xref_*` tables |
| Locate | `xref_llm.py`, `xref_search.py`, `proof_steps.py`, `decoy_test.py` | both indexes, the model | `search_*`, `decoy_*` tables |
| Extract | `extract.py` | located pairs, the model | `extract_*` tables |
| Static checks | `static_checks.py` | `repo/`, Lean index | `static_*` tables, `out/source_scan.csv`, `out/duplicate_statements.csv`, `out/external_imports.csv` |
| Report | `report.py` | all of the above | `out/` |

The paper index expects a PDF with a text layer, a table of contents up front, section headers that repeat
their contents line, numbered results like "Lemma 8.6." at the start of a paragraph, and equation numbers at
the right margin. A paper typeset differently will need changes to `paper_index.py`. The Lean side only needs
Lean 4 source files; nothing has to be built.

## License

Code (`audit/`) is under the [Apache License 2.0](LICENSE). Docs and data (`out/`, `METHODOLOGY.md`, this
README) are under [CC BY 4.0](LICENSE-CC-BY-4.0.md). The short excerpts quoted from the paper (OpenAI) and the
Lean source (openai/NavierStokesAndEuler, Apache-2.0) stay under their original terms and are only there to
identify the passages being compared.
