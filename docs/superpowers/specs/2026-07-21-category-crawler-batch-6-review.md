# Category Crawler Batch 6 Review

## Scope

Discovery follows direct category membership only. Namespace-0 pages are reviewed for DST publication; child categories and other namespaces are recorded but never traversed.

| Key | API pages | Direct | Child | Other namespace | Excluded | Publish | Done before crawl | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| innocents | 1 | 30 | 0 | 0 | 14 | 16 | 16 | 0 |
| items | 3 | 987 | 32 | 1 | 306 | 681 | 636 | 45 |

The two sources contain 697 accepted memberships and 692 canonical URLs. Five accepted Innocents memberships also occur in Items: Bee, Birds, Butterfly, Moleworm, and Rabbit. Before crawl, 647 canonical URLs are `Done`; 45 are absent from the registry.

## Category:Innocents

- Keep 16 DST mobs; all already have `Done` artifacts.
- Exclude six Shipwrecked-only pages: Bottlenose Ballphin, Dogfish, Doydoy, Jellyfish, Sealnado, and Swordfish.
- Exclude eight Hamlet-only pages: Dung Beetle, Elder Mandrake, Glowfly, Hippopotamoose, Pangolden, Piko, Pog, and Poison Dartfrog.
- This source has no child category or other namespace member.

## Category:Items

- The MediaWiki continuation chain contains 1,020 members across three API pages: 987 namespace-0 pages, 32 child categories, and `User:Bluegeist/Sandbox5`.
- Keep 681 DST item pages. Reuse 636 `Done` artifacts and fetch only the 45 missing canonical details.
- Exclude 139 Shipwrecked-only, 95 Hamlet-only, 12 Don't Starve-only, and two Reign of Giants-only pages.
- Exclude ten redirect aliases, including the six colored Moonlens aliases and aliases resolving to Shipwrecked-only Woodlegs' Keys.
- Exclude 30 overview/group pages and 15 category mismatches. This includes `Items`, the per-game item lists, Armor, Clothes, Cooking stations, Books, Gems, Kitchen sets, Wall, event overview pages, and Runic Turf.
- All 32 child categories are audit-only and are not recursively crawled.

## New accepted DST pages

The 45 new canonical URLs are:

- Base/shared items (8): Ashes, Beefalo Horn, Broken Shell, Bunny Puff, Pig Skin, Slurper Pelt, Thulecite Fragments, Walrus Tusk.
- The Forge items (27): Barbed Helm, Blacksmith's Edge, Blossomed Wreath, Clairvoyant Crown, Crystal Tiara, Darts, Feathered Reed Tunic, Feathered Wreath, Flower Headband, Hearthsfire Crystals, Infernal Staff, Jagged Grand Armor, Jagged Wood Armor, Living Staff, Molten Darts, Nox Helm, Petrifying Tome, Pith Pike, Reed Tunic, Resplendent Nox Helm, Spiral Spear, Steadfast Grand Armor, Steadfast Stone Armor, Stone Splint Mail, Tome of Beckoning, Wood Armor, Woven Garland.
- The Gorge items (10): Cookpot, Crab Trap, Flour, Iron Key Gorge, Large Casserole Dish, Large Cookpot, Slaughter Tools, Small Casserole Dish, Syrup Pot, Tree Tapping Kit.

The Forge and The Gorge are Don't Starve Together events, so their concrete item pages remain in DST scope even though they are not direct members of `Category:Don't Starve Together`.

## Authoritative decisions

The complete title-to-reason mappings are stored in `data/config/wiki-categories/innocents.json` and `data/config/wiki-categories/items.json`. Config regression tests lock counts, item types, tags, representative exclusions, and representative accepted DST pages.
