-- Phàm Nhân Tu Tiên: authoritative evidence adapters and perk installation.
local G = GLOBAL
if rawget(env, "_ttk_achievement_registered") then return end
rawset(env, "_ttk_achievement_registered", true)
AddReplicableComponent("ttk_achievement_progress")

local AchievementCatalog = require("achievement/ttk_achievement_catalog")
local SeasonalCatalog = require("achievement/ttk_seasonal_catalog")
local PerkCatalog = require("achievement/ttk_perk_catalog")
local PerkEffects = require("achievement/ttk_perk_effects")
local RankDefs = require("guild/hh_rank_defs")
local AlchemyDefs = require("alchemy/ttk_alchemy_defs")
local CHEST_MILESTONES = { 5, 10, 15, 20 }

local function Master()
    return G.TheWorld ~= nil and G.TheWorld.ismastersim == true
end

local function Integer(value, minimum, maximum)
    return type(value) == "number" and value == value and value >= minimum
        and value <= maximum and value == math.floor(value)
end

local function ValidID(id)
    return type(id) == "string" and #id > 0 and #id <= 80 and id:match("^[%w_]+$") ~= nil
end

local function ValidRequest(request_id)
    return type(request_id) == "string" and #request_id > 0 and #request_id <= 96
end

local function ResolveSender(sender)
    if not Master() or sender == nil or not sender:IsValid() or not sender:HasTag("player")
        or sender.components == nil then return nil end
    local component = sender.components.ttk_achievement_progress
    if component == nil or component.inst ~= sender then return nil end
    return component
end

local function Matches(params, evidence)
    for key, value in pairs(params) do
        if key == "prefabs" then
            local found = false
            for _, prefab in ipairs(value) do
                if evidence.prefab == prefab then found = true; break end
            end
            if not found then return false end
        elseif key == "level" or key == "milestone" then
            if type(evidence[key]) ~= "number" or evidence[key] < value then return false end
        elseif key == "rank" then
            if RankDefs.RANK[evidence.rank] == nil or RankDefs.RANK[value] == nil
                or RankDefs.RANK[evidence.rank] < RankDefs.RANK[value] then return false end
        elseif evidence[key] ~= value then
            return false
        end
    end
    return true
end

local function AdvanceTo(component, row, value, evidence)
    local saved = component.core.achievements[row.id]
    local progress = saved ~= nil and saved.progress or 0
    local desired = math.min(row.target, value)
    if desired > progress then component:Advance(row.id, desired - progress, evidence) end
end

local function Route(inst, tracker, evidence, amount, absolute)
    local component = ResolveSender(inst)
    if component == nil then return end
    for _, row in ipairs(AchievementCatalog.ByEvent(tracker)) do
        if row.id ~= "food_cultivation_pill_path" and Matches(row.params, evidence) then
            if absolute then
                AdvanceTo(component, row, row.target, evidence)
            else
                local saved = component.core.achievements[row.id]
                if saved == nil or saved.progress < row.target then component:Advance(row.id, amount or 1, evidence) end
            end
        end
    end
end

local function Seasonal(inst, event, evidence, amount)
    local component = ResolveSender(inst)
    local seasonal = component ~= nil and component.core.seasonal or nil
    if seasonal == nil or seasonal.season ~= G.TheWorld.state.season then return end
    evidence.event = event
    for _, slot in ipairs(seasonal.slots) do
        local row = SeasonalCatalog.ById(slot.task_id)
        if row ~= nil and row.event == event and Matches(row.params, evidence)
            and slot.progress < row.target and slot.claims < row.max_claims then
            component:AdvanceSeasonal(row.id, amount, evidence)
        end
    end
end

local function Seen(state, kind, identity)
    if type(identity) ~= "table" then return true end
    state[kind] = state[kind] or setmetatable({}, { __mode = "k" })
    if state[kind][identity] then return true end
    state[kind][identity] = true
    return false
end

-- DST components/eater.lua emits oneat before OnEaten/HandleEatRemove.
-- One context per Eat call permits successive units of the same stack while
-- duplicate oneat callbacks cannot credit the same consumption twice.
local function OnEat(inst, data)
    local context = inst._ttk_achievement_eating
    if context == nil or data == nil or data.food ~= context.food or context.observed then return end
    context.observed = true
end

local function InstallEater(eater)
    if not Master() or eater._ttk_achievement_hook then return end
    eater._ttk_achievement_hook = true
    local previous = eater.Eat
    eater.Eat = function(self, food, ...)
        local inst = self.inst
        if ResolveSender(inst) == nil or food == nil then return previous(self, food, ...) end
        local hunger = inst.components.hunger
        local context = { food=food, prefab=food.prefab, starving=hunger ~= nil and hunger:IsStarving() }
        local outer = inst._ttk_achievement_eating
        inst._ttk_achievement_eating = context
        local ok, result = pcall(previous, self, food, ...)
        inst._ttk_achievement_eating = outer
        if not ok then error(result) end
        if result == true and context.observed then
            local evidence = { prefab=context.prefab, starving=context.starving }
            Route(inst, "eat_prefabs", evidence, 1)
            Seasonal(inst, "oneat", evidence, 1)
        end
        return result
    end
end

-- ttk_cultivation:Consume commits stage and consumed before this event.
-- Use the committed prefix, including saved progress, never the event payload.
local function OnCultivation(inst)
    local component = ResolveSender(inst)
    local cultivation = inst.components.ttk_cultivation
    if component == nil or cultivation == nil then return end
    local stage = cultivation:GetStage()
    if not Integer(stage, 1, 15) then return end
    for index = 1, stage do
        local row = AlchemyDefs.GetCultivationStage(index)
        if row == nil or not cultivation.consumed[row.prefab] then return end
    end
    local id = "food_cultivation_pill_path"
    local saved = component.core.achievements[id]
    local progress = saved ~= nil and saved.progress or 0
    if stage > progress then component:Advance(id, stage - progress, { stage=stage }) end
    component:SetCultivationReference(cultivation:OnSave())
end

local function OnProgression(inst)
    local leveling, rank = inst.components.hh_leveling, inst.components.hh_rank
    if leveling ~= nil and Integer(leveling.level, 1, 1000000000) then
        Route(inst, "level_reached", { level=leveling.level }, 1, true)
    end
    if rank ~= nil and RankDefs.IsValidRank(rank:GetRank()) then
        Route(inst, "hunter_rank", { rank=RankDefs.GetName(rank:GetRank()) }, 1, true)
    end
end

-- combat.lua pushes killed on the actual attacker after health reaches zero.
-- Existing Phàm Nhân direct-kill producers (ttk_boss_swordfx.lua) omit attacker;
-- the server event source still identifies the credited killer in that case.
-- Follower events may credit only their current leader; victim identity is
-- shared with direct kills so a pet-forwarded callback cannot award twice.
local function OnKilled(killer, data)
    if not Master() or data == nil or (data.attacker ~= nil and data.attacker ~= killer) then return end
    local inst = killer
    if ResolveSender(inst) == nil then
        local follower = killer.components ~= nil and killer.components.follower or nil
        inst = follower ~= nil and follower:GetLeader() or nil
    end
    if ResolveSender(inst) == nil then return end
    local victim = data.victim
    if victim == nil or victim.components == nil or victim.components.health == nil
        or not victim.components.health:IsDead() then return end
    local state = inst._ttk_achievement_state
    if state == nil or state.kills[victim] then return end
    state.kills[victim] = true
    local evidence = { prefab=victim.prefab }
    Route(inst, "kill_prefab", evidence, 1)
    Route(inst, "combat_event", evidence, 1)
    Seasonal(inst, "killed", evidence, 1)
end

local function ConfigureXP(inst, component)
    -- EXP calibration belongs to the separate tuning task. Only an explicit
    -- server tuning value enables claims; no default is invented here. Until
    -- configured, Core keeps its nil callback and reports xp_unavailable.
    local SEASONAL_CLAIM_XP = G.TUNING and G.TUNING.TTK_SEASONAL_CLAIM_XP
    if type(SEASONAL_CLAIM_XP) ~= "number" or SEASONAL_CLAIM_XP ~= SEASONAL_CLAIM_XP
        or SEASONAL_CLAIM_XP <= 0 or SEASONAL_CLAIM_XP == math.huge then return end
    local awarded = {}
    component:SetSeasonalXPCallback(function(player, id, kind, number, claim_key)
        if not Master() or player ~= inst or ResolveSender(inst) ~= component then return false end
        local row = SeasonalCatalog.ById(id)
        local seasonal = component.core.seasonal
        local slot = component.core:FindSeasonalSlot(id)
        if row == nil or row.kind ~= kind or seasonal == nil or slot == nil
            or seasonal.season ~= G.TheWorld.state.season or row.season ~= seasonal.season
            or not Integer(number, 1, row.max_claims) then return false end
        local expected = seasonal.epoch .. ":" .. id .. ":" .. tostring(number)
        if claim_key ~= expected then return false end
        if awarded[claim_key] == true then return true end
        if awarded[claim_key] ~= nil or number ~= slot.claims + 1 or slot.progress < row.target then return false end
        local leveling = inst.components.hh_leveling
        if leveling == nil or SEASONAL_CLAIM_XP <= 0 then return false end
        -- Reserve before callbacks. If AddExp throws after changing EXP, retain
        -- the reservation (fail closed) rather than retrying an uncertain award.
        awarded[claim_key] = "pending"
        local ok = leveling:AddExp(SEASONAL_CLAIM_XP)
        awarded[claim_key] = ok == true and true or nil
        return ok == true
    end)
end

local function RefreshSeason(inst)
    local component = ResolveSender(inst)
    if component == nil then return end
    local state = G.TheWorld.state
    if state == nil or not SeasonalCatalog.IsSeason(state.season)
        or not Integer(state.cycles, 0, 1000000000)
        or not Integer(state.elapseddaysinseason, 0, 1000000000) then return end
    -- worldstate receives elapsed days from seasons:OnSeasonDirty. Defer the
    -- season watcher to let that event finish updating all world-state fields.
    local start_cycle = math.max(0, state.cycles - state.elapseddaysinseason)
    local epoch = state.season .. ":" .. tostring(start_cycle)
    local saved = component.core.seasonal
    if saved ~= nil and saved.season == state.season and saved.epoch == epoch then return end
    if component:StartSeason(state.season, epoch) then
        Route(inst, "season_mission_assigned", { source="seasonal" }, 1)
    end
end

-- Inventory:GiveItem emits itemget only for a new slot. Stackable:Put instead
-- emits stacksizechange, and Stackable:Get replaces split units with a new
-- entity. Track receipts per player/unit, carrying them through both operations;
-- fresh event tables, bag transfers, and stack splits are not new acquisitions.
local inventory_depth = 0
local pending_inventory = setmetatable({}, { __mode="k" })

local function ItemAmount(item)
    local stack = item.components ~= nil and item.components.stackable or nil
    local amount = stack ~= nil and stack:StackSize() or 1
    return Integer(amount, 1, 1000000) and amount or 0
end

local function Receipts(item, amount)
    local receipts = item._ttk_achievement_receipts
    if receipts == nil then
        receipts = setmetatable({}, { __mode="k" })
        item._ttk_achievement_receipts = receipts
    end
    for player, count in pairs(receipts) do receipts[player] = math.min(count, amount) end
    return receipts
end

local function CopyReceipts(item, amount)
    local copy = {}
    for player, count in pairs(Receipts(item, amount)) do copy[player] = count end
    return copy
end

local function CreditInventoryItem(item)
    if item == nil or not item:IsValid() or item.components == nil then return end
    if inventory_depth > 0 then pending_inventory[item] = true; return end
    local inventoryitem = item.components.inventoryitem
    local player = inventoryitem ~= nil and inventoryitem:GetGrandOwner() or nil
    if ResolveSender(player) == nil then return end
    local amount = ItemAmount(item)
    local receipts = Receipts(item, amount)
    local credited = receipts[player] or 0
    receipts[player] = amount -- Commit before Route can invoke other callbacks.
    local inventory = player.components.inventory
    if amount > credited and inventory ~= nil and not inventory.isloading then
        local evidence = { prefab=item.prefab }
        Route(player, "collect_prefab", evidence, amount - credited)
        Route(player, "collect_prefabs", evidence, amount - credited)
        Seasonal(player, "itemget", evidence, amount - credited)
    end
    -- Restored backpack contents get a baseline while Inventory:OnLoad still
    -- has isloading=true; equipping/moving a bag must not collect its contents.
    local container = item.components.container
    if container ~= nil then
        for _, child in pairs(container.slots) do CreditInventoryItem(child) end
    end
end

local function FlushInventory()
    if inventory_depth > 0 then return end
    local pending = pending_inventory
    pending_inventory = setmetatable({}, { __mode="k" })
    for item in pairs(pending) do CreditInventoryItem(item) end
end

local function OnBuild(inst, data, event)
    local state = inst._ttk_achievement_state
    if data == nil or data.item == nil or Seen(state, "builds", data.item) then return end
    local evidence = { prefab=data.item.prefab }
    Route(inst, "crafting_event", evidence, 1)
    Route(inst, "craft_prefab", evidence, 1)
    Seasonal(inst, event, evidence, 1)
end

local function InstallPlayer(inst)
    if not Master() or inst._ttk_achievement_installed then return end
    inst._ttk_achievement_installed = true
    if inst.components.ttk_achievement_progress == nil then inst:AddComponent("ttk_achievement_progress") end
    local component = inst.components.ttk_achievement_progress
    PerkEffects.Install(inst)
    component:SetEffectCallback(PerkEffects.Apply)
    component:ReapplyPurchased()
    local state = { kills=setmetatable({}, { __mode="k" }), dead=false }
    inst._ttk_achievement_state = state
    ConfigureXP(inst, component)
    if inst.components.eater ~= nil then InstallEater(inst.components.eater) end
    inst:ListenForEvent("ttk_cultivation_advanced", OnCultivation)
    inst:ListenForEvent("hh_levelup", OnProgression)
    inst:ListenForEvent("hh_rank_changed", OnProgression)
    inst:ListenForEvent("oneat", OnEat)
    inst:ListenForEvent("killed", OnKilled)
    inst:ListenForEvent("builditem", function(player, data) OnBuild(player, data, "builditem") end)
    inst:ListenForEvent("buildstructure", function(player, data) OnBuild(player, data, "buildstructure") end)
    inst:ListenForEvent("finishedwork", function(player, data)
        if data == nil or data.target == nil or data.action == nil or Seen(state, "work", data) then return end
        local evidence = { prefab=data.target.prefab, action=data.action.id }
        Route(player, "work_action", evidence, 1)
        Seasonal(player, "finishedwork", evidence, 1)
    end)
    inst:ListenForEvent("picksomething", function(player, data)
        if data == nil or data.object == nil or Seen(state, "picks", data) then return end
        local evidence = { prefab=data.object.prefab }
        Seasonal(player, "picksomething", evidence, 1)
        if data.object:HasTag("farm_plant") then
            Route(player, "harvest_crop", { source="farm", action="HARVEST" }, 1)
        end
    end)
    inst:ListenForEvent("itemget", function(player, data)
        if data ~= nil then CreditInventoryItem(data.item) end
    end)
    -- farmtiller.lua and oar.lua emit these only after the successful action.
    inst:ListenForEvent("tilling", function(player)
        Route(player, "farm_action", { action="TILL" }, 1)
        Seasonal(player, "tilling", { action="TILL" }, 1)
    end)
    inst:ListenForEvent("rowing", function(player) Seasonal(player, "rowing", { action="ROW" }, 1) end)
    inst:ListenForEvent("death", function(player)
        if state.dead or player.components.health == nil or not player.components.health:IsDead() then return end
        state.dead = true
    end)
    inst:ListenForEvent("ms_respawnedfromghost", function(player)
        if not state.dead then return end
        state.dead = false
        Route(player, "survival_event", { key="revive" }, 1)
    end)
    inst:WatchWorldState("season", function(player)
        player:DoTaskInTime(0, RefreshSeason)
    end)
    inst:DoTaskInTime(0, function(player)
        RefreshSeason(player)
        OnCultivation(player)
        OnProgression(player)
    end)
end

AddPlayerPostInit(function(inst)
    inst._ttk_achievement_rpc_namespace = modname
    inst._ttk_achievement_snapshot = G.net_string(inst.GUID, "ttk.achievement.snapshot", "ttk_achievement_netdirty")
    InstallPlayer(inst)
end)
modimport("main/ttk_achievement_perks.lua")
AddComponentPostInit("eater", InstallEater)
AddComponentPostInit("inventoryitem", function(self)
    if not Master() or self._ttk_achievement_hook then return end
    self._ttk_achievement_hook = true
    self.inst:ListenForEvent("onputininventory", function(item) CreditInventoryItem(item) end)
end)
AddComponentPostInit("stackable", function(self)
    if not Master() or self._ttk_achievement_hook then return end
    self._ttk_achievement_hook = true
    self.inst:ListenForEvent("stacksizechange", function(item) CreditInventoryItem(item) end)
    local previous_get, previous_put = self.Get, self.Put
    self.Get = function(stack, ...)
        local before = CopyReceipts(stack.inst, ItemAmount(stack.inst))
        inventory_depth = inventory_depth + 1
        local ok, child = pcall(previous_get, stack, ...)
        if ok and child ~= nil and child ~= stack.inst then
            local size = ItemAmount(child)
            local original, split = Receipts(stack.inst, ItemAmount(stack.inst)), Receipts(child, size)
            for player, count in pairs(before) do
                local moved = math.min(count, size)
                original[player], split[player] = count - moved, moved
            end
            pending_inventory[child] = true
        end
        inventory_depth = inventory_depth - 1
        FlushInventory()
        if not ok then error(child) end
        return child
    end
    self.Put = function(stack, item, ...)
        local oldsize = ItemAmount(stack.inst)
        local destination, donor = CopyReceipts(stack.inst, oldsize), CopyReceipts(item, ItemAmount(item))
        inventory_depth = inventory_depth + 1
        local ok, leftovers = pcall(previous_put, stack, item, ...)
        if ok then
            local moved = math.max(0, ItemAmount(stack.inst) - oldsize)
            local received = Receipts(stack.inst, ItemAmount(stack.inst))
            local remaining = Receipts(item, item:IsValid() and ItemAmount(item) or 0)
            for player, count in pairs(donor) do
                local carried = math.min(count, moved)
                received[player] = (destination[player] or 0) + carried
                remaining[player] = count - carried
            end
            pending_inventory[stack.inst] = true
        end
        inventory_depth = inventory_depth - 1
        FlushInventory()
        if not ok then error(leftovers) end
        return leftovers
    end
end)
AddComponentPostInit("follower", function(self)
    if not Master() or self._ttk_achievement_hook then return end
    self._ttk_achievement_hook = true
    self.inst:ListenForEvent("killed", OnKilled)
end)
-- deployable.lua's event contains only a prefab string. Capture the real item
-- before Deploy removes it, then route only its successful return value.
AddComponentPostInit("deployable", function(self)
    if not Master() or self._ttk_achievement_hook then return end
    self._ttk_achievement_hook = true
    local previous = self.Deploy
    self.Deploy = function(deployable, pt, deployer, ...)
        local prefab = deployable.inst.prefab
        local fertilizer = deployable.inst.components.fertilizer
        local nutrients = fertilizer ~= nil and fertilizer.nutrients ~= nil
            and { fertilizer.nutrients[1], fertilizer.nutrients[2], fertilizer.nutrients[3] } or nil
        local ok, reason = previous(deployable, pt, deployer, ...)
        if ok == true and ResolveSender(deployer) ~= nil then
            PerkEffects.ApplyFertilizer(deployer, pt, nutrients)
            Seasonal(deployer, "deployitem", { action="DEPLOY", prefab=prefab }, 1)
        end
        return ok, reason
    end
end)

-- RPC boundary: register names on both peers so DST assigns matching RPC IDs;
-- every handler resolves only the engine-provided sender on the master server.
-- Core methods preserve replay records; publish only on success, avoiding the
-- older component ClaimAchievement/PurchasePerk wrappers' failure snapshots.
AddModRPCHandler(modname, "AchievementClaim", function(sender, id, request_id, ...)
    if select("#", ...) ~= 0 or not ValidID(id) or not ValidRequest(request_id) then return end
    local component = ResolveSender(sender)
    if component == nil or AchievementCatalog.ById(id) == nil then return end
    local ok = component.core:ClaimAchievement(id, request_id)
    component:PushSnapshot() -- Also acknowledge rejected requests to release UI pending state.
end)

AddModRPCHandler(modname, "AchievementPerk", function(sender, id, request_id, ...)
    if select("#", ...) ~= 0 or not ValidID(id) or not ValidRequest(request_id) then return end
    local component = ResolveSender(sender)
    if component == nil or PerkCatalog.ById(id) == nil then return end
    local ok = component.core:PurchasePerk(id, request_id)
    component:PushSnapshot()
end)

AddModRPCHandler(modname, "AchievementSeasonal", function(sender, kind, slot_index, id, request_id, ...)
    if select("#", ...) ~= 0 or not ValidID(id) or not ValidRequest(request_id) then return end
    local component = ResolveSender(sender)
    local seasonal = component ~= nil and component.core.seasonal or nil
    if seasonal == nil or seasonal.season ~= G.TheWorld.state.season then return end
    if kind == "task" then
        if not Integer(slot_index, 1, 20) then return end
        local slot = seasonal.slots[slot_index]
        if slot == nil or slot.task_id ~= id then return end
        local before = slot.claims
        local ok = component:ClaimSeasonal(slot.task_id, request_id)
        if ok and slot.claims > before then
            Route(sender, "season_mission_completed", { milestone=seasonal.first_claims }, 1, true)
            Route(sender, "season_mission_claimed", { source="seasonal" }, 1)
            if slot.claims > 1 then Route(sender, "season_mission_repeat", { source="seasonal" }, 1) end
        end
    elseif kind == "chest" then
        if not Integer(slot_index, 1, 4) then return end
        local milestone = CHEST_MILESTONES[slot_index]
        if id ~= "chest_" .. tostring(milestone) then return end
        component:ClaimChest(seasonal.season, milestone, request_id)
    end
end)

AddModRPCHandler(modname, "AchievementSnapshot", function(sender, request_id, ...)
    if select("#", ...) ~= 0 or not ValidRequest(request_id) then return end
    local component = ResolveSender(sender)
    if component ~= nil then component:PushSnapshot() end
end)
