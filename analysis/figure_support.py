"""Portable export helpers for the English RAFS paper figures."""
from pathlib import Path
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.text import Text

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'figures';PDF=OUT/'pdf';PREVIEW=OUT/'previews'
SNAPSHOT=ROOT/'results/figure_data.json'
INK='#161616'

def configure():
    fonts=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'
    for name in ('times.ttf','timesbd.ttf'):
        if (fonts/name).exists():font_manager.fontManager.addfont(str(fonts/name))
    available={font.name for font in font_manager.fontManager.ttflist}
    family='Times New Roman' if 'Times New Roman' in available else 'DejaVu Serif'
    plt.rcParams.update({'font.family':family,'font.size':7.5,'mathtext.fontset':'stix',
        'axes.labelsize':7.8,'axes.titlesize':8.2,'xtick.labelsize':7,'ytick.labelsize':7,
        'legend.fontsize':6.9,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,
        'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.55,
        'axes.edgecolor':'#56616A','xtick.major.width':.5,'ytick.major.width':.5,
        'xtick.major.size':2.5,'ytick.major.size':2.5,'axes.grid':False,
        'legend.frameon':False,'legend.handlelength':1.4,'legend.columnspacing':1.2,
        'pdf.fonttype':42,'svg.fonttype':'none','axes.unicode_minus':False,
        'savefig.facecolor':'white','figure.facecolor':'white','lines.solid_capstyle':'round'})

def save(fig,name):
    for folder in (OUT,PDF,PREVIEW):folder.mkdir(parents=True,exist_ok=True)
    fig.canvas.draw()
    for text in fig.findobj(match=Text):text.set_color(INK)
    fig.savefig(OUT/(name+'.svg'),bbox_inches='tight',pad_inches=.035)
    fig.savefig(PDF/(name+'.pdf'),bbox_inches='tight',pad_inches=.035)
    fig.savefig(PREVIEW/(name+'.png'),dpi=450,bbox_inches='tight',pad_inches=.035)
    plt.close(fig)
