# Wiki Item Catalog List Design

## Context

The selective wiki crawl and database import are already connected to the
frontend export pipeline. The current published payload contains 2,876 catalog
entries, including 1,454 entries with wiki metadata and 883 entries with a
recipe. The list UI still presents every entry as a Prefab, which makes
standalone wiki pages look like technical records with synthetic identifiers
such as `wiki-100736`.

The database contains the authoritative imported pages, recipes, ingredients,
images, and entity mappings. `tools.extract.cli export` is the supported path
from that database to the public frontend contracts.

## Goals

- Regenerate the public item and wiki artifacts from
  `data/generated/wiki.sqlite` before changing the UI.
- Present the screen as a catalog of items instead of a raw Prefab browser.
- Keep DST, Tu Tien, mapped wiki pages, and standalone wiki pages accessible in
  one list.
- Make images, recipes, wiki provenance, and useful identifiers easy to scan.
- Load full wiki article content only after the user opens an item.
- Preserve the current route, keyboard search shortcuts, accessibility
  behavior, deterministic export pipeline, and progressive result batching.

## Non-goals

- No direct database access from the browser or Next.js runtime.
- No new crawler behavior or mapping heuristics.
- No URL or primary navigation changes.
- No fabricated Vietnamese translations, source values, or recipe data.
- No attempt to reproduce every MediaWiki template or JavaScript interaction.

## Chosen Approach

Use the existing generated JSON contracts as the deployment boundary. The
SQLite database remains the source of truth for extraction, while the Next.js
page imports a compact list payload at build time. Full article JSON and wiki
images remain separate public assets and are fetched only when an item detail
is opened.

This keeps the deployment static, avoids shipping the 843 MB SQLite database to
the browser, and prevents the initial list from embedding complete article
HTML for more than one thousand pages.

## Data Flow

1. `python3 -m tools.extract.cli export` reads the current SQLite database and
   existing game catalog assets.
2. The exporter rewrites `public/data/items.json`, per-page files under
   `public/data/wiki/pages`, wiki image assets, and the generated texture
   manifest atomically.
3. `app/page.tsx` parses the generated item payload once as a Server Component.
4. `WikiSearch` receives the validated list and derives filter counts and the
   visible result batch.
5. Selecting an entry opens `ItemDetailModal` immediately with compact catalog
   data.
6. When the entry has `wiki.detailUrl`, the modal fetches that local JSON file,
   validates the detail contract, and renders the article content. Loading and
   failure states stay inside the modal.

## Catalog Semantics

The UI distinguishes three user-facing sources:

- **Tu Tien**: entries whose namespace is `tu_tien`.
- **DST**: base-game entities without wiki metadata.
- **Wiki**: every entry with wiki metadata, whether mapped to a known entity or
  published as a standalone wiki item.

Mapped wiki entries may expose both their Wiki source and their real Prefab ID.
Standalone wiki entries must not display their synthetic `wiki-*` Prefab ID as
game metadata. They instead display a `Wiki item` label and their page title.

The existing technical categories remain the stable filter values. Their
labels stay localized as Item, Mob, Boss, Nhan vat, Cong trinh, Hieu ung, and
Khac. Wiki categories are searchable but are not expanded into hundreds of
filter controls.

## List UI

### Page summary

The page heading changes from a Prefab lookup framing to an item catalog
framing. A compact summary reports real derived counts for all visible catalog
items, wiki-backed entries, and entries with recipes. These are computed from
the parsed payload and are not hard-coded.

### Search and filters

The search field keeps `/`, Control K, Command K, Escape, clear, and focus
restoration behavior. Visible copy changes from Prefab terminology to item
terminology.

Controls are consolidated into three compact groups:

- Source: Tat ca, Wiki, DST, Tu Tien.
- Category: the existing normalized categories.
- Availability: Tat ca, Co cong thuc, Co anh.

Source, category, and availability filters combine using AND semantics. Search
continues matching names, descriptions, recipe ingredients, Wiki titles,
related pages, and Wiki categories. Changing any control resets the visible
batch to the first 40 results.

### Result cards

Cards retain the current responsive grid and 40-item progressive batching, but
use a denser information hierarchy:

- image at a stable size with the existing missing-image fallback;
- primary and English names;
- one source badge and one normalized category label;
- real Prefab ID only when the entry represents a real mapped entity;
- a two-line description when available;
- a compact recipe preview when a recipe is available;
- a clear `Xem chi tiet` action affordance without duplicating links.

Cards use one blue accent, the current cool neutral palette, 12 to 16 px corner
radii, and only feedback motion on hover, active, and filtered-result entry.
The page stays light themed to preserve the existing brand and avoid an
unrequested visual overhaul.

### Empty and result states

The result heading and screen-reader status report items rather than Prefabs.
The empty state explains that the query or active filters excluded all items
and provides one action to reset every control.

## Detail UI

The modal preserves the current focus trap, Escape handling, backdrop close,
scroll lock, focus restoration, and mobile bottom-sheet behavior.

The overview shows the best available image, title, English name, source,
category, mapping context, and real Prefab ID when applicable. Recipe content
uses the existing ingredient component and output count.

For wiki-backed entries, the modal adds:

- an internal article section loaded from `wiki.detailUrl`;
- the sanitized HTML exported by the trusted local extraction pipeline;
- responsive styling for headings, paragraphs, tables, lists, and images;
- a link to the canonical wiki page;
- related-page links from the compact metadata when present.

The article section shows a shape-matched loading skeleton. If fetching or
validation fails, the compact item detail remains usable and the section shows
a retry action plus the canonical external Wiki link.

## Contract Changes

The compact item payload remains schema version 4. Frontend filtering gains
explicit source and availability filter types. A separate runtime parser is
added for the existing per-page wiki detail schema so malformed public data is
reported as a contextual article error instead of crashing the entire list.

No full article HTML is added to `ItemListEntry` or serialized through the
Server Component boundary.

## Performance

- Keep the page itself as a Server Component and the interactive catalog as the
  existing focused Client Component boundary.
- Memoize derived item lookup maps, filter counts, and filtered results.
- Render at most 40 result cards initially and use `content-visibility` for
  off-screen cards where supported.
- Fetch full article JSON only for the selected wiki item.
- Avoid new animation or component dependencies.
- Reuse the existing Phosphor icon family and generated local images.

## Accessibility

- Every filter group has an accessible name and pressed or selected state.
- Search and result status updates remain announced without moving focus.
- Interactive targets remain at least 44 px high.
- Images receive meaningful item labels; decorative category icons stay hidden
  from assistive technology.
- Article tables remain horizontally scrollable on narrow screens.
- Loading, error, retry, canonical link, and modal close controls are keyboard
  accessible.
- Existing reduced-motion behavior is preserved.

## Error Handling

- Export failures leave atomic public JSON writes incomplete rather than
  partially published.
- Invalid compact payloads continue to fail during the page build.
- Wiki detail fetch and validation failures are isolated to the selected modal.
- Entries without images, recipes, descriptions, wiki data, or real Prefab IDs
  render valid compact states without placeholder facts.

## Testing

Tests follow a red-green cycle and cover:

- source and availability filter combinations;
- Wiki entries using Wiki semantics instead of synthetic Prefab labels;
- real mapped entries retaining their Prefab ID;
- derived summary counts;
- revised item-focused labels and screen-reader status;
- wiki detail schema parsing;
- modal loading, success, failure, retry, article, canonical link, recipe, and
  focus behavior;
- unchanged batching, search shortcuts, normalized Vietnamese search, empty
  state reset, ingredient navigation, and catalog curation.

Final verification runs the focused Vitest suites, the complete frontend test
suite, ESLint, the Python extraction tests, catalog validation, and a production
Next.js build.

## Design Audit

This is a targeted redesign that preserves the existing information
architecture, route, header, cool blue palette, Geist typography, accessible
interactions, and compact card pattern. The redesign retires Prefab-only copy,
synthetic identifier leakage, duplicated filter rows, and empty detail panels.

Design settings:

- `DESIGN_VARIANCE: 4`
- `MOTION_INTENSITY: 2`
- `VISUAL_DENSITY: 7`

The page remains a dense product UI, so it deliberately avoids landing-page
hero patterns, decorative motion, gradients, glass effects, generated imagery,
and new design-system dependencies.
