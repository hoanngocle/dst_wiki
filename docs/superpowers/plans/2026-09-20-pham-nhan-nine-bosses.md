# Phàm Nhân 2.0 — nine bosses implementation

Spec: `docs/superpowers/specs/2026-09-20-tu-tien-ky-nine-bosses-design.md`.
Execution authorized by the user's request to finish integration and check the mod. Work directly in the renamed active mod `mods/PhamNhanTuTien`, preserving existing uncommitted integrations; historical `mods/TuTienKy` references in the spec resolve to that directory. Do not migrate identifiers or reimport Solo.

## Interfaces and tasks

1. Root owns `scripts/ttk_boss_defs.lua`: `{order={suffix,...}, bosses={[suffix]={name,prefab,unique,food,summon,stat,gain,effect}}}`. Nine main suffixes: baihu,jfsn,qlch,qxdx,futu,spiderqueen,ziyunboss,stalke_fuben,deerclops_ziyun. Only qxdx/futu/ziyunboss are unique. Six foods are `ttk_boss_core_<suffix>`, six summoning items `ttk_summon_<suffix>`.
2. Combat port owns source extraction, assets, brains, stategraphs, boss/support prefabs, helper/component dependencies and `main/ttk_boss_combat.lua`. It must keep source mechanics and supply complete dependency registration, and expose main `ttk_<suffix>` prefabs. It must not implement root loot, neutral behavior, registry or food progress. Helper entities never count as main bosses. Test compilation and transitive asset/prefab resolution before runtime.
3. Food implementation owns `scripts/components/ttk_bossprogress.lua`, `scripts/prefabs/ttk_boss_cores.lua`, `main/ttk_boss_food.lua` and its tests. Six per-player counts clamp to 10; permanent contributions (+4 true damage, +20 HP/mana/hunger/sanity, +2 flat defense per respective food) derive from counts without double application. At 10: baihu criticalHitRate +10, jfsn immuneHot, qlch immuneCold, spiderqueen immunePoison, stalke_fuben immunitySleep, deerclops_ziyun immuneFreeze. Every food restores base 50 health/75 hunger/50 sanity; no mana. Save/load, respawn and character transfer preserve count and prevent refresh exploits. Integrate actual Solo APIs rather than changing AP or original source.
4. Root owns registry/summoning/world lifecycle, neutrality, drop policies, final `main/ttk_bosses.lua`, modmain import, documentation. Registry spawns one main each on Master once, persists dead unique bosses, reconciles loaded GUIDs, excludes temporary helpers. Three unique bosses stay neutral until attacked. Six main bosses drop one food and one matching summon at final death, no phase/minion duplicates. Summoning consumes one only after successful spawn, rejects ocean/Caves/interior/living duplicate. Source reward items are retained where supported and explicitly documented; unsupported original item purposes remain recorded in BOSS_DROPS_VI.md, never silent gameplay stubs.
5. Integration audit owns independent existing-mod checks and runtime runner in a new `.superpowers/pham-nhan-boss-audit` world, not a player save. Check original integration/HUD tests and record unrelated changes separately. Then review and exercise merged feature.

## Test contracts

```lua
-- Progress: each kind is independent; food 11 cannot increase or retrigger the perk.
for i=1,11 do progress:Absorb("jfsn") end
assert(progress.counts.jfsn == 10)
assert(progress.counts.qlch == nil or progress.counts.qlch == 0)
-- Registry: a unique boss final death is terminal across save/load.
local data=registry:OnSave()
-- Reload state before deferred seeding; dead must never transition to unspawned.
-- Summon: duplicate/already-living boss failure preserves stack.
-- Runtime: spawn every main and support prefab; exercise damage, phase transitions,
-- drop 1+1, AI ticking, neutral approach, player provocation, save/restart.
```

## Review focus

- Source callbacks assuming owner/dungeon globals: standalone Hươu Một Mắt and Thượng Cổ Hắc Ám must operate without dungeon/owner.
- Shared minion prefab versus main: no duplicate unique rewards or repeated food drops from Tử Vân helpers.
- Solo recalculation/reset and equipment removing identical effects: permanent food bonus survives without inflation.
- World entity load ordering: no nine extra bosses on restart or retry after failed placement.
- Existing assets/code changed by other tasks: never replace them merely to make original byte-equality checks pass.

## Verification commands

Use bundled Python `C:/Users/hoanc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` and the existing Lua 5.1 runtime under `.superpowers/ttk-solo-integration/lua-runtime`. Run targeted newly added tests, `tools/test_ttk_solo_integration.py`, `tools/test_ttk_combat_hud.py`, and a separate offline DST smoke/restart against a copy of the active mod. Record server and client verification separately; headless cannot establish rendered appearance.

## Progress ledger

- Plan created. Existing nine bosses absent; integration and HUD already present. Parallel ownership has no shared writable files except the root-owned shared definitions, which are read-only inputs to workers.
- Shared definitions, world registry, summon action/items, final-death/neutrality hooks and duplicate-loot exclusion implemented. Root tests cover unique persistence, missing entities, minion exclusion, one-token consumption, failed setup rollback, portal clearance, one-time rewards and Tử Vân phase death.
- Food integration is implemented; review found and is correcting network counter width (0–10 requires more than a 3-bit tinybyte) and ambiguous maximum-stat recalculation. Tests are rerun after each correction; a prior green run is not treated as final acceptance.
- Combat dependency port is registered through `main/ttk_bosses.lua` at the end of modmain. Disposable runtime passed module registration/world generation after initial asset-name corrections. Server smoke, phase persistence and reference restoration remain under active audit.
- Gameplay instructions added to `mods/PhamNhanTuTien/BOSSES_VI.md`; `BOSS_DROPS_VI.md` records the agreed reward rules and will receive the verified source-drop mapping before completion.
- Review fixes completed: component `LoadPostPass` engine hook; RMB-only summon action; `net_smallbyte` counters; deterministic base-max handling with scoped Solo dungeon delta adapter; restoration of saved current vitals after max bonuses load; original save reference returns and helper-alive state; source namespace conversion only at identifier prefixes.
- Source-drop mapping and pending-purpose notes now documented for all nine bosses. Boss pointers explicitly track the nine main types and exclude helpers; previous indicator contracts remain green.
- Fresh root verification: 26/26 boss unit/contract checks, 5/5 HUD files, 568 Lua sources compile. Original Solo preservation suite remains 6/7 solely due to the pre-existing `anim/lo_ren.zip` hash difference; no source asset reverted or checksum baseline rewritten. Runtime server audit is still pending completion.


## Completion record

- Implementation and scoped reviews completed in the active Phàm Nhân directory. Nine natural main bosses, six summon tokens/foods, saved per-player bonuses and unique-boss lifecycle are registered.
- Final checks: 32/32 boss tests; 5/5 HUD test files; all 569 Lua files compile. Combat manifest has 96 Lua modules and 198 assets.
- Dedicated offline server create, reload and final-reload commands all exit 0. Nine natural spawns, 268 support prefabs, actual final drops, repeat Baihu summoning, food save/load, Ziyun phase restoration/final death and no resurrection on the second reload verified.
- The final source asset fix for HT was separately exercised in the reload pass; no missing-animation warning remains in that log. No connected graphical client was used.
- Baseline integration suite is now 5/7: existing lo_ren source-hash drift plus concurrent removal of the inventory-size configuration option in the Mod Config task. Preserve those unrelated changes; report them rather than rewriting assertions to hide the differences.
- Final report: `docs/superpowers/reports/2026-09-20-pham-nhan-boss-audit.md`. Gameplay and pending drop purposes: `mods/PhamNhanTuTien/BOSSES_VI.md`, `BOSS_DROPS_VI.md`.
