from __future__ import annotations

import unittest
from pathlib import Path

from tools.extract.pham_nhan.catalog import build_catalog
from tools.extract.pham_nhan.discovery import discover_sources
from tools.extract.pham_nhan.sandbox import collect_registrations


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path("mods/PhamNhanTuTien")
        cls.items, cls.coverage = build_catalog(root, collect_registrations(root, discover_sources(root)))
        cls.by_prefab = {item["prefab"]: item for item in cls.items}

    def test_keeps_required_active_and_drop_items(self) -> None:
        for prefab in ("yellowgem", "ttk_xshj_blueprint", "eva_scythe", "wb_enhancegem", "hh_treasure_tally", "nkGem"):
            self.assertIn(prefab, self.by_prefab)
        self.assertEqual(self.by_prefab["yellowgem"]["recipeStatus"], "known")
        self.assertEqual(self.by_prefab["nkGem"]["recipeStatus"], "none")

    def test_excludes_runtime_helpers_and_creatures(self) -> None:
        prefabs = set(self.by_prefab)
        self.assertNotIn("hh_hac_nguyet_ho_placer", prefabs)
        self.assertNotIn("ttk_boss_baihu", prefabs)
        self.assertNotIn("hh_fx", prefabs)
        self.assertGreater(self.coverage["included"], 20)

    def test_recipes_keep_builder_and_cooking_conditions(self) -> None:
        eva = self.by_prefab["eva_scythe"]
        self.assertTrue(any("tag" in condition.lower() for recipe in eva["recipes"] for condition in recipe["conditions"]))
        luoshen = [item for item in self.items if item["prefab"].startswith("ttk_luoshen_")]
        self.assertGreaterEqual(len(luoshen), 2)
        self.assertTrue(any(recipe["kind"] == "cooking" and recipe["conditions"] for item in luoshen for recipe in item["recipes"]))

    def test_collects_both_runtime_fusion_potions(self) -> None:
        self.assertEqual(self.by_prefab["nn_liquidluck_2"]["recipes"][0]["ingredients"][0]["amount"], 3)
        self.assertEqual(self.by_prefab["nn_liquidluck_3"]["recipes"][0]["ingredients"][1]["amount"], 2)
