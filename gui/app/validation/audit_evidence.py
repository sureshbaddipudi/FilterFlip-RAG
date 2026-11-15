"""Recheck copied rehearsal evidence and saved-policy parity. No models/network."""
import sys,json,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from safety import canonical,policy_decision,require
from policies import prepare_arm

def sha(raw):return hashlib.sha256(raw).hexdigest()
def audit():
    runs=[]
    for folder in sorted((ROOT/'evidence').iterdir()):
        s=json.loads((folder/'state.json').read_text());r=json.loads((folder/'result.json').read_text())
        require(r['semantic_review']=='pending','New output must remain unreviewed')
        answers=[a for c in r['conditions'].values() for a in c['answers'].values()]
        raw=[json.loads(f.read_bytes()) for f in sorted(folder.glob('response_*.bin'))]
        require(collections.Counter(sha(canonical(a['raw_response'])) for a in answers)==collections.Counter(sha(canonical(a)) for a in raw),'Raw response mismatch')
        for c in r['conditions'].values():
            for arm,a in c['answers'].items():
                require(sha(canonical(a['request']))==a['request_sha256'],'Request hash mismatch')
                require(a['text']==a['raw_response']['message']['content'],'Answer differs from raw response')
                require(a['source']=='fresh_generation' and a['semantic_review']=='pending','Source/review mismatch')
                require(a['request']['options']==r['options'],'Options mismatch')
                texts=[c['retrieved'][i]['text'] for i in c['policies'][arm]['kept']]
                joined='\n\n'.join(texts)
                require(joined in a['request']['messages'][1]['content'],'Kept context absent from request')
        if s['status']=='completed':require(len(answers)==4 and len(raw)==4 and s['exit_code']==0,'Incomplete finished run')
        runs.append({'run_id':folder.name,'mode':s['mode'],'raw_job_status':s['status'],'effective_disposition':'interrupted (see separate record)' if s['status']=='running' else s['status'],'attempts_begun':r['generation_attempts'],'saved_responses':len(raw),'elapsed_seconds':round(s['finished_at']-s['started_at'],3) if 'finished_at' in s else None})
    src=ROOT/'validation/POLICY_PARITY_INPUT.json'
    require(sha(src.read_bytes())=='af269f08ac98707004173b41a1707cfb518ea71b5b92779fc58f077debe15550','Parity input changed')
    rows=json.loads(src.read_text())['records'];count=0
    for row in rows:
        texts=row['context']['texts']
        for arm in ('U','N','E','CN'):
            saved=row['policies'][arm]
            prepared=prepare_arm(arm,texts,row['scores'],row['matrix'])
            reps=prepared['representatives']
            def native(given):
                require(given==[texts[i] for i in reps],'Wrong native input')
                return [reps.index(i) for i in saved['kept']]
            got=policy_decision(arm,texts,row['scores'],row['matrix'],native)
            for field in ('kept','groups','representatives','singleton_bypass'):
                if field in saved:require(got[field]==saved[field],row['context']['key']+' '+arm+' '+field)
            count+=1
    return {'status':'pass','runs':runs,'total_attempts_begun':sum(x['attempts_begun'] for x in runs),'saved_responses':sum(x['saved_responses'] for x in runs),'policy_contexts':len(rows),'policy_mappings':count,'scope':'Raw response/request consistency and offline policy adapter parity using saved native decisions. Not new inference, semantic adjudication or proof of process termination.'}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
