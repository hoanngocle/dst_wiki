from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images/inventoryimages"


def read_ktex(path):
    data = path.read_bytes()
    assert data[:4] == b"KTEX"
    specifications = struct.unpack_from("<I", data, 4)[0]
    mip_count = (specifications >> 13) & 31
    metadata = [
        struct.unpack_from("<HHHI", data, 8 + 10 * index)
        for index in range(mip_count)
    ]
    offset = 8 + 10 * mip_count
    payloads = []
    for _, _, _, size in metadata:
        payloads.append(data[offset:offset + size])
        offset += size
    assert offset == len(data)
    return specifications, metadata, payloads


class EvaStartingIconTest(unittest.TestCase):
    def test_starting_icon_uses_lossless_64_pixel_mip_chain(self):
        original = read_ktex(IMAGES / "eva_scythe.tex")
        starting_path = IMAGES / "eva_scythe_starting.tex"
        self.assertTrue(starting_path.is_file(), "starting-item KTEX is missing")
        starting = read_ktex(starting_path)
        expected_specifications = (original[0] & ~(31 << 13)) | (7 << 13)
        self.assertEqual(starting[0], expected_specifications)
        self.assertEqual(starting[1], original[1][1:])
        self.assertEqual(starting[2], original[2][1:])
        self.assertEqual(starting[1][0][:2], (64, 64))

    def test_starting_atlas_has_64_pixel_half_pixel_inset(self):
        atlas_path = IMAGES / "eva_scythe_starting.xml"
        self.assertTrue(atlas_path.is_file(), "starting-item atlas is missing")
        atlas = ET.parse(atlas_path).getroot()
        self.assertEqual(atlas.find("Texture").attrib["filename"], "eva_scythe_starting.tex")
        element = atlas.find("Elements/Element")
        self.assertEqual(element.attrib, {
            "name": "eva_scythe_starting.tex",
            "u1": "0.0078125",
            "u2": "0.9921875",
            "v1": "0.0078125",
            "v2": "0.9921875",
        })

    def test_only_starting_item_uses_new_icon(self):
        source = (ROOT / "main/ttk_eva_source.lua").read_text(encoding="utf-8-sig")
        settings = (ROOT / "scripts/util/eva_settings.lua").read_text(encoding="utf-8-sig")
        prefab = (ROOT / "scripts/prefabs/eva_scythe.lua").read_text(encoding="utf-8-sig")
        recipes = (ROOT / "scripts/util/eva_recipes.lua").read_text(encoding="utf-8-sig")
        self.assertIn('Asset("IMAGE", "images/inventoryimages/eva_scythe_starting.tex")', source)
        self.assertIn('Asset("ATLAS", "images/inventoryimages/eva_scythe_starting.xml")', source)
        self.assertIn('atlas = "images/inventoryimages/eva_scythe_starting.xml"', settings)
        self.assertIn('image = "eva_scythe_starting.tex"', settings)
        self.assertIn('atlasname = "images/inventoryimages/eva_scythe.xml"', prefab)
        self.assertIn('atlas = "images/inventoryimages/eva_scythe.xml"', recipes)

    def test_description_replaces_only_first_bullet(self):
        settings = (ROOT / "scripts/util/eva_settings.lua").read_text(encoding="utf-8-sig")
        expected = ('STRINGS.CHARACTER_DESCRIPTIONS.eva = "\\n󰀍 EVA — Người bảo hộ cuối cùng.'
                    '\\n󰀉 Hồn Lực nuôi dưỡng sáu kỹ năng.'
                    '\\n󰀀 Lưỡi hái tím bạc, kiếm khí theo đòn đánh."')
        self.assertIn(expected, settings)


if __name__ == "__main__":
    unittest.main()
