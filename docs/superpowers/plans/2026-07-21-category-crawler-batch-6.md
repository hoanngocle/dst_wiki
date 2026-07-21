# Category Crawler Batch 6 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review and crawl `Category:Innocents` and `Category:Items` with DST-only scope, direct-member traversal, and shared canonical URL dedupe.

**Architecture:** Discover every `categorymembers` continuation page, retain only namespace-0 direct pages, and record child/other namespaces without recursion. Review exclusions before registry insertion, reuse all `Doing`/`Done` canonical artifacts, and fetch detail only for 45 accepted URLs absent from the 1,223-entry starting registry.

**Tech Stack:** Python 3, MediaWiki API, JSON category configs, durable URL registry, unittest, Markdown audit documents.

## Global Constraints

- Game scope is DST only.
- Direct namespace 0 only; 32 child categories and one User page are audit-only.
- Canonical URL is the dedupe key; `Doing` and `Done` skip detail network fetch.
- Preserve raw HTML, raw wikitext, notes, links, and original image artifacts.
- The batch has 1,017 direct memberships, 697 accepted memberships, and 692 canonical URLs: 647 already `Done`, 45 missing, and five cross-category duplicates.
- Exclude other-game-only pages, redirect aliases, overview/group pages, and category mismatches before registry insertion.

---

### Task 1: Lock the two reviewed configs with TDD

**Files:**
- Modify: `tests/crawl_wiki/test_category_config.py`
- Create: `data/config/wiki-categories/innocents.json`
- Create: `data/config/wiki-categories/items.json`

**Interfaces:**
- Consumes: `load_category_config(key)` and the reviewed direct-member snapshot.
- Produces: `innocents` as `30/16` mob pages and `items` as `987/681` item pages.

- [x] Add `test_loads_reviewed_batch_six_configs` asserting count/type/tag tuples and representative keep/exclusion decisions.
- [x] Run `python3 -m unittest tests.crawl_wiki.test_category_config -q` and verify RED because both configs are absent.
- [x] Create the two minimal JSON configs using only supported exclusion reasons.
- [x] Run `python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds -q` and verify GREEN.

### Task 2: Persist source review and queue decisions

**Files:**
- Create: `docs/superpowers/specs/2026-07-21-category-crawler-batch-6-review.md`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: three-page Items discovery, one-page Innocents discovery, wikitext/category evidence, and the 1,223-entry registry snapshot.
- Produces: durable source counts, exclusion rationale, child-category audit, and the exact 45-page new-DST list.

- [x] Record direct/child/other/excluded/published counts for both sources.
- [x] Record the 45 accepted missing pages and five cross-category duplicate memberships.
- [x] Document that The Forge/The Gorge event items are DST content, while Shipwrecked/Hamlet/Reign of Giants/Don't Starve-only pages are excluded.

### Task 3: Crawl both categories sequentially

**Files:**
- Generate: `data/crawled/fandom-categories/innocents/`
- Generate: `data/crawled/fandom-categories/items/`
- Modify: `data/crawled/fandom-url-registry.json`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: reviewed configs and the live shared registry.
- Produces: complete outputs for 16 Innocents pages and 681 Items pages, plus a 1,268-URL `Done` registry.

- [x] Crawl `innocents` first and verify it performs no new detail fetch.
- [x] Crawl `items` with a page budget above 681 so one invocation can process all 45 missing details.
- [x] Audit the live registry, export its snapshot, and regenerate the Shared item URL table.

### Task 4: Verify and commit

**Files:**
- Verify all modified tracked files and ignored generated outputs.

**Interfaces:**
- Consumes: complete category outputs and registry snapshot.
- Produces: a clean local commit on `codex/category-batch-6`.

- [x] Verify exact page counts, raw HTML/wikitext, empty errors, no pending queues, canonical uniqueness, and category memberships.
- [x] Copy both ignored output directories into the main checkout and compare them byte-for-byte.
- [x] Run Python tests, Vitest, TypeScript, ESLint, production build, and `git diff --check`.
- [x] Commit the reviewed batch.
