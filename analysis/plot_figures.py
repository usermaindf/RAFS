"""Journal-style, single-column figures 3–11 from the existing experiment readers.

Run with the project's scientific Python environment:
  python paper/figures/journal_plots.py
The numeric snapshot is retained in journal_plot_data.json. Use --refresh-data
only when intentionally regenerating figures from new experiment outputs.
"""
from pathlib import Path
import os,sys,json,importlib.util,argparse,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,colors
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'figures'
PDF=OUT/'pdf'
PREVIEW=OUT/'previews'
SNAPSHOT=ROOT/'results/figure_data.json'
SC,RAFS,GROUP='#3C5488','#C65A3A','#9099A4'
INK,MUTED,GRID='#222831','#626A73','#E5E8EC'
LIGHT='#C7CDD4'
WIDTH=3.40


def read_data():
    raise RuntimeError('Use the supplied results/figure_data.json snapshot. Recompute experiments using reproduce.py.')


def configure():
    fonts=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'
    for name in ('times.ttf','timesbd.ttf','simsun.ttc'):
        if (fonts/name).exists():font_manager.fontManager.addfont(str(fonts/name))
    available={f.name for f in font_manager.fontManager.ttflist}
    families=[n for n in ['Times New Roman','SimSun','Noto Serif CJK SC','DejaVu Serif'] if n in available]
    if not any(n in available for n in ['SimSun','Noto Serif CJK SC']):
        raise RuntimeError('Chinese labels require SimSun or Noto Serif CJK SC. Install a CJK font and rerun.')
    plt.rcParams.update({
        'font.family':families,'font.size':7.5,
        'mathtext.fontset':'stix','axes.labelsize':7.8,'axes.titlesize':8.2,
        'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':6.9,
        'text.color':INK,'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,
        'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.55,
        'axes.edgecolor':'#9AA2AC','xtick.major.width':.5,'ytick.major.width':.5,
        'xtick.major.size':2.5,'ytick.major.size':2.5,'axes.grid':False,
        'legend.frameon':False,'legend.handlelength':1.4,'legend.columnspacing':1.2,
        'pdf.fonttype':42,'svg.fonttype':'none','axes.unicode_minus':False,
        'savefig.facecolor':'white','figure.facecolor':'white','lines.solid_capstyle':'round'})


def frame(ax,grid='y'):
    ax.set_axisbelow(True)
    ax.grid(axis=grid,color=GRID,linewidth=.45)
    if grid=='x':
        ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0,pad=3)


def save(fig,name):
    OUT.mkdir(exist_ok=True);PDF.mkdir(exist_ok=True);PREVIEW.mkdir(exist_ok=True)
    fig.savefig(PDF/(name+'.pdf'),bbox_inches='tight',pad_inches=.035)
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',pad_inches=.035)
    fig.savefig(PREVIEW/(name+'.png'),dpi=450,bbox_inches='tight',pad_inches=.035)
    # Keep the Markdown draft's canonical image paths synchronized as well.
    plt.close(fig)


def legend_pair(ax,labels=('ShortcutCatcher','RAFS')):
    handles=[Line2D([],[],marker='o',mfc='white',mec=SC,color=SC,lw=0,ms=4,label=labels[0]),
             Line2D([],[],marker='D',mfc=RAFS,mec='white',mew=.4,color=RAFS,lw=0,ms=4,label=labels[1])]
    ax.legend(handles=handles,loc='lower center',bbox_to_anchor=(.5,1.035),ncol=2)


def fig3(d):
    v=np.asarray(d['v']);c=np.asarray(d['c']);y=np.arange(5);h=.28
    fig,ax=plt.subplots(figsize=(WIDTH,2.38))
    fig.subplots_adjust(left=.29,right=.96,bottom=.17,top=.87)
    ax.axhspan(3.55,4.45,color='#FCF0EA',zorder=0)
    ax.barh(y-h/2,v,height=h,color=LIGHT,edgecolor='none',label='验证集 V')
    ax.barh(y+h/2,c,height=h,color=[SC]*4+[RAFS],edgecolor='none',label='检验集 C')
    for yy,a,b in zip(y,v,c):
        ax.text(a+.55,yy-h/2,f'{a:.1f}',ha='left',va='center',fontsize=6.8,color=MUTED)
        ax.text(b+.55,yy+h/2,f'{b:.1f}',ha='left',va='center',fontsize=6.8,color=INK)
    ax.set_yticks(y,['不删除','源 IP','源、目的 IP','两个时间戳','IP＋两个时间戳'])
    ax.get_yticklabels()[-1].set_color(RAFS)
    ax.set_xlim(0,42);ax.set_xticks([0,10,20,30,40]);ax.invert_yaxis()
    ax.set_xlabel('macro-F1（%）');frame(ax,'x')
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.035),ncol=2)
    save(fig,'fig3_joint_removal_zh')


def fig4(d,labels):
    a,b=np.asarray(d['d']),np.asarray(d['c']);y=np.arange(len(a))
    fig,ax=plt.subplots(figsize=(WIDTH,2.85))
    fig.subplots_adjust(left=.28,right=.97,bottom=.16,top=.85)
    ax.hlines(y,b,a,color='#CDD2D8',lw=1.1)
    ax.scatter(a,y,s=18,facecolors='white',edgecolors='#8B95A1',lw=.8,zorder=3)
    ax.scatter(b,y,s=20,color=SC,edgecolors='white',lw=.4,zorder=4)
    for yy,delta in zip(y,a-b):ax.text(100,yy,f'{delta:.1f}',ha='right',va='center',fontsize=6.7,color=MUTED)
    ax.text(1,1.012,r'$\Delta$',transform=ax.transAxes,ha='right',va='bottom',fontsize=7.4)
    ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xticks([0,25,50,75,100])
    ax.set_xlabel('macro-F1（%）');frame(ax,'x')
    ax.legend(handles=[
        Line2D([],[],marker='o',mfc='white',mec='#8B95A1',ms=4,lw=0,label='同分布测试集 D'),
        Line2D([],[],marker='o',mfc=SC,mec='white',ms=4,lw=0,label='部署检验集 C')],
        loc='lower center',bbox_to_anchor=(.47,1.055),ncol=2,fontsize=6.6)
    save(fig,'fig4_shortcut_gap_zh')


def fig5(d):
    methods=[('unmitigated','不缓解',LIGHT),('none','ShortcutCatcher',SC),('grouppair','RAFS',RAFS)]
    families=['vpn-service','app53-time','app53-version']
    fig,ax=plt.subplots(figsize=(WIDTH,2.64))
    fig.subplots_adjust(left=.16,right=.98,bottom=.28,top=.84)
    x=np.arange(6);w=.245
    for i,(method,label,color) in enumerate(methods):
        means=np.concatenate([d[f][method]['mean'] for f in families])
        errs=np.concatenate([d[f][method]['sd'] for f in families])
        ax.bar(x+(i-1)*w,means,width=w*.88,color=color,label=label,
            yerr=errs,error_kw={'elinewidth':.65,'capsize':1.5,'capthick':.6,'ecolor':'#505A65'})
    for v in (1.5,3.5):ax.axvline(v,color=GRID,lw=.6,zorder=0)
    ax.set_xticks(x,['S0','S1']*3)
    for xx,label in zip([.5,2.5,4.5],['VPN','App-Time','App-Version']):
        ax.text(xx,-.19,label,transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=7.2)
    ax.set_ylim(0,80);ax.set_yticks([0,20,40,60,80]);ax.set_ylabel('部署 macro-F1（%）')
    frame(ax);ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),ncol=3,fontsize=6.7)
    save(fig,'fig5_temporal_zh')


def fig6(d):
    fig,axs=plt.subplots(2,2,figsize=(WIDTH,3.28))
    fig.subplots_adjust(left=.18,right=.98,bottom=.15,top=.89,wspace=.40,hspace=.61)
    for i,(ax,scene) in enumerate(zip(axs.ravel(),('s0','s1','s2'))):
        a=np.asarray(d[scene]['none']);b=np.asarray(d[scene]['grouppair'])
        ax.plot([25,65],[25,65],ls=(0,(3,3)),lw=.65,color='#B0B8C0')
        ax.scatter(a,b,s=19,c=RAFS,ec='white',lw=.5,zorder=3,alpha=.95)
        ax.set(xlim=(25,65),ylim=(25,65),xticks=[30,45,60],yticks=[30,45,60])
        ax.set_aspect('equal');frame(ax)
        ax.set_title(f'({chr(97+i)}) {scene.upper()}',loc='left',pad=5)
        ax.text(1,1.045,f'Δ +{(b-a).mean():.1f}',transform=ax.transAxes,ha='right',va='bottom',fontsize=6.8,color=RAFS)
        ax.text(.04,.94,f'胜 {int((b>a).sum())}/10',transform=ax.transAxes,ha='left',va='top',fontsize=6.5,color=MUTED)
    note=axs.ravel()[3];note.axis('off')
    note.text(.03,.53,'10 个配对种子\n虚线：两者相同\n上方：RAFS 更优',fontsize=7.4,va='center',linespacing=1.7)
    fig.text(.56,.025,'ShortcutCatcher macro-F1（%）',ha='center',fontsize=7.8)
    fig.text(.015,.54,'RAFS macro-F1（%）',rotation=90,va='center',fontsize=7.8)
    save(fig,'fig6_vpn_seeds_zh')


def fig7(d):
    fig,ax=plt.subplots(figsize=(WIDTH,2.72))
    fig.subplots_adjust(left=.15,right=.98,bottom=.17,top=.83)
    styles=[('none','ShortcutCatcher',SC,(0,(4,2)),None),
            ('group','仅字段分组',GROUP,(0,(1,2)),None),
            ('grouppair','RAFS',RAFS,'-','o')]
    for method,label,color,ls,marker in styles:
        x=np.asarray(d[method]['fits']);y=np.asarray(d[method]['v'])
        ax.plot(x,y,label=label,color=color,lw=1.25 if method=='grouppair' else 1.05,
            ls=ls,marker=marker,ms=2.7,mew=.35,mec='white')
        k=int(y.argmax())
        ax.plot(x[k],y[k],marker='o',ms=5.6,mfc=color,mec='white',mew=.8,zorder=5)
    row=d['grouppair'];j=next(i for i,r in enumerate(row['removed']) if 'ip_src' in r and 'tcp_timestamp' in r)
    ax.annotate('源 IP 与时间戳联合删除\n第 %d 轮，%d 次重训'%(j+1,row['fits'][j]),
        xy=(row['fits'][j],row['v'][j]),xytext=(165,24),
        fontsize=6.7,ha='left',va='center',linespacing=1.35,
        arrowprops={'arrowstyle':'-','color':MUTED,'lw':.6},
        bbox={'fc':'white','ec':'none','pad':1.2})
    ax.set(xlim=(0,540),ylim=(0,80),xticks=[0,150,300,450],yticks=[0,20,40,60,80])
    ax.set_xlabel('累计重训次数');ax.set_ylabel('V 上 macro-F1（%）');frame(ax)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.03),ncol=3,fontsize=6.5)
    save(fig,'fig7_vpn_s2_trajectory_zh')


def fig8(d):
    a=np.asarray(d['matrix'])
    fig=plt.figure(figsize=(WIDTH,4.05))
    ax=fig.add_axes([.30,.14,.54,.79])
    cmap=colors.ListedColormap(['#F4F5F7','#F3D8CB','#E5A183',RAFS])
    norm=colors.BoundaryNorm([-.5,.5,1.5,2.5,3.5],4)
    im=ax.pcolormesh(np.arange(a.shape[1]+1)-.5,np.arange(a.shape[0]+1)-.5,
        a,cmap=cmap,norm=norm,shading='flat',rasterized=False)
    ax.set_ylim(a.shape[0]-.5,-.5)
    ax.set_yticks(np.arange(len(d['fields'])),d['fields'],fontsize=6.3)
    ax.set_xticks(range(9),['S0','S1','S2']*3,fontsize=6.7)
    for center,label in zip([1,4,7],['VPN','App-Time','App-Version']):
        ax.text(center,-1.15,label,ha='center',va='bottom',fontsize=6.9)
    k=0
    for group,count in d['groups']:
        if k:ax.axhline(k-.5,color='white',lw=1.6)
        ax.text(8.80,k+(count-1)/2,group,fontsize=6.4,ha='left',va='center',color=MUTED)
        k+=count
    for v in (2.5,5.5):ax.axvline(v,color='white',lw=1.4)
    ax.set_xticks(np.arange(-.5,9),minor=True)
    ax.set_yticks(np.arange(-.5,len(a)),minor=True)
    ax.grid(which='minor',color='white',lw=.4)
    ax.tick_params(which='minor',length=0);ax.tick_params(which='major',length=0,pad=3)
    for spine in ax.spines.values():spine.set_visible(False)
    cax=fig.add_axes([.39,.05,.40,.018])
    cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[0,1,2,3])
    cb.outline.set_visible(False);cb.ax.tick_params(length=0,pad=2,labelsize=6.8)
    cb.set_label('删除频次（共 3 个种子）',fontsize=7.0,labelpad=3)
    save(fig,'fig8_removed_fields_zh')


def fig9(d):
    fig,axs=plt.subplots(1,2,figsize=(WIDTH,2.95),sharey=True)
    fig.subplots_adjust(left=.13,right=.98,bottom=.27,top=.79,wspace=.23)
    labels=['源 IP','目的 IP','时间戳','回显时间戳']
    for i,(ax,method,color,title) in enumerate(zip(axs,('none','grouppair'),(SC,RAFS),('ShortcutCatcher','RAFS'))):
        a=np.asarray(d[method])
        cmap=colors.ListedColormap(['#F4F5F7','#BAC4D0',color])
        ax.pcolormesh(np.arange(5)-.5,np.arange(11)-.5,a,cmap=cmap,
            vmin=-.5,vmax=2.5,shading='flat',rasterized=False)
        ax.set_ylim(9.5,-.5)
        ax.set_xticks(range(4),labels,rotation=45,ha='right',fontsize=6.2)
        ax.set_yticks(range(10),range(10),fontsize=6.4)
        ax.set_title(f'({chr(97+i)}) {title}',fontsize=7.5,pad=22,loc='left')
        count=int((a==2).all(axis=1).sum())
        ax.text(0,1.03,f'完整删除：{count}/10',transform=ax.transAxes,fontsize=6.6,va='bottom',color=MUTED)
        ax.set_xticks(np.arange(-.5,4),minor=True);ax.set_yticks(np.arange(-.5,10),minor=True)
        ax.grid(which='minor',color='white',lw=.7);ax.tick_params(which='both',length=0)
        for spine in ax.spines.values():spine.set_visible(False)
    axs[0].set_ylabel('随机种子',fontsize=7.3)
    fig.legend(handles=[Patch(fc='#F4F5F7',ec='#C8CED6',lw=.5,label='未删除'),
        Patch(fc='#BAC4D0',label='仅删除部分列'),
        Patch(fc=SC,label='全部删除（ShortcutCatcher）'),
        Patch(fc=RAFS,label='全部删除（RAFS）')],
        loc='lower center',bbox_to_anchor=(.5,.005),ncol=2,fontsize=6.1,columnspacing=1.0,handlelength=1.2)
    save(fig,'fig9_vpn_s2_removed_zh')


def paired(ax,a,b,labels):
    y=np.arange(len(a))
    ax.hlines(y,np.minimum(a,b),np.maximum(a,b),color='#CAD0D7',lw=1.0)
    ax.scatter(a,y,s=17,facecolors='white',edgecolors=SC,lw=.8,zorder=3)
    ax.scatter(b,y,s=20,marker='D',color=RAFS,edgecolors='white',lw=.35,zorder=4)
    ax.set_yticks(y,labels,fontsize=6.7);ax.invert_yaxis();frame(ax,'x')


def fig10(d,labels):
    fig,axs=plt.subplots(2,1,figsize=(WIDTH,4.55))
    fig.subplots_adjust(left=.28,right=.97,bottom=.10,top=.86,hspace=.64)
    paired(axs[0],np.asarray(d['none']['gap']),np.asarray(d['grouppair']['gap']),labels)
    axs[0].set_title('(a) 与 oracle 轮的 F1 差',loc='left',fontsize=8.0,pad=7)
    axs[0].set_xlim(0,9);axs[0].set_xticks([0,3,6,9]);axs[0].set_xlabel('F1 损失（点）')
    paired(axs[1],np.asarray(d['none']['rho']),np.asarray(d['grouppair']['rho']),labels)
    axs[1].set_title('(b) V 与 C 上分数的秩相关',loc='left',fontsize=8.0,pad=7)
    axs[1].set_xlim(0,1);axs[1].set_xticks([0,.25,.5,.75,1]);axs[1].set_xlabel(r'Spearman $\rho$')
    fig.legend(handles=[Line2D([],[],marker='o',mfc='white',mec=SC,ms=4,lw=0,label='ShortcutCatcher'),
        Line2D([],[],marker='D',mfc=RAFS,mec='white',mew=.4,ms=4,lw=0,label='RAFS')],
        loc='upper center',bbox_to_anchor=(.62,.993),ncol=2,fontsize=6.8)
    save(fig,'fig10_val_reliability_zh')


def fig11(d,labels):
    a,b=np.asarray(d['none']),np.asarray(d['grouppair'])
    fig,ax=plt.subplots(figsize=(WIDTH,3.20))
    fig.subplots_adjust(left=.28,right=.98,bottom=.15,top=.86)
    y=np.arange(len(a));h=.28
    ax.barh(y-h/2,a,height=h,color=SC,label=f'ShortcutCatcher（均值 {a.mean():.0f}）')
    ax.barh(y+h/2,b,height=h,color=RAFS,label=f'RAFS（均值 {b.mean():.0f}）')
    for yy,v in zip(y,b):
        ax.text(v+5,yy+h/2,f'{v:.0f}',va='center',fontsize=6.1,color=RAFS)
    for boundary in (2.5,5.5):ax.axhline(boundary,color=GRID,lw=.6)
    ax.set_yticks(y,labels,fontsize=6.7);ax.invert_yaxis();frame(ax,'x')
    ax.set_xlim(0,500);ax.set_xticks([0,100,200,300,400,500])
    ax.set_xlabel('到达最佳轮的重训次数')
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.04),ncol=1,fontsize=6.7)
    save(fig,'fig11_retrains_zh')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-data',action='store_true')
    parser.add_argument('--figures',nargs='+',type=int,choices=range(3,12),default=list(range(3,12)))
    args=parser.parse_args()
    data=read_data() if args.refresh_data or not SNAPSHOT.exists() else json.loads(SNAPSHOT.read_text(encoding='utf8'))
    configure()
    labels=data['labels']
    plots={3:lambda:fig3(data['fig3']),4:lambda:fig4(data['fig4'],labels),
        5:lambda:fig5(data['fig5']),6:lambda:fig6(data['fig6']),7:lambda:fig7(data['fig7']),
        8:lambda:fig8(data['fig8']),9:lambda:fig9(data['fig9']),
        10:lambda:fig10(data['fig10'],labels),11:lambda:fig11(data['fig11'],labels)}
    for number in args.figures:plots[number]()
    print('Rendered %d journal-style single-column analysis figures from the saved data snapshot.'%len(args.figures))


if __name__=='__main__':main()
