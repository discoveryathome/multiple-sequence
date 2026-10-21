import importlib.util,json,tempfile,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('readiness',ROOT/'scripts/readiness.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class PreparationTests(unittest.TestCase):
    def test_interface_and_claims(self):
        c=r.bound_case('BB11015');file=ROOT/c['incumbent']
        self.assertEqual(r.check_candidate('BB11015',file)['delta_from_inherited'],0)
        with self.assertRaises(ValueError):r.check_candidate('BB11015',file,999999)
        with self.assertRaises(ValueError):r.check_candidate('BB11001',file)
    def test_reference_free_check_and_postgeneration_diagnostic(self):
        c=r.bound_case('BB11015');file=ROOT/c['incumbent']
        self.assertNotIn('reference_metrics',r.check_candidate('BB11015',file))
        actual=r.read_fasta
        def guarded(path):
            if 'references' in str(path) or str(path).endswith('reference.fa'):raise RuntimeError('Reference access')
            return actual(path)
        with patch.object(r,'read_fasta',side_effect=guarded):
            self.assertTrue(r.check_candidate('BB11015',file)['valid'])
        result=r.check_candidate('BB11015',file,biological=True)
        self.assertLess(result['pair_recall_delta_from_best_baseline'],0)
    def test_forged_residue_rejected(self):
        c=r.bound_case('BB11015');rows=r.read_fasta(ROOT/c['incumbent']);key=next(iter(rows));rows[key]=rows[key].replace('A','W',1)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.fa';p.write_text(''.join('>'+k+'\n'+s+'\n' for k,s in rows.items()))
            with self.assertRaises(ValueError):r.check_candidate('BB11015',p)
    def test_reserve_sequence_overlap_and_input_contract(self):
        spec=importlib.util.spec_from_file_location('reserve',ROOT/'scripts/reserve_families.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        old='ARNDCQEGHILKMFPSTWYV';known=[(old,module.kmers(old))]
        self.assertTrue(module.overlaps({'different-id':old},known))
        self.assertTrue(module.overlaps({'near':old+'A'},known))
        self.assertFalse(module.overlaps({'unrelated':'WWWWWWWW'},known))
        with self.assertRaises(ValueError):module.sequences('>x\nAA-AA\n')
        with self.assertRaises(ValueError):module.sequences('>x\nAAAA\n>x\nAAAA\n')
if __name__=='__main__':unittest.main()
