"""Reoptimize predeclared first target/seed, without replacing any evidence."""
import json,time
from pathlib import Path
import numpy as np
from src.optimizers import optimize
from src.evaluator import evaluate
from src.model import Objective
from .benchmark import hybrid
from .coherence import required_nominal_eta

def main():
    tic=time.perf_counter();cfg=json.loads(Path('configs/experiment.json').read_text());plan=json.loads(Path('trial/plan.json').read_text());target=plan['targets'][0];seed=plan['evaluation_seeds'][0];margin=required_nominal_eta(np.sin(np.deg2rad(target['steer_deg'])));stored={r['method']:r for r in json.loads(Path('trial/benchmark.json').read_text())['rows'] if r['target']==target['id'] and r['seed']==seed};saved={};out=[]
    for name,gens,floor in [('de160',160,.85),('de200',200,.85),('de640',640,.85),('margin-de160',160,margin),('margin-de200',200,margin)]:
        local={**cfg,'de_generations':gens,'minimum_coherent_efficiency':floor};p,info=optimize(local,target,'de',seed);saved[name]=(p,info,local)
    for name,base in [('hybrid','de160'),('margin-hybrid','margin-de160')]:
        p,info,local=saved[base];p,info=hybrid(local,target,seed,p,info);saved[name]=(p,info,local)
    for name,(p,info,local) in saved.items():
        r=stored[name];equal=bool(np.array_equal(p,r['phases_rad']));assert equal,name+' does not replay exactly';assert info['objective_calls']==r['search']['objective_calls'];out.append(dict(method=name,phase_array_exact=equal,objective_calls=info['objective_calls']))
    Path('trial/replay-results.json').write_text(json.dumps(dict(target=target['id'],seed=seed,rows=out,seconds=time.perf_counter()-tic),indent=2)+'\n');print('PASS all seven methods reproduce identical discrete designs and objective counts')
if __name__=='__main__':main()
