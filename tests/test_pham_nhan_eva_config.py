import unittest
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".superpowers/ttk-solo-integration/lua-runtime"))
from lupa.lua51 import LuaRuntime


class PhamNhanEvaConfigTests(unittest.TestCase):
    def test_base_stats_are_fixed_and_removed_from_mod_menu(self):
        modinfo = (ROOT / "mods/PhamNhanTuTien/modinfo.lua").read_text(encoding="utf-8-sig")
        settings = (ROOT / "mods/PhamNhanTuTien/scripts/util/eva_settings.lua").read_text(encoding="utf-8-sig")
        fixed = {
            "EVA_HEALTH": 125,
            "EVA_HUNGER": 125,
            "EVA_SANITY": 200,
            "EVA_HUNGER_RATE": 1,
            "EVA_SPEED": 1,
            "EVA_DMG": 1,
        }

        for tuning, value in fixed.items():
            key = tuning.lower()
            self.assertNotIn(f'name = "{key}"', modinfo)
            self.assertIn(f"TUNING.{tuning} = {value}", settings)

    def test_all_eva_menu_options_are_removed(self):
        data = json.loads((ROOT / "app/data/pham-nhan-config.json").read_text(encoding="utf-8"))
        options = {option["key"]: option for option in data["options"]}

        for key in (
            "eva_life_key", "eva_wings_key", "eva_scythe_array_key", "eva_scythe_durability",
            "eva_scythe_dmg", "eva_scythe_recipe", "eva_hud", "eva_clothes",
        ):
            self.assertNotIn(key, options)
        self.assertEqual(len(options), 3)

    def test_removed_eva_options_use_fixed_runtime_values(self):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(r'''
GLOBAL = {
    require = function() return {DESCRIBE = {}} end,
    STRINGS = {
        CHARACTER_TITLES = {}, CHARACTER_NAMES = {}, CHARACTER_DESCRIPTIONS = {},
        CHARACTER_QUOTES = {}, CHARACTER_SURVIVABILITY = {}, NAMES = {},
        SKIN_NAMES = {}, SKIN_DESCRIPTIONS = {}, RECIPE_DESC = {},
        CHARACTERS = {EVA = {DESCRIBE = {}}, GENERIC = {DESCRIBE = {}}},
    },
}
TUNING = {
    GAMEMODE_STARTING_ITEMS = {DEFAULT = {}},
    STARTING_ITEM_IMAGE_OVERRIDE = {},
}
local overrides = {
    eva_scythe_dmg = 999,
    eva_scythe_recipe = 0,
    eva_hud = false,
    eva_clothes = false,
}
GetModConfigData = function(name) return overrides[name] end
''')
        lua.execute((ROOT / "mods/PhamNhanTuTien/scripts/util/eva_settings.lua").read_text(encoding="utf-8-sig"))
        tuning = lua.globals().TUNING
        self.assertEqual(tuning.EVA_SCYTHE_DMG, 68)
        self.assertEqual(tuning.EVA_SCYTHE_RECIPE, 1)
        self.assertTrue(tuning.EVA_HUD)
        self.assertTrue(tuning.EVA_HIDDEN)


if __name__ == "__main__":
    unittest.main()
