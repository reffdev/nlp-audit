# Navier–Stokes paper vs. Lean: correspondence audit

Tooling that compares OpenAI's paper *Finite time blowup for Navier–Stokes*
([PDF](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf)) with its Lean 4
formalization ([openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler)), and lists where
the two state things differently.

Lean checks that the formal theorems are proved. It does not check that the formal proof is the proof the paper
gives, or that each formal statement says what the paper says. Bastounis, Circelli and Hansen showed concrete
mismatches of this kind in this formalization (*Navier-Stokes lost in translation: Why Lean verification of AI
autoformalisation does not guarantee correct natural language proofs*,
[arXiv:2610.08144](https://arxiv.org/abs/2610.08144)). This project builds tooling to look for such mismatches
systematically.

**This tool finds differences; it does not decide whether they matter.** Every reported difference carries a
verbatim quote from the paper (with page) and from the Lean source (with file and line), and is meant for
expert review. See [METHODOLOGY.md](METHODOLOGY.md) for what is and is not established.

## Results so far

- **Paper ↔ Lean map, whole paper:** 77 of 80 numbered results located with all 3 independent samples agreeing;
  3 weak matches; none unlocated. The formalization ships no blueprint, and the paper references in its comments
  follow an earlier draft's numbering, so this map is new.
- **Differences, pilot:** Section 8, Lemma 10.5, and 8 numbered steps inside the proofs of Lemmas 8.2, 8.6 and
  10.5: 58 (paper result or step, Lean declaration) pairs, 717 grouped differences, 251 reported by all 3
  samples. See `out/report.html` and the 21-entry `out/review_shortlist.md`.
- **Validation:** both discrepancies identified by Bastounis et al. were reported by all 3 samples without any
  prompt mentioning them: Lemma 8.6 (m+4 derivatives in the paper, m+5 in the Lean) at statement level, and
  eq. (10.19) (a differently shaped pressure-flux bound) at proof level. A decoy test bounds how often a
  confident location is wrong (2 of 21).
- **Unreviewed lead:** eq. (8.10) in the proof of Lemma 8.2 appears to show the same derivative gap in general
  form (p+3 in the paper, p+4 in `applyMultiplier_finiteJets`). It needs expert confirmation.

## Outputs

| File | Contents |
|---|---|
| `out/report.html` | Everything on one static page, citations linked to the PDF page and the Lean line on GitHub |
| `out/review_shortlist.md` | The differences most worth an expert's time, selected mechanically, with quotes and links |
| `out/audit_table.csv` | One row per (paper result, Lean declaration) pair, most severe difference first |
| `out/differences.csv` | One row per grouped difference: type, agreement (of 3 samples), both quotes, all wordings |
| `out/paper_items_not_matched.csv` | Paper results without a confident Lean counterpart |
| `out/lean_theorems_without_paper_counterpart.csv` | Theorems in the pilot files not located for any paper result |

## Running it

Requirements: Python 3.12+ with `openai pdfplumber pylatexenc scikit-learn numpy`, `pdftotext` (poppler/xpdf),
Marker 1.8.4 in a separate environment for OCR, and an OpenAI-compatible endpoint serving the model (the results
here used `nvidia/Qwen3.8-27B-NVFP4` on vLLM, 128k context). Configure with `AUDIT_LLM_BASE_URL`,
`AUDIT_LLM_MODEL`, `AUDIT_LLM_MAX_CONCURRENCY`. The full sequence is in METHODOLOGY.md ("Reproducing").

Third-party sources (the paper, the Lean repository) are fetched, not redistributed.

## License

- Code (`audit/`): [Apache License 2.0](LICENSE).
- Documentation and data (`out/`, `METHODOLOGY.md`, this README): [CC BY 4.0](LICENSE-CC-BY-4.0.md).
- Short excerpts quoted from the paper (OpenAI) and from the Lean source (openai/NavierStokesAndEuler,
  Apache-2.0) remain under their original terms; they are included only to identify the passages compared.
