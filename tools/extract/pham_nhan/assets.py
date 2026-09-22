from __future__ import annotations

from pathlib import Path


def resolve_assets(mod_root: Path, payload: dict) -> tuple[dict, dict]:
    """Keep unresolved art explicit; never substitute an arbitrary atlas element."""
    diagnostics = payload.setdefault("diagnostics", {})
    diagnostics["missingSprites"] = [item["prefab"] for item in payload["items"] if item["sprite"] is None]
    return payload, {}
