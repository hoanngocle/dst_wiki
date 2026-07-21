# DST Aggregate Category Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crawl the complete `Category:Don't Starve Together` listing without recursive categories or duplicate detail fetches.

**Architecture:** Enumerate all MediaWiki categorymember pages until continuation ends, then retain namespace-0 articles only. Resolve redirects before registration, exclude six colored Moonlens aliases that collapse to the canonical Moonlens page, and let the shared URL registry reuse every `Done` page while fetching only missing canonical URLs.

**Tech Stack:** Python 3, MediaWiki API, JSON category config, durable shared crawler registry, unittest.

## Global Constraints

- Stop discovery only after the API returns all 899 category members.
- Publish direct namespace-0 pages only; do not recurse into 12 child categories.
- Ignore nine User/User blog members.
- Treat canonical URL as the dedupe key.
- Skip network detail fetch for `Doing` and `Done`; fetch only missing/`New` URLs.
- Keep raw page HTML/wikitext and notes in the normal category artifacts.
- Game scope and tag are DST / `Don't Starve Together`.

---

### Task 1: Lock the reviewed aggregate scope with TDD

**Files:**
- Modify: `tests/crawl_wiki/test_category_config.py`
- Create: `data/config/wiki-categories/dont_starve_together.json`

**Interfaces:**
- Consumes: `load_category_config(key)`.
- Produces: category key `dont_starve_together` with 878 direct and 872 published pages.

- [ ] Add a failing config test asserting `expectedDirectPages=878`, `expectedPublishedPages=872`, item type `content`, DST tag, and six `duplicate:canonical_redirect` exclusions.
- [ ] Run the focused test and confirm it fails because the config is missing.
- [ ] Add the minimal JSON config with the six colored Moonlens aliases excluded.
- [ ] Re-run focused config/seed tests and confirm they pass.

### Task 2: Document the 899-member review and registry overlap

**Files:**
- Modify: `docs/category-crawler-control.md`
- Create: `docs/superpowers/specs/2026-07-21-dst-aggregate-category-review.md`

**Interfaces:**
- Consumes: `/private/tmp/dst_aggregate_discovery.json` and the current registry snapshot.
- Produces: durable review decisions and queue counts for later category batches.

- [ ] Record 899 total members: 878 namespace-0 articles, 12 child categories, nine User/User blog pages.
- [ ] Record 872 canonical publications, 523 unique `Done` URLs reused, and 349 missing URLs to crawl.
- [ ] Record the ignored namespace titles and six Moonlens alias exclusions.

### Task 3: Crawl missing canonical pages and export the final snapshot

**Files:**
- Generate: `data/crawled/fandom-categories/dont_starve_together/`
- Modify: `data/crawled/fandom-url-registry.json`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: reviewed config and durable live registry.
- Produces: 872-page aggregate output with no duplicate detail fetches.

- [ ] Run the category crawler with a page budget above 872 and normal image collection.
- [ ] Verify 523 prior pages are reused and only 349 missing canonical URLs are fetched.
- [ ] Verify `pages=872`, `failures=0`, `pending_pages=0`, and `pending_images=0`.
- [ ] Audit the live registry, export its JSON snapshot, and regenerate the shared URL table.

### Task 4: Verify and commit

**Files:**
- Verify all modified files and ignored crawl artifacts.

**Interfaces:**
- Consumes: completed aggregate output and snapshot.
- Produces: a clean local commit on `codex/category-batch-3`.

- [ ] Verify manifest counts, empty errors, unique canonical page URLs, and registry `Done` membership.
- [ ] Run Python tests, Vitest, TypeScript, ESLint, production build, and `git diff --check`.
- [ ] Copy ignored category output into the main checkout for persistence.
- [ ] Commit the reviewed aggregate category batch.
