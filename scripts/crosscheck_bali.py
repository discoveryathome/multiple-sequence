#!/usr/bin/env python3
"""Independent BAliBASE 3.01 check. Legacy SP assumes gap-free core columns.
Legacy TC truncates to integer percent and is retained as a diagnostic only.
"""
import sys,json,subprocess,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from msa.core import *
ROOT=Path(__file__).resolve().parents[1]

def msf(rows,path):
    length=len(next(iter(rows.values())))
    text=f'PileUp\n\n MSF: {length} Type: P Check: 0 ..\n\n'
    for k,s in rows.items():text+=f' Name: {k} Len: {length} Check: 0 Weight: 1.0\n'
    text+='\n//\n\n'
    for i in range(0,length,50):
        for k,s in rows.items():text+=k+' '+s[i:i+50].replace('-','.')+'\n'
        text+='\n'
    path.write_text(text)

def main(binary,out):
    binary=str(Path(binary).resolve());out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    results=[]
    variants=json.loads((ROOT/'results/evaluation.json').read_text())['all_rows']
    for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']:
        ref=read_fasta(ROOT/d['reference']);mask=json.loads((ROOT/d['mask']).read_text())
        gapfree=all('-' not in c for c,on in zip(zip(*ref.values()),mask) if on)
        for r in [dict(dataset=d['id'],method='reference-self',alignment=d['reference'])]+[r for r in variants if r['dataset']==d['id']]:
            label=d['id']+'.'+r['method']+'.'+str(r.get('seed','na'))
            rows=read_fasta(ROOT/r['alignment']);path=out/(label+'.msf');msf(rows,path)
            run=subprocess.run([binary,str(ROOT/d['xml']),str(path)],capture_output=True,text=True,check=True,timeout=30)
            (out/(label+'.log')).write_text(run.stdout+run.stderr)
            sp=float(re.search(r'SP score=\s*([0-9.]+)',run.stdout).group(1))
            tc=float(re.search(r'TC score=\s*([0-9.]+)',run.stdout).group(1))
            ours=accuracy(rows,ref,mask)
            if not gapfree:raise ValueError('Legacy denominator differs on gapped core columns: '+d['id'])
            if abs(sp-ours['core_pair_recall'])>0.000501:raise ValueError('SP evaluator mismatch: '+label)
            results.append(dict(dataset=d['id'],method=r['method'],seed=r.get('seed'),
                                legacy_sp_rounded=sp,our_pair_recall=ours['core_pair_recall'],legacy_tc_truncated=tc,
                                our_strict_tc=ours['core_column_recall'],alignment=r['alignment']))
            path.unlink()
    (out/'crosscheck.json').write_text(json.dumps(dict(status='PASS',checks=len(results),
        evaluator='BAliBASE bali_score 3.01 (Jan 2008), source from pinned original archive',results=results),indent=2)+'\n')
    print('PASS',len(results),'independent BAliBASE SP checks')
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
