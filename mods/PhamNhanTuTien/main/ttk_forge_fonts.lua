-- Noto Serif Medium (OFL), compiled by tools/build_forge_font.py.
-- LoadFonts runs after asset registration. Calling LoadFont in modmain is
-- too early and causes a native assertion, even with a stock DST font.
local G = GLOBAL
if G.TheNet:IsDedicated() then return end
local alias = "ttk_forge_serif"
local filename = MODROOT .. "fonts/ttk_forge_serif.zip"
G.TTK_FORGE_SERIF = alias
Assets = Assets or {}
table.insert(Assets, Asset("FONT", "fonts/ttk_forge_serif.zip"))
for _, font in ipairs(G.FONTS) do
    if font.alias == alias then
        font.filename = filename
        font.fallback = G.DEFAULT_FALLBACK_TABLE
        return
    end
end
table.insert(G.FONTS, {
    filename = filename,
    alias = alias,
    fallback = G.DEFAULT_FALLBACK_TABLE,
})
