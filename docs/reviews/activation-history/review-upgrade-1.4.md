# Independent review: workspace activation profile upgrade

Date: 2026-11-06
Risk: R2
Worker: project-orchestrator (previous upgrade implementer)
Reviewer: Terra 6.1, independent read-only reviewer
Authority: user request to resolve project activation blocker; project maintainer routes the reviewed local upgrade.
Decision: ACCEPTED, limited to installation and consistency of the delivered operator-local profile 1.4 bundle and CI pin configuration.

Review observations: 17 installed files match their individually hashed source artifacts; all 53 file artifacts in the delivery manifest match their raw SHA-256 (one directory has no file hash). The generated workflow raw SHA-256 and its three profile/runner/bundle pins match the lock. Profile 1.2 lock and workflow were preserved in this directory. Public Core remains pinned at c4c8767ac8861854f40d466ba338ffd11eb9558e; the supplemental lock uses UNKNOWN because no full source commit was independently verified. The installer reported UPGRADED; the trusted supplemental bootstrap invocation passed installation and continuity controls, and reported the activation receipt missing.

Limits: hash agreement is delivery consistency, not an independent provenance trust anchor or full semantic code review. This review does not accept any task-specific activation receipt, establish hosted CI execution, live governance, product readiness, or waive future control assessments. The workflow template comment mentions profile 1.1; functional pins correspond to 1.4. The old public-Core doctor may report trusted mismatch against the intentionally supplemental bundle.
