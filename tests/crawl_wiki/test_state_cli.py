import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.crawl_wiki.state_cli import main
from tools.crawl_wiki.state_paths import CategoryStatePaths, StatePathError
from tools.crawl_wiki.url_registry import RegistryAudit, UrlRecord


def record(status="New"):
    return UrlRecord(
        url="https://dontstarve.fandom.com/wiki/Beefalo",
        status=status,
        categories=("animals",),
        worker_id=None,
        attempts=1,
        created_at="2026-07-21T10:00:00Z",
        updated_at="2026-07-21T10:00:00Z",
        claimed_at=None,
        completed_at=None,
        artifact_path=None,
        artifact_sha256=None,
        last_error=None,
    )


class StateCliTests(unittest.TestCase):
    def test_init_imports_and_exports_snapshot(self):
        snapshot = Path("tracked.json")
        stdout = io.StringIO()
        with patch(
            "tools.crawl_wiki.state_cli.resolve_category_state_paths",
            return_value=CategoryStatePaths(Path("live.json"), Path("cache")),
        ), patch("tools.crawl_wiki.state_cli.UrlRegistry") as registry, redirect_stdout(
            stdout
        ):
            registry.return_value.initialize_from_snapshot.return_value = 29
            registry.return_value.export_snapshot.return_value = 29

            result = main(["init", "--snapshot", str(snapshot)])

        self.assertEqual(result, 0)
        registry.return_value.initialize_from_snapshot.assert_called_once_with(snapshot)
        registry.return_value.export_snapshot.assert_called_once_with(snapshot)
        self.assertIn("initialized=29 snapshot=29", stdout.getvalue())

    def test_audit_returns_one_for_invalid_rows(self):
        stdout = io.StringIO()
        audits = (
            RegistryAudit(
                "https://dontstarve.fandom.com/wiki/Beefalo",
                "Done",
                None,
            ),
            RegistryAudit(
                "https://dontstarve.fandom.com/wiki/Rabbit",
                "Done",
                "missing",
            ),
        )
        with patch(
            "tools.crawl_wiki.state_cli.resolve_category_state_paths",
            return_value=CategoryStatePaths(Path("live.json"), Path("cache")),
        ), patch("tools.crawl_wiki.state_cli.UrlRegistry") as registry, redirect_stdout(
            stdout
        ):
            registry.return_value.audit.return_value = audits

            result = main(["audit"])

        self.assertEqual(result, 1)
        self.assertIn("urls=2 valid=1 invalid=1", stdout.getvalue())
        self.assertIn("Done missing", stdout.getvalue())

    def test_repair_exports_snapshot_without_touching_doing(self):
        snapshot = Path("tracked.json")
        stdout = io.StringIO()
        with patch(
            "tools.crawl_wiki.state_cli.resolve_category_state_paths",
            return_value=CategoryStatePaths(Path("live.json"), Path("cache")),
        ), patch("tools.crawl_wiki.state_cli.UrlRegistry") as registry, redirect_stdout(
            stdout
        ):
            registry.return_value.repair_invalid_done.return_value = (record(),)
            registry.return_value.export_snapshot.return_value = 30

            result = main(["repair", "--snapshot", str(snapshot)])

        self.assertEqual(result, 0)
        registry.return_value.repair_invalid_done.assert_called_once_with()
        registry.return_value.export_snapshot.assert_called_once_with(snapshot)
        self.assertIn("repaired=1 snapshot=30", stdout.getvalue())

    def test_snapshot_only_exports_current_live_state(self):
        snapshot = Path("tracked.json")
        with patch(
            "tools.crawl_wiki.state_cli.resolve_category_state_paths",
            return_value=CategoryStatePaths(Path("live.json"), Path("cache")),
        ), patch("tools.crawl_wiki.state_cli.UrlRegistry") as registry, redirect_stdout(
            io.StringIO()
        ):
            registry.return_value.export_snapshot.return_value = 30

            result = main(["snapshot", "--snapshot", str(snapshot)])

        self.assertEqual(result, 0)
        registry.return_value.export_snapshot.assert_called_once_with(snapshot)
        registry.return_value.audit.assert_not_called()

    def test_requires_paired_path_overrides(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = main(["--url-registry", "live.json", "audit"])

        self.assertEqual(result, 2)
        self.assertIn("together", stderr.getvalue())

    def test_maps_fatal_state_error_to_exit_two(self):
        stderr = io.StringIO()
        with patch(
            "tools.crawl_wiki.state_cli.resolve_category_state_paths",
            side_effect=StatePathError("not a repository"),
        ), redirect_stderr(stderr):
            result = main(["audit"])

        self.assertEqual(result, 2)
        self.assertIn("not a repository", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
