# Independent workspace activation implementation review

Status: ACTIVE_REFERENCE
Risk: R2
Worker: Terra activation_worker
Reviewer: Sol activation_design_review
Decision: ACCEPTED
Date: 2026-11-06

Accepted for the bounded local mechanical WSA setup implementation and full local verification flow. This result supports closure preparation and an honestly scoped FULL_FLOW_VERIFIED repair-history entry; final terminal packet admission, continuity/catalog synchronization and commit disposition remain orchestrator responsibilities. No future implementation action is authorized by this review.

Reviewed final source identities, SHA-256 after CRLF-to-LF normalization:

- `scripts/check_project_workspace.py`: `151fcbb97534c261cf8f3bc022a6cfda5e10bdd91eb1bfc87f96cdea42ac92b6`.
- `kiem_thu/test_project_workspace_checker.py`: `7c7c61412aabf5ee378c9e68d1b5fe708129dc2d6578c534e3402b94f7b2d6af`.

The adapter preserves the original doctor report and recognizes only the complete 28-row inventory, the known INST mismatch and optional paired known COV mismatch, with CONT and all25 baseline checks passing. It checks source selection and the reviewed upgrade, invokes the current trusted supplemental runner, and requires its exact four-control bootstrap family with coherent successful results. Protected inherited controls, public Core, application source and actual data were not changed by this review.

Reviewer-local repair disclosed: original parsing matched only exactly two-space status rows, so an additional status row at other indentation could be ignored. The parser now collects all status-shaped rows at any indentation, rejects unexpected uppercase status tokens through exact inventory comparison, and requires exactly one expected RESULT line. It also rejects contradictory current control outcome/findings even if ok=true. These focused corrections preserve objective, design, paths, authority, external effects and commit owner; the observed source determined the repair. No worker REWORK was necessary.

Actual commands and results:

- `python -B -m unittest kiem_thu.test_project_workspace_checker -v`: exit0, five groups PASS. The suite obtains the actual successful local flow, then checks malformed/extra/duplicate/missing checks, unrelated and CONT failures, additional COV paths and altered diagnostic codes, unexpected indentation/statuses, conflicting summaries, activation/source rejection, subprocess timeout, and missing/duplicate/failed/contradictory current controls. Synthetic substitutions are focused adapter checks, not live governance evidence.
- Final reviewed adapter `run()` (same path used by its CLI): COMPATIBLE_ASSESSED, exit0. `docs/reviews/activation-history/adapter-reviewed-full-flow.json` preserves the complete result: activation CURRENT_ASSESSED on AUTHORIZED_SUPPLEMENTAL, original doctor exit1 with26/28 and its two exact legacy failures, and current supplemental bootstrap exit0 with INST, CONT, COV and ACT PASS. The earlier CLI verification also returned COMPATIBLE_ASSESSED; final report was refreshed after the last focused parser correction.
- Test log: `docs/reviews/activation-history/adapter-reviewed-tests.txt`.

Acceptance reasoning: the exact current source works on this project, the recognized compatibility disposition preserves failed historical observations, and meaningful negative cases show that unrelated or malformed results do not receive that disposition. Existing reviewed source pins and action-specific receipt constrain the local flow. The old doctor remains failed; successful compatibility assessment is reported separately.

Limits: these are local filesystem/process and declared mechanical evidence checks. No provider call was performed and no AI/agent governance behavior is proven. Hosted CI, deployment, application acceptance, real-data recovery and native host loading remain outside this acceptance. Fixtures do not establish universal compliance. Reassess when source, policy, profile, packet bytes or relevant continuity changes; an assessed terminal review receipt cannot authorize unknown future BUILD work.
