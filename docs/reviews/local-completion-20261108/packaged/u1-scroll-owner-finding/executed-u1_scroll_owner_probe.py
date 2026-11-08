from pathlib import Path
import json,sys,traceback
from playwright.sync_api import sync_playwright,expect
from consumer_driver import Consumer
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();RUN=ROOT/'.cvf/runtime/local-completion-20261108/remaining-final';OUT=RUN/'u1-owner-probe';OUT.mkdir(exist_ok=True);c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);pw=sync_playwright().start();r={}
def scrolls():return c.page.evaluate('()=>({windowY:scrollY,documentY:document.scrollingElement.scrollTop,layoutY:document.querySelector(".layout").scrollTop,mainY:document.querySelector("main").scrollTop})')
try:
 c.launch(pw);p=c.page;c.report('2032-01-01_DAY');p.mouse.move(1200,400);p.mouse.wheel(0,1400);p.wait_for_timeout(150);r['editorAfterWheel']=scrolls();c.capture('u1-editor-native-scroll');p.locator('button[data-page="home"]').click();p.wait_for_load_state('networkidle');r['homeBeforeOpening']=scrolls()
 def console(m):
  if m.text.startswith('OPEN_SCROLL:'):r['actualOpeningPointerdown']=json.loads(m.text.split(':',1)[1])
 p.on('console',console);p.evaluate('()=>document.addEventListener("pointerdown",e=>{const b=e.target.closest("button[data-id]");if(b)console.debug("OPEN_SCROLL:"+JSON.stringify({id:b.dataset.id,isTrusted:e.isTrusted,windowY:scrollY,layoutY:document.querySelector(".layout").scrollTop}))})');p.locator('button[data-id="2032-01-01_DAY"]').first.click();p.locator('#edit:not(.hide)').wait_for();p.wait_for_load_state('networkidle');r['afterOpening']=scrolls();r['actorBounds']=p.locator('#actor').bounding_box();r['viewport']={'width':1366,'height':657};r['actorVisible']=r['actorBounds']['y']>=0 and r['actorBounds']['y']+r['actorBounds']['height']<=657;c.capture('u1-existing-from-nonzero');c.exit();r['status']='OBSERVED_PENDING_REVIEW'
except Exception as e:r['error']=str(e);r['traceback']=traceback.format_exc();r['status']='FAILED'
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception:pass
 c.save_proof();(OUT/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=False));pw.stop()
