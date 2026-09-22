import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class ProgressionExportTests(unittest.TestCase):
    def test_exports_canonical_catalogs_and_matches_checked_in_snapshot(self):
        exporter = ROOT / "tools/export_pham_nhan_progression.py"
        self.assertTrue(exporter.exists(), "The integrated progression exporter is missing")
        spec = importlib.util.spec_from_file_location("progression_export", exporter)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        data = module.build_data(ROOT)
        self.assertEqual(len(data["achievements"]), 231)
        self.assertEqual(len(data["groups"]), 13)
        self.assertEqual(sum(row["reward"] for row in data["achievements"]), 1000)
        self.assertEqual(len(data["perks"]), 39)
        self.assertEqual(sum(row["maxCost"] for row in data["perks"]), 945)
        self.assertEqual(data.get("perkRuntimeSource"), "mods/PhamNhanTuTien/ACHIEVEMENT_PERK_RUNTIME.md")
        availability = {row["id"]: row["availability"] for row in data["perks"]}
        self.assertEqual(sorted(key for key, value in availability.items() if value["status"] == "unavailable"),
                         ["icy_weed", "inherit_hantianzun", "inherit_jingwei", "inherit_wangmazi", "trinket_owner"])
        self.assertEqual(sorted(key for key, value in availability.items() if value["status"] == "partial"),
                         ["antique_shop", "inherit_luoshen", "inherit_sanxiao", "inherit_shiji", "inherit_sudaji"])
        self.assertEqual(sum(value["status"] == "implemented" for value in availability.values()), 29)
        self.assertIn("trinketowner", availability["trinket_owner"]["note"])
        self.assertIn("chasni_icyweed", availability["icy_weed"]["note"])
        self.assertIn("21", availability["antique_shop"]["note"])
        self.assertEqual(data["perks"][0]["levelPrices"], [2]*10 + [3]*5 + [4]*5 + [5]*5)
        seasons = data["seasons"]
        self.assertEqual([len(row["tasks"]) for row in seasons], [50]*4)
        self.assertEqual([row["draw"] for row in seasons], [{"once": 16, "repeat": 4}]*4)
        seeds = ["ttk_lc_lmg_seed", "ttk_lc_cyh_seed", "ttk_lc_qfx_seed", "ttk_lc_hsc_seed"]
        gems = ["yellowgem", "orangegem", "greengem", "bluegem"]
        trophies = ["goose_feather", "dragon_scales", "bearger_fur", "deerclops_eyeball"]
        for index, season in enumerate(seasons):
            self.assertEqual(season["milestones"], [
                {"completed": 5, "items": [{"prefab": seeds[index], "amount": 3}]},
                {"completed": 10, "items": [{"prefab": seeds[index], "amount": 5}, {"prefab": "ttk_lingshi1", "amount": 10}]},
                {"completed": 15, "items": [{"prefab": "ttk_lingshi2", "amount": 2}, {"prefab": gems[index], "amount": 1}]},
                {"completed": 20, "items": [{"prefab": "ttk_lingshi3", "amount": 1}, {"prefab": trophies[index], "amount": 1}]},
            ])
        self.assertEqual(len(data["cultivation"]), 15)
        self.assertEqual(data["cultivation"][0]["name"], "Tụ Khí Hoàn")
        self.assertEqual(len(data["buffs"]), 10)
        self.assertEqual(data["ranks"][-2:], [{"name": "SS", "level": 70}, {"name": "SSS", "level": 100}])
        self.assertEqual(data, module.build_data(ROOT))
        self.assertEqual(data, json.loads((ROOT / "data/generated/pham-nhan-progression.json").read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
