import tempfile
import unittest
import hashlib
import json
from pathlib import Path
from unittest import mock
from zipfile import ZipFile

from tools.extract.base_game import (
    DependencyRequest,
    derive_dependency_requests,
    enrich_dependencies,
    verify_snapshot_archive,
)
from tools.extract.cli import build_parser, main
from tools.extract.contracts import (
    EntityKey,
    Fact,
    FactBundle,
    SourceRef,
    dump_bundle,
)


class BaseGameTests(unittest.TestCase):
    def _archive(self, root, members):
        archive = root / "scripts.zip"
        with ZipFile(archive, "w") as handle:
            for name, source in members.items():
                handle.writestr(name, source)
        return archive

    def test_enriches_requested_item_without_unrelated_prefabs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "scripts.zip"
            po = root / "viethoa.po"
            po.write_text(
                'msgctxt "STRINGS.NAMES.GOLDNUGGET"\n'
                'msgid "Gold Nugget"\n'
                'msgstr "Vàng"\n',
                encoding="utf-8",
            )
            with ZipFile(archive, "w") as handle:
                handle.writestr(
                    "scripts/prefabs/goldnugget.lua",
                    'return Prefab("goldnugget", fn)',
                )
                handle.writestr(
                    "scripts/prefabs/pickaxe.lua", 'return Prefab("pickaxe", fn)'
                )
                handle.writestr(
                    "scripts/strings.lua",
                    'STRINGS.NAMES.GOLDNUGGET = "Gold Nugget"',
                )
                handle.writestr("scripts/recipes.lua", "")

            requests = [
                DependencyRequest(
                    "goldnugget", "ingredient", "tu_tien:xd_test_sword"
                )
            ]
            bundle = enrich_dependencies(archive, requests, po)

        ids = {
            fact.subject.prefab_id
            for fact in bundle.facts
            if fact.kind == "entity"
        }
        self.assertIn("goldnugget", ids)
        self.assertNotIn("pickaxe", ids)
        self.assertTrue(
            any(
                fact.kind == "name"
                and fact.subject.prefab_id == "goldnugget"
                and fact.payload["lang"] == "en"
                for fact in bundle.facts
            )
        )
        entity = next(fact for fact in bundle.facts if fact.kind == "entity")
        self.assertEqual(
            entity.payload["requested_by"],
            [
                {
                    "relation": "ingredient",
                    "subject": "tu_tien:xd_test_sword",
                }
            ],
        )

    def test_recipe_closure_is_exactly_one_level_and_string_aware(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": """
Recipe2(
    "pickaxe",
    {Ingredient("twigs", 2), Ingredient("flint", TUNING.ROCK_COST)},
    TECH.NONE,
    {description = ") } not syntax", numtogive = 1}
)
Recipe2("twigs", {Ingredient("cutgrass", 3)}, TECH.NONE)
""",
                    "scripts/strings.lua": """
STRINGS = {
  NAMES = {
    PICKAXE = "Pickaxe",
    TWIGS = "Twigs",
    FLINT = "Flint",
    CUTGRASS = "Grass",
  },
  DESCRIBE = { PICKAXE = "wrong table" },
}
""",
                    "scripts/prefabs/tools.lua": 'return Prefab("pickaxe", fn)',
                    "scripts/prefabs/twigs.lua": 'return Prefab("twigs", fn)',
                    "scripts/prefabs/flint.lua": 'return Prefab("flint", fn)',
                    "scripts/prefabs/cutgrass.lua": 'return Prefab("cutgrass", fn)',
                },
            )
            bundle = enrich_dependencies(
                archive,
                [DependencyRequest("pickaxe", "ingredient", "tu_tien:xd_tool")],
                root / "missing.po",
            )

        entities = {
            fact.subject.prefab_id
            for fact in bundle.facts
            if fact.kind == "entity"
        }
        self.assertEqual(entities, {"pickaxe", "twigs", "flint"})
        recipe = next(
            fact
            for fact in bundle.facts
            if fact.kind == "recipe" and fact.subject.prefab_id == "pickaxe"
        )
        self.assertEqual(recipe.payload["tech_expression"], "TECH.NONE")
        self.assertEqual(recipe.payload["output_count"], 1)
        ingredient = next(
            fact
            for fact in bundle.facts
            if fact.kind == "ingredient"
            and fact.payload["ingredient"]["prefab_id"] == "flint"
        )
        self.assertEqual(ingredient.payload["amount_expression"], "TUNING.ROCK_COST")
        self.assertNotIn("amount", ingredient.payload)
        twig_entity = next(
            fact
            for fact in bundle.facts
            if fact.kind == "entity" and fact.subject.prefab_id == "twigs"
        )
        self.assertEqual(
            twig_entity.payload["requested_by"],
            [
                {
                    "relation": "recipe_ingredient",
                    "subject": "base_game:pickaxe",
                    "root_requested_by": "tu_tien:xd_tool",
                    "root_evidence": {
                        "relation": "ingredient",
                        "subject": "tu_tien:xd_tool",
                    },
                }
            ],
        )
        pickaxe_name = next(
            fact
            for fact in bundle.facts
            if fact.kind == "name"
            and fact.subject.prefab_id == "pickaxe"
            and fact.payload["lang"] == "en"
        )
        self.assertEqual(pickaxe_name.payload["value"], "Pickaxe")

    def test_resolves_only_exact_registry_entries_and_reports_unresolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": 'Recipe2("recipe_only", {}, TECH.NONE)',
                    "scripts/strings.lua": 'STRINGS.NAMES.STRING_ONLY = "String Only"',
                    "scripts/prefabs/group.lua": 'return Prefab("declared_only", fn)',
                },
            )
            bundle = enrich_dependencies(
                archive,
                [
                    DependencyRequest("declared_only", "relation", "tu_tien:a"),
                    DependencyRequest("recipe_only", "ingredient", "tu_tien:b"),
                    DependencyRequest("string_only", "loot", "tu_tien:c"),
                    DependencyRequest("string", "loot", "tu_tien:d"),
                    DependencyRequest("missing", "loot", "tu_tien:e"),
                ],
                root / "missing.po",
            )

        entities = {
            fact.subject.prefab_id
            for fact in bundle.facts
            if fact.kind == "entity"
        }
        self.assertEqual(
            entities, {"declared_only", "recipe_only", "string_only"}
        )
        unresolved = {
            error["prefab_id"]
            for error in bundle.errors
            if error["code"] == "unresolved_base_game_dependency"
        }
        self.assertEqual(unresolved, {"string", "missing"})

    def test_extracts_common_stats_and_acquisition_with_source_expressions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": "",
                    "scripts/strings.lua": """
-- NAMES = { WRONG = "Comment must not become a registry" }
STRINGS.NAMES.TESTITEM = "Test Item"
""",
                    "scripts/prefabs/testitem.lua": """
local function fn()
  inst.components.weapon:SetDamage(TUNING.TEST_DAMAGE)
  inst.components.armor:InitCondition(100, TUNING.TEST_ABSORPTION)
  inst.components.finiteuses:SetMaxUses(25)
  inst.components.edible.healthvalue = -3
  inst.components.edible.hungervalue = TUNING.TEST_HUNGER
  inst.components.edible.sanityvalue = 2.5
  inst.components.lootdropper:SetLoot({"silk", "silk"})
  inst.components.lootdropper:AddChanceLoot("nightmarefuel", 0.25)
  inst.components.pickable:SetUp("twigs", TUNING.REGROW_TIME)
  inst.components.uses:SetUp("not_pickable", 99)
end
return Prefab("testitem", fn)
""",
                },
            )
            bundle = enrich_dependencies(
                archive,
                [DependencyRequest("testitem", "relation", "tu_tien:xd_test")],
                root / "missing.po",
            )

        stats = {
            fact.payload["key"]: fact.payload
            for fact in bundle.facts
            if fact.kind == "stat"
        }
        self.assertEqual(stats["damage"]["source_expression"], "TUNING.TEST_DAMAGE")
        self.assertNotIn("value", stats["damage"])
        self.assertEqual(stats["armor_condition"]["value"], 100)
        self.assertEqual(stats["max_uses"]["value"], 25)
        self.assertEqual(stats["health"]["value"], -3)
        self.assertEqual(stats["sanity"]["value"], 2.5)
        self.assertTrue(
            all("line:" in fact.locator for fact in bundle.facts if fact.kind == "stat")
        )

    def test_commented_string_table_does_not_resolve_an_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": "",
                    "scripts/strings.lua": """
-- NAMES = { COMMENT_ONLY = "Not evidence" }
STRINGS = { NAMES = { REAL = "Real" } }
""",
                },
            )
            bundle = enrich_dependencies(
                archive,
                [DependencyRequest("comment_only", "relation", "tu_tien:xd_test")],
                root / "missing.po",
            )
        self.assertFalse(any(fact.kind == "entity" for fact in bundle.facts))
        self.assertEqual(
            [error["prefab_id"] for error in bundle.errors], ["comment_only"]
        )

    def test_binds_stats_to_the_declared_constructor_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": "",
                    "scripts/strings.lua": "",
                    "scripts/prefabs/shared.lua": """
local function goldfn()
  inst.components.weapon:SetDamage(10)
  return inst
end
local function luckyfn()
  inst.components.weapon:SetDamage(99)
  return inst
end
local function cookedfn()
  inst.components.edible.hungervalue = 5
  return inst
end
return Prefab("gold", goldfn),
       Prefab("lucky_gold", luckyfn),
       Prefab("cookedmeat", cookedfn),
       Prefab("wrapped", MakeWrapped("wrapped"))
""",
                },
            )
            bundle = enrich_dependencies(
                archive,
                [
                    DependencyRequest("gold", "ingredient", "tu_tien:xd_gold"),
                    DependencyRequest(
                        "cookedmeat", "ingredient", "tu_tien:xd_food"
                    ),
                    DependencyRequest("wrapped", "relation", "tu_tien:xd_wrap"),
                ],
                root / "missing.po",
            )

        gold_damage = [
            fact.payload.get("value")
            for fact in bundle.facts
            if fact.kind == "stat"
            and fact.subject.prefab_id == "gold"
            and fact.payload["key"] == "damage"
        ]
        self.assertEqual(gold_damage, [10])
        cooked_hunger = next(
            fact
            for fact in bundle.facts
            if fact.kind == "stat"
            and fact.subject.prefab_id == "cookedmeat"
            and fact.payload["key"] == "hunger"
        )
        self.assertEqual(cooked_hunger.payload["value"], 5)
        warning = next(
            error
            for error in bundle.errors
            if error["code"] == "unsupported_constructor_binding"
        )
        self.assertEqual(warning["prefab_id"], "wrapped")
        self.assertEqual(warning["expression"], 'MakeWrapped("wrapped")')

    def test_reverse_acquisition_indexes_only_selected_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": "",
                    "scripts/strings.lua": "",
                    "scripts/prefabs/silk.lua": 'return Prefab("silk", silkfn)',
                    "scripts/prefabs/nightmarefuel.lua": 'return Prefab("nightmarefuel", fuelfn)',
                    "scripts/prefabs/spider.lua": """
local function common()
  inst.components.lootdropper:AddRandomLoot("silk", .5)
  return inst
end
local function spiderfn()
  return common()
end
return Prefab("spider", spiderfn)
""",
                    "scripts/prefabs/shadow.lua": """
local function shadowfn()
  inst.components.lootdropper:SetLoot({"nightmarefuel", "rocks"})
  return inst
end
return Prefab("shadow", shadowfn)
""",
                    "scripts/prefabs/bush.lua": """
local function bushfn()
  inst.components.pickable:SetUp("silk", TUNING.REGROW)
  return inst
end
return Prefab("bush", bushfn)
""",
                    "scripts/prefabs/unrelated.lua": """
local function unrelatedfn()
  inst.components.lootdropper:AddChanceLoot("rocks", .25)
  return inst
end
return Prefab("unrelated", unrelatedfn)
""",
                },
            )
            bundle = enrich_dependencies(
                archive,
                [
                    DependencyRequest("silk", "ingredient", "tu_tien:xd_web"),
                    DependencyRequest(
                        "nightmarefuel", "ingredient", "tu_tien:xd_shadow"
                    ),
                ],
                root / "missing.po",
            )

        acquisitions = [fact for fact in bundle.facts if fact.kind == "acquisition"]
        self.assertEqual(
            {
                (
                    fact.subject.prefab_id,
                    fact.payload["type"],
                    fact.payload["source"]["prefab_id"],
                )
                for fact in acquisitions
            },
            {
                ("silk", "drop", "spider"),
                ("silk", "harvest", "bush"),
                ("nightmarefuel", "drop", "shadow"),
            },
        )
        spider = next(
            fact
            for fact in acquisitions
            if fact.payload["source"]["prefab_id"] == "spider"
        )
        self.assertEqual(spider.payload["weight_expression"], ".5")
        self.assertEqual(spider.payload["weight"], 0.5)
        self.assertIn("scripts/prefabs/spider.lua:line:", spider.locator)
        self.assertNotIn(
            "rocks",
            {
                fact.subject.prefab_id
                for fact in bundle.facts
                if fact.kind in {"entity", "acquisition"}
            },
        )

    def test_string_and_edible_assignments_ignore_comments_and_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": "",
                    "scripts/strings.lua": '''
--[[
STRINGS.NAMES.COMMENT_ONLY = "Comment"
]]
local sample = [=[
STRINGS.NAMES.STRING_ONLY = "String"
]=]
STRINGS.NAMES.REALFOOD = "Real Food"
''',
                    "scripts/prefabs/realfood.lua": '''
local function fn()
  local sample = [=[
  inst.components.edible.hungervalue = 999
  ]=]
  --[[ inst.components.edible.hungervalue = 888 ]]
  inst.components.edible.hungervalue = 10
  return inst
end
return Prefab("realfood", fn)
''',
                },
            )
            bundle = enrich_dependencies(
                archive,
                [
                    DependencyRequest("realfood", "ingredient", "tu_tien:xd_food"),
                    DependencyRequest(
                        "comment_only", "relation", "tu_tien:xd_comment"
                    ),
                    DependencyRequest(
                        "string_only", "relation", "tu_tien:xd_string"
                    ),
                ],
                root / "missing.po",
            )

        hunger = [
            fact.payload.get("value")
            for fact in bundle.facts
            if fact.kind == "stat"
            and fact.subject.prefab_id == "realfood"
            and fact.payload["key"] == "hunger"
        ]
        self.assertEqual(hunger, [10])
        entities = {
            fact.subject.prefab_id
            for fact in bundle.facts
            if fact.kind == "entity"
        }
        self.assertNotIn("comment_only", entities)
        self.assertNotIn("string_only", entities)

    def test_dynamic_recipe_and_loot_subexpressions_emit_exact_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": '''
Recipe2("pickaxe", {
  Ingredient(dynamic_prefab, 1),
  Ingredient("twigs", TUNING.TWIG_COST)
}, TECH.NONE)
''',
                    "scripts/strings.lua": "",
                    "scripts/prefabs/pickaxe.lua": '''
local function fn() return inst end
return Prefab("pickaxe", fn)
''',
                    "scripts/prefabs/twigs.lua": '''
local function fn() return inst end
return Prefab("twigs", fn)
''',
                    "scripts/prefabs/silk.lua": '''
local function fn() return inst end
return Prefab("silk", fn)
''',
                    "scripts/prefabs/dropper.lua": '''
local function fn()
  inst.components.lootdropper:SetLoot({"silk", dynamic_loot})
  inst.components.lootdropper:AddChanceLoot(dynamic_target, .25)
  return inst
end
return Prefab("dropper", fn)
''',
                },
            )
            bundle = enrich_dependencies(
                archive,
                [
                    DependencyRequest("pickaxe", "ingredient", "tu_tien:xd_tool"),
                    DependencyRequest("silk", "ingredient", "tu_tien:xd_web"),
                ],
                root / "missing.po",
            )

        warnings = [
            error
            for error in bundle.errors
            if error["code"] == "unsupported_base_source_subexpression"
        ]
        self.assertEqual(
            {warning["expression"] for warning in warnings},
            {"dynamic_prefab", "dynamic_loot", "dynamic_target"},
        )
        self.assertTrue(
            all(warning["path"].startswith("scripts/") for warning in warnings)
        )
        self.assertTrue(all(isinstance(warning["line"], int) for warning in warnings))
        silk_drop = next(
            fact
            for fact in bundle.facts
            if fact.kind == "acquisition"
            and fact.subject.prefab_id == "silk"
            and fact.payload["source"]["prefab_id"] == "dropper"
        )
        self.assertEqual(silk_drop.payload["count"], 1)
        twigs = next(
            fact
            for fact in bundle.facts
            if fact.kind == "ingredient"
            and fact.payload["ingredient"]["prefab_id"] == "twigs"
        )
        self.assertEqual(twigs.payload["amount_expression"], "TUNING.TWIG_COST")

    def test_derives_unique_unresolved_markers_from_static_and_runtime_facts(self):
        source = SourceRef("fixture", "runtime_probe", "fixture", "1", "abc")
        static = FactBundle(
            1,
            [source],
            [
                Fact(
                    "relation",
                    EntityKey("tu_tien", "xd_alias"),
                    {
                        "relation": "string_alias",
                        "target_prefab_id": "GOLDNUGGET",
                        "dependency_candidate": True,
                        "resolution": "unresolved",
                    },
                    source,
                    0.5,
                    "line:1",
                )
            ],
            [],
        )
        runtime = FactBundle(
            1,
            [source],
            [
                Fact(
                    "ingredient",
                    EntityKey("tu_tien", "xd_sword"),
                    {
                        "ingredient": {
                            "prefab_id": "silk",
                            "dependency_candidate": True,
                            "resolution": "unresolved",
                        }
                    },
                    source,
                    1.0,
                    "recipes:0",
                ),
                Fact(
                    "relation",
                    EntityKey("tu_tien", "xd_other"),
                    {
                        "target": {
                            "namespace": "tu_tien",
                            "prefab_id": "xd_known",
                            "resolution": "resolved",
                        }
                    },
                    source,
                    1.0,
                    "relations:0",
                ),
            ],
            [],
        )

        requests = derive_dependency_requests(static, runtime)

        self.assertEqual(
            [(request.prefab_id, request.relation, request.requested_by) for request in requests],
            [
                ("goldnugget", "string_alias", "tu_tien:xd_alias"),
                ("silk", "ingredient", "tu_tien:xd_sword"),
            ],
        )
        self.assertTrue(all(request.source_id == "fixture" for request in requests))

    def test_dependency_request_retains_originating_fact_evidence(self):
        source = SourceRef(
            "runtime-probe",
            "runtime_probe",
            "data/raw/runtime.json",
            "18.0.10",
            "abc123",
        )
        bundle = FactBundle(
            1,
            [source],
            [
                Fact(
                    "relation",
                    EntityKey("tu_tien", "xd_portal"),
                    {
                        "relation": "transforms_to",
                        "target": {
                            "prefab_id": "goldnugget",
                            "dependency_candidate": True,
                            "resolution": "unresolved",
                        },
                    },
                    source,
                    0.75,
                    "prefabs:2:relations:0",
                )
            ],
            [],
        )

        request = derive_dependency_requests(bundle)[0]

        self.assertEqual(request.fact_kind, "relation")
        self.assertEqual(request.relation, "transforms_to")
        self.assertEqual(request.locator, "prefabs:2:relations:0")
        self.assertEqual(request.confidence, 0.75)
        self.assertEqual(request.source_id, "runtime-probe")
        self.assertEqual(request.source_path, "data/raw/runtime.json")
        self.assertEqual(request.source_sha256, "abc123")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = self._archive(
                root,
                {
                    "scripts/recipes.lua": "",
                    "scripts/strings.lua": "",
                    "scripts/prefabs/goldnugget.lua": '''
local function fn() return inst end
return Prefab("goldnugget", fn)
''',
                },
            )
            enriched = enrich_dependencies(
                archive, [request], root / "missing.po"
            )
        entity = next(fact for fact in enriched.facts if fact.kind == "entity")
        evidence = entity.payload["requested_by"][0]
        self.assertEqual(evidence["fact_kind"], "relation")
        self.assertEqual(evidence["relation"], "transforms_to")
        self.assertEqual(evidence["locator"], "prefabs:2:relations:0")
        self.assertEqual(evidence["confidence"], 0.75)
        self.assertEqual(
            evidence["source"],
            {
                "source_id": "runtime-probe",
                "kind": "runtime_probe",
                "path": "data/raw/runtime.json",
                "version": "18.0.10",
                "sha256": "abc123",
            },
        )

    def test_snapshot_hash_must_match_before_archive_is_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "scripts.zip"
            archive.write_bytes(b"copied archive")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "files": {
                            "scripts.zip": {
                                "size": len(b"copied archive"),
                                "sha256": hashlib.sha256(b"other").hexdigest(),
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "checksum"):
                verify_snapshot_archive(archive, manifest)

    def test_enrich_base_cli_has_explicit_inputs_and_verifies_manifest_first(self):
        args = build_parser().parse_args(
            [
                "enrich-base",
                "--static",
                "static.json",
                "--runtime",
                "runtime.json",
                "--scripts",
                "snapshot/scripts.zip",
                "--manifest",
                "snapshot/manifest.json",
                "--base-translation-po",
                "translation.po",
                "--output",
                "base.json",
            ]
        )
        self.assertEqual(args.scripts, Path("snapshot/scripts.zip"))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "snapshot"
            snapshot.mkdir()
            scripts = snapshot / "scripts.zip"
            scripts.write_bytes(b"not the manifest hash")
            manifest = snapshot / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "files": {
                            "scripts.zip": {
                                "size": scripts.stat().st_size,
                                "sha256": hashlib.sha256(b"different").hexdigest(),
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            static = root / "static.json"
            dump_bundle(static, FactBundle(1, [], [], []))
            runtime = root / "runtime.json"
            runtime.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "mod_version": "test",
                        "recipes": [],
                        "prefabs": [],
                        "errors": [],
                    }
                ),
                encoding="utf-8",
            )
            argv = [
                "dst-extract",
                "enrich-base",
                "--static",
                str(static),
                "--runtime",
                str(runtime),
                "--scripts",
                str(scripts),
                "--manifest",
                str(manifest),
                "--base-translation-po",
                str(root / "missing.po"),
                "--output",
                str(root / "base.json"),
            ]
            with mock.patch("sys.argv", argv):
                with self.assertRaisesRegex(ValueError, "checksum"):
                    main()


if __name__ == "__main__":
    unittest.main()
