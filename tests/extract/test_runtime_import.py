import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef, dump_bundle
from tools.extract.runtime_import import load_runtime_bundle
from tools.extract.runtime_runner import assert_within_workspace, run_runtime_probe
from tools.extract import cli
from tools.extract.cli import build_parser


COVERAGE_CATEGORIES = (
    "buff_debuff",
    "cooldown_recharge",
    "craft",
    "drop",
    "harvest",
    "progression",
    "start_gift",
    "trade_shop",
    "world_spawn",
)


def runtime_payload(*, recipes=None, prefabs=None, targets=None, coverage=None, errors=None, mod_version="18.0.10"):
    recipes = list(recipes or [])
    prefabs = list(prefabs or [])
    if targets is None:
        targets = sorted(
            {str(recipe["product"]).lower() for recipe in recipes}
            | {str(prefab["prefab"]).lower() for prefab in prefabs}
        )
    if coverage is None:
        coverage = [
            {
                "prefab": prefab,
                "category": category,
                "status": "unobserved",
                "reason": "fixture",
                "details": {},
            }
            for prefab in targets
            for category in COVERAGE_CATEGORIES
        ]
    return {
        "schema_version": 2,
        "mod_version": mod_version,
        "targets": list(targets),
        "recipes": recipes,
        "prefabs": prefabs,
        "coverage": coverage,
        "errors": list(errors or []),
    }


def write_static_fixture(workspace: Path, prefab_ids=("xd_test",), version="18.0.10") -> Path:
    source = SourceRef(
        "mod-static",
        "mod_static",
        "mod/3721846643/modinfo.lua",
        version,
        "a" * 64,
    )
    facts = [
        Fact(
            "entity",
            EntityKey("tu_tien", prefab_id),
            {"entity_type": "unknown", "discovered_by": "fixture"},
            source,
            1.0,
        )
        for prefab_id in prefab_ids
    ]
    path = workspace / "data/raw/mod_static.json"
    dump_bundle(path, FactBundle(1, [source], facts, []))
    return path


class RuntimeImportTests(unittest.TestCase):
    def test_ignores_explicit_non_prefab_runtime_targets(self):
        payload = runtime_payload(
            targets=["sudaji_killed", "xd_test"],
            errors=[
                {
                    "code": "prefab_inspection_failed",
                    "prefab": "sudaji_killed",
                    "detail": "SpawnPrefab returned nil",
                }
            ],
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)

        self.assertFalse(
            any(fact.subject.prefab_id == "sudaji_killed" for fact in bundle.facts)
        )
        self.assertEqual(bundle.errors, [])

    def test_recipe_ingredients_become_dependency_facts(self):
        payload = runtime_payload(
            recipes=[
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
            ]
        )
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
        payload = runtime_payload(
            prefabs=[
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
            targets=["xd_lingshi1", "xd_source"],
        )
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
        payload = runtime_payload(
            prefabs=[
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
            ]
        )
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
                        "schema_version": 99,
                        "mod_version": "18.0.10",
                        "targets": [],
                        "recipes": [],
                        "prefabs": [],
                        "coverage": [],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "schema_version"):
                load_runtime_bundle(path)

    def test_rejects_invalid_nested_runtime_shapes(self):
        payload = runtime_payload(
            recipes=[
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
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"output_count|filters"):
                load_runtime_bundle(path)

    def test_imports_dst_persistent_envelope(self):
        payload = runtime_payload()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            path.write_bytes(b"KLEI     1 " + encoded)
            bundle = load_runtime_bundle(path)
        self.assertEqual(bundle.schema_version, 1)

    def test_expected_mod_version_mismatch_hard_fails(self):
        payload = runtime_payload(mod_version="18.0.9")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError, r"runtime mod_version 18\.0\.9.*static mod version 18\.0\.10"
            ):
                load_runtime_bundle(path, expected_mod_version="18.0.10")

    def test_imports_non_xd_targets_trade_effects_and_explicit_coverage(self):
        prefab = {
            "prefab": "fence_luoshen",
            "entity_type": "structure",
            "stats": [
                {"key": "cooldown_duration", "value": 12, "unit": "seconds"}
            ],
            "effects": [
                {
                    "effect_key": "timer:shield",
                    "trigger": "timer",
                    "value": {"time_left": 4},
                    "duration": 10,
                }
            ],
            "loot": [],
            "harvest": [],
            "trade": [
                {
                    "prefab": "wall_luoshen",
                    "chance": 1,
                    "count": 1,
                    "conditions": {"cost_prefab": "fence_luoshen"},
                }
            ],
            "relations": [
                {"relation": "trades_for", "target_prefab_id": "wall_luoshen"}
            ],
        }
        payload = runtime_payload(
            prefabs=[prefab], targets=["fence_luoshen", "wall_luoshen"]
        )
        payload["coverage"][0].update(
            {"status": "observed", "reason": "timer component", "details": {"count": 1}}
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)

        self.assertTrue(
            any(
                fact.kind == "entity"
                and fact.subject == EntityKey("tu_tien", "fence_luoshen")
                for fact in bundle.facts
            )
        )
        trade = next(
            fact
            for fact in bundle.facts
            if fact.kind == "acquisition" and fact.payload["type"] == "trade"
        )
        self.assertEqual(
            trade.payload["target"],
            {
                "namespace": "tu_tien",
                "prefab_id": "wall_luoshen",
                "resolution": "resolved",
            },
        )
        effect = next(fact for fact in bundle.facts if fact.kind == "effect")
        self.assertEqual(effect.payload["duration"], 10)
        coverage = [fact for fact in bundle.facts if fact.kind == "coverage"]
        self.assertEqual(len(coverage), 2 * len(COVERAGE_CATEGORIES))
        self.assertEqual(coverage[0].source.kind, "runtime_probe")

    def test_rejects_incomplete_runtime_coverage_matrix(self):
        payload = runtime_payload(targets=["xd_test"])
        payload["coverage"].pop()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "coverage matrix"):
                load_runtime_bundle(path)

    def test_empty_lua_coverage_details_normalize_to_object(self):
        payload = runtime_payload(targets=["xd_test"])
        payload["coverage"][0]["details"] = []
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)
        row = next(
            fact
            for fact in bundle.facts
            if fact.kind == "coverage"
            and fact.payload["category"] == COVERAGE_CATEGORIES[0]
        )
        self.assertEqual(row.payload["details"], {})

    def test_observed_start_registry_becomes_start_acquisition(self):
        payload = runtime_payload(targets=["xd_start_gift"])
        start_row = next(
            row for row in payload["coverage"] if row["category"] == "start_gift"
        )
        start_row.update(
            {
                "status": "observed",
                "reason": "starting-item registry entries captured",
                "details": {
                    "count": 2,
                    "paths": [
                        "GAMEMODE_STARTING_ITEMS.DEFAULT.XD_TEST.1",
                        "GAMEMODE_STARTING_ITEMS.DEFAULT.XD_TEST.2",
                    ],
                },
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            bundle = load_runtime_bundle(path)
        acquisition = next(
            fact
            for fact in bundle.facts
            if fact.kind == "acquisition" and fact.payload["type"] == "start"
        )
        self.assertEqual(acquisition.subject, EntityKey("tu_tien", "xd_start_gift"))
        self.assertEqual(
            acquisition.payload["conditions"]["registry_paths"],
            start_row["details"]["paths"],
        )


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
        self.assertEqual(args.static, Path("data/raw/mod_static.json"))
        imported = build_parser().parse_args(
            ["import-runtime", "--input", "capture/runtime.json"]
        )
        self.assertEqual(imported.input, Path("capture/runtime.json"))
        all_args = build_parser().parse_args(
            ["all", "--static", "capture/static.json"]
        )
        self.assertEqual(all_args.static, Path("capture/static.json"))

    def test_persistent_candidate_must_be_inside_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            assert_within_workspace(workspace, workspace / "data/runtime/probe")
            with self.assertRaisesRegex(ValueError, "outside workspace"):
                assert_within_workspace(workspace, workspace.parent / "escape")

    def test_import_runtime_and_build_db_reject_stale_runtime_before_normalize(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            static_path = write_static_fixture(root, version="18.0.10")
            runtime_path = root / "runtime.json"
            runtime_path.write_text(
                json.dumps(runtime_payload(mod_version="18.0.9")), encoding="utf-8"
            )
            base_path = root / "base.json"
            dump_bundle(base_path, FactBundle(1, [], [], []))

            with self.assertRaisesRegex(ValueError, "runtime mod_version"):
                cli._import_runtime_stage(runtime_path, static_path)
            with mock.patch.object(cli, "normalize") as normalize:
                with self.assertRaisesRegex(ValueError, "runtime mod_version"):
                    cli._build_db_stage(
                        static_path, runtime_path, base_path, root / "wiki.sqlite"
                    )
                normalize.assert_not_called()

    def test_all_runtime_loading_stages_reject_same_version_target_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            static_path = write_static_fixture(
                root, prefab_ids=("xd_missing", "xd_present")
            )
            runtime_path = root / "runtime.json"
            runtime_path.write_text(
                json.dumps(runtime_payload(targets=["xd_present"])),
                encoding="utf-8",
            )
            base_path = root / "base.json"
            dump_bundle(base_path, FactBundle(1, [], [], []))

            with self.assertRaisesRegex(
                ValueError, "missing static allowlist entries.*xd_missing"
            ):
                cli._import_runtime_stage(runtime_path, static_path)

            with mock.patch.object(cli, "verify_snapshot_archive"), mock.patch.object(
                cli, "derive_dependency_requests"
            ) as requests:
                with self.assertRaisesRegex(
                    ValueError, "missing static allowlist entries.*xd_missing"
                ):
                    cli._enrich_base_stage(
                        static_path=static_path,
                        runtime_path=runtime_path,
                        scripts=root / "scripts.zip",
                        manifest=root / "manifest.json",
                        images=root / "images.zip",
                        translation=root / "translation.po",
                        output=root / "base-output.json",
                    )
                requests.assert_not_called()

            with mock.patch.object(cli, "normalize") as normalize:
                with self.assertRaisesRegex(
                    ValueError, "missing static allowlist entries.*xd_missing"
                ):
                    cli._build_db_stage(
                        static_path, runtime_path, base_path, root / "wiki.sqlite"
                    )
                normalize.assert_not_called()

    def test_all_propagates_its_static_path_to_every_runtime_loading_stage(self):
        static_path = Path("capture/static.json")
        with mock.patch.object(cli, "_extract_static_stage") as extract, mock.patch.object(
            cli, "_import_runtime_stage"
        ) as import_runtime, mock.patch.object(
            cli, "_enrich_base_stage"
        ) as enrich, mock.patch.object(
            cli, "_build_db_stage"
        ) as build, mock.patch.object(
            cli, "_import_wiki_stage"
        ) as import_wiki, mock.patch.object(
            cli, "_export_stage"
        ), mock.patch.object(
            cli, "_validate_stage", return_value={"hard_failures": []}
        ):
            cli.run_all(static_path=static_path)

        extract.assert_called_once_with(output=static_path)
        import_runtime.assert_called_once_with(static_path=static_path)
        enrich.assert_called_once_with(static_path=static_path)
        build.assert_called_once_with(static_path=static_path)
        import_wiki.assert_called_once_with()

    def test_all_stops_on_runtime_version_mismatch(self):
        mismatch = ValueError(
            "runtime mod_version 18.0.9 does not match static mod version 18.0.10"
        )
        with mock.patch.object(cli, "_extract_static_stage"), mock.patch.object(
            cli, "_import_runtime_stage", side_effect=mismatch
        ), mock.patch.object(cli, "_enrich_base_stage") as enrich, mock.patch.object(
            cli, "_build_db_stage"
        ) as build:
            with self.assertRaisesRegex(ValueError, "runtime mod_version"):
                cli.run_all()
        enrich.assert_not_called()
        build.assert_not_called()

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
            write_static_fixture(
                workspace, ("wall_luoshen", "xd_test"), version="test"
            )

            server = root / "fake-server"
            server.write_text(
                "#!/usr/bin/env python3\n"
                "import json, pathlib, re, sys\n"
                "root = pathlib.Path(sys.argv[sys.argv.index('-persistent_storage_root') + 1])\n"
                "target = root / 'probe-output' / 'runtime.json'\n"
                "target.parent.mkdir(parents=True, exist_ok=True)\n"
                "mods = pathlib.Path(__file__).parent / 'game-mods'\n"
                "probe = next(mods.glob('dst_wiki_probe_*'))\n"
                "ids = re.findall(r'\\\"([^\\\"]+)\\\"', (probe / 'scripts/target_ids.lua').read_text())\n"
                f"categories = {COVERAGE_CATEGORIES!r}\n"
                "coverage = [{'prefab': prefab, 'category': category, 'status': 'unobserved', 'reason': 'fixture', 'details': {}} for prefab in ids for category in categories]\n"
                "payload = json.dumps({'schema_version': 2, 'mod_version': 'test', 'targets': ids, 'recipes': [], 'prefabs': [], 'coverage': coverage, 'errors': []}).encode()\n"
                "target.write_bytes(b'KLEI     1 ' + payload)\n"
                "print('DST_WIKI_EXTRACT_COMPLETE', flush=True)\n",
                encoding="utf-8",
            )
            server.chmod(server.stat().st_mode | stat.S_IXUSR)

            first = run_runtime_probe(server, game_mods, workspace, timeout_seconds=10)
            second = run_runtime_probe(server, game_mods, workspace, timeout_seconds=10)

            self.assertEqual(first, (workspace / "data/raw/runtime.json").resolve())
            result = json.loads(second.read_text())
            self.assertEqual(result["schema_version"], 2)
            self.assertEqual(result["targets"], ["wall_luoshen", "xd_test"])
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
            write_static_fixture(workspace)
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
            write_static_fixture(workspace)
            server = root / "fake-server"
            server.write_text(
                "#!/usr/bin/env python3\n"
                "import json, pathlib, sys\n"
                "root = pathlib.Path(sys.argv[sys.argv.index('-persistent_storage_root') + 1])\n"
                "target = root / 'runtime.json'\n"
                f"target.write_text({json.dumps(runtime_payload(targets=['xd_test']))!r})\n"
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
            "health",
            "combat",
            "locomotor",
            "sanityaura",
            "freezable",
            "sleeper",
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
            "trader",
            "rechargeable",
            "cooldown",
            "debuff",
            "debuffable",
            "timer",
        ):
            self.assertIn(f"components.{component}", exporter)
        for stat in (
            "max_health",
            "attack_damage",
            "attack_period",
            "attack_range",
            "walk_speed",
            "run_speed",
            "sanity_aura",
            "freeze_resistance",
            "sleep_resistance",
            "special_states",
        ):
            self.assertIn(f'"{stat}"', exporter)
        self.assertIn('require("target_ids")', exporter)
        self.assertIn("TUNING.GAMEMODE_STARTING_ITEMS", exporter)
        self.assertIn('category = "world_spawn"', exporter)
        self.assertIn('status = "unsupported"', exporter)
        self.assertNotIn("timer_data.initial_time", exporter)
        self.assertNotIn("timer_data.timeleft", exporter)
        self.assertIn("runtime timer state is instance-specific", exporter)
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
