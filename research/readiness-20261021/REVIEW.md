# Review request: Antenna array synthesis

Status: prepared locally; not sent. No reviewer has signed off.

Baseline commit: `f2f728e0daccd9cd2c91235304a80f1c5e3d718c`. Review the preparation branch commit recorded in the cohort receipt when work is finalized.

Same 16-element, six-bit fixed-array model. Candidate upper peak must beat incumbent lower peak to establish an enclosure-resolved improvement. The calibration-margin track additionally requires the analytic coherent-efficiency lower bound >=0.85. This does not guarantee sidelobes, beamwidth or pointing under all errors.

1. Review ideal-element assumptions, calibration error box, coherence-angle proof and numerical enclosure limitations.
2. Select a motivated engineering use case and acceptable constraint ranges; identify usable coupling/embedded-pattern data.
3. Review our adaptation of Aslan et al. 2019. A same-case reproduction of their reported experiments and a stronger modern comparison remain open.

Return: the commit reviewed, commands run, exact outputs/artifact hashes, any
counterexamples or limitations, and a decision of revise / approve scoped beta /
defer. Specify the scope of approval and review capacity. Do not infer general
scientific validity from passing the automated suite. No signature is prefilled.
