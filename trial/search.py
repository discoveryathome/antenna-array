"""Reasoned extensions: coupled discrete moves and global-phase-aware rounding."""
import math,time
import numpy as np
from scipy.optimize import minimize
from src.model import Objective,quantize,steering


def gauge_round(o,phi):
    """Enumerate all distinct rounding intervals over a global phase-bin shift.

    Global phase is irrelevant before quantization. Its position relative to
    rounding thresholds changes relative rounded phase errors. There are at most
    N intervals per bin, so only O(N) representatives need checking.
    """
    step=2*np.pi/(2**o.cfg['phase_bits'])
    breaks=np.unique(np.r_[0.,step,np.mod(step*.5-np.asarray(phi),step)])
    shifts=(breaks[:-1]+breaks[1:])/2
    trials=quantize(np.asarray(phi)[None,:]+shifts[:,None],o.cfg['phase_bits'])
    score=o.score_batch(trials);return trials[np.argmin(score)]


def neighbors(q,mode='paired'):
    """Single +/-1,2 phase bins and equal/opposite changes on mirror pairs."""
    n=len(q);moves=[]
    for step in [-2,-1,1,2]:
        for i in range(n):
            d=np.zeros(n);d[i]=step;moves.append(d)
        if mode=='paired':
            for i in range(n//2):
                for sign in [-1,1]:
                    d=np.zeros(n);d[i]=step;d[n-1-i]=sign*step;moves.append(d)
    return (q[None,:]+np.array(moves))%64


def discrete_search(o,seed,start=None,budget=10000,mode='paired',gain_floor=None):
    rng=np.random.default_rng(seed);step=2*np.pi/(2**o.cfg['phase_bits'])
    initial=quantize(steering(o.x,o.u0) if start is None else start,o.cfg['phase_bits'])
    q=np.rint(initial/step).astype(int)%64;best=q.copy();bestscore=o.score(q*step);current=bestscore
    history=[dict(evaluations=o.calls,score=bestscore,phase_bins=best.tolist())];initial_calls=o.calls
    stalls=0
    while o.calls-initial_calls<budget:
        proposals=neighbors(q,mode)
        proposals=proposals[:max(0,budget-(o.calls-initial_calls))]
        if not len(proposals):break
        scores=o.score_batch(proposals*step);i=int(np.argmin(scores))
        if scores[i]<current-1e-12:
            q=proposals[i];current=float(scores[i]);stalls=0
            if current<bestscore:
                best=q.copy();bestscore=current;history.append(dict(evaluations=o.calls,score=bestscore,phase_bins=best.astype(int).tolist()))
        else:
            # Escapes have fixed, bounded perturbation sizes; keep incumbent.
            stalls+=1;q=best.copy()
            if mode=='paired':
                ids=rng.choice(len(q)//2,size=min(2+stalls//4,5),replace=False)
                for j in ids:
                    d=int(rng.choice([-4,-3,-2,2,3,4]));q[j]=(q[j]+d)%64;q[-1-j]=(q[-1-j]+d)%64
            else:
                ids=rng.choice(len(q),size=min(4+stalls//4,10),replace=False)
                q[ids]=(q[ids]+rng.choice([-4,-3,-2,2,3,4],size=len(ids)))%64
            current=o.score(q*step)
    return best*step,history


def local_refine(o,phi,maxiter=120):
    """Warm-start continuous minimax, then gauge-aware quantization."""
    base=np.asarray(phi);n=len(base)
    def unpack(y):return base+np.r_[0.,y[:-1]]
    def cons(y):
        p,p0=o.values(unpack(y));return np.r_[y[-1]*p0-o.weight*p,p0-o.cfg['minimum_coherent_efficiency']]
    def jac(y):
        p,p0,dp,dp0=o.values(unpack(y),True)
        return np.vstack((np.column_stack(((y[-1]*dp0[None,:]-o.weight[:,None]*dp)[:,1:],np.full(len(p),p0))),np.r_[dp0[1:],0.]))
    y0=np.r_[np.zeros(n-1),o.score(base)]
    out=minimize(lambda y:y[-1],y0,jac=lambda y:np.r_[np.zeros(n-1),1.],method='SLSQP',bounds=[(-.6,.6)]*(n-1)+[(0,100)],constraints=[{'type':'ineq','fun':cons,'jac':jac}],options={'maxiter':maxiter,'ftol':1e-10})
    plain=quantize(unpack(out.x),o.cfg['phase_bits']);gauged=gauge_round(o,unpack(out.x))
    return gauged,dict(success=bool(out.success),iterations=int(out.nit),plain_rounding_score=o.score(plain),gauge_rounding_score=o.score(gauged),continuous_score=o.score(unpack(out.x)))
