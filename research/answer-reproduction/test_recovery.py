import copy
import json
from pathlib import Path
import tempfile
import unittest
import recover_answers as r


class RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan,cls.original,cls.queue,cls.calls,cls.prior,cls.old_done=r.validate_release()
        cls.identity=r.identity_for(cls.plan)

    def response(self,job,reason='stop'):
        return dict(done=True,done_reason=reason,prompt_eval_count=job['call']['estimated_prompt_tokens'],
                    message=dict(content='SYNTHETIC TEST RESPONSE; NOT RESEARCH EVIDENCE'))

    def attempt(self,journal,job,reason='stop',finish=True):
        n=job['ordinal'];key=job['call']['request_sha256']
        journal.add('begin',ordinal=n,request_sha256=key,attempt_role=job['attempt_role'])
        if not finish:return None
        response=self.response(job,reason)
        record=dict(ordinal=n,request_sha256=key,status='truncated' if reason=='length' else 'ok',
                    answer=response['message']['content'],raw_response=response,attempt_role=job['attempt_role'])
        journal.add('done',ordinal=n,record=record)
        raw=r.c.canonical(response)
        return dict(request_sha256=key,response_sha256=r.c.sha(raw),response_bytes=len(raw),
                    response_base64=r.base64.b64encode(raw).decode())

    def test_queue_never_repeats_completed_prefix_or_durable_attempts(self):
        self.assertEqual([j['ordinal'] for j in self.queue],list(range(487,707)))
        previous={x['request_sha256'] for x in self.prior[:127]}|{x['request_sha256'] for x in self.old_done.values()}
        self.assertFalse(previous & {j['call']['request_sha256'] for j in self.queue})
        self.assertEqual(361+len(self.queue),581)

    def test_only_uncertain_487_receives_explicit_retry_role(self):
        self.assertEqual(self.queue[0]['attempt_role'],'explicit_user_authorized_retry_of_uncertain_487')
        self.assertTrue(all(j['attempt_role']=='previously_unattempted' for j in self.queue[1:]))
        self.assertTrue(all(j['call']['request']['options']['num_predict']==128 for j in self.queue))

    def test_unapproved_time_amendment_blocks_execution(self):
        plan=dict(self.plan,active_time_amendment_approved=False)
        with self.assertRaisesRegex(ValueError,'explicit approval'):r.require_execution_authority(plan)

    def test_approval_without_recorded_text_is_rejected(self):
        plan=dict(self.plan,active_time_amendment_approved=True,active_time_approval_text=None,retry_amendment_approved=True,retry_authorization='test approval')
        with self.assertRaises(ValueError):r.require_execution_authority(plan)

    def test_cumulative_accounting_and_preflight_allowance(self):
        self.assertEqual(5988+6494+600+60,self.plan['accounted_predecessor_seconds'])
        self.assertEqual(self.plan['accounted_predecessor_seconds']+self.plan['new_active_seconds_cap'],28800)
        self.assertIsNone(self.plan['v2_measured_total_active_seconds'])

    def test_clean_resume_preserves_done_and_counts_previous_time(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);j=r.c.Journal(out/'journal.jsonl',self.identity);j.add('session_start')
            for job,reason in zip(self.queue[:2],['stop','length']):r.c.append(out/'raw_responses.jsonl',self.attempt(j,job,reason))
            j.add('session_end',seconds=12.5)
            events,done,used=r.current_state(out,self.identity,self.queue)
            self.assertEqual(list(done),[487,488]);self.assertEqual(done[488]['status'],'truncated');self.assertEqual(used,12.5)

    def test_uncertain_new_attempt_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);j=r.c.Journal(out/'journal.jsonl',self.identity);j.add('session_start')
            self.attempt(j,self.queue[0],finish=False)
            with self.assertRaisesRegex(ValueError,'Uncertain'):r.current_state(out,self.identity,self.queue)

    def test_orphan_raw_response_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);j=r.c.Journal(out/'journal.jsonl',self.identity);j.add('session_start')
            capture=self.attempt(j,self.queue[0]);r.c.append(out/'raw_responses.jsonl',capture)
            # A separately captured response without a journal done must not be replayed.
            capture=dict(capture,request_sha256=self.queue[1]['call']['request_sha256']);r.c.append(out/'raw_responses.jsonl',capture)
            j.add('session_end',seconds=2)
            with self.assertRaisesRegex(ValueError,'Unreconciled'):r.current_state(out,self.identity,self.queue)

    def test_faulted_session_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);j=r.c.Journal(out/'journal.jsonl',self.identity);j.add('session_start');j.add('fault');j.add('session_end',seconds=1)
            with self.assertRaisesRegex(ValueError,'Faulted'):r.current_state(out,self.identity,self.queue)

    def test_stale_lock_blocks_resume_without_modification(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);r.c.save_new(out/'RUN.lock',{'pid':123});before=(out/'RUN.lock').read_bytes()
            with self.assertRaisesRegex(ValueError,'Lock'):r.current_state(out,self.identity,self.queue)
            self.assertEqual((out/'RUN.lock').read_bytes(),before)

    def test_journal_tamper_and_partial_line_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'journal';r.c.Journal(path,self.identity);raw=path.read_bytes()
            path.write_bytes(raw.replace(b'week04-recovery-v3',b'week04-recovery-v4'))
            with self.assertRaises(ValueError):r.verify_chain(path)
            path.write_bytes(raw[:-1])
            with self.assertRaises(ValueError):r.verify_chain(path)

    def test_changed_identity_blocks_resume(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);r.c.Journal(out/'journal.jsonl',{'wrong':'identity'})
            with self.assertRaisesRegex(ValueError,'identity'):r.current_state(out,self.identity,self.queue)

    def test_out_of_order_done_requests_block_resume(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);j=r.c.Journal(out/'journal.jsonl',self.identity);j.add('session_start')
            r.c.append(out/'raw_responses.jsonl',self.attempt(j,self.queue[1]));j.add('session_end',seconds=1)
            with self.assertRaisesRegex(ValueError,'order'):r.current_state(out,self.identity,self.queue)

    def test_full_synthetic_recovery_preserves_all_uncertain_attempts_and_128_truncations(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);j=r.c.Journal(out/'journal.jsonl',self.identity);j.add('session_start')
            for job in self.queue:self.attempt(j,job)
            j.add('session_end',seconds=10)
            summary=r.snapshot(out,self.calls,self.prior,self.old_done,j.events,self.plan)
            self.assertEqual(summary['effective_unique_status_counts'],{'ok':705,'truncated':1})
            self.assertEqual(summary['effective_unique_pending'],0)
            self.assertEqual(summary['total_fresh_attempts_begun_including_uncertain'],581)
            self.assertEqual(summary['original_128_and_retry_statuses'],['truncated','truncated'])
            attempts=json.loads((out/'ATTEMPT_LEDGER.json').read_text())
            self.assertEqual(len(attempts),581)
            both=[a for a in attempts if a['ordinal']==487]
            self.assertEqual([a['status'] for a in both],['uncertain_no_durable_response','ok'])
            self.assertEqual(len(json.loads((out/'COMBINED_LOGICAL_RESULTS.json').read_text())),1062)
            self.assertTrue(summary['all_recovery_requests_accounted_for'])


if __name__=='__main__':unittest.main(verbosity=2)
