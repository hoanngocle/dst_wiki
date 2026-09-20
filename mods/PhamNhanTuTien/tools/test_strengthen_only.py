"""Phàm Nhân: only strengthening remains; migrate legacy saves and preserve risks."""
from pathlib import Path
from zipfile import ZipFile
import sys

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]
sys.path.insert(0, str(ROOT / '.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
with ZipFile("C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip") as game:
    lua.execute(game.read('scripts/class.lua').decode())
lua.globals().package.path = str(MOD/'scripts/?.lua').replace('\\', '/') + ';' + lua.globals().package.path
lua.execute('''
S = require('components/wb_strengthen')
assert(S.DoIncrease == nil, 'Removed mode must have no callable entry point')
TheNet={Announce=function() end}
local player={name='Test',components={talker={Say=function() end}}}
function Make(level,mode)
 local inst={components={},HasTag=function() return false end,Remove=function(s) s.removed=true end}
 local s=setmetatable({inst=inst,level=level,do_mode=mode,original_name='Test',
  buffs_status={},prize_buff_list={},manual_buff_list={}}, {__index=S})
 function s:Refresh() end
 return s
end
for _, mode in ipairs({'strengthen','increase'}) do
 for _, level in ipairs({0,6,13,22}) do
  local s=Make(0,nil)
  s:OnLoad({do_mode=mode,level=level})
  assert(s.do_mode=='strengthen' and s.level==math.min(level,13),'Normalize legacy mode and cap')
  local saved=s:OnSave()
  assert(saved.do_mode=='strengthen')
  assert(not string.find(s:GetDisplayName('Test'),'Phụ Ma',1,true))
 end
end
for n=1,13 do
 local s=Make(n-1,'strengthen')
 assert(math.abs(s:GetProbability(player,'strengthen',n)-1.1*.85^n)<1e-12)
 s:DoFail(player,'strengthen',n)
 assert(s.level==(n>=6 and n-2 or n-1),'Failure downgrade changed')
 assert((s.inst.removed==true)==(n>=10),'Failure destruction changed')
end
local s=Make(5,'strengthen')
function s:GetProbability() return 1 end
s:DoStrengthen(player)
assert(s.level==6 and s.do_mode=='strengthen')
s:SetLevel(13)
s:DoStrengthen(player)
assert(s.level==13, 'Max level must stay capped')
''')
print('PASS: removed entry point, old-save migration, +13 cap, odds, success and failure tiers.')

for folder in ('main', 'scripts'):
    for path in (MOD/folder).rglob('*.lua'):
        text=path.read_text(encoding='utf-8-sig')
        assert 'Phụ Ma' not in text and 'phụ ma' not in text, path
        for token in ('DoIncrease', 'isincrease', 'wb_strengthen_increase', 'purplegem_count'):
            assert token not in text, (path, token)
print('PASS: no dormant mode API, option, UI text or purple-gem payload in runtime Lua.')
