# Category Crawler Batch 4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review and crawl Flying Creatures, Followers, Food, Food & Gardening Filter, Food Tab, From Beyond, Fruits, and Fuel with DST-only scope and canonical registry reuse.

**Architecture:** Discover direct namespace-0 members without recursive child categories, exclude overview and other-game-exclusive titles before detail, and register accepted canonical URLs in the durable shared registry. Reuse the existing reviewed Food config and all `Done` artifacts; fetch only nine missing DST pages.

**Tech Stack:** Python 3, MediaWiki API, JSON category configs, durable shared crawler registry, unittest.

## Global Constraints

- Game scope is DST only.
- Namespace 0 only; child categories are recorded but never crawled recursively.
- Canonical URL is the dedupe key; `Doing`/`Done` skip detail network fetch.
- Existing `food.json` remains authoritative at 184 direct / 122 published pages.
- Preserve raw HTML/wikitext and normal image artifacts.

---

### Task 1: Lock seven new reviewed configs with TDD

**Files:**
- Modify: `tests/crawl_wiki/test_category_config.py`
- Create: `data/config/wiki-categories/flying_creatures.json`
- Create: `data/config/wiki-categories/followers.json`
- Create: `data/config/wiki-categories/food_gardening_filter.json`
- Create: `data/config/wiki-categories/food_tab.json`
- Create: `data/config/wiki-categories/from_beyond.json`
- Create: `data/config/wiki-categories/fruits.json`
- Create: `data/config/wiki-categories/fuel.json`

**Interfaces:**
- Consumes: `load_category_config(key)`.
- Produces: reviewed direct/published counts `16/12`, `42/35`, `19/19`, `15/10`, `105/104`, `12/9`, and `119/89`.

- [x] Add a failing config test for all seven keys and representative exclusion reasons.
- [x] Run the focused test and confirm failure because configs are missing.
- [x] Add minimal configs with the exact reviewed exclusions.
- [x] Re-run config/seed tests and confirm green.

### Task 2: Record the review and queue state

**Files:**
- Modify: `docs/category-crawler-control.md`
- Create: `docs/superpowers/specs/2026-07-21-category-crawler-batch-4-review.md`

**Interfaces:**
- Consumes: discovery JSON and current 1,144-URL registry snapshot.
- Produces: durable decisions for 400 accepted memberships / 375 canonical URLs.

- [x] Record all category counts, child categories, exclusions, and Food reuse.
- [x] Record 366 canonical URLs already `Done`, nine missing URLs, and 25 cross-category duplicate memberships.
- [x] Record direct DST evidence for the nine missing pages.

### Task 3: Crawl categories sequentially

**Files:**
- Generate: `data/crawled/fandom-categories/<category>/`
- Modify: `data/crawled/fandom-url-registry.json`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: reviewed configs and shared registry.
- Produces: complete artifacts for all eight category memberships.

- [x] Skip re-crawling Food because its reviewed output already exists and all 122 accepted pages are `Done`.
- [x] Crawl the seven new category outputs sequentially.
- [x] Verify only nine canonical details are new and every other accepted page is reused.
- [x] Audit live registry, export snapshot, and regenerate the Shared item URL table.

### Task 4: Verify and commit

**Files:**
- Verify all modified files and ignored category artifacts.

**Interfaces:**
- Consumes: completed batch outputs and snapshot.
- Produces: clean local commit on `codex/category-batch-3`.

- [x] Verify expected page counts, empty errors, no pending queues, unique canonical URLs, and registry `Done` membership.
- [x] Run Python tests, Vitest, TypeScript, ESLint, production build, and `git diff --check`.
- [x] Copy ignored generated outputs into the main checkout.
- [x] Commit the reviewed batch.
