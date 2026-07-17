import unittest

from tools.extract.item_details import build_tu_tien_item_details


def entity(
    key,
    *,
    name=None,
    recipes=None,
    stats=None,
    acquisition=None,
    relations=None,
    effects=None,
):
    namespace, prefab_id = key.split(":", 1)
    return {
        "key": key,
        "namespace": namespace,
        "prefab_id": prefab_id,
        "name": {"vi": name or prefab_id, "en": None},
        "recipes": recipes or [],
        "stats": stats or [],
        "acquisition": acquisition or [],
        "relations": relations or [],
        "effects": effects or [],
    }


def item(key, *, name=None, recipe=None):
    namespace, prefab_id = key.split(":", 1)
    return {
        "id": key,
        "namespace": namespace,
        "prefabId": prefab_id,
        "name": name or prefab_id,
        "sprite": None,
        "recipe": recipe,
        "craftingNote": None,
    }


class ItemDetailTests(unittest.TestCase):
    def fixtures(self):
        herb_recipe = {
            "output_count": 1,
            "ingredients": [
                {"key": "tu_tien:herb", "amount": 2.0, "position": 0},
                {"key": "base_game:goldnugget", "amount": 1.0, "position": 1},
            ],
            "restrictions": {"builder_tags": ["xd_alchemist"]},
            "tech": "NONE",
        }
        entities = [
            entity(
                "tu_tien:herb",
                name="Linh Thảo",
                stats=[
                    {"key": "health", "value": 20.0, "unit": "hp"},
                    {"key": "hunger", "value": -5.0, "unit": "hunger"},
                    {"key": "sanity", "value": 10.0, "unit": "sanity"},
                ],
                acquisition=[
                    {
                        "type": "harvest",
                        "source": "tu_tien:spirit_plant",
                        "chance": 1.0,
                        "min_count": 1.0,
                        "max_count": 2.0,
                        "conditions": {"regrowth_seconds": 480},
                    }
                ],
            ),
            entity("tu_tien:pill", name="Linh Đan", recipes=[herb_recipe]),
            entity("tu_tien:spirit_plant", name="Linh Thảo Cây"),
            entity(
                "tu_tien:sword",
                name="Linh Kiếm",
                stats=[
                    {"key": "damage", "value": 68.0, "unit": "hp"},
                    {"key": "attack_range", "value": 2.0, "unit": "tiles"},
                    {"key": "uses", "value": 100.0, "unit": "uses"},
                ],
            ),
            entity(
                "tu_tien:armor",
                name="Linh Giáp",
                stats=[
                    {"key": "armor_durability", "value": 840.0, "unit": "hp"},
                    {"key": "damage_absorption", "value": 0.85, "unit": "ratio"},
                ],
            ),
            entity(
                "tu_tien:bag",
                name="Túi Càn Khôn",
                stats=[{"key": "container_slots", "value": 18.0, "unit": "slots"}],
            ),
            entity(
                "tu_tien:wand",
                name="Pháp Trượng",
                stats=[
                    {"key": "charge_capacity", "value": 180.0, "unit": "charge"},
                    {"key": "current_charge", "value": 90.0, "unit": "charge"},
                    {"key": "recharge_time", "value": 30.0, "unit": "seconds"},
                ],
            ),
            entity(
                "tu_tien:fruit",
                name="Linh Quả",
                relations=[
                    {
                        "type": "transforms_to",
                        "target": "base_game:spoiled_food",
                        "metadata": {},
                    }
                ],
            ),
            entity("tu_tien:unknown", name="Vật Bí Ẩn"),
            entity("base_game:goldnugget", name="Vàng"),
            entity("base_game:spoiled_food", name="Thức Ăn Hỏng"),
        ]
        items = [
            item("tu_tien:herb", name="Linh Thảo"),
            item(
                "tu_tien:pill",
                name="Linh Đan",
                recipe={
                    "outputCount": 1,
                    "ingredients": [
                        {"id": "tu_tien:herb", "name": "Linh Thảo", "amount": 2, "sprite": None},
                        {"id": "base_game:goldnugget", "name": "Vàng", "amount": 1, "sprite": None},
                    ],
                },
            ),
            item("tu_tien:sword", name="Linh Kiếm"),
            item("tu_tien:armor", name="Linh Giáp"),
            item("tu_tien:bag", name="Túi Càn Khôn"),
            item("tu_tien:wand", name="Pháp Trượng"),
            item("tu_tien:fruit", name="Linh Quả"),
            item("tu_tien:unknown", name="Vật Bí Ẩn"),
            item("base_game:goldnugget", name="Vàng"),
        ]
        return entities, items

    def test_builds_reverse_recipe_edible_usage_and_harvest_source(self):
        entities, items = self.fixtures()

        details, report = build_tu_tien_item_details(entities, items)

        herb = details["tu_tien:herb"]
        self.assertEqual(herb["recipeStatus"], "unknown")
        self.assertEqual(herb["usage"]["status"], "known")
        self.assertEqual(herb["usage"]["recipes"][0]["result"]["id"], "tu_tien:pill")
        self.assertEqual(herb["usage"]["recipes"][0]["subjectAmount"], 2)
        self.assertEqual(
            [ingredient["id"] for ingredient in herb["usage"]["recipes"][0]["ingredients"]],
            ["base_game:goldnugget"],
        )
        self.assertEqual(
            herb["usage"]["effects"][0]["text"],
            "Khi ăn: hồi 20 Máu, giảm 5 Đói và hồi 10 Tinh thần.",
        )
        self.assertEqual(herb["dropBy"]["status"], "known")
        self.assertEqual(herb["dropBy"]["sources"][0]["source"]["id"], "tu_tien:spirit_plant")
        self.assertEqual(herb["dropBy"]["sources"][0]["quantity"], "1–2")
        self.assertEqual(herb["dropBy"]["sources"][0]["chance"], "100%")
        self.assertEqual(herb["dropBy"]["sources"][0]["conditions"], "Hồi lại sau 480 giây")
        self.assertEqual(report["totalTuTienItems"], 8)

    def test_maps_supported_equipment_container_charge_and_relation_stats(self):
        entities, items = self.fixtures()

        details, report = build_tu_tien_item_details(entities, items)

        self.assertEqual(
            details["tu_tien:sword"]["usage"]["effects"][0]["text"],
            "Khi dùng làm vũ khí: gây 68 sát thương, tầm đánh 2 ô, độ bền 100 lần dùng.",
        )
        self.assertEqual(
            details["tu_tien:armor"]["usage"]["effects"][0]["text"],
            "Khi trang bị: hấp thụ 85% sát thương, độ bền 840.",
        )
        self.assertEqual(
            details["tu_tien:bag"]["usage"]["effects"][0]["text"],
            "Dùng làm vật chứa với 18 ô đồ.",
        )
        self.assertEqual(
            details["tu_tien:wand"]["usage"]["effects"][0]["text"],
            "Khi kích hoạt: 90/180 điểm năng lượng, hồi đầy trong 30 giây.",
        )
        self.assertEqual(
            details["tu_tien:fruit"]["usage"]["effects"][0]["text"],
            "Theo thời gian biến thành Thức Ăn Hỏng.",
        )
        self.assertIn(
            {"id": "tu_tien:unknown", "sections": ["recipe", "usage", "dropBy"]},
            report["unknownItems"],
        )

    def test_marks_recipe_known_and_craft_only_drop_source_none(self):
        entities, items = self.fixtures()
        pill = next(value for value in entities if value["key"] == "tu_tien:pill")
        pill["acquisition"] = [
            {
                "type": "craft",
                "source": None,
                "chance": None,
                "min_count": None,
                "max_count": None,
                "conditions": {},
            }
        ]

        details, _report = build_tu_tien_item_details(entities, items)

        self.assertEqual(details["tu_tien:pill"]["recipeStatus"], "known")
        self.assertEqual(details["tu_tien:pill"]["dropBy"], {"status": "none", "sources": []})

    def test_applies_evidence_backed_usage_override(self):
        entities, items = self.fixtures()
        overrides = {
            "schema_version": 1,
            "items": {
                "tu_tien:unknown": {
                    "usage": {
                        "replace": True,
                        "status": "known",
                        "recipes": [],
                        "effects": [
                            {
                                "trigger": "activate",
                                "text": "Khi kích hoạt: mở cổng bí cảnh.",
                                "evidence": [
                                    {
                                        "source": "mod/3721846643/scripts/prefabs/xd_unknown.lua",
                                        "locator": "OnActivate",
                                    }
                                ],
                            }
                        ],
                    }
                }
            },
        }

        details, report = build_tu_tien_item_details(entities, items, overrides)

        self.assertEqual(details["tu_tien:unknown"]["usage"]["status"], "known")
        self.assertEqual(report["manualOverrideItems"], ["tu_tien:unknown"])
        unknown = next(row for row in report["unknownItems"] if row["id"] == "tu_tien:unknown")
        self.assertEqual(unknown["sections"], ["recipe", "dropBy"])

    def test_rejects_invalid_overrides(self):
        entities, items = self.fixtures()
        invalid_cases = [
            (
                {"schema_version": 1, "items": {"tu_tien:missing": {}}},
                "unknown override entity",
            ),
            (
                {
                    "schema_version": 1,
                    "items": {
                        "tu_tien:unknown": {
                            "usage": {
                                "replace": True,
                                "status": "known",
                                "recipes": [],
                                "effects": [],
                            }
                        }
                    },
                },
                "known usage",
            ),
            (
                {
                    "schema_version": 1,
                    "items": {
                        "tu_tien:unknown": {
                            "usage": {
                                "replace": True,
                                "status": "known",
                                "recipes": [],
                                "effects": [
                                    {
                                        "trigger": "activate",
                                        "text": "Mở cổng.",
                                        "evidence": [
                                            {
                                                "source": "notes/guess.txt",
                                                "locator": None,
                                            }
                                        ],
                                    }
                                ],
                            }
                        }
                    },
                },
                "evidence source",
            ),
            (
                {
                    "schema_version": 1,
                    "items": {
                        "tu_tien:unknown": {
                            "dropBy": {
                                "replace": True,
                                "status": "known",
                                "sources": [
                                    {
                                        "type": "spawn",
                                        "source": None,
                                        "quantity": "1",
                                        "chance": "100%",
                                        "conditions": None,
                                        "evidence": [
                                            {
                                                "source": "mod/3721846643/scripts/prefabs/xd_unknown.lua",
                                                "locator": "fn",
                                            }
                                        ],
                                    }
                                ],
                            }
                        }
                    },
                },
                "drop source type",
            ),
            (
                {
                    "schema_version": 1,
                    "items": {
                        "tu_tien:unknown": {
                            "usage": {
                                "replace": True,
                                "status": "known",
                                "recipes": [],
                                "effects": [
                                    {
                                        "trigger": "activate",
                                        "text": "Mở cổng.",
                                        "evidence": [
                                            {
                                                "source": "mod/3721846643/scripts/prefabs/xd_unknown.lua",
                                                "locator": "fn",
                                            }
                                        ],
                                    },
                                    {
                                        "trigger": "activate",
                                        "text": "Mở cổng.",
                                        "evidence": [
                                            {
                                                "source": "mod/3721846643/scripts/prefabs/xd_unknown.lua",
                                                "locator": "fn",
                                            }
                                        ],
                                    },
                                ],
                            }
                        }
                    },
                },
                "duplicate usage record",
            ),
        ]

        for overrides, message in invalid_cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    build_tu_tien_item_details(entities, items, overrides)


if __name__ == "__main__":
    unittest.main()
