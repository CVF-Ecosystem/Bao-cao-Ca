"""Sao lưu SQLite đã kiểm tra, nhiều phiên bản và khôi phục có bảo toàn DB cũ."""
import datetime as dt
import hashlib
import json
import logging
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
from NGHIEP_VU import AppError, ClosingConnection
from THIET_LAP import VN


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + secrets.token_hex(4) + '.tmp')
    try:
        with tmp.open('w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def inspect_db(path):
    """Read-only, không tạo file nếu đường dẫn đã mất; kiểm tra cả cấu trúc và JSON."""
    path = Path(path).resolve()
    from LUU_TRU import Store
    store = Store(path, readonly=True)
    with store.connect() as c:
        checks = [r[0] for r in c.execute('PRAGMA integrity_check')]
        if checks != ['ok']:
            raise AppError('Bản sao bị lỗi toàn vẹn, không thể khôi phục.')
        rows = c.execute('SELECT day,shift,payload FROM reports ORDER BY day,shift').fetchall()
        for row in rows:
            payload = json.loads(row['payload'])
            if payload.get('date') != row['day'] or payload.get('shift') != row['shift']:
                raise AppError('Ngày/ca trong nội dung DB không khớp.')
        for row in c.execute('SELECT payload FROM revisions'):
            if not isinstance(json.loads(row[0]), dict):
                raise AppError('Lịch sử chỉnh sửa không hợp lệ.')
        # Nội dung ảnh/PDF cũng nằm trong snapshot; kiểm tra không mất byte.
        for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attachment_blobs'"):
            for blob in c.execute('SELECT hash,data FROM attachment_blobs'):
                if hashlib.sha256(blob['data']).hexdigest() != blob['hash']:
                    raise AppError('Một tệp đính kèm trong DB bị lỗi.')
        meta = dict(c.execute('SELECT key,value FROM meta'))
        if meta.get('review_copy') == '1':
            raise AppError('Đây là DB bổ sung. Dùng Nhập bổ sung, không thay DB chính bằng file này.')
        return dict(database_id=meta.get('database_id', ''), reports=len(rows),
                    first_day=rows[0]['day'] if rows else '', last_day=rows[-1]['day'] if rows else '',
                    revisions=c.execute('SELECT count(*) FROM revisions').fetchone()[0])


def snapshot(source, dest):
    """Chụp nhất quán cả WAL, kiểm tra rồi mới đổi tên thành .db hoàn chỉnh."""
    source, dest = Path(source).resolve(), Path(dest).resolve()
    if source == dest:
        raise AppError('Không ghi đè DB nguồn.')
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + '.' + secrets.token_hex(4) + '.tmp')
    try:
        with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True, factory=ClosingConnection) as src:
            with sqlite3.connect(str(tmp), factory=ClosingConnection) as target:
                src.backup(target, pages=256)
                target.commit()
        info = inspect_db(tmp)
        # Windows _commit cần descriptor có quyền ghi; rb gây EBADF (Errno 9).
        # Chỉ mở đọc/ghi bản sao tạm, tuyệt đối không đổi quyền mở DB nguồn.
        with tmp.open('r+b') as stream:
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, dest)
        return info
    finally:
        tmp.unlink(missing_ok=True)


class Protection:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.db = self.directory / 'BAO_CAO_CA.db'
        suffix = hashlib.sha256(str(self.directory).encode()).hexdigest()[:10]
        self.config_path = self.directory.parent / ('BAO_VE_DB_' + suffix + '.json')
        self.warning = ''
        # '' = ổn; 'info' = khuyến nghị (chưa chọn ổ dự phòng); 'error' = sao lưu thất bại.
        self.warning_level = ''
        if self.config_path.exists():
            try:
                self.config = json.loads(self.config_path.read_text(encoding='utf-8'))
                if not isinstance(self.config, dict):
                    raise ValueError()
            except Exception as e:
                raise AppError('Cấu hình bảo vệ DB bị lỗi. Giữ nguyên các tệp và khôi phục từ bản sao trước khi chạy tiếp.') from e
        else:
            self.config = {}

    @property
    def local(self):
        # Tách nguồn để chính sách dọn bản cũ không xóa bản của DB trước đó.
        directory = self.directory / 'SAO_LUU_AN_TOAN'
        identity = self.config.get('database_id')
        return directory / identity if identity else directory

    def installed_info(self):
        info = inspect_db(self.db)
        digest = hashlib.sha256()
        with self.db.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        info['sha256'] = digest.hexdigest()
        return info

    def needs_adoption(self):
        if not self.db.exists() or not self.config.get('database_id'):
            return False
        return inspect_db(self.db)['database_id'] != self.config['database_id']

    def accept_installed(self, digest):
        """Chỉ gọi sau xác nhận tiếp nhận DB đã chép vào, không trộn các nguồn."""
        from LUU_TRU import Store
        info = self.installed_info()
        if not secrets.compare_digest(info['sha256'], digest):
            raise AppError('DB đã thay đổi sau khi xem trước. Hãy mở lại bước tiếp nhận.')
        if not self.needs_adoption():
            return None
        stamp = dt.datetime.now(VN).strftime('%Y%m%d_%H%M%S_%f')
        archive = self.directory / 'TRUOC_TIEP_NHAN'
        before = archive / ('DB_TIEP_NHAN_' + stamp + '.db')
        snapshot(self.db, before)
        atomic_json(archive / ('CAU_HINH_CU_' + stamp + '.json'), self.config)
        # DB rất cũ chưa có mã nguồn sẽ được nâng cấp sau khi đã chụp bản gốc.
        incoming = Store(self.db)
        new = dict(self.config)
        new.update(initialized=True, database_id=incoming.meta('database_id'),
                   accepted_at=dt.datetime.now(VN).isoformat(), accepted_snapshot=str(before))
        new.pop('last_local', None)
        new.pop('last_external', None)
        atomic_json(self.config_path, new)
        self.config = new
        return before

    def guard_startup(self):
        evidence = self.config.get('initialized') or self.directory.exists() and any(
            (self.directory / name).exists() for name in
            ('SAO_LUU_TU_DONG', 'SAO_LUU_AN_TOAN', 'SAO_LUU_MANG_DI', 'PHIEN_DANG_CHAY.json'))
        if self.db.exists():
            if not self.db.stat().st_size:
                raise AppError('DB chính rỗng. Không tạo lại DB trắng; hãy chọn bản sao để khôi phục.')
            inspect_db(self.db)
        elif evidence:
            raise AppError('Không tìm thấy BAO_CAO_CA.db của bộ dữ liệu đã dùng. Không tạo DB trắng; hãy khôi phục bản sao.')

    def initialize(self):
        from LUU_TRU import Store
        identity = Store(self.db, readonly=True).meta('database_id')
        if self.config.get('database_id') and identity != self.config['database_id']:
            raise AppError('DB vừa chép vào khác nguồn đã đăng ký. Mở bản 1.8.1 bình thường và xác nhận Tiếp nhận DB đang có; không cần xóa cấu hình hoặc DB.')
        self.config.update(initialized=True, database_id=identity)
        atomic_json(self.config_path, self.config)

    def external(self):
        root = self.config.get('external_directory', '')
        return Path(root) / ('BAO_CAO_CA_' + self.config.get('database_id', 'chua_xac_dinh')) if root else None

    def set_external(self, text):
        if not isinstance(text, str) or not text.strip():
            raise AppError('Chọn một thư mục dự phòng ở ngoài DU_LIEU.')
        path = Path(text.strip()).expanduser()
        if not path.is_absolute() or not path.is_dir():
            raise AppError('Thư mục phải có sẵn, dùng đường dẫn đầy đủ; cắm ổ dự phòng trước khi chọn.')
        path = path.resolve()
        if path == self.directory or self.directory in path.parents:
            raise AppError('Chọn thư mục bên ngoài DU_LIEU để tránh mất chung.')
        probe = path / ('.thu_ghi_' + secrets.token_hex(5))
        try:
            probe.write_bytes(b'OK')
        except OSError as e:
            raise AppError('Không ghi được vào thư mục dự phòng.') from e
        finally:
            probe.unlink(missing_ok=True)
        if self.config.get('external_directory') != str(path):
            self.config.pop('last_external', None)
        self.config['external_directory'] = str(path)
        atomic_json(self.config_path, self.config)

    def prune(self, directory, today=None):
        """30 ngày: bản mới nhất mỗi ngày; hôm nay tối đa 10 bản; lâu hơn giữ cuối mỗi tháng."""
        today = today or dt.datetime.now(VN).date()
        groups = {}
        for path in directory.glob('BAO_CAO_CA_????????_??????_*.db'):
            try:
                day = dt.datetime.strptime(path.name[11:19], '%Y%m%d').date()
            except ValueError:
                continue
            groups.setdefault(day, []).append(path)
        monthly = {}
        keep = set()
        for day, paths in sorted(groups.items()):
            paths.sort()
            monthly[(day.year, day.month)] = paths[-1]
            if day == today:
                keep.update(paths[-10:])
            elif (today - day).days <= 30:
                keep.add(paths[-1])
        keep.update(monthly.values())
        for paths in groups.values():
            for path in paths:
                if path not in keep:
                    path.unlink()

    def backup(self):
        name = 'BAO_CAO_CA_' + dt.datetime.now(VN).strftime('%Y%m%d_%H%M%S_%f') + '_' + secrets.token_hex(3) + '.db'
        path = self.local / name
        snapshot(self.db, path)
        # Không dọn các bản cũ trước khi snapshot mới đã được kiểm tra thành công.
        self.prune(self.local)
        self.config['last_local'] = dict(at=dt.datetime.now(VN).isoformat(), name=name)
        errors = []
        level = ''
        outside = self.external()
        if outside:
            try:
                # Ổ rời mất kết nối: không tự tạo lại đường dẫn gốc.
                if not Path(self.config['external_directory']).is_dir():
                    raise OSError('Thư mục dự phòng chưa sẵn sàng')
                snapshot(path, outside / name)
                self.prune(outside)
                self.config['last_external'] = dict(at=dt.datetime.now(VN).isoformat(), name=name)
            except Exception:
                logging.exception('Sao luu ben ngoai that bai')
                errors.append('Sao lưu tại máy thành công; sao lưu bên ngoài thất bại. Kiểm tra ổ/thư mục dự phòng.')
                level = 'error'
        else:
            errors.append('Chưa chọn nơi dự phòng bên ngoài. Các bản sao hiện chỉ bảo vệ khi mất DB, chưa bảo vệ khi mất cả ổ máy.')
            level = 'info'
        self.warning = ' '.join(errors)
        self.warning_level = level
        atomic_json(self.config_path, self.config)
        return path

    def candidates(self):
        directories = [self.local, self.directory / 'SAO_LUU_AN_TOAN', self.directory / 'SAO_LUU_TU_DONG', self.directory / 'SAO_LUU_MANG_DI']
        if self.external():
            directories.append(self.external())
        rows = []
        self.choices = {}
        for directory in directories:
            if not directory.is_dir():
                continue
            for path in directory.glob('*.db'):
                key = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
                self.choices[key] = path
                stat = path.stat()
                rows.append(dict(id=key, name=path.name, location=str(directory), bytes=stat.st_size,
                                 modified=dt.datetime.fromtimestamp(stat.st_mtime, VN).isoformat()))
        return sorted(rows, key=lambda r: r['modified'], reverse=True)

    def status(self):
        return dict(warning=self.warning, warning_level=self.warning_level, external_directory=self.config.get('external_directory', ''),
                    last_local=self.config.get('last_local'), last_external=self.config.get('last_external'),
                    local_directory=str(self.local), database_exists=self.db.is_file(), backups=self.candidates())

    def selected(self, key):
        self.candidates()
        if key not in self.choices:
            raise AppError('Bản sao không còn tồn tại. Tải lại danh sách.')
        return self.choices[key]

    def preview(self, source):
        result = inspect_db(source)
        expected = self.config.get('database_id')
        if expected and result['database_id'] != expected:
            raise AppError('Bản sao không cùng nguồn với DB của máy này. Dùng đúng bản sao, hoặc mở DB kiểm tra.')
        digest = hashlib.sha256()
        with Path(source).open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        result['sha256'] = digest.hexdigest()
        return result

    def restore(self, source, digest):
        source = Path(source).resolve()
        info = self.preview(source)
        if not secrets.compare_digest(info['sha256'], digest):
            raise AppError('Bản sao đã thay đổi sau khi xem trước; hãy chọn lại.')
        if source == self.db:
            raise AppError('Chọn bản sao, không chọn DB chính.')
        for suffix in ('-wal', '-shm', '-journal'):
            if Path(str(self.db) + suffix).exists():
                raise AppError('DB còn tệp giao dịch. Đóng tất cả ứng dụng dùng DB trước khi khôi phục; giữ nguyên các tệp.')
        self.directory.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(VN).strftime('%Y%m%d_%H%M%S_%f')
        preserved = None
        if self.db.exists():
            preserved = self.directory / 'TRUOC_KHOI_PHUC' / ('DB_CU_' + stamp + '.db')
            preserved.parent.mkdir(parents=True, exist_ok=True)
            # Kể cả DB hỏng cũng giữ nguyên byte để có thể cứu dữ liệu sau này.
            shutil.copy2(self.db, preserved)
        staged = self.directory / ('KHOI_PHUC_' + secrets.token_hex(6) + '.tmp')
        try:
            snapshot(source, staged)
            os.replace(staged, self.db)
        finally:
            staged.unlink(missing_ok=True)
        self.initialize()
        return dict(restored=info, preserved=str(preserved) if preserved else '')



class SessionLock:
    """Khóa cấp hệ điều hành, tự nhả khi tiến trình chết; không khóa bằng file cờ."""
    def __init__(self, directory):
        directory = Path(directory).resolve()
        directory.parent.mkdir(parents=True, exist_ok=True)
        key = hashlib.sha256(str(directory).encode()).hexdigest()[:10]
        self.stream = (directory.parent / ('KHOA_DB_' + key + '.lock')).open('a+b')
        try:
            self.stream.seek(0, 2)
            if self.stream.tell() == 0:
                self.stream.write(b'0'); self.stream.flush()
            self.stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            self.stream.close()
            raise AppError('Một phiên Sổ báo cáo ca đang dùng thư mục này. Hãy Thoát tool trước khi mở phiên khác hoặc khôi phục.') from e

    def close(self):
        if self.stream.closed:
            return
        try:
            self.stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
        finally:
            self.stream.close()


def recovery_dialog(directory, message=''):
    """Được gọi trước khi chạy server: chọn file + xem phạm vi + xác nhận rõ."""
    import tkinter as tk
    from tkinter import filedialog, messagebox
    root = tk.Tk(); root.withdraw()
    lock = None
    try:
        lock = SessionLock(directory)
        protection = Protection(directory)
        if message:
            messagebox.showwarning('Cần khôi phục dữ liệu', message + '\nChọn bản sao DB đã lưu để phục hồi.', parent=root)
        source = filedialog.askopenfilename(parent=root, title='Chọn bản sao Sổ báo cáo ca',
                    initialdir=str(protection.local if protection.local.exists() else Path(directory).parent),
                    filetypes=[('SQLite DB', '*.db'), ('Tất cả', '*.*')])
        if not source:
            return False
        info = protection.preview(source)
        text = f"Bản sao có {info['reports']} ca, từ {info['first_day']} đến {info['last_day']}.\nCác thay đổi sau thời điểm bản sao sẽ không có.\nDB hiện có sẽ được giữ tại TRUOC_KHOI_PHUC.\nKhôi phục bản này?"
        if not messagebox.askyesno('Xác nhận khôi phục', text, parent=root):
            return False
        protection.restore(source, info['sha256'])
        messagebox.showinfo('Đã khôi phục', 'Khôi phục thành công. Có thể mở Sổ báo cáo ca.', parent=root)
        return True
    except Exception as e:
        messagebox.showerror('Chưa khôi phục', str(e), parent=root)
        return False
    finally:
        if lock is not None:
            lock.close()
        root.destroy()


def choose_directory():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk(); root.withdraw()
    try:
        root.attributes('-topmost', True)
        return filedialog.askdirectory(parent=root, title='Chọn thư mục sao lưu bên ngoài DU_LIEU')
    finally:
        root.destroy()


def adoption_dialog(directory):
    """Xác nhận file anh đã chép sẵn vào, thay vì bắt chọn lại bản khôi phục."""
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk(); root.withdraw()
    lock = None
    try:
        lock = SessionLock(directory)
        protection = Protection(directory)
        if not protection.needs_adoption():
            return True
        info = protection.installed_info()
        text = (
            'Phát hiện DB anh đã chép vào từ bộ dữ liệu khác.\n\n'
            + str(protection.db) + '\n'
            + f"Có {info['reports']} báo cáo, {info['revisions']} lần lưu lịch sử.\n"
            + f"Phạm vi: {info['first_day'] or 'chưa có'} → {info['last_day'] or 'chưa có'}.\n\n"
            + 'Dùng DB đang có này làm DB chính?\n'
            + 'Chương trình sao lưu file này và cấu hình trước khi tiếp nhận.\n'
            + 'Không gộp dữ liệu với DB trước. Các bản sao cũ vẫn được giữ.\n'
            + 'Nếu chép nhầm DB, bấm Không và kiểm tra lại file.'
        )
        if not messagebox.askyesno('Tiếp nhận DB đang có', text, parent=root):
            return False
        protection.accept_installed(info['sha256'])
        return True
    except Exception as e:
        messagebox.showerror('Chưa tiếp nhận DB', str(e), parent=root)
        return False
    finally:
        if lock is not None:
            lock.close()
        root.destroy()
