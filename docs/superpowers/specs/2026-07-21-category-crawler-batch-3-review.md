# Category crawler batch 3 review and implementation spec

Date: 2026-07-21

## Scope

Process the eight requested categories through the approved reusable category
crawler. Accept direct namespace-0 pages only, do not recurse into child
categories, and publish DST content only.

## Review policy

1. Keep pages explicitly available in Don't Starve Together.
2. Exclude Don't Starve, Reign of Giants, Shipwrecked, and Hamlet exclusives
   before detail fetch.
3. Keep `Parrot Pirate` as a manual DST exception despite incomplete Fandom game
   metadata.
4. Exclude overview/filter/category-mismatch pages that are not publishable
   entities for the requested category.
5. Exclude six colored Moonlens aliases as `duplicate:canonical_redirect`; keep
   the canonical `Moonlens` page.
6. Ignore all child categories and non-main namespaces.
7. Reuse `Doing` and `Done` canonical URL rows; only missing or `New` rows may
   be claimed for detail fetch.

## Reviewed matrix

| Config | Direct | Child | Excluded | Accepted | Done | New | Missing | Unique in batch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `a_new_reign` | 110 | 2 | 18 | 92 | 49 | 2 | 41 | 82 |
| `ancient_tab` | 15 | 0 | 1 | 14 | 14 | 0 | 0 | 2 |
| `ancient_tier_1` | 10 | 0 | 1 | 9 | 8 | 0 | 1 | 2 |
| `ancient_tier_2` | 7 | 0 | 0 | 7 | 7 | 0 | 0 | 1 |
| `animals` | 35 | 4 | 6 | 29 | 6 | 23 | 0 | 22 |
| `birds` | 17 | 0 | 7 | 10 | 0 | 5 | 5 | 2 |
| `boss_monsters` | 37 | 0 | 9 | 28 | 8 | 0 | 20 | 20 |
| `clockwork_monsters` | 8 | 0 | 2 | 6 | 1 | 0 | 5 | 6 |

Totals: 292 direct memberships, 201 canonical pages before review, 195 accepted
memberships, 166 accepted canonical URLs, 77 existing `Done`, 23 existing `New`,
66 missing, and 29 duplicate memberships across categories.

## Execution order

Run `ancient_tab`, `ancient_tier_1`, `ancient_tier_2`, `animals`, `birds`,
`clockwork_monsters`, `boss_monsters`, then `a_new_reign`. This maximizes reuse
before the broad expansion category. Every run must finish with zero failures,
zero pending pages, and zero pending images.

## Data contract

Seven new configs record exact direct/published counts and exclusion reasons.
The existing Animals config remains authoritative. Raw detail pages, images,
links, recipes, and notes remain in shared/category crawl artifacts; the tracked
registry snapshot and Markdown control table are regenerated only after a clean
registry audit.
