"""Read frozen artifacts, check hashes and prepare a plan. No model imports/calls."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

STAGES = {
 'stability': ('legacy/results/filterflip_stability_run1/results.jsonl',80,'output/filterflip_poc/STABILITY_RESULT_REVIEW.md'),
 'mechanism': ('legacy/results/mechanism6_run1/results.jsonl',360,'output/filterflip_poc/mechanism6/RESULT_REVIEW.md'),
 'mitigation': ('legacy/results/mitigation_screen_run1/results.jsonl',160,'output/filterflip_poc/mitigation1/RESULT_REVIEW.md'),
 'early_encoder': ('legacy/results/embedding_check_run1/results.jsonl',240,'output/filterflip_poc/embedding_check/RESULT_REVIEW.md'),
 'primary_filter': ('output/filterflip_study_v1_filter/results/filter_run1/results.jsonl',531,'output/filterflip_study_v1_filter/RESULT_REVIEW.md'),
 'order': ('output/filterflip_study_v1_order_check/results/run1/results.jsonl',828,'output/filterflip_study_v1_order_check/ORDER_CHECK_REVIEW.md'),
 'later_encoder': ('output/filterflip_study_v1_config_check/results/run1/results.jsonl',108,'output/filterflip_study_v1_config_check/CONFIGURATION_REVIEW.md'),
 'second_generator': ('output/filterflip_study_v1_second_generator/results/run1/results.jsonl',72,'output/filterflip_study_v1_second_generator/SECOND_MODEL_REVIEW.md'),
 'component': ('output/filterflip_trustrag_component/results/run1/results.jsonl',36,'output/filterflip_trustrag_component/RESULT_REVIEW.md'),
}
def require(ok, message):
    if not ok: raise ValueError(message)
def digest(raw): return hashlib.sha256(raw).hexdigest()
def dump(path, data): path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def build(package, review, out):
    package,review,out=package.resolve(),review.resolve(),out.resolve()
    require(not out.exists(), 'Use a fresh output directory')
    require(not out.is_relative_to(package) and not out.is_relative_to(review), 'Output must be outside frozen inputs')
    ref=(package/'reference').resolve()
    manifest_raw=(package/'REFERENCE_SHA256.json').read_bytes()
    manifest=json.loads(manifest_raw);tracked={}
    def read(name):
        p=(ref/name).resolve(strict=True)
        require(p.is_relative_to(ref), 'Input path escapes reference')
        raw=p.read_bytes();sha=digest(raw)
        require(manifest.get(name)==sha,'Frozen hash mismatch: '+name)
        tracked[name]=sha
        if name.endswith('.jsonl'):return [json.loads(x) for x in raw.splitlines() if x.strip()]
        if name.endswith('.json'):return json.loads(raw)
        return raw.decode('utf-8')
    rows={};coverage={}
    for key,(source,expected,review_path) in STAGES.items():
        rows[key]=read(source);read(review_path)
        require(len(rows[key])==expected,'Unexpected coverage: '+key)
        coverage[key]={'result_file':source,'rows':expected,'review_file':review_path,
                       'status_counts':dict(Counter(str(x.get('status','not recorded')) for x in rows[key])),
                       'human_verification':'pending; source review text retains historical attribution'}
    summaries={key:read(name) for key,name in {
      'mechanism':'legacy/results/mechanism6_run1/summary.json',
      'mitigation':'legacy/results/mitigation_screen_run1/summary.json',
      'order':'output/filterflip_study_v1_order_check/results/run1/summary.json',
      'later_encoder':'output/filterflip_study_v1_config_check/results/run1/summary.json',
      'second_generator':'output/filterflip_study_v1_second_generator/results/run1/summary.json',
      'component':'output/filterflip_trustrag_component/results/run1/summary.json'}.items()}
    for name in ['output/filterflip_poc/mitigation1/PROTOCOL.md','output/filterflip_poc/mitigation1/policy.py',
                 'output/filterflip_poc/mitigation1/wrong_copy_manifest.json',
                 'output/filterflip_trustrag_component/ASSISTANT_SUPPORT_REVIEW.json',
                 'output/filterflip_study_v1_config_check/ASSISTANT_CONTEXT_REVIEW.json',
                 'output/filterflip_study_v1_second_generator/MODEL_COMPARISON_REVIEW.json']:
        read(name)
    # Check the already delivered review register against its immutable release manifest.
    register_raw=(review/'case_register.json').read_bytes()
    review_manifest=json.loads((review/'RELEASE_SHA256.json').read_text())
    require(review_manifest['case_register.json']==digest(register_raw),'Review register hash mismatch')
    register=json.loads(register_raw)
    require(len(register['cases'])==59 and register['counts']=={
       'Assistant-confirmed event':4,'Not a strict event':47,'Needs adjudication':8},'Review count mismatch')
    # Recompute designated-evidence and wrong-copy measures from raw selected IDs.
    policies=['unfiltered','native','ordered_native','collapse_only','collapse_native']
    totals={p:{'designated_contexts':0,'wrong_copy_contexts':0} for p in policies}
    gains=losses=0;seen=set()
    for row in rows['mitigation']:
        key=(row['case_id'],row['variant']);require(key not in seen,'Duplicate mitigation key');seen.add(key)
        require(row['status']=='ok','Incomplete mitigation row')
        docids={d['id'] for d in row['docs']}; require(len(docids)==5,'Unexpected mitigation context')
        for p in policies:
            result=row['policies'][p];kept=set(result['kept_ids']);removed=set(result['removed_ids'])
            require(kept.isdisjoint(removed) and kept|removed==docids,'Invalid survivor partition')
            evidence=bool(kept & set(row['designated_evidence_ids_in_context']))
            wrong=bool(kept & set(row['wrong_copy_ids_in_context']))
            require(evidence==result['designated_evidence_retained'] and wrong==result['wrong_copy_retained'],'Retention flag mismatch')
            totals[p]['designated_contexts']+=evidence;totals[p]['wrong_copy_contexts']+=wrong
        n=row['policies']['native']['designated_evidence_retained'];c=row['policies']['collapse_native']['designated_evidence_retained']
        gains+=bool(c and not n);losses+=bool(n and not c)
    for p in policies:
        require(totals[p]['designated_contexts']==sum(x['evidence_counts'][p] for x in summaries['mitigation']['table']),'Summary disagreement')
        require(totals[p]['wrong_copy_contexts']==sum(x['wrong_copy_context_counts'][p] for x in summaries['mitigation']['table']),'Wrong-copy summary disagreement')
    require((gains,losses)==(6,42),'Unexpected negative baseline')
    benign_conditions=['C','BE1','PE1','BN1','PN1']
    context_plan=[];seen=set()
    for row in rows['primary_filter']:
        if row['condition'] not in benign_conditions:continue
        key=(row['case_id'],row['condition']);require(key not in seen,'Duplicate primary context');seen.add(key)
        require(row['status']=='ok' and len(row['retrieved'])==5,'Invalid saved context')
        hashes=[]
        for passage in row['retrieved']:
            require(digest(passage['text'].encode())==passage['text_sha256'],'Passage hash mismatch')
            hashes.append(passage['text_sha256'])
        context_plan.append({'case_id':row['case_id'],'condition':row['condition'],'ordered_text_sha256':hashes,
                             'saved_native_kept_indices':row['kept_indices']})
    require(len(context_plan)==295,'Expected 59 x 5 contexts')
    ids={x['case_id'] for x in register['cases']}
    require({x['case_id'] for x in context_plan}==ids,'Case mismatch')
    generation_ids=sorted(x['case_id'] for x in register['cases'] if x['review_priority']<=3)
    challenge_ids=sorted(x['case_id'] for x in register['cases'] if x['review_priority'] in (1,3))
    require(len(generation_ids)==18 and len(challenge_ids)==10,'Review queue mismatch')
    out.mkdir(parents=True)
    dump(out/'SOURCE_MANIFEST.json',{'reference_manifest_sha256':digest(manifest_raw),'reference_files':tracked,
      'week4_register_sha256':digest(register_raw),'scope':'Selected-file checks, not full-package validation'})
    dump(out/'EVIDENCE_INVENTORY.json',{'schema':'filterflip-week6-inventory-v1','human_verified':False,
      'coverage':coverage,'primary_assistant_counts':register['counts'],
      'negative_mitigation':{'contexts':160,'policies':totals,'paired_gains':gains,'paired_losses':losses,
        'unit':'repeated development contexts; designated evidence only; no generator'},
      'mechanism':{'calls':summaries['mechanism']['completed_calls'],'order_groups':len(summaries['mechanism']['groups']),
        'target_sensitive':sum(x['target_order_sensitive'] for x in summaries['mechanism']['groups']),
        'removal_set_sensitive':sum(x['removal_set_order_sensitive'] for x in summaries['mechanism']['groups'])},
      'later_encoder_comparisons':summaries['later_encoder']['comparisons'],
      'logical_second_generator':summaries['second_generator']['planned_logical'],
      'distinct_second_generator':summaries['second_generator']['saved_distinct'],
      'new_research_calls':0})
    dump(out/'EXECUTION_PLAN.json',{'schema':'filterflip-week6-plan-v1','status':'protocol specified; implementation and challenge freeze pending; NOT EXECUTED',
      'benign_conditions':benign_conditions,'contexts':sorted(context_plan,key=lambda x:(x['case_id'],x['condition'])),
      'main_policies':['U','N','E','CN'],'ordering_diagnostic':'O; no generator',
      'near_duplicate_threshold':0.95,'generation_case_ids':generation_ids,'generation_conditions':['C','BN1','PN1'],
      'challenge_anchor_ids':challenge_ids,'challenge_per_anchor':['neutral_append','wrong_answer_append','instruction_append'],
      'challenge_texts_status':'not constructed, not reviewed, not frozen',
      'sentinel_and_timing_case_ids':['NanoNQ:test1009','NanoNQ:test929','NanoNQ:test826','NanoNQ:test2598'],
      'sentinel_and_timing_conditions':['C','BN1','PN1'],
      'limits':{'benign_contexts':295,'challenge_contexts_max':30,'main_logical_decisions_max':1300,
                'ordering_diagnostic_decisions_max':325,'native_calls_arithmetic_max':1029,'native_attempt_cap':1050,
                'generation_logical_max':336,'existing_generation_logical_reused':108,'fresh_generation_attempt_cap':228,
                'filter_wall_seconds':7200,'generation_wall_seconds':14400,'paid_api_calls':0},
      'required_before_execution':['Separate tested runner and manifest','Reviewed frozen challenge texts and rubric',
         'Pinned environment/model/request identity','Read-only source checks and fresh output','Sentinel native matches'],
      'no_threshold_sweep':True,'independent_human_verification':'pending'})
    dump(out/'VALIDATION.json',{'selected_source_files_checked':len(tracked),'all_selected_hashes_match':True,
      'mitigation_survivor_partitions_checked':160*len(policies),'benign_passage_hashes_checked':295*5,
      'plan_counts_verified':True,'research_calls':0,'reviewer_role':'assistant/developer','independent_review':'pending'})
    print(json.dumps({'sources':len(tracked),'benign_contexts':295,'generation_cases':18,'challenge_anchors':10,'new_research_calls':0}))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--package',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();build(a.package,a.review,a.out)
