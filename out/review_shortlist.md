# Review shortlist

Differences between the paper and the Lean that are probably most worth an expert's time, picked by a fixed rule rather than by judgment. **No mathematician has reviewed these yet. Each one is a place where the two say different things, not a claimed error.** All the data is in `out/differences.csv`, and the method is in `METHODOLOGY.md`.

**How the targets were chosen.** Section 8 was the pilot. Lemmas 8.6 and 10.5 were added because Bastounis, Circelli and Hansen (arXiv:2610.08144) had already found discrepancies there, and the proof-level targets only cover the proofs of Lemmas 8.2, 8.6 and 10.5. The prompts never mention those discrepancies, but they did decide where the tool looked.

## Part A: differences in what is estimated

Every difference that all 3 samples reported as stronger-bound, weaker-bound or missing-supremum, plus the known discrepancies used to validate the tool (marked **validation**).

## 1. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.applyMultiplier_finiteJets`

- **Type:** stronger-bound · reported by 3/3 samples · declaration located by 2/3
- **Difference:** For corresponding output orders, the paper requires three derivatives beyond the multiplier order while the Lean statement requires four derivatives beyond l.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The input regularity is C^{m+p+3}_y.
  - quote: `C^{m+p+3}_y`
- **Lean** ([SmoothFamilyTorusInverse.lean:851](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L851)): The input finite jet bound is of order n+l+4.
  - quote: `JetBound f S (n + l + 4) C`

## 2. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets` · **validation**

- **Type:** stronger-bound · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper loses four derivatives, while the Lean declaration loses five.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper bounds N^{-1}F in C_y^m by C_m times the C_y^{m+4} norm of F.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$.`
- **Lean** ([SmoothFamilyTorusInverse.lean:868](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L868)): The Lean theorem assumes a JetBound of order n+5 and concludes a JetBound of order n.
  - quote: `JetBound f S (n + 5) C → JetBound (inverse d f) S n (K * C)`

## 3. Lemma 8.6 · `TorusInverse.zero_mean_series_has_smooth_inverse`

- **Type:** stronger-bound · reported by 3/3 samples · declaration located by 2/3
- **Difference:** The paper's displayed derivative-loss bound is absent from the Lean declaration.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper states the estimate for every integer m ≥ 0.
  - quote: `\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}.$$ (8.19)`
- **Lean** ([TorusInverse.lean:588-592](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TorusInverse.lean#L588-L592)): The Lean theorem states no C^m norm estimate.
  - quote: `∃ u : Torus → ℂ, Continuous u ∧ (∫ z, u z ∂torusMeasure) = 0 ∧`

## 4. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** missing-supremum · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The Lean conclusion is uniform in time over Ioo 0 T, while the paper's displayed step does not show a time quantifier.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The displayed estimate does not display a time variable or uniformity over t.
  - quote: `\left| \int \pi \, w \cdot \nabla \chi_R \right|`
- **Lean** ([R3/PressureFlux.lean:585](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L585)): Lean concludes for all t ∈ Ioo 0 T.
  - quote: `∀ t ∈ Ioo 0 T`

## 5. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples · declaration located by 2/3
- **Difference:** Lean includes uniformity over a parameter set S; the paper statement does not mention such a set.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper statement does not mention uniformity over a parameter set S.
  - quote: `C^m_y`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): The Lean statement quantifies over all p ∈ S and all Y.
  - quote: `∀ p ∈ S, ∀ Y`

## 6. (8.10) in proof of Lemma 8.2 · `UniformFourierAlias.realInverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples · declaration located by 2/3
- **Difference:** The Lean declaration quantifies over a parameter set A; the paper item does not display such a uniformity over A.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The estimate is stated for a torus function H without an explicit parameter set A.
  - quote: `For a zero-mean torus function $H$`
- **Lean** ([UniformFourierAlias.lean:614](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/UniformFourierAlias.lean#L614)): The estimate is uniform over an arbitrary set A and all p in A.
  - quote: `∀ p ∈ A, ∀ Y`

## 7. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples · declaration located by 3/3
- **Difference:** Lean takes a uniform bound over the set S; the paper statement does not display such a set.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The displayed estimate does not explicitly quantify over a parameter set S.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): JetBound is uniform for all p in S.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 8. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound` · **validation**

- **Type:** other · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The algebraic structure of the first part of the bound differs between the two statements.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The paper has R^{-1}[(B_R+1)B_R^{1/2}].
  - quote: `R^{-1} \left[ (B_R + 1) B_R^{1/2}`
- **Lean** ([R3/PressureFlux.lean:587-588](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L587-L588)): Lean has ((cutoffL6^{1/2}+1)*(dissipationRoot/R+1/R^2)).
  - quote: `(cutoffL6 (ComparisonCutoffs.cutoff R) (u - v) t ^ (1 / 2 : ℝ) + 1) *`

## 9. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound` · **validation**

- **Type:** other · reported by 2/3 samples · declaration located by 3/3
- **Difference:** The Lean bound includes additional terms not displayed in the paper's estimate.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The paper's displayed RHS does not contain dissipationRoot/R or 1/R^2 terms.
  - quote: `\left[ (B_R + 1) B_R^{1/2} + R^{-3/4} B_R^{3/4} \right]`
- **Lean** ([R3/PressureFlux.lean:588](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L588)): Lean's RHS contains dissipationRoot/R and 1/R^2.
  - quote: `(dissipationRoot (ComparisonCutoffs.cutoff R) (u - v) t / R + 1 / R ^ 2)`

## Part B: differences in how size is measured

Every difference that all 3 samples reported as different-norm. Most of these are the Lean writing a norm or function class another way (for example a C^m norm as a bound on iterated derivatives). They're here because the rule picks them up, not because anyone has judged them to matter.

## 10. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper measures the relevant size by B_R, while Lean measures it by cutoffL6 and dissipationRoot.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The paper's RHS uses B_R.
  - quote (too short to verify): `B_R`
- **Lean** ([R3/PressureFlux.lean:587-589](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L587-L589)): Lean's RHS uses cutoffL6 and dissipationRoot.
  - quote: `cutoffL6 (ComparisonCutoffs.cutoff R) (u - v) t ^ (1 / 2 : ℝ)`

## 11. (8.10) in proof of Lemma 8.2 · `FourierAlias.cutoffAlias_arbitrary_order`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The two sides measure size with different norms and different objects.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The left side is the C^m_y norm of L^{-p}H.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y}`
- **Lean** ([FourierAlias.lean:566](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/FourierAlias.lean#L566)): The left side is the norm of the iterated Frechet derivative of cutoffAlias at a state point.
  - quote: `‖iteratedFDeriv ℝ j (cutoffAlias χ M (vector d) f) z‖`

## 12. (8.10) in proof of Lemma 8.2 · `ParametricTorusInverse.mixedJet_inverse_bound`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper uses function norms, while the Lean conclusion is a pointwise norm of a mixed jet value.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper measures L^{-p}H in C^m_y and H in C^{m+p+3}_y.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}`
- **Lean** ([ParametricTorusInverse.lean:664](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ParametricTorusInverse.lean#L664)): The Lean statement measures the complex value mixedJet q w (inverse d f) (p,Y) and compares it to a constant times C.
  - quote: `‖mixedJet q w (inverse d f) (p, Y)‖ ≤ mixedLossConstant w.length * C`

## 13. (8.10) in proof of Lemma 8.2 · `ParametricTorusInverse.mixedJet_inverse_bound`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper uses a full function norm, while the Lean hypotheses are separate top-order pure derivative bounds.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The C^{m+p+3}_y norm includes all torus derivatives up to order m+p+3.
  - quote: `C^{m+p+3}_y`
- **Lean** ([ParametricTorusInverse.lean:659](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ParametricTorusInverse.lean#L659)): Lean assumes pure x and swapped-x jets of order w.length+5 are bounded by C.
  - quote: `‖SmoothFourierData.xJet (w.length + 5) (slice (parameterJet q f) p) (x, y)‖ ≤ C`

## 14. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 2/3
- **Difference:** The paper measures size with torus C^m norms; Lean measures size with full joint Fréchet-jet bounds.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper uses C^m_y and C^{m+p+3}_y norms.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): The Lean statement uses JetBound with iteratedFDeriv norms.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 15. (8.10) in proof of Lemma 8.2 · `UniformFourierAlias.realInverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 2/3
- **Difference:** The paper states a C^k norm estimate; the Lean statement gives pointwise bounds on each iterated derivative.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper uses C^m_y and C^{m+p+3}_y norms.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}`
- **Lean** ([UniformFourierAlias.lean:615](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/UniformFourierAlias.lean#L615)): The Lean statement bounds individual iteratedFDeriv norms by a common constant.
  - quote: `‖iteratedFDeriv ℝ j (realInverse d f) (p, Y)‖ ≤ K * C`

## 16. (8.9) in proof of Lemma 8.2 · `PhysicalMeanDomain.transport_compact_finiteJets_fiber`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper statement is scalar-valued, while the Lean statement is stated for a normed vector-valued function and measures size by a norm.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): Paper f is a smooth scalar coefficient and the derivative estimate is written with an absolute value.
  - quote: `be a smooth scalar coefficient. In particular, its smooth zero extension satisfies, for every fixed multi-index I of derivatives in $(R, Z, T, y)$,`
- **Lean** ([PhysicalMeanDomain.lean:252-255](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L252-L255)): Lean f is V-valued and the estimate uses a norm.
  - quote (not verified): `∀ (M : ℝ) (v : PressureStream.Plane) (f : PressureStream.Lift S → V), ContDiff ℝ ∞ f →
      RadiallySupported a b f → ∀ A : ℝ, 0 ≤ A → ∀ s : S,
      (∀ j : ℕ, j ≤ m → ∀ X ∈ Ioo a b, ∀ Y : PressureStream.Plane,
        ‖iteratedFDeriv ℝ j f (X, (s, Y))‖ ≤ A * logWeight cL cR a b p X)`

## 17. Lemma 10.5 · `WholeSpaceUniqueness.candidate_unique_on_Icc`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper uses an L-infinity-in-time L^2 function-class bound, while Lean uses the defined UniformFiniteEnergy condition, which requires square integrability at each time and a uniform kinetic-energy bound.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): v is in L-infinity([0,T];L^2(R^3)).
  - quote: `$v \in L^{\infty}([0,T];L^2(\mathbb{R}^3))$`
- **Lean** ([R3/WholeSpaceUniqueness.lean:77](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/WholeSpaceUniqueness.lean#L77)): v satisfies UniformFiniteEnergy on Icc 0 T.
  - quote: `(hev : UniformFiniteEnergy (Icc (0 : ℝ) T) v)`

## 18. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper's norm is written as a C_y norm, while Lean's JetBound is a full joint Fréchet-jet bound on a parameter set.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper uses the C_y^m norm.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): Lean uses JetBound, a bound on iterated Fréchet derivatives up to order n over p in S and all Y.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 19. Lemma 8.7 · `PositiveOrderMoments.exists_parameterized_exact_repair`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 2/3
- **Difference:** The paper measures regularity with S_alpha/M_alpha classes, while the Lean statement uses C^∞ smoothness on univ ×ˢ S.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper uses regularity classes S_alpha and M_alpha.
  - quote: `targets in $S_{\alpha}$give increments in $M_{\alpha}$`
- **Lean** ([PositiveOrderMoments.lean:926](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PositiveOrderMoments.lean#L926)): The Lean statement uses ContDiffOn ℝ ∞ smoothness.
  - quote: `ContDiffOn ℝ ∞ du (univ ×ˢ S) ∧ ContDiffOn ℝ ∞ de (univ ×ˢ S)`

## 20. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_mem`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper uses the class M; the Lean declaration uses MeanClass, which is defined as MemClass with weight s.zeta.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper concludes R_g ∈ M_{α+0.9-2κ_s}.
  - quote: `\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:439](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L439)): The Lean declaration concludes MeanClass s (H + 9/10 - 2κ) (actualRadialError o base m h W).
  - quote: `MeanClass s (H + 9 / 10 - 2 * κ) (actualRadialError o base m h W)`

## 21. Lemma 8.8 · `DefectIncrementBounds.defects_after_rank_mem`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper uses the symbol S for the target class, while the Lean statement uses an unweighted slow-strip MemClass.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The updated defects are stated to belong to S_{alpha + 0.9 - 2 kappa_s}.
  - quote: `(\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:569-570](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L569-L570)): The i-th updated defect is stated to belong to UnweightedClass slowStripData with exponent H + 9/10 - 2*kappa.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS) (H + 9 / 10 - 2 * κ)`

## 22. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** different-norm · reported by 3/3 samples · declaration located by 3/3
- **Difference:** The paper uses S-class notation for the defect triple; Lean uses an explicit unweighted slow-strip class for a debt component.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The new defect triple is stated to belong to S_{α+0.9-2κ_s}.
  - quote: `$$\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}, \qquad (\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}.$$`
- **Lean** ([DefectIncrementBounds.lean:857](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L857)): The i-th debt row is stated to belong to UnweightedClass on slowStripData with exponent H + 9/10 - 2κ.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS)`
