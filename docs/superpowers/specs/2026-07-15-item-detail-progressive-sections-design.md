# Item detail progressive sections

## Goal

Make the item detail modal visually ready for the complete wiki layout while the
catalog still exposes only its current fields. The modal must never show empty
or invented values.

## Chosen approach

Use progressive disclosure. Each section is rendered only when the item has a
value for it. Current catalog fields therefore produce the following visible
sections:

- **Overview**: sprite, Vietnamese and English names, source namespace, prefab
  ID, and category.
- **Description**: only when a description exists.
- **Crafting**: only when a recipe exists; it uses the existing ingredient
  renderer and exposes the output count.
- **Miscellaneous**: the stable prefab identifier and content namespace.

Future item fields can add sections for Food Info, Object Info, Source,
Filters, and Tier without changing the modal's layout contract. Until those
fields exist, they stay absent rather than displaying a blank card or a
"missing data" message.

## UI and accessibility

- Keep the existing accessible modal behavior: labelled dialog, close button,
  escape/backdrop handling, focus trap, focus restoration, and scroll lock.
- Replace the sparse white blocks with compact, consistent information panels
  inside the existing modal. Each visible panel has a clear heading and either
  a small definition list or the recipe ingredient renderer.
- Present the category in the overview so the modal contains all currently
  available item metadata.
- Preserve the user's existing title change: the heading is the item name,
  not "Chi tiết {item name}".
- Maintain responsive behavior: stacked content on small screens and a
  two-column metadata grid once sufficient width is available.

## Testing

- Extend the modal component test to assert current metadata sections and the
  no-recipe/no-description state.
- Run the focused component test and the project verification command defined
  by the package scripts.

## Scope boundaries

This change does not alter the generated item payload, scraper/extractor, or
catalog schema. It does not fabricate game values. Adding real Food Info,
Object Info, Source, Filters, Tier, and related sprites is deferred to the
future data-enrichment task.
