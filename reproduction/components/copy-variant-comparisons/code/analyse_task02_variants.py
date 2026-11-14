#!/usr/bin/env python3
"""Offline paired analysis of frozen FilterFlip copy variants; no model/network calls."""
import argparse
from collections import Counter
import hashlib,json
from pathlib import Path

CONDITIONS=['C','BN1','BN2','PN1','PN2','BE1','BE2','PE1','PE2']
SECONDARY=['BN2','PN2','BE1','BE2','PE1','PE2']
PAIRS=[('BN1','BN2'),('PN1','PN2'),('BE1','BE2'),('PE1','PE2'),('BN1','BE1'),('BN2','BE2'),('PN1','PE1'),('PN2','PE2')]
PRIMARY=['C','BN1','PN1']
MODES=['unfiltered','filtered']
def require(condition,message):
    if not condition:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def read(path):return json.loads(path.read_text())
def lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def compact(text):return ' '.join(text.split())
def quote_present(chunks,quote):
    require(bool(compact(quote)),'Empty support quote')
    return any(compact(quote) in compact(x['text']) for x in chunks)
def copy_exposure(chunks):
    copies=[x for x in chunks if x['copied_from'] is not None]
    return dict(documents=len({x['record_id'] for x in copies}),chunks=len(copies),document_ids=sorted({x['record_id'] for x in copies}))
def text_sequence(chunks):return [x['text'] for x in chunks]
def pair_answers(left,right):
    if left['status']!='ok' or right['status']!='ok':return 'incomplete'
    return 'same_text' if left['answer']==right['answer'] else 'different_text'
def index_rows(rows,keys):
    index={(r[keys[0]] if len(keys)==1 else tuple(r[k] for k in keys)):r for r in rows}
    require(len(index)==len(rows),'Duplicate row identity: '+str(keys))
    return index
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in row)+' |\n' for row in rows)

def analyse(inputs,out):
    inputs=inputs.resolve();out=out.absolute()
    require(not out.exists(),'Use a new, separate output directory')
    require(not out.resolve().is_relative_to(inputs),'Output inside source inputs')
    source=read(inputs.parent/'SOURCE_MANIFEST.json')
    require(set(source)=={p.name for p in inputs.iterdir() if p.is_file()},'Snapshot inventory differs')
    for name,record in source.items():
        require(Path(name).name==name and sha(inputs/name)==record['sha256'],'Source snapshot changed: '+name)
    manifest=read(inputs/'case_manifest.json');cases={c['case_id']:c for c in manifest['cases']}
    require(len(cases)==len(manifest['cases'])==59,'Case denominator differs')
    retrieval=lines(inputs/'retrieval_contexts.jsonl');filters=lines(inputs/'filter_results.jsonl')
    refs=lines(inputs/'reference_answers.jsonl');calls=lines(inputs/'calls.jsonl');rep=read(inputs/'reproduction_logical.json')
    rr=index_rows(retrieval,['case_id','condition']);ff=index_rows(filters,['case_id','condition'])
    aa=index_rows(refs,['call_id']);cc=index_rows(calls,['call_id']);bb=index_rows(rep,['call_id'])
    require(set(rr)==set(ff)=={(c,co) for c in cases for co in CONDITIONS},'Context coverage differs')
    require(set(aa)==set(cc)==set(bb) and len(aa)==1062,'Logical answer coverage differs')
    require(all(x['status']=='ok' for x in refs),'Reference response incomplete')
    require(Counter(x['status'] for x in rep)=={'ok':1057,'truncated':5},'Reproduction status differs')
    require(len({x['request_sha256'] for x in calls})==706,'Distinct request denominator differs')
    for name,filename,group in [('retrieval','contexts.jsonl','retrieval_result_manifest.json'),('filter','results.jsonl','filter_result_manifest.json'),('answer','results.jsonl','answer_result_manifest.json')]:
        snapshot={'retrieval':'retrieval_contexts.jsonl','filter':'filter_results.jsonl','answer':'reference_answers.jsonl'}[name]
        require(sha(inputs/snapshot)==read(inputs/group)['files'][filename],name+' original result hash differs')
    frozen=read(inputs/'original_answer_frozen_manifest.json')
    require(sha(inputs/'calls.jsonl')==frozen['files']['calls.jsonl'],'Frozen request file differs')
    for filename,key in [('case_manifest.json','case_manifest.json'),('source_labels.json','support_labels_snapshot.json')]:
        require(sha(inputs/filename)==frozen['retrieval_inputs'][key],'Frozen retrieval input differs')
    require(sha(inputs/'filter_results.jsonl')==frozen['filter_inputs']['results/filter_run1/results.jsonl'],'Frozen filter input differs')
    human=read(inputs/'primary_human_reviews.json');current=read(inputs/'current_review_summary.json')
    hh={r['case_id']:r for r in human['records']};cur={r['case_id']:r for r in current['records']}
    require(set(hh)==set(cur)==set(cases) and all(x['human_reviewed'] for x in hh.values()),'Primary human coverage differs')
    recorded={x['case_id']:x for x in read(inputs/'primary_recorded.json')['cases']}
    for group in ['primary_filter_triage.json','primary_answer_triage.json']:
        require(all('BN2' not in str(x.get('review_scope','')) for x in read(inputs/group)['records']),'Reassess review scope')
    require(all(set(x['conditions'])==set(PRIMARY) for x in recorded.values()),'Primary saved packet scope differs')
    aggregate=[];metrics={};packets=[];requests={}
    for cid,case in cases.items():
        evidence={}
        for co in CONDITIONS:
            r,f=rr[cid,co],ff[cid,co]
            require(r['status']==f['status']=='ok','Failed retrieval/filter row')
            require(r['retrieved']==f['retrieved'] and len(r['retrieved'])==5,'Upstream context mismatch')
            chunks=r['retrieved'];kept=f['kept_indices'];removed=f['removed_indices']
            require(len(set(kept))==len(kept) and len(set(removed))==len(removed),'Duplicate filter index')
            require(set(kept).isdisjoint(removed) and set(kept)|set(removed)==set(range(5)),'Invalid filter partition')
            survivors=[chunks[i] for i in kept]
            require([x['chunk_id'] for x in survivors]==f['kept_chunk_ids'],'Survivor order mismatch')
            for ch in chunks:require(hashlib.sha256(ch['text'].encode()).hexdigest()==ch['text_sha256'],'Chunk text hash mismatch')
            exp=copy_exposure(chunks);remaining=copy_exposure(survivors)
            budget=0 if co=='C' else int(co[2])
            require(len(r['inserted_documents'])==budget,'Inserted budget differs')
            require(exp['documents']==r['retrieved_inserted_documents']==f['before']['inserted_documents'],'Exposed document count differs')
            require(exp['chunks']==r['retrieved_inserted_chunks'],'Exposed chunk count differs')
            require(remaining['documents']==f['after']['inserted_documents'],'Retained document count differs')
            for docs,when in [(chunks,'before'),(survivors,'after')]:
                require(quote_present(docs,case['support_quote'])==f[when]['quote_present'],'Quote flag differs')
                require(any(x['record_id']==case['target_document_id'] for x in docs)==f[when]['original_source_present'],'Target flag differs')
                require(any(x['record_id']==case['target_document_id'] or x['copied_from']==case['target_document_id'] for x in docs)==f[when]['source_or_copy_present'],'Source-family flag differs')
            m=dict(case_id=cid,dataset=case['dataset'],condition=co,inserted_documents=budget,
                   retrieved_copy_documents=exp['documents'],retrieved_copy_chunks=exp['chunks'],retained_copy_documents=remaining['documents'],retained_copy_chunks=remaining['chunks'],
                   original_source_before=f['before']['original_source_present'],original_source_after=f['after']['original_source_present'],
                   source_or_copy_before=f['before']['source_or_copy_present'],source_or_copy_after=f['after']['source_or_copy_present'],
                   quote_before=f['before']['quote_present'],quote_after=f['after']['quote_present'],removed_chunks=len(removed),
                   retrieval_cutoff_tie=r['retrieval']['cutoff_exact_tie'],filter_removal_exact_tie=f['trace']['removal_exact_tie'])
            m['clean_qualified_quote_loss_screen']=co.startswith('P') and ff[cid,'C']['after']['quote_present'] and exp['documents']>0 and m['quote_before'] and not m['quote_after']
            m['matching_background_quote_retained']=None if not co.startswith('P') else ff[cid,'B'+co[1:]]['after']['quote_present']
            aggregate.append(m);metrics[cid,co]=m
            responses={}
            for mode,docs in [('unfiltered',chunks),('filtered',survivors)]:
                callid=f'{cid}__{co}__{mode}';call=cc[callid];a,b=aa[callid],bb[callid]
                require(all(call[k]==a[k]==b[k] for k in ['call_id','case_id','condition','mode','request_sha256']),'Answer identity mismatch')
                require(call['request_sha256']==digest(call['request']),'Full request hash differs')
                require(call['chunk_ids']==[d['chunk_id'] for d in docs] and call['text_hashes']==[d['text_sha256'] for d in docs],'Call context linkage differs')
                user='Document:\n<document>\n'+'\n\n'.join(d['text'] for d in docs)+'\n</document>\n\nQuestion: '+case['question']
                require(call['request']['messages'][1]['content']==user,'Prompt text/order differs')
                if call['request_sha256'] in requests:require(requests[call['request_sha256']]==[a['answer'],b['answer'],b['status']],'Identical request produced inconsistent linked answer')
                requests[call['request_sha256']]=[a['answer'],b['answer'],b['status']]
                equal_primary=[p for p in PRIMARY if text_sequence(docs)==text_sequence(ff[cid,p]['retrieved'] if mode=='unfiltered' else [ff[cid,p]['retrieved'][i] for i in ff[cid,p]['kept_indices']])]
                responses[mode]=dict(call_id=callid,request_sha256=call['request_sha256'],
                    reference={k:a[k] for k in ['status','answer','first_call_id','response_reused']},
                    reproduction={k:b[k] for k in ['status','answer','result_origin','response_reused']},
                    exact_reference_text_match=a['answer']==b['answer'] if b['status']=='ok' else None,
                    identical_ordered_text_to_primary=equal_primary,
                    semantic_review=dict(reviewer=None,actual_review_date=None,assistance=None,answer_core=None,extra_claim_errors=None,context_support=None,rationale=None),
                    review_note='Primary context equality is an evidence-navigation aid, not transfer of acceptance to this variant or new response.')
            evidence[co]=dict(metrics=m,passages=[dict(ch,kept=i in kept) for i,ch in enumerate(chunks)],kept_indices=kept,removed_indices=removed,
                filter_trace=f['trace'],responses=responses)
        packets.append(dict(case=case,source_label=[x for x in read(inputs/'source_labels.json') if x['case_id']==cid][0],
            original_primary_human_record=hh[cid],current_primary_review_summary=cur[cid],
            primary_review_scope='Original saved C/BN1/PN1 assessments; no new variant or reproduced-answer review inferred.',
            conditions=evidence,
            secondary_condition_reviews=[dict(condition=co,reference_support=None,reference_unfiltered_core=None,reference_filtered_core=None,reproduced_support=None,reproduced_unfiltered_core=None,reproduced_filtered_core=None,strict_endpoint=None,background_qualified_endpoint=None,reviewer=None,actual_review_date=None,assistance=None,decisive_passages=None,disagreement=None,rationale=None) for co in SECONDARY]))
    condition_tables=[]
    for dataset in ['All','NanoNQ','NanoMSMARCO']:
        for co in CONDITIONS:
            rows=[m for m in aggregate if m['condition']==co and (dataset=='All' or m['dataset']==dataset)]
            ids={m['case_id'] for m in rows};responses=[bb[f'{cid}__{co}__{mode}'] for cid in ids for mode in MODES]
            refrows=[aa[x['call_id']] for x in responses]
            condition_tables.append(dict(dataset=dataset,condition=co,n_cases=len(rows),
                copy_document_exposure_histogram=dict(sorted(Counter(m['retrieved_copy_documents'] for m in rows).items())),
                copy_chunk_exposure_histogram=dict(sorted(Counter(m['retrieved_copy_chunks'] for m in rows).items())),
                retrieved_copy_documents=sum(m['retrieved_copy_documents'] for m in rows),retained_copy_documents=sum(m['retained_copy_documents'] for m in rows),
                quote_before=sum(m['quote_before'] for m in rows),quote_after=sum(m['quote_after'] for m in rows),
                quote_disappeared=sum(m['quote_before'] and not m['quote_after'] for m in rows),
                source_or_copy_after=sum(m['source_or_copy_after'] for m in rows),
                clean_qualified_quote_loss_screen=sum(m['clean_qualified_quote_loss_screen'] for m in rows),
                background_qualified_quote_screen=sum(m['clean_qualified_quote_loss_screen'] and m['matching_background_quote_retained'] for m in rows),
                reference_logical_status=dict(Counter(x['status'] for x in refrows)),reproduction_logical_status=dict(Counter(x['status'] for x in responses)),
                reproduction_distinct_requests=len({x['request_sha256'] for x in responses}),
                complete_exact_reference_text_matches=sum(x['status']=='ok' and x['answer']==aa[x['call_id']]['answer'] for x in responses),
                complete_different_reference_text=sum(x['status']=='ok' and x['answer']!=aa[x['call_id']]['answer'] for x in responses)))
    paired=[];paired_summaries=[]
    for left,right in PAIRS:
        pair_rows=[]
        for cid,case in cases.items():
            l,r=metrics[cid,left],metrics[cid,right]
            row=dict(case_id=cid,dataset=case['dataset'],left=left,right=right,
                quote_transition=('1' if l['quote_after'] else '0')+'->'+('1' if r['quote_after'] else '0'),
                retrieved_copy_document_delta=r['retrieved_copy_documents']-l['retrieved_copy_documents'],
                retained_copy_document_delta=r['retained_copy_documents']-l['retained_copy_documents'],
                input_text_sequence_same=text_sequence(rr[cid,left]['retrieved'])==text_sequence(rr[cid,right]['retrieved']),
                survivor_text_sequence_same=text_sequence([ff[cid,left]['retrieved'][i] for i in ff[cid,left]['kept_indices']])==text_sequence([ff[cid,right]['retrieved'][i] for i in ff[cid,right]['kept_indices']]),
                reference_answer_comparison={mode:pair_answers(aa[f'{cid}__{left}__{mode}'],aa[f'{cid}__{right}__{mode}']) for mode in MODES},
                reproduction_answer_comparison={mode:pair_answers(bb[f'{cid}__{left}__{mode}'],bb[f'{cid}__{right}__{mode}']) for mode in MODES},
                endpoint_verdict=None,semantic_review='pending')
            pair_rows.append(row);paired.append(row)
        for dataset in ['All','NanoNQ','NanoMSMARCO']:
            rows=[x for x in pair_rows if dataset=='All' or x['dataset']==dataset]
            paired_summaries.append(dict(left=left,right=right,dataset=dataset,n_cases=len(rows),
                quote_transitions=dict(Counter(x['quote_transition'] for x in rows)),
                input_text_sequences_same=sum(x['input_text_sequence_same'] for x in rows),survivor_text_sequences_same=sum(x['survivor_text_sequence_same'] for x in rows),
                retrieved_copy_document_delta_histogram=dict(sorted(Counter(x['retrieved_copy_document_delta'] for x in rows).items())),
                reference_answer_comparison={mode:dict(Counter(x['reference_answer_comparison'][mode] for x in rows)) for mode in MODES},
                reproduction_answer_comparison={mode:dict(Counter(x['reproduction_answer_comparison'][mode] for x in rows)) for mode in MODES}))
    review_coverage=dict(primary_cases_human_confirmed=59,primary_conditions=PRIMARY,primary_confirmation_attribution=human['confirmation'],
        secondary_case_conditions=59*6,secondary_logical_answers_per_panel=59*6*2,
        documented_secondary_condition_specific_human_reviews_in_inspected_records=0,
        qualification='Coverage inventory of supplied primary packets, triage, individual/joint/confirmation records; no inference that the user report of all 59 primary assessments reviewed all nine conditions.',
        computational_rerun_comparisons={n:read(inputs/n) for n in ['retrieval_rerun_comparison.json','filter_rerun_comparison.json']},
        computational_limit='Saved selected-field comparisons are technical reproduction evidence, not semantic support or answer acceptance.',
        new_reproduced_answers='Task-1 technical completion; human semantic review pending for new answers; exact matches do not assign labels.')
    status=dict(recorded_date='2026-10-31',task=2,implementation='complete',offline_execution='complete',new_model_calls=0,new_retrieval_calls=0,new_filter_calls=0,
        analysis='Recorded paired copy/type metrics complete; illustrative assistant interpretation supplied separately; human semantic review pending under task 7.',
        scientific_acceptance='Pending for secondary/new response outcomes; accepted primary and Week-6 conclusions unchanged.',
        cases=59,contexts=531,logical_answer_rows_per_panel=1062,unique_requests_per_panel=706,
        secondary_case_conditions=354,paired_contrasts=8,paired_case_records=len(paired),
        accepted_primary=dict(events=8,non_events=51,unresolved_classifications=0),R110='uncertain in accepted Week-6 record; unaffected',
        generation_disposition='No additional run needed: all reference requests exist and the reproduction queue is accounted for. Retain request 128 truncation; do not treat it as a scientific failure or retry it.',
        planned_task7_dependency='Shradha reviews supplied secondary and reproduced outcomes, with joint decisions for material disagreement. No messages sent.',
        task8_dependency='Integrate reviewed paired outcomes after task-7 returns. This task does not invent a secondary event rate.')
    out.mkdir(parents=True)
    for filename,obj in [('STATUS.json',status),('CONDITION_TABLES.json',condition_tables),('CONTEXT_METRICS.json',aggregate),('PAIRED_CASES.json',paired),('PAIRED_SUMMARIES.json',paired_summaries),('REVIEW_COVERAGE.json',review_coverage),('REVIEW_PACKET_INDEX.json',[dict(case_id=p['case']['case_id'],packet='cases/'+p['case']['case_id'].replace(':','_')+'.json',secondary_conditions=SECONDARY) for p in packets])]:save(out/filename,obj)
    (out/'cases').mkdir()
    for p in packets:save(out/'cases'/(p['case']['case_id'].replace(':','_')+'.json'),p)
    allrows=[x for x in condition_tables if x['dataset']=='All']
    report='''# Task 2 — secondary copy/type analysis

Recorded: 31 October 2026, Asia/Kolkata. Offline analysis of saved evidence; zero retrieval, filter or model calls.

All nine predeclared conditions already ran in the original study. The additional reproduction is now accounted for. This analysis retains all 59 selected cases (35 NanoNQ, 24 NanoMSMARCO), including clean failures and exposure misses. Conditions are repeated measures on those cases, not independent samples. Current primary findings remain 8 events / 51 non-events / 0 unresolved primary classifications; R110 remains uncertain in the separate Week-6 study.

## Inventory and review scope

531 saved contexts and native-filter decisions join to 1062 logical answer rows per answer panel and 706 distinct generation requests. The reference panel is complete. The combined-machine/operator reproduction has 1057 complete logical rows and five truncated links to one unique request (NanoNQ:test306 filtered C/PN1/PN2/PE1/PE2). Its full unique coverage is 705 complete, one truncated, zero pending. Requests 286 and 487 have preserved uncertain originals and separately authorized successful retries; original/retried 128 truncations remain preserved in task 1. No new run is required for these analyses.

The accepted human confirmation covers all 59 original primary assessments (C/BN1/PN1), with individual and eight-case joint decisions taking precedence. The inspected records provide no condition-specific human decisions for the six secondary variants. This is a review-coverage gap for 354 case-condition comparisons and 708 logical answers per panel, not a claim that the original cases remain human-unreviewed. Existing selected-field retrieval/filter rerun comparisons are computational evidence, not semantic adjudication. REVIEW_COVERAGE.json preserves their exact scope.

## Copy exposure and quotation tracking

Digits are inserted document budgets. A document can contribute several chunks or none to the top five. The exposure columns count distinct inserted documents actually retrieved, not chunks or guaranteed correct/supporting passages. B denotes the background-source control; it is not a semantic irrelevance label. P denotes copies of the selected answer source.

The quote metric checks the complete archived support quote in any one passage after collapsing whitespace, exactly as the historical screen. It does not classify all sufficient semantic support. Missing quotes can coexist with adequate alternative evidence; source identity or answer-name occurrence alone cannot establish support.

'''
    report+=table(['Condition','Cases with 0 / 1 / 2 copy documents retrieved','Quote before /59','Quote after /59','Quote disappeared','Clean-qualified quote-loss screen'],[(x['condition'],' / '.join(str(x['copy_document_exposure_histogram'].get(i,0)) for i in range(3)),x['quote_before'],x['quote_after'],x['quote_disappeared'],x['clean_qualified_quote_loss_screen'] if x['condition'].startswith('P') else 'n/a') for x in allrows])
    report+='''
The last column requires: clean filtered quote retained; at least one P-copy document retrieved; P quote present before filtering and absent afterward. It is a structural screening flag, not an attack-success count. The complete case list, per-dataset tables and background-qualified screens are in the JSON outputs. A positive flag does not check clean/unfiltered answer usability or alternative surviving support; a negative flag does not prove safety.

## Paired copy-count and copy-type changes

Every pair below contains the same 59 cases. “0→1” means the full quote is absent after filtering in the left condition and present in the right. “1→0” means the reverse. Neither transition alone establishes a semantic gain or loss.

'''
    ps=[x for x in paired_summaries if x['dataset']=='All']
    report+=table(['Left → right','0→0','0→1','1→0','1→1','Identical ordered input text','Identical ordered survivor text'],[(x['left']+' → '+x['right'],*(x['quote_transitions'].get(k,0) for k in ['0->0','0->1','1->0','1->1']),x['input_text_sequences_same'],x['survivor_text_sequences_same']) for x in ps])
    report+='''
Two inserted P copies do not yield a monotonic worsening in this frozen configuration. PN1→PN2 restores the full quote in eight cases and loses it in four; PE1→PE2 restores it in seven and loses it in three. Equal marginal totals can also hide reversals: BN1 and BN2 each retain 33 quotes, with five gains and five losses. BE1→BE2 has four gains and five losses.

Exact versus prefixed P copies changes quote retention in two cases at each budget. PN1→PE1 loses the full quote for test3090 and test3108; PN2→PE2 loses it for Targeted Victory (1045374) and test2721. These are not four automatically confirmed new events. All case IDs and transitions are retained in PAIRED_CASES.json.

This is a comparison of the full predefined variants, not an isolated causal estimate of adding a prefix. Copy 1 uses “Source excerpt.\\n”; copy 2 uses “Reference excerpt.\\n”. Exact copies have neither prefix. The complete source is copied before fixed-window chunking, so prefixes can change chunk boundaries, embeddings, rankings, exposure, displaced passages and downstream filter behavior. The two-copy arm adds a different second prefix in N variants. Different copy identities also remain subject to the documented hash-based tie rule. No setting, passage order, label or threshold was changed to favour an outcome.

## Paired answer text

The two answer panels are shown separately. Counts below are identical/different/incomplete **strings** among the 59 paired filtered answers. An incomplete pair is excluded from same/different counts. “Different” includes harmless wording changes and material changes; “same” can still be wrong. Shared request hashes reuse one response and are not independent confirmations.

'''
    report+=table(['Pair','Reference: same / different / incomplete','Reproduction: same / different / incomplete'],[(x['left']+' → '+x['right'],*(' / '.join(str(x[k]['filtered'].get(label,0)) for label in ['same_text','different_text','incomplete']) for k in ['reference_answer_comparison','reproduction_answer_comparison'])) for x in ps])
    report+='\n### Reproduction versus reference by condition\n\n'
    report+=table(['Condition','Complete logical rows /118','Truncated links','Exact reference strings','Different complete strings'],[(x['condition'],x['reproduction_logical_status'].get('ok',0),x['reproduction_logical_status'].get('truncated',0),x['complete_exact_reference_text_matches'],x['complete_different_reference_text']) for x in allrows])
    report+='''
These counts overlap across conditions when the full generation request is identical. They must not be summed as independent requests or converted to accuracy/event rates. Task 1 retains the unique-request denominators; each per-case packet supplies request hashes, reference and reproduction answers, actual surviving text, and original attribution.

## Review and acceptance boundary

The six secondary variants have blank per-case human support, answer, endpoint, reviewer/date and disagreement fields in cases/. Original primary decisions are included for context and remain unchanged. Exact ordered-context matches to a primary arm are navigation aids, never silent transfer of acceptance to a secondary or newly reproduced answer. Human review must inspect every survivor, the clean prerequisite and exposed unfiltered condition, and the matching background control. Preserve accepted core/mixed interpretation and its original scope/post-outcome provenance; disclose any proposed extension to a new comparison, and obtain joint agreement where material. Do not mark a case as reviewed merely because a string or quote matches.

Task 2 implementation and offline paired analysis are complete. Human semantic review and scientific acceptance of the secondary/new outcomes remain pending under task 7; integrated reviewed outcome analysis follows under task 8. The companion CASE_INTERPRETATIONS.md supplies three explicitly assistant-authored examples, not a replacement 59-case adjudication. No teammate message is sent. Bigger datasets and new mitigation research remain deferred.
'''
    (out/'REPORT.md').write_text(report)
    validation=dict(status='PASS',generation_calls=0,source_snapshots_verified=len(source),cases=59,contexts=531,logical_rows_each_panel=1062,unique_requests=706,
        all_filter_partitions_checked=True,all_chunk_text_hashes_checked=True,all_request_hashes_and_context_joins_checked=True,
        independently_recomputed_quote_and_exposure_flags=True,primary_human_attribution_preserved=True,
        secondary_review_fields_blank=True,paired_case_records=len(paired),scientific_acceptance='not established by computational validation')
    save(out/'VALIDATION.json',validation)
    save(out/'SHA256_MANIFEST.json',{str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file()})
    return validation

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();print(json.dumps(analyse(a.inputs,a.out),indent=2))
if __name__=='__main__':main()
