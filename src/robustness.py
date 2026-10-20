"""Common-random-number bounded calibration stress and worst-case field bound."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from .evaluator import evaluate,db
from .run import digest
ROOT=Path(__file__).resolve().parents[1]
SCENARIOS={'phase':(1,0,0),'position':(0,1,0),'amplitude':(0,0,1),'combined':(1,1,1)}

def worst_case(cfg,row):
    # |(1+e_a)exp(i delta)-1| <= |e_a|+2 sin(|delta|/2).
    # Triangle inequality sum(a_n)/N gives a global field perturbation bound.
    phase=math.radians(2);pos=.005;gain=.03
    delta=phase+2*math.pi*pos
    epsilon=float(np.sum(np.abs(row['amplitudes']))/cfg['element_count'])*(gain+2*math.sin(delta/2))
    m=row['metrics']; main_lower=max(0,math.sqrt(m['target_power'])-epsilon)
    s_upper=math.sqrt(m['target_power']*10**(m['sidelobe_db_upper']/10))+epsilon
    n_upper=math.sqrt(m['target_power']*10**(m['notch_db_upper']/10))+epsilon
    denominator=max(main_lower**2,1e-300)
    return dict(field_error_bound=epsilon,target_power_lower=main_lower**2,
                sidelobe_db_upper=db(s_upper*s_upper/denominator),notch_db_upper=db(n_upper*n_upper/denominator),
                weighted_peak_db_upper=db(max(s_upper*s_upper,cfg['notch_weight_power']*n_upper*n_upper)/denominator),
                scope='all simultaneous |phase error|<=2deg, |position error|<=0.005lambda, |relative amplitude error|<=0.03; float64 analytical bound; no beamwidth guarantee')

def main():
    p=argparse.ArgumentParser();p.add_argument('--file',default='results/candidates.json');p.add_argument('--output',default='results/robustness.json');args=p.parse_args()
    cfg=json.loads((ROOT/'configs/experiment.json').read_text()); data=json.loads((ROOT/args.file).read_text())
    targets={t['id']:t for t in cfg['targets']}; rng=np.random.default_rng(cfg['robustness_seed'])
    # Identical error draws for every target/method; no outcome-selected seed.
    errors=rng.uniform(-1,1,(cfg['robustness_trials'],3,cfg['element_count']))
    records=[]
    for row in data['rows']:
        if row['split']!='held-out' or row['seed'] not in [None,cfg['seeds'][0]]:continue
        x=np.asarray(row['positions_lambda']);phi=np.asarray(row['phases_rad']);amp=np.asarray(row['amplitudes']); scenarios={}
        for name,(ps,xs,ams) in SCENARIOS.items():
            trials=[]
            for e in errors:
                m=evaluate(cfg,targets[row['target']],x+xs*.005*e[1],phi+ps*np.deg2rad(2)*e[0],amp*(1+ams*.03*e[2]),grid_n=2049)
                trials.append({k:m[k] for k in ['weighted_peak_db_upper','sidelobe_db_upper','notch_db_upper','coherent_efficiency','hpbw_u','pointing_error_u','feasible']})
            summary={k:dict(median=float(np.median([t[k] for t in trials])),p95=float(np.quantile([t[k] for t in trials],.95)),minimum=float(min(t[k] for t in trials)),maximum=float(max(t[k] for t in trials))) for k in trials[0] if k!='feasible'}
            scenarios[name]=dict(summary=summary,feasible_count=sum(t['feasible'] for t in trials),trials=trials)
        records.append(dict(id=row['id'],target=row['target'],method=row['method'],seed=row['seed'],scenarios=scenarios,worst_case=worst_case(cfg,row)))
        print('stress',row['id'],'combined feasible',scenarios['combined']['feasible_count'],'/',cfg['robustness_trials'],flush=True)
    result=dict(candidate_sha256=digest(ROOT/args.file),config_sha256=digest(ROOT/'configs/experiment.json'),seed=cfg['robustness_seed'],trials=cfg['robustness_trials'],
                perturbation_distribution='independent uniform per element: +/-2deg phase, +/-0.005lambda along-array position, +/-3% amplitude; common draws across methods/targets',
                verification_grid_n=2049,rows=records)
    (ROOT/args.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
