import json
import unittest
from pathlib import Path

from tools.extract.wiki_mapping import normalize_identity
from tools.extract.wiki_sections import (
    normalize_drop_and_usage_sections,
    strip_drop_and_usage_html,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "public"
    / "data"
    / "wiki"
    / "pages"
    / "210449.json"
)


class WikiSectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        detail = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.wikitext = detail["wikitext"]

    def normalize(self):
        return normalize_drop_and_usage_sections(
            self.wikitext,
            "Nightmare Fuel",
            {
                normalize_identity("Beardling"): "base_game:beardling",
                normalize_identity("Gold Nugget"): "base_game:goldnugget",
                normalize_identity("Night Light"): "base_game:nightlight",
            },
        )

    def test_normalizes_all_nightmare_fuel_drop_rows(self):
        rows = self.normalize()["dropTable"]["rows"]

        self.assertEqual(len(rows), 10)
        self.assertEqual(
            [source["title"] for source in rows[0]["sources"]],
            ["Beardling", "Crab Beardling"],
        )
        self.assertEqual(rows[0]["quantity"], "1-3")
        self.assertEqual(rows[0]["chance"], "40%")
        self.assertEqual(rows[0]["sources"][0]["entityId"], "base_game:beardling")
        self.assertIsNone(rows[0]["sources"][1]["entityId"])
        self.assertIsNone(rows[0]["context"])
        self.assertIsNone(rows[1]["context"])
        self.assertEqual(
            rows[0]["sources"][1]["url"],
            "https://dontstarve.wiki.gg/wiki/Crab_%28insanity%29",
        )
        self.assertEqual(
            [row["quantity"] for row in rows],
            [
                "1-3",
                "1",
                "1",
                "1",
                "1-3",
                "1",
                "1 (Hammer) 2 (Deconstruction Staff) 1-2",
                "3",
                "1",
                "5-10",
            ],
        )
        self.assertEqual(
            [row["chance"] for row in rows],
            ["40%", "50%", "60%", "3.07%", "20%", "100%", "100%", "0.46%", "0.1%", "75%"],
        )
        self.assertEqual(
            [source["title"] for source in rows[5]["sources"]],
            ["Ancient Statue", "Touch Stone"],
        )
        self.assertIn("sans gems", rows[5]["context"])
        self.assertIn("Broken by Resurrection", rows[5]["context"])

    def test_normalizes_all_nightmare_fuel_usage_recipes(self):
        recipes = self.normalize()["usage"]["recipes"]

        self.assertEqual(len(recipes), 30)
        self.assertEqual(recipes[0]["result"]["title"], "Divining Rod")
        self.assertEqual(recipes[-1]["result"]["title"], "The Flying Pig Arcane Shop")
        night_light = next(
            recipe for recipe in recipes if recipe["result"]["title"] == "Night Light"
        )
        self.assertEqual(night_light["nightmareFuelAmount"], 2)
        self.assertEqual(
            [
                (ingredient["item"]["title"], ingredient["amount"])
                for ingredient in night_light["ingredients"]
            ],
            [("Gold Nugget", 8), ("Red Gem", 1)],
        )
        self.assertEqual(night_light["station"], "Prestihatitator")
        self.assertEqual(night_light["result"]["entityId"], "base_game:nightlight")
        self.assertEqual(
            night_light["ingredients"][0]["item"]["entityId"],
            "base_game:goldnugget",
        )
        self.assertEqual(
            next(
                recipe
                for recipe in recipes
                if recipe["result"]["title"] == "Dripple Pipes"
            )["dlc"],
            "Shipwrecked",
        )
        sleepytime = next(
            recipe
            for recipe in recipes
            if recipe["result"]["title"] == "Sleepytime Stories"
        )
        self.assertEqual(sleepytime["character"], "Wickerbottom")
        self.assertEqual(
            next(recipe for recipe in recipes if recipe["result"]["title"] == "Oinc")[
                "resultAmount"
            ],
            5,
        )
        self.assertIn(
            "Shipwrecked",
            next(recipe for recipe in recipes if recipe["result"]["title"] == "Seaworthy")[
                "note"
            ],
        )

    def test_rejects_missing_required_sections(self):
        with self.assertRaisesRegex(ValueError, "Drop table"):
            normalize_drop_and_usage_sections(
                "== Usage ==\n{{Recipe|item1=Nightmare Fuel|result=Night Light}}",
                "Nightmare Fuel",
                {},
            )

        with self.assertRaisesRegex(ValueError, "Usage"):
            normalize_drop_and_usage_sections(
                "=== Drop table ===\n{|\n|-\n| Source\n| 1\n| 100%\n|}",
                "Nightmare Fuel",
                {},
            )

    def test_strips_normalized_html_and_preserves_following_article(self):
        value = (
            '<h2><span id="Infobox_section">Infobox section</span></h2>'
            '<h3><span id="Gathering_note">Gathering note</span></h3>'
            '<p id="Gathering">Gathering</p>'
            '<h3><span id="Drop_table">Drop table</span></h3>'
            '<table><tr><td>drop</td></tr></table>'
            '<h2><span id="Usage">Usage</span></h2>'
            '<div>recipes</div>'
            '<h2><span id="Trivia">Trivia</span></h2>'
            '<p>Trivia body</p>'
        )

        stripped = strip_drop_and_usage_html(value)

        self.assertIn("Gathering", stripped)
        self.assertNotIn("Drop_table", stripped)
        self.assertNotIn('id="Usage"', stripped)
        self.assertIn('id="Trivia"', stripped)
        self.assertIn("Trivia body", stripped)

    def test_html_stripping_requires_bounded_sections(self):
        with self.assertRaisesRegex(ValueError, "Drop table and Usage"):
            strip_drop_and_usage_html('<h2><span id="Usage">Usage</span></h2>')

        with self.assertRaisesRegex(ValueError, "following level-2"):
            strip_drop_and_usage_html(
                '<h3><span id="Drop_table">Drop</span></h3>'
                '<h2><span id="Usage">Usage</span></h2>'
            )


if __name__ == "__main__":
    unittest.main()
