# Category Crawler Batch 7 Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Review and crawl 18 useful DST-only direct-member categories from the 19 supplied sources while skipping the non-official Mods source and fetching each canonical code at most once.

**Architecture:** MediaWiki continuation discovery supplies all direct namespace-0 members while child/other namespaces remain audit-only. Reviewed JSON configs lock each category's direct/published counts and exclusions; the shared registry canonicalizes URLs, reuses Doing/Done, and permits network detail fetches only for 29 absent URLs.

**Tech Stack:** Python 3, MediaWiki API, JSON category configs, durable URL registry, unittest, Markdown audit documents.

## Global Constraints

- Game scope is DST only.
- Direct namespace 0 only; 35 child categories and six other-namespace rows are never traversed.
- Canonical URL/code is the unique identity across all categories.
- Doing and Done URLs are skipped/reused, never detail-fetched again.
- Preserve raw HTML, raw wikitext, notes, links, and original image artifacts.
- Category:Mods is audit-only and skipped because it publishes zero official DST entities.
- Batch scope is 759 accepted memberships, 491 unique URLs, 462 reused URLs, 29 new URLs, and 199 duplicated canonical URLs.

---

### Task 1: Lock reviewed configs with TDD

**Files:**
- Modify: tests/crawl_wiki/test_category_config.py
- Create: 18 JSON files under data/config/wiki-categories/

**Interfaces:**
- Consumes: load_category_config(key) and the reviewed MediaWiki direct-member snapshot.
- Produces: validated configs for every source except mods.

- [x] Add test_loads_reviewed_batch_seven_configs with this expected mapping:

    expected = {
        "light_sources": (94, 66, "content", "Light Sources"),
        "magic_tab": (30, 20, "item", "Magic Tab"),
        "magic_tier_1": (19, 14, "item", "Magic Tier 1"),
        "magic_tier_2": (14, 9, "item", "Magic Tier 2"),
        "meats": (48, 33, "food", "Meats"),
        "melee_weapons": (38, 23, "weapon", "Melee Weapons"),
        "mineable_objects": (32, 23, "object", "Mineable Objects"),
        "mob_dropped_items": (205, 142, "item", "Mob Dropped Items"),
        "mob_housing": (52, 23, "structure", "Mob Housing"),
        "mob_spawning_entities": (124, 77, "object", "Mob Spawning Entities"),
        "mobs": (279, 174, "mob", "Mobs"),
        "monster_foods": (9, 6, "food", "Monster Foods"),
        "monsters": (64, 40, "mob", "Monsters"),
        "neutral_creatures": (36, 22, "mob", "Neutral Creatures"),
        "nightmare_state_indicator": (9, 9, "object", "Nightmare State Indicator"),
        "nocturnals": (23, 17, "mob", "Nocturnals"),
        "ocean": (64, 31, "content", "Ocean"),
        "passive_creatures": (63, 30, "mob", "Passive Creatures"),
    }

- [x] Run python3 -m unittest tests.crawl_wiki.test_category_config -q and verify RED because the 18 configs are absent.
- [x] Create minimal configs from the reviewed exclusion map, keeping Spider Eggs and rejecting Parrot Pirate.
- [x] Run python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds -q and verify GREEN.

### Task 2: Persist review and queue decisions

**Files:**
- Create: docs/superpowers/specs/2026-07-22-category-crawler-batch-7-review.md
- Modify: docs/category-crawler-control.md

**Interfaces:**
- Consumes: 19 MediaWiki discovery pages, category/wikitext evidence, and the 1,268-entry starting registry.
- Produces: durable counts, exclusion rationale, namespace audit, 29-page new list, and duplicate metrics.

- [x] Record the 19 source decisions including the zero-publish Mods skip.
- [x] Record 759 memberships, 491 unique URLs, 462 reused, 29 new, 199 duplicated URLs, and 268 repeated memberships.
- [x] Record the Spider Eggs metadata exception and contaminated-but-rejected Parrot Pirate registry URL.

### Task 3: Crawl the 18 useful categories sequentially

**Files:**
- Generate: 18 directories under data/crawled/fandom-categories/
- Modify: data/crawled/fandom-url-registry.json
- Modify: docs/category-crawler-control.md

**Interfaces:**
- Consumes: reviewed configs and the shared canonical URL registry.
- Produces: complete category artifacts and a 1,297-URL all-Done registry.

- [x] Run the category CLI once per configured key, in the exact review-table order, with page-budget 1000.
- [x] Verify only the 29 absent canonical URLs perform detail fetches; every repeated/known URL uses the shared artifact.
- [x] Audit the live registry, export its snapshot, and regenerate the Shared item URL table.

### Task 4: Verify and commit

**Files:**
- Verify all tracked changes and ignored generated output directories.

**Interfaces:**
- Consumes: complete artifacts, manifest checksums, config seeds, and registry snapshot.
- Produces: a verified local commit on codex/category-batch-7.

- [x] Verify exact seeds/pages/images, raw HTML/wikitext, empty errors, no pending queues, normalized canonical uniqueness, and category membership evidence.
- [x] Copy all 18 ignored output directories into the main checkout without overwriting existing targets, then compare byte-for-byte.
- [x] Run Python tests, Vitest, TypeScript, ESLint, production build, and git diff --check.
- [x] Commit the reviewed batch.
