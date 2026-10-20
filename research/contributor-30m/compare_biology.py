"""Post-generation comparisons to all strong baselines; never used by search."""
import json,sys,math,statistics
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R))
from msa.core import *
base={d['id']:d for d in json.loads((R/'data/manifest.json').read_text())['datasets']}
e=json.loads((H/'evaluation.json').read_text());out=[]
for r in e['records']:
 case=r['dataset'];extra=H/'additional'/case
 if case in base:
  d=base[case];ref=read_fasta(R/d['reference']);mask=json.loads((R/d['mask']).read_text());paths=list((R/'results/baselines').glob(case+'.*.fa'))
 else:
  ref=read_fasta(extra/'reference.fa');mask=json.loads((extra/'core.json').read_text());paths=[extra/(s+'.fa') for s in ['mafft-linsi','mafft-ginsi','famsa2']]
 bs=[dict(path=str(p.relative_to(R)),score=score(read_fasta(p)),**accuracy(read_fasta(p),ref,mask)) for p in paths]
 if len(bs)!=3:raise ValueError((case,len(bs),paths))
 b=max(bs,key=lambda b:b['core_pair_recall']);a=r['arms']['row_dp']['accuracy'];rec=dict(dataset=case,baselines=bs,best_baseline_pair_recall=b['core_pair_recall'],best_baseline_path=b['path'],dp_pair_recall=a['core_pair_recall'],delta_vs_best_accuracy_baseline=a['core_pair_recall']-b['core_pair_recall'])
 conv=H/'convergence'/case/'final.fa'
 if conv.exists():rec['converged']=dict(score=score(read_fasta(conv)),**accuracy(read_fasta(conv),ref,mask))
 out.append(rec)
 print(case,'DP',round(100*a['core_pair_recall'],3),'best baseline',round(100*b['core_pair_recall'],3),'delta pp',round(100*rec['delta_vs_best_accuracy_baseline'],3))
full=[r for r in e['records'] if r['cohort']!='scaling-probe'];x=[r['arms']['row_dp']['gain']/(r['n']*(r['n']-1)/2) for r in full];y=[r['arms']['row_dp']['accuracy']['core_pair_recall']-r['initial_accuracy']['core_pair_recall'] for r in full]
def corr(x,y):
 mx=sum(x)/len(x);my=sum(y)/len(y);return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
def ranks(v):return [1+sum(a<b for a in v)+(sum(a==b for a in v)-1)/2 for b in v]
summary=dict(full_cases=len(full),score_improved=sum(v>0 for v in x),accuracy_improved=sum(v>0 for v in y),accuracy_worse=sum(v<0 for v in y),accuracy_equal=sum(v==0 for v in y),pearson_per_pair_gain_vs_recall_delta=corr(x,y),spearman=corr(ranks(x),ranks(y)),mean_recall_delta=sum(y)/len(y),median_recall_delta=statistics.median(y),note='Descriptive selected small sample; no significance or generalization claim. Excludes three-row scaling probe.')
(H/'biology-comparison.json').write_text(json.dumps(dict(summary=summary,records=out),indent=2)+'\n');print(summary)
