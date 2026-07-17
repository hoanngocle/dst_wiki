import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tests.extract.test_wiki_import import (
    append_structure_page,
    create_base_database,
    write_crawl,
)
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

    def test_export_exposes_structure_details_by_item_id(self):
        append_structure_page(self.crawl)
        import_wiki(self.database, self.crawl)

        wiki = load_wiki_export(self.database, self.crawl)

        self.assertIn("base_game:atrium_statue", wiki.structure_details)
        details = wiki.structure_details["base_game:atrium_statue"]
        self.assertIs(details["origin"]["naturallySpawned"], True)
        self.assertIs(details["destruction"]["destroyable"], False)

    def test_vietnamese_wiki_summary_overrides_database_description(self):
        source = "A nugget of gold."
        (self.crawl / "summary_vi.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "pages": {
                        "10": {
                            "source_sha256": hashlib.sha256(
                                source.encode("utf-8")
                            ).hexdigest(),
                            "source": source,
                            "vi": "Tóm tắt Wiki tiếng Việt.",
                        }
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        existing = [
            {
                "id": "base_game:goldnugget",
                "prefabId": "goldnugget",
                "namespace": "base_game",
                "category": "item",
                "name": "Vàng",
                "englishName": "Gold Nugget",
                "description": "Mô tả database.",
                "craftingNote": None,
                "sprite": None,
                "recipe": None,
                "wiki": None,
            }
        ]

        merged = merge_wiki_items(existing, load_wiki_export(self.database, self.crawl))

        self.assertEqual(merged[0]["description"], "Tóm tắt Wiki tiếng Việt.")

    def test_uses_crawled_seed_icon_when_wikitext_omits_image_field(self):
        (self.crawl / "seeds.jsonl").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "title": "Gold Nugget",
                    "href": "/wiki/Gold_Nugget",
                    "icon_title": "File:Gold Nugget.png",
                    "icon_thumbnail_url": (
                        "https://dontstarve.wiki.gg/images/thumb/"
                        "Gold_Nugget.png/40px-Gold_Nugget.png"
                    ),
                    "source_sections": ["Items#Resources-0"],
                },
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "update wiki_pages set wikitext=? where page_id=10",
                ('|spawnCode = "goldnugget"',),
            )

        wiki = load_wiki_export(self.database, self.crawl)
        item = merge_wiki_items([], wiki)[0]

        self.assertEqual(
            item["sprite"]["src"],
            "/assets/wiki/"
            + hashlib.sha256(b"original-image").hexdigest()
            + ".png",
        )

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

    def test_preserves_curated_wiki_assets_during_export(self):
        wiki = load_wiki_export(self.database, self.crawl)
        details = self.root / "public/data/wiki/pages"
        assets = self.root / "public/assets/wiki"
        curated = assets / "usage" / "station.png"
        curated.parent.mkdir(parents=True)
        curated.write_bytes(b"curated-station")

        export_wiki_artifacts(wiki, details, assets)

        self.assertEqual(curated.read_bytes(), b"curated-station")

    def test_exports_cached_vietnamese_wiki_summary_into_detail_and_item_data(self):
        source = "A nugget of gold."
        (self.crawl / "summary_vi.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "pages": {
                        "10": {
                            "source_sha256": hashlib.sha256(
                                source.encode("utf-8")
                            ).hexdigest(),
                            "source": source,
                            "vi": "Một cục vàng dùng làm nguyên liệu chế tạo.",
                        }
                    },
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        wiki = load_wiki_export(self.database, self.crawl)
        detail = next(value for value in wiki.details if value["pageId"] == 10)
        item = next(
            value for value in wiki.standalone_items if value["wiki"]["pageId"] == 10
        )

        self.assertEqual(
            detail.get("summaryViHtml"),
            "<h2>Tóm tắt</h2><p>Một cục vàng dùng làm nguyên liệu chế tạo.</p>",
        )
        self.assertEqual(
            item["description"], "Một cục vàng dùng làm nguyên liệu chế tạo."
        )

    def test_missing_wiki_tables_returns_an_empty_export(self):
        empty_database = self.root / "empty.sqlite"
        create_base_database(empty_database)

        wiki = load_wiki_export(empty_database, self.crawl)

        self.assertEqual(wiki.overlays, {})
        self.assertEqual(wiki.standalone_items, ())
        self.assertEqual(wiki.details, ())
        self.assertEqual(wiki.assets, ())
        self.assertEqual(wiki.structure_details, {})

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

    def test_normalizes_supported_sections_for_every_wiki_page(self):
        fixture = json.loads(
            (
                Path(__file__).resolve().parents[2]
                / "public/data/wiki/pages/210449.json"
            ).read_text(encoding="utf-8")
        )
        rendered_html = (
            '<p id="Gathering">Gathering</p>'
            '<h3><span id="Drop_table">Drop table</span></h3>'
            '<table><tr><td>drop</td></tr></table>'
            '<h2><span id="Usage">Usage</span></h2>'
            '<div>recipes</div>'
            '<h2><span id="Trivia">Trivia</span></h2>'
            '<p>Trivia body</p>'
        )
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "update wiki_pages set html=?,wikitext=? where page_id=10",
                (
                    '<p>A nugget of gold.</p>'
                    '<h2><span id="Usage">Usage</span></h2>'
                    '<div>gold recipes</div>'
                    '<h2><span id="Trivia">Trivia</span></h2>',
                    "{{Object Infobox\n"
                    "|droppedBy = {{pic24|Boulder}} ×1 ({{pic24|Pickaxe}})<br>"
                    "{{pic24|Pig King}} 50% ×2\n"
                    "}}\n"
                    "== Usage ==\n"
                    "{{Recipe|item1=Gold Nugget|count1=2|item2=Twigs|count2=4|"
                    "tool=Alchemy Engine|result=Luxury Axe}}\n"
                    "== Trivia ==\n",
                ),
            )
            connection.execute(
                "insert into entities(namespace,prefab_id,name_en) values(?,?,?)",
                ("base_game", "nightmarefuel", "Nightmare Fuel"),
            )
            connection.execute(
                "insert into wiki_pages select 210449,'Nightmare Fuel','Nightmare Fuel',"
                "'https://dontstarve.wiki.gg/wiki/Nightmare_Fuel',revision_id,"
                "revision_timestamp,revision_sha1,content_model,?,?,plain_text,"
                "categories_json,redirect_target,fetched_at,source_schema_version "
                "from wiki_pages where page_id=10",
                (rendered_html, fixture["wikitext"]),
            )
            connection.execute(
                "insert into wiki_entity_mappings values(?,?,?,?,?,?,?)",
                (
                    210449,
                    "base_game",
                    "nightmarefuel",
                    "canonical_alias",
                    1.0,
                    "{}",
                    1,
                ),
            )

        wiki = load_wiki_export(self.database, self.crawl)
        detail = next(value for value in wiki.details if value["pageId"] == 210449)
        ordinary = next(value for value in wiki.details if value["pageId"] == 10)

        self.assertEqual(detail["normalized"]["schema_version"], 2)
        self.assertEqual(len(detail["normalized"]["dropTable"]["rows"]), 10)
        self.assertEqual(len(detail["normalized"]["usage"]["recipes"]), 30)
        self.assertNotIn('id="Drop_table"', detail["html"])
        self.assertNotIn('id="Usage"', detail["html"])
        self.assertIn('id="Trivia"', detail["html"])
        self.assertIsNotNone(ordinary.get("normalized"))
        self.assertEqual(ordinary["normalized"]["subject"]["title"], "Gold Nugget")
        self.assertEqual(
            ordinary["normalized"]["usage"]["recipes"][0]["subjectAmount"], 2
        )
        self.assertEqual(
            [
                source["title"]
                for row in ordinary["normalized"]["dropTable"]["rows"]
                for source in row["sources"]
            ],
            ["Boulder", "Pig King"],
        )
        self.assertEqual(
            ordinary["normalized"]["dropTable"]["rows"][0]["context"],
            "(Pickaxe)",
        )
        self.assertNotIn('id="Usage"', ordinary["html"])


if __name__ == "__main__":
    unittest.main()
