local AchievementCatalog = require("achievement/ttk_achievement_catalog")
local PerkCatalog = require("achievement/ttk_perk_catalog")
local Core = require("achievement/ttk_achievement_core")

local MAX_SNAPSHOT_BYTES = 16384

local function StatusCode(status)
    return status == "claimed" and "c" or status == "completed_unclaimed" and "u" or "l"
end

local function SerializeSnapshot(snapshot)
    local achievements, perks = {}, {}
    for _, definition in ipairs(AchievementCatalog.All()) do
        local state = snapshot.achievements[definition.id]
        if state ~= nil then
            table.insert(achievements, definition.id .. ":" .. tostring(state.progress) .. ":" .. StatusCode(state.status))
        end
    end
    for _, perk in ipairs(PerkCatalog.All()) do
        local level = perk.max_level ~= nil and (snapshot.perks.levels[perk.id] or 0)
            or (snapshot.perks.unlocked[perk.id] and 1 or 0)
        if level > 0 then table.insert(perks, perk.id .. ":" .. tostring(level)) end
    end
    local encoded = table.concat({
        "v1", "e" .. tostring(snapshot.earned), "s" .. tostring(snapshot.spent),
        "a" .. table.concat(achievements, ","), "p" .. table.concat(perks, ","),
    }, ";")
    return #encoded <= MAX_SNAPSHOT_BYTES and encoded or "v1;e0;s0;a;p"
end

local function CopyScalarTree(value, depth, budget)
    if budget.count <= 0 or depth > 4 then return nil end
    local kind = type(value)
    if kind == "string" then
        if #value > 128 then return nil end
        budget.count = budget.count - 1
        return value
    end
    if kind == "boolean" then budget.count = budget.count - 1; return value end
    if kind == "number" and value == value and value ~= math.huge and value ~= -math.huge then
        budget.count = budget.count - 1
        return value
    end
    if kind ~= "table" then return nil end
    local copy = {}
    for key, child in pairs(value) do
        if type(key) == "string" and #key <= 64 then
            local copied = CopyScalarTree(child, depth + 1, budget)
            if copied ~= nil then copy[key] = copied end
        end
    end
    return copy
end

local TtkAchievementProgress = Class(function(self, inst)
    self.inst = inst
    self.version = 1
    self.effect_callback = nil
    self.cultivation_reference = {}
    self.seasonal_state = {}
    self.core = Core.New(inst, function(_, perk, level, mode)
        return self:ApplyPerk(perk, level, mode)
    end)
    inst:ListenForEvent("ms_respawnedfromghost", function() self:ReapplyPurchased() end)
    inst:ListenForEvent("ms_playeractivated", function() self:ReapplyPurchased() end)
end)

function TtkAchievementProgress:SetEffectCallback(callback)
    self.effect_callback = type(callback) == "function" and callback or nil
end

function TtkAchievementProgress:ApplyPerk(perk, level, mode)
    if self.effect_callback == nil then return true end
    return self.effect_callback(self.inst, perk, level, mode)
end

function TtkAchievementProgress:PushSnapshot()
    local encoded = SerializeSnapshot(self.core:GetSnapshot())
    self.snapshot = encoded
    self.inst:PushEvent("ttk_achievement_dirty", encoded)
    return encoded
end

function TtkAchievementProgress:Advance(id, amount, evidence)
    local ok, result = self.core:Advance(id, amount, evidence)
    if ok then self:PushSnapshot() end
    return ok, result
end

function TtkAchievementProgress:ClaimAchievement(id, request_id)
    local ok, result = self.core:ClaimAchievement(id, request_id)
    if type(request_id) == "string" and #request_id > 0 then self:PushSnapshot() end
    return ok, result
end

function TtkAchievementProgress:PurchasePerk(id, request_id)
    local ok, result = self.core:PurchasePerk(id, request_id)
    if type(request_id) == "string" and #request_id > 0 then self:PushSnapshot() end
    return ok, result
end

function TtkAchievementProgress:GetSnapshot()
    return self.core:GetSnapshot()
end

function TtkAchievementProgress:ReapplyPurchased()
    self.core:ReapplyPurchased()
    self:PushSnapshot()
end

function TtkAchievementProgress:SetCultivationReference(snapshot)
    self.cultivation_reference = CopyScalarTree(snapshot, 0, { count = 96 }) or {}
end

function TtkAchievementProgress:SetSeasonalState(snapshot)
    self.seasonal_state = CopyScalarTree(snapshot, 0, { count = 256 }) or {}
end

function TtkAchievementProgress:OnSave()
    local state = self.core:GetSaveData()
    state.version = self.version
    state.cultivation = CopyScalarTree(self.cultivation_reference, 0, { count = 96 }) or {}
    state.seasonal = CopyScalarTree(self.seasonal_state, 0, { count = 256 }) or {}
    return state
end

function TtkAchievementProgress:OnLoad(data)
    local state = type(data) == "table" and data or {}
    self.cultivation_reference = CopyScalarTree(state.cultivation, 0, { count = 96 }) or {}
    self.seasonal_state = CopyScalarTree(state.seasonal, 0, { count = 256 }) or {}
    self.core:Load(state)
    self:PushSnapshot()
end

return TtkAchievementProgress
