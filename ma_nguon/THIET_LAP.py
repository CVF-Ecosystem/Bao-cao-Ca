"""Thông số ứng dụng; danh mục mặc định đọc từ tệp ngoài."""
import sys
import datetime as dt
import json
import re
from pathlib import Path

VERSION = '1.9.2'
MAX_FILE = 100 * 1024 * 1024
MAX_DB = 8 * 1024 * 1024 * 1024
ROOT = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
ASSETS = Path(getattr(sys, '_MEIPASS', ROOT))
VN = dt.timezone(dt.timedelta(hours=7))
KEYS = ['f20', 'f40', 'e20', 'e40']


def build_info(assets=None, frozen=None):
    """Thông tin đóng gói; không nhận metadata sai phiên bản hoặc sai định dạng."""
    frozen = getattr(sys, 'frozen', False) if frozen is None else frozen
    fallback = dict(commit='khong-ro' if frozen else 'nguon', built_at='', version=VERSION)
    try:
        data = json.loads((Path(assets) if assets is not None else ASSETS).joinpath('PHIEN_BAN.json').read_text(encoding='utf-8'))
        if (not isinstance(data, dict) or data.get('version') != VERSION
                or not isinstance(data.get('commit'), str)
                or not re.fullmatch(r'[0-9a-f]{7,40}', data['commit'])
                or not isinstance(data.get('built_at'), str)):
            return fallback
        stamp = dt.datetime.fromisoformat(data['built_at'].replace('Z', '+00:00'))
        if stamp.utcoffset() != dt.timedelta(0):
            return fallback
        return {key: data[key] for key in ('commit', 'built_at', 'version')}
    except (OSError, ValueError, TypeError):
        return fallback

def _default(filename):
    path = ASSETS / 'mau' / 'DANH_MUC_MAU' / filename
    return [s.strip() for s in path.read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.lstrip().startswith('#')]

PEOPLE = _default('NHAN_VIEN.txt')
ROLES = _default('VI_TRI.txt')
JOBS = _default('CONG_VIEC.txt')
SHIPS = _default('TAU_MAU.txt')
