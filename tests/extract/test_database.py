import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef
from tools.extract.database import write_database
from tools.extract.normalize import normalize


def source(source_id, kind, marker):
    return SourceRef(source_id, kind, f"{source_id}.json", "18.0.10", marker * 64)


class DatabaseTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
