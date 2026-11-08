"""Personnel integration tests use only disposable catalogs and synthetic workbooks."""
import base64
import hashlib
import http.cookiejar
import io
import os
import inspect
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from PERSONNEL_XLSX import _library
openpyxl = _library()
from MAY_CHU import make_server
from QUAN_LY_DANH_MUC import PersonnelSaveError, FILES


def fixture():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Personnel'
    ws.append(['MSCĐ', 'Họ và Tên', 'Chức danh', 'Nhóm/Ca'])
    ws.append(['0001', 'Nhân viên giả lập mới', 'Bãi', 'Ca 1'])
    stream = io.BytesIO(); wb.save(stream); wb.close()
    return stream.getvalue()


class PersonnelIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.server = make_server(self.root / 'DU_LIEU')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True); self.thread.start()
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.base = 'http://' + self.server.app['host']
        self.client.open(self.base + '/?launch=' + self.server.app['token']).read()
        self.context = self.server.app['context']
        self.blob = fixture(); self.encoded = base64.b64encode(self.blob).decode()

    def tearDown(self):
        self.server.shutdown(); self.thread.join(); self.server.server_close(); self.tmp.cleanup()

    def post(self, endpoint, obj):
        req = urllib.request.Request(self.base + '/api/personnel-xlsx-' + endpoint, data=json.dumps(obj).encode(),
            headers={'Content-Type':'application/json', 'X-Ca-Request':'1'})
        try:
            with self.client.open(req) as result: return result.status, json.load(result)
        except urllib.error.HTTPError as exc:
            return exc.code, json.load(exc)

    def preview(self):
        return self.post('preview', dict(context=self.context, fileBase64=self.encoded,
            expectedFileSha256=hashlib.sha256(self.blob).hexdigest(), sheet='Personnel', headerRow=1,
            columns=dict(name=2, code=1, title=3, group=4), excludedRows=[]))

    def test_add_preserves_other_bytes_and_replay_noop(self):
        cat=self.server.app['catalogs']
        before={f:(cat.directory/f).read_bytes() for f in FILES.values() if f != FILES['people']}
        status, inspection=self.post('inspect', dict(context=self.context,fileBase64=self.encoded))
        self.assertEqual(status,200); self.assertEqual(inspection['sheets'][0]['name'],'Personnel')
        status, plan=self.preview(); self.assertEqual(status,200); self.assertTrue(plan['canConfirm'])
        status, result=self.post('confirm',dict(context=self.context,nonce=plan['nonce']))
        self.assertEqual(status,200); self.assertEqual(result['added'],1)
        self.assertEqual(before,{f:(cat.directory/f).read_bytes() for f in before})
        self.assertIn('Nhân viên giả lập mới',self.server.app['store'].people())
        self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],409)
        self.assertFalse(self.preview()[1]['canConfirm'])

    def test_stale_expired_cancel_and_context(self):
        cat=self.server.app['catalogs']
        _,plan=self.preview()
        (cat.directory/'NHAN_VIEN.txt').write_text('Bên ngoài\n',encoding='utf-8')
        self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[1]['code'],'STALE')
        cat.sync(); _,plan=self.preview()
        self.server.app['pending_personnel']['expires']=0
        self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],409)
        _,plan=self.preview(); self.post('cancel',dict(context=self.context))
        self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],409)
        self.assertEqual(self.post('inspect',dict(context='wrong',fileBase64=self.encoded))[0],409)

    def test_report_revision_and_noop_do_not_change(self):
        store=self.server.app['store']; cat=self.server.app['catalogs']
        report=dict(date='2026-11-04',shift='DAY',actor='Người thử',status='draft',notes='Giữ nguyên',
            staffing=[dict(role='PHỤ TRÁCH CHUNG',people='Người cũ')],
            jobs=[dict(name='Công việc cũ',detail='',xn=False,rtg=False,f20=1,f40=None,e20=0,e40=None)],handover=[])
        saved=store.save(report,0); old_report=store.get(saved['id']); old_history=store.history(saved['id'])
        _,plan=self.preview(); self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],200)
        before={f:(cat.directory/f).read_bytes() for f in FILES.values()}
        backup_count=len(list((cat.directory/'SAO_LUU').iterdir()))
        _,again=self.preview(); self.assertFalse(again['canConfirm']); self.assertIsNone(again['nonce'])
        self.assertEqual(before,{f:(cat.directory/f).read_bytes() for f in FILES.values()})
        self.assertEqual(backup_count,len(list((cat.directory/'SAO_LUU').iterdir())))
        self.assertEqual(store.get(saved['id']),old_report); self.assertEqual(store.history(saved['id']),old_history)

    def test_inactive_refusal_no_write(self):
        cat=self.server.app['catalogs']; before=cat.raw_digest()
        with self.server.app['store'].connect() as conn: conn.execute('UPDATE people SET active=0 WHERE rowid=(SELECT min(rowid) FROM people)')
        status, result=self.preview(); self.assertEqual((status,result['code']),(409,'CATALOG_UNSAFE'))
        self.assertEqual(cat.raw_digest(),before)

    def test_invalid_preview_clears_nonce_and_bad_index(self):
        _, plan = self.preview()
        req = urllib.request.Request(self.base+'/api/personnel-xlsx-preview',
            data=b'{"context":"x","context":"y"}', headers={'Content-Type':'application/json','X-Ca-Request':'1'})
        with self.assertRaises(urllib.error.HTTPError) as exc: self.client.open(req)
        self.assertEqual(exc.exception.code,400)
        self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],409)
        request=dict(context=self.context,fileBase64=self.encoded,expectedFileSha256=hashlib.sha256(self.blob).hexdigest(),
            sheet='Personnel',headerRow=True,columns=dict(name=2,code=1,title=3,group=4),excludedRows=[])
        self.assertEqual(self.post('preview',request)[0],400)

    def test_backup_failure_has_no_mutation(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest(); original=Path.write_bytes
        def deny(path, data):
            if 'SAO_LUU' in path.parts: raise PermissionError('simulated')
            return original(path,data)
        with patch.object(Path,'write_bytes',deny):
            with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
        self.assertEqual(exc.exception.code,'SAVE_FAILED'); self.assertEqual(cat.raw_digest(),digest)

    def test_restore_failure_reports_backup(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest()
        with patch.object(cat,'sync',side_effect=OSError('simulated')):
            with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
        self.assertEqual(exc.exception.code,'RECOVERY_REQUIRED')
        self.assertTrue((cat.directory/'SAO_LUU'/exc.exception.backup_id/'NHAN_VIEN.txt').exists())

    def test_failed_save_consumes_nonce(self):
        _,plan=self.preview()
        with patch.object(self.server.app['catalogs'],'add_personnel',side_effect=PersonnelSaveError('failure','SAVE_FAILED',500)):
            self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],500)
        self.assertEqual(self.post('confirm',dict(context=self.context,nonce=plan['nonce']))[0],409)

    def test_owner_sync_failure_restores(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest(); original=cat.sync
        calls=[]
        def fail_once():
            calls.append(1)
            if len(calls)==1: raise OSError('simulated disk failure')
            return original()
        with patch.object(cat,'sync',side_effect=fail_once):
            with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
        self.assertEqual(exc.exception.code,'SAVE_FAILED'); self.assertEqual(cat.raw_digest(),digest)
        self.assertTrue((cat.directory/'SAO_LUU'/exc.exception.backup_id/'NHAN_VIEN.txt').exists())

    def test_external_edit_during_failure_is_not_overwritten(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest()
        def conflict():
            (cat.directory/'NHAN_VIEN.txt').write_text('Sửa bên ngoài\n',encoding='utf-8')
            raise OSError('simulated sync failure')
        with patch.object(cat,'sync',side_effect=conflict):
            with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
        self.assertEqual(exc.exception.code,'RECOVERY_REQUIRED')
        self.assertEqual((cat.directory/'NHAN_VIEN.txt').read_text(encoding='utf-8'),'Sửa bên ngoài\n')

    def test_backup_original_read_and_verification_fail_closed(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest(); original=Path.read_bytes
        for mode in ('original','verify'):
            def read(path):
                if path.name == 'NHAN_VIEN.txt' and (('SAO_LUU' in path.parts) == (mode=='verify')):
                    if inspect.currentframe().f_back.f_code.co_name == 'add_personnel':
                        raise PermissionError('injected backup read')
                return original(path)
            with self.subTest(mode=mode), patch.object(Path,'read_bytes',read):
                with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
                self.assertEqual(exc.exception.code,'SAVE_FAILED')
            self.assertEqual(cat.raw_digest(),digest)
            self.assertNotIn('Nhân viên giả lập mới',self.server.app['store'].people())

    def test_temp_write_fsync_and_replace_failures(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest(); original_open=Path.open; original_replace=os.replace
        for mode in ('temp-write','fsync','replace'):
            def deny_open(path,*args,**kwargs):
                if str(path).endswith('.personnel.tmp'): raise PermissionError('temp open')
                return original_open(path,*args,**kwargs)
            def deny_replace(src,dst):
                if str(src).endswith('.personnel.tmp'): raise PermissionError('replace')
                return original_replace(src,dst)
            target = patch.object(Path,'open',deny_open) if mode=='temp-write' else (patch('QUAN_LY_DANH_MUC.os.fsync',side_effect=OSError('fsync')) if mode=='fsync' else patch('QUAN_LY_DANH_MUC.os.replace',side_effect=deny_replace))
            with self.subTest(mode=mode), target:
                with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
                self.assertEqual(exc.exception.code,'SAVE_FAILED')
                backup=cat.directory/'SAO_LUU'/exc.exception.backup_id
                self.assertEqual((backup/'NHAN_VIEN.txt').read_bytes(),(cat.directory/'NHAN_VIEN.txt').read_bytes())
            self.assertEqual(cat.raw_digest(),digest)
            self.assertNotIn('Nhân viên giả lập mới',self.server.app['store'].people())

    def test_real_sqlite_failure_and_postverify_rollback(self):
        cat=self.server.app['catalogs']; store=self.server.app['store']; digest=cat.raw_digest()
        with store.connect() as conn:
            conn.execute("CREATE TRIGGER stop_personnel BEFORE DELETE ON people BEGIN SELECT RAISE(ABORT,'injected'); END")
        with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
        self.assertEqual(exc.exception.code,'SAVE_FAILED'); self.assertEqual(cat.raw_digest(),digest)
        self.assertTrue((cat.directory/'SAO_LUU'/exc.exception.backup_id/'NHAN_VIEN.txt').exists())
        with store.connect() as conn: conn.execute('DROP TRIGGER stop_personnel')
        original=cat.personnel_safe_snapshot; calls=[]
        def verify(value):
            calls.append(value)
            if len(calls)==4: raise RuntimeError('injected postverify')
            return original(value)
        with patch.object(cat,'personnel_safe_snapshot',side_effect=verify):
            with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
        self.assertEqual(exc.exception.code,'SAVE_FAILED');self.assertEqual(cat.raw_digest(),digest)
        self.assertNotIn('Nhân viên giả lập mới',store.people())

    def test_restore_write_and_replace_failures_keep_backup(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest(); write=Path.write_bytes; replace=os.replace
        for mode in ('restore-write','restore-replace'):
            def deny_write(path,data):
                if str(path).endswith('.personnel.restore.tmp'): raise PermissionError('restore write')
                return write(path,data)
            def deny_replace(src,dst):
                if str(src).endswith('.personnel.restore.tmp'): raise PermissionError('restore replace')
                return replace(src,dst)
            fault=patch.object(Path,'write_bytes',deny_write) if mode=='restore-write' else patch('QUAN_LY_DANH_MUC.os.replace',side_effect=deny_replace)
            with self.subTest(mode=mode), patch.object(cat,'sync',side_effect=OSError('sync')), fault:
                with self.assertRaises(PersonnelSaveError) as exc: cat.add_personnel(['Nhân viên giả lập mới'],digest)
            self.assertEqual(exc.exception.code,'RECOVERY_REQUIRED')
            backup=cat.directory/'SAO_LUU'/exc.exception.backup_id/'NHAN_VIEN.txt'
            self.assertTrue(backup.is_file()); self.assertIn('Nhân viên giả lập mới',(cat.directory/'NHAN_VIEN.txt').read_text(encoding='utf-8'))
            (cat.directory/'NHAN_VIEN.txt').write_bytes(backup.read_bytes());cat.sync()
            self.assertEqual(cat.raw_digest(),digest)

    def test_http_auth_header_origin_viewer_review_copy(self):
        body=json.dumps(dict(context=self.context,fileBase64=self.encoded)).encode()
        path=self.base+'/api/personnel-xlsx-inspect'
        for client,headers in [(urllib.request.build_opener(),{'X-Ca-Request':'1'}),
                               (self.client,{}),(self.client,{'X-Ca-Request':'1','Origin':'http://invalid.example'})]:
            req=urllib.request.Request(path,data=body,headers={'Content-Type':'application/json',**headers})
            with self.assertRaises(urllib.error.HTTPError) as exc: client.open(req)
            self.assertEqual(exc.exception.code,403)
        with self.server.app['store'].connect() as conn:
            conn.execute("INSERT OR REPLACE INTO meta VALUES('review_copy','1')")
        self.assertEqual(self.post('inspect',dict(context=self.context,fileBase64=self.encoded))[0],409)
        with self.server.app['store'].connect() as conn: conn.execute("DELETE FROM meta WHERE key='review_copy'")
        req=urllib.request.Request(self.base+'/api/backup',data=json.dumps(dict(context=self.context)).encode(),headers={'X-Ca-Request':'1'})
        blob=self.client.open(req).read()
        req=urllib.request.Request(self.base+'/api/open-viewer',data=blob,headers={'X-Ca-Request':'1'})
        self.client.open(req).read()
        self.assertEqual(self.post('inspect',dict(context=self.server.app['context'],fileBase64=self.encoded))[0],409)

    def test_db_precondition_rechecked_immediately_before_replace(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest()
        def deactivate(_):
            with self.server.app['store'].connect() as conn:
                conn.execute('UPDATE people SET active=0 WHERE rowid=(SELECT min(rowid) FROM people)')
        with patch('QUAN_LY_DANH_MUC.os.fsync', side_effect=deactivate):
            with self.assertRaises(PersonnelSaveError) as exc:
                cat.add_personnel(['Nhân viên giả lập mới'], digest)
        self.assertEqual(exc.exception.code, 'CATALOG_UNSAFE')
        self.assertEqual(cat.raw_digest(), digest)
        with self.server.app['store'].connect() as conn:
            self.assertEqual(conn.execute('SELECT count(*) FROM people WHERE active=0').fetchone()[0], 1)

    def test_owner_refuses_a_name_that_catalog_parsing_would_split(self):
        cat=self.server.app['catalogs']; digest=cat.raw_digest()
        with self.assertRaises(PersonnelSaveError):
            cat.add_personnel(['Alpha\u2028Beta'], digest)
        self.assertEqual(cat.raw_digest(), digest)


if __name__=='__main__': unittest.main(verbosity=2)
