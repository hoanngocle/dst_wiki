# Remove Item Type Icon Design

## Goal

Remove the decorative `Package` icon labelled `Loại: Item` from the start of every item result card so the item sprite becomes the card's leading visual.

## Scope

- Remove the `Package` icon import and its labelled wrapper from `ItemResult`.
- Change the identity row from three columns to two columns: the 64 px item sprite and the remaining item metadata.
- Keep item names, source labels, prefab identifiers, descriptions, recipes, and all search behaviour unchanged.
- Update the focused component test so it no longer expects the removed type icon.

## Accessibility

The removed element is redundant because every card is already presented in the Items list and has a visible item heading. The item sprite keeps its existing accessible behaviour.

## Verification

- Run the `ItemResult` component test.
- Run lint to catch the removed import or JSX issues.
