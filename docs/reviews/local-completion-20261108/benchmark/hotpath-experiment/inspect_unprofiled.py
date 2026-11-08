import hashlib,json,sqlite3,sys,time
from pathlib import Path
from BAO_VE_DU_LIEU import inspect_db,Protection
from NGHIEP_VU import ClosingConnection
base=Path('.cvf/runtime/local-completion-20261108/fixtures-terra/benchmark/do_hieu_nang_k2rzn8ud').resolve(); db=base/'DU_LIEU'/'BAO_CAO_CA.db'; p=Protection(db.parent)
cache=p.config['verified_cache'];assert cache['database_id']==p.config['database_id'] and len(cache['hashes'])==200
with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as c: assert c.execute("SELECT value FROM meta WHERE key='database_id'").fetchone()[0]==cache['database_id']
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def sidecars():return {x.name:x.stat().st_size for x in db.parent.glob('BAO_CAO_CA.db*')}
r={'phase':sys.argv[1],'source_sha256':sha(Path('ma_nguon/NGHIEP_VU.py')),'db_before':sha(db),'sidecars_before':sidecars(),'cache_count':len(cache['hashes']),'scans':{}}
for level in ('full','quick'):
 t=time.perf_counter();info=inspect_db(db,level=level,verified=cache['hashes'] if level=='quick' else None);r['scans'][level]={'seconds':round(time.perf_counter()-t,3),'result':info};print(level,r['scans'][level]['seconds'],flush=True)
r['db_after']=sha(db);r['sidecars_after']=sidecars();assert r['db_before']==r['db_after'] and r['sidecars_before']==r['sidecars_after'];Path('.cvf/runtime/local-completion-20261108/fixtures-terra/benchmark/profile/'+sys.argv[1]+'-unprofiled.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
