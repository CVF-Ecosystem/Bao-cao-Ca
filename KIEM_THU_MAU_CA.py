"""V1.7 reusable staffing templates and backward compatibility."""
import json
from pathlib import Path
import tempfile
import unittest

from LUU_TRU import Store
from QUAN_LY_DANH_MUC import Catalogs
from MAU_PHAN_CONG import default_templates, parse_templates
from NGHIEP_VU import AppError


class ShiftTemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.store=Store(self.root/'DU_LIEU'/'BAO_CAO_CA.db')
        self.cat=Catalogs(self.root/'DANH_MUC',self.store);self.cat.sync()

    def tearDown(self):self.temp.cleanup()

    def configure(self):
        editor=self.cat.editor_data();editor['people']='An\nBình\nChi\nDũng\n'
        profiles=default_templates()
        profiles['team1']=[dict(role='PHỤ TRÁCH CHUNG',people=['An']),dict(role='TALLY TÀU',people=['Bình','Chi'])]
        profiles['team2']=[dict(role='PHỤ TRÁCH CHUNG',people=['Bình'])]
        profiles['day']=[dict(role='TALLY TÀU',people=['Dũng'])]
        editor['staff_templates']=json.dumps(profiles)
        return self.cat.save(editor,editor['digest']),profiles

    def test_default_four_profiles_empty_and_file_created(self):
        self.assertEqual(self.cat.sync()['staff_templates'],default_templates())
        self.assertTrue((self.cat.directory/'MAU_PHAN_CONG.json').exists())

    def test_save_restart_and_roster_contains_template_people_not_day_people(self):
        data,profiles=self.configure()
        self.assertEqual(data['staff_templates'],profiles)
        self.assertEqual(data['teams'][0]['people'],['An','Bình','Chi'])
        self.assertNotIn('Dũng',data['teams'][0]['people'])
        self.assertEqual(data['teams'][1]['people'],['Bình'])
        again=Catalogs(self.cat.directory,self.store)
        self.assertEqual(again.sync()['staff_templates'],profiles)
        self.assertEqual(json.loads(self.store.meta('catalog_staff_templates')),profiles)

    def test_regular_catalog_save_preserves_templates_if_omitted(self):
        _,profiles=self.configure();editor=self.cat.editor_data();del editor['staff_templates']
        self.cat.save(editor,editor['digest'])
        self.assertEqual(self.cat.sync()['staff_templates'],profiles)

    def test_unknown_person_or_role_rejected_before_files_or_db_change(self):
        self.configure();before={p.name:p.read_bytes() for p in self.cat.directory.iterdir() if p.is_file()}
        meta=self.store.meta('catalog_staff_templates')
        for row in [dict(role='PHỤ TRÁCH CHUNG',people=['Unknown']),dict(role='Unknown role',people=['An'])]:
            editor=self.cat.editor_data();profiles=default_templates();profiles['day']=[row]
            editor['staff_templates']=json.dumps(profiles)
            with self.assertRaises(AppError):self.cat.save(editor,editor['digest'])
            self.assertEqual(before,{p.name:p.read_bytes() for p in self.cat.directory.iterdir() if p.is_file()})
            self.assertEqual(meta,self.store.meta('catalog_staff_templates'))

    def test_bad_format_duplicate_positions_and_duplicate_names_rejected(self):
        cases=['bad',json.dumps([]),json.dumps({'team1':[]})]
        for rows in [[dict(role='GATE',people=['An','an'])],
                     [dict(role='GATE',people=[]),dict(role='gate',people=[])],
                     [dict(role='GATE',people=['An; Bình'])],
                     [dict(role='',people=[])]]:
            data=default_templates();data['team1']=rows;cases.append(json.dumps(data))
        for text in cases:
            with self.subTest(text=text),self.assertRaises(AppError):parse_templates(text)

    def test_explicit_empty_role_is_retained_for_replacement_preview(self):
        data=default_templates();data['team1']=[dict(role='GATE',people=[])]
        self.assertEqual(parse_templates(json.dumps(data)),data)

    def test_external_invalid_template_falls_back_to_db_snapshot(self):
        _,profiles=self.configure()
        (self.cat.directory/'MAU_PHAN_CONG.json').write_text('invalid',encoding='utf-8')
        snapshot=self.cat.sync()
        self.assertEqual(snapshot['staff_templates'],profiles)
        self.assertIn('MAU_PHAN_CONG.json',self.cat.warning)

    def test_configuration_change_does_not_rewrite_old_report_or_history(self):
        report=dict(date='2026-11-04',shift='DAY',status='closed',actor='Old name',notes='',
                    staffing=[dict(role='PHỤ TRÁCH CHUNG',people='Old chief'),
                              dict(role='TALLY TÀU',people='Old A',ships=['A']),
                              dict(role='TALLY TÀU',people='Old B',ships=['B'])],jobs=[],handover=[])
        saved=self.store.save(report,0);history=self.store.history(saved['id'])
        self.configure()
        self.assertEqual(self.store.get(saved['id']),saved)
        self.assertEqual(self.store.history(saved['id']),history)

    def test_templates_go_with_backup_and_review_while_main_stays_unchanged(self):
        _,profiles=self.configure()
        report=dict(date='2026-11-04',shift='DAY',status='draft',actor='An',notes='',staffing=[],jobs=[],handover=[])
        saved=self.store.save(report,0)
        review=Store(self.store.backup(self.root/'review.db'),True)
        before=review.path.read_bytes()
        self.assertEqual(self.cat.snapshot(review)['staff_templates'],profiles)
        self.assertEqual(review.path.read_bytes(),before)
        edited=review.enable_corrections('An');payload=edited.get(saved['id']);payload['staffing']=[dict(role='PHỤ TRÁCH CHUNG',people='An')]
        edited.save(payload,1,'Áp dụng mẫu thử')
        self.assertEqual(self.store.get(saved['id'])['staffing'],[])
        self.store.apply_corrections(edited,[saved['id']])
        self.assertEqual(self.store.get(saved['id'])['staffing'][0]['people'],'An')

    def test_old_db_without_new_metadata_readonly_is_byte_identical(self):
        self.configure();path=self.store.backup(self.root/'old.db')
        with Store(path).connect() as c:c.execute("DELETE FROM meta WHERE key='catalog_staff_templates'")
        before=path.read_bytes();view=Store(path,True)
        self.assertEqual(self.cat.snapshot(view)['staff_templates'],default_templates())
        self.assertEqual(path.read_bytes(),before)

    def test_template_conflict_does_not_overwrite_external_change(self):
        self.configure();editor=self.cat.editor_data();path=self.cat.directory/'MAU_PHAN_CONG.json'
        path.write_text(json.dumps(default_templates()),encoding='utf-8')
        with self.assertRaises(AppError) as raised:self.cat.save(editor,editor['digest'])
        self.assertEqual(raised.exception.status,409)
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')),default_templates())

    def test_restore_catalog_files_from_db_keeps_custom_roles_jobs_and_templates(self):
        self.configure();editor=self.cat.editor_data()
        editor['roles']='PHỤ TRÁCH CHUNG\nTALLY TÀU\nVỊ TRÍ RIÊNG\n'
        editor['jobs']='CÔNG VIỆC RIÊNG\n'
        self.cat.save(editor,editor['digest'])
        restored=Catalogs(self.root/'new_install'/'DANH_MUC',self.store).sync()
        self.assertIn('VỊ TRÍ RIÊNG',restored['roles'])
        self.assertEqual(restored['jobs'],['CÔNG VIỆC RIÊNG'])
        self.assertEqual(restored['staff_templates'],self.cat.snapshot()['staff_templates'])

    def test_http_profiles_roundtrip_and_asset_served(self):
        import threading,urllib.request,http.cookiejar
        from MAY_CHU import make_server
        server=make_server(self.root/'HTTP'/'DU_LIEU')
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://'+server.app['host']
        client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def get(path):
            with client.open(base+path) as response:return response.read()
        def post(path,body):
            raw=body if isinstance(body,bytes) else json.dumps(body).encode()
            req=urllib.request.Request(base+path,data=raw,headers={'X-Ca-Request':'1'})
            with client.open(req) as response:return response.read()
        try:
            html=get('/?launch='+server.app['token']).decode()
            self.assertIn('/tai_nguyen/phan_cong_mau.js',html)
            self.assertIn('manageStaffTemplates()',get('/tai_nguyen/phan_cong_mau.js').decode())
            info=json.loads(get('/api/info'));editor=json.loads(get('/api/catalogs'))
            profiles=default_templates();profiles['team1']=[dict(role='PHỤ TRÁCH CHUNG',people=[info['people'][0]])]
            editor['staff_templates']=json.dumps(profiles)
            post('/api/catalogs-save',dict(context=info['context'],digest=editor['digest'],text=editor))
            self.assertEqual(json.loads(get('/api/info'))['staff_templates'],profiles)
            raw=post('/api/backup',dict(context=info['context']));post('/api/open-viewer',raw)
            view=json.loads(get('/api/info'))
            self.assertTrue(view['readonly']);self.assertEqual(view['staff_templates'],profiles)
        finally:
            server.shutdown();thread.join();server.server_close()

if __name__=='__main__':unittest.main(verbosity=2)
