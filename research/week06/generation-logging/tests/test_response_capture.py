import unittest,tempfile,json,base64,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generation_worker import record_response,validate_response
from common import sha,canonical
class CaptureTests(unittest.TestCase):
 def test_incomplete_and_malformed_bytes_survive_validation_failure(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'responses.jsonl';q={'model':'synthetic'}
   raw=b'{"done":true,"done_reason":"length","message":{"content":"partial"}}'
   record_response(p,q,raw)
   with self.assertRaises(ValueError):validate_response(json.loads(raw),100)
   bad=b'not JSON: \xff';record_response(p,q,bad)
   entries=[json.loads(x) for x in p.read_text().splitlines()]
   self.assertEqual([base64.b64decode(x['response_base64']) for x in entries],[raw,bad])
   self.assertEqual(entries[0]['request_sha256'],sha(canonical(q)))
   self.assertEqual(entries[1]['response_sha256'],sha(bad))
 def test_symlink_rejected_without_overwriting_target(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'target';target.write_text('unchanged');p=Path(d)/'link';p.symlink_to(target)
   with self.assertRaises(ValueError):record_response(p,{},b'x')
   self.assertEqual(target.read_text(),'unchanged')
 def test_response_size_limit_recorded(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'responses';record_response(p,{},b'x'*(2*1024*1024+1))
   self.assertTrue(json.loads(p.read_text())['capture_limited'])
if __name__=='__main__':unittest.main()
