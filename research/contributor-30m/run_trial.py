"""Run exact row-coordinate ascent and seeded baseline-search controls."""
import sys,json,time,argparse,datetime,hashlib,resource,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from row_dp import optimize_row
from msa.core import read_fasta,write_fasta,score,pair_score,matrix,canonical_hash,digest
from msa.refine import refine

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def order_rows(rows):
    sub,op,ext=matrix()
    return sorted(rows,key=lambda k:(sum(pair_score(rows[k],rows[j],sub,op,ext) for j in rows if j!=k)/len(rows[k].replace('-','')),k))

def run(dataset,passes,control_seconds):
    record=next(r for r in json.loads((ROOT/'discover/records.json').read_text()) if r['dataset']==dataset)
    d=next(d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets'] if d['id']==dataset)
    initial=read_fasta(ROOT/record['object']);inputs=read_fasta(ROOT/d['input'])
    out=HERE/'outputs'/dataset;out.mkdir(parents=True,exist_ok=True)
    rows=dict(initial);value=score(rows);begin=time.monotonic();startstamp=now();trace=[]
    sourcehash=digest(HERE/'row_dp.py')
    for sweep in range(passes):
        changes=0
        for key in order_rows(rows):
            start=time.monotonic()
            proposal,stats=optimize_row(rows,key)
            accepted=stats['total_score']>value
            entry=dict(sweep=sweep,row=key,before=value,after=stats['total_score'],accepted=accepted,
                       elapsed=time.monotonic()-begin,step_seconds=time.monotonic()-start,**stats)
            if accepted:
                changes+=1;rows=proposal;value=stats['total_score']
                artifact=f'row-{len(trace):04d}.fa';write_fasta(out/artifact,rows)
                entry.update(artifact=artifact,canonical_sha256=canonical_hash(rows),observed_at=now())
                print(dataset,'DP',sweep,key,value,round(entry['elapsed'],2),flush=True)
            trace.append(entry)
        if not changes:break
    dp_seconds=time.monotonic()-begin
    write_fasta(out/'row-final.fa',rows)
    # Separate control starts at the SAME incumbent. Its fixed existing algorithm
    # continues across seeds; no deliberate weak initial alignment.
    control=dict(initial);cv=score(control);ctrace=[];cstart=time.monotonic();seed=1000
    budget=control_seconds if control_seconds else dp_seconds
    while time.monotonic()-cstart<budget:
        candidate,t=refine(inputs,control,seed,1)
        new=score(candidate);accepted=new>cv
        entry=dict(seed=seed,before=cv,after=new,accepted=accepted,elapsed=time.monotonic()-cstart,trace=t)
        if accepted:
            control,cv=candidate,new
            artifact=f'control-{seed}.fa';write_fasta(out/artifact,control)
            entry.update(artifact=artifact,canonical_sha256=canonical_hash(control))
            print(dataset,'CONTROL',seed,cv,round(entry['elapsed'],2),flush=True)
        ctrace.append(entry);seed+=1
    write_fasta(out/'control-final.fa',control)
    usage=resource.getrusage(resource.RUSAGE_SELF)
    result=dict(peak_rss_native=usage.ru_maxrss,peak_rss_unit='bytes' if platform.system()=='Darwin' else 'KiB',cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,dataset=dataset,started_at=startstamp,finished_at=now(),source_sha256=sourcehash,initial_path=record['object'],initial_score=score(initial),initial_hash=canonical_hash(initial),passes=passes,
                row_dp=dict(score=value,seconds=dp_seconds,alignment='row-final.fa',canonical_sha256=canonical_hash(rows),trace=trace),
                control=dict(score=cv,seconds=time.monotonic()-cstart,budget_seconds=budget,alignment='control-final.fa',canonical_sha256=canonical_hash(control),trace=ctrace),
                caveat='One process per arm, DP first then control; time budget rounded by complete control batches. Not a controlled speed benchmark.')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('DONE',dataset,result['initial_score'],value,cv,round(dp_seconds,2),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset');p.add_argument('--passes',type=int,default=2);p.add_argument('--control-seconds',type=float,default=0);a=p.parse_args()
    cases=[a.dataset] if a.dataset else [r['dataset'] for r in json.loads((ROOT/'discover/records.json').read_text())]
    results=[run(case,a.passes,a.control_seconds) for case in cases]
    (HERE/'outputs').mkdir(exist_ok=True)
    (HERE/'outputs'/('index-'+(a.dataset or 'all')+'.json')).write_text(json.dumps(results,indent=2)+'\n')
