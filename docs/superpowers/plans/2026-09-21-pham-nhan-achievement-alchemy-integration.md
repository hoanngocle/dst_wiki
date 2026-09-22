# Phàm Nhân Achievement, Alchemy and Seasonal Rewards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the approved 231-achievement, 1,000-Star progression inside Phàm Nhân, including deterministic Đan Lô crafting, a separate 15-stage cultivation track, SS/SSS ranks, fixed seasonal chest rewards, retained perks, integrated UI, and the replacement wiki page.

**Architecture:** Phàm Nhân owns every runtime module; historical Workshop data is evidence only. `hh_leveling` remains the sole Level/EXP authority, while cultivation is a small sequential state machine with no EXP. Catalogs are immutable Lua data, state transitions are server-authoritative, and UI/wiki consume validated exports rather than maintaining independent totals.

**Tech Stack:** Don't Starve Together Lua mod APIs, Python `unittest` validation tools, existing Next.js/Vitest wiki, PowerShell commands on Windows.

**Spec:** `docs/superpowers/specs/2026-09-21-pham-nhan-achievement-star-perks-design.md`

## Global Constraints

- Runtime target is `mods/PhamNhanTuTien`; do not import or require `mods/AchievementLevel` or `mods/2937640068`.
- Preserve existing `ttk_`, `hh_`, prefab, component, RPC and save identifiers unless this plan explicitly introduces a new identifier.
- Fresh save only for the removed Achievement Level system; do not migrate its Level, EXP, attribute points or perks.
- `hh_leveling` is the sole Level/EXP/AP authority. Cultivation contains only stage 0–15 and consumed-pill evidence.
- Exactly 231 achievements are active across 13 groups and sum to exactly 1,000 Star.
- Exactly 39 retained perks cost at most 945 Star; removed perks must not be registered.
- No total EXP multiplier cap. Round once after multiplying all eligible factors.
- Đan Lô has no failure roll, no Phế Đan, and no Thế Tử Phản Hồn Đan.
- Use only first-grade variants of the ten buff-pill families; omit “Nhất Phẩm” from display names.
- Preserve unrelated dirty-worktree changes. Stage and commit only paths listed by the current task.
- Complete and verify `docs/superpowers/plans/2026-09-21-pham-nhan-unified-level-progression.md` and `docs/superpowers/plans/2026-09-21-seasonal-task-redesign.md` before Task 2 or Task 8 consumes their outputs.

## Review Focus

- A forged or replayed RPC must not duplicate Star, perk purchases, seasonal rewards or pill consumption; Tasks 6–8 add replay tests.
- A wrong-order cultivation pill must remain in inventory and leave stage/achievement progress unchanged; Task 3 pins this behavior.
- Closing/reloading the world during a 180-second refining job must resume once and must never duplicate output; Task 5 covers save/load.
- A partially invalid seasonal reward bundle must grant nothing and remain claimable; Task 6 tests transaction preflight.
- SS/SSS must not inherit new bonuses or accidentally unlock S-gated content differently; Task 2 tests rank capabilities separately from display rank.

---

## File Structure

### New runtime modules

- `mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_defs.lua` — immutable furnace, pill, recipe, effect and cultivation-stage data.
- `mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_rules.lua` — pure exact-recipe matching and deterministic job transitions.
- `mods/PhamNhanTuTien/scripts/components/ttk_cultivation.lua` — persisted stage 0–15 and safe pill consumption.
- `mods/PhamNhanTuTien/scripts/components/ttk_alchemy_station.lua` — furnace inventory/job/save lifecycle.
- `mods/PhamNhanTuTien/scripts/prefabs/ttk_alchemy.lua` — `xd_liandanlu` plus allowed pill prefabs.
- `mods/PhamNhanTuTien/main/ttk_alchemy.lua` — assets, strings, container, action, recipe and component registration.
- `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua` — canonical 231 definitions.
- `mods/PhamNhanTuTien/scripts/achievement/ttk_perk_catalog.lua` — canonical 39 retained perks.
- `mods/PhamNhanTuTien/scripts/achievement/ttk_seasonal_catalog.lua` — canonical four 50-task season pools ported from the approved redesign.
- `mods/PhamNhanTuTien/scripts/achievement/ttk_seasonal_rewards.lua` — four fixed 5/10/15/20 reward tables.
- `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua` — pure validation, claim, purchase and seasonal transitions.
- `mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress.lua` — authoritative save state and gameplay adapters.
- `mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress_replica.lua` — compact client snapshot access.
- `mods/PhamNhanTuTien/main/ttk_achievement.lua` — registration, RPC endpoints and event hooks.
- `mods/PhamNhanTuTien/scripts/screens/ttk_progression_screen.lua` — three-tab in-game screen.

### New verification tools

- `mods/PhamNhanTuTien/tools/build_alchemy_defs.py`
- `mods/PhamNhanTuTien/tools/test_alchemy_catalog.py`
- `mods/PhamNhanTuTien/tools/test_alchemy_runtime.py`
- `mods/PhamNhanTuTien/tools/test_cultivation.py`
- `mods/PhamNhanTuTien/tools/test_extended_ranks.py`
- `mods/PhamNhanTuTien/tools/test_seasonal_rewards.py`
- `mods/PhamNhanTuTien/tools/test_achievement_catalog.py`
- `mods/PhamNhanTuTien/tools/test_achievement_state.py`
- `mods/PhamNhanTuTien/tools/test_achievement_trackers.py`
- `mods/PhamNhanTuTien/tools/test_achievement_ui.py`

### Existing integration points

- `mods/PhamNhanTuTien/modmain.lua` — load alchemy and achievement modules; remove stale Achievement-Level comment.
- `mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua` — extend E–S to SS/SSS.
- `mods/PhamNhanTuTien/main/hh_api.lua` and `scripts/progression/hh_progression.lua` — uncapped modifier integration and read-only rank access.
- `mods/PhamNhanTuTien/scripts/containers.lua` or the current container registration module — register the four-slot furnace layout.
- `mods/PhamNhanTuTien/scripts/widgets/hh_status_ui.lua` — open the unified progression screen.
- `mods/AchievementLevel/scripts/constants/seasonaltaskdata.lua` after the approved seasonal plan passes — read-only source for porting the final 4×50 catalogs.
- `app/pham-nhan-tu-tien/tien-trinh/page.tsx`, related data/component/tests and navigation — publish the integrated wiki page.
- Remove the old `app/achievement-level` route only after replacement tests pass.

### Baseline isolation

Each implementer begins with:

```powershell
git status --short
git diff --name-only
git diff --name-only --cached
```

The implementer records pre-existing modifications for every file they will touch. If a listed path is already modified by another active task, stop that task and report the overlap; do not overwrite or reformat the file.

---

### Task 1: Freeze the Alchemy Catalog Generator

**Files:**
- Create: `mods/PhamNhanTuTien/tools/build_alchemy_defs.py`
- Create: `mods/PhamNhanTuTien/tools/test_alchemy_catalog.py`
- Create: `mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_defs.lua`
- Read: `data/manual/tu_tien_item_details.json`
- Read: `app/lib/cultivation-guide.ts`

**Interfaces:**
- Consumes: manual item details under `items["tu_tien:<prefab>"]`.
- Produces: Lua table `{ furnace, cultivation, fasting, buffs, by_prefab }` with exact recipes and effects.

- [ ] **Step 1: Write the failing catalog test**

Assert the generated Lua source contains exactly these cultivation prefabs in order:

```python
CULTIVATION = [
    "xd_danyao_jq", "xd_danyao_dt", "xd_danyao_zj", "xd_danyao_xs",
    "xd_danyao_hj", "xd_danyao_yz", "xd_danyao_sm", "xd_danyao_rl",
    "xd_danyao_jy", "xd_danyao_yx", "xd_danyao_ns", "xd_danyao_hs",
    "xd_danyao_hy", "xd_danyao_hl", "xd_danyao_kx",
]
BUFFS = [
    "xd_dy_cyfxd_1", "xd_dy_dmhsd_1", "xd_dy_lmsqd_1",
    "xd_dy_qxdhd_1", "xd_dy_yfsxd_1", "xd_dy_pshsd_1",
    "xd_dy_qjqsd_1", "xd_dy_xynyd_1", "xd_dy_hsphd_1",
    "xd_dy_xttyd_1",
]
FORBIDDEN = {"xd_dy_fd", "xd_dy_tsfhd"}
```

Also assert `xd_danyao_bg` exists, every allowed pill has 1–4 positive ingredient rows, every ingredient prefab is non-empty, and neither forbidden ID occurs in generated output.

- [ ] **Step 2: Run the test and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_alchemy_catalog.py -v`

Expected: FAIL because generator/output do not exist.

- [ ] **Step 3: Implement deterministic generation**

The generator reads the 26 allowed item records, normalizes `tu_tien:` to runtime prefab IDs, emits stable key order and writes through a temporary sibling followed by `Path.replace`. Hard-code only the approved display-name overrides and stage order; recipe ingredients, quantities and documented effects come from the manual JSON.

Expose these Lua helpers in the generated file:

```lua
function M.Get(prefab) return M.by_prefab[prefab] end
function M.GetCultivationStage(stage) return M.cultivation[stage] end
function M.GetRecipe(prefab) local row=M.Get(prefab); return row and row.recipe or nil end
return M
```

All ten buff display names omit `Nhất Phẩm`. The furnace row is:

```lua
M.furnace = {
    prefab = "xd_liandanlu",
    duration = 180,
    ingredients = {
        { prefab="goldnugget", amount=5 },
        { prefab="cutstone", amount=3 },
        { prefab="flint", amount=3 },
        { prefab="ttk_lingshi1", amount=5 },
    },
}
```

- [ ] **Step 4: Generate and verify stable output**

Run twice:

```powershell
python mods/PhamNhanTuTien/tools/build_alchemy_defs.py
git diff --exit-code -- mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_defs.lua
python mods/PhamNhanTuTien/tools/test_alchemy_catalog.py -v
```

For the first run, inspect and stage the new output before using `git diff --exit-code` on the second run. Expected: second generation has no diff; tests PASS.

- [ ] **Step 5: Commit Task 1 only**

```powershell
git add -- mods/PhamNhanTuTien/tools/build_alchemy_defs.py mods/PhamNhanTuTien/tools/test_alchemy_catalog.py mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_defs.lua
git commit -m "feat: define deterministic Pham Nhan alchemy catalog"
```

### Task 2: Extend Hunter Ranks to SS and SSS

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua`
- Modify only where required: `mods/PhamNhanTuTien/scripts/components/hh_rank.lua`
- Test: `mods/PhamNhanTuTien/tools/test_extended_ranks.py`

**Interfaces:**
- Consumes: canonical player level from `hh_leveling`.
- Produces: `RANK.SS = 7`, `RANK.SSS = 8`, Level requirements 70 and 100.

- [ ] **Step 1: Write rank boundary tests**

```python
EXPECTED = {1:"E", 9:"E", 10:"D", 20:"C", 30:"B", 40:"A",
            50:"S", 69:"S", 70:"SS", 99:"SS", 100:"SSS"}
```

Assert `GetRankForLevel`, `GetName`, `GetNextRank`, and `IsValidRank` agree. Assert all existing capability checks using `rank >= S` behave identically for S, SS and SSS; no separate SS/SSS stat bonus is registered.

- [ ] **Step 2: Run the test and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_extended_ranks.py -v`

Expected: FAIL at missing `SS`.

- [ ] **Step 3: Extend the rank table and iteration bounds**

```lua
M.RANK = { E=1, D=2, C=3, B=4, A=5, S=6, SS=7, SSS=8 }
M.LEVEL_REQUIREMENTS[M.RANK.SS] = 70
M.LEVEL_REQUIREMENTS[M.RANK.SSS] = 100
```

Use `M.RANK.SSS` as the maximum in validation/next-rank loops. Do not add SS/SSS exam definitions, shop rows, EXP factors or combat stats.

- [ ] **Step 4: Run rank and guild regressions**

```powershell
python mods/PhamNhanTuTien/tools/test_extended_ranks.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py -v
python mods/PhamNhanTuTien/tools/test_guild_system.py -v
```

Expected: PASS. `test_unified_progression_dungeon.py` is supplied by the prerequisite unified-progression plan; if it is absent, complete that prerequisite before this task rather than substituting a weaker test.

- [ ] **Step 5: Commit Task 2 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua mods/PhamNhanTuTien/scripts/components/hh_rank.lua mods/PhamNhanTuTien/tools/test_extended_ranks.py
git commit -m "feat: add SS and SSS hunter ranks"
```

### Task 3: Implement the Separate Cultivation State Machine

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/components/ttk_cultivation.lua`
- Create: `mods/PhamNhanTuTien/tools/test_cultivation.py`
- Modify: `mods/PhamNhanTuTien/main/ttk_alchemy.lua`

**Interfaces:**
- Consumes: `AlchemyDefs.GetCultivationStage(stage + 1)`.
- Produces: `CanConsume(prefab) -> boolean, reason`, `Consume(prefab) -> boolean, stage_or_reason`, `GetStage() -> integer`.

- [ ] **Step 1: Write state-machine tests**

Test fresh stage 0, exact first pill, all 15 sequential pills, wrong-order rejection, duplicate rejection, invalid prefab rejection, stage clamping on load, and save/load preservation of the 15-bit consumed set.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_cultivation.py -v`

Expected: FAIL because component is missing.

- [ ] **Step 3: Implement the component**

```lua
function TtkCultivation:CanConsume(prefab)
    local nextrow = Defs.GetCultivationStage(self.stage + 1)
    if nextrow == nil then return false, "max_stage" end
    if nextrow.prefab ~= prefab then return false, "wrong_stage" end
    return true
end

function TtkCultivation:Consume(prefab)
    local ok, reason = self:CanConsume(prefab)
    if not ok then return false, reason end
    self.stage = self.stage + 1
    self.consumed[prefab] = true
    self.inst:PushEvent("ttk_cultivation_advanced", {stage=self.stage, prefab=prefab})
    return true, self.stage
end
```

`OnLoad` clamps stage to 0–15 and reconstructs `consumed` only for the ordered prefix; it never trusts arbitrary saved pill IDs.

- [ ] **Step 4: Run tests**

Run: `python mods/PhamNhanTuTien/tools/test_cultivation.py -v`

Expected: PASS.

- [ ] **Step 5: Commit Task 3 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/components/ttk_cultivation.lua mods/PhamNhanTuTien/main/ttk_alchemy.lua mods/PhamNhanTuTien/tools/test_cultivation.py
git commit -m "feat: add sequential cultivation progression"
```

### Task 4: Implement Allowed Pill Prefabs and Effects

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/prefabs/ttk_alchemy.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_alchemy.lua`
- Test: `mods/PhamNhanTuTien/tools/test_alchemy_runtime.py`

**Interfaces:**
- Consumes: `ttk_alchemy_defs` and player `ttk_cultivation`.
- Produces: 15 cultivation pills, Tịch Cốc Đan and ten buff pills under original `xd_*` prefab IDs.

- [ ] **Step 1: Write prefab/effect tests**

Assert exactly 26 consumable pills register; forbidden prefabs never register. For cultivation pills, only successful `Consume` removes the item. For buffs, verify the first-grade source values: damage +40%, heal 120 then 15/6s, lightning +180, sanity regeneration, speed +25%, damage reduction 35%, work efficiency +90%, cold protection, heat protection and lifesteal 50%, each for 2,400 seconds. Tịch Cốc reduces hunger drain to 20% and reapplies idempotently after load.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_alchemy_runtime.py -v`

Expected: FAIL at missing prefabs.

- [ ] **Step 3: Implement a shared edible factory**

Use one factory for inventory/edible/save behavior and dispatch server-side effects by definition `effect.kind`. Give every pill tag `xd_danyao`; never apply gameplay effects on clients. Timed buffs use named external multipliers keyed by prefab so consuming the same pill refreshes duration instead of stacking another copy.

- [ ] **Step 4: Run runtime and existing combat tests**

```powershell
python mods/PhamNhanTuTien/tools/test_alchemy_runtime.py -v
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
```

Expected: PASS with no duplicate multiplier keys.

- [ ] **Step 5: Commit Task 4 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/prefabs/ttk_alchemy.lua mods/PhamNhanTuTien/main/ttk_alchemy.lua mods/PhamNhanTuTien/tools/test_alchemy_runtime.py
git commit -m "feat: port approved cultivation and buff pills"
```

### Task 5: Implement Deterministic Đan Lô Jobs

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_rules.lua`
- Create: `mods/PhamNhanTuTien/scripts/components/ttk_alchemy_station.lua`
- Modify: `mods/PhamNhanTuTien/scripts/prefabs/ttk_alchemy.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_alchemy.lua`
- Extend test: `mods/PhamNhanTuTien/tools/test_alchemy_runtime.py`

**Interfaces:**
- Consumes: four-slot container inventory and `AlchemyDefs.GetRecipe`.
- Produces: `FindExactRecipe(items)`, `Start(doer)`, `Finish()`, persisted `{output, remaining}` job.

- [ ] **Step 1: Add failing furnace tests**

Cover exact ingredients, missing quantity, extra quantity, unknown ingredient, busy furnace, hammer while busy, 179/180-second boundary, output delivery, full output slot fallback to ground, save/load at 90 seconds, and duplicate callback protection. Assert every valid job succeeds and no RNG function or failure prefab is referenced.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_alchemy_runtime.py -v`

Expected: FAIL at missing station component.

- [ ] **Step 3: Implement exact matching and transaction start**

`FindExactRecipe` compares a normalized `{prefab -> total stack size}` map with each recipe. `Start` preflights a recipe, consumes the exact quantities once, closes/locks the container, stores output and end time, then schedules `Finish`. There is no random branch.

- [ ] **Step 4: Implement save/load and destruction safety**

Persist the output prefab and remaining seconds. `OnLoad` schedules one task. `Finish` clears job state before spawning output. Hammering a busy furnace returns the locked ingredients only when start never committed; after committed start it first completes/cancels according to one tested path, never both.

- [ ] **Step 5: Register building/action/assets and verify**

Register `xd_liandanlu`, its placer, four-slot UI, original animation assets already present in the mod, the approved building recipe and one server-validated “Luyện Đan” action.

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_alchemy_runtime.py -v
python mods/PhamNhanTuTien/tools/audit_registration.py
```

Expected: PASS; audit reports the furnace and exactly 26 pill prefabs.

- [ ] **Step 6: Commit Task 5 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_rules.lua mods/PhamNhanTuTien/scripts/components/ttk_alchemy_station.lua mods/PhamNhanTuTien/scripts/prefabs/ttk_alchemy.lua mods/PhamNhanTuTien/main/ttk_alchemy.lua mods/PhamNhanTuTien/tools/test_alchemy_runtime.py
git commit -m "feat: add deterministic Dan Lo refining"
```

### Task 6: Add SS/SSS and the Exact 231-Achievement Catalog

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua`
- Create: `mods/PhamNhanTuTien/tools/test_achievement_catalog.py`

**Interfaces:**
- Produces: `All()`, `ById(id)`, `ByEvent(event)`, `Validate()`.

- [ ] **Step 1: Write structural validator tests**

Assert 231 active, 0 future, 13 group totals `10/40/33/11/20/15/14/33/13/12/12/8/10`, unique IDs/signatures, reward counts `71/57/55/34/14` for values `2/3/5/8/10`, and total 1,000.

Assert the exact 19 food IDs from spec section 5.5, `craft_alchemy_furnace`, rank SS at Level 70, rank SSS at Level 100, and all explicitly removed achievements are absent.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_achievement_catalog.py -v`

Expected: FAIL because catalog is missing.

- [ ] **Step 3: Encode the approved catalog and indexes**

Every entry has `id`, `group`, `name`, `description`, `tracker`, `target`, `reward`, `status="active"`, `visibility="visible"`, and immutable `params`. Build indexes once at module load and throw on duplicate IDs/signatures.

- [ ] **Step 4: Run validator**

Run: `python mods/PhamNhanTuTien/tools/test_achievement_catalog.py -v`

Expected: PASS with printed totals 231 and 1,000.

- [ ] **Step 5: Commit Task 6 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua mods/PhamNhanTuTien/tools/test_achievement_catalog.py
git commit -m "feat: add approved 231 achievement catalog"
```

### Task 7: Implement Achievement/Star/Perk State Transactions

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/achievement/ttk_perk_catalog.lua`
- Create: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua`
- Create: `mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress.lua`
- Create: `mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress_replica.lua`
- Test: `mods/PhamNhanTuTien/tools/test_achievement_state.py`

**Interfaces:**
- Produces: `Advance(id, amount, evidence)`, `ClaimAchievement(id, request_id)`, `PurchasePerk(id, request_id)`, `GetSnapshot()`.

- [ ] **Step 1: Write transaction and corruption tests**

Cover locked/completed/claimed transitions, replayed request IDs, double-click claim, Star earned/spent invariant, insufficient balance, max level 25 price bands 2/3/4/5, one-time perks, effect-application rollback, NaN/negative load data, unknown IDs and idempotent respawn reapply.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_achievement_state.py -v`

Expected: FAIL because core/component are missing.

- [ ] **Step 3: Implement the pure core and canonical perk catalog**

The seven repeatable perks each cost 80 Star over 25 levels. Encode the retained 14 ability and 18 craft unlock rows from spec; sum maximum cost to 945. `ClaimAchievement` writes `claimed_reward` before returning success. `PurchasePerk` validates and applies before incrementing spent; on apply failure it restores the previous snapshot.

- [ ] **Step 4: Implement component save/replica snapshot**

Persist versioned achievements, earned/spent, perks, cultivation reference and seasonal state. Replica sends compact serialized snapshots on open/dirty events rather than one netvar per achievement.

- [ ] **Step 5: Run state tests**

Run: `python mods/PhamNhanTuTien/tools/test_achievement_state.py -v`

Expected: PASS; full completion/full purchase leaves 55 Star.

- [ ] **Step 6: Commit Task 7 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/achievement/ttk_perk_catalog.lua mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress.lua mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress_replica.lua mods/PhamNhanTuTien/tools/test_achievement_state.py
git commit -m "feat: add authoritative achievement and perk state"
```

### Task 8: Finalize Seasonal Chest Reward Transactions

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/achievement/ttk_seasonal_catalog.lua`
- Create: `mods/PhamNhanTuTien/scripts/achievement/ttk_seasonal_rewards.lua`
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress.lua`
- Test: `mods/PhamNhanTuTien/tools/test_seasonal_rewards.py`

**Interfaces:**
- Produces: `GetBundle(season, milestone)`, `ClaimChest(player, milestone, request_id)`.

- [ ] **Step 1: Write exact bundle tests**

First assert the ported pools contain exactly 4 seasons × (40 once + 10 repeat), 200 unique IDs/signatures and no character/other pool. Then encode and assert the reward table: spring `lmg/yellowgem/goose_feather`, summer `cyh/orangegem/dragon_scales`, autumn `qfx/greengem/bearger_fur`, winter `hsc/bluegem/deerclops_eyeball`, with 3 seeds; 5 seeds + 10 low stones; 2 medium stones + gem; 1 high stone + boss material.

Also test milestone 5/10/15/20 distinct tasks, repeated-task claims not incrementing chest count, replay, wrong season, missing prefab preflight, full inventory fallback and reload.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_seasonal_rewards.py -v`

Expected: FAIL because bundle definitions are missing.

- [ ] **Step 3: Implement all-or-nothing claim**

Port the already-reviewed 200 definitions from `mods/AchievementLevel/scripts/constants/seasonaltaskdata.lua` into `ttk_seasonal_catalog.lua` without changing IDs, events, targets or seasonal ownership. Preflight every reward prefab and amount, reserve the claim request, create every item stack, deliver to inventory or a deterministic ground position, then set `chest_claimed[index]`. If creation fails before delivery, remove staged items and clear the reservation.

- [ ] **Step 4: Run seasonal suites**

```powershell
python mods/PhamNhanTuTien/tools/test_seasonal_rewards.py -v
python mods/PhamNhanTuTien/tools/test_seasonal_task_catalog.py -v
python mods/PhamNhanTuTien/tools/test_seasonal_task_state.py -v
```

Expected: PASS. The two prerequisite tests are created by the approved seasonal redesign plan; complete that plan first if either file is absent.

- [ ] **Step 5: Commit Task 8 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/achievement/ttk_seasonal_catalog.lua mods/PhamNhanTuTien/scripts/achievement/ttk_seasonal_rewards.lua mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua mods/PhamNhanTuTien/scripts/components/ttk_achievement_progress.lua mods/PhamNhanTuTien/tools/test_seasonal_rewards.py
git commit -m "feat: add fixed seasonal chest rewards"
```

### Task 9: Wire Gameplay Trackers and RPCs

**Files:**
- Create: `mods/PhamNhanTuTien/main/ttk_achievement.lua`
- Create: `mods/PhamNhanTuTien/tools/test_achievement_trackers.py`
- Modify: `mods/PhamNhanTuTien/modmain.lua`

**Interfaces:**
- Consumes: catalog event indexes and authoritative component methods.
- Produces: server RPCs for claim, purchase, seasonal claim and snapshot request.

- [ ] **Step 1: Write tracker/RPC tests**

Test cultivation-event credit, each first-grade buff consumption, Tịch Cốc, Phúc Lạc three-item bitset, six boss-food prefabs, Đan Lô construction, SS/SSS level events, duplicate death/eat callbacks, pet ownership and forged reward/price payloads.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_achievement_trackers.py -v`

Expected: FAIL because hooks/RPCs are missing.

- [ ] **Step 3: Install indexed server event adapters**

One listener per event type looks up candidate IDs via `Catalog.ByEvent(event)`. It sends only ID/progress evidence to the component; reward and target always come from catalog. Register the new modules after core Phàm Nhân systems and before client widgets.

- [ ] **Step 4: Add strict RPC payload validation**

Accept only scalar stable IDs, slot indexes and opaque request IDs with bounded length. Resolve the player from RPC sender. Reject client-supplied reward, price, level, target or progress fields.

- [ ] **Step 5: Run tracker and bootstrap tests**

```powershell
python mods/PhamNhanTuTien/tools/test_achievement_trackers.py -v
lua mods/PhamNhanTuTien/tools/solo_integration_smoke.lua
```

Expected: PASS and one registration of each event/RPC.

- [ ] **Step 6: Commit Task 9 only**

```powershell
git add -- mods/PhamNhanTuTien/main/ttk_achievement.lua mods/PhamNhanTuTien/modmain.lua mods/PhamNhanTuTien/tools/test_achievement_trackers.py
git commit -m "feat: connect Pham Nhan achievement trackers"
```

### Task 10: Apply Perks and Remove the EXP Multiplier Cap

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/progression/hh_progression.lua`
- Modify: `mods/PhamNhanTuTien/main/hh_tunning.lua`
- Modify only approved integration files for combat/recipes named by the spec.
- Extend: `mods/PhamNhanTuTien/tools/test_unified_progression_core.py`
- Extend: `mods/PhamNhanTuTien/tools/test_achievement_state.py`

**Interfaces:**
- Consumes: perk levels/unlocks from `ttk_achievement_progress`.
- Produces: idempotent stat effects and `1 + 0.05 * xp_perk_level` in the canonical EXP award path.

- [ ] **Step 1: Update failing progression expectations**

For base 100 with rank 1.25, player 1.25 and dungeon 1.35, assert 211 after one final rounding. With XP perk 25, assert 475 (`100 * 1.25 * 1.25 * 1.35 * 2.25 = 474.609375`). Assert daily quest fixed rewards bypass these modifiers.

- [ ] **Step 2: Run and verify failure**

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_achievement_state.py -v
```

Expected: FAIL at the former 1.75 cap/missing perk provider.

- [ ] **Step 3: Remove the total clamp and apply the perk last**

Multiply eligible factors, then `xp_perk = 1 + 0.05 * level`, then round once. Delete `MAX_BONUS_MULTIPLIER` and every `math.min(...1.75...)` in the canonical award path; do not delete ordinary-mob overlevel reduction.

- [ ] **Step 4: Implement retained perk effects idempotently**

Use named external modifier keys for planar defense/damage, crit rate/damage, lifesteal and scale. Craft unlocks expose recipes to EVA immediately after purchase and after load. Do not register any perk listed as removed in spec section 7.

- [ ] **Step 5: Run progression/combat/perk suites**

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
python mods/PhamNhanTuTien/tools/test_achievement_state.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit Task 10 only**

Stage only files shown by `git diff --name-only` for this task and commit:

```powershell
git commit -m "feat: apply achievement perks without EXP cap"
```

### Task 11: Build the Three-Tab Progression UI

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/screens/ttk_progression_screen.lua`
- Modify: `mods/PhamNhanTuTien/scripts/widgets/hh_status_ui.lua`
- Test: `mods/PhamNhanTuTien/tools/test_achievement_ui.py`

**Interfaces:**
- Consumes: replica snapshot and strict RPCs.
- Produces: Achievement, Seasonal Task and Perk tabs with Claim/Purchase controls.

- [ ] **Step 1: Write static/UI harness tests**

Assert 13 group filters, 231 count, Star header, claimed/unclaimed button states, 20 seasonal rows, four chest buttons, repeat count 0–5, three perk groups, next-level price, max-level state, and absence of a Level tab.

- [ ] **Step 2: Run and verify failure**

Run: `python mods/PhamNhanTuTien/tools/test_achievement_ui.py -v`

Expected: FAIL because screen is missing.

- [ ] **Step 3: Implement snapshot-driven UI**

The client never predicts rewards. Disable a button immediately while its request ID is pending, then refresh only from the next server snapshot. Paginate or virtualize achievement rows; do not instantiate 231 heavy row widgets simultaneously.

- [ ] **Step 4: Run UI and dedicated-server guards**

```powershell
python mods/PhamNhanTuTien/tools/test_achievement_ui.py -v
python mods/PhamNhanTuTien/tools/test_unified_ui.py -v
```

Expected: PASS; server bootstrap never requires screen/widget modules.

- [ ] **Step 5: Commit Task 11 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/screens/ttk_progression_screen.lua mods/PhamNhanTuTien/scripts/widgets/hh_status_ui.lua mods/PhamNhanTuTien/tools/test_achievement_ui.py
git commit -m "feat: add integrated progression screen"
```

### Task 12: Replace the Standalone Wiki Route

**Files:**
- Create: `app/pham-nhan-tu-tien/tien-trinh/page.tsx`
- Create: `app/components/pham-nhan-progression.tsx`
- Create: `app/components/pham-nhan-progression.test.tsx`
- Create: `tools/export_pham_nhan_progression.py`
- Create: `data/generated/pham-nhan-progression.json`
- Modify: Phàm Nhân navigation registry containing `PhamNhanNav`
- Delete after tests pass: `app/achievement-level/**`
- Remove obsolete manual route data only after reverse-reference audit.

**Interfaces:**
- Consumes: exported canonical Lua catalogs.
- Produces: `/pham-nhan-tu-tien/tien-trinh`; removes `/achievement-level`.

- [ ] **Step 1: Write route/data tests**

Assert 231 achievements, 13 groups, 1,000 Star, 39 perks/945 cost, 4×50/20 seasonal model, exact seasonal bundles, 15 cultivation pills, ten buff pills, SS/SSS at 70/100, and no standalone route/nav link.

- [ ] **Step 2: Run and verify failure**

Run: `npm test -- --run app/components/pham-nhan-progression.test.tsx`

Expected: FAIL because page/export are missing.

- [ ] **Step 3: Implement deterministic export and page**

Export IDs, display copy, counts, reward values and alchemy/rank tables from canonical data. The page uses `PhamNhanNav`, labels the mod “Phàm Nhân Tu Tiên”, and explains that cultivation is separate from `hh_leveling` rather than presenting a second Level bar.

- [ ] **Step 4: Remove the old route only after replacement passes**

Run reverse-reference search:

```powershell
rg -n '/achievement-level|achievement-level' app tests tools data docs
```

Update intentional links/tests, delete the route, then rerun the focused test.

- [ ] **Step 5: Run wiki verification**

```powershell
npm test -- --run app/components/pham-nhan-progression.test.tsx
npm test -- --run
npm run build
```

Expected: all tests and build PASS.

- [ ] **Step 6: Commit Task 12 only**

Stage the exact page/component/export/data/navigation/deleted-route paths and commit:

```powershell
git commit -m "feat: move achievement progression into Pham Nhan wiki"
```

### Task 13: Full Verification, CodeGraph and Whole-Branch Review

**Files:**
- Modify only failing files proven to belong to Tasks 1–12.
- Update: `.codegraph/` using the repository-supported indexing command after all code is final.

**Interfaces:**
- Consumes: every task deliverable.
- Produces: verified integration ready for user playtest.

- [ ] **Step 1: Run all new Python suites**

```powershell
python mods/PhamNhanTuTien/tools/test_alchemy_catalog.py -v
python mods/PhamNhanTuTien/tools/test_cultivation.py -v
python mods/PhamNhanTuTien/tools/test_alchemy_runtime.py -v
python mods/PhamNhanTuTien/tools/test_extended_ranks.py -v
python mods/PhamNhanTuTien/tools/test_achievement_catalog.py -v
python mods/PhamNhanTuTien/tools/test_achievement_state.py -v
python mods/PhamNhanTuTien/tools/test_seasonal_rewards.py -v
python mods/PhamNhanTuTien/tools/test_achievement_trackers.py -v
python mods/PhamNhanTuTien/tools/test_achievement_ui.py -v
```

- [ ] **Step 2: Run affected Phàm Nhân regressions**

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py -v
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
python mods/PhamNhanTuTien/tools/test_unified_ui.py -v
python mods/PhamNhanTuTien/tools/audit_registration.py
```

- [ ] **Step 3: Run wiki tests/build**

```powershell
npm test -- --run
npm run build
```

- [ ] **Step 4: Run forbidden-content and invariant searches**

```powershell
rg -n 'xd_dy_fd|xd_dy_tsfhd|MAX_BONUS_MULTIPLIER|1\.75|/achievement-level' mods/PhamNhanTuTien app
rg -n 'status\s*=\s*"future"|visibility\s*=\s*"hidden"' mods/PhamNhanTuTien/scripts/achievement
```

Expected: no runtime references except explicit negative tests/documentation fixtures.

- [ ] **Step 5: Refresh CodeGraph and inspect final diff**

Run the repository-supported CodeGraph update command, then:

```powershell
git diff --check
git status --short
git log --oneline -15
```

- [ ] **Step 6: Request fresh whole-branch review**

Reviewer checks spec coverage, dirty-worktree preservation, server authority, save compatibility, duplicate rewards, deterministic furnace behavior and absence of removed content. Fix only confirmed issues and rerun the smallest affected suite plus the final invariant searches.

- [ ] **Step 7: Commit final verification fixes**

```powershell
git commit -m "test: verify Pham Nhan achievement integration"
```

Skip the commit only when there are no verification changes; record the final tested commit SHA either way.
