# Category crawler batch 2 review and implementation spec

Date: 2026-07-21

## Scope

Crawl only direct namespace-0 members of the 14 reviewed Fandom categories. Do
not recurse into child categories. Publish DST data only and preserve the shared
canonical-URL registry with `New`, `Doing`, `Done` states.

## Review policy

1. Keep pages explicitly categorized for Don't Starve Together.
2. Exclude pages that are exclusive to Don't Starve, Reign of Giants,
   Shipwrecked, or Hamlet before any detail fetch.
3. Exclude overview/group pages and category-mismatch pages that are not a
   publishable item for the category.
4. Keep `Ice` in Cooling and Food as an explicit DST exception even though its
   Fandom metadata also contains a Shipwrecked category.
5. Ignore child categories and non-main namespaces.
6. Canonicalize URLs before registry lookup. `Doing` and `Done` skip detail
   network fetch; only missing or `New` entries may be claimed.

## Reviewed matrix

| Config | Direct | Child | Excluded | Accepted | Existing registry | New URL | Unique in batch |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cooking_filter` | 15 | 0 | 1 | 14 | 5 | 9 | 0 |
| `crock_pot_recipes` | 83 | 0 | 15 | 68 | 2 | 66 | 11 |
| `cooling` | 26 | 1 | 4 | 22 | 1 | 21 | 0 |
| `craftable_items` | 496 | 5 | 137 | 359 | 63 | 296 | 166 |
| `craftable_structures` | 165 | 2 | 72 | 93 | 5 | 88 | 47 |
| `crafting_stations` | 15 | 1 | 3 | 12 | 1 | 11 | 6 |
| `decorations_filter` | 52 | 0 | 3 | 49 | 0 | 49 | 1 |
| `eggs` | 8 | 0 | 1 | 7 | 1 | 6 | 1 |
| `equipable_items` | 198 | 5 | 67 | 131 | 31 | 100 | 22 |
| `events` | 68 | 0 | 0 | 68 | 0 | 68 | 55 |
| `fertilizer` | 13 | 0 | 1 | 12 | 0 | 12 | 3 |
| `food` | 184 | 10 | 62 | 122 | 11 | 111 | 51 |
| `fight_tab` | 32 | 0 | 17 | 15 | 6 | 9 | 0 |
| `fishes` | 20 | 0 | 14 | 6 | 1 | 5 | 0 |

Totals: 1,375 direct memberships, 906 canonical pages before review, 647 unique
accepted DST URLs, 88 existing registry URLs, and 559 new URLs. There are 383
cross-category duplicate memberships.

## Sequential execution

Run narrower/reuse-heavy categories first, then broad categories last:

1. `cooking_filter`, `cooling`, `crafting_stations`, `eggs`, `fertilizer`,
   `fight_tab`, `fishes`.
2. `decorations_filter`, `crock_pot_recipes`, `events`, `food`.
3. `equipable_items`, `craftable_structures`, `craftable_items`.

Repeat a category command until its pending page count reaches zero when the
accepted count exceeds the per-run page budget. After the batch, audit the live
registry, export its JSON snapshot, regenerate the shared URL table, and run the
Python plus frontend verification suites.

## Data contract

Each category config records exact direct/published counts and explicit
exclusion reasons. Each successful detail produces a shared raw artifact and a
category projection. Notes stay in raw detail data so downstream normalization
can summarize their main meaning without losing source evidence.
