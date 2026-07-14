import hashlib
import tempfile
import unittest
from pathlib import Path

from tools.extract.source_manifest import snapshot_game_sources


class SourceManifestTests(unittest.TestCase):
    def test_copies_whole_archives_and_records_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundles = root / "game" / "databundles"
            bundles.mkdir(parents=True)
            (bundles / "scripts.zip").write_bytes(b"scripts")
            (bundles / "images.zip").write_bytes(b"images")

            result = snapshot_game_sources(root / "game", root / "snapshot")

            self.assertEqual(
                (root / "snapshot" / "scripts.zip").read_bytes(), b"scripts"
            )
            self.assertEqual(
                result["files"]["scripts.zip"]["sha256"],
                hashlib.sha256(b"scripts").hexdigest(),
            )
            self.assertEqual(result["files"]["images.zip"]["size"], 6)
