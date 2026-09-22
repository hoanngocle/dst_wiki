from pathlib import Path
import sys
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / ".superpowers/ttk-solo-integration/lua-runtime"))
from lupa.lua51 import LuaRuntime


lua = LuaRuntime(unpack_returned_tuples=True)
with ZipFile("C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip") as game:
    lua.execute(game.read("scripts/class.lua").decode())
    lua.globals().Trader = lua.execute(game.read("scripts/components/trader.lua").decode())
    lua.globals().FiniteUses = lua.execute(game.read("scripts/components/finiteuses.lua").decode())
lua.globals().package.path = str(ROOT / "scripts/?.lua").replace("\\", "/") + ";" + lua.globals().package.path
lua.execute(r'''
local function noop() end
local dummy = setmetatable({}, {__index = function() return noop end})
TUNING = {EVA_SCYTHE_DMG = 68, EVA_SCYTHE_DURABILITY = 666}
TheWorld = {ismastersim = true}
Asset = function(...) return {...} end
Prefab = function(name, fn, assets, deps) return {name = name, fn = fn, assets = assets, deps = deps} end
MakeInventoryPhysics = noop
MakeInventoryFloatable = noop
MakeHauntableLaunch = noop
function CreateEntity()
    local entity = {entity = dummy, AnimState = dummy, MiniMapEntity = dummy, components = {}, tags = {}, events = {}}
    function entity:AddTag(tag) self.tags[tag] = true end
    function entity:RemoveTag(tag) self.tags[tag] = nil end
    function entity:HasTag(tag) return self.tags[tag] == true end
    function entity:IsValid() return not self.removed end
    function entity:Remove() self.removed = true end
    function entity:PushEvent(name, data) if self.events[name] then self.events[name](self, data) end end
    function entity:ListenForEvent(name, fn) self.events[name] = fn end
    function entity:AddComponent(name)
        if name == "finiteuses" then self.components[name] = FiniteUses(self)
        elseif name == "trader" then self.components[name] = Trader(self)
        else
            local component = {inst = self}
            self.components[name] = component
            if name == "weapon" then function component:SetDamage(value) self.damage = value end
            elseif name == "equippable" then
                function component:SetOnEquip(fn) self.onequip = fn end
                function component:SetOnUnequip(fn) self.onunequip = fn end
            end
        end
    end
    return entity
end
''')
lua.globals().scythe_prefab = lua.execute((ROOT / "scripts/prefabs/eva_scythe.lua").read_text(encoding="utf-8"))
lua.execute(r'''
local scythe = scythe_prefab.fn()
local uses = scythe.components.finiteuses
assert(uses.total == 1000 and uses:GetUses() == 1000)
uses:Use(1000)
assert(scythe:IsValid() and uses:GetUses() == 0)
local consumed = 0
local function donor(name)
    local item = CreateEntity()
    item.prefab = name
    item.components.inventoryitem = {RemoveFromOwner = function() end}
    function item:Remove() consumed = consumed + 1; self.removed = true end
    return item
end
local trader = scythe.components.trader
assert(not trader:AcceptGift(nil, donor("twigs")))
assert(trader:AcceptGift(nil, donor("spear")))
assert(consumed == 1 and uses:GetUses() == 25)
assert(trader:AcceptGift(nil, donor("nightsword")) and uses:GetUses() == 125)
uses:SetUses(999)
assert(trader:AcceptGift(nil, donor("spear")) and uses:GetUses() == 1000)
assert(not trader:AcceptGift(nil, donor("spear")))
print("PASS: EVA scythe has 1000 uses, survives depletion and recharges from weapon donors")
''')
