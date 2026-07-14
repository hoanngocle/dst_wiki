import os
import tempfile
import unittest
from pathlib import Path

from tools.extract.lua_strings import (
    decode_lua_string_literal,
    parse_simple_names_table,
    parse_string_assignments,
)
from tools.extract.mod_static import extract_mod_static
from tools.extract.po_strings import load_po_by_context


class ModStaticTests(unittest.TestCase):
    def test_extracts_exact_character_profile_metadata_without_executing_lua(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root = root / "content"
            (mod_root / "scripts/main").mkdir(parents=True)
            (mod_root / "scripts/prefabs").mkdir(parents=True)
            (mod_root / "images/inventoryimages").mkdir(parents=True)
            (mod_root / "modinfo.lua").write_text(
                'version = "18.0.10"\n', encoding="utf-8"
            )
            (mod_root / "scripts/main/strings.lua").write_text(
                "", encoding="utf-8"
            )
            translation_root = root / "translation"
            translation_root.mkdir()
            (translation_root / "modinfo.lua").write_text(
                'version = "1.0.11"\n', encoding="utf-8"
            )
            translation = translation_root / "modmain.lua"
            translation.write_text(
                '''
local names = { ["xd_hero"] = "Anh Hùng" }
STRINGS.CHARACTER_TITLES["xd_hero"] = "Kiếm Tu"
STRINGS.CHARACTER_SURVIVABILITY["xd_hero"] = "Gai Góc"
STRINGS.CHARACTER_DESCRIPTIONS["xd_hero"] = "*Dòng một\\n*Dòng hai"
STRINGS.CHARACTER_QUOTES["xd_hero"] = "\\\"Một câu nói.\\\""
-- STRINGS.CHARACTER_DESCRIPTIONS["xd_comment"] = "Không được lấy"
STRINGS.CHARACTER_DESCRIPTIONS[dynamic_id] = "Không có ID chính xác"
STRINGS.CHARACTER_QUOTES["xd_dynamic"] = make_quote()
''',
                encoding="utf-8",
            )

            bundle = extract_mod_static(
                mod_root, translation, root / "missing.po"
            )

        description = next(
            fact
            for fact in bundle.facts
            if fact.kind == "description" and fact.subject.prefab_id == "xd_hero"
        )
        self.assertEqual(description.payload["value"], "*Dòng một\n*Dòng hai")
        self.assertEqual(description.payload["description_type"], "character_profile")
        self.assertEqual(description.source.version, "1.0.11")
        self.assertRegex(description.locator, r"^line:\d+$")
        self.assertEqual(description.confidence, 1.0)
        effects = {
            fact.payload["effect_key"]: fact.payload["value"]
            for fact in bundle.facts
            if fact.kind == "effect" and fact.subject.prefab_id == "xd_hero"
        }
        self.assertEqual(
            effects,
            {
                "character_quote": '"Một câu nói."',
                "character_survivability": "Gai Góc",
                "character_title": "Kiếm Tu",
            },
        )
        self.assertFalse(
            any(
                fact.subject.prefab_id in {"xd_comment", "xd_dynamic"}
                for fact in bundle.facts
            )
        )

    def test_decodes_lua_short_string_escapes_without_python_semantics(self):
        self.assertEqual(decode_lua_string_literal(r'"\065"'), "A")
        self.assertEqual(
            decode_lua_string_literal('"first\\\nsecond"'), "first\nsecond"
        )
        self.assertEqual(
            decode_lua_string_literal('"left\\z \n\t right"'), "leftright"
        )
        self.assertEqual(
            decode_lua_string_literal(r'"quote: \" slash: \\"'),
            'quote: " slash: \\',
        )

    def test_parses_name_description_recipe_and_alias(self):
        path = Path("tests/extract/fixtures/strings.lua")
        rows = parse_string_assignments(path)
        values = {(row["field"], row["prefab_id"]): row for row in rows}
        self.assertEqual(values[("name", "xd_test_sword")]["value"], "Kiếm Thử")
        self.assertEqual(values[("description", "xd_test_sword")]["line"], 3)
        self.assertEqual(values[("name", "xd_alias")]["alias_prefab_id"], "goldnugget")

    def test_loads_po_context_and_continued_strings(self):
        values = load_po_by_context(Path("tests/extract/fixtures/viethoa.po"))
        self.assertEqual(values["STRINGS.NAMES.GOLDNUGGET"], "Vàng Thỏi")
        self.assertEqual(
            values["STRINGS.CHARACTERS.GENERIC.DESCRIBE.GOLDNUGGET"],
            "Kim loại quý.",
        )
        self.assertNotIn("STRINGS.NAMES.EMPTY", values)

    def test_parses_simple_literal_names_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "translation.lua"
            path.write_text(
                'local names = {\n    ["xd_hero"] = "Anh Hùng",\n}\n',
                encoding="utf-8",
            )
            self.assertEqual(
                parse_simple_names_table(path),
                [
                    {
                        "field": "name",
                        "prefab_id": "xd_hero",
                        "line": 2,
                        "value": "Anh Hùng",
                    }
                ],
            )

    def test_unions_static_ids_and_reports_missing_asset_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root = root / "content"
            (mod_root / "scripts/main").mkdir(parents=True)
            (mod_root / "scripts/prefabs").mkdir(parents=True)
            (mod_root / "images/inventoryimages").mkdir(parents=True)
            (mod_root / "images").mkdir(exist_ok=True)
            (mod_root / "modinfo.lua").write_text('version = "1.2.3"\n', encoding="utf-8")
            (mod_root / "scripts/main/strings.lua").write_text(
                'STRINGS.NAMES.XD_TEST_SWORD = "Kiếm Thử"\n'
                "STRINGS.NAMES.XD_ALIAS = STRINGS.NAMES.GOLDNUGGET\n",
                encoding="utf-8",
            )
            (mod_root / "scripts/prefabs/xd_prefab.lua").write_text("return {}\n", encoding="utf-8")
            (mod_root / "images/inventoryimages/xd_icon.xml").write_text(
                '<Atlas><Texture filename="xd_icon.tex"/><Elements>'
                '<Element name="xd_icon.tex" u1="0" u2="1" v1="0" v2="1"/>'
                '</Elements></Atlas>', encoding="utf-8"
            )
            (mod_root / "images/inventoryimages/xd_icon.tex").write_bytes(b"tex")
            (mod_root / "images/inventoryimages/xd_missing.xml").write_text(
                '<Atlas><Texture filename="xd_missing.tex"/><Elements>'
                '<Element name="xd_missing.tex" u1="0" u2="1" v1="0" v2="1"/>'
                '</Elements></Atlas>', encoding="utf-8"
            )
            (mod_root / "images/xd_info_1.xml").write_text(
                '<Atlas><Texture filename="xd_info_1.tex"/><Elements>'
                '<Element name="xd_info_1.tex" u1="0" u2="1" v1="0" v2="1"/>'
                '</Elements></Atlas>', encoding="utf-8"
            )
            (mod_root / "images/xd_info_1.tex").write_bytes(b"page")
            translation = root / "translation.lua"
            translation.write_text(
                'STRINGS.NAMES.XD_TRANSLATED = "Tên Dịch"\n', encoding="utf-8"
            )
            po = root / "base.po"
            po.write_text(
                'msgctxt "STRINGS.NAMES.GOLDNUGGET"\nmsgid "Gold Nugget"\nmsgstr ""\n',
                encoding="utf-8",
            )

            bundle = extract_mod_static(mod_root, translation, po)
            entity_ids = {
                fact.subject.prefab_id for fact in bundle.facts if fact.kind == "entity"
            }
            self.assertTrue(
                {"xd_test_sword", "xd_prefab", "xd_icon", "xd_missing", "xd_translated"}
                <= entity_ids
            )
            asset_payloads = [fact.payload for fact in bundle.facts if fact.kind == "asset"]
            self.assertTrue(any(value.get("asset_type") == "inventory" for value in asset_payloads))
            self.assertTrue(any(value.get("asset_type") == "handbook_image" for value in asset_payloads))
            self.assertTrue(
                any(error.get("code") == "missing_asset_texture" for error in bundle.errors)
            )
            self.assertTrue(all(fact.subject.namespace == "tu_tien" for fact in bundle.facts))
            self.assertTrue(all(fact.source.sha256 for fact in bundle.facts))
            alias = next(
                fact
                for fact in bundle.facts
                if fact.kind == "relation" and fact.subject.prefab_id == "xd_alias"
            )
            self.assertEqual(alias.payload["resolution"], "unresolved")
            self.assertTrue(alias.payload["dependency_candidate"])
            self.assertNotIn("target_namespace", alias.payload)
            self.assertFalse(
                any(
                    fact.kind == "name"
                    and fact.subject.prefab_id == "xd_alias"
                    and fact.source.source_id == "base-translation-po"
                    for fact in bundle.facts
                )
            )

            original_cwd = Path.cwd()
            try:
                os.chdir(root)
                second_bundle = extract_mod_static(mod_root, translation, po)
            finally:
                os.chdir(original_cwd)
            self.assertEqual(bundle, second_bundle)


if __name__ == "__main__":
    unittest.main()
