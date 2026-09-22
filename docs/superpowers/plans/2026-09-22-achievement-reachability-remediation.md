# Phàm Nhân Achievement Reachability Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every active, source-backed achievement reachable by a real master-simulation transaction, correct the distinct-item and unified-level regressions found by final acceptance, and state remaining upstream dependencies without dummy unlocks.

**Architecture:** `ttk_achievement` remains a server-authoritative consumer of committed gameplay receipts. Each adapter is installed at the existing success boundary that knows the actor, rather than at prediction, animation, setter, proximity, or arbitrary client RPC boundaries. The achievement core gains a narrow persisted evidence-set rule only for definitions explicitly marked distinct; EVA souls read `hh_leveling` as their sole level authority.

**Tech Stack:** DST Lua, existing Phàm Nhân components/RPCs, Lupa Lua 5.1 tests under Python 3.14, Next/Vitest only for exported wiki documentation.

**Spec:** `docs/superpowers/specs/2026-09-21-pham-nhan-achievement-star-perks-design.md`

## Global Constraints

- Runtime target is `mods/PhamNhanTuTien`; do not import `mods/AchievementLevel` or its Level/EXP authority.
- Preserve current `ttk_` and `hh_` save/RPC/prefab identifiers. All awards run on master simulation after a successful commit.
- Keep exactly 231 active achievements and exactly 1,000 Star. A catalog correction must preserve group and reward totals.
- Do not credit client prediction, failed actions, setters reused by loading/admin paths, nearby players, or unproven item ownership.
- `hh_leveling` is the only Level/EXP authority. Do not set `TUNING.TTK_SEASONAL_CLAIM_XP`; its amount remains owned by the separate EXP-calibration task.
- Do not fabricate the unavailable two ability dependencies, 42 inheritance recipes, or 21 Antique items. Keep their purchasing guards and documented statuses.

## Review Focus

- Repeated receipt/delivery callbacks must never advance a counter twice; each task below pins its receipt identity or state transition.
- A different player, a load callback, or a failed transaction must never receive credit for a cook, spin, dungeon, guild, or strengthening action.
- Definitions requiring all variants must preserve the exact seen set through save/load and reject duplicates/unknown IDs without changing ordinary quantity objectives.
- Dungeon completion and Igris/Beru kills must use current-run membership, not combat target or player proximity.
- Seasonal EXP must remain claimable only after a finite positive configuration is supplied; absence must leave state untouched rather than inventing XP.

---

### Task 14: Canonical Distinct Evidence and Unified Soul Level

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua`
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/eva_souls.lua`
- Modify: `mods/PhamNhanTuTien/scripts/util/eva_widget.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_achievement_state.py`
- Modify: `mods/PhamNhanTuTien/tools/eva_integration_smoke.lua`

**Interfaces:**
- Adds definition metadata `distinct="prefab"` only to `food_liquid_luck_trinity`.
- `Core:Advance(id, amount, evidence)` derives progress from the allowlisted seen set when `distinct="prefab"`.
- `eva_souls:GetLevel()` reads `inst.components.hh_leveling.level`; `hh_levelup` is its update event.

- [ ] Write failing Lupa tests for I+I+I, I+II, save/load+III, unknown evidence, amount 100, inflated legacy counter, and one claim after reload.
- [ ] Change the trinity copy to explicitly require I, II, and III; keep cultivation-path evidence on its existing cultivation adapter.
- [ ] In the core, accept only a string evidence prefab contained in `definition.params.prefabs`; store `seen_prefabs[prefab]=true`; compute canonical progress by counting allowlisted `true` entries; sanitize saves by discarding unknown/false/nested entries and never infer a set from an old counter.
- [ ] Replace `levelsystem` and `chasni_levelup` reads/listeners in `eva_souls` with `hh_leveling` and `hh_levelup`; retain `eva_level`, soul netvars, current-soul/death save state, delayed load reconciliation, and the existing cap formula.
- [ ] Run the new state tests plus the soul smoke fixture for legacy saved level 151 versus `hh_leveling` 70, OnLoad ordering, level-up update, and death/reload preservation; commit only Task 14 paths.

### Task 15: Player Activity, Ownership, Farming, Fishing, Cooking, and Solo Survival Receipts

**Files:**
- Modify: `mods/PhamNhanTuTien/main/ttk_achievement.lua`
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_achievement_trackers.py`
- Create: `mods/PhamNhanTuTien/tools/test_achievement_reachability.py`

**Interfaces:**
- `Route(player, tracker, evidence, amount, options)` receives only committed server receipts.
- Inventory ownership uses an observed count adapter, not target-jumping `absolute=true` routing.
- Survival keys are generated from world/player state and retain no multiplayer-only rescue condition.

- [ ] Write failing source-and-Lupa tests covering a real `picksomething`, `fishingcollect`, successful cookpot completion attributed to native `chef_id`, a successful farm seed plant, successful farm-only water/fertilize actions, quantity changes in held inventory/overflow, and failed actions producing no route.
- [ ] Add one master-only pick adapter to the existing `picksomething` listener and a `fishingcollect` listener that requires the actual fish receipt; retain weak event-data deduplication only for duplicate delivery.
- [ ] Attribute cooking to saved native `chef_id` after committed `ondonecooking`, preserve the previous callback, and prevent load replay from awarding twice. Capture planting crop evidence from supported seed mappings after `farmplantable:Plant` succeeds.
- [ ] Attach a single `BufferedAction:AddSuccessAction` from `performaction`; filter `POUR_WATER`, `POUR_WATER_GROUNDTILE`, `FERTILIZE`, and the eligible `DEPLOY` fertilizer branch to actual farm targets/soil, never campfires or plain ground.
- [ ] Recompute four ownership objectives from the player inventory/overflow on deferred inventory receipt, stack/loss changes, and post-load initialization. Advance only to the observed count, preserving partial holdings and never counting remote containers.
- [ ] Replace the solo-incompatible `survive_rescue_friend` definition with a concrete solo world/player survival milestone of equal target/reward. Implement all season/day/night/temperature/revive keys from authoritative world state, counting a season only at its completed transition and heat/cold only after the player returns to a safe state. Add tests for each key and a solo-only player.
- [ ] Run reachability tests for every tracker in this task, existing tracker/catalog/state tests, then commit only Task 15 paths.

### Task 16: Guild and Dungeon Committed Boundaries

**Files:**
- Modify: `mods/PhamNhanTuTien/main/ttk_achievement.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_dungeon_shop.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_guild_shop.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_rank.lua`
- Modify only if a missing post-commit event is required: `mods/PhamNhanTuTien/scripts/components/hh_guild_quest.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_achievement_reachability.py`

**Interfaces:**
- Dungeon completion emits one receipt per cleared run to saved current-run members.
- Dungeon kill evidence carries `context="dungeon"` only for a current-run member.
- Guild routes consume existing post-commit events or emit after delivery/debit/state commit.

- [ ] Write failing tests for repeated dungeon death, a nonmember nearby player, re-entry, successful/failed dungeon shop purchase, coin add versus spend/load, automatic SS promotion versus claimed rank exam, and each guild purchase/credit receipt.
- [ ] Route existing `hh_guild_quest_assigned` and `hh_guild_quest_completed` events; add rank-exam credit only for `ClaimExam`/`source="claim_exam"`, and guild interface credit only after a valid staff interaction opens the authoritative UI.
- [ ] Emit guild-shop purchase and exact credit-spend receipts only after item delivery, debit, and stock decrement have succeeded.
- [ ] At `DungeonManager:EnterDungeon`, record first valid entry for the current run. At final-clear commit, emit one completion receipt to the member snapshot and guard duplicate final-death processing. Route positive `hh_dungeon_coin_changed`, committed dungeon-shop open, and delivery/debit/stock-complete purchases.
- [ ] Attach dungeon context to Igris/Beru kill credit using manager membership/run state rather than a target/nearby-player guess.
- [ ] Run all Task 16 reachability cases plus dungeon/guild regressions and commit only Task 16 paths.

### Task 17: Strengthening and Slot-Machine Receipts; Catalog Source Corrections

**Files:**
- Modify: `mods/PhamNhanTuTien/main/ttk_achievement.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_solo_source.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/wb_strengthen.lua`
- Modify: `mods/PhamNhanTuTien/scripts/prefabs/wb_strengthen_levelpaper.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/ttk_slotmachine.lua`
- Modify: `mods/PhamNhanTuTien/scripts/prefabs/ttk_choujiangji.lua`
- Modify: `mods/PhamNhanTuTien/scripts/ttk_slot_prizes.lua`
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_achievement_reachability.py`

**Interfaces:**
- Strengthening emits after actual consumption/outcome, never from `SetLevel`.
- Slot jobs persist accepted actor/userid and receipt state across reload; payout returns actual spawned reward.
- Gacha pill achievement is backed by an allowed first-grade pill reward, not a declared but impossible category.

- [ ] Write failing tests for gem consume, successful category threshold +3/+6, wildcard success count, protection consumption branches, compatible/incompatible level-scroll use, failed RPC/payment/spawn, two slot users, and reload during queued payout.
- [ ] Route gem spending only after `ConsumeByName`, success only after `DoSuccess` commits, protection only at actual consumption, and scroll only after a compatible item has changed. Treat `category="any"` as a wildcard success counter; treat +3/+6 objectives as a single committed level threshold.
- [ ] Retarget the unregistered `wb_strengthen_clearpaper` objective to the real level-paper zero-level (clear) outcome and revise its text/evidence accordingly; do not register a fake prefab or add assets that do not exist.
- [ ] Preserve the giver at `OnAccept`, persist actor/receipt with the slot job, emit one spin only after `Start` commits, and classify/route only the successfully spawned payout prefab. Advance receipt state before callbacks so load/retry cannot duplicate credit.
- [ ] Add one approved first-grade buff-pill bundle to the real slot prize data and explicitly classify existing prize rows as `pill`, `rare`, or `material`; keep fallback prize classification tied to the actual fallback spawn.
- [ ] Retitle/rebind the shop-restock achievement to the real stock-token restock transaction rather than claiming dungeon completion restocks inventory; route after `RestockOne` commits.
- [ ] Run all Task 17 cases, catalog totals, and source-registration audits; commit only Task 17 paths.

### Task 18: Acceptance Audit and Explicit External Seams

**Files:**
- Modify: `mods/PhamNhanTuTien/tools/test_achievement_reachability.py`
- Modify only if copy requires correction: `mods/PhamNhanTuTien/ACHIEVEMENT_PERK_RUNTIME.md`
- Modify: `.superpowers/sdd/2026-09-21-pham-nhan-achievement-alchemy-integration/progress.md`

- [ ] Add a validator that maps every active catalog tracker to at least one tested master-only route and fails for dead route types, with explicit exemptions only for the `TTK_SEASONAL_CLAIM_XP` configuration seam and unavailable perk source dependencies.
- [ ] Test seasonal configuration absent, zero, nonfinite, and positive: absent/invalid returns `xp_unavailable` without state change; a supplied positive configuration calls `hh_leveling:AddExp` once per idempotent claim. Do not set the tuning value in this change set.
- [ ] Re-run all focused Lua/Python tools, canonical wiki exporter check, wiki tests, webpack build, `git diff --check`, and route/import/obsolete-level searches. Record exact pass/fail counts and baseline limitations in the SDD ledger.
- [ ] Have a fresh reviewer verify every active achievement route, distinct evidence persistence, current-run attribution, no Levelsystem authority, catalog 231/1,000 and no dummy unavailable perk. Commit only audit/ledger/test documentation paths.

## Execution Boundary

The original user-approved execution method is subagent-driven development. Tasks 14–17 each require an implementer followed by a fresh reviewer; run their overlapping `ttk_achievement.lua` work sequentially. Task 18 is a whole-branch audit. The seasonal XP amount and missing upstream perk sources remain external deliverables, not reasons to invent implementation.

### Task 19: Canonical Alchemy Ingredient Resolution

**Files:**
- Modify: `mods/PhamNhanTuTien/tools/build_alchemy_defs.py`
- Modify: `mods/PhamNhanTuTien/scripts/alchemy/ttk_alchemy_defs.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_alchemy_catalog.py`
- Modify/create: `mods/PhamNhanTuTien/tools/test_alchemy_runtime.py`

**Interfaces:**
- The generator translates historical recipe-source prefab IDs to verified, registered Phàm Nhân runtime prefab IDs before emitting `ttk_alchemy_defs.lua`.
- The generated catalog remains an exact-recipe catalog; `ttk_alchemy_rules` does not accept an ambiguous alias at craft time.

- [ ] Build an explicit deterministic source-to-runtime map from the existing proven reward alias table and current prefab registrations. Cover every historical ingredient used by the 26 approved outputs; reject an unmapped historical ID during generation.
- [ ] Normalize only at generation. Preserve source JSON provenance but emit only current prefabs such as `ttk_lingshi*` and verified `ttk_*` boss/herb/material IDs.
- [ ] Replace the two unregistered stage-15 `_2` buff-pill ingredients with their approved first-grade `_1` variants. Do not register second-grade pills.
- [ ] Add a validator proving every generated ingredient is a registered/runtime-provided current prefab and no `xd_` historical ingredient remains. Include exact stage-15 regression and rerun every 26 recipe through `FindExactRecipe`.
- [ ] Regenerate deterministically, run alchemy/catalog/runtime/cultivation tests, then commit only Task 19 paths. A fresh reviewer must verify alias evidence and no fake prefab.

### Task 20: Final Native Correctness Fix Wave

**Files:**
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_catalog.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_achievement.lua`
- Modify: `mods/PhamNhanTuTien/main/ttk_alchemy.lua`
- Modify: `mods/PhamNhanTuTien/scripts/prefabs/ttk_alchemy.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/ttk_alchemy_effects.lua`
- Modify: `mods/PhamNhanTuTien/scripts/achievement/ttk_achievement_core.lua`
- Modify: affected native/Lupa tests under `mods/PhamNhanTuTien/tools/`

- [ ] Correct every active catalog condition that uses a nonexistent alias/general label to actual registered prefab evidence, and route the stump row by real stump tag rather than a fake `stump` prefab. Add a test that executes every corrected condition through its real adapter.
- [ ] Give achievement cooking a dedicated postinit flag, preserving the perk stewer hook and allowing both callbacks in runtime registration.
- [ ] Gate cultivation pills before `Eater` removes them using the native edible/action validation seam. Wrong-order, duplicate, and max-stage pills must not be consumed; valid ordered pills must consume once and advance once.
- [ ] Make health/sanity regeneration buffs retain deadlines and save/load duration; reload must not replay immediate health healing.
- [ ] Preserve a saved claimed reward exactly when valid, reconstruct earned Star from persisted awarded values, and only use catalog reward for unclaimed/missing legacy claim fields.
- [ ] Run native combined-registration, condition-level reachability, edible removal, effects save/load, historical reward, all focused suites, wiki export/build, then fresh whole-branch review.

### Task 21: Native Food and Seasonal Prefab Corrections

- [ ] Correct active food conditions to native `perogies` and `hotchili`, preserving achievement IDs/rewards/targets.
- [ ] Correct seasonal conditions to native `frogglebunwich`, `coldfirepit`, and `perogies`.
- [ ] Add executable eater/build/seasonal route tests that reject the obsolete IDs and advance only on the real native products.
- [ ] Regenerate the canonical wiki export, run catalog/seasonal/export/wiki checks, and send the five-ID diff to a scoped reviewer.

### Task 22: Seasonal Rollover Settlement

- [ ] Before replacing the seasonal pool, settle every outgoing ready task exactly once through the configured XP callback and settle each eligible unclaimed chest through the existing atomic reward grant path.
- [ ] Preserve correct outgoing-season identity after world state already changes; receipt keys must remain idempotent across a deferred refresh, load, or duplicate watcher event.
- [ ] If XP/reward settlement cannot commit, persist an outgoing settlement record and retry before starting a new pool; never silently discard a ready task or chest.
- [ ] Add executable native world-watcher rollover tests: five claimed tasks plus chest, one ready unclaimed task, configured/invalid XP, reward/preflight failure, retry/load, and duplicate season event.
