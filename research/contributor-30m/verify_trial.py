"""Offline exact-score, integrity and reference evaluation verification."""
import argparse,json,sys,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from msa.core import *
from row_dp import optimize_row
p=argparse.ArgumentParser();p.add_argument('--replay-first',action='store_true');p.add_argument('--replay-case');a=p.parse_args()
subprocess.run([sys.executable,str(HERE/'test_row_dp.py'),'-v'],check=True)
subprocess.run([sys.executable,str(HERE/'test_randomized.py'),'-v'],check=True)
known_hashes={digest(HERE/'row_dp.py'),digest(HERE/'row_dp_v1.py')}
checked=0;replayed=0
expected={d['id'] for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets']}
if {p.parent.name for p in (HERE/'outputs').glob('*/result.json')}!=expected:raise ValueError('missing original case result')
expected_extra={d['id'] for d in json.loads((HERE/'additional/manifest.json').read_text())['records']}
if {p.parent.name for p in (HERE/'additional').glob('*/result.json')}!=expected_extra:raise ValueError('missing additional case result')

def check(inputs,path,expected):
 global checked
 rows=read_fasta(path);validate(inputs,rows);value=score(rows)
 if value!=expected or oracle_score(rows)!=value:raise ValueError('exact score mismatch: '+str(path))
 checked+=1;return rows

for p in sorted((HERE/'outputs').glob('*/result.json')):
 r=json.loads(p.read_text());d=next(d for d in json.loads((ROOT/'data/manifest.json').read_text())['datasets'] if d['id']==r['dataset']);inputs=read_fasta(ROOT/d['input'])
 if r['source_sha256'] not in known_hashes:raise ValueError('unknown source hash')
 initial=check(inputs,ROOT/r['initial_path'],r['initial_score'])
 if canonical_hash(initial)!=r['initial_hash']:raise ValueError('initial hash mismatch')
 for arm in ['row_dp','control']:
  last=r['initial_score']
  for t in r[arm]['trace']:
   if t['before']!=last or t['accepted']!=(t['after']>last):raise ValueError('invalid acceptance chain')
   if t['accepted']:
    rows=check(inputs,p.parent/t['artifact'],t['after']);last=t['after']
    if canonical_hash(rows)!=t['canonical_sha256']:raise ValueError('artifact hash mismatch')
  rows=check(inputs,p.parent/r[arm]['alignment'],r[arm]['score'])
  if last!=r[arm]['score'] or canonical_hash(rows)!=r[arm]['canonical_sha256']:raise ValueError('final mismatch')
 if a.replay_first or a.replay_case==r['dataset']:
  rows=initial
  trace=r['row_dp']['trace'] if a.replay_case==r['dataset'] else r['row_dp']['trace'][:1]
  for t in trace:
   proposal,stats=optimize_row(rows,t['row'])
   if score(proposal)!=t['after']:raise ValueError('row replay differs')
   if t['accepted']:
    if canonical_hash(proposal)!=t['canonical_sha256']:raise ValueError('row replay hash differs')
    rows=proposal
   replayed+=1
for p in sorted((HERE/'additional').glob('*/result.json')):
 r=json.loads(p.read_text());d=next(d for d in json.loads((HERE/'additional/manifest.json').read_text())['records'] if d['id']==r['dataset']);folder=p.parent
 for name,h in d['sha256'].items():
  if digest(folder/name)!=h:raise ValueError('additional data drift')
 if r['source_sha256'] not in known_hashes:raise ValueError('unknown additional source hash')
 inputs=read_fasta(folder/'input.fa');initial=check(inputs,folder/f'legacy.s{r["starting_seed"]}.fa',r['start_score']);last=r['start_score']
 for b in r['baselines']:
  rows=check(inputs,folder/(b['method']+'.fa'),b['score'])
  if b['repeat_hashes']!=[canonical_hash(rows)]*2:raise ValueError('additional baseline replay mismatch')
 for legacy in r['legacy']:check(inputs,folder/f'legacy.s{legacy["seed"]}.fa',legacy['score'])
 for t in r['trace']:
  if 'error' in t:continue
  if t['before']!=last or t['accepted']!=(t['after']>last):raise ValueError('additional trace mismatch')
  if t['accepted']:check(inputs,folder/t['artifact'],t['after']);last=t['after']
 rows=check(inputs,folder/'row-final.fa',r['final_score'])
 if last!=r['final_score'] or canonical_hash(rows)!=r['final_hash']:raise ValueError('additional final mismatch')
 if a.replay_first and r['trace'] and 'error' not in r['trace'][0]:
  t=r['trace'][0];proposal,stats=optimize_row(initial,t['row'])
  if score(proposal)!=t['after']:raise ValueError('additional row replay differs')
  replayed+=1
for p in sorted((HERE/'convergence').glob('*/result.json')):
 r=json.loads(p.read_text())
 if r['source_sha256'] not in known_hashes:raise ValueError('unknown convergence source hash')
 initial=read_fasta(ROOT/r['start_path']);inputs={k:s.replace('-','') for k,s in initial.items()};last=score(initial)
 for t in r['trace']:
  if t['before']!=last or t['accepted']!=(t['after']>last):raise ValueError('convergence trace mismatch')
  if t['accepted']:check(inputs,p.parent/t['artifact'],t['after']);last=t['after']
 rows=check(inputs,p.parent/'final.fa',r['score'])
 if last!=r['score'] or canonical_hash(rows)!=r['final_hash']:raise ValueError('convergence final hash mismatch')
 if r['local_optimum'] and r['sweeps'][-1]['accepted']!=0:raise ValueError('false coordinate optimum claim')
subprocess.run([sys.executable,str(HERE/'evaluate_trial.py')],check=True)
print(json.dumps(dict(status='PASS',alignment_checks=checked,exact_row_replays=replayed,coverage='Exact values and preserved residues; biological metrics separately recomputed. Coordinate optimality requires full last-sweep replay.')))
