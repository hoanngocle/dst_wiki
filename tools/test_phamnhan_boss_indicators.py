"""Existing boss-pointer regression plus the nine-boss main/helper boundary."""
import os
import unittest
from test_phamnhan_boss_registry import ROOT, make_lua


class IndicatorTests(unittest.TestCase):
    def test_existing_indicator_contracts(self):
        previous = os.getcwd()
        try:
            os.chdir(ROOT)
            make_lua().execute((ROOT / 'mods/PhamNhanTuTien/tests/test_bossindicators.lua').read_text(encoding='utf-8'))
        finally:
            os.chdir(previous)

    def test_all_nine_main_bosses_visible_helpers_excluded(self):
        make_lua().execute('''
local indicators=require('ttk_bossindicators')
local defs=require('ttk_boss_defs')
for _,key in ipairs(defs.order) do
 local main=Entity(defs.bosses[key].prefab)
 assert(indicators.ShouldTrack(main),key..' is not tracked')
 local aux=Entity('ttk_boss_'..key..'_aux');aux:AddTag('epic');aux._ttk_boss_auxiliary=true
 assert(not indicators.ShouldTrack(aux),'helper produced a boss pointer')
end
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
