# Antenna array synthesis: second-cohort preparation

Local preparation authorized by the project coordinator on 2026-10-21. Evidence is
**author-checked**; outside scientific review is pending. The project has been open to
donated sessions since 2026-10-21 (see `DISCOVERY.md`). No external contact or reviewer
consent is implied.

## Prepared work

All 420 trial designs are re-evaluated. Twelve target masks now have separate nominal and calibration-margin tasks with inherited feasible witnesses. A bounded convex phase-perturbation reference implements the published small-phase linearization on our constraints; its four-case diagnostic retains null results.

The machine-readable portfolio is [`portfolio.json`](portfolio.json).
Historical experiments retain their original exposure and evidence labels. These
preparation cases are now exposed development material, not a sealed test set.

## First contributor step

Activate the repository's documented Python environment, then run from its root:

```sh
python -m src.readiness check --task fresh-01-calibration-margin --candidate research/readiness-20261021/fresh-01-calibration-margin.json
```

Same 16-element, six-bit fixed-array model. Candidate upper peak must beat incumbent lower peak to establish an enclosure-resolved improvement. The calibration-margin track additionally requires the analytic coherent-efficiency lower bound >=0.85. This does not guarantee sidelobes, beamwidth or pointing under all errors.

Before searching, read the portfolio and select one bounded task. Preserve the
starting witness, source hashes, seed and budget. Reserve time to verify the final
artifact. Record unsuccessful runs. A useful handoff can be a replication, a
reproducible defect, a bounded negative finding, or an improvement under the same
formulation; identify which one it is. Passing a local check does not imply novelty
or independent acceptance.

## Outside review

[REVIEW.md](REVIEW.md) contains concrete questions; [review.json](review.json) is an
unfilled review receipt. Review must identify a commit and exact artifact hashes.
The person reproducing a result should disclose any involvement in its creation.

## Independent contributor trial protocol

Choose a task using the refreshed catalogue and give a new contributor only the
published instructions. Record setup time, time to first valid artifact, total
compute, failed attempts and reviewer minutes. Start from the inherited frontier.
Freeze algorithm submissions before evaluating on a separately prepared unseen
case pool. Author-run smoke checks here do not count as independent trials.

Remaining gates:

- RF/array specialist review.
- Published-case reproduction and hardware-relevant input data.
- Independent contributor and numerical replay.

## Published-method diagnostic

`src/readiness.py` implements the small-phase field linearization of Aslan et al.,
[2019, equations 4 and 6](https://doi.org/10.1109/LAWP.2019.2937682), with our weighted
mask and gain inequality, numerical SLSQP subproblems, trust steps and six-bit
quantization. This is an adaptation, not a reproduction of their figures or
coupling-aware cases. `published-method-diagnostic.json` contains all four tested
inherited calibration cases. None improved beyond numerical noise. No algorithmic
superiority follows from this development diagnostic. Full published-case
reproduction remains an open replication task.
