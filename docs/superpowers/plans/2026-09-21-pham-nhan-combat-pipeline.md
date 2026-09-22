# Phàm Nhân Combat Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the inherited Solo combat hooks with one deterministic, testable Phàm Nhân combat pipeline that implements every approved Mục 2 rule without changing historical source mods.

**Architecture:** Pure math and scoped hit-context modules own probability, caps, damage packets, and per-hit metadata. `Combat:GetAttacked` remains the single orchestration boundary: it checks dodge before offensive rolls, resolves Phàm Nhân modifiers, then delegates armor/resistance and HP mutation to DST. Post-hit effects consume the resolved primary-hit context and cannot recursively create unauthorized procs.

**Tech Stack:** Don't Starve Together Lua 5.1 APIs, Python 3 `unittest`, `lupa.lua51`, dedicated-server smoke tests, CodeGraph CLI.

**Spec:** `PHAM_NHAN_SOLO_AUDIT_HANDOFF.md`

## Global Constraints

- The current mod is **Phàm Nhân Tu Tiên 2.0**; use **Phàm Nhân** in user-facing copy and keep existing `ttk_`/`hh_` identifiers.
- Work only in `mods/PhamNhanTuTien`, its tests/tools, and this plan/spec. Never edit `mods/3780347550`, `mods/2937640068`, or `mods/AchievementLevel`.
- The standalone Solo source has already been integrated; do not add it as an optional dependency.
- Fresh-save only: do not add save migration or compatibility conversion for removed effects/sets.
- Player combat is solo-balanced. Do not add party sharing, nearby-player healing, or group scaling.
- Preserve vanilla DST armor, resistance, redirect, mount, planar, invincibility, death, and event behavior by delegating the final packet to the original `Combat:GetAttacked`.
- Phàm Nhân reduction is one percentage pool capped at `80%`; vanilla armor remains separate, so two `80%` layers may produce `96%` total reduction.
- Dodge uses exactly one roll capped at `70%`, occurs before crit/Bạo Phát, and a dodge consumes no offensive proc.
- Crit uses `x(2 + criticalHitEffect / 100)`, chance clamped to `0..100`, no overcrit. Bạo Phát is an independent weapon-only roll with exactly one tier per weapon: I `30% x1.5`, II `20% x2`, III `10% x3`, IV `8% x5`.
- Xuyên Giáp is an additional percentage true-damage packet calculated from the primary hit after base flat/percentage bonuses but before crit and Bạo Phát: STR contributes at most `20%`, weapon tier contributes `3–5/6–10/11–15/16–20%`, combined cap `40%`.
- Targets with `immuneTrue` remain immune to the Xuyên Giáp packet. As approved true damage, Xuyên Giáp bypasses the target player's Phàm Nhân reduction pool and normal physical armor. Existing non-armor DST defenses and explicit monster defenses remain independently owned by their systems.
- Nghịch Cảnh keeps exactly one of `bloodOutburst`, `spiritFade`, or `hungerAssault` per weapon. Its bonus is `50% * missing resource ratio`, capped at `+50%`, reads the attacker's resource, and joins the pre-crit percentage pool.
- Hút Máu uses actual HP lost, has a per-event cap of `15%` attacker max HP and a rolling one-second cap of `90%` attacker max HP. It excludes Trọng Thương, Độc, Kết Liễu, true/%HP packets, and unrelated damage.
- Trọng Thương deals `3%` target current HP to normal mobs and `1%` to bosses; it cannot crit, Bạo Phát, lifesteal, or recursively proc.
- Trọng Thương remains subject to Phàm Nhân reduction and vanilla armor and is blocked by `immuneTearing`. Kết Liễu keeps its `15%` threshold for non-boss monsters only.
- Hạ Độc is a weapon-only one-tier affix with chances I `10%`, II `20%`, III `30%`, IV `40%`. A direct primary hit adds one stack, maximum five; all stacks refresh to `10s`; ticks are every `2s`; each stack deals `20%` of the triggering primary hit before crit/Bạo Phát; poison bypasses normal armor and cannot crit, Bạo Phát, Xuyên Giáp, Trọng Thương, Kết Liễu, lifesteal, or proc other effects.
- Giảm Hồi Máu reduces healing by `90%` for `5s`, refreshes but does not stack, works on bosses, and is applied only by a direct primary hit. Canonical source `addSuppressAddHealth`: Chu Tước-TĐ `10–50%`, ★Chu Tước-TM `100%`.
- Đóng Băng is weapon-only I `5%`, II `10%`, III `15%`, IV `20%`; direct primary only; normal targets freeze `2s`; bosses slow `20%` for `2s`; target ICD `5s`.
- Siêu★Lan is `20%` per gem capped at `60%`, radius `3`, based on the primary hit after Công Kích/crit/Bạo Phát but before the primary target's armor. Secondary targets use their own armor. Splash does not roll crit/Bạo Phát or apply status/procs; its actual damage may grant Hút Máu.
- Kết Liễu evaluates after the landed hit, never executes bosses, and must respect death-threshold prevention.
- Attack speed tiers are I `5–10%`, II `15–25%`, III `30–45%`, IV `50–70%`, weapon-only and one tier; total Phàm Nhân attack-speed bonus cap `+100%` (`x2`).
- Move speed keeps Nhanh Nhẹn weapon `5–25%` plus existing gem sources `+3%` and `+6%`; Phàm Nhân pool cap `+50%`; vanilla multipliers remain independent.
- Remove `soakStrike`, conditional time/species flat damage, custom reflection, sanity shield, Ban Phúc, Hồi Não, Đá Sát Thương, player Giáp Đốt, player Giáp Băng, player legacy poison keys, typo `atkSpeedatkSpeed`, and sets Bạch Hổ Thiên Cương/Phi Vân Dật Ảnh/Thánh Quang Tí Hựu exactly as specified in the handoff.
- Retain monster poison/freeze systems for their later dedicated audit. Do not remove monster-owned behavior merely because the player equivalent is removed.
- Preserve unrelated dirty-worktree changes. Before every edit, re-read the target file and `git diff -- <file>`; never reset, clean, checkout, or stage broadly.

## Review Focus

- Missing `health`, dead attacker, dead target, invalid/nonnumeric/negative damage, and removed entities must return safely without dereferencing `nil`; Task 2 pins this.
- Nested or simultaneous projectile hits must keep their own crit/Bạo Phát/base-damage context and never claim another hit's metadata; Tasks 1 and 2 pin this.
- A dodged hit must not consume RNG for crit, Bạo Phát, poison, freeze, or Giảm Hồi Máu; Task 2 pins this.
- Xuyên Giáp true damage bypasses the target player's Phàm Nhân reduction pool and normal physical armor, but not invincibility, explicit non-armor DST defenses, redirect, or death-threshold guards; the corrective integration task pins this.
- Multi-target splash and poison ticks must not recursively trigger splash/status/Trọng Thương/Kết Liễu, while permitted splash lifesteal still obeys both caps; Task 3 pins this.

---

## File Structure

### New files

- `mods/PhamNhanTuTien/scripts/combat/hh_combat_math.lua` — pure clamps, percentage rolls, outgoing multipliers, pre-crit Xuyên Giáp packet calculation, reduction, and lifesteal-budget math.
- `mods/PhamNhanTuTien/scripts/combat/hh_combat_context.lua` — scoped per-hit stack keyed by attacker/target, safe for nested callbacks and simultaneous projectiles.
- `mods/PhamNhanTuTien/scripts/combat/hh_combat_status.lua` — nonpersistent poison, healing-reduction, freeze/slow, ICD, splash, and packet-origin rules.
- `mods/PhamNhanTuTien/tools/test_combat_math.py` — pure boundary and arithmetic tests.
- `mods/PhamNhanTuTien/tools/test_combat_pipeline.py` — hook order, guard, RNG, armor, reduction, and context integration tests.
- `mods/PhamNhanTuTien/tools/test_combat_status.py` — poison/status/splash/lifesteal/execute tests.
- `mods/PhamNhanTuTien/tools/test_combat_catalog.py` — affix range, equipment restriction, removed-key/set, attack-speed, and move-speed tests.
- `mods/PhamNhanTuTien/tools/combat_smoke.lua` — in-engine deterministic player-versus-normal and player-versus-boss scenarios.
- `tools/run_phamnhan_combat_smoke.py` — isolated dedicated-server smoke runner.

### Existing files modified

- `mods/PhamNhanTuTien/main/hh_api.lua` — install the ordered combat hook, define the armor-piercing special packet type, remove old true-damage injection, and base lifesteal on resolved HP loss.
- `mods/PhamNhanTuTien/scripts/components/hh_player.lua` — safe guards, primary outgoing calculation, dodge API, capped speed/reduction access, and removal of obsolete event branches.
- `mods/PhamNhanTuTien/scripts/components/hh_monster.lua` — correct crit roll helper use without changing monster-only status behavior.
- `mods/PhamNhanTuTien/scripts/components/hh_leveling.lua` — change STR and VIT stat contributions from flat values to the approved percentage semantics.
- `mods/PhamNhanTuTien/scripts/utils/hh_utils.lua` — attack-speed cap and shared safe living-entity checks.
- `mods/PhamNhanTuTien/scripts/enums/hh_effects.lua` — canonical player effect registry and removed keys.
- `mods/PhamNhanTuTien/scripts/enums/hh_enchant.lua` — exact tier ranges, weapon restrictions, exclusivity groups, gems, removed sources, and set deletion.
- `mods/PhamNhanTuTien/scripts/enums/hh_buff.lua` — remove player-obsolete buffs and keep monster-owned buffs.
- `mods/PhamNhanTuTien/main/hh_tunning.lua` — canonical Vietnamese names/descriptions and removal of deleted set/effect copy.
- `mods/PhamNhanTuTien/scripts/components/hh_equip.lua` — enforce weapon-only and one-tier affix groups during roll/add/inherit operations.
- `mods/PhamNhanTuTien/scripts/components/hh_dungeon_effects.lua` — keep dungeon bonuses inside the same capped combat pools.
- `mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua` — remove obsolete combat-effect awards without changing dungeon authority.
- `mods/PhamNhanTuTien/scripts/enums/hh_items.lua`, `hh_monster.lua`, and `hh_treasure_monster.lua` — remove obsolete player acquisition/drop paths while preserving approved monster poison/freeze behavior.
- `mods/PhamNhanTuTien/main/hh_sg.lua` — keep animation attack-speed reads on the single capped `atk_speed` key.
- `mods/PhamNhanTuTien/tools/test_ttk_solo_integration.py` — include new files and deleted-source assertions in the full integration gate.
- `mods/PhamNhanTuTien/README_VI.md` and `mods/PhamNhanTuTien/Wiki.txt` — final player-facing combat rules after code is green.

---

### Task 1: Deterministic Combat Math and Scoped Hit Context

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/combat/hh_combat_math.lua`
- Create: `mods/PhamNhanTuTien/scripts/combat/hh_combat_context.lua`
- Create: `mods/PhamNhanTuTien/tools/test_combat_math.py`

**Interfaces:**
- Produces: `Math.Clamp(value, low, high)`, `Math.RollPercent(rate, rng)`, `Math.ResolvePrimary(base, flat, percent, crit_rate, crit_effect, burst, rng)`, `Math.CalculateArmorPierce(pre_crit_damage, percent)`, `Math.ApplyReduction(damage, percent)`, `Math.TakeLifestealBudget(state, now, requested, max_health)`.
- Produces: `Context.Begin(attacker, target, data) -> token`, `Context.Current(attacker, target) -> data|nil`, `Context.Finish(token) -> data|nil`, `Context.WithPacket(kind, fn, ...)`, `Context.PacketKind() -> string|nil`.

- [x] **Step 1: Write failing pure-math and context tests**

Create a Python `unittest` harness using the repository's bundled `lupa.lua51`. Use literal expected values and assert:

```python
self.assertEqual(resolve(base=100, flat=20, percent=50, crit_roll=1,
                         crit_rate=100, crit_effect=150,
                         burst_roll=8, burst_chance=8, burst_mult=5), 3150)
self.assertEqual(calculate_pierce(pre_crit=1000, percent=40), 400)
self.assertEqual(apply_reduction(1000, 95), 200)       # pool caps at 80%
self.assertEqual(roll_percent(0, 1), False)
self.assertEqual(roll_percent(1, 1), True)
self.assertEqual(roll_percent(1, 2), False)
self.assertEqual(roll_percent(100, 100), True)
self.assertEqual(take_budget(now=10, requested=500, max_hp=1000), 150)
self.assertEqual(take_budget(now=10.5, requested=800, max_hp=1000,
                             already=850), 50)
```

Add nested-context assertions: outer hit A→X, inner hit A→Y, finishing inner restores A→X; finishing tokens out of order must not leak or return another hit's data.

- [x] **Step 2: Run tests and verify RED**

Run:

```powershell
python mods/PhamNhanTuTien/tools/test_combat_math.py -v
```

Expected: FAIL because both combat modules are absent.

- [x] **Step 3: Implement the minimal pure modules**

`RollPercent` must call the supplied `rng(1, 100)` exactly once only when the clamped chance is greater than zero and lower than 100; return immediately for 0 and 100. `ResolvePrimary` must calculate `(base + flat) * (1 + percent/100)`, then independently apply crit and the supplied single Bạo Phát tier. Return a record containing `pre_crit`, `final`, `critical`, `critical_multiplier`, `burst`, and `burst_multiplier`.

`CalculateArmorPierce` clamps the percentage to `0..40` and returns `pre_crit_damage * p` as an additional `hh_armor_pierce` packet; it never subtracts from the normal hit and never reads the post-crit/post-Bạo Phát total. `ApplyReduction` clamps to `0..80`. `TakeLifestealBudget` starts a new one-second window when `now - state.started_at >= 1`, then returns the minimum of requested amount, `15%` max HP per event, and remaining `90%` max HP in the current window.

Implement context as a stack of opaque tokens, never as one global boolean. `WithPacket` must restore the previous packet kind even when `fn` errors by using `xpcall` and rethrowing the original error.

- [x] **Step 4: Run tests and verify GREEN**

Run the focused test, then the existing Luc Nguyên context regression:

```powershell
python mods/PhamNhanTuTien/tools/test_combat_math.py -v
python mods/PhamNhanTuTien/tools/test_lucnguyen.py
```

Expected: all tests pass; no warnings or leaked context.

---

### Task 2: Ordered Primary-Hit Pipeline, Guards, Dodge, Crit, Penetration, and Defense

**Files:**
- Create: `mods/PhamNhanTuTien/tools/test_combat_pipeline.py`
- Modify: `mods/PhamNhanTuTien/main/hh_api.lua:695-875,904-1035`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_player.lua:677-925`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_monster.lua:880-925`
- Modify: `mods/PhamNhanTuTien/scripts/utils/hh_utils.lua:340-374`

**Interfaces:**
- Consumes: Task 1 math/context APIs.
- Produces: `HHPlayer:TryDodge(attacker, rng) -> boolean`, `HHPlayer:ResolvePrimaryHit(target, damage, weapon, rng) -> normal_damage, pierce_damage, metadata`, where normal damage is the full post-crit/post-Bạo Phát hit and piercing damage is additional damage derived only from `metadata.pierce_base`; `HHPlayer:GetPhamNhanReduction() -> number`.
- Maintains: original `Combat:GetAttacked(attacker, damage, weapon, stimuli, spdamage, ...)` return semantics.

- [x] **Step 1: Write failing pipeline tests**

Build real Lua component instances with small DST stubs and literal assertions for:

```text
missing attacker health -> original damage returned, no crash
dead attacker or target -> no Phàm Nhân proc, no crash
dodge 70%, roll 70 -> original Combat:GetAttacked not called
dodge 70%, roll 71 -> hit continues
dodged hit -> RNG trace is ["dodge"] only
crit 1%, roll 1 -> crit; roll 2 -> no crit
player, hh_monster, and shadow-follower crit all share the same boundaries
100 base, crit x3.5, Bạo Phát IV x5 -> 1750 before mitigation
1000 pre-crit outgoing, 40% pierce -> original receives the full normal hit + 400 hh_armor_pierce
100 base, crit x3.5, Bạo Phát IV x5, 40% pierce -> 1750 normal + 40 hh_armor_pierce, never 700 pierce
1000 incoming, 80% Phàm Nhân reduction, 80% vanilla armor -> 40 HP lost
world-rank x2 changes both normal and pierce once, never twice
redirect/invincible/planar/death-threshold behavior remains owned by original Combat
```

- [x] **Step 2: Run tests and verify RED**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
```

Expected: guard nil crash or order assertion failure; current crit boundary also fails at `1%`.

- [x] **Step 3: Reorder the hook and use the pure math contract**

In the `Combat:GetAttacked` wrapper, perform these phases exactly once:

```lua
-- 1. validate numeric damage and living attacker/target
-- 2. target.hh_player:TryDodge(attacker) and return false immediately on dodge
-- 3. resolve attacker player/monster/follower outgoing damage and metadata
-- 4. add player Xuyên Giáp from pre-crit damage as hh_armor_pierce spdamage; keep the full normal hit
-- 5. apply target Phàm Nhân reduction to normal and packet types that permit it; true-damage hh_armor_pierce bypasses this player pool
-- 6. apply follower modifiers and world-rank exactly once
-- 7. call original Combat:GetAttacked so DST owns armor/resistance/redirect/HP/events
```

Register `hh_armor_pierce` once through `require("components/spdamageutil").DefineSpType` with zero intrinsic attacker damage and zero defense. Merge it into a copied `spdamage` table; never mutate a caller-owned table.

Before adding the packet, return zero piercing damage when the target's `hh_monster` has `immuneTrue`. The target player's Phàm Nhân percentage reduction applies to normal damage but not `hh_armor_pierce`; normal physical armor is also bypassed. Crit and Bạo Phát multiply the normal hit but must never multiply the Xuyên Giáp packet.

Replace both unsafe guards with explicit safe checks using `or`. Remove dodge, `suit_fyyy`, sanity shielding, reflection, flat reduction, and `suit_bhtg` damage amplification from `GetBlockDamage`; the method may remain as a compatibility shim that applies only the approved percentage pool until all callers use the new helper.

Use `Math.RollPercent` for player, `hh_monster`, and `ApplyFollowerCritical`. Crit and Bạo Phát metadata must be written to the current hit token, not shared fields.

- [x] **Step 4: Remove the old double-reduction and flat true-damage paths**

Delete the `Health:DoDelta` VIT flat subtraction and the `onhitother` `DoHHDelta(-trueDamageNum)` branch. Keep `DoHHDelta` for explicitly tagged true/%HP packets used elsewhere; Xuyên Giáp no longer calls it.

- [x] **Step 5: Verify GREEN and regressions**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
python mods/PhamNhanTuTien/tools/test_lucnguyen.py
python tools/test_ttk_combat_hud.py
```

Expected: all pass; Luc Nguyên still observes the real crit result and the HUD still displays actual resolved damage.

---

### Task 3: Post-Hit Status Packets, Splash, Execute, and Lifesteal Budgets

**Files:**
- Create: `mods/PhamNhanTuTien/scripts/combat/hh_combat_status.lua`
- Create: `mods/PhamNhanTuTien/tools/test_combat_status.py`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_player.lua:291-402,797-842,911-925`
- Modify: `mods/PhamNhanTuTien/main/hh_api.lua:695-875,937-1035`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_buff.lua`

**Interfaces:**
- Consumes: Task 1 hit metadata and packet-kind context; Task 2 actual `damageresolved`.
- Produces: `Status.AfterPrimary(metadata, resolved)`, `Status.ApplyPoison(attacker, target, pre_crit_damage)`, `Status.ApplyHealReduction(target)`, `Status.ApplyFreezeOrSlow(target)`, `Status.ApplySplash(metadata)`, `Status.TryExecute(attacker, target)`.

- [x] **Step 1: Write failing status tests**

Use a fake scheduler clock and literal cases:

```text
poison chance success adds one stack; five further hits cap at five
any successful reapplication refreshes every stack to 10 seconds
one stack from pre-crit 100 deals 20 at t=2,4,6,8,10; five stacks deal 100 each tick
poison packet bypasses armor and never increases lifesteal or causes another proc
healing reduction changes +100 healing to +10 for 5 seconds and refreshes without stacking
normal target freezes 2 seconds; boss receives 0.8 speed multiplier for 2 seconds
freeze/slow target ICD blocks retrigger until 5 seconds
splash 60% from pre-mitigation primary 1000 sends 600 to each eligible target in radius 3
secondary target armor applies independently; player/companion/structure/wall exclusions remain
splash never creates splash/status/heavy-wound/execute recursion
3% normal and 1% boss Trọng Thương use current HP at trigger time
Kết Liễu never kills a boss and does not override death-threshold prevention
lifesteal on 10,000 resolved damage with 1,000 max HP heals 150 for that event
six further events in the same second stop at 900 total; next second resets the window
```

- [x] **Step 2: Run tests and verify RED**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_status.py -v
```

Expected: FAIL because the status module is absent and legacy poison/splash recursively use `Combat:GetAttacked` without packet metadata.

- [x] **Step 3: Implement packet-origin-safe post-hit processing**

Call `AfterPrimary` only after the original combat method has produced a landed primary event with positive actual HP loss. Each auxiliary packet must run inside `Context.WithPacket(kind, fn)` using one of `heavy_wound`, `poison`, `splash`, or `execute`. `AfterPrimary` must return immediately when `Context.PacketKind()` is non-`nil`.

Poison stores transient per-target state with `stacks`, `damage_per_stack`, `expires_at`, and one periodic task. A new stack captures `20%` of that hit's `pre_crit` damage; existing stacks keep their own captured value; refresh changes expiry only. Every tick sums active stack values and sends one `hh_poison` special packet through the original combat method: Phàm Nhân reduction and invincibility still apply, normal armor does not, and packet context blocks every player proc.

Giảm Hồi Máu uses the existing player/monster health-suppression buff names only as the runtime carrier, with one canonical `90%` multiplier and `5s` duration. Remove the legacy `healthSuppressNum` chance branch from outgoing math.

For boss detection, first use `hh_monster:GetMonsterType()` and treat `boss_monster`/`endgameboss_monster` as bosses; then fall back to the integrated boss registries already used by execute logic. Do not infer boss status from max HP.

Trọng Thương calls original combat through a `heavy_wound` packet context so the target's Phàm Nhân reduction and vanilla armor apply. It must return without damage for `immuneTearing`, and its context prevents crit/Bạo Phát/Xuyên Giáp/status/splash/execute/lifesteal.

Splash calls original combat through a packet context so each secondary target gets vanilla armor but no player offensive proc. Feed each positive `damageresolved` to the permitted lifesteal budget. For a primary packet containing `hh_armor_pierce`, compute eligible lifesteal from the actual HP loss apportioned to the post-defense normal portion; never heal from the piercing portion.

- [x] **Step 4: Replace old listeners and resolved-damage healing**

Reduce the old `onhitother` listener to one call into `Status.AfterPrimary`; delete its legacy player poison, flat Xuyên Giáp, direct freeze, and splash blocks. Replace `HandleBloodSuck(raw_delta)` with a method that receives actual positive damage plus packet kind, checks the allowlist `{primary=true, splash=true}`, and asks `Math.TakeLifestealBudget` before healing.

- [x] **Step 5: Verify GREEN**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_status.py -v
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
python mods/PhamNhanTuTien/tools/test_weapon_solo.py
```

Expected: all pass with no auxiliary-proc recursion.

---

### Task 4: Canonical Affix Catalog, Equipment Restrictions, Speeds, and Deletions

**Files:**
- Create: `mods/PhamNhanTuTien/tools/test_combat_catalog.py`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_leveling.lua`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_effects.lua`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_enchant.lua`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_buff.lua`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_items.lua`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_monster.lua`
- Modify: `mods/PhamNhanTuTien/scripts/enums/hh_treasure_monster.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_equip.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_dungeon_effects.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/dungeon_manager.lua`
- Modify: `mods/PhamNhanTuTien/scripts/components/hh_player.lua:275-290,1980-2000`
- Modify: `mods/PhamNhanTuTien/scripts/utils/hh_utils.lua:68-80`
- Modify: `mods/PhamNhanTuTien/main/hh_sg.lua`
- Modify: `mods/PhamNhanTuTien/main/hh_tunning.lua`

**Interfaces:**
- Produces equipment metadata fields: `slot="hand"` and `exclusive_group` values `burst`, `armor_pierce`, `adversity`, `dragon_damage`, `poison`, `freeze`, and `attack_speed`.
- Preserves old internal IDs where the handoff explicitly requires them, including `special_bhtg` as ★Thanh Long IV.

- [x] **Step 1: Write failing catalog tests**

Load the real registries and assert exact ranges, restrictions, and deletions:

```text
Bạo Phát I..IV = (30,1.5),(20,2),(10,3),(8,5), hand-only, one burst group
Xuyên Giáp I..IV ranges = 3–5,6–10,11–15,16–20, hand-only, one group
Nghịch Cảnh = bloodOutburst/spiritFade/hungerAssault, hand-only, one group, max +50%
Thanh Long I..IV = 3–5,6–10,11–15,16–20% main-hit damage, hand-only, one group
Hạ Độc I..IV chances = 10,20,30,40, hand-only, one group
Đóng Băng I..IV chances = 5,10,15,20, hand-only, one group
Liên Kích I..IV ranges = 5–10,15–25,30–45,50–70, hand-only, one group
Nhanh Nhẹn weapon range = 5–25; speed gems remain +3 and +6
Bảo★Sát = +15%; Siêu★Sát = +20%; attack gems may coexist
Siêu★Lan = +20% each and runtime cap 60%
deleted keys/sources/recipes/sets are absent; monster poison/freeze keys remain
attempting a second affix from one exclusive group is rejected without consuming the item
inherit/refresh cannot move a hand-only affix onto body/head equipment
attack-speed helper caps bonus at 100%; move-speed application caps Phàm Nhân pool at 50%
```

- [x] **Step 2: Run tests and verify RED**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_catalog.py -v
```

Expected: FAIL on old ranges, missing `moreDamage30To150`, missing exclusivity metadata, typo key, and deleted set/effect entries still present.

- [x] **Step 3: Rewrite the canonical player catalog**

Add `moreDamage30To150` to the player registry and rename the four displayed lines to `Bạo Phát I–IV`. Keep all four historical effect IDs to avoid breaking internal references, but expose exactly one per weapon through the `burst` exclusive group.

Convert `trueDamageNum` values from flat damage to the approved percentage ranges and cap the aggregated runtime value at `40`. Convert Thanh Long I–IV to `3–5/6–10/11–15/16–20%` main-hit damage and keep IV's separately tagged Trọng Thương behavior. Set Bảo★Sát/Siêu★Sát and Siêu★Lan to the approved values.

Change base-stat application so each STR contributes `0.1` percentage point of `trueDamageNum` and each VIT contributes `1` percentage point to the unified reduction pool. Add tests at STR `0/1/200/500` and VIT `0/1/80/200` proving runtime caps remain `20%` for STR contribution, `40%` total penetration, and `80%` reduction.

Put `bloodOutburst`, `spiritFade`, and `hungerAssault` in the `adversity` exclusive group. Their runtime formula reads the attacker's matching resource and contributes `50 * (1 - current_percent)` to the pre-crit percentage pool. It must not inspect target resources or multiply Xuyên Giáp, Trọng Thương, splash, or poison.

Delete player sources, dungeon rewards, treasure drops, registry entries, runtime branches, and descriptions for `soakStrike`; `sunlightStrike`, `afterglowStrike`, `nightMenace`; every player `addHit*Damage`; `sanReplaceDamageChance`; `reflexiveInjury`, `reflexiveInjuryByPercent`, and `retaliateGem`; `attackToAddHealth`; `restoreSpirit`; player `hitSuppressAddHealth`; player `hitChanceAddFreeze`; player `atkChanceAddPoison`; player `hitChanceAddPoison`; `atkSpeedatkSpeed`; and Đá Sát Thương. Remove custom monster rebound keys only where they belong to the deleted Phàm Nhân reflection system. Preserve monster-owned poison/freeze behavior.

Delete `suit_bhtg`, `suit_fyyy`, `suit_yhby`, their nine `z_suit_*` marks, recipes, listeners, buffs, and display strings. Do not delete shared forge assets/stones or `special_bhtg`.

- [x] **Step 4: Enforce restrictions in every equipment mutation path**

Before add, random roll, inherit, or refresh commits an effect, validate the receiving item slot and scan its existing effects for the same `exclusive_group`. Return the existing localized failure result without consuming stones/materials. This validation must live in one helper used by all four paths.

Clamp `GetWeaponAtkSpeed` to `1..2` for the approved nonnegative bonus, keep `hh_sg.lua` and client RPC reads on `atk_speed`, and clamp the `hh_equip_speed` locomotor multiplier to `1..1.5`; do not clamp vanilla external multipliers or alter work/action animation speed.

- [x] **Step 5: Verify GREEN**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_catalog.py -v
python mods/PhamNhanTuTien/tools/test_armor_set.py
python tools/test_ttk_forge_backend.py
```

Expected: canonical catalog passes; forge operations reject invalid group/slot combinations without material loss.

---

### Task 5: Full Integration Gate, Dedicated-Server Smoke, and Documentation

**Files:**
- Create: `mods/PhamNhanTuTien/tools/combat_smoke.lua`
- Create: `tools/run_phamnhan_combat_smoke.py`
- Modify: `tools/test_ttk_solo_integration.py`
- Modify: `mods/PhamNhanTuTien/tools/boss_smoke.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_strengthen_only.py`
- Modify: `mods/PhamNhanTuTien/scripts/components/wb_strengthen.lua`
- Modify: `mods/PhamNhanTuTien/main/hh_tunning.lua`
- Modify: `mods/PhamNhanTuTien/scripts/combat/hh_combat_status.lua`
- Modify: `mods/PhamNhanTuTien/tools/test_combat_status.py`
- Modify: `mods/PhamNhanTuTien/README_VI.md`
- Modify: `mods/PhamNhanTuTien/Wiki.txt`
- Modify: `PHAM_NHAN_SOLO_AUDIT_HANDOFF.md`

**Interfaces:**
- Consumes: Tasks 1–4 complete behavior.
- Produces: one reproducible runtime acceptance command and final handoff evidence.

- [x] **Step 1: Write the failing smoke assertions before runtime glue**

The smoke script must spawn one fresh Phàm Nhân test player, one ordinary armored target, and one boss-class target in an isolated cluster. Give deterministic test effects directly through `hh_player`, inject deterministic RNG through the test seam, and emit one PASS marker only after proving:

```text
dodge short-circuits offensive RNG
crit x3.5 and Bạo Phát IV combine to x17.5
40% Xuyên Giáp adds exactly 40% of the isolated pre-crit/pre-Bạo Phát base against both armored and unarmored targets, while bypassing the target player's Phàm Nhân reduction pool and normal physical armor
80% Phàm Nhân reduction plus the effective 80% vanilla armor layer produces 96% reduction; two 80% vanilla pieces alone still use DST's highest-absorption rule
poison reaches five stacks and expires after the refreshed 10-second window
normal freeze and boss slow/ICD take their separate branches
splash hits a secondary armored target without re-proccing
lifesteal respects 15% event and 90% second caps
boss Trọng Thương is 1%, normal Trọng Thương is 3%, boss execute is refused
```

The Python runner must create a new test cluster under `.superpowers/pham-nhan-combat-runtime`, copy the current mod, never point at a player save, stop the server in `finally`, and fail on `LUA ERROR`, timeout, or absence of `PHAM_NHAN_COMBAT_SMOKE_PASS`.

- [x] **Step 2: Run smoke and verify RED**

```powershell
python tools/run_phamnhan_combat_smoke.py
```

Expected: FAIL until the script is registered with the isolated runtime and all deterministic seams exist.

- [x] **Step 3: Extend the integration gate**

Make `test_ttk_solo_integration.py` compile every new Lua file, run the four new Python suites, verify no deleted player effect/set is registered, verify historical source directories are unchanged, and retain all existing integration assertions. The existing source-manifest parity gate must keep hashing the historical source, but replace byte-equality assumptions for approved Phàm Nhân combat overlay files with an explicit narrow allowlist; never weaken provenance checks for other files. Do not test deletion by source grep alone: load registries and exercise equipment/public behavior.

Update `boss_smoke.lua` so it asserts percentage Xuyên Giáp behavior and its `40%` aggregate cap rather than the obsolete flat `trueDamageNum == 40` contract.

Remove the remaining custom strengthening buff `reflect` and its `+7` Phản Đòn/Phản Chấn descriptions. Keep the generic `ontakedamage` plumbing used by other strengthening buffs, and do not alter unrelated vanilla reflection flags, bramble behavior, or `reflectivevest`. Extend `test_strengthen_only.py` to prove `reflect` has no config/runtime producer while another `ontakedamage` buff still works.

The dedicated-server smoke is authoritative for engine lifecycle semantics. If normal `Freezable:Freeze(2)` remains frozen through DST's default thaw wear-off, make the status layer end the freeze immediately at the approved two-second deadline and add a focused regression test; retain boss slow/ICD behavior and safe timer cleanup.

- [x] **Step 4: Update player documentation**

Document only shipped behavior: exact formulas, caps, direct-hit versus auxiliary-packet rules, boss exceptions, and removed sets/effects. Remove descriptions of obsolete flat Xuyên Giáp, multi-proc Bạo Phát, shared EXP, and deleted sets. State that DST uses the highest vanilla armor absorption rather than multiplying two armor pieces; show `80%` Phàm Nhân pool multiplied by effective `80%` vanilla armor = `96%` total reduction.

- [x] **Step 5: Run the complete verification matrix**

```powershell
python mods/PhamNhanTuTien/tools/test_combat_math.py -v
python mods/PhamNhanTuTien/tools/test_combat_pipeline.py -v
python mods/PhamNhanTuTien/tools/test_combat_status.py -v
python mods/PhamNhanTuTien/tools/test_combat_catalog.py -v
python tools/test_ttk_solo_integration.py
python tools/run_phamnhan_combat_smoke.py
git diff --check
```

Expected: every command exits `0`, the smoke prints `PHAM_NHAN_COMBAT_SMOKE_PASS`, and `git diff --check` is clean.

- [x] **Step 6: Record final evidence in the handoff**

Append the exact commands, pass counts, smoke marker, changed-file list, any environment limitation, and confirmation that `mods/3780347550`, `mods/2937640068`, and `mods/AchievementLevel` were not changed. Mark Mục 2 implemented only after all gates pass.

---

## Execution Notes

- Execute Tasks 1–5 sequentially; Task 2 consumes Task 1, Task 3 consumes Tasks 1–2, and the catalog in Task 4 must be green before Task 5 runtime smoke.
- Use one fresh implementer and one task reviewer per task. Never run two implementation agents concurrently because Tasks 2–4 share `hh_player.lua`, `hh_api.lua`, and registries.
- The current checkout is a dirty `master` whose integrated Phàm Nhân state is not present in `HEAD`; a normal Git worktree would omit required uncommitted integration changes. Execute in place, restrict every task to its named files, save before/after diff packages in this plan's SDD workspace, and do not commit pre-existing unrelated hunks.
