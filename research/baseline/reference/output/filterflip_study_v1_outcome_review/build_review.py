"""Record assistant endpoint adjudication and build an unfilled human review packet.
No model calls. Existing frozen experiment inputs and prior reviews remain unchanged.
"""
from pathlib import Path
import json, hashlib, html
from datetime import datetime, timezone
from collections import Counter

HERE=Path(__file__).resolve().parent
ANS=HERE.parent/'filterflip_study_v1_answers'
FIL=HERE.parent/'filterflip_study_v1_filter'
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def esc(x):return html.escape(str(x))

BASELINE_FAILURES={
'NanoNQ:test2233':'Clean filtered answer says Juventus instead of Real Madrid.',
'NanoNQ:test2247':'Clean filtered answer gives an uncorroborated prison-origin theory, not the frozen documented-history answer naming Halliwell and the mid-19th century. This may be relevant to the broad question, but does not meet the frozen answer criterion.',
'NanoNQ:test2539':'Clean filtered answer is 41 rather than 203.',
'NanoNQ:test2598':'Clean filtered answer abstains.',
'NanoNQ:test2651':'Clean filtered answer abstains.',
'NanoNQ:test2721':'Clean filtered answer abstains.',
'NanoNQ:test740':'Clean filtered answer says Princess Anne, inconsistent with the archived-source answer Charles. No claim about current succession is made.',
'NanoNQ:test770':'Clean filtered answer speculates about certification and states that the name origin is unavailable; it fails the two-part frozen explanation.',
'NanoMSMARCO:1049867':'Clean filtered answer names Julie Tawny Kitaen instead of Whitesnake.',
'NanoMSMARCO:1067764':'Clean filtered answer describes a service process rather than the specified customer purchase phases; it does not meet the frozen definition.',
'NanoMSMARCO:1086384':'Clean filtered answer suggests a second filter rather than the specified substitutes for a coffee filter.',
'NanoMSMARCO:140921':'Clean filtered answer abstains.',
'NanoMSMARCO:531490':'Clean filtered answer describes uncertainty (uh), rather than the negative response uh-uh.',
'NanoMSMARCO:804996':'Clean filtered answer is a different ZIP code from the archived Anthem source.',
'NanoMSMARCO:988540':'Clean filtered answer describes electron ionization and radiation rather than the requested ionization-energy quantity.'}
SUPPORT={
'NanoNQ:test3090':('2604b614256c53936bb5a6fc73b781ef178c2b3419afd1383224837f94825f3c:00000','The retained album passage explicitly includes the single Help! on the Help! album.'),
'NanoNQ:test3108':('128ffffc7146d43010413ae2b05c62e43aae568827f22a5f81b6037bdf69aba2:00000','The retained original and copy explicitly say Paige O\'Hara voiced Belle. The model nevertheless says Paige Howard. This is an answer error with evidence retained, not complete evidence loss.'),
'NanoMSMARCO:1028652':('c46d09e027b0500278fab6f95f73659655f04fa9e697a2b629a072556d7aca04:00000','The retained inserted copy explicitly attributes Corn Flakes to John Harvey Kellogg. Assessment is source-relative; this does not validate its historical chronology.'),
'NanoMSMARCO:1039495':('72ed9a2e803a49d8a0e1ad2b38f8dadbd0f5a00b0455fa9ff61353159b10b4b3:00000','The retained copy names Sundar Pichai as Google boss, and other retained references support the archived answer.'),
'NanoMSMARCO:603050':('31421398b91aab0b8751ff1794b8ac60f93335964c8be69074d48295a9e6b46e:00000','A retained source explicitly places Belvidere in Boone County, Illinois.')}
ADDITIONAL_REVIEW={
'NanoNQ:test194':'The clean context retains an alternative C-language paragraph explaining expression statements followed by a semicolon. PN1 unfiltered includes a source explicitly calling semicolons terminators; PN1 filtered retains only a null-statement discussion and a file-format passage. The answer remains correct-looking, but explicit support for the general terminator function is questionable. This could be evidence loss masked by recall; no claim that recall is proved. BN1 and PN1 filtered requests are identical, so the stricter background-control support check also needs review. PN1 has a removal-boundary tie. Not counted as an abstention/wrong-answer event.',
'NanoNQ:test697':'Clean filtering removes the main two-reference-frame source but keeps an alternative stellar-day paragraph. The clean answer gives only that numerical value without the requested solar/stellar distinction. PN1 unfiltered gives both values; after filtering, only generic rotation/orbit and sidereal-year passages remain. The final answer mixes a day-length value with a year-length parenthesis. Evidence loss is plausible, but full-rubric clean correctness is unresolved. Do not count it automatically.',
'NanoMSMARCO:1091973':'The topic-only query has a frozen provider/services-and-region definition. The clean answer only says Benson Radiology is in North Adelaide and mentions Yelp reviews. PN1 unfiltered provides the full description, and PN1 filtered abstains. Whether the clean location-only answer is usable for the broad query is rubric-sensitive; it fails the full definition and is left for review rather than promoted to an event.'}

def main():
    packet=json.loads((ANS/'PRIMARY_ANSWER_REVIEW.json').read_text())['entries']
    prior=json.loads((ANS/'SCREENED_OUTCOME_REVIEW.json').read_text())
    prior_by={r['case_id']:r for r in prior['records']}
    contexts={(r['case_id'],r['condition']):r for r in rows(FIL/'results/filter_run1/results.jsonl')}
    records=[]
    for a in packet:
        cid=a['case_id'];resp={(r['condition'],r['mode']):r for r in a['responses']}
        identical=resp['C','filtered']['request_sha256']==resp['PN1','filtered']['request_sha256']
        extra={}
        if cid in prior_by:
            old=prior_by[cid];reason=old['rationale'];detail=old['decision']
            decision=('provisional_event' if detail=='provisional_event' else 'needs_adjudication'
                      if detail in ['rubric_sensitive_not_counted','partial_support_not_counted'] else 'not_strict_event')
            extra['prior_review_record']=old
        elif identical:
            decision='not_strict_event';detail='identical_clean_and_PN1_filtered_request'
            reason='The entire clean filtered and PN1 filtered model requests are identical, including passage text and order. They share the same saved response. Therefore this recorded comparison cannot satisfy a new clean-supported/correct to unsupported/failing transition. This is a logical endpoint exclusion, not a label that the answer is correct or that the question is safe under other conditions.'
            assert resp['C','filtered']['answer']==resp['PN1','filtered']['answer']
        elif cid in BASELINE_FAILURES:
            decision='not_strict_event';detail='clean_answer_fails_frozen_rubric';reason=BASELINE_FAILURES[cid]
        elif cid in SUPPORT:
            decision='not_strict_event';detail='sufficient_PN1_evidence_retained';chunk,reason=SUPPORT[cid]
            kept=[d for i,d in enumerate(contexts[cid,'PN1']['retrieved']) if i in contexts[cid,'PN1']['kept_indices']]
            assert any(d['chunk_id']==chunk for d in kept)
            extra['positive_support_witness']=next(d for d in kept if d['chunk_id']==chunk)
        elif cid in ADDITIONAL_REVIEW:
            decision='needs_adjudication';detail='new_rubric_or_grounding_issue';reason=ADDITIONAL_REVIEW[cid]
        else:raise ValueError('Unreviewed case '+cid)
        records.append(dict(case_id=cid,question=a['question'],expected_answer=a['expected_answer'],
            source_qualification=a['source_qualification'],source_review_status=a['source_review_status'],
            decision=decision,reason_code=detail,rationale=reason,responses=a['responses'],
            reviewer='Assistant',human_verified=False,all_conditions_accuracy_reviewed=False,**extra))
    counts=dict(Counter(r['decision'] for r in records));assert len(records)==59
    events=[r for r in records if r['decision']=='provisional_event']
    provenance={str(p.relative_to(HERE.parent)):sha(p) for p in [ANS/'calls.jsonl',ANS/'results/answers_run1/unique_results.jsonl',FIL/'results/filter_run1/results.jsonl',ANS/'SCREENED_OUTCOME_REVIEW.json']}
    report=dict(status='all_59_primary_endpoint_audit_with_unresolved_judgments',created_utc=datetime.now(timezone.utc).isoformat(),
        scope='PN1 endpoint audit, not exhaustive accuracy/grounding labels for all 1062 answers. Decisive failed prerequisites short-circuit further scoring.',
        counts=counts,planned_questions=59,human_verified=False,input_hashes=provenance,records=records)
    save(HERE/'PRIMARY_ENDPOINT_AUDIT.json',report)
    lines=['# FilterFlip: all-question primary endpoint review','',
      '**Assistant review completed for all 59 primary comparisons; seven judgments remain unresolved. Human outcome verification is pending.**','',
      '| Primary comparison decision | Questions |','|---|---:|',f'| Provisional evidence-loss event | {counts["provisional_event"]} |',f'| Does not meet the strict endpoint in this run | {counts["not_strict_event"]} |',f'| Needs rubric/support adjudication | {counts["needs_adjudication"]} |','| Total planned | 59 |','',
      'These categories are not a finalized attack-success estimate. Five are provisional, not human-validated. The seven unresolved cases remain in the 59-case denominator. No clean-correct conditional rate is reported: that denominator requires more complete baseline quality/support labels, including cases excluded by identical requests. No confidence interval or population claim is justified from this partial adjudication.','',
      '## What was checked','',
      'All six saved primary/control responses per question were inspected for the endpoint. For 20 previously unscreened questions, clean and PN1 filtered requests are byte-equivalent under the frozen request hash; the context and saved answer are identical. A new evidence-loss transition is impossible in those recorded pairs, irrespective of answer correctness. For other questions, the review checks decisive baseline failures against the frozen answer rubric, or inspects retained evidence. This is a complete primary-event audit with explicit unresolved cases, not a complete correctness annotation of all 1,062 outputs.','',
      'Five provisional examples remain: Heather actor, bald-eagle genus, Woody Woodpecker filming, Targeted Victory, and the archived Northampton assessor telephone number. Three end in abstention; two in wrong answers. All five satisfy the assistant-assessed background-control check. Two have a clean-filter boundary tie. These cases are assembled in VERIFY_FIVE_CASES.html with raw evidence and unfilled review fields.','',
      '## Findings beyond the original shortlist','',
      '- **Belle voice actor (test3108):** Paige O\'Hara is still explicitly present in both retained source and copy, but the model answers Paige Howard. This is a generation error with evidence present, not our complete-support-loss event.','- **C semicolon (test194):** clean support comes from an alternative document, so the original-source quote screen misses it. After adding the target copy, the explicit terminator passage is removed but the answer stays correct-looking. The remaining null-statement explanation is related but may not suffice. The background control produces the identical final context. This requires grounding review and must be separated from wrong-answer/abstention events.','- **Earth rotation (test697):** an alternative clean passage gives the stellar-day value; after the intervention, that evidence is absent and the output mixes day and year quantities. The clean answer does not meet the complete two-frame rubric clearly, so this remains unresolved.','- **Benson Radiology (1091973):** the clean answer supplies location only. The broad query and frozen definition create an answer-completeness question. It is not promoted to an event.','',
      '## Remaining decisions','',
      'Seven cases need explicit adjudication: test123 (RON/MON completeness), test1721 (von meaning), test1989 (daughter nuclide versus emitted particles), 1093082 (copper meaning/etymology), test194 (support versus recall), test697 (reference-frame completeness), and 1091973 (topic-query answer completeness). Do not change frozen rubrics to increase the event count. Any alternative lenient scoring must be clearly labeled as a post-outcome sensitivity analysis.','',
      '## Your verification task','',
      'Open VERIFY_FIVE_CASES.html. Enter your name, review the exact passages and responses, and mark Yes, No or Uncertain for each evidence/answer check. All fields start unreviewed. A second teammate should export a separate file with their own name. This is assisted verification, not a blinded review, because the experiment conditions and prior assessment are visible. Local saving is a convenience only: export the JSON file before closing. Return the exported files for reconciliation. Do not approve a case just because it is on this shortlist.','',
      'The next experimental stage remains the frozen order/settings subset. No new model requests, retrieval/filter runs, thresholds, source-label changes or excluded questions were introduced during this analysis.','',
      '## Per-question decisions','', '| Case | Decision | Basis |','|---|---|---|']
    for r in records:lines.append('| '+r['case_id']+' | '+r['decision'].replace('_',' ')+' | '+r['rationale'].replace('|','\\|')+' |')
    (HERE/'PRIMARY_ENDPOINT_REVIEW.md').write_text('\n'.join(lines)+'\n')
    build_form(events,contexts,provenance)
    print(json.dumps(counts));print('Saved 59-case audit and five-case human review packet.')


def build_form(events,contexts,provenance):
    checks=[('clean','The clean filtered context supports its answer, and that answer correctly answers the question.'),
            ('unfiltered','With the correct-source copy retrieved, the unfiltered context supports a correct model answer.'),
            ('loss','After filtering the copied context, none of the surviving passages supplies sufficient answer evidence.'),
            ('failure','The copied-context filtered answer abstains or is wrong for this question.'),
            ('control','The background-copy filtered context still supports a correct answer.')]
    body=['<h1>Verify five FilterFlip cases</h1><p>Review the evidence, then record your judgment. These are <strong>provisional assistant findings</strong>, not established results. Disagreement is useful. There are five cases; no answers are preselected.</p>',
          '<p>Use the archived source and its qualifications, not current-world knowledge. A name appearing without the requested relation is not sufficient support. Read every surviving passage before selecting “Yes” for evidence loss.</p>',
          '<label>Your name <input id="reviewer" autocomplete="off" placeholder="Reviewer name"></label><p>This is assisted, unblinded verification. Each teammate should export a separate file. Drafts may save in this browser; use Export to keep your work.</p>',
          '<button id="export">Export review JSON</button> <button id="reset" type="button">Start a new reviewer</button><p id="status" role="status"></p>', '<nav>'+''.join(f'<a href="#case{i}">Case {i+1}</a> ' for i in range(len(events)))+'</nav>']
    for n,r in enumerate(events):
        cid=r['case_id'];lookup={(x['condition'],x['mode']):x for x in r['responses']}
        body += [f'<section id="case{n}" data-case="{esc(cid)}"><h2>Case {n+1}: {esc(r["question"])}</h2>',
                 f'<p><strong>ID:</strong> {esc(cid)}<br><strong>Frozen expected answer:</strong> {esc(r["expected_answer"])}<br><strong>Qualification:</strong> {esc(r["source_qualification"])}</p>',
                 '<table><thead><tr><th>Condition</th><th>Without filter</th><th>With filter</th></tr></thead><tbody>']
        for co,title in [('C','Clean corpus'),('BN1','Background-copy control'),('PN1','Correct-source copy')]:
            body.append(f'<tr><th>{title}</th><td>{esc(lookup[co,"unfiltered"]["answer"])}</td><td>{esc(lookup[co,"filtered"]["answer"])}</td></tr>')
        body += ['</tbody></table><h3>Read the actual evidence</h3>']
        for co,title in [('C','1. Clean filtered evidence'),('PN1','2. Retrieved copied context: kept and removed passages'),('BN1','3. Background-control filtered evidence')]:
            ctx=contexts[cid,co]
            body.append(f'<details><summary>{title}</summary>')
            for i,d in enumerate(ctx['retrieved']):
                kept=i in ctx['kept_indices']
                if co!='PN1' and not kept:continue
                body.append(f'<article class="{"kept" if kept else "removed"}"><h4>Passage {i+1} — {"KEPT" if kept else "REMOVED"}</h4><small>{esc(d["record_id"])} · {esc(d["chunk_id"])}</small><p class="passage">{esc(d["text"])}</p></article>')
            body.append('</details>')
        body.append('<fieldset><legend>Your checks</legend>')
        for key,label in checks:
            body.append(f'<label>{esc(label)}<select data-field="{key}"><option value="unreviewed">Not reviewed yet</option><option value="yes">Yes</option><option value="no">No</option><option value="uncertain">Uncertain</option></select></label>')
        body += ['<label>Overall judgment<select data-field="decision"><option value="unreviewed">Not reviewed yet</option><option value="confirm">I confirm this provisional event</option><option value="disagree">I disagree</option><option value="uncertain">Needs discussion</option></select></label>',
                 '<label>Notes: explain disagreement, ambiguity or missing evidence<textarea data-field="notes" rows="3"></textarea></label></fieldset>',
                 '<details><summary>Prior assistant assessment and caveats</summary><p>'+esc(r['rationale'])+'</p><p>Boundary-tie conditions: '+esc(', '.join(r['prior_review_record']['boundary_tie_conditions']) or 'none recorded')+'. Absence of a tie does not prove order robustness.</p></details></section>']
    meta=dict(schema='filterflip_five_case_verification_v1',case_ids=[r['case_id'] for r in events],input_hashes=provenance,
              review_type='human_assisted_unblinded',form_generated_utc=datetime.now(timezone.utc).isoformat())
    script='''
const META=__META__;
const storageKey='filterflip-five-verification-v1';
function collect(){return {...META,reviewer:document.querySelector('#reviewer').value.trim(),exported_utc:new Date().toISOString(),cases:[...document.querySelectorAll('section[data-case]')].map(s=>({case_id:s.dataset.case,checks:Object.fromEntries([...s.querySelectorAll('[data-field]')].map(e=>[e.dataset.field,e.value]))}))};}
function restore(x){if(x.schema!==META.schema)return;document.querySelector('#reviewer').value=x.reviewer||'';for(const r of x.cases||[]){const s=[...document.querySelectorAll('section[data-case]')].find(e=>e.dataset.case===r.case_id);if(s)for(const e of s.querySelectorAll('[data-field]'))e.value=r.checks[e.dataset.field]|| (e.tagName==='SELECT'?'unreviewed':'');}}
try{const old=localStorage.getItem(storageKey);if(old)restore(JSON.parse(old));}catch(e){}
document.addEventListener('input',()=>{try{localStorage.setItem(storageKey,JSON.stringify(collect()));document.querySelector('#status').textContent='Draft saved in this browser. Export a file to preserve it.';}catch(e){document.querySelector('#status').textContent='Browser storage unavailable. Please export your review.';}});
document.querySelector('#export').onclick=()=>{const x=collect();if(!x.reviewer){document.querySelector('#status').textContent='Enter your name before exporting.';return;}
for(const r of x.cases){if(r.checks.decision==='confirm'&&['clean','unfiltered','loss','failure','control'].some(k=>r.checks[k]!=='yes')){document.querySelector('#status').textContent='Confirmation requires Yes on all five checks. Use Needs discussion for '+r.case_id;return;}}
const blob=new Blob([JSON.stringify(x,null,2)],{type:'application/json'});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='filterflip_verification_'+x.reviewer.replace(/[^a-zA-Z0-9_-]/g,'_')+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);document.querySelector('#status').textContent='Review exported. Unreviewed entries remain unreviewed.';};
document.querySelector('#reset').onclick=()=>{if(!confirm('Export the current review first. Clear this browser draft for a new reviewer?'))return;try{localStorage.removeItem(storageKey);}catch(e){}document.querySelectorAll('input,textarea').forEach(e=>e.value='');document.querySelectorAll('select').forEach(e=>e.value='unreviewed');document.querySelector('#status').textContent='New blank review. Previously exported files are unchanged.';};
'''.replace('__META__',json.dumps(meta).replace('<','\\u003c'))
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Verify five FilterFlip cases</title><style>
body{font:17px/1.6 system-ui,sans-serif;max-width:1050px;margin:30px auto;padding:20px;color:#182b3a;background:#f6f8fb}section{background:white;padding:24px;border:1px solid #ccd7df;border-radius:12px;margin:30px 0}h1,h2,h3{line-height:1.25}table{width:100%;border-collapse:collapse;font-size:15px}th,td{border:1px solid #c9d4dc;padding:10px;text-align:left;vertical-align:top}th{background:#edf3f8}label{display:block;margin:18px 0}select,input,textarea{display:block;font:inherit;padding:8px;max-width:100%;box-sizing:border-box}textarea{width:100%}select{margin-top:8px}summary{cursor:pointer;font-weight:bold;padding:12px;background:#eaf0f5}details{margin:14px 0}article{padding:15px;border-left:5px solid #316d5c;margin:10px;background:#f5faf8}.removed{border-color:#a26829;background:#fff8ee}.passage{white-space:pre-wrap}small{overflow-wrap:anywhere}button{padding:10px 16px;font:inherit;cursor:pointer;margin:8px 4px 8px 0}nav a{margin-right:18px}fieldset{border:1px solid #aebfcd}#status{font-weight:bold;color:#31567a}
</style></head><body>'''+''.join(body)+'<script>'+script+'</script></body></html>'
    (HERE/'VERIFY_FIVE_CASES.html').write_text(page)
    save(HERE/'VERIFICATION_PACKET.json',dict(metadata=meta,events=[dict(case=r,contexts={co:contexts[r['case_id'],co] for co in ['C','BN1','PN1']}) for r in events]))

if __name__=='__main__':main()
