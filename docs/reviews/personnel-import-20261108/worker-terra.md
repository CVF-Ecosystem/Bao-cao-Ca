# Terra worker return — PNI integration

Risk: R2
Worker: Terra
Reviewer: Astra
Status: RETURNED_FOR_REVIEW

## Result and scope

Implemented E1–E5 integration within assigned files: four bounded endpoints and server-owned single-use preview, additive catalog owner with precondition refusal and retained verified backups, manual Excel mapping/preview/confirmation UI, version and user/API notes. All test data were synthetic and all catalog/DB operations used disposable temporary roots. No team assignment, schema/auth, report-format or operational-data changes. E6 product, native Windows EXE, independent review and milestone acceptance remain pending; Root owns full release and Sol owns native proof.

## Validation

- `PYTHONPATH=ma_nguon; PYTHONIOENCODING=utf-8; python -B -m unittest kiem_thu.KIEM_THU_PERSONNEL_API kiem_thu.KIEM_THU_DANH_MUC -v`: exit 0, 16 tests, 0 skips. Raw `.cvf/runtime/personnel-import-20261108/terra-focused.txt`.
- `node kiem_thu/KIEM_THU_PERSONNEL_UI.js`: exit 0, escaped sample and nonce invalidation. Raw `.cvf/runtime/personnel-import-20261108/terra-ui.txt`.
- `node --check giao_dien/tai_nguyen/danh_muc.js`: exit 0.
- Initial API test run: 3/5 passed, 1 failed and 1 errored because an openpyxl-generated fixture was rejected by the first reader revision. Sol corrected relationship namespace. Second run: 4/5 passed, 1 failed because integration passed a tuple to list concatenation; Terra corrected the owner operation. Both defects were retained here rather than relabelled; the final focused run above passed.
- Tests cover inspect/preview/confirm, no-op/replay, old report/revision snapshots, unchanged other catalog bytes, inactive refusal after startup, stale/expired/cancelled context, duplicate JSON/bool index, backup failure, verified rollback, restore failure, and preserving a detected external edit. Not every injected boundary, real GUI or clean packaged EXE is independently proven by this slice; see Astra review and Root/Sol remaining work.

## Changed source and SHA-256

- `ma_nguon/MAY_CHU.py`: ff37a6ae05e226c27e6a950ffddad2d9bf40da7ea12a69b2405410e4cacc24e6
- `ma_nguon/QUAN_LY_DANH_MUC.py`: 0611034808a8c8dc92cdfdec2c70d524b75ce138e72ff3c544cb62c59dcb1490
- `ma_nguon/THIET_LAP.py`: c977b4f80889c604be4882a0965a3561246313d47b472bf4fff6693d6d8671f1
- `giao_dien/tai_nguyen/danh_muc.js`: 16e13337158f444635214909a5f0215aee9d2279cfaf4f9aecccb793fdf42a46
- `kiem_thu/KIEM_THU_PERSONNEL_API.py`: 64165d5f8cfdfd9f128de8f739c197349255e392316719ccd9d62cd5f7c9a7e3
- `kiem_thu/KIEM_THU_PERSONNEL_UI.js`: 1ca5517e71f6766d5404311ab0cc5cf89e665855c550b2798599217c7f68b72b
- `tai_lieu/API.md`: 23e11bd7d237a0effc7194aef49ef1c80a3f8679cd86f923ba2023e13f27a585
- `tai_lieu/THAY_DOI_V1_9_2.txt`: 28a96e9222d59c6cb0026bea82a835778e9297913118fc1ad310d37c6be01c0a
- `HUONG_DAN.txt`: 23e970d602f9993e1b2a40fb6ba45791f98ff41cce852b7f9fbfc6ee2dba1fd0

Worker return does not claim milestone completion, full-suite pass, governance behavior, release or business acceptance. Source is subject to independent review and changes require refreshed hashes and affected tests.

## Same-scope repair round 1 — F6/F7

Role: REPAIR_WORKER. The prior return and initial failed checks above remain historical. The first F7 injection initially intercepted the earlier `raw_digest` read, yielding `STALE` rather than the intended backup-read `SAVE_FAILED`; the injection was narrowed to the actual backup read call and the final suite passed. No production data used.

F6: per-dialog object/generation/context and visible-dialog guards discard late inspect/preview/confirm responses; file selection clears file/hash/sheets immediately even when invalid; cancel closes immediately and cannot close a later dialog. Deterministic asynchronous UI tests cover stale preview after selection change, invalid replacement, delayed inspect and cancel, changed context and closed dialog during confirm.

F7: tests exercise original backup read, backup verification read, backup write, temp write/fsync/replacement, actual SQLite DELETE-trigger failure, post-sync verification, restore write/replacement failure, retained backup and DB/file outcomes, auth cookie/header/origin, viewer and review-copy. Existing tests cover rollback, inactive state and external file edit. Simulated fault evidence is local technical proof, not a provider-governance claim.

- `PYTHONPATH=ma_nguon; PYTHONIOENCODING=utf-8; python -B -m unittest kiem_thu.KIEM_THU_PERSONNEL_API kiem_thu.KIEM_THU_DANH_MUC -v`: exit 0, 23 tests, 0 skips; `.cvf/runtime/personnel-import-20261108/terra-repair1-final.txt`.
- `node kiem_thu/KIEM_THU_PERSONNEL_UI.js`: exit 0; `.cvf/runtime/personnel-import-20261108/terra-repair1-ui.txt`.
- `node --check giao_dien/tai_nguyen/danh_muc.js`: exit 0.
- Reviewer-local F1–F5 retained; reviewer and Root own source re-review and full aggregate, respectively. E6/native proof remains pending.

Current SHA-256 after LF normalization (supersedes initial byte hashes, not historical record):

- `ma_nguon/MAY_CHU.py`: ca55728d8dc6e7204a5fdcdcbd5b29d16276b49fce334318f87324bf5e74d1c9
- `ma_nguon/QUAN_LY_DANH_MUC.py`: 681a3c102d8155bfb6d676c615e6b9d09e37e6e7411089ce9b2e41c412e75924
- `ma_nguon/THIET_LAP.py`: bf5164a7a8bfe6736c4cd12f550579beb4d2716853ea12a9b6d3cc90976fdeaf
- `giao_dien/tai_nguyen/danh_muc.js`: e26ad47170705ec7ea3c24969415d495998b31f5fe0cb4fc05b35d7e81cd56e2
- `kiem_thu/KIEM_THU_PERSONNEL_API.py`: 85792e14fb159d0ef33c441a35e01ffd36901f0d06d8ddcbd61b7021e5bcf6d3
- `kiem_thu/KIEM_THU_PERSONNEL_UI.js`: fed21a9ecba8e7a9e5560c3b1a8691aa10b9de5f489550713ae00eba2125c60c
- `tai_lieu/API.md`: 9b2550f3efc92b82fa6ba093dba61bac3a2919eb774457661c1868aaae535ecd
- `tai_lieu/THAY_DOI_V1_9_2.txt`: 57bacd1f3022728e56e464a329727f4d373bdd414a15ddfa72652c8feccee3c4
- `HUONG_DAN.txt`: 637b764ab56acacfb6c5c8b89c78425c5f2163f6d3ef18f0e27e370f86aa1bac
