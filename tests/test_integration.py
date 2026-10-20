import unittest
from msa.cli import check_candidate
from msa.core import ROOT,read_fasta,score

class CandidateTests(unittest.TestCase):
    def test_wrong_claim_rejected(self):
        path=ROOT/'results/baselines/BB11001.mafft-linsi.fa'
        actual=score(read_fasta(path))
        self.assertEqual(check_candidate('BB11001',path,actual)['score'],actual)
        with self.assertRaises(ValueError):check_candidate('BB11001',path,actual+1)

    def test_different_dataset_rejected(self):
        with self.assertRaises(ValueError):check_candidate('BB11015',ROOT/'results/baselines/BB11001.mafft-linsi.fa')
