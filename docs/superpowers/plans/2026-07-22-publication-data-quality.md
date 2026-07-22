# Publication Data Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair published catalog records first, remove only unrecoverable records, and prove that every remaining item and Guide has a unique identity, valid image, content, and type-appropriate information.

**Architecture:** A pure audit module evaluates candidate records and emits deterministic issues. A repair layer merges duplicates and fills recoverable fields from existing catalog, Wiki, recipe, crawl, and image evidence. The exporter writes replacement payloads atomically only after the repaired candidate passes all publication invariants, alongside a machine-readable report for every keep, repair, merge, or removal decision.

**Tech Stack:** Python 3 standard library, existing extraction pipeline and SQLite evidence, JSON reports, local image files, unittest, existing Next.js parsers and build checks.

## Global Constraints

- Repair always runs before removal.
- Removal is permitted only after all deterministic local repair sources and the canonical DST crawl have been attempted.
- Every removal records identity, URL, failed rules, repair attempts, and final reason.
- Every published entity with a prefab code has a unique normalized `prefabId`; Guides have unique IDs and slugs.
- Every published record has a valid locally served image, non-empty human-readable content, source metadata, and type-appropriate detail.
- Shipwrecked-only, Hamlet-only, Reign of Giants-only, single-player-only, obsolete event, and technical wrapper records are not publishable.
- Replacement outputs are atomic; a failed candidate never replaces the last valid artifact.

---

### Task 1: Publication audit contract

**Files:**
- Create: `tools/extract/publication_quality.py`
- Create: `tests/extract/test_publication_quality.py`

**Interfaces:**
- Produces: `audit_publication(items_path: Path, guides_path: Path, public_root: Path) -> PublicationAudit`
- Produces issue codes: `duplicate_identity`, `duplicate_code`, `duplicate_slug`, `missing_content`, `missing_detail`, `missing_image`, `invalid_image`, `missing_source`, `invalid_scope`

- [ ] **Step 1: Write failing audit tests**

Build temporary item and Guide fixtures covering each issue code, corrupt images, zero-byte images, missing files, duplicate normalized prefab IDs, duplicate canonical URLs, and valid records for each published item category.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.extract.test_publication_quality.PublicationQualityTest -v`

Expected: import failure for `tools.extract.publication_quality`.

- [ ] **Step 3: Implement pure deterministic auditing**

Validate PNG, JPEG, GIF, and WebP signatures plus positive file size. Treat content as present when a record has a non-empty description or validated Wiki summary/article. Require `mob` for mob/boss, `structureDetails` for structures, `recipe` or `details` for craftable items, `character` for characters, and a validated detail payload for Guides.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest tests.extract.test_publication_quality.PublicationQualityTest -v`

Expected: all issue-code and valid-fixture tests pass.

- [ ] **Step 5: Commit**

Run: `git add tools/extract/publication_quality.py tests/extract/test_publication_quality.py && git commit -m "test: define publication quality contract"`

### Task 2: Repair and removal decisions

**Files:**
- Modify: `tools/extract/publication_quality.py`
- Modify: `tests/extract/test_publication_quality.py`

**Interfaces:**
- Produces: `repair_publication(candidates, evidence, public_root) -> RepairResult`
- `RepairResult` contains `items`, `guides`, `rows`, and `summary`
- Row actions are `keep`, `repair`, `merge`, or `remove`

- [ ] **Step 1: Write failing repair tests**

Cover duplicate merge by canonical prefab ID, newest valid Wiki revision selection, description recovery, Wiki mapping recovery, image recovery from an existing canonical page asset, derived-field rebuilding, deterministic survivor selection, and an unrecoverable record that becomes `remove` only after recorded attempts.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.extract.test_publication_quality.PublicationRepairTest -v`

Expected: failures because repair APIs are absent.

- [ ] **Step 3: Implement evidence precedence**

Use this exact order: current valid field, canonical duplicate field, current `public/data/wiki/pages` detail, matching reviewed category crawl, base catalog or recipe evidence. Images may only be copied from an asset tied to the same canonical item or Wiki page. Never use a generic placeholder.

- [ ] **Step 4: Implement final removal decisions**

Re-audit repaired candidates. Any record still failing a hard publication rule becomes `remove`; its row contains the initial issues, ordered attempts, final issues, source URL, and identity. Valid repaired records keep provenance for every changed field.

- [ ] **Step 5: Verify GREEN and determinism**

Run: `python3 -m unittest tests.extract.test_publication_quality -v`

Expected: all tests pass and serializing the same result twice produces identical JSON.

- [ ] **Step 6: Commit**

Run: `git add tools/extract/publication_quality.py tests/extract/test_publication_quality.py && git commit -m "feat: repair incomplete publication records"`

### Task 3: Atomic CLI workflow

**Files:**
- Modify: `tools/extract/cli.py`
- Modify: `tools/extract/validate.py`
- Modify: `tests/extract/test_export_validate.py`
- Modify: `tests/extract/test_cli.py`
- Generate: `data/generated/publication-quality-report.json`

**Interfaces:**
- Produces CLI command `publication-quality`
- Consumes `--items`, `--guides`, `--public-root`, `--wiki-pages`, `--category-root`, `--report`, and optional `--apply`

- [ ] **Step 1: Write failing CLI and validator tests**

Assert audit-only mode never writes catalog files, `--apply` writes only when post-repair hard failures are zero, report paths are explicit, invalid inputs exit non-zero, and the existing validation command includes publication quality failures in `hard_failures`.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.extract.test_cli tests.extract.test_export_validate -v`

Expected: failures for the missing command and validation integration.

- [ ] **Step 3: Add audit-only and apply modes**

Audit-only writes the report and exits non-zero when repairs or removals are required. Apply mode writes repaired `items.json`, Guide index/details, and the report to sibling temporary paths, validates those temporary outputs, then replaces targets with `Path.replace()` only when every hard invariant passes.

- [ ] **Step 4: Extend export validation**

Require a schema-version-1 publication report whose published counts match actual files, whose `remove` identities are absent, and whose post-repair issue list is empty.

- [ ] **Step 5: Verify GREEN**

Run: `python3 -m unittest tests.extract.test_cli tests.extract.test_export_validate -v`

Expected: all CLI and validation tests pass.

- [ ] **Step 6: Commit**

Run: `git add tools/extract/cli.py tools/extract/validate.py tests/extract/test_export_validate.py tests/extract/test_cli.py && git commit -m "feat: add atomic publication quality workflow"`

### Task 4: Audit and repair the real catalog

**Files:**
- Modify: `public/data/items.json`
- Modify: `public/data/guides/index.json`
- Modify: `public/data/guides/pages/`
- Modify: `public/assets/`
- Create: `data/generated/publication-quality-report.json`

**Interfaces:**
- Consumes: current public catalog, Wiki pages, reviewed category crawls, local assets
- Produces: fully validated public catalog and complete decision report

- [ ] **Step 1: Run audit-only mode**

Run: `python3 -m tools.extract.cli publication-quality --items public/data/items.json --guides public/data/guides --public-root public --wiki-pages public/data/wiki/pages --category-root data/crawled/fandom-categories --report data/generated/publication-quality-report.json`

Expected: report lists exact keep, repair, merge, and remove candidates; command exits non-zero while action is required.

- [ ] **Step 2: Inspect all removal candidates**

For every proposed removal, confirm the report contains the canonical source, every failed rule, and attempted evidence sources. Re-crawl canonical DST URLs for missing detail or images before permitting removal.

- [ ] **Step 3: Apply repairs and removals atomically**

Run the same command with `--apply`.

Expected: zero post-repair hard failures, every removed identity absent, and every retained record covered by exactly one report row.

- [ ] **Step 4: Verify publication invariants independently**

Scan actual files to prove unique IDs, unique prefab IDs, unique Guide slugs, positive-size valid image files, non-empty content, parseable details, and DST scope. Do not rely only on report summary counts.

- [ ] **Step 5: Commit generated decisions and public output**

Run: `git add public/data/items.json public/data/guides public/assets data/generated/publication-quality-report.json && git commit -m "data: repair and clean published catalog"`

### Task 5: Final regression and documentation

**Files:**
- Modify: `docs/data-extraction.md`
- Create: `docs/superpowers/specs/2026-07-22-publication-quality-review.md`

**Interfaces:**
- Produces: operational instructions and final proof of publication invariants

- [ ] **Step 1: Document the workflow**

Document audit-only usage, repair evidence order, apply semantics, report fields, hard failure rules, and how to restore the previous valid artifact from Git.

- [ ] **Step 2: Run all verification**

Run: `python3 -m unittest discover -s tests -p 'test_*.py'`

Run: `npm test`

Run: `npx tsc --noEmit`

Run: `npm run lint`

Run: `npm run build`

Expected: every command exits zero.

- [ ] **Step 3: Re-run audit-only mode on final output**

Expected: exit zero, zero repair candidates, zero merge candidates, zero removal candidates, zero hard failures, and all published images valid.

- [ ] **Step 4: Write the final review**

Record before/after totals by category, repaired fields, merged duplicates, removed identities and reasons, image coverage, content coverage, detail coverage, and exact verification commands.

- [ ] **Step 5: Commit**

Run: `git add docs/data-extraction.md docs/superpowers/specs/2026-07-22-publication-quality-review.md && git commit -m "docs: record publication quality verification"`
