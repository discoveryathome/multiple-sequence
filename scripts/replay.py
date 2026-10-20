#!/usr/bin/env python3
"""Replay every seeded proposal and compare trace and final alignment hashes."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import ROOT,read_fasta,canonical_hash,score
from msa.refine import refine

def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset');a=p.parse_args()
    ds={d['id']:d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']}
    checked=0
    records=json.loads((ROOT/'results/experiments/index.json').read_text())
    records += [dict(r,baseline_path=r['initial'],operations=['block','subgroup','gap','profile']) for r in json.loads((ROOT/'results/extended/index.json').read_text())]
    for r in records:
        if a.dataset and r['dataset']!=a.dataset:continue
        inputs=read_fasta(ROOT/ds[r['dataset']]['input']);initial=read_fasta(ROOT/r['baseline_path'])
        rows,trace=refine(inputs,initial,r['seed'],r['rounds'],r['operations'])
        if trace!=r['trace'] or canonical_hash(rows)!=r['canonical_sha256'] or score(rows)!=r['score']:
            raise ValueError('replay differs: '+r['alignment'])
        checked+=1
        print('PASS',r['alignment'],flush=True)
    if not checked:raise ValueError('no cases')
    print('REPLAY PASS',checked)
if __name__=='__main__':main()
