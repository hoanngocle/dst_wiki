local assets = {
    Asset("ANIM", "anim/eva_scythe.zip"),
    Asset("ANIM", "anim/swap_eva_scythe.zip"),
    Asset("ATLAS", "images/inventoryimages/eva_scythe.xml"),
}

local function OnEquip(inst, owner)
    owner.AnimState:OverrideSymbol("swap_object", "swap_eva_scythe", "swap_eva_scythe")
    owner.AnimState:Show("ARM_carry")
    owner.AnimState:Hide("ARM_normal")
end

local function OnUnequip(inst, owner)
    owner.AnimState:Hide("ARM_carry")
    owner.AnimState:Show("ARM_normal")
end

local function fn()
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    inst.entity:AddMiniMapEntity()

    MakeInventoryPhysics(inst)

    inst.AnimState:SetBank("eva_scythe")
    inst.AnimState:SetBuild("eva_scythe")
    inst.AnimState:PlayAnimation("idle")
    inst.MiniMapEntity:SetIcon("eva_scythe.tex")

    inst:AddTag("eva_scythe")
    inst:AddTag("shadow_item")
    inst:AddTag("shadow")
    inst:AddTag("sharp")
    inst:AddTag("weapon")

    local swap_data = {sym_build = "swap_eva_scythe"}
    MakeInventoryFloatable(inst, "large", 0.05, {0.8, 0.35, 0.8}, true, -27, swap_data)

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(TUNING.EVA_SCYTHE_DMG)

    if TUNING.EVA_SCYTHE_DURABILITY ~= 9999 then
        inst:AddComponent("finiteuses")
        inst.components.finiteuses:SetMaxUses(TUNING.EVA_SCYTHE_DURABILITY)
        inst.components.finiteuses:SetUses(TUNING.EVA_SCYTHE_DURABILITY)
        inst.components.finiteuses:SetOnFinished(inst.Remove)
    end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "eva_scythe"
    inst.components.inventoryitem.atlasname = "images/inventoryimages/eva_scythe.xml"

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(OnEquip)
    inst.components.equippable:SetOnUnequip(OnUnequip)

    MakeHauntableLaunch(inst)

    return inst
end

return Prefab("common/inventory/eva_scythe", fn, assets)
