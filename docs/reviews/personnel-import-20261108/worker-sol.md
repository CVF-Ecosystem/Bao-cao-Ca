# Sol reader and packaging worker return

Status: SOURCE_READY_NATIVE_PENDING
Risk: R2
Worker: Sol
Reviewer: Astra (independent; acceptance pending)

## Authority and scope

Acknowledged BUILD continuity and exact work order fbc56001358dc6ada77207a780b9d213d8c152b8ee808b95a5a9efdce7419f20 before implementation. Only the nine assigned product/test/dependency paths below changed by this worker; this return is separately allowed. No worker commit, operational-data access, Core/gate mutation, provider invocation or deployment. Root owns aggregate gates/commit and Astra independent acceptance.

## Slice result

E1/E2/E5 reader/planner implemented: strict personnel header mapping, full bounded archive/XML preflight before library loading, streamed all-sheet physical-coordinate and duplicate checks, formula refusal even on excluded mapped rows, type/name/code conflict/exclusion oracle, NFC/casefold exact catalog match, preserved zero-prefixed text codes and non-merging close-name warning. Near-name warning uses accent folding or a single-character edit comparison with linear work per pair; it does not change identity. No filesystem/catalog/database/network persistence in reader functions.

E6 build preparation implemented: clean-tree checks retained before toolchain and before metadata, no automatic pip/network in builder, exact installed tool/runtime version checks, copied frozen runtime metadata, explicit defusedxml collection, ambient lxml excluded and full third-party wheel license notices bundled. Actual EXE/native acceptance remains pending. TAO_FILE_EXE uses active python environment instead of the py launcher overriding the activated environment.

## Focused proof

Actual commands used isolated `.cvf/runtime/personnel-import-20261108/build-venv/Scripts/python.exe -B`:

- `-m unittest kiem_thu.KIEM_THU_PERSONNEL_XLSX kiem_thu.KIEM_THU_PHAT_HANH -v`:24tests PASS,0skip,2.322seconds on final run. Includes source launcher smoke on temporary data (no headed UI).
- `-m pip check`:exit0, no broken requirements.
- AST parse of changed Python sources with feature_version=(3,9):PASS. This is syntax compatibility only; no Python3.9 interpreter was available.

Raw local logs: `.cvf/runtime/personnel-import-20261108/sol-focused-tests.txt`, `dependency-install.log`, `wheel-verification.json`, `sol-source-manifest.json`. Root may bind sanitized durable excerpts as evidence. Early first reader run failed three valid-workbook tests due to trailing slash in the relationship XML namespace; corrected to the actual namespace and reran successfully. A shell quoting attempt to apply that correction raised SyntaxError and changed no source; apply_patch then applied the correction. Initial notice extraction missed British-spelled LICENCE filenames; extraction was corrected and all ten wheel license sets included. No failed result is counted as PASS.

## Isolated dependency provisioning

Downloaded only ten reviewed official wheel URLs from source-review.json, SHA-256 checked each before writing and installation. Created isolated Python3.11.9 venv at the admitted path; invoked pip install with `--no-index --find-links <verified-wheelhouse> --only-binary=:all: --require-hashes -r requirements-build.txt`, exit0. No source distribution, arbitrary source URL or global upgrade. Exact runtime:openpyxl3.1.5,defusedxml0.7.1,et-xmlfile2.0.0; build:PyInstaller6.14.2,altgraph0.17.4,packaging24.2,pefile2023.2.7,pyinstaller-hooks-contrib2025.5,pywin32-ctypes0.2.3,setuptools84.1.0. Python>=3.10 is required for tooling; source/runtime target remains3.9+. Installed global setuptools78.1 was not used for the build environment. Hash verification binds downloaded wheel identities, not an independent security certification.

## Changed source custody

| Path | SHA-256 of current raw bytes |
|---|---|
| `ma_nguon/PERSONNEL_XLSX.py` | `2a57344e30023abb024156362d6b228cd8934003be68b161c88eb405b7886859` |
| `kiem_thu/KIEM_THU_PERSONNEL_XLSX.py` | `63f8fbe823c0a1da5d981d430df64c5ace0a5dc30845a5798584f9a278248085` |
| `requirements.txt` | `214614443a22797d6f31d94ca4f077de2924bd29155ca8732fd989df1fc41233` |
| `requirements-build.txt` | `8f7260fe41b9a1e4ce9d69df5e304859bb89c42f3f8de09323ddae4ab4e0d9a5` |
| `THIRD_PARTY_NOTICES.md` | `dc103575eb2cacf30cde153ebd971c9cdb6be30081b19c08faa703222c4ebf51` |
| `pyproject.toml` | `eac0217bab0d0dfe41e20441f879befbd6ad68843383323c6bbd3710f96182db` |
| `cong_cu/DONG_GOI.py` | `8da6cb1953d5fc2aae035f60a1b2863d977b2c481c4232aef3c37b9b0d839159` |
| `cong_cu/TAO_FILE_EXE.bat` | `27f310cec50bcb5b09fa7f5a8413418a659ce083977c778eefcf256d7271823e` |
| `kiem_thu/KIEM_THU_PHAT_HANH.py` | `1dc57cd6908acffb08decdc6aa3a57e3674868b3512ef70061d6d221145994fe` |


## Remaining and next owner

Tranche: source slice ready for independent review; Root owns aggregate release/gates. Product: E1–E6 not collectively accepted, E3/E4 belong to Terra, and E6 actual clean-commit Windows binary/headed import/person-picker/save/restart/export and old-report invariants still open. Sol owns that proof only after Root supplies the independently reviewed clean committed candidate. Full release and same-list manual-versus-import time/step comparison remain required. No no-skip or product completion inference comes from focused tests. E7 and original roadmap gaps remain separately owned.

## Post-review custody — LF normalization (2026-11-08)

Root requested owner-only LF normalization after Astra reviewer-local reader/test corrections (referenced-sheet preflight, Unicode separators and locked near-name warning). Rehydrated canonical REVIEW continuity and transitioned to REPAIR_WORKER. Preserved original return/hashes/failure history above. Normalized only the nine assigned files to LF and verified unchanged non-CR bytes. Initial normalization assertion detected residual CRLF in bundled third-party notice text originating from duplicated carriage returns; the remaining CRLF pairs were normalized and final assertion confirms no CR remains in any of the nine files. No text/token/behavior changes were made, and Astra corrections remain intact. Astra targeted regression evidence `astra-local-regressions.txt` records32 PASS; no duplicate behavior suite is warranted solely for newline replacement. Root owns the final aggregate release after Terra UI repair. No EXE/native proof or acceptance claimed.

| Path | Current raw SHA-256 |
|---|---|
| `ma_nguon/PERSONNEL_XLSX.py` | `58f083074587553f3d62e66ba01105143c9e5576dc0ff397245d53bd23d563d2` |
| `kiem_thu/KIEM_THU_PERSONNEL_XLSX.py` | `7cd5373db2f468e9bebcb2081a57c5f18fa71fed4d6b49a7d87e859a2175cdc7` |
| `requirements.txt` | `6277d17aa658a18f49d19ef8e43b8a5be0477a072ae19bf52e0613fec23b74e9` |
| `requirements-build.txt` | `81acdaa00dfe39a7beb2c7c5e04c609ab4befc66a02ff566579360959d87e8b3` |
| `THIRD_PARTY_NOTICES.md` | `56d1d2fcdeb4683a870c822f02564ca44926564d524d5994d8d5f14fbbf02fdb` |
| `pyproject.toml` | `0e1f9df3707ec1a335d1ceb30829c9ef63a49f4c5cab9972bb92456625fb481e` |
| `cong_cu/DONG_GOI.py` | `8da6cb1953d5fc2aae035f60a1b2863d977b2c481c4232aef3c37b9b0d839159` |
| `cong_cu/TAO_FILE_EXE.bat` | `823e72787bf8a61fabd41798425e8f0f601865f720a37ebd6077242c42af82b4` |
| `kiem_thu/KIEM_THU_PHAT_HANH.py` | `1dc57cd6908acffb08decdc6aa3a57e3674868b3512ef70061d6d221145994fe` |

## Same-scope repair round1 — F8 structural refusal evidence

Repair risk remains R2. Role: REPAIR_WORKER. Rehydrated BUILD canonical continuity and acknowledged the consolidated round1 handoff/exact fbc560 work order before this evidence repair. No reader implementation, locked SPEC/ADR, dependency, packaging or native runtime behavior changed. Reviewer-local preflight/Unicode/near-warning fixes preserved. Only reader tests and the assigned worker/native evidence paths changed.

Decisive proof uses bounded in-memory reads of all three actual reference workbooks, with SHA-256 equality to prior source-observations.json required before processing and verified unchanged afterward. No personal cell values, workbook bytes or inspection samples are retained. `native/report-structure-refusals.json` binds exact source and reader hashes, prior structural observations and selected mapping, refusal codes/locations and safe reasons. Results:

| Required reference | Inspect | Plan/import eligibility |
|---|---|---|
| Bai cont ca.xlsx (`03040121…`) | Bounded inspection only; samples discarded | INVALID_INPUT at N09-9 row1 col2; report header cannot be mapped to personnel name. |
| Thu tuc ca.xlsx (`96c5f7e4…`) | INVALID_INPUT; unsupported workbook relationship | INVALID_INPUT; rejected before a plan exists. |
| Dieu hanh ca.xlsx (`2586a272…`) | INVALID_INPUT; unsupported workbook relationship | INVALID_INPUT; rejected before a plan exists. |

Additionally added a reproducible three-profile synthetic regression (separate subcases): N09-9 A1:I27 with3observed merges/no formulas; T10 A3:F581 scale with15observed merge ranges/151synthetic formula cells;10.2025 A1:G77 with3observed title merges/no formulas. This is a structural representative, not an exact clone of source cells/row occupancy or all unknown formatting/relationships. Actual-reference proof above is authoritative for the three required files; the synthetic regression independently prevents report-shaped headers being accepted as manually mapped personnel tables. All fixture values/formulas are invented.

Focused command: isolated build-venv Python3.11.9 `-B -m unittest kiem_thu.KIEM_THU_PERSONNEL_XLSX -v`:17tests PASS,0skip,1.087seconds. Raw retained log copied to `native/F8-reader-tests.txt`. Direct actual-reference probe asserted all three plan outcomes REFUSED, exit0. A follow-up console attempt to print a safe Vietnamese reason encountered cp1252 UnicodeEncodeError (no source mutation); safe reasons were subsequently retained as UTF-8 JSON instead. No failure hidden or counted as PASS. Root owns aggregate release and Astra independent F8 disposition. E6 still pending clean reviewed candidate; no app/EXE/native launch.

| Current artifact | Raw SHA-256 |
|---|---|
| `kiem_thu/KIEM_THU_PERSONNEL_XLSX.py` | `c37e4499ed5b28863e2088fa1366c1f58a1f4ea23d1cdff02e4b61bce1e6ede9` |
| `ma_nguon/PERSONNEL_XLSX.py` | `58f083074587553f3d62e66ba01105143c9e5576dc0ff397245d53bd23d563d2` |
| `docs/reviews/personnel-import-20261108/native/report-structure-refusals.json` | `218fea2a34d39766dfd283a284441402b2b2bacc966754ff2e2a9822dd0be7be` |
| `docs/reviews/personnel-import-20261108/native/F8-reader-tests.txt` | `e3e4eb16442d336505fab4fb84a211e3fc0e72ceaaa30ad48cbe61fe3bf57b00` |

## r3 build-graph compatibility repair return

Status: DELTA_SOURCE_READY_NATIVE_PENDING
Repair narrative Risk: R2
Repair narrative Worker: Sol REPAIR_WORKER
Repair narrative Reviewer: Astra independent review pending

Rehydrated BUILD continuity and acknowledged exact r3 work order7bf5cb359e772a81d836278cecd81dede12aee8b1f494fb01961bcb6e5c25a9c before writes. Original failed candidate378dab6149d5 and its log/observation remain retained. Actual failure established altgraph0.17.4 imported pkg_resources absent from setuptools84.1.0; original test-version-only gap is preserved, not relabeled successful. Applied only the admitted locked build compatibility amendment: altgraph0.17.5 official wheel SHA-256 f3a22400bce1b0c701683820ac4f3b159cd301acab067c51c653e06961600597, length21228, verified before install. Downloaded exactly one official files.pythonhosted.org wheel from reviewed metadata; installed using existing isolated venv pip `--no-index --find-links <reviewed-wheelhouse> --only-binary=:all: --require-hashes --no-deps -r <single-pin-lock>`, exit0. No other pin or global environment changed.

Changed only four admitted build/test files below: exact requirement/version/license notice replacement, actual import preflight of altgraph and PyInstaller.building.build_main after exact version checks and before metadata/build, meaningful missing-import regressions proving no metadata/subprocess build effects, and a real installed full graph import test. Both clean-tree gates, offline builder and frozen runtime collection remain intact. Full application/runtime/reader/SPEC/ADR bytes untouched by this worker.

Focused command: isolated Python3.11.9 `-B -m unittest kiem_thu.KIEM_THU_PHAT_HANH kiem_thu.KIEM_THU_MA_NGUON -v`:16tests PASS,0skip,1.260seconds; includes actual installed-toolchain import and source launcher smoke. No EXE build, packaged smoke or native launch performed during repair; awaiting new independently reviewed clean candidate. Raw local evidence: sol-r3-focused-tests.txt, altgraph-r3-install.log and altgraph-r3-wheel.json under ignored runtime. Original180/45 ceilings and repair history continue; no reset. Root owns aggregate release/gates/commit and Astra independent delta review.

| Current raw artifact | SHA-256 |
|---|---|
| `requirements-build.txt` | `5464a122989898d0649ac2c703311ca64b0a480b0754be5b20835e0cccfe6818` |
| `cong_cu/DONG_GOI.py` | `2ddad11b77d3a9c3bf6bbc24fe70ecb4687c26c097e105e7133452be4d801479` |
| `THIRD_PARTY_NOTICES.md` | `c64796b63340e6fbd0bf50a7ca7548bd2bbe698941cabd61d9ce958dcffb5c4f` |
| `kiem_thu/KIEM_THU_PHAT_HANH.py` | `1f0b9b83176cd7b696b454721a588ebfadd041bd3e9083f7134a4cefba2eba04` |
