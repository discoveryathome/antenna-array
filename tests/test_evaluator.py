import copy
import json
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import quad
from scipy.signal.windows import chebwin
from src.model import positions, power, quantize, Objective
from src.evaluator import radiation, peak_enclosure, evaluate, integrated_power, validate_witness

CFG=json.loads((Path(__file__).parents[1]/'configs/experiment.json').read_text())
T=CFG['targets'][0]


def test_independent_trigonometric_and_complex_evaluators():
    r=np.random.default_rng(91)
    x=r.normal(size=16); p=r.normal(size=16); a=r.uniform(.5,1.5,16); u=r.uniform(-1,1,731)
    np.testing.assert_allclose(radiation(u,x,p,a),power(u,x,p,a),atol=2e-15)


def test_uniform_closed_form_and_efficiency():
    x=positions(); u=np.linspace(-.99,.99,1001); u=u[abs(u)>1e-10]
    expected=(np.sin(16*np.pi*u/2)/(16*np.sin(np.pi*u/2)))**2
    np.testing.assert_allclose(radiation(u,x,np.zeros(16),np.ones(16)),expected,atol=2e-15)
    m=evaluate(CFG,T,x,np.zeros(16))
    assert m['coherent_efficiency']==pytest.approx(1)
    assert m['directivity_target']==pytest.approx(16)
    assert -13.2<m['sidelobe_db_lower']<-13.1
    assert .110<m['hpbw_u']<.112
    assert m['feasible']


def test_chebyshev_reference():
    a=chebwin(16,at=50); a=a/np.linalg.norm(a)*4
    cfg={**CFG,'guard_u':.32}
    m=evaluate(cfg,T,positions(),np.zeros(16),a)
    assert m['sidelobe_db_lower']==pytest.approx(-50,abs=.01)
    assert m['sidelobe_db_upper']>=-50


def test_analytic_integral_matches_quadrature():
    r=np.random.default_rng(7); x=r.uniform(-4,4,16); p=r.uniform(-3,3,16); a=r.uniform(.8,1.2,16)
    exact=integrated_power(x,p,a,-.73,.91)
    numeric=quad(lambda u:radiation([u],x,p,a)[0],-.73,.91,epsabs=1e-12)[0]
    assert exact==pytest.approx(numeric,abs=1e-12)


def test_bound_catches_peak_missed_by_coarse_grid():
    x=np.array([-8.,8.]); p=-2*np.pi*x*.03125; a=np.ones(2)
    # Deliberately coarse samples are not safe as peak estimates.
    coarse=peak_enclosure(x,p,a,[(-1,1)],33)
    dense=peak_enclosure(x,p,a,[(-1,1)],100009)
    assert dense['lower']>coarse['lower']+.4
    assert coarse['upper']>=dense['lower']


def test_bounds_enclose_unrelated_dense_grid():
    r=np.random.default_rng(88); x=positions(); p=r.uniform(-3,3,16); a=r.uniform(.7,1.3,16)
    b=peak_enclosure(x,p,a,[(-.81,.94)],401)
    fine=radiation(np.linspace(-.81,.94,123457),x,p,a).max()
    assert b['lower']<=fine+1e-7<=b['upper']+1e-7


def witness():
    return {'class':'phase-only','positions_lambda':positions().tolist(), 'phases_rad':[0.]*16,'amplitudes':[1.]*16}


def test_reject_false_claim_and_invalid_hardware():
    w=witness(); w['metrics']=evaluate(CFG,T,positions(),np.zeros(16)); validate_witness(CFG,T,w)
    w['metrics']['sidelobe_db_upper']=-40
    with pytest.raises(ValueError,match='wrong claim'): validate_witness(CFG,T,w)
    for field, value in [('phases_rad',.0123),('amplitudes',.7),('positions_lambda',-20),('phases_rad',float('nan'))]:
        w=witness(); w[field][0]=value
        with pytest.raises(ValueError):validate_witness(CFG,T,w)


def test_quantization_and_gradient():
    r=np.random.default_rng(14); p=r.normal(size=16)
    q=quantize(p); np.testing.assert_allclose(q*64/(2*np.pi),np.round(q*64/(2*np.pi)),atol=1e-12)
    o=Objective(CFG,T); _,_,dp,dp0=o.values(p,jac=True); eps=1e-6
    for j in [0,7,15]:
        d=np.zeros(16);d[j]=eps
        a,a0=o.values(p+d);b,b0=o.values(p-d)
        np.testing.assert_allclose((a-b)/(2*eps),dp[:,j],atol=1e-9)
        assert (a0-b0)/(2*eps)==pytest.approx(dp0[j],abs=1e-9)
