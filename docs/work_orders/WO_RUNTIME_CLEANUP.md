# Remove finished synthetic benchmark payloads

Status: CLOSED_ACCEPTED
docType: work_order
dispatchKind: INITIAL
Risk: R2
Worker: Root
Reviewer: Astra independent
Commit owner: Root
Date: 2026-11-08

## Dispatch Prompt Envelope

Terminal REVIEW only: reconcile exact16-file completed synthetic payload deletion, independent result acceptance, current activation/continuity and commit. No further deletion, product tests or BUILD. Original admitted packet845f and receipt preserved under history.

## Design and safety contract

Allowlisted roots are .cvf/runtime/local-completion-20261108/fixtures-terra and .cvf/runtime/local-completion-20261108/large-ui-d8de489. Resolve each absolute path, reject links/reparse ancestors or anything outside those roots, reject Git-tracked paths, require original size/mtime and no active fixture command line, then unlink only exact files using one runtime. No recursive delete, shell composition, process termination or access to operational DB. Preserve durable logs/oracles/source/PDF/screenshots in docs/reviews, fixture generators, released EXE, user workbook and original root DU_LIEU/DANH_MUC/backups. No provider/network/credential/global/Core/gate/security changes. Raw disposable DB bytes will no longer be retained/replayable; existing historical measurements and durable manifests remain as original observations, not re-proved.

Allowed metadata: this packet, CLN authority registry entry, activation receipt, canonical continuity/implementation/index/catalog pointers and local-completion review family; record pre/post count, bytes, skipped reasons and actual disk free. No artifact duplication or new large archive. Meaningful safety validation only; never rerun product suites or regenerate fixtures. Root alone commits. No web/release grant or claim of live AI governance.

## Acceptance layers and value

Job/input/output: remove completed synthetic benchmark payloads, exact manifest input and deletion/free-space receipt output. Standard/provenance: prior recorded synthetic fixtures and operator cleanup request. Technical: path/tracked/metadata restrictions before deletion. Developer-product: actual deleted bytes and disk space, retained EXE identity. Business/device acceptance remains unchanged. No speed claim; only measured free-space improvement.

## Acceptance criteria — CLN

| ID | Required observable outcome |
|---|---|
| C1 | Remove only the16 exact generated synthetic benchmark DB payloads in runtime-cleanup-plan.json under its two explicit runtime roots after resolved-path/reparse/tracked-file and size/mtime checks. Preserve root real DU_LIEU/DANH_MUC/backups, user workbook, all durable docs evidence, fixture scripts/logs and delivered EXE. Record actual deleted count/bytes/free space; locked/changed files skipped, no process termination or recursive deletion. |

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | Root | PRE_DISPATCH | CLN authority, SPEC, work order and action records | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | Root | PRE_DISPATCH | CLN metadata and exact assessment records | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| pre_implementation_autorun | IMPLEMENTATION | Root | IMPLEMENTATION | CLN metadata and assigned worker source families | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | dispatch_continuity |
| focused_checker_tests | WORKER_RETURN | Root | WORKER_RETURN | exact cleanup path/metadata manifest only | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | dispatch_continuity |
| adif_integrity | WORKER_RETURN | Root | WORKER_RETURN | CLN changed-path and artifact evidence | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | focused_checker_tests |
| worker_return_fast | WORKER_RETURN | Root | WORKER_RETURN | assigned source/test/return paths | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | adif_integrity |
| reviewer_fast | REVIEW | Astra | REVIEW | CLN review records and disclosed localized in-scope repairs | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | Root | PRE_MATERIAL_COMMIT | CLN reviewed candidate and metadata | BOUNDED_PATH_FAMILIES | Root | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | Astra | POST_MATERIAL | CLN cleanup deletion/space results and review records | BOUNDED_PATH_FAMILIES | Root | CONTINUITY_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | canonical continuity, catalog and accepted CLN evidence | BOUNDED_PATH_FAMILIES | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | Root | POST_MATERIAL_CLOSURE | CLN committed-range verification records | BOUNDED_PATH_FAMILIES | Root | CONTINUITY_COMMIT | continuity |

## Coverage

```cvf-milestone-coverage-json
{
  "schemaVersion": "cvf.milestoneCoverage@1.0.0",
  "authority": {
    "path": "docs/work_orders/WO_RUNTIME_CLEANUP.md",
    "heading": "## Acceptance criteria — CLN",
    "sha256": "e9b23274c9f759e01ad52e6867dac04109b55c06a38786d77361c1aa58a6bb98"
  },
  "milestone": {
    "id": "CLN",
    "consumer": "Local project owner",
    "outcome": "Recover disk space from finished synthetic benchmark payloads without affecting local delivery or real data",
    "checkpoint": {
      "trigger": "Before delete and terminal review",
      "owner": "Root with independent Astra reviewer",
      "decision": "Exact16-file allowlist only; preserve production and durable evidence; no product retest"
    }
  },
  "phase": "REVIEW",
  "action": {
    "kind": "REVIEW",
    "selected": [
      "C1"
    ],
    "owner": "Root CLOSER/COMMIT_STEWARD; Astra independent reviewer",
    "output": "Accept actual16-file synthetic payload cleanup and free-space result; unchanged local delivery",
    "budgetMinutes": 5,
    "stop": "Stop on result/identity mismatch or failed required terminal gate; original15minute cleanup ceiling unchanged, no extra delete/test",
    "next": "Commit cleanup records then return accepted LOCAL FREEZE; future work separately assessed"
  },
  "rows": [
    {
      "id": "C1",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root",
      "destination": "docs/work_orders/WO_RUNTIME_CLEANUP.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/runtime-cleanup-result.json",
          "sha256": "d91818af6856ab3d9c5bec2695e66e5a715a4c793bab5b4b260fe84563f92939"
        },
        {
          "path": "docs/reviews/local-completion-20261108/cleanup-executed.py",
          "sha256": "989f1550675720b8ec231e998d83029c130f2d926ad34f3066c34ef2e9e99def"
        },
        {
          "path": "docs/reviews/local-completion-20261108/cleanup-admission-review.json",
          "sha256": "8692ef736eaea36e6785c6a1e2c0713fb5d5ec1e48c804feec22af7ebcbac628"
        }
      ]
    }
  ],
  "supportingWork": [],
  "conclusions": {
    "tranche": "COMPLETE",
    "trancheSummary": "Exactly16 allowlisted generated DB files removed,20,028,223,488bytes, no skipped/remaining; exact released EXE unchanged",
    "trancheEvidence": [
      {
        "path": "docs/reviews/local-completion-20261108/runtime-cleanup-result.json",
        "sha256": "d91818af6856ab3d9c5bec2695e66e5a715a4c793bab5b4b260fe84563f92939"
      },
      {
        "path": "docs/reviews/local-completion-20261108/cleanup-executed.py",
        "sha256": "989f1550675720b8ec231e998d83029c130f2d926ad34f3066c34ef2e9e99def"
      },
      {
        "path": "docs/reviews/local-completion-20261108/cleanup-admission-review.json",
        "sha256": "8692ef736eaea36e6785c6a1e2c0713fb5d5ec1e48c804feec22af7ebcbac628"
      }
    ],
    "product": "COMPLETE",
    "productSummary": "CLN disk cleanup outcome complete, Dfree27.36GB; accepted LOCAL engineering remains unchanged, no product retest or operational acceptance claim",
    "acceptance": [
      {
        "path": "docs/reviews/local-completion-20261108/runtime-cleanup-result.json",
        "sha256": "d91818af6856ab3d9c5bec2695e66e5a715a4c793bab5b4b260fe84563f92939"
      },
      {
        "path": "docs/reviews/local-completion-20261108/cleanup-executed.py",
        "sha256": "989f1550675720b8ec231e998d83029c130f2d926ad34f3066c34ef2e9e99def"
      },
      {
        "path": "docs/reviews/local-completion-20261108/cleanup-admission-review.json",
        "sha256": "8692ef736eaea36e6785c6a1e2c0713fb5d5ec1e48c804feec22af7ebcbac628"
      }
    ],
    "owner": "Root with independent Astra result/terminal acceptance"
  }
}
```

## Terminal result

Executed once after independent admission and pre-dispatch.16 of16 allowlisted synthetic DB files removed,20,028,223,488bytes; zero skipped/remaining. D free7,333,425,152->27,361,681,408bytes (ambient filesystem activity explains32,768B delta beyond sizes). Delivered EXE SHA10aaf013 unchanged. Actual result and reviewed execution script bind exact effects; no operational DB, user workbook, true backups, durable evidence or process termination. Synthetic bulk payloads no longer retained/replayable; historical measurements and generators/logs remain, not re-proved. Only metadata terminal review/gates/commit follows, no more tests. Terminal5min is part of original15min, no budget reset; no network/provider/security/web effect.
