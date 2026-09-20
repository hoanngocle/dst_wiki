# EVA Hồ Ảnh and HUD Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development with user-selected GPT-5.6 Sol High, separate implementers for bounded independent units; parent integrates and reviews, then an independent reviewer audits final runtime flow.

**Goal:** Port free 20-range/12s Hồ Ảnh and expose three abilities through no-inventory skill icons and Hồ Ảnh through ground right-click.

**Architecture:** Existing character components remain authoritative. New Fox component owns blink and transient fire. New HUD/owned hidden book adapts native targeting and routes to those components, with replicated cooldown/status for display.

**Tech Stack:** DST Lua5.1, native scripts.zip, Python/Lupa tests, existing Tu Tiên animation assets copied standalone.

**Spec:** `docs/superpowers/specs/2026-09-19-eva-fox-hud.md`

## Global constraints

Preserve existing95-file EVA baseline; new additions isolated. Original mod inputs read-only. User chose cost0,range20,CD12, no-slot three-icon panel and right-click-only Hồ Ảnh. No publication/Steam edits/commits. Existing Sol High preference used. Parent alone backs up/packages.

## Review focus

- Clicking an icon must not instantly cast targeted skills at the UI's world projection; world confirmation/cancel is explicit.
- Own casting states must permit component activation without letting clients bypass busy or ownership validation.
- Two EVA clients cannot cast each other's hidden book or share cooldown/status.
- Interrupt/load/death midfade restores visible living/ghost presentation and does not clear foreign invulnerability or Wings collisions.
- Destination validity is rechecked at relocation; moving platforms, blocked land, cavevoid and turned-off Wings reject safely.

## Task1 — Fox component and FX (Sol High)

Own new `scripts/components/eva_fox_blink.lua`, `scripts/util/eva_fox_common.lua`, `scripts/prefabs/eva_fox_fx.lua`, optional `scripts/util/eva_fox_states.lua` only if needed, new uniquely named anim archives, and tests `mods/eva-assets-work/fox-hud/test_fox*`. Do not edit shared character/modmain/config/UI files.

- [x] Inspect decoded `xd_sudaji_mxrg.lua`, `xd_sudaji_fx.lua`, `main/stategraph.lua` and actual engine visibility/health/stategraph APIs.
- [x] Write scheduler-driven tests: out-of-range/NaN/Inf/mapblock rejects noCD, success costs0, exact timeline and3fireticks, ally protection/killowner, outside teleport permissions, midcast blocked destination, load cleanup, foreign protection, Wings coexistence.
- [x] Implement interface `CastAt(x,z)`, `GetCooldownRemaining()`, `Stop(reason)`, `OnSave/OnLoad`. Use source timeline and fire behavior from spec; new runtime FX names prefixed EVA and native-safe animations.
- [x] Run tests and report dependencies/integration requirements; no shared-file changes.

## Task2 — HUD + hidden book integration (Sol High)

Own new `scripts/widgets/eva_skillpanel.lua`, `scripts/prefabs/eva_skillbook.lua`, `scripts/util/eva_skillpanel.lua` or equivalent focused router; modify `modmain.lua`, `scripts/prefabs/calliope_mori.lua`, settings/config only if necessary, READMEs and existing identity/config fixtures. Coordinate explicit Fox interface with Task1. Existing components may get narrowly scoped native-cast context support only after discussing with parent.

- [x] Inspect native spellbook/aoetargeting/playercontroller, Hàn hiddenbook+widget and owned inventory behavior; choose safe native path without global IsGrandOwner overrides.
- [x] Write tests for book ownership and no inventory slots, click-vs-target flow, cancel/no-cost, menu/ghost/chat guards, replicated countdowns, toggle state, dedicated safety and current G/H/J preservation.
- [x] Implement3icons with Vietnamese hover labels/costs, host+client targeting, native reticules, collapse and sensible screen anchoring; distinct existing built-in or source icons, no new painted assets.
- [x] Add user-requested direct ground right-click Hồ Ảnh action on host/remote client; retain object interactions, active-item/deploy behavior, native targeting cancellation and foreign actionpicker overrides. Test all priority guards and server ownership/range validation.
- [x] Install new component/FX on EVA; preserve listen-host ownership boundaries; expose correct visible status from server. Document source asset attribution and manual smoke checklist.
- [x] Run UI/router fixtures and impacted existing config/identity suites. Report complete changed-file list.

## Task3 — Parent baseline, independent audit and package

- [x] Snapshot95-files + dist hash manifest before implementers start.
- [x] Audit both tasks' native engine use; separate final Sol High reviewer follows actual HUD-to-server-to-Fox path and lifecycle.
- [x] Resolve findings; run all Fox/HUD and prior regression suites with fresh evidence.
- [x] Package `mods/dist/EVA_v1.0.zip`; CRC/exactbytes/unchangedoriginalart, save verification evidence and concise Vietnamese delivery with limitations.

## Rulings

- User has explicitly authorized implementation and selected the UI; proceed under that authorization without further design approval gates.
- Source fire has heal and sleep effects not in earlier brief; port its actual behavior and tell user, retaining EVA target protections.
- Keep existing optional keys to avoid removing established use; add no new mandatory hotkey.
