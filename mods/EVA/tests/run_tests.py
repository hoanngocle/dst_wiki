"""Run from any directory with Python + lupa (Lua 5.1)."""
import os
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
workspace = root.parents[1]
sys.path.insert(0, str(workspace / 'mods/mod_steam/.fasttravel-test-runtime'))
from lupa.lua51 import LuaRuntime

os.chdir(root)
lua = LuaRuntime(unpack_returned_tuples=True)
compile_lua = lua.eval('function(s, n) local f, e = loadstring(s, n); return f ~= nil, e end')
paths = list(root.rglob('*.lua'))
for path in paths:
    ok, error = compile_lua(path.read_text(encoding='utf-8-sig'), str(path))
    assert ok, error
print(f'Lua 5.1 syntax: {len(paths)} files passed', flush=True)
lua.execute((root / 'tests/test_damage.lua').read_text(encoding='utf-8'))
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute((root / 'tests/test_souls.lua').read_text(encoding='utf-8'))
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute((root / 'tests/test_skill_unlocks.lua').read_text(encoding='utf-8'))
