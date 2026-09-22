local Rules = require("alchemy/ttk_alchemy_rules")

local DURATION = 180

local AlchemyStation = Class(function(self, inst)
    self.inst = inst
    self.output = nil
    self.end_time = nil
    self.finish_task = nil
    self.finishing = false
end)

local function IsRemaining(value)
    return type(value) == "number"
        and value == value
        and value ~= math.huge
        and value ~= -math.huge
end

function AlchemyStation:IsBusy()
    return self.output ~= nil
end

function AlchemyStation:GetRecipe()
    local container = self.inst.components.container
    local items = container ~= nil and Rules.NormalizeStacks(container.slots) or nil
    return Rules.FindExactRecipe(items)
end

function AlchemyStation:CanStart()
    if self:IsBusy() then return false end
    local recipe, output = self:GetRecipe()
    return recipe ~= nil and Rules.IsApprovedOutput(output)
end

function AlchemyStation:CancelFinishTask()
    if self.finish_task ~= nil then
        self.finish_task:Cancel()
        self.finish_task = nil
    end
end

function AlchemyStation:ScheduleFinish(remaining)
    self:CancelFinishTask()
    self.finish_task = self.inst:DoTaskInTime(math.max(0, remaining), function()
        self.finish_task = nil
        self:Finish()
    end)
end

function AlchemyStation:Start(doer)
    if not TheWorld.ismastersim or self:IsBusy() then return false end
    local container = self.inst.components.container
    local recipe, output = self:GetRecipe()
    if container == nil or recipe == nil or not Rules.IsApprovedOutput(output) then return false end

    -- All checks precede mutation. Exact matching means each captured stack is consumed once.
    local consumed = {}
    for slot, item in pairs(container.slots) do
        if item == nil then return false end
        consumed[#consumed + 1] = { slot = slot, item = item }
    end
    if #consumed == 0 then return false end
    for _, entry in ipairs(consumed) do
        entry.item:Remove()
    end

    container:Close()
    self.output = output
    self.end_time = GetTime() + DURATION
    self:ScheduleFinish(DURATION)
    return true
end

function AlchemyStation:Finish()
    if self.finishing or not self:IsBusy() then return false end
    self.finishing = true
    local output = self.output
    -- Clear/cancel before creating an item so re-entry cannot duplicate output.
    self.output = nil
    self.end_time = nil
    self:CancelFinishTask()

    local item = SpawnPrefab(output)
    local container = self.inst.components.container
    local placed = item ~= nil and container ~= nil and container:GiveItem(item, nil, nil, false)
    if item ~= nil and not placed and item:IsValid() then
        item.Transform:SetPosition(self.inst.Transform:GetWorldPosition())
    end
    self.finishing = false
    return item ~= nil
end

function AlchemyStation:OnSave()
    if not self:IsBusy() or not Rules.IsApprovedOutput(self.output) then return nil end
    local remaining = self.end_time - GetTime()
    if not IsRemaining(remaining) then return nil end
    return { output = self.output, remaining = math.max(0, remaining) }
end

function AlchemyStation:OnLoad(data)
    self:CancelFinishTask()
    self.output = nil
    self.end_time = nil
    if type(data) ~= "table" or not Rules.IsApprovedOutput(data.output) or not IsRemaining(data.remaining) then return end
    self.output = data.output
    self.end_time = GetTime() + math.max(0, data.remaining)
    self:ScheduleFinish(data.remaining)
end

function AlchemyStation:OnRemoveFromEntity()
    self:CancelFinishTask()
end

return AlchemyStation
