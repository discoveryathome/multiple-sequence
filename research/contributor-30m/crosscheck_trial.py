import json,subprocess,sys,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from msa.core import *
from crosscheck_bali import msf
binary=str(Path(sys.argv[1]).resolve());out=HERE/'bali-crosscheck';out.mkdir(exist_ok=True)
base={d['id']:d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']};jobs=[]
for p in (HERE/'outputs').glob('*/result.json'):
 r=json.loads(p.read_text());d=base[r['dataset']]
 for arm in ['row_dp','control']:jobs.append((r['dataset']+'.'+arm,ROOT/d['xml'],ROOT/d['reference'],ROOT/d['mask'],p.parent/r[arm]['alignment']))
for p in (HERE/'additional').glob('*/result.json'):
 jobs.append((p.parent.name+'.row_dp',p.parent/'reference.xml',p.parent/'reference.fa',p.parent/'core.json',p.parent/'row-final.fa'))
for p in (HERE/'convergence').glob('*/result.json'):
 case=p.parent.name
 if case in base:
  d=base[case];xml,ref,mask=ROOT/d['xml'],ROOT/d['reference'],ROOT/d['mask']
 else:
  folder=HERE/'additional'/case;xml,ref,mask=folder/'reference.xml',folder/'reference.fa',folder/'core.json'
 jobs.append((case+'.converged',xml,ref,mask,p.parent/'final.fa'))
results=[]
for label,xml,ref,mask,path in sorted(jobs):
 reference=read_fasta(ref);core=json.loads(mask.read_text());rows=read_fasta(path);ours=accuracy(rows,reference,core)
 gapfree=all('-' not in c for c,on in zip(zip(*reference.values()),core) if on)
 if not gapfree:raise ValueError('legacy evaluator cannot match gapped core denominator: '+label)
 tmp=out/(label+'.msf');msf(rows,tmp)
 run=subprocess.run([binary,str(xml),str(tmp)],capture_output=True,text=True,check=True,timeout=30)
 (out/(label+'.log')).write_text(run.stdout+run.stderr);tmp.unlink()
 observed=float(re.search(r'SP score=\s*([0-9.]+)',run.stdout).group(1))
 if abs(observed-ours['core_pair_recall'])>0.000501:raise ValueError('independent SP mismatch')
 results.append(dict(label=label,our_accuracy=ours,legacy_sp=observed,alignment=str(path.relative_to(ROOT))))
(out/'crosscheck.json').write_text(json.dumps(dict(status='PASS',checks=len(results),results=results),indent=2)+'\n')
print('TRIAL BALI CROSSCHECK PASS',len(results))
