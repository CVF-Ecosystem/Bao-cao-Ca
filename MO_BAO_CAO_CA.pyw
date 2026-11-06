# -*- coding: utf-8 -*-
"""Bấm đúp để mở giao diện, không hiện cửa sổ CMD trên Windows."""
import logging
import sys
from pathlib import Path

if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'ma_nguon'))
import BAO_CAO_CA as app  # noqa: E402

if __name__ == '__main__':
    try:
        logs = app.ROOT / 'DU_LIEU'
        logs.mkdir(parents=True, exist_ok=True)
        app.rotate_log(logs / 'LOI_CHUONG_TRINH.log')
        app.rotate_log(logs / 'NHAT_KY_CHAY.log')
        logging.basicConfig(filename=str(logs / 'LOI_CHUONG_TRINH.log'), level=logging.ERROR,
                            format='%(asctime)s %(levelname)s %(message)s', encoding='utf-8')
        # pythonw / windowed executables have no standard console streams.
        with (logs / 'NHAT_KY_CHAY.log').open('a', encoding='utf-8') as stream:
            sys.stdout = sys.stderr = stream
            app.main(['--quiet'] + sys.argv[1:])
    except Exception as e:
        logging.exception('Loi khoi dong')
        app.show_error('Không mở được Sổ báo cáo ca: ' + str(e))
