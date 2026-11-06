# -*- coding: utf-8 -*-
"""Đo hiệu năng trên DB giả lập. Chỉ dùng thư mục tạm, KHÔNG chạm DU_LIEU thật.

Dữ liệu được tạo qua Store.save (đúng đường ghi thật): payload thay đổi giữa các lần lưu,
nên số revision đúng bằng số lần lưu. Đo tách từng thành phần của sao lưu, đo khởi động
theo đúng đường gọi của main(), và đo độ trễ HTTP từ lúc gửi lưu đến lúc có phản hồi.

Ví dụ:
  python cong_cu\\DO_HIEU_NANG.py                       # cỡ vừa, vài phút
  python cong_cu\\DO_HIEU_NANG.py --profile nho         # kiểm tra nhanh script
  python cong_cu\\DO_HIEU_NANG.py --profile lon --external --disk-label "HDD 7200"
"""
import argparse
import datetime as dt
import hashlib
import http.cookiejar
import json
import os
import platform
import random
import shutil
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'ma_nguon'))
from BAO_VE_DU_LIEU import Protection, snapshot  # noqa: E402
from LUU_TRU import Store  # noqa: E402
from MAY_CHU import make_server  # noqa: E402
from NGHIEP_VU import ClosingConnection  # noqa: E402
from THIET_LAP import VERSION  # noqa: E402

# days = số ngày (mỗi ngày 2 ca); saves = số lần lưu mỗi ca; blobs/blob_mb = tệp đính kèm duy nhất.
PROFILES = {
    'nho': dict(days=10, saves=6, blobs=5, blob_mb=1),
    'vua': dict(days=120, saves=20, blobs=40, blob_mb=2),
    'lon': dict(days=1095, saves=40, blobs=200, blob_mb=2),  # gần cỡ baseline 1,15 GB; seed có thể mất nhiều phút
}


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return time.perf_counter() - start, result


def repeat(fn, count):
    """Trả (lần đầu, trung vị các lần sau). Không xóa được bộ nhớ đệm của hệ điều hành,
    nên lần đầu chỉ gần với 'nguội', không bảo đảm nguội hoàn toàn."""
    times = [timed(fn)[0] for _ in range(count)]
    return times[0], (statistics.median(times[1:]) if len(times) > 1 else None)


def make_report(rng, day, shift, version, closed, staff_pool):
    jobs = []
    for i in range(30):
        jobs.append(dict(name='DỜI DỌN %d' % i, detail='Bãi %s%d' % (rng.choice('ABCD'), rng.randint(1, 30)),
                         xn=rng.random() < .3, rtg=rng.random() < .3,
                         f20=rng.randint(0, 40), f40=rng.randint(0, 40), e20=rng.randint(0, 20),
                         e40=rng.choice([None, rng.randint(0, 20)]), ships=['TAU %d' % rng.randint(0, 9)]))
    staffing = [dict(role='PHỤ TRÁCH CHUNG', people=rng.choice(staff_pool))]
    staffing += [dict(role='VỊ TRÍ %d' % i, people='; '.join(rng.sample(staff_pool, 2))) for i in range(40)]
    return dict(date=day, shift=shift, actor='NGUOI NHAP', status='closed' if closed else 'draft',
                notes=('Ghi chú ca %d. ' % version) * rng.randint(20, 120), staffing=staffing, jobs=jobs,
                handover=[dict(text='Việc %d lần %d' % (i, version), done=rng.random() < .5) for i in range(5)])


def seed(store, profile, rng, say):
    staff_pool = ['NHAN VIEN %02d' % i for i in range(30)]
    blobs = []
    for i in range(profile['blobs']):
        raw = b'\xff\xd8\xff' + rng.randbytes(profile['blob_mb'] * 1024 * 1024)
        blobs.append(store.upload_attachment(raw, 'anh_%d.jpg' % i, 'NGUOI NHAP'))
    start = dt.date(2024, 1, 1)
    total = profile['days'] * 2
    for n in range(profile['days']):
        for shift in ('DAY', 'NIGHT'):
            day = (start + dt.timedelta(n)).isoformat()
            version = 0
            for k in range(profile['saves']):
                report = make_report(rng, day, shift, k, closed=(k == profile['saves'] - 1), staff_pool=staff_pool)
                if k == profile['saves'] - 1 and blobs:
                    report['attachments'] = [dict(blobs[(n * 2 + (shift == 'NIGHT')) % len(blobs)], caption='')]
                reason = 'Chốt ca' if report['status'] == 'closed' else ''
                version = store.save(report, version, reason)['version']
        if n % 20 == 19:
            say('  seed %d/%d ca' % ((n + 1) * 2, total))


def disk_info(directory):
    usage = shutil.disk_usage(directory)
    return '%.0f GB trống / %.0f GB' % (usage.free / 2**30, usage.total / 2**30)


def http_call(opener, base, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, headers={'X-Ca-Request': '1', 'Content-Type': 'application/json'})
    with opener.open(req, timeout=600) as response:
        return json.load(response)


def measure_http(server, rng, count):
    """Độ trễ /api/save: lưu thường (sao lưu bị hoãn theo giới hạn 5 phút) và chốt ca (sao lưu ngay)."""
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port, app = server.server_port, server.app
    base = 'http://127.0.0.1:%d' % port
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.open(base + '/?launch=' + app['token'], timeout=60).read()
    staff_pool = ['NHAN VIEN %02d' % i for i in range(30)]
    auto, close = [], []
    try:
        for i in range(count):
            day = (dt.date(2030, 1, 1) + dt.timedelta(i)).isoformat()
            version = 0
            for k in range(3):
                report = make_report(rng, day, 'DAY', k, False, staff_pool)
                took, saved = timed(lambda: http_call(opener, base, '/api/save',
                                                      dict(report=report, version=version, reason='', context=app['context'])))
                version = saved['version']
                auto.append(took)
            report = make_report(rng, day, 'DAY', 9, True, staff_pool)
            took, _ = timed(lambda: http_call(opener, base, '/api/save',
                                              dict(report=report, version=version, reason='Chốt ca', context=app['context'])))
            close.append(took)
    finally:
        server.shutdown()
        thread.join(30)
    return auto, close


def summary(values):
    return '%.2f s (nhỏ nhất %.2f, lớn nhất %.2f, n=%d)' % (statistics.median(values), min(values), max(values), len(values))


def main():
    for stream in (sys.stdout, sys.stderr):
        # Console thật hiển thị Unicode trực tiếp; khi ghi ra ống/tệp thì dùng UTF-8 để không mất dấu tiếng Việt.
        stream.reconfigure(errors='replace', **({} if stream.isatty() else {'encoding': 'utf-8'}))
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--profile', choices=sorted(PROFILES), default='vua')
    p.add_argument('--days', type=int)
    p.add_argument('--saves', type=int, help='số lần lưu mỗi ca')
    p.add_argument('--blobs', type=int)
    p.add_argument('--blob-mb', type=int)
    p.add_argument('--repeat', type=int, default=3, help='số lần lặp mỗi phép đo (>=2 để có số liệu "các lần sau")')
    p.add_argument('--http-reports', type=int, default=3, help='số ca chốt để đo độ trễ HTTP')
    p.add_argument('--external', action='store_true', help='bật nơi dự phòng ngoài (ổ/thư mục thứ hai trong thư mục tạm)')
    p.add_argument('--dir', help='thư mục làm việc (mặc định: thư mục tạm của hệ thống)')
    p.add_argument('--disk-label', default='không xác định', help='ghi loại ổ đĩa để lưu vào báo cáo (SSD/HDD/USB...)')
    p.add_argument('--keep', action='store_true', help='giữ lại thư mục làm việc')
    p.add_argument('--json', help='ghi kết quả ra file JSON')
    p.add_argument('--seed', type=int, default=20261106)
    args = p.parse_args()

    profile = dict(PROFILES[args.profile])
    for key, value in (('days', args.days), ('saves', args.saves), ('blobs', args.blobs), ('blob_mb', args.blob_mb)):
        if value is not None:
            profile[key] = value
    if min(profile.values()) < 1 or args.repeat < 1:
        p.error('các tham số phải >= 1')
    rng = random.Random(args.seed)
    work = Path(tempfile.mkdtemp(prefix='do_hieu_nang_', dir=args.dir))
    data_dir = work / 'DU_LIEU'
    say = lambda text: print(text, flush=True)  # noqa: E731
    result = dict(version=VERSION, profile=profile, disk_label=args.disk_label)
    try:
        say('Thư mục làm việc (xóa sau khi chạy nếu không dùng --keep): ' + str(work))
        data_dir.mkdir()
        db = data_dir / 'BAO_CAO_CA.db'
        store = Store(db)
        say('Tạo dữ liệu qua Store.save: %d ca x %d lần lưu, %d tệp x %d MB...'
            % (profile['days'] * 2, profile['saves'], profile['blobs'], profile['blob_mb']))
        took, _ = timed(lambda: seed(store, profile, rng, say))
        result['seed_s'] = round(took, 1)

        with store.connect() as c:
            result['data'] = dict(
                reports=c.execute('SELECT COUNT(*) FROM reports').fetchone()[0],
                revisions=c.execute('SELECT COUNT(*) FROM revisions').fetchone()[0],
                blobs=c.execute('SELECT COUNT(*) FROM attachment_blobs').fetchone()[0],
                avg_payload_kb=round(c.execute('SELECT AVG(LENGTH(payload)) FROM reports').fetchone()[0] / 1024, 1),
                revisions_mb=round(c.execute('SELECT SUM(LENGTH(payload)) FROM revisions').fetchone()[0] / 2**20),
                blobs_mb=round(c.execute('SELECT SUM(LENGTH(data)) FROM attachment_blobs').fetchone()[0] / 2**20),
                distinct_revision_payloads=c.execute('SELECT COUNT(DISTINCT payload) FROM revisions').fetchone()[0])
        result['data']['db_mb'] = round(db.stat().st_size / 2**20)

        protection = Protection(data_dir)
        protection.initialize()
        if args.external:
            outside = work / 'NGOAI'
            outside.mkdir()
            protection.set_external(str(outside))
        protection.backup()  # trạng thái thực tế: đã có ít nhất một bản sao trước khi khởi động

        say('Đo từng thành phần (lặp %d lần)...' % args.repeat)
        tmp = work / 'do_tam.db'
        ext = work / 'sao_ngoai.db'

        def copy_only():
            with sqlite3.connect(db.as_uri() + '?mode=ro', uri=True, factory=ClosingConnection) as src:
                with sqlite3.connect(str(tmp), factory=ClosingConnection) as dst:
                    src.backup(dst, pages=256)
                    dst.commit()
            tmp.unlink()

        def pragma(name):
            def run():
                with store.connect() as c:
                    return c.execute('PRAGMA ' + name).fetchall()
            return run

        def walk_json():
            with store.connect() as c:
                for row in c.execute('SELECT payload FROM reports'):
                    json.loads(row[0])
                for row in c.execute('SELECT payload FROM revisions'):
                    json.loads(row[0])

        def hash_blobs():
            with store.connect() as c:
                for row in c.execute('SELECT hash,data FROM attachment_blobs'):
                    hashlib.sha256(row['data']).hexdigest()

        def copy_external():
            shutil.copyfile(db, ext)
            ext.unlink()

        def full_snapshot():
            snapshot(db, tmp)
            tmp.unlink()

        parts = [('Chép DB bằng SQLite Backup API (không kiểm tra)', copy_only),
                 ('quick_check', pragma('quick_check')),
                 ('integrity_check', pragma('integrity_check')),
                 ('Duyệt JSON (reports + revisions)', walk_json),
                 ('Hash SHA-256 mọi tệp đính kèm', hash_blobs),
                 ('Chép file DB sang ổ ngoài (chỉ chép byte)', copy_external),
                 ('snapshot() đầy đủ = chép + kiểm tra + fsync', full_snapshot)]
        result['parts'] = {}
        for name, fn in parts:
            first, later = repeat(fn, args.repeat)
            result['parts'][name] = dict(first_s=round(first, 2), later_median_s=None if later is None else round(later, 2))

        say('Đo Protection.backup() (có%s dự phòng ngoài)...' % ('' if args.external else ' KHÔNG'))
        first, later = repeat(protection.backup, args.repeat)
        result['protection_backup'] = dict(external=args.external, first_s=round(first, 2),
                                           later_median_s=None if later is None else round(later, 2))

        say('Đo khởi động theo đường gọi của main()...')
        phases = {}
        protection = Protection(data_dir)
        phases['guard_startup (main)'], startup_check = timed(protection.guard_startup)
        phases['needs_adoption (main)'] = timed(lambda: protection.needs_adoption(startup_check))[0]
        took, server = timed(lambda: make_server(data_dir, startup_check=startup_check))
        phases['make_server (mở Store, sao lưu đầu)'] = took
        result['startup'] = {k: round(v, 1) for k, v in phases.items()}
        result['startup']['TỔNG'] = round(sum(phases.values()), 1)

        say('Đo độ trễ HTTP /api/save (%d ca)...' % args.http_reports)
        auto, close = measure_http(server, rng, args.http_reports)
        server.server_close()
        result['http_save_s'] = dict(auto_median=round(statistics.median(auto), 2), auto_max=round(max(auto), 2),
                                     close_median=round(statistics.median(close), 2), close_max=round(max(close), 2))

        started = time.perf_counter()
        rows = store.list({'q': 'tau 3'})
        result['search_s'] = dict(seconds=round(time.perf_counter() - started, 2), matches=len(rows))

        print()
        print('=' * 78)
        print('KẾT QUẢ ĐO — Sổ báo cáo ca %s' % VERSION)
        print('=' * 78)
        print('Máy: %s | Python %s | CPU %s luồng' % (platform.platform(), platform.python_version(), os.cpu_count()))
        print('Loại ổ đĩa (do người chạy khai): %s | %s' % (args.disk_label, disk_info(work)))
        print('Dự phòng ngoài: %s | Lặp mỗi phép đo: %d | seed ngẫu nhiên: %d' % ('có' if args.external else 'không', args.repeat, args.seed))
        d = result['data']
        print('Dữ liệu: %d ca, %d revision (%d payload khác nhau), %d tệp duy nhất, DB %d MB'
              % (d['reports'], d['revisions'], d['distinct_revision_payloads'], d['blobs'], d['db_mb']))
        print('  revisions %d MB | tệp đính kèm %d MB | payload trung bình %.1f KB/ca | tạo dữ liệu %.0f s'
              % (d['revisions_mb'], d['blobs_mb'], d['avg_payload_kb'], result['seed_s']))
        print()
        print('%-58s %8s %12s' % ('Thành phần', 'Lần 1', 'Các lần sau'))
        for name, v in result['parts'].items():
            later = '-' if v['later_median_s'] is None else '%.2f s' % v['later_median_s']
            print('%-58s %6.2f s %12s' % (name, v['first_s'], later))
        b = result['protection_backup']
        later = '-' if b['later_median_s'] is None else '%.2f s' % b['later_median_s']
        print('%-58s %6.2f s %12s' % ('Protection.backup() toàn bộ', b['first_s'], later))
        print()
        print('Khởi động (theo đường gọi của main):')
        for name, value in result['startup'].items():
            print('  %-62s %6.1f s' % (name, value))
        print()
        print('Độ trễ HTTP /api/save (từ lúc gửi đến lúc nhận phản hồi):')
        print('  Lưu thường (sao lưu bị hoãn): trung vị %.2f s, lớn nhất %.2f s' % (result['http_save_s']['auto_median'], result['http_save_s']['auto_max']))
        print('  Chốt ca (sao lưu ngay)      : trung vị %.2f s, lớn nhất %.2f s' % (result['http_save_s']['close_median'], result['http_save_s']['close_max']))
        print('Tìm kiếm toàn văn "tau 3": %.2f s, %d ca' % (result['search_s']['seconds'], result['search_s']['matches']))
        print()
        print('Lưu ý: lần 1 chỉ gần với trạng thái "nguội", không xóa được bộ nhớ đệm hệ điều hành.')
        print('Số đo chỉ có giá trị so sánh trước/sau trên cùng máy, cùng tham số và cùng loại ổ.')
        if args.json:
            Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print('Đã ghi JSON: ' + args.json)
    finally:
        if args.keep:
            print('Giữ lại: ' + str(work))
        else:
            shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
