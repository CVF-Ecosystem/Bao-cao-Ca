import importlib.util
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('workspace_check', ROOT / 'scripts/check_project_workspace.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class CheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = checker.run()
        assert cls.actual['status'] == 'COMPATIBLE_ASSESSED', cls.actual.get('error')
        cls.output = cls.actual['legacyDoctor']['output']

    def test_exact_legacy_and_variants(self):
        self.assertTrue(checker.legacy_compatible(self.output, 1))
        for changed in [
            self.output.replace('Project folder exists', 'Missing project folder'),
            self.output.replace('Project folder exists', 'Project folder exists\n  Project folder exists [PASS]'),
            self.output.replace('CVF public core matches origin/main                [PASS]', 'CVF public core matches origin/main                [FAIL]'),
            self.output.replace('COV_OBJECT_SHAPE@docs/work_orders/WO_WORKSPACE_ACTIVATION.md', 'OTHER@docs/work_orders/WO_WORKSPACE_ACTIVATION.md'),
            self.output.replace('26/28 checks passed, 2 failed', '27/28 checks passed, 1 failed'),
            self.output + '\n         -> UNEXPECTED [FAIL]\n',
        ]:
            self.assertFalse(checker.legacy_compatible(changed, 1))
        self.assertFalse(checker.legacy_compatible(self.output, 0))
        single = self.output.replace('Gate CVF-DG-COV-01                                 [FAIL]', 'Gate CVF-DG-COV-01                                 [PASS]')
        single = single.replace('         -> COV_OBJECT_SHAPE@docs/roadmaps/WORKSPACE_ACTIVATION.md; COV_OBJECT_SHAPE@docs/work_orders/WO_WORKSPACE_ACTIVATION.md [FAIL]\n', '')
        single = single.replace('26/28 checks passed, 2 failed', '27/28 checks passed, 1 failed')
        self.assertTrue(checker.legacy_compatible(single, 1))

    def test_activation_receipt_and_source_fail_closed(self):
        activation = self.actual['activation']
        for modified in [dict(activation, exitCode=2), dict(activation, output=activation['output'].replace('CURRENT_ASSESSED', 'REVIEW_REQUIRED')), dict(activation, output=activation['output'].replace('AUTHORIZED_SUPPLEMENTAL', 'UNVERIFIED'))]:
            with patch.object(checker, 'invoke', return_value=modified) as call:
                self.assertEqual(checker.run()['status'], 'FAIL')
                self.assertEqual(call.call_count, 1)
        original = checker.digest
        with patch.object(checker, 'invoke', return_value=activation), patch.object(checker, 'digest', side_effect=lambda path, normalized=True: 'tampered' if path.name == 'cvf_downstream_gate_runner.py' else original(path, normalized)):
            self.assertEqual(checker.run()['status'], 'FAIL')

    def test_extra_status_rows_and_conflicting_summaries(self):
        for indentation in ['', ' ', '   ', '\t']:
            for status in ['PASS', 'FAIL', 'WARN', 'ERROR']:
                with self.subTest(indentation=repr(indentation), status=status):
                    changed = self.output + '\n' + indentation + 'Unexpected check [' + status + ']\n'
                    self.assertFalse(checker.legacy_compatible(changed, 1))
        for extra in ['RESULT: PASS', ' RESULT: FAIL (27/28 checks passed, 1 failed)', 'RESULT: unrecognized']:
            self.assertFalse(checker.legacy_compatible(self.output + '\n' + extra + '\n', 1))
        changed = self.output.replace('Gate CVF-DG-CONT-01                                [PASS]', 'Gate CVF-DG-CONT-01                                [FAIL]')
        self.assertNotEqual(changed, self.output)
        self.assertFalse(checker.legacy_compatible(changed, 1))
        for changed in [
            self.output.replace('COV_OBJECT_SHAPE@docs/roadmaps/WORKSPACE_ACTIVATION.md;', 'COV_OBJECT_SHAPE@docs/third.md; COV_OBJECT_SHAPE@docs/roadmaps/WORKSPACE_ACTIVATION.md;'),
            self.output.replace('  Project folder exists                              [PASS]\n', ''),
        ]:
            self.assertNotEqual(changed, self.output)
            self.assertFalse(checker.legacy_compatible(changed, 1))

    def test_current_control_inventory_and_coherence(self):
        baseline = json.loads(self.actual['supplementalBootstrap']['output'])
        for change in ['missing', 'duplicate', 'contradictory', 'findings']:
            data = json.loads(json.dumps(baseline))
            if change == 'missing':
                data['results'].pop()
            elif change == 'duplicate':
                data['results'].append(data['results'][0])
            elif change == 'contradictory':
                data['results'][0]['outcome'] = 'FAIL'
            else:
                data['results'][0]['findings'] = [{'code': 'unexpected'}]
            bad = dict(self.actual['supplementalBootstrap'], output=json.dumps(data))
            with self.subTest(change=change), patch.object(checker, 'invoke', side_effect=[self.actual['activation'], self.actual['legacyDoctor'], bad]):
                self.assertEqual(checker.run()['status'], 'FAIL')

    def test_timeout_and_bootstrap_failure(self):
        with patch.object(checker, 'invoke', side_effect=subprocess.TimeoutExpired('test', 60)):
            self.assertEqual(checker.run()['status'], 'FAIL')
        bad = dict(self.actual['supplementalBootstrap'], exitCode=1)
        with patch.object(checker, 'invoke', side_effect=[self.actual['activation'], self.actual['legacyDoctor'], bad]):
            self.assertEqual(checker.run()['status'], 'FAIL')
        data = json.loads(self.actual['supplementalBootstrap']['output'])
        data['results'][0]['ok'] = False
        bad = dict(self.actual['supplementalBootstrap'], output=json.dumps(data))
        with patch.object(checker, 'invoke', side_effect=[self.actual['activation'], self.actual['legacyDoctor'], bad]):
            self.assertEqual(checker.run()['status'], 'FAIL')

if __name__ == '__main__':
    unittest.main()
