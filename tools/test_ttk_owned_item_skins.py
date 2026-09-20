import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from zipfile import ZipFile


MODULE_PATH = Path(__file__).with_name("port_ttk_owned_item_skins.py")


def load_module():
    spec = importlib.util.spec_from_file_location("ttk_skin_port", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OwnedSkinImporterTests(unittest.TestCase):
    def test_import_is_safe(self):
        with mock.patch("pathlib.Path.write_text", side_effect=AssertionError("write during import")), \
             mock.patch("shutil.copyfile", side_effect=AssertionError("copy during import")):
            module = load_module()
        self.assertTrue(callable(module.main))

    def test_merge_preserves_custom_and_deduplicates(self):
        module = load_module()
        portal = {"name": "ttt_portal_gcsz", "base": "homesign", "build": "ttt_portal_gcsz"}
        discovered = {"name": "ttk_a_skins_b", "base": "ttk_a", "build": "xd_a_skins_b"}
        merged = module.merge_records([discovered], [portal, discovered], [discovered])
        self.assertEqual([portal["name"], discovered["name"]], [x["name"] for x in merged])

    def test_actual_prefab_discovery_includes_generated_groups(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.lua").write_text('return Prefab("ttk_literal", fn)\n', encoding="utf-8")
            (root / "b.lua").write_text('local definitions={{prefab="ttk_grouped"}}\nreturn Make(def.prefab)\n', encoding="utf-8")
            self.assertTrue({"ttk_literal", "ttk_grouped"} <= module.discover_destination_prefabs(root))

    def test_reconcile_reports_missing_resources_and_filters_unowned(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "anim").mkdir()
            rows = module.reconcile_candidates(
                [{"source_id": "xd_owned_skins_a", "source_base": "xd_owned"},
                 {"source_id": "xd_other_skins_b", "source_base": "xd_other"}],
                {"ttk_owned"}, root, {"xd_owned": ["ttk_owned"]})
            self.assertEqual("missing_resource", rows[0]["final_status"])
            self.assertEqual("base_not_implemented", rows[1]["final_status"])

    def test_deterministic_render(self):
        module = load_module()
        records = [{"name": "b", "base": "x", "build": "b"}, {"name": "a", "base": "x", "build": "a"}]
        self.assertEqual(module.render_json(records), module.render_json(list(reversed(records))))
        self.assertEqual(module.render_lua(records), module.render_lua(list(reversed(records))))
        self.assertEqual(json.loads(module.render_json(records))[0]["name"], "a")

    def test_copied_resource_validation_detects_stale_target(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); source = root / "source"; dest = root / "dest"
            for base in (source, dest):
                (base / "anim").mkdir(parents=True)
                (base / "images/inventoryimages").mkdir(parents=True)
            with ZipFile(source / "anim/xd_skin_a.zip", "w") as archive:
                archive.writestr("anim.bin", b"xd_skin_a")
                archive.writestr("build.bin", b"xd_skin_a")
            (source / "images/inventoryimages/xd_skin_a.xml").write_text(
                '<Atlas><Texture filename="xd_skin_a.tex" /></Atlas>', encoding="utf-8")
            (source / "images/inventoryimages/xd_skin_a.tex").write_bytes(b"texture")
            record = {"source_id": "xd_skin_a", "asset_name": "ttk_shared_xd_skin_a",
                      "icon_name": "ttk_shared_xd_skin_a"}
            (dest / "anim/ttk_shared_xd_skin_a.zip").write_bytes(
                (source / "anim/xd_skin_a.zip").read_bytes())
            (dest / "images/inventoryimages/ttk_shared_xd_skin_a.xml").write_text(
                '<Atlas><Texture filename="ttk_shared_xd_skin_a.tex" /></Atlas>', encoding="utf-8")
            target_tex = dest / "images/inventoryimages/ttk_shared_xd_skin_a.tex"
            target_tex.write_bytes(b"texture")
            self.assertEqual([], module.validate_copied_resource(source, dest, record))
            target_tex.write_bytes(b"stale")
            self.assertIn("texture đích thiếu/khác nguồn", module.validate_copied_resource(source, dest, record))

    def test_build_only_equipment_archive_is_valid(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root / "anim").mkdir(); (root / "images/inventoryimages").mkdir(parents=True)
            with ZipFile(root / "anim/xd_hyparmor.zip", "w") as archive:
                archive.writestr("build.bin", b"xd_hyparmor swap_body")
            (root / "images/inventoryimages/xd_hyparmor.xml").write_text(
                '<Atlas><Texture filename="xd_hyparmor.tex" /></Atlas>', encoding="utf-8")
            (root / "images/inventoryimages/xd_hyparmor.tex").write_bytes(b"texture")
            valid, _, _ = module.validate_resource(root, "xd_hyparmor")
            self.assertTrue(valid)

    def test_lua_metadata_must_match_manifest_not_just_name(self):
        module = load_module()
        records = [{"name": "skin", "base": "right", "build": "build"}]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "data.lua"
            path.write_text(module.render_lua([{"name": "skin", "base": "wrong", "build": "build"}]), encoding="utf-8")
            self.assertFalse(module.lua_matches_manifest(path, records))

    def test_yaohat_visibility_branch_uses_embedded_source_build(self):
        source = (MODULE_PATH.parents[1] / "mods/PhamNhanTuTien/scripts/prefabs/ttk_zcmj.lua").read_text(encoding="utf-8")
        self.assertIn('skin_build == "xd_yaohat"', source)
        self.assertNotIn('skin_build == "ttk_yaohat"', source)

    def test_explicit_equipment_declarations_have_stable_order(self):
        module = load_module()
        names = [row["source_id"] for row in module.discover_source_declarations()]
        positions = [names.index(name) for name in module.EXCLUSIVE_EQUIPMENT]
        self.assertEqual(sorted(positions), positions)


if __name__ == "__main__":
    unittest.main()
