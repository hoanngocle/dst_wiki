from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from .assets import resolve_assets
from .catalog import build_catalog
from .discovery import discover_sources
from .enrichment import enrich_catalog
from .sandbox import collect_registrations


def _bytes(value: dict) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def validate_snapshot(snapshot: dict, report: dict) -> None:
    ids = [item["id"] for item in snapshot["items"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate item IDs")
    known = {item["prefab"] for item in snapshot["items"]}
    for item in snapshot["items"]:
        if item["recipeStatus"] not in {"known", "none", "unknown"}:
            raise ValueError(f"invalid recipe status: {item['prefab']}")
        for recipe in item["recipes"]:
            if recipe["amount"] < 1 or any(ingredient["amount"] < 1 for ingredient in recipe["ingredients"]):
                raise ValueError(f"invalid amount: {recipe['id']}")
            if not recipe["evidence"]:
                raise ValueError(f"missing evidence: {recipe['id']}")
    if not math.isfinite(float(len(snapshot["items"]))):
        raise ValueError("non-finite JSON")


def build_snapshot(mod_root: Path) -> tuple[dict, dict, dict]:
    discovery = discover_sources(mod_root)
    registrations = collect_registrations(mod_root, discovery)
    items, coverage = build_catalog(mod_root, registrations)
    payload = enrich_catalog(mod_root, items, registrations)
    payload, assets = resolve_assets(mod_root, payload)
    source_hash = hashlib.sha256("".join(f"{key}:{value}" for key, value in sorted(discovery["sourceHashes"].items())).encode()).hexdigest()
    snapshot = {"schemaVersion": 1, "meta": {"name": "Phàm Nhân Tu Tiên", "version": "2.0", "sourceHash": source_hash},
                "items": payload["items"], "references": payload["references"], "affixes": payload["affixes"], "guides": payload["guides"], "config": payload["config"]}
    report = {"sourceHashes": discovery["sourceHashes"], "modules": discovery["modules"], "unresolved": [*discovery["unresolved"], *coverage["unresolved"]],
              "candidates": coverage["candidates"], "included": coverage["included"], "excluded": coverage["excluded"], "recipes": coverage["recipes"],
              "missingSprites": payload["diagnostics"].get("missingSprites", []), "conflicts": payload["diagnostics"].get("conflicts", []), "diagnostics": registrations["diagnostics"]}
    validate_snapshot(snapshot, report)
    return snapshot, report, assets


def write_snapshot(snapshot: dict, report: dict, output: Path, report_path: Path, check: bool = False) -> bool:
    expected, report_bytes = _bytes(snapshot), _bytes(report)
    if check:
        return output.is_file() and report_path.is_file() and output.read_bytes() == expected and report_path.read_bytes() == report_bytes
    output.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    for path, content in ((output, expected), (report_path, report_bytes)):
        staging = path.with_suffix(path.suffix + ".staging")
        staging.write_bytes(content)
        staging.replace(path)
    return True
