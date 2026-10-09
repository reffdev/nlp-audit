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

It also does not check the Lean (nothing was compiled; the repository provides Comparator challenge
files for independent checking of the two main theorems against a fixed statement and a permitted-axiom
list), and it does not check whether the paper's own proofs are right.

## Sources

| | |
|---|---|
| Paper | *Finite time blowup for Navier–Stokes*, OpenAI, [PDF](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), 166 pages |
| Lean | [openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler) at commit `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, `NavierStokes/` only (816 files, 36,151 declarations); the Euler half is out of scope |
| Model | `nvidia/Qwen3.8-27B-NVFP4`, served locally with vLLM, reasoning ("thinking") enabled; every request and raw response is logged in `data/llm_raw.jsonl` |

## How the targets were chosen

Section 8, the section that contains Lemma 8.6, was the pilot section. Lemma 8.6 and Lemma 10.5 were added as
anchors (`data/phase2_sample.json`) because Bastounis, Circelli and Hansen had published discrepancies in them,
and proof-level targets were run only inside the proofs of Lemmas 8.2, 8.6 and 10.5. The validation checks
below therefore test whether the model reports a known discrepancy when shown the material, not whether the
tool would have chosen to look there. A random sample of 12 further results (same file) was used for the
whole-paper locating estimate.

## Pipeline

All target-specific settings (the paper's URL and hash, the Lean repository and commit, the paper's running
heads and result numbering, the top-level theorems, the pilot plan and the validation targets) are in
`audit.toml`, read by `audit/config.py`. `audit/fetch.py` downloads the paper, checks its hash, fetches the
Lean repository at the pinned commit, and derives the text layer and page images.

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

- **Known discrepancy, reported without being named in any prompt.** Bastounis, Circelli and Hansen
  ([arXiv:2610.08144](https://arxiv.org/abs/2610.08144), Example 3.1) compare Lemma 8.6, eq. (8.19), which
  loses m+4 derivatives, with the Lean theorem `norm_derivativeWord_inverse_le`, which loses m+5; their
  Remark 3.2 notes the same m+5 in `inverse_finiteJets` and `mixedJet_inverse_bound`. Here, Lemma 8.6 was
  located to `SmoothFamilyTorusInverse.inverse_finiteJets` (on the main proof path), which assumes
  `JetBound … (n + 5)`; `norm_derivativeWord_inverse_le` was named by one sample as a proof step. No prompt
  mentions derivative counts or the discrepancy. All 3 samples reported it as `stronger-bound`, citing line
  868 and page 95, with both quotes verified. The theorem's own docstring says "five torus derivatives lost".
- **Second known discrepancy, at proof level.** Eq. (10.19), inside the proof of Lemma 10.5, bounds the
  pressure flux by C_T R⁻¹[(B_R+1)B_R^{1/2} + R^{-3/4}B_R^{3/4}]. The Lean theorem
  `PressureFlux.exists_uniform_actual_pressure_flux_bound` (statement at lines 585–589; Bastounis et al. cite
  the declaration's first line, 576) has the same R^{-7/4}B^{3/4} term but a different first term,
  (B^{1/2}+1)(A/R + 1/R²), involving the dissipation quantity A. The proof-step target (10.19) was located
  to that theorem by all 3 samples in round 1, and all 3 extraction samples reported that the first part of
  the bound differs (lines 587–588, quotes verified). They typed it `other` rather than a bound type,
  because neither bound is simply stronger; see Known limitations. An earlier version of the report merged
  this difference with neighbouring ones (the grouping rule treated adjacent lines as overlapping) and
  showed it under the wording of a trivial constant-naming difference; the rule now requires a shared line.
- **Decoy test** (`audit/decoy_test.py`). Each of 21 sampled results was shown only declarations from
  an unrelated part of the formalization. In 17 of 21 the model reported no candidate at all; in 2 of
  21 all 3 samples agreed on a (necessarily wrong) declaration. On real candidates the same bar was met
  for 18 of 21. So a "found" is informative but at least 1 in 10 may point at the wrong declaration.
  Caveats: 9 of the 21 decoy pools were the same small pool (204 declarations, the whole-space uniqueness
  files), smaller than typical; and decoy pools come from a different section with no shared files, so
  they are obviously unrelated. The test bounds blatant failures. It says nothing about the more likely
  failure, picking a neighbouring wrong declaration in the right file, so 1 in 10 is a lower bound.
- **Spot checks by a second model** (Claude). Proposition 8.3: the agreed declarations contain the
  paper's identity (8.13) nearly symbol for symbol. Lemma 10.3: the 2-of-3 candidate formalizes the
  same construction for the periodic problem rather than the whole-space one; it stayed "weak" after 3
  rounds, as it should.
- **Citations.** At the sample level, 2,784 of 2,788 paper quotes (99.9%) and 2,773 of 2,788 Lean quotes
  (99.5%) in reported differences were found at the cited location. After grouping, 1,011 of 1,014 grouped
  differences have every paper quote verified and 1,000 of 1,014 every Lean quote; the others are marked
  "not verified" in the tables.
- **Judgment-word scan.** 13 grouped differences contain a word from the forbidden list. 12 are the word
  "error" in the paper's own term "radial error" (Lemma 8.8); 1 is "equivalent", on the Lemma 8.6 pair with
  `TorusInverse.zero_mean_series_has_smooth_inverse`. All are shown in the report.

## Results so far

- Locating: 77 of 80 paper results found (68 in round 1, 7 in round 2, 2 in round 3); 3 weak matches
  (Proposition 4.2, Corollary 7.3, Lemma 10.3); none not found. The full map, including the 8 proof-step
  targets, is `out/paper_lean_map.csv`; the weak ones are also in `out/paper_items_not_matched.csv`.
- Extraction: Section 8 (34 pairs), Lemma 10.5 (1 pair) and 8 proof steps of Lemmas 8.2, 8.6 and 10.5
  (23 pairs); 3 valid samples per pair; 1,014 grouped differences, 322 reported by all 3 samples. 17 of the
  58 pairs are on the detected dependency path of the two main theorems (`on_main_proof_path` in
  `out/audit_table.csv`); for the other 41 the path was not detected, which does not mean they are unused.
- Review shortlist (`out/review_shortlist.md`). Part A: differences reported by all 3 samples of type
  stronger-bound, weaker-bound or missing-supremum, plus the two validation hits (8 entries). Part B:
  different-norm differences reported by all 3 samples (13 entries), most of which are the Lean encoding a
  norm or function class under another name. Part A opens with eq. (8.10), inside the proof of Lemma 8.2,
  which loses p+3 derivatives for ℒ^{-p}, while `SmoothFamilyTorusInverse.applyMultiplier_finiteJets`
  (line 851) needs l+4 for a multiplier of order l; all 3 samples reported it, conditional on `l` playing the
  role of `p`. A manual reading of this entry follows.

### Manual follow-up of the (8.10) entry

This section is a reading of the paper and the Lean source by the author with an AI assistant (Claude),
done after the run. It is not pipeline output, nothing was compiled, and it has not been reviewed by a
mathematician. An earlier draft of this file said the (8.10) entry was the Lemma 8.6 discrepancy "traced one
lemma upstream". That holds on the Lean side only.

- **Lean side: one cause.** `inverse_finiteJets` (the Lemma 8.6 match, line 868) is proved by applying
  `applyMultiplier_finiteJets` with l = 1 (line 869). That lemma requires n + l + 4 derivatives, so Lemma 8.6
  gets n + 5. In this repository the general lemma is used only with l = 0 (`nonbarPart_finiteJets`, line 1024) and
  l = 1; no instance corresponding to (8.10) with p ≥ 2 was found among the uses of these two lemmas.
- **Paper side: two separate derivations.** The proof of Lemma 8.6 (p. 96) obtains its m + 4 directly from the
  divisor bound (6.7) for v_t: one power of |k| from the divisor, three more for a summable lattice sum. It
  does not use (8.10). Its one citation of Lemma 8.2 concerns slow derivatives of the cutoff term, not the
  torus derivative count. (8.10) (p. 91) is derived separately for ℒ = v_r·∂_y with the same counting.
- **The match is the right counterpart but a more general statement.** Beyond the +3/+4,
  `applyMultiplier_finiteJets` takes any multiplier with |m(k)| ≤ B·weight(k)^l, weight(k) = 1+|k₁|+|k₂|,
  not only ℒ^{-p}; it bounds joint parameter-and-torus derivatives uniformly over a parameter set, where
  (8.10) bounds torus derivatives (the paper treats the others in a separate sentence); and it has no
  zero-mean hypothesis, because the multiplier is defined to vanish at k = 0. The extra derivative is
  visible in the code: the Lean coefficient bound (`coefficient_moment_bound`, line 689) sums against
  Σ weight(k)^{-4}, where the paper sums against Σ(1+|k|)^{-3}. Whether ^{-3} would suffice in the Lean's
  setting is a question for a mathematician.
- **The located match was a different declaration.** For (8.10), all 3 locating samples named
  `ParametricTorusInverse.mixedJet_inverse_bound`, which is not on the detected main proof path;
  `applyMultiplier_finiteJets` was named by 2 of 3. Both were extracted. See "Matching is by resemblance"
  under Known limitations.
- **Not yet confirmed by Lean.** The dependency above was read in the source (the call is the first line of
  the proof). Confirmation from Lean's elaborated environment needs a build and was not done.

## Known limitations

The first two are the main weaknesses of this version; a fix is sketched under Planned fixes.

- **Matching is by resemblance.** A Lean declaration is located for a paper result because its statement
  looks like the paper's, never because it plays the same role in the proof. Nothing checks that the matched
  declaration is used where the paper uses the result. The (8.10) entry shows the cost: the 3-of-3 match,
  `mixedJet_inverse_bound`, is not on the detected main proof path, while the declaration the Lean proof
  actually uses was matched by only 2 of 3 samples. The decoy test measures blatant mismatches only, not
  resemblance to a neighbouring, wrong declaration.
- **There is no paper-side dependency graph.** Citations inside the paper's proofs are indexed
  (`paper_refs`), but no graph of which result uses which is built or compared with the Lean's. Differences
  in the route of a proof are therefore invisible to the tool: that the Lean derives Lemma 8.6 from a
  general lemma the paper's proof of Lemma 8.6 does not use was found only by the manual reading above.
- **The Lean index is parsed from source.** Statements, hidden `variable`s and references come from
  parsing the `.lean` files, not from Lean's elaborated environment; the dependency graph is a lower bound.
  A spot check of the parsed statements against Lean's elaborated ones needs a build and has not been done,
  so the parser's error rate is unknown. It is a possible contributor to the locating errors the decoy test
  measures.
- **Proof coverage is partial.** Proof-level targets are numbered equations only, and only in the proofs of
  Lemmas 8.2, 8.6 and 10.5 so far. Unnumbered displayed steps and other proofs are not yet targeted.
- **Bounds of a different shape are typed `other`.** When neither bound is simply stronger (as at (10.19)),
  the samples use `other`, which sorts last. A dedicated type for differently shaped bounds would surface
  these; until then the validation check, not the severity order, puts (10.19) in Part A of the shortlist.
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

## Planned fixes

A second version would match on structure as well as resemblance:

1. **Lean index from Lean itself.** Build the formalization once and read each declaration's elaborated
   statement and the constants its proof uses from the Lean environment, replacing the source parser. This
   gives an exact dependency graph and removes parser errors as a source of mismatches.
2. **Paper dependency graph.** For each proof, the results and equations it uses: the explicit citations
   already indexed, plus uses the model extracts with quotes, under the same 3-sample, no-voting rule.
3. **Structure-aware locating.** Score a candidate declaration also by whether its Lean dependencies
   correspond to the paper dependencies of the result it is matched to, given the matches already made, and
   prefer declarations the main theorems actually use. Report an edge present on one side only as its own
   difference type (a different proof route), with both sides cited.
4. **Output as a blueprint.** The natural product is a machine-inferred blueprint of the formalization (each
   paper result linked to its Lean declarations, with dependency edges on both sides) in a form humans can
   correct, rather than a table alone.

## Reproducing

```
python audit/fetch.py                                            # paper PDF (hash-checked), Lean repo at the commit
python audit/fetch.py --ocr                                      # in the OCR environment (Marker 1.8.4)
python audit/paper_index.py && python audit/ocr_attach.py      # paper
python audit/lean_index.py && python audit/xref_cheap.py         # Lean index, reachability, cheap candidates
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
The locating and extraction stages accept `--items "Lemma 10.5"` to run on a few results first.
Responses are cached by (model, prompt, sample), so reruns reuse earlier samples rather than resampling.
