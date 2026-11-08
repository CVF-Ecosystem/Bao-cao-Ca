# Validation hotpath worker return

Risk: R2
Worker: Terra (REPAIR_WORKER)
Reviewer: Astra (independent review pending)

The sole product change compiles the same XML-control pattern once and invokes its `.sub` with the same replacement and strip. Type/length guards, error behavior, default flags, report validation and all other behavior remain intact. Differential tests compare the prior expression on all 32 C0 characters individually and combined, embedded and boundary tab/LF/CR, empty, boundary and over-limit strings, nonstrings, Vietnamese, combining and astral Unicode.

Reviewed Python 3.11.9 build environment: `PYTHONPATH=ma_nguon;kiem_thu`, `python -X utf8 -B -m unittest discover -s kiem_thu -t . -p KIEM_THU*.py -v` ran 211 tests, 0 skips, in 40.897 s. Raw log `.cvf/runtime/local-completion-20261108/fixtures-terra/benchmark/profile/hotpath-full-python.log`; injected-disconnection error logging in passing tests is expected. JS source was not modified by this worker; independent current UI evidence belongs to Sol.

One unprofiled same-dataset pair, warm OS cache uncontrolled, ran before/after sequentially on the same 1.25 GB synthetic DB with the legitimate identity-matched 200-hash cache. Before full/quick: 28.896/28.465 seconds. After full/quick: 33.331/30.200 seconds. Total inspection time 120.892 seconds, under five-minute cap. One pair does not demonstrate improvement; no causal speed or threshold claim is warranted. Full and quick return objects were respectively identical; DB SHA-256 before/after each pair `51757e7c9db4af7bfa43e6b5a5ae09c8f0b3987c64705e6c024a0bae037c5307`, sidecar observations identical (DB only). Source hashes and complete result objects in `.cvf/runtime/local-completion-20261108/fixtures-terra/benchmark/profile/{before,after}-unprofiled.json`; script is `fixtures-terra/inspect_unprofiled.py`. Host details remain `fixtures-terra/host.json`. Source DB and fixture were not mutated.

## Frozen worker files and SHA-256

- `ma_nguon/NGHIEP_VU.py`: `6c8736ec4f276fd82087e5e82dcbf29b1a3f4952bde8d707c4ddead17d5d074f`
- `kiem_thu/KIEM_THU_LOCAL_COMPLETION.py`: `2c3d7ab1aa2eda2b52a9f44caa7fab6301ac6fe0a9d8666d6a87514de560e9b1`

No commit made. Independent review must decide whether the unchanged semantics and hypothesized dispatch savings justify retaining this microchange despite the observed timing pair.
