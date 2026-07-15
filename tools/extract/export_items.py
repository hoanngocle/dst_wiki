"""Build the compact, deterministic item payload consumed by the frontend."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


JsonObject = Dict[str, Any]
PREFAB_CATEGORIES = {
    "item",
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
        if asset.get("type") != "inventory" or not isinstance(key, str):
            continue
        grouped.setdefault(key, []).append(asset)
    return {
        key: sorted(candidates, key=_asset_sort_key)[0]
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
    entity_type = entity.get("type")
    if not isinstance(entity_type, str):
        raise ValueError("entity type must be a string")
    category = LEGACY_CATEGORY_MAP.get(entity_type, entity_type)
    if category in PREFAB_CATEGORIES:
        return category
    return "other" if namespace == "tu_tien" else None


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
                    "name": _display_name(ingredient_entity, ingredient_id.split(":")[-1]),
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
        "sprite": _sprite(entity.get("icon_key"), selected_assets, textures),
        "recipe": recipe_payload,
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


def build_item_export(
    catalog: JsonObject,
    assets: JsonObject,
    crafting_notes: Optional[Dict[str, str]] = None,
) -> Tuple[JsonObject, JsonObject]:
    """Build compact item and texture payloads from the public audit exports."""

    source_entities = catalog.get("entities")
    source_assets = assets.get("assets")
    if not isinstance(source_entities, list) or not isinstance(source_assets, list):
        raise ValueError("catalog and asset payloads must contain arrays")
    entities = {
        entity["key"]: entity
        for entity in source_entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    selected_assets = _select_inventory_assets(
        [asset for asset in source_assets if isinstance(asset, dict)]
    )
    textures: Dict[str, JsonObject] = {}
    exportable_entities = []
    for entity in source_entities:
        if not isinstance(entity, dict) or _category(entity) is None:
            continue
        if entity.get("namespace") == "tu_tien" and _vietnamese_name(entity) is None:
            continue
        exportable_entities.append(entity)
    note_lookup = crafting_notes or {}
    items = [
        _build_item_entry(entity, entities, selected_assets, textures, note_lookup)
        for entity in exportable_entities
    ]
    items.sort(key=lambda item: item["id"])
    return (
        {"schema_version": 3, "items": items},
        {
            "schema_version": 1,
            "textures": [textures[key] for key in sorted(textures)],
        },
    )


def export_items(
    database_path: Path,
    catalog_path: Path,
    assets_path: Path,
    items_path: Path,
    textures_path: Path,
) -> None:
    """Read audit JSON and atomically publish the compact frontend contracts."""

    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    assets = json.loads(Path(assets_path).read_text(encoding="utf-8"))
    crafting_notes = load_crafting_notes(database_path)
    items, textures = build_item_export(catalog, assets, crafting_notes)
    _atomic_json(Path(items_path), items)
    _atomic_json(Path(textures_path), textures)
