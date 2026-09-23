local callbacks = {}
local load_calls = {}

GLOBAL = {
    TheNet = { IsDedicated = function() return false end },
    TheSim = {
        LoadFont = function(_, filename, alias)
            table.insert(load_calls, { filename = filename, alias = alias })
        end,
    },
}
MODROOT = "../mods/PhamNhanTuTien/"
Assets = {}
Asset = function(kind, file) return { type = kind, file = file } end
AddSimPostInit = function(fn) table.insert(callbacks, fn) end

assert(loadfile(__font_loader_path))()
assert(#Assets == 1 and Assets[1].type == "FONT", "font archive is registered as a client asset")
assert(#callbacks == 1, "font loading is deferred until registered assets are resident")
assert(GLOBAL.TTK_FORGE_SERIF == nil, "font alias is hidden before native loading succeeds")
callbacks[1]()
assert(#load_calls == 1 and load_calls[1].alias == "ttk_forge_serif", "native font loads once")
assert(GLOBAL.TTK_FORGE_SERIF == "ttk_forge_serif", "successful load publishes the alias")

local failed_callbacks = {}
GLOBAL.TTK_FORGE_SERIF = nil
GLOBAL.TheSim = { LoadFont = function() error("broken archive") end }
Assets = {}
AddSimPostInit = function(fn) table.insert(failed_callbacks, fn) end
assert(loadfile(__font_loader_path))()
assert(pcall(failed_callbacks[1]), "font load failure is contained")
assert(GLOBAL.TTK_FORGE_SERIF == nil, "failed loading retains native fallback")

GLOBAL = { TheNet = { IsDedicated = function() return true end } }
Assets = {}
callbacks = {}
AddSimPostInit = function(fn) table.insert(callbacks, fn) end
assert(loadfile(__font_loader_path))()
assert(GLOBAL.TTK_FORGE_SERIF == nil, "dedicated server exposes a safe nil alias")
assert(#Assets == 0 and #callbacks == 0, "dedicated server skips client font setup")

print("Forge font lifecycle checks PASS")
