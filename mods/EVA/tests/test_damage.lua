-- Engine rendering/network calls are stubbed; the real scythe prefab and Solo
-- damage buff run below. Assertions cover EVA's ordinary-weapon contract.
package.path = './scripts/?.lua;../mod_steam/3780347550/scripts/?.lua;' .. package.path

local count = 0
local function eq(actual, expected, label)
    assert(actual == expected, label .. ': expected ' .. tostring(expected) .. ', got ' .. tostring(actual))
    count = count + 1
end

local noop = function() end
local visual = setmetatable({}, {__index = function() return noop end})

TUNING = {
    EVA_SCYTHE_DMG = 50,
    EVA_SCYTHE_DURABILITY = 100,
}
TheWorld = {ismastersim = true}
Asset = noop
MakeInventoryPhysics = noop
MakeInventoryFloatable = noop
MakeHauntableLaunch = noop
Prefab = function(name, fn) return {name = name, fn = fn} end
Class = function() return {} end

function CreateEntity()
    local inst = {
        entity = visual,
        AnimState = visual,
        MiniMapEntity = visual,
        components = {},
        tags = {},
        prefab = 'eva_scythe',
    }
    function inst:AddTag(tag) self.tags[tag] = true end
    inst.Remove = noop
    function inst:AddComponent(name)
        local component = {}
        if name == 'weapon' then
            function component:SetDamage(value) self.damage = value end
            function component:GetDamage() return self.damage, self.special end
            function component:CanRangedAttack() return false end
            function component:SetOnAttack(fn) self.onattack = fn end
        elseif name == 'finiteuses' then
            function component:SetMaxUses(value) self.max = value end
            function component:SetUses(value) self.uses = value end
            function component:SetOnFinished(fn) self.onfinished = fn end
        elseif name == 'equippable' then
            function component:SetOnEquip(fn) self.onequip = fn end
            function component:SetOnUnequip(fn) self.onunequip = fn end
        end
        self.components[name] = component
        return component
    end
    return inst
end

local prefab = dofile('scripts/prefabs/eva_scythe.lua')

TheWorld.ismastersim = false
local client_scythe = prefab.fn()
eq(client_scythe.components.weapon, nil, 'remote client has no weapon component')
eq(client_scythe.components.finiteuses, nil, 'remote client has no durability component')
TheWorld.ismastersim = true

local scythe = prefab.fn()
local weapon = scythe.components.weapon

eq(prefab.name, 'common/inventory/eva_scythe', 'save-compatible prefab name')
eq(weapon.damage, 50, 'configured base damage')
eq(scythe.components.finiteuses.max, 100, 'configured maximum durability')
eq(scythe.components.finiteuses.uses, 100, 'configured starting durability')
eq(scythe.components.reticule, nil, 'no targeting reticule')
eq(scythe.components.spellcaster, nil, 'no Soul Strike spellcaster')
eq(weapon.onattack, nil, 'no critical or proc attack callback')
eq(scythe.spelltype, nil, 'no Soul Strike action label')

local range_changes = 0
local owner = {
    AnimState = visual,
    components = {
        combat = {
            SetRange = function()
                range_changes = range_changes + 1
            end,
        },
    },
}
scythe.components.equippable.onequip(scythe, owner)
scythe.components.equippable.onunequip(scythe, owner)
eq(range_changes, 0, 'equip and unequip do not alter attack reach')
eq(scythe.components.equippable.dapperness, nil, 'equip does not drain sanity')

-- Use the actual Solo buff implementation: it may adjust configured base
-- damage, while EVA adds no crit multiplier or resource mechanic.
local buff = require('components/wb_strengthen').BUFFS_CONFIG.damage
scythe.components.wb_strengthen = {do_mode = 'strengthen'}
local status = {}
buff.bind_fn(scythe, 6, status, buff) -- base 50 + 16 = 66
eq(weapon.damage, 66, 'Solo +6 base')
eq(weapon:GetDamage(owner, {}), 66, 'Solo-enhanced hit remains ordinary damage')
eq(status.original_damage, 50, 'Solo remembers configured base')

buff.update_fn(scythe, 8, status, buff)
eq(weapon.damage, 82, 'changing enhancement level')
eq(weapon:GetDamage(owner, {}), 82, 'updated enhancement remains ordinary damage')

weapon.special = {planar = 7}
local damage, special = weapon:GetDamage(owner, {})
eq(damage, 82, 'special damage keeps physical base')
eq(special.planar, 7, 'special damage return is preserved')

buff.unbind_fn(scythe, 8, status, buff)
scythe.components.wb_strengthen = nil
eq(weapon.damage, 50, 'removing enhancement restores configured base')
eq(prefab.fn().components.weapon.damage, 50, 'new instance starts from configured base')

print('PASS: ' .. count .. ' normal-scythe assertions (real Solo buff + prefab)')
