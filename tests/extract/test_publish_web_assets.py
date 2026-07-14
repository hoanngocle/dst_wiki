import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.extract.publish_web_assets import publish_web_assets


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PublishWebAssetsTests(unittest.TestCase):
    def make_sources(self, root: Path):
        mod_root = root / "mod"
        mod_texture = mod_root / "images" / "inventoryimages" / "item.tex"
        mod_texture.parent.mkdir(parents=True)
        mod_texture.write_bytes(b"mod-texture")

        sources = root / "data" / "sources" / "game"
        sources.mkdir(parents=True)
        images_zip = sources / "images.zip"
        with ZipFile(images_zip, "w") as archive:
            archive.writestr("images/inventoryimages1.tex", b"base-texture")
        scripts_zip = sources / "scripts.zip"
        scripts_zip.write_bytes(b"scripts")
        manifest = {
            "schema_version": 1,
            "files": {
                path.name: {
                    "size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for path in (scripts_zip, images_zip)
            },
        }
        manifest_path = sources / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        texture_manifest = root / "textures.json"
        texture_manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "textures": [
                        {
                            "sha256": "a" * 64,
                            "source": "mod",
                            "texture": "images/inventoryimages/item.tex",
                        },
                        {
                            "sha256": "b" * 64,
                            "source": "base_game",
                            "texture": "images/inventoryimages1.tex",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        return mod_root, images_zip, manifest_path, texture_manifest

    def make_decoder(self, root: Path, body: str) -> Path:
        decoder = root / "decoder"
        decoder.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
        decoder.chmod(0o755)
        return decoder

    def test_publishes_mod_and_verified_base_textures_by_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root, images_zip, manifest_path, texture_manifest = self.make_sources(root)
            decoder = self.make_decoder(
                root,
                """import pathlib, sys
source = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
destination.mkdir(parents=True, exist_ok=True)
(destination / (source.stem + '.png')).write_bytes(b'\\x89PNG\\r\\n\\x1a\\n' + source.read_bytes())
""",
            )
            output = root / "public" / "assets" / "game"

            published = publish_web_assets(
                texture_manifest,
                mod_root,
                images_zip,
                manifest_path,
                output,
                str(decoder),
            )

            self.assertEqual(
                [path.name for path in published],
                ["a" * 64 + ".png", "b" * 64 + ".png"],
            )
            self.assertTrue(all(path.read_bytes().startswith(PNG_SIGNATURE) for path in published))
            self.assertIn(b"mod-texture", published[0].read_bytes())
            self.assertIn(b"base-texture", published[1].read_bytes())

    def test_duplicate_hash_is_decoded_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root, images_zip, manifest_path, texture_manifest = self.make_sources(root)
            payload = json.loads(texture_manifest.read_text(encoding="utf-8"))
            payload["textures"].append(dict(payload["textures"][0]))
            texture_manifest.write_text(json.dumps(payload), encoding="utf-8")
            calls = root / "calls.txt"
            decoder = self.make_decoder(
                root,
                f"""import pathlib, sys
source = pathlib.Path(sys.argv[1])
destination = pathlib.Path(sys.argv[2])
destination.mkdir(parents=True, exist_ok=True)
with pathlib.Path({str(calls)!r}).open('a', encoding='utf-8') as handle:
    handle.write(source.name + '\\n')
(destination / (source.stem + '.png')).write_bytes(b'\\x89PNG\\r\\n\\x1a\\n' + source.read_bytes())
""",
            )

            publish_web_assets(
                texture_manifest,
                mod_root,
                images_zip,
                manifest_path,
                root / "output",
                str(decoder),
            )

            self.assertEqual(calls.read_text(encoding="utf-8").splitlines(), ["item.tex", "inventoryimages1.tex"])

    def test_missing_decoder_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root, images_zip, manifest_path, texture_manifest = self.make_sources(root)
            output = root / "output"
            output.mkdir()
            existing = output / "existing.png"
            existing.write_bytes(PNG_SIGNATURE + b"existing")

            with self.assertRaisesRegex(RuntimeError, "decoder not found"):
                publish_web_assets(
                    texture_manifest,
                    mod_root,
                    images_zip,
                    manifest_path,
                    output,
                    str(root / "missing-ktech"),
                )

            self.assertEqual(existing.read_bytes(), PNG_SIGNATURE + b"existing")
            self.assertEqual([path.name for path in output.iterdir()], ["existing.png"])

    def test_decoder_failure_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root, images_zip, manifest_path, texture_manifest = self.make_sources(root)
            decoder = self.make_decoder(root, "import sys\nsys.exit(2)\n")
            output = root / "output"
            output.mkdir()
            existing = output / "existing.png"
            existing.write_bytes(PNG_SIGNATURE + b"existing")

            with self.assertRaisesRegex(RuntimeError, "texture decoder failed"):
                publish_web_assets(
                    texture_manifest,
                    mod_root,
                    images_zip,
                    manifest_path,
                    output,
                    str(decoder),
                )

            self.assertEqual(existing.read_bytes(), PNG_SIGNATURE + b"existing")

    def test_missing_png_output_fails_before_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root, images_zip, manifest_path, texture_manifest = self.make_sources(root)
            decoder = self.make_decoder(root, "import sys\nsys.exit(0)\n")
            output = root / "output"

            with self.assertRaisesRegex(RuntimeError, "did not produce"):
                publish_web_assets(
                    texture_manifest,
                    mod_root,
                    images_zip,
                    manifest_path,
                    output,
                    str(decoder),
                )

            self.assertFalse(output.exists())

    def test_verifies_base_archive_before_reading_members(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mod_root, images_zip, manifest_path, texture_manifest = self.make_sources(root)
            images_zip.write_bytes(b"changed-after-manifest")
            decoder = self.make_decoder(root, "import sys\nsys.exit(0)\n")

            with self.assertRaisesRegex(ValueError, "snapshot"):
                publish_web_assets(
                    texture_manifest,
                    mod_root,
                    images_zip,
                    manifest_path,
                    root / "output",
                    str(decoder),
                )


if __name__ == "__main__":
    unittest.main()
