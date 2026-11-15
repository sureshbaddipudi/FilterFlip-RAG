// Rendering/navigation controls over frozen evidence. No network, model or human judgments.
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../app'),nodes=new Map(),downloads=[],blobs=new Map(),requests=[],pending=[];let serial=0,deferStudy=false;
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.value='';this.hidden=false;this.disabled=false;this.text='';this.classes=new Set();this.classList={toggle:(key,on)=>on?this.classes.add(key):this.classes.delete(key)};}
 set textContent(s){this.text=String(s);this.children=[];}get textContent(){return this.text+this.children.map(x=>x.textContent).join('\n');}
 set innerHTML(_){throw Error('Unsafe HTML');}append(...n){this.children.push(...n);}replaceChildren(...n){this.text='';this.children=n;if(this.tag==='select')this.value=n[0]?.value||'';}click(){if(this.tag==='a')downloads.push(this);else this.onclick?.();}scrollIntoView(){this.scrolled=true;}
}
const selects=new Set(['mode','case','condition','saved-case','saved-condition','saved-source']);
const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(selects.has(id)?'select':'div'));return nodes.get(id);};
get('mode').value='variants';get('saved-source').value='reproduction';get('saved').hidden=true;
const read=n=>JSON.parse(fs.readFileSync(path.join(root,'data',n),'utf8')),catalog=read('STUDY_CATALOG.json');
const packet=cid=>{const d=read(catalog[cid].case),r=read(catalog[cid].review);return {case:d.case,conditions:d.conditions,review_records:r.records,notice:'Saved evidence only'};};
const cases=read('recorded.json').cases.map(c=>({id:c.case_id,question:c.question,mitigation:true,challenge:true}));
const response=data=>({ok:true,json:async()=>data});
const fetch=async(url,options)=>{requests.push(url);if(url==='/api/bootstrap')return response({token:'synthetic',cases,active:null});if(url.startsWith('/api/study/')){const d=packet(url.slice('/api/study/'.length));if(deferStudy)return new Promise(resolve=>pending.push(()=>resolve(response(d))));return response(d);}throw Error('Unexpected route: '+url);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t)},fetch,Blob,URL:{createObjectURL:b=>{const id='blob:'+ ++serial;blobs.set(id,b);return id;},revokeObjectURL(){}},setTimeout:()=>1,clearTimeout(){}});
vm.runInContext(fs.readFileSync(path.join(root,'static/app.js'),'utf8'),ctx);vm.runInContext(fs.readFileSync(path.join(root,'static/study.js'),'utf8'),ctx);
const flush=async()=>{for(let i=0;i<50;i++)await Promise.resolve();};
const descendants=e=>[e,...e.children.flatMap(descendants)];
(async()=>{
 await flush();
 get('mode').value='challenge';get('mode').onchange();
 assert.match(get('explanation').textContent,/five saved passages/);
 assert.match(get('explanation').textContent,/four fresh answers/);
 assert.doesNotMatch(get('explanation').textContent+get('qualification').textContent,/teammate|v2\.4|acceptance return/i);
 get('mode').value='variants';get('mode').onchange();
 await flush();let overviews=0,focusViews=0;
 for(const cid of Object.keys(catalog)){
  const d=packet(cid),before=JSON.stringify(d);
  for(const source of ['reference','reproduction']){
   ctx.renderOverview(d,source,'PN1');const overview=get('saved-overview').textContent;
   for(const [co,c] of Object.entries(d.conditions)){
    assert.ok(overview.includes(co));assert.ok(overview.includes(`${c.metrics.retrieved_copy_documents} / ${c.metrics.inserted_documents}`));
    for(const mode of ['unfiltered','filtered'])assert.ok(overview.includes(ctx.shortAnswer(c.responses[mode][source]?.answer)));
    ctx.renderSavedFocus(d,co,source);const text=get('saved-focus').textContent;
    for(const mode of ['unfiltered','filtered'])assert.ok(text.includes(c.responses[mode][source].answer),cid+' '+co+' '+source);
    for(const p of c.passages)assert.ok(text.includes(p.text));
    if(!d.review_records.some(r=>r.record_type==='secondary_condition'&&r.condition===co))assert.ok(text.includes('No condition-level review in this panel'));
    if(source==='reproduction')for(const mode of ['unfiltered','filtered'])if(!ctx.linkedResponseReviews(d,c.responses[mode]).length)assert.ok(text.includes('No separate assessment recorded for this answer.'));
    focusViews++;
   }
   overviews++;
  }
  assert.equal(JSON.stringify(d),before,'Frozen packet mutated');
 }
 const uncertain=packet('NanoNQ:test1618');ctx.renderSavedFocus(uncertain,'PN2','reproduction');assert.match(get('saved-focus').textContent,/condition review says filtered core “no”; response review says “uncertain”/);
 const truncated=packet('NanoNQ:test306');ctx.renderSavedFocus(truncated,'PN2','reproduction');assert.match(get('saved-focus').textContent,/truncated/);
 const hostile=packet('NanoNQ:test1009');hostile.case.question='<img src=x onerror=alert(1)>';hostile.conditions.PN1.responses.filtered.reproduction.answer='<script>alert(1)</script>';ctx.renderOverview(hostile,'reproduction','PN1');ctx.renderSavedFocus(hostile,'PN1','reproduction');assert.ok(get('saved-focus').textContent.includes(hostile.case.question));assert.ok(get('saved-overview').textContent.includes('<script>alert(1)</script>'));
 get('saved-tab').onclick();assert.match(get('view-badge').textContent,/No generation/);await get('load-saved').onclick();const count=requests.length;
 const pn2=descendants(get('saved-overview')).find(e=>e.tag==='button'&&e.text==='PN2');pn2.click();assert.equal(requests.length,count);assert.equal(get('saved-condition').value,'PN2');assert.match(get('saved-focus').textContent,/PN2/);
 get('saved-source').value='reference';get('saved-source').onchange();assert.equal(requests.length,count);assert.match(get('saved-focus').textContent,/Reference · original study/);
 get('export-saved').onclick();const exported=JSON.parse(await blobs.get(downloads.at(-1).href).text());assert.equal(exported.selection.condition,'PN2');assert.equal(exported.selection.overview_source,'reference');assert.equal(exported.kind,'recorded_study_inspection');assert.equal(Object.keys(exported.packet.conditions).length,9);
 get('presentation-toggle').onclick();assert.equal(get('saved-detail').open,false);assert.equal(get('workspace').classes.has('presentation'),true);assert.equal(get('presentation-toggle').ariaPressed,'true');
 get('study-tab').onclick();assert.match(get('view-badge').textContent,/Recorded findings/);get('live-tab').onclick();assert.match(get('view-badge').textContent,/Live demonstration/);
 const live={status:'cancelled',conditions:{PN1:{retrieved:[{text:'SYNTHETIC original'},{text:'SYNTHETIC copy',copied_from:'docX'},{text:'SYNTHETIC challenge',challenge_added:true}],policies:{U:{kept:[0,1,2],representatives:[0,1,2]},N:{kept:[2],representatives:[0,1,2]},E:{kept:[0],representatives:[0,2]},CN:{kept:[0],representatives:[0],singleton_bypass:true}},answers:{U:{text:'SYNTHETIC partial text',status:'truncated',seconds:0},N:{text:'',status:'empty',seconds:0}}}}};
 const before=JSON.stringify(live);ctx.render(live);const compact=get('results').children[0].textContent;assert.match(compact,/Grouped out/);assert.match(compact,/truncated/);assert.match(compact,/Execution: empty/);assert.match(compact,/No completed answer recorded/);assert.match(compact,/human interpretation pending/i);assert.match(compact,/native filter bypassed/);assert.equal(JSON.stringify(live),before);
 get('presentation-toggle').onclick();assert.equal(get('workspace').classes.has('presentation'),false);assert.equal(get('saved-detail').open,true);
 // Changing the selected question invalidates in-flight saved evidence.
 get('saved-tab').onclick();deferStudy=true;const old=get('load-saved').onclick();get('saved-case').value=Object.keys(catalog).find(k=>k!=='NanoNQ:test1009');get('saved-case').onchange();pending[0]();await old;assert.equal(get('saved-overview').children.length,0);assert.equal(get('saved-focus').children.length,0);assert.equal(get('export-saved').disabled,true);assert.equal(get('saved-detail').hidden,true);
 console.log(JSON.stringify({result:'PASS',overview_views:overviews,focus_views:focusViews,all_frozen_text_and_counts:true,uncertainty_and_truncation_retained:true,literal_text:true,navigation_export_and_source_switch:true,presentation_toggle:true,stale_saved_request_discarded:true,compact_live_partial_and_four_policies:true,frozen_data_unchanged:true,model_calls:0,HTTP_calls:0},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
