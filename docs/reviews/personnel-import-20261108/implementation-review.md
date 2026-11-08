# Personnel import independent implementation review

Status: SOURCE_CANDIDATE_ACCEPTED
Risk: R2
Worker: Terra integration / Sol reader and packaging
Reviewer: Astra independent REVIEWER
Date: 2026-11-08
Action: docs/work_orders/WO_PERSONNEL_EXCEL_IMPORT.md
Action raw SHA-256: fbc56001358dc6ada77207a780b9d213d8c152b8ee808b95a5a9efdce7419f20
Admission metadata commit: c855598

## Review intake and limits

CVF Agent Declaration: project SO_BAO_CAO_CA_V1_9; pinned Core ../.Controlled-Vibe-Framework-CVF at68a7446cc35b7f4bfd2e6ca4029d4ee389c8a5b6; canonical phase BUILD; risk ceiling R2; live evidence required YES; independent REVIEWER; active handoff CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md; next move admitted Terra/Sol implementation then independent review before candidate commit and exact Windows EXE proof; parked checkpoint none. Canonical state/memory/handoff/implementation/index were rehydrated. Frozen prior audit/admission reviews remain unchanged.

This intake defines review focus from locked SPEC/ADR and existing catalog/server ownership. Worker code is in progress; no result is accepted yet. Source-candidate review, exact packaged consumer acceptance and aggregate product conclusion are separate. Reuse worker execution evidence where adequate; repeat only named gaps, regressions or required phase gates. No real operational catalog or database is part of review fixtures.

## Required evidence and highest-risk cases

| Criterion | Review questions and decisive cases | Evidence expected | Current result |
|---|---|---|---|
| E1 | Flat four-header input; multiple sheets and non-first header; physical row/column indices preserved; manual mapping cannot reinterpret unrelated headers. Three observed report structures refused without writes. | Reader/API tests with synthetic oracle and structural-only real-source result hashes; no personal rows in committed artifacts. | PENDING |
| E2 | Exact NEW/EXISTING/ERROR/EXCLUDED counts; NFC/casefold preserves existing spelling; deterministic close-name warning never merges; duplicate name/code conflicts affect all participating included rows. Excluding invalid rows resolves only permitted row errors; formulas remain rejected even when excluded. Fully repeated input is write-free no-op. | Expected versus actual row plans and meaningful UI checks; all four source fields visible with name-only persistence notice. | PENDING |
| E3 | Only selected new names written; four untouched catalog files remain byte-identical, custom teams/templates/roles/jobs remain semantically equal, old report/revision values unchanged. Inactive people after startup, extra/missing DB names or catalog mismatch refuse before mutation. Generic save behavior is not silently rewritten. | Before/after fixture fingerprints plus direct owner and HTTP tests; repeated import and no-op produce no unnecessary backup or DB update. | PENDING |
| E4 | Auth/Origin/header/main-store/read-only/review-copy guards; stale context/digest; malformed JSON, duplicate keys, boolean-as-integer, forged names/nonce, replay, expiry boundary, cross-tab replacement and invalid-preview invalidation. Context changes clear pending plan. | Real local HTTP tests exercising handlers and owner; nonce consumed on failed confirmation and no subsequent replay. | PENDING |
| E4 | Fail each actual backup/read/verify/temp-write/replace/sync/post-write-verify boundary. Restore succeeds only with verified original state; restore failure keeps backup and returns RECOVERY_REQUIRED. Detected external people edit is preserved rather than rolled back over. External unrelated-file change is not silently repaired. | Fault injections tied to concrete calls, backup readability/hash checks and file/DB state after every failure; no claim of atomic power-loss/cross-process safety. | PENDING |
| E5 | Compressed/body limits, actual streamed inflated total/per-member/ratio, duplicates/case collision/traversal/encryption/macros/relationships, XML DTD/entities, sparse and duplicate coordinates, all-sheet bounds, mapped formulas/cached formulas and merged table ranges. Header/mapping and workbook structure are validated server-side. | Adversarial fixtures with exact expected refusal codes and locations; all-sheet preflight before library load and bounded response/UI rendering. | PENDING |
| E5 | Escape sheet/header/name/message text once at DOM boundary; no workbook formula execution or external fetching. Hardened parser cannot silently switch through ambient lxml/already-imported module/environment. Dependency metadata survives frozen bundling. | Source inspection plus executable parser provenance/fail-closed tests and exact packaged runtime evidence. | PENDING |
| E6 | Clean reviewed commit builds with exact isolated hash-verified wheel set, no unpinned installation by builder. Applicable full Python/JS release groups and launcher smoke pass; skips explicitly itemized. | Worker commands/exit codes, full logs, source hashes, wheel manifest, build metadata/EXE hash and exact supported runtime versions. | PENDING |
| E6 | Actual headed Windows EXE: open, select file, inspect/map/exclude/preview/confirm, picker shows new name, create/save report, exit/reopen, export, old report intact. No headless/API-only substitution. | Timestamped sanitized native evidence plus persisted/export oracle on same exact EXE. Native file-picker versus browser-upload scope explicit. Manual-versus-import steps/time for same synthetic list, no invented improvement threshold. | PENDING |

## Existing-owner traps to inspect at return

Catalogs.sync replaces people and may return last-good snapshot on AppError; successful function return alone therefore does not establish a successful import. Read actual warning/error handling and verify expected DB/catalog state. Catalogs.raw_digest and Catalogs.read use different digest meanings; preview/confirm must bind raw digest consistently. Existing server context paths include restore, viewer, return-to-main and correction mode; review every pending-plan invalidation edge. Guard failure must not leak local paths or raw workbook content. A plan is server-owned and tied to validated bytes/selections, never reconstructed from untrusted names in confirmation.

Boundary cases should verify equality as well as overflow: allowed maximum versus maximum+1, exact expiry time, empty/whitespace rows, empty optional mappings, nonexistent exclusions and type confusion. Test source assumptions independently of implementation logic; avoid a test that merely calls the same helper to generate its expected result.

## Return and review sequence

Workers return assigned path diff, requirement/proof mapping, exact source hashes, commands/results/skips, failures and unresolved limitations. Reviewer first performs one consolidated source/evidence pass. Clear reviewer-local fixes within unchanged design/paths/authority/effects/commit owner may be applied and disclosed; material redesign or missing new evidence goes back through the existing repair boundary. Do not silently self-approve broad implementation.

Root owns aggregate milestone reconciliation and candidate commit. Source review can permit the clean candidate commit needed for E6 without falsely completing E6. After exact EXE evidence, reviewer issues separate final acceptance disposition and identifies remaining original roadmap work. Until then all PNI E1-E6 product results remain pending; E7 and later proposals are outside this slice. No provider governance, hosted CI, deployment or operational readiness is claimed by these local tests.

## Consolidated source review — round 1

Source-candidate acceptance is withheld pending F6-F8 in source-review-round1.json. Five evidence-determined reviewer-local corrections F1-F5 were applied within admitted paths and validated by32focused tests,0skips (astra-local-regressions.txt); original failures remain documented. The independent review found real counterexamples beyond the initial worker tests, including worksheet path preflight bypass, DB precondition timing and Unicode line splitting. No broad implementation was authored by reviewer.

Terra owns F6 async UI lifecycle and F7 missing HTTP/owner failure evidence; Sol owns finite F8 three-report refusal proof. Reuse existing valid tests; add only missing cases and run affected suites, then Root repeats full release for final source candidate. Complete worker return hash refresh after LF normalization, preserving initial hashes as historical. No frozen raw metadata is normalized.

The Root roadmap deltas preserve the authoritative PNI criteria and unrelated D2-D5 remainder; candidate1.9.2 is not claimed released. Dependency pins/build source retain the admitted isolated/offline toolchain and clean-tree gates. E6 native proof is intentionally still pending after source review.

Reviewer-local repair decision: unchangedObjective=YES; unchangedDesign=YES; unchangedPaths=YES; unchangedAuthority=YES; unchangedEffects=YES; unchangedCommitOwner=YES; evidenceDetermined=YES for F1-F5.

REWORK decision envelope: reviewerLocalRepairBoundary=NEW_EVIDENCE_REQUIRED; reviewerLocalRepairBasis=Async UI lifecycle correction requires deterministic ordering/close regression proof and actual missing fault-boundary evidence; small determined source corrections were already made locally. unchangedObjective=YES; unchangedDesign=YES; unchangedPaths=YES; unchangedAuthority=YES; unchangedEffects=YES; unchangedCommitOwner=YES; evidenceDetermined=NO for F6-F8.

Tranche conclusion: source returned with bounded same-scope rework; no accepted candidate yet. Product conclusion: E1-E6 remain unaccepted; E6 exact Windows EXE is still mandatory, and E7/original roadmap gaps remain separately owned.


## Consolidated repair round 1 disposition — source candidate

Independent re-review accepts the source candidate bound by source-candidate-review.json. F1-F8 are resolved for source review; the preceding intake table and REWORK conclusion remain historical. E1-E5 source/API/reader behavior is supported by the focused regressions and final 189-test Python release result (0 failures, 0 skips). E6 remains PENDING: Root must finish final JavaScript groups and required commit gates, then Sol must prove the exact clean committed Windows EXE and headed end-to-end workflow before terminal acceptance. This decision permits the candidate commit needed for that proof; it does not close the product or release it.

F6 worker guards correctly discard obsolete inspect/preview results, invalid replacement clears old file state and delayed cancel cannot close a later dialog. Re-review found that cancel and mapping remained active while a confirmation could already commit. Reviewer locally disabled import inputs/selects/buttons during confirmation and refresh, guarded direct mutation/cancel/duplicate-confirm calls, displayed waiting status, and restored controls on failure with the nonce consumed. Deterministic deferred confirmation success and failure regressions pass in astra-confirmation-ui.txt. No global Escape/backdrop handling was introduced. This is an evidence-determined same-contract repair, not an authority or design change.

F7 now exercises actual owner backup-read/verify/write, temp-write/fsync/replace, SQLite-trigger sync failure, postverification and restore-write/replace boundaries, checking retained backup and file/DB state. HTTP cases cover authentication, origin/header, viewer and review-copy. These controlled failures do not establish power-loss atomicity or cross-process locking. The reviewer removed the unused sqlite3 test import after the preserved aggregate hygiene failure; SourceTests4 passed and Root's later full189 suite passed. Python source was unchanged after that full result.

F8 uses exact hashes of all three reference workbooks before/after bounded reads, with personal values discarded. Bai cont is inspectable but its selected report header cannot produce an import plan; Thu tuc fails an unsupported relationship; Dieu hanh fails an unsupported member (the worker table's relationship label is imprecise; the actual JSON reason governs). The synthetic three-profile regression complements, and does not substitute for, this real-reference refusal observation.

The final manifest supersedes historical worker hashes only for current byte custody. All18 listed implementation/test/dependency/user-document files are LF. The two reviewer-edited JavaScript files and API test import removal are explicitly included. Frozen SPEC/ADR/action and prior admission reviews are unchanged. Root roadmap edits preserve the authoritative PNI criteria and open original product remainder; candidate1.9.2 remains unreleased.

Reviewer-local repair decision for the final hygiene/busy-state corrections: unchangedObjective=YES; unchangedDesign=YES; unchangedPaths=YES; unchangedAuthority=YES; unchangedEffects=YES; unchangedCommitOwner=YES; evidenceDetermined=YES. No new REWORK dispatch required. Mechanical test observations do not assert live provider governance.

Final aggregate received and bound: release-final.json records189Python,6JavaScriptgroups,4workspace tests and source smoke1.9.2 PASS, zero reported skips. Reviewer verified each referenced final log hash. The source manifest now binds this exact aggregate; only Root commit gates/clean candidate and E6 native proof remain.
