# How the audit works

## What it does and doesn't tell you

The tool looks for places where the paper and the Lean formalization say different things. For each result in the paper it finds the Lean declarations that formalize it, writes down what each side assumes and concludes, and lists the differences, each quoted word for word from both sources.

It doesn't decide whether a difference matters. Some are harmless: the same thing said another way, or a hypothesis the paper leaves implicit. Others might mean the paper claims something the Lean doesn't prove. That call belongs to a mathematician. The model is never asked whether anything "matches", is "correct" or is "equivalent". The text of each difference it reports (its description of each side and of the difference) is scanned for words like those, and any hits are shown in the report. Quotes, proof summaries and the model's reasoning aren't scanned.

It also doesn't check the Lean itself. Nothing was compiled; the Lean repo has its own Comparator challenges for checking the two main theorems against fixed statements and a list of allowed axioms. And it doesn't check whether the paper's proofs are right.

## Sources

| | |
|---|---|
| Paper | *Finite time blowup for Navier–Stokes*, OpenAI, [PDF](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf), 166 pages |
| Lean | [openai/NavierStokesAndEuler](https://github.com/openai/NavierStokesAndEuler) at `f9e8bc5b38b6e212696e8a30e3e91517af887bbd`, `NavierStokes/` only (816 files, 36,151 declarations). The Euler half is out of scope. |
| Model | `nvidia/Qwen3.8-27B-NVFP4` on vLLM, run locally with reasoning on. Every response, with its reasoning, is logged in `data/llm_raw.jsonl`, keyed by a hash of its prompt and settings; v0.2 also logs full prompt text in `data/llm_prompts.jsonl`. Both are attached to the v0.2 release. |

## How the targets were chosen

Section 8 was the pilot because it contains Lemma 8.6. Lemmas 8.6 and 10.5 were added to the list (`data/phase2_sample.json`) because Bastounis, Circelli and Hansen had already published discrepancies in them, and the proof-level targets only cover the proofs of Lemmas 8.2, 8.6 and 10.5. So the validation checks below show that the model reports a known discrepancy when it's shown the right material. They don't show that the tool would have found the right place to look on its own. For the whole-paper locating estimate I also drew a random sample of 12 other results (same file).

## Pipeline

Everything specific to this paper and this Lean repo is in `audit.toml`, read by `audit/config.py`. `audit/fetch.py` downloads the paper and checks its hash, fetches the Lean repo at the pinned commit, and produces the text layer and page images.

1. **Paper index** (`paper_index.py`, `ocr_attach.py`). All 80 numbered results and 362 numbered equations, with page, section, statement and proof, taken from the PDF's text layer. The text layer mangles displayed math, so every page was also run through OCR to LaTeX (Marker 1.8.4), and each OCR block was compared symbol by symbol with the PDF's own glyphs. 19 of the 362 numbered equations got flagged, mostly for genuine OCR misreads like `j` read as `i`. Page images are in `data/pages/`.
2. **Lean index** (`lean_index.py`). Every declaration, with its name, file, lines, docstring, statement, the section `variable`s in scope, and the declarations it refers to. Under Lean 4's rule a section variable becomes a hypothesis of a theorem only if the theorem's statement refers to it or an `include` brings it in, and `omit` removes one. The index can't apply that rule without elaborating, so the hypothesis lists the model extracts are source-derived and may include variables Lean would not include. The references give the set of declarations the two main theorems depend on. This "main proof path" is an approximation in both directions: lemmas that automation uses behind the scenes can be missed, and a name resolved to the wrong declaration can add a link that isn't really there.
3. **Finding counterparts** (`xref_llm.py`, `xref_search.py`). For each paper result, the model picks candidate files from a catalog of all 816 files, then reads every declaration in them (in chunks; nothing is cut off) and names the ones that formalize the result. Routine helpers (simp lemmas, private declarations, undocumented one-line smoothness or arithmetic facts) are skipped. A result counts as found when all 3 samples name the same declaration as its statement and share at least one term that appears in both texts. If not, up to two more rounds run, with the files already read taken out and hints added from the paper's structure: neighbouring results, citations in either direction, and import links. Every round is recorded (`search_rounds`, `search_status`).
4. **Extraction** (`extract.py`). For each (paper result, Lean declaration) pair, 3 independent samples return strict JSON: hypotheses and conclusions on each side, the parts of the paper result this declaration doesn't cover, typed differences, and a short summary of each proof. The model sees the paper statement and proof (from the OCR'd LaTeX when it is complete, otherwise from the PDF text layer), built once per comparison as an immutable context object (`paper_text.Context`) that quote verification also uses, so quotes are checked against exactly what the model was shown. It also sees the Lean with real line numbers, the `variable`s in scope, and the definitions the statement uses. Every field except the proof summaries has to quote its source; the proof summaries carry no citation and are unverified. Code then checks each quote. A Lean quote must appear at the cited lines of the Lean text the model was shown, which includes definitions in other files; the report links each quote to the file where it was actually found. A paper quote is checked twice, against the text of the cited page (the headline figure) and against the context the model was shown, and gets one of three statuses: exact, normalized (after keeping LaTeX commands as the symbols they stand for, so `\le` and `\ge` differ, and keeping brace grouping, so `x^{n+1}` and `x^n+1` differ), or unresolved-OCR. Paper quotes of 3 characters or fewer are marked "too short to verify". Page numbers come from the index, not from the model.
5. **Proof steps** (`proof_steps.py`). Comparing statements can't catch a difference that sits inside a proof. So each numbered equation in a chosen proof becomes a target of its own, `(n) in proof of <result>`, described by the parent statement and the surrounding proof text. It's located and extracted like any other result, with the same 3-of-3 bar and retry rounds. So far this covers the proofs of Lemmas 8.2, 8.6 and 10.5: 8 equations, 7 located and 1 weak.
6. **Putting the samples together** (`report.py`). The 3 samples are grouped, never voted on. A group holds at most one difference from each sample, all on the same pair and of the same type, and every two of them must cite at least one Lean line in common in the same file (a quote can come from a definition in another file with the same line numbers); groups don't chain. The number of samples in a group is its `overlapping_citations` (1 to 3).
7. **Adjudication** (`adjudicate.py`). Overlapping citations don't show that two samples are describing the same thing. For every group with 2 or more samples, 3 further samples see only the group's descriptions and answer whether they assert the same difference. Nothing is voted: the count of "yes" answers is kept (`adjudicated_same`), and a group's `agreement` is reported only where all 3 said yes. Single-sample groups have agreement 1.

Difference types (always reading from the paper towards the Lean):

- `stronger-bound`: the paper states a stronger estimate than the Lean proves
- `missing-hypothesis`: the Lean assumes something the paper's statement doesn't
- `different-norm`, `missing-supremum`, `different-domain`
- `extra-hypothesis`: the paper assumes something the Lean doesn't
- `weaker-bound`, `other`

Tables are sorted in that order, then by agreement.

## Checks

**Retrospective recovery of two published discrepancies.** The two targets were put on the list because Bastounis, Circelli and Hansen had published them, so this checks recovery when the tool is pointed at them, not discovery. Each is defined in `audit.toml` as a place, not a wording: the Lean declaration, the lines of the expression the discrepancy is about (read from the Lean source, not from the model's answers), and the difference types that count. A sample hits the target if it reported a difference of one of those types whose Lean quote is found at those lines of the declaration's own file; an unplaceable quote is not a hit. Hits are counted per sample, so the result doesn't depend on grouping. As a control, the same check (same types, a window of the same number of lines) is run along the statement of every other pair compared; the number of pairs where it fires, and the share of windows, are reported next to the result. The code is `audit/validation.py`. An earlier version matched the samples' wording against hand-written patterns; one of those had to be widened after a change to the grouping, which is why it was replaced.

**Lemma 8.6.** Bastounis, Circelli and Hansen ([arXiv:2610.08144](https://arxiv.org/abs/2610.08144), Example 3.1) compare Lemma 8.6, eq. (8.19), which loses m+4 derivatives, with the Lean theorem `norm_derivativeWord_inverse_le`, which loses m+5. Their Remark 3.2 points out the same m+5 in `inverse_finiteJets` and `mixedJet_inverse_bound`, and traces it to the series that comes from `coefficient_seminorm_bound`. Here, Lemma 8.6 was matched to `SmoothFamilyTorusInverse.inverse_finiteJets` (among others), which is on the main proof path and assumes `JetBound … (n + 5)`. No prompt says anything about derivative counts or the discrepancy. In v0.2, all 3 samples reported it as `stronger-bound` at line 868, and the same check fires on 0 of the other 66 pairs (0 of 606 windows). In v0.1 it was also 3 of 3 (control: 2 of 57 pairs). The theorem's own docstring says "five torus derivatives lost".

**Eq. (10.19).** Inside the proof of Lemma 10.5, (10.19) bounds the pressure flux by C_T R⁻¹[(B_R+1)B_R^{1/2} + R^{-3/4}B_R^{3/4}]. The Lean theorem `PressureFlux.exists_uniform_actual_pressure_flux_bound` (statement at lines 585–589; Bastounis et al. cite the first line of the declaration, 576) has the same R^{-7/4}B^{3/4} term but a different first term, (B^{1/2}+1)(A/R + 1/R²), which involves the dissipation quantity A. In both runs all 3 samples matched (10.19) to that theorem in the first round. In v0.2 the location-and-type check (lines 587–588, the first term of the Lean bound; types `stronger-bound`, `weaker-bound` or `other`) counts 3 of 3 samples, but the same check fires on 60 of the other 66 pairs (37.5% of windows), because `other` also covers notation and naming differences. Under adjudication it is not confirmed: the grouped difference "the first part of the bound differs" has citations from 2 samples, confirmed by 2 of 3 adjudication samples. Reading the three samples, the third described a different observation: it reported the extra 1/R² summand inside the first factor as a `stronger-bound` difference at line 588, and the change from B_R to `cutoffL6`/`dissipationRoot` as a separate `different-norm` difference at line 587, but did not say that the first term's form differs (the other two samples also list the 1/R² summand as a separate observation). A dedicated type for differently shaped bounds might change this (see Known limitations). In v0.1 the prompt for this step lacked the surrounding proof text (see CHANGES-v0.2.md).

**Decoy test** (`decoy_test.py`). It measures how often a confident match is accepted when the pool contains only deliberately unrelated declarations. 21 sampled results were each shown declarations from an unrelated part of the formalization, with the same prompt and 3 samples, first chunk only and no retry rounds. In v0.2, 18 of the 21 got no candidate at all, 0 of 21 received a confident (3 of 3) false match, and 1 a weak (2 of 3) one; in v0.1 2 of 21 received a confident false match. 21 items is too few to distinguish these. The test is easier and narrower than the real search: the decoys come from a different section with no files in common (9 of the 21 share one small pool of 204 declarations), so it says nothing about the likelier failure of picking a neighbouring, wrong declaration in the right file. For comparison, 18 of these 21 results got a 3-of-3 match in the first round of the real search, in both runs.

**Spot checks by a second model** (Claude). For Proposition 8.3, the agreed declarations contain the paper's identity (8.13) almost symbol for symbol. For Lemma 10.3, the 2-of-3 candidate formalizes the same construction for the periodic problem instead of the whole-space one, and it stayed "weak" after 3 rounds, which is the right outcome.

**Quotes.** Across all samples in v0.2, 2,430 of the 3,050 paper quotes in reported differences are found on the page their citation points to (2,330 exact, 100 normalized, 620 unresolved-OCR), and 3,040 in the text the model was shown (2,905 exact, 135 normalized, 10 unresolved-OCR); 613 pass in that text but fail on the cited page. 44 quotes are 3 characters or fewer. 3,031 of 3,050 Lean quotes were found at the cited lines, 225 of them in a definition from another file rather than the declaration itself; the report links to that file. After grouping, 1,286 of the 1,712 differences have a paper quote found on the cited page, 21 one too short to verify, and 405 one not found there; 1,702 have one found in the text the model was shown. These figures come from re-scoring the stored outputs after the fixes described in CHANGES-v0.2.md (`rescore.py`), which changed the status of 4 difference quotes.

**Judgment words.** The scan covers the text of each reported difference (its description of each side and of the difference), not quotes, proof summaries or the model's reasoning. In v0.2, 13 grouped differences contain a word from the list: 12 are "error" used as a mathematical term (Proposition 8.1 and Lemma 8.8), and 1 is "matches", on a (10.15) pair, where a sample wrote that the Lean's tensor "matches the paper's g" after swapping the velocity variables. All are shown in the report.

## Static checks on the Lean source

These come from `audit/static_checks.py`. They read the source files and the index; nothing is compiled or elaborated, so they can only see what's written in the files.

**Sorry, axioms and other escape hatches.** I counted `axiom`, `sorry`, `admit`, `native_decide` and `unsafe`, plus `opaque`, `implemented_by`, `extern` and `debug.skipKernelTC`, in every `.lean` file in the repo, ignoring comments and strings. Every count is zero in all 816 files under `NavierStokes/` and all 1,839 under `Euler/`. The only hits in the whole repo are 4 `sorry`s in `ComparatorChallenges/NavierStokes.lean` and `ComparatorChallenges/Euler.lean`, which are the challenge statements' intended placeholders (the file says so). No file imports anything other than Mathlib and the repo's own modules. Per-file counts are in `out/source_scan.csv` and in the `file_axiom_sorry_admit_native_decide_unsafe` column of the two main tables; the import list, which is empty, is `out/external_imports.csv`. This is consistent with what the repo states (`formalization.yaml` reports no `sorry` and only `propext`, `Classical.choice` and `Quot.sound` for the main theorems, the same three the Comparator config allows), but it's a weaker check. A text scan can't see an axiom that reaches the proof through Mathlib or through a tactic. Only Lean (`#print axioms`, or running Comparator) can confirm that, and I haven't run either.

**Duplicate statements.** Of the 27,269 theorems under `NavierStokes/`, 474 declarations fall into 187 normalized-statement clusters (287 beyond one representative each): their statements are the same once you ignore the theorem's name, the names of bound variables, universe levels and whitespace, and write every repo name out in full. The normalization also ignores section hypotheses, so two members of a cluster can differ in the `variable`s they depend on. The largest clusters are trivial inequalities. 183 groups are exact matches and 4 differ only in spacing or brackets. A fuzzy match turned up 278 more pairs, but almost all of them were siblings rather than copies (an `add` lemma next to a `sub` lemma, `n + 4` next to `n + 5`), so they're left out. 57 of the 474 copies aren't referenced anywhere else in the repo, and in 21 groups no copy is referenced at all. In 33 groups more than one copy is on the main proof path, in 63 exactly one is, and in 91 none is. Nearly all groups (183) span more than one file:

| Group | Copies | Unreferenced | On main path | Statement (first copy) |
|---|---|---|---|---|
| 1 | 83 | 7 | 34 | `nat_le_infty`: (n : ℕ) : (n : WithTop ℕ∞) ≤ ∞ |
| 2 | 10 | 0 | 4 | `infty_add_one_le`: (∞ : WithTop ℕ∞) + 1 ≤ ∞ |
| 3 | 3 | 0 | 1 | `ActivationCone.radialPartial_eq_partialY` |
| 4 | 3 (spacing) | 0 | 2 | `ActivationHolomorphic.scale_symmetric_interval` |
| 5 | 3 | 0 | 1 | `ActiveAnnulusWeight.iteratedDeriv_zero_function` |
| 6 | 3 | 0 | 3 | `ActualInitialization.smooth_conjugatePair` |
| 7 | 3 | 0 | 3 | `BaseChartJets.iteratedFDeriv_pair` |
| 8 | 3 | 0 | 3 | `CurrentPhysicalModeGerms.liftXY_common` |
| 9 | 3 | 0 | 3 | `DirectAngularDiagonal.divergence_congr` |
| 10 | 3 | 0 | 0 | `FlatCovariance.sqrt_edge` |

Every group, with file and line for each copy and what references it, is in `out/duplicate_statements.csv`. "Referenced" means another declaration names it in the source; a lemma used only through `simp` or other automation would be missed, though none of the unreferenced copies is tagged `@[simp]`.

**Definitional depth.** For each theorem, the longest chain of the repo's own definitions (`def`, `abbrev`, `structure`, `inductive`) you have to unfold, starting from the names in its statement, before everything is Mathlib. For a definition matched to a paper result the chain starts at the definition itself. For the 77 located results the depth runs from 0 to 55, with a median of 9; across all theorems under `NavierStokes/` the median is 5. 17 of the 77 are 20 or deeper, led by Proposition 9.6 (55, `ActualCycleCoherence.step`), Proposition 9.5 (53, `ActualInitialization.initial_invariant`) and Proposition 7.5 (30, `PrimaryTargetBounds.exists_actual_bounds`). It is the longest definition chain to Mathlib in the source-resolved graph; it makes no claim about review effort or drift. It's in the `def_depth` and `def_chain` columns of `out/paper_lean_map.csv` and `out/audit_table.csv`. Names are resolved from the source the same way as for the Lean index, and section `variable`s aren't followed.

**Statements the Lean index cut short.** Rereading full statements for these checks showed that the Lean index (`lean_index.py`) cut 923 of the 27,269 theorem statements (3.4%) short: 711 at a line starting with `|`, which it takes for a match arm but is an absolute value, and 212 at the `:=` of a `let` inside the statement. The locating step only ever shows the model the first 350 characters of a statement, so what matters is the 726 (2.7%) cut inside those 350 characters. Across all locating rounds, 3.3% of the theorem entries the model read had a shortened statement (its name and docstring were still there). 85 of the 88 targets had at least one in their files. Among the declarations all samples agreed on, 9 in 6 targets are affected (Lemma 7.1, Proposition 9.5, Lemma A.6, Proposition A.7, Lemma B.7, Remark B.9), and they were found anyway. What can't be measured without a rerun is the other direction: a true counterpart that was missed or got only 2 of 3 votes because its statement was cut. The 4 weak targets had 5 to 102 such entries in their files. Extraction shows the Lean source lines directly, so it saw every statement in full. The one effect there: the "definitions used in the statement" context left out definitions that appear only in the cut-off part, for 2 of the 58 v0.1 pairs. These are the (10.19) pair, which lost `dissipationRoot` and `cutoffL6`, and one Lemma 8.6 pair (`commonTemporalFields_represents`), which lost 4. All 3 samples still reported the (10.19) difference. The static checks use the full statements. The index itself is left as it was; v0.2 uses the same index so that the two runs stay comparable.

## Results so far

**Locating.** 77 of 80 results found, in both runs: 68 in the first round, 7 in the second, 2 in the third. 3 are weak (Proposition 7.2, Lemma 10.2, Lemma 10.3; in v0.1 Proposition 4.2, Corollary 7.3, Lemma 10.3) and none came up empty. All 8 proof steps were found. The matches themselves moved between runs: see Known limitations and CHANGES-v0.2.md. The full map is in `out/paper_lean_map.csv`; the weak ones are also listed in `out/paper_items_not_matched.csv`.

**Extraction.** Section 8 and Lemma 10.5 (43 pairs for 9 results) and the 8 proof steps of Lemmas 8.2, 8.6 and 10.5 (24 pairs), with 3 valid samples per pair. That gives 1,712 grouped differences: 442 with overlapping citations from all 3 samples, of which 206 were confirmed by all 3 adjudication samples as describing the same difference; 268 confirmed at 2 samples, 816 single-sample, and 422 groups whose citations overlap but were not confirmed (4 of them not adjudicated, see CHANGES-v0.2.md). 40 of the 67 pairs use a declaration all 3 samples named when matching and 27 one that 2 named (`located_by` in `out/audit_table.csv`). A paper result can have several declarations that all 3 samples named, so `located_by` is about the pair's own declaration, not about whether it's the single "found" declaration in the map. 22 of the 67 pairs are on the detected path to the two main theorems (`on_main_proof_path`); for the other 45 no path was found, which doesn't mean they're unused.

**Shortlist** (`out/review_shortlist.md`). Selected by a fixed rule; no mathematician has reviewed it, and its entries are textual differences, not established mathematical ones. Part A has the confirmed 3-of-3 differences of type stronger-bound, weaker-bound or missing-supremum, plus the confirmed 3-of-3 differences at the two validation targets (3 entries). Part B has the confirmed 3-of-3 different-norm differences (14 entries). Each entry carries a heuristic `likely_explanation` label assigned by fixed rules; 9 of the 17 are labelled as probable formalization conventions (7 naming, 2 parameter-set uniformity). The label doesn't affect selection or order. Part C lists the 123 confirmed 3-of-3 differences of type missing-hypothesis or different-domain, the categories Parts A and B leave out, so the exclusion is visible. Two model descriptions in the (8.10) pairs say the paper only uses a finite derivative norm; the paper's lemma assumes a smooth coefficient, so the shortlist and summary show an editorial note next to them (configured in `audit.toml`; the model's text is unchanged).

### (8.10), followed up by hand

This section is mostly a reading of the paper and the Lean source, done by hand after the v0.1 run with Claude; nothing was compiled, and no mathematician has checked it. What the tool contributed: in v0.1 it produced `applyMultiplier_finiteJets` as a 2-of-3 candidate for (8.10), with the p+3 vs l+4 difference reported by all 3 samples; v0.2 reproduced the candidate at 2 of 3 and the difference at 1 of 3. The dependency link and the exponent attribution below came from reading the source, and the adversarial review of v0.1 confirmed them.

In the Lean, both differences have one cause. `inverse_finiteJets` (the Lemma 8.6 match, line 868) is proved by applying `applyMultiplier_finiteJets` with l = 1 (line 869). That lemma assumes n + l + 4 derivatives, so Lemma 8.6 ends up assuming n + 5. In this repo the general lemma is only used with l = 0 (`nonbarPart_finiteJets`, line 1024) and l = 1; looking at where these two lemmas are used, I found nothing that corresponds to (8.10) with p ≥ 2.

The paper derives the two displayed derivative estimates separately: (8.19) from (6.7), in the proof of Lemma 8.6 (p. 96), and (8.10) within the proof of Lemma 8.2 (p. 91). It does not cite (8.10) in the proof of Lemma 8.6; its one citation of Lemma 8.2 there concerns slow derivatives of the cutoff term. Both estimates use the same Diophantine and Fourier-summability mechanism: one power of |k| per inverted derivative, plus three more for a summable lattice sum.

`applyMultiplier_finiteJets` is the right counterpart to (8.10), but it's a more general statement, and it differs in more than the +3/+4:

- It takes any multiplier with |m(k)| ≤ B·weight(k)^l, where weight(k) = 1+|k₁|+|k₂|, not just ℒ^{-p}.
- It bounds all joint derivatives in the parameters and the torus together, uniformly over a parameter set. (8.10) bounds torus derivatives, and the paper handles the rest in a separate sentence.
- It accepts any polynomially bounded multiplier and has no zero-mode condition.

Bastounis, Circelli and Hansen's Remark 3.2 already traces the extra derivative to the series that comes from `coefficient_seminorm_bound`, contrasting the paper's Σ(1+|k|)^{-3} with the Lean's Σ weight(k)^{-4}; in this repo that series enters through `coefficient_moment_bound` (line 689). What is added here is only the link to the (8.10) candidate through the l = 1 specialization. Σ over ℤ² of (1+|k|)^{-3} converges, so summability is not the open question; the work nobody has done is a checked sharper coefficient estimate, propagated through the Lean lemmas.

The tool's own top match for (8.10) was a different declaration. All 3 locating samples named `ParametricTorusInverse.mixedJet_inverse_bound`, which isn't on the detected main proof path; `applyMultiplier_finiteJets` got 2 of 3. Both pairs were extracted. This is the clearest example of the first weakness below.

The dependency was read off the source (the call is the first line of the proof). Confirming it from Lean's own environment needs a build, which I haven't done.

## Known limitations

The first two are the main weaknesses of this version. There's a sketch of a fix under Planned fixes.

**Matches are made on resemblance.** A Lean declaration is matched to a paper result because its statement looks like the paper's, never because it plays the same role in the proof. Nothing checks that the matched declaration is used where the paper uses the result. (8.10) shows what that costs: the 3-of-3 match, `mixedJet_inverse_bound`, isn't on the detected main proof path, while the declaration the Lean proof actually uses got only 2 of 3. The decoy test doesn't help here, since it only measures blatant mismatches.

**There's no dependency graph on the paper side.** The citations inside the paper's proofs are indexed (`paper_refs`), but nothing builds a graph of which result uses which, or compares it with the Lean's. So the tool can't see when the two take different routes. That the Lean derives Lemma 8.6 from a general lemma the paper's proof doesn't use only came out of the reading above.

**The Lean index is parsed from source.** Statements, hidden `variable`s and references come from parsing the `.lean` files, not from Lean's elaborated environment, and the dependency graph is approximate. Two known errors: 3.4% of theorem statements were cut short (see Static checks), and 9 theorems in `PositiveAxisSystem.lean` are indented by one space, so the index, which only reads declarations starting at the left margin, misses them entirely. Checking the parsed statements against Lean's needs a build and hasn't been done, so other errors may exist. Parser mistakes may account for some of the locating errors the decoy test picks up.

**The static checks are static: source-level, no elaboration.** The sorry/axiom scan, the duplicate scan and definitional depth all work on the text of the files and the source index. They can't see what Lean adds when it elaborates (axioms pulled in through Mathlib or tactics, implicit arguments, instances, uses through automation), and names are resolved by the same rules as the index.

**Only part of the proofs are covered.** Proof-level targets are numbered equations only, and only in the proofs of Lemmas 8.2, 8.6 and 10.5 so far. Unnumbered steps and other proofs aren't targeted yet.

**Bounds of a different shape end up as `other`.** When neither bound is simply stronger, as at (10.19), the samples choose `other`, which sorts last. A type for differently shaped bounds would bring these up. For now (10.19) is in Part A of the shortlist because it's a validation target, not because of how it was typed.

**Noise.** Lots of differences are just naming (the paper's J_θ vs. the Lean's `axialFlux`), or the Lean spelling out conditions the paper leaves implicit (smoothness, support, explicit parameters). All 3 samples report these on nearly every pair. Sorting by type and agreement pushes them down, but they're still there.

**One result, several declarations.** A paper result is often split across several Lean declarations, and several results can share a declaration (Proposition 8.3 and Lemma 8.6, for example). Each pair lists the parts of the paper result that its declaration doesn't cover, so read a result's pairs together.

**Matches aren't stable between runs.** Between v0.1 and v0.2, 59 of the 88 targets changed their top declaration or their set of agreed declarations. In 12 the top declaration stayed, in 13 the old top is still among the new agreed declarations, in 14 the agreed sets overlap, and in 20 they share nothing. By distance between the two tops: 0 within a duplicate-statement cluster, 6 within the same file, 39 within the same folder (which separates little, since 35,014 of the 36,151 declarations are in `NavierStokes/`), and 2 in a different folder. Some of this comes from the changed prompts and some from sampling. Prompts also changed between the runs, so this is sensitivity to changed inputs, not a measurement of sampling noise. That measurement is deferred to v2.

**Overlapping citations are the same observation only about half the time.** Of the 442 groups where all 3 samples cite overlapping Lean lines, 206 were confirmed by adjudication. Across the 896 adjudicated groups with 2 or more samples, all 3 adjudication samples said "same" for 474, and none did for 371.

**Agreement isn't independence.** The 3 samples come from the same model and the same prompt, so agreement, even adjudicated, measures consistency, not correctness. The adjudication samples are the same model again.

**The paper references in the Lean comments** use an older draft's numbering (e.g. "Proposition 11.7", but the published paper has no Section 11), so they weren't used as anchors.

**OCR.** Displayed math comes from OCR. Flagged blocks are marked in the prompts; when in doubt, the page images are the reference.

**Lean theorems without a paper counterpart** (`out/lean_theorems_without_paper_counterpart.csv`) are only listed for the Section 8 files, and most of them are supporting steps.

## Planned fixes

A second version would match on structure, not just resemblance:

1. **Build the Lean index from Lean.** Compile the formalization once and read each declaration's elaborated statement, and the constants its proof uses, straight from the Lean environment instead of parsing source. That gives an exact dependency graph and takes parser errors out of the picture.
2. **Build a dependency graph for the paper.** For each proof, the results and equations it uses: the citations already indexed, plus uses the model extracts with quotes, under the same rule of 3 samples and no voting.
3. **Use structure when matching.** Score a candidate declaration partly on whether its Lean dependencies line up with the paper dependencies of the result it's being matched to, given the matches already made, and prefer declarations the main theorems actually use. When a dependency shows up on one side only, report it as its own type of difference (a different proof route), citing both sides.
4. **Output a blueprint.** The natural end product is a machine-inferred blueprint of the formalization, with each paper result linked to its Lean declarations and dependency edges on both sides, in a form people can correct. A table alone isn't enough.

## Reproducing

```
python audit/fetch.py                                            # paper PDF (hash-checked), Lean repo at the commit
python audit/fetch.py --ocr                                      # in the OCR environment (Marker 1.8.4)
python audit/paper_index.py && python audit/ocr_attach.py && python audit/paper_text.py   # paper
python audit/lean_index.py && python audit/xref_cheap.py         # Lean index, reachability, cheap candidates
python audit/xref_llm.py files                                   # candidate files (all items)
python audit/xref_search.py --group all                          # locating, multiple rounds
python audit/decoy_test.py
python audit/extract.py --section 8
python audit/extract.py --section 10 --items "Lemma 10.5"
python audit/proof_steps.py --items "Lemma 8.2,Lemma 8.6,Lemma 10.5"   # proof-level targets
python audit/extract.py --steps
python audit/adjudicate.py                                       # do grouped differences describe the same thing?
python audit/rescore.py                                          # re-check paper quotes against the shown context
python audit/static_checks.py                                    # sorry/axiom scan, duplicates, definitional depth
python audit/report.py                                           # tables and out/report.html
python audit/changes.py                                          # CHANGES-v0.2.md against the v0.1 database and tag
```

Every model-derived row carries a run id in its `model` column (`<model>|thinking=<0/1>|run=<id>`; set with `AUDIT_RUN_ID` or `[run] id` in `audit.toml`), and report queries read only the current run's rows. The response cache key covers the model, the reasoning setting, temperature, token budget and the prompt. Responses logged before that key was introduced (the published v0.1 and v0.2 runs) are reused only with `AUDIT_LLM_LEGACY_CACHE=1`. `migrate_run_id.py` added run ids to rows written before run ids existed. `resample.py` (locating rerun with fresh seeds on a subset) is in the repo but was not run for v0.2.

The whole v0.2 sequence, including clearing the model-derived tables and the proof-choice log (`paper_text.py`), is `audit/run_v02.ps1`.

Set the model endpoint with `AUDIT_LLM_BASE_URL`, `AUDIT_LLM_MODEL` and `AUDIT_LLM_MAX_CONCURRENCY`. The locating and extraction scripts take `--items "Lemma 10.5"` if you want to try a few results first. Responses are cached by (model, prompt, sample), so a rerun reuses earlier samples instead of drawing new ones.
