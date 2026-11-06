"""Kiểm thử phá hủy trên thư mục tạm; không sửa dữ liệu thật."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from BAO_VE_DU_LIEU import Protection, inspect_db, snapshot
from LUU_TRU import Store
from NGHIEP_VU import AppError, ClosingConnection

class ProtectionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.data=self.root/'DU_LIEU'
  self.protect=Protection(self.data);self.protect.guard_startup();self.store=Store(self.protect.db);self.protect.initialize()
  self.payload=dict(date='2026-11-04',shift='DAY',status='closed',actor='Người kiểm thử',notes='',staffing=[dict(role='PHỤ TRÁCH CHUNG',people='Trưởng ca')],jobs=[dict(name='TRẢI LÓT PHÁO',detail='',xn=True,rtg=False,f20=None,f40=None,e20=5,e40=2)],handover=[])
  self.store.save(self.payload,0)
 def tearDown(self):self.temp.cleanup()
 def test_restore_deleted_db_and_history(self):
  backup=self.protect.backup();self.payload['notes']='Mới';self.store.save(self.payload,1,'Sửa sau chốt')
  preview=self.protect.preview(backup);self.protect.db.unlink()
  with self.assertRaises(AppError):self.protect.guard_startup()
  self.assertFalse(self.protect.db.exists())
  self.protect.restore(backup,preview['sha256'])
  self.assertEqual(Store(self.protect.db).get('2026-11-04_DAY')['notes'],'')
  self.assertEqual(inspect_db(self.protect.db)['revisions'],1)
 def test_keep_current_before_restore(self):
  backup=self.protect.backup();self.payload['notes']='Giữ lại';self.store.save(self.payload,1,'Sửa')
  result=self.protect.restore(backup,self.protect.preview(backup)['sha256'])
  self.assertEqual(Store(result['preserved'],True).get('2026-11-04_DAY')['notes'],'Giữ lại')
 def test_corrupt_backup_rejected_no_change(self):
  old=self.protect.db.read_bytes();bad=self.root/'bad.db';bad.write_bytes(b'broken')
  with self.assertRaises(Exception):self.protect.preview(bad)
  self.assertEqual(self.protect.db.read_bytes(),old)
 def test_corrupt_main_preserved(self):
  backup=self.protect.backup();p=self.protect.preview(backup);self.protect.db.write_bytes(b'broken')
  result=self.protect.restore(backup,p['sha256']);self.assertEqual(Path(result['preserved']).read_bytes(),b'broken')
  self.assertEqual(inspect_db(self.protect.db)['reports'],1)
 def test_restore_reject_other_origin_and_review(self):
  other=self.root/'other.db';Store(other)
  with self.assertRaises(AppError):self.protect.preview(other)
  backup=self.protect.backup()
  with sqlite3.connect(backup,factory=ClosingConnection) as c:c.execute("insert into meta values('review_copy','1')")
  with self.assertRaises(AppError):self.protect.preview(backup)
 def test_deleted_store_never_recreated_by_read_or_write(self):
  self.protect.db.unlink()
  with self.assertRaises(Exception):self.store.list({})
  with self.assertRaises(Exception):self.store.save(self.payload,1,'Sửa')
  with self.assertRaises(Exception):Store(self.protect.db,True)
  self.assertFalse(self.protect.db.exists())
 def test_deleted_whole_data_dir_still_detected(self):
  import shutil
  shutil.rmtree(self.data)
  with self.assertRaises(AppError):Protection(self.data).guard_startup()
 def test_external_copy_works_and_disconnect_warns(self):
  outside=self.root/'OUTSIDE';outside.mkdir();self.protect.set_external(str(outside));p=self.protect.backup()
  self.assertEqual(inspect_db(self.protect.external()/p.name)['reports'],1)
  self.assertFalse(self.protect.warning)
  old=self.protect.config['last_external'];outside.rename(self.root/'DISCONNECTED');self.protect.backup()
  self.assertIn('thất bại',self.protect.warning);self.assertEqual(self.protect.config['last_external'],old)
 def test_reject_external_inside_data(self):
  for p in (self.data,self.data/'nested'):
   p.mkdir(exist_ok=True)
   with self.assertRaises(AppError):self.protect.set_external(str(p))
 def test_snapshot_uses_wal_and_carries_blob(self):
  data=b'attachment';h=hashlib.sha256(data).hexdigest()
  with sqlite3.connect(self.protect.db,factory=ClosingConnection) as c:
   c.execute('pragma journal_mode=WAL')
   c.execute('insert into attachment_blobs values(?,?,?,?,?)',(h,'image/png',data,'2026','tester'));c.commit()
   target=self.root/'wal_backup.db';snapshot(self.protect.db,target)
   with sqlite3.connect(target,factory=ClosingConnection) as b:self.assertEqual(b.execute('select data from attachment_blobs').fetchone()[0],data)
 def test_backup_failure_keeps_old_snapshots(self):
  p=self.protect.backup()
  with patch('BAO_VE_DU_LIEU.snapshot',side_effect=OSError('disk full')):
   with self.assertRaises(OSError):self.protect.backup()
  self.assertTrue(p.exists());self.assertEqual(inspect_db(p)['reports'],1)
 def test_changed_backup_and_sidecars_rejected(self):
  p=self.protect.backup();preview=self.protect.preview(p)
  with sqlite3.connect(p,factory=ClosingConnection) as c:c.execute("update reports set actor='changed'")
  with self.assertRaises(AppError):self.protect.restore(p,preview['sha256'])
  preview=self.protect.preview(p);Path(str(self.protect.db)+'-wal').write_bytes(b'')
  with self.assertRaises(AppError):self.protect.restore(p,preview['sha256'])
 def test_retention_daily_monthly(self):
  folder=self.root/'retention';folder.mkdir()
  names=['20260131_120000_000001','20260131_130000_000001','20260228_120000_000001','20261001_120000_000001','20261031_120000_000001','20261104_120000_000001','20261104_130000_000001']+[f'20261105_120000_{i:06d}' for i in range(12)]
  for n in names:(folder/('BAO_CAO_CA_'+n+'_abc.db')).touch()
  (folder/'MANUAL.db').touch();self.protect.prune(folder,dt.date(2026,11,5));files=[p.name for p in folder.iterdir()]
  self.assertEqual(len([n for n in files if '20261105' in n]),10)
  self.assertFalse(any('20261001' in n for n in files))
  self.assertFalse(any('20260131_120000' in n for n in files))
  self.assertTrue(any('20260131_130000' in n for n in files));self.assertIn('MANUAL.db',files)
 def test_config_corruption_blocks_startup(self):
  self.protect.config_path.write_text('broken')
  with self.assertRaises(AppError):Protection(self.data)


class HttpProtectionTests(unittest.TestCase):
 def test_restore_api_and_stale_context(self):
  import http.cookiejar, threading, urllib.request, urllib.error
  from MAY_CHU import make_server
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);server=make_server(root/'DU_LIEU');thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));base='http://'+server.app['host']
   def api(path,p=None):
    req=urllib.request.Request(base+path,data=None if p is None else json.dumps(p).encode(),headers={'X-Ca-Request':'1','Content-Type':'application/json'})
    with opener.open(req) as res:return json.load(res)
   try:
    with opener.open(base+'/?launch='+server.app['token']) as res:res.read()
    info=api('/api/info');ctx=info['context'];state=api('/api/protection');self.assertTrue(state['backups'])
    backup_id=state['backups'][0]['id'];preview=api('/api/restore-preview',dict(context=ctx,id=backup_id))
    with self.assertRaises(urllib.error.HTTPError):api('/api/restore',dict(context=ctx,id=backup_id,sha256=preview['sha256']))
    # Mất DB ngay trong phiên: endpoint phục hồi vẫn hoạt động, không sinh DB trắng.
    server.app['main_store'].path.unlink()
    api('/api/restore',dict(context=ctx,id=backup_id,sha256=preview['sha256'],confirmation='KHOI PHUC'))
    new=api('/api/info');self.assertNotEqual(new['context'],ctx)
    with self.assertRaises(urllib.error.HTTPError):api('/api/protection-backup',dict(context=ctx))
    self.assertTrue(api('/api/protection')['database_exists'])
    with opener.open(base+'/tai_nguyen/bao_ve.js') as res:self.assertIn(b'openProtection',res.read())
   finally:server.shutdown();server.server_close();thread.join()

class LockTests(unittest.TestCase):
 def test_single_process_lock_and_release(self):
  from BAO_VE_DU_LIEU import SessionLock
  with tempfile.TemporaryDirectory() as td:
   first=SessionLock(Path(td)/'DU_LIEU')
   try:
    with self.assertRaises(AppError):SessionLock(Path(td)/'DU_LIEU')
   finally:first.close()
   again=SessionLock(Path(td)/'DU_LIEU');again.close()
 def test_server_lock_prevents_second_server(self):
  from MAY_CHU import make_server
  with tempfile.TemporaryDirectory() as td:
   server=make_server(Path(td)/'DU_LIEU')
   try:
    with self.assertRaises(AppError):make_server(Path(td)/'DU_LIEU')
   finally:server.server_close()
   server=make_server(Path(td)/'DU_LIEU');server.server_close()

class BackupScheduleTests(unittest.TestCase):
 def test_draft_throttled_but_close_forced(self):
  from MAY_CHU import daily_backup
  from unittest.mock import Mock
  import time
  store=Mock();store.readonly=False;protection=Mock();protection.warning=''
  app=dict(store=store,main_store=store,protection=protection,backup_tick=time.monotonic())
  daily_backup(app,force=False);protection.backup.assert_not_called()
  daily_backup(app,force=True);protection.backup.assert_called_once()


class AdoptionTests(unittest.TestCase):
 def test_replace_blank_db_with_old_data(self):
  import shutil
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=Protection(root/'DU_LIEU');Store(p.db);p.initialize();previous=p.config['database_id'];old_backup=p.backup()
   source=root/'OLD.db';old=Store(source)
   report=dict(date='2026-11-04',shift='DAY',status='draft',actor='Cũ',staffing=[],jobs=[],handover=[],notes='Dữ liệu cần giữ')
   old.save(report,0);old_id=old.meta('database_id');shutil.copy2(source,p.db)
   self.assertTrue(p.needs_adoption());before=p.installed_info();archived=p.accept_installed(before['sha256'])
   self.assertEqual(p.config['database_id'],old_id);self.assertNotEqual(old_id,previous)
   self.assertTrue(old_backup.exists());self.assertEqual(inspect_db(archived)['reports'],1)
   self.assertEqual(Store(p.db).get('2026-11-04_DAY')['notes'],'Dữ liệu cần giữ')
   self.assertFalse(p.needs_adoption());self.assertNotIn('last_local',p.config)
   new=p.backup();self.assertNotEqual(new.parent,old_backup.parent)
   self.assertTrue(old_backup.exists());self.assertEqual(Protection(p.directory).config['database_id'],old_id)
 def test_no_adoption_does_not_touch_installed_db_or_config(self):
  import shutil
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=Protection(root/'DU_LIEU');Store(p.db);p.initialize();source=root/'OTHER.db';Store(source);shutil.copy2(source,p.db)
   before=p.db.read_bytes();config=p.config_path.read_bytes()
   self.assertTrue(p.needs_adoption());p.installed_info()
   self.assertEqual(before,p.db.read_bytes());self.assertEqual(config,p.config_path.read_bytes())
 def test_adoption_failure_leaves_config_and_db(self):
  import shutil
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);p=Protection(root/'DU_LIEU');Store(p.db);p.initialize();source=root/'OTHER.db';Store(source);shutil.copy2(source,p.db)
   before=p.db.read_bytes();config=p.config_path.read_bytes();digest=p.installed_info()['sha256']
   with patch('BAO_VE_DU_LIEU.snapshot',side_effect=OSError('disk full')):
    with self.assertRaises(OSError):p.accept_installed(digest)
   self.assertEqual(before,p.db.read_bytes());self.assertEqual(config,p.config_path.read_bytes())
   with self.assertRaises(AppError):p.accept_installed('wrong-digest')
 def test_corrupt_and_review_db_not_accepted(self):
  with tempfile.TemporaryDirectory() as td:
   p=Protection(Path(td)/'DU_LIEU');Store(p.db);p.initialize()
   with sqlite3.connect(p.db,factory=ClosingConnection) as c:c.execute("insert into meta values('review_copy','1')")
   with self.assertRaises(AppError):p.installed_info()
   p.db.write_bytes(b'broken')
   with self.assertRaises(Exception):p.installed_info()


class WindowsSyncTests(unittest.TestCase):
 def test_snapshot_fsync_uses_writable_descriptor(self):
  # Mô phỏng yêu cầu handle có quyền ghi của Windows _commit/FlushFileBuffers.
  import os
  original = os.fsync
  def windows_fsync(fd):
   os.write(fd, b'')  # EBADF với handle chỉ đọc; không thay đổi byte nào.
   original(fd)
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/'source.db';Store(source)
   with patch('BAO_VE_DU_LIEU.os.fsync', side_effect=windows_fsync):
    snapshot(source,root/'backup.db')
   self.assertEqual(inspect_db(root/'backup.db')['reports'],0)

if __name__=='__main__':unittest.main()
