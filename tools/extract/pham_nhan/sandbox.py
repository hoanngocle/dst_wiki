from __future__ import annotations

import hashlib
import re
from pathlib import Path


def _balanced_calls(source: str, name: str):
    marker = re.compile(rf"(?<!\w){re.escape(name)}\s*\(")
    for found in marker.finditer(source):
        start = source.find("(", found.start())
        depth, quote, index = 0, None, start
        while index < len(source):
            char = source[index]
            if quote:
                if char == "\\":
                    index += 2
                    continue
                if char == quote:
                    quote = None
            elif char in "'\"":
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    yield source[start + 1:index], found.start()
                    break
            index += 1


def _split_top_level(value: str) -> list[str]:
    parts: list[str] = []
    start = depth = 0
    quote: str | None = None
    for index, char in enumerate(value):
        if quote:
            if char == quote and (index == 0 or value[index - 1] != "\\"):
                quote = None
        elif char in "'\"":
            quote = char
        elif char in "({[":
            depth += 1
        elif char in ")} ]".replace(" ", ""):
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return parts


def _value(table: str, key: str) -> str | None:
    match = re.search(rf"(?:\b{re.escape(key)}|\[['\"]{re.escape(key)}['\"]\])\s*=\s*(['\"])(.*?)\1", table, re.DOTALL)
    return match.group(2) if match else None


def _number(table: str, key: str, default: int = 1) -> int:
    match = re.search(rf"(?:\b{re.escape(key)}|\[['\"]{re.escape(key)}['\"]\])\s*=\s*(\d+)", table)
    return int(match.group(1)) if match else default


def _ingredients(value: str) -> list[dict]:
    return [
        {"prefab": match.group(1), "amount": int(match.group(2))}
        for match in re.finditer(r"(?:GLOBAL\.)?Ingredient\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(\d+)", value)
    ]


def _evidence(root: Path, relative: str, locator: str) -> dict:
    return {"path": relative, "locator": locator, "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(), "kind": "runtime"}


def collect_registrations(mod_root: Path, discovery: dict) -> dict:
    """Collect declarative registrations without executing gameplay Lua or proxies."""
    root = mod_root.resolve()
    recipes: dict[str, dict] = {}
    names: dict[str, str] = {}
    descriptions: dict[str, str] = {}
    atlases: dict[str, dict] = {}
    diagnostics: list[dict] = []
    loaded_sources: list[str] = []
    prefabs: set[str] = set()
    for module in discovery["modules"]:
        if module["status"] != "loaded":
            continue
        relative = module["path"]
        path = root / relative
        source = path.read_text(encoding="utf-8", errors="replace")
        loaded_sources.append(relative)
        for match in re.finditer(r"STRINGS\.NAMES\.([A-Z0-9_]+)\s*=\s*(['\"])(.*?)\2", source):
            names[match.group(1).lower()] = match.group(3)
        for match in re.finditer(r"STRINGS\.RECIPE_DESC\.([A-Z0-9_]+)\s*=\s*(['\"])(.*?)\2", source):
            descriptions[match.group(1).lower()] = match.group(3)
        for match in re.finditer(r"RegisterInventoryItemAtlas\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]", source):
            atlases[match.group(2)] = {"atlas": match.group(1), "image": match.group(2)}
        for args, position in _balanced_calls(source, "AddRecipe2"):
            values = _split_top_level(args)
            if len(values) < 4:
                diagnostics.append({"path": relative, "locator": f"AddRecipe2@{position}", "reason": "unsupported argument shape"})
                continue
            recipe_id = re.match(r"\s*['\"]([^'\"]+)['\"]", values[0])
            if not recipe_id:
                diagnostics.append({"path": relative, "locator": f"AddRecipe2@{position}", "reason": "dynamic recipe id"})
                continue
            options = values[3]
            product = _value(options, "product") or recipe_id.group(1)
            recipe = {
                "id": recipe_id.group(1), "kind": "crafting", "product": product,
                "amount": _number(options, "numtogive"), "ingredients": _ingredients(values[1]),
                "station": ", ".join(re.findall(r"['\"]([A-Z_]+)['\"]", values[4] if len(values) > 4 else "")) or "Chế tạo",
                "conditions": [f"Cần tag người chế tạo: {_value(options, 'builder_tag')}"] if _value(options, "builder_tag") else [],
                "atlas": _value(options, "atlas"), "image": _value(options, "image"),
                "evidence": [_evidence(root, relative, f"AddRecipe2@{position}")],
            }
            recipes[recipe["id"]] = recipe
            prefabs.add(product)
            prefabs.update(item["prefab"] for item in recipe["ingredients"])
    return {"recipes": recipes, "names": names, "descriptions": descriptions, "atlases": atlases,
            "prefabs": sorted(prefabs), "diagnostics": diagnostics, "loadedSources": loaded_sources}
