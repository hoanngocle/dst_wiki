# Thiên Cơ Ốc Implementation Plan

> Execute inline with superpowers:executing-plans; user requested both planning and implementation.

**Goal:** Port the craftable scroll, portable house entrance, recall token, and persistent furnished interior from Tu Tiên 19.7 to Tu Tiên Ký.

**Architecture:** Dedicated `ttk_tianjirooms` world component stores one room per owner on each shard, matching the source owner-based room identity. A room remains in the world when its entrance is packed. A player component saves the outside return point. All map exceptions are limited to registered room rectangles; client room markers rebuild those exceptions from replicated positions.

**Tech Stack:** DST Lua 5.1, original animation/texture assets, Python/Lupa tests using installed DST scripts.

**Spec:** User request in this task: plan and transfer Thiên Cơ Ốc, Lệnh Bài and associated Quyển Trục. Preserve crafting/deploy/enter/exit/recall/redeploy and save/load; no source mod runtime dependency.

## Global Constraints

- Work in current local mod directory; preserve all unrelated uncommitted files.
- `ttk_` namespace for gameplay. Preserve embedded original bank/build names.
- Original scroll recipe: papyrus 7, marble 15, livinglog 6, `ttk_lingshi1` 45; MAGIC_THREE crafting, no character restriction.
- Only owner may recall an entrance. Token is consumed on successful recall; failed recall changes nothing. A replacement token is craftable.
- Persist room furniture independently of entrance. Packed scroll retains owner and originating shard; reject cross-shard redeployment rather than silently linking a different room.
- Preserve source interior floor/wall/door placement, room size and fixed camera. No paid skins or source character systems.

## Review Focus

1. Reloading while indoors must not drown the player before map registration.
2. Recall while someone is inside must retain a safe exit even if the entrance is gone.
3. Another player must not recall or take ownership of a packed house.
4. Failed spawns/deploy checks must not consume scroll/token or duplicate rooms.
5. Full inventory, repeated actions, room-slot exhaustion and return points on water must fail safely.

## Task 1: persistent room and return routing

Files: `scripts/components/ttk_tianjirooms.lua`, `scripts/components/ttk_tianjireturn.lua`, `scripts/ttk_tianjimap.lua`, `tools/test_tianji.py`.

- [x] Write failing Lua tests for `GetRoom(owner)`, `OnSave/OnLoad`, `Contains(x,z)`, duplicate-owner lookup and allocation exhaustion.
- [x] Implement original 30-by-30 room allocation outside the map, refusing occupied/terrain slots. Register walkable 28-by-28 rectangles before player load.
- [x] Implement `Enter(house, player)` / `Exit(player)` with saved return point and safe portal fallback. Keep furniture and room identity when an entrance is removed.
- [x] Test owner isolation, invalid return points, failed room construction rollback and ordinary terrain delegation.

## Task 2: house, scroll and token

Files: `scripts/prefabs/ttk_tianji.lua`, `scripts/prefabs/ttk_tianji_interior.lua`, `main/ttk_tianji.lua`, `modmain.lua`.

- [x] Add failing tests for deploy/recall ownership, successful token consumption, save/load of packed owner/shard, client construction and registration.
- [x] Build `ttk_tianjiwu`, `ttk_tianji_juanzhou`, `ttk_tianji_lingpai` and interior prefabs. `Deploy` consumes scroll only after house/room/token exist; `Recall` emits packed scroll only after owner checks and successful spawn.
- [x] Register custom enter/exit action for normal players and ghosts on server/client stategraphs. Bind world/player components and preload map data.
- [x] Register recipes, inventory/minimap atlases and Vietnamese strings. Copy only required source assets with renamed paths.

## Task 3: visual integration and verification

Files: `main/ttk_tianji.lua`, `tools/test_tianji.py`, `README_VI.md`, `CREDITS.md`.

- [x] Install scoped room camera and lighting/temperature/shelter behavior, invisible perimeter walls and floor decoration using source dimensions.
- [x] Run tests through Lua 5.1, compile every mod Lua file, validate XML texture paths and ZIP checksums.
- [x] Review finished implementation independently, fix material findings and rerun affected tests.
- [x] Document recipe, ownership, recall/redeploy, shard constraint and verification limits.

## Progress / rulings

- Source checked statically from local original 19.7; loader never executed.
- Ruling: preserve owner/shard binding of packed scroll, fixing source's reassignment-on-deploy behavior so furniture cannot appear lost when someone else redeploys it.
- Ruling: no destructive hammer removal of entrance; use recall token so furniture remains reachable. Replacement token recipe prevents a lost token blocking recall.


## Verification results

- Lua 5.1 tests passed: allocation/owner isolation, scoped terrain/preload, room persistence, allocation exhaustion, return-point reload, portal fallback, owner-only recall, spawn failures, packed scroll save/load, shard lock, repeated action, client prefab boundary, active-item followers, mirror save/load, rain immunity cleanup and weather emitter restoration.
- Independent review identified rain protection, active-item followers and mirrored decal persistence; all corrected and covered by tests. Follow-up review found no further actionable defect.
- Full static audit: 150 Lua files compile; no missing static require/modimport; 152 atlas texture references and 127 animation archives validate.
- Actual isolated DST build 747465: `TTK_TIANJI_CREATE_PASS` then server restart and `TTK_TIANJI_RELOAD_PASS`. A real treasure chest and its gold nugget survived world save/load inside the room.
- Full mod boot was blocked by an unrelated missing food asset `images/cookbook_unagi_spice_salt.xml`. Live smoke therefore ran a scratch copy loading only Tian Ji + spirit stones. Production modules were not disabled. No live graphical/multiplayer interaction was performed.
- Logs: `.superpowers/dst-runtime-audit/tianji_create.log`, `.superpowers/dst-runtime-audit/tianji_reload.log`.
