# Nightmare Fuel Wiki Sections Design

## Context

The item detail modal currently mixes compact catalog metadata with a complete
sanitized Wiki article. The article contains useful structured sections, but
Drop table and Usage are still rendered as raw MediaWiki HTML. The modal also
shows Related pages and Technical information panels that the user no longer
wants.

The SQLite database stores both normalized game extraction tables and the
complete imported Wiki revision. For `base_game:nightmarefuel`, the normalized
game tables contain 5 acquisition rows and 17 recipe usages, while the imported
Wiki revision contains 10 Drop table rows and 30 Usage recipes across Don't
Starve and its DLC variants. The Wiki revision is the selected source because
it is materially more complete.

This change is a one-record pilot for Nhiên liệu Ác Mộng / Nightmare Fuel. The
normalizer must be reusable, but only Wiki page `210449` is published with the
new structured contract in this iteration.

## Goals

- Remove the Related pages panel from every item detail.
- Remove the Technical information panel from every item detail.
- Normalize the Nightmare Fuel Drop table and Usage sections from the imported
  Wiki wikitext during the deterministic export.
- Render Drop table and Usage as dedicated, readable regions before the
  remaining Wiki article.
- Remove the original Drop table and Usage blocks from the free-form article so
  the data is not duplicated.
- Preserve all other article content, including Gathering, Trivia, Gallery,
  images, and the canonical Wiki link.
- Keep the pilot backward compatible for all other Wiki page detail files.

## Non-goals

- Do not normalize every Wiki page in this iteration.
- Do not use the smaller game extraction tables as the displayed source for
  Drop table or Usage.
- Do not parse Wiki HTML in the browser.
- Do not add dependencies, change crawler behavior, change routes, or change
  entity mapping heuristics.
- Do not download every icon referenced by the Wiki usage table in this pilot.
- Do not translate Wiki-only names or notes that have no mapped Vietnamese item
  name.

## Chosen Approach

Normalize data at export time with a focused Python module. The module accepts
Wiki wikitext and produces typed JSON for the two requested sections. It parses
MediaWiki table rows and balanced Recipe templates without executing templates
or depending on network access.

The exporter invokes this normalizer only for page `210449`. The generated
detail JSON keeps schema version 1 and gains an optional `normalized` object
with its own schema version. All existing page details remain valid and all
existing consumers may ignore the optional field.

This approach is preferred over client-side HTML parsing because it is
deterministic, testable, and reusable. It is preferred over handcrafted JSON
because future pages can use the same parser once their section shapes are
reviewed.

## Data Source and Flow

1. `wiki_pages.wikitext` and `wiki_pages.html` remain the source records in
   `data/generated/wiki.sqlite`.
2. `load_wiki_export()` identifies page `210449` as an enabled normalized-page
   pilot.
3. The Wiki section normalizer extracts Drop table and Usage from wikitext.
4. Reference titles are resolved against selected `wiki_entity_mappings` when
   possible. A resolved reference receives an internal item ID such as
   `base_game:amulet`; unresolved references retain their Wiki title and URL.
5. The exporter removes the rendered Drop table and Usage blocks from the
   article HTML for this page only.
6. `public/data/wiki/pages/210449.json` receives the optional normalized object
   and the remaining article HTML.
7. The frontend parser validates the optional contract after the detail file is
   fetched.
8. The modal renders the two structured regions, then renders the remaining
   Wiki article.

## Detail Contract

The optional detail field uses this shape:

```json
{
  "normalized": {
    "schema_version": 1,
    "dropTable": {
      "rows": [
        {
          "sources": [
            {
              "title": "Beardling",
              "url": "https://dontstarve.wiki.gg/wiki/Beardling",
              "entityId": null
            }
          ],
          "quantity": "1-3",
          "chance": "40%",
          "context": null
        }
      ]
    },
    "usage": {
      "recipes": [
        {
          "result": {
            "title": "Night Light",
            "url": "https://dontstarve.wiki.gg/wiki/Night_Light",
            "entityId": "base_game:nightlight"
          },
          "nightmareFuelAmount": 2,
          "ingredients": [
            {
              "item": {
                "title": "Gold Nugget",
                "url": "https://dontstarve.wiki.gg/wiki/Gold_Nugget",
                "entityId": "base_game:goldnugget"
              },
              "amount": 8
            }
          ],
          "station": "Prestihatitator",
          "dlc": null,
          "character": null,
          "note": null
        }
      ]
    }
  }
}
```

Rules:

- `quantity` and `chance` preserve the exact Wiki display value.
- Drop sources are ordered as they appear in the Wiki row.
- `context` preserves meaningful conditions not represented by source titles,
  quantity, or chance.
- Usage recipes remain in Wiki order.
- Missing ingredient counts default to 1, matching MediaWiki Recipe template
  semantics.
- `nightmareFuelAmount` is extracted from whichever ingredient slot references
  Nightmare Fuel.
- `result`, `station`, `dlc`, `character`, and `note` preserve Wiki values.
- `entityId` is optional and never guessed. It is emitted only when the page
  mapping resolves uniquely to a selected entity.

## Wikitext Normalization

### Drop table

The normalizer locates the heading whose normalized text is `Drop table`, then
reads the following MediaWiki table until the next level-2 heading. It skips the
header row and extracts three logical cells per data row: source, quantity, and
chance.

The source cell parser recognizes `Pic` template variants and Wiki links. It
normalizes template arguments into reference titles, removes duplicate
references while preserving order, and converts remaining meaningful markup to
plain context text. Unsupported markup is preserved as context text rather than
silently fabricated.

### Usage

The normalizer locates the level-2 Usage section and reads each balanced
`Recipe` template until the next level-2 heading. Template names and parameter
keys are case insensitive. Named parameters are parsed only at the top template
level so nested Wiki links and templates do not break field boundaries.

Ingredient slots `item1` through `item3` and their matching `count` values are
normalized. Nightmare Fuel is separated from the other ingredients. Result,
tool, DLC, character, note, and result count values are preserved.

If the pilot page no longer contains either expected section, export fails with
a contextual error instead of publishing an empty successful contract.

## Article De-duplication

The trusted exported HTML is already sanitized. For page `210449`, the exporter
removes the block beginning at the heading containing `id="Drop_table"` through
the final Usage recipe immediately before the next level-2 heading. Drop table
and Usage are contiguous in the current revision, so the entire range can be
removed as one bounded operation.

The operation must verify both heading markers and the following level-2
boundary. If the expected structure is missing, export fails and preserves the
previous atomic output.

## Detail UI

The modal header, description, existing item recipe, focus trap, Escape close,
backdrop close, scroll lock, focus restoration, and mobile bottom-sheet behavior
remain unchanged.

Related pages and Technical information are removed without replacement.

### Drop table region

Drop table is one bordered region with a heading and real row count. Rows use a
single-column grid on mobile and two columns from the medium breakpoint. Each
row displays source names first, then quantity and chance as compact numeric
facts, with context below when present. Internal item names use the catalog's
Vietnamese display name when `entityId` resolves; otherwise the Wiki title is
shown. Numbers use the existing mono type treatment.

### Usage region

Usage is one bordered region grouped by DLC value. Recipes use a single column
on mobile and two columns from the medium breakpoint. Each recipe emphasizes
the result, shows the Nightmare Fuel amount, lists remaining ingredients, and
shows station, character restriction, DLC, and note only when present.

The region contains all normalized recipes. It does not truncate, paginate, or
hide Wiki rows in this pilot because completeness is the purpose of the test.

### Remaining article

The existing Wiki article component continues to show saved source images, the
canonical link, loading state, retry state, and the remaining sanitized HTML.
The Bài viết Wiki heading remains because the article still contains useful
prose and media after the two structured sections are removed.

## Visual Direction

Reading this as a targeted redesign of a dense knowledge detail for players who
need complete reference data, with a calm technical language using the existing
Tailwind utilities, cool-neutral palette, blue accent, and Phosphor icon family.

Design settings:

- `DESIGN_VARIANCE: 3`
- `MOTION_INTENSITY: 1`
- `VISUAL_DENSITY: 7`

The modal keeps the established 12 to 16 px radius system. Drop rows and Usage
recipes use restrained grouped tiles because the content exceeds five entries
and a long divider table would be harder to scan. No new animation, gradients,
theme changes, generated imagery, or dependency is introduced.

## Accessibility

- Both regions use headings and semantic lists.
- Quantity and chance labels remain visible and are not encoded only by color.
- Linked Wiki references use descriptive titles and retain keyboard focus
  styling.
- Internal item actions remain buttons when navigation is available.
- Mobile layouts avoid page-level horizontal overflow.
- The article loading, error, retry, and canonical-link states remain intact.

## Error Handling

- Missing or malformed pilot Wiki sections fail export with the page ID and
  section name.
- Invalid optional normalized JSON fails only the selected modal article state,
  following the existing detail-parser behavior.
- Unresolved Wiki references render their title and canonical link without an
  invented internal ID or translation.
- Empty optional fields are omitted or represented as null consistently.
- Existing atomic export behavior prevents a partial pilot detail file.

## Testing

Tests follow red-green-refactor cycles and cover:

- parsing all 10 Nightmare Fuel Drop table rows from a realistic fixture;
- parsing all 30 Nightmare Fuel Usage recipes in source order;
- default ingredient amounts, DLC, character, station, note, and result fields;
- selected mapping resolution and unresolved reference behavior;
- export allowlisting only page `210449`;
- removal of Drop table and Usage HTML without removing Trivia or Gallery;
- strict frontend validation of the optional normalized contract;
- removal of Related pages and Technical information from modal details;
- rendering Drop table and Usage regions with exact row counts and key values;
- unchanged loading, retry, canonical-link, focus, recipe, and mobile behavior.

Final verification includes focused Python and Vitest suites, deterministic
export, generated-file inspection for page `210449`, full Python tests, complete
frontend tests, ESLint, extraction validation, production build, and desktop
and mobile browser checks.

