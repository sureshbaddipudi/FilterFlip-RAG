"""Execution safeguards; no model calls or study-result scoring."""
import unittest
from run_second import response_status,OPTIONS,canonical,digest
class Safeguards(unittest.TestCase):
    def test_incomplete_and_truncated_outputs_are_not_ok(self):
        base={'done':True,'message':{'content':'A response'},'prompt_eval_count':100,'done_reason':'stop'}
        self.assertEqual(response_status(base,100),'ok')
        self.assertEqual(response_status({**base,'done_reason':'length'},100),'truncated')
        self.assertEqual(response_status({**base,'message':{'content':' '}},100),'empty')
        self.assertEqual(response_status({**base,'done':False},100),'malformed')
    def test_token_mismatch_and_overflow_stop(self):
        r={'done':True,'message':{'content':'x'},'prompt_eval_count':101}
        self.assertEqual(response_status(r,100),'token_count_review_needed')
        count=OPTIONS['num_ctx']-OPTIONS['num_predict']-63
        self.assertEqual(response_status({**r,'prompt_eval_count':count},count),'context_window_review_needed')
    def test_request_identity_includes_model_and_passage_order(self):
        a={'model':'a','messages':[{'role':'user','content':'one\n\ntwo'}]}
        b={'model':'a','messages':[{'role':'user','content':'two\n\none'}]}
        self.assertNotEqual(digest(canonical(a)),digest(canonical(b)))
        self.assertNotEqual(digest(canonical(a)),digest(canonical({**a,'model':'b'})))
if __name__=='__main__':unittest.main()
