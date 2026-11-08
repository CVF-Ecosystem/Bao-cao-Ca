# PNI release documentation return

Risk: R2
Worker: Terra
Reviewer: Astra

Updated the first screen of `HUONG_DAN.txt` for 1.9.2 while preserving the existing 1.9.1 and earlier text below. Updated `tai_lieu/THAY_DOI_V1_9_2.txt` to identify the technical evidence and its limits. No application, build, or test changes and no rebuild were made in this documentation-only return.

Evidence read: `release-r3-final.json` records 191 Python tests passed with zero skips and six JavaScript groups on unchanged bytes. `native/headed-e6-proof.json` binds candidate 7ce0305b6000, successful EXE build/smoke and headed Chrome workflow; `native/persistence-export-proof.json` records persistence/export observations. The browser file-input upload was exercised; the native Windows file dialog and Python 3.9 were NOT_TESTED. Business, printing and full-roadmap acceptance remain open. Independent final review at `native-e6-review.json` is pending; no human speed claim is made.

Text-only checks verified the new guide heading, preserved historical heading and required release evidence/limitations. No application test was rerun. Exact SHA-256:

- `HUONG_DAN.txt`: cbf9b11bd6b99f5850bca364a0742616b07efb6f2e2130caf992f5b6ecea4e80
- `tai_lieu/THAY_DOI_V1_9_2.txt`: f6d59189e258aa9ba696089cadb836cf39bfffc345a48aa88deaba5d9853a97b

Astra must independently review the final wording; Root owns metadata and commits. This return does not itself approve the release or product milestone.
