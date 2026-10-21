"""Checked inherited starts and separate post-generation biological diagnostics."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from msa.core import read_fasta,validate,score,oracle_score,accuracy,digest,canonical_hash
OUT=ROOT/'research/readiness-20261021'

def checked(path,inputs):
    rows=read_fasta(path);validate(read_fasta(inputs),rows)
    a,b=score(rows),oracle_score(rows)
    if a!=b:raise ValueError('Scorers disagree')
    return rows,a

def bound_case(name,biological=False):
    p=json.loads((OUT/('portfolio.json' if biological else 'starts.json')).read_text())
    for file,sha in p['shared_bindings'].items():
        if digest(ROOT/file)!=sha:raise ValueError('Model/checker binding changed: '+file)
    matches=[r for r in p['cases'] if r['dataset']==name]
    if len(matches)!=1:raise ValueError('Unknown preparation case')
    c=matches[0]
    # Generation/checking requires no biological-reference reads.
    for key in ('input','incumbent'):
        if digest(ROOT/c[key])!=c['sha256'][key]:raise ValueError('Case binding changed')
    return c

def check_candidate(name,path,claimed=None,biological=False):
    start=time.perf_counter();c=bound_case(name,biological);rows,value=checked(path,ROOT/c['input'])
    if claimed is not None and value!=claimed:raise ValueError('Claimed score mismatch')
    _,inherited=checked(ROOT/c['incumbent'],ROOT/c['input'])
    if inherited!=c['score']:raise ValueError('Inherited score mismatch')
    result=dict(dataset=name,valid=True,score=value,delta_from_inherited=value-inherited,
      optimization_improvement=value>inherited,canonical_sha256=canonical_hash(rows),
      interpretation='Feasible optimization artifact; no biological improvement or acceptance follows.',
      seconds=time.perf_counter()-start)
    if biological:
        for key in ('reference','mask'):
            if digest(ROOT/c[key])!=c['sha256'][key]:raise ValueError('Reference binding changed')
        for baseline in c['baselines']:
            if digest(ROOT/baseline['object'])!=baseline['sha256']:raise ValueError('Baseline binding changed')
        ref=read_fasta(ROOT/c['reference']);mask=json.loads((ROOT/c['mask']).read_text())
        a=accuracy(rows,ref,mask);result['reference_metrics']=a
        result['pair_recall_delta_from_inherited']=a['core_pair_recall']-c['reference_metrics']['core_pair_recall']
        result['pair_recall_delta_from_best_baseline']=a['core_pair_recall']-max(b['reference_metrics']['core_pair_recall'] for b in c['baselines'])
        result['interpretation']='Post-generation diagnostic on exposed development references; no fresh confirmation or biological acceptance.'
    return result

def prepare():
    original={d['id']:d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']}
    trial=ROOT/'research/contributor-30m';cases=[]
    for r in json.loads((trial/'candidate-records.json').read_text()):
        name=r['dataset'];extra=trial/'additional'/name
        if name in original:
            d=original[name];paths={k:d[k] for k in ('input','reference','mask')}
            bs=sorted((ROOT/'results/baselines').glob(name+'.*.fa'))
        else:
            paths={k:str((extra/f).relative_to(ROOT)) for k,f in [('input','input.fa'),('reference','reference.fa'),('mask','core.json')]}
            bs=[extra/(m+'.fa') for m in ('mafft-linsi','mafft-ginsi','famsa2')]
        paths['incumbent']=r['object'];rows,value=checked(ROOT/r['object'],ROOT/paths['input'])
        if value!=r['value'] or canonical_hash(rows)!=r['canonical_sha256']:raise ValueError('Historical candidate mismatch')
        ref=read_fasta(ROOT/paths['reference']);mask=json.loads((ROOT/paths['mask']).read_text());baselines=[]
        if len(bs)!=3:raise ValueError('Expected three strong baselines')
        for file in bs:
            brow,bscore=checked(file,ROOT/paths['input']);baselines.append(dict(object=str(file.relative_to(ROOT)),sha256=digest(file),score=bscore,reference_metrics=accuracy(brow,ref,mask)))
        c=dict(dataset=name,**paths,sha256={k:digest(ROOT/f) for k,f in paths.items()},score=value,
          n=len(rows),max_ungapped_length=max(len(s.replace('-','')) for s in rows.values()),
          reference_metrics=accuracy(rows,ref,mask),baselines=baselines,
          single_row_saturated='coordinate optimum' in r['kind'],
          role='scaling-only' if name=='BB20036' else 'exposed-development',
          status='Inherited author-checked candidate; scientific review pending')
        cases.append(c)
    package=dict(version='msa-preparation-v1',model='MSA-SP-v1 unchanged',
      shared_bindings={f:digest(ROOT/f) for f in ('msa/core.py','data/matrices/BLOSUM62','docs/MODEL.md')},
      cases=cases,policy='Search uses sequences and integer objective only. Reference diagnostics run after outputs are frozen. No reference-guided acceptance in the original model.')
    (OUT/'portfolio.json').write_text(json.dumps(package,indent=2)+'\n')
    starts=dict(version=package['version'],model=package['model'],shared_bindings=package['shared_bindings'],cases=[])
    for c in cases:
        starts['cases'].append({**{k:c[k] for k in ('dataset','input','incumbent','score','n','max_ungapped_length','single_row_saturated','role','status')},'sha256':{k:c['sha256'][k] for k in ('input','incumbent')}})
    (OUT/'starts.json').write_text(json.dumps(starts,indent=2)+'\n')
    print('PASS',len(cases),'inherited starts and',sum(len(c['baselines']) for c in cases),'baseline outputs')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','check','evaluate']);p.add_argument('--dataset');p.add_argument('--candidate');p.add_argument('--claimed-score',type=int);a=p.parse_args()
    if a.action=='prepare':prepare();return
    if not a.dataset:p.error('--dataset is required')
    path=Path(a.candidate) if a.candidate else ROOT/bound_case(a.dataset)['incumbent']
    print(json.dumps(check_candidate(a.dataset,path,a.claimed_score,a.action=='evaluate'),indent=2))
if __name__=='__main__':main()
