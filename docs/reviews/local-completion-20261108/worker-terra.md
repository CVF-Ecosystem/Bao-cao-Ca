# Backend worker return

Risk: R2
Worker: Terra (IMPLEMENTATION_WORKER)
Reviewer: Astra (independent review pending)

Implemented explicit schema 4 migration with verified recovery copies, save-kind history and provenance, protection pins and full verification, guarded maintenance, ship hiding, capabilities and manifest-bound restricted recovery. Inspection rejects malformed payloads and missing referenced blobs. Schema 4 correction provenance survives import; invalid metadata rolls back. Synthetic fixtures only.

Full suite: `$env:PYTHONPATH='ma_nguon;kiem_thu'; .cvf/runtime/personnel-import-20261108/build-venv/Scripts/python.exe -X utf8 -B -m unittest discover -s kiem_thu -t . -p 'KIEM_THU*.py' -v`: **210 passed, 0 skipped**, 43.070 seconds; `.cvf/runtime/local-completion-20261108/terra-full-isolated-r2.txt`. Expected injected external-disconnection tracebacks occur in passing tests. Actual installed toolchain graph was checked; this does not prove native consumer acceptance.

Earlier outcomes retained under `.cvf/runtime/local-completion-20261108/`: `terra-existing-core-initial.txt` and `terra-existing-core-r1.txt` (fixture/contract corrections); `terra-pni-regression-initial.txt`; `terra-focused-final.txt` (142 tests, outdated 400 assertion corrected to locked 413 LIMIT_EXCEEDED); `terra-full-final.txt` (global interpreter wrong toolchain, startup spy missing keywords, unused test import); `terra-full-isolated-final.txt` (209 pass and one startup spy missing keywords; spy corrected). `terra-review-fixes.txt` has 19 focused passes and `terra-protection-final.txt` has 23. Initial nonexistent `.venv` lookup failed harmlessly. No dependency installation performed. API documentation normalized to LF after test run; no runtime source changed after the run.

No claim of native headed recovery, print, performance target, Python 3.9 runtime, business acceptance or independent review. Outside writers can race stamp checks; recovery retains verified copies. No commit made.

## Frozen worker-owned files and SHA-256

- `ma_nguon/BAO_VE_DU_LIEU.py`: `99cd19b28c051b0f0302dc8f984adfa57ea774908fda0fc78ae2fe768428ab64`
- `ma_nguon/LUU_TRU.py`: `17ba6d6cb64677ef9bffd48b41b5b562bdbbb0a556522684f0fd5f86dad498ab`
- `ma_nguon/MAY_CHU.py`: `929f263a00025f4b22f6436dc6c18473c181b4e53e4e8c445c58e656dd9350f7`
- `ma_nguon/THIET_LAP.py`: `628e0ed165749760adca22ab5cb9c1f751aed181389c2871ae7e39b0ff12da0e`
- `ma_nguon/BAO_TRI_CSDL.py`: `902f231f59f0d2fe151588c9501d5f5b18cd80722e24c537f1500d5608f0084a`
- `ma_nguon/NANG_CAP_CSDL.py`: `7cc26e6abffb46ebaef702c4bbaa7dda5a07413e2f43d7a8339d676b4a113f99`
- `kiem_thu/KIEM_THU.py`: `e83634b4ba55421b47ec4fab97a4aee29139f7c06e128dd7725cbd1baac48b4d`
- `kiem_thu/KIEM_THU_API.py`: `6065b3c30f83b73ccc1b5c608db963b3da65d678484911ca5f5c0a3018d97fd1`
- `kiem_thu/KIEM_THU_V1_9.py`: `a12622df1027ac2edc006056deb06381aa52d24a5f8af12727209dad2270f27c`
- `kiem_thu/KIEM_THU_KHOI_DONG.py`: `d22c31a41ecb56e28a48132a16815e1d2a52c1ac343e55108f339d4902b6e425`
- `kiem_thu/KIEM_THU_LOCAL_COMPLETION.py`: `255e0915c818355bf303e69beb376ad97dfa76ffaa6cf6beb605a0584e6d1b68`
- `tai_lieu/API.md`: `d19e0850e52ba8be10260b2c992460b95b30d929a06a466f2f57c6c4ebcd525b`
