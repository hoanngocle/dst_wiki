# Tu Tien Ky Boss Indicators Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show nearby, off-screen major bosses with directional HUD markers in Tu Tien Ky, including optional Solo bosses.

**Architecture:** A client-only controller scans nearby networked entities with the `epic` tag every 0.5 seconds, filters dead, hidden, friendly, minor, and stale entities, and owns namespaced indicator widgets under `PlayerHud.under_root`. The widget extends the current DST `TargetIndicator`, uses the credited source atlas where an icon exists, and falls back to the game unknown-avatar icon plus a readable prefab name.

**Tech Stack:** DST Lua 5.1 APIs, current `widgets/targetindicator`, executable Lua mock tests through Lupa.

**Spec:** Approved in-chat Boss Indicators integration scope supplied for this task.

## Global Constraints

- Keep Tu Tien Ky server-required while all HUD work remains client-only and dedicated-safe.
- Do not import or require Solo modules; recognize its public prefab names and replicated `epic` tags only.
- Preserve manual-only inventory sorting and all existing integrations.
- Do not run obfuscated source loaders, launch DST, package a ZIP, or publish.

## Review Focus

- A target leaving the world, dying, entering view, or falling out of range must lose its widget.
- Repeated scans and HUD reconstruction must not duplicate widgets or callbacks.
- Unknown mod bosses must get a safe icon and readable name.
- Solo summons/pets and known base minibosses must not appear through the generic `epic` fallback.
- Dedicated servers must not load widget code or install HUD hooks.

---

### Task 1: Controller, widget, assets, and registration

**Files:**
- Create: `mods/TuTienKy/tests/test_bossindicators.lua`
- Create: `mods/TuTienKy/scripts/ttk_bossindicators.lua`
- Create: `mods/TuTienKy/scripts/widgets/ttk_bossindicator.lua`
- Create: `mods/TuTienKy/images/ttk_bossindicators.tex`
- Create: `mods/TuTienKy/images/ttk_bossindicators.xml`
- Modify: `mods/TuTienKy/modmain.lua`

**Interfaces:**
- Produces: `require("ttk_bossindicators").Install(env)`, `RefreshHUD(hud, globals, factory)`, `CleanupHUD(hud)`, `ShouldTrack(target, globals)`, and safe name/icon helpers.

- [x] Write an executable Lua test for filtering, off-screen discovery, duplicate prevention, stale cleanup, fallback metadata, Solo prefabs, and dedicated/client installation.
- [x] Run it and confirm it fails because `scripts/ttk_bossindicators.lua` does not exist.
- [x] Implement the controller/widget, copy the credited source texture, register assets, and install the client hook.
- [x] Run the focused test, then the automated Tu Tien Ky Lua tests and Lua 5.1 syntax checks.

### Task 2: User-facing integration notes

**Files:**
- Modify: `mods/TuTienKy/modinfo.lua`
- Modify: `mods/TuTienKy/README_VI.md`
- Modify: `mods/TuTienKy/CHANGELOG.md`
- Modify: `mods/TuTienKy/CREDITS.md`

**Interfaces:**
- Consumes: behavior and source attribution delivered by Task 1.

- [x] Bump the version and document automatic behavior, supported Solo bosses, source credit, and in-game visual-test limitation.
- [x] Re-run focused tests, automated Tu Tien Ky Lua tests, syntax checks, and asset-reference checks.

## Verification evidence

- `test_bossindicators.lua`, `test_inventorysort.lua`, and `test_inventory45_compat.lua` pass under Lua 5.1.
- All 121 Lua files present in Tu Tien Ky compile under Lua 5.1.
- The integrated TEX is byte-identical to the credited source (SHA-256 `C5ED10AFCA81E02C59EDA4D5B4163C31603A2A83F188778328EB88EE626C5A76`) and the rewritten atlas reference resolves.
- An independent smoke test using the installed DST ZIP's real `Class` and `widgets/targetindicator.lua` passed for construction, deferred start, update, source/fallback icons, fallback name, arrow placement/colour, hover label, and early task cancellation.
- Actual rendering, resolution scaling, live multiplayer timing, and gameplay remain for in-game verification.
