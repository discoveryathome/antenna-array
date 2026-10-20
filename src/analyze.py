"""Produce tables, a self-contained report, and publication-style static plots."""
import csv
import json
import os
from pathlib import Path
import numpy as np
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .evaluator import radiation
from .run import ROOT,digest
METHODS=['uniform','coordinate','random','slsqp','de','chebyshev30']
LABELS={'uniform':'Uniform steering','coordinate':'Coordinate only','random':'Random search','slsqp':'SLSQP + polish','de':'DE + polish','chebyshev30':'Chebyshev (amplitude reference)'}
COLORS={'uniform':'#737b88','coordinate':'#c2902d','random':'#c06682','slsqp':'#196bc2','de':'#15916c','chebyshev30':'#9b75bd'}


def summarize(data,robust,cfg):
    rows=[r for r in data['rows'] if r['split']=='held-out'];table=[];aggregate=[]
    for t in [t for t in cfg['targets'] if t['split']=='held-out']:
        for method in METHODS:
            rr=[r for r in rows if r['target']==t['id'] and r['method']==method]
            v=[r['metrics']['weighted_peak_db_upper'] for r in rr]
            table.append(dict(target=t['id'],method=method,median_weighted_db=float(np.median(v)),minimum_weighted_db=min(v),maximum_weighted_db=max(v),feasible=sum(r['metrics']['feasible'] for r in rr),runs=len(rr)))
    for method in METHODS:
        rr=[r for r in rows if r['method']==method];gains=[];ngains=[];sgains=[]
        for r in rr:
            baseline=next(b for b in rows if b['target']==r['target'] and b['method']=='uniform')['metrics'];m=r['metrics']
            gains.append(baseline['weighted_peak_db_lower']-m['weighted_peak_db_upper'])
            ngains.append(baseline['notch_db_lower']-m['notch_db_upper'])
            sgains.append(baseline['sidelobe_db_lower']-m['sidelobe_db_upper'])
        stress=[r for r in robust['rows'] if r['method']==method]
        aggregate.append(dict(method=method,mean_weighted_gain_db=float(np.mean(gains)),minimum_weighted_gain_db=min(gains),maximum_weighted_gain_db=max(gains),
                              mean_notch_gain_db=float(np.mean(ngains)),mean_sidelobe_gain_db=float(np.mean(sgains)),
                              min_coherent_efficiency=min(r['metrics']['coherent_efficiency'] for r in rr),max_hpbw_u=max(r['metrics']['hpbw_u'] for r in rr),
                              nominal_feasible=sum(r['metrics']['feasible'] for r in rr),runs=len(rr),
                              combined_feasible=sum(r['scenarios']['combined']['feasible_count'] for r in stress),combined_trials=len(stress)*cfg['robustness_trials'],
                              median_objective_calls=float(np.median([r['search'].get('objective_calls',0) for r in rr])),
                              median_search_seconds=float(np.median([r['search'].get('elapsed_seconds',0) for r in rr]))))
    return dict(candidate_sha256=digest(ROOT/'results/candidates.json'),robustness_sha256=digest(ROOT/'results/robustness.json'),table=table,aggregate=aggregate,
                max_nominal_enclosure_gap_db=max(r['metrics']['peak_enclosure_gap_db'] for r in rows),heldout_candidate_count=len(rows))


def plot(data,robust,cfg):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':180})
    targets=[t for t in cfg['targets'] if t['split']=='held-out'];rows=data['rows']
    def get(t,method):return next(r for r in rows if r['target']==t['id'] and r['method']==method and r['seed'] in [None,cfg['seeds'][0]])
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    theta=np.linspace(-90,90,7201);u=np.sin(np.deg2rad(theta))
    for ax,t in zip(axes.flat,targets):
        for method in ['uniform','slsqp','de','chebyshev30']:
            r=get(t,method);p=radiation(u,r['positions_lambda'],r['phases_rad'],r['amplitudes'])
            ax.plot(theta,10*np.log10(np.maximum(p/r['metrics']['target_power'],1e-6)),color=COLORS[method],lw=1.3,label=LABELS[method])
        for a,b in t['notches_deg']:ax.axvspan(a,b,color='#efb458',alpha=.23)
        u0=np.sin(np.deg2rad(t['steer_deg']));edges=np.degrees(np.arcsin([u0-cfg['guard_u'],u0+cfg['guard_u']]))
        for e in edges:ax.axvline(e,color='#b2bac3',ls=':',lw=1)
        ax.set(xlim=(-90,90),ylim=(-45,2),title=f"{t['id']}  |  steer {t['steer_deg']}°",xlabel='Angle from broadside (degrees)',ylabel='Power / desired-direction power (dB)');ax.grid(alpha=.16)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=2,frameon=False)
    fig.suptitle('Held-out beam patterns • fixed representative seed 1729\nAmber: protected sectors; dotted: fixed main-beam exclusion',fontsize=14)
    fig.savefig(ROOT/'figures/beam-patterns.png');fig.savefig(ROOT/'figures/beam-patterns.svg');plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(10,10),subplot_kw={'projection':'polar'},layout='constrained')
    angles=np.linspace(-np.pi,np.pi,7201);u=np.sin(angles)
    for ax,t in zip(axes.flat,targets):
        for method in ['uniform','slsqp','de']:
            r=get(t,method);p=radiation(u,r['positions_lambda'],r['phases_rad'],r['amplitudes']);level=10*np.log10(np.maximum(p/r['metrics']['target_power'],1e-4))
            ax.plot(angles,np.maximum(level,-40)+40,color=COLORS[method],lw=1.1,label=LABELS[method])
        ax.set_theta_zero_location('N');ax.set_theta_direction(-1);ax.set_ylim(0,40);ax.set_yticks([10,20,30,40]);ax.set_yticklabels(['−30','−20','−10','0 dB']);ax.set_title(t['id'],pad=20);ax.grid(alpha=.3)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False)
    fig.suptitle('Full polar cuts • isotropic linear array\nFront/back copies are physical symmetry of this ideal model',fontsize=14)
    fig.savefig(ROOT/'figures/polar-patterns.png');fig.savefig(ROOT/'figures/polar-patterns.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,4.6),layout='constrained')
    for method in METHODS:
        rr=[r for r in rows if r['split']=='held-out' and r['method']==method]
        axes[0].scatter([r['metrics']['coherent_efficiency'] for r in rr],[r['metrics']['weighted_peak_db_upper'] for r in rr],s=40,color=COLORS[method],alpha=.8,label=LABELS[method])
    axes[0].axvline(.85,color='black',ls=':',lw=1);axes[0].set(xlabel='Coherent array efficiency',ylabel='Weighted peak upper bound (dB; lower is better)',title='All held-out runs • gain / suppression tradeoff');axes[0].grid(alpha=.16)
    for i,method in enumerate(METHODS):
        rr=[r for r in robust['rows'] if r['method']==method]
        v=[q['weighted_peak_db_upper'] for r in rr for q in r['scenarios']['combined']['trials']]
        axes[1].boxplot([v],positions=[i],widths=.55,patch_artist=True,boxprops={'facecolor':COLORS[method],'alpha':.55},showfliers=False)
    axes[1].set_xticks(range(len(METHODS)),['Uniform','Coordinate','Random','SLSQP','DE','Chebyshev'],rotation=25);axes[1].set(ylabel='Weighted peak upper bound (dB)',title='Combined bounded calibration stress\n64 draws × 4 targets; seed-1729 representatives');axes[1].grid(axis='y',alpha=.16)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=3,frameon=False)
    fig.savefig(ROOT/'figures/tradeoffs-robustness.png');fig.savefig(ROOT/'figures/tradeoffs-robustness.svg');plt.close(fig)


def report(s,robust,cfg):
    lines=['# Antenna array beam-pattern pilot — results','',
           'Local, author-checked simulation evidence. No maintainer acceptance, hardware result, global optimum, or algorithmic novelty is claimed. Model: 16 isotropic elements, half-wavelength spacing, 3 GHz, equal amplitude and 6-bit phase control. See [model and bounds](MODEL.md), [frozen experiment](EXPERIMENTS.md), and [literature audit](LITERATURE.md).','',
           '## Held-out comparison','',
           'The primary score is max(global fixed-mask sidelobe power, 16 × protected-sector peak power), divided by desired-direction power. Lower dB is better. The table reports medians over three seeds for SLSQP, DE and random search, and one deterministic run for the other methods. Chebyshev uses amplitude freedom and is outside the hardware class.','',
           '| Target | Uniform | Coordinate | Random | SLSQP | DE | Chebyshev reference |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for t in [t for t in cfg['targets'] if t['split']=='held-out']:
        v=[next(r['median_weighted_db'] for r in s['table'] if r['target']==t['id'] and r['method']==m) for m in METHODS]
        lines.append('| '+t['id']+' | '+' | '.join(f'{x:.2f}' for x in v)+' |')
    lines+=['','| Method | Mean weighted improvement vs steering (dB) | Mean sector improvement (dB) | Mean global SLL improvement (dB) | Nominal feasible | Combined-stress feasible |',
            '|---|---:|---:|---:|---:|---:|']
    for a in s['aggregate']:
        lines.append(f"| {LABELS[a['method']]} | {a['mean_weighted_gain_db']:.2f} | {a['mean_notch_gain_db']:.2f} | {a['mean_sidelobe_gain_db']:.2f} | {a['nominal_feasible']}/{a['runs']} | {a['combined_feasible']}/{a['combined_trials']} |")
    lines+=['','Improvements compare baseline **lower** bounds to candidate **upper** bounds. A negative value means degradation, including the tiny negative self-comparison caused by enclosure width. Gains are averaged over all method runs, pairing each run with the same target baseline. The four cases are not a statistical sample of all array applications.',
            '',f"The largest nominal sidelobe/sector enclosure width across held-out witnesses was {s['max_nominal_enclosure_gap_db']:.5f} dB. Beamwidth and pointing checks remain numerical, and the curvature bounds use float64 rather than directed rounding.",'',
            '## Before / after patterns','','![Before and after beam patterns](../figures/beam-patterns.png)','','![Full polar cuts](../figures/polar-patterns.png)','','![Tradeoffs and calibration stress](../figures/tradeoffs-robustness.png)','','## Calibration sensitivity','',
            'The stress trials perturb phases by up to 2°, along-array positions by up to 0.005 wavelength (about 0.50 mm), and amplitudes by up to 3%, both separately and together. Errors are independent uniform draws; all methods see the same 64 draws. Representatives were fixed to seed 1729 before outcomes, not chosen for favorable robustness. Bounds on each trial use a different density-2049 grid. Feasible counts include gain, width and pointing limits. These finite trials do not guarantee fabrication yield.','',
            '| Target / method | Nominal representative | Combined stress median | Combined stress 95th percentile | All-error-box upper bound |',
            '|---|---:|---:|---:|---:|']
    candidates=json.loads((ROOT/'results/candidates.json').read_text())['rows']
    for r in robust['rows']:
        if r['method'] not in ['uniform','slsqp','de']:continue
        nom=next(a['metrics']['weighted_peak_db_upper'] for a in candidates if a['id']==r['id']);st=r['scenarios']['combined']['summary']['weighted_peak_db_upper']
        lines.append(f"| {r['target']} / {r['method']} | {nom:.2f} | {st['median']:.2f} | {st['p95']:.2f} | {r['worst_case']['weighted_peak_db_upper']:.2f} |")
    lines+=['','The all-error-box bound follows a triangle-inequality field enclosure, not Monte Carlo. It is deliberately conservative and does not establish beamwidth or pointing robustness. Nominal designs close to the 0.85 gain floor can fail that floor under small calibration errors. That is a reason to optimize with margin or a robust objective before engineering use.','','## Cost and reproducibility','',
            '| Method | Median objective evaluations | Median search seconds |','|---|---:|---:|']
    for a in s['aggregate']:
        if a['method'] in ['uniform','chebyshev30']:continue
        lines.append(f"| {a['method']} | {a['median_objective_calls']:.0f} | {a['median_search_seconds']:.3f} |")
    lines+=['','Timing is descriptive on this host; background load was not controlled. Analytic-gradient SLSQP and population search have different budgets, so this is not an equal-cost efficiency ranking. DE and nonadaptive random search have matched core proposal counts; both intelligent methods use the same discrete polish. Stored witnesses can be checked without rerunning optimization. All phases, amplitudes, seeds, solver diagnostics, configuration hashes, and environment versions are retained.','','## Discovery yield and engineering relevance','',
            'The useful output is a verified benchmark, feasible phase tables, measured tradeoffs, and a discriminating negative case. On the two-sector broadside target, this SLSQP procedure returns the steering pattern for every seed, while DE finds a better discrete configuration. This supports keeping a global-search comparator; it does not show that all local or manifold methods fail. On easier targets, cheap coordinate changes already recover much of the improvement, so the extra benefit of sophisticated optimization must be compared against that baseline.','',
            'The experiment shows that constrained phase configuration can improve protected-sector rejection in an ideal array while retaining prescribed nominal gain, width and pointing. The amplitude reference illustrates the cost of equal-amplitude hardware. Robustness checks expose limited gain margin in some optimized configurations. Those observations have engineering meaning for phase-shifter resolution and calibration budgets, but no coupling, element pattern, amplifier, feed, polarization or measurement model is present. There is no hardware performance claim.','',
            'Scientific novelty yield is unestablished. DE, constrained minimax synthesis, phase-only notching and Chebyshev tapering all predate this pilot. The benchmark is too small and lacks a modern manifold/ADMM comparator or rigorous optimization lower bound to claim a new frontier. A promising next step is robust quantized synthesis with explicit gain margin, a larger untouched target set, nonisotropic embedded-element patterns, and a convex or gridless lower-bound comparison. A maintainer and independent review are still needed before opening donor intake.','']
    (ROOT/'docs/RESULTS.md').write_text('\n'.join(lines))


def main():
    cfg=json.loads((ROOT/'configs/experiment.json').read_text());data=json.loads((ROOT/'results/candidates.json').read_text());robust=json.loads((ROOT/'results/robustness.json').read_text())
    s=summarize(data,robust,cfg);(ROOT/'results/summary.json').write_text(json.dumps(s,indent=2)+'\n')
    flat=[dict(id=r['id'],target=r['target'],split=r['split'],method=r['method'],seed=r['seed'],**r['metrics']) for r in data['rows']]
    with (ROOT/'results/metrics.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
    plot(data,robust,cfg);report(s,robust,cfg);print(json.dumps(s['aggregate'],indent=2))
if __name__=='__main__':main()
