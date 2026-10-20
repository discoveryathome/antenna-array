"""Frozen unseen-target evaluation; all attempts retained, no benchmark tuning."""
import json,time,hashlib,platform
from pathlib import Path
import numpy as np
from src.model import Objective
from src.evaluator import evaluate
from src.optimizers import optimize
from .search import discrete_search,local_refine
from .coherence import efficiency_lower,required_nominal_eta


def hybrid(cfg,target,seed,basephi,baseinfo):
    tic=time.perf_counter();o=Objective(cfg,target)
    refined,diag=local_refine(o,basephi)
    paired,history=discrete_search(o,seed+10000,start=refined,budget=2000,mode='paired')
    pool=[np.asarray(basephi),refined,paired]
    usable=[p for p in pool if o.values(p)[1]>=cfg['minimum_coherent_efficiency']-1e-10]
    if not usable:usable=pool
    scores=[o.score(p) for p in usable];best=usable[int(np.argmin(scores))]
    return best,dict(elapsed_seconds=baseinfo['elapsed_seconds']+time.perf_counter()-tic,objective_calls=baseinfo['objective_calls']+o.calls,diagnostics=diag,refinement_history=history,base_phase=basephi.tolist())


def main():
    cfg=json.loads(Path('configs/experiment.json').read_text());plan=json.loads(Path('trial/plan.json').read_text());rows=[];start=time.perf_counter()
    for target in plan['targets']:
        for seed in plan['evaluation_seeds']:
            u0=np.sin(np.deg2rad(target['steer_deg']));margin=required_nominal_eta(u0)
            # Order alternates by seed to reduce obvious scheduling biases.
            jobs=[('de160',160,.85),('de200',200,.85),('de640',640,.85),('margin-de160',160,margin),('margin-de200',200,margin)]
            if seed%2:jobs=jobs[::-1]
            saved={}
            for name,gens,floor in jobs:
                local={**cfg,'de_generations':gens,'minimum_coherent_efficiency':floor}
                phi,info=optimize(local,target,'de',seed);saved[name]=(phi,info,local)
            for name,base in [('hybrid','de160'),('margin-hybrid','margin-de160')]:
                phi,info,local=saved[base];q,inf=hybrid(local,target,seed,phi,info);saved[name]=(q,inf,local)
            for name,(phi,info,local) in saved.items():
                x=Objective(cfg,target).x;m=evaluate(cfg,target,x,phi)
                row=dict(id=f"{target['id']}__{name}__{seed}",target=target['id'],group=target['group'],method=name,seed=seed,
                         positions_lambda=x.tolist(),phases_rad=phi.tolist(),amplitudes=[1.]*len(x),metrics=m,search=info,design_gain_floor=local['minimum_coherent_efficiency'],
                         efficiency_error_box_lower=efficiency_lower(m['coherent_efficiency'],u0))
                row['class']='phase-only';rows.append(row)
            print(target['id'],seed,'DE',round(saved['de160'][1]['elapsed_seconds'],2),'scores',[(r['method'],round(r['metrics']['weighted_peak_db_upper'],3),round(r['efficiency_error_box_lower'],4)) for r in rows[-7:]],flush=True)
            Path('trial/benchmark.json').write_text(json.dumps(dict(rows=rows,elapsed_seconds=time.perf_counter()-start),indent=2)+'\n')
    print('COMPLETE',len(rows),'seconds',time.perf_counter()-start,flush=True)
if __name__=='__main__':main()
