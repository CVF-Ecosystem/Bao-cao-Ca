"""Giao tiếp nội bộ giữa giao diện và dữ liệu của máy."""
import datetime as dt
import base64
import binascii
import hashlib
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
from NGHIEP_VU import now, suggest, shift_label, AppError, file_type, database_error, ClosingConnection
from LUU_TRU import Store
from BAO_VE_DU_LIEU import Protection, SessionLock, _database_stamp
from QUAN_LY_DANH_MUC import Catalogs, PersonnelSaveError
from NANG_CAP_CSDL import plan_upgrade, upgrade
from BAO_TRI_CSDL import preview as maintenance_preview, confirm as maintenance_confirm, register_viewer, MaintenanceError
from BAO_CAO_EXCEL import aggregate, monthly_tables, styled_xlsx, report_table

def clear_pending_context(app):
    for key in ('pending_personnel','pending_maintenance','pending_upgrade','pending_recovery','pending_import'):
        app.pop(key,None)


def local_json(raw, headers):
    if headers.get_content_type() != 'application/json':
        raise AppError('Cần dữ liệu JSON.')
    def unique(pairs):
        value={}
        for key,item in pairs:
            if key in value: raise ValueError('duplicate')
            value[key]=item
        return value
    value=json.loads(raw,object_pairs_hook=unique)
    if not isinstance(value,dict): raise AppError('Dữ liệu không hợp lệ.')
    return value


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
                  '/tai_nguyen/phan_cong_mau.js': 'application/javascript; charset=utf-8',
                  '/tai_nguyen/local_ui.js': 'application/javascript; charset=utf-8'}
        if u.path in assets:
            self.send_data((ASSETS / 'giao_dien' / u.path.lstrip('/')).read_bytes(), assets[u.path])
        elif u.path == '/':
            self.send_data((ASSETS / 'giao_dien' / 'giao_dien.html').read_bytes(), 'text/html; charset=utf-8')
        elif u.path == '/api/info':
            if self.app.get('migration_required'):
                self.send_data(dict(version=VERSION, context=self.app['context'], migrationRequired=True,
                    schemaVersion=store.meta('schema_version'), capabilities=dict(migration=True,saveKinds=False,
                    revisionDiff=False,hideShips=False,backupLevels=False,maintenance=False),lastFull=None))
                return
            catalog = self.app['catalogs']
            pin = self.app['protection'].config.get('last_full_local') if store is self.app['main_store'] and self.app['protection']._pin_name('last_full_local') else None
            data = catalog.sync() if store is self.app['main_store'] else catalog.snapshot(store)
            self.send_data(dict(migrationRequired=False, schemaVersion=store.meta('schema_version'), capabilities=dict(migration=False, saveKinds=True, revisionDiff=True, hideShips=store is self.app['main_store'] and not store.readonly, backupLevels=True, maintenance=store is self.app['main_store'] and not store.readonly), lastFull=({'at':pin['at'],'databaseId':pin['database_id'],'location':'local'} if pin and isinstance(pin.get('at'),str) else None), suggestion=suggest(), jobs=data['jobs'], roles=data['roles'], version=VERSION, build=build_info(),
                                people=data['people'], teams=data['teams'], staff_templates=data['staff_templates'], ships=store.ships(), catalog_warning=catalog.warning if store is self.app['main_store'] else '',
                                readonly=store.readonly, database=store.path.name, now=now(),
                                context=self.app['context'],
                                review=store.path != self.app['main_store'].path,
                                reviewer=store.meta('reviewer_name') if store.path != self.app['main_store'].path else '',
                                backup_warning=self.app.get('backup_warning', ''),
                                backup_level=self.app.get('backup_level', '')))
        elif self.app.get('migration_required') and u.path == '/api/protection':
            self.send_data(dict(backups=self.app['protection'].recovery_candidates(),migrationRequired=True))
        elif self.app.get('migration_required'):
            raise AppError('Cần nâng cấp DB trước khi sử dụng.', 409)
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
            if q.get('context') != self.app['context']: raise AppError('DB đã đổi.',409)
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

    def personnel_post(self):
        from PERSONNEL_XLSX import inspect_workbook, build_plan, PersonnelXlsxError
        path = urllib.parse.urlsplit(self.path).path
        names = {'/api/personnel-xlsx-inspect': {'context', 'fileBase64'},
                 '/api/personnel-xlsx-preview': {'context', 'fileBase64', 'expectedFileSha256', 'sheet', 'headerRow', 'columns', 'excludedRows'},
                 '/api/personnel-xlsx-confirm': {'context', 'nonce'},
                 '/api/personnel-xlsx-cancel': {'context'}}
        unread = True
        def fail(message, code, status=400, sheet=None, row=None, column=None, backup_id=None):
            result = dict(error=message, code=code, sheet=sheet, row=row, column=column)
            if backup_id is not None: result['backupId'] = backup_id
            if unread: self.reject_unread(result, status)
            else: self.send_data(result, status=status)
        try:
            self.authorize()
            if self.headers.get('X-Ca-Request') != '1' or (self.headers.get('Origin') and self.headers['Origin'] != 'http://' + self.app['host']):
                raise AppError('Yêu cầu không hợp lệ.', 403)
            if path == '/api/personnel-xlsx-preview':
                self.app.pop('pending_personnel', None)
            if path not in names:
                fail('Không tìm thấy chức năng.', 'INVALID_INPUT', 404); return
            length = self.request_length()
            if length > 3 * 1024 * 1024:
                fail('Yêu cầu quá lớn.', 'LIMIT_EXCEEDED', 413); return
            if self.headers.get_content_type() != 'application/json':
                fail('Cần dữ liệu JSON.', 'INVALID_INPUT'); return
            raw = self.rfile.read(length)
            unread = False
            if len(raw) != length: raise ValueError('short body')
            def unique(pairs):
                result = {}
                for key, value in pairs:
                    if key in result: raise ValueError('duplicate key')
                    result[key] = value
                return result
            p = json.loads(raw, object_pairs_hook=unique)
            if not isinstance(p, dict) or set(p) != names[path] or not isinstance(p.get('context'), str):
                raise ValueError('invalid fields')
            if path == '/api/personnel-xlsx-preview':
                self.app.pop('pending_personnel', None)
            if (p['context'] != self.app['context'] or self.app['store'] is not self.app['main_store'] or
                    self.app['store'].readonly or self.app['store'].meta('review_copy') == '1'):
                self.app.pop('pending_personnel', None)
                fail('DB đã đổi hoặc không phải DB chính; tải lại.', 'STALE', 409); return
            if path == '/api/personnel-xlsx-cancel':
                self.app.pop('pending_personnel', None); self.send_data(dict(cancelled=True)); return
            if path == '/api/personnel-xlsx-confirm':
                pending = self.app.pop('pending_personnel', None)
                if (not isinstance(p['nonce'], str) or not pending or
                    not secrets.compare_digest(p['nonce'], pending['nonce']) or
                    pending['context'] != p['context'] or time.monotonic() >= pending['expires']):
                    fail('Phiên xem trước hết hạn hoặc đã sử dụng.', 'STALE', 409); return
                self.app['catalogs'].add_personnel(pending['names'], pending['digest'])
                self.send_data(dict(added=len(pending['names']), existing=pending['existing'], fileSha256=pending['hash']))
                return
            encoded = p['fileBase64']
            if not isinstance(encoded, str):
                raise ValueError('invalid file')
            if len(encoded) > 2796204:
                fail('File vượt giới hạn 2 MiB.', 'LIMIT_EXCEEDED', 413); return
            blob = base64.b64decode(encoded, validate=True)
            if not 0 < len(blob) <= 2 * 1024 * 1024:
                fail('File vượt giới hạn 2 MiB hoặc rỗng.', 'LIMIT_EXCEEDED', 413); return
            digest = hashlib.sha256(blob).hexdigest()
            if path == '/api/personnel-xlsx-inspect':
                response = inspect_workbook(blob)
                response['fileSha256'] = digest
                self.send_data(response); return
            if (not isinstance(p['expectedFileSha256'], str) or p['expectedFileSha256'] != digest or
                not isinstance(p['sheet'], str) or type(p['headerRow']) is not int or
                not isinstance(p['columns'], dict) or set(p['columns']) != {'name','code','title','group'} or
                type(p['columns']['name']) is not int or
                any(v is not None and type(v) is not int for v in p['columns'].values()) or
                not isinstance(p['excludedRows'], list) or any(type(v) is not int for v in p['excludedRows'])):
                raise ValueError('invalid mapping')
            catalog = self.app['catalogs']
            catalog_digest = catalog.raw_digest()
            data = catalog.personnel_safe_snapshot(catalog_digest)
            plan = build_plan(blob, p['sheet'], p['headerRow'], p['columns'], p['excludedRows'], data['people'])
            additions = plan.pop('newNames')
            plan.update(fileSha256=digest, nonce=None, expiresInSeconds=None)
            if plan['canConfirm']:
                nonce = secrets.token_hex(16)
                self.app['pending_personnel'] = dict(nonce=nonce, expires=time.monotonic()+300, context=p['context'],
                    digest=catalog_digest, names=tuple(additions), existing=plan['counts']['existing'], hash=digest)
                plan.update(nonce=nonce, expiresInSeconds=300)
            self.send_data(plan)
        except AppError as exc:
            fail(str(exc), 'FORBIDDEN' if exc.status == 403 else 'INVALID_INPUT', exc.status)
        except PersonnelSaveError as exc:
            fail(str(exc), exc.code, exc.status, backup_id=exc.backup_id)
        except PersonnelXlsxError as exc:
            fail(exc.message, exc.code, 413 if exc.code == 'LIMIT_EXCEEDED' else 400, exc.sheet, exc.row, exc.column)
        except (ValueError, TypeError, KeyError, UnicodeError, binascii.Error):
            fail('Dữ liệu nhập không hợp lệ.', 'INVALID_INPUT')
        except (OSError, sqlite3.Error):
            fail('Không thể đọc hoặc ghi danh mục.', 'SAVE_FAILED', 500)

    def do_POST(self):
        if urllib.parse.urlsplit(self.path).path.startswith('/api/personnel-xlsx-'):
            return self.personnel_post()
        unread = True
        local_routes = ('/api/maintenance-preview','/api/maintenance-confirm','/api/maintenance-cancel',
                        '/api/schema-upgrade-preview','/api/schema-upgrade-confirm','/api/schema-upgrade-cancel','/api/restore-preview','/api/restore','/api/restore-cancel','/api/ships-hide','/api/save')
        local_route = urllib.parse.urlsplit(self.path).path in local_routes
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
            if self.app.get('migration_required') and route.path not in ('/api/schema-upgrade-preview','/api/schema-upgrade-confirm','/api/schema-upgrade-cancel','/api/restore-preview','/api/restore','/api/restore-cancel','/api/shutdown'):
                raise AppError('Cần nâng cấp DB trước khi sử dụng.',409)
            is_db = route.path in ('/api/open-viewer', '/api/corrections-preview')
            limit = MAX_DB if is_db else MAX_FILE if route.path == '/api/attachment-upload' else 4 * 1024 * 1024
            if not 0 <= length <= limit:
                if local_route: raise AppError('Yêu cầu quá lớn.',413)
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
            if self.app.get('migration_required') and self.path in ('/api/restore-preview','/api/restore','/api/restore-cancel'):
                p=local_json(raw,self.headers)
                keys={'context','id'} if self.path.endswith('preview') else {'context'} if self.path.endswith('cancel') else {'context','nonce','confirmation'}
                if set(p)!=keys or p.get('context')!=self.app['context'] or self.app['store'] is not self.app['main_store']:
                    raise AppError('Phiên khôi phục đã thay đổi.',409)
                if self.path.endswith('cancel'):
                    self.app.pop('pending_recovery',None)
                    self.send_data(dict(cancelled=True))
                elif self.path.endswith('preview'):
                    self.app.pop('pending_recovery',None)
                    info=self.app['protection'].recovery_preview(p['id'])
                    nonce=secrets.token_hex(16)
                    self.app['pending_recovery']=dict(id=p['id'],sha256=info['sha256'],context=p['context'],
                        main_stamp=_database_stamp(self.app['protection'].db),nonce=nonce,expires=time.monotonic()+300)
                    self.send_data(dict(info,nonce=nonce,expiresInSeconds=300))
                else:
                    pending=self.app.pop('pending_recovery',None)
                    if (p.get('confirmation')!='KHOI PHUC' or not pending or p.get('nonce')!=pending['nonce'] or
                            pending['context']!=p['context'] or time.monotonic()>=pending['expires']):
                        raise AppError('Phiên khôi phục đã hết hạn hoặc chưa xác nhận.',409)
                    try:
                        result=self.app['protection'].restore_recovery(pending['id'],pending['sha256'],pending['main_stamp'])
                        view=Store(self.app['protection'].db,readonly=True)
                        if view.meta('schema_version') not in ('1','2','3'): raise AppError('DB khôi phục không phải bản cũ.')
                        self.app['store']=self.app['main_store']=view
                        self.app['migration_required']=True
                        self.app.pop('pending_upgrade',None)
                        clear_pending_context(self.app)
                        self.app['context']=secrets.token_hex(16)
                        result['context']=self.app['context']
                        self.send_data(result)
                    except Exception:
                        if _database_stamp(self.app['protection'].db)!=pending['main_stamp']:
                            self.send_data(dict(error='Khôi phục chưa xác minh; dừng sửa và giữ bản trước khôi phục.',code='RECOVERY_REQUIRED'),status=500)
                        else: raise
            elif self.path in ('/api/maintenance-preview','/api/maintenance-confirm','/api/maintenance-cancel'):
                p = local_json(raw,self.headers)
                if not isinstance(p,dict) or p.get('context')!=self.app['context'] or self.app['store'] is not self.app['main_store'] or self.app['store'].readonly or self.app['store'].meta('review_copy')=='1':
                    raise AppError('Về DB chính trước khi bảo trì.',409)
                if self.path.endswith('preview'):
                    self.app.pop('pending_maintenance',None)
                    if set(p)!={'context','kind'} or p['kind'] not in ('viewer_cleanup','orphan_blobs','restore_drill'):
                        raise AppError('Loại bảo trì không hợp lệ.')
                    items,values=maintenance_preview(self.app,p['kind'])
                    nonce=secrets.token_hex(16)
                    self.app['pending_maintenance']=dict(nonce=nonce,kind=p['kind'],values=values,context=p['context'],expires=time.monotonic()+300)
                    response=dict(kind=p['kind'],items=items,count=len(items),nonce=nonce,expiresInSeconds=300)
                    if p['kind']=='orphan_blobs':
                        with self.app['main_store'].connect() as c:
                            response['totalBytes']=sum(c.execute('SELECT length(data) FROM attachment_blobs WHERE hash=?',(digest,)).fetchone()[0] for digest in values)
                    self.send_data(response)
                elif self.path.endswith('cancel'):
                    if set(p)!={'context','kind'}: raise AppError('Dữ liệu không hợp lệ.')
                    self.app.pop('pending_maintenance',None)
                    self.send_data(dict(cancelled=True))
                else:
                    plan=self.app.pop('pending_maintenance',None)
                    if set(p)!={'context','nonce'} or not plan or p['nonce']!=plan['nonce'] or plan['context']!=p['context'] or time.monotonic()>=plan['expires']:
                        raise AppError('Phiên bảo trì đã hết hạn.',409)
                    self.send_data(maintenance_confirm(self.app,plan['kind'],plan['values']))
            elif self.path in ('/api/schema-upgrade-preview', '/api/schema-upgrade-confirm', '/api/schema-upgrade-cancel'):
                p = local_json(raw,self.headers)
                expected_keys = {'context'} if self.path.endswith(('preview','cancel')) else {'context','nonce'}
                if not isinstance(p,dict) or set(p) != expected_keys or p.get('context') != self.app['context'] or not self.app.get('migration_required'):
                    raise AppError('Phiên nâng cấp đã thay đổi.',409)
                if self.path.endswith('cancel'):
                    self.app.pop('pending_upgrade',None)
                    self.send_data(dict(cancelled=True))
                elif self.path.endswith('preview'):
                    self.app.pop('pending_upgrade',None)
                    plan = plan_upgrade(self.app['data_dir'] / 'BAO_CAO_CA.db')
                    nonce = secrets.token_hex(16)
                    self.app['pending_upgrade'] = dict(plan=plan,nonce=nonce,context=self.app['context'],expires=time.monotonic()+300)
                    self.send_data({**{k:v for k,v in plan.items() if k not in ('stamp','manifestName','sourceDatabaseId')},'nonce':nonce,'expiresInSeconds':300})
                else:
                    pending = self.app.pop('pending_upgrade',None)
                    if not pending or p.get('nonce') != pending['nonce'] or pending['context'] != self.app['context'] or time.monotonic()>=pending['expires']:
                        raise AppError('Phiên xem trước đã hết hạn.',409)
                    plan=pending['plan']
                    try:
                        upgrade(self.app['data_dir'] / 'BAO_CAO_CA.db',plan)
                        store=Store(self.app['data_dir'] / 'BAO_CAO_CA.db')
                        protection=self.app['protection']
                        if protection.config.get('database_id') not in (None,'',plan['databaseId']):
                            from BAO_VE_DU_LIEU import atomic_json
                            archive=self.app['data_dir'] / 'TRUOC_TIEP_NHAN' / ('CAU_HINH_CU_'+secrets.token_hex(8)+'.json')
                            atomic_json(archive,protection.config)
                            protection.config={}
                        for key in ('verified_cache','last_full_local','last_full_external','last_validation'):
                            protection.config.pop(key,None)
                        protection.initialize(store)
                        self.app['store']=self.app['main_store']=store
                        self.app['catalogs']=Catalogs(self.app['data_dir'].parent/'DANH_MUC',store)
                        self.app['catalogs'].sync()
                        self.app['migration_required']=False
                        clear_pending_context(self.app)
                        self.app['context']=secrets.token_hex(16)
                        daily_backup(self.app,full=True)
                        self.send_data(dict(schemaVersion='4',databaseId=plan['databaseId'],backupName=plan['backupName'],context=self.app['context']))
                    except Exception:
                        db=self.app['data_dir'] / 'BAO_CAO_CA.db'
                        try:
                            with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as conn:
                                row=conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                            changed=not row or row[0]!=plan['sourceSchema']
                        except (OSError,sqlite3.Error):
                            changed=True
                        if changed:
                            existing=next((step['backupName'] for step in plan['migrationSteps'] if db.with_name(step['backupName']).is_file()),None)
                            self.send_data(dict(error='Nâng cấp chưa hoàn tất. Dừng sửa; đóng ứng dụng và khôi phục bản trước nâng cấp đã xác minh.',code='RECOVERY_REQUIRED',backupName=existing),status=500)
                        else:
                            raise
            elif self.app.get('migration_required') and self.path != '/api/shutdown':
                raise AppError('Cần nâng cấp DB trước khi sử dụng.',409)
            elif self.path in ('/api/protection-directory', '/api/protection-config', '/api/protection-backup', '/api/restore-preview', '/api/restore'):
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
                    daily_backup(self.app, full=True)
                    self.send_data(protection.status())
                elif self.path == '/api/restore-preview':
                    self.send_data(protection.preview(protection.selected(p.get('id'))))
                else:
                    if p.get('confirmation') != 'KHOI PHUC':
                        raise AppError('Cần nhập KHOI PHUC để xác nhận thay dữ liệu hiện tại.')
                    result = protection.restore(protection.selected(p.get('id')), p.get('sha256', ''))
                    view = Store(protection.db, readonly=True)
                    legacy = view.meta('schema_version') in ('1','2','3')
                    store = view if legacy else Store(protection.db)
                    self.app['store'] = self.app['main_store'] = store
                    self.app.pop('pending_personnel', None)
                    self.app.pop('pending_maintenance',None)
                    clear_pending_context(self.app)
                    self.app['context'] = secrets.token_hex(16)
                    self.app['migration_required'] = legacy
                    if legacy:
                        self.app.pop('catalogs',None)
                    else:
                        self.app['catalogs'] = Catalogs(self.app['data_dir'].parent / 'DANH_MUC', store)
                        daily_backup(self.app)
                    result['migrationRequired'] = legacy
                    result['context'] = self.app['context']
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
            elif self.path == '/api/ships-hide':
                p = local_json(raw,self.headers)
                if set(p)!={'context','name'} or p.get('context')!=self.app['context'] or self.app['store'] is not self.app['main_store']:
                    raise AppError('DB đã đổi. Về DB chính.',409)
                self.send_data(dict(ships=self.app['store'].hide_ship(p['name'])))
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
                try:
                    register_viewer(path)
                except (OSError, AppError):
                    logging.warning('Không thể ghi nhận bản xem; bản này sẽ không được tự dọn.')
                self.app['store'] = newstore
                self.app.pop('pending_personnel', None)
                clear_pending_context(self.app)
                self.app['context'] = secrets.token_hex(16)
                self.app.pop('pending_maintenance',None)
                self.send_data({'ok': True})
            elif self.path == '/api/main-db':
                self.app['store'] = self.app['main_store']
                self.app.pop('pending_personnel', None)
                clear_pending_context(self.app)
                self.app['context'] = secrets.token_hex(16)
                self.app.pop('pending_maintenance',None)
                self.send_data({'ok': True})
            elif self.path == '/api/enable-corrections':
                p = json.loads(raw)
                if p.get('context') != self.app['context']:
                    raise AppError('DB vừa thay đổi. Tải lại trước khi bật bổ sung.', 409)
                if self.app['store'].path.parent != (self.app['data_dir'] / 'DB_KIEM_TRA').resolve():
                    raise AppError('Chức năng này chỉ dùng trên bản sao DB kiểm tra.')
                self.app['store'] = self.app['store'].enable_corrections(p.get('reviewer', ''))
                self.app.pop('pending_personnel', None)
                clear_pending_context(self.app)
                self.app['context'] = secrets.token_hex(16)
                self.app.pop('pending_maintenance',None)
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
                p = local_json(raw,self.headers)
                if p.get('context') != self.app['context']:
                    raise AppError('DB đang mở đã thay đổi ở cửa sổ khác. Hãy tải lại tool trước khi nhập tiếp.', 409)
                if set(p) != {'context','report','version','reason','save_kind'} or not isinstance(p['report'],dict) or {'os_user','auth_user'} & p['report'].keys() or p['save_kind'] not in ('auto','manual','close','correction'):
                    raise AppError('Loại lưu không hợp lệ.')
                r = self.app['store'].save(p['report'], p.get('version'), p.get('reason', ''), p['save_kind'])
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
        except MaintenanceError as e:
            self.send_data(dict(error=str(e),code='OPERATION_FAILED',completed=e.completed,retained=e.retained),status=500)
        except AppError as e:
            result={'error':str(e)}
            if local_route: result['code']='FORBIDDEN' if e.status==403 else 'CONFLICT' if e.status==409 else 'LIMIT_EXCEEDED' if e.status==413 else 'INVALID_INPUT'
            if unread:
                self.reject_unread(result, e.status)
            else:
                self.send_data(result, status=e.status)
        except (sqlite3.Error, OSError) as e:
            logging.exception('Loi tai tep / ghi DB: %s', urllib.parse.urlsplit(self.path).path)
            self.send_data({'error': database_error(e), **({'code':'OPERATION_FAILED'} if local_route else {})}, status=503 if 'locked' in str(e).lower() else 500)
        except (ValueError, KeyError, TypeError, AttributeError):
            self.send_data({'error': 'Dữ liệu gửi lên không hợp lệ.', **({'code':'INVALID_INPUT'} if local_route else {})}, status=400)
        except Exception:
            logging.exception('Loi ghi du lieu')
            self.send_data({'error': 'Lỗi chương trình khi xử lý tệp/dữ liệu. Xem DU_LIEU/LOI_CHUONG_TRINH.log; chưa thể kết luận do dung lượng hoặc quyền ghi.'}, status=500)


def daily_backup(app, force=True, full=False):
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
        level = protection.backup_level(force_full=full)
        result = protection.backup(level=level)
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
        db = directory / 'BAO_CAO_CA.db'
        legacy = False
        if db.exists() and db.stat().st_size:
            with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as conn:
                row=conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                legacy=bool(row and row[0] in ('1','2','3'))
        store = Store(db, readonly=legacy)
        if not legacy:
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
                         host='127.0.0.1:' + str(server.server_port), migration_required=legacy)
        if not legacy:
            server.app['catalogs'] = Catalogs(directory.parent / 'DANH_MUC', store)
            server.app['catalogs'].sync()
            daily_backup(server.app)
        return server
    except Exception:
        if server is not None:
            server.server_close()
        lock.close()
        raise
