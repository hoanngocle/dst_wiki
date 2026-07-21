# Category Crawler Batch 4 Review

## Scope

Sources: Flying Creatures, Followers, Food, Food & Gardening Filter, Food Tab, From Beyond, Fruits, and Fuel. Discovery uses direct namespace-0 members only and ignores child categories.

| Key | Direct | Child | Excluded | Publish | Done before crawl | Missing |
|---|---:|---:|---:|---:|---:|---:|
| flying_creatures | 16 | 1 | 4 | 12 | 12 | 0 |
| followers | 42 | 1 | 7 | 35 | 33 | 2 |
| food | 184 | 10 | 62 | 122 | 122 | 0 |
| food_gardening_filter | 19 | 0 | 0 | 19 | 19 | 0 |
| food_tab | 15 | 0 | 5 | 10 | 10 | 0 |
| from_beyond | 105 | 0 | 1 | 104 | 103 | 1 |
| fruits | 12 | 1 | 3 | 9 | 9 | 0 |
| fuel | 119 | 2 | 30 | 89 | 83 | 6 |

The batch has 400 accepted memberships and 375 unique canonical URLs. Twenty-five memberships overlap another category in this batch. Before crawl, 366 canonical URLs are `Done` and nine are absent from the registry.

## Reuse decisions

- `Food` reuses the previously reviewed `food.json` unchanged at 184 direct / 122 published pages and does not need another crawl.
- All `Done` URLs are reused by canonical URL. Only the nine missing DST pages may perform detail fetches.

## New DST pages

- Followers: Abigail, Merm.
- From Beyond: Brightshade Husk.
- Fuel: Berry Bush, Grass Tuft, Pine Cone, Slurtle Slime, Spiky Bush, Tentacle Spots.

Wikitext evidence was checked before registration: each page contains a DST section, DST recipe/infobox marker, or an explicit statement that it is part of Don't Starve Together.

## Exclusions

- Flying Creatures: Mobs (`non_item:overview`); Packim Baggims, Poison Mosquito, Stink Ray (`non_dst:shipwrecked`). Ignore child Category:Birds.
- Followers: Bottlenose Ballphin, Packim Baggims, Prime Ape, Wildbore (`non_dst:shipwrecked`); Pog, Ro Bin (`non_dst:hamlet`); Spiders (`non_item:overview`). Ignore child Category:Spiders.
- Food: reuse the existing 62 reviewed exclusions and ignore ten child categories.
- Food & Gardening Filter: no exclusions.
- Food Tab: Farm (`non_dst:dont_starve`); Fish Farm, Mussel Bed, Mussel Stick (`non_dst:shipwrecked`); Sprinkler (`non_dst:hamlet`).
- From Beyond: Combat (`non_item:overview`).
- Fruits: Coconut, Coffee Beans (`non_dst:shipwrecked`); Fruit (`non_item:overview`). Ignore child Category:Crock Pot Recipes.
- Fuel: Turfs (`non_item:overview`); Ashy Turf, Bamboo, Bamboo Patch, Bioluminescence, Blubber, Cloth, Coffee Plant, Elephant Cactus, Jungle Tree Seed, Jungle Turf, Magma Turf, Meadow Turf, Palm Leaf, Snakeskin Rug, Tar, Tidal Marsh Turf, Vine, Viney Bush, Volcano Turf (`non_dst:shipwrecked`); Clippings, Cultivated Turf, Dense Turf, Flat Stone Turf, Lawn Turf, Mossy Turf, Painted Sand Turf, Rainforest Turf, Stone Road Turf, Wild Plains Turf (`non_dst:hamlet`). Ignore child Category:Fertilizer and Category:Turf Items.
