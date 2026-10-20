"""Measure remaining hill-climbing yield after the initial exact-row sweep(s)."""
import argparse,json,sys,time,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from row_dp import optimize_row
from run_trial import order_rows
from msa.core import *
p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--start',required=True);p.add_argument('--passes',type=int,default=5);a=p.parse_args()
start_path=ROOT/a.start;rows=read_fasta(start_path);initial=score(rows);out=HERE/'convergence'/a.dataset;out.mkdir(parents=True,exist_ok=True)
trace=[];begin=time.monotonic();sweeps=[]
for sweep in range(a.passes):
 before=score(rows);accepted=0
 for key in order_rows(rows):
  proposal,stats=optimize_row(rows,key);value=stats['total_score'];old=score(rows)
  entry=dict(sweep=sweep,row=key,before=old,after=value,accepted=value>old,elapsed=time.monotonic()-begin,**stats)
  if value>old:
   accepted+=1;rows=proposal;filename=f'row-{len(trace):04d}.fa';write_fasta(out/filename,rows);entry['artifact']=filename
   print(a.dataset,sweep,key,old,value,round(entry['elapsed'],2),flush=True)
  trace.append(entry)
 sweeps.append(dict(sweep=sweep,before=before,after=score(rows),accepted=accepted,elapsed=time.monotonic()-begin))
 result=dict(dataset=a.dataset,start_path=a.start,start_score=initial,score=score(rows),source_sha256=digest(HERE/'row_dp.py'),sweeps=sweeps,trace=trace,local_optimum=not accepted,seconds=time.monotonic()-begin,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 write_fasta(out/'final.fa',rows);result['final_hash']=canonical_hash(rows);(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
 if not accepted:break
print('CONVERGENCE',a.dataset,initial,score(rows),'local optimum',not accepted,flush=True)
