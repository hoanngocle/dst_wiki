# EVA Thần thông Sinh Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to execute the tightly coupled implementation below. The requested implementer is GPT-5.6 Sol with High reasoning. Parent performs independent review and package verification.

**Goal:** Ship a standalone Thần thông Sinh skill in EVA v1.0 with the approved numbers and lavender/silver feedback.

**Architecture:** One server component owns activation, timers, cooldown, shielding and save/load. A shared utility defines tuning and valid targets. An RPC/input module requests activation; clients never supply damage, heal or cooldown values. A small prefab module supplies replicated FX and projectiles built on verified DST APIs.

**Tech Stack:** DST Lua 5.1/LuaJIT, bundled DST scripts, local Python/Lupa test runner, ZIP distribution.

**Spec:** `docs/superpowers/specs/2026-09-19-eva-life-skill.md`

## Global Constraints

- Preserve all approved EVA character/weapon/skin assets. Latest user correction removes Calliope mechanics except Soul counter; add only Life, not Death or other shortlisted skills.
- Work in `mods/EVA_v1.0`; do not modify Tu Tiên, original Calliope, Steam installation, unrelated web code, or publish/commit.
- Use an immutable baseline backup before edits. New unit test assets stay outside distributable mod; retain and update the existing bundled test suite.
- No external mod imports. Use a unique EVA namespace for component, FX and RPC.
- Read actual DST health/combat/projectile APIs before implementing finite shield. Preserve any pre-existing health hooks; never make shield infinite or absorb damage twice. Document order relative to armor and health absorption.
- Cooldown starts on activation; cleanup is idempotent. Skill attack damage must not loop through original weapon procs.
- Do not claim live-game testing. Existing Computer Use launch was blocked by approval review.

## Review Focus

Server authority and RPC spam; exact five heal ticks; shield overflow and compatibility; allied target filtering; save/load cooldown; no orphaned projectiles/FX; no visual asset regression.

## Task 1 — Implement and verify the complete skill

**Create:** `scripts/components/eva_life.lua`, `scripts/util/eva_life_common.lua`, `scripts/util/eva_life_input.lua`, `scripts/prefabs/eva_life_fx.lua` under the mod; `mods/eva-assets-work/life-skill/test_life_skill.py` and Lua fixtures as needed.

**Modify:** mod `modmain.lua`, `modinfo.lua`, `scripts/prefabs/calliope_mori.lua`, `README_EVA.md` and character description if needed. File boundaries may be simplified when source inspection justifies it.

- [x] Capture baseline backup and per-file hashes under `mods/eva-assets-work/life-skill` / `mods/backups` without overwriting previous backups.
- [x] Inspect core health, combat, projectile, netvars, frontend input patterns and existing Calliope hooks. Record chosen shield interception semantics.
- [x] Establish failing behavior checks using accessible local Lupa (`mods/mod_steam/.fasttravel-test-runtime`) or another available Lua runtime. Do not install packages unless necessary.
- [x] Implement constants and shared target predicate: alive, combat-capable, in range, legal enemy, alliance/PvP protection. Call predicate again when projectile lands.
- [x] Implement `Activate()` returning accepted/reason, `Stop()`, `GetCooldownRemaining()`, save/load methods. Server only. Buff 15 s; cooldown 60 s; heal at 0/3/6/9/12; projectile .2 s (80, range12); aura .5 s (67, radius6).
- [x] Add finite 25%-max-health shield with overflow; cleanup restores compatible health behavior. Remove old immortality/sleep powers per latest instruction.
- [x] Implement networked pale-purple/silver FX using existing, verified game banks/builds. Unique prefab names, correct pristine/master split; dedicated server safe. Projectiles have bounded lifetime and cleanup.
- [x] Add configurable G shortcut (with alternatives/off), suppress during text input/menu; RPC validates character, alive and skill state. Give readable cooldown/activation feedback.
- [x] Wire component into character safely and register new prefabs/import. Preserve Soul saves and remove old immortality save/load hacks.
- [x] Run tests covering exact cadence/count, activation rejection, death/removal cleanup, target becoming invalid/friendly, shield partial/full/overflow/depletion/expiry, cooldown persistence, and existing hooks. Compile every mod Lua chunk.
- [x] Update documentation for shortcut, approved numbers, target rules, shield ordering and live-test limitations. Remove inaccurate claim of entirely unchanged skills.

## Task 1B — Remove Calliope powers, retain Soul (Sol High)

Latest user correction supersedes old preservation instructions. Separate Sol High worker owns `scripts/prefabs/calliope_mori.lua`, `calliope_scythe.lua`, `scripts/components/calliope_souls.lua`, `scripts/util/calliope_widget.lua`, `calliope_recipes.lua`, `calliope_settings.lua`. Task 1 worker owns new Life files, `modmain.lua`, `modinfo.lua`, and README. Avoid concurrent edits to the same file.

- [x] Strip immortality, sleep recovery, reactive auto-revive, kill healing, soul loss and custom sanity/monster/relationship effects from character. Add server `eva_life` component.
- [x] Preserve Soul counter and HUD with authoritative server state, save/load, cap and normal/ghost/epic awards. Count legal kills with any weapon/skill; no combat effects or decay.
- [x] Make scythe ordinary configured damage/durability, keep art; remove Soul Strike, crit and reach/sanity side effects.
- [x] Remove old specialty item recipes; retain prefab save compatibility. Rename crafting/character descriptions to EVA and remove obsolete config choices (coordinate with Task 1).
- [x] Behavioral regression tests for Soul awards/cap/persistence, no kill-heal/no immortality, no scythe spell/crit, client-safe HUD setup.

## Task 2 — Parent review and delivery

- [x] Inspect complete diff against backup, verify only intended files changed; review authority, cleanup and compatibility using actual engine source.
- [x] Re-run behavior suite and Lua compile checks. Resolve concrete failures before packaging.
- [x] Build `mods/dist/EVA_v1.0.zip` with top-level `EVA_v1.0/`; verify CRC and file-by-file byte parity to working mod. Retain backup.
- [x] Record results, hash and limitations in `mods/eva-assets-work/life-skill/verification.json`.
- [x] Provide download link and concise activation instructions. Live checklist: host and remote client; G while idle/chat; near hostile and allied mobs; shield overflow; 15-second expiry; 60-second cooldown; save/reload; Soul counting with Life and normal scythe attacks; absence of Calliope powers.

## Completion evidence

Implemented by GPT-5.6 Sol High, independently reviewed by a separate Sol High worker. Critical modinfo sandbox issue fixed and rechecked. Parent verification: 12 Life groups, 6 identity groups, installed-engine health integration, 27 Lua syntax checks and 21 ordinary-scythe assertions passed. Archive CRC/content parity and unchanged appearance hashes passed. Final archive SHA-256: `d277e62c63de11b6b91b1d6a4799c6278a3f57802671c8095c06910165090689`. No live-game/multiplayer run or Steam installation. Existing bundled tests were updated, not removed; new test fixtures remain outside the mod.
