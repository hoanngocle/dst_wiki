local Ingredient = GLOBAL.Ingredient
local TECH = GLOBAL.TECH

local eva_tab = AddRecipeTab(
    "EVA",
    99,
    "images/inventoryimages/evatab.xml",
    "evatab.tex",
    "eva"
)

local ingredients
if TUNING.EVA_SCYTHE_RECIPE == 0 then
    ingredients = {
        Ingredient("nightmarefuel", 6),
        Ingredient("monstermeat", 6),
        Ingredient("spear", 6),
    }
elseif TUNING.EVA_SCYTHE_RECIPE == 1 then
    ingredients = {
        Ingredient("nightmarefuel", 6),
        Ingredient("bluegem", 6),
        Ingredient("spear", 6),
    }
else
    ingredients = {
        Ingredient("nightmarefuel", 6),
        Ingredient("purplegem", 6),
        Ingredient("nightsword", 6),
    }
end

AddRecipe(
    "eva_scythe",
    ingredients,
    eva_tab,
    TECH.NONE,
    nil,
    nil,
    nil,
    1,
    "eva",
    "images/inventoryimages/eva_scythe.xml",
    "eva_scythe.tex"
)
