"""Conservative Mob/Boss enrichment from the local full-Wiki JSONL crawl."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence

from tools.extract.wiki_mapping import (
    build_entity_index,
    extract_spawn_codes,
    map_page,
    normalize_identity,
)


JsonObject = Dict[str, Any]
SENTENCE = re.compile(r"(?<=[.!?])\s+")
SOURCE_WORDS = re.compile(
    r"\b(?:spawn|spawns|spawned|summon|summoned|appears|encountered|found)\b",
    re.IGNORECASE,
)
MECHANIC_WORDS = re.compile(
    r"\b(?:attack|attacks|summons?|transforms?|becomes?|immune|enraged?|"
    r"targets?|teleports?|will not|cannot|phase|absorbing|active|inert)\b",
    re.IGNORECASE,
)
INFOBOX_START = re.compile(r"(?=\{\{(?:Object|Mob)\s+Infobox\b)", re.IGNORECASE)
IMAGE_FIELD = re.compile(r"\|\s*image\s*=\s*([^|}\n]+)", re.IGNORECASE)


def _image_title(value: str) -> Optional[str]:
    value = value.strip()
    file_match = re.search(r"(?:File:)?([^\]|]+\.(?:png|jpe?g|gif|webp))", value, re.IGNORECASE)
    if file_match is None:
        return None
    return file_match.group(1).strip().removeprefix("File:")


def _variant_image_titles(page: Mapping[str, Any]) -> Dict[str, str]:
    wikitext = page.get("wikitext")
    if not isinstance(wikitext, str):
        return {}
    result: Dict[str, str] = {}
    for chunk in INFOBOX_START.split(wikitext):
        image_match = IMAGE_FIELD.search(chunk)
        if image_match is None:
            continue
        title = _image_title(image_match.group(1))
        if title is None:
            continue
        for spawn_code in extract_spawn_codes(chunk):
            result.setdefault(spawn_code, title)
    return dict(sorted(result.items()))


def _summary(page: Mapping[str, Any]) -> Optional[str]:
    plain_text = page.get("plain_text")
    if not isinstance(plain_text, str):
        return None
    paragraphs = [
        " ".join(value.split())
        for value in re.split(r"\n\s*\n|\n", plain_text)
        if value.strip()
    ]
    for paragraph in paragraphs:
        if len(paragraph) < 20 or paragraph.casefold().startswith("exclusive to"):
            continue
        return SENTENCE.split(paragraph, maxsplit=1)[0].strip()
    return None


def _intro_text(page: Mapping[str, Any]) -> str:
    plain_text = page.get("plain_text")
    if not isinstance(plain_text, str):
        return ""
    lines = []
    for line in plain_text.splitlines():
        if line.strip().casefold() == "contents":
            break
        lines.append(line)
    return " ".join(" ".join(lines).split())


def _sources(page: Mapping[str, Any]) -> list[str]:
    intro = _intro_text(page)
    if not intro:
        return []
    values = []
    for sentence in SENTENCE.split(intro):
        sentence = sentence.strip()
        if SOURCE_WORDS.search(sentence) and 20 <= len(sentence) <= 280:
            values.append(sentence)
        if len(values) == 3:
            break
    return list(dict.fromkeys(values))


def _mechanics(page: Mapping[str, Any]) -> list[str]:
    intro = _intro_text(page)
    if not intro:
        return []
    values = []
    for sentence in SENTENCE.split(intro):
        sentence = sentence.strip()
        if MECHANIC_WORDS.search(sentence) and 20 <= len(sentence) <= 280:
            values.append(sentence)
        if len(values) == 3:
            break
    return list(dict.fromkeys(values))


def _normalize_page(page: Mapping[str, Any], method: str) -> JsonObject:
    images = page.get("images")
    image_titles = sorted(
        {
            str(value).removeprefix("File:")
            for value in images if isinstance(value, str) and value.strip()
        }
    ) if isinstance(images, list) else []
    categories = page.get("categories")
    page_id = page.get("page_id")
    variant_images = _variant_image_titles(page)
    primary_image = next(iter(variant_images.values()), None)
    if primary_image is None and image_titles:
        page_identity = normalize_identity(str(page.get("title") or ""))
        primary_image = next(
            (
                title
                for title in image_titles
                if page_identity and page_identity in normalize_identity(title)
            ),
            None,
        )
    return {
        "pageId": page_id if isinstance(page_id, int) else None,
        "title": str(page.get("title") or ""),
        "canonicalUrl": str(page.get("canonical_url") or ""),
        "summary": _summary(page),
        "categories": sorted(
            str(value).removeprefix("Category:")
            for value in categories if isinstance(value, str)
        ) if isinstance(categories, list) else [],
        "sources": _sources(page),
        "mechanics": _mechanics(page),
        "imageTitles": image_titles,
        "primaryImageTitle": primary_image,
        "variantImageTitles": variant_images,
        "mappingMethod": method,
        "evidence": [
            {
                "source": "data/crawled/dontstarve-wiki/pages.jsonl",
                "locator": f"page:{page_id}" if page_id is not None else str(page.get("title") or ""),
            }
        ],
    }


def load_mob_wiki_details(
    pages_path: Path,
    items: Sequence[JsonObject],
    groups: Sequence[JsonObject] = (),
) -> Dict[str, JsonObject]:
    grouped_members = {
        str(member["id"]): str(group["canonicalId"])
        for group in groups
        if isinstance(group, Mapping) and isinstance(group.get("canonicalId"), str)
        for member in group.get("members", [])
        if isinstance(member, Mapping) and isinstance(member.get("id"), str)
    }
    rows = [
        {
            "namespace": str(item["id"]).split(":", 1)[0],
            "prefab_id": str(item.get("prefabId") or ""),
            "name_en": item.get("englishName"),
        }
        for item in items
        if str(item.get("id") or "").startswith("base_game:")
        and grouped_members.get(str(item["id"]), str(item["id"])) == str(item["id"])
    ]
    index = build_entity_index(rows)
    candidates: Dict[str, list[tuple[float, JsonObject]]] = {}
    with Path(pages_path).open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            page = json.loads(line)
            if not isinstance(page, dict) or page.get("namespace") != 0:
                continue
            decision = map_page(page, index)
            if decision.entity_key is None:
                continue
            normalized = _normalize_page(page, decision.method)
            candidates.setdefault(decision.entity_key, []).append(
                (decision.confidence, normalized)
            )

    result: Dict[str, JsonObject] = {}
    for item_id, values in sorted(candidates.items()):
        best_confidence = max(confidence for confidence, _ in values)
        best = [value for confidence, value in values if confidence == best_confidence]
        page_ids = {value.get("pageId") for value in best}
        if len(page_ids) != 1:
            continue
        result[item_id] = best[0]
    return result
