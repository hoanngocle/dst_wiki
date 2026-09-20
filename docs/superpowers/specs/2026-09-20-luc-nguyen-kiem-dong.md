# Lục Nguyên Kiếm Đồng — approved design

Historical baseline. The later user-approved elemental expansion in `../plans/2026-09-20-luc-nguyen-elements.md` supersedes the recipe, auxiliary damage range, and visual-only element behavior below. Current range is 10–20%, recipe is one of each six held swords, and impacts apply the specified elemental effects.

User approved implementation and delegated it to GPT-5.6 Sol High on 2026-09-20. Do not restart approval/design discussions.

## Gameplay
- Add an independent TuTienKy weapon, prefab `ttk_lucnguyenkiemdong`, usable by every character without the original cultivation mod enabled.
- Display name: Lục Nguyên Kiếm Đồng. Original visual source: Tu Tiên 19.7 (`mods/mod_steam/3235319974`), `xd_jingwei_blowdart` inventory, equipped, and projectile art. Preserve attribution.
- Base damage 50, attack range 8. No ammo items. 1,000 shots maximum and initially full; one durability per shot, not per auxiliary sword. Empty weapon remains but cannot shoot. One `ttk_lingshi1` restores 100 shots, capped at 1,000; refuse when full. Save/load preserves remaining shots and enhancement state.
- Recipe at Science Two: 2 livinglog, 6 goldnugget, 2 purplegem, 2 ttk_lingshi2. No character restriction.
- A successfully landed primary shot which actually crits through installed Solo triggers exactly one volley. Use Solo's actual crit outcome; never reroll a second independent critical chance. No new inherent crit chance. Without Solo the weapon still shoots normally but has no Solo crit-triggered volley.
- Each proc independently chooses an integer 1–6 swords. Choose that many distinct elemental models without replacement. Each individual sword independently rolls an integer percentage 10–50 inclusive of the shot's original normal damage before critical multipliers. Take a per-shot damage snapshot so equipment switching or later upgrades do not change an in-flight hit. Preserve Solo weapon enhancement; do not reuse crit-amplified values or apply player offensive multipliers twice.
- Auxiliary swords do not crit, reroll Solo effects, trigger another volley, consume durability, or inflict elemental debuffs. Defense/armor should still function. Preserve attacker attribution.
- Swords originate around the player's position when proc happens, fan left/right, then curve to pursue the actual moving target. Each sword damages its target once and disappears; no return/orbit/repeated strikes. Clean up on target death/removal, owner removal, or flight timeout. Reference Lục Mạch movement but do not import its autonomous repeated-attack system or opaque callbacks.
- Six models/colors: Kim = Vô Tướng Kiếm `xd_wxj` white/silver; Mộc = Thanh Trúc Phong Vân Kiếm `xd_htz_qzj` green; Thủy = Tinh La Kiếm `xd_xlj` blue; Hỏa = Phần Thiên Kiếm `xd_ftj` orange/red; Thổ = Tiên Kiếm `xd_xianjian_builder` gold/earth; Lôi = Ma Kiếm `xd_mo_builder` purple. Inspect actual bank/build/symbols; builder prefab names need not equal their animation zip names. Original silhouettes should remain visible. Modest matching trails, no persistent orbiting swords.

## Scope and operating constraints
- Work directly in existing workspace: the whole mods folder is currently untracked and contains required user work, so a HEAD worktree would omit the project. Back up only files this feature changes before editing.
- Never reset, clean, mass-add, commit unrelated changes, edit original source mods, publish, install into Steam, or open the game UI automatically.
- Keep changes within TuTienKy, feature tooling/docs, and its generated web data if existing exporter supports the new item. No unrelated Next.js UI work.
- Verify Lua 5.1 and real component integrations with the available game scripts and Solo code. Distinguish headless checks from visual confirmation in final report.
