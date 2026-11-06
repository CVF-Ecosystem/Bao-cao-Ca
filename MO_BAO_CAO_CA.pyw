# -*- coding: utf-8 -*-
"""Bấm đúp để mở giao diện, không hiện cửa sổ CMD trên Windows."""
import logging
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'ma_nguon'))
import BAO_CAO_CA as app  # noqa: E402

if __name__ == '__main__':
    try:
        logs = Path(app.parse_args(sys.argv[1:]).data_dir).resolve()
        logs.mkdir(parents=True, exist_ok=True)
        app.rotate_log(logs / 'LOI_CHUONG_TRINH.log')
        app.rotate_log(logs / 'NHAT_KY_CHAY.log')
        logging.basicConfig(filename=str(logs / 'LOI_CHUONG_TRINH.log'), level=logging.ERROR,
                            format='%(asctime)s %(levelname)s %(message)s', encoding='utf-8')
        # pythonw / windowed executables have no standard console streams.
        with (logs / 'NHAT_KY_CHAY.log').open('a', encoding='utf-8') as stream, redirect_stdout(stream), redirect_stderr(stream):
            result = app.main(['--quiet'] + sys.argv[1:])
        sys.exit(result)
    except Exception as e:
        logging.exception('Loi khoi dong')
        if '--no-browser' in sys.argv[1:]:
            if sys.stderr is not None:
                print('Khong mo duoc So bao cao ca: ' + str(e), file=sys.stderr)
        else:
            app.show_error('Không mở được Sổ báo cáo ca: ' + str(e))
        sys.exit(1)
