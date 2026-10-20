import sys,unittest,random
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parents[1]))
from test_row_dp import placements
from row_dp import optimize_row
from msa.core import score,oracle_score,strip_empty
class IndependentEnumeration(unittest.TestCase):
 def test_seeded_gapped_profiles(self):
  rng=random.Random(8947182);tested=0
  while tested<200:
   n=rng.randrange(1,4);width=rng.randrange(1,5)
   profile={str(k):''.join(rng.choice('AC-') for _ in range(width)) for k in range(n)}
   if any(not v.replace('-','') for v in profile.values()):continue
   profile=strip_empty(profile);seq=''.join(rng.choice('AC') for _ in range(rng.randrange(1,4)))
   possibilities=list(placements(seq,profile));answer,stats=optimize_row(possibilities[0],'moving','dna')
   # The oracle explicitly deletes double gaps and counts full gap runs.
   optimum=max(oracle_score(x,'dna') for x in possibilities)
   self.assertEqual(score(answer,'dna'),optimum)
   self.assertLessEqual(stats['max_cell_states'],2*len(next(iter(profile.values())))+1)
   tested+=1
 def test_protein_scores(self):
  rng=random.Random(2751)
  for iteration in range(40):
   profile={'a':'A-C','b':'-WC'}
   seq=''.join(rng.choice('AWC') for _ in range(rng.randrange(1,4)))
   possibilities=list(placements(seq,profile));answer,_=optimize_row(possibilities[0],'moving','protein')
   self.assertEqual(score(answer,'protein'),max(oracle_score(x,'protein') for x in possibilities))
if __name__=='__main__':unittest.main()
