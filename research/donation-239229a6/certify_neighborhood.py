"""Exact-integer interval audit of the predeclared fresh-08 neighborhood.

Model: exact six-bit phases, decimal steering angle, equal amplitudes, fixed ULA.
This research script changes no project evaluator or accepted result record.
"""
import argparse
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import time

from integer_intervals import I, PI, SCALE, interval, sincos, ceildiv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TASK = 'fresh-08-calibration-margin'
PINS = {
    'configs/experiment.json': 'f4f2b1d0ba59c9f3fa39612ac00bebfcbc887a873a210c7b8e3d80806d7381aa',
    'research/readiness-20261021/portfolio.json': '6f649596ce80bf423a102aee79d6aa236b70f20286bfffe5e1726f58aec7743b',
    'research/readiness-20261021/fresh-08-calibration-margin.json': '3c5820c2d9960eefadf8b69f86ce197d9396bd2e934e4aaa7da6fe917c323080',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def neighbors(bins):
    for i in range(16):
        for step in range(1,64):
            q = list(bins)
            q[i] = (q[i]+step)%64
            yield q, [[i,step]]
    for i,j in itertools.combinations(range(16),2):
        for a,b in itertools.product((-2,-1,1,2),repeat=2):
            q = list(bins)
            q[i],q[j] = (q[i]+a)%64,(q[j]+b)%64
            yield q, [[i,a],[j,b]]


PHASE = [sincos(PI*Fraction(q,32)) for q in range(64)]


@lru_cache(maxsize=512)
def steering_coefficients(lo, hi):
    u = I(lo,hi)
    positive = [sincos(PI*u*Fraction(2*k+1,2)) for k in range(8)]
    return [(-s,c) for s,c in positive[::-1]]+positive


def power(bins, u):
    re,im = interval(0),interval(0)
    for q,(s,c) in zip(bins,steering_coefficients(u.lo,u.hi)):
        sp,cp = PHASE[q]
        re,im = re+c*cp-s*sp,im+s*cp+c*sp
    return (re.square()+im.square())/256


def nominal_floor(u0):
    a = PI/90+2*PI*u0.absolute()*Fraction(1,200)
    s,c = sincos(a)
    t = interval(Fraction(3,100))
    ca = (1-t.square()).sqrt()
    sd,cd = s*ca+c*t,c*ca-s*t
    # asin(.03) < .031, and 0 < delta < acos(sqrt(.85)) < pi/2.
    assert sincos(interval(Fraction(31,1000)))[0].lo > t.hi
    assert a.lo > 0 and a.hi+interval(Fraction(31,1000)).hi < PI.lo//2
    eta = interval(Fraction(85,100))
    assert sd.lo > 0 and cd.lo > eta.sqrt().hi
    return (eta.sqrt()*cd+(1-eta).sqrt()*sd).square()


def model():
    for path,h in PINS.items():
        assert digest(ROOT/path) == h, path
    read = lambda p:json.loads((ROOT/p).read_text(),parse_float=Decimal)
    cfg = read('configs/experiment.json')
    card = next(t for t in read('research/readiness-20261021/portfolio.json')['tasks'] if t['id']==TASK)
    assert cfg['element_count']==16 and cfg['phase_bits']==6
    assert cfg['spacing_wavelengths']==Decimal('.5') and cfg['minimum_coherent_efficiency']==Decimal('.85')
    target = card['target']
    u0 = sincos(PI*Fraction(target['steer_deg'])/180)[0]
    guard = interval(Fraction(cfg['guard_u']))
    regions = [('side-left',interval(-1),u0-guard,1),('side-right',u0+guard,interval(1),1)]
    for i,(a,b) in enumerate(target['notches_deg']):
        regions.append((f'notch-{i}',sincos(PI*Fraction(a)/180)[0],sincos(PI*Fraction(b)/180)[0],
                        int(cfg['notch_weight_power'])))
    for name,a,b,w in regions:
        assert -SCALE <= a.lo < a.hi+1 <= b.lo+1 and b.hi <= SCALE and w>0
    return card,u0,regions


def baseline_upper(bins, u0, regions, mesh):
    eta = power(bins,u0)
    assert eta.lo > 0
    # E|x|=2, E x^2=85/16 for x=(-15,-13,...,15)/4.
    curvature = 2*((2*PI*2).square()+(2*PI).square()*Fraction(85,16))
    records = []
    for name,a,b,weight in regions:
        n = ceildiv((b.hi-a.lo)*mesh,SCALE)
        h = (b-a)/n
        maximum,index = -1,None
        for i in range(n+1):
            u = (a*(n-i)+b*i)/n
            p = power(bins,u)
            if p.hi > maximum:
                maximum,index = p.hi,i
        correction = curvature*h.square()/8
        bound = (I(0,maximum)+correction)*weight/eta
        records.append(dict(region=name,intervals=n,weight=weight,
            maximum_grid_upper=I(maximum,maximum).endpoints()[0],maximum_grid_index=index,
            interpolation_error=correction.endpoints(),normalized_upper=I(bound.hi,bound.hi).endpoints()[0]))
        print('incumbent',name,'grid nodes',n+1,'score upper',records[-1]['normalized_upper'],flush=True)
    upper = max(interval(Fraction(r['normalized_upper'])).hi for r in records)
    return upper,dict(nominal_efficiency=eta.endpoints(),second_derivative_bound=curvature.endpoints(),
        mesh_intervals_per_unit=mesh,regions=records,weighted_score_upper=I(upper,upper).endpoints()[0])


def main(mesh):
    if not __debug__:
        raise RuntimeError('Run without -O: this certificate requires all assertions')
    start = time.monotonic()
    card,u0,regions = model()
    inputs_path = HERE/'point-witnesses.json'
    data = json.loads(inputs_path.read_text())
    bins = data['incumbent_bins']
    assert len(bins)==16 and all(type(q) is int and 0<=q<64 for q in bins)
    # Stored decimal phases encode the canonical bin; the certificate uses exact 2*pi*q/64.
    for phi,q in zip(card['incumbent']['phases_rad'],bins):
        error = (interval(Fraction(phi))-PI*Fraction(q,32)).absolute()
        assert error.hi < interval(Fraction(1,10**13)).lo
    all_neighbors = list(neighbors(bins))
    assert len(all_neighbors)==len({tuple(q) for q,_ in all_neighbors})==2928
    assert len(data['points'])==2928
    floor = nominal_floor(u0)
    assert power(bins,u0).lo >= floor.hi
    upper,baseline = baseline_upper(bins,u0,regions,mesh)
    records,failed_margin,worse = [],0,0
    minimum_gap = None
    for index,((q,delta),point) in enumerate(zip(all_neighbors,data['points'])):
        eta = power(q,u0)
        record = dict(index=index,changes=delta,nominal_eta=eta.endpoints())
        if eta.hi < floor.lo:
            failed_margin += 1
            record['excluded_by'] = 'pinned-calibration-bound-gate'
        else:
            assert eta.lo >= floor.hi, ('ambiguous calibration gate',index)
            region = point['region']
            assert type(region) is int and 0<=region<len(regions)
            name,a,b,weight = regions[region]
            if 'u_decimal' in point:
                u = interval(Fraction(point['u_decimal']))
                assert a.hi <= u.lo <= u.hi <= b.lo, ('point not certified inside region',index)
            else:
                i,n = point['numerator'],point['denominator']
                assert type(i) is int and type(n) is int and 0<=i<=n and n>0
                u = (a*(n-i)+b*i)/n
            ratio = power(q,u)*weight/eta
            if ratio.lo <= upper:
                raise ValueError(f'Unresolved neighbor {index}; refine its point or incumbent mesh, not the claim')
            worse += 1
            gap = ratio.lo-upper
            minimum_gap = gap if minimum_gap is None else min(minimum_gap,gap)
            record.update(excluded_by='weighted-point-lower-above-incumbent-upper',point=point,
                          u_interval=u.endpoints(),weighted_score=ratio.endpoints())
        records.append(record)
    result = dict(task=TASK,model='Canonical exact 2*pi*q/64 phases and exact decimal target angle; fixed half-wavelength ULA.',
        source_sha256=PINS,point_witnesses_sha256=digest(inputs_path),pi_interval=PI.endpoints(),scale=str(SCALE),
        nominal_efficiency_threshold=floor.endpoints(),incumbent=baseline,
        neighborhood_size=len(records),excluded_by_calibration_gate=failed_margin,excluded_by_objective=worse,
        minimum_objective_separation=I(minimum_gap,minimum_gap).endpoints()[0],records=records,
        script_sha256={p.name:digest(p) for p in (Path(__file__),HERE/'integer_intervals.py')},
        elapsed_seconds=time.monotonic()-start,
        limitations=['Author-written exact-integer interval implementation, not formally verified software.',
            'Only the enumerated neighborhood is excluded; larger/coordinated phase changes remain untested.',
            'Failing the pinned efficiency lower-bound gate does not prove actual physical inefficiency.',
            'No worst-case perturbed sidelobe or hardware claim; exact mathematical interpretation is stated explicitly.'])
    (HERE/'neighborhood-certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS',failed_margin,'calibration exclusions;',worse,'objective exclusions; minimum gap',result['minimum_objective_separation'],
          'seconds',result['elapsed_seconds'],flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh',type=int,default=6000)
    args = parser.parse_args()
    if not 1000 <= args.mesh <= 20000:
        parser.error('mesh must be between 1000 and 20000 intervals per unit u')
    main(args.mesh)
