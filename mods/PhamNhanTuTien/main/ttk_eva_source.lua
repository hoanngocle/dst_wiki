PrefabFiles = {
	"eva",
    "eva_none",
    "eva_scythe",
    "eva_life_fx",
    "eva_wings_fx",
    "eva_scythe_array_fx",
    "eva_combat_fx",
    "eva_harvest_fx",
    "eva_fox_fx",
    "eva_skillbook"
}

Assets = {
    Asset("IMAGE", "images/eva_skill_toggle.tex"),
    Asset("ATLAS", "images/eva_skill_toggle.xml"),
    Asset("IMAGE", "images/eva_skill_icons.tex"),
    Asset("ATLAS", "images/eva_skill_icons.xml"),
    Asset("IMAGE", "images/inventoryimages/eva_moon_wings.tex"),
    Asset("ATLAS", "images/inventoryimages/eva_moon_wings.xml"),
    Asset("IMAGE", "images/inventoryimages/eva_life_flower.tex"),
    Asset("ATLAS", "images/inventoryimages/eva_life_flower.xml"),
    Asset("IMAGE", "images/inventoryimages/eva_scythe_starting.tex"),
    Asset("ATLAS", "images/inventoryimages/eva_scythe_starting.xml"),
    Asset( "IMAGE", "images/saveslot_portraits/eva.tex" ),
    Asset( "ATLAS", "images/saveslot_portraits/eva.xml" ),

    Asset( "IMAGE", "images/selectscreen_portraits/eva.tex" ),
    Asset( "ATLAS", "images/selectscreen_portraits/eva.xml" ),
	
    Asset( "IMAGE", "images/selectscreen_portraits/eva_silho.tex" ),
    Asset( "ATLAS", "images/selectscreen_portraits/eva_silho.xml" ),

    Asset( "IMAGE", "bigportraits/eva.tex" ),
    Asset( "ATLAS", "bigportraits/eva.xml" ),

    Asset( "IMAGE", "bigportraits/eva_none.tex" ),
    Asset( "ATLAS", "bigportraits/eva_none.xml" ),

	
	Asset( "IMAGE", "images/map_icons/eva.tex" ),
	Asset( "ATLAS", "images/map_icons/eva.xml" ),
	
	Asset( "IMAGE", "images/avatars/avatar_eva.tex" ),
    Asset( "ATLAS", "images/avatars/avatar_eva.xml" ),
	
	Asset( "IMAGE", "images/avatars/avatar_ghost_eva.tex" ),
    Asset( "ATLAS", "images/avatars/avatar_ghost_eva.xml" ),
	
	Asset( "IMAGE", "images/avatars/self_inspect_eva.tex" ),
    Asset( "ATLAS", "images/avatars/self_inspect_eva.xml" ),
	
	Asset( "IMAGE", "images/names_eva.tex" ),
    Asset( "ATLAS", "images/names_eva.xml" ),
	
	Asset( "IMAGE", "images/names_gold_eva.tex" ),
    Asset( "ATLAS", "images/names_gold_eva.xml" ),

    Asset( "IMAGE", "images/inventoryimages/evatab.tex" ),
    Asset( "ATLAS", "images/inventoryimages/evatab.xml" ),

	Asset("IMAGE", "images/souls/darksoul_0.tex"),
    Asset("ATLAS", "images/souls/darksoul_0.xml"),
	Asset("IMAGE", "images/souls/darksoul_1.tex"),
    Asset("ATLAS", "images/souls/darksoul_1.xml"),
    Asset("IMAGE", "images/souls/darksoul_2.tex"),
    Asset("ATLAS", "images/souls/darksoul_2.xml"),
    Asset("IMAGE", "images/souls/darksoul_3.tex"),
    Asset("ATLAS", "images/souls/darksoul_3.xml"),

    Asset("ANIM", "anim/status_meter_soul.zip"),

}

AddMinimapAtlas("images/map_icons/eva.xml")



modimport("scripts/util/eva_settings.lua")
modimport("scripts/util/eva_recipes.lua")
modimport("scripts/util/eva_widget.lua")
modimport("scripts/announcestrings.lua")

local EvaLifeInput = require "util/eva_life_input"
EvaLifeInput.Install({
    key = GetModConfigData("eva_life_key"),
    add_rpc = AddModRPCHandler,
    add_key_handler = function(key, fn)
        if GLOBAL.TheInput ~= nil
            and (GLOBAL.TheNet == nil or not GLOBAL.TheNet:IsDedicated()) then
            GLOBAL.TheInput:AddKeyDownHandler(key, fn)
        end
    end,
    send_rpc = function(namespace, name)
        SendModRPCToServer(MOD_RPC[namespace][name])
    end,
    get_player = function() return GLOBAL.ThePlayer end,
    get_frontend = function() return GLOBAL.TheFrontEnd end,
})

local EvaWingsInput = require "util/eva_wings_input"
EvaWingsInput.Install({
    key = GetModConfigData("eva_wings_key"),
    life_key = GetModConfigData("eva_life_key"),
    add_rpc = AddModRPCHandler,
    add_key_handler = function(key, fn)
        if GLOBAL.TheInput ~= nil
            and (GLOBAL.TheNet == nil or not GLOBAL.TheNet:IsDedicated()) then
            GLOBAL.TheInput:AddKeyDownHandler(key, fn)
        end
    end,
    send_rpc = function(namespace, name)
        SendModRPCToServer(MOD_RPC[namespace][name])
    end,
    get_player = function() return GLOBAL.ThePlayer end,
    get_frontend = function() return GLOBAL.TheFrontEnd end,
})

local EvaScytheArrayInput = require "util/eva_scythe_array_input"
EvaScytheArrayInput.Install({
    key = GetModConfigData("eva_scythe_array_key"),
    life_key = GetModConfigData("eva_life_key"),
    wings_key = GetModConfigData("eva_wings_key"),
    add_rpc = AddModRPCHandler,
    add_key_handler = function(key, fn)
        if GLOBAL.TheInput ~= nil
            and (GLOBAL.TheNet == nil or not GLOBAL.TheNet:IsDedicated()) then
            GLOBAL.TheInput:AddKeyDownHandler(key, fn)
        end
    end,
    send_rpc = function(namespace, name, x, z)
        SendModRPCToServer(MOD_RPC[namespace][name], x, z)
    end,
    get_player = function() return GLOBAL.ThePlayer end,
    get_frontend = function() return GLOBAL.TheFrontEnd end,
    get_world_position = function()
        return GLOBAL.TheInput ~= nil and GLOBAL.TheInput:GetWorldPosition() or nil
    end,
})

local EvaSkillPanel = require "util/eva_skillpanel"
local fox_action = AddAction("EVA_FOX_BLINK", "Hồ Ảnh", function(action)
    return EvaSkillPanel.CastFoxAction(action)
end)
fox_action.rmb = true
fox_action.priority = 1
fox_action.distance = math.huge
fox_action.invalid_hold_action = true
fox_action.mount_valid = false

EvaSkillPanel.Install({
    add_rpc = AddModRPCHandler,
    send_rpc = function(namespace, name, skill)
        SendModRPCToServer(MOD_RPC[namespace][name], skill)
    end,
})

require("util/eva_skillpanel_states").Install({
    add_state = AddStategraphState,
    add_postinit = AddStategraphPostInit,
    add_action_handler = AddStategraphActionHandler,
})

AddComponentPostInit("playeractionpicker", function(picker)
    local previous = picker.GetRightClickActions
    picker.GetRightClickActions = function(self, position, target, spellbook)
        local actions = previous(self, position, target, spellbook)
        if actions ~= nil and #actions > 0 then return actions end
        if EvaSkillPanel.CanUseGroundFox(
            self.inst, self, position, target, spellbook, GLOBAL.TheFrontEnd) then
            return {GLOBAL.BufferedAction(
                self.inst, nil, GLOBAL.ACTIONS.EVA_FOX_BLINK, nil, position)}
        end
        return actions or {}
    end
end)

if GLOBAL.TheNet == nil or not GLOBAL.TheNet:IsDedicated() then
    local EvaFacingAliasRuntime = require "util/eva_facing_alias_runtime"
    EvaFacingAliasRuntime.InstallSkinsPuppet(AddClassPostConstruct)

    local EvaSkillPanelWidget = require "widgets/eva_skillpanel"
    AddClassPostConstruct("widgets/controls", function(controls)
        local owner = controls.owner
        if owner ~= nil and owner.prefab == "eva"
            and controls.bottomright_root ~= nil then
            controls.eva_skillpanel = controls.bottomright_root:AddChild(
                EvaSkillPanelWidget(owner))
            controls.eva_skillpanel:SetPosition(-285, 170, 0)
        end
    end)
end


-- The skins shown in the cycle view window on the character select screen.
-- A good place to see what you can put in here is in skinutils.lua, in the function GetSkinModes
local skin_modes = {
    { 
        type = "ghost_skin",
        anim_bank = "ghost",
        idle_anim = "idle",
        scale = 0.75,
        offset = { 0, -25 }
    },
}
-- Add mod character to mod character list. Also specify a gender. Possible genders are MALE, FEMALE, ROBOT, NEUTRAL, and PLURAL.
AddModCharacter("eva", "FEMALE",skin_modes)
