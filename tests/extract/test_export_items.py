import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.extract.export_items import (
    build_item_export,
    export_items,
    load_crafting_notes,
)


class ExportItemsTests(unittest.TestCase):
    def fixtures(self):
        catalog = {
            "schema_version": 1,
            "entities": [
                {
                    "key": "base_game:goldnugget",
                    "namespace": "base_game",
                    "prefab_id": "goldnugget",
                    "type": "inventory_item",
                    "is_inventory_item": True,
                    "name": {"vi": "Vàng", "en": "Gold Nugget"},
                    "description": {"vi": None, "en": "A gold nugget."},
                    "icon_key": "base_game:goldnugget",
                    "recipes": [],
                },
                {
                    "key": "tu_tien:xd_sword",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_sword",
                    "type": "inventory_item",
                    "is_inventory_item": True,
                    "name": {"vi": "Kiếm Thử", "en": "Test Sword"},
                    "description": {"vi": "Một thanh kiếm", "en": None},
                    "icon_key": "tu_tien:xd_sword",
                    "recipes": [
                        {
                            "output_count": 1,
                            "ingredients": [
                                {
                                    "key": "base_game:goldnugget",
                                    "amount": 2.0,
                                    "position": 0,
                                }
                            ],
                        }
                    ],
                },
                {
                    "key": "tu_tien:xd_special",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_special",
                    "type": "inventory_item",
                    "is_inventory_item": True,
                    "name": {"vi": None, "en": "Special Item"},
                    "description": {"vi": None, "en": None},
                    "icon_key": None,
                    "recipes": [{"output_count": 1, "ingredients": []}],
                },
                {
                    "key": "tu_tien:xd_fallback",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_fallback",
                    "type": "unknown",
                    "is_inventory_item": True,
                    "name": {"vi": None, "en": None},
                    "description": {"vi": None, "en": None},
                    "icon_key": None,
                    "recipes": [],
                },
                {
                    "key": "tu_tien:xd_creature",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_creature",
                    "type": "creature",
                    "is_inventory_item": False,
                    "name": {"vi": "Sinh vật", "en": "Creature"},
                    "description": {"vi": None, "en": None},
                    "icon_key": None,
                    "recipes": [],
                },
                {
                    "key": "base_game:deerclops",
                    "namespace": "base_game",
                    "prefab_id": "deerclops",
                    "type": "boss",
                    "is_inventory_item": False,
                    "name": {"vi": None, "en": "Deerclops"},
                    "description": {"vi": None, "en": None},
                    "icon_key": None,
                    "recipes": [],
                },
                {
                    "key": "base_game:dependency_alias",
                    "namespace": "base_game",
                    "prefab_id": "dependency_alias",
                    "type": "unknown",
                    "is_inventory_item": False,
                    "name": {"vi": None, "en": None},
                    "description": {"vi": None, "en": None},
                    "icon_key": None,
                    "recipes": [],
                },
            ],
        }
        assets = {
            "schema_version": 1,
            "assets": [
                {
                    "asset_id": "gold-unavailable",
                    "key": "base_game:goldnugget",
                    "namespace": "base_game",
                    "prefab_id": "goldnugget",
                    "type": "inventory",
                    "atlas": "images/inventoryimages.xml",
                    "texture": "images/inventoryimages.tex",
                    "element": "goldnugget.tex",
                    "uv": {"u1": 0.0, "u2": 0.5, "v1": 0.0, "v2": 0.5},
                    "available": False,
                    "texture_sha256": "c" * 64,
                    "evidence": [{"confidence": 1.0, "selected": True}],
                },
                {
                    "asset_id": "gold-available",
                    "key": "base_game:goldnugget",
                    "namespace": "base_game",
                    "prefab_id": "goldnugget",
                    "type": "inventory",
                    "atlas": "images/inventoryimages1.xml",
                    "texture": "images/inventoryimages1.tex",
                    "element": "goldnugget.tex",
                    "uv": {"u1": 0.25, "u2": 0.5, "v1": 0.5, "v2": 0.75},
                    "available": True,
                    "texture_sha256": "b" * 64,
                    "evidence": [{"confidence": 0.7, "selected": True}],
                },
                {
                    "asset_id": "sword",
                    "key": "tu_tien:xd_sword",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_sword",
                    "type": "inventory",
                    "atlas": "images/inventoryimages/xd_sword.xml",
                    "texture": "images/inventoryimages/xd_sword.tex",
                    "element": "xd_sword.tex",
                    "uv": {"u1": 0.0, "u2": 1.0, "v1": 0.0, "v2": 1.0},
                    "available": True,
                    "texture_sha256": "a" * 64,
                    "evidence": [{"confidence": 1.0, "selected": True}],
                },
            ],
        }
        return catalog, assets

    def test_builds_named_tu_tien_prefabs_with_crafting_notes_and_base_game(self):
        catalog, assets = self.fixtures()

        items, textures = build_item_export(
            catalog,
            assets,
            {"xd_sword": "Rèn một thanh kiếm thử"},
        )

        self.assertEqual(
            [item["id"] for item in items["items"]],
            [
                "base_game:deerclops",
                "base_game:goldnugget",
                "tu_tien:xd_creature",
                "tu_tien:xd_sword",
            ],
        )
        self.assertEqual(items["schema_version"], 4)
        by_id = {item["id"]: item for item in items["items"]}
        self.assertEqual(by_id["base_game:deerclops"]["category"], "boss")
        self.assertEqual(by_id["base_game:goldnugget"]["category"], "item")
        self.assertEqual(by_id["tu_tien:xd_creature"]["category"], "mob")
        self.assertNotIn("base_game:dependency_alias", by_id)
        sword = next(
            item for item in items["items"] if item["id"] == "tu_tien:xd_sword"
        )
        self.assertEqual(sword["name"], "Kiếm Thử")
        self.assertEqual(sword["description"], "Một thanh kiếm")
        self.assertEqual(sword["craftingNote"], "Rèn một thanh kiếm thử")
        self.assertIsNone(by_id["base_game:deerclops"]["craftingNote"])
        self.assertIsNone(by_id["base_game:deerclops"]["wiki"])
        self.assertEqual(
            sword["sprite"]["src"], "/assets/game/" + "a" * 64 + ".png"
        )
        self.assertEqual(
            sword["recipe"]["ingredients"][0],
            {
                "id": "base_game:goldnugget",
                "name": "Vàng",
                "amount": 2,
                "sprite": {
                    "src": "/assets/game/" + "b" * 64 + ".png",
                    "uv": {"u1": 0.25, "u2": 0.5, "v1": 0.5, "v2": 0.75},
                },
            },
        )
        self.assertEqual(
            textures,
            {
                "schema_version": 1,
                "textures": [
                    {
                        "sha256": "a" * 64,
                        "source": "mod",
                        "texture": "images/inventoryimages/xd_sword.tex",
                    },
                    {
                        "sha256": "b" * 64,
                        "source": "base_game",
                        "texture": "images/inventoryimages1.tex",
                    },
                ],
            },
        )

    def test_applies_name_description_recipe_and_sprite_fallbacks(self):
        catalog, assets = self.fixtures()
        sword = next(
            entity
            for entity in catalog["entities"]
            if entity["key"] == "tu_tien:xd_sword"
        )
        sword["recipes"][0]["ingredients"].append(
            {
                "key": "base_game:character_tool",
                "amount": 0.0,
                "position": 1,
            }
        )

        items, _textures = build_item_export(catalog, assets)
        by_id = {item["id"]: item for item in items["items"]}

        self.assertEqual(by_id["base_game:goldnugget"]["description"], "A gold nugget.")
        self.assertNotIn("tu_tien:xd_special", by_id)
        self.assertNotIn("tu_tien:xd_fallback", by_id)
        self.assertEqual(
            [
                ingredient["id"]
                for ingredient in by_id["tu_tien:xd_sword"]["recipe"]["ingredients"]
            ],
            ["base_game:goldnugget"],
        )

    def test_export_is_deterministic_and_atomic(self):
        catalog, assets = self.fixtures()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalog_path = root / "catalog.json"
            assets_path = root / "assets.json"
            database_path = root / "wiki.sqlite"
            items_path = root / "items.json"
            textures_path = root / "textures.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            assets_path.write_text(json.dumps(assets), encoding="utf-8")
            with sqlite3.connect(database_path) as connection:
                connection.execute(
                    "create table game_text (text_key text not null, value_vi text not null)"
                )

            export_items(
                database_path,
                catalog_path,
                assets_path,
                items_path,
                textures_path,
            )
            first_items = items_path.read_bytes()
            first_textures = textures_path.read_bytes()
            export_items(
                database_path,
                catalog_path,
                assets_path,
                items_path,
                textures_path,
            )

            self.assertEqual(items_path.read_bytes(), first_items)
            self.assertEqual(textures_path.read_bytes(), first_textures)
            self.assertFalse((root / ".items.json.tmp").exists())
            self.assertFalse((root / ".textures.json.tmp").exists())

    def test_loads_deduplicated_crafting_notes_and_rejects_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "wiki.sqlite"
            note = "Đá có linh khiếu, thần niệm có thể thông đạt"
            with sqlite3.connect(database) as connection:
                connection.execute(
                    "create table game_text (text_key text not null, value_vi text not null)"
                )
                connection.executemany(
                    "insert into game_text(text_key,value_vi) values(?,?)",
                    [
                        ("STRINGS.RECIPE_DESC.XD_SJ_TLSQ", note),
                        ("STRINGS.RECIPE_DESC.XD_SJ_TLSQ", note),
                        ("STRINGS.NAMES.XD_SJ_TLSQ", "Thông Linh Thạch Khiếu"),
                    ],
                )

            self.assertEqual(
                load_crafting_notes(database),
                {"xd_sj_tlsq": note},
            )

            with sqlite3.connect(database) as connection:
                connection.execute(
                    "insert into game_text(text_key,value_vi) values(?,?)",
                    ("STRINGS.RECIPE_DESC.XD_SJ_TLSQ", "Nội dung khác"),
                )

            with self.assertRaisesRegex(
                ValueError,
                "STRINGS.RECIPE_DESC.XD_SJ_TLSQ",
            ):
                load_crafting_notes(database)


if __name__ == "__main__":
    unittest.main()
