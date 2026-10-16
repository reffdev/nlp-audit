# Review shortlist

**Selected by a fixed rule; not reviewed by a mathematician; entries are textual differences, not established mathematical differences.** Each entry also carries `likely_explanation`, a heuristic label assigned by fixed rules from the type and wording (parameter-set-uniformity, quantifier-made-explicit, norm-packaging, naming, incomplete-pair-coverage, needs-translation, substantive-candidate). It is a reading aid, not a finding, and it does not affect which entries are listed or their order. All the data is in `out/differences.csv`, and the method is in `METHODOLOGY.md`.

**How the targets were chosen.** Section 8 was the pilot. Lemmas 8.6 and 10.5 were added because Bastounis, Circelli and Hansen (arXiv:2610.08144) had already found discrepancies there, and the proof-level targets only cover the proofs of Lemmas 8.2, 8.6 and 10.5. The prompts never mention those discrepancies, but they did decide where the tool looked.

## Part A: differences in what is estimated

Every difference that all 3 samples reported (citing overlapping Lean lines, and confirmed the same difference by all 3 adjudication samples) as stronger-bound, weaker-bound or missing-supremum, plus the known discrepancies used to validate the tool (marked **validation**).

## 1. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets` · **validation**

- **Type:** stronger-bound · likely explanation (heuristic): `substantive-candidate` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper's derivative loss is m+4, while the Lean theorem assumes n+5 and concludes n.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The norm bound uses four extra derivatives: C_y^m bound from C_y^{m+4}.
  - quote (on the cited page: exact; in the text shown to the model: exact): `\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}`
- **Lean** ([SmoothFamilyTorusInverse.lean:868](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L868)): The JetBound conclusion uses order n from input order n+5, i.e. five extra derivatives.
  - quote: `JetBound f S (n + 5) C → JetBound (inverse d f) S n (K * C)`

## 2. (8.10) in proof of Lemma 8.2 · `ParametricTorusInverse.mixedJet_inverse_bound`

- **Type:** missing-supremum · likely explanation (heuristic): `parameter-set-uniformity` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration assumes uniform bounds over a parameter set and unit-square coordinates; the paper item does not state such uniformity.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper statement is not expressed as a uniform bound over a parameter set S and x,y in Icc(0,1).
  - quote (on the cited page: exact; in the text shown to the model: exact): `$$\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}, \qquad p \ge 1. \tag{8.10}$$`
- **Lean** ([ParametricTorusInverse.lean:656-657](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ParametricTorusInverse.lean#L656-L657)): The Lean hypotheses are uniform over p in S and x,y in Icc(0,1).
  - quote: `hzero : ∀ p ∈ S, ∀ x ∈ Icc (0 : ℝ) 1, ∀ y ∈ Icc (0 : ℝ) 1,
      ‖parameterJet q f (p, (x, y))‖ ≤ C`

## 3. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** missing-supremum · likely explanation (heuristic): `parameter-set-uniformity` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes uniformity over the parameter set S and the whole torus cover; the paper statement does not display that uniformity.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The displayed bound is a torus norm, not explicitly a uniform bound over an arbitrary parameter set S.
  - quote (on the cited page: exact; in the text shown to the model: exact): `\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}`
- **Lean** ([SmoothFamilyTorusInverse.lean:652-653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L652-L653)): JetBound quantifies over all p ∈ S and all Y.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## Part B: differences in how size is measured

Every difference that all 3 samples reported as different-norm (overlapping citations, confirmed by adjudication). Most of these are the Lean writing a norm or function class another way (for example a C^m norm as a bound on iterated derivatives). They're here because the rule picks them up, not because anyone has judged them to matter.

## 4. (8.10) in proof of Lemma 8.2 · `DiophantineGraph.radial_inverse_power_bound`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The two sides measure size by different objects, a function norm versus an absolute value of a symbol.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The left side is a C^m_y norm of L^{-p}H.
  - quote (on the cited page: exact; in the text shown to the model: exact): `\|\mathcal{L}^{-p}H\|_{C^m_y}`
- **Lean** ([DiophantineGraph.lean:257](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DiophantineGraph.lean#L257)): The left side is an absolute value of a scalar symbol.
  - quote: `|1 / radialSymbol m n| ^ p`

## 5. (8.10) in proof of Lemma 8.2 · `ParametricTorusInverse.mixedJet_inverse_bound`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses a C^m_y norm of the inverse applied to H; the Lean theorem uses the absolute norm of a mixed jet value of the inverse of f.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The bound is on ||L^{-p} H||_{C^m_y}.
  - quote (on the cited page: exact; in the text shown to the model: exact): `$$\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}, \qquad p \ge 1. \tag{8.10}$$`
- **Lean** ([ParametricTorusInverse.lean:664](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ParametricTorusInverse.lean#L664)): The bound is on ‖mixedJet q w (inverse d f) (p, Y)‖.
  - quote: `‖mixedJet q w (inverse d f) (p, Y)‖ ≤ mixedLossConstant w.length * C`

## 6. Lemma 8.2 · `VariableGaugeMean.compactPrimitive_q_finiteJets_global`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The two sides use different weight expressions for the role of controlling input derivatives.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The input derivative bound is expressed with C_{j,I}, ε^α, S_*^B, ζ, and δ^{-B}.
  - quote (on the cited page: exact; in the text shown to the model: exact): `$$|\partial^I f| \leq C_{j,I} \varepsilon^{\alpha} S^{B_{j,I}}_* \zeta \delta^{-B_{j,I}}.$$`
- **Lean** ([VariableGaugeMean.lean:1547](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L1547)): The input derivative bound is expressed as A times logWeight cL cR a b p of the radial ratio.
  - quote: `‖iteratedFDeriv ℝ j f (R, (z.2.1, Y))‖ ≤ A * logWeight cL cR a b p (R / qLength coord z.2.1)`

## 7. Lemma 8.2 · `VariableGaugeMean.compactPrimitive_q_finiteJets_global`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper uses a function-class description, while the Lean declaration uses an explicit finite derivative inequality.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The output is described by membership in M_alpha under the primitive normalization.
  - quote (on the cited page: exact; in the text shown to the model: exact): `belongs to $M_{\alpha}$ under the primitive normalization just defined.`
- **Lean** ([VariableGaugeMean.lean:1549](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L1549)): The output is described by a finite jet bound involving K, A, and logWeight.
  - quote: `K * A * logWeight cL cR a b p (z.1 / qLength coord z.2.1)`

## 8. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses a torus C^m norm, while Lean uses joint Fréchet jet bounds in parameters and torus variable.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): Size is measured by the torus norm C_y^m.
  - quote (on the cited page: exact; in the text shown to the model: exact): `\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}`
- **Lean** ([SmoothFamilyTorusInverse.lean:652-653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L652-L653)): Size is measured by JetBound, a prefix of full joint Fréchet-jet bounds on a parameter set.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 9. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper uses S_alpha and M_alpha class notation, while the Lean statement uses a different class predicate.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper measures targets and increments by S_alpha and M_alpha.
  - quote (on the cited page: exact; in the text shown to the model: exact): `targets in $S_{\alpha}$give increments in $M_{\alpha}$`
- **Lean** ([MeanLocalDefectBounds.lean:249](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L249)): The Lean statement measures the debt by UnweightedClass, and its assumptions use MeanClass, BandBound, and UnweightedClass.
  - quote: `UnweightedClass`

## 10. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper names S_alpha and M_alpha classes, while Lean uses a WeightedClasses.UnweightedClass hypothesis.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper uses S_alpha targets and M_alpha increments.
  - quote (on the cited page: exact; in the text shown to the model: exact): `targets in $S_{\alpha}$give increments in $M_{\alpha}$`
- **Lean** ([MeanRankUpdate.lean:1956](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1956)): The Lean declaration assumes UnweightedClass s alpha for the defect d.
  - quote: `(hd : WeightedClasses.UnweightedClass s α (fun n p => d n p.2.1))`

## 11. Lemma 8.7 · `MeanRankUpdate.concrete_physical_rank_update_meanClass`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The target class named in the paper is S_alpha, while the Lean hypothesis uses UnweightedClass.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper assumes targets in S_alpha.
  - quote (on the cited page: exact; in the text shown to the model: exact): `For every $\alpha$, targets in $S_{\alpha}$give increments in $M_{\alpha}$`
- **Lean** ([MeanRankUpdate.lean:1111-1112](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1111-L1112)): The Lean declaration assumes d is UnweightedClass α.
  - quote: `WeightedClasses.UnweightedClass (normalizedStripData coord qlo qhi rlo rhi cL cR
      hc hc1 hrlo hcL hcR ε S hε hεone hS) α d`

## 12. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_mem`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses the class notation M, while the Lean declaration uses the abbreviation MeanClass.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): R_g is stated to lie in M_{alpha+0.9-2kappa_s}.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:439](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L439)): actualRadialError is stated to lie in MeanClass s (H + 9/10 - 2κ).
  - quote: `MeanClass s (H + 9 / 10 - 2 * κ) (actualRadialError o base m h W)`

## 13. Lemma 8.8 · `DefectIncrementBounds.defects_after_rank_mem`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses the S-class notation, while Lean uses an unweighted MemClass over the slow strip data.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The updated defect vector is stated to lie in S_{α+0.9-2κ_s}.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: normalized): `$(\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}$.`
- **Lean** ([DefectIncrementBounds.lean:569-570](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L569-L570)): The Lean conclusion states that the i-th updated defect lies in UnweightedClass (slowStripData) with exponent H + 9/10 - 2κ.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS) (H + 9 / 10 - 2 * κ)`

## 14. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses the notation S, while the Lean declaration uses the UnweightedClass abbreviation over slowStripData.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The new defects are stated to lie in S_{alpha+0.9-2*kappa_s}.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `(\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:857](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L857)): The debt component is stated to lie in UnweightedClass with slowStripData.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS)`

## 15. Proposition 8.3 · `PhysicalMeanDomain.meanClass_pressureMass`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper names the target class S_α, while Lean names it UnweightedClass with localSlowStripData.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(i)): The paper concludes P ∈ S_α.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `$\mathcal{P} \in S_\alpha$`
- **Lean** ([PhysicalMeanDomain.lean:1058-1059](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1058-L1059)): The Lean conclusion is UnweightedClass (localSlowStripData ...) α (fun n => PressureStream.pressureMass (f n)).
  - quote: `UnweightedClass (localSlowStripData U hU ε L hε hεone hL) α
      (fun n => PressureStream.pressureMass (f n))`

## 16. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamGamma`

- **Type:** different-norm · likely explanation (heuristic): `norm-packaging` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper names the function class M_α, while the Lean statement uses MeanClass on localStripData.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): The class hypothesis is γ_d ∈ M_α.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `If $\gamma_d \in M_\alpha$,`
- **Lean** ([PhysicalMeanDomain.lean:1622](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1622)): The Lean hypothesis is MeanClass (localStripData ...) α f.
  - quote: `(hclass : MeanClass (localStripData a b cL cR ha hcL hcR ε L hε hεone hL U hU) α f)`

## 17. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamPotential`

- **Type:** different-norm · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper's function class is named M_alpha, while the Lean statement uses a formal MeanClass based on localStripData.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): The paper uses the class M_alpha for gamma_d.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `If $\gamma_d \in M_\alpha$`
- **Lean** ([PhysicalMeanDomain.lean:1571](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1571)): The Lean declaration uses MeanClass with localStripData for f.
  - quote: `MeanClass (localStripData a b cL cR ha hcL hcR ε L hε hεone hL U hU) α f`

## Part C: confirmed differences in the categories Parts A and B leave out

Every difference that all 3 samples reported, confirmed by adjudication, as missing-hypothesis (the Lean assumes something the paper's statement doesn't) or different-domain. These are left out of Parts A and B because most are the Lean spelling out conditions the paper leaves implicit; they are listed so the exclusion can be checked.

## 18. (10.15) in proof of Lemma 10.5 · `ConservativeDifference.conservative_difference_equation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper states the divergence condition for the difference, while Lean assumes each velocity field is divergence-free at the point.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), (10.15)): The paper displays div w = 0 as part of (10.15).
  - quote (on the cited page: exact; in the text shown to the model: exact): `\text{div } w = 0.`
- **Lean** ([R3/ConservativeDifference.lean:145-146](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/ConservativeDifference.lean#L145-L146)): The Lean theorem assumes spatialDivergence u t x = 0 and spatialDivergence v t x = 0.
  - quote: `(hdivu : spatialDivergence u t x = 0)`

## 19. (10.16) in proof of Lemma 10.5 · `RieszTestOperators.pressurePair_laplacianCLM`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration quantifies over a Schwartz test function; the paper statement does not mention one.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), (10.16)): the displayed distribution statement has no explicit test function.
  - quote (on the cited page: normalized; in the text shown to the model: normalized): `$\pi_* = \sum_{i,j=1}^3 R_i R_j g_{ij}$`
- **Lean** ([R3/RieszTestOperators.lean:278](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/RieszTestOperators.lean#L278)): ψ : ComplexTest is an explicit argument.
  - quote: `(ψ : ComplexTest)`

## 20. (10.17) in proof of Lemma 10.5 · `WeightedSobolev.cutoffL6_le`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean parameterizes the size of the cutoff derivative by L; the paper encodes it through the scaling R.
- **Paper** ([p.122](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=122), (10.17)): The paper does not introduce an explicit derivative bound L; the coefficient in front of ||w||_2 is R^{-1}.
  - quote (on the cited page: exact; in the text shown to the model: exact): `R^{-1} \|w\|_2`
- **Lean** ([R3/WeightedSobolev.lean:242](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/WeightedSobolev.lean#L242)): The Lean declaration assumes 0≤L and ‖fderiv φ x‖≤L, and uses L in the conclusion.
  - quote: `{L : ℝ} (hL0 : 0 ≤ L) (hL : ∀ x, ‖fderiv ℝ φ x‖ ≤ L) :`

## 21. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean assumes a uniform L1 bound on tensor differences; the paper statement does not state it.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): The paper statement does not state a uniform L1 bound for tensor differences of u and v.
  - quote (on the cited page: exact; in the text shown to the model: exact): `where u is the localized velocity of Proposition 10.1.`
- **Lean** ([R3/PressureFlux.lean:583-584](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L583-L584)): The Lean declaration assumes integrability and an L1 bound for tensorDiff u v.
  - quote: `(hG : ∀ t ∈ Icc 0 T, ∀ i j : Fin 3,
      Integrable (tensorDiff u v t i j) volume ∧ comparisonLpNorm 1 (tensorDiff u v t i j) ≤ G₀)`

## 22. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean assumes the residuals of the two pairs are equal; the paper statement does not state this equality.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): The paper says v,P is a smooth solution of (1.1); it does not state an equality of Navier-Stokes residuals between u,p and v,q.
  - quote (on the cited page: exact; in the text shown to the model: exact): `If $v, P$ is a smooth solution of (1.1) at viscosity one`
- **Lean** ([R3/PressureRecovery.lean:41-42](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureRecovery.lean#L41-L42)): The Lean declaration assumes equation, the equality of navierStokesResidual u p and v q.
  - quote: `equation : ∀ t ∈ Ioo 0 T, ∀ x,
    navierStokesResidual u p t x = navierStokesResidual v q t x`

## 23. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean assumes both velocity fields are spatially divergence-free; the paper statement does not explicitly state it.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): The paper statement does not explicitly state spatial divergence-free conditions for u and v.
  - quote (on the cited page: exact; in the text shown to the model: exact): `If $v, P$ is a smooth solution of (1.1) at viscosity one`
- **Lean** ([R3/PressureRecovery.lean:39-40](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureRecovery.lean#L39-L40)): The Lean declaration assumes div_u and div_v.
  - quote: `div_u : ∀ t ∈ Ioo 0 T, ∀ x, spatialDivergence u t x = 0
    div_v : ∀ t ∈ Ioo 0 T, ∀ x, spatialDivergence v t x = 0`

## 24. (8.10) in proof of Lemma 8.2 · `DiophantineGraph.radial_inverse_power_bound`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes an explicit nonzero integer pair hypothesis that is not stated verbatim in the paper item.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The quoted paper item does not explicitly state a nonzero-frequency hypothesis for the displayed estimate.
  - quote (on the cited page: exact; in the text shown to the model: exact): `the Diophantine inequality (6.7) gives`
- **Lean** ([DiophantineGraph.lean:256](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DiophantineGraph.lean#L256)): The Lean theorem assumes m ≠ 0 ∨ n ≠ 0.
  - quote: `(hmn : m ≠ 0 ∨ n ≠ 0)`

## 25. (8.10) in proof of Lemma 8.2 · `FourierAlias.cutoffAlias_arbitrary_order`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement assumes support in a radial interval, while the paper item (8.10) does not state such support.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The displayed inequality (8.10) does not include a radial support assumption.
  - quote (on the cited page: exact; in the text shown to the model: exact): `For a zero-mean torus function $H$`
- **Lean** ([FourierAlias.lean:563](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/FourierAlias.lean#L563)): The Lean declaration assumes RadiallySupported a b f.
  - quote: `(hs : RadialAlias.RadiallySupported a b f)`

## 26. (8.10) in proof of Lemma 8.2 · `FourierAlias.cutoffAlias_arbitrary_order`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement assumes explicit cutoff behavior, while the paper item (8.10) does not state it.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The displayed inequality (8.10) does not state cutoff plateau conditions.
  - quote (on the cited page: exact; in the text shown to the model: exact): `For a zero-mean torus function $H$`
- **Lean** ([FourierAlias.lean:564](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/FourierAlias.lean#L564)): The Lean declaration assumes hleft and hright, namely χ u = 0 for u ≤ a and χ u = 1 for b ≤ u.
  - quote: `(hleft : ∀ u ≤ a, χ u = 0) (hright : ∀ u, b ≤ u → χ u = 1)`

## 27. (8.10) in proof of Lemma 8.2 · `ParametricTorusInverse.mixedJet_inverse_bound`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration assumes infinite smoothness, while the paper statement is expressed with a finite derivative norm.
  - *Editorial note: the paper's lemma assumes a smooth coefficient; this description is wrong*
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper statement only displays the finite C^{m+p+3}_y norm of H.
  - quote (on the cited page: exact; in the text shown to the model: exact): `\|H\|_{C^{m+p+3}_y}`
- **Lean** ([ParametricTorusInverse.lean:654](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ParametricTorusInverse.lean#L654)): The Lean theorem assumes f is ContDiff ℝ ∞.
  - quote: `hf : ContDiff ℝ ∞ f`

## 28. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.applyMultiplier_finiteJets`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean assumes infinite smoothness, whereas the paper statement only uses a finite C^{m+p+3} norm.
  - *Editorial note: the paper's lemma assumes a smooth coefficient; this description is wrong*
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): H only needs C^{m+p+3}_y regularity in the stated norm.
  - quote (on the cited page: exact; in the text shown to the model: exact): `\|H\|_{C^{m+p+3}_y}`
- **Lean** ([SmoothFamilyTorusInverse.lean:850](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L850)): f is assumed ContDiff ℝ ∞.
  - quote: `ContDiff ℝ ∞ f →`

## 29. (8.23) in proof of Lemma 8.6 · `CopySolveCompatibility.commonSolve_refine`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean theorem has an explicit inequality hypothesis that is not present in the paper's displayed identity.
- **Paper** ([p.96](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=96), (8.23)): The paper statement of (8.23) does not state an inequality a ≤ b.
  - quote (on the cited page: exact; in the text shown to the model: exact): `N_{\text{abs}}^{-1} P_i = T_g^{-i} P_i N_i^{-1}.`
- **Lean** ([CopySolveCompatibility.lean:153](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/CopySolveCompatibility.lean#L153)): The Lean declaration assumes hab : a ≤ b.
  - quote: `(hab : a ≤ b)`

## 30. (8.23) in proof of Lemma 8.6 · `TemporalMeanUpdate.absoluteInverse_coverMap`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean makes the unit-periodicity condition on the universal cover explicit.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The quoted step does not explicitly assume unit periodicity on Plane.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $N = v_t \cdot \partial_y$ on $\mathbb{T}^2$`
- **Lean** ([TemporalMeanUpdate.lean:247](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TemporalMeanUpdate.lean#L247)): The theorem assumes SmoothFourierData.UnitPeriodic f.
  - quote: `(hp : SmoothFourierData.UnitPeriodic f)`

## 31. (8.9) in proof of Lemma 8.2 · `LocalSignedRequest.meanClass_compact`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean includes an explicit radial support hypothesis for f; the quoted paper step only refers to the shell.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.9)): The paper item does not explicitly state a radial support hypothesis for f; it refers to the shell.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Multiplication by $R^e$ preserves the input estimate on the shell.`
- **Lean** ([LocalSignedRequest.lean:369](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/LocalSignedRequest.lean#L369)): Lean assumes SupportedOn a b U for each f n.
  - quote: `(hs : ∀ n, PhysicalMeanDomain.SupportedOn a b U (f n))`

## 32. (8.9) in proof of Lemma 8.2 · `LocalSignedRequest.meanClass_compact`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean includes auxiliary scale sequences epsilon and L with explicit bounds; the paper item does not state an L sequence.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper uses epsilon and constants but does not state an L sequence with 1≤L.
  - quote (on the cited page: exact; in the text shown to the model: exact): `$$|\partial^I f| \leq C_{j,I} \varepsilon^{\alpha} S^{B_{j,I}}_* \zeta \delta^{-B_{j,I}}.$$`
- **Lean** ([LocalSignedRequest.lean:365](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/LocalSignedRequest.lean#L365)): Lean assumes L : ℕ→ℝ with ∀ n, 1≤L n and epsilon bounds.
  - quote: `(ε L : ℕ → ℝ) (hε : ∀ n, 0 < ε n) (hεone : ∀ n, ε n ≤ 1) (hL : ∀ n, 1 ≤ L n)`

## 33. (8.9) in proof of Lemma 8.2 · `RadialPullback.physicalCompact_eq_radialIntegral`

- **Type:** missing-hypothesis · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration includes an explicit support hypothesis with named endpoints a and b.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.9)): The paper says the shell stays in a fixed compact subset of R>0.
  - quote (on the cited page: exact; in the text shown to the model: exact): `The shell stays in a fixed compact subset of $R > 0$`
- **Lean** ([RadialPullback.lean:360](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L360)): Lean assumes RadiallySupported a b g, i.e. support in Icc a b.
  - quote (not verified): `(hs : RadialAlias.RadiallySupported a b g)`

## 34. (8.9) in proof of Lemma 8.2 · `RadialPullback.physicalCompact_eq_radialIntegral`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires the radial coordinate of z to lie above a.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.9)): The paper's displayed (8.9) does not state a lower-bound condition on the evaluation point.
  - quote (on the cited page: exact; in the text shown to the model: exact): `The shell stays in a fixed compact subset of $R > 0$`
- **Lean** ([RadialPullback.lean:361](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L361)): Lean assumes hz : a ≤ z.1.
  - quote: `(hz : a ≤ z.1)`

## 35. Lemma 8.2 · `RadialPullback.meanClass_physicalCompact`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration includes an explicit radial support hypothesis that is not spelled out in the paper statement.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The lemma statement does not explicitly assume a closed radial support for f.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $f \in M_{\alpha}$ be a smooth scalar coefficient.`
- **Lean** ([RadialPullback.lean:814](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L814)): Lean assumes RadiallySupported a b (g n).
  - quote (not verified): `RadiallySupported a b (g n)`

## 36. Lemma 8.2 · `RadialPullback.meanClass_physicalCompact`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration makes the positivity and order of the strip parameters explicit.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The statement fixes a band and shell but does not state 0<a<a<b, 0<d, and 0<cL,cR.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix a correction stage j, an exponent $\alpha$, a band, its common torus $y = Y_{i_0}$`
- **Lean** ([RadialPullback.lean:811](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L811)): Lean assumes these parameter inequalities.
  - quote: `ha : 0 < a) (hab : a < b) (hd : 0 < d) (hcL : 0 < cL) (hcR : 0 < cR`

## 37. Lemma 8.2 · `RadialPullback.supported_meanClass_physicalCompact`

- **Type:** missing-hypothesis · likely explanation (heuristic): `quantifier-made-explicit` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean makes explicit uniform bounds on the small and large scales that are not written in the paper lemma statement.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The lemma statement uses ε and S_* in the bounds but does not state the inequalities 0 < ε ≤ 1 and S ≥ 1.
  - quote (on the cited page: normalized; in the text shown to the model: normalized): `$\varepsilon^{\alpha} S^{B_{j,I}}_* \zeta \delta^{-B_{j,I}}$`
- **Lean** ([RadialPullback.lean:845](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L845)): The Lean declaration assumes hε, hεone, and hS for all n.
  - quote: `(hε : ∀ n, 0 < ε n) (hεone : ∀ n, ε n ≤ 1) (hS : ∀ n, 1 ≤ S n)`

## 38. Lemma 8.2 · `RadialPullback.supported_meanClass_physicalCompact`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean names concrete annulus and edge-scale parameters with positivity assumptions, while the paper describes the band and profile abstractly.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper refers to a band and a fixed profile without naming a, b, cL, cR or their inequalities in the lemma statement.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix a correction stage j, an exponent $\alpha$, a band, its common torus $y = Y_{i_0}$`
- **Lean** ([RadialPullback.lean:843-844](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L843-L844)): The Lean declaration assumes 0 < a < b, cL > 0, cR > 0 and builds logStripData from them.
  - quote: `{a b d cL cR : ℝ}
    (ha : 0 < a) (hab : a < b) (hd : 0 < d) (hcL : 0 < cL) (hcR : 0 < cR)`

## 39. Lemma 8.2 · `VariableGaugeMean.compactPrimitive_q_finiteJets_global`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean assumes a structured slow region, while the paper statement refers to a band and common torus.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper statement does not state a SlowRegion hypothesis.
  - quote (on the cited page: exact; in the text shown to the model: exact): `a band, its common torus $y = Y_{i_0}$`
- **Lean** ([VariableGaugeMean.lean:1536](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L1536)): The Lean declaration takes U : SlowRegion coord.
  - quote: `(U : SlowRegion coord)`

## 40. Lemma 8.2 · `VariableGaugeMean.compactPrimitive_radial_identity`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration has an explicit support hypothesis not written in the paper lemma statement.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper statement does not explicitly state a SupportedGauge support condition on f.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $f \in M_{\alpha}$ be a smooth scalar coefficient.`
- **Lean** ([VariableGaugeMean.lean:2117](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2117)): The Lean theorem assumes hs : SupportedGauge a b (qLength coord) U.carrier f.
  - quote: `(hs : SupportedGauge a b (qLength coord) U.carrier f)`

## 41. Lemma 8.2 · `VariableGaugeMean.meanClass_compactPrimitive`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** These positivity assumptions are present in the Lean context.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper item does not explicitly state 0 < a, 0 < cL, 0 < cR.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix a correction stage j, an exponent $\alpha$, a band, its common torus $y = Y_{i_0}$, and $e \in \{0,1,2\}$.`
- **Lean** ([VariableGaugeMean.lean:1689](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L1689)): The Lean section variables include ha, hcL, hcR.
  - quote: `variable (ha : 0 < a) (hcL : 0 < cL) (hcR : 0 < cR)`

## 42. Lemma 8.2 · `VariableGaugeMean.meanClass_compactPrimitive`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** These are explicit Lean hypotheses.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper item does not explicitly state the sequence bounds on ε and L.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix a correction stage j, an exponent $\alpha$, a band, its common torus $y = Y_{i_0}$, and $e \in \{0,1,2\}$.`
- **Lean** ([VariableGaugeMean.lean:1690](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L1690)): The Lean context assumes ε n > 0, ε n ≤ 1, and 1 ≤ L n.
  - quote: `(ε L : ℕ → ℝ) (hε : ∀ n, 0 < ε n) (hεone : ∀ n, ε n ≤ 1) (hL : ∀ n, 1 ≤ L n)`

## 43. Lemma 8.2 · `VariableGaugeMean.meanClass_compactPrimitive`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement includes an explicit support hypothesis.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper states f is in M_alpha and smooth, but does not separately state a supported-gauge condition.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $f \in M_{\alpha}$ be a smooth scalar coefficient.`
- **Lean** ([VariableGaugeMean.lean:1695](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L1695)): The Lean declaration assumes SupportedGauge for each f n.
  - quote: `(hs : ∀ n, SupportedGauge a b (qLength coord) U.carrier (f n))`

## 44. Lemma 8.6 · `MeanChartCompatibility.commonTemporalFields_represents`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes an explicit ContDiff ∞ assumption for fθ and fz that is not present in the quoted paper part.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The quoted compatibility part does not explicitly assume smoothness of the chart fields.
  - quote (on the cited page: exact; in the text shown to the model: exact): `For a pair $E_{\theta}, E_z \in M_{\alpha}$ of normalized angularly invariant residual coefficients`
- **Lean** ([MeanChartCompatibility.lean:1166](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1166)): The Lean theorem assumes each chart field is infinitely smooth.
  - quote: `(hθ : ∀ n, ContDiff ℝ ∞ (fθ n)) (hz : ∀ n, ContDiff ℝ ∞ (fz n))`

## 45. Lemma 8.6 · `MeanChartCompatibility.commonTemporalFields_represents`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean requires TorusPeriodicLift for fθ and fz, while the paper's compatibility sentence does not state this explicitly.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The quoted compatibility part does not explicitly assume torus periodicity of the chart fields.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `This physical definition ensures agreement on chart overlaps.`
- **Lean** ([MeanChartCompatibility.lean:1167-1168](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1167-L1168)): The Lean theorem assumes both chart fields are torus periodic lifts.
  - quote: `(hpθ : ∀ n, PressureStream.TorusPeriodicLift (fθ n))
    (hpz : ∀ n, PressureStream.TorusPeriodicLift (fz n))`

## 46. Lemma 8.6 · `MeanChartCompatibility.commonTemporalFields_represents`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean adds a RadiallySupported hypothesis for fz that is not stated in the paper's compatibility sentence.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The quoted compatibility part does not state a radial-support condition on fz.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `This physical definition ensures agreement on chart overlaps.`
- **Lean** ([MeanChartCompatibility.lean:1169](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1169)): The Lean theorem assumes fz is radially supported in a scaled interval.
  - quote (not verified): `(hsz : ∀ n, RadialAlias.RadiallySupported (chartScale n * a) (chartScale n * b) (fz n))`

## 47. Lemma 8.6 · `MeanChartCompatibility.commonTemporalFields_represents`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean takes explicit source-identity hypotheses that are not stated in the quoted paper part.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The paper defines the update by the physical inverse and normalizations, without stating these exact source identities as assumptions.
  - quote (on the cited page: exact; in the text shown to the model: exact): `use this inverse in the original auxiliary coordinate $Y$ to define the physical tangential update $-N_{\text{abs}}^{-1}(E_{\theta,\text{phys}}^{\circ},E_{z,\text{phys}}^{\circ})$`
- **Lean** ([MeanChartCompatibility.lean:1170-1171](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1170-L1171)): The Lean theorem assumes fieldOnPhysical identities for fθ and fz at level 2*A h + 1/2.
  - quote: `(hsourceθ : ∀ n, fieldOnPhysical h n (index n) (2 * CoordinateAlgebra.A h + 1 / 2) (fθ n) = Fθ)
    (hsourcez : ∀ n, fieldOnPhysical h n (index n) (2 * CoordinateAlgebra.A h + 1 / 2) (fz n) = Fz)`

## 48. Lemma 8.6 · `MeanChartCompatibility.commonTemporalFields_represents`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean restricts the point z by a nonnegativity condition not stated in the paper sentence.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The paper's compatibility sentence does not assume a nonnegative first coordinate for the evaluation point.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `This physical definition ensures agreement on chart overlaps.`
- **Lean** ([MeanChartCompatibility.lean:1172](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1172)): The Lean theorem assumes 0 ≤ z.1.
  - quote: `(hr : 0 ≤ z.1)`

## 49. Lemma 8.6 · `TemporalMeanUpdate.temporal_mean_update`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean restricts fz to radial support in Icc a b.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The paper statement does not state that fz is supported in a fixed radial interval.
  - quote (on the cited page: exact; in the text shown to the model: exact): `For a pair $E_{\theta}, E_z \in M_{\alpha}$ of normalized angularly invariant residual coefficients`
- **Lean** ([TemporalMeanUpdate.lean:822](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TemporalMeanUpdate.lean#L822)): The Lean declaration assumes RadiallySupported a b fz.
  - quote: `(hsz : RadialAlias.RadiallySupported a b fz)`

## 50. Lemma 8.6 · `TemporalMeanUpdate.temporal_mean_update`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean adds positivity and interval-order hypotheses.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The paper statement does not state 0<a, a<b, or 0<d.
  - quote (on the cited page: exact; in the text shown to the model: exact): `For a pair $E_{\theta}, E_z \in M_{\alpha}$ of normalized angularly invariant residual coefficients`
- **Lean** ([TemporalMeanUpdate.lean:818](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TemporalMeanUpdate.lean#L818)): The Lean declaration assumes ha, hab, and hd.
  - quote: `(ha : 0 < a) (hab : a < b) (hd : 0 < d)`

## 51. Lemma 8.7 · `FiveRowRank.exists_five_row_repair`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement has an explicit vanishing hypothesis for G, whereas the paper statement leaves G in the displayed equations and cites (8.24).
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper statement does not explicitly state G = 0; it only refers to the fixed slow base satisfying (8.24).
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24)`
- **Lean** ([FiveRowRank.lean:314](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/FiveRowRank.lean#L314)): The Lean declaration assumes G R = 0 on Ioo a b.
  - quote: `hG : ∀ R ∈ Ioo a b, G R = 0`

## 52. Lemma 8.7 · `FiveRowRank.exists_five_row_repair`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement fixes V by the explicit background formula, while the paper statement refers to condition (8.24) without displaying that formula in the lemma statement.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper statement does not explicitly write V R = background lam C R; it cites (8.24).
  - quote (on the cited page: exact; in the text shown to the model: exact): `satisfies (8.24)`
- **Lean** ([FiveRowRank.lean:313](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/FiveRowRank.lean#L313)): The Lean declaration assumes V equals background lam C R on Ioo a b.
  - quote: `hV : ∀ R ∈ Ioo a b, V R = background lam C R`

## 53. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement includes additional regularity and support hypotheses on covariance components that are not present in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state smoothness and support assumptions on the covariance components.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$.`
- **Lean** ([MeanLocalDefectBounds.lean:237-238](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L237-L238)): The Lean theorem assumes hWc and hWs for u.covariance.
  - quote: `SmoothOn (PhysicalMeanDomain.slowDomain U.carrier) (u.covariance i j)`

## 54. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes operator bounds that are not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state OperatorBounds on c.operators with a parameter kappa.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$.`
- **Lean** ([MeanLocalDefectBounds.lean:241-242](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L241-L242)): The Lean theorem assumes ho : OperatorBounds ... c.operators kappa.
  - quote: `c.operators κ)`

## 55. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes local base bounds that are not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state LocalBaseBounds on c.base.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$.`
- **Lean** ([MeanLocalDefectBounds.lean:243-244](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L243-L244)): The Lean theorem assumes hb : LocalBaseBounds ... c.base.
  - quote: `(fun n => tsupport (rankPotential g r c u n)) c.base)`

## 56. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes cumulative mean bounds that are not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state CumulativeBounds on u.mean.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$.`
- **Lean** ([MeanLocalDefectBounds.lean:245-246](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L245-L246)): The Lean theorem assumes hm : MeanIncrementBounds.CumulativeBounds ... u.mean.
  - quote: `u.mean)`

## 57. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement includes a support hypothesis for the mean triple that is not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state a SupportedTriple assumption for u.mean.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$.`
- **Lean** ([MeanLocalDefectBounds.lean:236](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L236)): The Lean theorem assumes hms : SupportedTriple ... u.mean.
  - quote: `SupportedTriple g.radial.inner g.radial.outer (qLength coord) U.carrier u.mean`

## 58. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes local operators that are not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state a LocalRankDefect.LocalOperators assumption.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$.`
- **Lean** ([MeanLocalDefectBounds.lean:233](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L233)): The Lean theorem assumes hop : LocalRankDefect.LocalOperators U.carrier c.operators.
  - quote: `(hop : LocalRankDefect.LocalOperators U.carrier c.operators)`

## 59. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes explicit interval-containment hypotheses not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state containment of lo and hi in terms of sqrt(qlo)*a and sqrt(qhi)*b.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1949](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1949)): The Lean declaration assumes lo ≤ Real.sqrt qlo * a and Real.sqrt qhi * b ≤ hi.
  - quote: `(hleft : lo ≤ Real.sqrt qlo * a) (hright : Real.sqrt qhi * b ≤ hi)`

## 60. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes a positive-time chartInput condition.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state that chartInput is in positiveTime on the domain.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1950](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1950)): The Lean declaration assumes chartInput p is in positiveTime for p in s.domain.
  - quote: `(hT : ∀ p ∈ s.domain, chartInput p ∈ PhysicalCoordinateBounds.positiveTime)`

## 61. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes a bounded chartQ condition.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state that chartQ lies in Icc qlo qhi.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1951](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1951)): The Lean declaration assumes chartQ coord p lies in Icc qlo qhi for p in s.domain.
  - quote: `(hq : ∀ p ∈ s.domain, chartQ coord p ∈ Icc qlo qhi)`

## 62. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes an explicit radial-coordinate bound.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state that the first coordinate of p lies in Icc lo hi.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1952](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1952)): The Lean declaration assumes p.1 lies in Icc lo hi for p in s.domain.
  - quote: `(hR : ∀ p ∈ s.domain, p.1 ∈ Icc lo hi)`

## 63. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes a supportBand zeta positivity hypothesis.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state a positive lower bound for s.zeta on supportBand.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1953](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1953)): The Lean declaration assumes such a lower bound exists.
  - quote: `(hz : ∃ δ : ℝ, 0 < δ ∧ ∀ p ∈ s.domain, p ∈ supportBand a b qlo qhi → δ ≤ s.zeta p)`

## 64. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean's StripData parameter carries structural regularity assumptions not stated in the paper item.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper does not state an open-domain StripData with smooth nonnegative zeta.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1945](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1945)): The Lean theorem takes s : WeightedClasses.StripData ChartPoint, which includes isOpen_domain, zeta_smooth, and zeta_nonneg.
  - quote: `theorem actual_rank_stream_identities (s : WeightedClasses.StripData ChartPoint)`

## 65. Lemma 8.7 · `MeanRankUpdate.concrete_physical_rank_update_meanClass`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean adds strip containment inequalities.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper statement does not state rlo < sqrt qlo * a or sqrt qhi * b < rhi.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the fixed slow base satisfies (8.24) on the reserved interior interval $I_m$, with $\lambda > 0$ and $|a(\eta)| \ge a_0 > 0$`
- **Lean** ([MeanRankUpdate.lean:1108](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1108)): The Lean declaration assumes hleft and hright.
  - quote: `(hleft : rlo < Real.sqrt qlo * a) (hright : Real.sqrt qhi * b < rhi)`

## 66. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_eq_formula`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean requires U to be open; the paper statement does not state an open set.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): No openness hypothesis for U is stated.
  - quote (on the cited page: exact; in the text shown to the model: exact): `supported in the active shell`
- **Lean** ([DefectIncrementBounds.lean:401](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L401)): hU : IsOpen U is assumed.
  - quote: `(hU : IsOpen U)`

## 67. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_eq_formula`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean assumes smoothness of the radial profile on U; the paper statement does not state this exact hypothesis.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper does not state ContDiffOn infinity smoothness of o.radialProfile on U.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the slow base satisfies (8.24)`
- **Lean** ([DefectIncrementBounds.lean:402](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L402)): ha assumes ContDiffOn ℝ ∞ o.radialProfile U.
  - quote: `ha : ContDiffOn ℝ ∞ o.radialProfile U`

## 68. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_eq_formula`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean assumes each component of W is smooth on U; the paper statement does not state this exact hypothesis.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper says the wave field w is fixed but does not state smoothness of W i j on U.
  - quote (on the cited page: normalized; in the text shown to the model: normalized): `keep the base and wave field $w$ fixed`
- **Lean** ([DefectIncrementBounds.lean:405](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L405)): hW assumes SmoothOn U (W i j) for all i j.
  - quote: `hW : ∀ i j, SmoothOn U (W i j)`

## 69. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration assumes smoothness of every component of W on s.domain, while the paper item only notes that W is unchanged in the proof.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Proof): The paper proof says the covariance W is unchanged; the statement does not require SmoothOn W.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `The covariance W is unchanged`
- **Lean** ([DefectIncrementBounds.lean:438](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L438)): The Lean declaration assumes hW : ∀ i j, SmoothOn s.domain (W i j).
  - quote: `(hW : ∀ i j, SmoothOn s.domain (W i j))`

## 70. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration assumes an OperatorBounds hypothesis, while the paper statement does not state this hypothesis explicitly.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper statement does not mention an OperatorBounds hypothesis.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the slow base satisfies (8.24)`
- **Lean** ([DefectIncrementBounds.lean:415](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L415)): The Lean declaration includes ho : OperatorBounds s o κ.
  - quote: `(ho : OperatorBounds s o κ)`

## 71. Lemma 8.8 · `DefectIncrementBounds.defects_after_rank_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean assumes a precise linear-row cancellation equality that is not stated verbatim in the paper lemma statement.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper statement does not explicitly assume the equality linearRows o base h = -defects o base m W; it describes applying Lemma 8.7 and realizing gamma_d.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Apply Lemma 8.7 with these three defects as its targets, and realize the resulting $\gamma_d$ by $(8.14)$.`
- **Lean** ([DefectIncrementBounds.lean:568](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L568)): The Lean theorem has hrows as an explicit hypothesis.
  - quote: `(hrows : linearRows o base h = -defects o base m W)`

## 72. Lemma 8.8 · `DefectIncrementBounds.defects_after_rank_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean includes an explicit shell-support hypothesis for the W field.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper keeps the wave field w fixed but does not state that W is Shell a b for all indices.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Lemma 8.8.`
- **Lean** ([DefectIncrementBounds.lean:533](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L533)): Lean assumes hW : ∀ i j, Shell a b (W i j).
  - quote: `(hW : ∀ i j, Shell a b (W i j))`

## 73. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration includes a covariance shell hypothesis not spelled out in the paper item.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper statement does not explicitly assume a shell condition on the covariance.
  - quote (on the cited page: exact; in the text shown to the model: exact): `keep the base and wave field w fixed`
- **Lean** ([DefectIncrementBounds.lean:839](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L839)): The Lean statement assumes hW : forall i j, Shell a b (u.covariance i j).
  - quote: `  (hW : ∀ i j, Shell a b (u.covariance i j))`

## 74. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration has an explicit rank-geometry hypothesis.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper statement does not mention a RankGeometry hypothesis.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Form $g_r$ and $(\mathcal{P}, \mathcal{J}_{\theta}, \mathcal{J}_z)$ by Equations (8.3), (8.12) and (8.15).`
- **Lean** ([DefectIncrementBounds.lean:835](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L835)): The Lean statement assumes hg : RankGeometry p r c u.
  - quote: `  (axial : P × PressureStream.Plane) (hg : RankGeometry p r c u)`

## 75. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration includes a positivity hypothesis for the operators.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper statement does not mention a PositiveOperators hypothesis.
  - quote (on the cited page: exact; in the text shown to the model: exact): `keep the base and wave field w fixed`
- **Lean** ([DefectIncrementBounds.lean:836](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L836)): The Lean statement assumes hop : PositiveOperators c.operators.
  - quote: `  (hop : PositiveOperators c.operators) (hbs : SmoothTriple positiveDomain c.base)`

## 76. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration uses an abstract operator-bounds hypothesis.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper statement does not mention an OperatorBounds hypothesis.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `every fixed coefficient derivative of b is bounded by $C_I \varepsilon S^{B_I}_*$, and those of the slow $V$, $G$ by $C_I S^{B_I}_*$`
- **Lean** ([DefectIncrementBounds.lean:841](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L841)): The Lean statement assumes ho : OperatorBounds ... c.operators kappa.
  - quote: `  (ho : OperatorBounds`

## 77. Lemma 8.8 · `MeanLocalDefectBounds.rankStage_gain_of_targets`

- **Type:** missing-hypothesis · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration has a named operator-bound hypothesis that is not explicitly stated in the paper item.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): does not explicitly assume an operator bound with parameter kappa
  - quote (on the cited page: exact; in the text shown to the model: exact): `Apply Lemma 8.7 with these three defects as its targets`
- **Lean** ([MeanLocalDefectBounds.lean:307-308](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L307-L308)): assumes OperatorBounds for c.operators with kappa
  - quote: `(ho : OperatorBounds (movingStripData U g.radial.inner g.radial.outer cL cR ha hcL hcR ε L hε hεone hL)
      c.operators κ)`

## 78. Lemma 8.8 · `MeanLocalDefectBounds.rankStage_gain_of_targets`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration makes the covariance smoothness/support assumptions explicit.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): does not explicitly assume smoothness and support of the covariance entries
  - quote (on the cited page: exact; in the text shown to the model: exact): `keep the base and wave field w fixed`
- **Lean** ([MeanLocalDefectBounds.lean:303-304](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L303-L304)): assumes SmoothOn and Support for every covariance entry
  - quote: `(hWc : ∀ i j, SmoothOn (PhysicalMeanDomain.slowDomain U.carrier) (u.covariance i j))`

## 79. Lemma 8.8 · `MeanLocalDefectBounds.rankStage_gain_of_targets`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration includes a smoothness hypothesis for the base that is not explicitly written in the paper item.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): states that the slow base satisfies (8.24) but not a SmoothTriple hypothesis on the positive domain
  - quote (on the cited page: exact; in the text shown to the model: exact): `Suppose that the slow base satisfies (8.24)`
- **Lean** ([MeanLocalDefectBounds.lean:300](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L300)): assumes SmoothTriple on LocalRankDefect.positiveDomain for c.base
  - quote: `(hbc : SmoothTriple (LocalRankDefect.positiveDomain U.carrier) c.base)`

## 80. Proposition 8.1 · `CorrectionStep.meanCoefficientValue_eq_meanResidual`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes U is open.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state an open set U.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([LiftedMeanResidual.lean:821](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/LiftedMeanResidual.lean#L821)): The Lean theorem assumes H.isOpen : IsOpen U.
  - quote: `isOpen : IsOpen U`

## 81. Proposition 8.1 · `CorrectionStep.meanCoefficientValue_eq_meanResidual`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes zero angular mean of oscillatory pressure.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper states zero angular mean for w but does not state zero angular mean for oscillatory pressure.
  - quote (on the cited page: exact; in the text shown to the model: exact): `and $\langle w \rangle_{\theta} = 0$`
- **Lean** ([LiftedMeanResidual.lean:834](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/LiftedMeanResidual.lean#L834)): The Lean theorem assumes H.oscillatoryPressure_mean_zero.
  - quote: `oscillatoryPressure_mean_zero : ∀ n x, x ∈ U → CorrectionState.angularAverage u.oscillatoryPressure n x = 0`

## 82. Proposition 8.1 · `CorrectionStep.meanCoefficientValue_eq_meanResidual`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes the lifted base is divergence-free.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement says u has a divergence-free decomposition but does not separately state base divergence-free.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([LiftedMeanResidual.lean:835-837](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/LiftedMeanResidual.lean#L835-L837)): The Lean theorem assumes H.base_divergence.
  - quote: `base_divergence : ∀ n p, p ∈ cylinder U → realDivergence`

## 83. Proposition 8.1 · `CorrectionStep.meanCoefficientValue_eq_meanResidual`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes frame regularity.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state regularity of the context frame.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([HarmonicResidual.lean:1465](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/HarmonicResidual.lean#L1465)): The Lean theorem assumes h.frame.
  - quote: `frame : (contextFrame c n).Regular U`

## 84. Proposition 8.1 · `CorrectionStep.meanCoefficientValue_eq_meanResidual`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes block regularity.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state regularity of each harmonic block.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([HarmonicResidual.lean:1469](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/HarmonicResidual.lean#L1469)): The Lean theorem assumes h.blocks.
  - quote: `blocks : ∀ l ∈ labels n, (ofBlock (blockFamily l) (gaussianCoeffs l) (aliasCoeffs l) n).Regular U`

## 85. Proposition 8.1 · `CorrectionStep.meanCoefficientValue_eq_meanResidual`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean statement assumes disjoint block time supports.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state disjoint time supports for distinct blocks.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([HarmonicResidual.lean:1472-1473](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/HarmonicResidual.lean#L1472-L1473)): The Lean theorem assumes h.disjoint.
  - quote: `disjoint : ∀ l ∈ labels n, ∀ j ∈ labels n, l ≠ j →`

## 86. Proposition 8.1 · `MeanResidual.exact_mean_balances`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration explicitly assumes smoothness, while the paper statement does not display that regularity assumption.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The proposition text does not explicitly assume C-infinity regularity.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([MeanResidual.lean:936-938](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanResidual.lean#L936-L938)): Lean assumes ContDiff ℝ ∞ for the listed fields.
  - quote: `(hb : ∀ i, ContDiff ℝ ∞ (b i)) (hm : ∀ i, ContDiff ℝ ∞ (m i))`

## 87. Proposition 8.1 · `MeanResidual.exact_mean_balances`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration explicitly assumes an average-pressure decomposition, while the paper statement does not display that equality.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper introduces p_m as a pressure correction but does not explicitly state the average pressure decomposition.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $p_m$ be its angularly invariant pressure correction`
- **Lean** ([MeanResidual.lean:941](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanResidual.lean#L941)): Lean assumes hpavg, namely average p = pb + pm.
  - quote: `(hpavg : average p = fun q => pb q + pm q)`

## 88. Proposition 8.1 · `MeanResidual.exact_mean_balances`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration explicitly assumes the base velocity is divergence-free, while the paper text does not display that base divergence condition.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper says u has a divergence-free decomposition but does not explicitly state divergence b = 0 in the proposition text.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([MeanResidual.lean:943](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanResidual.lean#L943)): Lean assumes hbdiv, namely divergence b = 0 where radius is positive.
  - quote: `(hbdiv : ∀ y, 0 < radius y → divergence b y = 0)`

## 89. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires an open set S; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not mention an open set S.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:618](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L618)): The Lean theorem assumes S : Set ℝ and hS : IsOpen S.
  - quote: `{S : Set ℝ} (hS : IsOpen S)`

## 90. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration imposes a smallness and positivity range on h; the paper statement does not state it.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state a range for h.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:619](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L619)): The Lean theorem assumes 0 < h < 1/2.
  - quote: `{h : ℝ} (hh : 0 < h) (hh1 : h < 1 / 2)`

## 91. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration is stated for finite-profile data N, C, f; the paper statement does not mention these formal parameters.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not mention finite truncation parameters N, C, or SlowProfiles f.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:619](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L619)): The Lean theorem takes N, C, and f as parameters.
  - quote: `(N : ℕ) (C : ℝ) (f : SlowProfiles)`

## 92. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires smoothness of thetaDensity coefficients on region S; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state Smooth support for thetaDensity coefficients.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:620](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L620)): The Lean theorem assumes hTheta for all n ≤ N.
  - quote: `(hTheta : ∀ n ≤ N, SlowStressSupport.Smooth S (thetaDensity h C f n))`

## 93. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires smoothness of zDensity coefficients on region S; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state Smooth support for zDensity coefficients.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:621](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L621)): The Lean theorem assumes hZ for all n ≤ N.
  - quote: `(hZ : ∀ n ≤ N, SlowStressSupport.Smooth S (zDensity h f n))`

## 94. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires ContDiffAt ℝ 2 for f.flux n; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state C^2 regularity for flux coefficients at the inner profile point.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:624](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L624)): The Lean theorem assumes hv.
  - quote: `(hv : ∀ n ≤ N, ContDiffAt ℝ 2 (f.flux n) (SimilarityProfile.inner h (profilePoint t x)))`

## 95. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires ContDiffAt ℝ 2 for f.phi n; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state C^2 regularity for phi coefficients at the inner profile point.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:625](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L625)): The Lean theorem assumes hphi.
  - quote: `(hphi : ∀ n ≤ N, ContDiffAt ℝ 2 (f.phi n) (SimilarityProfile.inner h (profilePoint t x)))`

## 96. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires ContDiffAt ℝ 2 for f.axial n; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state C^2 regularity for axial coefficients at the inner profile point.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:626](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L626)): The Lean theorem assumes hu.
  - quote: `(hu : ∀ n ≤ N, ContDiffAt ℝ 2 (f.axial n) (SimilarityProfile.inner h (profilePoint t x)))`

## 97. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration requires DifferentiableAt for f.pressure n; the paper statement does not state this.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state differentiability of pressure coefficients at the inner profile point.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let u have the divergence-free decomposition (8.1)`
- **Lean** ([SlowResidualMatching.lean:627](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L627)): The Lean theorem assumes hp.
  - quote: `(hp : ∀ n ≤ N, DifferentiableAt ℝ (f.pressure n) (SimilarityProfile.inner h (profilePoint t x)))`

## 98. Proposition 8.1 · `SlowResidualMatching.navierStokesResidual_eq_stress_add_truncation`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration assumes vanishing pressure coefficients; the paper statement does not state this condition.
- **Paper** ([p.89](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=89), Proposition 8.1): The paper statement does not state that the pressure coefficients vanish.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $p_m$ be its angularly invariant pressure correction`
- **Lean** ([SlowResidualMatching.lean:628](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SlowResidualMatching.lean#L628)): The Lean theorem assumes hpressure : ∀ n ≤ N, pressureCoefficient h C f n ... = 0.
  - quote: `(hpressure : ∀ n ≤ N, pressureCoefficient h C f n (SimilarityProfile.inner h (profilePoint t x)) = 0)`

## 99. Proposition 8.3 · `MeanChartCompatibility.physicalPressure_naturality`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Periodicity is an explicit Lean hypothesis but not an explicit paper clause.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(i)): the paper does not explicitly state torus periodicity in this excerpt
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `For a smooth shell-supported scalar source $g_r(R, Z, T, y)$`
- **Lean** ([MeanChartCompatibility.lean:765](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L765)): the Lean theorem assumes TorusPeriodicLift f
  - quote: `(hf : ContDiff ℝ ∞ f) (hp : PressureStream.TorusPeriodicLift f)`

## 100. Proposition 8.3 · `PhysicalMeanDomain.meanClass_meanPressure`

- **Type:** missing-hypothesis · likely explanation (heuristic): `parameter-set-uniformity` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean includes an open slow-parameter set U that is not explicit in the paper sentence.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), (i)): The paper does not state an open set U or its openness.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `For a smooth shell-supported scalar source $g_r(R, Z, T, y)$`
- **Lean** ([PhysicalMeanDomain.lean:1024](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1024)): Lean assumes U : Set S and IsOpen U.
  - quote: `(U : Set S) (hU : IsOpen U)`

## 101. Proposition 8.3 · `PhysicalMeanDomain.meanClass_meanPressure`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean includes weight and scale sequence hypotheses not present in the paper sentence.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), (i)): The paper does not state sequences ε and L with 0 < ε n ≤ 1 and L n ≥ 1.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `For a smooth shell-supported scalar source $g_r(R, Z, T, y)$`
- **Lean** ([PhysicalMeanDomain.lean:1023](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1023)): Lean assumes ε L : ℕ → ℝ and these inequalities.
  - quote: `(ε L : ℕ → ℝ) (hε : ∀ n, 0 < ε n) (hεone : ∀ n, ε n ≤ 1) (hL : ∀ n, 1 ≤ L n)`

## 102. Proposition 8.3 · `PhysicalMeanDomain.meanClass_pressureMass`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean's statement lives in a normed-space context; the paper statement does not display this.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The paper does not state normed-space structure for S.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.3`
- **Lean** ([PhysicalMeanDomain.lean:25](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L25)): The Lean section context gives S a normed-space structure.
  - quote: `variable {S V : Type} [NormedAddCommGroup S] [NormedSpace ℝ S]`

## 103. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamGamma`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** These are explicit Lean hypotheses not present in the paper statement.
- **Paper** ([p.93](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=93), (8.14)): The paper uses ε in Δβ but does not state sequence bounds for ε or L.
  - quote (on the cited page: normalized; in the text shown to the model: normalized): `$\Delta \beta = -\varepsilon \partial_Z \Psi_*$`
- **Lean** ([PhysicalMeanDomain.lean:1618](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1618)): The declaration assumes ε n > 0, ε n ≤ 1, and L n ≥ 1.
  - quote: `(ε L : ℕ → ℝ) (hε : ∀ n, 0 < ε n) (hεone : ∀ n, ε n ≤ 1) (hL : ∀ n, 1 ≤ L n)`

## 104. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamPotential`

- **Type:** missing-hypothesis · likely explanation (heuristic): `parameter-set-uniformity` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration is local to an open slow-parameter set U, whereas the paper statement is not expressed with an explicit open set U.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): The paper does not state an open set U of slow parameters.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `at every $(Z, T)$.`
- **Lean** ([PhysicalMeanDomain.lean:1568](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1568)): U : Set S and IsOpen U are assumed.
  - quote: `(U : Set S) (hU : IsOpen U)`

## 105. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamPotential`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean theorem makes strip and cutoff parameters and their positivity/ordering hypotheses explicit, while the paper item refers only to Lemma 8.2 and the bump.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The paper statement does not explicitly list real parameters a, b, d, cL, cR with 0<a<b, 0<d, 0<cL, 0<cR.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix the radial operators of Lemma 8.2 and the bump $\rho$ above.`
- **Lean** ([PhysicalMeanDomain.lean:1566](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1566)): These parameters and inequalities are explicit hypotheses.
  - quote: `(ha : 0 < a) (hab : a < b) (hd : 0 < d) (hcL : 0 < cL) (hcR : 0 < cR)`

## 106. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamPotential`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean theorem assumes scale and cutoff sequences with explicit bounds, which are not stated in the paper item.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The paper statement does not explicitly assume sequences ε and L with 0<ε n≤1 and 1≤L n.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix the radial operators of Lemma 8.2 and the bump $\rho$ above.`
- **Lean** ([PhysicalMeanDomain.lean:1567](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1567)): These sequences and bounds are explicit hypotheses.
  - quote: `(ε L : ℕ → ℝ) (hε : ∀ n, 0 < ε n) (hεone : ∀ n, ε n ≤ 1) (hL : ∀ n, 1 ≤ L n)`

## 107. Proposition 8.3 · `PhysicalMeanDomain.meanClass_streamPotential`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean theorem has additional gauge or scaling sequence parameters M and v that are not explicitly listed in the paper statement.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): The paper defines Psi using (8.4) but does not list M and v as hypotheses in Proposition 8.3.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `using (8.4)`
- **Lean** ([PhysicalMeanDomain.lean:1572](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L1572)): M : ℕ → ℝ and v : ℕ → PressureStream.Plane are explicit arguments used in streamPotential.
  - quote: `(M : ℕ → ℝ) (v : ℕ → PressureStream.Plane)`

## 108. Proposition 8.3 · `PressureStream.meanPressure_bar_hasDerivAt`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration includes an explicit torus-periodicity hypothesis.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): the paper item does not explicitly state torus periodicity of the source.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `For a smooth shell-supported scalar source $g_r(R, Z, T, y)$`
- **Lean** ([PressureStream.lean:700](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PressureStream.lean#L700)): the theorem assumes TorusPeriodicLift f.
  - quote: `(hp : TorusPeriodicLift f)`

## 109. Proposition 8.3 · `TemporalMeanUpdate.temporal_mean_update`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration includes explicit positivity and ordering assumptions on the radial interval and parameter d that are not stated in the paper item.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The proposition statement does not explicitly assume 0 < a, a < b, and 0 < d.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.3.`
- **Lean** ([TemporalMeanUpdate.lean:818](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TemporalMeanUpdate.lean#L818)): The theorem assumes ha : 0 < a, hab : a < b, and hd : 0 < d.
  - quote: `(ha : 0 < a) (hab : a < b) (hd : 0 < d)`

## 110. Proposition 8.3 · `VariableGaugeMean.reconstructState_radial_identity`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement is pointwise and includes an explicit membership hypothesis for the slow variable.
- **Paper** ([p.93](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=93), (8.13)): The paper does not state a pointwise condition z.2.1 ∈ U.carrier.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Then`
- **Lean** ([VariableGaugeMean.lean:2932](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2932)): The Lean requires `hz : z.2.1 ∈ U.carrier`.
  - quote: `hz : z.2.1 ∈ U.carrier`

## 111. Proposition 8.3 · `VariableGaugeMean.temporalAxialDifference_eq_dividedAlias`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean declaration has an explicit periodicity hypothesis; the paper sentence does not explicitly state one.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), (ii)): The paper statement does not explicitly state a periodicity condition in the auxiliary variable Y.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `Let $\gamma_d(R, Z, T, y)$ be a smooth shell-supported desired axial increment`
- **Lean** ([VariableGaugeMean.lean:2946](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2946)): The Lean declaration assumes PhysicalMeanDomain.PeriodicOn U.carrier (u.axialResidual c n).
  - quote: `(hp : PhysicalMeanDomain.PeriodicOn U.carrier (u.axialResidual c n))`

## 112. Proposition 8.3 · `VariableGaugeMean.temporalIncrementState_classes`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean identifies the context operator epsilon with the section epsilon.
- **Paper** ([p.93](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=93), (8.14)): the paper uses epsilon in the definition of Delta beta but does not state an equality with a context operator epsilon
  - quote (on the cited page: normalized; in the text shown to the model: normalized): `$\Delta \beta = -\varepsilon \partial_Z \Psi_*$`
- **Lean** ([VariableGaugeMean.lean:2842](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2842)): Lean assumes heps : c.operators.epsilon = ε
  - quote: `(heps : c.operators.epsilon = ε)`

## 113. Proposition 8.3 · `VariableGaugeMean.temporalIncrementState_classes`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** Lean adds an explicit periodicity hypothesis.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): the paper statement does not explicitly assert a periodicity predicate for gamma_d
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `Let $\gamma_d(R, Z, T, y)$ be a smooth shell-supported desired axial increment`
- **Lean** ([VariableGaugeMean.lean:2846](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2846)): Lean assumes axial residual is periodic
  - quote: `(hpz : ∀ n, PhysicalMeanDomain.PeriodicOn U.carrier (u.axialResidual c n))`

## 114. Proposition 8.3 · `VariableGaugeMean.temporalIncrementState_supportedGauge`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement has an explicit periodicity hypothesis that is not stated in the paper sentence.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), (i) Pressure): The paper statement says the source is smooth and shell-supported but does not state a periodicity hypothesis on the Lean residual.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `For a smooth shell-supported scalar source $g_r(R, Z, T, y)$`
- **Lean** ([VariableGaugeMean.lean:2978](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2978)): The Lean statement assumes PeriodicOn U.carrier (u.axialResidual c n).
  - quote: `(hp : PhysicalMeanDomain.PeriodicOn U.carrier (u.axialResidual c n))`

## 115. Proposition 8.3 · `VariableGaugeMean.temporalIncrementState_supportedGauge`

- **Type:** missing-hypothesis · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement has a support hypothesis for u.thetaResidual c n that is not named in the paper support sentence.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The paper support sentence does not mention a theta residual function.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `The pressure and vector potential are compactly supported in the active shell and retain the projection of the source support to $(Z,T)$.`
- **Lean** ([VariableGaugeMean.lean:2980](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2980)): The Lean statement assumes SupportedGauge for u.thetaResidual c n.
  - quote: `(hsθ : SupportedGauge g.radial.inner g.radial.outer (qLength coord) U.carrier (u.thetaResidual c n))`

## 116. Proposition 8.4 · `CorrectionInitializationNoOptions.MovingInitialization.zeroMean_debt_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration includes an operator-bounds hypothesis that is not stated in the paper item.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper does not state an OperatorBounds hypothesis with ChartScales.kappa.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.4.`
- **Lean** ([CorrectionInitializationNoOptions.lean:2197-2198](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/CorrectionInitializationNoOptions.lean#L2197-L2198)): The Lean declaration assumes ho : OperatorBounds ... ChartScales.kappa.
  - quote: `(ho : OperatorBounds (movingStripData U a b cL cR ha hcL hcR ε L hε hεone hL)`

## 117. Proposition 8.4 · `CorrectionInitializationNoOptions.MovingInitialization.zeroMean_debt_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration includes a local-operators hypothesis that is not stated in the paper item.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper does not state a LocalRankDefect.LocalOperators hypothesis.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.4.`
- **Lean** ([CorrectionInitializationNoOptions.lean:2199](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/CorrectionInitializationNoOptions.lean#L2199)): The Lean declaration assumes hop : LocalRankDefect.LocalOperators U.carrier c.operators.
  - quote: `(hop : LocalRankDefect.LocalOperators U.carrier c.operators)`

## 118. Proposition 8.4 · `CorrectionInitializationNoOptions.MovingInitialization.zeroMean_debt_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration assumes a weighted mean-class condition on covariance components.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper does not state MeanClass hypotheses for covariance components.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.4.`
- **Lean** ([CorrectionInitializationNoOptions.lean:2201-2202](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/CorrectionInitializationNoOptions.lean#L2201-L2202)): The Lean declaration assumes hW : ∀ i j, MeanClass ... 1 (u.covariance i j).
  - quote: `(hW : ∀ i j, MeanClass (movingStripData U a b cL cR ha hcL hcR ε L hε hεone hL)`

## 119. Proposition 8.4 · `CorrectionInitializationNoOptions.MovingInitialization.zeroMean_debt_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration assumes infinite differentiability on the slow domain for covariance components.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper does not state ContDiffOn hypotheses for covariance components.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.4.`
- **Lean** ([CorrectionInitializationNoOptions.lean:2203-2204](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/CorrectionInitializationNoOptions.lean#L2203-L2204)): The Lean declaration assumes hWc : ∀ i j n, ContDiffOn ℝ ∞ (u.covariance i j n) ...
  - quote: `(hWc : ∀ i j n, ContDiffOn ℝ ∞ (u.covariance i j n)`

## 120. Proposition 8.4 · `CorrectionInitializationNoOptions.MovingInitialization.zeroMean_debt_mem`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The Lean declaration assumes a supported-gauge condition for covariance components.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper does not state SupportedGauge hypotheses for covariance components.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Proposition 8.4.`
- **Lean** ([CorrectionInitializationNoOptions.lean:2205](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/CorrectionInitializationNoOptions.lean#L2205)): The Lean declaration assumes hWs : ∀ i j n, SupportedGauge a b (qLength coord) U.carrier (u.covariance i j n).
  - quote: `(hWs : ∀ i j n, SupportedGauge a b (qLength coord) U.carrier (u.covariance i j n))`

## 121. Proposition 8.4 · `MeanChartCompatibility.stateDebt_eq_sourceDebt`

- **Type:** missing-hypothesis · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean context carries normed-space typeclass assumptions on S that are not part of the paper's stated hypotheses.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper statement does not state normed vector space structure on a type S.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $(\beta, \nu, \gamma)$ and w be the smooth shell-supported corrections of (8.1).`
- **Lean** ([MeanChartCompatibility.lean:1200](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1200)): The Lean section variables include NormedAddCommGroup S and NormedSpace ℝ S for S.
  - quote: `[NormedAddCommGroup S] [NormedSpace ℝ S]`

## 122. (10.15) in proof of Lemma 10.5 · `ConservativeDifference.conservative_difference_equation`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper's setting is a whole time interval; the Lean statement is pointwise in time and space and componentwise.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): The paper fixes T<1 and works on R^3 x [0,T].
  - quote (on the cited page: exact; in the text shown to the model: exact): `Fix $T < 1$. If $v, P$ is a smooth solution of (1.1) at viscosity one on $\mathbb{R}^3 \times [0, T]$`
- **Lean** ([R3/ConservativeDifference.lean:138](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/ConservativeDifference.lean#L138)): The Lean theorem is at a single t : ℝ, x : Space, and component k : Fin 3.
  - quote: `{t : ℝ} {x : Space}`

## 123. (8.23) in proof of Lemma 8.6 · `TemporalMeanUpdate.absoluteInverse_coverMap`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses the torus as the domain, while the Lean declaration uses the universal cover Plane.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The operator N is stated on the 2-torus.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $N = v_t \cdot \partial_y$ on $\mathbb{T}^2$`
- **Lean** ([TemporalMeanUpdate.lean:246](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TemporalMeanUpdate.lean#L246)): The theorem is stated for f : Plane → ℂ.
  - quote: `{f : Plane → ℂ}`

## 124. (8.23) in proof of Lemma 8.6 · `TemporalMeanUpdate.temporalInverse_coverMap`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper's domain is the torus, while Lean uses PressureStream.Lift S and an explicit periodicity condition.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The paper places F on T^2.
  - quote (on the cited page: exact; in the text shown to the model: exact): `on $\mathbb{T}^2$`
- **Lean** ([TemporalMeanUpdate.lean:525](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TemporalMeanUpdate.lean#L525)): The Lean function is a lift S function with a torus periodic lift hypothesis.
  - quote: `{f : PressureStream.Lift S → ℝ}`

## 125. (8.23) in proof of Lemma 8.6 · `VariableGaugeMean.temporalAtIndex_fast_cancellation_on`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The underlying function space and domain differ between the paper's torus/charts and Lean's lifted physical domain.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), Lemma 8.6): The paper works on the auxiliary torus T^2 and chart maps J_g, with F a function of Y.
  - quote (on the cited page: exact; in the text shown to the model: exact): `Let $N = v_t \cdot \partial_y$ on $\mathbb{T}^2$, with $v_t$ as in (6.2)`
- **Lean** ([VariableGaugeMean.lean:2558](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2558)): The Lean theorem works with f : PressureStream.Lift S → ℝ on slowDomain U over an open set U in S.
  - quote: `{f : PressureStream.Lift S → ℝ}`

## 126. (8.9) in proof of Lemma 8.2 · `RadialPullback.physicalCompact_eq_radialIntegral`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper's displayed half-line integrals are over the negative and positive u-axes, while the Lean conclusion uses finite radial intervals.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.9)): A_- and A_+ are defined by integrals over u in (-∞,0) and (0,∞).
  - quote (on the cited page: exact; in the text shown to the model: exact): `$$A_{-}(U,y) = \int_{-\infty}^{0} F(U+u,y+Muv_{r}) du,$$`
- **Lean** ([RadialPullback.lean:363](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L363)): The conclusion uses integrals over s in a..z.1 and s in a..b.
  - quote: `∫ s in a..z.1, g (s, z.2 + (M * (s ^ d - z.1 ^ d)) • v)`

## 127. Lemma 10.5 · `WholeSpaceUniqueness.candidate_unique_on_Icc`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The time domain for the equation is stated as the closed interval in the paper and the open interval in Lean.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): The paper says v, P is a smooth solution on R3 x [0,T].
  - quote (on the cited page: exact; in the text shown to the model: exact): `If $v, P$ is a smooth solution of (1.1) at viscosity one on $\mathbb{R}^3 \times [0, T]$`
- **Lean** ([R3/WholeSpaceUniqueness.lean:79](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/WholeSpaceUniqueness.lean#L79)): Lean assumes the residual equation only for t in Ioo (0,T).
  - quote: `∀ t ∈ Ioo (0 : ℝ) T, ∀ x, navierStokesResidual 1 v q t x = f (t, x)`

## 128. Lemma 8.2 · `RadialPullback.supported_meanClass_physicalCompact`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean records radial support but does not record the paper's support restriction in the slow variables.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper concludes T_e f is supported in the active radial shell and in the projection of the input support to (Z,T).
  - quote (on the cited page: exact; in the text shown to the model: exact): `supported in the same active radial shell and in the projection of the input support to $(Z, T)$`
- **Lean** ([RadialPullback.lean:852](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/RadialPullback.lean#L852)): The Lean conclusion only says F is RadiallySupported a b, i.e. supported in the radial interval [a,b].
  - quote: `(∀ n, RadialAlias.RadiallySupported a b (F n))`

## 129. Lemma 8.2 · `VariableGaugeMean.compactPrimitive_radial_identity`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The domains and variable roles in the regularity assumptions are stated differently.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): The paper's derivative hypothesis concerns derivatives in (R,Z,T,y) of the smooth zero extension.
  - quote (on the cited page: exact; in the text shown to the model: exact): `for every fixed multi-index I of derivatives in $(R, Z, T, y)$`
- **Lean** ([VariableGaugeMean.lean:2116](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2116)): The Lean smoothness hypothesis is ContDiffOn on PhysicalMeanDomain.slowDomain U.carrier.
  - quote: `ContDiffOn ℝ ∞ f (PhysicalMeanDomain.slowDomain U.carrier)`

## 130. Lemma 8.7 · `MeanLocalDefectBounds.rankStage_defect_class`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** The paper names a reserved interior interval, while the Lean statement uses a local slow strip data object based on U.carrier.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper works on the reserved interior interval I_m.
  - quote (on the cited page: exact; in the text shown to the model: exact): `on the reserved interior interval $I_m$`
- **Lean** ([MeanLocalDefectBounds.lean:249](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L249)): The Lean conclusion is stated on PhysicalMeanDomain.localSlowStripData U.carrier ...
  - quote: `PhysicalMeanDomain.localSlowStripData U.carrier U.isOpen ε L hε hεone hL`

## 131. Lemma 8.7 · `MeanRankUpdate.actual_rank_stream_identities`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The two sides describe the domain of quantification using different geometric bounds.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper states the result on the reserved interior interval I_m.
  - quote (on the cited page: exact; in the text shown to the model: exact): `reserved interior interval $I_m$`
- **Lean** ([MeanRankUpdate.lean:1949-1952](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanRankUpdate.lean#L1949-L1952)): The Lean result is quantified over p in s.domain with p.1 in Icc lo hi and chartQ in Icc qlo qhi.
  - quote: `(hR : ∀ p ∈ s.domain, p.1 ∈ Icc lo hi)`

## 132. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_eq_formula`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement is localized to U, while the paper refers to the active shell/support.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper locates the correction in the active shell and does not name an open set U.
  - quote (on the cited page: exact; in the text shown to the model: exact): `supported in the active shell`
- **Lean** ([DefectIncrementBounds.lean:406](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L406)): The Lean conclusion is an Agree on an open set U.
  - quote: `Agree U (actualRadialError o base m h W) (radialRemainder o base m h)`

## 133. Lemma 8.8 · `MeanLocalDefectBounds.rankStage_gain_of_targets`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The Lean statement specifies different strip-data objects for the radial error and the defect components.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): states the final estimates in M and S without naming the formal strip data
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `$\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([MeanLocalDefectBounds.lean:318-322](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L318-L322)): actualRadialError is in MeanClass on movingStripData, while debt is in UnweightedClass on localSlowStripData
  - quote: `MeanClass (movingStripData U g.radial.inner g.radial.outer cL cR ha hcL hcR ε L hε hεone hL)
      (H + 9 / 10 - 2 * κ)
      (actualRadialError c.operators c.base u.mean (rankIncrementState g r axial c u) u.covariance) ∧
    ∀ i : Fin 3, UnweightedClass (PhysicalMeanDomain.localSlowStripData U.carrier U.isOpen ε L hε hεone hL)`

## 134. Proposition 8.3 · `MeanChartCompatibility.physicalPressure_naturality`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 2/3
- **Difference:** Lean specifies a scaled closed interval; the paper uses informal shell support.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(i)): the paper assumes smooth shell support
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `smooth shell-supported scalar source`
- **Lean** ([MeanChartCompatibility.lean:766](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L766)): the Lean theorem assumes RadiallySupported in [chartScale n * a, chartScale n * b]
  - quote: `(hs : RadialAlias.RadiallySupported (chartScale n * a) (chartScale n * b) f) :`

## 135. Proposition 8.3 · `PressureStream.reconstructed_divergence_zero`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses explicit coordinate variables; Lean uses an abstract normed auxiliary space E.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3 (ii)): γ_d is written as a function of R,Z,T,y.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `Let $\gamma_d(R, Z, T, y)$`
- **Lean** ([PressureStream.lean:741](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PressureStream.lean#L741)): γd is a function on ℝ × E.
  - quote: `{γd : ℝ × E → ℝ}`

## 136. Proposition 8.3 · `VariableGaugeMean.reconstructState_radial_identity`

- **Type:** different-domain · likely explanation (heuristic): `naming` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper’s smoothness statement is phrased as smooth shell-supported; the Lean regularity is stated on a named slow domain.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The paper assumes a smooth shell-supported scalar source.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `For a smooth shell-supported scalar source $g_r(R, Z, T, y)$`
- **Lean** ([VariableGaugeMean.lean:2930](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2930)): The Lean assumes `ContDiffOn ℝ ∞` on `slowDomain U.carrier`.
  - quote: `hf : ContDiffOn ℝ ∞ (u.gr c n) (PhysicalMeanDomain.slowDomain U.carrier)`

## 137. Proposition 8.3 · `VariableGaugeMean.reconstructState_radial_identity`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The paper uses the phrase shell-supported; the Lean uses an explicit supported-gauge predicate.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3): The paper says the source is shell-supported.
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `smooth shell-supported`
- **Lean** ([VariableGaugeMean.lean:2931](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2931)): The Lean encodes support by `SupportedGauge` with `qLength coord` and `U.carrier`.
  - quote: `hs : SupportedGauge g.radial.inner g.radial.outer (qLength coord) U.carrier (u.gr c n)`

## 138. Proposition 8.3 · `VariableGaugeMean.temporalIncrementState_classes`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The regularity domain is specified by a Lean predicate on the slow domain.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): the paper says gamma_d is smooth and shell-supported
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `Let $\gamma_d(R, Z, T, y)$ be a smooth shell-supported desired axial increment`
- **Lean** ([VariableGaugeMean.lean:2844](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2844)): Lean requires ContDiffOn ∞ on PhysicalMeanDomain.slowDomain U.carrier
  - quote: `(hz : ∀ n, ContDiffOn ℝ ∞ (u.axialResidual c n) (PhysicalMeanDomain.slowDomain U.carrier))`

## 139. Proposition 8.3 · `VariableGaugeMean.temporalIncrementState_classes`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The support condition is formalized by a different predicate.
- **Paper** ([p.92](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=92), Proposition 8.3(ii)): the paper says gamma_d is shell-supported
  - quote (on the cited page: unresolved-OCR; in the text shown to the model: exact): `Let $\gamma_d(R, Z, T, y)$ be a smooth shell-supported desired axial increment`
- **Lean** ([VariableGaugeMean.lean:2847](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/VariableGaugeMean.lean#L2847)): Lean requires SupportedGauge with g.radial.inner, g.radial.outer, qLength coord, and U.carrier
  - quote: `(hsz : ∀ n, SupportedGauge g.radial.inner g.radial.outer (qLength coord) U.carrier (u.axialResidual c n))`

## 140. Proposition 8.4 · `MeanChartCompatibility.stateDebt_eq_sourceDebt`

- **Type:** different-domain · likely explanation (heuristic): `needs-translation` · reported by 3/3 samples, confirmed the same difference by 3/3 adjudication samples · declaration located by 3/3
- **Difference:** The parameter spaces used by the two statements are different.
- **Paper** ([p.94](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=94), Proposition 8.4): The paper's hypotheses are stated at every (Z,T).
  - quote (on the cited page: exact; in the text shown to the model: exact): `vanish at every $(Z,T)$`
- **Lean** ([MeanChartCompatibility.lean:1259](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanChartCompatibility.lean#L1259)): The Lean theorem is stated for n : ℕ and s : S.
  - quote: `(n : ℕ) (s : S)`
