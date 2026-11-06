# -*- coding: utf-8 -*-
"""Kiểm thử nghiệp vụ và DB; không chạm dữ liệu thật."""
import copy
import datetime as dt
import io
import json
from pathlib import Path
import tempfile
import threading
import urllib.request
import urllib.error
import http.cookiejar
import base64
import unittest
import zipfile
import xml.etree.ElementTree as ET
import sqlite3
import urllib.parse
from BAO_CAO_CA import running_session
from BAO_CAO_EXCEL import aggregate, monthly_tables, report_table, styled_xlsx, xlsx_bytes
from LUU_TRU import Store
from MAY_CHU import make_server
from NGHIEP_VU import AppError, ClosingConnection, file_type, normalize, suggest
from THIET_LAP import ASSETS, JOBS, MAX_FILE, PEOPLE, ROLES, SHIPS


class Tests(unittest.TestCase):
    PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aC1sAAAAASUVORK5CYII=')
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root/'main.db')
        self.p = dict(date='2026-11-02', shift='NIGHT', status='draft', actor='Người nhập thử', notes='',
                      staffing=[dict(role='PHỤ TRÁCH CHUNG', people='Trưởng ca')],
                      jobs=[dict(name='DỜI CẤP RỖNG', detail='Thử nghiệm', xn=True, rtg=False,
                                 f20=None, f40=None, e20=3, e40=2)], handover=[dict(text='Kiểm tra lại', done=False)])

    def tearDown(self):
        self.temp.cleanup()

    def test_shift_boundaries(self):
        for hour,minute,day,shift in [(0,0,'2026-11-01','NIGHT'),(5,59,'2026-11-01','NIGHT'),
                                    (6,0,'2026-11-02','DAY'),(17,59,'2026-11-02','DAY'),(18,0,'2026-11-02','NIGHT')]:
            self.assertEqual(suggest(dt.datetime(2026,11,2,hour,minute)),dict(date=day,shift=shift))
        self.assertEqual(suggest(dt.datetime(2027,1,1,2)),dict(date='2026-12-31',shift='NIGHT'))

    def test_save_duplicate_conflict_and_blank_zero(self):
        r = self.store.save(self.p,0)
        self.assertEqual(r['version'],1)
        with self.assertRaises(AppError) as ctx:
            self.store.save(self.p,0)
        self.assertEqual(ctx.exception.status,409)
        self.assertEqual(len(self.store.list({})),1)
        self.p['jobs'][0]['f20']=0
        r=self.store.save(self.p,1)
        self.assertEqual(r['jobs'][0]['f20'],0)
        self.assertIsNone(r['jobs'][0]['f40'])
        self.assertEqual(len(self.store.history(r['id'])),2)

    def test_close_and_revision_reason(self):
        self.store.save(self.p,0)
        self.p['status']='closed'
        self.store.save(self.p,1,'Chốt ca')
        self.p['notes']='Sửa bổ sung'
        with self.assertRaises(AppError):self.store.save(self.p,2)
        r=self.store.save(self.p,2,'Bổ sung bàn giao')
        h=self.store.history(r['id'])
        self.assertEqual(h[0]['reason'],'Bổ sung bàn giao')
        self.assertEqual(h[1]['payload']['notes'],'')
        self.assertEqual(r['version'],3)

    def test_invalid_counts_and_chief(self):
        for v in [-1,1.2,True,'=1+2','1e3',10000000]:
            p=copy.deepcopy(self.p);p['jobs'][0]['e20']=v
            with self.assertRaises(AppError):self.store.save(p,0)
        p=copy.deepcopy(self.p);p['status']='closed';p['staffing']=[]
        with self.assertRaises(AppError):self.store.save(p,0)

    def test_consistent_backup_readonly_and_snapshot(self):
        r=self.store.save(self.p,0)
        path=self.store.backup(self.root/'copy.db')
        before=path.read_bytes(); view=Store(path,True)
        with self.assertRaises(AppError):view.save(self.p,1)
        self.assertEqual(view.get(r['id'])['jobs'][0]['e20'],3)
        self.p['jobs'][0]['e20']=7;self.store.save(self.p,1)
        self.assertEqual(view.get(r['id'])['jobs'][0]['e20'],3)
        self.assertEqual(path.read_bytes(),before)
        self.assertEqual(len(view.history(r['id'])),1)

    def test_filters_totals_and_export(self):
        self.store.save(self.p,0)
        p=copy.deepcopy(self.p);p['date']='2026-11-03';p['status']='closed'
        p['jobs'][0]['e20']=8;self.store.save(p,0)
        rows=self.store.list({'status':'closed','from':'2026-11-03','q':'Thử nghiệm'})
        self.assertEqual(len(rows),1)
        self.assertEqual(aggregate(rows)[0]['e20'],8)
        output=xlsx_bytes([('Bao cao',report_table(rows[0]))])
        with zipfile.ZipFile(io.BytesIO(output)) as z:
            for name in z.namelist():ET.fromstring(z.read(name))
            sheet=z.read('xl/worksheets/sheet1.xml').decode()
            self.assertIn('<v>8</v>',sheet)
        output=xlsx_bytes([('Text',[['=1+2','<script>','ký tự Việt']])])
        with zipfile.ZipFile(io.BytesIO(output)) as z:
            sheet=z.read('xl/worksheets/sheet1.xml').decode()
            self.assertNotIn('<f>',sheet)
            self.assertIn('&lt;script&gt;',sheet)

    def test_wrong_db_rejected(self):
        p=self.root/'wrong.db';p.write_bytes(b'not a database')
        with self.assertRaises(AppError):Store(p,True)

    def test_edit_names_after_reopen_draft_and_multiple_ships(self):
        r=self.store.save(self.p,0)
        reopened=Store(self.store.path)
        edit=reopened.get(r['id'])
        edit['staffing'][0]['people']='Giáp Hoàng Duy; Vũ Thanh Phong'
        edit['staffing'][0]['ships']=SHIPS[:3]
        edit['ships']=SHIPS[:3]
        edit['jobs'][0]['ships']=SHIPS[:2]
        saved=reopened.save(edit,edit['version'])
        self.assertEqual(saved['staffing'][0]['people'],'Giáp Hoàng Duy; Vũ Thanh Phong')
        self.assertEqual(saved['staffing'][0]['ships'],SHIPS[:3])
        self.assertEqual(aggregate([saved])[0]['e20'],3)
        copy_db=reopened.backup(self.root/'reopened_copy.db')
        self.assertEqual(Store(copy_db,True).get(r['id'])['ships'],SHIPS[:3])

    def test_khb_default_position_saved_and_exported(self):
        self.assertIn('KHB (KẾ HOẠCH BÃI)',ROLES)
        p=copy.deepcopy(self.p)
        p['staffing'].append(dict(role='KHB (KẾ HOẠCH BÃI)',people='Người kế hoạch bãi'))
        r=self.store.save(p,0)
        self.assertEqual(Store(self.store.path).get(r['id'])['staffing'][-1]['people'],'Người kế hoạch bãi')
        data=styled_xlsx([('Bao cao ca',report_table(r))],{'Bao cao ca':r})
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            text=' '.join(ET.fromstring(z.read('xl/worksheets/sheet1.xml')).itertext())
            self.assertIn('KHB (KẾ HOẠCH BÃI)',text)
            self.assertIn('Người kế hoạch bãi',text)

    def test_new_ship_directory_persists_and_merges(self):
        r=self.store.save(self.p,0)
        self.assertEqual(self.store.ships(),SHIPS)
        self.store.add_ship('  TAU   MOI  ')
        self.store.add_ship('tau moi')
        self.assertEqual(Store(self.store.path).ships().count('TAU MOI'),1)
        review=self.review_copy();review.add_ship('TAU BO SUNG')
        edit=copy.deepcopy(self.p);edit['ships']=['TAU BO SUNG'];review.save(edit,1,'Thêm tàu cho ca cũ')
        self.store.apply_corrections(review,[r['id']])
        self.assertIn('TAU BO SUNG',self.store.ships())
        with self.assertRaises(AppError):Store(review.path,True).add_ship('ABC')
        edit['ships']='TAU MOI'
        with self.assertRaises(AppError):normalize(edit)

    def test_month_export_full_calendar_and_template_style(self):
        self.store.save(self.p,0)
        p=copy.deepcopy(self.p);p['date']='2026-11-02';p['shift']='DAY';p['status']='closed';p['ships']=SHIPS[:2]
        self.store.save(p,0)
        other=copy.deepcopy(self.p);other['date']='2026-12-01';self.store.save(other,0)
        tables=monthly_tables(self.store,'2026-11')
        self.assertEqual([t[0] for t in tables],['Tong_hop_thang','02-11_Ngay','02-11_Dem'])
        calendar_rows=[row for row in tables[0][1] if row and isinstance(row[0],str) and row[0].startswith('2026-11-')]
        self.assertEqual(len(calendar_rows),60)
        self.assertEqual(sum(row[2]=='Chưa có báo cáo' for row in calendar_rows),58)
        reports={tables[1][0]:self.store.get('2026-11-02_DAY'),tables[2][0]:self.store.get('2026-11-02_NIGHT')}
        output=styled_xlsx(tables,reports)
        n={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        with zipfile.ZipFile(io.BytesIO(output)) as z,zipfile.ZipFile(ASSETS/'mau'/'MAU_BAO_CAO.xlsx') as original:
            for f in z.namelist():ET.fromstring(z.read(f))
            styles=ET.fromstring(z.read('xl/styles.xml'));old=ET.fromstring(original.read('xl/styles.xml'))
            for new_style,old_style in zip(styles.find('m:cellXfs',n),old.find('m:cellXfs',n)):
                self.assertEqual(ET.tostring(new_style),ET.tostring(old_style))
            sheet=ET.fromstring(z.read('xl/worksheets/sheet2.xml'));template=ET.fromstring(original.read('xl/worksheets/sheet1.xml'))
            self.assertEqual(ET.tostring(sheet.find('m:cols',n)),ET.tostring(template.find('m:cols',n)))
            cell=sheet.find('.//m:c[@r="B4"]',n)
            self.assertIsNone(cell.get('t'));self.assertEqual(int(cell.find('m:v',n).text),46328)
            self.assertEqual(len(sheet.findall('.//m:f',n)),4)
        for month,days in [('2028-02',29),('2026-02',28),('2026-10',31)]:
            rows=monthly_tables(self.store,month)[0][1]
            self.assertEqual(sum(bool(row) and isinstance(row[0],str) and row[0].startswith(month+'-') for row in rows),days*2)
        with self.assertRaises(AppError):monthly_tables(self.store,'2026-13')

    def test_dynamic_template_keeps_all_long_names_jobs_and_notes(self):
        p=copy.deepcopy(self.p)
        p['staffing']=[dict(role='Vị trí '+str(i),people='; '.join(PEOPLE[:4]),ships=SHIPS[:3]) for i in range(15)]
        p['jobs']=[dict(name=name,detail='Chi tiết '+str(i),xn=False,rtg=False,f20=i,f40=0,e20=None,e40=None,ships=SHIPS[:3]) for i,name in enumerate(JOBS)]
        p['notes']='\n'.join('Bàn giao dài '+str(i) for i in range(80))
        r=self.store.save(p,0)
        data=styled_xlsx([('Bao cao ca',report_table(r))],{'Bao cao ca':r})
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            n={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            alltext=' '.join(root.itertext())
            self.assertIn('Vị trí 14',alltext);self.assertIn('Bàn giao dài 79',alltext)
            for ship in SHIPS[:3]:self.assertIn(ship,alltext)
            for name in JOBS:self.assertIn(name,alltext)
            self.assertNotIn('TRẢI ĐÓNG HÀNG',alltext)
            merges=[m.get('ref') for m in root.findall('m:mergeCells/m:mergeCell',n)]
            self.assertEqual(len(merges),len(set(merges)))
            self.assertTrue(any(float(row.get('ht','15'))>21 for row in root.findall('m:sheetData/m:row',n)))

    def test_http_ship_directory_and_month_export(self):
        server=make_server(self.root/'http_month')
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://'+server.app['host']
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        try:
            opener.open(base+'/?launch='+server.app['token']).read()
            ctx=json.loads(opener.open(base+'/api/info').read())['context']
            body=json.dumps(dict(name='TAU MOI KIEM THU',context=ctx)).encode()
            result=json.loads(opener.open(urllib.request.Request(base+'/api/ships-add',data=body,headers={'X-Ca-Request':'1'})).read())
            self.assertIn('TAU MOI KIEM THU',result['ships'])
            p=copy.deepcopy(self.p);p['ships']=['TAU MOI KIEM THU']
            server.app['store'].save(p,0)
            path='/api/export-month?'+urllib.parse.urlencode(dict(month='2026-11',context=ctx))
            result=opener.open(base+path)
            self.assertIn('2026-11.xlsx',result.headers['Content-Disposition'])
            with zipfile.ZipFile(io.BytesIO(result.read())) as z:
                n={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                wb=ET.fromstring(z.read('xl/workbook.xml'))
                self.assertEqual(len(wb.findall('m:sheets/m:sheet',n)),2)
                self.assertIn('TAU MOI KIEM THU',' '.join(ET.fromstring(z.read('xl/worksheets/sheet2.xml')).itertext()))
            with self.assertRaises(urllib.error.HTTPError) as e:
                opener.open(base+'/api/export-month?month=2026-99&context='+ctx)
            self.assertEqual(e.exception.code,400)
        finally:
            server.shutdown();thread.join();server.server_close()

    def test_attachments_backup_and_revision_removal(self):
        a=self.store.upload_attachment(self.PNG,'ảnh hiện trường.jpg','Trưởng ca')
        self.assertTrue(a['name'].endswith('.jpg'))  # original name is retained
        a['caption']='Hiện trường khu C'
        self.p['attachments']=[a]
        r=self.store.save(self.p,0)
        self.assertEqual(r['attachments'][0]['caption'],'Hiện trường khu C')
        p=self.store.backup(self.root/'with_images.db');view=Store(p,True)
        self.assertEqual(view.attachment(a['hash'])['data'],self.PNG)
        self.p['attachments']=[];self.store.save(self.p,1,'Gỡ nhầm ảnh')
        self.assertFalse(self.store.get(r['id']).get('attachments'))
        self.assertEqual(self.store.history(r['id'])[1]['payload']['attachments'][0]['hash'],a['hash'])
        self.assertEqual(self.store.attachment(a['hash'])['data'],self.PNG)
        with self.assertRaises(AppError):view.upload_attachment(self.PNG,'a.png','Anh')

    def test_merge_transfers_images_and_preserves_historical_files(self):
        r=self.store.save(self.p,0);review=self.review_copy()
        a=review.upload_attachment(self.PNG,'bien_ban.png','Giám sát')
        edit=copy.deepcopy(self.p);edit['attachments']=[a];review.save(edit,1,'Bổ sung ảnh hiện trường')
        edit['attachments']=[];edit['notes']='Ảnh đã chuyển sang lịch sử';review.save(edit,2,'Gỡ khỏi bản hiện tại')
        self.store.apply_corrections(review,[r['id']])
        self.assertEqual(self.store.attachment(a['hash'])['data'],self.PNG)
        self.assertEqual(self.store.history(r['id'])[1]['payload']['attachments'][0]['hash'],a['hash'])

    def test_missing_or_corrupted_attachment_rejected(self):
        self.store.save(self.p,0);review=self.review_copy()
        a=review.upload_attachment(self.PNG,'a.png','Giám sát');edit=copy.deepcopy(self.p);edit['attachments']=[a]
        with self.assertRaises(AppError):self.store.save(edit,1)
        review.save(edit,1,'Bổ sung ảnh')
        with review.connect() as c:c.execute('UPDATE attachment_blobs SET data=? WHERE hash=?',(b'corrupted',a['hash']))
        with self.assertRaises(AppError):self.store.apply_corrections(review,['2026-11-02_NIGHT'])
        self.assertEqual(self.store.get('2026-11-02_NIGHT')['version'],1)

    def test_attachment_limits_types_and_deduplication(self):
        for data in (b'', b'%PDF-'+b'x'*MAX_FILE):
            with self.assertRaises(AppError):self.store.upload_attachment(data,'t.html','Anh')
        a=self.store.upload_attachment(self.PNG,'a.png','Anh')
        self.store.upload_attachment(self.PNG,'b.png','Anh')
        with self.store.connect() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM attachment_blobs').fetchone()[0],1)
        self.p['attachments']=[a,a]
        with self.assertRaises(AppError):self.store.save(self.p,0)
        self.p['attachments']=[dict(hash='f'*64,name='a.png',caption='')]
        with self.assertRaises(AppError):self.store.save(self.p,0)
        self.assertEqual(file_type(b'\x00\x00\x00\x20ftypheic\x00\x00\x00\x00mif1')[0],'image/heic')

    def test_all_extensions_original_bytes_and_closed_shift_direct_attach(self):
        self.p['status']='closed'
        r=self.store.save(self.p,0,'Chốt ca')
        for i,ext in enumerate(('.docx','.xlsx','.zip','.mp4','.mp3','.svg','.html','.abc','')):
            data=(str(i)+' nguyên bản <script>không thực thi</script>').encode()
            name='biên bản '+str(i)+ext
            result=self.store.add_attachment(r['id'],r['version'],data,name,'Giám sát')
            r=result['report'];a=result['attachment']
            self.assertEqual(a['name'],name)
            self.assertEqual(self.store.attachment(a['hash'])['data'],data)
            self.assertEqual(self.store.attachment(a['hash'])['mime'],'application/octet-stream')
            self.assertEqual(r['status'],'closed')
        h=self.store.history(r['id'])
        self.assertEqual(len(h),10)
        self.assertTrue(h[0]['reason'].startswith('Thêm tệp đính kèm:'))
        duplicate=self.store.add_attachment(r['id'],r['version'],data,name,'Giám sát')
        self.assertFalse(duplicate['added'])
        self.assertEqual(duplicate['report']['version'],r['version'])

    def test_direct_attach_to_review_copy_keeps_main_untouched(self):
        self.p['status']='closed';r=self.store.save(self.p,0,'Chốt ca')
        review=self.review_copy()
        result=review.add_attachment(r['id'],r['version'],b'word file bytes','biên bản.doc','Anh')
        self.assertEqual(len(result['report']['attachments']),1)
        self.assertFalse(self.store.get(r['id']).get('attachments'))
        self.store.apply_corrections(review,[r['id']])
        a=self.store.get(r['id'])['attachments'][0]
        self.assertEqual(self.store.attachment(a['hash'])['data'],b'word file bytes')

    def test_explicit_attachment_columns_and_connection_close(self):
        with self.store.connect() as c:
            c.execute('ALTER TABLE attachment_blobs ADD COLUMN extra_note TEXT')
            with self.assertRaises(sqlite3.OperationalError):
                c.execute('INSERT INTO attachment_blobs VALUES(?,?,?,?,?)',('hash','type',b'data','time','actor'))
        with self.assertRaises(sqlite3.ProgrammingError):c.execute('SELECT 1')
        a=self.store.upload_attachment(self.PNG,'ảnh.png','Anh')
        self.assertEqual(self.store.attachment(a['hash'])['data'],self.PNG)

    def test_http_direct_upload_arbitrary_file_and_error_diagnostics(self):
        from unittest.mock import patch
        server=make_server(self.root/'http_direct');worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        base='http://'+server.app['host'];opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def post(path,payload):
            body=payload if isinstance(payload,bytes) else json.dumps(payload).encode()
            return opener.open(urllib.request.Request(base+path,data=body,headers={'X-Ca-Request':'1'}))
        try:
            opener.open(base+'/?launch='+server.app['token']).read()
            ctx=server.app['context'];self.p['status']='closed'
            r=json.loads(post('/api/save',dict(report=self.p,version=0,context=ctx,reason='Chốt ca')).read())
            qs=urllib.parse.urlencode(dict(context=ctx,id=r['id'],version=r['version'],name='biên bản.html',actor='Anh'))
            result=json.loads(post('/api/attachment-upload?'+qs,b'<html><script>alert(1)</script></html>').read())
            self.assertTrue(result['added']);self.assertEqual(result['report']['status'],'closed')
            a=result['attachment']
            url='/api/attachment?'+urllib.parse.urlencode(dict(context=ctx,hash=a['hash'],name=a['name']))
            response=opener.open(base+url)
            self.assertEqual(response.headers['Content-Type'],'application/octet-stream')
            self.assertIn('attachment;',response.headers['Content-Disposition'])
            self.assertEqual(response.read(),b'<html><script>alert(1)</script></html>')
            with self.assertLogs(level='ERROR'), patch.object(server.app['store'],'add_attachment',side_effect=sqlite3.OperationalError('database is locked')):
                with self.assertRaises(urllib.error.HTTPError) as error:post('/api/attachment-upload?'+qs,b'test')
            self.assertEqual(error.exception.code,503)
            message=json.loads(error.exception.read())['error']
            self.assertIn('DB đang',message);self.assertNotIn('dung lượng',message)
        finally:
            server.shutdown();worker.join();server.server_close()

    def test_people_directory_and_multiple_names_survive_backup(self):
        self.assertEqual(len(self.store.people()),34)
        self.assertEqual(len(set(self.store.people())),34)
        self.assertIn('Nguyễn Trần Tân Phong',self.store.people())
        self.p['actor']='Giáp Hoàng Duy'
        self.p['staffing'][0]['people']='; '.join(self.store.people())
        r=self.store.save(self.p,0)
        view=Store(self.store.backup(self.root/'names.db'),True)
        self.assertEqual(view.people(),self.store.people())
        self.assertEqual(view.get(r['id'])['staffing'][0]['people'],self.p['staffing'][0]['people'])

    def test_legacy_viewer_gets_default_people_without_mutation(self):
        with self.store.connect() as c:c.execute('DROP TABLE people')
        before=self.store.path.read_bytes()
        self.assertEqual(Store(self.store.path,True).people(),PEOPLE)
        self.assertEqual(self.store.path.read_bytes(),before)

    def test_legacy_db_without_attachments_table_can_be_opened(self):
        self.store.save(self.p,0)
        with self.store.connect() as c:
            c.execute('DROP TABLE attachment_blobs')
            c.execute("UPDATE meta SET value='1' WHERE key='schema_version'")
        view=Store(self.store.path,True)
        self.assertEqual(len(view.list({})),1)
        writable=Store(self.store.path)
        self.assertEqual(writable.meta('schema_version'),'3')
        old=Store(self.store.path.with_name('main_TRUOC_NANG_CAP_1_2.db'),True)
        self.assertEqual(old.meta('schema_version'),'1')
        self.assertEqual(len(old.list({})),1)
        a=writable.upload_attachment(self.PNG,'a.png','Anh')
        self.assertEqual(writable.attachment(a['hash'])['data'],self.PNG)

    def test_http_attachments_zip_shutdown_and_running_session(self):
        server=make_server(self.root/'http_images');worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        base='http://'+server.app['host'];token=server.app['token']
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def get(path):return opener.open(base+path)
        def post(path,payload):
            data=payload if isinstance(payload,bytes) else json.dumps(payload).encode()
            return opener.open(urllib.request.Request(base+path,data=data,headers={'X-Ca-Request':'1'}))
        try:
            get('/?launch='+token).read();ctx=json.loads(get('/api/info').read())['context']
            # A file larger than the previous 10 MB limit must remain byte-for-byte intact.
            large_png=self.PNG + b'\x00'*(12*1024*1024)
            a=json.loads(post('/api/attachment-upload?'+urllib.parse.urlencode(dict(context=ctx,name='ảnh hiện trường.png',actor='Anh')),large_png).read())
            self.p['attachments']=[a]
            r=json.loads(post('/api/save',dict(report=self.p,version=0,context=ctx)).read())
            self.assertEqual(get('/api/attachment?'+urllib.parse.urlencode(dict(context=ctx,hash=a['hash']))).read(),large_png)
            with self.assertRaises(urllib.error.HTTPError) as e:get('/api/attachment?hash='+a['hash']+'&context=old')
            self.assertEqual(e.exception.code,409)
            package=get('/api/attachments-zip?'+urllib.parse.urlencode(dict(context=ctx,id=r['id']))).read()
            with zipfile.ZipFile(io.BytesIO(package)) as z:
                image=next(n for n in z.namelist() if n.endswith('.png'))
                self.assertEqual(z.read(image),large_png)
            session=self.root/'http_images'/'PHIEN_DANG_CHAY.json'
            session.write_text(json.dumps(dict(port=server.server_port,token=token)))
            self.assertTrue(running_session(session.parent).startswith(base))
            self.assertTrue(json.loads(post('/api/shutdown',{}).read())['ok'])
            worker.join(3);self.assertFalse(worker.is_alive())
        finally:
            server.shutdown();worker.join();server.server_close()

    def review_copy(self):
        path=self.store.backup(self.root/'review.db')
        return Store(path,True).enable_corrections('Người giám sát')

    def test_review_edit_preserves_original_and_requires_reason(self):
        r=self.store.save(self.p,0)
        original=self.store.path.read_bytes()
        review=self.review_copy()
        p=copy.deepcopy(self.p);p['actor']='Người giám sát';p['notes']='Bổ sung ca cũ'
        with self.assertRaises(AppError):review.save(p,1)
        review.save(p,1,'Anh em thiếu bàn giao')
        self.assertEqual(self.store.get(r['id'])['notes'],'')
        self.assertEqual(self.store.path.read_bytes(),original)
        self.assertEqual(len(review.history(r['id'])),2)
        new=copy.deepcopy(p);new['date']='2026-11-03'
        with self.assertRaises(AppError):review.save(new,0,'Không tạo mới trong bản sao')

    def test_merge_preserves_new_shifts_and_reviewer_history(self):
        r=self.store.save(self.p,0)
        review=self.review_copy()
        edit=copy.deepcopy(self.p);edit['actor']='Người giám sát';edit['jobs'][0]['e20']=9
        review.save(edit,1,'Bổ sung 6 lượt thiếu')
        edit['notes']='Đã đối chiếu';review.save(edit,2,'Ghi rõ đã đối chiếu')
        new=copy.deepcopy(self.p);new['date']='2026-11-03';self.store.save(new,0)
        plan=self.store.correction_plan(review)
        self.assertEqual([(x['id'],x['state']) for x in plan],[(r['id'],'ready')])
        self.assertEqual(self.store.apply_corrections(review,[r['id']]),1)
        self.assertEqual(len(self.store.list({})),2)
        self.assertEqual(self.store.get(r['id'])['jobs'][0]['e20'],9)
        hist=self.store.history(r['id']);self.assertEqual(len(hist),3)
        self.assertEqual(hist[0]['actor'],'Người giám sát')
        self.assertIn('Ghi rõ đã đối chiếu',hist[0]['reason'])
        self.assertEqual(self.store.correction_plan(review)[0]['state'],'same')
        with self.assertRaises(AppError):self.store.apply_corrections(review,[r['id']])

    def test_conflict_does_not_overwrite_and_whole_batch_rolls_back(self):
        first=self.store.save(self.p,0)
        second=copy.deepcopy(self.p);second['date']='2026-11-01'
        second_id=self.store.save(second,0)['id']
        review=self.review_copy()
        for p in (copy.deepcopy(self.p),copy.deepcopy(second)):
            p['notes']='Giám sát bổ sung';review.save(p,1,'Thiếu ghi chú')
        edit=copy.deepcopy(self.p);edit['notes']='Anh em đã cập nhật mới'
        self.store.save(edit,1)
        states={r['id']:r['state'] for r in self.store.correction_plan(review)}
        self.assertEqual(states[first['id']],'conflict');self.assertEqual(states[second_id],'ready')
        with self.assertRaises(AppError):self.store.apply_corrections(review,[second_id,first['id']])
        self.assertEqual(self.store.get(second_id)['notes'],'')
        self.assertEqual(self.store.get(first['id'])['notes'],'Anh em đã cập nhật mới')

    def test_reject_foreign_db_and_legacy_review(self):
        self.store.save(self.p,0);review=self.review_copy()
        other=Store(self.root/'other.db')
        with self.assertRaises(AppError):other.correction_plan(review)
        legacy=self.root/'legacy.db';self.store.backup(legacy)
        with sqlite3.connect(str(legacy),factory=ClosingConnection) as c:c.execute("DELETE FROM meta WHERE key='database_id'")
        with self.assertRaises(AppError):Store(legacy,True).enable_corrections('Người giám sát')

    def test_unchanged_review_excluded_and_main_requires_correct_mode(self):
        self.store.save(self.p,0);review=self.review_copy()
        self.assertEqual(self.store.correction_plan(review),[])
        with self.assertRaises(AppError):review.correction_plan(self.store)

    def test_http_workflow_and_source_switch_protection(self):
        server=make_server(self.root/'http')
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        base='http://'+server.app['host']
        opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def get(path):
            return opener.open(base+path).read()
        def post(path,payload,mime='application/json'):
            body=payload if isinstance(payload,bytes) else json.dumps(payload).encode()
            return opener.open(urllib.request.Request(base+path,data=body,headers={'Content-Type':mime,'X-Ca-Request':'1'})).read()
        try:
            with self.assertRaises(urllib.error.HTTPError):get('/api/info')
            self.assertIn(b'<html',get('/?launch='+server.app['token']))
            info=json.loads(get('/api/info'));context=info['context']
            r=json.loads(post('/api/save',dict(report=self.p,version=0,context=context)))
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                post('/api/save',dict(report=self.p,version=0,context=context))
            self.assertEqual(ctx.exception.code,409)
            exported=get('/api/export?id='+r['id']+'&context='+context)
            self.assertTrue(zipfile.is_zipfile(io.BytesIO(exported)))
            db=post('/api/backup',dict(context=context))
            self.assertTrue(db.startswith(b'SQLite format 3'))
            original=(self.root/'http'/'BAO_CAO_CA.db').read_bytes()
            post('/api/open-viewer',db,'application/octet-stream')
            viewinfo=json.loads(get('/api/info'));self.assertTrue(viewinfo['readonly'])
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                post('/api/save',dict(report=self.p,version=1,context=viewinfo['context']))
            self.assertEqual(ctx.exception.code,403)
            self.assertEqual((self.root/'http'/'BAO_CAO_CA.db').read_bytes(),original)
            post('/api/enable-corrections',dict(context=viewinfo['context'],reviewer='Giám sát'))
            editinfo=json.loads(get('/api/info'));self.assertFalse(editinfo['readonly'])
            edit=copy.deepcopy(self.p);edit['actor']='Giám sát';edit['notes']='Bổ sung qua giao diện API'
            post('/api/save',dict(report=edit,version=1,reason='Bổ sung thông tin thiếu',context=editinfo['context']))
            revised=post('/api/backup',dict(context=editinfo['context']))
            post('/api/main-db',{})
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                post('/api/save',dict(report=self.p,version=1,context=context))
            self.assertEqual(ctx.exception.code,409)
            plan=json.loads(post('/api/corrections-preview',revised,'application/octet-stream'))
            self.assertEqual(plan['items'][0]['state'],'ready')
            result=json.loads(post('/api/corrections-apply',dict(nonce=plan['nonce'],selected=[r['id']])))
            self.assertEqual(result['count'],1)
            self.assertEqual(json.loads(get('/api/report?id='+r['id']))['notes'],'Bổ sung qua giao diện API')
            self.assertEqual(len(list((self.root/'http'/'TRUOC_KHI_NHAP_BO_SUNG').glob('*.db'))),1)
            self.assertEqual(len(json.loads(get('/api/reports'))),1)
            self.assertGreaterEqual(len(list((self.root/'http'/'SAO_LUU_AN_TOAN').rglob('*.db'))),1)
        finally:
            server.shutdown();worker.join();server.server_close()


if __name__=='__main__':
    unittest.main(verbosity=2)
