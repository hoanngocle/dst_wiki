"""Fold only literal Lua string expressions, then rename the embedded sword.

Never executes mod code. Lua evaluates only grammar-restricted string literals,
string.char(integer, ...) and :reverse() expressions from the source.
"""
from pathlib import Path
import json
import re
import sys

workspace = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workspace / 'mods/mod_steam/.fasttravel-test-runtime'))
from lupa.lua51 import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)
literal = r'''(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')'''
chars = r'string\.char\(\s*\d+(?:\s*,\s*\d+)*\s*\)'
simple = f'(?:{literal}|{chars})'
atom = rf'(?:\(\s*{simple}\s*\)|{simple})(?::reverse\(\))?'
comment = r'--\[\[.*?\]\]|--[^\r\n]*'
expression = re.compile(comment + '|' + atom + r'(?:\s*\.\.\s*' + atom + r')*', re.S)
protected = set()

def quote(s):
    value = json.dumps(s, ensure_ascii=False)
    return re.sub(r'\\u00([0-9a-f]{2})', lambda m: '\\' + str(int(m[1],16)).zfill(3), value)

def rename(s):
    # These are compiled sound-bank/vanilla event resource names, not mod IDs.
    if s.startswith('sound/terraprisma_sfx') or s.startswith('terraprisma_sfx/') or s.startswith('terraria1/skins/terraprisma'):
        protected.add(s)
        return s
    return (s.replace('TERRAPRISMA', 'LUCMACHTHANKIEM')
        .replace('Terraprisma', 'LucMachThanKiem').replace('terraprisma','lucmachthankiem')
        .replace('ttk_lucmach','lucmachthankiem').replace('TTK_LUCMACH','LUCMACHTHANKIEM')
        .replace('TTK_LucMach','lucmachthankiem').replace('ttk_lm_', 'lucmachthankiem_'))

def fold(m):
    if m.group().startswith('--'):
        return rename(m.group())
    return quote(rename(lua.eval(m.group())))

root = workspace / 'mods/PhamNhanTuTien'
paths = [p for p in root.rglob('*.lua') if
    'terraprisma' in p.name or 'ttk_lucmach' in p.name or p.name in ('modmain.lua','modinfo.lua')]
for p in paths:
    source = p.read_text('utf-8-sig')
    # Constant-fold first; stash strings so identifier rewriting cannot touch
    # protected compiled-audio resource names inside them.
    source = expression.sub(fold, source)
    strings = []
    def stash(m):
        strings.append(m.group()); return f'__LITERAL_{len(strings)-1}__'
    source = re.sub(comment + '|' + literal, stash, source, flags=re.S)
    source = rename(source)
    source = re.sub(r'__LITERAL_(\d+)__', lambda m: strings[int(m[1])], source)
    # Semicolons outside literals can be separated for more readable source.
    fn, error = lua.eval('function(s) local f,e=loadstring(s); return f,e end')(source)
    assert fn is not None, (p, error)
    p.write_text(source, encoding='utf-8')
for p in list(root.rglob('*')):
    if p.is_file() and p.suffix == '.xml' and 'terraprisma' in p.name:
        p.write_text(rename(p.read_text('utf-8-sig')), encoding='utf-8')
for p in list(root.rglob('*')):
    if p.is_file() and ('terraprisma' in p.name or 'ttk_lucmach' in p.name) and p.parent.name != 'sound':
        target = p.with_name(rename(p.name))
        assert not target.exists(), target
        p.rename(target)
print(f'Renamed {len(paths)} Lua files; compiled syntax before writing')
print('Required existing audio resource names:', sorted(protected))
