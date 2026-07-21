import hashlib
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

    def test_audit_accepts_valid_done_artifact(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            url = "https://dontstarve.fandom.com/wiki/Beefalo"
            claim = registry.claim(url, "animals", "worker")
            registry.complete(claim, {"page": {"title": "Beefalo"}})

            audit = registry.audit()

            self.assertEqual(len(audit), 1)
            self.assertEqual(audit[0].url, url)
            self.assertEqual(audit[0].status, "Done")
            self.assertIsNone(audit[0].issue)

    def test_audit_and_repair_missing_done_artifact(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            url = "https://dontstarve.fandom.com/wiki/Beefalo"
            claim = registry.claim(url, "animals", "worker")
            registry.claim(url, "cave_creatures", "other-worker")
            completed = registry.complete(claim, {"page": {"title": "Beefalo"}})
            (registry.path.parent / completed.artifact_path).unlink()

            audit = registry.audit()
            repaired = registry.repair_invalid_done()

            self.assertEqual(audit[0].issue, "missing")
            self.assertEqual(repaired[0].status, "New")
            self.assertEqual(
                repaired[0].categories,
                ("animals", "cave_creatures"),
            )
            self.assertEqual(repaired[0].attempts, 1)
            self.assertIsNone(repaired[0].artifact_path)
            self.assertEqual(
                repaired[0].last_error,
                "requeued invalid Done: missing",
            )

    def test_audit_classifies_checksum_and_json_failures(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry = self.make_registry(root)
            first = registry.claim(
                "https://dontstarve.fandom.com/wiki/Beefalo",
                "animals",
                "worker-a",
            )
            first_done = registry.complete(first, {"page": {"title": "Beefalo"}})
            first_path = registry.path.parent / first_done.artifact_path
            first_path.write_text('{"page": {"title": "Changed"}}\n', encoding="utf-8")

            second = registry.claim(
                "https://dontstarve.fandom.com/wiki/Bunnyman",
                "animals",
                "worker-b",
            )
            second_done = registry.complete(second, {"page": {"title": "Bunnyman"}})
            second_path = registry.path.parent / second_done.artifact_path
            second_path.write_text("not-json", encoding="utf-8")
            stored = json.loads(registry.path.read_text(encoding="utf-8"))
            second_row = next(
                row for row in stored["items"] if row["url"].endswith("/Bunnyman")
            )
            second_row["artifactSha256"] = hashlib.sha256(
                second_path.read_bytes()
            ).hexdigest()
            registry._write(stored)

            issues = {entry.url: entry.issue for entry in registry.audit()}

            self.assertEqual(issues[first_done.url], "checksum_error")
            self.assertEqual(issues[second_done.url], "invalid_json")

    def test_audit_requires_done_payload_to_be_an_object(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            claim = registry.claim(
                "https://dontstarve.fandom.com/wiki/Rabbit",
                "animals",
                "worker",
            )
            completed = registry.complete(claim, {"page": {"title": "Rabbit"}})
            artifact = registry.path.parent / completed.artifact_path
            artifact.write_text("[]\n", encoding="utf-8")
            stored = json.loads(registry.path.read_text(encoding="utf-8"))
            stored["items"][0]["artifactSha256"] = hashlib.sha256(
                artifact.read_bytes()
            ).hexdigest()
            registry._write(stored)

            self.assertEqual(registry.audit()[0].issue, "invalid_json")

    def test_audit_reports_invalid_state_metadata(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            claim = registry.claim(
                "https://dontstarve.fandom.com/wiki/Rabbit",
                "animals",
                "worker",
            )
            registry.complete(claim, {"page": {"title": "Rabbit"}})
            stored = json.loads(registry.path.read_text(encoding="utf-8"))
            stored["items"][0]["artifactSha256"] = None
            registry._write(stored)

            self.assertEqual(registry.audit()[0].issue, "invalid_state")

    def test_repair_preserves_doing_rows(self):
        with tempfile.TemporaryDirectory() as tempdir:
            registry = self.make_registry(Path(tempdir))
            claim = registry.claim(
                "https://dontstarve.fandom.com/wiki/Rabbit",
                "animals",
                "worker",
            )

            repaired = registry.repair_invalid_done()
            stored = json.loads(registry.path.read_text(encoding="utf-8"))["items"][0]

            self.assertEqual(repaired, ())
            self.assertEqual(stored["status"], "Doing")
            self.assertEqual(stored["workerId"], claim.record.worker_id)

    def test_initialize_snapshot_imports_rows_as_new(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            snapshot_registry = self.make_registry(root / "snapshot")
            claim = snapshot_registry.claim(
                "https://dontstarve.fandom.com/wiki/Beefalo",
                "animals",
                "worker",
            )
            snapshot_registry.complete(claim, {"page": {"title": "Beefalo"}})
            live_registry = self.make_registry(root / "live")

            count = live_registry.initialize_from_snapshot(snapshot_registry.path)
            imported = json.loads(
                live_registry.path.read_text(encoding="utf-8")
            )["items"][0]

            self.assertEqual(count, 1)
            self.assertEqual(imported["status"], "New")
            self.assertEqual(imported["categories"], ["animals"])
            self.assertEqual(imported["attempts"], 1)
            self.assertIsNone(imported["workerId"])
            self.assertIsNone(imported["claimedAt"])
            self.assertIsNone(imported["completedAt"])
            self.assertIsNone(imported["artifactPath"])
            self.assertIsNone(imported["artifactSha256"])
            self.assertEqual(
                imported["lastError"],
                "imported from snapshot without raw artifact",
            )

    def test_initialize_refuses_to_overwrite_existing_live_registry(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            snapshot = root / "snapshot.json"
            snapshot.write_text(
                json.dumps({"schemaVersion": 1, "items": []}),
                encoding="utf-8",
            )
            registry = self.make_registry(root / "live")
            registry.register(
                "https://dontstarve.fandom.com/wiki/Rabbit",
                "animals",
            )

            with self.assertRaisesRegex(UrlRegistryError, "already exists"):
                registry.initialize_from_snapshot(snapshot)

    def test_export_snapshot_is_stable_and_preserves_statuses(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            registry = self.make_registry(root / "live")
            registry.register(
                "https://dontstarve.fandom.com/wiki/Rabbit",
                "animals",
            )
            claim = registry.claim(
                "https://dontstarve.fandom.com/wiki/Beefalo",
                "animals",
                "worker",
            )
            registry.complete(claim, {"page": {"title": "Beefalo"}})
            target = root / "snapshot.json"

            count = registry.export_snapshot(target)
            exported = json.loads(target.read_text(encoding="utf-8"))

            self.assertEqual(count, 2)
            self.assertEqual(
                [row["url"].rsplit("/", 1)[-1] for row in exported["items"]],
                ["Beefalo", "Rabbit"],
            )
            self.assertEqual(
                [row["status"] for row in exported["items"]],
                ["Done", "New"],
            )


if __name__ == "__main__":
    unittest.main()
