# Wiki Data Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import the 1,570-page selective Don't Starve crawl into the existing SQLite database and expose mapped plus standalone wiki items through the current Next.js list payload.

**Architecture:** Add wiki-owned relational tables and a deterministic importer beside the existing audit schema. Resolve only high-confidence page-to-prefab mappings, then extend the existing exporter with wiki list metadata, page-detail JSON, and content-addressed original images while keeping `app/page.tsx` on its current build-time JSON contract.

**Tech Stack:** Python 3 standard library (`sqlite3`, `json`, `hashlib`, `html.parser`, `shutil`), `unittest`, SQLite, TypeScript 5, React 19, Next.js 16.2, Vitest.

## Global Constraints

- The crawler source is `data/crawled/dontstarve-items` and contains only the latest revision for each page.
- Store all 1,570 pages and all valid recipes even when no existing prefab mapping can be selected.
- Existing game facts remain canonical; wiki data only fills missing list/detail data.
- A mapping is selected only when spawn code, normalized English name, or an unambiguous recognized alias resolves to exactly one base-game entity.
- Standalone list IDs use `wiki:<page_id>` and namespace `base_game`.
- List payloads remain compact; full page payloads live under `public/data/wiki/pages`.
- Original wiki images are published under content-addressed paths in `public/assets/wiki`.
- Import and export are deterministic, idempotent, foreign-key checked, and atomic at their output boundaries.
- Follow TDD: each production behavior starts with a test that is observed failing for the intended reason.

---

## File structure

- Create `tools/extract/wiki_import.py`: input validation, wiki schema, JSONL loading, mapping orchestration, and transactional database import.
- Create `tools/extract/wiki_mapping.py`: normalization, infobox spawn-code extraction, candidate indexes, and deterministic mapping decisions.
- Create `tools/extract/wiki_export.py`: database reads, standalone/mapped wiki item overlays, detail payload generation, and original-image publication.
- Modify `tools/extract/export_items.py`: accept wiki overlays, positive fractional ingredient amounts, payload schema v4, and wiki output paths.
- Modify `tools/extract/cli.py`: expose `import-wiki`, extend `export`, and include wiki import before export in the combined lifecycle.
- Create `tests/extract/test_wiki_import.py`: schema, validation, transactional replacement, and idempotence tests.
- Create `tests/extract/test_wiki_mapping.py`: exact spawn code, unique name, alias, ambiguity, and unmatched tests.
- Create `tests/extract/test_wiki_export.py`: merge, standalone item, recipe, detail JSON, and asset publication tests.
- Modify `tests/extract/test_export_items.py`: schema v4 and fractional quantity coverage.
- Modify `app/lib/item-catalog.ts`: schema v4 parser and optional wiki metadata types.
- Modify `app/lib/item-catalog.test.ts`: wiki metadata and fractional quantity parsing tests.
- Modify `app/lib/wiki-search.ts`: index wiki title and categories.
- Modify `app/lib/wiki-search.test.ts`: wiki-field search tests.
- Modify `docs/data-extraction.md`: document repeatable import/export commands and generated outputs.

---

### Task 1: Wiki mapping engine

**Files:**
- Create: `tools/extract/wiki_mapping.py`
- Test: `tests/extract/test_wiki_mapping.py`

**Interfaces:**
- Consumes: `page: Mapping[str, Any]` and existing entity rows containing `namespace`, `prefab_id`, and `name_en`.
- Produces: `build_entity_index(rows) -> EntityIndex` and `map_page(page, index) -> MappingDecision` where the decision contains `entity_key`, `method`, `confidence`, and `evidence`, or no selected key.

- [ ] **Step 1: Write failing mapping tests**

```python
class WikiMappingTests(unittest.TestCase):
    def setUp(self):
        self.index = build_entity_index([
            {"namespace": "base_game", "prefab_id": "goldnugget", "name_en": "Gold Nugget"},
            {"namespace": "base_game", "prefab_id": "fish_raw_small", "name_en": "Fish Morsel"},
            {"namespace": "base_game", "prefab_id": "fish_raw_small_cooked", "name_en": "Cooked Fish Morsel"},
        ])

    def test_exact_spawn_code_has_highest_precedence(self):
        page = {"page_id": 1, "title": "Gold", "wikitext": '|spawnCode = "goldnugget"'}
        self.assertEqual(map_page(page, self.index).entity_key, "base_game:goldnugget")
        self.assertEqual(map_page(page, self.index).method, "spawn_code")

    def test_unique_normalized_english_name_maps(self):
        decision = map_page({"page_id": 2, "title": "Fish Morsel", "wikitext": ""}, self.index)
        self.assertEqual(decision.entity_key, "base_game:fish_raw_small")
        self.assertEqual(decision.method, "english_name")

    def test_dst_suffix_is_a_canonical_alias(self):
        decision = map_page({"page_id": 3, "title": "Fish Morsel/DST", "wikitext": ""}, self.index)
        self.assertEqual(decision.entity_key, "base_game:fish_raw_small")
        self.assertEqual(decision.method, "canonical_alias")

    def test_ambiguous_name_is_not_selected(self):
        index = build_entity_index([
            {"namespace": "base_game", "prefab_id": "one", "name_en": "Shared"},
            {"namespace": "base_game", "prefab_id": "two", "name_en": "Shared"},
        ])
        decision = map_page({"page_id": 4, "title": "Shared", "wikitext": ""}, index)
        self.assertIsNone(decision.entity_key)
        self.assertEqual(decision.method, "ambiguous_name")
```

- [ ] **Step 2: Run mapping tests and verify RED**

Run: `python3 -m unittest tests.extract.test_wiki_mapping -v`

Expected: import failure for missing `tools.extract.wiki_mapping`.

- [ ] **Step 3: Implement normalization and decisions**

```python
@dataclass(frozen=True)
class MappingDecision:
    entity_key: str | None
    method: str
    confidence: float
    evidence: dict[str, Any]

@dataclass(frozen=True)
class EntityIndex:
    by_prefab: dict[str, tuple[str, ...]]
    by_name: dict[str, tuple[str, ...]]

def normalize_identity(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", folded.casefold()).strip()

def canonical_title(title: str) -> str:
    return re.sub(r"/DST$", "", title, flags=re.IGNORECASE).strip()

def extract_spawn_codes(wikitext: str) -> tuple[str, ...]:
    values = re.findall(r"\|\s*spawnCode\s*=\s*['\"]?([^\n|'\"}]+)", wikitext, re.IGNORECASE)
    return tuple(dict.fromkeys(value.strip().casefold() for value in values if value.strip()))

def map_page(page: Mapping[str, Any], index: EntityIndex) -> MappingDecision:
    # Exact spawn code first, then exact title, then canonical `/DST` alias.
    # Select only a one-element candidate tuple; otherwise return an explicit
    # ambiguous or unmatched decision with the evaluated candidates in evidence.
```

- [ ] **Step 4: Run mapping tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_wiki_mapping -v`

Expected: 4 tests pass.

- [ ] **Step 5: Commit mapping engine**

```bash
git add tools/extract/wiki_mapping.py tests/extract/test_wiki_mapping.py
git commit -m "feat: add deterministic wiki entity mapping"
```

---

### Task 2: Transactional wiki database importer

**Files:**
- Create: `tools/extract/wiki_import.py`
- Test: `tests/extract/test_wiki_import.py`

**Interfaces:**
- Consumes: crawler directory containing `manifest.json`, `pages.jsonl`, `recipes.jsonl`, `images.jsonl`, and `index.json`.
- Produces: `import_wiki(database_path: Path, crawl_root: Path) -> ImportSummary` and wiki-owned SQLite tables.

- [ ] **Step 1: Write failing importer tests using a minimal crawl fixture**

```python
def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

class WikiImportTests(unittest.TestCase):
    def test_imports_pages_recipes_ingredients_images_and_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database, [("base_game", "goldnugget", "Gold Nugget")])
            write_minimal_crawl(crawl, title="Gold Nugget", prefab="goldnugget")

            summary = import_wiki(database, crawl)

            with sqlite3.connect(database) as connection:
                self.assertEqual(connection.execute("select count(*) from wiki_pages").fetchone()[0], 1)
                self.assertEqual(connection.execute("select count(*) from wiki_recipes").fetchone()[0], 1)
                self.assertEqual(connection.execute("select count(*) from wiki_recipe_ingredients").fetchone()[0], 1)
                self.assertEqual(connection.execute("select entity_prefab_id from wiki_entity_mappings where selected=1").fetchone()[0], "goldnugget")
                self.assertEqual(connection.execute("pragma foreign_key_check").fetchall(), [])
            self.assertEqual(summary.pages, 1)

    def test_failed_reimport_preserves_previous_successful_tables(self):
        # Import a valid fixture, corrupt recipes.jsonl with a missing page_id,
        # assert ValueError, then assert the original wiki_pages row remains.

    def test_identical_import_is_idempotent(self):
        # Import twice and compare ordered rows from all wiki-owned tables.
```

- [ ] **Step 2: Run importer tests and verify RED**

Run: `python3 -m unittest tests.extract.test_wiki_import -v`

Expected: import failure for missing `tools.extract.wiki_import`.

- [ ] **Step 3: Implement schema and strict JSONL validation**

```python
WIKI_TABLES = (
    "wiki_recipe_ingredients", "wiki_recipes", "wiki_entity_mappings",
    "wiki_images", "wiki_pages", "wiki_import_runs",
)

@dataclass(frozen=True)
class ImportSummary:
    pages: int
    recipes: int
    ingredients: int
    images: int
    mapped: int
    unmatched: int

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"required crawl dataset is missing: {path}")
    rows = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSONL at {path}:{line_number}: {error.msg}") from error
        if not isinstance(value, dict):
            raise ValueError(f"JSONL row must be an object at {path}:{line_number}")
        rows.append(value)
    return rows

def import_wiki(database_path: Path, crawl_root: Path) -> ImportSummary:
    # Validate manifest and every row before BEGIN IMMEDIATE. In one transaction,
    # recreate wiki tables, insert canonical ordered rows, compute mapping via
    # map_page(), run PRAGMA foreign_key_check, record the completed run, commit.
    # Roll back on every exception.
```

- [ ] **Step 4: Run importer tests and verify GREEN**

Run: `python3 -m unittest tests.extract.test_wiki_import -v`

Expected: all importer tests pass and foreign-key checks are empty.

- [ ] **Step 5: Commit importer**

```bash
git add tools/extract/wiki_import.py tests/extract/test_wiki_import.py
git commit -m "feat: import crawled wiki data into sqlite"
```

---

### Task 3: CLI integration and lifecycle

**Files:**
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_database.py`

**Interfaces:**
- Consumes: `import_wiki(database, crawl_root)` from Task 2.
- Produces: `import-wiki --input PATH --database PATH`, and a combined lifecycle that imports wiki data after rebuilding the base database.

- [ ] **Step 1: Write failing CLI tests**

```python
def test_import_wiki_stage_uses_cli_paths(self):
    with mock.patch.object(cli, "import_wiki") as importer:
        importer.return_value = mock.Mock(
            pages=1, recipes=2, ingredients=3, images=4, mapped=1, unmatched=0
        )
        cli._import_wiki_stage(Path("crawl"), Path("wiki.sqlite"))
    importer.assert_called_once_with(Path("wiki.sqlite"), Path("crawl"))

def test_parser_exposes_import_wiki_defaults(self):
    args = cli.build_parser().parse_args(["import-wiki"])
    self.assertEqual(args.input, Path("data/crawled/dontstarve-items"))
    self.assertEqual(args.database, Path("data/generated/wiki.sqlite"))
```

- [ ] **Step 2: Run the CLI tests and verify RED**

Run: `python3 -m unittest tests.extract.test_database.DatabaseTests.test_import_wiki_stage_uses_cli_paths tests.extract.test_database.DatabaseTests.test_parser_exposes_import_wiki_defaults -v`

Expected: failures because the parser and stage do not exist.

- [ ] **Step 3: Add CLI constants, parser, stage, and dispatch**

```python
WIKI_CRAWL = Path("data/crawled/dontstarve-items")

import_wiki_parser = sub.add_parser("import-wiki")
import_wiki_parser.add_argument("--input", type=Path, default=WIKI_CRAWL)
import_wiki_parser.add_argument("--database", type=Path, default=DATABASE)

def _import_wiki_stage(input_path: Path = WIKI_CRAWL, database: Path = DATABASE):
    summary = import_wiki(database, input_path)
    print(
        f"{database} wiki_pages={summary.pages} recipes={summary.recipes} "
        f"ingredients={summary.ingredients} images={summary.images} "
        f"mapped={summary.mapped} unmatched={summary.unmatched}"
    )
    return summary
```

- [ ] **Step 4: Run CLI and complete Python unit suites**

Run: `python3 -m unittest tests.extract.test_database -v`

Expected: all database/CLI tests pass.

- [ ] **Step 5: Commit CLI integration**

```bash
git add tools/extract/cli.py tests/extract/test_database.py
git commit -m "feat: add wiki import command"
```

---

### Task 4: Wiki-aware list/detail exporter

**Files:**
- Create: `tools/extract/wiki_export.py`
- Modify: `tools/extract/export_items.py`
- Test: `tests/extract/test_wiki_export.py`
- Modify: `tests/extract/test_export_items.py`

**Interfaces:**
- Consumes: wiki tables from Task 2 and the existing `build_item_export()` result.
- Produces: `load_wiki_export(database_path, crawl_root) -> WikiExport`, item overlays, standalone items, page detail payloads, and published image files.

- [ ] **Step 1: Write failing exporter tests**

```python
class WikiExportTests(unittest.TestCase):
    def test_merges_mapped_page_and_emits_unmapped_page(self):
        export = load_wiki_export(self.database, self.crawl_root)
        merged = merge_wiki_items(existing_items, export)
        by_id = {item["id"]: item for item in merged}
        self.assertEqual(by_id["base_game:goldnugget"]["wiki"]["pageId"], 10)
        self.assertEqual(by_id["wiki:11"]["namespace"], "base_game")
        self.assertEqual(by_id["wiki:11"]["wiki"]["mappingState"], "unmatched")

    def test_fractional_wiki_recipe_amount_is_preserved(self):
        item = merge_wiki_items([], self.export_with_amount(0.5))[0]
        self.assertEqual(item["recipe"]["ingredients"][0]["amount"], 0.5)

    def test_exports_detail_json_and_content_addressed_original_image(self):
        export_wiki_artifacts(self.database, self.crawl_root, self.detail_root, self.asset_root)
        detail = json.loads((self.detail_root / "10.json").read_text())
        self.assertEqual(detail["pageId"], 10)
        self.assertTrue(detail["html"])
        self.assertEqual(list(self.asset_root.iterdir())[0].read_bytes(), b"original-image")
```

- [ ] **Step 2: Run exporter tests and verify RED**

Run: `python3 -m unittest tests.extract.test_wiki_export -v`

Expected: import failure for missing `tools.extract.wiki_export`.

- [ ] **Step 3: Implement wiki export objects and merge rules**

```python
@dataclass(frozen=True)
class WikiExport:
    overlays: dict[str, dict[str, Any]]
    standalone_items: tuple[dict[str, Any], ...]
    details: tuple[dict[str, Any], ...]
    assets: tuple[WikiAsset, ...]

def merge_wiki_items(items: list[dict[str, Any]], wiki: WikiExport) -> list[dict[str, Any]]:
    merged = []
    seen = set()
    for item in items:
        overlay = wiki.overlays.get(item["id"])
        value = apply_missing_field_overlay(item, overlay) if overlay else item
        merged.append(value)
        seen.add(value["id"])
    for item in wiki.standalone_items:
        if item["id"] in seen:
            raise ValueError(f"duplicate item id: {item['id']}")
        merged.append(item)
        seen.add(item["id"])
    return sorted(merged, key=lambda value: value["id"])
```

Update the compact payload to schema version 4 and replace integer-only ingredient validation with finite positive numeric validation:

```python
def _positive_number(value: Any, field: str) -> int | float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be a positive number")
    return int(value) if float(value).is_integer() else float(value)
```

- [ ] **Step 4: Extend `export_items()` atomically**

```python
def export_items(
    database_path: Path,
    catalog_path: Path,
    assets_path: Path,
    items_path: Path,
    textures_path: Path,
    wiki_crawl_path: Path = Path("data/crawled/dontstarve-items"),
    wiki_details_path: Path = Path("public/data/wiki/pages"),
    wiki_assets_path: Path = Path("public/assets/wiki"),
) -> None:
    # Build current entries, detect wiki tables, merge WikiExport, atomically
    # write schema v4 items/textures, then replace staged detail/asset trees.
```

- [ ] **Step 5: Run exporter suites and verify GREEN**

Run: `python3 -m unittest tests.extract.test_export_items tests.extract.test_wiki_export -v`

Expected: all exporter tests pass; no temporary file/directory remains.

- [ ] **Step 6: Commit exporter**

```bash
git add tools/extract/wiki_export.py tools/extract/export_items.py tests/extract/test_wiki_export.py tests/extract/test_export_items.py
git commit -m "feat: export wiki items and detail assets"
```

---

### Task 5: Frontend schema and search support

**Files:**
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/lib/wiki-search.ts`
- Modify: `app/lib/wiki-search.test.ts`

**Interfaces:**
- Consumes: items payload schema version 4.
- Produces: optional `WikiItemMetadata` on `ItemListEntry` and wiki-aware search.

- [ ] **Step 1: Write failing TypeScript parser/search tests**

```typescript
it("accepts wiki metadata and fractional recipe quantities", () => {
  const payload = structuredClone(validPayload);
  payload.schema_version = 4;
  payload.items[0].recipe.ingredients[0].amount = 0.5;
  payload.items[0].wiki = {
    pageId: 158,
    title: "Fish Morsel",
    canonicalUrl: "https://dontstarve.wiki.gg/wiki/Fish_Morsel",
    categories: ["Food", "Fishes"],
    mappingState: "mapped",
    detailUrl: "/data/wiki/pages/158.json",
  };
  expect(parseItemPayload(payload)[0].wiki?.pageId).toBe(158);
});

it.each(["fish morsel", "fishes"])("matches wiki field %s", (query) => {
  expect(filterItems([wikiItem], query, "all", "all")).toEqual([wikiItem]);
});
```

- [ ] **Step 2: Run frontend tests and verify RED**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts`

Expected: schema-version and wiki-field assertions fail.

- [ ] **Step 3: Implement schema v4 parser and types**

```typescript
export interface WikiItemMetadata {
  readonly pageId: number;
  readonly title: string;
  readonly canonicalUrl: string;
  readonly categories: readonly string[];
  readonly mappingState: "mapped" | "unmatched";
  readonly detailUrl: string;
}

export interface ItemListEntry {
  // Existing fields stay unchanged.
  readonly wiki: WikiItemMetadata | null;
}
```

Validate finite positive numeric ingredient amounts and require `wiki` to be either `null` or a complete metadata object. Search joins `wiki.title` and `wiki.categories` with the existing searchable fields.

- [ ] **Step 4: Run frontend unit tests and verify GREEN**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts`

Expected: all selected Vitest tests pass.

- [ ] **Step 5: Commit frontend contract**

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/lib/wiki-search.ts app/lib/wiki-search.test.ts
git commit -m "feat: expose wiki items in catalog search"
```

---

### Task 6: Real import, documentation, and end-to-end verification

**Files:**
- Modify: `docs/data-extraction.md`
- Generate: `data/generated/wiki.sqlite`
- Generate: `public/data/items.json`
- Generate: `public/data/wiki/pages/*.json`
- Generate: `public/assets/wiki/*`

**Interfaces:**
- Consumes: all prior tasks and the completed real crawl.
- Produces: repeatable commands, real imported database, and deployable frontend artifacts.

- [ ] **Step 1: Document the commands and outputs**

```markdown
## Import selective wiki crawl

python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export

The importer updates wiki-owned tables in `data/generated/wiki.sqlite`.
The exporter updates `public/data/items.json`, per-page detail JSON under
`public/data/wiki/pages`, and referenced original images under
`public/assets/wiki`.
```

- [ ] **Step 2: Run the real import and export**

Run:

```bash
python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export
```

Expected: import reports 1,570 pages, 1,444 recipes, zero foreign-key errors, and export writes schema v4.

- [ ] **Step 3: Verify database and generated references**

Run:

```bash
sqlite3 data/generated/wiki.sqlite "SELECT COUNT(*) FROM wiki_pages; SELECT COUNT(*) FROM wiki_recipes; PRAGMA foreign_key_check;"
jq '{schema_version,items:(.items|length),unique_ids:([.items[].id]|unique|length),wiki:([.items[]|select(.wiki != null)]|length)}' public/data/items.json
```

Expected: page count `1570`, recipe count `1444`, no foreign-key rows, schema version `4`, and `items == unique_ids`.

- [ ] **Step 4: Run full verification from a clean command boundary**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
npm test
npm run lint
npm run build
```

Expected: every command exits 0 with zero failed tests and zero lint/build errors.

- [ ] **Step 5: Commit documentation and generated data allowed by repository policy**

```bash
git add docs/data-extraction.md
git commit -m "docs: document wiki database import"
```

Before staging generated artifacts, inspect `.gitignore` and `git status`; do not force-add ignored crawl/database outputs.

---

## Self-review

- Spec coverage: importer, relational schema, all pages, recipes, images, mapping precedence, unmatched pages, compact list, separate details, idempotence, and verification each have an owning task.
- Placeholder scan: no deferred implementation or unspecified error-handling step remains.
- Type consistency: `MappingDecision`, `ImportSummary`, `WikiExport`, `WikiItemMetadata`, schema version 4, `wiki:<page_id>`, and default paths are consistent across producer and consumer tasks.
- Scope: the plan changes data availability and search only; visual redesign of the detail modal remains a separate feature.
