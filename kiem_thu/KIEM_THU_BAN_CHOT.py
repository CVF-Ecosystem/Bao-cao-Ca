"""Regression checks for release 1.5.1; temporary data only, no dependencies."""
import copy
import http.cookiejar
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error
import zipfile
import xml.etree.ElementTree as ET

from BAO_CAO_EXCEL import monthly_tables, styled_xlsx
from LUU_TRU import Store
from MAY_CHU import make_server
from NGHIEP_VU import AppError, chief_people


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root/'main.db')
        self.report = dict(date='2026-11-02', shift='DAY', actor='Tester', status='closed', notes='MAIN',
                           staffing=[dict(role='PHỤ TRÁCH CHUNG', people='Chief')],
                           jobs=[dict(name='DỜI CẤP RỖNG', detail='', xn=True, rtg=False,
                                      f20=0, f40=None, e20=3, e40=2)], handover=[])

    def tearDown(self):
        self.temp.cleanup()

    def counts(self):
        with self.store.connect() as c:
            return tuple(c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
                         for table in ('attachment_blobs', 'reports', 'revisions'))

    def test_duplicate_chief_consistent_with_closed_and_excel(self):
        rows = [dict(role='PHỤ TRÁCH CHUNG', people=''),
                dict(role='PHỤ TRÁCH CHUNG', people='Chief'),
                dict(role='PHỤ TRÁCH CHUNG', people='Chief')]
        self.report['staffing'] = rows
        saved = self.store.save(self.report, 0)
        self.assertEqual(saved['staffing'], rows)
        self.assertEqual(chief_people(rows), 'Chief')
        tables = monthly_tables(self.store, '2026-11')
        entry = next(row for row in tables[0][1] if len(row)>3 and row[0]=='2026-11-02' and row[1].startswith('Ngày'))
        self.assertEqual(entry[3], 'Chief')
        reports = {'02-11_Ngay': saved}
        with zipfile.ZipFile(io.BytesIO(styled_xlsx(tables, reports))) as z:
            xml = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            ns = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            chief_cells = [c for c in xml.findall('.//s:c', ns)
                           if c.get('r','').startswith('D') and ''.join(c.itertext())=='Chief']
            self.assertTrue(chief_cells)

    def test_all_nonempty_chiefs_shown_without_changing_old_rows(self):
        rows = [dict(role='PHỤ TRÁCH CHUNG', people='Chief A'),
                dict(role='PHỤ TRÁCH CHUNG', people='Chief B')]
        self.assertEqual(chief_people(rows), 'Chief A; Chief B')
        self.report['staffing'] = rows
        self.assertEqual(self.store.save(self.report, 0)['staffing'], rows)

    def test_no_chief_still_cannot_close(self):
        self.report['staffing'] = [dict(role='PHỤ TRÁCH CHUNG', people=' ')]
        with self.assertRaises(AppError): self.store.save(self.report, 0)
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_full_capacity_and_duplicate_do_not_write_orphan(self):
        saved = self.store.save(self.report, 0)
        for i in range(40):
            result = self.store.add_attachment(saved['id'], saved['version'], str(i).encode(), str(i)+'.txt', 'Tester')
            saved = result['report']
        counts = self.counts()
        with self.assertRaises(AppError):
            self.store.add_attachment(saved['id'], saved['version'], b'new-41', '41.txt', 'Tester')
        self.assertEqual(self.counts(), counts)
        self.assertEqual(self.store.get(saved['id']), saved)
        duplicate = self.store.add_attachment(saved['id'], saved['version'], b'0', '0.txt', 'Tester')
        self.assertFalse(duplicate['added'])
        self.assertEqual(duplicate['report'], saved)
        self.assertEqual(self.counts(), counts)

    def test_invalid_version_caption_and_missing_report_leave_no_blob(self):
        saved = self.store.save(self.report, 0)
        before = self.counts()
        for rid, version, caption in [(saved['id'], 0, ''), (saved['id'], True, ''),
                                      ('missing', 0, ''), (saved['id'], 1, 'x'*1001)]:
            with self.subTest(rid=rid, version=version, caption_length=len(caption)):
                with self.assertRaises(AppError):
                    self.store.add_attachment(rid, version, b'new', 'new.txt', 'Tester', caption)
                self.assertEqual(self.counts(), before)
                self.assertEqual(self.store.get(saved['id']), saved)

    def test_failure_after_blob_insert_rolls_back_blob_report_and_history(self):
        saved = self.store.save(self.report, 0)
        counts = self.counts()
        original = self.store._save_report
        def fail_after_report_write(*args, **kwargs):
            original(*args, **kwargs)
            raise sqlite3.OperationalError('simulated disk failure before commit')
        with patch.object(self.store, '_save_report', side_effect=fail_after_report_write):
            with self.assertRaises(sqlite3.OperationalError):
                self.store.add_attachment(saved['id'], 1, b'not-committed', 'new.txt', 'Tester')
        self.assertEqual(self.counts(), counts)
        self.assertEqual(self.store.get(saved['id']), saved)

    def test_successful_attachment_commits_all_and_original_bytes(self):
        saved = self.store.save(self.report, 0)
        raw = b'original-file-bytes\x00\xff'
        result = self.store.add_attachment(saved['id'], 1, raw, 'proof.bin', 'Tester', 'Evidence')
        self.assertTrue(result['added'])
        self.assertEqual(self.counts(), (1, 1, 2))
        self.assertEqual(self.store.attachment(result['attachment']['hash'])['data'], raw)
        history = self.store.history(saved['id'])
        self.assertNotIn('attachments', history[-1]['payload'])
        self.assertEqual(history[0]['payload']['attachments'][0]['caption'], 'Evidence')
        self.assertEqual(result['report']['status'], 'closed')

    def test_http_stale_and_missing_context_rejected_current_source_exported(self):
        server = make_server(self.root/'HTTP'/'DU_LIEU')
        worker = threading.Thread(target=server.serve_forever, daemon=True); worker.start()
        base = 'http://'+server.app['host']
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def get(path):
            with opener.open(base+path) as response: return response.read()
        def post(path, body):
            raw = body if isinstance(body, bytes) else json.dumps(body).encode()
            req = urllib.request.Request(base+path, data=raw, headers={'X-Ca-Request':'1'})
            with opener.open(req) as response: return response.read()
        def assert_blocked(call):
            with self.assertRaises(urllib.error.HTTPError) as raised: call()
            self.assertEqual(raised.exception.code, 409)
            raised.exception.close()
        try:
            get('/?launch='+server.app['token'])
            info = json.loads(get('/api/info')); old = info['context']
            saved = server.app['main_store'].save(self.report, 0)
            other = Store(self.root/'other.db'); incoming = copy.deepcopy(self.report); incoming['notes'] = 'REVIEW_SOURCE'
            other.save(incoming, 0)
            raw = other.backup(self.root/'other_copy.db').read_bytes()
            post('/api/open-viewer', raw)
            current = json.loads(get('/api/info'))['context']
            for context in ('', '&context='+old):
                assert_blocked(lambda: get('/api/export?id='+saved['id']+context))
                assert_blocked(lambda: get('/api/export?from=2026-11-01'+context))
            for payload in ({}, {'context':old}):
                assert_blocked(lambda: post('/api/backup', payload))
            self.assertFalse((server.app['data_dir']/'SAO_LUU_MANG_DI').exists())
            for path in ['/api/export?id='+saved['id'], '/api/export?from=2026-11-01', '/api/export-month?month=2026-11']:
                exported = get(path+'&context='+current)
                with zipfile.ZipFile(io.BytesIO(exported)) as z:
                    for name in z.namelist():
                        if name.endswith('.xml'): ET.fromstring(z.read(name))
                if 'id=' in path:
                    with zipfile.ZipFile(io.BytesIO(exported)) as z:
                        self.assertIn('REVIEW_SOURCE', z.read('xl/worksheets/sheet1.xml').decode())
            backup = post('/api/backup', {'context':current})
            dest = self.root/'verified.db'; dest.write_bytes(backup)
            self.assertEqual(Store(dest, True).get(saved['id'])['notes'], 'REVIEW_SOURCE')
            post('/api/main-db', {})
            assert_blocked(lambda: get('/api/export?id='+saved['id']+'&context='+current))
            self.assertEqual(server.app['main_store'].get(saved['id'])['notes'], 'MAIN')
        finally:
            server.shutdown(); worker.join(); server.server_close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
