from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


def _evidence(root: Path, relative: str, locator: str, kind: str = "runtime") -> dict:
    return {"path": relative, "locator": locator, "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(), "kind": kind}


def _string_overrides(root: Path) -> dict[str, tuple[str, str, dict]]:
    path = root / "main" / "hh_string.lua"
    if not path.is_file():
        return {}
    source = path.read_text(encoding="utf-8", errors="replace")
    result = {}
    for match in re.finditer(r'\["([\w_]+)"\]\s*=\s*\{\s*"([^"]+)"\s*,\s*"([^"]*)"', source):
        result[match.group(1)] = (match.group(2), match.group(3), _evidence(root, "main/hh_string.lua", f"string {match.group(1)}"))
    return result


def _guides(root: Path) -> tuple[list[dict], list[dict]]:
    source_path = Path("app/data/pham-nhan-guides.json")
    if not source_path.is_file():
        return [], [{"reason": "guide snapshot missing"}]
    source = json.loads(source_path.read_text(encoding="utf-8"))
    guides, conflicts = [], []
    for entry in source:
        if entry["id"].startswith("book-"):
            conflicts.append({"guide": entry["id"], "reason": "historical book omitted until runtime facts are verified"})
            continue
        referenced = root / entry.get("source", "")
        if referenced.is_file():
            evidence = _evidence(root, referenced.relative_to(root).as_posix(), "guide source", "doc")
        else:
            # Existing authored guides remain discoverable but explicitly say
            # that their detailed text is not catalog membership evidence.
            evidence = {"path": entry.get("source", "app/data/pham-nhan-guides.json"), "locator": entry["id"], "sha256": hashlib.sha256(entry["text"].encode()).hexdigest(), "kind": "history"}
        plain = re.sub(r"\[(?:ITEM|TABLE|HEADER|ROW)[^\]]*\]|\[/(?:TABLE|HEADER|ROW)\]", "", entry["text"])
        guides.append({"id": entry["id"], "title": entry["title"], "text": plain, "evidence": [evidence]})
    return guides, conflicts


def _affixes(root: Path) -> list[dict]:
    path = root / "scripts" / "enums" / "hh_enchant.lua"
    if not path.is_file():
        return []
    source = path.read_text(encoding="utf-8", errors="replace")
    entries = []
    for match in re.finditer(r'\["([A-Za-z][\w_]+)"\]\s*=\s*\{\s*\["name"\]\s*=\s*([^,\n]+)', source):
        key, expression = match.groups()
        if key.startswith(("fx", "ph")):
            continue
        entries.append({"id": key, "name": key, "description": f"Thuộc tính runtime: {expression.strip()}", "details": [], "rarity": "runtime", "sprite": None,
                        "evidence": [_evidence(root, "scripts/enums/hh_enchant.lua", f"affix {key}")]})
    return entries


def _config(root: Path) -> list[dict]:
    path = root / "modinfo.lua"
    source = path.read_text(encoding="utf-8", errors="replace")
    result = []
    for match in re.finditer(r'name\s*=\s*"([^"]+)".*?default\s*=\s*([^,}\n]+)', source, re.DOTALL):
        key, default = match.groups()
        if key.lower().startswith("eva_") and "removed" in source[max(0, match.start()-200):match.end()].lower():
            continue
        parsed: str | int | bool = default.strip().strip('"')
        if parsed in ("true", "false"):
            parsed = parsed == "true"
        elif isinstance(parsed, str) and parsed.isdigit():
            parsed = int(parsed)
        result.append({"key": key, "label": key, "description": "Tùy chọn đăng ký trong modinfo.lua.", "default": parsed, "choices": [],
                       "evidence": [_evidence(root, "modinfo.lua", f"configuration {key}")]})
    return result


def enrich_catalog(mod_root: Path, items: list[dict], registrations: dict) -> dict:
    root = mod_root.resolve()
    overrides = _string_overrides(root)
    for item in items:
        if item["prefab"] in overrides:
            item["name"], item["description"], evidence = overrides[item["prefab"]]
            item["evidence"] = [*item["evidence"], evidence]
        for recipe in item["recipes"]:
            for ingredient in recipe["ingredients"]:
                ingredient["name"] = overrides.get(ingredient["prefab"], (registrations["names"].get(ingredient["prefab"], ingredient["prefab"].replace("_", " ").title()), "", None))[0]
                ingredient["sprite"] = None
    references = [{"id": f"item:{item['prefab']}", "prefab": item["prefab"], "name": item["name"], "sprite": None} for item in items]
    guides, conflicts = _guides(root)
    return {"items": items, "references": references, "affixes": _affixes(root), "guides": guides, "config": _config(root),
            "diagnostics": {"conflicts": conflicts}}
