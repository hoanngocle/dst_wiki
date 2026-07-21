import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.category_assets import publish_category_assets


class CategoryAssetTests(unittest.TestCase):
    def test_publishes_only_referenced_images_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            crawl = root / "crawl"
            original = crawl / "images" / "original"
            original.mkdir(parents=True)
            content = b"png-fixture"
            digest = hashlib.sha256(content).hexdigest()
            source = original / (digest + ".png")
            source.write_bytes(content)
            (crawl / "images.jsonl").write_text(
                json.dumps({
                    "title": "File:Beefalo Build.png",
                    "mime": "image/png",
                    "sha256": digest,
                    "local_path": str(source.relative_to(crawl)),
                }) + "\n",
                encoding="utf-8",
            )
            output = root / "public" / "animals"
            output.mkdir(parents=True)
            (output / "unused.png").write_bytes(b"unused")
            artifact = {
                "category": "animals",
                "pages": [{
                    "identity": {"sourcePageId": 10},
                    "visual": {"sourceTitle": "File:Beefalo_Build.png", "asset": None},
                }],
            }

            published = publish_category_assets(artifact, crawl, output)

            self.assertEqual(
                [value["publicPath"] for value in published],
                ["/assets/wiki-categories/animals/" + digest + ".png"],
            )
            self.assertFalse((output / "unused.png").exists())
            self.assertEqual((output / (digest + ".png")).read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
