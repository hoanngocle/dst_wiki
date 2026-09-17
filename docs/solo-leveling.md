# Solo Leveling wiki

Tab `/solo-leveling` uses the checked-in data in `data/generated/solo-leveling.json`.
Each topic has its own tab, with search scoped to that tab and 12 entries per
page. Existing `#solo-<topic>` links still open the matching tab; entry links
such as `#daily-26` also select the correct tab and page. The public page has
10 topic tabs; configuration, effects and source-reader tabs have been removed. Their
old hash links fall back to the gameplay guide. The page does not send the
configuration/effects groups or file inventory to the browser.
It includes the complete text/tables from `solo_leveling/Wiki.txt`, the in-game
help book, crafting recipes, daily/guild quests, Rank exams, both shop catalogues,
shadow talents. Equipment effects and literal tuning/configuration are retained
in the generated dataset for offline reference.

The guild shop uses the shared `GameSprite` inventory-icon component and Rank
filters. Its cards distinguish price in guild credits, items received per
purchase, and purchases available per shop cycle. The extractor reuses images
from `public/data/items.json` plus the local Star Caller's Staff wiki image,
with explicit aliases for catalogue names that differ from actual game
prefabs. Original Lua purchase fields and source references remain available
under each card's details. Bone Armor (`armorskeleton`) has no local inventory
image, so its card explicitly shows that the image is unavailable.

Other topics use icon cards too. Crafting displays the actual product quantity,
each ingredient's inventory image and quantity, and the required station.
Dungeon products use their actual `prefab_id` images and dungeon credits;
generic placeholder prefabs are not used as product pictures. All 53 dungeon
products and all five shadows have local mod images. Shadow talents are shown
as individual level milestones. Quests emphasize objectives and rewards and
offer target thumbnails where available. Guides and Wiki tables keep their
full-width reading layout. Every original text line remains accessible.
Category filters cover station, quest difficulty and Rank.
Entries without a matching image use a topic symbol.
The item catalogue excludes internal UI containers, status/projectile helpers,
decorative arena objects and companions already documented in the shadows tab.
Treasure-scroll recipe aliases and the five forms of Tà Thuật Đen are
consolidated into single cards. Usable enchantment stones, weapons, crafting
stations, extraction corpses, creatures and luck potions remain.
Daily quests and Rank Up exams use full-width horizontal rows. Daily difficulty
is labeled and color coded: green for easy, amber for medium, rose for hard.
Objectives and rewards remain visible; progress rules and conditions expand
under each row. Existing `#solo-exams` links still open Rank Up.
Rank Up rows have distinct Rank colors: D green, C blue, B violet, A amber,
S rose; labels remain visible alongside the colors.
Daily Quest has a difficulty filter above the list. Guild quests also use
horizontal rows, with separate Rank and browsing difficulty filters. Guild
definitions declare Rank but no difficulty: the UI groups E–D as easy, C–B as
medium and A–S as hard, clearly labeled as a browsing classification rather
than a mod field. Original objectives, delivery requirements, duration and
rewards remain accessible under each row's details.

The visual publisher decodes only referenced KTEX atlases into PNG, preserving
the atlas UV coordinates. It uses installed Pillow, performs format/size checks,
and never modifies mod textures or executes Lua. There are 40 published icon
atlases in `public/solo-leveling/icons/`.

Regenerate after updating the local mod:

```powershell
python -m tools.extract.build_solo_leveling_data
# Use a Python environment with Pillow (the bundled Codex Python has it):
python -m tools.extract.publish_solo_leveling_assets
python -m unittest tests.extract.test_build_solo_leveling_data
python -m unittest tests.extract.test_publish_solo_leveling_assets
```

The extractor reads local files without executing the mod. It folds literal
TUNING assignments, references to already-defined tuning values and the mod's
explicit EXP remapping loops. Arbitrary functions and values supplied by the
game/server are not evaluated. The configuration section describes the static
defaults; conditional overrides in `hh_config.lua` are excluded, since they
depend on the chosen difficulty/server settings. Actual values may depend on
the server.

The extractor creates `public/solo-leveling/sources.json` and a ZIP with the
original Lua, XML and TXT files for local offline reference. These archives
and the local `solo_leveling/` input directory are excluded from Git.
The file inventory lists every file, including binary animation, textures,
manifest and audio; the source reader does not preview arbitrary binary assets.

`Wiki.txt` is preserved as published by the mod. The crafting section separately
notes discrepancies with current recipes (marble for Hắc Nguyệt Hồ and the
90-second duration of Phúc Lạc Dược II).
