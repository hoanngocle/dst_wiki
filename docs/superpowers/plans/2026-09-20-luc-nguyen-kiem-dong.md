# Lục Nguyên Kiếm Đồng Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this coupled weapon feature task-by-task. User explicitly selected GPT-5.6 Sol with High reasoning and authorized execution; no additional approval checkpoint.

**Goal:** Ship the approved ranged weapon with six curved homing sword visuals and real Solo critical-triggered volleys.

**Architecture:** Keep gameplay math/motion in a testable Lua helper, rendering and entity lifecycle in prefabs, and registration/optional Solo compatibility in a mod entry file. One implementer owns these tightly coupled changes. Observe an explicit actual crit result; do not infer crit from damage magnitude, reroll math.random, or temporarily mutate global random/functions/components.

**Tech Stack:** DST Lua 5.1, Klei ANIM/KTEX assets, Python/Pillow/Lupa for asset inspection and testing.

**Spec:** docs/superpowers/specs/2026-09-20-luc-nguyen-kiem-dong.md

## Global constraints
All values and asset mappings in the spec are binding. Existing user work remains intact. No edits to source mods, no automatic client launch/deployment. Use local assets only. Keep Solo optional and use per-shot state to handle overlapping shots correctly.

## Review focus
1. Simultaneous in-flight primary shots, changed equipment, two attackers: crit and base damage must belong to the correct shot/target.
2. Auxiliary hits: exactly once, retain defenses/kill credit, never reapply Solo crit or recursively generate swords.
3. Target/owner dies, disappears, teleports, or becomes invulnerable: terminate safely with bounded lifetime and no leaked tasks.
4. Last charge, rapid shots, refill from a stack, full refill rejection, save/load: exactly one charge per shot and one stone per refill.
5. Dedicated server/client and Solo disabled/enabled: registered assets resolve; client never runs authoritative damage; normal shooting remains usable without Solo.

## Source evidence and tools
- TuTienKy entry: `mods/TuTienKy/modmain.lua`, convention `main/ttk_tinhlakiem.lua`, `scripts/prefabs/ttk_tinhlakiem.lua`.
- Existing damage carrier: `scripts/ttk_weapon_damage.lua` preserves numeric weapon.damage for wb_strengthen.
- Solo: `mods/mod_steam/3780347550/scripts/components/hh_player.lua`, `DoAttackDamage` around line 676, crit branches around 750–795. `main/hh_api.lua` around 937 invokes DoAttackDamage inside Combat:GetAttacked before mitigation. Multiple named critical branches exist. Inspect current code before choosing the smallest reliable optional adapter; do not equate any damage boost with crit. A wrapper that only sees the final number is insufficient.
- Lục Mạch: `scripts/prefabs/lucmachthankiem.lua` (obfuscated one-line code): launch, launch_jab, launch_slash use initial sideways velocity and target-position steering. Existing effect assets may be reused but its autonomous attack/state graph should not be copied wholesale.
- Decoded older source for inspection: `mods/eva-assets-work/skill-audit/decoded/scripts/prefabs/xd_jingwei_blowdart.lua`; source 19.7 Lua is encoded, original assets are usable. Existing port scripts show extraction tooling.
- Python: `C:/Users/hoanc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
- Existing test runtime: `.superpowers/vinhhang-runtime`, used by `mods/TuTienKy/tools/test_weapon_solo.py`; load Lupa lua51. If unreadable, use an accessible existing runtime or install only into workspace scratch.
- Real DST scripts zip: `C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`.
- KTEX decoder: `tools/extract/publish_solo_leveling_assets.py:decode_ktex`.

## Task 1 — Pure volley rules and steering
**Files:** create `mods/TuTienKy/scripts/ttk_lucnguyen_rules.lua`; create `mods/TuTienKy/tools/test_lucnguyen.py`.
**Interfaces:** `Rules.RollVolley(base_damage, random)` returns array `{element=1..6, damage=number}`; `Rules.Step(x,z,heading,target_x,target_z,dt,speed,turn_rate)` returns new x,z,heading. Angles are radians. Inject random for deterministic tests; inclusive integer rolls.
- [ ] Write and run failing tests before implementation. Examples:
```lua
local low = Rules.RollVolley(100, function(lo, hi) return lo end)
assert(#low == 1 and low[1].damage == 10)
local high = Rules.RollVolley(100, function(lo, hi) return hi end)
assert(#high == 6)
local seen = {}
for _, shot in ipairs(high) do
  assert(shot.damage == 50 and not seen[shot.element])
  seen[shot.element] = true
end
```
- [ ] Implement unbiased selection without replacement and independent percent rolls. Keep percentages pre-crit and immutable after launch.
```lua
local pool = {1,2,3,4,5,6}
local count = random(1,6)
local volley = {}
for i = 1,count do
  local pick = random(1,#pool)
  volley[i] = {element=table.remove(pool,pick), damage=base_damage*random(10,50)/100}
end
```
- [ ] Test moving-target steering with dt 1/30 and different initial fan angles, shortest-angle wraparound, arrival detection without overshoot, and finite timeout. Implement bounded angular turn, not a static endpoint Bezier which misses moving targets.
- [ ] Run Lua tests and record results.

## Task 2 — Weapon, assets, crit adapter, and projectile lifecycle
**Files:** create `scripts/prefabs/ttk_lucnguyenkiemdong.lua`, `scripts/ttk_lucnguyen_combat.lua`, `main/ttk_lucnguyenkiemdong.lua` under TuTienKy; modify modmain.lua; add dedicated namespaced assets under anim and images/inventoryimages; create `tools/port_lucnguyen_assets.py` if transformations are required.
**Interfaces:** primary projectile stores owner, weapon, precrit damage snapshot and shot token; successful actual critical hit invokes `LaunchVolley(owner,target,base_damage)`. Auxiliary entities hold immutable damage and element, and finish exactly once. Keep adapter functions isolated so real Solo integration can be tested without render stubs.
- [ ] Back up touched existing files to feature-specific workspace scratch. Inspect bank/build/symbol metadata of all selected archives, not just inventory icons. Verify original dart weapon normally consumes itself; replace that behavior with persistent charged weapon.
- [ ] Write failing tests for primary normal/critical hits, duplicate events, concurrent shots, missed/dodged hits, secondary non-recursion, last charge and stack refill. Use real Solo DoAttackDamage/Combat:GetAttacked where possible, not only fake crit events.
- [ ] Implement an optional, narrowly scoped actual crit observer compatible with installed Solo, without modifying Solo files. If a direct hook is unavailable, find a proven call-local observation point and document the exact compatibility limitation; do not silently substitute a separate random chance. Ensure the damage basis excludes critical multipliers and auxiliary attacks bypass offensive rerolls but preserve victim mitigation.
- [ ] Implement server-owned primary shot and six auxiliary visual prefabs. Emit swords at owner position, fan toward both sides, continuously steer to live target and use swept arrival checks. Bound life and range; remove tasks and FX when invalid.
- [ ] Implement 50 numeric base damage, range 8, 1,000 finite uses, empty retained/non-shootable state, stone repair +100 with capped uses, and save/load consistency. Numeric damage remains compatible with wb_strengthen.
- [ ] Register independent craft recipe and Vietnamese name/description. Server authority follows:
```lua
inst.entity:AddNetwork()
inst.entity:SetPristine()
if not TheWorld.ismastersim then return inst end
```
- [ ] Run feature tests plus `mods/TuTienKy/tools/test_weapon_solo.py`. Check deterministic crit at 0/100%, proc amount bounds and no buff recursion. Confirm all dependencies resolve with original Tu Tien disabled.

## Task 3 — Integration verification and documentation
**Files:** update `mods/TuTienKy/README_VI.md`, `mods/TuTienKy/CREDITS.md`, feature tests and a feature verification report under docs/superpowers/reports. If supported without unrelated UI changes, update `tools/build_tu_tien_ky_web.py` and regenerate existing TuTienKy data/icons to include the new item.
- [ ] Validate recipe, PrefabFiles, atlas element names, animation banks/builds and Lua 5.1 syntax. Run `mods/TuTienKy/tools/audit_registration.py` if compatible with current mod.
- [ ] Exercise a dedicated/headless server spawn-and-hit test if current harness permits; do not auto-open the client. Capture actual command/output and distinguish existing failures from feature failures.
- [ ] Document normal behavior without Solo, exact base-damage definition, charges/repair, random ranges, six asset credits, no elemental debuffs, and visual QA not yet performed if no client render is available.
- [ ] Self-review only feature diff and assets; return changed-file manifest, exact passing checks, known limitations, and no unverified success claims. Do not commit the untracked mods tree or unrelated working changes.

## Handoff
User requested a Sol High implementer explicitly. Parent coordinates and reviews the finished implementation while the implementer performs all three coupled tasks. Use the approved spec to resolve ordinary choices without further confirmation. If a fundamental crit integration blocker is found, report concrete evidence promptly instead of shipping fake crit behavior.
