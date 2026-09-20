"""Phàm Nhân Tu Tiên: execute HUD contracts and compile the integrated Lua tree."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'mods/PhamNhanTuTien'
sys.path.insert(0, str(ROOT / '.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.chdir(TARGET)
    failed = []
    tests = sorted((TARGET / 'tests/hud').glob('test_*.lua'))
    for path in tests:
        print('RUN', path.relative_to(TARGET), flush=True)
        try:
            lua = LuaRuntime(unpack_returned_tuples=True)
            lua.execute(path.read_text(encoding='utf-8-sig'), name='@' + str(path))
        except Exception as exc:
            failed.append(str(path))
            print(exc, flush=True)
    if not tests:
        failed.append('No HUD tests found')
    lua = LuaRuntime(unpack_returned_tuples=True)
    compile_lua = lua.eval('function(s,n) local f,e=loadstring(s,n); return f~=nil,e end')
    sources = list(TARGET.rglob('*.lua'))
    for path in sources:
        ok, err = compile_lua(path.read_text(encoding='utf-8-sig'), '@' + str(path))
        if not ok:
            failed.append(str(path))
            print(err, flush=True)
    print(f'HUD tests: {len(tests)} files; syntax: {len(sources)} Lua files; failures: {len(failed)}')
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
