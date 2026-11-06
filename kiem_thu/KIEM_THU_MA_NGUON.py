# -*- coding: utf-8 -*-
"""Kiểm tra mã nguồn chỉ bằng thư viện chuẩn: cú pháp hợp lệ, không import thừa, nguồn UTF-8."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SOURCES = sorted(list(ROOT.glob('*.pyw')) + list((ROOT / 'ma_nguon').glob('*.py')) + list((ROOT / 'kiem_thu').glob('*.py')))


def unused_imports(path):
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    tree = ast.parse(text, filename=str(path))
    imported = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported[(alias.asname or alias.name).split('.')[0]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported[alias.asname or alias.name] = node.lineno
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    exported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__all__' for t in node.targets):
            exported = {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    result = []
    for name, line in sorted(imported.items(), key=lambda item: item[1]):
        if name in used or name in exported or name == '*':
            continue
        if 'noqa: F401' in lines[line - 1]:
            continue
        result.append('%s:%d import không dùng: %s' % (path.name, line, name))
    return result


class SourceTests(unittest.TestCase):
    def test_sources_exist(self):
        self.assertGreater(len(SOURCES), 10)

    def test_every_source_parses_as_utf8(self):
        for path in SOURCES:
            with self.subTest(file=path.name):
                ast.parse(path.read_text(encoding='utf-8'), filename=str(path))

    def test_no_unused_imports(self):
        problems = [line for path in SOURCES for line in unused_imports(path)]
        self.assertEqual(problems, [], '\n' + '\n'.join(problems))

    def test_detector_catches_an_unused_import(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            sample = Path(folder) / 'mau.py'
            sample.write_text('import os\nimport sys  # noqa: F401\nimport json\nprint(json.dumps(1))\n', encoding='utf-8')
            self.assertEqual(unused_imports(sample), ['mau.py:1 import không dùng: os'])


if __name__ == '__main__':
    unittest.main()
