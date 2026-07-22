import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.cli import build_parser
from tools.extract.publication_quality import audit_publication, repair_publication


PNG = b"\x89PNG\r\n\x1a\nquality"


def item(item_id="base_game:bearger", **overrides):
    value = {
        "id": item_id,
        "namespace": "base_game",
        "prefabId": item_id.split(":", 1)[1],
        "category": "boss",
        "name": "Bearger",
        "englishName": "Bearger",
        "description": "A seasonal giant.",
        "sprite": None,
        "wiki": None,
        "recipe": None,
        "details": None,
        "mob": {"stats": [{"key": "health", "value": 6000}], "mechanics": [], "loot": []},
        "structureDetails": None,
        "character": None,
    }
    value.update(overrides)
    return value


class PublicationQualityTests(unittest.TestCase):
    def test_cli_exposes_audit_and_apply_modes(self):
        args = build_parser().parse_args(
            [
                "publication-quality",
                "--items", "items.json",
                "--guides", "guides",
                "--public-root", "public",
                "--category-root", "categories",
                "--report", "report.json",
                "--apply",
            ]
        )

        self.assertEqual(args.command, "publication-quality")
        self.assertTrue(args.apply)
        self.assertEqual(args.items, Path("items.json"))

    def test_audit_reports_duplicate_missing_image_content_and_detail(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            items_path = root / "items.json"
            items_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "items": [
                            item(),
                            item(description=None, mob=None),
                        ],
                    }
                ),
                encoding="utf-8",
            )
            guides = root / "guides"
            guides.mkdir()
            (guides / "index.json").write_text(
                json.dumps({"schemaVersion": 1, "count": 0, "guides": []}),
                encoding="utf-8",
            )

            audit = audit_publication(items_path, guides, root)
            codes = {issue["code"] for issue in audit["issues"]}

            self.assertIn("duplicate_identity", codes)
            self.assertIn("duplicate_code", codes)
            self.assertIn("missing_image", codes)
            self.assertIn("missing_content", codes)
            self.assertIn("missing_detail", codes)

    def test_repairs_cover_from_same_category_page_before_removal(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            public = root / "public"
            categories = root / "categories" / "bosses"
            categories.mkdir(parents=True)
            source = categories / "assets" / "bearger.png"
            source.parent.mkdir()
            source.write_bytes(PNG)
            (categories / "pages.jsonl").write_text(
                json.dumps(
                    {
                        "page_id": 9,
                        "title": "Bearger",
                        "canonical_url": "https://dontstarve.fandom.com/wiki/Bearger",
                        "images": ["File:Bearger.png"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (categories / "images.jsonl").write_text(
                json.dumps(
                    {
                        "title": "File:Bearger.png",
                        "local_path": "assets/bearger.png",
                        "mime": "image/png",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = repair_publication([item()], public, categories.parent)

            self.assertEqual(len(result["items"]), 1)
            self.assertEqual(result["rows"][0]["action"], "repair")
            self.assertTrue(result["items"][0]["sprite"]["src"].startswith("/assets/quality/"))
            self.assertTrue((public / result["items"][0]["sprite"]["src"].lstrip("/")).is_file())

    def test_removes_only_after_ordered_repair_attempts_fail(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            broken = item(
                "base_game:empty_wrapper",
                name="empty_wrapper",
                englishName=None,
                description=None,
                mob=None,
                category="other",
            )

            result = repair_publication([broken], root / "public", root / "categories")

            self.assertEqual(result["items"], [])
            row = result["rows"][0]
            self.assertEqual(row["action"], "remove")
            self.assertEqual(row["attempts"], [
                "current_valid_field",
                "canonical_duplicate",
                "wiki_detail",
                "reviewed_category_crawl",
                "catalog_recipe_evidence",
            ])
            self.assertIn("missing_image", row["finalIssues"])
            self.assertIn("missing_content", row["finalIssues"])


if __name__ == "__main__":
    unittest.main()
