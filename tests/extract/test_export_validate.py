import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from zipfile import ZipFile

from tools.extract.database import create_schema
from tools.extract.export_json import export_catalog
from tools.extract.validate import (
    _effect_other_audit_errors,
    _mob_boss_audit_errors,
    _structure_export_errors,
    validate_catalog,
)
from tools.extract.runtime_import import COVERAGE_CATEGORIES
from tools.extract import cli


class ExportValidateTests(unittest.TestCase):
    def test_mob_boss_validation_rejects_merged_member_still_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = root / "items.json"
            audit = root / "mob-audit.json"
            groups = root / "groups.json"
            mob = {
                "appearance": {"status": "unknown", "sources": []},
                "variants": [
                    {
                        "id": "base_game:champion",
                        "prefabId": "champion",
                        "name": "Champion",
                        "role": "phase",
                        "order": 1,
                        "sprite": None,
                    },
                    {
                        "id": "base_game:champion_dead",
                        "prefabId": "champion_dead",
                        "name": "Defeated Champion",
                        "role": "post_defeat",
                        "order": 2,
                        "sprite": None,
                    },
                ],
                "stats": [],
                "mechanics": [],
                "lootStatus": "unknown",
                "loot": [],
            }
            items.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {"id": "base_game:champion", "category": "boss", "mob": mob},
                            {"id": "base_game:champion_dead", "category": "structure", "mob": None},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {"total": 2, "keep": 1, "merge": 1, "exclude": 0},
                        "rows": [
                            {"id": "base_game:champion", "canonicalId": "base_game:champion", "action": "keep"},
                            {"id": "base_game:champion_dead", "canonicalId": "base_game:champion", "action": "merge"},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            groups.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "groups": [
                            {
                                "canonicalId": "base_game:champion",
                                "category": "boss",
                                "members": [
                                    {"id": "base_game:champion", "role": "phase", "order": 1},
                                    {"id": "base_game:champion_dead", "role": "post_defeat", "order": 2},
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = _mob_boss_audit_errors(items, audit, groups)

        self.assertIn(
            {"code": "merged_mob_member_is_public", "id": "base_game:champion_dead"},
            errors,
        )

    def test_mob_boss_validation_rejects_known_empty_and_missing_reward(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items = root / "items.json"
            audit = root / "mob-audit.json"
            groups = root / "groups.json"
            items.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:spider",
                                "category": "mob",
                                "mob": {
                                    "appearance": {"status": "unknown", "sources": []},
                                    "variants": [],
                                    "stats": [],
                                    "mechanics": [],
                                    "lootStatus": "known",
                                    "loot": [],
                                },
                            },
                            {
                                "id": "base_game:hound",
                                "category": "mob",
                                "mob": {
                                    "appearance": {"status": "unknown", "sources": []},
                                    "variants": [{"id": "base_game:hound"}],
                                    "stats": [],
                                    "mechanics": [],
                                    "lootStatus": "known",
                                    "loot": [
                                        {
                                            "item": {"id": "base_game:missing"},
                                            "minimum": 1,
                                            "maximum": 1,
                                            "method": "kill",
                                            "sourceVariant": "base_game:hound",
                                        }
                                    ],
                                },
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rows = [
                {"id": item_id, "canonicalId": item_id, "action": "keep"}
                for item_id in ("base_game:hound", "base_game:spider")
            ]
            audit.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {"total": 2, "keep": 2, "merge": 0, "exclude": 0},
                        "rows": rows,
                    }
                ),
                encoding="utf-8",
            )
            groups.write_text(
                json.dumps({"schema_version": 1, "groups": []}), encoding="utf-8"
            )

            errors = _mob_boss_audit_errors(items, audit, groups)

        self.assertIn(
            {"code": "known_mob_loot_is_empty", "id": "base_game:spider"},
            errors,
        )
        self.assertIn(
            {
                "code": "missing_mob_reward_reference",
                "id": "base_game:hound",
                "reward": "base_game:missing",
            },
            errors,
        )

    def test_effect_other_audit_rejects_public_exclusion_with_positive_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items_path = root / "items.json"
            audit_path = root / "effect-other-audit.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:helper",
                                "prefabId": "helper",
                                "namespace": "base_game",
                                "category": "effect",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {
                            "total": 1,
                            "keep": 0,
                            "exclude": 1,
                            "categories": {"effect": 1, "other": 0},
                        },
                        "rows": [
                            {
                                "id": "base_game:helper",
                                "category": "effect",
                                "action": "exclude",
                                "reasonCode": "empty_unreferenced",
                                "reason": "Fixture",
                                "signals": {"sprite": True},
                                "references": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = _effect_other_audit_errors(items_path, audit_path)

        self.assertEqual(
            errors,
            [
                {
                    "code": "excluded_effect_other_is_public",
                    "id": "base_game:helper",
                },
                {
                    "code": "excluded_effect_other_has_positive_signal",
                    "id": "base_game:helper",
                },
            ],
        )

    def test_prefab_coverage_accepts_effect_other_audit_exclusions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            with sqlite3.connect(db_path) as db:
                create_schema(db)
            scripts_path = root / "scripts.zip"
            with ZipFile(scripts_path, "w") as archive:
                archive.writestr("scripts/prefabs/helper.lua", "return {}")
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps({"schema_version": 6, "items": []}), encoding="utf-8"
            )
            audit_path = root / "effect-other-audit.json"
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {
                            "total": 1,
                            "keep": 0,
                            "exclude": 1,
                            "categories": {"effect": 1, "other": 0},
                        },
                        "rows": [
                            {
                                "id": "base_game:helper",
                                "prefabId": "helper",
                                "namespace": "base_game",
                                "category": "effect",
                                "action": "exclude",
                                "reasonCode": "empty_unreferenced",
                                "reason": "Fixture",
                                "signals": {"sprite": False},
                                "references": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                prefab_scripts_path=scripts_path,
                items_path=items_path,
                effect_other_audit_path=audit_path,
            )

        self.assertEqual(report["prefab_export_coverage_errors"], [])
        self.assertEqual(report["effect_other_audit_errors"], [])
        self.assertNotIn("effect_other_audit_errors", report["hard_failures"])

    def test_structure_validation_requires_craftable_construction_and_visual(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items_path = root / "items.json"
            audit_path = root / "structure-icon-audit.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:broken_station",
                                "prefabId": "broken_station",
                                "namespace": "base_game",
                                "category": "structure",
                                "sprite": None,
                                "recipe": {"outputCount": 1, "ingredients": []},
                                "structureDetails": {
                                    "origin": {
                                        "status": "known",
                                        "naturallySpawned": False,
                                        "craftable": True,
                                        "note": None,
                                    },
                                    "construction": {"status": "unknown"},
                                    "functions": {"status": "unknown"},
                                    "craftables": {"status": "none", "recipes": []},
                                    "destruction": {"status": "unknown"},
                                    "visual": {
                                        "status": "unknown",
                                        "sprite": None,
                                        "image": None,
                                    },
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {"total": 1},
                        "rows": [
                            {
                                "id": "base_game:broken_station",
                                "classification": "craftable_missing_asset",
                                "action": "keep",
                                "reason": "Fixture",
                                "evidence": [{"source": "fixture"}],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = _structure_export_errors(items_path, audit_path)

        self.assertEqual(
            errors,
            [
                {
                    "code": "craftable_structure_missing_construction",
                    "id": "base_game:broken_station",
                },
                {
                    "code": "craftable_structure_missing_visual",
                    "id": "base_game:broken_station",
                },
            ],
        )

    def test_structure_validation_requires_natural_note_and_audit_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            items_path = root / "items.json"
            audit_path = root / "structure-icon-audit.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:natural_station",
                                "prefabId": "natural_station",
                                "namespace": "base_game",
                                "category": "structure",
                                "sprite": None,
                                "recipe": None,
                                "structureDetails": {
                                    "origin": {
                                        "status": "known",
                                        "naturallySpawned": True,
                                        "craftable": False,
                                        "note": None,
                                    },
                                    "construction": {"status": "none"},
                                    "functions": {"status": "known"},
                                    "craftables": {"status": "none", "recipes": []},
                                    "destruction": {"status": "unknown"},
                                    "visual": {"status": "unknown"},
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {"total": 1},
                        "rows": [
                            {
                                "id": "base_game:natural_station",
                                "classification": "natural_structure",
                                "action": "keep",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            errors = _structure_export_errors(items_path, audit_path)

        self.assertEqual(
            errors,
            [
                {
                    "code": "invalid_structure_audit_reason",
                    "id": "base_game:natural_station",
                },
                {
                    "code": "invalid_structure_audit_evidence",
                    "id": "base_game:natural_station",
                },
                {
                    "code": "natural_structure_missing_note",
                    "id": "base_game:natural_station",
                },
            ],
        )

    def test_validation_hard_fails_prefab_module_export_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.commit()
            db.close()
            scripts_path = root / "scripts.zip"
            with ZipFile(scripts_path, "w") as archive:
                archive.writestr("scripts/prefabs/alpha.lua", "return {}")
                archive.writestr("scripts/prefabs/beta.lua", "return {}")
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:alpha",
                                "prefabId": "alpha",
                                "namespace": "base_game",
                                "category": "other",
                            },
                            {
                                "id": "base_game:gamma",
                                "prefabId": "gamma",
                                "namespace": "base_game",
                                "category": "other",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                prefab_scripts_path=scripts_path,
                items_path=items_path,
            )

        self.assertEqual(
            report["prefab_export_coverage_errors"],
            [{"missing": ["beta"], "unexpected": ["gamma"]}],
        )
        self.assertIn("prefab_export_coverage_errors", report["hard_failures"])

    def test_prefab_coverage_ignores_standalone_wiki_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.commit()
            db.close()
            scripts_path = root / "scripts.zip"
            with ZipFile(scripts_path, "w") as archive:
                archive.writestr("scripts/prefabs/alpha.lua", "return {}")
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:alpha",
                                "prefabId": "alpha",
                                "namespace": "base_game",
                                "wiki": None,
                            },
                            {
                                "id": "wiki:999",
                                "prefabId": "wiki-999",
                                "namespace": "base_game",
                                "wiki": {"mappingState": "unmatched"},
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                prefab_scripts_path=scripts_path,
                items_path=items_path,
            )

        self.assertEqual(report["prefab_export_coverage_errors"], [])
        self.assertNotIn("prefab_export_coverage_errors", report["hard_failures"])

    def test_prefab_coverage_accepts_published_recipe_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.commit()
            db.close()
            scripts_path = root / "scripts.zip"
            with ZipFile(scripts_path, "w") as archive:
                archive.writestr("scripts/prefabs/alpha.lua", "return {}")
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:alpha",
                                "prefabId": "alpha",
                                "namespace": "base_game",
                                "recipe": {
                                    "ingredients": [
                                        {"id": "base_game:pumpkin"}
                                    ]
                                },
                            },
                            {
                                "id": "base_game:pumpkin",
                                "prefabId": "pumpkin",
                                "namespace": "base_game",
                                "category": "item",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                prefab_scripts_path=scripts_path,
                items_path=items_path,
            )

        self.assertEqual(report["prefab_export_coverage_errors"], [])
        self.assertNotIn("prefab_export_coverage_errors", report["hard_failures"])

    def test_prefab_coverage_accepts_audited_technical_prefab_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.commit()
            db.close()
            scripts_path = root / "scripts.zip"
            with ZipFile(scripts_path, "w") as archive:
                archive.writestr("scripts/prefabs/alpha.lua", "return {}")
                archive.writestr("scripts/prefabs/beta.lua", "return {}")
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:alpha",
                                "prefabId": "alpha",
                                "namespace": "base_game",
                                "category": "other",
                                "structureDetails": None,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_path = root / "structure-icon-audit.json"
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {"total": 1},
                        "rows": [
                            {
                                "id": "base_game:beta",
                                "namespace": "base_game",
                                "prefabId": "beta",
                                "classification": "technical_prefab",
                                "action": "exclude",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                prefab_scripts_path=scripts_path,
                items_path=items_path,
                structure_audit_path=audit_path,
            )

        self.assertEqual(report["prefab_export_coverage_errors"], [])

    def test_validation_requires_complete_structure_details_and_resolved_repairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.commit()
            db.close()
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:researchlab",
                                "prefabId": "researchlab",
                                "namespace": "base_game",
                                "category": "structure",
                                "sprite": None,
                                "structureDetails": {
                                    "origin": {"status": "known"},
                                    "construction": {"status": "known"},
                                    "functions": {"status": "known"},
                                    "craftables": {"status": "known", "recipes": []},
                                    "destruction": {"status": "known"},
                                    "visual": {
                                        "status": "known",
                                        "kind": "wiki_image",
                                        "image": {"src": "/assets/wiki/researchlab.png"},
                                    },
                                },
                            },
                            {
                                "id": "base_game:goldnugget",
                                "prefabId": "goldnugget",
                                "namespace": "base_game",
                                "category": "item",
                                "structureDetails": None,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_path = root / "structure-icon-audit.json"
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {"total": 1},
                        "rows": [
                            {
                                "id": "base_game:researchlab",
                                "namespace": "base_game",
                                "prefabId": "researchlab",
                                "classification": "craftable_missing_asset",
                                "action": "repair",
                                "reason": "Fixture repair",
                                "evidence": [{"source": "fixture"}],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                items_path=items_path,
                structure_audit_path=audit_path,
            )
            self.assertEqual(report["structure_detail_errors"], [])

            payload = json.loads(items_path.read_text(encoding="utf-8"))
            payload["items"][0]["structureDetails"]["visual"]["status"] = "unknown"
            items_path.write_text(json.dumps(payload), encoding="utf-8")
            invalid = validate_catalog(
                db_path,
                items_path=items_path,
                structure_audit_path=audit_path,
            )

        self.assertEqual(
            invalid["structure_detail_errors"],
            [
                {
                    "code": "unresolved_structure_visual_repair",
                    "id": "base_game:researchlab",
                }
            ],
        )
        self.assertIn("structure_detail_errors", invalid["hard_failures"])

    def test_validation_rejects_unresolved_structure_recipe_ingredients(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.commit()
            db.close()
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 6,
                        "items": [
                            {
                                "id": "base_game:researchlab",
                                "prefabId": "researchlab",
                                "namespace": "base_game",
                                "category": "structure",
                                "sprite": {"src": "/assets/game/researchlab.png"},
                                "structureDetails": {
                                    "origin": {"status": "known"},
                                    "construction": {"status": "known"},
                                    "functions": {"status": "known"},
                                    "craftables": {
                                        "status": "known",
                                        "recipes": [
                                            {
                                                "result": {
                                                    "id": "base_game:missing_result"
                                                },
                                                "ingredients": [
                                                    {"id": "base_game:missing"}
                                                ],
                                                "station": "base_game:researchlab",
                                            }
                                        ],
                                    },
                                    "destruction": {"status": "unknown"},
                                    "visual": {"status": "known"},
                                },
                            },
                            {
                                "id": "base_game:rope",
                                "prefabId": "rope",
                                "namespace": "base_game",
                                "category": "item",
                                "structureDetails": None,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_path = root / "structure-icon-audit.json"
            audit_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "summary": {
                            "total": 0,
                            "keep": 0,
                            "repair": 0,
                            "exclude": 0,
                            "classifications": {},
                        },
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )

            report = validate_catalog(
                db_path,
                items_path=items_path,
                structure_audit_path=audit_path,
            )

        self.assertEqual(
            report["structure_detail_errors"],
            [
                {
                    "code": "unresolved_structure_craftable_result",
                    "id": "base_game:researchlab",
                    "result": "base_game:missing_result",
                },
                {
                    "code": "unresolved_structure_craftable_ingredient",
                    "id": "base_game:researchlab",
                    "ingredient": "base_game:missing",
                    "result": "base_game:missing_result",
                }
            ],
        )
        self.assertIn("structure_detail_errors", report["hard_failures"])

    def write_archive_fixture(self, root: Path):
        sources = root / "data" / "sources" / "game"
        sources.mkdir(parents=True, exist_ok=True)
        paths = {
            "scripts.zip": sources / "scripts.zip",
            "images.zip": sources / "images.zip",
        }
        paths["scripts.zip"].write_bytes(b"scripts")
        paths["images.zip"].write_bytes(b"images")
        manifest = {
            "schema_version": 1,
            "files": {
                name: {
                    "size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for name, path in paths.items()
            },
        }
        manifest_path = sources / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path, manifest, paths

    def build_catalog(self, root: Path) -> Path:
        _manifest_path, manifest, _paths = self.write_archive_fixture(root)
        path = root / "catalog.sqlite"
        db = sqlite3.connect(path)
        create_schema(db)
        db.executemany(
            "insert into sources values(?,?,?,?,?)",
            [
                ("fixture", "mod_static", "mod/fixture.lua", "1", "a" * 64),
                ("scripts", "snapshot", "data/sources/game/scripts.zip", "snapshot", manifest["files"]["scripts.zip"]["sha256"]),
                ("images", "snapshot", "data/sources/game/images.zip", "snapshot", manifest["files"]["images.zip"]["sha256"]),
            ],
        )
        db.executemany(
            "insert into entities(namespace,prefab_id,entity_type,is_inventory_item,name_vi,name_en,description_vi,description_en,icon_key,confidence) values(?,?,?,?,?,?,?,?,?,?)",
            [
                ("base_game", "goldnugget", "inventory_item", 1, "Vàng", "Gold Nugget", None, None, "base_game:goldnugget", 1.0),
                ("tu_tien", "xd_test_sword", "inventory_item", 1, "Kiếm Thử", None, "Một thanh kiếm", None, "tu_tien:xd_test_sword", 1.0),
            ],
        )
        db.execute(
            "insert into recipes values(?,?,?,?,?,?)",
            ("tu_tien:xd_test_sword", "tu_tien", "xd_test_sword", 1, "SCIENCE_ONE", '{"filters":["WEAPONS"]}'),
        )
        db.execute(
            "insert into recipe_ingredients values(?,?,?,?,?)",
            ("tu_tien:xd_test_sword", 0, "base_game", "goldnugget", 2),
        )
        db.execute(
            "insert into acquisition_sources values(?,?,?,?,?,?,?,?,?,?)",
            ("acq", "tu_tien", "xd_test_sword", "craft", None, None, None, None, None, "{}"),
        )
        db.executemany(
            "insert into runtime_coverage values(?,?,?,?,?,?,?)",
            [
                (
                    f"coverage-{category}",
                    "tu_tien",
                    "xd_test_sword",
                    category,
                    "unobserved",
                    "fixture",
                    "{}",
                )
                for category in sorted(COVERAGE_CATEGORIES)
            ],
        )
        db.execute(
            "insert into stats values(?,?,?,?,?,?,?)",
            ("tu_tien", "xd_test_sword", "damage", 68, None, "hp", 1.0),
        )
        db.execute(
            "insert into effects values(?,?,?,?,?,?,?)",
            ("effect", "tu_tien", "xd_test_sword", "onhit", "planar_damage", '{"amount":5}', 3),
        )
        db.execute(
            "insert into entity_relations values(?,?,?,?,?,?,?)",
            ("relation", "tu_tien", "xd_test_sword", "upgrades_to", "base_game", "goldnugget", '{"level":2}'),
        )
        db.execute(
            "insert into assets values(?,?,?,?,?,?,?,?)",
            ("asset", "tu_tien", "xd_test_sword", "inventory", "images/item.xml", "images/item.tex", "xd_test_sword.tex", '{"u1":0,"u2":1,"v1":0,"v2":1}'),
        )
        raw_asset = {
            "asset_type": "inventory",
            "available": True,
            "texture_sha256": "b" * 64,
        }
        db.execute(
            "insert into evidence values(?,?,?,?,?,?,?,?)",
            ("evidence", "asset", "asset", "fixture", "element:1", json.dumps(raw_asset), 1.0, 1),
        )
        db.commit()
        db.close()
        return path

    def test_export_is_stable_complete_and_has_asset_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = self.build_catalog(root)
            catalog = root / "catalog.json"
            assets = root / "assets.json"

            export_catalog(db, catalog, assets)
            first_catalog = catalog.read_bytes()
            first_assets = assets.read_bytes()
            export_catalog(db, catalog, assets)

            self.assertEqual(catalog.read_bytes(), first_catalog)
            self.assertEqual(assets.read_bytes(), first_assets)
            payload = json.loads(first_catalog)
            self.assertEqual(
                [(row["namespace"], row["prefab_id"]) for row in payload["entities"]],
                [("base_game", "goldnugget"), ("tu_tien", "xd_test_sword")],
            )
            sword = payload["entities"][1]
            self.assertEqual(sword["recipes"][0]["ingredients"][0], {"amount": 2.0, "key": "base_game:goldnugget", "position": 0})
            self.assertEqual(sword["acquisition"][0]["type"], "craft")
            self.assertEqual(sword["stats"][0]["value"], 68.0)
            self.assertEqual(sword["effects"][0]["value"], {"amount": 5})
            self.assertEqual(sword["relations"][0]["target"], "base_game:goldnugget")
            asset = json.loads(first_assets)["assets"][0]
            self.assertTrue(asset["available"])
            self.assertEqual(asset["texture_sha256"], "b" * 64)
            self.assertEqual(asset["evidence"][0]["source"]["path"], "mod/fixture.lua")

    def test_validation_reports_integrity_coverage_and_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.execute(
                "insert into evidence values(?,?,?,?,?,?,?,?)",
                ("url", "name", "tu_tien:xd_test_sword", "fixture", "line:1", '{"note":"https://example.invalid/wiki"}', 1.0, 0),
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(report["entity_counts"], {"base_game": 1, "tu_tien": 1})
            self.assertEqual(report["foreign_key_errors"], [])
            self.assertEqual(report["unresolved_dependencies"], [])
            self.assertEqual(len(report["wiki_urls"]), 1)
            self.assertEqual(report["hard_failures"], ["wiki_urls"])
            self.assertIn("coverage", report)
            self.assertIn("warnings", report)

    def test_validation_surfaces_low_confidence_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.execute(
                "insert into evidence values(?,?,?,?,?,?,?,?)",
                (
                    "low-confidence-relation",
                    "relation",
                    "relation",
                    "fixture",
                    "line:17",
                    '{"relation_type":"string_alias"}',
                    0.5,
                    1,
                ),
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(
                report["low_confidence_fields"],
                [
                    {
                        "evidence_id": "low-confidence-relation",
                        "record_type": "relation",
                        "record_id": "relation",
                        "source_id": "fixture",
                        "source_kind": "mod_static",
                        "locator": "line:17",
                        "confidence": 0.5,
                        "selected": True,
                    }
                ],
            )
            self.assertIn(
                {"code": "low_confidence_fields_present", "count": 1},
                report["warnings"],
            )

    def test_validation_surfaces_explicit_runtime_coverage_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.executemany(
                "update runtime_coverage set status=?,reason=? "
                "where namespace=? and prefab_id=? and category=?",
                [
                    (
                        "unobserved",
                        "no debuff component at spawn",
                        "tu_tien",
                        "xd_test_sword",
                        "buff_debuff",
                    ),
                    (
                        "unsupported",
                        "no safe reverse world-spawn registry",
                        "tu_tien",
                        "xd_test_sword",
                        "world_spawn",
                    ),
                ],
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(
                report["runtime_coverage_summary"],
                {"unobserved": 8, "unsupported": 1},
            )
            self.assertEqual(len(report["runtime_coverage"]), 9)
            self.assertIn(
                {"code": "runtime_coverage_gaps", "count": 9},
                report["warnings"],
            )

    def test_validation_hard_fails_missing_or_unexpected_runtime_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.execute(
                "delete from runtime_coverage where namespace='tu_tien' "
                "and prefab_id='xd_test_sword' and category='world_spawn'"
            )
            db.execute(
                "insert into runtime_coverage values(?,?,?,?,?,?,?)",
                (
                    "coverage-unexpected",
                    "tu_tien",
                    "xd_test_sword",
                    "unknown_category",
                    "unobserved",
                    "fixture",
                    "{}",
                ),
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(
                report["runtime_coverage_errors"],
                [
                    {
                        "namespace": "tu_tien",
                        "prefab_id": "xd_test_sword",
                        "missing_categories": ["world_spawn"],
                        "unexpected_categories": ["unknown_category"],
                        "duplicate_categories": [],
                    }
                ],
            )
            self.assertIn("runtime_coverage_errors", report["hard_failures"])

    def test_validation_does_not_require_runtime_rows_for_non_target_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.execute(
                "insert into entities(namespace,prefab_id,entity_type,is_inventory_item,"
                "name_vi,name_en,description_vi,description_en,icon_key,confidence) "
                "values(?,?,?,?,?,?,?,?,?,?)",
                (
                    "tu_tien",
                    "xd_child_variant",
                    "unknown",
                    0,
                    None,
                    None,
                    None,
                    None,
                    None,
                    1.0,
                ),
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(report["runtime_coverage_errors"], [])
            self.assertNotIn("runtime_coverage_errors", report["hard_failures"])

    def test_validation_lists_every_tu_tien_inventory_item_missing_a_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.executemany(
                "insert into entities(namespace,prefab_id,entity_type,is_inventory_item,name_vi,name_en,description_vi,description_en,icon_key,confidence) values(?,?,?,?,?,?,?,?,?,?)",
                [
                    ("tu_tien", "xd_zeta", "inventory_item", 1, None, None, None, None, None, 1.0),
                    ("tu_tien", "xd_alpha", "inventory_item", 1, "", None, None, None, None, 1.0),
                    ("tu_tien", "xd_named", "inventory_item", 1, "Có tên", None, None, None, None, 1.0),
                    ("base_game", "base_missing", "inventory_item", 1, None, None, None, None, None, 1.0),
                    ("tu_tien", "xd_non_item", "unknown", 0, None, None, None, None, None, 1.0),
                ],
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

        self.assertEqual(report["missing_inventory_names"], ["xd_alpha", "xd_zeta"])
        self.assertIn(
            {"code": "missing_inventory_names", "count": 2}, report["warnings"]
        )
        self.assertNotIn("missing_inventory_names", report["hard_failures"])

    def test_validation_scans_evidence_locator_and_nested_manifest_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.execute(
                "insert into evidence values(?,?,?,?,?,?,?,?)",
                ("locator-url", "name", "tu_tien:xd_test_sword", "fixture", "https://locator.invalid/wiki", "{}", 1.0, 0),
            )
            db.commit()
            db.close()
            manifest_path = root / "data/sources/game/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["metadata"] = {
                "nested": [{"https://manifest-key.invalid/wiki": "https://manifest-value.invalid/wiki"}]
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            report = validate_catalog(path)

            locations = {item["location"] for item in report["wiki_urls"]}
            self.assertTrue(any(location.startswith("evidence:locator-url.locator") for location in locations))
            self.assertTrue(any(location.startswith("manifest:") for location in locations))
            self.assertEqual(len(report["wiki_urls"]), 3)

    def test_validation_hard_fails_foreign_keys_and_unresolved_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self.build_catalog(root)
            db = sqlite3.connect(path)
            db.execute(
                "insert into recipe_ingredients values(?,?,?,?,?)",
                ("tu_tien:xd_test_sword", 1, "base_game", "missing", 1),
            )
            db.execute(
                "insert into extraction_errors values(?,?,?,?,?,?,?,?)",
                ("unresolved", "bundle", None, "bundle", "ingredient:1", 0, "unresolved_base_game_dependency", '{"prefab_id":"missing"}'),
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(len(report["foreign_key_errors"]), 1)
            self.assertEqual(report["unresolved_dependencies"][0]["subject"], "missing")
            self.assertEqual(
                report["hard_failures"],
                ["foreign_key_errors", "unresolved_dependencies"],
            )

    def test_validation_checks_snapshot_manifest_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data"
            generated = data / "generated"
            sources = data / "sources" / "game"
            generated.mkdir(parents=True)
            sources.mkdir(parents=True)
            scripts = sources / "scripts.zip"
            images = sources / "images.zip"
            scripts.write_bytes(b"scripts")
            images.write_bytes(b"images")
            manifest = {
                "schema_version": 1,
                "files": {
                    name: {"size": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                    for name, path in (("scripts.zip", scripts), ("images.zip", images))
                },
            }
            (sources / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            db_path = generated / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.executemany(
                "insert into sources values(?,?,?,?,?)",
                [
                    ("scripts", "base_game_source", "data/sources/game/scripts.zip", "snapshot", manifest["files"]["scripts.zip"]["sha256"]),
                    ("images", "base_game_source", "data/sources/game/images.zip", "snapshot", manifest["files"]["images.zip"]["sha256"]),
                ],
            )
            db.commit()
            db.close()

            self.assertEqual(validate_catalog(db_path)["archive_checksum_errors"], [])
            scripts.write_bytes(b"changed")
            self.assertEqual(len(validate_catalog(db_path)["archive_checksum_errors"]), 1)

    def test_validation_requires_both_archive_provenance_rows_for_base_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.execute(
                "insert into entities values(?,?,?,?,?,?,?,?,?,?)",
                ("base_game", "goldnugget", "inventory_item", 1, None, None, None, None, None, 1.0),
            )
            db.commit()
            db.close()

            report = validate_catalog(db_path)

            missing = {
                error.get("archive")
                for error in report["archive_checksum_errors"]
                if error["code"] == "missing_source_archive"
            }
            self.assertEqual(missing, {"scripts.zip", "images.zip"})
            self.assertIn("archive_checksum_errors", report["hard_failures"])

    def test_validation_rejects_one_missing_archive_provenance_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest, _paths = self.write_archive_fixture(root)
            db_path = root / "wiki.sqlite"
            db = sqlite3.connect(db_path)
            create_schema(db)
            db.execute(
                "insert into sources values(?,?,?,?,?)",
                ("scripts", "custom_snapshot_kind", "data/sources/game/scripts.zip", "snapshot", manifest["files"]["scripts.zip"]["sha256"]),
            )
            db.commit()
            db.close()

            report = validate_catalog(db_path, manifest_path)

            missing = [
                error for error in report["archive_checksum_errors"]
                if error["code"] == "missing_source_archive"
            ]
            self.assertEqual([error["archive"] for error in missing], ["images.zip"])

    def test_all_runs_exact_offline_stage_order_without_runtime_server(self):
        calls = []

        def stage(name, result=None):
            def run(*args, **kwargs):
                calls.append(name)
                return result
            return run

        clean_report = {"hard_failures": []}
        with mock.patch.object(cli, "_extract_static_stage", stage("extract-static")), \
             mock.patch.object(cli, "_import_runtime_stage", stage("import-runtime")), \
             mock.patch.object(cli, "_enrich_base_stage", stage("enrich-base")), \
             mock.patch.object(cli, "_build_db_stage", stage("build-db")), \
             mock.patch.object(cli, "_import_wiki_stage", stage("import-wiki")), \
             mock.patch.object(cli, "_export_stage", stage("export")), \
             mock.patch.object(cli, "_validate_stage", stage("validate", clean_report)), \
             mock.patch.object(cli, "run_runtime_probe") as runtime:
            self.assertEqual(cli.run_all(), clean_report)

        self.assertEqual(
            calls,
            [
                "extract-static",
                "import-runtime",
                "enrich-base",
                "build-db",
                "import-wiki",
                "export",
                "validate",
            ],
        )
        runtime.assert_not_called()

    def test_export_stage_writes_compact_frontend_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            catalog = root / "catalog.json"
            assets = root / "assets.json"
            items = root / "items.json"
            textures = root / "item-textures.json"
            detail_overrides = root / "item-details.json"
            detail_report = root / "item-details-report.json"
            structure_audit = root / "structure-icon-audit.json"
            effect_other_audit = root / "effect-other-audit.json"
            mob_audit = root / "mob-boss-audit.json"
            mob_groups = root / "mob-groups.json"
            mob_wiki = root / "mob-wiki-pages.jsonl"

            with mock.patch.object(cli, "export_catalog") as export_catalog, \
                 mock.patch.object(cli, "export_items") as export_items:
                cli._export_stage(
                    database,
                    catalog,
                    assets,
                    items,
                    textures,
                    detail_overrides,
                    detail_report,
                    structure_audit,
                    effect_other_audit,
                    mob_audit,
                    mob_groups,
                    mob_wiki,
                )

            export_catalog.assert_called_once_with(database, catalog, assets)
            export_items.assert_called_once_with(
                database,
                catalog,
                assets,
                items,
                textures,
                detail_overrides_path=detail_overrides,
                detail_report_path=detail_report,
                structure_audit_path=structure_audit,
                effect_other_audit_path=effect_other_audit,
                mob_audit_path=mob_audit,
                mob_groups_path=mob_groups,
                mob_wiki_path=mob_wiki,
            )

    def test_export_cli_exposes_item_detail_paths(self):
        args = cli.build_parser().parse_args(["export"])

        self.assertEqual(
            args.detail_overrides,
            Path("data/manual/tu_tien_item_details.json"),
        )
        self.assertEqual(
            args.detail_report,
            Path("data/generated/tu-tien-item-details-report.json"),
        )
        self.assertEqual(
            args.structure_audit,
            Path("data/generated/structure-icon-audit.json"),
        )
        self.assertEqual(
            args.effect_other_audit,
            Path("data/generated/effect-other-audit.json"),
        )
        self.assertEqual(
            args.mob_audit,
            Path("data/generated/mob-boss-audit.json"),
        )
        self.assertEqual(
            args.mob_groups,
            Path("data/manual/mob-variant-groups.json"),
        )
        self.assertEqual(
            args.mob_wiki,
            Path("data/crawled/dontstarve-wiki/pages.jsonl"),
        )

        validate_args = cli.build_parser().parse_args(["validate"])
        self.assertEqual(
            validate_args.effect_other_audit,
            Path("data/generated/effect-other-audit.json"),
        )
        self.assertEqual(
            validate_args.mob_audit,
            Path("data/generated/mob-boss-audit.json"),
        )
        self.assertEqual(
            validate_args.mob_groups,
            Path("data/manual/mob-variant-groups.json"),
        )

    def test_publish_assets_cli_has_explicit_inputs(self):
        args = cli.build_parser().parse_args(["publish-assets"])

        self.assertEqual(args.textures, Path("data/generated/item-textures.json"))
        self.assertEqual(args.mod_root, Path("mod/3721846643"))
        self.assertEqual(args.images, Path("data/sources/game/images.zip"))
        self.assertEqual(args.manifest, Path("data/sources/game/manifest.json"))
        self.assertEqual(args.output, Path("public/assets/game"))
        self.assertEqual(args.decoder, "ktech")

    def test_publish_assets_cli_dispatches_explicit_paths(self):
        arguments = [
            "dst-extract",
            "publish-assets",
            "--textures",
            "custom-textures.json",
            "--mod-root",
            "custom-mod",
            "--images",
            "custom-images.zip",
            "--manifest",
            "custom-manifest.json",
            "--output",
            "custom-output",
            "--decoder",
            "custom-ktech",
        ]
        published = [Path("custom-output/a.png")]
        with mock.patch("sys.argv", arguments), \
             mock.patch.object(cli, "publish_web_assets", return_value=published) as publish:
            self.assertEqual(cli.main(), 0)

        publish.assert_called_once_with(
            Path("custom-textures.json"),
            Path("custom-mod"),
            Path("custom-images.zip"),
            Path("custom-manifest.json"),
            Path("custom-output"),
            "custom-ktech",
        )


if __name__ == "__main__":
    unittest.main()
