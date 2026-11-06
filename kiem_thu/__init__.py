import sys
from pathlib import Path

# Các module chương trình nằm trong ma_nguon/ và được import theo tên phẳng.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'ma_nguon'))
