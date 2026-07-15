import html
import json
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from tools.crawl_wiki.models import SCHEMA_VERSION


_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_TAG = re.compile(r"<[^>]+>")
_WIKI_LINK = re.compile(r"\[\[([^\[\]]+)\]\]")
_WHITESPACE = re.compile(r"\s+")
_SIZE = re.compile(r"^\d+(?:x\d+)?px$", re.IGNORECASE)
_INGREDIENT_KEY = re.compile(r"^ingredient(\d+)(.*)$", re.IGNORECASE)
_ITEM_KEY = re.compile(r"^item(\d+)$", re.IGNORECASE)


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


def _split_field(value: str) -> Optional[Tuple[str, str]]:
    parts = _split_top_level(value, "=")
    if len(parts) < 2:
        return None
    return parts[0].strip(), "=".join(parts[1:]).strip()


def _parse_template(value: str) -> Tuple[str, Dict[str, str], List[str]]:
    content = value.strip()
    if content.startswith("{{") and content.endswith("}}"):
        content = content[2:-2]
    parts = _split_top_level(content, "|")
    name = parts[0].strip() if parts else ""
    fields: Dict[str, str] = {}
    positional: List[str] = []
    for part in parts[1:]:
        field = _split_field(part)
        if field is None:
            positional.append(part.strip())
            continue
        key, field_value = field
        fields[key.strip()] = field_value.strip()
    return name, fields, positional


def _replace_wiki_link(match: re.Match) -> str:
    content = match.group(1)
    parts = content.split("|")
    selected = parts[-1] if len(parts) > 1 else parts[0]
    return selected.split("#", 1)[0]


def _clean_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = _COMMENT.sub("", value).strip()
    if not cleaned:
        return None

    templates = list(_balanced_templates(cleaned))
    if len(templates) == 1 and templates[0].strip() == cleaned:
        _, fields, positional = _parse_template(cleaned)
        candidates = [
            item
            for item in positional
            if item and not _SIZE.match(item.strip())
        ]
        if not candidates and "link" in fields:
            candidates = [fields["link"]]
        if candidates:
            cleaned = candidates[-1]

    cleaned = _WIKI_LINK.sub(_replace_wiki_link, cleaned)
    cleaned = _HTML_TAG.sub(" ", cleaned)
    cleaned = cleaned.replace("'''", "").replace("''", "")
    cleaned = html.unescape(cleaned).replace("_", " ")
    cleaned = _WHITESPACE.sub(" ", cleaned).strip()
    return cleaned or None


def _count(value: Optional[str]) -> Any:
    cleaned = _clean_value(value)
    if cleaned is None:
        return 1.0
    numeric = cleaned.lower().lstrip("x").strip()
    try:
        return float(numeric)
    except ValueError:
        return cleaned


def _field(
    fields: Mapping[str, str], name: str, suffix: str = ""
) -> Optional[str]:
    by_casefold = {key.casefold(): value for key, value in fields.items()}
    if suffix:
        variant = by_casefold.get((name + suffix).casefold())
        if variant is not None:
            return variant
    return by_casefold.get(name.casefold())


def _ingredients(
    fields: Mapping[str, str], keys: Sequence[Tuple[int, str]], count_prefix: str
) -> List[Dict[str, Any]]:
    ingredients: List[Dict[str, Any]] = []
    by_casefold = {key.casefold(): value for key, value in fields.items()}
    for number, key in sorted(keys):
        title = _clean_value(fields[key])
        if title is None:
            continue
        suffix_match = _INGREDIENT_KEY.match(key)
        suffix = suffix_match.group(2) if suffix_match else ""
        count_value = by_casefold.get(
            "{}{}{}".format(count_prefix, number, suffix).casefold()
        )
        ingredients.append({"title": title, "count": _count(count_value)})
    return ingredients


def _canonical_title(value: Optional[str]) -> str:
    cleaned = (_clean_value(value) or "").strip()
    if cleaned.casefold().endswith("/dst"):
        cleaned = cleaned[:-4]
    return cleaned.casefold()


def _record(
    page_id: int,
    result: str,
    source: str,
    variant: str,
    ingredients: List[Dict[str, Any]],
    station: Optional[str],
    tab: Optional[str],
    tier: Optional[str],
    dlc: Optional[str],
    character: Optional[str],
    note: Optional[str],
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "page_id": page_id,
        "result": result,
        "source": source,
        "variant": variant,
        "ingredients": ingredients,
        "station": station,
        "tab": tab,
        "tier": tier,
        "dlc": dlc,
        "character": character,
        "note": note,
    }


def _infobox_records(
    page_id: int, title: str, fields: Mapping[str, str]
) -> List[Dict[str, Any]]:
    variants: Dict[str, List[Tuple[int, str]]] = {}
    for key in fields:
        match = _INGREDIENT_KEY.match(key)
        if match is None:
            continue
        variants.setdefault(match.group(2), []).append((int(match.group(1)), key))

    records: List[Dict[str, Any]] = []
    for suffix in sorted(variants, key=lambda value: (bool(value), value.casefold())):
        ingredients = _ingredients(fields, variants[suffix], "multiplier")
        if not ingredients:
            continue
        records.append(
            _record(
                page_id=page_id,
                result=title,
                source="Object Infobox",
                variant=suffix or "base",
                ingredients=ingredients,
                station=_clean_value(_field(fields, "tool", suffix)),
                tab=_clean_value(_field(fields, "tab", suffix)),
                tier=_clean_value(_field(fields, "tier", suffix)),
                dlc=_clean_value(_field(fields, "dlc", suffix)),
                character=_clean_value(_field(fields, "character", suffix)),
                note=_clean_value(_field(fields, "note", suffix)),
            )
        )
    return records


def _recipe_record(
    page_id: int, title: str, fields: Mapping[str, str]
) -> Optional[Dict[str, Any]]:
    if _canonical_title(fields.get("result")) != _canonical_title(title):
        return None
    item_keys: List[Tuple[int, str]] = []
    for key in fields:
        match = _ITEM_KEY.match(key)
        if match is not None:
            item_keys.append((int(match.group(1)), key))
    ingredients: List[Dict[str, Any]] = []
    by_casefold = {key.casefold(): value for key, value in fields.items()}
    for number, key in sorted(item_keys):
        item_title = _clean_value(fields[key])
        if item_title is None:
            continue
        ingredients.append(
            {
                "title": item_title,
                "count": _count(by_casefold.get("count{}".format(number))),
            }
        )
    if not ingredients:
        return None
    return _record(
        page_id=page_id,
        result=title,
        source="Recipe",
        variant=_clean_value(fields.get("dlc")) or "base",
        ingredients=ingredients,
        station=_clean_value(fields.get("tool")),
        tab=None,
        tier=None,
        dlc=_clean_value(fields.get("dlc")),
        character=_clean_value(fields.get("character")),
        note=_clean_value(fields.get("note")),
    )


def extract_recipes(
    page_id: int, title: str, wikitext: str
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for template in _balanced_templates(wikitext):
        name, fields, _ = _parse_template(template)
        normalized_name = _WHITESPACE.sub(" ", name).strip().casefold()
        if normalized_name == "object infobox":
            records.extend(_infobox_records(page_id, title, fields))
        elif normalized_name == "recipe":
            record = _recipe_record(page_id, title, fields)
            if record is not None:
                records.append(record)

    unique: Dict[str, Dict[str, Any]] = {}
    for record in records:
        identity = json.dumps(
            record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        unique[identity] = record
    return list(unique.values())
