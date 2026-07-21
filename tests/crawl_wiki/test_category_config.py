import json
import tempfile
import unittest
from pathlib import Path

from tools.crawl_wiki.category_config import (
    CategoryConfigError,
    load_category_config,
)


class CategoryConfigTests(unittest.TestCase):
    def test_loads_animals_category_with_reviewed_scope(self):
        config = load_category_config("animals")

        self.assertEqual(config.category_title, "Category:Animals")
        self.assertEqual(config.expected_direct_pages, 35)
        self.assertEqual(config.expected_published_pages, 29)
        self.assertEqual(config.allowed_namespaces, (0,))
        self.assertEqual(
            dict(config.excluded_titles),
            {
                "Blue Whale": "non_dst:shipwrecked",
                "White Whale": "non_dst:shipwrecked",
                "Wildbore": "non_dst:shipwrecked",
                "Peagawk": "non_dst:hamlet",
                "Pog": "non_dst:hamlet",
                "Glowfly": "non_dst:hamlet",
            },
        )
        self.assertEqual(config.game, "DST")
        self.assertEqual(config.item_type, "mob")
        self.assertEqual(config.tags, ("Animals",))
        self.assertEqual(
            config.output_path,
            Path("data/crawled/fandom-categories/animals"),
        )

    def test_loads_reviewed_batch_configs(self):
        expected = {
            "armour_filter": (19, 19, "armor", "Armour Filter"),
            "beefalo_foods": (5, 5, "food", "Beefalo Foods"),
            "boss_dropped_items": (75, 63, "item", "Boss Dropped Items"),
            "backpacks": (10, 6, "container", "Backpacks"),
            "clothing_filter": (10, 10, "clothing", "Clothing Filter"),
            "cave_creatures": (32, 29, "mob", "Cave Creatures"),
            "celestial_filter": (6, 6, "item", "Celestial Filter"),
            "celestial_tab": (6, 6, "item", "Celestial Tab"),
            "containers": (28, 15, "container", "Containers"),
        }

        for key, values in expected.items():
            with self.subTest(key=key):
                direct, published, item_type, tag = values
                config = load_category_config(key)
                self.assertEqual(
                    (
                        config.expected_direct_pages,
                        config.expected_published_pages,
                    ),
                    (direct, published),
                )
                self.assertEqual(config.item_type, item_type)
                self.assertEqual(config.tags, (tag,))
                self.assertEqual(config.game, "DST")

        cave_exclusions = dict(
            load_category_config("cave_creatures").excluded_titles
        )
        self.assertEqual(cave_exclusions["Mobs"], "non_item:overview")
        self.assertEqual(cave_exclusions["Shadow Creature"], "non_item:overview")
        self.assertEqual(cave_exclusions["Spiders"], "non_item:overview")

    def test_rejects_exclusion_count_that_does_not_match_publication_count(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            payload = {
                "schema_version": 1,
                "key": "animals",
                "sourceUrl": "https://dontstarve.fandom.com/wiki/Category:Animals",
                "categoryTitle": "Category:Animals",
                "expectedDirectPages": 3,
                "expectedPublishedPages": 2,
                "allowedNamespaces": [0],
                "excludedTitles": {},
                "game": "DST",
                "itemType": "mob",
                "tags": ["Animals"],
            }
            (root / "animals.json").write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(CategoryConfigError, "difference"):
                load_category_config("animals", root)

    def test_loads_reviewed_batch_two_configs(self):
        expected = {
            "cooking_filter": (15, 14, "item", "Cooking Filter"),
            "crock_pot_recipes": (83, 68, "food", "Crock Pot Recipes"),
            "cooling": (26, 22, "item", "Cooling"),
            "craftable_items": (496, 359, "item", "Craftable Items"),
            "craftable_structures": (
                165,
                93,
                "structure",
                "Craftable Structures",
            ),
            "crafting_stations": (15, 12, "structure", "Crafting Stations"),
            "decorations_filter": (52, 49, "item", "Decorations Filter"),
            "eggs": (8, 7, "food", "Eggs"),
            "equipable_items": (198, 131, "item", "Equipable Items"),
            "events": (68, 68, "event", "Events"),
            "fertilizer": (13, 12, "item", "Fertilizer"),
            "food": (184, 122, "food", "Food"),
            "fight_tab": (32, 15, "item", "Fight Tab"),
            "fishes": (20, 6, "food", "Fishes"),
        }

        for key, values in expected.items():
            with self.subTest(key=key):
                direct, published, item_type, tag = values
                config = load_category_config(key)
                self.assertEqual(
                    (
                        config.expected_direct_pages,
                        config.expected_published_pages,
                    ),
                    (direct, published),
                )
                self.assertEqual(config.item_type, item_type)
                self.assertEqual(config.tags, (tag,))
                self.assertEqual(config.game, "DST")

        craftable_exclusions = dict(
            load_category_config("craftable_items").excluded_titles
        )
        self.assertEqual(
            craftable_exclusions["Crabby Hermit"],
            "non_item:category_mismatch",
        )
        self.assertEqual(
            craftable_exclusions["Old Bell"],
            "non_dst:reign_of_giants",
        )
        food_exclusions = dict(load_category_config("food").excluded_titles)
        self.assertNotIn("Ice", food_exclusions)
        self.assertEqual(food_exclusions["Cooking"], "non_item:overview")


if __name__ == "__main__":
    unittest.main()
