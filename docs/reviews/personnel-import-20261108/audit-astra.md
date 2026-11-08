# Independent personnel-import design audit

Status: DESIGN_REVIEW
Date: 2026-11-08
Reviewer: Astra (independent REVIEWER; no product implementation authored)
Risk: R2
Worker: Root orchestration / Terra specification / Sol feasibility
Scope: finite source/design audit, not implementation acceptance or BUILD admission.

## Context and evidence

CVF Agent Declaration: SO_BAO_CAO_CA_V1_9; Core ../.Controlled-Vibe-Framework-CVF at 68a7446cc35b7f4bfd2e6ca4029d4ee389c8a5b6; DESIGN; risk ceiling R2; live evidence required YES; REVIEWER; active handoff CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md; next move review draft/resolve bounded SPEC; parked checkpoint none. Canonical state, memory, handoff, implementation truth and docs index agree. BOOTSTRAP_MIGRATION_PENDING is nonblocking. Canonical Core knowledge ingest ran from project cwd into ignored runtime output after resolving the missing project-local wrapper; README-only input, no network call.

Independent doctor invocation returned CORE_ASSESSED, current activation, all 29 native checks and four trusted bootstrap results PASS. Assessed packet remained terminal WO_CORE_RECONCILIATION.md: this is no personnel BUILD grant and no live governance proof. Pinned lifecycle, product coverage and coverage machine standards were read. Supplemental project-development application standard was resolved through active pack source 662cc1f61, artifact SHA256 d06b62387e015160a77658f333882a2a316d54ffd0421071354cf63a3730dd7a; it does not replace executable Core.

Sources inspected: draft adoption roadmap; source-observations.json; current product roadmap; Catalogs owner; catalog JS; HTTP save/request guards; catalog/release tests; packaging script. Rechecked all 20 observation source hashes: 19 match; tai_lieu/ROADMAP_SAU_V1_9.md differs and was read currently rather than accepted through the old hash. Do not rewrite original snapshot to conceal this difference. Native runtime and EXE were not exercised in this audit.

## Design disposition

The first useful scope is additive import of a flat personnel .xlsx list: explicit sheet/header/column selection and explicit eligible row selection, preview, then confirmed addition through existing catalog ownership. Preserve E1-E6 in full; keep E7 group assignment in its separate future scope. No identity migration, inferred department, automated team assignment or cross-project sync is required. Existing selector/search/staff-template behavior should be reused.

The latest user request authorizes audit and implementation preparation; asking the user to reapprove routine reader/API/test decisions would add avoidable wait. Exact SPEC, action, authority coverage, independent review and fresh admission are still required before product BUILD. Unknown real roster/source ownership and group meanings prevent claims of operational fitness or automatic classification, but do not block a generic manually selected additive importer tested with synthetic lists. Do not call Chuc danh a department or infer DAY/NIGHT from group labels.

## Findings to resolve in SPEC and tests

1. E3 preservation has a real owner boundary. Catalogs.save serializes all five catalog files, and Catalogs.sync deletes/reinserts people with active=1. Adding a name must not silently change inactive-person state, team/template meaning or historical reports. Define semantic versus byte preservation precisely; retain untouched non-people bytes where required and reject unsupported inconsistent catalog/DB states rather than widening into a general catalog rewrite. Test preexisting custom formatting, active/inactive records, absent source names and repeated imports.
2. E4 is not already proven by reuse. Backup creation/writes occur before save's try block; rollback can itself fail. Test backup creation failure, each file replacement, SQLite sync failure and rollback failure. Require honest failed result and retained recovery material; distinguish recoverable error from a promise of atomic multi-file crash recovery. Avoid broad new storage architecture unless the selected contract demands it.
3. Bind confirmation to server-derived preview bytes, source hash, selected sheet/header/mapping/row set, catalog digest and DB context. A client-supplied name list alone does not prove it is the preview the user accepted. Recheck total catalog limits at apply, invalidate stale plans, and make cancel/no-op write-free.
4. E1/E5 must resist accidental report ingestion as well as hostile workbooks. Manual mapping cannot silently override structural rejection of the three report layouts; define a positive flat-table contract. Preflight compressed/uncompressed totals, ZIP entries and paths, XML structure and worksheet dimensions before heavy parsing. Reject identity formulas even with cached values, unsupported numeric identifiers, macro/encrypted/legacy formats and external links. Bound rows/cells and response size. Render all values as escaped text.
5. Existing parse_lines uses NFC + strip + casefold duplicate checks, not accent folding or arbitrary internal whitespace collapse. Lock normalization and ambiguity rules to avoid creating unintended identities. Preserve textual leading zero IDs, display ignored source fields, and disclose that employee codes are not persisted or sufficient to recognize renames on later imports.
6. E6 packaging requires a clean committed source under DONG_GOI.py. Its normal route pip-installs PyInstaller; dependency/network effects must be accounted for before invocation. A reviewed source commit can precede final product acceptance; commit is not closure. Bind final EXE hash, build commit, runtime and real native consumer workflow to review evidence. Existing mocked packaging tests and HTTP/headless tests cannot satisfy E6.

## Reader and acceptance assessment

Terra proposes openpyxl 3.1.5 with bounded ZIP/XML preflight and hardened parsing. This is a reasonable candidate for a deliberately limited format, subject to ADR with exact dependency/license/provenance, local packaging availability and failure tests. A maintained reader avoids implementing general OOXML semantics; preflight remains necessary. Root owns current official-source dependency verification. This audit neither installs a dependency nor certifies security from library presence.

| Criterion | Required evidence and review focus |
|---|---|
| E1 | Known flat template headers plus multi-sheet/header mapping; three report-shaped fixtures refused with no writes. |
| E2 | Independent synthetic oracle for counts/source rows/mapping, missing/conflicting IDs/names, Unicode and close names; cancel unchanged. |
| E3 | Add/repeat/no-op, existing and absent people, inactive state, teams/templates and report/revision snapshots before/after. |
| E4 | Stale digest/context, preview tampering, backup/file/DB/rollback failure matrix, demonstrable recovery. |
| E5 | Invalid/empty/oversized ZIP/XML, formulas, unsupported types/features, row/cell limits and escaping; server rejection. |
| E6 | Applicable release suite with explicit skips; real exact Windows EXE open/import/select/create/save/reopen/export, old report retained; native evidence. |

Five readiness answers: (1) component adds selected names from flat Excel using existing catalog ownership; (2) standard is the locked E1-E6 contract and synthetic source-derived expected results; (3) implementation and exact-version evidence are still absent; (4) expected value is fewer manual roster entry actions, to be measured without invented speed claims; (5) Windows EXE consumer flow is mandatory and still untested. Technical checks precede developer product acceptance, then user business-fit feedback. No technical QA is delegated to the user.

## Next move and limits

Root should admit complete criterion authority, preserve the original roadmap's unrelated remainder and prepare exact work order with paths, effects, commits, finite budget and failure boundaries. Independent reviewer then assesses SPEC/action/native-control observations and supplemental source before fresh pre-dispatch. Current audit result is sufficient to continue bounded design, with the six findings above carried into the contract. Product E1-E6 remain unmet; E7 and later adoption proposals remain separate; existing EXE/UI and D2-D5 gaps retain their original owners. No live provider governance, deployment, operational-data mutation or product-ready claim is made.
## Follow-up SPEC audit

Reviewer read the expanded SPEC/API and ADR on 2026-11-08. The exact extension resolves nonce lifetime, bounded all-sheet parsing, row exclusions, positive header profile and the additive-owner decision. Proposed 300-second single-use server plan, 2 MiB workbook/3 MiB transport bounds and refusal of unsafe inactive/catalog mismatch states are coherent with the selected slice. Refusal is not a claim that existing startup Catalogs.sync preserves inactive people; test the new operation's boundary honestly.

Before final hash/admission, reconcile superseded generic-save/undecided persistence prose with the selected people-only owner operation; make CATALOG_UNSAFE and backupId explicit in the error contract; choose deterministic near-name warning semantics; keep whole report/revision preservation checks in test evidence instead of adding unbounded production scans; stop rollback with RECOVERY_REQUIRED when post-write people bytes changed externally rather than overwriting a detected newer edit. Remaining cross-process races must stay disclosed. Exact package/dependency evidence and final work order are still pending. These corrections need no new business decision and do not change E1-E6.

The public Core's referenced acceptance-ledger addendum is unavailable in the delivered trees according to Root's scoped lookup. No specific installed gate obligation has been demonstrated impossible: preserve explicit requirements/proof/return manifest and actual installed closeability controls, disclose the unavailable reference, and make no invented machine-fulfillment claim. This absence is not a reason to reopen Core recovery or stop unrelated design.
## Consolidated contract review before exact admission

Reviewed the expanded SPEC, ADR, joint WO_PERSONNEL_EXCEL_IMPORT.md and dependency-source-review.json. The previously requested persistence/API/limits corrections are incorporated: additive people-only operation, refusal of unsafe inactive states, deterministic warning, explicit codes, test-only historical scans and no rollback over detected external edits. The joint path ownership and reader/server interface retain independent review; no product source was authored by this reviewer.

No new technical feasibility blocker was identified in this contract review. The exact Windows build order is closeable: reviewed candidate commit first, clean-tree build in an isolated environment, native evidence afterward, evidence/closure commit last. E6 stays mandatory; headless proof cannot substitute. A supported native tool inventory is feasibility evidence, not execution or usability proof.

The bounded development effect of official hash-verified wheels installed solely in the project ignored venv is proportionate to this implementation. Rejecting the observed setuptools78.1.0 candidate in favor of84.1.0 avoids knowingly admitting that affected build pin. Official metadata reports Python>=3.10 for84.1.0; Python3.11 is therefore the concrete build environment. Runtime Python3.9 remains a compatibility target, not an exercised claim. Metadata's empty vulnerability list is not a security audit. The evidence preserves the rejected candidate and exact distribution hashes; no dependency was downloaded or installed by the reviewer.

Before final admission, Root must finish the already-planned coverage block/authority, current continuity and exact observations/receipt. ADR must stop describing completed dependency assessment as merely pending and bind dependency-source-review.json plus the exact chosen runtime/build set, isolated wheel-only install, rejected78.1.0 and supported/tested version limits. Resolve the harmless but confusing inspect wording to raw JSON strings escaped once by UI, consistent with the later integration contract. These are routine documentary completion tasks under the existing authority, not new business approvals.

Work-order budget and stop rules retain the same outcome:180minutes implementation/tests/build/native plus30minutes supporting admission/review, earlier cumulative preparation UNKNOWN. Actual elapsed effort should be recorded; document edits do not renew it. On ceiling or unsupported native flow preserve partial evidence and unmet E6 rather than manufacturing acceptance.

Disposition: suitable for final exact action assessment after the stated documentary prerequisites; this review is not an executable admission, implementation acceptance or product completion.
