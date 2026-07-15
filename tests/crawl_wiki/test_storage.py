import hashlib
import json
import tempfile
import unittest
import weakref
from pathlib import Path
from unittest.mock import patch

import tools.crawl_wiki.storage as storage_module
from tools.crawl_wiki.storage import CrawlStorage, StorageError


def _page(page_id=1, title="Wilson", fetched_at="2026-07-15T00:00:00Z"):
    return {
        "schema_version": 1,
        "page_id": page_id,
        "namespace": 0,
        "namespace_name": "Main",
        "title": title,
        "display_title": title,
        "canonical_url": "https://dontstarve.wiki.gg/wiki/" + title,
        "redirect_target": None,
        "revision": {"id": 3, "timestamp": fetched_at, "sha1": "abc"},
        "content_model": "wikitext",
        "wikitext": title,
        "html": "<p>{}</p>".format(title),
        "plain_text": title,
        "categories": [],
        "links": ["File:Wilson.png"],
        "images": ["File:Wilson.png"],
        "fetched_at": fetched_at,
    }


def _link():
    return {
        "schema_version": 1,
        "source_page_id": 1,
        "source_title": "Wilson",
        "target_title": "File:Wilson.png",
        "target_namespace": 6,
        "exists": True,
        "in_scope": True,
    }


class StorageTests(unittest.TestCase):
    def make_storage(self, output, **kwargs):
        return CrawlStorage(
            output,
            "https://dontstarve.wiki.gg/",
            (0, 14, 6),
            clock=lambda: "2026-07-15T00:00:00Z",
            **kwargs,
        )

    def test_queues_pages_images_and_recovers_processing_after_reopen(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            with self.make_storage(output) as storage:
                self.assertEqual(
                    storage.enqueue_pages(
                        [
                            {"pageid": 1, "ns": 0, "title": "Wilson"},
                            {"pageid": 2, "ns": 14, "title": "Category:People"},
                        ]
                    ),
                    2,
                )
                self.assertEqual(storage.claim_page()["title"], "Wilson")
                storage.complete_page(
                    1, _page(), [_link(), _link()], {"File:Wilson.png"}
                )
                self.assertEqual(
                    storage.claim_image()["title"], "File:Wilson.png"
                )
                self.assertEqual(
                    storage.claim_page()["title"], "Category:People"
                )

            with self.make_storage(output) as storage:
                self.assertEqual(
                    storage.claim_page()["title"], "Category:People"
                )
                self.assertEqual(
                    storage.claim_image()["title"], "File:Wilson.png"
                )

    def test_truncates_incomplete_tail_and_compacts_duplicate_records(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            with self.make_storage(output) as storage:
                storage.enqueue_pages(
                    [{"pageid": 1, "ns": 0, "title": "Wilson"}]
                )
                storage.claim_page()
                storage.complete_page(1, _page(), [_link(), _link()], set())

            with (output / "pages.jsonl").open("ab") as handle:
                handle.write(b'{"page_id":999')

            with self.make_storage(output) as storage:
                self.assertTrue((output / "pages.jsonl").read_bytes().endswith(b"\n"))
                newer = _page(fetched_at="2026-07-16T00:00:00Z")
                with (output / "pages.jsonl").open("ab") as handle:
                    handle.write(
                        (json.dumps(newer, sort_keys=True) + "\n").encode("utf-8")
                    )
                summary = storage.finalize({"skip_images": True})

            pages = [
                json.loads(line)
                for line in (output / "pages.jsonl").read_text().splitlines()
            ]
            links = [
                json.loads(line)
                for line in (output / "links.jsonl").read_text().splitlines()
            ]
            self.assertEqual(len(pages), 1)
            self.assertEqual(
                pages[0]["fetched_at"], "2026-07-16T00:00:00Z"
            )
            self.assertEqual(len(links), 1)
            self.assertEqual(summary.pages, 1)

            index = json.loads((output / "index.json").read_text())
            offset = index["pages"]["by_title"]["Wilson"]
            with (output / "pages.jsonl").open("rb") as handle:
                handle.seek(offset)
                self.assertEqual(json.loads(handle.readline())["title"], "Wilson")

    def test_content_addresses_duplicate_image_bytes(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            expected_hash = hashlib.sha256(b"same-image").hexdigest()
            with self.make_storage(output) as storage:
                paths = []
                for number in (1, 2):
                    part = storage.new_image_part()
                    part.write_bytes(b"same-image")
                    paths.append(
                        storage.commit_image_file(
                            part,
                            expected_hash,
                            "https://cdn.example/image{}.png".format(number),
                            "image/png",
                        )
                    )
                self.assertEqual(paths[0], paths[1])

            originals = list((output / "images" / "original").iterdir())
            self.assertEqual(len(originals), 1)
            self.assertEqual(
                originals[0].name, expected_hash + ".png"
            )

    def test_compaction_streams_page_payloads_instead_of_retaining_them(self):
        class TrackedDict(dict):
            pass

        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            with self.make_storage(output) as storage:
                with (output / "pages.jsonl").open("w", encoding="utf-8") as handle:
                    for page_id in range(1, 21):
                        record = _page(page_id, "Page {}".format(page_id))
                        record["html"] = "x" * 10_000
                        handle.write(json.dumps(record) + "\n")

                original_loads = storage_module.json.loads
                references = []
                peak_live_records = [0]

                def tracking_loads(value, *args, **kwargs):
                    result = original_loads(value, *args, **kwargs)
                    if not isinstance(result, dict):
                        return result
                    tracked = TrackedDict(result)
                    references.append(weakref.ref(tracked))
                    peak_live_records[0] = max(
                        peak_live_records[0],
                        sum(reference() is not None for reference in references),
                    )
                    return tracked

                with patch.object(
                    storage_module.json, "loads", side_effect=tracking_loads
                ):
                    storage.finalize({"skip_images": True})

            self.assertLessEqual(peak_live_records[0], 3)

    def test_finalizes_errors_checksums_and_rejects_fresh_overwrite(self):
        with tempfile.TemporaryDirectory() as tempdir:
            output = Path(tempdir)
            with self.make_storage(output) as storage:
                storage.enqueue_pages(
                    [{"pageid": 1, "ns": 0, "title": "Wilson"}]
                )
                storage.claim_page()
                storage.fail_page(
                    1,
                    {
                        "stage": "page",
                        "subject": "1",
                        "url": "https://dontstarve.wiki.gg/api.php",
                        "error_type": "ClientError",
                        "message": "not found",
                        "status": 404,
                        "code": None,
                        "retryable": False,
                        "timestamp": "2026-07-15T00:00:00Z",
                    },
                )
                summary = storage.finalize({"skip_images": True})

            self.assertEqual(summary.failures, 1)
            errors = (output / "errors.jsonl").read_text().splitlines()
            self.assertEqual(len(errors), 1)
            manifest = json.loads((output / "manifest.json").read_text())
            for filename, expected in manifest["checksums"].items():
                actual = hashlib.sha256((output / filename).read_bytes()).hexdigest()
                self.assertEqual(actual, expected)
            with self.assertRaises(StorageError):
                self.make_storage(output, fresh=True)


if __name__ == "__main__":
    unittest.main()
