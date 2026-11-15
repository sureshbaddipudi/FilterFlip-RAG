'use strict';
const $=id=>document.getElementById(id);
const studyConditions=['C','BN1','BN2','PN1','PN2','BE1','BE2','PE1','PE2'];
const labels={C:'C: Clean corpus',BN1:'BN1: Background copy',PN1:'PN1: Answer-source copy',BN2:'BN2: Two background copies',PN2:'PN2: Two answer-source copies',BE1:'BE1: Exact background copy',BE2:'BE2: Two exact background copies',PE1:'PE1: Exact answer-source copy',PE2:'PE2: Two exact answer-source copies',neutral_append:'Neutral source excerpt',wrong_answer_append:'False-claim excerpt',instruction_append:'Instruction-containing excerpt'};
const policies={U:['No filter','All supplied passages reach the answer model.'],N:['Native filter','The original RAGDefender decision.'],E:['Exact-copy handling','Identical text is collapsed, then the native filter runs.'],CN:['Near-copy handling','Passages are grouped at 0.95 similarity, then the native filter runs.']};
let token,cases=[],runId=null,payload=null,active=false,pollTimer=null,lastRendered=null,referenceRequest=0;
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
async function api(path,data){const r=await fetch(path,data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Run-Token':token},body:JSON.stringify(data)});const d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');return d;}
function setBusy(value){active=value;for(const id of ['run','case','mode','condition','reference'])$(id).disabled=value;$('cancel').disabled=!value;}
function tab(study){$('saved').hidden=true;$('saved-tab').classList.toggle('selected',false);$('study').hidden=!study;$('live').hidden=study;$('study-tab').classList.toggle('selected',study);$('live-tab').classList.toggle('selected',!study);}
$('study-tab').onclick=()=>tab(true);$('live-tab').onclick=$('back-live').onclick=()=>tab(false);
function choices(preserveRun=false){const mode=$('mode').value,previous=$('case').value;const visible=cases.filter(c=>mode==='original'||mode==='variants'||c[mode]);$('case').replaceChildren(...visible.map(c=>{const o=el('option',c.question);o.value=c.id;return o;}));$('case').value=visible.some(c=>c.id===previous)?previous:(visible.some(c=>c.id==='NanoNQ:test1009')?'NanoNQ:test1009':visible[0]?.id||'');const options=mode==='variants'?studyConditions:mode==='original'?['C,PN1']:mode==='mitigation'?['PN1','C','BN1']:['wrong_answer_append','neutral_append','instruction_append'];$('condition').replaceChildren(...options.map(c=>{const o=el('option',labels[c]||'C: Clean corpus + PN1: Answer-source copy');o.value=c;return o;}));if(!preserveRun)describe();}
function invalidateReference(){referenceRequest++;$('reference-panel').hidden=true;}
function describe(preserveRun=false){invalidateReference();if(!active&&!preserveRun){$('run-identity').textContent='';$('results').replaceChildren();$('context').replaceChildren();$('events').replaceChildren();payload=null;runId=null;$('export').disabled=true;$('heading').textContent='Ready for a live comparison';$('run-badge').textContent='Not started';$('status').textContent='Selection changed. Start a new run or inspect saved evidence.';}const mode=$('mode').value,c=cases.find(c=>c.id===$('case').value);$('explanation').textContent=mode==='variants'?'Retrieve the selected study condition live, apply the unchanged native filter, then generate two fresh answers: without filtering and with native filtering. Select any of the nine original conditions.':mode==='original'?'Live retrieval in two corpora, followed by fresh answers with and without the native filter. One copy is the only corpus change.':mode==='mitigation'?'Retrieve one context live, then run the four Week-6 choices on the same passages and generate four fresh answers.':'Use the approved clean five passages plus one fixed challenge passage. Filtering and four answers are fresh. This is forced exposure, not a new retrieval attack. All three Heather challenge variants completed in the accepted clean v2.4 teammate return. That decision covers those recorded jobs; this new run still requires human interpretation.';$('qualification').textContent=mode==='challenge'?'Fixture qualification: '+(c?.qualification||'See the supplied reviewer record.')+(['NanoNQ:test1009','NanoNQ:test1635','NanoMSMARCO:1048359'].includes(c?.id)?' This trio has a recorded reviewer limitation; read the challenge review before generalizing.':''):'Corpus embeddings are reused; the question and added copy are encoded now. Saved answers are never substituted.';}
$('mode').onchange=()=>choices();$('case').onchange=()=>describe();$('condition').onchange=()=>describe();
function restoreRunSelection(state){
  const c=cases.find(c=>c.id===state.case_id);
  if(!c)throw Error('Run question unavailable');
  $('mode').value=state.mode;choices(true);$('case').value=state.case_id;$('condition').value=state.condition;
  describe(true);
  $('run-identity').textContent=`${c.question} · ${state.case_id} · ${state.mode} · ${labels[state.condition]||state.condition}`;
}
function render(result){$('results').replaceChildren();$('context').replaceChildren();for(const [co,c] of Object.entries(result.conditions||{})){const section=el('section',undefined,'comparison');section.append(el('h3',labels[co]||co));const grid=el('div',undefined,'policy-grid');for(const arm of ['U','N','E','CN'].filter(a=>c.policies?.[a])){const p=c.policies[arm];const box=el('article',undefined,'policy');box.append(el('h4',policies[arm][0]),el('p',policies[arm][1],'note'));const a=c.answers?.[arm];box.append(el('div',a?.text||((result.status==='running'&&active)?'Waiting for fresh generation…':'No completed answer recorded.'),'answer'));if(a)box.append(el('p',`Fresh response · ${a.status} · ${a.seconds.toFixed(1)} seconds · human review pending`,'note'));if(p.singleton_bypass)box.append(el('p','One representative remains: native filter bypassed under the evaluated policy.','notice'));box.append(el('p',`${p.kept.length} of ${c.retrieved.length} passages reach the model. Order: ${p.kept.map(i=>i+1).join(', ')||'none'}.`,'keep-count'));c.retrieved.forEach((passage,i)=>{const kept=p.kept.includes(i),rep=p.representatives.includes(i);const status=kept?'Kept':rep?'Removed by filter':'Grouped out';const detail=el('details',undefined,'passage '+(kept?'kept':'removed'));const extra=passage.challenge_added?' · Challenge passage':passage.copied_from?' · Inserted copy':'';detail.append(el('summary',`${i+1}. ${status}${extra}`),el('p',passage.text));box.append(detail);});grid.append(box);}section.append(grid);$('results').append(section);const context=el('details',undefined,'context-details');context.append(el('summary',`${labels[co]||co} · inspect complete supplied context`));c.retrieved.forEach((p,i)=>context.append(el('h4',`Passage ${i+1}${p.challenge_added?' · appended challenge':''}${p.copied_from?' · inserted copy':''}`),el('p',p.text)));$('context').append(context);}}
async function poll(){const requestedRun=runId;try{const snapshot=await api('/api/runs/'+requestedRun);if(runId!==requestedRun)return;restoreRunSelection(snapshot.state);payload=snapshot;const state=payload.effective_status;const isRunning=state==='running';setBusy(isRunning);$('run-badge').textContent=state;$('heading').textContent='Live computation';$('status').textContent=`Run ${runId.slice(0,8)} · ${payload.state.mode} · CPU. ${isRunning?'Computing new evidence and answers…':state==='completed'?'Run complete. Read the answers and remaining support before judging the outcome.':'Run stopped. Partial output is preserved; missing answers are not negative findings.'}`;$('events').replaceChildren(...(payload.events||[]).slice(-5).map(e=>el('li',e.stage+(e.condition?' · '+(labels[e.condition]||e.condition):'')+(e.policy?' · '+policies[e.policy][0]:''))));if(payload.result){const display={...payload.result,status:isRunning?'running':state};const fingerprint=JSON.stringify(display);if(fingerprint!==lastRendered){render(display);lastRendered=fingerprint;}}$('export').disabled=false;if(isRunning)pollTimer=setTimeout(poll,1200);}catch(e){if(runId!==requestedRun)return;$('status').textContent='Status connection lost. No new generation was started. Reconnecting…';pollTimer=setTimeout(poll,3000);}}
$('run').onclick=async()=>{try{setBusy(true);if(pollTimer)clearTimeout(pollTimer);payload=null;lastRendered=null;$('export').disabled=true;invalidateReference();$('run-identity').textContent='';$('results').replaceChildren();$('context').replaceChildren();$('events').replaceChildren();$('heading').textContent='Starting live computation';$('status').textContent='Checking local configuration and frozen inputs…';const r=await api('/api/runs',{case_id:$('case').value,mode:$('mode').value,condition:$('condition').value});runId=r.run_id;poll();}catch(e){$('status').textContent=e.message;setBusy(false);}};
$('cancel').onclick=async()=>{try{$('cancel').disabled=true;await api('/api/cancel',{run_id:runId});$('status').textContent='Stopping the owned model process; partial evidence is retained.';}catch(e){$('status').textContent=e.message;}};
function reviewDate(value){return value&&value!=='Not supplied'?value:'Date not supplied';}
function recordedValue(value){return value===null||value===undefined||value===''?'Not separately recorded':String(value);}
function reviewSection(title){const n=el('section',undefined,'review-section');n.append(el('h4',title));return n;}
function reviewFields(rows){const list=el('dl',undefined,'review-fields');for(const [label,value] of rows)list.append(el('dt',label),el('dd',recordedValue(value)));return list;}
function renderRecordedCase(d){
  const panel=$('reference-panel'),r=d.current_human_review,review=d.display_review_summary;
  const source=r.current_assessment.source,value=r.current_assessment.recorded_value;
  const prior=r.prior_individual_human_review,joint=r.prior_joint_adjudication;
  const isJoint=source==='prior_joint_adjudication',isIndividual=source==='prior_individual_human_review';
  const verdict=({yes:'Strict endpoint met',event:'Strict endpoint met',no:'Strict endpoint not met','non-event':'Strict endpoint not met','Not a strict event':'Strict endpoint not met'})[value]||recordedValue(value);
  const basis=isJoint?'Case-specific joint adjudication':isIndividual?'Dated individual case review, confirmed by the reviewers':'Human confirmation of the existing case assessment';
  panel.replaceChildren(el('h3','Recorded case · not the live result'),el('p','This review applies to the saved evidence. Any newly generated answers require their own review.','notice'));
  const decision=reviewSection('1 · Question and recorded decision');
  decision.append(el('p',d.question,'review-question'),el('p',verdict,'review-verdict'),reviewFields([
    ['Case',d.case_id],['Frozen expected answer',d.expected_answer],['Source interpretation',d.source_qualification],['Review basis',basis]
  ]),el('p','A strict event requires the full reviewed chain: a usable clean answer, an answer-preserving retrieved copy, a usable PN1 unfiltered answer, loss of supporting evidence, and failure after filtering. The background-copy condition is an additional control.','note'));
  panel.append(decision);
  const checks=reviewSection('2 · Review checks and reasoning');
  if(isJoint&&joint){
    checks.append(reviewFields([
      ['Q1 · Clean filtered answer supported and usable',joint.Q1_Q6?.Q1],
      ['Q2 · Copy retrieved with the answer preserved',joint.Q1_Q6?.Q2],
      ['Q3 · PN1 unfiltered answer supported and usable',joint.Q1_Q6?.Q3],
      ['Q4 · All answer support lost after PN1 filtering',joint.Q1_Q6?.Q4],
      ['Q5 · PN1 filtered answer fails the agreed rule',joint.Q1_Q6?.Q5],
      ['Q6 · Background-copy control supported and usable',joint.Q1_Q6?.Q6]
    ]));
  }else if(isIndividual&&prior){
    const checkValue=key=>prior[key]==null&&d.case_id==='NanoNQ:test1635'&&['Answer preserved in copy?','All support lost after filter?'].includes(key)?'Not applicable — the added copy was not retrieved':prior[key];
    checks.append(reviewFields([
      ['Clean filtered answer supported and correct','Clean supported + correct?'],
      ['Added copy retrieved','Copy retrieved?'],['Answer preserved in the copy','Answer preserved in copy?'],
      ['PN1 unfiltered answer supported and correct','PN1 unfiltered supported + correct?'],
      ['All answer support lost after PN1 filtering','All support lost after filter?'],
      ['PN1 filtered answer category','PN1 filtered answer category'],
      ['Background-copy control supported and correct','Background supported + correct?'],
      ['Background-qualified event','Background-qualified event?']
    ].map(([label,key])=>[label,checkValue(key)])));
  }else{
    checks.append(el('p','The existing case assessment was confirmed without changes. A separate completed check-by-check form is not recorded for this case.','note'));
  }
  const reasoning=isJoint?joint?.agreed_rationale:isIndividual?prior?.['Evidence and reasoning']:r.historical_case_register_entry?.current_assistant_rationale;
  checks.append(el('h5','Reason for the decision'));
  for(const paragraph of (reasoning||'Reasoning not separately recorded.').split(/\n+|\s+(?=Q[1-6]:)/).filter(Boolean))checks.append(el('p',paragraph,'review-reason'));
  if(isJoint&&joint){
    const rules=el('details',undefined,'review-detail');rules.append(el('summary','Agreed scoring rules and decisive quotations'),reviewFields([['Answer completeness rule',joint.answer_completeness_rule],['Mixed-answer rule',joint.mixed_answer_rule]]));
    for(const quote of joint.decisive_quotes||[])rules.append(el('blockquote',quote));checks.append(rules);
  }
  if(d.support_quote){const quote=el('details',undefined,'review-detail');quote.append(el('summary','Frozen supporting excerpt'),el('p',d.support_quote));checks.append(quote);}
  panel.append(checks);
  const answers=reviewSection('3 · Saved answers: C, BN1 and PN1');
  answers.append(el('p','These are the original recorded answers, not responses from your current live run. “Kept” describes the filter decision; it does not by itself prove that a passage supports the answer.','note'));
  const grid=el('div',undefined,'policy-grid');
  for(const condition of ['C','BN1','PN1']){
    const c=d.conditions?.[condition],card=el('article',undefined,'policy');card.append(el('h5',labels[condition]));
    if(!c){card.append(el('p','Condition not recorded.'));grid.append(card);continue;}
    const passages=c.passages||[];card.append(el('p',`${passages.filter(p=>p.kept===true).length} of ${passages.length} passages kept by the native filter.`,'keep-count'));
    for(const [mode,label] of [['unfiltered','Without filtering'],['filtered','With native filtering']]){
      const a=c.answers?.[mode];card.append(el('h6',label),el('div',a?.answer??'No answer recorded.','answer'));
      if(a?.status)card.append(el('p','Saved response status: '+a.status,'note'));
    }
    grid.append(card);
  }
  answers.append(grid);panel.append(answers);
  const evidence=reviewSection('4 · Retrieved passages and filter decisions');
  evidence.append(el('p','Expand a condition, then a passage, to read its full saved text. Passage numbers show retrieval order.','note'));
  for(const condition of ['C','BN1','PN1']){
    const c=d.conditions?.[condition];if(!c)continue;
    const group=el('details',undefined,'review-detail');group.append(el('summary',labels[condition]));
    for(const [i,p] of (c.passages||[]).entries()){
      const status=p.kept===true?'Kept':p.kept===false?'Removed':'Decision not recorded';
      const item=el('details',undefined,'passage '+(p.kept===true?'kept':'removed'));
      item.append(el('summary',`P${p.rank??i+1} · ${status} · ${recordedValue(p.record_id)}${p.copied_from?' · Added copy':''}`),el('p',p.text),reviewFields([['Record ID',p.record_id],['Chunk ID',p.chunk_id],['Copy of',p.copied_from||'Original passage'],['Text SHA-256',p.text_sha256]]));group.append(item);
    }
    evidence.append(group);
  }
  panel.append(evidence);
  const provenance=reviewSection('5 · Review dates and trace references');
  if(review){
    provenance.append(reviewFields([['Human reviewers',review.reviewers.join(' and ')],['Shradha’s review date',reviewDate(review.shradha_review_date)],['Suresh’s corresponding review date',reviewDate(review.suresh_review_date)]]));
    provenance.append(el('p','Suresh requested that his corresponding review use Shradha’s date; this date instruction was recorded on 28 October 2026.','note'));
    if(review.shradha_review_date==='Not supplied')provenance.append(el('p','The later confirmation was recorded on '+review.later_confirmation_recorded_date+'. Its actual review date has not been supplied. The recording date is not substituted for it.','note'));
  }
  if(isJoint&&joint)provenance.append(reviewFields([['Joint agreement recorded',joint.agreement_recorded_date],['Evidence reviewed',joint.source],['Rule set',joint.adopted_rule_set_id]]));
  else if(isIndividual&&prior)provenance.append(reviewFields([['Evidence reviewed',prior['Reviewed run / artifact version']]]));
  if(d.later_order_note)provenance.append(el('p',d.later_order_note,'note'));
  const trace=el('details',undefined,'review-detail');trace.append(el('summary','Answer call IDs and request fingerprints'));
  for(const condition of ['C','BN1','PN1'])for(const mode of ['unfiltered','filtered']){
    const a=d.conditions?.[condition]?.answers?.[mode];if(!a)continue;
    trace.append(el('h5',`${labels[condition]} · ${mode}`),reviewFields([['Call ID',a.call_id],['Request SHA-256',a.request_sha256]]));
  }
  provenance.append(trace,el('p','This view presents selected fields from the preserved evidence and review records. Complete source records and their attribution remain in the package.','note'));panel.append(provenance);panel.hidden=false;
}
$('reference').onclick=async()=>{const request=++referenceRequest,caseId=$('case').value;$('reference-panel').hidden=true;try{const recorded=await api('/api/reference/'+caseId);if(request!==referenceRequest)return;renderRecordedCase(recorded);}catch(e){if(request===referenceRequest)$('status').textContent=e.message;}};
$('export').onclick=()=>{if(!payload)return;const u=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=el('a');a.href=u;a.download='FilterFlip_live_'+runId+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
api('/api/bootstrap').then(d=>{token=d.token;cases=d.cases;choices();$('run').disabled=false;if(d.active){runId=d.active;setBusy(true);poll();}}).catch(()=>{$('status').textContent='Cannot connect to the local demo. Check the launch terminal.';});
