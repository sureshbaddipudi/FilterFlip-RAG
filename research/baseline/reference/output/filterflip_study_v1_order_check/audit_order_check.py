"""Validate complete coverage, permutation identities, saved decisions and immutable inputs."""
import json,itertools
from collections import defaultdict
from run_order_check import HERE,INPUT,PLAN,sha,rows,save,base

def main():
 out=HERE/'results/run1';tasks=json.loads((HERE/'plan.json').read_text());results=rows(out/'results.jsonl')
 assert len(tasks)==len(results)==828
 m=json.loads((HERE/'FROZEN_MANIFEST.json').read_text())
 for name,h in m['files'].items():assert sha(HERE/name)==h
 for name,h in m['inputs'].items():assert sha(HERE.parent/name)==h
 old={(r['case_id'],r['condition']):r for r in rows(INPUT)}
 cases={r['case_id']:r for r in json.loads(PLAN.read_text())['cases']}
 groups=defaultdict(list);canonical=0
 for task,r in zip(tasks,results):
  assert all(r[k]==v for k,v in task.items()) and r['status']=='ok'
  ctx=old[r['case_id'],r['condition']];chunks=[ctx['retrieved'][i] for i in r['order']]
  assert sorted(r['order'])==list(range(5))
  assert r['input_chunk_ids']==[c['chunk_id'] for c in chunks]
  assert r['input_text_hashes']==[c['text_sha256'] for c in chunks]
  assert r['kept_indices']==[i for i in range(5) if i not in r['removed_indices']]
  assert r['kept_chunk_ids']==[chunks[i]['chunk_id'] for i in r['kept_indices']]
  assert r['removed_chunk_ids']==[chunks[i]['chunk_id'] for i in r['removed_indices']]
  assert set(r['kept_chunk_ids']).isdisjoint(r['removed_chunk_ids'])
  assert set(r['kept_chunk_ids'])|set(r['removed_chunk_ids'])==set(r['input_chunk_ids'])
  assert r['trace']['estimated_removal_count']==len(r['removed_indices'])
  assert r['trace']['matches_native_removals'] and max(r['token_counts'])<=256
  assert r['matches_saved_kept_set']==(set(r['kept_chunk_ids'])==set(ctx['kept_chunk_ids']))
  case=cases[r['case_id']]
  assert r['after']==base.metrics([chunks[i] for i in r['kept_indices']],case['target_document_id'],case['support_quote'])
  if r['order']==[0,1,2,3,4]:assert r['matches_saved_kept_set'];canonical+=1
  groups[r['group'],r['case_id'],r['condition']].append(r)
 for (g,cid,co),rr in groups.items():
  expected=set(itertools.permutations(range(5))) if g=='post_outcome_tied_case_diagnostic' else {(0,1,2,3,4),(4,3,2,1,0),(2,3,4,0,1)}
  assert {tuple(r['order']) for r in rr}==expected and len(rr)==len(expected)
 assert canonical==42
 primary_env=json.loads((base.HERE/'results/filter_run1/environment.json').read_text())
 current_env=json.loads((out/'environment.json').read_text())
 assert current_env['versions']==primary_env['versions']
 report=dict(status='passed',native_calls=828,canonical_matches=canonical,primary_version_match=True,
  frozen_sample_contexts=36,exhaustive_diagnostic_contexts=6,all_permutation_identities_preserved=True,
  native_traces_match=True,no_truncation=True,input_and_runner_hashes_unchanged=True,
  limitation='No generator calls; no independent semantic ground truth or prevalence inference.')
 save(HERE/'VALIDATION.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
