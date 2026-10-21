"""Trial-informed task portfolio; frozen historical experiment files stay untouched."""
import argparse,copy,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from src.model import Objective,steering,quantize
from src.evaluator import validate_witness,evaluate
from trial.benchmark import hybrid
from trial.coherence import efficiency_lower,required_nominal_eta
from trial.search import gauge_round
from src.optimizers import optimize
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'

def convex_phase_steps(o,phi,iterations=20):
    """Aslan et al. 2019 Eq.4 small-phase linearization, adapted to our gain floor.
    Convex norm constraints, trust bound .15 rad; SLSQP numerical implementation.
    Our weighted mask, gain inequality and quantization differ from their cases.
    Actual nonlinear feasibility is recomputed after every step.
    """
    phase=np.array(phi,float);history=[];n=len(phi)
    for _ in range(iterations):
        weights=np.exp(1j*phase);z=o.A*weights;f=z.sum(axis=1);z0=o.a0*weights;f0=z0.sum();rotation=np.exp(-1j*np.angle(f0))
        def cons(y):
            predicted=f+1j*z@y[:-1];desired=(f0+1j*z0@y[:-1])*rotation
            return np.r_[y[-1]-np.sqrt(o.weight)*np.abs(predicted),desired.real-np.sqrt(o.cfg['minimum_coherent_efficiency'])]
        y0=np.r_[np.zeros(n),np.max(np.sqrt(o.weight)*abs(f))]
        out=minimize(lambda y:y[-1],y0,method='SLSQP',bounds=[(0,0)]+[(-.15,.15)]*(n-1)+[(0,10)],
          constraints=[{'type':'ineq','fun':cons}],options={'maxiter':60,'ftol':1e-9})
        old=o.score(phase);accepted=False
        if out.success:
            for scale in (1.,.5,.25,.125):
                trial=phase+scale*out.x[:-1];p,p0=o.values(trial)
                if p0>=o.cfg['minimum_coherent_efficiency'] and o.score(trial)<old-1e-10:
                    phase=trial;accepted=True;break
        history.append(dict(subproblem_success=bool(out.success),accepted=accepted))
        if not accepted:break
    candidates=[quantize(phi,o.cfg['phase_bits']),gauge_round(o,phase)]
    feasible=[p for p in candidates if o.values(p)[1]>=o.cfg['minimum_coherent_efficiency']-1e-10]
    return min(feasible or candidates,key=o.score),history

def check_candidate(path,task):
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());portfolio=json.loads((OUT/'portfolio.json').read_text())
    if hashlib.sha256((ROOT/'configs/experiment.json').read_bytes()).hexdigest()!=portfolio['config_sha256']:
        raise ValueError('portfolio configuration changed')
    card=next(t for t in portfolio['tasks'] if t['id']==task);row=json.loads(Path(path).read_text())
    if row.get('class')!='phase-only' or row.get('target')!=card['target']['id']:raise ValueError('wrong class/target')
    m=validate_witness(cfg,card['target'],row)
    if not m['feasible']:raise ValueError('infeasible candidate')
    lower=efficiency_lower(m['coherent_efficiency'],np.sin(np.deg2rad(card['target']['steer_deg'])))
    if card['track']=='calibration-margin' and lower<.85:raise ValueError('coherent-efficiency error-box bound fails')
    incumbent=validate_witness(cfg,card['target'],card['incumbent'])
    if not incumbent['feasible']:raise ValueError('infeasible inherited witness')
    return dict(metrics=m,efficiency_error_box_lower=lower,
      established_improvement=m['weighted_peak_db_upper']<incumbent['weighted_peak_db_lower'])

def prepare():
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());targets=json.loads((ROOT/'trial/plan.json').read_text())['targets']
    rows=json.loads((ROOT/'trial/benchmark.json').read_text())['rows'];tasks=[]
    for target in targets:
        valid=[]
        for row in rows:
            if row['target']!=target['id']:continue
            m=validate_witness(cfg,target,row)
            if m['feasible']:valid.append(row)
        for track in ('nominal','calibration-margin'):
            candidates=[r for r in valid if track=='nominal' or efficiency_lower(r['metrics']['coherent_efficiency'],np.sin(np.deg2rad(target['steer_deg'])))>=.85]
            if not candidates:raise ValueError('no valid inherited witness')
            winner=min(candidates,key=lambda r:r['metrics']['weighted_peak_db_upper']);target=copy.deepcopy(target);target['split']='exposed-development'
            tasks.append(dict(id=f"{target['id']}-{track}",track=track,target=target,incumbent=winner,
                scope='Fixed six-bit, 16-element model; margin guarantees coherent efficiency only',status='local preparation; RF review pending'))
    package=dict(model='isotropic-ula-phase-v1',config_sha256=hashlib.sha256((ROOT/'configs/experiment.json').read_bytes()).hexdigest(),
       source_sha256=hashlib.sha256((ROOT/'trial/benchmark.json').read_bytes()).hexdigest(),tasks=tasks,independent_review=False)
    (OUT/'portfolio.json').write_text(json.dumps(package,indent=2)+'\n')
    for card in tasks:
        file=OUT/f"{card['id']}.json";file.write_text(json.dumps(card['incumbent'],indent=2)+'\n');check_candidate(file,card['id'])
    print(f'PASS {len(tasks)} inherited task witnesses from {len(rows)} rechecked designs')

def compare():
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());tasks=json.loads((OUT/'portfolio.json').read_text())['tasks'];rows=[]
    # Diagnostic development comparison, not heldout evidence or an equal-time superiority test.
    for card in [t for t in tasks if t['track']=='calibration-margin'][:4]:
        target=card['target'];local={**cfg,'minimum_coherent_efficiency':required_nominal_eta(np.sin(np.deg2rad(target['steer_deg'])))}
        for name in ('inherited','convex-perturbation'):
            start=time.perf_counter();o=Objective(local,target);phi=np.array(card['incumbent']['phases_rad'])
            if name=='convex-perturbation':phi,history=convex_phase_steps(o,phi)
            else:history=[]
            m=evaluate(cfg,target,o.x,phi)
            rows.append(dict(task=card['id'],method=name,phases_rad=phi.tolist(),metrics=m,seconds=time.perf_counter()-start,history=history))
    (OUT/'published-method-diagnostic.json').write_text(json.dumps(dict(source='https://doi.org/10.1109/LAWP.2019.2937682',
      scope='Equation-4/6 method adaptation to pilot constraints; not reproduction of paper figures or full coupling model',rows=rows),indent=2)+'\n')
    print('PASS diagnostic complete; retain all outcomes')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','compare','check']);p.add_argument('--candidate');p.add_argument('--task');a=p.parse_args()
    if a.action=='prepare':prepare()
    elif a.action=='compare':compare()
    else:
        if not a.candidate or not a.task:p.error('check requires --candidate and --task')
        print(json.dumps(check_candidate(a.candidate,a.task),indent=2))
if __name__=='__main__':main()
