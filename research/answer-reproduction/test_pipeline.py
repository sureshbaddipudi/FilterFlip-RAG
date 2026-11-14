import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock,patch
import run_pipeline as pipeline


class PipelineTests(unittest.TestCase):
    def run_case(self,generate_code,audit_code):
        with tempfile.TemporaryDirectory() as td:
            release=Path(td)/'release';release.mkdir()
            plan=dict(active_time_amendment_approved=True,active_time_approval_text='synthetic approval',
                      retry_amendment_approved=True,retry_authorization='synthetic approval',
                      recovery_output_name='test_run',new_active_seconds_cap=15658)
            generation=Mock(pid=123,wait=Mock(return_value=generate_code),poll=Mock(return_value=generate_code))
            audit=Mock(pid=124,wait=Mock(return_value=audit_code),poll=Mock(return_value=audit_code))
            with patch.object(pipeline.r,'ROOT',release),patch.object(pipeline.r,'validate_release',return_value=(plan,)),patch.object(pipeline.signal,'signal'),patch.object(pipeline.subprocess,'Popen',side_effect=[generation,audit]) as spawn:
                if generate_code or audit_code:
                    with self.assertRaises(RuntimeError):pipeline.main()
                else:pipeline.main()
                saved=json.loads((Path(td)/'FilterFlip_Week04_Recovery_v3_Pipeline_Status_2026-10-31.json').read_text())
                return saved,spawn.call_count

    def test_clean_generation_runs_offline_audit_once(self):
        state,count=self.run_case(0,0)
        self.assertEqual(state['status'],'complete');self.assertEqual(count,2)

    def test_generation_fault_stops_without_retry_or_audit(self):
        state,count=self.run_case(1,0)
        self.assertEqual(state['status'],'stopped_requires_inspection');self.assertEqual(count,1)

    def test_audit_failure_does_not_repeat_generation(self):
        state,count=self.run_case(0,1)
        self.assertEqual(state['status'],'stopped_requires_inspection');self.assertEqual(count,2)


if __name__=='__main__':unittest.main(verbosity=2)
