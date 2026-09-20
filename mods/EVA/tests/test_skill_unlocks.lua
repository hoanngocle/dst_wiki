local count = 0
local function eq(got, want, label)
    assert(got == want, label .. ': expected ' .. tostring(want) .. ', got ' .. tostring(got))
    count = count + 1
end
package.path = './scripts/?.lua;' .. package.path
Class = function(ctor)
    local cls = {}; cls.__index = cls
    return setmetatable(cls, {__call = function(_, ...)
        local obj = setmetatable({}, cls); ctor(obj, ...); return obj
    end})
end
TheWorld = {ismastersim = true}
local Common = require 'util/eva_scythe_array_common'
eq(Common.SOUL_COST, 100, 'ultimate cost')
eq(Common.COOLDOWN, 60, 'ultimate cooldown')
eq(Common.STRIKE_DAMAGE, 734, 'ultimate center strike')
eq(Common.BEAM_DAMAGE * Common.BEAM_PULSES + Common.STRIKE_DAMAGE, 2934, 'full ultimate base damage')
local Progression = require 'util/eva_progression'
local player = {components = {eva_souls = {level = 1, current = 1000}}}
for skill, level in pairs({fox=1, wave=1, life=10, harvest=20, wings=30, daydu=50, array=100}) do
    eq(Progression.RequiredLevel(skill), level, skill .. ' milestone')
    player.components.eva_souls.level = math.max(1, level - 1)
    if level > 1 then eq(Progression.IsUnlocked(player, skill), false, skill .. ' locked below threshold') end
    player.components.eva_souls.level = level
    eq(Progression.IsUnlocked(player, skill), true, skill .. ' unlocked at threshold')
end
-- Direct component entry points must enforce locks, including keyboard/RPC bypasses.
SpawnPrefab = function() error('locked skill spawned FX') end
for _, case in ipairs({{'eva_life','Activate',10}, {'eva_harvest','CastAt',20},
    {'eva_wings','Enable',30}, {'eva_scythe_array','CastAt',100}, {'eva_daydu','CastAt',50}}) do
    local Component = require('components/' .. case[1])
    player.components.eva_souls.level = case[3] - 1
    local c = setmetatable({inst=player, cooldown_end=0, active=false}, Component)
    local ok, reason = c[case[2]](c, 0, 0)
    eq(ok, false, case[1] .. ' direct cast rejected')
    eq(reason, 'level_locked', case[1] .. ' correct rejection')
    eq(player.components.eva_souls.current, 1000, case[1] .. ' no cost when locked')
    eq(c.cooldown_end, 0, case[1] .. ' no cooldown when locked')
end
local Wings = require 'components/eva_wings'
player.components.eva_souls.level = 29
local restored = setmetatable({inst=player, active=false}, Wings)
eq(restored:_EnableWithoutCost(), false, 'saved wings cannot bypass level gate')

-- Client never reads server components, and uses server-replicated EVA level.
TheWorld.ismastersim = false
local level = 99
local client = {eva_level = {value = function() return level end},
    components = setmetatable({}, {__index=function() error('client accessed server component') end})}
eq(Progression.IsUnlocked(client, 'array'), false, 'client ultimate locked at 99')
level = 100
eq(Progression.IsUnlocked(client, 'array'), true, 'client ultimate unlocks at 100')
local Router = require 'util/eva_skillpanel'
eq(Router.IsSkillUnlocked(client, 'array'), true, 'panel uses shared unlock rules')
level = 9
eq(Router.IsSkillUnlocked(client, 'life'), false, 'panel life lock')
assert(string.find(Router.GetSkillTooltip(client, 'life'), '10', 1, true))
assert(string.find(Router.GetSkillTooltip(client, 'array'), '100', 1, true))

-- Exercise actual panel update/click code with client-side widget doubles.
local function node()
    local n = {}
    function n:AddChild(child) return child end
    function n:SetString(value) self.text = value end
    function n:SetImageNormalColour(r) self.tint = r end
    function n:SetOnClick(fn) self.onclick = fn end
    function n:Show() self.visible = true end
    function n:Hide() self.visible = false end
    function n:SetPosition(x, y) self.x = x; self.y = y end
    n.SetColour = function() end
    n.ForceImageSize = function() end
    n.StartUpdating = function() end
    return n
end
local Widget = {_ctor = function() end}
package.preload['widgets/widget'] = function()
    return setmetatable(Widget, {__call = function() return node() end})
end
package.preload['widgets/imagebutton'] = function() return node end
package.preload['widgets/text'] = function() return node end
Class = function(base, ctor)
    local c = {}; c.__index = c
    return setmetatable(c, {__call = function(_, ...)
        local obj = setmetatable(node(), c); ctor(obj, ...); return obj
    end})
end
GetInventoryItemAtlas = function() return 'images/inventoryimages.xml' end
client.prefab = 'eva'
client.IsValid = function() return true end
client.HasTag = function(_, tag) return tag == 'eva' end
TheFrontEnd = {IsControlsDisabled = function() return false end,
    GetActiveScreen = function() return {name='HUD'} end}
local WidgetClass = require 'widgets/eva_skillpanel'
local panel = WidgetClass(client)
panel:OnUpdate()
eq(panel.icons.life.state.text, 'Cấp 10', 'locked life icon displays milestone')
eq(panel.icons.life.tint, 0.38, 'locked icon is dimmed')
client._eva_skillbook = {value = function() error('locked click reached spellbook') end}
panel:ActivateSkill(1, 'life')
level = 10; panel:OnUpdate()
eq(panel.icons.life.tint, 1, 'life icon becomes active at level 10')
eq(panel.icons.life.state.text, '', 'unlocked life clears requirement label')
eq(panel.icons.array.state.text, 'Cấp 100', 'ultimate still locked at level 10')
level = 100; panel:OnUpdate()
eq(panel.icons.array.tint, 1, 'ultimate icon becomes active at level 100')
eq(panel.expanded, false, 'panel starts collapsed')
eq(panel.icons.life.visible, false, 'skills hidden while collapsed')
panel.collapse.onclick()
eq(panel.expanded, true, 'toggle expands panel')
local ordered = {'life','harvest','wings','daydu','array'}
local previous = panel.collapse.x
local expected_index = {life=1,wings=2,array=3,harvest=4,daydu=5}
client._eva_skillbook = {value = function() error('unexpected book access in layout test') end}
local selected = {}
panel.ActivateSkill = function(_, index, skill) selected[skill] = index end
for _, skill in ipairs(ordered) do
    eq(panel.icons[skill].visible, true, skill .. ' visible on expand')
    assert(panel.icons[skill].x > previous, 'visual order must ascend from left to right')
    previous = panel.icons[skill].x
    panel.icons[skill].onclick()
    eq(selected[skill], expected_index[skill], skill .. ' preserved native spell index')
    eq(Router.SKILLS[skill].atlas, 'images/eva_skill_icons.xml', skill .. ' correct atlas')
end
panel.collapse.onclick()
eq(panel.expanded, false, 'second click collapses panel')
for _, skill in ipairs(ordered) do eq(panel.icons[skill].visible, false, skill .. ' collapsed') end
eq(Router.SKILLS.array.label, 'Trảm Linh', 'short array name')
eq(Router.SKILLS.daydu.label, 'Dạ Du', 'short daydu name')
print('PASS: ' .. count .. ' skill unlock/ultimate assertions')
