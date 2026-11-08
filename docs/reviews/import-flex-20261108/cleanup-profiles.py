"""Remove only frozen, stopped browser test profiles from the reviewed FLEX plan."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
root=Path.cwd().resolve(); review=root/'docs/reviews/import-flex-20261108';planfile=review/'profile-cleanup-plan.json'
assert hashlib.sha256(planfile.read_bytes()).hexdigest()=='0c02d16dd1d75f31810fe15c4a6b17342fbee41586d7b41916a8a11ae8bbc77e'
plan=json.loads(planfile.read_text(encoding='utf8'));base=root/'.cvf/runtime/local-completion-20261108'
tracked=set(subprocess.check_output(['C:/Program Files/Git/cmd/git.exe','ls-files','-z'],cwd=root).decode().split('\0'))
procs=json.loads(subprocess.check_output(['C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('chrome.exe','msedge.exe','python.exe','pythonw.exe') } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],text=True) or '[]')
if isinstance(procs,dict):procs=[procs]
cmds=[(x.get('CommandLine') or '').casefold().replace('\\','/') for x in procs]
def inventory(p):
 result=[]
 for folder,dirs,files in os.walk(p,followlinks=False):
  for q in [Path(folder)]+[Path(folder)/n for n in dirs+files]:
   s=q.lstat();assert not q.is_symlink() and not(getattr(s,'st_file_attributes',0)&1024),'Reparse path'
  for n in files:
   q=Path(folder)/n;s=q.stat();result.append([q.relative_to(p).as_posix(),s.st_size,str(s.st_mtime_ns)])
 return sorted(result)
result={'mode':'EXECUTE' if '--execute' in sys.argv else 'PRECHECK','planSha256':hashlib.sha256(planfile.read_bytes()).hexdigest(),'profilesPlanned':len(plan['targets']),'bytesPlanned':plan['totalBytes'],'freeBefore':shutil.disk_usage(root).free,'eligible':[],'deleted':[],'skipped':[]}
for t in plan['targets']:
 p=root/t['path']
 try:
  assert p.name in ('chrome-profile','msedge-profile') and p.resolve(strict=True)==p.absolute() and p.resolve().is_relative_to(base.resolve()),'Target boundary'
  q=p
  while q!=root:
   assert not q.is_symlink() and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'Reparse ancestor'
   q=q.parent
  assert not any(f==t['path'] or f.startswith(t['path']+'/') for f in tracked),'Tracked path'
  assert not any(p.as_posix().casefold() in c for c in cmds),'Profile still active'
  assert inventory(p)==sorted(t['files']),'Profile changed'
  result['eligible'].append({'path':t['path'],'bytes':t['bytes']})
  if '--execute' in sys.argv:
   shutil.rmtree(p)
   result['deleted'].append({'path':t['path'],'bytes':t['bytes']})
 except (OSError,AssertionError) as e:result['skipped'].append({'path':t['path'],'reason':str(e)})
result['deletedBytes']=sum(x['bytes'] for x in result['deleted']);result['freeAfter']=shutil.disk_usage(root).free;result['freeDelta']=result['freeAfter']-result['freeBefore']
result['remainingProfiles']=[t['path'] for t in plan['targets'] if (root/t['path']).exists()]
result['preservation']='Only exact old test-browser profile trees; all nonprofile files, wheels/venv, scripts/logs, real data/backups, workbook and delivered EXEs untouched.'
(review/('profile-cleanup-result.json' if '--execute' in sys.argv else 'profile-cleanup-precheck.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ('eligible','deleted','remainingProfiles','preservation')},indent=2))
