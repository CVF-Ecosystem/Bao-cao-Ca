import datetime as dt, hashlib, importlib.util, json, os, platform, random, shutil, sqlite3, sys, time
from pathlib import Path
root=Path(__file__).resolve().parent
old=root/'baseline-source'
spec=importlib.util.spec_from_file_location('baseline_benchmark',old/'cong_cu'/'DO_HIEU_NANG.py'); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
work=root/'baseline-data'; work.mkdir(exist_ok=False); directory=work/'DU_LIEU'; directory.mkdir()
db=directory/'BAO_CAO_CA.db'; store=module.Store(db); rng=random.Random(20261106)
reserve=5*2**30
def guard(extra=0):
    free=shutil.disk_usage(work).free
    if free < reserve+extra: raise RuntimeError(f'disk guard: {free} bytes free, reserve {reserve}, needed {extra}')
    return free
if guard()<15*2**30: raise RuntimeError('less than 15 GiB before seed')
result={'baseline_commit':'7ce0305b6000f4895be4910a93d9bf9d9a01ad95','baseline_tool_sha256':hashlib.sha256((old/'cong_cu'/'DO_HIEU_NANG.py').read_bytes()).hexdigest(),'python':platform.python_version(),'platform':platform.platform(),'seed':20261106,'started_at':dt.datetime.now().astimezone().isoformat(),'profile':module.PROFILES['lon'],'free_before':guard(),'attachment_semantics':'synthetic JPEG headers and random bytes only; not decodable-image proof'}
start=time.perf_counter(); module.seed(store,result['profile'],rng,lambda s:print(s,flush=True)); result['seed_s']=round(time.perf_counter()-start,2)
with store.connect() as c:
    result['counts']={'reports':c.execute('SELECT count(*) FROM reports').fetchone()[0],'revisions':c.execute('SELECT count(*) FROM revisions').fetchone()[0],'blobs':c.execute('SELECT count(*) FROM attachment_blobs').fetchone()[0],'blob_bytes':c.execute('SELECT sum(length(data)) FROM attachment_blobs').fetchone()[0],'db_bytes':db.stat().st_size}
result['free_after_seed']=guard();result['target_1GB_reached']=db.stat().st_size>=1_000_000_000
result['snapshot_s']=[]
for n in range(2):
    result.setdefault('free_before_snapshot',[]).append(guard(db.stat().st_size*2))
    dest=work/f'snapshot_{n}.db'; start=time.perf_counter();module.snapshot(db,dest);result['snapshot_s'].append(round(time.perf_counter()-start,2))
    dest.unlink()
result['finished_at']=dt.datetime.now().astimezone().isoformat()
(work/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2),flush=True)
