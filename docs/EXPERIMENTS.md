# Frozen comparative experiment

All target masks, seeds, thresholds, and search budgets are in `configs/experiment.json`. `configs/frozen.json` hashes the model, evaluator, optimizer and configuration before held-out runs; git commit d105d4f is the freeze point. Development has two targets. Held-out evaluation has four new masks, including a two-sector target. The parameters were retained after sanity checks, not selected by a broad hyperparameter sweep.

## Methods

1. **Uniform steering:** equal amplitude and nearest 6-bit steering phases. This is the operational same-hardware baseline.
2. **Chebyshev 30 dB:** SciPy's symmetric Dolph–Chebyshev amplitudes, RMS normalized to equal total excitation, continuous phases. Outside hardware class; illustrates amplitude flexibility. Our fixed exclusion mask may include the shoulder of its wider main beam, so its fixed-mask SLL need not equal -30 dB.
3. **Coordinate-only:** three deterministic sweeps of +/- one phase-bin changes from uniform steering. This ablates the main search. One run; no fake seed replication.
4. **Random:** 64*161 independent residual-phase proposals, no adaptive updates or polish, with the steering solution retained if better. A cheap nonadaptive search control; not a universal random-search distribution.
5. **SLSQP:** four starts (one steering, three seeded Gaussian perturbations), an epigraph minimax problem and analytic Jacobians; gain >=0.85 is explicit. Up to 160 iterations per start. One global phase is fixed. Residual phases are bounded to +/-1.2 rad. Quantize each start's result and select using the optimizer objective, then apply three discrete coordinate sweeps. Solver success flags are retained; success flags do not replace verification.
6. **Differential evolution:** 64 members, 160 generations, current-to-best/1/bin, F=.65, crossover .8, steering initialized as one member. Residual phases start uniformly in +/-0.45 rad and are clipped to +/-1.2 rad. Fitness evaluates 6-bit quantization. Finish with the same coordinate polish as SLSQP.

Three independent fixed seeds (1729, 2718, 3141) per random/SLSQP/DE target. The two main methods represent constrained local minimax optimization and population-based evolutionary optimization. Neither has a global optimality claim. Discrete searches penalize gain deficit by 100 times the shortfall; hard feasibility is determined by the evaluator.

## Reporting and limits

All attempts are saved, including any infeasible ones. Main method comparisons use all seeds and per-target medians, not the best run. The local frontier separately stores the best feasible witness per target (explicitly a best-of-portfolio result). Plots and robustness use the predetermined first seed 1729, never an outcome-selected winner. Performance is scored on the independent verifier grids and curvature bounds.

DE and random have matched core candidate budgets, but SLSQP uses analytic gradients and a different budget. Coordinate polishing also has a variable early-stop count. Objective calls and elapsed times are recorded; they are descriptive, not evidence of universal speed superiority. Tests/search run locally, single-process, with BLAS threads set to one. Other host activity is not controlled. Cross-platform floating-point/SLSQP paths may vary; verification of stored witnesses is more stable than bitwise re-optimization. Timing is not a controlled benchmark.

Targets were specified in advance, but this is a tiny hand-selected family rather than a random representative application sample. “Held-out” means search settings were frozen before those target runs, not that the optimizer cannot see its requested mask. A gain on these targets is evidence of benchmark usefulness only. Future tuning must use a new untouched test set.

Robustness uses the four scenarios and deterministic bound in MODEL.md. Nominal and perturbed metrics must remain separate. A design meeting nominal eta=0.85 may cross that limit under small errors; do not conceal those failures or treat average robustness as a guarantee.
