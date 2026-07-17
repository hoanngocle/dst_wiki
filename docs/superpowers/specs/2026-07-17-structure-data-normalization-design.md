# Structure Data Normalization Design

## Objective

Normalize every published structure across base-game Don't Starve Together and
the Tu Tiên mods so the detail modal exposes the structure's complete verified
gameplay data. The pipeline must also explain every missing icon, retain real
naturally spawned structures, remove invalid technical prefabs from the public
catalog, and fold all Wiki-backed records into the DST source group.

## Scope

This change covers every `structure` item exported to `public/data/items.json`
for the `base_game` and `tu_tien` namespaces. It extends the crawler/import and
game/mod extraction pipeline only where structure-specific facts are needed.
Existing item, pill, mob, boss, character, and effect detail behavior remains
unchanged.

Wiki remains a provenance and article source. It is no longer a user-facing
source group. Wiki-only records are published as DST records, including pages
that cannot be mapped to a concrete game prefab, provided the page is verified
as a real structure. Invalid, non-entity, and technical prefab rows are removed
from the public payload but remain auditable in the database or generated
report.

## Current Baseline

The current payload contains 290 structures:

- 229 DST structures, including 74 without a published icon;
- 61 Tu Tiên structures, including 11 without a published icon;
- 8 of the 74 iconless DST rows have a recipe;
- 66 iconless DST rows have no recipe;
- all 11 iconless Tu Tiên rows currently have no recipe.

The current base-game classifier can publish a module filename as if it were a
standalone prefab. This allows wrapper modules, prefab families, spawners, and
other technical implementation units to appear as user-facing structures. The
current source filter also treats any item with Wiki metadata as belonging to a
separate Wiki group, even when the item is a mapped DST prefab.

## Approaches Considered

### Dedicated structure detail contract — selected

Add a `structureDetails` contract alongside the existing generic item fields.
The contract can express construction, origin, functions, station outputs,
destruction, visuals, and evidence without overloading the Tu Tiên item detail
schema. This gives the modal predictable sections and makes completeness
machine-verifiable.

### Extend the existing generic `details` contract

This minimizes top-level fields but conflates item usage/drop semantics with
structure origin, destruction, production, and station behavior. It would make
validation and rendering increasingly conditional and is rejected.

### Publish only the sanitized Wiki article

This preserves prose but cannot reliably power structured modal sections,
cross-item navigation, completeness gates, or icon audit decisions. It is
rejected.

## Public Data Contract

Every published structure receives a `structureDetails` object. Each major
section has a status of `known`, `none`, or `unknown`:

- `known`: verified facts are present;
- `none`: the source proves the concept does not apply;
- `unknown`: the available sources do not prove either facts or absence.

The contract contains:

### Identity and provenance

- namespace, prefab identifier, Vietnamese and English display names;
- DLC, event, character, or world-mode restrictions when present;
- canonical Wiki URL and imported revision metadata when available;
- evidence references for every normalized fact group.

### Visual

- selected display image and its kind: `inventory_icon`, `wiki_image`, or
  `world_asset`;
- all verified alternative images suitable for the modal;
- a status and explicit reason when no display image exists.

Visual resolution priority is inventory/build-menu icon, Wiki primary image,
then a deterministic game/mod world asset. The pipeline never invents an icon
or silently substitutes an unrelated texture.

### Origin

- whether the structure is craftable or naturally spawned;
- biome, set piece, world-generation source, mob, boss, event, or other
  spawner;
- spawn conditions, respawn timing, and renewability when available;
- a Vietnamese note for real naturally spawned structures that have no
  inventory icon and no construction recipe.

### Construction

- output count and complete ingredient list;
- tech, filter, station, builder tag, character, DLC, and event restrictions;
- placement or deployment notes when the source provides them.

Craftable structures must have `construction.status = known`. A verified
naturally spawned, non-craftable structure has `construction.status = none`,
not `unknown`.

### Functions

Functions are represented as typed facts with a stable key, localized label,
display value, optional unit/context, related entity references, and evidence.
This supports heterogeneous structure behavior without a sparse universal
column set. Examples include storage slots, light and heat, fuel inputs,
production outputs and cycle time, spawning, crafting/prototyping, farming,
teleportation, protection radius, activation conditions, and cooldowns.

Every real published structure must have either at least one known function or
an explicit `none`/`unknown` status with a reason. The complete sanitized Wiki
article remains available as prose fallback and source context.

### Craftables

For a structure that acts as a prototyper or crafting station, the payload lists
every verified item or structure craftable through it. Each result contains a
resolvable item reference, output count, ingredients, station/tech/filter
requirements, restrictions, note, and evidence.

DST station outputs are derived from canonical game recipes first and enriched
from imported Wiki recipe/station data. Tu Tiên outputs are derived from mod
recipes and runtime/static restrictions. Wiki does not override a conflicting
higher-confidence game or mod fact.

### Destruction and drops

- whether the structure can be destroyed;
- required action/tool such as hammering or mining;
- work amount, durability, or hit points when available;
- burn behavior when relevant;
- every verified drop with quantity, chance, conditions, and item reference;
- reset, regeneration, or respawn behavior following destruction.

Indestructible structures use `destruction.status = none` with an explicit
indestructible flag and supporting evidence. Missing parsing support remains
`unknown`; it must not be presented as “no drops.”

## Structure Verification and Icon Audit

The pipeline emits a deterministic generated report covering every structure
that originally lacked a selected icon. Each row contains:

- namespace and prefab/page identity;
- names and canonical Wiki URL if known;
- whether it has a construction recipe;
- available inventory, Wiki, and world assets;
- classification, reason, evidence, and export action.

Allowed classifications are:

- `natural_structure`: verified world structure with no construction recipe;
- `craftable_missing_asset`: verified craftable structure whose icon mapping is
  broken or absent;
- `world_asset_only`: verified structure represented only by a world asset;
- `technical_prefab`: wrapper, prefab family, spawner, helper, FX, classified
  state, or other implementation-only entity;
- `unverified`: no exact structure identity can be established after the
  required source and one-pass Wiki lookup.

The audit action is one of `keep`, `repair`, or `exclude`:

- `natural_structure` and `world_asset_only` are kept with an explanatory note;
- `craftable_missing_asset` must resolve a valid display asset before the
  pipeline can claim complete visual coverage;
- `technical_prefab` and unresolved `unverified` rows are excluded from the
  public payload.

Exclusion applies only to published catalog/search records. Raw extraction,
SQLite provenance, and audit evidence remain intact.

## Wiki Lookup Policy

For an otherwise valid structure without an imported Wiki mapping, the audit
performs one deterministic lookup using, in order:

1. exact English display name plus DST;
2. exact prefab/spawn code;
3. a known alias from canonical game/mod source.

An exact canonical page or an unambiguous page containing the prefab/spawn code
can be imported and mapped. Ambiguous search results do not establish identity.
If neither local source nor the one-pass lookup verifies a real structure, the
row is classified `unverified` and excluded.

## Data Flow

1. Extract canonical DST and Tu Tiên entities, recipes, restrictions, assets,
   relations, stats, and runtime coverage as today.
2. Import Wiki pages, recipes, images, revision metadata, and
   structure-specific normalized facts into SQLite.
3. Verify candidate structures against exact prefab declarations and
   player-visible source evidence instead of treating every prefab module stem
   as a publishable entity.
4. Build reverse station mappings from recipe tech/filter/station restrictions.
5. Resolve visuals using the defined priority and create the icon audit.
6. Assemble `structureDetails`, merge Wiki enrichment without overwriting
   higher-confidence canonical facts, and exclude invalid candidates.
7. Publish all Wiki-backed and Wiki-only valid records as DST items.
8. Validate completeness and write deterministic JSON/public assets.

## Source Group Behavior

The UI source filter contains only `all`, `base_game`, and `tu_tien`, displayed
as “Tất cả,” “DST,” and “Tu Tiên.”

- Every mapped DST item belongs to `base_game`, whether or not it has Wiki
  metadata.
- Every valid Wiki-only item is also exposed through the DST group.
- Tu Tiên items remain in `tu_tien`.
- Wiki links, articles, revision data, and evidence remain accessible from the
  item modal.
- No “Wiki” source filter or source badge remains.

Search continues to match Wiki titles and article-derived metadata where useful;
removing the group does not remove Wiki content.

## Modal Behavior

The structure modal renders, in order:

1. visual, identity, namespace, and prefab;
2. summary and availability/origin;
3. construction recipe or verified naturally spawned note;
4. functions;
5. items craftable through the structure;
6. destruction and drops;
7. sanitized Wiki article and external canonical link when available.

Empty verified sections are omitted or shown as a concise “not applicable”
state. Unknown sections are clearly marked as not yet verified and are never
silently rendered as empty.

## Error Handling and Quality Gates

- Invalid structure detail shapes fail export before replacing public output.
- A craftable structure without a resolved visual produces a hard validation
  failure until repaired or explicitly reclassified with evidence.
- A station recipe referencing an unresolved published result or ingredient is
  a hard validation failure.
- Audit rows must cover the complete pre-resolution missing-icon set exactly
  once.
- Every excluded structure candidate must have a classification, reason, and
  evidence.
- Wiki/API failures preserve prior successful crawl state and leave the fact
  `unknown`; they do not manufacture `none`.
- Re-running import/export from unchanged inputs produces byte-stable public
  JSON and audit reports.

## Testing Strategy

Python unit tests cover:

- parsing structure origin, visual, construction, function, station output,
  destruction, and drop variants from representative Wiki fixtures;
- deriving reverse crafting-station outputs from DST and Tu Tiên recipe
  restrictions;
- visual priority and missing-icon classifications;
- keeping naturally spawned structures while excluding technical prefabs;
- one-pass lookup matching and ambiguity rejection;
- SQLite import/export round trips and deterministic audit output;
- validation failures for incomplete craftable structures and unresolved
  references.

TypeScript and React tests cover:

- parsing the structure detail contract and rejecting invalid status/data
  combinations;
- source filters containing only All, DST, and Tu Tiên;
- every Wiki-backed and Wiki-only valid item appearing under DST;
- structure modal states for craftable, naturally spawned, station,
  indestructible, missing-image, and unknown data cases;
- click-through from station craftables and drop references to item modals;
- Wiki article and canonical link behavior after removal of the Wiki group.

Final verification runs focused Python and React tests, the full extraction test
suite, Vitest, lint, build, export validation, SQLite foreign-key checks, report
coverage checks, and `git diff --check`.

## Acceptance Criteria

1. Every published DST and Tu Tiên structure has a valid `structureDetails`
   object and renders normally in the detail modal.
2. Crafting/prototyping structures list all verified items craftable through
   them with resolvable references.
3. Every originally iconless structure appears exactly once in the audit report
   with an evidence-backed reason and action.
4. Real naturally spawned, non-craftable structures remain published with a
   clear note; technical or unverified rows do not appear publicly.
5. Craftable structures have a resolved display visual or fail validation.
6. Source filtering exposes only All, DST, and Tu Tiên, and all valid Wiki
   records appear under DST.
7. Wiki provenance and article content remain available without a Wiki group.
8. Generated outputs are deterministic, references are valid, SQLite reports no
   foreign-key errors, and all required tests and quality gates pass.
