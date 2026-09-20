# Solo into Tu Tiên Ký Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ship one TuTienKy package containing all existing Solo Leveling functionality.

**Architecture:** Preserve the source modules and identifiers. Run Solo's relocated entrypoint after TuTienKy initialization, merging registration tables without replacing existing entries. Merge configuration declarations into the metadata sandbox and run Solo world generation through TuTienKy.

**Tech Stack:** DST Lua 5.1, Python standard library, Lupa, local dedicated-server runtime.

**Spec:** `docs/superpowers/specs/2026-09-20-solo-into-tu-tien-ky-design.md`

## Global Constraints

- Source Solo and player saves remain untouched. Back up TuTienKy before editing.
- Preserve Solo prefab/component/save keys, RPC namespaces and defaults.
- Include all 660 source files with explicit mapping for conflicting entrypoints.
- A separately enabled Solo must stop initialization before hooks are installed.
- Keep SoloCombatHUD optional and do not change the website.
- Report actual runtime coverage; mocks do not prove live clients or multiplayer.

## Review Focus

- Registration tables must retain both mods' assets and prefabs, including repeated load protection.
- False config values must survive the metadata merge; every original config key remains present.
- Renamed local Solo folders must be detected, not only the Workshop identifier.
- Forest worldgen must retain arena topology, while existing maps must not be rewritten.
- Save/reload must retain Solo player components and existing TuTienKy objects.

### Task 1: Snapshot and regression harness

Files: `tools/test_ttk_solo_integration.py`, `mods/backups/TuTienKy_before_solo_*.zip`, `.superpowers/ttk-solo-integration/`.

- [x] Snapshot destination and source hashes using `zipfile.ZipFile` and `hashlib.sha256` before mutation.
- [x] Add executable Lua tests loaded via `LuaRuntime`: `assert(loadfile(root .. '/main/ttk_solo_bootstrap.lua'))`; use a stub modimport that replaces PrefabFiles/Assets to prove both old and new registrations survive. Verify duplicate detection runs before this import and repeated calls do not reinstall hooks.
- [x] Run harness and observe expected missing-bootstrap failures.

### Task 2: Integrated package

Files: `mods/TuTienKy/modmain.lua`, `modinfo.lua`, `modworldgenmain.lua`, `main/ttk_solo_bootstrap.lua`, `scripts/ttk_solo_guard.lua`, `main/ttk_solo_source.lua`, source assets/modules and `SOLO_SOURCE_MANIFEST.json`.

- [x] Copy source files without overwriting any destination file; relocate source modmain into `main/ttk_solo_source.lua` and archive source modinfo under provenance.
- [x] Append config declarations in a local function returning Solo configuration_options; concatenate with existing config table and prefix UI labels. Keep all config keys/defaults.
- [x] Insert duplicate guard at the start of runtime and worldgen. Detect known IDs and metadata names through KnownModIndex.
- [x] At the end of runtime, import Solo through a bootstrap that snapshots existing registrations and merges them with Solo registrations. Match the original TuTienKy-before-Solo load order.
- [x] Execute package tests, compile every Lua file, and verify every mapped source checksum except explicitly documented wrapper modifications.

### Task 3: Runtime and delivery

Files: `tools/run_ttk_solo_smoke.py`, `mods/TuTienKy/tools/solo_integration_smoke.lua`, `mods/TuTienKy/SOLO_INTEGRATION_VI.md`, `mods/dist/TuTienKy_v0.10.0.zip`.

- [x] Start an isolated offline dedicated-server cluster from a copied runtime using only TuTienKy. Use `subprocess.CREATE_NO_WINDOW`; do not touch live saves or servers.
- [x] Validate new-world arena, spawn representative Solo and TuTienKy items, verify Solo player components, save/reload and persisted state. Fail on Lua errors or timeout.
- [x] Run existing applicable Lua regression files and investigate failures against baseline.
- [x] Request one independent final review of the integration while checking package completeness locally. Resolve material findings and rerun affected tests.
- [x] Write install/migration limits and verified results, produce ZIP, verify ZIP hashes against the final folder.

## Execution ledger

- User approved the written design and explicitly requested immediate implementation. Execute inline without asking for authorization again.
- Work directly on the provided untracked mod tree with a timestamped backup: a Git worktree would omit the actual mod files and is unsuitable for this checkout.

- Completed: 7/7 integration checks, 423 Lua syntax checks, 3 existing Lua regressions, offline creation/reload and two-mod-to-one-mod save migration smoke passed. Independent review has no unresolved material findings.
- Preserved concurrent armor/skin edits; see report and concurrent_changes.json.
- ZIP verified against all 1659 current files; CRC passes. No commit/push or changes to live saves performed.
