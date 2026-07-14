# Real Item Search List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the eight-entry search demo with all real inventory items, real game sprites, Vietnamese search filters, recipe ingredient images, and bounded load-more rendering.

**Architecture:** The offline pipeline exports a compact `items.json` and a deterministic texture manifest from `catalog.json` plus `assets.json`. A separate explicit KTEX publishing command decodes only referenced textures into hashed PNG files. The server page validates and passes compact serializable records into the existing client search island, which composes focused sprite, recipe, and result-card components.

**Tech Stack:** Python 3.9 standard library, SQLite export JSON, external `ktech`-compatible decoder, Next.js 16 App Router, React 19, TypeScript, Tailwind CSS v4, Phosphor Icons, Vitest, Testing Library, unittest.

## Global Constraints

- Do not modify any file under `mod/3721846643`, `mod/3721859355`, or `mod/3731181944`.
- Do not crawl, scrape, or import data from a wiki or website.
- Keep `app/page.tsx` as a Server Component and `WikiSearch` as the interactive client boundary.
- Keep existing keyboard shortcuts, focus restoration, Unicode normalization, and screen-reader announcements.
- The Items page includes only records with `is_inventory_item === true`.
- The `base_game` namespace represents only dependencies referenced by Tu Tien, not the complete DST catalog.
- Generate stable PNG paths from verified texture SHA-256 values.
- Do not send asset evidence, source checksums, or the full catalog into the client component.
- Render 40 filtered results initially and reveal 40 more per action.
- Follow `node_modules/next/dist/docs/01-app/01-getting-started/05-server-and-client-components.md`, `public-folder.md`, and `loading.md` before implementation.
- Develop production behavior test-first and observe every new test fail for the expected reason.
- Preserve unrelated dirty-worktree changes.

---

### Task 1: Export the compact item and texture contracts

**Files:**
- Create: `tools/extract/export_items.py`
- Create: `tests/extract/test_export_items.py`

**Interfaces:**
- Consumes: parsed schema-version-1 `catalog.json` and `assets.json` payloads.
- Produces: `build_item_export(catalog: dict, assets: dict) -> tuple[dict, dict]`.
- Produces: `export_items(catalog_path: Path, assets_path: Path, items_path: Path, textures_path: Path) -> None`.
- Item output shape: `{ "schema_version": 1, "items": ItemListEntry[] }`.
- Texture output shape: `{ "schema_version": 1, "textures": [{ "sha256", "source", "texture" }] }`.

- [ ] **Step 1: Write the failing exporter tests**

Create fixtures inline in `tests/extract/test_export_items.py` with:

```python
catalog = {
    "schema_version": 1,
    "entities": [
        {
            "key": "base_game:goldnugget",
            "namespace": "base_game",
            "prefab_id": "goldnugget",
            "is_inventory_item": True,
            "name": {"vi": "Vàng", "en": "Gold Nugget"},
            "description": {"vi": None, "en": "A gold nugget."},
            "icon_key": "base_game:goldnugget",
            "recipes": [],
        },
        {
            "key": "tu_tien:xd_sword",
            "namespace": "tu_tien",
            "prefab_id": "xd_sword",
            "is_inventory_item": True,
            "name": {"vi": "Kiếm Thử", "en": "Test Sword"},
            "description": {"vi": "Một thanh kiếm", "en": None},
            "icon_key": "tu_tien:xd_sword",
            "recipes": [{
                "output_count": 1,
                "ingredients": [{"key": "base_game:goldnugget", "amount": 2.0, "position": 0}],
            }],
        },
    ],
}
```

Provide duplicate base-game assets where one is unavailable and assert the available row wins. Assert:

```python
items, textures = build_item_export(catalog, assets)
sword = next(item for item in items["items"] if item["id"] == "tu_tien:xd_sword")
self.assertEqual(sword["recipe"]["ingredients"][0]["name"], "Vàng")
self.assertEqual(sword["recipe"]["ingredients"][0]["amount"], 2)
self.assertEqual(sword["sprite"]["src"], "/assets/game/" + "b" * 64 + ".png")
self.assertEqual(len(textures["textures"]), 2)
```

Add separate tests for Vietnamese-English-prefab fallback, non-inventory exclusion, a zero-ingredient recipe, missing sprite, deterministic ordering, and byte-stable atomic writes.

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
python3 -m unittest tests.extract.test_export_items -v
```

Expected: import failure for `tools.extract.export_items`.

- [ ] **Step 3: Implement the minimal pure exporter**

Implement helpers with deterministic map lookups:

```python
def build_item_export(catalog: dict, assets: dict) -> tuple[dict, dict]:
    entities = {entity["key"]: entity for entity in catalog["entities"]}
    selected_assets = _select_inventory_assets(assets["assets"])
    items = []
    textures = {}
    for entity in catalog["entities"]:
        if not entity.get("is_inventory_item"):
            continue
        items.append(
            _build_item_entry(entity, entities, selected_assets, textures)
        )
    return (
        {"schema_version": 1, "items": sorted(items, key=lambda item: item["id"])},
        {"schema_version": 1, "textures": [textures[key] for key in sorted(textures)]},
    )
```

Selection order is: available first, highest selected evidence confidence, then atlas, texture, element, asset ID. Source is `mod` for `tu_tien` and `base_game` otherwise. Use a local atomic JSON writer matching `export_json.py` behavior.

- [ ] **Step 4: Run exporter tests and the full Python suite**

```bash
python3 -m unittest tests.extract.test_export_items -v
python3 -m unittest discover -s tests/extract -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit the checkpoint**

```bash
git add tools/extract/export_items.py tests/extract/test_export_items.py
git commit -m "feat: export compact item search data"
```

---

### Task 2: Publish referenced KTEX textures atomically

**Files:**
- Create: `tools/extract/publish_web_assets.py`
- Create: `tests/extract/test_publish_web_assets.py`

**Interfaces:**
- Consumes: the texture manifest from Task 1, immutable mod root, verified `images.zip`, source manifest, destination directory, decoder executable.
- Produces: `publish_web_assets(texture_manifest: Path, mod_root: Path, images_archive: Path, source_manifest: Path, output_dir: Path, decoder: str = "ktech") -> list[Path]`.

- [ ] **Step 1: Write failing publisher tests**

Use temporary mod files and a temporary base-game ZIP. Create an executable fake decoder that receives `INPUT OUTPUT_DIRECTORY` and writes `OUTPUT_DIRECTORY/<input-stem>.png`.

Assert:

```python
published = publish_web_assets(
    texture_manifest,
    mod_root,
    images_zip,
    source_manifest,
    output_dir,
    str(fake_decoder),
)
self.assertEqual([path.name for path in published], ["a" * 64 + ".png", "b" * 64 + ".png"])
self.assertTrue(all(path.read_bytes().startswith(b"\x89PNG") for path in published))
```

Add tests that identical hashes decode once, missing decoder raises a clear error, non-zero decoder exit preserves an existing output directory byte-for-byte, missing PNG output fails, and the base archive checksum is verified before reading a member.

- [ ] **Step 2: Run the tests and verify RED**

```bash
python3 -m unittest tests.extract.test_publish_web_assets -v
```

Expected: import failure for `tools.extract.publish_web_assets`.

- [ ] **Step 3: Implement staging and decoder invocation**

Use `tempfile.TemporaryDirectory`, `ZipFile`, `subprocess.run(..., check=True)`, and `verify_snapshot_archive`. Decode every unique texture into a staging directory first. Verify each result begins with the PNG signature and is non-empty. Only after every decode succeeds, swap the completed staging directory into `output_dir`, restoring the previous directory if the swap fails.

The decoder invocation is exactly:

```python
subprocess.run(
    [decoder, str(input_path), str(decode_directory)],
    check=True,
    capture_output=True,
    text=True,
)
```

- [ ] **Step 4: Run publisher tests and the full Python suite**

```bash
python3 -m unittest tests.extract.test_publish_web_assets -v
python3 -m unittest discover -s tests/extract -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit the checkpoint**

```bash
git add tools/extract/publish_web_assets.py tests/extract/test_publish_web_assets.py
git commit -m "feat: publish browser game textures"
```

---

### Task 3: Wire compact export and asset publication into the CLI

**Files:**
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_export_validate.py`
- Modify: `docs/data-extraction.md`

**Interfaces:**
- `export` additionally writes `public/data/items.json` and `data/generated/item-textures.json`.
- New command: `publish-assets --textures --mod-root --images --manifest --output --decoder`.
- `all` remains offline and never invokes the external decoder automatically.

- [ ] **Step 1: Add failing CLI tests**

Assert parser defaults and stage calls:

```python
args = cli.build_parser().parse_args(["publish-assets"])
self.assertEqual(args.decoder, "ktech")
self.assertEqual(args.output, Path("public/assets/game"))
```

Patch `export_catalog` and `export_items`, call `_export_stage`, and assert both are called in order. Patch `publish_web_assets`, dispatch `main()` with `publish-assets`, and assert explicit paths are forwarded. Preserve the existing test proving `all` never runs the runtime server or decoder.

- [ ] **Step 2: Run the targeted test and verify RED**

```bash
python3 -m unittest tests.extract.test_export_validate.ExportValidateTests.test_publish_assets_cli_has_explicit_inputs -v
```

Expected: parser rejects `publish-assets`.

- [ ] **Step 3: Implement CLI wiring and runbook text**

Add constants:

```python
ITEMS_JSON = Path("public/data/items.json")
ITEM_TEXTURES = Path("data/generated/item-textures.json")
WEB_ASSETS = Path("public/assets/game")
```

Extend `_export_stage` to call `export_items` after `export_catalog`. Add `publish-assets` dispatch calling `publish_web_assets`. Document that `all` refreshes JSON only, then `publish-assets` must be run explicitly with a reviewed decoder installation.

- [ ] **Step 4: Run all Python tests**

```bash
python3 -m unittest discover -s tests/extract -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit the checkpoint**

```bash
git add tools/extract/cli.py tests/extract/test_export_validate.py docs/data-extraction.md
git commit -m "feat: wire frontend item export commands"
```

---

### Task 4: Define and test the item search model

**Files:**
- Create: `app/lib/item-catalog.ts`
- Create: `app/lib/item-catalog.test.ts`
- Modify: `app/lib/wiki-search.ts`
- Modify: `app/lib/wiki-search.test.ts`

**Interfaces:**
- `ItemListEntry`, `RecipeIngredient`, `SpriteDescriptor`, and `ItemFilter` types.
- `parseItemPayload(value: unknown): readonly ItemListEntry[]` validates generated JSON at the server boundary.
- `filterItems(items: readonly ItemListEntry[], query: string, filter: ItemFilter): ItemListEntry[]`.
- Existing `normalizeSearchText` and `findNormalizedTextMatch` remain stable.

- [ ] **Step 1: Write failing contract and filter tests**

Use a Tu Tien sword and base-game gold fixture. Assert parsing rejects a malformed amount and accepts a zero-ingredient recipe. Assert search matches Vietnamese with and without accents, English name, prefab ID, description, and ingredient name. Assert namespace and craftable filters combine with text search.

Example:

```ts
expect(filterItems(items, "kiem", "all").map((item) => item.id)).toEqual([
  "tu_tien:xd_sword",
]);
expect(filterItems(items, "gold", "craftable").map((item) => item.id)).toEqual([
  "tu_tien:xd_sword",
]);
```

- [ ] **Step 2: Run targeted tests and verify RED**

```bash
npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts
```

Expected: import failure for `item-catalog` or missing `filterItems`.

- [ ] **Step 3: Implement the minimal types, parser, and filter**

Keep normalization in `wiki-search.ts`. Build searchable text from item names, prefab, description, and ingredient names. Use early returns for filter mismatch and one normalized joined string per item evaluation.

- [ ] **Step 4: Run targeted and full Vitest suites**

```bash
npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts
npm test
```

Expected: all tests pass.

- [ ] **Step 5: Commit the checkpoint**

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/lib/wiki-search.ts app/lib/wiki-search.test.ts
git commit -m "feat: define real item search model"
```

---

### Task 5: Build sprite, recipe, card, and interactive result UI

**Files:**
- Create: `app/components/game-sprite.tsx`
- Create: `app/components/game-sprite.test.tsx`
- Create: `app/components/recipe-ingredients.tsx`
- Create: `app/components/recipe-ingredients.test.tsx`
- Create: `app/components/item-result.tsx`
- Create: `app/components/item-result.test.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`

**Interfaces:**
- `GameSprite({ sprite, size, className?, label? })` renders UV-cropped background or fallback.
- `RecipeIngredients({ recipe })` renders normal, absent, and special recipes.
- `ItemResult({ item, query })` renders one accessible card.
- `WikiSearch({ items })` owns query, filter, result limit, shortcut, focus, status, and reset behavior.

- [ ] **Step 1: Write failing `GameSprite` tests**

Assert a full-texture UV produces `backgroundSize: 100% 100%`, partial UV produces finite position values, labeled sprites receive `role="img"`, decorative sprites are `aria-hidden`, and `null` renders a named fallback hook.

- [ ] **Step 2: Verify sprite tests fail, then implement and pass**

```bash
npm test -- app/components/game-sprite.test.tsx
```

Use these formulas with full-width/full-height guards:

```ts
const width = uv.u2 - uv.u1;
const height = uv.v2 - uv.v1;
const x = width >= 1 ? 50 : (uv.u1 / (1 - width)) * 100;
const yTop = 1 - uv.v2;
const y = height >= 1 ? 50 : (yTop / (1 - height)) * 100;
```

- [ ] **Step 3: Write failing recipe and item-card tests**

Assert normal recipe text contains `Vàng ×2`, its ingredient wrapper has accessible name `Vàng, số lượng 2`, no recipe shows `Không có công thức`, and an empty ingredient array shows `Công thức đặc biệt`. Assert `ItemResult` includes the visible name, source label, prefab, UI package icon, and highlighted query.

- [ ] **Step 4: Verify RED, implement recipe/card components, and verify GREEN**

```bash
npm test -- app/components/recipe-ingredients.test.tsx app/components/item-result.test.tsx
```

Use a consistent soft radius system, cool neutral surfaces, cobalt focus states, fixed sprite boxes, and a recipe layout that wraps below 768 px.

- [ ] **Step 5: Replace `WikiSearch` tests with real item behavior**

Preserve existing tests for shortcuts, Unicode highlight, category-group naming, reset, motion boundary, and live status. Change props and visible copy to Vietnamese. Add 41-item fixture coverage proving:

```ts
expect(screen.getAllByRole("listitem")).toHaveLength(40);
fireEvent.click(screen.getByRole("button", { name: "Xem thêm" }));
expect(screen.getAllByRole("listitem")).toHaveLength(41);
```

Then change query or filter and assert the visible limit resets to 40.

- [ ] **Step 6: Run the failing search component tests**

```bash
npm test -- app/components/wiki-search.test.tsx
```

Expected: failures because the old component accepts `entries`, renders old filters, and has no load-more behavior.

- [ ] **Step 7: Implement the new `WikiSearch` composition**

Use `useMemo` for filtered results, state setters that reset the visible limit in the same event, and `visibleResults = results.slice(0, visibleLimit)`. Keep the global keyboard effect with strict cleanup. Render a two-column card grid on desktop and one column below 768 px.

- [ ] **Step 8: Run component and full Vitest suites**

```bash
npm test -- app/components/game-sprite.test.tsx app/components/recipe-ingredients.test.tsx app/components/item-result.test.tsx app/components/wiki-search.test.tsx
npm test
```

Expected: all tests pass.

- [ ] **Step 9: Commit the checkpoint**

```bash
git add app/components app/lib
git commit -m "feat: render searchable item recipe cards"
```

---

### Task 6: Integrate generated data, publish real assets, and verify the page

**Files:**
- Modify: `app/page.tsx`
- Modify: `app/page.test.tsx`
- Create: `app/loading.tsx`
- Modify: `app/layout.tsx`
- Modify: `app/globals.css`
- Delete: `app/data/wiki-entries.ts`
- Create: `public/data/items.json` through the exporter
- Create: `data/generated/item-textures.json` through the exporter
- Create: `public/assets/game/*.png` through the publisher

**Interfaces:**
- `page.tsx` imports generated JSON, calls `parseItemPayload`, and passes `items` to `WikiSearch`.
- `loading.tsx` is a server-rendered skeleton matching the final grid shape.

- [ ] **Step 1: Write failing page and loading tests**

Assert the page renders `Don't Starve Together`, Vietnamese search label, real catalog count, and one known real item. Assert the loading component contains four skeleton cards and accessible loading text.

- [ ] **Step 2: Run page tests and verify RED**

```bash
npm test -- app/page.test.tsx
```

Expected: failures because the page still imports the demo dataset and no loading component exists.

- [ ] **Step 3: Generate compact JSON from current verified outputs**

```bash
python3 -m tools.extract.cli export
```

Expected: `public/data/items.json` contains 437 items and `data/generated/item-textures.json` contains only unique referenced textures.

- [ ] **Step 4: Install or select a reviewed `ktech`-compatible decoder and publish textures**

Preflight:

```bash
command -v ktech
```

If missing, stop and request approval before downloading or building the decoder. Once available:

```bash
python3 -m tools.extract.cli publish-assets --decoder "$(command -v ktech)"
```

Expected: every texture listed in the manifest has a non-empty hashed PNG under `public/assets/game/`.

- [ ] **Step 5: Implement page, loading shell, metadata, and final styling**

Import and validate the compact JSON only in the Server Component. Remove the demo data module. Localize document metadata and visible page copy. Keep one client island and the existing light cobalt palette. Add `content-visibility: auto` only if browser inspection shows the 40-card DOM benefits without accessibility regression.

- [ ] **Step 6: Run page and full test suites**

```bash
npm test -- app/page.test.tsx
npm test
python3 -m unittest discover -s tests/extract -v
```

Expected: all tests pass.

- [ ] **Step 7: Run static and production verification**

```bash
npm run lint
npm run build
python3 -m tools.extract.cli validate
git diff --check
```

Expected: zero lint/build errors, no extraction hard failures, and no whitespace errors.

- [ ] **Step 8: Run visual pre-flight**

Start the local server and inspect `/` at desktop and 375 px widths. Verify:

- Exactly one light theme and one cobalt accent.
- Card radius, input radius, and button radius follow one documented system.
- Main sprites and ingredient sprites show real decoded game assets.
- Recipe rows wrap without horizontal overflow.
- Missing sprite, no recipe, special recipe, no results, and loading states remain readable.
- Keyboard focus, `/`, Ctrl/Cmd+K, Escape, clear, filters, and load-more work.
- No em-dash or en-dash is present in visible copy.
- Motion is limited to meaningful state feedback and respects reduced motion.

- [ ] **Step 9: Commit the integration checkpoint**

```bash
git add app public/data/items.json public/assets/game data/generated/item-textures.json
git commit -m "feat: ship real item search list"
```

---

## Plan Self-Review

- Every requirement in the approved design is mapped to a task.
- The compact payload, texture manifest, and TypeScript contract use the same field names.
- The external decoder is isolated from `all` and requires explicit invocation.
- Every production unit begins with a failing test.
- No task modifies immutable mod directories or imports web content.
- The final integration does not stage unrelated existing database, coverage, IDE, or local mod changes.
