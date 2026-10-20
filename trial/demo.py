"""Truthful scientific demo: only evaluated, realizable discrete configurations."""
import json,os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path('.mplconfig').resolve()))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from src.evaluator import evaluate,radiation

OUT=Path('trial/figures');OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#f7f9fc','axes.facecolor':'#f7f9fc','text.color':'#14243b','axes.labelcolor':'#14243b','xtick.color':'#45556a','ytick.color':'#45556a','savefig.facecolor':'#f7f9fc'})
COLORS=['#8895a7','#ed8b36','#a477ca','#007c91']
def main():
    cfg=json.loads(Path('configs/experiment.json').read_text());target=next(t for t in cfg['targets'] if t['id']=='test-two-notch');old=json.loads(Path('results/candidates.json').read_text())['rows'];ex=json.loads(Path('trial/exploration.json').read_text())
    valid=[r for r in old if r['target']==target['id'] and r['class']=='phase-only' and r['metrics']['feasible']];inc=min(valid,key=lambda r:r['metrics']['score_upper']);x=np.asarray(inc['positions_lambda']);amp=np.ones(16)
    best=lambda mode:min((r for r in ex if r['target']==target['id'] and r['method']==mode),key=lambda r:r['metrics']['score_upper'])
    states=[dict(label='Coherent steering',phase=np.zeros(16),note='Simple reference'),dict(label='Starting pilot best',phase=np.array(inc['phases_rad']),note='Work already in starter'),dict(label='Paired phase moves',phase=np.array(best('paired')['phases_rad']),note='Contributor trial'),dict(label='Refine + smarter rounding',phase=np.array(best('hybrid')['phases_rad']),note='Contributor trial')]
    for s in states:s['metrics']=evaluate(cfg,target,x,s['phase'])
    angles=np.linspace(-90,90,8001);u=np.sin(np.deg2rad(angles));curves=[10*np.log10(np.maximum(radiation(u,x,s['phase'],amp),1e-7)) for s in states]
    def make(k,save=True):
        fig=plt.figure(figsize=(13,8),layout='constrained');gs=fig.add_gridspec(3,3,height_ratios=[.22,1,.45],width_ratios=[1.1,1.1,1]);head=fig.add_subplot(gs[0,:]);head.axis('off')
        head.text(0,1,'Aim the signal. Quiet the neighbours.',fontsize=23,weight='bold',va='top');head.text(0,.15,'16 antennas · equal amplitudes · 64 phase settings · ideal far-field model',fontsize=13,color='#45556a')
        ax=fig.add_subplot(gs[1,:2]);polar=fig.add_subplot(gs[1,2],projection='polar');ph=fig.add_subplot(gs[2,:2]);stats=fig.add_subplot(gs[2,2]);stats.axis('off')
        for lo,hi in target['notches_deg']:
            ax.axvspan(lo,hi,color='#de6d6d',alpha=.16);polar.bar(np.deg2rad((lo+hi)/2),45,width=np.deg2rad(hi-lo),bottom=0,color='#de6d6d',alpha=.12)
        for j in range(k+1):
            lw=2.2 if j==k else 1.2;alpha=1 if j==k else .65
            ax.plot(angles,curves[j],color=COLORS[j],lw=lw,alpha=alpha,label=states[j]['label']);polar.plot(np.deg2rad(angles),np.maximum(curves[j],-40)+40,color=COLORS[j],lw=lw,alpha=alpha)
        ax.set(xlim=(-60,60),ylim=(-45,2),xlabel='Direction from broadside (degrees)',ylabel='Power (dB, same coherent reference)');ax.grid(alpha=.17);ax.legend(fontsize=9,loc='lower center',ncol=2);ax.set_title('Red sectors: directions we want to keep quiet',fontsize=12,loc='left')
        polar.set_theta_zero_location('N');polar.set_theta_direction(-1);polar.set_thetamin(-90);polar.set_thetamax(90);polar.set_ylim(0,41);polar.set_yticks([0,10,20,30,40],['−40','−30','−20','−10','0']);polar.tick_params(labelsize=8);polar.set_title('Front-half polar cut',fontsize=12,pad=18)
        bins=np.rint(states[k]['phase']*64/(2*np.pi)).astype(int)%64
        ph.imshow(bins[None,:],cmap='twilight',vmin=0,vmax=64,aspect='auto');ph.set_yticks([]);ph.set_xticks(range(16),range(1,17));ph.set_xlabel('Antenna number');ph.set_title(states[k]['label']+' — phase settings (0–63)',loc='left',fontsize=12)
        for j,b in enumerate(bins):ph.text(j,0,str(b),ha='center',va='center',color='white',weight='bold',fontsize=10,bbox={'facecolor':'#14243b','alpha':.5,'edgecolor':'none','pad':2})
        m=states[k]['metrics'];stats.text(0,1,f"Weighted peak: {m['weighted_peak_db_upper']:.2f} dB\nSidelobe (fixed mask): {m['sidelobe_db_upper']:.2f} dB\nQuiet-sector peak: {m['notch_db_upper']:.2f} dB\nCoherent efficiency: {100*m['coherent_efficiency']:.1f}%",va='top',linespacing=1.65,fontsize=11)
        stats.text(0,.12,'Peak metrics use desired-direction power.\nWeighted score adds a sector penalty.',fontsize=8,color='#45556a',va='top')
        fig.suptitle(f"Step {k+1}/4  ·  {states[k]['note']}       |       Simulation, not measured hardware",x=.5,y=-.005,fontsize=10,color='#45556a')
        if save:fig.savefig(OUT/f'demo-{k}.png',dpi=140,bbox_inches='tight')
        return fig
    for k in range(4):plt.close(make(k))
    fig=make(3,False);fig.savefig(OUT/'before-after.svg',bbox_inches='tight');fig.savefig(OUT/'before-after.png',dpi=160,bbox_inches='tight');plt.close(fig)
    svg=OUT/'before-after.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    # Discrete held frames only; no interpolated, unevaluated phase settings.
    frames=[Image.open(OUT/f'demo-{k}.png').convert('RGB') for k in range(4)]
    frames[0].save(OUT/'contributor-progress.gif',save_all=True,append_images=frames[1:],duration=[2200,2800,2200,4000],loop=0)
    Path('trial/demo-data.json').write_text(json.dumps([dict(label=s['label'],phase_bins=(np.rint(s['phase']*64/(2*np.pi)).astype(int)%64).tolist(),metrics=s['metrics']) for s in states],indent=2)+'\n')
    print('Wrote four evaluated demo states, PNG, SVG, and GIF.')
if __name__=='__main__':main()
