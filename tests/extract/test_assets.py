import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.extract.assets import (
    add_base_game_asset_facts,
    index_mod_assets,
    parse_atlas,
    parse_atlas_bytes,
)
from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef


class AssetTests(unittest.TestCase):
    def test_parses_texture_element_and_uv(self):
        atlas = parse_atlas(Path("tests/extract/fixtures/atlas.xml"))
        self.assertEqual(atlas.texture, "inventoryimages.tex")
        self.assertEqual(
            atlas.elements["goldnugget.tex"], (0.0, 0.5, 0.0, 0.5)
        )
        self.assertEqual(
            parse_atlas_bytes(
                Path("tests/extract/fixtures/atlas.xml").read_bytes()
            ),
            atlas,
        )

    def test_rejects_malformed_xml_and_missing_texture_declaration(self):
        with self.assertRaisesRegex(ValueError, "invalid atlas XML"):
            parse_atlas_bytes(b"<Atlas>")
        with self.assertRaisesRegex(ValueError, "Texture"):
            parse_atlas_bytes(b"<Atlas><Elements /></Atlas>")

    def test_indexes_exactly_five_base_atlases_and_reports_missing_tex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "images.zip"
            atlas = (
                '<Atlas><Texture filename="{texture}"/><Elements>'
                '<Element name="{element}.tex" u1="0" u2="1" v1="0" v2="1"/>'
                "</Elements></Atlas>"
            )
            with ZipFile(archive, "w") as handle:
                for suffix, element in (
                    ("", "goldnugget"),
                    ("1", "silk"),
                    ("2", "nightmarefuel"),
                    ("3", "twigs"),
                    ("4", "flint"),
                ):
                    texture = f"inventoryimages{suffix}.tex"
                    handle.writestr(
                        f"images/inventoryimages{suffix}.xml",
                        atlas.format(texture=texture, element=element),
                    )
                    if suffix != "2":
                        handle.writestr(f"images/{texture}", b"tex")
                handle.writestr(
                    "images/inventoryimages5.xml",
                    atlas.format(
                        texture="inventoryimages5.tex", element="should_ignore"
                    ),
                )
                handle.writestr("images/inventoryimages5.tex", b"tex")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "files": {
                            "images.zip": {
                                "size": archive.stat().st_size,
                                "sha256": hashlib.sha256(
                                    archive.read_bytes()
                                ).hexdigest(),
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            source = SourceRef(
                "scripts",
                "base_game_source",
                "scripts.zip",
                "snapshot",
                "a" * 64,
            )
            entities = [
                Fact("entity", EntityKey("base_game", prefab_id), {}, source, 1.0)
                for prefab_id in (
                    "goldnugget",
                    "silk",
                    "nightmarefuel",
                    "twigs",
                    "flint",
                    "should_ignore",
                )
            ]
            original = FactBundle(1, [source], entities, [])

            bundle = add_base_game_asset_facts(original, archive, manifest)

            assets = [fact for fact in bundle.facts if fact.kind == "asset"]
            self.assertEqual(
                {fact.subject.prefab_id for fact in assets},
                {"goldnugget", "silk", "nightmarefuel", "twigs", "flint"},
            )
            missing = next(
                fact
                for fact in assets
                if fact.subject.prefab_id == "nightmarefuel"
            )
            self.assertFalse(missing.payload["available"])
            self.assertEqual(missing.confidence, 0.7)
            self.assertTrue(missing.source.sha256)
            self.assertIn("images/inventoryimages2.xml", missing.locator)
            self.assertTrue(
                any(
                    error["code"] == "missing_asset_texture"
                    for error in bundle.errors
                )
            )
            self.assertEqual(
                {
                    fact.subject.prefab_id
                    for fact in bundle.facts
                    if fact.kind == "entity"
                },
                set(fact.subject.prefab_id for fact in entities),
            )

    def test_verifies_images_snapshot_before_opening_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "images.zip"
            with ZipFile(archive, "w") as handle:
                handle.writestr("images/inventoryimages.xml", "<Atlas />")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "files": {
                            "images.zip": {
                                "size": archive.stat().st_size,
                                "sha256": "0" * 64,
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                add_base_game_asset_facts(FactBundle(1), archive, manifest)

    def test_mod_inventory_and_handbook_assets_are_stable_and_report_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            mod_root = Path(tmp) / "mod"
            inventory = mod_root / "images/inventoryimages"
            inventory.mkdir(parents=True)
            (mod_root / "images/xd_info_2.xml").write_text(
                '<Atlas><Texture filename="xd_info_2.tex"/><Elements>'
                '<Element name="xd_info_2.tex" u1="0" u2="1" v1="0" v2="1"/>'
                "</Elements></Atlas>",
                encoding="utf-8",
            )
            (mod_root / "images/xd_info_2.tex").write_bytes(b"page2")
            (mod_root / "images/xd_info_1.xml").write_text(
                '<Atlas><Texture filename="xd_info_1.tex"/><Elements>'
                '<Element name="xd_info_1.tex" u1="0" u2="1" v1="0" v2="1"/>'
                "</Elements></Atlas>",
                encoding="utf-8",
            )
            (mod_root / "images/xd_info_1.tex").write_bytes(b"page1")
            (inventory / "xd_icon.xml").write_text(
                '<Atlas><Texture filename="xd_icon.tex"/><Elements>'
                '<Element name="xd_icon.tex" u1="0" u2="1" v1="0" v2="1"/>'
                "</Elements></Atlas>",
                encoding="utf-8",
            )
            (inventory / "broken.xml").write_text("<Atlas>", encoding="utf-8")

            first = index_mod_assets(mod_root, "1.2.3")
            second = index_mod_assets(mod_root, "1.2.3")

            self.assertEqual(first, second)
            handbook = [
                fact
                for fact in first.facts
                if fact.payload.get("asset_type") == "handbook_image"
            ]
            self.assertEqual(
                [fact.subject.prefab_id for fact in handbook],
                ["xd_info_1", "xd_info_2"],
            )
            self.assertTrue(all(fact.payload["available"] for fact in handbook))
            inventory_fact = next(
                fact
                for fact in first.facts
                if fact.payload.get("asset_type") == "inventory"
            )
            self.assertFalse(inventory_fact.payload["available"])
            self.assertTrue(
                any(error["code"] == "invalid_atlas_xml" for error in first.errors)
            )
            self.assertTrue(
                any(error["code"] == "missing_asset_texture" for error in first.errors)
            )


if __name__ == "__main__":
    unittest.main()
