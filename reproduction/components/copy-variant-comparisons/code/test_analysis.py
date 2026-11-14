import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('analysis',Path(__file__).with_name('analyse_task02_variants.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'.test_work';WORK.mkdir(exist_ok=True)

class AnalysisChecks(unittest.TestCase):
    def test_multiple_chunks_are_one_exposed_document(self):
        docs=[dict(record_id='copy1',copied_from='source',text='a'),dict(record_id='copy1',copied_from='source',text='b'),dict(record_id='original',copied_from=None,text='c')]
        self.assertEqual(a.copy_exposure(docs),dict(documents=1,chunks=2,document_ids=['copy1']))
    def test_unretrieved_insertion_does_not_count_as_exposure(self):
        self.assertEqual(a.copy_exposure([dict(record_id='original',copied_from=None)])['documents'],0)
    def test_quote_screen_collapses_whitespace_without_equating_a_name_to_a_relation(self):
        self.assertTrue(a.quote_present([{'text':'Alice\n plays  Heather.'}],'Alice plays Heather.'))
        self.assertFalse(a.quote_present([{'text':'Alice and Bob appear in the cast.'}],'Alice plays Heather.'))
        with self.assertRaises(ValueError):a.quote_present([{'text':'anything'}],' ')
    def test_text_equality_preserves_order_and_literal_text(self):
        one=[dict(text='A',record_id='original'),dict(text='B')]
        copy=[dict(text='A',record_id='copy'),dict(text='B')]
        self.assertEqual(a.text_sequence(one),a.text_sequence(copy))
        self.assertNotEqual(a.text_sequence(one),a.text_sequence(list(reversed(copy))))
        self.assertNotEqual(a.text_sequence(one),a.text_sequence([dict(text='A '),dict(text='B')]))
    def test_truncation_is_not_counted_as_same_or_different_complete_answer(self):
        self.assertEqual(a.pair_answers(dict(status='ok',answer='A'),dict(status='truncated',answer='A')),'incomplete')
    def test_duplicate_case_condition_is_rejected(self):
        with self.assertRaises(ValueError):a.index_rows([dict(case_id='c',condition='PN2')]*2,['case_id','condition'])
    def test_raw_input_mutation_rejected_before_outputs(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            p=Path(tmp);shutil.copytree(ROOT/'inputs',p/'inputs');shutil.copy2(ROOT/'SOURCE_MANIFEST.json',p/'SOURCE_MANIFEST.json')
            with (p/'inputs/reproduction_logical.json').open('a') as f:f.write(' ')
            with self.assertRaisesRegex(ValueError,'Source snapshot changed'):a.analyse(p/'inputs',p/'analysis')
            self.assertFalse((p/'analysis').exists())
    def test_full_offline_run_and_expected_regression(self):
        with tempfile.TemporaryDirectory(dir=WORK) as tmp:
            out=Path(tmp)/'analysis';result=a.analyse(ROOT/'inputs',out)
            self.assertEqual(result['paired_case_records'],472)
            for p in (ROOT/'expected').rglob('*'):
                if p.is_file():self.assertEqual(p.read_bytes(),(out/p.relative_to(ROOT/'expected')).read_bytes(),str(p))
            pairs=a.read(out/'PAIRED_SUMMARIES.json')
            p=next(x for x in pairs if x['dataset']=='All' and x['left']=='PN1' and x['right']=='PN2')
            self.assertEqual(p['quote_transitions'],{'0->0':42,'0->1':8,'1->0':4,'1->1':5})
            for packet in (out/'cases').glob('*.json'):
                x=a.read(packet)
                self.assertEqual(len(x['secondary_condition_reviews']),6)
                self.assertTrue(all(all(v is None for k,v in r.items() if k!='condition') for r in x['secondary_condition_reviews']))
            with self.assertRaisesRegex(ValueError,'new, separate'):a.analyse(ROOT/'inputs',out)
if __name__=='__main__':unittest.main(verbosity=2)
