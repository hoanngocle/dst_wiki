# Complete skins for existing Tu Tiên Ký items — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to execute these tightly coupled steps in order. Track completion with the checkboxes below. The user explicitly authorized implementation and requested a GPT-5.6 delegate.

**Goal:** Bring every available skin for an item already implemented in Tu Tiên Ký from the local Tu Tiên sources, including any additional definitions found in Unlock Skin.

**Architecture:** Discover actual registered destination prefabs and source skin definitions, reconcile them with existing skin metadata, then extend the existing native crafting/reskin integration. Skin resources retain their embedded source bank/build identifiers; destination prefab and filesystem identifiers use established Tu Tiên Ký conventions. Source loaders are inspected as data, never executed.

**Tech Stack:** DST Lua, Python standard-library asset inspection/import tooling, local Lua smoke harness where available.

**Spec:** User-approved in-chat scope: existing destination items only; all matching variants from Tu Tiên and Unlock Skin; deduplicate; include icons/animation/dependencies/effects; preserve item gameplay and existing skins; verify selection, reset, persistence and client behavior with explicit runtime limitations.

## Global Constraints

- Work in `C:/Users/hoanc/company/dst_wiki`; `mods/TuTienKy` and most associated tools are currently untracked. A clean Git worktree would omit the actual working mod. Preserve all existing unrelated edits and create a scoped backup before modifying existing mod files.
- Do not commit the whole workspace, reset, clean, modify installed Steam files, push or publish.
- Sources: `mods/mod_steam/3235319974` (known Tu Tiên), `mods/mod_steam/3773896514` (Unlock Skin 1.1). Inspect other local Tu Tiên copies only after identifying them through modinfo and comparing provenance.
- Do not execute obfuscated/untrusted source loaders or fetch remote code. Decode source statically when necessary using existing repository utilities.
- Keep existing IDs stable, including exceptional skins whose names or bases are outside `ttk_*_skins_*` conventions.
- Do not add new base items, character skins, or unrelated features.
- Do not change recipes, combat stats or unlock unrelated game cosmetics. Port presentation dependencies for supported item skins and document source effects with gameplay implications separately.
- Preserve localized text and current bank/build exceptions. Do not blindly rerun the existing importer: it overwrites the entire manifest and generated Lua table.
- Website changes are limited to regenerating existing skin data/icons if needed. Read `node_modules/next/dist/docs/` before writing any Next.js code; no UI changes are required for this task.
- Update only the skin count/documentation justified by the actual result. Package a new, uniquely named local ZIP if the mod's documented workflow expects a distributable; do not overwrite existing releases.

## Review Focus

1. Dynamic/grouped prefab registration must count as implemented; a filename-only whitelist misses items.
2. Existing custom entries must survive regeneration, especially nonstandard identifiers and base `homesign`.
3. Weapons, equipment and staged structures may have a different bank, equip symbol, animation or reset behavior than generic idle structures.
4. A source declaration without an asset archive, or an archive without a usable declaration, must be explicitly reconciled rather than silently counted as imported.
5. Reapplying/resetting a skin must not leave duplicate effects, incorrect inventory icons, forced idle states, or client-only/server-only errors.

## Task 1 — Audit and implement the complete owned-item skin pipeline

These steps are one implementation unit: source classification determines both importer metadata and runtime dispatch. The GPT-5.6 implementer owns the importer, audit, runtime edits and focused tests. The parent independently checks coverage and reviews the final changes.

**Files:**
- Modify: `tools/port_ttk_owned_item_skins.py` (safe discover/reconcile/import entry point).
- Modify as needed: `mods/TuTienKy/skins_manifest.json`, `mods/TuTienKy/scripts/ttk_skin_data.lua`, `mods/TuTienKy/scripts/ttk_skins.lua`, `mods/TuTienKy/scripts/ttk_skin_effects.lua`, `mods/TuTienKy/scripts/prefabs/ttk_hhlmz_skins.lua`.
- Modify only if required by an actual skin: destination base prefab modules and registration modules.
- Add resources under `mods/TuTienKy/anim`, `mods/TuTienKy/images/inventoryimages`, and relevant map/effect asset directories.
- Create: `tools/test_ttk_owned_item_skins.py` (focused importer/coverage regression tests).
- Create: `docs/superpowers/reports/2026-09-20-tu-tien-ky-all-owned-skins.json` (machine-readable audit).
- Create: `docs/superpowers/reports/2026-09-20-tu-tien-ky-all-owned-skins.md` (Vietnamese outcome, provenance and limitations).

**Interfaces:**
- Consumes actual source definitions/assets, destination registrations and existing metadata; never treats the old hardcoded BASES list as the exhaustive destination inventory.
- Produces one deduplicated manifest and matching Lua records plus a per-source-skin audit with source ID, source base, destination base, original status, final status, assets and reason for exclusions.
- Importer must be import-safe and offer read-only audit/check behavior independently of mutation, with deterministic output.

- [x] Read all destination skin integration and registration code, relevant source definitions, Unlock Skin files, and existing extraction helpers. Record baseline file hashes, manifest entries and counts. Back up existing files before changing them under a unique `mods/backups/TuTienKy_before_all_owned_skins_*` directory.
- [x] Build the destination prefab set using actual `Prefab` registrations and generated groups/registration tables. Trace renamed items through code and source bank/builds, not only prefix substitution. Exclude helper FX and characters from the requested item list.
- [x] Build the source skin inventory from source declaration tables plus animation/icon assets. Inspect Unlock Skin statically for additional names/aliases and asset locations. Explicitly list skins for missing base items, duplicates and missing assets in the audit.
- [x] Compare with the current manifest AND Lua table. Resolve pre-existing disagreement without dropping valid custom records. Audit every supported source variant, not just files containing `_skins_`.
- [x] Add focused regression tests before implementation for preservation of custom records, deduplication, base ownership filtering, missing-resource reporting, and idempotent output. Use standard-library unittest and temporary fixtures; do not depend on the game for importer tests.

Run focused tests with:

```powershell
python -m unittest discover -s tools -p test_ttk_owned_item_skins.py -v
```

- [x] Implement safe discovery/reconciliation and copy validated ZIP/XML/TEX resources. Validate ZIP CRC, embedded bank/build identifiers and atlas texture references. Preserve already-valid custom skin records and write JSON/Lua in the same order.
- [x] Implement per-family skin metadata and callbacks only where source evidence requires them. Maintain default banks/builds, inventory atlas/image, equip symbols, placement previews, map icons and presentation FX. Avoid forcing idle on weapons or structures whose current animation/state must persist.
- [x] Register every imported skin with existing native selection/reskin integration. Ensure skin dependencies are registered and available on client and server. Preserve delegated behavior for unrelated skin names.
- [x] Run importer tests and focused Lua smoke checks for Apply/Clear, wrong-base rejection, reapplication cleanup, client guards, equipment presentation and existing special skins. If runtime tooling is unavailable, record that precisely and perform static checks without claiming in-game success.
- [x] Re-run audit: every source skin with an implemented destination base must be imported or carry a concrete resource/compatibility explanation. Import twice and compare hashes of generated files to prove idempotence. Compare baseline entries and assets to prove no accidental loss.
- [x] Update skin count in `mods/TuTienKy/modinfo.lua` and relevant `README_VI.md` sections using verified counts. Regenerate existing wiki data/icons through `tools/build_tu_tien_ky_web.py` only if compatible and necessary, preserving unrelated catalog content.
- [x] Write reports with source-to-destination mapping, added counts, exclusions, exact checks/results and in-game validation still needed. Include touched-file list and backup path. Prepare uniquely named local distributable if appropriate and verify its file list/CRC; never overwrite another release.

## Task 2 — Independent review and delivery

**Files:** implementation files and reports from Task 1; the parent performs verification without changing unrelated work.

- [x] Independently compare the source skin set, actual destination ownership and final audit; inspect all exclusions for false omissions.
- [x] Review integration for missing equip/map/effect dependencies, old custom skin loss, blanket source loader execution, or unintended gameplay changes.
- [x] Run the focused regression suite and verify manifest/Lua consistency and archive integrity using commands recorded by the implementer. Inspect the changed-file hashes against the scoped backup.
- [x] Send actionable defects to the same GPT-5.6 implementer, then verify the repairs. Do not declare completion with unresolved missing owned-item skins silently hidden as exclusions.
- [x] Mark this plan complete and deliver a concise Vietnamese summary, report/distributable links, actual added/final counts and explicit limitations of game testing.

## Execution Record

- 2026-09-20: User approved the analyzed scope and explicitly requested planning followed by GPT-5.6 delegation. Proceed without another permission round.
- Baseline: manifest has 31 entries across 25 bases; runtime Lua/custom registrations must be reconciled before using this as a definitive total.
- Workspace choice: use the existing working mod with scoped backups because the implementation is untracked and other unrelated workspace changes must remain intact.

## Completion — 2026-09-20

- GPT-5.6 Sol implemented the changes; a separate GPT-5.6 Sol reviewed source coverage/importer preservation. The parent independently reviewed runtime, parsed assets, and ran final checks.
- Final: 179 registrations on 40 bases, 95 distinct visuals; added 147 registrations / 63 visuals over the effective 32-skin baseline. All 21 exclusive-owner declarations were reconciled; all original 31 manifest records and the Lua-only portal skin survive.
- Final parent verification: 10 importer regression tests pass; read-only check reports `checked=148 imported_records=178 failures=0`; Lua skin/effect smoke checks and armor suite pass. Earlier relevant weapon, fan, lantern and elemental-family regressions also passed.
- The source/importer review found no important issues remaining after repairs. No live DST host/client validation was performed, and source character/combat skill triggers remain outside scope.
- No full website regeneration or release ZIP was produced. Existing wiki generator now accepts shared skin icons without overwriting unrelated catalog work. Concurrent Solo integration changes were preserved.
- Backup deviation: exact pre-edit copies of the two sword prefab files were not captured before their equip-callback changes. Other scoped backups and the precise limitation are recorded in the outcome report; no reconstructed file is presented as an original backup.
- Deliverables: `mods/TuTienKy`, `docs/superpowers/reports/2026-09-20-tu-tien-ky-all-owned-skins.md`, and the matching JSON audit.
