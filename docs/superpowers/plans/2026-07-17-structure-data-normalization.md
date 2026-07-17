# Structure Data Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish complete, evidence-backed structure details for DST and Tu Tiên, audit and resolve every missing structure icon, exclude technical prefabs, and fold all Wiki records into the DST source group.

**Architecture:** A focused Python structure-detail builder combines canonical catalog facts with imported Wiki normalization and emits both `structureDetails` and a deterministic icon audit. The existing export pipeline applies the builder after Wiki merging, validates completeness, and publishes schema version 6. TypeScript parses the same contract, the source filter treats Wiki as provenance instead of a group, and a dedicated React renderer presents structure-specific sections.

**Tech Stack:** Python 3 standard library, SQLite, existing extraction/crawler modules, TypeScript 5, React 19, Next.js 16.2 local conventions, Vitest, Testing Library.

## Global Constraints

- Cover every published `structure` in both `base_game` and `tu_tien`.
- Preserve raw/SQLite evidence when excluding public technical or unverified rows.
- Wiki facts may enrich but never overwrite conflicting higher-confidence game/mod facts.
- Every pre-resolution iconless structure appears exactly once in the generated audit.
- Status fields use only `known`, `none`, or `unknown`; missing parser support is never converted to `none`.
- All valid Wiki records are exposed under DST; no Wiki source group or badge remains.
- Outputs and reports must be deterministic from unchanged inputs.
- Follow the repository's Next.js 16.2 documentation in `node_modules/next/dist/docs/` for any framework-facing code.

---

## File Map

- Create `tools/extract/structure_details.py`: structure contract assembly, reverse station recipes, visual resolution, candidate classification, audit generation.
- Create `tools/extract/wiki_structures.py`: deterministic normalization of structure-specific Wiki wikitext/infobox facts.
- Create `tests/extract/test_structure_details.py`: builder, station mapping, audit, and classification tests.
- Create `tests/extract/test_wiki_structures.py`: Wiki structure parser fixtures.
- Modify `tools/extract/wiki_import.py`: persist normalized structure facts in `wiki_structure_details`.
- Modify `tools/extract/wiki_export.py`: expose normalized structure facts and Wiki visuals to the structure builder; publish standalone Wiki items as DST.
- Modify `tools/extract/export_items.py`: assemble schema version 6, write the structure audit atomically, and exclude audited invalid candidates.
- Modify `tools/extract/validate.py`: enforce structure-detail, audit coverage, reference, and source-group invariants.
- Modify `tools/extract/cli.py`: thread the structure audit output through export defaults.
- Modify `tests/extract/test_wiki_import.py`, `tests/extract/test_wiki_export.py`, `tests/extract/test_export_items.py`, and `tests/extract/test_export_validate.py`: integration and validation coverage.
- Modify `app/lib/item-catalog.ts` and `app/lib/item-catalog.test.ts`: schema version 6 structure types and strict parsing.
- Modify `app/lib/wiki-search.ts`, `app/lib/wiki-search.test.ts`, `app/components/wiki-search.tsx`, `app/components/wiki-search.test.tsx`, and `app/page.tsx`: remove the Wiki group and classify all Wiki records as DST.
- Create `app/components/structure-details.tsx` and `app/components/structure-details.test.tsx`: structure modal sections and reference navigation.
- Modify `app/components/item-detail-modal.tsx` and `app/components/item-detail-modal.test.tsx`: render structure details and DST provenance.
- Generate `data/generated/structure-icon-audit.json`, `data/generated/wiki.sqlite`, `public/data/items.json`, and Wiki detail/assets using the pipeline.
- Modify `docs/data-extraction.md`: document structure completeness and icon-audit workflow.

---

### Task 1: Normalize Structure Wiki Facts

**Files:**
- Create: `tools/extract/wiki_structures.py`
- Create: `tests/extract/test_wiki_structures.py`

**Interfaces:**
- Consumes: a Wiki page mapping with `page_id`, `title`, `canonical_url`, `categories`, `wikitext`, and revision metadata.
- Produces: `normalize_structure_page(page: Mapping[str, Any]) -> Optional[Dict[str, Any]]`.
- Produces keys: `origin`, `functions`, `destruction`, and `visual_candidates`, each with deterministic values and evidence locators.

- [ ] **Step 1: Write failing parser tests for representative structures**

```python
from tools.extract.wiki_structures import normalize_structure_page


def page(title: str, text: str) -> dict:
    return {
        "page_id": 10,
        "title": title,
        "canonical_url": f"https://dontstarve.wiki.gg/wiki/{title.replace(' ', '_')}",
        "categories": ["Category:Structures", "Category:Don't Starve Together"],
        "wikitext": text,
        "revision": {"id": 20, "sha1": "abc", "timestamp": "2026-07-17T00:00:00Z"},
    }


def test_normalizes_natural_indestructible_structure():
    result = normalize_structure_page(page(
        "Ancient Statue/DST",
        "{{Object Infobox|image=Ancient Statue DST.png|renewable=Yes|tool=Can't Be Destroyed|spawnCode=atrium_statue}}\n"
        "Found naturally in the [[Atrium]] Biome and respawned after the Ancient Fuelweaver is killed.",
    ))
    assert result["origin"]["naturallySpawned"] is True
    assert result["origin"]["renewable"] is True
    assert result["destruction"]["destroyable"] is False
    assert result["visual_candidates"][0]["title"] == "File:Ancient Statue DST.png"


def test_normalizes_fueled_functional_structure():
    result = normalize_structure_page(page(
        "Fire Pit/DST",
        "{{Object Infobox|image=Fire Pit.png|fuel=Fire Fuel|renewable=Yes|spawnCode=firepit}}\n"
        "The Fire Pit provides light and warmth and can be refueled.",
    ))
    keys = {fact["key"] for fact in result["functions"]["facts"]}
    assert {"fuel", "light", "warmth"} <= keys


def test_returns_none_for_non_structure_page():
    value = page("Gold Nugget", "{{Object Infobox|stack=40}}")
    value["categories"] = ["Category:Items"]
    assert normalize_structure_page(value) is None
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.extract.test_wiki_structures -v`

Expected: import failure for missing `tools.extract.wiki_structures`.

- [ ] **Step 3: Implement balanced-template parsing and conservative fact normalization**

```python
DETAIL_STATUSES = {"known", "none", "unknown"}


def normalize_structure_page(page: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    categories = {str(value).casefold() for value in page.get("categories", [])}
    if not any("structure" in value for value in categories):
        return None
    fields = _object_infobox_fields(str(page.get("wikitext") or ""))
    evidence = [{
        "source": str(page["canonical_url"]),
        "locator": f"revision:{page['revision']['id']}",
    }]
    return {
        "origin": _origin(fields, str(page.get("wikitext") or ""), evidence),
        "functions": _functions(fields, str(page.get("wikitext") or ""), evidence),
        "destruction": _destruction(fields, str(page.get("wikitext") or ""), evidence),
        "visual_candidates": _visual_candidates(fields, evidence),
    }
```

Implement exact field-name parsing plus bounded prose signals for `naturally
spawned`, `renewable`, `respawn`, `fuel`, `light`, `warmth`, `storage`,
`spawns`, `production`, `tool required`, and `can't be destroyed`. Every prose
fact keeps the Wiki revision evidence. Unknown fields remain absent.

- [ ] **Step 4: Run parser tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_wiki_structures -v`

Expected: all parser tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/extract/wiki_structures.py tests/extract/test_wiki_structures.py
git commit -m "feat: normalize structure wiki facts"
```

---

### Task 2: Persist Structure Facts in SQLite and Wiki Export

**Files:**
- Modify: `tools/extract/wiki_import.py`
- Modify: `tools/extract/wiki_export.py`
- Modify: `tests/extract/test_wiki_import.py`
- Modify: `tests/extract/test_wiki_export.py`

**Interfaces:**
- Consumes: `normalize_structure_page(page["mapping_input"])` from Task 1.
- Produces SQLite table `wiki_structure_details(page_id INTEGER PRIMARY KEY, details_json TEXT NOT NULL, source_schema_version INTEGER NOT NULL)`.
- Extends `WikiExport` with `structure_details: Dict[str, Dict[str, Any]]`, keyed by published item ID.

- [ ] **Step 1: Write failing importer/exporter tests**

```python
def test_import_persists_normalized_structure_details(self):
    summary = import_wiki(self.database, self.crawl)
    self.assertGreater(summary.pages, 0)
    with sqlite3.connect(self.database) as connection:
        row = connection.execute(
            "select details_json from wiki_structure_details where page_id=?", (10,)
        ).fetchone()
    self.assertEqual(json.loads(row[0])["origin"]["naturallySpawned"], True)


def test_export_exposes_structure_details_by_item_id(self):
    export = load_wiki_export(self.database, self.crawl)
    self.assertIn("base_game:atrium_statue", export.structure_details)
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python3 -m unittest tests.extract.test_wiki_import tests.extract.test_wiki_export -v`

Expected: failures because `wiki_structure_details` and `WikiExport.structure_details` do not exist.

- [ ] **Step 3: Add the normalized table transactionally**

```python
WIKI_STRUCTURE_SCHEMA = """CREATE TABLE wiki_structure_details (
      page_id INTEGER PRIMARY KEY,
      details_json TEXT NOT NULL,
      source_schema_version INTEGER NOT NULL,
      FOREIGN KEY(page_id) REFERENCES wiki_pages(page_id)
    )"""

WIKI_SCHEMA = WIKI_SCHEMA + (WIKI_STRUCTURE_SCHEMA,)

structure_rows = [
    {
        "page_id": page["page_id"],
        "details_json": _canonical_json(details),
        "source_schema_version": 1,
    }
    for page in pages
    for details in [normalize_structure_page(page["mapping_input"])]
    if details is not None
]
```

Insert rows inside the same `BEGIN IMMEDIATE` import transaction and include the
table in `WIKI_TABLES` so repeated imports remain idempotent.

- [ ] **Step 4: Load structure details into `WikiExport`**

```python
@dataclass(frozen=True)
class WikiExport:
    overlays: Dict[str, JsonObject]
    standalone_items: Tuple[JsonObject, ...]
    details: Tuple[JsonObject, ...]
    assets: Tuple[WikiAsset, ...]
    structure_details: Dict[str, JsonObject]
```

Map normalized rows through selected entity mappings. For unmatched structure
pages, key them by the same final standalone ID (`wiki:<page_id>`) used by
`merge_wiki_items`. Attach resolved Wiki image assets to each normalized visual
candidate without changing canonical fact precedence.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_wiki_import tests.extract.test_wiki_export -v`

Expected: all focused tests pass and `PRAGMA foreign_key_check` remains empty.

- [ ] **Step 6: Commit**

```bash
git add tools/extract/wiki_import.py tools/extract/wiki_export.py tests/extract/test_wiki_import.py tests/extract/test_wiki_export.py
git commit -m "feat: persist normalized structure wiki data"
```

---

### Task 3: Build Complete Structure Details and Reverse Station Recipes

**Files:**
- Create: `tools/extract/structure_details.py`
- Create: `tests/extract/test_structure_details.py`

**Interfaces:**
- Produces `build_structure_details(items, catalog_entities, wiki_details) -> Dict[str, JsonObject]`.
- Produces `build_station_outputs(items, catalog_entities) -> Dict[str, List[JsonObject]]`.
- Produces `audit_structure_visuals(items, catalog_entities, wiki_details) -> Tuple[List[JsonObject], Set[str]]`, returning report rows and excluded IDs.

- [ ] **Step 1: Write failing tests for construction, station outputs, and natural notes**

```python
def test_builds_construction_and_natural_origin_statuses(self):
    details = build_structure_details(self.items, self.entities, {})
    self.assertEqual(details["tu_tien:xd_liandanlu"]["construction"]["status"], "known")
    self.assertEqual(details["base_game:atrium_statue"]["construction"]["status"], "none")
    self.assertIn("tự sinh", details["base_game:atrium_statue"]["origin"]["note"])


def test_maps_station_tag_recipes_back_to_structure(self):
    outputs = build_station_outputs(self.items, self.entities)
    ids = [row["result"]["id"] for row in outputs["base_game:lunar_forge"]]
    self.assertEqual(ids, ["base_game:armor_lunarplant"])


def test_maps_tu_tien_recipe_filters_back_to_structure(self):
    outputs = build_station_outputs(self.items, self.entities)
    self.assertIn("tu_tien:xd_test_pill", {
        row["result"]["id"] for row in outputs["tu_tien:xd_liandanlu"]
    })
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.extract.test_structure_details -v`

Expected: import failure for missing `tools.extract.structure_details`.

- [ ] **Step 3: Implement status-aware structure assembly**

```python
def build_structure_details(
    items: Sequence[JsonObject],
    catalog_entities: Sequence[JsonObject],
    wiki_details: Mapping[str, JsonObject],
) -> Dict[str, JsonObject]:
    items_by_id = {str(item["id"]): item for item in items}
    entities_by_id = {str(entity["key"]): entity for entity in catalog_entities}
    station_outputs = build_station_outputs(items, catalog_entities)
    result = {}
    for item in items:
        if item.get("category") != "structure":
            continue
        item_id = str(item["id"])
        entity = entities_by_id.get(item_id)
        wiki = wiki_details.get(item_id, {})
        result[item_id] = {
            "origin": _origin(item, entity, wiki),
            "construction": _construction(item, entity),
            "functions": _functions(item, entity, wiki),
            "craftables": _craftables(station_outputs.get(item_id, [])),
            "destruction": _destruction(entity, wiki),
            "visual": _visual(item, entity, wiki),
        }
    return result
```

Use exact `station_tag` extraction from recipe restriction/config expressions,
tech mappings for canonical prototypers, and Tu Tiên `filters`/builder tags.
Resolve all result and ingredient references through the published item index.
Sort station outputs by result ID and evidence deterministically.

- [ ] **Step 4: Run builder tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_structure_details -v`

Expected: construction, natural origin, DST station, Tu Tiên station, function,
destruction, and deterministic ordering tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/extract/structure_details.py tests/extract/test_structure_details.py
git commit -m "feat: derive complete structure details"
```

---

### Task 4: Audit Missing Icons and Exclude Invalid Candidates

**Files:**
- Modify: `tools/extract/structure_details.py`
- Modify: `tests/extract/test_structure_details.py`
- Modify: `tools/extract/exclusions.py`

**Interfaces:**
- `audit_structure_visuals` returns exactly one row per input structure whose pre-resolution `sprite` is null.
- Audit row keys are `namespace`, `id`, `prefabId`, `name`, `englishName`, `wikiUrl`, `craftable`, `assets`, `classification`, `reason`, `evidence`, and `action`.

- [ ] **Step 1: Write failing classification and coverage tests**

```python
def test_audit_keeps_natural_structure_and_excludes_wrapper(self):
    rows, excluded = audit_structure_visuals(self.items, self.entities, self.wiki)
    by_id = {row["id"]: row for row in rows}
    self.assertEqual(by_id["base_game:atrium_statue"]["classification"], "natural_structure")
    self.assertEqual(by_id["base_game:atrium_statue"]["action"], "keep")
    self.assertEqual(by_id["base_game:evergreens"]["classification"], "technical_prefab")
    self.assertIn("base_game:evergreens", excluded)


def test_audit_covers_each_originally_iconless_structure_once(self):
    rows, _ = audit_structure_visuals(self.items, self.entities, self.wiki)
    expected = {item["id"] for item in self.items if item["category"] == "structure" and item["sprite"] is None}
    self.assertEqual({row["id"] for row in rows}, expected)
    self.assertEqual(len(rows), len(expected))
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python3 -m unittest tests.extract.test_structure_details -v`

Expected: classification assertions fail before the audit rules exist.

- [ ] **Step 3: Implement evidence-backed classification**

Classification rules, in order:

1. A craftable row with a Wiki/world candidate is `craftable_missing_asset` and `repair`.
2. A non-craftable row with a verified Wiki/world asset is `world_asset_only` and `keep`.
3. A non-craftable exact player-visible prefab with name/description, Wiki mapping,
   or gameplay facts is `natural_structure` and `keep`.
4. A module-family/wrapper/helper with no exact player-visible identity is
   `technical_prefab` and `exclude`.
5. A remaining row with no exact local identity and no unambiguous imported Wiki
   mapping is `unverified` and `exclude`.

Keep explicit curated exclusions in `NON_ITEM_PREFAB_IDS` only for cases whose
source evidence cannot be represented generically. Every curated entry includes
a code comment explaining the source proof.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_structure_details -v`

Expected: classification, action, evidence, coverage, and stable-sort tests pass.

- [ ] **Step 5: Commit**

```bash
git add tools/extract/structure_details.py tools/extract/exclusions.py tests/extract/test_structure_details.py
git commit -m "feat: audit structure visuals and invalid prefabs"
```

---

### Task 5: Integrate Export, Audit Artifact, and Validation

**Files:**
- Modify: `tools/extract/export_items.py`
- Modify: `tools/extract/validate.py`
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_export_items.py`
- Modify: `tests/extract/test_export_validate.py`

**Interfaces:**
- `export_items(database_path, catalog_path, assets_path, items_path, textures_path, wiki_crawl_path, wiki_details_path, wiki_assets_path, description_translations_path, detail_overrides_path, detail_report_path, structure_audit_path)` writes schema version 6 plus an atomic audit report; `structure_audit_path` defaults to `Path("data/generated/structure-icon-audit.json")`.
- Every published structure has non-null `structureDetails`; every non-structure has `structureDetails: null`.

- [ ] **Step 1: Write failing export and validation tests**

```python
def test_export_attaches_structure_details_and_writes_audit(self):
    export_items(
        self.database,
        self.catalog_path,
        self.assets_path,
        self.items_path,
        self.textures_path,
        wiki_crawl_path=self.wiki_crawl,
        wiki_details_path=self.wiki_details,
        wiki_assets_path=self.wiki_assets,
        description_translations_path=self.description_translations,
        detail_overrides_path=self.detail_overrides,
        detail_report_path=self.detail_report,
        structure_audit_path=self.audit_path,
    )
    payload = json.loads(self.items_path.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in payload["items"]}
    self.assertEqual(payload["schema_version"], 6)
    self.assertIsNotNone(by_id["base_game:atrium_statue"]["structureDetails"])
    self.assertIsNone(by_id["base_game:goldnugget"]["structureDetails"])
    self.assertEqual(json.loads(self.audit_path.read_text())["schema_version"], 1)


def test_validate_rejects_missing_structure_detail(self):
    report = validate_export(self.database, self.items_path, self.audit_path)
    self.assertEqual(report["structure_detail_errors"], [])
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python3 -m unittest tests.extract.test_export_items tests.extract.test_export_validate -v`

Expected: failures for schema version, missing `structureDetails`, and missing audit.

- [ ] **Step 3: Wire structure assembly after Wiki merging**

```python
wiki = load_wiki_export(database_path, wiki_crawl_path)
merged = merge_wiki_items(items["items"], wiki)
details = build_structure_details(merged, catalog["entities"], wiki.structure_details)
audit_rows, excluded_ids = audit_structure_visuals(merged, catalog["entities"], wiki.structure_details)
published = []
for item in merged:
    if item["id"] in excluded_ids:
        continue
    row = dict(item)
    row["structureDetails"] = details.get(item["id"])
    published.append(row)
items = {"schema_version": 6, "items": link_recipe_ingredients(published)}
```

Write the audit with the existing atomic JSON pattern. Ensure `wiki:*` standalone
rows retain `namespace: base_game`, so they naturally belong to DST.

- [ ] **Step 4: Add validation invariants**

Validate exact detail/null placement, status values, required evidence,
craftable visual coverage, station references, audit one-to-one coverage,
excluded-row absence, duplicate IDs, and that no public item uses a `wiki`
namespace. Include failures in `hard_failures` and stable diagnostic arrays.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_export_items tests.extract.test_export_validate -v`

Expected: all export/validation tests pass.

- [ ] **Step 6: Commit**

```bash
git add tools/extract/export_items.py tools/extract/validate.py tools/extract/cli.py tests/extract/test_export_items.py tests/extract/test_export_validate.py
git commit -m "feat: export and validate structure details"
```

---

### Task 6: Parse Schema Version 6 and Remove the Wiki Source Group

**Files:**
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/lib/wiki-search.ts`
- Modify: `app/lib/wiki-search.test.ts`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/page.tsx`

**Interfaces:**
- `ItemSourceFilter = "all" | ItemNamespace`.
- `ItemListEntry.structureDetails: StructureDetails | null`.
- `parseItemPayload` accepts only schema version 6.

- [ ] **Step 1: Write failing parser and source-filter tests**

```typescript
it("requires structure details only for structures", () => {
  const payload = structuredClone(validPayload);
  payload.items[0].category = "structure";
  payload.items[0].structureDetails = null;
  expect(() => parseItemPayload(payload)).toThrow(/structureDetails/i);
});

it("shows Wiki-backed items under DST", () => {
  const wikiBacked = { ...item, namespace: "base_game", wiki: wikiMetadata };
  expect(filterItems([wikiBacked], "", "base_game", "all", "all")).toEqual([wikiBacked]);
});

it("does not render a Wiki source filter", () => {
  render(<WikiSearch items={items} />);
  expect(screen.queryByRole("button", { name: "Wiki" })).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts app/components/wiki-search.test.tsx`

Expected: schema/parser and Wiki-filter assertions fail.

- [ ] **Step 3: Add strict structure types and parsers**

```typescript
export type StructureSectionStatus = "known" | "none" | "unknown";

export type StructureDetails = {
  origin: StructureOrigin;
  construction: StructureConstruction;
  functions: StructureFunctions;
  craftables: StructureCraftables;
  destruction: StructureDestruction;
  visual: StructureVisual;
};

export type ItemSourceFilter = "all" | ItemNamespace;
```

Add dedicated parsing helpers for evidence, item references, ingredients,
function facts, drops, visual candidates, and each section. Reject impossible
combinations such as `known` with empty required arrays, `none` with facts, or
non-structure rows with non-null `structureDetails`.

- [ ] **Step 4: Remove Wiki source branching and copy**

```typescript
const sourceFilters = [
  { value: "all", label: "Tất cả" },
  { value: "base_game", label: "DST" },
  { value: "tu_tien", label: "Tu Tiên" },
] as const;

const matchesSource = source === "all" || item.namespace === source;
```

Update hero/search copy from “DST, Tu Tiên và Wiki” to “DST và Tu Tiên” while
retaining Wiki-title search fields.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts app/components/wiki-search.test.tsx`

Expected: all focused tests pass.

- [ ] **Step 6: Commit**

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/lib/wiki-search.ts app/lib/wiki-search.test.ts app/components/wiki-search.tsx app/components/wiki-search.test.tsx app/page.tsx
git commit -m "feat: fold wiki records into DST"
```

---

### Task 7: Render Complete Structure Details in the Modal

**Files:**
- Create: `app/components/structure-details.tsx`
- Create: `app/components/structure-details.test.tsx`
- Modify: `app/components/item-detail-modal.tsx`
- Modify: `app/components/item-detail-modal.test.tsx`

**Interfaces:**
- `StructureDetails({ item, itemsById, onSelectItem, titleId })` renders all structure-specific sections.
- Reuses `GameSprite` and item-modal navigation for station outputs, ingredients, and drops.

- [ ] **Step 1: Write failing component tests for four modal states**

```tsx
it("renders construction, functions, station outputs, and destruction", () => {
  render(<StructureDetails item={station} itemsById={itemsById} onSelectItem={select} titleId="station" />);
  expect(screen.getByRole("heading", { name: "Cách xây" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Công dụng" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Có thể chế tạo tại đây" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Phá hủy và vật phẩm rơi" })).toBeInTheDocument();
});

it("explains a naturally spawned structure without an inventory icon", () => {
  render(<StructureDetails item={natural} itemsById={itemsById} onSelectItem={select} titleId="natural" />);
  expect(screen.getByText(/tự sinh/i)).toBeInTheDocument();
  expect(screen.getByText(/không thể chế tạo/i)).toBeInTheDocument();
});

it("navigates to a station output", async () => {
  render(<StructureDetails item={station} itemsById={itemsById} onSelectItem={select} titleId="station" />);
  await userEvent.click(screen.getByRole("button", { name: /Thulecite Crown/i }));
  expect(select).toHaveBeenCalledWith(itemsById.get("base_game:ruinshat"));
});
```

- [ ] **Step 2: Run component tests and verify RED**

Run: `npm test -- app/components/structure-details.test.tsx app/components/item-detail-modal.test.tsx`

Expected: import failure for missing `StructureDetails` component.

- [ ] **Step 3: Implement the focused structure renderer**

Render origin, construction, functions, craftables, and destruction as separate
semantic sections. `known` renders facts, `none` renders only meaningful
structure-specific states such as “Không thể chế tạo” or “Không thể phá hủy,”
and `unknown` renders “Chưa xác minh” with its reason. Use buttons only for
references present in `itemsById`; unresolved external references remain text.

- [ ] **Step 4: Integrate modal source and content ordering**

```tsx
const sourceLabel = item.namespace === "tu_tien" ? "Tu Tiên" : "DST";

const structuredContent = item.category === "structure" ? (
  <StructureDetails
    item={item}
    itemsById={itemsById}
    onSelectItem={onSelectItem}
    titleId={titleId}
  />
) : item.namespace === "tu_tien" ? (
  <TuTienItemSections {...props} />
) : (
  <CraftingSections item={item} titleId={titleId} />
);
```

Keep the Wiki article after structured content and retain the external canonical
link. Do not display a Wiki source badge.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `npm test -- app/components/structure-details.test.tsx app/components/item-detail-modal.test.tsx`

Expected: all structure/modal tests pass.

- [ ] **Step 6: Commit**

```bash
git add app/components/structure-details.tsx app/components/structure-details.test.tsx app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx
git commit -m "feat: render complete structure details"
```

---

### Task 8: Regenerate Data, Review the Full Icon Audit, and Verify

**Files:**
- Modify: `docs/data-extraction.md`
- Generate: `data/generated/structure-icon-audit.json`
- Generate: `data/generated/wiki.sqlite`
- Generate: `public/data/items.json`
- Generate: `public/data/wiki/pages/*.json`
- Generate: `public/assets/wiki/*`

**Interfaces:**
- The normal `import-wiki`, `export`, and `validate` lifecycle reproduces all generated artifacts.

- [ ] **Step 1: Document the structure refresh and audit review**

Add exact commands:

```bash
python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export
python3 -m tools.extract.cli validate
jq '.summary, .rows[] | select(.action != "keep")' data/generated/structure-icon-audit.json
```

Document classification meanings, why natural structures may lack inventory
icons, how Wiki/world visuals are selected, and that excluded rows remain in
SQLite/audit evidence.

- [ ] **Step 2: Re-import Wiki and regenerate export**

Run:

```bash
python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export
python3 -m tools.extract.cli validate
```

Expected: import/export complete, validation has no hard failures, and the audit
contains exactly the pre-resolution missing-icon structures once each.

- [ ] **Step 3: Inspect acceptance invariants directly**

Run:

```bash
jq '[.items[] | select(.category=="structure" and .structureDetails==null)] | length' public/data/items.json
jq '[.items[] | select(.namespace=="base_game" and .wiki!=null)] | length' public/data/items.json
jq '[.items[] | select(.category=="structure" and .sprite==null and .structureDetails.visual.status=="known")] | length' public/data/items.json
jq '.summary' data/generated/structure-icon-audit.json
sqlite3 data/generated/wiki.sqlite 'pragma foreign_key_check;'
```

Expected: zero structures without details; Wiki-backed records are non-zero and
all have the DST namespace; no visual claims `known` while the published sprite
is null; audit counts balance; foreign-key output is empty.

- [ ] **Step 4: Run complete verification**

Run:

```bash
python3 -m unittest discover -s tests/extract -v
python3 -m unittest discover -s tests/crawl_wiki -p 'test_*.py' -v
npm test
npm run lint
npm run build
git diff --check
```

Expected: every command exits 0 with no test failures, lint errors, build errors,
or whitespace errors.

- [ ] **Step 5: Commit generated artifacts and documentation**

```bash
git add docs/data-extraction.md data/generated/structure-icon-audit.json data/generated/wiki.sqlite public/data/items.json public/data/wiki public/assets/wiki
git commit -m "data: publish normalized structure catalog"
```

---

## Completion Audit

Before declaring completion, compare the generated state against all eight
acceptance criteria in
`docs/superpowers/specs/2026-07-17-structure-data-normalization-design.md`.
For each criterion, cite the direct test, report query, generated-file query, or
SQLite check that proves it. Missing or indirect evidence means the task remains
incomplete.
