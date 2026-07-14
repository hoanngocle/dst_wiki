# Real Item Search List Design

Date: 2026-07-14
Status: Proposed for implementation

## Context

The current Items page is a working search demo backed by eight `WikiEntry` records. The offline extraction pipeline now publishes a real catalog with 437 inventory items, Vietnamese names, recipe relationships, and inventory asset metadata. The next increment replaces the demo rows with real Tu Tien and referenced base-game items.

This specification supersedes only the eight-sample-entry requirement in `2026-07-14-vietnamese-items-base-gallery-design.md`. The shared navigation and `/base` gallery remain outside this increment.

## Goal

Render a fast, Vietnamese item-search experience in which each result presents a UI type icon, the real inventory sprite, the item name, and a recipe made of ingredient sprites with quantities.

## Scope

Included:

- Inventory items where `is_inventory_item` is true.
- Both `tu_tien` items and the `base_game` dependencies referenced by Tu Tien.
- Vietnamese-first names and descriptions with English and prefab fallbacks.
- Client-side, case-insensitive and diacritic-insensitive search.
- Filters for all items, Tu Tien, base-game dependencies, and craftable items.
- Web publication of real inventory textures from local KTEX sources.
- Recipe ingredient sprites, accessible ingredient names, and integer quantities.
- A bounded initial result set with a load-more action.
- Loading, empty, missing-image, and no-recipe states.

Excluded:

- A complete catalog of every base-game DST item.
- Item detail routes.
- Search ranking services, server-side search, or a database API.
- Editing, authentication, favorites, or persistence.
- Handbook page presentation.
- Changes to `/base`.

## Design Read

This is a data-heavy reference surface for DST players. Preserve the existing bright, cool-neutral visual language and accessibility behavior while increasing information density enough for rapid scanning.

- `DESIGN_VARIANCE: 4`
- `MOTION_INTENSITY: 3`
- `VISUAL_DENSITY: 6`
- Tailwind CSS v4 with the existing Geist family and Phosphor icons.
- Light theme remains locked for this increment because the current application is explicitly light-only and a dark-theme redesign is not part of the request.

## Chosen Approach

Generate a compact frontend payload and browser-compatible texture files offline, then pass the compact records from the server page into the existing client search island.

This approach is preferred because it:

- Keeps extraction provenance and large asset evidence out of the client bundle.
- Avoids fetching two large JSON documents after hydration.
- Preserves immediate local search over only 437 records.
- Reuses decoded texture atlases for both result images and recipe ingredients.
- Keeps proprietary KTEX decoding outside the browser.

Alternatives rejected:

1. Join `catalog.json` and `assets.json` in the browser. This transfers roughly 1.2 MB before textures and exposes provenance fields the UI does not use.
2. Add a server search endpoint. The dataset is too small to justify network round trips or server search state.
3. Crop and publish one image per item. This duplicates shared base-game atlases and requires a second image-processing dependency. Publishing decoded textures plus UV descriptors is smaller and keeps the pipeline deterministic.

## Data and Asset Flow

```text
wiki.sqlite
  -> catalog.json + assets.json
  -> frontend item exporter
       -> public/data/items.json
       -> required texture manifest

local mod textures + copied images.zip
  -> pinned ktech-compatible decoder
  -> public/assets/game/<texture-sha256>.png

app/page.tsx
  -> compact ItemListEntry[]
  -> WikiSearch client island
  -> ItemResult + GameSprite + RecipeIngredient
```

The converter is an external build-time tool, not a data source. It may only decode the local mod files and the verified local `images.zip` snapshot. No website or wiki content enters the dataset.

The publisher accepts an explicit decoder command, defaults to `ktech`, and fails with an actionable error when it is unavailable. Generated texture filenames use the existing texture SHA-256 so repeated runs are stable and identical textures are decoded once.

## Frontend Contract

`public/data/items.json` uses a compact, versioned structure:

```ts
type SpriteDescriptor = {
  src: string;
  uv: {
    u1: number;
    u2: number;
    v1: number;
    v2: number;
  };
};

type RecipeIngredient = {
  id: string;
  name: string;
  amount: number;
  sprite: SpriteDescriptor | null;
};

type ItemListEntry = {
  id: string;
  prefabId: string;
  namespace: "tu_tien" | "base_game";
  name: string;
  englishName: string | null;
  description: string | null;
  sprite: SpriteDescriptor | null;
  recipe: {
    outputCount: number;
    ingredients: RecipeIngredient[];
  } | null;
};
```

Rules:

- `name` uses Vietnamese, then English, then `prefabId`.
- `description` uses Vietnamese, then English, then `null`.
- Only one asset row is selected per icon key. Prefer `available: true`, then the highest-confidence deterministic row.
- Recipe lists remain arrays in the source catalog, but the current normalized data has at most one recipe per product. The list contract exposes that single recipe as nullable.
- A source recipe with zero normal ingredients remains a recipe with an empty ingredient array. The UI labels it as a special recipe instead of claiming data is missing.
- Quantities are serialized as integers. Current ingredient quantities have no fractional values.

## Texture Publication and Sprite Rendering

The asset publisher performs these operations:

1. Select only textures referenced by item and ingredient sprites.
2. Read Tu Tien textures from the immutable mod directory and base-game textures from the checksum-verified `images.zip` snapshot.
3. Decode each unique KTEX texture to PNG through the explicit decoder command.
4. Verify the decoder produced a non-empty PNG before atomically publishing it under `public/assets/game/`.
5. Keep UV coordinates from `assets.json` in the compact item payload.

`GameSprite` renders the decoded texture as a CSS background and crops it with the normalized UV rectangle. Vertical coordinates are converted from the atlas bottom-left origin to CSS top-left positioning. The component receives a fixed square size so layout does not shift while textures load.

The item name is already visible beside the main sprite, so the main sprite is decorative. Each recipe ingredient wrapper exposes its ingredient name and quantity through an accessible label because the visual formula otherwise contains only an image and a number.

## Search and Filtering

The existing Unicode normalization and keyboard shortcuts remain.

Searchable text includes:

- Vietnamese item name.
- English item name.
- Prefab ID.
- Vietnamese or English description.
- Ingredient names.

Filters:

- `Tất cả`: every inventory item in the compact payload.
- `Tu Tiên`: `namespace === "tu_tien"`.
- `DST gốc`: `namespace === "base_game"`. The interface describes these as referenced dependencies, not the complete DST catalog.
- `Có công thức`: recipe is non-null.

Filtering remains synchronous and memoized. The result count and screen-reader status update whenever query or filter state changes.

## Result Layout

Desktop results use a two-column card grid rather than a long divider list. Each card contains:

- A Phosphor package icon as the UI type icon.
- A fixed square inventory sprite.
- Vietnamese item name and compact prefab/source metadata.
- A recipe row that wraps ingredient groups naturally.

On viewports below 768 px, each card becomes a single-column composition. The sprite and name remain on the first row; the recipe occupies a full-width second row. Ingredient groups may wrap but must never cause horizontal page overflow.

The page initially shows 40 filtered results. `Xem thêm` reveals the next 40. A query or filter change resets the visible limit to 40. This bounds texture requests and DOM work without adding pagination state to the URL.

## States and Edge Cases

- Missing sprite: render a neutral image placeholder with the same dimensions.
- No recipe: show `Không có công thức` in subdued text.
- Special recipe with zero ingredients: show `Công thức đặc biệt`.
- No search results: keep the existing reset action and restore search focus.
- Empty item payload: show an explanatory empty state rather than a blank grid.
- Texture decode failure: the offline publish command fails before replacing existing generated assets.
- Two inventory items without `icon_key`: use the normal missing-sprite state.
- Base-game duplicate asset rows: select only the available row deterministically.

## Component Boundaries

- `tools/extract/export_items.py`: build the compact item contract and required texture manifest from published catalog and asset metadata.
- `tools/extract/publish_web_assets.py`: locate verified local KTEX inputs, invoke the decoder, and atomically publish hashed PNG textures.
- `app/lib/item-catalog.ts`: TypeScript contract validation helpers and search/filter logic.
- `app/components/game-sprite.tsx`: one sprite crop with missing-image fallback.
- `app/components/recipe-ingredients.tsx`: accessible formula rendering.
- `app/components/item-result.tsx`: one item card.
- `app/components/wiki-search.tsx`: query, filters, result limit, status, and composition only.
- `app/page.tsx`: server entry point that supplies compact item data.

Each unit has one responsibility and can be tested independently.

## Performance

- Do not pass `catalog.json`, `assets.json`, SQLite evidence, or checksums into the client component.
- Build lookup maps once during export and once for client-side filtering where needed.
- Render at most 40 new cards per load-more action.
- Reserve sprite dimensions to prevent layout shift.
- Import Phosphor icons directly from the existing dependency.
- Keep motion to hover, active, and the existing short result-boundary transition. Respect reduced-motion preferences.

## Testing and Verification

Develop test-first.

Python tests cover:

- Vietnamese and English fallback selection.
- Available asset selection when duplicate rows exist.
- Ingredient name, quantity, and sprite joins.
- Zero-ingredient special recipes.
- Stable hashed texture paths and one decode per unique texture.
- Atomic behavior when the decoder is absent or fails.

TypeScript tests cover:

- Real item filtering by namespace and craftability.
- Search by Vietnamese text with and without diacritics.
- Search by English name, prefab ID, and ingredient name.
- Main item sprite, name, and recipe rendering.
- Accessible ingredient names and quantities.
- Missing image, no recipe, and special recipe states.
- Load-more batches and reset after query/filter changes.
- Existing keyboard shortcuts, focus restoration, and live-region announcements.
- Mobile-safe category/source metadata remains visible.

Completion checks:

```bash
python3 -m unittest discover -s tests/extract -v
npm test
npm run lint
npm run build
python3 -m tools.extract.cli validate
git diff --check
```

Visually inspect the Items route at desktop and 375 px widths. Confirm readable recipes, no horizontal overflow, stable image boxes, and clear missing-data states.

## Acceptance Criteria

- The Items page contains no eight-entry demo dataset.
- Search operates on all 437 current inventory items.
- Every result displays a UI icon, item name, and an inventory sprite or intentional fallback.
- Craftable items display ingredient sprites multiplied by integer quantities.
- All ingredient formulas have accessible names.
- Search and filters preserve the current keyboard and screen-reader behavior.
- The client receives only the compact item payload.
- Published images are derived exclusively from local verified game/mod assets.
- Full tests, lint, production build, extraction validation, and visual checks pass.
