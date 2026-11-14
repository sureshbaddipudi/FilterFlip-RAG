"""Focused offline tests for uncertainty, joins, integrity, costs and write boundaries."""
import copy
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import analyze as a


class CalculationRules(unittest.TestCase):
    def test_unknown_is_neither_failure_nor_success(self):
        self.assertIsNone(a.core('uncertain'))
        self.assertEqual(a.paired(None, False), 'unresolved')
        self.assertEqual(a.paired(True, None), 'unresolved')

    def test_gain_and_loss_are_directional(self):
        self.assertEqual(a.paired(True, False), 'gain')
        self.assertEqual(a.paired(False, True), 'loss')
        self.assertEqual(a.paired(False, False), 'both_no')

    def test_core_does_not_require_support(self):
        self.assertTrue(a.core('correct-unsupported'))
        self.assertFalse(a.core('wrong'))
        with self.assertRaises(ValueError):
            a.core('unreviewed')

    def test_duplicate_join_rejected(self):
        rows = [{'case': 'a', 'arm': 'N'}, {'case': 'a', 'arm': 'N'}]
        with self.assertRaises(ValueError):
            a.index(rows, ['case', 'arm'])

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            a.decode('{"verdict":"yes","verdict":"no"}')

    def test_nonfinite_json_rejected(self):
        for value in ['NaN', 'Infinity', '-Infinity', '1e999']:
            with self.assertRaises(ValueError):
                a.decode('{"score":' + value + '}')

    def test_manifest_tampering_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'data').write_bytes(b'frozen')
            (root / 'manifest.json').write_text(json.dumps({'data': a.sha(b'frozen')}))
            self.assertEqual(a.verify_manifest('manifest.json', root), 1)
            (root / 'data').write_bytes(b'changed')
            with self.assertRaises(ValueError):
                a.verify_manifest('manifest.json', root)

    def test_traversal_and_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'real').write_text('data')
            (root / 'link').symlink_to(root / 'real')
            for name in ['../escape', '/etc/passwd', 'link']:
                with self.assertRaises(ValueError):
                    a.safe_file(root, name)

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                a.destination(td)

    def test_output_cannot_modify_release(self):
        with self.assertRaises(ValueError):
            a.destination(a.ROOT / 'new-output')

    def test_broken_journal_chain_rejected(self):
        original = a.safe_file(a.ROOT, 'inputs/execution/generation_run/journal.jsonl').read_text().splitlines()
        row = json.loads(original[-1])
        row['seconds'] += 1
        original[-1] = json.dumps(row)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / 'journal'
            p.write_text('\n'.join(original))
            with patch.object(a, 'safe_file', return_value=p):
                with self.assertRaisesRegex(ValueError, 'Broken journal'):
                    a.journal('ignored')


class FrozenEvidenceIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A network/subprocess attempt fails immediately during the real calculation.
        with patch.object(socket, 'socket', side_effect=RuntimeError('Network prohibited')), \
             patch.object(socket, 'create_connection', side_effect=RuntimeError('Network prohibited')), \
             patch.object(subprocess, 'Popen', side_effect=RuntimeError('Subprocess prohibited')):
            cls.files = a.calculate()
        cls.data = {name[:-5]: json.loads(content) for name, content in cls.files.items() if name.endswith('.json')}

    def test_current_and_historical_scoring_are_distinct(self):
        changes = self.data['validation']['category_changes']
        self.assertEqual(len(changes), 7)
        self.assertEqual(sum(r['logical_conditions'] for r in changes), 12)
        self.assertEqual(self.data['totals']['logical_categories']['uncertain'], 5)

    def test_r110_bounds_keep_one_shared_judgment(self):
        scenarios = self.data['sensitivity']
        def totals(name):
            return {(r['panel'], r['arm']): r['accepted_core'] for r in scenarios[name]['core_counts']
                    if r['dataset'] == r['condition'] == 'ALL'}
        lo, hi = totals('R110_all_five_unusable'), totals('R110_all_five_usable')
        diffs = {k: hi[k] - lo[k] for k in lo}
        self.assertEqual(sum(diffs.values()), 5)
        self.assertEqual(diffs['benign', 'N'], 1)
        self.assertEqual(diffs['benign', 'E'], 1)
        self.assertEqual(diffs['benign', 'CN'], 1)
        self.assertEqual(diffs['challenge', 'CN'], 2)
        self.assertEqual(self.data['totals']['distinct_categories']['uncertain'], 1)

    def test_cache_cost_counted_once_per_execution(self):
        cost = self.data['cost_tables']['generation']
        self.assertEqual(cost['fresh']['distinct_responses'], 67)
        self.assertEqual(cost['saved_historical_only']['distinct_responses'], 106)
        self.assertEqual(cost['logical_source_counts']['needs_new_generation'], 117)
        self.assertEqual(cost['logical_source_counts']['saved_exact_request'], 207)
        self.assertEqual(cost['fresh']['raw_reported_tokens']['eval_count'], 978)

    def test_harmful_tradeoff_is_not_only_net_count(self):
        rows = [r for r in self.data['challenge_tables']['harm_pairs']
                if r['comparison'] == 'CN_vs_N' and r['condition'] == 'wrong_answer_append']
        self.assertEqual({r['case_id'] for r in rows if r['harm_pair'] == 'new_harm'}, {'NanoNQ:test1009', 'NanoNQ:test929'})
        self.assertEqual({r['case_id'] for r in rows if r['harm_pair'] == 'avoided_harm'}, {'NanoNQ:test3108'})
        rows = [r for r in self.data['challenge_tables']['summary'] if r['dataset'] == 'ALL' and r['condition'] == 'wrong_answer_append']
        actual = {(r['subset'], r['arm']): (r['yes'], r['n']) for r in rows}
        self.assertEqual(actual['all_nine', 'CN'], (2, 9))
        self.assertEqual(actual['six_unflagged_secondary', 'CN'], (1, 6))

    def test_benign_pairs_reconcile_with_totals(self):
        row = next(r for r in self.data['paired_tables']['summary'] if r['panel'] == 'benign' and r['dataset'] == r['condition'] == 'ALL' and r['comparison'] == 'CN_vs_N')
        self.assertEqual(row['core'], {'gain': 7, 'loss': 8, 'both_yes': 31, 'both_no': 7, 'unresolved': 1})
        self.assertEqual(sum(row['core'].values()), 54)

    def test_filter_and_answer_denominators_are_separate(self):
        self.assertEqual(len(self.data['filter_tables']['details']), 322 * 5)
        self.assertEqual(len(self.data['paired_tables']['copy_vs_clean']), 18 * 4 * 2)
        self.assertEqual(len(self.data['challenge_tables']['matched_neutral_detail']), 72)

    def test_no_model_calls_in_analysis(self):
        self.assertEqual(self.data['validation']['research_calls_by_this_tool'], 0)
        self.assertIn('Woody Woodpecker', self.files['REPORT.md'].decode())

    def test_request_tampering_stops_analysis(self):
        original_read = a.read
        def changed_read(name, root=a.ROOT):
            obj = original_read(name, root)
            if name == 'inputs/scoring/LOGICAL_SCORING_MAP.json':
                obj['records'][0]['request_sha256'] = '0' * 64
            return obj
        with patch.object(a, 'read', side_effect=changed_read):
            with self.assertRaisesRegex(ValueError, 'join mismatch'):
                a.load_and_validate()


if __name__ == '__main__':
    unittest.main(verbosity=2)
