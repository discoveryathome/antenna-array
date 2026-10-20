"""Fresh calibration trials, fixed before inspection of complete benchmark."""
import argparse,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from src.model import Objective
from src.evaluator import evaluate
from .coherence import efficiency_lower


def adversarial_gain(row,u0,seed=5454):
    rng=np.random.default_rng(seed);x=np.asarray(row['positions_lambda']);p=np.asarray(row['phases_rad'])+2*np.pi*x*u0
    delta=np.deg2rad(2)+2*np.pi*abs(u0)*.005
    def eta(e):
        a=1+.03*e[16:];f=np.mean(a*np.exp(1j*(p+delta*e[:16])));return abs(f)**2/np.mean(a*a)
    runs=[minimize(eta,rng.uniform(-1,1,32),method='L-BFGS-B',bounds=[(-1,1)]*32,options={'maxiter':100,'ftol':1e-12}) for _ in range(3)]
    best=min(runs,key=lambda r:r.fun)
    return dict(minimum_found=float(best.fun),successes=sum(r.success for r in runs),starts=len(runs),errors=best.x.tolist(),note='Adversarial numerical search, not a global minimum certificate')


def main():
    p=argparse.ArgumentParser();p.add_argument('--wait',action='store_true');a=p.parse_args();start=time.monotonic()
    plan=json.loads(Path('trial/plan.json').read_text());cfg=json.loads(Path('configs/experiment.json').read_text());expected=len(plan['targets'])*len(plan['evaluation_seeds'])*7
    while True:
        try:
            data=json.loads(Path('trial/benchmark.json').read_text())
            if len(data['rows'])==expected:break
        except (OSError,json.JSONDecodeError):pass
        if not a.wait or time.monotonic()-start>2400:raise RuntimeError('complete frozen benchmark not available')
        time.sleep(10)
    rng=np.random.default_rng(11235813);errors=rng.uniform(-1,1,(64,3,16));out=[];targets={t['id']:t for t in plan['targets']}
    for row in data['rows']:
        if row['seed']!=plan['evaluation_seeds'][0]:continue
        target=targets[row['target']];u0=np.sin(np.deg2rad(target['steer_deg']));x=np.asarray(row['positions_lambda']);phi=np.asarray(row['phases_rad']);trials=[]
        for e in errors:
            m=evaluate(cfg,target,x+.005*e[1],phi+np.deg2rad(2)*e[0],1+.03*e[2],grid_n=2049)
            trials.append({k:m[k] for k in ['weighted_peak_db_upper','notch_db_upper','sidelobe_db_upper','coherent_efficiency','hpbw_u','pointing_error_u','feasible']})
        adversary=adversarial_gain(row,u0)
        lower=efficiency_lower(row['metrics']['coherent_efficiency'],u0)
        assert min(t['coherent_efficiency'] for t in trials)>=lower-1e-10
        assert adversary['minimum_found']>=lower-1e-10
        out.append(dict(id=row['id'],target=row['target'],method=row['method'],trials=trials,feasible_count=sum(t['feasible'] for t in trials),gain_bound=lower,adversarial_gain=adversary))
        print('STRESS',row['id'],out[-1]['feasible_count'],'/64','bound',round(lower,4),'adversary',round(adversary['minimum_found'],4),flush=True)
        Path('trial/robustness.json').write_text(json.dumps(dict(seed=11235813,representative_seed=901,draws=64,rows=out),indent=2)+'\n')
if __name__=='__main__':main()
