# Full DST Prefab Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export and search one base-game entry for every verified `scripts/prefabs/*.lua` module, assign a stable category, retain all Tu Tiên entities, and keep 40-result incremental rendering.

**Architecture:** Extend the existing static `ScriptIndex` with deterministic module discovery and classification, then let the CLI enrichment stage include every discovered module in addition to dependency-only evidence. Carry the normalized entity type into compact schema version 2 as `category`, filter only non-module base helper entities during export, and add an independent category filter to the React search UI.

**Tech Stack:** Python 3 standard library and `unittest`; SQLite normalization/export pipeline; Next.js 16 App Router; React 19; TypeScript; Vitest and Testing Library; Tailwind CSS.

## Global Constraints

- Base-game coverage is exactly one entry per `.lua` file directly under `scripts/prefabs/`.
- The prefab ID is the lowercase file stem.
- Do not execute DST or expand multiple `Prefab(...)` values from one file.
- Missing names, descriptions, recipes, and icons must not exclude an entry.
- Every exported entry uses one of `item`, `mob`, `boss`, `character`, `structure`, `effect`, or `other`.
- Existing Tu Tiên entities remain searchable.
- Initial rendering and each `Xem thêm` increment remain exactly 40 results.
- Preserve unrelated working-tree changes and stage only task files.

---

### Task 1: Discover and Classify Every Base Prefab Module

**Files:**
- Modify: `tools/extract/base_game.py`
- Test: `tests/extract/test_base_game.py`

**Interfaces:**
- Produces: `discover_prefab_modules(members: Iterable[str]) -> Dict[str, str]`
- Produces: `classify_prefab_module(prefab_id: str, source: str) -> str`
- Updates: `ScriptIndex.prefab_members` to use validated discovery.

- [ ] **Step 1: Write failing discovery and classification tests**

Add tests that build a ZIP with direct prefab modules, nested/non-Lua files, a BOM, duplicate case-folded stems, and representative source for all seven categories. Assert sorted direct-module discovery, duplicate rejection, first-match priority, and comments not changing classification.

```python
def test_discovers_every_direct_prefab_module_and_rejects_duplicate_ids(self):
    members = [
        "scripts/prefabs/zeta.lua",
        "scripts/prefabs/alpha.lua",
        "scripts/prefabs/nested/ignored.lua",
        "scripts/prefabs/readme.txt",
    ]
    self.assertEqual(
        discover_prefab_modules(members),
        {"alpha": "scripts/prefabs/alpha.lua", "zeta": "scripts/prefabs/zeta.lua"},
    )
    with self.assertRaisesRegex(ValueError, "duplicate prefab module id alpha"):
        discover_prefab_modules([
            "scripts/prefabs/Alpha.lua",
            "scripts/prefabs/alpha.lua",
        ])

def test_classifies_prefab_modules_with_stable_priority(self):
    cases = {
        "spark_fx": ("return Prefab('spark_fx', fn)", "effect"),
        "wilson": ("return MakePlayerCharacter('wilson', prefabs, assets, fn)", "character"),
        "deerclops": ('inst:AddTag("epic")', "boss"),
        "spider": ('inst:AddTag("monster")', "mob"),
        "axe": ('inst:AddComponent("inventoryitem")', "item"),
        "wall": ('inst:AddTag("structure")', "structure"),
        "mystery": ("return Prefab('mystery', fn)", "other"),
    }
    for prefab_id, (source, expected) in cases.items():
        with self.subTest(prefab_id=prefab_id):
            self.assertEqual(classify_prefab_module(prefab_id, source), expected)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python3 -m unittest tests.extract.test_base_game.BaseGameTests.test_discovers_every_direct_prefab_module_and_rejects_duplicate_ids tests.extract.test_base_game.BaseGameTests.test_classifies_prefab_modules_with_stable_priority -v`

Expected: import/name failures because the two functions do not exist.

- [ ] **Step 3: Implement deterministic discovery and classification**

Implement direct-path matching, lowercase stem derivation, sorted output, duplicate rejection, literal call/tag/component inspection, effect markers, and the approved first-match priority. Use the existing Lua scanner helpers so comments do not become signals.

```python
PREFAB_CATEGORIES = (
    "item", "mob", "boss", "character", "structure", "effect", "other"
)

def discover_prefab_modules(members: Iterable[str]) -> Dict[str, str]:
    discovered: Dict[str, str] = {}
    for member in sorted(members):
        path = PurePosixPath(member)
        if path.parent.as_posix() != "scripts/prefabs" or path.suffix != ".lua":
            continue
        prefab_id = path.stem.lower()
        if prefab_id in discovered:
            raise ValueError(f"duplicate prefab module id {prefab_id}")
        discovered[prefab_id] = member
    return discovered
```

- [ ] **Step 4: Run focused and full base-game tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_base_game -v`

Expected: all base-game tests pass.

- [ ] **Step 5: Commit the discovery unit**

```bash
git add tools/extract/base_game.py tests/extract/test_base_game.py
git commit -m "feat: discover and classify DST prefab modules"
```

### Task 2: Enrich the Complete Module Set Without Removing Dependency Evidence

**Files:**
- Modify: `tools/extract/base_game.py`
- Modify: `tools/extract/cli.py`
- Test: `tests/extract/test_base_game.py`
- Test: `tests/extract/test_export_validate.py`

**Interfaces:**
- Produces: `enrich_prefab_modules(archive: Path, requests: Iterable[DependencyRequest], base_translation_po: Path) -> FactBundle`
- Preserves: `enrich_dependencies(...)` dependency-only behavior for focused callers.
- Updates: `_enrich_base_stage()` to call `enrich_prefab_modules`.

- [ ] **Step 1: Write a failing full-enrichment test**

Create an archive containing several modules where only one is requested. Assert `enrich_prefab_modules` emits one category-bearing entity fact per module, preserves request evidence for the requested module, and emits no extra module entry for a nested file.

```python
bundle = enrich_prefab_modules(
    archive,
    [DependencyRequest("axe", "ingredient", "tu_tien:xd_tool")],
    root / "missing.po",
)
entities = {
    fact.subject.prefab_id: fact.payload
    for fact in bundle.facts
    if fact.kind == "entity"
}
self.assertEqual(set(entities), {"axe", "spider", "spark_fx"})
self.assertEqual(entities["axe"]["entity_type"], "item")
self.assertEqual(entities["spider"]["entity_type"], "mob")
self.assertEqual(entities["spark_fx"]["entity_type"], "effect")
self.assertEqual(entities["axe"]["requested_by"][0]["subject"], "tu_tien:xd_tool")
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python3 -m unittest tests.extract.test_base_game.BaseGameTests.test_enriches_every_prefab_module_without_dependency_gate -v`

Expected: failure because `enrich_prefab_modules` does not exist.

- [ ] **Step 3: Refactor enrichment around an explicit selected set**

Share the existing enrichment body through a private helper. Dependency-only mode builds the current selected set. Full-module mode starts with every `ScriptIndex.prefab_members` ID, assigns `classify_prefab_module` output as `entity_type`, and merges direct `requested_by` evidence where IDs overlap. Non-module dependency entities may remain in the audit catalog with `unknown` type for referential integrity, but only category-bearing modules are eligible for compact base export.

- [ ] **Step 4: Switch the CLI stage and update its contract test**

Change `_enrich_base_stage` to call `enrich_prefab_modules`. Update the CLI test to assert the full-module entry point is used while all explicit paths remain unchanged.

- [ ] **Step 5: Run extraction tests and verify GREEN**

Run: `python3 -m unittest discover -s tests/extract -v`

Expected: all extraction tests pass.

- [ ] **Step 6: Commit the full enrichment unit**

```bash
git add tools/extract/base_game.py tools/extract/cli.py tests/extract/test_base_game.py tests/extract/test_export_validate.py
git commit -m "feat: enrich the full DST prefab module set"
```

### Task 3: Export Compact Schema Version 2 Without the Inventory Gate

**Files:**
- Modify: `tools/extract/export_items.py`
- Test: `tests/extract/test_export_items.py`
- Modify: `tools/extract/validate.py`
- Test: `tests/extract/test_export_validate.py`

**Interfaces:**
- Produces compact entries with required `category`.
- Produces item payload `{ "schema_version": 2, "items": [...] }`.
- Includes every Tu Tiên entity.
- Includes base-game entities only when their normalized `type` is an approved category.

- [ ] **Step 1: Write failing export tests**

Extend fixtures with `type`, category-bearing non-inventory base modules, a Tu Tiên non-inventory entity, and an unknown dependency-only base entity. Assert the two non-inventory catalog entries are included, the unknown base helper is excluded, categories are mapped, and schema version is 2.

```python
self.assertEqual(items["schema_version"], 2)
self.assertIn("base_game:deerclops", by_id)
self.assertEqual(by_id["base_game:deerclops"]["category"], "boss")
self.assertIn("tu_tien:xd_creature", by_id)
self.assertEqual(by_id["tu_tien:xd_creature"]["category"], "mob")
self.assertNotIn("base_game:dependency_alias", by_id)
```

- [ ] **Step 2: Run exporter tests and verify RED**

Run: `python3 -m unittest tests.extract.test_export_items -v`

Expected: failures showing inventory-only exclusion and missing category/schema 2.

- [ ] **Step 3: Implement strict category mapping and inclusion**

Add `_category(entity)` that accepts the seven normalized values, maps `inventory_item` to `item`, maps known legacy types, returns `other` for unknown Tu Tiên types, and rejects invalid non-string values. Replace the inventory-only list condition with namespace-aware inclusion and emit category in `_build_item_entry`.

- [ ] **Step 4: Add validation for exact module/export coverage**

During validation, derive module stems from the verified scripts archive and compare them with schema-2 base-game compact IDs. Emit a hard failure containing sorted `missing` and `unexpected` IDs when the sets differ.

- [ ] **Step 5: Run exporter and validation tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_export_items tests.extract.test_export_validate -v`

Expected: all focused tests pass.

- [ ] **Step 6: Commit the schema/export unit**

```bash
git add tools/extract/export_items.py tools/extract/validate.py tests/extract/test_export_items.py tests/extract/test_export_validate.py
git commit -m "feat: export all categorized prefabs"
```

### Task 4: Parse, Filter, and Render Prefab Categories in the Frontend

**Files:**
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/lib/wiki-search.ts`
- Modify: `app/lib/wiki-search.test.ts`
- Modify: `app/components/item-result.tsx`
- Modify: `app/components/item-result.test.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/page.tsx`
- Modify: `app/page.test.tsx`

**Interfaces:**
- Produces: `PrefabCategory` and category-bearing `ItemListEntry`.
- Updates: `filterItems(items, query, filter, category)`.
- Preserves: `RESULT_BATCH_SIZE = 40` and the `Xem thêm` interaction.

- [ ] **Step 1: Read the bundled Next.js App Router guide**

Read the relevant page/component guidance under `node_modules/next/dist/docs/` before editing App Router code, as required by the repository rules.

- [ ] **Step 2: Write failing schema and filtering tests**

Update the valid fixture to schema version 2 with category. Add tests rejecting schema 1 and invalid category. Add combined namespace/category/craftability tests against `filterItems`.

```ts
expect(() => parseItemPayload({ ...validPayload, schema_version: 1 })).toThrow(
  /schema version 2/i,
);
expect(filterItems(items, "", "base_game", "boss").map((item) => item.id)).toEqual([
  "base_game:deerclops",
]);
```

- [ ] **Step 3: Run model tests and verify RED**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts`

Expected: failures for schema/category parsing and the missing fourth filter argument.

- [ ] **Step 4: Implement the schema-2 model and pure filter logic**

Add the seven-value union and validator. Require schema version 2. Extend `filterItems` so namespace/craftability and category are independent predicates while text matching remains unchanged.

- [ ] **Step 5: Run model tests and verify GREEN**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts`

Expected: all focused model tests pass.

- [ ] **Step 6: Write failing component tests**

Assert cards expose localized category labels, the category group combines with namespace filtering, empty reset restores both groups, and changing category resets an expanded 80-card list to 40.

- [ ] **Step 7: Run component tests and verify RED**

Run: `npm test -- app/components/item-result.test.tsx app/components/wiki-search.test.tsx app/page.test.tsx`

Expected: failures because category metadata and category controls do not exist.

- [ ] **Step 8: Implement category UI and Prefab copy**

Add localized labels and category-specific Phosphor icons in `ItemResult`. Add a second named filter group in `WikiSearch`, category state, reset behavior, result keys/status text, and 40-item batch reset. Update page headings and accessible copy from Items to Prefabs where the catalog is described.

- [ ] **Step 9: Run frontend tests and verify GREEN**

Run: `npm test`

Expected: all frontend tests pass, including the existing 40/80 batching assertions.

- [ ] **Step 10: Commit the frontend unit**

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/lib/wiki-search.ts app/lib/wiki-search.test.ts app/components/item-result.tsx app/components/item-result.test.tsx app/components/wiki-search.tsx app/components/wiki-search.test.tsx app/page.tsx app/page.test.tsx
git commit -m "feat: search prefabs by category"
```

### Task 5: Regenerate Full Catalog Artifacts and Verify End to End

**Files:**
- Modify: `data/raw/base_game.json`
- Modify: `data/generated/wiki.sqlite`
- Modify: `data/generated/coverage.json`
- Modify: `data/generated/item-textures.json`
- Modify: `public/data/catalog.json`
- Modify: `public/data/assets.json`
- Modify: `public/data/items.json`
- Modify as generated: `public/assets/game/*.png`
- Modify: `docs/data-extraction.md`

**Interfaces:**
- Consumes the verified game archives and updated extraction code.
- Produces schema-2 frontend data with exact base module coverage.

- [ ] **Step 1: Regenerate the base facts and normalized exports**

Run the explicit CLI stages in pipeline order using the existing verified local inputs:

```bash
python3 -m tools.extract.cli enrich-base
python3 -m tools.extract.cli build-db
python3 -m tools.extract.cli export
python3 -m tools.extract.cli publish-assets
python3 -m tools.extract.cli validate
```

Expected: no hard failures; output reports a base-game catalog count equal to direct `scripts/prefabs/*.lua` modules.

- [ ] **Step 2: Verify exact archive-to-export equality**

Compare sorted lowercase stems from `scripts.zip` with sorted base-game `prefabId` values in `public/data/items.json`. Expected: no missing or unexpected values.

- [ ] **Step 3: Update extraction documentation**

Document the file-module source of truth, category heuristics, schema version 2, the absence of the inventory inclusion gate, and the fact that UI batching does not limit export coverage.

- [ ] **Step 4: Run complete verification**

```bash
python3 -m unittest discover -s tests/extract -v
npm test
npm run lint
npm run build
git diff --check
```

Expected: 0 Python failures, 0 Vitest failures, clean lint, successful static production build, and no whitespace errors.

- [ ] **Step 5: Review generated scope and commit**

Confirm generated changes contain only expected extraction artifacts and required published textures, then stage those exact paths and commit:

```bash
git add data/raw/base_game.json data/generated/wiki.sqlite data/generated/coverage.json data/generated/item-textures.json public/data/catalog.json public/data/assets.json public/data/items.json public/assets/game docs/data-extraction.md
git commit -m "data: publish the full DST prefab catalog"
```

## Final Verification Checklist

- [ ] Every production change was preceded by a focused failing test.
- [ ] Direct module stems and exported base IDs are exactly equal.
- [ ] Every compact entry has one valid category.
- [ ] Tu Tiên entries remain present.
- [ ] Search combines text, namespace, craftability, and category.
- [ ] Initial and incremental result batches remain 40.
- [ ] Full Python/frontend suites, lint, build, validation, and diff checks pass.
- [ ] No unrelated working-tree changes are staged.
