from pathlib import Path
import os,json,subprocess,shutil,hashlib,sys
root=Path.cwd().resolve()
review=root/'docs/reviews/local-completion-20261108'
plan_path=review/'runtime-cleanup-plan.json'
plan=json.loads(plan_path.read_text(encoding='utf8'))
assert hashlib.sha256(plan_path.read_bytes()).hexdigest()=='44f88abe93a21b933036837b8c045b99edbbf17e6972726ef7e9097765795a8d'
allowed=[(root/p).resolve(strict=True) for p in plan['allowedRoots']]
assert all(p.is_relative_to(root/'.cvf/runtime/local-completion-20261108') for p in allowed)
tracked=set(subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','ls-files','-z'],cwd=root).decode().split('\0'))
proc=json.loads(subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('SO_BAO_CAO_CA.exe','SO_BAO_CAO_CA_1_10_0.exe','python.exe','pythonw.exe') } | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress"],text=True) or '[]')
if isinstance(proc,dict):proc=[proc]
for x in proc:
 cmd=(x.get('CommandLine') or '').lower().replace('\\','/')
 assert not any(p.relative_to(root).as_posix().lower() in cmd for p in allowed),'Active synthetic fixture process'
checked=[]
for item in plan['targets']:
 p=root/item['path']; actual=p.resolve(strict=True)
 assert actual==p.absolute() and any(actual.is_relative_to(a) for a in allowed),'Unsafe target'
 assert item['path'] not in tracked,'Tracked evidence target'
 cur=p
 while cur!=root:
  s=cur.lstat()
  assert not cur.is_symlink() and not (getattr(s,'st_file_attributes',0)&1024),'Link/reparse target ancestor'
  cur=cur.parent
 s=p.stat();assert s.st_size==item['bytes'] and s.st_mtime_ns==item['mtimeNs'],'Changed target'
 assert p.is_file() and p.suffix=='.db' and s.st_size>=200_000_000
 checked.append((p,item))
assert len(checked)==16
before=shutil.disk_usage(root).free
result={'mode':'EXECUTE' if '--execute' in sys.argv else 'PRECHECK','planSha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'files':len(checked),'plannedBytes':sum(i['bytes'] for _,i in checked),'freeBefore':before,'deleted':[],'skipped':[],'preservation':'Only listed synthetic files. No recursion/process termination/operational DB access. Durable evidence and fixture generators remain; removed bulk payloads no longer retained for replay.'}
if '--execute' in sys.argv:
 for p,i in checked:
  try:
   s=p.stat()
   if s.st_size!=i['bytes'] or s.st_mtime_ns!=i['mtimeNs']:raise ValueError('Changed before unlink')
   p.unlink()
   result['deleted'].append({'path':i['path'],'bytes':i['bytes']})
  except (OSError,ValueError) as e:result['skipped'].append({'path':i['path'],'error':str(e)})
 result['deletedBytes']=sum(x['bytes'] for x in result['deleted'])
 result['freeAfter']=shutil.disk_usage(root).free
 result['freeDelta']=result['freeAfter']-before
 result['remainingTargets']=[i['path'] for p,i in checked if p.exists()]
 exe=root/'SO_BAO_CAO_CA_1_10_0.exe'
 result['deliveredExeSha256']=hashlib.sha256(exe.read_bytes()).hexdigest()
 assert result['deliveredExeSha256']=='10aaf013cabee0fc3b3139a0ae2605bd5f0393bbfecb9d42ff3ca6a32a648917'
 (review/'runtime-cleanup-result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
else:(review/'runtime-cleanup-precheck.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['deleted','preservation']},indent=2))
