#!/usr/bin/env python3
"""Offline validation of Task-5 evidence; no network, installs or model imports."""
from pathlib import Path
import json,hashlib,collections,ast,re,sys
p=Path(__file__).resolve().parent.parent;errors=[];counts={}
def read(rel):return json.loads((p/rel).read_text())
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def require(test,message):
 if not test:errors.append(message)
def child(rel):
 require(not Path(rel).is_absolute() and '..' not in Path(rel).parts,'Unsafe member '+rel)
 return p/rel
manifest=read('SHA256_MANIFEST.json')
actual={str(f.relative_to(p)) for f in p.rglob('*') if f.is_file() and f!=p/'SHA256_MANIFEST.json'}
require(set(manifest)==actual,'Manifest inventory mismatch')
for rel,wanted in manifest.items():
 f=child(rel);require(f.is_file() and not f.is_symlink() and sha(f)==wanted,'Changed/missing member '+rel)
counts['manifest_files']=len(manifest)
for rel,entry in read('SOURCE_MANIFEST.json').items():require(sha(child('sources/'+rel))==entry['sha256'],'Source snapshot '+rel)
for entry in read('ADVISORY_SOURCE_INDEX.json')['sources']:
 if entry['status']=='retrieved':require(sha(child('advisories/'+entry['id']+'.json'))==entry['sha256'],'Advisory snapshot '+entry['id'])
for entry in read('ADVISORY_ALIAS_SUPPLEMENT.json'):
 if entry['status']=='retrieved':require(sha(child('advisories/'+entry['retrieved_id']+'.json'))==entry['sha256'],'Alias advisory '+entry['retrieved_id'])
for entry in read('FRESH_ADDITIONAL_SOURCE_INDEX.json'):require(sha(child('advisories/'+entry['id']+'.json'))==entry['sha256'],'Fresh advisory '+entry['id'])
old=read('FINDING_ASSESSMENTS.json');extra=read('FRESH_ADDITIONAL_ASSESSMENTS.json');ledger=read('sources/validation/OPEN_DEPENDENCY_FINDINGS.json')['findings']
require(len(old)==71 and {(x['component'],x['id']) for x in old}=={(x['component'],x['id']) for x in ledger},'Original 71 coverage differs')
require(len(extra)==12 and collections.Counter(x['component'] for x in extra)=={'filelock':9,'pillow':3},'Fresh addition coverage differs')
for record in old+extra:
 for field in ['feature','trigger_precondition','project_relevance','reachability_rationale','action_and_remaining_gap','reassessment_trigger','evidence']:
  require(bool(record.get(field)),record['id']+' missing '+field)
 require(record['risk_acceptance']=='not recorded' and record['scientific_compatibility']=='pending Task 9',record['id']+' false acceptance')
 require(child(record['advisory_snapshot']).is_file(),record['id']+' missing advisory')
counts['preserved_assessments']=len(old);counts['additional_assessments']=len(extra)
# Rebuild alias components independently from every retrieved document and the preserved ledger.
parent={}
def find(id):
 parent.setdefault(id,id)
 if parent[id]!=id:parent[id]=find(parent[id])
 return parent[id]
def union(ids):
 root=find(ids[0])
 for id in ids[1:]:parent[find(id)]=root
for x in ledger:union([x['id']]+x['aliases'])
for file in (p/'advisories').glob('*.json'):
 d=json.loads(file.read_text());union([d['id']]+d.get('aliases',[]))
groups=collections.defaultdict(set)
for id in list(parent):groups[find(id)].add(id)
lookup={id:tuple(sorted(group)) for group in groups.values() for id in group}
raw=read('validation/FRESH_VERSION_MATCHES.json')['results'];reconciled=read('validation/ALIAS_RECONCILIATION.json')['profiles']
require(len(raw)==84,'Expected 84 package/version bindings')
for name,expected_raw,expected_clusters in [('baseline',114,83),('candidate',38,27)]:
 rows=[x for x in raw if x['profile']==name]
 total_raw=sum(len(x['vulns']) for x in rows);total=sum(len({lookup[v['id']] for v in x['vulns']}) for x in rows)
 require(len(rows)==42 and total_raw==expected_raw and total==expected_clusters,name+' lookup counts differ')
 require(reconciled[name]['component_advisory_clusters']==total,name+' saved reconciliation differs')
 counts[name+'_raw_records']=total_raw;counts[name+'_advisory_clusters']=total
for wheel in read('candidate/WHEEL_MANIFEST.json'):
 require(sha(child('candidate/wheels/'+wheel['filename']))==wheel['sha256'],'Wheel hash differs '+wheel['filename'])
 require(any(u['filename']==wheel['filename'] and u['digests']['sha256']==wheel['sha256'] and not u['yanked'] for f in (p/'candidate').glob('*-pypi.json') for u in json.loads(f.read_text())['urls']),'Wheel not bound to PyPI metadata')
checks=read('validation/CANDIDATE_CHECK_local_guard.json');upstream=read('validation/CANDIDATE_CHECK_upstream_5_6.json')
require(checks['status']=='PASS' and len(checks['checks'])==8 and all(x['passed'] for x in checks['checks']),'Final eight checks differ')
failures=[x['check'] for x in upstream['checks'] if not x['passed']]
require(upstream['status']=='FAIL' and failures==['false_trust_flag_blocks_local_dynamic_loader'],'Upstream disagreement not preserved')
require('No broken requirements found.' in (p/'validation/PIP_CHECK.log').read_text(),'pip check not passing')
versions=read('candidate/VERSION_DIFF.json');require(versions['baseline_distributions']==43 and versions['candidate_distributions']==43,'Top-level inventory count differs')
require(set(versions['changed'])=={'certifi','filelock','pillow','setuptools','sentence-transformers'},'Unexpected installed version changes')
require(set(versions['native_baseline_version_mismatches'])=={'sentence-transformers'},'Native mismatch differs')
preservation=read('validation/PRESERVATION_CHECK.json');require(preservation['status']=='PASS' and preservation['complete_inventory_and_hashes_match_before'] and preservation['changed']==[] and preservation['application_release_files_unchanged']==156,'Baseline preservation check differs')
counts['baseline_environment_entries_preserved']=preservation['baseline_environment_files_and_symlinks'];counts['release_files_preserved']=156
for file in (p/'code').glob('*.py'):ast.parse(file.read_text())
for file in p.glob('*.md'):
 for url in re.findall(r'\]\(([^)]+)\)',file.read_text()):
  if not url.startswith('https://'):require((file.parent/url).is_file(),'Broken Markdown link '+str(file.name)+':'+url)
result={'status':'FAIL' if errors else 'PASS','checks':counts,'errors':errors,'scope':'Offline artifact integrity/structure and recorded outcomes, not fresh inference, live scanner or scientific acceptance'}
print(json.dumps(result,indent=2));raise SystemExit(bool(errors))
