#!/usr/bin/env python3
"""Offline Task 8 aggregation of frozen evidence and accepted human review. No models/network."""
from pathlib import Path
import argparse,collections,copy,hashlib,json,zipfile
PAIRS=[('BN1','BN2'),('PN1','PN2'),('BE1','BE2'),('PE1','PE2'),('BN1','BE1'),('BN2','BE2'),('PN1','PE1'),('PN2','PE2')]
SECONDARY=['BN2','PN2','BE1','BE2','PE1','PE2']
FIELDS=[f'{arm}_{field}' for arm in ['unfiltered','filtered'] for field in ['context_support','core_usable','full_complete']]+['strict_endpoint','background_qualified_endpoint']
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda d:json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
count=lambda values:dict(sorted(collections.Counter('missing' if x is None else str(x) for x in values).items()))
def flatten(d):return d.get('records',[])+d.get('answer_groups',[])+d.get('run_reviews',[])
def transition(left,right,incomplete=False):
 if left is None or right is None:return {'state':'not_reviewed','left':left,'right':right}
 if left=='not_applicable' or right=='not_applicable':return {'state':'not_applicable','left':left,'right':right}
 if incomplete:return {'state':'incomplete_pair','left':left,'right':right}
 if left=='uncertain' or right=='uncertain':return {'state':'uncertain_pair','left':left,'right':right}
 return {'state':'complete_pair','left':left,'right':right,'transition':str(left)+' -> '+str(right)}
def summarize_transitions(ts):
 return {'planned_pairs':len(ts),'states':count(t['state'] for t in ts),'complete_value_transitions':count(t['transition'] for t in ts if t['state']=='complete_pair'),'uncertain_value_transitions':count(str(t['left'])+' -> '+str(t['right']) for t in ts if t['state']=='uncertain_pair')}
def strict_history(d):
 value=d['current_primary_review_summary']['current_assessment']['recorded_value']
 if value in ['yes','event']:return 'met'
 if value in ['no','non-event','Not a strict event']:return 'not_met'
 raise ValueError('Unknown historical endpoint value '+str(value))
def verify_sources(packet):
 manifest=json.loads((packet/'SOURCE_MANIFEST.json').read_text());archives={}
 for relative,m in manifest.items():
  f=packet/relative
  if sha(f.read_bytes())!=m['sha256']:raise ValueError('Source hash mismatch: '+relative)
  if m['kind']=='unchanged_archive_member':
   archive=m['archive']
   if archive not in archives:archives[archive]=zipfile.ZipFile(packet/archive)
   if archives[archive].read(m['member'])!=f.read_bytes():raise ValueError('Source archive/member mismatch '+relative)
 for z in archives.values():z.close()
 return len(manifest)
def analyse(packet,out):
 packet=Path(packet);out=Path(out)
 if out.exists():raise FileExistsError('Refusing existing analysis output '+str(out))
 nsource=verify_sources(packet);read=lambda f:json.loads((packet/f).read_text())
 joint=read('inputs/acceptance/JOINT_ADJUDICATION.json')
 if joint['accepted_return']['sha256']!='8e833c591fc001c22b0fabf0b7c8b9f9b91a9edb155b1cc18f270008d8dfd1f6' or joint['review_type']!='joint_human_review':raise ValueError('Unexpected review authority')
 index=read('inputs/review/RETURN_FORM_INDEX.json');allrows=[];formfiles={}
 for relative,ids in index.items():
  rows=flatten(read('inputs/returned/'+relative))
  if [r['record_id'] for r in rows]!=ids:raise ValueError('Review inventory mismatch '+relative)
  allrows.extend(rows)
  for r in rows:formfiles[r['record_id']]='inputs/returned/'+relative
 reviews={r['record_id']:r for r in allrows}
 if len(reviews)!=len(allrows) or len(reviews)!=1113:raise ValueError('Duplicate/missing review ID')
 catalog={r['record_id']:r for r in read('inputs/review/REVIEW_RECORD_CATALOG.json')}
 for rid,r in reviews.items():
  if any(r.get(k)!=v for k,v in catalog[rid].items()):raise ValueError('Immutable review field mismatch '+rid)
  if r['human']['review_status'] not in ['reviewed','evidence_incomplete']:raise ValueError('Review not completed '+rid)
 cases={d['case']['case_id']:d for d in [json.loads(f.read_text()) for f in sorted((packet/'inputs/task02/cases').glob('*.json'))]}
 new=read('inputs/task01/NEW_RESPONSE_REVIEW_PACKET.json')['records'];newbyhash={r['request_sha256']:r for r in new};comparison=read('inputs/task01/REPRODUCTION_COMPARISON_INDEX.json')
 if len(cases)!=59 or len(newbyhash)!=579 or len(comparison)!=706:raise ValueError('Unexpected source coverage')
 for r in new:
  if sha(canon(r['request']))!=r['request_sha256']:raise ValueError('Frozen request mismatch')
 def review_ref(r,panel,field):return {'file':formfiles[r['record_id']],'record_id':r['record_id'],'panel':panel,'field':field}
 def panel_view(cid,co,panel):
  d=cases[cid];c=d['conditions'][co];values={k:None for k in FIELDS};refs={k:None for k in FIELDS}
  if co in SECONDARY:
   r=reviews['SECONDARY:'+cid+':'+co]
   for k in FIELDS:values[k]=r[panel][k];refs[k]=review_ref(r,panel,k)
  elif panel=='reproduction':
   for arm in ['unfiltered','filtered']:
    a=c['responses'][arm];rid='R1:'+a['request_sha256']
    if rid not in reviews:continue
    r=reviews[rid]
    if a['call_id'] not in [l['call_id'] for l in r['logical_links']]:raise ValueError('Unbound primary response '+a['call_id'])
    for field,jfield in [('context_support','context_support'),('core_usable','core_usable'),('full_complete','full_frozen_answer_complete')]:
     k=arm+'_'+field;values[k]=r['judgment'][jfield];refs[k]=review_ref(r,'judgment',jfield)
  if co=='PN1':
   if panel=='reference':
    values['strict_endpoint']=strict_history(d);refs['strict_endpoint']={'file':'inputs/task02/cases/'+cid.replace(':','_')+'.json','field':'current_primary_review_summary.current_assessment','scope':'accepted historical primary endpoint; earlier attribution retained'}
   elif 'R1CASE:'+cid in reviews:
    r=reviews['R1CASE:'+cid]
    for k in ['strict_endpoint','background_qualified_endpoint']:values[k]=r['judgment'][k];refs[k]=review_ref(r,'judgment',k)
  if co.startswith('B'):
   for k in ['strict_endpoint','background_qualified_endpoint']:values[k]='not_applicable'
  status={arm:c['responses'][arm][panel]['status'] for arm in ['unfiltered','filtered']}
  return {'values':values,'review_refs':refs,'technical_status':status}
 def incomplete_for(cid,co,panel,field):
  conditions=cases[cid]['conditions']
  if field.endswith('endpoint'):
   checks=[('C','filtered'),(co,'unfiltered'),(co,'filtered')]
   if field=='background_qualified_endpoint' and co.startswith('P'):checks.append(({'PN1':'BN1','PN2':'BN2','PE1':'BE1','PE2':'BE2'}[co],'filtered'))
  else:checks=[(co,'unfiltered' if field.startswith('unfiltered_') else 'filtered')]
  return [conditions[c]['responses'][arm]['request_sha256'] for c,arm in checks if conditions[c]['responses'][arm][panel]['status']!='ok']
 # Request-level semantic differences, never multiplied into independent trials.
 repro=[]
 for x in new:
  r=reviews['R1:'+x['request_sha256']]
  repro.append({'record_id':r['record_id'],'case_id':r['case_id'],'dataset':r['case_id'].split(':')[0],'request_sha256':x['request_sha256'],'technical_status':x['status'],'exact_reference_text_match':x['exact_reference_text_match'],'judgment':r['judgment'],'logical_links':x['logical_conditions'],'review_ref':{'file':formfiles[r['record_id']],'record_id':r['record_id']},'reference_answer':x['reference_answer'],'reproduced_answer':x['reproduced_answer'],'source_qualification':x['source_qualification'],'rationale':r['human']['rationale'],'flag_note':r['human']['disagreement']})
 repro_summary={}
 for stratum in ['all','NanoNQ','NanoMSMARCO']:
  rr=[r for r in repro if stratum=='all' or r['dataset']==stratum]
  repro_summary[stratum]={'unique_requests':len(rr),'logical_links':sum(len(r['logical_links']) for r in rr),'technical_status':count(r['technical_status'] for r in rr),'text_equality':count(r['exact_reference_text_match'] for r in rr),'semantic_difference':count(r['judgment']['semantic_difference_from_reference'] for r in rr),'answer_category':count(r['judgment']['answer_category'] for r in rr),'context_support':count(r['judgment']['context_support'] for r in rr),'core_usable':count(r['judgment']['core_usable'] for r in rr),'full_complete':count(r['judgment']['full_frozen_answer_complete'] for r in rr),'changed_string_semantic_labels':count(r['judgment']['semantic_difference_from_reference'] for r in rr if r['exact_reference_text_match'] is False)}
 primary=[]
 for cid in cases:
  if 'R1CASE:'+cid not in reviews:continue
  r=reviews['R1CASE:'+cid];bad=incomplete_for(cid,'PN1','reproduction','strict_endpoint');original=strict_history(cases[cid])
  primary.append({'case_id':cid,'dataset':cid.split(':')[0],'reference_historical_strict':original,'reproduction_review':r['judgment'],'incomplete_request_hashes':list(dict.fromkeys(bad)),'strict_pair':transition(original,r['judgment']['strict_endpoint'],bool(bad)),'review_ref':{'file':formfiles[r['record_id']],'record_id':r['record_id']},'rationale':r['human']['rationale'],'flag_note':r['human']['disagreement']})
 primary_summary={'accepted_original':count(strict_history(d) for d in cases.values()),'new_endpoint_records':len(primary),'new_literal_strict':count(r['reproduction_review']['strict_endpoint'] for r in primary),'new_literal_background':count(r['reproduction_review']['background_qualified_endpoint'] for r in primary),'paired_with_historical_reference':summarize_transitions([r['strict_pair'] for r in primary]),'new_primary_endpoint_not_assessed_in_task07':sorted(set(cases)-{r['case_id'] for r in primary}),'scope':'Original 59 and new reviewed 35 are distinct denominators. No full new 59-case endpoint classification or automatic historical transfer.'}
 # All eight case-paired copy contrasts, preserving missing primary per-answer review coverage.
 pairs=[]
 for cid,d in cases.items():
  for left,right in PAIRS:
   lc=d['conditions'][left];rc=d['conditions'][right];lm=lc['metrics'];rm=rc['metrics']
   structural={'retrieved_copy_document_delta':rm['retrieved_copy_documents']-lm['retrieved_copy_documents'],'retained_copy_document_delta':rm['retained_copy_documents']-lm['retained_copy_documents'],'retrieved_copy_documents':[lm['retrieved_copy_documents'],rm['retrieved_copy_documents']],'retained_copy_documents':[lm['retained_copy_documents'],rm['retained_copy_documents']],'inserted_documents':[lm['inserted_documents'],rm['inserted_documents']],'same_ordered_input_text':[p['text'] for p in lc['passages']]==[p['text'] for p in rc['passages']],'same_ordered_survivor_text':[p['text'] for p in lc['passages'] if p['kept']]==[p['text'] for p in rc['passages'] if p['kept']],'quote_retention_transition':str(lm['quote_after'])+' -> '+str(rm['quote_after'])}
   for panel in ['reference','reproduction']:
    lv=panel_view(cid,left,panel);rv=panel_view(cid,right,panel);ts={}
    for field in FIELDS:
     bad=incomplete_for(cid,left,panel,field)+incomplete_for(cid,right,panel,field);t=transition(lv['values'][field],rv['values'][field],bool(bad));t['incomplete_request_hashes']=list(dict.fromkeys(bad));t['left_review_ref']=lv['review_refs'][field];t['right_review_ref']=rv['review_refs'][field];ts[field]=t
    pairs.append({'case_id':cid,'dataset':cid.split(':')[0],'left':left,'right':right,'panel':panel,'structural':structural,'fields':ts})
 pair_summary=[]
 for left,right in PAIRS:
  for panel in ['reference','reproduction']:
   for stratum in ['all','NanoNQ','NanoMSMARCO']:
    pp=[r for r in pairs if r['left']==left and r['right']==right and r['panel']==panel and (stratum=='all' or r['dataset']==stratum)]
    pair_summary.append({'left':left,'right':right,'panel':panel,'stratum':stratum,'planned_case_pairs':len(pp),'same_ordered_input':sum(r['structural']['same_ordered_input_text'] for r in pp),'same_ordered_survivors':sum(r['structural']['same_ordered_survivor_text'] for r in pp),'retrieved_document_delta':count(r['structural']['retrieved_copy_document_delta'] for r in pp),'retained_document_delta':count(r['structural']['retained_copy_document_delta'] for r in pp),'fields':{f:summarize_transitions([r['fields'][f] for r in pp]) for f in FIELDS}})
 conditions=[]
 for co in ['C','BN1','BN2','PN1','PN2','BE1','BE2','PE1','PE2']:
  for stratum in ['all','NanoNQ','NanoMSMARCO']:
   ds=[d for cid,d in cases.items() if stratum=='all' or cid.startswith(stratum+':')];metrics=[d['conditions'][co]['metrics'] for d in ds]
   row={'condition':co,'stratum':stratum,'case_contexts':len(ds),'inserted_document_budget':metrics[0]['inserted_documents'],'retrieved_copy_documents':count(m['retrieved_copy_documents'] for m in metrics),'retained_copy_documents':count(m['retained_copy_documents'] for m in metrics),'zero_copy_exposure':sum(m['retrieved_copy_documents']==0 for m in metrics),'retrieved_source_or_copy':sum(m['source_or_copy_before'] for m in metrics),'retained_source_or_copy':sum(m['source_or_copy_after'] for m in metrics),'quote_retained_screen_only':sum(m['quote_after'] for m in metrics)}
   row['panels']={}
   for panel in ['reference','reproduction']:
    views=[panel_view(d['case']['case_id'],co,panel) for d in ds];row['panels'][panel]={'reviewed_field_values':{f:count(v['values'][f] for v in views) for f in FIELDS},'incomplete_filtered_logical_answers':sum(v['technical_status']['filtered']!='ok' for v in views)}
   conditions.append(row)
 # Cross-record field differences are reported; never silently harmonized into a new human judgment.
 observations=collections.defaultdict(list)
 def observe(group,value,ref):
  if value is not None:observations[group].append({'value':value,'ref':ref})
 for cid,d in cases.items():
  for co,c in d['conditions'].items():
   for arm,a in c['responses'].items():
    if co in SECONDARY:
     r=reviews['SECONDARY:'+cid+':'+co]
     for panel in ['reference','reproduction']:
      for field in ['context_support','core_usable','full_complete']:observe((panel,a['request_sha256'],field),r[panel][arm+'_'+field],review_ref(r,panel,arm+'_'+field))
 for r in repro:
  for field,jfield in [('context_support','context_support'),('core_usable','core_usable'),('full_complete','full_frozen_answer_complete')]:observe(('reproduction',r['request_sha256'],field),r['judgment'][jfield],{**r['review_ref'],'panel':'judgment','field':jfield})
 # TrustRAG's fresh U/T panel is internally paired; historical native arms stay explicitly historical.
 t3cases=[json.loads(f.read_text()) for f in sorted((packet/'inputs/task03/cases').glob('*.json'))];contexts=[];endpoints=[];t3unique=read('inputs/task03/UNIQUE_RESULTS.json');unique={r['request_sha256']:r for r in t3unique};freshgroups=collections.defaultdict(list)
 for d in t3cases:
  cid=d['case']['case_id'];er=reviews['T3CASE:'+cid];native_new=reviews.get('R1CASE:'+cid);original=strict_history(cases[cid])
  endpoints.append({'case_id':cid,'dataset':cid.split(':')[0],'native_historical_strict':original,'native_new_strict':native_new['judgment']['strict_endpoint'] if native_new else None,'TrustRAG_review':er['judgment'],'historical_vs_T':transition(original,er['judgment']['strict_endpoint']),'new_native_vs_T':transition(native_new['judgment']['strict_endpoint'] if native_new else None,er['judgment']['strict_endpoint']),'review_ref':{'file':formfiles[er['record_id']],'record_id':er['record_id']},'rationale':er['human']['rationale'],'flag_note':er['human']['disagreement']})
  for c in d['contexts']:
   co=c['condition'];r=reviews['T3CONTEXT:'+cid+':'+co];labels=r['judgment'];n=cases[cid]['conditions'][co];record={'case_id':cid,'dataset':cid.split(':')[0],'condition':co,'retrieved_passages':len(c['retrieved']),'T_kept':len(c['T_native_indices']),'R_kept':len(c['prior_ragdefender_survivor_indices']),'same_native_R_and_T_ordered_survivors':c['T_native_indices']==c['prior_ragdefender_survivor_indices'],'judgment':labels,'review_ref':{'file':formfiles[r['record_id']],'record_id':r['record_id']},'rationale':r['human']['rationale'],'flag_note':r['human']['disagreement'],'pairs':{}}
   for key in ['sufficient_support','core_usable','full_complete']:record['pairs'][key]=transition(labels['U_'+key],labels['T_'+key])
   record['actual_retrieved_copies']=n['metrics']['retrieved_copy_documents'];record['answers']={}
   for arm in ['U','T']:
    a=c[arm]['new_result'];rid='T3:'+a['request_sha256'];ar=reviews[rid];texts=[x['text'] for x in c['retrieved']] if arm=='U' else c['T_output_texts'];req=copy.deepcopy(new[0]['request']);req['messages'][1]['content']='Document:\n<document>\n'+'\n\n'.join(texts)+'\n</document>\n\nQuestion: '+d['case']['question']
    if sha(canon(req))!=a['request_sha256'] or unique[a['request_sha256']]['answer']!=a['answer']:raise ValueError('Task3 request/answer mismatch')
    freshgroups[a['request_sha256']].append(a['logical_id']);record['answers'][arm]={'request_sha256':a['request_sha256'],'answer':a['answer'],'record_id':rid,'logical_id':a['logical_id']}
    for field,jfield in [('sufficient_support','context_support'),('core_usable','core_usable'),('full_complete','full_frozen_answer_complete')]:
     observe(('trustrag',a['request_sha256'],jfield),ar['judgment'][jfield],review_ref(ar,'judgment',jfield));observe(('trustrag',a['request_sha256'],jfield),labels[arm+'_'+field],review_ref(r,'judgment',arm+'_'+field))
   for panel in ['reference','reproduction']:
    native=n['responses']['filtered'];record['native_'+panel]={'request_sha256':native['request_sha256'],'answer':native[panel]['answer'],'same_request_as_T':native['request_sha256']==record['answers']['T']['request_sha256'],'same_answer_as_T':native[panel]['answer']==record['answers']['T']['answer'],'origin':native[panel].get('result_origin','historical_reference')}
   contexts.append(record)
 consistency=[]
 for (panel,h,field),oo in observations.items():
  if len({str(x['value']) for x in oo})>1:consistency.append({'panel':panel,'request_sha256':h,'field':field,'observations':oo,'disposition':'Original accepted records preserved. Aggregation uses each named source role; no inferred harmonized label.'})
 trust_summaries=[]
 for condition in ['all','C','BN1','PN1']:
  for stratum in ['all','NanoNQ','NanoMSMARCO']:
   cc=[r for r in contexts if (condition=='all' or r['condition']==condition) and (stratum=='all' or r['dataset']==stratum)]
   trust_summaries.append({'condition':condition,'stratum':stratum,'context_pairs':len(cc),'U_to_T':{f:summarize_transitions([r['pairs'][f] for r in cc]) for f in ['sufficient_support','core_usable','full_complete']},'U_core':count(r['judgment']['U_core_usable'] for r in cc),'T_core':count(r['judgment']['T_core_usable'] for r in cc),'U_support':count(r['judgment']['U_sufficient_support'] for r in cc),'T_support':count(r['judgment']['T_sufficient_support'] for r in cc),'empty_T_contexts':sum(r['T_kept']==0 for r in cc),'R_T_same_ordered_survivors':sum(r['same_native_R_and_T_ordered_survivors'] for r in cc),'same_R_T_request':sum(r['native_reference']['same_request_as_T'] for r in cc)})
 trust_summary={'case_count':len(t3cases),'context_count':len(contexts),'distinct_fresh_responses':len(freshgroups),'logical_positions':sum(len(x) for x in freshgroups.values()),'strict_endpoint':count(r['TrustRAG_review']['strict_endpoint'] for r in endpoints),'background_endpoint':count(r['TrustRAG_review']['background_qualified_endpoint'] for r in endpoints),'historical_native_vs_new_T':summarize_transitions([r['historical_vs_T'] for r in endpoints]),'new_native_vs_new_T':summarize_transitions([r['new_native_vs_T'] for r in endpoints]),'support_and_answer_pairs':trust_summaries,'scope':'Stage 1 plus frozen answering, 12 selected cases. Native historical/reproduction answers are not a fresh jointly generated native-filter control panel.'}
 # Conservative field-level sensitivity: withhold only the exact conflicting field, never change source labels.
 affected_refs={canon(o['ref']) for g in consistency for o in g['observations']};sensitivity=[]
 for left,right in PAIRS:
  for panel in ['reference','reproduction']:
   pp=[r for r in pairs if r['left']==left and r['right']==right and r['panel']==panel];summaries={};affected_pairs=[]
   for field in FIELDS:
    ts=[]
    for r in pp:
     t=copy.deepcopy(r['fields'][field]);conflict=any(ref is not None and canon(ref) in affected_refs for ref in [t['left_review_ref'],t['right_review_ref']])
     if conflict:
      affected_pairs.append({'case_id':r['case_id'],'field':field,'literal_state':t['state']})
      if t['state']=='complete_pair':t['state']='cross_record_field_difference';t.pop('transition',None)
     ts.append(t)
    summaries[field]=summarize_transitions(ts)
   sensitivity.append({'left':left,'right':right,'panel':panel,'affected_fields':affected_pairs,'fields':summaries,'scope':'Only inconsistent field observations withheld; original labels are unchanged. Endpoint fields are not harmonized or altered.'})
 # Carryover application results stay outside primary/TrustRAG case totals.
 live_queue=read('inputs/additional_live/ADDITIONAL_LIVE_REVIEW_QUEUE.json')['entries'];live=[];exposed=0;markeranswers=0;instruction_outputs=0;falseclaims=[]
 with zipfile.ZipFile(packet/'inputs/additional_live/FilterFlip_Review_Demo_v2_Runs.zip') as z:
  for entry in live_queue:
   runid=entry['run_id'];r=json.loads(z.read('FilterFlip_Review_Demo_v2_Runs/'+runid+'/result.json'));rr=reviews['LIVERUN:'+runid];live.append({'run_id':runid,'mode':r['mode'],'case_id':r['case_id'],'judgment':rr['judgment'],'review_ref':{'file':formfiles[rr['record_id']],'record_id':rr['record_id']}})
   for co,c in r['conditions'].items():
    for policy,a in c['answers'].items():
     if co=='instruction_append':
      instruction_outputs+=1;supplied='FILTERFLIP_TEST_ONLY' in a['request']['messages'][1]['content'];exposed+=supplied;markeranswers+=supplied and 'FILTERFLIP_TEST_ONLY' in a['text']
     if co=='wrong_answer_append' and policy=='CN':
      rid='LIVE:'+sha(canon({'case_id':r['case_id'],'request_sha256':a['request_sha256'],'answer':a['text']}));falseclaims.append({'run_id':runid,'case_id':r['case_id'],'policy':policy,'answer_category':reviews[rid]['judgment']['answer_category'],'record_id':rid})
 live_summary={'runs':len(live),'logical_answers':76,'answer_groups':18,'instruction_outputs':instruction_outputs,'instruction_marker_exposed_outputs':exposed,'literal_marker_matches_in_exposed_answers':markeranswers,'CN_false_claim_runs':falseclaims,'scope':'Older carryover only, exact 19 run IDs; no pooling with Task 6 fresh v2.4 jobs, primary cases or independent repeated-trial claim.'}
 quality={'cross_record_field_difference_groups':consistency,'exact_text_but_non_none_semantic_labels':[{'record_id':r['record_id'],'case_id':r['case_id'],'literal_text_equal':True,'source_semantic_label':r['judgment']['semantic_difference_from_reference'],'review_ref':r['review_ref']} for r in repro if r['exact_reference_text_match'] is True and r['judgment']['semantic_difference_from_reference'] not in ['none',None]],'disposition':'Preserve returned labels, compare changed strings separately, and use field-specific conservative sensitivity. No assistant repair or new scientific adjudication.'}
 outputs={'REVIEW_QUALITY_NOTES.json':quality,'REPRODUCTION_RECORDS.json':repro,'REPRODUCTION_SUMMARY.json':repro_summary,'MATERIAL_DIFFERENCES.json':[r for r in repro if r['judgment']['semantic_difference_from_reference']=='material'],'PRIMARY_COMPARISON.json':primary,'PRIMARY_SUMMARY.json':primary_summary,'COPY_PAIR_RECORDS.json':pairs,'COPY_PAIR_SUMMARIES.json':pair_summary,'CONDITION_SUMMARIES.json':conditions,'TRUSTRAG_CONTEXTS.json':contexts,'TRUSTRAG_ENDPOINTS.json':endpoints,'TRUSTRAG_SUMMARY.json':trust_summary,'CROSS_RECORD_DIFFERENCES.json':consistency,'COPY_PAIR_SENSITIVITY.json':sensitivity,'ADDITIONAL_LIVE_RUNS.json':live,'ADDITIONAL_LIVE_SUMMARY.json':live_summary,'ANALYSIS_STATUS.json':{'task':8,'computation':'complete','source_records_verified':nsource,'new_model_calls':0,'new_scientific_judgments':0,'human_source':'Task 7 joint human review by Shradha and Suresh without AI assistance for those reviews; earlier attribution unchanged','derived_analysis':'Code-generated descriptive aggregation, not an additional human review or new scientific acceptance','accepted_primary':'8/51/0 unchanged','R110':'uncertain unchanged','raw_flag_notes_preserved':150,'cross_record_differences':len(consistency),'task09_started':False}}
 out.mkdir(parents=True)
 for f,d in outputs.items():(out/f).write_text(json.dumps(d,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 return {'source_records':nsource,'reproduction_requests':len(repro),'copy_case_panel_pairs':len(pairs),'trust_contexts':len(contexts),'cross_record_differences':len(consistency)}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--packet',type=Path,default=Path(__file__).resolve().parent.parent);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();print(json.dumps(analyse(a.packet,a.out),indent=2))
if __name__=='__main__':main()
