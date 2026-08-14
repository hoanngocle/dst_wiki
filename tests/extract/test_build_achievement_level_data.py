import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.build_achievement_level_data import build_artifact, parse_report


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "mod-achievement-level-2937640068.md"


class AchievementLevelDataBuilderTests(unittest.TestCase):
    def test_parse_report_preserves_complete_mod_snapshot(self) -> None:
        artifact = parse_report(REPORT.read_text(encoding="utf-8"))

        self.assertEqual(
            artifact["meta"],
            {
                "workshopId": "2937640068",
                "name": "Achievement & Level",
                "version": "7.3.4",
                "locale": "vi",
                "taskPoolCount": 28,
                "characterTaskGroupCount": 18,
            },
        )
        self.assertEqual(sum(len(group["tasks"]) for group in artifact["taskGroups"]), 763)
        self.assertEqual(len(artifact["achievements"]), 169)
        self.assertEqual(len(artifact["perks"]), 128)
        self.assertEqual(len(artifact["rewards"]["task2"]), 19)
        self.assertEqual(len(artifact["rewards"]["task4"]), 11)

    def test_task_occurrences_keep_pool_context(self) -> None:
        artifact = parse_report(REPORT.read_text(encoding="utf-8"))
        occurrences = [
            task
            for group in artifact["taskGroups"]
            for task in group["tasks"]
            if task["name"] == "Kill a Batilisk"
        ]

        self.assertGreater(len(occurrences), 1)
        self.assertEqual(len({task["key"] for task in occurrences}), len(occurrences))

    def test_parse_report_rejects_missing_required_section(self) -> None:
        markdown = REPORT.read_text(encoding="utf-8").replace(
            "## Toàn bộ perk/kỹ năng đổi bằng Sao",
            "## Phần bị thiếu",
        )

        with self.assertRaisesRegex(ValueError, "perk section"):
            parse_report(markdown)

    def test_build_artifact_writes_stable_utf8_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "achievement-level.json"

            first = build_artifact(REPORT, output)
            first_bytes = output.read_bytes()
            second = build_artifact(REPORT, output)

            self.assertEqual(second, first)
            self.assertEqual(output.read_bytes(), first_bytes)
            parsed = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(parsed["achievements"][0]["name"])


if __name__ == "__main__":
    unittest.main()
