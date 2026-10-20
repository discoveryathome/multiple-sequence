#!/usr/bin/env python3
"""Generate candidates without importing or opening biological references."""
import argparse,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import read_fasta,write_fasta,score,canonical_hash,digest
from msa.refine import refine
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/experiments');p.add_argument('--dataset');p.add_argument('--quick',action='store_true');a=p.parse_args()
    out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
    config=json.loads((ROOT/'experiment.json').read_text())
    datasets=json.loads((ROOT/'data/manifest.json').read_text())['datasets']
    records=[]
    for d in datasets:
        if a.dataset and d['id']!=a.dataset: continue
        inputs=read_fasta(ROOT/d['input'])
        initial_options=[]
        for method in config['baselines']:
            path=f'results/baselines/{d["id"]}.{method}.fa'
            rows=read_fasta(ROOT/path);initial_options.append((score(rows),method,path,rows))
        # Fixed tie break: method name ascending. No reference accuracy selection.
        value,method,path,initial=sorted(initial_options,key=lambda x:(-x[0],x[1]))[0]
        settings=[('combined',seed,config['rounds'],config['operations']) for seed in config['seeds']]
        settings += [(op,config['seeds'][0],config['rounds']*len(config['operations']),[op]) for op in config['operations']]
        if a.quick: settings=settings[:1]
        for mode,seed,rounds,operations in settings:
            name=f'{d["id"]}.{mode}.s{seed}'
            start=time.monotonic();rows,trace=refine(inputs,initial,seed,rounds,operations)
            elapsed=time.monotonic()-start
            write_fasta(out/(name+'.fa'),rows)
            record=dict(dataset=d['id'],mode=mode,seed=seed,rounds=rounds,operations=operations,
                        baseline=method,baseline_path=path,baseline_hash=canonical_hash(initial),baseline_score=value,
                        score=score(rows),alignment=name+'.fa',canonical_sha256=canonical_hash(rows),
                        input_sha256=digest(ROOT/d['input']),trace=trace,seconds=elapsed,
                        config_sha256=digest(ROOT/'experiment.json'))
            (out/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n');records.append(record)
            print(name,value,record['score'],round(elapsed,2),flush=True)
    (out/'index.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
