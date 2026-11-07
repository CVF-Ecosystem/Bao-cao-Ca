import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import check_project_workspace as checker

ROOT = Path(__file__).resolve().parents[1]


class NativeOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = (ROOT / 'docs/reviews/core-reconciliation/native-admitted.txt').read_text(encoding='utf-8-sig')

    def test_actual_native_output_and_corruption(self):
        self.assertTrue(checker.native_pass(self.native, 0))
        first = '  Project folder exists                              [PASS]'
        variants = [self.native.replace(first, ''), self.native.replace(first, first + '\n' + first),
                    self.native.replace('[PASS]', '[FAIL]', 1), self.native.replace('[PASS]', '[WARN]', 1),
                    self.native.replace('RESULT: PASS (29/29 checks passed)', 'RESULT: PASS (28/29 checks passed)'),
                    self.native + '\nRESULT: FAIL (0/29 checks passed)\n',
                    self.native + '\n  Unknown check [FAIL]\n', self.native[:150]]
        variants += [self.native + '\nUnexpected [' + token + ']\n'
                     for token in ('fail', 'Warn', 'error', 'UNKNOWN', 'PASS')]
        variants += [self.native + '\nUnexpected [fail] trailing data\n',
                     self.native + '\nUnexpected [Warn\n',
                     self.native + '\nWARNING: merged child-process diagnostic\n',
                     self.native + '\nError: merged child-process diagnostic\n',
                     self.native + '\nresult: FAIL (0/29 checks passed)\n',
                     self.native + '\nResult : FAIL (0/29 checks passed)\n']
        for variant in variants:
            with self.subTest(variant=variant[-70:]):
                self.assertFalse(checker.native_pass(variant, 0))
        self.assertFalse(checker.native_pass(self.native, 1))

    def test_bootstrap_control_set(self):
        rows = [dict(controlId=x, outcome='PASS', ok=True, findings=[]) for x in checker.BOOTSTRAP_CONTROLS]
        data = dict(phase='bootstrap', exitCode=0, results=rows)
        def result(value, code=0):
            return dict(exitCode=code, output=json.dumps(value))
        self.assertTrue(checker.bootstrap_pass(result(data)))
        for mutate in ('missing', 'duplicate', 'not_applicable', 'finding', 'phase', 'exit'):
            changed = json.loads(json.dumps(data))
            if mutate == 'missing': changed['results'].pop()
            if mutate == 'duplicate': changed['results'].append(changed['results'][0])
            if mutate == 'not_applicable': changed['results'][2]['outcome'] = 'NOT_APPLICABLE_WITH_REASON'
            if mutate == 'finding': changed['results'][0]['findings'] = [{'code': 'BAD'}]
            if mutate == 'phase': changed['phase'] = 'pre-dispatch'
            if mutate == 'exit': changed['exitCode'] = 1
            with self.subTest(mutate=mutate): self.assertFalse(checker.bootstrap_pass(result(changed)))
        self.assertFalse(checker.bootstrap_pass(result(data, 1)))


class CoreIdentityTests(unittest.TestCase):
    def test_disposable_repo_identity_and_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); core = root / 'core'; core.mkdir()
            def git(*args):
                return subprocess.run(['git', '-C', str(core), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
            git('init', '-q'); git('config', 'user.email', 'fixture@example.invalid'); git('config', 'user.name', 'Fixture')
            git('remote', 'add', 'origin', 'https://example.invalid/core.git')
            for path in checker.CORE_FILES:
                f = core / path; f.parent.mkdir(parents=True, exist_ok=True); f.write_text('fixture\n', encoding='utf-8')
            git('add', '.'); git('commit', '-qm', 'fixture'); head = git('rev-parse', 'HEAD')
            manifest = dict(cvfCoreCommit=head, cvfCoreRelativePath='core', cvfCoreRepository='https://example.invalid/core.git')
            with patch.object(checker, 'ROOT', root):
                self.assertEqual(checker.verify_core(manifest), core)
                for bad in [dict(manifest, cvfCoreCommit='0'*40), dict(manifest, cvfCoreRepository='https://example.invalid/other')]:
                    with self.assertRaises(ValueError): checker.verify_core(bad)
                (core / checker.CORE_FILES[0]).write_text('tampered\n', encoding='utf-8')
                with self.assertRaises(ValueError): checker.verify_core(manifest)


class DelegationTests(unittest.TestCase):
    def test_fail_closed_and_explicit_packet(self):
        native = (ROOT / 'docs/reviews/core-reconciliation/native-admitted.txt').read_text(encoding='utf-8-sig')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / '.cvf').mkdir(); pin = 'a'*40
            def put(name, value): (root / '.cvf' / name).write_text(json.dumps(value), encoding='utf-8')
            put('manifest.json', dict(cvfCoreCommit=pin))
            put('policy.json', dict(workspaceActivationSourcePolicy='CORE_AND_SUPPLEMENTAL', workspaceActivationExecutableSource='PINNED_CORE'))
            put('gate-profile.lock.json', dict(profileSha256='b'*64, runnerSha256='c'*64, bundleSha256='d'*64))
            put('workspace-activation.json', dict(actions=[dict(packet='docs/work_orders/WO.md')]))
            activation = dict(status='CURRENT_ASSESSED', identity=dict(sourceRoute='PINNED_CORE', coreCommit=pin),
                              sourcePolicy='CORE_AND_SUPPLEMENTAL', delivery=dict(mode='CORE_AND_SUPPLEMENTAL'),
                              supplementalRequirement=dict(mode='INSPECTED'), findings=[])
            controls = [dict(controlId=x, outcome='PASS', ok=True, findings=[]) for x in checker.BOOTSTRAP_CONTROLS]
            replies = [dict(exitCode=0, output=json.dumps(activation)), dict(exitCode=0, output=native),
                       dict(exitCode=0, output=json.dumps(dict(phase='bootstrap', exitCode=0, results=controls)))]
            with patch.object(checker, 'ROOT', root), patch.object(checker, 'verify_core', return_value=root/'core'):
                with patch.object(checker, 'invoke', side_effect=replies) as invoke:
                    result = checker.run()
                self.assertEqual(result['status'], 'CORE_ASSESSED')
                cmd = invoke.call_args_list[2].args[0]
                self.assertIn('--trusted', cmd); self.assertIn('--no-receipt', cmd)
                self.assertEqual(cmd[-2:], ['--packet', 'docs/work_orders/WO.md'])
                for bad in ('REVIEW_REQUIRED', 'BLOCKED_INVALID_INPUT'):
                    rejected = dict(replies[0], exitCode=2, output=json.dumps(dict(status=bad)))
                    with patch.object(checker, 'invoke', return_value=rejected):
                        self.assertEqual(checker.run()['status'], 'FAIL')
                with patch.object(checker, 'invoke', return_value=dict(exitCode=0, output='[]')):
                    self.assertEqual(checker.run()['status'], 'FAIL')
                malformed = dict(exitCode=0, output=json.dumps(dict(phase='bootstrap', exitCode=0, results=[None])))
                with patch.object(checker, 'invoke', side_effect=[replies[0], replies[1], malformed]):
                    self.assertEqual(checker.run()['status'], 'FAIL')
                put('workspace-activation.json', dict(actions=[]))
                with patch.object(checker, 'invoke', side_effect=replies[:2]):
                    self.assertEqual(checker.run()['status'], 'FAIL')
                put('policy.json', dict(workspaceActivationSourcePolicy='CORE_ONLY', workspaceActivationExecutableSource='PINNED_CORE'))
                with patch.object(checker, 'invoke') as invoke:
                    self.assertEqual(checker.run()['status'], 'FAIL'); invoke.assert_not_called()


if __name__ == '__main__':
    unittest.main()
