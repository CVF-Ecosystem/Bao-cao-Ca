from pathlib import Path
import sys,json,subprocess,time,hashlib,base64,traceback,urllib.request,http.cookiejar,shutil,os,re,datetime
from playwright.sync_api import sync_playwright
import fitz
CHANNEL=os.environ.get('PRINT_BROWSER','chrome');FIXTURE=os.environ.get('PRINT_FIXTURE','short');HEADERS=os.environ.get('PRINT_HEADERS','0')=='1';TRIGGER=os.environ.get('PRINT_TRIGGER','button');CASE=CHANNEL+'-'+FIXTURE+'-headers'+str(int(HEADERS))+'-'+TRIGGER
KEY_EVENTS=[]
def do_trigger(page):
 if TRIGGER=='ctrlp':
  def observe(message):
   if message.text.startswith('PRINT_KEY_WITNESS:'):
    KEY_EVENTS.append(json.loads(message.text.split(':',1)[1]));(RUN/'trusted-key-events.json').write_text(json.dumps(KEY_EVENTS),encoding='utf-8')
  page.on('console',observe)
  page.evaluate("()=>document.addEventListener('keydown',event=>{if(event.ctrlKey&&event.key.toLowerCase()==='p')console.debug('PRINT_KEY_WITNESS:'+JSON.stringify({key:event.key,ctrlKey:event.ctrlKey,isTrusted:event.isTrusted,repeat:event.repeat,defaultPrevented:event.defaultPrevented}));})")
  page.bring_to_front();page.locator('.preview h2').click();page.locator('.preview h2').press('Control+p',timeout=2500)
 else:page.locator('button:text-is("In / Lưu PDF")').click(timeout=2500)
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();BASE=ROOT/'.cvf/runtime/local-completion-20261108';RUN=BASE/('matrix-'+CASE+'-'+str(int(time.time())));RUN.mkdir();started=time.monotonic();data=RUN/'dataset/DU_LIEU';shutil.copytree(BASE/'consumer-main-0f6ed11/DU_LIEU',data);records=[{'fixture':FIXTURE,'id':('2026-10-01_DAY' if FIXTURE=='short' else '2026-10-02_DAY'),'staffRows':9 if FIXTURE=='short' else 24,'jobRows':6 if FIXTURE=='short' else 30,'chiefs':1 if FIXTURE=='short' else 2}]
proc=subprocess.Popen([str(ROOT/'dist/SO_BAO_CAO_CA.exe'),'--no-browser','--data-dir',str(data)],cwd=RUN,creationflags=subprocess.CREATE_NO_WINDOW);allresults={'fixtures':records,'exeSha256':hashlib.sha256((ROOT/'dist/SO_BAO_CAO_CA.exe').read_bytes()).hexdigest(),'method':'Actual headed app Print, browser kiosk-printing Save as PDF destination in owned profile; no PDF generation API','runs':[]};state=None;browser=None
try:
 for _ in range(300):
  if (data/'PHIEN_DANG_CHAY.json').exists():break
  time.sleep(.05)
 state=json.loads((data/'PHIEN_DANG_CHAY.json').read_text());url='http://127.0.0.1:'+str(state['port'])
 with sync_playwright() as p:
  for channel in [CHANNEL]:
   if time.monotonic()-started>480:raise RuntimeError('Approaching10min ceiling')
   out=RUN/(channel+'-output');out.mkdir();profile=RUN/(channel+'-profile');(profile/'Default').mkdir(parents=True)
   settings={'version':2,'selectedDestinationId':'Save as PDF','recentDestinations':[{'id':'Save as PDF','origin':'local','account':''}],'isHeaderFooterEnabled':HEADERS,'isCssBackgroundEnabled':False,'isLandscapeEnabled':True,'mediaSize':{'height_microns':297000,'width_microns':210000,'custom_display_name':'A4','name':'ISO_A4','imageable_area_bottom_microns':0,'imageable_area_left_microns':0,'imageable_area_right_microns':210000,'imageable_area_top_microns':297000,'is_default':False},'marginsType':0,'scalingType':3,'scaling':'100'}
   prefs={'printing':{'print_preview_sticky_settings':{'appState':json.dumps(settings)}},'savefile':{'default_directory':str(out)}};(profile/'Default/Preferences').write_text(json.dumps(prefs),encoding='utf-8')
   record={'trustedKeyWitness':KEY_EVENTS,'case':CASE,'trigger':TRIGGER,'headersRequested':HEADERS,'channel':channel,'headless':False,'settingsRequested':settings,'outputDirectory':out.name,'dialog':None,'outputs':[]};allresults['runs'].append(record)
   ctx=p.chromium.launch_persistent_context(str(profile),channel=channel,headless=False,viewport={'width':1366,'height':657});browser=ctx;page=ctx.pages[0];page.set_default_timeout(6000);page.on('dialog',lambda d:d.accept());page.goto(url+'/?launch='+state['token']);page.locator('button[data-id="'+records[0]['id']+'"]').click();page.locator('button:text-is("Xem / In")').click();cdp=ctx.browser.new_browser_cdp_session();record['browserVersion']=ctx.browser.version
   try:do_trigger(page)
   except Exception:pass
   time.sleep(1);targets=cdp.send('Target.getTargets')['targetInfos'];target=next(t for t in targets if t['url'].startswith(('chrome://print','edge://print')));received={}
   def on_message(event):
    msg=json.loads(event['message'])
    if 'id' in msg:received[msg['id']]=msg
   cdp.on('Target.receivedMessageFromTarget',on_message);session=cdp.send('Target.attachToTarget',{'targetId':target['targetId'],'flatten':False})
   selectA4="(()=>{const all=[];function w(r){for(const e of r.querySelectorAll('*')){all.push(e);if(e.shadowRoot)w(e.shadowRoot)}}w(document);const more=all.find(e=>(e.tagName.includes('BUTTON')||e.tagName==='A'||e.tagName==='SPAN'||e.getAttribute('role')==='button')&&/^More settings/.test((e.innerText||e.textContent||'').trim()));if(more)more.click();const select=all.find(e=>e.tagName==='SELECT'&&[...e.options].some(o=>o.text.trim()==='A4'));if(select){const o=[...select.options].find(o=>o.text.trim()==='A4');select.value=o.value;select.dispatchEvent(new Event('change',{bubbles:true}));return {control:'native paper SELECT',selected:select.value}}return {paperControlNotFound:true};})()"
   cdp.send('Target.sendMessageToTarget',{'sessionId':session['sessionId'],'message':json.dumps({'id':90,'method':'Runtime.evaluate','params':{'expression':selectA4,'returnByValue':True}})})
   for _ in range(10):cdp.send('Target.getTargets');time.sleep(.1)
   record['nativePaperSelection']=received.get(90)
   if channel=='msedge':
    edgeSelect="(()=>{const all=[];function w(r){for(const e of r.querySelectorAll('*')){all.push(e);if(e.shadowRoot)w(e.shadowRoot)}}w(document);const b=all.find(e=>e.tagName==='BUTTON'&&['Letter','A4'].includes((e.innerText||'').trim()));if(b)b.click();const option=all.find(e=>e.tagName==='FLUENT-OPTION'&&(e.innerText||e.textContent||'').trim()==='A4');if(option)option.click();return {clickedPaperButton:!!b,clickedActualA4Option:!!option};})()"
    cdp.send('Target.sendMessageToTarget',{'sessionId':session['sessionId'],'message':json.dumps({'id':92,'method':'Runtime.evaluate','params':{'expression':edgeSelect,'returnByValue':True}})})
    for _ in range(10):cdp.send('Target.getTargets');time.sleep(.1)
    record['edgeNativePaperControlAction']=received.get(92)
   expression="(()=>{const controls=[];function walk(r){for(const e of r.querySelectorAll('*')){if(e.shadowRoot)walk(e.shadowRoot);if((['INPUT','SELECT'].includes(e.tagName)||e.tagName.includes('SELECT')||e.tagName.includes('COMBOBOX')||e.tagName.includes('OPTION'))||e.tagName.includes('BUTTON')||'checked' in e||e.getAttribute('role')==='checkbox')controls.push({tag:e.tagName,id:e.id,text:e.innerText||e.textContent,label:e.getAttribute('aria-label'),role:e.getAttribute('role'),ariaChecked:e.getAttribute('aria-checked'),value:e.value,checked:e.checked,disabled:e.disabled});}}walk(document);return controls;})()"
   for mid,method,params in [(1,'Runtime.evaluate',{'expression':expression,'returnByValue':True}),(2,'Page.captureScreenshot',{})]:cdp.send('Target.sendMessageToTarget',{'sessionId':session['sessionId'],'message':json.dumps({'id':mid,'method':method,'params':params})})
   for _ in range(40):
    cdp.send('Target.getTargets');time.sleep(.1)
    if 1 in received and 2 in received:break
   cdp.send('Target.sendMessageToTarget',{'sessionId':session['sessionId'],'message':json.dumps({'id':91,'method':'DOM.getDocument','params':{'depth':-1,'pierce':True}})})
   for _ in range(5):cdp.send('Target.getTargets');time.sleep(.1)
   if 91 in received:(RUN/(channel+'-native-dom.json')).write_text(json.dumps(received[91],ensure_ascii=False),encoding='utf-8')
   record['dialog']={'target':target,'relatedTargets':[t for t in targets if 'print' in t['url']],'controls':received.get(1)}
   if 2 in received:(RUN/(channel+'-actual-dialog.png')).write_bytes(base64.b64decode(received[2]['result']['data']))
   ctx.close();browser=None
   stored=json.loads((profile/'Default/Preferences').read_text(encoding='utf-8'));record['persistedPrintingAppState']=json.loads(stored.get('printing',{}).get('print_preview_sticky_settings',{}).get('appState','{}'))
   # Same profile keeps observed destination/settings. Kiosk skips OS SaveAs only.
   ctx=p.chromium.launch_persistent_context(str(profile),channel=channel,headless=False,args=['--kiosk-printing'],viewport={'width':1366,'height':657});browser=ctx;page=ctx.pages[0];page.set_default_timeout(6000);page.on('dialog',lambda d:d.accept());page.goto(url+'/?launch='+state['token'])
   for fixture in records:
    if fixture['fixture']=='long':page.locator('button[data-page="home"]').click()
    page.locator('button[data-id="'+fixture['id']+'"]').click();page.locator('button:text-is("Xem / In")').click();page.screenshot(path=str(RUN/(channel+'-'+fixture['fixture']+'-before-print.png')));prior={f:(f.stat().st_mtime_ns,f.stat().st_size) for f in out.glob('*.pdf')};trigger=time.time()
    try:do_trigger(page)
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
     texts=[page_.get_text() for page_ in pdf];media=[[page_.rect.width,page_.rect.height] for page_ in pdf];pdf[0].get_pixmap(matrix=fitz.Matrix(1,1)).save(str(RUN/(channel+'-'+fixture['fixture']+'-page1.png')))
    expectedDay='01/10/2026' if FIXTURE=='short' else '02/10/2026';oracles={'A4landscape':all(abs(w-841.89)<2 and abs(h-595.28)<2 for w,h in media),'shortOnePage':FIXTURE!='short' or len(texts)==1,'perPageIdentity':all(expectedDay+' · Ca ngày' in text for text in texts),'perPageNumber':all('Trang '+str(i+1)+'/'+str(len(texts)) in text for i,text in enumerate(texts)),'perPageMachineTime':all(re.search(r'In lúc \d{2}:\d{2} \d{2}/\d{2}/\d{4}',text) for text in texts),'signatureOnlyLast':all('Trưởng ca (Phụ trách chung)' not in text for text in texts[:-1]) and 'Trưởng ca (Phụ trách chung)' in texts[-1],'allChiefNamesLast':[name in texts[-1] for name in ['SYNTH CHIEF 1']+(['SYNTH CHIEF 2'] if FIXTURE=='long' else [])]};record['layoutOracles']=oracles;record['mediaBoxes']=media
    record['outputs'].append({'fixture':fixture['fixture'],'triggerEpoch':trigger,'completedEpoch':time.time(),'filename':completed.name,'retainedCopy':persist.name,'bytes':persist.stat().st_size,'sha256':hashlib.sha256(persist.read_bytes()).hexdigest(),'pages':len(texts),'pageTexts':texts,'oracleFound':('LOCAL ORACLE '+fixture['fixture']) in '\n'.join(texts),'origin':'BROWSER_NATIVE_COMPLETED_SAVE_FROM_APP_PRINT','OSSaveAs':'NOT_TESTED'})
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
