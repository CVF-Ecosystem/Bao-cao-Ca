import cProfile, hashlib, json, pstats, sqlite3, time
from pathlib import Path
from BAO_VE_DU_LIEU import Protection, inspect_db
from NGHIEP_VU import ClosingConnection
base=Path('.cvf/runtime/local-completion-20261108/fixtures-terra/benchmark/do_hieu_nang_k2rzn8ud').resolve()
root=base.parent/'profile';root.mkdir(exist_ok=True)
db=base/'DU_LIEU'/'BAO_CAO_CA.db'; protection=Protection(db.parent)
cache=protection.config['verified_cache']; assert cache['database_id']==protection.config['database_id']
with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,factory=ClosingConnection) as c:
 identity=c.execute("SELECT value FROM meta WHERE key='database_id'").fetchone()[0]
assert identity==cache['database_id']; verified=cache['hashes'];assert len(verified)==200
sidecars=lambda:{x.name:x.stat().st_size for x in db.parent.glob('BAO_CAO_CA.db*')}
def digest():
 with db.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
res={'before_sha256':digest(),'sidecars_before':sidecars(),'dataset_id':identity,'cache_count':len(verified),'profiles':{}}
(root/'partial.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
for level in ('full','quick'):
 print('Profiling',level,flush=True); p=cProfile.Profile();t=time.perf_counter();p.enable()
 try: info=inspect_db(db,level=level,verified=verified if level=='quick' else None)
 finally: p.disable()
 elapsed=time.perf_counter()-t
 with (root/(level+'-top20.txt')).open('w',encoding='utf-8') as stream: pstats.Stats(p,stream=stream).strip_dirs().sort_stats('cumulative').print_stats(20)
 p.dump_stats(str(root/(level+'.prof')))
 res['profiles'][level]={'seconds':round(elapsed,3),'reports':info['reports'],'revisions':info['revisions'],'verified_count':len(info['verified_hashes'])}
 (root/'partial.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
res['after_sha256']=digest();res['sidecars_after']=sidecars();res['unchanged']=res['before_sha256']==res['after_sha256']
(root/'result.json').write_text(json.dumps(res,indent=2),encoding='utf-8');print(json.dumps(res,indent=2),flush=True)
