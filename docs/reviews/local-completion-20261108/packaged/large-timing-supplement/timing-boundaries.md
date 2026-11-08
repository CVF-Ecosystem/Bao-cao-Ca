Risk: R2
Worker: Sol
Reviewer: Astra

The preserved result timings yearSummary=0.04469s and filesTab=0.06889s stop at action return before subsequent expectedDOM/decode checks; they are NOT end-to-end ready latencies. Do not use them for a readiness/speed claim. allList/page2/searchEmpty include explicit expected rendered state. upload40 stops at saved40status; actual image decode follows. viewerOpen ends at actual viewer label; report-open and40image decode follow. portableCompleted includes genuine download/save completion, hash follows. startup includes browser UIload; exit includes actualprocesswait/sessionremoval. First attempt74.24s startup, listDOMrace andexit0 retained, resumedstartup75.68s. Warmcache/host limits/no causal improvement.

40persistedPNG dimensions/hashes independently read from newreport DB; bothactualmain/viewer tab decode calls resolved. The executed driver ignored Boolean return of evaluate_all, so exact DOMcount is inferred from persisted40 attachments and unchanged render loop, not separately serialized DOMcount. All40blob PNGs decode240x140; do not treat200fakeJPEGstorageblobs as decodedimages.
