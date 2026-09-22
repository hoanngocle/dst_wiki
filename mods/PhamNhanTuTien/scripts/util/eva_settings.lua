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
STRINGS.CHARACTER_DESCRIPTIONS.eva = "\n󰀍 EVA — Người bảo hộ cuối cùng.\n󰀉 Hồn Lực nuôi dưỡng sáu kỹ năng.\n󰀀 Lưỡi hái tím bạc, kiếm khí theo đòn đánh."
STRINGS.CHARACTER_QUOTES.eva = "\"Linh hồn vẫn luôn ghi nhớ.\""
STRINGS.CHARACTER_SURVIVABILITY.eva = "Khó"

STRINGS.CHARACTERS.EVA = require "speech_eva"

STRINGS.NAMES.EVA = "EVA"
STRINGS.SKIN_NAMES.eva_none = "EVA"
STRINGS.SKIN_DESCRIPTIONS.eva_none = "Váy tím bạc"

-- Chỉ số nền cố định, không còn xuất hiện trong menu cấu hình.
TUNING.EVA_HEALTH = 125
TUNING.EVA_HUNGER = 125
TUNING.EVA_SANITY = 200
TUNING.EVA_HUNGER_RATE = 1
TUNING.EVA_SPEED = 1
TUNING.EVA_DMG = 1
TUNING.EVA_REAP_COUNTER = 100 -- Fixed base; actual capacity follows saved EVA level.
TUNING.EVA_WINGS_SOUL_COST = 100
TUNING.EVA_WINGS_SPEED_MULTIPLIER = 1.08
TUNING.EVA_SCYTHE_ARRAY_SOUL_COST = 100
TUNING.EVA_SCYTHE_ARRAY_COOLDOWN = 60

TUNING.EVA_STARTERS = Config("eva_starters", true)
TUNING.EVA_SCYTHE_DMG = 68
TUNING.EVA_SCYTHE_RECIPE = 1
TUNING.EVA_HIDDEN = true
TUNING.EVA_HUD = true

if TUNING.EVA_STARTERS then
    TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.EVA = {
        "eva_scythe",
    }
    TUNING.STARTING_ITEM_IMAGE_OVERRIDE["eva_scythe"] = {
        atlas = "images/inventoryimages/eva_scythe_starting.xml",
        image = "eva_scythe_starting.tex",
    }
else
    TUNING.GAMEMODE_STARTING_ITEMS.DEFAULT.EVA = {}
end

STRINGS.NAMES.EVA_SCYTHE = "Lưỡi Hái EVA"
STRINGS.CHARACTERS.GENERIC.DESCRIBE.EVA_SCYTHE = "Một lưỡi hái mang sắc tím bạc."
STRINGS.CHARACTERS.EVA.DESCRIBE.EVA_SCYTHE = "Người bạn đồng hành của mình."
STRINGS.RECIPE_DESC.EVA_SCYTHE = "Lưỡi hái tím bạc của EVA."
