# Core identity reconciliation work order

Status: CLOSED_ACCEPTED
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
  "phase": "REVIEW",
  "action": {
    "kind": "REVIEW",
    "selected": [
      "CRC1",
      "CRC2",
      "CRC3",
      "CRC4"
    ],
    "owner": "Root closer with independent Sol review",
    "output": "Terminal CRC local mechanical acceptance, current continuity and exact reviewed receipt",
    "budgetMinutes": 15,
    "stop": "Stop on unexpected source drift, failed checks or missing independent terminal review",
    "next": "Commit terminal records after current exact-action assessment; future product work needs its own governed action"
  },
  "rows": [
    {
      "id": "CRC1",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/core-reconciliation/implementation-review.md",
          "sha256": "596ba059b759c87fdac4e3caae72afe62984c2def2fc467b84527a7ec9a39ffc"
        },
        {
          "path": "docs/reviews/core-reconciliation/clean-material-proof.json",
          "sha256": "2bae2f5c85f85690908bd3fd1ebfe43e7b234bdc35afa31e25364e6b0a624084"
        },
        {
          "path": "docs/reviews/core-reconciliation/final-preservation.json",
          "sha256": "6972c14fb40af91bc5b253a4ca6754bad2b1b8bc5a11d69e5fa3ddce0c2e811a"
        },
        {
          "path": "docs/reviews/core-reconciliation/negative-integration.json",
          "sha256": "d48800c2c812e6767e67c50544a8a38857e6d1c29315b98883c6d38826f1da7a"
        }
      ]
    },
    {
      "id": "CRC2",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/core-reconciliation/implementation-review.md",
          "sha256": "596ba059b759c87fdac4e3caae72afe62984c2def2fc467b84527a7ec9a39ffc"
        },
        {
          "path": "docs/reviews/core-reconciliation/clean-material-proof.json",
          "sha256": "2bae2f5c85f85690908bd3fd1ebfe43e7b234bdc35afa31e25364e6b0a624084"
        },
        {
          "path": "docs/reviews/core-reconciliation/final-preservation.json",
          "sha256": "6972c14fb40af91bc5b253a4ca6754bad2b1b8bc5a11d69e5fa3ddce0c2e811a"
        },
        {
          "path": "docs/reviews/core-reconciliation/negative-integration.json",
          "sha256": "d48800c2c812e6767e67c50544a8a38857e6d1c29315b98883c6d38826f1da7a"
        }
      ]
    },
    {
      "id": "CRC3",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/core-reconciliation/implementation-review.md",
          "sha256": "596ba059b759c87fdac4e3caae72afe62984c2def2fc467b84527a7ec9a39ffc"
        },
        {
          "path": "docs/reviews/core-reconciliation/clean-material-proof.json",
          "sha256": "2bae2f5c85f85690908bd3fd1ebfe43e7b234bdc35afa31e25364e6b0a624084"
        },
        {
          "path": "docs/reviews/core-reconciliation/final-preservation.json",
          "sha256": "6972c14fb40af91bc5b253a4ca6754bad2b1b8bc5a11d69e5fa3ddce0c2e811a"
        },
        {
          "path": "docs/reviews/core-reconciliation/negative-integration.json",
          "sha256": "d48800c2c812e6767e67c50544a8a38857e6d1c29315b98883c6d38826f1da7a"
        }
      ]
    },
    {
      "id": "CRC4",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root orchestrator",
      "destination": "CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md",
      "evidence": [
        {
          "path": "docs/reviews/core-reconciliation/implementation-review.md",
          "sha256": "596ba059b759c87fdac4e3caae72afe62984c2def2fc467b84527a7ec9a39ffc"
        },
        {
          "path": "docs/reviews/core-reconciliation/clean-material-proof.json",
          "sha256": "2bae2f5c85f85690908bd3fd1ebfe43e7b234bdc35afa31e25364e6b0a624084"
        },
        {
          "path": "docs/reviews/core-reconciliation/final-preservation.json",
          "sha256": "6972c14fb40af91bc5b253a4ca6754bad2b1b8bc5a11d69e5fa3ddce0c2e811a"
        },
        {
          "path": "docs/reviews/core-reconciliation/negative-integration.json",
          "sha256": "d48800c2c812e6767e67c50544a8a38857e6d1c29315b98883c6d38826f1da7a"
        }
      ]
    }
  ],
  "supportingWork": [],
  "conclusions": {
    "tranche": "COMPLETE",
    "trancheSummary": "Current-Core local recovery independently reviewed and verified on clean committed source",
    "trancheEvidence": [
      {
        "path": "docs/reviews/core-reconciliation/implementation-review.md",
        "sha256": "596ba059b759c87fdac4e3caae72afe62984c2def2fc467b84527a7ec9a39ffc"
      },
      {
        "path": "docs/reviews/core-reconciliation/clean-material-proof.json",
        "sha256": "2bae2f5c85f85690908bd3fd1ebfe43e7b234bdc35afa31e25364e6b0a624084"
      },
      {
        "path": "docs/reviews/core-reconciliation/final-preservation.json",
        "sha256": "6972c14fb40af91bc5b253a4ca6754bad2b1b8bc5a11d69e5fa3ddce0c2e811a"
      },
      {
        "path": "docs/reviews/core-reconciliation/negative-integration.json",
        "sha256": "d48800c2c812e6767e67c50544a8a38857e6d1c29315b98883c6d38826f1da7a"
      }
    ],
    "product": "COMPLETE",
    "productSummary": "Only CRC1-CRC4 workspace recovery criteria are accepted; application roadmap, EXE and headed/native UI acceptance remain separate",
    "acceptance": [
      {
        "path": "docs/reviews/core-reconciliation/implementation-review.md",
        "sha256": "596ba059b759c87fdac4e3caae72afe62984c2def2fc467b84527a7ec9a39ffc"
      },
      {
        "path": "docs/reviews/core-reconciliation/clean-material-proof.json",
        "sha256": "2bae2f5c85f85690908bd3fd1ebfe43e7b234bdc35afa31e25364e6b0a624084"
      },
      {
        "path": "docs/reviews/core-reconciliation/final-preservation.json",
        "sha256": "6972c14fb40af91bc5b253a4ca6754bad2b1b8bc5a11d69e5fa3ddce0c2e811a"
      },
      {
        "path": "docs/reviews/core-reconciliation/negative-integration.json",
        "sha256": "d48800c2c812e6767e67c50544a8a38857e6d1c29315b98883c6d38826f1da7a"
      }
    ],
    "owner": "Root closer"
  }
}
```

## Terminal disposition

Accepted implementation was committed at 5fec5a122339486f5a85afa4276362e76691d61b. The actual clean committed flow passed with explicit assessed packet coverage and matching reviewed source hashes. This settled REVIEW record grants no implementation action. Original IMPLEMENT packet/receipt and all initial failures remain in docs/reviews/core-reconciliation/. Exact terminal action assessment is refreshed before the terminal commit.
