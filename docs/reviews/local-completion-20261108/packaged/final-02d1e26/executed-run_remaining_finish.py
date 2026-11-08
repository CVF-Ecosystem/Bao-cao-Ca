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
 c.launch(pw);p=c.page;c.report('2032-01-01_DAY');a=p.locator('#actor').bounding_box();r['existingOpeningActor']=a;check('U1 existingreport actor visible',a['y']>=0 and a['y']+a['height']<=657);c.capture('existing-opening');p.keyboard.press('Control+End');beforeScroll=p.evaluate('window.scrollY');c.click('Lưu nháp');afterScroll=p.evaluate('window.scrollY');r['sameEditorScroll']={'before':beforeScroll,'after':afterScroll};check('U1 manual sameeditor scroll preserved',abs(afterScroll-beforeScroll)<=2);p.locator('button[data-page="edit"]').click();c.click('Hủy');check('U1 cancel newopening scroll preserved',abs(p.evaluate('window.scrollY')-afterScroll)<=2);c.capture('same-editor-cancel-scroll');p.locator('button[title="Chọn 1 tàu cho dòng này"]').first.click();check('U4 ship search focused',p.locator('#shipSearch').evaluate('(e)=>e===document.activeElement'));p.locator('#shipSearch').fill('SYNTH');c.capture('ship-search-keyboard');p.keyboard.press('Escape')
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
