-- Noto Serif Medium, SIL Open Font License; see fonts/ttk_forge_serif-OFL.txt.
-- Imported after Assets is initialized. Only the forge widget uses this alias.
local G = GLOBAL
local alias = "ttk_forge_serif"
local filename = MODROOT .. "fonts/ttk_forge_serif.zip"
G.TTK_FORGE_SERIF = alias
Assets = Assets or {}
table.insert(Assets, Asset("FONT", "fonts/ttk_forge_serif.zip"))

local function LoadForgeFont()
    if G.TheNet ~= nil and G.TheNet:IsDedicated() then return end
    G.TheSim:LoadFont(filename, alias)
    G.TheSim:SetupFontFallbacks(alias, G.DEFAULT_FALLBACK_TABLE)
end

-- Register immediately for widgets, and reload after a new simulation starts.
LoadForgeFont()
AddSimPostInit(LoadForgeFont)
