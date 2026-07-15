import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.extract import cli
from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef
from tools.extract.database import write_database
from tools.extract.normalize import normalize


def source(source_id, kind, marker):
    return SourceRef(source_id, kind, f"{source_id}.json", "18.0.10", marker * 64)


class DatabaseTests(unittest.TestCase):
    def test_build_database_stage_passes_collected_game_text_to_writer(self):
        static = source("static", "mod_static", "a")
        bundle = FactBundle(1, [static], [], [])
        catalog = normalize([bundle])
        text_source = SourceRef(
            "game-text:mod/strings.lua",
            "mod_static",
            "mod/strings.lua",
            "18.0.10",
            "b" * 64,
        )
        text_rows = [
            {
                "text_id": "c" * 64,
                "text_key": "STRINGS.XD_UI.OPEN",
                "value_vi": "Mở ra",
                "source_id": text_source.source_id,
                "locator": "line:1",
            }
        ]
        with mock.patch.object(cli, "load_bundle", return_value=bundle), \
             mock.patch.object(cli, "load_runtime_bundle", return_value=bundle), \
             mock.patch.object(cli, "static_mod_version", return_value="18.0.10"), \
             mock.patch.object(cli, "static_runtime_target_ids", return_value=[]), \
             mock.patch.object(cli, "normalize", return_value=catalog), \
             mock.patch.object(cli, "collect_game_text", return_value=([text_source], text_rows), create=True), \
             mock.patch.object(cli, "write_database") as write:
            cli._build_db_stage(Path("static.json"), Path("runtime.json"), Path("base.json"), Path("wiki.sqlite"))

        write.assert_called_once_with(Path("wiki.sqlite"), catalog, [text_source], text_rows)

    def test_persists_game_text_with_source_foreign_key(self):
        text_source = SourceRef(
            "game-text:mod/strings.lua",
            "mod_static",
            "mod/strings.lua",
            "18.0.10",
            "a" * 64,
        )
        text_row = {
            "text_id": "b" * 64,
            "text_key": "STRINGS.XD_UI.OPEN",
            "value_vi": "Mở ra",
            "source_id": text_source.source_id,
            "locator": "line:42",
        }
        catalog = normalize([FactBundle(1, [], [], [])])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(
                path,
                catalog,
                game_text_sources=[text_source],
                game_text_rows=[text_row],
            )
            db = sqlite3.connect(path)
            self.assertEqual(
                db.execute(
                    "select text_key,value_vi,source_id,locator from game_text"
                ).fetchone(),
                ("STRINGS.XD_UI.OPEN", "Mở ra", text_source.source_id, "line:42"),
            )
            self.assertEqual(db.execute("pragma foreign_key_check").fetchall(), [])
            db.close()

    def test_generic_description_wins_display_while_recipe_conflict_is_preserved(self):
        static = source("static", "mod_translation", "a")
        key = EntityKey("base_game", "goldnugget")
        facts = [
            Fact("entity", key, {"entity_type": "unknown"}, static, 1.0, "entity"),
            Fact(
                "description",
                key,
                {"lang": "vi", "value": "Mô tả vật thể", "description_type": "generic"},
                static,
                0.9,
                "context:generic",
            ),
            Fact(
                "description",
                key,
                {"lang": "vi", "value": "Mô tả công thức", "description_type": "recipe"},
                static,
                0.9,
                "context:recipe",
            ),
        ]

        catalog = normalize([FactBundle(1, [static], facts, [])])

        self.assertEqual(catalog.entities[0]["description_vi"], "Mô tả vật thể")
        self.assertEqual(len(catalog.conflicts), 1)
        self.assertEqual(catalog.conflicts[0]["field_key"], "description:vi")
        selected = [
            row
            for row in catalog.evidence
            if row["record_type"] == "description" and row["selected"]
        ]
        self.assertEqual(len(selected), 1)
        self.assertEqual(json.loads(selected[0]["raw_value_json"])["description_type"], "generic")

    def test_runtime_coverage_facts_are_persisted_with_provenance(self):
        runtime = source("runtime", "runtime_probe", "b")
        key = EntityKey("tu_tien", "wall_luoshen")
        facts = [
            Fact(
                "entity",
                key,
                {"entity_type": "structure"},
                runtime,
                1.0,
                "targets:0",
            ),
            Fact(
                "coverage",
                key,
                {
                    "category": "world_spawn",
                    "status": "unsupported",
                    "reason": "no safe reverse world-spawn registry",
                    "details": {},
                },
                runtime,
                1.0,
                "coverage:0",
            ),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, normalize([FactBundle(1, [runtime], facts, [])]))
            db = sqlite3.connect(path)
            self.assertEqual(
                db.execute(
                    "select namespace,prefab_id,category,status,reason,details_json "
                    "from runtime_coverage"
                ).fetchone(),
                (
                    "tu_tien",
                    "wall_luoshen",
                    "world_spawn",
                    "unsupported",
                    "no safe reverse world-spawn registry",
                    "{}",
                ),
            )
            self.assertEqual(
                db.execute(
                    "select record_type from evidence where locator='coverage:0'"
                ).fetchone()[0],
                "coverage",
            )
            db.close()

    def test_runtime_wins_and_conflict_keeps_both_evidence_rows(self):
        static = source("static", "mod_static", "a")
        runtime = source("runtime", "runtime_probe", "b")
        key = EntityKey("tu_tien", "xd_test_sword")
        bundles = [
            FactBundle(
                1,
                [static],
                [Fact("stat", key, {"key": "damage", "value": 60, "unit": "hp"}, static, 0.9, "line:1")],
                [],
            ),
            FactBundle(
                1,
                [runtime],
                [Fact("stat", key, {"key": "damage", "value": 68, "unit": "hp"}, runtime, 1.0, "prefabs:0")],
                [],
            ),
        ]

        catalog = normalize(bundles)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, catalog)
            db = sqlite3.connect(path)
            self.assertEqual(
                db.execute("select value_num from stats where stat_key='damage'").fetchone()[0],
                68,
            )
            self.assertEqual(db.execute("select count(*) from evidence").fetchone()[0], 2)
            self.assertEqual(db.execute("select sum(selected) from evidence").fetchone()[0], 1)
            conflict = db.execute(
                "select subject_key, field_key, candidates_json, selected_json from conflicts"
            ).fetchone()
            self.assertEqual(conflict[:2], ("tu_tien:xd_test_sword", "stat:damage"))
            self.assertEqual(json.loads(conflict[3])["value"], 68)
            self.assertEqual(len(json.loads(conflict[2])), 2)
            self.assertEqual(db.execute("pragma foreign_key_check").fetchall(), [])
            db.close()

    def test_normalizes_real_fact_shapes_and_keeps_unselected_acquisition_source(self):
        runtime = source("runtime", "runtime_probe", "b")
        base = source("base", "base_game_source", "c")
        sword = EntityKey("tu_tien", "xd_test_sword")
        gold = EntityKey("base_game", "goldnugget")
        facts = [
            Fact("entity", sword, {"entity_type": "inventory_item", "discovered_by": "runtime_prefab"}, runtime, 1.0, "prefabs:0"),
            Fact("name", sword, {"lang": "vi", "value": "Kiếm Thử"}, runtime, 1.0, "names:0"),
            Fact("recipe", sword, {"output_count": 1, "tech": "SCIENCE_ONE", "filters": ["WEAPONS"], "builder_tags": ["xd"]}, runtime, 1.0, "recipes:0"),
            Fact("ingredient", sword, {"position": 0, "amount": 2, "ingredient": {"prefab_id": "goldnugget", "dependency_candidate": True, "resolution": "unresolved"}}, runtime, 1.0, "recipes:0:ingredients:0"),
            Fact("acquisition", sword, {"type": "craft", "source": None, "chance": None, "conditions": {}}, runtime, 1.0, "recipes:0"),
            Fact("relation", sword, {"relation": "upgrades_to", "target": {"namespace": "base_game", "prefab_id": "goldnugget", "resolution": "resolved"}, "level": 2}, runtime, 1.0, "relations:0"),
            Fact("asset", sword, {"asset_type": "inventory", "atlas": "images/items.xml", "texture": "images/items.tex", "element": "xd_test_sword.tex", "uv": {"u1": 0, "u2": 1, "v1": 0, "v2": 1}, "available": True}, runtime, 1.0, "element:1"),
            Fact("entity", gold, {"entity_type": "unknown", "discovered_by": "prefab_registry", "requested_by": [{"relation": "ingredient", "subject": "tu_tien:xd_test_sword"}]}, base, 1.0, "scripts/prefabs/goldnugget.lua"),
            Fact("stat", gold, {"key": "damage", "source_expression": "TUNING.GOLD_DAMAGE"}, base, 0.9, "scripts/prefabs/goldnugget.lua:line:2"),
            Fact("acquisition", gold, {"type": "drop", "source": {"namespace": "base_game", "prefab_id": "evidence_only_mob", "resolution": "evidence_only"}, "target": {"namespace": "base_game", "prefab_id": "goldnugget", "resolution": "resolved"}, "chance": 0.25, "count": 2, "conditions": {}, "source_member": "scripts/prefabs/mob.lua", "source_expression": "AddChanceLoot(...)"}, base, 0.9, "scripts/prefabs/mob.lua:line:4"),
        ]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, normalize([FactBundle(1, [runtime, base], facts, [])]))
            db = sqlite3.connect(path)
            self.assertEqual(
                db.execute("select namespace,prefab_id from entities order by 1,2").fetchall(),
                [("base_game", "goldnugget"), ("tu_tien", "xd_test_sword")],
            )
            self.assertEqual(
                db.execute("select ingredient_namespace,ingredient_id,amount from recipe_ingredients").fetchone(),
                ("base_game", "goldnugget", 2.0),
            )
            source_row = db.execute(
                "select source_type,source_namespace,source_id,conditions_json from acquisition_sources where source_type='drop'"
            ).fetchone()
            self.assertEqual(source_row[:3], ("drop", None, None))
            self.assertEqual(
                json.loads(source_row[3])["source_identity"]["prefab_id"],
                "evidence_only_mob",
            )
            self.assertEqual(db.execute("select value_text from stats").fetchone()[0], "TUNING.GOLD_DAMAGE")
            self.assertEqual(db.execute("select count(*) from entity_relations").fetchone()[0], 1)
            self.assertEqual(db.execute("select count(*) from assets").fetchone()[0], 1)
            self.assertEqual(db.execute("pragma foreign_key_check").fetchall(), [])
            db.close()

    def test_missing_recipe_ingredient_is_an_explicit_validation_error(self):
        runtime = source("runtime", "runtime_probe", "b")
        sword = EntityKey("tu_tien", "xd_test_sword")
        bundle = FactBundle(
            1,
            [runtime],
            [
                Fact("recipe", sword, {"output_count": 1, "tech": None}, runtime, 1.0, "recipes:0"),
                Fact("ingredient", sword, {"position": 0, "amount": 1, "ingredient": {"namespace": "base_game", "prefab_id": "missing"}}, runtime, 1.0, "recipes:0:ingredients:0"),
            ],
            [],
        )

        with self.assertRaisesRegex(ValueError, "recipe ingredient.*base_game:missing"):
            normalize([bundle])

    def test_database_rebuild_has_deterministic_rows_and_ids(self):
        static = source("static", "mod_static", "a")
        key = EntityKey("tu_tien", "xd_item")
        bundle = FactBundle(
            1,
            [static],
            [
                Fact("entity", key, {"entity_type": "item"}, static, 0.9, "line:2"),
                Fact("name", key, {"lang": "vi", "value": "Vật phẩm"}, static, 1.0, "line:1"),
            ],
            [{"code": "sample_warning", "detail": "kept"}],
        )

        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.sqlite"
            second = Path(tmp) / "second.sqlite"
            write_database(first, normalize([bundle]))
            write_database(second, normalize([bundle]))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            db = sqlite3.connect(first)
            ids = {
                table: [row[0] for row in db.execute(f"select {column} from {table} order by {column}")]
                for table, column in (
                    ("evidence", "evidence_id"),
                    ("extraction_errors", "error_id"),
                )
            }
            self.assertEqual(ids, {table: sorted(values) for table, values in ids.items()})
            self.assertTrue(all(len(value) == 64 for values in ids.values() for value in values))
            db.close()

    def test_identical_extractor_errors_are_semantically_deduplicated(self):
        warning = {"code": "runtime_spawn_failed", "prefab": "xd_item", "detail": "boom"}
        catalog = normalize([FactBundle(1, [], [], [warning, dict(warning)])])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, catalog)
            db = sqlite3.connect(path)
            self.assertEqual(db.execute("select count(*) from extraction_errors").fetchone()[0], 1)
            db.close()

    def test_writer_inserts_each_table_in_primary_key_order(self):
        alpha = source("alpha", "mod_static", "a")
        zeta = source("zeta", "mod_static", "b")
        catalog = normalize([FactBundle(1, [zeta, alpha], [], [])])
        catalog.sources.reverse()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, catalog)
            db = sqlite3.connect(path)
            self.assertEqual(
                [row[0] for row in db.execute("select source_id from sources order by rowid")],
                ["alpha", "zeta"],
            )
            db.close()

    def test_only_explicit_evidence_only_acquisition_sources_may_be_unselected(self):
        runtime = source("runtime", "runtime_probe", "b")
        target = EntityKey("tu_tien", "xd_target")

        invalid_references = [
            {"namespace": "base_game", "prefab_id": "missing", "resolution": "resolved"},
            {"namespace": "base_game", "resolution": "resolved"},
        ]
        for reference in invalid_references:
            with self.subTest(reference=reference):
                fact = Fact(
                    "acquisition",
                    target,
                    {"type": "drop", "source": reference, "conditions": {}},
                    runtime,
                    1.0,
                    "loot:0",
                )
                with self.assertRaisesRegex(ValueError, "acquisition source"):
                    normalize([FactBundle(1, [runtime], [fact], [])])

        shared_base = EntityKey("base_game", "shared")
        shared_mod = EntityKey("tu_tien", "shared")
        ambiguous = [
            Fact("entity", shared_base, {"entity_type": "unknown"}, runtime, 1.0),
            Fact("entity", shared_mod, {"entity_type": "unknown"}, runtime, 1.0),
            Fact(
                "acquisition",
                target,
                {"type": "drop", "source": {"prefab_id": "shared", "resolution": "resolved"}, "conditions": {}},
                runtime,
                1.0,
            ),
        ]
        with self.assertRaisesRegex(ValueError, "acquisition source.*ambiguous"):
            normalize([FactBundle(1, [runtime], ambiguous, [])])

    def test_error_provenance_distinguishes_bundles_and_exact_source_path(self):
        alpha = SourceRef("alpha", "runtime_probe", "data/alpha.json", "1", "a" * 64)
        bravo = SourceRef("bravo", "runtime_probe", "data/bravo.json", "1", "b" * 64)
        scripts = SourceRef("scripts", "base_game_source", "data/scripts.zip", "1", "c" * 64)
        translation = SourceRef("translation", "mod_translation", "mod/viethoa.po", "1", "d" * 64)
        repeated = {"code": "same_error", "detail": "same payload"}
        located = {"code": "parse_error", "path": "data/scripts.zip", "line": 12}
        catalog = normalize(
            [
                FactBundle(1, [alpha], [], [repeated, dict(repeated)]),
                FactBundle(1, [bravo], [], [dict(repeated)]),
                FactBundle(1, [scripts, translation], [], [located]),
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            write_database(path, catalog)
            db = sqlite3.connect(path)
            repeated_rows = db.execute(
                "select bundle_id,source_id,source_kind from extraction_errors where code='same_error' order by source_id"
            ).fetchall()
            self.assertEqual(len(repeated_rows), 2)
            self.assertEqual([row[1:] for row in repeated_rows], [("alpha", "runtime_probe"), ("bravo", "runtime_probe")])
            self.assertNotEqual(repeated_rows[0][0], repeated_rows[1][0])
            self.assertEqual(
                db.execute(
                    "select source_id,source_kind,locator from extraction_errors where code='parse_error'"
                ).fetchone(),
                ("scripts", "base_game_source", "data/scripts.zip:line:12"),
            )
            db.close()

    def test_recipe_counts_and_ingredient_positions_are_exact_positive_integers(self):
        runtime = source("runtime", "runtime_probe", "b")
        product = EntityKey("tu_tien", "xd_product")
        ingredient = EntityKey("base_game", "goldnugget")
        for invalid_count in (0, -1, 1.5, True):
            with self.subTest(output_count=invalid_count):
                recipe = Fact("recipe", product, {"output_count": invalid_count}, runtime, 1.0)
                with self.assertRaisesRegex(ValueError, "positive integer output_count"):
                    normalize([FactBundle(1, [runtime], [recipe], [])])

        for invalid_position in (-1, 0.5, "0", True):
            with self.subTest(position=invalid_position):
                facts = [
                    Fact("entity", ingredient, {"entity_type": "inventory_item"}, runtime, 1.0),
                    Fact("recipe", product, {"output_count": 1}, runtime, 1.0),
                    Fact(
                        "ingredient",
                        product,
                        {"position": invalid_position, "amount": 1, "ingredient": {"namespace": "base_game", "prefab_id": "goldnugget"}},
                        runtime,
                        1.0,
                    ),
                ]
                with self.assertRaisesRegex(ValueError, "non-negative integer position"):
                    normalize([FactBundle(1, [runtime], facts, [])])

    def test_atomic_replace_failure_cleans_temporary_database(self):
        catalog = normalize([])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wiki.sqlite"
            path.write_bytes(b"original")
            temporary = path.with_name(f".{path.name}.tmp")

            with mock.patch("tools.extract.database.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    write_database(path, catalog)

            self.assertEqual(path.read_bytes(), b"original")
            self.assertFalse(temporary.exists())


if __name__ == "__main__":
    unittest.main()
