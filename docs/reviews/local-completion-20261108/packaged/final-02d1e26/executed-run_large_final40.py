from pathlib import Path
import json,sys,time,hashlib,shutil,traceback
from playwright.sync_api import sync_playwright,expect
from consumer_driver import Consumer
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();B=ROOT/'.cvf/runtime/local-completion-20261108';RUN=B/'large-ui-d8de489';OUT=RUN/'final-02d1e26';OUT.mkdir(exist_ok=True);db=RUN/'DU_LIEU/BAO_CAO_CA.db';r={'freeBefore':shutil.disk_usage(RUN).free,'mainShaBefore':hashlib.sha256(db.read_bytes()).hexdigest()};assert r['freeBefore']-2*db.stat().st_size>5*1024**3;c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);c.startup_timeout=240;c.operation_timeout=180;c.exit_timeout=180;pw=sync_playwright().start()
try:
 print('FINAL40 LAUNCH',flush=True);start=time.perf_counter();c.launch(pw);r['startupSeconds']=time.perf_counter()-start;c.report('2031-01-01_DAY');c.page.keyboard.press('Alt+4');expect(c.page.locator('#tab_files')).to_have_attribute('aria-selected','true');expect(c.page.locator('#attachmentRows img')).to_have_count(40);start=time.perf_counter();r['observedDOM']=c.page.locator('#attachmentRows img').evaluate_all('async a=>{const decoded=await Promise.allSettled(a.map(x=>x.decode()));return {count:a.length,decoded:decoded.map(x=>x.status),images:a.map(x=>({name:x.alt,complete:x.complete,width:x.naturalWidth,height:x.naturalHeight})),allDecoded:decoded.every(x=>x.status==="fulfilled")}}');r['decodeObservationSeconds']=time.perf_counter()-start;assert r['observedDOM']['count']==40 and r['observedDOM']['allDecoded'] and all(x['complete'] and x['width']==240 and x['height']==140 for x in r['observedDOM']['images']);c.capture('final02-large-40-actualDOM');print('ACTUAL40DOM ALLTRUE',flush=True);start=time.perf_counter();c.exit();r['exitSeconds']=time.perf_counter()-start;r['mainShaAfter']=hashlib.sha256(db.read_bytes()).hexdigest();assert r['mainShaBefore']==r['mainShaAfter'];r['freeAfter']=shutil.disk_usage(RUN).free;assert r['freeAfter']>5*1024**3;r['status']='OBSERVED_PENDING_REVIEW'
except Exception as e:
 r['status']='FAILED';r['error']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception:pass
 c.save_proof();shutil.copyfile(RUN/'consumer-events.json',OUT/'consumer-events.json');shutil.copyfile(RUN/'final02-large-40-actualDOM.png',OUT/'actual40.png') if (RUN/'final02-large-40-actualDOM.png').exists() else None;(OUT/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');pw.stop();print(r.get('status'),flush=True);sys.exit(1 if r['status']=='FAILED' else 0)
