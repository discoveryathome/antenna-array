"""Locate numerical point witnesses; the integer verifier checks them independently.

Root locations are merely candidate evaluation points, not completeness claims.
No phase vector outside the predeclared neighborhood is generated.
"""
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from src.model import Objective, regions
from trial.coherence import required_nominal_eta
from certify_neighborhood import neighbors

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = 'fresh-08-calibration-margin'


def main():
    cfg = json.loads((ROOT/'configs/experiment.json').read_text())
    card = next(t for t in json.loads((ROOT/'research/readiness-20261021/portfolio.json').read_text())['tasks'] if t['id']==TASK)
    target = card['target']
    q0 = np.rint(np.asarray(card['incumbent']['phases_rad'])*64/(2*np.pi)).astype(int)%64
    qs = np.asarray([q for q,_ in neighbors(q0.tolist())])
    objective = Objective(cfg,target)
    u0,sides,notches = regions(target,cfg['guard_u'])
    segments = [(a,b,1.) for a,b in sides]+[(a,b,cfg['notch_weight_power']) for a,b in notches]
    points,us = [],[]
    for region,(a,b,weight) in enumerate(segments):
        n = max(17,int(np.ceil((b-a)*(cfg['optimizer_grid_n']-1)/2))+1)
        us.extend(np.linspace(a,b,n))
        points.extend(dict(region=region,numerator=i,denominator=n-1) for i in range(n))
    assert np.array_equal(us,objective.u)
    w = np.exp(2j*np.pi*qs/64)
    p0 = abs(w@objective.a0)**2
    weighted = abs(w@objective.A.T)**2*objective.weight
    indices = np.argmax(weighted,axis=1)
    selected = [points[i] for i in indices]
    scores = weighted[np.arange(len(qs)),indices]/p0
    eligible = p0>=required_nominal_eta(u0,slack=0)
    nearest = np.argsort(np.where(eligible,scores,np.inf))[:8]
    refinements = []
    k = 2*np.pi*objective.x
    for index in nearest:
        z = np.exp(2j*np.pi*qs[index]/64)/16
        def value(u):
            terms = np.exp(1j*np.outer(np.atleast_1d(u),k))*z
            f = terms.sum(axis=1)
            df = (terms*(1j*k)).sum(axis=1)
            return abs(f)**2,2*np.real(np.conj(f)*df)
        best = (-1.,None)
        for region,(a,b,weight) in enumerate(segments):
            grid = np.linspace(a,b,2049)
            derivative = value(grid)[1]
            brackets = np.flatnonzero(derivative[:-1]*derivative[1:]<0)
            roots = [brentq(lambda u:float(value(u)[1][0]),grid[i],grid[i+1],xtol=1e-14) for i in brackets]
            for u in (a,b,*roots):
                score = weight*float(value(u)[0][0])/p0[index]
                point = dict(region=region,u_decimal=repr(float(u)))
                if u==a or u==b:
                    point = dict(region=region,numerator=int(u==b),denominator=1)
                if score>best[0]:
                    best = score,point
        selected[index] = best[1]
        refinements.append(dict(index=int(index),numerical_score=best[0],point=best[1]))
    data = dict(task=TASK,incumbent_bins=q0.tolist(),points=selected,
        refined_points=refinements,scope='One point per enumerated neighbor; numerical locations alone carry no proof.',
        numerical_grid='Original Objective grid, with eight nearest eligible scores refined by stationary-root point locations.')
    (HERE/'point-witnesses.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Located',len(selected),'point witnesses; refined indices',nearest.tolist())


if __name__ == '__main__':
    main()
