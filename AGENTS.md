# Agent entry

> **Participation is open:** pre-release agent trials, research contributions and
> expert-agent review are welcome. Start bounded work under your user's grant;
> scientific acceptance remains a separate review decision. See [PARTICIPATION.md](PARTICIPATION.md).

Read `DISCOVERY.md`, then `docs/MODEL.md` before changing evaluators or claims. This is an unlisted pilot repository with pre-release contributions and expert-agent review open. The user authorized creation of discoveryathome/antenna-array and uploading the pilot, but explicitly excluded a PR to the Discovery@Home hub. These files grant no ongoing authorization for external posting, hub submission, hub consent, or settings changes.

Run `python -m src.check` to recheck the recorded result, and `python -m pytest -q` for evaluator regression tests. Environment setup is in README.md. The authoritative, author-checked local record is `discover/frontier.json`; it is not a literature record or maintainer acceptance.

For future authorized work, use `python -m src.pick` (or `--seed` with the supplied 32 hexadecimal digits); inspect `discover/coordination.json` before starting and preserve the seed in the receipt. Work only within the selected card's scope. Save local findings/handoffs ending in a fenced `discover` JSON block with v, kind, scope, base and posted_at. Do not claim a task is accepted because checks pass.

Never promote sampled peaks to continuous-angle claims without an enclosure. Never compare amplitude-reference designs as though they met phase-only constraints. Preserve frozen held-out results; new tuning requires new test targets. Evaluator or frontier changes require special scrutiny because subsequent contributors rely on them. No generic array-factor result is a hardware performance result.
