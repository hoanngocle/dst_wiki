# Vietnamese Presentation Patch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Translate every currently unnamed Tu Tiên inventory item into consistent Hán–Việt Vietnamese and apply deterministic terminology corrections to the SQLite/JSON presentation layer.

**Architecture:** A bounded runtime snapshot supplies original labels for packed prefabs. A tracked manual patch and glossary update normalized SQLite after `build-db`; the existing exporter then produces matching web JSON. Raw source facts and character quotes remain unchanged, while a deterministic audit records every presentation replacement.

**Tech Stack:** Python 3.9 standard library, DST Lua runtime probe, SQLite 3, JSON, `unittest`.

## Global Constraints

- Do not modify files under `mod/3721846643`, `mod/3721859355`, or `mod/3731181944`.
- Do not crawl, scrape, or import data from any wiki or website.
- Use Hán–Việt cultivation terminology consistent with `Linh Thạch`, `Pháp Bảo`, and `Hạ/Trung/Thượng/Cực Phẩm`.
- Normalize names, descriptions, recipe display text, and non-quote effects; preserve character quotes byte-for-byte.
- Correct clear mistranslations; do not invent an ambiguous poetic name without local evidence.
- Patch SQLite after `build-db`, then regenerate JSON so database and web data stay consistent.
- Preserve raw facts, evidence, conflicts, runtime coverage, dependency scope, and archive provenance.
- The patch must be idempotent and deterministic.
- No placeholder translations or partial output are acceptable.

---

## Planned File Map

| Path | Responsibility |
|---|---|
| `tools/runtime_mod/scripts/exporter.lua` | Snapshot original `STRINGS.NAMES` labels for the existing Tu Tiên target allowlist |
| `tools/extract/runtime_import.py` | Validate deterministic runtime label rows without treating them as Vietnamese facts |
| `tools/extract/postbuild_vi.py` | Validate and atomically apply the SQLite presentation patch and write the audit |
| `tools/extract/database.py` | Create the deterministic `presentation_patches` audit table |
| `tools/extract/cli.py` | Add `patch-vi` and insert it between `build-db` and `export` in `all` |
| `tools/extract/validate.py` | Validate translation coverage, glossary rules, audit integrity, and quote preservation |
| `data/manual/vi_presentation_patch.json` | Complete curated Vietnamese overrides and their local evidence |
| `data/manual/vi_glossary.json` | Canonical terms, prohibited variants, scopes, and exact replacement rules |
| `data/generated/translation_audit.json` | Deterministic applied/unresolved/glossary audit |
| `tests/extract/test_postbuild_vi.py` | Patch, glossary, idempotence, quote, and SQLite/JSON consistency tests |

---

### Task 1: Capture exact original runtime labels

**Files:**
- Modify: `tools/runtime_mod/scripts/exporter.lua`
- Modify: `tools/extract/runtime_import.py`
- Modify: `tests/extract/fixtures/runtime.json`
- Modify: `tests/extract/test_runtime_import.py`

**Interfaces:**
- Runtime payload adds `labels: [{prefab, key, available, value}]`, sorted by `prefab`.
- `load_runtime_payload(path) -> dict` validates that label prefab IDs equal the payload target set exactly and that every available label has a non-empty string value.
- Runtime labels are translation evidence only and do not emit `name` facts.

- [ ] **Step 1: Add failing schema and Lua-contract tests**

Add tests asserting this complete label row:

```python
{
    "prefab": "xd_test_sword",
    "key": "XD_TEST_SWORD",
    "available": True,
    "value": "测试剑",
}
```

Also reject duplicate labels, missing targets, extra base-game targets, empty available values, and unsorted rows. The Lua contract test must assert lookup by `STRINGS.NAMES[string.upper(prefab)]` and sorting before encoding.

- [ ] **Step 2: Run the focused tests and verify RED**

Run `python3 -m unittest tests.extract.test_runtime_import -v`.

Expected: failures because runtime schema v2 does not yet contain or validate `labels`.

- [ ] **Step 3: Implement deterministic Lua label rows**

```lua
local function LabelRows(ids)
    local rows = {}
    for _, prefab in ipairs(ids) do
        local key = string.upper(prefab)
        local value = STRINGS and STRINGS.NAMES and STRINGS.NAMES[key] or nil
        table.insert(rows, {
            prefab = prefab,
            key = key,
            available = type(value) == "string" and value ~= "",
            value = type(value) == "string" and value or false,
        })
    end
    return rows
end
```

Include `labels = LabelRows(ids)` in the schema-v2 payload. Do not export the full DST registry.

- [ ] **Step 4: Implement strict Python validation**

Validate keys, types, uniqueness, sort order, exact equality with `targets`, and `available/value` consistency before importing runtime facts. Keep labels in raw runtime data only.

- [ ] **Step 5: Run tests and an isolated runtime probe twice**

Run focused and full tests. Run the dedicated server with the existing isolated workspace/cleanup rules. Require byte-identical outputs, one label per target, unchanged mod hashes, and no temporary installed mods.

- [ ] **Step 6: Commit**

```bash
git add tools/runtime_mod/scripts/exporter.lua tools/extract/runtime_import.py tests/extract/fixtures/runtime.json tests/extract/test_runtime_import.py
git commit -m "feat: capture Tu Tien runtime labels"
```

---

### Task 2: Build the deterministic post-build patch engine

**Files:**
- Create: `tools/extract/postbuild_vi.py`
- Modify: `tools/extract/database.py`
- Create: `tests/extract/test_postbuild_vi.py`

**Interfaces:**
- `load_patch(path: Path) -> ViPresentationPatch`
- `load_glossary(path: Path) -> ViGlossary`
- `apply_vi_patch(database: Path, patch: Path, glossary: Path, runtime: Path, audit: Path) -> dict`
- SQLite table `presentation_patches(patch_id, namespace, prefab_id, field_key, old_value, new_value, source_key, source_text, rationale)`.

- [ ] **Step 1: Write failing patch and idempotence tests**

Use a database containing an unnamed `tu_tien:xd_test_sword`, a description containing `tổn thương`, and a `character_quote`. Use this full override row:

```json
{
  "prefab_id": "xd_test_sword",
  "field": "name_vi",
  "value": "Thí Luyện Kiếm",
  "source_key": "XD_TEST_SWORD",
  "source_text": "测试剑",
  "rationale": "Hán–Việt cultivation rendering"
}
```

Assert the name changes, the description becomes canonical, quote bytes stay equal, audit rows retain old/new values, and a second application is byte/row identical.

- [ ] **Step 2: Run focused tests and verify RED**

Run `python3 -m unittest tests.extract.test_postbuild_vi -v`.

Expected: import error for `tools.extract.postbuild_vi`.

- [ ] **Step 3: Add the audit table**

```sql
CREATE TABLE presentation_patches (
  patch_id TEXT PRIMARY KEY,
  namespace TEXT NOT NULL,
  prefab_id TEXT NOT NULL,
  field_key TEXT NOT NULL,
  old_value TEXT,
  new_value TEXT NOT NULL,
  source_key TEXT NOT NULL,
  source_text TEXT NOT NULL,
  rationale TEXT NOT NULL,
  FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
)
```

The normal writer creates the empty table; the patch fills it transactionally.

- [ ] **Step 4: Implement strict patch and glossary contracts**

Reject duplicate `(prefab_id, field)`, unknown entities, unsupported fields, empty values/evidence, runtime source-key mismatches, glossary cycles, unrestricted substring rules, and attempts to patch `character_quote`. Glossary scopes are `name_vi`, `description_vi`, and `effect_display`.

- [ ] **Step 5: Apply atomically**

Copy SQLite to a unique sibling temporary file, enable foreign keys, apply overrides and boundary-aware glossary rules, replace audit rows deterministically, run `foreign_key_check`, commit, and atomically replace the database. Preserve the original and remove the temporary file on failure.

- [ ] **Step 6: Write deterministic audit JSON**

```json
{
  "schema_version": 1,
  "required_count": 1,
  "applied": [],
  "normalizations": [],
  "unresolved": [],
  "forbidden_variants": [],
  "quote_changes": []
}
```

Sort lists by semantic key and use atomic replacement without timestamps.

- [ ] **Step 7: Run focused/full tests and commit**

```bash
python3 -m unittest tests.extract.test_postbuild_vi -v
python3 -m unittest discover -s tests -v
git add tools/extract/postbuild_vi.py tools/extract/database.py tests/extract/test_postbuild_vi.py
git commit -m "feat: add Vietnamese presentation patch engine"
```

---

### Task 3: Curate all missing names and canonical terminology

**Files:**
- Create: `data/manual/vi_presentation_patch.json`
- Create: `data/manual/vi_glossary.json`
- Create: `data/manual/required_vi_names.json`
- Modify: `tests/extract/test_postbuild_vi.py`

**Interfaces:**
- `required_vi_names.json` freezes the exact approved pre-patch missing-name set.
- The patch contains exactly one `name_vi` override per required prefab plus evidence-backed corrections.
- The glossary contains approved canonical terms and exact prohibited variants.

- [ ] **Step 1: Freeze the required set**

Copy the sorted pre-patch `coverage.json.missing_inventory_names` array into `required_vi_names.json`. Test that it contains exactly 127 unique sorted IDs and matches the pre-patch SQL query.

- [ ] **Step 2: Produce the local evidence worksheet**

Join required IDs to `runtime.json.labels`, entity/recipe/relation rows, and exact asset or skin-parent metadata. Include prefab ID, original label, parent item, and related existing terminology. Use no network source.

- [ ] **Step 3: Write all 127 Hán–Việt overrides**

Add one complete `name_vi` override for every required prefab. Every row must have a non-empty Vietnamese value, exact source key/text, and concrete rationale. Proper names and poetic skin titles use Hán–Việt readings of the original label. ID-derived placeholders such as `Vật Phẩm <prefab_id>` are forbidden.

- [ ] **Step 4: Write context-aware glossary rules**

Audit all names, descriptions, and non-quote effects. The canonical baseline is:

```json
[
  "Linh Thạch",
  "Pháp Bảo",
  "Linh Lực",
  "Sát Thương",
  "Hộ Giáp",
  "Độ Bền",
  "Hồi Chiêu",
  "Sinh Lực",
  "Tinh Thần",
  "Hạ Phẩm",
  "Trung Phẩm",
  "Thượng Phẩm",
  "Cực Phẩm"
]
```

Only automate unambiguous, boundary-safe variants in declared scopes. Record ambiguous occurrences without replacement.

- [ ] **Step 5: Add completeness/no-placeholder tests**

Assert exact required-set equality, unique overrides, runtime/local evidence, non-empty Vietnamese, absence of prefab IDs and generic placeholder patterns, and exact SQLite values after applying to a copy of the real database.

- [ ] **Step 6: Commit**

```bash
git add data/manual/vi_presentation_patch.json data/manual/vi_glossary.json data/manual/required_vi_names.json tests/extract/test_postbuild_vi.py
git commit -m "data: translate Tu Tien inventory catalog"
```

---

### Task 4: Wire patching into `all` and publish web data

**Files:**
- Modify: `tools/extract/cli.py`
- Modify: `tools/extract/validate.py`
- Modify: `tests/extract/test_export_validate.py`
- Modify: `docs/data-extraction.md`
- Create: `data/generated/translation_audit.json`
- Modify: `data/generated/wiki.sqlite`
- Modify: `data/generated/coverage.json`
- Modify: `public/data/catalog.json`

**Interfaces:**
- CLI: `patch-vi --database --patch --glossary --runtime --audit`.
- `run_all()` order: `extract-static -> import-runtime -> enrich-base -> build-db -> patch-vi -> export -> validate`.
- `validate_catalog` emits `translation_errors` and adds them to `hard_failures`.

- [ ] **Step 1: Write failing CLI-order and validation tests**

Assert `all` calls patching after database build and before export. Assert hard failure for a required missing name, missing audit row, forbidden variant, source-label mismatch, or changed character quote.

- [ ] **Step 2: Run tests and verify RED**

Run `python3 -m unittest tests.extract.test_export_validate -v`.

Expected: failures because `patch-vi` and `translation_errors` are not wired.

- [ ] **Step 3: Add CLI stage and defaults**

```text
patch:    data/manual/vi_presentation_patch.json
glossary: data/manual/vi_glossary.json
runtime:  data/raw/runtime.json
audit:    data/generated/translation_audit.json
```

The standalone command patches its database. `all` applies defaults and exports only after patch success.

- [ ] **Step 4: Add hard translation validation**

Require an empty missing-name list, one matching audit row per required prefab, no unresolved/forbidden/quote-change rows, and no forbidden variant in scoped SQLite fields. Keep existing warnings visible.

- [ ] **Step 5: Update documentation**

Document `patch-vi`, its post-build position, tracked patch/glossary files, audit review, and persistence across `all`.

- [ ] **Step 6: Run the complete pipeline twice**

```bash
python3 -m unittest discover -s tests -v
python3 -m tools.extract.cli all
python3 -m tools.extract.cli all
python3 -m tools.extract.cli validate
```

Require identical SQLite/catalog/coverage/assets/audit hashes and:

```text
missing_inventory_names = []
translation_errors = []
foreign_key_errors = []
runtime_coverage_errors = []
hard_failures = []
```

Check all required IDs in SQLite and `catalog.json`, quote equality, and byte-identical mod directories.

- [ ] **Step 7: Commit**

```bash
git add tools/extract/cli.py tools/extract/validate.py tests/extract/test_export_validate.py docs/data-extraction.md data/generated/translation_audit.json data/generated/wiki.sqlite data/generated/coverage.json public/data/catalog.json
git commit -m "feat: publish curated Vietnamese catalog"
```

