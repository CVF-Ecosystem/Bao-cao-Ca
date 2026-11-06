"""Thông số ứng dụng; danh mục mặc định đọc từ tệp ngoài."""
import sys
import datetime as dt
from pathlib import Path

VERSION = '1.9.0'
MAX_FILE = 100 * 1024 * 1024
MAX_DB = 8 * 1024 * 1024 * 1024
ROOT = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
ASSETS = Path(getattr(sys, '_MEIPASS', ROOT))
VN = dt.timezone(dt.timedelta(hours=7))
KEYS = ['f20', 'f40', 'e20', 'e40']

def _default(filename):
    path = ASSETS / 'mau' / 'DANH_MUC_MAU' / filename
    return [s.strip() for s in path.read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.lstrip().startswith('#')]

PEOPLE = _default('NHAN_VIEN.txt')
ROLES = _default('VI_TRI.txt')
JOBS = _default('CONG_VIEC.txt')
SHIPS = _default('TAU_MAU.txt')
