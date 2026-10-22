# Discovery@Home pilot: constrained antenna array synthesis

## Precise question

For a fixed 3 GHz 16-element isotropic half-wavelength linear array, can 6-bit phase-only configuration reduce weighted off-target power relative to quantized coherent steering while maintaining coherent efficiency >=0.85, half-power width <=0.14 in direction cosine, and pointing error <=0.015? The exact objective, masks, model and imperfections are in [MODEL.md](docs/MODEL.md). Progress is measured first by feasibility, then the continuous-angle weighted-peak upper bound, then robustness at the same nominal score; timings are descriptive.

The original broad question is already settled. This constrained benchmark tests tradeoffs and verification procedures. The known conditional classical result is Dolph–Chebyshev amplitude synthesis; see [the literature and claim audit](docs/LITERATURE.md). That does not solve quantized constant-modulus synthesis. No verified published optimum for this exact target family was identified. Modern manifold, ADMM and gridless synthesis are important comparison gaps.

## Record and evidence

`discover/frontier.json` is the sole authoritative **local, author-checked** result record. Its table names the best feasible phase-only witness found for each held-out case, not a global optimum or accepted scientific discovery. `results/candidates.json` records every attempt. `docs/RESULTS.md` reports all-seed comparative outcomes, negative results and robustness failures. Verification profile: simulation; claim kind: model. Two implementations and a fresh-clone replay are author checks, not independent-person review.

Run `python -m src.check` and `python -m pytest -q`. The check recomputes constructions, metrics, interval enclosures, independent theta-grid audits, table values, summary consistency and reproducible stress samples. For every stress trial rerun `python -m src.robustness --output results/robustness-replay.json` and compare it with `results/robustness.json`. The result package includes seeds, configuration hashes, source provenance, pinned dependencies and static figures. See README.md for complete commands.

## Bottleneck and tracks

The bottleneck is credible comparison and robustness, not a shortage of search heuristics. Four tracks in `discover/catalog.json` sum to 100:

* **Verification (20):** strengthen floating-point bounds and independently check negative controls.
* **Replication (15):** replay stored designs and optimization with new independent implementations.
* **Literature and bounds (10):** audit modern gridless/manifold methods and define valid relaxations.
* **Robust synthesis (55):** optimize with calibration margin and expand untouched targets.

Each card has a tested positive-control first step. Use the seeded picker rather than choosing the attractive result. No broad geometry search is silently mixed into the fixed-hardware benchmark. Geometry optimization would need a new explicit aperture, minimum spacing, phase and element-pattern contract.

## Settled points

Full coherent phase alignment already maximizes ideal desired-direction field for equal amplitudes. Any suppression improvement must trade off gain or redistribute other radiation. Amplitude tapering has additional hardware freedom. Grid-only peak estimates can miss violations. A one-dimensional isotropic array has cone/front-back ambiguity. RF radiation efficiency is absent from this model. Read the scope-specific traps in the literature audit before proposing work.

## Maintainer, review and coordination

No person has agreed to maintain this project. Review capacity is undeclared, intake is paused, and there is no hub consent or public coordination board. `maintainers` contains an explicit UNASSIGNED sentinel solely because the v0 schema requires one entry; it does not appoint anyone. `canonical_repo` points to the private GitHub repository, created on the user's explicit instruction after the local trial. The project is unlisted, has not been submitted to the Discovery@Home hub, and is not eligible for a donor launcher. Historical local receipts retain their original scope and timestamps.

Future acceptance requires a consenting maintainer, a fresh independent replay, review of mathematical assumptions and claim wording, and a literature comparison. Until then, passing a verifier means only author-checked evidence. No automated acceptance is authorized. Local task lifecycle lives in `discover/coordination.json`; there are no live claims. New external coordination or publication requires the user's instruction. Review capacity, not donated compute, will determine the pace.

## Credit and license

MIT for original code, documentation and generated experiment artifacts. Source papers retain their own licenses and are linked, not redistributed. `CONTRIBUTORS.md` records human and agent contributions honestly; no named person is appointed maintainer or coauthor. Future contributions should identify what was implemented, verified or reviewed. Coauthorship is not promised merely for compute donation.

## Second-cohort preparation (2026-10-21)

For the refreshed task pool, read [the preparation package](research/readiness-20261021/README.md) and `discover/readiness.json`. These versioned portfolios provide the starting witnesses for the new catalogue cards. They do not retroactively change historical experiments or grant public donor intake.
