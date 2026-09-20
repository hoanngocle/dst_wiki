# EVA Huyền Thiên Trảm Linh Kiếm — approved contract

User requests plan + implementation of the Tu Tiên sword array adapted to EVA's five purple scythes and a large central scythe. User explicitly chooses **15 Hồn Lực per successful cast**. The skill is independent: remove original Thanh Trúc Phong Vân Kiếm buff/cultivation prerequisites. Keep current Life, Wings, Soul awards and all approved appearance.

## Gameplay

- J at world mouse position by default, separately configurable, HUD/text/menu guards. Range 12 from caster (implementation choice); server validates finite coordinates and legal map position. Land/platform valid; ocean center valid only with active EVA wings. Never invalid tile/cave void/out of bounds. Invalid requests cost nothing and start no cooldown.
- Successful cast deducts 15 Soul once and starts 25 s cooldown immediately. No item/equipped scythe prerequisite, no repeated drain. Cooldown survives save/load; cast entities do not resume/load or recharge Soul. Collision with Life/Wings key gives existing skills priority.
- Five small scythes on pentagon vertices, circumradius5, fixed selected world center. No following the player. Connect the perimeter visibly; silver/amethyst palette uses current EVA scythe artwork plus verified built-in FX.
- Beginning at1.3 s, scan every0.3 s: root valid enemy locomotor targets strictly inside/on pentagon (not just circle), releasing EVA-owned root sources when leaving/becoming invalid. Preserve other root sources; clean all on finish/owner death/removal.
- Large center scythe spawns at1.3 s; strike367 base once at1.8 s, radius6 (matching original sword damage area).
- Beam appears at1.8 s with native wagboss_beam `beam_pre` (33 frames at30fps =1.1 s). Damage100 each0.5 s from2.9 s through7.9 s inclusive (11 scheduled pulses). Damage radius6 matching source, distinct from pentagon root region. Terminal pulse and cleanup ordering must be deterministic, no damage after final pulse.
- Controller lasts about7.9 s; release roots and cancel owned gameplay tasks after terminal pulse; short harmless FX fade may finish afterward. Ending early on death/ghost/despawn/removal must remove controller/roots/FX and prevent further hits. No cleanup may interfere with a different EVA's simultaneous array.
- Target rules reuse existing EVA valid-target protection for allies, followers, protected players, invisible/untargetable/dead entities and neutral bystanders. All attack tests are relative to selected center (not accidentally caster range); attacker credited to EVA so kills award Soul. No weapon/crit multiplier or armor bypass.

## Source evidence

Reference only: `mods/eva-assets-work/skill-audit/decoded/scripts/prefabs/xd_htz_spell.lua:119` and `xd_htz_xtzlj.lua`. Native `wagboss_beam.zip` inspected: beam_pre33frames,30fps,1.1s. Reimplement with DST APIs, no Tu Tiên runtime dependency or partially decoded Lua copied into production.

## Validation / constraints

Standalone mod `mods/EVA_v1.0`; do not restore Calliope powers. No Steam installation or publishing. Preserve all existing binary appearance assets. Test polygon geometry, target changes, overlapping root sources, timing, final pulse/cleanup, RPC coordinate abuse, resource/cooldown rejection and persistence, input/config key collisions, client/master boundaries. Run existing Wings/Life/identity/scythe suites and restricted modinfo environment. Archive CRC and byte parity; report absence of actual live-game multiplayer testing.
