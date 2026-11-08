from pathlib import Path
import json,sys,shutil,hashlib,sqlite3,time,traceback
from playwright.sync_api import sync_playwright,expect
from consumer_driver import Consumer
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();B=ROOT/'.cvf/runtime/local-completion-20261108';RUN=B/'remaining-final';RUN.mkdir(exist_ok=True);cat=RUN/'DANH_MUC';cat.mkdir(exist_ok=True);people=cat/'NHAN_VIEN.txt'
if not people.exists():people.write_text('SYNTH ACTOR\nSYNTH CHIEF 1\nSYNTH REVIEWER\nPNI Đã Có\n',encoding='utf-8')
external=RUN/'EXTERNAL_LOCAL_FOLDER';external.mkdir(exist_ok=True);c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);pw=sync_playwright().start();r={'checks':[],'limitations':['browser fileinput exercised; nativeOSfiledialog NOT_TESTED','external folder samehost, not independentdevice/cloudproof']}
def check(label,value):
 assert value,label
 r['checks'].append(label);(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(label,flush=True)
def observe_save(page,notes,status=200):
 with page.expect_response(lambda z:'/api/save' in z.url and z.request.method=='POST') as response:
  page.locator('#notes').fill(notes);page.keyboard.press('Control+s')
 value=response.value;value.finished();check('actual save response '+str(status),value.status==status)
def note():
 with sqlite3.connect((c.data/'BAO_CAO_CA.db').resolve().as_uri()+'?mode=ro',uri=True) as x:return json.loads(x.execute("SELECT payload FROM reports WHERE id='2032-01-01_DAY'").fetchone()[0])['notes']
try:
 c.launch(pw);p=c.page;p.locator('.skipLink').focus();p.keyboard.press('Enter');check('U4 skip focuses main',p.locator('#mainContent').evaluate('(e)=>e===document.activeElement'));c.capture('skip-main')
 c.menu('Bảo vệ dữ liệu / Khôi phục');expect(p.locator('#modalBody')).to_contain_text('90 ngày');p.locator('#modalBody .modalHead').wait_for();p.locator('#modalBody .modalActions').wait_for();p.locator('#modalBody').evaluate('(e)=>e.scrollTop=e.scrollHeight');r['protectionStickyBounds']={k:p.locator('#modalBody .'+k).bounding_box() for k in ['modalHead','modalActions']};check('U10 protection sticky visible',all(v and v['y']>=0 and v['y']+v['height']<=657 for v in r['protectionStickyBounds'].values()));c.capture('protection-sticky');p.get_by_role('button',name='Kiểm tra / khôi phục',exact=True).first.click();expect(p.locator('#modalBody')).to_contain_text('Chưa có báo cáo nào');check('U12 empty restore explicit',True);c.capture('empty-restore-preview');p.keyboard.press('Escape')
 c.menu('Bảo vệ dữ liệu / Khôi phục');p.locator('#backupDirectory').fill(str(external));c.click('Lưu nơi dự phòng')
 with p.expect_response(lambda z:'/api/protection-backup' in z.url) as backupResponse:c.click('Sao lưu ngay')
 backupResponse.value.finished();expect(p.locator('#modalBody')).to_contain_text('Kiểm tra đầy đủ gần nhất bên ngoài');check('external folder actual backup files',len(list(external.glob('*.db')))>0);r['externalFiles']=[{'name':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in external.glob('*.db')];c.capture('external-full-success');p.keyboard.press('Escape')
 fixture=B.parent/'personnel-import-20261108/native-preparation/PNI_SYNTHETIC.xlsx';before=hashlib.sha256(people.read_bytes()).hexdigest()
 def pni():
  c.menu('Danh mục nhân sự / công việc');c.click('Nhập nhân viên Excel');p.locator('#personnelFile').set_input_files(str(fixture));p.locator('#personnelHeader').wait_for();c.click('Xem trước');expect(p.locator('#personnelPlan')).to_contain_text('Mới:')
 pni();c.capture('pni-preview-cancel');p.keyboard.press('Escape');p.locator('#modal').wait_for(state='hidden');check('PNI Escape unchanged catalog',hashlib.sha256(people.read_bytes()).hexdigest()==before);pni();p.locator('#personnelPlan tbody input').first.check();expect(p.locator('#personnelPlan')).to_contain_text('Đã loại: 1');c.capture('pni-excluded-existing');c.click('Xác nhận thêm nhân viên');p.locator('#modal').wait_for(state='hidden');check('PNI actual two names persisted',all(n in people.read_text(encoding='utf-8') for n in ['PNI Người Mới A','PNI Người Mới B']));pni();expect(p.locator('#personnelPlan')).to_contain_text('Mới: 0');check('PNI repeat noop confirm absent',p.get_by_role('button',name='Xác nhận thêm nhân viên',exact=True).count()==0);c.capture('pni-repeat-noop');p.keyboard.press('Escape')
 p.locator('button[data-page="edit"]').click();p.locator('#newDate').fill('2032-01-01');p.locator('#newShift').select_option('DAY');c.click('Vào ca này');a=p.locator('#actor').bounding_box();r['newOpeningActor']=a;check('U1 newshift actor visible',a['y']>=0 and a['y']+a['height']<=657);p.locator('#actor').select_option('PNI Người Mới B');p.get_by_role('button',name='Chọn người',exact=True).first.click();p.locator('#modalBody .modalHead').wait_for();p.locator('#modalBody .modalActions').wait_for();p.locator('#modalBody').evaluate('(e)=>e.scrollTop=e.scrollHeight');r['staffStickyBounds']={k:p.locator('#modalBody .'+k).bounding_box() for k in ['modalHead','modalActions']};check('U10 staffing sticky visible',all(v and v['y']>=0 and v['y']+v['height']<=657 for v in r['staffStickyBounds'].values()));c.capture('staffing-sticky');p.locator('#peopleChoices input[value="PNI Người Mới A"]').check();c.click('Dùng các tên đã chọn');check('newPNI person picker applied',p.locator('[data-staff-people]').first.input_value()=='PNI Người Mới A');p.get_by_role('button',name='Chọn 1 tàu',exact=True).first.click();check('U4 ship search focused',p.locator('#shipSearch').evaluate('(e)=>e===document.activeElement'));p.locator('#shipSearch').fill('SYNTH');c.capture('ship-search-keyboard');p.keyboard.press('Escape')
 for key,tab in [('1','staff'),('2','jobs'),('3','notes'),('4','files')]:
  p.keyboard.press('Alt+'+key);expect(p.locator('#tab_'+tab)).to_have_attribute('aria-selected','true')
 check('U4 all4keyboard tabs actual',True);p.keyboard.press('Alt+3');observe_save(p,'SYNTH INITIAL');expect(p.locator('#saveState')).to_contain_text('Đã lưu lúc');c.capture('fresh-report-saved');p2=c.context.new_page();p2.goto(c.base);c.page=p2;c.report('2032-01-01_DAY');p2.keyboard.press('Alt+3');observe_save(p2,'SYNTH WINNER');expect(p2.locator('#saveState')).to_contain_text('Đã lưu lúc');c.page=p;observe_save(p,'SYNTH UNSAVED LOCAL',409);expect(p.get_by_role('button',name='Tải bản mới, giữ ghi chú chưa lưu',exact=True)).to_be_visible();c.capture('conflict-before-keep');c.click('Tải bản mới, giữ ghi chú chưa lưu');expect(p.locator('#notes')).to_have_value('SYNTH UNSAVED LOCAL');expect(p.locator('#saveState')).to_contain_text('chưa được lưu');p.wait_for_timeout(2000);check('U6 keep local notes/no winner overwrite',note()=='SYNTH WINNER');c.capture('conflict-kept-unsaved');p2.close();c.report('2032-01-01_DAY');p.keyboard.press('Alt+3');expect(p.locator('#notes')).to_have_value('SYNTH WINNER')
 portable=c.download(lambda:c.menu('Sao lưu mang đi'),'fresh-portable.db');c.open_viewer(portable);c.enable_corrections();c.correct_note('2032-01-01_DAY','SYNTH REVIEWER CHANGE');export=c.download(lambda:c.click('Xuất DB đã bổ sung'),'fresh-reviewer.db');c.click('Về DB chính của máy')
 with p.expect_file_chooser() as fc:c.menu('Nhập bổ sung từ DB')
 fc.value.set_files(str(export));p.get_by_role('button',name='Xem hai bản',exact=True).first.click();expect(p.locator('.revisionDiff')).to_contain_text('SYNTH WINNER');expect(p.locator('.revisionDiff')).to_contain_text('SYNTH REVIEWER CHANGE');check('U11 exact correction before-after shared diff',p.locator('#modalBody').get_by_role('button',name='In / Lưu PDF',exact=True).count()==0);c.capture('correction-exact-diff');p.keyboard.press('Escape');c.exit();pid=c.process.pid;c.launch(pw);p=c.page;c.report('2032-01-01_DAY');p.keyboard.press('Alt+3');expect(p.locator('#notes')).to_have_value('SYNTH WINNER');check('fresh exit/restart persisted',c.process.pid!=pid);c.capture('fresh-reopened');c.exit();r['status']='OBSERVED_PENDING_REVIEW'
except Exception as e:
 r['status']='FAILED';r['error']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
 try:c.capture('failure')
 except Exception:pass
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception:pass
 c.save_proof();(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');pw.stop();sys.exit(1 if r['status']=='FAILED' else 0)
