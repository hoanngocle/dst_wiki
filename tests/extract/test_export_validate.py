import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.extract.database import create_schema
from tools.extract.export_json import export_catalog
from tools.extract.validate import validate_catalog
from tools.extract import cli


class ExportValidateTests(unittest.TestCase):
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
                "insert into runtime_coverage values(?,?,?,?,?,?,?)",
                [
                    (
                        "coverage-a",
                        "tu_tien",
                        "xd_test_sword",
                        "buff_debuff",
                        "unobserved",
                        "no debuff component at spawn",
                        "{}",
                    ),
                    (
                        "coverage-b",
                        "tu_tien",
                        "xd_test_sword",
                        "world_spawn",
                        "unsupported",
                        "no safe reverse world-spawn registry",
                        "{}",
                    ),
                ],
            )
            db.commit()
            db.close()

            report = validate_catalog(path)

            self.assertEqual(
                report["runtime_coverage_summary"],
                {"unobserved": 1, "unsupported": 1},
            )
            self.assertEqual(
                [row["category"] for row in report["runtime_coverage"]],
                ["buff_debuff", "world_spawn"],
            )
            self.assertIn(
                {"code": "runtime_coverage_gaps", "count": 2},
                report["warnings"],
            )

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
             mock.patch.object(cli, "_export_stage", stage("export")), \
             mock.patch.object(cli, "_validate_stage", stage("validate", clean_report)), \
             mock.patch.object(cli, "run_runtime_probe") as runtime:
            self.assertEqual(cli.run_all(), clean_report)

        self.assertEqual(
            calls,
            ["extract-static", "import-runtime", "enrich-base", "build-db", "export", "validate"],
        )
        runtime.assert_not_called()


if __name__ == "__main__":
    unittest.main()
