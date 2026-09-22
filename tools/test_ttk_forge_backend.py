"""Run forge rule regressions in Lua 5.1 without starting a DST server."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute("package.path = ... .. '/scripts/?.lua;' .. package.path", (ROOT / 'mods/PhamNhanTuTien').as_posix())
lua.execute('''
rules = require('utils/ttk_forge_rules')
local value = 'cleanse'
forge = {ttk_forge_mode = {value=function() return value end, set=function(_, v) value=v end}}
local nextid=10
function item(prefab, gear)
    nextid=nextid+1
    local id=nextid
    return {prefab=prefab, Network={GetNetworkID=function() return id end}, components=gear and {hh_equip={},equippable={}} or {},
        replica=gear and {equippable={}} or {}, HasTag=function(_,tag) return gear and tag=='hh_equip' end}
end
gear, stone, essence, fuel = item('spear',true),item('hh_effect_stone'),item('hh_essence'),item('nightmarefuel')
assert(rules.GetMode({inst=forge}) == 'cleanse')
for slot=1,5 do
    assert(rules.ItemTest(forge,gear,slot) == (slot==1), 'cleanse slot restriction')
    assert(not rules.ItemTest(forge,stone,slot))
end
forge.ttk_forge_mode:set('stone_change')
assert(rules.ItemTest({inst=forge},stone,2))
assert(rules.ItemTest(forge,essence,3))
assert(not rules.ItemTest(forge,gear,1))
assert(not rules.ItemTest(forge,essence,4))
forge.ttk_forge_mode:set('equip_inherit')
assert(rules.ItemTest(forge,gear,2) and rules.ItemTest(forge,gear,3))
assert(rules.ItemTest(forge,essence,4) and rules.ItemTest(forge,fuel,5))
assert(not rules.ItemTest(forge,fuel,4) and not rules.ItemTest(forge,gear,1))
assert(not rules.ItemTest(forge,item('ad_cleanStone'),1))
assert(not rules.ItemTest(forge,gear,nil))
''')
source = (ROOT / 'mods/PhamNhanTuTien/scripts/components/hh_player.lua').read_text(encoding='utf-8')
lua.execute('''
b_u__G = {}; TTKForgeRules = rules; B_U_g = {}; __b__UG_ = {}
_B__Ug__ = { HasComponents=function(_,inst,key) return inst and inst.components and inst.components[key] ~= nil end,
    HHClientRpc=function(_,_,key,value) if key=='hh_forge_equip' then last_rpc={key,value} end end, TableToStr=function(_,v) return v end }
''')
for name in ['CanUseForge', 'ReturnForgeItems', 'SetForgeMode', 'UpdateForgeEquipInfo', 'UpdateForgeState',
             'RemoveMoreEquipEffect', 'AddReplaceStone', 'EquipEffectInherit', 'CompoundEquipEffect', 'CompositeSuitEffect']:
    marker = 'function b_u__G:' + name + '('
    assert marker in source, 'Missing backend method: ' + name
    start = source.index(marker)
    end = source.find('\nfunction b_u__G:', start + 1)
    lua.execute(source[start:end])
lua.execute('''
local opened=true
local slots={[1]=gear,[2]=stone,[3]=essence,[4]=fuel,[5]=item('twigs')}
local returned={}
local player={suit_hh_guid=99, components={}, HasTag=function() return false end,
    GetPosition=function() return {x=3,y=0,z=7} end, GetDistanceSqToInst=function() return 4 end}
Ents={[99]={IsValid=function() return true end,HasTag=function(_,tag) return tag=='hh_suit_build' end}}
player.components.inventory={GiveItem=function(_,i,_,pos) assert(i.prevcontainer==nil and i.prevslot==nil); returned[#returned+1]=i; assert(pos.x==3) end}
forge.hh_ui_owner=player
forge.components={container={inst=forge, IsOpenedBy=function(_,p) return opened and p==player end,
    GetNumSlots=function() return 5 end, GetItemInSlot=function(_,s) return slots[s] end,
    RemoveItemBySlot=function(_,s) local i=slots[s];slots[s]=nil;if i then i.prevcontainer=forge;i.prevslot=s end;return i end}}
component=setmetatable({inst=player,forge_container=forge},{__index=b_u__G})
test_slots=slots
assert(component:SetForgeMode('cleanse'))
assert(#returned==5 and next(slots)==nil, 'every old slot must be returned')
assert(last_rpc[1]=='hh_forge_equip' and next(last_rpc[2])==nil, 'stale gear info cleared')
assert(rules.GetMode(forge)=='cleanse')
assert(not component:SetForgeMode('forged_mode'))
opened=false; assert(not component:SetForgeMode('stone_change'))
opened=true; player.GetDistanceSqToInst=function() return 37 end
assert(not component:SetForgeMode('stone_change'))
player.GetDistanceSqToInst=function() return 4 end
assert(not component:CanUseForge('equip_inherit'))
assert(component:CanUseForge('cleanse'))
player.HasTag=function(_,tag) return tag=='playerghost' end
assert(not component:CanUseForge('cleanse'))
player.HasTag=function() return false end
forge.hh_ui_owner={}; assert(not component:CanUseForge('cleanse')); forge.hh_ui_owner=player
slots[4]=fuel
assert(not component:CanUseForge('cleanse'), 'hidden legacy contents must reject an action')
''')
lua.execute('''
_B__Ug__.IsHHType=function(_,v,t) return type(v)==t end
-- Load the production validator against this fixture's crafted registry.
Class=function() return {} end
package.preload['utils/hh_utils']=function() return _B__Ug__ end
package.preload['enums/hh_enchant']=function()
    return {HH_EQUIP_BUFF_LIST=B_U_g,HH_GEM_BUFF_LIST=__b__UG_,HH_SUIT_LIST={}}
end
local HHEquip=require('components/hh_equip')
local slots=test_slots
slots[4]=nil
slots[1]=gear
gear.components.hh_equip.equip_buff_list={{name='a'},{name='b'}}
local cleaned=0
gear.components.hh_equip.ReduceMoreEquipBuff=function(_,selection)
    for _,v in pairs(selection) do if v then cleaned=cleaned+1 end end
    return true,cleaned,'cleaned'
end
local balance=2
component.GetItemsByKey=function() return balance end
component.RemoveItemsByKey=function(_,_,n) balance=balance-n end
assert(not component:RemoveMoreEquipEffect({true,'truthy'}), 'crafted truthy selection must reject')
assert(cleaned==0 and balance==2)
assert(component:RemoveMoreEquipEffect({true,false}))
assert(cleaned==1 and balance==1)
assert(not component:AddReplaceStone(), 'wrong mode rejected')
assert(not component:EquipEffectInherit(), 'wrong mode rejected')
assert(not component:CompoundEquipEffect('anything'))
assert(not component:CompositeSuitEffect('anything'))
slots[1]=nil; forge.ttk_forge_mode:set('stone_change')
slots[2]=stone; slots[3]=essence
stone.hh_effect='common'; B_U_g.common={can_add=true}; B_U_g.rare={can_add=false}
local essence_count=10
local container=forge.components.container
container.Has=function(_,prefab,count) return prefab=='hh_essence' and essence_count>=count end
container.ConsumeByName=function(_,prefab,count) assert(prefab=='hh_essence'); essence_count=essence_count-count end
container.GiveItem=function(_,i,slot) assert(rules.ItemTest(forge,i,slot)); slots[slot]=i end
stone.Remove=function() slots[2]=nil end
component.inst.name='Tester'
math.random=function() return .9 end
HHSpawnComEffectStone=function() local output=item('hh_effect_stone'); output.hh_effect='common'; return output end
assert(component:AddReplaceStone())
assert(essence_count==5 and slots[2]~=stone)
slots[2].hh_effect='rare'; assert(not component:AddReplaceStone()); assert(essence_count==5)
slots[2].hh_effect='unknown'; assert(not component:AddReplaceStone()); assert(essence_count==5)
forge.ttk_forge_mode:set('equip_inherit')
local donor,receiver=item('spear',true),item('armorwood',true)
slots[2]=donor;slots[3]=receiver;slots[4]=essence;slots[5]=fuel
donor.components.hh_equip.equip_buff_list={{name='a',value=3},{name='b',value=7}}
donor.components.hh_equip.GetEffectsNum=function() return 2 end
receiver.components.hh_equip.GetEffectsNum=function() return 0 end
receiver.components.hh_equip.equip_buff_list={}
receiver.components.hh_equip.equip_buff_limit=6
receiver.components.hh_equip.inst=receiver
receiver.components.hh_equip.ValidateEquipBuff=HHEquip.ValidateEquipBuff
receiver.components.hh_equip.AddEquipBuff=function(self,name,value) table.insert(self.equip_buff_list,{name=name,value=value}) end
local costs={hh_essence=20,nightmarefuel=20}
container.Has=function(_,prefab,n) return costs[prefab]>=n end
container.ConsumeByName=function(_,prefab,n) costs[prefab]=costs[prefab]-n end
donor.Remove=function() slots[2]=nil end
B_U_g.a={check_equip_can_add=function() return false end};B_U_g.b={}
assert(not component:EquipEffectInherit(), 'incompatible receiver rejected before donor or costs removed')
assert(slots[2]==donor and costs.hh_essence==20 and costs.nightmarefuel==20)
B_U_g.a={}
assert(component:EquipEffectInherit())
assert(slots[2]==nil and slots[3]==receiver and #receiver.components.hh_equip.equip_buff_list==2)
assert(costs.hh_essence==0 and costs.nightmarefuel==0)
''')
rpc_source = (ROOT / 'mods/PhamNhanTuTien/main/hh_rpc.lua').read_text(encoding='utf-8')
lua.execute('''
uFkUcCikg=function() return true end
iFkuiCkKf=_B__Ug__; iFkuiCkKf.HHSay=function() end
iFkuiCkKf.StrToTable=function() return {true} end
AddModRPCHandler=function(_,_,fn) test_forge_rpc=fn end
''')
lua.execute(rpc_source[rpc_source.index('local function iFcucCfkg('):rpc_source.index('local iFuUgciKc =')])
lua.execute('''
local actions=0
local hh={_ttk_forge_revision=7, UpdateForgeState=function(self) self._ttk_forge_revision=self._ttk_forge_revision+1 end,
    RemoveMoreEquipEffect=function() actions=actions+1; return true end}
local p={components={hh_player=hh},HasTag=function() return false end}
p.DoTaskInTime=function(_,_,fn) fn() end
test_forge_rpc(p,'CleanEffect','{true}',7)
assert(actions==1 and hh._ttk_forge_revision==8)
test_forge_rpc(p,'CleanEffect','{true}',7)
assert(actions==1, 'replayed index selection cannot execute twice')
test_forge_rpc(p,'CleanEffect','{true}')
assert(actions==1, 'old crafted RPC without revision cannot execute')
local revision=hh._ttk_forge_revision
p.hh_rpc_cd=true
test_forge_rpc(p,'CleanEffect','{true}',revision)
assert(actions==1 and hh._ttk_forge_revision==revision+1, 'cooldown refusal acknowledges pending client')
''')
for path in ['scripts/components/hh_player.lua', 'scripts/prefabs/hh_prefabs.lua', 'main/hh_rpc.lua']:
    lua.execute('assert(loadstring(...))', (ROOT / 'mods/PhamNhanTuTien' / path).read_text(encoding='utf-8'))
print('Forge backend rules, preservation, access, action costs/output, stale RPC rejection, syntax PASS')
