# Supplemental independent corrective-design review

Status: ACTIVE_REFERENCE
Risk: R2
Worker: project-orchestrator
Reviewer: Sol activation_design_review
Decision: ACCEPTED
Date: 2026-11-06

This accepts a narrowly specified correction to the compatibility design under the existing user-authorized WSA setup objective, paths, R2 ceiling, external-effect boundary and commit owner. It does not accept an amended packet not yet seen, authorize implementation before renewed admission, or claim completion.

I inspected `scripts/check_project_workspace.py` and independently ran the pinned original doctor. The observed result is 26/28: all 25 non-gate baseline checks and legacy CONT pass; INST fails with `LOCK_INVALID@.cvf/gate-profile.lock.json`; COV fails with `COV_OBJECT_SHAPE` at exactly `docs/roadmaps/WORKSPACE_ACTIVATION.md` and `docs/work_orders/WO_WORKSPACE_ACTIVATION.md`. The prior 27/28 observation remains valid for its earlier inputs. The new failure follows enrollment of the current registry1.1 repairControls into a project whose pinned Core coverage validator predates that schema. It is a new compatibility boundary, not evidence of a new failure in product behavior.

Chosen route: retain the complete legacy inventory and observations, permit only the two precisely identified version incompatibilities, and require a complete current supplemental bootstrap result for INST, CONT, COV and ACT. This is safer than broadly ignoring the legacy gate family and is maintainable because authoritative gate semantics are delegated to the reviewed current bundle rather than reimplemented locally.

Required implementation contract:

- Preserve every legacy row, detail and exit. Require the exact complete ordered 28-check inventory once each. All 25 non-gate checks and legacy CONT must PASS. Missing, duplicate, reordered, unknown or malformed checks reject.
- Permit legacy INST failure only with the exact known LOCK_INVALID diagnostic and legacy COV failure only with the exact COV_OBJECT_SHAPE diagnostics for the two current WSA documents. No wildcard document, code or gate exception is accepted. Require consistent original exit and summary counts. A recognized earlier 27/28 variant may remain supported, but cannot excuse a COV failure missing either required current diagnostic or containing an extra diagnostic. Do not accept arbitrary extra failure lines outside the parsed check table.
- Treat the three legacy profile-gate rows as preserved version-bound observations, never a legacy PASS. Require actual current INST, CONT, COV and ACT checks from the reviewed supplemental source, the exact complete current control inventory, coherent PASS outcomes and successful exit. A changed current inventory requires explicit design review. Activation must independently be CURRENT_ASSESSED for the exact rebound action and authorized supplemental source.
- Preserve Core pin, protected inherited modules, application source, real data and shared workspace. Reuse verified existing selectors and runner. Maintain the original WORK_ORDER 45-minute action budget; this finding does not silently restart it. If remaining time cannot fit, record the boundary for orchestration.
- Tests must exercise the actual 26/28 shape, positive current verification, rejection of unrelated baseline or CONT failure, missing/duplicate/extra diagnostics and checks, a third coverage path or different coverage code, contradictory summary/exit, and any failed or absent current control. Disposable fixture observations prove parser behavior only.
- Amend the exact action packet, accepted repair assessment and action receipt before resuming worker execution. Preserve the old admitted packet/receipt and failed adapter outcome as immutable evidence; re-review action-specific invocation bindings because changed packet bytes stale every prior binding. Record the new evidence as a distinct root cause in the same causal chain rather than erasing the failed repair.

The first design review's instruction to allow only INST is superseded solely by the precise additional COV incompatibility above. All other scope, independent result review and evidence limits remain. No inherited control is disabled; original failure and separate compatibility result must both remain visible. Static local checks do not prove live AI governance, hosted CI or application readiness.

Terminal closure plan is acceptable in principle: preserve the admitted IMPLEMENT artifact and receipt; append a MET history record only after exact-version full local setup flow and independent result acceptance; close the original order with REVIEW coverage, remove it from activeWorkOrders and synchronize settled continuity. A new terminal action receipt is a mechanical assessment of that review packet, not permission for a future BUILD. Keep APPL's actual terminal outcome and rationale; do not force a N/A or PASS. Clearing audit is allowed only when all affected repair failures have genuine full-flow resolution evidence.
