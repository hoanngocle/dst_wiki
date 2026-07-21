# Mob and Boss Catalog Normalization Design

## Objective

Publish complete, evidence-backed detail data for every player-facing Mob and
Boss in base DST and Tu Tiên. Each canonical creature record must expose its
identity, variants or phases, appearance sources, combat/gameplay facts,
special mechanics, image, and every obtainable item with quantity, chance,
method, and condition.

The work also corrects category and grouping errors. In particular,
`alterguardian_phase3dead` must disappear from **Công trình** and be merged into
the canonical Celestial Champion Boss record as its post-defeat, mineable phase.

## Scope

The normalization covers public `mob` and `boss` records from both
`base_game` and `tu_tien`. It changes extraction, canonical grouping, Wiki
enrichment, the public item contract, validation, generated audit data, and the
shared Mob/Boss modal.

Raw Lua facts and provenance remain intact. Variant records hidden by grouping
remain traceable in the audit and canonical catalog even though they no longer
appear as duplicate search results.

The current public payload contains 161 `mob` records, including 105 base DST
and 56 Tu Tiên records. Only 15 currently have known loot, only 27 have a
sprite, and base DST Mob details are largely empty. Boss records use a separate
filter but share the same normalization contract.

## Approaches Considered

### Hybrid source, runtime, and Wiki normalization — selected

Use Lua/static extraction and runtime snapshots as gameplay sources, Wiki data
as descriptive and visual enrichment, and a small reviewed manifest only for
variant grouping or dynamic exceptions. This provides deterministic facts
without treating prose as the source of numeric gameplay truth.

### Manual JSON overrides

Hand-writing every Mob and drop would give immediate coverage but would be
large, difficult to review, and stale after game or mod updates. Overrides are
therefore limited to explicit grouping and irreducible exceptions.

### Wiki-only crawling

Wiki pages contain useful summaries and images, but page structure and wording
vary, variant pages are often combined, and exact runtime loot can differ from
prose. Wiki-only normalization is rejected as the canonical gameplay source.

## Canonical Identity and Grouping

Every public Mob or Boss has one canonical record. Closely related prefabs are
grouped only through explicit, reviewed group facts; display-name similarity
must never merge records automatically.

Each group defines:

- one existing prefab-backed canonical ID;
- member prefab IDs;
- a member role such as `phase`, `variant`, `summon`, or `post_defeat`;
- optional ordering and display label;
- whether a member remains independently searchable.

The Celestial Champion group uses `base_game:alterguardian_phase3` as its
canonical public record. Phase 1, phase 2, phase 3, and
`alterguardian_phase3dead` appear in its ordered phase list.
`alterguardian_phase3dead` is not published as a standalone structure or Mob.
Its mineable rewards are attached to the canonical Boss with the method
`mine_post_defeat`.

Bosses remain in the **Boss** filter and ordinary creatures remain in **Mob**.
Both use the same detail schema and UI renderer.

## Mob and Boss Detail Contract

The public item schema is versioned forward and gives every canonical Mob or
Boss a `mob` object with explicit section states and evidence.

### Identity and phases

- canonical prefab ID and category;
- ordered phases or variants with source prefab ID, label, role, and optional
  per-phase image;
- English and Vietnamese names and summary at item level;
- Wiki URL and local detail payload when resolved.

### Appearance

- `status`: `known`, `none`, or `unknown`;
- world/biome/event/boss-transition sources;
- spawn code or member prefab ID;
- renewable/respawn facts when proven;
- conditions and evidence.

Absence of evidence must not be rendered as `Không`. Unknown values remain
unknown in both JSON and the modal.

### Stats and mechanics

Stats include every supported numeric or displayable combat fact available
from source/runtime: maximum health, damage, planar damage, attack period,
attack and hit range, movement speeds, sanity aura, resistances, armor or
damage absorption, and phase-specific overrides.

Mechanics are structured facts rather than unlabelled prose where possible.
They cover phase transitions, special states, summons, enrage or transformation
conditions, targeting behavior, and other verified gameplay abilities. Facts
retain their source prefab and evidence.

### Obtainable items

Every reward entry contains:

- referenced item ID, name, and sprite;
- minimum and maximum quantity;
- chance when known;
- method: `kill`, `mine_post_defeat`, `harvest`, or `conditional`;
- source phase/variant;
- conditions, loot-table name, and evidence.

Duplicate static entries are aggregated only when item, method, source phase,
chance, and conditions match. Guaranteed entries and independent chance rolls
remain distinguishable. Items created directly by a reward callback, rather
than a `lootdropper`, are still included with their actual method and condition.

`lootStatus = none` is allowed only when the relevant source was successfully
observed or parsed and proves that no reward exists. Parse gaps must produce
`unknown`, never `none`.

## Extraction and Data Flow

1. Classify each returned prefab from its own constructor/body signals instead
   of assigning one category from the aggregate module source.
2. Extract Mob/Boss stats, tags, components, spawn relations, phase relations,
   and reward calls from base DST Lua and Tu Tiên source/runtime data.
3. Resolve static loot from `SetLoot`, `AddChanceLoot`, `AddRandomLoot`,
   `SetSharedLootTable`, and `SetChanceLootTable`.
4. Capture direct reward `SpawnPrefab` calls reached from death, work, harvest,
   or phase-completion callbacks with method and source-member evidence.
5. Resolve Wiki pages once for records missing mappings; use Wiki prose and
   assets for summaries, appearance notes, mechanics context, and images, not
   as an unqualified replacement for source facts.
6. Apply the reviewed grouping manifest and select canonical public records.
7. Merge member stats, mechanics, appearance, and rewards into canonical Mob
   details while preserving phase attribution.
8. Link reward items to published catalog entries and write deterministic JSON.
9. Generate a complete Mob/Boss audit before replacing public output.

## Audit Report

`data/generated/mob-boss-audit.json` covers every pre-group Mob/Boss candidate
and every member moved from another category. Each row records:

- original ID/category and final canonical ID/category;
- action: `keep`, `merge`, or `exclude`;
- grouping role and evidence;
- name, description, image, Wiki, appearance, stats, mechanics, and reward
  coverage;
- unresolved parser or reference reasons;
- a stable Vietnamese explanation.

A player-facing prefab is not deleted merely because it lacks a Wiki page or
inventory icon when game/mod source proves its identity or gameplay role.
Technical wrappers with no independent identity, facts, visual, Wiki mapping,
or references may be excluded, but only with an audit reason.

## Celestial Champion Correction

The current error has four causes that this design addresses:

- module classification treats any `workable` prefab as a structure;
- the structure visual audit labels a named record `natural_structure` without
  proving natural spawning;
- missing origin data defaults to `naturallySpawned: false` and renders as a
  verified `Không`;
- base extraction does not resolve the shared loot table used by
  `alterguardian_phase3dead`.

After normalization, the standalone structure entry is absent. The Celestial
Champion Boss record lists its combat phases and a post-defeat phase. Mining
the defeated form with a pickaxe exposes the shared loot-table rewards plus the
altar-piece and upgraded Moon Rock Seed rewards created by the work callback,
each with its actual chance and condition.

## Frontend Behavior

The Mob and Boss filters remain separate. Both categories render the same
sections:

- overview and image;
- appearance/source;
- phases or variants;
- stats;
- mechanics;
- obtainable items grouped or labelled by method and source phase.

Reward references remain clickable. Unknown sections show an explicit
unverified status, and conditional or post-defeat rewards must never be labelled
as ordinary guaranteed kill drops.

## Validation and Failure Handling

Export or validation hard-fails when:

- a grouped member is published independently when the manifest says it is
  hidden;
- a member belongs to multiple canonical groups;
- a `structure` record is merged into Mob/Boss but remains in structure output
  or the structure audit;
- a known reward references a missing public item;
- a known loot section is empty;
- chance, quantity, method, or source phase is invalid;
- a shared loot table is referenced but unresolved without an explicit
  `unknown` reason;
- an unknown appearance value is serialized or rendered as a verified `false`;
- the Mob/Boss audit and public output disagree.

Incomplete optional Wiki data is conservative: source-proven Mob/Boss records
remain public with `unknown` enrichment fields. Export output and audit order
must be deterministic.

## Testing Strategy

Tests are written before implementation and cover:

- per-prefab classification in a multi-prefab Lua module;
- static, chance, random, shared-table, and direct callback rewards;
- reward aggregation without multiplying chance incorrectly;
- phase/variant grouping and hidden member behavior;
- Celestial Champion phase and post-defeat reward normalization;
- base DST and Tu Tiên Mob/Boss export;
- parser rejection of malformed phase, appearance, stat, mechanic, and reward
  contracts;
- shared Mob/Boss modal rendering and navigation;
- audit completeness, consistency, and deterministic output;
- export/validation hard failures for broken references or contradictory
  status.

The complete Python, Vitest, TypeScript, ESLint, export, and catalog validation
suites must pass before completion.

## Acceptance Criteria

- All retained DST and Tu Tiên Mob/Boss records have a valid `mob` detail
  object with explicit section states.
- Every stat, mechanic, appearance source, and obtainable item supported by the
  available source/runtime/Wiki inputs is published with provenance.
- `alterguardian_phase3dead` is absent from Công trình and standalone search.
- Celestial Champion contains the merged phases and correctly labelled
  post-defeat mining rewards.
- Boss details render for base DST as well as Tu Tiên; Mob details are no longer
  gated to the Tu Tiên namespace.
- No known reward points to a missing item.
- `data/generated/mob-boss-audit.json` explains every keep, merge, or exclusion.
- Generated artifacts are deterministic and every required validation suite
  passes.
