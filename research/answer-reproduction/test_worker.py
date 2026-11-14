import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import launch_worker as launcher


class WorkerTests(unittest.TestCase):
    def test_unapproved_amendment_cannot_spawn_worker(self):
        plan=dict(active_time_amendment_approved=False,active_time_approval_text=None,
                  retry_amendment_approved=False,retry_authorization=None)
        with patch.object(launcher.r,'validate_release',return_value=(plan,)),patch.object(launcher.subprocess,'Popen') as spawn:
            with self.assertRaises(ValueError):launcher.main()
            spawn.assert_not_called()

    def test_single_logged_detached_launch_refuses_duplicate(self):
        plan=dict(active_time_amendment_approved=True,active_time_approval_text='synthetic test approval',
                  retry_amendment_approved=True,retry_authorization='synthetic test approval',recovery_output_name='test_run')
        with tempfile.TemporaryDirectory() as td:
            release=Path(td)/'release';release.mkdir();(release/'SHA256_MANIFEST.json').write_text('{}')
            with patch.object(launcher.r,'ROOT',release),patch.object(launcher.r,'validate_release',return_value=(plan,)),patch.object(launcher.subprocess,'Popen',return_value=Mock(pid=999999)) as spawn,contextlib.redirect_stdout(io.StringIO()):
                launcher.main()
                self.assertTrue(spawn.call_args.kwargs['start_new_session'])
                self.assertEqual(spawn.call_args.kwargs['stdin'],launcher.subprocess.DEVNULL)
                self.assertEqual(Path(spawn.call_args.args[0][-1]).name,'run_pipeline.py')
                with self.assertRaisesRegex(ValueError,'evidence exists'):launcher.main()
                spawn.assert_called_once()
            self.assertTrue((Path(td)/'FilterFlip_Week04_Recovery_v3_Worker_2026-10-31.json').exists())


if __name__=='__main__':unittest.main(verbosity=2)
