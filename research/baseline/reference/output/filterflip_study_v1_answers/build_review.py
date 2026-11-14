"""Make a readable paired-output packet without inventing correctness labels."""
import json
from pathlib import Path
from run_answers import HERE,RETRIEVAL,rows,save

def main():
    out=HERE/'results/answers_run1'
    calls=rows(HERE/'calls.jsonl');unique={r['request_sha256']:r for r in rows(out/'unique_results.jsonl')}
    cases=json.loads((RETRIEVAL/'case_manifest.json').read_text())['cases']
    lookup={(c['case_id'],c['condition'],c['mode']):c for c in calls}
    packet=['# FilterFlip: primary paired answers for every planned question','',
            'All 59 questions are retained. An answer appearing here is not automatically correct or supported. Pending calls stay pending. Source answers are historical/source-relative where qualified.','']
    entries=[]
    for case in cases:
        cid=case['case_id']
        packet += ['',f'## {cid}', '',f"**Question:** {case['question']}",f"**Expected:** {case['expected_answer']}",
                   f"**Qualification:** {case['source_qualification']}",f"**Source review:** {case['review_status']}",'',
                   '| Condition | Mode | Response status | Model answer |','|---|---|---|---|']
        entry={'case_id':cid,'question':case['question'],'expected_answer':case['expected_answer'],
               'source_qualification':case['source_qualification'],'source_review_status':case['review_status'],'responses':[],
               'correctness_review':'UNREVIEWED','grounding_review':'UNREVIEWED','human_verified':False}
        for co in ['C','BN1','PN1']:
            for mode in ['unfiltered','filtered']:
                c=lookup[cid,co,mode];r=unique.get(c['request_sha256'],{'status':'pending','answer':None})
                answer=(r.get('answer') or '').replace('|','\\|').replace('\n',' ')
                packet.append(f"| {co} | {mode} | {r['status']} | {answer} |")
                entry['responses'].append({'condition':co,'mode':mode,'call_id':c['call_id'],'request_sha256':c['request_sha256'],
                    'status':r['status'],'answer':r.get('answer'),'identical_request_to':c['identical_request_to']})
        entries.append(entry)
    (HERE/'PRIMARY_ANSWER_REVIEW.md').write_text('\n'.join(packet)+'\n')
    save(HERE/'PRIMARY_ANSWER_REVIEW.json',dict(status='output_packet_not_adjudicated',entries=entries))
    print('Saved primary paired-output packet. Completed unique requests:',len(unique))

if __name__=='__main__':main()
