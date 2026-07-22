import copy
import hashlib
import json
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import unquote, urlsplit


JsonObject = Dict[str, Any]
REPAIR_ATTEMPTS = [
    "current_valid_field",
    "canonical_duplicate",
    "wiki_detail",
    "reviewed_category_crawl",
    "catalog_recipe_evidence",
]


def _key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.casefold())


def _image_key(value: str) -> str:
    return value.removeprefix("File:").replace("_", " ").casefold().strip()


def _read_jsonl(path: Path) -> List[JsonObject]:
    if not path.is_file():
        return []
    rows = []
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("{}:{} must contain an object".format(path, line_number))
            rows.append(value)
    return rows


def _image_signature(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size <= 0:
        return False
    head = path.read_bytes()[:16]
    return (
        head.startswith(b"\x89PNG\r\n\x1a\n")
        or head.startswith(b"\xff\xd8\xff")
        or head.startswith((b"GIF87a", b"GIF89a"))
        or (head.startswith(b"RIFF") and head[8:12] == b"WEBP")
    )


def _sprite_path(sprite: Any, public_root: Path) -> Optional[Path]:
    if not isinstance(sprite, Mapping):
        return None
    source = sprite.get("src")
    if not isinstance(source, str) or not source.startswith("/"):
        return None
    relative = Path(source.lstrip("/"))
    if relative.is_absolute() or ".." in relative.parts:
        return None
    return public_root / relative


def _valid_sprite(sprite: Any, public_root: Path) -> bool:
    path = _sprite_path(sprite, public_root)
    return path is not None and _image_signature(path)


def _meaningful(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value not in {"unknown", "none"}
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, list):
        return any(_meaningful(row) for row in value)
    if isinstance(value, Mapping):
        ignored = {
            "contract", "evidence", "id", "name", "order", "prefabId", "role",
            "sourceVariant", "status", "wikiUrl",
        }
        return any(key not in ignored and _meaningful(row) for key, row in value.items())
    return False


def _has_content(item: Mapping[str, Any]) -> bool:
    if isinstance(item.get("description"), str) and item["description"].strip():
        return True
    if isinstance(item.get("wiki"), Mapping):
        return True
    return any(
        _meaningful(item.get(field))
        for field in ("recipe", "details", "mob", "structureDetails", "character")
    )


def _has_detail(item: Mapping[str, Any]) -> bool:
    category = item.get("category")
    if category in {"mob", "boss"}:
        return _meaningful(item.get("mob"))
    if category == "structure":
        return _meaningful(item.get("structureDetails"))
    if category == "character":
        return _meaningful(item.get("character"))
    return any(
        _meaningful(item.get(field))
        for field in ("recipe", "details", "description", "wiki")
    )


def _item_issues(item: Mapping[str, Any], public_root: Path) -> List[str]:
    issues = []
    if not _valid_sprite(item.get("sprite"), public_root):
        issues.append("missing_image")
    if not _has_content(item):
        issues.append("missing_content")
    if not _has_detail(item):
        issues.append("missing_detail")
    if not str(item.get("id") or "").strip() or not str(item.get("namespace") or "").strip():
        issues.append("missing_source")
    scope = " ".join(
        str(item.get(field) or "") for field in ("name", "englishName", "description")
    ).casefold()
    if any(marker in scope for marker in ("shipwrecked-only", "hamlet-only", "reign of giants-only")):
        issues.append("invalid_scope")
    return issues


def _duplicate_issues(items: Iterable[Mapping[str, Any]]) -> List[JsonObject]:
    issues = []
    identities: Dict[str, List[str]] = {}
    codes: Dict[str, List[str]] = {}
    for item in items:
        identity = str(item.get("id") or "").casefold()
        code = "{}:{}".format(item.get("namespace") or "", item.get("prefabId") or "").casefold()
        identities.setdefault(identity, []).append(str(item.get("id") or ""))
        codes.setdefault(code, []).append(str(item.get("id") or ""))
    for values in identities.values():
        if len(values) > 1:
            issues.append({"code": "duplicate_identity", "identities": values})
    for values in codes.values():
        if len(values) > 1:
            issues.append({"code": "duplicate_code", "identities": values})
    return issues


def _audit_guides(guides_root: Path, public_root: Path) -> List[JsonObject]:
    index_path = guides_root / "index.json"
    if not index_path.is_file():
        return [{"code": "missing_content", "identity": "guides:index"}]
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    guides = payload.get("guides") if isinstance(payload, dict) else None
    if not isinstance(guides, list):
        return [{"code": "missing_content", "identity": "guides:index"}]
    issues = []
    ids = set()
    slugs = set()
    for guide in guides:
        if not isinstance(guide, Mapping):
            issues.append({"code": "missing_content", "identity": "guide:invalid"})
            continue
        identity = str(guide.get("id") or "")
        slug = str(guide.get("slug") or "")
        if identity in ids:
            issues.append({"code": "duplicate_identity", "identity": identity})
        if slug in slugs:
            issues.append({"code": "duplicate_slug", "identity": identity})
        ids.add(identity)
        slugs.add(slug)
        cover = guide.get("cover")
        source = cover.get("src") if isinstance(cover, Mapping) else None
        if not isinstance(source, str) or not _image_signature(public_root / source.lstrip("/")):
            issues.append({"code": "missing_image", "identity": identity})
        if not str(guide.get("summaryVi") or "").strip():
            issues.append({"code": "missing_content", "identity": identity})
        detail_path = guides_root / "pages" / (slug + ".json")
        if not detail_path.is_file():
            issues.append({"code": "missing_detail", "identity": identity})
            continue
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        if not isinstance(detail.get("sections"), list) or not detail["sections"]:
            issues.append({"code": "missing_detail", "identity": identity})
    if payload.get("count") != len(guides):
        issues.append({"code": "missing_detail", "identity": "guides:count"})
    return issues


def audit_publication(items_path: Path, guides_root: Path, public_root: Path) -> JsonObject:
    payload = json.loads(items_path.read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise ValueError("items payload must contain an items array")
    issues = _duplicate_issues(items)
    for item in items:
        for code in _item_issues(item, public_root):
            issues.append({"code": code, "identity": item.get("id")})
    issues.extend(_audit_guides(guides_root, public_root))
    return {
        "schemaVersion": 1,
        "items": len(items),
        "guides": json.loads((guides_root / "index.json").read_text()).get("count", 0),
        "issues": issues,
    }


def _category_evidence(category_root: Path) -> Tuple[Dict[str, JsonObject], Dict[str, Tuple[Path, str]]]:
    by_page: Dict[str, JsonObject] = {}
    by_image: Dict[str, Tuple[Path, str]] = {}
    if not category_root.is_dir():
        return by_page, by_image
    for directory in sorted(path for path in category_root.iterdir() if path.is_dir()):
        images = {}
        for row in _read_jsonl(directory / "images.jsonl"):
            title = str(row.get("title") or "")
            source = directory / str(row.get("local_path") or "")
            if title and _image_signature(source):
                images[_image_key(title)] = (source, title)
                by_image.setdefault(_image_key(title), (source, title))
        for page in _read_jsonl(directory / "pages.jsonl"):
            candidates = [
                images[_image_key(str(title))]
                for title in page.get("images", [])
                if _image_key(str(title)) in images
            ]
            if not candidates:
                continue
            title_key = _key(str(page.get("title") or "").split("/", 1)[-1])
            if title_key:
                selected = sorted(candidates, key=lambda row: row[1].casefold())[0]
                by_page.setdefault(
                    title_key,
                    {
                        "source": selected[0],
                        "imageTitle": selected[1],
                        "plainText": str(page.get("plain_text") or ""),
                        "canonicalUrl": str(page.get("canonical_url") or ""),
                    },
                )
    return by_page, by_image


def _publish_quality_asset(source: Path, title: str, public_root: Path) -> JsonObject:
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    extension = source.suffix.casefold() or Path(title).suffix.casefold() or ".bin"
    relative = Path("assets") / "quality" / (digest + extension)
    destination = public_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.is_file():
        temporary = destination.with_name(destination.name + ".tmp")
        shutil.copyfile(source, temporary)
        os.replace(temporary, destination)
    return {
        "src": "/" + relative.as_posix(),
        "uv": {"u1": 0.0, "u2": 1.0, "v1": 0.0, "v2": 1.0},
    }


def _wiki_description(item: Mapping[str, Any], public_root: Path) -> Optional[str]:
    wiki = item.get("wiki")
    if not isinstance(wiki, Mapping) or not isinstance(wiki.get("detailUrl"), str):
        return None
    path = public_root / str(wiki["detailUrl"]).lstrip("/")
    if not path.is_file():
        return None
    detail = json.loads(path.read_text(encoding="utf-8"))
    plain = re.sub(r"\s+", " ", str(detail.get("plainText") or "")).strip()
    if not plain:
        return None
    return plain[:360].rsplit(" ", 1)[0].strip() + "…"


def repair_publication(
    candidates: Iterable[Mapping[str, Any]],
    public_root: Path,
    category_root: Path,
) -> JsonObject:
    source_items = [copy.deepcopy(dict(item)) for item in candidates]
    by_page, by_image = _category_evidence(category_root)
    ingredient_sprites = {}
    for item in source_items:
        recipe = item.get("recipe")
        if not isinstance(recipe, Mapping):
            continue
        for ingredient in recipe.get("ingredients", []):
            if isinstance(ingredient, Mapping) and _valid_sprite(ingredient.get("sprite"), public_root):
                ingredient_sprites.setdefault(str(ingredient.get("id")), ingredient.get("sprite"))

    canonical: Dict[str, JsonObject] = {}
    merged_ids = set()
    rows = []
    for item in source_items:
        code = "{}:{}".format(item.get("namespace") or "", item.get("prefabId") or "").casefold()
        existing = canonical.get(code)
        if existing is None:
            canonical[code] = item
            continue
        for field in ("description", "sprite", "wiki", "recipe", "details", "mob", "structureDetails", "character"):
            if not existing.get(field) and item.get(field):
                existing[field] = item[field]
        merged_ids.add(str(item.get("id")))
        rows.append(
            {
                "identity": item.get("id"),
                "action": "merge",
                "mergedInto": existing.get("id"),
                "initialIssues": ["duplicate_code"],
                "attempts": list(REPAIR_ATTEMPTS),
                "finalIssues": [],
                "sourceUrl": (item.get("wiki") or {}).get("canonicalUrl") if isinstance(item.get("wiki"), Mapping) else None,
                "changes": [],
            }
        )

    repaired_items = []
    for item in canonical.values():
        identity = str(item.get("id") or "")
        initial = _item_issues(item, public_root)
        changes = []
        page_evidence = None
        for value in (item.get("name"), item.get("englishName"), item.get("prefabId")):
            if value and _key(str(value)) in by_page:
                page_evidence = by_page[_key(str(value))]
                break
        if not str(item.get("description") or "").strip():
            description = _wiki_description(item, public_root)
            if description:
                item["description"] = description
                changes.append({"field": "description", "source": "wiki_detail"})
            elif page_evidence is not None:
                plain = re.sub(r"\s+", " ", str(page_evidence.get("plainText") or "")).strip()
                if plain:
                    item["description"] = plain[:360].rsplit(" ", 1)[0].strip() + "…"
                    changes.append(
                        {"field": "description", "source": "reviewed_category_crawl"}
                    )
        if (
            item.get("category") == "character"
            and not _meaningful(item.get("character"))
            and page_evidence is not None
            and str(item.get("description") or "").strip()
        ):
            profile = dict(item.get("character") or {})
            profile.setdefault("abilities", [])
            profile["title"] = str(item["description"]).split(".", 1)[0][:160]
            profile.setdefault("survivability", None)
            profile.setdefault("quote", None)
            item["character"] = profile
            changes.append(
                {"field": "character.title", "source": "reviewed_category_crawl"}
            )
        if not _valid_sprite(item.get("sprite"), public_root):
            evidence = None
            sprite = item.get("sprite")
            if isinstance(sprite, Mapping) and isinstance(sprite.get("src"), str):
                filename = unquote(urlsplit(str(sprite["src"])).path.rsplit("/", 1)[-1])
                evidence = by_image.get(_image_key(filename))
            if evidence is None and page_evidence is not None:
                evidence = (
                    page_evidence["source"],
                    page_evidence["imageTitle"],
                )
            if evidence is not None:
                item["sprite"] = _publish_quality_asset(evidence[0], evidence[1], public_root)
                changes.append({"field": "sprite", "source": "reviewed_category_crawl"})
            elif identity in ingredient_sprites:
                item["sprite"] = ingredient_sprites[identity]
                changes.append({"field": "sprite", "source": "catalog_recipe_evidence"})
        final = _item_issues(item, public_root)
        action = "remove" if final else ("repair" if changes else "keep")
        row = {
            "identity": identity,
            "code": item.get("prefabId"),
            "category": item.get("category"),
            "action": action,
            "initialIssues": initial,
            "attempts": list(REPAIR_ATTEMPTS),
            "finalIssues": final,
            "sourceUrl": (
                (item.get("wiki") or {}).get("canonicalUrl")
                if isinstance(item.get("wiki"), Mapping)
                else (page_evidence or {}).get("canonicalUrl")
            ),
            "changes": changes,
        }
        rows.append(row)
        if action != "remove":
            repaired_items.append(item)

    rows.sort(key=lambda row: (str(row.get("identity", "")).casefold(), row["action"]))
    repaired_items.sort(key=lambda item: str(item.get("id", "")).casefold())
    summary = {action: sum(row["action"] == action for row in rows) for action in ("keep", "repair", "merge", "remove")}
    summary.update({"before": len(source_items), "after": len(repaired_items)})
    return {"items": repaired_items, "rows": rows, "summary": summary}


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def run_publication_quality(
    items_path: Path,
    guides_root: Path,
    public_root: Path,
    category_root: Path,
    report_path: Path,
    apply: bool = False,
) -> JsonObject:
    payload = json.loads(items_path.read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        raise ValueError("items payload must contain an items array")
    before = audit_publication(items_path, guides_root, public_root)

    temporary_context = None
    repair_root = public_root
    if not apply:
        temporary_context = tempfile.TemporaryDirectory()
        repair_root = Path(temporary_context.name) / "public"
        repair_root.mkdir()
        for child in public_root.iterdir():
            if child.name != "assets":
                (repair_root / child.name).symlink_to(child.resolve(), target_is_directory=child.is_dir())
                continue
            mirrored_assets = repair_root / "assets"
            mirrored_assets.mkdir()
            for asset_group in child.iterdir():
                if asset_group.name == "quality":
                    mirrored_quality = mirrored_assets / "quality"
                    mirrored_quality.mkdir()
                    for asset in asset_group.iterdir():
                        (mirrored_quality / asset.name).symlink_to(asset.resolve())
                    continue
                (mirrored_assets / asset_group.name).symlink_to(
                    asset_group.resolve(), target_is_directory=asset_group.is_dir()
                )

    try:
        result = repair_publication(items, repair_root, category_root)
        post_issues = _duplicate_issues(result["items"])
        for item in result["items"]:
            for code in _item_issues(item, repair_root):
                post_issues.append({"code": code, "identity": item.get("id")})
        post_issues.extend(_audit_guides(guides_root, public_root))
    finally:
        if temporary_context is not None:
            temporary_context.cleanup()
    report = {
        "schemaVersion": 1,
        "mode": "apply" if apply else "audit",
        "summary": result["summary"],
        "beforeIssues": before["issues"],
        "postRepairIssues": post_issues,
        "rows": result["rows"],
        "guides": before["guides"],
    }
    if apply and post_issues:
        _write_json_atomic(report_path, report)
        raise ValueError("publication candidate still has hard failures")
    if apply:
        repaired_payload = dict(payload)
        repaired_payload["items"] = result["items"]
        _write_json_atomic(items_path, repaired_payload)
    _write_json_atomic(report_path, report)
    return report
