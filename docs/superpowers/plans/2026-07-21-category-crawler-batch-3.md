# Category Crawler Batch 3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review, crawl, and register direct DST pages from eight Fandom categories without recursive category traversal or duplicate detail fetches.

**Architecture:** Reuse the generic category crawler and Git-common canonical URL registry. Seven new JSON configs describe exact counts and exclusions; the existing `animals.json` config is reused. Narrow and high-overlap categories run first so `Done` rows are projected without network detail fetches, while broad `A New Reign` runs last.

**Tech Stack:** Python 3 standard library, MediaWiki API client, SQLite-backed crawler state, JSON category configs, Markdown control/spec files, unittest, Vitest/Next.js verification.

## Global Constraints

- Accept only direct namespace-0 pages; never recurse into child categories.
- Publish DST data only; exclude Don't Starve, Reign of Giants, Shipwrecked, and Hamlet exclusives before detail fetch.
- Keep `Parrot Pirate` as an explicit DST exception in Animals and Birds.
- Canonical URL registry states are exactly `New`, `Doing`, and `Done`; skip detail fetch for `Doing` and `Done`.
- Six colored Moonlens aliases resolve to `Moonlens` and must be excluded as `duplicate:canonical_redirect` so one canonical page is registered.
- Preserve raw notes and page evidence in shared artifacts for later summary normalization.

---

### Task 1: Category config contract and reviewed configs

**Files:**
- Modify: `tests/crawl_wiki/test_category_config.py`
- Modify: `tools/crawl_wiki/category_config.py`
- Create: `data/config/wiki-categories/a_new_reign.json`
- Create: `data/config/wiki-categories/ancient_tab.json`
- Create: `data/config/wiki-categories/ancient_tier_1.json`
- Create: `data/config/wiki-categories/ancient_tier_2.json`
- Create: `data/config/wiki-categories/birds.json`
- Create: `data/config/wiki-categories/boss_monsters.json`
- Create: `data/config/wiki-categories/clockwork_monsters.json`

**Interfaces:**
- Consumes: `load_category_config(key: str) -> CategoryConfig` and the approved exclusion reason set.
- Produces: seven loadable configs with direct/published counts `110/92`, `15/14`, `10/9`, `7/7`, `17/10`, `37/28`, and `8/6`.

- [ ] **Step 1: Write the failing config test**

Add a test that loads all seven keys, checks the exact counts/item types/tags, and asserts:

```python
exclusions = dict(load_category_config("a_new_reign").excluded_titles)
self.assertEqual(
    exclusions["Blue Moonlens"],
    "duplicate:canonical_redirect",
)
self.assertEqual(exclusions["Disease"], "non_item:category_mismatch")
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_category_config.CategoryConfigTests.test_loads_reviewed_batch_three_configs -q
```

Expected: fail because `a_new_reign.json` and the other new configs do not exist.

- [ ] **Step 3: Add the minimal config support and JSON files**

Add `"duplicate:canonical_redirect"` to `_EXCLUSION_REASONS`. Create each config with `allowedNamespaces: [0]`, `game: "DST"`, exact reviewed exclusions, one matching tag, and these item types:

```text
a_new_reign=content
ancient_tab=item
ancient_tier_1=item
ancient_tier_2=item
birds=mob
boss_monsters=mob
clockwork_monsters=mob
```

- [ ] **Step 4: Run config tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.crawl_wiki.test_category_config tests.crawl_wiki.test_category_seeds -q
```

Expected: all tests pass.

### Task 2: Batch review documentation and control queue

**Files:**
- Create: `docs/superpowers/specs/2026-07-21-category-crawler-batch-3-review.md`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: reviewed discovery JSON with 292 direct memberships, 201 unique pages before review, and 166 accepted canonical URLs.
- Produces: reproducible Keep/Exclude lists, child-category decisions, overlap counts, and queue rows marked `Reviewed`.

- [ ] **Step 1: Record the review matrix**

Document 195 accepted memberships, 166 canonical URLs, 29 cross-category duplicates, 77 existing `Done`, 23 existing `New`, and 66 missing URLs.

- [ ] **Step 2: Record direct member decisions**

List every accepted title, every excluded title/reason, and all ignored child/non-main namespaces for the eight categories. Reuse the existing Animals review/config rather than changing its six exclusions.

- [ ] **Step 3: Validate documentation**

Run:

```bash
git diff --check
```

Expected: exit 0.

### Task 3: Sequential detail crawl

**Files:**
- Generated/ignored: `data/crawled/fandom-categories/<category>/`
- Shared durable state: `<git-common-dir>/category-crawler/`

**Interfaces:**
- Consumes: the seven new configs plus existing `animals` config and shared registry snapshot.
- Produces: complete page/image projections and shared raw page artifacts.

- [ ] **Step 1: Audit pre-crawl state**

Run:

```bash
python3 -m tools.crawl_wiki.state_cli audit
```

Expected: `urls=729 valid=729 invalid=0 New=23 Doing=0 Done=706`.

- [ ] **Step 2: Crawl in reuse-maximizing order**

Run each category sequentially with `--page-budget 500 --delay 0.1` in this order:

```text
ancient_tab
ancient_tier_1
ancient_tier_2
animals
birds
clockwork_monsters
boss_monsters
a_new_reign
```

Expected per category: `failures=0 pending_pages=0 pending_images=0`.

- [ ] **Step 3: Verify generated category invariants**

For every category, assert page count equals `expectedPublishedPages`, `errors.jsonl` is empty, manifest status is `complete`, and every projected canonical URL is `Done` with the category membership in the registry.

### Task 4: Snapshot and control table finalization

**Files:**
- Modify: `data/crawled/fandom-url-registry.json`
- Modify: `docs/category-crawler-control.md`

**Interfaces:**
- Consumes: live Git-common registry after all eight crawls.
- Produces: exact tracked JSON snapshot and a matching Markdown URL/status/category table.

- [ ] **Step 1: Audit and export**

Run:

```bash
python3 -m tools.crawl_wiki.state_cli audit
python3 -m tools.crawl_wiki.state_cli snapshot --snapshot data/crawled/fandom-url-registry.json
```

Expected: zero invalid and zero `Doing`; all 23 former Animals `New` rows become `Done`.

- [ ] **Step 2: Regenerate control status**

Mark all eight queue rows `Done`, set exact registry counts, update the live audit, and regenerate all shared URL rows from the exported snapshot.

### Task 5: Full verification and commit

**Files:**
- Verify all changed files from Tasks 1-4.

**Interfaces:**
- Consumes: complete batch implementation.
- Produces: one clean commit on `codex/category-batch-3`.

- [ ] **Step 1: Run full verification**

Run:

```bash
python3 -m unittest discover -s tests -q
npm test
npx tsc --noEmit
npm run lint
npm run build
git diff --check
```

Expected: 325+ Python tests pass, 129 Vitest tests pass, and typecheck/lint/build/diff-check exit 0.

- [ ] **Step 2: Commit the batch**

Stage only reviewed configs, tests, docs, plan/spec, and registry snapshot; commit with:

```bash
git commit -m "feat: crawl third DST category batch"
```
