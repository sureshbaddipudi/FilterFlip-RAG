import unittest
from run_answers import request,canonical,digest,response_status,expand

class Checks(unittest.TestCase):
    def test_requests_exclude_labels_and_ids(self):
        a=request('q',[{'text':'first','record_id':'a','expected':'secret'},{'text':'second'}])
        b=request('q',[{'text':'first','record_id':'different'},{'text':'second'}])
        self.assertEqual(digest(canonical(a)),digest(canonical(b)))
        self.assertNotIn('secret',str(a));self.assertIn('first\n\nsecond',a['messages'][1]['content'])
    def test_order_changes_request(self):
        self.assertNotEqual(request('q',[{'text':'a'},{'text':'b'}]),request('q',[{'text':'b'},{'text':'a'}]))
    def test_no_correctness_in_status(self):
        r={'done':True,'message':{'content':'A wrong answer'},'prompt_eval_count':99,'done_reason':'stop'}
        self.assertEqual(response_status(r,100),'ok')
        r['done_reason']='length';self.assertEqual(response_status(r,100),'truncated')
        r['prompt_eval_count']=3;self.assertEqual(response_status(r,100),'token_count_review_needed')
    def test_reuse_preserves_logical_identity(self):
        calls=[{'call_id':'a','case_id':'x','condition':'C','mode':'filtered','request_sha256':'h','identical_request_to':None},
               {'call_id':'b','case_id':'x','condition':'PN1','mode':'filtered','request_sha256':'h','identical_request_to':'a'}]
        r=expand(calls,{'h':{'status':'ok','answer':'answer','first_call_id':'a'}})
        self.assertEqual([x['call_id'] for x in r],['a','b']);self.assertTrue(r[1]['response_reused'])
        self.assertEqual(expand(calls,{})[0]['status'],'pending')

if __name__=='__main__':unittest.main()
