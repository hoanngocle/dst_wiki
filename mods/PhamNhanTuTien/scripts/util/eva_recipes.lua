local Ingredient = GLOBAL.Ingredient
local TECH = GLOBAL.TECH

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

AddRecipe2(
    "eva_scythe",
    ingredients,
    TECH.NONE,
    {numtogive = 1, builder_tag = "eva", atlas = "images/inventoryimages/eva_scythe.xml", image = "eva_scythe.tex"},
    {"CHARACTER"}
)
