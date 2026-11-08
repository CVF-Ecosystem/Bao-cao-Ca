"""Danh mục tệp ngoài; không sửa báo cáo lịch sử khi đổi nhân viên/vị trí."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import unicodedata

from NGHIEP_VU import AppError
from THIET_LAP import JOBS, ROLES
from MAU_PHAN_CONG import default_templates, merge_team_members, parse_templates, validate_templates


FILES = {'people': 'NHAN_VIEN.txt', 'roles': 'VI_TRI.txt', 'jobs': 'CONG_VIEC.txt', 'teams': 'TO_NHAN_SU.json', 'staff_templates': 'MAU_PHAN_CONG.json'}
KEEP_CATALOG_BACKUPS = 20
LIMITS = {'people': (500, 120), 'roles': (80, 150), 'jobs': (100, 200)}


def parse_lines(text, key):
    if not isinstance(text, str) or len(text) > 200000:
        raise AppError('Danh mục quá dài hoặc sai định dạng.')
    values, seen = [], set()
    count, length = LIMITS[key]
    for line in text.splitlines():
        value = unicodedata.normalize('NFC', line.strip())
        if not value or value.startswith('#'):
            continue
        if len(value) > length or any(ord(c) < 32 for c in value):
            raise AppError(FILES[key] + ': tên quá dài hoặc chứa ký tự không hợp lệ.')
        if ';' in value:
            raise AppError(FILES[key] + ': mỗi dòng chỉ một tên, không dùng dấu chấm phẩy.')
        if value.casefold() in seen:
            raise AppError(FILES[key] + ': tên bị trùng: ' + value)
        seen.add(value.casefold())
        values.append(value)
    if not values or len(values) > count:
        raise AppError(FILES[key] + ': phải có từ 1 đến ' + str(count) + ' dòng.')
    # Chốt ca sử dụng vị trí này làm điều kiện bắt buộc.
    if key == 'roles' and not any(v.upper() == 'PHỤ TRÁCH CHUNG' for v in values):
        raise AppError('VI_TRI.txt cần giữ vị trí PHỤ TRÁCH CHUNG để chốt ca.')
    return values


def default_teams():
    return [dict(id='team'+str(i), name='Ca '+str(i), people=[]) for i in range(1, 4)]


def parse_teams(text):
    if not isinstance(text, str) or len(text) > 200000:
        raise AppError('TO_NHAN_SU.json: dữ liệu quá dài hoặc sai kiểu.')
    try:
        items = json.loads(text)
    except ValueError:
        raise AppError('TO_NHAN_SU.json: sai định dạng. Sửa tại Danh mục / 3 tổ nhân sự.')
    if not isinstance(items, list) or len(items) != 3:
        raise AppError('Cần đúng 3 tổ nhân sự.')
    teams, labels = [], set()
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict) or item.get('id') != 'team'+str(i):
            raise AppError('Mã tổ cần giữ team1, team2, team3 theo thứ tự.')
        name = item.get('name')
        if not isinstance(name, str) or not name.strip() or len(name) > 80 or any(ord(c)<32 for c in name):
            raise AppError('Tên tổ phải có từ 1 đến 80 ký tự, không xuống dòng.')
        name = unicodedata.normalize('NFC', name.strip())
        if name.casefold() in labels:
            raise AppError('Tên các tổ không được trùng nhau.')
        labels.add(name.casefold())
        people = item.get('people')
        if not isinstance(people, list) or len(people) > 500 or not all(isinstance(v,str) for v in people):
            raise AppError(name+': danh sách nhân viên không hợp lệ.')
        # Empty teams are valid before the user sets up the real roster.
        if any(not v.strip() or '\n' in v or '\r' in v for v in people):
            raise AppError(name+': mỗi mục chỉ chứa một họ tên, không để trống.')
        checked = parse_lines('\n'.join(people), 'people') if people else []
        teams.append(dict(id=item['id'], name=name, people=checked))
    return teams


def parse_catalog(text, key):
    if key == 'teams': return parse_teams(text)
    if key == 'staff_templates': return parse_templates(text)
    return parse_lines(text, key)


def serialize_catalog(values, key):
    return json.dumps(values, ensure_ascii=False, indent=2)+'\n' if key in ('teams', 'staff_templates') else '\n'.join(values)+'\n'


def validate_team_members(data):
    known = set(data['people'])
    for team in data['teams']:
        for person in team['people']:
            if person not in known:
                raise AppError(team['name']+': '+person+' chưa có trong danh mục Nhân viên. Thêm đúng họ tên ở Nhân viên trước.')


class PersonnelSaveError(Exception):
    def __init__(self, message, code, status, backup_id=None):
        super().__init__(message)
        self.code, self.status, self.backup_id = code, status, backup_id


class Catalogs:
    def __init__(self, directory, main_store):
        self.directory = Path(directory)
        self.store = main_store
        self.directory.mkdir(parents=True, exist_ok=True)
        seeds = dict(people=main_store.people(),
                     roles=json.loads(main_store.meta('catalog_roles') or 'null') or ROLES,
                     jobs=json.loads(main_store.meta('catalog_jobs') or 'null') or JOBS,
                     teams=json.loads(main_store.meta('catalog_teams') or 'null') or default_teams(),
                     staff_templates=json.loads(main_store.meta('catalog_staff_templates') or 'null') or default_templates())
        # Chỉ tạo file thiếu; không ghi đè danh mục người dùng đã chỉnh.
        for key, filename in FILES.items():
            path = self.directory / filename
            if not path.exists():
                path.write_text(serialize_catalog(seeds[key], key), encoding='utf-8')
        self.warning = ''

    def read(self):
        result = {}
        try:
            for key, filename in FILES.items():
                result[key] = parse_catalog((self.directory / filename).read_text(encoding='utf-8-sig'), key)
        except (OSError, UnicodeError) as exc:
            raise AppError('Không đọc được DANH_MUC. Lưu file bằng UTF-8 hoặc sửa qua nút Danh mục. ' + str(exc))
        validate_team_members(result)
        validate_templates(result)
        result['teams'] = merge_team_members(result)
        result['digest'] = hashlib.sha256(json.dumps(result, ensure_ascii=False).encode()).hexdigest()
        return result

    def snapshot(self, store=None):
        store = store or self.store
        try:
            return dict(people=store.people(), roles=json.loads(store.meta('catalog_roles') or 'null') or ROLES,
                        jobs=json.loads(store.meta('catalog_jobs') or 'null') or JOBS,
                        teams=json.loads(store.meta('catalog_teams') or 'null') or default_teams(),
                        staff_templates=json.loads(store.meta('catalog_staff_templates') or 'null') or default_templates(),
                        digest=store.meta('catalog_digest') or '')
        except (ValueError, TypeError):
            raise AppError('Bản danh mục lưu trong DB không hợp lệ.')

    def sync(self):
        try:
            data = self.read()
            if self.store.meta('catalog_digest') != data['digest']:
                with self.store.connect() as c:
                    c.execute('BEGIN IMMEDIATE')
                    c.execute('DELETE FROM people')
                    c.executemany('INSERT INTO people(name,active) VALUES(?,1)', [(s,) for s in data['people']])
                    for key in ('roles', 'jobs', 'teams', 'staff_templates'):
                        c.execute('INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)',
                                  ('catalog_' + key, json.dumps(data[key], ensure_ascii=False)))
                    c.execute("INSERT OR REPLACE INTO meta VALUES('catalog_digest',?)", (data['digest'],))
            self.warning = ''
            return data
        except AppError as exc:
            self.warning = str(exc) + ' Đang dùng danh mục hợp lệ gần nhất trong DB.'
            return self.snapshot()

    def editor_data(self):
        contents = {}
        for key, filename in FILES.items():
            try:
                contents[key] = (self.directory / filename).read_text(encoding='utf-8-sig')
            except (OSError, UnicodeError):
                contents[key] = serialize_catalog(self.snapshot()[key], key)
        contents['digest'] = self.raw_digest()
        return contents

    def raw_digest(self):
        h = hashlib.sha256()
        for filename in FILES.values():
            try:
                h.update((self.directory / filename).read_bytes())
            except OSError:
                h.update(b'<missing>')
            h.update(b'\x00')
        return h.hexdigest()

    def prune_backups(self, keep=KEEP_CATALOG_BACKUPS):
        """Giữ các bản sao danh mục mới nhất; lỗi dọn dẹp không được chặn việc lưu."""
        root = self.directory / 'SAO_LUU'
        try:
            folders = sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
            for old in folders[keep:]:
                shutil.rmtree(old, ignore_errors=True)
        except OSError:
            pass

    def personnel_safe_snapshot(self, expected):
        if self.raw_digest() != expected:
            raise PersonnelSaveError('Danh mục đã thay đổi; xem trước lại.', 'STALE', 409)
        try:
            data = self.read()
            snapshot = self.snapshot()
            with self.store.connect() as conn:
                rows = [(row['name'], row['active']) for row in conn.execute('SELECT name,active FROM people')]
            if (any(active != 1 for _, active in rows) or
                    sorted(name for name, _ in rows) != sorted(data['people']) or
                    any(snapshot[key] != data[key] for key in ('roles', 'jobs', 'teams', 'staff_templates')) or
                    snapshot['digest'] != data['digest']):
                raise PersonnelSaveError('Danh mục hoặc DB chưa đồng bộ / có người ngừng hoạt động. Hãy đối chiếu danh mục trước.', 'CATALOG_UNSAFE', 409)
            return data
        except PersonnelSaveError:
            raise
        except (AppError, OSError, ValueError, TypeError) as exc:
            raise PersonnelSaveError('Danh mục không an toàn để nhập; hãy đối chiếu danh mục.', 'CATALOG_UNSAFE', 409) from exc

    def add_personnel(self, names, expected):
        current = self.personnel_safe_snapshot(expected)
        people = parse_lines('\n'.join(current['people'] + list(names)), 'people')
        if not names or people != current['people'] + list(names):
            raise PersonnelSaveError('Kế hoạch nhập không hợp lệ.', 'CATALOG_UNSAFE', 409)
        originals = {}
        backup_id = secrets.token_hex(8)
        backup = self.directory / 'SAO_LUU' / backup_id
        try:
            for filename in FILES.values():
                originals[filename] = (self.directory / filename).read_bytes()
            backup.mkdir(parents=True)
            for filename, content in originals.items():
                (backup / filename).write_bytes(content)
                if (backup / filename).read_bytes() != content:
                    raise OSError('backup verification failed')
        except OSError as exc:
            raise PersonnelSaveError('Không tạo được bản sao danh mục; chưa nhập.', 'SAVE_FAILED', 500) from exc
        self.personnel_safe_snapshot(expected)
        people_path = self.directory / FILES['people']
        temp = self.directory / (FILES['people'] + '.personnel.tmp')
        written = serialize_catalog(people, 'people').encode('utf-8')
        replaced = False
        try:
            with temp.open('wb') as f:
                f.write(written)
                f.flush()
                os.fsync(f.fileno())
            self.personnel_safe_snapshot(expected)
            os.replace(temp, people_path)
            replaced = True
            result = self.sync()
            if self.warning or sorted(result['people']) != sorted(people):
                raise RuntimeError('catalog synchronization failed')
            self.personnel_safe_snapshot(self.raw_digest())
            if any((self.directory / filename).read_bytes() != content for filename, content in originals.items() if filename != FILES['people']):
                raise RuntimeError('other catalog changed')
            return result
        except Exception as exc:
            if not replaced:
                if isinstance(exc, PersonnelSaveError):
                    raise
                raise PersonnelSaveError('Không thể nhập; danh mục chưa thay đổi.', 'SAVE_FAILED', 500, backup_id) from exc
            try:
                if people_path.read_bytes() != written:
                    raise RuntimeError('people file changed externally')
                restore = self.directory / (FILES['people'] + '.personnel.restore.tmp')
                restore.write_bytes((backup / FILES['people']).read_bytes())
                os.replace(restore, people_path)
                self.sync()
                if self.warning or any((self.directory / filename).read_bytes() != content for filename, content in originals.items()):
                    raise RuntimeError('restore verification failed')
                self.personnel_safe_snapshot(expected)
            except Exception as restore_error:
                raise PersonnelSaveError('Khôi phục chưa xác minh. Dừng chỉnh sửa và dùng bản sao danh mục.', 'RECOVERY_REQUIRED', 500, backup_id) from restore_error
            raise PersonnelSaveError('Nhập thất bại; đã xác minh khôi phục danh mục.', 'SAVE_FAILED', 500, backup_id) from exc
        finally:
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass

    def save(self, text, expected):
        if not isinstance(text, dict):
            raise AppError('Nội dung danh mục không hợp lệ.')
        if expected != self.raw_digest():
            raise AppError('Danh mục đã đổi ở nơi khác. Đóng và mở lại Danh mục để tránh ghi đè.', 409)
        current = self.editor_data()
        parsed = {key: parse_catalog(text.get(key, current[key] if key in ('teams', 'staff_templates') else ''), key) for key in FILES}
        validate_team_members(parsed)
        validate_templates(parsed)
        parsed['teams'] = merge_team_members(parsed)
        backup = self.directory / 'SAO_LUU' / secrets.token_hex(8)
        backup.mkdir(parents=True, exist_ok=True)
        old = {}
        for filename in FILES.values():
            path = self.directory / filename
            old[filename] = path.read_bytes() if path.exists() else None
            if old[filename] is not None:
                (backup / filename).write_bytes(old[filename])
        self.prune_backups()
        try:
            for key, filename in FILES.items():
                temp = self.directory / (filename + '.tmp')
                temp.write_text(serialize_catalog(parsed[key], key), encoding='utf-8')
                os.replace(temp, self.directory / filename)
            data = self.sync()
            if self.warning:
                raise AppError(self.warning)
            return data
        except Exception:
            for filename, content in old.items():
                path = self.directory / filename
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)
            raise
