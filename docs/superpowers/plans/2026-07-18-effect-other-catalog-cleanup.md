# Effect and Other Catalog Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deterministically audit every `effect` and `other` catalog record, remove the 537 records proven to have no presentation, gameplay, or dependency value, and publish a complete evidence-backed audit report.

**Architecture:** Add a focused Python audit module that evaluates final item data together with canonical catalog facts and typed reverse references. Integrate it after Wiki/structure enrichment but before writing `items.json`, then validate the audit against the filtered public payload and prefab coverage. Raw catalog and SQLite provenance remain unchanged.

**Tech Stack:** Python 3 standard library, JSON/SQLite extraction pipeline, `unittest`, TypeScript/Vitest frontend regression tests.

## Global Constraints

- Only `effect` and `other` records are eligible for this cleanup.
- Exclude a record only when every presentation, direct-gameplay, and reverse-reference signal is absent.
- A human-readable name is meaningful text; a raw `prefabId` fallback is not.
- Missing or unparseable optional evidence keeps the record conservatively.
- Raw catalog, crawler data, and SQLite provenance must not be deleted.
- Generated item and audit JSON must be deterministic and atomically written.
- The current 537 proven-empty records must be removed; the two blank-looking records with stats must remain.

---

### Task 1: Implement the pure audit decision engine

**Files:**
- Create: `tools/extract/effect_other_audit.py`
- Create: `tests/extract/test_effect_other_audit.py`

**Interfaces:**
- Consumes: final item dictionaries, canonical entity dictionaries, and optional Wiki detail dictionaries.
- Produces: `audit_effect_other_items(items, entities, wiki_details) -> tuple[list[dict[str, Any]], set[str]]`.
- Produces report rows with `id`, identity fields, `action`, `reasonCode`, `reason`, `signals`, and typed `references`.

- [ ] **Step 1: Write failing tests for empty exclusion and positive-signal retention**

```python
class EffectOtherAuditTests(unittest.TestCase):
    def test_excludes_only_blank_unreferenced_effect_or_other(self):
        rows, excluded = audit_effect_other_items(
            [blank_item("base_game:spark_helper", "effect")],
            [blank_entity("base_game:spark_helper", "effect")],
            {},
        )
        self.assertEqual(excluded, {"base_game:spark_helper"})
        self.assertEqual(rows[0]["action"], "exclude")
        self.assertEqual(rows[0]["reasonCode"], "empty_unreferenced")

    def test_keeps_each_positive_presentation_or_gameplay_signal(self):
        for field, value in (
            ("sprite", {"src": "/icon.png", "uv": {}}),
            ("name", "Readable Name"),
            ("description", "Useful description"),
            ("englishName", "English Name"),
            ("craftingNote", "Crafting note"),
            ("wiki", {"detailUrl": "/data/wiki/pages/1.json"}),
            ("recipe", {"outputCount": 1, "ingredients": []}),
        ):
            item = blank_item("base_game:kept", "other")
            item[field] = value
            rows, excluded = audit_effect_other_items(
                [item], [blank_entity("base_game:kept", "other")], {}
            )
            self.assertEqual(excluded, set(), field)
            self.assertEqual(rows[0]["action"], "keep", field)
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.extract.test_effect_other_audit -v`

Expected: import failure for `tools.extract.effect_other_audit` or missing `audit_effect_other_items`.

- [ ] **Step 3: Implement signal extraction and deterministic decisions**

```python
IN_SCOPE_CATEGORIES = frozenset({"effect", "other"})


def audit_effect_other_items(items, entities, wiki_details=None):
    entities_by_id = {
        entity["key"]: entity
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    references = _build_reverse_references(items, entities, wiki_details or {})
    rows = []
    excluded = set()
    for item in sorted(
        (value for value in items if value.get("category") in IN_SCOPE_CATEGORIES),
        key=lambda value: value["id"],
    ):
        entity = entities_by_id.get(item["id"], {})
        signals = _signals(item, entity)
        item_references = references.get(item["id"], [])
        if any(signals.values()):
            action, code = "keep", "positive_signal"
        elif item_references:
            action, code = "keep", "reverse_reference"
        else:
            action, code = "exclude", "empty_unreferenced"
            excluded.add(item["id"])
        rows.append(_row(item, action, code, signals, item_references))
    return rows, excluded
```

Implement `_signals` with booleans for sprite, meaningful text, Wiki mapping,
inventory flag, recipe, acquisition, stats, effects, relations, and typed item
details. Implement `_build_reverse_references` with stable `(source, kind)`
pairs for catalog recipe ingredients, acquisition sources, relation targets,
item recipe ingredients, usage recipes, structure recipes/drops, mob loot, and
Wiki `entityId` references.

- [ ] **Step 4: Add reverse-reference, stat retention, scope, and ordering tests**

```python
def test_keeps_blank_item_referenced_as_recipe_ingredient(self):
    source = blank_entity("base_game:tool", "item")
    source["recipes"] = [{
        "output_count": 1,
        "ingredients": [{"key": "base_game:helper", "amount": 1, "position": 0}],
    }]
    rows, excluded = audit_effect_other_items(
        [blank_item("base_game:helper", "other")],
        [source, blank_entity("base_game:helper", "other")],
        {},
    )
    self.assertEqual(excluded, set())
    self.assertEqual(rows[0]["reasonCode"], "reverse_reference")
    self.assertEqual(rows[0]["references"][0]["kind"], "catalog_recipe_ingredient")

def test_keeps_blank_effect_with_stat(self):
    entity = blank_entity("base_game:flamethrower_fx", "effect")
    entity["stats"] = [{"key": "damage", "value": 10}]
    rows, excluded = audit_effect_other_items(
        [blank_item("base_game:flamethrower_fx", "effect")], [entity], {}
    )
    self.assertEqual(excluded, set())
    self.assertTrue(rows[0]["signals"]["stats"])
```

- [ ] **Step 5: Run Task 1 tests and confirm GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.extract.test_effect_other_audit -v`

Expected: all audit decision tests pass with no warnings.

- [ ] **Step 6: Commit Task 1**

```bash
git add tools/extract/effect_other_audit.py tests/extract/test_effect_other_audit.py
git commit -m "feat: audit empty effect and other records"
```

---

### Task 2: Integrate filtering and atomic report generation

**Files:**
- Modify: `tools/extract/export_items.py`
- Modify: `tests/extract/test_export_items.py`
- Generate later: `data/generated/effect-other-audit.json`

**Interfaces:**
- Consumes: `audit_effect_other_items` from Task 1.
- Adds: `EFFECT_OTHER_AUDIT = Path("data/generated/effect-other-audit.json")`.
- Extends: `export_items(..., effect_other_audit_path: Path = EFFECT_OTHER_AUDIT)`.

- [ ] **Step 1: Write a failing exporter test**

Extend `test_export_is_deterministic_and_atomic` with a blank `effect` fixture,
an `effect_other_audit_path`, two export runs, and these assertions:

```python
self.assertNotIn("base_game:spark_helper", by_id)
self.assertEqual(effect_audit["schema_version"], 1)
self.assertEqual(effect_audit["summary"]["exclude"], 1)
self.assertEqual(effect_audit["rows"][0]["id"], "base_game:spark_helper")
self.assertEqual(effect_audit["rows"][0]["action"], "exclude")
self.assertEqual(effect_other_audit_path.read_bytes(), first_effect_audit)
self.assertFalse((root / ".effect-other-audit.json.tmp").exists())
```

- [ ] **Step 2: Run the exporter test and confirm RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.extract.test_export_items.ExportItemsTests.test_export_is_deterministic_and_atomic -v`

Expected: failure because `export_items` does not accept or write
`effect_other_audit_path`.

- [ ] **Step 3: Integrate the audit after complete detail enrichment**

In `export_items`, retain the existing Wiki merge, recipe linking, structure
visual audit, structure filtering, and structure detail construction. After
`structureDetails` is assigned, call:

```python
audit_rows, excluded_ids = audit_effect_other_items(
    items["items"], catalog["entities"], wiki.details
)
items["items"] = [
    item for item in items["items"] if item.get("id") not in excluded_ids
]
effect_other_audit = {
    "schema_version": 1,
    "summary": {
        "total": len(audit_rows),
        "keep": sum(row["action"] == "keep" for row in audit_rows),
        "exclude": sum(row["action"] == "exclude" for row in audit_rows),
        "categories": {
            category: sum(row["category"] == category for row in audit_rows)
            for category in ("effect", "other")
        },
    },
    "rows": audit_rows,
}
_atomic_json(Path(effect_other_audit_path), effect_other_audit)
```

Write the report in the same atomic output block as items, textures, detail
report, and structure audit. Ensure all rows and summary keys are sorted and
derived from the final row list.

- [ ] **Step 4: Run exporter tests and confirm GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.extract.test_export_items -v`

Expected: all exporter tests pass, including byte-identical audit output.

- [ ] **Step 5: Commit Task 2**

```bash
git add tools/extract/export_items.py tests/extract/test_export_items.py
git commit -m "feat: filter audited effect and other records"
```

---

### Task 3: Validate audit integrity and wire CLI paths

**Files:**
- Modify: `tools/extract/validate.py`
- Modify: `tools/extract/cli.py`
- Modify: `tests/extract/test_export_validate.py`

**Interfaces:**
- Adds: `_effect_other_audit_errors(items_path, audit_path) -> list[dict[str, Any]]`.
- Extends: `_prefab_export_coverage(..., effect_other_audit_path=None)`.
- Extends: `validate_catalog(..., effect_other_audit_path=None)`.
- Adds CLI default `EFFECT_OTHER_AUDIT` and `--effect-other-audit` to `export` and `validate`.

- [ ] **Step 1: Write failing validator tests**

```python
def test_effect_other_audit_rejects_excluded_public_or_signaled_items(self):
    errors = _effect_other_audit_errors(items_path, audit_path)
    self.assertEqual(errors, [
        {"code": "excluded_effect_other_is_public", "id": "base_game:helper"},
        {"code": "excluded_effect_other_has_positive_signal", "id": "base_game:helper"},
    ])

def test_prefab_coverage_accepts_effect_other_audit_exclusions(self):
    report = validate_catalog(
        db_path,
        prefab_scripts_path=scripts_path,
        items_path=items_path,
        effect_other_audit_path=audit_path,
    )
    self.assertEqual(report["prefab_export_coverage_errors"], [])
    self.assertEqual(report["effect_other_audit_errors"], [])
```

Add CLI assertions that both subcommands default to
`data/generated/effect-other-audit.json` and that `_export_stage` forwards the
path to `export_items`.

- [ ] **Step 2: Run the focused validator/CLI tests and confirm RED**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.extract.test_export_validate -v`

Expected: import/signature/assertion failures for the new audit validator and
CLI path.

- [ ] **Step 3: Implement audit validation and coverage subtraction**

```python
def _effect_other_audit_errors(items_path, audit_path):
    if items_path is None or audit_path is None:
        return []
    payload = json.loads(Path(items_path).read_text(encoding="utf-8"))
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else None
    rows = audit.get("rows") if isinstance(audit, dict) else None
    if payload.get("schema_version") != 6 or not isinstance(items, list):
        return [{"code": "invalid_effect_other_items_payload"}]
    if audit.get("schema_version") != 1 or not isinstance(rows, list):
        return [{"code": "invalid_effect_other_audit_payload"}]
    public_ids = {
        item.get("id") for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    errors = []
    seen = set()
    for row in rows:
        row_id = row.get("id") if isinstance(row, dict) else None
        if not isinstance(row_id, str):
            errors.append({"code": "invalid_effect_other_audit_row"})
            continue
        if row_id in seen:
            errors.append({"code": "duplicate_effect_other_audit_row", "id": row_id})
        seen.add(row_id)
        action = row.get("action")
        signals = row.get("signals")
        references = row.get("references")
        if action not in {"keep", "exclude"}:
            errors.append({"code": "invalid_effect_other_audit_action", "id": row_id})
        elif action == "keep" and row_id not in public_ids:
            errors.append({"code": "audited_effect_other_not_public", "id": row_id})
        elif action == "exclude" and row_id in public_ids:
            errors.append({"code": "excluded_effect_other_is_public", "id": row_id})
        if not isinstance(signals, dict) or not all(
            isinstance(value, bool) for value in signals.values()
        ):
            errors.append({"code": "invalid_effect_other_audit_signals", "id": row_id})
        elif action == "exclude" and any(signals.values()):
            errors.append({"code": "excluded_effect_other_has_positive_signal", "id": row_id})
        if not isinstance(references, list):
            errors.append({"code": "invalid_effect_other_audit_references", "id": row_id})
        elif action == "exclude" and references:
            errors.append({"code": "excluded_effect_other_is_referenced", "id": row_id})
    expected_summary = {
        "total": len(rows),
        "keep": sum(row.get("action") == "keep" for row in rows if isinstance(row, dict)),
        "exclude": sum(row.get("action") == "exclude" for row in rows if isinstance(row, dict)),
        "categories": {
            category: sum(row.get("category") == category for row in rows if isinstance(row, dict))
            for category in ("effect", "other")
        },
    }
    if audit.get("summary") != expected_summary:
        errors.append({"code": "effect_other_audit_summary_mismatch"})
    return errors


def validate_catalog(..., effect_other_audit_path=None):
    prefab_export_coverage_errors = _prefab_export_coverage(
        prefab_scripts_path,
        items_path,
        structure_audit_path,
        effect_other_audit_path,
    )
    effect_other_audit_errors = _effect_other_audit_errors(
        items_path, effect_other_audit_path
    )
    if effect_other_audit_errors:
        hard_failures.append("effect_other_audit_errors")
```

When calculating expected base-game prefab coverage, subtract base-game rows
whose effect/other audit action is `exclude`, exactly as structure exclusions
are already subtracted.

- [ ] **Step 4: Wire export/validate CLI and stage calls**

```python
EFFECT_OTHER_AUDIT = Path("data/generated/effect-other-audit.json")

export.add_argument("--effect-other-audit", type=Path, default=EFFECT_OTHER_AUDIT)
validate.add_argument("--effect-other-audit", type=Path, default=EFFECT_OTHER_AUDIT)
```

Pass the argument through `main`, `_export_stage`, `_validate_stage`, and
`run_all`; include its path in export stage output.

- [ ] **Step 5: Run extraction tests and confirm GREEN**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests/extract -p 'test_*.py'`

Expected: all extraction tests pass.

- [ ] **Step 6: Commit Task 3**

```bash
git add tools/extract/validate.py tools/extract/cli.py tests/extract/test_export_validate.py
git commit -m "test: validate effect and other audit output"
```

---

### Task 4: Regenerate public data and prove the real 537-record cleanup

**Files:**
- Modify: `public/data/items.json`
- Create: `data/generated/effect-other-audit.json`
- Potential deterministic refresh: `data/generated/item-textures.json`
- Potential deterministic refresh: `data/generated/tu-tien-item-details-report.json`
- Potential deterministic refresh: `data/generated/structure-icon-audit.json`

**Interfaces:**
- Consumes the completed exporter and existing canonical data.
- Produces a public payload with 2,286 items and the complete audit report.

- [ ] **Step 1: Run the real export**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m tools.extract.cli export`

Expected: export output lists `data/generated/effect-other-audit.json`; no
temporary output remains.

- [ ] **Step 2: Verify real counts and protected records**

Run:

```bash
jq '{total:(.items|length), effect:([.items[]|select(.category=="effect")]|length), other:([.items[]|select(.category=="other")]|length)}' public/data/items.json
jq '.summary' data/generated/effect-other-audit.json
jq -e '.items | any(.id=="base_game:flamethrower_fx") and any(.id=="base_game:wortox_soul_spawn")' public/data/items.json
```

Expected item counts: total `2286`, effect `327`, other `602`.

Expected audit counts: total `1466`, exclude `537`, keep `929`.

Expected protected-record check: `true`.

- [ ] **Step 3: Run catalog validation**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m tools.extract.cli validate`

Expected: exit code 0 and zero hard failures.

- [ ] **Step 4: Run frontend regression tests**

Run: `npm test -- --run`

Expected: all Vitest files and tests pass; Hiệu ứng and Khác filtering remains
functional with the cleaned payload.

- [ ] **Step 5: Commit generated artifacts**

```bash
git add public/data/items.json data/generated/effect-other-audit.json data/generated/item-textures.json data/generated/tu-tien-item-details-report.json data/generated/structure-icon-audit.json
git commit -m "data: remove empty effect and other records"
```

Only stage generated files whose bytes actually changed.

---

### Task 5: Full verification and handoff

**Files:**
- Verify all changed files from Tasks 1–4.

**Interfaces:**
- Produces fresh evidence required by `verification-before-completion`.

- [ ] **Step 1: Run the complete Python suite**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'`

Expected: all tests pass with zero failures/errors.

- [ ] **Step 2: Run frontend tests, type checking, and lint**

Run: `npm test -- --run`

Run: `npx tsc --noEmit`

Run: `npm run lint`

Expected: every command exits 0.

- [ ] **Step 3: Re-run export and compare deterministic hashes**

Run the export twice and compare SHA-256 hashes of
`public/data/items.json` and `data/generated/effect-other-audit.json` after
each run. Expected: both hashes match between runs.

- [ ] **Step 4: Review final diff and audit list**

Run: `git diff --check`

Run: `git status --short`

Run: `jq -r '.rows[] | select(.action=="exclude") | [.id,.category,.reasonCode] | @tsv' data/generated/effect-other-audit.json`

Expected: no whitespace errors; exactly 537 exclusion rows are listed.

- [ ] **Step 5: Complete the development branch**

Invoke `superpowers:finishing-a-development-branch`, rerun its required fresh
verification, and present the integration options to the user. Do not push or
merge without explicit instruction.
