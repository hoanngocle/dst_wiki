import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.extract.contracts import EntityKey
from tools.extract.runtime_import import load_runtime_bundle
from tools.extract.runtime_runner import assert_within_workspace, run_runtime_probe
from tools.extract.cli import build_parser


class RuntimeImportTests(unittest.TestCase):
    def test_recipe_ingredients_become_dependency_facts(self):
        payload = {
            "schema_version": 1,
            "mod_version": "18.0.10",
            "recipes": [
                {
                    "product": "xd_test_sword",
                    "ingredients": [
                        {
                            "group": "item",
                            "type": "goldnugget",
                            "prefab": "goldnugget",
                            "amount": 2,
                        }
                    ],
                    "character_ingredients": [
                        {"group": "character", "type": "health", "amount": 10}
                    ],
                    "tech_ingredients": [
                        {"group": "tech", "type": "lunar", "amount": 1}
                    ],
                    "tech": "SCIENCE_ONE",
                    "filters": [],
                    "builder_tags": [],
                    "output_count": 1,
                }
            ],
            "prefabs": [],
            "errors": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)
        ingredient = next(fact for fact in bundle.facts if fact.kind == "ingredient")
        self.assertEqual(
            sum(fact.kind == "ingredient" for fact in bundle.facts),
            1,
            "character and tech costs must not become item dependency facts",
        )
        self.assertEqual(
            ingredient.payload["ingredient"],
            {
                "prefab_id": "goldnugget",
                "dependency_candidate": True,
                "resolution": "unresolved",
            },
        )
        self.assertEqual(ingredient.confidence, 1.0)
        discovered = next(fact for fact in bundle.facts if fact.kind == "entity")
        self.assertEqual(discovered.payload["entity_type"], "unknown")
        self.assertEqual(discovered.confidence, 0.9)
        recipe = next(fact for fact in bundle.facts if fact.kind == "recipe")
        self.assertEqual(
            recipe.payload["character_ingredients"],
            [{"group": "character", "type": "health", "amount": 10}],
        )
        self.assertEqual(
            recipe.payload["tech_ingredients"],
            [{"group": "tech", "type": "lunar", "amount": 1}],
        )

    def test_runtime_references_remain_unresolved_until_base_game_enrichment(self):
        payload = {
            "schema_version": 1,
            "mod_version": "18.0.10",
            "recipes": [],
            "prefabs": [
                {
                    "prefab": "xd_source",
                    "entity_type": "creature",
                    "stats": [],
                    "loot": [{"prefab": "silk", "chance": 1, "count": 1}],
                    "harvest": [
                        {"prefab": "xd_lingshi1", "chance": 1, "count": 1}
                    ],
                    "relations": [
                        {"relation": "transforms_to", "target_prefab_id": "nightmarefuel"}
                    ],
                }
            ],
            "errors": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)

        self.assertFalse(
            any(fact.subject.namespace == "base_game" for fact in bundle.facts)
        )
        silk = next(
            fact
            for fact in bundle.facts
            if fact.kind == "acquisition"
            and fact.payload.get("target", {}).get("prefab_id") == "silk"
        )
        self.assertEqual(silk.subject, EntityKey("tu_tien", "xd_source"))
        self.assertEqual(
            silk.payload["target"],
            {
                "prefab_id": "silk",
                "dependency_candidate": True,
                "resolution": "unresolved",
            },
        )
        harvest = next(
            fact
            for fact in bundle.facts
            if fact.kind == "acquisition"
            and fact.payload.get("target", {}).get("prefab_id") == "xd_lingshi1"
        )
        self.assertEqual(
            harvest.payload["target"],
            {
                "namespace": "tu_tien",
                "prefab_id": "xd_lingshi1",
                "resolution": "resolved",
            },
        )
        relation = next(fact for fact in bundle.facts if fact.kind == "relation")
        self.assertEqual(relation.payload["target"]["resolution"], "unresolved")
        self.assertNotIn("target_namespace", relation.payload)

    def test_empty_runtime_conditions_normalize_to_an_object(self):
        payload = {
            "schema_version": 1,
            "mod_version": "18.0.10",
            "recipes": [],
            "prefabs": [
                {
                    "prefab": "xd_source",
                    "stats": [],
                    "loot": [
                        {
                            "prefab": "goldnugget",
                            "chance": 1,
                            "count": 1,
                            "conditions": [],
                        }
                    ],
                    "harvest": [],
                    "relations": [],
                }
            ],
            "errors": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)
        acquisition = next(
            fact for fact in bundle.facts if fact.kind == "acquisition"
        )
        self.assertEqual(acquisition.payload["conditions"], {})

    def test_fixture_imports_recipe_and_prefab_stats_deterministically(self):
        bundle = load_runtime_bundle(Path("tests/extract/fixtures/runtime.json"))
        self.assertEqual(bundle.schema_version, 1)
        self.assertEqual({source.source_id for source in bundle.sources}, {"runtime-probe"})
        self.assertEqual(
            [(fact.kind, fact.subject.namespace, fact.subject.prefab_id) for fact in bundle.facts],
            sorted(
                (fact.kind, fact.subject.namespace, fact.subject.prefab_id)
                for fact in bundle.facts
            ),
        )
        damage = next(fact for fact in bundle.facts if fact.kind == "stat")
        self.assertEqual(damage.payload, {"key": "damage", "unit": "hp", "value": 68})

    def test_rejects_invalid_runtime_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "mod_version": "18.0.10",
                        "recipes": [],
                        "prefabs": [],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "schema_version"):
                load_runtime_bundle(path)

    def test_rejects_invalid_nested_runtime_shapes(self):
        payload = {
            "schema_version": 1,
            "mod_version": "18.0.10",
            "recipes": [
                {
                    "product": "xd_bad",
                    "ingredients": [
                        {
                            "group": "item",
                            "type": "goldnugget",
                            "prefab": "goldnugget",
                            "amount": 1,
                        }
                    ],
                    "character_ingredients": [],
                    "tech_ingredients": [],
                    "tech": "SCIENCE_ONE",
                    "filters": "not-an-array",
                    "builder_tags": [],
                    "output_count": True,
                }
            ],
            "prefabs": [],
            "errors": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"output_count|filters"):
                load_runtime_bundle(path)

    def test_imports_dst_persistent_envelope(self):
        payload = {
            "schema_version": 1,
            "mod_version": "18.0.10",
            "recipes": [],
            "prefabs": [],
            "errors": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            path.write_bytes(b"KLEI     1 " + encoded)
            bundle = load_runtime_bundle(path)
        self.assertEqual(bundle.schema_version, 1)


class RuntimeRunnerTests(unittest.TestCase):
    def test_runtime_cli_accepts_explicit_isolation_arguments(self):
        args = build_parser().parse_args(
            [
                "run-runtime",
                "--server-bin",
                "/game/server",
                "--game-mods-dir",
                "/game/mods",
                "--workspace",
                "/workspace",
                "--timeout",
                "45",
            ]
        )
        self.assertEqual(args.timeout, 45)
        imported = build_parser().parse_args(
            ["import-runtime", "--input", "capture/runtime.json"]
        )
        self.assertEqual(imported.input, Path("capture/runtime.json"))

    def test_persistent_candidate_must_be_inside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            assert_within_workspace(workspace, workspace / "data/runtime/probe")
            with self.assertRaisesRegex(ValueError, "outside workspace"):
                assert_within_workspace(workspace, workspace.parent / "escape")

    def test_runner_copies_mods_uses_unique_root_and_cleans_only_own_mods(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            game_mods = root / "game-mods"
            game_mods.mkdir()
            (game_mods / "keep-me").mkdir()
            (workspace / "mod/3721846643").mkdir(parents=True)
            (workspace / "mod/3721846643/modinfo.lua").write_text("version='test'\n")
            (workspace / "tools/runtime_mod").mkdir(parents=True)
            (workspace / "tools/runtime_mod/modinfo.lua").write_text("version='test'\n")

            server = root / "fake-server"
            server.write_text(
                "#!/usr/bin/env python3\n"
                "import json, pathlib, sys\n"
                "root = pathlib.Path(sys.argv[sys.argv.index('-persistent_storage_root') + 1])\n"
                "target = root / 'probe-output' / 'runtime.json'\n"
                "target.parent.mkdir(parents=True, exist_ok=True)\n"
                "payload = json.dumps({'schema_version': 1, 'mod_version': 'test', 'recipes': [], 'prefabs': [], 'errors': []}).encode()\n"
                "target.write_bytes(b'KLEI     1 ' + payload)\n"
                "print('DST_WIKI_EXTRACT_COMPLETE', flush=True)\n",
                encoding="utf-8",
            )
            server.chmod(server.stat().st_mode | stat.S_IXUSR)

            first = run_runtime_probe(server, game_mods, workspace, timeout_seconds=10)
            second = run_runtime_probe(server, game_mods, workspace, timeout_seconds=10)

            self.assertEqual(first, (workspace / "data/raw/runtime.json").resolve())
            self.assertEqual(json.loads(second.read_text())["schema_version"], 1)
            self.assertTrue((game_mods / "keep-me").is_dir())
            self.assertEqual(
                sorted(path.name for path in game_mods.iterdir()), ["keep-me"]
            )
            roots = sorted((workspace / "data/runtime").glob("probe-*"))
            self.assertEqual(len(roots), 2)
            self.assertNotEqual(roots[0].name, roots[1].name)
            self.assertTrue(all((path / "server.log").is_file() for path in roots))

    def test_runner_cleans_a_partially_copied_owned_mod(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            game_mods = root / "game-mods"
            game_mods.mkdir()
            (game_mods / "keep-me").mkdir()
            (workspace / "mod/3721846643").mkdir(parents=True)
            (workspace / "tools/runtime_mod").mkdir(parents=True)
            server = root / "server"
            server.write_text("not executed", encoding="utf-8")

            def fail_after_creating_target(source, target, symlinks):
                target.mkdir()
                (target / "partial").write_text("partial", encoding="utf-8")
                raise OSError("copy failed")

            with mock.patch(
                "tools.extract.runtime_runner.shutil.copytree",
                side_effect=fail_after_creating_target,
            ):
                with self.assertRaisesRegex(OSError, "copy failed"):
                    run_runtime_probe(server, game_mods, workspace, timeout_seconds=1)

            self.assertEqual(
                sorted(path.name for path in game_mods.iterdir()), ["keep-me"]
            )

    def test_runner_removes_owned_publish_temp_when_validation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "workspace"
            game_mods = root / "game-mods"
            game_mods.mkdir()
            (workspace / "mod/3721846643").mkdir(parents=True)
            (workspace / "tools/runtime_mod").mkdir(parents=True)
            server = root / "fake-server"
            server.write_text(
                "#!/usr/bin/env python3\n"
                "import json, pathlib, sys\n"
                "root = pathlib.Path(sys.argv[sys.argv.index('-persistent_storage_root') + 1])\n"
                "target = root / 'runtime.json'\n"
                "target.write_text(json.dumps({'schema_version': 1, 'mod_version': 'test', 'recipes': [], 'prefabs': [], 'errors': []}))\n"
                "print('DST_WIKI_EXTRACT_COMPLETE', flush=True)\n",
                encoding="utf-8",
            )
            server.chmod(server.stat().st_mode | stat.S_IXUSR)

            with mock.patch(
                "tools.extract.runtime_runner.read_runtime_json_bytes",
                return_value=b"not-json",
            ):
                with self.assertRaisesRegex(ValueError, "invalid runtime JSON"):
                    run_runtime_probe(server, game_mods, workspace, timeout_seconds=10)

            self.assertEqual(list((workspace / "data/raw").glob(".*.tmp")), [])


class RuntimeLuaContractTests(unittest.TestCase):
    def test_probe_declares_server_mod_and_per_prefab_isolation(self):
        modinfo = Path("tools/runtime_mod/modinfo.lua").read_text(encoding="utf-8")
        modmain = Path("tools/runtime_mod/modmain.lua").read_text(encoding="utf-8")
        exporter = Path("tools/runtime_mod/scripts/exporter.lua").read_text(
            encoding="utf-8"
        )

        self.assertIn("client_only_mod = false", modinfo)
        self.assertIn("priority = -1000", modinfo)
        self.assertIn("AddSimPostInit", modmain)
        self.assertIn('AddPrefabPostInit("world"', modmain)
        self.assertIn("RunOnce", modmain)
        self.assertIn("TheWorld.ismastersim", modmain)
        self.assertIn("pcall(SpawnAndInspect", exporter)
        self.assertIn("SpawnPrefab", exporter)
        for component in (
            "weapon",
            "armor",
            "finiteuses",
            "edible",
            "perishable",
            "lootdropper",
            "pickable",
            "tradable",
            "stackable",
            "container",
        ):
            self.assertIn(f"components.{component}", exporter)
        self.assertIn("local function SanitizeError", exporter)
        self.assertIn('recipe.character_ingredients', exporter)
        self.assertIn('recipe.tech_ingredients', exporter)
        self.assertIn('group = "character"', exporter)
        self.assertIn('group = "tech"', exporter)
        self.assertIn(
            'if value_type == "string" or value_type == "boolean" then',
            exporter,
        )
        self.assertIn('gsub("dst_wiki_probe_[0-9a-f]+"', exporter)
        self.assertIn('gsub("dst_wiki_core_[0-9a-f]+"', exporter)
        self.assertEqual(exporter.count("DST_WIKI_EXTRACT_COMPLETE"), 1)
        self.assertIn('TheSim:SetPersistentString("runtime.json"', exporter)


if __name__ == "__main__":
    unittest.main()
