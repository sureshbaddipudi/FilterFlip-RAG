// Unit checks of text-safe rendering, not a browser or fresh model experiment.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../app');
class Element{constructor(tag){this.tag=tag;this.children=[];this.value='';this.hidden=true;}set textContent(s){this.value=String(s);this.children=[];}get textContent(){return this.value+this.children.map(n=>n.textContent).join('\n');}set innerHTML(_){throw Error('Unsafe HTML insertion');}append(...n){this.children.push(...n);}replaceChildren(...n){this.value='';this.children=n;}}
const panel=new Element('section'),nodes=new Map();
const read=n=>JSON.parse(fs.readFileSync(path.join(root,'data',n),'utf8'));
const labels={C:'C: Clean corpus',BN1:'BN1: Background copy',BN2:'BN2: Two background copies',PN1:'PN1: Answer-source copy',PN2:'PN2: Two answer-source copies',BE1:'BE1: Exact background copy',BE2:'BE2: Two exact background copies',PE1:'PE1: Exact answer-source copy',PE2:'PE2: Two exact answer-source copies'};
const ctx=vm.createContext({document:{createElement:t=>new Element(t)},$:id=>id==='saved-content'?panel:(nodes.has(id)?nodes.get(id):(nodes.set(id,new Element('div')),nodes.get(id))),labels});
const app=fs.readFileSync(path.join(root,'static/app.js'),'utf8'),js=fs.readFileSync(path.join(root,'static/study.js'),'utf8');
vm.runInContext(app.slice(app.indexOf('function el('),app.indexOf('async function api('))+app.slice(app.indexOf('function recordedValue('),app.indexOf("$('reference').onclick")),ctx);
vm.runInContext(js.slice(js.indexOf('function savedReview('),js.indexOf('function populateSaved(')),ctx);
let n=0;
for(const [cid,v] of Object.entries(read('STUDY_CATALOG.json'))){const d=read(v.case),r=read(v.review),packet={case:d.case,conditions:d.conditions,review_records:r.records,notice:'Recorded evidence'};
 for(const co of Object.keys(labels)){ctx.renderSavedStudy(packet,co);const text=panel.textContent,c=d.conditions[co];
  for(const p of c.passages)assert.ok(text.includes(p.text),cid+' '+co+' full passage');
  for(const a of Object.values(c.responses))for(const k of ['reference','reproduction']){assert.ok(text.includes(a[k].answer),cid+' '+co+' '+k+' answer');assert.ok(text.includes(a[k].status));}
  const review=r.records.find(x=>x.record_type==='secondary_condition'&&x.condition===co);
  if(review){assert.ok(text.includes(review.human.rationale));for(const k of ['reference','reproduction'])assert.ok(text.includes(review[k].strict_endpoint));}
  assert.ok(!text.includes('source_statement'));n++;
 }
}
const v=Object.values(read('STUDY_CATALOG.json'))[0],d=read(v.case);d.case.question='<img src=x onerror=alert(1)>';
ctx.renderSavedStudy({case:d.case,conditions:d.conditions,review_records:[],notice:'test'},'C');assert.ok(panel.textContent.includes(d.case.question));
ctx.renderSavedStudy({case:d.case,conditions:d.conditions,review_records:[],notice:'test'},'PN2');assert.ok(panel.textContent.includes('No separate assessment recorded'));
console.log(JSON.stringify({result:'PASS',case_condition_views:n,answer_panel_positions:n*4,full_passages:true,literal_text:true,missing_reviews_not_imputed:true,model_calls:0}));
