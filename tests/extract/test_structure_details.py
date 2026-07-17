import unittest

from tools.extract.structure_details import (
    build_station_outputs,
    build_structure_details,
)


def item(
    item_id,
    category,
    name,
    recipe=None,
    sprite=None,
    description=None,
):
    namespace, prefab_id = item_id.split(":", 1)
    return {
        "id": item_id,
        "prefabId": prefab_id,
        "namespace": namespace,
        "category": category,
        "name": name,
        "englishName": name,
        "description": description,
        "craftingNote": None,
        "sprite": sprite,
        "recipe": recipe,
        "details": None,
        "wiki": None,
    }


def entity(item_id, entity_type, recipes=None, stats=None, description=None):
    namespace, prefab_id = item_id.split(":", 1)
    return {
        "key": item_id,
        "namespace": namespace,
        "prefab_id": prefab_id,
        "type": entity_type,
        "name": {"vi": prefab_id, "en": prefab_id},
        "description": {"vi": description, "en": None},
        "recipes": recipes or [],
        "stats": stats or [],
        "effects": [],
        "relations": [],
        "acquisition": [],
    }


class StructureDetailTests(unittest.TestCase):
    def setUp(self):
        self.sprite = {
            "src": "/assets/test.png",
            "uv": {"u1": 0.0, "u2": 1.0, "v1": 0.0, "v2": 1.0},
        }
        self.items = [
            item(
                "base_game:atrium_statue",
                "structure",
                "Ancient Statue",
                description="A naturally occurring statue.",
            ),
            item("base_game:lunar_forge", "structure", "Brightsmithy"),
            item("wiki:158535", "structure", "Science Machine"),
            item(
                "base_game:axe",
                "item",
                "Axe",
                recipe={
                    "outputCount": 1,
                    "ingredients": [
                        {
                            "id": "base_game:goldnugget",
                            "name": "Gold Nugget",
                            "amount": 1,
                            "sprite": None,
                        }
                    ],
                },
            ),
            item(
                "base_game:armor_lunarplant",
                "item",
                "Brightshade Armor",
                recipe={
                    "outputCount": 1,
                    "ingredients": [
                        {
                            "id": "base_game:purebrilliance",
                            "name": "Pure Brilliance",
                            "amount": 4,
                            "sprite": None,
                        }
                    ],
                },
                sprite=self.sprite,
            ),
            item(
                "base_game:purebrilliance",
                "item",
                "Pure Brilliance",
                sprite=self.sprite,
            ),
            item(
                "tu_tien:xd_liandanlu",
                "structure",
                "Đan Lô",
                recipe={
                    "outputCount": 1,
                    "ingredients": [
                        {
                            "id": "base_game:goldnugget",
                            "name": "Gold Nugget",
                            "amount": 5,
                            "sprite": None,
                        }
                    ],
                },
                sprite=self.sprite,
            ),
            item(
                "tu_tien:xd_test_pill",
                "pill",
                "Đan thử",
                recipe={
                    "outputCount": 2,
                    "ingredients": [
                        {
                            "id": "base_game:goldnugget",
                            "name": "Gold Nugget",
                            "amount": 1,
                            "sprite": None,
                        }
                    ],
                },
                sprite=self.sprite,
            ),
            item("base_game:goldnugget", "item", "Gold Nugget"),
        ]
        self.entities = [
            entity("base_game:atrium_statue", "structure"),
            entity("base_game:lunar_forge", "structure"),
            entity(
                "base_game:axe",
                "item",
                recipes=[
                    {
                        "output_count": 1,
                        "ingredients": [
                            {
                                "key": "base_game:goldnugget",
                                "amount": 1,
                                "position": 0,
                            }
                        ],
                        "tech": "TECH.SCIENCE_ONE",
                        "restrictions": {},
                    }
                ],
            ),
            entity(
                "base_game:armor_lunarplant",
                "item",
                recipes=[
                    {
                        "output_count": 1,
                        "ingredients": [
                            {
                                "key": "base_game:purebrilliance",
                                "amount": 4,
                                "position": 0,
                            }
                        ],
                        "tech": "TECH.LUNARFORGING_TWO",
                        "restrictions": {
                            "config_expression": (
                                '{nounlock=true, station_tag="lunar_forge"}'
                            )
                        },
                    }
                ],
            ),
            entity("base_game:purebrilliance", "item"),
            entity(
                "tu_tien:xd_liandanlu",
                "structure",
                stats=[
                    {
                        "key": "container_slots",
                        "value": 4.0,
                        "unit": "slots",
                        "confidence": 1.0,
                    }
                ],
            ),
            entity("tu_tien:xd_test_pill", "item"),
            entity("base_game:goldnugget", "item"),
        ]
        wiki_evidence = [
            {
                "source": "https://dontstarve.wiki.gg/wiki/Ancient_Statue/DST",
                "locator": "revision:103",
            }
        ]
        self.wiki = {
            "base_game:atrium_statue": {
                "origin": {
                    "status": "known",
                    "naturallySpawned": True,
                    "renewable": True,
                    "spawnCode": "atrium_statue",
                    "sources": [],
                    "respawn": "Có",
                    "evidence": wiki_evidence,
                },
                "functions": {
                    "status": "unknown",
                    "facts": [],
                    "reason": "No normalized functions.",
                    "evidence": wiki_evidence,
                },
                "destruction": {
                    "status": "known",
                    "destroyable": False,
                    "tool": "Can't Be Destroyed",
                    "work": None,
                    "health": None,
                    "burnable": None,
                    "drops": [],
                    "regeneration": "Có",
                    "evidence": wiki_evidence,
                },
                "visual_candidates": [],
            }
        }

    def test_builds_construction_and_natural_origin_statuses(self):
        details = build_structure_details(self.items, self.entities, self.wiki)

        furnace = details["tu_tien:xd_liandanlu"]
        statue = details["base_game:atrium_statue"]
        self.assertEqual(furnace["construction"]["status"], "known")
        self.assertEqual(statue["construction"]["status"], "none")
        self.assertIn("tự sinh", statue["origin"]["note"].casefold())
        self.assertIn("không thể chế tạo", statue["origin"]["note"].casefold())

    def test_maps_station_tag_recipes_back_to_structure(self):
        outputs = build_station_outputs(self.items, self.entities)

        recipes = outputs["base_game:lunar_forge"]
        self.assertEqual(
            [recipe["result"]["id"] for recipe in recipes],
            ["base_game:armor_lunarplant"],
        )
        self.assertEqual(recipes[0]["tech"], "TECH.LUNARFORGING_TWO")
        self.assertEqual(recipes[0]["ingredients"][0]["amount"], 4)

    def test_maps_standard_tech_recipe_to_wiki_only_dst_station(self):
        outputs = build_station_outputs(self.items, self.entities)

        recipes = outputs["wiki:158535"]
        self.assertEqual(
            [recipe["result"]["id"] for recipe in recipes],
            ["base_game:axe"],
        )
        self.assertEqual(recipes[0]["tech"], "TECH.SCIENCE_ONE")

    def test_maps_tu_tien_pills_to_alchemy_furnace(self):
        outputs = build_station_outputs(self.items, self.entities)

        recipes = outputs["tu_tien:xd_liandanlu"]
        self.assertEqual(
            [recipe["result"]["id"] for recipe in recipes],
            ["tu_tien:xd_test_pill"],
        )
        self.assertEqual(recipes[0]["resultAmount"], 2)

    def test_derives_function_facts_from_catalog_stats(self):
        details = build_structure_details(self.items, self.entities, self.wiki)

        functions = details["tu_tien:xd_liandanlu"]["functions"]
        self.assertEqual(functions["status"], "known")
        self.assertEqual(functions["facts"][0]["key"], "container_slots")
        self.assertEqual(functions["facts"][0]["value"], "4")
        self.assertEqual(functions["facts"][0]["unit"], "slots")

    def test_keeps_wiki_indestructible_status_and_visual_fallback(self):
        details = build_structure_details(self.items, self.entities, self.wiki)

        statue = details["base_game:atrium_statue"]
        self.assertIs(statue["destruction"]["destroyable"], False)
        self.assertEqual(statue["visual"]["status"], "unknown")
        self.assertEqual(statue["visual"]["kind"], None)


if __name__ == "__main__":
    unittest.main()
