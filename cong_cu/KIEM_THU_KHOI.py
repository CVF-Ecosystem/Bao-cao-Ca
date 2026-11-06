"""Kiểm thử launcher trong thư mục tạm; không chạy EXE nếu không được chỉ định."""
import argparse
import http.cookiejar
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'ma_nguon'))
from THIET_LAP import VERSION  # noqa: E402


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def smoke(executable=None, timeout=30, expected_version=VERSION, expected_commit=None):
    require(not executable or bool(expected_commit), 'Smoke EXE can --commit ma Git du kien.')
    with tempfile.TemporaryDirectory(prefix='bao_cao_smoke_') as temporary:
        root = Path(temporary)
        directory = root / 'DU_LIEU'
        command = ([str(Path(executable).resolve())] if executable else
                   [sys.executable, str(ROOT / 'MO_BAO_CAO_CA.pyw')])
        command += ['--no-browser', '--data-dir', str(directory)]
        process = subprocess.Popen(command, cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        base = None

        def shutdown():
            if base:
                request = urllib.request.Request(base + '/api/shutdown', data=b'{}',
                                                 headers={'X-Ca-Request': '1', 'Content-Type': 'application/json'})
                with client.open(request, timeout=3) as response:
                    require(json.load(response).get('ok') is True, 'Shutdown khong tra ok.')

        try:
            deadline = time.monotonic() + timeout
            session = directory / 'PHIEN_DANG_CHAY.json'
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('Launcher thoat truoc khi may chu san sang: ' + str(process.returncode))
                try:
                    state = json.loads(session.read_text(encoding='utf-8'))
                    base = 'http://127.0.0.1:' + str(state['port'])
                    with client.open(base + '/?launch=' + state['token'], timeout=2) as response:
                        response.read()
                    break
                except (OSError, ValueError, KeyError):
                    time.sleep(0.05)
            else:
                raise RuntimeError('Het thoi gian cho launcher.')
            with client.open(base + '/api/info', timeout=5) as response:
                info = json.load(response)
            require(info.get('version') == expected_version, 'Sai version: ' + repr(info))
            build = info['build']
            require(isinstance(build, dict) and set(build) == {'commit', 'built_at', 'version'}
                    and build['version'] == expected_version, 'Sai metadata: ' + repr(build))
            if executable:
                require(build['commit'] == expected_commit and bool(build['built_at']), 'Sai build EXE: ' + repr(build))
            else:
                require(build == dict(commit='nguon', built_at='', version=expected_version), 'Sai build nguon: ' + repr(build))
            require((directory / 'NHAT_KY_CHAY.log').is_file(), 'Thieu nhat ky trong data-dir tam.')
            require((directory / 'LOI_CHUONG_TRINH.log').is_file(), 'Thieu log loi trong data-dir tam.')
            shutdown()
            require(process.wait(timeout=10) == 0, 'Launcher tra exit code loi.')
            require(not session.exists(), 'Phien chua duoc don sau shutdown')
            return info
        finally:
            if process.poll() is None:
                try:
                    shutdown()
                    process.wait(timeout=3)
                except Exception:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=3)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--exe', type=Path)
    parser.add_argument('--version', default=VERSION)
    parser.add_argument('--commit', help='Ma Git ngan du kien, bat buoc khi smoke EXE moi da build')
    args = parser.parse_args(argv)
    if args.exe and not args.commit:
        parser.error('--exe can --commit de doi chieu dung ban build')
    info = smoke(args.exe, expected_version=args.version, expected_commit=args.commit)
    print('OK launcher: version=' + info['version'] + ', build=' + info['build']['commit'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
