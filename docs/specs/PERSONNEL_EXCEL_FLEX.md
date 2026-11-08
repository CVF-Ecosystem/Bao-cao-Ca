# Flexible ordinary personnel XLSX import — bounded amendment

Status: LOCKED_FOR_ADMISSION
Date: 2026-11-08
Version: 1.10.1; schema4 unchanged

## Authority and inherited contracts

Operator explicitly requests further runtime cleanup and more flexible Excel import after the shown normal employee workbook was refused. Original PNI SPEC/ADR and LOCAL acceptance remain historical immutable baselines; this amendment supersedes ONLY the reader acceptance/header suggestion/numeric-code rules below. Reuse reader/planner, existing preview/nonce/server/additive catalog owner; no arbitrary Excel execution, group assignment or identity migration. No new dependency/network.

## Reader acceptance

Accept canonical inert printer-settings parts ONLY: exact xl/printerSettings/printerSettingsN.bin path (positive decimal N), exact standard printerSettings content type, exact internal worksheet printerSettings relationship to that part, bounded <=64KiB per part plus existing member/archive/ratio limits. Validate ownership/target/type and reject unreferenced/wrong-type/misplaced/oversized parts. Never execute/interpret driver data. All other arbitrary binary, macro/VBA/ActiveX/OLE/external relationships remain refused. XML uses existing actual defusedxml path and all original ZIP/sheet/cell limits remain. A worksheet title merged wholly above selected header remains accepted under existing rule; merged selected data table remains refused.

Code cells may additionally be finite nonnegative integral numbers up to15decimal digits; reject bool/date/nonintegral/negative/oversized values and ambiguous numeric formats. General, text format @, and pure zero masks of1..32zeros only; zero-mask padding preserves visible leading zeros. Existing text codes stay exact after existing normalization. Preview shows converted code and a nonblocking explanatory message; code uniqueness/blank/duplicates and names-only persistence remain unchanged. No formula evaluation; mapped formula including excluded rows still refuses.

Header normalization stays whitespace/NFC/casefold. Closed aliases expand for ordinary accents/no-accents/English names (not arbitrary substring matching): name: existing plus ho va ten,ho ten,ten nhan vien,ho ten nhan vien,ho va ten nhan vien,họ tên nhân viên,họ và tên nhân viên,full name,employee name; code: existing plus mscd,msnv,mã nv,ma nv,ma nhan vien,employee id,employee code; title: existing plus chuc danh,chức vụ,chuc vu,vị trí,vi tri,job title; group: existing plus nhom/ca,to nhan su,tổ,to,nhóm,nhom,ca,thời gian làm việc,thoi gian lam viec,shift,team. Do not silently map bộ phận to a group. Preserve minimum recognized name plus another recognized mapped personnel column and existing three report-workbook refusal evidence.

## UI behavior

Suggest unique recognized header row/column mappings from the existing20x20 bounded inspection sample on selecting/changing a sheet. Actual target suggests row2/nameB/codeC/titleD/groupF. No positive unique match/ambiguous duplicate header rows or duplicate role columns means no guessed mapping for that ambiguity; user selects explicit eligible fields manually, can clear optional ones. Backend always revalidates. Explain row/column suggestions are editable; changes invalidate pending nonce. No hidden automatic import or API/session/security changes.

## Cleanup and delivery

Only44 exact inactive owned chrome-profile/msedge-profile trees from profile-cleanup-plan.json under .cvf/runtime/local-completion-20261108,1077402818bytes. Verify resolved absolute roots/ancestors/no reparse, inventory/file size+mtime/tracked exclusion and no process using a target. Delete within one native runtime; skip changed/active/locked trees, no process kill. Preserve all nonprofile data, build-venv/wheels, scripts/logs/durable evidence, real DB/catalog/backups/user workbook and EXEs. Remove newly created owned single-check browser profile only after its process closes and durable sanitized evidence is copied. No automatic startup cleanup feature.

Deliver same-directory versioned1.10.1 EXE built offline from exact reviewed clean short Git producer using existing tools. Retain original source workbook byte-identical. Reader unit/security negatives + affected UI checks and required source/package smoke only; inherit unrelated accepted source evidence. ONE disposable actual-workbook headed flow verifies correct suggestion,63rows/14numeric conversions/0errors against frozen structural oracle with empty fixturecatalog, selected confirm,repeatnoop,newperson availability and exit/restart persistence. Never import into real operational DB. Committed proof contains only hashes/coordinates/aggregate counts/digests and no personnel records or screenshots of private names. A synthetic fixture may show UI if necessary. No broad release/bigdata/performance/print matrices.

## Acceptance layers and five evidence answers

Job: use normal staff workbook with inert print metadata and numeric codes; output editable preview and deliberate additive names. Standard: inherited nonce/catalog/preservation rules plus explicit bounded amendment. Technical: targeted positive/negative parser/UI cases and unchanged full security envelope. Developer-product: exact1.10.1 EXE actual-workbook disposable preview/confirm/noop/restart with expected63names and original file preservation, plus actual cleaned cache bytes. Value: formerly rejected supported workbook now usable; no speed claim. Delivery: exact reviewed source/EXE/hash, guide, same-directory DATA location and no production mutation. Business/yard-device/physicalprinter/web limits remain separate.
