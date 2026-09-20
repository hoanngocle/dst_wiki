"""World lifecycle and summon transaction tests with Lua 5.1."""
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime

def make_lua():
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.globals().root=(ROOT/'mods/PhamNhanTuTien/scripts').as_posix()
    lua.execute('''
package.path=root..'/?.lua;'..package.path
function Class(init)
 local c={}; c.__index=c
 return setmetatable(c,{__call=function(_,...) local o=setmetatable({},c);init(o,...);return o end})
end
function Vector3(x,y,z) return {x=x,y=y,z=z} end
Ents={}; AllPlayers={}; serial=1
function Entity(prefab)
 serial=serial+1
 local e={GUID=serial,prefab=prefab,components={},tags={},valid=true,x=200,z=200}
 function e:IsValid() return self.valid end
 function e:HasTag(t) return self.tags[t] or false end
 function e:AddTag(t) self.tags[t]=true end
 function e:Remove() self.valid=false; Ents[self.GUID]=nil end
 function e:ListenForEvent() end
 function e:DoTaskInTime() return {Cancel=function() end} end
 e.Transform={GetWorldPosition=function() return e.x,0,e.z end,SetPosition=function(x,y,z) e.x=x;e.z=z end}
 e.components.health={IsDead=function() return false end}
 e.components.lootdropper={SpawnLootPrefab=function() end}
 Ents[e.GUID]=e
 return e
end
TheWorld=Entity('world'); TheWorld.ismastersim=true
TheWorld.Map={IsAboveGroundAtPoint=function() return true end,IsPassableAtPoint=function() return true end,
 IsOceanAtPoint=function() return false end,IsPointNearHole=function() return false end}
TheSim={FindEntities=function() return {} end}
package.loaded.ttk_tianjimap={Contains=function() return false end}
function SpawnPrefab(name) return Entity(name) end
Registry=require('components/ttk_bossregistry')
function NewRegistry() local r=Registry(TheWorld);TheWorld.components.ttk_bossregistry=r;r.ready=true;return r end
function PlayerAndItem(key,count)
 local p=Entity('wilson');p:AddTag('player');p.userid='player1'
 p.components.inventory={IsHolding=function(_,i) return i.owner==p end}
 local item=Entity('ttk_summon_'..key);item.owner=p
 item.components.inventoryitem={GetGrandOwner=function() return item.owner end}
 item.components.stackable={stacksize=count,Get=function(s,n) s.stacksize=s.stacksize-(n or 1);return {Remove=function()end} end}
 return p,item
end
''')
    return lua

class RegistryTests(unittest.TestCase):
    def test_setup_exception_removes_partial_boss_without_spending_token(self):
        make_lua().execute('''local r=NewRegistry();r.entries.baihu={status='dead'}
local p,item=PlayerAndItem('baihu',3);local partial
SpawnPrefab=function(name)
 partial=Entity(name);partial.components.knownlocations={RememberLocation=function() error('setup failure') end}
 return partial
end
assert(not r:TrySummon('baihu',p,item));assert(item.components.stackable.stacksize==3)
assert(not partial:IsValid());assert(r.entries.baihu.status=='dead');assert(not r.busy.baihu)
''')

    def test_portal_clearance_also_applies_to_summons(self):
        make_lua().execute('''local r=NewRegistry();local portal=Entity('portal');portal:AddTag('multiplayer_portal')
portal.x=240;portal.z=200
TheSim.FindEntities=function(_,x,y,z,radius) assert(radius>=60);return {portal} end
assert(not r:FreePoint(200,200,false))
''')

    def test_dead_unique_is_terminal_after_load(self):
        make_lua().execute('''local r=NewRegistry();local b=Entity('ttk_qxdx')
assert(r:Register('qxdx',b));assert(r:MarkDead('qxdx',b));assert(not r:MarkDead('qxdx',b))
local data=r:OnSave();local n=NewRegistry();n:OnLoad(data);n:LoadPostPass({},data)
assert(n.entries.qxdx.status=='dead');assert(not n:CanSpawn('qxdx',false))
''')
    def test_live_and_missing_entities_never_reseed(self):
        make_lua().execute('''local r=NewRegistry();local b=Entity('ttk_baihu');assert(r:Register('baihu',b))
local data=r:OnSave();local n=NewRegistry();n:OnLoad(data);n:LoadPostPass({[b.GUID]={entity=b}},data)
assert(n.entries.baihu.status=='alive');assert(not n:CanSpawn('baihu',false))
b:Remove();local m=NewRegistry();m:OnLoad(data);m:LoadPostPass({},data)
assert(m.entries.baihu.status~='unspawned');assert(not m:CanSpawn('baihu',false))
''')
    def test_auxiliary_does_not_occupy_or_finish_main(self):
        make_lua().execute('''local r=NewRegistry();local b=Entity('ttk_deerclops_ziyun');b._ttk_boss_auxiliary=true
assert(not r:Register('deerclops_ziyun',b));assert(not r:MarkDead('deerclops_ziyun',b))
assert(r:CanSpawn('deerclops_ziyun',false))
''')
    def test_summon_consumes_once_and_blocks_duplicate(self):
        make_lua().execute('''local r=NewRegistry();r.entries.baihu={status='dead'}
local p,item=PlayerAndItem('baihu',3)
assert(r:TrySummon('baihu',p,item));assert(item.components.stackable.stacksize==2)
assert(not r:TrySummon('baihu',p,item));assert(item.components.stackable.stacksize==2)
''')
    def test_failed_spawn_wrong_owner_and_caves_preserve_item(self):
        make_lua().execute('''local r=NewRegistry();r.entries.baihu={status='dead'}
local p,item=PlayerAndItem('baihu',3);SpawnPrefab=function() return nil end
assert(not r:TrySummon('baihu',p,item));assert(item.components.stackable.stacksize==3)
item.owner=Entity('wilson');assert(not r:TrySummon('baihu',p,item));assert(item.components.stackable.stacksize==3)
item.owner=p;TheWorld:AddTag('cave');assert(not r:TrySummon('baihu',p,item));assert(item.components.stackable.stacksize==3)
assert(not r:TrySummon('qxdx',p,item))
''')

if __name__=='__main__': unittest.main(verbosity=2)
