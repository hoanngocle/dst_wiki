from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / ".superpowers/ttk-solo-integration/lua-runtime"))
from lupa.lua51 import LuaRuntime


lua = LuaRuntime(unpack_returned_tuples=True)
lua.globals().package.path = str(ROOT / "scripts/?.lua").replace("\\", "/") + ";" + lua.globals().package.path
lua.execute(r'''
package.preload["util/eva_progression"] = function()
    return {
        IsUnlocked = function() return true end,
        RequiredLevel = function() return 1 end,
        Check = function() return true end,
    }
end
GetTime = function() return 1 end

local Panel = require("util/eva_skillpanel")
local expected = {"life", "harvest", "wings", "daydu", "array"}
local expected_spell_indexes = {1, 4, 2, 5, 3}
assert(#Panel.HOTKEY_ORDER == 5)
for index, skill in ipairs(expected) do
    assert(Panel.HOTKEY_ORDER[index] == skill)
    assert(Panel.DISPLAY_ORDER[index] == skill)
end

local selected, executed, handlers = {}, {}, {}
local player = {
    prefab = "eva",
    components = {},
    HUD = {HasInputFocus = function() return false end},
    IsValid = function() return true end,
    HasTag = function(_, tag) return tag == "eva" end,
}
local spellbook = {items = {}}
function spellbook:SelectSpell(index)
    selected[#selected + 1] = index
    return true
end
for index = 1, 5 do
    spellbook.items[index] = {execute = function() executed[#executed + 1] = index end}
end
local book = {
    components = {spellbook = spellbook},
    IsValid = function() return true end,
    GetEvaOwner = function() return player end,
}
player._eva_skillbook_entity = book
local frontend = {
    IsControlsDisabled = function() return false end,
    GetActiveScreen = function() return {name = "HUD"} end,
}

Panel.Install({
    add_rpc = function() end,
    send_rpc = function() end,
    keys = {49, 50, 51, 52, 53},
    add_key_handler = function(key, fn) handlers[key] = fn end,
    get_player = function() return player end,
    get_frontend = function() return frontend end,
})
for key = 49, 53 do
    assert(type(handlers[key]) == "function", "missing top-row handler " .. tostring(key))
    handlers[key]()
end
assert(#selected == 5 and #executed == 5)
for index = 1, 5 do
    assert(selected[index] == expected_spell_indexes[index])
    assert(executed[index] == expected_spell_indexes[index])
end
print("PASS: EVA skills use fixed top-row keys 1-5 in unlock-level order")
''')
