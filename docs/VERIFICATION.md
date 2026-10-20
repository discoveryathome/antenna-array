# Local verification receipt — 2026-10-20

This receipt records author checks, not independent-person review or maintainer acceptance.

## Reproduction evidence

- Initial model/search freeze: `d105d4f`. The source configuration, evaluator and optimization settings were fixed before held-out targets were run. A later model **docstring-only** correction is recorded in `configs/frozen.json`; ASTs excluding docstrings were identical. No executed search statement or numerical assumption changed.
- Complete experiment snapshot: `56a0834`, cloned locally with `git clone --no-hardlinks` into `../fresh-check`. The clone had no generated interpreter/font caches. It reused the explicitly documented session virtual environment and pinned packages; it was not a separate machine or independent contributor.
- Full search replay from that clone: 72/72 candidate IDs matched. Maximum phase-table difference was **0 radians** and maximum numeric nominal metric difference was **0**. All booleans matched. Timing and source-provenance metadata were excluded from the comparison. This establishes same-environment determinism, not cross-platform bitwise identity.
- Full evaluator replay: 72 independently reconstructed nominal witnesses and their independent uniform-theta grid audits passed; **6,144/6,144** calibration trials were recomputed and matched; all stress summaries, analytical error-box bounds, frontier values and artifact hashes passed.
- Numerical regression suite: **8 tests passed**, including complex-vs-real evaluator comparison, uniform-array closed form, Chebyshev positive control, analytic integral check, grid-aliasing negative control, finer-grid enclosure audit, false-claim/invalid-hardware rejection and phase-gradient checks.
- Full-check elapsed time was 228.78 seconds, including first-use macOS font discovery through the plotting module. The final checker avoids this plotting initialization; it does not need a font cache. The full run used 73.91 user CPU seconds. Other local work ran concurrently, so elapsed timings are not controlled performance measurements.
- Every catalog first-step command passed in the fresh checkout. The seeded picker was exercised with test seed `123456789abcdef0123456789abcdef0`; this was a test, not a claimed research task.
- The SHA-256-verified Discovery@Home helper reported `conformant: true`, no problems or warnings, and a four-row frontier table. Its static screen reported no findings. Absence of a public coordination channel, ledger and package convention is disclosed; this is a paused local proposal.
- Polar, Cartesian and tradeoff figures were opened and visually checked for axis labels, legends and clipping. Front/back symmetry and per-design desired-power normalization are explicitly identified.

## Runtime and provenance

Python 3.14.6, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2; complete transitive lock in `requirements.lock.txt`. Searches used one process and `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`. The supplied workspace permission profile was unrestricted. The session ran its own generated scientific code and registry binary wheels; no claim of sandbox isolation is made. No repository was created on GitHub, no message was posted, no setting was changed, and no hub consent was granted.

The external playbook and helper were fetched into the enclosing task's `setup/` folder. The helper hash was checked before execution:

`77c850c65ff54e951b102950d06321751273ba6e9ef1bf28786930fb216802b6`

Raw session receipts are under `../setup/` (outside the git project): `protocol-validation.json`, `catalog-check.log`, `fresh-check.log`, `reoptimization.log`, `reoptimization-comparison.json`, and `final-check.log`. The scientific result artifacts themselves are in git and pinned by the frontier record.

## Limits and open review

The verifier covers the declared ideal model and numerical metrics. Curvature enclosures are computed with float64 padding, not directed rounding. Half-power crossings and peak location are numerical. The four held-out masks and three search seeds are small, specified examples. The finite stress draws are not a reliability estimate for manufacturing. Analytical error-box bounds do not include coupling, embedded-element patterns or RF losses, and do not guarantee width or pointing. The 51 combined-stress feasibility failures all crossed the coherent-gain floor; none failed width or pointing.

There is no proof of global optimality, no established scientific novelty, no hardware validation, no consenting maintainer and no independent-person acceptance. Future work should improve calibration margin, strengthen numerical bounds, and compare modern phase-only methods under matched scopes and budgets. Review of the evaluator and frontier deserves priority.
