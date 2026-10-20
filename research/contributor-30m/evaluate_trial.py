"""Separate, post-generation reference evaluation of every completed trial case."""
import sys,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT))
from msa.core import *
records=[]
for p in sorted((HERE/'outputs').glob('*/result.json')):
 r=json.loads(p.read_text());d=next(d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets'] if d['id']==r['dataset'])
 ref=read_fasta(ROOT/d['reference']);core=json.loads((ROOT/d['mask']).read_text());inputs=read_fasta(ROOT/d['input'])
 row=dict(dataset=r['dataset'],cohort='original',n=d['n'],max_length=d['max_length'],initial_score=r['initial_score'],initial_accuracy=accuracy(read_fasta(ROOT/r['initial_path']),ref,core),arms={})
 for arm in ['row_dp','control']:
  a=r[arm];aln=read_fasta(p.parent/a['alignment']);validate(inputs,aln);v=score(aln)
  if v!=oracle_score(aln) or v!=a['score'] or canonical_hash(aln)!=a['canonical_sha256']:raise ValueError('candidate verification failed')
  row['arms'][arm]=dict(score=v,gain=v-r['initial_score'],accuracy=accuracy(aln,ref,core),seconds=a['seconds'])
 row['peak_rss_native']=r.get('peak_rss_native');row['peak_rss_unit']=r.get('peak_rss_unit');records.append(row)
for p in sorted((HERE/'additional').glob('*/result.json')):
 r=json.loads(p.read_text());d=next(d for d in json.loads((HERE/'additional/manifest.json').read_text())['records'] if d['id']==r['dataset'])
 folder=p.parent;ref=read_fasta(folder/'reference.fa');core=json.loads((folder/'core.json').read_text());inputs=read_fasta(folder/'input.fa')
 initial=read_fasta(folder/f'legacy.s{r["starting_seed"]}.fa');aln=read_fasta(folder/'row-final.fa');validate(inputs,aln)
 v=score(aln)
 if v!=oracle_score(aln) or v!=r['final_score'] or canonical_hash(aln)!=r['final_hash']:raise ValueError('additional candidate mismatch')
 records.append(dict(dataset=r['dataset'],cohort=r['role'],n=d['n'],max_length=d['max_length'],initial_score=r['start_score'],initial_accuracy=accuracy(initial,ref,core),arms={'row_dp':dict(score=v,gain=v-r['start_score'],accuracy=accuracy(aln,ref,core),seconds=r['dp_seconds'])},peak_rss_native=r['peak_rss_native'],peak_rss_unit=r['peak_rss_unit']))
(HERE/'evaluation.json').write_text(json.dumps(dict(records=records,note='Post-generation evaluation. Original-case controls except BB20029 have only 5 seconds and are not runtime-matched comparisons.'),indent=2)+'\n')
for r in records:
 a=r['arms']['row_dp'];delta=a['accuracy']['core_pair_recall']-r['initial_accuracy']['core_pair_recall']
 print(r['dataset'],r['n'],'SP',r['initial_score'],'->',a['score'],'gain',a['gain'],'accuracy delta',round(delta,6),'seconds',round(a['seconds'],2))
