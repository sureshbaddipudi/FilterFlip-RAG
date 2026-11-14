"""F2 synthetic controls only; never human/scientific review records."""
import copy,json,shutil,subprocess,sys,tempfile,unittest,zipfile,io,contextlib
from unittest.mock import patch
from pathlib import Path
from packet_common import P,load,sha
from return_evidence import plan,specs,existing_outputs
from validate_review_return import validate

def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def synthetic_return(root,features=None):
 features=features or {'node':True,'numpy':True};root=Path(root);root.mkdir(parents=True);offline=root/'offline';offline.mkdir();manifest=sha(P/'SHA256_MANIFEST.json')
 for src,dest in [('VERIFICATION_RETURN_TEMPLATE.json','VERIFICATION_RETURN.json'),('TASK12_ANSWER_REVIEW_TEMPLATE.json','TASK12_ANSWER_REVIEW.json')]:
  d=load(P/'review'/src);d.update(packet_manifest_sha256=manifest,reviewer='SYNTHETIC CONTROL — NOT A HUMAN REVIEW',review_date='2026-11-03',assistance_disclosure='Synthetic software fixture; no human review occurred')
  if 'records'in d:
   for r in d['records']:r.update(review_state='reviewed',support='uncertain',core_usable='uncertain',answer_category='uncertain',extra_error='uncertain',instruction_followed='uncertain',comments='SYNTHETIC CONTROL: valid uncertainty, not a scientific judgment')
  else:
   d.update(received_zip_sha256='1'*64,recommendation='request_changes')
   for r in d['checks'].values():r.update(status='PASS',evidence='notes.txt')
   d['checks']['pristine_integrity_before']['evidence']='offline/pristine_before.json';d['checks']['pristine_integrity_after']['evidence']='offline/pristine_after.json';d['checks']['offline_reproduction']['evidence']='offline/EXECUTION.json';d['checks']['saved_Task12_answer_review']['evidence']='TASK12_ANSWER_REVIEW.json'
  save(root/dest,d)
 (root/'notes.txt').write_text('SYNTHETIC CONTROL: not actual browser/human evidence.\n');save(root/'DISCREPANCIES.json',[])
 report={'integrity':'PASS','packet_manifest_sha256':manifest,'files':len(load(P/'SHA256_MANIFEST.json')),'sealed_components':15,'review_records':20,'model_calls':0,'verification_stage':'before'}
 save(offline/'pristine_before.json',report);save(offline/'pristine_after.json',dict(report,verification_stage='after'))
 steps=[]
 for spec in specs(features):
  n=spec['name']
  if spec['kind']=='not_run'or(not features['node']and n in ('javascript_syntax','recorded59_dom')):steps.append({'name':n,'status':'NOT_RUN','reason':'SYNTHETIC: missing tool'});continue
  if 'output_set'in spec:
   s=plan()['output_sets'][spec['output_set']]
   for f in s['files']:
    dst=offline/s['output_root']/f
    if not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/s['expected_packet_root']/f,dst)
  if n.startswith('comparator31_'):
   source='TEST_NORMAL.json'if n.endswith('normal')else'TEST_OPTIMIZED.json';shutil.copy2(P/'components/task09_v2/validation'/source,offline/spec['output_files'][0])
  if n=='saved_rehearsal507':shutil.copy2(P/'components/task12/validation/REHEARSAL_AUDIT.json',offline/'REHEARSAL_AUDIT.json')
  log=offline/'logs'/(n+'.log');log.parent.mkdir(exist_ok=True);log.write_text('SYNTHETIC CONTROL: no command or human review performed.\n')
  row={'name':n,'status':'PASS','log':str(log.relative_to(offline)),'log_sha256':sha(log),'outputs':existing_outputs(offline,spec)}
  if spec['kind']=='command':row['exit_code']=0
  steps.append(row)
 overall='PASS_WITH_NOT_RUN'if not all(features.values())else'PASS'
 execution={'schema_version':2,'packet_manifest_sha256':manifest,'plan_sha256':sha(P/'provenance/OFFLINE_PLAN.json'),'driver_sha256':sha(P/'tools/reproduce_offline.py'),'features':features,'overall':overall,'steps':steps,'integrity_before':report,'integrity_before_file':'pristine_before.json','integrity_before_sha256':sha(offline/'pristine_before.json')}
 execution.update({f:0 for f in plan()['action_fields']});save(offline/'EXECUTION.json',execution)
 if overall!='PASS':
  v=load(root/'VERIFICATION_RETURN.json');v['checks']['offline_reproduction'].update(status='NOT_RUN',notes='SYNTHETIC: documented missing-tool branch; remaining checks supplied');save(root/'VERIFICATION_RETURN.json',v)
 return root

class F2Controls(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.base=tempfile.TemporaryDirectory();cls.seed=synthetic_return(Path(cls.base.name)/'seed')
 @classmethod
 def tearDownClass(cls):cls.base.cleanup()
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name)/'return';shutil.copytree(self.seed,self.r)
 def tearDown(self):self.tmp.cleanup()
 def vedit(self,fn):p=self.r/'VERIFICATION_RETURN.json';d=load(p);fn(d);save(p,d)
 def eedit(self,fn):p=self.r/'offline/EXECUTION.json';d=load(p);fn(d);save(p,d)
 def test_complete_positive_uncertain_return(self):
  d=validate(self.r);self.assertEqual(d['completion'],'COMPLETE_RETURN');self.assertEqual(d['verification_result'],'PASS');self.assertEqual(d['uncertain_or_incomplete_rows'],20);self.assertEqual(d['Suresh_final_acceptance'],'pending separate decision')
 def test_missing_received_hash_is_pending(self):self.vedit(lambda d:d.update(received_zip_sha256=None));self.assertIn('received_zip_sha256',validate(self.r)['pending_fields'])
 def test_invalid_received_hash_rejected(self):
  self.vedit(lambda d:d.update(received_zip_sha256='not a digest'))
  with self.assertRaisesRegex(ValueError,'64 hexadecimal'):validate(self.r)
 def test_trusted_checksum_mismatch_rejected(self):
  with self.assertRaisesRegex(ValueError,'trusted delivery'):validate(self.r,'2'*64)
 def test_supplied_archive_hash_mismatch_rejected(self):
  z=Path(self.tmp.name)/'received.zip';z.write_bytes(b'SYNTHETIC archive bytes')
  with self.assertRaisesRegex(ValueError,'supplied archive'):validate(self.r,received_zip=z)
 def test_supplied_archive_hash_matches_without_auth_claim(self):
  z=Path(self.tmp.name)/'received.zip';z.write_bytes(b'SYNTHETIC archive bytes');self.vedit(lambda d:d.update(received_zip_sha256=sha(z)));d=validate(self.r,received_zip=z);self.assertEqual(d['received_zip_verification'],'MATCHES_SUPPLIED_ARCHIVE_ONLY')
 def test_PASS_without_checklist_evidence_pending(self):
  self.vedit(lambda d:[r.update(evidence=None)for r in d['checks'].values()]);self.assertNotEqual(validate(self.r)['completion'],'COMPLETE_RETURN')
 def test_missing_before_report_rejected(self):
  (self.r/'offline/pristine_before.json').unlink()
  with self.assertRaises(ValueError):validate(self.r)
 def test_missing_after_report_rejected(self):
  (self.r/'offline/pristine_after.json').unlink()
  with self.assertRaises(ValueError):validate(self.r)
 def test_wrong_integrity_packet_rejected(self):
  p=self.r/'offline/pristine_after.json';d=load(p);d['packet_manifest_sha256']='3'*64;save(p,d)
  with self.assertRaisesRegex(ValueError,'packet binding'):validate(self.r)
 def test_before_report_cannot_be_reused_as_after(self):
  self.vedit(lambda d:d['checks']['pristine_integrity_after'].update(evidence='offline/pristine_before.json'))
  with self.assertRaisesRegex(ValueError,'before/after'):validate(self.r)
 def test_missing_integrity_stage_rejected(self):
  p=self.r/'offline/pristine_after.json';d=load(p);d.pop('verification_stage');save(p,d)
  with self.assertRaisesRegex(ValueError,'before/after'):validate(self.r)
 def test_wrong_after_integrity_inventory_rejected(self):
  p=self.r/'offline/pristine_after.json';d=load(p);d['files']+=1;save(p,d)
  with self.assertRaisesRegex(ValueError,'inventory'):validate(self.r)
 def test_empty_PASS_inventory_rejected(self):
  self.eedit(lambda d:d.update(steps=[]))
  with self.assertRaisesRegex(ValueError,'planned execution'):validate(self.r)
 def test_missing_step_rejected(self):
  self.eedit(lambda d:d['steps'].pop(0))
  with self.assertRaisesRegex(ValueError,'planned execution'):validate(self.r)
 def test_duplicate_step_rejected(self):
  self.eedit(lambda d:d['steps'].append(copy.deepcopy(d['steps'][0])))
  with self.assertRaisesRegex(ValueError,'Duplicate'):validate(self.r)
 def test_unknown_step_rejected(self):
  self.eedit(lambda d:d['steps'][0].update(name='unknown_check'))
  with self.assertRaisesRegex(ValueError,'unknown'):validate(self.r)
 def test_reordered_steps_rejected(self):
  self.eedit(lambda d:d['steps'].reverse())
  with self.assertRaisesRegex(ValueError,'reordered'):validate(self.r)
 def test_missing_log_declaration_rejected(self):
  self.eedit(lambda d:d['steps'][0].pop('log'))
  with self.assertRaisesRegex(ValueError,'needs log'):validate(self.r)
 def test_missing_log_file_rejected(self):
  e=load(self.r/'offline/EXECUTION.json');(self.r/'offline'/e['steps'][0]['log']).unlink()
  with self.assertRaises(ValueError):validate(self.r)
 def test_log_hash_mismatch_rejected(self):
  self.eedit(lambda d:d['steps'][0].update(log_sha256='4'*64))
  with self.assertRaisesRegex(ValueError,'execution log'):validate(self.r)
 def test_empty_log_rejected_even_with_matching_hash(self):
  e=load(self.r/'offline/EXECUTION.json');p=self.r/'offline'/e['steps'][0]['log'];p.write_bytes(b'');e['steps'][0]['log_sha256']=sha(p);save(self.r/'offline/EXECUTION.json',e)
  with self.assertRaisesRegex(ValueError,'empty'):validate(self.r)
 def test_missing_generated_output_rejected(self):
  e=load(self.r/'offline/EXECUTION.json');r=next(r for r in e['steps']if r['name']=='task08_analysis');(self.r/'offline'/next(iter(r['outputs']))).unlink()
  with self.assertRaisesRegex(ValueError,'outputs'):validate(self.r)
 def test_omitted_output_binding_rejected(self):
  self.eedit(lambda d:next(r for r in d['steps']if r['name']=='task08_expected')['outputs'].popitem())
  with self.assertRaisesRegex(ValueError,'outputs'):validate(self.r)
 def test_changed_generated_output_rejected(self):
  e=load(self.r/'offline/EXECUTION.json');r=next(r for r in e['steps']if r['name']=='task08_expected');(self.r/'offline'/next(iter(r['outputs']))).write_text('SYNTHETIC CORRUPTION')
  with self.assertRaisesRegex(ValueError,'outputs'):validate(self.r)
 def test_wrong_plan_binding_rejected(self):
  self.eedit(lambda d:d.update(plan_sha256='5'*64))
  with self.assertRaisesRegex(ValueError,'plan/driver'):validate(self.r)
 def test_overall_mismatch_rejected(self):
  self.eedit(lambda d:d.update(overall='FAIL'))
  with self.assertRaisesRegex(ValueError,'overall'):validate(self.r)
 def test_missing_Node_branch_complete_with_NOT_RUN(self):
  other=synthetic_return(Path(self.tmp.name)/'missing_node',{'node':False,'numpy':True});d=validate(other);self.assertEqual(d['completion'],'COMPLETE_RETURN');self.assertEqual(d['verification_result'],'PASS_WITH_NOT_RUN')
 def test_missing_NumPy_branch_complete_with_NOT_RUN(self):
  other=synthetic_return(Path(self.tmp.name)/'missing_numpy',{'node':True,'numpy':False});d=validate(other);self.assertEqual(d['execution']['planned_steps'],31);self.assertEqual(d['completion'],'COMPLETE_RETURN');self.assertEqual(d['verification_result'],'PASS_WITH_NOT_RUN')
 def test_missing_NumPy_branch_inventory_rejected(self):
  other=synthetic_return(Path(self.tmp.name)/'bad_numpy',{'node':True,'numpy':False});p=other/'offline/EXECUTION.json';d=load(p);d['steps']=[r for r in d['steps']if r['name']!='comparator_numpy_replay'];save(p,d)
  with self.assertRaises(ValueError):validate(other)
 def test_complete_failed_check_report_is_not_success(self):
  def change(d):d['steps'][0].update(status='FAIL',exit_code=1);d['overall']='FAIL'
  self.eedit(change);self.vedit(lambda d:d['checks']['offline_reproduction'].update(status='FAIL',notes='SYNTHETIC expected failure; evidence preserved'));v=validate(self.r);self.assertEqual(v['completion'],'COMPLETE_RETURN');self.assertEqual(v['verification_result'],'FAIL')
 def test_failed_upstream_requires_skipped_comparison(self):
  def change(d):
   next(r for r in d['steps']if r['name']=='task08_analysis').update(status='FAIL',exit_code=1);d['overall']='FAIL'
  self.eedit(change);self.vedit(lambda d:d['checks']['offline_reproduction'].update(status='FAIL',notes='SYNTHETIC failure'))
  with self.assertRaisesRegex(ValueError,'upstream'):validate(self.r)
  def skip(d):
   r=next(r for r in d['steps']if r['name']=='task08_expected');r.clear();r.update(name='task08_expected',status='NOT_RUN',reason='SYNTHETIC upstream failure')
  self.eedit(skip);self.assertEqual(validate(self.r)['verification_result'],'FAIL')
 def test_explicit_blocked_integrity_is_not_success(self):
  self.vedit(lambda d:d['checks']['pristine_integrity_before'].update(status='NOT_RUN',evidence=None,notes='SYNTHETIC initial integrity check unavailable'));v=validate(self.r);self.assertEqual(v['completion'],'COMPLETE_RETURN');self.assertEqual(v['verification_result'],'PASS_WITH_NOT_RUN')
 def test_interrupted_inventory_remains_pending(self):
  self.eedit(lambda d:d.update(overall='IN_PROGRESS',steps=d['steps'][:2]));self.vedit(lambda d:d['checks']['offline_reproduction'].update(status='pending'));self.assertIn('execution_in_progress',validate(self.r)['pending_fields'])
 def test_finished_ledger_with_unfilled_checkbox_stays_pending(self):
  self.vedit(lambda d:d['checks']['offline_reproduction'].update(status='pending'));v=validate(self.r);self.assertEqual(v['completion'],'PENDING');self.assertIn('offline_reproduction',v['pending_fields'])
 def test_interrupted_failure_report_stays_pending(self):
  self.eedit(lambda d:d.update(overall='IN_PROGRESS',steps=d['steps'][:2]));self.vedit(lambda d:d['checks']['offline_reproduction'].update(status='FAIL',notes='SYNTHETIC driver interruption'));self.assertEqual(validate(self.r)['completion'],'PENDING')
 def test_explicit_incomplete_route_retained(self):
  self.vedit(lambda d:d.update(received_zip_sha256=None));z=Path(self.tmp.name)/'incomplete.zip';args=[sys.executable,'-B',str(P/'tools/seal_return.py'),'--return-dir',str(self.r),'--zip',str(z)]
  refused=subprocess.run(args,capture_output=True,text=True);self.assertNotEqual(refused.returncode,0);self.assertFalse(z.exists())
  allowed=subprocess.run(args+['--allow-incomplete'],capture_output=True,text=True);self.assertEqual(allowed.returncode,0,allowed.stderr);state=load(self.r/'RETURN_STATE.json');self.assertEqual(state['completion'],'PENDING');self.assertEqual(state['verification_result'],'PENDING');self.assertEqual(state['received_zip_verification'],'MISSING_RECEIPT_CHECKSUM')
 def test_failed_integrity_cli_keeps_packet_and_stage(self):
  import verify_handover as module
  output=io.StringIO()
  with patch.object(module,'verify',side_effect=ValueError('SYNTHETIC expected integrity failure')),contextlib.redirect_stdout(output):rc=module.main(['--stage','after'])
  report=json.loads(output.getvalue());self.assertEqual(rc,1);self.assertEqual(report['integrity'],'FAIL');self.assertEqual(report['verification_stage'],'after');self.assertEqual(report['packet_manifest_sha256'],sha(P/'SHA256_MANIFEST.json'))
 def test_complete_failed_integrity_report_allowed(self):
  e=load(self.r/'offline/EXECUTION.json');report={'integrity':'FAIL','packet_manifest_sha256':e['packet_manifest_sha256'],'verification_stage':'after','error':'SYNTHETIC source mismatch'};save(self.r/'offline/pristine_after.json',report)
  row=next(r for r in e['steps']if r['name']=='pristine_after');row.update(status='FAIL',outputs={'pristine_after.json':sha(self.r/'offline/pristine_after.json')});e['overall']='FAIL';save(self.r/'offline/EXECUTION.json',e)
  def change(d):d['checks']['pristine_integrity_after'].update(status='FAIL',notes='SYNTHETIC mismatch');d['checks']['offline_reproduction'].update(status='FAIL',notes='SYNTHETIC integrity failure')
  self.vedit(change);v=validate(self.r);self.assertEqual(v['completion'],'COMPLETE_RETURN');self.assertEqual(v['verification_result'],'FAIL')
 def test_F2_default_sealing_refused(self):
  self.eedit(lambda d:d.update(steps=[]));self.vedit(lambda d:d.update(received_zip_sha256=None));z=Path(self.tmp.name)/'bad.zip';r=subprocess.run([sys.executable,'-B',str(P/'tools/seal_return.py'),'--return-dir',str(self.r),'--zip',str(z)],capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertFalse(z.exists());self.assertFalse((self.r/'SHA256_MANIFEST.json').exists())
 def test_positive_complete_return_can_be_sealed(self):
  z=Path(self.tmp.name)/'good.zip';r=subprocess.run([sys.executable,'-B',str(P/'tools/seal_return.py'),'--return-dir',str(self.r),'--zip',str(z),'--trusted-zip-sha256','1'*64],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);d=load(self.r/'RETURN_STATE.json');self.assertEqual(d['completion'],'COMPLETE_RETURN');self.assertEqual(d['verification_result'],'PASS');self.assertEqual(d['Suresh_final_acceptance'],'pending separate decision')
  with zipfile.ZipFile(z)as zz:self.assertIsNone(zz.testzip())
if __name__=='__main__':unittest.main()
