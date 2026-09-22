"""Executable integration contracts using DST-compatible Lua 5.1."""
import hashlib
import json
import os
import importlib.util
import io
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ('.superpowers/solo-combat-audit/lua-runtime'
                             if sys.version_info[:2] == (3, 12)
                             else '.superpowers/ttk-solo-integration/lua-runtime')))
from lupa.lua51 import LuaRuntime

TARGET = ROOT / 'mods/PhamNhanTuTien'
SOURCE = ROOT / 'mods/3780347550'
BASELINE = ROOT / '.superpowers/ttk-solo-integration/baseline.json'

# Closed, byte-pinned overlays that predate the combat work. These preserve
# already-approved integration/UI/art updates, not arbitrary source drift.
INTEGRATION_OVERLAYS = {
    'anim/igris_dungeon.zip': 'c89b8ee01145ffe3bec468e7a619dc8728fc5308bc6cad11b426f4843fafdea6',
    'anim/lo_ren.zip': '02fd23f5a02b48812a6938f1540c393192d8fde61291789c518ab97a8197e190',
    'images/lo_ren.tex': 'a589c69975251bc68e4db4d24d5f3173e50e666826a62b565deae2ff50f68114',
    'images/lo_ren.xml': '09892ba31c43f388ac04033c2da0a491927786354cf8feb38e9c127458151b1b',
    'main/hh_dungeon_shop.lua': '3e9d4371c89383e37be0842be6d6b21ad04042b4eda1a9ade583a3726d128f71',
    'main/hh_guild_main.lua': '5e453c539d951ae58c89458bab76fdc871cbda6c302f8407278d888c88abced0',
    'main/hh_guild_rpc.lua': '889b772991720b6dc9ae7e8905098e4495b0ac641a5b9d773b682612d14d4aac',
    'main/hh_recipe.lua': '265afa505c626440bb40fe46d4a6d99e4a8d0ef7e022b7ffbc752991f27c4cab',
    'main/hh_rpc.lua': 'e10adf281b06c5a27424ec9ad19e50e894cc0d19ae2dbecb250c10d68fb4dd6b',
    'main/hh_ui.lua': 'f969ac3aad1cacaa2754939e1e9b539d8a1ef26f1d0ed418e176b77d5e523097',
    'main/ttk_solo_source.lua': 'b07af708d3e124964716eab0310730134d000b984626b44907cc552054a91d46',
    'scripts/components/hh_mana.lua': 'f4fcc20fe0eb07882ac648d6335bcc4cc2af9afd6d1c6c27a2899cd29d47483b',
    'scripts/components/hh_rank.lua': 'e036c68500b6f2232516c82a8f727abfe33ea8e6c8c45efaf3ab87e6fe372a8a',
    'scripts/components/hh_shadow_manager.lua': '1998b6aa37b6e1e214683cacbfcf0d6b297255d2b6c39b5de364fd2eb6172ba7',
    'scripts/dungeon_shop/hh_dungeon_shop_defs.lua': 'fe7decc291b066d9ce2453f24bcd45f514d07b04463efb254fea185b18a986d8',
    'scripts/enums/hh_boss.lua': 'c7f33ae3fc5cef692cc464b960ae6cc0ef7d168128c644c1e08766505158e40f',
    'scripts/prefabs/hh_fx.lua': 'faed6bf5d2a5cea5143b0d9bb1171adabac3e5a1479ee9a463bbff673f7c00a4',
    'scripts/prefabs/hh_lo_ren.lua': '30678b90c222741ab9e9da2eb04b5872c7390398c78da967b4e4c8fd532a86d4',
    'scripts/prefabs/hh_prefabs.lua': '82dfb40dc78039ec0c408bdcb1fcf071f5b1a345b15dc656096c217788b372ce',
    'scripts/prefabs/hh_shadows.lua': '3f70c25e3ad1a902ca8332d61a919182653e04a1096d2a0560df0dfde4c41b80',
    'scripts/prefabs/wb_strengthen_levelpaper.lua': '4b125ba79d4c856dae71bacd551be6181ce3338f28f3cbab755551a25f8a54c2',
    'scripts/screens/hh_dungeon_shop_screen.lua': '1a5337f6a48084fc082ae850477b57d8098624a5532d8e4a087929214a090c86',
    'scripts/screens/hh_shadow_upgrade_screen.lua': '9337a7296c801d65723105d3dd836c6b9ccfa60586054222c0a6bd29c94d13ce',
    'scripts/widgets/hh_guild_ui.lua': '404748f7196a6d4e7c768c8bcd97430f8a9d9fd7fc49c6dd140ac8bcd612b242',
    'scripts/widgets/hh_hoverer.lua': '56fbdd080d29d3b923baf68a4a99113e0c40b6754edd0ab896df8f0369a724c7',
    'scripts/widgets/hh_shadow_ui.lua': '3ef6377d2036d45ee9c19cab90bf5741a4c701ed740b7184d229c4f3a4f7e21f',
    'scripts/widgets/hh_status_ui.lua': '36144c28b60ed092fc8af4ba9044e1605aa1e0e24001521aeeadba42fae2ed04',
    'scripts/widgets/hh_ui/hh_equip_ui.lua': '5a2a55a5dfa86350c0837748d71492c25b4e6eca73b5dd1b11a466941f2fdc1a',
    'scripts/widgets/hh_ui/hh_forge_ui.lua': 'c8b6d963ae45b35282c23d225437375c9b69e8d726c877e1aa37fb7abf46041b',
}
# Approved Mục 2 overlays only. New combat modules are exercised by the suites
# below and every Lua file is compiled; historical source hashes stay strict.
COMBAT_OVERLAYS = {
    'Wiki.txt': '08d1ee7ad9e4770152db4da90eb5c70fc97eb9dd6c293caaa49c74eb453e1d8b',
    'main/hh_api.lua': '2ace97ef4727fac788066545f0f16d76b2130498d8c38d304f1b93c1db398b41',
    'main/hh_string.lua': 'c38aee5fe502aece929111a86c7aa78da5e314e17a4e9a6b80d29754104b12f8',
    'main/hh_tunning.lua': 'bfd6986f32dd7d68d19d5896e3c742c8ef6200b7e95e1c6888188b8e2dc5ab37',
    'scripts/components/hh_dungeon_effects.lua': 'b1280806e84440b0552126522d6cdf12d13e261f27f8582eb85021a55c4e9cae',
    'scripts/components/hh_equip.lua': '1782df62d56194feb9737a61301ff060771c3b653c93747e486d2e6359aedf8e',
    'scripts/components/hh_leveling.lua': '75299ad5450b555bd98ce1467e21c24283cc365fdc0ee304357c0d64901be60b',
    'scripts/components/hh_monster.lua': 'a8420033ba9230349e9720529e2c8c3e42eabfe154116ea27b29b49697c7be49',
    'scripts/components/hh_player.lua': 'cde3931baa5fcfd1a4b0c8266b37072eddf0d5218e33d20cbf2b5787d50008a9',
    # Existing strengthening integration plus the approved Task 5 reflect removal.
    'scripts/components/wb_strengthen.lua': 'dfd18cae2adf056ff09d283f238e554b1e027d35ee09e0c11dae212c75eeadae',
    'scripts/enums/hh_buff.lua': '34e7a50c308c2a1883a46180bd25ace435e661ffe2f898a52adb6a7cab50c698',
    'scripts/enums/hh_effects.lua': '9471553d67a4e749ac2a293913a87c7bcebcc99e5ac60505d9dd63c4be6655fd',
    'scripts/enums/hh_enchant.lua': '77bac9b84311edb3ea6a74956a0e34ec792d4bfad901a1798768e6173aca221b',
    'scripts/enums/hh_equip.lua': 'f1a4db3ea48de70df2e745d809c5728e6e5e03c6d65151363838d2cbcba59fdb',
    'scripts/enums/hh_items.lua': 'f7dc8e4b0920c2fec9d38fba330282c4a1f94408ffa7d099c22a8ffda9f61990',
    'scripts/enums/hh_monster.lua': 'd26199c240d8e86d70930c66a7f3e6ec4e949eda113d68edea3de7aaa0d919ae',
    'scripts/enums/hh_treasure_monster.lua': '93154dd335de48d77f2b5352afd28b0402bc9f30af43bd33216d75c526e76607',
    'scripts/utils/hh_utils.lua': '9c13d224e6fb5915008f6f32d1e0a4eea7153abe0625ee6d32f4b5ea68d587b5',
}
SOURCE_TREE_DIGESTS = {
    '3780347550': (660, '5eea2e2e3cadd715e8d17265802cae0f8cd86edebd69e786cc67b40e84f8c3c6'),
    '2937640068': (2006, 'e6ea984c655a2fd57902144dff7ed4a5a563ab5044a2eda32cf56a71bbde53e5'),
    'AchievementLevel': (2012, '707e4663c09f11522c7d6e0e0d70486d8f54491663277f603fa2157aa6e1e89b'),
}


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.globals().root = TARGET.as_posix()
    lua.execute("package.path = root .. '/scripts/?.lua;' .. package.path")
    return lua


def metadata(lua, path):
    return lua.eval('function(path) local e = {}; setfenv(assert(loadfile(path)), e)(); return e end')(path.as_posix())


class CombatSmokeRunnerTests(unittest.TestCase):
    def runner(self):
        path = ROOT / 'tools/run_phamnhan_combat_smoke.py'
        self.assertTrue(path.is_file(), 'isolated combat acceptance runner is missing')
        spec = importlib.util.spec_from_file_location('combat_smoke_runner', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_console_payload_executes_complete_unicode_source(self):
        runner = self.runner()
        lua = runtime()
        source = 'result = "Phàm Nhân"\n' + ('-- bounded console input\n' * 500) + 'result = result .. " complete"'
        lines = runner.console_payload(source).splitlines()
        self.assertGreater(len(lines), 2)
        self.assertLess(max(len(line) for line in lines), 4000)
        for line in lines:
            lua.execute(line)
        self.assertEqual('Phàm Nhân complete', lua.globals().result)

    def test_echo_and_error_cannot_masquerade_as_runtime_pass(self):
        runner = self.runner()
        self.assertIsNone(runner.log_result('RemoteCommandInput: print("PHAM_NHAN_COMBAT_SMOKE_PASS")'))
        self.assertEqual('pass', runner.log_result('[00:01] PHAM_NHAN_COMBAT_SMOKE_PASS'))
        self.assertEqual('fail', runner.log_result('PHAM_NHAN_COMBAT_SMOKE_PASS\nLUA ERROR boom'))
        self.assertEqual('fail', runner.log_result('PHAM_NHAN_COMBAT_SMOKE_FAIL assertion'))

    def test_runtime_preflight_refuses_missing_binary_before_copy(self):
        runner = self.runner()
        folder = ROOT / '.superpowers/combat-missing-runtime-fixture'
        self.assertFalse(folder.exists())
        with self.assertRaisesRegex(FileNotFoundError, 'dedicated-server'):
            runner.validate_seed(folder)

    def test_shutdown_stops_a_process_that_ignores_console(self):
        runner = self.runner()
        import subprocess
        process = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],
                                   stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        try:
            runner.stop_server(process, timeout=.05)
            self.assertIsNotNone(process.poll(), 'smoke left its owned child alive')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


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
        # These options were deliberately fixed/removed by the existing Solo UI
        # and Blink work; every retained historical option still keeps its default.
        retired = {'hoverer_text', 'hoverer_effect', 'teleport_hotkey',
                   'can_show_text_fx', 'equip', 'announcement'}
        for data in (before, source):
            for row in data.configuration_options.values():
                if row.name in retired:
                    self.assertNotIn(row.name, actual)
                    continue
                self.assertIn(row.name, actual)
                self.assertEqual(row.default, actual[row.name])
        self.assertEqual('Phàm Nhân Tu Tiên', target.name)
        self.assertRegex(target.version, r'^2\.0(?:\.\d+)?$')
        self.assertTrue(target.all_clients_require_mod)

    def test_all_solo_files_preserved_and_source_unchanged(self):
        manifest = TARGET / 'SOLO_SOURCE_MANIFEST.json'
        self.assertTrue(manifest.exists(), 'Source manifest is missing')
        data = json.loads(manifest.read_text(encoding='utf-8'))
        baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
        self.assertEqual(set(baseline['source']), {r['source'] for r in data['files']})
        overlays = {**INTEGRATION_OVERLAYS, **COMBAT_OVERLAYS}
        self.assertFalse(set(INTEGRATION_OVERLAYS) & set(COMBAT_OVERLAYS))
        self.assertTrue(set(overlays) <= {r['destination'] for r in data['files']})
        for row in data['files']:
            original = hashlib.sha256((SOURCE / row['source']).read_bytes()).hexdigest()
            with self.subTest(source=row['source']):
                self.assertEqual(baseline['source'][row['source']], original, row['source'])
                self.assertEqual(original, row['sha256'])
            # Continue every destination assertion even if historical provenance
            # has already failed. A source mismatch remains a real test failure.
            with self.subTest(destination=row['destination']):
                if row['destination'] == 'scripts/widgets/hh_help_ui.lua':
                    self.assertFalse((TARGET / row['destination']).exists())
                    replacement = TARGET / 'scripts/screens/ttk_unified_screen.lua'
                    self.assertEqual('cb6d5763dfa352d10470a913dd596c9da90ef71329e95fc65b7e4fabb1971d0b',
                                     hashlib.sha256(replacement.read_bytes()).hexdigest())
                    continue
                destination = hashlib.sha256((TARGET / row['destination']).read_bytes()).hexdigest()
                self.assertEqual(overlays.get(row['destination'], original), destination, row['destination'])

    def test_all_historical_source_trees_remain_unchanged(self):
        for name, (count, expected) in SOURCE_TREE_DIGESTS.items():
            with self.subTest(source=name):
                source = ROOT / 'mods' / name
                files = {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in sorted(source.rglob('*')) if path.is_file()}
                self.assertEqual(count, len(files))
                self.assertEqual(expected, hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest())

    def test_combat_suites_exercise_runtime_and_public_catalog(self):
        sys.path.insert(0, str(TARGET / 'tools'))
        for name in ('test_combat_math', 'test_combat_pipeline', 'test_combat_status', 'test_combat_catalog'):
            with self.subTest(suite=name):
                module = __import__(name)
                output = io.StringIO()
                result = unittest.TextTestRunner(stream=output).run(unittest.defaultTestLoader.loadTestsFromModule(module))
                self.assertTrue(result.wasSuccessful(), output.getvalue())
                print(f'{name}: {result.testsRun} passed', flush=True)

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
