local require = GLOBAL.require
local STRINGS = GLOBAL.STRINGS

local function Config(name, fallback)
    local value = GetModConfigData(name)
    if value == nil then
        return fallback
    end
    return value
end

STRINGS.CHARACTER_TITLES.eva = "Linh Hồn Tử Sắc"
STRINGS.CHARACTER_NAMES.eva = "EVA"
STRINGS.CHARACTER_DESCRIPTIONS.eva = "\n󰀍 Sinh Chi Hoa tấn công và bảo hộ.\n󰀉 Hồn Lực nuôi dưỡng sáu kỹ năng.\n󰀀 Lưỡi hái tím bạc, kiếm khí theo đòn đánh."
STRINGS.CHARACTER_QUOTES.eva = "\"Linh hồn vẫn luôn ghi nhớ.\""
STRINGS.CHARACTER_SURVIVABILITY.eva = "Khó"

STRINGS.CHARACTERS.EVA = require "speech_eva"

STRINGS.NAMES.EVA = "EVA"
STRINGS.SKIN_NAMES.eva_none = "EVA"
STRINGS.SKIN_DESCRIPTIONS.eva_none = "Váy tím bạc"

-- Active EVA tuning. Fallbacks keep existing worlds usable after old menu
-- entries are removed from modinfo.
TUNING.EVA_HEALTH = Config("eva_health", 125)
TUNING.EVA_HUNGER = Config("eva_hunger", 125)
TUNING.EVA_SANITY = Config("eva_sanity", 200)
TUNING.EVA_HUNGER_RATE = Config("eva_hunger_rate", 1)
TUNING.EVA_SPEED = Config("eva_speed", 1)
TUNING.EVA_DMG = Config("eva_dmg", 1)
TUNING.EVA_REAP_COUNTER = 100 -- Fixed base; actual capacity follows saved EVA level.
TUNING.EVA_WINGS_SOUL_COST = 100
TUNING.EVA_WINGS_SPEED_MULTIPLIER = 1.08
TUNING.EVA_SCYTHE_ARRAY_SOUL_COST = 100
TUNING.EVA_SCYTHE_ARRAY_COOLDOWN = 60

TUNING.EVA_STARTERS = Config("eva_starters", true)
TUNING.EVA_SCYTHE_DMG = Config("eva_scythe_dmg", 68)
TUNING.EVA_SCYTHE_RECIPE = Config("eva_scythe_recipe", 1)
TUNING.EVA_SCYTHE_DURABILITY = Config("eva_scythe_durability", 666)
TUNING.EVA_HIDDEN = Config("eva_clothes", false)
TUNING.EVA_HUD = Config("eva_hud", true)

if TUNING.EVA_STARTERS then
    TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.EVA = {
        "eva_scythe",
    }
    TUNING.STARTING_ITEM_IMAGE_OVERRIDE["eva_scythe"] = {
        atlas = "images/inventoryimages/eva_scythe.xml",
        image = "eva_scythe.tex",
    }
else
    TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.EVA = {}
end

STRINGS.NAMES.EVA_SCYTHE = "Lưỡi Hái EVA"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.EVA_SCYTHE = "Một lưỡi hái mang sắc tím bạc."
STRINGS.CHARACTERS.EVA.DESCRIBE.EVA_SCYTHE = "Người bạn đồng hành của mình."
STRINGS.RECIPE_DESC.EVA_SCYTHE = "Lưỡi hái tím bạc của EVA."
