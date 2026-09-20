# EVA Phong Lôi Xí — implementation contract

User approved toggle wings, +8% movement, real water walking, no cultivation level, silver wings/violet lightning. Follow-up explicitly chooses **3 Soul per successful OFF -> ON transition, no maintenance drain**. Existing Soul becomes Hồn Lực resource; preserve awards/save/HUD and existing Life skill. Continue requested GPT-5.6 Sol High implementation workflow.

## Design

- Default H toggle, configurable independently of G/Life, no input while chat/menu. Server validates identity/alive/state, cooldown against RPC spam, and >=3 Soul. Deduct exactly once on successful enable, nothing on reject/disable/load.
- Independent `eva_wings` server component owns state, movement multiplier key, lifecycle, persisted active flag, replicated net bool, FX. Restore active state safely on load without charging again, especially when saved over water. Do not persist references/tasks.
- Water traversal must actually work on server and remote prediction: inspect installed DST locomotor/pathcaps/physics/drownable APIs, synchronize client state. Preserve obstacles/collisions; no flight across cave void, walls or arbitrary out-of-bounds terrain.
- Reject manual OFF while over ocean with no platform, with feedback to land first. No passive depletion. Death/ghost/removal forcibly cleans up owned changes and FX; never leave ghost physics corrupted. Reject riding/hopping/swimming/frozen or incompatible activation states. Handle mount transition without restoring stale human collision masks over mount/ghost state.
- Use existing Tu Tiên `anim/xd_htz_flc.zip` as a bundled standalone wing source with attribution and uniquely named EVA FX prefab. Reference `xd_htz_spell.lua` wing prefab for follower/sort placement. Runtime silver/violet tint + violet electrical accents; do not overwrite approved character/scythe textures. No Tu Tiên Lua/runtime dependency.
- Preserve prior drowning/platform/pathcaps settings where possible and remove only own speed multiplier. No invincibility. Do not disable void falling globally in caves. Do not copy partial decoded source as executable Lua.

## Files / ownership

Sol implementer owns new `scripts/components/eva_wings.lua`, `scripts/util/eva_wings_input.lua` (shared helper if needed), `scripts/prefabs/eva_wings_fx.lua`; modmain/modinfo/character common/master integration; README files; renamed/copied bundled wing animation only. Do not alter original character/scythe assets or Life stats/behavior. Tests go in `mods/eva-assets-work/wings-skill/`.

Baseline current `mods/EVA_v1.0` first; retain previous Life ZIP backup. No Steam install, git commit, or publish. Parent owns review and distribution packaging. If changing config entries, update existing restricted-modinfo regression's expected count/defaults. Existing identity test must admit `eva_wings` as an approved EVA component while still rejecting Calliope powers.

## Acceptance checklist

- [x] Immutable baseline/hash manifest before edits.
- [x] 3 Soul cost once; insufficient funds unchanged; repeated enable/RPC doesn't double-charge; OFF free; no maintenance decay; saved ON restores free.
- [x] +8% modifier coexists with base stats and other modifiers; removed cleanly.
- [x] Water collisions + pathfinding + drowning behavior verified using installed engine code; remote client state handling tested; cave void protection retained.
- [x] Manual OFF at sea blocked; OFF on land/platform allowed; death/removal/load/mount edge cases safe.
- [x] Wing FX registered correctly, layered/follows owner, silver/violet, bounded lightning, client/dedicated-safe lifecycle.
- [x] Restricted modinfo environment test, new wing behavioral suite, existing Life/identity/scythe/engine-health regression suites pass.
- [x] Parent independent review; fix concrete blockers; package ZIP CRC/exact parity + original visuals unchanged.
- [x] Deliver ZIP and H toggle/cost explanation, explicitly distinguish automated checks from not-yet-performed live multiplayer test.

## Delivery evidence

Sol High implementation and independent Sol High review complete. Parent checks: Wings13, Life12, identity6, scythe21, actual-engine drowning/health integration, restricted-modinfo loader and30 Lua syntax checks passed. FinalZIP91files, CRC andexactcontentparitypass. Alloriginalappearanceassetsunchanged. SHA256: `00a43e9721e39a39d17a013c156d9b7871f925fa71f81f340c02efe729481cac`. PreviousZIPretainedat `mods/backups/EVA_v1.0_before_wings_d277e62c.zip`. NoSteaminstallation orlivegame/multiplayertest performed.
