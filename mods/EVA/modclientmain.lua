PrefabFiles = {
	"eva",
    "eva_none",
    "eva_scythe",
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

}

AddMinimapAtlas("images/map_icons/eva.xml")



modimport("scripts/util/eva_settings.lua")

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
