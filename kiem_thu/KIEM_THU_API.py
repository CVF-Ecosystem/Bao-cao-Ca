# -*- coding: utf-8 -*-
"""Kiểm thử hợp đồng API (xem tai_lieu/API.md). Chạy máy chủ thật trên cổng ngẫu nhiên, dữ liệu trong thư mục tạm.

Mục đích: ghim hành vi hiện tại của giao diện lập trình để các đợt sau (gộp tự lưu, tách dịch vụ ứng dụng,
bản web) đổi bên trong mà không làm vỡ hợp đồng. Không kiểm thử nghiệp vụ chi tiết; phần đó ở các file khác.
"""
import base64
import http.cookiejar
import json
import http.client
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import urllib.error
import urllib.parse
import urllib.request

from MAY_CHU import Handler, make_server

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aC1sAAAAASUVORK5CYII=')


def report(day='2026-11-02', shift='DAY', status='draft', notes=''):
    return dict(date=day, shift=shift, actor='Người nhập thử', status=status, notes=notes,
                staffing=[dict(role='PHỤ TRÁCH CHUNG', people='Trưởng ca')], jobs=[], handover=[])


class ApiContract(unittest.TestCase):
    def test_info_build_contract(self):
        info = self.call('/api/info')[2]
        self.assertEqual(set(info['build']), {'commit', 'built_at', 'version'})
        self.assertEqual(info['build'], dict(commit='nguon', built_at='', version=info['version']))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = make_server(Path(self.temp.name) / 'DU_LIEU')
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.base = 'http://' + self.server.app['host']
        self.session = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        self.anonymous = urllib.request.build_opener()
        self.call('/?launch=' + self.server.app['token'])
        self.context = self.call('/api/info')[2]['context']

    def tearDown(self):
        self.server.shutdown()
        self.worker.join(10)
        self.server.server_close()
        self.temp.cleanup()

    def call(self, path, body=None, headers=None, anonymous=False, method=None, post=None):
        """Trả (mã trạng thái, tiêu đề, nội dung). Nội dung là dict nếu là JSON, ngược lại là bytes."""
        is_post = body is not None if post is None else post
        send = {'X-Ca-Request': '1'} if is_post else {}
        data = None
        if body is not None:
            data = body if isinstance(body, bytes) else json.dumps(body).encode()
            send['Content-Type'] = 'application/json'
        send.update(headers or {})
        request = urllib.request.Request(self.base + path, data=data, headers=send, method=method)
        try:
            response = (self.anonymous if anonymous else self.session).open(request, timeout=30)
            status, head, raw = response.status, response.headers, response.read()
        except urllib.error.HTTPError as error:
            status, head, raw = error.code, error.headers, error.read()
        try:
            content = json.loads(raw) if 'json' in head.get('Content-Type', '') else raw
        except ValueError:
            content = raw
        return status, head, content

    def save(self, rep, version, reason='', context=None):
        return self.call('/api/save', dict(report=rep, version=version, reason=reason,
                                           context=context if context is not None else self.context, save_kind='close' if rep['status']=='closed' and version==0 else 'manual'))

    # ---- Xác thực và kiểm tra yêu cầu -------------------------------------------------------------

    def test_session_cookie_and_launch_token(self):
        self.assertEqual(self.call('/api/info', anonymous=True)[0], 403)
        self.assertEqual(self.call('/?launch=sai-token', anonymous=True)[0], 403)
        status, head, body = self.call('/?launch=' + self.server.app['token'], anonymous=True)
        self.assertEqual(status, 200)
        self.assertIn('HttpOnly', head['Set-Cookie'])
        self.assertIn('SameSite=Strict', head['Set-Cookie'])
        self.assertIn(b'<html', body)

    def test_post_requires_header_origin_and_host(self):
        rep = report()
        body = dict(report=rep, version=0, context=self.context, reason='', save_kind='manual')
        self.assertEqual(self.call('/api/save', body, headers={'X-Ca-Request': ''})[0], 403)
        self.assertEqual(self.call('/api/save', body, headers={'Origin': 'http://evil.example'})[0], 403)
        self.assertEqual(self.call('/api/info', headers={'Host': 'evil.example'})[0], 403)
        # Origin đúng được chấp nhận (trình duyệt luôn gửi Origin cho POST).
        self.assertEqual(self.call('/api/save', body, headers={'Origin': self.base})[0], 200)

    def test_rejected_bodies_and_invalid_length(self):
        body = {'data': 'x' * 300}
        for i in range(100):
            options = ({'headers': {'X-Ca-Request': ''}},
                       {'headers': {'Origin': 'http://evil.example'}},
                       {'anonymous': True})[i % 3]
            status, _, result = self.call('/api/save', body, **options)
            self.assertEqual(status, 403, i)
            self.assertIsInstance(result['error'], str)
        status, _, result = self.call('/api/save', b'x' * (5 * 1024 * 1024))
        self.assertEqual(status, 413)
        self.assertEqual(result['code'], 'LIMIT_EXCEEDED')
        self.assertIsInstance(result['error'], str)
        for length in ('-1', 'abc', '9' * 5000):
            connection = http.client.HTTPConnection(self.server.app['host'], timeout=5)
            connection.request('POST', '/api/save', body=b'x' * 300,
                               headers={'Content-Length': length, 'X-Ca-Request': '1',
                                        'Cookie': 'ca_session_%s=%s' % (self.server.server_port, self.server.app['token'])})
            response = connection.getresponse()
            self.assertEqual(response.status, 400)
            self.assertIsInstance(json.loads(response.read())['error'], str)
            connection.close()
        for i in range(100):
            path, anonymous, expected = (('/api/info', True, 403),
                                         ('/api/khong-co', False, 404))[i % 2]
            status, _, result = self.call(path, b'x' * 300, anonymous=anonymous, method='GET')
            self.assertEqual(status, expected, i)
            self.assertIsInstance(result['error'], str)

    def test_drain_has_total_deadline_and_byte_limit(self):
        handler = Handler.__new__(Handler)
        handler.connection = Mock()
        handler.connection.gettimeout.return_value = None
        handler.rfile = Mock()
        handler.rfile.read1.return_value = b'x'
        with patch('MAY_CHU.time.monotonic', side_effect=[0, 0.1, 0.1, 0.6]):
            handler.drain_body(100)
        self.assertEqual(handler.rfile.read1.call_count, 1)
        self.assertEqual(handler.connection.settimeout.call_args_list[-1].args, (None,))
        handler.rfile.reset_mock()
        handler.rfile.read1.side_effect = lambda size: b'x' * size
        with patch('MAY_CHU.time.monotonic', return_value=0):
            handler.drain_body(8 * 1024 * 1024)
        self.assertEqual(handler.rfile.read1.call_count, 64)
        self.assertTrue(all(call.args == (65536,) for call in handler.rfile.read1.call_args_list))

    # ---- /api/save ---------------------------------------------------------------------------------

    def test_save_returns_report_with_identity_version_and_timestamps(self):
        status, _, saved = self.save(report(), 0)
        self.assertEqual(status, 200)
        self.assertEqual(saved['id'], '2026-11-02_DAY')
        self.assertEqual(saved['version'], 1)
        self.assertTrue(saved['created_at'] and saved['updated_at'])
        for key in ('date', 'shift', 'actor', 'status', 'notes', 'staffing', 'jobs', 'handover'):
            self.assertIn(key, saved)
        again = self.save(dict(report(), notes='đã đổi'), 1)[2]
        self.assertEqual(again['version'], 2)
        self.assertEqual(again['created_at'], saved['created_at'])
        unchanged = self.save(dict(report(), notes='đã đổi'), 2)[2]
        self.assertEqual(unchanged['version'], 2, 'nội dung không đổi thì không tăng phiên bản')

    def test_stale_version_wrong_type_and_missing_context_are_409(self):
        self.assertEqual(self.save(report(), 0)[0], 200)
        for version in (0, 5, '1', None):
            self.assertEqual(self.save(report(notes='x'), version)[0], 409, repr(version))
        self.assertEqual(self.call('/api/save', dict(report=report(notes='x'), version=1))[0], 409)
        self.assertEqual(self.save(report(notes='x'), 1, context='cu')[0], 409)

    def test_closed_report_needs_reason_and_cannot_reopen(self):
        self.assertEqual(self.save(report(status='closed'), 0, 'Chốt ca')[2]['status'], 'closed')
        status, _, body = self.save(report(status='closed', notes='sửa'), 1)
        self.assertEqual(status, 400)
        self.assertIn('lý do', body['error'])
        self.assertEqual(self.save(report(status='draft', notes='mở lại'), 1, 'Mở lại')[0], 400)
        self.assertEqual(self.save(report(status='closed', notes='sửa'), 1, 'Sửa số liệu')[0], 200)

    def test_malformed_requests_are_400_with_error_envelope(self):
        for body in (b'{khong phai json', b'', json.dumps(dict(version=0, context=self.context)).encode()):
            status, _, content = self.call('/api/save', body)
            self.assertEqual(status, 400, body)
            self.assertIsInstance(content['error'], str)
        status, _, content = self.save(report(day='2026-13-45'), 0)
        self.assertEqual(status, 400)
        self.assertIn('error', content)

    # ---- Định tuyến và kiểm tra tham số -----------------------------------------------------------

    def test_unknown_routes_and_methods(self):
        self.assertEqual(self.call('/api/khong-co')[0], 404)
        self.assertEqual(self.call('/api/khong-co', {})[0], 404)
        self.assertEqual(self.call('/api/save', {'test': 'dữ liệu'}, method='PUT')[0], 501)
        # Hành vi hiện tại: tuyến POST dạng JSON so khớp cả chuỗi truy vấn, nên thêm ?x=1 là 404.
        # Chỉ /api/attachment-upload nhận tham số trên URL. Ghim lại để thay đổi có chủ đích.
        self.assertEqual(self.call('/api/save?x=1', dict(report=report(), version=0, context=self.context))[0], 404)

    def test_query_parameter_validation(self):
        for query in ('limit=0', 'limit=201', 'limit=abc', 'offset=-1', 'offset=abc'):
            status, _, body = self.call('/api/reports-page?' + query)
            self.assertEqual(status, 400, query)
            self.assertIn('Tham số', body['error'])
        self.assertEqual(self.call('/api/reports-page?limit=200&offset=0')[0], 200)
        for month in ('', 'month=abc', 'month=2026-13', 'month=2026-1'):
            query = '/api/export-month?context=' + self.context + ('&' + month if month else '')
            self.assertEqual(self.call(query)[0], 400, month)
        self.assertEqual(self.call('/api/report?id=2099-01-01_DAY')[0], 404)
        self.assertEqual(self.call('/api/attachment?hash=zz&context=' + self.context)[0], 400)
        status, _, page = self.call('/api/reports-page?limit=5')
        self.assertEqual(sorted(page), ['limit', 'offset', 'rows', 'total'])

    def test_context_bound_routes_reject_stale_context(self):
        self.assertEqual(self.save(report(), 0)[0], 200)
        stale = 'context-cu'
        self.assertEqual(self.call('/api/export?id=2026-11-02_DAY&context=' + stale)[0], 409)
        self.assertEqual(self.call('/api/export-month?month=2026-11&context=' + stale)[0], 409)
        self.assertEqual(self.call('/api/attachments-zip?id=2026-11-02_DAY&context=' + stale)[0], 409)
        self.assertEqual(self.call('/api/ships-add', dict(name='tàu thử', context=stale))[0], 409)
        self.assertEqual(self.call('/api/backup', dict(context=stale))[0], 409)
        self.assertEqual(self.call('/api/catalogs-save', dict(context=stale, text={}, digest=''))[0], 409)
        self.assertEqual(self.call('/api/attachment-upload?name=a.png&actor=A&context=' + stale, PNG)[0], 409)
        self.assertEqual(self.call('/api/protection-backup', dict(context=stale))[0], 409)
        # Cùng các tuyến đó với context đúng thì được phục vụ.
        self.assertEqual(self.call('/api/export?id=2026-11-02_DAY&context=' + self.context)[0], 200)

    # ---- Tệp đính kèm -----------------------------------------------------------------------------

    def test_attachment_upload_shapes_with_and_without_report(self):
        query = '/api/attachment-upload?name=anh.png&actor=' + urllib.parse.quote('Người nhập') + '&context=' + self.context
        status, _, loose = self.call(query, PNG)
        self.assertEqual(status, 200)
        self.assertEqual(sorted(loose), ['caption', 'hash', 'name'])
        self.assertEqual(len(loose['hash']), 64)
        self.assertEqual(self.save(report(), 0)[2]['version'], 1)
        status, _, attached = self.call(query + '&id=2026-11-02_DAY&version=1&caption=' + urllib.parse.quote('ghi chú'), PNG)
        self.assertEqual(status, 200)
        self.assertEqual(attached['attachment']['caption'], 'ghi chú')
        self.assertEqual(sorted(attached), ['added', 'attachment', 'report'])
        self.assertTrue(attached['added'])
        self.assertEqual(attached['report']['version'], 2)
        self.assertEqual(attached['attachment']['hash'], loose['hash'])
        again = self.call(query + '&id=2026-11-02_DAY&version=2', PNG)[2]
        self.assertFalse(again['added'], 'cùng tệp không đính kèm hai lần')
        self.assertEqual(self.call(query + '&id=2026-11-02_DAY&version=1', PNG)[0], 409)
        status, head, data = self.call('/api/attachment?hash=%s&context=%s' % (loose['hash'], self.context))
        self.assertEqual((status, head['Content-Type'], data), (200, 'image/png', PNG))

    # ---- Dạng lỗi thống nhất ----------------------------------------------------------------------

    def test_every_error_is_json_with_error_text(self):
        probes = [('/api/info', None, True), ('/api/khong-co', None, False), ('/api/report?id=x', None, False),
                  ('/api/reports-page?limit=0', None, False), ('/api/save', b'{', False)]
        for path, body, anonymous in probes:
            status, head, content = self.call(path, body, anonymous=anonymous)
            self.assertGreaterEqual(status, 400, path)
            self.assertIn('application/json', head['Content-Type'], path)
            self.assertIsInstance(content['error'], str, path)
            self.assertEqual(head['Cache-Control'], 'no-store', path)
            self.assertEqual(head['X-Content-Type-Options'], 'nosniff', path)


if __name__ == '__main__':
    unittest.main()
