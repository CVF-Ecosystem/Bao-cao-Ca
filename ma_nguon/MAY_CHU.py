"""Giao tiếp nội bộ giữa giao diện và dữ liệu của máy."""
import datetime as dt
import json
from pathlib import Path
import re
import secrets
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
import logging
import shutil
import socket
import zipfile
from http.server import BaseHTTPRequestHandler
from THIET_LAP import VERSION, MAX_FILE, MAX_DB, ASSETS, VN, KEYS, build_info
from NGHIEP_VU import now, suggest, shift_label, AppError, file_type, database_error
from LUU_TRU import Store
from BAO_VE_DU_LIEU import Protection, SessionLock
from QUAN_LY_DANH_MUC import Catalogs
from BAO_CAO_EXCEL import aggregate, monthly_tables, styled_xlsx, report_table

def int_param(query, name, default, low, high):
    """Số nguyên trong query; sai kiểu hoặc ngoài khoảng thì báo lỗi rõ thay vì lỗi 500."""
    try:
        value = int(query.get(name, default))
    except (TypeError, ValueError):
        raise AppError('Tham số ' + name + ' phải là số nguyên.')
    if not low <= value <= high:
        raise AppError('Tham số ' + name + ' phải từ ' + str(low) + ' đến ' + str(high) + '.')
    return value


class Handler(BaseHTTPRequestHandler):
    server_version = 'BaoCaoCa/' + VERSION

    def log_message(self, *_):
        pass

    @property
    def app(self):
        return self.server.app

    def authorize(self):
        if self.headers.get('Host') != self.app['host']:
            raise AppError('Địa chỉ truy cập không hợp lệ.', 403)
        cookie = self.headers.get('Cookie', '')
        if f"ca_session_{self.server.server_port}={self.app['token']}" not in cookie.split('; '):
            raise AppError('Phiên làm việc hết hạn. Mở lại tool.', 403)

    def send_data(self, data, mime='application/json; charset=utf-8', name=None, status=200, cookie=False):
        if not isinstance(data, bytes):
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; object-src 'none'; base-uri 'none'")
        if cookie:
            self.send_header('Set-Cookie', f"ca_session_{self.server.server_port}={self.app['token']}; HttpOnly; SameSite=Strict; Path=/")
        if name:
            fallback = re.sub(r'[^A-Za-z0-9._-]', '_', name)
            self.send_header('Content-Disposition', 'attachment; filename="' + fallback + '"; filename*=UTF-8\'\'' + urllib.parse.quote(name, safe=''))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path, name):
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename="' + name + '"')
        self.send_header('Content-Length', str(path.stat().st_size))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        with path.open('rb') as stream:
            shutil.copyfileobj(stream, self.wfile, 1024 * 1024)

    def request_length(self):
        value = self.headers.get('Content-Length', '0')
        if not value.isascii() or not value.isdigit():
            raise AppError('Content-Length không hợp lệ.')
        try:
            return int(value)
        except ValueError:
            raise AppError('Content-Length không hợp lệ.')

    def drain_body(self, length):
        # Không chờ vô hạn hoặc đọc quá 4 MiB từ client gửi chậm.
        previous = self.connection.gettimeout()
        self.connection.settimeout(0.5)
        try:
            remaining = min(length, 4 * 1024 * 1024)
            deadline = time.monotonic() + 0.5
            while remaining and time.monotonic() < deadline:
                self.connection.settimeout(max(0.001, deadline - time.monotonic()))
                chunk = self.rfile.read1(min(remaining, 65536))
                if not chunk:
                    break
                remaining -= len(chunk)
        except (OSError, ValueError):
            pass
        finally:
            self.connection.settimeout(previous)

    def reject_unread(self, data, status):
        try:
            length = self.request_length()
        except AppError:
            length = None
        if length is not None and length <= 4 * 1024 * 1024:
            self.drain_body(length)
            self.send_data(data, status=status)
        else:
            self.send_data(data, status=status)
            self.wfile.flush()
            try:
                self.connection.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            self.drain_body(length if length is not None else 4 * 1024 * 1024)

    def unsupported_method(self):
        # Giữ phản hồi 501 mặc định, nhưng không bỏ lại thân nhỏ chưa đọc.
        try:
            length = self.request_length()
        except AppError:
            self.reject_unread({'error': 'Content-Length không hợp lệ.'}, 400)
            return
        if length <= 4 * 1024 * 1024:
            self.drain_body(length)
            self.send_error(501, "Unsupported method (%r)" % self.command)
        else:
            self.send_error(501, "Unsupported method (%r)" % self.command)
            self.wfile.flush()
            try:
                self.connection.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            self.drain_body(length)

    do_PUT = unsupported_method
    do_DELETE = unsupported_method
    do_HEAD = unsupported_method

    def do_GET(self):
        try:
            length = self.request_length()
        except AppError as e:
            self.reject_unread({'error': str(e)}, e.status)
            return
        try:
            if length > 4 * 1024 * 1024:
                self.reject_unread({'error': 'Thân request quá lớn.'}, 400)
                return
            self.drain_body(length)
            self.get_route()
        except AppError as e:
            self.send_data({'error': str(e)}, status=e.status)
        except Exception:
            logging.exception('Loi doc du lieu')
            self.send_data({'error': 'Không đọc được dữ liệu. Hãy kiểm tra file DB và thử lại.'}, status=500)

    def get_route(self):
        u = urllib.parse.urlsplit(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        if u.path == '/' and secrets.compare_digest(q.get('launch', ''), self.app['token']):
            if self.headers.get('Host') != self.app['host']:
                raise AppError('Địa chỉ truy cập không hợp lệ.', 403)
            self.send_data((ASSETS / 'giao_dien' / 'giao_dien.html').read_bytes(), 'text/html; charset=utf-8', cookie=True)
            return
        self.authorize()
        store = self.app['store']
        assets = {'/tai_nguyen/bao_ve.js': 'application/javascript; charset=utf-8',
                  '/tai_nguyen/style.css': 'text/css; charset=utf-8',
                  '/tai_nguyen/ung_dung.js': 'application/javascript; charset=utf-8',
                  '/tai_nguyen/danh_muc.js': 'application/javascript; charset=utf-8',
                  '/tai_nguyen/phan_cong_mau.js': 'application/javascript; charset=utf-8'}
        if u.path in assets:
            self.send_data((ASSETS / 'giao_dien' / u.path.lstrip('/')).read_bytes(), assets[u.path])
        elif u.path == '/':
            self.send_data((ASSETS / 'giao_dien' / 'giao_dien.html').read_bytes(), 'text/html; charset=utf-8')
        elif u.path == '/api/info':
            catalog = self.app['catalogs']
            data = catalog.sync() if store is self.app['main_store'] else catalog.snapshot(store)
            self.send_data(dict(suggestion=suggest(), jobs=data['jobs'], roles=data['roles'], version=VERSION, build=build_info(),
                                people=data['people'], teams=data['teams'], staff_templates=data['staff_templates'], ships=store.ships(), catalog_warning=catalog.warning if store is self.app['main_store'] else '',
                                readonly=store.readonly, database=store.path.name, now=now(),
                                context=self.app['context'],
                                review=store.path != self.app['main_store'].path,
                                reviewer=store.meta('reviewer_name') if store.path != self.app['main_store'].path else '',
                                backup_warning=self.app.get('backup_warning', ''),
                                backup_level=self.app.get('backup_level', '')))
        elif u.path == '/api/protection':
            self.send_data(self.app['protection'].status())
        elif u.path == '/api/catalogs':
            if store is not self.app['main_store']:
                raise AppError('Về DB chính để sửa danh mục; báo cáo trong bản kiểm tra giữ nguyên danh mục nguồn.')
            self.send_data(self.app['catalogs'].editor_data())
        elif u.path == '/api/reports':
            self.send_data(store.list(q))
        elif u.path == '/api/reports-page':
            self.send_data(store.page(q, int_param(q, 'limit', 50, 1, 200), int_param(q, 'offset', 0, 0, 10_000_000)))
        elif u.path == '/api/overview':
            self.send_data(store.overview(suggest(), now()[:7]))
        elif u.path == '/api/report':
            self.send_data(store.get(q.get('id', '')))
        elif u.path == '/api/history':
            self.send_data(store.history(q.get('id', '')))
        elif u.path == '/api/attachment':
            if q.get('context') != self.app['context']:
                raise AppError('DB đã đổi. Mở lại báo cáo để xem tệp.', 409)
            a = store.attachment(q.get('hash', ''))
            mime, ext = file_type(a['data'])
            name = q.get('name', 'dinh_kem' + ext)
            previewable = mime in ('image/png', 'image/jpeg', 'image/webp')
            self.send_data(a['data'], mime, name if q.get('download') == '1' or not previewable else None)
        elif u.path == '/api/attachments-zip':
            if q.get('context') != self.app['context']:
                raise AppError('DB đã đổi. Mở lại báo cáo.', 409)
            r = store.get(q.get('id', ''))
            output = self.app['data_dir'] / 'XUAT_DINH_KEM' / (secrets.token_hex(12) + '.zip')
            output.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
                notes = [r['date'] + ' - ' + shift_label(r['shift'])]
                for i, a in enumerate(r.get('attachments', []), 1):
                    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', a['name'])[:160]
                    fname = f'{i:02d}_' + safe
                    z.writestr(fname, store.attachment(a['hash'])['data'])
                    notes.append(fname + '\n' + a.get('caption', ''))
                z.writestr('GHI_CHU_DINH_KEM.txt', '\n\n'.join(notes).encode('utf-8'))
            try:
                self.send_file(output, 'DINH_KEM_' + r['id'] + '.zip')
            finally:
                output.unlink(missing_ok=True)
        elif u.path == '/api/export-month':
            if q.get('context') != self.app['context']:
                raise AppError('DB đã đổi. Mở lại chức năng xuất tháng.', 409)
            tables = monthly_tables(store, q.get('month', ''))
            reports = {f"{int(r['date'][8:10]):02d}-{int(r['date'][5:7]):02d}_" + ('Ngay' if r['shift']=='DAY' else 'Dem'):r for r in store.list({'from':q['month']+'-01','to':q['month']+'-31'})}
            self.send_data(styled_xlsx(tables, reports), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           'BAO_CAO_THANG_' + q['month'] + '.xlsx')
        elif u.path == '/api/export':
            if q.get('context') != self.app['context']:
                raise AppError('DB đã đổi. Mở lại báo cáo hoặc tổng hợp trước khi xuất Excel.', 409)
            reports = {}
            if q.get('id'):
                report = store.get(q['id'])
                tables = [('Bao cao ca', report_table(report))]
                reports = {'Bao cao ca':report}
            else:
                rows = store.list(q)
                tables = [('Tong hop', [['TỔNG HỢP LƯỢT CÔNG VIỆC', q.get('from', '') + ' đến ' + q.get('to', '')],
                    ['Trạng thái lọc', q.get('status') or 'Tất cả (gồm cả nháp)'], ['Số ca', len(rows)], [],
                    ['Công việc', 'F20', 'F40', 'E20', 'E40'],
                    *[[j['name'], *[j[k] for k in KEYS]] for j in aggregate(rows)],
                    [], ['Lưu ý', 'Lượt công việc, không phải số container duy nhất.']]),
                    ('Chi tiet', [['Ngày', 'Ca', 'Trạng thái', 'Công việc', 'Chi tiết', 'XN', 'RTG', 'F20', 'F40', 'E20', 'E40'],
                    *[[r['date'], shift_label(r['shift']), r['status'], j['name'], j['detail'], 'X' if j['xn'] else '', 'X' if j['rtg'] else '', *[j[k] for k in KEYS]] for r in rows for j in r['jobs']]])]
            self.send_data(styled_xlsx(tables, reports), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'BAO_CAO_CA.xlsx')
        else:
            raise AppError('Không tìm thấy chức năng.', 404)

    def do_POST(self):
        unread = True
        try:
            self.authorize()
            if self.headers.get('X-Ca-Request') != '1':
                raise AppError('Yêu cầu không hợp lệ.', 403)
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.app['host']:
                raise AppError('Nguồn yêu cầu không hợp lệ.', 403)
            length = self.request_length()
            route = urllib.parse.urlsplit(self.path)
            query = dict(urllib.parse.parse_qsl(route.query))
            is_db = route.path in ('/api/open-viewer', '/api/corrections-preview')
            limit = MAX_DB if is_db else MAX_FILE if route.path == '/api/attachment-upload' else 4 * 1024 * 1024
            if not 0 <= length <= limit:
                raise AppError('DB tối đa 8 GB; mỗi ảnh/PDF tối đa 100 MB.')
            unread = False
            uploaded = None
            if is_db:
                uploaded = self.app['data_dir'] / 'DB_KIEM_TRA' / ('ban_sao_' + secrets.token_hex(8) + '.db')
                uploaded.parent.mkdir(parents=True, exist_ok=True)
                remaining = length
                with uploaded.open('wb') as f:
                    while remaining:
                        chunk = self.rfile.read(min(remaining, 1024 * 1024))
                        if not chunk:
                            raise AppError('Chưa nhận đủ file DB.')
                        f.write(chunk)
                        remaining -= len(chunk)
                with uploaded.open('rb') as f:
                    if not f.read(16).startswith(b'SQLite format 3\x00'):
                        uploaded.unlink(missing_ok=True)
                        raise AppError('Chọn file DB SQLite do tool xuất ra.')
                raw = b''
            else:
                raw = self.rfile.read(length)
            if self.path in ('/api/protection-directory', '/api/protection-config', '/api/protection-backup', '/api/restore-preview', '/api/restore'):
                p = json.loads(raw)
                if p.get('context') != self.app['context'] or self.app['store'] is not self.app['main_store']:
                    raise AppError('Về DB chính và tải lại trước khi thao tác bảo vệ dữ liệu.', 409)
                protection = self.app['protection']
                if self.path == '/api/protection-directory':
                    from BAO_VE_DU_LIEU import choose_directory
                    self.send_data(dict(directory=choose_directory()))
                elif self.path == '/api/protection-config':
                    protection.set_external(p.get('directory'))
                    daily_backup(self.app)
                    self.send_data(protection.status())
                elif self.path == '/api/protection-backup':
                    daily_backup(self.app)
                    self.send_data(protection.status())
                elif self.path == '/api/restore-preview':
                    self.send_data(protection.preview(protection.selected(p.get('id'))))
                else:
                    if p.get('confirmation') != 'KHOI PHUC':
                        raise AppError('Cần nhập KHOI PHUC để xác nhận thay dữ liệu hiện tại.')
                    result = protection.restore(protection.selected(p.get('id')), p.get('sha256', ''))
                    store = Store(protection.db)
                    self.app['store'] = self.app['main_store'] = store
                    self.app['context'] = secrets.token_hex(16)
                    self.app['catalogs'] = Catalogs(self.app['data_dir'].parent / 'DANH_MUC', store)
                    daily_backup(self.app)
                    self.send_data(result)
            elif self.path == '/api/catalogs-save':
                p = json.loads(raw)
                if p.get('context') != self.app['context'] or self.app['store'] is not self.app['main_store']:
                    raise AppError('DB đang mở đã thay đổi. Về DB chính trước khi sửa danh mục.', 409)
                data = self.app['catalogs'].save(p.get('text'), p.get('digest'))
                daily_backup(self.app, force=False)
                self.send_data(data)
            elif route.path == '/api/attachment-upload':
                if query.get('context') != self.app['context']:
                    raise AppError('DB đã đổi. Mở lại báo cáo trước khi thêm tệp.', 409)
                if query.get('id'):
                    a = self.app['store'].add_attachment(query['id'], int(query.get('version', '-1')), raw,
                         query.get('name', ''), query.get('actor', ''), query.get('caption', ''))
                    daily_backup(self.app, force=False)
                else:
                    a = self.app['store'].upload_attachment(raw, query.get('name', ''), query.get('actor', ''))
                self.send_data(a)
            elif self.path == '/api/ships-add':
                p = json.loads(raw)
                if p.get('context') != self.app['context']:
                    raise AppError('DB đã đổi. Mở lại danh sách tàu.', 409)
                ships = self.app['store'].add_ship(p.get('name', ''))
                daily_backup(self.app, force=False)
                self.send_data({'ships': ships})
            elif self.path == '/api/shutdown':
                if self.app.get('backup_pending'):
                    daily_backup(self.app)
                self.send_data({'ok': True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            elif self.path == '/api/open-viewer':
                path = uploaded
                try:
                    newstore = Store(path, readonly=True)
                except Exception:
                    path.unlink(missing_ok=True)
                    raise
                self.app['store'] = newstore
                self.app['context'] = secrets.token_hex(16)
                self.send_data({'ok': True})
            elif self.path == '/api/main-db':
                self.app['store'] = self.app['main_store']
                self.app['context'] = secrets.token_hex(16)
                self.send_data({'ok': True})
            elif self.path == '/api/enable-corrections':
                p = json.loads(raw)
                if p.get('context') != self.app['context']:
                    raise AppError('DB vừa thay đổi. Tải lại trước khi bật bổ sung.', 409)
                if self.app['store'].path.parent != (self.app['data_dir'] / 'DB_KIEM_TRA').resolve():
                    raise AppError('Chức năng này chỉ dùng trên bản sao DB kiểm tra.')
                self.app['store'] = self.app['store'].enable_corrections(p.get('reviewer', ''))
                self.app['context'] = secrets.token_hex(16)
                self.send_data({'ok': True})
            elif self.path == '/api/corrections-preview':
                if self.app['store'] is not self.app['main_store']:
                    raise AppError('Về DB chính của máy trước khi nhập bản bổ sung.')
                path = uploaded
                source = Store(path, True)
                plan = self.app['main_store'].correction_plan(source)
                nonce = secrets.token_hex(16)
                self.app['pending_import'] = dict(source=source, nonce=nonce, context=self.app['context'])
                self.send_data(dict(nonce=nonce, items=[{k:v for k,v in r.items() if k!='base_payload'} for r in plan]))
            elif self.path == '/api/corrections-apply':
                p = json.loads(raw)
                pending = self.app.get('pending_import')
                if (not pending or p.get('nonce') != pending['nonce'] or
                    pending['context'] != self.app['context'] or self.app['store'] is not self.app['main_store']):
                    raise AppError('Phiên đối chiếu đã thay đổi. Mở lại file bổ sung.', 409)
                stamp = dt.datetime.now(VN).strftime('%Y%m%d_%H%M%S')
                self.app['main_store'].backup(self.app['data_dir'] / 'TRUOC_KHI_NHAP_BO_SUNG' / (stamp+'_'+secrets.token_hex(3)+'.db'))
                count = self.app['main_store'].apply_corrections(pending['source'], p.get('selected'))
                self.app.pop('pending_import', None)
                daily_backup(self.app)
                self.send_data(dict(ok=True, count=count))
            elif self.path == '/api/save':
                p = json.loads(raw)
                if p.get('context') != self.app['context']:
                    raise AppError('DB đang mở đã thay đổi ở cửa sổ khác. Hãy tải lại tool trước khi nhập tiếp.', 409)
                r = self.app['store'].save(p['report'], p.get('version'), p.get('reason', ''))
                daily_backup(self.app, force=r['status'] == 'closed')
                self.send_data(r)
            elif self.path == '/api/backup':
                p = json.loads(raw)
                if p.get('context') != self.app['context']:
                    raise AppError('DB đã đổi. Tải lại màn hình trước khi sao lưu mang đi.', 409)
                stamp = dt.datetime.now(VN).strftime('%Y%m%d_%H%M%S')
                prefix = 'DB_BO_SUNG_' if self.app['store'].meta('review_copy') == '1' else 'BAO_CAO_CA_'
                name = prefix + stamp + '_' + secrets.token_hex(2) + '.db'
                path = self.app['data_dir'] / 'SAO_LUU_MANG_DI' / name
                self.app['store'].backup(path)
                self.send_file(path, name)
            else:
                raise AppError('Không tìm thấy chức năng.', 404)
        except AppError as e:
            if unread:
                self.reject_unread({'error': str(e)}, e.status)
            else:
                self.send_data({'error': str(e)}, status=e.status)
        except (sqlite3.Error, OSError) as e:
            logging.exception('Loi tai tep / ghi DB: %s', urllib.parse.urlsplit(self.path).path)
            self.send_data({'error': database_error(e)}, status=503 if 'locked' in str(e).lower() else 500)
        except (ValueError, KeyError, TypeError, AttributeError):
            self.send_data({'error': 'Dữ liệu gửi lên không hợp lệ.'}, status=400)
        except Exception:
            logging.exception('Loi ghi du lieu')
            self.send_data({'error': 'Lỗi chương trình khi xử lý tệp/dữ liệu. Xem DU_LIEU/LOI_CHUONG_TRINH.log; chưa thể kết luận do dung lượng hoặc quyền ghi.'}, status=500)


def daily_backup(app, force=True):
    # Bản kiểm tra/bổ sung có luồng xuất riêng, không vào bộ phục hồi DB chính.
    if app['store'] is not app['main_store'] or app['store'].readonly:
        return
    if not force and time.monotonic() - app.get('backup_tick', -1e20) < 300:
        app['backup_pending'] = True  # bù khi có thao tác chốt/sao lưu kế tiếp hoặc khi thoát tool
        return
    protection = app.get('protection')
    if protection is None:
        protection = app['protection'] = Protection(app['data_dir'])
        protection.initialize()
    try:
        result = protection.backup()
        if result is None:
            app['backup_pending'] = True
        else:
            app['backup_tick'] = time.monotonic()
            app['backup_pending'] = False
        app['backup_warning'] = protection.warning
        level = getattr(protection, 'warning_level', '')
        app['backup_level'] = level if isinstance(level, str) else ''
    except Exception:
        logging.exception('Sao luu tu dong that bai')
        app['backup_level'] = protection.warning_level = 'error'
        protection.warning = app['backup_warning'] = 'Sao lưu tự động thất bại. Dữ liệu vừa lưu vẫn ở DB chính; kiểm tra dung lượng/quyền ghi và bấm Sao lưu ngay.'


def make_server(directory, port=0, startup_check=None):
    directory = Path(directory).resolve()
    protection = Protection(directory)
    if protection._checked_info(startup_check) is None:
        protection.guard_startup()
    lock = SessionLock(directory)
    server = None
    try:
        store = Store(directory / 'BAO_CAO_CA.db')
        protection.initialize(store)
        if store.meta('review_copy') == '1':
            raise AppError('Đây là DB bổ sung, không phải DB chính. Dùng Nhập bổ sung từ DB.')
        from http.server import HTTPServer
        class ProtectedServer(HTTPServer):
            def server_close(self):
                try:
                    super().server_close()
                finally:
                    lock.close()
        server = ProtectedServer(('127.0.0.1', port), Handler)
        server.app = dict(store=store, main_store=store, protection=protection, data_dir=directory,
                         context=secrets.token_hex(16), token=secrets.token_urlsafe(32),
                         host='127.0.0.1:' + str(server.server_port))
        server.app['catalogs'] = Catalogs(directory.parent / 'DANH_MUC', store)
        server.app['catalogs'].sync()
        daily_backup(server.app)
        return server
    except Exception:
        if server is not None:
            server.server_close()
        lock.close()
        raise
