import tempfile
import unittest
from pathlib import Path

from tools.extract.lua_strings import parse_string_assignments
from tools.extract.mod_static import extract_mod_static
from tools.extract.po_strings import load_po_by_context


class ModStaticTests(unittest.TestCase):
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
        self.assertEqual(values["STRINGS.NAMES.EMPTY"], "Empty")

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
                'STRINGS.NAMES.XD_TEST_SWORD = "Kiếm Thử"\n', encoding="utf-8"
            )
            (mod_root / "scripts/prefabs/xd_prefab.lua").write_text("return {}\n", encoding="utf-8")
            (mod_root / "images/inventoryimages/xd_icon.xml").write_text(
                '<Atlas><Elements><Element name="xd_icon.tex" /></Elements></Atlas>', encoding="utf-8"
            )
            (mod_root / "images/inventoryimages/xd_icon.tex").write_bytes(b"tex")
            (mod_root / "images/inventoryimages/xd_missing.xml").write_text(
                '<Atlas><Elements><Element name="xd_missing.tex" /></Elements></Atlas>', encoding="utf-8"
            )
            (mod_root / "images/xd_info_1.xml").write_text(
                '<Atlas><Elements><Element name="xd_info_1.tex" /></Elements></Atlas>', encoding="utf-8"
            )
            (mod_root / "images/xd_info_1.tex").write_bytes(b"page")
            translation = root / "translation.lua"
            translation.write_text(
                'STRINGS.NAMES.XD_TRANSLATED = "Tên Dịch"\n', encoding="utf-8"
            )
            po = root / "base.po"
            po.write_text(
                'msgctxt "STRINGS.NAMES.GOLDNUGGET"\nmsgid "Gold Nugget"\nmsgstr "Vàng Thỏi"\n',
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
            self.assertTrue(any(value.get("asset_type") == "handbook" for value in asset_payloads))
            self.assertTrue(
                any(error.get("code") == "missing_asset_pair" for error in bundle.errors)
            )
            self.assertTrue(all(fact.subject.namespace == "tu_tien" for fact in bundle.facts))
            self.assertTrue(all(fact.source.sha256 for fact in bundle.facts))


if __name__ == "__main__":
    unittest.main()
