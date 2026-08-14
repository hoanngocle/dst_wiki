from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable


JsonObject = dict[str, Any]

TASK_SECTION = "## Toàn bộ nhiệm vụ"
ACHIEVEMENT_SECTION = "## Toàn bộ thành tựu"
PERK_SECTION = "## Toàn bộ perk/kỹ năng đổi bằng Sao"
LEVEL_SECTION = "## Hệ thống Level và điểm thuộc tính"
SOURCE_SECTION = "## File nguồn chính"


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def _plain(value: str) -> str:
    return value.replace("`", "").strip()


def _cells(line: str) -> list[str]:
    return [cell.strip().replace("\\|", "|") for cell in line.strip().strip("|").split("|")]


def _heading_index(lines: list[str], heading: str, error_label: str | None = None) -> int:
    try:
        return lines.index(heading)
    except ValueError as error:
        label = error_label or heading
        raise ValueError(f"missing {label}") from error


def _table_after(lines: list[str], heading_index: int) -> list[list[str]]:
    cursor = heading_index + 1
    while cursor < len(lines) and not lines[cursor].startswith("|"):
        cursor += 1
    if cursor + 1 >= len(lines):
        raise ValueError(f"table missing after {lines[heading_index]}")
    cursor += 2
    rows: list[list[str]] = []
    while cursor < len(lines) and lines[cursor].startswith("|"):
        rows.append(_cells(lines[cursor]))
        cursor += 1
    return rows


def _headings_between(lines: list[str], start: int, end: int) -> Iterable[tuple[int, str]]:
    for index in range(start + 1, end):
        if lines[index].startswith("### "):
            yield index, lines[index]


def _task_group_context(heading: str) -> tuple[str, str | None, str | None]:
    if "Nhiệm vụ 1" in heading:
        slot = "character"
    elif "2–4" in heading:
        slot = "seasonal"
    elif "5–6" in heading:
        slot = "repeat"
    else:
        raise ValueError(f"unknown task slot in heading: {heading}")

    season = next(
        (
            value
            for marker, value in (
                ("Mùa xuân", "spring"),
                ("Mùa đông", "winter"),
                ("Mùa hè", "summer"),
                ("Mùa thu", "autumn"),
                ("Ngoài mùa / fallback", "fallback"),
            )
            if marker in heading
        ),
        None,
    )
    character_match = re.search(r"Nhiệm vụ 1 — (.+?) \(yêu cầu nhân vật", heading)
    character = character_match.group(1) if character_match else None
    if slot == "character" and character is None:
        raise ValueError(f"missing character in task heading: {heading}")
    if slot != "character" and season is None:
        raise ValueError(f"missing season in task heading: {heading}")
    return slot, season, character


def _parse_task_groups(lines: list[str], start: int, end: int) -> list[JsonObject]:
    groups: list[JsonObject] = []
    for heading_index, heading in _headings_between(lines, start, end):
        heading_text = heading.removeprefix("### ")
        label = re.sub(r" — \d+ mục$", "", heading_text)
        slot, season, character = _task_group_context(heading)
        group_id = f"{slot}-{character or season}"
        tasks: list[JsonObject] = []
        for position, row in enumerate(_table_after(lines, heading_index), start=1):
            if len(row) != 5:
                raise ValueError(f"task row in {heading} must have 5 columns")
            tasks.append(
                {
                    "key": f"{_slug(group_id)}:{position}",
                    "sourceId": _plain(row[4]),
                    "name": row[1],
                    "instructions": row[2],
                    "event": _plain(row[3]),
                }
            )
        groups.append(
            {
                "id": _slug(group_id),
                "label": label,
                "slot": slot,
                "season": season,
                "character": character,
                "repeatCount": 10 if "lặp 10 lần" in heading else 1,
                "tasks": tasks,
            }
        )
    return groups


def _parse_achievements(lines: list[str], start: int, end: int) -> list[JsonObject]:
    achievements: list[JsonObject] = []
    for heading_index, heading in _headings_between(lines, start, end):
        category = re.sub(r" — \d+ thành tựu$", "", heading.removeprefix("### "))
        for row in _table_after(lines, heading_index):
            if len(row) != 6:
                raise ValueError(f"achievement row in {heading} must have 6 columns")
            achievements.append(
                {
                    "id": _plain(row[0]),
                    "name": row[1],
                    "description": row[2],
                    "target": row[3],
                    "stars": int(row[4]),
                    "characterRequirement": row[5],
                    "category": category,
                }
            )
    return achievements


def _parse_perks(lines: list[str], start: int, end: int) -> list[JsonObject]:
    perks: list[JsonObject] = []
    for heading_index, heading in _headings_between(lines, start, end):
        category = re.sub(r" — \d+ perk$", "", heading.removeprefix("### "))
        for row in _table_after(lines, heading_index):
            if len(row) != 6:
                raise ValueError(f"perk row in {heading} must have 6 columns")
            perks.append(
                {
                    "id": _plain(row[0]),
                    "name": row[1],
                    "description": row[2],
                    "cost": int(row[3]),
                    "scope": row[4],
                    "notes": None if row[5] == "—" else row[5],
                    "category": category,
                }
            )
    return perks


def _parse_reward_table(lines: list[str], heading: str) -> list[JsonObject]:
    heading_index = _heading_index(lines, heading)
    rows = _table_after(lines, heading_index)
    return [{"character": row[0], "effect": row[1]} for row in rows]


def _table_blocks_between(lines: list[str], start: int, end: int) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    cursor = start + 1
    while cursor < end:
        if not lines[cursor].startswith("|"):
            cursor += 1
            continue
        cursor += 2
        rows: list[list[str]] = []
        while cursor < end and lines[cursor].startswith("|"):
            rows.append(_cells(lines[cursor]))
            cursor += 1
        tables.append(rows)
    return tables


def _parse_level(lines: list[str], start: int, end: int) -> JsonObject:
    summary = [
        line.removeprefix("- ")
        for line in lines[start + 1 : end]
        if line.startswith("- ")
    ]
    tables = _table_blocks_between(lines, start, end)
    if len(tables) != 2:
        raise ValueError(f"expected 2 level tables, got {len(tables)}")

    def attributes(rows: list[list[str]]) -> list[JsonObject]:
        parsed: list[JsonObject] = []
        for row in rows:
            if len(row) != 3:
                raise ValueError("level attribute row must have 3 columns")
            parsed.append({"name": row[0], "increase": row[1], "multi": _plain(row[2])})
        return parsed

    return {
        "summary": summary,
        "playerAttributes": attributes(tables[0]),
        "petAttributes": attributes(tables[1]),
    }


def parse_report(markdown: str) -> JsonObject:
    lines = markdown.splitlines()
    task_start = _heading_index(lines, TASK_SECTION, "task section")
    achievement_start = _heading_index(lines, ACHIEVEMENT_SECTION, "achievement section")
    perk_start = _heading_index(lines, PERK_SECTION, "perk section")
    level_start = _heading_index(lines, LEVEL_SECTION, "level section")
    source_start = _heading_index(lines, SOURCE_SECTION, "source section")

    task_groups = _parse_task_groups(lines, task_start, achievement_start)
    achievements = _parse_achievements(lines, achievement_start, perk_start)
    perks = _parse_perks(lines, perk_start, level_start)
    rewards = {
        "task2": _parse_reward_table(lines, "### Mốc 2 nhiệm vụ — hiệu ứng tức thời"),
        "task4": _parse_reward_table(lines, "### Mốc 4 nhiệm vụ — 200 XP và kỹ năng mùa"),
    }
    level = _parse_level(lines, level_start, source_start)

    task_count = sum(len(group["tasks"]) for group in task_groups)
    if len(task_groups) != 28:
        raise ValueError(f"expected 28 task pools, got {len(task_groups)}")
    if task_count != 763:
        raise ValueError(f"expected 763 task occurrences, got {task_count}")
    if len(achievements) != 169:
        raise ValueError(f"expected 169 achievements, got {len(achievements)}")
    if len(perks) != 128:
        raise ValueError(f"expected 128 perks, got {len(perks)}")
    character_groups = sum(group["slot"] == "character" for group in task_groups)
    if character_groups != 18:
        raise ValueError(f"expected 18 character task groups, got {character_groups}")

    return {
        "meta": {
            "workshopId": "2937640068",
            "name": "Achievement & Level",
            "version": "7.3.4",
            "locale": "vi",
            "taskPoolCount": 28,
            "characterTaskGroupCount": 18,
        },
        "taskGroups": task_groups,
        "achievements": achievements,
        "perks": perks,
        "rewards": rewards,
        "level": level,
    }


def build_artifact(report_path: Path, output_path: Path) -> JsonObject:
    artifact = parse_report(report_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("mod-achievement-level-2937640068.md"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/manual/achievement-level.json"),
    )
    args = parser.parse_args()
    build_artifact(args.report, args.output)


if __name__ == "__main__":
    main()
