# Core identity reconciliation work order

Status: READY
docType: work_order
dispatchKind: INITIAL
Risk: R2

## Scope and acceptance

The operator authorizes resolving known Core drift. Inherit INTAKE/DESIGN/SPEC in docs/reviews/core-reconciliation/design.md and all four CRC criteria. This is bounded project recovery, not application implementation. Root may preserve history, pin current Core, explicitly refresh identical inherited profile via canonical installer, retain inspected rule-pack guidance, assess actual control observations, bind a fresh receipt and synchronize active records. Terra may change only scripts/check_project_workspace.py and kiem_thu/test_project_workspace_checker.py after that receipt is admitted. Root owns docs/, .cvf/, AGENTS.md and commit. No manual inherited algorithm edit, shared workspace/Core/pack mutation, product code/data/evidence edit, provider invocation or publication. Native doctor public git fetch is admitted solely for freshness observation and tracking-ref refresh.

Recovery stops dependent product work while identity is stale; the user-authorized metadata/receipt repair is the selected work, not an assertion that the failed doctor passed. Retain actual pre-receipt ACT failure. Six other mandatory controls and supplemental manifest inspection require independent Sol review before worker BUILD. Native output/exit remains visible and modern doctor checks have no legacy failure exemptions. Require full actual bootstrap controls and explicit packet scope even after Git becomes clean.

Budget60minutes. Stop on unexpected authority/source drift or unrelated failures; retain evidence and perform a consolidated causal audit before a dependent repair. No worker commit. Root is commit steward.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | project-orchestrator | PRE_DISPATCH | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | project-orchestrator | PRE_DISPATCH | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| focused_checker_tests | WORKER_RETURN | project-orchestrator | WORKER_RETURN | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | dispatch_continuity |
| adif_integrity | WORKER_RETURN | project-orchestrator | WORKER_RETURN | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | focused_checker_tests |
| pre_implementation_autorun | IMPLEMENTATION | project-orchestrator | IMPLEMENTATION | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | project-orchestrator | WORKER_RETURN | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | focused_checker_tests |
| reviewer_fast | REVIEW | project-orchestrator | REVIEW | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | project-orchestrator | PRE_MATERIAL_COMMIT | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | project-orchestrator | POST_MATERIAL | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | project-orchestrator | POST_MATERIAL_CLOSURE | project recovery governance records, canonical installer and current project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | continuity |


## Milestone contribution

```cvf-milestone-coverage-json
{
  "schemaVersion": "cvf.milestoneCoverage@1.0.0",
  "authority": {
    "path": "docs/roadmaps/CORE_RECONCILIATION.md",
    "heading": "## Acceptance criteria",
    "sha256": "d03d7c5abd06e4d42fbdf5c6ee7c66b3490da24b6cbb838443df7df90b736d0f"
  },
  "milestone": {
    "id": "CRC",
    "consumer": "Project development team",
    "outcome": "Current public Core identity and honest exact-action development readiness",
    "checkpoint": {
      "trigger": "Before dependent project BUILD",
      "owner": "Root orchestrator",
      "decision": "Require actual current-source checks, assessed action and independent review"
    }
  },
  "phase": "DISPATCH",
  "action": {
    "kind": "IMPLEMENT",
    "selected": [
      "CRC1",
      "CRC2",
      "CRC3",
      "CRC4"
    ],
    "owner": "Terra worker with Root-owned metadata/receipt recovery",
    "output": "Current Core project doctor, focused regressions and reviewed activation/continuity evidence",
    "budgetMinutes": 60,
    "stop": "Stop on new source/authority drift, unexpected failures or budget; preserve findings before any dependent successor",
    "next": "Independent review then terminal action assessment and local project commit; product work stays separate"
  },
  "rows": [
    {
      "id": "CRC1",
      "state": "NOT_STARTED",
      "gap": "Bind the current clean public Core and verify the canonical installed profile/workflow; preserve prior identity and retained supplemental inspection.",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": []
    },
    {
      "id": "CRC2",
      "state": "NOT_STARTED",
      "gap": "Delegate the project doctor to actual PINNED_CORE activation/native doctor and explicit-packet bootstrap; reject every unrelated or malformed failure.",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": []
    },
    {
      "id": "CRC3",
      "state": "NOT_STARTED",
      "gap": "Assess exact recovery action, six mandatory controls and inspected supplemental delivery with real invocation evidence and independent review; prove fail-closed negatives.",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": []
    },
    {
      "id": "CRC4",
      "state": "NOT_STARTED",
      "gap": "Synchronize active instructions, continuity, catalog and committed-tree evidence; preserve application source, real data, both Antigravity bundles and prior setup history.",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": []
    }
  ],
  "supportingWork": [],
  "conclusions": {
    "tranche": "PENDING",
    "trancheSummary": "Recovery implementation and independent acceptance pending",
    "trancheEvidence": [],
    "product": "PENDING",
    "productSummary": "Only local workspace recovery is selected; application roadmap and native UI proof remain open",
    "acceptance": [],
    "owner": "Root reviewer"
  }
}
```
