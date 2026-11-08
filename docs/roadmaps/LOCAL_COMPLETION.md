# Hoàn thiện bản local trước giai đoạn web

Status: DESIGN

Authority: operator2026-11-08 explicitly approves the proposed completion sequence and requires local completion beforephase2web. Baselineeb852f3 / PNI1.9.2 remains accepted onlywithinitsownscope. Original product owner: `tai_lieu/ROADMAP_SAU_V1_9.md`; locked integratedSPEC: `docs/specs/LOCAL_COMPLETION.md`.

## Design decisions and continuation

Deliver1.10.0/schema4 using currentStore/Protection/servercontext and plainJS owners. Explicitupgrade preview/confirm is a team safety choice within alreadyauthorizedmigration, not an additionaloperatorinstruction. D2 uses wall elapsed24h sincefull, downtimeincluded, executesonlyonnextappoperation; clockrollback/missing/corruptmarkerforcesfull. Viewerretention30days; orphanblobgrace24h; explicitmaintenance afterverifiedfull, conservativeunknownretention, noVACUUM. Preservefullmigrationcopy/history/identity; sharedWindowsaccount is notrealuserauthentication. No newdependency/provider/network/globalinstall orrealdata is admitted.

Sequence: source-backed audit -> sharedSPEC/API -> exactWORK_ORDER/admission -> Terra storage/API and Sol UI/print -> source/fault review -> clean committed candidate -> current-toolchain EXE plus headed consumer/drill/large-data/actualprint proof -> independent aggregate review/freeze. Native control currently fails kernel-assetsoserror3; retain1.9.2baselineEXEforbefore/afterprint, investigate finitebrowser-onlycontrolwithoutOSsecuritychanges; otherimplementation is independent, V1 remains mandatory. Product must remainPENDING ifrequirednativeproofcannotbeobtained.

## Acceptance criteria — LOCAL

Internal engineering acceptance for the complete local release. Existing roadmap obligations remain linked, including separate operational deployment witnesses; no web work is admitted.

| ID | Required observable outcome |
|---|---|
| L1 | Core local report and correction workflows V2/V3 preserve original actors, closed status, revisions, blob hashes, source immutability and optimistic conflicts through actual headed UI. |
| L2 | Actual UI portable backup, monthly XLSX incl empty/draft month, attachments ZIP special/duplicate names and previous unfinished work boundary cases V4-V7 match predefined synthetic oracles. |
| L3 | U1-U14 desktop UI/print outcomes from original roadmap are implemented and exercised at1366x657; V1 actual Chrome and Edge print dialogs before/after U8 with headers on/off, background off, correct time/page identity/final signatures. Native dialog failure remains unproved, never replaced by scripted PDF. |
| L4 | D2 quick/full scheduling uses wall elapsed24h incl downtime, pinned last-good full survives failed replacement/prune, restore/adoption/manual backup alwaysfull, exact recovered reports/revisions/blobs and interruption/space/external-disconnect failures are verified. D4-3 disposable restore drill and recovery guidance exist. |
| L5 | D3 explicit verified schema1/2/3-to4 upgrade and legacy correction import preserve old data and recoverable copies; exact6-row save-kind oracle, OS identity caveat, conflict checks, diff U5/U11 and failed migration rollback pass. |
| L6 | D4 conservative viewer cleanup and explicit aged-orphan maintenance preview/confirm preserve correction/pending/unknown files and all report/revision/correction_base references under concurrency; reupload refreshes age; no implicit VACUUM. |
| L7 | V8 current-host large synthetic workload through real Store.save reaches near1GB and records setup cost, baseline/current latency, list/search/year-summary/40attachments responsiveness and host/storage facts without unsupported speed thresholds. |
| L8 | Full applicable release tests and exact clean committed1.10.0 EXE smoke/portable fresh-folder/upgrade/save/export/recovery/exit/restart proof pass with independent review, current user guide and recoverable upgrade instructions. PNI remains working; all skips and site/business acceptance limits disclosed. |

## Coverage and owned remainder

```cvf-milestone-coverage-json
{
  "schemaVersion": "cvf.milestoneCoverage@1.0.0",
  "authority": {
    "path": "docs/roadmaps/LOCAL_COMPLETION.md",
    "heading": "## Acceptance criteria — LOCAL",
    "sha256": "d3e51ba906511d9decdde87dbcfc0392264b15123843fc45c18739309283c953"
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
  "phase": "PLAN",
  "action": {
    "kind": "PLAN",
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
    "owner": "Root ORCHESTRATOR",
    "output": "Integrated locked local SPEC/WO and independent exact admission",
    "budgetMinutes": 20,
    "stop": "Return source-backed gaps at finiteaudit ceiling; no BUILD on missing authority",
    "next": "Independent SPEC/WO/admission review then bounded implementation"
  },
  "rows": [
    {
      "id": "L1",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Independent source/fault review and technical suite accepted; exact1.10.0 packaged consumer/failure proof remains required.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    },
    {
      "id": "L2",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Independent source/fault review and technical suite accepted; exact1.10.0 packaged consumer/failure proof remains required.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    },
    {
      "id": "L3",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "U1-U14 source accepted including quarterly reminder; exact1.10.0 Chrome/Edge short/long headers-on/off native matrix and full U consumer checks pending.",
      "owner": "Sol UI/native proof with Root blockerownership",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    },
    {
      "id": "L4",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Independent source/fault review and technical suite accepted; exact1.10.0 packaged consumer/failure proof remains required.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    },
    {
      "id": "L5",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Independent source/fault review and technical suite accepted; exact1.10.0 packaged consumer/failure proof remains required.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    },
    {
      "id": "L6",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Independent source/fault review and technical suite accepted; exact1.10.0 packaged consumer/failure proof remains required.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    },
    {
      "id": "L7",
      "state": "NOT_STARTED",
      "gap": "Near1GB real Store.save workload is being seeded under owned runtime; actual byte size, baseline/current timings and exact EXE headed large-data/40valid-image proof pending.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        }
      ]
    },
    {
      "id": "L8",
      "state": "IMPLEMENTED_UNPROVED",
      "gap": "Independent source/fault review and technical suite accepted; exact1.10.0 packaged consumer/failure proof remains required.",
      "owner": "Terra backend / Sol UI and packaged proof / Root aggregate",
      "destination": "docs/work_orders/WO_LOCAL_COMPLETION.md",
      "evidence": [
        {
          "path": "docs/reviews/local-completion-20261108/audit-astra.json",
          "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
        },
        {
          "path": "docs/reviews/local-completion-20261108/design-terra.md",
          "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-baseline.json",
          "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
        },
        {
          "path": "docs/specs/LOCAL_COMPLETION.md",
          "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-return-manifest.json",
          "sha256": "a6f059e3de70b5e917da22655fd173223ef9dada6c1826a0002d3a440d4da777"
        },
        {
          "path": "docs/reviews/local-completion-20261108/technical/release-source.json",
          "sha256": "ddb3890d743241e426759084c667f8b32fb17174bfc305392d413cd8111ade0c"
        },
        {
          "path": "docs/reviews/local-completion-20261108/source-candidate-review.json",
          "sha256": "26065913e8157523535ddc6b5bea3dce5c9cd1457935bbee4ddc0f57fe949240"
        }
      ]
    }
  ],
  "supportingWork": [
    {
      "criterionIds": [
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8"
      ],
      "reason": "Existing source/evidence leaves reallocaloutcomes unmet; integratedcontract/admission prevents incompatible server/UI/migrationchanges, reuses PNI and existing native owners.",
      "budgetMinutes": 60,
      "stop": "No repeated preparation chain or gate/core mutation; preserve failures and stop at originalsupport ceiling",
      "returnToProduct": "Admitted exactlocal implementation and independent review"
    }
  ],
  "conclusions": {
    "tranche": "PENDING",
    "trancheSummary": "Read-only audit/design only; no localimplementation admitted yet",
    "trancheEvidence": [
      {
        "path": "docs/reviews/local-completion-20261108/audit-astra.json",
        "sha256": "3b932a0fcedf594181827297f98e53d374e99033a87bb30cde402d287f5f2f95"
      },
      {
        "path": "docs/reviews/local-completion-20261108/design-terra.md",
        "sha256": "de1ea93893af37a7be7605b3b683674ac92b22a83973b24c457263bb98d7b824"
      },
      {
        "path": "docs/reviews/local-completion-20261108/source-baseline.json",
        "sha256": "dfdfb14fc9c117a8f88074265511d54966f24c41d6fdc4fc36562335dcea3133"
      },
      {
        "path": "docs/specs/LOCAL_COMPLETION.md",
        "sha256": "6e0842af89a2701b8bccb0d72f4924ee0df22effd854a71f4c6e803f7c95d385"
      }
    ],
    "product": "PENDING",
    "productSummary": "WholelocalL1-L8 notaccepted; webphase2held",
    "acceptance": [],
    "owner": "Root orchestrator"
  }
}
```

## Operational deployment and business witnesses

OriginalD0-2 measurement on actualyardhost and migration trial on a permitted copy of realDB remain explicit owned obligations; no suchdata iscurrentlyadmitted and syntheticproofmustnotbe relabeledasrealdata. Root owns re-entry upon available targethost/source and authorizeddisposablecopy. Operator explicitly answered: another yard machine, device acceptance later. Current-host engineering delivery proceeds; D0-2 hardware deployment witness is deliberately deferred by the scope owner, never mislabeledPASS. Physicalprinter/independentexternalmedia availability is separate from currenthostPDF/separate-folderproof. Engineering can be internally accepted onlyagainst definedL1-L8; business suitability and operational rollout remainseparate, no requestforusertechnicalQA. Python3.9 source execution remainsNOT_TESTEDunlessactuallyavailable; packagedPython3.11EXEisprimarydelivery. E7teamExcelmapping/stableemployeeID/HRM/sync are optionalfutureproposals, notsilentlyincluded. Web2.0 remainsfuturephase2withitsownW0decisions.

## Development application and cost

PinnedCore68a7446/profile1.4execute; CORE_AND_SUPPLEMENTALguidance inspectedseparately operator-local662cc1f61/applicationstandardd06b6238. AlllocalmechanicalgateclaimsareINVOCEDscopeonly,noprovidergovernanceclaim. R2migration/maintenance/sourcewritesuse independentAstrareview; syntheticfaulttests plusactualEXEconsumerproof precedeuserfeedback. Acceptancequestion1job=localreporting/backup/history;2standard=originalroadmap+lockedSPEC;3proof=revision-bound source/fault/UI/oracle+independentreview;4value=missinglocalcorrectness/usability/recovery, no unmeasuredspeedclaim;5delivery=cleanEXE/freshfolder+upgrade+restoreandalllimits.

PriorPNIelapsed106min isreused, otherpastcostUNKNOWN. Localauditstarted2026-11-08T07:27:34Z, finite20min. Independentwhole-local audit supports additional480min execution and60min supportingreview; exactdispatchstartrecordedbeforeBUILD. This pre-BUILD budgetdefinition is not a repairreset; allprep/retries/revieware retained, stop atceiling/thirdsame-rootrepair/missingmandatoryproof, only dependentactionsheld. Noextraexperimentssolelyforlearning.
