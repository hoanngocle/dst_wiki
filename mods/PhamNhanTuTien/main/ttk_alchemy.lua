AddPlayerPostInit(function(inst)
    if not TheWorld.ismastersim then return end
    if inst.components.ttk_cultivation == nil then
        inst:AddComponent("ttk_cultivation")
    end
end)
