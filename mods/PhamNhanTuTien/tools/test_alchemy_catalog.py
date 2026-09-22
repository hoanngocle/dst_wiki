"""Catalog contract tests for the generated Phàm Nhân alchemy definitions."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "mods" / "PhamNhanTuTien" / "scripts" / "alchemy" / "ttk_alchemy_defs.lua"

CULTIVATION = [
    "xd_danyao_jq", "xd_danyao_dt", "xd_danyao_zj", "xd_danyao_xs",
    "xd_danyao_hj", "xd_danyao_yz", "xd_danyao_sm", "xd_danyao_rl",
    "xd_danyao_jy", "xd_danyao_yx", "xd_danyao_ns", "xd_danyao_hs",
    "xd_danyao_hy", "xd_danyao_hl", "xd_danyao_kx",
]
BUFFS = [
    "xd_dy_cyfxd_1", "xd_dy_dmhsd_1", "xd_dy_lmsqd_1",
    "xd_dy_qxdhd_1", "xd_dy_yfsxd_1", "xd_dy_pshsd_1",
    "xd_dy_qjqsd_1", "xd_dy_xynyd_1", "xd_dy_hsphd_1",
    "xd_dy_xttyd_1",
]
FORBIDDEN = {"xd_dy_fd", "xd_dy_tsfhd"}


class AlchemyCatalogTest(unittest.TestCase):
    def assert_ingredients_valid(self, source: str) -> None:
        for prefab in [*CULTIVATION, *BUFFS, "xd_danyao_bg"]:
            match = re.search(
                rf'M\.by_prefab\["{prefab}"\] = \{{(?P<row>.*?)\n\}}',
                source,
                re.DOTALL,
            )
            self.assertIsNotNone(match, prefab)
            ingredient_block = re.search(
                r'ingredients = \{\n(?P<ingredients>.*?)\n    \},',
                match.group("row"),
                re.DOTALL,
            )
            self.assertIsNotNone(ingredient_block, prefab)
            ingredient_lines = [
                line.strip()
                for line in ingredient_block.group("ingredients").splitlines()
                if line.strip()
            ]
            ingredients = [
                re.fullmatch(r'\{ prefab="([^"]*)", amount=(-?\d+) \},', line)
                for line in ingredient_lines
            ]
            self.assertEqual(len(ingredients), len(ingredient_lines), prefab)
            self.assertGreaterEqual(len(ingredients), 1, prefab)
            self.assertLessEqual(len(ingredients), 4, prefab)
            for ingredient in ingredients:
                self.assertIsNotNone(ingredient, prefab)
                ingredient_prefab, amount = ingredient.groups()
                self.assertTrue(ingredient_prefab, prefab)
                self.assertGreater(int(amount), 0, prefab)

    def test_generated_catalog_has_only_approved_pills_and_valid_recipes(self):
        """Removing an approved pill or emitting a forbidden or empty recipe fails."""
        source = OUTPUT.read_text(encoding="utf-8")

        cultivation = re.findall(r'M\.cultivation\[\d+\] = M\.by_prefab\["([^"]+)"\]', source)
        buffs = re.findall(r'M\.buffs\["([^"]+)"\] = M\.by_prefab\["\1"\]', source)
        self.assertEqual(cultivation, CULTIVATION)
        self.assertEqual(buffs, BUFFS)
        self.assertIn('M.by_prefab["xd_danyao_bg"]', source)
        self.assertNotIn("xd_dy_fd", source)
        self.assertNotIn("xd_dy_tsfhd", source)

        self.assert_ingredients_valid(source)

    def test_invalid_ingredient_row_is_rejected(self):
        """A malformed emitted row cannot be skipped by ingredient validation."""
        source = OUTPUT.read_text(encoding="utf-8")
        malformed = source.replace(
            '{ prefab="spidergland", amount=5 }',
            '{ prefab="", amount=0 }',
            1,
        )

        with self.assertRaises(AssertionError):
            self.assert_ingredients_valid(malformed)


if __name__ == "__main__":
    unittest.main()
