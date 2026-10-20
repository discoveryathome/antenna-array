import argparse
import hashlib
import json
import platform
import time
import warnings
from pathlib import Path
import numpy as np
import scipy
from scipy.signal.windows import chebwin
from .model import positions,steering,quantize
from .evaluator import evaluate,validate_witness
from .optimizers import optimize

ROOT=Path(__file__).resolve().parents[1]

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--split',choices=['development','held-out','all'],default='all');p.add_argument('--output',default='results/candidates.json');args=p.parse_args()
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());x=positions(cfg['element_count'],cfg['spacing_wavelengths']);rows=[];start=time.perf_counter()
    for target in cfg['targets']:
        if args.split!='all' and target['split']!=args.split:continue
        u0=np.sin(np.deg2rad(target['steer_deg']));base=steering(x,u0)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore');taper=chebwin(len(x),at=30)
        taper*=np.sqrt(len(x)/np.sum(taper*taper))
        jobs=[('uniform',None,quantize(base,cfg['phase_bits']),np.ones(len(x)),{}),('chebyshev30',None,base,taper,{})]
        for method in ['coordinate','random','slsqp','de']:
            for seed in ([cfg['seeds'][0]] if method=='coordinate' else cfg['seeds']):
                phi,info=optimize(cfg,target,method,seed);jobs.append((method,seed,phi,np.ones(len(x)),info))
        for method,seed,phi,amp,info in jobs:
            row=dict(id=f"{target['id']}__{method}__{seed}",target=target['id'],split=target['split'],method=method,seed=seed,
                     positions_lambda=x.tolist(),phases_rad=phi.tolist(),amplitudes=amp.tolist(),search=info)
            row['class']='amplitude-reference' if method=='chebyshev30' else 'phase-only'
            row['metrics']=evaluate(cfg,target,x,phi,amp)
            validate_witness(cfg,target,row);rows.append(row)
            print(target['id'],method,seed,'weighted dB',round(row['metrics']['weighted_peak_db_upper'],3),'SLL',round(row['metrics']['sidelobe_db_upper'],3),'notch',round(row['metrics']['notch_db_upper'],3),'eta',round(row['metrics']['coherent_efficiency'],4),'feasible',row['metrics']['feasible'],flush=True)
    output=ROOT/args.output;output.parent.mkdir(parents=True,exist_ok=True)
    record=dict(config_sha256=digest(ROOT/'configs/experiment.json'),source_sha256={p.name:digest(p) for p in sorted((ROOT/'src').glob('*.py'))},
                environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),processor=platform.processor()),
                elapsed_seconds=time.perf_counter()-start,rows=rows)
    output.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    print('Saved',output,'seconds',record['elapsed_seconds'])

if __name__=='__main__':main()
