# Wiki Data Import Design

## Goal

Import the completed selective crawl from
`data/crawled/dontstarve-items` into `data/generated/wiki.sqlite`, map wiki
pages to existing base-game entities where the evidence is unambiguous, and
make every crawled page discoverable from the existing item list.

The current frontend contract remains build-time JSON. SQLite is the canonical
audit and mapping store; the Next.js application continues to read compact,
deterministic files from `public/data`.

## Chosen architecture

Extend the existing SQLite database and export pipeline instead of creating a
second database or opening SQLite at application runtime.

The flow is:

1. `import-wiki` reads the crawler manifest and JSONL datasets.
2. It validates and transactionally replaces the wiki-owned tables.
3. It maps unambiguous wiki pages to existing `base_game` entities.
4. `export` merges mapped wiki data into existing list entries and emits
   standalone entries for unmapped pages.
5. List data stays compact in `public/data/items.json`; large detail payloads
   are emitted per page under `public/data/wiki/pages`.
6. Referenced original images are copied to content-addressed paths under
   `public/assets/wiki`.

Re-importing an identical crawl is idempotent and produces byte-stable exports.

## Database model

The importer adds the following wiki-owned tables:

- `wiki_import_runs`: manifest checksum, source path, timestamps, status, and
  imported counts.
- `wiki_pages`: MediaWiki page ID, title, display title, canonical URL,
  revision metadata, HTML, wikitext, plain text, categories, redirect target,
  and fetch metadata.
- `wiki_recipes`: recipe identity, source page, result title, source template,
  station, tab, tier, character, DLC, variant, and note.
- `wiki_recipe_ingredients`: ordered ingredient title and numeric amount.
- `wiki_images`: MediaWiki file identity, original URL, MIME/size/checksum,
  crawler-local path, and published path.
- `wiki_entity_mappings`: page-to-entity mapping, method, confidence, and
  evidence. A page has at most one selected mapping.

Foreign keys are enabled and checked before commit. JSON fields are stored in a
canonical serialized form so exports remain deterministic.

## Mapping policy

Mapping never guesses. Candidates are evaluated in this order:

1. An infobox spawn code exactly matches an existing base-game prefab ID.
2. A normalized wiki or infobox English name uniquely matches an existing
   base-game English name.
3. A canonical alias, including `/DST` and recognized cooked/variant names,
   resolves to exactly one valid entity.

Ambiguous and unmatched pages remain standalone wiki list entries. Every
crawled page is stored even when it cannot be mapped.

For mapped pages, the existing game entity remains canonical. Wiki data fills
missing descriptions, sprites, recipes, categories, and detail content without
overwriting higher-confidence extracted game facts.

## Frontend contract

Existing mapped entries keep their stable IDs, such as
`base_game:fish_raw_small`. Standalone pages use `wiki:<page_id>` and retain the
`base_game` namespace so they appear in the current DST filter.

Compact item entries gain optional wiki metadata containing page ID, title,
canonical URL, categories, mapping state, and detail payload URL. Search covers
these fields and recipe ingredient names.

The exporter uses a suitable original wiki image when no game sprite is
available. Content-addressed filenames avoid collisions and allow safe
re-export. Full sanitized page detail is stored separately at
`public/data/wiki/pages/<page_id>.json` so the initial list payload does not
contain all article HTML.

Recipe quantities remain numeric and may be fractional. Existing integer
recipes remain unchanged.

## Commands and lifecycle

The public commands are:

```bash
python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export
```

`import-wiki` defaults to `data/crawled/dontstarve-items` and
`data/generated/wiki.sqlite`, with explicit CLI overrides for testing and
recovery. Rebuilding the base database must be followed by `import-wiki`; the
combined pipeline will run the stages in that order.

## Failure handling

- Validate the manifest and required JSONL inputs before mutating the database.
- Run schema creation and import in one SQLite transaction.
- Reject duplicate primary keys, missing page references, malformed revisions,
  invalid ingredient amounts, and missing referenced local images.
- Keep the prior successful wiki tables intact when import fails.
- Write JSON and copied assets through temporary paths followed by atomic
  replacement.
- Report imported, mapped, unmatched, recipe, ingredient, and image counts.

## Verification

Automated tests cover schema creation, validation, mapping precedence,
ambiguity handling, merge behavior, fractional recipes, image publication,
detail export, deterministic reruns, and CLI defaults.

The completed import must demonstrate:

- all 1,570 crawled pages are stored;
- all 1,444 recipes and their ingredients have valid parents;
- list item IDs are unique;
- every exported image reference exists;
- rerunning import and export produces the same logical result;
- Python tests, frontend tests, and the Next.js production build pass.
