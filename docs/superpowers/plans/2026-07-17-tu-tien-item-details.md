# Tu Tiên Item Details Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate evidence-backed recipe, gameplay usage, and acquisition data for every exported Tu Tiên item, render all three modal sections, and report every unresolved section.

**Architecture:** A focused Python detail builder derives reverse recipes, supported stat/relation/effect prose, acquisition rows, statuses, and a deterministic audit report from the normalized catalog. `export_items.py` attaches this contract to every Tu Tiên item and applies validated manual overrides. The TypeScript parser validates schema version 5, while a dedicated React component renders all three sections without changing base-game wiki behavior.

**Tech Stack:** Python 3 standard library and `unittest`; TypeScript 5; React 19; Vitest and Testing Library; Next.js 16.2.10.

## Global Constraints

- Cover every Tu Tiên inventory item selected by the existing catalog curation; the current export contains 381 items.
- Never infer behavior from names, descriptions, or artwork alone.
- Keep base-game wiki detail behavior unchanged.
- Always render Công thức, Cách sử dụng, and Nguồn nhận for Tu Tiên modals.
- Render `Chưa xác định từ dữ liệu mod.` and include the item in the report for every `unknown` section.
- Preserve all unrelated uncommitted workspace changes.

---

### Task 1: Derive and validate item detail data

**Files:**
- Create: `tools/extract/item_details.py`
- Create: `tests/extract/test_item_details.py`
- Create: `data/manual/tu_tien_item_details.json`

**Interfaces:**
- Consumes: normalized `public/data/catalog.json` entity records and compact item records.
- Produces: `build_tu_tien_item_details(entities, items, overrides) -> tuple[dict[str, dict], dict]`.
- Produces: each detail object with `recipeStatus`, `usage`, and `dropBy`.

- [ ] **Step 1: Write failing tests for reverse recipes and supported stat groups**

```python
def test_builds_reverse_recipe_and_edible_usage(self):
    details, report = build_tu_tien_item_details(
        entities=[ingredient_entity, result_entity],
        items=[ingredient_item, result_item],
        overrides={"schema_version": 1, "items": {}},
    )
    self.assertEqual(details["tu_tien:herb"]["usage"]["status"], "known")
    self.assertEqual(
        details["tu_tien:herb"]["usage"]["recipes"][0]["result"]["id"],
        "tu_tien:pill",
    )
    self.assertIn("Hồi 20 Máu", details["tu_tien:herb"]["usage"]["effects"][0]["text"])
    self.assertEqual(report["totalTuTienItems"], 2)
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `python3 -m unittest tests.extract.test_item_details -v`

Expected: FAIL because `tools.extract.item_details` does not exist.

- [ ] **Step 3: Implement deterministic reference, recipe, stat, relation, and acquisition derivation**

Implement these public entry points:

```python
DETAIL_STATUSES = {"known", "none", "unknown"}
DROP_TYPES = {"drop", "harvest", "start", "trade", "other"}

def build_tu_tien_item_details(
    entities: list[dict[str, Any]],
    items: list[dict[str, Any]],
    overrides: dict[str, Any] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Return deterministic detail records and the unresolved-data report."""
```

Rules implemented in this task:

- Reverse-index every recipe ingredient.
- Convert `health`, `hunger`, and `sanity` into one `eat` effect.
- Convert weapon `damage`, `attack_range`, and `uses` into one `equip` effect.
- Convert `armor_durability` and `damage_absorption` into one `equip` effect.
- Convert `container_slots` into one `open` effect.
- Convert `charge_capacity`, `current_charge`, and `recharge_time` into one `activate` effect.
- Convert `transforms_to` relations into one `lifecycle` effect.
- Exclude `craft` from `dropBy`; convert the remaining acquisition rows.
- Use `known` only with records, `none` for positively established craft-only acquisition, otherwise `unknown`.
- Sort every list by stable semantic keys.

- [ ] **Step 4: Write failing override-validation and report tests**

```python
def test_rejects_known_empty_override(self):
    with self.assertRaisesRegex(ValueError, "known usage"):
        build_tu_tien_item_details(
            [ingredient_entity],
            [ingredient_item],
            {"schema_version": 1, "items": {
                "tu_tien:herb": {"usage": {"replace": True, "status": "known", "recipes": [], "effects": []}}
            }},
        )

def test_reports_unknown_sections_in_stable_order(self):
    _details, report = build_tu_tien_item_details(
        entities=[ingredient_entity, result_entity],
        items=[ingredient_item, result_item],
        overrides={"schema_version": 1, "items": {}},
    )
    self.assertEqual(report["unknownItems"], sorted(report["unknownItems"], key=lambda row: row["id"]))
```

- [ ] **Step 5: Implement explicit per-section override merging and validation**

Manual JSON starts as:

```json
{
  "schema_version": 1,
  "items": {}
}
```

An override section must contain `replace`, `status`, and its section records. Evidence entries must use paths beginning with `mod/3721846643/`.

- [ ] **Step 6: Run tests and commit Task 1**

Run: `python3 -m unittest tests.extract.test_item_details -v`

Expected: PASS.

Commit: `git commit -m "feat: derive Tu Tien item details"`

---

### Task 2: Publish details and deterministic audit report

**Files:**
- Modify: `tools/extract/export_items.py`
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_export_items.py`
- Create: `data/generated/tu-tien-item-details-report.json` (generated)
- Modify: `public/data/items.json` (generated)

**Interfaces:**
- Consumes: `build_tu_tien_item_details` from Task 1.
- Produces: item payload schema version 5 and report schema version 1.
- Extends: `export_items(database_path, catalog_path, assets_path, items_path, textures_path, detail_overrides_path=Path("data/manual/tu_tien_item_details.json"), detail_report_path=Path("data/generated/tu-tien-item-details-report.json"))`.

- [ ] **Step 1: Add failing export tests**

```python
items, textures, report = build_item_export(catalog, assets)
self.assertEqual(items["schema_version"], 5)
self.assertIsNone(by_id["base_game:goldnugget"]["details"])
self.assertEqual(by_id["tu_tien:xd_sword"]["details"]["recipeStatus"], "known")
self.assertEqual(report["totalTuTienItems"], 2)
```

The deterministic export test also asserts byte-identical report output after two exports.

- [ ] **Step 2: Run the tests and verify schema/report assertions fail**

Run: `python3 -m unittest tests.extract.test_export_items -v`

Expected: FAIL because the current payload is schema version 4 and has no details report.

- [ ] **Step 3: Integrate the builder into the export pipeline**

After compact items are assembled, call:

```python
details, detail_report = build_tu_tien_item_details(
    source_entities,
    items,
    detail_overrides,
)
for item in items:
    item["details"] = details.get(item["id"])
```

Read `data/manual/tu_tien_item_details.json` before building, atomically write the report, and bump the item payload to schema version 5.

- [ ] **Step 4: Add CLI defaults**

Add:

```python
ITEM_DETAILS_OVERRIDES = Path("data/manual/tu_tien_item_details.json")
ITEM_DETAILS_REPORT = Path("data/generated/tu-tien-item-details-report.json")
```

Pass both paths through the normal `export` stage.

- [ ] **Step 5: Run focused and full Python tests**

Run: `python3 -m unittest tests.extract.test_item_details tests.extract.test_export_items -v`

Expected: PASS.

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS.

Commit: `git commit -m "feat: export Tu Tien item detail report"`

---

### Task 3: Validate the schema in the frontend

**Files:**
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/item-catalog.test.ts`

**Interfaces:**
- Consumes: item payload schema version 5 from Task 2.
- Produces: `ItemDetails`, `ItemUsageRecipe`, `ItemUsageEffect`, and `ItemDropSource` types.
- Invariant: Tu Tiên items require non-null `details`; base-game items require `details: null`.

- [ ] **Step 1: Add details to the valid fixture and failing parser cases**

```ts
details: {
  recipeStatus: "known",
  usage: { status: "unknown", recipes: [], effects: [] },
  dropBy: { status: "none", sources: [] },
},
```

Add tests that reject a Tu Tiên item with `details: null`, a `known` empty section, an invalid drop type, and a legacy schema version.

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `npm test -- app/lib/item-catalog.test.ts`

Expected: FAIL because the parser only accepts schema version 4 and ignores details.

- [ ] **Step 3: Implement strict details parsers**

Add explicit parsers for status, evidence, references, usage recipes/effects, drop sources, and the details object. Require positive amounts and match status invariants:

```ts
if (status === "known" && recordCount === 0) {
  throw new Error(`${field} known section must contain data`);
}
```

Bump `parseItemPayload` to schema version 5 and enforce namespace-specific nullability.

- [ ] **Step 4: Run parser tests and type-check through the suite**

Run: `npm test -- app/lib/item-catalog.test.ts`

Expected: PASS.

Commit: `git commit -m "feat: validate Tu Tien item details"`

---

### Task 4: Render all three Tu Tiên modal sections

**Files:**
- Create: `app/components/tu-tien-item-sections.tsx`
- Create: `app/components/tu-tien-item-sections.test.tsx`
- Modify: `app/components/item-detail-modal.tsx`
- Modify: `app/components/item-detail-modal.test.tsx`

**Interfaces:**
- Consumes: `ItemListEntry.details` and the modal `itemsById`/`onSelectItem` callbacks.
- Produces: `TuTienItemSections` with headings Công thức, Cách sử dụng, and Nguồn nhận.

- [ ] **Step 1: Read the bundled Next.js guide before editing**

Run: `rg -n "Client Components|use client|components" node_modules/next/dist/docs/01-app node_modules/next/dist/docs -g '*.md' | head -80`

Expected: relevant Next.js 16 component guidance is identified and read.

- [ ] **Step 2: Add failing component tests for known, none, and unknown states**

```tsx
render(<TuTienItemSections item={tuTienItem} itemsById={items} onSelectItem={onSelectItem} />);
expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
expect(screen.getByRole("heading", { name: "Cách sử dụng" })).toBeDefined();
expect(screen.getByRole("heading", { name: "Nguồn nhận" })).toBeDefined();
expect(screen.getByText("Chưa xác định từ dữ liệu mod.")).toBeDefined();
```

Also test clickable recipe results and drop sources, gameplay-effect prose, and `Không có công thức chế tạo.`.

- [ ] **Step 3: Run focused tests and verify failure**

Run: `npm test -- app/components/tu-tien-item-sections.test.tsx app/components/item-detail-modal.test.tsx`

Expected: FAIL because `TuTienItemSections` does not exist.

- [ ] **Step 4: Implement the dedicated renderer**

Use the existing `RecipeIngredients` and `GameSprite` primitives. Render a shared section shell and state message. Result/source references call `onSelectItem` only when `itemsById` contains the referenced ID; otherwise render plain text.

- [ ] **Step 5: Integrate without duplicating wiki sections**

In `ItemDetailModal`, render `TuTienItemSections` only when `item.namespace === "tu_tien"`. Keep the existing `CraftingSections` path for base-game items and wiki content.

- [ ] **Step 6: Run frontend tests**

Run: `npm test -- app/components/tu-tien-item-sections.test.tsx app/components/item-detail-modal.test.tsx`

Expected: PASS.

Run: `npm test`

Expected: PASS.

Commit: `git commit -m "feat: show complete Tu Tien item sections"`

---

### Task 5: Regenerate, audit, and verify all current items

**Files:**
- Modify: `public/data/items.json` (generated)
- Create: `data/generated/tu-tien-item-details-report.json` (generated)
- Modify: `data/manual/tu_tien_item_details.json` only for evidence-backed exceptional Lua behavior discovered during audit.

**Interfaces:**
- Consumes: the current normalized catalog and manual overrides.
- Produces: final 381-item detail coverage and unresolved report.

- [ ] **Step 1: Regenerate the item payload and report**

Run: `python3 -m tools.extract.cli export`

Expected: `public/data/items.json` and `data/generated/tu-tien-item-details-report.json` are written atomically.

- [ ] **Step 2: Audit coverage against the actual curated frontend set**

Run:

```bash
jq '[.items[] | select(.namespace == "tu_tien")] | {total:length, missingDetails:map(select(.details == null))|length}' public/data/items.json
```

Expected: `total` is at least 381 before client curation and `missingDetails` is 0. The report's total must equal the exported Tu Tiên item count.

- [ ] **Step 3: Inspect unsupported and unknown records against mod Lua**

For each unsupported shape or high-confidence dynamic item found in the report, search the exact prefab ID in `mod/3721846643/scripts`. Add only evidence-backed manual overrides, including the source path. Regenerate after each coherent batch.

- [ ] **Step 4: Run final verification**

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS.

Run: `npm test`

Expected: PASS.

Run: `npm run lint`

Expected: PASS.

Run: `npm run build`

Expected: PASS.

Run: `git diff --check`

Expected: no whitespace errors.

- [ ] **Step 5: Review final unresolved report**

Confirm every `unknown` section in the report corresponds to the modal message `Chưa xác định từ dữ liệu mod.`. Summarize counts and provide the report path to the user.

Commit: `git commit -m "data: publish Tu Tien item detail coverage"`
