# Category Crawler Batch 5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review and crawl Gameplay, Hats, Healing, Health Loss, Hostile Creatures, Indestructible Object, and Infobox missing crafting description with DST-only scope while rejecting the non-category Gems source.

**Architecture:** Discover direct namespace-0 members only, record but never recurse into child categories, and reject other-game-only pages before they enter the durable registry. Accepted canonical URLs reuse `Done` artifacts; only 70 missing DST pages may perform detail requests. `Gems` is documented as skipped because `Category:Gems` redirects to the `Gems` disambiguation article instead of exposing category members.

**Tech Stack:** Python 3, MediaWiki API, JSON category configs, durable shared crawler registry, unittest.

## Global Constraints

- Game scope is DST only.
- Namespace 0 only; child categories and non-main namespaces are audit-only.
- Canonical URL is the dedupe key; `Doing`/`Done` skip detail network fetch.
- Preserve raw HTML, raw wikitext, page notes, links, and image artifacts.
- Seven valid categories produce 459 accepted memberships / 443 canonical URLs: 373 already `Done`, 70 missing, and 16 duplicate memberships.
- `Gems` is not converted into a synthetic Category config.

---

### Task 1: Lock the seven reviewed configs with TDD

**Files:**
- Modify: `tests/crawl_wiki/test_category_config.py`
- Create: `data/config/wiki-categories/gameplay.json`
- Create: `data/config/wiki-categories/hats.json`
- Create: `data/config/wiki-categories/healing.json`
- Create: `data/config/wiki-categories/health_loss.json`
- Create: `data/config/wiki-categories/hostile_creatures.json`
- Create: `data/config/wiki-categories/indestructible_object.json`
- Create: `data/config/wiki-categories/infobox_missing_crafting_description.json`

**Interfaces:**
- Consumes: `load_category_config(key)` and the reviewed classification snapshot.
- Produces: exact direct/published counts `112/80`, `63/40`, `192/139`, `51/37`, `112/72`, `87/39`, and `52/52`.

- [x] Add `test_loads_reviewed_batch_five_configs` with the seven count/type/tag tuples and representative exclusions/accepted titles.
- [x] Run `python3 -m unittest tests.crawl_wiki.test_category_config -q` and verify RED because all seven configs are missing.
- [x] Create the seven minimal JSON configs with every reviewed exclusion and only supported exclusion reasons.
- [x] Run `python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds -q` and verify GREEN.

### Task 2: Persist review decisions and queue state

**Files:**
- Modify: `docs/category-crawler-control.md`
- Create: `docs/superpowers/specs/2026-07-21-category-crawler-batch-5-review.md`

**Interfaces:**
- Consumes: direct discovery, wikitext evidence, registry snapshot with 1,153 `Done` URLs.
- Produces: durable source decisions, exclusion rationale, new-page lists, and queue counts.

- [x] Record direct/child/non-main/excluded/published counts for all seven Category sources.
- [x] Record `Gems` as skipped because both its article URL and `Category:Gems` resolve to a disambiguation page.
- [x] Record the 70 new canonical URLs and the 16 cross-category duplicate memberships.

### Task 3: Crawl all valid categories sequentially

**Files:**
- Generate: `data/crawled/fandom-categories/<category>/`
- Modify: `data/crawled/fandom-url-registry.json`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: seven reviewed configs and the live shared registry.
- Produces: complete artifacts for 459 accepted memberships and a 1,223-URL `Done` registry.

- [x] Crawl `gameplay`, `hats`, `healing`, `health_loss`, `hostile_creatures`, `indestructible_object`, and `infobox_missing_crafting_description` in that order.
- [x] Verify exactly 70 canonical details are new and all other accepted pages use `Done` artifacts.
- [x] Audit the registry, export its snapshot, and regenerate the Shared item URL table.

### Task 4: Verify and commit

**Files:**
- Verify all modified tracked files and ignored category artifacts.

**Interfaces:**
- Consumes: completed category outputs and registry snapshot.
- Produces: a clean local commit on `codex/category-batch-5`.

- [x] Verify expected page counts, raw HTML/wikitext, empty errors, no pending queues, canonical uniqueness, and registry memberships.
- [x] Copy the seven ignored generated outputs into the main checkout and compare them byte-for-byte.
- [x] Run Python tests, Vitest, TypeScript, ESLint, production build, and `git diff --check`.
- [x] Commit the reviewed batch.
