# Tu Tiên Item Detail Data Design

## Goal

Every Tu Tiên item modal must consistently show three sections: **Công thức**, **Cách sử dụng**, and **Nguồn nhận**. Data must be derived from evidence in the Tu Tiên mod and the existing extraction database. When evidence is insufficient, the section remains visible with `Chưa xác định`, and the item is included in a deterministic audit report.

## Scope

- Cover every Tu Tiên inventory item selected by the existing catalog curation. The current export contains 381 such items.
- Keep base-game wiki detail behavior unchanged.
- Preserve the existing recipe rendering, sprites, navigation between catalog items, and current uncommitted workspace changes.
- Do not invent behavior from an item name, description, or visual appearance alone.

## Chosen Approach

Use a hybrid evidence pipeline:

1. Derive reliable data from normalized catalog fields already extracted from Lua/runtime evidence.
2. Reverse-index recipes so an ingredient can list every recipe that uses it.
3. Convert normalized effects into Vietnamese gameplay usage statements only when the effect shape is explicitly supported.
4. Convert acquisition facts into `dropBy` rows for drops, harvests, starting grants, and other evidenced non-crafting sources.
5. Apply a checked-in manual override file for dynamic Lua behavior that cannot be represented reliably by the generic extractor.
6. Mark unresolved sections as `unknown` and export a review report instead of guessing.

This provides deterministic regeneration while allowing careful curation of exceptional mod logic.

## Data Model

Each `ItemListEntry` gains a `details` object:

```ts
type ItemDetailStatus = "known" | "none" | "unknown";

type ItemEvidence = {
  source: string;
  locator: string | null;
};

type ItemReference = {
  id: string;
  name: string;
  sprite: SpriteDescriptor | null;
};

type ItemUsageRecipe = {
  result: ItemReference;
  resultAmount: number;
  subjectAmount: number;
  ingredients: readonly RecipeIngredient[];
  craftingNote: string | null;
};

type ItemUsageEffect = {
  trigger: string;
  text: string;
  evidence: readonly ItemEvidence[];
};

type ItemUsage = {
  status: ItemDetailStatus;
  recipes: readonly ItemUsageRecipe[];
  effects: readonly ItemUsageEffect[];
};

type ItemDropSource = {
  type: "drop" | "harvest" | "start" | "trade" | "other";
  source: ItemReference | null;
  quantity: string | null;
  chance: string | null;
  conditions: string | null;
  evidence: readonly ItemEvidence[];
};

type ItemDetails = {
  recipeStatus: ItemDetailStatus;
  usage: ItemUsage;
  dropBy: {
    status: ItemDetailStatus;
    sources: readonly ItemDropSource[];
  };
};
```

The existing top-level `recipe` remains the canonical recipe payload so current consumers do not break. `details.recipeStatus` explains whether a missing recipe is confirmed absent or still unresolved.

`known` means at least one supported record exists. `none` is used only when the evidence pipeline can positively establish that the section does not apply. `unknown` means no reliable conclusion can be reached.

## Derivation Rules

### Công thức

- Read every normalized recipe for the item, not merely infer ingredients from descriptions.
- Preserve output count and ingredient amounts.
- Preserve recipe restrictions as a Vietnamese crafting note when the source includes station, builder tag, character ingredient, or filter restrictions.
- `known` when a supported recipe exists.
- `none` only for an item whose acquisition evidence positively identifies it as non-craftable and no recipe is present.
- Otherwise use `unknown`.

### Cách sử dụng

- Reverse-index all normalized recipes. For each ingredient, add the result recipe, ingredient amount, other ingredients, output count, and restrictions.
- Add gameplay effects from normalized `effects` records only through an explicit mapping of supported `trigger` and `effect_key` shapes to Vietnamese text.
- Manual overrides may add or replace effect statements for dynamic callbacks, equipment components, edible behavior, spell actions, and giver interactions found directly in mod Lua.
- `known` when at least one recipe use or effect statement exists.
- `none` only when code evidence explicitly establishes no supported use.
- Otherwise use `unknown`.

### Nguồn nhận

- Exclude `craft` acquisition rows because crafting is already represented by the recipe section.
- Include evidenced `drop`, `harvest`, `start`, `trade`, and other supported acquisition types.
- Preserve source, quantity/range, chance, and conditions when present.
- Resolve source sprites/names through the same entity map used by recipe ingredients.
- `known` when at least one source exists.
- `none` when the item is craft-only and that is positively established.
- Otherwise use `unknown`.

## Manual Overrides

Store exceptional records in `data/manual/tu_tien_item_details.json`. The file is keyed by full entity ID such as `tu_tien:xd_example` and uses the same public detail shapes. Overrides must include evidence paths into `mod/3721846643` and may not silently replace derived data: replacement must be explicit per section.

The override parser rejects:

- unknown entity IDs;
- unsupported status values or source types;
- non-positive quantities;
- `known` sections with no records;
- evidence paths outside the mod directory;
- duplicate semantic records.

## Export and Audit Report

`tools/extract/export_items.py` builds details during the normal `export` command and writes them into `public/data/items.json`. It also writes `data/generated/tu-tien-item-details-report.json` containing:

- total Tu Tiên items;
- counts by status for each section;
- item IDs with one or more `unknown` sections;
- unsupported normalized effect shapes;
- manual override coverage and rejected-record errors.

Output ordering is stable so regenerated artifacts produce reviewable diffs.

## Modal Behavior

- Tu Tiên modals always render the three sections in this order: Công thức, Cách sử dụng, Nguồn nhận.
- A `known` section renders all structured rows.
- A `none` section renders a concise explicit message such as `Không có công thức chế tạo.`
- An `unknown` section renders `Chưa xác định từ dữ liệu mod.`
- Recipe and usage item references remain clickable when the referenced entity exists in the catalog.
- Base-game wiki structured sections continue to render from wiki detail data and are not duplicated by the Tu Tiên detail renderer.

## Error Handling

- Invalid public JSON fails fast in the TypeScript catalog parser with the item index and field name.
- Invalid manual overrides fail the export command before replacing generated files.
- Unsupported effects do not become prose. They are recorded in the audit report and leave the relevant section `unknown` unless other reliable usage exists.
- Missing references retain their prefab ID as text and are reported; they do not crash export or rendering.

## Testing

- Python unit tests cover reverse recipe derivation, acquisition conversion, effect mapping, status classification, override merging, deterministic report output, and rejection cases.
- TypeScript parser tests cover the full details schema and invalid states.
- React tests cover all three modal states, structured recipe usage, gameplay effects, drop sources, and click-through references.
- Existing extractor and frontend tests must remain green.
- The final export must prove all current Tu Tiên item entries contain `details` and the report count equals the catalog count.

## Completion Criteria

- Every exported Tu Tiên item has a valid `details` object.
- Every Tu Tiên modal visibly contains all three sections.
- Derived recipes, reverse usage recipes, supported effects, and acquisition sources are represented without name-based guessing.
- Every unresolved section is visible as `Chưa xác định` and listed in the generated report.
- Tests, lint, and production build pass.
