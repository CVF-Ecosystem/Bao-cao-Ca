from pathlib import Path
import json,sys,shutil,traceback
from playwright.sync_api import sync_playwright,expect
from consumer_driver import Consumer
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();B=ROOT/'.cvf/runtime/local-completion-20261108';RUN=B/'narrow-final-8e641d3';RUN.mkdir(exist_ok=True)
if not (RUN/'DU_LIEU').exists():shutil.copytree(B/'consumer-main-0f6ed11/DU_LIEU',RUN/'DU_LIEU')
if not (RUN/'DANH_MUC').exists():shutil.copytree(B/'consumer-main-0f6ed11/DANH_MUC',RUN/'DANH_MUC')
c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);pw=sync_playwright().start();r={'pointerEvents':[]}
def owner():return c.page.locator('.layout').evaluate('(e)=>e.scrollTop')
def wheel():
 c.page.mouse.move(1100,450);c.page.mouse.wheel(0,2000)
 for _ in range(10):
  y=owner()
  if y>200:return y
  c.page.wait_for_timeout(50)
 raise AssertionError('native wheel did not create nonzero layout>200')
def visibleActor():
 box=c.page.locator('#actor').bounding_box();return {'bounds':box,'fullyVisible':box['y']>=0 and box['y']+box['height']<=657,'layoutY':owner()}
try:
 c.launch(pw);p=c.page;c.report('2026-10-01_DAY');r['beforeNewOpeningY']=wheel()
 p.locator('button[data-page="edit"]').click();p.locator('#newDate').fill('2033-01-01');p.locator('#newShift').select_option('DAY');c.click('Vào ca này');expect(p.locator('#edit .sectionno').first).to_contain_text('01/01/2033');r['newOpening']=visibleActor();assert r['newOpening']['fullyVisible'] and r['newOpening']['layoutY']==0;p.locator('#actor').select_option('SYNTH ACTOR');p.keyboard.press('Alt+3')
 with p.expect_response(lambda z:'/api/save' in z.url and z.request.method=='POST') as response:p.locator('#notes').fill('NARROW FINAL SAVE ORACLE');p.keyboard.press('Control+s')
 response.value.finished();expect(p.locator('#saveState')).to_contain_text('Đã lưu lúc');c.capture('new-report-saved');c.exit();first=c.process.pid;c.launch(pw);p=c.page;c.report('2033-01-01_DAY');p.keyboard.press('Alt+3');expect(p.locator('#notes')).to_have_value('NARROW FINAL SAVE ORACLE');r['reopenedNewPID']=c.process.pid!=first;assert r['reopenedNewPID'];c.capture('reopened-saved-report');c.exit();r['status']='OBSERVED_PENDING_INDEPENDENT_REVIEW'
except Exception as e:
 r['status']='FAILED';r['error']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
 try:c.capture('failure')
 except Exception:pass
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception:pass
 c.save_proof();(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');pw.stop();print(json.dumps(r,ensure_ascii=False),flush=True);sys.exit(1 if r['status']=='FAILED' else 0)
