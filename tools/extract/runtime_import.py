import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef


SCHEMA_VERSION = 1
REQUIRED_KEYS = {
    "schema_version",
    "mod_version",
    "recipes",
    "prefabs",
    "errors",
}
PERSISTENT_HEADER = re.compile(rb"\AKLEI +[0-9]+ ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    parts = path.resolve().parts
    if "data" in parts:
        index = len(parts) - 1 - list(reversed(parts)).index("data")
        return Path(*parts[index:]).as_posix()
    return path.name


def _require_object(value: Any, label: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _require_number(value: Any, label: str) -> Any:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    return value


def _require_string_list(value: Any, label: str) -> List[str]:
    values = _require_list(value, label)
    for index, entry in enumerate(values):
        _require_string(entry, f"{label}[{index}]")
    return values


def _runtime_reference(prefab_id: str) -> Dict[str, Any]:
    if prefab_id.startswith("xd_"):
        return {
            "namespace": "tu_tien",
            "prefab_id": prefab_id,
            "resolution": "resolved",
        }
    return {
        "prefab_id": prefab_id,
        "dependency_candidate": True,
        "resolution": "unresolved",
    }


def _validate_cost_rows(
    value: Any, label: str, expected_group: str, *, item: bool = False
) -> List[Dict[str, Any]]:
    rows = _require_list(value, label)
    validated = []
    for index, raw_row in enumerate(rows):
        row_label = f"{label}[{index}]"
        row = _require_object(raw_row, row_label)
        if row.get("group") != expected_group:
            raise ValueError(f"{row_label}.group must be {expected_group!r}")
        cost_type = _require_string(row.get("type"), f"{row_label}.type").lower()
        amount = _require_number(row.get("amount"), f"{row_label}.amount")
        normalized = {"group": expected_group, "type": cost_type, "amount": amount}
        if item:
            prefab = _require_string(row.get("prefab"), f"{row_label}.prefab").lower()
            if prefab != cost_type:
                raise ValueError(f"{row_label}.prefab must match type")
            normalized["prefab"] = prefab
        validated.append(normalized)
    return validated


def read_runtime_json_bytes(path: Path) -> bytes:
    """Return JSON bytes, removing DST's uncompressed persistent-file envelope."""

    raw = Path(path).read_bytes()
    if raw.startswith(b"KLEI"):
        match = PERSISTENT_HEADER.match(raw)
        if match is None:
            raise ValueError(f"invalid KLEI persistent header at {path}")
        raw = raw[match.end() :]
    return raw


def _validate_payload(data: Any) -> Dict[str, Any]:
    payload = _require_object(data, "runtime payload")
    missing = REQUIRED_KEYS - set(payload)
    if missing:
        raise ValueError(f"runtime payload missing keys: {sorted(missing)}")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {payload['schema_version']!r}; expected {SCHEMA_VERSION}"
        )
    _require_string(payload["mod_version"], "mod_version")
    _require_list(payload["recipes"], "recipes")
    _require_list(payload["prefabs"], "prefabs")
    _require_list(payload["errors"], "errors")
    return payload


def load_runtime_bundle(path: Path) -> FactBundle:
    """Validate a runtime export and convert it into provenance-aware facts."""

    path = Path(path)
    try:
        data = json.loads(read_runtime_json_bytes(path).decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid runtime JSON at {path}: {exc}") from exc
    payload = _validate_payload(data)
    source = SourceRef(
        "runtime-probe",
        "runtime_probe",
        _display_path(path),
        payload["mod_version"],
        _sha256(path),
    )
    facts: List[Fact] = []

    recipes = []
    for index, raw_recipe in enumerate(payload["recipes"]):
        recipe = _require_object(raw_recipe, f"recipes[{index}]")
        product = _require_string(recipe.get("product"), f"recipes[{index}].product").lower()
        ingredients = _validate_cost_rows(
            recipe.get("ingredients", []),
            f"recipes[{index}].ingredients",
            "item",
            item=True,
        )
        character_ingredients = _validate_cost_rows(
            recipe.get("character_ingredients", []),
            f"recipes[{index}].character_ingredients",
            "character",
        )
        tech_ingredients = _validate_cost_rows(
            recipe.get("tech_ingredients", []),
            f"recipes[{index}].tech_ingredients",
            "tech",
        )
        output_count = _require_number(
            recipe.get("output_count", 1), f"recipes[{index}].output_count"
        )
        tech = recipe.get("tech")
        if tech is not None and not isinstance(tech, str):
            raise ValueError(f"recipes[{index}].tech must be a string or null")
        filters = _require_string_list(
            recipe.get("filters", []), f"recipes[{index}].filters"
        )
        builder_tags = _require_string_list(
            recipe.get("builder_tags", []), f"recipes[{index}].builder_tags"
        )
        recipes.append(
            (
                product,
                index,
                ingredients,
                character_ingredients,
                tech_ingredients,
                output_count,
                tech,
                filters,
                builder_tags,
            )
        )
    for (
        product,
        index,
        ingredients,
        character_ingredients,
        tech_ingredients,
        output_count,
        tech,
        filters,
        builder_tags,
    ) in sorted(
        recipes, key=lambda value: (value[0], value[1])
    ):
        subject = EntityKey("tu_tien", product)
        facts.append(
            Fact(
                "entity",
                subject,
                {"entity_type": "unknown", "discovered_by": "runtime_recipe"},
                source,
                0.9,
                f"recipes:{index}",
            )
        )
        facts.append(
            Fact(
                "recipe",
                subject,
                {
                    "output_count": output_count,
                    "tech": tech,
                    "filters": filters,
                    "builder_tags": builder_tags,
                    "character_ingredients": character_ingredients,
                    "tech_ingredients": tech_ingredients,
                },
                source,
                1.0,
                f"recipes:{index}",
            )
        )
        facts.append(
            Fact(
                "acquisition",
                subject,
                {"type": "craft", "source": None, "chance": None, "conditions": {}},
                source,
                1.0,
                f"recipes:{index}",
            )
        )
        for position, ingredient in enumerate(ingredients):
            ingredient_id = ingredient["prefab"]
            amount = ingredient["amount"]
            facts.append(
                Fact(
                    "ingredient",
                    subject,
                    {
                        "position": position,
                        "amount": amount,
                        "ingredient": _runtime_reference(ingredient_id),
                    },
                    source,
                    1.0,
                    f"recipes:{index}:ingredients:{position}",
                )
            )

    prefabs = []
    for index, raw_prefab in enumerate(payload["prefabs"]):
        prefab = _require_object(raw_prefab, f"prefabs[{index}]")
        prefab_id = _require_string(
            prefab.get("prefab"), f"prefabs[{index}].prefab"
        ).lower()
        entity_type = prefab.get("entity_type", "unknown")
        _require_string(entity_type, f"prefabs[{index}].entity_type")
        prefabs.append((prefab_id, index, prefab))
    for prefab_id, index, prefab in sorted(prefabs, key=lambda value: (value[0], value[1])):
        subject = EntityKey("tu_tien", prefab_id)
        facts.append(
            Fact(
                "entity",
                subject,
                {
                    "entity_type": prefab.get("entity_type", "unknown"),
                    "discovered_by": "runtime_prefab",
                },
                source,
                1.0,
                f"prefabs:{index}",
            )
        )
        for stat_index, raw_stat in enumerate(
            _require_list(prefab.get("stats", []), f"prefabs[{index}].stats")
        ):
            stat = _require_object(raw_stat, f"prefabs[{index}].stats[{stat_index}]")
            _require_string(stat.get("key"), f"prefabs[{index}].stats[{stat_index}].key")
            stat_value = stat.get("value")
            if not isinstance(stat_value, (str, int, float, bool)):
                raise ValueError(
                    f"prefabs[{index}].stats[{stat_index}].value must be primitive"
                )
            unit = stat.get("unit")
            if unit is not None and not isinstance(unit, str):
                raise ValueError(
                    f"prefabs[{index}].stats[{stat_index}].unit must be a string or null"
                )
            facts.append(
                Fact(
                    "stat",
                    subject,
                    dict(stat),
                    source,
                    1.0,
                    f"prefabs:{index}:stats:{stat_index}",
                )
            )
        for group, acquisition_type in (("loot", "drop"), ("harvest", "harvest")):
            for item_index, raw_item in enumerate(
                _require_list(prefab.get(group, []), f"prefabs[{index}].{group}")
            ):
                item = _require_object(
                    raw_item, f"prefabs[{index}].{group}[{item_index}]"
                )
                target = _require_string(
                    item.get("prefab"),
                    f"prefabs[{index}].{group}[{item_index}].prefab",
                ).lower()
                chance = _require_number(
                    item.get("chance", 1),
                    f"prefabs[{index}].{group}[{item_index}].chance",
                )
                count = _require_number(
                    item.get("count", 1),
                    f"prefabs[{index}].{group}[{item_index}].count",
                )
                conditions = item.get("conditions", {})
                if conditions == []:
                    conditions = {}
                else:
                    conditions = _require_object(
                        conditions,
                        f"prefabs[{index}].{group}[{item_index}].conditions",
                    )
                facts.append(
                    Fact(
                        "acquisition",
                        subject,
                        {
                            "type": acquisition_type,
                            "source": {
                                "namespace": "tu_tien",
                                "prefab_id": prefab_id,
                            },
                            "target": _runtime_reference(target),
                            "chance": chance,
                            "count": count,
                            "conditions": conditions,
                        },
                        source,
                        1.0,
                        f"prefabs:{index}:{group}:{item_index}",
                    )
                )
        for relation_index, raw_relation in enumerate(
            _require_list(prefab.get("relations", []), f"prefabs[{index}].relations")
        ):
            relation = _require_object(
                raw_relation, f"prefabs[{index}].relations[{relation_index}]"
            )
            relation_type = _require_string(
                relation.get("relation"),
                f"prefabs[{index}].relations[{relation_index}].relation",
            )
            target = _require_string(
                relation.get("target_prefab_id"),
                f"prefabs[{index}].relations[{relation_index}].target_prefab_id",
            ).lower()
            facts.append(
                Fact(
                    "relation",
                    subject,
                    {
                        "relation": relation_type,
                        "target": _runtime_reference(target),
                    },
                    source,
                    1.0,
                    f"prefabs:{index}:relations:{relation_index}",
                )
            )

    facts.sort(
        key=lambda fact: (
            fact.kind,
            fact.subject.namespace,
            fact.subject.prefab_id,
            fact.locator,
            json.dumps(fact.payload, ensure_ascii=False, sort_keys=True),
        )
    )
    errors = []
    for index, error in enumerate(payload["errors"]):
        record = _require_object(error, f"errors[{index}]")
        for field in ("code", "prefab", "detail"):
            _require_string(record.get(field), f"errors[{index}].{field}")
        errors.append(dict(record))
    errors.sort(key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True))
    return FactBundle(SCHEMA_VERSION, [source], facts, errors)
