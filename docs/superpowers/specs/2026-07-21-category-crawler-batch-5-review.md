# Category Crawler Batch 5 Review

## Scope

Discovery uses direct namespace-0 members only. Child categories and User/Talk/Board members are recorded for audit but are never followed.

| Key | Direct | Child | Other namespace | Excluded | Publish | Done before crawl | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|
| gameplay | 112 | 24 | 1 | 32 | 80 | 29 | 51 |
| hats | 63 | 0 | 0 | 23 | 40 | 40 | 0 |
| healing | 192 | 2 | 0 | 53 | 139 | 134 | 5 |
| health_loss | 51 | 0 | 0 | 14 | 37 | 34 | 3 |
| hostile_creatures | 112 | 4 | 0 | 40 | 72 | 68 | 4 |
| indestructible_object | 87 | 0 | 0 | 48 | 39 | 28 | 11 |
| infobox_missing_crafting_description | 52 | 0 | 7 | 0 | 52 | 52 | 0 |

The seven valid categories contain 459 accepted memberships and 443 canonical URLs. Sixteen memberships overlap another category in this batch. Before crawl, 373 canonical URLs are `Done`; 70 are absent from the registry.

## Source decision: Gems

`https://dontstarve.fandom.com/wiki/Gems` is a namespace-0 disambiguation/article page. `Category:Gems` exists only as a redirect back to `Gems`, so it has no direct Category member list. It is redundant with the individual gem pages already present in the registry and is skipped instead of receiving a synthetic category config.

## New accepted DST pages

- Gameplay (51): Abyss, Armor, Biomes, Bridge, Caves, Character quotes, Characters, Charlie, Clothes, Console/Commands, Cooking, Crafting, Day-Night Cycle, Death, Durability, Earthquake, Farming, Fire, Freezing, Glossary, Graveyard, Health, Hunger, Inventory, Items, Lightning, Map, Mods, Moon Cycle, Nightmare Cycle, Non-renewable resources, Ocean, Pig Village, Combat, Rain, Road, Ruins, Sanity, Saving, Seasons/Winter, Seasons/World, Sleeping, Soundtrack, Structures, Sunken Forest, Surface World, Survivor Speed, World Customization, World Generation, World Generation Screen, World Retrofit.
- Healing (5): Butter, Butterfly Wings, Mosquito Sack, Small Jerky, Spider Gland.
- Health Loss (3): Charlie, Fire, Freezing.
- Hostile Creatures (4): Ghost, Hound, Suspicious Peeper, Werepig.
- Indestructible Object (11): Bones, Bridge, Cave Light, Eye Bone, Grave, Obelisk, Pig King, Pond, Sinkhole, Walrus Camp, Worm Hole.

Bridge, Charlie, Fire, and Freezing overlap another category, leaving exactly 70 new canonical URLs rather than 74 new memberships.

## Exclusion policy

- Gameplay keeps shared or explicitly documented DST mechanics/content. It excludes 32 Don't Starve-only, Reign of Giants-only, Shipwrecked-only, Hamlet-only, or disambiguation pages. The 24 child categories and `User:Queron/Caves` are audit-only.
- Hats excludes all 23 missing pages because they are Shipwrecked/Hamlet/single-player-only; all 40 accepted hats were already `Done`.
- Healing excludes 53 other-game-only pages or group pages such as Crop Seeds; five base-game items confirmed to exist in DST are retained.
- Health Loss excludes 14 other-game-only or overview pages, including Monster Food.
- Hostile Creatures excludes other-game creatures and overview/group pages. Blue Hound and Red Hound are excluded as redirects to canonical Hound.
- Indestructible Object excludes 48 Adventure Mode, Pocket Edition, Shipwrecked, or Hamlet objects and retains eleven shared/DST objects.
- Infobox missing crafting description is a maintenance category. Its 52 namespace-0 pages are retained as provenance membership without any new detail fetch; seven discussion/user namespace members are ignored.

The authoritative title-to-reason mapping is stored in the seven reviewed JSON configs and locked by config tests.
