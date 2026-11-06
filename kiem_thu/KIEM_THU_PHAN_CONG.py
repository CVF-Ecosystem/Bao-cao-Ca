"""V1.6 crew catalog and per-vessel assignments. No real data is touched."""
import copy
import io
import json
from pathlib import Path
import tempfile
import threading
import urllib.request
import urllib.error
import http.cookiejar
from MAY_CHU import make_server
import unittest
import zipfile
import xml.etree.ElementTree as ET

from LUU_TRU import Store
from NGHIEP_VU import AppError
from BAO_CAO_EXCEL import styled_xlsx, report_table
from QUAN_LY_DANH_MUC import Catalogs, default_teams, parse_teams


class AssignmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root/'DU_LIEU'/'BAO_CAO_CA.db')
        self.catalogs = Catalogs(self.root/'DANH_MUC', self.store)
        self.catalogs.sync()

    def tearDown(self): self.temp.cleanup()

    def configure(self):
        data = self.catalogs.editor_data()
        data['people'] = 'An\nBình\nChi\nDũng\n'
        teams = default_teams()
        teams[0].update(name='Tổ sáng', people=['An','Bình'])
        teams[1].update(name='Tổ chiều', people=['Chi'])
        teams[2].update(name='Tổ dự phòng', people=['Dũng','An'])
        data['teams'] = json.dumps(teams, ensure_ascii=False)
        return self.catalogs.save(data, data['digest'])

    def report(self):
        rows = [dict(role='PHỤ TRÁCH CHUNG',people='Chief')]
        for role in ('TALLY TÀU', 'XUẤT TÀU'):
            for ship, person in [('VESSEL A','An'),('VESSEL B','Bình'),('VESSEL C','Chi')]:
                rows.append(dict(role=role, ships=[ship], people=person))
        return dict(date='2026-11-05', shift='NIGHT', actor='An', status='closed',
                    notes='', staffing=rows, jobs=[], handover=[])

    def test_empty_teams_created_without_guessing_real_members(self):
        data = self.catalogs.sync()
        self.assertEqual(data['teams'], default_teams())
        self.assertTrue((self.catalogs.directory/'TO_NHAN_SU.json').is_file())

    def test_configure_three_teams_and_restart(self):
        expected = self.configure()
        again = Catalogs(self.catalogs.directory, self.store)
        self.assertEqual(again.sync()['teams'], expected['teams'])
        self.assertEqual(json.loads(self.store.meta('catalog_teams')), expected['teams'])
        self.assertEqual(len(list((self.catalogs.directory/'SAO_LUU').iterdir())), 1)

    def test_teams_travel_with_db_and_do_not_use_receiver_roster(self):
        data = self.configure()
        incoming = Store(self.store.backup(self.root/'mang_di.db'), True)
        snapshot = self.catalogs.snapshot(incoming)
        self.assertEqual(snapshot['teams'], data['teams'])
        with incoming.connect() as c:
            self.assertEqual(c.execute('PRAGMA query_only').fetchone()[0], 1)

    def test_invalid_json_and_unknown_names_preserve_all_catalogs(self):
        good = self.configure()
        for text in ('broken json', json.dumps([dict(id='team1',name='Only',people=[])])):
            editor = self.catalogs.editor_data(); editor['teams'] = text
            before = {p.name:p.read_bytes() for p in self.catalogs.directory.iterdir() if p.is_file()}
            with self.assertRaises(AppError): self.catalogs.save(editor, editor['digest'])
            self.assertEqual({p.name:p.read_bytes() for p in self.catalogs.directory.iterdir() if p.is_file()}, before)
        editor = self.catalogs.editor_data(); bad=copy.deepcopy(good['teams']);bad[0]['people']=['Unknown']
        editor['teams'] = json.dumps(bad)
        with self.assertRaises(AppError) as raised: self.catalogs.save(editor, editor['digest'])
        self.assertIn('Unknown', str(raised.exception))
        self.assertEqual(self.catalogs.sync()['teams'], good['teams'])

    def test_bad_external_team_file_falls_back_to_last_snapshot(self):
        good = self.configure()
        (self.catalogs.directory/'TO_NHAN_SU.json').write_text('invalid', encoding='utf-8')
        self.assertEqual(self.catalogs.sync()['teams'], good['teams'])
        self.assertIn('TO_NHAN_SU.json', self.catalogs.warning)

    def test_duplicate_labels_or_members_and_wrong_ids_rejected(self):
        for change in ('label', 'member', 'id', 'newline'):
            teams = default_teams()
            if change=='label': teams[1]['name']='Ca 1'
            if change=='member': teams[0]['people']=['An','an']
            if change=='id': teams[1]['id']='team1'
            if change=='newline': teams[0]['people']=['An\nBình']
            with self.subTest(change=change), self.assertRaises(AppError): parse_teams(json.dumps(teams))

    def test_concurrent_edit_to_team_file_rejected(self):
        self.configure(); editor = self.catalogs.editor_data()
        path = self.catalogs.directory/'TO_NHAN_SU.json'
        teams=json.loads(path.read_text(encoding='utf-8'));teams[0]['name']='External edit'
        path.write_text(json.dumps(teams), encoding='utf-8')
        with self.assertRaises(AppError) as raised: self.catalogs.save(editor, editor['digest'])
        self.assertEqual(raised.exception.status, 409)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8'))[0]['name'], 'External edit')

    def test_six_assignments_survive_save_backup_review_merge_and_excel(self):
        saved = self.store.save(self.report(), 0)
        self.assertEqual(saved['staffing'], self.report()['staffing'])
        view = Store(self.store.backup(self.root/'review.db'), True)
        review = view.enable_corrections('Reviewer')
        edit = review.get(saved['id'])
        edit['staffing'][2]['people'] = 'Dũng'
        review.save(edit, 1, 'Đổi người TALLY tàu B')
        self.assertEqual(self.store.correction_plan(review)[0]['state'], 'ready')
        self.store.apply_corrections(review, [saved['id']])
        merged = self.store.get(saved['id'])
        self.assertEqual(merged['staffing'][2]['people'], 'Dũng')
        self.assertEqual(merged['staffing'][5]['people'], 'Bình') # XUẤT TÀU B unchanged
        self.assertEqual(self.store.history(saved['id'])[-1]['payload']['staffing'], saved['staffing'])
        blob=styled_xlsx([('Bao cao ca',report_table(merged))], {'Bao cao ca':merged})
        ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            root=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            pairs=[]
            for row in root.findall('.//s:sheetData/s:row',ns):
                cells={''.join(filter(str.isalpha,c.get('r'))):''.join(c.itertext()) for c in row}
                if cells.get('A','').startswith(('TALLY TÀU','XUẤT TÀU')):pairs.append((cells['A'],cells.get('E','')))
        self.assertEqual(len(pairs),6)
        self.assertIn(('TALLY TÀU\nTàu: VESSEL B','Dũng'), pairs)
        self.assertIn(('XUẤT TÀU\nTàu: VESSEL B','Bình'), pairs)

    def test_team_changes_do_not_rewrite_historical_assignments(self):
        saved = self.store.save(self.report(), 0)
        self.configure()
        self.assertEqual(self.store.get(saved['id']), saved)
        self.assertEqual(len(self.store.history(saved['id'])), 1)

    def test_legacy_shared_vessels_preserved_until_user_edits(self):
        report = self.report()
        report['staffing'][1]['ships'] = ['VESSEL A', 'VESSEL B']
        report['staffing'][1]['people'] = 'An; Bình'
        saved = self.store.save(report, 0)
        self.catalogs.sync()
        self.assertEqual(self.store.get(saved['id'])['staffing'][1], report['staffing'][1])
        self.assertEqual(self.store.history(saved['id'])[0]['payload']['staffing'][1],report['staffing'][1])

    def test_old_db_without_teams_gets_safe_defaults_without_mutation(self):
        self.configure()
        old = self.store.backup(self.root/'old.db')
        with Store(old).connect() as c:c.execute("DELETE FROM meta WHERE key='catalog_teams'")
        before=old.read_bytes()
        snap=self.catalogs.snapshot(Store(old,True))
        self.assertEqual(snap['teams'],default_teams())
        self.assertEqual(old.read_bytes(), before)

    def test_http_team_configuration_and_readonly_source_snapshot(self):
        server=make_server(self.root/'HTTP'/'DU_LIEU')
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        base='http://'+server.app['host']
        client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def get(path):
            with client.open(base+path) as response:return response.read()
        def post(path,data):
            raw=data if isinstance(data,bytes) else json.dumps(data).encode()
            request=urllib.request.Request(base+path,data=raw,headers={'X-Ca-Request':'1'})
            with client.open(request) as response:return response.read()
        try:
            get('/?launch='+server.app['token'])
            info=json.loads(get('/api/info'))
            editor=json.loads(get('/api/catalogs'))
            editor['people']='An\nBình\nChi\n'
            teams=default_teams();teams[0]['people']=['An','Bình'];teams[1]['people']=['Chi']
            editor['teams']=json.dumps(teams)
            post('/api/catalogs-save',dict(context=info['context'],digest=editor['digest'],text=editor))
            self.assertEqual(json.loads(get('/api/info'))['teams'],teams)
            db=post('/api/backup',dict(context=info['context']))
            post('/api/open-viewer',db)
            snapshot=json.loads(get('/api/info'))
            self.assertTrue(snapshot['readonly'])
            self.assertEqual(snapshot['teams'],teams)
            with self.assertRaises(urllib.error.HTTPError):
                post('/api/catalogs-save',dict(context=snapshot['context'],digest=editor['digest'],text=editor))
        finally:
            server.shutdown();worker.join();server.server_close()

if __name__=='__main__':unittest.main(verbosity=2)
