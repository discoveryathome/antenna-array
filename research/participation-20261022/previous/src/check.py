"""End-to-end result audit. Full stress replay is optional but reproducible."""
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
import jsonschema
from .run import ROOT,digest
from .evaluator import validate_witness,radiation,evaluate
from .robustness import SCENARIOS,worst_case


def load(p):return json.loads((ROOT/p).read_text())

def numerical(cfg,data,do_all=True):
    for path,sha in load('configs/frozen.json')['sha256'].items():
        assert digest(ROOT/path)==sha,'changed frozen source '+path
    assert data['config_sha256']==digest(ROOT/'configs/experiment.json')
    targets={t['id']:t for t in cfg['targets']}
    for t in targets.values():
        u0=math.sin(math.radians(t['steer_deg']))
        for a,b in t['notches_deg']:
            assert -90<=a<b<=90
            ua,ub=map(lambda q:math.sin(math.radians(q)),(a,b))
            assert ub<=u0-cfg['guard_u'] or ua>=u0+cfg['guard_u']
    rows=data['rows'] if do_all else [data['rows'][0]]
    for row in rows:
        target=targets[row['target']];m=validate_witness(cfg,target,row)
        assert m.keys()==row['metrics'].keys(),'incomplete metrics'
        # Completely different angular grid, uniform theta rather than u.
        theta=np.linspace(-90,90,14011);u=np.sin(np.deg2rad(theta));u0=math.sin(math.radians(target['steer_deg']))
        p=radiation(u,row['positions_lambda'],row['phases_rad'],row['amplitudes'])/m['target_power']
        side=abs(u-u0)>=cfg['guard_u'];notch=np.zeros(len(u),bool)
        for a,b in target['notches_deg']:notch|=(theta>=a)&(theta<=b)
        assert p[side].max()<=10**(m['sidelobe_db_upper']/10)+1e-10
        assert p[notch].max()<=10**(m['notch_db_upper']/10)+1e-10
    print(f'PASS numerical: {len(rows)} independent reconstructions and uniform-theta grid audits')


def protocol():
    for path,schema in [('discover.json','manifest'),('discover/frontier.json','frontier'),('discover/catalog.json','catalog')]:
        jsonschema.Draft202012Validator(load(f'discover/schemas/{schema}.schema.json')).validate(load(path))
    assert sum(t['weight'] for t in load('discover/catalog.json')['tracks'])==100
    assert load('discover.json')['review']['paused']
    assert not load('discover.json').get('hubs')
    print('PASS protocol schemas, track weights, local-only paused status')


def literature():
    text=(ROOT/'docs/LITERATURE.md').read_text()
    for s in ['Dolph','Lebret','Kurup','2026','Unverified','403']:
        assert s.lower() in text.lower()
    print('PASS literature inventory present; source validity/theorems still require human/full-text audit')


def stress(cfg,data,full):
    robust=load('results/robustness.json');assert robust['candidate_sha256']==digest(ROOT/'results/candidates.json')
    assert robust['config_sha256']==digest(ROOT/'configs/experiment.json')
    errors=np.random.default_rng(cfg['robustness_seed']).uniform(-1,1,(cfg['robustness_trials'],3,cfg['element_count']))
    candidates={r['id']:r for r in data['rows']};targets={t['id']:t for t in cfg['targets']};checked=0
    for r in robust['rows']:
        row=candidates[r['id']];assert r['worst_case']==worst_case(cfg,row)
        x,phi,amp=[np.asarray(row[k]) for k in ['positions_lambda','phases_rad','amplitudes']]
        for name,(ps,xs,ams) in SCENARIOS.items():
            sc=r['scenarios'][name];trials=sc['trials'];assert len(trials)==cfg['robustness_trials']
            assert sc['feasible_count']==sum(t['feasible'] for t in trials)
            for k,v in sc['summary'].items():
                values=[t[k] for t in trials]
                expected=dict(median=float(np.median(values)),p95=float(np.quantile(values,.95)),minimum=min(values),maximum=max(values))
                assert v==expected
            indices=range(len(trials)) if full else [0,len(trials)-1]
            for i in indices:
                e=errors[i];m=evaluate(cfg,targets[row['target']],x+xs*.005*e[1],phi+ps*np.deg2rad(2)*e[0],amp*(1+ams*.03*e[2]),grid_n=2049)
                for k,v in trials[i].items():
                    assert np.isclose(m[k],v,atol=2e-8,rtol=2e-8),f'stress mismatch {r["id"]} {name} {i} {k}'
                checked+=1
            # Nominal analytical error-box bound must dominate the numerical
            # continuous-angle upper bounds at these stress grid resolutions.
            for t in trials:
                assert t['weighted_peak_db_upper']<=r['worst_case']['weighted_peak_db_upper']+1e-8
    print(f'PASS robustness: {checked} trials recomputed; all recorded summaries and analytical box bounds checked')


def tables(cfg,data):
    from .analyze import summarize
    recorded=load('results/summary.json');computed=summarize(data,load('results/robustness.json'),cfg)
    assert recorded==computed,'summary mismatch'
    table=load('discover/frontier-table.json');rows={r['id']:r for r in data['rows']}
    for entry in table:
        row=rows[entry['id']];assert row['class']=='phase-only' and row['metrics']['feasible']
        assert entry['value']==row['metrics']['weighted_peak_db_upper']
        assert entry['target']==row['target']
        possible=[r for r in data['rows'] if r['target']==entry['target'] and r['class']=='phase-only' and r['metrics']['feasible']]
        assert entry['value']==min(r['metrics']['weighted_peak_db_upper'] for r in possible)
    assert len(table)==len([t for t in cfg['targets'] if t['split']=='held-out'])
    with (ROOT/'results/best-phases.csv').open() as f:
        exported=list(csv.DictReader(f))
    assert len(exported)==len(table)*cfg['element_count']
    expected_ids={entry['id'] for entry in table}
    seen=set()
    for entry in exported:
        row=rows[entry['candidate']];i=int(entry['element'])
        assert row['id'] in expected_ids and 0<=i<cfg['element_count']
        assert (row['id'],i) not in seen;seen.add((row['id'],i))
        assert entry['target']==row['target']
        assert int(entry['phase_bin'])==int(round(row['phases_rad'][i]*(2**cfg['phase_bits'])/(2*np.pi)))%(2**cfg['phase_bits'])
        assert float(entry['position_lambda'])==row['positions_lambda'][i]
        assert np.isclose(float(entry['position_m']),row['positions_lambda'][i]*cfg['speed_of_light_m_s']/cfg['frequency_hz'],rtol=0,atol=1e-12)
        assert np.isclose(float(entry['phase_degrees']),row['phases_rad'][i]*180/np.pi,rtol=0,atol=1e-10)
        assert float(entry['amplitude'])==1
    for art in load('discover/frontier.json').get('artifacts',[]):assert digest(ROOT/art['path'])==art['sha256'],art['path']
    print('PASS frontier witnesses, best-of-local-portfolio values, summary and artifact hashes')


def main():
    p=argparse.ArgumentParser();p.add_argument('--section',choices=['all','numerical','protocol','literature','robustness'],default='all');p.add_argument('--full-stress',action='store_true');a=p.parse_args()
    cfg=load('configs/experiment.json');data=load('results/candidates.json')
    if a.section in ['all','numerical']:numerical(cfg,data)
    if a.section in ['all','protocol']:protocol()
    if a.section in ['all','literature']:literature()
    if a.section in ['all','robustness']:stress(cfg,data,a.full_stress)
    if a.section=='all':tables(cfg,data)
    print('PASS: author-check only; no hardware or global-optimality claim.')
if __name__=='__main__':main()
