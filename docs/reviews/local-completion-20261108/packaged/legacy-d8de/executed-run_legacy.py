from pathlib import Path
import sqlite3,json,hashlib,sys
from playwright.sync_api import sync_playwright
from consumer_driver import Consumer
ROOT=Path('.').resolve();BASE=ROOT/'.cvf/runtime/local-completion-20261108';records=[];pw=sync_playwright().start()
def state(path):
 with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as db:
  return {'schema':db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0],'reports':db.execute('SELECT id,version,payload FROM reports ORDER BY id').fetchall(),'revisions':db.execute('SELECT report_id,version,actor,reason,payload FROM revisions ORDER BY report_id,version').fetchall()}
try:
 for variant in ['1','2','3','interrupted']:
  run=BASE/'legacy-consumer-d8de489'/variant;c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',run);record={'variant':variant,'setup':'Terra synthetic legacy fixture; interrupted uses preconstructed injected-fault state, not naturalEXEfaulttrigger'};records.append(record);db=c.data/'BAO_CAO_CA.db';record['before']=state(db);original=hashlib.sha256(db.read_bytes()).hexdigest()
  try:
   c.launch(pw);c.page.get_by_role('button',name='Xem kế hoạch nâng cấp',exact=True).wait_for();c.capture('restricted-start')
   if variant=='interrupted':
    c.click('Phục hồi từ bản sao đã giữ');c.click('Kiểm tra / phục hồi');c.capture('recovery-preview-cancel');c.click('Hủy');c.page.wait_for_load_state('networkidle');assert hashlib.sha256(db.read_bytes()).hexdigest()==original;c.recover_known();record['afterRestore']=state(db);assert record['afterRestore']['schema']=='1';c.exit();c.save_proof();c.launch(pw);c.page.get_by_role('button',name='Xem kế hoạch nâng cấp',exact=True).wait_for();record['restartedStillRestricted']=True
   else:
    c.click('Xem kế hoạch nâng cấp');c.capture('preview-cancel');c.click('Hủy');c.page.wait_for_load_state('networkidle');assert hashlib.sha256(db.read_bytes()).hexdigest()==original;record['cancelDBUnchanged']=True
   c.upgrade();record['afterUpgrade']=state(db);assert record['afterUpgrade']['schema']=='4';assert record['afterUpgrade']['reports']==record['before']['reports'];assert record['afterUpgrade']['revisions']==record['before']['revisions'];c.exit();c.save_proof();firstPID=c.process.pid;c.launch(pw);assert c.process.pid!=firstPID;c.report('2026-11-08_DAY');c.page.keyboard.press('Alt+3');c.page.locator('#tab_notes[aria-selected="true"]').wait_for();assert c.page.locator('#notes').input_value()=='Synthetic baseline '+variant;c.capture('report-after-restart');c.exit();c.save_proof();record['status']='OBSERVED_PENDING_REVIEW'
  except Exception as e:
   record['status']='FAILED';record['error']=type(e).__name__+': '+str(e)
   try:c.capture('failure')
   except Exception:pass
   raise
  finally:
   c.save_proof();(BASE/'legacy-consumer-d8de489/results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   if c.process and c.process.poll() is None:
    try:c.exit()
    except Exception:pass
finally:pw.stop()
