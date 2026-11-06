"""Kiểm tra cấu hình ngoài, tương thích DB và các tệp giao diện đã tách."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
import http.cookiejar

from LUU_TRU import Store
from MAY_CHU import make_server
from NGHIEP_VU import AppError
from QUAN_LY_DANH_MUC import Catalogs, parse_lines


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / 'DU_LIEU' / 'BAO_CAO_CA.db')

    def tearDown(self):
        self.temp.cleanup()

    def report(self):
        return dict(date='2026-11-04', shift='DAY', actor='Tên cũ', status='draft',
                    notes='', staffing=[dict(role='PHỤ TRÁCH CHUNG', people='Tên cũ')],
                    jobs=[dict(name='Công việc cũ', detail='', xn=False, rtg=False,
                               f20=1, f40=None, e20=0, e40=None)], handover=[])

    def test_first_migration_preserves_custom_db_people(self):
        with self.store.connect() as c:
            c.execute('DELETE FROM people')
            c.execute('INSERT INTO people(name,active) VALUES(?,1)', ('Nhân viên tùy chỉnh',))
        cat = Catalogs(self.root/'DANH_MUC', self.store)
        self.assertEqual(cat.sync()['people'], ['Nhân viên tùy chỉnh'])
        # Existing external files must never be re-seeded on startup.
        (cat.directory/'NHAN_VIEN.txt').write_text('Tên mới\n', encoding='utf-8')
        again = Catalogs(cat.directory, self.store)
        self.assertEqual(again.sync()['people'], ['Tên mới'])

    def test_external_change_affects_catalog_not_historical_reports(self):
        r = self.store.save(self.report(), 0)
        cat = Catalogs(self.root/'DANH_MUC', self.store)
        cat.sync()
        (cat.directory/'NHAN_VIEN.txt').write_text('Anh mới\nChị mới\n', encoding='utf-8')
        (cat.directory/'CONG_VIEC.txt').write_text('Công việc mới\n', encoding='utf-8')
        data = cat.sync()
        self.assertEqual(data['people'], ['Anh mới', 'Chị mới'])
        self.assertEqual(self.store.people(), data['people'])
        self.assertEqual(self.store.get(r['id'])['staffing'][0]['people'], 'Tên cũ')
        self.assertEqual(self.store.get(r['id'])['jobs'][0]['name'], 'Công việc cũ')
        self.assertEqual(len(self.store.history(r['id'])), 1)

    def test_invalid_file_uses_last_good_snapshot(self):
        cat = Catalogs(self.root/'DANH_MUC', self.store)
        original = cat.sync()
        (cat.directory/'NHAN_VIEN.txt').write_text('Trùng tên\ntrùng tên\n', encoding='utf-8')
        data = cat.sync()
        self.assertEqual(data['people'], original['people'])
        self.assertIn('bị trùng', cat.warning)
        with self.assertRaises(AppError): parse_lines('GATE\nCFS', 'roles')
        with self.assertRaises(AppError): parse_lines('', 'people')

    def test_save_and_concurrent_file_edit_conflict(self):
        cat = Catalogs(self.root/'DANH_MUC', self.store)
        cat.sync()
        old = cat.editor_data()
        (cat.directory/'NHAN_VIEN.txt').write_text('Tên sửa bên ngoài\n', encoding='utf-8')
        with self.assertRaises(AppError) as ctx:
            cat.save(old, old['digest'])
        self.assertEqual(ctx.exception.status, 409)
        data = cat.editor_data()
        data['people'] = 'Người mới\n'
        result = cat.save(data, data['digest'])
        self.assertEqual(result['people'], ['Người mới'])
        self.assertEqual(len(list((cat.directory/'SAO_LUU').iterdir())), 1)

    def test_catalog_travels_in_db_without_external_files(self):
        cat = Catalogs(self.root/'DANH_MUC', self.store)
        cat.sync()
        data = cat.editor_data()
        data.update(people='Người theo DB\n', roles='PHỤ TRÁCH CHUNG\nVỊ TRÍ MỚI\n', jobs='VIỆC MỚI\n')
        cat.save(data, data['digest'])
        db = Store(self.store.backup(self.root/'mang_di.db'), True)
        snapshot = cat.snapshot(db)
        self.assertEqual(snapshot['people'], ['Người theo DB'])
        self.assertEqual(snapshot['jobs'], ['VIỆC MỚI'])
        self.assertIn('VỊ TRÍ MỚI', snapshot['roles'])

    def test_http_catalog_save_assets_and_review_protection(self):
        server = make_server(self.root/'HTTP'/'DU_LIEU')
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        base = 'http://' + server.app['host']
        def get(path): return opener.open(base+path)
        def post(path, body):
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            return opener.open(urllib.request.Request(base+path, data=data, headers={'X-Ca-Request':'1'}))
        try:
            html = get('/?launch='+server.app['token']).read().decode()
            self.assertIn('Mr Ân / Tân Thuận', html)
            for asset in ['style.css', 'ung_dung.js', 'danh_muc.js']:
                response = get('/tai_nguyen/'+asset)
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 100)
                self.assertIn("script-src 'self'", response.headers['Content-Security-Policy'])
            info = json.load(get('/api/info'))
            editor = json.load(get('/api/catalogs'))
            editor['people'] = 'Nhân viên mới từ giao diện\n'
            post('/api/catalogs-save', dict(context=info['context'], digest=editor['digest'], text=editor)).read()
            self.assertEqual(json.load(get('/api/info'))['people'], ['Nhân viên mới từ giao diện'])
            blob = post('/api/backup', dict(context=info['context'])).read()
            post('/api/open-viewer', blob).read()
            view = json.load(get('/api/info'))
            self.assertEqual(view['people'], ['Nhân viên mới từ giao diện'])
            with self.assertRaises(urllib.error.HTTPError): get('/api/catalogs')
            with self.assertRaises(urllib.error.HTTPError):
                post('/api/catalogs-save', dict(context=view['context'], digest=editor['digest'], text=editor))
        finally:
            server.shutdown(); worker.join(); server.server_close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
