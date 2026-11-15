// Offline checks of data precedence, missing values and literal-text rendering.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
class Element{
 constructor(tag){this.tag=tag;this.children=[];this.value='';this.hidden=true;}
 set textContent(s){this.value=String(s);this.children=[];}get textContent(){return this.value+this.children.map(n=>n.textContent).join('\n');}
 set innerHTML(_){throw Error('Unsafe HTML insertion');}
 append(...n){this.children.push(...n);}replaceChildren(...n){this.value='';this.children=n;}
}
const panel=new Element('section');
const ctx=vm.createContext({document:{createElement:t=>new Element(t)},$:()=>panel,labels:{C:'C: Clean corpus',BN1:'BN1: Background copy',PN1:'PN1: Answer-source copy'}});
const js=fs.readFileSync(path.join(root,'static/app.js'),'utf8');
vm.runInContext(js.slice(js.indexOf('function el('),js.indexOf('async function api('))+js.slice(js.indexOf('function recordedValue('),js.indexOf("$('reference').onclick")),ctx);
const read=n=>JSON.parse(fs.readFileSync(path.join(root,'data',n),'utf8'));
const reviews=Object.fromEntries(read('human_reviews.json').records.map(r=>[r.case_id,r]));
const dates=Object.fromEntries(read('CURRENT_REVIEW_SUMMARY.json').records.map(r=>[r.case_id,r]));
const cases=read('recorded.json').cases;
const render=d=>{ctx.renderRecordedCase({...d,current_human_review:reviews[d.case_id],display_review_summary:dates[d.case_id]});return panel.textContent;};
for(const d of cases){
 const text=render(d);assert.equal(panel.hidden,false);assert.equal(panel.children.filter(n=>n.tag==='section').length,5);
 for(const c of Object.values(d.conditions)){
  for(const a of Object.values(c.answers))assert.ok(text.includes(a.answer),d.case_id+' answer missing');
  for(const p of c.passages)assert.ok(text.includes(p.text),d.case_id+' passage missing');
 }
 assert.ok(!text.includes('source_statement'));assert.ok(!text.includes('source_reviewer_field'));assert.ok(!text.includes('actual_review_date'));
 assert.doesNotMatch(text,/teammate|v2\.4|joint agreement recorded|human reviewers/i);
 const r=reviews[d.case_id];
 if(r.current_assessment.source==='prior_joint_adjudication')assert.ok(text.includes(r.prior_joint_adjudication.agreed_rationale));
 if(r.current_assessment.source==='existing_assessment_now_human_confirmed_without_change')assert.ok(text.includes('separate completed check-by-check form is not recorded'));
}
const get=id=>cases.find(c=>c.case_id===id);
assert.ok(render(get('NanoNQ:test1635')).includes('Not applicable — the added copy was not retrieved'));
assert.ok(render(get('NanoMSMARCO:1045374')).includes('Mixed-answer rule'));
assert.ok(render(get('NanoNQ:test1009')).includes('Answer call IDs and request fingerprints'));
const literal='<img src=x onerror=alert(1)>';
assert.ok(render({...get('NanoNQ:test1009'),question:literal}).includes(literal));
console.log('PASS: all 59 cases; every saved answer and passage; joint-review precedence; missing checklist handling; UCC applicability; literal-text rendering. No models or research calls.');
