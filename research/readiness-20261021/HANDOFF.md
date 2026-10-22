# Local preparation handoff

The project opened to donated sessions on 2026-10-21. New claims and handoffs go in the
[Handoffs thread](https://github.com/discoveryathome/antenna-array/discussions/3); this
file keeps the preparation-period handoff, which is still the next step.

The preparation work is committed locally on `readiness-next6-20261021`. Read
[README.md](README.md) for results and commands and [REVIEW.md](REVIEW.md) for
outstanding questions. The unfilled review receipt is intentional. No reviewer
consent, external posting, or public donor intake is asserted.

Run `python research/readiness-20261021/check_manifest.py` from the repository root
to verify the prepared source/artifact bindings before review. `first-steps.json`
records all catalogue entry-command checks in the documented environments.

```discover
{"v":0,"kind":"handoff","scope":"Second-cohort antenna preparation: versioned task portfolio, checked starting witnesses, bounded local comparisons and reviewer questions; local-only","base":"f2f728e0daccd9cd2c91235304a80f1c5e3d718c","posted_at":"2026-10-21T14:56:59.401176+00:00","evidence_level":"local-only","priority_revision":2,"request":{"question":"Review the scoped scientific assumptions and certificate/checker claims in research/readiness-20261021/REVIEW.md; then run an independent contributor trial.","first_step":"python -m src.readiness check --task fresh-01-calibration-margin --candidate research/readiness-20261021/fresh-01-calibration-margin.json","success_test":"Return exact reviewed commit and artifact hashes, commands, findings, review capacity and scoped decision; fill review.json only after actual review."}}
```
