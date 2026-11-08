"""Metadata, cổng Git và launcher thật; tất cả dữ liệu thử nằm trong thư mục tạm."""
import json
import io
from pathlib import Path
import subprocess
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

from THIET_LAP import VERSION, build_info
from BAO_CAO_CA import parse_args
from cong_cu import DONG_GOI
from cong_cu.KIEM_THU_KHOI import smoke


class ReleaseTests(unittest.TestCase):
    def test_metadata_loader_source_and_frozen(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(build_info(root, False), dict(commit='nguon', built_at='', version=VERSION))
            self.assertEqual(build_info(root, True)['commit'], 'khong-ro')
            valid = dict(commit='abcdef123456', built_at='2026-11-06T00:00:00+00:00', version=VERSION)
            path = root / 'PHIEN_BAN.json'
            path.write_text(json.dumps(valid), encoding='utf-8')
            self.assertEqual(build_info(root, True), valid)
            with patch('THIET_LAP.ASSETS', root), patch('THIET_LAP.sys.frozen', True, create=True):
                self.assertEqual(build_info(), valid)
            for bad in ('[1]', '{broken', json.dumps(dict(valid, version='0.0.0')),
                        json.dumps(dict(valid, commit='bad<script>')),
                        json.dumps(dict(valid, built_at='bad')),
                        json.dumps(dict(valid, built_at='2026-11-06T00:00:00'))):
                with self.subTest(bad=bad):
                    path.write_text(bad, encoding='utf-8')
                    self.assertEqual(build_info(root, True)['commit'], 'khong-ro')

    def test_parser_data_directory_forms(self):
        for argv in (['--data-dir', 'some folder'], ['--data-dir=some folder']):
            self.assertEqual(parse_args(argv).data_dir, 'some folder')

    def test_launcher_help_cp1252_does_not_open_error_dialog(self):
        launcher = Path(__file__).resolve().parent.parent / 'MO_BAO_CAO_CA.pyw'
        stream = io.TextIOWrapper(io.BytesIO(), encoding='cp1252', errors='strict')
        with patch('BAO_CAO_CA.show_error') as dialog, patch.object(sys, 'argv', [str(launcher), '--help']), \
                patch.object(sys, 'stdout', stream), patch.object(sys, 'stderr', stream):
            with self.assertRaises(SystemExit) as result:
                runpy.run_path(str(launcher), run_name='__main__')
            self.assertEqual(result.exception.code, 0)
            dialog.assert_not_called()
        stream.close()

    def test_launcher_uses_explicit_log_directory_and_exit_code(self):
        launcher = Path(__file__).resolve().parent.parent / 'MO_BAO_CAO_CA.pyw'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / 'chosen'
            with patch('BAO_CAO_CA.ROOT', root / 'source'), patch('BAO_CAO_CA.main', return_value=1), \
                    patch('logging.basicConfig') as configure, patch.object(sys, 'stdout'), patch.object(sys, 'stderr'), \
                    patch.object(sys, 'argv', [str(launcher), '--no-browser', '--data-dir=' + str(data)]):
                with self.assertRaises(SystemExit) as result:
                    runpy.run_path(str(launcher), run_name='__main__')
                self.assertEqual(result.exception.code, 1)
            self.assertTrue((data / 'NHAT_KY_CHAY.log').is_file())
            self.assertEqual(configure.call_args.kwargs['filename'], str(data / 'LOI_CHUONG_TRINH.log'))
            self.assertFalse((root / 'source').exists())

    def test_dirty_git_rejected_before_any_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            # Repo sạch nhưng chưa có HEAD cũng phải bị chặn, không tạo commit để thử.
            with self.assertRaises(RuntimeError):
                DONG_GOI.clean_commit(root)
            (root / 'dirty.txt').write_text('dirty', encoding='utf-8')
            for staged in (False, True):
                if staged:
                    subprocess.run(['git', '-C', str(root), 'add', 'dirty.txt'], check=True)
                with self.subTest(staged=staged), patch.object(DONG_GOI, 'metadata') as metadata:
                    with self.assertRaisesRegex(RuntimeError, 'chua commit'):
                        DONG_GOI.package(root)
                    metadata.assert_not_called()
                self.assertFalse((root / 'dist').exists())
            self.assertEqual(DONG_GOI.main(['--root', str(root), '--check']), 1)

    def test_git_errors_fail_closed(self):
        with patch.object(DONG_GOI.subprocess, 'run', side_effect=FileNotFoundError()):
            with self.assertRaises(RuntimeError):
                DONG_GOI.clean_commit(Path('.'))
        for invalid in ('', 'not-a-commit'):
            with patch.object(DONG_GOI.subprocess, 'run', side_effect=[
                    subprocess.CompletedProcess([], 0, stdout=''),
                    subprocess.CompletedProcess([], 0, stdout=invalid)]):
                with self.assertRaises(RuntimeError):
                    DONG_GOI.clean_commit(Path('.'))

    def test_packaging_metadata_is_temporary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'ma_nguon').mkdir()
            (root / 'ma_nguon' / 'THIET_LAP.py').write_text("VERSION = 'test-version'\n", encoding='utf-8')
            seen = []

            def run(command, **kwargs):
                self.assertNotIn('pip', command)
                if 'PyInstaller' in command:
                    self.assertIn('lxml', command)
                    self.assertIn('defusedxml.ElementTree', command)
                    self.assertEqual(command.count('--copy-metadata'), 3)
                    self.assertIn('THIRD_PARTY_NOTICES.md:.', command)
                    argument = next(value for value in command if value.endswith('PHIEN_BAN.json:.'))
                    path = Path(argument[:-2])
                    value = json.loads(path.read_text(encoding='utf-8'))
                    self.assertEqual(value['commit'], 'abcdef123456')
                    self.assertEqual(value['version'], 'test-version')
                    self.assertTrue(value['built_at'])
                    self.assertNotEqual(path.parent, root)
                    seen.append(path)

            with patch.object(DONG_GOI, 'clean_commit', return_value='abcdef123456') as gate, \
                    patch.object(DONG_GOI, 'check_toolchain'), \
                    patch.object(DONG_GOI.subprocess, 'run', side_effect=run), \
                    patch.object(DONG_GOI.shutil, 'copy2'):
                DONG_GOI.package(root)
            self.assertEqual(gate.call_count, 2)
            self.assertEqual(len(seen), 1)
            self.assertFalse(seen[0].exists())
            self.assertFalse((root / 'PHIEN_BAN.json').exists())

    def test_offline_toolchain_missing_wrong_version_and_no_install(self):
        from importlib.metadata import PackageNotFoundError
        with patch.object(DONG_GOI, 'version', side_effect=PackageNotFoundError()), self.assertRaises(RuntimeError):
            DONG_GOI.check_toolchain()
        with patch.object(DONG_GOI, 'version', return_value='wrong'), self.assertRaises(RuntimeError):
            DONG_GOI.check_toolchain()
        with patch.object(DONG_GOI, 'version', side_effect=lambda name: DONG_GOI.BUILD_PINS[name]), \
                patch.object(DONG_GOI.importlib, 'import_module') as imports:
            DONG_GOI.check_toolchain()
            self.assertEqual([call.args[0] for call in imports.call_args_list],
                             ['altgraph', 'PyInstaller.building.build_main'])
        with patch.object(DONG_GOI, 'clean_commit', return_value='abcdef123456'), \
                patch.object(DONG_GOI, 'check_toolchain', side_effect=RuntimeError('missing')), \
                patch.object(DONG_GOI.subprocess, 'run') as run, self.assertRaises(RuntimeError):
            DONG_GOI.package(Path('.'))
        run.assert_not_called()

    def test_missing_graph_import_fails_before_metadata_or_build(self):
        for missing in ('altgraph', 'PyInstaller.building.build_main'):
            def graph_import(name):
                if name == missing:
                    raise ModuleNotFoundError('missing transitive dependency')
            with self.subTest(missing=missing), \
                    patch.object(DONG_GOI, 'clean_commit', return_value='abcdef123456'), \
                    patch.object(DONG_GOI, 'version', side_effect=lambda name: DONG_GOI.BUILD_PINS[name]), \
                    patch.object(DONG_GOI.importlib, 'import_module', side_effect=graph_import), \
                    patch.object(DONG_GOI, 'metadata') as metadata, \
                    patch.object(DONG_GOI.subprocess, 'run') as run, self.assertRaisesRegex(RuntimeError, 'Do thi'):
                DONG_GOI.package(Path('.'))
            metadata.assert_not_called()
            run.assert_not_called()

    def test_actual_installed_toolchain_graph_imports(self):
        # Deliberately real: exact isolated build environment is a release prerequisite.
        # Version mocks alone missed the altgraph0.17.4/setuptools84 incompatibility.
        DONG_GOI.check_toolchain()

    def test_source_launcher_smoke_and_logs(self):
        self.assertEqual(smoke()['build']['commit'], 'nguon')

    def test_exe_smoke_requires_expected_commit_before_launch(self):
        with patch('cong_cu.KIEM_THU_KHOI.subprocess.Popen') as launch:
            with self.assertRaisesRegex(RuntimeError, '--commit'):
                smoke('unused.exe')
            launch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
