import json,time
from pathlib import Path
import numpy as np
from src.model import Objective
from src.evaluator import evaluate
from src.optimizers import optimize
from .search import discrete_search,local_refine

def main():
    cfg=json.loads(Path('configs/experiment.json').read_text());old=json.loads(Path('results/candidates.json').read_text())['rows'];rows=[]
    for target in [t for t in cfg['targets'] if t['split']=='held-out']:
        feasible=[r for r in old if r['target']==target['id'] and r['class']=='phase-only' and r['metrics']['feasible']];inc=min(feasible,key=lambda r:r['metrics']['score_upper'])
        print('\nCASE',target['id'],'incumbent',inc['metrics']['weighted_peak_db_upper'],flush=True)
        for mode in ['single','paired','hybrid','margin-hybrid']:
            for seed in [71,72,73]:
                localcfg={**cfg,'minimum_coherent_efficiency':.88} if mode=='margin-hybrid' else cfg
                o=Objective(localcfg,target);tic=time.perf_counter()
                phi,h=discrete_search(o,seed,start=inc['phases_rad'],budget=5000,mode='single' if mode=='single' else 'paired')
                diag={}
                if 'hybrid' in mode:
                    phi,diag=local_refine(o,phi);phi,h2=discrete_search(o,seed+100,start=phi,budget=3000,mode='paired');h+=h2
                m=evaluate(cfg,target,o.x,phi)
                row=dict(target=target['id'],method=mode,seed=seed,phases_rad=phi.tolist(),metrics=m,calls=o.calls,seconds=time.perf_counter()-tic,history=h,diagnostics=diag)
                rows.append(row);print(mode,seed,round(m['weighted_peak_db_upper'],4),'eta',round(m['coherent_efficiency'],5),'calls',o.calls,'s',round(row['seconds'],2),'valid',m['feasible'],flush=True)
        Path('trial/exploration.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
