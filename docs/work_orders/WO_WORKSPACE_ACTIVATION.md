# Workspace activation repair work order

Status: CLOSED_ACCEPTED
docType: work_order
dispatchKind: INITIAL
Risk: R2

## Scope and acceptance

User authorized applying workspace rules and resolving all remaining setup blockers. Inherit the reviewed 1.4 installation and four WSA criteria. Worker may add scripts/check_project_workspace.py and a focused verification script under kiem_thu/. Orchestrator owns .cvf receipts, policy, continuity, docs/ registries, and roadmap setup notes. Inherited scripts/cvf_gates, shared Core/workspace, application source and actual data are excluded. No network deployment or provider call is authorized by this work order.

Amendment 2: preserve the initial partial implementation and observed legacy26/28 failure. Accept only exact INST LOCK_INVALID plus optional exact COV_OBJECT_SHAPE on both current WSA documents, with CONT and all25 non-gate checks PASS; full current1.4 bootstrap must independently pass. Reject additional or altered diagnostics.

Keep original doctor output/exit and replace only the exact documented obsolete installation and milestone-schema comparisons after independently verifying the supplemental source. Fail on unexpected failures, missing checks, source/hash mismatches or missing action receipt. Preserve all original core freshness, pin, kit, catalog and continuity checks. Validate a positive path plus unrelated doctor failure, tampered source/receipt and unexpected legacy output without mutating protected files.

Budget: 45 minutes. Stop on unexpected drift or unrelated failures; return to orchestrator with concrete evidence. No commit required from worker.

## Gate-To-Role Closeability Contract

closeabilityContractVersion: cvf.gate-role-closeability@1.0.0
closeabilityDisposition: CLOSEABLE
returnTimeRecheck: REQUIRED_BEFORE_REPAIR
implementationTopologyPolicy: BOUNDED_PATH_FAMILIES
foreseeableFileSplitDisposition: COVERED_BY_BOUNDED_PATH_FAMILY

| gateId | mustPassBy | repairOwner | repairPhase | mutationSurface | topology | commitOwner | commitPhase | dependsOn |
|---|---|---|---|---|---|---|---|---|
| authorization_review | PRE_DISPATCH | project-orchestrator | PRE_DISPATCH | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | NONE |
| pre_dispatch_gate | PRE_DISPATCH | project-orchestrator | PRE_DISPATCH | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | authorization_review |
| dispatch_continuity | IMPLEMENTATION | session-sync-steward | IMPLEMENTATION | CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md material-SHA marker | EXACT_PATHS | session-sync-steward | DISPATCH_CONTINUITY_COMMIT | pre_dispatch_gate |
| focused_checker_tests | WORKER_RETURN | project-orchestrator | WORKER_RETURN | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | dispatch_continuity |
| adif_integrity | WORKER_RETURN | project-orchestrator | WORKER_RETURN | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | focused_checker_tests |
| pre_implementation_autorun | IMPLEMENTATION | project-orchestrator | IMPLEMENTATION | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | dispatch_continuity |
| worker_return_fast | WORKER_RETURN | project-orchestrator | WORKER_RETURN | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | focused_checker_tests |
| reviewer_fast | REVIEW | project-orchestrator | REVIEW | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | worker_return_fast |
| pre_commit | PRE_MATERIAL_COMMIT | project-orchestrator | PRE_MATERIAL_COMMIT | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | reviewer_fast |
| terminal_completion_review | POST_MATERIAL | project-orchestrator | POST_MATERIAL | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | pre_commit |
| continuity | CONTINUITY_COMMIT | session-sync-steward | CONTINUITY_COMMIT | project governance records and project doctor | BOUNDED_PATH_FAMILIES | session-sync-steward | CONTINUITY_COMMIT | terminal_completion_review |
| committed_range_closure | POST_MATERIAL_CLOSURE | project-orchestrator | POST_MATERIAL_CLOSURE | project governance records and project doctor | BOUNDED_PATH_FAMILIES | project-orchestrator | MATERIAL_COMMIT | continuity |

## Milestone contribution

```cvf-milestone-coverage-json
{
  "schemaVersion": "cvf.milestoneCoverage@1.0.0",
  "authority": {
    "path": "docs/roadmaps/WORKSPACE_ACTIVATION.md",
    "heading": "## Acceptance criteria",
    "sha256": "76c85851b0f9785ab7b87195e0288b85dbc55940094b62d1beaf4c6320a188d4"
  },
  "milestone": {
    "id": "WSA",
    "consumer": "Project development team",
    "outcome": "Repeatable local mechanical workspace setup with honest action-specific activation",
    "checkpoint": {
      "trigger": "Before next application implementation dispatch",
      "owner": "project orchestrator",
      "decision": "Accept this bounded setup only after compatibility and activation checks pass"
    }
  },
  "phase": "REVIEW",
  "action": {
    "kind": "REVIEW",
    "selected": [
      "WSA1",
      "WSA2",
      "WSA3",
      "WSA4"
    ],
    "owner": "project orchestrator",
    "output": "Accepted local workspace setup review and continuation handoff",
    "budgetMinutes": 15,
    "stop": "Stop on final gate or source drift; reopen bounded review",
    "next": "Read product roadmap and admit a new exact action before future BUILD"
  },
  "rows": [
    {
      "id": "WSA1",
      "state": "VERIFIED",
      "gap": "",
      "owner": "project orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-full-flow.json",
          "sha256": "1a4fe15707dfd231dadf77a2035c0d3c2ac75fd8c80f6b719e4b9720a8cd9b6d"
        },
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-tests.txt",
          "sha256": "d3865f0faae762337df504480fca945eeb18214a7fe1995eb3205f2a7c5edb73"
        },
        {
          "path": "docs/reviews/workspace-activation-review.md",
          "sha256": "549cfe8f4bcdd9a22846a3b0a9eece52caf4b77b46509d0c3a950602dfb9ece7"
        }
      ]
    },
    {
      "id": "WSA2",
      "state": "VERIFIED",
      "gap": "",
      "owner": "project orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-full-flow.json",
          "sha256": "1a4fe15707dfd231dadf77a2035c0d3c2ac75fd8c80f6b719e4b9720a8cd9b6d"
        },
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-tests.txt",
          "sha256": "d3865f0faae762337df504480fca945eeb18214a7fe1995eb3205f2a7c5edb73"
        },
        {
          "path": "docs/reviews/workspace-activation-review.md",
          "sha256": "549cfe8f4bcdd9a22846a3b0a9eece52caf4b77b46509d0c3a950602dfb9ece7"
        }
      ]
    },
    {
      "id": "WSA3",
      "state": "VERIFIED",
      "gap": "",
      "owner": "project orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-full-flow.json",
          "sha256": "1a4fe15707dfd231dadf77a2035c0d3c2ac75fd8c80f6b719e4b9720a8cd9b6d"
        },
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-tests.txt",
          "sha256": "d3865f0faae762337df504480fca945eeb18214a7fe1995eb3205f2a7c5edb73"
        },
        {
          "path": "docs/reviews/workspace-activation-review.md",
          "sha256": "549cfe8f4bcdd9a22846a3b0a9eece52caf4b77b46509d0c3a950602dfb9ece7"
        }
      ]
    },
    {
      "id": "WSA4",
      "state": "VERIFIED",
      "gap": "",
      "owner": "project orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-full-flow.json",
          "sha256": "1a4fe15707dfd231dadf77a2035c0d3c2ac75fd8c80f6b719e4b9720a8cd9b6d"
        },
        {
          "path": "docs/reviews/activation-history/adapter-reviewed-tests.txt",
          "sha256": "d3865f0faae762337df504480fca945eeb18214a7fe1995eb3205f2a7c5edb73"
        },
        {
          "path": "docs/reviews/workspace-activation-review.md",
          "sha256": "549cfe8f4bcdd9a22846a3b0a9eece52caf4b77b46509d0c3a950602dfb9ece7"
        }
      ]
    }
  ],
  "supportingWork": [],
  "conclusions": {
    "tranche": "COMPLETE",
    "trancheSummary": "Reviewed compatible local project setup and exact action assessment accepted",
    "trancheEvidence": [
      {
        "path": "docs/reviews/activation-history/adapter-reviewed-full-flow.json",
        "sha256": "1a4fe15707dfd231dadf77a2035c0d3c2ac75fd8c80f6b719e4b9720a8cd9b6d"
      },
      {
        "path": "docs/reviews/activation-history/adapter-reviewed-tests.txt",
        "sha256": "d3865f0faae762337df504480fca945eeb18214a7fe1995eb3205f2a7c5edb73"
      },
      {
        "path": "docs/reviews/workspace-activation-review.md",
        "sha256": "549cfe8f4bcdd9a22846a3b0a9eece52caf4b77b46509d0c3a950602dfb9ece7"
      }
    ],
    "product": "COMPLETE",
    "productSummary": "Only the four WSA development setup criteria are complete; application product acceptance is outside this milestone",
    "acceptance": [
      {
        "path": "docs/reviews/activation-history/adapter-reviewed-full-flow.json",
        "sha256": "1a4fe15707dfd231dadf77a2035c0d3c2ac75fd8c80f6b719e4b9720a8cd9b6d"
      },
      {
        "path": "docs/reviews/activation-history/adapter-reviewed-tests.txt",
        "sha256": "d3865f0faae762337df504480fca945eeb18214a7fe1995eb3205f2a7c5edb73"
      },
      {
        "path": "docs/reviews/workspace-activation-review.md",
        "sha256": "549cfe8f4bcdd9a22846a3b0a9eece52caf4b77b46509d0c3a950602dfb9ece7"
      }
    ],
    "owner": "project orchestrator"
  }
}
```
