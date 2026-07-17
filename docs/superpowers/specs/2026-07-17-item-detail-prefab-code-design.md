# Item Detail Prefab Code Design

## Goal

Show an item's real prefab code in the detail modal beneath its displayed names, matching the search result card.

## Behavior

- Import and use `hasRealPrefab` from `app/lib/wiki-search` in `ItemDetailModal`.
- When `hasRealPrefab(item)` is true, render `item.prefabId` in a `<code>` element directly below the English name, or directly below the primary name when no English name exists.
- Use the same compact monospace treatment as the result card.
- When the item is a standalone Wiki page without a real prefab, render no synthetic prefab code.
- Keep the existing title, English name, category/source badges, accessibility behavior, and modal interactions unchanged.

## Testing

- Update the existing modal identity test to expect the real prefab code.
- Add coverage proving a standalone Wiki item does not expose its synthetic `prefabId`.
- Run the focused modal test, then lint and the full test suite.

## Scope

This change is limited to the item detail modal and its tests. It does not introduce a shared identity component or alter catalog data.
