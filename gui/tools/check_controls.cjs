// Exercise the real UI handlers with synthetic HTTP replies and captured download Blobs.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../app');
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.value='';this.hidden=false;this.disabled=false;this.text='';this.classList={toggle(){}};}
 set textContent(s){this.text=String(s);this.children=[];}get textContent(){return this.text+this.children.map(n=>n.textContent).join('\n');}
 set innerHTML(_){throw Error('Unsafe HTML insertion');}append(...n){this.children.push(...n);}replaceChildren(...n){this.text='';this.children=n;if(this.tag==='select')this.value=n[0]?.value||'';}
 click(){if(this.tag==='a')downloads.push({name:this.download,url:this.href});}
}
const nodes=new Map(),downloads=[],blobs=new Map(),requests=[];let next=0,status='completed',selection=null;
const selectIds=new Set(['mode','case','condition','saved-case','saved-condition']);
const get=id=>{if(!nodes.has(id))nodes.set(id,new Element(selectIds.has(id)?'select':'div'));return nodes.get(id);};
get('mode').value='variants';
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/STUDY_CATALOG.json'),'utf8'));
const cid='NanoNQ:test1009',item=catalog[cid],d=JSON.parse(fs.readFileSync(path.join(root,'data',item.case),'utf8')),r=JSON.parse(fs.readFileSync(path.join(root,'data',item.review),'utf8'));
const packet={case:d.case,conditions:d.conditions,review_records:r.records,notice:'Synthetic transport uses real saved evidence'};
const cases=JSON.parse(fs.readFileSync(path.join(root,'data/recorded.json'),'utf8')).cases.map(c=>({id:c.case_id,question:c.question,mitigation:true,challenge:true}));
const fetch=async(url,options)=>{
 const body=options?.body?JSON.parse(options.body):null;requests.push({url,body});let data;
 if(url==='/api/bootstrap')data={token:'synthetic',cases,active:null};
 else if(url==='/api/runs'){selection=body;data={run_id:'a'.repeat(32)};}
 else if(url==='/api/cancel'){status='cancelled';data={status:'cancellation_requested'};}
 else if(url.startsWith('/api/runs/'))data={effective_status:status,state:{case_id:selection.case_id,mode:selection.mode,condition:selection.condition,status},events:[],result:{status,conditions:{[selection.condition]:{retrieved:[{text:'SYNTHETIC CONTROL CHECK'}],policies:{U:{kept:[0],representatives:[0]},N:{kept:[],representatives:[0]}},answers:{U:{text:'SYNTHETIC fresh answer',status:'ok',seconds:0},N:{text:'Not enough information.',status:'ok',seconds:0}}}}}};
 else if(url.startsWith('/api/study/'))data=packet;else throw Error('Unexpected route '+url);
 return {ok:true,json:async()=>data};
};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t)},fetch,Blob,URL:{createObjectURL:b=>{const key='blob:'+ ++next;blobs.set(key,b);return key;},revokeObjectURL(){}},setTimeout:()=>1,clearTimeout(){}});
vm.runInContext(fs.readFileSync(path.join(root,'static/app.js'),'utf8'),ctx);vm.runInContext(fs.readFileSync(path.join(root,'static/study.js'),'utf8'),ctx);
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
(async()=>{
 await flush();assert.equal(get('run').disabled,false);assert.deepEqual(get('condition').children.map(o=>o.value),Object.keys(d.conditions));
 for(const co of Object.keys(d.conditions)){
  get('condition').value=co;get('condition').onchange();assert.equal(get('export').disabled,true);
  status='completed';await get('run').onclick();await flush();assert.equal(selection.condition,co);assert.equal(selection.mode,'variants');assert.equal(get('cancel').disabled,true);assert.equal(get('export').disabled,false);
  get('export').onclick();const out=JSON.parse(await blobs.get(downloads.at(-1).url).text());assert.equal(out.state.condition,co);assert.equal(out.result.conditions[co].answers.U.text,'SYNTHETIC fresh answer');
 }
 status='running';await get('run').onclick();await flush();assert.equal(get('run').disabled,true);assert.equal(get('cancel').disabled,false);
 await get('cancel').onclick();await ctx.poll();await flush();assert.equal(get('run').disabled,false);get('export').onclick();assert.equal(JSON.parse(await blobs.get(downloads.at(-1).url).text()).effective_status,'cancelled');
 get('saved-tab').onclick();get('saved-condition').value='PE2';await get('load-saved').onclick();assert.equal(get('export-saved').disabled,false);get('export-saved').onclick();
 const saved=JSON.parse(await blobs.get(downloads.at(-1).url).text());assert.equal(saved.kind,'recorded_study_inspection');assert.equal(saved.selection.condition,'PE2');assert.equal(saved.packet.case.case_id,cid);
 get('saved-condition').value='BN2';get('saved-condition').onchange();assert.equal(get('export-saved').disabled,false);assert.ok(get('saved-content').textContent.includes('BN2'));get('export-saved').onclick();assert.equal(JSON.parse(await blobs.get(downloads.at(-1).url).text()).selection.condition,'BN2');
 get('saved-case').value='changed-case';get('saved-case').onchange();assert.equal(get('export-saved').disabled,true);assert.equal(get('saved-content').children.length,0);assert.equal(get('saved-overview').children.length,0);
 console.log(JSON.stringify({result:'PASS',all_nine_live_selection_and_export_handlers:true,start_stop_cancelled_export:true,saved_inspection_export:true,selection_clears_stale_output:true,synthetic_only:true,browser_download_dialog:'not exercised',model_calls:0}));
})().catch(e=>{console.error(e);process.exitCode=1;});
