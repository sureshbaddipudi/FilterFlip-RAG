"""Plot the frozen offline summary; does not run a model."""
import argparse,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser();p.add_argument('--analysis',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('Use a new plot output directory')
    rows=[x for x in json.loads((a.analysis/'CONDITION_TABLES.json').read_text()) if x['dataset']=='All']
    plt.rcParams.update({'font.size':11,'svg.hashsalt':'filterflip-task02-v1'})
    fig,axes=plt.subplots(1,2,figsize=(14,5.7),layout='constrained')
    ax=axes[0];x=list(range(len(rows)));w=.36
    ax.bar([i-w/2 for i in x],[r['quote_before'] for r in rows],width=w,label='Before filtering',color='#a7c9e8')
    ax.bar([i+w/2 for i in x],[r['quote_after'] for r in rows],width=w,label='After filtering',color='#235c90')
    for i,r in enumerate(rows):
        ax.text(i-w/2,r['quote_before']+.8,str(r['quote_before']),ha='center',fontsize=9)
        ax.text(i+w/2,r['quote_after']+.8,str(r['quote_after']),ha='center',fontsize=9)
    ax.set(xticks=x,xticklabels=[r['condition'] for r in rows],ylim=(0,59),ylabel='Cases with full support quote in a passage',title='Full-quote tracking across conditions')
    ax.legend(loc='upper right',fontsize=9)
    ax=axes[1];rs=rows[1:];x=list(range(len(rs)));bottom=[0]*len(rs)
    for n,color,label in [(0,'#e5b3ae','0 documents'),(1,'#a7c9e8','1 document'),(2,'#235c90','2 documents')]:
        v=[r['copy_document_exposure_histogram'].get(str(n),0) for r in rs]
        ax.bar(x,v,bottom=bottom,label=label,color=color)
        for i,y in enumerate(v):
            if y>=3:ax.text(i,bottom[i]+y/2,str(y),ha='center',va='center',color='white' if n==2 else '#172f46',fontsize=10)
        bottom=[b+y for b,y in zip(bottom,v)]
    ax.set(xticks=x,xticklabels=[r['condition'] for r in rs],ylim=(0,68),ylabel='Cases',title='Inserted copy documents actually retrieved')
    ax.legend(loc='upper center',ncol=3,fontsize=9)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.16)
    fig.suptitle('FilterFlip-RAG: saved secondary-variant comparisons\n59 selected cases per condition; quote tracking is not semantic correctness',fontsize=14)
    a.out.mkdir(parents=True)
    fig.savefig(a.out/'secondary_variants.png',dpi=180)
    fig.savefig(a.out/'secondary_variants.svg',metadata={'Date':None})
    plt.close(fig)
if __name__=='__main__':main()
