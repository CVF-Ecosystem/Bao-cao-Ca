from pathlib import Path
import json,sys,shutil,sqlite3,hashlib,traceback
from playwright.sync_api import sync_playwright,expect
from consumer_driver import Consumer
sys.stdout.reconfigure(encoding='utf-8');ROOT=Path('.').resolve();B=ROOT/'.cvf/runtime/local-completion-20261108';RUN=B/'maintenance-d8de489';RUN.mkdir(exist_ok=True);source=B/'fixtures-terra/maintenance';oracle=json.loads((source/'oracle.json').read_text(encoding='utf-8'))
if not (RUN/'DU_LIEU').exists():shutil.copytree(source/'DU_LIEU',RUN/'DU_LIEU')
c=Consumer(ROOT/'dist/SO_BAO_CAO_CA.exe',RUN);pw=sync_playwright().start();r={};db=RUN/'DU_LIEU/BAO_CAO_CA.db'
def rows(path):
 with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True) as x:return {t:x.execute('SELECT * FROM '+t+' ORDER BY 1').fetchall() for t in ['reports','revisions']}
r['beforeRows']=rows(db)
try:
 c.launch(pw);p=c.page
 for button,label in [('Dọn bản chỉ xem cũ','viewer'),('Dọn tệp không tham chiếu','orphan')]:
  c.menu('Bảo vệ dữ liệu / Khôi phục');c.click(button);expect(p.locator('#modalBody')).to_contain_text('1 mục có thể thực hiện');c.capture(label+'-preview-one');c.click('Xác nhận thực hiện');p.locator('#modal').wait_for(state='hidden');p.wait_for_load_state('networkidle');c.capture(label+'-completed')
 files={f.name for f in (RUN/'DU_LIEU/DB_KIEM_TRA').glob('*.db')};r['viewerFiles']=sorted(files);assert not set(oracle['viewer_delete_only'])&files;assert set(oracle['viewer_keep'])<=files
 with sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True) as x:
  r['afterBlobHashes']=[z[0] for z in x.execute('SELECT hash FROM attachment_blobs ORDER BY hash')];r['integrity']=x.execute('PRAGMA integrity_check').fetchone()[0]
 assert len(r['afterBlobHashes'])==4 and not set(oracle['orphan_delete_only'])&set(r['afterBlobHashes']);assert set(oracle['references_preserved'])<=set(r['afterBlobHashes']);r['afterRows']=rows(db);assert r['afterRows']==r['beforeRows'];r['backups']=[]
 for backup in (RUN/'DU_LIEU').rglob('*.db'):
  if backup==db or 'DB_KIEM_TRA' in backup.parts:continue
  with sqlite3.connect(backup.resolve().as_uri()+'?mode=ro',uri=True) as x:
   hashes=[z[0] for z in x.execute('SELECT hash FROM attachment_blobs ORDER BY hash')];r['backups'].append({'path':str(backup.relative_to(RUN)),'sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'hashes':hashes,'integrity':x.execute('PRAGMA integrity_check').fetchone()[0]})
 assert any(len(z['hashes'])==5 and oracle['hashes']['old_orphan'] in z['hashes'] and z['integrity']=='ok' for z in r['backups']);c.exit();r['status']='OBSERVED_PENDING_REVIEW'
except Exception as e:
 r['status']='FAILED';r['error']=str(e);r['traceback']=traceback.format_exc();print(r['traceback'])
 try:c.capture('failure')
 except Exception:pass
finally:
 if c.process and c.process.poll() is None:
  try:c.exit()
  except Exception:pass
 c.save_proof();(RUN/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');pw.stop();print(r['status']);sys.exit(1 if r['status']=='FAILED' else 0)
