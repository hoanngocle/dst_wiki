"""Fixed Thanh Tu seed loot and plantable source-tree seed contracts."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mods/PhamNhanTuTien'
sys.path.insert(0,str(ROOT/'.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime
import port_phamnhan_boss_combat as port
import port_phamnhan_seed_tree as trees
from zipfile import ZipFile
import xml.etree.ElementTree as ET

class SeedTests(unittest.TestCase):
    def test_herb_harvest_tool_seed_chance_and_conditional_quantity(self):
        code=(MOD/'scripts/prefabs/ttk_herbs.lua').read_text(encoding='utf8')
        callback=code[code.index('    local function OnPicked'):code.index('    local function SetPickable')]
        for suffix in ['hsc','dms','qfx','cyh','lmg','yhh']:
            for tool,roll,quantity_roll,seeds in [(True,.74,.24,2),(True,.74,.25,1),(True,.74,.99,1),(True,.75,.1,0),(False,.39,.1,1),(False,.4,.1,0)]:
                lua=LuaRuntime()
                lua.globals().suffix=suffix
                lua.globals().has_tool=tool
                lua.globals().roll=roll
                lua.globals().quantity_roll=quantity_roll
                lua.globals().expected=seeds
                lua.execute('''
data={};tool_calls=0;items={}
package.preload.ttk_herbtool=function() return function() tool_calls=tool_calls+1;return has_tool end end
random_calls=0
math.random=function() random_calls=random_calls+1;return random_calls==1 and roll or quantity_roll end
SpawnPrefab=function(name) return {prefab=name} end
local inventory={GiveItem=function(_,item) items[item.prefab]=(items[item.prefab] or 0)+1 end}
doer={components={inventory=inventory}}
plant={GetPosition=function() return {} end}
'''+callback+'''
OnPicked(plant,doer)
assert(items['ttk_lc_'..suffix]==1)
assert((items['ttk_lc_'..suffix..'_seed'] or 0)==expected)
assert(tool_calls==1)
assert(random_calls==((has_tool and expected>0) and 2 or 1))
''')

    def test_tree_port_and_assets_remain_reproducible(self):
        for name,code in [('ttk_zuichunyan',trees.tree_code()),('ttk_zuichunyan_saplings',trees.sapling_code())]:
            self.assertEqual(code,(MOD/'scripts/prefabs'/(name+'.lua')).read_text(encoding='utf8'))
            self.assertIsNone(LuaRuntime().eval('function(s) local f,e=loadstring(s);return e end')(code))
        for colour in ['green','purple']:
            with ZipFile(MOD/'anim'/('xd_zuichunyan_'+colour+'.zip')) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('build.bin',archive.namelist())
        for variant in ['green','purple','stump','burnt']:
            p=MOD/'images/map_icons'/('ttk_zuichunyan_'+variant+'.xml')
            atlas=ET.parse(p).getroot()
            self.assertTrue((p.parent/atlas.find('Texture').attrib['filename']).exists())
        factory=(MOD/'scripts/prefabs/ttk_boss_collectibles.lua').read_text(encoding='utf8')
        self.assertIn('name ~= "ttk_boss_zcyseed"',factory)

    def test_fixed_twenty_seed_death_reward_without_pills(self):
        code=(MOD/'scripts/prefabs/ttk_qxdx.lua').read_text(encoding='utf8')
        self.assertNotIn('RandomFivePill',code)
        self.assertNotIn('RandomTwoSeeds',code)
        start=code.index('local fixed_seed_loot')
        end=code.index('local function OnEntityWake',start)
        lua=LuaRuntime()
        lua.execute(code[start:end]+'''
local drops={};local inst={components={lootdropper={SpawnLootPrefab=function(_,name) drops[name]=(drops[name] or 0)+1 end}}}
OnDeath(inst);OnDeath(inst)
assert(drops.ttk_boss_zcyseed==2)
local count=0
for _,suffix in ipairs({'hsc','dms','qfx','cyh','lmg','yhh'}) do assert(drops['ttk_lc_'..suffix..'_seed']==3) end
for _,n in pairs(drops) do count=count+n end;assert(count==20)
''')
        self.assertEqual(code,port.prepare('scripts/prefabs/xd_qxdx.lua',port.read('scripts/prefabs/xd_qxdx.lua')))

    def test_seed_factory_edible_and_deploy_consumes_only_on_success(self):
        lua=LuaRuntime()
        lua.execute('''
TheWorld={ismastersim=true};FOODTYPE={SEEDS='SEEDS'};DEPLOYMODE={PLANT='PLANT'}
TUNING={STACK_SIZE_SMALLITEM=120,PERISH_PRESERVED=9600}
function Asset() end;function Prefab(n,fn) return {name=n,fn=fn} end
function MakePlacer() return {} end
function MakeInventoryPhysics() end;function MakeInventoryFloatable() end;function MakeHauntableLaunchAndPerish() end
function CreateEntity()
 local i={components={},tags={},entity={},AnimState={}}
 for _,n in ipairs({'AddTransform','AddAnimState','AddNetwork','SetPristine'}) do i.entity[n]=function() end end
 for _,n in ipairs({'SetBank','SetBuild','PlayAnimation'}) do i.AnimState[n]=function() end end
 function i:AddTag(t) self.tags[t]=true end
 function i:AddComponent(n)
  local c={};self.components[n]=c
  c.SetDeployMode=function(s,v) s.mode=v end;c.SetPerishTime=function() end;c.StartPerishing=function() end
  c.ChangeImageName=function() end
  c.Get=function() return {Remove=function() i.consumed=(i.consumed or 0)+1 end} end
 end
 return i
end
lastspawn=nil;failspawn=false
function SpawnPrefab(n)
 if failspawn then return nil end
 lastspawn=n;return {Transform={SetPosition=function() end}}
end
''')
        lua.globals().seed=lua.execute((MOD/'scripts/prefabs/ttk_boss_zcyseed.lua').read_text(encoding='utf8'))[0]
        lua.execute('''
local inst=seed.fn();local food=inst.components.edible
assert(food.healthvalue==5 and food.hungervalue==12 and food.sanityvalue==2)
assert(food.foodtype==FOODTYPE.SEEDS and inst.components.deployable.mode==DEPLOYMODE.PLANT)
local pt={Get=function() return 1,0,2 end}
math.random=function() return .25 end;inst.components.deployable.ondeploy(inst,pt,nil)
assert(lastspawn=='ttk_zuichunyan_green_sapling' and inst.consumed==1)
math.random=function() return .75 end;inst.components.deployable.ondeploy(inst,pt,nil)
assert(lastspawn=='ttk_zuichunyan_purple_sapling' and inst.consumed==2)
failspawn=true;inst.components.deployable.ondeploy(inst,pt,nil);assert(inst.consumed==2)
TheWorld.ismastersim=false;local client=seed.fn();assert(next(client.components)==nil)
''')

if __name__=='__main__':unittest.main()
