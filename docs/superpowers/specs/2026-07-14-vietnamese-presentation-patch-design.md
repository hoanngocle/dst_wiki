# Vietnamese Presentation Patch Design

## Goal

Fill every Tu Tiên inventory item missing a Vietnamese display name and normalize cultivation terminology used by web-facing names, descriptions, recipes, and effects. Preserve character quotes unchanged. The web artifacts are the primary deliverable.

## Scope

- Translate all prefab IDs currently listed by `coverage.json.missing_inventory_names`.
- Use a Hán–Việt cultivation style consistent with existing terms such as `Linh Thạch`, `Pháp Bảo`, and `Hạ/Trung/Thượng/Cực Phẩm`.
- Correct clear mistranslations and canonicalize synonymous terminology in display fields.
- Do not rewrite character quotes or invent a translation when the original label cannot be recovered.
- Do not edit any file inside the three source mod directories.
- Do not use a wiki, crawler, or website as a translation source.

## Architecture

The change is a deterministic post-build presentation patch rather than a new source extractor.

1. `data/manual/vi_presentation_patch.json` stores complete approved overrides. Each row includes prefab ID, Vietnamese value, original runtime label or other local evidence, and a short rationale.
2. `data/manual/vi_glossary.json` stores canonical terms, disallowed variants, field scope, and replacement boundaries.
3. `tools/extract/postbuild_vi.py` patches normalized SQLite display columns after `build-db`, records an audit table, and leaves raw fact/evidence tables unchanged.
4. The normal JSON exporter runs after the patch, so `catalog.json` and SQLite remain consistent.
5. Validation writes `translation_audit.json` and fails if a required item remains unnamed, an override lacks evidence, a prohibited term remains in scoped display text, or a character quote changes.

The `all` order becomes:

`extract-static -> import-runtime -> enrich-base -> build-db -> patch-vi -> export -> validate`

## Recovering Original Labels

Many missing rows are packed skin prefabs with no literal English or Vietnamese source text. A bounded runtime label snapshot reads only `STRINGS.NAMES` for the existing Tu Tiên target allowlist. These labels are translation evidence used to author the manual patch; they are not automatically treated as Vietnamese and do not change gameplay facts.

Evidence preference is:

1. Exact runtime `STRINGS.NAMES` label.
2. Exact local skin-parent or recipe metadata.
3. Existing local translation text.

If none is available, the row remains in the translation review report rather than receiving a guessed poetic name. Completion requires resolving that report before delivery.

## Terminology Rules

The glossary applies only to Vietnamese names, descriptions, recipe display text, and non-quote effect display text. Rules are context-aware rather than unrestricted substring replacements.

Initial canonical vocabulary includes:

- `Linh Thạch`
- `Pháp Bảo`
- `Linh Lực`
- `Sát Thương`
- `Hộ Giáp`
- `Độ Bền`
- `Hồi Chiêu`
- `Sinh Lực`
- `Tinh Thần`
- `Hạ Phẩm`, `Trung Phẩm`, `Thượng Phẩm`, `Cực Phẩm`

The audit may expand this list after inspecting all current Vietnamese display text. Proper names and poetic skin titles use Hán–Việt readings when the original Chinese label is available.

## SQLite and JSON Behavior

- Patch only presentation values: entity Vietnamese name/description and approved non-quote effect display values.
- Keep all original evidence and conflicts untouched.
- Add deterministic patch audit rows containing field, old value, new value, patch ID, and evidence label.
- Re-export `public/data/catalog.json` from patched SQLite.
- Do not patch `assets.json` unless a display label is added to its schema later.

## Validation and Completion

Automated checks must prove:

- `missing_inventory_names` is empty.
- Every original missing prefab has a non-empty Vietnamese name in SQLite and `catalog.json`.
- SQLite and JSON values match.
- No prohibited glossary variant remains in scoped fields.
- Character quote values are byte-identical before and after the patch.
- Applying the patch twice is idempotent.
- Running `cli all` twice produces identical SQLite, catalog, coverage, and translation-audit artifacts.
- Foreign keys, archive checksums, runtime target coverage, and existing pipeline tests still pass.

## Generated Files for the Web

- `public/data/catalog.json`: patched names and descriptions used by the list/detail UI.
- `public/data/assets.json`: unchanged asset mapping.
- `data/generated/wiki.sqlite`: patched query database.
- `data/generated/translation_audit.json`: replacement and unresolved-review report.

