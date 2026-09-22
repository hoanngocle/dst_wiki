local assets = {
    Asset("ANIM", "anim/eva_scythe.zip"),
    Asset("ANIM", "anim/swap_eva_scythe.zip"),
    Asset("ATLAS", "images/inventoryimages/eva_scythe.xml"),
}

local MAX_USES = 1000
local repairvalues = require "ttk_tinhlakiem_repair"

local function CanRepair(inst, item, giver, count)
    return item ~= nil and item ~= inst and repairvalues[item.prefab] ~= nil
        and (count == nil or count == 1)
        and inst.components.finiteuses:GetPercent() < 1
end

local function OnRepair(inst, giver, item)
    inst.components.finiteuses:Repair(repairvalues[item.prefab])
    if giver ~= nil and giver.SoundEmitter ~= nil then
        giver.SoundEmitter:PlaySound("dontstarve/common/nightmareAddFuel")
    end
end

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
    inst:AddTag("alltrader")

    local swap_data = {sym_build = "swap_eva_scythe"}
    MakeInventoryFloatable(inst, "large", 0.05, {0.8, 0.35, 0.8}, true, -27, swap_data)

    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("weapon")
    inst.components.weapon:SetDamage(TUNING.EVA_SCYTHE_DMG)

    inst:AddComponent("finiteuses")
    inst.components.finiteuses:SetMaxUses(MAX_USES)
    inst.components.finiteuses:SetUses(MAX_USES)

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "eva_scythe"
    inst.components.inventoryitem.atlasname = "images/inventoryimages/eva_scythe.xml"

    inst:AddComponent("equippable")
    inst.components.equippable:SetOnEquip(OnEquip)
    inst.components.equippable:SetOnUnequip(OnUnequip)

    inst:AddComponent("trader")
    inst.components.trader.acceptnontradable = true
    inst.components.trader:SetAbleToAcceptTest(CanRepair)
    inst.components.trader.onaccept = OnRepair

    MakeHauntableLaunch(inst)

    return inst
end

return Prefab("common/inventory/eva_scythe", fn, assets)
