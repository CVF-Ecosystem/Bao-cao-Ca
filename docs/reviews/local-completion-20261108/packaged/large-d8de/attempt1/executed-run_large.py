from pathlib import Path
import json,sys,time,shutil,sqlite3,hashlib,traceback
from playwright.sync_api import sync_playwright
from consumer_driver import Consumer
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();B=ROOT/'.cvf/runtime/local-completion-20261108';RUN=B/'large-ui-d8de489';c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);c.startup_timeout=240;c.operation_timeout=180;c.exit_timeout=180;pw=sync_playwright().start();r={'checks':[],'timings':{},'bounds':{'startup':240,'operation':180,'exit':180},'limitations':['Warm OS cache, no causal speedup claim','200 original fakeJPEG blobs storage-only, 40newPNG are valid image oracle','Same physical NVMe, benchmark/profiling jobs completed']};oracle=json.loads((RUN/'setup-oracle.json').read_text(encoding='utf-8'))
def persist():c.save_proof();(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
def check(label,value):
 assert value,label
 r['checks'].append(label);persist();print(label,flush=True)
def space(extra=0):
 free=shutil.disk_usage(RUN).free;r.setdefault('freeBytes',[]).append(free);assert free-extra>5*1024**3,'5GiB reserve';persist()
try:
 print('LARGE LAUNCH START',flush=True);start=time.perf_counter();c.launch(pw);r['timings']['startup']=time.perf_counter()-start;check('large exactEXE ready',True);p=c.page;c.capture('large-ready')
 start=time.perf_counter();p.locator('button[data-page="list"]').click();p.wait_for_load_state('networkidle');p.locator('#lfrom').fill('2024-01-01');p.locator('#lto').fill('2030-12-31');c.click('Tìm báo cáo');r['timings']['allList']=time.perf_counter()-start;check('large2191count/50page',p.locator('#listCount').inner_text().startswith('2191 báo cáo') and p.locator('#reportList button[data-id]').count()==50);c.capture('large-page1');start=time.perf_counter();c.click('Trang sau →');r['timings']['page2']=time.perf_counter()-start;check('large page2', '51–100' in p.locator('#listCount').inner_text());c.capture('large-page2');p.locator('#lq').fill('SYNTH ABSENT QUERY 918273');start=time.perf_counter();c.click('Tìm báo cáo');r['timings']['searchEmpty']=time.perf_counter()-start;check('large search0',p.locator('#listCount').inner_text()=='0 báo cáo');c.capture('large-search-empty')
 p.locator('button[data-page="summary"]').click();p.wait_for_load_state('networkidle');p.locator('#sfrom').fill('2026-01-01');p.locator('#sto').fill('2026-12-31');p.locator('#sstatus').select_option('');start=time.perf_counter();c.click('Xem tổng hợp');r['timings']['yearSummary']=time.perf_counter()-start;values=p.locator('#summaryData .metric strong').all_inner_texts();expected=[format(oracle['year2026Totals'][k],',').replace(',','.') for k in ['f20','f40','e20','e40']];r['summaryObserved']=values;r['summaryExpected']=expected;check('large year728aggregate independent SQLoracle',values==expected and '728 ca' in p.locator('#summaryData').inner_text());c.capture('large-year-summary')
 p.locator('button[data-page="edit"]').click();p.locator('#newDate').fill('2031-01-01');p.locator('#newShift').select_option('DAY');c.click('Vào ca này');p.locator('#actor').select_option('SYNTH LARGE ACTOR');p.keyboard.press('Alt+3');p.locator('#notes').fill('SYNTH LARGE40VALIDPNG ORACLE');p.keyboard.press('Control+s');p.locator('#saveState').get_by_text('Đã lưu lúc',exact=False).wait_for(timeout=180000);images=json.loads((B/'consumer-prep/attachment-oracle.json').read_text(encoding='utf-8'))['images'];start=time.perf_counter();c.upload_images([x['path'] for x in images]);r['timings']['upload40']=time.perf_counter()-start;p.locator('#attachmentRows img').last.wait_for();p.locator('#attachmentRows img').evaluate_all('(a)=>Promise.all(a.map(x=>x.decode())).then(()=>a.length===40&&a.every(x=>x.naturalWidth===240&&x.naturalHeight===140))');check('large40PNG actually decoded',True);c.capture('large-40decoded');start=time.perf_counter();p.locator('#tab_notes').click();p.locator('#tab_files').click();r['timings']['filesTab']=time.perf_counter()-start;c.capture('large-files-tab')
 space(oracle['bytes']*2);button=p.get_by_role('button',name='Sao lưu mang đi',exact=True,include_hidden=True)
 if not button.is_visible():button.locator('xpath=..').locator('summary').click()
 start=time.perf_counter()
 with p.expect_download(timeout=180000) as download:
  button.click();p.wait_for_timeout(500);c.capture('portable-visible-wait');toggle=p.locator('summary').first;t=time.perf_counter();toggle.click();r['timings']['portablePendingLocalMenuResponse']=time.perf_counter()-t;c.capture('portable-pending-menu-responsive')
 file=download.value;target=RUN/'large-portable.db';file.save_as(str(target));r['timings']['portableCompleted']=time.perf_counter()-start;r['portable']={'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()};check('large portable completed artifact',target.stat().st_size>10**9)
 with sqlite3.connect(target.resolve().as_uri()+'?mode=ro',uri=True) as db:
  r['portable']['reports']=db.execute('SELECT COUNT(*) FROM reports').fetchone()[0];r['portable']['revisions']=db.execute('SELECT COUNT(*) FROM revisions').fetchone()[0];r['portable']['largeNotes']=json.loads(db.execute("SELECT payload FROM reports WHERE id='2031-01-01_DAY'").fetchone()[0])['notes'];r['portable']['quickCheck']=db.execute('PRAGMA quick_check').fetchone()[0]
 check('large portable logical counts/newreport',r['portable']['reports']==2192 and r['portable']['quickCheck']=='ok' and r['portable']['largeNotes']=='SYNTH LARGE40VALIDPNG ORACLE');space(oracle['bytes']);start=time.perf_counter();c.open_viewer(target);r['timings']['viewerOpen']=time.perf_counter()-start;c.report('2031-01-01_DAY');p.keyboard.press('Alt+4');p.locator('#attachmentRows img').evaluate_all('(a)=>Promise.all(a.map(x=>x.decode())).then(()=>a.length===40&&a.every(x=>x.naturalWidth===240))');check('large portable viewer40decode',True);c.capture('large-viewer-40');c.click('Về DB chính của máy');start=time.perf_counter();c.exit();r['timings']['exit']=time.perf_counter()-start;check('large actualUI exit0',True);r['status']='OBSERVED_PENDING_REVIEW'
except Exception as e:
 r['status']='FAILED';r['error']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'],flush=True)
 try:c.capture('failure')
 except Exception:pass
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception as e:r['cleanupError']=str(e)
 persist();pw.stop();sys.exit(1 if r['status']=='FAILED' else 0)
