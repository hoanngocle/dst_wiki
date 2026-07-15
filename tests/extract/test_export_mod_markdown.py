import tempfile
import unittest
import json
from pathlib import Path

from tools.extract.export_mod_markdown import (
    collect_game_text,
    export_mod_markdown,
    extract_game_strings,
    render_crafting_recipes,
)
from tools.extract.cli import build_parser


class ExportModMarkdownTests(unittest.TestCase):
    def test_collects_game_text_with_source_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "mod"
            source = root / "scripts" / "main" / "strings.lua"
            source.parent.mkdir(parents=True)
            source.write_text('STRINGS.XD_UI = "Giao diện"\n', encoding="utf-8")

            sources, rows = collect_game_text([root])

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].path, "mod/scripts/main/strings.lua")
        self.assertEqual(sources[0].source_id, "game-text:mod/scripts/main/strings.lua")
        self.assertEqual(len(sources[0].sha256), 64)
        self.assertEqual(
            rows,
            [
                {
                    "text_id": rows[0]["text_id"],
                    "text_key": "STRINGS.XD_UI",
                    "value_vi": "Giao diện",
                    "source_id": "game-text:mod/scripts/main/strings.lua",
                    "locator": "line:1",
                }
            ],
        )
        self.assertEqual(len(rows[0]["text_id"]), 64)

    def test_renders_runtime_recipe_as_a_vietnamese_formula(self):
        catalog = {
            "entities": [
                {
                    "key": "base_game:goldnugget",
                    "namespace": "base_game",
                    "prefab_id": "goldnugget",
                    "name": {"vi": "Vàng", "en": "Gold Nugget"},
                    "description": {"vi": None, "en": None},
                },
                {
                    "key": "tu_tien:xd_lingshi1",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_lingshi1",
                    "name": {"vi": "Linh Thạch", "en": None},
                    "description": {"vi": None, "en": None},
                },
                {
                    "key": "tu_tien:xd_test_sword",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_test_sword",
                    "name": {"vi": "Kiếm Thử", "en": None},
                    "description": {"vi": "Một thanh kiếm để kiểm thử.", "en": None},
                },
                {
                    "key": "tu_tien:xd_jingwei",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_jingwei",
                    "name": {"vi": "Tinh Vệ", "en": None},
                    "description": {"vi": None, "en": None},
                },
            ]
        }
        runtime = {
            "mod_version": "18.0.10",
            "recipes": [
                {
                    "product": "xd_test_sword",
                    "ingredients": [
                        {"prefab": "goldnugget", "amount": 2},
                        {"prefab": "xd_lingshi1", "amount": 1},
                    ],
                    "output_count": 3,
                    "tech": "SCIENCE_ONE",
                    "builder_tags": ["xd_jingwei"],
                    "character_ingredients": [
                        {"type": "decrease_health", "amount": 20},
                        {"type": "decrease_sanity", "amount": 10},
                        {"type": "decrease_sanity", "amount": 0},
                    ],
                    "filters": [],
                    "tech_ingredients": [],
                }
            ],
        }

        markdown = render_crafting_recipes(catalog, runtime)

        self.assertIn("### Kiếm Thử — `xd_test_sword`", markdown)
        self.assertIn(
            "**Công thức:** 2 × Vàng + 1 × Linh Thạch → 3 × Kiếm Thử",
            markdown,
        )
        self.assertIn("**Điều kiện:** Công nghệ: `SCIENCE_ONE`", markdown)
        self.assertIn("Nhân vật: Tinh Vệ (`xd_jingwei`)", markdown)
        self.assertIn("Chi phí: giảm 20 máu; giảm 10 tỉnh táo", markdown)
        self.assertIn("**Mô tả:** Một thanh kiếm để kiểm thử.", markdown)
        self.assertNotIn("giảm 0 tỉnh táo", markdown)

    def test_extracts_direct_and_table_strings_with_source_locators(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "strings.lua"
            source.write_text(
                'STRINGS.XD_STATUS = "Sẵn sàng"\n'
                'STRINGS.XD_ACTION = {\n'
                '    OPEN = "Mở ra",\n'
                '    [2] = "Lời thứ hai",\n'
                '    SUB = {\n'
                '        ON = "Bật",\n'
                '    },\n'
                '    "Lời đầu",\n'
                '}\n',
                encoding="utf-8",
            )

            rows = extract_game_strings([source])

        self.assertEqual(
            rows,
            [
                {
                    "key": "STRINGS.XD_ACTION.OPEN",
                    "value": "Mở ra",
                    "source": "strings.lua",
                    "line": 3,
                },
                {
                    "key": "STRINGS.XD_ACTION.SUB.ON",
                    "value": "Bật",
                    "source": "strings.lua",
                    "line": 6,
                },
                {
                    "key": "STRINGS.XD_ACTION[1]",
                    "value": "Lời đầu",
                    "source": "strings.lua",
                    "line": 8,
                },
                {
                    "key": "STRINGS.XD_ACTION[2]",
                    "value": "Lời thứ hai",
                    "source": "strings.lua",
                    "line": 4,
                },
                {
                    "key": "STRINGS.XD_STATUS",
                    "value": "Sẵn sàng",
                    "source": "strings.lua",
                    "line": 1,
                },
            ],
        )

    def test_exports_deterministic_reference_and_excludes_speech_sources(self):
        catalog = {
            "schema_version": 1,
            "entities": [
                {
                    "key": "tu_tien:xd_test",
                    "namespace": "tu_tien",
                    "prefab_id": "xd_test",
                    "name": {"vi": "Vật phẩm thử", "en": None},
                    "description": {"vi": "Mô tả thử.", "en": None},
                }
            ],
        }
        runtime = {
            "schema_version": 2,
            "mod_version": "18.0.10",
            "targets": ["xd_test"],
            "recipes": [
                {
                    "product": "xd_test",
                    "ingredients": [],
                    "output_count": 1,
                    "tech": "NONE",
                    "builder_tags": [],
                    "character_ingredients": [],
                    "filters": [],
                    "tech_ingredients": [],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog_path = root / "catalog.json"
            runtime_path = root / "runtime.json"
            mod_root = root / "mod"
            strings_path = mod_root / "scripts" / "main" / "strings.lua"
            speech_path = mod_root / "scripts" / "speech_xd_test.lua"
            strings_path.parent.mkdir(parents=True)
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
            strings_path.write_text('STRINGS.XD_UI = "Giao diện"\n', encoding="utf-8")
            speech_path.write_text('STRINGS.XD_SPEECH = "Không xuất"\n', encoding="utf-8")
            (mod_root / "scripts" / "compiled.lua").write_bytes(b"\xe1\x00\x80")
            (mod_root / "modinfo.lua").write_text(
                'name = "Tu Tiên"\n'
                'label = "Tùy chọn hiển thị"\n'
                'description = "Bật hoặc tắt"\n',
                encoding="utf-8",
            )
            output = root / "docs"

            export_mod_markdown(catalog_path, runtime_path, [mod_root], output)
            first = {path.name: path.read_bytes() for path in sorted(output.iterdir())}
            export_mod_markdown(catalog_path, runtime_path, [mod_root], output)
            second = {path.name: path.read_bytes() for path in sorted(output.iterdir())}

        self.assertEqual(first, second)
        self.assertEqual(set(first), {"README.md", "crafting-recipes.md", "game-text.md"})
        self.assertIn("1 công thức", first["README.md"].decode("utf-8"))
        self.assertIn("Không cần vật phẩm → 1 × Vật phẩm thử", first["crafting-recipes.md"].decode("utf-8"))
        game_text = first["game-text.md"].decode("utf-8")
        self.assertIn("Giao diện", game_text)
        self.assertIn("Tùy chọn hiển thị", game_text)
        self.assertNotIn("Không xuất", game_text)

    def test_cli_accepts_export_markdown_defaults(self):
        args = build_parser().parse_args(["export-markdown"])

        self.assertEqual(args.command, "export-markdown")
        self.assertEqual(args.output, Path("docs/mod-text"))


if __name__ == "__main__":
    unittest.main()
