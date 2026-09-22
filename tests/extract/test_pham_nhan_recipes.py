from __future__ import annotations

import unittest
from pathlib import Path

from tools.extract.pham_nhan.discovery import discover_sources
from tools.extract.pham_nhan.sandbox import collect_registrations
from tools.extract.pham_nhan.recipes import normalize_recipes


class RecipeTests(unittest.TestCase):
    fixture = Path(__file__).parent / "fixtures" / "pham_nhan_recipes"

    def test_preserves_product_variants_and_last_recipe_id_override(self) -> None:
        registrations = collect_registrations(self.fixture, discover_sources(self.fixture))
        recipes = normalize_recipes(registrations)
        target = [recipe for recipe in recipes if recipe["product"] == "target"]
        self.assertEqual([recipe["id"] for recipe in target], ["variant_a", "variant_b"])
        self.assertEqual(next(recipe for recipe in target if recipe["id"] == "variant_a")["ingredients"][0]["amount"], 3)
        self.assertEqual(next(recipe for recipe in recipes if recipe["product"] == "bulk")["amount"], 8)

    def test_real_mod_keeps_required_recipe_facts(self) -> None:
        root = Path("mods/PhamNhanTuTien")
        recipes = normalize_recipes(collect_registrations(root, discover_sources(root)))
        tally = [recipe for recipe in recipes if recipe["product"] == "hh_treasure_tally"]
        self.assertEqual(len(tally), 2)
        enhancement = next(recipe for recipe in recipes if recipe["product"] == "wb_enhancegem")
        self.assertEqual(enhancement["amount"], 8)
        pond = next(recipe for recipe in recipes if recipe["product"] == "hh_hac_nguyet_ho")
        self.assertIn({"prefab": "marble", "amount": 10}, [{"prefab": item["prefab"], "amount": item["amount"]} for item in pond["ingredients"]])
