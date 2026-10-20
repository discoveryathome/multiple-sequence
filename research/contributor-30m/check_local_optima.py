import sys,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from row_dp import optimize_row
from msa.core import *
results=[]
for p in sorted((HERE/'convergence').glob('*/result.json')):
 r=json.loads(p.read_text())
 if not r['local_optimum']:continue
 rows=read_fasta(p.parent/'final.fa');value=score(rows);start=time.monotonic();checks=[]
 for key in sorted(rows):
  candidate,stats=optimize_row(rows,key)
  if stats['total_score']!=value:raise ValueError('not a row-coordinate optimum')
  checks.append(dict(row=key,optimum=stats['total_score'],states=stats['states']))
 results.append(dict(dataset=r['dataset'],score=value,checks=checks,seconds=time.monotonic()-start,hash=canonical_hash(rows)))
 print('LOCAL OPTIMUM VERIFIED',r['dataset'],value,len(checks),flush=True)
(HERE/'local-optima-verification.json').write_text(json.dumps(results,indent=2)+'\n')
