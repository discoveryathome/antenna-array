"""Descriptive comparisons; targets, not repeated solver seeds, are case units."""
import json
from pathlib import Path
import numpy as np

METHODS=['de160','de200','hybrid','de640','margin-de160','margin-de200','margin-hybrid']
def mean(x):return float(np.mean(x))
def median(x):return float(np.median(x))
def main():
    bench=json.loads(Path('trial/benchmark.json').read_text());rows=bench['rows'];assert len(rows)==420
    plan=json.loads(Path('trial/plan.json').read_text());by={(r['target'],r['seed'],r['method']):r for r in rows};summary={}
    stress=json.loads(Path('trial/robustness.json').read_text())['rows'];assert len(stress)==84
    for method in METHODS:
        rr=[r for r in rows if r['method']==method];ss=[s for s in stress if s['method']==method]
        diag=[r['search'].get('diagnostics',{}) for r in rr]
        summary[method]=dict(mean_weighted_db=mean([r['metrics']['weighted_peak_db_upper'] for r in rr]),mean_sidelobe_db=mean([r['metrics']['sidelobe_db_upper'] for r in rr]),mean_notch_db=mean([r['metrics']['notch_db_upper'] for r in rr]),mean_nominal_eta=mean([r['metrics']['coherent_efficiency'] for r in rr]),nominal_feasible=sum(r['metrics']['feasible'] for r in rr),min_gain_bound=min(r['efficiency_error_box_lower'] for r in rr),median_objective_calls=median([r['search']['objective_calls'] for r in rr]),mean_seconds=mean([r['search']['elapsed_seconds'] for r in rr]),stress_feasible=sum(s['feasible_count'] for s in ss),stress_total=len(ss)*64,adversarial_gain_failures=sum(s['adversarial_gain']['minimum_found']<.85 for s in ss),minimum_adversarial_eta=min(s['adversarial_gain']['minimum_found'] for s in ss))
    for method in METHODS:
        ss=[s for s in stress if s['method']==method]
        byid={r['id']:r for r in rows}
        degradation=[max(t['weighted_peak_db_upper'] for t in s['trials'])-byid[s['id']]['metrics']['weighted_peak_db_upper'] for s in ss]
        summary[method]['mean_worst_sample_score_degradation_db']=mean(degradation)
        summary[method]['max_worst_sample_score_degradation_db']=max(degradation)
        summary[method]['random_failure_causes']={
            'coherent_efficiency':sum(t['coherent_efficiency']<.85-1e-10 for s in ss for t in s['trials']),
            'beamwidth':sum(t['hpbw_u'] is None or t['hpbw_u']>.14 for s in ss for t in s['trials']),
            'pointing':sum(t['pointing_error_u']>.015 for s in ss for t in s['trials'])}
    comparisons={}
    for candidate,baseline in [('hybrid','de160'),('hybrid','de200'),('hybrid','de640'),('margin-hybrid','margin-de160'),('margin-hybrid','margin-de200')]:
        case_means=[];groups={};wins=losses=0;deltas=[];per_target=[]
        for t in plan['targets']:
            ds=[]
            for seed in plan['evaluation_seeds']:
                a,b=by[t['id'],seed,candidate],by[t['id'],seed,baseline];am,bm=a['metrics'],b['metrics']
                ds.append(bm['weighted_peak_db_upper']-am['weighted_peak_db_upper'])
                wins+=int(am['weighted_peak_db_upper']<bm['weighted_peak_db_lower']);losses+=int(bm['weighted_peak_db_upper']<am['weighted_peak_db_lower'])
            d=mean(ds);case_means.append(d);groups.setdefault(t['group'],[]).append(d);deltas+=ds;per_target.append(dict(target=t['id'],group=t['group'],mean_gain_db=d))
        comparisons[candidate+' vs '+baseline]=dict(mean_gain_db=mean(case_means),median_case_gain_db=median(case_means),range_case_gain_db=[min(case_means),max(case_means)],targets_positive=sum(d>0 for d in case_means),targets_above_quarter_db=sum(d>=.25 for d in case_means),bounded_paired_wins=wins,bounded_paired_losses=losses,overlapping_enclosures=60-wins-losses,group_mean_gain_db={g:mean(v) for g,v in groups.items()},per_target=per_target)
    old=json.loads(Path('results/candidates.json').read_text())['rows'];sat=json.loads(Path('trial/saturation.json').read_text());ex=json.loads(Path('trial/exploration.json').read_text());cfg=json.loads(Path('configs/experiment.json').read_text());saturation=[]
    for t in [t for t in cfg['targets'] if t['split']=='held-out']:
        def best(rs):return min([r for r in rs if r['metrics']['feasible']],key=lambda r:r['metrics']['weighted_peak_db_upper'])
        inc=best([r for r in old if r['target']==t['id'] and r['class']=='phase-only']);bde=best([r for r in sat if r['target']==t['id'] and r['method']=='more-de']);bhy=best([r for r in sat if r['target']==t['id'] and r['method']=='more-de-hybrid']);bex=best([r for r in ex if r['target']==t['id']]);score=lambda r:r['metrics']['weighted_peak_db_upper']
        saturation.append(dict(target=t['id'],initial_db=score(inc),initial_id=inc['id'],first_exploration_best_db=score(bex),first_gain_db=score(inc)-score(bex),best_20_more_de_db=score(bde),best_20_hybrid_db=score(bhy),hybrid_gain_over_more_de_db=score(bde)-score(bhy),more_de_id=bde['id'],hybrid_id=bhy['id']))
    out=dict(methods=summary,comparisons=comparisons,saturation=saturation,benchmark_elapsed_seconds=bench['elapsed_seconds'],case_count=12,seeds_per_case=5,notes=['Descriptive local trial; no population-level confidence claim.','New target family was declared before evaluation; algorithms frozen before fresh results.','Objective includes a 16x protected-sector power weight. Weighted dB is not global sidelobe dB.','Wall times were affected by concurrent experiments; objective calls are a complementary budget measure.'])
    Path('trial/analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
