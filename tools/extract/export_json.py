"""Deterministic, frontend-oriented exports from the normalized catalog."""

import json
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional


def _json_value(value: Optional[str], default: Any) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def _atomic_json(path: Path, value: Dict[str, Any]) -> None:
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


def _key(namespace: str, prefab_id: str) -> str:
    return f"{namespace}:{prefab_id}"


def _catalog_entities(db: sqlite3.Connection) -> List[Dict[str, Any]]:
    entities: List[Dict[str, Any]] = []
    rows = db.execute("select * from entities order by namespace,prefab_id").fetchall()
    for row in rows:
        namespace = row["namespace"]
        prefab_id = row["prefab_id"]
        entity_key = _key(namespace, prefab_id)
        recipes = []
        for recipe in db.execute(
            "select * from recipes where product_namespace=? and product_id=? order by recipe_id",
            (namespace, prefab_id),
        ):
            ingredients = [
                {
                    "key": _key(item["ingredient_namespace"], item["ingredient_id"]),
                    "amount": item["amount"],
                    "position": item["position"],
                }
                for item in db.execute(
                    "select * from recipe_ingredients where recipe_id=? "
                    "order by position,ingredient_namespace,ingredient_id,amount",
                    (recipe["recipe_id"],),
                )
            ]
            recipes.append(
                {
                    "output_count": recipe["output_count"],
                    "tech": recipe["tech"],
                    "restrictions": _json_value(recipe["restrictions_json"], {}),
                    "ingredients": ingredients,
                }
            )

        acquisition = []
        for item in db.execute(
            "select * from acquisition_sources where target_namespace=? and target_id=? "
            "order by source_type,coalesce(source_namespace,''),coalesce(source_id,''),"
            "coalesce(chance,-1),coalesce(min_count,-1),coalesce(max_count,-1),conditions_json,acquisition_id",
            (namespace, prefab_id),
        ):
            source = None
            if item["source_namespace"] is not None and item["source_id"] is not None:
                source = _key(item["source_namespace"], item["source_id"])
            acquisition.append(
                {
                    "type": item["source_type"],
                    "source": source,
                    "chance": item["chance"],
                    "min_count": item["min_count"],
                    "max_count": item["max_count"],
                    "conditions": _json_value(item["conditions_json"], {}),
                }
            )

        stats = []
        for item in db.execute(
            "select * from stats where namespace=? and prefab_id=? order by stat_key",
            (namespace, prefab_id),
        ):
            stats.append(
                {
                    "key": item["stat_key"],
                    "value": item["value_num"] if item["value_num"] is not None else item["value_text"],
                    "unit": item["unit"],
                    "confidence": item["confidence"],
                }
            )

        effects = [
            {
                "trigger": item["trigger_name"],
                "key": item["effect_key"],
                "value": _json_value(item["value_json"], None),
                "duration": item["duration"],
            }
            for item in db.execute(
                "select * from effects where namespace=? and prefab_id=? "
                "order by coalesce(trigger_name,''),effect_key,value_json,coalesce(duration,-1),effect_id",
                (namespace, prefab_id),
            )
        ]
        relations = [
            {
                "type": item["relation_type"],
                "target": _key(item["to_namespace"], item["to_id"]),
                "metadata": _json_value(item["metadata_json"], {}),
            }
            for item in db.execute(
                "select * from entity_relations where from_namespace=? and from_id=? "
                "order by relation_type,to_namespace,to_id,metadata_json,relation_id",
                (namespace, prefab_id),
            )
        ]
        entities.append(
            {
                "key": entity_key,
                "namespace": namespace,
                "prefab_id": prefab_id,
                "type": row["entity_type"],
                "is_inventory_item": bool(row["is_inventory_item"]),
                "name": {"vi": row["name_vi"], "en": row["name_en"]},
                "description": {"vi": row["description_vi"], "en": row["description_en"]},
                "icon_key": row["icon_key"],
                "stats": stats,
                "recipes": recipes,
                "acquisition": acquisition,
                "effects": effects,
                "relations": relations,
                "confidence": row["confidence"],
            }
        )
    return entities


def _asset_rows(db: sqlite3.Connection) -> List[Dict[str, Any]]:
    assets = []
    for row in db.execute(
        "select * from assets order by namespace,coalesce(prefab_id,''),asset_type,"
        "coalesce(atlas,''),texture,coalesce(element,''),asset_id"
    ):
        evidence = []
        available_values = []
        texture_hashes = []
        for item in db.execute(
            "select e.*,s.kind source_kind,s.path source_path,s.version source_version,s.sha256 source_sha256 "
            "from evidence e join sources s on s.source_id=e.source_id "
            "where e.record_type='asset' and e.record_id=? "
            "order by e.source_id,e.locator,e.evidence_id",
            (row["asset_id"],),
        ):
            raw = _json_value(item["raw_value_json"], {})
            if isinstance(raw, dict):
                if isinstance(raw.get("available"), bool):
                    available_values.append(raw["available"])
                if isinstance(raw.get("texture_sha256"), str):
                    texture_hashes.append(raw["texture_sha256"])
            evidence.append(
                {
                    "source": {
                        "id": item["source_id"],
                        "kind": item["source_kind"],
                        "path": item["source_path"],
                        "version": item["source_version"],
                        "sha256": item["source_sha256"],
                    },
                    "locator": item["locator"],
                    "confidence": item["confidence"],
                    "selected": bool(item["selected"]),
                }
            )
        available = any(available_values) if available_values else bool(row["texture"])
        texture_sha256 = sorted(set(texture_hashes))[0] if texture_hashes else None
        linked_key = (
            _key(row["namespace"], row["prefab_id"])
            if row["prefab_id"] is not None
            else None
        )
        assets.append(
            {
                "asset_id": row["asset_id"],
                "key": linked_key or row["asset_id"],
                "namespace": row["namespace"],
                "prefab_id": row["prefab_id"],
                "type": row["asset_type"],
                "atlas": row["atlas"],
                "texture": row["texture"],
                "element": row["element"],
                "uv": _json_value(row["uv_json"], None),
                "available": available,
                "texture_sha256": texture_sha256,
                "evidence": evidence,
            }
        )
    return assets


def export_catalog(db_path: Path, catalog_path: Path, assets_path: Path) -> None:
    """Export complete nested entity data and an evidence-bearing asset map."""

    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    try:
        catalog = {"schema_version": 1, "entities": _catalog_entities(db)}
        assets = {"schema_version": 1, "assets": _asset_rows(db)}
    finally:
        db.close()
    _atomic_json(Path(catalog_path), catalog)
    _atomic_json(Path(assets_path), assets)
