local G = GLOBAL
local containers = G.require("containers")

table.insert(Assets, Asset("ANIM", "anim/ui_xd_liandanlu_1x4.zip"))

containers.params.xd_liandanlu = {
    widget = {
        slotpos = { G.Vector3(-55, 0, 0), G.Vector3(-18, 0, 0), G.Vector3(18, 0, 0), G.Vector3(55, 0, 0) },
        animbank = "ui_xd_liandanlu_1x4",
        animbuild = "ui_xd_liandanlu_1x4",
        pos = G.Vector3(0, 200, 0),
    },
    type = "chest",
}

G.STRINGS.NAMES.XD_LIANDANLU = "Đan Lô"
G.STRINGS.RECIPE_DESC.XD_LIANDANLU = "Luyện đan chính xác trong 180 giây."
G.STRINGS.CHARACTERS.GENERIC.DESCRIBE.XD_LIANDANLU = "Một lò luyện đan ổn định."

AddRecipe2("xd_liandanlu", {
    G.Ingredient("goldnugget", 5),
    G.Ingredient("cutstone", 3),
    G.Ingredient("flint", 3),
    G.Ingredient("ttk_lingshi1", 5),
}, G.TECH.SCIENCE_TWO, {
    atlas = "images/inventoryimages/xd_liandanlu.xml",
    image = "xd_liandanlu.tex",
    placer = "xd_liandanlu_placer",
    no_deconstruction = true,
}, { "STRUCTURES", "MAGIC" })

local refine = G.Action({ priority = 1, rmb = true, mount_valid = true })
refine.id = "TTK_ALCHEMY_REFINE"
refine.fn = function(action)
    if not TheWorld.ismastersim or action.target == nil or action.target.components == nil then return false end
    local station = action.target.components.ttk_alchemy_station
    return station ~= nil and station:Start(action.doer) or false
end
AddAction(refine)
G.STRINGS.ACTIONS.TTK_ALCHEMY_REFINE = "Luyện Đan"
AddComponentAction("SCENE", "inspectable", function(inst, doer, actions, right)
    local station = inst.components ~= nil and inst.components.ttk_alchemy_station or nil
    if right and station ~= nil and station:CanStart() then table.insert(actions, refine) end
end)
for _, stategraph in ipairs({ "wilson", "wilson_client" }) do
    AddStategraphActionHandler(stategraph, G.ActionHandler(refine, "give"))
end

AddPlayerPostInit(function(inst)
    if not TheWorld.ismastersim then return end
    if inst.components.ttk_cultivation == nil then
        inst:AddComponent("ttk_cultivation")
    end
    if inst.components.ttk_alchemy_effects == nil then
        inst:AddComponent("ttk_alchemy_effects")
    end
end)
