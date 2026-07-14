# Interactive Recipe Item Details Design

## Goal

Make recipe ingredients discoverable and actionable without leaving the Items list. Hovering or focusing an ingredient reveals its name, and activating it opens a modal containing that ingredient's existing full `ItemListEntry` data. This increment also removes the redundant `Loại: Item` icon from each result card.

## User experience

- The item sprite becomes the leading visual in each result card after the `Package` type icon is removed.
- An ingredient that resolves to a full catalog item is rendered as a button.
- Hovering or focusing the ingredient button reveals a custom tooltip with the Vietnamese item name.
- Clicking the ingredient button, or activating it with Enter or Space, opens a modal for that item.
- The modal shows the item sprite, Vietnamese and English names when available, source, prefab identifier, description, and recipe.
- The modal closes from its close button, the backdrop, or Escape.
- Closing restores focus to the ingredient button that opened the modal.
- If an ingredient does not resolve to a full catalog entry, it remains a non-interactive recipe chip with its existing accessible label and native title. No partial modal is opened.

## Architecture

`WikiSearch` already owns the complete `readonly ItemListEntry[]`. It builds a memoized `Map<string, ItemListEntry>` once, owns the selected full item in state, and renders one shared modal. The modal never performs an ID lookup.

`WikiSearch` passes the item map and an `onSelectItem(item: ItemListEntry)` callback through `ItemResult` to `RecipeIngredients`. `RecipeIngredients` resolves each recipe reference before rendering its control. Activating a resolved ingredient sends the full `ItemListEntry` object upward. `ItemDetailModal` receives only the selected full item and `onClose`, keeping it independent from the catalog and lookup logic.

The modal's recipe is display-only in this increment. Ingredient navigation begins from the list cards; recursively opening another item from inside the modal is outside the requested scope.

## Component boundaries

- `WikiSearch`: catalog lookup, selected-item state, and modal placement.
- `ItemResult`: item card layout and prop forwarding to its recipe.
- `RecipeIngredients`: interactive ingredient controls, tooltip presentation, and unresolved fallback chips.
- `ItemDetailModal`: detail presentation, dismissal, scroll lock, focus entry/trap/restoration.

## Accessibility

- Ingredient buttons retain the existing accessible name format: `<name>, số lượng <amount>`.
- Tooltips are connected with `aria-describedby` and appear on both pointer hover and keyboard focus.
- The modal uses `role="dialog"`, `aria-modal="true"`, and a labelled heading.
- Opening focuses the close button. Tab and Shift+Tab remain within the modal.
- Escape closes the modal and focus returns to the opener.
- Motion and hover styling do not carry information required to use the controls.

## Data and error handling

No schema or generated JSON changes are required. `RecipeIngredient.id` is matched against `ItemListEntry.id`. Unresolved references keep their current static rendering, so incomplete source data cannot produce an empty or misleading modal.

## Verification

- Component tests cover full-item callback payloads, tooltip semantics, and unresolved ingredient fallback.
- Modal tests cover full detail rendering, close controls, Escape, backdrop dismissal, initial focus, focus trapping, and focus restoration.
- Integration coverage in `WikiSearch` confirms a recipe ingredient opens the modal with the referenced full item rather than the parent card item.
- Existing item search, filtering, batching, normalized highlighting, empty recipes, and missing sprites remain passing.
- Lint and production build pass.
