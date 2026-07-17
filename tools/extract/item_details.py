"""Derive deterministic Tu Tiên recipe, usage, and acquisition details."""

import json
from typing import Any, Dict, List, Optional, Tuple


JsonObject = Dict[str, Any]
DETAIL_STATUSES = {"known", "none", "unknown"}
DROP_TYPES = {"drop", "harvest", "start", "trade", "other"}
DERIVED_EVIDENCE_SOURCE = "public/data/catalog.json"


def _number(value: Any) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else format(number, "g")


def _entity_name(entity: Optional[JsonObject], fallback: str) -> str:
    if entity:
        names = entity.get("name")
        if isinstance(names, dict):
            for language in ("vi", "en"):
                value = names.get(language)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return fallback.split(":")[-1]


def _reference(
    entity_id: str,
    entities: Dict[str, JsonObject],
    items: Dict[str, JsonObject],
) -> JsonObject:
    item = items.get(entity_id)
    if item:
        return {
            "id": entity_id,
            "name": str(item.get("name") or entity_id.split(":")[-1]),
            "sprite": item.get("sprite"),
        }
    return {
        "id": entity_id,
        "name": _entity_name(entities.get(entity_id), entity_id),
        "sprite": None,
    }


def _evidence(entity_id: str, group: str) -> List[JsonObject]:
    return [
        {
            "source": DERIVED_EVIDENCE_SOURCE,
            "locator": f"{entity_id}:{group}",
        }
    ]


def _ingredient(
    raw: JsonObject,
    entities: Dict[str, JsonObject],
    items: Dict[str, JsonObject],
) -> JsonObject:
    entity_id = str(raw["key"])
    reference = _reference(entity_id, entities, items)
    return {
        "id": reference["id"],
        "name": reference["name"],
        "amount": raw["amount"],
        "sprite": reference["sprite"],
    }


def _crafting_note(entity: JsonObject, item: Optional[JsonObject]) -> Optional[str]:
    if item and isinstance(item.get("craftingNote"), str):
        return item["craftingNote"]
    recipes = entity.get("recipes")
    if not isinstance(recipes, list) or not recipes:
        return None
    recipe = recipes[0]
    restrictions = recipe.get("restrictions") if isinstance(recipe, dict) else None
    if not isinstance(restrictions, dict):
        return None
    labels = []
    builder_tags = restrictions.get("builder_tags")
    if isinstance(builder_tags, list) and builder_tags:
        labels.append("người chế tạo " + ", ".join(sorted(map(str, builder_tags))))
    filters = restrictions.get("filters")
    if isinstance(filters, list) and filters:
        labels.append("bộ lọc " + ", ".join(sorted(map(str, filters))))
    return "Yêu cầu " + "; ".join(labels) + "." if labels else None


def _reverse_recipes(
    entities: Dict[str, JsonObject],
    items: Dict[str, JsonObject],
) -> Dict[str, List[JsonObject]]:
    result: Dict[str, List[JsonObject]] = {}
    for result_id in sorted(entities):
        entity = entities[result_id]
        recipes = entity.get("recipes")
        if not isinstance(recipes, list):
            continue
        for recipe in recipes:
            if not isinstance(recipe, dict) or not isinstance(recipe.get("ingredients"), list):
                continue
            ingredients = sorted(
                (value for value in recipe["ingredients"] if isinstance(value, dict)),
                key=lambda value: (int(value.get("position", 0)), str(value.get("key") or "")),
            )
            for subject in ingredients:
                subject_id = str(subject.get("key") or "")
                if not subject_id:
                    continue
                other_ingredients = [
                    _ingredient(value, entities, items)
                    for value in ingredients
                    if str(value.get("key") or "") != subject_id
                    and float(value.get("amount", 0)) > 0
                ]
                result.setdefault(subject_id, []).append(
                    {
                        "result": _reference(result_id, entities, items),
                        "resultAmount": recipe.get("output_count", 1),
                        "subjectAmount": subject.get("amount"),
                        "ingredients": other_ingredients,
                        "craftingNote": _crafting_note(entity, items.get(result_id)),
                    }
                )
    for recipes in result.values():
        recipes.sort(key=lambda value: value["result"]["id"])
    return result


def _signed_effect(value: Any, positive: str, negative: str, label: str) -> str:
    number = float(value)
    verb = positive if number >= 0 else negative
    return f"{verb} {_number(abs(number))} {label}"


def _usage_effects(
    entity_id: str,
    entity: JsonObject,
    entities: Dict[str, JsonObject],
    items: Dict[str, JsonObject],
) -> Tuple[List[JsonObject], List[JsonObject]]:
    stats = {
        str(value.get("key")): value.get("value")
        for value in entity.get("stats", [])
        if isinstance(value, dict) and isinstance(value.get("key"), str)
    }
    effects: List[JsonObject] = []
    supported = set()

    edible_keys = [key for key in ("health", "hunger", "sanity") if key in stats]
    if edible_keys:
        labels = {
            "health": ("hồi", "giảm", "Máu"),
            "hunger": ("hồi", "giảm", "Đói"),
            "sanity": ("hồi", "giảm", "Tinh thần"),
        }
        parts = [_signed_effect(stats[key], *labels[key]) for key in edible_keys]
        effects.append(
            {
                "trigger": "eat",
                "text": "Khi ăn: " + ", ".join(parts[:-1]) + (" và " if len(parts) > 1 else "") + parts[-1] + ".",
                "evidence": _evidence(entity_id, "stats"),
            }
        )
        supported.update(edible_keys)

    weapon_keys = [key for key in ("damage", "attack_range", "uses") if key in stats]
    if weapon_keys:
        parts = []
        if "damage" in stats:
            parts.append(f"gây {_number(stats['damage'])} sát thương")
        if "attack_range" in stats:
            parts.append(f"tầm đánh {_number(stats['attack_range'])} ô")
        if "uses" in stats:
            parts.append(f"độ bền {_number(stats['uses'])} lần dùng")
        effects.append(
            {
                "trigger": "equip",
                "text": "Khi dùng làm vũ khí: " + ", ".join(parts) + ".",
                "evidence": _evidence(entity_id, "stats"),
            }
        )
        supported.update(weapon_keys)

    armor_keys = [key for key in ("damage_absorption", "armor_durability") if key in stats]
    if armor_keys:
        parts = []
        if "damage_absorption" in stats:
            parts.append(f"hấp thụ {_number(float(stats['damage_absorption']) * 100)}% sát thương")
        if "armor_durability" in stats:
            parts.append(f"độ bền {_number(stats['armor_durability'])}")
        effects.append(
            {
                "trigger": "equip",
                "text": "Khi trang bị: " + ", ".join(parts) + ".",
                "evidence": _evidence(entity_id, "stats"),
            }
        )
        supported.update(armor_keys)

    if "container_slots" in stats:
        effects.append(
            {
                "trigger": "open",
                "text": f"Dùng làm vật chứa với {_number(stats['container_slots'])} ô đồ.",
                "evidence": _evidence(entity_id, "stats"),
            }
        )
        supported.add("container_slots")

    charge_keys = [
        key for key in ("current_charge", "charge_capacity", "recharge_time") if key in stats
    ]
    if charge_keys:
        parts = []
        current = stats.get("current_charge")
        capacity = stats.get("charge_capacity")
        if current is not None and capacity is not None:
            parts.append(f"{_number(current)}/{_number(capacity)} điểm năng lượng")
        elif capacity is not None:
            parts.append(f"tối đa {_number(capacity)} điểm năng lượng")
        if "recharge_time" in stats:
            parts.append(f"hồi đầy trong {_number(stats['recharge_time'])} giây")
        effects.append(
            {
                "trigger": "activate",
                "text": "Khi kích hoạt: " + ", ".join(parts) + ".",
                "evidence": _evidence(entity_id, "stats"),
            }
        )
        supported.update(charge_keys)

    for relation in entity.get("relations", []):
        if not isinstance(relation, dict) or relation.get("type") != "transforms_to":
            continue
        target_id = relation.get("target")
        if not isinstance(target_id, str) or not target_id:
            continue
        target = _reference(target_id, entities, items)
        effects.append(
            {
                "trigger": "lifecycle",
                "text": f"Theo thời gian biến thành {target['name']}.",
                "evidence": _evidence(entity_id, "relations"),
            }
        )

    unsupported = [
        {"id": entity_id, "kind": "stat", "key": key, "value": stats[key]}
        for key in sorted(stats)
        if key not in supported
    ]
    unsupported.extend(
        {
            "id": entity_id,
            "kind": "effect",
            "trigger": value.get("trigger"),
            "key": value.get("key"),
        }
        for value in entity.get("effects", [])
        if isinstance(value, dict)
    )
    effects.sort(key=lambda value: (value["trigger"], value["text"]))
    return effects, unsupported


def _quantity(acquisition: JsonObject) -> Optional[str]:
    minimum = acquisition.get("min_count")
    maximum = acquisition.get("max_count")
    if minimum is None and maximum is None:
        return None
    if minimum is None:
        minimum = maximum
    if maximum is None:
        maximum = minimum
    if float(minimum) == float(maximum):
        return _number(minimum)
    return f"{_number(minimum)}–{_number(maximum)}"


def _chance(value: Any) -> Optional[str]:
    if value is None:
        return None
    return f"{_number(float(value) * 100)}%"


def _conditions(value: Any) -> Optional[str]:
    if not isinstance(value, dict) or not value:
        return None
    parts = []
    if "regrowth_seconds" in value:
        parts.append(f"Hồi lại sau {_number(value['regrowth_seconds'])} giây")
    registry_paths = value.get("registry_paths")
    if isinstance(registry_paths, list) and registry_paths:
        owners = sorted(
            {
                str(path).split(".")[2]
                for path in registry_paths
                if len(str(path).split(".")) >= 3
            }
        )
        if owners:
            parts.append("Vật phẩm khởi đầu của " + ", ".join(owners))
    known = {"regrowth_seconds", "registry_paths", "loot_table"}
    remaining = {key: value[key] for key in sorted(value) if key not in known}
    if remaining:
        parts.append(json.dumps(remaining, ensure_ascii=False, sort_keys=True))
    return "; ".join(parts) if parts else None


def _drop_sources(
    entity_id: str,
    entity: JsonObject,
    entities: Dict[str, JsonObject],
    items: Dict[str, JsonObject],
) -> List[JsonObject]:
    rows = []
    for acquisition in entity.get("acquisition", []):
        if not isinstance(acquisition, dict) or acquisition.get("type") == "craft":
            continue
        source_type = str(acquisition.get("type") or "other")
        if source_type not in DROP_TYPES:
            source_type = "other"
        source_id = acquisition.get("source")
        rows.append(
            {
                "type": source_type,
                "source": (
                    _reference(source_id, entities, items)
                    if isinstance(source_id, str) and source_id
                    else None
                ),
                "quantity": _quantity(acquisition),
                "chance": _chance(acquisition.get("chance")),
                "conditions": _conditions(acquisition.get("conditions")),
                "evidence": _evidence(entity_id, "acquisition"),
            }
        )
    rows.sort(
        key=lambda value: (
            value["type"],
            (value["source"] or {}).get("id", ""),
            value["quantity"] or "",
            value["chance"] or "",
            value["conditions"] or "",
        )
    )
    return rows


def _validate_evidence(records: List[JsonObject], field: str) -> None:
    for record in records:
        evidence = record.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ValueError(f"{field} must contain evidence")
        for entry in evidence:
            source = entry.get("source") if isinstance(entry, dict) else None
            if not isinstance(source, str) or not source.startswith("mod/3721846643/"):
                raise ValueError(f"{field} evidence source must be inside mod/3721846643")


def _validate_override_section(section: Any, field: str) -> JsonObject:
    if not isinstance(section, dict) or section.get("replace") is not True:
        raise ValueError(f"{field} override must explicitly replace the section")
    status = section.get("status")
    if status not in DETAIL_STATUSES:
        raise ValueError(f"{field} status is invalid")
    records = []
    if field == "usage":
        recipes = section.get("recipes")
        effects = section.get("effects")
        if not isinstance(recipes, list) or not isinstance(effects, list):
            raise ValueError("usage override must contain recipe and effect arrays")
        records = recipes + effects
        _validate_evidence(effects, field)
    else:
        sources = section.get("sources")
        if not isinstance(sources, list):
            raise ValueError("dropBy override must contain sources")
        records = sources
        if any(
            not isinstance(source, dict) or source.get("type") not in DROP_TYPES
            for source in sources
        ):
            raise ValueError("drop source type is invalid")
        _validate_evidence(sources, field)
    if status == "known" and not records:
        raise ValueError(f"known {field} override must contain data")
    if status != "known" and records:
        raise ValueError(f"{field} {status} override cannot contain data")
    semantic_records = [
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for record in records
    ]
    if len(semantic_records) != len(set(semantic_records)):
        raise ValueError(f"duplicate {field} record")
    result = dict(section)
    result.pop("replace", None)
    return result


def _apply_overrides(
    details: Dict[str, JsonObject], overrides: Optional[JsonObject]
) -> List[str]:
    if overrides is None:
        return []
    if not isinstance(overrides, dict) or overrides.get("schema_version") != 1:
        raise ValueError("item detail overrides must use schema version 1")
    override_items = overrides.get("items")
    if not isinstance(override_items, dict):
        raise ValueError("item detail overrides must contain an items object")
    for entity_id in sorted(override_items):
        if entity_id not in details:
            raise ValueError(f"unknown override entity {entity_id}")
        override = override_items[entity_id]
        if not isinstance(override, dict):
            raise ValueError(f"override for {entity_id} must be an object")
        if "recipeStatus" in override:
            status = override["recipeStatus"]
            if status not in DETAIL_STATUSES:
                raise ValueError(f"recipeStatus override for {entity_id} is invalid")
            details[entity_id]["recipeStatus"] = status
        if "usage" in override:
            details[entity_id]["usage"] = _validate_override_section(
                override["usage"], "usage"
            )
        if "dropBy" in override:
            details[entity_id]["dropBy"] = _validate_override_section(
                override["dropBy"], "dropBy"
            )
    return sorted(override_items)


def build_tu_tien_item_details(
    entities: List[JsonObject],
    items: List[JsonObject],
    overrides: Optional[JsonObject] = None,
) -> Tuple[Dict[str, JsonObject], JsonObject]:
    """Return deterministic detail records and an unresolved-data report."""

    entities_by_id = {
        str(value["key"]): value
        for value in entities
        if isinstance(value, dict) and isinstance(value.get("key"), str)
    }
    items_by_id = {
        str(value["id"]): value
        for value in items
        if isinstance(value, dict) and isinstance(value.get("id"), str)
    }
    tu_tien_ids = sorted(
        entity_id
        for entity_id, value in items_by_id.items()
        if value.get("namespace") == "tu_tien"
    )
    reverse_recipes = _reverse_recipes(entities_by_id, items_by_id)
    details: Dict[str, JsonObject] = {}
    unsupported: List[JsonObject] = []

    for entity_id in tu_tien_ids:
        entity = entities_by_id.get(entity_id, {})
        item = items_by_id[entity_id]
        recipe_status = "known" if item.get("recipe") is not None else "unknown"
        usage_recipes = reverse_recipes.get(entity_id, [])
        usage_effects, unsupported_rows = _usage_effects(
            entity_id, entity, entities_by_id, items_by_id
        )
        unsupported.extend(unsupported_rows)
        usage_status = "known" if usage_recipes or usage_effects else "unknown"
        drop_sources = _drop_sources(entity_id, entity, entities_by_id, items_by_id)
        acquisitions = [
            value for value in entity.get("acquisition", []) if isinstance(value, dict)
        ]
        craft_only = bool(acquisitions) and all(
            value.get("type") == "craft" for value in acquisitions
        )
        drop_status = "known" if drop_sources else ("none" if craft_only else "unknown")
        details[entity_id] = {
            "recipeStatus": recipe_status,
            "usage": {
                "status": usage_status,
                "recipes": usage_recipes,
                "effects": usage_effects,
            },
            "dropBy": {"status": drop_status, "sources": drop_sources},
        }

    manual_items = _apply_overrides(details, overrides)
    section_keys = (
        ("recipe", lambda value: value["recipeStatus"]),
        ("usage", lambda value: value["usage"]["status"]),
        ("dropBy", lambda value: value["dropBy"]["status"]),
    )
    unknown_items = []
    counts = {
        "recipe": {status: 0 for status in sorted(DETAIL_STATUSES)},
        "usage": {status: 0 for status in sorted(DETAIL_STATUSES)},
        "dropBy": {status: 0 for status in sorted(DETAIL_STATUSES)},
    }
    for entity_id in sorted(details):
        value = details[entity_id]
        unknown_sections = []
        for section, getter in section_keys:
            status = getter(value)
            counts[section][status] += 1
            if status == "unknown":
                unknown_sections.append(section)
        if unknown_sections:
            unknown_items.append({"id": entity_id, "sections": unknown_sections})

    report = {
        "schema_version": 1,
        "totalTuTienItems": len(tu_tien_ids),
        "statusCounts": counts,
        "unknownItems": unknown_items,
        "unsupportedRecords": sorted(
            unsupported,
            key=lambda value: (
                value.get("id", ""),
                value.get("kind", ""),
                value.get("key", ""),
            ),
        ),
        "manualOverrideItems": manual_items,
    }
    return details, report
