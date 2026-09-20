# EVA v1.0 — Thần thông Sinh

## Approved scope

Add only Thần thông Sinh to the existing EVA mod and preserve the approved single-gown EVA appearance. User approved the listed numbers and requested implementation by GPT-5.6 Sol High after planning. Subsequent explicit correction: EVA retains ONLY the Soul counter from Calliope, not Calliope abilities. This is an independent implementation using DST APIs; Tu Tiên must not be installed to run it.

## Behavior

| Feature | Contract |
| --- | --- |
| Activation | Configurable keyboard shortcut, default G; do not fire while typing, menus, ghost/dead, or inappropriate busy state. Server validates every request. |
| Duration | 15 seconds; no stacking or refresh while active. |
| Cooldown | 60 seconds from accepted activation; retained across save/load; reconnect cannot reset it. |
| Projectiles | Acquire a valid enemy within 12 units every 0.2 s, one projectile for 80 base damage. Respect target defenses; do not apply weapon crit/Soul Strike multipliers. |
| Aura | Follow owner; radius 6, 67 base damage per valid enemy every 0.5 s. |
| Healing | 5% current maximum health at seconds 0, 3, 6, 9, 12; respect effective health cap; exactly five ticks. |
| Shield | Snapshot 25% maximum health at activation, consume finite shield points, pass overflow damage through; expire with buff or earlier depletion. No invulnerability flag. |
| Target safety | Valid live combat targets; prefer current combat target and hostile threats. Never self, ghosts, untargetable entities, allied followers or neutral scenery; players excluded with PvP off. Revalidate at impact. |
| Feedback | Lavender/silver projectile, aura, shield using verified built-in DST visuals where possible; concise activation/cooldown feedback. |
| Cleanup | End tasks, FX and shield on death/ghost/despawn/removal. On load restore cooldown but not active buff/free heals. |

No new resource cost or dependence on scythe equipped. Existing source schedules an immediate heal plus a zero-delay periodic task: intentionally avoid that double-instant heal.

## EVA identity correction (latest user instruction)

- Remove Calliope Soul Strike, Soul-driven weapon crit, kill healing, immortality/sleep recovery, automatic resurrection, special sanity/aura/graveyard/Kiara effects, and Soul loss from being hit or passive decay.
- Preserve Soul HUD, configured maximum and saved count: +1 normal valid kill, +10 ghost, +30 epic; all valid EVA kills count, including Life without the scythe equipped. Soul has no combat effect/cost in this release. Preserve reset on actual death/ghost transition.
- Preserve configurable basic stats and approved art. Scythe becomes EVA's normal melee weapon with existing base damage/durability/recipe, no spell, crit, special reach or sanity penalty.
- Remove wine/hat/kazoo from EVA crafting. Keep old prefab registrations solely to avoid deleting existing save items; legacy item config fallbacks may remain internal, not exposed as EVA powers.
- Update descriptions/options to reflect EVA + Soul + Life rather than Calliope perks. Internal prefab names stay compatible with existing saves.

## Validation

Automated Lua behavior checks for timers, damage, target safety, shield overflow, RPC rejection and cleanup; syntax checks for all mod Lua; packaged archive CRC and content parity. Character and weapon assets must remain byte-identical. Separate in-game smoke checklist for host/client visual and gameplay verification; do not claim game-tested without actual evidence.

## Evidence and paths

- Editable mod: `mods/EVA_v1.0` (internal prefab `calliope_mori`).
- Reference only: `mods/eva-assets-work/skill-audit/decoded/scripts/prefabs/xd_luoshen_krss.lua`, `xd_luoshen_shentong_fx.lua`.
- DST core: `C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`.
- Do not copy unreadable/partially decoded source into executable Lua.
