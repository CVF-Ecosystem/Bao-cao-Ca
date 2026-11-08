# ADR: personnel Excel build compatibility amendment

Status: ADR_LOCKED — compatibility amendment; independent exact-action admission required.
Date: 2026-11-08

## Observed failure and inherited scope

Candidate378dab6149d5 passed the source suite but its first real E6 build failed: altgraph0.17.4 imports pkg_resources, absent from setuptools84.1.0. Preserve the failed candidate/log, original locked reader ADR and dependency-source-review.json as history; none is proof of an EXE. Application design, runtime pins openpyxl3.1.5/defusedxml0.7.1/et-xmlfile2.0.0 and SPEC remain unchanged.

## Exact build-only decision

Replace only altgraph0.17.4 with altgraph0.17.5 in the build set. Keep setuptools84.1.0 and the other nine admitted runtime/build wheel pins unchanged. This amendment supersedes only the altgraph build pin in the original ADR; no downgrade of the patched setuptools candidate. The official [0.17.5 release](https://pypi.org/project/altgraph/0.17.5/) and [upstream fix](https://github.com/ronaldoussoren/altgraph/commit/3719ef2) remove pkg_resources. Official tagged __init__.py instead declares its version directly. Root metadata observation docs/reviews/personnel-import-20261108/dependency-altgraph-0.17.5-review.json records MIT, no declared runtime requirements, wheel size21228, not yanked, SHA256 f3a22400bce1b0c701683820ac4f3b159cd301acab067c51c653e06961600597. Empty PyPI advisories are not a security certification or compatibility proof.

## Bounded implementation and acceptance

After fresh exact admission, Sol downloads only that official hash-verified wheel and updates requirements-build.txt, DONG_GOI BUILD_PINS, corresponding license notice and focused release tests. Install only in the existing isolated build-venv with --no-index --require-hashes --only-binary; no global changes or other upgrades. Add actual dependency-graph import preflight (altgraph and PyInstaller.building.build_main) before metadata/build, with controlled missing-import failure and a real successful installed-toolchain import test. Version strings alone missed the failure and are insufficient. Preserve both clean Git gates, offline builder and all reader/runtime collection rules.

Astra independently reviews the bounded delta and exact unchanged application hashes; Root commits a new clean candidate before Sol rebuilds/smokes/executes E6. Full applicable source suite, exact committed EXE hash/metadata and actual headed consumer proof remain required. This consumes the original work-order budget and stop conditions; no clock or repair-count reset. No product or E6 acceptance is granted by this amendment.
