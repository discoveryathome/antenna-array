# Bounded contributor trial

Start with [ASSESSMENT.md](ASSESSMENT.md) for the featured-pilot recommendation, [the animation](figures/contributor-progress.gif) for the public demonstration, and [MATH.md](MATH.md) for the gain-robustness argument.

This is a local extension of the original pilot. `discover/frontier.json` still describes the original author-checked record. This trial has not been accepted, published, or independently reviewed. `plan.json` records the predeclared target family and seeds; `freeze.json` fixes the algorithms before fresh-target results. The four original held-out cases were explicitly reused for development. The 12 new cases are the fresh test family.

## Verify the delivered evidence

Run from the **repository root**, not from this directory. The original `requirements.lock.txt` also covers this extension. Python 3.14.6 on macOS arm64 was tested. Create an environment using the repository README, then:

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -m pytest -q
python -m src.check
python -m trial.check
```

Expected: 12 tests, original baseline verification, and 640 trial witnesses checked against quantization, independently evaluated metrics and a separate 20,011-point theta grid. The trial checker also validates frozen-source hashes, corrupt-witness rejection, and selected stress replays. Ordinary float64 calculations are used; this is not formal interval verification.

To recheck every stored stress metric without replacing the experiment evidence, run `python -m trial.check --full-stress`. This writes `full-check-results.json` and takes longer than the sample audit.

The environment used in this session is `../../.venv/bin/python` relative to this checkout. The scripts use no network at runtime and no GPU or commercial solver.

## Reproduce optimization and stress tests

These commands overwrite generated **trial** results and timing metadata. Make a separate checkout/copy first if preserving the delivered evidence. They do not update the original frontier.

```bash
python -m trial.explore
python -m trial.incumbent
python -m trial.benchmark
python -m trial.robust
python -m trial.replay_one
python -m trial.check
python -m trial.analyze
python -m trial.demo
python -m trial.plots
python -m trial.write_report
```

`trial.benchmark` reports seven methods: DE160, approximately call-matched DE200, DE640, the DE160/refinement hybrid, and three gain-margin variants. It runs 12 targets × 5 seeds × 7 reported methods = 420 designs. Shared DE initializations are charged to each hybrid. There are 48 original-case exploratory attempts and 172 subsequent saturation/margin attempts. All results, including negative outcomes, are retained.

`trial.robust` evaluates the predeclared first seed for each method and target: 84 designs × 64 fresh simultaneous-error draws = 5,376 trials. It also performs three-start adversarial gain minimization per design. A separate analytic bound covers coherent efficiency throughout the error box; the adversarial search is not itself a certificate. `trial.replay_one` independently reruns all seven methods on the predeclared first target and seed, checking identical phase arrays and objective-call counts on this environment. Other platforms/library versions may have different optimizer trajectories.

The benchmark took roughly the recorded `analysis.json:benchmark_elapsed_seconds` on a shared Apple M2 host; use objective-call counts alongside timings. Concurrent host work makes these descriptive timings, not controlled performance rankings. `scaling.py` is only a cheap objective-evaluation affordability probe, not evidence that large-array scientific optimization is solved.

## Evidence map

| File | Role |
|---|---|
| `plan.json`, `freeze.json`, `stress-plan.json` | Scope, targets, seeds, declared controls and algorithm hashes |
| `search.py`, `coherence.py`, `benchmark.py` | Contributor method and robustness bound, frozen before fresh outcomes |
| `exploration.json` | All first-stage exploratory attempts |
| `saturation.json` | Extra-compute controls and robust-incumbent follow-up |
| `benchmark.json` | All 420 fresh-target constructions, metrics, costs and diagnostics |
| `robustness.json` | All 5,376 stress outcomes and adversarial error vectors |
| `analysis.json` | Paired descriptive comparisons and method summaries |
| `check-results.json`, `replay-results.json` | Verification and deterministic reoptimization receipts |
| `demo-data.json`, `figures/` | Evaluated public-demo states and scientific plots |
| `receipt.json` | Actual trial timing, local status and evidence summary |

All peak-score comparisons use the original fixed-mask definition, with protected-sector power multiplied by 16. A weighted-score gain is not generally an equal gain in global sidelobe suppression. Coherent efficiency is an excitation-vector metric, not RF radiation efficiency. The array has isotropic elements, no mutual coupling, a fixed 3 GHz frequency and fixed half-wavelength geometry. The geometry never changes; only 6-bit phases are optimized.
