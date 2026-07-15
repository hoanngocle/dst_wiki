import json
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tools.crawl_wiki.client import MediaWikiClient
from tools.crawl_wiki.crawler import SelectiveItemsCrawler, WikiCrawler
from tools.crawl_wiki.storage import CrawlStorage


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
                10: "{{Object Infobox|ingredient1=Grass|multiplier1=1}}",
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


class CrawlerTests(unittest.TestCase):
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

    def test_selective_items_resume_by_budget_and_download_only_seed_icons(self):
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
            self.assertEqual(first.images, 1)
            self.assertEqual(first.pending_pages, 1)
            self.assertEqual(
                [record["title"] for record in _records(output / "pages.jsonl")],
                ["Cut Grass"],
            )
            self.assertEqual(
                [record["title"] for record in _records(output / "images.jsonl")],
                ["File:Cut Grass.png"],
            )

            with self.make_item_storage(output, server) as storage:
                second = SelectiveItemsCrawler(
                    self.make_client(server),
                    storage,
                    item_budget=1,
                    clock=lambda: "2026-07-16T00:00:00Z",
                ).run({"profile": "items"})

            self.assertEqual(second.pages, 2)
            self.assertEqual(second.images, 2)
            self.assertEqual(second.pending_pages, 0)
            self.assertEqual(
                {record["title"] for record in _records(output / "images.jsonl")},
                {"File:Cut Grass.png", "File:Twigs.png"},
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
