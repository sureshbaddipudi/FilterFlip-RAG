"""Synthetic negative/uncertainty controls; never real human reviews."""
import json,tempfile,unittest,shutil,subprocess,sys
from pathlib import Path
from packet_common import P,load,sha,verify_tree
from validate_review_return import validate
class IntegrityControls(unittest.TestCase):
 def fixture(self,root):
  (root/'one.txt').write_text('known');(root/'SHA256_MANIFEST.json').write_text(json.dumps({'one.txt':sha(root/'one.txt')}))
 def test_corrupt_source_rejected(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);(r/'one.txt').write_text('changed')
   with self.assertRaises(ValueError):verify_tree(r)
 def test_extra_file_rejected(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);(r/'extra').write_text('extra')
   with self.assertRaises(ValueError):verify_tree(r)
 def test_path_escape_rejected(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);(r/'SHA256_MANIFEST.json').write_text(json.dumps({'../escape':'0'*64}))
   with self.assertRaises(ValueError):verify_tree(r)
class ReturnControls(unittest.TestCase):
 def fixture(self,r):
  for src,dst in [('VERIFICATION_RETURN_TEMPLATE.json','VERIFICATION_RETURN.json'),('TASK12_ANSWER_REVIEW_TEMPLATE.json','TASK12_ANSWER_REVIEW.json')]:
   d=load(P/'review'/src);d['packet_manifest_sha256']=sha(P/'SHA256_MANIFEST.json');(r/dst).write_text(json.dumps(d))
  (r/'DISCREPANCIES.json').write_text('[]')
 def test_blank_is_pending_not_pass(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);self.assertEqual(validate(r)['completion'],'PENDING')
 def test_identity_tampering_rejected(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);p=r/'TASK12_ANSWER_REVIEW.json';d=load(p);d['records'][0]['request_sha256']='0'*64;p.write_text(json.dumps(d))
   with self.assertRaises(ValueError):validate(r)
 def test_duplicate_record_rejected(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);p=r/'TASK12_ANSWER_REVIEW.json';d=load(p);d['records'][-1]=d['records'][0];p.write_text(json.dumps(d))
   with self.assertRaises(ValueError):validate(r)
 def test_uncertainty_retained(self):
  with tempfile.TemporaryDirectory()as t:
   r=Path(t);self.fixture(r);p=r/'TASK12_ANSWER_REVIEW.json';d=load(p)
   for row in d['records']:row.update(review_state='evidence_incomplete',comments='SYNTHETIC CONTROL: evidence unavailable; no real human review')
   p.write_text(json.dumps(d));result=validate(r);self.assertEqual(result['uncertain_or_incomplete_rows'],20);self.assertEqual(result['completion'],'PENDING')
class PortableAuditControls(unittest.TestCase):
 def run_copy(self,change,success):
  with tempfile.TemporaryDirectory()as t:
   root=Path(t);packet=root/'copied_task12';shutil.copytree(P/'components/task12',packet)
   change(packet)
   args=[sys.executable,'-I','-B',str(P/'tools/audit_saved_rehearsal.py'),'--packet',str(packet),'--runs',str(packet/'runs'),'--guard-events',str(packet/'runtime/guard_events.jsonl'),'--source-app',str(P/'baseline/v24'),'--out',str(root/'audit.json')]
   r=subprocess.run(args,capture_output=True,text=True)
   self.assertEqual(r.returncode==0,success,r.stdout+r.stderr)
 def test_nonexistent_authoring_locators_not_needed(self):
  def change(packet):
   p=packet/'inputs/SOURCE_BINDINGS.json';d=load(p);p.write_text(json.dumps({'/nonexistent_authoring_machine/'+str(i):v for i,v in enumerate(d.values())}))
  self.run_copy(change,True)
 def test_changed_source_snapshot_rejected(self):
  def change(packet):
   d=load(packet/'inputs/SOURCE_BINDINGS.json');p=packet/next(iter(d.values()))['snapshot'];p.write_text('CORRUPTED SYNTHETIC CONTROL')
  self.run_copy(change,False)
 def test_changed_raw_capture_rejected(self):
  def change(packet):next((packet/'runs').glob('*/response_01.bin')).write_text('{}')
  self.run_copy(change,False)
from test_return_f2 import F2Controls
if __name__=='__main__':unittest.main()
