# Packaging and native-consumer feasibility

Status: DRAFT

Date: 2026-11-08. Author/owner: Sol packaging/native-consumer worker. Documentary feasibility only, prepared for Root admission and Astra independent review. Current canonical state remains DESIGN, no product BUILD. Observed HEAD: `eef6734ba0ff52cc8217de99814dc5b0a082f789`; initial `git status --short` was empty. This report itself subsequently changes the working tree. No EXE build, dependency installation, application launch, browser launch or UI test was performed.

## Authority and rehydration

Read manifest/policy, canonical active state (compact bootstrap absent: BOOTSTRAP_MIGRATION_PENDING), memory, active handoff, implementation truth, docs index, workspace rules, bootstrap log and public Core AGENTS/handoff. Core pin is `68a7446cc35b7f4bfd2e6ca4029d4ee389c8a5b6`, profile1.4, execution PINNED_CORE; supplemental guidance inspection remains separate. Applied lifecycle/product coverage/machine-contract references. `python -B scripts/check_project_workspace.py --json` returned CORE_ASSESSED, CURRENT_ASSESSED, all29 native checks PASS and trusted bootstrap INST/CONT/COV/ACT PASS. That invocation assessed the terminal CRC packet, not an Excel-import implementation order. Controls are INVOKED for that listed scope, not PROVEN_HERMETIC or live AI governance. Canonical knowledge ingest ran from project root into ignored `.cvf/runtime/roadmap-status-knowledge-index.json`; one README chunk, no external POST.

## Observed execution surface

| Surface | Local observation | Consequence |
|---|---|---|
| Python | CPython3.11.9 x64 at `C:/Users/DELL/AppData/Local/Programs/Python/Python311/python.exe`; launcher also lists uv3.13.12, no3.9 interpreter | Native execution can prove3.11 Windows behavior; it cannot prove runtime3.9 compatibility. |
| PyInstaller |6.14.2 installed, package metadata Requires-Python `>=3.8,<3.14` | Existing offline build dependency is available. |
| openpyxl |3.1.5 installed, MIT, Requires-Python `>=3.8`; defusedxml discoverable | Selecting this reader is technically compatible with the3.9 claim, but current project has no declared runtime dependency. Installed presence is not dependency admission or frozen import proof. |
| Browser tooling | Python Playwright1.61.0 installed; Requires-Python `>=3.10`; Node/npm available | Keep browser verification tooling separate from shipped application dependencies, preserving Python3.9+ product scope. |
| Browsers | Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe`; Edge at `C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`; multiple Chromium cache directories | A headed local browser route needs no browser installation. Existence only; launch/session access unproved. |
| Computer use | Session exposes `mcp__cua_repl` and node-repl discovery; read bundled computer-use SKILL.md | Native controls and screen capture are available in principle; runtime must initialize and read returned API docs before use. No native session attached yet. |
| Existing release entry | `cong_cu/CHAY_KIEM_THU.bat` runs Python discovery and every `KIEM_THU*.js`, treats absent Node as failure | Run noninteractive equivalent commands preserving every result and skip count. Pausing .bat is not needed for automated evidence. |

`cong_cu/DONG_GOI.py` checks clean Git before any install/metadata work, then unconditionally runs `python -m pip install pyinstaller`, checks clean Git again and builds onefile/windowed `SO_BAO_CAO_CA.exe`. It bundles `giao_dien`, `mau` and temporary `PHIEN_BAN.json`. Its existing behavior therefore is not an offline build even when PyInstaller is installed. The .bat claim "Internet only if missing" does not match the unconditional pip invocation. Do not invoke it until the admitted packet resolves this concrete mismatch.

## Proposed exact-version build proof

1. Root admits SPEC/criterion authority/exact work order including `cong_cu/DONG_GOI.py` and `kiem_thu/KIEM_THU_PHAT_HANH.py`. Small packaging repair selects the installed pinned PyInstaller without pip/network, fails clearly if missing/wrong version, preserves clean-tree rejection and temporary metadata. Preserve both clean-commit checks unless independently reviewed contract says otherwise. Existing metadata and dirty-tree tests remain; add focused missing-tool/offline-no-pip verification. Never suppress the clean-tree gate to accommodate evidence files.
2. Root COMMIT_STEWARD commits independently reviewed product/dependency/packaging bytes and continuity first. Build only on the resulting completely clean tree; runtime outputs belong in already ignored `build/`, `dist/`, EXE and `.cvf/runtime/` paths. New review documents cannot be left untracked during build. Record full HEAD, expected12-character commit, source hashes, tool/dependency versions, start/end times, exit status and complete build output. Build metadata uses12-character HEAD and UTC timestamp; retain the separate full HEAD mapping. EXE SHA-256 binds the proof; timestamped builds need not be byte-reproducible.
3. Run `python cong_cu/KIEM_THU_KHOI.py --exe <absolute-exe-path> --version <actual-VERSION> --commit <12-character-HEAD>`. The existing tool creates an isolated temporary directory, authenticates the loopback server, verifies `/api/info` metadata and log files, requests shutdown, checks exit0 and session-file removal. It needs no UI. Retain command/output and EXE hash before and after. This is launcher/HTTP proof only.
4. Perform the separate headed E6 flow below on that same hashed EXE. Final evidence documents can be written after the build. If source changes, rebuild from a newly clean committed tree and rerun affected proofs; do not relabel the earlier binary.

Dependency declaration/install plan belongs to SPEC/ADR owner. openpyxl3.1.5 supports3.9, but execution on this host is3.11. Preserve the3.9 source target and use compatibility parsing/checks where available; report absence of3.9 execution explicitly. Do not silently introduce Playwright into runtime requirements or raise product Python minimum.

## Headed/native E6 proof plan

Sol is sole UI controller; Root owns orchestration/commits and Astra consumes screenshots/logs/artifact hashes as independent reviewer without steering shared UI concurrently. Use admitted ignored `.cvf/runtime/personnel-import-20261108/` for durable disposable evidence custody. A unique run root contains EXE copy, browser profile, fixture, downloads and `data/DU_LIEU`; its sibling `data/DANH_MUC` is also disposable. This sibling matters: `make_server` obtains catalogs from `directory.parent / 'DANH_MUC'`, not from inside `--data-dir`. Never use a data-dir whose parent is the actual project root. Protection/lock files and logs must also remain below that run root.

Launch the EXE with explicit absolute `--data-dir` and hidden background process when using Start-Process. Let its browser opening establish the normal native consumer path, or use `--no-browser` plus an explicitly visible controlled browser if necessary; disclose which route ran. Read disposable session metadata to obtain the loopback URL without publishing its launch token. If native control is used, follow the computer-use initialization/guidance/API requirements; no arbitrary helper protocol. If a controlled browser is needed, use the provided CUA tab APIs and their returned documentation. Browser/headed process availability still needs an admitted runtime check.

Use synthetic names only. First create/save a baseline old report through UI, capture its report/revision identity and export before import; freeze a read-only disposable DB/catalog observation. Then:

1. Select the admitted synthetic flat `.xlsx` fixture using the real file-selection/upload UI. Preview exact new/existing/error counts and source rows against a fixture oracle. Exercise cancel and confirm cancellation persistence through UI plus read-only DB/catalog comparison.
2. Reopen preview, confirm valid import, inspect `Chọn người`, select a newly imported person and save a new report. Keep baseline report unchanged. Repeat same import to prove no duplicate names through both visible result and persisted counts.
3. Use `Thoát tool`; verify process exit and session/lock cleanup. Relaunch the same EXE against the same disposable data. Verify imported catalog and the saved new report survive, and open the old report to compare its prior content/revision identity.
4. Export the report through UI. Capture the actual downloaded workbook, size/hash and structural values against the known oracle (no formulas executed). Confirm selected synthetic names/day/period in export. Capture final UI and persistence observations and graceful shutdown.

Evidence packet: full source commit/EXE hash, platform/interpreter/browser versions, fixture bytes/hash and expected rows, launch commands with token redaction, timestamped screenshots of preview/cancel/confirm/person picker/saved report/relaunch/export, observed downloaded file/hash, before/after disposable catalogs/DB report and revision invariants, process exits/logs, release-suite results with skip accounting. UI screenshots prove displayed behavior; read-only persistence/export checks support data truth. API-only insertion of the new report/import is not consumer-flow proof. Avoid broad unrelated feature testing.

Headed app with browser controls can satisfy the web-based desktop consumer path. A source-only browser run or headless DOM/DB test cannot satisfy the actual packaged E6 criterion. Selecting files through browser upload API proves browser submission, but does not prove native Windows file-picker interaction; disclose this if used. A native picker claim requires actual CUA screenshot/action proof.

## Ownership, cost and stop boundaries

Estimated prospective budgets, not measured spend: offline packaging repair/focused tests15–25min (Sol), reviewed commit/clean build and EXE smoke10–20min (Root commit owner, Sol execution), synthetic fixtures/headed E6/evidence30–45min (Sol), independent evidence review15–25min (Astra). Total70–115min excluding product implementation, admission and genuine repair. First feasibility read/report elapsed cost is unmeasured; no monetary model-cost claim.

Stop the affected proof on dirty Git, dependency mismatch, build/metadata mismatch, inaccessible headed/native runtime, escape from disposable roots, incorrect preview or persistence, missing export, app error or failing/skipped mandatory release group. Preserve logs/screenshots. A first causal failure needs a bounded diagnosis; third same-root repair requires REVIEW_COST_ESCALATION_REQUIRED under existing project rules. Do not send the user to perform technical QA; developer and reviewer own this acceptance.

Tranche position: feasibility report drafted; actual packaging repair/build/native proof awaits independent exact admission. Product position: E6 remains unproved, baseline application/EXE acceptance remains open, and proposed E1–E7 have not been admitted by this report. No live provider call or governance-behavior claim is made; no release, installation, operational-data import or commit authority is inferred.

## Proposed exact dependency/reader worker contract

Continuation rehydration on2026-11-08 again found DESIGN/no product BUILD on all canonical surfaces. Role remains documentary packaging/reader feasibility; proposed implementation ownership is not active authority. Root owns prospective1.9.2 version/release notes and rescheduling tentative D2. Sol will not edit those shared files.

| Proposed Sol-owned path | Bounded responsibility after admission |
|---|---|
| `ma_nguon/PERSONNEL_XLSX.py` | Pure bounded reader/planner, hardened XML/ZIP preflight and explicit errors, no catalog/DB/network/file persistence. |
| `kiem_thu/KIEM_THU_PERSONNEL_XLSX.py` | Synthetic reader/planner oracles and archive/typed-cell/coordinate/limit negative cases. |
| `requirements.txt` | Exactly runtime openpyxl3.1.5, defusedxml0.7.1 and et_xmlfile2.0.0, official release SHA-256 hashes. |
| `requirements-build.txt` | Runtime requirements inclusion plus exact Windows build graph and Python3.9 conditional dependencies, official release hashes. |
| `THIRD_PARTY_NOTICES.md` | Runtime/build package identities, licenses and required notices, distinguish shipped runtime from build/test-only tooling. |
| `cong_cu/DONG_GOI.py` | Fail-closed installed version checks, no automatic install/network, existing clean-tree gates and temporary metadata, explicit reader/hardened XML collection if required. |
| `kiem_thu/KIEM_THU_PHAT_HANH.py` | Focused installed-tool/version failure tests, dirty-tree-before-effects retained, no-pip packaging proof and metadata/collection contract checks. |

Terra retains `MAY_CHU.py`, `QUAN_LY_DANH_MUC.py`, `danh_muc.js` and API/catalog/UI tests. Root owns exact dependency release-hash acquisition and independent admission. Send official metadata results to Sol before implementation; installed package RECORD hashes are not wheel/sdist release hashes and must never be substituted.

Read-only installed version/Requires-Python inventory:

| Distribution | Exact installed pin | Requires-Python | Scope |
|---|---|---|---|
| openpyxl |3.1.5 |>=3.8 | runtime |
| defusedxml |0.7.1 |>=2.7 excluding3.0–3.4 | runtime |
| et_xmlfile |2.0.0 |>=3.8 | runtime, openpyxl dependency |
| PyInstaller |6.14.2 |>=3.8,<3.14 | build |
| altgraph |0.17.4 |unspecified in metadata | build |
| packaging |24.2 |>=3.8 | build |
| pefile |2023.2.7 |>=3.6.0 | Windows build; satisfies excluded2024.8.26 requirement |
| pyinstaller-hooks-contrib |2025.5 |>=3.8 | build |
| pywin32-ctypes |0.2.3 |>=3.6 | Windows build |
| setuptools |78.1.0 |>=3.9 | build |
| importlib_metadata |8.7.1 |>=3.9 | build only when Python<3.10 |
| zipp |3.23.0 |>=3.9 | importlib_metadata dependency under same condition |

Twelve distributions total. Build pins target the documented Windows Python3.9+ scope; macOS macholib is outside this Windows EXE lock. Wheel hashes should cover supported Windows architectures only where real support is claimed; keep pure Python wheels and exact tested Windows PyInstaller wheel plus sdist hashes as appropriate. No broadened architecture/platform claim follows. Offline version checks verify installed identities, not installation origin/RECORD integrity; hash-required requirements provide a separately controlled future provisioning route. No provisioning is authorized now. Root must preserve exact filenames and SHA-256 obtained from official versioned PyPI JSON in a secret-free dependency evidence artifact. Vulnerability/advisory evaluation remains a distinct dependency review, never implied by an exact pin.

Proposed reader interface sent to Terra: `inspect_workbook(blob: bytes) -> {"sheets": list}`; `build_plan(blob: bytes, sheet: str, header_row: int, columns: dict, excluded_rows: list, existing_names: list) -> {sheet, headerRow, columns, counts, rows, canConfirm, newNames}`. `newNames` is internal-only. Use `PersonnelXlsxError(code, message, sheet=None, row=None, column=None)` with safe messages and location. SPEC currently describes inspect return both as a dict and as "exactly the sheets value"; Terra owns resolving this small interface ambiguity before lock. Reader and handler must agree rather than adapting silently.

Observed hardening mismatch: importing installed openpyxl normally gives `openpyxl.xml.DEFUSEDXML=True` **and** `LXML=True`, `fromstring` a functools-wrapped callable and `iterparse` from defusedxml. Thus installed defusedxml alone does not prove all selected parsing paths. The admitted reader must force no ambient lxml before its first openpyxl import, require hardened XML enabled, validate actual selected parser provenance or reject unsafe already-imported configuration, and test both ordinary and pre-imported/disabled configurations. Do not read or print the broader environment to diagnose this. Frozen E6 should exercise the identical safe path. This is local package-source inspection, not a claim of untrusted workbook safety or governance proof.

If the reader checks pinned runtime versions through `importlib.metadata.version`, frozen packaging must explicitly collect the three distribution metadata sets (for example `--copy-metadata` for each runtime distribution). Normal static Python import collection does not by itself prove metadata lookup will work. Include the applicable third-party notice artifact in the EXE asset/release delivery and verify it exists in the packaged output path; declaration in the repository alone is not shipped notice delivery. Exact approach belongs in the admitted packaging change and frozen runtime proof.
