# Full DST Prefab Catalog Design

## Goal

Expose every base-game DST prefab module found under `scripts/prefabs/*.lua` in
the wiki search experience. Keep the existing batch size of 40 results and the
`Xem thêm` interaction, while assigning every exported prefab to one stable
category.

## Approved Scope

- The source of truth for base-game coverage is the complete set of `.lua`
  files directly under `scripts/prefabs/` in the verified `scripts.zip`
  snapshot.
- Each source file produces exactly one base-game catalog entry.
- The prefab ID is the lowercase file stem. For example,
  `scripts/prefabs/alterguardian_phase1.lua` produces
  `base_game:alterguardian_phase1`.
- The extractor does not execute DST and does not attempt to expand multiple
  `Prefab(...)` values returned by one file.
- No dependency request, inventory status, recipe presence, name, icon, or
  category may prevent a prefab module from being exported.
- Existing Tu Tiên entities remain searchable; this change must not remove
  them.
- Search results continue to reveal 40 entries at a time through `Xem thêm`.

## Non-goals

- Building an authoritative runtime registry of every dynamically generated
  `Prefab(...)` name.
- Executing a headless DST server during extraction.
- Guaranteeing that every helper/effect prefab has a localized display name,
  icon, description, or recipe.
- Adding prefab detail pages.
- Manually maintaining a category mapping for every prefab.

## Data Model

Every compact search entry has the following fields:

```ts
type PrefabCategory =
  | "item"
  | "mob"
  | "boss"
  | "character"
  | "structure"
  | "effect"
  | "other";

type PrefabListEntry = {
  id: string;
  prefabId: string;
  namespace: "tu_tien" | "base_game";
  category: PrefabCategory;
  name: string;
  englishName: string | null;
  description: string | null;
  sprite: SpriteDescriptor | null;
  recipe: ItemRecipe | null;
};
```

Missing metadata is valid:

- `name` falls back to `prefabId`.
- `englishName`, `description`, `sprite`, and `recipe` may be `null`.
- A missing sprite renders the existing placeholder.
- A missing recipe renders `Không có công thức`.

The public payload advances to schema version `2`; the parser rejects missing
or invalid `category` values.

## Prefab Discovery

`ScriptIndex` exposes all prefab modules from the verified scripts archive.
Discovery must:

1. select archive members matching `scripts/prefabs/*.lua` directly;
2. derive the lowercase file stem;
3. reject duplicate derived IDs rather than silently overwriting one;
4. return entries sorted by prefab ID;
5. create a minimal base-game entity for every discovered ID, even when the
   existing dependency enrichment cannot find name, recipe, stats, or assets.

Dependency evidence from Tu Tiên remains attached where available, but it is
provenance rather than an inclusion gate.

## Category Classification

Classification is deterministic and uses the prefab ID plus literal source
signals from its Lua module. The first matching rule wins:

1. `effect`: prefab ID contains or ends with an effect/helper marker such as
   `_fx`, `fx`, `_projectile`, `_placer`, `_classified`, `_marker`, or source
   sets `persists` to `false`.
2. `character`: source contains a `MakePlayerCharacter` call.
3. `boss`: source adds the literal `epic` tag.
4. `mob`: source adds a literal creature tag (`animal`, `character`,
   `hostile`, `monster`, or `smallcreature`), or contains literal health,
   combat, and locomotor component assignments.
5. `item`: source contains a literal inventory-item component assignment.
6. `structure`: source adds the literal `structure` tag, or contains a
   literal workable component assignment without an inventory-item component.
7. `other`: no earlier rule matches.

The classifier operates on code with comments and strings handled by the
existing Lua scanning helpers, so a commented component name cannot change a
category. Category is intentionally heuristic; `other` is the safe fallback.

For Tu Tiên entities, use an existing normalized category when it maps to the
seven values above. Otherwise apply the same source classifier when source is
available, then fall back to `other`.

## Extraction and Export Flow

1. Verify `scripts.zip` and `images.zip` against the snapshot manifest.
2. Build `ScriptIndex` and discover every base-game prefab module.
3. Create minimal entity facts for the full discovered set.
4. Enrich the set with existing names, descriptions, recipes, stats,
   acquisition data, dependency evidence, and inventory assets when present.
5. Normalize and persist all entities in `wiki.sqlite`.
6. Export every normalized Tu Tiên entity and exactly the discovered
   base-game module IDs to `public/data/items.json`; remove the current
   `is_inventory_item == true` inclusion condition.
7. Publish only textures referenced by exported entries. Missing textures do
   not exclude an entry.

The export remains deterministic and sorted by entity ID.

## Search Interface

- Keep namespace filters: `Tất cả`, `Tu Tiên`, and `DST gốc`.
- Keep `Có công thức` as an optional filter.
- Add a separate category filter group with `Tất cả`, `Item`, `Mob`, `Boss`,
  `Nhân vật`, `Công trình`, `Hiệu ứng`, and `Khác`.
- Text search covers display name, English name, prefab ID, description, and
  recipe ingredient names.
- A result card displays its category and namespace as visible metadata.
- Initial rendering is capped at 40 matching results. Each `Xem thêm` click
  reveals the next 40 until every match is visible.
- Changing search text, namespace, craftability, or category resets the visible
  batch to 40.
- Empty-state reset clears every filter.

The page language changes from `Items` to `Prefabs` where it describes the
whole catalog. Recipe-specific text remains item-oriented.

## Error Handling and Validation

Extraction hard-fails when:

- the scripts snapshot fails checksum validation;
- a prefab module cannot be decoded as UTF-8 with BOM support;
- two archive members derive the same prefab ID;
- an exported entry has an invalid namespace or category;
- the exported base-game ID set differs from the discovered prefab-module ID
  set.

Missing names, descriptions, recipes, and icons are coverage warnings, not
hard failures.

## Testing Strategy

Python unit tests cover:

- complete, sorted prefab-module discovery;
- duplicate-ID rejection;
- every category rule and rule priority;
- comments and unrelated strings not affecting classification;
- full base-game export without the inventory-only filter;
- exact equality between discovered base-game IDs and exported base-game IDs;
- deterministic output and missing-metadata fallbacks.

Frontend tests cover:

- parsing all seven categories;
- category and namespace filters combining correctly;
- visible category metadata;
- 40-result batching remains intact;
- query or filter changes reset the batch;
- empty-state reset clears category as well as existing filters.

Regression verification runs the complete Python and frontend test suites,
lint, production build, archive/export validation, and an explicit count check
against `scripts/prefabs/*.lua`.

## Acceptance Criteria

- Every `.lua` file directly under `scripts/prefabs/` has exactly one matching
  `base_game` entry in `public/data/items.json`.
- No base-game prefab module is excluded for lacking inventory status or other
  metadata.
- Every entry has exactly one approved category.
- Existing Tu Tiên entries remain present.
- Search and filters operate across the combined catalog.
- The UI still renders 40 results initially and exposes all remaining matches
  through `Xem thêm`.
- All automated checks pass without staging or overwriting unrelated local
  data changes.
