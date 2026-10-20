#!/usr/bin/env python3
"""Offline entry-point verification, standard-library only."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import ROOT,digest,read_fasta,canonical_hash
from msa.cli import verify

def main():
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,check=True)
    for p,h in json.loads((ROOT/'results/generation-source.json').read_text()).items():
        if digest(ROOT/p)!=h:raise ValueError('generation source drift: '+p)
    for provenance in ['provenance.json','famsa-provenance.json']:
        for r in json.loads((ROOT/'results/baselines'/provenance).read_text())['records']:
            actual=canonical_hash(read_fasta(ROOT/'results/baselines'/r['alignment']))
            if r['repeat_hashes']!=[actual,actual] or actual!=r['canonical_sha256']:
                raise ValueError('baseline hashes disagree')
    for r in json.loads((ROOT/'results/experiments/index.json').read_text()):
        separate=json.loads((ROOT/'results/experiments'/Path(r['alignment']).with_suffix('.json')).read_text())
        if r!=separate:raise ValueError('index/sidecar mismatch')
        if canonical_hash(read_fasta(ROOT/r['baseline_path']))!=r['baseline_hash']:raise ValueError('initial alignment drift')
    verify()
    subprocess.run([sys.executable,'scripts/evaluate.py','--check'],cwd=ROOT,check=True)
    x=json.loads((ROOT/'results/bali-crosscheck/crosscheck.json').read_text())
    if x['status']!='PASS' or x['checks']!=len(x['results']):raise ValueError('independent evaluator record malformed')
    expected=json.loads((ROOT/'results/evaluation.json').read_text())['all_rows']
    for r in x['results']:
        if abs(r['legacy_sp_rounded']-r['our_pair_recall'])>0.000501:raise ValueError('legacy evaluator disagreement')
        if r['method']!='reference-self':
            row=next(y for y in expected if (y['dataset'],y['method'],y.get('seed'))==(r['dataset'],r['method'],r.get('seed')))
            if row['core_pair_recall']!=r['our_pair_recall']:raise ValueError('legacy comparison stale')
    print('OFFLINE VERIFY PASS; external baseline/evaluator execution and full proposal replay are separate checks.')
if __name__=='__main__':main()
