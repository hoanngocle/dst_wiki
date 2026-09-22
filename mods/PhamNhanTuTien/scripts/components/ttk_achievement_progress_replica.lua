local PerkCatalog = require("achievement/ttk_perk_catalog")

local MAX_SNAPSHOT_BYTES = 16384

local function Copy(value)
    if type(value) ~= "table" then return value end
    local copied = {}
    for key, child in pairs(value) do copied[key] = Copy(child) end
    return copied
end

local function Split(value, separator)
    local parts = {}
    for part in string.gmatch(value, "([^" .. separator .. "]*)") do
        table.insert(parts, part)
        if #parts > 4096 then return nil end
    end
    return parts
end

local function NonNegativeInteger(value)
    local number = tonumber(value)
    return number ~= nil and number == math.floor(number) and number >= 0 and number or nil
end

local function CanonicalNumber(value)
    if type(value) ~= "string" or not string.match(value, "^%d[%d%.eE%+%-]*$") then return nil end
    local number = tonumber(value)
    return number ~= nil and number == number and number ~= math.huge and number ~= -math.huge and number >= 0 and number or nil
end

local function DecodeSnapshot(encoded)
    if type(encoded) ~= "string" or #encoded == 0 or #encoded > MAX_SNAPSHOT_BYTES then return nil end
    local sections = {}
    for part in string.gmatch(encoded, "[^;]+") do
        local key, value = string.match(part, "^([vesap])(.*)$")
        if key == nil or sections[key] ~= nil then return nil end
        sections[key] = value
    end
    if sections.v ~= "1" then return nil end
    local earned, spent = NonNegativeInteger(sections.e), NonNegativeInteger(sections.s)
    if earned == nil or spent == nil or spent > earned or sections.a == nil or sections.p == nil then return nil end
    local snapshot = { version = 1, earned = earned, spent = spent, balance = earned - spent, achievements = {}, perks = { levels = {}, unlocked = {} } }
    for entry in string.gmatch(sections.a, "[^,]+") do
        local id, progress, status = string.match(entry, "^([a-z][a-z0-9_]*):([^:]+):([luc])$")
        progress = CanonicalNumber(progress)
        if id == nil or progress == nil or snapshot.achievements[id] ~= nil then return nil end
        snapshot.achievements[id] = { progress = progress, status = status == "c" and "claimed" or status == "u" and "completed_unclaimed" or "locked" }
    end
    for entry in string.gmatch(sections.p, "[^,]+") do
        local id, level = string.match(entry, "^([a-z][a-z0-9_]*):(%d+)$")
        level = NonNegativeInteger(level)
        local perk = id ~= nil and PerkCatalog.ById(id) or nil
        if perk == nil or level == nil or level == 0 then return nil end
        if perk.max_level ~= nil then
            if level > perk.max_level or snapshot.perks.levels[id] ~= nil then return nil end
            snapshot.perks.levels[id] = level
        else
            if level ~= 1 or snapshot.perks.unlocked[id] ~= nil then return nil end
            snapshot.perks.unlocked[id] = true
        end
    end
    return snapshot
end

local TtkAchievementProgressReplica = Class(function(self, inst)
    self.inst = inst
    self.snapshot = { version = 1, earned = 0, spent = 0, balance = 0, achievements = {}, perks = { levels = {}, unlocked = {} } }
    inst:ListenForEvent("ttk_achievement_dirty", function(_, encoded) self:SetSnapshot(encoded) end)
end)

function TtkAchievementProgressReplica:SetSnapshot(encoded)
    local decoded = DecodeSnapshot(encoded)
    if decoded == nil then return false end
    self.snapshot = decoded
    return true
end

function TtkAchievementProgressReplica:GetSnapshot()
    return Copy(self.snapshot)
end

return TtkAchievementProgressReplica
