-- Keep the unpaid queue in save data, including saves during the spin animation.
local SlotMachine = Class(function(self, inst)
    self.inst = inst
    self.busy = false
end)

function SlotMachine:CanAccept(item)
    return not self.busy and item ~= nil and item.prefab == "ttk_lingshi2"
end

function SlotMachine:Start(prize)
    if self.busy or prize == nil then return false end
    self.queue = {}
    for _, item in ipairs(prize.items) do
        for i = 1, item.count do self.queue[#self.queue + 1] = item.prefab end
    end
    self.category = prize.category
    self.nextitem = 1
    self.busy = true
    self.inst:PushEvent("ttk_slot_spin", {category = self.category})
    return true
end

function SlotMachine:Pay()
    if not self.busy or self.task ~= nil then return end
    self.task = self.inst:DoTaskInTime(.25, function()
        self.task = nil
        local name = self.queue[self.nextitem]
        if name ~= nil then
            self.inst:DispensePrize(name)
            self.nextitem = self.nextitem + 1
        end
        if self.nextitem > #self.queue then
            self.busy = false
            self.queue = nil
            self.inst:PushEvent("ttk_slot_done")
        else
            self:Pay()
        end
    end)
end

function SlotMachine:OnSave()
    if not self.busy then return end
    local pending = {}
    for i = self.nextitem, #self.queue do pending[#pending + 1] = self.queue[i] end
    return {queue = pending, category = self.category}
end

function SlotMachine:OnLoad(data)
    if data == nil or data.queue == nil or #data.queue == 0 then return end
    self.queue = data.queue
    self.category = data.category
    self.nextitem = 1
    self.busy = true
    self:Pay()
end

function SlotMachine:OnRemoveFromEntity()
    if self.task ~= nil then self.task:Cancel(); self.task = nil end
end

return SlotMachine
