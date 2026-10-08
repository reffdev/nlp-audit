# Navier–Stokes paper vs. Lean: correspondence audit

> **Status: preliminary.** Nothing here has yet been reviewed by a mathematician. Every listed difference is a
> difference in how the paper and the Lean code state something, not a claimed error.

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
  may claim more than was formalized. That judgment is left to experts. See [METHODOLOGY.md](METHODOLOGY.md).

## Where to start

- **[`out/review_shortlist.md`](out/review_shortlist.md)**: the differences most worth an expert's time, selected
  mechanically, each with quotes and links to the PDF page and the Lean line.
- **`out/report.html`**: everything on one page. GitHub shows HTML as source code, so download it and open it in a
  browser.
- **[METHODOLOGY.md](METHODOLOGY.md)**: how it works, how it was checked, and its limitations.

## Results so far

- **Paper ↔ Lean map, whole paper.** For 77 of the paper's 80 numbered results, the tool located a Lean declaration
  that all 3 independent samples agreed on; 3 are weak matches (2 of 3 samples); none were left unlocated. The
  formalization has no blueprint, and the paper references in its comments follow an earlier draft's numbering, so
  this map is new. A decoy test suggests roughly 1 in 10 confident locations may point at the wrong declaration.
- **Differences, pilot.** Section 8, Lemma 10.5, and 8 numbered steps inside the proofs of Lemmas 8.2, 8.6 and 10.5:
  58 (paper result or step, Lean declaration) pairs, 717 grouped differences, 251 reported by all 3 samples. Many are
  naming or explicit conditions that the paper leaves implicit; the shortlist filters for differences in what is
  estimated.
- **Validation.** Both discrepancies identified by Bastounis et al. were reported by all 3 samples without any prompt
  mentioning them: Lemma 8.6 (m+4 derivatives in the paper, m+5 in the Lean) and eq. (10.19) inside the proof of
  Lemma 10.5 (a pressure-flux bound of a different shape).

## Versions audited

| Source | Version |
|---|---|
| Paper | PDF as downloaded 2026-10-07, SHA-256 `0e779481c4da40bd28d1e642e1d8ca57447d129610df28dfa5a11e9af8ae228f` |
| Lean | `openai/NavierStokesAndEuler` at commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, `NavierStokes/` only |
| Model | `nvidia/Qwen3.8-27B-NVFP4` (open weights), served locally with vLLM, 128k context, reasoning enabled |

## How it was made

The analysis is done by a language model, run locally on open weights so anyone can reproduce it; every model
response is logged and cached, and every quoted passage is checked mechanically against its source. The code and
documentation were written with an AI coding assistant (Claude, by Anthropic) under the author's direction.

## Running it

- Main environment: `pip install -r requirements.txt`, plus `pdftotext` (poppler or xpdf) on PATH.
- OCR environment: `pip install -r requirements-ocr.txt` in a separate Python 3.12 environment with a CUDA build of
  PyTorch.
- A model server with an OpenAI-compatible API. Configure with `AUDIT_LLM_BASE_URL`, `AUDIT_LLM_MODEL`,
  `AUDIT_LLM_MAX_CONCURRENCY`.
- The full command sequence is in [METHODOLOGY.md](METHODOLOGY.md#reproducing).

The published results took about 18 hours of run time on a single 96 GB workstation GPU (RTX PRO 6000 Blackwell),
almost all of it model reasoning. The paper and the Lean repository are fetched, not redistributed.

## License

- Code (`audit/`): [Apache License 2.0](LICENSE).
- Documentation and data (`out/`, `METHODOLOGY.md`, this README): [CC BY 4.0](LICENSE-CC-BY-4.0.md).
- Short excerpts quoted from the paper (OpenAI) and from the Lean source (openai/NavierStokesAndEuler, Apache-2.0)
  remain under their original terms; they are included only to identify the passages compared.
