"""Build published structure details and reverse crafting-station recipes."""

import re
from typing import Any, Dict, List, Mapping, Optional, Sequence


JsonObject = Dict[str, Any]
_STATION_TAG = re.compile(r"\bstation_tag\s*=\s*['\"]([^'\"]+)['\"]")
_TECH_STATIONS = {
    "ANCIENT_FOUR": (("ancient_altar", "Ancient Pseudoscience Station"),),
    "ANCIENT_TWO": (
        ("ancient_altar_broken", "Broken Ancient Pseudoscience Station"),
        ("ancient_altar", "Ancient Pseudoscience Station"),
    ),
    "CARNIVAL_HOSTSHOP_THREE": (("carnival_hostshop", "Cawnival Tree"),),
    "CARPENTRY_TWO": (("carpentry_station", "Sawhorse"),),
    "CARTOGRAPHY_TWO": (("cartographydesk", "Cartographer's Desk"),),
    "CATCOONOFFERING_THREE": (("yot_catcoonshrine", "Catcoon Shrine"),),
    "CELESTIAL_ONE": (("moon_altar", "Celestial Altar"),),
    "CELESTIAL_THREE": (("moon_altar", "Celestial Altar"),),
    "KNIGHTOFFERING_THREE": (("yoth_knightshrine", "Knook Shrine"),),
    "MAGIC_THREE": (("researchlab3", "Shadow Manipulator"),),
    "MAGIC_TWO": (
        ("researchlab4", "Prestihatitator"),
        ("researchlab3", "Shadow Manipulator"),
    ),
    "PERDOFFERING_ONE": (("perdshrine", "Gobbler Shrine"),),
    "RABBITOFFERING_THREE": (("yotr_rabbitshrine", "Bunnyman Shrine"),),
    "SCIENCE_ONE": (
        ("researchlab", "Science Machine"),
        ("researchlab2", "Alchemy Engine"),
    ),
    "SCIENCE_TWO": (("researchlab2", "Alchemy Engine"),),
    "SEAFARING_ONE": (("seafaring_prototyper", "Think Tank"),),
    "VAULT_REFINE_ONE": (("vault_security_desk", "Ancient Guard Post"),),
    "WAGPUNK_WORKSTATION_TWO": (
        ("wagpunk_workstation", "W.A.R.B.I.S. Workstation"),
    ),
    "WARGOFFERING_THREE": (("yotd_dragonshrine", "Dragonfly Shrine"),),
    "YOT_CATCOON": (("yot_catcoonshrine", "Catcoon Shrine"),),
    "YOTB": (("yotb_beefaloshrine", "Beefalo Shrine"),),
    "YOTC": (("yotc_carratshrine", "Carrat Shrine"),),
    "YOTD": (("yotd_dragonshrine", "Dragonfly Shrine"),),
    "YOTH": (("yoth_knightshrine", "Knook Shrine"),),
    "YOTP": (("perdshrine", "Gobbler Shrine"),),
    "YOTS": (("yots_snakeshrine", "Snake Shrine"),),
}
_STAT_LABELS = {
    "container_slots": "Sức chứa",
    "sanity_aura": "Hào quang tinh thần",
    "max_health": "Độ bền",
    "uses": "Số lần sử dụng",
    "trader_enabled": "Có thể nhận vật phẩm",
    "trader_deletes_item": "Tiêu hao vật phẩm được trao",
}


def _number(value: Any) -> str:
    if isinstance(value, bool):
        return "Có" if value else "Không"
    if isinstance(value, (int, float)):
        number = float(value)
        return str(int(number)) if number.is_integer() else format(number, "g")
    return str(value)


def _catalog_evidence(item_id: str, group: str) -> List[JsonObject]:
    return [
        {
            "source": "public/data/catalog.json",
            "locator": f"{item_id}:{group}",
        }
    ]


def _reference(item: JsonObject) -> JsonObject:
    return {
        "id": item["id"],
        "name": item["name"],
        "sprite": item.get("sprite"),
    }


def _station_item_id(
    station_tag: str,
    items_by_id: Mapping[str, JsonObject],
) -> Optional[str]:
    candidates = [
        item_id
        for item_id, item in items_by_id.items()
        if item.get("category") == "structure"
        and str(item.get("prefabId") or "").casefold() == station_tag.casefold()
    ]
    return sorted(candidates)[0] if candidates else None


def _identity(value: Any) -> str:
    text = str(value or "").casefold().replace("/dst", "")
    return re.sub(r"[^a-z0-9]+", "", text)


def _tech_station_ids(
    tech: Any,
    items_by_id: Mapping[str, JsonObject],
) -> List[str]:
    tech_name = str(tech or "").upper()
    if tech_name.startswith("TECH."):
        tech_name = tech_name[5:]
    specs = _TECH_STATIONS.get(tech_name, ())
    result = []
    for prefab_id, display_name in specs:
        candidates = [
            item_id
            for item_id, item in items_by_id.items()
            if item.get("category") == "structure"
            and (
                _identity(item.get("prefabId")) == _identity(prefab_id)
                or _identity(item.get("name")) == _identity(display_name)
                or _identity(item.get("englishName")) == _identity(display_name)
                or _identity(
                    item.get("wiki", {}).get("title")
                    if isinstance(item.get("wiki"), dict)
                    else None
                )
                == _identity(display_name)
            )
        ]
        if candidates:
            result.append(sorted(candidates)[0])
    return sorted(set(result))


def _recipe_station_ids(
    entity: JsonObject,
    items_by_id: Mapping[str, JsonObject],
) -> List[str]:
    result = []
    recipes = entity.get("recipes")
    if not isinstance(recipes, list):
        return result
    for recipe in recipes:
        if not isinstance(recipe, dict):
            continue
        restrictions = recipe.get("restrictions")
        if not isinstance(restrictions, dict):
            continue
        direct = restrictions.get("station_tag")
        tags = [direct] if isinstance(direct, str) else []
        expression = restrictions.get("config_expression")
        if isinstance(expression, str):
            tags.extend(_STATION_TAG.findall(expression))
        for tag in tags:
            station_id = _station_item_id(tag, items_by_id)
            if station_id is not None:
                result.append(station_id)
    return sorted(set(result))


def _station_recipe(
    item: JsonObject,
    entity: Optional[JsonObject],
    station_id: str,
) -> Optional[JsonObject]:
    recipe = item.get("recipe")
    if not isinstance(recipe, dict) or not isinstance(recipe.get("ingredients"), list):
        return None
    raw_recipes = entity.get("recipes") if isinstance(entity, dict) else None
    raw_recipe = (
        raw_recipes[0]
        if isinstance(raw_recipes, list)
        and raw_recipes
        and isinstance(raw_recipes[0], dict)
        else {}
    )
    restrictions = raw_recipe.get("restrictions")
    if not isinstance(restrictions, dict):
        restrictions = {}
    return {
        "result": _reference(item),
        "resultAmount": recipe.get("outputCount", 1),
        "ingredients": [dict(value) for value in recipe["ingredients"]],
        "station": station_id,
        "tech": raw_recipe.get("tech"),
        "restrictions": dict(sorted(restrictions.items())),
        "note": item.get("craftingNote"),
        "evidence": _catalog_evidence(str(item["id"]), "recipe"),
    }


def build_station_outputs(
    items: Sequence[JsonObject],
    catalog_entities: Sequence[JsonObject],
) -> Dict[str, List[JsonObject]]:
    """Reverse item recipes into the structures required to craft them."""

    items_by_id = {
        str(item["id"]): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    entities_by_id = {
        str(entity["key"]): entity
        for entity in catalog_entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    result: Dict[str, List[JsonObject]] = {}
    for item_id in sorted(items_by_id):
        current = items_by_id[item_id]
        entity = entities_by_id.get(item_id)
        station_ids = _recipe_station_ids(entity or {}, items_by_id)
        raw_recipes = entity.get("recipes") if isinstance(entity, dict) else None
        if isinstance(raw_recipes, list):
            for raw_recipe in raw_recipes:
                if isinstance(raw_recipe, dict):
                    station_ids.extend(
                        _tech_station_ids(raw_recipe.get("tech"), items_by_id)
                    )
        if (
            current.get("namespace") == "tu_tien"
            and current.get("category") == "pill"
            and "tu_tien:xd_liandanlu" in items_by_id
        ):
            station_ids.append("tu_tien:xd_liandanlu")
        for station_id in sorted(set(station_ids)):
            recipe = _station_recipe(current, entity, station_id)
            if recipe is not None:
                result.setdefault(station_id, []).append(recipe)
    for station_id in result:
        result[station_id].sort(key=lambda value: value["result"]["id"])
    return dict(sorted(result.items()))


def _origin(
    item: JsonObject,
    wiki: Mapping[str, Any],
) -> JsonObject:
    recipe = item.get("recipe")
    craftable = isinstance(recipe, dict)
    raw = wiki.get("origin")
    if isinstance(raw, dict):
        result = dict(raw)
    else:
        result = {
            "status": "known" if craftable else "unknown",
            "naturallySpawned": False,
            "renewable": None,
            "spawnCode": item.get("prefabId"),
            "sources": [],
            "respawn": None,
            "evidence": _catalog_evidence(str(item["id"]), "origin"),
        }
    naturally_spawned = result.get("naturallySpawned") is True
    result["craftable"] = craftable
    result["note"] = (
        "Công trình tự sinh trong thế giới và không thể chế tạo."
        if naturally_spawned and not craftable
        else None
    )
    return result


def _construction(item: JsonObject, entity: Optional[JsonObject]) -> JsonObject:
    recipe = item.get("recipe")
    evidence = _catalog_evidence(str(item["id"]), "construction")
    if not isinstance(recipe, dict):
        return {
            "status": "none",
            "outputCount": None,
            "ingredients": [],
            "tech": None,
            "station": None,
            "restrictions": {},
            "note": "Không thể chế tạo.",
            "evidence": evidence,
        }
    raw_recipes = entity.get("recipes") if isinstance(entity, dict) else None
    raw_recipe = (
        raw_recipes[0]
        if isinstance(raw_recipes, list)
        and raw_recipes
        and isinstance(raw_recipes[0], dict)
        else {}
    )
    restrictions = raw_recipe.get("restrictions")
    if not isinstance(restrictions, dict):
        restrictions = {}
    return {
        "status": "known",
        "outputCount": recipe.get("outputCount", 1),
        "ingredients": [dict(value) for value in recipe.get("ingredients", [])],
        "tech": raw_recipe.get("tech"),
        "station": None,
        "restrictions": dict(sorted(restrictions.items())),
        "note": item.get("craftingNote"),
        "evidence": evidence,
    }


def _catalog_function_facts(
    item_id: str,
    entity: Optional[JsonObject],
) -> List[JsonObject]:
    if not isinstance(entity, dict) or not isinstance(entity.get("stats"), list):
        return []
    facts = []
    for stat in entity["stats"]:
        if not isinstance(stat, dict) or not isinstance(stat.get("key"), str):
            continue
        key = stat["key"]
        facts.append(
            {
                "key": key,
                "label": _STAT_LABELS.get(key, key.replace("_", " ").capitalize()),
                "value": _number(stat.get("value")),
                "unit": stat.get("unit") if isinstance(stat.get("unit"), str) else None,
                "context": None,
                "related": [],
                "evidence": _catalog_evidence(item_id, f"stats:{key}"),
            }
        )
    return sorted(facts, key=lambda value: value["key"])


def _functions(
    item_id: str,
    entity: Optional[JsonObject],
    wiki: Mapping[str, Any],
) -> JsonObject:
    wiki_functions = wiki.get("functions")
    wiki_facts = (
        wiki_functions.get("facts")
        if isinstance(wiki_functions, dict)
        and isinstance(wiki_functions.get("facts"), list)
        else []
    )
    facts_by_key = {
        str(fact["key"]): dict(fact)
        for fact in wiki_facts
        if isinstance(fact, dict) and isinstance(fact.get("key"), str)
    }
    for fact in _catalog_function_facts(item_id, entity):
        facts_by_key[fact["key"]] = fact
    facts = [facts_by_key[key] for key in sorted(facts_by_key)]
    if facts:
        return {
            "status": "known",
            "facts": facts,
            "reason": None,
            "evidence": [
                evidence
                for fact in facts
                for evidence in fact.get("evidence", [])
                if isinstance(evidence, dict)
            ],
        }
    if isinstance(wiki_functions, dict):
        return dict(wiki_functions)
    return {
        "status": "unknown",
        "facts": [],
        "reason": "Chưa xác minh được công dụng có cấu trúc.",
        "evidence": _catalog_evidence(item_id, "functions"),
    }


def _visual(item: JsonObject, wiki: Mapping[str, Any]) -> JsonObject:
    sprite = item.get("sprite")
    evidence = _catalog_evidence(str(item["id"]), "visual")
    if isinstance(sprite, dict):
        return {
            "status": "known",
            "kind": "inventory_icon",
            "sprite": sprite,
            "image": None,
            "alternatives": [],
            "reason": None,
            "evidence": evidence,
        }
    candidates = wiki.get("visual_candidates")
    candidates = candidates if isinstance(candidates, list) else []
    resolved = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict) and isinstance(candidate.get("src"), str)
    ]
    if resolved:
        selected = dict(resolved[0])
        return {
            "status": "known",
            "kind": "wiki_image",
            "sprite": None,
            "image": selected,
            "alternatives": [dict(value) for value in resolved[1:]],
            "reason": None,
            "evidence": selected.get("evidence", evidence),
        }
    return {
        "status": "unknown",
        "kind": None,
        "sprite": None,
        "image": None,
        "alternatives": [
            dict(value) for value in candidates if isinstance(value, dict)
        ],
        "reason": "Chưa tìm thấy icon, ảnh Wiki hoặc world asset đã xác minh.",
        "evidence": evidence,
    }


def build_structure_details(
    items: Sequence[JsonObject],
    catalog_entities: Sequence[JsonObject],
    wiki_details: Mapping[str, JsonObject],
) -> Dict[str, JsonObject]:
    """Assemble complete section states for every published structure."""

    entities_by_id = {
        str(entity["key"]): entity
        for entity in catalog_entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    outputs = build_station_outputs(items, catalog_entities)
    result: Dict[str, JsonObject] = {}
    for item in items:
        if not isinstance(item, dict) or item.get("category") != "structure":
            continue
        item_id = str(item["id"])
        entity = entities_by_id.get(item_id)
        wiki = wiki_details.get(item_id, {})
        station_recipes = outputs.get(item_id, [])
        result[item_id] = {
            "origin": _origin(item, wiki),
            "construction": _construction(item, entity),
            "functions": _functions(item_id, entity, wiki),
            "craftables": {
                "status": "known" if station_recipes else "none",
                "recipes": station_recipes,
                "reason": None,
                "evidence": _catalog_evidence(item_id, "craftables"),
            },
            "destruction": (
                dict(wiki["destruction"])
                if isinstance(wiki.get("destruction"), dict)
                else {
                    "status": "unknown",
                    "destroyable": None,
                    "tool": None,
                    "work": None,
                    "health": None,
                    "burnable": None,
                    "drops": [],
                    "regeneration": None,
                    "evidence": _catalog_evidence(item_id, "destruction"),
                }
            ),
            "visual": _visual(item, wiki),
        }
    return dict(sorted(result.items()))
