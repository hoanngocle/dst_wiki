# Item Detail Progressive Sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Present every currently available item field in a structured detail card that is ready to grow into the complete game-wiki layout.

**Architecture:** Keep `ItemListEntry` and the extracted payload unchanged. `ItemDetailModal` owns the presentation-only metadata mapping and renders discrete sections only when their underlying field is present. `RecipeIngredients` remains the sole renderer of recipe ingredients.

**Tech Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS 4, Vitest, Testing Library.

## Global Constraints

- Do not change the item payload, extractor, or `ItemListEntry` schema.
- Do not display invented values or empty data panels.
- Preserve the existing dialog accessibility, close behavior, focus trap, focus restoration, and scroll lock.
- Preserve the existing item-name-only dialog heading.

---

## File structure

- Modify `app/components/item-detail-modal.tsx`: map the current category and namespace data to labelled detail rows; replace the sparse body with consistent, conditional panels.
- Modify `app/components/item-detail-modal.test.tsx`: specify the displayed metadata and absence of empty sections.

### Task 1: Define the item-detail behavior with component tests

**Files:**

- Modify: `app/components/item-detail-modal.test.tsx:7-98`
- Modify: `app/components/item-detail-modal.tsx:17-150`

**Interfaces:**

- Consumes: `ItemListEntry` with `namespace`, `category`, `description`, `prefabId`, and nullable `recipe`.
- Produces: `ItemDetailModal({ item, onClose })`, a labelled dialog with optional Description and Crafting panels and always-visible Object Info, Source, and Miscellaneous panels.

- [x] **Step 1: Write the failing test**

  Add the assertions below to the existing first test, and add the second test.

  ```tsx
  expect(screen.getByRole("heading", { name: "Object Info" })).toBeDefined();
  expect(screen.getByText("Loại")).toBeDefined();
  expect(screen.getByText("Item")).toBeDefined();
  expect(screen.getByRole("heading", { name: "Source" })).toBeDefined();
  expect(screen.getByText("DST gốc liên quan")).toBeDefined();
  expect(screen.getByRole("heading", { name: "Crafting" })).toBeDefined();
  expect(screen.getByText("Số lượng tạo ra")).toBeDefined();
  expect(screen.getByText("1")).toBeDefined();
  expect(screen.getByRole("heading", { name: "Description" })).toBeDefined();
  expect(screen.getByRole("heading", { name: "Miscellaneous" })).toBeDefined();
  expect(screen.getByText("Prefab ID")).toBeDefined();

  it("omits optional empty panels", () => {
    render(
      <ItemDetailModal
        item={{ ...item, description: null, recipe: null }}
        onClose={vi.fn()}
      />,
    );

    expect(screen.queryByRole("heading", { name: "Description" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Crafting" })).toBeNull();
    expect(screen.getByRole("heading", { name: "Object Info" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Source" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Miscellaneous" })).toBeDefined();
  });
  ```

- [x] **Step 2: Run the focused test to verify it fails**

  Run: `npm test -- app/components/item-detail-modal.test.tsx`

  Expected: FAIL because the Object Info, Source, Crafting, Description, and Miscellaneous section headings do not yet exist.

- [x] **Step 3: Implement the minimal sectioned modal body**

  In `app/components/item-detail-modal.tsx`, add the category labels beside `FOCUSABLE_SELECTOR`:

  ```tsx
  const categoryLabel = {
    item: "Item",
    mob: "Mob",
    boss: "Boss",
    character: "Nhân vật",
    structure: "Công trình",
    effect: "Hiệu ứng",
    other: "Khác",
  } as const;
  ```

  Compute `const category = categoryLabel[item.category];` inside the component. Replace the body below the modal header with a `space-y-4` panel stack. Use `section` elements and `h3` headings for `Object Info`, `Source`, and `Miscellaneous`; render one `dl` row in each: `Loại`/`category`, `Nội dung`/`sourceLabel`, and `Prefab ID`/`item.prefabId`. Render `Description` only when `item.description` is truthy. Render `Crafting` only when `item.recipe` is truthy; include a `Số lượng tạo ra`/`item.recipe.outputCount` definition row above `<RecipeIngredients recipe={item.recipe} />`. Apply the existing cool gray/blue palette and use a two-column definition-list grid from the `sm` breakpoint. Keep all existing event handlers and refs unchanged.

- [x] **Step 4: Run the focused test to verify it passes**

  Run: `npm test -- app/components/item-detail-modal.test.tsx`

  Expected: PASS with all modal tests green.

- [x] **Step 5: Run full verification**

  Run: `npm run lint && npm test && npm run build`

  Expected: all commands exit with code 0.

- [ ] **Step 6: Commit the implementation**

  ```bash
  git add app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx
  git commit -m "feat: structure item detail metadata"
  ```
