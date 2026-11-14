import base64,importlib.util,json,shutil,tempfile,unittest,time,signal
from pathlib import Path
from unittest.mock import Mock,patch
import run_task03 as r
import audit_task03 as a
import pipeline as pipeline_module
ROOT=r.ROOT
WORK=ROOT.parent.parent/'work/task03_implementation'

def seal(root):
    r.snapshot(root/'SHA256_MANIFEST.json',{str(p.relative_to(root)):r.sha(p) for p in sorted(root.rglob('*')) if p.is_file() and p!=root/'SHA256_MANIFEST.json' and '.tmp' not in p.name and not str(p.relative_to(root)).startswith('validation/')})

class Harness:
    def __init__(self,out,plan,queue,probe,behavior=None):
        self.out=out;self.plan=plan;self.queue=queue;self.probe=probe;self.seconds=0.;self.calls=[];self.behavior=behavior;self.closed=0
        self.rows={x['request_sha256']:x for x in [probe]+queue}
    def budget(self,used):return r.Budget(used=used,clock=lambda:self.seconds,alarms=False)
    def factory(self,out,model,budget):
        h=self
        class Fake:
            start_identity={'synthetic_transport':True}
            def identity(self):return self.start_identity
            def chat(self,req):
                key=r.digest(r.canonical(req));h.calls.append(key);h.seconds+=.1
                row=h.rows[key];response=dict(model=model['name'],done=True,message={'content':'Synthetic answer '+str(len(h.calls))},prompt_eval_count=row['estimated_prompt_tokens'],eval_count=8,done_reason='stop')
                if h.behavior:return h.behavior(len(h.calls)-1,response)
                return 200,r.canonical(response)
            def loaded_cpu(self):return dict(models=[dict(name=model['name'],digest=model['digest'],size_vram=0)])
            def close(self):h.closed+=1
        return Fake()
    def run(self,j,max_jobs=None):return r.run_session(self.out,j,self.plan,self.queue,[],self.probe,self.factory,self.budget,max_jobs=max_jobs)

class Task03Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan,cls.queue,cls.logical,cls.probe=r.validate_release()
    def setUp(self):
        self.fsync_patch=patch.object(r.os,'fsync');self.fsync_mock=self.fsync_patch.start()
        self.temp=tempfile.TemporaryDirectory(dir=WORK);self.p=Path(self.temp.name);self.out=self.p/'run';self.out.mkdir()
        self.j=r.Journal(self.out/'journal.jsonl',r.identity_for(),create=True)
    def tearDown(self):self.temp.cleanup();self.fsync_patch.stop()
    def harness(self,behavior=None):return Harness(self.out,self.plan,self.queue,self.probe,behavior)
    def test_exact_approved_requests_and_native_empty_context(self):
        self.assertEqual(len(self.logical),72);self.assertEqual(len(self.queue),60)
        empty=[x for x in self.logical if x['arm']=='T' and not x['chunk_ids']]
        self.assertEqual(len(empty),3);self.assertEqual(len({x['request_sha256'] for x in empty}),1)
        mulberry=next(x for x in self.logical if x['case_id']=='NanoNQ:test2247' and x['condition']=='C' and x['arm']=='T')
        self.assertEqual(mulberry['native_input_indices'],[3,4,1])
    def test_all_attempts_raw_links_and_audit_do_not_inherit_historical_answers(self):
        h=self.harness();h.run(self.j);self.assertEqual(len(h.calls),61);self.assertEqual(len(set(h.calls)),61)
        self.assertGreater(self.fsync_mock.call_count,180)
        summary=a.audit(ROOT,self.out,self.p/'audit')
        self.assertEqual(summary['unique_status_counts'],{'ok':60});self.assertEqual(summary['logical_status_counts'],{'ok':72})
        self.assertEqual(summary['historical_reference_exact_matches'],0)
        for row in r.read(self.p/'audit/LOGICAL_RESULTS.json'):self.assertFalse(row['historical_answer_used_for_primary'])
        packet=r.read(next((self.p/'audit/cases').glob('*.json')))
        self.assertTrue(all(v is None for v in packet['endpoint_review'].values()))
    def test_clean_durable_prefix_skipped_without_second_preflight(self):
        h=self.harness();h.run(self.j,max_jobs=3);self.assertEqual(len(h.calls),4)
        reopened=r.Journal(self.out/'journal.jsonl',r.identity_for());h.run(reopened)
        self.assertEqual(len(h.calls),61);self.assertEqual(len(set(h.calls)),61)
        self.assertEqual(len([e for e in reopened.events if e['kind']=='session_end']),2)
    def test_study_length_stop_preserved_and_queue_continues(self):
        def behavior(i,response):
            if i==1:response.update(done_reason='length',eval_count=128)
            return 200,r.canonical(response)
        h=self.harness(behavior);h.run(self.j)
        _,done,_,_=r.validate_state(self.out,self.j,self.queue,self.probe)
        self.assertEqual(done[1]['status'],'truncated');self.assertEqual(len(done),61)
    def test_synthetic_length_stop_prevents_study(self):
        def behavior(i,response):response['done_reason']='length';return 200,r.canonical(response)
        h=self.harness(behavior)
        with self.assertRaises(ValueError):h.run(self.j)
        self.assertEqual(len(h.calls),1)
    def test_malformed_empty_wrong_model_tokens_overflow_and_http_stop(self):
        cases=['malformed','empty','model','tokens','overflow','http','json_duplicate','not_done','unknown_reason']
        for case in cases:
            with self.subTest(case=case),tempfile.TemporaryDirectory(dir=WORK) as tmp:
                out=Path(tmp);j=r.Journal(out/'journal.jsonl',r.identity_for(),create=True)
                def behavior(i,response):
                    if case=='malformed':return 200,b'not-json'
                    if case=='empty':response['message']['content']=' '
                    if case=='model':response['model']='other'
                    if case=='tokens':response['prompt_eval_count']+=17
                    if case=='overflow':response['prompt_eval_count']=4096
                    if case=='http':return 500,b'{"error":"synthetic fault"}'
                    if case=='json_duplicate':return 200,b'{"done":true,"done":false}'
                    if case=='not_done':response['done']=False
                    if case=='unknown_reason':response['done_reason']='other'
                    return 200,r.canonical(response)
                h=Harness(out,self.plan,self.queue,self.probe,behavior)
                with self.assertRaises((ValueError,json.JSONDecodeError)):h.run(j)
                self.assertEqual(len(h.calls),1);self.assertEqual(h.closed,1)
    def test_timeout_and_operator_interruption_are_consumed_not_retried(self):
        for error in [TimeoutError('synthetic'),InterruptedError('synthetic')]:
            with self.subTest(error=error),tempfile.TemporaryDirectory(dir=WORK) as tmp:
                out=Path(tmp);j=r.Journal(out/'journal.jsonl',r.identity_for(),create=True)
                def fail(i,response):raise error
                h=Harness(out,self.plan,self.queue,self.probe,fail)
                with self.assertRaises(type(error)):h.run(j)
                self.assertEqual(sum(e['kind']=='begin' for e in j.events),1)
                with self.assertRaises(ValueError):h.run(j)
                self.assertEqual(len(h.calls),1)
    def test_unclosed_session_and_ambiguous_begin_refuse_resume(self):
        self.j.add('session_start',unix=0);self.j.add('begin',ordinal=0,request_sha256=self.probe['request_sha256'])
        with self.assertRaisesRegex(ValueError,'Unclosed'):r.validate_state(self.out,self.j,self.queue,self.probe,resume=True)
        self.j.add('session_end',seconds=.1,faulted=False)
        with self.assertRaisesRegex(ValueError,'Ambiguous'):r.validate_state(self.out,self.j,self.queue,self.probe,resume=True)
    def test_corrupted_chain_and_trailing_partial_record_rejected(self):
        p=self.out/'journal.jsonl';p.write_bytes(p.read_bytes().replace(b'identity',b'identitY',1))
        with self.assertRaises(ValueError):r.Journal(p,r.identity_for())
        p.write_bytes(b'{')
        with self.assertRaisesRegex(ValueError,'Partial'):r.Journal(p,r.identity_for())
    def test_raw_capture_corruption_missing_duplicate_and_orphan_rejected(self):
        h=self.harness();h.run(self.j,max_jobs=1);path=self.out/'raw_responses.jsonl';original=path.read_bytes();raw=r.lines(path)
        for mode in ['changed','missing','duplicate','orphan']:
            with self.subTest(mode=mode):
                path.write_bytes(original)
                if mode=='changed':
                    x=raw[0].copy();x['response_base64']=base64.b64encode(b'bad').decode();path.write_bytes(r.canonical(x)+b'\n'+b'\n'.join(r.canonical(x) for x in raw[1:])+b'\n')
                if mode=='missing':path.write_bytes(b'')
                if mode in ['duplicate','orphan']:r.append(path,raw[0])
                with self.assertRaises(ValueError):r.validate_state(self.out,self.j,self.queue,self.probe,resume=True)
    def test_duplicate_done_and_out_of_plan_attempt_rejected(self):
        h=self.harness();h.run(self.j,max_jobs=1)
        rec=next(x for x in self.j.events if x['kind']=='done');self.j.add('done',ordinal=rec['ordinal'],record=rec['record'])
        with self.assertRaises(ValueError):r.validate_state(self.out,self.j,self.queue,self.probe)
    def test_time_cap_includes_preflight_and_resumed_elapsed(self):
        clock=[0.];b=r.Budget(used=7199,clock=lambda:clock[0],alarms=False);self.assertEqual(b.remaining(),1.)
        clock[0]=1.
        with self.assertRaisesRegex(ValueError,'allowance'):b.check()
        h=self.harness();h.run(self.j,max_jobs=0)
        self.assertEqual(len(h.calls),1)
        _,_,used,_=r.validate_state(self.out,self.j,self.queue,self.probe)
        self.assertAlmostEqual(used,.1)
    def test_wrong_served_version_digest_template_and_gpu_rejected(self):
        model=self.plan['model'];backend=object.__new__(r.Backend);backend.model=model
        valid={'version':{'version':model['ollama_version']},'tags':{'models':[dict(name=model['name'],digest=model['digest'])]},'show':{'template':r.read(ROOT/'design/evidence/answer_model_setup.json')['template']}}
        for field in ['version','digest','template']:
            data=json.loads(json.dumps(valid))
            if field=='version':data['version']['version']='0'
            if field=='digest':data['tags']['models'][0]['digest']='bad'
            if field=='template':data['show']['template']='bad'
            backend.api=lambda endpoint,payload=None:data[endpoint]
            with self.assertRaises(ValueError):backend.identity()
        backend.api=lambda *x:dict(models=[dict(name=model['name'],digest=model['digest'],size_vram=1)])
        with self.assertRaises(ValueError):backend.loaded_cpu()
    def test_source_mutation_refused_before_model_transport(self):
        clone=self.p/'release';shutil.copytree(ROOT,clone)
        with (clone/'design/checks/DRAFT_LOGICAL_REQUESTS.jsonl').open('ab') as f:f.write(b' ')
        with self.assertRaisesRegex(ValueError,'Release changed'):r.validate_release(clone)
    def test_cleanup_targets_only_owned_process_group(self):
        backend=object.__new__(r.Backend);backend.process=Mock(pid=1234567);backend.log=Mock()
        with patch.object(r.os,'killpg') as stop:backend.close()
        stop.assert_called_once_with(1234567,r.signal.SIGKILL);backend.process.wait.assert_called_once()
    def test_occupied_port_prevents_service_launch(self):
        fake=Mock();fake.__enter__=Mock(return_value=fake);fake.__exit__=Mock(return_value=False);fake.connect_ex.return_value=0
        with patch.object(r.socket,'socket',return_value=fake),patch.object(r.subprocess,'Popen') as spawn:
            with self.assertRaisesRegex(ValueError,'port occupied'):r.Backend(self.out,self.plan['model'],r.Budget(alarms=False))
            spawn.assert_not_called()
    def test_pipeline_audit_failure_never_reruns_generation(self):
        clone=self.p/'release';clone.mkdir();children=[Mock(pid=1),Mock(pid=2)];children[0].wait.return_value=0;children[1].wait.return_value=1
        for child in children:child.poll.return_value=0
        spawn=Mock(side_effect=children)
        with patch.object(r,'validate_release',return_value=None):
            with self.assertRaisesRegex(ValueError,'audit stopped'):pipeline_module.pipeline(root=clone,spawn=spawn)
        self.assertEqual(spawn.call_count,2)
        self.assertIn('run_task03.py',spawn.call_args_list[0].args[0][3]);self.assertIn('audit_task03.py',spawn.call_args_list[1].args[0][2])
        self.assertEqual(r.read(self.p/'FilterFlip_Task03_Pipeline_Status_2026-10-31.json')['status'],'stopped_requires_inspection')

    def test_real_deadline_interrupts_blocking_operation(self):
        original=signal.getsignal(signal.SIGALRM)
        def expired(signum,frame):raise TimeoutError('synthetic alarm')
        signal.signal(signal.SIGALRM,expired)
        b=r.Budget(cap=1)
        try:
            with self.assertRaises(TimeoutError):
                with b.limit(.03):time.sleep(.2)
        finally:b.cancel();signal.signal(signal.SIGALRM,original)
    def test_attempt_cap_and_unknown_ordinal_rejected(self):
        self.j.add('session_start',unix=0)
        self.j.add('begin',ordinal=61,request_sha256=self.probe['request_sha256'])
        with self.assertRaisesRegex(ValueError,'attempt'):r.validate_state(self.out,self.j,self.queue,self.probe)

if __name__=='__main__':unittest.main(verbosity=2)
