"""Lưu SQLite, lịch sử, ảnh và đối chiếu bản bổ sung."""
import hashlib
import json
from pathlib import Path
import re
import secrets
import sqlite3
from THIET_LAP import MAX_FILE, PEOPLE, SHIPS
from NGHIEP_VU import now, AppError, clean_text, file_type, ClosingConnection, ship_names, report_ships, normalize

SUPPORTED_SCHEMAS = ('1', '2', '3')
# DB cũ được giữ nguyên một bản trước khi nâng lên schema 3.
UPGRADE_COPY_SUFFIX = {'1': '_TRUOC_NANG_CAP_1_2.db', '2': '_TRUOC_NANG_CAP_1_4.db'}
SCHEMA = '''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reports(
  id TEXT PRIMARY KEY, day TEXT NOT NULL, shift TEXT NOT NULL,
  version INTEGER NOT NULL, status TEXT NOT NULL,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
  actor TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(day, shift));
CREATE TABLE IF NOT EXISTS revisions(
  id INTEGER PRIMARY KEY, report_id TEXT NOT NULL, version INTEGER NOT NULL,
  saved_at TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
  payload TEXT NOT NULL, UNIQUE(report_id, version));
CREATE INDEX IF NOT EXISTS report_days ON reports(day, shift);
CREATE TABLE IF NOT EXISTS correction_base(
  report_id TEXT PRIMARY KEY, version INTEGER NOT NULL, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS attachment_blobs(
  hash TEXT PRIMARY KEY, mime TEXT NOT NULL, data BLOB NOT NULL,
  uploaded_at TEXT NOT NULL, actor TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS people(name TEXT PRIMARY KEY, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS ships(name TEXT PRIMARY KEY, active INTEGER NOT NULL DEFAULT 1);
INSERT OR IGNORE INTO meta VALUES('schema_version', '3');
'''


class Store:
    def __init__(self, path, readonly=False):
        self.path = Path(path).resolve()
        self.readonly = readonly
        self._creating = not readonly and not self.path.exists()
        if not readonly:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._preserve_before_upgrade()
            self._ensure_schema()
        self._creating = False
        self.validate()

    def _preserve_before_upgrade(self):
        """Từ chối schema lạ; giữ bản gốc của DB schema 1/2 trước khi nâng cấp."""
        if not (self.path.exists() and self.path.stat().st_size):
            return
        with self.connect() as source:
            row = source.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if not row or row[0] not in SUPPORTED_SCHEMAS:
                raise AppError('DB có phiên bản không được hỗ trợ. Không thay đổi dữ liệu.')
            suffix = UPGRADE_COPY_SUFFIX.get(row[0])
            if suffix:
                previous = self.path.with_name(self.path.stem + suffix)
                if not previous.exists():
                    with sqlite3.connect(str(previous), factory=ClosingConnection) as dest:
                        source.backup(dest)

    def _ensure_schema(self):
        with self.connect() as c:
            c.executescript(SCHEMA)
            c.execute("UPDATE meta SET value='3' WHERE key='schema_version'")
            c.execute("INSERT OR IGNORE INTO meta VALUES('database_id',?)", (secrets.token_hex(16),))
            self._seed_once(c, 'people', PEOPLE)
            self._seed_once(c, 'ships', SHIPS)

    @staticmethod
    def _seed_once(c, table, names):
        """Nạp danh sách mặc định đúng một lần; về sau người dùng tự quản lý."""
        flag = table + '_seeded'
        if c.execute('SELECT 1 FROM meta WHERE key=?', (flag,)).fetchone():
            return
        c.executemany('INSERT OR IGNORE INTO ' + table + '(name) VALUES(?)', [(name,) for name in names])
        c.execute('INSERT INTO meta VALUES(?,?)', (flag, '1'))

    def connect(self):
        uri = self.path.as_uri() + ('?mode=ro' if self.readonly else '?mode=rw')
        # First creation must permit SQLite to create the file.
        creating = self._creating and not self.path.exists()
        c = sqlite3.connect(str(self.path) if creating else uri, uri=not creating, timeout=10,
                            factory=ClosingConnection)
        c.row_factory = sqlite3.Row
        c.execute('PRAGMA busy_timeout=10000')
        if self.readonly:
            c.execute('PRAGMA query_only=ON')
        return c

    def validate(self):
        try:
            with self.connect() as c:
                if c.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    raise ValueError()
                if c.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0] not in SUPPORTED_SCHEMAS:
                    raise ValueError()
                c.execute('SELECT id,day,shift,version,status,created_at,updated_at,actor,payload FROM reports LIMIT 1')
                c.execute('SELECT report_id,version,saved_at,actor,reason,payload FROM revisions LIMIT 1')
        except (sqlite3.Error, ValueError, TypeError):
            raise AppError('DB không đúng định dạng Sổ báo cáo ca 1.0 hoặc đã hỏng.')

    @staticmethod
    def decode(r):
        if r is None:
            return None
        d = json.loads(r['payload'])
        d.update(id=r['id'], version=r['version'], created_at=r['created_at'], updated_at=r['updated_at'])
        return d

    def get(self, rid):
        with self.connect() as c:
            r = self.decode(c.execute('SELECT * FROM reports WHERE id=?', (rid,)).fetchone())
        if r is None:
            raise AppError('Chưa có báo cáo ca này.', 404)
        return r

    def save(self, p, expected, reason=''):
        if self.readonly:
            raise AppError('Đang xem bản DB kiểm tra. Không được ghi dữ liệu.', 403)
        d = normalize(p)
        reason = clean_text(reason, 1000)
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            return self._save_report(c, d, expected, reason)

    def _save_report(self, c, d, expected, reason):
        """Caller owns the transaction; report and revision commit together."""
        rid = d['date'] + '_' + d['shift']
        stamp = now()
        old = c.execute('SELECT * FROM reports WHERE id=?', (rid,)).fetchone()
        for a in d.get('attachments', []):
            if not c.execute('SELECT 1 FROM attachment_blobs WHERE hash=?', (a['hash'],)).fetchone():
                raise AppError('Tệp đính kèm chưa có trong DB. Tải tệp lên lại trước khi lưu.')
        review = c.execute("SELECT value FROM meta WHERE key='review_copy'").fetchone()
        if review and review[0] == '1':
            if not old:
                raise AppError('Bản bổ sung chỉ sửa ca đã có. Tạo ca mới trên máy nhập chính.')
            if not reason:
                raise AppError('Nhập lý do bổ sung trước khi lưu bản kiểm tra.')
        version = old['version'] if old else 0
        if type(expected) is not int or expected != version:
            raise AppError('Báo cáo đã được lưu ở cửa sổ khác. Hãy tải lại trước khi sửa tiếp.', 409)
        if old and old['status'] == 'closed' and not reason:
            raise AppError('Báo cáo đã chốt. Cần nhập lý do sửa và lưu thủ công.')
        if old and old['status'] == 'closed' and d['status'] != 'closed':
            raise AppError('Báo cáo đã chốt phải giữ trạng thái đã chốt.')
        payload = json.dumps(d, ensure_ascii=False)
        if old and payload == old['payload']:
            return self.decode(old)
        version += 1
        c.executemany('INSERT OR IGNORE INTO ships(name) VALUES(?)', [(name,) for name in report_ships(d)])
        c.execute('INSERT INTO reports VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
                  'version=excluded.version,status=excluded.status,updated_at=excluded.updated_at,'
                  'actor=excluded.actor,payload=excluded.payload',
                  (rid, d['date'], d['shift'], version, d['status'], old['created_at'] if old else stamp,
                   stamp, d['actor'], payload))
        c.execute('INSERT INTO revisions(report_id,version,saved_at,actor,reason,payload) VALUES(?,?,?,?,?,?)',
                  (rid, version, stamp, d['actor'], reason or ('Chốt ca' if d['status'] == 'closed' else 'Lưu nháp'), payload))
        return self.decode(c.execute('SELECT * FROM reports WHERE id=?', (rid,)).fetchone())

    def meta(self, key):
        with self.connect() as c:
            row = c.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
        return row[0] if row else None

    def people(self):
        with self.connect() as c:
            if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='people'").fetchone():
                return [r[0] for r in c.execute('SELECT name FROM people WHERE active=1 ORDER BY rowid')]
        return PEOPLE.copy()

    def ships(self):
        with self.connect() as c:
            if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='ships'").fetchone():
                return [r[0] for r in c.execute('SELECT name FROM ships WHERE active=1 ORDER BY rowid')]
        return SHIPS.copy()

    def add_ship(self, name):
        if self.readonly:
            raise AppError('Bật chỉnh sửa / bổ sung trước khi thêm tàu.', 403)
        names = ship_names([name])
        if not names:
            raise AppError('Điền tên tàu mới.')
        with self.connect() as c:
            c.execute('INSERT INTO ships(name,active) VALUES(?,1) ON CONFLICT(name) DO UPDATE SET active=1', (names[0],))
        return self.ships()

    def _attachment_record(self, raw, filename, actor):
        if not raw or len(raw) > MAX_FILE:
            raise AppError('Mỗi tệp tối đa 100 MB, không nhận tệp rỗng.')
        mime, _ = file_type(raw)
        actor = clean_text(actor, 100)
        if not actor:
            raise AppError('Điền người nhập trước khi thêm tệp.')
        filename = clean_text(filename, 240).replace('\\', '/').split('/')[-1]
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename) or 'dinh_kem'
        suffix = Path(filename).suffix
        filename = Path(filename).stem[:max(1, 180-len(suffix))] + suffix
        digest = hashlib.sha256(raw).hexdigest()
        return dict(hash=digest, name=filename, caption=''), mime, actor

    def _insert_blob(self, c, attachment, mime, raw, actor):
        c.execute('INSERT OR IGNORE INTO attachment_blobs(hash,mime,data,uploaded_at,actor) VALUES(?,?,?,?,?)',
                  (attachment['hash'], mime, sqlite3.Binary(raw), now(), actor))

    def upload_attachment(self, raw, filename, actor):
        if self.readonly:
            raise AppError('Bật chỉnh sửa / bổ sung trước khi thêm tệp.', 403)
        attachment, mime, actor = self._attachment_record(raw, filename, actor)
        with self.connect() as c:
            self._insert_blob(c, attachment, mime, raw, actor)
        return attachment

    def add_attachment(self, rid, expected, raw, filename, actor, caption=''):
        if self.readonly:
            raise AppError('Bản sao đang chỉ xem.', 403)
        attachment, mime, actor = self._attachment_record(raw, filename, actor)
        attachment['caption'] = clean_text(caption, 1000)
        # Validate capacity/version before writing. Any later failure rolls back the blob too.
        with self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            report = self.decode(c.execute('SELECT * FROM reports WHERE id=?', (rid,)).fetchone())
            if report is None:
                raise AppError('Chưa có báo cáo ca này.', 404)
            if type(expected) is not int or report['version'] != expected:
                raise AppError('Báo cáo đã thay đổi ở cửa sổ khác. Mở lại báo cáo để tải tệp.', 409)
            if any(a['hash'] == attachment['hash'] for a in report.get('attachments', [])):
                return dict(attachment=attachment, report=report, added=False)
            if len(report.get('attachments', [])) >= 40:
                raise AppError('Ca này đã đủ 40 tệp đính kèm.')
            report.setdefault('attachments', []).append(attachment)
            report['actor'] = actor
            checked = normalize(report)
            self._insert_blob(c, attachment, mime, raw, actor)
            saved = self._save_report(c, checked, expected, 'Thêm tệp đính kèm: ' + attachment['name'])
            return dict(attachment=attachment, report=saved, added=True)

    def attachment(self, digest):
        if not re.fullmatch(r'[a-f0-9]{64}', digest):
            raise AppError('Mã tệp không hợp lệ.')
        with self.connect() as c:
            exists = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='attachment_blobs'").fetchone()
            row = c.execute('SELECT * FROM attachment_blobs WHERE hash=?', (digest,)).fetchone() if exists else None
        if not row:
            raise AppError('Không tìm thấy tệp trong DB này.', 404)
        return row

    def enable_corrections(self, reviewer):
        if not self.readonly:
            raise AppError('Bản này đã cho phép chỉnh sửa.')
        # Only called on a copy created in DB_KIEM_TRA, never on the uploaded original.
        if not self.meta('database_id'):
            raise AppError('DB từ bản 1.0 chưa có mã nguồn dữ liệu. Mở DB chính bằng bản 1.1 rồi Sao lưu mang đi lại trước khi bổ sung.')
        writable = Store(self.path)
        reviewer = clean_text(reviewer, 100)
        if not reviewer:
            raise AppError('Nhập tên người kiểm tra / bổ sung.')
        with writable.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('INSERT OR IGNORE INTO correction_base SELECT id,version,payload FROM reports')
            c.execute("INSERT OR REPLACE INTO meta VALUES('review_copy','1')")
            c.execute("INSERT OR REPLACE INTO meta VALUES('reviewer_name',?)", (reviewer,))
        return writable

    def correction_plan(self, incoming):
        if self.readonly or self.meta('review_copy') == '1':
            raise AppError('Chỉ nhập bổ sung vào DB chính của máy nhập.')
        if not self.meta('database_id') or self.meta('database_id') != incoming.meta('database_id'):
            raise AppError('DB này không cùng nguồn với DB chính. Hãy nhập bổ sung tại đúng máy bãi đã xuất bản sao.')
        if incoming.meta('review_copy') != '1':
            raise AppError('File này chưa phải bản DB bổ sung. Chọn DB đã bật bổ sung, sửa và xuất lại.')
        with incoming.connect() as source, self.connect() as target:
            try:
                bases = source.execute('SELECT * FROM correction_base').fetchall()
            except sqlite3.Error:
                raise AppError('DB không có mốc đối chiếu để nhập bổ sung.')
            result = []
            for b in bases:
                final = source.execute('SELECT * FROM reports WHERE id=?', (b['report_id'],)).fetchone()
                if not final or final['payload'] == b['payload']:
                    continue
                current = target.execute('SELECT * FROM reports WHERE id=?', (b['report_id'],)).fetchone()
                state = ('missing' if not current else 'same' if current['payload'] == final['payload'] else
                         'ready' if current['payload'] == b['payload'] else 'conflict')
                result.append(dict(id=b['report_id'], state=state, date=final['day'], shift=final['shift'],
                                   actor=final['actor'], current=self.decode(current), incoming=self.decode(final),
                                   base_version=b['version'], base_payload=b['payload']))
        return result

    def apply_corrections(self, incoming, selected):
        plan = {r['id']: r for r in self.correction_plan(incoming)}
        if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)):
            raise AppError('Chọn ít nhất một báo cáo, không chọn trùng.')
        for rid in selected:
            if rid not in plan or plan[rid]['state'] != 'ready':
                raise AppError('Có báo cáo đã thay đổi hoặc xung đột. Xem đối chiếu lại trước khi nhập.', 409)
        # Preserve every reviewer revision, not just the final snapshot.
        with incoming.connect() as source, self.connect() as target:
            target.execute('BEGIN IMMEDIATE')
            for rid in selected:
                item = plan[rid]
                current = target.execute('SELECT * FROM reports WHERE id=?', (rid,)).fetchone()
                if not current or current['payload'] != item['base_payload']:
                    raise AppError('Báo cáo vừa đổi ở cửa sổ khác. Không ghi đè.', 409)
                edits = source.execute('SELECT * FROM revisions WHERE report_id=? AND version>? ORDER BY version',
                                       (rid, item['base_version'])).fetchall()
                if not edits:
                    raise AppError('Bản bổ sung thiếu lịch sử chỉnh sửa.')
                if edits[-1]['payload'] != source.execute('SELECT payload FROM reports WHERE id=?', (rid,)).fetchone()[0]:
                    raise AppError('Lịch sử bản bổ sung không khớp nội dung cuối.')
                version = current['version']
                for edit in edits:
                    checked = normalize(json.loads(edit['payload']))
                    target.executemany('INSERT OR IGNORE INTO ships(name) VALUES(?)', [(name,) for name in report_ships(checked)])
                    if checked['date'] + '_' + checked['shift'] != rid:
                        raise AppError('Lịch sử có ngày/ca không khớp.')
                    if current['status'] == 'closed' and checked['status'] != 'closed':
                        raise AppError('Không nhập bản sửa làm mở lại ca đã chốt.')
                    for a in checked.get('attachments', []):
                        blob = source.execute('SELECT * FROM attachment_blobs WHERE hash=?', (a['hash'],)).fetchone()
                        if not blob or hashlib.sha256(blob['data']).hexdigest() != a['hash']:
                            raise AppError('Tệp đính kèm trong bản bổ sung bị thiếu hoặc không khớp. Chưa nhập dữ liệu.')
                        target.execute('INSERT OR IGNORE INTO attachment_blobs(hash,mime,data,uploaded_at,actor) VALUES(?,?,?,?,?)',
                                       (blob['hash'], blob['mime'], blob['data'], blob['uploaded_at'], blob['actor']))
                    version += 1
                    reason = 'Bổ sung từ DB • ' + edit['reason'] + ' • Nhập về máy chính ' + now()
                    target.execute('INSERT INTO revisions(report_id,version,saved_at,actor,reason,payload) VALUES(?,?,?,?,?,?)',
                                   (rid, version, edit['saved_at'], checked['actor'], reason, edit['payload']))
                final = item['incoming']
                target.execute('UPDATE reports SET version=?,status=?,updated_at=?,actor=?,payload=? WHERE id=?',
                               (version, final['status'], now(), final['actor'], edits[-1]['payload'], rid))
        return len(selected)

    _FILTERS = (('from', 'day>=?'), ('to', 'day<=?'), ('shift', 'shift=?'), ('status', 'status=?'))
    _ORDER = " ORDER BY day DESC, CASE shift WHEN 'NIGHT' THEN 0 ELSE 1 END"

    def _where(self, filters):
        clauses, args = [], []
        for key, expr in self._FILTERS:
            if filters.get(key):
                clauses.append(expr)
                args.append(filters[key])
        return (' WHERE ' + ' AND '.join(clauses)) if clauses else '', args

    @staticmethod
    def _search_text(filters):
        return (filters.get('q') or '').strip().casefold()

    def list(self, filters):
        where, args = self._where(filters)
        with self.connect() as c:
            rows = [self.decode(r) for r in c.execute('SELECT * FROM reports' + where + self._ORDER, args)]
        q = self._search_text(filters)
        if q:
            rows = [r for r in rows if q in json.dumps(r, ensure_ascii=False).casefold()]
        return rows

    def page(self, filters, limit, offset=0):
        """Một trang báo cáo + tổng số. Không tìm chữ thì phân trang ngay trong SQL."""
        if self._search_text(filters):
            rows = self.list(filters)
            return dict(rows=rows[offset:offset + limit], total=len(rows), limit=limit, offset=offset)
        where, args = self._where(filters)
        with self.connect() as c:
            total = c.execute('SELECT COUNT(*) FROM reports' + where, args).fetchone()[0]
            rows = [self.decode(r) for r in c.execute(
                'SELECT * FROM reports' + where + self._ORDER + ' LIMIT ? OFFSET ?', args + [limit, offset])]
        return dict(rows=rows, total=total, limit=limit, offset=offset)

    def overview(self, suggestion, month, recent=6):
        """Số liệu trang chủ; không đọc toàn bộ báo cáo."""
        with self.connect() as c:
            month_count = c.execute('SELECT COUNT(*) FROM reports WHERE day>=? AND day<=?',
                                    (month + '-01', month + '-31')).fetchone()[0]
            drafts = c.execute("SELECT COUNT(*) FROM reports WHERE status='draft'").fetchone()[0]
            rows = [self.decode(r) for r in c.execute('SELECT * FROM reports' + self._ORDER + ' LIMIT ?', (recent,))]
            current = c.execute('SELECT status FROM reports WHERE id=?',
                                (suggestion['date'] + '_' + suggestion['shift'],)).fetchone()
        return dict(month_count=month_count, draft_count=drafts, recent=rows,
                    current_status=current[0] if current else '')

    def history(self, rid):
        with self.connect() as c:
            rows = [dict(r) for r in c.execute('SELECT version,saved_at,actor,reason,payload FROM revisions WHERE report_id=? ORDER BY version DESC', (rid,))]
        for r in rows:
            r['payload'] = json.loads(r['payload'])
        return rows

    def backup(self, dest):
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.resolve() == self.path:
            raise AppError('Không ghi đè DB chính.')
        with self.connect() as source, sqlite3.connect(str(dest), factory=ClosingConnection) as target:
            source.backup(target)
            target.commit()
        return dest
