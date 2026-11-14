#!/usr/bin/env python3
"""Offline regression controls. Mutations occur only in temporary workspace copies."""
from pathlib import Path
import argparse,importlib.util,json,shutil,subprocess,sys,tempfile,unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from compare_research import numeric,compare,P
WORK=None
SCENARIOS=[]

def load(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def edit(runs,label,name,change):
 path=runs/label/name;value=load(path);result=change(value);save(path,value if result is None else result)
def cache_change(runs,change,label='candidate'):edit(runs,label,'FROZEN_INDEX_PROBE_COMPARISON.json',change)
def completion(runs,field,value,label='candidate'):
 def change(c):
  if field=='encode_calls':c['counts'][field]=value
  else:c[field]=value
 edit(runs,label,'COMPLETE.json',change)

class Checks(unittest.TestCase):
 def scenario(self,name,mutate=None,error=None,historical_pass=False,cli=False):
  with tempfile.TemporaryDirectory(dir=WORK,prefix='control_') as td:
   root=Path(td);runs=root/'runs';shutil.copytree(P/'inputs/saved_profiles',runs)
   if mutate:mutate(runs)
   historical=None
   if historical_pass:
    spec=importlib.util.spec_from_file_location('original_comparator',P/'inputs/original_code/compare_research.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.P=P
    historical=mod.compare(runs,root/'historical')['status'];self.assertEqual(historical,'PASS_BOUNDED_COMPATIBILITY')
   result=compare(runs,root/'corrected');expected='FAIL_COMPATIBILITY' if error else 'PASS_BOUNDED_COMPATIBILITY'
   self.assertEqual(result['status'],expected)
   if error:self.assertIn(error,result['errors'])
   if cli:
    proc=subprocess.run([sys.executable,'-I','-B',*(['-O'] if sys.flags.optimize else []),str(P/'code/compare_research.py'),'--runs',str(runs),'--out',str(root/'cli')],capture_output=True,text=True)
    self.assertEqual(proc.returncode,1 if error else 0,proc.stderr)
    self.assertEqual(json.loads(proc.stdout)['status'],expected)
   SCENARIOS.append({'name':name,'expected_status':expected,'actual_status':result['status'],'failed_gates':result['errors'],'historical_status':historical,'CLI_exit_checked':cli})
   return result
 def test_saved_profiles_pass(self):
  r=self.scenario('unchanged_saved_profiles',cli=True)
  self.assertEqual(r['context_count'],75);self.assertEqual(r['discrepancies'],0)
  for label in ['baseline','candidate']:
   self.assertTrue(r['frozen_index_probe_comparison'][label]['inventory_matches'])
 def test_unplanned_case_in_both_profiles(self):
  def mutate(runs):
   for label in ['baseline','candidate']:edit(runs,label,'CONTEXTS.json',lambda x:x[0].update(case_id='SYNTHETIC:unplanned'))
  self.scenario('unplanned_case_both',mutate,'baseline exact planned case/context keys',historical_pass=True,cli=True)
 def test_unplanned_condition_in_both_profiles(self):
  def mutate(runs):
   for label in ['baseline','candidate']:edit(runs,label,'CONTEXTS.json',lambda x:x[0].update(condition='SYNTHETIC_unplanned'))
  self.scenario('unplanned_condition_both',mutate,'candidate exact planned case/context keys')
 def test_duplicate_context(self):
  def mutate(runs):
   for label in ['baseline','candidate']:
    def change(x):x[1]=x[0]
    edit(runs,label,'CONTEXTS.json',change)
  self.scenario('duplicate_context_both',mutate,'baseline exact planned case/context keys')
 def test_missing_candidate_context(self):
  self.scenario('missing_candidate_context',lambda r:edit(r,'candidate','CONTEXTS.json',lambda x:x[:-1]),'candidate exact planned case/context keys')
 def test_maximum_and_mean_cache_deviation(self):
  self.scenario('cache_maximum_and_mean_exceeded',lambda r:cache_change(r,lambda x:x[0].update(max_absolute=0.5,mean_absolute=0.1)),'candidate valid cached-index deviations within frozen tolerances',historical_pass=True,cli=True)
 def test_mean_cache_deviation_alone(self):
  self.scenario('cache_mean_only_exceeded',lambda r:cache_change(r,lambda x:x[0].update(max_absolute=8e-7,mean_absolute=2e-7)),'candidate valid cached-index deviations within frozen tolerances')
 def test_maximum_cache_deviation_alone(self):
  self.scenario('cache_maximum_only_exceeded',lambda r:cache_change(r,lambda x:x[0].update(max_absolute=2e-6,mean_absolute=1e-8)),'candidate valid cached-index deviations within frozen tolerances')
 def test_empty_cache(self):
  result=self.scenario('empty_cache',lambda r:cache_change(r,lambda x:[]),'candidate exact planned cached-index probe inventory')
  self.assertIsNone(result['frozen_index_probe_comparison']['candidate']['maximum_absolute'])
 def test_missing_cache_probe(self):
  self.scenario('missing_cache_probe',lambda r:cache_change(r,lambda x:x[:-1]),'candidate exact planned cached-index probe inventory')
 def test_duplicate_cache_probe(self):
  def mutate(runs):
   def change(x):x[1]=x[0]
   cache_change(runs,change)
  self.scenario('duplicate_cache_probe',mutate,'candidate exact planned cached-index probe inventory')
 def test_unplanned_cache_probe_both_profiles(self):
  def mutate(runs):
   for label in ['baseline','candidate']:cache_change(runs,lambda x:x[0].update(chunk_id='SYNTHETIC:unplanned'),label)
  self.scenario('unplanned_cache_probe_both',mutate,'baseline exact planned cached-index probe inventory')
 def test_invalid_cache_values(self):
  for name,value in [('NaN',float('nan')),('infinity',float('inf')),('negative',-1.0),('boolean',False),('string','0')]:
   with self.subTest(value=name):self.scenario('invalid_cache_'+name,lambda r:cache_change(r,lambda x:x[0].update(max_absolute=value)),'candidate valid cached-index deviations within frozen tolerances')
 def test_cache_mean_exceeds_maximum(self):
  self.scenario('cache_mean_exceeds_maximum',lambda r:cache_change(r,lambda x:x[0].update(max_absolute=0.,mean_absolute=1e-8)),'candidate valid cached-index deviations within frozen tolerances')
 def test_missing_cache_value(self):
  def mutate(runs):
   def change(x):del x[0]['mean_absolute']
   cache_change(runs,change)
  self.scenario('missing_cache_value',mutate,'candidate valid cached-index deviations within frozen tolerances')
 def test_invalid_cache_record(self):
  def mutate(runs):
   def change(x):x[0]=None
   cache_change(runs,change)
  self.scenario('invalid_cache_record',mutate,'candidate valid cached-index deviations within frozen tolerances')
 def test_invalid_cache_container(self):
  self.scenario('invalid_cache_container',lambda r:cache_change(r,lambda x:{}),'candidate exact planned cached-index probe inventory')
 def test_runtime_limit_each_profile(self):
  for label in ['baseline','candidate']:
   with self.subTest(profile=label):self.scenario('runtime_limit_'+label,lambda r:completion(r,'active_seconds',1801,label),label+' recorded execution within frozen bounds',historical_pass=True,cli=True)
 def test_encode_limit_each_profile(self):
  for label in ['baseline','candidate']:
   with self.subTest(profile=label):self.scenario('encode_limit_'+label,lambda r:completion(r,'encode_calls',1001,label),label+' recorded execution within frozen bounds',historical_pass=True,cli=True)
 def test_invalid_runtime_values(self):
  for name,value in [('NaN',float('nan')),('infinity',float('inf')),('negative',-1.),('boolean',False),('string','1')]:
   with self.subTest(value=name):self.scenario('invalid_runtime_'+name,lambda r:completion(r,'active_seconds',value),'candidate recorded execution within frozen bounds')
 def test_invalid_encode_counts(self):
  for name,value in [('negative',-1),('fractional',1.5),('boolean',True),('string','373')]:
   with self.subTest(value=name):self.scenario('invalid_encode_count_'+name,lambda r:completion(r,'encode_calls',value),'candidate recorded execution within frozen bounds')
 def test_incomplete_status(self):
  self.scenario('incomplete_status',lambda r:completion(r,'status','INCOMPLETE'),'candidate complete planned coverage')
 def test_empty_probes_both_profiles(self):
  def mutate(runs):
   for label in ['baseline','candidate']:
    edit(runs,label,'PROBES.json',lambda x:x.update(texts=[],token_ids=[],embedding_shape=[0,384]));np.save(runs/label/'PROBE_EMBEDDINGS.npy',np.empty((0,384)),allow_pickle=False)
  self.scenario('empty_probes_both',mutate,'baseline exact planned probe text inventory')
 def test_unplanned_probe_text_both_profiles(self):
  def mutate(runs):
   for label in ['baseline','candidate']:
    def change(x):x['texts'][0]='SYNTHETIC unplanned probe'
    edit(runs,label,'PROBES.json',change)
  self.scenario('unplanned_probe_text_both',mutate,'baseline exact planned probe text inventory')
 def test_probe_array_metadata_disagreement(self):
  def mutate(runs):
   for label in ['baseline','candidate']:np.save(runs/label/'PROBE_EMBEDDINGS.npy',np.empty((0,384)),allow_pickle=False)
  self.scenario('probe_array_empty_with_valid_metadata',mutate,'baseline actual probe array has planned dimensions')
 def test_missing_probe_token_record(self):
  def mutate(runs):
   for label in ['baseline','candidate']:edit(runs,label,'PROBES.json',lambda x:x.update(token_ids=[]))
  self.scenario('missing_probe_token_record_both',mutate,'baseline complete valid probe token records')
 def test_document_ID_change_fails_even_with_same_text_and_requests(self):
  def mutate(runs):
   def change(x):x[0]['retrieved'][0]['chunk_id']+='__SYNTHETIC_ID'
   edit(runs,'candidate','CONTEXTS.json',change)
  self.scenario('changed_document_ID',mutate,'all contexts retrieved_order_and_text')
 def test_maximum_and_mean_tolerances_both_enforced(self):
  self.assertTrue(numeric([0.,0.],[1e-7,0.],1e-6,1e-7)['passed'])
  self.assertFalse(numeric([0.,0.],[1e-6,0.],1e-6,1e-7)['passed'])
  self.assertFalse(numeric([0.],[1.1e-6],1e-6)['passed'])
 def test_nonfinite_or_different_shapes_fail(self):
  self.assertFalse(numeric([0.],[float('nan')],1e-6)['passed']);self.assertFalse(numeric([1.],[[1.]],1e-6)['passed'])
 def test_empty_copy_arrays_are_valid(self):self.assertTrue(numeric([],[],1e-6)['passed'])
 def test_output_refuses_overwrite(self):
  with tempfile.TemporaryDirectory(dir=WORK) as d:
   with self.assertRaises(FileExistsError):compare(Path(d)/'absent',d)

def main():
 global WORK
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work-root',type=Path,required=True);ap.add_argument('--result',type=Path,required=True);a=ap.parse_args()
 if a.result.exists():raise FileExistsError(a.result)
 WORK=a.work_root.resolve();WORK.mkdir(parents=True,exist_ok=True)
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 a.result.parent.mkdir(parents=True,exist_ok=True)
 save(a.result,{'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'python_optimization':sys.flags.optimize,'python_executable':sys.executable,'temporary_copy_scenarios':len(SCENARIOS),'scenarios':SCENARIOS,'scope':'Offline synthetic mutations of copied saved records; no encoders, generators, services or scientific review changes.'})
 return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
