# Review shortlist

Differences between the paper and the Lean formalization that may deserve an expert's attention, selected mechanically: reported by all 3 independent samples and concerning what is estimated (bound, norm, or uniformity), plus the hits on the two published discrepancies. **Nothing here has been reviewed by a mathematician; each entry is a difference in wording, not a claimed error.** Full data: `out/differences.csv`; method: `METHODOLOGY.md`.

## 1. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** stronger-bound · reported by 3/3 samples
- **Difference:** The paper loses four derivatives, while the Lean declaration loses five.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper bounds N^{-1}F in C_y^m by C_m times the C_y^{m+4} norm of F.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$.`
- **Lean** ([SmoothFamilyTorusInverse.lean:868](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L868)): The Lean theorem assumes a JetBound of order n+5 and concludes a JetBound of order n.
  - quote: `JetBound f S (n + 5) C → JetBound (inverse d f) S n (K * C)`

## 2. Lemma 8.6 · `TorusInverse.zero_mean_series_has_smooth_inverse`

- **Type:** stronger-bound · reported by 3/3 samples
- **Difference:** The paper's displayed derivative-loss bound is absent from the Lean declaration.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper states the estimate for every integer m ≥ 0.
  - quote: `\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}.$$ (8.19)`
- **Lean** ([TorusInverse.lean:588-592](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TorusInverse.lean#L588-L592)): The Lean theorem states no C^m norm estimate.
  - quote: `∃ u : Torus → ℂ, Continuous u ∧ (∫ z, u z ∂torusMeasure) = 0 ∧`

## 3. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper's norm is written as a C_y norm, while Lean's JetBound is a full joint Fréchet-jet bound on a parameter set.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper uses the C_y^m norm.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): Lean uses JetBound, a bound on iterated Fréchet derivatives up to order n over p in S and all Y.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 4. Lemma 8.7 · `PositiveOrderMoments.exists_parameterized_exact_repair`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper measures regularity with S_alpha/M_alpha classes, while the Lean statement uses C^∞ smoothness on univ ×ˢ S.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper uses regularity classes S_alpha and M_alpha.
  - quote: `targets in $S_{\alpha}$give increments in $M_{\alpha}$`
- **Lean** ([PositiveOrderMoments.lean:926](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PositiveOrderMoments.lean#L926)): The Lean statement uses ContDiffOn ℝ ∞ smoothness.
  - quote: `ContDiffOn ℝ ∞ du (univ ×ˢ S) ∧ ContDiffOn ℝ ∞ de (univ ×ˢ S)`

## 5. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_mem`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses the class M; the Lean declaration uses MeanClass, which is defined as MemClass with weight s.zeta.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper concludes R_g ∈ M_{α+0.9-2κ_s}.
  - quote: `\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:439](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L439)): The Lean declaration concludes MeanClass s (H + 9/10 - 2κ) (actualRadialError o base m h W).
  - quote: `MeanClass s (H + 9 / 10 - 2 * κ) (actualRadialError o base m h W)`

## 6. Lemma 8.8 · `DefectIncrementBounds.defects_after_rank_mem`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses the symbol S for the target class, while the Lean statement uses an unweighted slow-strip MemClass.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The updated defects are stated to belong to S_{alpha + 0.9 - 2 kappa_s}.
  - quote: `(\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:569-570](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L569-L570)): The i-th updated defect is stated to belong to UnweightedClass slowStripData with exponent H + 9/10 - 2*kappa.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS) (H + 9 / 10 - 2 * κ)`

## 7. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses S-class notation for the defect triple; Lean uses an explicit unweighted slow-strip class for a debt component.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The new defect triple is stated to belong to S_{α+0.9-2κ_s}.
  - quote: `$$\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}, \qquad (\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}.$$`
- **Lean** ([DefectIncrementBounds.lean:857](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L857)): The i-th debt row is stated to belong to UnweightedClass on slowStripData with exponent H + 9/10 - 2κ.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS)`

## 8. Lemma 8.8 · `MeanLocalDefectBounds.rankStage_gain_of_targets`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper's S class is formalized in Lean as an UnweightedClass.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The three targets belong to S_α.
  - quote: `and the three targets belong to $S_{\alpha}$ for $\alpha \ge 0.9$`
- **Lean** ([MeanLocalDefectBounds.lean:315-317](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L315-L317)): The three current debts are assumed to lie in UnweightedClass H.
  - quote: `UnweightedClass (PhysicalMeanDomain.localSlowStripData U.carrier U.isOpen ε L hε hεone hL)`

## 9. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples
- **Difference:** Lean takes a uniform bound over the set S; the paper statement does not display such a set.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The displayed estimate does not explicitly quantify over a parameter set S.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): JetBound is uniform for all p in S.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`
