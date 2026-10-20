"""Small affordability probe; does not enter the scientific leaderboard."""
import json,time,resource,platform
from pathlib import Path
import numpy as np
from src.model import Objective,steering

def main():
    cfg=json.loads(Path('configs/experiment.json').read_text());target=cfg['targets'][0];rng=np.random.default_rng(19);out=[]
    for n in [16,32,64,128,256]:
        c={**cfg,'element_count':n,'guard_u':.15*16/n,'optimizer_grid_n':max(513,n*32+1)}
        tic=time.perf_counter();o=Objective(c,target);build=time.perf_counter()-tic
        trials=steering(o.x,o.u0)+rng.uniform(-.4,.4,(256,n));tic=time.perf_counter();o.score_batch(trials);elapsed=time.perf_counter()-tic
        out.append(dict(elements=n,angular_samples=len(o.u),candidates=256,objective_matrix_bytes=o.A.nbytes,build_seconds=build,batch_seconds=elapsed,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    Path('trial/scaling.json').write_text(json.dumps(dict(platform=platform.platform(),rows=out,note='Descriptive CPU affordability probe, concurrent workloads present. Masks/grid density change with N. Not a cross-size performance or scientific-quality comparison. macOS ru_maxrss units are bytes.'),indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
