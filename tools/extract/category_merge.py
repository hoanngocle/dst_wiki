"""Merge reviewed DST category records into the public item catalog by prefab code."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Set


JsonObject = Dict[str, Any]
_SECTIONS = (
    "stats",
    "effects",
    "combat",
    "movement",
    "traits",
    "loot",
    "spawnsFrom",
    "notes",
)
_VALID_ACTIONS = {
    "created",
    "merged",
    "kept",
    "flagged",
    "duplicate_hidden",
    "excluded",
}


@dataclass(frozen=True)
class CategoryMergeResult:
    items: List[JsonObject]
    audit: JsonObject


def merge_category_mobs(
    items: Sequence[Mapping[str, Any]],
    artifact: Mapping[str, Any],
    entities: Sequence[Mapping[str, Any]],
) -> CategoryMergeResult:
    """Merge canonical category pages into existing records without changing IDs."""

    category = artifact.get("category")
    pages = artifact.get("pages")
    discovery = artifact.get("discovery")
    if (
        artifact.get("schemaVersion") != 1
        or not isinstance(category, str)
        or not category
        or artifact.get("game") != "DST"
        or not isinstance(pages, list)
        or not isinstance(discovery, Mapping)
    ):
        raise ValueError("category Mob artifact is invalid")

    result = [deepcopy(dict(item)) for item in items if isinstance(item, Mapping)]
    by_id = {
        item.get("id"): item
        for item in result
        if isinstance(item.get("id"), str)
    }
    entity_by_id = {
        entity.get("key"): entity
        for entity in entities
        if isinstance(entity, Mapping) and isinstance(entity.get("key"), str)
    }
    code_owners: Dict[str, List[JsonObject]] = {}
    for item in result:
        for code in _item_codes(item):
            code_owners.setdefault(code, []).append(item)

    rows: List[JsonObject] = []
    hidden_ids: Set[str] = set()
    matched_ids: Set[str] = set()
    fetched_titles: List[str] = []

    for raw_page in sorted(pages, key=_page_sort_key):
        if not isinstance(raw_page, Mapping):
            raise ValueError("category Mob page must be an object")
        page = deepcopy(dict(raw_page))
        identity = page.get("identity")
        if not isinstance(identity, Mapping):
            raise ValueError("category Mob identity is missing")
        primary_code = _code(identity.get("primaryCode"))
        codes = _codes(identity.get("prefabCodes"))
        if primary_code not in codes:
            raise ValueError("category Mob primary code is not in prefab codes")
        title = identity.get("name")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("category Mob title is missing")
        fetched_titles.append(title.strip())

        candidates = _unique_items(
            owner for code in codes for owner in code_owners.get(code, [])
        )
        preferred_id = "base_game:" + primary_code
        canonical = next(
            (item for item in candidates if item.get("id") == preferred_id),
            None,
        )
        if canonical is None and candidates:
            canonical = sorted(candidates, key=_canonical_sort_key)[0]

        action = "merged"
        if canonical is None:
            canonical = _new_item(page, primary_code)
            result.append(canonical)
            by_id[canonical["id"]] = canonical
            for code in codes:
                code_owners.setdefault(code, []).append(canonical)
            action = "created"

        canonical_id = str(canonical["id"])
        page = _overlay_runtime_facts(page, entity_by_id.get(canonical_id))
        canonical["mob"] = page
        canonical["category"] = "mob"
        canonical["namespace"] = canonical.get("namespace") or "base_game"
        canonical["prefabId"] = canonical.get("prefabId") or primary_code
        canonical.setdefault("englishName", identity.get("englishName"))
        canonical.setdefault("description", page.get("summary"))
        canonical.setdefault("sprite", _page_sprite(page))
        matched_ids.add(canonical_id)

        flags = []
        if canonical.get("sprite") is None and _page_sprite(page) is None:
            flags.append("missing_visual")
        rows.append(
            _audit_row(canonical_id, action, page, codes, flags)
        )

        for duplicate in candidates:
            duplicate_id = duplicate.get("id")
            if duplicate is canonical or not isinstance(duplicate_id, str):
                continue
            hidden_ids.add(duplicate_id)
            matched_ids.add(duplicate_id)
            rows.append(
                _audit_row(
                    duplicate_id,
                    "duplicate_hidden",
                    page,
                    codes,
                    ["duplicate_code"],
                    canonical_id=canonical_id,
                )
            )

    for item in result:
        item_id = item.get("id")
        if (
            not isinstance(item_id, str)
            or item_id in matched_ids
            or item.get("category") not in {"mob", "boss"}
        ):
            continue
        flags = ["orphan_record"]
        if _is_empty_details(item.get("mob")):
            flags.insert(0, "empty_details")
        if item.get("sprite") is None:
            flags.append("missing_visual")
        rows.append(
            {
                "recordId": item_id,
                "action": "flagged",
                "pageId": None,
                "title": item.get("name"),
                "prefabCodes": sorted(_item_codes(item)),
                "canonicalId": item_id,
                "flags": sorted(set(flags)),
                "noteStatus": None,
            }
        )

    seeds = discovery.get("seeds")
    if not isinstance(seeds, list):
        raise ValueError("category discovery seeds must be an array")
    excluded_non_dst = []
    direct_pages = 0
    for seed in seeds:
        if not isinstance(seed, Mapping):
            continue
        namespace = seed.get("namespace", seed.get("ns"))
        if namespace == 0:
            direct_pages += 1
        reason = seed.get("reason", seed.get("exclusionReason"))
        title = seed.get("title")
        accepted = seed.get("accepted") is True
        if not accepted and isinstance(title, str):
            rows.append(
                {
                    "recordId": "category-source:" + str(seed.get("pageId", seed.get("page_id", title))),
                    "action": "excluded",
                    "pageId": seed.get("pageId", seed.get("page_id")),
                    "title": title,
                    "prefabCodes": [],
                    "canonicalId": None,
                    "flags": [],
                    "reason": reason,
                    "noteStatus": None,
                }
            )
        if (
            namespace == 0
            and isinstance(title, str)
            and isinstance(reason, str)
            and reason.startswith("non_dst:")
        ):
            excluded_non_dst.append({"title": title, "reason": reason})

    public_items = [item for item in result if item.get("id") not in hidden_ids]
    public_items.sort(key=lambda item: str(item.get("id", "")))
    rows.sort(key=lambda row: (str(row.get("recordId", "")), str(row.get("action", ""))))
    if any(row.get("action") not in _VALID_ACTIONS for row in rows):
        raise AssertionError("invalid category merge action")
    audit = {
        "schemaVersion": 1,
        "category": category,
        "game": "DST",
        "summary": {
            "directPages": direct_pages,
            "publishedPages": len(pages),
            "actions": {
                action: sum(row.get("action") == action for row in rows)
                for action in sorted(_VALID_ACTIONS)
            },
        },
        "excludedNonDst": sorted(
            excluded_non_dst, key=lambda value: (value["title"].casefold(), value["title"])
        ),
        "fetchedTitles": sorted(set(fetched_titles), key=lambda value: (value.casefold(), value)),
        "rows": rows,
    }
    return CategoryMergeResult(public_items, audit)


def _new_item(page: Mapping[str, Any], primary_code: str) -> JsonObject:
    identity = page["identity"]
    return {
        "id": "base_game:" + primary_code,
        "prefabId": primary_code,
        "namespace": "base_game",
        "category": "mob",
        "name": identity.get("name") or primary_code,
        "englishName": identity.get("englishName"),
        "description": page.get("summary"),
        "craftingNote": None,
        "sprite": _page_sprite(page),
        "recipe": None,
        "mob": None,
        "character": None,
        "structureDetails": None,
        "wiki": None,
        "details": None,
    }


def _overlay_runtime_facts(page: JsonObject, entity: Any) -> JsonObject:
    if not isinstance(entity, Mapping):
        return page
    raw_stats = entity.get("stats")
    if not isinstance(raw_stats, list):
        return page
    section_by_key = {
        value.get("key"): section_name
        for section_name in ("stats", "effects", "combat", "movement")
        for value in (
            page.get(section_name, {}).get("values", [])
            if isinstance(page.get(section_name), Mapping)
            else []
        )
        if isinstance(value, Mapping) and isinstance(value.get("key"), str)
    }
    for stat in raw_stats:
        if not isinstance(stat, Mapping) or not isinstance(stat.get("key"), str):
            continue
        key = stat["key"]
        section_name = section_by_key.get(key)
        if section_name is None:
            continue
        section = page[section_name]
        values = section["values"]
        for index, value in enumerate(values):
            if isinstance(value, Mapping) and value.get("key") == key:
                replacement = deepcopy(dict(value))
                replacement["value"] = stat.get("value")
                replacement["unit"] = stat.get("unit") if isinstance(stat.get("unit"), str) else None
                replacement["evidence"] = [{
                    "source": "runtime:normalized_catalog",
                    "recordId": entity.get("key"),
                    "locator": "stats:" + key,
                    "game": "DST",
                }]
                values[index] = replacement
    return page


def _audit_row(
    record_id: str,
    action: str,
    page: Mapping[str, Any],
    codes: Iterable[str],
    flags: Iterable[str],
    canonical_id: str = None,
) -> JsonObject:
    identity = page["identity"]
    notes = page.get("notes")
    note_status = None
    if isinstance(notes, Mapping):
        if notes.get("status") == "none":
            note_status = "none"
        elif notes.get("status") == "known":
            values = notes.get("values")
            note_status = (
                "reviewed"
                if isinstance(values, list)
                and values
                and all(isinstance(value, Mapping) and value.get("status") == "reviewed" for value in values)
                else "unreviewed"
            )
        else:
            note_status = "unreviewed"
    return {
        "recordId": record_id,
        "action": action,
        "pageId": identity.get("sourcePageId"),
        "title": identity.get("name"),
        "prefabCodes": sorted(set(codes)),
        "canonicalId": canonical_id or record_id,
        "flags": sorted(set(flags)),
        "noteStatus": note_status,
    }


def _page_sprite(page: Mapping[str, Any]) -> Any:
    visual = page.get("visual")
    if isinstance(visual, Mapping):
        asset = visual.get("asset")
        if isinstance(asset, Mapping) and isinstance(asset.get("publicPath"), str):
            return {
                "src": asset["publicPath"],
                "uv": {"u1": 0.0, "u2": 1.0, "v1": 0.0, "v2": 1.0},
            }
    return None


def _item_codes(item: Mapping[str, Any]) -> Set[str]:
    codes = set()
    prefab_id = item.get("prefabId")
    if isinstance(prefab_id, str) and prefab_id.strip():
        codes.add(_code(prefab_id))
    mob = item.get("mob")
    identity = mob.get("identity") if isinstance(mob, Mapping) else None
    if isinstance(identity, Mapping) and isinstance(identity.get("prefabCodes"), list):
        codes.update(_codes(identity["prefabCodes"]))
    return codes


def _codes(value: Any) -> Set[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("category Mob prefab codes are invalid")
    return {_code(code) for code in value}


def _code(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("category Mob prefab code is invalid")
    return value.strip().casefold()


def _unique_items(values: Iterable[JsonObject]) -> List[JsonObject]:
    result = []
    seen = set()
    for value in values:
        marker = id(value)
        if marker not in seen:
            seen.add(marker)
            result.append(value)
    return result


def _canonical_sort_key(item: Mapping[str, Any]):
    return (
        0 if item.get("namespace") == "base_game" else 1,
        0 if item.get("sprite") is not None else 1,
        0 if not _is_empty_details(item.get("mob")) else 1,
        str(item.get("id", "")),
    )


def _is_empty_details(value: Any) -> bool:
    return value is None or value == {} or (
        isinstance(value, Mapping)
        and not any(value.get(section) for section in _SECTIONS)
    )


def _page_sort_key(page: Any):
    if not isinstance(page, Mapping):
        return (0, "")
    identity = page.get("identity")
    if not isinstance(identity, Mapping):
        return (0, "")
    page_id = identity.get("sourcePageId")
    return (page_id if isinstance(page_id, int) else 0, str(identity.get("name", "")))
