from __future__ import annotations

import hashlib
import re
from collections import deque
from pathlib import Path
from typing import Iterable


_IMPORT = re.compile(r"\bmodimport\s*(?:\(\s*)?['\"]([^'\"]+)['\"]\s*\)?")
_REQUIRE = re.compile(r"\brequire\s*(?:\(\s*)?['\"]([^'\"]+)['\"]\s*\)?")
_FALSE_BLOCK = re.compile(r"\bif\s+false\s+then\b(.*?)\bend\b", re.DOTALL)


def _without_comments_and_strings(source: str) -> str:
    """Keep quoted import arguments but blank comments and unrelated strings."""
    result: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(source):
        char = source[index]
        next_two = source[index:index + 2]
        if quote:
            result.append(char)
            if char == "\\" and index + 1 < len(source):
                result.append(source[index + 1])
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if next_two == "--":
            newline = source.find("\n", index)
            if newline == -1:
                break
            result.append("\n")
            index = newline + 1
            continue
        if char in "'\"":
            quote = char
        result.append(char)
        index += 1
    return "".join(result)


def _resolve(root: Path, parent: Path, kind: str, raw: str) -> Path | None:
    raw_path = raw.replace(".", "/") if kind == "require" and "/" not in raw else raw
    candidates = [root / raw_path]
    if not raw_path.endswith(".lua"):
        candidates.append(root / f"{raw_path}.lua")
    if kind == "require" and not raw_path.startswith(("scripts/", "main/")):
        candidates.append(root / "scripts" / f"{raw_path}.lua")
    for candidate in candidates:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


def _calls(source: str) -> Iterable[tuple[str, str, bool]]:
    clean = _without_comments_and_strings(source)
    disabled_spans = [match.span(1) for match in _FALSE_BLOCK.finditer(clean)]
    index = 0
    quote: str | None = None
    while index < len(source):
        if quote:
            if source[index] == "\\":
                index += 2
                continue
            if source[index] == quote:
                quote = None
            index += 1
            continue
        if source.startswith("--", index):
            newline = source.find("\n", index)
            index = len(source) if newline == -1 else newline + 1
            continue
        if source[index] in "'\"":
            quote = source[index]
            index += 1
            continue
        match = re.match(r"(modimport|require)\s*(?:\(\s*)?(['\"])([^'\"]+)\2\s*\)?", source[index:])
        if match and (index == 0 or not (source[index - 1].isalnum() or source[index - 1] == "_")):
            kind, _, raw = match.groups()
            disabled = any(start <= index < end for start, end in disabled_spans)
            yield kind, raw, disabled
            index += match.end()
            continue
        index += 1


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_sources(mod_root: Path) -> dict:
    """Traverse only active local Lua imports, retaining diagnostics for gaps."""
    root = mod_root.resolve()
    entrypoint = root / "modmain.lua"
    if not entrypoint.is_file():
        raise FileNotFoundError(f"Missing mod entrypoint: {entrypoint}")
    modules: list[dict] = []
    unresolved: list[dict] = []
    seen: set[Path] = set()
    queued: deque[tuple[Path, str | None, int, str]] = deque([(entrypoint, None, 0, "loaded")])
    while queued:
        path, parent, order, requested_status = queued.popleft()
        canonical = path.resolve()
        if canonical in seen:
            continue
        seen.add(canonical)
        relative = canonical.relative_to(root).as_posix()
        source = canonical.read_text(encoding="utf-8", errors="replace")
        row = {"path": relative, "parent": parent, "order": order, "status": requested_status, "reason": None}
        modules.append(row)
        for call_order, (kind, raw, disabled) in enumerate(_calls(source)):
            target = _resolve(root, canonical, "require" if kind == "require" else "modimport", raw)
            expected = raw if raw.endswith(".lua") else f"{raw}.lua"
            if target is None:
                # Game modules are not diagnostics; local-looking paths are.
                if kind == "modimport" or raw.startswith(("main/", "scripts/", "prefabs/")):
                    unresolved.append({"path": expected, "parent": relative, "kind": kind, "reason": "missing local module"})
                continue
            target_relative = target.resolve().relative_to(root).as_posix()
            if disabled:
                if target.resolve() not in seen:
                    modules.append({"path": target_relative, "parent": relative, "order": order + call_order + 1, "status": "disabled", "reason": "if false branch"})
                    seen.add(target.resolve())
                continue
            queued.append((target, relative, order + call_order + 1, "loaded"))
    modules.sort(key=lambda row: (row["order"], row["path"]))
    loaded = [row for row in modules if row["status"] == "loaded"]
    registration_files = [row["path"] for row in loaded if re.search(r"\b(AddRecipe2|AddCookerRecipe|RegisterInventoryItemAtlas|PrefabFiles)\b", (root / row["path"]).read_text(encoding="utf-8", errors="replace"))]
    prefab_files = [row["path"] for row in loaded if "PrefabFiles" in (root / row["path"]).read_text(encoding="utf-8", errors="replace")]
    return {
        "entrypoint": "modmain.lua",
        "modules": modules,
        "registrationFiles": registration_files,
        "prefabFiles": prefab_files,
        "unresolved": unresolved,
        "sourceHashes": {row["path"]: _hash(root / row["path"]) for row in loaded},
    }
