"""Kiểm thử hết dung lượng bằng thư mục tạm và disk_usage giả lập."""
import collections
import http.cookiejar
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.request
from unittest.mock import patch
from MAY_CHU import make_server, daily_backup

Usage = collections.namedtuple('Usage', 'total used free')


class SpaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.server = make_server(self.root / 'DU_LIEU')
        self.protection = self.server.app['protection']
        self.old = self.protection.backup()
        self.outside = self.root / 'NGOAI'
        self.outside.mkdir()
        self.protection.set_external(str(self.outside))
        self.protection.backup()
        self.db_before = self.protection.db.read_bytes()
        self.old_before = self.old.read_bytes()
        self.last_local = dict(self.protection.config['last_local'])
        self.last_external = dict(self.protection.config['last_external'])

    def tearDown(self):
        self.server.server_close()
        self.temp.cleanup()

    def test_full_local_preserves_files_and_http_warning(self):
        config = self.protection.config_path.read_bytes()
        tick = self.server.app['backup_tick']
        with patch('BAO_VE_DU_LIEU.shutil.disk_usage', return_value=Usage(100, 100, 0)):
            daily_backup(self.server.app)
        self.assertEqual(self.server.app['backup_tick'], tick)
        self.assertTrue(self.server.app['backup_pending'])
        self.assertEqual(self.protection.warning_level, 'error')
        self.assertIn(str(self.protection.local), self.protection.warning)
        self.assertIn('0 byte', self.protection.warning)
        self.assertEqual(self.protection.db.read_bytes(), self.db_before)
        self.assertEqual(self.old.read_bytes(), self.old_before)
        self.assertEqual(self.protection.config_path.read_bytes(), config)
        self.assertEqual(self.protection.config['last_local'], self.last_local)
        self.assertEqual(self.protection.config['last_external'], self.last_external)
        self.assertFalse(list(self.root.rglob('*.tmp')))
        worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        worker.start()
        try:
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
            base = 'http://' + self.server.app['host']
            opener.open(base + '/?launch=' + self.server.app['token']).read()
            info = json.load(opener.open(base + '/api/info'))
            self.assertEqual(info['backup_level'], 'error')
            self.assertEqual(info['backup_warning'], self.protection.warning)
        finally:
            self.server.shutdown()
            worker.join(10)

    def test_full_external_keeps_local_and_old_external(self):
        old_external = self.protection.external() / self.last_external['name']
        original_external = old_external.read_bytes()
        def disk_usage(path):
            return Usage(100, 100, 0) if Path(path) == self.protection.external() else Usage(10**12, 0, 10**12)
        with patch('BAO_VE_DU_LIEU.shutil.disk_usage', side_effect=disk_usage):
            result = self.protection.backup()
        self.assertTrue(result.is_file())
        self.assertEqual(self.protection.warning_level, 'error')
        self.assertIn(str(self.protection.external()), self.protection.warning)
        self.assertIn('0 byte', self.protection.warning)
        self.assertEqual(self.protection.config['last_external'], self.last_external)
        self.assertNotEqual(self.protection.config['last_local'], self.last_local)
        self.assertEqual(old_external.read_bytes(), original_external)
        self.assertEqual(self.protection.db.read_bytes(), self.db_before)
        self.assertEqual(self.old.read_bytes(), self.old_before)
        self.assertFalse(list(self.root.rglob('*.tmp')))

    def test_missing_destination_root_fails_without_loop(self):
        with patch.object(Path, 'exists', return_value=False):
            with self.assertRaisesRegex(OSError, 'Không tìm thấy'):
                self.protection._space_warning(self.root / 'missing' / 'backup', 100)

    def test_free_space_boundary(self):
        required = self.protection._space_required()
        with patch('BAO_VE_DU_LIEU.shutil.disk_usage', return_value=Usage(required, 0, required)):
            self.assertTrue(self.protection.backup().is_file())
        with patch('BAO_VE_DU_LIEU.shutil.disk_usage', return_value=Usage(required, 1, required - 1)):
            self.assertIsNone(self.protection.backup())
            self.assertEqual(self.protection.warning_level, 'error')

    def test_safety_factor_accounts_for_live_wal(self):
        import sqlite3
        from NGHIEP_VU import ClosingConnection
        db = self.protection.db
        with sqlite3.connect(db, factory=ClosingConnection) as connection:
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute("update meta set value=value || 'x' where key='people_seeded'")
            connection.commit()
            wal = Path(str(db) + '-wal')
            total = db.stat().st_size + wal.stat().st_size
            self.assertGreaterEqual(self.protection._space_required(), (total * 6 + 4) // 5)


if __name__ == '__main__':
    unittest.main()
