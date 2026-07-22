# Category Crawler Batch 9 Review

## Scope

Batch 9 reviews 14 supplied Fandom sources under the established crawler
contract: DST-only, direct namespace 0 only, no recursive traversal, canonical
URL/code as global identity, and reuse of every valid `Doing`/`Done` artifact.

Twelve Category sources are published. `Treasure Hunting Tab` and the `Wall`
article are audit-only and do not create configs or registry rows.

## Source review

| Key | Direct | Child | Other | Excluded | Publish | Action |
|---|---:|---:|---:|---:|---:|---|
| shadow_magic_filter | 31 | 0 | 0 | 0 | 31 | New config |
| spiders | 14 | 0 | 1 | 1 | 13 | New config |
| structures | 278 | 4 | 3 | 123 | 155 | New config |
| survival_tab | 34 | 0 | 0 | 10 | 24 | New config |
| survivor_items_filter | 21 | 0 | 0 | 0 | 21 | New config |
| tools_filter | 38 | 0 | 2 | 0 | 38 | New config |
| tools_tab | 12 | 0 | 1 | 2 | 10 | New config |
| turf_items | 50 | 0 | 0 | 18 | 32 | New config |
| trees | 27 | 0 | 0 | 10 | 17 | New config |
| treasure_hunting_tab | 4 | 0 | 0 | 4 | 0 | Skip: Hamlet-only |
| vegetables | 33 | 1 | 1 | 7 | 26 | New config |
| wall | 0 | 0 | 0 | 1 | 0 | Skip: overview article |
| weapons | 58 | 3 | 0 | 23 | 35 | New config |
| weather | 11 | 0 | 0 | 4 | 7 | New config |

Totals: 611 direct memberships, eight child categories, eight other-namespace
rows, 202 rejected memberships, and 409 published memberships.

## Canonical dedupe

- Published memberships: 409.
- Unique canonical URLs: 358.
- Existing registry URLs reused: 355.
- New canonical URLs fetched: 3.
- Canonical URLs shared by at least two requested Category outputs: 50.
- Repeated memberships removed at fetch time: 51.

The only new accepted DST pages are `Merm Head`, `Pig Head`, and `Quagmire
Firepit`. The live registry moved from 1,302 to 1,305 rows and audits as 1,305
valid `Done`, zero `New`, zero `Doing`.

## Review decisions

- `Treasure Hunting Tab` contains only Ball Pein Hammer, Disarming Tools, Gold
  Pan, and Magnifying Glass; all four are Hamlet-only.
- `Wall` describes a family of wall entities across multiple games. It is an
  overview article, not a single canonical entity for publication.
- `Structures` rejects 123 direct pages: single-player exclusives, overview or
  event pages, plus `Mutated Merm` and `Suspicious Peeper` as category mismatch.
- `Floor` redirects to `Turfs`, already rejected as an overview; neither creates
  a registry row. `Snow` resolves to `Seasons/Winter`, whose canonical page has
  a DST section, so the canonical URL is retained once.
- `Obsidian Axe` and `Obsidian Machete` are excluded as Shipwrecked-only before
  redirect resolution.
- Child categories and User/Template/Thread/Board/User-blog rows are audit-only
  and never traversed.

## Crawl result

The 12 outputs contain 409 pages, 334 original images, and 292,986 links with
zero failures, zero pending pages, and zero pending images. All three new detail
pages were claimed exactly once; every other accepted page used the shared
artifact cache.
