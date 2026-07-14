# DST Tu Tiên Data Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reproducible extraction pipeline that inventories Tu Tiên content, captures runtime-only facts, enriches only referenced DST base-game entities, stores normalized provenance-aware SQLite, and exports deterministic search JSON.

**Architecture:** Python 3.9 standard-library extractors emit versioned raw-fact JSON from three independent sources: static mod files, copied base-game archives, and a dedicated-server runtime probe. A normalizer merges these facts with explicit precedence/conflict rules, writes SQLite with foreign keys and evidence, validates coverage, and exports frontend JSON plus an asset map.

**Tech Stack:** Python 3.9 (`argparse`, `dataclasses`, `hashlib`, `json`, `sqlite3`, `unittest`, `xml.etree.ElementTree`, `zipfile`), DST Lua runtime probe, SQLite 3, existing Next.js public directory.

## Global Constraints

- Do not modify any file under `mod/3721846643`, `mod/3721859355`, or `mod/3731181944`.
- Do not crawl, scrape, or import data from any wiki or website.
- Copy each required game file in full into `data/sources/game/` and record SHA-256 before parsing it.
- The minimum copied game inputs are `scripts.zip` and `images.zip`.
- Import only DST base-game entities referenced by Tu Tiên; do not ingest the full base-game catalog.
- Use namespace `tu_tien` for mod entities and `base_game` for resolved DST dependencies.
- Every normalized fact must have evidence and confidence.
- Run the dedicated server only with persistent storage rooted inside this workspace and never use a real save.
- Keep large source archives and runtime scratch data local-only; track their manifest, extractor code, tests, database schema, coverage report, and frontend exports.
- UI implementation is out of scope.

---

## Planned File Map

| Path | Responsibility |
|---|---|
| `tools/extract/contracts.py` | Versioned raw-fact contracts and JSON serialization |
| `tools/extract/source_manifest.py` | Copy and checksum full game archives |
| `tools/extract/lua_strings.py` | Parse literal Lua string assignments and aliases |
| `tools/extract/po_strings.py` | Parse Vietnamese PO entries by DST string key |
| `tools/extract/mod_static.py` | Static Tu Tiên entities, descriptions, assets, handbook pages |
| `tools/extract/runtime_import.py` | Validate runtime-probe JSON |
| `tools/extract/runtime_runner.py` | Install probe copy, run isolated server, collect output |
| `tools/extract/base_game.py` | Resolve dependency candidates and enrich from copied archives |
| `tools/extract/assets.py` | Build atlas/element asset facts from mod files and `images.zip` |
| `tools/extract/normalize.py` | Merge facts, precedence, conflicts and confidence |
| `tools/extract/database.py` | SQLite schema and deterministic persistence |
| `tools/extract/export_json.py` | Deterministic `catalog.json` and `assets.json` |
| `tools/extract/validate.py` | Referential-integrity and coverage checks |
| `tools/extract/cli.py` | Stage-oriented and full-pipeline CLI |
| `tools/runtime_mod/*` | Lua runtime probe loaded beside Tu Tiên |
| `tests/extract/*` | Unit/integration fixtures and assertions |

---

### Task 1: Establish raw-fact contracts and CLI package

**Files:**
- Create: `tools/__init__.py`
- Create: `tools/extract/__init__.py`
- Create: `tools/extract/contracts.py`
- Create: `tools/extract/cli.py`
- Create: `tests/extract/__init__.py`
- Create: `tests/extract/test_contracts.py`

**Interfaces:**
- Produces: `SourceRef`, `EntityKey`, `Fact`, `FactBundle`, `dump_bundle(path, bundle)`, `load_bundle(path)`.
- `Fact.kind` values: `entity`, `name`, `description`, `recipe`, `ingredient`, `acquisition`, `stat`, `effect`, `relation`, `asset`.
- `Fact.subject` is always `EntityKey(namespace, prefab_id)`.

- [ ] **Step 1: Write the failing contract round-trip test**

```python
# tests/extract/test_contracts.py
import tempfile
import unittest
from pathlib import Path

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef, dump_bundle, load_bundle


class ContractTests(unittest.TestCase):
    def test_bundle_round_trip_is_deterministic(self):
        source = SourceRef("mod-static", "mod_static", "mod/3721846643/scripts/main/strings.lua", "18.0.10", "abc")
        fact = Fact("name", EntityKey("tu_tien", "xd_lingshi1"), {"lang": "vi", "value": "Hạ Phẩm Linh Thạch"}, source, 1.0)
        bundle = FactBundle(1, [source], [fact], [])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "facts.json"
            dump_bundle(path, bundle)
            first = path.read_bytes()
            self.assertEqual(load_bundle(path), bundle)
            dump_bundle(path, bundle)
            self.assertEqual(path.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify the package is missing**

Run: `python3 -m unittest tests.extract.test_contracts -v`

Expected: `ERROR` with `ModuleNotFoundError: No module named 'tools.extract.contracts'`.

- [ ] **Step 3: Implement immutable contracts and deterministic serialization**

```python
# tools/extract/contracts.py
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True, order=True)
class EntityKey:
    namespace: str
    prefab_id: str


@dataclass(frozen=True, order=True)
class SourceRef:
    source_id: str
    kind: str
    path: str
    version: str
    sha256: str


@dataclass(frozen=True)
class Fact:
    kind: str
    subject: EntityKey
    payload: Dict[str, Any]
    source: SourceRef
    confidence: float
    locator: str = ""


@dataclass(frozen=True)
class FactBundle:
    schema_version: int
    sources: List[SourceRef] = field(default_factory=list)
    facts: List[Fact] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)


def _sort_key(fact: Fact):
    return (fact.subject.namespace, fact.subject.prefab_id, fact.kind, fact.locator, json.dumps(fact.payload, ensure_ascii=False, sort_keys=True))


def dump_bundle(path: Path, bundle: FactBundle) -> None:
    data = {
        "schema_version": bundle.schema_version,
        "sources": [asdict(v) for v in sorted(bundle.sources)],
        "facts": [
            {
                **asdict(v),
                "subject": asdict(v.subject),
                "source": asdict(v.source),
            }
            for v in sorted(bundle.facts, key=_sort_key)
        ],
        "errors": sorted(bundle.errors, key=lambda v: json.dumps(v, sort_keys=True)),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_bundle(path: Path) -> FactBundle:
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = {v["source_id"]: SourceRef(**v) for v in data["sources"]}
    facts = []
    for value in data["facts"]:
        source_id = value["source"]["source_id"]
        facts.append(Fact(value["kind"], EntityKey(**value["subject"]), value["payload"], sources[source_id], value["confidence"], value["locator"]))
    return FactBundle(data["schema_version"], list(sources.values()), facts, data["errors"])
```

- [ ] **Step 4: Add a CLI with explicit stages**

```python
# tools/extract/cli.py
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dst-extract")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("snapshot-game", "extract-static", "run-runtime", "import-runtime", "enrich-base", "build-db", "export", "validate", "all"):
        sub.add_parser(name)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    raise SystemExit(f"stage not wired: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run tests**

Run: `python3 -m unittest tests.extract.test_contracts -v`

Expected: one test passes.

- [ ] **Step 6: Commit**

```bash
git add tools/__init__.py tools/extract tests/extract
git commit -m "feat: define extraction fact contracts"
```

---

### Task 2: Snapshot complete game archives before use

**Files:**
- Modify: `.gitignore`
- Create: `tools/extract/source_manifest.py`
- Modify: `tools/extract/cli.py`
- Create: `tests/extract/test_source_manifest.py`

**Interfaces:**
- Consumes: source directory containing `databundles/scripts.zip` and `databundles/images.zip`.
- Produces: `snapshot_game_sources(game_data: Path, destination: Path) -> dict` and `data/sources/game/manifest.json`.

- [ ] **Step 1: Write the failing copy/checksum test**

```python
# tests/extract/test_source_manifest.py
import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.extract.source_manifest import snapshot_game_sources


class SourceManifestTests(unittest.TestCase):
    def test_copies_whole_archives_and_records_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundles = root / "game" / "databundles"
            bundles.mkdir(parents=True)
            (bundles / "scripts.zip").write_bytes(b"scripts")
            (bundles / "images.zip").write_bytes(b"images")
            result = snapshot_game_sources(root / "game", root / "snapshot")
            self.assertEqual((root / "snapshot" / "scripts.zip").read_bytes(), b"scripts")
            self.assertEqual(result["files"]["scripts.zip"]["sha256"], hashlib.sha256(b"scripts").hexdigest())
            self.assertEqual(result["files"]["images.zip"]["size"], 6)
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest tests.extract.test_source_manifest -v`

Expected: import error for `source_manifest`.

- [ ] **Step 3: Implement atomic full-file copy and verification**

```python
# tools/extract/source_manifest.py
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ARCHIVES = ("scripts.zip", "images.zip")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def snapshot_game_sources(game_data: Path, destination: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in ARCHIVES:
        source = game_data / "databundles" / name
        if not source.is_file():
            raise FileNotFoundError(source)
        target = destination / name
        temporary = destination / (name + ".partial")
        shutil.copyfile(source, temporary)
        if source.stat().st_size != temporary.stat().st_size or _sha256(source) != _sha256(temporary):
            temporary.unlink(missing_ok=True)
            raise IOError(f"copy verification failed: {name}")
        temporary.replace(target)
        files[name] = {"size": target.stat().st_size, "sha256": _sha256(target)}
    manifest = {"schema_version": 1, "copied_at": datetime.now(timezone.utc).isoformat(), "files": files}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest
```

- [ ] **Step 4: Wire `snapshot-game` and ignore only large local inputs and scratch runtime data**

Add `--game-data` and `--destination` (default `data/sources/game`) to the `snapshot-game` subparser, call `snapshot_game_sources`, and print the two copied paths plus their hashes. Then append:

```gitignore
# Local extraction inputs and runtime scratch
/data/sources/game/*.zip
/data/raw/runtime.json
/data/runtime/
```

- [ ] **Step 5: Run tests and then snapshot the real archives**

Run: `python3 -m unittest tests.extract.test_source_manifest -v`

Expected: one test passes.

Execution command after implementation:

```bash
python3 -m tools.extract.cli snapshot-game --game-data "$HOME/Library/Application Support/Steam/steamapps/common/Don't Starve Together/dontstarve_steam.app/Contents/data"
```

Expected: `data/sources/game/scripts.zip` (~54 MB), `images.zip` (~32 MB), and a verified manifest. No parser opens the original game archives.

- [ ] **Step 6: Commit**

```bash
git add .gitignore tools/extract/cli.py tools/extract/source_manifest.py tests/extract/test_source_manifest.py data/sources/game/manifest.json
git commit -m "feat: snapshot verified DST source archives"
```

---

### Task 3: Extract static Tu Tiên entities, translations and asset references

**Files:**
- Create: `tools/extract/lua_strings.py`
- Create: `tools/extract/po_strings.py`
- Create: `tools/extract/mod_static.py`
- Modify: `tools/extract/cli.py`
- Create: `tests/extract/fixtures/strings.lua`
- Create: `tests/extract/fixtures/viethoa.po`
- Create: `tests/extract/test_mod_static.py`

**Interfaces:**
- Produces: `extract_mod_static(mod_root: Path, tu_tien_translation: Path, base_translation_po: Path) -> FactBundle`.
- Writes: `data/raw/mod_static.json`.

- [ ] **Step 1: Add fixture and failing assertions**

```lua
-- tests/extract/fixtures/strings.lua
STRINGS.NAMES.XD_TEST_SWORD = "Kiếm Thử"
STRINGS.RECIPE_DESC.XD_TEST_SWORD = "Rèn để thử"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.XD_TEST_SWORD = "Một thanh kiếm"
STRINGS.NAMES.XD_ALIAS = STRINGS.NAMES.GOLDNUGGET
```

```python
# tests/extract/test_mod_static.py
import tempfile
import unittest
from pathlib import Path

from tools.extract.lua_strings import parse_string_assignments


class ModStaticTests(unittest.TestCase):
    def test_parses_name_description_recipe_and_alias(self):
        path = Path("tests/extract/fixtures/strings.lua")
        rows = parse_string_assignments(path)
        values = {(row["field"], row["prefab_id"]): row for row in rows}
        self.assertEqual(values[("name", "xd_test_sword")]["value"], "Kiếm Thử")
        self.assertEqual(values[("description", "xd_test_sword")]["line"], 3)
        self.assertEqual(values[("name", "xd_alias")]["alias_prefab_id"], "goldnugget")
```

- [ ] **Step 2: Verify the parser test fails**

Run: `python3 -m unittest tests.extract.test_mod_static -v`

Expected: import error for `lua_strings`.

- [ ] **Step 3: Implement the restricted string parser**

```python
# tools/extract/lua_strings.py
import ast
import re
from pathlib import Path


PATTERNS = (
    ("name", re.compile(r'^STRINGS\.NAMES\.([A-Z0-9_]+)\s*=\s*(.+?)\s*$')),
    ("recipe_description", re.compile(r'^STRINGS\.RECIPE_DESC\.([A-Z0-9_]+)\s*=\s*(.+?)\s*$')),
    ("description", re.compile(r'^STRINGS\.CHARACTERS\.GENERIC\.DESCRIBE\.([A-Z0-9_]+)\s*=\s*(.+?)\s*$')),
)
ALIAS = re.compile(r'^STRINGS\.(?:NAMES|RECIPE_DESC|CHARACTERS\.GENERIC\.DESCRIBE)\.([A-Z0-9_]+)$')


def parse_string_assignments(path: Path):
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        for field, pattern in PATTERNS:
            match = pattern.match(line.strip())
            if not match:
                continue
            prefab_id, expression = match.groups()
            row = {"field": field, "prefab_id": prefab_id.lower(), "line": line_number}
            alias = ALIAS.match(expression)
            if alias:
                row["alias_prefab_id"] = alias.group(1).lower()
            elif expression.startswith(('"', "'")):
                row["value"] = ast.literal_eval(expression)
            else:
                row["unparsed_expression"] = expression
            rows.append(row)
            break
    return rows
```

- [ ] **Step 4: Implement static inventory and provenance assembly**

`mod_static.py` must union IDs from parsed strings, `scripts/prefabs/*.lua`, `images/inventoryimages/*.xml`, and the runtime-independent mod metadata. It must add asset facts for every XML/TEX pair and handbook facts for `images/xd_info_*.xml`, while reporting missing pairs instead of inventing them.

Core signature:

```python
def extract_mod_static(mod_root: Path, tu_tien_translation: Path, base_translation_po: Path) -> FactBundle:
    """Return sorted static facts; never execute Lua and never modify mod_root."""
```

`po_strings.py` must parse `msgctxt`, `msgid`, and `msgstr`, including continued quoted lines, and expose:

```python
def load_po_by_context(path: Path) -> dict:
    """Map an exact PO context such as STRINGS.NAMES.GOLDNUGGET to translated text."""
```

- [ ] **Step 5: Wire `extract-static`, run unit tests and extract the real static bundle**

The CLI stage must accept explicit mod/translation paths, use the defaults listed in Task 8, and write through `dump_bundle` to `data/raw/mod_static.json`.

Run: `python3 -m unittest tests.extract.test_mod_static -v`

Expected: parser tests pass.

Run: `python3 -m tools.extract.cli extract-static`

Expected: `data/raw/mod_static.json` includes hundreds of `tu_tien` entities, name/description evidence, 379 inventory atlas candidates, and 39 handbook pages; errors are explicit.

- [ ] **Step 6: Commit**

```bash
git add tools/extract/cli.py tools/extract/lua_strings.py tools/extract/po_strings.py tools/extract/mod_static.py tests/extract data/raw/mod_static.json
git commit -m "feat: extract static Tu Tien catalog facts"
```

---

### Task 4: Capture recipes, prefab stats and acquisition at runtime

**Files:**
- Create: `tools/runtime_mod/modinfo.lua`
- Create: `tools/runtime_mod/modmain.lua`
- Create: `tools/runtime_mod/scripts/exporter.lua`
- Create: `tools/extract/runtime_import.py`
- Create: `tools/extract/runtime_runner.py`
- Modify: `tools/extract/cli.py`
- Create: `tests/extract/fixtures/runtime.json`
- Create: `tests/extract/test_runtime_import.py`

**Interfaces:**
- Lua output schema: `{schema_version=1, mod_version, recipes, prefabs, errors}`.
- Produces: `run_runtime_probe(server_bin, game_mods_dir, workspace, timeout_seconds) -> Path`.
- Imports: `load_runtime_bundle(path: Path) -> FactBundle`.

- [ ] **Step 1: Write a failing runtime-contract test**

```python
# tests/extract/test_runtime_import.py
import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.runtime_import import load_runtime_bundle


class RuntimeImportTests(unittest.TestCase):
    def test_recipe_ingredients_become_dependency_facts(self):
        payload = {
            "schema_version": 1,
            "mod_version": "18.0.10",
            "recipes": [{"product": "xd_test_sword", "ingredients": [{"prefab": "goldnugget", "amount": 2}], "tech": "SCIENCE_ONE"}],
            "prefabs": [],
            "errors": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)
        ingredient = next(f for f in bundle.facts if f.kind == "ingredient")
        self.assertEqual(ingredient.payload["ingredient"], {"namespace": "base_game", "prefab_id": "goldnugget"})
        self.assertEqual(ingredient.confidence, 1.0)
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest tests.extract.test_runtime_import -v`

Expected: import error for `runtime_import`.

- [ ] **Step 3: Implement Lua registry export with per-prefab isolation**

```lua
-- tools/runtime_mod/modinfo.lua
name = "DST Wiki Runtime Extractor"
description = "Exports registry facts into an isolated test cluster"
author = "dst_wiki"
version = "1.0.0"
api_version = 10
dst_compatible = true
all_clients_require_mod = false
client_only_mod = false
priority = -1000
```

```lua
-- tools/runtime_mod/modmain.lua
local exporter = require("exporter")

AddSimPostInit(function()
    TheWorld:DoTaskInTime(0, function()
        exporter.Run()
    end)
end)
```

`exporter.lua` must:

1. Select mod-prefab IDs from `STRINGS.NAMES` keys beginning `XD_` plus recipe products beginning `xd_`.
2. Serialize every matching `AllRecipes` entry, including ingredient type/amount, tech, filters, builder tags and output count.
3. Call `SpawnPrefab(id)` inside `pcall`, inspect only known components, remove the instance, and append an error record on failure.
4. Export common component fields from `weapon`, `armor`, `finiteuses`, `edible`, `perishable`, `lootdropper`, `pickable`, `tradable`, `stackable`, and `container`.
5. Write `runtime.json` through `TheSim:SetPersistentString` and print exactly `DST_WIKI_EXTRACT_COMPLETE` after the callback succeeds.

The exported component shape is fixed:

```lua
{
    prefab = "xd_test_sword",
    entity_type = "inventory_item",
    stats = {{key = "damage", value = 68, unit = "hp"}},
    loot = {{prefab = "goldnugget", chance = 1, count = 1}},
    harvest = {},
    relations = {}
}
```

- [ ] **Step 4: Implement the Python importer and isolated runner**

The runner must copy, never symlink, these folders into a uniquely named temporary mod directory:

- `mod/3721846643`
- `tools/runtime_mod`

It must create a persistent root at `data/runtime/`, start the dedicated-server executable with that root, poll the log for the completion sentinel, terminate only the process it started, locate `runtime.json` recursively under the persistent root, validate it, and copy it to `data/raw/runtime.json`.

The runner must refuse any persistent root outside the resolved workspace:

```python
def assert_within_workspace(workspace: Path, candidate: Path) -> None:
    candidate.resolve().relative_to(workspace.resolve())
```

- [ ] **Step 5: Run importer tests**

Run: `python3 -m unittest tests.extract.test_runtime_import -v`

Expected: runtime schema and namespace tests pass.

- [ ] **Step 6: Wire and run the dedicated-server smoke probe with approval for the temporary game-mod copy**

Add `run-runtime` arguments `--server-bin`, `--game-mods-dir`, `--workspace` and `--timeout` (default `180`), and add `import-runtime --input data/raw/runtime.json`. Run the probe through the extraction CLI. The execution step must request approval before writing the temporary mod copies into the installed game's `mods/` directory.

Expected:

- Log contains `DST_WIKI_EXTRACT_COMPLETE`.
- `data/raw/runtime.json` passes schema validation.
- The runner removes only its own temporary probe/core-mod copies.
- The original `mod/3721846643` remains byte-identical.

- [ ] **Step 7: Commit**

```bash
git add tools/runtime_mod tools/extract/cli.py tools/extract/runtime_import.py tools/extract/runtime_runner.py tests/extract/test_runtime_import.py tests/extract/fixtures/runtime.json
git commit -m "feat: capture Tu Tien runtime registry facts"
```

---

### Task 5: Resolve and enrich only referenced base-game dependencies

**Files:**
- Create: `tools/extract/base_game.py`
- Modify: `tools/extract/cli.py`
- Create: `tests/extract/test_base_game.py`

**Interfaces:**
- Consumes: static/runtime bundles, copied `scripts.zip`, base Vietnamese PO.
- Produces: `extract_base_game_dependencies(...) -> FactBundle` and `data/raw/base_game.json`.

- [ ] **Step 1: Write a failing dependency-closure test**

```python
# tests/extract/test_base_game.py
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.extract.base_game import DependencyRequest, enrich_dependencies


class BaseGameTests(unittest.TestCase):
    def test_enriches_requested_item_without_unrelated_prefabs(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "scripts.zip"
            with ZipFile(archive, "w") as handle:
                handle.writestr("scripts/prefabs/goldnugget.lua", 'return Prefab("goldnugget", fn)')
                handle.writestr("scripts/prefabs/pickaxe.lua", 'return Prefab("pickaxe", fn)')
                handle.writestr("scripts/strings.lua", 'STRINGS.NAMES.GOLDNUGGET = "Gold Nugget"')
                handle.writestr("scripts/recipes.lua", '')
            requests = [DependencyRequest("goldnugget", "ingredient", "tu_tien:xd_test_sword")]
            bundle = enrich_dependencies(archive, requests, Path("tests/extract/fixtures/viethoa.po"))
        ids = {f.subject.prefab_id for f in bundle.facts if f.kind == "entity"}
        self.assertIn("goldnugget", ids)
        self.assertNotIn("pickaxe", ids)
        self.assertTrue(any(f.kind == "name" and f.subject.prefab_id == "goldnugget" for f in bundle.facts))
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest tests.extract.test_base_game -v`

Expected: import error for `base_game`.

- [ ] **Step 3: Implement indexed ZIP lookup and exact resolution rules**

```python
# tools/extract/base_game.py
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


@dataclass(frozen=True)
class DependencyRequest:
    prefab_id: str
    relation: str
    requested_by: str


class ScriptIndex:
    def __init__(self, archive: Path):
        self.archive = archive
        with ZipFile(archive) as handle:
            self.members = tuple(handle.namelist())
            self.prefab_members = {Path(name).stem: name for name in self.members if name.startswith("scripts/prefabs/") and name.endswith(".lua")}

    def read(self, member: str) -> str:
        with ZipFile(self.archive) as handle:
            return handle.read(member).decode("utf-8-sig")

    def contains_prefab(self, prefab_id: str) -> bool:
        return prefab_id in self.prefab_members
```

Resolution must accept an ID only when found in at least one of:

- `scripts/prefabs/<id>.lua`
- a `Prefab("<id>"...)` declaration in indexed prefab source
- a `Recipe2("<id>"...)` product
- `STRINGS.NAMES.<ID>`

The bundle must retain `requested_by` evidence. Recipe parsing must use balanced parentheses/braces rather than a single multiline regex. Common stat/acquisition patterns must preserve the literal source expression and line number even when a TUNING expression cannot be evaluated.

- [ ] **Step 4: Add exact common-pattern extractors**

Support these source patterns first:

```text
Recipe2(product, {Ingredient(prefab, amount), ...}, tech, config)
inst.components.weapon:SetDamage(value)
inst.components.armor:InitCondition(condition, absorption)
inst.components.finiteuses:SetMaxUses(value)
inst.components.edible.healthvalue/hungervalue/sanityvalue
inst.components.lootdropper:SetLoot({...})
inst.components.lootdropper:AddChanceLoot(prefab, chance)
inst.components.pickable:SetUp(product, regrow_time)
```

Anything outside these patterns becomes source evidence plus a coverage warning; it must not be guessed.

- [ ] **Step 5: Wire `enrich-base`, run tests and real enrichment**

The CLI must load `data/raw/mod_static.json` and `data/raw/runtime.json`, derive unique dependency requests, verify source archive hashes against `data/sources/game/manifest.json`, and write `data/raw/base_game.json`.

Run: `python3 -m unittest tests.extract.test_base_game -v`

Expected: dependency resolution, one-level closure and unresolved-ID tests pass.

Run: `python3 -m tools.extract.cli enrich-base`

Expected: `data/raw/base_game.json` contains only IDs requested by Tu Tiên facts plus explicit one-level recipe references, each with `requested_by` provenance.

- [ ] **Step 6: Commit**

```bash
git add tools/extract/base_game.py tools/extract/cli.py tests/extract/test_base_game.py data/raw/base_game.json
git commit -m "feat: enrich referenced DST base entities"
```

---

### Task 6: Build icon and handbook asset facts

**Files:**
- Create: `tools/extract/assets.py`
- Create: `tests/extract/test_assets.py`
- Create: `tests/extract/fixtures/atlas.xml`

**Interfaces:**
- Produces: asset facts containing `atlas`, `texture`, `element`, UV coordinates, source checksum and availability.
- Writes: asset records into `data/raw/mod_static.json`/`base_game.json`; final map is `public/data/assets.json`.

- [ ] **Step 1: Write a failing atlas parse test**

```xml
<!-- tests/extract/fixtures/atlas.xml -->
<Atlas><Texture filename="inventoryimages.tex"/><Elements><Element name="goldnugget.tex" u1="0.0" u2="0.5" v1="0.0" v2="0.5"/></Elements></Atlas>
```

```python
# tests/extract/test_assets.py
import unittest
from pathlib import Path

from tools.extract.assets import parse_atlas


class AssetTests(unittest.TestCase):
    def test_parses_texture_element_and_uv(self):
        atlas = parse_atlas(Path("tests/extract/fixtures/atlas.xml"))
        self.assertEqual(atlas.texture, "inventoryimages.tex")
        self.assertEqual(atlas.elements["goldnugget.tex"], (0.0, 0.5, 0.0, 0.5))
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest tests.extract.test_assets -v`

Expected: import error for `assets`.

- [ ] **Step 3: Implement XML/ZIP atlas parsing**

```python
# tools/extract/assets.py
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Atlas:
    texture: str
    elements: Dict[str, Tuple[float, float, float, float]]


def parse_atlas(path: Path) -> Atlas:
    root = ET.fromstring(path.read_text(encoding="utf-8-sig"))
    texture = root.find("Texture").attrib["filename"]
    elements = {}
    for node in root.find("Elements"):
        elements[node.attrib["name"]] = tuple(float(node.attrib[key]) for key in ("u1", "u2", "v1", "v2"))
    return Atlas(texture, elements)
```

Add a sibling `parse_atlas_bytes(data: bytes)` for XML members inside `images.zip`. Scan exactly the five base atlases `inventoryimages.xml` through `inventoryimages4.xml`, and direct mod inventory XML files. Record `.tex` presence and UV metadata; do not attempt browser PNG conversion in this extraction plan.

The 39 `xd_info_*.xml/.tex` pairs are recorded as `handbook_image` assets with stable sort order. OCR is excluded because the images themselves are primary assets and runtime/source facts remain authoritative.

- [ ] **Step 4: Run tests**

Run: `python3 -m unittest tests.extract.test_assets -v`

Expected: atlas tests pass, including malformed XML and missing texture cases.

- [ ] **Step 5: Commit**

```bash
git add tools/extract/assets.py tests/extract/test_assets.py tests/extract/fixtures/atlas.xml
git commit -m "feat: index DST and Tu Tien asset atlases"
```

---

### Task 7: Normalize facts into provenance-aware SQLite

**Files:**
- Create: `tools/extract/normalize.py`
- Create: `tools/extract/database.py`
- Modify: `tools/extract/cli.py`
- Create: `tests/extract/test_database.py`

**Interfaces:**
- Consumes: three `FactBundle` inputs.
- Produces: `normalize(bundles) -> NormalizedCatalog`, `create_schema(connection)`, and `write_database(path, catalog)`.
- Writes: `data/generated/wiki.sqlite`.

- [ ] **Step 1: Write failing precedence, conflict and foreign-key tests**

```python
# tests/extract/test_database.py
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.extract.database import write_database
from tools.extract.normalize import normalize
from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef


class DatabaseTests(unittest.TestCase):
    def test_runtime_wins_but_both_evidence_rows_survive(self):
        static = SourceRef("static", "mod_static", "strings.lua", "18.0.10", "a")
        runtime = SourceRef("runtime", "runtime_probe", "runtime.json", "18.0.10", "b")
        key = EntityKey("tu_tien", "xd_test_sword")
        bundles = [
            FactBundle(1, [static], [Fact("stat", key, {"key": "damage", "value": 60, "unit": "hp"}, static, 0.9)], []),
            FactBundle(1, [runtime], [Fact("stat", key, {"key": "damage", "value": 68, "unit": "hp"}, runtime, 1.0)], []),
        ]
        catalog = normalize(bundles)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, catalog)
            db = sqlite3.connect(path)
            self.assertEqual(db.execute("select value_num from stats where stat_key='damage'").fetchone()[0], 68)
            self.assertEqual(db.execute("select count(*) from evidence").fetchone()[0], 2)
            self.assertEqual(db.execute("pragma foreign_key_check").fetchall(), [])
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest tests.extract.test_database -v`

Expected: import error for `database` or `normalize`.

- [ ] **Step 3: Implement explicit precedence and conflict records**

```python
# tools/extract/normalize.py
SOURCE_PRIORITY = {
    "runtime_probe": 400,
    "mod_static": 300,
    "base_game_source": 300,
    "mod_translation": 200,
    "manual_review": 100,
}


def fact_rank(fact):
    return (SOURCE_PRIORITY[fact.source.kind], fact.confidence, fact.source.source_id, fact.locator)
```

For every scalar slot `(subject, kind, payload.key/lang)`, retain all candidates as evidence, choose the maximum rank, and emit a conflict whenever distinct values exist. Relation facts are deduplicated by their full semantic key rather than ranked away.

- [ ] **Step 4: Implement the complete SQLite schema**

`database.py` must create these tables with `PRAGMA foreign_keys=ON`:

```sql
CREATE TABLE sources (
  source_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  path TEXT NOT NULL,
  version TEXT NOT NULL,
  sha256 TEXT NOT NULL
);
CREATE TABLE entities (
  namespace TEXT NOT NULL,
  prefab_id TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  is_inventory_item INTEGER NOT NULL,
  name_vi TEXT,
  name_en TEXT,
  description_vi TEXT,
  description_en TEXT,
  icon_key TEXT,
  confidence REAL NOT NULL,
  PRIMARY KEY(namespace, prefab_id)
);
CREATE TABLE recipes (
  recipe_id TEXT PRIMARY KEY,
  product_namespace TEXT NOT NULL,
  product_id TEXT NOT NULL,
  output_count INTEGER NOT NULL,
  tech TEXT,
  restrictions_json TEXT NOT NULL,
  FOREIGN KEY(product_namespace, product_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE recipe_ingredients (
  recipe_id TEXT NOT NULL,
  position INTEGER NOT NULL,
  ingredient_namespace TEXT NOT NULL,
  ingredient_id TEXT NOT NULL,
  amount REAL NOT NULL,
  PRIMARY KEY(recipe_id, position),
  FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
  FOREIGN KEY(ingredient_namespace, ingredient_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE acquisition_sources (
  acquisition_id TEXT PRIMARY KEY,
  target_namespace TEXT NOT NULL,
  target_id TEXT NOT NULL,
  source_type TEXT NOT NULL,
  source_namespace TEXT,
  source_id TEXT,
  chance REAL,
  min_count REAL,
  max_count REAL,
  conditions_json TEXT NOT NULL,
  FOREIGN KEY(target_namespace, target_id) REFERENCES entities(namespace, prefab_id),
  FOREIGN KEY(source_namespace, source_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE stats (
  namespace TEXT NOT NULL,
  prefab_id TEXT NOT NULL,
  stat_key TEXT NOT NULL,
  value_num REAL,
  value_text TEXT,
  unit TEXT,
  confidence REAL NOT NULL,
  PRIMARY KEY(namespace, prefab_id, stat_key),
  FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE effects (
  effect_id TEXT PRIMARY KEY,
  namespace TEXT NOT NULL,
  prefab_id TEXT NOT NULL,
  trigger_name TEXT,
  effect_key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  duration REAL,
  FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE entity_relations (
  relation_id TEXT PRIMARY KEY,
  from_namespace TEXT NOT NULL,
  from_id TEXT NOT NULL,
  relation_type TEXT NOT NULL,
  to_namespace TEXT NOT NULL,
  to_id TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  FOREIGN KEY(from_namespace, from_id) REFERENCES entities(namespace, prefab_id),
  FOREIGN KEY(to_namespace, to_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE assets (
  asset_id TEXT PRIMARY KEY,
  namespace TEXT NOT NULL,
  prefab_id TEXT,
  asset_type TEXT NOT NULL,
  atlas TEXT,
  texture TEXT NOT NULL,
  element TEXT,
  uv_json TEXT,
  FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
);
CREATE TABLE evidence (
  evidence_id TEXT PRIMARY KEY,
  record_type TEXT NOT NULL,
  record_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  locator TEXT NOT NULL,
  raw_value_json TEXT NOT NULL,
  confidence REAL NOT NULL,
  selected INTEGER NOT NULL,
  FOREIGN KEY(source_id) REFERENCES sources(source_id)
);
CREATE TABLE conflicts (
  conflict_id TEXT PRIMARY KEY,
  subject_key TEXT NOT NULL,
  field_key TEXT NOT NULL,
  candidates_json TEXT NOT NULL,
  selected_json TEXT NOT NULL
);
```

Writes must occur inside one transaction and in sorted primary-key order.

- [ ] **Step 5: Wire `build-db`, run tests and build the real database**

The CLI stage loads all three raw bundles in fixed order, calls `normalize`, and writes `data/generated/wiki.sqlite` via a temporary database followed by atomic rename.

Run: `python3 -m unittest tests.extract.test_database -v`

Expected: precedence, evidence preservation, deterministic record IDs and foreign-key tests pass.

Run: `python3 -m tools.extract.cli build-db`

Expected: `data/generated/wiki.sqlite` is created and `sqlite3 data/generated/wiki.sqlite 'pragma foreign_key_check'` prints no rows.

- [ ] **Step 6: Commit**

```bash
git add tools/extract/normalize.py tools/extract/database.py tools/extract/cli.py tests/extract/test_database.py data/generated/wiki.sqlite
git commit -m "feat: build provenance-aware DST catalog database"
```

---

### Task 8: Export deterministic search JSON and coverage report

**Files:**
- Create: `tools/extract/export_json.py`
- Create: `tools/extract/validate.py`
- Create: `tests/extract/test_export_validate.py`
- Modify: `tools/extract/cli.py`
- Create: `public/data/catalog.json`
- Create: `public/data/assets.json`
- Create: `data/generated/coverage.json`

**Interfaces:**
- Produces: `export_catalog(db_path, catalog_path, assets_path)` and `validate_catalog(db_path) -> dict`.
- Final CLI: `python3 -m tools.extract.cli all`.

- [ ] **Step 1: Write failing deterministic-export and coverage tests**

```python
# tests/extract/test_export_validate.py
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.extract.database import create_schema
from tools.extract.export_json import export_catalog
from tools.extract.validate import validate_catalog


class ExportTests(unittest.TestCase):
    def build_catalog(self, path: Path):
        db = sqlite3.connect(path)
        create_schema(db)
        db.executemany(
            "insert into entities(namespace,prefab_id,entity_type,is_inventory_item,name_vi,confidence) values(?,?,?,?,?,?)",
            [
                ("base_game", "goldnugget", "inventory_item", 1, "Vàng", 1.0),
                ("tu_tien", "xd_test_sword", "inventory_item", 1, "Kiếm Thử", 1.0),
            ],
        )
        db.execute("insert into recipes values(?,?,?,?,?,?)", ("tu_tien:xd_test_sword", "tu_tien", "xd_test_sword", 1, "SCIENCE_ONE", "{}"))
        db.execute("insert into recipe_ingredients values(?,?,?,?,?)", ("tu_tien:xd_test_sword", 0, "base_game", "goldnugget", 2))
        db.commit()
        db.close()

    def test_export_is_stable_and_contains_nested_recipe_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "catalog.sqlite"
            self.build_catalog(db)
            catalog = Path(tmp) / "catalog.json"
            assets = Path(tmp) / "assets.json"
            export_catalog(db, catalog, assets)
            first = catalog.read_bytes()
            export_catalog(db, catalog, assets)
            self.assertEqual(catalog.read_bytes(), first)
            item = json.loads(first)["entities"][0]
            self.assertIn("recipes", item)
            self.assertIn("acquisition", item)

    def test_validation_rejects_unresolved_foreign_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "catalog.sqlite"
            self.build_catalog(db)
            report = validate_catalog(db)
            self.assertEqual(report["foreign_key_errors"], [])
            self.assertEqual(report["wiki_urls"], [])
```

- [ ] **Step 2: Run the test and verify failure**

Run: `python3 -m unittest tests.extract.test_export_validate -v`

Expected: import errors for `export_json` and `validate`.

- [ ] **Step 3: Implement deterministic frontend exports**

`catalog.json` has this fixed top-level shape:

```json
{
  "schema_version": 1,
  "entities": [
    {
      "key": "tu_tien:xd_test_sword",
      "namespace": "tu_tien",
      "prefab_id": "xd_test_sword",
      "type": "inventory_item",
      "name": {"vi": "Kiếm Thử", "en": null},
      "description": {"vi": "Một thanh kiếm", "en": null},
      "icon_key": "tu_tien:xd_test_sword",
      "stats": [{"key": "damage", "value": 68, "unit": "hp"}],
      "recipes": [{"output_count": 1, "ingredients": [{"key": "base_game:goldnugget", "amount": 2}]}],
      "acquisition": [{"type": "craft", "source": null, "chance": null, "conditions": {}}],
      "effects": [],
      "relations": [],
      "confidence": 1.0
    }
  ]
}
```

Sort entities by `(namespace, prefab_id)` and every nested list by semantic key. Do not export timestamps.

- [ ] **Step 4: Implement hard validation and coverage metrics**

`validate_catalog` must return and the CLI must write:

```python
{
    "entity_counts": {"tu_tien": 0, "base_game": 0},
    "coverage": {"name_vi": 0.0, "icon": 0.0, "recipe": 0.0, "acquisition": 0.0, "stats": 0.0},
    "unresolved_dependencies": [],
    "foreign_key_errors": [],
    "runtime_errors": [],
    "conflicts": [],
    "wiki_urls": [],
}
```

The `validate` and `all` commands exit nonzero when foreign keys fail, a referenced dependency is unresolved, a source archive checksum differs from the manifest, or any URL is found in evidence/source paths. Missing optional stats remain coverage warnings.

- [ ] **Step 5: Wire all CLI stages with explicit default paths**

Defaults:

```text
mod content:       mod/3721846643
Tu Tiên language: mod/3721859355/modmain.lua
base VI PO:        mod/3731181944/viethoa.po
game sources:      data/sources/game
raw facts:         data/raw
SQLite:            data/generated/wiki.sqlite
coverage:          data/generated/coverage.json
frontend JSON:     public/data/catalog.json, public/data/assets.json
```

`all` runs `extract-static -> import-runtime -> enrich-base -> build-db -> export -> validate`. It does not run or install the dedicated-server probe automatically; runtime capture remains an explicit preceding action because it requires approval and a disposable server process.

- [ ] **Step 6: Run the complete test suite and pipeline twice**

Run:

```bash
python3 -m unittest discover -s tests/extract -v
python3 -m tools.extract.cli all
shasum -a 256 public/data/catalog.json public/data/assets.json > /tmp/dst-wiki-first.sha256
python3 -m tools.extract.cli all
shasum -a 256 -c /tmp/dst-wiki-first.sha256
sqlite3 data/generated/wiki.sqlite 'pragma foreign_key_check'
```

Expected:

- All tests pass.
- Both JSON checksum checks print `OK`.
- Foreign-key check prints no rows.
- Coverage report contains zero unresolved dependencies and zero wiki URLs.
- Static/runtime errors, if any, are named by prefab and do not disappear silently.

- [ ] **Step 7: Commit**

```bash
git add tools/extract/cli.py tools/extract/export_json.py tools/extract/validate.py tests/extract/test_export_validate.py public/data data/generated/coverage.json
git commit -m "feat: export and validate searchable DST catalog"
```

---

### Task 9: Final extraction audit and handoff

**Files:**
- Create: `docs/data-extraction.md`
- Modify only if audit finds a concrete defect: extractor/test files from Tasks 1–8

**Interfaces:**
- Produces: repeatable operator instructions and a signed-off coverage snapshot.

- [ ] **Step 1: Document the exact refresh workflow**

`docs/data-extraction.md` must describe:

1. How to verify mod versions.
2. How to snapshot full `scripts.zip` and `images.zip` into the workspace.
3. How to run the explicit runtime probe in an isolated persistent root.
4. How to run `python3 -m tools.extract.cli all`.
5. How to interpret unresolved dependencies, conflicts and runtime errors.
6. Which generated files feed the future wiki UI.
7. A clear statement that wiki crawling is prohibited for this dataset.

- [ ] **Step 2: Run the final verification set**

Run:

```bash
python3 -m unittest discover -s tests/extract -v
python3 -m tools.extract.cli validate
sqlite3 data/generated/wiki.sqlite 'select namespace, count(*) from entities group by namespace order by namespace;'
sqlite3 data/generated/wiki.sqlite 'select count(*) from evidence where selected = 1;'
git diff --check
```

Expected: tests and validation pass, both namespaces are reported, selected evidence count is nonzero, and `git diff --check` is silent.

- [ ] **Step 3: Review coverage against the design spec**

The audit must explicitly confirm:

- Every base-game entity has `requested_by` evidence from a Tu Tiên fact.
- Every recipe ingredient resolves to an entity.
- No source/evidence contains an HTTP URL.
- The original mod directories have not changed.
- Archive checksums still match `data/sources/game/manifest.json`.
- Runtime failures and low-confidence fields are visible in `coverage.json`.

- [ ] **Step 4: Commit**

```bash
git add docs/data-extraction.md
git commit -m "docs: document DST catalog refresh workflow"
```
