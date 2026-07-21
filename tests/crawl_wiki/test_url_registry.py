import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

from tools.crawl_wiki.url_registry import (
    UrlRegistry,
    UrlRegistryError,
    normalize_crawler_url,
)


ORIGIN = "https://dontstarve.fandom.com"


class UrlRegistryTests(unittest.TestCase):
    def make_registry(self, root: Path, clock=None) -> UrlRegistry:
        return UrlRegistry(
            root / "fandom-url-registry.json",
            root / "fandom-shared-pages",
            ORIGIN,
            clock=clock or (lambda: "2026-07-21T10:00:00Z"),
        )

    def test_normalizes_page_url_and_rejects_another_origin(self):
        self.assertEqual(
            normalize_crawler_url(
                "https://DONTSTARVE.fandom.com/wiki/Blue%20Whale#Behavior",
                ORIGIN,
            ),
            "https://dontstarve.fandom.com/wiki/Blue_Whale",
        )
        with self.assertRaisesRegex(UrlRegistryError, "origin"):
            normalize_crawler_url(
                "https://example.com/wiki/Beefalo",
                ORIGIN,
            )

    def test_registers_missing_url_as_new_without_duplicate_categories(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry = self.make_registry(root)

            first = registry.register(
                "https://dontstarve.fandom.com/wiki/Beefalo",
                "animals",
            )
            second = registry.register(
                "https://dontstarve.fandom.com/wiki/Beefalo#Stats",
                "animals",
            )

            self.assertEqual(first.status, "New")
            self.assertEqual(second.categories, ("animals",))
            payload = json.loads(registry.path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(len(payload["items"]), 1)

    def test_claim_complete_and_reuse_preserve_all_categories(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry = self.make_registry(root)
            url = "https://dontstarve.fandom.com/wiki/Beefalo"

            claimed = registry.claim(url, "animals", "worker-animals")
            busy = registry.claim(url, "mobs", "worker-mobs")
            completed = registry.complete(
                claimed,
                {"page": {"page_id": 1, "title": "Beefalo"}},
            )
            reused = registry.claim(url, "creatures", "worker-creatures")

            self.assertEqual(claimed.decision, "crawl")
            self.assertEqual(claimed.record.status, "Doing")
            self.assertEqual(busy.decision, "busy")
            self.assertEqual(completed.status, "Done")
            self.assertEqual(reused.decision, "reuse")
            self.assertEqual(
                reused.record.categories,
                ("animals", "creatures", "mobs"),
            )
            self.assertEqual(
                registry.load_payload(reused.record),
                {"page": {"page_id": 1, "title": "Beefalo"}},
            )

    def test_only_claim_owner_can_release_and_retry(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            url = "https://dontstarve.fandom.com/wiki/Bunnyman"
            claimed = registry.claim(url, "animals", "worker-a")

            with self.assertRaisesRegex(UrlRegistryError, "owner"):
                registry.release(claimed.with_worker("worker-b"), "wrong")

            released = registry.release(claimed, "temporary failure")
            retried = registry.claim(url, "animals", "worker-b")
            self.assertEqual(released.status, "New")
            self.assertEqual(released.last_error, "temporary failure")
            self.assertEqual(retried.decision, "crawl")
            self.assertEqual(retried.record.attempts, 2)

    def test_two_registry_instances_allow_only_one_worker_to_crawl(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            first = self.make_registry(root)
            second = self.make_registry(root)
            url = "https://dontstarve.fandom.com/wiki/Koalefant"
            barrier = Barrier(2)

            def claim(registry, category, worker):
                barrier.wait()
                return registry.claim(url, category, worker)

            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(
                    executor.map(
                        lambda values: claim(*values),
                        [
                            (first, "animals", "worker-a"),
                            (second, "mobs", "worker-b"),
                        ],
                    )
                )

            self.assertEqual(
                sorted(result.decision for result in results),
                ["busy", "crawl"],
            )
            stored = json.loads(first.path.read_text(encoding="utf-8"))
            self.assertEqual(stored["items"][0]["categories"], ["animals", "mobs"])

    def test_operator_can_requeue_stuck_doing_url_with_owner_guard(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            url = "https://dontstarve.fandom.com/wiki/Rabbit"
            registry.claim(url, "animals", "worker-a")

            with self.assertRaisesRegex(UrlRegistryError, "owner"):
                registry.requeue(url, expected_worker_id="worker-b")

            requeued = registry.requeue(url, expected_worker_id="worker-a")
            retried = registry.claim(url, "animals", "worker-b")
            self.assertEqual(requeued.status, "New")
            self.assertEqual(requeued.last_error, "manually requeued")
            self.assertEqual(retried.decision, "crawl")
            self.assertEqual(retried.record.attempts, 2)


if __name__ == "__main__":
    unittest.main()
