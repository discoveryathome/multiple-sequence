import sys,unittest,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from row_dp import optimize_row
from msa.core import score,strip_empty


def placements(seq,profile):
    ids=sorted(profile);width=len(profile[ids[0]])
    def visit(i,j,out):
        if i==len(seq) and j==width:
            yield {k:''.join(v) for k,v in out.items()};return
        if i<len(seq) and j<width:
            yield from visit(i+1,j+1,{k:v+[seq[i] if k=='moving' else profile[k][j]] for k,v in out.items()})
        if j<width:
            yield from visit(i,j+1,{k:v+['-' if k=='moving' else profile[k][j]] for k,v in out.items()})
        if i<len(seq):
            yield from visit(i+1,j,{k:v+[seq[i] if k=='moving' else '-'] for k,v in out.items()})
    yield from visit(0,0,{k:[] for k in ['moving']+ids})

class RowDPTests(unittest.TestCase):
    def test_exhaustive_fixed_profiles(self):
        profiles=[{'a':'AC','b':'AC'}, {'a':'A-C','b':'-AC'}, {'a':'AC-','b':'-CA'},
                  {'a':'A--C','b':'-AC-'},{'a':'A--','b':'-C-','c':'--A'}]
        for profile in profiles:
            for length in [1,2,3]:
                for seq in map(''.join,itertools.product('AC',repeat=length)):
                    all_rows=list(placements(seq,profile));start=all_rows[0]
                    result,stats=optimize_row(start,'moving','dna')
                    self.assertEqual(score(result,'dna'),max(score(r,'dna') for r in all_rows))
                    self.assertEqual(strip_empty({k:v for k,v in result.items() if k!='moving'}),profile)

    def test_doublegap_affine_history(self):
        rows={'moving':'A--C','a':'-AC-','b':'A--C','c':'-AC-'}
        a,_=optimize_row(rows,'moving','dna');b,_=optimize_row(rows,'moving','dna')
        self.assertEqual(a,b)

    def test_budget_failure_explicit(self):
        with self.assertRaises(RuntimeError):optimize_row({'a':'AC','b':'AC'},'a','dna',max_states=1)

if __name__=='__main__':unittest.main()
