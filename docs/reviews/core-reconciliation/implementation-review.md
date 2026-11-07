# Independent current-Core implementation review

Status: ACTIVE_REFERENCE
Risk: R2
Worker: Terra implementation plus Root metadata recovery
Reviewer: Sol 6.1 Medium / activation_design_review
Decision: ACCEPTED
Date: 2026-11-07

Accepted for the bounded CRC project-local recovery implementation and its observed local mechanical verification. This is not terminal closure, committed clean-tree acceptance, application acceptance or new product BUILD authority. Root still owns material commit, actual committed-tree proof, terminal action reassessment and continuity/catalog disposition.

## Exact reviewed source

SHA-256 after CRLF-to-LF normalization:

- `scripts/check_project_workspace.py`: `e52d495301123beab049d2edd308919045a48d18abf6aee484fb7c78684f147a`.
- `kiem_thu/test_project_workspace_checker.py`: `0a7f2228a9df0ef34ff35115d193cc7166f227b5d9f187fb501129445cb947bb`.

The delegate verifies a full Core pin, repository identity/origin, clean tracked checkout and selected executable source bytes before invoking the pinned Core activation CLI directly. It requires current PINNED_CORE activation, inspected supplemental guidance, the exact complete29 native PASS rows with the sole canonical summary, and coherent successful results for the four trusted bootstrap controls. Verified receipt actions are supplied explicitly with --packet, retaining actual coverage even after ordinary Git candidate discovery becomes empty. No obsolete legacy failure is exempted and no inherited gate algorithm was edited.

## Reviewer-local repair

I confirmed that the worker's uppercase-only native status parser could ignore an additional lower/mixed-case status row alongside the expected29 PASS rows. The existing summary collector could likewise ignore a lower-case extra result label. Within the same two authorized files, I changed status-shaped row collection to include any bracket token, reject malformed status trailers and merged warning/error diagnostics, and collect RESULT labels case-insensitively while still requiring the exact canonical PASS summary. Added focused cases cover lower/mixed-case status, unknown/extra PASS rows, malformed bracket/trailing output, warning/error lines and lower-case/space-varied result labels.

This is the same consolidated parser finding, not a new design or scope: objective, design, paths, authority, effects and commit owner are unchanged; observed source determines the correction. The local repair is disclosed instead of hidden self-approval. No receipt, packet, inherited module, shared Core/pack or application data was changed by this reviewer.

## Actual verification and evidence

- Final reviewer command `python -B -m unittest kiem_thu.test_project_workspace_checker -v`: exit0, four groups PASS in1.503 seconds. Tests cover real disposable Git identity/drift, exact delegation arguments, invalid policy/activation/JSON shapes, native output omissions/duplicates/failures/extra diagnostics and malformed/incomplete bootstrap identity/outcomes. Reporting fixtures establish delegate behavior only.
- Final reviewer execution `python -B scripts/check_project_workspace.py --json`: exit0, CORE_ASSESSED; activation/native doctor/trusted bootstrap each exit0. Root/worker's retained `worker-full-flow.json` independently records native29/29 and explicit bootstrap INST/CONT/COV/ACT PASS. The reviewer rerun used the final corrected source identities above.
- `focused-tests.txt` and `worker-full-flow.json` preserve the worker's preceding four-group PASS and actual positive flow; their earlier observations remain distinct from the reviewer-local correction and final rerun.
- `negative-integration.json` and `negative-integration-harness.original.txt`: inspected actual canonical checks on disposable relocated copies, restored passing baseline and eleven expected refusals. Findings match the intended boundaries: wrong pin, wrong policy, lock/module changes, old receipt identity, missing control, held/unreviewed supplemental source, changed output/budget and altered invocation evidence. This is inherited local mechanical evidence, not a new semantic approval for the relocated fixture or provider governance proof. The harness never mutates shared Core/pack or reads application data.
- `installation-preservation.json` and Root's `final-preservation.json` retain source/workflow and protected/history/data preservation observations. The earlier independent admission review verified exact current metadata/action,17 installed source files and56 delivered pack files; source inspection remained separate from implementation acceptance.

## Limits and remaining closure work

Core/source checks are point-in-time observations, not an atomic filesystem lock or proof against arbitrary concurrent out-of-band mutations. Canonical activation and trusted bootstrap recheck their own identity/evidence boundaries; later source or action drift still requires reassessment. Additional informational JSON fields are not treated as independent authority. Malformed result shapes fail the public run path through its error handling; standalone helper predicates are not general external parser APIs.

Root must preserve final reviewed source bytes through commit, obtain actual clean committed-tree success, and reassess the exact terminal REVIEW action after closure changes its packet bytes. Keep original ACT failures and historical WSA acceptance. Current instructions/catalog must describe the new delegate and retain prior commands only as clearly historical context. Future product work and Antigravity headed/native verification remain separate.

No provider call was performed; no risk/approval/AI governance behavior, universal enforcement, host auto-loading, hosted CI, deployment or application acceptance is proven by these local mechanical checks.
