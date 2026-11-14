#!/usr/bin/env python3
"""Optional standalone descriptive plots; requires Matplotlib, no experiments."""
from pathlib import Path
import argparse,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
P=Path(__file__).resolve().parent.parent

def plot(out):
 out=Path(out)
 if out.exists():raise FileExistsError('Choose a new figure directory')
 out.mkdir(parents=True)
 load=lambda f:json.loads((P/'expected'/f).read_text())
 conditions={r['condition']:r for r in load('CONDITION_SUMMARIES.json') if r['stratum']=='all'}
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':12,'axes.labelsize':11,'svg.fonttype':'none'})
 fig=plt.figure(figsize=(13,10));grid=gridspec.GridSpec(2,2,figure=fig,height_ratios=[1,1]);ax=fig.add_subplot(grid[0,:]);colors=['#d9e4ec','#5889b0','#183f68'];names=['BN1','BN2','PN1','PN2','BE1','BE2','PE1','PE2'];bottom=[0]*len(names)
 for i,color in enumerate(colors):
  vals=[conditions[n]['retrieved_copy_documents'].get(str(i),0) for n in names];ax.bar(names,vals,bottom=bottom,color=color,label=str(i)+(' copy retrieved' if i==1 else ' copies retrieved'),edgecolor='white')
  for x,(v,b) in enumerate(zip(vals,bottom)):
   if v>=5:ax.text(x,b+v/2,str(v),ha='center',va='center',color='white' if i==2 else '#152b3a',fontsize=10)
  bottom=[b+v for b,v in zip(bottom,vals)]
 ax.set_xticks(range(len(names)),[n+'\n'+' / '.join(str(conditions[n]['retrieved_copy_documents'].get(str(i),0)) for i in range(3)) for n in names]);ax.set_ylim(0,65);ax.set_ylabel('Selected case contexts (59 per condition)');ax.set_title('Actual retrieved copied documents (tick counts: 0 / 1 / 2 copies)');ax.legend(ncol=3,loc='upper left',bbox_to_anchor=(0,1.19),frameon=False)
 for col,panel,names,title in [(0,'reference',['PN1','PN2','PE1','PE2'],'Reference: original PN1 and reviewed variants'),(1,'reproduction',['PN2','PE1','PE2'],'Reproduction: reviewed secondary variants')]:
  ax=fig.add_subplot(grid[1,col]);bottom=[0]*len(names)
  for key,color,label in [('not_met','#cbd8e2','Not met'),('met','#244f74','Met'),('uncertain','#d5a243','Uncertain')]:
   vals=[conditions[n]['panels'][panel]['reviewed_field_values']['strict_endpoint'].get(key,0) for n in names];ax.bar(names,vals,bottom=bottom,color=color,label=label,edgecolor='white')
   for x,(v,b) in enumerate(zip(vals,bottom)):
    if v:ax.text(x,61 if key=='uncertain' else b+v/2,str(v),ha='center',va='center',color='white' if key=='met' else '#152b3a',fontsize=10)
   bottom=[b+v for b,v in zip(bottom,vals)]
  ax.set_ylim(0,64);ax.set_ylabel('Literal human endpoint labels (n=59)');ax.set_title(title)
  if col==0:ax.legend(ncol=3,loc='upper left',bbox_to_anchor=(0,1.19),frameon=False)
 fig.suptitle('FilterFlip: copy exposure and scoped endpoint judgments',fontsize=16,y=.99)
 fig.text(.06,.025,'Selected cases; repeated conditions are not independent trials. New PN1 reproduction has only 35 endpoint records and is omitted here.\nEach reproduction secondary row retains one test306 incomplete chain in its literal labels; paired calculations exclude that chain.',fontsize=10)
 fig.subplots_adjust(left=.075,right=.98,top=.88,bottom=.12,hspace=.47,wspace=.3)
 fig.savefig(out/'copy_exposure_endpoints.png',dpi=160);fig.savefig(out/'copy_exposure_endpoints.svg',metadata={'Date':None});plt.close(fig)
 contexts=load('TRUSTRAG_CONTEXTS.json');fig,axes=plt.subplots(1,2,figsize=(12,6.2))
 for ax,field,levels,title in [(axes[0],'core_usable',['yes','no','uncertain'],'Core usability: U → T'),(axes[1],'sufficient_support',['sufficient','partial','absent'],'External support: U → T')]:
  matrix=[[sum(r['judgment']['U_'+field]==u and r['judgment']['T_'+field]==t for r in contexts) for t in levels] for u in levels];ax.imshow(matrix,cmap='Blues',vmin=0,vmax=max(max(row) for row in matrix));ax.set_xticks(range(3),levels);ax.set_yticks(range(3),levels);ax.set_xlabel('T: stage-1 survivors');ax.set_ylabel('U: all retrieved passages');ax.set_title(title,pad=14)
  high=max(max(row) for row in matrix)
  for y,row in enumerate(matrix):
   for x,v in enumerate(row):ax.text(x,y,str(v),ha='center',va='center',color='white' if v>high*.5 else '#142d42',fontsize=20)
 fig.suptitle('TrustRAG stage 1 + frozen answering: all 36 context pairs',fontsize=15,y=.98)
 fig.text(.06,.035,'12 selected cases; 60 distinct fresh answers /72 logical U–T positions. Not independent trials or full TrustRAG.\nCore usability has one no→yes, eight yes→no and four uncertain pairs. Support loss and answer failure are distinct.',fontsize=10)
 fig.subplots_adjust(left=.09,right=.98,top=.83,bottom=.2,wspace=.45)
 fig.savefig(out/'trustrag_support_core.png',dpi=160);fig.savefig(out/'trustrag_support_core.svg',metadata={'Date':None});plt.close(fig)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();plot(args.out)
