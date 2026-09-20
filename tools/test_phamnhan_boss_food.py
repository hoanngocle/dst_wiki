"""Executable contracts for Pham Nhan boss-core progression (Lua 5.1)."""

from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "mods" / "PhamNhanTuTien"
sys.path.insert(0, str(ROOT / ".superpowers" / "ttk-solo-integration" / "lua-runtime"))

from lupa.lua51 import LuaRuntime


FOODS = (
    "baihu",
    "jfsn",
    "qlch",
    "spiderqueen",
    "stalke_fuben",
    "deerclops_ziyun",
)


def make_lua():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.globals().root = (MOD / "scripts").as_posix()
    lua.globals().modroot = MOD.as_posix()
    lua.execute(
        r'''
package.path = root .. '/?.lua;' .. package.path

function Class(init)
    local class = {}
    class.__index = class
    return setmetatable(class, {
        __call = function(_, ...)
            local object = setmetatable({}, class)
            init(object, ...)
            return object
        end,
    })
end

local component_postinits = {}
local player_postinits = {}
function AddComponentPostInit(name, fn)
    component_postinits[name] = component_postinits[name] or {}
    table.insert(component_postinits[name], fn)
end
function AddPlayerPostInit(fn) table.insert(player_postinits, fn) end
function RunComponentPostInits(name, component)
    for _, fn in ipairs(component_postinits[name] or {}) do fn(component) end
end

TheWorld = {ismastersim=true}
TheNet = {IsDedicated=function() return false end}
FOODTYPE = {GOODIES='GOODIES',MEAT='MEAT'}
TUNING = {STACK_SIZE_SMALLITEM=40}
STRINGS = {NAMES={}, CHARACTERS={GENERIC={DESCRIBE={}}}}
PrefabFiles = {}
Assets = {}
env = setmetatable({
    AddComponentPostInit=AddComponentPostInit,
    AddPlayerPostInit=AddPlayerPostInit,
    PrefabFiles=PrefabFiles,
    Assets=Assets,
}, {__index=_G})
GLOBAL = _G
function Asset(kind, file) return {type=kind,file=file} end
function RegisterInventoryItemAtlas() end
function Prefab(name, fn, assets) return {name=name,fn=fn,assets=assets} end
function MakeInventoryPhysics() end
function MakeInventoryFloatable() end
function MakeHauntableLaunch() end
function CreateEntity()
    local inst={components={},tags={}}
    inst.entity={AddTransform=function() end,AddAnimState=function() end,AddNetwork=function() end,
        SetPristine=function() end}
    inst.AnimState={
        SetBank=function(self, value) self.bank=value end,
        SetBuild=function(self, value) self.build=value end,
        PlayAnimation=function(self, value) self.animation=value end,
        SetScale=function(self, x, y, z) self.scale={x,y,z} end,
        OverrideSymbol=function(self, symbol, build, swap)
            self.override={symbol=symbol,build=build,swap=swap}
        end,
    }
    function inst:AddTag(tag) self.tags[tag]=true end
    function inst:HasTag(tag) return self.tags[tag] or false end
    function inst:AddComponent(name)
        local component={inst=self}
        if name=='edible' then
            function component:SetOnEatenFn(fn) self.oneaten=fn end
        end
        self.components[name]=component
        return component
    end
    return inst
end
local function bounded_netfield(maximum)
    local value = 0
    return {
        set=function(_, v) value=math.max(0,math.min(maximum,math.floor(v))) end,
        value=function() return value end,
    }
end
function net_tinybyte(_, _, _) return bounded_netfield(7) end
function net_smallbyte(_, _, _) return bounded_netfield(63) end

local next_guid = 100
local function netfield()
    local value = 0
    return {set=function(_, v) value=v end, value=function() return value end}
end

function NewPlayer()
    next_guid = next_guid + 1
    local inst = {GUID=next_guid, components={}, tags={player=true}, events={}}
    function inst:IsValid() return true end
    function inst:HasTag(tag) return self.tags[tag] or false end
    function inst:AddComponent(name)
        if name == 'ttk_bossprogress' then
            self.components[name] = require('components/ttk_bossprogress')(self)
        end
        return self.components[name]
    end
    function inst:DoTaskInTime(_, fn) fn(self); return {Cancel=function() end} end
    function inst:PushEvent(name, data) self.events[name]=data end

    local health = {inst=inst,maxhealth=100,currenthealth=37}
    function health:SetMaxHealth(value) self.maxhealth=value; self.currenthealth=value end
    function health:SetCurrentHealth(value) self.currenthealth=math.max(0,math.min(value,self.maxhealth)) end
    function health:GetMaxWithPenalty() return self.maxhealth end
    function health:OnLoad(data) self:SetCurrentHealth(data.health) end
    inst.components.health=health

    local hunger = {inst=inst,max=150,current=43}
    function hunger:SetMax(value) self.max=value; self.current=value end
    -- Native DST intentionally omits the record for full hunger.
    function hunger:OnSave() return self.current ~= self.max and {hunger=self.current} or nil end
    function hunger:OnLoad(data) self.current=math.max(0,math.min(data.hunger,self.max)) end
    inst.components.hunger=hunger

    local sanity = {inst=inst,max=200,current=51}
    function sanity:SetMax(value) self.max=value; self.current=value end
    function sanity:OnLoad(data) self.current=math.max(0,math.min(data.current,self.max)) end
    inst.components.sanity=sanity

    local hh_player={inst=inst,hh_effects={trueDamageNum=7,criticalHitRate=3,reduceAttackedDamage=5,
        immuneHot=0,immuneCold=0,immunePoison=0,immunitySleep=0,immuneFreeze=0}}
    function hh_player:GetEffectValueByKey(key) return self.hh_effects[key] or 0 end
    function hh_player:HasSpecialEffect(key) return self:GetEffectValueByKey(key)>0 end
    inst.components.hh_player=hh_player

    local mana={inst=inst,current=61,max=100,base=100}
    function mana:RecalculateMax(fill_initial)
        self.max=self.base
        if fill_initial then self.current=self.max else self.current=math.min(self.current,self.max) end
    end
    function mana:Sync() self.synced=(self.synced or 0)+1 end
    function mana:OnLoad(data)
        self:RecalculateMax(false)
        self.current=math.max(0,math.min(data.current,self.max))
        self:Sync()
    end
    inst.components.hh_mana=mana

    RunComponentPostInits('health',health)
    RunComponentPostInits('hunger',hunger)
    RunComponentPostInits('sanity',sanity)
    RunComponentPostInits('hh_player',hh_player)
    RunComponentPostInits('hh_mana',mana)
    for _, fn in ipairs(player_postinits) do fn(inst) end
    return inst
end

function LoadFoodMain()
    local chunk=assert(loadfile(modroot..'/main/ttk_boss_food.lua'))
    setfenv(chunk, env)
    chunk()
end
'''
    )
    return lua


class BossFoodTests(unittest.TestCase):
    def test_tenth_unlocks_once_and_eleventh_only_restores(self):
        lua = make_lua()
        lua.execute(
            """
local Progress=require('components/ttk_bossprogress')
local p=NewPlayer(); local progress=Progress(p); p.components.ttk_bossprogress=progress
for i=1,10 do local accepted,count=progress:Absorb('baihu'); assert(accepted and count==i) end
assert(progress:GetCount('baihu')==10)
assert(progress:GetEffectBonus('trueDamageNum')==40)
assert(progress:GetEffectBonus('criticalHitRate')==10)
local accepted,count=progress:Absorb('baihu')
assert(not accepted and count==10)
assert(progress:GetEffectBonus('trueDamageNum')==40)
assert(progress:GetEffectBonus('criticalHitRate')==10)
assert(progress:GetCount('qlch')==0)
"""
        )

    def test_load_replay_and_equipment_coexist_without_inflation(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local p=NewPlayer(); local progress=p.components.ttk_bossprogress
for i=1,10 do progress:Absorb('baihu') end
assert(p.components.hh_player:GetEffectValueByKey('trueDamageNum')==47)
assert(p.components.hh_player:GetEffectValueByKey('criticalHitRate')==13)
assert(p.ttk_bossprogress_baihu:value()==10)
p.components.ttk_bossprogress=nil
assert(p:GetTtkBossProgressCount('baihu')==10)
p.components.ttk_bossprogress=progress
p.components.hh_player.hh_effects.trueDamageNum=2
assert(p.components.hh_player:GetEffectValueByKey('trueDamageNum')==42)
local data=progress:OnSave()
progress:OnLoad(data); progress:OnLoad(data); progress:Refresh()
assert(progress:GetCount('baihu')==10)
assert(p.components.hh_player:GetEffectValueByKey('trueDamageNum')==42)
assert(p.components.hh_player:GetEffectValueByKey('criticalHitRate')==13)
"""
        )

    def test_max_stats_keep_current_and_mana_recalculation_is_stable(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local p=NewPlayer(); local progress=p.components.ttk_bossprogress
for i=1,4 do progress:Absorb('jfsn') end
for i=1,3 do progress:Absorb('qlch') end
for i=1,2 do progress:Absorb('spiderqueen') end
for i=1,5 do progress:Absorb('deerclops_ziyun') end
assert(p.components.health.maxhealth==180 and p.components.health.currenthealth==37)
assert(p.components.hunger.max==190 and p.components.hunger.current==43)
assert(p.components.sanity.max==300 and p.components.sanity.current==51)
assert(p.components.hh_mana.max==160 and p.components.hh_mana.current==61)
p.components.hh_mana.current=151
p.components.hh_mana.base=140
p.components.hh_mana:RecalculateMax(false)
assert(p.components.hh_mana.max==200 and p.components.hh_mana.current==151)
p.components.hh_mana:RecalculateMax(false)
assert(p.components.hh_mana.max==200 and p.components.hh_mana.current==151)
p.components.health:SetMaxHealth(120)
assert(p.components.health.maxhealth==200)
"""
        )

    def test_visible_max_modifiers_do_not_reapply_food_bonus(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local p=NewPlayer(); local progress=p.components.ttk_bossprogress
-- A normal SetMaxHealth argument is always a new base, even when it jumps
-- farther than the permanent food bonus.
p.components.health:SetMaxHealth(150)
for i=1,10 do progress:Absorb('jfsn') end
assert(p.components.health.maxhealth==350)
p.components.health:SetMaxHealth(300)
assert(p.components.health.maxhealth==500)

-- Solo's timed dungeon effect is the one known caller that passes a visible
-- maximum.  Its component post-init marks that narrow call scope.
local dungeon={inst=p,delta=0}
function dungeon:RefreshTargets()
 local health=self.inst.components.health
 health:SetMaxHealth(health.maxhealth+self.delta)
end
RunComponentPostInits('hh_dungeon_effects',dungeon)
local dungeon_bonus=p.components.health.maxhealth*.20
dungeon.delta=dungeon_bonus; dungeon:RefreshTargets()
assert(p.components.health.maxhealth==600)
dungeon.delta=-dungeon_bonus; dungeon:RefreshTargets()
assert(p.components.health.maxhealth==500)
progress:Refresh()
assert(p.components.health.maxhealth==500)
"""
        )

    def test_augmented_current_values_survive_both_component_load_orders(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local counts={version=1,counts={jfsn=10,qlch=10,spiderqueen=10,deerclops_ziyun=10}}
local function load_stats(p)
 p.components.health:OnLoad({health=300})
 p.components.hunger:OnLoad({hunger=350})
 p.components.sanity:OnLoad({current=400})
 p.components.hh_mana:OnLoad({current=300})
end
local function check(p)
 assert(p.components.health.maxhealth==300 and p.components.health.currenthealth==300)
 assert(p.components.hunger.max==350 and p.components.hunger.current==350)
 assert(p.components.sanity.max==400 and p.components.sanity.current==400)
 assert(p.components.hh_mana.max==300 and p.components.hh_mana.current==300)
end

-- Native stat components load first and initially clamp to their base maxima.
local components_first=NewPlayer()
load_stats(components_first)
components_first.components.ttk_bossprogress:OnLoad(counts)
check(components_first)

-- Progress may also load before the native stat component records.
local progress_first=NewPlayer()
progress_first.components.ttk_bossprogress:OnLoad(counts)
load_stats(progress_first)
progress_first.components.ttk_bossprogress:Refresh()
check(progress_first)
"""
        )

    def test_native_full_hunger_save_keeps_augmented_absolute_current(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local plain=NewPlayer()
plain.components.hunger.current=plain.components.hunger.max
assert(plain.components.hunger:OnSave()==nil)

local original=NewPlayer()
for i=1,10 do original.components.ttk_bossprogress:Absorb('spiderqueen') end
local progress_data=original.components.ttk_bossprogress:OnSave()
for _,current in ipairs({350,278,43,0}) do
 original.components.hunger.current=current
 local hunger_data=original.components.hunger:OnSave()
 assert(hunger_data~=nil and hunger_data.hunger==current,'full augmented hunger omitted')
 local restored=NewPlayer()
 restored.components.hunger:OnLoad(hunger_data)
 restored.components.ttk_bossprogress:OnLoad(progress_data)
 assert(restored.components.hunger.max==350)
 assert(restored.components.hunger.current==current,'load must preserve absolute hunger')
 restored.components.hunger.current=math.max(0,current-11)
 restored.components.ttk_bossprogress:Refresh()
 assert(restored.components.hunger.current==math.max(0,current-11),'refresh must not replay save')
end

-- Another mod may attach fields or entity references to the native record.
local refs={701,702}
local decorated={inst=original,current=333,max=350}
function decorated:OnSave() return {custom='keep'},refs end
RunComponentPostInits('hunger',decorated)
local record,saved_refs=decorated:OnSave()
assert(record.custom=='keep' and record.hunger==333 and saved_refs==refs)
"""
        )

    def test_death_state_and_prefab_transfer_preserve_progress(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local old=NewPlayer(); local progress=old.components.ttk_bossprogress
for i=1,7 do progress:Absorb('stalke_fuben') end
old.tags.playerghost=true
progress:Refresh()
old.tags.playerghost=nil
assert(progress:GetCount('stalke_fuben')==7)
assert(old.components.hh_player:GetEffectValueByKey('reduceAttackedDamage')==19)
local new=NewPlayer(); progress:TransferComponent(new)
assert(new.components.ttk_bossprogress:GetCount('stalke_fuben')==7)
assert(new.components.hh_player:GetEffectValueByKey('reduceAttackedDamage')==19)
"""
        )

    def test_food_callback_uses_actual_eater_and_all_perks_match(self):
        lua = make_lua()
        lua.execute(
            """
LoadFoodMain()
local eater=NewPlayer(); local other=NewPlayer(); ThePlayer=other
local chunk=assert(loadfile(modroot..'/scripts/prefabs/ttk_boss_cores.lua'))
local prefabs={chunk()}; local foodprefab=nil
local visuals={}
for _,prefab in ipairs(prefabs) do if prefab.name=='ttk_boss_core_jfsn' then foodprefab=prefab end end
for _,prefab in ipairs(prefabs) do
 local item=prefab.fn()
 local visual=item.AnimState.bank..'|'..item.AnimState.build..'|'..item.AnimState.animation
 assert(visuals[visual]==nil,prefab.name)
 visuals[visual]=true
end
assert(#prefabs==6)
assert(foodprefab~=nil)
local food=foodprefab.fn()
assert(food.components.edible.healthvalue==50 and food.components.edible.hungervalue==75
    and food.components.edible.sanityvalue==50)
assert(food.components.edible.foodtype==FOODTYPE.GOODIES
    and food.components.edible.secondaryfoodtype==FOODTYPE.MEAT)
food.components.edible.oneaten(food,eater)
assert(eater.components.ttk_bossprogress:GetCount('jfsn')==1)
assert(other.components.ttk_bossprogress:GetCount('jfsn')==0)
local description=food.components.inspectable.descriptionfn(food,eater)
assert(string.find(description,'1/10',1,true)~=nil)
assert(string.find(description,'+20 máu tối đa',1,true)~=nil)
assert(string.find(description,'miễn nhiễm nóng',1,true)~=nil)
local expected={jfsn='immuneHot',qlch='immuneCold',spiderqueen='immunePoison',
 stalke_fuben='immunitySleep',deerclops_ziyun='immuneFreeze'}
for suffix,effect in pairs(expected) do
 local p=NewPlayer()
 for i=1,10 do p.components.ttk_bossprogress:Absorb(suffix) end
 assert(p.components.hh_player:GetEffectValueByKey(effect)==1,suffix)
end
"""
        )

    def test_prefab_and_asset_contracts(self):
        component = MOD / "scripts" / "components" / "ttk_bossprogress.lua"
        prefab = MOD / "scripts" / "prefabs" / "ttk_boss_cores.lua"
        main = MOD / "main" / "ttk_boss_food.lua"
        self.assertTrue(component.is_file())
        self.assertTrue(prefab.is_file())
        self.assertTrue(main.is_file())
        code = prefab.read_text(encoding="utf-8")
        self.assertIn("healthvalue = 50", code)
        self.assertIn("hungervalue = 75", code)
        self.assertIn("sanityvalue = 50", code)
        self.assertNotIn("ThePlayer", code)
        self.assertNotIn("cook_pot_food", code)
        self.assertNotIn("meatballs", code)
        for phrase in (
            "+4 xuyên giáp",
            "+20 máu tối đa",
            "+20 mana tối đa",
            "+20 độ no tối đa",
            "-2 sát thương nhận vào",
            "+20 tinh thần tối đa",
        ):
            self.assertIn(phrase, code)
        for suffix in FOODS:
            stem = f"ttk_boss_core_{suffix}"
            atlas = MOD / "images" / "inventoryimages" / f"{stem}.xml"
            texture = atlas.with_suffix(".tex")
            self.assertTrue(atlas.is_file(), stem)
            self.assertTrue(texture.is_file(), stem)
            root = ET.parse(atlas).getroot()
            self.assertEqual(f"{stem}.tex", root.find("Texture").attrib["filename"])
            self.assertEqual(f"{stem}.tex", root.find("Elements/Element").attrib["name"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
