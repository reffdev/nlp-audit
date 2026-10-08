# Methodology: auditing the Navier–Stokes paper against its Lean formalization

## What this establishes, and what it does not

This tool finds **where the paper and the Lean formalization state things differently**. For each
paper result it locates the Lean declarations that formalize it, extracts what each side assumes and
concludes, and lists the differences, each with a verbatim quote from both sources.

It does **not** say whether any difference matters. A listed difference may be harmless (a different
but equivalent formulation, a hypothesis the paper leaves implicit), or it may mean the paper claims
something the Lean does not prove. Deciding that is a mathematician's job. No model was asked whether
anything "matches", is "correct", or is "equivalent"; outputs are scanned for such words and any hits
are shown.

It also does not check the Lean (nothing was compiled; the repository states the main theorems build
with zero `sorry`), and it does not check whether the paper's own proofs are right.

## Sources

| | |
|---|---|
| Paper | *Finite time blowup for Navier–Stokes*, OpenAI, [PDF](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), 166 pages |
| Lean | [openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler) at commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, `NavierStokes/` only (816 files, 36,151 declarations); the Euler half is out of scope |
| Model | `nvidia/Qwen3.8-27B-NVFP4`, served locally with vLLM, reasoning ("thinking") enabled; every request and raw response is logged in `data/llm_raw.jsonl` |

## Pipeline

1. **Paper index** (`audit/paper_index.py`, `audit/ocr_attach.py`). All 80 numbered results and 362
   numbered equations, with page, section, statement and proof, from the PDF's text layer. Displayed
   math in the text layer is garbled, so every page was also OCR'd to LaTeX (Marker 1.8.4), and every
   OCR block was checked symbol by symbol against the PDF's own glyphs; 19 of 362 numbered equations
   carry a flag (mostly real OCR misreadings such as `j` read as `i`). Page images are in `data/pages/`.
2. **Lean index** (`audit/lean_index.py`). Every declaration with name, file, line range, docstring,
   statement, the section `variable`s in scope (these are hidden hypotheses), and the declarations it
   references. From the references: which declarations the two main theorems depend on. This
   "main proof path" is a lower bound: lemmas used implicitly by automation can be missed.
3. **Locating counterparts** (`audit/xref_llm.py`, `audit/xref_search.py`). For each paper result the
   model picks candidate files from the whole file catalogue, then reads every declaration in them
   (in chunks, nothing truncated) and names the ones that formalize the result. Routine helper lemmas
   (simp lemmas, private declarations, undocumented smoothness/arithmetic one-liners) are left out.
   A result counts as **found** when all 3 independent samples name the same declaration as its
   statement, with at least one shared term verified in both texts. Otherwise up to two more rounds
   run with the already-examined files removed and hint files suggested by the paper's structure
   (neighbouring results, citations in either direction, import links). Every round is recorded in
   tables `search_rounds` and `search_status`.
4. **Extraction** (`audit/extract.py`). For each (paper result, Lean declaration) pair, 3 independent
   samples return strict JSON: hypotheses and conclusions on each side, paper parts this declaration
   does not cover, typed differences, and a short proof summary per side. The Lean side is shown with
   real line numbers, the in-scope `variable`s, and the definitions its statement uses. Every field
   quotes its source; quotes are verified mechanically against the cited Lean lines and the paper text,
   and paper pages are attached from the index, not taken from the model.
5. **Proof steps** (`audit/proof_steps.py`). Statement-level extraction cannot see a difference that sits
   inside a proof. Every numbered equation in the proofs of selected results becomes its own target,
   "(n) in proof of <result>", described by the parent statement plus the surrounding proof text, and is
   located (same 3-of-3 bar, same retry rounds) and extracted exactly like a result. So far: the proofs of
   Lemma 8.2, Lemma 8.6 and Lemma 10.5 (8 equations; 7 located, 1 weak).
6. **Aggregation** (`audit/report.py`). The 3 samples are **grouped, never voted**: two differences of
   the same pair and type are treated as one when their cited Lean lines overlap. Each grouped difference
   keeps its agreement (1, 2 or 3 of 3) and every sample's wording.

Difference types, always comparing the paper with the Lean: `stronger-bound` (the paper states a
stronger estimate than the Lean proves), `missing-hypothesis` (the Lean assumes something the paper's
statement does not state), `different-norm`, `missing-supremum`, `different-domain`,
`extra-hypothesis` (the paper assumes something the Lean does not), `weaker-bound`, `other`. Tables are
sorted in that order, then by agreement.

## Checks on the method

- **Known discrepancy, found unprompted.** Bastounis, Circelli and Hansen ([arXiv:2610.08144](https://arxiv.org/abs/2610.08144))
  identified this mismatch. Lemma 8.6, eq. (8.19), states a loss of m+4 derivatives;
  the Lean theorem `SmoothFamilyTorusInverse.inverse_finiteJets` (on the main proof path) assumes
  `JetBound … (n + 5)`. No prompt mentions this lemma, derivative counts, or the discrepancy. All 3
  samples reported it as `stronger-bound`, citing line 868 and page 95, with both quotes verified.
- **Second known discrepancy, found unprompted, at proof level.** Eq. (10.19), inside the proof of
  Lemma 10.5, bounds the pressure flux by C_T R⁻¹[(B_R+1)B_R^{1/2} + R^{-3/4}B_R^{3/4}]. The Lean theorem
  `PressureFlux.exists_uniform_actual_pressure_flux_bound` (lines 587–589) has the same R^{-7/4}B^{3/4} term but
  a different first term, (B^{1/2}+1)(A/R + 1/R²), involving the dissipation quantity A. The proof-step
  target (10.19) was located to that theorem by all 3 samples in round 1, and all 3 extraction samples
  reported that the first part of the bound differs (lines 587–588, quotes verified). They typed it
  `other` rather than a bound type, because neither bound is simply stronger; see Known limitations.
- **Decoy test** (`audit/decoy_test.py`). Each of 21 sampled results was shown only declarations from
  an unrelated part of the formalization. In 17 of 21 the model reported no candidate at all; in 2 of
  21 all 3 samples agreed on a (necessarily wrong) declaration. On real candidates the same bar was met
  for 18 of 21. So a "found" is informative but roughly 1 in 10 may point at the wrong declaration.
  Caveat: 8 of the 21 decoy pools were the same small pool (204 declarations), smaller than typical.
- **Spot checks by a second model** (Claude). Proposition 8.3: the agreed declarations contain the
  paper's identity (8.13) nearly symbol for symbol. Lemma 10.3: the 2-of-3 candidate formalizes the
  same construction for the periodic problem rather than the whole-space one; it stayed "weak" after 3
  rounds, as it should.
- **Citations.** 99.8% of paper quotes and 99.6% of Lean quotes in reported differences were found at
  the cited location.

## Results so far

- Locating: 77 of 80 paper results found (68 in round 1, 7 in round 2, 2 in round 3); 3 weak matches
  (Proposition 4.2, Corollary 7.3, Lemma 10.3); none not found. See `out/paper_items_not_matched.csv`.
- Extraction: Section 8 (34 pairs), Lemma 10.5 (1 pair) and 8 proof steps of Lemmas 8.2, 8.6 and 10.5
  (23 pairs); 3 valid samples per pair; 717 grouped differences, 251 reported by all 3 samples.
- Review shortlist (`out/review_shortlist.md`): differences reported by all 3 samples whose type concerns
  what is estimated (bound, norm, uniformity), plus the two validation hits. It includes a lead beyond the
  published examples: eq. (8.10), inside the proof of Lemma 8.2, loses p+3 derivatives for ℒ^{-p}, while
  `SmoothFamilyTorusInverse.applyMultiplier_finiteJets` (line 851) needs one more; all 3 samples reported it,
  conditional on the Lean order `l` playing the role of the paper's `p`. For p = 1 this is the Lemma 8.6 gap.
  Not reviewed by a mathematician.

## Known limitations

- **Proof coverage is partial.** Proof-level targets are numbered equations only, and only in the proofs of
  Lemmas 8.2, 8.6 and 10.5 so far. Unnumbered displayed steps and other proofs are not yet targeted.
- **Bounds of a different shape are typed `other`.** When neither bound is simply stronger (as at (10.19)),
  the samples use `other`, which sorts last. A dedicated type for differently shaped bounds would surface
  these; until then the validation check, not the severity order, puts (10.19) on the shortlist.
- **Noise.** Many differences are naming (the paper's J_θ vs. Lean's `axialFlux`) or the Lean spelling
  out conditions the paper leaves implicit (smoothness, support, explicit parameters). These are reported
  by all 3 samples on nearly every pair. Severity order and agreement push them down, but they are not
  removed.
- **One paper result, several Lean declarations.** Results are often split across declarations; each
  pair lists the paper parts that declaration does not cover, and several paper results share
  declarations (e.g. Proposition 8.3 and Lemma 8.6). Read a result's pairs together.
- **Agreement is not independence.** The 3 samples come from the same model and prompt; agreement
  measures consistency, not correctness. The decoy test bounds how often consistency is wrong.
- **Paper references inside the Lean comments** use an earlier draft's numbering (e.g. "Proposition
  11.7"; the published paper has no Section 11), so they were not used as anchors.
- **OCR.** Displayed math comes from OCR; flagged blocks are marked in prompts, and page images are
  the reference for any doubt.
- **Lean theorems without a paper counterpart** (`out/lean_theorems_without_paper_counterpart.csv`) are
  listed for the Section 8 files only and are mostly supporting steps.

## Reproducing

```
python audit/paper_index.py && python audit/ocr_attach.py      # paper (OCR via .venv-ocr, Marker 1.8.4)
python audit/lean_index.py                                       # Lean
python audit/xref_llm.py files                                   # file candidates (all items)
python audit/xref_search.py --group all                          # multi-round locating
python audit/decoy_test.py
python audit/extract.py --section 8                              # Phase 3
python audit/extract.py --section 10 --items "Lemma 10.5"
python audit/proof_steps.py --items "Lemma 8.2,Lemma 8.6,Lemma 10.5"   # proof-level targets
python audit/extract.py --steps
python audit/report.py                                           # tables + out/report.html
```
The model endpoint is set with `AUDIT_LLM_BASE_URL`, `AUDIT_LLM_MODEL`, `AUDIT_LLM_MAX_CONCURRENCY`.
Responses are cached by (model, prompt, sample), so reruns reuse earlier samples rather than resampling.
