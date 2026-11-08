from pathlib import Path
import sys,json,time,subprocess,hashlib,sqlite3,shutil
from playwright.sync_api import sync_playwright,expect
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path.cwd();BASE=ROOT/'.cvf/runtime/import-flex-20261108';RUN=BASE/'private-fixture';PROFILE=BASE/'chrome-profile';OUT=BASE/'native';OUT.mkdir(exist_ok=True);RUN.mkdir(exist_ok=True);CAT=RUN/'DANH_MUC';CAT.mkdir(exist_ok=True)
(CAT/'NHAN_VIEN.txt').write_text('SYNTHETIC SENTINEL\n',encoding='utf-8');(CAT/'VI_TRI.txt').write_text('PHỤ TRÁCH CHUNG\n',encoding='utf-8');(CAT/'CONG_VIEC.txt').write_text('SYNTHETIC JOB\n',encoding='utf-8');(CAT/'TO_NHAN_SU.json').write_text(json.dumps([{'id':'team'+str(i),'name':'Ca '+str(i),'people':[]} for i in range(1,4)]),encoding='utf-8');(CAT/'MAU_PHAN_CONG.json').write_text(json.dumps({k:[] for k in ['team1','team2','team3','day']}),encoding='utf-8')
WB=ROOT/'Danh sach doi container 28.12.2025.xlsx';EXE=ROOT/'dist/SO_BAO_CAO_CA.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();result={'exeSha256':sha(EXE),'commit':'563c4b83eb23','version':'1.10.1','workbookSha256Before':sha(WB),'headless':False,'viewport':{'width':1366,'height':657},'browserInputUpload':'EXERCISED','nativeOSFileDialog':'NOT_TESTED','events':[]};proc=None;context=None;phase='launch'
def log(event,**values):result['events'].append({'event':event,**values});(OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
def launch(p):
 global proc
 proc=subprocess.Popen([str(EXE),'--no-browser','--data-dir',str(RUN/'DU_LIEU')],cwd=RUN,creationflags=subprocess.CREATE_NO_WINDOW)
 session=RUN/'DU_LIEU/PHIEN_DANG_CHAY.json';deadline=time.monotonic()+40
 while not session.exists():
  assert proc.poll() is None,'EXE readiness';assert time.monotonic()<deadline,'readiness timeout';time.sleep(.1)
 state=json.loads(session.read_text(encoding='utf-8'));p.goto('http://127.0.0.1:'+str(state['port'])+'/?launch='+state['token']);expect(p.locator('button[data-page="edit"]')).to_be_enabled();log('exeStarted',pid=proc.pid)
def exit_app(p):
 p.get_by_role('button',name='Thoát tool',exact=True).click();proc.wait(timeout=35);assert proc.returncode==0;log('exeExited',pid=proc.pid,exitCode=proc.returncode,sessionRemoved=not(RUN/'DU_LIEU/PHIEN_DANG_CHAY.json').exists())
def menu(p):
 p.get_by_text('Cài đặt',exact=True).click();p.get_by_role('button',name='Danh mục nhân sự / công việc',exact=True).click();expect(p.locator('#catalog_people')).to_be_visible()
def inspect(p):
 p.get_by_role('button',name='Nhập nhân viên Excel',exact=True).click()
 with p.expect_response(lambda z:z.url.endswith('/api/personnel-xlsx-inspect')) as response:p.locator('#personnelFile').set_input_files(str(WB))
 assert response.value.status==200
 expect(p.locator('#personnelHeader')).to_have_value('2')
 values={k:p.locator('#personnelCol_'+k).input_value() for k in ['name','code','title','group']};assert values=={'name':'2','code':'3','title':'4','group':'6'}
 log('inspectSuggested',headerRow=2,columns=values)
def preview(p,expected_new,expected_existing):
 with p.expect_response(lambda z:z.url.endswith('/api/personnel-xlsx-preview')) as response:p.get_by_role('button',name='Xem trước',exact=True).click()
 d=response.value.json();assert response.value.status==200;expect(p.locator('#personnelPlan>p').first).to_contain_text('Mới: '+str(expected_new));assert d['counts']['new']==expected_new and d['counts']['existing']==expected_existing and d['counts']['error']==0
 conversions=sum('Mã số đã chuyển thành văn bản theo định dạng ô.' in row['messages'] for row in d['rows']);assert conversions==14
 log('preview',counts=d['counts'],numericConversions=conversions,canConfirm=d['canConfirm']);p.locator('#personnelPlan>p').first.screenshot(path=str(OUT/('preview-'+str(expected_new)+'-counts.png')))
try:
 with sync_playwright() as pw:
  context=pw.chromium.launch_persistent_context(str(PROFILE),channel='chrome',headless=False,viewport={'width':1366,'height':657});p=context.pages[0];p.set_default_timeout(15000);p.on('dialog',lambda d:d.accept());result['browserVersion']=context.browser.version
  launch(p);phase='synthetic dialogs';opener=p.locator('button[data-page="edit"]');opener.click();expect(p.locator('#newDate')).to_be_visible();p.screenshot(path=str(OUT/'newshift-visible-x.png'));log('syntheticDialogReady');print('SYNTHETIC_DIALOG_READY',flush=True)
  deadline=time.monotonic()+120
  while not(BASE/'CONTINUE').exists():assert time.monotonic()<deadline,'visual review timeout';time.sleep(.2)
  p.get_by_role('button',name='Đóng hộp thoại',exact=True).click();expect(p.locator('#modal')).to_be_hidden();assert opener.evaluate('(e)=>document.activeElement===e');log('newshiftX',closed=True,openerFocusRestored=True)
  opener.click();expect(p.locator('#newDate')).to_be_visible();box=p.locator('#modalBody').bounding_box();assert box['x']>8;p.mouse.click(5,5);expect(p.locator('#modal')).to_be_hidden();log('newshiftBackdrop',closed=True)
  opener.click();expect(p.locator('#newDate')).to_be_visible();p.keyboard.press('Escape');expect(p.locator('#modal')).to_be_hidden();log('newshiftEscape',closed=True)
  with sqlite3.connect((RUN/'DU_LIEU/BAO_CAO_CA.db').as_uri()+'?mode=ro',uri=True) as db:assert db.execute('select count(*) from reports').fetchone()[0]==0
  log('dismissalNoReportCreated',reports=0)
  phase='private import';menu(p);assert p.locator('#catalog_people').input_value().strip()=='SYNTHETIC SENTINEL';inspect(p);preview(p,63,0)
  with p.expect_response(lambda z:z.url.endswith('/api/personnel-xlsx-confirm')) as response:p.get_by_role('button',name='Xác nhận thêm nhân viên',exact=True).click()
  d=response.value.json();assert response.value.status==200 and d['added']==63;expect(p.locator('#modal')).to_be_hidden();log('confirm',added=d['added'])
  opener.click();expect(p.locator('#newDate')).to_be_visible();p.locator('#newDate').fill('2035-01-01');p.get_by_role('button',name='Vào ca này',exact=True).click();expect(p.locator('#actor')).to_be_visible();options=p.locator('#actor option').evaluate_all('(es)=>es.filter(e=>e.value).length');assert options==64;log('reportPersonPickerAvailable',total=options,syntheticSentinel=1,actualImported=63)
  p.locator('button[data-page="home"]').click();menu(p);inspect(p);preview(p,0,63);assert p.get_by_role('button',name='Xác nhận thêm nhân viên',exact=True).count()==0;p.keyboard.press('Escape');expect(p.locator('#modal')).to_be_hidden();log('repeatNoop',noConfirmButton=True)
  before=sha(CAT/'NHAN_VIEN.txt');count=len([x for x in (CAT/'NHAN_VIEN.txt').read_text(encoding='utf-8').splitlines() if x.strip()]);assert count==64;exit_app(p)
  phase='restart';launch(p);menu(p);countUI=len([x for x in p.locator('#catalog_people').input_value().splitlines() if x.strip()]);assert countUI==64 and sha(CAT/'NHAN_VIEN.txt')==before;log('restartPersistence',total=countUI,actualImported=63,syntheticSentinel=1,catalogSha256=before);p.keyboard.press('Escape');exit_app(p)
  context.close();context=None
 result['status']='OBSERVED_PENDING_INDEPENDENT_REVIEW';result['workbookSha256After']=sha(WB);assert result['workbookSha256After']==result['workbookSha256Before'];log('workbookUnchanged',sha256=result['workbookSha256After'])
except Exception as e:
 result['status']='FAILED';result['failure']={'phase':phase,'class':type(e).__name__,'frames':[{'line':f.lineno,'function':f.name} for f in __import__('traceback').extract_tb(e.__traceback__)]};print('FAILED',phase,type(e).__name__,flush=True)
 if context:
  try:exit_app(p)
  except Exception:pass
finally:
 if context:
  try:context.close()
  except Exception:pass
 result['processEnded']=proc is None or proc.poll() is not None
 (OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(result['status'],flush=True)
 sys.exit(0 if result['status']=='OBSERVED_PENDING_INDEPENDENT_REVIEW' else 1)
