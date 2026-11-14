import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import continue_answers as c

class Tests(unittest.TestCase):
    def response(self, reason='stop'):
        return {'done':True,'message':{'content':'answer'},'prompt_eval_count':100,'done_reason':reason}
    def test_stop_is_complete_not_semantic_correctness(self):
        self.assertEqual(c.validate_response(self.response(),100),'ok')
    def test_length_preserved_as_incomplete(self):
        self.assertEqual(c.validate_response(self.response('length'),100),'truncated')
    def test_malformed_stop_rejected(self):
        r=self.response();r['done']=False
        with self.assertRaises(ValueError):c.validate_response(r,100)
    def test_bad_tokens_stop(self):
        with self.assertRaises(ValueError):c.validate_response(self.response(),200)
    def test_unknown_finish_reason_stops(self):
        with self.assertRaises(ValueError):c.validate_response(self.response('unknown'),100)
    def test_duplicate_json_rejected(self):
        with self.assertRaises(ValueError):c.decode('{"status":"ok","status":"fault"}')
    def test_nonfinite_json_rejected(self):
        for text in ['NaN','1e999']:
            with self.assertRaises(ValueError):c.decode(text)
    def test_journal_completed_attempt_can_resume_without_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'journal';j=c.Journal(p,{'v':1});j.add('session_start');j.add('begin',ordinal=128);j.add('done',ordinal=128,record={'status':'truncated'});j.add('session_end',seconds=1)
            restored=c.Journal(p,{'v':1})
            self.assertEqual([e['ordinal'] for e in restored.events if e['kind']=='done'],[128])
    def test_uncertain_attempt_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'journal';j=c.Journal(p,{'v':1});j.add('session_start');j.add('begin',ordinal=128)
            with self.assertRaises(ValueError):c.Journal(p,{'v':1})
    def test_journal_tamper_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'journal';c.Journal(p,{'v':1});p.write_text(p.read_text().replace('"v":1','"v":2'))
            with self.assertRaises(ValueError):c.Journal(p,{'v':2})
    def test_identity_change_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'journal';c.Journal(p,{'v':1})
            with self.assertRaises(ValueError):c.Journal(p,{'v':2})
    def test_completed_prefix_never_queued(self):
        q=c.decode(c.read(c.ROOT/'queue.json'));old=c.lines(c.ROOT/'inputs/prior_unique_results.jsonl')
        self.assertEqual([x['ordinal'] for x in q],list(range(128,707)))
        self.assertFalse({x['call']['request_sha256'] for x in q}&{x['request_sha256'] for x in old[:127]})
        self.assertEqual(q[0]['call']['request_sha256'],old[127]['request_sha256'])
    def test_queue_request_bytes_match_frozen_calls(self):
        q=c.decode(c.read(c.ROOT/'queue.json'))
        for x in q:
            self.assertEqual(c.sha(c.canonical(x['call']['request'])),x['call']['request_sha256'])
            self.assertEqual(x['call']['request']['options']['num_predict'],128)
    def test_original_truncation_preserved_in_empty_continuation(self):
        calls=c.lines(c.ROOT/'inputs/calls.jsonl');prior=c.lines(c.ROOT/'inputs/prior_unique_results.jsonl')
        before=c.canonical(prior)
        with tempfile.TemporaryDirectory() as td:
            j=c.Journal(Path(td)/'journal',{'v':1});s=c.build_outputs(Path(td),calls,prior,j)
            self.assertEqual(s['effective_unique_status_counts'],{'ok':127,'truncated':1})
            self.assertEqual(s['continuation_attempts_completed'],0)
        self.assertEqual(c.canonical(prior),before)
    def test_owned_group_termination(self):
        from unittest.mock import Mock
        b=c.Backend.__new__(c.Backend);b.process=Mock();b.process.pid=12345;b.log=Mock()
        with patch.object(c.os,'killpg') as kill:
            b.close();kill.assert_called_once_with(12345,c.signal.SIGKILL)
            b.process.wait.assert_called_once_with(timeout=10)
    def test_no_redirects(self):
        with self.assertRaises(ValueError):c.NoRedirect().redirect_request(None,None,None,None,None,None)

if __name__=='__main__':unittest.main(verbosity=2)
