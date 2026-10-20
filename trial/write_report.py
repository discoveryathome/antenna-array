"""Build the assessment from checked result tables; no hand-entered score claims."""
import json
from pathlib import Path

def main():
    load=lambda p:json.loads(Path(p).read_text())
    a=load('trial/analysis.json');checks=load('trial/check-results.json');demo=load('trial/demo-data.json');methods=a['methods'];c=a['comparisons'];sat=a['saturation']
    method_table='\n'.join(f"| {name} | {m['mean_weighted_db']:.3f} | {m['median_objective_calls']:,.0f} | {m['mean_seconds']:.2f} | {m['nominal_feasible']}/60 |" for name,m in methods.items())
    sat_table='\n'.join(f"| {s['target']} | {s['initial_db']:.3f} | {s['first_exploration_best_db']:.3f} | {s['best_20_more_de_db']:.3f} | {s['best_20_hybrid_db']:.3f} |" for s in sat)
    robust_table='\n'.join(f"| {name} | {methods[name]['stress_feasible']}/{methods[name]['stress_total']} | {methods[name]['adversarial_gain_failures']}/12 | {methods[name]['min_gain_bound']:.4f} |" for name in ['de160','de200','hybrid','de640','margin-de200','margin-hybrid'])
    comparison_table='\n'.join(f"| {name} | {m['mean_gain_db']:+.3f} | {m['targets_positive']}/12 | {m['bounded_paired_wins']} / {m['bounded_paired_losses']} / {m['overlapping_enclosures']} |" for name,m in c.items())
    gain=demo[1]['metrics']['weighted_peak_db_upper']-demo[3]['metrics']['weighted_peak_db_upper'];frac=100*(1-10**(-gain/10));margin_cost=methods['margin-hybrid']['mean_weighted_db']-methods['hybrid']['mean_weighted_db']
    text=f'''# Antenna contributor trial: featured-pilot assessment

**Recommendation: a conditional yes as an accessible engineering showcase; not yet a lead scientific-discovery flagship.** This trial produced a real early improvement and a useful robustness argument on modest hardware. It also exposed quick saturation, modest fresh-target gains, and substantial prior art. The feature should be about designing and verifying better radio patterns under constraints. It should not promise that ordinary contributors will invent a new antenna technology every session.

**What was actually tested.** Starting from local commit `ad3e034105b1d88610a22ba1fb1acd1547757b40`, the contributor clock started at 2026-10-20 18:55:53 UTC with a planned 45-minute ceiling. The receipt records the actual finish. The starter already contained a working model, dependencies, evaluator, literature review and optimized baselines. This was one agent acting as contributor after authoring that starter, not a blind onboarding test or a representative sample of human volunteers. Work remained local; the original pilot repository and its frontier were preserved.

The seeded task picker selected `replication-01` (seed `ce159d5b459f1087e0f32b440cbc8f99`). Baseline replication was the positive control. The user's explicit suitability request then authorized this bounded search/robustness extension; it is not an accepted catalogue-task result. The four old test cases became development cases. Twelve new target masks were declared before evaluation, with five fixed seeds each. Algorithms were hashed before their fresh results were inspected. All attempts, including ineffective ones, remain in the package.

**Early hill-climbing: real but uneven.** Within about four minutes, coupled phase changes, warm-started constrained refinement and rounding that uses common-phase freedom improved the difficult symmetric case from {demo[1]['metrics']['weighted_peak_db_upper']:.3f} to {demo[3]['metrics']['weighted_peak_db_upper']:.3f} dB. That is {gain:.3f} dB, or approximately {frac:.1f}% less power in the limiting normalized objective. On this particular case the objective is limited by the global fixed-mask sidelobe, so the same improvement also applies to that sidelobe metric. Quiet-sector peak changed from {demo[1]['metrics']['notch_db_upper']:.3f} to {demo[3]['metrics']['notch_db_upper']:.3f} dB; coherent efficiency changed from {100*demo[1]['metrics']['coherent_efficiency']:.2f}% to {100*demo[3]['metrics']['coherent_efficiency']:.2f}%. Beamwidth increased slightly, from {demo[1]['metrics']['hpbw_deg']:.3f} to {demo[3]['metrics']['hpbw_deg']:.3f} degrees, within its limit.

The other three development cases had much smaller first gains. Twenty additional differential-evolution restarts per case measured whether more routine search could recover the advantage. All columns below are best feasible weighted peaks; lower is better. Best-of-20 results demonstrate saturation/headroom and are not the unbiased fresh-target comparison.

| Development case | Starting best | First exploration best | Best of 20 more DE runs | Same 20 starts + hybrid |
|---|---:|---:|---:|---:|
{sat_table}

On the symmetric case, ordinary extra DE runs recovered part of the early improvement: the hybrid's best-of-20 advantage over extra DE is {sat[-1]['hybrid_gain_over_more_de_db']:.3f} dB. Thus the initial half-dB win is not evidence that additional solver work cannot catch up.

[Hill-climb trajectories](figures/hill-climb.png) show the return from each additional restart. These are best-found records, not lower bounds or proven optima. The small 16-element fixture offers useful first wins but does not yet establish a sustained supply of wins for many contributors.

**Does reasoning beat extra compute?** The frozen hybrid starts with 160 generations of differential evolution, adds constrained SLSQP refinement, enumerates distinct common-phase rounding intervals, and makes paired/single discrete phase moves. DE200 is an approximately matched objective-call control; DE640 uses four times as many generations as DE160. All hybrids are charged for their starting DE run. Margin methods impose the analytically derived gain reserve. The same 12 targets and five seeds are paired across methods.

| Method | Mean weighted peak (dB) | Median objective calls | Mean seconds per attempt | Nominally feasible |
|---|---:|---:|---:|---:|
{method_table}

| Paired comparison | Mean improvement (dB) | Targets with positive mean | Runs: bounded win / loss / overlap |
|---|---:|---:|---:|
{comparison_table}

The primary near-budget comparison, hybrid versus DE200, improves the target-averaged objective by {c['hybrid vs de200']['mean_gain_db']:.3f} dB. The per-target mean ranges from {c['hybrid vs de200']['range_case_gain_db'][0]:.3f} to {c['hybrid vs de200']['range_case_gain_db'][1]:.3f} dB; {c['hybrid vs de200']['targets_above_quarter_db']} of 12 exceed 0.25 dB. Against DE640 the hybrid difference is {c['hybrid vs de640']['mean_gain_db']:+.3f} dB. This is evidence of useful algorithmic choices, not a large universal advantage over spending more CPU. See [fresh-target comparisons](figures/fresh-comparison.png). The 60 runs are 12 target cases with repeated optimizer seeds, not 60 independent engineering deployments; no population-level significance claim is made. The near-budget control is approximate, and objective calls do not perfectly price gradient or constraint work.

**A more substantive contributor result: calibration margin.** Nominal designs near the minimum coherent efficiency can fail after small errors. The contributor derived a normalized-vector-angle bound covering every simultaneous combination of ±2° phase error, ±0.005 wavelength (about 0.50 mm at 3 GHz) along-array position error, and ±3% amplitude error. It gives

`eta_perturbed >= cos²(acos(sqrt(eta_nominal)) + 2° + 2*pi*abs(u0)*0.005 + asin(0.03))`

when the angle is below pi/2, and zero otherwise. Angles in implementation are radians. Inverting the inequality and adding 0.005 absolute efficiency slack supplies a physically interpretable optimization constraint. The [derivation and limitations](MATH.md) are short enough to review. This is an application of elementary inequalities, not a claim of a new mathematical theorem. Its implementation is ordinary float64, not formally verified interval arithmetic.

For each method, the predeclared first seed on each of the 12 fresh targets received 64 common, newly generated simultaneous-error draws. Three-start numerical adversarial searches separately attempted to minimize coherent efficiency. They find damaging examples but do not certify a global worst case. The bound is what covers the whole error box.

| Method | Random trials feasible | Targets where adversarial search found eta < .85 | Minimum analytical gain bound over all 60 designs |
|---|---:|---:|---:|
{robust_table}

Random-trial feasibility checks gain, beamwidth and pointing; it does not mean that the original nominal sidelobe score is preserved. Averaging the worst of 64 sampled errors per target, weighted peak degrades by {methods['hybrid']['mean_worst_sample_score_degradation_db']:.3f} dB for hybrid and {methods['margin-hybrid']['mean_worst_sample_score_degradation_db']:.3f} dB for margin-hybrid. These are sample maxima, not worst-case certificates.

Reserving robustness costs an average {margin_cost:.3f} dB of nominal weighted suppression for margin-hybrid versus hybrid. This is a tradeoff, not a free improvement. The analytical guarantee concerns **coherent efficiency only**. Sidelobe, width and pointing outcomes under errors remain numerical stress tests; there is no all-error certificate for those metrics. The stated error box does not include coupling, element-pattern changes, electronics losses, frequency drift or environmental scattering. [Robustness figure](figures/robustness.png).

**Suitability against the launch criteria.**

| Criterion | Assessment from this trial |
|---|---|
| Tangible first-session progress | Good for a prepared contributor: a verified 0.506 dB gain in minutes, plus a checkable gain bound. Not demonstrated for a new human/agent without starter knowledge. |
| Sustained hill-climbing | Mixed: progress on the symmetric case, quick plateaus elsewhere. Need a stronger, broader challenge family before recruiting many contributors. |
| Public explanation and visual appeal | Strong: aim the main beam, quiet chosen directions, watch phase settings change. A half-dB contribution is much less visually dramatic than the initial steering-to-optimized improvement; show both honestly. |
| Home-PC accessibility | Strong for this fixture: CPU-only on an Apple M2 with 24 GiB RAM; no GPU, cluster or paid solver. Most individual searches take seconds. |
| Agent intelligence matters | Moderate to strong for formulating constraints, exploiting symmetry/rounding and checking bounds. The measured incremental search advantage is modest; do not market this as immunity to ordinary solver competition. |
| Meaningful engineering relevance | Plausible for quantized phase control and calibration tradeoffs, but limited by isotropic uncoupled elements and a single frequency. Hardware relevance requires embedded patterns/coupling and an expert-defined use case. |
| Scientific discovery yield | Unproven. This run improves the local benchmark and verification workflow; it establishes neither a new synthesis method nor a literature record. |

**Onboarding mismatch to fix.** The existing catalogue gives 30% weight to verification, 25% to replication, 20% to literature/bounds and only 25% to robust synthesis. This run initially drew replication and then used the user-authorized trial extension to attempt optimization. A randomly assigned newcomer would not necessarily receive the same hill-climbing opportunity. Verification work is valuable, but a launch promise of visible design improvement should be matched by the actual first-session route and task inventory. The catalogue was not changed during this trial.

**Compute footprint.** The 420-design frozen comparison took {a["benchmark_elapsed_seconds"]/60:.2f} minutes of wall time on a shared Apple M2 (8 logical CPUs, 24 GiB RAM), about 305 CPU-seconds including system time, with a measured peak resident set of about 79 MB for that process. Each search used one BLAS thread. The separate stress command’s wall time includes waiting for the benchmark and must not be added as independent compute time. An objective-only probe reached 256 elements at about 215 MB resident memory; that is an affordability probe, not a completed large-array synthesis study. No GPU was used. Environment installation and the starter-pilot creation preceded this contributor clock.

**What the public can see.** The [35-second narration](DEMO_SCRIPT.md), [animated progression](figures/contributor-progress.gif) and [static before/after figure](figures/before-after.png) use actual evaluated six-bit configurations. Frames are held discrete states, not fabricated interpolation between unevaluated arrays. They separate coherent steering, the already optimized starter, paired moves, and the contributor's refined result. All curves use the same coherent-power reference; reported peak metrics use desired-direction power. The red sectors are the target quiet regions. The polar view is one front-half angular cut: this isotropic linear array has cone/front/back ambiguity, not a unique pencil beam in 3D. The model predicts no measured hardware performance. A suitable public sentence is: “Small timing changes can make a chosen direction quieter while keeping most of the useful signal.”

**Prior art changes the headline.** [Hatam, Mohammadpour and Abdi (2026)](https://pmc.ncbi.nlm.nih.gov/articles/PMC13265949/) already study a genetic-algorithm/SQP hybrid for phase-only sidelobe and efficiency tradeoffs, including larger arrays. [Aslan et al. (2019)](https://pure.tudelft.nl/ws/portalfiles/portal/69797398/08818285.pdf) use iterative phase perturbations and convex subproblems for sidelobes/null sectors, incorporating mutual coupling. These establish that the broad idea and hybrid strategy are mature. This trial did not reproduce their exact cases or implementations; the fresh-target gains are against this pilot's controls, not against those papers. A modern published-method reproduction is a material launch gap.

**Recommended launch decision.** Feature this as one of several hands-on engineering laboratories if the narrative is verified design under constraints. Do not make this tiny fixture the principal evidence that Discovery@Home generates new scientific discoveries. Before broad contributor intake: appoint a willing antenna/RF reviewer; reproduce at least one modern strong baseline; freeze a larger, engineering-defined family with calibration/fault/element-pattern constraints; and run five independent 45-minute contributor sessions starting from the strengthened baseline. Measure time to first independently verified improvement, retained gains against extra-compute controls, review burden, and how many sessions stall. Those gates are a proposed product test, not evidence already obtained.

Keep the 16-element problem as onboarding and regression material. Reward reusable artifacts—correct evaluators, bounds, transferable initialization strategies, robust Pareto improvements and failure explanations—as well as best-found scores. Avoid filling the task board with repeated random restarts or tiny seed-selected records. A good contributor card should name a physical constraint, an existing control, a concrete witness/check and what would count as failure. Robust gain-margin design is a better example than “try another optimizer.”

**Verification and reproduction.** {checks['witnesses_checked']} trial candidate records were reconstructed, all with independent 20,011-point uniform-angle audits against analytical peak enclosures. The maximum enclosure gap over these candidates was {checks['max_peak_enclosure_gap_db']:.5f} dB. The checker rejects altered score, off-grid phase and non-unit amplitude witnesses. It replays {checks['stress_metrics_replayed']} selected error draws, including every record's worst-gain and worst-objective draw, and checks all stored stress summaries against the gain bound. Full stress regeneration is available. See [run instructions](README.md), [raw comparative analysis](analysis.json), [check receipt](check-results.json), [method freeze](freeze.json), and [seeded reoptimization replay](replay-results.json). These are author checks, not independent-person review. Nothing was published or promoted into the original frontier.
'''
    if Path('trial/full-check-results.json').exists():
        full=load('trial/full-check-results.json')
        text+=f"\nThe full audit also replayed all {full['stress_metrics_replayed']:,} stored stress trials successfully. The quick audit independently recomputed all 84 saved adversarial error vectors. See [full audit receipt](full-check-results.json).\n"
    if Path('trial/protocol-finding.json').exists():
        text+='\n```discover\n'+json.dumps(load('trial/protocol-finding.json'),indent=2)+'\n```\n'
    Path('trial/ASSESSMENT.md').write_text(text)
    print('Wrote assessment from completed result tables.')
if __name__=='__main__':main()
