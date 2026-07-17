import unittest

from tools.extract.effect_other_audit import audit_effect_other_items


def blank_item(entity_id, category="effect"):
    prefab_id = entity_id.split(":", 1)[1]
    return {
        "id": entity_id,
        "prefabId": prefab_id,
        "namespace": entity_id.split(":", 1)[0],
        "category": category,
        "name": prefab_id,
        "englishName": None,
        "description": None,
        "craftingNote": None,
        "sprite": None,
        "recipe": None,
        "details": None,
        "mob": None,
        "character": None,
        "structureDetails": None,
        "wiki": None,
    }


def blank_entity(entity_id, entity_type="effect"):
    return {
        "key": entity_id,
        "namespace": entity_id.split(":", 1)[0],
        "prefab_id": entity_id.split(":", 1)[1],
        "type": entity_type,
        "is_inventory_item": False,
        "name": {"vi": None, "en": None},
        "description": {"vi": None, "en": None},
        "recipes": [],
        "acquisition": [],
        "stats": [],
        "effects": [],
        "relations": [],
    }


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

    def test_does_not_audit_categories_outside_effect_and_other(self):
        rows, excluded = audit_effect_other_items(
            [blank_item("base_game:real_item", "item")],
            [blank_entity("base_game:real_item", "item")],
            {},
        )

        self.assertEqual(rows, [])
        self.assertEqual(excluded, set())

    def test_keeps_each_positive_presentation_or_item_signal(self):
        cases = (
            ("sprite", {"src": "/icon.png", "uv": {}}),
            ("name", "Readable Name"),
            ("description", "Useful description"),
            ("englishName", "English Name"),
            ("craftingNote", "Crafting note"),
            ("wiki", {"detailUrl": "/data/wiki/pages/1.json"}),
            ("recipe", {"outputCount": 1, "ingredients": []}),
        )
        for field, value in cases:
            with self.subTest(field=field):
                item = blank_item("base_game:kept", "other")
                item[field] = value

                rows, excluded = audit_effect_other_items(
                    [item], [blank_entity("base_game:kept", "other")], {}
                )

                self.assertEqual(excluded, set())
                self.assertEqual(rows[0]["action"], "keep")
                self.assertEqual(rows[0]["reasonCode"], "positive_signal")

    def test_keeps_each_positive_catalog_signal(self):
        cases = (
            ("is_inventory_item", True, "inventoryItem"),
            ("recipes", [{"output_count": 1, "ingredients": []}], "recipe"),
            ("acquisition", [{"type": "drop", "source": None}], "acquisition"),
            ("stats", [{"key": "damage", "value": 10}], "stats"),
            ("effects", [{"key": "burn", "value": True}], "effects"),
            ("relations", [{"type": "alias", "target": "base_game:any"}], "relations"),
        )
        for field, value, signal in cases:
            with self.subTest(field=field):
                entity = blank_entity("base_game:kept", "effect")
                entity[field] = value

                rows, excluded = audit_effect_other_items(
                    [blank_item("base_game:kept", "effect")], [entity], {}
                )

                self.assertEqual(excluded, set())
                self.assertTrue(rows[0]["signals"][signal])

    def test_keeps_typed_item_details_but_not_empty_unknown_status(self):
        useful = blank_item("tu_tien:useful", "other")
        useful["details"] = {
            "dropBy": {"status": "known", "sources": []},
            "recipeStatus": "none",
            "usage": {
                "status": "known",
                "recipes": [],
                "effects": [{"trigger": "equip", "text": "Phát sáng"}],
            },
        }
        unknown = blank_item("tu_tien:unknown", "other")
        unknown["details"] = {
            "dropBy": {"status": "unknown", "sources": []},
            "recipeStatus": "none",
            "usage": {"status": "unknown", "recipes": [], "effects": []},
        }

        rows, excluded = audit_effect_other_items(
            [unknown, useful],
            [
                blank_entity("tu_tien:unknown", "other"),
                blank_entity("tu_tien:useful", "other"),
            ],
            {},
        )
        by_id = {row["id"]: row for row in rows}

        self.assertTrue(by_id["tu_tien:useful"]["signals"]["details"])
        self.assertEqual(by_id["tu_tien:useful"]["action"], "keep")
        self.assertEqual(by_id["tu_tien:unknown"]["action"], "exclude")
        self.assertEqual(excluded, {"tu_tien:unknown"})

    def test_keeps_blank_item_referenced_by_canonical_entities(self):
        ingredient_source = blank_entity("base_game:tool", "item")
        ingredient_source["recipes"] = [
            {
                "output_count": 1,
                "ingredients": [
                    {"key": "base_game:helper", "amount": 1, "position": 0}
                ],
            }
        ]
        drop_target = blank_entity("base_game:drop", "item")
        drop_target["acquisition"] = [
            {"type": "drop", "source": "base_game:helper"}
        ]
        relation_source = blank_entity("base_game:alias", "item")
        relation_source["relations"] = [
            {"type": "points_to", "target": "base_game:helper"}
        ]

        rows, excluded = audit_effect_other_items(
            [blank_item("base_game:helper", "other")],
            [
                blank_entity("base_game:helper", "other"),
                ingredient_source,
                drop_target,
                relation_source,
            ],
            {},
        )

        self.assertEqual(excluded, set())
        self.assertEqual(rows[0]["reasonCode"], "reverse_reference")
        self.assertEqual(
            [(reference["source"], reference["kind"]) for reference in rows[0]["references"]],
            [
                ("base_game:alias", "catalog_relation_target"),
                ("base_game:drop", "catalog_acquisition_source"),
                ("base_game:tool", "catalog_recipe_ingredient"),
            ],
        )

    def test_keeps_blank_item_referenced_by_final_items_and_wiki_details(self):
        source = blank_item("base_game:source", "item")
        source["recipe"] = {
            "outputCount": 1,
            "ingredients": [
                {"id": "base_game:helper", "name": "Helper", "amount": 1}
            ],
        }
        structure = blank_item("base_game:station", "structure")
        structure["structureDetails"] = {
            "construction": {
                "ingredients": [{"id": "base_game:helper", "amount": 1}]
            },
            "craftables": {
                "recipes": [
                    {
                        "result": {"id": "base_game:helper"},
                        "ingredients": [{"id": "base_game:helper", "amount": 1}],
                    }
                ]
            },
            "destruction": {"drops": [{"id": "base_game:helper"}]},
        }
        wiki_details = {
            "1": {
                "normalized": {
                    "subject": {"entityId": "base_game:source"},
                    "usage": {
                        "recipes": [
                            {"result": {"entityId": "base_game:helper"}}
                        ]
                    },
                }
            }
        }

        rows, excluded = audit_effect_other_items(
            [blank_item("base_game:helper", "effect"), source, structure],
            [blank_entity("base_game:helper", "effect")],
            wiki_details,
        )

        self.assertEqual(excluded, set())
        self.assertEqual(
            [(reference["source"], reference["kind"]) for reference in rows[0]["references"]],
            [
                ("base_game:source", "item_recipe_ingredient"),
                ("base_game:station", "structure_construction_ingredient"),
                ("base_game:station", "structure_craftable_ingredient"),
                ("base_game:station", "structure_craftable_result"),
                ("base_game:station", "structure_destruction_drop"),
                ("wiki:1", "wiki_entity_reference"),
            ],
        )

    def test_rows_and_references_are_sorted_deterministically(self):
        source = blank_entity("base_game:z_source", "item")
        source["relations"] = [
            {"type": "alias", "target": "base_game:a_helper"},
            {"type": "alias", "target": "base_game:a_helper"},
        ]

        rows, excluded = audit_effect_other_items(
            [
                blank_item("base_game:z_helper", "effect"),
                blank_item("base_game:a_helper", "other"),
            ],
            [
                blank_entity("base_game:z_helper", "effect"),
                blank_entity("base_game:a_helper", "other"),
                source,
            ],
            {},
        )

        self.assertEqual([row["id"] for row in rows], ["base_game:a_helper", "base_game:z_helper"])
        self.assertEqual(len(rows[0]["references"]), 1)
        self.assertEqual(excluded, {"base_game:z_helper"})


if __name__ == "__main__":
    unittest.main()
