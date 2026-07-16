import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.extract.wiki_import import import_wiki


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_base_database(path):
    with sqlite3.connect(path) as connection:
        connection.execute(
            "create table entities ("
            "namespace text not null, prefab_id text not null, "
            "name_en text, primary key(namespace,prefab_id))"
        )
        connection.executemany(
            "insert into entities(namespace,prefab_id,name_en) values(?,?,?)",
            [
                ("base_game", "goldnugget", "Gold Nugget"),
                ("tu_tien", "goldnugget", "Mod Gold"),
            ],
        )


def write_crawl(root, recipe_page_id=10):
    image_bytes = b"original-image"
    image_relative = Path("images/original") / ("a" * 64 + ".png")
    (root / image_relative).parent.mkdir(parents=True, exist_ok=True)
    (root / image_relative).write_bytes(image_bytes)
    image_sha = hashlib.sha256(image_bytes).hexdigest()
    pages = [
        {
            "schema_version": 1,
            "page_id": 10,
            "title": "Gold Nugget",
            "display_title": "Gold Nugget",
            "canonical_url": "https://dontstarve.wiki.gg/wiki/Gold_Nugget",
            "revision": {
                "id": 101,
                "timestamp": "2026-01-01T00:00:00Z",
                "sha1": "page-sha1",
            },
            "content_model": "wikitext",
            "html": "<p>A nugget of gold.</p>",
            "wikitext": '|spawnCode = "goldnugget"',
            "plain_text": "A nugget of gold.",
            "categories": ["Category:Items", "Category:Resources"],
            "redirect_target": None,
            "fetched_at": "2026-07-15T00:00:00Z",
        },
        {
            "schema_version": 1,
            "page_id": 11,
            "title": "Unmapped Relic",
            "display_title": "Unmapped Relic",
            "canonical_url": "https://dontstarve.wiki.gg/wiki/Unmapped_Relic",
            "revision": {
                "id": 102,
                "timestamp": "2026-01-02T00:00:00Z",
                "sha1": "page-sha2",
            },
            "content_model": "wikitext",
            "html": "<p>Unknown.</p>",
            "wikitext": "",
            "plain_text": "Unknown.",
            "categories": ["Category:Items"],
            "redirect_target": None,
            "fetched_at": "2026-07-15T00:01:00Z",
        },
    ]
    recipes = [
        {
            "schema_version": 1,
            "page_id": recipe_page_id,
            "result": "Gold Nugget",
            "ingredients": [{"title": "Rocks", "count": 0.5}],
            "source": "Object Infobox",
            "station": "Alchemy Engine",
            "tab": "Refine",
            "tier": "2",
            "character": None,
            "dlc": "DST",
            "variant": "base",
            "note": None,
        }
    ]
    images = [
        {
            "schema_version": 1,
            "page_id": 200,
            "title": "File:Gold Nugget.png",
            "original_url": "https://dontstarve.wiki.gg/images/Gold_Nugget.png",
            "local_path": image_relative.as_posix(),
            "mime": "image/png",
            "byte_size": len(image_bytes),
            "sha256": image_sha,
            "mediawiki_sha1": "mediawiki-sha1",
            "width": 64,
            "height": 64,
            "fetched_at": "2026-07-15T00:02:00Z",
        }
    ]
    write_jsonl(root / "pages.jsonl", pages)
    write_jsonl(root / "recipes.jsonl", recipes)
    write_jsonl(root / "images.jsonl", images)
    (root / "index.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "pages": {"by_id": {}, "by_title": {}},
                "images": {"by_title": {}},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    manifest = {
        "schema_version": 1,
        "status": "complete",
        "base_url": "https://dontstarve.wiki.gg/",
        "started_at": "2026-07-15T00:00:00Z",
        "completed_at": "2026-07-15T01:00:00Z",
        "counts": {
            "pages": len(pages),
            "recipes": len(recipes),
            "images": len(images),
            "failures": 0,
            "pending_pages": 0,
            "pending_images": 0,
        },
        "checksums": {
            name: sha256(root / name)
            for name in ("pages.jsonl", "recipes.jsonl", "images.jsonl")
        },
        "options": {"profile": "items"},
        "unresolved_errors": [],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True), encoding="utf-8"
    )


def wiki_snapshot(database):
    tables = (
        "wiki_import_runs",
        "wiki_pages",
        "wiki_recipes",
        "wiki_recipe_ingredients",
        "wiki_images",
        "wiki_entity_mappings",
    )
    with sqlite3.connect(database) as connection:
        return {
            table: connection.execute(
                'select * from "' + table + '" order by rowid'
            ).fetchall()
            for table in tables
        }


class WikiImportTests(unittest.TestCase):
    def test_imports_pages_recipes_ingredients_images_and_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database)
            write_crawl(crawl)

            summary = import_wiki(database, crawl)

            with sqlite3.connect(database) as connection:
                self.assertEqual(
                    connection.execute("select count(*) from wiki_pages").fetchone()[0],
                    2,
                )
                self.assertEqual(
                    connection.execute("select count(*) from wiki_recipes").fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute(
                        "select ingredient_title,amount from wiki_recipe_ingredients"
                    ).fetchone(),
                    ("Rocks", 0.5),
                )
                self.assertEqual(
                    connection.execute(
                        "select entity_namespace,entity_prefab_id,method "
                        "from wiki_entity_mappings where selected=1"
                    ).fetchone(),
                    ("base_game", "goldnugget", "spawn_code"),
                )
                self.assertEqual(connection.execute("pragma foreign_key_check").fetchall(), [])
            self.assertEqual(summary.pages, 2)
            self.assertEqual(summary.recipes, 1)
            self.assertEqual(summary.ingredients, 1)
            self.assertEqual(summary.images, 1)
            self.assertEqual(summary.mapped, 1)
            self.assertEqual(summary.unmatched, 1)

    def test_failed_reimport_preserves_previous_successful_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database)
            write_crawl(crawl)
            import_wiki(database, crawl)
            before = wiki_snapshot(database)

            write_crawl(crawl, recipe_page_id=999)
            with self.assertRaisesRegex(ValueError, "unknown page_id 999"):
                import_wiki(database, crawl)

            self.assertEqual(wiki_snapshot(database), before)

    def test_identical_import_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database)
            write_crawl(crawl)

            first_summary = import_wiki(database, crawl)
            first = wiki_snapshot(database)
            second_summary = import_wiki(database, crawl)

            self.assertEqual(second_summary, first_summary)
            self.assertEqual(wiki_snapshot(database), first)

    def test_rejects_manifest_checksum_mismatch_before_database_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database)
            write_crawl(crawl)
            (crawl / "pages.jsonl").write_text("{}\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "checksum mismatch.*pages.jsonl"):
                import_wiki(database, crawl)

            with sqlite3.connect(database) as connection:
                self.assertEqual(
                    connection.execute(
                        "select count(*) from sqlite_master where name like 'wiki_%'"
                    ).fetchone()[0],
                    0,
                )

    def test_normalizes_decorated_recipe_count_and_preserves_raw_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database)
            write_crawl(crawl)
            recipes_path = crawl / "recipes.jsonl"
            recipes = [json.loads(recipes_path.read_text(encoding="utf-8"))]
            recipes[0]["ingredients"][0]["count"] = "2 (link=Wurt only)"
            write_jsonl(recipes_path, recipes)
            manifest_path = crawl / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["checksums"]["recipes.jsonl"] = sha256(recipes_path)
            manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

            import_wiki(database, crawl)

            with sqlite3.connect(database) as connection:
                self.assertEqual(
                    connection.execute(
                        "select amount,amount_text from wiki_recipe_ingredients"
                    ).fetchone(),
                    (2.0, "2 (link=Wurt only)"),
                )

    def test_preserves_parenthesized_fraction_and_negative_recipe_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / "wiki.sqlite"
            crawl = root / "crawl"
            crawl.mkdir()
            create_base_database(database)
            write_crawl(crawl)
            recipes_path = crawl / "recipes.jsonl"
            recipes = [json.loads(recipes_path.read_text(encoding="utf-8"))]
            recipes[0]["ingredients"] = [
                {"title": "Vegetables", "count": "(0.5)"},
                {"title": "Health Decrease", "count": "-50 (character only)"},
            ]
            write_jsonl(recipes_path, recipes)
            manifest_path = crawl / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["checksums"]["recipes.jsonl"] = sha256(recipes_path)
            manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

            import_wiki(database, crawl)

            with sqlite3.connect(database) as connection:
                self.assertEqual(
                    connection.execute(
                        "select amount,amount_text from wiki_recipe_ingredients "
                        "order by position"
                    ).fetchall(),
                    [
                        (0.5, "(0.5)"),
                        (-50.0, "-50 (character only)"),
                    ],
                )


if __name__ == "__main__":
    unittest.main()
