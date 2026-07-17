"""Deterministically audit public effect and other catalog records."""

from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


JsonObject = Dict[str, Any]
IN_SCOPE_CATEGORIES = frozenset({"effect", "other"})


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def _details_signal(item: JsonObject) -> bool:
    details = item.get("details")
    if isinstance(details, dict):
        drop_by = details.get("dropBy")
        usage = details.get("usage")
        if isinstance(drop_by, dict) and _nonempty_list(drop_by.get("sources")):
            return True
        if isinstance(usage, dict) and (
            _nonempty_list(usage.get("recipes"))
            or _nonempty_list(usage.get("effects"))
        ):
            return True
    return any(
        isinstance(item.get(field), dict)
        for field in ("mob", "character", "structureDetails")
    )


def _signals(item: JsonObject, entity: JsonObject) -> JsonObject:
    meaningful_name = _text(item.get("name")) and item.get("name") != item.get(
        "prefabId"
    )
    return {
        "sprite": isinstance(item.get("sprite"), dict),
        "meaningfulText": bool(
            meaningful_name
            or _text(item.get("englishName"))
            or _text(item.get("description"))
            or _text(item.get("craftingNote"))
        ),
        "wiki": isinstance(item.get("wiki"), dict),
        "inventoryItem": entity.get("is_inventory_item") is True,
        "recipe": isinstance(item.get("recipe"), dict)
        or _nonempty_list(entity.get("recipes")),
        "acquisition": _nonempty_list(entity.get("acquisition")),
        "stats": _nonempty_list(entity.get("stats")),
        "effects": _nonempty_list(entity.get("effects")),
        "relations": _nonempty_list(entity.get("relations")),
        "details": _details_signal(item),
    }


def _reference_id(value: Any) -> Optional[str]:
    if not isinstance(value, dict):
        return None
    direct = value.get("id")
    if isinstance(direct, str):
        return direct
    item = value.get("item")
    return item.get("id") if isinstance(item, dict) and isinstance(item.get("id"), str) else None


def _build_reverse_references(
    items: Sequence[JsonObject],
    entities: Sequence[JsonObject],
    wiki_details: Any,
) -> Dict[str, List[JsonObject]]:
    collected: Dict[str, Set[Tuple[str, str]]] = {}

    def add(target: Any, source: Any, kind: str) -> None:
        if not isinstance(target, str) or not isinstance(source, str) or target == source:
            return
        collected.setdefault(target, set()).add((source, kind))

    for entity in entities:
        if not isinstance(entity, dict):
            continue
        source = entity.get("key")
        if not isinstance(source, str):
            continue
        for recipe in entity.get("recipes", []):
            if not isinstance(recipe, dict):
                continue
            for ingredient in recipe.get("ingredients", []):
                if isinstance(ingredient, dict):
                    add(ingredient.get("key"), source, "catalog_recipe_ingredient")
        for acquisition in entity.get("acquisition", []):
            if isinstance(acquisition, dict):
                add(acquisition.get("source"), source, "catalog_acquisition_source")
        for relation in entity.get("relations", []):
            if isinstance(relation, dict):
                add(relation.get("target"), source, "catalog_relation_target")

    for item in items:
        if not isinstance(item, dict):
            continue
        source = item.get("id")
        if not isinstance(source, str):
            continue
        recipe = item.get("recipe")
        if isinstance(recipe, dict):
            for ingredient in recipe.get("ingredients", []):
                add(_reference_id(ingredient), source, "item_recipe_ingredient")

        details = item.get("details")
        if isinstance(details, dict):
            drop_by = details.get("dropBy")
            if isinstance(drop_by, dict):
                for drop_source in drop_by.get("sources", []):
                    add(_reference_id(drop_source), source, "item_drop_source")
            usage = details.get("usage")
            if isinstance(usage, dict):
                for usage_recipe in usage.get("recipes", []):
                    if not isinstance(usage_recipe, dict):
                        continue
                    add(
                        _reference_id(usage_recipe.get("result")),
                        source,
                        "item_usage_result",
                    )
                    for ingredient in usage_recipe.get("ingredients", []):
                        add(
                            _reference_id(ingredient),
                            source,
                            "item_usage_ingredient",
                        )

        mob = item.get("mob")
        if isinstance(mob, dict):
            for loot in mob.get("loot", []):
                add(_reference_id(loot), source, "mob_loot")

        structure = item.get("structureDetails")
        if isinstance(structure, dict):
            construction = structure.get("construction")
            if isinstance(construction, dict):
                for ingredient in construction.get("ingredients", []):
                    add(
                        _reference_id(ingredient),
                        source,
                        "structure_construction_ingredient",
                    )
            craftables = structure.get("craftables")
            if isinstance(craftables, dict):
                for station_recipe in craftables.get("recipes", []):
                    if not isinstance(station_recipe, dict):
                        continue
                    add(
                        _reference_id(station_recipe.get("result")),
                        source,
                        "structure_craftable_result",
                    )
                    for ingredient in station_recipe.get("ingredients", []):
                        add(
                            _reference_id(ingredient),
                            source,
                            "structure_craftable_ingredient",
                        )
            destruction = structure.get("destruction")
            if isinstance(destruction, dict):
                for drop in destruction.get("drops", []):
                    add(
                        _reference_id(drop),
                        source,
                        "structure_destruction_drop",
                    )

    def collect_wiki_entity_ids(value: Any, source: str) -> None:
        if isinstance(value, dict):
            entity_id = value.get("entityId")
            if isinstance(entity_id, str):
                add(entity_id, source, "wiki_entity_reference")
            for nested in value.values():
                collect_wiki_entity_ids(nested, source)
        elif isinstance(value, list):
            for nested in value:
                collect_wiki_entity_ids(nested, source)

    if isinstance(wiki_details, dict):
        wiki_entries = sorted(wiki_details.items(), key=lambda entry: str(entry[0]))
    elif isinstance(wiki_details, (list, tuple)):
        wiki_entries = sorted(
            (
                (
                    detail.get("pageId", index)
                    if isinstance(detail, dict)
                    else index,
                    detail,
                )
                for index, detail in enumerate(wiki_details)
            ),
            key=lambda entry: str(entry[0]),
        )
    else:
        wiki_entries = []
    for page_id, detail in wiki_entries:
        collect_wiki_entity_ids(detail, f"wiki:{page_id}")

    return {
        target: [
            {"source": source, "kind": kind}
            for source, kind in sorted(references)
        ]
        for target, references in sorted(collected.items())
    }


def _row(
    item: JsonObject,
    action: str,
    reason_code: str,
    signals: JsonObject,
    references: List[JsonObject],
) -> JsonObject:
    reasons = {
        "positive_signal": "Giữ lại vì record có dữ liệu hiển thị hoặc gameplay.",
        "reverse_reference": "Giữ lại vì record được dữ liệu khác tham chiếu.",
        "empty_unreferenced": "Loại vì record không có ảnh, text, công dụng hoặc liên kết.",
    }
    return {
        "id": item["id"],
        "namespace": item["namespace"],
        "prefabId": item["prefabId"],
        "category": item["category"],
        "name": item["name"],
        "action": action,
        "reasonCode": reason_code,
        "reason": reasons[reason_code],
        "signals": signals,
        "references": references,
    }


def audit_effect_other_items(
    items: Sequence[JsonObject],
    entities: Sequence[JsonObject],
    wiki_details: Optional[Any] = None,
) -> Tuple[List[JsonObject], Set[str]]:
    """Return stable audit rows and IDs proven empty and unreferenced."""

    entities_by_id = {
        entity["key"]: entity
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    references = _build_reverse_references(items, entities, wiki_details or {})
    rows: List[JsonObject] = []
    excluded: Set[str] = set()
    for item in sorted(
        (
            value
            for value in items
            if isinstance(value, dict)
            and value.get("category") in IN_SCOPE_CATEGORIES
        ),
        key=lambda value: str(value.get("id") or ""),
    ):
        signals = _signals(item, entities_by_id.get(item.get("id"), {}))
        item_references = references.get(item.get("id"), [])
        if any(signals.values()):
            action, reason_code = "keep", "positive_signal"
        elif item_references:
            action, reason_code = "keep", "reverse_reference"
        else:
            action, reason_code = "exclude", "empty_unreferenced"
            excluded.add(item["id"])
        rows.append(_row(item, action, reason_code, signals, item_references))
    return rows, excluded
