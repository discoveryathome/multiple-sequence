import unittest,random
from itertools import combinations
from msa.core import score,oracle_score,validate,matrix,strip_empty
from msa.refine import profile_align

class PropertyTests(unittest.TestCase):
    def test_double_gaps_with_third_row(self):
        rows={'a':'A--A','b':'----','c':'-AA-'}
        # Exercise the pair scorer internally; public input validator forbids empty b.
        self.assertEqual(score(rows),oracle_score(rows))
        self.assertEqual(score({'a':'A---A','b':'-----','c':'-AAA-'}),oracle_score({'a':'A---A','b':'-----','c':'-AAA-'}))

    def test_generated_valid_msas(self):
        rng=random.Random(917)
        for _ in range(200):
            n=rng.randrange(2,7);ids=[str(i) for i in range(n)]
            rows={k:'' for k in ids}
            for col in range(rng.randrange(2,20)):
                take=rng.sample(ids,rng.randrange(1,n+1))
                for k in ids:rows[k]+=rng.choice('ACGT') if k in take else '-'
            if any(not s.replace('-','') for s in rows.values()):continue
            inputs={k:s.replace('-','') for k,s in rows.items()}
            validate(inputs,rows,'dna')
            self.assertEqual(score(rows,'dna'),oracle_score(rows,'dna'))
            self.assertEqual(score(rows,'dna'),score(dict(reversed(list(rows.items()))),'dna'))
            self.assertEqual(score(rows,'dna'),sum(score({a:rows[a],b:rows[b]},'dna') for a,b in combinations(ids,2)))

    def test_matrix_contract(self):
        sub,op,ext=matrix()
        self.assertEqual((op,ext),(11,1))
        self.assertEqual((sub['W','W'],sub['A','R'],sub['C','C']),(11,-1,9))
        self.assertTrue(all(v==sub[b,a] for (a,b),v in sub.items()))

    def test_empty_profile_window(self):
        out=profile_align({'a':'---'},{'b':'ACA'},'dna')
        self.assertEqual(out,{'a':'---','b':'ACA'})
