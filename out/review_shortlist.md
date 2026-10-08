# Review shortlist

Differences between the paper and the Lean formalization that may deserve an expert's attention, selected mechanically: reported by all 3 independent samples and concerning what is estimated (bound, norm, or uniformity), plus the hits on the two published discrepancies. **Nothing here has been reviewed by a mathematician; each entry is a difference in wording, not a claimed error.** Full data: `out/differences.csv`; method: `METHODOLOGY.md`.

## 1. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.applyMultiplier_finiteJets`

- **Type:** stronger-bound · reported by 3/3 samples
- **Difference:** For corresponding output orders, the paper requires three derivatives beyond the multiplier order while the Lean statement requires four derivatives beyond l.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The input regularity is C^{m+p+3}_y.
  - quote: `C^{m+p+3}_y`
- **Lean** ([SmoothFamilyTorusInverse.lean:851](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L851)): The input finite jet bound is of order n+l+4.
  - quote: `JetBound f S (n + l + 4) C`

## 2. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** stronger-bound · reported by 3/3 samples
- **Difference:** The paper loses four derivatives, while the Lean declaration loses five.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper bounds N^{-1}F in C_y^m by C_m times the C_y^{m+4} norm of F.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$.`
- **Lean** ([SmoothFamilyTorusInverse.lean:868](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L868)): The Lean theorem assumes a JetBound of order n+5 and concludes a JetBound of order n.
  - quote: `JetBound f S (n + 5) C → JetBound (inverse d f) S n (K * C)`

## 3. Lemma 8.6 · `TorusInverse.zero_mean_series_has_smooth_inverse`

- **Type:** stronger-bound · reported by 3/3 samples
- **Difference:** The paper's displayed derivative-loss bound is absent from the Lean declaration.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper states the estimate for every integer m ≥ 0.
  - quote: `\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}.$$ (8.19)`
- **Lean** ([TorusInverse.lean:588-592](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/TorusInverse.lean#L588-L592)): The Lean theorem states no C^m norm estimate.
  - quote: `∃ u : Torus → ℂ, Continuous u ∧ (∫ z, u z ∂torusMeasure) = 0 ∧`

## 4. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper measures the relevant size by B_R, while Lean measures it by cutoffL6 and dissipationRoot.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The paper's RHS uses B_R.
  - quote: `B_R`
- **Lean** ([R3/PressureFlux.lean:587-589](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L587-L589)): Lean's RHS uses cutoffL6 and dissipationRoot.
  - quote: `cutoffL6 (ComparisonCutoffs.cutoff R) (u - v) t ^ (1 / 2 : ℝ)`

## 5. (8.10) in proof of Lemma 8.2 · `FourierAlias.cutoffAlias_arbitrary_order`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The two sides measure size with different norms and different objects.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The left side is the C^m_y norm of L^{-p}H.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y}`
- **Lean** ([FourierAlias.lean:566](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/FourierAlias.lean#L566)): The left side is the norm of the iterated Frechet derivative of cutoffAlias at a state point.
  - quote: `‖iteratedFDeriv ℝ j (cutoffAlias χ M (vector d) f) z‖`

## 6. (8.10) in proof of Lemma 8.2 · `ParametricTorusInverse.mixedJet_inverse_bound`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses function norms, while the Lean conclusion is a pointwise norm of a mixed jet value.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper measures L^{-p}H in C^m_y and H in C^{m+p+3}_y.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}`
- **Lean** ([ParametricTorusInverse.lean:664](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/ParametricTorusInverse.lean#L664)): The Lean statement measures the complex value mixedJet q w (inverse d f) (p,Y) and compares it to a constant times C.
  - quote: `‖mixedJet q w (inverse d f) (p, Y)‖ ≤ mixedLossConstant w.length * C`

## 7. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper measures size with torus C^m norms; Lean measures size with full joint Fréchet-jet bounds.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper uses C^m_y and C^{m+p+3}_y norms.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): The Lean statement uses JetBound with iteratedFDeriv norms.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 8. (8.10) in proof of Lemma 8.2 · `UniformFourierAlias.realInverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper states a C^k norm estimate; the Lean statement gives pointwise bounds on each iterated derivative.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper uses C^m_y and C^{m+p+3}_y norms.
  - quote: `\|\mathcal{L}^{-p}H\|_{C^m_y} \le C_{m,p} \|H\|_{C^{m+p+3}_y}`
- **Lean** ([UniformFourierAlias.lean:615](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/UniformFourierAlias.lean#L615)): The Lean statement bounds individual iteratedFDeriv norms by a common constant.
  - quote: `‖iteratedFDeriv ℝ j (realInverse d f) (p, Y)‖ ≤ K * C`

## 9. (8.9) in proof of Lemma 8.2 · `PhysicalMeanDomain.transport_compact_finiteJets_fiber`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper statement is scalar-valued, while the Lean statement is stated for a normed vector-valued function and measures size by a norm.
- **Paper** ([p.90](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=90), Lemma 8.2): Paper f is a smooth scalar coefficient and the derivative estimate is written with an absolute value.
  - quote: `be a smooth scalar coefficient. In particular, its smooth zero extension satisfies, for every fixed multi-index I of derivatives in $(R, Z, T, y)$,`
- **Lean** ([PhysicalMeanDomain.lean:252-255](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PhysicalMeanDomain.lean#L252-L255)): Lean f is V-valued and the estimate uses a norm.
  - quote (not verified): `∀ (M : ℝ) (v : PressureStream.Plane) (f : PressureStream.Lift S → V), ContDiff ℝ ∞ f →
      RadiallySupported a b f → ∀ A : ℝ, 0 ≤ A → ∀ s : S,
      (∀ j : ℕ, j ≤ m → ∀ X ∈ Ioo a b, ∀ Y : PressureStream.Plane,
        ‖iteratedFDeriv ℝ j f (X, (s, Y))‖ ≤ A * logWeight cL cR a b p X)`

## 10. Lemma 10.5 · `WholeSpaceUniqueness.candidate_unique_on_Icc`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses an L-infinity-in-time L^2 function-class bound, while Lean uses the defined UniformFiniteEnergy condition, which requires square integrability at each time and a uniform kinetic-energy bound.
- **Paper** ([p.121](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=121), Lemma 10.5): v is in L-infinity([0,T];L^2(R^3)).
  - quote: `$v \in L^{\infty}([0,T];L^2(\mathbb{R}^3))$`
- **Lean** ([R3/WholeSpaceUniqueness.lean:77](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/WholeSpaceUniqueness.lean#L77)): v satisfies UniformFiniteEnergy on Icc 0 T.
  - quote: `(hev : UniformFiniteEnergy (Icc (0 : ℝ) T) v)`

## 11. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper's norm is written as a C_y norm, while Lean's JetBound is a full joint Fréchet-jet bound on a parameter set.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The paper uses the C_y^m norm.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): Lean uses JetBound, a bound on iterated Fréchet derivatives up to order n over p in S and all Y.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 12. Lemma 8.7 · `PositiveOrderMoments.exists_parameterized_exact_repair`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper measures regularity with S_alpha/M_alpha classes, while the Lean statement uses C^∞ smoothness on univ ×ˢ S.
- **Paper** ([p.97](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=97), Lemma 8.7): The paper uses regularity classes S_alpha and M_alpha.
  - quote: `targets in $S_{\alpha}$give increments in $M_{\alpha}$`
- **Lean** ([PositiveOrderMoments.lean:926](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/PositiveOrderMoments.lean#L926)): The Lean statement uses ContDiffOn ℝ ∞ smoothness.
  - quote: `ContDiffOn ℝ ∞ du (univ ×ˢ S) ∧ ContDiffOn ℝ ∞ de (univ ×ˢ S)`

## 13. Lemma 8.8 · `DefectIncrementBounds.actualRadialError_mem`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses the class M; the Lean declaration uses MeanClass, which is defined as MemClass with weight s.zeta.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The paper concludes R_g ∈ M_{α+0.9-2κ_s}.
  - quote: `\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:439](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L439)): The Lean declaration concludes MeanClass s (H + 9/10 - 2κ) (actualRadialError o base m h W).
  - quote: `MeanClass s (H + 9 / 10 - 2 * κ) (actualRadialError o base m h W)`

## 14. Lemma 8.8 · `DefectIncrementBounds.defects_after_rank_mem`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses the symbol S for the target class, while the Lean statement uses an unweighted slow-strip MemClass.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The updated defects are stated to belong to S_{alpha + 0.9 - 2 kappa_s}.
  - quote: `(\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}`
- **Lean** ([DefectIncrementBounds.lean:569-570](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L569-L570)): The i-th updated defect is stated to belong to UnweightedClass slowStripData with exponent H + 9/10 - 2*kappa.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS) (H + 9 / 10 - 2 * κ)`

## 15. Lemma 8.8 · `DefectIncrementBounds.rankStage_defect_class`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper uses S-class notation for the defect triple; Lean uses an explicit unweighted slow-strip class for a debt component.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The new defect triple is stated to belong to S_{α+0.9-2κ_s}.
  - quote: `$$\mathcal{R}_g \in \mathsf{M}_{\alpha+0.9-2\kappa_s}, \qquad (\mathcal{P}_{\text{new}}, (\mathcal{J}_\theta)_{\text{new}}, (\mathcal{J}_z)_{\text{new}}) \in \mathsf{S}_{\alpha+0.9-2\kappa_s}.$$`
- **Lean** ([DefectIncrementBounds.lean:857](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/DefectIncrementBounds.lean#L857)): The i-th debt row is stated to belong to UnweightedClass on slowStripData with exponent H + 9/10 - 2κ.
  - quote: `UnweightedClass (MeanMomentBounds.slowStripData (D := P) ε S hε hεone hS)`

## 16. Lemma 8.8 · `MeanLocalDefectBounds.rankStage_gain_of_targets`

- **Type:** different-norm · reported by 3/3 samples
- **Difference:** The paper's S class is formalized in Lean as an UnweightedClass.
- **Paper** ([p.98](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=98), Lemma 8.8): The three targets belong to S_α.
  - quote: `and the three targets belong to $S_{\alpha}$ for $\alpha \ge 0.9$`
- **Lean** ([MeanLocalDefectBounds.lean:315-317](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/MeanLocalDefectBounds.lean#L315-L317)): The three current debts are assumed to lie in UnweightedClass H.
  - quote: `UnweightedClass (PhysicalMeanDomain.localSlowStripData U.carrier U.isOpen ε L hε hεone hL)`

## 17. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** missing-supremum · reported by 3/3 samples
- **Difference:** The Lean conclusion is uniform in time over Ioo 0 T, while the paper's displayed step does not show a time quantifier.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The displayed estimate does not display a time variable or uniformity over t.
  - quote: `\left| \int \pi \, w \cdot \nabla \chi_R \right|`
- **Lean** ([R3/PressureFlux.lean:585](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L585)): Lean concludes for all t ∈ Ioo 0 T.
  - quote: `∀ t ∈ Ioo 0 T`

## 18. (8.10) in proof of Lemma 8.2 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples
- **Difference:** Lean includes uniformity over a parameter set S; the paper statement does not mention such a set.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The paper statement does not mention uniformity over a parameter set S.
  - quote: `C^m_y`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): The Lean statement quantifies over all p ∈ S and all Y.
  - quote: `∀ p ∈ S, ∀ Y`

## 19. (8.10) in proof of Lemma 8.2 · `UniformFourierAlias.realInverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples
- **Difference:** The Lean declaration quantifies over a parameter set A; the paper item does not display such a uniformity over A.
- **Paper** ([p.91](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=91), (8.10)): The estimate is stated for a torus function H without an explicit parameter set A.
  - quote: `For a zero-mean torus function $H$`
- **Lean** ([UniformFourierAlias.lean:614](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/UniformFourierAlias.lean#L614)): The estimate is uniform over an arbitrary set A and all p in A.
  - quote: `∀ p ∈ A, ∀ Y`

## 20. Lemma 8.6 · `SmoothFamilyTorusInverse.inverse_finiteJets`

- **Type:** missing-supremum · reported by 3/3 samples
- **Difference:** Lean takes a uniform bound over the set S; the paper statement does not display such a set.
- **Paper** ([p.95](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=95), (8.19)): The displayed estimate does not explicitly quantify over a parameter set S.
  - quote: `$\|N^{-1}F\|_{C_y^m} \le C_m \|F\|_{C_y^{m+4}}$`
- **Lean** ([SmoothFamilyTorusInverse.lean:653](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/SmoothFamilyTorusInverse.lean#L653)): JetBound is uniform for all p in S.
  - quote: `∀ j ≤ n, ∀ p ∈ S, ∀ Y, ‖iteratedFDeriv ℝ j f (p, Y)‖ ≤ C`

## 21. (10.19) in proof of Lemma 10.5 · `PressureFlux.exists_uniform_actual_pressure_flux_bound`

- **Type:** other · reported by 3/3 samples
- **Difference:** The paper writes a named constant depending on T, while Lean states an existential nonnegative constant.
- **Paper** ([p.123](https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf#page=123), (10.19)): The paper uses a constant C_T.
  - quote: `C_T`
- **Lean** ([R3/PressureFlux.lean:585](https://github.com/openai/NavierStokesAndEuler/blob/f9e8bc5b38b6e212696e8a30e3e91517af887bbd/NavierStokes/R3/PressureFlux.lean#L585)): Lean proves existence of a nonnegative constant CP.
  - quote: `∃ CP : ℝ, 0 ≤ CP`
