#!/usr/bin/env python3
"""Boundary, provenance and independent reconciliation checks for Task 8."""
from pathlib import Path
import collections,hashlib,json,tempfile,unittest,zipfile
from analyse import analyse,verify_sources,transition,PAIRS
P=Path(__file__).resolve().parent.parent
load=lambda f:json.loads((P/f).read_text())
class Checks(unittest.TestCase):
 def test_missing_and_uncertain_never_become_negative(self):
  self.assertEqual(transition(None,'no')['state'],'not_reviewed')
  self.assertEqual(transition('uncertain','no')['state'],'uncertain_pair')
 def test_incomplete_and_control_not_applicable(self):
  self.assertEqual(transition('yes','no',True)['state'],'incomplete_pair')
  self.assertEqual(transition('not_applicable','not_applicable',True)['state'],'not_applicable')
 def test_existing_output_refused_before_source_loading(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileExistsError):analyse(Path(d)/'absent',Path(d))
 def test_corrupt_source_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'x').write_bytes(b'original');(p/'SOURCE_MANIFEST.json').write_text(json.dumps({'x':{'sha256':hashlib.sha256(b'original').hexdigest(),'kind':'unchanged_file'}}));self.assertEqual(verify_sources(p),1);(p/'x').write_bytes(b'changed')
   with self.assertRaisesRegex(ValueError,'hash mismatch'):verify_sources(p)
 def test_correct_digest_wrong_archive_member_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)
   with zipfile.ZipFile(p/'a.zip','w') as z:z.writestr('x',b'other')
   (p/'x').write_bytes(b'original');(p/'SOURCE_MANIFEST.json').write_text(json.dumps({'x':{'sha256':hashlib.sha256(b'original').hexdigest(),'kind':'unchanged_archive_member','archive':'a.zip','member':'x'}}))
   with self.assertRaisesRegex(ValueError,'archive/member mismatch'):verify_sources(p)
 def test_full_reproduction_and_independent_reconciliations(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'fresh';analyse(P,out)
   for f in (P/'expected').glob('*.json'):self.assertEqual((out/f.name).read_bytes(),f.read_bytes(),f.name)
   read=lambda f:json.loads((out/f).read_text());pairs=read('COPY_PAIR_RECORDS.json');self.assertEqual(len(pairs),59*8*2)
   frozen={(r['case_id'],r['left'],r['right']):r for r in load('inputs/task02/PAIRED_CASES.json')}
   for r in pairs:
    f=frozen[r['case_id'],r['left'],r['right']];s=r['structural'];self.assertEqual(s['retrieved_copy_document_delta'],f['retrieved_copy_document_delta']);self.assertEqual(s['retained_copy_document_delta'],f['retained_copy_document_delta']);self.assertEqual(s['same_ordered_input_text'],f['input_text_sequence_same']);self.assertEqual(s['same_ordered_survivor_text'],f['survivor_text_sequence_same'])
   for r in read('COPY_PAIR_SUMMARIES.json'):
    for f in r['fields'].values():self.assertEqual(sum(f['states'].values()),r['planned_case_pairs']);self.assertEqual(sum(f['complete_value_transitions'].values()),f['states'].get('complete_pair',0))
   main=read('REPRODUCTION_SUMMARY.json')['all'];self.assertEqual(main['unique_requests'],579);self.assertEqual(main['logical_links'],821);self.assertEqual(main['changed_string_semantic_labels'],{'none':83,'minor':163,'material':11})
   self.assertEqual(len(read('REVIEW_QUALITY_NOTES.json')['exact_text_but_non_none_semantic_labels']),2);self.assertEqual(len(read('MATERIAL_DIFFERENCES.json')),11);self.assertEqual(len(read('CROSS_RECORD_DIFFERENCES.json')),1)
   prim=read('PRIMARY_SUMMARY.json');self.assertEqual(prim['accepted_original'],{'met':8,'not_met':51});self.assertEqual(prim['paired_with_historical_reference']['states'],{'complete_pair':34,'incomplete_pair':1})
   ts=read('TRUSTRAG_SUMMARY.json');self.assertEqual((ts['case_count'],ts['context_count'],ts['distinct_fresh_responses'],ts['logical_positions']),(12,36,60,72));self.assertEqual(ts['strict_endpoint'],{'met':5,'not_met':6,'uncertain':1})
   live=read('ADDITIONAL_LIVE_SUMMARY.json');self.assertEqual((live['instruction_outputs'],live['instruction_marker_exposed_outputs'],live['literal_marker_matches_in_exposed_answers']),(12,8,0));self.assertEqual(len(live['CN_false_claim_runs']),4)
   self.assertTrue(all(x['answer_category']=='wrong' for x in live['CN_false_claim_runs']))
 def test_case_source_exposure_is_distinct_documents_not_chunks(self):
  count=0
  for f in (P/'inputs/task02/cases').glob('*.json'):
   d=json.loads(f.read_text())
   for co,c in d['conditions'].items():
    copies=[p for p in c['passages'] if p['copied_from'] is not None]
    # instance_key is document-instance identity; a document can contribute more than one chunk.
    self.assertEqual(len({p['instance_key'] for p in copies}),c['metrics']['retrieved_copy_documents']);count+=1
  self.assertEqual(count,59*9)
if __name__=='__main__':unittest.main(verbosity=2)
