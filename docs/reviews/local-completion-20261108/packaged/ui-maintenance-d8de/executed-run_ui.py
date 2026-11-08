from pathlib import Path
import json,sys,shutil,sqlite3,time,hashlib,traceback
from playwright.sync_api import sync_playwright
from consumer_driver import Consumer,readonly_db_oracle
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();B=ROOT/'.cvf/runtime/local-completion-20261108';RUN=B/'ui-d8de489';RUN.mkdir(exist_ok=True)
if not (RUN/'DU_LIEU').exists():shutil.copytree(B/'consumer-main-0f6ed11/DU_LIEU',RUN/'DU_LIEU')
c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);r={'checks':[]};pw=sync_playwright().start()
def check(label,value):
 assert value,label
 r['checks'].append(label);(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(label,flush=True)
try:
 c.launch(pw);p=c.page;check('U7 server version', '1.10.0' in p.locator('#appVersion').inner_text());c.report('2026-10-01_DAY');a=p.locator('#actor').bounding_box();r['U1OpeningExistingActorBounds']=a;r['U1OpeningExistingVisible']=a['y']>=0 and a['y']+a['height']<657;c.capture('opening-existing-scroll');p.keyboard.press('Control+Home');c.capture('compact-first-input-after-explicit-home');p.keyboard.press('Alt+1');p.locator('#tab_staff[aria-selected="true"]').wait_for()
 p.locator('[data-staff-people]').first.fill('');c.click('Chốt ca');check('U3 missing chief focused/no confirm',p.locator('#tab_staff').get_attribute('aria-selected')=='true' and len(c.dialogs)==0);c.capture('chief-validation');p.locator('[data-staff-people]').first.fill('SYNTH CHIEF 1')
 p.keyboard.press('Alt+2');p.locator('#tab_jobs[aria-selected="true"]').wait_for();num=p.locator('[data-job="0"][data-key="f20"]');num.fill('1.5');p.keyboard.press('Control+s');check('U2 decimal invalid',num.get_attribute('aria-invalid')=='true');check('U2 exact job-column feedback','F20' in p.locator('#toast').inner_text());c.capture('invalid-quantity');num.fill('1');p.keyboard.press('Control+s');p.locator('#saveState').get_by_text('Đã lưu lúc',exact=False).wait_for()
 p.keyboard.press('Alt+3');p.locator('#notes').fill('SAFE <script>alert(1)</script> & first');p.keyboard.press('Control+s');p.locator('#saveState').get_by_text('Đã lưu lúc',exact=False).wait_for();p.locator('#notes').fill('SAFE <script>alert(1)</script> & second');p.keyboard.press('Control+s');p.locator('#saveState').get_by_text('Đã lưu lúc',exact=False).wait_for();c.click('Lịch sử sửa');c.capture('history');p.get_by_role('button',name='Xem thay đổi',exact=True).first.click();check('U5 escaped adjacent diff',p.locator('.revisionDiff').count()==1 and '<script>' in p.locator('.revisionDiff').inner_text() and p.locator('.revisionDiff script').count()==0);check('U5 no redundant print control',p.locator('#modalBody').get_by_role('button',name='In / Lưu PDF',exact=True).count()==0);c.capture('history-diff');p.keyboard.press('Escape');check('U4 Escape closes history',p.locator('#modal').get_attribute('class').find('hide')>=0)
 c.menu('Danh mục nhân sự / công việc');p.locator('#modalBody .modalHead').wait_for();p.locator('#modalBody .modalActions').wait_for();p.locator('#modalBody').evaluate('(e)=>e.scrollTop=e.scrollHeight');head=p.locator('#modalBody .modalHead').bounding_box();actions=p.locator('#modalBody .modalActions').bounding_box();check('U10 catalog sticky header/actions',head is not None and actions is not None and head['y']>=0 and actions['y']+actions['height']<=657);c.capture('catalog-sticky');p.keyboard.press('Escape')
 c.menu('Danh sách tàu');p.locator('#catalogShipName').fill('SYNTH HIDDEN SHIP');c.click('Thêm tàu');p.locator('#modalBody p').filter(has_text='SYNTH HIDDEN SHIP').wait_for();row=p.locator('#modalBody p').filter(has_text='SYNTH HIDDEN SHIP');row.get_by_role('button',name='Ẩn',exact=True).click();row.wait_for(state='hidden');check('U9 hidden ship removed',p.locator('#modalBody p').filter(has_text='SYNTH HIDDEN SHIP').count()==0);p.locator('#catalogShipName').fill('SYNTH HIDDEN SHIP');c.click('Thêm tàu');p.locator('#modalBody p').filter(has_text='SYNTH HIDDEN SHIP').wait_for();check('U9 explicit add reactivates',p.locator('#modalBody p').filter(has_text='SYNTH HIDDEN SHIP').count()==1);c.capture('ship-reactivated');p.keyboard.press('Escape')
 c.menu('Bảo vệ dữ liệu / Khôi phục');check('quarterly restore reminder visible','90 ngày' in p.locator('#modalBody').inner_text());c.capture('protection-status');c.click('Dọn bản chỉ xem cũ');c.capture('maintenance-viewer-preview');p.keyboard.press('Escape');check('maintenance Escape closes preview', 'hide' in p.locator('#modal').get_attribute('class'));c.menu('Bảo vệ dữ liệu / Khôi phục');c.click('Dọn tệp không tham chiếu');c.capture('maintenance-orphan-preview');c.click('Hủy');c.menu('Bảo vệ dữ liệu / Khôi phục');c.click('Khôi phục thử định kỳ');c.capture('restore-drill-preview');c.click('Chạy khôi phục thử');p.locator('#modal.hide').wait_for(timeout=60000);check('restore drill actual completed UI',True);c.menu('Bảo vệ dữ liệu / Khôi phục');check('restore drill status updated','Chưa thực hiện' not in p.locator('#modalBody').inner_text().split('Khôi phục thử gần nhất:')[1].split('</p>')[0][:100]);c.capture('restore-drill-completed');p.keyboard.press('Escape')
 c.report('2026-10-01_DAY');p.keyboard.press('Alt+4');
 with p.expect_file_chooser() as fc:c.click('＋ Thêm tệp')
 fc.value.set_files(str(B/'consumer-prep/valid-native-report-sample.pdf'));p.locator('#uploadState').get_by_text('Đã lưu ngay 1 tệp',exact=False).wait_for(timeout=60000);check('valid PDF actual upload',p.locator('#attachmentRows .fileIcon').inner_text()=='PDF');c.capture('valid-pdf-attachment');c.download(lambda:c.click('Tải tất cả tệp'),'valid-pdf.zip');c.exit();c.save_proof();r['status']='OBSERVED_PENDING_REVIEW'
except Exception as e:
 r['status']='FAILED';r['error']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
 try:c.capture('failure')
 except Exception:pass
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception:pass
 c.save_proof();(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');pw.stop()
 sys.exit(1 if r['status']=='FAILED' else 0)
