#!/usr/bin/env python3
"""Post-hoc reference evaluation; never used by the optimizer."""
import sys,json,math,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import *
ROOT=Path(__file__).resolve().parents[1]

def corr(x,y):
    if len(x)<3 or len(set(x))<2 or len(set(y))<2:return None
    mx,my=statistics.mean(x),statistics.mean(y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))

def ranks(xs):
    ordered=sorted(xs)
    return [sum(i+1 for i,y in enumerate(ordered) if y==x)/ordered.count(x) for x in xs]

def main():
    manifest=json.loads((ROOT/'data/manifest.json').read_text())
    experiments=json.loads((ROOT/'results/experiments/index.json').read_text())
    extended=json.loads((ROOT/'results/extended/index.json').read_text()) if (ROOT/'results/extended/index.json').exists() else []
    rows=[];frontier=[];primary=[]
    for d in manifest['datasets']:
        ref=read_fasta(ROOT/d['reference']);core=json.loads((ROOT/d['mask']).read_text())
        variants=[]
        for method in ['mafft-linsi','mafft-ginsi','famsa2']:
            variants.append(dict(method=method,alignment=f'results/baselines/{d["id"]}.{method}.fa'))
        for r in experiments:
            if r['dataset']==d['id']:
                variants.append(dict(method=r['mode'],seed=r['seed'],baseline=r['baseline'],
                                     alignment='results/experiments/'+r['alignment']))
        for r in extended:
            if r['dataset']==d['id']:
                variants.append(dict(method='extended',seed=r['seed'],alignment=r['alignment']))
        evaluated=[]
        for v in variants:
            aln=read_fasta(ROOT/v['alignment'])
            row=dict(dataset=d['id'],split=d['split'],n=d['n'],**v,score=score(aln),**accuracy(aln,ref,core))
            rows.append(row);evaluated.append(row)
        baselines=[r for r in evaluated if r['method'] in ('mafft-linsi','mafft-ginsi','famsa2')]
        base=sorted(baselines,key=lambda r:(-r['score'],r['method']))[0]
        candidates=[r for r in evaluated if r['method']=='combined']
        best=sorted(candidates,key=lambda r:(-r['score'],r['seed']))[0]
        primary.append(dict(dataset=d['id'],split=d['split'],baseline=base['method'],baseline_score=base['score'],
                            score=best['score'],score_delta=best['score']-base['score'],
                            score_delta_per_pair=(best['score']-base['score'])/(d['n']*(d['n']-1)/2),
                            baseline_accuracy=base['core_pair_recall'],accuracy=best['core_pair_recall'],
                            accuracy_delta=best['core_pair_recall']-base['core_pair_recall'],
                            baseline_tc=base['core_column_recall'],tc=best['core_column_recall']))
        record=sorted([r for r in evaluated if r['method'] not in ('mafft-linsi','mafft-ginsi','famsa2')],key=lambda r:(-r['score'],r['method'],r['seed']))[0]
        record_source='results/extended/index.json' if record['method']=='extended' else 'results/experiments/'+Path(record['alignment']).stem+'.json'
        frontier.append(dict(dataset=d['id'],value=str(record['score']),object=record['alignment'],
                             by='Local pilot automation (unreviewed)',source=record_source,
                             updated='2026-10-20',baseline=base['method'],baseline_score=str(base['score']),
                             core_pair_recall=record['core_pair_recall']))
    deltas=[r['score_delta_per_pair'] for r in primary];acc=[r['accuracy_delta'] for r in primary]
    changed=[r for r in primary if r['score_delta']>0]
    stats=dict(families=len(primary),improved_score=len(changed),accuracy_increased=sum(r['accuracy_delta']>0 for r in changed),
               accuracy_decreased=sum(r['accuracy_delta']<0 for r in changed),accuracy_unchanged=sum(r['accuracy_delta']==0 for r in changed),
               mean_accuracy_delta=statistics.mean(acc),pearson_delta_per_pair_vs_accuracy_delta=corr(deltas,acc),
               spearman_delta_per_pair_vs_accuracy_delta=corr(ranks(deltas),ranks(acc)),
               correlation_unit='One score-selected combined candidate per family (8 units); exploratory, correlated homologous families and no significance claim.')
    report=dict(primary=primary,summary=stats,all_rows=rows)
    if '--check' in sys.argv:
        if json.loads((ROOT/'results/evaluation.json').read_text())!=report:raise ValueError('evaluation summary mismatch')
        if json.loads((ROOT/'discover/records.json').read_text())!=frontier:raise ValueError('frontier table mismatch')
        print('EVALUATION RECOMPUTATION PASS')
        return
    (ROOT/'results/evaluation.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'discover/records.json').write_text(json.dumps(frontier,indent=2)+'\n')
    print(json.dumps(stats,indent=2));print(json.dumps(primary,indent=2))
if __name__=='__main__':main()
