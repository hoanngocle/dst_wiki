import json
import html
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from tools.crawl_wiki.category_config import CategoryConfig
from tools.extract.category_notes import ReviewedNote, build_note_review
_FIELD_SPECS = {
    "stats": (("max_health", "Health", ("health", "hp")),),
    "effects": (("sanity_aura", "Sanity Aura", ("sanityaura", "sanity")),),
    "combat": (
        ("attack_damage", "Damage", ("damage", "attackdamage")),
        ("attack_period", "Attack Period", ("attackperiod",)),
        ("attack_range", "Attack Range", ("attackrange",)),
    ),
    "movement": (
        ("walk_speed", "Walking Speed", ("walkspeed", "walkingspeed")),
        ("run_speed", "Running Speed", ("runspeed", "runningspeed")),
    ),
}
_NON_DST_MARKERS = re.compile(
    r"Shipwrecked|Hamlet|Reign of Giants|\bDS\b|Don't Starve(?!\s+Together)",
    re.I,
)
_DST_TEMPLATE = re.compile(r"\{\{\s*DST\s*\|([^{}]+)\}\}", re.I)
_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")
_PREFAB_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


def extract_mob_page(
    page: Mapping[str, Any],
    config: CategoryConfig,
    mappings: Mapping[Any, Any],
) -> Dict[str, Any]:
    page_id = _positive_int(page.get("page_id"), "page_id")
    title = _string(page.get("title"), "title")
    source_url = _string(page.get("canonical_url"), "canonical_url")
    revision = page.get("revision")
    if not isinstance(revision, Mapping):
        raise ValueError("Mob page revision is missing")
    revision_id = _positive_int(revision.get("id"), "revision.id")
    wikitext = _string(page.get("wikitext"), "wikitext")
    fields = _infobox_fields(wikitext)
    codes, variants = _prefab_identity(page_id, title, wikitext, mappings)
    evidence_root = {
        "source": "fandom",
        "pageId": page_id,
        "revisionId": revision_id,
        "sourceUrl": source_url,
        "game": "DST",
    }

    sections = {}
    for section, specs in _FIELD_SPECS.items():
        values = []
        ambiguous = False
        for key, label, aliases in specs:
            raw_key, raw_value = _first_field(fields, aliases)
            if raw_value is None:
                continue
            selected, reason = _dst_value(raw_value)
            if reason == "ambiguous_game_version":
                ambiguous = True
                continue
            if selected is None:
                continue
            evidence = dict(evidence_root)
            evidence["locator"] = "infobox:{}".format(raw_key)
            values.append(
                {
                    "key": key,
                    "label": label,
                    "value": _scalar(selected),
                    "unit": None,
                    "sourceVariant": None,
                    "evidence": [evidence],
                }
            )
        sections[section] = _section(
            values,
            "ambiguous_game_version" if ambiguous and not values else None,
        )

    trait_key, trait_raw = _first_field(
        fields, ("specialability", "specialabilities", "traits", "ability")
    )
    trait_values = []
    if trait_raw is not None:
        selected, _ = _dst_value(trait_raw)
        for text in _split_list(selected or ""):
            trait_values.append({"text": text, "sourceVariant": None})

    _, loot_raw = _first_field(fields, ("loot", "drops", "drop"))
    loot_values = []
    if loot_raw is not None:
        selected, _ = _dst_value(loot_raw)
        loot_values = [_loot(value) for value in _split_list(selected or "")]

    _, spawn_raw = _first_field(fields, ("spawnsfrom", "spawnfrom"))
    spawn_values = []
    if spawn_raw is not None:
        selected, _ = _dst_value(spawn_raw)
        spawn_values = [
            {
                "sourceTitle": value,
                "conditions": None,
                "sourceVariant": None,
            }
            for value in _split_list(selected or "")
        ]

    image_title = _infobox_image(fields)
    visual = (
        {"sourceTitle": image_title, "asset": None}
        if image_title is not None
        else None
    )

    return {
        "schemaVersion": 1,
        "identity": {
            "id": "base_game:{}".format(codes[0]),
            "name": title,
            "englishName": title,
            "primaryCode": codes[0],
            "prefabCodes": list(codes),
            "sourcePageId": page_id,
            "sourceUrl": source_url,
            "revisionId": revision_id,
        },
        "classification": {
            "type": config.item_type,
            "tags": list(config.tags),
            "game": "DST",
        },
        "visual": visual,
        "summary": _summary(page.get("plain_text"), title),
        **sections,
        "traits": _section(trait_values),
        "loot": _section(loot_values),
        "spawnsFrom": _section(spawn_values),
        "notes": _section([], "not_reviewed"),
        "variants": variants,
        "evidence": [evidence_root],
    }


def normalize_category_mobs(
    crawl_root: Path,
    config: CategoryConfig,
    mappings: Mapping[Any, Any],
    summaries: Mapping[Any, Any],
) -> Dict[str, Any]:
    root = Path(crawl_root)
    pages = _read_jsonl(root / "pages.jsonl")
    if len(pages) != config.expected_published_pages:
        raise ValueError(
            "category page count mismatch: expected {}, got {}".format(
                config.expected_published_pages, len(pages)
            )
        )
    review = build_note_review(pages, config)
    mobs = []
    for page in sorted(pages, key=lambda value: int(value["page_id"])):
        mob = extract_mob_page(page, config, mappings)
        page_id = int(page["page_id"])
        note = review["pages"].get(str(page_id))
        if note is None:
            mob["notes"] = {"status": "none", "values": [], "reason": "source_has_no_notes", "evidence": []}
        else:
            reviewed = _reviewed_summary(summaries.get(page_id, summaries.get(str(page_id))))
            if reviewed is None or reviewed.source_sha256 != note["source_sha256"]:
                raise ValueError(
                    "page {} requires a reviewed Vietnamese summary".format(page_id)
                )
            mob["notes"] = {
                "status": "known",
                "values": [
                    {
                        "source": note["source"],
                        "summaryVi": reviewed.vi,
                        "sourceSha256": reviewed.source_sha256,
                        "status": "reviewed",
                    }
                ],
                "reason": None,
                "evidence": [],
            }
        mobs.append(mob)

    seeds_path = root / "seeds.jsonl"
    seeds = _read_jsonl(seeds_path) if seeds_path.is_file() else []
    return {
        "schemaVersion": 1,
        "category": config.key,
        "game": "DST",
        "pages": mobs,
        "discovery": {"seeds": seeds},
    }


def load_prefab_mappings(path: Path) -> Mapping[int, Mapping[str, Any]]:
    path = Path(path)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("invalid category prefab mapping file: {}".format(path)) from error
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("category prefab mapping schema is invalid")
    pages = payload.get("pages")
    if not isinstance(pages, dict):
        raise ValueError("category prefab mapping pages must be an object")
    result = {}
    for raw_page_id, value in pages.items():
        try:
            page_id = int(raw_page_id)
        except (TypeError, ValueError) as error:
            raise ValueError("category prefab mapping page ID is invalid") from error
        if page_id <= 0 or not isinstance(value, dict):
            raise ValueError("category prefab mapping entry is invalid")
        result[page_id] = value
    return result


def write_category_mobs(
    crawl_root: Path,
    config: CategoryConfig,
    mappings: Mapping[Any, Any],
    summaries: Mapping[Any, Any],
    output: Path,
) -> Dict[str, Any]:
    artifact = normalize_category_mobs(crawl_root, config, mappings, summaries)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(".{}.tmp".format(output.name))
    temporary.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(str(temporary), str(output))
    return artifact


def _section(values: Sequence[Mapping[str, Any]], reason: Optional[str] = None):
    if values:
        return {"status": "known", "values": list(values), "reason": None, "evidence": []}
    return {
        "status": "unknown" if reason else "unknown",
        "values": [],
        "reason": reason or "not_found",
        "evidence": [],
    }


def _infobox_fields(wikitext: str) -> Dict[str, str]:
    for content in _top_level_templates(wikitext):
        parts = _split_top_level(content, "|")
        if not parts or "infobox" not in parts[0].casefold():
            continue
        fields = {}
        for part in parts[1:]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            normalized = re.sub(r"[^a-z0-9]+", "", key.casefold())
            if normalized:
                fields[normalized] = value.strip()
        return fields
    raise ValueError("Mob page has no supported infobox")


def _top_level_templates(value: str) -> Iterable[str]:
    depth = 0
    start = None
    index = 0
    while index < len(value) - 1:
        pair = value[index : index + 2]
        if pair == "{{":
            if depth == 0:
                start = index + 2
            depth += 1
            index += 2
            continue
        if pair == "}}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                yield value[start:index]
                start = None
            index += 2
            continue
        index += 1


def _split_top_level(value: str, separator: str) -> List[str]:
    parts = []
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
        if value[index] == separator and template_depth == 0 and link_depth == 0:
            parts.append(value[start:index])
            start = index + 1
        index += 1
    parts.append(value[start:])
    return parts


def _first_field(fields: Mapping[str, str], aliases: Sequence[str]):
    for alias in aliases:
        if alias in fields:
            return alias, fields[alias]
    return aliases[0], None


def _dst_value(raw: str) -> Tuple[Optional[str], Optional[str]]:
    dst = [value.strip() for value in _DST_TEMPLATE.findall(raw) if value.strip()]
    if dst:
        return _clean_markup(dst[0]), None
    cleaned = _clean_markup(raw)
    if _NON_DST_MARKERS.search(raw):
        if "don't starve together" in raw.casefold() and re.search(r"[/|]", raw):
            return None, "ambiguous_game_version"
        return None, "non_dst_only"
    return (cleaned, None) if cleaned else (None, "not_found")


def _clean_markup(value: str) -> str:
    value = re.sub(r"<\s*(?:br|hr)\b[^>]*>", ";", value, flags=re.I)
    value = re.sub(
        r"\[\[File:[^\]|]+(?:\|[^\]]*?\blink=([^\]|]+))?[^\]]*\]\]",
        _file_link_title,
        value,
        flags=re.I,
    )
    value = re.sub(r"\{\{([^{}]+)\}\}", _template_text, value)
    value = re.sub(r"\[\[[^\]|]+\|([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value).replace("×", "x")
    return " ".join(value.replace("'''", "").replace("''", "").split()).strip()


def _scalar(value: str):
    normalized = value.replace(",", "").strip()
    if _NUMBER.fullmatch(normalized):
        number = float(normalized)
        return int(number) if number.is_integer() else number
    return value.strip()


def _split_list(value: str) -> List[str]:
    return [part.strip() for part in re.split(r"[;,\n]+", value) if part.strip()]


def _loot(value: str) -> Dict[str, Any]:
    chance = None
    chance_match = re.search(r"(?<![\d.])(\d+(?:\.\d+)?%)(?!\d)", value)
    if chance_match:
        chance = chance_match.group(1)
        value = (value[: chance_match.start()] + value[chance_match.end() :]).strip()
    quantity = "1"
    quantity_match = re.search(
        r"\bx\s*(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)\b",
        value,
        re.I,
    )
    if quantity_match:
        quantity = re.sub(r"\s+", "", quantity_match.group(1))
        value = (value[: quantity_match.start()] + value[quantity_match.end() :]).strip()
    conditions = None
    condition_match = re.search(r"\(([^()]*)\)\s*$", value)
    if condition_match:
        conditions = condition_match.group(1).strip() or None
        value = value[: condition_match.start()].strip()
    return {
        "itemTitle": re.sub(r"^(?:or|and)\s+", "", value, flags=re.I).strip(" ,().") or "Unknown",
        "quantity": quantity,
        "chance": chance,
        "conditions": conditions,
        "method": "conditional" if conditions else "kill",
        "sourceVariant": None,
        "game": "DST",
    }


def _infobox_image(fields: Mapping[str, str]) -> Optional[str]:
    raw = fields.get("image")
    if not isinstance(raw, str) or not raw.strip():
        return None
    cleaned = re.sub(r"</?gallery[^>]*>", "", raw, flags=re.I)
    for line in cleaned.splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        candidate = candidate.split("|", 1)[0].strip().strip('"\'')
        if candidate:
            return candidate if candidate.startswith("File:") else "File:" + candidate
    return None


def _file_link_title(match: re.Match) -> str:
    linked = match.group(1)
    if isinstance(linked, str) and linked.strip():
        return linked.strip()
    filename = re.match(r"\[\[File:([^\]|]+)", match.group(0), re.I)
    if filename is None:
        return ""
    return re.sub(r"\.[A-Za-z0-9]+$", "", filename.group(1)).strip()


def _template_text(match: re.Match) -> str:
    parts = _split_top_level(match.group(1), "|")
    if not parts:
        return ""
    name = parts[0].strip().casefold()
    if not re.fullmatch(r"pic(?:24|32)?", name):
        return ""
    values = [part.strip() for part in parts[1:] if part.strip()]
    if name == "pic" and values and re.fullmatch(r"x?\d+", values[0], re.I):
        values = values[1:]
    positional = [value for value in values if "=" not in value]
    return positional[-1] if positional else ""


def _prefab_identity(page_id, title, wikitext, mappings):
    mapping = mappings.get(page_id, mappings.get(str(page_id)))
    if mapping is not None:
        if not isinstance(mapping, Mapping):
            raise ValueError("Mob prefab mapping must be an object")
        codes = mapping.get("prefabCodes")
        primary = mapping.get("primaryCode")
        if (
            not isinstance(codes, list)
            or not codes
            or not all(isinstance(code, str) and code.strip() for code in codes)
            or not isinstance(primary, str)
            or primary not in codes
        ):
            raise ValueError("Mob prefab mapping codes are invalid")
        normalized_codes = tuple(code.strip().casefold() for code in codes)
        ordered_codes = (primary.strip().casefold(),) + tuple(
            code for code in normalized_codes if code != primary.strip().casefold()
        )
        raw_variants = mapping.get("variants", [])
        if not isinstance(raw_variants, list):
            raise ValueError("Mob prefab mapping variants are invalid")
        labels = {
            value.get("code", "").casefold(): value.get("label")
            for value in raw_variants
            if isinstance(value, Mapping)
            and isinstance(value.get("code"), str)
            and isinstance(value.get("label"), str)
        }
    else:
        ordered_codes = _extract_category_spawn_codes(wikitext)
        labels = {}
    if not ordered_codes:
        raise ValueError("Mob page has no verified prefab code: {}".format(title))
    variants = [
        {
            "code": code,
            "label": labels.get(code, title if len(ordered_codes) == 1 else code),
            "order": index,
            "sprite": None,
        }
        for index, code in enumerate(ordered_codes)
    ]
    return ordered_codes, variants


def _extract_category_spawn_codes(wikitext: str) -> Tuple[str, ...]:
    values = []
    for raw_line in re.findall(
        r"\|\s*spawnCode\s*=\s*([^\n]+)", wikitext, re.IGNORECASE
    ):
        raw = re.split(r"\|\s*[A-Za-z][^=|]*=", raw_line, maxsplit=1)[0].strip()
        if raw.startswith("{{"):
            continue
        quoted = re.findall(r"['\"]([A-Za-z][A-Za-z0-9_]*)['\"]", raw)
        candidates = quoted or re.findall(r"^([A-Za-z][A-Za-z0-9_]*)", raw)
        for candidate in candidates:
            code = candidate.casefold()
            if _PREFAB_CODE.fullmatch(code):
                values.append(code)
    return tuple(dict.fromkeys(values))


def _summary(value: Any, fallback: str) -> str:
    if not isinstance(value, str) or not value.strip():
        return fallback
    normalized = " ".join(value.split())
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    dst_only = " ".join(
        sentence for sentence in sentences if not _NON_DST_MARKERS.search(sentence)
    ).strip()
    return (dst_only or fallback)[:600]


def _reviewed_summary(value: Any) -> Optional[ReviewedNote]:
    if isinstance(value, ReviewedNote):
        return value if value.reviewed else None
    if (
        isinstance(value, Mapping)
        and value.get("reviewed") is True
        and isinstance(value.get("source_sha256"), str)
        and isinstance(value.get("vi"), str)
        and value["vi"].strip()
    ):
        return ReviewedNote(value["source_sha256"], " ".join(value["vi"].split()), True)
    return None


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records = []
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, start=1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError("invalid JSONL at {}:{}".format(path, line_number)) from error
            if not isinstance(value, dict):
                raise ValueError("category JSONL row must be an object")
            records.append(value)
    return records


def _positive_int(value: Any, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError("{} must be a positive integer".format(name))
    return value


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("{} must be a non-empty string".format(name))
    return value.strip()
