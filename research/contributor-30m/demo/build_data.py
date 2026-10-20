import sys,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'repo';sys.path.insert(0,str(BASE))
from msa.core import read_fasta,score,accuracy,positions
H=BASE/'research/contributor-30m';out=[]
for case,group,label in [('BB11029','additional','Reference accuracy improves'),('BB11015','outputs','Reference accuracy declines')]:
 folder=H/group/case;r=json.loads((folder/'result.json').read_text())
 if group=='additional':
  reference=read_fasta(folder/'reference.fa');core=json.loads((folder/'core.json').read_text());initial=folder/f'legacy.s{r["starting_seed"]}.fa';trace=r['trace']
 else:
  d=next(d for d in json.loads((BASE/'data/manifest.json').read_text())['datasets'] if d['id']==case)
  reference=read_fasta(BASE/d['reference']);core=json.loads((BASE/d['mask']).read_text());initial=BASE/r['initial_path'];trace=r['row_dp']['trace']
 ids=sorted(reference);refcols=positions(reference);mapping={k:{} for k in ids}
 for ci,col in enumerate(refcols):
  if not core[ci]:continue
  for k,p in zip(ids,col):
   if p is not None:mapping[k][p]=ci
 paths=[initial]+[folder/t['artifact'] for t in trace if t.get('accepted')]
 frames=[]
 for path in paths:
  rows=read_fasta(path);a=accuracy(rows,reference,core)
  frames.append(dict(score=score(rows),accuracy=a['core_pair_recall'],hits=a['pair_hits'],total=a['reference_pairs'],rows=rows))
 # Focus on an anchor residue where co-aligned partners changed, selected for
 # visualization only, never fed back into optimization or score acceptance.
 def partners(rows):
  cols=positions(rows);return {c[0]:c for c in cols if c[0] is not None}
 before=partners(frames[0]['rows']);after=partners(frames[-1]['rows']);changed=[p for p in before if p in after and before[p]!=after[p] and p in mapping[ids[0]]]
 focus=changed[len(changed)//2] if changed else max(1,len(reference[ids[0]].replace('-',''))//2)
 out.append(dict(id=case,label=label,ids=ids,frames=frames,referenceColumns=mapping,focus=focus))
Path(__file__).with_name('data.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print([(c['id'],len(c['frames']),c['focus']) for c in out])
