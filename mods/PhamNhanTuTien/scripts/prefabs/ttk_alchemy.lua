local Defs = require("alchemy/ttk_alchemy_defs")

local function OnEaten(inst, eater)
    if eater == nil or not TheWorld.ismastersim then return end
    local cultivation = eater.components.ttk_cultivation
    if cultivation ~= nil and Defs.GetCultivationStage(cultivation:GetStage() + 1) ~= nil then
        local row = Defs.Get(inst.prefab)
        if row ~= nil and row == Defs.GetCultivationStage(cultivation:GetStage() + 1) then
            local ok = eater.components.ttk_cultivation:Consume(inst.prefab)
            if ok then
                inst:Remove()
            end
            return
        end
    end
    if eater.components.ttk_alchemy_effects ~= nil then eater.components.ttk_alchemy_effects:Apply(inst.prefab) end
end

local function MakePill(prefab)
    local function fn()
        local inst = CreateEntity()
        inst.entity:AddTransform(); inst.entity:AddAnimState(); inst.entity:AddNetwork()
        MakeInventoryPhysics(inst)
        inst:AddTag("xd_danyao")
        inst.AnimState:SetBank("quagmire_food"); inst.AnimState:SetBuild("quagmire_food"); inst.AnimState:PlayAnimation("idle")
        inst.entity:SetPristine()
        if not TheWorld.ismastersim then return inst end
        inst:AddComponent("inspectable")
        inst:AddComponent("inventoryitem")
        inst:AddComponent("edible")
        inst.components.edible.foodtype = FOODTYPE.GOODIES
        inst.components.edible:SetOnEatenFn(OnEaten)
        return inst
    end
    return Prefab(prefab, fn)
end

return MakePill("xd_danyao_jq"), MakePill("xd_danyao_dt"), MakePill("xd_danyao_zj"),
    MakePill("xd_danyao_xs"), MakePill("xd_danyao_hj"), MakePill("xd_danyao_yz"),
    MakePill("xd_danyao_sm"), MakePill("xd_danyao_rl"), MakePill("xd_danyao_jy"),
    MakePill("xd_danyao_yx"), MakePill("xd_danyao_ns"), MakePill("xd_danyao_hs"),
    MakePill("xd_danyao_hy"), MakePill("xd_danyao_hl"), MakePill("xd_danyao_kx"),
    MakePill("xd_danyao_bg"), MakePill("xd_dy_cyfxd_1"), MakePill("xd_dy_dmhsd_1"),
    MakePill("xd_dy_lmsqd_1"), MakePill("xd_dy_qxdhd_1"), MakePill("xd_dy_yfsxd_1"),
    MakePill("xd_dy_pshsd_1"), MakePill("xd_dy_qjqsd_1"), MakePill("xd_dy_xynyd_1"),
    MakePill("xd_dy_hsphd_1"), MakePill("xd_dy_xttyd_1")
