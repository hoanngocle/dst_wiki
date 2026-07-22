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

    def test_loads_reviewed_batch_three_configs(self):
        expected = {
            "a_new_reign": (110, 92, "content", "A New Reign"),
            "ancient_tab": (15, 14, "item", "Ancient Tab"),
            "ancient_tier_1": (10, 9, "item", "Ancient Tier 1"),
            "ancient_tier_2": (7, 7, "item", "Ancient Tier 2"),
            "birds": (17, 10, "mob", "Birds"),
            "boss_monsters": (37, 28, "mob", "Boss Monsters"),
            "clockwork_monsters": (8, 6, "mob", "Clockwork Monsters"),
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

        reign_exclusions = dict(
            load_category_config("a_new_reign").excluded_titles
        )
        self.assertEqual(
            reign_exclusions["Blue Moonlens"],
            "duplicate:canonical_redirect",
        )
        self.assertEqual(
            reign_exclusions["Disease"],
            "non_item:category_mismatch",
        )

    def test_loads_reviewed_dont_starve_together_aggregate(self):
        config = load_category_config("dont_starve_together")

        self.assertEqual(config.category_title, "Category:Don't Starve Together")
        self.assertEqual(config.expected_direct_pages, 878)
        self.assertEqual(config.expected_published_pages, 872)
        self.assertEqual(config.allowed_namespaces, (0,))
        self.assertEqual(config.game, "DST")
        self.assertEqual(config.item_type, "content")
        self.assertEqual(config.tags, ("Don't Starve Together",))
        self.assertEqual(
            dict(config.excluded_titles),
            {
                "Blue Moonlens": "duplicate:canonical_redirect",
                "Green Moonlens": "duplicate:canonical_redirect",
                "Orange Moonlens": "duplicate:canonical_redirect",
                "Purple Moonlens": "duplicate:canonical_redirect",
                "Red Moonlens": "duplicate:canonical_redirect",
                "Yellow Moonlens": "duplicate:canonical_redirect",
            },
        )
        self.assertEqual(
            config.output_path,
            Path("data/crawled/fandom-categories/dont_starve_together"),
        )

    def test_loads_reviewed_batch_four_configs(self):
        expected = {
            "flying_creatures": (16, 12, "mob", "Flying Creatures"),
            "followers": (42, 35, "mob", "Followers"),
            "food_gardening_filter": (
                19,
                19,
                "item",
                "Food & Gardening Filter",
            ),
            "food_tab": (15, 10, "item", "Food Tab"),
            "from_beyond": (105, 104, "content", "From Beyond"),
            "fruits": (12, 9, "food", "Fruits"),
            "fuel": (119, 89, "item", "Fuel"),
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

        flying = dict(load_category_config("flying_creatures").excluded_titles)
        self.assertEqual(flying["Mobs"], "non_item:overview")
        self.assertEqual(flying["Packim Baggims"], "non_dst:shipwrecked")

        followers = dict(load_category_config("followers").excluded_titles)
        self.assertNotIn("Abigail", followers)
        self.assertNotIn("Merm", followers)
        self.assertEqual(followers["Spiders"], "non_item:overview")
        self.assertEqual(followers["Wildbore"], "non_dst:shipwrecked")

        food_tab = dict(load_category_config("food_tab").excluded_titles)
        self.assertEqual(food_tab["Farm"], "non_dst:dont_starve")

        beyond = dict(load_category_config("from_beyond").excluded_titles)
        self.assertEqual(beyond["Combat"], "non_item:overview")

        fruits = dict(load_category_config("fruits").excluded_titles)
        self.assertEqual(fruits["Fruit"], "non_item:overview")
        self.assertEqual(fruits["Coconut"], "non_dst:shipwrecked")

        fuel = dict(load_category_config("fuel").excluded_titles)
        self.assertEqual(fuel["Ashy Turf"], "non_dst:shipwrecked")
        self.assertEqual(fuel["Clippings"], "non_dst:hamlet")
        self.assertEqual(fuel["Turfs"], "non_item:overview")
        for title in (
            "Berry Bush",
            "Grass Tuft",
            "Pine Cone",
            "Slurtle Slime",
            "Spiky Bush",
            "Tentacle Spots",
        ):
            self.assertNotIn(title, fuel)

    def test_loads_reviewed_batch_five_configs(self):
        expected = {
            "gameplay": (112, 80, "content", "Gameplay"),
            "hats": (63, 40, "item", "Hats"),
            "healing": (192, 139, "item", "Healing"),
            "health_loss": (51, 37, "content", "Health Loss"),
            "hostile_creatures": (112, 72, "mob", "Hostile Creatures"),
            "indestructible_object": (
                87,
                39,
                "object",
                "Indestructible Object",
            ),
            "infobox_missing_crafting_description": (
                52,
                52,
                "item",
                "Infobox missing crafting description",
            ),
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

        gameplay = dict(load_category_config("gameplay").excluded_titles)
        self.assertEqual(gameplay["Adventure Mode"], "non_dst:dont_starve")
        self.assertEqual(gameplay["Armor/DS"], "non_dst:dont_starve")
        self.assertEqual(gameplay["Beard"], "non_item:overview")
        self.assertNotIn("Abyss", gameplay)
        self.assertNotIn("Armor", gameplay)

        hats = dict(load_category_config("hats").excluded_titles)
        self.assertEqual(hats["Captain Hat"], "non_dst:shipwrecked")
        self.assertEqual(hats["Royal Crown"], "non_dst:hamlet")

        healing = dict(load_category_config("healing").excluded_titles)
        self.assertEqual(healing["Crop Seeds"], "non_item:overview")
        self.assertEqual(healing["Dried Seaweed"], "non_dst:shipwrecked")
        self.assertNotIn("Butter", healing)
        self.assertNotIn("Spider Gland", healing)

        health_loss = dict(load_category_config("health_loss").excluded_titles)
        self.assertEqual(health_loss["Monster Food"], "non_item:overview")
        self.assertEqual(health_loss["Poison"], "non_dst:shipwrecked")
        self.assertNotIn("Charlie", health_loss)

        hostile = dict(load_category_config("hostile_creatures").excluded_titles)
        self.assertEqual(hostile["Blue Hound"], "duplicate:canonical_redirect")
        self.assertEqual(hostile["Mobs"], "non_item:overview")
        self.assertEqual(hostile["Ancient Herald"], "non_dst:hamlet")
        self.assertNotIn("Hound", hostile)
        self.assertNotIn("Suspicious Peeper", hostile)

        objects = dict(load_category_config("indestructible_object").excluded_titles)
        self.assertEqual(objects["Compromising Statue"], "non_dst:dont_starve")
        self.assertEqual(objects["Fishbone"], "non_dst:shipwrecked")
        self.assertEqual(objects["Wooden Thing"], "non_dst:dont_starve")
        self.assertNotIn("Bones", objects)
        self.assertNotIn("Eye Bone", objects)

        maintenance = load_category_config(
            "infobox_missing_crafting_description"
        )
        self.assertEqual(maintenance.excluded_titles, ())

    def test_loads_reviewed_batch_six_configs(self):
        expected = {
            "innocents": (30, 16, "mob", "Innocents"),
            "items": (987, 681, "item", "Items"),
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

        innocents = dict(load_category_config("innocents").excluded_titles)
        self.assertEqual(
            innocents["Bottlenose Ballphin"], "non_dst:shipwrecked"
        )
        self.assertEqual(innocents["Pog"], "non_dst:hamlet")
        self.assertNotIn("Beefalo", innocents)
        self.assertNotIn("Rabbit", innocents)

        items = dict(load_category_config("items").excluded_titles)
        self.assertEqual(items["Armor"], "non_item:overview")
        self.assertEqual(items["Items"], "non_item:overview")
        self.assertEqual(items["Runic Turf"], "non_item:category_mismatch")
        self.assertEqual(items["Blue Moonlens"], "duplicate:canonical_redirect")
        self.assertEqual(items["Old Bell"], "non_dst:reign_of_giants")
        self.assertEqual(items["Wild Plains Turf"], "non_dst:hamlet")
        self.assertEqual(items["Woodlegs' Keys"], "non_dst:shipwrecked")
        for title in (
            "Ashes",
            "Barbed Helm",
            "Beefalo Horn",
            "Cookpot",
            "Pig Skin",
            "Thulecite Fragments",
            "Walrus Tusk",
        ):
            self.assertNotIn(title, items)

    def test_loads_reviewed_batch_seven_configs(self):
        expected = {
            "light_sources": (94, 66, "content", "Light Sources"),
            "magic_tab": (30, 20, "item", "Magic Tab"),
            "magic_tier_1": (19, 14, "item", "Magic Tier 1"),
            "magic_tier_2": (14, 9, "item", "Magic Tier 2"),
            "meats": (48, 33, "food", "Meats"),
            "melee_weapons": (38, 23, "weapon", "Melee Weapons"),
            "mineable_objects": (32, 23, "object", "Mineable Objects"),
            "mob_dropped_items": (205, 142, "item", "Mob Dropped Items"),
            "mob_housing": (52, 23, "structure", "Mob Housing"),
            "mob_spawning_entities": (
                124,
                77,
                "object",
                "Mob Spawning Entities",
            ),
            "mobs": (279, 174, "mob", "Mobs"),
            "monster_foods": (9, 6, "food", "Monster Foods"),
            "monsters": (64, 40, "mob", "Monsters"),
            "neutral_creatures": (36, 22, "mob", "Neutral Creatures"),
            "nightmare_state_indicator": (
                9,
                9,
                "object",
                "Nightmare State Indicator",
            ),
            "nocturnals": (23, 17, "mob", "Nocturnals"),
            "ocean": (64, 31, "content", "Ocean"),
            "passive_creatures": (63, 30, "mob", "Passive Creatures"),
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

        dropped = dict(
            load_category_config("mob_dropped_items").excluded_titles
        )
        self.assertNotIn("Spider Eggs", dropped)
        self.assertEqual(dropped["Sweetener"], "non_item:overview")

        spawning = dict(
            load_category_config("mob_spawning_entities").excluded_titles
        )
        self.assertEqual(spawning["Plants"], "non_item:overview")
        self.assertEqual(
            spawning["Guides/Hatching A Smallbird"],
            "non_item:category_mismatch",
        )

        mobs = dict(load_category_config("mobs").excluded_titles)
        self.assertEqual(mobs["Animals"], "non_item:overview")
        self.assertEqual(mobs["Parrot Pirate"], "non_dst:shipwrecked")
        self.assertNotIn("Terrorclaw", mobs)
        self.assertNotIn("Wavey Jones", mobs)

        indicators = dict(
            load_category_config(
                "nightmare_state_indicator"
            ).excluded_titles
        )
        self.assertNotIn("Flower", indicators)
        self.assertNotIn("Runic Turf", indicators)


if __name__ == "__main__":
    unittest.main()
