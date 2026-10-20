# Literature audit and claim register

Audit date: 2026-10-20. The question “can arrays concentrate power and suppress sidelobes?” is settled in ideal array theory. The pilot asks how much usable suppression survives equal-amplitude, 6-bit phase control and explicit gain/width constraints on a small benchmark. It is a local benchmark proposal, not a claim to have invented array synthesis or surpassed the field's frontier.

## Source-backed context

| Source | What the source supports | Role and boundary here |
|---|---|---|
| S. J. Orfanidis, *Electromagnetic Waves and Antennas*, author-hosted [textbook](https://eceweb1.rutgers.edu/~orfanidi/ewa/ewa-1up.pdf) | Standard array synthesis, steering, beamwidth and directivity; treatment of coupled antennas is distinct. | Model background. This pilot uses the uncoupled isotropic special case. |
| C. L. Dolph, *A current distribution for broadside arrays which optimizes the relationship between beam width and side-lobe level* (1946), cited and implemented in [SciPy chebwin documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.chebwin.html) | Chebyshev amplitude weighting gives an equiripple sidelobe design and a beamwidth tradeoff for a uniformly spaced array. | Known optimality is conditional on its classical formulation, not a solution to the present quantized phase-only weighted-sector objective. Our continuous 30 dB taper is an informative outside-class reference; the 50 dB test checks the implementation. |
| H. Lebret and S. Boyd, *Antenna Array Pattern Synthesis via Convex Optimization*, IEEE TSP 45(3), 526–532 (1997), [author page](https://web.stanford.edu/~boyd/papers/ant-pat.html), [paper](https://stanford.edu/~boyd/papers/pdf/ant-pat.pdf) | Many pattern constraints with adjustable complex excitations admit efficient convex formulations, including some robustness constraints. | Explains why an unrestricted complex-weight result is not comparable to quantized constant-modulus control. A convex relaxation with a lower bound remains useful future work. |
| D. G. Kurup, M. Himdi and A. Rydberg, *Synthesis of Uniform Amplitude Unequally Spaced Antenna Arrays Using the Differential Evolution Algorithm*, IEEE TAP 51(9), 2210–2217 (2003), [author institution record](https://www.amrita.edu/publication/synthesis-of-uniform-amplitude-unequally-spaced-antenna-arrays-using-the-differential-evolution-algorithm/), DOI 10.1109/TAP.2003.816361 | Differential evolution was already used for uniform-amplitude position/phase array synthesis. | Motivates our DE comparator and a future geometry track. We implement a documented current-to-best variant, not a numerical replication of that paper. Institution abstract checked; publisher full text was inaccessible. |
| B. Kadri, M. Boussahla and F. T. Bendimerad, *Phase-Only Planar Antenna Array Synthesis with Fuzzy Genetic Algorithms* (2010), [author preprint](https://arxiv.org/abs/1002.1176) | Evolutionary phase-only synthesis is established. | Further evidence that phase-only optimization itself is not novel; different geometry and method from this pilot. |
| *Phase-only beampattern synthesis for maximizing mainlobe gain via Riemannian Newton method* (2024), [publisher record](https://www.sciencedirect.com/science/article/pii/S0165168424000951) | Modern phase-only work explicitly studies mainlobe gain and manifold optimization. | Search-indexed publisher abstract checked; full-page fetch returned 403. No numerical superiority or theorem from it is adopted. |
| *Array pattern synthesis with phase-only constraint based on scaled-ADMM algorithm*, Digital Signal Processing 153, 104645 (2024), [publisher record](https://doi.org/10.1016/j.dsp.2024.104645) | An iterative ADMM approach addresses constant-modulus pattern synthesis. | Candidate future comparator; this pilot does not reproduce its convergence claims. Publisher abstract only. |
| *Gridless Phase-Only Focused Beampattern Synthesis for Uniform Rectangular Arrays* (2026), [publisher record](https://www.sciencedirect.com/science/article/pii/S0165168426003476) | The indexed abstract describes continuous-region sidelobe constraints using conservative regions, semidefinite formulations and reference lower bounds. | Particularly relevant current work on grid-missed peaks. Rectangular arrays and its continuous-phase formulation differ from this benchmark. Full-page fetch returned 403; treat as a lead for full-text audit, not a replicated frontier. |

The strongest established reference in the **classical amplitude-taper setting** is the conditional Dolph–Chebyshev beamwidth/sidelobe tradeoff. There is no verified published global optimum for this pilot's exact 16-element, 6-bit, gain-limited, fixed-mask target family in the sources examined. Consequently, `discover/frontier.json` records only locally best feasible witnesses, not “best known in the literature” or optimal designs. Recent gridless and manifold methods make it especially inappropriate to claim state-of-the-art status from a DE/SLSQP comparison.

## Claims from the request and decisions

| Claim or premise | Status | Evidence/action |
|---|---|---|
| Array configurations can concentrate far-field response and suppress unwanted directions. | Confirmed for the specified ideal model. | Orfanidis, Dolph, Lebret–Boyd; uniform and Chebyshev positive controls. |
| Sampling angles alone can miss a true maximum. | Confirmed analytically and by test. | The curvature interpolation proof in MODEL.md; deliberately aliased two-element example. |
| Useful optimization is possible under phase-only constraints. | Established method family; quantitative result depends on constraints. | Kurup et al., Kadri et al.; independently evaluated local experiments. |
| The resulting designs will work on real hardware. | Unverified, not claimed. | Requires embedded patterns/coupling, calibration, EM simulation and measurement. |
| Our methods or resulting patterns are novel/global optima. | Unverified, not claimed. | No exhaustive search, lower-bound match or prior-art equivalence check. |

## Settled questions and traps

* Unit-amplitude coherent steering already attains the maximum possible desired-direction field magnitude N by the triangle inequality. Phase perturbation cannot improve that ideal gain; suppression needs a tradeoff.
* Dolph–Chebyshev's amplitude freedom is unavailable to phase-only hardware. It is a reference, not a fair same-class “competitor.”
* A deep sampled null is not a wide-sector guarantee. Endpoints and between-grid bounds matter.
* Uncontrolled beam broadening can appear to reduce sidelobes if the main region is allowed to move. Fixed masks, width limits and pointing checks prevent that comparison error.
* Main-beam combining efficiency is not radiation efficiency. No loss model means no RF efficiency claim.
* Algorithms are re-run for each held-out target. These are held-out problem instances for a frozen procedure, not a learned beamforming policy generalizing without optimization.

## Unresolved comparison gaps

Add a continuous complex-weight convex relaxation and report its relationship to the discrete feasible set; implement a modern constant-modulus manifold or ADMM method; compare under equal computational budgets; enlarge the target distribution and seed count; establish directed-rounding bounds; repeat with specified nonisotropic embedded-element patterns. These are more credible discovery directions than renaming another evolutionary heuristic.
