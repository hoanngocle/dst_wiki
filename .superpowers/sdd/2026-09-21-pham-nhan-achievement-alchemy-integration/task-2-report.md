# Task 2 report — Extend Hunter Ranks to SS and SSS

## Scope

- Base: `8740fce621f2d6969f789f520c8cabcfbc79b635`
- Implementation commit: `9bfe0704` (`feat: add SS and SSS hunter ranks`).
- Report commit: this ignored report is force-added in the follow-up documentation commit.

Changed paths:

- `mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua`
- `mods/PhamNhanTuTien/scripts/components/hh_rank.lua`
- `mods/PhamNhanTuTien/tools/test_extended_ranks.py`
- `.superpowers/sdd/2026-09-21-pham-nhan-achievement-alchemy-integration/task-2-report.md`

## RED evidence

Before modifying production Lua, I created and ran the focused stdlib contract
harness:

```text
python mods/PhamNhanTuTien/tools/test_extended_ranks.py -v
Ran 5 tests
FAILED (failures=4)
```

The failures were the expected absent feature behavior: the definitions lacked
SS/SSS, S-or-higher capability coverage was incomplete, the component did not
listen for `hh_levelup` or reconcile level-only promotions, and a missing SS/SSS
exam left stale exam presentation state. The no-gameplay-row audit already
passed, confirming the baseline has no extended-rank registrations to preserve.

`Get-Command lua` reported `lua_available=False`, so the test does not claim Lua
or DST runtime execution. It is a deterministic source-contract harness that
parses static rank tables, evaluates the boundary map independently, and audits
the rank component transition contract.

## Implementation

- Extended `RANK`, labels, level requirements, level mapping, rank validation,
  and next-rank progression through `SSS` (E=1 through SSS=8).
- Added `ReconcileLevelPromotion`, driven by `hh_levelup` and load. It only
  promotes an existing S-or-higher rank using `hh_leveling`'s canonical level;
  it never demotes and does not bypass unfinished E-to-S exams.
- Level-only promotions emit `hh_rank_changed` with
  `source = "level_promotion"`, refresh guild quest offers, refresh stale exam
  presentation, and sync net values.
- When SS/SSS has no deliberately defined exam, `RefreshExamAvailability`
  clears the exam id/status/progress/target and syncs instead of retaining the
  prior S exam display.
- No exams, shop tiers/rows, EXP factors, combat stats, bonuses, or other
  gameplay unlocks were added for SS/SSS.

## Verification

Focused post-change verification:

```text
python mods/PhamNhanTuTien/tools/test_extended_ranks.py -v
Ran 5 tests in 0.051s
OK
```

The suite covers the supplied boundary map, rank API/order/validation and
next-rank bounds, S-or-higher numeric comparisons, absence of extended gameplay
rows, level 70/100 promotion boundaries, A-at-100 and SSS-no-demotion cases,
load reconciliation, event/quest/sync contract, stale exam clearing, and the
absence of fixed `1..6` rank iteration in validation/presentation code.

Required prerequisite tests do not exist at this clean baseline:

```text
mods/PhamNhanTuTien/tools/test_guild_system.py=False
mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py=False
```

I therefore did not create unrelated placeholders or report those tests as
passing. A source audit found no other relevant stdlib guild/progression test;
the focused contract suite above compensates as directed.

Broader discovery was attempted but is not a usable signal for this change:

```text
python -m unittest discover -v
Ran 23 tests
FAILED (errors=19)
```

The errors are pre-existing/environmental and unrelated to these files:
missing `lupa` and `PIL`, unavailable `%TEMP%` writes, import-path assumptions,
and permission denial for `.superpowers/dst-runtime-audit`.

Final scope and whitespace checks are recorded after the report is staged.

## Concerns

- Lua/DST runtime execution was unavailable, so validation is intentionally
  limited to the deterministic stdlib source-contract harness.
- The named unified-progression and guild-system tests are absent and must be
  rerun by Task 13 if their prerequisite artifacts later arrive.
- The broader repository unittest discovery suite remains blocked by unrelated
  dependencies and sandbox filesystem permissions.
