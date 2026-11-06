# Independent review of workspace activation corrective design

Status: ACTIVE_REFERENCE
Risk: R2
Worker: project-orchestrator
Reviewer: Sol activation_design_review
Decision: ACCEPTED
Date: 2026-11-06

This decision accepts the causal relevance and bounded corrective design, not execution results, dispatch readiness, or tranche closure. Authority is the user's request to apply workspace rules and resolve the remaining setup blockers within this project. The reviewer is independent of the project orchestrator and implementation worker.

Reviewed action: `docs/work_orders/WO_WORKSPACE_ACTIVATION.md`, raw SHA-256 `0d61528540db32bd5ff12ca94232325424531c39e95f4fce8f4e240cbaefe20e`. Reviewed causal assessment: `docs/reviews/activation-history/repair-causal-audit.md`, raw SHA-256 `3caf5ec79c5586cdec8f8c7d7440e89d0211d3c889720dbd7f19c5d8adf56974`. Any changed action bytes require renewed binding and review.

The observed failure has two concrete boundaries. The original doctor verifies Core identity and freshness but its old installation validator rejects the supplemental 1.4 lock. Activation separately lacks a real action receipt. I independently reproduced the doctor result, 27/28 with only the installation comparison failing as LOCK_INVALID, and inspected the activation implementation: its receipt inventory excludes ACT itself. A complete initial pre-dispatch invocation can therefore supply honest individual results while retaining its ACT failure. The corrective chain addresses these boundaries directly; repeating installation or repinning Core would not supply the missing action evidence.

The four WSA criteria preserve the product roadmap boundary and cover source identity, compatibility verification, action-specific activation and continuity. The 45-minute exact IMPLEMENT action is a reasonable finite repair scope. Prior effort remains UNKNOWN. The recorded failed repair is an explicit current projection of the reported earlier attempt, not an invented historical packet. No claim is made that a static repair proves the full outcome.

Acceptance constraints:

- Before implementation, bind an accepted repair-chain assessment to the exact work order, preserve failed history and its genuine Git baseline, complete the applicable lifecycle/role transitions, and obtain passing action admission. The present registry audit=null and INTAKE continuity do not authorize BUILD.
- Preserve the original doctor output and nonzero exit. The project adapter must verify the expected complete legacy check inventory, accept only the exact obsolete installation mismatch, and independently verify the reviewed supplemental installation plus current action. Any other failure, missing or duplicate check, unexpected output or source/receipt mismatch fails closed. The adapter's success is a separate compatibility result; the original doctor remains failed.
- Preserve inherited gate source, Core/workspace, application source, real data, prior lock/workflow and failures. Allowed implementation is the project doctor and focused verification under the stated path families; orchestration changes remain bounded project governance records.
- The receipt covers INST, CONT, RANGE, APPL, ROUTE and COV, and one supplemental assessment. Use actual per-control outcomes; retain N/A semantics, preserve the initial ACT failure, pin immutable invocation evidence and obtain independent action-specific review. Never promote configured invocation to observed execution.
- Verify the positive path and refusal of unrelated legacy failures, incomplete or unexpected legacy output, and source/receipt tampering using disposable inputs. A fixture result establishes adapter behavior only; it is not live provider governance proof.
- Before closure, independently review the actual implementation and evidence, synchronize continuity/catalog, and retain application acceptance, hosted CI and live AI governance as unproven. This review makes no provider-backed governance claim and authorizes no provider/network, deployment or application-data effect.

The orchestrator owns preparation and binding of the machine repair assessment. This review does not certify a future assessment's hashes, field joins, packet pin or invocation evidence.
