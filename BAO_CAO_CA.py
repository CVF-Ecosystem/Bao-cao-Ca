"""Điểm khởi động: mở phiên, kiểm tra bảo vệ dữ liệu rồi chạy máy chủ nội bộ."""
import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys
import urllib.request
import webbrowser
from THIET_LAP import VERSION, ROOT
from NGHIEP_VU import AppError
from MAY_CHU import make_server
from BAO_VE_DU_LIEU import Protection, recovery_dialog, adoption_dialog

LOG_LIMIT = 1024 * 1024
LOG_KEEP = 3


def rotate_log(path, limit=LOG_LIMIT, keep=LOG_KEEP):
    """Đổi tên nhật ký quá lớn thành .1, .2… và bỏ bản cũ nhất; không bao giờ làm hỏng việc khởi động."""
    path = Path(path)
    try:
        if not path.is_file() or path.stat().st_size <= limit:
            return
        for index in range(keep, 0, -1):
            older = path.with_name(path.name + '.' + str(index))
            newer = path if index == 1 else path.with_name(path.name + '.' + str(index - 1))
            if newer.exists():
                older.unlink(missing_ok=True)
                newer.replace(older)
    except OSError:
        pass


def running_session(directory):
    try:
        state = json.loads((Path(directory) / 'PHIEN_DANG_CHAY.json').read_text(encoding='utf-8'))
        port, token = state['port'], state['token']
        if type(port) is not int or not 1 <= port <= 65535 or not re.fullmatch(r'[A-Za-z0-9_-]{32,128}', token):
            return None
        base = 'http://127.0.0.1:' + str(port)
        req = urllib.request.Request(base + '/api/info', headers={'Cookie': f'ca_session_{port}={token}'})
        with urllib.request.urlopen(req, timeout=2) as response:
            version = json.load(response).get('version')
            if version and version != VERSION:
                raise AppError('Tool nền còn chạy bản ' + str(version) + '. Bấm Thoát tool trong tab cũ rồi mở lại bản ' + VERSION + '. Không cần xóa DB.')
            if version:
                return base + '/?launch=' + token
    except AppError:
        raise
    except Exception:
        return None


def show_error(message):
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror('Sổ báo cáo ca', message)
        root.destroy()
    except Exception:
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message, 'Sổ báo cáo ca', 16)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', default=str(ROOT / 'DU_LIEU'))
    p.add_argument('--no-browser', action='store_true')
    p.add_argument('--quiet', action='store_true')
    p.add_argument('--restore', action='store_true', help='Chọn bản sao để khôi phục trước khi mở ứng dụng')
    args = p.parse_args(argv)
    try:
        existing = running_session(args.data_dir)
        if existing:
            if args.restore:
                raise AppError('Hãy bấm Thoát tool trong ứng dụng trước khi khôi phục ngoại tuyến.')
            if not args.no_browser:
                webbrowser.open(existing)
            return 0
        if args.restore:
            if not recovery_dialog(args.data_dir):
                return 1
        try:
            Protection(args.data_dir).guard_startup()
        except Exception as e:
            if args.no_browser or not recovery_dialog(args.data_dir, str(e)):
                raise
        if Protection(args.data_dir).needs_adoption():
            if args.no_browser:
                raise AppError('DB vừa chép vào khác nguồn. Mở MO_BAO_CAO_CA.pyw để xác nhận Tiếp nhận DB đang có.')
            if not adoption_dialog(args.data_dir):
                return 1
        server = make_server(args.data_dir)
    except Exception as e:
        logging.exception('Khong mo duoc tool')
        if args.quiet:
            show_error('Không mở được tool: ' + str(e) + '\nXem LOI_CHUONG_TRINH.log trong thư mục DU_LIEU.')
        else:
            print('Khong mo duoc tool:', e)
        return 1
    url = 'http://' + server.app['host'] + '/?launch=' + server.app['token']
    session = server.app['data_dir'] / 'PHIEN_DANG_CHAY.json'
    session.write_text(json.dumps(dict(port=server.server_port, token=server.app['token'])), encoding='utf-8')
    if not args.quiet:
        print('SO BAO CAO CA', VERSION, '- DANG CHAY')
        print('Thu muc du lieu:', server.app['data_dir'])
        print('Tat chuong trinh bang nut Thoat tool tren giao dien.')
    if not args.no_browser:
        webbrowser.open(url)
    elif not args.quiet:
        print(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        session.unlink(missing_ok=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
