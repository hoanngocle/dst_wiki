"""Loot replacement and shipped boss relic asset regressions."""
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'mods/PhamNhanTuTien'
sys.path.insert(0, str(MOD / 'tools'))
from build_portal_assets import inspect_build, inspect_anim, inspect_ktex_alpha
import port_phamnhan_boss_combat as port
from test_phamnhan_boss_lifecycle import runtime


class RelicTests(unittest.TestCase):
    def test_source_regeneration_removes_only_retired_loot(self):
        for key, old in [('baihu', 'baihu_skin'), ('jfsn', 'fs'), ('qlch', 'qlr')]:
            path = 'scripts/prefabs/xd_' + key + '.lua'
            generated = port.prepare(path, port.read(path))
            self.assertEqual(generated, (MOD / ('scripts/prefabs/ttk_' + key + '.lua')).read_text(encoding='utf8'))
            self.assertNotRegex(generated, r'\{\s*[\"\x27]ttk_boss_' + old + r'[\"\x27]\s*,')
            self.assertIn('goldnugget', generated)
        legacy = (MOD / 'scripts/ttk_boss_collectible_defs.lua').read_text(encoding='utf8')
        for name in ['ttk_boss_baihu_skin', 'ttk_boss_fs', 'ttk_boss_qlr', 'ttk_boss_dy_']:
            self.assertNotIn(name, legacy)
        registered = runtime().execute(legacy)
        self.assertEqual(len(registered), 4)

    def test_six_bosses_award_one_core_and_one_summon(self):
        runtime().execute('''
local r=NewRegistry()
for _,key in ipairs({'baihu','jfsn','qlch','spiderqueen','stalke_fuben','deerclops_ziyun'}) do
 local def=defs.bosses[key];local b=Boss(key);assert(r:Register(key,b))
 assert(def.summon_name~=nil)
 assert(lifecycle.OnDeath(b,def));assert(not lifecycle.OnDeath(b,def))
 assert(b.drops[def.food]==1 and b.drops[def.summon]==1)
end
assert(defs.bosses.jfsn.food_name=='Kim Phượng Tinh Huyết')
assert(defs.bosses.stalke_fuben.summon_name=='Tâm Nhĩ Hắc Ám')
assert(defs.bosses.spiderqueen.summon_name=='Huyết Ngọc Tri Thù Noãn')
assert(defs.bosses.deerclops_ziyun.summon_name=='Độc Nhãn Tàn Hồn')
''')

    def test_six_icons_and_ground_sprites(self):
        for key in ['baihu', 'jfsn', 'qlch', 'spiderqueen', 'stalke_fuben', 'deerclops_ziyun']:
            for prefix in ['ttk_boss_core_', 'ttk_summon_']:
                name = prefix + key
                if name == 'ttk_summon_stalke_fuben':
                    continue  # native DST shadowheart art, verified by prefab test below
                atlas = MOD / 'images/inventoryimages' / (name + '.xml')
                root = ET.parse(atlas).getroot()
                self.assertEqual(name + '.tex', root.find('Texture').attrib['filename'])
                self.assertEqual(name + '.tex', root.find('Elements/Element').attrib['name'])
                self.assertEqual((0, 255), inspect_ktex_alpha(atlas.with_suffix('.tex')))
                with ZipFile(MOD / 'anim' / (name + '.zip')) as archive:
                    self.assertIsNone(archive.testzip())
                    build = inspect_build(archive.read('build.bin'))
                    self.assertEqual(name, build['name'])
                    self.assertEqual(['atlas-0.tex'], build['atlases'])
                    self.assertEqual('idle', inspect_anim(archive.read('anim.bin'))[0]['name'])
                    self.assertTrue(archive.read('atlas-0.tex').startswith(b'KTEX'))
        icons = MOD / 'images/inventoryimages'
        for name, old in [('ttk_boss_core_jfsn', 'xd_fs'), ('ttk_boss_core_qlch', 'xd_dy_lmsqd_5'), ('ttk_summon_spiderqueen','xd_htz_xyzzl'), ('ttk_summon_deerclops_ziyun','xd_sudaji_soul'), ('ttk_boss_core_deerclops_ziyun','xd_hxyp')]:
            self.assertEqual((icons / (old+'.tex')).read_bytes(), (icons / (name+'.tex')).read_bytes())

    def test_summon_prefabs_keep_keys_and_use_correct_images(self):
        lua = runtime()
        lua.execute('''
TUNING={STACK_SIZE_SMALLITEM=40}
function Asset(kind,path) return {kind=kind,path=path} end
function Prefab(name,fn,assets) return {name=name,fn=fn,assets=assets} end
function GetInventoryItemAtlas(name) assert(name=='shadowheart.tex');return 'images/inventoryimages3.xml' end
function MakeInventoryPhysics() end
function MakeInventoryFloatable() end
function MakeHauntableLaunch() end
function CreateEntity()
 local item={entity={},AnimState={},components={},tags={}}
 for _,name in ipairs({'AddTransform','AddAnimState','AddNetwork','SetPristine'}) do item.entity[name]=function() end end
 for _,name in ipairs({'SetBank','SetBuild','PlayAnimation'}) do item.AnimState[name]=function(self,value) self[name]=value end end
 function item:AddTag(tag) self.tags[tag]=true end
 function item:AddComponent(name)
  self.components[name]={ChangeImageName=function(self,value) self.imagename=value end}
 end
 return item
end
TheWorld.ismastersim=true
''')
        lua.globals().summon_file = (MOD / 'scripts/prefabs/ttk_boss_summons.lua').as_posix()
        lua.execute('''
local items={assert(loadfile(summon_file))()};assert(#items==6)
for _,prefab in ipairs(items) do
 local inst=prefab.fn();local key=inst.components.ttk_bosssummoner.key
 local def=require('ttk_boss_defs').bosses[key]
 assert(prefab.name==def.summon)
 assert(inst.components.inventoryitem.imagename==(def.summon_icon or def.summon))
 assert(inst.AnimState.SetBuild==(def.summon_icon or def.summon))
 assert(not inst.tags.shadowheart and inst.tags.ttk_boss_summon)
end
''')


if __name__ == '__main__':
    unittest.main()
