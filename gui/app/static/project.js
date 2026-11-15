'use strict';
(() => {
 const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 const button=(text,fn)=>{const b=node('button',text);b.onclick=fn;return b;};
 function show(){for(const name of ['live','saved','study']){$(name).hidden=true;$(name+'-tab').classList.toggle('selected',false);}$('project').hidden=false;$('project-tab').classList.toggle('selected',true);$('view-badge').textContent='Project work · Recorded evidence and scope';}
 $('project-tab').onclick=show;
 function go(action){
  if(action==='saved'){$('saved-tab').click();return;}
  if(action==='findings'){tab(true);return;}
  if(action==='security'){document.getElementById('project-security').open=true;document.getElementById('project-security').scrollIntoView({block:'start'});return;}
  if(action==='report'){window.open('/semester-report.pdf','_blank','noopener');return;}
  if(active){$('project-status').textContent='A live run is active. Finish or stop it before selecting another experiment.';return;}
  tab(false);$('mode').value=action;choices();$('live-setup').open=true;$('live-setup').scrollIntoView({block:'start'});
 }
 function render(data){
  const root=$('project-content');root.replaceChildren(node('p',data.intro.early),node('p',data.intro.limit,'note'));
  const nav=node('div',undefined,'buttons');[['Original comparison','original'],['All nine live conditions','variants'],['TrustRAG live comparison','trust'],['Mitigation comparison','mitigation'],['Security challenges','challenge']].forEach(([label,id])=>nav.append(button(label,()=>go(id))));root.append(nav);
  for(const t of data.tasks){
   const card=node('details',undefined,'finding-section');card.append(node('summary',`${t.number} · ${t.title}`),node('p',t.status,'notice'),node('p',t.summary));
   card.append(button(t.action==='report'?'Open semester report draft':t.action==='security'?'Read security coverage':t.action==='saved'?'Inspect saved conditions':t.action==='findings'?'Explore findings':'Select this live experiment',()=>go(t.action)));
   const source=node('details',undefined,'source-record');source.append(node('summary','Read dated supporting record · '+t.source_name),node('p','Original record retained. Its dates and status apply to that artifact; the current summary above may reflect later accepted review.','note'),node('pre',t.source_text,'source-text'));card.append(source);root.append(card);
  }
  const sec=node('details',undefined,'finding-section');sec.id='project-security';sec.append(node('summary','Application security · STRIDE and all four OWASP mappings'),node('p','Coverage describes applicability, implemented controls and remaining gaps. It does not mean every risk is eliminated or the application is certified.','notice'));
  for(const doc of data.security){const detail=node('details',undefined,'source-record');detail.append(node('summary',doc.title),node('pre',doc.text,'source-text'));sec.append(detail);}root.append(sec);
  const limits=node('section',undefined,'walkthrough');limits.append(node('h3','What remains open'));const list=node('ul');data.current_limits.forEach(t=>list.append(node('li',t)));limits.append(list);root.append(limits);$('project-status').textContent='All 13 later tasks are mapped to their evidence; earlier milestones and open work are summarized below.';
 }
 fetch('/api/project').then(r=>{if(!r.ok)throw Error('Project evidence unavailable');return r.json();}).then(render).catch(()=>{$('project-status').textContent='Project evidence could not be loaded. Check release integrity and refresh.';});
})();
