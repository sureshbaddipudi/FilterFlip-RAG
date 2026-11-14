#!/usr/bin/env python3
"""Task 9 comparator v2: enforce planned coverage, probes, tolerances and limits offline."""
from pathlib import Path
import argparse,hashlib,json,math
import numpy as np
P=Path(__file__).resolve().parent.parent

def numeric(left,right,max_abs,mean_abs=None):
 a=np.asarray(left,dtype=np.float64);b=np.asarray(right,dtype=np.float64)
 if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():return {'passed':False,'shape_left':list(a.shape),'shape_right':list(b.shape),'error':'shape/nonfinite mismatch'}
 delta=np.abs(a-b);mx=float(delta.max()) if delta.size else 0.;mean=float(delta.mean()) if delta.size else 0.
 return {'passed':mx<=max_abs and (mean_abs is None or mean<=mean_abs),'maximum_absolute':mx,'mean_absolute':mean,'shape':list(a.shape),'bit_equal_values':bool(np.array_equal(a,b))}
def finite_nonnegative(value):
 return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0

def nonnegative_int(value):
 return type(value) is int and value>=0

def planned_inventory(plan):
 """Derive inventories from frozen selection records; no encoder/tokenizer calls."""
 case_ids=[x['case_id'] for x in plan['case_selection']]
 conditions=plan['conditions'];challenges=plan['challenge_conditions']
 if len(case_ids)!=len(set(case_ids)) or len(conditions)!=len(set(conditions)) or len(challenges)!=len(set(challenges)):
  raise ValueError('Duplicate entries in frozen plan')
 expected={(cid,co) for cid in case_ids for co in conditions}
 expected.update((plan['challenge_case'],co) for co in challenges)
 retrieval_count=len(case_ids)*len(conditions)
 if retrieval_count!=plan['retrieval_contexts_per_profile'] or len(challenges)!=plan['challenge_contexts_per_profile'] or len(expected)!=retrieval_count+len(challenges):
  raise ValueError('Inconsistent frozen plan counts')
 selected=[json.loads((P/'inputs/selected_cases'/str(cid.replace(':','_')+'.json')).read_text()) for cid in case_ids]
 if any(d['case']['case_id']!=cid for d,cid in zip(selected,case_ids)):
  raise ValueError('Selected record case identity differs from plan')
 texts=list(dict.fromkeys([d['case']['question'] for d in selected]+[r['text'] for d in selected for c in d['conditions'].values() for r in c['passages']]))
 cache={(d['case']['dataset'],r['chunk_id']) for d in selected for c in d['conditions'].values() for r in c['passages'] if r['copied_from'] is None}
 if not texts or not cache:raise ValueError('Empty frozen probe inventory')
 return expected,texts,cache

def cached_index_checks(records,expected,tol):
 """Invalid/empty records never receive a reassuring default zero deviation."""
 if not isinstance(records,list):
  return {'original_chunks_checked':0,'expected_original_chunks':len(expected),'inventory_matches':False,'invalid_records':1,'outside_embedding_tolerance':0,'maximum_absolute':None},False,False
 keys=[];valid=[];invalid=0;outside=0
 for r in records:
  identity=isinstance(r,dict) and isinstance(r.get('dataset'),str) and isinstance(r.get('chunk_id'),str)
  if identity:keys.append((r['dataset'],r['chunk_id']))
  numeric_ok=identity and all(finite_nonnegative(r.get(k)) for k in ['max_absolute','mean_absolute'])
  if numeric_ok:numeric_ok=r['mean_absolute']<=r['max_absolute']
  if not numeric_ok:invalid+=1;continue
  valid.append(r)
  if r['max_absolute']>tol['maximum_absolute'] or r['mean_absolute']>tol['mean_absolute']:outside+=1
 inventory=len(records)==len(keys)==len(set(keys))==len(expected) and set(keys)==expected
 values=bool(records) and invalid==0 and outside==0
 return {'original_chunks_checked':len(records),'expected_original_chunks':len(expected),'inventory_matches':inventory,'invalid_records':invalid,'outside_embedding_tolerance':outside,'maximum_absolute':max((r['max_absolute'] for r in valid),default=None)},inventory,values

def compare(runs,out):
 runs=Path(runs);out=Path(out)
 if out.exists():raise FileExistsError('Existing comparison output')
 read=lambda label,name:json.loads((runs/label/name).read_text());plan=json.loads((P/'VERIFICATION_PLAN.json').read_text());tol=plan['embedding_tolerance'];expected_keys,expected_probes,expected_cache=planned_inventory(plan);total_contexts=len(expected_keys);errors=[];checks=[];discrepancies=[]
 def check(name,ok,detail=None):
  checks.append({'check':name,'passed':bool(ok),'detail':detail})
  if not ok:errors.append(name)
 for label in ['baseline','candidate']:
  identity=read(label,'IDENTITY.json');expected=json.loads((P/'profiles'/str(label+'.json')).read_text());paths=json.loads((P/'AUTHORING_PATHS.json').read_text())
  check(label+' recorded runtime identity',identity['profile']==label and identity['versions']==expected['versions'] and identity['prefix']==paths[label+'_env'] and identity['model_files']==expected['model_files'] and identity['cpu_threads']==plan['torch_threads'])
  if label=='candidate':check('candidate recorded local guard binding',identity['local_guard']==expected['candidate_identity'])
  c=read(label,'COMPLETE.json')
  counts_ok=all(nonnegative_int(c.get(k)) for k in ['contexts','retrieval_contexts','challenge_contexts','generation_attempts','model_constructions','probes'])
  coverage=counts_ok and c.get('status')=='COMPLETE' and c['contexts']==total_contexts and c['retrieval_contexts']==plan['retrieval_contexts_per_profile'] and c['challenge_contexts']==plan['challenge_contexts_per_profile'] and c['generation_attempts']==plan['generation_attempt_cap'] and c['model_constructions']==1 and c['probes']==len(expected_probes)
  check(label+' complete planned coverage',coverage,c)
  encode_calls=c.get('counts',{}).get('encode_calls');active=c.get('active_seconds')
  check(label+' recorded execution within frozen bounds',nonnegative_int(encode_calls) and encode_calls<=plan['maximum_encoder_encode_calls_per_profile'] and finite_nonnegative(active) and active<=plan['maximum_wall_seconds_per_profile'],{'encode_calls':encode_calls,'active_seconds':active,'maximum_encode_calls':plan['maximum_encoder_encode_calls_per_profile'],'maximum_seconds':plan['maximum_wall_seconds_per_profile']})
 lp=read('baseline','PROBES.json');rp=read('candidate','PROBES.json')
 for label,probe in [('baseline',lp),('candidate',rp)]:
  check(label+' exact planned probe text inventory',probe.get('texts')==expected_probes)
  tokens=probe.get('token_ids');tokens_ok=isinstance(tokens,list) and len(tokens)==len(expected_probes) and all(isinstance(row,list) and bool(row) and all(nonnegative_int(t) for t in row) for row in tokens)
  check(label+' complete valid probe token records',tokens_ok)
  check(label+' planned probe dimensions/window',probe.get('max_seq_length')==256 and probe.get('embedding_shape')==[len(expected_probes),384])
 check('same predeclared probe texts',lp['texts']==rp['texts']);check('encoder tokenizer IDs identical',lp['token_ids']==rp['token_ids'])
 arrays={label:np.load(runs/label/'PROBE_EMBEDDINGS.npy',allow_pickle=False) for label in ['baseline','candidate']}
 for label,array in arrays.items():check(label+' actual probe array has planned dimensions',array.shape==(len(expected_probes),384))
 emb=numeric(arrays['baseline'],arrays['candidate'],tol['maximum_absolute'],tol['mean_absolute']);check('probe embeddings within frozen tolerances',emb['passed'],emb)
 left=read('baseline','CONTEXTS.json');right=read('candidate','CONTEXTS.json');lm={(x['case_id'],x['condition']):x for x in left};rm={(x['case_id'],x['condition']):x for x in right};check('same exact case/context keys',len(lm)==len(left)==len(rm)==len(right)==total_contexts and set(lm)==set(rm))
 for label,items,mapping in [('baseline',left,lm),('candidate',right,rm)]:check(label+' exact planned case/context keys',len(items)==len(mapping)==total_contexts and set(mapping)==expected_keys)
 rows=[]
 for key,l in lm.items():
  if key not in rm:continue
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
 for field in ['retrieved_order_and_text','added_chunk_records','passage_token_IDs','policy_decisions','answer_request_and_token_IDs']:check('all contexts '+field,all(r['discrete'][field] for r in rows),{'matching':sum(r['discrete'][field] for r in rows),'total':total_contexts})
 for field in ['query_vector','copy_vectors','scores','matrix','retrieval_scores']:check('all contexts numeric '+field,all(r['numeric'][field]['passed'] for r in rows))
 historical={}
 for label,cc in [('baseline',left),('candidate',right)]:
  original=[r for r in cc if r['historical'] is not None];historical[label]={'retrieval_contexts':len(original),'retrieved_ids_match':sum(r['historical']['retrieved_ids_match'] for r in original),'native_kept_match':sum(r['historical']['native_kept_match'] for r in original),'U_request_match':sum(r['historical']['U_request_match'] for r in original),'N_request_match':sum(r['historical']['N_request_match'] for r in original),'cutoff_exact_ties':sum(r['retrieval'].get('cutoff_exact_tie',False) for r in original),'cutoff_near_ties':sum(r['retrieval'].get('cutoff_near_tie',False) for r in original)}
 index={label:read(label,'FROZEN_INDEX_PROBE_COMPARISON.json') for label in ['baseline','candidate']}
 index_summary={}
 for label,records in index.items():
  summary,inventory_ok,values_ok=cached_index_checks(records,expected_cache,tol);index_summary[label]=summary
  check(label+' exact planned cached-index probe inventory',inventory_ok,summary)
  check(label+' valid cached-index deviations within frozen tolerances',values_ok,summary)
 status='PASS_BOUNDED_COMPATIBILITY' if not errors else 'FAIL_COMPATIBILITY'
 summary={'status':status,'checks':checks,'errors':errors,'comparator_version':2,'context_count':len(rows),'expected_context_count':total_contexts,'policies_per_context':len(plan['policies']),'answer_requests_compared':len(rows)*len(plan['policies']),'encoder_probe_texts':len(lp['texts']),'probe_embedding_difference':emb,'historical_comparison':historical,'frozen_index_probe_comparison':index_summary,'discrepancies':len(discrepancies),'generation_attempts':0,'answer_scope':'Same request bytes and Qwen token IDs/estimates, frozen prompt/options, synthetic status/transport validation only. No fresh Qwen service or semantic answer rerun.','filter_scope':'RAGDefender U/N/E/CN on predeclared subset, verified frozen full corpus embedding index reused with fresh query/copy encodings. No whole-corpus re-embedding or new TrustRAG stage-1 execution.','acceptance_scope':'Computational verification only; no deployment, human scientific/risk acceptance, all-advisory closure or whole-system guarantee inferred.'}
 out.mkdir(parents=True)
 for name,value in [('SUMMARY.json',summary),('CONTEXT_COMPARISONS.json',rows),('DISCREPANCIES.json',discrepancies)]: (out/name).write_text(json.dumps(value,indent=2)+'\n')
 return summary
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--runs',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();r=compare(a.runs,a.out);print(json.dumps({k:v for k,v in r.items() if k!='checks'},indent=2));raise SystemExit(0 if r['status']=='PASS_BOUNDED_COMPATIBILITY' else 1)
