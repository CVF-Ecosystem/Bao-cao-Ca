"""Explicit schema upgrade with pre-upgrade snapshots; never invoked during preview."""
import secrets
import hashlib
import sqlite3
from pathlib import Path
from BAO_VE_DU_LIEU import inspect_db, snapshot, _database_stamp, atomic_json
from LUU_TRU import SCHEMA
from NGHIEP_VU import AppError, ClosingConnection


def plan_upgrade(path):
    path = Path(path).resolve()
    before = _database_stamp(path)
    info = inspect_db(path)
    with sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, factory=ClosingConnection) as c:
        row=c.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        version=row[0] if row else None
    if version not in ('1','2','3') or before != _database_stamp(path):
        raise AppError('Phiên bản DB không hỗ trợ hoặc đã đổi.',409)
    steps=[]
    for number in range(int(version),4):
        name=path.stem+'_TRUOC_NANG_CAP_'+str(number)+'_'+str(number+1)+'.db'
        steps.append(dict(fromSchema=str(number),toSchema=str(number+1),backupName=name))
    return dict(sourceSchema=version,targetSchema='4',databaseId=info['database_id'] or secrets.token_hex(16),
                backupName=steps[-1]['backupName'],migrationSteps=steps,stamp=before,
                sourceDatabaseId=info['database_id'], manifestName='NANG_CAP_'+secrets.token_hex(16)+'.json')


def logical_hash(path):
    digest=hashlib.sha256()
    with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as connection:
        for line in connection.iterdump():
            digest.update(line.encode('utf-8'));digest.update(b'\n')
    return digest.hexdigest()


def file_hash(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def upgrade(path, plan):
    path=Path(path).resolve()
    if _database_stamp(path)!=plan['stamp']:
        raise AppError('DB đã đổi sau xem trước.',409)
    # A prior step's exact logical snapshot may be reused after an explicit restore;
    # any different or unverified existing copy refuses before mutation.
    for step in plan['migrationSteps']:
        existing=path.with_name(step['backupName'])
        if existing.exists() and step['fromSchema']!=plan['sourceSchema']:
            raise AppError('Bản trước nâng cấp tiếp theo đã tồn tại; giữ nguyên và kiểm tra.',409)
    manifest=path.parent/plan['manifestName']
    if manifest.exists(): raise AppError('Biên bản nâng cấp đã tồn tại.',409)
    receipt=dict(schema='local-upgrade-manifest-1',databaseId=plan['databaseId'],sourceDatabaseId=plan['sourceDatabaseId'],sourceSchema=plan['sourceSchema'],steps=[])
    expected_stamp=plan['stamp']
    for step in plan['migrationSteps']:
        if _database_stamp(path)!=expected_stamp: raise AppError('DB đã đổi trước nâng cấp.',409)
        backup=path.with_name(step['backupName'])
        if backup.exists():
            inspect_db(backup)
            if logical_hash(backup)!=logical_hash(path):
                raise AppError('Bản trước nâng cấp đã tồn tại và khác dữ liệu; không ghi đè.',409)
        else:
            snapshot(path,backup)
        info=inspect_db(backup)
        receipt['steps'].append(dict(name=backup.name,sha256=file_hash(backup),sourceSchema=step['fromSchema'],sourceDatabaseId=info['database_id']))
        atomic_json(manifest,receipt)
        if _database_stamp(path)!=expected_stamp: raise AppError('DB đã đổi trong lúc sao lưu; chưa nâng cấp.',409)
        with sqlite3.connect(path.as_uri()+'?mode=rw',uri=True,factory=ClosingConnection) as c:
            c.execute('BEGIN IMMEDIATE')
            if _database_stamp(path)!=expected_stamp: raise AppError('DB đã đổi trước khi ghi.',409)
            row=c.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            if not row or row[0]!=step['fromSchema']:
                raise AppError('Phiên bản DB vừa thay đổi.',409)
            if step['toSchema']=='4':
                cols={r[1] for r in c.execute('PRAGMA table_info(revisions)')}
                for name,typ in (('kind',"TEXT NOT NULL DEFAULT 'legacy'"),('os_user','TEXT'),('auth_user','TEXT')):
                    if name not in cols: c.execute('ALTER TABLE revisions ADD COLUMN '+name+' '+typ)
                for stmt in SCHEMA.split(';'):
                    stmt=stmt.strip()
                    if stmt and not stmt.startswith('INSERT OR IGNORE INTO meta'):
                        c.execute(stmt)
                c.execute("INSERT OR IGNORE INTO meta VALUES('database_id',?)",(plan['databaseId'],))
            c.execute("UPDATE meta SET value=? WHERE key='schema_version'",(step['toSchema'],))
            c.commit()
        expected_stamp=_database_stamp(path)
    info=inspect_db(path)
    if info['database_id'] != plan['databaseId']:
        raise AppError('Không xác minh được danh tính DB sau nâng cấp.')
    return info
