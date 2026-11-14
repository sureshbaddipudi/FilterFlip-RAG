#!/usr/bin/env python3
"""Meaningful comparator controls; all mutations are temporary copies, no inference."""
from pathlib import Path
import json,shutil,tempfile,unittest,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from compare_research import numeric,compare,P
class Checks(unittest.TestCase):
 def test_maximum_and_mean_tolerances_both_enforced(self):
  self.assertTrue(numeric([0.,0.],[1e-7,0.],1e-6,1e-7)['passed'])
  self.assertFalse(numeric([0.,0.],[1e-6,0.],1e-6,1e-7)['passed'])
  self.assertFalse(numeric([0.],[1.1e-6],1e-6)['passed'])
 def test_nonfinite_or_different_shapes_fail(self):
  self.assertFalse(numeric([0.],[float('nan')],1e-6)['passed']);self.assertFalse(numeric([1.],[[1.]],1e-6)['passed'])
 def test_empty_copy_arrays_are_valid(self):self.assertTrue(numeric([],[],1e-6)['passed'])
 def test_output_refuses_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileExistsError):compare(Path(d)/'absent',d)
 def test_document_ID_change_fails_even_with_same_text_and_requests(self):
  paths=json.loads((P/'AUTHORING_PATHS.json').read_text());runs=Path(paths['task09_work'])/'profile_runs'
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);shutil.copytree(runs,d/'runs');f=d/'runs/candidate/CONTEXTS.json';rows=json.loads(f.read_text());before=rows[0]['requests'];rows[0]['retrieved'][0]['chunk_id']+='__synthetic_ID_change';f.write_text(json.dumps(rows));out=d/'comparison';result=compare(d/'runs',out)
   self.assertEqual(result['status'],'FAIL_COMPATIBILITY');self.assertIn('all contexts retrieved_order_and_text',result['errors']);self.assertEqual(rows[0]['requests'],before)
if __name__=='__main__':unittest.main(verbosity=2)
