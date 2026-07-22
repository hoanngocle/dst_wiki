# DST Guides Library Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crawl reviewed DST Guide pages and publish a searchable `/guides` library with statically generated `/guides/[slug]` reading pages.

**Architecture:** The existing category crawler discovers and stores direct Guide pages. A focused Python exporter converts accepted crawl artifacts into a compact index plus validated detail payloads. Next.js Server Components load those local payloads, while one client search component owns filtering and mobile table-of-contents interaction.

**Tech Stack:** Python 3 standard library, MediaWiki crawler, JSON artifacts, Next.js 16 App Router, React 19, TypeScript 5, Tailwind CSS 4, Vitest, Testing Library.

## Global Constraints

- Crawl only direct namespace-zero members of `Category:Guides`; never recurse into `Category:Dedicated Servers`.
- Publish only content applicable to Don't Starve Together.
- Exclude the `Guides` overview, Board Thread, Shipwrecked-only, Hamlet-only, Reign of Giants-only, single-player-only, and obsolete event guides.
- Every published guide requires a unique ID, unique slug, valid local cover image, Vietnamese summary, non-empty sections, and revision metadata.
- Routes are `/guides` and `/guides/[slug]`; Guide details never use the item side peek.
- Preserve the current cool gray and blue visual system with design dials `5 / 3 / 5`.
- Do not introduce a new runtime dependency.

---

### Task 1: Reviewed Guides category configuration

**Files:**
- Create: `data/config/wiki-categories/guides.json`
- Modify: `tests/crawl_wiki/test_category_config.py`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: `load_category_config(path: Path) -> CategoryConfig`
- Produces: category key `guides`, item type `guide`, exact discovery and publication counts

- [ ] **Step 1: Add a failing config test**

Add a test that loads `guides.json` and asserts `source_url`, `category_title`, `item_type == "guide"`, namespace `[0]`, exact `expected_direct_pages`, exact `expected_published_pages`, and a non-empty exclusion reason for every rejected namespace-zero title.

- [ ] **Step 2: Verify the test fails**

Run: `python3 -m unittest tests.crawl_wiki.test_category_config.CategoryConfigTest.test_loads_reviewed_guides_config -v`

Expected: failure because `data/config/wiki-categories/guides.json` does not exist.

- [ ] **Step 3: Review all direct pages and add the config**

Use MediaWiki API discovery, resolve redirects, inspect game applicability, and create a schema-version-1 config. `excludedTitles` maps every rejected namespace-zero title to one of these explicit reason families: `overview`, `not_dst`, `shipwrecked_only`, `hamlet_only`, `reign_of_giants_only`, `obsolete_event`, or `insufficient_guide_content`.

- [ ] **Step 4: Verify config and seed normalization**

Run: `python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds -v`

Expected: all tests pass and `expectedPublishedPages + len(excludedTitles) == expectedDirectPages`.

- [ ] **Step 5: Record the reviewed queue**

Add the Guides source, reviewed counts, exclusion policy, and `Doing` status to `docs/category-crawler-control.md` without manually duplicating registry rows.

- [ ] **Step 6: Commit**

Run: `git add data/config/wiki-categories/guides.json tests/crawl_wiki/test_category_config.py docs/category-crawler-control.md && git commit -m "feat: review DST guides category"`

### Task 2: Crawl and validate Guide source artifacts

**Files:**
- Modify: `data/crawled/fandom-url-registry.json`
- Generate ignored: `data/crawled/fandom-categories/guides/`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: `data/config/wiki-categories/guides.json`
- Produces: complete category manifest, seeds, page snapshots, image assets, and Done registry entries

- [ ] **Step 1: Audit the registry before crawling**

Run: `python3 -m tools.crawl_wiki.cli registry-audit --registry data/crawled/fandom-url-registry.json`

Expected: zero invalid, zero `Doing`, and zero stale entries.

- [ ] **Step 2: Crawl the reviewed category**

Run: `python3 -m tools.crawl_wiki.cli crawl-category --config data/config/wiki-categories/guides.json --output data/crawled/fandom-categories/guides --registry data/crawled/fandom-url-registry.json --page-budget 500 --delay 0.05`

Expected: manifest is complete, page count equals `expectedPublishedPages`, and failure lists are empty.

- [ ] **Step 3: Validate source integrity**

Check that every accepted seed has one page payload, raw HTML and wikitext are non-empty, downloaded image checksums match, canonical URLs are unique, and excluded titles are absent from published pages.

- [ ] **Step 4: Snapshot and audit the registry**

Run: `python3 -m tools.crawl_wiki.cli registry-snapshot --registry data/crawled/fandom-url-registry.json --output data/crawled/fandom-url-registry.json`

Expected: all registry items are `Done`; existing canonical rows gain only the Guides category membership.

- [ ] **Step 5: Mark the queue Done and commit**

Run: `git add data/crawled/fandom-url-registry.json docs/category-crawler-control.md && git commit -m "data: crawl reviewed DST guides"`

### Task 3: Normalize and export Guide payloads

**Files:**
- Create: `tools/extract/guides.py`
- Create: `tests/extract/test_guides.py`
- Modify: `tools/extract/cli.py`
- Generate: `public/data/guides/index.json`
- Generate: `public/data/guides/pages/<slug>.json`
- Generate: `public/assets/guides/`

**Interfaces:**
- Produces: `export_guides(crawl_root: Path, output_root: Path, asset_root: Path) -> dict`
- Produces index schema 1 with `guides: GuideListEntry[]`
- Produces detail schema 1 with `sections: GuideSection[]` and `toc: GuideTocEntry[]`

- [ ] **Step 1: Write failing normalization tests**

Fixtures must prove deterministic slugging, heading anchors, unsafe tag removal, local image rewriting, cover selection, Vietnamese summary fallback, topic classification, audience classification, reading-time calculation, duplicate-slug rejection, and rejection of empty or imageless pages.

- [ ] **Step 2: Verify the tests fail**

Run: `python3 -m unittest tests.extract.test_guides -v`

Expected: import failure for `tools.extract.guides`.

- [ ] **Step 3: Implement the minimal exporter**

Define immutable normalized guide records, sanitize source HTML with an explicit element and attribute allowlist, select the first valid article image as cover, copy assets atomically, derive summaries from the lead section when no reviewed Vietnamese summary exists, and write sorted JSON with stable checksums.

- [ ] **Step 4: Add the CLI command**

Add `export-guides` with explicit `--crawl`, `--output`, and `--assets` paths. The command exits non-zero before replacing output when any accepted page violates the contract.

- [ ] **Step 5: Run tests and export real artifacts**

Run: `python3 -m unittest tests.extract.test_guides -v`

Run: `python3 -m tools.extract.cli export-guides --crawl data/crawled/fandom-categories/guides --output public/data/guides --assets public/assets/guides`

Expected: tests pass, index count equals the Guide manifest page count, every detail and cover path exists, and two consecutive exports are byte-identical.

- [ ] **Step 6: Commit**

Run: `git add tools/extract/guides.py tests/extract/test_guides.py tools/extract/cli.py public/data/guides public/assets/guides && git commit -m "feat: export normalized DST guides"`

### Task 4: Guide catalog TypeScript contract

**Files:**
- Create: `app/lib/guide-catalog.ts`
- Create: `app/lib/guide-catalog.test.ts`

**Interfaces:**
- Produces: `parseGuideIndex(value: unknown): GuideIndex`
- Produces: `parseGuideDetail(value: unknown): GuideDetail`
- Produces: `filterGuides(guides, query, topic, audience): readonly GuideListEntry[]`

- [ ] **Step 1: Write failing parser and filter tests**

Cover valid payloads plus duplicate IDs, duplicate slugs, missing covers, empty summaries, empty sections, duplicate heading anchors, malformed revisions, accent-insensitive Vietnamese search, topic filters, and audience filters.

- [ ] **Step 2: Verify RED**

Run: `npx vitest run app/lib/guide-catalog.test.ts`

Expected: module-not-found failure.

- [ ] **Step 3: Implement strict parsing and pure filtering**

Parse unknown JSON without unchecked casts. Validate every required nested field and build Sets for duplicate checks. Keep filtering deterministic and independent of React.

- [ ] **Step 4: Verify GREEN**

Run: `npx vitest run app/lib/guide-catalog.test.ts`

Expected: all Guide catalog tests pass.

- [ ] **Step 5: Commit**

Run: `git add app/lib/guide-catalog.ts app/lib/guide-catalog.test.ts && git commit -m "feat: add guide catalog contract"`

### Task 5: Header and Guide index route

**Files:**
- Modify: `app/components/site-header.tsx`
- Modify: `app/components/site-header.test.tsx`
- Create: `app/components/guide-browser.tsx`
- Create: `app/components/guide-browser.test.tsx`
- Create: `app/guides/page.tsx`
- Create: `app/guides/loading.tsx`

**Interfaces:**
- Consumes: `GuideListEntry[]`, `filterGuides`
- Produces: shared `SiteHeader active="guides"` and accessible Guide catalog UI

- [ ] **Step 1: Write failing header and browser tests**

Assert `/guides` navigation, active state, search, topic and audience filtering, result count announcement, reset action, no-results state, card image dimensions, and card links to `/guides/<slug>`.

- [ ] **Step 2: Verify RED**

Run: `npx vitest run app/components/site-header.test.tsx app/components/guide-browser.test.tsx`

Expected: missing Guides navigation and component module.

- [ ] **Step 3: Implement the shared header update**

Add `{ id: "guides", href: "/guides", label: "Guide" }`. Preserve a single desktop nav line and make the compact mobile header horizontally usable without clipping the active item.

- [ ] **Step 4: Implement the Guide browser and page**

Keep `app/guides/page.tsx` as a Server Component that parses the imported local index. Isolate query and filters in `guide-browser.tsx` with semantic labels, keyboard focus, responsive one/two-column layout, real covers, and no client data fetch.

- [ ] **Step 5: Add a shape-matched loading page**

Render header, intro blocks, filter skeletons, and card skeletons with fixed dimensions and reduced-motion-safe styling.

- [ ] **Step 6: Verify GREEN**

Run: `npx vitest run app/components/site-header.test.tsx app/components/guide-browser.test.tsx`

Expected: all tests pass.

- [ ] **Step 7: Commit**

Run: `git add app/components/site-header.tsx app/components/site-header.test.tsx app/components/guide-browser.tsx app/components/guide-browser.test.tsx app/guides/page.tsx app/guides/loading.tsx && git commit -m "feat: add Guides catalog route"`

### Task 6: Static Guide reading route

**Files:**
- Create: `app/components/guide-article.tsx`
- Create: `app/components/guide-article.test.tsx`
- Create: `app/guides/[slug]/page.tsx`
- Create: `app/guides/[slug]/loading.tsx`
- Create: `app/guides/[slug]/not-found.tsx`

**Interfaces:**
- Consumes: `GuideDetail`, local index payload
- Produces: `generateStaticParams()`, per-guide metadata, article renderer

- [ ] **Step 1: Write failing article tests**

Assert breadcrumb, title, cover, summary, reading metadata, desktop table of contents, mobile disclosure, stable heading IDs, safe section HTML, source link, revision information, and the absence of item side-peek semantics.

- [ ] **Step 2: Verify RED**

Run: `npx vitest run app/components/guide-article.test.tsx`

Expected: module-not-found failure.

- [ ] **Step 3: Implement the article component**

Render a constrained reading column with sticky desktop navigation and a native `details` disclosure on mobile. Use local images with reserved dimensions. Source HTML is already sanitized by the exporter and must not be transformed in the browser.

- [ ] **Step 4: Implement the dynamic route**

Resolve `params` as a Promise per Next.js 16, call `notFound()` for missing slugs, generate all accepted static params from the index, and generate title and description metadata from parsed local data.

- [ ] **Step 5: Verify GREEN and route build**

Run: `npx vitest run app/components/guide-article.test.tsx`

Run: `npx tsc --noEmit`

Expected: tests and TypeScript pass.

- [ ] **Step 6: Commit**

Run: `git add app/components/guide-article.tsx app/components/guide-article.test.tsx app/guides && git commit -m "feat: add static Guide reading pages"`

### Task 7: Guide verification and documentation

**Files:**
- Modify: `docs/category-crawler-control.md`
- Create: `docs/superpowers/specs/2026-07-22-guides-crawl-review.md`

**Interfaces:**
- Consumes: final manifest, registry, index, detail pages, and build output
- Produces: auditable review counts and completed queue status

- [ ] **Step 1: Validate every Guide artifact**

Prove index/detail count equality, unique IDs/slugs/canonical URLs, valid checksums, valid local images with positive dimensions, non-empty summaries and sections, and no rejected title in output.

- [ ] **Step 2: Run full verification**

Run: `python3 -m unittest discover -s tests -p 'test_*.py'`

Run: `npm test`

Run: `npx tsc --noEmit`

Run: `npm run lint`

Run: `npm run build`

Expected: every command exits zero and the build lists `/guides` plus all generated `/guides/[slug]` paths.

- [ ] **Step 3: Complete review documentation**

Record direct, excluded, published, reused, newly crawled, image, and failure counts. Include the exact game-scope decisions and final registry totals.

- [ ] **Step 4: Commit**

Run: `git add docs/category-crawler-control.md docs/superpowers/specs/2026-07-22-guides-crawl-review.md && git commit -m "docs: record Guides crawl verification"`
