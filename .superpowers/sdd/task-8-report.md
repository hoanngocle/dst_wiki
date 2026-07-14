# Task 8 implementation report

## Outcome

- Added deterministic frontend exports for every normalized entity, including names,
  descriptions, stats, recipes with nested dependencies, acquisition sources, effects,
  relations, confidence, and icon keys.
- Added an asset export with availability, texture checksum, UV data, and structured
  source evidence for UI use.
- Added deterministic coverage and validation reporting for entity counts, optional
  field coverage, unresolved dependencies, SQLite foreign keys, runtime/extraction
  errors, conflicts, URL/wiki leakage, and copied archive manifest checksums.
- Wired `export`, `validate`, and the exact offline `all` stage order. `all` validates
  the existing `data/raw/runtime.json` but never invokes or installs the runtime probe.
- JSON and coverage writes use atomic replacement and contain no generated timestamps.

## TDD and test evidence

- RED: `python3 -m unittest tests.extract.test_export_validate -v` initially failed
  with `ModuleNotFoundError: No module named 'tools.extract.export_json'`.
- GREEN focused: 5 tests passed.
- GREEN full: `python3 -m unittest discover -s tests/extract -v` passed 59 tests.

## Real pipeline evidence

`python3 -m tools.extract.cli all` was run twice. Both runs exited 0 and reported:

- static: 629 entities, 418 asset facts, 5 named extraction warnings
- runtime import: 1,781 facts, 43 named prefab errors
- base enrichment: 464 requests, 62 resolved base-game entities, 0 unresolved
- database: 691 entities, 5,102 evidence rows, 403 retained conflicts
- validation: 629 `tu_tien`, 62 `base_game`, 0 hard failures, 7 warnings

The second run matched the first byte-for-byte for all four checked artifacts:

- `public/data/catalog.json`: `4e5f4443aa7075ad1a832f2a0b031a104e823d1c960780a4435ffe23a6930a67`
- `public/data/assets.json`: `696a56cb4cd912d5c6b32eaa735cbf698d3afe1a6d23a81818c671c29f16d71e`
- `data/generated/coverage.json`: `e53a2ee252b60a1e76471a064fc67b832ce6ab13829940aa60673538d002074d`
- `data/generated/wiki.sqlite`: `b528b14864f8f3440220c1fb0e0c099a9eac4d497d8f034f210549a6688da2e5`

`sqlite3 data/generated/wiki.sqlite 'pragma foreign_key_check; pragma integrity_check;'`
returned no foreign-key rows and `ok`.

## Data spot checks

- `base_game:goldnugget`, `base_game:silk`, and `base_game:nightmarefuel` include
  Vietnamese and English names, icon keys, and their available recipes/stats/acquisition.
- `tu_tien:xd_crc` exports a nested recipe referencing `base_game:cutstone`,
  `base_game:boards`, and `tu_tien:xd_lingshi1` with positions and amounts.
- Export totals: 691 catalog entities and 524 assets, of which 474 are available.
- Final coverage has 0 unresolved dependencies, 0 foreign-key errors, 0 URL/wiki
  leaks, and 0 archive checksum errors. Optional coverage gaps and all 141 extraction
  diagnostics remain explicit warnings rather than being silently dropped.

## Constraints

- No network/wiki crawler was used.
- No files under the three mod directories were modified.
- Runtime server execution/installation was not invoked by `all`.
