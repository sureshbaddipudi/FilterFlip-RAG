"""Recompute all 36 frozen stage-1 decisions. No encoder or answer model loaded."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'app'))
import safety,trust
if __name__=='__main__':
 safety.verify_release();rows=[]
 for expected in safety.load(R/'provenance/TRUST_EXPECTED_SELECTIONS.json'):
  source,result=trust.compute(expected['case_id'],expected['condition']);kept=result['policies']['T']['kept']
  ok=kept==expected['kept_indices_native_order'] and [source['retrieved'][i]['text'] for i in kept]==expected['output_texts']
  rows.append({'case_id':source['case_id'],'condition':source['condition'],'kept':kept,'matches_saved_selection':ok})
 print(json.dumps({'status':'PASS' if all(r['matches_saved_selection'] for r in rows) else 'FAIL','contexts':len(rows),'answer_model_calls':0,'encoder_calls':0,'rows':rows},indent=2))
 if len(rows)!=36 or not all(r['matches_saved_selection'] for r in rows):raise SystemExit(1)
