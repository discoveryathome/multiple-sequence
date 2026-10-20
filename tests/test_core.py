import unittest
from itertools import product
from tempfile import TemporaryDirectory
from pathlib import Path
from msa.core import *
from msa.refine import profile_align,refine


def all_alignments(a,b):
    if not a and not b:
        yield ('','')
    if a and b:
        for x,y in all_alignments(a[1:],b[1:]): yield a[0]+x,b[0]+y
    if a:
        for x,y in all_alignments(a[1:],b): yield a[0]+x,'-'+y
    if b:
        for x,y in all_alignments(a,b[1:]): yield '-'+x,b[0]+y


class ExactTests(unittest.TestCase):
    def test_hand_scores(self):
        self.assertEqual(score({'a':'AA','b':'AA'}),8)
        self.assertEqual(score({'a':'AAAA','b':'A---'}),4-11-2)
        self.assertEqual(score({'a':'-A','b':'A-'}),-22)
        # Double-gap columns do not split a pair's gap run.
        self.assertEqual(score({'a':'A--A','b':'----'}),-12)
        self.assertEqual(score({'a':'A--A','b':'A--A'}),8)
        self.assertEqual(score({'a':'AC','b':'AT'},'dna'),1)
        self.assertEqual(score({'a':'A','b':'A','c':'A'}),12)

    def test_exhaustive_two_sequence(self):
        # 900+ paths, including adjacent opposite gaps and terminal runs.
        for n in range(1,4):
            for m in range(1,4):
                for a in map(''.join,product('AC',repeat=n)):
                    for b in map(''.join,product('AC',repeat=m)):
                        for x,y in all_alignments(a,b):
                            rows={'a':x,'b':y}
                            validate({'a':a,'b':b},rows,'dna')
                            self.assertEqual(score(rows,'dna'),oracle_score(rows,'dna'))

    def test_validation_negative(self):
        inputs={'a':'AC','b':'AC'}
        bad=[{'a':'AC','c':'AC'}, {'a':'AC','b':'A'}, {'a':'AC','b':'AT'},
             {'a':'A-C','b':'A-C'}, {'a':'AC.','b':'AC-'}, {'a':'CA','b':'AC'},
             {'a':'ACC','b':'AC-'}, {'a':'AX','b':'AC'}]
        for rows in bad:
            with self.assertRaises(ValueError): validate(inputs,rows,'dna')
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'bad.fa'
            for text in ['>a\nAC\n>a\nAC\n','AC\n','>\nAC\n','>a\n']:
                p.write_text(text)
                with self.assertRaises(ValueError): read_fasta(p)

    def test_accuracy_residue_coordinates(self):
        ref={'a':'AC-','b':'A-C'}
        got={'a':'AC','b':'AC'}
        r=accuracy(got,ref,[True,True,False])
        self.assertEqual((r['pair_hits'],r['reference_pairs']), (1,1))
        self.assertEqual((r['column_hits'],r['core_columns']),(1,2))
        self.assertEqual(accuracy(ref,ref,[True]*3)['core_pair_recall'],1)
        ref={'a':'-AC','b':'A-C'};got={'a':'AC','b':'AC'}
        self.assertEqual(accuracy(got,ref,[False,False,True])['pair_hits'],1)

    def test_profile_surrogate_global_optimum(self):
        sub,_,_=matrix('dna')
        for a,b in [('AC','CA'),('AAC','AC'),('A','C')]:
            def linear(x,y): return sum(-4 if '-' in (u,v) else sub[u,v] for u,v in zip(x,y))
            rows=profile_align({'a':a},{'b':b},'dna')
            best=max(linear(x,y) for x,y in all_alignments(a,b))
            self.assertEqual(linear(rows['a'],rows['b']),best)

    def test_refinement_deterministic_valid_monotonic(self):
        inputs={'a':'AAC','b':'AC','c':'ACC'}
        initial={'a':'AAC-','b':'A-C-','c':'A-CC'}
        for op in ['block','subgroup','gap','profile']:
            a,t=refine(inputs,initial,5,2,(op,),'dna')
            b,u=refine(inputs,initial,5,2,(op,),'dna')
            self.assertEqual((a,t),(b,u));validate(inputs,a,'dna')
            self.assertGreaterEqual(score(a,'dna'),score(initial,'dna'))
            self.assertTrue(all(not e['accepted'] or e['proposal']>e['before'] for e in t))

if __name__=='__main__': unittest.main()
