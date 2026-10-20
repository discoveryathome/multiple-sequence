import argparse,json,time,sys,subprocess,datetime,resource,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from msa.core import *
from msa.refine import refine
from row_dp import optimize_row
from run_trial import order_rows
p=argparse.ArgumentParser();p.add_argument('--mafft',required=True);p.add_argument('--famsa',required=True);p.add_argument('--dataset');a=p.parse_args()
for d in json.loads((HERE/'additional/manifest.json').read_text())['records']:
 if a.dataset and a.dataset!=d['id']:continue
 folder=HERE/'additional'/d['id'];inp=folder/'input.fa';inputs=read_fasta(inp);bs=[];started=time.monotonic()
 for method,flag in [('mafft-linsi','--localpair'),('mafft-ginsi','--globalpair'),('famsa2',None)]:
  hashes=[];dur=[]
  for repeat in range(2):
   out=folder/f'{method}.repeat.fa';t=time.monotonic()
   if method=='famsa2':
    cmd=[a.famsa,'-t','1',str(inp),str(out)];run=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=180)
   else:
    cmd=[a.mafft,'--thread','1','--amino',flag,'--maxiterate','1000','--inputorder',str(inp)];run=subprocess.run(cmd,capture_output=True,text=True,check=True,timeout=180);out.write_text(run.stdout)
   dur.append(time.monotonic()-t);rows=read_fasta(out);validate(inputs,rows);hashes.append(canonical_hash(rows))
   if repeat==0:write_fasta(folder/(method+'.fa'),rows)
   (folder/(method+'.'+str(repeat)+'.log')).write_text(run.stderr)
   out.unlink()
  assert hashes[0]==hashes[1]
  bs.append(dict(method=method,score=score(rows),hash=hashes[0],repeat_hashes=hashes,seconds=dur,argv=cmd))
 base=sorted(bs,key=lambda x:(-x['score'],x['method']))[0]
 initial=read_fasta(folder/(base['method']+'.fa'))
 legacy=[]
 for seed in range(3):
  rows,tr=refine(inputs,initial,seed,3);write_fasta(folder/f'legacy.s{seed}.fa',rows);legacy.append(dict(seed=seed,score=score(rows),trace=tr,hash=canonical_hash(rows)))
 best=sorted(legacy,key=lambda x:(-x['score'],x['seed']))[0];rows=read_fasta(folder/f'legacy.s{best["seed"]}.fa');start_score=score(rows);trace=[];begin=time.monotonic()
 keys=order_rows(rows)
 if d['role']=='scaling-probe':keys=keys[:3]
 for k in keys:
  t=time.monotonic()
  try:proposal,stats=optimize_row(rows,k)
  except RuntimeError as exc:
   trace.append(dict(row=k,error=str(exc),elapsed=time.monotonic()-begin));continue
  entry=dict(row=k,before=score(rows),after=stats['total_score'],seconds=time.monotonic()-t,elapsed=time.monotonic()-begin,**stats)
  entry['accepted']=entry['after']>entry['before']
  if entry['accepted']:
   rows=proposal;file=f'row-{len(trace):04d}.fa';write_fasta(folder/file,rows);entry['artifact']=file
   print(d['id'],k,entry['after'],round(entry['elapsed'],2),flush=True)
  trace.append(entry)
 write_fasta(folder/'row-final.fa',rows)
 usage=resource.getrusage(resource.RUSAGE_SELF)
 result=dict(dataset=d['id'],role=d['role'],baselines=bs,legacy=legacy,starting_seed=best['seed'],start_score=start_score,final_score=score(rows),trace=trace,dp_seconds=time.monotonic()-begin,total_seconds=time.monotonic()-started,final_hash=canonical_hash(rows),finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),peak_rss_native=usage.ru_maxrss,peak_rss_unit='bytes' if platform.system()=='Darwin' else 'KiB',source_sha256=digest(HERE/'row_dp.py'))
 (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('DONE',d['id'],start_score,result['final_score'],flush=True)
