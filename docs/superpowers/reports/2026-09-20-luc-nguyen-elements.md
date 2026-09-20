# Lục Nguyên elemental expansion

Status: implemented and verified locally. Independent Sol High review found no remaining actionable gameplay/API defects after the shield-scope and hit-counter persistence fixes.

## Scope

- Five new held swords plus the existing Tinh La; six separate elemental passives.
- Each sword recipe uses one Trung Phẩm Linh Thạch and the approved tripled material quantities.
- Gun recipe consumes one of each sword. Crit volley damage changes to independently rolled 10–20% per sword, with elemental impact effects.
- Auxiliary damage must preserve defense and attribution without extra crit, recursive passives, or unwanted ally/PvP hits.
- README, credits and website catalog describe the revised recipes and separate held/ranged effects.

## Verification record

- `mods/TuTienKy/tools/test_elemental_swords.py`: PASS. Elemental values, hostile filtering, nonstacking slow, independent owner cooldowns, post-defense shield absorption and callback isolation, cadence persistence, five held prefabs, native Kim planar, exact recipes and Lua 5.1 parsing.
- `mods/TuTienKy/tools/test_lucnguyen.py`: PASS. Distinct 1–6 swords, independent 10–20% damage rolls, curved pursuit, scoped auxiliary damage and installed Solo `hh_player:DoAttackDamage` at deterministic 100%/0% crit.
- `mods/TuTienKy/tools/test_lucnguyen_prefab.py`: PASS. Charges, refill, save/load, enhanced damage snapshot, six projectiles and client/server split.
- `mods/TuTienKy/tools/test_tinhlakiem.py`: PASS. Existing 300/1,000 uses, 100 damage at depletion, real trader donor consumption, save/load and character independence.
- `mods/TuTienKy/tools/test_weapon_solo.py`: PASS, three compatibility groups.
- `mods/TuTienKy/tools/audit_registration.py`: PASS, 60 configurations, 185 Lua files, 186 atlas texture references and 158 animation archives.
- `tools/build_tu_tien_ky_web.py`: PASS, 169 catalog entries and 370 supporting references. Separate catalog checks confirmed six new entries, local icons, exact gun ingredients, reverse crafting links, one Trung Phẩm stone per sword, and no removed existing entries. Only existing gun/stone records changed.
- `tools/run_lucnguyen_smoke.py`: PASS, exit 0. Full current mod loaded in a separate offline dedicated world; `.superpowers/lucnguyen-audit/lucnguyen_smoke.log` records `[00:00:42]: TTK_LUCNGUYEN_SMOKE_PASS`. Checks include all six recipe registrations, Kim native planar 10, new/Tinh La initial durability, real locomotor 0.75 multiplier, real combat shield absorption, gun projectile hit, 2→1→0 charges without deleting the gun, real trader refill, save/load and six homing swords hitting/cleaning up.

Graphical client appearance (especially Tiên/Ma hand attachment, scale and effect presentation) has not been verified. Source build symbols were inspected; dedicated success does not certify visual quality. Solo was tested through installed Lua code, not a live multiplayer client session. No deployment or player save modification was performed.

## Implementation decisions

- New five held swords start full at 1,000 uses and break when depleted. Tinh La retains its existing 300/1,000 starting uses, nonbreaking behavior and donor repair.
- Ranged Thủy slow lasts 2 seconds; held Tinh La slow lasts 3 seconds, matching the separate approved tables.
- Owner cooldowns for ranged Mộc and Thổ are independent, preventing cooldown bypass by switching weapons.
- Shield absorbs actual combat health loss after normal defenses; negative healing, unrelated health costs and regeneration are not shield damage.

## Main files

- `mods/TuTienKy/scripts/ttk_elemental_combat.lua`
- `mods/TuTienKy/scripts/prefabs/ttk_elemental_swords.lua`
- `mods/TuTienKy/main/ttk_elemental_swords.lua`
- Existing Tinh La registration/prefab, Lục Nguyên registration/prefab/rules/combat bridge, and `modmain.lua`.
- Five new namespaced inventory atlases/textures; existing six animation archives reused.
- Elemental feature tests, updated gun tests and dedicated smoke script.
- README, credits, web exporter, generated catalog and inventory icons.
