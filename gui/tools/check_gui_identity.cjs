// Regression checks use the real frontend and deferred synthetic replies. No HTTP/models.
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(process.argv[2]||path.join(__dirname,'../app'));
const script=fs.readFileSync(path.join(root,'static/app.js'),'utf8');
const A='NanoNQ:test1009',B='NanoNQ:test_other_synthetic';
const cases=[{id:A,question:'Heather question',mitigation:true,challenge:true},{id:B,question:'Other synthetic question',mitigation:true,challenge:true}];
const flush=async()=>{for(let i=0;i<60;i++)await Promise.resolve();};
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.value='';this.hidden=false;this.disabled=false;this.text='';this.classList={toggle(){}};}
 set textContent(v){this.text=String(v);this.children=[];}get textContent(){return this.text+this.children.map(c=>c.textContent).join('\n');}
 set innerHTML(_){throw Error('Text rendering required');}
 append(...v){this.children.push(...v);}replaceChildren(...v){this.children=v;this.text='';if(this.tag==='select')this.value=v[0]?.value||'';}
 click(){if(this.tag==='a')this.onDownload(this);}
}
function setup(activeState=null){
 const nodes=new Map(),blobs=new Map(),downloads=[],references=[],polls=[],rendered=[];
 let state=activeState,runId='a'.repeat(32),blobId=0,deferPoll=false;
 const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(['case','mode','condition'].includes(id)?'select':'div'));return nodes.get(id);};get('mode').value='variants';
 const snapshot=()=>({state:{...state},effective_status:state.status,events:[]});
 const response=data=>({ok:true,json:async()=>data});
 const fetch=async(url,options)=>{
  if(url==='/api/bootstrap')return response({token:'synthetic',cases,active:activeState?runId:null});
  if(url==='/api/runs'){const selection=JSON.parse(options.body);state={...selection,status:'running'};runId='b'.repeat(32);return response({run_id:runId});}
  if(url.startsWith('/api/runs/')){
   if(deferPoll)return new Promise(resolve=>polls.push({resolve,data:snapshot()}));
   return response(snapshot());
  }
  if(url.startsWith('/api/reference/'))return new Promise((resolve,reject)=>references.push({caseId:url.split('/').pop(),resolve:d=>resolve(response(d)),reject}));
  throw Error('Unexpected route '+url);
 };
 const ctx=vm.createContext({document:{getElementById:get,createElement:t=>{const e=new Element(t);e.onDownload=a=>downloads.push(a);return e;}},fetch,Blob,URL:{createObjectURL:b=>{const id='blob:'+ ++blobId;blobs.set(id,b);return id;},revokeObjectURL(){}},setTimeout:()=>1,clearTimeout(){}});
 vm.runInContext(script,ctx);
 // Identity/race tests isolate dispatch; the full renderer has its separate 59-case test.
 ctx.renderRecordedCase=d=>{rendered.push(d.case_id);get('reference-panel').textContent=d.case_id;get('reference-panel').hidden=false;};
 return {ctx,get,blobs,downloads,references,rendered,polls,setStatus:s=>state.status=s,deferPolling:()=>deferPoll=true,response};
}
const checks=[];
async function check(name,f){await f();checks.push(name);}
async function expectHiddenAfterChange(kind){
 const t=setup();await flush();const pending=t.get('reference').onclick();
 if(kind==='case')t.get('case').value=B;
 if(kind==='condition')t.get('condition').value='PN2';
 if(kind==='mode')t.get('mode').value='mitigation';
 t.get(kind).onchange();t.references[0].resolve({case_id:A});await pending;
 assert.deepEqual(t.rendered,[]);assert.equal(t.get('reference-panel').hidden,true);
}
(async()=>{
 await check('reload reconnect restores non-default question, mitigation mode and BN1 before displaying run',async()=>{
  const t=setup({case_id:B,mode:'mitigation',condition:'BN1',status:'running'});await flush();
  assert.deepEqual(['case','mode','condition'].map(k=>t.get(k).value),[B,'mitigation','BN1']);
  for(const k of ['case','mode','condition','run','reference'])assert.equal(t.get(k).disabled,true);
  assert.match(t.get('run-identity').textContent,/Other synthetic question/);assert.match(t.get('run-identity').textContent,/NanoNQ:test_other_synthetic/);assert.match(t.get('run-identity').textContent,/BN1/);
  t.setStatus('completed');await t.ctx.poll();assert.equal(t.get('run').disabled,false);
  assert.equal(t.get('condition').value,'BN1');assert.match(t.get('run-identity').textContent,/Other synthetic question/);
  t.get('export').onclick();const exported=JSON.parse(await t.blobs.get(t.downloads[0].href).text());
  assert.deepEqual(exported.state,{case_id:B,mode:'mitigation',condition:'BN1',status:'completed'});
 });
 await check('reload retains original paired-condition identity',async()=>{
  const t=setup({case_id:B,mode:'original',condition:'C,PN1',status:'running'});await flush();
  assert.equal(t.get('case').value,B);assert.equal(t.get('condition').value,'C,PN1');assert.match(t.get('run-identity').textContent,/C,PN1/);
 });
 for(const kind of ['case','condition','mode'])await check('delayed recorded reply discarded after '+kind+' change',()=>expectHiddenAfterChange(kind));
 await check('starting a live run discards an outstanding recorded reply',async()=>{
  const t=setup();await flush();const pending=t.get('reference').onclick();t.get('case').value=B;t.get('case').onchange();
  // A new inspection of B is also invalidated by starting the run, even without a selection change.
  const next=t.get('reference').onclick();await t.get('run').onclick();await flush();
  t.references[0].resolve({case_id:A});t.references[1].resolve({case_id:B});await Promise.all([pending,next]);
  assert.deepEqual(t.rendered,[]);assert.equal(t.get('reference-panel').hidden,true);assert.match(t.get('run-identity').textContent,/Other synthetic question/);
 });
 await check('second inspection supersedes first even for same question',async()=>{
  const t=setup();await flush();const first=t.get('reference').onclick(),second=t.get('reference').onclick();
  t.references[1].resolve({case_id:A});await second;assert.deepEqual(t.rendered,[A]);
  t.references[0].resolve({case_id:A});await first;assert.deepEqual(t.rendered,[A]);assert.equal(t.get('reference-panel').hidden,false);
 });
 await check('current recorded reply still renders and selection change hides it',async()=>{
  const t=setup();await flush();const pending=t.get('reference').onclick();t.references[0].resolve({case_id:A});await pending;
  assert.deepEqual(t.rendered,[A]);assert.equal(t.get('reference-panel').hidden,false);
  t.get('condition').value='PE2';t.get('condition').onchange();assert.equal(t.get('reference-panel').hidden,true);
 });
 await check('stale recorded errors do not overwrite status of newer selection',async()=>{
  const t=setup();await flush();const pending=t.get('reference').onclick();t.get('case').value=B;t.get('case').onchange();const status=t.get('status').textContent;
  t.references[0].reject(Error('Old request failed'));await pending;assert.equal(t.get('status').textContent,status);
 });
 await check('current recorded error remains visible',async()=>{
  const t=setup();await flush();const pending=t.get('reference').onclick();t.references[0].reject(Error('Current request failed'));await pending;assert.equal(t.get('status').textContent,'Current request failed');
 });
 await check('a late poll for an old completed run cannot replace a new run',async()=>{
  const t=setup({case_id:A,mode:'variants',condition:'PN2',status:'completed'});await flush();t.deferPolling();
  const old=t.ctx.poll();t.get('case').value=B;t.get('case').onchange();await t.get('run').onclick();await flush();
  assert.equal(t.polls.length,2);t.polls[1].resolve(t.response(t.polls[1].data));await flush();
  t.polls[0].resolve(t.response(t.polls[0].data));await old;
  assert.match(t.get('run-identity').textContent,/Other synthetic question/);assert.equal(t.get('case').value,B);assert.equal(t.get('run').disabled,true);
 });
 console.log(JSON.stringify({result:'PASS',checks:checks.length,passed:checks,synthetic_only:true,model_calls:0,HTTP_calls:0,browser_download_dialog:'not exercised'},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
