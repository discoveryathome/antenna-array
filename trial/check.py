"""Author replay: immutable algorithms, witnesses, independent angle grid, tampering."""
import argparse,copy,hashlib,json,math,time
from pathlib import Path
import numpy as np
from src.evaluator import validate_witness,evaluate
from .coherence import efficiency_lower


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--full-stress',action='store_true');args=parser.parse_args()
    tic=time.perf_counter(); cfg=json.loads(Path('configs/experiment.json').read_text());plan=json.loads(Path('trial/plan.json').read_text())
    freeze=json.loads(Path('trial/freeze.json').read_text())
    for f,h in freeze['files'].items():
        assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h, f+' modified after freeze'
    targets={t['id']:t for t in cfg['targets']+plan['targets']}
    fresh=json.loads(Path('trial/benchmark.json').read_text())['rows'];assert len(fresh)==420
    sat=json.loads(Path('trial/saturation.json').read_text());assert len(sat)==172
    exp=json.loads(Path('trial/exploration.json').read_text());assert len(exp)==48
    rows=fresh+sat
    for r in exp:
        rows.append({**r,'id':f"explore__{r['target']}__{r['method']}__{r['seed']}",'class':'phase-only','positions_lambda':(.5*(np.arange(16)-7.5)).tolist(),'amplitudes':[1.]*16})
    maxgap=0.;violations=[]
    theta=np.linspace(-np.pi/2,np.pi/2,20011);u=np.sin(theta)
    for row in rows:
        row={**row,'class':'phase-only'};target=targets[row['target']];m=validate_witness(cfg,target,row)
        x=np.asarray(row['positions_lambda']);phi=np.asarray(row['phases_rad']);u0=math.sin(math.radians(target['steer_deg']))
        # Third check uses a complex sum on a uniform-theta grid, independent of evaluator grids.
        p=abs(np.exp(1j*(2*np.pi*u[:,None]*x+phi)).mean(axis=1))**2/m['target_power']
        sm=np.abs(u-u0)>=cfg['guard_u'];nm=np.zeros(len(u),bool)
        for lo,hi in target['notches_deg']:nm|=(theta>=np.deg2rad(lo))&(theta<=np.deg2rad(hi))
        score=max(np.max(p[sm]),cfg['notch_weight_power']*np.max(p[nm]))
        assert score<=m['score_upper']+1e-10,row['id']
        if 'efficiency_error_box_lower' in row:assert abs(efficiency_lower(m['coherent_efficiency'],u0)-row['efficiency_error_box_lower'])<1e-12
        maxgap=max(maxgap,m['peak_enclosure_gap_db'])
        if not m['feasible']:violations.append(row['id'])
    # The checker must reject both corrupted scientific claims and invalid constructions.
    for kind in ['metric','phase','amplitude']:
        bad=copy.deepcopy(fresh[0]);target=targets[bad['target']]
        if kind=='metric':bad['metrics']['weighted_peak_db_upper']-=.1
        if kind=='phase':bad['phases_rad'][0]+=.01
        if kind=='amplitude':bad['amplitudes'][0]=.9
        try:validate_witness(cfg,target,bad)
        except ValueError:pass
        else:raise AssertionError('failed to reject '+kind)
    stress=json.loads(Path('trial/robustness.json').read_text());assert len(stress['rows'])==84
    errors=np.random.default_rng(stress['seed']).uniform(-1,1,(64,3,16));byid={r['id']:r for r in fresh};replayed=0
    for s in stress['rows']:
        r=byid[s['id']];target=targets[r['target']];x=np.asarray(r['positions_lambda']);phi=np.asarray(r['phases_rad'])
        assert s['feasible_count']==sum(m['feasible'] for m in s['trials'])
        assert min(m['coherent_efficiency'] for m in s['trials'])>=s['gain_bound']-1e-10
        assert s['adversarial_gain']['minimum_found']>=s['gain_bound']-1e-10
        adversary=np.asarray(s['adversarial_gain']['errors'],float)
        assert adversary.shape==(32,) and np.all(np.abs(adversary)<=1+1e-12)
        u0=math.sin(math.radians(target['steer_deg']));delta=np.deg2rad(2)+2*np.pi*abs(u0)*.005
        aa=1+.03*adversary[16:];pp=phi+2*np.pi*x*u0+delta*adversary[:16]
        attained=abs(np.mean(aa*np.exp(1j*pp)))**2/np.mean(aa**2)
        assert np.isclose(attained,s['adversarial_gain']['minimum_found'],rtol=1e-12,atol=1e-12)
        # Replay fixed samples plus each record's worst gain and worst objective samples.
        indices=set([0,17,63,int(np.argmin([m['coherent_efficiency'] for m in s['trials']])),int(np.argmax([m['weighted_peak_db_upper'] for m in s['trials']]))])
        if args.full_stress:indices=set(range(64))
        for k in sorted(indices):
            e=errors[k];actual=evaluate(cfg,target,x+.005*e[1],phi+np.deg2rad(2)*e[0],1+.03*e[2],grid_n=2049)
            for key,value in s['trials'][k].items():
                if isinstance(value,bool) or value is None:assert value==actual[key]
                else:assert np.isclose(value,actual[key],rtol=2e-8,atol=2e-8)
            replayed+=1
    out=dict(frozen_hashes='pass',witnesses_checked=len(rows),independent_theta_points=20011,max_peak_enclosure_gap_db=maxgap,nominal_infeasible_ids=violations,tampering_rejections=3,stress_records=84,adversarial_vectors_recomputed=84,stress_metrics_replayed=replayed,seconds=time.perf_counter()-tic)
    output=Path('trial/full-check-results.json' if args.full_stress else 'trial/check-results.json')
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
