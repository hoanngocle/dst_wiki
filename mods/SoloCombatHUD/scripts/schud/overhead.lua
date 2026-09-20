local M = {}

function M.install(env)
    local G = env.GLOBAL
    if not G.TheNet:GetIsServer() or not G.TUNING.SCHUD.OVERHEAD_BAR then return end

    env.AddComponentPostInit("combat", function(combat)
        local inst = combat.inst
        if inst:HasTag("player") then return end

        local function ensure_proxy()
            if inst.components.health == nil or inst.components.health:IsDead() then return end
            if inst._schud_overhead == nil or not inst._schud_overhead:IsValid() then
                local proxy = G.SpawnPrefab("schud_overhead_proxy")
                proxy.entity:SetParent(inst.entity)
                proxy._parent = inst
                inst._schud_overhead = proxy
            end
            inst._schud_overhead:Refresh()
        end

        inst:ListenForEvent("attacked", ensure_proxy)
        inst:ListenForEvent("healthdelta", ensure_proxy)
        inst:ListenForEvent("death", function()
            if inst._schud_overhead ~= nil then inst._schud_overhead:Remove() end
        end)
    end)
end

return M
