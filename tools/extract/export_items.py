"""Build the compact, deterministic item payload consumed by the frontend."""

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from tools.extract.wiki_export import (
    export_wiki_artifacts,
    load_wiki_export,
    merge_wiki_items,
)
from tools.extract.effect_other_audit import audit_effect_other_items
from tools.extract.category_assets import publish_category_assets
from tools.extract.category_merge import (
    finalize_category_references,
    merge_category_mobs,
)
from tools.extract.exclusions import NON_ITEM_PREFAB_IDS
from tools.extract.item_details import build_tu_tien_item_details
from tools.extract.mob_details import build_mob_boss_audit, build_mob_details
from tools.extract.mob_groups import apply_mob_groups, load_mob_groups
from tools.extract.mob_wiki import load_mob_wiki_details
from tools.extract.structure_details import (
    audit_structure_visuals,
    build_structure_details,
)


JsonObject = Dict[str, Any]
PREFAB_CATEGORIES = {
    "item",
    "pill",
    "mob",
    "boss",
    "character",
    "structure",
    "effect",
    "other",
}
LEGACY_CATEGORY_MAP = {
    "inventory_item": "item",
    "creature": "mob",
    "player": "character",
}
RECIPE_DESC_PREFIX = "STRINGS.RECIPE_DESC."
DESCRIPTION_TRANSLATIONS = Path("data/manual/item_description_vi.json")
ITEM_DETAIL_OVERRIDES = Path("data/manual/tu_tien_item_details.json")
ITEM_DETAIL_REPORT = Path("data/generated/tu-tien-item-details-report.json")
STRUCTURE_ICON_AUDIT = Path("data/generated/structure-icon-audit.json")
EFFECT_OTHER_AUDIT = Path("data/generated/effect-other-audit.json")
CATEGORY_ARTIFACT = Path("data/generated/categories/animals.json")
CATEGORY_CRAWL = Path("data/crawled/fandom-categories/animals")
CATEGORY_ASSETS = Path("public/assets/wiki-categories/animals")
CATEGORY_AUDIT = Path("data/generated/category-crawl-audits/animals.json")
MOB_BOSS_AUDIT = Path("data/generated/mob-boss-audit.json")
MOB_GROUPS = Path("data/manual/mob-variant-groups.json")
MOB_WIKI_PAGES = Path("data/crawled/dontstarve-wiki/pages.jsonl")
ICON_KEY_ALIASES = {
    "tu_tien:xd_beefalo": "base_game:beefalo",
}
DISPLAY_NAME_OVERRIDES = {
    "base_game:asparagus": "Măng Tây",
    "base_game:berries": "Dâu Rừng",
    "base_game:bird_egg": "Trứng Chim",
    "base_game:blue_cap": "Nấm Lam",
    "base_game:corn": "Ngô",
    "base_game:pepper": "Ớt",
    "base_game:potato": "Khoai Tây",
    "base_game:shroomcake": "Bánh Nấm",
    "base_game:tomato": "Cà Chua",
    "base_game:watermelon": "Dưa Hấu",
}
MOB_STAT_LABELS = {
    "max_health": "Máu tối đa",
    "attack_damage": "Sát thương",
    "planar_damage": "Sát thương vị diện",
    "attack_period": "Chu kỳ tấn công",
    "attack_range": "Tầm đánh",
    "hit_range": "Tầm trúng đòn",
    "walk_speed": "Tốc độ đi",
    "run_speed": "Tốc độ chạy",
    "sanity_aura": "Hào quang tinh thần",
    "freeze_resistance": "Kháng đóng băng",
    "sleep_resistance": "Kháng ru ngủ",
}
MOB_STAT_ORDER = {key: position for position, key in enumerate(MOB_STAT_LABELS)}
RECIPE_INGREDIENT_ITEM_ALIASES = {
    "base_game:asparagus": "wiki:11814",
    "base_game:batwing": "wiki:129751",
    "base_game:berries": "wiki:194765",
    "base_game:bird_egg": "wiki:121150",
    "base_game:blue_cap": "wiki:53485",
    "base_game:bluegem": "wiki:196261",
    "base_game:corn": "wiki:195689",
    "base_game:dragonfruit": "wiki:171910",
    "base_game:feather_canary": "wiki:111783",
    "base_game:feather_crow": "wiki:111783",
    "base_game:fig": "wiki:133345",
    "base_game:green_cap": "wiki:177817",
    "base_game:ice": "wiki:210812",
    "base_game:mandrake": "wiki:162524",
    "base_game:marble": "wiki:127143",
    "base_game:meat": "wiki:164959",
    "base_game:monstermeat": "wiki:200397",
    "base_game:pepper": "wiki:160201",
    "base_game:plantmeat": "wiki:64181",
    "base_game:potato": "wiki:192129",
    "base_game:purplegem": "wiki:106511",
    "base_game:redgem": "wiki:59983",
    "base_game:shroomcake": "wiki:31197",
    "base_game:smallmeat": "wiki:96458",
    "base_game:tomato": "wiki:134571",
    "base_game:watermelon": "wiki:34175",
}
PILL_PREFAB_PATTERN = re.compile(
    r"^xd_dy_(?:cyfxd|dmhsd|hsphd|lmsqd|pshsd|qjqsd|qxdhd|xttyd|xynyd|yfsxd)_[1-5]$"
)


def _is_pill_prefab(prefab_id: Any) -> bool:
    return isinstance(prefab_id, str) and (
        prefab_id.startswith("xd_danyao_")
        or prefab_id in {"xd_dy_fd", "xd_dy_tsfhd"}
        or PILL_PREFAB_PATTERN.fullmatch(prefab_id) is not None
    )


def _atomic_json(path: Path, value: JsonObject) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, path)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise


def _asset_confidence(asset: JsonObject) -> float:
    evidence = asset.get("evidence")
    if not isinstance(evidence, list):
        return 0.0
    selected = [
        item
        for item in evidence
        if isinstance(item, dict) and item.get("selected") is True
    ]
    candidates = selected or [item for item in evidence if isinstance(item, dict)]
    return max(
        (
            float(item.get("confidence", 0.0))
            for item in candidates
            if isinstance(item.get("confidence", 0.0), (int, float))
        ),
        default=0.0,
    )


def _asset_sort_key(asset: JsonObject) -> Tuple[Any, ...]:
    return (
        0 if asset.get("available") is True else 1,
        -_asset_confidence(asset),
        str(asset.get("atlas") or ""),
        str(asset.get("texture") or ""),
        str(asset.get("element") or ""),
        str(asset.get("asset_id") or ""),
    )


def _select_inventory_assets(assets: List[JsonObject]) -> Dict[str, JsonObject]:
    grouped: Dict[str, List[JsonObject]] = {}
    for asset in assets:
        key = asset.get("key")
        if asset.get("type") not in {"inventory", "portrait", "map_icon"} or not isinstance(key, str):
            continue
        grouped.setdefault(key, []).append(asset)
    return {
        key: sorted(
            candidates,
            key=lambda asset: (
                {"inventory": 0, "portrait": 1, "map_icon": 2}.get(
                    str(asset.get("type")), 3
                ),
                *_asset_sort_key(asset),
            ),
        )[0]
        for key, candidates in grouped.items()
    }


def _display_name(entity: Optional[JsonObject], fallback: str) -> str:
    if not entity:
        return fallback
    names = entity.get("name")
    if isinstance(names, dict):
        for language in ("vi", "en"):
            value = names.get(language)
            if isinstance(value, str) and value.strip():
                return value.strip()
    prefab_id = entity.get("prefab_id")
    return prefab_id if isinstance(prefab_id, str) and prefab_id else fallback


def _vietnamese_name(entity: JsonObject) -> Optional[str]:
    names = entity.get("name")
    if not isinstance(names, dict):
        return None
    value = names.get("vi")
    return value.strip() if isinstance(value, str) and value.strip() else None


def _english_name(entity: JsonObject) -> Optional[str]:
    names = entity.get("name")
    if not isinstance(names, dict):
        return None
    value = names.get("en")
    return value.strip() if isinstance(value, str) and value.strip() else None


def _description(entity: JsonObject) -> Optional[str]:
    descriptions = entity.get("description")
    if not isinstance(descriptions, dict):
        return None
    for language in ("vi", "en"):
        value = descriptions.get(language)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _category(entity: JsonObject) -> Optional[str]:
    namespace = entity.get("namespace")
    if namespace not in ("tu_tien", "base_game"):
        raise ValueError("entity namespace is invalid")
    if namespace == "tu_tien" and _is_pill_prefab(entity.get("prefab_id")):
        return "pill"
    entity_type = entity.get("type")
    if not isinstance(entity_type, str):
        raise ValueError("entity type must be a string")
    if (
        namespace == "base_game"
        and entity_type == "dependency"
        and entity.get("is_inventory_item") is True
    ):
        return "item"
    category = LEGACY_CATEGORY_MAP.get(entity_type, entity_type)
    if category in PREFAB_CATEGORIES:
        return category
    return "other" if namespace == "tu_tien" else None


def _apply_manual_recipe_overrides(
    source_entities: List[Any], overrides: Optional[JsonObject]
) -> Tuple[List[Any], Dict[str, str]]:
    if overrides is None:
        return source_entities, {}
    if not isinstance(overrides, dict) or overrides.get("schema_version") != 1:
        raise ValueError("item detail overrides must use schema version 1")
    override_items = overrides.get("items")
    if not isinstance(override_items, dict):
        raise ValueError("item detail overrides must contain an items object")

    entities = [dict(entity) if isinstance(entity, dict) else entity for entity in source_entities]
    by_id = {
        entity.get("key"): entity
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    crafting_notes: Dict[str, str] = {}
    for entity_id, override in sorted(override_items.items()):
        if not isinstance(override, dict) or "recipe" not in override:
            continue
        entity = by_id.get(entity_id)
        if entity is None:
            raise ValueError(f"unknown manual recipe entity {entity_id}")
        recipe = override["recipe"]
        if not isinstance(recipe, dict) or not isinstance(recipe.get("ingredients"), list):
            raise ValueError(f"manual recipe for {entity_id} must contain ingredients")
        normalized_ingredients = []
        for position, ingredient in enumerate(recipe["ingredients"]):
            if not isinstance(ingredient, dict) or not isinstance(ingredient.get("id"), str):
                raise ValueError(f"manual recipe ingredient {position} for {entity_id} is invalid")
            ingredient_id = ingredient["id"]
            normalized_ingredients.append(
                {
                    "key": ingredient_id,
                    "amount": _positive_integer(
                        ingredient.get("amount"), "manual recipe ingredient amount"
                    ),
                    "position": position,
                }
            )
        entity["recipes"] = [
            {
                "output_count": _positive_integer(
                    recipe.get("outputCount", 1), "manual recipe output count"
                ),
                "ingredients": normalized_ingredients,
            }
        ]
        note = recipe.get("craftingNote")
        if note is not None:
            if not isinstance(note, str) or not note.strip():
                raise ValueError(f"manual recipe craftingNote for {entity_id} is invalid")
            crafting_notes[str(entity["prefab_id"]).lower()] = note.strip()
    return entities, crafting_notes


def _positive_integer(value: Any, field: str) -> int:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer")
    integer = int(value)
    if integer <= 0 or float(integer) != float(value):
        raise ValueError(f"{field} must be a positive integer")
    return integer


def _sprite(
    icon_key: Any,
    selected_assets: Dict[str, JsonObject],
    textures: Dict[str, JsonObject],
) -> Optional[JsonObject]:
    if not isinstance(icon_key, str):
        return None
    asset = selected_assets.get(icon_key)
    if not asset or asset.get("available") is not True:
        return None
    texture_hash = asset.get("texture_sha256")
    texture = asset.get("texture")
    uv = asset.get("uv")
    namespace = asset.get("namespace")
    if (
        not isinstance(texture_hash, str)
        or len(texture_hash) != 64
        or not isinstance(texture, str)
        or not isinstance(uv, dict)
        or namespace not in ("tu_tien", "base_game")
    ):
        return None
    normalized_uv = {
        key: float(uv[key])
        for key in ("u1", "u2", "v1", "v2")
        if isinstance(uv.get(key), (int, float))
    }
    if len(normalized_uv) != 4:
        return None
    textures.setdefault(
        texture_hash,
        {
            "sha256": texture_hash,
            "source": "mod" if namespace == "tu_tien" else "base_game",
            "texture": texture,
        },
    )
    return {
        "src": f"/assets/game/{texture_hash}.png",
        "uv": normalized_uv,
    }


def _build_item_entry(
    entity: JsonObject,
    entities: Dict[str, JsonObject],
    selected_assets: Dict[str, JsonObject],
    textures: Dict[str, JsonObject],
    crafting_notes: Dict[str, str],
) -> JsonObject:
    entity_id = str(entity["key"])
    prefab_id = str(entity["prefab_id"])
    category = _category(entity)
    if category is None:
        raise ValueError(f"base-game entity {entity_id} has no prefab category")
    recipes = entity.get("recipes")
    recipe_payload = None
    if isinstance(recipes, list) and recipes:
        recipe = recipes[0]
        ingredients = []
        source_ingredients = recipe.get("ingredients", [])
        for ingredient in sorted(
            source_ingredients,
            key=lambda value: (
                int(value.get("position", 0)),
                str(value.get("key") or ""),
            ),
        ):
            raw_amount = ingredient.get("amount")
            if (
                isinstance(raw_amount, (int, float))
                and not isinstance(raw_amount, bool)
                and float(raw_amount) == 0.0
            ):
                continue
            ingredient_id = str(ingredient["key"])
            ingredient_entity = entities.get(ingredient_id)
            ingredient_icon = (
                ingredient_entity.get("icon_key") if ingredient_entity else None
            )
            ingredients.append(
                {
                    "id": ingredient_id,
                    "name": _display_name(
                        ingredient_entity,
                        DISPLAY_NAME_OVERRIDES.get(
                            ingredient_id, ingredient_id.split(":")[-1]
                        ),
                    ),
                    "amount": _positive_integer(raw_amount, "ingredient amount"),
                    "sprite": _sprite(ingredient_icon, selected_assets, textures),
                }
            )
        recipe_payload = {
            "outputCount": _positive_integer(
                recipe.get("output_count", 1), "recipe output count"
            ),
            "ingredients": ingredients,
        }
    return {
        "id": entity_id,
        "prefabId": prefab_id,
        "namespace": entity["namespace"],
        "category": category,
        "name": _display_name(entity, prefab_id),
        "englishName": _english_name(entity),
        "description": _description(entity),
        "craftingNote": crafting_notes.get(prefab_id.lower()),
        "sprite": _sprite(
            entity.get("icon_key")
            or (entity_id if entity_id in selected_assets else None)
            or (
                entities.get(ICON_KEY_ALIASES.get(entity_id, ""), {}).get("icon_key")
            ),
            selected_assets,
            textures,
        ),
        "recipe": recipe_payload,
        "mob": None,
        "character": None,
        "structureDetails": None,
        "wiki": None,
    }


def _format_number(value: Any) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else format(number, "g")


def _format_chance(value: Any) -> Optional[str]:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    return f"{_format_number(float(value) * 100)}%"


def _reference_for_item(
    entity_id: str,
    entities: Dict[str, JsonObject],
    items_by_id: Dict[str, JsonObject],
) -> JsonObject:
    item = items_by_id.get(entity_id)
    if item is not None:
        return {"id": entity_id, "name": item["name"], "sprite": item.get("sprite")}
    return {
        "id": entity_id,
        "name": _display_name(entities.get(entity_id), entity_id.split(":")[-1]),
        "sprite": None,
    }


def _mob_details(
    entity: JsonObject,
    entities: Dict[str, JsonObject],
    items_by_id: Dict[str, JsonObject],
    runtime_coverage: List[JsonObject],
) -> JsonObject:
    entity_id = str(entity["key"])
    raw_stats = {
        str(stat.get("key")): stat
        for stat in entity.get("stats", [])
        if isinstance(stat, dict) and isinstance(stat.get("key"), str)
    }
    stats = []
    for key in sorted(
        (key for key in raw_stats if key in MOB_STAT_LABELS),
        key=lambda key: (MOB_STAT_ORDER[key], key),
    ):
        stat = raw_stats[key]
        value = stat.get("value")
        if not isinstance(value, (str, int, float)) or isinstance(value, bool):
            continue
        stats.append(
            {
                "key": key,
                "label": MOB_STAT_LABELS[key],
                "value": value,
                "unit": stat.get("unit") if isinstance(stat.get("unit"), str) else None,
            }
        )

    mechanics = []
    special_states = raw_stats.get("special_states", {}).get("value")
    if isinstance(special_states, str) and special_states.strip():
        mechanics.append("Trạng thái đặc biệt: " + special_states.strip())

    grouped: Dict[Tuple[str, Any, str], JsonObject] = {}
    for target_id, target in entities.items():
        for acquisition in target.get("acquisition", []):
            if (
                not isinstance(acquisition, dict)
                or acquisition.get("type") != "drop"
                or acquisition.get("source") != entity_id
            ):
                continue
            conditions = acquisition.get("conditions")
            conditions_text = ""
            if isinstance(conditions, dict) and conditions:
                loot_table = conditions.get("loot_table")
                if isinstance(loot_table, str) and loot_table:
                    conditions_text = f"Bảng rơi: {loot_table}"
            chance = acquisition.get("chance")
            group_key = (
                target_id,
                chance if isinstance(chance, (int, float)) else None,
                conditions_text,
            )
            minimum = acquisition.get("min_count", 1)
            maximum = acquisition.get("max_count", minimum)
            row = grouped.setdefault(
                group_key,
                {
                    "item": _reference_for_item(target_id, entities, items_by_id),
                    "minimum": 0.0,
                    "maximum": 0.0,
                    "chance": _format_chance(chance),
                    "conditions": conditions_text or None,
                },
            )
            row["minimum"] += float(minimum) if isinstance(minimum, (int, float)) else 1.0
            row["maximum"] += float(maximum) if isinstance(maximum, (int, float)) else 1.0

    loot = []
    for row in sorted(grouped.values(), key=lambda value: value["item"]["id"]):
        minimum = row.pop("minimum")
        maximum = row.pop("maximum")
        row["quantity"] = (
            _format_number(minimum)
            if minimum == maximum
            else f"{_format_number(minimum)}–{_format_number(maximum)}"
        )
        loot.append(row)
    drop_coverage = next(
        (
            value
            for value in runtime_coverage
            if value.get("namespace") == entity.get("namespace")
            and value.get("prefab_id") == entity.get("prefab_id")
            and value.get("category") == "drop"
        ),
        None,
    )
    loot_status = "known" if loot else (
        "none" if drop_coverage and drop_coverage.get("status") == "observed" else "unknown"
    )
    return {"stats": stats, "mechanics": mechanics, "lootStatus": loot_status, "loot": loot}


def _character_profile(entity: JsonObject) -> JsonObject:
    profile = {
        str(effect.get("key")): effect.get("value")
        for effect in entity.get("effects", [])
        if isinstance(effect, dict) and effect.get("trigger") == "character_profile"
    }
    description = _description(entity) or ""
    abilities = [
        line.lstrip("*• ").strip()
        for line in description.splitlines()
        if line.lstrip("*• ").strip()
    ]
    return {
        "title": profile.get("character_title") if isinstance(profile.get("character_title"), str) else None,
        "survivability": profile.get("character_survivability") if isinstance(profile.get("character_survivability"), str) else None,
        "quote": profile.get("character_quote") if isinstance(profile.get("character_quote"), str) else None,
        "abilities": abilities,
    }


def load_crafting_notes(database_path: Path) -> Dict[str, str]:
    """Load deterministic Tu Tiên recipe descriptions from the audit database."""

    grouped: Dict[str, set[str]] = {}
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "select text_key,value_vi from game_text "
            "where text_key glob 'STRINGS.RECIPE_DESC.*' "
            "order by text_key,value_vi"
        )
        for text_key, value_vi in rows:
            grouped.setdefault(str(text_key), set()).add(str(value_vi))

    conflicts = sorted(key for key, values in grouped.items() if len(values) > 1)
    if conflicts:
        raise ValueError(f"conflicting crafting note for {conflicts[0]}")

    return {
        text_key[len(RECIPE_DESC_PREFIX) :].lower(): next(iter(values))
        for text_key, values in sorted(grouped.items())
    }


def load_runtime_coverage(database_path: Path) -> List[JsonObject]:
    """Load normalized runtime coverage used to confirm absent detail sections."""

    with sqlite3.connect(database_path) as connection:
        exists = connection.execute(
            "select 1 from sqlite_master where type='table' and name='runtime_coverage'"
        ).fetchone()
        if not exists:
            return []
        rows = connection.execute(
            "select namespace,prefab_id,category,status,reason,details_json "
            "from runtime_coverage order by namespace,prefab_id,category"
        )
        result = []
        for namespace, prefab_id, category, status, reason, details_json in rows:
            details = json.loads(str(details_json))
            if not isinstance(details, dict):
                raise ValueError(
                    f"runtime coverage {namespace}:{prefab_id}:{category} details must be an object"
                )
            result.append(
                {
                    "namespace": str(namespace),
                    "prefab_id": str(prefab_id),
                    "category": str(category),
                    "status": str(status),
                    "reason": str(reason),
                    "details": details,
                }
            )
    return result


def build_item_export(
    catalog: JsonObject,
    assets: JsonObject,
    crafting_notes: Optional[Dict[str, str]] = None,
    detail_overrides: Optional[JsonObject] = None,
    runtime_coverage: Optional[List[JsonObject]] = None,
) -> Tuple[JsonObject, JsonObject, JsonObject]:
    """Build compact item and texture payloads from the public audit exports."""

    source_entities = catalog.get("entities")
    source_assets = assets.get("assets")
    if not isinstance(source_entities, list) or not isinstance(source_assets, list):
        raise ValueError("catalog and asset payloads must contain arrays")
    source_entities, manual_crafting_notes = _apply_manual_recipe_overrides(
        source_entities, detail_overrides
    )
    entities = {
        entity["key"]: entity
        for entity in source_entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    selected_assets = _select_inventory_assets(
        [asset for asset in source_assets if isinstance(asset, dict)]
    )
    referenced_dependency_ids = {
        ingredient.get("key")
        for entity in source_entities
        if isinstance(entity, dict) and entity.get("type") != "dependency"
        for recipe in (
            entity.get("recipes") if isinstance(entity.get("recipes"), list) else []
        )
        if isinstance(recipe, dict)
        for ingredient in (
            recipe.get("ingredients")
            if isinstance(recipe.get("ingredients"), list)
            else []
        )
        if isinstance(ingredient, dict) and isinstance(ingredient.get("key"), str)
    }
    referenced_dependency_ids.update(
        str(entity["key"])
        for entity in source_entities
        if isinstance(entity, dict)
        and isinstance(entity.get("key"), str)
        and isinstance(entity.get("acquisition"), list)
        and bool(entity["acquisition"])
    )
    textures: Dict[str, JsonObject] = {}
    exportable_entities = []
    for entity in source_entities:
        if not isinstance(entity, dict) or _category(entity) is None:
            continue
        if (
            entity.get("type") == "dependency"
            and entity.get("key") not in referenced_dependency_ids
        ):
            continue
        if entity.get("prefab_id") in NON_ITEM_PREFAB_IDS:
            continue
        if entity.get("namespace") == "tu_tien" and _vietnamese_name(entity) is None:
            continue
        exportable_entities.append(entity)
    note_lookup = {**(crafting_notes or {}), **manual_crafting_notes}
    items = [
        _build_item_entry(entity, entities, selected_assets, textures, note_lookup)
        for entity in exportable_entities
    ]
    items.sort(key=lambda item: item["id"])
    details, detail_report = build_tu_tien_item_details(
        [entity for entity in source_entities if isinstance(entity, dict)],
        items,
        detail_overrides,
        runtime_coverage,
    )
    for item in items:
        item["details"] = details.get(item["id"])
    items_by_id = {item["id"]: item for item in items}
    for item in items:
        entity = entities[item["id"]]
        if item["category"] == "mob":
            item["mob"] = _mob_details(
                entity, entities, items_by_id, runtime_coverage or []
            )
        elif item["category"] == "character":
            item["character"] = _character_profile(entity)
    return (
        {"schema_version": 7, "items": items},
        {
            "schema_version": 1,
            "textures": [textures[key] for key in sorted(textures)],
        },
        detail_report,
    )


def apply_description_translations(
    items: List[JsonObject], translations_path: Path
) -> List[JsonObject]:
    """Replace an English database description only when its source still matches."""

    path = Path(translations_path)
    if not path.is_file():
        return items
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError(f"invalid item description translations: {path}")
    translations = value.get("items")
    if not isinstance(translations, dict):
        raise ValueError(f"item description translations must contain an items object: {path}")

    result = []
    for item in items:
        translated = dict(item)
        entry = translations.get(item.get("id"))
        if (
            isinstance(entry, dict)
            and item.get("description") == entry.get("source")
            and isinstance(entry.get("vi"), str)
            and entry["vi"].strip()
        ):
            translated["description"] = entry["vi"].strip()
        result.append(translated)
    return result


def link_recipe_ingredients(items: List[JsonObject]) -> List[JsonObject]:
    """Attach every resolvable recipe ingredient to its published item and icon."""

    items_by_id = {
        item.get("id"): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    linked_items = []
    for item in items:
        linked_item = dict(item)
        recipe = item.get("recipe")
        if not isinstance(recipe, dict) or not isinstance(recipe.get("ingredients"), list):
            linked_items.append(linked_item)
            continue
        linked_ingredients = []
        for ingredient in recipe["ingredients"]:
            linked_ingredient = dict(ingredient)
            ingredient_id = ingredient.get("id")
            target_id = RECIPE_INGREDIENT_ITEM_ALIASES.get(
                ingredient_id, ingredient_id
            )
            target = items_by_id.get(target_id)
            if target is not None:
                linked_ingredient["id"] = target_id
                if linked_ingredient.get("sprite") is None:
                    linked_ingredient["sprite"] = target.get("sprite")
            linked_ingredients.append(linked_ingredient)
        linked_item["recipe"] = {**recipe, "ingredients": linked_ingredients}
        linked_items.append(linked_item)
    return linked_items


def filter_unreferenced_base_dependencies(
    items: List[JsonObject], entities: Sequence[JsonObject]
) -> List[JsonObject]:
    """Keep materialized dependencies only when a public detail links to them."""

    dependency_ids = {
        str(entity["key"])
        for entity in entities
        if isinstance(entity, dict)
        and entity.get("type") == "dependency"
        and isinstance(entity.get("key"), str)
    }
    referenced_ids = set()

    def collect(value: Any) -> None:
        if isinstance(value, list):
            for entry in value:
                collect(entry)
            return
        if not isinstance(value, dict):
            return
        ingredients = value.get("ingredients")
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                ingredient_id = ingredient.get("id") if isinstance(ingredient, dict) else None
                if isinstance(ingredient_id, str):
                    referenced_ids.add(ingredient_id)
        loot = value.get("loot")
        if isinstance(loot, list):
            for drop in loot:
                drop_item = drop.get("item") if isinstance(drop, dict) else None
                drop_id = drop_item.get("id") if isinstance(drop_item, dict) else None
                if isinstance(drop_id, str):
                    referenced_ids.add(drop_id)
        for nested in value.values():
            collect(nested)

    collect(items)
    return [
        item
        for item in items
        if str(item.get("id")) not in dependency_ids
        or str(item.get("id")) in referenced_ids
    ]


def export_items(
    database_path: Path,
    catalog_path: Path,
    assets_path: Path,
    items_path: Path,
    textures_path: Path,
    wiki_crawl_path: Path = Path("data/crawled/dontstarve-items"),
    wiki_details_path: Path = Path("public/data/wiki/pages"),
    wiki_assets_path: Path = Path("public/assets/wiki"),
    description_translations_path: Path = DESCRIPTION_TRANSLATIONS,
    detail_overrides_path: Path = ITEM_DETAIL_OVERRIDES,
    detail_report_path: Path = ITEM_DETAIL_REPORT,
    structure_audit_path: Path = STRUCTURE_ICON_AUDIT,
    effect_other_audit_path: Path = EFFECT_OTHER_AUDIT,
    category_artifact_path: Path = CATEGORY_ARTIFACT,
    category_crawl_path: Path = CATEGORY_CRAWL,
    category_assets_path: Path = CATEGORY_ASSETS,
    category_audit_path: Path = CATEGORY_AUDIT,
    mob_audit_path: Path = MOB_BOSS_AUDIT,
    mob_groups_path: Path = MOB_GROUPS,
    mob_wiki_path: Path = MOB_WIKI_PAGES,
) -> None:
    """Read audit JSON and atomically publish the compact frontend contracts."""

    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    assets = json.loads(Path(assets_path).read_text(encoding="utf-8"))
    detail_overrides = json.loads(
        Path(detail_overrides_path).read_text(encoding="utf-8")
    )
    runtime_coverage = load_runtime_coverage(database_path)
    crafting_notes = load_crafting_notes(database_path)
    items, textures, detail_report = build_item_export(
        catalog,
        assets,
        crafting_notes,
        detail_overrides,
        runtime_coverage,
    )
    items["items"] = apply_description_translations(
        items["items"], description_translations_path
    )
    wiki = load_wiki_export(database_path, wiki_crawl_path)
    items["items"] = merge_wiki_items(items["items"], wiki)
    items["items"] = link_recipe_ingredients(items["items"])
    mob_groups = load_mob_groups(mob_groups_path)
    mob_wiki_details = (
        load_mob_wiki_details(mob_wiki_path, items["items"], mob_groups)
        if Path(mob_wiki_path).is_file()
        else {}
    )
    mob_details = build_mob_details(
        items["items"],
        catalog["entities"],
        mob_wiki_details,
        runtime_coverage,
        mob_groups,
    )
    items_by_id = {str(item["id"]): item for item in items["items"]}
    for item_id, detail in mob_details.items():
        if item_id in items_by_id:
            item = items_by_id[item_id]
            item["mob"] = detail
            if item.get("sprite") is None:
                variants = detail.get("variants", [])
                canonical_variant = next(
                    (
                        variant
                        for variant in variants
                        if isinstance(variant, dict) and variant.get("id") == item_id
                    ),
                    None,
                )
                if isinstance(canonical_variant, dict):
                    item["sprite"] = canonical_variant.get("sprite")
    mob_audit = build_mob_boss_audit(items["items"], mob_details, mob_groups)
    items["items"], _group_rows = apply_mob_groups(items["items"], mob_groups)
    category_audit = None
    category_artifact_path = Path(category_artifact_path)
    if category_artifact_path.is_file():
        category_artifact = json.loads(
            category_artifact_path.read_text(encoding="utf-8")
        )
        published_assets = publish_category_assets(
            category_artifact,
            Path(category_crawl_path),
            Path(category_assets_path),
        )
        category_result = merge_category_mobs(
            items["items"], category_artifact, catalog["entities"]
        )
        items["items"] = category_result.items
        category_audit = {**category_result.audit, "assets": published_assets}
    items["items"] = filter_unreferenced_base_dependencies(
        items["items"], catalog["entities"]
    )
    audit_rows, excluded_ids = audit_structure_visuals(
        items["items"], catalog["entities"], wiki.structure_details
    )
    items["items"] = [
        item for item in items["items"] if item.get("id") not in excluded_ids
    ]
    structure_details = build_structure_details(
        items["items"], catalog["entities"], wiki.structure_details
    )
    for item in items["items"]:
        item.setdefault("details", None)
        item["structureDetails"] = structure_details.get(item.get("id"))
    effect_other_rows, effect_other_excluded_ids = audit_effect_other_items(
        items["items"], catalog["entities"], wiki.details
    )
    items["items"] = [
        item
        for item in items["items"]
        if item.get("id") not in effect_other_excluded_ids
    ]
    finalize_category_references(items["items"])
    effect_other_audit = {
        "schema_version": 1,
        "summary": {
            "total": len(effect_other_rows),
            "keep": sum(
                row.get("action") == "keep" for row in effect_other_rows
            ),
            "exclude": sum(
                row.get("action") == "exclude" for row in effect_other_rows
            ),
            "categories": {
                category: sum(
                    row.get("category") == category for row in effect_other_rows
                )
                for category in ("effect", "other")
            },
        },
        "rows": effect_other_rows,
    }
    action_counts = {
        action: sum(row.get("action") == action for row in audit_rows)
        for action in ("keep", "repair", "exclude")
    }
    classifications = sorted(
        {
            str(row["classification"])
            for row in audit_rows
            if isinstance(row.get("classification"), str)
        }
    )
    structure_audit = {
        "schema_version": 1,
        "summary": {
            "total": len(audit_rows),
            **action_counts,
            "classifications": {
                classification: sum(
                    row.get("classification") == classification
                    for row in audit_rows
                )
                for classification in classifications
            },
        },
        "rows": audit_rows,
    }
    _atomic_json(Path(items_path), items)
    _atomic_json(Path(textures_path), textures)
    _atomic_json(Path(detail_report_path), detail_report)
    _atomic_json(Path(structure_audit_path), structure_audit)
    _atomic_json(Path(effect_other_audit_path), effect_other_audit)
    if category_audit is not None:
        _atomic_json(Path(category_audit_path), category_audit)
    _atomic_json(Path(mob_audit_path), mob_audit)
    if wiki.details or wiki.assets:
        export_wiki_artifacts(wiki, wiki_details_path, wiki_assets_path)
