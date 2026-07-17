"""Normalize selected structured sections from imported MediaWiki wikitext."""

import html
import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.parse import quote

from tools.extract.wiki_mapping import normalize_identity


JsonObject = Dict[str, Any]
WIKI_PAGE_BASE = "https://dontstarve.wiki.gg/wiki/"
WIKI_FILE_REDIRECT_BASE = WIKI_PAGE_BASE + "Special:Redirect/file/"


def _split_top_level(value: str, separator: str = "|") -> List[str]:
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
        if value[index] == separator and template_depth == 0 and link_depth == 0:
            parts.append(value[start:index])
            start = index + 1
        index += 1
    parts.append(value[start:])
    return parts


def _balanced_templates(value: str) -> Iterable[Tuple[int, int, str]]:
    depth = 0
    start: Optional[int] = None
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
                yield start, index, value[start + 2 : index - 2]
                start = None
            continue
        index += 1


def _template_parts(content: str) -> List[str]:
    return [part.strip() for part in _split_top_level(content)]


def _pic_values(content: str) -> Optional[Tuple[str, str]]:
    parts = _template_parts(content)
    if not parts or not re.fullmatch(r"pic(?:\d+)?", parts[0], re.IGNORECASE):
        return None
    positional = [part for part in parts[1:] if "=" not in part]
    if positional and re.fullmatch(r"\d+(?:px)?", positional[0], re.IGNORECASE):
        positional = positional[1:]
    if not positional:
        return None
    target = positional[0].strip()
    label = positional[1].strip() if len(positional) > 1 else target
    return target, label or target


def _replace_templates(value: str) -> str:
    rendered: List[str] = []
    cursor = 0
    for start, end, content in _balanced_templates(value):
        rendered.append(value[cursor:start])
        pic = _pic_values(content)
        if pic is not None:
            rendered.append(" " + pic[1] + " ")
        else:
            parts = _template_parts(content)
            rendered.append(" " + (parts[0] if parts else "") + " ")
        cursor = end
    rendered.append(value[cursor:])
    return "".join(rendered)


def _replace_wiki_link(match: re.Match) -> str:
    parts = match.group(1).split("|")
    target = parts[0].strip()
    if re.match(r"^(?:File|Image):", target, re.IGNORECASE):
        return " "
    label = parts[-1].strip() if len(parts) > 1 else target
    return " " + (label or target) + " "


def _plain_text(value: str) -> str:
    value = _replace_templates(value)
    value = re.sub(r"\[\[([^\]]+)\]\]", _replace_wiki_link, value)
    value = re.sub(r"\[(?:https?://\S+)(?:\s+([^\]]+))?\]", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("'''", "").replace("''", "")
    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\(\s+", "(", value)
    return re.sub(r"\s+\)", ")", value)


def _heading_sections(wikitext: str) -> Iterable[Tuple[int, int, int, str]]:
    pattern = re.compile(r"^(={2,6})\s*(.*?)\s*\1\s*$", re.MULTILINE)
    matches = list(pattern.finditer(wikitext))
    for index, match in enumerate(matches):
        level = len(match.group(1))
        end = len(wikitext)
        for following in matches[index + 1 :]:
            if len(following.group(1)) <= level:
                end = following.start()
                break
        yield match.end(), end, level, _plain_text(match.group(2))


def _required_section(wikitext: str, requested_title: str) -> str:
    section = _optional_section(wikitext, requested_title)
    if section is not None:
        return section
    raise ValueError(f"{requested_title} section is required")


def _optional_section(wikitext: str, requested_title: str) -> Optional[str]:
    requested = normalize_identity(requested_title)
    for start, end, _level, title in _heading_sections(wikitext):
        normalized = normalize_identity(title)
        if normalized == requested or normalized.endswith(" " + requested):
            return wikitext[start:end]
    return None


def _wiki_url(target: str) -> str:
    slug = target.strip().replace(" ", "_")
    return WIKI_PAGE_BASE + quote(slug, safe="/")


def _wiki_file_url(target: str) -> str:
    filename = target.strip()
    if not re.search(r"\.(?:gif|jpe?g|png|webp)$", filename, re.IGNORECASE):
        filename += ".png"
    return WIKI_FILE_REDIRECT_BASE + quote(filename.replace(" ", "_"), safe="")


def _reference(
    title: str,
    target: str,
    entity_ids_by_title: Mapping[str, str],
    icon_target: Optional[str] = None,
) -> JsonObject:
    entity_id = entity_ids_by_title.get(normalize_identity(target))
    if entity_id is None:
        entity_id = entity_ids_by_title.get(normalize_identity(title))
    return {
        "title": title.strip(),
        "url": _wiki_url(target),
        "entityId": entity_id,
        "iconUrl": _wiki_file_url(icon_target) if icon_target else None,
    }


def _table_cells(row: str) -> List[str]:
    cells: List[str] = []
    current: Optional[List[str]] = None
    for line in row.splitlines():
        if line.startswith("|") and not line.startswith("|}"):
            values = line[1:].split("||")
            for value in values:
                if current is not None:
                    cells.append("\n".join(current).strip())
                current = [value]
        elif current is not None:
            current.append(line)
    if current is not None:
        cells.append("\n".join(current).strip())
    return cells


def _source_references(
    source_cell: str,
    entity_ids_by_title: Mapping[str, str],
) -> Tuple[List[JsonObject], Optional[str]]:
    sources: List[JsonObject] = []
    seen = set()
    for line in source_cell.splitlines():
        candidate = line.split("+", 1)[0]
        found_pic = False
        for _start, _end, content in _balanced_templates(candidate):
            pic = _pic_values(content)
            if pic is None:
                continue
            found_pic = True
            target, label = pic
            identity = normalize_identity(label)
            if identity and identity not in seen:
                sources.append(
                    _reference(
                        label,
                        target,
                        entity_ids_by_title,
                        icon_target=target,
                    )
                )
                seen.add(identity)
        if found_pic:
            continue
        for match in re.finditer(r"\[\[([^\]]+)\]\]", candidate):
            parts = match.group(1).split("|")
            target = parts[0].strip()
            if re.match(r"^(?:File|Image):", target, re.IGNORECASE):
                continue
            label = parts[-1].strip() if len(parts) > 1 else target
            identity = normalize_identity(label or target)
            if identity and identity not in seen:
                sources.append(_reference(label or target, target, entity_ids_by_title))
                seen.add(identity)

    context = _plain_text(source_cell)
    for source in sorted(sources, key=lambda value: len(value["title"]), reverse=True):
        context = re.sub(re.escape(source["title"]), " ", context, flags=re.IGNORECASE)
    context = re.sub(r"\s+", " ", context).strip(" +")
    return sources, context or None


def _parse_drop_rows(
    section: str,
    entity_ids_by_title: Mapping[str, str],
) -> List[JsonObject]:
    table_start = section.find("{|")
    table_end = section.find("|}", table_start + 2)
    if table_start < 0 or table_end < 0:
        raise ValueError("Drop table section does not contain a complete Wiki table")
    table = section[table_start + 2 : table_end]
    rows: List[JsonObject] = []
    for raw_row in re.split(r"(?m)^\|-\s*$", table)[1:]:
        cells = _table_cells(raw_row)
        if len(cells) != 3:
            continue
        sources, context = _source_references(cells[0], entity_ids_by_title)
        if not sources:
            continue
        rows.append(
            {
                "sources": sources,
                "quantity": _plain_text(cells[1]),
                "chance": _plain_text(cells[2]),
                "context": context,
            }
        )
    return rows


def _recipe_parameters(content: str) -> Dict[str, str]:
    parts = _template_parts(content)
    parameters: Dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        parameters[key.strip().casefold()] = value.strip()
    return parameters


def _positive_number(value: Optional[str], default: int = 1) -> Any:
    if value is None or not value.strip():
        return default
    cleaned = _plain_text(value)
    try:
        number = float(cleaned)
    except ValueError as error:
        raise ValueError(f"Usage count must be numeric: {cleaned}") from error
    if number <= 0:
        raise ValueError(f"Usage count must be positive: {cleaned}")
    return int(number) if number.is_integer() else number


def _optional_text(parameters: Mapping[str, str], key: str) -> Optional[str]:
    value = _plain_text(parameters.get(key, ""))
    return value or None


def _parse_usage_recipes(
    section: str,
    subject_title: str,
    entity_ids_by_title: Mapping[str, str],
    strict: bool = True,
) -> List[JsonObject]:
    recipes: List[JsonObject] = []
    subject_identity = normalize_identity(subject_title)
    for _start, _end, content in _balanced_templates(section):
        parts = _template_parts(content)
        if not parts or parts[0].casefold() != "recipe":
            continue
        parameters = _recipe_parameters(content)
        result_title = _plain_text(parameters.get("result", ""))
        if not result_title:
            if strict:
                raise ValueError("Usage Recipe is missing a result")
            continue
        nightmare_amount: Optional[Any] = None
        ingredients: List[JsonObject] = []
        for index in range(1, 4):
            item_title = _plain_text(parameters.get(f"item{index}", ""))
            if not item_title:
                continue
            try:
                amount = _positive_number(parameters.get(f"count{index}"))
            except ValueError:
                if strict:
                    raise
                ingredients = []
                nightmare_amount = None
                break
            if normalize_identity(item_title) == subject_identity:
                nightmare_amount = amount
            else:
                ingredients.append(
                    {
                        "item": _reference(item_title, item_title, entity_ids_by_title),
                        "amount": amount,
                    }
                )
        if nightmare_amount is None:
            if strict:
                raise ValueError(f"Usage Recipe for {result_title} omits {subject_title}")
            continue
        try:
            result_amount = _positive_number(parameters.get("resultcount"))
        except ValueError:
            if strict:
                raise
            continue
        recipes.append(
            {
                "result": _reference(result_title, result_title, entity_ids_by_title),
                "resultAmount": result_amount,
                "subjectAmount": nightmare_amount,
                "ingredients": ingredients,
                "station": _optional_text(parameters, "tool"),
                "dlc": _optional_text(parameters, "dlc"),
                "character": _optional_text(parameters, "character"),
                "note": _optional_text(parameters, "note"),
            }
        )
    return recipes


def _infobox_parameter(wikitext: str, key: str) -> Optional[str]:
    match = re.search(
        rf"(?ims)^\|\s*{re.escape(key)}\s*=\s*(.*?)"
        r"(?=^\|\s*[A-Za-z][A-Za-z0-9_ ]*\s*=|^}})",
        wikitext,
    )
    if match is None:
        return None
    value = match.group(1).strip()
    return value or None


def _is_drop_context_reference(reference: Mapping[str, Any]) -> bool:
    identity = normalize_identity(str(reference.get("title", "")))
    return (
        identity.endswith(" icon")
        or identity in {"dst", "sw", "ham", "rog", "shipwrecked", "hamlet"}
    )


def _parse_dropped_by(
    value: str,
    entity_ids_by_title: Mapping[str, str],
) -> List[JsonObject]:
    rows: List[JsonObject] = []
    value = re.sub(r"<hr\b[^>]*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    for raw_line in value.splitlines():
        raw_line = raw_line.strip(" ,")
        if not raw_line:
            continue
        decoded = html.unescape(raw_line)
        source_segment = re.split(
            r"(?:×\s*\d|(?<!\w)[xX]\s*\d|\d+(?:\.\d+)?\s*%)",
            decoded,
            maxsplit=1,
        )[0]
        source_segment = re.sub(r"\([^)]*\)", " ", source_segment)
        sources, _unused_context = _source_references(
            source_segment, entity_ids_by_title
        )
        sources = [
            source for source in sources if not _is_drop_context_reference(source)
        ]
        if not sources:
            continue

        plain = _plain_text(decoded)
        quantity_match = re.search(
            r"(?:×|(?<!\w)[xX])\s*(\d+(?:\.\d+)?(?:\s*-\s*\d+(?:\.\d+)?)?)",
            plain,
        )
        chance_match = re.search(r"\b\d+(?:\.\d+)?\s*%", plain)
        quantity = (
            re.sub(r"\s+", "", quantity_match.group(1))
            if quantity_match is not None
            else "1"
        )
        chance = (
            re.sub(r"\s+", "", chance_match.group(0))
            if chance_match is not None
            else "—"
        )
        context = plain
        for source in sorted(sources, key=lambda item: len(item["title"]), reverse=True):
            context = re.sub(
                re.escape(source["title"]), " ", context, flags=re.IGNORECASE
            )
        if quantity_match is not None:
            context = context.replace(quantity_match.group(0), " ")
        if chance_match is not None:
            context = context.replace(chance_match.group(0), " ")
        context = re.sub(r"\s+", " ", context).strip(" ,:+-")
        rows.append(
            {
                "sources": sources,
                "quantity": quantity,
                "chance": chance,
                "context": context or None,
            }
        )
    return rows


def normalize_available_sections(
    wikitext: str,
    subject_title: str,
    entity_ids_by_title: Mapping[str, str],
) -> Optional[JsonObject]:
    """Normalize every supported Drop/Usage section without requiring both."""

    drop_rows: List[JsonObject] = []
    drop_section = _optional_section(wikitext, "Drop table")
    if drop_section is not None:
        try:
            drop_rows = _parse_drop_rows(drop_section, entity_ids_by_title)
        except ValueError:
            drop_rows = []
    if not drop_rows:
        dropped_by = _infobox_parameter(wikitext, "droppedBy")
        if dropped_by is not None:
            drop_rows = _parse_dropped_by(dropped_by, entity_ids_by_title)

    usage_recipes: List[JsonObject] = []
    usage_section = _optional_section(wikitext, "Usage")
    if usage_section is not None:
        usage_recipes = _parse_usage_recipes(
            usage_section,
            subject_title,
            entity_ids_by_title,
            strict=False,
        )

    if not drop_rows and not usage_recipes:
        return None
    return {
        "subject": _reference(subject_title, subject_title, entity_ids_by_title),
        "dropTable": {"rows": drop_rows},
        "usage": {"recipes": usage_recipes},
    }


def normalize_drop_and_usage_sections(
    wikitext: str,
    subject_title: str,
    entity_ids_by_title: Mapping[str, str],
) -> JsonObject:
    """Return structured Drop table and Usage data from one Wiki revision."""

    drop_rows = _parse_drop_rows(
        _required_section(wikitext, "Drop table"), entity_ids_by_title
    )
    usage_recipes = _parse_usage_recipes(
        _required_section(wikitext, "Usage"), subject_title, entity_ids_by_title
    )
    if not drop_rows:
        raise ValueError("Drop table section contains no data rows")
    if not usage_recipes:
        raise ValueError("Usage section contains no Recipe templates")
    return {
        "subject": _reference(subject_title, subject_title, entity_ids_by_title),
        "dropTable": {"rows": drop_rows},
        "usage": {"recipes": usage_recipes},
    }


def strip_available_sections_html(
    value: str,
    *,
    drop_table: bool,
    usage: bool,
) -> str:
    """Remove normalized Wiki sections while preserving all other article HTML."""

    section_ids = []
    if drop_table:
        section_ids.append("Drop_table")
    if usage:
        section_ids.append("Usage")
    for section_id in section_ids:
        heading = re.search(
            rf'<h([2-6])\b[^>]*>(?:(?!</h\1>).)*id="{section_id}"'
            rf"(?:(?!</h\1>).)*</h\1>",
            value,
            re.IGNORECASE | re.DOTALL,
        )
        if heading is None:
            continue
        level = int(heading.group(1))
        following = value[heading.end() :]
        next_heading = re.search(
            rf"<h[2-{level}](?:\s|>)", following, re.IGNORECASE
        )
        end = len(value) if next_heading is None else heading.end() + next_heading.start()
        value = value[: heading.start()] + value[end:]
    return value


def strip_drop_and_usage_html(value: str) -> str:
    """Remove contiguous normalized sections from sanitized Wiki HTML."""

    drop_heading = re.search(
        r'<h3\b[^>]*>(?:(?!</h3>).)*id="Drop_table"(?:(?!</h3>).)*</h3>',
        value,
        re.IGNORECASE | re.DOTALL,
    )
    usage_heading = re.search(
        r'<h2\b[^>]*>(?:(?!</h2>).)*id="Usage"(?:(?!</h2>).)*</h2>',
        value,
        re.IGNORECASE | re.DOTALL,
    )
    if (
        drop_heading is None
        or usage_heading is None
        or usage_heading.start() <= drop_heading.start()
    ):
        raise ValueError("Drop table and Usage HTML headings are required")
    next_heading = re.search(r"<h2(?:\s|>)", value[usage_heading.end() :], re.IGNORECASE)
    if next_heading is None:
        raise ValueError("Usage HTML section must have a following level-2 heading")
    end = usage_heading.end() + next_heading.start()
    return value[: drop_heading.start()] + value[end:]
