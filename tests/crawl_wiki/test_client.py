import hashlib
import json
import tempfile
import threading
import unittest
import urllib.parse
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tools.crawl_wiki.client import ClientError, MediaWikiClient


class _WikiHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        del format, args

    def _json(self, payload, status=200, headers=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed_url = urllib.parse.urlsplit(self.path)
        if parsed_url.path == "/asset.png":
            body = b"png-bytes"
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed_url.path != "/api.php":
            self.send_error(404)
            return
        if self.server.always_404:
            self._json({"error": "missing"}, status=404)
            return

        query = urllib.parse.parse_qs(parsed_url.query)
        if query.get("list") == ["allpages"]:
            self.server.counts["allpages"] += 1
            if self.server.counts["allpages"] == 1:
                self._json(
                    {"error": "busy"},
                    status=503,
                    headers={"Retry-After": "0"},
                )
                return
            self._json(
                {
                    "continue": {"apcontinue": "next-token", "continue": "-||"},
                    "query": {
                        "allpages": [
                            {"pageid": 1, "ns": 0, "title": "Wilson"}
                        ]
                    },
                }
            )
            return
        if query.get("action") == ["parse"]:
            self.server.counts["parse"] += 1
            if self.server.counts["parse"] == 1:
                self._json(
                    {
                        "error": {
                            "code": "maxlag",
                            "info": "Waiting for replicas",
                            "lag": 1,
                        }
                    }
                )
                return
            self._json({"parse": {"title": "Wilson", "text": "<p>Hi</p>"}})
            return
        if query.get("prop") == ["info|revisions"]:
            self._json(
                {
                    "query": {
                        "pages": [
                            {
                                "pageid": 1,
                                "ns": 0,
                                "title": "Wilson",
                                "revisions": [{"revid": 3}],
                            }
                        ]
                    }
                }
            )
            return
        if query.get("prop") == ["imageinfo"]:
            self._json(
                {
                    "query": {
                        "pages": [
                            {
                                "pageid": 9,
                                "ns": 6,
                                "title": "File:Wilson.png",
                                "imageinfo": [
                                    {
                                        "url": self.server.base_url + "asset.png",
                                        "size": 9,
                                        "width": 2,
                                        "height": 3,
                                        "mime": "image/png",
                                        "sha1": "mediawiki-sha1",
                                    }
                                ],
                            }
                        ]
                    }
                }
            )
            return
        self._json({"error": {"code": "badrequest", "info": "unknown"}})


class WikiServer:
    def __init__(self, always_404=False):
        self.always_404 = always_404

    def __enter__(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _WikiHandler)
        self.server.always_404 = self.always_404
        self.server.counts = Counter()
        self.server.base_url = "http://127.0.0.1:{}/".format(
            self.server.server_port
        )
        self.base_url = self.server.base_url
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        del exc_type, exc_value, traceback
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


class ClientTests(unittest.TestCase):
    def test_retries_http_and_api_errors_and_streams_download(self):
        with WikiServer() as server, tempfile.TemporaryDirectory() as tempdir:
            sleeps = []
            client = MediaWikiClient(
                server.base_url,
                delay=0,
                timeout=2,
                max_attempts=3,
                sleep=sleeps.append,
                jitter=lambda: 0,
                require_https_downloads=False,
            )

            pages, token = client.list_allpages(0)
            self.assertEqual(
                pages, [{"pageid": 1, "ns": 0, "title": "Wilson"}]
            )
            self.assertEqual(token, "next-token")
            self.assertGreaterEqual(server.server.counts["allpages"], 2)
            self.assertEqual(client.get_page(1)["title"], "Wilson")

            parsed = client.parse_page(1)
            self.assertEqual(parsed["title"], "Wilson")
            self.assertTrue(sleeps)

            image = client.get_image_info("File:Wilson.png")
            self.assertEqual(image["title"], "File:Wilson.png")
            target = Path(tempdir) / "asset.part"
            result = client.download(server.base_url + "asset.png", target)
            self.assertEqual(target.read_bytes(), b"png-bytes")
            self.assertEqual(result.byte_size, 9)
            self.assertEqual(
                result.sha256, hashlib.sha256(b"png-bytes").hexdigest()
            )

    def test_does_not_retry_permanent_http_error(self):
        with WikiServer(always_404=True) as server:
            client = MediaWikiClient(
                server.base_url,
                delay=0,
                max_attempts=3,
                require_https_downloads=False,
            )
            with self.assertRaises(ClientError) as raised:
                client.list_allpages(0)
            self.assertFalse(raised.exception.retryable)
            self.assertEqual(raised.exception.status, 404)

    def test_rejects_non_https_original_download(self):
        with WikiServer() as server, tempfile.TemporaryDirectory() as tempdir:
            client = MediaWikiClient(server.base_url, delay=0)
            with self.assertRaises(ClientError) as raised:
                client.download(
                    server.base_url + "asset.png", Path(tempdir) / "asset.part"
                )
            self.assertFalse(raised.exception.retryable)
            self.assertIn("HTTPS", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
