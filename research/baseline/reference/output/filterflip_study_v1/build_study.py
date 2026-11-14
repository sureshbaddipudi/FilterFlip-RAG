#!/usr/bin/env python3
"""Create source-screened candidates and blank support labels, never filter outcomes."""
import argparse
from collections import defaultdict
import hashlib
import html
import json
from pathlib import Path
import re
import unicodedata

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def rows(path):return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
def norm(s):return ' '.join(re.findall(r'\w+',unicodedata.normalize('NFKC',s).casefold()))
def grams(s):
    t=norm(s).split();return set(tuple(t[i:i+5]) for i in range(max(0,len(t)-4)))
def overlap(a,b):
    if norm(a)==norm(b):return {'match':True,'reason':'normalized_exact','jaccard':1.0,'containment':1.0}
    x,y=grams(a),grams(b);shared=len(x&y)
    j=shared/len(x|y) if x|y else 0
    c=shared/min(len(x),len(y)) if x and y else 0
    flag=shared>=10 and (j>=.8 or c>=.8)
    return {'match':flag,'reason':'fivegram_overlap' if flag else None,'jaccard':j,'containment':c}

def previous(root):
    paths=[];documents={};questions=set()
    vendor=root/'vendor/RAGDefender/artifacts'
    for name in ['nq','msmarco']:
        for rel in [f'GARAG/garag_{name}.json',f'results/target_queries/{name}.json']:
            p=vendor/rel;paths.append(p)
            for row in json.loads(p.read_text()):
                if 'ground_truth' in row:documents[row['ground_truth']]=str(p.relative_to(root))
                questions.add(norm(row.get('question',row.get('query',''))))
    for rel in ['pilot20/pilot20_plan.json','newcase20/newcase20_plan.json','confirmation12/confirmation_plan.json']:
        p=root/rel;paths.append(p)
        for case in json.loads(p.read_text())['cases']:
            questions.add(norm(case['question']))
            if case.get('target_text'):documents[case['target_text']]=rel
            for d in case.get('conditions',{}).get('clean',[]):documents[d['text']]=rel
    for rel in ['results/retrieval118_run1/indexed_chunks.json','results/newcase20_retrieval_run1/indexed_chunks.json']:
        p=root/rel;paths.append(p)
        for row in json.loads(p.read_text()):documents[row['text']]=rel
    return {'scope':'Conservative exclusion: all two-dataset author-artifact questions/references plus prior plans/corpus chunks, not only successful targets.',
            'input_hashes':{str(p.relative_to(root)):sha(p) for p in paths},
            'questions':sorted(questions- {''}),
            'documents':[{'text':t,'origin':o} for t,o in sorted(documents.items())]}

def validate_data(corpus,queries,qrels):
    for data,name in [(corpus,'corpus'),(queries,'queries')]:
        ids=[d['_id'] for d in data]
        if len(ids)!=len(set(ids)):raise ValueError('Duplicate '+name+' IDs')
        if any(not d['text'].strip() for d in data):raise ValueError('Empty '+name+' text')
    cids={d['_id'] for d in corpus};qids={d['_id'] for d in queries}
    if any(r['corpus-id'] not in cids or r['query-id'] not in qids for r in qrels):
        raise ValueError('Dangling qrel')
    if qids!={r['query-id'] for r in qrels}:raise ValueError('Query without qrels')

def build(package,root,out):
    out.mkdir(parents=True,exist_ok=False)
    prior=previous(root);save(out/'prior_exclusion_catalog.json',prior)
    acquisition=json.loads((package/'sources/acquisition.json').read_text())
    candidates=[];reference_docs={};counts={}
    for name in ['NanoNQ','NanoMSMARCO']:
        base=package/'sources'/name
        data={s:rows(base/(s+'.jsonl')) for s in ['corpus','queries','qrels']}
        for split,items in data.items():
            expected=acquisition['datasets'][name]['splits'][split]
            if sha(base/(split+'.jsonl'))!=expected['jsonl_sha256'] or len(items)!=expected['rows']:
                raise ValueError('Acquisition integrity mismatch')
        validate_data(**data)
        lookup={r['_id']:r['text'] for r in data['corpus']};rels=defaultdict(list)
        for r in data['qrels']:rels[r['query-id']].append(r['corpus-id'])
        for q in sorted(data['queries'],key=lambda x:x['_id']):
            cid=name+':'+q['_id'];references=[];matches=[]
            for did in sorted(set(rels[q['_id']])):
                text=lookup[did];key=name+':'+did;reference_docs[key]=text
                references.append({'document_id':did,'text':text,'sha256':hashlib.sha256(text.encode()).hexdigest()})
                for old in prior['documents']:
                    result=overlap(text,old['text'])
                    if result['match']:
                        matches.append({'document_id':did,'prior_text_sha256':hashlib.sha256(old['text'].encode()).hexdigest(),
                                        'prior_origin':old['origin'],**result})
            qmatch=norm(q['text']) in prior['questions']
            reasons=(['prior_question_overlap'] if qmatch else [])+(['prior_source_overlap'] if matches else [])
            candidates.append({'case_id':cid,'dataset':name,'query_id':q['_id'],'question':q['text'],
                'qrel_documents':references,'prior_question_match':qmatch,'prior_source_matches':matches,
                'screen_status':'excluded_overlap' if reasons else 'pending_support_review',
                'exclusion_reasons':reasons,'human_support_status':'UNREVIEWED'})
        counts[name]={'documents':len(data['corpus']),'queries':len(data['queries']),'qrels':len(data['qrels'])}
    # Connected components across qrel texts give conservative family clusters.
    parent={c['case_id']:c['case_id'] for c in candidates}
    def find(x):
        while x!=parent[x]:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):
        a,b=sorted([find(x),find(y)]);parent[b]=a
    family_edges=[]
    for i,a in enumerate(candidates):
        for b in candidates[i+1:]:
            matching=any(overlap(x['text'],y['text'])['match'] for x in a['qrel_documents'] for y in b['qrel_documents'])
            if matching or norm(a['question'])==norm(b['question']):
                union(a['case_id'],b['case_id']);family_edges.append([a['case_id'],b['case_id']])
    contaminated={find(c['case_id']) for c in candidates if c['screen_status']=='excluded_overlap'}
    for c in candidates:
        c['source_family']=find(c['case_id'])
        if c['source_family'] in contaminated and c['screen_status']!='excluded_overlap':
            c['screen_status']='excluded_overlap';c['exclusion_reasons'].append('linked_to_prior_overlap_family')
    for name in counts:
        sub=[c for c in candidates if c['dataset']==name]
        counts[name]['excluded_overlap']=sum(c['screen_status']=='excluded_overlap' for c in sub)
        counts[name]['pending_support_review']=sum(c['screen_status']=='pending_support_review' for c in sub)
    save(out/'candidates.json',candidates)
    save(out/'screening_summary.json',{'datasets':counts,'candidate_count':len(candidates),
        'prior_questions':len(prior['questions']),'prior_unique_texts':len(prior['documents']),
        'source_family_count':len({find(c['case_id']) for c in candidates}),
        'family_edges':family_edges,'outcomes_examined':False,
        'limitation':'Lexical screening only; source URLs are absent. Article/entity or semantic independence is not guaranteed. Qrels are relevance labels, not complete answer labels.'})
    labels=[{'case_id':c['case_id'],'reviewer':'','decision':'pending','target_document_id':'',
             'expected_answer':'','answer_aliases':[],'support_quote':'','source_qualification':'',
             'exclusion_reason':'','notes':''} for c in candidates if c['screen_status']=='pending_support_review']
    save(out/'support_labels_TEMPLATE.json',labels)
    lines=['# Candidate source review','',
           'No filter, embedding or generator outcome has been evaluated. These are candidate source texts, not validated answers.',
           'Decide eligibility from question/source meaning only. Do not replace cases based on later retrieval or filtering.', '']
    for c in candidates:
        lines += ['## '+c['case_id'],'','**Question:** '+c['question'],'',
                  '**Screen:** '+c['screen_status']+'; family '+c['source_family'],'']
        for d in c['qrel_documents']:
            lines += ['**Document '+d['document_id']+'**','',d['text'],'']
    (out/'SOURCE_REVIEW.md').write_text('\n'.join(lines),encoding='utf-8')
    make_review_page(out,candidates,labels)
    print(json.dumps(counts,indent=2))

def make_review_page(out,candidates,labels):
    payload=json.dumps({'candidates':candidates,'labels':labels},ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><title>FilterFlip source review</title>
<style>body{font:17px system-ui;max-width:1000px;margin:35px auto;padding:0 20px;background:#f5f7fa;color:#182a40}article{background:white;padding:25px;border-radius:12px}pre{white-space:pre-wrap;font:16px/1.65 system-ui}label{display:block;margin:14px 0}input,textarea,select{display:block;box-sizing:border-box;width:100%;padding:9px;font:inherit}button{padding:10px 16px;margin:6px;border:1px solid #456;background:white;cursor:pointer}nav{position:sticky;top:0;background:#f5f7fa;padding:10px 0}small{color:#40536c}</style>
<h1>FilterFlip: source review</h1><p>Read the question and source. Decide whether one source supports a clear factual answer. These are relevance-labeled candidates; no attack results are shown.</p>
<p><b>Save your work:</b> click Download labels regularly. Browser refresh loses unsaved edits. Import your downloaded JSON to continue. A blank row remains pending.</p>
<nav><button id="prev">Previous</button><button id="next">Next</button><button id="download">Download labels</button><label>Resume from saved labels<input type="file" id="import" accept=".json"></label><span id="count"></span></nav>
<article><h2 id="title"></h2><p id="question"></p><div id="sources"></div>
<label>Your name<input id="reviewer"></label><label>Decision<select id="decision"><option value="pending">Pending</option><option value="eligible">One source supports a clear answer</option><option value="exclude">Unsuitable or insufficient source support</option></select></label>
<label>Document ID containing the answer<input id="target_document_id"></label><label>Expected short answer<input id="expected_answer"></label><label>Alternative valid spellings/answers (one per line)<textarea id="answer_aliases"></textarea></label>
<label>Copy the exact supporting sentence(s)<textarea id="support_quote" rows="4"></textarea></label><label>Qualification: historical, disputed, source-specific, etc.<textarea id="source_qualification"></textarea></label>
<label>If excluded, give the source-based reason<input id="exclusion_reason"></label><label>Other notes<textarea id="notes"></textarea></label></article>
<script id="data" type="application/json">PAYLOAD</script><script>
const D=JSON.parse(document.querySelector('#data').textContent);let labels=D.labels;let i=0;
const cases=new Map(D.candidates.map(x=>[x.case_id,x]));const fields=['reviewer','decision','target_document_id','expected_answer','answer_aliases','support_quote','source_qualification','exclusion_reason','notes'];
function save(){if(!labels.length)return;for(const k of fields){const v=document.getElementById(k).value;labels[i][k]=k==='answer_aliases'?v.split('\\n').map(x=>x.trim()).filter(Boolean):v;}}
function render(){if(!labels.length){document.querySelector('article').textContent='No candidates require review.';return;}
 const r=labels[i],c=cases.get(r.case_id);document.querySelector('#title').textContent=r.case_id;document.querySelector('#question').textContent=c.question;
 const box=document.querySelector('#sources');box.replaceChildren();for(const d of c.qrel_documents){const h=document.createElement('h3');h.textContent='Document '+d.document_id;const p=document.createElement('pre');p.textContent=d.text;box.append(h,p);}
 for(const k of fields)document.getElementById(k).value=k==='answer_aliases'?r[k].join('\\n'):r[k];
 document.querySelector('#count').textContent=(i+1)+' / '+labels.length+'; '+labels.filter(x=>x.decision!=='pending').length+' marked';}
document.querySelector('#prev').onclick=()=>{save();i=Math.max(0,i-1);render();};document.querySelector('#next').onclick=()=>{save();i=Math.min(labels.length-1,i+1);render();};
document.querySelector('#download').onclick=()=>{save();const u=URL.createObjectURL(new Blob([JSON.stringify(labels,null,2)+'\\n'],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='support_labels.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),500);render();};
document.querySelector('#import').onchange=async e=>{try{const x=JSON.parse(await e.target.files[0].text());if(!Array.isArray(x)||x.length!==labels.length||x.some((r,j)=>r.case_id!==labels[j].case_id||!Array.isArray(r.answer_aliases)||fields.some(k=>k!=='answer_aliases'&&typeof r[k]!=='string')||!['pending','eligible','exclude'].includes(r.decision)))throw Error('Expected labels for this frozen candidate list.');labels=x;i=0;render();}catch(err){alert(err.message);}};render();
</script></html>'''.replace('PAYLOAD',payload)
    (out/'REVIEW.html').write_text(page,encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();build(Path(__file__).resolve().parent,a.project,a.out)
