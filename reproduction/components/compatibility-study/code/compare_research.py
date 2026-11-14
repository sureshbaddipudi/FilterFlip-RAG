#!/usr/bin/env python3
"""Compare bounded Task 9 runs without re-running inference or assigning scientific labels."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
P=Path(__file__).resolve().parent.parent

def numeric(left,right,max_abs,mean_abs=None):
 a=np.asarray(left,dtype=np.float64);b=np.asarray(right,dtype=np.float64)
 if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():return {'passed':False,'shape_left':list(a.shape),'shape_right':list(b.shape),'error':'shape/nonfinite mismatch'}
 delta=np.abs(a-b);mx=float(delta.max()) if delta.size else 0.;mean=float(delta.mean()) if delta.size else 0.
 return {'passed':mx<=max_abs and (mean_abs is None or mean<=mean_abs),'maximum_absolute':mx,'mean_absolute':mean,'shape':list(a.shape),'bit_equal_values':bool(np.array_equal(a,b))}
def compare(runs,out):
 runs=Path(runs);out=Path(out)
 if out.exists():raise FileExistsError('Existing comparison output')
 read=lambda label,name:json.loads((runs/label/name).read_text());plan=json.loads((P/'VERIFICATION_PLAN.json').read_text());tol=plan['embedding_tolerance'];errors=[];checks=[];discrepancies=[]
 def check(name,ok,detail=None):
  checks.append({'check':name,'passed':bool(ok),'detail':detail})
  if not ok:errors.append(name)
 for label in ['baseline','candidate']:
  identity=read(label,'IDENTITY.json');expected=json.loads((P/'profiles'/str(label+'.json')).read_text());paths=json.loads((P/'AUTHORING_PATHS.json').read_text())
  check(label+' recorded runtime identity',identity['profile']==label and identity['versions']==expected['versions'] and identity['prefix']==paths[label+'_env'] and identity['model_files']==expected['model_files'] and identity['cpu_threads']==plan['torch_threads'])
  if label=='candidate':check('candidate recorded local guard binding',identity['local_guard']==expected['candidate_identity'])
  c=read(label,'COMPLETE.json');check(label+' complete bounded coverage',c['contexts']==75 and c['retrieval_contexts']==72 and c['challenge_contexts']==3 and c['generation_attempts']==0 and c['model_constructions']==1,c)
 lp=read('baseline','PROBES.json');rp=read('candidate','PROBES.json');check('same predeclared probe texts',lp['texts']==rp['texts']);check('encoder tokenizer IDs identical',lp['token_ids']==rp['token_ids']);check('encoder dimensions/window unchanged',lp['max_seq_length']==rp['max_seq_length']==256 and lp['embedding_shape']==rp['embedding_shape'] and lp['embedding_shape'][1]==384)
 emb=numeric(np.load(runs/'baseline/PROBE_EMBEDDINGS.npy',allow_pickle=False),np.load(runs/'candidate/PROBE_EMBEDDINGS.npy',allow_pickle=False),tol['maximum_absolute'],tol['mean_absolute']);check('probe embeddings within frozen tolerances',emb['passed'],emb)
 left=read('baseline','CONTEXTS.json');right=read('candidate','CONTEXTS.json');lm={(x['case_id'],x['condition']):x for x in left};rm={(x['case_id'],x['condition']):x for x in right};check('same exact case/context keys',len(lm)==len(left)==len(rm)==len(right)==75 and set(lm)==set(rm));rows=[]
 for key,l in lm.items():
  r=rm[key];cid,condition=key;discrete={}
  for name,lv,rv in [('retrieved_order_and_text',[(x.get('chunk_id',x['record_id']),x['text']) for x in l['retrieved']],[(x.get('chunk_id',x['record_id']),x['text']) for x in r['retrieved']]),('added_chunk_records',l['copy_chunks'],r['copy_chunks']),('passage_token_IDs',l['token_ids'],r['token_ids']),('policy_decisions',l['policies'],r['policies']),('answer_request_and_token_IDs',l['requests'],r['requests'])]:
   same=lv==rv;discrete[name]=same
   if not same:discrepancies.append({'case_id':cid,'condition':condition,'field':name,'baseline':lv,'candidate':rv})
  numeric_checks={}
  for field in ['query_vector','copy_vectors','scores','matrix']:
   t=numeric(l[field],r[field],tol['maximum_absolute'] if field in ['query_vector','copy_vectors'] else tol['score_absolute'],tol['mean_absolute'] if field in ['query_vector','copy_vectors'] else None);numeric_checks[field]=t
   if not t['passed']:discrepancies.append({'case_id':cid,'condition':condition,'field':field,'comparison':t})
  # Ranking scores and cutoff metadata are recorded separately from exact top-five identity.
  rank=numeric([x.get('retrieval_score',0) for x in l['retrieved']],[x.get('retrieval_score',0) for x in r['retrieved']],tol['score_absolute']);numeric_checks['retrieval_scores']=rank
  if not rank['passed']:discrepancies.append({'case_id':cid,'condition':condition,'field':'retrieval_scores','comparison':rank})
  rows.append({'case_id':cid,'condition':condition,'discrete':discrete,'numeric':numeric_checks,'baseline_cutoff':l['retrieval'],'candidate_cutoff':r['retrieval'],'historical_baseline_comparison':l['historical'],'historical_candidate_comparison':r['historical']})
 for field in ['retrieved_order_and_text','added_chunk_records','passage_token_IDs','policy_decisions','answer_request_and_token_IDs']:check('all contexts '+field,all(r['discrete'][field] for r in rows),{'matching':sum(r['discrete'][field] for r in rows),'total':75})
 for field in ['query_vector','copy_vectors','scores','matrix','retrieval_scores']:check('all contexts numeric '+field,all(r['numeric'][field]['passed'] for r in rows))
 historical={}
 for label,cc in [('baseline',left),('candidate',right)]:
  original=[r for r in cc if r['historical'] is not None];historical[label]={'retrieval_contexts':len(original),'retrieved_ids_match':sum(r['historical']['retrieved_ids_match'] for r in original),'native_kept_match':sum(r['historical']['native_kept_match'] for r in original),'U_request_match':sum(r['historical']['U_request_match'] for r in original),'N_request_match':sum(r['historical']['N_request_match'] for r in original),'cutoff_exact_ties':sum(r['retrieval'].get('cutoff_exact_tie',False) for r in original),'cutoff_near_ties':sum(r['retrieval'].get('cutoff_near_tie',False) for r in original)}
 index={label:read(label,'FROZEN_INDEX_PROBE_COMPARISON.json') for label in ['baseline','candidate']}
 index_summary={label:{'original_chunks_checked':len(rr),'maximum_absolute':max((r['max_absolute'] for r in rr),default=0),'outside_embedding_tolerance':sum(r['max_absolute']>tol['maximum_absolute'] or r['mean_absolute']>tol['mean_absolute'] for r in rr)} for label,rr in index.items()}
 status='PASS_BOUNDED_COMPATIBILITY' if not errors else 'FAIL_COMPATIBILITY'
 summary={'status':status,'checks':checks,'errors':errors,'context_count':75,'policies_per_context':4,'answer_requests_compared':300,'encoder_probe_texts':len(lp['texts']),'probe_embedding_difference':emb,'historical_comparison':historical,'frozen_index_probe_comparison':index_summary,'discrepancies':len(discrepancies),'generation_attempts':0,'answer_scope':'Same request bytes and Qwen token IDs/estimates, frozen prompt/options, synthetic status/transport validation only. No fresh Qwen service or semantic answer rerun.','filter_scope':'RAGDefender U/N/E/CN on predeclared subset, verified frozen full corpus embedding index reused with fresh query/copy encodings. No whole-corpus re-embedding or new TrustRAG stage-1 execution.','acceptance_scope':'Computational verification only; no deployment, human scientific/risk acceptance, all-advisory closure or whole-system guarantee inferred.'}
 out.mkdir(parents=True)
 for name,value in [('SUMMARY.json',summary),('CONTEXT_COMPARISONS.json',rows),('DISCREPANCIES.json',discrepancies)]: (out/name).write_text(json.dumps(value,indent=2)+'\n')
 return summary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();r=compare(a.runs,a.out);print(json.dumps({k:v for k,v in r.items() if k!='checks'},indent=2));raise SystemExit(0 if r['status']=='PASS_BOUNDED_COMPATIBILITY' else 1)
