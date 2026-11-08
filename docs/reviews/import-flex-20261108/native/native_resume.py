from pathlib import Path
import sys,json,hashlib,subprocess,time,ctypes
from ctypes import wintypes
from playwright.sync_api import sync_playwright,expect
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path.cwd();BASE=ROOT/'.cvf/runtime/import-flex-20261108';OUT=BASE/'native';RUN=BASE/'private-fixture';PROFILE=BASE/'chrome-profile';EXE=ROOT/'dist/SO_BAO_CAO_CA.exe';WB=ROOT/'Danh sach doi container 28.12.2025.xlsx';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'attempt2-result.json').write_bytes((OUT/'result.json').read_bytes());result=json.loads((OUT/'result.json').read_text(encoding='utf-8'));result['failureHistory']=[{'attempt':1,'cause':'Harness read bounding box before async newShift render completed; TypeError; added visible newDate wait.'},{'attempt':2,'cause':'Harness unconditionally toggled already-open Settings menu closed; timeout on hidden catalog button. Resume retained imported fixture, no repeated confirm.'}];result.pop('failure',None);result.pop('processEnded',None);result['events'].append({'event':'processCustodyCorrection','actualInitialExePID':54284,'attempt2SpawnWasNotServing':'Original retained session served consumer; second launch did not replace lock owner.'})
k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE;k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];k.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)];k.CloseHandle.argtypes=[wintypes.HANDLE]
h=k.OpenProcess(0x100000|0x1000,False,54284)
def log(event,**values):result['events'].append({'event':event,**values});(OUT/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
def connect(p):
 s=json.loads((RUN/'DU_LIEU/PHIEN_DANG_CHAY.json').read_text(encoding='utf-8'));p.goto('http://127.0.0.1:'+str(s['port'])+'/?launch='+s['token']);expect(p.locator('button[data-page="edit"]')).to_be_enabled()
def menu(p):
 b=p.get_by_role('button',name='Danh mục nhân sự / công việc',exact=True,include_hidden=True)
 if not b.is_visible():p.get_by_text('Cài đặt',exact=True).click()
 b.click();expect(p.locator('#catalog_people')).to_be_visible()
with sync_playwright() as pw:
 context=pw.chromium.launch_persistent_context(str(PROFILE),channel='chrome',headless=False,viewport={'width':1366,'height':657});p=context.pages[0];p.set_default_timeout(15000);p.on('dialog',lambda d:d.accept());connect(p);menu(p);assert len(p.locator('#catalog_people').input_value().splitlines())==64;p.get_by_role('button',name='Nhập nhân viên Excel',exact=True).click()
 with p.expect_response(lambda z:z.url.endswith('/api/personnel-xlsx-inspect')) as res:p.locator('#personnelFile').set_input_files(str(WB))
 expect(p.locator('#personnelHeader')).to_have_value('2')
 with p.expect_response(lambda z:z.url.endswith('/api/personnel-xlsx-preview')) as res:p.get_by_role('button',name='Xem trước',exact=True).click()
 d=res.value.json();expect(p.locator('#personnelPlan>p').first).to_contain_text('Mới: 0');assert d['counts']=={'new':0,'existing':63,'error':0,'excluded':0};assert not d['canConfirm'];assert p.get_by_role('button',name='Xác nhận thêm nhân viên',exact=True).count()==0;p.locator('#personnelPlan>p').first.screenshot(path=str(OUT/'preview-0-counts.png'));log('repeatNoop',counts=d['counts'],noConfirmButton=True)
 p.keyboard.press('Escape');expect(p.locator('#modal')).to_be_hidden();before=sha(RUN/'DANH_MUC/NHAN_VIEN.txt');p.get_by_role('button',name='Thoát tool',exact=True).click()
 assert h and k.WaitForSingleObject(h,35000)==0;code=wintypes.DWORD();assert k.GetExitCodeProcess(h,ctypes.byref(code));k.CloseHandle(h);assert code.value==0;log('initialExeExited',pid=54284,exitCode=code.value,sessionRemoved=not(RUN/'DU_LIEU/PHIEN_DANG_CHAY.json').exists())
 proc=subprocess.Popen([str(EXE),'--no-browser','--data-dir',str(RUN/'DU_LIEU')],cwd=RUN,creationflags=subprocess.CREATE_NO_WINDOW);deadline=time.monotonic()+40
 while not(RUN/'DU_LIEU/PHIEN_DANG_CHAY.json').exists():assert proc.poll() is None;assert time.monotonic()<deadline;time.sleep(.1)
 connect(p);menu(p);assert len(p.locator('#catalog_people').input_value().splitlines())==64 and sha(RUN/'DANH_MUC/NHAN_VIEN.txt')==before;log('restartPersistence',newPID=proc.pid,total=64,actualImported=63,syntheticSentinel=1,catalogSha256=before);p.keyboard.press('Escape');p.get_by_role('button',name='Thoát tool',exact=True).click();proc.wait(timeout=35);assert proc.returncode==0;log('restartExeExited',pid=proc.pid,exitCode=proc.returncode,sessionRemoved=not(RUN/'DU_LIEU/PHIEN_DANG_CHAY.json').exists());context.close()
result['status']='OBSERVED_PENDING_INDEPENDENT_REVIEW';result['workbookSha256After']=sha(WB);assert result['workbookSha256After']==result['workbookSha256Before'];result['processEnded']=True;log('workbookUnchanged',sha256=result['workbookSha256After']);print('PASS repeat0NEW63EXISTING, restart64total63actual, originalPIDexit0 restartPIDexit0, workbook unchanged',flush=True)
