# Hoàn thiện bản local trước giai đoạn web

Status: CLOSED_ACCEPTED

Authority: operator2026-11-08 explicitly approves the proposed completion sequence and requires local completion beforephase2web. Baselineeb852f3 / PNI1.9.2 remains accepted onlywithinitsownscope. Original product owner: `tai_lieu/ROADMAP_SAU_V1_9.md`; locked integratedSPEC: `docs/specs/LOCAL_COMPLETION.md`.

## Design decisions and continuation

Deliver1.10.0/schema4 using currentStore/Protection/servercontext and plainJS owners. Explicitupgrade preview/confirm is a team safety choice within alreadyauthorizedmigration, not an additionaloperatorinstruction. D2 uses wall elapsed24h sincefull, downtimeincluded, executesonlyonnextappoperation; clockrollback/missing/corruptmarkerforcesfull. Viewerretention30days; orphanblobgrace24h; explicitmaintenance afterverifiedfull, conservativeunknownretention, noVACUUM. Preservefullmigrationcopy/history/identity; sharedWindowsaccount is notrealuserauthentication. No newdependency/provider/network/globalinstall orrealdata is admitted.

Sequence: source-backed audit -> sharedSPEC/API -> exactWORK_ORDER/admission -> Terra storage/API and Sol UI/print -> source/fault review -> clean committed candidate -> current-toolchain EXE plus headed consumer/drill/large-data/actualprint proof -> independent aggregate review/freeze. Original native OS-control initialization failed kernel-assetsoserror3; its failure is preserved. Browser-mediated headed native dialog and browser-saved PDF route is independently eligible, with1.9.2baseline retained; final d8de489 print matrix and subsequent exact packaged consumer outcomes are retained with explicit unchanged-effect inheritance. Final review accepts revised engineering scope; original failed observations remain history.

## Acceptance criteria — LOCAL

Internal engineering acceptance for local1.10.0, amended2026-11-08 after operator requested proportionate QA ("Kiểm tra quá kỹ, tôi nghĩ không cần thiết"). Existing functional and safety obligations remain; only two precise V8 click-to-completion timings are deferred NOT_MEASURED. Original SPEC6e0842af remains an immutable baseline; this independently reviewed terminal amendment supersedes only that measurement obligation. No web work or site/business acceptance is granted.

| ID | Required observable outcome |
|---|---|
| L1 | Core local report and correction workflows V2/V3 preserve original actors, closed status, revisions, blob hashes, source immutability and optimistic conflicts through actual headed UI. |
| L2 | Actual UI portable backup, monthly XLSX incl empty/draft month, attachments ZIP special/duplicate names and previous unfinished work boundary cases V4-V7 match predefined synthetic oracles. |
| L3 | U1-U14 desktop UI/print outcomes from original roadmap are implemented and exercised at1366x657; V1 actual Chrome and Edge print dialogs before/after U8 with headers on/off, background off, correct time/page identity/final signatures. Native dialog failure remains unproved, never replaced by scripted PDF. |
| L4 | D2 quick/full scheduling uses wall elapsed24h incl downtime, pinned last-good full survives failed replacement/prune, restore/adoption/manual backup alwaysfull, exact recovered reports/revisions/blobs and interruption/space/external-disconnect failures are verified. D4-3 disposable restore drill and recovery guidance exist. |
| L5 | D3 explicit verified schema1/2/3-to4 upgrade and legacy correction import preserve old data and recoverable copies; exact6-row save-kind oracle, OS identity caveat, conflict checks, diff U5/U11 and failed migration rollback pass. |
| L6 | D4 conservative viewer cleanup and explicit aged-orphan maintenance preview/confirm preserve correction/pending/unknown files and all report/revision/correction_base references under concurrency; reupload refreshes age; no implicit VACUUM. |
| L7 | V8 real Store.save large synthetic workload reaches near1GB; record setup cost, baseline/current representative latency, functional list/search/year-summary/40attachments and host/storage facts. Year-summary and files-tab precise click-to-completion timings are NOT_MEASURED/deferred per operator-directed reduced QA. No speed threshold, speedup claim or original-full-timing PASS. |
| L8 | Full applicable release tests and exact clean committed1.10.0 EXE smoke/portable fresh-folder/upgrade/save/export/recovery/exit/restart proof pass with independent review, current user guide and recoverable upgrade instructions. PNI remains working; all skips and site/business acceptance limits disclosed. |

## Coverage and owned remainder

```cvf-milestone-coverage-json
{
  "schemaVersion": "cvf.milestoneCoverage@1.0.0",
  "authority": {
    "path": "docs/roadmaps/LOCAL_COMPLETION.md",
    "heading": "## Acceptance criteria — LOCAL",
    "sha256": "795e79915a8a2cf9680baaef0b874aa09e687fc26ae385745ce4c401099093cb"
  },
  "milestone": {
    "id": "LOCAL",
    "consumer": "Local shift-report operator",
    "outcome": "Recoverable, usable local1.10.0 release with full workflow, print, history and maintenance proof before phase2web",
    "checkpoint": {
      "trigger": "Before dispatch and terminal developer-product acceptance",
      "owner": "Root with independent Astra review",
      "decision": "Cover allL1-L8, keep unproved native/site/business limits explicit; web deferred until complete local engineering acceptance"
    }
  },
  "phase": "REVIEW",
  "action": {
    "kind": "REVIEW",
    "selected": [
      "L1",
      "L2",
      "L3",
      "L4",
      "L5",
      "L6",
      "L7",
      "L8"
    ],
    "owner": "Root CLOSER/COMMIT_STEWARD with independent Astra REVIEWER",
    "output": "Accepted revised LOCAL L1-L8 internal engineering delivery and local EXE/guide handover; operational witnesses separate",
    "budgetMinutes": 15,
    "stop": "Stop on exact custody drift or failed required terminal gate; original480+60 ceilings continue without reset; no further product tests",
    "next": "Commit reviewed terminal records; target yard-device operational acceptance later. Web requires separate work order and W0 decisions."
  },
  "rows": [
    {
      "id": "L1",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L2",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L3",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L4",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L5",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L6",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L7",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    },
    {
      "id": "L8",
      "state": "VERIFIED",
      "gap": "",
      "owner": "Root closer with independent review",
      "destination": "docs/roadmaps/LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/final-local-review.json",
          "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
          "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
        },
        {
          "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
          "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
        },
        {
          "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
          "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
        },
        {
          "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
          "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
        },
        {
          "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
          "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
        },
        {
          "path": "docs/reviews/local-completion-20261108/partial-review.json",
          "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
        },
        {
          "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
          "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
        }
      ]
    }
  ],
  "supportingWork": [],
  "conclusions": {
    "tranche": "COMPLETE",
    "trancheSummary": "Local1.10.0 source/build/main flows accepted; known scroll defect corrected, reduced QA amendment explicit and prior failures retained",
    "trancheEvidence": [
      {
        "path": "docs/reviews/local-completion-20261108/final-local-review.json",
        "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
      },
      {
        "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
        "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
      },
      {
        "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
        "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
      },
      {
        "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
        "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
      },
      {
        "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
        "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
      },
      {
        "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
        "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
      },
      {
        "path": "docs/reviews/local-completion-20261108/partial-review.json",
        "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
      },
      {
        "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
        "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
      }
    ],
    "product": "COMPLETE",
    "productSummary": "Only revised LOCAL engineering milestone L1-L8 complete. Two fine V8 timings deferred NOT_MEASURED; yard/realdata/physicalprinter/business and optional E7/web remain separate.",
    "acceptance": [
      {
        "path": "docs/reviews/local-completion-20261108/final-local-review.json",
        "sha256": "e7bfe50685033f4d6fd01f1e2e37017a11cf05fa48b13a62c30ec9a6f1850b5e"
      },
      {
        "path": "docs/reviews/local-completion-20261108/technical/release-final.json",
        "sha256": "8b22323b7175d7c0ce9c89a60629a25e91e91a651a6c3c7248d71c1647063eed"
      },
      {
        "path": "docs/reviews/local-completion-20261108/u1-scroll-owner-root-review.json",
        "sha256": "78e42bf91f9b7af0d00a7c0a5a79d7041b0e003db63480c209ddbcad3ced3575"
      },
      {
        "path": "docs/reviews/local-completion-20261108/packaged/narrow-final-8e641d3/artifact-manifest.json",
        "sha256": "29db56dab067a5e876b98796e38b94153ac5ba70337b6d6d7103729d0a500d35"
      },
      {
        "path": "docs/reviews/local-completion-20261108/final-native-batch-review.json",
        "sha256": "f462d1a453ceac6509fe30117c1e74fe05b9d070b2524002451fcaf691cf2e0b"
      },
      {
        "path": "docs/reviews/local-completion-20261108/supplemental-native-review.json",
        "sha256": "033ba9ac220b1828e92d0c46b43ed7773774def24117b6c1b75e886c6a9003ee"
      },
      {
        "path": "docs/reviews/local-completion-20261108/partial-review.json",
        "sha256": "58ed5087c52f7d2dca74cd2700f9500175e5ba50bbb9d8a1020eff61525a9da3"
      },
      {
        "path": "docs/reviews/local-completion-20261108/print-matrix-review.json",
        "sha256": "b241a51e47c0b823d17997de52afb5f2a49526795b5c92d5284955e709c03b34"
      }
    ],
    "owner": "Root CLOSER"
  }
}
```

## Operational deployment and business witnesses

OriginalD0-2 measurement on actualyardhost and migration trial on a permitted copy of realDB remain explicit owned obligations; no suchdata iscurrentlyadmitted and syntheticproofmustnotbe relabeledasrealdata. Root owns re-entry upon available targethost/source and authorizeddisposablecopy. Operator explicitly answered: another yard machine, device acceptance later. Current-host engineering delivery proceeds; D0-2 hardware deployment witness is deliberately deferred by the scope owner, never mislabeledPASS. Physicalprinter/independentexternalmedia availability is separate from currenthostPDF/separate-folderproof. Engineering can be internally accepted onlyagainst definedL1-L8; business suitability and operational rollout remainseparate, no requestforusertechnicalQA. Python3.9 source execution remainsNOT_TESTEDunlessactuallyavailable; packagedPython3.11EXEisprimarydelivery. E7teamExcelmapping/stableemployeeID/HRM/sync are optionalfutureproposals, notsilentlyincluded. Web2.0 remainsfuturephase2withitsownW0decisions.

## Development application and cost

PinnedCore68a7446/profile1.4execute; CORE_AND_SUPPLEMENTALguidance inspectedseparately operator-local662cc1f61/applicationstandardd06b6238. AlllocalmechanicalgateclaimsareINVOCEDscopeonly,noprovidergovernanceclaim. R2migration/maintenance/sourcewritesuse independentAstrareview; syntheticfaulttests plusactualEXEconsumerproof precedeuserfeedback. Acceptancequestion1job=localreporting/backup/history;2standard=originalroadmap+lockedSPEC;3proof=revision-bound source/fault/UI/oracle+independentreview;4value=missinglocalcorrectness/usability/recovery, no unmeasuredspeedclaim;5delivery=cleanEXE/freshfolder+upgrade+restoreandalllimits.

PriorPNIelapsed106min isreused, otherpastcostUNKNOWN. Localauditstarted2026-11-08T07:27:34Z, finite20min. Independentwhole-local audit supports additional480min execution and60min supportingreview; exactdispatchstartrecordedbeforeBUILD. This pre-BUILD budgetdefinition is not a repairreset; allprep/retries/revieware retained, stop atceiling/thirdsame-rootrepair/missingmandatoryproof, only dependentactionsheld. Noextraexperimentssolelyforlearning.

## Terminal acceptance and proportionate QA — 2026-11-08

Independent final-local-review.json accepts revised L1-L8. Exact clean isolated producer commit8e641d3152581ad6341551ae3415efcb14519a2c built1.10.0/schema4; EXE SHA25610aaf013cabee0fc3b3139a0ae2605bd5f0393bbfecb9d42ff3ca6a32a648917,13192535bytes. Final app delta resets the actual .layout scroll owner only after successful opening; final small native existing/new opening, retained-scroll save and newPID reopen pass. Prior211Python/other6JS/checker4 apply to unchanged source; focused LOCAL39 passed. No claim all previous native cases reran on8e.

Original admitted586b packet, receipt and original criteria are preserved byte-for-byte in history/*before-terminal.snapshot. Operator-reduced-qa-decision.json distinguishes the exact user request from team interpretation. This amendment waives only two precise year-summary/files-tab V8 timing obligations. Functional year totals and40decoded attachments were actually observed; action-return/decode-only samples are never end-to-end latency. No new large runs, timing experiments or print matrix is needed. Actual large startup observations span74–123seconds on current host; no speed improvement guaranteed.

Acceptance layers: technical source/fault tests and exact build/smoke passed; developer-product acceptance uses predefined synthetic oracles and independent actual UI/export/upgrade/recovery/print review, with source-effect inheritance; business/device rollout is separate and not declared accepted.

Five development-owned evidence answers:
1. Job: create/correct/close a shift report, import selected flat-XLSX personnel, retain revisions, export XLSX/ZIP/print, backup and recover. Existing Store/Protection/catalog/UI owners are reused; team mapping/stable identity/web excluded.
2. Standard: original product roadmap and immutable SPEC define fields, time periods, preservation/conflict rules, explicit upgrade/maintenance consent and invalid-input errors. Synthetic fixtures and precomputed source hashes/oracles establish provenance; shared OS identity is not real user authentication.
3. Evidence: independently reviewed source/fault tests, exact old/new binary identities, actual UI correction/export/maintenance/legacy copies, Chrome/Edge native default-margin PDFs and final positive scroll/save/reopen witness. Earlier failures remain retained. Unmeasured fine timings and untested operational surfaces remain explicit.
4. Value: missing recoverable upgrade, revision attribution/diff, safe cleanup, tiered backup, usable opening/print and personnel import now have concrete successful outputs. Baseline observations are bounded; inconclusive baseline shortcut is not PASS. No causal speed or human productivity gain is claimed.
5. Delivery: exact offline clean producer EXE and current external guide/changelog; fresh disposable directory, legacy1/2/3, recoverable copy, restore and exit/restart evidence. Default A4 landscape/default margins/backgroundOFF tested; arbitrary margins or physical printing not promised. Original root unrelated user XLSX remains untouched/unopened/unignored; only authorized tracked records are committed.

Tranche conclusion: implemented/reviewed local work is settled. Product conclusion: revised local engineering milestone complete, not operational/business rollout. Root owns later target-host/authorized real-copy/independent external-media and physical-printer entry when available; no user technical QA is requested. Web stays phase2 and receives no BUILD grant. No provider API was called; local mechanical gates are INVOKED only, not live AI-governance proof. Original dispatch2026-11-08T07:44:07.889Z,480min execution/60min support ceilings unchanged; earlierPNI106min reused, other earlier/cumulative active effort UNKNOWN. Terminal15min is bounded remaining work, not reset.
