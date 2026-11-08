"""Reusable real headed EXE controller. No API mutations, no browser evaluation that mutates app data."""
from pathlib import Path
import time,json,subprocess,hashlib,sqlite3
class Consumer:
 def __init__(self,exe,run,channel='chrome'):
  self.exe=Path(exe).resolve();self.run=Path(run).resolve();self.data=self.run/'DU_LIEU';self.channel=channel;self.proof=[];self.process=None;self.browser=None;self.startup_timeout=60;self.operation_timeout=30;self.exit_timeout=30
 def launch(self,p,default_browser=False):
  self.run.mkdir(parents=True,exist_ok=True);launchStarted=time.perf_counter();self.process=subprocess.Popen([str(self.exe),'--data-dir',str(self.data)]+([] if default_browser else ['--no-browser']),cwd=self.run,creationflags=subprocess.CREATE_NO_WINDOW)
  session=self.data/'PHIEN_DANG_CHAY.json'
  for _ in range(int(self.startup_timeout*10)):
   if session.exists():break
   if self.process.poll() is not None:raise RuntimeError('EXE exited before readiness')
   time.sleep(.1)
  if not session.exists():raise TimeoutError('EXE readiness exceeded '+str(self.startup_timeout)+' seconds')
  state=json.loads(session.read_text(encoding='utf-8'));self.base='http://127.0.0.1:'+str(state['port']);self.browser=p.chromium.launch(channel=self.channel,headless=False);self.context=self.browser.new_context(viewport={'width':1366,'height':657},accept_downloads=True);self.page=self.context.new_page();self.page.set_default_timeout(max(15000,self.operation_timeout*1000));self.page.set_default_navigation_timeout(self.startup_timeout*1000);self.dialogs=[]
  self.page.on('dialog',self._dialog);self.page.goto(self.base+'/?launch='+state['token']);self.proof.append({'event':'launch','readinessSeconds':time.perf_counter()-launchStarted,'pid':self.process.pid,'headless':False,'browser':self.browser.version,'exeSha256':hashlib.sha256(self.exe.read_bytes()).hexdigest()})
 def _dialog(self,d):
  self.dialogs.append({'type':d.type,'message':d.message});d.accept('SYNTHETIC CORRECTION REASON' if d.type=='prompt' else None)
 def click(self,text):
  self.proof.append({'event':'click-start','text':text});self.save_proof();self.page.get_by_role('button',name=text,exact=True).click();self.page.wait_for_load_state('networkidle');self.proof.append({'event':'click-done','text':text});self.save_proof()
 def capture(self,name):self.page.screenshot(path=str(self.run/(name+'.png')));self.proof.append({'event':'screenshot','file':name+'.png'})
 def menu(self,text):
  self.proof.append({'event':'menu-start','text':text});self.save_proof()
  button=self.page.get_by_role('button',name=text,exact=True,include_hidden=True)
  if not button.is_visible():button.locator('xpath=..').locator('summary').click()
  button.click();self.page.wait_for_load_state('networkidle');self.proof.append({'event':'menu-done','text':text});self.save_proof()
 def report(self,report_id):
  self.page.locator('button[data-page="home"]').click();button=self.page.locator('button[data-id="'+report_id+'"]')
  if button.count():button.first.click();self.page.locator('#edit:not(.hide)').wait_for();self.page.wait_for_load_state('networkidle');return
  self.page.locator('button[data-page="list"]').click();day=report_id[:10];self.page.locator('#lfrom').fill(day);self.page.locator('#lto').fill(day);self.click('Tìm báo cáo');self.page.locator('button[data-id="'+report_id+'"]').click();self.page.locator('#edit:not(.hide)').wait_for();self.page.wait_for_load_state('networkidle')
 def download(self,action,name):
  self.proof.append({'event':'download-start','target':name});self.save_proof()
  with self.page.expect_download(timeout=self.operation_timeout*1000) as event:action()
  download=event.value;target=self.run/name;download.save_as(str(target));self.proof.append({'event':'download','file':name,'suggested':download.suggested_filename,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()});return target
 def upload_images(self,paths):
  self.page.keyboard.press('Alt+4');start=time.perf_counter()
  with self.page.expect_file_chooser() as picker:self.click('＋ Thêm tệp')
  picker.value.set_files([str(p) for p in paths]);self.page.locator('#uploadState').get_by_text('Đã lưu ngay 40 tệp',exact=False).wait_for(timeout=180000);self.proof.append({'event':'upload40','seconds':time.perf_counter()-start});self.capture('forty-images')
 def export_month(self,month,target):
  self.menu('Xuất Excel cả tháng');self.page.locator('#exportMonth').fill(month);return self.download(lambda:self.click('Xuất cả tháng'),target)
 def enable_corrections(self):
  self.click('Bật chỉnh sửa / bổ sung');self.page.locator('#singlePerson').select_option('SYNTH REVIEWER');self.click('Chọn tên này');self.page.get_by_text('ĐANG BỔ SUNG · BẢN SAO DB',exact=True).wait_for()
 def open_viewer(self,path):
  with self.page.expect_file_chooser() as picker:self.menu('Mở DB kiểm tra / bổ sung')
  picker.value.set_files(str(path));self.page.get_by_text('CHỈ XEM · DB KIỂM TRA',exact=True).wait_for()
 def correct_note(self,report_id,note):
  self.report(report_id);self.page.keyboard.press('Alt+3');self.page.locator('#notes').fill(note);self.page.keyboard.press('Control+s');self.page.locator('#saveState').get_by_text('Đã lưu lúc',exact=False).wait_for();self.page.wait_for_load_state('networkidle')
 def upgrade(self):
  self.click('Xem kế hoạch nâng cấp');self.capture('upgrade-preview');self.page.locator('#upgradeConsent').check();self.click('Nâng cấp dữ liệu');self.page.locator('button[data-page="edit"]:not([disabled])').wait_for();self.capture('upgrade-complete')
 def recover_known(self):
  self.click('Phục hồi từ bản sao đã giữ');self.capture('known-recovery-list');self.page.get_by_role('button',name='Kiểm tra / phục hồi',exact=True).first.click();self.capture('known-recovery-preview');self.page.locator('#confirmRecovery').fill('KHOI PHUC');self.click('Phục hồi bản sao này');self.page.get_by_role('button',name='Xem kế hoạch nâng cấp',exact=True).wait_for();self.capture('restored-legacy-restricted')
 def exit(self):
  self.page.keyboard.press('Escape');self.menu('Thoát tool');self.process.wait(timeout=self.exit_timeout);self.proof.append({'event':'exit','pid':self.process.pid,'exitCode':self.process.returncode,'sessionFileRemoved':not(self.data/'PHIEN_DANG_CHAY.json').exists()});assert self.process.returncode==0
  if self.browser:self.browser.close();self.browser=None
 def save_proof(self): (self.run/'consumer-events.json').write_text(json.dumps(self.proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def readonly_db_oracle(path):
 with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True) as c:
  result={}
  for name in ['reports','revisions','attachment_blobs','meta']:
   digest=hashlib.sha256();count=0
   for row in c.execute('SELECT * FROM '+name+' ORDER BY 1'):
    digest.update(json.dumps([{'blobSha256':hashlib.sha256(x).hexdigest(),'bytes':len(x)} if isinstance(x,bytes) else x for x in row],ensure_ascii=False).encode());count+=1
   result[name]={'count':count,'rowsSha256':digest.hexdigest()}
  return result
