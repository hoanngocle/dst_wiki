local AchievementCatalog = require("achievement/ttk_achievement_catalog")
local PerkCatalog = require("achievement/ttk_perk_catalog")

local Core = {}
Core.__index = Core

local MAX_REPLAYS = 64
local MAX_REQUEST_ID = 96

local function IsFinite(value)
    return type(value) == "number" and value == value
        and value ~= math.huge and value ~= -math.huge
end

local function IsFiniteInteger(value)
    return IsFinite(value) and value == math.floor(value)
end

local function IsValidRequestId(request_id)
    return type(request_id) == "string" and #request_id > 0 and #request_id <= MAX_REQUEST_ID
end

local function Copy(value)
    if type(value) ~= "table" then return value end
    local copied = {}
    for key, child in pairs(value) do copied[key] = Copy(child) end
    return copied
end

local function NewResult(ok, code, extra)
    local result = { ok = ok == true, code = code }
    for key, value in pairs(extra or {}) do result[key] = value end
    return result
end

local function CanonicalAchievement(definition, saved)
    local progress = type(saved) == "table" and saved.progress or 0
    if not IsFinite(progress) or progress < 0 then progress = 0 end
    progress = math.min(definition.target, progress)
    local state = { progress = progress, status = "locked", claimed_reward = nil }
    local status = type(saved) == "table" and saved.status or nil
    if progress >= definition.target then
        state.status = status == "claimed" and "claimed" or "completed_unclaimed"
        if state.status == "claimed" then state.claimed_reward = definition.reward end
    end
    return state
end

function Core.New(inst, apply_effect)
    local self = setmetatable({}, Core)
    self.inst = inst
    self.apply_effect = apply_effect
    self.achievements = {}
    self.levels = {}
    self.unlocked = {}
    self.earned = 0
    self.spent = 0
    self.replays = {}
    self.replay_order = {}
    return self
end

function Core:GetReplay(request_id)
    return self.replays[request_id] and Copy(self.replays[request_id]) or nil
end

function Core:StoreReplay(request_id, result)
    if not IsValidRequestId(request_id) then return end
    if self.replays[request_id] == nil then table.insert(self.replay_order, request_id) end
    self.replays[request_id] = Copy(result)
    while #self.replay_order > MAX_REPLAYS do
        local dropped = table.remove(self.replay_order, 1)
        self.replays[dropped] = nil
    end
end

function Core:Balance()
    return math.max(0, self.earned - self.spent)
end

function Core:EnsureAchievement(definition)
    local state = self.achievements[definition.id]
    if state == nil then
        state = { progress = 0, status = "locked", claimed_reward = nil }
        self.achievements[definition.id] = state
    end
    return state
end

function Core:Advance(id, amount, evidence)
    local definition = AchievementCatalog.ById(id)
    if definition == nil or definition.status ~= "active" or definition.visibility ~= "visible" then
        return false, NewResult(false, "unknown_achievement")
    end
    if not IsFinite(amount) or amount <= 0 then
        return false, NewResult(false, "invalid_amount")
    end
    local state = self:EnsureAchievement(definition)
    if state.status == "claimed" then return false, NewResult(false, "already_claimed") end
    state.progress = math.min(definition.target, state.progress + amount)
    if state.progress >= definition.target then state.status = "completed_unclaimed" end
    return true, NewResult(true, state.status, { id = id, progress = state.progress })
end

function Core:ClaimAchievement(id, request_id)
    if not IsValidRequestId(request_id) then return false, NewResult(false, "invalid_request") end
    local replay = self:GetReplay(request_id)
    if replay ~= nil then return replay.ok, replay end
    local definition = AchievementCatalog.ById(id)
    if definition == nil or definition.status ~= "active" or definition.visibility ~= "visible" then
        local result = NewResult(false, "unknown_achievement")
        self:StoreReplay(request_id, result)
        return false, result
    end
    local state = self:EnsureAchievement(definition)
    if state.status ~= "completed_unclaimed" then
        local result = NewResult(false, "not_claimable")
        self:StoreReplay(request_id, result)
        return false, result
    end
    state.status = "claimed"
    state.claimed_reward = definition.reward
    self.earned = self.earned + definition.reward
    local result = NewResult(true, "claimed", { id = id, reward = definition.reward, earned = self.earned })
    self:StoreReplay(request_id, result)
    return true, result
end

function Core:Capture()
    return {
        achievements = Copy(self.achievements), levels = Copy(self.levels), unlocked = Copy(self.unlocked),
        earned = self.earned, spent = self.spent, replays = Copy(self.replays), replay_order = Copy(self.replay_order),
    }
end

function Core:Restore(snapshot)
    self.achievements = Copy(snapshot.achievements)
    self.levels = Copy(snapshot.levels)
    self.unlocked = Copy(snapshot.unlocked)
    self.earned = snapshot.earned
    self.spent = snapshot.spent
    self.replays = Copy(snapshot.replays)
    self.replay_order = Copy(snapshot.replay_order)
end

function Core:Apply(perk, level, mode)
    if self.apply_effect == nil then return true end
    local called, applied = pcall(self.apply_effect, self.inst, perk, level, mode)
    return called and applied ~= false
end

function Core:PurchasePerk(id, request_id)
    if not IsValidRequestId(request_id) then return false, NewResult(false, "invalid_request") end
    local replay = self:GetReplay(request_id)
    if replay ~= nil then return replay.ok, replay end
    local perk = PerkCatalog.ById(id)
    if perk == nil then
        local result = NewResult(false, "unknown_perk")
        self:StoreReplay(request_id, result)
        return false, result
    end
    local current_level = self.levels[id] or 0
    if perk.max_level ~= nil and current_level >= perk.max_level then
        local result = NewResult(false, "max_level")
        self:StoreReplay(request_id, result)
        return false, result
    end
    if perk.max_level == nil and self.unlocked[id] then
        local result = NewResult(false, "already_unlocked")
        self:StoreReplay(request_id, result)
        return false, result
    end
    local next_level = perk.max_level ~= nil and current_level + 1 or 1
    local price = PerkCatalog.NextPrice(perk, current_level)
    if price == nil or self:Balance() < price then
        local result = NewResult(false, "insufficient_stars")
        self:StoreReplay(request_id, result)
        return false, result
    end
    local before = self:Capture()
    if not self:Apply(perk, next_level, "purchase") then
        self:Restore(before)
        return false, NewResult(false, "apply_failed")
    end
    if perk.max_level ~= nil then self.levels[id] = next_level else self.unlocked[id] = true end
    self.spent = self.spent + price
    local result = NewResult(true, "purchased", { id = id, level = next_level, price = price, spent = self.spent })
    self:StoreReplay(request_id, result)
    return true, result
end

function Core:ReapplyPurchased()
    local applied = true
    for _, perk in ipairs(PerkCatalog.All()) do
        local level = perk.max_level ~= nil and (self.levels[perk.id] or 0) or (self.unlocked[perk.id] and 1 or 0)
        if level > 0 and not self:Apply(perk, level, "reapply") then applied = false end
    end
    return applied
end

function Core:CanonicalizePerks(saved)
    self.levels, self.unlocked, self.spent = {}, {}, 0
    saved = type(saved) == "table" and saved or {}
    local saved_levels = type(saved.levels) == "table" and saved.levels or {}
    local saved_unlocked = type(saved.unlocked) == "table" and saved.unlocked or {}
    for _, perk in ipairs(PerkCatalog.All()) do
        if perk.max_level ~= nil then
            local level = saved_levels[perk.id]
            if not IsFiniteInteger(level) or level < 0 then level = 0 end
            level = math.min(level, perk.max_level)
            for purchased = 1, level do
                local price = PerkCatalog.PriceForLevel(purchased)
                if self.earned - self.spent < price then break end
                self.levels[perk.id] = purchased
                self.spent = self.spent + price
            end
        elseif saved_unlocked[perk.id] == true and self.earned - self.spent >= perk.price then
            self.unlocked[perk.id] = true
            self.spent = self.spent + perk.price
        end
    end
end

function Core:Load(data)
    local state = type(data) == "table" and data or {}
    self.achievements, self.replays, self.replay_order = {}, {}, {}
    local saved_achievements = type(state.achievements) == "table" and state.achievements or {}
    self.earned = 0
    for _, definition in ipairs(AchievementCatalog.All()) do
        local achievement = CanonicalAchievement(definition, saved_achievements[definition.id])
        if achievement.progress > 0 or achievement.status ~= "locked" then self.achievements[definition.id] = achievement end
        if achievement.status == "claimed" then self.earned = self.earned + definition.reward end
    end
    self:CanonicalizePerks(state.perks)
    local saved_replays = type(state.replays) == "table" and state.replays or {}
    for _, entry in ipairs(saved_replays) do
        if type(entry) == "table" and IsValidRequestId(entry.id) and type(entry.result) == "table"
            and type(entry.result.ok) == "boolean" and type(entry.result.code) == "string" then
            self:StoreReplay(entry.id, entry.result)
        end
    end
    self:ReapplyPurchased()
end

function Core:GetSaveData()
    local replays = {}
    for _, request_id in ipairs(self.replay_order) do
        table.insert(replays, { id = request_id, result = Copy(self.replays[request_id]) })
    end
    return {
        version = 1, achievements = Copy(self.achievements),
        perks = { levels = Copy(self.levels), unlocked = Copy(self.unlocked) }, replays = replays,
    }
end

function Core:GetSnapshot()
    return {
        version = 1, achievements = Copy(self.achievements),
        perks = { levels = Copy(self.levels), unlocked = Copy(self.unlocked) },
        earned = self.earned, spent = self.spent, balance = self:Balance(),
    }
end

return Core
