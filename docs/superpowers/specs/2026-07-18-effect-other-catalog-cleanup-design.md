# Effect and Other Catalog Cleanup Design

## Objective

Remove non-user-facing records from the public **Hiệu ứng** (`effect`) and
**Khác** (`other`) catalog groups without deleting a real item, entity, recipe
dependency, gameplay effect, or other referenced record. Every exclusion must
be deterministic, explainable, and listed in a generated audit report.

## Scope

The cleanup applies to `effect` and `other` records published through
`public/data/items.json` for both `base_game` and `tu_tien`. It changes the
exported search/catalog payload and its validation. Raw extraction records,
`public/data/catalog.json`, crawler data, and SQLite provenance remain intact so
an excluded prefab can still be investigated later.

The current payload contains 1,466 records in scope: 698 `effect` records and
768 `other` records. The initial conservative audit found 539 records with no
display image, real display text, recipe, Wiki mapping, or detail data. Two of
those records still contain gameplay stats and must be retained. The remaining
537 records currently satisfy the exclusion rule.

## Approaches Considered

### Rule-based export audit — selected

Evaluate every `effect` and `other` record from canonical catalog facts, final
item details, and reverse references. Publish a deterministic report containing
the decision and evidence, then exclude only records for which every useful
signal is absent. This handles the current 537 records and future crawler runs
without maintaining a large hand-written identifier list.

### Hard-coded exclusion identifiers

Adding all 537 identifiers to `NON_ITEM_PREFAB_IDS` would reproduce today's
result, but it would become stale as game data changes and would not explain why
new technical prefabs appear. This approach is rejected.

### Frontend-only hiding

Filtering the two tabs in React would leave the records in the public payload,
search indexes, counts, and downstream consumers. It would also provide no
generated audit trail. This approach is rejected.

## Exclusion Contract

A record is eligible for exclusion only when its category is `effect` or
`other` and **all** of the following are true.

### No presentation value

- `sprite` is absent;
- Vietnamese and English descriptions are absent;
- English display name and crafting note are absent;
- the selected display name is only the raw `prefabId` fallback;
- no Wiki mapping or Wiki detail URL exists.

A localized or human-readable name counts as text even when the description is
missing. This deliberately keeps records such as Abigail, bosses, structures,
and world objects that are currently misclassified but still have recognizable
player-facing identity.

### No direct gameplay value

- the entity is not marked as an inventory item;
- it has no recipe, acquisition, stat, effect, or relation facts in the
  canonical catalog;
- it has no normalized item recipe;
- it has no known drop source, usage recipe, or usage effect;
- it has no mob, character, or structure detail payload.

The two currently blank-looking records with gameplay stats are retained by
this rule. Unknown detail status is not itself evidence of usefulness, but a
fact inside any detail section is.

### No reverse dependency

The record is not referenced by another published or canonical entity as:

- a recipe ingredient or result;
- an acquisition/drop source or result;
- a relation target;
- a usage recipe result or ingredient;
- a structure construction ingredient, station output, or destruction drop;
- a mob loot result;
- a normalized Wiki drop or usage reference.

Any resolvable reverse reference forces `keep`, even if the record has no image
or text of its own. The exporter must calculate the complete reference set
before filtering so exclusions cannot create broken modal links or recipes.

## Audit Report

The export writes `data/generated/effect-other-audit.json` using a stable schema
and deterministic ordering. The report covers every pre-filter `effect` and
`other` record exactly once and contains:

- item ID, namespace, prefab ID, category, and display name;
- `keep` or `exclude` action;
- presentation signals: image, meaningful text, Wiki mapping;
- direct gameplay signals: inventory status, recipe, acquisition, stats,
  effects, relations, and typed detail facts;
- reverse-reference count and the referencing IDs/kinds;
- a stable reason code and concise Vietnamese reason.

Current excluded IDs are the rows with `action = "exclude"`. This report is the
requested full list; the final implementation summary also states totals by
namespace and category.

## Export Flow

1. Build canonical entities, assets, recipes, detail sections, and Wiki
   enrichment as today.
2. Assemble the full candidate item list before removing any record.
3. Build typed reverse-reference indexes from canonical and final normalized
   data.
4. Evaluate every `effect` and `other` item against the exclusion contract.
5. Write the complete audit report atomically.
6. Remove only `exclude` rows from the published item list.
7. Link recipe/detail references and run validation against the filtered list.
8. Write `public/data/items.json` and other generated artifacts atomically.

The existing raw catalog is not rewritten. Re-running the exporter with
unchanged inputs must produce byte-identical item and audit JSON.

## Validation and Failure Handling

Export fails before replacing public output when:

- an in-scope item is missing from the audit report or appears more than once;
- an excluded item has any positive presentation, gameplay, or reference
  signal;
- a published recipe/detail/reference points to an excluded ID;
- the report decision disagrees with the actual published item set;
- a report entry has an unknown action or reason code.

Missing optional source data is treated conservatively. If the exporter cannot
prove the absence of a dependency or cannot parse a relevant fact group, the
record is kept rather than deleted.

## Frontend Behavior

The Hiệu ứng and Khác filters remain available. Their counts and results come
from the cleaned payload, so excluded technical prefabs disappear from search,
filter counts, and detail navigation without adding a second UI-only blacklist.
The existing `_item` counterpart preference remains unchanged.

The current defensive `_fx` curation may remain temporarily, but correctness
must not depend on it: every empty `_fx` record covered by this cleanup is
already absent from the exported payload and listed in the audit report.

## Testing Strategy

Python tests are written first and must demonstrate the following failures
before implementation:

- an entirely blank, unreferenced `effect` or `other` record is excluded;
- a candidate with a sprite, meaningful name, description, Wiki mapping,
  recipe, stat, effect, acquisition, relation, typed detail, or inventory flag
  is retained;
- an otherwise blank candidate referenced by another entity is retained;
- the audit covers all in-scope inputs once with stable ordering and reasons;
- unchanged input produces deterministic output;
- validation rejects an excluded-but-referenced record.

Existing TypeScript tests continue to prove that parsing, category filters,
result counts, modal navigation, and `_item` counterpart selection work with the
cleaned payload. The complete Python, Vitest, TypeScript, ESLint, export, and
data-validation suites must pass before completion.

## Acceptance Criteria

- The current 537 proven-empty records are absent from
  `public/data/items.json` after regeneration.
- Both currently blank-looking records with gameplay stats remain published.
- No retained item loses a recipe, usage, drop, structure, mob, Wiki, or other
  resolvable relationship.
- `data/generated/effect-other-audit.json` lists every evaluated item and gives
  an evidence-backed reason for every exclusion.
- The Hiệu ứng and Khác tabs contain only retained records and show correct
  counts.
- Raw catalog and provenance data remain available.
- Export and audit output are deterministic and all validation suites pass.
