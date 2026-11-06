# -*- coding: utf-8 -*-
"""Kiểm thử các thay đổi bản 1.9: phân trang, trang chủ, sao lưu hoãn, xoay vòng nhật ký, dọn bản sao."""
import copy
import http.cookiejar
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import Mock, patch

from BAO_CAO_CA import rotate_log
from LUU_TRU import Store
from MAU_PHAN_CONG import merge_team_members
from MAY_CHU import daily_backup, int_param, make_server
from NGHIEP_VU import AppError
from QUAN_LY_DANH_MUC import Catalogs


def draft(day, shift='DAY', status='draft', note=''):
    return dict(date=day, shift=shift, actor='Người kiểm thử', status=status, notes=note,
                staffing=[dict(role='PHỤ TRÁCH CHUNG', people='Trưởng ca')], jobs=[], handover=[])


class PagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / 'DU_LIEU' / 'BAO_CAO_CA.db')
        for day in range(1, 8):
            self.store.save(draft('2026-11-%02d' % day, note='ghi chú số %d' % day), 0)
        self.store.save(draft('2026-10-31', status='closed', note='cuối tháng'), 0)

    def tearDown(self):
        self.temp.cleanup()

    def test_page_slices_and_counts_in_sql(self):
        first = self.store.page({}, 3, 0)
        self.assertEqual((first['total'], len(first['rows'])), (8, 3))
        self.assertEqual([r['date'] for r in first['rows']], ['2026-11-07', '2026-11-06', '2026-11-05'])
        last = self.store.page({}, 3, 6)
        self.assertEqual([r['date'] for r in last['rows']], ['2026-11-01', '2026-10-31'])
        self.assertEqual(self.store.page({}, 3, 99)['rows'], [])

    def test_page_matches_list_with_filters_and_search(self):
        for filters in ({'status': 'closed'}, {'from': '2026-11-03', 'to': '2026-11-05'}, {'q': 'số 4'}, {'q': 'KHÔNG CÓ'}):
            with self.subTest(filters=filters):
                everything = self.store.list(filters)
                paged = self.store.page(filters, 2, 0)
                self.assertEqual(paged['total'], len(everything))
                self.assertEqual([r['id'] for r in paged['rows']], [r['id'] for r in everything][:2])

    def test_overview_counts_without_loading_everything(self):
        view = self.store.overview({'date': '2026-11-03', 'shift': 'DAY'}, '2026-11', recent=6)
        self.assertEqual(view['month_count'], 7)
        self.assertEqual(view['draft_count'], 7)
        self.assertEqual(len(view['recent']), 6)
        self.assertEqual(view['recent'][0]['date'], '2026-11-07')
        self.assertEqual(view['current_status'], 'draft')
        missing = self.store.overview({'date': '2026-12-01', 'shift': 'NIGHT'}, '2026-12')
        self.assertEqual((missing['month_count'], missing['current_status']), (0, ''))

    def test_int_param_rejects_bad_values(self):
        self.assertEqual(int_param({}, 'limit', 50, 1, 200), 50)
        self.assertEqual(int_param({'limit': '7'}, 'limit', 50, 1, 200), 7)
        for bad in ('abc', '0', '201', '-1', '1.5'):
            with self.subTest(bad=bad), self.assertRaises(AppError):
                int_param({'limit': bad}, 'limit', 50, 1, 200)


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        # Đăng ký trước: cleanup chạy ngược, nên máy chủ đóng xong mới xóa thư mục tạm.
        self.addCleanup(self.temp.cleanup)

    def start(self):
        server = make_server(self.root / 'DU_LIEU')
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://' + server.app['host']
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        opener.open(base + '/?launch=' + server.app['token']).read()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join(5)))
        return server, base, opener

    def test_paging_and_overview_over_http(self):
        server, base, opener = self.start()
        for day in range(1, 6):
            server.app['store'].save(draft('2026-11-%02d' % day), 0)
        page = json.loads(opener.open(base + '/api/reports-page?limit=2&offset=2').read())
        self.assertEqual((page['total'], [r['date'] for r in page['rows']]), (5, ['2026-11-03', '2026-11-02']))
        view = json.loads(opener.open(base + '/api/overview').read())
        self.assertEqual(view['draft_count'], 5)
        self.assertLessEqual(len(view['recent']), 6)
        with self.assertRaises(urllib.error.HTTPError) as raised:
            opener.open(base + '/api/reports-page?limit=abc')
        self.assertEqual(raised.exception.code, 400)

    def test_cheap_writes_do_not_force_a_full_backup(self):
        calls = []
        with patch('MAY_CHU.daily_backup', side_effect=lambda app, force=True: calls.append(force)):
            server, base, opener = self.start()
            calls.clear()
            context = json.loads(opener.open(base + '/api/info').read())['context']
            body = json.dumps(dict(name='TAU KIEM THU 1.9', context=context)).encode()
            opener.open(urllib.request.Request(base + '/api/ships-add', data=body, headers={'X-Ca-Request': '1'})).read()
            self.assertEqual(calls, [False])
            report = json.dumps(dict(report=draft('2026-11-05', status='closed'), version=0, reason='', context=context)).encode()
            opener.open(urllib.request.Request(base + '/api/save', data=report, headers={'X-Ca-Request': '1'})).read()
            self.assertEqual(calls, [False, True])

    def test_deferred_backup_is_made_up_on_shutdown(self):
        server, base, opener = self.start()
        server.app['backup_pending'] = True
        with patch('MAY_CHU.daily_backup') as backup:
            opener.open(urllib.request.Request(base + '/api/shutdown', data=b'{}', headers={'X-Ca-Request': '1'})).read()
        backup.assert_called_once()


class DeferredBackupTests(unittest.TestCase):
    def test_throttled_call_marks_pending_and_next_success_clears_it(self):
        store = Mock()
        store.readonly = False
        protection = Mock()
        protection.warning = ''
        app = dict(store=store, main_store=store, protection=protection, backup_tick=time.monotonic())
        daily_backup(app, force=False)
        protection.backup.assert_not_called()
        self.assertTrue(app['backup_pending'])
        daily_backup(app, force=True)
        protection.backup.assert_called_once()
        self.assertFalse(app['backup_pending'])


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_merge_team_members_does_not_mutate_input(self):
        data = dict(teams=[dict(id='team1', name='Ca 1', people=['An'])],
                    staff_templates=dict(team1=[dict(role='X', people=['An', 'Bình'])], day=[]))
        before = copy.deepcopy(data)
        merged = merge_team_members(data)
        self.assertEqual(data, before)
        self.assertEqual(merged[0]['people'], ['An', 'Bình'])

    def test_rotate_log_keeps_three_old_files(self):
        log = self.root / 'NHAT_KY.log'
        for turn in range(6):
            log.write_text('lần %d ' % turn + 'x' * 50, encoding='utf-8')
            rotate_log(log, limit=10, keep=3)
            self.assertFalse(log.exists())
        names = sorted(p.name for p in self.root.iterdir())
        self.assertEqual(names, ['NHAT_KY.log.1', 'NHAT_KY.log.2', 'NHAT_KY.log.3'])
        self.assertIn('lần 5', (self.root / 'NHAT_KY.log.1').read_text(encoding='utf-8'))

    def test_rotate_log_ignores_small_or_missing_files(self):
        log = self.root / 'nho.log'
        rotate_log(log)
        log.write_text('ngắn', encoding='utf-8')
        rotate_log(log)
        self.assertEqual(log.read_text(encoding='utf-8'), 'ngắn')

    def test_catalog_backups_are_capped_newest_first(self):
        store = Store(self.root / 'DU_LIEU' / 'BAO_CAO_CA.db')
        catalogs = Catalogs(self.root / 'DANH_MUC', store)
        folder = catalogs.directory / 'SAO_LUU'
        folder.mkdir(parents=True, exist_ok=True)
        now = time.time()
        for index in range(25):
            item = folder / ('bản%02d' % index)
            item.mkdir()
            os.utime(item, (now + index, now + index))
        catalogs.prune_backups(keep=20)
        left = sorted(p.name for p in folder.iterdir())
        self.assertEqual(len(left), 20)
        self.assertNotIn('bản04', left)
        self.assertIn('bản24', left)


if __name__ == '__main__':
    unittest.main()
