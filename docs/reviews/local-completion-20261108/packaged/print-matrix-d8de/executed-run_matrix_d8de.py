from pathlib import Path
import os,subprocess,json,time,sys
sys.stdout.reconfigure(encoding='utf-8');root=Path('.').resolve();base=root/'.cvf/runtime/local-completion-20261108';records=[]
for browser in ['chrome','msedge']:
 for fixture in ['short','long']:
  for headers in ['0','1']:
   for trigger in ['button','ctrlp']:
    if fixture=='short' and headers=='0' and trigger=='ctrlp':continue
    env=os.environ.copy();env.update(PRINT_BROWSER=browser,PRINT_FIXTURE=fixture,PRINT_HEADERS=headers,PRINT_TRIGGER=trigger)
    case='-'.join([browser,fixture,headers,trigger]);start=time.time();r=subprocess.run([sys.executable,'-B',str(base/'consumer-prep/print_case.py')],env=env,capture_output=True,text=True,encoding='utf-8',timeout=100)
    records.append({'case':case,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed':time.time()-start});(base/'matrix-d8de-batch.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8');print(case,r.returncode,r.stdout.strip(),flush=True)
    if r.returncode:sys.exit(r.returncode)
