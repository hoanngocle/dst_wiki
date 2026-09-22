"""Contract checks for SS/SSS hunter-rank progression.

This repository does not bundle a Lua interpreter in the standard test path.  The
test therefore parses the intentionally static rank definitions and audits the
rank component's observable transition contract instead of claiming a DST/Lua
runtime execution.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RANK_DEFS = ROOT / "mods/PhamNhanTuTien/scripts/guild/hh_rank_defs.lua"
RANK_COMPONENT = ROOT / "mods/PhamNhanTuTien/scripts/components/hh_rank.lua"
EXAM_DEFS = ROOT / "mods/PhamNhanTuTien/scripts/guild/hh_rank_exam_defs.lua"
SHOP_DEFS = ROOT / "mods/PhamNhanTuTien/scripts/guild/hh_guild_shop_defs.lua"
EXPECTED = {
    1: "E", 9: "E", 10: "D", 20: "C", 30: "B", 40: "A",
    50: "S", 69: "S", 70: "SS", 99: "SS", 100: "SSS",
}
RANK_VALUES = {"E": 1, "D": 2, "C": 3, "B": 4, "A": 5, "S": 6, "SS": 7, "SSS": 8}


def table_block(source: str, name: str) -> str:
    match = re.search(rf"M\.{name}\s*=\s*\{{(?P<body>.*?)\n\}}", source, re.DOTALL)
    if match is None:
        raise AssertionError(f"missing M.{name} table")
    return match.group("body")


def rank_table(source: str, table_name: str) -> dict[str, int]:
    body = table_block(source, table_name)
    if table_name == "RANK":
        return {
            name: int(value)
            for name, value in re.findall(r"^\s*([A-Z]+)\s*=\s*(\d+)", body, re.MULTILINE)
        }
    return {
        name: int(value)
        for name, value in re.findall(
            r"\[M\.RANK\.([A-Z]+)\]\s*=\s*(\d+)", body
        )
    }


def name_table(source: str) -> dict[str, str]:
    return {
        rank: name
        for rank, name in re.findall(
            r'\[M\.RANK\.([A-Z]+)\]\s*=\s*"([A-Z]+)"', table_block(source, "NAMES")
        )
    }


def rank_for_level(level: int, ranks: dict[str, int], requirements: dict[str, int]) -> str:
    result = "E"
    for name, rank in sorted(ranks.items(), key=lambda item: item[1]):
        if rank >= ranks["D"] and level >= requirements.get(name, float("inf")):
            result = name
    return result


def reconcile_level_promotion(current: str, level: int, ranks: dict[str, int], requirements: dict[str, int]) -> str:
    """Model the component contract: only S+ ranks receive level-only promotions."""
    if ranks[current] < ranks["S"]:
        return current
    target = rank_for_level(level, ranks, requirements)
    return target if ranks[target] > ranks[current] else current


def claim_exam_then_reconcile(current: str, level: int, ranks: dict[str, int], requirements: dict[str, int]) -> str:
    """Model a completed exam claim followed by the component catch-up contract."""
    claimed = next(name for name, value in ranks.items() if value == ranks[current] + 1)
    return reconcile_level_promotion(claimed, level, ranks, requirements)


def rank_load_before_leveling_then_deferred(
    saved_rank: str, restored_level: int, ranks: dict[str, int], requirements: dict[str, int]
) -> tuple[str, list[tuple[str, str]]]:
    """Model rank-load-first, then level-load, then one or more zero-delay callbacks."""
    current = saved_rank
    events: list[tuple[str, str]] = []

    def reconcile(level: int) -> None:
        nonlocal current
        promoted = reconcile_level_promotion(current, level, ranks, requirements)
        if promoted != current:
            events.append((current, promoted))
            current = promoted

    reconcile(1)  # Rank OnLoad runs before hh_leveling restores its saved level.
    reconcile(restored_level)  # The scheduled post-load callback.
    reconcile(restored_level)  # A duplicate callback or favorable load order is a no-op.
    return current, events


def component_method(source: str, method_name: str) -> str:
    match = re.search(
        rf"function HHRank:{method_name}\([^)]*\)(?P<body>.*?)(?=\nfunction HHRank:|\nreturn HHRank)",
        source,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing HHRank:{method_name}")
    return match.group("body")


class ExtendedRankContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.defs = RANK_DEFS.read_text(encoding="utf-8")
        cls.component = RANK_COMPONENT.read_text(encoding="utf-8")
        cls.ranks = rank_table(cls.defs, "RANK")
        cls.names = name_table(cls.defs)
        cls.requirements = rank_table(cls.defs, "LEVEL_REQUIREMENTS")

    def test_rank_api_agrees_through_sss(self) -> None:
        """Removing SS/SSS from the definitions or rank bounds breaks level API agreement."""
        self.assertEqual(self.ranks, RANK_VALUES)
        self.assertEqual(self.names, {name: name for name in RANK_VALUES})
        self.assertEqual(self.requirements, {"D": 10, "C": 20, "B": 30, "A": 40, "S": 50, "SS": 70, "SSS": 100})
        self.assertRegex(self.defs, r"function M\.GetName\(rank\)")
        self.assertRegex(self.defs, r"for rank = M\.RANK\.D, M\.RANK\.SSS do")
        self.assertRegex(self.defs, r"rank <= M\.RANK\.SSS")
        self.assertRegex(self.defs, r"if rank < M\.RANK\.SSS then")
        for level, expected_name in EXPECTED.items():
            actual_name = rank_for_level(level, self.ranks, self.requirements)
            self.assertEqual(actual_name, expected_name, f"Level {level}")
            rank = self.ranks[actual_name]
            self.assertEqual(self.names[actual_name], actual_name)
            self.assertTrue(self.ranks["E"] <= rank <= self.ranks["SSS"])

    def test_s_or_higher_capability_checks_include_extended_ranks(self) -> None:
        """A numeric S capability gate remains available to SS and SSS hunters."""
        self.assertTrue({"S", "SS", "SSS"}.issubset(self.ranks))
        self.assertTrue(all(self.ranks[name] >= self.ranks["S"] for name in ("S", "SS", "SSS")))

    def test_extended_ranks_do_not_register_gameplay_rows(self) -> None:
        """SS/SSS stay labels: no exam, shop, EXP, combat, or bonus consumer registers them."""
        self.assertNotRegex(EXAM_DEFS.read_text(encoding="utf-8"), r"RANK\.(?:SSS|SS)\b")
        self.assertNotRegex(SHOP_DEFS.read_text(encoding="utf-8"), r"RANK\.(?:SSS|SS)\b")
        registered = []
        for path in (ROOT / "mods/PhamNhanTuTien/scripts").rglob("*.lua"):
            if path == RANK_DEFS:
                continue
            if re.search(r"RANK\.(?:SSS|SS)\b", path.read_text(encoding="utf-8")):
                registered.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(registered, [])

    def test_component_reconciles_level_only_promotions_without_demoting(self) -> None:
        """Removing the level listener, load reconciliation, or S gate breaks promotion safety."""
        self.assertRegex(self.component, r'ListenForEvent\("hh_levelup", function\(\)\s*self:ReconcileLevelPromotion\(\)')
        body = component_method(self.component, "ReconcileLevelPromotion")
        self.assertRegex(body, r"(?:self\.rank|old_rank) < RankDefs\.RANK\.S")
        self.assertRegex(body, r"RankDefs\.GetRankForLevel\(GetLevel\(self\.inst\)\)")
        self.assertRegex(body, r"level_rank <= self\.rank")
        self.assertRegex(body, r'source\s*=\s*"level_promotion"')
        self.assertRegex(body, r"quest:RefreshOffers\(\)")
        self.assertRegex(body, r"self:RefreshExamAvailability\(\)")
        self.assertRegex(body, r"self:Sync\(\)")
        self.assertRegex(self.component, r"self:ReconcileLevelPromotion\(\)\s*\n\s*self:RefreshExamAvailability\(\)")

        self.assertEqual(reconcile_level_promotion("S", 70, self.ranks, self.requirements), "SS")
        self.assertEqual(reconcile_level_promotion("S", 100, self.ranks, self.requirements), "SSS")
        self.assertEqual(reconcile_level_promotion("SS", 100, self.ranks, self.requirements), "SSS")
        self.assertEqual(reconcile_level_promotion("A", 100, self.ranks, self.requirements), "A")
        self.assertEqual(reconcile_level_promotion("SSS", 1, self.ranks, self.requirements), "SSS")

    def test_claiming_s_exam_catches_up_to_current_level_rank(self) -> None:
        """Removing post-claim reconciliation leaves a Level 70/100 hunter incorrectly at S."""
        claim_exam = component_method(self.component, "ClaimExam")
        self.assertRegex(
            claim_exam,
            r"self\.pending_exam_reward = true\s*\n\s*local level_promoted = self:ReconcileLevelPromotion\(\)",
        )
        self.assertLess(claim_exam.index('source = "claim_exam"'), claim_exam.index("self:ReconcileLevelPromotion()"))
        self.assertIn('source = "level_promotion"', component_method(self.component, "ReconcileLevelPromotion"))
        self.assertRegex(claim_exam, r"if not level_promoted then\s*\n\s*self:RefreshExamAvailability\(\)")
        self.assertRegex(claim_exam, r"if not level_promoted then\s*\n\s*local quest = self\.inst\.components\.hh_guild_quest")
        self.assertEqual(claim_exam_then_reconcile("A", 70, self.ranks, self.requirements), "SS")
        self.assertEqual(claim_exam_then_reconcile("A", 100, self.ranks, self.requirements), "SSS")

    def test_rank_load_before_leveling_uses_one_deferred_catch_up_event(self) -> None:
        """Without a guarded zero-delay callback, rank-first loading strands S at its stale level."""
        on_load = component_method(self.component, "OnLoad")
        self.assertRegex(
            on_load,
            r"self:Sync\(\)\s*\n\s*self\.inst:DoTaskInTime\(0, function\(inst\)",
        )
        self.assertRegex(on_load, r"if inst:IsValid\(\) and inst\.components\.hh_rank == self then")
        self.assertRegex(on_load, r"self:ReconcileLevelPromotion\(\)")
        self.assertNotRegex(on_load, r'PushEvent\("hh_rank_changed"')
        self.assertEqual(
            rank_load_before_leveling_then_deferred("S", 70, self.ranks, self.requirements),
            ("SS", [("S", "SS")]),
        )
        self.assertEqual(
            rank_load_before_leveling_then_deferred("S", 100, self.ranks, self.requirements),
            ("SSS", [("S", "SSS")]),
        )

    def test_component_clears_exam_presentation_when_extended_rank_has_no_exam(self) -> None:
        """A missing SS/SSS exam must clear a stale S exam instead of leaving it visible."""
        missing_exam = re.search(r"if exam == nil then(?P<body>.*?)\n\s*end", self.component, re.DOTALL)
        self.assertIsNotNone(missing_exam)
        body = missing_exam.group("body")
        for field in ("self.exam_id = 0", "self.exam_progress = 0", "self.exam_target = 0", "self:Sync()"):
            self.assertIn(field, body)
        self.assertNotRegex(
            self.component,
            r"for\s+\w*rank\w*\s*=\s*1\s*,\s*6\b",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
