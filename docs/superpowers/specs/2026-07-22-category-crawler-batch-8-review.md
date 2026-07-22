# Category Crawler Batch 8 Review

## Scope

Batch 8 reviews 13 supplied Fandom categories under the established crawler rules:

- DST content only.
- Direct namespace-0 pages only; no recursive category traversal.
- Canonical crawler URL/code is the global unique identity.
- Existing `Doing` or `Done` URLs are reused without a detail fetch.
- Shipwrecked-only, Hamlet-only, Don't Starve-only, overview/group, disambiguation, and category-mismatch pages are excluded before registry insertion.
- `Passive Creatures` is a drift check and full reuse of the batch-7 config/output, not a recrawl.

## Source review

| Key | Direct | Child | Other | Excluded | Publish | Action |
|---|---:|---:|---:|---:|---:|---|
| plants | 66 | 1 | 0 | 29 | 37 | New config |
| passive_creatures | 63 | 1 | 0 | 33 | 30 | Reuse Done |
| portal | 9 | 0 | 0 | 7 | 2 | New config |
| ranged_weapons | 15 | 0 | 0 | 8 | 7 | New config |
| rare_blueprint_exclusive | 38 | 0 | 0 | 3 | 35 | New config |
| refine_tab | 20 | 0 | 0 | 5 | 15 | New config |
| resources | 106 | 3 | 0 | 27 | 79 | New config |
| resurrection | 11 | 0 | 0 | 3 | 8 | New config |
| ruins_creatures | 13 | 1 | 0 | 2 | 11 | New config |
| science | 99 | 0 | 0 | 14 | 85 | New config |
| science_tier_2 | 147 | 0 | 5 | 51 | 96 | New config |
| science_tier_1 | 117 | 0 | 1 | 54 | 63 | New config |
| seafaring_filter | 14 | 0 | 0 | 1 | 13 | New config |

Totals: 718 direct memberships, six child categories, six other-namespace rows, 237 rejected memberships, and 481 published memberships.

## Canonical dedupe

Across all 13 requested sources:

- Published memberships: 481.
- Unique canonical URLs: 362.
- Existing registry URLs reused: 357.
- New canonical URLs requiring detail fetch: 5.
- Canonical URLs shared by at least two requested categories: 109.
- Repeated memberships removed at fetch time: 119.

Excluding the already-complete `Passive Creatures` output, the 12 new configs contain 451 published memberships, 334 unique canonical URLs, 329 reused URLs, five new URLs, 107 duplicated URLs, and 117 repeated memberships.

The five new accepted DST pages are:

1. Cave Banana Tree
2. Cave Lichen
3. Reeds
4. Spiky Tree
5. Totally Normal Tree

## Review decisions

- `Passive Creatures` still matches its reviewed 63 direct/30 published config exactly, including the `Parrot Pirate` Shipwrecked exclusion and `Snurtle` redirect exclusion.
- `Plants`, `Resources`, `Science Tier 1`, and `Science Tier 2` contain most non-DST-only rows; their Shipwrecked/Hamlet pages are rejected even when another category also references them.
- `Books`, `Chess Pieces`, `Dart`, `Food`, `Goggles`, `Mobs`, `Mushroom Lights`, `Mushrooms`, `Non-renewable resources`, `Plants`, `Research Points List`, `Shadow Creature`, `Slingshot Ammo`, `Wall`, and `Weeds` are group/overview pages and do not represent one publishable entity.
- `Year of the Dragonfly` is DST content but is rejected from `Seafaring Filter` as a category-mismatch page rather than a seafaring entity.
- `Ice` is retained because the page contains a DST entity/variant despite also carrying Shipwrecked crafting information.
- Child categories `Trees`, `Followers`, `Minerals`, `Non-Renewable`, `Plants`, and `Spiders` are audit-only. The five User/Board/Talk rows in Science Tier 2 and one Thread row in Science Tier 1 are also excluded by namespace.
