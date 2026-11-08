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
 c.launch(pw);p=c.page
 def console(m):
  if m.text.startswith('NARROW_POINTER:'):r['pointerEvents'].append(json.loads(m.text.split(':',1)[1]))
 p.on('console',console);p.evaluate('()=>document.addEventListener("pointerdown",e=>{const b=e.target.closest("button");if(b)console.debug("NARROW_POINTER:"+JSON.stringify({text:b.innerText,id:b.dataset.id||null,isTrusted:e.isTrusted,layoutY:document.querySelector(".layout").scrollTop,windowY:scrollY}))})');r['homeNativeWheelY']=wheel();c.capture('home-scrolled-before-open');p.locator('button[data-id="2026-10-01_DAY"]').first.click();p.locator('#edit:not(.hide)').wait_for();p.wait_for_load_state('networkidle');r['existingOpening']=visibleActor();assert r['existingOpening']['fullyVisible'] and r['existingOpening']['layoutY']==0;assert any(x['id']=='2026-10-01_DAY' and x['isTrusted'] and x['layoutY']>200 for x in r['pointerEvents']);c.capture('existing-opening-first-input')
 r['beforeManualSaveY']=wheel();c.capture('manual-save-before-nonzero')
 with p.expect_response(lambda z:'/api/info' in z.url) as infoResponse:
  with p.expect_response(lambda z:'/api/save' in z.url and z.request.method=='POST') as saveResponse:p.get_by_role('button',name='Lưu nháp',exact=True).click()
 saveResponse.value.finished();infoResponse.value.finished();r['manualSaveStatus']=saveResponse.value.status;r['afterManualSaveY']=owner();assert r['manualSaveStatus']==200 and r['beforeManualSaveY']>200 and abs(r['afterManualSaveY']-r['beforeManualSaveY'])<=2;assert any(x['text']=='Lưu nháp' and x['isTrusted'] and x['layoutY']>200 for x in r['pointerEvents']);c.capture('manual-save-after-nonzero')
 p.locator('button[data-page="edit"]').click();p.locator('#newDate').fill('2033-01-01');p.locator('#newShift').select_option('DAY');c.click('Vào ca này');r['newOpening']=visibleActor();assert r['newOpening']['fullyVisible'] and r['newOpening']['layoutY']==0;p.locator('#actor').select_option('SYNTH ACTOR');p.keyboard.press('Alt+3')
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
