# Nightmare Fuel Wiki Sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize the complete Nightmare Fuel Drop table and Usage sections from imported Wiki wikitext, render them as dedicated item-detail regions, and remove Related pages and Technical information from item details.

**Architecture:** A focused Python module parses Wiki table rows and balanced Recipe templates during deterministic export. Page `210449` receives a backward-compatible optional `normalized` detail object and de-duplicated article HTML. The frontend validates that optional object and renders it through a dedicated React component before the remaining article.

**Tech Stack:** Python 3 standard library, SQLite, Next.js 16.2 App Router, React 19.2, TypeScript 5, Tailwind CSS 4, Phosphor Icons, unittest, Vitest, Testing Library.

## Global Constraints

- Work directly on `master` as explicitly approved by the user.
- Treat `wiki_pages.wikitext` for page `210449` as the displayed source of truth.
- Keep per-page Wiki detail schema version 1 and add `normalized.schema_version = 1` optionally.
- Publish normalized sections only for page `210449` in this pilot.
- Preserve Wiki source order, exact quantity strings, exact chance strings, and optional Wiki metadata.
- Fail export if either requested pilot section is missing or malformed.
- Remove the raw Drop table and Usage HTML only after both normalized sections succeed.
- Do not add dependencies, change crawler behavior, change routes, or change mapping heuristics.
- Remove Related pages and Technical information from every item detail.
- Preserve modal keyboard behavior, compact item recipes, article loading, retry, images, canonical link, and remaining article HTML.
- Keep the existing light theme, cool-neutral palette, blue accent, Phosphor icons, and 12 to 16 px radius system.
- Use `DESIGN_VARIANCE: 3`, `MOTION_INTENSITY: 1`, and `VISUAL_DENSITY: 7`.

---

### Task 1: Normalize Wiki Drop table and Usage wikitext

**Files:**
- Create: `tools/extract/wiki_sections.py`
- Create: `tests/extract/test_wiki_sections.py`

**Interfaces:**
- Consumes: `normalize_identity`, Nightmare Fuel wikitext, canonical Wiki base URL, and `Mapping[str, str]` from normalized Wiki title to selected entity ID.
- Produces: `normalize_drop_and_usage_sections(wikitext, subject_title, entity_ids_by_title) -> Dict[str, Any]` and `strip_drop_and_usage_html(value) -> str`.

- [x] **Step 1: Write realistic failing Drop table tests**

Create a fixture containing the complete 10-row Nightmare Fuel Drop table from page `210449`. Assert exact source order, quantity, chance, context preservation, canonical URLs, and resolved entity IDs:

```python
sections = normalize_drop_and_usage_sections(
    NIGHTMARE_FUEL_WIKITEXT,
    "Nightmare Fuel",
    {
        normalize_identity("Beardling"): "base_game:beardling",
        normalize_identity("Night Light"): "base_game:nightlight",
    },
)

self.assertEqual(len(sections["dropTable"]["rows"]), 10)
self.assertEqual(sections["dropTable"]["rows"][0]["quantity"], "1-3")
self.assertEqual(sections["dropTable"]["rows"][0]["chance"], "40%")
self.assertEqual(
    [source["title"] for source in sections["dropTable"]["rows"][0]["sources"]],
    ["Beardling", "Crab Beardling"],
)
self.assertEqual(
    sections["dropTable"]["rows"][0]["sources"][0]["entityId"],
    "base_game:beardling",
)
```

- [x] **Step 2: Write realistic failing Usage tests**

Include the complete 30 Recipe templates from page `210449`. Assert source order, default counts, station, DLC, character, note, and internal mapping:

```python
recipes = sections["usage"]["recipes"]
self.assertEqual(len(recipes), 30)
night_light = next(recipe for recipe in recipes if recipe["result"]["title"] == "Night Light")
self.assertEqual(night_light["nightmareFuelAmount"], 2)
self.assertEqual(
    [(value["item"]["title"], value["amount"]) for value in night_light["ingredients"]],
    [("Gold Nugget", 8), ("Red Gem", 1)],
)
self.assertEqual(night_light["station"], "Prestihatitator")
self.assertEqual(night_light["result"]["entityId"], "base_game:nightlight")
self.assertEqual(
    next(recipe for recipe in recipes if recipe["result"]["title"] == "Dripple Pipes")["dlc"],
    "Shipwrecked",
)
```

- [x] **Step 3: Run the focused test and confirm RED**

```bash
python3 -m unittest tests.extract.test_wiki_sections -v
```

Expected: import failure because `tools.extract.wiki_sections` does not exist.

- [x] **Step 4: Implement balanced template and section parsing**

Implement standard-library helpers with these exact public signatures:

```python
def normalize_drop_and_usage_sections(
    wikitext: str,
    subject_title: str,
    entity_ids_by_title: Mapping[str, str],
) -> Dict[str, Any]:
    drop_rows = _parse_drop_rows(
        _required_section(wikitext, "Drop table"),
        entity_ids_by_title,
    )
    usage_recipes = _parse_usage_recipes(
        _required_section(wikitext, "Usage"),
        subject_title,
        entity_ids_by_title,
    )
    if not drop_rows:
        raise ValueError("Drop table section contains no data rows")
    if not usage_recipes:
        raise ValueError("Usage section contains no Recipe templates")
    return {
        "dropTable": {"rows": drop_rows},
        "usage": {"recipes": usage_recipes},
    }

def strip_drop_and_usage_html(value: str) -> str:
    drop_heading = re.search(
        r'<h3[^>]*>.*?id="Drop_table".*?</h3>', value, re.IGNORECASE | re.DOTALL
    )
    usage_heading = re.search(
        r'<h2[^>]*>.*?id="Usage".*?</h2>', value, re.IGNORECASE | re.DOTALL
    )
    if drop_heading is None or usage_heading is None or usage_heading.start() <= drop_heading.start():
        raise ValueError("Drop table and Usage HTML headings are required")
    next_heading = re.search(
        r'<h2(?:\s|>)', value[usage_heading.end():], re.IGNORECASE
    )
    if next_heading is None:
        raise ValueError("Usage HTML section must have a following level-2 heading")
    end = usage_heading.end() + next_heading.start()
    return value[:drop_heading.start()] + value[end:]
```

The implementation must:

- locate headings case-insensitively;
- split Wiki table rows without splitting nested templates or links;
- recognize `Pic`, `pic32`, and similar image-reference templates;
- normalize Wiki links and template labels into ordered references;
- scan balanced MediaWiki Recipe templates;
- split only top-level pipe parameters;
- default missing counts to 1;
- separate the subject from other ingredients;
- construct canonical URLs with `urllib.parse.quote`;
- attach an entity ID only from `entity_ids_by_title`;
- raise `ValueError` naming Drop table or Usage when missing;
- remove the sanitized HTML range from `id="Drop_table"` through the next level-2 heading after `id="Usage"`.

- [x] **Step 5: Run focused tests and confirm GREEN**

```bash
python3 -m unittest tests.extract.test_wiki_sections -v
```

Expected: all normalization and HTML de-duplication tests pass.

- [x] **Step 6: Commit the normalizer**

```bash
git add tools/extract/wiki_sections.py tests/extract/test_wiki_sections.py
git commit -m "feat: normalize wiki drop and usage sections"
```

---

### Task 2: Publish the Nightmare Fuel pilot detail contract

**Files:**
- Modify: `tools/extract/wiki_export.py`
- Modify: `tests/extract/test_wiki_export.py`

**Interfaces:**
- Consumes: Task 1 normalizer, selected Wiki entity mappings, page detail rows.
- Produces: optional `normalized` detail object for page `210449` and de-duplicated `html` for that page only.

- [x] **Step 1: Write a failing pilot export test**

Insert a page `210449` fixture with the full Nightmare Fuel wikitext and representative rendered HTML. Map it to `base_game:nightmarefuel`, then assert:

```python
detail = next(value for value in wiki.details if value["pageId"] == 210449)
self.assertEqual(detail["normalized"]["schema_version"], 1)
self.assertEqual(len(detail["normalized"]["dropTable"]["rows"]), 10)
self.assertEqual(len(detail["normalized"]["usage"]["recipes"]), 30)
self.assertNotIn('id="Drop_table"', detail["html"])
self.assertNotIn('id="Usage"', detail["html"])
self.assertIn('id="Trivia"', detail["html"])
```

Also assert that the existing fixture page does not receive a `normalized` key.

- [x] **Step 2: Run the export test and confirm RED**

```bash
python3 -m unittest tests.extract.test_wiki_export.WikiExportTests.test_normalizes_only_the_nightmare_fuel_pilot -v
```

Expected: failure because the detail exporter does not publish normalized sections.

- [x] **Step 3: Wire the pilot into `load_wiki_export`**

Add:

```python
NORMALIZED_SECTION_PAGE_IDS = frozenset({210449})
```

Build `entity_ids_by_title` only from selected mappings:

```python
entity_ids_by_title = {
    normalize_identity(page["title"]):
        f"{page['entity_namespace']}:{page['entity_prefab_id']}"
    for page in pages
    if page["selected"]
}
```

When a page ID is allowlisted, call Task 1 functions, add
`normalized.schema_version = 1`, and publish stripped HTML. All other detail
objects keep the existing fields and HTML.

- [x] **Step 4: Run focused export suites and confirm GREEN**

```bash
python3 -m unittest tests.extract.test_wiki_export tests.extract.test_wiki_sections -v
```

Expected: all Wiki export and section tests pass.

- [x] **Step 5: Commit pilot export wiring**

```bash
git add tools/extract/wiki_export.py tests/extract/test_wiki_export.py
git commit -m "feat: publish nightmare fuel wiki sections"
```

---

### Task 3: Validate and render normalized Wiki sections

**Files:**
- Modify: `app/lib/wiki-detail.ts`
- Modify: `app/lib/wiki-detail.test.ts`
- Create: `app/components/wiki-structured-sections.tsx`
- Create: `app/components/wiki-structured-sections.test.tsx`
- Modify: `app/components/wiki-article.tsx`
- Modify: `app/components/wiki-article.test.tsx`

**Interfaces:**
- Consumes: optional `normalized` detail JSON, item lookup map, and item-selection callback.
- Produces: `NormalizedWikiSections`, strict optional parser support, and `WikiStructuredSections`.

- [x] **Step 1: Write failing TypeScript contract tests**

Extend the valid detail fixture with one Drop row and one Usage recipe. Assert exact parsed output and rejection of malformed counts, missing references, empty arrays, and schema version 2:

```typescript
expect(parseWikiPageDetail(detail).normalized?.dropTable.rows).toHaveLength(1);
expect(parseWikiPageDetail(detail).normalized?.usage.recipes[0]).toMatchObject({
  nightmareFuelAmount: 2,
  station: "Prestihatitator",
});
expect(() =>
  parseWikiPageDetail({
    ...detail,
    normalized: { schema_version: 2, dropTable: { rows: [] }, usage: { recipes: [] } },
  }),
).toThrow();
```

- [x] **Step 2: Run the parser test and confirm RED**

```bash
npm test -- app/lib/wiki-detail.test.ts
```

Expected: failure because `WikiPageDetail` has no normalized contract.

- [x] **Step 3: Implement strict optional parsing**

Add exact exported types:

```typescript
export type NormalizedWikiReference = {
  title: string;
  url: string;
  entityId: string | null;
};

export type NormalizedWikiSections = {
  dropTable: { rows: readonly NormalizedWikiDropRow[] };
  usage: { recipes: readonly NormalizedWikiUsageRecipe[] };
};
```

Validate non-empty strings, nullable strings, positive amounts, non-empty source
arrays, non-empty Drop rows, non-empty Usage recipes, URL strings, and exact
normalized schema version 1. Return `normalized: null` when absent.

- [x] **Step 4: Write failing structured-region component tests**

Render one Drop row and two Usage recipes, one with a mapped internal item.
Assert headings, counts, exact quantity/chance, ingredient amounts, DLC group,
station, note, external Wiki links, and internal item selection.

```typescript
expect(screen.getByRole("heading", { name: "Drop table" })).toBeDefined();
expect(screen.getByText("10 nguồn từ Wiki")).toBeDefined();
expect(screen.getByText("40%")).toBeDefined();
expect(screen.getByRole("heading", { name: "Usage" })).toBeDefined();
fireEvent.click(screen.getByRole("button", { name: "Đèn bóng đêm" }));
expect(onSelectItem).toHaveBeenCalledWith(nightLight);
```

- [x] **Step 5: Run the component test and confirm RED**

```bash
npm test -- app/components/wiki-structured-sections.test.tsx
```

Expected: import failure because the component does not exist.

- [x] **Step 6: Implement `WikiStructuredSections`**

Render semantic lists inside two bordered regions. Use `grid-cols-1 md:grid-cols-2`,
mono numeric facts, DLC subgroup headings, `GameSprite` for resolved internal
items, internal buttons for selectable mapped items, and external anchors for
unresolved references. Do not truncate rows or recipes.

- [x] **Step 7: Integrate normalized data into `WikiArticle`**

Add optional props:

```typescript
itemsById?: ReadonlyMap<string, ItemListEntry>;
onSelectItem?: (item: ItemListEntry) => void;
```

Render `WikiStructuredSections` after the article header and saved-image strip,
but before `.wiki-article`. Preserve loading, error, retry, and canonical link
behavior.

- [x] **Step 8: Run focused frontend tests and confirm GREEN**

```bash
npm test -- app/lib/wiki-detail.test.ts app/components/wiki-structured-sections.test.tsx app/components/wiki-article.test.tsx
```

Expected: all parser, structured-region, and article tests pass.

- [x] **Step 9: Commit the frontend contract and regions**

```bash
git add app/lib/wiki-detail.ts app/lib/wiki-detail.test.ts app/components/wiki-structured-sections.tsx app/components/wiki-structured-sections.test.tsx app/components/wiki-article.tsx app/components/wiki-article.test.tsx
git commit -m "feat: render structured wiki item sections"
```

---

### Task 4: Simplify the modal and connect internal item navigation

**Files:**
- Modify: `app/components/item-detail-modal.tsx`
- Modify: `app/components/item-detail-modal.test.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`

**Interfaces:**
- Consumes: the existing `itemsById` map, selected item state, and Task 3 `WikiArticle` props.
- Produces: a detail modal without Technical information or Related pages and with structured-section internal item navigation.

- [x] **Step 1: Write failing modal-removal tests**

Update modal tests to assert:

```typescript
expect(screen.queryByRole("heading", { name: "Thông tin kỹ thuật" })).toBeNull();
expect(screen.queryByRole("heading", { name: "Trang liên quan" })).toBeNull();
expect(screen.queryByText("Prefab ID")).toBeNull();
expect(screen.queryByText("Halberd/DST")).toBeNull();
```

Add a test proving `itemsById` and `onSelectItem` reach the structured Wiki
component and selecting a resolved Usage result calls the callback.

- [x] **Step 2: Run focused modal tests and confirm RED**

```bash
npm test -- app/components/item-detail-modal.test.tsx app/components/wiki-search.test.tsx
```

Expected: failures because both panels still render and navigation props are not connected.

- [x] **Step 3: Remove obsolete modal panels**

Delete the `hasRealPrefab` import, real-Prefab local, Technical information
section, and Related pages section. Keep metadata in the list contract for
search compatibility, but do not render it in the modal.

- [x] **Step 4: Connect item selection**

Change the modal signature to:

```typescript
export function ItemDetailModal({
  item,
  itemsById,
  onSelectItem,
  onClose,
}: {
  item: ItemListEntry;
  itemsById: ReadonlyMap<string, ItemListEntry>;
  onSelectItem: (item: ItemListEntry) => void;
  onClose: () => void;
})
```

Pass the map and callback to `WikiArticle`. In `WikiSearch`, pass its memoized
`itemsById` and `setSelectedItem` to the modal.

- [x] **Step 5: Run focused modal and search tests and confirm GREEN**

```bash
npm test -- app/components/item-detail-modal.test.tsx app/components/wiki-search.test.tsx app/components/wiki-article.test.tsx
```

Expected: all detail, selection, focus, and search behavior tests pass.

- [x] **Step 6: Commit the modal simplification**

```bash
git add app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx app/components/wiki-search.tsx app/components/wiki-search.test.tsx
git commit -m "refactor: simplify item detail metadata"
```

---

### Task 5: Export the pilot, inspect artifacts, and deliver

**Files:**
- Modify: `public/data/wiki/pages/210449.json`
- Verify: `public/data/items.json`
- Modify: `docs/superpowers/plans/2026-07-16-nightmare-fuel-wiki-sections.md` only to check completed steps.

**Interfaces:**
- Consumes: the completed parser, exporter, frontend contract, and UI.
- Produces: verified generated pilot data and final master commit state.

- [x] **Step 1: Run the deterministic export**

```bash
python3 -m tools.extract.cli export
```

Expected: exit 0 and only deterministic generated changes.

- [x] **Step 2: Inspect the exact pilot artifact**

```bash
jq '{pageId, normalized, hasDropHtml: (.html | contains("Drop_table")), hasUsageHtml: (.html | contains("id=\"Usage\""))}' public/data/wiki/pages/210449.json
```

Expected: `pageId` is 210449, Drop rows are 10, Usage recipes are 30, and both HTML flags are false.

- [x] **Step 3: Run all automated verification**

```bash
python3 -m unittest discover -s tests -v
npm test
npm run lint
python3 -m tools.extract.cli validate
npm run build
```

Expected: 156 or more Python tests pass, all Vitest suites pass, lint exits 0,
validation reports `hard_failures=0`, and the static production build succeeds.

- [x] **Step 4: Audit visible copy and duplication**

```bash
rg -n 'Thông tin kỹ thuật|Trang liên quan|id="Drop_table"|id="Usage"|—|–' app public/data/wiki/pages/210449.json
```

Expected: obsolete modal headings and duplicated article section IDs have no
visible matches. Wiki source prose may contain dash characters inside imported
content; authored UI copy must contain none.

- [x] **Step 5: Verify desktop and mobile behavior in a browser**

At desktop and 390 px mobile width:

- search for `Nhiên liệu Ác Mộng`;
- open the item detail;
- confirm Drop table shows 10 rows;
- confirm Usage shows 30 recipes and DLC subgroups;
- activate one mapped Usage result and confirm the modal switches item;
- confirm the remaining article has no duplicate Drop table or Usage;
- confirm no page-level horizontal overflow and no console errors.

- [x] **Step 6: Complete the plan and review staged scope**

```bash
git diff --check
git status --short
```

Expected: `.yarnrc.yml` remains untracked and excluded. Only source, tests,
generated page `210449`, and this plan are staged.

- [x] **Step 7: Commit delivery state**

```bash
git add public/data/wiki/pages/210449.json docs/superpowers/plans/2026-07-16-nightmare-fuel-wiki-sections.md
git commit -m "data: publish nightmare fuel wiki sections"
```

Expected: the final pilot artifact and completed plan state are committed on `master`.
