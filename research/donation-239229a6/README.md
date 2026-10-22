# fresh-08: a checked negative neighborhood result

The inherited calibration-margin witness cannot be improved by any of the
specified 2,928 single/pair phase changes in the canonical mathematical model.
An author-written integer interval audit excludes every neighbor: 1,508 fail
the pinned analytical calibration gate and 1,420 have strictly worse nominal
continuous-angle objective. This is a finite-neighborhood result, not global
optimality, independent-person acceptance, or hardware validation.

The seeded task is `fresh-08-calibration-margin`, round seed
`239229a686e46247e5c96c3b6d7b0993`, at project base
`d9db8b4f07222da18b89cd4a936cbcf5e915925f`. The target, array, phase bits,
evaluator, acceptance gates and accepted/frontier records are unchanged.

## Experiment and result

The predeclared experiment adapts the discrete method from
[PR #7](https://github.com/discoveryathome/antenna-array/pull/7), commit
`51c71068ae26b99585231938de139ddbdd6d99ea`, to the distinct fresh-08 task.
It tries every nonzero six-bit change on one element, followed by changes of
plus/minus one or two bins on each pair. Two nominal-efficiency floors are
tested: the inherited optimizer slack and the exact contract floor plus 1e-9.
The cap is 30 sweeps per stage and 30 minutes overall; every stage stopped
naturally after one sweep. All 7,872 scores are retained, including repeated
evaluations across stages/floors. There are 2,928 unique phase neighbors.

All four variants retain the inherited phase bins. The unchanged task checker
returns nominal feasibility and `established_improvement: false`. Its weighted
peak enclosure is about `[-14.59274430135, -14.59245393035]` dB, nominal coherent
efficiency is `0.90166305558`, and the analytical error-box efficiency lower
bound is `0.85593521995`.

The optimizer grid alone leaves one candidate too close to exclude by the
incumbent's existing upper estimate. That candidate changes bins 10 and 15 by
-1; the unchanged evaluator also ranks it worse. Rather than infer a continuous
claim from sampled descent, the package checks the entire neighborhood with
an exact-integer interval calculation.

| Interval audit quantity | Value |
|---|---:|
| Enumerated neighbors | 2,928 |
| Below the mathematical calibration threshold | 1,508 |
| Above threshold and worse by objective bounds | 1,420 |
| Ambiguous or dropped cases | 0 |
| Certified incumbent weighted-score upper | 0.03473444010039710 |
| Smallest competitor-lower minus incumbent-upper | 0.00000946132880931 |

Those displayed decimals abbreviate the exact endpoints in
[neighborhood-certificate.json](neighborhood-certificate.json).
The certificate uses exact phases `2*pi*q/64`, exact decimal target angles,
and the centered quarter-integer positions with half-wavelength spacing.
It covers the full calibration-bound gate, without the optimizer's extra slack
or its 1e-9 padding. Failure of that sufficient-bound gate does not prove actual
physical inefficiency.

[MATHEMATICS.md](MATHEMATICS.md) explains each bound. Integer floor/ceiling
arithmetic, rational Machin-series pi bounds, bounded sine/cosine Taylor
remainders and integer square roots replace platform libm in the certificate.
A second-derivative interpolation bound covers the incumbent's complete scoring
regions. One verified in-region point is sufficient to lower-bound each
competitor's maximum. Numerical stationary-point locations are used only as
suggested points and are checked afresh.

The internal scale is 10^50; the trigonometric remainder, about 7.30e-42,
limits accuracy. The implementation is author-checked, not formally verified
software. The separate [source audit](bounds-audit.md) reviews the mathematical
route and primary references, not the parent implementation or computed result.

## Reproduce

The exact interval audit needs only Python 3's standard library and the included
point-witness data. From the repository root, without Python's `-O` option:

```sh
python research/donation-239229a6/test_intervals.py
python research/donation-239229a6/certify_neighborhood.py
```

The certificate checks the three frozen input hashes before computation, generates
the complete neighborhood independently of the search routine, validates every
point's domain, and stops on any ambiguous interval comparison. On this host the
final audit took about 29 seconds; this is not a controlled speed comparison.

For the numerical experiment and replay, use the project's pinned local
environment (`requirements.lock.txt`; this run used Python 3.13.5,
NumPy 2.5.4 and SciPy 1.18.1):

```sh
python -m src.readiness check --task fresh-08-calibration-margin --candidate research/readiness-20261021/fresh-08-calibration-margin.json
PYTHONPATH=. python research/donation-239229a6/search.py --output /tmp/antenna-239229a6-replay
PYTHONPATH=. python research/donation-239229a6/verify.py --output /tmp/antenna-239229a6-verification.json
python -m pytest -q
```

`verify.py` replays all four rows and every attempted score exactly in the
recorded environment, checks an independent 100,001-angle-per-region field
implementation with stationary-point refinement, verifies an extended-precision
calibration calculation, and rejects five deliberately invalid witnesses.
Its float64 checks do not supply the integer interval proof. Exact floating
replay may differ on other platforms even when the scientific checks agree.

`locate_points.py` can regenerate the point proposals using the pinned numerical
environment. It never creates a new phase vector outside the original finite
neighborhood. The interval audit does not need SciPy or NumPy once the points
are present.

## Validation and existing full-check failure

All 17 tests pass, including four arithmetic controls with exact rational oracles.
The search replay, five rejecting controls and exact interval audit pass. The
source, candidate and artifact hashes needed for replay are retained.

The existing `python -m src.check` is **not fully passing on this environment**.
It passes 72 stored reconstruction/angle-grid audits, protocol checks and the
literature inventory, then fails exact dictionary equality at `src/check.py:66`.
Five stored robustness values reproduce one ULP differently (maximum absolute
difference about 3.55e-15). The table/frontier/summary checks pass when invoked
separately. [baseline-check.json](baseline-check.json) records every discrepancy;
reproduce with `PYTHONPATH=. python research/donation-239229a6/baseline_check.py`.
No assertion was relaxed and no stored value was rewritten. Full robustness
replay is not claimed complete. This discrepancy is separate from the new
standard-library interval result.

## Credit and remaining work

The model, calibration theorem, readiness corpus and inherited witness belong
to the repository's cited contributors. The discrete method is credited to the
earlier donation PR above. This package adds AI-authored experiment records,
interval calculations, implementation controls and documentation under the
donor's grant; it asserts no automatic coauthorship or accepted result.

An external reviewer should inspect the arithmetic and model interpretation,
replay the exact certificate and assess the claim wording. Further synthesis
must try moves outside this excluded neighborhood or another explicitly scoped
method. Perturbed sidelobes, beamwidth/pointing under calibration, mutual coupling,
element patterns and hardware remain unverified. The frozen held-out and
accepted-result records are untouched.
