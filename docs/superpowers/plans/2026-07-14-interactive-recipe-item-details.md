# Interactive Recipe Item Details Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the redundant item-type icon and let users identify and inspect recipe ingredients through accessible tooltips and a full-data modal.

**Architecture:** `WikiSearch` memoizes the complete item catalog by ID, owns the selected `ItemListEntry`, and renders one modal. It passes the lookup map and a full-item selection callback through `ItemResult` to `RecipeIngredients`; the modal receives the selected object directly and never looks up data.

**Tech Stack:** Next.js 16.2 App Router, React 19, TypeScript, Tailwind CSS 4, Phosphor Icons, Vitest, Testing Library.

## Global Constraints

- Do not change the generated item JSON schema or extraction pipeline.
- The modal must receive a full `ItemListEntry` object, not an ingredient ID.
- Unresolved ingredients remain non-interactive and never open a partial modal.
- Preserve all existing search, filter, batching, recipe-empty-state, and missing-sprite behaviour.
- Keep `WikiSearch` as the existing Client Component boundary; imported interactive children do not need their own `"use client"` directive.

---

### Task 1: Remove the redundant item-type icon

**Files:**
- Modify: `app/components/item-result.test.tsx`
- Modify: `app/components/item-result.tsx`

**Interfaces:**
- Consumes: existing `ItemResult({ item, query })` until Task 3 expands its props.
- Produces: a two-column identity row containing the 64 px sprite and item metadata.

- [ ] **Step 1: Change the focused test to reject the removed icon**

Replace the positive type-icon assertion with:

```tsx
expect(screen.queryByLabelText("Loại: Item")).toBeNull();
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `npm test -- app/components/item-result.test.tsx`

Expected: FAIL because `Loại: Item` is still present.

- [ ] **Step 3: Remove the icon and collapse the grid**

Delete the `Package` import and its labelled `<span>`. Change the row class to:

```tsx
<div className="grid grid-cols-[64px_minmax(0,1fr)] items-center gap-3">
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `npm test -- app/components/item-result.test.tsx`

Expected: all `ItemResult` tests PASS.

- [ ] **Step 5: Commit the isolated layout change**

```bash
git add app/components/item-result.tsx app/components/item-result.test.tsx
git commit -m "fix: remove redundant item type icon"
```

### Task 2: Make recipe ingredients emit full catalog items

**Files:**
- Modify: `app/components/recipe-ingredients.test.tsx`
- Modify: `app/components/recipe-ingredients.tsx`

**Interfaces:**
- Consumes: `recipe: ItemRecipe | null`, optional `itemsById: ReadonlyMap<string, ItemListEntry>`, optional `onSelectItem: (item: ItemListEntry) => void`.
- Produces: accessible ingredient buttons for resolved items and unchanged static chips for unresolved items.

- [ ] **Step 1: Add failing interaction and fallback tests**

Define a full referenced item and assert the exact object is emitted:

```tsx
const fullItem: ItemListEntry = {
  id: "base_game:goldnugget",
  prefabId: "goldnugget",
  namespace: "base_game",
  name: "Vàng",
  englishName: "Gold Nugget",
  description: "Một cục vàng.",
  sprite: null,
  recipe: null,
};
const onSelectItem = vi.fn();

render(
  <RecipeIngredients
    recipe={recipe}
    itemsById={new Map([[fullItem.id, fullItem]])}
    onSelectItem={onSelectItem}
  />,
);

const ingredient = screen.getByRole("button", { name: "Vàng, số lượng 2" });
const tooltip = screen.getByRole("tooltip", { name: "Vàng" });
expect(ingredient.getAttribute("aria-describedby")).toBe(tooltip.id);
fireEvent.click(ingredient);
expect(onSelectItem).toHaveBeenCalledWith(fullItem);
```

Also render with an empty map and assert there is no ingredient button while the labelled static chip remains.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `npm test -- app/components/recipe-ingredients.test.tsx`

Expected: FAIL because the new props and ingredient button do not exist.

- [ ] **Step 3: Implement resolved buttons and tooltips**

Use this prop contract:

```tsx
type RecipeIngredientsProps = {
  recipe: ItemRecipe | null;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
};
```

Create one `useId()` prefix per rendered recipe. For each ingredient, resolve `itemsById?.get(ingredient.id)`. When both the full item and callback exist, render a `type="button"` control whose click calls `onSelectItem(fullItem)`, whose accessible label includes the quantity, and whose tooltip is connected using a unique `aria-describedby`. Use `group-hover` and `group-focus-visible` classes to reveal the tooltip. Otherwise keep the current `<span title={ingredient.name}>` fallback.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `npm test -- app/components/recipe-ingredients.test.tsx`

Expected: all `RecipeIngredients` tests PASS.

- [ ] **Step 5: Commit the ingredient interaction**

```bash
git add app/components/recipe-ingredients.tsx app/components/recipe-ingredients.test.tsx
git commit -m "feat: make recipe ingredients selectable"
```

### Task 3: Add the full-data item detail modal

**Files:**
- Create: `app/components/item-detail-modal.tsx`
- Create: `app/components/item-detail-modal.test.tsx`

**Interfaces:**
- Consumes: `item: ItemListEntry`, `onClose: () => void`.
- Produces: `ItemDetailModal` with no catalog lookup dependency.

- [ ] **Step 1: Write failing modal behaviour tests**

Render a complete item and assert:

```tsx
expect(screen.getByRole("dialog", { name: "Chi tiết Vàng" })).toBeDefined();
expect(screen.getByText("Gold Nugget")).toBeDefined();
expect(screen.getByText("goldnugget")).toBeDefined();
expect(screen.getByText("Một cục vàng.")).toBeDefined();
expect(document.activeElement).toBe(screen.getByRole("button", { name: "Đóng chi tiết" }));
```

Add separate assertions that the close button, Escape, and backdrop each call `onClose`; Tab from the last focusable control wraps to the close button; Shift+Tab from the close button wraps to the last control; and unmount restores the element focused before the modal opened.

- [ ] **Step 2: Run the modal test and verify RED**

Run: `npm test -- app/components/item-detail-modal.test.tsx`

Expected: FAIL because `ItemDetailModal` does not exist.

- [ ] **Step 3: Implement modal presentation and focus lifecycle**

Export this contract:

```tsx
export function ItemDetailModal({
  item,
  onClose,
}: {
  item: ItemListEntry;
  onClose: () => void;
})
```

Render a fixed backdrop and a labelled `role="dialog"` panel. Show `GameSprite`, names, source label, prefab, description fallback, and display-only `RecipeIngredients`. In an effect, capture the previously focused element, focus the close button, listen for Escape and Tab/Shift+Tab, lock `document.body.style.overflow`, and restore both body overflow and previous focus during cleanup. Backdrop dismissal must only run when `event.target === event.currentTarget`.

- [ ] **Step 4: Run the modal test and verify GREEN**

Run: `npm test -- app/components/item-detail-modal.test.tsx`

Expected: all `ItemDetailModal` tests PASS.

- [ ] **Step 5: Commit the modal**

```bash
git add app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx
git commit -m "feat: add accessible item detail modal"
```

### Task 4: Wire selection from the list to the shared modal

**Files:**
- Modify: `app/components/item-result.tsx`
- Modify: `app/components/item-result.test.tsx`
- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`

**Interfaces:**
- Consumes: `ItemDetailModal`, the complete `items` prop, and Task 2's recipe-selection props.
- Produces: one full-item selection flow from any resolved list-card ingredient to the shared modal.

- [ ] **Step 1: Add a failing integration test**

Make the sword recipe reference the existing full log item:

```tsx
ingredients: [
  {
    id: "base_game:log",
    name: "Gỗ",
    amount: 2,
    sprite: null,
  },
],
```

Then assert:

```tsx
const swordCard = screen.getByText("Kiếm Thử").closest("li") as HTMLElement;
const ingredient = within(swordCard).getByRole("button", {
  name: "Gỗ, số lượng 2",
});
fireEvent.click(ingredient);

const dialog = screen.getByRole("dialog", { name: "Chi tiết Gỗ" });
expect(within(dialog).getByText("Log")).toBeDefined();
expect(within(dialog).getByText("Nguyên liệu cơ bản.")).toBeDefined();

fireEvent.click(within(dialog).getByRole("button", { name: "Đóng chi tiết" }));
expect(screen.queryByRole("dialog")).toBeNull();
expect(document.activeElement).toBe(ingredient);
```

- [ ] **Step 2: Run the integration tests and verify RED**

Run: `npm test -- app/components/item-result.test.tsx app/components/wiki-search.test.tsx`

Expected: FAIL because `ItemResult` does not accept lookup/selection props and no modal is rendered.

- [ ] **Step 3: Forward full-item selection through ItemResult**

Expand the public props to:

```tsx
type ItemResultProps = {
  item: ItemListEntry;
  query: string;
  itemsById?: ReadonlyMap<string, ItemListEntry>;
  onSelectItem?: (item: ItemListEntry) => void;
};
```

Pass `itemsById` and `onSelectItem` to `RecipeIngredients`. Keep both optional so focused card tests and non-interactive uses remain simple.

- [ ] **Step 4: Own lookup and modal state in WikiSearch**

Add:

```tsx
const [selectedItem, setSelectedItem] = useState<ItemListEntry | null>(null);
const itemsById = useMemo(
  () => new Map(items.map((item) => [item.id, item] as const)),
  [items],
);
```

Pass `itemsById` and `onSelectItem={setSelectedItem}` to each `ItemResult`. After the result/empty-state branch, render:

```tsx
{selectedItem ? (
  <ItemDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
) : null}
```

- [ ] **Step 5: Run the integration tests and verify GREEN**

Run: `npm test -- app/components/item-result.test.tsx app/components/wiki-search.test.tsx`

Expected: all focused integration tests PASS.

- [ ] **Step 6: Commit the shared selection flow**

```bash
git add app/components/item-result.tsx app/components/item-result.test.tsx app/components/wiki-search.tsx app/components/wiki-search.test.tsx
git commit -m "feat: open item details from recipe ingredients"
```

### Task 5: Verify the complete increment

**Files:**
- Modify only files requiring fixes revealed by verification.

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: a regression-checked, buildable Items experience.

- [ ] **Step 1: Run the entire test suite**

Run: `npm test`

Expected: all Vitest suites PASS.

- [ ] **Step 2: Run lint**

Run: `npm run lint`

Expected: exit code 0 with no ESLint errors.

- [ ] **Step 3: Run the production build**

Run: `npm run build`

Expected: Next.js production build exits 0.

- [ ] **Step 4: Inspect the final diff**

Run: `git diff HEAD~4 --check` and `git status --short`.

Expected: no whitespace errors and only intended changes/commits are present.
