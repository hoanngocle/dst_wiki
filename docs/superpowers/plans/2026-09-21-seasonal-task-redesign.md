# Seasonal Task Redesign Implementation Plan

> **Required execution mode:** Use `superpowers:subagent-driven-development` to implement this plan task-by-task. Use a fresh implementer subagent and a fresh reviewer subagent for each task; do not run implementation tasks in parallel.

**Goal:** Replace Achievement & Level's legacy six-slot seasonal-task system with four curated 50-task catalogs, a locked 20-task seasonal draw, per-completion XP claims, repeatable tasks capped at five claims, and chest milestones at 5/10/15/20.

**Architecture:** Keep the work isolated in `mods/AchievementLevel`. Convert `seasonaltaskdata.lua` into a static, validated catalog and put selection/state transitions in a small pure Lua module. `allachivevent` remains the server authority for listeners, persistence, claims, migration, and season changes. Network fields expose 20 slot snapshots; the UI renders those snapshots as a scrollable list and only sends claim requests.

**Tech Stack:** Don't Starve Together Lua, DST net variables/RPC/widgets, Python `unittest` catalog validators, Lupa/Lua 5.1 component harness, Git.

**Spec:** `docs/superpowers/specs/2026-09-21-seasonal-task-redesign-design.md`

## Scope and invariants

- Modify only `mods/AchievementLevel` in this implementation. Treat `mods/2937640068` as read-only evidence and do not modify `mods/PhamNhanTuTien` yet.
- Preserve Level, XP, Stars, perks, attribute points, and ordinary achievements when loading an old save.
- Do not choose XP numbers. Every valid task claim must call one resolver with `task_id`, `kind`, and `claim_index`.
- Keep the four existing chest reward handlers as temporary reward hooks; only change their thresholds to 5/10/15/20.
- A task must be unique by both `id` and semantic signature: `event + handler/condition + target`. Renaming a duplicate or adding a numeric suffix does not make it a different task.
- Catalog totals are exactly four seasons × (40 once + 10 repeat) = 200 tasks.
- Active totals are exactly 16 once + 4 repeat = 20 tasks, sampled without replacement and locked until the season changes.
- Repeatable tasks grant up to five separate XP claims. Only the first claim contributes one point to chest progress.
- No character pool, `other` pool, manual reroll, or client-authoritative reward path remains.

## File map

### Create

- `mods/AchievementLevel/scripts/systems/seasonaltasklogic.lua` — pure catalog lookup, validation, selection, slot state transitions, milestone eligibility, and legacy-season-state detection.
- `mods/AchievementLevel/tests/seasonaltask_harness.py` — shared Lupa setup and DST stubs for loading the pure module/component.
- `mods/AchievementLevel/tests/test_seasonal_task_catalog.py` — catalog shape, uniqueness, strings, and solo-safety tests.
- `mods/AchievementLevel/tests/test_seasonal_task_logic.py` — deterministic selection and claim-state tests.
- `mods/AchievementLevel/tests/test_seasonal_task_component.py` — save/load, migration, transition, listener, reward, and anti-double-claim tests.
- `mods/AchievementLevel/tests/test_seasonal_task_network_ui.py` — source-contract checks for 20 net slots, RPC removal, scroll list, and thresholds.
- `mods/AchievementLevel/docs/seasonal-task-curation.md` — final 200-task review table and curation rationale.
- `mods/AchievementLevel/docs/seasonal-task-ingame-checklist.md` — short host/client smoke checklist.

### Modify

- `mods/AchievementLevel/scripts/constants/seasonaltaskdata.lua` — retain reusable event helpers, replace legacy pools with four curated catalogs, and export stable numeric/task-ID maps.
- `mods/AchievementLevel/scripts/components/allachivevent.lua` — replace six legacy slots with the 20-slot server state and migration logic.
- `mods/AchievementLevel/scripts/functions/achievfunctions.lua` — replace six-slot replication setters with 20-slot snapshot setters.
- `mods/AchievementLevel/modmain.lua` — declare the new net fields and remove client-triggered seasonal reroll.
- `mods/AchievementLevel/scripts/system/rpc.lua` — add per-task claim RPC, retain chest claim RPCs, remove `refreshSeasonalTask`.
- `mods/AchievementLevel/scripts/widgets/uiachievement.lua` — render/update a scrollable 20-row task list with per-row Claim buttons.
- `mods/AchievementLevel/main_strings.lua` — add task-state, claim, repeat-count, and 5/10/15/20 milestone copy.
- `mods/AchievementLevel/main_strings_cn.lua` — mirror the new string keys so language switching cannot yield missing labels.
- `mods/AchievementLevel/tools/export_seasonal_tasks.py` — understand the new schema and emit the curated review document.
- `mods/AchievementLevel/tests/test_seasonal_task_export.py` — update legacy inventory expectations to the new 200-task catalog.
- `mods/AchievementLevel/tests/test_eva_task_scope.py` — replace obsolete generic-character-slot assertions with the no-character-pool contract.

## Public interfaces to implement

`scripts/constants/seasonaltaskdata.lua` returns a module with:

```lua
{
    VERSION = 2,
    SEASONS = { "spring", "summer", "autumn", "winter" },
    MILESTONES = { 5, 10, 15, 20 },
    POOLS = { spring = {...}, summer = {...}, autumn = {...}, winter = {...} },
    BY_ID = { [task_id] = task_definition },
    ID_TO_CODE = { [task_id] = numeric_code },
    CODE_TO_ID = { [numeric_code] = task_id },
    GetSeasonKey = function(world_state) ... end,
}
```

Each task definition has exactly these required fields:

```lua
{
    id = "stable_snake_case_id",
    name = STRINGS.SEASONAL_TASK["stable_snake_case_id"],
    season = "spring", -- spring/summer/autumn/winter
    kind = "once",     -- once/repeat
    event = "oneat",
    fn = function(inst, data, slot_index) ... end,
    handler = "eatfn", -- stable validator/debug label
    condition = 'foodprefab = "example"',
    target = 1,
    xp_reward_key = "seasonal_once",
    max_claims = 1,
}
```

`scripts/systems/seasonaltasklogic.lua` returns pure functions:

```lua
ValidateCatalog(catalog) -> true | false, error_message
SelectTasks(catalog, season_key, rng) -> { 20 task_ids }
NewSlot(task_definition) -> slot_state
Advance(slot_state, amount) -> changed, became_ready
CanClaim(slot_state) -> boolean
Claim(slot_state) -> claim_index, first_claim | nil
UniqueClaimCount(slots) -> integer
CanClaimMilestone(unique_count, milestone_index, claimed_flags) -> boolean
IsLegacySave(data) -> boolean
```

The saved seasonal envelope is:

```lua
seasonal_tasks = {
    version = 2,
    season = "spring",
    slots = {
        {
            task_id = "...",
            progress = 0,
            ready = false,
            claims = 0,
            counted_for_chest = false,
            closed = false,
        },
        -- exactly 20 entries
    },
    chest_claimed = { false, false, false, false },
}
```

## Task 1: Curate and validate the four catalogs

**Files:**

- Modify: `mods/AchievementLevel/scripts/constants/seasonaltaskdata.lua`
- Modify: `mods/AchievementLevel/tools/export_seasonal_tasks.py`
- Create: `mods/AchievementLevel/tests/test_seasonal_task_catalog.py`
- Modify: `mods/AchievementLevel/tests/test_seasonal_task_export.py`
- Create: `mods/AchievementLevel/docs/seasonal-task-curation.md`

**Step 1: Write failing catalog tests**

Test all of the following before touching the catalog:

- seasons are exactly `spring`, `summer`, `autumn`, `winter`;
- each season contains 50 entries, 40 `once` and 10 `repeat`;
- all 200 IDs and numeric codes are globally unique;
- semantic signatures are globally unique;
- every entry has all required fields and a matching `STRINGS.SEASONAL_TASK` key;
- `max_claims` is 1/5 and `xp_reward_key` is `seasonal_once`/`seasonal_repeat` according to kind;
- no task definition contains `character`, `char`, `other`, or a player-to-player-only condition;
- repeat targets describe common solo actions and do not include `get_fed_by_another_player`;
- there are no legacy functions named `chasni_getseasonalcharlist` or `chasni_getseasonaltasklists`.

Run:

```powershell
python -m unittest mods.AchievementLevel.tests.test_seasonal_task_catalog -v
```

Expected: FAIL against the six-slot/ten-pool source.

**Step 2: Curate from the existing inventory**

Use `mods/AchievementLevel/docs/seasonal-task-inventory.md` as the candidate source. Keep a candidate in its original real season unless the action is clearly more appropriate elsewhere. Select 40 old standard entries as `once` and 10 old count entries as `repeat` per season.

For repeat tasks, use this reviewed seed set and only replace an item if its event/prefab is proven invalid in current DST:

- Spring: `eat_10_wet_goops`, `eat_10_foods_while_starving`, `kill_10_bees`, `kill_10_killer_bees`, `kill_10_frogs`, `kill_10_crawling_horrors`, `catch_10_butterflies`, `catch_10_things_using_a_net`, `pick_10_flowers`, `till_soil_10_times_using_a_hoe`.
- Summer: `eat_10_fists_full_of_jam`, `eat_10_pierogies`, `kill_10_mosquitos`, `mine_10_stone_fruits`, `hammer_things_10_times`, `pick_10_banana_bushes`, `pick_10_monkeytails`, `pick_10_cacti`, `pick_10_oasis_cacti`, `row_10_times`.
- Autumn: `eat_10_honey_hams`, `eat_10_honey_nuggets`, `eat_10_trail_mixes`, `kill_10_crows`, `kill_10_red_birds`, `chop_down_10_birchnut_trees`, `chop_down_something_10_times`, `pick_10_grass`, `pick_10_saplings`, `plant_10_birchnuts`.
- Winter: `eat_10_kabobs`, `eat_10_meatballs`, `eat_10_meaty_stews`, `kill_10_snowbirds`, `kill_10_puffins`, `kill_10_pengulls`, `chop_down_10_evergreens`, `chop_down_10_lumpy_evergreens`, `mine_10_mini_glaciers`, `pick_10_lichens`.

For the 40 one-shot entries in each season, preserve a mix of food, combat, crafting, gathering, and exploration; reject multiplayer-only actions and every semantic duplicate reported by the validator. Do not silently weaken a task to make it unique: select a genuinely different old task.

**Step 3: Rewrite the data module**

- Keep the old event helper implementations that are still referenced by selected entries.
- Change their completion callback to `inst.components.allachivevent:AdvanceSeasonalTask(slot_index, 1)`.
- Delete unused helpers and all `other`, character, standard/count slot-dispatch globals.
- Build `BY_ID`, `ID_TO_CODE`, and `CODE_TO_ID` once when the module loads; fail early on an invalid catalog.
- Preserve IDs used in `STRINGS.SEASONAL_TASK` wherever possible.

**Step 4: Update the exporter and generated review table**

Emit season, kind, ID, display name, event, handler, condition, target, and source provenance. The summary must show 200 total and 50/40/10 per season. Do not overwrite the old audit file; generate `seasonal-task-curation.md`.

Run:

```powershell
python mods/AchievementLevel/tools/export_seasonal_tasks.py
python -m unittest mods.AchievementLevel.tests.test_seasonal_task_catalog mods.AchievementLevel.tests.test_seasonal_task_export -v
```

Expected: PASS.

**Step 5: Commit**

```powershell
git add mods/AchievementLevel/scripts/constants/seasonaltaskdata.lua mods/AchievementLevel/tools/export_seasonal_tasks.py mods/AchievementLevel/tests/test_seasonal_task_catalog.py mods/AchievementLevel/tests/test_seasonal_task_export.py mods/AchievementLevel/docs/seasonal-task-curation.md
git commit -m "feat: curate seasonal task catalogs"
```

## Task 2: Implement the pure selection and claim state machine

**Files:**

- Create: `mods/AchievementLevel/scripts/systems/seasonaltasklogic.lua`
- Create: `mods/AchievementLevel/tests/seasonaltask_harness.py`
- Create: `mods/AchievementLevel/tests/test_seasonal_task_logic.py`

**Step 1: Establish the Lua 5.1 test harness**

Use the bundled Python 3.12 executable. If Lupa is absent, install it into an isolated, ignored directory `mods/AchievementLevel/.test-runtime`; do not modify global Python:

```powershell
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m pip install --target mods/AchievementLevel/.test-runtime lupa
```

Add `.test-runtime/` to the mod-local `.gitignore` if one exists, otherwise to the repository `.gitignore` only after confirming it does not overlap another task's edit.

**Step 2: Write failing behavioral tests**

Cover:

- deterministic RNG always returns 20 unique IDs with 16 once and 4 repeat;
- source pools are never mutated by selection;
- once task: active → ready → claim 1 → closed; second claim rejected;
- repeat task: five active/ready/claim cycles; claim 5 closes; claim 6 rejected;
- progress stops while ready so excess events cannot queue hidden claims;
- only first repeat claim flips `counted_for_chest`;
- `UniqueClaimCount` is bounded at 20;
- milestone eligibility is exactly 5/10/15/20 and respects prior claim flags;
- `IsLegacySave` detects six-slot fields and does not classify version-2 data as legacy.

Run:

```powershell
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest mods.AchievementLevel.tests.test_seasonal_task_logic -v
```

Expected: FAIL because the module does not exist.

**Step 3: Implement the smallest pure module**

- Use Fisher–Yates selection with the injected RNG; do not call global RNG inside tests.
- Copy selected IDs into a new array.
- Clamp progress to target.
- Make `Claim` return `nil` for invalid states so the component can reject duplicate RPC calls without side effects.
- Keep DST entities, listeners, net variables, and rewards out of this module.

**Step 4: Run tests and commit**

```powershell
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest mods.AchievementLevel.tests.test_seasonal_task_logic -v
git add mods/AchievementLevel/scripts/systems/seasonaltasklogic.lua mods/AchievementLevel/tests/seasonaltask_harness.py mods/AchievementLevel/tests/test_seasonal_task_logic.py
git commit -m "feat: add seasonal task state machine"
```

## Task 3: Replace component state, save/load, and season transitions

**Files:**

- Modify: `mods/AchievementLevel/scripts/components/allachivevent.lua`
- Modify: `mods/AchievementLevel/scripts/functions/achievfunctions.lua`
- Modify: `mods/AchievementLevel/tests/test_eva_task_scope.py`
- Create: `mods/AchievementLevel/tests/test_seasonal_task_component.py`

**Step 1: Write failing component tests**

With stubbed `inst`, listeners, `TheWorld.state`, `levelsystem`, and chest handlers, test:

- first initialization creates and registers exactly 20 listeners;
- same-season save/load restores the same IDs, progress, ready flags, claim counts, and chest flags;
- old `task1code`…`task6code`/`taskprize1`…`taskprize4` data is ignored only for the seasonal subsystem;
- unrelated component fields round-trip unchanged;
- `AdvanceSeasonalTask` changes only the addressed slot;
- `ClaimSeasonalTask` calls `ResolveSeasonalTaskXP(task_id, kind, claim_index)` exactly once after a valid state transition;
- a duplicate claim RPC has no XP or chest effect;
- a repeat task's first claim increments unique progress and claims 2–5 do not;
- chest handlers become eligible at 5/10/15/20 and remain one-shot;
- a real season-key change auto-claims ready tasks and eligible chests before removing listeners/resetting;
- a repeated same-season callback does not regenerate tasks;
- entering mid-season without version-2 data generates once.

Expected: FAIL against the current component.

**Step 2: Implement version-2 state**

Replace the constructor's six task fields with `self.seasonal_tasks`. Add private methods for:

- current season-key lookup;
- creating/restoring slot state;
- registering/unregistering each selected task's event listener;
- pushing a full net snapshot;
- resolving task XP through the single injected/default resolver;
- auto-claiming ready tasks and eligible chests;
- handling a season-key change.

Do not route seasonal tasks through `CheckAchievement`, `CountAchievement`, or the ordinary `ach_lists.task1`…`task6` flags. Ordinary achievement completion remains unchanged.

**Step 3: Implement safe persistence and migration**

- `OnSave` writes `seasonal_tasks` version 2 plus all existing nonseasonal fields.
- `OnLoad` restores valid same-season version-2 data.
- If version-2 data is missing/invalid or only old six-slot fields exist, discard just seasonal data and schedule one fresh generation after component readiness.
- Never copy old `taskprize` flags into the new season.
- Do not mutate or delete Level/XP/Star/perk/attribute data owned by other components.

**Step 4: Remove obsolete replication setters**

Delete six `gettaskNcode`, `checktaskN`, and `currenttaskN` paths only after the new snapshot setters exist. Keep ordinary achievement replication intact.

**Step 5: Run tests and commit**

```powershell
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest mods.AchievementLevel.tests.test_seasonal_task_logic mods.AchievementLevel.tests.test_seasonal_task_component mods.AchievementLevel.tests.test_eva_task_scope -v
git add mods/AchievementLevel/scripts/components/allachivevent.lua mods/AchievementLevel/scripts/functions/achievfunctions.lua mods/AchievementLevel/tests/test_eva_task_scope.py mods/AchievementLevel/tests/test_seasonal_task_component.py
git commit -m "feat: migrate seasonal task component"
```

## Task 4: Add 20-slot replication and server-authoritative RPCs

**Files:**

- Modify: `mods/AchievementLevel/modmain.lua`
- Modify: `mods/AchievementLevel/scripts/system/rpc.lua`
- Create: `mods/AchievementLevel/tests/test_seasonal_task_network_ui.py`

**Step 1: Write failing network/RPC contract tests**

Assert that:

- `modmain.lua` creates 20 numeric task-code fields, 20 progress fields, 20 state fields, and 20 claim-count fields using a loop and unique net names;
- it exposes season key/version and four chest flags;
- no UI/world-state callback sends `refreshSeasonalTask`;
- `rpc.lua` has `claimSeasonalTask(player, slot_index)` and validates integer range 1–20 before calling the component;
- chest RPC validates milestone index 1–4;
- `refreshSeasonalTask` no longer exists;
- no RPC accepts task IDs, progress, ready flags, or XP amounts from the client.

**Step 2: Implement replication**

Use stable field names:

```lua
seasonaltaskcode1..20
seasonaltaskprogress1..20
seasonaltaskstate1..20
seasonaltaskclaims1..20
seasonaltaskseason
seasonaltaskversion
taskprize1..4
```

Use numeric state values `0=empty`, `1=active`, `2=ready`, `3=closed`. Use numeric catalog codes on the wire and task IDs in saves.

**Step 3: Implement RPC handlers**

- `claimSeasonalTask` forwards only a validated slot number.
- Existing single/all chest claims may remain, but eligibility is recomputed server-side using 5/10/15/20.
- Remove `refreshSeasonalTask` and the client `WatchWorldState("season", ...)` reroll path. The server component owns season transitions.

**Step 4: Run tests and commit**

```powershell
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest mods.AchievementLevel.tests.test_seasonal_task_network_ui mods.AchievementLevel.tests.test_seasonal_task_component -v
git add mods/AchievementLevel/modmain.lua mods/AchievementLevel/scripts/system/rpc.lua mods/AchievementLevel/tests/test_seasonal_task_network_ui.py
git commit -m "feat: replicate seasonal task state"
```

## Task 5: Rebuild the seasonal-task UI as a scrollable 20-row list

**Files:**

- Modify: `mods/AchievementLevel/scripts/widgets/uiachievement.lua`
- Modify: `mods/AchievementLevel/main_strings.lua`
- Modify: `mods/AchievementLevel/main_strings_cn.lua`
- Modify: `mods/AchievementLevel/tests/test_seasonal_task_network_ui.py`

**Step 1: Extend failing UI contract tests**

Assert that the widget:

- builds 20 rows through a scroll-list/list-recycler API instead of six fixed-position tiles;
- reads task definitions from `CODE_TO_ID`/`BY_ID` and never indexes legacy `chasni_getseasonaltasklists`;
- displays current progress/target, and `claims/5` for repeat tasks;
- shows a per-row Claim button only in net state `2`;
- disables/closes the row in state `3`;
- sends only `claimSeasonalTask(slot_index)`;
- computes the chest bar from `counted first claims`, not total repeat claims;
- labels the milestone points 5, 10, 15, 20;
- contains no manual reroll or `refreshSeasonalTask` call.

**Step 2: Implement the list**

- Reuse the existing task panel, art, and chest controls.
- Put the 20 task rows inside a scrollable viewport; do not extend the panel beyond the screen.
- Refresh row text/state from net snapshots in `updatetaskpage` without reconstructing the whole screen every frame.
- Use concise status text: active progress, ready to claim, repeat claims `n/5`, and completed.
- Preserve existing hide/show and input behavior outside the task page.

**Step 3: Update strings**

Add matching English and Chinese keys for Claim XP, ready, complete, repeat-claim count, unknown/expired task, and milestone progress. Keep current chest reward descriptions because reward contents are explicitly deferred.

**Step 4: Run tests and commit**

```powershell
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest mods.AchievementLevel.tests.test_seasonal_task_network_ui -v
git add mods/AchievementLevel/scripts/widgets/uiachievement.lua mods/AchievementLevel/main_strings.lua mods/AchievementLevel/main_strings_cn.lua mods/AchievementLevel/tests/test_seasonal_task_network_ui.py
git commit -m "feat: add seasonal task claim list"
```

## Task 6: Full regression, source audit, and in-game checklist

**Files:**

- Create: `mods/AchievementLevel/docs/seasonal-task-ingame-checklist.md`
- Modify only files found defective by the tests/audit above.

**Step 1: Run the complete automated suite**

```powershell
python -m unittest discover -s mods/AchievementLevel/tests -p "test_seasonal_*.py" -v
& C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -m unittest discover -s mods/AchievementLevel/tests -p "test_*.py" -v
```

Expected: all tests pass. If an unrelated pre-existing test cannot run, record its exact command/output and prove it is unrelated; do not silently omit it.

**Step 2: Audit forbidden legacy paths**

```powershell
rg -n "currenttask[1-6]code|chasni_getseasonalcharlist|chasni_getseasonaltasklists|refreshSeasonalTask|for i=1,6|for i = 1, 6" mods/AchievementLevel
rg -n "get_fed_by_another_player|seasonaltasks_other|seasonaltaskcounts_other" mods/AchievementLevel/scripts
```

Expected: no runtime matches. Historical inventory/docs may be explicitly excluded from the command or listed as evidence-only matches.

**Step 3: Create the smoke checklist**

Include these exact checks:

1. New solo world shows 20 tasks with 16 once/4 repeat.
2. Save/reload and cave traversal preserve the same 20 IDs and progress.
3. A ready one-shot grants XP once and closes.
4. A repeat task grants five separate claims, resets progress after claims 1–4, and closes after claim 5.
5. Repeat claims 2–5 do not move the chest bar.
6. Chests become claimable at 5/10/15/20 unique first claims.
7. Leaving ready rewards unclaimed and changing season auto-claims them before the new draw.
8. Same-season UI reopen/reconnect cannot reroll.
9. A migrated old save preserves level, XP, Stars, perks, attribute points, and ordinary achievements.
10. Host plus one client can view/claim without desync or duplicate XP.

**Step 4: Review the diff and commit verification artifacts**

```powershell
git diff --check
git status --short
git add mods/AchievementLevel/docs/seasonal-task-ingame-checklist.md
git commit -m "test: verify seasonal task overhaul"
```

## Subagent execution ledger

Run tasks serially in an isolated worktree. For each numbered task:

1. Generate a task brief containing that task's complete section plus the Scope/invariants and Public interfaces sections.
2. Spawn a fresh implementer subagent with an explicit model and reasoning effort.
3. Require the implementer to follow TDD, run the named commands, commit only scoped files, and report commit SHA/test output.
4. Generate a review package from the resulting commit.
5. Spawn a fresh reviewer subagent. The reviewer checks spec compliance, regressions, test quality, server authority, and unrelated-file contamination.
6. If review finds issues, send them back to the same implementer; rerun tests and review before advancing.
7. After Task 6, run a final whole-branch reviewer against this plan and the design spec.

Do not begin integration into `mods/PhamNhanTuTien` in this branch. That requires a separate integration plan after the standalone system passes the automated suite and the in-game checklist.

## Plan self-review

- **Spec coverage:** Covers catalog counts/uniqueness, 16/4 selection, five repeat claims, first-claim chest progress, 5/10/15/20 rewards, no reroll, auto-claim on transition, save migration, networking, UI, and standalone-only scope.
- **No deferred product decisions:** XP amounts and chest contents remain hooks because the approved spec explicitly defers them; their interfaces and current fallback handlers are concrete.
- **Type consistency:** Saves use string task IDs; network snapshots use numeric catalog codes; slot states use numeric enums; claim indexes are integers 1–5.
- **Review focus:** Highest-risk areas are event-listener cleanup, duplicate RPC idempotency, old-save migration, cave/shard persistence, and client UI reading partially replicated slot data.
- **Isolation warning:** `mods/AchievementLevel` is currently untracked in the main repository. The execution worktree must receive a copied snapshot of that directory before Task 1, and subagents must not touch the dirty `mods/PhamNhanTuTien` tree.
