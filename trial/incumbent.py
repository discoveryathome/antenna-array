"""Follow-up hill-climbs and extra-compute control on the old development cases."""
import json,time
from pathlib import Path
import numpy as np
from src.model import Objective
from src.evaluator import evaluate
from src.optimizers import optimize
from .search import discrete_search,local_refine
from .benchmark import hybrid
from .coherence import required_nominal_eta,efficiency_lower

def main():
    cfg=json.loads(Path('configs/experiment.json').read_text());original=json.loads(Path('results/candidates.json').read_text())['rows'];rows=[]
    for target in [t for t in cfg['targets'] if t['split']=='held-out']:
        inc=min((r for r in original if r['target']==target['id'] and r['class']=='phase-only' and r['metrics']['feasible']),key=lambda r:r['metrics']['score_upper']);u0=np.sin(np.deg2rad(target['steer_deg']))
        for seed in range(5001,5021):
            phi,info=optimize(cfg,target,'de',seed)
            for name,q,inf in [('more-de',phi,info),('more-de-hybrid',*hybrid(cfg,target,seed,phi,info))]:
                m=evaluate(cfg,target,inc['positions_lambda'],q);rows.append(dict(id=f"{target['id']}__{name}__{seed}",target=target['id'],method=name,seed=seed,phases_rad=q.tolist(),positions_lambda=inc['positions_lambda'],amplitudes=[1.]*16,metrics=m,search=inf,efficiency_error_box_lower=efficiency_lower(m['coherent_efficiency'],u0)))
            print(target['id'],seed,[(r['method'],round(r['metrics']['weighted_peak_db_upper'],4)) for r in rows[-2:]],flush=True)
            Path('trial/saturation.json').write_text(json.dumps(rows,indent=2)+'\n')
        for seed in [71,72,73]:
            local={**cfg,'minimum_coherent_efficiency':required_nominal_eta(u0)};o=Objective(local,target);tic=time.perf_counter()
            q,h=discrete_search(o,seed,start=inc['phases_rad'],budget=5000);q,diag=local_refine(o,q);q,h2=discrete_search(o,seed+100,start=q,budget=2000)
            m=evaluate(cfg,target,inc['positions_lambda'],q)
            rows.append(dict(id=f"{target['id']}__robust-incumbent__{seed}",target=target['id'],method='robust-incumbent',seed=seed,phases_rad=q.tolist(),positions_lambda=inc['positions_lambda'],amplitudes=[1.]*16,metrics=m,search=dict(elapsed_seconds=time.perf_counter()-tic,objective_calls=o.calls),design_gain_floor=local['minimum_coherent_efficiency'],efficiency_error_box_lower=efficiency_lower(m['coherent_efficiency'],u0)))
        Path('trial/saturation.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
