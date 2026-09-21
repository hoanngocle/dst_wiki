# Phàm Nhân Unified Level Progression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one balanced solo level progression for Phàm Nhân, fed by survival, production, combat, daily quests, bosses, and dungeons, while leaving a stable seam for a later Achievement merge that never creates a second level track.

**Architecture:** `scripts/progression/hh_progression.lua` becomes the stable public boundary for reading level state and awarding EXP; `hh_leveling` remains the sole state owner. Thin source adapters translate authoritative DST events into calls to this boundary, while combat attribution, modifiers, daily scaling, and duplicate protection stay centralized and testable.

**Tech Stack:** Don't Starve Together Lua 5.1 mod APIs, Python 3 `unittest`, `lupa.lua51`, CodeGraph CLI.

**Spec:** `docs/superpowers/specs/2026-09-21-pham-nhan-unified-level-progression-design.md`

## Global Constraints

- Work only in `mods/PhamNhanTuTien`, its tests/tools, and the associated repository documentation.
- Do not edit, import, or partially merge `mods/AchievementLevel` or historical source mod `mods/2937640068`.
- Achievement is not merged now; the future merge must call the stable Phàm Nhân progression API and must not attach `levelsystem`.
- Achievement and Star completion handlers never award EXP.
- `hh_leveling` is the sole owner of level, EXP, AP, stats, network state, and save state.
- Fresh-save acceptance starts at level 1, EXP 0, AP 0; no Achievement save migration is implemented.
- Level 100 is a tuning milestone, not a hard cap.
- Solo attribution only: direct player kills and player-owned shadow/follower kills give 100% to one owner; no nearby scan and no division.
- No daily EXP cap and no diminishing returns for valid repeated actions.
- No character-specific EXP bonuses.
- Preserve existing AP/stat/level-up restoration behavior.
- The working tree contains unrelated user/task changes. Re-read every target file and its diff immediately before editing; never use `git add -A`, broad checkout, reset, or cleanup commands.
- Every implementation commit stages only the files named in that task.

## Review Focus

- Non-finite EXP (`NaN`, `math.huge`, `-math.huge`), zero, negative, or unknown source names must return a reason and never mutate level state; Task 2 pins this.
- Cyclic or stale ownership chains must terminate without credit, while a valid owned shadow still credits exactly one living owner; Task 3 pins this.
- Repeated death, recipe-learning, cooking-harvest, repair, or tending callbacks must not double-award; Tasks 3, 4, and 5 pin this.
- Recipes with no positive item or character ingredient cost must award zero, without blocking legitimate recipes whose only cost is a positive character ingredient; Task 4 pins this.
- Invalid wave counts, absent rank components, and ranks below the gate requirement must fail closed without changing existing cooldown/authority checks; Task 7 pins this.

---

## File Structure

### New files

- `mods/PhamNhanTuTien/scripts/progression/hh_progression.lua` — stable level/EXP API, curve, reward scaling, modifiers, combat metadata, and solo kill attribution.
- `mods/PhamNhanTuTien/scripts/components/hh_exp_tracker.lua` — per-player authoritative activity listeners and persisted first-learn duplicate state.
- `mods/PhamNhanTuTien/main/hh_exp_events.lua` — component post-inits for cooking, repair, and plant tending.
- `mods/PhamNhanTuTien/docs/achievement-merge-progression-contract.md` — exact future Achievement integration contract and public calls.
- `mods/PhamNhanTuTien/tools/test_unified_progression_core.py` — curve, API, modifier, and invalid-input regression tests.
- `mods/PhamNhanTuTien/tools/test_unified_progression_combat.py` — solo attribution, duplicate death, tier, boss, and overlevel regression tests.
- `mods/PhamNhanTuTien/tools/test_unified_progression_activities.py` — gameplay-event and anti-exploit regression tests.
- `mods/PhamNhanTuTien/tools/test_unified_progression_quests.py` — difficulty scaling and one-shot completion regression tests.
- `mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py` — shared rank mapping and entry validation regression tests.
- `mods/PhamNhanTuTien/tools/simulate_unified_progression.py` — deterministic old/new/Achievement curve and pacing report.

### Existing files modified

- `mods/PhamNhanTuTien/scripts/components/hh_leveling.lua` — delegate curve mathematics to the public progression module.
- `mods/PhamNhanTuTien/scripts/components/hh_dungeon_effects.lua` — expose separate player/dungeon EXP factors for centralized capping.
- `mods/PhamNhanTuTien/main/hh_tunning.lua` — activity values, modifier cap, Rank S value, combat tiers, and boss rewards.
- `mods/PhamNhanTuTien/main/hh_api.lua` — attach the tracker and replace local shared-kill logic with the progression API.
- `mods/PhamNhanTuTien/main/ttk_solo_source.lua` — load the activity hook module after tuning/API initialization.
- `mods/PhamNhanTuTien/scripts/components/hh_daily_quest.lua` — compute difficulty-scaled rewards and award through the central API.
- `mods/PhamNhanTuTien/scripts/quests/hh_daily_quest_defs.lua` — retain difficulty and remove fixed reward authority.
- `mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua` — own the wave-to-rank mapping used by display and validation.
- `mods/PhamNhanTuTien/scripts/prefabs/dungeon_gate.lua` — display rank from the shared mapping.
- `mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua` — enforce the displayed rank before entry.
- `mods/PhamNhanTuTien/modmain.lua` — correct the stale comment that currently attributes progression to Achievement.

---

### Task 1: Canonical Curve and Future Achievement Boundary

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/progression/hh_progression.lua`
- Create: `mods/PhamNhanTuTien/docs/achievement-merge-progression-contract.md`
- Create: `mods/PhamNhanTuTien/tools/test_unified_progression_core.py`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_leveling.lua:1-70`
- Modify: `mods/PhamNhanTuTien/modmain.lua:141-148`

**Interfaces:**
- Consumes: `player.components.hh_leveling.level`, `HHLeveling:AddExp(amount)`.
- Produces: `Progression.GetExpGoal(level) -> integer`, `Progression.GetLevel(player) -> integer|nil`, `Progression.GetExpGoalForPlayer(player) -> integer|nil`.

- [ ] **Step 1: Write failing curve and compatibility tests**

Create `tools/test_unified_progression_core.py` with the same `LuaRuntime`, `Class`, `NewInst`, `TUNING`, and `HHUtils` stubs used by `tools/test_solo_progression.py`, then add these exact assertions:

```python
class UnifiedProgressionCoreTests(unittest.TestCase):
    def test_curve_and_cumulative_milestones(self):
        lua = progression_runtime()
        values = lua.eval(
            "function() local p=require('progression/hh_progression'); "
            "local total=0; local marks={}; "
            "for level=1,99 do total=total+p.GetExpGoal(level); "
            "if level==9 or level==19 or level==49 or level==99 then "
            "marks[level+1]=total end end; return marks,total end"
        )()
        marks, total = values
        self.assertEqual(marks[10], 1568)
        self.assertEqual(marks[20], 6778)
        self.assertEqual(marks[50], 73708)
        self.assertEqual(total, 536258)

    def test_public_bridge_reads_only_hh_leveling(self):
        lua = progression_runtime()
        level, goal = lua.eval(
            "function() local p=require('progression/hh_progression'); "
            "local player=NewInst(); player.components.hh_leveling={level=37}; "
            "return p.GetLevel(player),p.GetExpGoalForPlayer(player) end"
        )()
        self.assertEqual(level, 37)
        self.assertEqual(goal, 2404)

    def test_fresh_component_starts_at_level_one_exp_zero_ap_zero(self):
        lua = progression_runtime()
        state = lua.eval(
            "function() local inst=NewInst(); local c=HHLeveling(inst); "
            "return c.level,c.exp,c.ap end"
        )()
        self.assertEqual(state, (1, 0, 0))

    def test_multi_level_award_preserves_remainder_and_existing_ap_rules(self):
        lua = progression_runtime()
        state = lua.eval(
            "function() local inst=NewInst(); local c=HHLeveling(inst); "
            "inst.components.hh_leveling=c; c:AddExp(500); "
            "return c.level,c.exp,c.ap end"
        )()
        self.assertEqual(state, (5, 18, 8))
```

- [ ] **Step 2: Run the tests and verify the missing module failure**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
```

Expected: FAIL because `progression/hh_progression.lua` does not exist.

- [ ] **Step 3: Implement the pure curve and read-only bridge**

Create `scripts/progression/hh_progression.lua` with this initial public surface:

```lua
local M = {}

local function FiniteNumber(value)
    value = tonumber(value)
    if value == nil or value ~= value or value == math.huge or value == -math.huge then
        return nil
    end
    return value
end

function M.GetExpGoal(level)
    level = math.max(1, FiniteNumber(level) or 1)
    local n = level - 1
    return math.floor(100 + 10 * n + 1.5 * n * n + 0.5)
end

function M.GetLevel(player)
    local leveling = player ~= nil and player.components ~= nil
        and player.components.hh_leveling or nil
    return leveling ~= nil and math.max(1, math.floor(FiniteNumber(leveling.level) or 1)) or nil
end

function M.GetExpGoalForPlayer(player)
    local level = M.GetLevel(player)
    return level ~= nil and M.GetExpGoal(level) or nil
end

return M
```

In `hh_leveling.lua`, require the module and replace local formula ownership:

```lua
local Progression = require("progression/hh_progression")

function HHLeveling:GetExpGoal(level)
    return Progression.GetExpGoal(level)
end
```

- [ ] **Step 4: Add the future Achievement integration contract**

Create `docs/achievement-merge-progression-contract.md` with these enforceable rules:

```markdown
# Achievement Merge — Progression Contract

Achievement is not part of the current Phàm Nhân runtime. Keep it absent until
the dedicated merge task is approved.

When it is merged:

1. Never add `levelsystem`, its netvars, HUD, save fields, or attribute points.
2. Read player level only with `require("progression/hh_progression").GetLevel(player)`.
3. Gameplay adapters may call `Progression.Award(player, source, base, context)`.
4. Combat adapters call `Progression.AwardKill(attacker, victim)`.
5. Achievement/Star completion never calls either award function.
6. Do not conditionally require the standalone Achievement mod from Phàm Nhân.

Allowed award sources are `activity`, `first_learn`, `combat`, `boss`,
`dungeon`, and `daily_quest`. There is deliberately no `achievement` source.
```

Change the `modmain.lua` comment to:

```lua
-- EVA uses Phàm Nhân's canonical hh_leveling progression. A later Achievement
-- merge must use progression/hh_progression and must not add a second level component.
modimport("main/ttk_eva.lua")
```

- [ ] **Step 5: Run the core tests**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
```

Expected: all Task 1 tests PASS.

- [ ] **Step 6: Commit Task 1 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/progression/hh_progression.lua mods/PhamNhanTuTien/scripts/components/hh_leveling.lua mods/PhamNhanTuTien/docs/achievement-merge-progression-contract.md mods/PhamNhanTuTien/tools/test_unified_progression_core.py mods/PhamNhanTuTien/modmain.lua
git commit -m "feat: establish canonical Pham Nhan progression API"
```

---

### Task 2: Central Award Pipeline and Modifier Cap

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/progression/hh_progression.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_dungeon_effects.lua:233-245`
- Modify: `mods/PhamNhanTuTien/main/hh_tunning.lua:603-625,766-778`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_progression_core.py`

**Interfaces:**
- Consumes: `Progression.GetExpGoal`, `player.components.hh_leveling:AddExp`, `player.components.hh_rank:GetRank`, `player.components.hh_dungeon_effects:GetExpFactors`.
- Produces: `Progression.Award(player, source, base_amount, context) -> boolean, integer|string`, `Progression.GetDailyQuestReward(player, difficulty) -> integer|nil`, `HHDungeonEffects:GetExpFactors(is_dungeon) -> number, number`.

- [ ] **Step 1: Add failing invalid-input, scaling, modifier, and sealed-award tests**

Append tests that construct a living player with stub `hh_leveling`, `hh_rank`, and `hh_dungeon_effects` components:

```python
def test_award_rejects_invalid_and_achievement_sources(self):
    lua = progression_runtime()
    result = lua.eval(
        "function() local p=require('progression/hh_progression'); local x=NewAwardPlayer(); "
        "local a,ar=p.Award(x,'activity',0); "
        "local b,br=p.Award(x,'activity',math.huge); "
        "local c,cr=p.Award(x,'achievement',100); "
        "return a,ar,b,br,c,cr,x.components.hh_leveling.received end"
    )()
    self.assertEqual(result, (False, "invalid_amount", False, "invalid_amount",
                              False, "invalid_source", 0))

def test_daily_rewards_scale_from_current_goal_without_modifiers(self):
    lua = progression_runtime()
    rewards = lua.eval(
        "function() local p=require('progression/hh_progression'); "
        "local x=NewAwardPlayer(); x.components.hh_leveling.level=1; "
        "local e=p.GetDailyQuestReward(x,'easy'); "
        "x.components.hh_leveling.level=50; "
        "return e,p.GetDailyQuestReward(x,'medium'),p.GetDailyQuestReward(x,'hard') end"
    )()
    self.assertEqual(rewards, (20, 419, 629))

def test_combined_bonus_is_capped_at_one_point_seven_five(self):
    lua = progression_runtime()
    ok, amount = lua.eval(
        "function() local p=require('progression/hh_progression'); local x=NewAwardPlayer(); "
        "x.components.hh_rank.rank=6; "
        "x.components.hh_dungeon_effects.player=1.25; "
        "x.components.hh_dungeon_effects.dungeon=1.35; "
        "return p.Award(x,'dungeon',100,{is_combat=true,is_dungeon=true}) end"
    )()
    self.assertTrue(ok)
    self.assertEqual(amount, 175)
```

Also test that `AddExp` returning `false, "sealed"` propagates the failure and does not report an awarded amount.

- [ ] **Step 2: Run only the new tests and verify failure**

Run:

```powershell
python -m unittest -v mods.PhamNhanTuTien.tools.test_unified_progression_core
```

Expected: FAIL because `Award`, `GetDailyQuestReward`, and `GetExpFactors` do not exist.

- [ ] **Step 3: Add exact tuning constants**

Extend `TUNING.HH_EXP_BALANCE` and `TUNING.HH_DAILY_QUEST`:

```lua
TUNING.HH_EXP_BALANCE = {
    MAX_BONUS_MULTIPLIER = 1.75,
    LEVEL_FACTORS = {
        { gap = 40, factor = 0.10 },
        { gap = 30, factor = 0.25 },
        { gap = 20, factor = 0.50 },
        { gap = 10, factor = 0.75 },
    },
}

TUNING.HH_SUPER_GROWTH.KILL_EXP_MULT = 1.25

TUNING.HH_DAILY_QUEST.REWARD_BY_DIFFICULTY = {
    easy = { ratio = 0.06, minimum = 20 },
    medium = { ratio = 0.10, minimum = 35 },
    hard = { ratio = 0.15, minimum = 50 },
}
```

Delete `SHARE_RADIUS`; no replacement is allowed.

- [ ] **Step 4: Expose independent EXP factors**

Replace `GetExpMultiplier` ownership in `hh_dungeon_effects.lua` with:

```lua
function HHDungeonEffects:GetExpFactors(is_dungeon)
    local player_factor = self:IsActive("player_exp") and 1.25 or 1
    local dungeon_factor = is_dungeon and self:IsActive("player_dungeon_exp") and 1.35 or 1
    return player_factor, dungeon_factor
end

function HHDungeonEffects:GetExpMultiplier(is_dungeon)
    local player_factor, dungeon_factor = self:GetExpFactors(is_dungeon)
    return math.min(TUNING.HH_EXP_BALANCE.MAX_BONUS_MULTIPLIER or 1.75,
        player_factor * dungeon_factor)
end
```

The wrapper preserves callers outside the new progression module.

- [ ] **Step 5: Implement the central award functions**

Add to `hh_progression.lua`:

```lua
local RankDefs = require("guild/hh_rank_defs")

local ALLOWED_SOURCES = {
    activity = true, first_learn = true, combat = true,
    boss = true, dungeon = true, daily_quest = true,
}

local function EligiblePlayer(player)
    local health = player ~= nil and player.components ~= nil and player.components.health or nil
    return player ~= nil and player.IsValid ~= nil and player:IsValid()
        and player.HasTag ~= nil and not player:HasTag("playerghost")
        and health ~= nil and not health:IsDead()
        and player.components.hh_leveling ~= nil
end

function M.GetDailyQuestReward(player, difficulty)
    local row = TUNING.HH_DAILY_QUEST.REWARD_BY_DIFFICULTY[difficulty]
    local goal = M.GetExpGoalForPlayer(player)
    if row == nil or goal == nil then return nil end
    return math.max(row.minimum, math.floor(goal * row.ratio + 0.5))
end

function M.Award(player, source, base_amount, context)
    if not ALLOWED_SOURCES[source] then return false, "invalid_source" end
    base_amount = FiniteNumber(base_amount)
    if base_amount == nil or base_amount <= 0 then return false, "invalid_amount" end
    if not EligiblePlayer(player) then return false, "invalid_player" end

    context = context or {}
    local level_factor = FiniteNumber(context.level_factor) or 1
    level_factor = math.max(0, math.min(1, level_factor))
    local bonus = 1
    if source ~= "daily_quest" then
        if context.is_combat then
            local rank = player.components.hh_rank
            if rank ~= nil and rank:GetRank() >= RankDefs.RANK.S then
                bonus = bonus * (TUNING.HH_SUPER_GROWTH.KILL_EXP_MULT or 1.25)
            end
        end
        local effects = player.components.hh_dungeon_effects
        if effects ~= nil then
            local player_factor, dungeon_factor = effects:GetExpFactors(context.is_dungeon == true)
            bonus = bonus * player_factor * dungeon_factor
        end
        bonus = math.min(TUNING.HH_EXP_BALANCE.MAX_BONUS_MULTIPLIER or 1.75, bonus)
    end

    local amount = math.max(1, math.floor(base_amount * level_factor * bonus + 0.5))
    local ok, reason = player.components.hh_leveling:AddExp(amount)
    return ok and true or false, ok and amount or reason
end
```

- [ ] **Step 6: Run core tests and existing progression regression**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_solo_progression.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit Task 2 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/progression/hh_progression.lua mods/PhamNhanTuTien/scripts/components/hh_dungeon_effects.lua mods/PhamNhanTuTien/main/hh_tunning.lua mods/PhamNhanTuTien/tools/test_unified_progression_core.py
git commit -m "feat: centralize Pham Nhan experience awards"
```

---

### Task 3: Solo Combat Attribution and Rebalanced Enemy Rewards

**Files:**
- Create: `mods/PhamNhanTuTien/tools/test_unified_progression_combat.py`
- Modify: `mods/PhamNhanTuTien/scripts/progression/hh_progression.lua`
- Modify: `mods/PhamNhanTuTien/main/hh_api.lua:77-147,275-325,327-445`
- Modify: `mods/PhamNhanTuTien/main/hh_tunning.lua:633-764`

**Interfaces:**
- Consumes: `HHUtils:GetKillCreditPlayer(attacker)`, `Progression.Award`, `TUNING.HH_MOB_EXP`, `TUNING.HH_TREASURE_BOSS_EXP`, `TUNING.HH_DUNGEON_BOSS_EXP`.
- Produces: `Progression.AwardKill(attacker, victim) -> boolean, integer|string`.

- [ ] **Step 1: Write failing solo-combat tests**

Create a Lua-runtime harness with a living player, a decoy `AllPlayers` entry, an owned shadow whose follower leader is the player, and victims with prefab/tag/component stubs. Pin these behaviors:

```python
def test_direct_kill_credits_only_killer_and_never_scans_nearby_players(self):
    lua = combat_runtime()
    ok, amount, owner_xp, decoy_xp = lua.eval("RunDirectKillCase")()
    self.assertEqual((ok, amount, owner_xp, decoy_xp), (True, 10, 10, 0))

def test_owned_shadow_kill_credits_owner_once(self):
    lua = combat_runtime()
    ok, amount, owner_xp = lua.eval("RunOwnedShadowKillCase")()
    self.assertEqual((ok, amount, owner_xp), (True, 10, 10))

def test_cyclic_owner_chain_returns_no_credit(self):
    lua = combat_runtime()
    ok, reason = lua.eval("RunCyclicOwnerCase")()
    self.assertEqual((ok, reason), (False, "no_player_owner"))

def test_duplicate_death_noxp_and_owned_victim_award_zero(self):
    lua = combat_runtime()
    first, duplicate, noxp, owned, total = lua.eval("RunIneligibleVictimCases")()
    self.assertTrue(first)
    self.assertEqual((duplicate, noxp, owned, total), (False, False, False, 10))

def test_overlevel_reduction_affects_normal_mob_but_not_boss(self):
    lua = combat_runtime()
    normal_amount, boss_amount = lua.eval("RunOverlevelCases")()
    self.assertEqual((normal_amount, boss_amount), (1, 750))

def test_named_dungeon_boss_base_rewards(self):
    lua = combat_runtime()
    igris, sharkboi, beru = lua.eval("ReadNamedDungeonBossRewards")()
    self.assertEqual((igris, sharkboi, beru), (3000, 4500, 6000))
```

Define the named Lua fixtures in `combat_runtime()`. Each fixture constructs fresh objects with `NewAwardPlayer`, `NewOwnedShadow`, and `NewVictim`; `RunDirectKillCase` sets a decoy in `AllPlayers` and replaces iteration with an error sentinel, while `RunIneligibleVictimCases` calls the same victim twice and gives the other victims a `noxp` tag or valid player owner.

- [ ] **Step 2: Run combat tests and verify failure**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_combat.py -v
```

Expected: FAIL because `Progression.AwardKill` is missing and `hh_api.lua` still contains recipient sharing.

- [ ] **Step 3: Rebalance combat data to the approved bands**

Keep the existing prefab membership lists, but replace the numeric remap with:

```lua
local MOB_EXP_BY_SOURCE_TIER = {
    [1] = 5, [2] = 10, [3] = 25, [4] = 40, [5] = 60,
    [20] = 750, [30] = 2000, [40] = 2500,
}
for prefab, source_tier in pairs(TUNING.HH_MOB_EXP) do
    TUNING.HH_MOB_EXP[prefab] = MOB_EXP_BY_SOURCE_TIER[source_tier]
end
```

Apply explicit miniboss overrides:

```lua
TUNING.HH_MOB_EXP.leif = 100
TUNING.HH_MOB_EXP.leif_sparse = 100
TUNING.HH_MOB_EXP.lordfruitfly = 120
TUNING.HH_MOB_EXP.fruitdragon = 120
TUNING.HH_MOB_EXP.spiderqueen = 150
TUNING.HH_MOB_EXP.warg = 180
TUNING.HH_MOB_EXP.claywarg = 180
TUNING.HH_MOB_EXP.gingerbreadwarg = 180
```

Keep dungeon ordinary mobs at 20 and the dungeon pig at 40. Set special tables exactly:

```lua
TUNING.HH_TREASURE_BOSS_EXP = {
    walrus_adc = { exp = 3500, level = 65, class = "boss" },
    mutateddeerclops_boss = { exp = 3500, level = 80, class = "superboss" },
    mutatedbearger_boss = { exp = 3500, level = 80, class = "superboss" },
    mutatedwarg_boss = { exp = 3500, level = 80, class = "superboss" },
    hh_sharkboi_boss = { exp = 3500, level = 85, class = "superboss" },
    treasure_kps = { exp = 3500, level = 100, class = "superboss" },
    treasure_cat_you = { exp = 3500, level = 100, class = "superboss" },
}

TUNING.HH_DUNGEON_BOSS_EXP = {
    leif = { exp = 750, level = 20, class = "boss" },
    spiderqueen = { exp = 750, level = 25, class = "boss" },
    warg = { exp = 750, level = 30, class = "boss" },
    deerclops = { exp = 1000, level = 35, class = "boss" },
    bearger = { exp = 1000, level = 35, class = "boss" },
    dragonfly = { exp = 1500, level = 45, class = "boss" },
    minotaur = { exp = 1500, level = 45, class = "boss" },
    hh_igris_dungeon = { exp = 3000, level = 60, class = "boss" },
    hh_sharkboi = { exp = 4500, level = 80, class = "superboss" },
    hh_beru_dungeon = { exp = 6000, level = 100, class = "superboss" },
}
```

Preserve recommended levels by deriving `HH_MOB_RECOMMENDED_LEVEL` before replacing source-tier numbers, as the current file already does.

- [ ] **Step 4: Implement kill metadata and one-recipient attribution**

Move the current metadata and level-factor behavior from `hh_api.lua` into `hh_progression.lua`. `AwardKill` must follow this order:

```lua
function M.AwardKill(attacker, victim)
    if victim == nil or victim.hh_exp_awarded then return false, "duplicate_death" end
    if victim.HasTag ~= nil and (victim:HasTag("noxp") or victim:HasTag("player")) then
        return false, "ineligible_victim"
    end
    if HHUtils:GetKillCreditPlayer(victim) ~= nil then
        return false, "owned_victim"
    end

    local player = HHUtils:GetKillCreditPlayer(attacker)
    if player == nil then return false, "no_player_owner" end
    local meta = ResolveExpMeta(victim)
    if meta == nil or (meta.exp or 0) <= 0 then return false, "no_reward" end

    victim.hh_exp_awarded = true
    local is_dungeon = victim.hh_is_dungeon_monster == true
        or victim.hh_is_dungeon_boss == true
    local source = is_dungeon and "dungeon"
        or (meta.class == "boss" or meta.class == "superboss") and "boss" or "combat"
    return M.Award(player, source, meta.exp, {
        is_combat = true,
        is_dungeon = is_dungeon,
        level_factor = GetLevelFactor(player, meta),
    })
end
```

`ResolveExpMeta` must prefer treasure metadata, then dungeon-boss metadata, then ordinary prefab data. `GetLevelFactor` returns 1 for `boss` and `superboss` and uses the ordered `LEVEL_FACTORS` table otherwise.

- [ ] **Step 5: Replace all `hh_api.lua` combat award call sites**

At the top of `hh_api.lua` add:

```lua
local Progression = require("progression/hh_progression")
```

Delete `HHIsEligibleExpPlayer`, `HHGetExpRecipients`, and the local award loop. Replace the local function with:

```lua
local function HHAwardKillExp(killer, victim)
    return Progression.AwardKill(killer, victim)
end
```

Keep the Sharkboi/daywalker defeated-state guards and the player's `killed` listener, but make every path call this same function. No code in the resulting file may iterate `AllPlayers`, `players_in_dungeon`, or divide by recipient count for EXP.

- [ ] **Step 6: Run combat, core, and existing solo tests**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_combat.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_solo_progression.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit Task 3 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/progression/hh_progression.lua mods/PhamNhanTuTien/main/hh_api.lua mods/PhamNhanTuTien/main/hh_tunning.lua mods/PhamNhanTuTien/tools/test_unified_progression_combat.py
git commit -m "feat: award solo combat experience to one owner"
```

---

### Task 4: Player-Event Survival and Production EXP

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/components/hh_exp_tracker.lua`
- Create: `mods/PhamNhanTuTien/tools/test_unified_progression_activities.py`
- Modify: `mods/PhamNhanTuTien/main/hh_tunning.lua:617-633`
- Modify: `mods/PhamNhanTuTien/main/hh_api.lua:410-430`

**Interfaces:**
- Consumes: `Progression.Award(player, source, base, context)` and authoritative player/world events.
- Produces: `HHExpTracker:OnPick`, `OnFinishedWork`, `OnBuild`, `OnEat`, `OnFish`, `OnCatch`, `OnPlant`, `OnLearnRecipe`, `OnSave`, `OnLoad`.

- [ ] **Step 1: Write failing activity and duplicate-suppression tests**

Create a runtime harness that loads `hh_exp_tracker.lua`. Pin this table exactly:

```python
EXPECTED_BASE = {
    "pick": 1, "finishedwork": 4, "plant_regular": 2,
    "plant_special": 3, "tend": 1, "cook": 4,
    "craft": 2, "build": 6, "repair": 5,
    "pond_fish": 8, "ocean_fish": 20, "catch": 5,
    "first_learn": 10,
}
```

Add explicit tests for:

```python
def test_eating_uses_positive_hunger_only_and_clamps_one_to_five(self):
    lua = activity_runtime()
    negative, zero, tiny, medium, large = lua.eval("RunEatingCases")()
    self.assertEqual((negative, zero, tiny, medium, large), (0, 0, 1, 2, 5))

def test_free_recipe_is_rejected_but_positive_character_cost_counts(self):
    lua = activity_runtime()
    free_xp, zero_xp, character_cost_xp = lua.eval("RunRecipeCostCases")()
    self.assertEqual((free_xp, zero_xp, character_cost_xp), (0, 0, 2))

def test_recipe_first_learn_is_idempotent_across_save_and_load(self):
    lua = activity_runtime()
    before_save, after_load = lua.eval("RunFirstLearnSaveCase")()
    self.assertEqual((before_save, after_load), (10, 10))

def test_pick_does_not_listen_to_itemget_or_dropitem(self):
    lua = activity_runtime()
    after_inventory_events, after_pick = lua.eval("RunPickCases")()
    self.assertEqual((after_inventory_events, after_pick), (0, 1))

def test_work_awards_only_finishedwork_not_working(self):
    lua = activity_runtime()
    after_hits, after_completion = lua.eval("RunWorkCases")()
    self.assertEqual((after_hits, after_completion), (0, 4))

```

Define these Lua fixtures inside `activity_runtime()`. They instantiate `HHExpTracker`, route events through the test entity's real listener table, and read the cumulative amount from the stub `hh_leveling:AddExp`; `RunFirstLearnSaveCase` creates a second tracker and feeds it the first tracker's `OnSave()` result before replaying the recipe event.

- [ ] **Step 2: Run activity tests and verify missing tracker failure**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_activities.py -v
```

Expected: FAIL because `hh_exp_tracker.lua` does not exist.

- [ ] **Step 3: Add activity tuning and recipe-cost helper**

Add:

```lua
TUNING.HH_ACTIVITY_EXP = {
    PICK = 1, FINISHED_WORK = 4,
    PLANT_REGULAR = 2, PLANT_SPECIAL = 3,
    TEND = 1, COOK = 4, CRAFT = 2, BUILD = 6,
    REPAIR = 5, POND_FISH = 8, OCEAN_FISH = 20,
    CATCH = 5, FIRST_LEARN = 10,
}

TUNING.HH_SPECIAL_PLANT_PREFABS = {
    pinecone = true, acorn = true, twiggy_nut = true,
    marblebean = true, palmcone_seed = true,
}
```

In the tracker, implement `HasPositiveRecipeCost(recipe)` by scanning both `recipe.ingredients` and `recipe.character_ingredients` and accepting only a finite `amount > 0`.

- [ ] **Step 4: Implement the player activity tracker**

The component constructor registers only these listeners:

```lua
inst:ListenForEvent("picksomething", function(_, data) self:OnPick(data) end)
inst:ListenForEvent("finishedwork", function(_, data) self:OnFinishedWork(data) end)
inst:ListenForEvent("builditem", function(_, data) self:OnBuild(data, false) end)
inst:ListenForEvent("buildstructure", function(_, data) self:OnBuild(data, true) end)
inst:ListenForEvent("oneat", function(_, data) self:OnEat(data) end)
inst:ListenForEvent("fishingcollect", function(_, data) self:OnFish(data, false) end)
inst:ListenForEvent("fishcaught", function(_, data) self:OnFish(data, true) end)
inst:ListenForEvent("catch", function(_, data) self:OnCatch(data) end)
inst:ListenForEvent("learnrecipe", function(_, data) self:OnLearnRecipe(data) end)
```

Listen to `TheWorld`'s `itemplanted` event and accept only `data.doer == inst`. Classify special plants from `data.item`, `data.seed`, `data.plant`, or `data.prefab`; a recognized special prefab or an entity carrying the `tree` tag gets 3, otherwise 2.

Eating computes:

```lua
local hunger = data ~= nil and data.food ~= nil and data.food.components ~= nil
    and data.food.components.edible ~= nil and data.food.components.edible.hungervalue or 0
if hunger > 0 then
    local base = math.max(1, math.min(5, math.floor(hunger / 20 + 0.5)))
    Progression.Award(self.inst, "activity", base)
end
```

Recipe learning normalizes `data.recipe` to a string key, checks `self.rewarded_recipes[key]`, marks it before calling `Progression.Award(self.inst, "first_learn", TUNING.HH_ACTIVITY_EXP.FIRST_LEARN)`, and persists the set through `OnSave`/`OnLoad`. All other tracker handlers use source `activity` and their named `TUNING.HH_ACTIVITY_EXP` value. Do not register `itemget`, `dropitem`, or `working` listeners.

- [ ] **Step 5: Attach the tracker without touching Achievement**

In the existing master-sim player setup in `hh_api.lua`:

```lua
if not inst.components.hh_exp_tracker then
    inst:AddComponent("hh_exp_tracker")
end
```

Do not add any require, mod dependency, or conditional detection for Achievement.

- [ ] **Step 6: Run activity, core, and combat tests**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_activities.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_combat.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit Task 4 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/components/hh_exp_tracker.lua mods/PhamNhanTuTien/main/hh_tunning.lua mods/PhamNhanTuTien/main/hh_api.lua mods/PhamNhanTuTien/tools/test_unified_progression_activities.py
git commit -m "feat: award experience for player activities"
```

---

### Task 5: Authoritative Tending, Cooking, and Repair Completion

**Files:**
- Create: `mods/PhamNhanTuTien/main/hh_exp_events.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_solo_source.lua:20-36`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_progression_activities.py`

**Interfaces:**
- Consumes: `Progression.Award(player, "activity", base)`, DST `farmplanttendable`, `stewer`, and `repairer` components.
- Produces: transparent component wrappers that preserve all original returns and award only after a successful state change.

- [ ] **Step 1: Add failing component-wrapper tests**

Capture registered `AddComponentPostInit` callbacks in the Lua harness and assert exact call counts and rewards:

```python
def test_tend_requires_consumed_tendable_state(self):
    lua = activity_runtime()
    result = lua.eval("RunTendCases")()
    self.assertEqual(tuple(result.values()), (0, 1, 1))

def test_cooking_rewards_owner_once_when_finished_batch_is_harvested(self):
    lua = activity_runtime()
    failed, first, duplicate, original_calls = lua.eval("RunCookingCases")()
    self.assertEqual((failed, first, duplicate, original_calls), (0, 4, 4, 3))

def test_repair_requires_durability_increase_and_preserves_returns(self):
    lua = activity_runtime()
    no_change, repaired, first_return, second_return = lua.eval("RunRepairCases")()
    self.assertEqual((no_change, repaired), (0, 5))
    self.assertEqual((first_return, second_return), ("ok", 17))
```

`RunTendCases`, `RunCookingCases`, and `RunRepairCases` are Lua fixtures in the test file. Each fixture installs the captured wrapper, invokes the wrapped method with failed and successful component state, and returns cumulative awarded EXP plus original return values.

- [ ] **Step 2: Run wrapper tests and verify the missing module failure**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_activities.py -v
```

Expected: FAIL because `main/hh_exp_events.lua` does not exist.

- [ ] **Step 3: Install authoritative component wrappers**

In `main/hh_exp_events.lua`, wrap and preserve original return values for:

1. `farmplanttendable:TendTo(doer, ...)`: award 1 only when `tendable` was true, the call did not return false, and the action consumed the tendable state.
2. `stewer:StartCooking(doer, ...)`: record the valid cook owner and increment a batch key.
3. `stewer:Harvest(harvester, ...)`: award 4 to the recorded owner only when the pot was done before the call, harvest succeeded, and that batch key has not been rewarded.
4. `repairer:Repair(target, doer, ...)`: snapshot finite uses, armor condition, or fueled percent before and after; award 5 only when the call succeeds and the value increases.

Use this shared return-preservation helper:

```lua
local function Pack(...)
    return { n = select("#", ...), ... }
end

local function Unpack(results)
    return unpack(results, 1, results.n)
end
```

Every wrapper calls the original exactly once and returns all original values.

- [ ] **Step 4: Load the hook module after tuning and progression initialization**

In `ttk_solo_source.lua`, immediately after `hh_api.lua`:

```lua
modimport("main/hh_exp_events.lua")
```

Do not inspect, import, or conditionally branch on the standalone Achievement mod.

- [ ] **Step 5: Run activity and bootstrap tests**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_activities.py -v
python mods/PhamNhanTuTien/tools/test_unified_ui.py -v
```

Expected: all tests PASS and bootstrap loading reaches the hook module after tuning/API.

- [ ] **Step 6: Commit Task 5 only**

```powershell
git add -- mods/PhamNhanTuTien/main/hh_exp_events.lua mods/PhamNhanTuTien/main/ttk_solo_source.lua mods/PhamNhanTuTien/tools/test_unified_progression_activities.py
git commit -m "feat: award experience for completed world actions"
```

---

### Task 6: Difficulty-Scaled Daily Quest EXP

**Files:**
- Create: `mods/PhamNhanTuTien/tools/test_unified_progression_quests.py`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_daily_quest.lua:250-285,401-445,709-740`
- Modify: `mods/PhamNhanTuTien/scripts/quests/hh_daily_quest_defs.lua:1-70`

**Interfaces:**
- Consumes: `Progression.GetDailyQuestReward(player, difficulty)`, `Progression.Award(player, "daily_quest", amount)`.
- Produces: quest definitions whose `difficulty` is authoritative and a completion event whose `reward` is the computed amount.

- [ ] **Step 1: Write failing daily quest tests**

Create tests for assignment, load, and completion:

```python
def test_assignment_uses_difficulty_not_legacy_fixed_reward(self):
    lua = quest_runtime()
    reward = lua.eval("RunAssignmentCase")("easy", 1, 9999)
    self.assertEqual(reward, 20)

def test_reward_is_recomputed_at_completion_level(self):
    lua = quest_runtime()
    assigned, completed = lua.eval("RunLevelChangeCompletionCase")()
    self.assertEqual((assigned, completed), (35, 419))

def test_completion_bypasses_rank_and_timed_multipliers(self):
    lua = quest_runtime()
    reward, received = lua.eval("RunBuffedQuestCase")()
    self.assertEqual((reward, received), (419, 419))

def test_completion_is_idempotent(self):
    lua = quest_runtime()
    received, completed_count = lua.eval("RunDuplicateCompletionCase")()
    self.assertEqual((received, completed_count), (20, 1))

def test_load_ignores_saved_legacy_reward(self):
    lua = quest_runtime()
    loaded_reward = lua.eval("RunLegacyLoadCase")()
    self.assertEqual(loaded_reward, 20)
```

Define each named fixture in `quest_runtime()`. Use a deterministic one-entry `QuestDefs.list`, stub `math.random` to select it, set `hh_leveling.level` explicitly, and record `hh_leveling.received` through the real `Progression.Award` path.

- [ ] **Step 2: Run quest tests and verify fixed-reward failures**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_quests.py -v
```

Expected: FAIL because assignment/load still copy `quest.reward` and completion calls `hh_leveling:AddExp` directly.

- [ ] **Step 3: Make difficulty the only reward authority**

At the top of `hh_daily_quest.lua` add:

```lua
local Progression = require("progression/hh_progression")
```

On assignment, set progress fields first but do not freeze the level-scaled value for completion:

```lua
self.reward = Progression.GetDailyQuestReward(self.inst, quest.difficulty) or 0
```

At the start of `CompleteQuest`, before status becomes completed, recompute:

```lua
local computed_reward = quest ~= nil
    and Progression.GetDailyQuestReward(self.inst, quest.difficulty) or nil
if computed_reward == nil then return end
self.reward = computed_reward
```

Award through:

```lua
local exp_granted, exp_result = Progression.Award(
    self.inst, "daily_quest", self.reward, { is_combat = false, is_dungeon = false })
local granted_amount = exp_granted and exp_result or 0
```

Use `granted_amount` in FX, talker text, and the completion event. Preserve `exp_reason` when blocked.

On load, derive `self.reward` from the current quest difficulty; ignore `data.reward` and `quest.reward` for the fresh-save path.

- [ ] **Step 4: Remove fixed rewards from quest definitions**

Mechanically remove every `reward=<number>` field from `hh_daily_quest_defs.lua`. Keep each `difficulty="easy|medium|hard"` unchanged. Add module validation after the list:

```lua
local VALID_DIFFICULTY = { easy = true, medium = true, hard = true }
for _, quest in ipairs(quests) do
    assert(VALID_DIFFICULTY[quest.difficulty],
        "Daily quest " .. tostring(quest.id) .. " has invalid difficulty")
end
```

- [ ] **Step 5: Run quest and activity tests**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_quests.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_activities.py -v
```

Expected: all tests PASS; quest events still track the same gameplay events as before.

- [ ] **Step 6: Commit Task 6 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/components/hh_daily_quest.lua mods/PhamNhanTuTien/scripts/quests/hh_daily_quest_defs.lua mods/PhamNhanTuTien/tools/test_unified_progression_quests.py
git commit -m "feat: scale daily quest experience by level goal"
```

---

### Task 7: Shared Dungeon Rank Mapping and Server Enforcement

**Files:**
- Create: `mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py`
- Modify: `mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua:1-60`
- Modify: `mods/PhamNhanTuTien/scripts/prefabs/dungeon_gate.lua:1-64`
- Modify: `mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua:1211-1301`

**Interfaces:**
- Consumes: `player.components.hh_rank:GetRank()`, `DungeonManager.max_waves`.
- Produces: `RankDefs.GetDungeonRequiredRank(waves) -> rank|nil`, `RankDefs.GetDungeonRequiredRankName(waves) -> string|nil`.

- [ ] **Step 1: Write failing mapping and gate tests**

Pin the complete mapping and fail-closed behavior:

```python
def test_wave_rank_mapping(self):
    expected = {2: "E", 3: "D", 4: "C", 5: "B", 6: "A",
                7: "S", 8: "S", 9: "S", 10: "S"}
    lua = dungeon_runtime()
    get_name = lua.eval("function(w) return RankDefs.GetDungeonRequiredRankName(w) end")
    self.assertEqual({wave: get_name(wave) for wave in expected}, expected)
    self.assertIsNone(get_name(1))
    self.assertIsNone(get_name(11))

def test_gate_rejects_missing_or_insufficient_rank(self):
    lua = dungeon_runtime()
    missing, below, message = lua.eval("RunRejectedRankCases")()
    self.assertEqual((missing, below), (False, False))
    self.assertIn("Rank A", message)

def test_gate_accepts_exact_or_higher_rank(self):
    lua = dungeon_runtime()
    exact, higher = lua.eval("RunAcceptedRankCases")()
    self.assertEqual((exact, higher), (True, True))

def test_rank_check_does_not_bypass_existing_guards(self):
    lua = dungeon_runtime()
    dead, cooldown, inactive, late = lua.eval("RunExistingGuardCases")()
    self.assertEqual((dead, cooldown, inactive, late), (False, False, False, False))
```

Define the named fixtures in `dungeon_runtime()`. `NewDungeonPlayer(rank)` supplies talker, health, inventory, cooldown, and `hh_rank`; `NewDungeonManager(waves)` supplies an active gate and valid exit, then each guard fixture changes exactly one pre-existing condition.

- [ ] **Step 2: Run dungeon tests and verify missing helper failure**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py -v
```

Expected: FAIL because mapping is local to the prefab and manager entry has no rank validation.

- [ ] **Step 3: Move the mapping to `hh_rank_defs.lua`**

Add:

```lua
local DUNGEON_RANK_BY_WAVES = {
    [2] = M.RANK.E, [3] = M.RANK.D, [4] = M.RANK.C,
    [5] = M.RANK.B, [6] = M.RANK.A,
    [7] = M.RANK.S, [8] = M.RANK.S, [9] = M.RANK.S, [10] = M.RANK.S,
}

function M.GetDungeonRequiredRank(waves)
    return DUNGEON_RANK_BY_WAVES[tonumber(waves)]
end

function M.GetDungeonRequiredRankName(waves)
    local rank = M.GetDungeonRequiredRank(waves)
    return rank ~= nil and M.GetName(rank) or nil
end
```

- [ ] **Step 4: Make the gate display consume the shared helper**

Delete local `DUNGEON_RANK_BY_WAVES`. Require `guild/hh_rank_defs` and use:

```lua
local rank = RankDefs.GetDungeonRequiredRankName(total_waves)
```

Keep existing icon and party-size presentation unchanged in this task.

- [ ] **Step 5: Enforce rank in `CanEnterDungeon`**

After validating player state and active gate, but before cooldown/inventory scans, add:

```lua
local required_rank = RankDefs.GetDungeonRequiredRank(self.max_waves)
local rank_component = player.components ~= nil and player.components.hh_rank or nil
local current_rank = rank_component ~= nil and rank_component:GetRank() or nil
if required_rank == nil then
    Say("Lỗi: Cấp hầm ngục không hợp lệ.")
    return false
end
if current_rank == nil or current_rank < required_rank then
    Say("Cần đạt Rank " .. RankDefs.GetName(required_rank) .. " để vào hầm ngục này.")
    return false
end
```

Add the `RankDefs` require at file top. Do not reorder or delete cooldown, state, follower-item, authority, or exit checks.

- [ ] **Step 6: Run dungeon and related progression tests**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_combat.py -v
python mods/PhamNhanTuTien/tools/test_jitan_solo.py -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit Task 7 only**

```powershell
git add -- mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua mods/PhamNhanTuTien/scripts/prefabs/dungeon_gate.lua mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py
git commit -m "feat: enforce displayed dungeon rank requirements"
```

---

### Task 8: Progression Simulation, Integration Guard, and Full Verification

**Files:**
- Create: `mods/PhamNhanTuTien/tools/simulate_unified_progression.py`
- Modify: `mods/PhamNhanTuTien/tools/test_unified_progression_core.py`
- Modify: `mods/PhamNhanTuTien/docs/achievement-merge-progression-contract.md`

**Interfaces:**
- Consumes: the final formula and reward tables from Tasks 1–7.
- Produces: deterministic CLI report and static integration guard for the later Achievement merge.

- [ ] **Step 1: Write the deterministic comparison and pacing simulation**

Implement exact curve functions:

```python
def old_pham_nhan_goal(level: int) -> int:
    n = level - 1
    return 100 + 25 * n + 5 * n * n

def unified_goal(level: int) -> int:
    n = level - 1
    return int(100 + 10 * n + 1.5 * n * n + 0.5)

def achievement_goal(level: int) -> int:
    return 50 + int(0.1 * level * level)

def achievement_total(target_level: int) -> int:
    # The historical strict `>` check costs one extra EXP for the whole climb;
    # the carried remainder prevents paying that extra point at every level.
    return sum(achievement_goal(level) for level in range(1, target_level)) + 1
```

Use these deterministic profiles:

```python
PROFILES = {
    "balanced": {
        "xp_per_hour": 7450,
        "shares": {"survival": .33, "combat": .22, "quests": .22, "bosses": .23},
        "range": (60, 80),
    },
    "optimized": {
        "xp_per_hour": 11917,
        "shares": {"survival": .20, "combat": .30, "quests": .20, "bosses": .30},
        "range": (40, 50),
    },
    "survival_heavy": {
        "xp_per_hour": 4970,
        "shares": {"survival": .60, "combat": .15, "quests": .20, "bosses": .05},
        "range": (95, 120),
    },
    "casual": {
        "xp_per_hour": 4663,
        "shares": {"survival": .40, "combat": .20, "quests": .20, "bosses": .20},
        "range": (100, 130),
    },
}
```

The script prints cumulative totals at levels 10 through 100, old/new/Achievement ratios, hours per profile, and source percentages. It exits non-zero unless:

```python
assert total(unified_goal) == 536258
assert total(old_pham_nhan_goal) == 1723920
assert achievement_total(100) == 37741
assert 60 <= hours["balanced"] <= 80
assert 40 <= hours["optimized"] <= 50
assert 95 <= hours["survival_heavy"] <= 120
assert 100 <= hours["casual"] <= 130
assert 0.30 <= PROFILES["balanced"]["shares"]["survival"] <= 0.35
assert 0.20 <= PROFILES["balanced"]["shares"]["combat"] <= 0.25
assert 0.20 <= PROFILES["balanced"]["shares"]["quests"] <= 0.25
assert 0.20 <= PROFILES["balanced"]["shares"]["bosses"] <= 0.30
```

- [ ] **Step 2: Add a static future-merge guard test**

Append a Python test that reads current Phàm Nhân bootstrap/API files and the contract:

```python
def test_achievement_is_not_currently_imported_and_contract_is_explicit(self):
    modmain = (MOD / "modmain.lua").read_text(encoding="utf-8")
    bootstrap = (MOD / "main" / "ttk_solo_source.lua").read_text(encoding="utf-8")
    contract = (MOD / "docs" / "achievement-merge-progression-contract.md").read_text(encoding="utf-8")
    runtime = modmain + "\n" + bootstrap
    self.assertNotIn('modimport("mods/AchievementLevel', runtime)
    self.assertNotIn('AddComponent("levelsystem")', runtime)
    self.assertIn('Progression.Award(player, source, base, context)', contract)
    self.assertIn('Achievement/Star completion never calls either award function', contract)
```

- [ ] **Step 3: Run the complete progression suite**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_progression_core.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_combat.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_activities.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_quests.py -v
python mods/PhamNhanTuTien/tools/test_unified_progression_dungeon.py -v
python mods/PhamNhanTuTien/tools/test_solo_progression.py -v
python mods/PhamNhanTuTien/tools/simulate_unified_progression.py
```

Expected: all tests PASS; simulation reports 536,258 new EXP, 1,723,920 old EXP, 37,741 Achievement EXP, and about 72.0 balanced hours.

- [ ] **Step 4: Run affected existing regression tools**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_unified_ui.py -v
python mods/PhamNhanTuTien/tools/test_jitan_solo.py -v
python mods/PhamNhanTuTien/tools/test_weapon_solo.py -v
python mods/PhamNhanTuTien/tools/test_vanhonphien_solo.py -v
```

Expected: all tests PASS. If an unrelated pre-existing failure occurs, record the exact command/output and do not rewrite unrelated features to hide it.

- [ ] **Step 5: Verify forbidden runtime coupling and removed sharing**

Run:

```powershell
rg -n "levelsystem|AchievementLevel|allachivevent|allachivcoin" mods/PhamNhanTuTien/modmain.lua mods/PhamNhanTuTien/main mods/PhamNhanTuTien/scripts/progression mods/PhamNhanTuTien/scripts/components/hh_exp_tracker.lua
rg -n "SHARE_RADIUS|HHGetExpRecipients|/ #recipients|players_in_dungeon.*EXP" mods/PhamNhanTuTien/main/hh_api.lua mods/PhamNhanTuTien/scripts/progression/hh_progression.lua mods/PhamNhanTuTien/main/hh_tunning.lua
```

Expected: first command finds only the explanatory prohibition in comments/docs if those paths include it; second command returns no matches.

- [ ] **Step 6: Refresh CodeGraph and query the final award path**

Run:

```powershell
codegraph sync .
codegraph explore "Progression.Award AwardKill hh_exp_tracker daily quest dungeon rank gate in mods/PhamNhanTuTien"
```

Expected: the graph shows activity, combat, and quest adapters converging on `Progression.Award`, which calls `hh_leveling:AddExp`; no Achievement module appears in the runtime call path.

- [ ] **Step 7: Review the final diff against the approved spec**

Run:

```powershell
git diff --check
git diff --stat
git status --short
```

Check every spec section against the task tests, confirm only intended files are staged for this task, and preserve every unrelated dirty-worktree path.

- [ ] **Step 8: Commit Task 8 only**

```powershell
git add -- mods/PhamNhanTuTien/tools/simulate_unified_progression.py mods/PhamNhanTuTien/tools/test_unified_progression_core.py mods/PhamNhanTuTien/docs/achievement-merge-progression-contract.md
git commit -m "test: verify unified Pham Nhan progression pacing"
```

---

## Final Acceptance Checklist

- [ ] A fresh player begins at level 1, EXP 0, AP 0.
- [ ] The exact level-100 cumulative requirement is 536,258.
- [ ] All approved survival/production actions award their exact base values once per successful completion.
- [ ] Failed actions, free recipes, repeated recipe learning, duplicate death callbacks, owned victims, and `noxp` targets award zero.
- [ ] One direct player or owned shadow receives 100% of kill EXP; nearby players receive nothing.
- [ ] Rank S is 1.25× combat EXP, player buff is 1.25×, dungeon buff is 1.35×, and combined bonus is capped at 1.75×.
- [ ] Daily quests use 6%/10%/15% with minimums 20/35/50 and no modifiers.
- [ ] Dungeon waves 2–10 display and enforce E/D/C/B/A/S/S/S/S.
- [ ] Achievement is still unmerged, no runtime dependency exists, and the future integration contract names the only allowed APIs.
- [ ] The simulation compares old Phàm Nhân, historical Achievement, and unified progression and passes every pacing band.
- [ ] CodeGraph is synchronized after implementation.
