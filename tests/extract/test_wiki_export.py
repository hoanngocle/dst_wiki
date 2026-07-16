import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tests.extract.test_wiki_import import create_base_database, write_crawl
from tools.extract.wiki_export import (
    export_wiki_artifacts,
    load_wiki_export,
    merge_wiki_items,
)
from tools.extract.wiki_import import import_wiki


class WikiExportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.database = self.root / "wiki.sqlite"
        self.crawl = self.root / "crawl"
        self.crawl.mkdir()
        create_base_database(self.database)
        write_crawl(self.crawl)
        import_wiki(self.database, self.crawl)

    def tearDown(self):
        self.temporary.cleanup()

    def test_merges_mapped_page_and_emits_unmapped_page(self):
        existing = [
            {
                "id": "base_game:goldnugget",
                "prefabId": "goldnugget",
                "namespace": "base_game",
                "category": "item",
                "name": "Vàng",
                "englishName": "Gold Nugget",
                "description": None,
                "craftingNote": None,
                "sprite": None,
                "recipe": None,
                "wiki": None,
            }
        ]

        wiki = load_wiki_export(self.database, self.crawl)
        merged = merge_wiki_items(existing, wiki)
        by_id = {item["id"]: item for item in merged}
        image_sha = hashlib.sha256(b"original-image").hexdigest()

        self.assertEqual(by_id["base_game:goldnugget"]["name"], "Vàng")
        self.assertEqual(by_id["base_game:goldnugget"]["wiki"]["pageId"], 10)
        self.assertEqual(
            by_id["base_game:goldnugget"]["sprite"],
            {
                "src": "/assets/wiki/"
                + image_sha
                + ".png",
                "uv": {"u1": 0.0, "u2": 1.0, "v1": 0.0, "v2": 1.0},
            },
        )
        self.assertEqual(by_id["wiki:11"]["namespace"], "base_game")
        self.assertEqual(by_id["wiki:11"]["prefabId"], "wiki-11")
        self.assertEqual(by_id["wiki:11"]["wiki"]["mappingState"], "unmatched")

    def test_fractional_wiki_recipe_amount_is_preserved(self):
        wiki = load_wiki_export(self.database, self.crawl)

        item = merge_wiki_items([], wiki)[0]

        self.assertEqual(item["id"], "wiki:10")
        self.assertEqual(item["prefabId"], "wiki-10")
        self.assertEqual(item["wiki"]["mappingState"], "mapped")
        self.assertEqual(item["recipe"]["ingredients"][0]["amount"], 0.5)
        self.assertEqual(item["recipe"]["ingredients"][0]["name"], "Rocks")

    def test_exports_sanitized_detail_json_and_content_addressed_image(self):
        wiki = load_wiki_export(self.database, self.crawl)
        details = self.root / "public/data/wiki/pages"
        assets = self.root / "public/assets/wiki"

        export_wiki_artifacts(wiki, details, assets)

        detail = json.loads((details / "10.json").read_text(encoding="utf-8"))
        self.assertEqual(detail["pageId"], 10)
        self.assertIn("A nugget of gold.", detail["html"])
        self.assertNotIn("script", detail["html"].casefold())
        self.assertNotIn("Repeated navigation", detail["html"])
        self.assertEqual(detail["recipes"][0]["ingredients"][0]["amount"], 0.5)
        published = assets / (hashlib.sha256(b"original-image").hexdigest() + ".png")
        self.assertEqual(published.read_bytes(), b"original-image")

        first_detail = (details / "10.json").read_bytes()
        export_wiki_artifacts(wiki, details, assets)
        self.assertEqual((details / "10.json").read_bytes(), first_detail)

    def test_missing_wiki_tables_returns_an_empty_export(self):
        empty_database = self.root / "empty.sqlite"
        create_base_database(empty_database)

        wiki = load_wiki_export(empty_database, self.crawl)

        self.assertEqual(wiki.overlays, {})
        self.assertEqual(wiki.standalone_items, ())
        self.assertEqual(wiki.details, ())
        self.assertEqual(wiki.assets, ())

    def test_multiple_pages_for_one_entity_are_related_without_duplicate_items(self):
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "insert into wiki_pages select 12,'Gold Nugget/DST','Gold Nugget/DST',"
                "'https://dontstarve.wiki.gg/wiki/Gold_Nugget/DST',revision_id,"
                "revision_timestamp,revision_sha1,content_model,html,wikitext,"
                "plain_text,categories_json,redirect_target,fetched_at,"
                "source_schema_version from wiki_pages where page_id=10"
            )
            connection.execute(
                "insert into wiki_entity_mappings values(?,?,?,?,?,?,?)",
                (
                    12,
                    "base_game",
                    "goldnugget",
                    "canonical_alias",
                    0.94,
                    "{}",
                    1,
                ),
            )

        wiki = load_wiki_export(self.database, self.crawl)
        merged = merge_wiki_items([], wiki)

        self.assertEqual([item["id"] for item in merged], ["wiki:10", "wiki:11"])
        self.assertEqual(
            [page["pageId"] for page in merged[0]["wiki"]["relatedPages"]],
            [12],
        )


if __name__ == "__main__":
    unittest.main()
