import json
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tools.crawl_wiki.category_config import CategoryConfig
from tools.crawl_wiki.client import MediaWikiClient, ResolvedTitle
from tools.crawl_wiki.crawler import (
    CategoryCrawler,
    SelectiveItemsCrawler,
    WikiCrawler,
    select_primary_article_image,
)
from tools.crawl_wiki.storage import CrawlStorage
from tools.crawl_wiki.url_registry import UrlRegistry


PAGES = {
    1: {"pageid": 1, "ns": 0, "title": "Wilson"},
    2: {"pageid": 2, "ns": 14, "title": "Category:Characters"},
    3: {"pageid": 3, "ns": 6, "title": "File:Wilson.png"},
    10: {"pageid": 10, "ns": 0, "title": "Cut Grass"},
    11: {"pageid": 11, "ns": 0, "title": "Twigs"},
}


class _CrawlerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        del format, args

    def _json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed_url = urllib.parse.urlsplit(self.path)
        if parsed_url.path.startswith("/images/"):
            body = ("original:" + parsed_url.path).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed_url.path != "/api.php":
            self.send_error(404)
            return

        query = urllib.parse.parse_qs(parsed_url.query)
        if query.get("action") == ["parse"] and "page" in query:
            title = query["page"][0]
            source_html = {
                "Items": """
                  <article id="Resources-0">
                    <a href="/wiki/Cut_Grass" title="Cut Grass">
                      <img alt="Cut Grass.png" src="/images/thumb/Cut_Grass.png">
                    </a>
                    <a href="/wiki/Twigs" title="Twigs">
                      <img alt="Twigs.png" src="/images/thumb/Twigs.png">
                    </a>
                  </article>
                  <article id="Food-0">
                    <a href="/wiki/Cut_Grass" title="Cut Grass">
                      <img alt="Cut Grass.png" src="/images/thumb/Cut_Grass.png">
                    </a>
                  </article>
                """,
                "Plants": """
                  <article id="DST-0">
                    <a href="/wiki/Twigs" title="Twigs">
                      <img alt="Twigs.png" src="/images/thumb/Twigs.png">
                    </a>
                  </article>
                """,
            }[title]
            self._json({"parse": {"title": title, "text": source_html}})
            return

        if query.get("prop") == ["info"] and "titles" in query:
            by_title = {page["title"]: page for page in PAGES.values()}
            pages = [
                by_title[title]
                for title in query["titles"][0].split("|")
                if title in by_title
            ]
            self._json({"query": {"pages": pages}})
            return

        if query.get("list") == ["allpages"]:
            namespace = int(query["apnamespace"][0])
            continuation = query.get("apcontinue", [None])[0]
            if namespace == 0 and continuation is None:
                self._json(
                    {
                        "continue": {"continue": "-||", "apcontinue": "Wilson-next"},
                        "query": {"allpages": [PAGES[1]]},
                    }
                )
                return
            if namespace == 0:
                self._json({"query": {"allpages": []}})
                return
            page_id = 2 if namespace == 14 else 3
            self._json({"query": {"allpages": [PAGES[page_id]]}})
            return

        if query.get("prop") == ["info|revisions"]:
            page_id = int(query["pageids"][0])
            page = dict(PAGES[page_id])
            content = {
                1: "'''Wilson''' is a character.",
                2: "A category for characters.",
                3: "The original Wilson portrait.",
                10: (
                    "{{Object Infobox|image=Science Machine.png|"
                    "ingredient1=Grass|multiplier1=1}}"
                ),
                11: "'''Twigs''' are a resource.",
            }[page_id]
            page["revisions"] = [
                {
                    "revid": 100 + page_id,
                    "timestamp": "2026-07-01T10:00:00Z",
                    "sha1": "sha1-{}".format(page_id),
                    "contentmodel": "wikitext",
                    "slots": {"main": {"content": content}},
                }
            ]
            self._json({"query": {"pages": [page]}})
            return

        if query.get("action") == ["parse"]:
            page_id = int(query["pageid"][0])
            if self.server.fail_page_id == page_id:
                self._json(
                    {"error": {"code": "permissiondenied", "info": "fixture failure"}}
                )
                return
            parsed = {
                "title": PAGES[page_id]["title"],
                "displaytitle": PAGES[page_id]["title"],
                "text": {
                    1: "<p><b>Wilson</b> is a character.</p>",
                    2: "<p>A category for characters.</p>",
                    3: "<p>The original Wilson portrait.</p>",
                    10: "<p><b>Cut Grass</b> is a resource.</p>",
                    11: "<p><b>Twigs</b> are a resource.</p>",
                }[page_id],
                "links": [],
                "categories": [],
                "images": [],
            }
            if page_id == 1:
                parsed.update(
                    {
                        "links": [
                            {"ns": 6, "title": "File:Wilson.png", "exists": True},
                            {"ns": 10, "title": "Template:Infobox", "exists": True},
                            {"ns": 0, "title": "Missing page"},
                        ],
                        "categories": [{"category": "Characters"}],
                        "images": ["Wilson.png", "Wilson.png"],
                    }
                )
            elif page_id in (10, 11):
                parsed["images"] = [
                    "Unrelated Navbox.png",
                    "{}.png".format(PAGES[page_id]["title"]),
                ]
                if page_id == 10:
                    parsed["categories"] = [{"category": "Structures"}]
            self._json({"parse": parsed})
            return

        if query.get("prop") == ["imageinfo"]:
            title = query["titles"][0]
            filename = title.removeprefix("File:").replace(" ", "_")
            self._json(
                {
                    "query": {
                        "pages": [
                            {
                                "pageid": 3,
                                "ns": 6,
                                "title": title,
                                "imageinfo": [
                                    {
                                        "url": self.server.base_url + "images/" + filename,
                                        "size": len(("original:/images/" + filename).encode("utf-8")),
                                        "width": 64,
                                        "height": 64,
                                        "mime": "image/png",
                                        "sha1": "image-sha1",
                                    }
                                ],
                            }
                        ]
                    }
                }
            )
            return

        self._json({"error": {"code": "badrequest", "info": "unknown query"}})


class CrawlerServer:
    def __enter__(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _CrawlerHandler)
        self.server.base_url = "http://127.0.0.1:{}/".format(
            self.server.server_port
        )
        self.server.fail_page_id = None
        self.base_url = self.server.base_url
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


def _records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


class CategoryClient:
    base_url = "https://dontstarve.fandom.com/"
    api_url = "https://dontstarve.fandom.com/api.php"

    def __init__(self, batches, infobox_image=False, article_image=False):
        self.batches = list(batches)
        self.infobox_image = infobox_image
        self.article_image = article_image
        self.category_calls = []
        self.page_calls = []
        self.parsed_titles = []
        self.pages = {
            1: {"pageid": 1, "ns": 0, "title": "Beefalo"},
            4: {"pageid": 4, "ns": 0, "title": "Bunnyman"},
        }

    def list_category_members(self, title, continuation=None):
        self.category_calls.append((title, continuation))
        return self.batches.pop(0)

    def resolve_titles_detailed(self, titles):
        by_title = {value["title"]: value for value in self.pages.values()}
        return [
            ResolvedTitle(
                requested_title=title,
                page_id=by_title[title]["pageid"],
                namespace=0,
                canonical_title=title,
                canonical_url="https://dontstarve.fandom.com/wiki/{}".format(
                    title.replace(" ", "_")
                ),
                page=by_title[title],
            )
            for title in titles
        ]

    def get_page(self, page_id):
        page = dict(self.pages[page_id])
        self.page_calls.append(page_id)
        content = "'''{}'''".format(page["title"])
        if self.infobox_image:
            content = (
                "{{Mob Infobox\n"
                "|image=<gallery>\n"
                "{} Primary.png|Normal\n"
                "{}.png|Other\n"
                "</gallery>\n"
                "|health=500\n"
                "}}"
            ).format(page["title"], page["title"])
        page["revisions"] = [
            {
                "revid": 100 + page_id,
                "timestamp": "2026-07-01T00:00:00Z",
                "sha1": "sha1-{}".format(page_id),
                "contentmodel": "wikitext",
                "slots": {"main": {"content": content}},
            }
        ]
        return page

    def parse_page(self, page_id):
        title = self.pages[page_id]["title"]
        self.parsed_titles.append(title)
        if self.infobox_image:
            text = (
                "<img alt='Navigation.png'>"
                "<aside class='portable-infobox'>"
                "<img alt='{}.png'><img alt='{} Primary.png'>"
                "</aside>".format(
                    title, title
                )
            )
            images = [
                "Navigation.png",
                "{}.png".format(title),
                "{} Primary.png".format(title),
            ]
        elif self.article_image:
            text = (
                "<div class='notice'><img data-image-name='Icon Books.png' "
                "width='40' height='49'></div>"
                "<figure><img data-image-name='{} Guide.png' "
                "width='320' height='180'></figure>"
                "<table class='navbox'><img data-image-name='Navigation.png' "
                "width='600' height='400'></table>"
            ).format(title)
            images = [
                "Icon Books.png",
                "{} Guide.png".format(title),
                "Navigation.png",
            ]
        else:
            text = "<aside class='portable-infobox'><p>{}</p></aside>".format(title)
            images = []
        return {
            "title": title,
            "displaytitle": title,
            "text": text,
            "links": [],
            "categories": [],
            "images": images,
        }


def category_config(
    expected_direct_pages=3,
    expected_published_pages=2,
    excluded_titles=(("Blue Whale", "non_dst:shipwrecked"),),
    item_type="mob",
):
    return CategoryConfig(
        key="animals",
        source_url="https://dontstarve.fandom.com/wiki/Category:Animals",
        category_title="Category:Animals",
        expected_direct_pages=expected_direct_pages,
        expected_published_pages=expected_published_pages,
        allowed_namespaces=(0,),
        excluded_titles=excluded_titles,
        game="DST",
        item_type=item_type,
        tags=("Animals",),
    )


class CrawlerTests(unittest.TestCase):
    def test_selects_largest_article_image_outside_notice_and_navigation(self):
        parsed = {
            "images": [
                "Icon Books.png",
                "Map_Icon.png",
                "Charlie_Closeup.PNG",
                "Navigation.png",
            ],
            "text": """
                <div class="notice">
                  <img data-image-name="Icon Books.png" width="40" height="49">
                </div>
                <p>Guide introduction.</p>
                <figure>
                  <img data-image-name="Map Icon.png" width="137" height="137">
                </figure>
                <figure>
                  <img data-image-name="Charlie Closeup.PNG" width="284" height="284">
                </figure>
                <table class="navbox">
                  <img data-image-name="Navigation.png" width="500" height="500">
                </table>
            """,
        }

        self.assertEqual(
            select_primary_article_image(parsed),
            "File:Charlie_Closeup.PNG",
        )

    def test_accepts_wide_article_cover_with_one_dimension_below_96(self):
        parsed = {
            "images": ["Beefalo_Tendencies.jpg"],
            "text": (
                "<figure><img data-image-name='Beefalo Tendencies.jpg' "
                "width='180' height='89'></figure>"
            ),
        }

        self.assertEqual(
            select_primary_article_image(parsed),
            "File:Beefalo_Tendencies.jpg",
        )

    def test_rejects_article_images_that_are_only_small_icons(self):
        parsed = {
            "images": ["Carrots.png", "Twigs.png"],
            "text": """
                <p>Guide introduction.</p>
                <img data-image-name="Carrots.png" width="32" height="32">
                <img data-image-name="Twigs.png" width="40" height="40">
            """,
        }

        self.assertIsNone(select_primary_article_image(parsed))

    def test_category_crawler_skips_doing_then_reuses_when_owner_completes(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            url = "https://dontstarve.fandom.com/wiki/Beefalo"
            registry = UrlRegistry(
                root / "fandom-url-registry.json",
                root / "shared-pages",
                "https://dontstarve.fandom.com",
            )
            owner = registry.claim(url, "other-category", "worker-other")
            client = CategoryClient(
                [([{"pageid": 1, "ns": 0, "title": "Beefalo"}], None)]
            )
            one_page = category_config(1, 1, ())
            output = root / "animals"

            with CrawlStorage(
                output,
                client.base_url,
                (0,),
                profile="category:animals",
            ) as storage:
                first = CategoryCrawler(
                    client,
                    storage,
                    one_page,
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-animals",
                ).run({"profile": "category"})

            self.assertEqual(first.pages, 0)
            self.assertEqual(first.pending_pages, 1)
            self.assertEqual(client.page_calls, [])
            registry.complete(
                owner,
                {
                    "page": {
                        "schema_version": 1,
                        "page_id": 1,
                        "namespace": 0,
                        "title": "Beefalo",
                        "canonical_url": url,
                    },
                    "links": [],
                    "imageTitles": [],
                },
            )

            with CrawlStorage(
                output,
                client.base_url,
                (0,),
                profile="category:animals",
            ) as storage:
                second = CategoryCrawler(
                    client,
                    storage,
                    one_page,
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-animals",
                ).run({"profile": "category"})

            self.assertEqual(second.pages, 1)
            self.assertEqual(second.pending_pages, 0)
            self.assertEqual(client.page_calls, [])

    def test_category_crawler_selects_infobox_image_not_navigation_image(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            client = CategoryClient(
                [([{"pageid": 1, "ns": 0, "title": "Beefalo"}], None)],
                infobox_image=True,
            )
            registry = UrlRegistry(
                root / "fandom-url-registry.json",
                root / "shared-pages",
                "https://dontstarve.fandom.com",
            )
            with CrawlStorage(
                root / "animals",
                client.base_url,
                (0,),
                profile="category:animals",
            ) as storage:
                CategoryCrawler(
                    client,
                    storage,
                    category_config(1, 1, ()),
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-animals",
                ).run({"profile": "category"})

            row = json.loads(registry.path.read_text())["items"][0]
            shared = registry.load_payload(registry.claim(row["url"], "animals", "reader").record)
            self.assertEqual(shared["imageTitles"], ["File:Beefalo Primary.png"])

    def test_category_crawler_selects_article_cover_for_guides(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            client = CategoryClient(
                [([{"pageid": 1, "ns": 0, "title": "Beefalo"}], None)],
                article_image=True,
            )
            registry = UrlRegistry(
                root / "fandom-url-registry.json",
                root / "shared-pages",
                "https://dontstarve.fandom.com",
            )
            with CrawlStorage(
                root / "guides",
                client.base_url,
                (0,),
                profile="category:guides",
            ) as storage:
                CategoryCrawler(
                    client,
                    storage,
                    category_config(1, 1, (), item_type="guide"),
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-guides",
                ).run({"profile": "category"})

            row = json.loads(registry.path.read_text())["items"][0]
            shared = registry.load_payload(
                registry.claim(row["url"], "guides", "reader").record
            )
            self.assertEqual(shared["imageTitles"], ["File:Beefalo Guide.png"])

    def test_category_crawler_discovers_all_members_but_queues_only_dst_pages(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            output = root / "animals"
            client = CategoryClient(
                [
                    ([{"pageid": 1, "ns": 0, "title": "Beefalo"}], "next"),
                    (
                        [
                            {"pageid": 2, "ns": 14, "title": "Category:Birds"},
                            {"pageid": 3, "ns": 0, "title": "Blue Whale"},
                            {"pageid": 4, "ns": 0, "title": "Bunnyman"},
                        ],
                        None,
                    ),
                ]
            )
            registry = UrlRegistry(
                root / "fandom-url-registry.json",
                root / "shared-pages",
                "https://dontstarve.fandom.com",
                clock=lambda: "2026-07-21T00:00:00Z",
            )
            with CrawlStorage(
                output,
                client.base_url,
                (0,),
                profile="category:animals",
                clock=lambda: "2026-07-21T00:00:00Z",
            ) as storage:
                summary = CategoryCrawler(
                    client,
                    storage,
                    category_config(),
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-animals",
                    clock=lambda: "2026-07-21T00:00:00Z",
                ).run({"profile": "category"})

            self.assertEqual(
                client.category_calls,
                [("Category:Animals", None), ("Category:Animals", "next")],
            )
            self.assertEqual(summary.pages, 1)
            self.assertEqual(summary.pending_pages, 1)
            self.assertEqual(client.parsed_titles, ["Beefalo"])
            self.assertNotIn("Blue Whale", client.parsed_titles)
            seeds = _records(output / "seeds.jsonl")
            self.assertEqual(sum(seed["accepted"] for seed in seeds), 2)
            registry_rows = json.loads(registry.path.read_text())["items"]
            self.assertEqual(len(registry_rows), 2)
            self.assertEqual(
                {row["status"] for row in registry_rows},
                {"New", "Done"},
            )

    def test_category_crawler_reuses_done_shared_payload_without_fetching(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry = UrlRegistry(
                root / "fandom-url-registry.json",
                root / "shared-pages",
                "https://dontstarve.fandom.com",
                clock=lambda: "2026-07-21T00:00:00Z",
            )
            claim = registry.claim(
                "https://dontstarve.fandom.com/wiki/Beefalo",
                "other-category",
                "worker-other",
            )
            registry.complete(
                claim,
                {
                    "page": {
                        "schema_version": 1,
                        "page_id": 1,
                        "namespace": 0,
                        "title": "Beefalo",
                        "canonical_url": "https://dontstarve.fandom.com/wiki/Beefalo",
                    },
                    "links": [],
                    "imageTitles": [],
                },
            )
            client = CategoryClient(
                [
                    (
                        [
                            {"pageid": 1, "ns": 0, "title": "Beefalo"},
                            {"pageid": 3, "ns": 0, "title": "Blue Whale"},
                            {"pageid": 4, "ns": 0, "title": "Bunnyman"},
                        ],
                        None,
                    )
                ]
            )
            with CrawlStorage(
                root / "animals",
                client.base_url,
                (0,),
                profile="category:animals",
            ) as storage:
                CategoryCrawler(
                    client,
                    storage,
                    category_config(),
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-animals",
                ).run({"profile": "category"})

            self.assertEqual(client.page_calls, [])
            self.assertEqual(_records(root / "animals" / "pages.jsonl")[0]["title"], "Beefalo")

    def test_category_crawler_repairs_missing_guide_cover_from_reused_page(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry = UrlRegistry(
                root / "fandom-url-registry.json",
                root / "shared-pages",
                "https://dontstarve.fandom.com",
            )
            url = "https://dontstarve.fandom.com/wiki/Beefalo"
            claim = registry.claim(url, "other-category", "worker-other")
            registry.complete(
                claim,
                {
                    "page": {
                        "schema_version": 1,
                        "page_id": 1,
                        "namespace": 0,
                        "title": "Beefalo",
                        "canonical_url": url,
                        "html": (
                            "<figure><img data-image-name='Beefalo Guide.png' "
                            "width='320' height='180'></figure>"
                        ),
                        "images": ["Beefalo Guide.png"],
                    },
                    "links": [],
                    "imageTitles": [],
                },
            )
            client = CategoryClient(
                [([{"pageid": 1, "ns": 0, "title": "Beefalo"}], None)]
            )
            with CrawlStorage(
                root / "guides",
                client.base_url,
                (0,),
                profile="category:guides",
            ) as storage:
                summary = CategoryCrawler(
                    client,
                    storage,
                    category_config(1, 1, (), item_type="guide"),
                    registry,
                    page_budget=1,
                    skip_images=True,
                    worker_id="worker-guides",
                ).run({"profile": "category"})

            self.assertEqual(client.page_calls, [])
            self.assertEqual(summary.pending_images, 1)
    def make_client(self, server):
        return MediaWikiClient(
            server.base_url,
            delay=0,
            timeout=2,
            max_attempts=2,
            jitter=lambda: 0,
            require_https_downloads=False,
        )

    def make_storage(self, output, server):
        return CrawlStorage(
            output,
            server.base_url,
            (0, 14, 6),
            clock=lambda: "2026-07-15T00:00:00Z",
        )

    def make_item_storage(self, output, server):
        return CrawlStorage(
            output,
            server.base_url,
            (0,),
            clock=lambda: "2026-07-15T00:00:00Z",
        )

    def test_selective_items_resume_and_download_seed_and_structure_images(self):
        with CrawlerServer() as server, tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            with self.make_item_storage(output, server) as storage:
                first = SelectiveItemsCrawler(
                    self.make_client(server),
                    storage,
                    item_budget=1,
                    clock=lambda: "2026-07-15T00:00:00Z",
                ).run({"profile": "items"})

            self.assertEqual(first.pages, 1)
            self.assertEqual(first.images, 2)
            self.assertEqual(first.pending_pages, 1)
            self.assertEqual(
                [record["title"] for record in _records(output / "pages.jsonl")],
                ["Cut Grass"],
            )
            self.assertEqual(
                [record["title"] for record in _records(output / "images.jsonl")],
                ["File:Cut Grass.png", "File:Science Machine.png"],
            )

            with self.make_item_storage(output, server) as storage:
                second = SelectiveItemsCrawler(
                    self.make_client(server),
                    storage,
                    item_budget=1,
                    clock=lambda: "2026-07-16T00:00:00Z",
                ).run({"profile": "items"})

            self.assertEqual(second.pages, 2)
            self.assertEqual(second.images, 3)
            self.assertEqual(second.pending_pages, 0)
            self.assertEqual(
                {record["title"] for record in _records(output / "images.jsonl")},
                {
                    "File:Cut Grass.png",
                    "File:Science Machine.png",
                    "File:Twigs.png",
                },
            )
            self.assertEqual(len(_records(output / "seeds.jsonl")), 2)
            recipes = _records(output / "recipes.jsonl")
            self.assertEqual(len(recipes), 1)
            self.assertEqual(recipes[0]["result"], "Cut Grass")

    def test_crawls_all_namespaces_links_and_original_image(self):
        with CrawlerServer() as server, tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            with self.make_storage(output, server) as storage:
                summary = WikiCrawler(
                    self.make_client(server),
                    storage,
                    (0, 14, 6),
                    clock=lambda: "2026-07-15T00:00:00Z",
                ).run({"skip_images": False})

            pages = _records(output / "pages.jsonl")
            links = _records(output / "links.jsonl")
            pages_by_title = {page["title"]: page for page in pages}
            self.assertEqual(summary.pages, 3)
            self.assertEqual(summary.images, 1)
            self.assertEqual(summary.failures, 0)
            self.assertEqual(
                set(pages_by_title),
                {"Wilson", "Category:Characters", "File:Wilson.png"},
            )
            self.assertEqual(
                pages_by_title["Wilson"]["wikitext"],
                "'''Wilson''' is a character.",
            )
            self.assertIn(
                "Wilson is a character.",
                pages_by_title["Wilson"]["plain_text"],
            )
            self.assertTrue(
                any(
                    link["target_title"] == "Template:Infobox"
                    and not link["in_scope"]
                    for link in links
                )
            )
            self.assertTrue(
                any(
                    link["target_title"] == "Missing page"
                    and not link["exists"]
                    for link in links
                )
            )
            self.assertEqual(
                len(list((output / "images" / "original").iterdir())), 1
            )

    def test_records_failure_then_resumes_without_duplicate_records(self):
        with CrawlerServer() as server, tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            server.server.fail_page_id = 2
            with self.make_storage(output, server) as storage:
                first = WikiCrawler(
                    self.make_client(server),
                    storage,
                    (0, 14, 6),
                    skip_images=True,
                    clock=lambda: "2026-07-15T00:00:00Z",
                ).run({"skip_images": True})
            self.assertEqual(first.pages, 2)
            self.assertEqual(first.failures, 1)

            server.server.fail_page_id = None
            with self.make_storage(output, server) as storage:
                storage.retry_errors()
                second = WikiCrawler(
                    self.make_client(server),
                    storage,
                    (0, 14, 6),
                    skip_images=True,
                    clock=lambda: "2026-07-16T00:00:00Z",
                ).run({"skip_images": True})

            pages = _records(output / "pages.jsonl")
            self.assertEqual(second.pages, 3)
            self.assertEqual(second.failures, 0)
            self.assertEqual(len({page["page_id"] for page in pages}), 3)
            self.assertEqual(len(pages), 3)
            self.assertEqual((output / "errors.jsonl").read_text(), "")


if __name__ == "__main__":
    unittest.main()
