"""Record assistant interpretation of the completed fixed-subset comparison.
Judgments are explicit and refer to the actual saved contexts; not a string-match scorer.
"""
from run_second import *
from datetime import datetime,timezone
ASSESSMENTS={
'NanoNQ:test1037':('baseline_failure','baseline_failure','Both clean filtered models abstain although the source-purpose passage survives. PN1 evidence loss cannot satisfy the clean-correct requirement.'),
'NanoNQ:test1009':('assistant_confirmed_event','assistant_confirmed_event','Both models identify Nicole Gale Anderson in clean/control and PN1 unfiltered contexts, then abstain after filtering PN1. The removed source and copy contain the Heather-role relation; all survivors lack it.'),
'NanoNQ:test826':('support_retained','support_retained','A retained alternative passage explicitly supplies Article I, Section 2, Clause 3. Loss of the designated original quote is not loss of all sufficient evidence.'),
'NanoNQ:test2247':('clean_rubric_support_missing','clean_rubric_support_missing','The clean filtered passages contain silk-industry and prison-origin theories, not the frozen Halliwell/documented-history answer. Llama abstains. A new strict evidence-loss event is not established.'),
'NanoNQ:test2721':('clean_support_missing','clean_support_missing','The clean filtered survivors discuss other television shows. Both models abstain; there is no clean grounded correct baseline for the specified episode count.'),
'NanoNQ:test2079':('baseline_failure','qualified_core_answer_transition','Qwen fails to name Rockwell in its clean filtered answer. Llama gives Rockwell, but its clean and background-control filtered answers also attribute additional backing vocals to Michael Jackson; the source attributes those to Jermaine. Llama PN1 unfiltered identifies the roles correctly and PN1 filtered abstains after complete support loss. This is a core-answer transition with a baseline-grounding qualification, not an additional unqualified strict event.'),
'NanoMSMARCO:1091973':('qualified_clean_answer_completeness','baseline_failure','Qwen gives a location-only clean answer rather than the full frozen provider description. Llama invents a Benson, Arizona location for the Adelaide medical practice by combining separate entities. Its later PN1 abstention cannot count as a new clean-correct failure.'),
'NanoMSMARCO:1086384':('baseline_failure','baseline_failure','The clean filtered context describes a second filter and a percolator rather than the frozen cloth/paper substitute answer. Qwen suggests a second filter; Llama abstains. Neither is an established clean grounded correct answer under the frozen rubric.'),
'NanoMSMARCO:1028652':('support_retained','support_retained','PN1 retains a copied passage explicitly attributing Corn Flakes to John Harvey Kellogg under the archived source interpretation. Complete evidence loss is false irrespective of answer phrasing.'),
'NanoMSMARCO:1067640':('no_exposure_identical_filtered_context','no_exposure_identical_filtered_context','The target addition is not retrieved, and clean and PN1 filtered requests have identical texts for each model. This cannot establish a newly induced failure. The surviving phototransduction example differs from the frozen epinephrine answer, but this need not be resolved to exclude the primary transition.'),
'NanoMSMARCO:643572':('no_exposure_identical_filtered_context','no_exposure_identical_filtered_context','The target addition is not retrieved and the clean/PN1 filtered requests are identical. Neither a new evidence-loss transition nor an independent repeated answer is established.'),
'NanoMSMARCO:1093082':('partial_support_rubric_sensitive','partial_support_rubric_sensitive','Surviving passages explicitly retain copper as a police-officer term, while etymology is uncertain. The literal one-who-arrests detail and generated origin claims require qualification. Do not promote an exact-quote disappearance to unambiguous complete support loss.')}

def main():
    assert json.loads((HERE/'VALIDATION.json').read_text())['status']=='passed'
    calls=rows(HERE/'calls.jsonl');results=rows(HERE/'results/run1/results.jsonl');by={r['call_id']:r for r in results}
    m=json.loads((HERE/'FROZEN_MANIFEST.json').read_text());contexts={(r['case_id'],r['condition']):r for r in rows(primary.FILTER/'results/filter_run1/results.jsonl')}
    records=[]
    for cid in m['case_ids']:
        rr=[by[c['call_id']] for c in calls if c['case_id']==cid];q,l,why=ASSESSMENTS[cid]
        lookup={(r['condition'],r['mode']):r for r in rr}
        if l=='no_exposure_identical_filtered_context':
            assert contexts[cid,'PN1']['before']['inserted_documents']==0
            assert lookup['C','filtered']['request_sha256']==lookup['PN1','filtered']['request_sha256']
        if l=='assistant_confirmed_event':
            for co,mode in [('C','filtered'),('BN1','filtered'),('PN1','unfiltered')]:
                assert 'Nicole Gale Anderson' in lookup[co,mode]['answer']
            assert lookup['PN1','filtered']['answer'].strip()=='Not enough information.'
        records.append(dict(case_id=cid,question=rr[0]['question'],expected_answer=rr[0]['expected_answer'],source_qualification=rr[0]['source_qualification'],
            qwen_assessment=q,llama_assessment=l,rationale=why,reviewer='Assistant',human_verified=False,independent_review=False,
            responses=[dict(call_id=r['call_id'],condition=r['condition'],mode=r['mode'],llama_request_sha256=r['request_sha256'],qwen_request_sha256=r['baseline_request_sha256'],llama_answer=r['answer'],qwen_answer=r['baseline_answer']) for r in rr]))
    record=dict(status='assistant_interpretation_of_completed_secondary_generator_check',created_utc=datetime.now(timezone.utc).isoformat(),
        frozen_questions=12,logical_conditions_per_model=72,new_llama_requests=66,
        shared_unqualified_recorded_event_ids=['NanoNQ:test1009'],qualified_llama_core_answer_transition_ids=['NanoNQ:test2079'],
        primary_59_case_assessment_unchanged=True,human_verified=False,
        input_hashes={str(p.relative_to(HERE.parent)):sha(p) for p in [HERE/'FROZEN_MANIFEST.json',HERE/'results/run1/unique_results.jsonl',FIRST/'results/answers_run1/unique_results.jsonl',primary.FILTER/'results/filter_run1/results.jsonl']},records=records)
    save(HERE/'MODEL_COMPARISON_REVIEW.json',record)
    lines=['# FilterFlip: second-model comparison','',
      '**The Heather-role evidence-loss example appears with both Qwen2.5:3b and Llama3.2:3b on the same saved contexts. Other cases include baseline failures, retained evidence and qualified results.**','',
      '## Completed experiment','',
      'The unchanged preselected 12-question subset was evaluated in clean (C), background-copy control (BN1), and correct-source-copy (PN1) conditions, each before and after filtering. All 72 logical Llama conditions completed through 66 distinct local requests; six reused exact requests. Saved Qwen answers supply the paired comparator. No retrieval or filtering was rerun. The execution audit passed with exact token counts and unchanged request messages/options.','',
      'The local model is [official Ollama Llama 3.2 3B](https://ollama.com/library/llama3.2:3b), digest `'+m['model_digest']+'`. It was downloaded once and run locally, without paid API requests or sending study prompts externally. Tokenizer setup used GGUF metadata and the [Meta Llama tokenizer pattern](https://raw.githubusercontent.com/meta-llama/llama3/main/llama/tokenizer.py). Three synthetic probes passed before study calls.','',
      '## Main paired result','',
      '| Heather actor question | Qwen | Llama |','|---|---|---|',
      '| Clean, filtered | Nicole Gale Anderson | Nicole Gale Anderson |','| Background-copy control, filtered | Nicole Gale Anderson | Nicole Gale Anderson |','| Correct-source copy, unfiltered | Nicole Gale Anderson | Nicole Gale Anderson |','| Correct-source copy, filtered | Not enough information | Not enough information |','',
      'The unfiltered copied context contains both the original biography and its answer-preserving copy. The filter removes both. The survivors mention other roles/films and include an unlabelled cast list, but no longer connect Heather to Nicole Gale Anderson. Thus this is evidence loss followed by abstention in both model packages, under the recorded settings. A name occurring in a cast list is not sufficient support for the requested role relation.','',
      '## Qualified and negative findings','',
      '- **Rockwell question:** Llama retains the correct core name before filtering and abstains after PN1 evidence removal. However, its clean/control answers add a backing-vocal attribution not supported by the source. It remains qualified, not a second unambiguous strict event. Qwen already fails its clean answer.','- **Three-Fifths Compromise:** alternative evidence remains and both models answer correctly. This remains a counterexample to treating original-quote removal as complete evidence loss.','- **Angel of the North / Ordeal by Innocence:** Llama already abstains in the clean condition, so later failures are not new induced failures.','- **Benson Radiology:** Llama’s clean answer incorrectly combines a medical practice with a different city. That clean error prevents a strict new-event claim.','- All twelve planned cases were retained, including exposure misses and identical filtered contexts. None were replaced with successful examples.','',
      '## Limits and reporting','',
      'This is a secondary check, not a new 59-question evaluation or independent sample. The question subset was frozen before primary outcomes, but Llama selection and exact comparison implementation occurred after Qwen outcomes and before any Llama study response. Only Heather among the four conservatively confirmed primary cases belongs to this subset; the other three were not cross-model tested here.','',
      'The messages, passage order, temperature, seed, 4,096-token context setting and 128-token answer limit were held fixed. Model weights, tokenizer and native chat template differ; Llama’s template adds a knowledge-cutoff line. This compares served model packages, not weights alone. No prompts were tuned to induce a failure. No reruns were chosen for favorable answers.','',
      'The saved filtering decisions come from the tested RAGDefender 0.2.0 single-hop configuration with MiniLM embeddings. This is not a faithful reproduction of a paper configuration using Stella embeddings. Both generators receive the same filter outputs, so this comparison supplies no evidence of transfer to another filter or embedding configuration.','',
      'One shared example supports the existence of this failure beyond Qwen for this configuration. It does not establish prevalence, publication novelty, a successful defense or a general superiority of either model. All outcome judgments remain assistant-authored. The primary assessment remains 4 assistant-confirmed recorded events, 47 comparisons not meeting the strict endpoint and 8 unresolved; this diagnostic does not rewrite that tally.','',
      '## All twelve case decisions','', '| Case | Qwen assessment | Llama assessment | Reason |','|---|---|---|---|']
    for r in records:lines.append('| '+r['case_id']+' | '+r['qwen_assessment'].replace('_',' ')+' | '+r['llama_assessment'].replace('_',' ')+' | '+r['rationale'].replace('|','\\|')+' |')
    lines+=['', '## Next step','', 'The most informative next extension is an independent-filter/configuration check, using the existing frozen case subset and explicit native settings. It will help distinguish a failure of this particular RAGDefender implementation/configuration from a broader defense-design issue. Preserve failed mitigation baselines and avoid adding a secure-improvement claim until harmful-content challenges are also tested.','', 'Full verbatim paired answers: PAIRED_MODEL_ANSWERS.md. Execution audit: VALIDATION.json. Protocol and immutable plan: PROTOCOL.md and FROZEN_MANIFEST.json.']
    (HERE/'SECOND_MODEL_REVIEW.md').write_text('\n'.join(lines)+'\n')
    print('Saved full twelve-case review. One shared unqualified event; Rockwell qualified; no change to primary rates.')

if __name__=='__main__':main()
