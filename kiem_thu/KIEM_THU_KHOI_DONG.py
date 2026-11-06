"""Kiểm tra tái sử dụng kết quả khởi động trên dữ liệu tạm."""
import sqlite3
import http.server
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import BAO_CAO_CA as entry
import BAO_VE_DU_LIEU as protection_module
from BAO_VE_DU_LIEU import Protection
from LUU_TRU import Store
from NGHIEP_VU import AppError, ClosingConnection
from MAY_CHU import make_server


class StartupReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name) / 'DU_LIEU'
        server = make_server(self.data)
        server.server_close()
        self.protection = Protection(self.data)

    def tearDown(self):
        self.temp.cleanup()

    def test_check_counts_main_and_direct(self):
        inspect = protection_module.inspect_db
        validate = Store.validate
        for direct in (False, True):
            inspected = []
            validations = []
            def counted_inspect(path):
                inspected.append(Path(path).resolve())
                return inspect(path)
            def counted_validate(store):
                validations.append(store.path)
                return validate(store)
            with patch.object(protection_module, 'inspect_db', counted_inspect), \
                 patch.object(Store, 'validate', counted_validate), \
                 patch.object(entry, 'running_session', return_value=None), \
                 patch.object(http.server.HTTPServer, 'serve_forever'), patch('builtins.print'):
                if direct:
                    server = make_server(self.data)
                    server.server_close()
                else:
                    self.assertEqual(entry.main(['--data-dir', str(self.data), '--no-browser']), 0)
            self.assertEqual(len(inspected), 2)
            self.assertEqual(inspected.count(self.protection.db), 1)
            self.assertNotEqual(inspected[1], self.protection.db)
            self.assertEqual(len(validations), 3)

    def test_db_change_during_inspection_blocks_startup(self):
        real_inspect = protection_module.inspect_db
        def inspect_then_change(path):
            info = real_inspect(path)
            with sqlite3.connect(path, factory=ClosingConnection) as connection:
                connection.execute("update meta set value=value || 'x' where key='people_seeded'")
            return info
        with patch.object(protection_module, 'inspect_db', side_effect=inspect_then_change):
            with self.assertRaisesRegex(AppError, 'thay đổi trong lúc kiểm tra'):
                self.protection.guard_startup()
            with self.assertRaisesRegex(AppError, 'thay đổi trong lúc kiểm tra'):
                make_server(self.data)

    def test_receipt_invalid_after_writes_and_sidecars(self):
        db = self.protection.db
        for suffix in ('-wal', '-journal'):
            receipt = self.protection.guard_startup()
            sidecar = Path(str(db) + suffix)
            sidecar.write_bytes(b'')
            self.assertIsNone(self.protection._checked_info(receipt))
            sidecar.unlink()
        receipt = self.protection.guard_startup()
        with sqlite3.connect(db, factory=ClosingConnection) as connection:
            connection.execute("update meta set value='changed' where key='people_seeded'")
        self.assertIsNone(self.protection._checked_info(receipt))
        with patch.object(protection_module, 'inspect_db', wraps=protection_module.inspect_db) as inspect:
            server = make_server(self.data, startup_check=receipt)
            server.server_close()
            self.assertEqual(inspect.call_count, 2)

    def test_wal_database_without_writer_can_start(self):
        with sqlite3.connect(self.protection.db, factory=ClosingConnection) as connection:
            connection.execute('PRAGMA journal_mode=WAL')
        with patch.object(protection_module, 'inspect_db', wraps=protection_module.inspect_db) as inspect:
            receipt = self.protection.guard_startup()
            self.assertEqual(inspect.call_count, 2)
        self.assertIsNotNone(receipt)
        server = make_server(self.data, startup_check=receipt)
        server.server_close()

    def test_lazy_wal_retry_rejects_further_change(self):
        db = self.protection.db
        wal = Path(str(db) + '-wal')
        real_inspect = protection_module.inspect_db
        def mutate(path):
            info = real_inspect(path)
            if not wal.exists():
                wal.write_bytes(b'')
            else:
                wal.write_bytes(b'changed')
            return info
        with patch.object(protection_module, 'inspect_db', side_effect=mutate) as inspect:
            with self.assertRaises(AppError):
                self.protection.guard_startup()
            self.assertEqual(inspect.call_count, 2)
        wal.unlink()

    def test_new_nonempty_wal_does_not_retry(self):
        wal = Path(str(self.protection.db) + '-wal')
        real_inspect = protection_module.inspect_db
        def mutate(path):
            info = real_inspect(path)
            wal.write_bytes(b'not empty')
            return info
        with patch.object(protection_module, 'inspect_db', side_effect=mutate) as inspect:
            with self.assertRaises(AppError):
                self.protection.guard_startup()
            self.assertEqual(inspect.call_count, 1)
        wal.unlink()

    def test_receipt_invalid_after_live_wal_and_replacement(self):
        db = self.protection.db
        with sqlite3.connect(db, factory=ClosingConnection) as connection:
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute("update meta set value=value || 'x' where key='people_seeded'")
            connection.commit()
            receipt = self.protection.guard_startup()
            connection.execute("update meta set value='wal change' where key='people_seeded'")
            connection.commit()
            self.assertIsNone(self.protection._checked_info(receipt))
            with patch.object(protection_module, 'inspect_db', wraps=protection_module.inspect_db) as inspect:
                self.assertFalse(self.protection.needs_adoption(receipt))
                self.assertEqual(inspect.call_count, 1)
        with sqlite3.connect(db, factory=ClosingConnection) as connection:
            connection.execute('PRAGMA journal_mode=DELETE')
        receipt = self.protection.guard_startup()
        replacement = Path(self.temp.name) / 'replacement.db'
        Store(replacement)
        replacement.replace(db)
        self.assertIsNone(self.protection._checked_info(receipt))
        self.assertTrue(self.protection.needs_adoption(receipt))
        with self.assertRaises(AppError):
            make_server(self.data, startup_check=receipt)

    def test_receipt_wrong_path_missing_and_corrupt_never_bypass(self):
        receipt = self.protection.guard_startup()
        other = Protection(Path(self.temp.name) / 'OTHER')
        self.assertIsNone(other._checked_info(receipt))
        self.protection.db.unlink()
        with self.assertRaises(AppError):
            make_server(self.data, startup_check=receipt)
        self.assertFalse(self.protection.db.exists())
        self.protection.db.write_bytes(b'broken')
        with self.assertRaises(AppError):
            make_server(self.data, startup_check=receipt)
        self.assertEqual(self.protection.db.read_bytes(), b'broken')

    def test_receipt_rechecked_after_recovery_and_adoption(self):
        db = self.protection.db
        original = db.read_bytes()
        db.write_bytes(b'broken')
        checks = []
        guard = Protection.guard_startup
        def counted_guard(protection):
            checks.append('guard')
            return guard(protection)
        def stop_after_check(directory, startup_check=None):
            self.assertIsNotNone(Protection(directory)._checked_info(startup_check))
            raise RuntimeError('stop after validated receipt')
        def recover(*args):
            db.write_bytes(original)
            return True
        with patch.object(entry, 'running_session', return_value=None), \
             patch.object(entry, 'recovery_dialog', side_effect=recover), \
             patch.object(entry, 'make_server', side_effect=stop_after_check), \
             patch.object(entry.logging, 'exception'), patch('builtins.print'), \
             patch.object(Protection, 'guard_startup', counted_guard):
            self.assertEqual(entry.main(['--data-dir', str(self.data)]), 1)
        self.assertEqual(len(checks), 2)
        other = Path(self.temp.name) / 'replacement.db'
        Store(other)
        shutil.copyfile(other, db)
        checks.clear()
        def adopt(directory):
            p = Protection(directory)
            p.accept_installed(p.installed_info()['sha256'])
            return True
        with patch.object(entry, 'running_session', return_value=None), \
             patch.object(entry, 'adoption_dialog', side_effect=adopt), \
             patch.object(entry, 'make_server', side_effect=stop_after_check), \
             patch.object(entry.logging, 'exception'), patch('builtins.print'), \
             patch.object(Protection, 'guard_startup', counted_guard):
            self.assertEqual(entry.main(['--data-dir', str(self.data)]), 1)
        self.assertEqual(len(checks), 2)

    def test_initialize_rejects_store_from_other_path(self):
        other = Store(Path(self.temp.name) / 'other.db')
        with self.assertRaises(AppError):
            self.protection.initialize(other)


if __name__ == '__main__':
    unittest.main()
