"""Normalize conservative, structure-specific facts from Wiki page records."""

import html
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


JsonObject = Dict[str, Any]
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]+>")
_WIKI_LINK = re.compile(r"\[\[([^\[\]]+)\]\]")
_WHITESPACE = re.compile(r"\s+")


def _balanced_templates(value: str) -> Iterable[str]:
    start: Optional[int] = None
    depth = 0
    index = 0
    while index < len(value) - 1:
        pair = value[index : index + 2]
        if pair == "{{":
            if depth == 0:
                start = index
            depth += 1
            index += 2
            continue
        if pair == "}}" and depth:
            depth -= 1
            index += 2
            if depth == 0 and start is not None:
                yield value[start:index]
                start = None
            continue
        index += 1


def _split_top_level(value: str, separator: str) -> List[str]:
    parts: List[str] = []
    start = 0
    template_depth = 0
    link_depth = 0
    index = 0
    while index < len(value):
        pair = value[index : index + 2]
        if pair == "{{":
            template_depth += 1
            index += 2
            continue
        if pair == "}}" and template_depth:
            template_depth -= 1
            index += 2
            continue
        if pair == "[[":
            link_depth += 1
            index += 2
            continue
        if pair == "]]" and link_depth:
            link_depth -= 1
            index += 2
            continue
        if (
            value[index] == separator
            and template_depth == 0
            and link_depth == 0
        ):
            parts.append(value[start:index])
            start = index + 1
        index += 1
    parts.append(value[start:])
    return parts


def _replace_wiki_link(match: re.Match) -> str:
    parts = match.group(1).split("|")
    return parts[-1].split("#", 1)[0].strip()


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    result = _COMMENT.sub("", value)
    result = _WIKI_LINK.sub(_replace_wiki_link, result)
    result = _HTML_TAG.sub(" ", result)
    result = result.replace("'''", "").replace("''", "")
    result = html.unescape(result).replace("_", " ")
    result = _WHITESPACE.sub(" ", result).strip()
    return result or None


def _object_infobox_fields(wikitext: str) -> Dict[str, str]:
    for template in _balanced_templates(wikitext):
        content = template[2:-2]
        parts = _split_top_level(content, "|")
        if not parts or _WHITESPACE.sub(" ", parts[0]).strip().casefold() != "object infobox":
            continue
        result: Dict[str, str] = {}
        for part in parts[1:]:
            field = _split_top_level(part, "=")
            if len(field) < 2:
                continue
            key = field[0].strip().casefold()
            if key:
                result[key] = "=".join(field[1:]).strip()
        return result
    return {}


def _truth(value: Optional[str]) -> Optional[bool]:
    cleaned = (_clean(value) or "").casefold()
    if cleaned in {"yes", "true", "renewable"}:
        return True
    if cleaned in {"no", "false", "non-renewable", "not renewable"}:
        return False
    return None


def _evidence(page: Mapping[str, Any]) -> List[JsonObject]:
    revision = page.get("revision")
    revision_id = revision.get("id") if isinstance(revision, Mapping) else None
    return [
        {
            "source": str(page["canonical_url"]),
            "locator": f"revision:{revision_id}",
        }
    ]


def _fact(
    key: str,
    label: str,
    value: str,
    evidence: List[JsonObject],
) -> JsonObject:
    return {
        "key": key,
        "label": label,
        "value": value,
        "unit": None,
        "context": None,
        "related": [],
        "evidence": evidence,
    }


def _function_facts(
    fields: Mapping[str, str],
    wikitext: str,
    evidence: List[JsonObject],
) -> List[JsonObject]:
    text = (_clean(wikitext) or "").casefold()
    facts: Dict[str, JsonObject] = {}

    fuel = _clean(fields.get("fuel"))
    if fuel:
        facts["fuel"] = _fact("fuel", "Nhiên liệu", fuel, evidence)

    spawned = _clean(fields.get("spawns") or fields.get("spawn"))
    if spawned:
        facts["spawns"] = _fact("spawns", "Sinh ra", spawned, evidence)

    storage = _clean(fields.get("storage") or fields.get("slots"))
    if storage:
        facts["storage"] = _fact("storage", "Sức chứa", storage, evidence)

    if re.search(r"\b(?:provides?|emits?|produces?) light\b", text):
        facts["light"] = _fact("light", "Ánh sáng", "Có", evidence)
    if re.search(r"\b(?:provides?|produces?) (?:light and )?warmth\b", text):
        facts["warmth"] = _fact("warmth", "Nhiệt", "Có", evidence)

    return [facts[key] for key in sorted(facts)]


def _valid_image_title(title: str) -> bool:
    folded = title.casefold()
    if folded.startswith("file:image:"):
        return False
    basename = title.split(":", 1)[-1].strip()
    if re.fullmatch(r"\d+px(?:\.[a-z0-9]+)?", basename, re.I):
        return False
    return bool(re.search(r"\.(?:png|jpe?g|gif|webp)$", basename, re.I))


def _visual_candidates(
    page: Mapping[str, Any], fields: Mapping[str, str], evidence: List[JsonObject]
) -> List[JsonObject]:
    values: List[JsonObject] = []
    for key in ("image", "icon"):
        title = _clean(fields.get(key))
        if not title:
            continue
        if not title.casefold().startswith("file:"):
            title = "File:" + title
        if _valid_image_title(title):
            values.append({"title": title, "evidence": evidence})

    if not values:
        page_title = str(page.get("title") or "").replace("_", " ").strip()
        expected = f"File:{page_title}.png".replace("_", " ").casefold()
        images = page.get("images")
        if isinstance(images, list):
            for raw_title in images:
                if not isinstance(raw_title, str):
                    continue
                title = raw_title if raw_title.casefold().startswith("file:") else "File:" + raw_title
                comparable = title.replace("_", " ").casefold()
                if comparable == expected and _valid_image_title(title):
                    values.append({"title": title, "evidence": evidence})
                    break
    unique = {value["title"]: value for value in values}
    return [unique[key] for key in sorted(unique)]


def normalize_structure_page(
    page: Mapping[str, Any],
) -> Optional[JsonObject]:
    """Return conservative normalized facts for a Wiki structure page."""

    categories = page.get("categories")
    if not isinstance(categories, list) or not any(
        isinstance(value, str) and "structure" in value.casefold()
        for value in categories
    ):
        return None

    wikitext = str(page.get("wikitext") or "")
    fields = _object_infobox_fields(wikitext)
    evidence = _evidence(page)
    plain_text = (_clean(wikitext) or "").casefold()
    naturally_spawned = bool(
        re.search(r"\b(?:found|spawn(?:s|ed)?) naturally\b", plain_text)
        or "naturally-spawning" in plain_text
        or "naturally spawning" in plain_text
    )
    renewable = _truth(fields.get("renewable"))
    functions = _function_facts(fields, wikitext, evidence)
    tool = _clean(fields.get("tool") or fields.get("tool required"))
    destroyable: Optional[bool] = None
    if tool and re.search(r"can(?:not|'t) be destroyed|indestructible", tool, re.I):
        destroyable = False
    elif tool:
        destroyable = True

    return {
        "origin": {
            "status": "known" if naturally_spawned or renewable is not None else "unknown",
            "naturallySpawned": naturally_spawned,
            "renewable": renewable,
            "spawnCode": _clean(fields.get("spawncode") or fields.get("spawn code")),
            "sources": [],
            "respawn": "Có" if "respawn" in plain_text else None,
            "evidence": evidence,
        },
        "functions": {
            "status": "known" if functions else "unknown",
            "facts": functions,
            "reason": None if functions else "Wiki page has no normalized function facts.",
            "evidence": evidence,
        },
        "destruction": {
            "status": "known" if destroyable is not None else "unknown",
            "destroyable": destroyable,
            "tool": tool,
            "work": None,
            "health": None,
            "burnable": None,
            "drops": [],
            "regeneration": "Có" if "respawn" in plain_text else None,
            "evidence": evidence,
        },
        "visual_candidates": _visual_candidates(page, fields, evidence),
    }
