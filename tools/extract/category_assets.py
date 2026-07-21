"""Publish only primary images referenced by a normalized category artifact."""

import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Mapping


_EXTENSIONS = {
    "image/gif": ".gif",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def publish_category_assets(
    artifact: Mapping[str, Any], crawl_root: Path, output: Path
) -> List[Dict[str, Any]]:
    """Stage, verify and atomically replace one category's public image directory."""

    category = artifact.get("category")
    pages = artifact.get("pages")
    if not isinstance(category, str) or not category or not isinstance(pages, list):
        raise ValueError("category artifact is invalid")
    crawl_root = Path(crawl_root).resolve()
    output = Path(output)
    records = _image_records(crawl_root / "images.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.parent / ("." + output.name + ".staging-" + uuid.uuid4().hex)
    backup = output.parent / ("." + output.name + ".backup-" + uuid.uuid4().hex)
    staging.mkdir()
    published = []
    try:
        for page in sorted(pages, key=_page_id):
            if not isinstance(page, dict):
                continue
            visual = page.get("visual")
            if not isinstance(visual, dict):
                continue
            requested_title = visual.get("sourceTitle")
            if not isinstance(requested_title, str):
                continue
            record = records.get(_title_key(requested_title))
            if record is None:
                continue
            title = record["title"]
            visual["sourceTitle"] = title
            source = _safe_source(crawl_root, record.get("local_path"))
            digest = _sha256(source)
            expected = record.get("sha256")
            if not isinstance(expected, str) or digest != expected.casefold():
                raise ValueError("category image hash mismatch: " + title)
            mime = record.get("mime")
            extension = _EXTENSIONS.get(mime)
            if extension is None:
                raise ValueError("unsupported category image MIME: {}".format(mime))
            filename = digest + extension
            destination = staging / filename
            if not destination.exists():
                shutil.copyfile(source, destination)
            public_path = "/assets/wiki-categories/{}/{}".format(category, filename)
            page_id = _page_id(page)
            asset = {
                "pageId": page_id,
                "sourceTitle": title,
                "sha256": digest,
                "mime": mime,
                "publicPath": public_path,
            }
            visual["asset"] = asset
            published.append(asset)
        if output.exists():
            os.replace(str(output), str(backup))
        os.replace(str(staging), str(output))
        if backup.exists():
            shutil.rmtree(backup)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        if backup.exists() and not output.exists():
            os.replace(str(backup), str(output))
        raise
    return sorted(published, key=lambda value: (value["pageId"], value["sourceTitle"]))


def _image_records(path: Path) -> Dict[str, Mapping[str, Any]]:
    if not path.is_file():
        return {}
    records = {}
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError("invalid image JSONL at {}:{}".format(path, line_number)) from error
            title = value.get("title") if isinstance(value, dict) else None
            if not isinstance(title, str) or not title:
                raise ValueError("category image record has no title")
            records[_title_key(title)] = value
    return records


def _title_key(value: str) -> str:
    return " ".join(value.replace("_", " ").casefold().split())


def _safe_source(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("category image record has no local path")
    candidate = Path(value)
    path = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError("category image path escapes crawl root") from error
    if not path.is_file():
        raise ValueError("category image file is missing: " + str(path))
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _page_id(page: Any) -> int:
    if not isinstance(page, Mapping):
        return 0
    identity = page.get("identity")
    value = identity.get("sourcePageId") if isinstance(identity, Mapping) else None
    return value if isinstance(value, int) else 0
