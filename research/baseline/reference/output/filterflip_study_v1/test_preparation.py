import copy
import unittest
from build_study import overlap,validate_data
from check_labels import validate

class PreparationTests(unittest.TestCase):
    def test_contained_prior_passage_is_not_fresh(self):
        text='The old source provides a sufficiently long passage whose several words establish a known prior document about a particular subject.'
        self.assertTrue(overlap(text,'New heading. '+text+' A closing note.')['match'])
    def test_short_generic_phrase_not_family(self):
        self.assertFalse(overlap('This is an example of a source.','This is an example of a different source.')['match'])
    def test_case_and_whitespace_overlap(self):
        self.assertTrue(overlap('THE Known Source','the   known source')['match'])
    def test_dangling_qrel_rejected(self):
        with self.assertRaises(ValueError):validate_data([{'_id':'d','text':'a'}],[{'_id':'q','text':'b'}],[{'query-id':'q','corpus-id':'missing'}])
    def test_missing_query_assessment_rejected(self):
        with self.assertRaises(ValueError):validate_data([{'_id':'d','text':'a'}],[{'_id':'q','text':'b'}],[])
    def test_duplicate_document_id_rejected(self):
        with self.assertRaises(ValueError):validate_data([{'_id':'d','text':'a'},{'_id':'d','text':'b'}],[{'_id':'q','text':'b'}],[{'query-id':'q','corpus-id':'d'}])
    def fixtures(self):
        c=[{'case_id':'q','screen_status':'pending_support_review','qrel_documents':[{'document_id':'d','text':'The answer is seven.'}]}]
        r=[{'case_id':'q','reviewer':'A','decision':'eligible','target_document_id':'d','expected_answer':'seven',
            'answer_aliases':['7'],'support_quote':'The answer is seven.','source_qualification':'','exclusion_reason':'','notes':''}]
        return c,r
    def test_valid_quote(self):
        c,r=self.fixtures();self.assertEqual(validate(r,c)[0],[])
    def test_fabricated_quote_rejected(self):
        c,r=self.fixtures();r[0]['support_quote']='The answer is eight.';self.assertTrue(validate(r,c)[0])
    def test_removed_candidate_rejected(self):
        c,r=self.fixtures();self.assertTrue(validate([],c)[0])
    def test_duplicate_candidate_rejected(self):
        c,r=self.fixtures();self.assertTrue(validate(r+copy.deepcopy(r),c)[0])
    def test_pending_does_not_become_validated(self):
        c,r=self.fixtures();r[0]['decision']='pending';errors,counts=validate(r,c);self.assertFalse(errors);self.assertEqual(counts['pending'],1)

if __name__=='__main__':unittest.main()
