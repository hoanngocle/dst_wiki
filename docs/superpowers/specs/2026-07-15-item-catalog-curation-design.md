# Item Catalog Curation Design

## Context

The wiki currently exposes internal prefab variants in the search results. This creates duplicate-looking cards such as `fence_gate_luoshen` and `fence_gate_luoshen_item`, while effect-only prefabs ending in `_fx` add noise. Base-game source labels are also inconsistent between the filter, result card, and detail modal.

## Requirements

- Display `DST` everywhere the UI currently displays `DST gốc` or `DST gốc liên quan`.
- Exclude every catalog entry whose `prefabId` ends with the exact suffix `_fx`.
- For entries in the same namespace whose prefab IDs form an exact `foo` and `foo_item` pair:
  - keep only `foo_item` when it has a sprite;
  - otherwise keep only `foo`.
- Preserve standalone entries that do not form such a pair, including standalone `_item` entries.
- Preserve the existing order of every retained entry.
- Apply the curated catalog consistently to search results, result counts, item lookup, recipes, and detail selection.

## Considered Approaches

### Curate after parsing the catalog (selected)

Parse and validate every payload entry first, then run one deterministic curation pass before returning the catalog. This gives every UI consumer the same data without changing the generated JSON or duplicating filtering rules in components.

### Filter only in the search component

This is a smaller local edit, but hidden entries could remain in lookup maps or be reachable through recipe interactions. Counts and other future catalog consumers could also diverge.

### Filter during data export

This produces a smaller generated payload, but broadens the change into the extraction pipeline and requires regenerating published data. It also makes a presentation-oriented rule harder to adjust independently.

## Design

`parseItemPayload` will continue validating the complete schema and parsing each entry. A focused catalog-curation function will then:

1. remove entries whose `prefabId` ends in `_fx`;
2. index entries by namespace and `prefabId`;
3. identify exact base/`_item` pairs;
4. select the `_item` entry only when its `sprite` is non-null, otherwise select the base entry;
5. return retained entries in their original input order.

Pairing by both namespace and prefab ID stem prevents a Tu Tiên prefab from suppressing a base-game prefab with the same technical name. The rule only applies to exact suffix relationships, so unrelated names containing `_item` are unaffected.

The filter button, item card, and item detail modal will use the single label `DST` for the `base_game` namespace.

## Data Flow

The generated `items.json` payload remains unchanged. The server page parses it once, receives the curated list, and passes that list to `WikiSearch`. Search filtering, result totals, `itemsById`, result cards, and modal navigation therefore operate on the same catalog.

## Error Handling

Payload validation behavior remains unchanged: malformed entries still throw instead of being silently discarded. Curation runs only on validated `ItemListEntry` values. Missing pair members are normal and do not produce errors.

## Testing

Catalog tests will cover these independent behaviors:

- `_fx` entries are removed;
- `foo_item` with a sprite replaces `foo`;
- `foo_item` without a sprite is removed while `foo` remains;
- standalone `_item` entries remain;
- retained entries preserve their original order and namespace isolation.

Component tests will assert that the base-game filter, result card, and detail modal render `DST` and no longer render the old labels. Existing search and interaction tests must continue to pass.

## Out of Scope

- Rewriting or shrinking `public/data/items.json`.
- Fuzzy duplicate detection based on translated names or descriptions.
- Changing card layout, category labels, sprites, or recipe presentation.
