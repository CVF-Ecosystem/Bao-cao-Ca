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
 c.launch(pw);p=c.page
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
