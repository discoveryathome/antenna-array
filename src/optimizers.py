"""Two intelligent phase searches plus ablations. Seeded, single-process only."""
import time
import numpy as np
from scipy.optimize import minimize
from .model import Objective, steering, quantize


def polish(o,phi,sweeps):
    """Deterministic discrete +/- one phase-bin coordinate descent."""
    phi=quantize(phi,o.cfg['phase_bits']); step=2*np.pi/(2**o.cfg['phase_bits'])
    score=o.score(phi)
    for _ in range(sweeps):
        changed=False
        for j in range(len(phi)):
            trials=np.repeat(phi[None,:],2,axis=0);trials[:,j]+=[-step,step]
            values=o.score_batch(trials); k=int(np.argmin(values))
            if values[k]<score-1e-12:
                phi=trials[k];score=float(values[k]);changed=True
        if not changed:break
    return quantize(phi,o.cfg['phase_bits'])


def slsqp(o,rng):
    """Multistart epigraph minimax with analytic phase Jacobians and gain constraint."""
    n=len(o.x);base=steering(o.x,o.u0); best=None;bestval=float('inf'); diagnostics=[]
    for run in range(o.cfg['slsqp_starts']):
        offset=np.zeros(n-1) if run==0 else rng.normal(0,.20,n-1)
        def unpack(y):return base+np.r_[0.,y[:-1]]
        def constraint(y):
            p,p0=o.values(unpack(y))
            return np.r_[y[-1]*p0-o.weight*p,p0-o.cfg['minimum_coherent_efficiency']]
        def jac(y):
            p,p0,dp,dp0=o.values(unpack(y),True)
            a=np.column_stack(((y[-1]*dp0[None,:]-o.weight[:,None]*dp)[:,1:],np.full(len(p),p0)))
            return np.vstack((a,np.r_[dp0[1:],0.]))
        initial=np.r_[offset,o.score(base+np.r_[0.,offset])]
        out=minimize(lambda y:y[-1],initial,jac=lambda y:np.r_[np.zeros(n-1),1.],
                     method='SLSQP',bounds=[(-1.2,1.2)]*(n-1)+[(0,100)],
                     constraints=[{'type':'ineq','fun':constraint,'jac':jac}],
                     options={'maxiter':o.cfg['slsqp_maxiter'],'ftol':1e-10})
        phi=unpack(out.x); val=o.score(quantize(phi,o.cfg['phase_bits']))
        diagnostics.append({'success':bool(out.success),'iterations':int(out.nit),'message':str(out.message)})
        if val<bestval:best=phi;bestval=val
    return best,diagnostics


def differential_evolution(o,rng):
    """DE/current-to-best/1/bin on residual phases, fitness after quantization.

    Bounds restrict residual search to +/-1.2 rad, not the admissible hardware set.
    Population includes conventional steering. Fixed F=.65, CR=.8.
    """
    n=len(o.x);base=steering(o.x,o.u0); size=o.cfg['de_population']
    pop=rng.uniform(-.45,.45,(size,n));pop[0]=0
    score=o.score_batch(quantize(base+pop,o.cfg['phase_bits']))
    for _ in range(o.cfg['de_generations']):
        best=pop[np.argmin(score)].copy();trials=[]
        for i in range(size):
            choices=np.delete(np.arange(size),i);a,b=rng.choice(choices,2,replace=False)
            mutant=np.clip(pop[i]+.65*(best-pop[i])+.65*(pop[a]-pop[b]),-1.2,1.2)
            cross=rng.random(n)<.8;cross[rng.integers(n)]=True
            trials.append(np.where(cross,mutant,pop[i]))
        trials=np.array(trials)
        new=o.score_batch(quantize(base+trials,o.cfg['phase_bits']))
        good=new<score;pop[good]=trials[good];score[good]=new[good]
    return base+pop[np.argmin(score)],[]


def random_search(o,rng):
    """Nonadaptive control with the same core number of candidates as DE."""
    base=steering(o.x,o.u0);best=quantize(base,o.cfg['phase_bits']);value=o.score(best)
    for _ in range(o.cfg['de_generations']+1):
        trials=quantize(base+rng.uniform(-.45,.45,(o.cfg['de_population'],len(base))),o.cfg['phase_bits'])
        score=o.score_batch(trials);k=int(np.argmin(score))
        if score[k]<value:best=trials[k];value=float(score[k])
    return best,[]


def optimize(cfg,target,method,seed):
    o=Objective(cfg,target);rng=np.random.default_rng(seed);start=time.perf_counter()
    if method=='slsqp':phi,diagnostics=slsqp(o,rng)
    elif method=='de':phi,diagnostics=differential_evolution(o,rng)
    elif method=='random':phi,diagnostics=random_search(o,rng)
    elif method=='coordinate':phi=steering(o.x,o.u0);diagnostics=[]
    else:raise ValueError(method)
    pre=quantize(phi,cfg['phase_bits']);pre_score=o.score(pre)
    # Random control intentionally receives no adaptive polish.
    if method!='random':phi=polish(o,phi,cfg['coordinate_sweeps'])
    else:phi=pre
    return phi,dict(elapsed_seconds=time.perf_counter()-start,objective_calls=o.calls,
                    pre_polish_score=pre_score,post_polish_score=o.score(phi),solver_diagnostics=diagnostics)
