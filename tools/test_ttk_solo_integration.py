"""Executable integration contracts using DST-compatible Lua 5.1."""
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime

TARGET = ROOT / 'mods/PhamNhanTuTien'
SOURCE = ROOT / 'mods/mod_steam/3780347550'
BASELINE = ROOT / '.superpowers/ttk-solo-integration/baseline.json'


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.globals().root = TARGET.as_posix()
    lua.execute("package.path = root .. '/scripts/?.lua;' .. package.path")
    return lua


def metadata(lua, path):
    return lua.eval('function(path) local e = {}; setfenv(assert(loadfile(path)), e)(); return e end')(path.as_posix())


class IntegrationTests(unittest.TestCase):
    def test_bootstrap_keeps_both_registrations_and_loads_once(self):
        self.assertTrue((TARGET / 'main/ttk_solo_bootstrap.lua').exists(), 'Solo bootstrap is missing')
        lua = runtime()
        lua.execute('''
            GLOBAL = _G
            env = setmetatable({PrefabFiles={'ttk_weapon', 'shared'}, Assets={{type='ANIM', file='ttk.zip'}}}, {__index=_G})
            local calls = 0
            env.modimport = function(path)
                assert(path == 'main/ttk_solo_source.lua')
                calls = calls + 1
                env.PrefabFiles = {'hh_weapon', 'shared'}
                env.Assets = {{type='ANIM',file='hh.zip'}}
            end
            local f = setfenv(assert(loadfile(root .. '/main/ttk_solo_bootstrap.lua')), env)
            f(); f()
            assert(calls == 1, 'hooks installed twice')
            assert(table.concat(env.PrefabFiles, ',') == 'ttk_weapon,shared,hh_weapon')
            assert(#env.Assets == 2 and env.Assets[1].file == 'ttk.zip' and env.Assets[2].file == 'hh.zip')
        ''')

    def test_duplicate_guard_supports_ids_local_names_and_self(self):
        self.assertTrue((TARGET / 'scripts/ttk_solo_guard.lua').exists(), 'Duplicate guard is missing')
        lua = runtime()
        lua.execute('''
            local guard = require('ttk_solo_guard')
            local info = {name='【Solo Leveling】'}
            local names = {'PhamNhanTuTien'}
            local index = {
                GetModsToLoad=function(_, cached)
                    assert(cached == true, 'Worldgen has no TheSim; cached mod index required')
                    return names
                end,
                GetModInfo=function(_, name) return name == 'CustomSolo' and info or nil end,
            }
            local g = {KnownModIndex=index}
            guard.Check(g, 'PhamNhanTuTien')
            for _, id in ipairs({'workshop-3780347550', '3780347550', 'SoloLeveling', 'CustomSolo'}) do
                names = {'PhamNhanTuTien', id}
                local ok, err = pcall(guard.Check, g, 'PhamNhanTuTien')
                assert(not ok and string.find(err, 'Phàm Nhân Tu Tiên', 1, true), 'duplicate accepted: ' .. id)
            end
            names = {'workshop-3780347550'}
            guard.Check(g, 'workshop-3780347550')
            names = {'PhamNhanTuTien', 'SoloCombatHUD'}
            guard.Check(g, 'PhamNhanTuTien')
        ''')

    def test_metadata_preserves_all_defaults_and_identity(self):
        lua = runtime()
        target = metadata(lua, TARGET / 'modinfo.lua')
        source = metadata(lua, SOURCE / 'modinfo.lua')
        baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
        before = metadata(lua, Path(baseline['metadata_snapshot']))
        options = list(target.configuration_options.values())
        names = [v.name for v in options]
        self.assertEqual(len(names), len(set(names)), 'duplicate configuration keys')
        actual = {v.name: v.default for v in options}
        for data in (before, source):
            for row in data.configuration_options.values():
                self.assertIn(row.name, actual)
                self.assertEqual(row.default, actual[row.name])
        self.assertEqual('Phàm Nhân Tu Tiên', target.name)
        self.assertEqual('2.0', target.version)
        self.assertTrue(target.all_clients_require_mod)

    def test_all_solo_files_preserved_and_source_unchanged(self):
        manifest = TARGET / 'SOLO_SOURCE_MANIFEST.json'
        self.assertTrue(manifest.exists(), 'Source manifest is missing')
        data = json.loads(manifest.read_text(encoding='utf-8'))
        baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
        self.assertEqual(set(baseline['source']), {r['source'] for r in data['files']})
        for row in data['files']:
            original = hashlib.sha256((SOURCE / row['source']).read_bytes()).hexdigest()
            self.assertEqual(baseline['source'][row['source']], original, row['source'])
            self.assertEqual(original, row['sha256'])
            destination = hashlib.sha256((TARGET / row['destination']).read_bytes()).hexdigest()
            self.assertEqual(original, destination, row['destination'])

    def test_guard_precedes_hooks_and_worldgen_is_integrated(self):
        code = (TARGET / 'modmain.lua').read_text(encoding='utf-8-sig')
        self.assertIn('ttk_solo_guard', code)
        self.assertLess(code.index('ttk_solo_guard'), code.index('ttk_weapon_solo'))
        self.assertIn('main/ttk_solo_bootstrap.lua', code)
        path = TARGET / 'modworldgenmain.lua'
        self.assertTrue(path.exists(), 'Solo worldgen not integrated')
        code = path.read_text(encoding='utf-8-sig')
        self.assertLess(code.index('ttk_solo_guard'), code.index('main/ttk_solo_worldgen.lua'))

    def test_solo_registered_prefabs_and_assets_resolve(self):
        lua = runtime()
        lua.execute('''
            Asset = function(kind, file, param) return {type=kind, file=file, param=param} end
            RegisterInventoryItemAtlas = function() end
            AddMinimapAtlas = function() end
            dofile(root .. '/main/hh_assets.lua')
        ''')
        game_data = ROOT / '.superpowers/dst-runtime-audit/data'
        with zipfile.ZipFile(game_data / 'databundles/scripts.zip') as bundle:
            game_scripts = set(bundle.namelist())
        for prefab in lua.globals().PrefabFiles.values():
            relative = 'scripts/prefabs/' + prefab + '.lua'
            self.assertTrue((TARGET / relative).is_file() or relative in game_scripts, prefab)
        for asset in lua.globals().Assets.values():
            self.assertTrue((TARGET / asset.file).is_file() or (game_data / asset.file).is_file(), asset.file)
        for atlas in (TARGET / 'images').rglob('*.xml'):
            for texture in ET.parse(atlas).iter('Texture'):
                self.assertTrue((atlas.parent / texture.attrib['filename']).is_file(), str(atlas))

    def test_every_lua_file_compiles(self):
        lua = runtime()
        compile_file = lua.eval('function(path) local f,e=loadfile(path); return f ~= nil,e end')
        files = list(TARGET.rglob('*.lua'))
        for path in files:
            ok, error = compile_file(path.as_posix())
            self.assertTrue(ok, f'{path}: {error}')
        print(f'Compiled {len(files)} Lua files', flush=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
