"""SciDraw-inspired, evidence-preserving figures 3–11 for the RAFS paper.

Run: python analysis/plot_figures.py
Matplotlib implementations written for this project's numeric snapshot, informed
by the public R/Python examples at https://avi7ii.github.io/scidraw-gallery/.
Template sample data, significance tests and confidence bands are not imported.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.lines import Line2D
from matplotlib.patches import Patch,Rectangle
import figure_support as j

# Traceable aesthetic references; card numbers are the gallery's actual IDs.
TEMPLATES={
    3:[97],4:[129],5:[97,87],6:[125,126],7:[85],
    8:[54,55],9:[101,102],10:[157],11:[115,129],
}
REPO='https://github.com/Avi7ii/scidraw-gallery'
SC,RAFS,GROUP='#35978F','#BF812D','#7B6BA7'
INK,GRID,PALE='#161616','#E8ECEB','#B8C6C5'
WIDTH=3.40
SAVE=j.save

def configure():
    j.configure();j.SC,j.RAFS,j.GROUP=SC,RAFS,GROUP
    j.INK,j.MUTED,j.GRID=INK,INK,GRID
    plt.rcParams.update({'axes.edgecolor':INK,'axes.linewidth':.65,
        'xtick.color':INK,'ytick.color':INK,'font.size':7.5,
        'axes.labelsize':7.8,'axes.titlesize':8.0,'legend.fontsize':6.8,
        'xtick.direction':'out','ytick.direction':'out'})

def frame(ax,axis=None):
    ax.set_axisbelow(True)
    if axis:ax.grid(axis=axis,color=GRID,lw=.45)
    if axis=='x':ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)

def strip(ax,title,face='#EDF3F1'):
    ax.add_patch(Rectangle((0,1.015),1,.105,transform=ax.transAxes,clip_on=False,
        fc=face,ec='none',zorder=0))
    ax.text(.5,1.065,title,transform=ax.transAxes,ha='center',va='center',fontsize=7.1)

def method_legend(fig,top=.995,ncol=3,baseline=False):
    handles=[]
    if baseline:handles.append(Patch(fc=PALE,ec=INK,lw=.45,label='Unmitigated'))
    handles.extend([Patch(fc=SC,ec=INK,lw=.45,label='ShortcutCatcher'),
        Patch(fc=RAFS,ec=INK,lw=.45,label='RAFS')])
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.55,top),ncol=ncol,fontsize=6.7)

def fig3(d):
    v,c=np.asarray(d['v']),np.asarray(d['c']);y=np.arange(5)
    fig,ax=plt.subplots(figsize=(WIDTH,2.55));fig.subplots_adjust(left=.30,right=.97,bottom=.17,top=.85)
    ax.axhspan(3.52,4.48,fc='#F8F1E4',zorder=0)
    ax.barh(y-.16,v,height=.27,fc='white',ec=SC,lw=.8,label='Validation V',zorder=3)
    ax.barh(y+.16,c,height=.27,fc=RAFS,ec=RAFS,lw=.5,label='Test C',zorder=3)
    for yy,a,b in zip(y,v,c):
        ax.text(a+.6,yy-.16,f'{a:.1f}',va='center',fontsize=6.7)
        ax.text(b+.6,yy+.16,f'{b:.1f}',va='center',fontsize=6.7)
    ax.set_yticks(y,['No removal','Source IP','Src./dst. IP','TCP timestamps','IPs + timestamps'])
    ax.invert_yaxis();ax.set_xlim(0,42);ax.set_xticks([0,10,20,30,40]);frame(ax,'x')
    ax.set_xlabel('Macro F1-score (%)')
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.05),ncol=2)
    SAVE(fig,'fig3_joint_removal_zh')

def fig4(d,labels):
    a,b=np.asarray(d['d']),np.asarray(d['c']);delta=a-b;y=np.arange(9)
    fig=plt.figure(figsize=(WIDTH,2.95))
    ax=fig.add_axes([.28,.17,.48,.65]);side=fig.add_axes([.82,.17,.15,.65],sharey=ax)
    for bound in (2.5,5.5):
        ax.axhline(bound,color='#CBD4D1',lw=.6);side.axhline(bound,color='#CBD4D1',lw=.6)
    ax.hlines(y,b,a,color='#849C96',lw=.85)
    ax.scatter(a,y,s=18,fc='white',ec=SC,lw=.8,zorder=3)
    ax.scatter(b,y,s=20,fc=RAFS,ec='white',lw=.35,zorder=4)
    ax.set_yticks(y,labels,fontsize=6.6);ax.set_ylim(8.6,-.6);ax.set_xlim(0,100)
    ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Macro F1-score (%)');frame(ax,'x')
    side.barh(y,delta,height=.40,color=SC,alpha=.82)
    for yy,v in zip(y,delta):side.text(0,yy-.28,f'{v:.1f}',fontsize=6.2,va='bottom')
    side.set_xlim(0,85);side.set_xticks([0,80]);side.set_xlabel('Gap Δ',fontsize=7.0)
    side.tick_params(axis='y',left=False,labelleft=False)
    for sp in ('left','right','top'):side.spines[sp].set_visible(False)
    fig.legend(handles=[Line2D([],[],marker='o',mfc='white',mec=SC,lw=0,ms=4,label='In-distribution D'),
        Line2D([],[],marker='o',mfc=RAFS,mec='white',lw=0,ms=4,label='Deployment C')],
        loc='upper center',bbox_to_anchor=(.57,.915),ncol=2,fontsize=6.8)
    SAVE(fig,'fig4_shortcut_gap_zh')

def fig5(d):
    fig,axs=plt.subplots(1,3,figsize=(WIDTH,2.75),sharey=True)
    fig.subplots_adjust(left=.14,right=.98,bottom=.18,top=.77,wspace=.12)
    methods=[('unmitigated','Unmitigated',PALE),('none','ShortcutCatcher',SC),('grouppair','RAFS',RAFS)]
    for i,(ax,family,title) in enumerate(zip(axs,['vpn-service','app53-time','app53-version'],['VPN','App-Time','App-Version'])):
        for k,(method,label,color) in enumerate(methods):
            row=d[family][method];x=np.arange(2)+(k-1)*.235
            ax.bar(x,row['mean'],width=.205,color=color,ec=INK,lw=.4,zorder=3,
                yerr=row['sd'],error_kw={'ecolor':INK,'elinewidth':.6,'capsize':1.5,'capthick':.6})
        ax.set_xticks([0,1],['S0','S1']);ax.set_xlim(-.5,1.5);ax.set_ylim(0,80);ax.set_yticks([0,20,40,60,80])
        if i:ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        frame(ax,'y');strip(ax,title)
    axs[0].set_ylabel('Deployment macro F1-score (%)');method_legend(fig,baseline=True)
    SAVE(fig,'fig5_temporal_zh')

def fig6(d):
    fig,axs=plt.subplots(1,3,figsize=(WIDTH,2.97),sharey=True)
    fig.subplots_adjust(left=.15,right=.98,bottom=.18,top=.77,wspace=.18)
    jitter=np.array([-.09,.03,.10,-.03,.07,-.07,.01,.12,-.12,.05])
    for i,(ax,scene) in enumerate(zip(axs,['s0','s1','s2'])):
        a=np.asarray(d[scene]['none']);b=np.asarray(d[scene]['grouppair'])
        for seed,(av,bv) in enumerate(zip(a,b)):
            ax.plot([0+jitter[seed],1+jitter[seed]],[av,bv],color='#A6B5B0',lw=.45,alpha=.65,zorder=1)
        boxes=ax.boxplot([a,b],positions=[0,1],widths=.42,patch_artist=True,showfliers=False,
            medianprops={'color':INK,'linewidth':.8},whiskerprops={'color':INK,'linewidth':.55},
            capprops={'color':INK,'linewidth':.55},boxprops={'edgecolor':INK,'linewidth':.6})
        for patch,color in zip(boxes['boxes'],[SC,RAFS]):patch.set_facecolor(colors.to_rgba(color,.18))
        ax.scatter(jitter,a,s=14,c=SC,ec='white',lw=.3,zorder=4)
        ax.scatter(1+jitter,b,s=14,c=RAFS,ec='white',lw=.3,zorder=4)
        ax.set_xticks([0,1],['SC','RAFS'],fontsize=6.6);ax.set_xlim(-.45,1.45)
        ax.set_ylim(25,65);ax.set_yticks([30,40,50,60]);frame(ax)
        strip(ax,f'{scene.upper()}  Δ +{(b-a).mean():.1f}')
        ax.text(.5,-.17,f'Wins {int((b>a).sum())}/10',transform=ax.transAxes,ha='center',fontsize=6.8)
        if i:ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
    axs[0].set_ylabel('Deployment macro F1-score (%)')
    method_legend(fig,top=.925,ncol=2)
    SAVE(fig,'fig6_vpn_seeds_zh')

def fig7(d):
    fig,ax=plt.subplots(figsize=(WIDTH,2.80));fig.subplots_adjust(left=.16,right=.98,bottom=.18,top=.82)
    for method,label,color,ls in [('none','ShortcutCatcher',SC,(0,(4,2))),('group','Field grouping',GROUP,(0,(1,2))),('grouppair','RAFS',RAFS,'-')]:
        x=np.asarray(d[method]['fits']);y=np.asarray(d[method]['v'])
        ax.plot(x,y,c=color,ls=ls,lw=1.2,label=label,marker='o' if method=='grouppair' else None,
            ms=2.5,mec='white',mew=.3)
        k=y.argmax();ax.scatter(x[k],y[k],s=29,c=color,ec='white',lw=.7,zorder=5)
    row=d['grouppair'];k=next(i for i,v in enumerate(row['removed']) if 'ip_src' in v and 'tcp_timestamp' in v)
    ax.axvline(row['fits'][k],color='#98A8A1',lw=.65,ls=(0,(2,3)),zorder=0)
    ax.annotate('Src. IP + TCP timestamp\nRound %d; %d retrainings'%(k+1,row['fits'][k]),
        xy=(row['fits'][k],row['v'][k]),xytext=(170,24),fontsize=6.6,
        arrowprops={'arrowstyle':'-','lw':.6,'color':INK},bbox={'fc':'white','ec':'none','pad':1.1})
    ax.set(xlim=(0,540),ylim=(0,80),xticks=[0,150,300,450],yticks=[0,20,40,60,80])
    ax.set_xlabel('Cumulative retrainings');ax.set_ylabel('Macro F1-score on V (%)');frame(ax)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),ncol=3,fontsize=6.4)
    SAVE(fig,'fig7_vpn_s2_trajectory_zh')

def fig8(d):
    a=np.asarray(d['matrix']);fig=plt.figure(figsize=(WIDTH,4.28))
    ax=fig.add_axes([.31,.19,.52,.73]);xs=np.array([0,1,2,3.6,4.6,5.6,7.2,8.2,9.2]);yy,xx=np.indices(a.shape)
    palette=['#FFFFFF','#D9EBE5','#8BC5B5','#287F6F']
    cmap=colors.ListedColormap(palette);norm=colors.BoundaryNorm([-.5,.5,1.5,2.5,3.5],4)
    sizes=np.where(a==0,2.2,8+15*a)
    ax.scatter(xs[xx.ravel()],yy.ravel(),s=sizes.ravel(),c=a.ravel(),cmap=cmap,norm=norm,
        edgecolors='#6E8B80',linewidths=.35,zorder=3)
    ax.set(xlim=(-.7,9.9),ylim=(29.7,-1.1))
    ax.set_yticks(range(30),d['fields'],fontsize=6.3)
    ax.set_xticks(xs,['S0','S1','S2']*3,fontsize=6.6)
    for center,label in zip([1,4.6,8.2],['VPN','App-Time','App-Version']):ax.text(center,-1.45,label,ha='center',va='bottom',fontsize=6.7)
    start=0
    for group,count in d['groups']:
        if start:ax.axhline(start-.5,color='#A9BDB4',lw=.5,zorder=0)
        ax.text(10.15,start+(count-1)/2,group,fontsize=6.3,va='center')
        start+=count
    for boundary in [2.8,6.4]:ax.axvline(boundary,color=GRID,lw=.7)
    ax.tick_params(axis='both',length=0,pad=3)
    for sp in ax.spines.values():sp.set_visible(False)
    handles=[Line2D([],[],ls='',marker='o',ms=np.sqrt(2.2 if value==0 else 8+15*value),mfc=palette[value],mec='#6E8B80',mew=.4,label=str(value)) for value in range(4)]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.57,.045),ncol=4,title='Removal count (3 seeds)',fontsize=6.7,title_fontsize=7.0,columnspacing=1.1)
    SAVE(fig,'fig8_removed_fields_zh')

def fig9(d):
    fig,axs=plt.subplots(1,2,figsize=(WIDTH,2.72),sharey=True)
    fig.subplots_adjust(left=.25,right=.98,bottom=.28,top=.82,wspace=.20)
    labels=['Source IP','Destination IP','TCP timestamp','Echo timestamp'];y=np.arange(4)
    for i,(ax,method,title) in enumerate(zip(axs,['none','grouppair'],['(a) ShortcutCatcher','(b) RAFS'])):
        a=np.asarray(d[method]);left=np.zeros(4)
        for state,col in [(2,SC),(1,RAFS),(0,'#FFFFFF')]:
            counts=(a==state).sum(axis=0)
            ax.barh(y,counts,left=left,height=.51,color=col,ec=INK,lw=.4,zorder=3)
            for row,n in enumerate(counts):
                if n:ax.text(left[row]+n/2,row,str(n),ha='center',va='center',fontsize=7.1)
            left+=counts
        assert (left==10).all()
        ax.set_yticks(y,labels,fontsize=7.0);ax.set_ylim(3.6,-.6)
        ax.set_xlim(0,10);ax.set_xticks([0,5,10]);ax.tick_params(axis='y',length=0,pad=4)
        frame(ax,'x');strip(ax,title)
    fig.legend(handles=[Patch(fc=SC,ec=INK,lw=.4,label='Full removal'),Patch(fc=RAFS,ec=INK,lw=.4,label='Partial removal'),
        Patch(fc='white',ec=INK,lw=.4,label='No removal')],
        loc='upper center',bbox_to_anchor=(.59,1.015),ncol=3,fontsize=6.5,columnspacing=1.0)
    fig.text(.62,.12,'Seeds (n = 10)',ha='center',fontsize=7.2)
    SAVE(fig,'fig9_vpn_s2_removed_zh')

def fig10(d,labels):
    fig=plt.figure(figsize=(WIDTH,3.08));axs=[fig.add_axes([.29,.20,.29,.57]),fig.add_axes([.67,.20,.29,.57])]
    for i,(ax,key,title,vmax,pale) in enumerate(zip(axs,['gap','rho'],['(a) F1 loss (pp)','(b) Spearman ρ'],[9,1],['#E9C39B','#B9DDD1'])):
        a=np.column_stack([d['none'][key],d['grouppair'][key]])
        cmap=colors.LinearSegmentedColormap.from_list(key,['#FFFFFF',pale])
        im=ax.pcolormesh(np.arange(3)-.5,np.arange(10)-.5,a,cmap=cmap,vmin=0,vmax=vmax,
            shading='flat',edgecolors='white',linewidth=1.0,rasterized=False)
        ax.set_ylim(8.5,-.5);ax.set_xticks([0,1],['SC','RAFS'],fontsize=6.8)
        ax.set_yticks(range(9),labels if i==0 else [],fontsize=6.5)
        for row in range(9):
            for col in range(2):ax.text(col,row,f'{a[row,col]:.1f}' if key=='gap' else f'{a[row,col]:.2f}',ha='center',va='center',fontsize=7.0)
        for boundary in [2.5,5.5]:ax.axhline(boundary,color='#899A91',lw=.5)
        ax.tick_params(which='both',length=0,pad=3);strip(ax,title,'#F2F1EC')
        for sp in ax.spines.values():sp.set_visible(False)
        cax=fig.add_axes([ax.get_position().x0,.095,.29,.018]);cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[0,vmax/2,vmax])
        cb.solids.set_rasterized(False)
        cb.outline.set_visible(False);cb.ax.tick_params(labelsize=6.1,length=2,pad=1)
        cb.set_label('Lower is better' if key=='gap' else 'Higher is better',fontsize=6.6,labelpad=2)
    fig.text(.62,.875,'SC: ShortcutCatcher',ha='center',fontsize=6.9)
    SAVE(fig,'fig10_val_reliability_zh')

def fig11(d,labels):
    a,b=np.asarray(d['none']),np.asarray(d['grouppair']);saving=100*(a-b)/a;y=np.arange(9)
    fig=plt.figure(figsize=(WIDTH,3.10));ax=fig.add_axes([.28,.17,.49,.65]);side=fig.add_axes([.84,.17,.14,.65],sharey=ax)
    ax.barh(y,a,height=.62,color=colors.to_rgba(SC,.24),ec=SC,lw=.45,label='ShortcutCatcher')
    ax.barh(y,b,height=.30,color=RAFS,ec=RAFS,lw=.4,label='RAFS')
    for yy,v in zip(y,b):ax.text(v+4,yy,f'{v:.0f}',va='center',fontsize=6.4)
    ax.set_yticks(y,labels,fontsize=6.6);ax.set_ylim(8.65,-.65);ax.set_xlim(0,500);ax.set_xticks([0,200,400])
    ax.set_xlabel('Retrainings to best round',fontsize=7.2);frame(ax,'x')
    for boundary in [2.5,5.5]:ax.axhline(boundary,color='#CAD4CF',lw=.5)
    for yy,v in zip(y,saving):side.text(.5,yy,f'{v:.0f}%',ha='center',va='center',fontsize=7.0)
    side.set_xlim(0,1);side.set_xticks([]);side.tick_params(axis='y',left=False,labelleft=False)
    for sp in side.spines.values():sp.set_visible(False)
    strip(side,'Reduction','#F8F1E4')
    fig.legend(handles=[Patch(fc=colors.to_rgba(SC,.24),ec=SC,label=f'SC (mean {a.mean():.0f})'),Patch(fc=RAFS,label=f'RAFS (mean {b.mean():.0f})')],
        loc='upper center',bbox_to_anchor=(.61,.995),ncol=2,fontsize=6.6)
    SAVE(fig,'fig11_retrains_zh')

def main():
    configure();d=json.loads(j.SNAPSHOT.read_text(encoding='utf8'))
    d['labels']=[label.replace('App-Ver.','App-Version') for label in d['labels']]
    plots=[lambda:fig3(d['fig3']),lambda:fig4(d['fig4'],d['labels']),lambda:fig5(d['fig5']),
        lambda:fig6(d['fig6']),lambda:fig7(d['fig7']),lambda:fig8(d['fig8']),lambda:fig9(d['fig9']),
        lambda:fig10(d['fig10'],d['labels']),lambda:fig11(d['fig11'],d['labels'])]
    for draw in plots:draw()
    print('Rendered 9 SciDraw-inspired figures from the unchanged numeric snapshot.')

if __name__=='__main__':main()
