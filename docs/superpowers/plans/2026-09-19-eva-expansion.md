# EVA passive, harvest and Dạ Du implementation plan

> Use superpowers:subagent-driven-development with previously selected GPT-5.6 Sol High. Parent owns integration review and packaging. User approved the in-chat design; execute under existing authorization.

**Goal:** Add the approved two-hit melee passive and two targeted HUD abilities to standalone EVA v1.0.

**Architecture:** Server components own activation, costs and cooldown; isolated prefabs own projectiles/harvest/mark lifetimes. Extend existing owner-bound hidden book to five icons and preserve right-click Fox.

**Tech stack:** DST Lua5.1, installed scripts.zip, Python/Lupa scheduler and native-engine fixtures.

**Spec:** Approved in-chat design summarized below is the binding specification.

## Global constraints and rulings

- Every two valid successful weapon melee hits emit one sword wave; all weapon types including attacking with tools count, no unarmed/work/miss/ranged/skill/generated-hit counting. Free passive, no icon. Base damage50 from source Qi; purple crescent using existing art. Server hit event must distinguish melee and successful attack, no recursion. Partial counter resets on death/load.
- Harvest: point-targeted, cost3 Souls, CD10, duration7, radius8; harvest pickables, chop/mine, dig stumps only, gather loose objects to center without giving inventory. Exclude structures/traders/containers/held items; never uproot planted pickables or destroy protected plant infrastructure. Purple-silver wind FX reuse existing source assets. No unverified fire-extinguish claim. Point range12 chosen consistently with Array.
- Dạ Du: target selected at pointed enemy within12 (nearest valid within2 of point), projectile applies damage-taken multiplier1.10 for5s on impact, reapply refreshes without stacking across EVA casters. Cost5, CD15. Ruling: mark-only projectile, zero direct hit damage because none was approved; uses existing EVA scythe art. No refund after accepted cast if target dies/invalidates in flight. Invalid initial target costs nothing.
- Exactly five panel icons: life,wings,array,harvest,daydu. Fox remains RMB only. HUD tooltip/cooldown replicated; no new required hotkeys or inventory items. Existing G/H/J and all art/abilities intact.
- No cultivation/Tu Tiên runtime dependency, no original mod changes, no Steam write, no commit/publication. In-place authoritative mod is untracked alongside unrelated workspace changes, use full baseline backup rather than a worktree that would omit it.

## Review focus

- Native onattackother payload for ranged/projectiles and rejected hits; passive cannot trigger from skill damage or forge arbitrary client effects.
- Harvest operations can invalidate entities; safe iteration and no held/container/player-built objects or planted bush digging; finite range/map validation and owner lifetime.
- Debuff is source-owned, refresh-only, releases on expiry/removal/death, preserves foreign damage modifiers.
- Hidden book chosen spell and scoped busy authorization must match exact owner/action, including both new skill IDs and remote clients.
- Cooldown/cost acceptance atomic; cancellation/invalid destination free; malformed coordinates/save values bounded.

## Task 1: combat expansion

Own scripts/components/eva_melee_wave.lua, scripts/components/eva_daydu.lua, scripts/util/eva_combat_common.lua, scripts/prefabs/eva_combat_fx.lua; tests under mods/eva-assets-work/expansion/test_combat*. Do not edit shared files.

Interfaces: passive component auto-listens; daydu CastAt(x,z), GetCooldownRemaining(), Stop(reason), OnSave/OnLoad. Common exposes DAYDU_RANGE=12, DAYDU_COST=5, DAYDU_COOLDOWN=15. Prefab registration file eva_combat_fx. Consult existing eva_life_common target policy; reuse EVA source art. Tests must use native combat event evidence and real components.

- [x] Read native combat and original Chen Ping An Qi/Dạ Du source; write failing focused event, hit timing, mark ownership tests.
- [x] Implement two-hit counter and bounded projectile lifecycle with no attack-event recursion.
- [x] Implement validated point-to-target marking, cost/cooldown/save, 1.10/5s refresh-only modifier and cleanup.
- [x] Run Lua syntax and focused tests; report exact assets/interfaces/native findings.

## Task 2: harvest

Own scripts/components/eva_harvest.lua, scripts/util/eva_harvest_common.lua, scripts/prefabs/eva_harvest_fx.lua and tests test_harvest*. May add uniquely named standalone archive only if required, never edit existing art.

Interfaces: CastAt(x,z), GetCooldownRemaining(), Stop(reason), OnSave/OnLoad; range12,cost3,CD10. Controller Start(owner,x,z), owner callback cleanup. Source xd_jingwei_fan.lua plus brain in skill-audit/decoded; do not execute source mod.

- [x] Inspect source/native pickable/workable/inventory and write targeted lifecycle/charging/protected-object tests.
- [x] Implement 7s radius8 point vortex, harvest/work every0.5s and bounded item pull cadence; only appropriate objects, preserve original work drops.
- [x] Add lavender existing visual effects and safe expiration/death/remove/load cleanup; run tests.

## Task 3: panel and shared wiring

Own modmain.lua, modinfo.lua, scripts/prefabs/calliope_mori.lua, scripts/util/eva_skillpanel.lua, scripts/prefabs/eva_skillbook.lua, scripts/widgets/eva_skillpanel.lua, shared state if necessary, READMEs and existing impacted fixture expectations.

- [x] Extend existing native book to array,harvest,daydu point targeting, five explicit skill entries and correct server component routing.
- [x] Expand narrowly scoped CASTAOE authorization to exact context/selected book; register components/prefabs and two net_byte cooldowns.
- [x] Test three targeted branches, actual selected spell, invalid ownership/cancel, five icons/no Fox icon, correct net CD widths. Preserve state timeline of Fox.
- [x] Update user documentation for limits/controls and costs; run impacted fixtures.

## Task 4: parent review and package

- [x] Snapshot104-file mod and prior distribution before mutations.
- [x] Audit native APIs and implementer evidence, review actual combined flows and resolve findings.
- [x] Run all new and relevant old regressions, native probes and Lua syntax; no live game claim.
- [x] Record reviewed delta/hash, ensure original binary art unchanged, package ZIP with CRC/per-file parity, deliver concise Vietnamese result.
