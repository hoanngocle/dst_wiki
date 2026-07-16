# Wiki Item Catalog List Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish the current imported wiki dataset to the frontend and replace the Prefab-oriented list with a source-aware item catalog that lazily renders full local wiki articles.

**Architecture:** SQLite remains the extraction source of truth and `tools.extract.cli export` publishes static frontend contracts. The Server Component parses the compact item JSON once, while one focused Client Component owns search and filters. Per-page wiki JSON stays outside the initial React payload and is fetched only inside the selected item modal.

**Tech Stack:** Python 3 extraction pipeline, SQLite, Next.js 16.2 App Router, React 19.2, TypeScript 5, Tailwind CSS 4, Phosphor Icons, Vitest, Testing Library.

## Global Constraints

- Work directly on `master` as explicitly approved by the user.
- Keep `public/data/items.json` at schema version 4.
- Do not access the 843 MB SQLite database from browser or Next.js runtime code.
- Preserve `/`, Control K, Command K, Escape, clear, focus restoration, modal focus trap, backdrop close, and 40-result batching.
- Do not change routes, primary navigation labels, crawler behavior, or mapping heuristics.
- Do not add dependencies, fabricated translations, placeholder source facts, or decorative animation.
- Keep the existing light theme, cool neutral palette, blue accent, Geist type, Phosphor icons, and 12 to 16 px radius system.
- Hide synthetic `wiki-*` Prefab identifiers from standalone wiki items.
- Fetch full article JSON only after a wiki-backed item is selected.

---

### Task 1: Republish the current database snapshot

**Files:**
- Modify: `public/data/items.json`
- Modify: `public/data/wiki/pages/*.json`
- Modify: `public/assets/wiki/*`
- Modify: `data/generated/item-textures.json`

**Interfaces:**
- Consumes: `data/generated/wiki.sqlite`, `public/data/catalog.json`, `public/data/assets.json`, and `data/crawled/dontstarve-items`.
- Produces: schema-versioned compact items, local wiki article JSON, wiki images, and texture metadata consumed by later tasks.

- [x] **Step 1: Run the deterministic export**

```bash
python3 -m tools.extract.cli export
```

Expected: exit 0 and output naming `public/data/catalog.json`, `public/data/assets.json`, `public/data/items.json`, and `data/generated/item-textures.json`.

- [x] **Step 2: Verify the published contract is internally populated**

```bash
node - <<'NODE'
const payload = require('./public/data/items.json');
const items = payload.items;
const counts = {
  total: items.length,
  wiki: items.filter((item) => item.wiki).length,
  recipes: items.filter((item) => item.recipe).length,
  pictured: items.filter((item) => item.sprite).length,
};
if (payload.schema_version !== 4) throw new Error('unexpected schema');
if (!counts.total || !counts.wiki || !counts.recipes || !counts.pictured) {
  throw new Error(`empty published segment: ${JSON.stringify(counts)}`);
}
console.log(counts);
NODE
```

Expected: schema validation succeeds and every count is greater than zero.

- [x] **Step 3: Run extraction regression tests**

```bash
python3 -m unittest discover -s tests -v
```

Expected: all extraction and crawler tests pass.

---

### Task 2: Add source, availability, and summary semantics

**Files:**
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/wiki-search.ts`
- Modify: `app/lib/wiki-search.test.ts`

**Interfaces:**
- Consumes: validated `ItemListEntry` records.
- Produces: `ItemSourceFilter`, `ItemAvailabilityFilter`, `CatalogSummary`, `summarizeItems(items)`, `hasRealPrefab(item)`, and the expanded `filterItems(items, query, source, category, availability)` contract.

- [x] **Step 1: Write failing source, availability, summary, and identifier tests**

Add fixtures for a Tu Tien item, a plain DST entity, a mapped wiki entity, and an unmatched standalone wiki item. Add assertions equivalent to:

```typescript
expect(filterItems(items, "", "wiki", "all", "all").map((item) => item.id)).toEqual([
  "base_game:goldnugget",
  "wiki:100736",
]);
expect(filterItems(items, "", "all", "all", "recipe")).toEqual([craftable]);
expect(filterItems(items, "", "all", "all", "image")).toEqual([pictured]);
expect(summarizeItems(items)).toEqual({
  total: 4,
  wiki: 2,
  recipes: 1,
  pictured: 1,
});
expect(hasRealPrefab(mappedWiki)).toBe(true);
expect(hasRealPrefab(standaloneWiki)).toBe(false);
```

- [x] **Step 2: Run the focused library test and confirm RED**

```bash
npm test -- app/lib/wiki-search.test.ts
```

Expected: fail because the new types, helpers, and five-argument filter contract do not exist.

- [x] **Step 3: Implement the minimal semantics**

Add these public types to `app/lib/item-catalog.ts`:

```typescript
export type ItemSourceFilter = "all" | "wiki" | ItemNamespace;
export type ItemAvailabilityFilter = "all" | "recipe" | "image";
export type CatalogSummary = {
  total: number;
  wiki: number;
  recipes: number;
  pictured: number;
};
```

Implement source matching as mutually exclusive user-facing provenance:

```typescript
function matchesSource(item: ItemListEntry, source: ItemSourceFilter): boolean {
  if (source === "all") return true;
  if (source === "wiki") return item.wiki !== null;
  if (source === "tu_tien") return item.namespace === "tu_tien";
  return item.namespace === "base_game" && item.wiki === null;
}

export function hasRealPrefab(item: ItemListEntry): boolean {
  return item.wiki?.mappingState !== "unmatched";
}

export function summarizeItems(items: readonly ItemListEntry[]): CatalogSummary {
  return items.reduce<CatalogSummary>(
    (summary, item) => ({
      total: summary.total + 1,
      wiki: summary.wiki + Number(item.wiki !== null),
      recipes: summary.recipes + Number(item.recipe !== null),
      pictured: summary.pictured + Number(item.sprite !== null),
    }),
    { total: 0, wiki: 0, recipes: 0, pictured: 0 },
  );
}
```

Extend `filterItems` with source, category, and availability AND semantics while preserving the current normalized search text.

- [x] **Step 4: Run the focused test and confirm GREEN**

```bash
npm test -- app/lib/wiki-search.test.ts
```

Expected: all `wiki-search` library tests pass.

---

### Task 3: Replace Prefab list copy and controls with the item catalog UI

**Files:**
- Modify: `app/page.tsx`
- Modify: `app/page.test.tsx`
- Modify: `app/loading.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/components/item-result.tsx`
- Modify: `app/components/item-result.test.tsx`
- Modify: `app/globals.css`

**Interfaces:**
- Consumes: Task 2 filter types, summary helper, real-Prefab predicate, and item list.
- Produces: item-focused page heading, derived summary metrics, three filter groups, source-aware cards, and item-focused result statuses.

- [x] **Step 1: Write failing page and search tests for the new information architecture**

Update page assertions and add component assertions equivalent to:

```typescript
expect(screen.getByRole("heading", { level: 1, name: "Danh mục vật phẩm" })).toBeDefined();
expect(screen.getByRole("searchbox", { name: "Tìm kiếm vật phẩm." })).toBeDefined();
expect(screen.getByText(`${items.length} vật phẩm`)).toBeDefined();
expect(screen.getByRole("group", { name: "Lọc theo nguồn" })).toBeDefined();
expect(screen.getByRole("group", { name: "Lọc theo dữ liệu" })).toBeDefined();
fireEvent.click(screen.getByRole("button", { name: "Wiki" }));
expect(screen.getByText("Halberd")).toBeDefined();
fireEvent.click(screen.getByRole("button", { name: "Có công thức" }));
expect(screen.queryByText("Halberd")).toBeNull();
```

Update batching and shortcut tests to query the new accessible search label.

- [x] **Step 2: Write failing card tests for mapped and standalone wiki entries**

```typescript
render(<ItemResult item={standaloneWiki} query="" onSelectItem={vi.fn()} />);
expect(screen.getByText("Wiki item")).toBeDefined();
expect(screen.queryByText("wiki-100736")).toBeNull();

render(<ItemResult item={mappedWiki} query="" onSelectItem={vi.fn()} />);
expect(screen.getByText("Wiki")).toBeDefined();
expect(screen.getByText("goldnugget")).toBeDefined();
```

- [x] **Step 3: Run focused component tests and confirm RED**

```bash
npm test -- app/page.test.tsx app/components/wiki-search.test.tsx app/components/item-result.test.tsx
```

Expected: fail on the old Prefab copy, missing controls, missing summary, and synthetic identifier leakage.

- [x] **Step 4: Implement the item page heading and summary**

Keep `app/page.tsx` as a Server Component. Use `summarizeItems(items)` and render `Danh mục vật phẩm`, concise explanatory copy, and three real summary values: total items, Wiki entries, and recipes.

- [x] **Step 5: Implement consolidated search controls**

In `WikiSearch`, replace `filter` with `source` and add `availability` state. Define these exact options:

```typescript
const sourceFilters = [
  { value: "all", label: "Tất cả" },
  { value: "wiki", label: "Wiki" },
  { value: "base_game", label: "DST" },
  { value: "tu_tien", label: "Tu Tiên" },
] as const;

const availabilityFilters = [
  { value: "all", label: "Tất cả dữ liệu" },
  { value: "recipe", label: "Có công thức" },
  { value: "image", label: "Có ảnh" },
] as const;
```

Keep each control at least 44 px tall, reset batching on every change, update empty-state reset, and change result/status copy from Prefab to `vật phẩm`.

- [x] **Step 6: Implement source-aware dense cards**

Use `item.wiki ? "Wiki" : item.namespace === "tu_tien" ? "Tu Tiên" : "DST"` for the source badge. Render the real Prefab ID only when `hasRealPrefab(item)` is true; otherwise render `Wiki item`. Preserve the image, two-line description, recipe ingredient navigation, highlight behavior, and click target. Add `content-visibility: auto` through a reusable `.catalog-card` class in `app/globals.css` with a stable intrinsic fallback size.

- [x] **Step 7: Update the loading shell and confirm GREEN**

Use `Đang tải danh mục vật phẩm` in the live loading status and keep four shape-matched card skeletons.

```bash
npm test -- app/page.test.tsx app/components/wiki-search.test.tsx app/components/item-result.test.tsx
```

Expected: all focused page, search, and result tests pass.

---

### Task 4: Load and render local wiki article details on demand

**Files:**
- Create: `app/lib/wiki-detail.ts`
- Create: `app/lib/wiki-detail.test.ts`
- Create: `app/components/wiki-article.tsx`
- Create: `app/components/wiki-article.test.tsx`
- Modify: `app/components/item-detail-modal.tsx`
- Modify: `app/components/item-detail-modal.test.tsx`
- Modify: `app/globals.css`

**Interfaces:**
- Consumes: `item.wiki.detailUrl`, exported wiki page schema version 1, compact recipe metadata, and canonical URL.
- Produces: `WikiPageDetail`, `parseWikiPageDetail(value)`, a lazy `WikiArticle` state machine, styled sanitized article HTML, related links, and canonical fallback.

- [x] **Step 1: Write the failing wiki detail parser test**

```typescript
expect(
  parseWikiPageDetail({
    schema_version: 1,
    pageId: 100736,
    title: "Halberd",
    canonicalUrl: "https://dontstarve.wiki.gg/wiki/Halberd",
    html: "<p>Pointy and hurty.</p>",
    categories: ["Items"],
    images: [],
    recipes: [],
    revision: { id: 1, sha1: "abc", timestamp: "2026-07-12T00:00:00Z" },
  }),
).toMatchObject({ pageId: 100736, title: "Halberd" });
expect(() => parseWikiPageDetail({ schema_version: 2 })).toThrow();
```

- [x] **Step 2: Run the parser test and confirm RED**

```bash
npm test -- app/lib/wiki-detail.test.ts
```

Expected: fail because the module does not exist.

- [x] **Step 3: Implement the strict compact article parser**

Define a `WikiPageDetail` containing `pageId`, `title`, `canonicalUrl`, `html`, `categories`, `images`, and `revision`. Validate schema version 1, positive numeric page ID, non-empty strings, arrays, and revision object. Preserve only fields rendered by the UI.

- [x] **Step 4: Run the parser test and confirm GREEN**

```bash
npm test -- app/lib/wiki-detail.test.ts
```

Expected: parser tests pass.

- [x] **Step 5: Write failing article loading tests**

Mock `fetch` and assert all three states:

```typescript
expect(screen.getByRole("status").textContent).toContain("Đang tải bài viết Wiki");
expect(await screen.findByText("Pointy and hurty.")).toBeDefined();
expect(screen.getByRole("link", { name: "Mở trên Don't Starve Wiki" })).toHaveProperty(
  "href",
  "https://dontstarve.wiki.gg/wiki/Halberd",
);
```

For a rejected fetch, assert `Không tải được bài viết Wiki`, a `Thử lại` button, and the canonical link. Clicking retry must call `fetch` again.

- [x] **Step 6: Implement `WikiArticle` and integrate the modal**

`WikiArticle` uses an `AbortController`, fetches `detailUrl`, validates JSON with `parseWikiPageDetail`, and exposes loading, success, and error states. Success renders the already sanitized export HTML with `dangerouslySetInnerHTML` inside `.wiki-article`, plus the canonical link. The modal renders it only for `item.wiki` and keeps the compact overview and recipe visible before the request resolves.

Remove the fabricated `Source / Dropped by` panel. Add a real description panel when `item.description` exists. Show a real Prefab definition row only when `hasRealPrefab(item)` is true. For standalone wiki items, show `Wiki page` and the page ID instead. Render compact related-page links when provided.

- [x] **Step 7: Style exported wiki HTML and confirm GREEN**

Add scoped `.wiki-article` rules for headings, paragraphs, links, lists, figures, responsive images, code, blockquotes, and horizontally scrollable tables. Do not style global HTML tags.

```bash
npm test -- app/lib/wiki-detail.test.ts app/components/wiki-article.test.tsx app/components/item-detail-modal.test.tsx
```

Expected: parser, article state, and modal tests all pass.

---

### Task 5: Full verification and delivery

**Files:**
- Modify: `docs/superpowers/plans/2026-07-16-wiki-item-catalog-list.md` only to check completed steps.
- Verify: every file changed by Tasks 1 through 4.

**Interfaces:**
- Consumes: completed data and UI implementation.
- Produces: verified master commit containing generated artifacts, UI code, tests, and plan state.

- [x] **Step 1: Run the complete frontend test suite**

```bash
npm test
```

Expected: every Vitest suite passes with zero failures.

- [x] **Step 2: Run ESLint**

```bash
npm run lint
```

Expected: exit 0 with no lint errors.

- [x] **Step 3: Run extraction validation**

```bash
python3 -m tools.extract.cli validate
```

Expected: exit 0 and `hard_failures=0` in the validation summary.

- [x] **Step 4: Run the production build**

```bash
npm run build
```

Expected: Next.js production compilation and static page generation complete successfully.

- [x] **Step 5: Audit generated data and visible copy**

```bash
rg -n 'Tìm kiếm Prefabs|Danh sách Prefabs|Tra cứu Prefab|wiki-[0-9]+' app
```

Expected: no obsolete visible Prefab copy and no hard-coded synthetic wiki identifier in UI code.

- [x] **Step 6: Review the exact staged scope and commit**

```bash
git diff --check
git status --short
git add app public/data public/assets/wiki data/generated/item-textures.json docs/superpowers/plans/2026-07-16-wiki-item-catalog-list.md
git commit -m "feat: present imported wiki item catalog"
```

Expected: the unrelated `.yarnrc.yml` remains untracked and excluded; the implementation commit succeeds on `master`.
