"""Chặn cây Git bẩn, tạo metadata tạm rồi gọi PyInstaller."""
import argparse
import ast
import datetime as dt
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from importlib.metadata import PackageNotFoundError, version

BUILD_PINS = {'pyinstaller': '6.14.2', 'altgraph': '0.17.4', 'packaging': '24.2',
              'pefile': '2023.2.7', 'pyinstaller-hooks-contrib': '2025.5',
              'pywin32-ctypes': '0.2.3', 'setuptools': '84.1.0',
              'openpyxl': '3.1.5', 'defusedxml': '0.7.1', 'et_xmlfile': '2.0.0'}


def check_toolchain():
    """No installation/network side effect: provisioning is a separate explicit step."""
    if sys.version_info < (3, 10) or sys.platform != 'win32':
        raise RuntimeError('Dong goi Windows can Python >=3.10; ung dung van nham Python3.9+.')
    try:
        for name, expected in BUILD_PINS.items():
            if version(name) != expected:
                raise RuntimeError('Sai phien ban ' + name + '; dung requirements-build.txt trong moi truong rieng.')
    except PackageNotFoundError as error:
        raise RuntimeError('Thieu thu vien dong goi; dung requirements-build.txt trong moi truong rieng.') from error


def clean_commit(root):
    try:
        status = subprocess.run(['git', '-C', str(root), 'status', '--porcelain=v1', '--untracked-files=all'],
                                capture_output=True, text=True, check=True)
        if status.stdout.strip():
            raise RuntimeError('Cay Git con thay doi chua commit; tu choi build.')
        commit = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '--short=12', 'HEAD'],
                                capture_output=True, text=True, check=True).stdout.strip()
        if not re.fullmatch(r'[0-9a-f]{12,40}', commit):
            raise RuntimeError('Ma Git HEAD khong hop le; tu choi build.')
        return commit
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError('Khong xac minh duoc Git/HEAD; tu choi build.') from error


def metadata(root, commit):
    tree = ast.parse((root / 'ma_nguon' / 'THIET_LAP.py').read_text(encoding='utf-8-sig'))
    version = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'VERSION' for target in node.targets))
    return dict(commit=commit, built_at=dt.datetime.now(dt.timezone.utc).isoformat(), version=version)


def package(root):
    clean_commit(root)  # Không cài công cụ hoặc tạo metadata trước khi qua cổng Git.
    check_toolchain()
    commit = clean_commit(root)
    with tempfile.TemporaryDirectory(prefix='bao_cao_build_') as temporary:
        path = Path(temporary) / 'PHIEN_BAN.json'
        path.write_text(json.dumps(metadata(root, commit), ensure_ascii=False), encoding='utf-8')
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onefile', '--windowed',
                        '--name', 'SO_BAO_CAO_CA', '--paths', 'ma_nguon', '--add-data', 'giao_dien:giao_dien',
                        '--add-data', 'mau:mau', '--add-data', 'THIRD_PARTY_NOTICES.md:.',
                        '--copy-metadata', 'openpyxl', '--copy-metadata', 'defusedxml',
                        '--copy-metadata', 'et_xmlfile', '--hidden-import', 'defusedxml.ElementTree',
                        '--exclude-module', 'lxml', '--add-data', str(path) + ':.', 'MO_BAO_CAO_CA.pyw'],
                       cwd=root, check=True)
    shutil.copy2(root / 'dist' / 'SO_BAO_CAO_CA.exe', root / 'SO_BAO_CAO_CA.exe')


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Chỉ kiểm tra cổng Git, không build')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args(argv)
    try:
        if args.check:
            clean_commit(args.root)
        else:
            package(args.root)
        return 0
    except (RuntimeError, OSError, ValueError, StopIteration, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
