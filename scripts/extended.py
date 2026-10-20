#!/usr/bin/env python3
"""A pre-specified longer-run check on three sizes, still reference blind."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import *
from msa.refine import refine
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'results/extended';out.mkdir(parents=True,exist_ok=True)
records=[]
for dataset in ['BB11001','BB20029','BB50013']:
    d=next(d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets'] if d['id']==dataset)
    candidates=[r for r in json.loads((ROOT/'results/experiments/index.json').read_text()) if r['dataset']==dataset and r['mode']=='combined']
    best=sorted(candidates,key=lambda r:(-r['score'],r['seed']))[0]
    initial=read_fasta(ROOT/'results/experiments'/best['alignment'])
    start=time.monotonic();rows,trace=refine(read_fasta(ROOT/d['input']),initial,101,12)
    write_fasta(out/(dataset+'.fa'),rows)
    records.append(dict(dataset=dataset,seed=101,rounds=12,initial='results/experiments/'+best['alignment'],initial_score=best['score'],score=score(rows),trace=trace,seconds=time.monotonic()-start,alignment='results/extended/'+dataset+'.fa',canonical_sha256=canonical_hash(rows)))
    print(dataset,best['score'],score(rows),flush=True)
(out/'index.json').write_text(json.dumps(records,indent=2)+'\n')
