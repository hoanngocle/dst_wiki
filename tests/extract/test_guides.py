import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.cli import build_parser
from tools.extract.guides import export_guides


def write_jsonl(path, values):
    path.write_text(
        "".join(json.dumps(value) + "\n" for value in values),
        encoding="utf-8",
    )


class GuideExportTests(unittest.TestCase):
    def fixture(self, root, *, title="Guides/Taming a Beefalo", html=None):
        crawl = root / "crawl"
        crawl.mkdir()
        asset = crawl / "assets" / "beefalo.jpg"
        asset.parent.mkdir()
        asset.write_bytes(b"guide-cover")
        html = html or """
          <div class="notice"><script>alert(1)</script>Notice</div>
          <p>Learn obedience and domestication before choosing a tendency.</p>
          <h2>Getting started</h2>
          <p>Feed the Beefalo and track obedience.</p>
          <figure><img data-image-name="Beefalo Tendencies.jpg"
            src="https://example.test/beefalo.jpg" width="180" height="89"
            onerror="alert(1)"></figure>
          <h2>Getting started</h2><p>Choose a tendency.</p>
        """
        page = {
            "schema_version": 1,
            "page_id": 7,
            "namespace": 0,
            "title": title,
            "canonical_url": "https://dontstarve.fandom.com/wiki/" + title.replace(" ", "_"),
            "revision": {
                "id": 70,
                "timestamp": "2026-07-22T00:00:00Z",
                "sha1": "abc123",
            },
            "html": html,
            "plain_text": " ".join("guide content" for _ in range(210)),
            "images": ["File:Beefalo_Tendencies.jpg"],
        }
        image = {
            "title": "File:Beefalo Tendencies.jpg",
            "local_path": "assets/beefalo.jpg",
            "mime": "image/jpeg",
            "width": 1152,
            "height": 571,
            "sha256": "fake-sha",
        }
        write_jsonl(crawl / "pages.jsonl", [page])
        write_jsonl(crawl / "images.jsonl", [image])
        return crawl

    def test_cli_exposes_export_guides(self):
        args = build_parser().parse_args(
            ["export-guides", "--crawl", "crawl", "--output", "out", "--assets", "assets"]
        )

        self.assertEqual(args.command, "export-guides")
        self.assertEqual(args.crawl, Path("crawl"))

    def test_exports_safe_deterministic_index_detail_and_local_cover(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            crawl = self.fixture(root)
            output = root / "public" / "data" / "guides"
            assets = root / "public" / "assets" / "guides"

            report = export_guides(crawl, output, assets)
            first = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted(root.rglob("*.json"))
            }
            export_guides(crawl, output, assets)
            second = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted(root.rglob("*.json"))
            }

            self.assertEqual(report["guides"], 1)
            self.assertEqual(first, second)
            index = json.loads((output / "index.json").read_text())
            guide = index["guides"][0]
            self.assertEqual(guide["slug"], "taming-a-beefalo")
            self.assertEqual(guide["topic"], "domestication")
            self.assertEqual(guide["audience"], "intermediate")
            self.assertEqual(guide["readingMinutes"], 2)
            self.assertTrue(guide["summaryVi"])
            self.assertTrue((root / "public" / guide["cover"]["src"].lstrip("/")).is_file())

            detail = json.loads((output / "pages" / "taming-a-beefalo.json").read_text())
            article = "".join(section["html"] for section in detail["sections"])
            self.assertNotIn("script", article)
            self.assertNotIn("onerror", article)
            self.assertNotIn("https://example.test/beefalo.jpg", article)
            self.assertIn("/assets/guides/beefalo-tendencies.jpg", article)
            self.assertEqual([row["id"] for row in detail["toc"]], ["getting-started", "getting-started-2"])

    def test_rejects_duplicate_slugs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            crawl = self.fixture(root)
            pages = [json.loads(line) for line in (crawl / "pages.jsonl").read_text().splitlines()]
            duplicate = dict(pages[0], page_id=8, title="Guides/Taming-a-Beefalo")
            write_jsonl(crawl / "pages.jsonl", [pages[0], duplicate])

            with self.assertRaisesRegex(ValueError, "duplicate guide slug"):
                export_guides(crawl, root / "out", root / "assets")

    def test_rejects_empty_or_imageless_pages(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            crawl = self.fixture(root, html="<script>bad()</script>")
            (crawl / "images.jsonl").write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "usable local cover|article content"):
                export_guides(crawl, root / "out", root / "assets")


if __name__ == "__main__":
    unittest.main()
