import unittest

from tools.crawl_wiki.recipes import extract_recipes


class RecipeTests(unittest.TestCase):
    def test_extracts_infobox_ingredients_as_product_recipe(self):
        text = """{{Object Infobox
        |ingredient1 = Rotten Egg|multiplier1 = 1
        |ingredient2 = Charcoal|multiplier2 = 2
        |tab = Science|tier = 2}}
        """

        records = extract_recipes(7, "Gunpowder", text)

        self.assertEqual(
            records,
            [
                {
                    "schema_version": 1,
                    "page_id": 7,
                    "result": "Gunpowder",
                    "source": "Object Infobox",
                    "variant": "base",
                    "ingredients": [
                        {"title": "Rotten Egg", "count": 1.0},
                        {"title": "Charcoal", "count": 2.0},
                    ],
                    "station": None,
                    "tab": "Science",
                    "tier": "2",
                    "dlc": None,
                    "character": None,
                    "note": None,
                }
            ],
        )

    def test_keeps_only_recipe_templates_that_create_current_page(self):
        text = """
        {{Recipe
        |item1={{Pic|32px|Meats}}
        |item2=Filler
        |count2=3
        |tool=Crock Pot
        |result=[[Meatballs]]}}
        {{Recipe|item1=Meatballs|item2=Twigs|result=Wet Goop}}
        """

        records = extract_recipes(9, "Meatballs", text)

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["ingredients"],
            [
                {"title": "Meats", "count": 1.0},
                {"title": "Filler", "count": 3.0},
            ],
        )
        self.assertEqual(records[0]["station"], "Crock Pot")
        self.assertEqual(records[0]["source"], "Recipe")

    def test_extracts_infobox_variants_without_mixing_inputs(self):
        text = """{{Object Infobox
        |ingredient1 = Log|multiplier1 = 1
        |ingredient2 = Flint|multiplier2 = 1
        |ingredient1DST = Twigs|multiplier1DST = 2
        |ingredient2DST = Flint|multiplier2DST = 1
        |tab = Tools|tier = 1}}
        """

        records = extract_recipes(11, "Axe", text)

        self.assertEqual([record["variant"] for record in records], ["base", "DST"])
        self.assertEqual(
            records[1]["ingredients"],
            [
                {"title": "Twigs", "count": 2.0},
                {"title": "Flint", "count": 1.0},
            ],
        )


if __name__ == "__main__":
    unittest.main()
