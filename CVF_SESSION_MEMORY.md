# Project Session Memory

Memory class: POINTER_RECORD

This is the project continuity front door. It is CVF-governed project state,
not provider-specific memory and not a chat transcript.

## Current Truth

- Contract: cvf.downstreamContinuityContract@1.0.0
- Current mode: REVIEW
- Active phase: REVIEW
- Active handoff: CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md

Update these four lines together with `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
the active handoff and `IMPLEMENTATION_STATUS.json`. The portable gate runner
reports any disagreement with a field-specific locator.

## Startup Order

1. Read `.cvf/manifest.json` and `.cvf/policy.json`.
2. Read `CVF_SESSION/ACTIVE_SESSION_STATE.json`.
3. Read the active handoff named by that state file.
4. Read `IMPLEMENTATION_STATUS.json` and `docs/INDEX.md`.
5. Read matching records from `docs/reviews/learnings/README.md` before similar work; the home indexes shared findings and parent feedback.
6. State current mode, active handoff, next allowed move, parked checkpoint,
   and active role before material work.

## Mandatory Continuity Rehydration

Repeat the startup order before material work at every new or resumed
chat/session, after context loss or compaction, at the start of every new
tranche or work order, and whenever responsibility or the active handoff
changes. Read current files again; do not rely on chat history,
provider-local memory, or a declaration from a previous session.

Emit a fresh `CVF Agent Declaration` before the first material action. At a
tranche transition, also record the acknowledgment in the active handoff
before BUILD. If continuity surfaces disagree, stop and report
`BLOCKED_CONTINUITY_DRIFT`.

Active state: `CVF_SESSION/ACTIVE_SESSION_STATE.json`

Initial active handoff: `CVF_SESSION/handoffs/AGENT_HANDOFF_V1_2026-11-06.md`

Provider-local files may assist execution but are not project source authority.

## Historical accepted setup

Previous supplemental profile1.4 setup and compatibility doctor were accepted at their recorded source identity. Their original review and six focused groups remain preserved in docs/reviews/activation-history/. They are historical evidence and do not authorize the current Core migration. Read docs/reviews/learnings/WSA_BOOTSTRAP_CONVERGENCE.md before similar recovery.

## Current Core recovery

Operator2026-11-07 authorizes docs/work_orders/WO_CORE_RECONCILIATION.md. Source changes from c4c8767 to68a7446; preserve CORE_AND_SUPPLEMENTAL guidance but execute PINNED_CORE. Prior accepted setup and receipts are historical. Current activation/readiness is pending fresh assessment; no prior PASS covers this migration. Root owns metadata/receipts and commit; Terra6.1High owns doctor/tests after admission, Sol6.1Medium independently reviews. No parked operator decision; product and Antigravity headed/native acceptance remain open.
