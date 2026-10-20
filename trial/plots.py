"""Scientific figures from completed frozen results."""
import json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path('.mplconfig').resolve()))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path('trial/figures');OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f7f9fc','axes.facecolor':'#f7f9fc','text.color':'#14243b','savefig.facecolor':'#f7f9fc'})
def save(fig,name):
    fig.savefig(OUT/(name+'.png'),dpi=160,bbox_inches='tight');fig.savefig(OUT/(name+'.svg'),bbox_inches='tight');plt.close(fig)
    svg=OUT/(name+'.svg');svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
def main():
    a=json.loads(Path('trial/analysis.json').read_text());sat=json.loads(Path('trial/saturation.json').read_text());bench=json.loads(Path('trial/benchmark.json').read_text())['rows'];stress=json.loads(Path('trial/robustness.json').read_text())['rows'];plan=json.loads(Path('trial/plan.json').read_text())
    fig,axs=plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for ax,s in zip(axs.flat,a['saturation']):
        for method,color,label in [('more-de','#ed8b36','20 extra DE restarts'),('more-de-hybrid','#007c91','Same restarts + refinement')]:
            rr=sorted([r for r in sat if r['target']==s['target'] and r['method']==method],key=lambda r:r['seed']);ys=s['initial_db']-np.minimum.accumulate([s['initial_db']]+[r['metrics']['weighted_peak_db_upper'] for r in rr]);ax.step(range(21),ys,where='post',label=label,color=color,lw=2)
        ax.axhline(0,color='#8995a7',ls=':',label='Starting pilot best');ax.set_title(s['target']);ax.set_xlabel('Additional independent restart');ax.set_ylabel('Improvement over starting best (dB)');ax.set_ylim(-.02,.56);ax.grid(alpha=.15)
    axs[0,0].legend(fontsize=9);fig.suptitle('Progress is uneven across the four starting cases',fontsize=16);save(fig,'hill-climb')
    fig,axs=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    comp=a['comparisons']['hybrid vs de200']['per_target'];ds=[r['mean_gain_db'] for r in comp];axs[0].barh(range(12),ds,color=['#007c91' if d>=0 else '#ed8b36' for d in ds]);axs[0].set_yticks(range(12),[r['target'] for r in comp]);axs[0].invert_yaxis();axs[0].axvline(0,color='#14243b',lw=1);axs[0].axhline(5.5,color='#8995a7',ls=':');axs[0].set_xlabel('Improvement over DE200 (dB; positive is better)');axs[0].set_title('New targets: hybrid vs similar solver-call budget');axs[0].text(.98,.98,'01–06: two sectors\n07–12: one sector\n5 seeds per target',transform=axs[0].transAxes,ha='right',va='top',fontsize=9)
    methods=['de160','de200','hybrid','de640','margin-de200','margin-hybrid'];colors=['#8995a7','#ed8b36','#007c91','#784e9d','#cc6b3f','#1a9e8b']
    for method,color in zip(methods,colors):
        ss=a['methods'][method];axs[1].scatter(ss['mean_nominal_eta'],ss['mean_weighted_db'],s=70,color=color,label=method)
    axs[1].set(xlabel='Mean nominal coherent efficiency',ylabel='Mean weighted peak (dB; lower better)',title='Robustness margin costs nominal suppression');axs[1].legend(fontsize=9);axs[1].grid(alpha=.15);save(fig,'fresh-comparison')
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for method,color in [('hybrid','#007c91'),('margin-hybrid','#ed8b36')]:
        ss=[s for s in stress if s['method']==method];bounds=[s['gain_bound'] for s in ss];emp=[min(t['coherent_efficiency'] for t in s['trials']) for s in ss];adv=[s['adversarial_gain']['minimum_found'] for s in ss]
        axs[0].scatter(bounds,adv,label=method,color=color,s=40);axs[1].scatter(range(1,13),emp,label=method+' random minimum',color=color,marker='o');axs[1].scatter(range(1,13),adv,label=method+' adversarial search',color=color,marker='x')
    axs[0].plot([.77,.91],[.77,.91],':',color='#8995a7');axs[0].axhline(.85,ls='--',color='#14243b');axs[0].axvline(.85,ls='--',color='#14243b');axs[0].set(xlabel='Analytical lower bound on coherent efficiency',ylabel='Lowest efficiency found by adversarial search',title='A bound covers the specified error box');axs[0].legend(fontsize=9)
    axs[1].axhline(.85,ls='--',color='#14243b');axs[1].set(xlabel='Fresh target',ylabel='Perturbed coherent efficiency',title='Random trials alone miss damaging error combinations');axs[1].legend(fontsize=8);axs[1].set_xticks(range(1,13));fig.suptitle('Gain robustness only: ±2° phase, ±0.005 wavelength position, ±3% amplitude',fontsize=14);save(fig,'robustness')
    print('Wrote hill-climb, fresh-comparison and robustness PNG/SVG figures.')
if __name__=='__main__':main()
