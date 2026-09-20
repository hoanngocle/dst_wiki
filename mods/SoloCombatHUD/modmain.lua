local G = GLOBAL
if G.rawget(G, "TTK_COMBAT_HUD_OWNER") ~= nil then return end
G.SCHUD_STANDALONE_OWNER = modname
for _, key in ipairs({ "_G", "setmetatable", "rawget" }) do env[key] = G[key] end
setmetatable(env, { __index = function(_, key) return rawget(G, key) end })
G.TUNING.SCHUD = {
    BOSS_BAR = GetModConfigData("BOSS_BAR") ~= false,
    OVERHEAD_BAR = GetModConfigData("OVERHEAD_BAR") ~= false,
    HIDE_BOSS_OVERHEAD = GetModConfigData("HIDE_BOSS_OVERHEAD") ~= false,
    SHOW_VALUES = GetModConfigData("SHOW_VALUES") ~= false,
    DAMAGE_NUMBERS = GetModConfigData("DAMAGE_NUMBERS") ~= false,
    SHOW_OTHERS = GetModConfigData("SHOW_OTHERS") == true,
}

G.SCHUDCore = require("schud/epic_core")
SCHUDCore = G.SCHUDCore
modimport("scripts/util/schud_modutil.lua")
modimport("scripts/util/schud_simutil.lua")
if G.TUNING.SCHUD.BOSS_BAR then modimport("scripts/schud/epic.lua") end

if not G.TheNet:IsDedicated() and G.TUNING.SCHUD.OVERHEAD_BAR then
    AddClassPostInit("widgets/controls", function(self)
        local Bar = require("widgets/schud_overhead")
        self._schud_overhead_widgets = setmetatable({}, { __mode = "k" })
        local function eligible(parent)
            if parent == nil or G.ThePlayer == nil or parent:GetDistanceSqToInst(G.ThePlayer) > 1225 then return false end
            local x, y, z = parent.Transform:GetWorldPosition()
            local sx, sy = G.TheSim:GetScreenPos(x, y + 2.7, z)
            local width, height = G.TheSim:GetScreenSize()
            return sx ~= nil and sy ~= nil and sx >= -80 and sy >= -80 and sx <= width + 80 and sy <= height + 80
        end
        self.inst:DoPeriodicTask(0.25, function()
            local count = 0
            for proxy, widget in pairs(self._schud_overhead_widgets) do
                local parent = proxy:IsValid() and proxy.entity:GetParent() or nil
                if not proxy._visible:value() or not eligible(parent) then
                    widget:Kill()
                    self._schud_overhead_widgets[proxy] = nil
                else
                    count = count + 1
                end
            end
            for proxy in pairs(G.SCHUD_OVERHEAD_PROXIES or {}) do
                local parent = proxy.entity:GetParent()
                if count < 32 and self._schud_overhead_widgets[proxy] == nil
                    and proxy._visible:value() and eligible(parent) then
                    self._schud_overhead_widgets[proxy] = self:AddChild(Bar(proxy))
                    count = count + 1
                end
            end
        end)
    end)
end

table.insert(PrefabFiles, "schud_damage_number")
table.insert(PrefabFiles, "schud_overhead_proxy")
table.insert(Assets, Asset("ATLAS", "images/schud_overhead.xml"))
table.insert(Assets, Asset("IMAGE", "images/schud_overhead.tex"))

if G.TheNet:GetIsServer() then
    require("schud/server_damage").install(env)
end

AddClientModRPCHandler("schud", "damage", function(guid, amount, kind, x, y, z)
    if not G.TUNING.SCHUD.DAMAGE_NUMBERS then return end
    G.SCHUD_POPUPS = G.SCHUD_POPUPS or {}
    local active = G.SCHUD_POPUPS
    for i = #active, 1, -1 do if not active[i]:IsValid() then table.remove(active, i) end end
    if #active >= 32 then active[1]:Remove(); table.remove(active, 1) end
    local same_target = 0
    for _, popup in ipairs(active) do if popup._target_guid == guid then same_target = same_target + 1 end end
    local fx = G.SpawnPrefab("schud_damage_number")
    if fx ~= nil then
        fx._target_guid = guid
        fx:Display(guid, amount, kind, x + (same_target % 3 - 1) * 0.35, y, z)
        table.insert(active, fx)
    end
end)

require("schud/overhead").install(env)
