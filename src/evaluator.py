"""Independent evaluator: real trigonometric sums, no optimization model imports.

Peak enclosures use a global bound on the second derivative of power and
piecewise linear interpolation. Analytical in real arithmetic; float64 with
1e-12 padding is NOT a directed-rounding/formal interval certificate.
"""
import math
import numpy as np
from scipy.optimize import brentq, minimize_scalar


def radiation(u, x, phi, amplitude):
    u = np.atleast_1d(u).astype(float)
    re = np.zeros(len(u)); im = np.zeros(len(u))
    for xx, pp, aa in zip(x, phi, amplitude, strict=True):
        angle = 2*math.pi*xx*u + pp
        re += aa*np.cos(angle)
        im += aa*np.sin(angle)
    return (re*re+im*im)/len(x)**2


def second_derivative_bound(x, amplitude):
    # P'' = -sum_ij a_i a_j (2 pi (x_i-x_j))² cos(...)/N².
    # Translation invariant; direct pairwise formula avoids moment cancellation.
    return sum(abs(ai*aj)*(2*math.pi*(xi-xj))**2
               for xi,ai in zip(x,amplitude) for xj,aj in zip(x,amplitude))/len(x)**2


def peak_enclosure(x, phi, amplitude, intervals, grid_n=10007):
    bound = second_derivative_bound(x, amplitude)
    lower = 0.; upper = 0.; arg = None
    for left,right in intervals:
        n = max(3, int(math.ceil((right-left)*(grid_n-1)/2))+1)
        u = np.linspace(left,right,n)
        p = radiation(u,x,phi,amplitude)
        k = int(np.argmax(p))
        if p[k] >= lower:
            lower = float(p[k]); arg = float(u[k])
        h = (right-left)/(n-1)
        upper = max(upper,float(np.max(p))+bound*h*h/8+1e-12)
    return {'lower':lower,'upper':upper,'argmax_sample_u':arg}


def integrated_power(x,phi,amp,left,right):
    """Exact exponential integral evaluated in float64; np.sinc uses pi units."""
    x,phi,amp = map(np.asarray,(x,phi,amp))
    d = x[:,None]-x[None,:]
    midpoint = (left+right)/2
    phase = phi[:,None]-phi[None,:]+2*np.pi*d*midpoint
    return float((right-left)*np.sum(amp[:,None]*amp[None,:]*np.cos(phase)*np.sinc(d*(right-left)))/len(x)**2)


def db(value):
    return 10*math.log10(max(value,1e-300))


def evaluate(cfg,target,x,phi,amplitude=None,grid_n=None):
    x,phi = np.asarray(x,float),np.asarray(phi,float)
    amplitude = np.ones(len(x)) if amplitude is None else np.asarray(amplitude,float)
    n = cfg['verification_grid_n'] if grid_n is None else grid_n
    u0 = math.sin(math.radians(target['steer_deg'])); guard = cfg['guard_u']
    side = [(-1.,u0-guard),(u0+guard,1.)]
    notch = [(math.sin(math.radians(a)),math.sin(math.radians(b))) for a,b in target['notches_deg']]
    p0 = float(radiation([u0],x,phi,amplitude)[0])
    if p0 < 1e-12:
        raise ValueError('desired-direction power is zero or too small')
    ps = peak_enclosure(x,phi,amplitude,side,n)
    pn = peak_enclosure(x,phi,amplitude,notch,n)
    pm = peak_enclosure(x,phi,amplitude,[(u0-guard,u0+guard)],n)
    # Local peak and half-power crossings: adjacent crossings around sampled
    # main-region maximum, with root refinement. This is a numerical metric.
    u = np.linspace(u0-guard,u0+guard,2003)
    p = radiation(u,x,phi,amplitude); k = int(np.argmax(p))
    opt = minimize_scalar(lambda v:-radiation([v],x,phi,amplitude)[0],
                          bounds=(u[max(0,k-1)],u[min(len(u)-1,k+1)]),method='bounded',
                          options={'xatol':1e-13})
    peak_u = float(opt.x); peak_p = -float(opt.fun)
    h = p-peak_p/2
    crossings=[]
    for j in np.flatnonzero(h[:-1]*h[1:] < 0):
        crossings.append(brentq(lambda v:radiation([v],x,phi,amplitude)[0]-peak_p/2,u[j],u[j+1],xtol=1e-13))
    l = [v for v in crossings if v<peak_u]; r = [v for v in crossings if v>peak_u]
    width_u = min(r)-max(l) if l and r else None
    width_deg = math.degrees(math.asin(min(r))-math.asin(max(l))) if l and r else None
    eta = len(x)*p0/float(np.sum(amplitude**2))
    integral = integrated_power(x,phi,amplitude,-1,1)
    main_integral = integrated_power(x,phi,amplitude,u0-guard,u0+guard)
    score_lo = max(ps['lower'],cfg['notch_weight_power']*pn['lower'])/p0
    score_hi = max(ps['upper'],cfg['notch_weight_power']*pn['upper'])/p0
    feasible = bool(eta>=cfg['minimum_coherent_efficiency']-1e-10 and width_u is not None
                    and width_u<=cfg['maximum_hpbw_u'] and abs(peak_u-u0)<=cfg['maximum_pointing_error_u'])
    return dict(target_power=p0, coherent_efficiency=eta,
                main_region_power_fraction=main_integral/integral,
                directivity_target=2*p0/integral,
                sidelobe_db_lower=db(ps['lower']/p0),sidelobe_db_upper=db(ps['upper']/p0),
                notch_db_lower=db(pn['lower']/p0),notch_db_upper=db(pn['upper']/p0),
                score_lower=score_lo,score_upper=score_hi,
                weighted_peak_db_lower=db(score_lo),weighted_peak_db_upper=db(score_hi),
                hpbw_u=width_u,hpbw_deg=width_deg,peak_u=peak_u,
                pointing_error_u=abs(peak_u-u0),main_peak_power_upper=pm['upper'],
                peak_enclosure_gap_db=max(db(ps['upper']/max(ps['lower'],1e-300)),db(pn['upper']/max(pn['lower'],1e-300))),
                feasible=feasible)


def validate_witness(cfg, target, candidate):
    n = cfg['element_count']
    x = np.asarray(candidate['positions_lambda'],float)
    phi = np.asarray(candidate['phases_rad'],float)
    a = np.asarray(candidate['amplitudes'],float)
    if any(v.shape != (n,) or not np.all(np.isfinite(v)) for v in (x,phi,a)):
        raise ValueError('invalid shape or nonfinite construction')
    expected = cfg['spacing_wavelengths']*(np.arange(n)-(n-1)/2)
    if not np.allclose(x,expected,atol=1e-12,rtol=0):
        raise ValueError('positions violate fixed ULA')
    if candidate['class']=='phase-only':
        if not np.allclose(a,1.,atol=1e-12,rtol=0):
            raise ValueError('phase-only amplitudes must equal one')
        q = phi*(2**cfg['phase_bits'])/(2*np.pi)
        if not np.allclose(q,np.round(q),atol=1e-10,rtol=0):
            raise ValueError('phases violate quantization')
    elif candidate['class']!='amplitude-reference':
        raise ValueError('unknown candidate class')
    elif np.any(a<0) or not np.isclose(np.sum(a*a),n,atol=1e-10):
        raise ValueError('reference must have nonnegative amplitudes and equal total excitation power')
    result = evaluate(cfg,target,x,phi,a)
    for key,claimed in candidate.get('metrics',{}).items():
        if key not in result:
            raise ValueError('unknown metric '+key)
        actual = result[key]
        if isinstance(actual,bool) or actual is None:
            if actual!=claimed: raise ValueError('wrong claim '+key)
        elif not np.isclose(actual,claimed,atol=2e-8,rtol=2e-8):
            raise ValueError('wrong claim '+key)
    return result
