import numpy as np
from scipy.optimize import minimize
from src.model import Objective,steering,quantize,positions
from trial.search import gauge_round
from trial.coherence import efficiency_lower,required_nominal_eta
import json
from pathlib import Path
CFG=json.loads(Path('configs/experiment.json').read_text())

def test_global_phase_rounding_covers_dense_offsets():
    o=Objective(CFG,CFG['targets'][0]);phi=np.random.default_rng(88).normal(0,.3,16)
    candidate=gauge_round(o,phi)
    dense=quantize(phi+np.linspace(0,2*np.pi/64,3000,endpoint=False)[:,None])
    assert o.score(candidate)<=min(o.score_batch(dense))+1e-12


def test_coherence_angle_bound_random_errors():
    rng=np.random.default_rng(121);x=positions()
    for u0 in [-.7,0.,.43]:
        for _ in range(8):
            residual=rng.normal(0,.28,16);nominal=abs(np.mean(np.exp(1j*residual)))**2
            eps=rng.uniform(-1,1,(1000,3,16));amp=1+.03*eps[:,2]
            p=residual+np.deg2rad(2)*eps[:,0]+2*np.pi*u0*.005*eps[:,1]
            eta=abs(np.mean(amp*np.exp(1j*p),axis=1))**2/np.mean(amp**2,axis=1)
            assert eta.min()>=efficiency_lower(nominal,u0)-1e-12


def test_coherence_bound_against_adversarial_minimization():
    rng=np.random.default_rng(22)
    for u0 in [-.6,0,.4]:
        phase=rng.normal(0,.29,16);nominal=abs(np.mean(np.exp(1j*phase)))**2
        delta=np.deg2rad(2)+2*np.pi*abs(u0)*.005
        def eta(e):
            a=1+.03*e[16:];f=np.mean(a*np.exp(1j*(phase+delta*e[:16])))
            return abs(f)**2/np.mean(a*a)
        best=min(minimize(eta,rng.uniform(-1,1,32),bounds=[(-1,1)]*32,method='L-BFGS-B').fun for _ in range(4))
        assert best>=efficiency_lower(nominal,u0)-1e-10


def test_required_margin_and_zero_errors():
    for u0 in np.linspace(-.7,.7,15):
        eta=required_nominal_eta(u0)
        assert efficiency_lower(eta,u0)>.85
    for eta in [.4,.85,.9,1.]:assert abs(efficiency_lower(eta,0,0,0,0)-eta)<1e-12
