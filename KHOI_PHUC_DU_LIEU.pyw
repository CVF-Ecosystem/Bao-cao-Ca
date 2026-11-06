"""Chỉ mở khôi phục khi đã thoát phiên đang chạy."""
import sys
from pathlib import Path

if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'ma_nguon'))
from BAO_CAO_CA import main  # noqa: E402
if __name__ == '__main__':
    main(['--restore', '--quiet'])
