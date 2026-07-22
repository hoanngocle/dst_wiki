# Category Crawler Batch 7 Review

## Scope

This batch reviews 19 Fandom category sources with the established rules:

- DST content only.
- Direct namespace-0 pages only.
- Child categories and other namespaces are recorded but never traversed.
- Canonical crawler URL/code is the unique identity.
- Registry entries in Doing or Done are reused; only absent URLs may fetch detail.
- Redirects, overview/group pages, guides, disambiguations, community mods, and non-DST exclusives are excluded before registry insertion.

## Source review

| Key | Direct | Child | Other | Excluded | Publish | Type |
|---|---:|---:|---:|---:|---:|---|
| light_sources | 94 | 0 | 0 | 28 | 66 | content |
| magic_tab | 30 | 0 | 0 | 10 | 20 | item |
| magic_tier_1 | 19 | 0 | 1 | 5 | 14 | item |
| magic_tier_2 | 14 | 0 | 0 | 5 | 9 | item |
| meats | 48 | 1 | 0 | 15 | 33 | food |
| melee_weapons | 38 | 0 | 0 | 15 | 23 | weapon |
| mineable_objects | 32 | 0 | 0 | 9 | 23 | object |
| mob_dropped_items | 205 | 3 | 0 | 63 | 142 | item |
| mob_housing | 52 | 0 | 0 | 29 | 23 | structure |
| mob_spawning_entities | 124 | 2 | 1 | 47 | 77 | object |
| mobs | 279 | 22 | 0 | 105 | 174 | mob |
| mods | 3 | 0 | 0 | 3 | 0 | skip |
| monster_foods | 9 | 0 | 0 | 3 | 6 | food |
| monsters | 64 | 4 | 4 | 24 | 40 | mob |
| neutral_creatures | 36 | 2 | 0 | 14 | 22 | mob |
| nightmare_state_indicator | 9 | 0 | 0 | 0 | 9 | object |
| nocturnals | 23 | 0 | 0 | 6 | 17 | mob |
| ocean | 64 | 0 | 0 | 33 | 31 | content |
| passive_creatures | 63 | 1 | 0 | 33 | 30 | mob |

Totals: 1,206 direct memberships, 35 child categories, six other-namespace rows, 447 rejected memberships, and 759 published memberships. Category:Mods is intentionally skipped because Mods is an overview and The Lost Fragment/The Screecher are community modifications rather than official DST entities.

## Canonical dedupe

- Published memberships: 759.
- Unique canonical URLs: 491.
- Existing registry URLs reused: 462.
- New canonical URLs to fetch: 29.
- Canonical URLs shared by at least two requested categories: 199.
- Repeated memberships eliminated at fetch time: 268.

The dedupe key is the output of normalize_crawler_url, not the display title. A URL already in Doing or Done must not be fetched again.

## New URL review

The 29 new accepted pages are:

1. Beehive
2. Boaraudience
3. Broken Clockworks
4. Crawling Horror
5. Evergreen
6. Harp Statue
7. Hound Mound
8. Light Flower
9. Lumpy Evergreen
10. Lureplant
11. Marble Pillar
12. Marble Tree
13. Mermhouse
14. Night Hand
15. Pig Torch
16. Rabbit Hole
17. Runic Turf
18. Shadow Tentacle
19. Shadow Watcher
20. Slurtle Mound
21. Spider Den
22. Spilagmite
23. Splumonkey Pod
24. Stalagmite
25. Suspicious Dirt Pile
26. Tallbird Nest
27. Terrorbeak
28. Terrorclaw
29. Wavey Jones

Spider Eggs is retained as DST content despite an incomplete Fandom category tag that only names Reign of Giants; its page contains the DST variant and the URL is already a reviewed registry artifact. Parrot Pirate, by contrast, is explicitly Shipwrecked-only and is rejected even though an older aggregate crawl left its URL in the shared registry.

## Namespace audit

- Child categories are concentrated under Meats, Mob Dropped Items, Mob Spawning Entities, Mobs, Monsters, Neutral Creatures, and Passive Creatures.
- Other namespaces consist of one Board Thread row, four Thread rows, and one User sandbox.
- None of these 41 rows enter a config seed set or recursive traversal.
