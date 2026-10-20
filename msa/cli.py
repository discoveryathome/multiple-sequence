import argparse,json
from pathlib import Path
from .core import ROOT,read_fasta,validate,score,oracle_score,accuracy,canonical_hash,digest,write_fasta
from .refine import refine


def datasets():
    return json.loads((ROOT/'data/manifest.json').read_text())['datasets']


def check_candidate(dataset,path,claimed=None):
    ds=next(d for d in datasets() if d['id']==dataset)
    rows=read_fasta(path);validate(read_fasta(ROOT/ds['input']),rows)
    value=score(rows)
    if value!=oracle_score(rows): raise ValueError('score implementation disagreement')
    if claimed is not None and value!=int(claimed): raise ValueError('claimed score is false')
    return dict(dataset=dataset,score=value,canonical_sha256=canonical_hash(rows))


def verify(dataset=None):
    import xml.etree.ElementTree as ET
    evaluation=json.loads((ROOT/'results/evaluation.json').read_text())
    records=json.loads((ROOT/'discover/records.json').read_text())
    checked=0
    for d in datasets():
        if dataset and d['id']!=dataset:continue
        for field,h in d['sha256'].items():
            if digest(ROOT/d[field])!=h:raise ValueError('dataset hash mismatch '+d['id'])
        xml=ET.parse(ROOT/d['xml'])
        original={s.findtext('seq-name').strip():''.join(s.findtext('seq-data').split()).upper()
                  for s in xml.findall('.//sequence')}
        ref=read_fasta(ROOT/d['reference']);mask=json.loads((ROOT/d['mask']).read_text())
        if original!=ref:raise ValueError('XML reference conversion mismatch')
        xmlmask=[int(x)==1 for c in xml.findall('.//column-score') if c.findtext('colsco-name')=='coreblock' for x in c.findtext('colsco-data').split()]
        if mask!=xmlmask:raise ValueError('XML core mask mismatch')
        if accuracy(ref,ref,mask)['core_pair_recall']!=1:raise ValueError('reference self-test failed')
        for r in evaluation['all_rows']:
            if r['dataset']!=d['id']:continue
            check_candidate(d['id'],ROOT/r['alignment'],r['score'])
            measured=accuracy(read_fasta(ROOT/r['alignment']),ref,mask)
            if any(r[k]!=v for k,v in measured.items()):raise ValueError('accuracy claim mismatch')
            checked+=1
        row=next(r for r in records if r['dataset']==d['id'])
        check_candidate(d['id'],ROOT/row['object'],row['value'])
        for r in json.loads((ROOT/'results/experiments/index.json').read_text()):
            if r['dataset']!=d['id']:continue
            if digest(ROOT/'experiment.json')!=r['config_sha256']:raise ValueError('configuration drift')
            current=r['baseline_score']
            for t in r['trace']:
                if t['before']!=current or t['accepted']!=(t['proposal']>current):raise ValueError('invalid acceptance trace')
                if t['accepted']:current=t['proposal']
            if current!=r['score']:raise ValueError('trace final score mismatch')
            result=check_candidate(d['id'],ROOT/'results/experiments'/r['alignment'],r['score'])
            if result['canonical_sha256']!=r['canonical_sha256']:raise ValueError('candidate hash mismatch')
    if not checked:raise ValueError('no datasets checked')
    print(json.dumps(dict(status='PASS',alignment_checks=checked,dataset=dataset or 'all',
                          coverage='Exact objective and saved accuracy; proposal replay is a separate command.')))


def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('verify');q.add_argument('--dataset')
    q=s.add_parser('check');q.add_argument('--dataset',required=True);q.add_argument('--alignment',required=True);q.add_argument('--claimed-score',type=int)
    q=s.add_parser('refine');q.add_argument('--dataset',required=True);q.add_argument('--alignment',required=True);q.add_argument('--out',required=True);q.add_argument('--seed',type=int,default=0);q.add_argument('--rounds',type=int,default=3);q.add_argument('--operation',choices=['block','subgroup','gap','profile'])
    q=s.add_parser('datasets')
    a=p.parse_args()
    if a.cmd=='verify':verify(a.dataset)
    elif a.cmd=='check':print(json.dumps(check_candidate(a.dataset,a.alignment,a.claimed_score)))
    elif a.cmd=='datasets':print(json.dumps(datasets(),indent=2))
    elif a.cmd=='refine':
        d=next(d for d in datasets() if d['id']==a.dataset)
        ops=(a.operation,) if a.operation else ('block','subgroup','gap','profile')
        rows,trace=refine(read_fasta(ROOT/d['input']),read_fasta(a.alignment),a.seed,a.rounds,ops)
        write_fasta(a.out,rows);Path(a.out+'.json').write_text(json.dumps(dict(score=score(rows),trace=trace),indent=2)+'\n')
        print(json.dumps(check_candidate(a.dataset,a.out)))
if __name__=='__main__':main()
