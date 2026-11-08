"""Explicit local maintenance; all destructive selection remains server-owned."""
import datetime as dt
import json
import hashlib
import re
import secrets
import sqlite3
import tempfile
import itertools
from pathlib import Path
from BAO_VE_DU_LIEU import inspect_db, snapshot, atomic_json
from NGHIEP_VU import AppError, ClosingConnection
from THIET_LAP import VN


class MaintenanceError(Exception):
    def __init__(self, message, completed, retained):
        super().__init__(message)
        self.completed, self.retained = completed, retained


def stamp(path):
    stat=path.lstat()
    if path.is_symlink() or getattr(stat,'st_file_attributes',0) & 0x400 or not path.is_file():
        raise AppError('Tệp bảo trì không an toàn.',409)
    return (stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)


def referenced(conn):
    hashes=set()
    for table in ('reports','revisions','correction_base'):
        for row in conn.execute('SELECT payload FROM '+table):
            obj=json.loads(row[0])
            if not isinstance(obj,dict): raise AppError('Nội dung DB không hợp lệ; chưa dọn.')
            attachments=obj.get('attachments',[])
            if not isinstance(attachments,list): raise AppError('Tham chiếu tệp không hợp lệ; chưa dọn.')
            for attachment in attachments:
                if not isinstance(attachment,dict) or not re.fullmatch('[a-f0-9]{64}',str(attachment.get('hash',''))):
                    raise AppError('Tham chiếu tệp không hợp lệ; chưa dọn.')
                hashes.add(attachment['hash'])
    return hashes


def file_hash(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024),b''):
            digest.update(block)
    return digest.hexdigest()


def register_viewer(path):
    path=Path(path)
    root=path.parent
    if root.is_symlink() or getattr(root.lstat(),'st_file_attributes',0) & 0x400:
        raise AppError('Thư mục DB kiểm tra không an toàn.')
    before=stamp(path); digest=file_hash(path)
    if stamp(path)!=before: raise AppError('Tệp đã thay đổi trong lúc ghi nhận.',409)
    index=root/'VIEWER_CUSTODY.json'
    if index.is_symlink(): raise AppError('Dữ liệu nhận diện bản xem không an toàn.')
    try:
        values=json.loads(index.read_text(encoding='utf-8')) if index.exists() else {}
        if not isinstance(values,dict): raise ValueError()
    except (OSError,ValueError,TypeError):
        raise AppError('Dữ liệu nhận diện bản xem không hợp lệ.')
    if len(values)>=10000 and path.name not in values: raise AppError('Danh sách bản xem quá lớn.')
    values[path.name]=digest
    atomic_json(index,values)


def viewer_candidates(app):
    root=app['data_dir']/'DB_KIEM_TRA'
    if not root.is_dir() or root.is_symlink() or getattr(root.lstat(),'st_file_attributes',0) & 0x400: return []
    index=root/'VIEWER_CUSTODY.json'
    try:
        if index.is_symlink(): return []
        if index.stat().st_size>1024*1024: return []
        custody=json.loads(index.read_text(encoding='utf-8'))
        if not isinstance(custody,dict): return []
    except (OSError,ValueError,TypeError): return []
    result=[]; now=dt.datetime.now(dt.timezone.utc).timestamp()
    pending=app.get('pending_import') or {}
    pending_path=getattr(pending.get('source'),'path',None)
    active=getattr(app.get('store'),'path',None)
    candidates=list(itertools.islice(root.glob('ban_sao_*.db'),501))
    if len(candidates)>500: raise AppError('Quá nhiều bản xem; chưa dọn.')
    for path in sorted(candidates):
        try:
            if not re.fullmatch(r'ban_sao_[0-9a-f]{16}\.db',path.name): continue
            identity=stamp(path)
            if path.resolve().parent!=root.resolve() or path.resolve() in (pending_path,active): continue
            if now-identity[3]/1e9 < 30*86400: continue
            if custody.get(path.name)!=file_hash(path) or stamp(path)!=identity: continue
            with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as conn:
                row=conn.execute("SELECT value FROM meta WHERE key='review_copy'").fetchone()
                if row and row[0]=='1': continue
                if conn.execute('PRAGMA quick_check').fetchone()[0]!='ok': continue
                version=conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                if not version or version[0] not in ('1','2','3','4'): continue
            result.append((path,identity))
        except (OSError,sqlite3.Error,ValueError):
            continue
    return result


def old_orphans(conn):
    refs=referenced(conn); result=[]; cutoff=dt.datetime.now(VN)-dt.timedelta(hours=24)
    for digest,at in conn.execute('SELECT hash,uploaded_at FROM attachment_blobs'):
        try:
            moment=dt.datetime.fromisoformat(at)
            if moment.tzinfo is None: continue
            if digest not in refs and moment<=cutoff:
                result.append(digest)
                if len(result)>500: raise AppError('Quá nhiều tệp cần xem xét; chưa dọn.')
        except (ValueError,TypeError):
            continue
    return sorted(result)


def preview(app,kind):
    if kind=='viewer_cleanup':
        values=viewer_candidates(app)
        items=[dict(id=secrets.token_hex(8),label=path.name,eligible=True,reason='Bản chỉ xem quá 30 ngày') for path,_ in values]
    elif kind=='orphan_blobs':
        with app['main_store'].connect() as c: values=old_orphans(c)
        items=[dict(id=secrets.token_hex(8),label='Tệp không tham chiếu '+str(i+1),eligible=True,reason='Quá 24 giờ') for i,_ in enumerate(values)]
    elif kind=='restore_drill':
        values=['drill'];items=[dict(id=secrets.token_hex(8),label='Khôi phục thử trong thư mục tạm',eligible=True,reason='Không thay DB chính')]
    else: raise AppError('Loại bảo trì không hợp lệ.')
    return items,values


def confirm(app,kind,values):
    protection=app['protection']; store=app['main_store']
    if kind=='viewer_cleanup':
        backup=protection.backup(level='full')
        if not backup or protection.warning_level=='error': raise AppError('Sao lưu đầy đủ thất bại; chưa dọn.')
        current=dict(viewer_candidates(app)); done=0
        for path,identity in values:
            try:
                if current.get(path)!=identity or stamp(path)!=identity:
                    raise OSError('changed')
                path.unlink();done+=1
            except OSError as exc:
                raise MaintenanceError('Đã dừng dọn do tệp thay đổi hoặc lỗi ghi.',done,len(values)-done) from exc
        return dict(kind=kind,completed=done,retained=0,message='Đã dọn các bản chỉ xem đủ điều kiện.')
    if kind=='orphan_blobs':
        with store.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            actual=old_orphans(c)
            if actual!=values: raise AppError('Danh sách tệp đã đổi; xem trước lại.',409)
            backup=protection.backup(level='full')
            if not backup or protection.warning_level=='error': raise AppError('Sao lưu đầy đủ thất bại; chưa dọn.')
            check=inspect_db(backup)
            if check['database_id']!=store.meta('database_id'): raise AppError('Bản sao khác nguồn; chưa dọn.')
            if old_orphans(c)!=values: raise AppError('Nguồn đã đổi; chưa dọn.',409)
            c.executemany('DELETE FROM attachment_blobs WHERE hash=?',[(x,) for x in values])
        return dict(kind=kind,completed=len(values),retained=0,message='Đã dọn trong DB; dung lượng tệp trên ổ chưa chắc giảm.')
    if kind=='restore_drill':
        backup=protection.backup(level='full')
        if not backup or protection.warning_level=='error': raise AppError('Không có bản sao đầy đủ để thử khôi phục.')
        with tempfile.TemporaryDirectory(prefix='kiem_tra_khoi_phuc_') as directory:
            target=Path(directory)/'RESTORE.db'; source_info=inspect_db(backup); snapshot(backup,target); result=inspect_db(target)
            if any(result[k]!=source_info[k] for k in ('database_id','reports','revisions','verified_hashes')):
                raise AppError('Khôi phục thử không khớp bản sao.')
            with sqlite3.connect(backup.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as original, sqlite3.connect(target.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as restored:
                for table in ('reports','revisions','correction_base'):
                    if original.execute('SELECT payload FROM '+table+' ORDER BY rowid LIMIT 1').fetchone()!=restored.execute('SELECT payload FROM '+table+' ORDER BY rowid LIMIT 1').fetchone():
                        raise AppError('Nội dung kiểm tra khôi phục không khớp.')
        updated=dict(protection.config)
        updated['last_restore_drill']=dt.datetime.now(VN).isoformat()
        atomic_json(protection.config_path,updated);protection.config=updated
        return dict(kind=kind,completed=1,retained=0,message='Đã kiểm tra khôi phục trong thư mục tạm.')
    raise AppError('Loại bảo trì không hợp lệ.')
