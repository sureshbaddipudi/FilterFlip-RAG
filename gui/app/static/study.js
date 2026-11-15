'use strict';
let savedPacket=null,savedRequest=0,savedSelection=null;
function clearSaved(){savedRequest++;savedPacket=null;savedSelection=null;$('saved-content').replaceChildren();$('saved-overview').replaceChildren();$('saved-focus').replaceChildren();$('saved-detail').hidden=true;$('export-saved').disabled=true;$('saved-status').textContent='Selection changed. Inspect the selected case and condition.';}
function savedReview(h){return reviewFields([['Rule used',h?.rule_used],['Reason',h?.rationale]]);}
function renderSavedStudy(packet,condition){
 const panel=$('saved-content'),c=packet.conditions[condition],meta=packet.case;
 if(!c)throw Error('Condition not recorded');
 panel.replaceChildren(el('h3',labels[condition]+' · '+meta.question),el('p','Saved answers from the original study and the reproduction run.','notice'));
 panel.append(reviewFields([['Case',meta.case_id],['Frozen expected answer',meta.expected_answer],['Source interpretation',meta.source_qualification]]));
 panel.append(el('p',`Inserted documents: ${c.metrics.inserted_documents}. Copy documents actually retrieved: ${c.metrics.retrieved_copy_documents}. Copy documents retained: ${c.metrics.retained_copy_documents}. Kept passages: ${c.kept_indices.length} of ${c.passages.length}.`,'keep-count'));
 panel.append(el('p','N variants add a neutral prefix; E variants copy exact text. B copies a background source, P an answer source. The digit is the insertion budget, not guaranteed retrieval.','note'));
 const endpoint=(packet.review_records||[]).find(r=>r.record_type==='secondary_condition'&&r.condition===condition);
 if(endpoint){
  const review=el('details',undefined,'review-detail');review.append(el('summary','Existing secondary-condition review'));
  review.append(savedReview(endpoint.human));
  for(const [key,title] of [['reference','Reference panel'],['reproduction','Reproduction panel']]){
   const d=endpoint[key]||{};review.append(el('h5',title),reviewFields([['Strict endpoint',d.strict_endpoint],['Background-qualified endpoint',d.background_qualified_endpoint],['Unfiltered support',d.unfiltered_context_support],['Filtered support',d.filtered_context_support],['Unfiltered core usable',d.unfiltered_core_usable],['Filtered core usable',d.filtered_core_usable],['Filtered full answer complete',d.filtered_full_complete],['Extra wrong claims',d.wrong_extra_claims]]));
  }
  panel.append(review);
 }else panel.append(el('p','This is a primary condition. Use “Inspect recorded case” in Live demonstration for the historical C/BN1/PN1 endpoint and its five review sections. A missing new per-answer review is not inferred from that historical decision.','note'));
 if(meta.case_id==='NanoNQ:test1618'&&condition==='PN2')panel.append(el('p','Preserved review discrepancy: PN2 filtered core usability is “no” in the condition panel and “uncertain” in its response review. Both values remain visible; the analysis includes a conservative sensitivity.','notice'));
 if(meta.case_id==='NanoNQ:test306')panel.append(el('p','The reproduced filtered C/PN1/PN2/PE1/PE2 links share one truncated response. Partial text is retained and is not a complete scientific outcome.','notice'));
 const grid=el('div',undefined,'policy-grid');
 for(const [key,title] of [['reference','Saved reference answers'],['reproduction','Saved reproduced answers']]){
  const card=el('article',undefined,'policy');card.append(el('h4',title));
  for(const [mode,heading] of [['unfiltered','Without filtering'],['filtered','With native filtering']]){
   const response=c.responses[mode],a=response?.[key];card.append(el('h5',heading),el('div',a?.answer??'No answer recorded.','answer'),el('p','Execution status (not correctness): '+recordedValue(a?.status),'note'));
   if(key==='reproduction'){
    const rows=(packet.review_records||[]).filter(r=>r.record_type==='reproduction_response'&&r.request_sha256===response?.request_sha256&&(r.logical_links||[]).some(l=>l.call_id===response.call_id));
    if(!rows.length)card.append(el('p','No separate assessment recorded for this answer.','note'));
    for(const r of rows){const detail=el('details',undefined,'review-detail');detail.append(el('summary','Existing response review'),savedReview(r.human),reviewFields([['Support',r.judgment?.context_support],['Answer category',r.judgment?.answer_category],['Core usable',r.judgment?.core_usable],['Full frozen answer complete',r.judgment?.full_frozen_answer_complete],['Extra errors',r.judgment?.wrong_or_unsupported_extras],['Semantic difference from reference',r.judgment?.semantic_difference_from_reference]]));card.append(detail);}
   }
   const trace=el('details',undefined,'review-detail');trace.append(el('summary','Saved answer identity'),reviewFields([['Call ID',response?.call_id],['Request SHA-256',response?.request_sha256],['Reference text identical',response?.exact_reference_text_match]]));card.append(trace);
  }
  grid.append(card);
 }
 panel.append(grid);
 const evidence=reviewSection('Full retrieved passages · native filter decisions');
 evidence.append(el('p','All retrieved passages form the unfiltered context; only passages marked Kept form the filtered context. A kept passage is not automatically sufficient answer support.','note'));
 for(const [i,p] of c.passages.entries()){
  const kept=p.kept===true,item=el('details',undefined,'passage '+(kept?'kept':'removed'));
  item.append(el('summary',`P${p.retrieval_rank??i+1} · ${kept?'Kept':'Removed'} · ${p.record_id}${p.copied_from?' · Inserted copy '+p.copy_number:''}`),el('p',p.text),reviewFields([['Record ID',p.record_id],['Chunk ID',p.chunk_id],['Copy of',p.copied_from||'Original passage'],['Text SHA-256',p.text_sha256]]));evidence.append(item);
 }
 panel.append(evidence);
}
function populateSaved(){
 const old=$('saved-case').value;$('saved-case').replaceChildren(...cases.map(c=>{const o=el('option',c.question);o.value=c.id;return o;}));$('saved-case').value=cases.some(c=>c.id===old)?old:'NanoNQ:test1009';
 $('saved-condition').replaceChildren(...studyConditions.map(c=>{const o=el('option',labels[c]);o.value=c;return o;}));$('saved-condition').value='PN1';
}
$('saved-tab').onclick=()=>{$('project').hidden=true;$('project-tab').classList.toggle('selected',false);$('view-badge').textContent='Saved study evidence · No generation';$('live').hidden=true;$('study').hidden=true;$('saved').hidden=false;for(const name of ['live','study'])$(name+'-tab').classList.toggle('selected',false);$('saved-tab').classList.toggle('selected',true);if(!$('saved-case').children.length)populateSaved();};
$('saved-case').onchange=clearSaved;
$('saved-condition').onchange=()=>{if(savedPacket&&savedSelection?.case_id===$('saved-case').value)selectSavedCondition($('saved-condition').value);else clearSaved();};
$('saved-source').onchange=()=>{if(savedPacket)refreshSaved();};
$('load-saved').onclick=async()=>{
 const id=++savedRequest,cid=$('saved-case').value,condition=$('saved-condition').value;
 savedPacket=null;savedSelection=null;$('saved-content').replaceChildren();$('saved-overview').replaceChildren();$('saved-focus').replaceChildren();$('saved-detail').hidden=true;$('export-saved').disabled=true;$('saved-status').textContent='Loading saved evidence…';
 try{const packet=await api('/api/study/'+cid);if(id!==savedRequest)return;savedPacket=packet;savedSelection={case_id:cid,condition};refreshSaved();$('export-saved').disabled=false;$('saved-status').textContent='Saved evidence loaded. No model was run.';}
 catch(e){if(id===savedRequest)$('saved-status').textContent=e.message;}
};
$('export-saved').onclick=()=>{
 if(!savedPacket)return;const output={kind:'recorded_study_inspection',selection:{...savedSelection,overview_source:$('saved-source').value},packet:savedPacket,notice:'Export of saved evidence, not fresh generation or a new human decision.'};
 const url=URL.createObjectURL(new Blob([JSON.stringify(output,null,2)],{type:'application/json'})),a=el('a');a.href=url;a.download='FilterFlip_saved_'+savedSelection.case_id.replace(':','_')+'_'+savedSelection.condition+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};

// Navigation summaries are derived only from the loaded, frozen case packet.
function sourceTitle(source){return source==='reference'?'Reference · original study':'Reproduction · later run';}
function linkedResponseReviews(packet,response){return (packet.review_records||[]).filter(r=>r.record_type==='reproduction_response'&&r.request_sha256===response?.request_sha256&&(r.logical_links||[]).some(l=>l.call_id===response?.call_id));}
function conditionReviewText(packet,condition,source){
  const row=(packet.review_records||[]).find(r=>r.record_type==='secondary_condition'&&r.condition===condition);
  if(!row)return 'No condition-level review in this panel';
  return `Review: ${recordedValue(row.human?.review_status)} · Strict endpoint: ${recordedValue(row[source]?.strict_endpoint)}`;
}
function shortAnswer(answer){if(answer==null)return 'No answer recorded';return answer.length>130?answer.slice(0,127)+'…':answer;}
function renderOverview(packet,source,selected){
  const panel=$('saved-overview');panel.replaceChildren(el('h3','Nine conditions at a glance'),el('p',sourceTitle(source)+' · Saved answers, not live output. Select a condition to explain its evidence.','note'));
  const scroll=el('div',undefined,'table-scroll');scroll.tabIndex=0;scroll.ariaLabel='Nine saved conditions';
  const table=el('table',undefined,'condition-table');table.append(el('caption','B = background source; P = answer source; N = neutral prefix; E = exact copy. 1 / 2 = copies inserted. Answer excerpts are shortened; full answers appear below.'));
  const head=el('thead'),tr=el('tr');
  for(const title of ['Condition','Copies retrieved / inserted','Passages kept','Without filter','With native filter','Recorded review']){const th=el('th',title);th.scope='col';tr.append(th);}head.append(tr);table.append(head);
  const body=el('tbody');
  for(const condition of studyConditions){
    const c=packet.conditions[condition],row=el('tr',undefined,condition===selected?'selected-condition':'');
    const first=el('th'),button=el('button',condition,'condition-link');first.scope='row';button.title=labels[condition];button.ariaLabel='Inspect '+labels[condition];button.ariaPressed=String(condition===selected);button.onclick=()=>selectSavedCondition(condition);first.append(button,el('span',labels[condition]?.split(': ')[1]||condition,'condition-name'));row.append(first);
    if(!c){row.append(el('td','Condition not recorded'));body.append(row);continue;}
    row.append(el('td',`${c.metrics.retrieved_copy_documents} / ${c.metrics.inserted_documents}`),el('td',`${c.kept_indices.length} / ${c.passages.length}`));
    for(const mode of ['unfiltered','filtered']){const a=c.responses[mode]?.[source],cell=el('td');cell.append(el('p',shortAnswer(a?.answer)),el('span','Execution: '+recordedValue(a?.status),'note'));row.append(cell);}
    const review=el('td',conditionReviewText(packet,condition,source),'note');
    if(packet.case.case_id==='NanoNQ:test1618'&&condition==='PN2')review.append(el('strong','Preserved review discrepancy; see details.','review-warning'));
    row.append(review);body.append(row);
  }
  table.append(body);scroll.append(table);panel.append(scroll,el('p','Execution “ok” does not mean the answer is correct. Missing reviews are not inferred. C / BN1 / PN1 historical case decisions remain in “Inspect recorded case” on the Live demonstration tab.','note'));
}
function renderSavedFocus(packet,condition,source){
  const c=packet.conditions[condition],panel=$('saved-focus');if(!c){panel.replaceChildren();return;}
  panel.replaceChildren(el('p',sourceTitle(source)+' · '+labels[condition],'eyebrow'),el('h3',packet.case.question),el('p',`${packet.case.case_id} · ${packet.case.source_qualification||'Read the supplied source context.'}`,'note'));
  const flow=el('div',undefined,'saved-flow');
  const evidence=el('article',undefined,'flow-evidence');evidence.append(el('h4','1 · Retrieved passages → native filter'),el('p',`${c.metrics.retrieved_copy_documents} copied documents retrieved; ${c.kept_indices.length} of ${c.passages.length} passages kept.`,'keep-count'),passageStrip(c.passages,c.kept_indices),el('p','Open a passage to read its exact text. Kept/removed labels describe filter decisions, not semantic support.','note'));
  const answers=el('article',undefined,'flow-answers');answers.append(el('h4','2 · Compare the paired answers'));
  for(const [mode,title] of [['unfiltered','Without filtering'],['filtered','With native filtering']]){
    const response=c.responses[mode],a=response?.[source];answers.append(el('h5',title),el('div',a?.answer??'No answer recorded.','answer'),el('p','Execution: '+recordedValue(a?.status),'note'));
    if(source==='reproduction'){
      const reviews=linkedResponseReviews(packet,response);
      if(!reviews.length)answers.append(el('p','No separate assessment recorded for this answer.','note'));
      for(const row of reviews)answers.append(el('p',`Recorded response review: ${recordedValue(row.judgment?.answer_category)} · Core usable: ${recordedValue(row.judgment?.core_usable)}`,'note'));
    }
  }
  flow.append(evidence,answers);panel.append(flow,el('p',conditionReviewText(packet,condition,source),'notice'));
  const back=el('button','Back to all nine conditions');back.onclick=()=>$('saved-overview').scrollIntoView?.({block:'start'});panel.append(back);
  if(packet.case.case_id==='NanoNQ:test1618'&&condition==='PN2')panel.append(el('p','Preserved discrepancy: condition review says filtered core “no”; response review says “uncertain”. Both are retained.','notice'));
  if(packet.case.case_id==='NanoNQ:test306')panel.append(el('p','Some filtered conditions share a truncated reproduced response. Partial text is not a complete outcome; inspect the execution status and full records.','notice'));
}
function refreshSaved(){
  if(!savedPacket||!savedSelection)return;
  const source=$('saved-source').value==='reference'?'reference':'reproduction',condition=savedSelection.condition;
  renderOverview(savedPacket,source,condition);renderSavedFocus(savedPacket,condition,source);renderSavedStudy(savedPacket,condition);
  $('saved-detail').hidden=false;$('saved-detail').open=!presentation;
}
function selectSavedCondition(condition){
  if(!savedPacket||!savedPacket.conditions[condition])return;
  $('saved-condition').value=condition;savedSelection={case_id:savedPacket.case.case_id,condition};refreshSaved();
  $('saved-status').textContent='Saved '+condition+' selected. No model was run.';
  $('saved-focus').scrollIntoView?.({block:'start'});
}
