# Independent post-commit compatibility regression review

Status: ACTIVE_REFERENCE
Risk: R2
Worker: project-orchestrator
Reviewer: Sol activation_design_review
Decision: ACCEPTED
Date: 2026-11-07

Accepted the same-scope reviewer-local correction to explicit assessed-packet propagation. Original accepted outcome, permitted paths, authority, effects and commit owner remain unchanged. No terminal action packet or activation receipt bytes were changed by this review. This record supplements the earlier exact-version review rather than rewriting its evidence.

Observed root cause: after commit, ordinary candidate discovery no longer enumerated the settled WSA order. `docs/reviews/activation-history/postcommit-unbound-bootstrap.json` preserves the actual bootstrap result: INST, CONT and ACT PASS but COV NOT_APPLICABLE_WITH_REASON, with no current packet candidates. The adapter correctly refused this weaker result because it requires actual coverage PASS. The former dirty-tree success therefore did not establish clean-tree reuse.

Correction: after successful CURRENT_ASSESSED activation, read the already validated receipt actions and pass every exact packet explicitly using --packet to the current supplemental bootstrap runner. Preserve the complete current control inventory and coherent PASS requirements. This reuses existing packet validation and makes the current settled action discoverable without weakening coverage or granting another action. Missing action packets still fail. The test uses immutable captured26/28 legacy output for parser variants while retaining actual live local positive verification, so the recognized27/28 clean-tree legacy observation does not invalidate unrelated parser tests.

Final reviewed SHA-256 identities after CRLF-to-LF normalization:

- `scripts/check_project_workspace.py`: `18c3a322da9825019ba1beeafaf9c408803c8f562ef9eba714f90d7a03c077b8`.
- `kiem_thu/test_project_workspace_checker.py`: `98e406b13bd5770e4197e7609ca940e74fd3ac4fa597ccf3edf548da992c1fce`.

Independent actual verification:

- `python -B -m unittest kiem_thu.test_project_workspace_checker -v`: exit0, six groups PASS. The added regression confirms every receipt action packet is explicitly passed; prior parser, source/activation refusal, timeout and current control-coherence checks still pass.
- Independent invocation of final adapter run(): COMPATIBLE_ASSESSED. Current bootstrap INST, CONT, COV and ACT each PASS; COV notes explicitly name `docs/work_orders/WO_WORKSPACE_ACTIVATION.md`. No roadmap/order change was required for that actual result. Root's `docs/reviews/activation-history/postcommit-bound-bootstrap.json` preserves the corresponding bound positive flow and the original legacy27/28 failure.

This accepts the implementation correction and observed explicit-packet local flow. At review time the correction is not yet the final committed clean tree; the commit steward must verify the same adapter from that final clean tree before claiming committed clean-tree acceptance. That final verification may be reported separately without changing the terminal packet or this reviewed source identity.

Limits remain local mechanical setup only. The terminal receipt is a settled REVIEW assessment, not future BUILD authority. Original doctor failures remain visible. No provider call, live AI governance behavior, hosted CI, application acceptance or deployment is established. Preserve the post-commit failed/N/A evidence alongside the corrected proof.
