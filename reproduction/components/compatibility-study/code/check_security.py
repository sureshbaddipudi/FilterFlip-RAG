#!/usr/bin/env python3
"""Task 9 benign targeted checks in the unchanged Task 5 candidate. No weights or untrusted code."""
from pathlib import Path
import argparse,copy,hashlib,io,json,os,ssl,sys,sysconfig,tempfile
from unittest.mock import patch
P=Path(__file__).resolve().parent.parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--label',choices=['normal','optimized'],default='normal');a=ap.parse_args();tempfile.tempdir=str(a.work/'tmp');os.environ['TMPDIR']=tempfile.tempdir
 sys.path.insert(0,str(P/'candidate_app'));from runtime_profile import verify_runtime_profile
 profile=json.loads((P/'profiles/candidate.json').read_text());baseline=json.loads((P/'profiles/baseline.json').read_text());identity=verify_runtime_profile(profile)
 import setuptools,certifi,filelock,torch,transformers,sentence_transformers
 from PIL import Image,UnidentifiedImageError
 from sentence_transformers import SentenceTransformer
 from sentence_transformers.util.misc import import_module_class
 checks=[]
 def record(name,ok,detail):checks.append({'check':name,'passed':bool(ok),'detail':detail})
 def rejected(call,expected=(ValueError,)):
  try:call();return False,None
  except expected as e:return True,{'type':type(e).__name__,'message':str(e)}
 paths={n:str(sys.modules[n].__file__) for n in ['certifi','filelock','PIL','torch','transformers','sentence_transformers']}
 record('candidate_package_isolation',sys.prefix!=sys.base_prefix and all(Path(x).is_relative_to(sys.prefix) for x in paths.values()),paths)
 record('candidate_profile_and_guard_identity',bool(identity),identity)
 ok,e=rejected(lambda:verify_runtime_profile(baseline));record('original_version_profile_refuses_candidate',ok and 'sentence-transformers' in e['message'],e)
 bad=copy.deepcopy(profile);bad['candidate_identity']['local_guard_sha256']='0'*64;ok,e=rejected(lambda:verify_runtime_profile(bad));record('candidate_profile_refuses_wrong_guard_hash',ok,e)
 old_bundle=Path(sys.base_prefix)/'lib/python3.11/site-packages/certifi/cacert.pem';contains=lambda file:any('emSign ECC Root CA - G3' in str(x.get('subject')) for x in ssl.create_default_context(cafile=str(file)).get_ca_certs());record('affected_CA_root_removed',contains(old_bundle) and not contains(certifi.where()),{'baseline_has_root':contains(old_bundle),'candidate_has_root':contains(certifi.where()),'scope':'Local bundle membership only'})
 with tempfile.TemporaryDirectory(dir=a.work/'tmp') as tmp:
  root=Path(tmp)
  for name,pathref in [('false_trust_existing_local',str(root)),('false_trust_missing_path',str(root/'missing')),('namespace_prefix_confusable',str(root))]:
   calls=[]
   with patch('transformers.dynamic_module_utils.get_class_from_dynamic_module',side_effect=lambda *a,**k:calls.append('dynamic')),patch('sentence_transformers.util.misc.import_from_string',side_effect=lambda *a,**k:calls.append('fallback')):
    ok,e=rejected(lambda:import_module_class('sentence_transformers_evil.Sentinel' if name=='namespace_prefix_confusable' else 'filterflip_fixture.Sentinel',pathref,trust_remote_code=False,local_files_only=True))
   record(name,ok and not calls,{'loader_calls':calls,'error':e})
  class Sentinel:pass
  calls=[]
  def stub(*a,**k):calls.append('dynamic');return Sentinel
  with patch('transformers.dynamic_module_utils.get_class_from_dynamic_module',side_effect=stub):value=import_module_class('filterflip_fixture.Sentinel',str(root),trust_remote_code=True,local_files_only=True)
  record('explicit_trust_stub_preserved',value is Sentinel and calls==['dynamic'],'Harmless in-process stub; no custom file executed')
  value=import_module_class('sentence_transformers.models.Pooling',str(root),trust_remote_code=False,local_files_only=True);record('installed_builtin_alias_resolves',value.__name__=='Pooling','Installed class lookup, no model weights')
  fixture=root/'synthetic';fixture.mkdir();(fixture/'modules.json').write_text(json.dumps([{'idx':0,'name':'0','path':'','type':'filterflip_fixture.Sentinel'}]));(fixture/'config_sentence_transformers.json').write_text(json.dumps({'model_type':'SentenceTransformer'}))
  calls=[]
  with patch('transformers.dynamic_module_utils.get_class_from_dynamic_module',side_effect=lambda *a,**k:calls.append('dynamic')),patch('sentence_transformers.util.misc.import_from_string',side_effect=lambda *a,**k:calls.append('fallback')):
   ok,e=rejected(lambda:SentenceTransformer(str(fixture),device='cpu',local_files_only=True,trust_remote_code=False))
  record('actual_constructor_rejects_custom_module_before_loader',ok and not calls and 'explicit trust_remote_code' in e['message'],{'loader_calls':calls,'error':e,'weights_loaded':False})
  (fixture/'modules.json').write_text('{"broken":');ok,e=rejected(lambda:SentenceTransformer(str(fixture),device='cpu',local_files_only=True,trust_remote_code=False),(ValueError,));record('malformed_module_config_fails_closed',ok,e)
  lock=root/'lock'
  with filelock.FileLock(lock):
   try:filelock.FileLock(lock).acquire(timeout=0);exclusive=False
   except filelock.Timeout:exclusive=True
  record('benign_exclusive_file_lock',exclusive,'Two instances; not hostile-filesystem race coverage')
  with filelock.FileLock(lock,timeout=1):record('lock_reacquirable_after_release',True,'Same workspace file')
  stream=io.BytesIO();Image.new('RGB',(3,3),(12,34,56)).save(stream,format='PNG');raw=stream.getvalue()
  with Image.open(io.BytesIO(raw)) as im:im.load();record('synthetic_PNG_roundtrip',im.size==(3,3) and im.getpixel((0,0))==(12,34,56),'3x3 RGB image only')
  ok,e=rejected(lambda:Image.open(io.BytesIO(raw[:12])).load(),(OSError,UnidentifiedImageError));record('truncated_synthetic_PNG_rejected',ok,e)
  with patch.object(Image,'MAX_IMAGE_PIXELS',2):ok,e=rejected(lambda:Image.open(io.BytesIO(raw)),(Image.DecompressionBombError,))
  record('synthetic_image_pixel_limit_active',ok,e)
 report={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'count':len(checks),'scientific_model_weights_loaded':0,'custom_code_files_executed':0,'scope':'Selected benign/helper and constructor checks, not full exploit prevention or all advisory closure'}
 (P/'results'/('SECURITY_CHECKS_'+a.label+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':[(c['check'],c['passed']) for c in checks]},indent=2));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
