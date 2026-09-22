from __future__ import annotations

import unittest
from pathlib import Path

from tools.extract.pham_nhan.discovery import discover_sources


class DiscoveryTests(unittest.TestCase):
    fixtures = Path(__file__).parent / "fixtures" / "pham_nhan_discovery"

    def test_discovers_nested_imports_without_comment_or_string_false_positives(self) -> None:
        result = discover_sources(self.fixtures / "nested")
        paths = [row["path"] for row in result["modules"]]
        self.assertIn("main/first.lua", paths)
        self.assertIn("main/second.lua", paths)
        self.assertIn("scripts/cyclic.lua", paths)
        self.assertNotIn("main/ignored.lua", paths)
        self.assertNotIn("main/not-code.lua", paths)
        self.assertFalse(any(row["path"] == "main/not-code.lua" for row in result["unresolved"]))
        self.assertEqual(len(paths), len(set(paths)))

    def test_missing_module_is_diagnostic(self) -> None:
        result = discover_sources(self.fixtures / "missing")
        self.assertTrue(any(row["path"] == "main/missing.lua" for row in result["unresolved"]))

    def test_if_false_import_is_recorded_as_disabled(self) -> None:
        result = discover_sources(self.fixtures / "disabled")
        disabled = next(row for row in result["modules"] if row["path"] == "main/disabled.lua")
        self.assertEqual(disabled["status"], "disabled")
