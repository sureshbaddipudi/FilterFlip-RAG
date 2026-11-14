import unittest
from run_filter import metrics,classify,CaptureEncoder

class Checks(unittest.TestCase):
    def test_quote_in_alternative_is_retained(self):
        c={'record_id':'other','copied_from':None,'chunk_id':'x','text':'The answer is Paris.'}
        m=metrics([c],'target','The answer is Paris.')
        self.assertTrue(m['quote_present']);self.assertFalse(m['source_or_copy_present'])
    def test_source_id_does_not_establish_quote(self):
        c={'record_id':'target','copied_from':None,'chunk_id':'x','text':'Only the introduction.'}
        m=metrics([c],'target','The answer is Paris.')
        self.assertFalse(m['quote_present']);self.assertTrue(m['source_or_copy_present'])
    def test_copy_counts_and_no_support_labels(self):
        c={'record_id':'insert','copied_from':'target','chunk_id':'a','text':'Answer Paris'}
        m=metrics([c,{**c,'chunk_id':'b'}],'target','Answer Paris')
        self.assertEqual(m['inserted_documents'],1);self.assertEqual(len(m['quote_chunk_ids']),2)
        self.assertNotIn('semantic_support',m)
    def test_candidate_requires_clean_retention_and_exposure(self):
        def r(before,after,add):return {'status':'ok','before':{'quote_present':before,'inserted_documents':add},'after':{'quote_present':after}}
        by={'C':r(True,True,0),'BN1':r(True,True,1),'PN1':r(True,False,1)}
        self.assertTrue(classify(by)['background_qualified'])
        by['C']=r(True,False,0);self.assertFalse(classify(by)['quote_loss_candidate'])
        by['C']=r(True,True,0);by['PN1']=r(True,False,0)
        self.assertFalse(classify(by)['quote_loss_candidate'])
        by['PN1']={'status':'fault'};self.assertIsNone(classify(by)['quote_loss_candidate'])
    def test_capture_does_not_change_arguments_or_output(self):
        sentinel=object()
        class E:
            def encode(self,strings,*a,**kw):
                self.args=(strings,a,kw);return sentinel
        e=E();c=CaptureEncoder(e)
        out=c.encode(['a','b'],9,convert_to_tensor=True)
        self.assertIs(out,sentinel);self.assertIs(c.last,sentinel)
        self.assertEqual(e.args,(['a','b'],(9,),{'convert_to_tensor':True}))

if __name__=='__main__':unittest.main()
