# Item Catalog Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Present a curated prefab catalog, standardize the DST label, and show English item names beneath Vietnamese names on result cards.

**Architecture:** Keep the generated JSON unchanged and curate validated `ItemListEntry` objects inside `parseItemPayload`, so every UI consumer receives the same ordered list. Keep presentation changes local to the three existing components and validate behavior through colocated Vitest/Testing Library tests plus the page integration test.

**Tech Stack:** Next.js 16.2.10 App Router, React 19.2.4, TypeScript 5, Vitest 4, React Testing Library, Tailwind CSS 4.

## Global Constraints

- Display `DST` everywhere the UI currently displays `DST gốc` or `DST gốc liên quan`.
- Display `englishName` directly below the Vietnamese result-card heading only when it is non-null.
- Remove entries whose `prefabId` ends with the exact suffix `_fx`.
- Within one namespace, prefer an exact `foo_item` counterpart only when it has a non-null sprite; otherwise retain `foo`.
- Preserve standalone entries, namespace isolation, and the original order of retained entries.
- Do not rewrite `public/data/items.json` or change category, sprite, or recipe presentation.
- Follow the bundled Next.js Vitest guidance at `node_modules/next/dist/docs/01-app/02-guides/testing/vitest.md`.

## File Structure

- Modify `app/lib/item-catalog.ts`: curate the validated item array before returning it.
- Modify `app/lib/item-catalog.test.ts`: cover `_fx` removal, exact-pair selection, fallback, ordering, and namespace isolation.
- Modify `app/page.test.tsx`: assert the curated production payload count and absence of an `_fx` result.
- Modify `app/components/item-result.tsx`: render the `DST` label and conditional English subtitle.
- Modify `app/components/item-result.test.tsx`: cover English subtitle behavior and the result-card source label.
- Modify `app/components/item-detail-modal.tsx`: render the `DST` source label.
- Modify `app/components/item-detail-modal.test.tsx`: cover the modal source label.
- Modify `app/components/wiki-search.tsx`: rename the base-game filter to `DST`.
- Modify `app/components/wiki-search.test.tsx`: cover the renamed filter.

---

### Task 1: Curate the parsed item catalog

**Files:**
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/page.test.tsx`

**Interfaces:**
- Consumes: the existing `parseItemPayload(value: unknown): readonly ItemListEntry[]` API.
- Produces: the same public signature, returning validated and curated entries in input order.

- [ ] **Step 1: Add reusable valid catalog fixtures**

Add this helper below `validPayload` in `app/lib/item-catalog.test.ts`:

```ts
function makeValidItem(
  prefabId: string,
  {
    namespace = "tu_tien",
    sprite = structuredClone(validPayload.items[0].sprite),
  }: {
    namespace?: "tu_tien" | "base_game";
    sprite?: (typeof validPayload.items)[number]["sprite"] | null;
  } = {},
) {
  return {
    ...structuredClone(validPayload.items[0]),
    id: `${namespace}:${prefabId}`,
    prefabId,
    namespace,
    sprite,
  };
}
```

- [ ] **Step 2: Write failing catalog-curation tests**

Add these tests inside `describe("parseItemPayload", ...)`:

```ts
it("removes effect-only prefabs while preserving retained order", () => {
  const payload = {
    schema_version: 3,
    items: [
      makeValidItem("first"),
      makeValidItem("spark_fx"),
      makeValidItem("last"),
    ],
  };

  expect(parseItemPayload(payload).map((item) => item.prefabId)).toEqual([
    "first",
    "last",
  ]);
});

it("prefers a pictured _item counterpart without crossing namespaces", () => {
  const payload = {
    schema_version: 3,
    items: [
      makeValidItem("gate"),
      makeValidItem("gate", { namespace: "base_game" }),
      makeValidItem("gate_item"),
      makeValidItem("standalone_item", { sprite: null }),
    ],
  };

  expect(
    parseItemPayload(payload).map((item) => `${item.namespace}:${item.prefabId}`),
  ).toEqual([
    "base_game:gate",
    "tu_tien:gate_item",
    "tu_tien:standalone_item",
  ]);
});

it("keeps the base prefab when its _item counterpart has no image", () => {
  const payload = {
    schema_version: 3,
    items: [makeValidItem("gate"), makeValidItem("gate_item", { sprite: null })],
  };

  expect(parseItemPayload(payload).map((item) => item.prefabId)).toEqual(["gate"]);
});
```

In `app/page.test.tsx`, change the production-payload assertions to:

```tsx
expect(screen.getByText("1887 Prefabs")).toBeDefined();
expect(
  screen.queryByRole("heading", { level: 3, name: "abigail_attack_fx" }),
).toBeNull();
```

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```bash
npm test -- app/lib/item-catalog.test.ts app/page.test.tsx
```

Expected: FAIL because `_fx` entries and both sides of exact base/`_item` pairs are still returned, and the page still reports `1975 Prefabs`.

- [ ] **Step 4: Implement the minimal catalog curation**

Add these private helpers above `parseItemPayload` in `app/lib/item-catalog.ts`:

```ts
function catalogKey(item: Pick<ItemListEntry, "namespace" | "prefabId">): string {
  return `${item.namespace}:${item.prefabId}`;
}

function curateItems(items: readonly ItemListEntry[]): ItemListEntry[] {
  const candidates = items.filter((item) => !item.prefabId.endsWith("_fx"));
  const itemsByKey = new Map(candidates.map((item) => [catalogKey(item), item]));

  return candidates.filter((item) => {
    if (item.prefabId.endsWith("_item")) {
      const basePrefabId = item.prefabId.slice(0, -"_item".length);
      const baseItem = itemsByKey.get(
        catalogKey({ namespace: item.namespace, prefabId: basePrefabId }),
      );
      return !baseItem || item.sprite !== null;
    }

    const itemVariant = itemsByKey.get(
      catalogKey({ namespace: item.namespace, prefabId: `${item.prefabId}_item` }),
    );
    return !itemVariant || itemVariant.sprite === null;
  });
}
```

Change the final return in `parseItemPayload` to:

```ts
return curateItems(value.items.map(parseItem));
```

- [ ] **Step 5: Run the focused tests and verify GREEN**

Run:

```bash
npm test -- app/lib/item-catalog.test.ts app/page.test.tsx
```

Expected: both test files PASS; the production fixture reports `1887 Prefabs` and no `abigail_attack_fx` card.

- [ ] **Step 6: Commit the catalog behavior**

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/page.test.tsx
git commit -m "feat: curate item catalog variants"
```

---

### Task 2: Standardize DST labels and show English card names

**Files:**
- Modify: `app/components/item-result.test.tsx`
- Modify: `app/components/item-result.tsx`
- Modify: `app/components/item-detail-modal.test.tsx`
- Modify: `app/components/item-detail-modal.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/components/wiki-search.tsx`

**Interfaces:**
- Consumes: existing `ItemResult`, `ItemDetailModal`, and `WikiSearch` props without signature changes.
- Produces: visible `DST` copy and a conditional `<p lang="en">` immediately after the Vietnamese `<h3>` in result cards.

- [ ] **Step 1: Write failing component expectations**

In `app/components/item-result.test.tsx`, replace the old base-game assertion with:

```ts
expect(screen.getByText("DST")).toBeDefined();
expect(screen.queryByText("DST gốc liên quan")).toBeNull();
```

Add this result-card test:

```tsx
it("shows an available English name below Vietnamese and omits an empty subtitle", () => {
  const { container, rerender } = render(<ItemResult item={item} query="" />);
  const vietnameseHeading = screen.getByRole("heading", { name: "Kiếm Thử" });
  const englishName = screen.getByText("Test Sword");

  expect(vietnameseHeading.nextElementSibling).toBe(englishName);
  expect(englishName.getAttribute("lang")).toBe("en");

  rerender(<ItemResult item={{ ...item, englishName: null }} query="" />);
  expect(container.querySelector('[lang="en"]')).toBeNull();
});
```

In `app/components/item-detail-modal.test.tsx`, replace the source assertion with:

```ts
expect(screen.getByText("DST")).toBeDefined();
expect(screen.queryByText("DST gốc liên quan")).toBeNull();
```

In `app/components/wiki-search.test.tsx`, change the base-game filter lookup to:

```ts
fireEvent.click(screen.getByRole("button", { name: "DST" }));
```

- [ ] **Step 2: Run the component tests and verify RED**

Run:

```bash
npm test -- app/components/item-result.test.tsx app/components/item-detail-modal.test.tsx app/components/wiki-search.test.tsx
```

Expected: FAIL because components still render the old labels and `ItemResult` does not render `englishName`.

- [ ] **Step 3: Implement the minimal UI changes**

In both `app/components/item-result.tsx` and `app/components/item-detail-modal.tsx`, set the source label to:

```ts
const sourceLabel = item.namespace === "tu_tien" ? "Tu Tiên" : "DST";
```

In `app/components/wiki-search.tsx`, change the base-game filter entry to:

```ts
{ value: "base_game", label: "DST" },
```

In `app/components/item-result.tsx`, insert this conditional directly after the Vietnamese `<h3>`:

```tsx
{item.englishName ? (
  <p lang="en" className="mt-0.5 truncate text-sm text-[#607188]">
    {item.englishName}
  </p>
) : null}
```

- [ ] **Step 4: Run the component tests and verify GREEN**

Run:

```bash
npm test -- app/components/item-result.test.tsx app/components/item-detail-modal.test.tsx app/components/wiki-search.test.tsx
```

Expected: all three test files PASS with the new copy and subtitle behavior.

- [ ] **Step 5: Commit the UI behavior**

```bash
git add app/components/item-result.tsx app/components/item-result.test.tsx app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx app/components/wiki-search.tsx app/components/wiki-search.test.tsx
git commit -m "feat: refine item result metadata"
```

---

### Task 3: Verify the complete application

**Files:**
- No source changes expected.

**Interfaces:**
- Consumes: the completed catalog and UI behavior from Tasks 1 and 2.
- Produces: fresh evidence that tests, lint, and the production build succeed together.

- [ ] **Step 1: Run the full test suite**

```bash
npm test
```

Expected: all Vitest files PASS with zero failures.

- [ ] **Step 2: Run lint**

```bash
npm run lint
```

Expected: exit code 0 with no ESLint errors.

- [ ] **Step 3: Run the production build**

```bash
npm run build
```

Expected: exit code 0 and a successful Next.js production build.

- [ ] **Step 4: Inspect the final diff and worktree state**

```bash
git diff HEAD~2 --check
git status --short
```

Expected: no whitespace errors and no uncommitted implementation files.
