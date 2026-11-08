from pathlib import Path
import sys,json,subprocess,time,hashlib,base64,traceback,urllib.request,http.cookiejar,shutil
from playwright.sync_api import sync_playwright
import fitz
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();BASE=ROOT/'.cvf/runtime/local-completion-20261108';RUN=BASE/('native-save-'+str(int(time.time())));RUN.mkdir();sys.path.insert(0,str(BASE/'baseline-seed-source/ma_nguon'));from LUU_TRU import Store
records=[];started=time.monotonic();data=RUN/'dataset/DU_LIEU';data.mkdir(parents=True);catalog=data.parent/'DANH_MUC';catalog.mkdir();(catalog/'NHAN_VIEN.txt').write_text('SYNTH ACTOR\nSYNTH CHIEF 1\nSYNTH CHIEF 2\n',encoding='utf-8')
store=Store(data/'BAO_CAO_CA.db')
for name,day,count,jobs,chiefs in [('short','2026-10-01',9,6,1),('long','2026-10-02',24,30,2)]:
 staff=[{'role':'PHỤ TRÁCH CHUNG','people':'; '.join('SYNTH CHIEF '+str(i+1) for i in range(chiefs))}]+[{'role':'SYNTH POSITION '+str(i),'people':'SYNTH PERSON '+str(i)} for i in range(count-1)]
 report={'date':day,'shift':'DAY','status':'draft','actor':'SYNTH ACTOR','notes':'BASELINE '+name.upper()+' PRINT ORACLE','staffing':staff,'jobs':[dict(name='SYNTH JOB '+str(i),detail='YARD '+str(i),xn=True,rtg=False,f20=i+1,f40=2,e20=0,e40=1) for i in range(jobs)],'handover':[]}
 store.save(report,0);records.append({'fixture':name,'id':day+'_DAY','staffRows':count,'jobRows':jobs,'chiefs':chiefs,'payloadSha256':hashlib.sha256(json.dumps(report,sort_keys=True).encode()).hexdigest()})
proc=subprocess.Popen([str(BASE/'BASELINE_1_9_2.exe'),'--no-browser','--data-dir',str(data)],cwd=RUN,creationflags=subprocess.CREATE_NO_WINDOW);allresults={'fixtures':records,'exeSha256':hashlib.sha256((BASE/'BASELINE_1_9_2.exe').read_bytes()).hexdigest(),'method':'Actual headed app Print, browser kiosk-printing Save as PDF destination in owned profile; no PDF generation API','runs':[]};state=None;browser=None
try:
 for _ in range(300):
  if (data/'PHIEN_DANG_CHAY.json').exists():break
  time.sleep(.05)
 state=json.loads((data/'PHIEN_DANG_CHAY.json').read_text());url='http://127.0.0.1:'+str(state['port'])
 with sync_playwright() as p:
  for channel in ['chrome','msedge']:
   if time.monotonic()-started>480:raise RuntimeError('Approaching10min ceiling')
   out=RUN/(channel+'-output');out.mkdir();profile=RUN/(channel+'-profile');(profile/'Default').mkdir(parents=True)
   settings={'version':2,'selectedDestinationId':'Save as PDF','recentDestinations':[{'id':'Save as PDF','origin':'local','account':''}],'isHeaderFooterEnabled':True,'isCssBackgroundEnabled':False,'isLandscapeEnabled':True,'mediaSize':{'height_microns':297000,'width_microns':210000,'custom_display_name':'A4','is_default':True},'marginsType':0,'scalingType':3,'scaling':'100'}
   prefs={'printing':{'print_preview_sticky_settings':{'appState':json.dumps(settings)}},'savefile':{'default_directory':str(out)}};(profile/'Default/Preferences').write_text(json.dumps(prefs),encoding='utf-8')
   record={'channel':channel,'headless':False,'settingsRequested':settings,'outputDirectory':out.name,'dialog':None,'outputs':[]};allresults['runs'].append(record)
   ctx=p.chromium.launch_persistent_context(str(profile),channel=channel,headless=False,viewport={'width':1366,'height':657});browser=ctx;page=ctx.pages[0];page.set_default_timeout(6000);page.on('dialog',lambda d:d.accept());page.goto(url+'/?launch='+state['token']);page.locator('button[data-id="2026-10-01_DAY"]').click();page.locator('button:text-is("Xem / In")').click();cdp=ctx.browser.new_browser_cdp_session();record['browserVersion']=ctx.browser.version
   try:page.locator('button:text-is("In / Lưu PDF")').click(timeout=2500)
   except Exception:pass
   time.sleep(1);targets=cdp.send('Target.getTargets')['targetInfos'];target=next(t for t in targets if t['url'].startswith(('chrome://print','edge://print')));received={}
   def on_message(event):
    msg=json.loads(event['message'])
    if 'id' in msg:received[msg['id']]=msg
   cdp.on('Target.receivedMessageFromTarget',on_message);session=cdp.send('Target.attachToTarget',{'targetId':target['targetId'],'flatten':False})
   expression="(()=>{const controls=[];function walk(r){for(const e of r.querySelectorAll('*')){if(e.shadowRoot)walk(e.shadowRoot);if(['INPUT','SELECT','CR-CHECKBOX','CR-BUTTON','PRINT-PREVIEW-HEADER'].includes(e.tagName))controls.push({tag:e.tagName,id:e.id,text:e.innerText,value:e.value,checked:e.checked,disabled:e.disabled});}}walk(document);return controls;})()"
   for mid,method,params in [(1,'Runtime.evaluate',{'expression':expression,'returnByValue':True}),(2,'Page.captureScreenshot',{})]:cdp.send('Target.sendMessageToTarget',{'sessionId':session['sessionId'],'message':json.dumps({'id':mid,'method':method,'params':params})})
   for _ in range(40):
    cdp.send('Target.getTargets');time.sleep(.1)
    if 1 in received and 2 in received:break
   record['dialog']={'target':target,'relatedTargets':[t for t in targets if 'print' in t['url']],'controls':received.get(1)}
   if 2 in received:(RUN/(channel+'-actual-dialog.png')).write_bytes(base64.b64decode(received[2]['result']['data']))
   ctx.close();browser=None
   # Same profile keeps observed destination/settings. Kiosk skips OS SaveAs only.
   ctx=p.chromium.launch_persistent_context(str(profile),channel=channel,headless=False,args=['--kiosk-printing'],viewport={'width':1366,'height':657});browser=ctx;page=ctx.pages[0];page.set_default_timeout(6000);page.on('dialog',lambda d:d.accept());page.goto(url+'/?launch='+state['token'])
   for fixture in records:
    if fixture['fixture']=='long':page.locator('button[data-page="home"]').click()
    page.locator('button[data-id="'+fixture['id']+'"]').click();page.locator('button:text-is("Xem / In")').click();page.screenshot(path=str(RUN/(channel+'-'+fixture['fixture']+'-before-print.png')));prior={f:(f.stat().st_mtime_ns,f.stat().st_size) for f in out.glob('*.pdf')};trigger=time.time()
    try:page.locator('button:text-is("In / Lưu PDF")').click(timeout=2500)
    except Exception:pass
    completed=None
    for _ in range(150):
     files={f for f in out.glob('*.pdf') if f not in prior or (f.stat().st_mtime_ns,f.stat().st_size)!=prior[f]}
     if files:
      candidate=max(files,key=lambda f:f.stat().st_mtime)
      try:
       with fitz.open(candidate) as pdf:
        if pdf.page_count:completed=candidate;break
      except Exception:pass
     time.sleep(.1)
    if not completed:raise RuntimeError(channel+' native save produced no complete PDF within15s')
    persist=RUN/(channel+'-'+fixture['fixture']+'-native-saved.pdf');shutil.copyfile(completed,persist)
    with fitz.open(persist) as pdf:
     texts=[page_.get_text() for page_ in pdf];pdf[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(str(RUN/(channel+'-'+fixture['fixture']+'-page1.png')))
    record['outputs'].append({'fixture':fixture['fixture'],'triggerEpoch':trigger,'completedEpoch':time.time(),'filename':completed.name,'retainedCopy':persist.name,'bytes':completed.stat().st_size,'sha256':hashlib.sha256(completed.read_bytes()).hexdigest(),'pages':len(texts),'pageTexts':texts,'oracleFound':('BASELINE '+fixture['fixture'].upper()+' PRINT ORACLE') in '\n'.join(texts),'origin':'BROWSER_NATIVE_COMPLETED_SAVE_FROM_APP_PRINT','OSSaveAs':'NOT_TESTED'})
    page.locator('#modalBody button:text-is("Đóng")').click()
   ctx.close();browser=None
except Exception as e:allresults['error']=type(e).__name__+': '+str(e);allresults['traceback']=traceback.format_exc()
finally:
 if browser:
  try:browser.close()
  except Exception:pass
 if state:
  try:
   client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));client.open(url+'/?launch='+state['token'],timeout=3).read();client.open(urllib.request.Request(url+'/api/shutdown',data=b'{}',headers={'X-Ca-Request':'1','Content-Type':'application/json'}),timeout=3).read();proc.wait(timeout=10);allresults['cleanupExitCode']=proc.returncode
  except Exception as e:allresults['cleanupError']=type(e).__name__
 allresults['elapsedSeconds']=time.monotonic()-started;(RUN/'result.json').write_text(json.dumps(allresults,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'run':str(RUN),'elapsed':allresults['elapsedSeconds'],'error':allresults.get('error'),'outputs':[{ 'channel':r['channel'],'outputs':[{k:v for k,v in o.items() if k!='pageTexts'} for o in r['outputs']]} for r in allresults['runs']]},ensure_ascii=False));sys.exit(1 if 'error' in allresults else 0)
