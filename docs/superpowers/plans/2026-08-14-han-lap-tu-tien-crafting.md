# Han Lập Tu Tiên Crafting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Characters area with a verified catalog of Tu Tiên items Hàn Lập can create, remove `/characters`, and make every recipe ingredient open the shared item-detail modal—including in the restored cultivation guide.

**Architecture:** Keep filtering and catalog validation in Server Component code so the full raw catalog never ships to the browser. A pure selector combines `items.json` recipes with `catalog.json` builder restrictions, admits public/`player`/`xd_hantianzun` recipes, and rejects entries without a resolved recipe or verified use. Reuse `WikiSearch`, `RecipeIngredients`, and `ItemDetailPeek`; extend them only to accept a separate full reference catalog so filtered results can still navigate to ingredient details.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, Vitest, Testing Library.

---

## Task 1: Build the verified Hàn Lập craftability selector

**Files:**

- Create: `app/lib/tu-tien-crafting.ts`
- Create: `app/lib/tu-tien-crafting.test.ts`

- [ ] **Step 1: Write failing selector tests**

Cover these independent rules with compact fixtures:

1. Include a public recipe (`builder_tags: []`).
2. Include recipes tagged only `player` or `xd_hantianzun`.
3. Include a verified manual/alchemy recipe that exists in `items.json` but has no runtime recipe entry in `catalog.json`.
4. Exclude recipes tagged to another character.
5. Exclude an item with no recipe, no verified use, or an unresolved ingredient.
6. Return a stable exclusion reason for audit/debugging.

Expected public contract:

```ts
export type CraftingExclusionReason =
  | "no_recipe"
  | "other_character"
  | "no_verified_use"
  | "unresolved_ingredient";

export type HanLapCraftingSelection = {
  items: readonly ItemListEntry[];
  excluded: readonly {
    id: string;
    reason: CraftingExclusionReason;
  }[];
};

export function selectHanLapCraftables(
  items: readonly ItemListEntry[],
  catalogPayload: unknown,
): HanLapCraftingSelection;
```

- [ ] **Step 2: Run the focused test and confirm RED**

Run: `npm test -- app/lib/tu-tien-crafting.test.ts`

Expected: FAIL because the selector module does not exist.

- [ ] **Step 3: Implement the minimum pure selector**

Implementation rules:

```ts
const HAN_LAP_BUILDER_TAGS = new Set(["player", "xd_hantianzun"]);
```

- Only consider `namespace === "tu_tien"`.
- Require `item.recipe` and require every ingredient ID to resolve in the full `items` list.
- If runtime recipes exist for the item, accept when at least one recipe has no builder tags or every tag belongs to `HAN_LAP_BUILDER_TAGS`.
- If no runtime recipe exists, treat the item recipe as a verified manual/alchemy creation path.
- Verify use when `details.usage.status === "known"`, `structureDetails.functions.status === "known"`, the item has documented mob mechanics, or the item is referenced as an ingredient by another resolved recipe.
- Sort deterministically by category and Vietnamese name.
- Record one exclusion reason per rejected Tu Tiên item without inventing recipe data.

- [ ] **Step 4: Run the focused test and confirm GREEN**

Run: `npm test -- app/lib/tu-tien-crafting.test.ts`

Expected: PASS.

- [ ] **Step 5: Commit the selector**

```bash
git add app/lib/tu-tien-crafting.ts app/lib/tu-tien-crafting.test.ts
git commit -m "feat: select verified Han Lap craftables"
```

## Task 2: Let filtered catalogs resolve every recipe ingredient

**Files:**

- Modify: `app/components/wiki-search.tsx`
- Modify: `app/components/wiki-search.test.tsx`
- Modify: `app/components/item-detail-peek.tsx`
- Modify: `app/components/item-detail-peek.test.tsx`

- [ ] **Step 1: Write failing interaction tests**

Add a `WikiSearch` test that renders one visible result but passes a larger `referenceItems` array. Clicking an ingredient absent from visible results must open that ingredient in the shared dialog.

Add a test for `hideSourceFilters` so the Tu Tiên crafting page can omit the redundant source filter while retaining category/availability filtering.

Add a modal test where a base-game item opened in `ItemDetailPeek` has its own recipe; clicking that nested ingredient must replace the current dialog detail.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `npm test -- app/components/wiki-search.test.tsx app/components/item-detail-peek.test.tsx`

Expected: FAIL because `WikiSearch` has no `referenceItems`/`hideSourceFilters` props and base-game modal recipes do not receive navigation callbacks.

- [ ] **Step 3: Extend `WikiSearch` without changing default behavior**

Use this serializable prop contract:

```ts
type WikiSearchProps = {
  items: readonly ItemListEntry[];
  referenceItems?: readonly ItemListEntry[];
  hideSourceFilters?: boolean;
};
```

- Default `referenceItems` to `items`.
- Build `itemsById` from `referenceItems`, not visible results.
- Omit only the source filter group when `hideSourceFilters` is true.
- Keep existing `/` behavior unchanged.

- [ ] **Step 4: Propagate modal navigation inside base-game recipe details**

Update the internal base-game crafting section in `ItemDetailPeek` to accept `itemsById` and `onSelectItem`, then pass both to `RecipeIngredients`. Tu Tiên, mob, and structure branches already use the shared reference map.

- [ ] **Step 5: Run focused tests and confirm GREEN**

Run: `npm test -- app/components/wiki-search.test.tsx app/components/item-detail-peek.test.tsx app/components/recipe-ingredients.test.tsx`

Expected: PASS.

- [ ] **Step 6: Commit shared modal navigation**

```bash
git add app/components/wiki-search.tsx app/components/wiki-search.test.tsx app/components/item-detail-peek.tsx app/components/item-detail-peek.test.tsx
git commit -m "feat: open recipe ingredients in shared detail modal"
```

## Task 3: Replace Characters with the Hàn Lập crafting page

**Files:**

- Create: `app/tu-tien-crafting/page.tsx`
- Create: `app/tu-tien-crafting/page.test.tsx`
- Modify: `app/components/site-header.tsx`
- Modify: `app/components/site-header.test.tsx`
- Delete: `app/characters/page.tsx`
- Delete: `app/lib/character-catalog.ts`
- Delete: `app/lib/character-catalog.test.ts`

- [ ] **Step 1: Write failing page and header tests**

Assert that:

- The new page heading is `Đồ chế Tu Tiên của Hàn Lập`.
- It renders `WikiSearch` with verified results and the full item list as references.
- A Hàn Lập recipe is included and a different-character recipe is excluded.
- The header links are `Vật phẩm`, `Chế tạo Tu Tiên`, `Cảnh giới Tu Tiên` in that order.
- No `Nhân vật` link remains.
- The source filter is hidden on the new page.

- [ ] **Step 2: Run focused tests and confirm RED**

Run: `npm test -- app/tu-tien-crafting/page.test.tsx app/components/site-header.test.tsx`

Expected: FAIL because the route and new nav section do not exist.

- [ ] **Step 3: Implement the Server Component page**

In `app/tu-tien-crafting/page.tsx`:

```tsx
const allItems = parseItemPayload(itemsPayload);
const selection = selectHanLapCraftables(allItems, catalogPayload);

<WikiSearch
  items={selection.items}
  referenceItems={allItems}
  hideSourceFilters
/>
```

Add a concise hero explaining that only items with a verified creation path and verified use are listed. Show the verified total, but do not expose excluded or speculative entries in the UI.

- [ ] **Step 4: Update global navigation and remove Characters**

Change the nav type to:

```ts
type SiteSection = "items" | "tu-tien-crafting" | "tu-tien";
```

Point `Chế tạo Tu Tiên` to `/tu-tien-crafting`. Delete the Characters route and its route-only selector/tests. Do not add a redirect; `/characters` must naturally return 404.

- [ ] **Step 5: Run focused tests and confirm GREEN**

Run: `npm test -- app/tu-tien-crafting/page.test.tsx app/components/site-header.test.tsx app/lib/tu-tien-crafting.test.ts`

Expected: PASS.

- [ ] **Step 6: Commit the route replacement**

```bash
git add app/tu-tien-crafting app/components/site-header.tsx app/components/site-header.test.tsx app/characters/page.tsx app/lib/character-catalog.ts app/lib/character-catalog.test.ts
git commit -m "feat: replace characters with Han Lap crafting catalog"
```

## Task 4: Restore Cảnh giới Tu Tiên with clickable ingredients

**Files:**

- Create: `app/lib/cultivation-guide.ts`
- Create: `app/lib/cultivation-guide.test.ts`
- Create: `app/components/cultivation-browser.tsx`
- Create: `app/components/cultivation-browser.test.tsx`
- Create: `app/tu-tien/page.tsx`
- Create: `app/tu-tien/page.test.tsx`

- [ ] **Step 1: Write failing cultivation data tests**

Restore the 15-stage Hàn Lập progression contract and assert every stage resolves to an existing pill with a recipe whose ingredients all resolve in the full catalog. Do not synthesize missing recipes in the guide.

- [ ] **Step 2: Run the data test and confirm RED**

Run: `npm test -- app/lib/cultivation-guide.test.ts`

Expected: FAIL because the guide module is absent.

- [ ] **Step 3: Implement the cultivation guide data layer**

Define the 15 stages and their pill IDs (`jq`, `dt`, `zj`, `xs`, `hj`, `yz`, `sm`, `rl`, `jy`, `yx`, `ns`, `hs`, `hy`, `hl`, `kx`). Resolve them strictly from `ItemListEntry[]`; throw a clear error during build/tests if a stage, recipe, or ingredient is missing.

- [ ] **Step 4: Write failing cultivation interaction tests**

Test `CultivationBrowser` with a small fixture. Clicking a recipe ingredient button must open `ItemDetailPeek` for that ingredient. Also assert stage/pill content remains visible and accessible.

- [ ] **Step 5: Run the component test and confirm RED**

Run: `npm test -- app/components/cultivation-browser.test.tsx`

Expected: FAIL because the client component is absent.

- [ ] **Step 6: Implement the client interaction boundary**

`CultivationBrowser` must:

- Receive serializable `stages` and `referenceItems` arrays.
- Build `itemsById` with `useMemo` inside the client.
- Own `selectedItem` state.
- Render each recipe with the existing `RecipeIngredients` component.
- Pass the complete reference map and selection callback so every resolved ingredient is a button.
- Render one shared `ItemDetailPeek`; nested ingredient clicks replace its current content.

- [ ] **Step 7: Implement the restored Server Component route**

`app/tu-tien/page.tsx` parses the full item payload, builds the 15 stages, renders `SiteHeader active="tu-tien"`, a compact page introduction, and `CultivationBrowser`.

- [ ] **Step 8: Run focused tests and confirm GREEN**

Run: `npm test -- app/lib/cultivation-guide.test.ts app/components/cultivation-browser.test.tsx app/tu-tien/page.test.tsx`

Expected: PASS.

- [ ] **Step 9: Commit the restored cultivation guide**

```bash
git add app/lib/cultivation-guide.ts app/lib/cultivation-guide.test.ts app/components/cultivation-browser.tsx app/components/cultivation-browser.test.tsx app/tu-tien/page.tsx app/tu-tien/page.test.tsx
git commit -m "feat: restore interactive cultivation guide"
```

## Task 5: Full verification and cleanup

**Files:**

- Modify only files required by verification findings.

- [ ] **Step 1: Run the complete test suite**

Run: `npm test`

Expected: all tests pass.

- [ ] **Step 2: Run lint**

Run: `npm run lint`

Expected: no errors.

- [ ] **Step 3: Run a production build**

Run: `npm run build`

Expected: build succeeds; `/tu-tien-crafting` and `/tu-tien` are emitted while `/characters` is absent.

- [ ] **Step 4: Inspect the final diff and route inventory**

Run:

```bash
git status --short
git diff --check
find app -maxdepth 2 -name page.tsx -print | sort
```

Confirm unrelated user files remain untouched and untracked, especially the Achievement & Level plan/module notes.

- [ ] **Step 5: Request code review and address only verified findings**

Use the project’s code-review skill. Re-run affected focused tests after any correction.

- [ ] **Step 6: Final verification commit if needed**

```bash
git add <only files changed by verified fixes>
git commit -m "fix: address Han Lap crafting review findings"
```
