"""Catalog contract tests for the generated Phàm Nhân alchemy definitions."""

import copy
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

import build_alchemy_defs as generator


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
    def manual_items(self) -> dict:
        with generator.MANUAL_PATH.open(encoding="utf-8") as manual_file:
            return json.load(manual_file)["items"]

    def assert_manual_rejected(self, items: dict) -> None:
        with patch.object(generator.json, "load", return_value={"items": items}):
            with self.assertRaises(ValueError):
                generator.read_records()

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

    def test_committed_catalog_exactly_matches_generator_and_manual(self):
        """A stale checked-in Lua catalog must differ from fresh manual generation."""
        self.assertEqual(
            OUTPUT.read_text(encoding="utf-8"),
            generator.render(generator.read_records()),
        )

    def test_generator_rejects_malformed_manual_scalars(self):
        """Malformed JSON scalars cannot reach Lua interpolation."""
        target = "tu_tien:xd_danyao_jq"
        cases = [
            ("boolean output count", lambda item: item["recipe"].__setitem__("outputCount", True)),
            ("zero output count", lambda item: item["recipe"].__setitem__("outputCount", 0)),
            ("string output count", lambda item: item["recipe"].__setitem__("outputCount", "1")),
            ("boolean amount", lambda item: item["recipe"]["ingredients"][0].__setitem__("amount", True)),
            ("zero amount", lambda item: item["recipe"]["ingredients"][0].__setitem__("amount", 0)),
            ("string amount", lambda item: item["recipe"]["ingredients"][0].__setitem__("amount", "1")),
            ("empty ingredient prefab", lambda item: item["recipe"]["ingredients"][0].__setitem__("id", "")),
            ("missing crafting note", lambda item: item["recipe"].__setitem__("craftingNote", None)),
            ("non-string crafting note", lambda item: item["recipe"].__setitem__("craftingNote", 1)),
            ("non-list effects", lambda item: item["usage"].__setitem__("effects", {})),
            ("non-mapping effect", lambda item: item["usage"].__setitem__("effects", ["bad"])),
            ("non-string trigger", lambda item: item["usage"]["effects"][0].__setitem__("trigger", 1)),
            ("non-string text", lambda item: item["usage"]["effects"][0].__setitem__("text", None)),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                items = copy.deepcopy(self.manual_items())
                mutate(items[target])
                self.assert_manual_rejected(items)

    def test_lua_string_escapes_lua_control_characters(self):
        """Control characters must be emitted as Lua-safe escape sequences."""
        value = 'quote" slash\\ newline\n tab\t backspace\b formfeed\f vertical\v bell\a unit\x1f null\0 delete\x7f'
        expected = '"quote\\" slash\\\\ newline\\n tab\\t backspace\\b formfeed\\f vertical\\v bell\\a unit\\031 null\\000 delete\\127"'
        self.assertEqual(generator.lua_string(value), expected)

    def test_runtime_prefab_rejects_noncanonical_manual_ids(self):
        """Only one approved namespace and one canonical prefab segment are valid."""
        invalid_ids = (
            "bogus:spidergland",
            "base_game: spidergland ",
            "base_game:spidergland ",
            " base_game:spidergland",
            "base_game:foo:bar",
        )
        for item_id in invalid_ids:
            with self.subTest(item_id=item_id):
                with self.assertRaises(ValueError):
                    generator.runtime_prefab(item_id)

    def test_runtime_prefab_rejects_invalid_dst_prefab_characters(self):
        """Runtime prefabs only permit lowercase ASCII letters, digits, and underscores."""
        invalid_ids = (
            "base_game:spider gland",
            "base_game:spider\ngland",
            "base_game:spider\0gland",
            "base_game:Spidergland",
            "base_game:spider-gland",
            "base_game:spider.gland",
        )
        for item_id in invalid_ids:
            with self.subTest(item_id=item_id):
                with self.assertRaises(ValueError):
                    generator.runtime_prefab(item_id)

    def test_runtime_prefab_accepts_every_manual_ingredient_id(self):
        """The current manual catalog contains only valid DST runtime prefabs."""
        for prefab, record in generator.read_records():
            for ingredient in record["recipe"]["ingredients"]:
                with self.subTest(catalog_prefab=prefab, item_id=ingredient["id"]):
                    self.assertRegex(generator.runtime_prefab(ingredient["id"]), r"^[a-z0-9_]+$")

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
