local function update(inst)
    -- HUD widgets consume the replicated values directly.
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddNetwork()
    inst:AddTag("FX")
    inst:AddTag("NOCLICK")
    inst.persists = false
    inst.Transform:SetPosition(0, 2.35, 0)

    inst._current = net_float(inst.GUID, "schud.overhead.current", "schud_overhead_dirty")
    inst._maximum = net_float(inst.GUID, "schud.overhead.maximum", "schud_overhead_dirty")
    inst._visible = net_bool(inst.GUID, "schud.overhead.visible", "schud_overhead_dirty")
    inst:ListenForEvent("schud_overhead_dirty", update)
    inst.entity:SetPristine()

    if not TheNet:IsDedicated() then
        SCHUD_OVERHEAD_PROXIES = SCHUD_OVERHEAD_PROXIES or setmetatable({}, { __mode = "k" })
        SCHUD_OVERHEAD_PROXIES[inst] = true
        inst:ListenForEvent("onremove", function() SCHUD_OVERHEAD_PROXIES[inst] = nil end)
    end

    if not TheWorld.ismastersim then
        return inst
    end

    function inst:Refresh()
        local health = self._parent ~= nil and self._parent.components.health or nil
        if health == nil then self:Remove() return end
        self._current:set(math.max(0, health.currenthealth))
        self._maximum:set(math.max(1, health.maxhealth))
        self._visible:set(true)
        if self._hide_task ~= nil then self._hide_task:Cancel() end
        self._hide_task = self:DoTaskInTime(8, function(proxy) proxy._visible:set(false) end)
    end
    return inst
end

return Prefab("schud_overhead_proxy", fn)
