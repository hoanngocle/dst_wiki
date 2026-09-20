"""Tiên Hà backpack layout, equipment and legacy-stack migration contracts."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mods/PhamNhanTuTien'
sys.path.insert(0,str(ROOT/'.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime

class BackpackTests(unittest.TestCase):
    def lua(self):
        lua=LuaRuntime()
        lua.execute('''
GLOBAL=_G;PrefabFiles={};Assets={};STRINGS={NAMES={},CHARACTERS={GENERIC={DESCRIBE={}}}}
containers={params={},MAXITEMSLOTS=12};package.loaded.containers=containers
function Vector3(x,y,z) return {x=x,y=y,z=z} end
function Asset(t,p) return {type=t,path=p} end
function RegisterInventoryItemAtlas() end
function Prefab(n,fn,a) return {name=n,fn=fn,assets=a} end
EQUIPSLOTS={BACK='back',BODY='body'};TheWorld={ismastersim=true}
function MakeInventoryPhysics() end;function MakeInventoryFloatable() end
function MakeHauntableLaunchAndDropFirstItem() end
tasks={};spawned={}
function CreateEntity()
 local inst={components={},tags={},entity={},AnimState={},Transform={}}
 for _,n in ipairs({'AddTransform','AddAnimState','AddNetwork','SetPristine'}) do inst.entity[n]=function() end end
 for _,n in ipairs({'SetBank','SetBuild','PlayAnimation'}) do inst.AnimState[n]=function() end end
 inst.Transform.GetWorldPosition=function() return 10,0,20 end
 inst.Transform.SetPosition=function(_,x,y,z) inst.pos={x,y,z} end
 function inst:AddTag(t) self.tags[t]=true end
 function inst:AddComponent(n)
  local c={};self.components[n]=c
  if n=='inventoryitem' then c.ChangeImageName=function(s,v) s.imagename=v end;c.GetGrandOwner=function() return nil end
  elseif n=='container' then
   c.WidgetSetup=function(s,k) s.numslots=#containers.params[k].widget.slotpos end
   c.Open=function(s,o) s.owner=o end;c.Close=function(s) s.owner=nil end
  elseif n=='equippable' then
   for _,v in ipairs({'OnEquip','OnUnequip','OnEquipToModel'}) do c['Set'..v]=function(s,fn) s[v]=fn end end
  end
 end
 function inst:DoTaskInTime(_,fn) table.insert(tasks,function() fn(self) end) end
 return inst
end
function RunTasks() local q=tasks;tasks={};for _,fn in ipairs(q) do fn() end end
function SpawnPrefab(n) local e=CreateEntity();e.prefab=n;table.insert(spawned,e);return e end
''')
        lua.execute((MOD/'main/ttk_boss_backpack.lua').read_text(encoding='utf8'))
        lua.globals().bag=lua.execute((MOD/'scripts/prefabs/ttk_boss_back_xh.lua').read_text(encoding='utf8'))
        return lua

    def test_layout_and_equipment(self):
        self.lua().execute('''
local p=containers.params.ttk_boss_back_xh
assert(#p.widget.slotpos==18 and p.type=='pack' and p.issidewidget)
local xs,ys={},{};for _,v in ipairs(p.widget.slotpos) do xs[v.x]=true;ys[v.y]=true end
local x,y=0,0;for _ in pairs(xs) do x=x+1 end;for _ in pairs(ys) do y=y+1 end
assert(x==3 and y==6 and containers.MAXITEMSLOTS>=18)
local b=bag.fn();assert(b.components.container.numslots==18)
assert(b.components.equippable.equipslot=='back' and b.tags.backpack)
assert(not b.components.stackable and not b.components.armor and not b.components.preserver)
assert(b.components.inventoryitem.cangoincontainer==false)
local owner={AnimState={OverrideSymbol=function() end,ClearOverrideSymbol=function() end}}
b.components.equippable.OnEquip(b,owner);assert(b.components.container.owner==owner)
b.components.equippable.OnUnequip(b,owner);assert(b.components.container.owner==nil)
TheWorld.ismastersim=false;local client=bag.fn();assert(client.tags.backpack and next(client.components)==nil)
''')

    def test_legacy_stack_is_preserved_once_and_pending_count_is_saved(self):
        self.lua().execute('''
local b=bag.fn();b.prefab=bag.name;b:OnLoad({stackable={stack=3}})
local data={};b:OnSave(data);assert(data.ttk_legacy_bags==2)
RunTasks();assert(#spawned==2 and spawned[1].prefab==bag.name)
local saved={};b:OnSave(saved);assert(not saved.ttk_legacy_bags)
local loaded=bag.fn();loaded.prefab=bag.name;loaded:OnLoad(saved);RunTasks();assert(#spawned==2)
local pending=bag.fn();pending.prefab=bag.name;pending:OnLoad(data);RunTasks();assert(#spawned==4)
''')

if __name__=='__main__':unittest.main()
