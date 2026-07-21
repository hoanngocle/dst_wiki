# Reusable Category Crawler, Animals Mob Data, and Side Peek Design

## Objective

Build the first reusable Fandom category-ingestion flow for the DST wiki. The
first configured category is `Category:Animals`: discover exactly 35 direct
namespace-0 pages, exclude six reviewed non-DST exclusives before detail crawl,
publish the remaining 29 DST Mob pages, ignore all subcategories, merge records
by verified prefab code, summarize meaningful page notes in Vietnamese, and
replace the centered item modal with a right-side peek.

The category framework must be reusable. Future category work should add a
configuration and, when necessary, an item-type normalizer instead of copying
discovery, retry, checkpoint, storage, audit, or export code.

## Relationship to Existing Mob/Boss Work

This design is a focused category-ingestion and presentation slice. It does not
replace the broader Mob/Boss normalization contract in
`2026-07-21-mob-boss-catalog-normalization-design.md`.

The existing source-authority rule remains in effect: verified Lua/runtime facts
are authoritative for numeric gameplay and reward conflicts. The Animals crawl
replaces stale or incomplete Wiki-derived/presentation data for a matching
prefab, supplies missing DST facts, notes, summaries, images, and provenance,
and must never downgrade a verified source/runtime fact to an unverified Wiki
value.

## Confirmed Scope

- Source: `https://dontstarve.fandom.com/wiki/Category:Animals`.
- Discover exactly 35 direct namespace-0 pages as the reviewed category
  membership baseline.
- Exclude `Blue Whale`, `White Whale`, and `Wildbore` as Shipwrecked-only, and
  `Peagawk`, `Pog`, and `Glowfly` as Hamlet-only, before requesting page detail
  or images.
- Crawl, normalize, and publish exactly the remaining 29 DST Mob pages.
- Exclude namespace-14 category entries and never recurse into category children.
- Retain discovery evidence for both non-DST pages and excluded category entries
  in the audit.
- Normalize and display DST data only.
- Represent the 29 canonical records at Wiki-page level while supporting one or
  more verified prefab codes and variants per page.
- Reuse the existing Python crawler, generated catalog, local asset, and React
  application architecture.
- Do not fetch Fandom at browser runtime.
- Do not automatically delete existing catalog records in this delivery.

## Approaches Considered

### Extend the existing crawler with a reusable category profile — selected

Reuse the MediaWiki client, retry policy, SQLite checkpoint, JSONL storage,
image download, deterministic export, and validation paths. Add a generic
category configuration plus item-type normalizers. This has the smallest
maintenance surface and makes subsequent categories configuration-driven.

### Standalone Animals crawler

A separate crawler would isolate initial changes but duplicate retry, resume,
storage, image, validation, and export behavior. It would become expensive as
more categories are added.

### Browser-time Fandom fetch

Fetching when the side peek opens avoids generated artifacts but adds latency,
rate-limit exposure, layout-parser fragility, and an external runtime
dependency. It is unsuitable for a stable, searchable local wiki.

## Architecture and Data Flow

```text
Category configuration
        |
        v
MediaWiki category discovery + continuation
        |
        v
Namespace/redirect filtering and seed audit
        |
        v
Resumable page and image crawler
        |
        v
Immutable raw records + checkpoint + manifest
        |
        v
Item-type normalizer (Mob for Animals)
        |
        v
DST-only normalized records + note cache
        |
        v
Prefab-code merge + cleanup audit
        |
        v
Generated catalog and local assets
        |
        v
Right-side item peek
```

The crawler owns discovery, continuation, redirects, retries, checkpoints, raw
page storage, and image storage. Direct item fetches are coordinated through a
shared canonical-URL registry and content-addressed page cache so overlapping
categories do not request the same page twice. It does not contain
Animals-specific parsing. The selected normalizer owns DST filtering and the
Mob contract. Merge and validation run only after the crawl snapshot is
internally complete.

The web application reads generated local artifacts. Opening or navigating
inside the side peek never contacts Fandom.

## Reusable Category Configuration

Animals is represented by a reviewed configuration equivalent to:

```json
{
  "key": "animals",
  "sourceUrl": "https://dontstarve.fandom.com/wiki/Category:Animals",
  "categoryTitle": "Category:Animals",
  "expectedDirectPages": 35,
  "expectedPublishedPages": 29,
  "allowedNamespaces": [0],
  "excludedTitles": {
    "Blue Whale": "non_dst:shipwrecked",
    "White Whale": "non_dst:shipwrecked",
    "Wildbore": "non_dst:shipwrecked",
    "Peagawk": "non_dst:hamlet",
    "Pog": "non_dst:hamlet",
    "Glowfly": "non_dst:hamlet"
  },
  "game": "DST",
  "itemType": "mob",
  "tags": ["Animals"]
}
```

`key` determines isolated crawl/output state. `categoryTitle` is passed to the
MediaWiki API. `allowedNamespaces` prevents category recursion.
`expectedDirectPages` guards the 35-page namespace-0 membership and is not a
pagination limit. `excludedTitles` is the reviewed non-DST exclusion set, and
`expectedPublishedPages` guards the 29-page queue/output after those exclusions.
`game` selects version filtering, and `itemType` routes raw pages to a normalizer.

Every future category uses separate discovery checkpoint and output state. Two
category runs must not share category membership queues or silently overwrite
one another's snapshot. They intentionally share only the canonical-URL claim
registry and completed raw page cache.

## Shared URL Registry and Page Cache

All category crawlers coordinate direct page work through:

```text
data/crawled/fandom-url-registry.json
data/crawled/fandom-url-registry.lock
data/crawled/fandom-shared-pages/<sha256-canonical-url>.json
```

The human-readable registry contains one row per normalized canonical URL and
uses exactly `New`, `Doing`, or `Done`. A missing URL is inserted as `New`; a
worker atomically claims `New` as `Doing`; `Doing` and `Done` are skipped for
network fetch. Every discovery still appends its category key to the row so
overlap remains auditable.

Registry mutations hold an exclusive sidecar file lock and replace the JSON
atomically. A completed row points at a shared page artifact. A later category
that sees `Done` reuses that artifact in its isolated snapshot. A handled fetch
failure releases the row to `New` with error evidence. An unexpected process
death may leave `Doing`; it remains skipped until an operator explicitly
requeues it after review.

The complete operational contract is maintained in
`docs/category-crawler-knowledge.md` and applies to every future Category.

## Generated Artifact Layout

Category state and output are isolated by configuration key:

```text
data/crawled/fandom-categories/animals/
├── state.sqlite
├── seeds.jsonl
├── pages.jsonl
├── images.jsonl
├── errors.jsonl
├── manifest.json
└── images/original/<sha256>.<extension>

data/generated/categories/animals.json
data/generated/category-crawl-audits/animals.json
data/manual/category-prefab-mappings/animals.json
data/manual/category-note-summaries/animals.json
```

The generated catalog consumes the normalized category artifact rather than
the raw crawl files. A later aggregate audit may index category-specific audit
files, but one category run never rewrites another category's audit.

## Discovery and Crawl Semantics

Discovery requests all direct category members and follows MediaWiki
continuation tokens until exhausted. It records every returned member, then:

1. records and excludes disallowed namespaces without visiting them;
2. normalizes namespace-0 titles and URLs;
3. compares the direct namespace-0 membership with the reviewed 35-page set;
4. records the six configured non-DST titles and excludes them before any detail
   or image request;
5. resolves redirects for the remaining DST candidates;
6. deduplicates by resolved page ID and canonical URL;
7. compares the crawl queue with the reviewed 29-page publication count.

Animals export is blocked unless discovery contains exactly 35 unique
namespace-0 pages, the exact six reviewed non-DST exclusions are present, and
the resulting detail queue contains exactly 29 pages. A membership change
produces an added/removed diff for review; it never silently expands the crawl
or catalog.

Page processing stores the latest revision, page ID, title, canonical URL,
wikitext, rendered HTML, normalized plain text, categories, internal links, and
image references. Selected primary Mob images are downloaded to content-addressed
local storage. Re-running the same command resumes from SQLite state and does
not reprocess completed pages whose revision is unchanged.

## Canonical Mob Contract

Each published Animals record has a stable envelope:

```json
{
  "schemaVersion": 1,
  "identity": {
    "id": "base_game:koalefant_summer",
    "name": "Koalefant",
    "englishName": "Koalefant",
    "primaryCode": "koalefant_summer",
    "prefabCodes": ["koalefant_summer", "koalefant_winter"],
    "sourcePageId": 12345,
    "sourceUrl": "https://dontstarve.fandom.com/wiki/Koalefant",
    "revisionId": 67890
  },
  "classification": {
    "type": "mob",
    "tags": ["Animals"],
    "game": "DST"
  },
  "visual": {},
  "summary": null,
  "stats": {},
  "effects": {},
  "combat": {},
  "movement": {},
  "traits": {},
  "loot": {},
  "spawnsFrom": {},
  "notes": {},
  "variants": [],
  "evidence": []
}
```

The concrete record contains:

- identity, source page, revision, primary prefab code, and all verified aliases;
- `type: mob`, the `Animals` tag, and `game: DST`;
- a local visual asset and source metadata;
- a concise Mob summary;
- health and other supported general stats;
- DST effects such as sanity aura;
- damage, attack period, attack range, and other supported combat facts;
- walking and running speed;
- normalized special abilities and behavioral traits;
- obtainable items with quantity, chance, condition, method, source variant,
  clickable item reference, and evidence;
- spawn sources with clickable references when mapped;
- cleaned source notes and concise reviewed Vietnamese summaries;
- prefab/spawn code display data;
- provenance locators for material facts.

Every variable section uses `known`, `none`, or `unknown`. `none` is valid only
when the source proves absence. Parser gaps and unobserved data remain
`unknown`; they are never rendered as zero or false.

## DST-Only Normalization

The Mob normalizer recognizes version-labelled infobox values, repeated rows,
tables, templates, and notes. It selects DST-labelled values and rejects values
that are exclusive to Don't Starve, Reign of Giants, Shipwrecked, Hamlet, or
other non-DST variants.

When a page offers one unlabelled value shared by every edition, the normalizer
may use it for DST only when the page structure proves that it is shared. A
version ambiguity becomes `unknown` plus an audit reason rather than an
arbitrary first-column choice.

No DS/DLC tabs or alternate-edition values are exported to the Animals side
peek.

## Prefab Variants and Page-Level Canonical Records

The public result contains 29 page-level DST Mob records. A page may own multiple
verified DST prefab codes for seasonal, color, phase, or transformation
variants.

Each record declares one `primaryCode` and a deterministic `prefabCodes` list.
Variants preserve their code, label, ordering, visual, stats, loot, conditions,
and evidence when these differ. A prefab code may belong to only one canonical
Mob page.

The side peek displays a variant selector only when a record has multiple
variants. Selecting a variant changes only variant-specific values; shared
summary, notes, classification, and source context remain stable.

## Existing Catalog Merge and Cleanup Audit

The identity match is exact normalized namespace plus prefab code. Display-name
similarity is never sufficient for an automatic merge.

For one existing matching record:

- preserve its stable canonical ID and inbound catalog relationships;
- replace stale or incomplete Wiki/presentation fields with `known` Animals
  values;
- retain a valid existing value when the new section is `unknown`;
- preserve verified Lua/runtime gameplay facts when they conflict with a Wiki
  value;
- attach the new source revision and evidence;
- do not publish a second record for the same prefab code.

When several existing records share a code, one deterministic canonical record
is retained, inbound relationships are redirected, and the others are hidden
from public output. They are not deleted automatically.

Records that are empty, malformed, weakly identified, or no longer public are
reported with flags such as `missing_code`, `empty_details`, `invalid_schema`,
`missing_visual`, `orphan_record`, and `duplicate_code`.

`data/generated/category-crawl-audits/animals.json` records `created`,
`merged`, `kept`, `flagged`, `duplicate_hidden`, or `excluded` for each affected
record. Flagged rows contain `recommendedAction`, an optional `replacementId`,
reasons, and evidence. Destructive deletion is explicitly outside this
delivery.

## Notes and Vietnamese Summaries

The notes pipeline extracts the `Notes` section, meaningful gameplay notices
or callouts, and note-like infobox/table content. It removes citations,
navigation, patch-history trivia, duplicated text, and non-DST-only statements.

Each retained note stores cleaned source text, a source hash, a concise
Vietnamese summary, and review status. The existing summary translation cache
pattern is extended so unchanged source hashes reuse reviewed output and a
changed source invalidates the cache. Manual overrides remain available for
awkward or misleading automatic text.

For Animals, every existing meaningful note must have a reviewed Vietnamese
summary before export. A summary contains at most one or two short gameplay
ideas. A proven absence uses `none`; extraction or review gaps use `unknown`
and block the final quality gate when a source note exists.

## Right-Side Peek

The existing centered `ItemDetailModal` interaction becomes a shared
right-side peek without changing item-selection ownership.

On desktop, the panel is fixed to the right edge, fills `100dvh`, and is about
520-560 pixels wide. It has no radius on the right edge and rounded left
corners. A dim overlay covers the page, background scroll is locked, the header
is sticky, and the body scrolls independently.

On mobile, the panel fills the viewport and still enters from the right. It uses
dynamic viewport height so browser chrome does not hide controls.

The Mob content order is:

1. summary;
2. stats;
3. effects when present;
4. combat;
5. movement;
6. traits and special abilities;
7. loot;
8. spawn sources when present;
9. reviewed notes;
10. prefab code;
11. Fandom source link.

Stats, combat, and movement use responsive grids inspired by the supplied
reference images. Loot and spawn references use local sprites and remain
clickable. Selecting a related item replaces content inside the open side peek
and scrolls it to the top.

The panel closes through its close button, Escape, or overlay click. Focus is
trapped while open and restored to the originating item after close. Title
changes are announced for assistive technology. Motion honors
`prefers-reduced-motion`.

`none` sections are omitted unless an explanation is useful. `unknown` sections
display a concise `Chưa xác minh` state.

The source link, page title, and revision metadata remain available for Fandom
attribution and verification. The player-facing Notes section renders the
reviewed summary rather than republishing the full raw article text.

## Failure Handling

Export or validation hard-fails when:

- the direct namespace-0 discovery set is not exactly the reviewed 35 pages;
- the configured non-DST exclusion set is not the exact six reviewed titles, or
  one of those titles is absent from discovery;
- the post-exclusion crawl queue or published result is not exactly 29 pages;
- detail or image crawling is attempted for a configured non-DST title;
- a category child is queued for detail crawling;
- a published page has no verified prefab code or approved manual mapping;
- a prefab code belongs to multiple canonical pages;
- a known section violates its schema;
- a known loot reference cannot resolve to a catalog item;
- generated output and the merge/cleanup audit disagree;
- a source note exists without a reviewed Vietnamese summary;
- output would expose a non-DST value;
- an atomic generated-artifact replacement cannot complete.

Transient network and CDN errors retry with backoff. Exhausted failures remain
in the checkpoint and error report so a later invocation can resume. Redirect
cycles, duplicate canonical URLs, parser failures, missing images, and ambiguous
version fields retain raw evidence and explicit audit reasons. Missing images
do not remove a Mob, but visual status remains `unknown` and the image stays
retryable.

## Testing Strategy

Tests are written before implementation and cover:

- category continuation and discovery of exactly 35 namespace-0 pages;
- exclusion of the exact six Shipwrecked/Hamlet-only pages before detail and
  image requests, leaving exactly 29 queued and published DST pages;
- exclusion of every category child without recursive requests;
- redirect normalization, page-ID/URL deduplication, and drift diffs;
- interrupted crawl resume, transient retry, and unchanged-revision reuse;
- raw snapshot and category-state isolation;
- DST selection across multi-edition infobox/table layouts;
- ambiguity handling without first-column fallback;
- stats, effects, combat, movement, traits, loot, spawn sources, notes, code,
  images, and evidence;
- multi-prefab variants and code ownership;
- merge precedence, canonical-ID preservation, duplicate hiding, and cleanup
  flags;
- note source hashes, cache reuse, invalidation, manual override, and review
  gates;
- deterministic normalized JSON and audit output;
- right-side desktop layout and full-screen mobile layout;
- close behavior, focus trap, focus restoration, related-item navigation,
  scroll reset, accessible titles, and reduced motion;
- removal of the centered modal presentation.

The complete focused Python and Vitest suites, TypeScript compiler, ESLint,
Next.js build, generated-data validation, and audit validation must pass before
completion.

## Acceptance Criteria

- Discovery records exactly 35 direct namespace-0 pages, audits the six reviewed
  non-DST exclusions, and publishes exactly 29 DST Mob pages.
- `Blue Whale`, `White Whale`, `Wildbore`, `Peagawk`, `Pog`, and `Glowfly` are
  never crawled for detail, normalized, or published.
- No `Category:*` page is crawled recursively or published as a Mob.
- Every published Mob contains at least one verified DST prefab code.
- No prefab code belongs to two canonical Mob records.
- All normalized and rendered gameplay data is DST-only.
- Page-level records correctly retain prefab-specific variants.
- Matching existing data is merged without changing stable canonical IDs or
  losing verified source/runtime facts.
- Sparse, invalid, orphaned, and duplicate existing records are visible in a
  non-destructive cleanup audit.
- Every meaningful source note has a short reviewed Vietnamese summary.
- All browser-facing text and images are served from generated local artifacts.
- Source page and revision attribution remain available for every crawled Mob.
- Item details open as an accessible right-side peek on desktop and a
  full-screen right-side drawer on mobile.
- Generated artifacts are deterministic and all required verification suites
  pass.

## Future Category Extension

A new category should require only a reviewed configuration and an existing or
new item-type normalizer. Discovery, continuation, checkpointing, retry,
storage, raw snapshots, image download, note caching, audit structure, atomic
export, and side-peek shell remain shared.

Expected-count drift is reviewed per category. Category-specific exceptions,
manual prefab mappings, and note-summary overrides remain explicit data rather
than hidden parser branches.
