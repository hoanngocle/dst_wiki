import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef


RUNTIME_SCHEMA_VERSION = 2
FACT_SCHEMA_VERSION = 1
REQUIRED_KEYS = {
    "schema_version",
    "mod_version",
    "targets",
    "recipes",
    "prefabs",
    "coverage",
    "errors",
}
COVERAGE_CATEGORIES = {
    "buff_debuff",
    "cooldown_recharge",
    "craft",
    "drop",
    "harvest",
    "progression",
    "start_gift",
    "trade_shop",
    "world_spawn",
}
COVERAGE_STATUSES = {"observed", "unobserved", "unsupported"}
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


def _runtime_reference(prefab_id: str, mod_prefabs: Set[str]) -> Dict[str, Any]:
    if prefab_id in mod_prefabs:
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
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError(
            "unsupported schema_version: "
            f"{payload['schema_version']!r}; expected {RUNTIME_SCHEMA_VERSION}"
        )
    _require_string(payload["mod_version"], "mod_version")
    _require_list(payload["targets"], "targets")
    _require_list(payload["recipes"], "recipes")
    _require_list(payload["prefabs"], "prefabs")
    _require_list(payload["coverage"], "coverage")
    _require_list(payload["errors"], "errors")
    return payload


def static_mod_version(bundle: FactBundle) -> str:
    """Return the single Tu Tien version represented by static source facts."""

    versions = {source.version for source in bundle.sources if source.kind == "mod_static"}
    if len(versions) != 1:
        raise ValueError(
            f"static facts must contain exactly one mod_static version, found {sorted(versions)}"
        )
    return next(iter(versions))


def load_runtime_bundle(
    path: Path,
    expected_mod_version: Optional[str] = None,
    expected_targets: Optional[List[str]] = None,
) -> FactBundle:
    """Validate a runtime export and convert it into provenance-aware facts."""

    path = Path(path)
    try:
        data = json.loads(read_runtime_json_bytes(path).decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid runtime JSON at {path}: {exc}") from exc
    payload = _validate_payload(data)
    if (
        expected_mod_version is not None
        and payload["mod_version"] != expected_mod_version
    ):
        raise ValueError(
            f"runtime mod_version {payload['mod_version']} does not match "
            f"static mod version {expected_mod_version}"
        )
    source = SourceRef(
        "runtime-probe",
        "runtime_probe",
        _display_path(path),
        payload["mod_version"],
        _sha256(path),
    )
    facts: List[Fact] = []

    targets = [
        _require_string(value, f"targets[{index}]").lower()
        for index, value in enumerate(payload["targets"])
    ]
    if targets != sorted(set(targets)):
        raise ValueError("targets must be sorted and unique")
    if expected_targets is not None:
        missing_targets = sorted(set(expected_targets) - set(targets))
        if missing_targets:
            raise ValueError(
                "runtime targets are missing static allowlist entries: "
                f"{missing_targets}"
            )
    mod_prefabs = set(targets)
    for index, prefab_id in enumerate(targets):
        facts.append(
            Fact(
                "entity",
                EntityKey("tu_tien", prefab_id),
                {"entity_type": "unknown", "discovered_by": "runtime_target_allowlist"},
                source,
                0.9,
                f"targets:{index}",
            )
        )

    recipes = []
    for index, raw_recipe in enumerate(payload["recipes"]):
        recipe = _require_object(raw_recipe, f"recipes[{index}]")
        product = _require_string(recipe.get("product"), f"recipes[{index}].product").lower()
        if product not in mod_prefabs:
            raise ValueError(f"recipes[{index}].product is not in targets")
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
                        "ingredient": _runtime_reference(ingredient_id, mod_prefabs),
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
        if prefab_id not in mod_prefabs:
            raise ValueError(f"prefabs[{index}].prefab is not in targets")
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
        for group, acquisition_type in (
            ("loot", "drop"),
            ("harvest", "harvest"),
            ("trade", "trade"),
        ):
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
                            "target": _runtime_reference(target, mod_prefabs),
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
                        "target": _runtime_reference(target, mod_prefabs),
                    },
                    source,
                    1.0,
                    f"prefabs:{index}:relations:{relation_index}",
                )
            )

        for effect_index, raw_effect in enumerate(
            _require_list(prefab.get("effects", []), f"prefabs[{index}].effects")
        ):
            effect = _require_object(
                raw_effect, f"prefabs[{index}].effects[{effect_index}]"
            )
            effect_key = _require_string(
                effect.get("effect_key"),
                f"prefabs[{index}].effects[{effect_index}].effect_key",
            )
            trigger = effect.get("trigger")
            if trigger is not None and not isinstance(trigger, str):
                raise ValueError(
                    f"prefabs[{index}].effects[{effect_index}].trigger "
                    "must be a string or null"
                )
            duration = effect.get("duration")
            if duration is not None:
                _require_number(
                    duration, f"prefabs[{index}].effects[{effect_index}].duration"
                )
            facts.append(
                Fact(
                    "effect",
                    subject,
                    {
                        "effect_key": effect_key,
                        "trigger": trigger,
                        "value": effect.get("value"),
                        "duration": duration,
                    },
                    source,
                    1.0,
                    f"prefabs:{index}:effects:{effect_index}",
                )
            )

    coverage_pairs = set()
    for index, raw_coverage in enumerate(payload["coverage"]):
        row = _require_object(raw_coverage, f"coverage[{index}]")
        prefab_id = _require_string(
            row.get("prefab"), f"coverage[{index}].prefab"
        ).lower()
        if prefab_id not in mod_prefabs:
            raise ValueError(f"coverage[{index}].prefab is not in targets")
        category = _require_string(
            row.get("category"), f"coverage[{index}].category"
        )
        if category not in COVERAGE_CATEGORIES:
            raise ValueError(f"coverage[{index}].category is unsupported")
        status = _require_string(row.get("status"), f"coverage[{index}].status")
        if status not in COVERAGE_STATUSES:
            raise ValueError(f"coverage[{index}].status is unsupported")
        reason = _require_string(row.get("reason"), f"coverage[{index}].reason")
        details = row.get("details", {})
        if details == []:
            details = {}
        else:
            details = _require_object(details, f"coverage[{index}].details")
        pair = (prefab_id, category)
        if pair in coverage_pairs:
            raise ValueError(f"duplicate runtime coverage row for {prefab_id}:{category}")
        coverage_pairs.add(pair)
        facts.append(
            Fact(
                "coverage",
                EntityKey("tu_tien", prefab_id),
                {
                    "category": category,
                    "status": status,
                    "reason": reason,
                    "details": details,
                },
                source,
                1.0,
                f"coverage:{index}",
            )
        )
        if category == "start_gift" and status == "observed":
            registry_paths = _require_string_list(
                details.get("paths"), f"coverage[{index}].details.paths"
            )
            count = _require_number(
                details.get("count"), f"coverage[{index}].details.count"
            )
            facts.append(
                Fact(
                    "acquisition",
                    EntityKey("tu_tien", prefab_id),
                    {
                        "type": "start",
                        "source": None,
                        "chance": 1,
                        "count": count,
                        "conditions": {"registry_paths": registry_paths},
                    },
                    source,
                    1.0,
                    f"coverage:{index}:start",
                )
            )
    expected_pairs = {
        (prefab_id, category)
        for prefab_id in targets
        for category in COVERAGE_CATEGORIES
    }
    if coverage_pairs != expected_pairs:
        missing = sorted(expected_pairs - coverage_pairs)
        extra = sorted(coverage_pairs - expected_pairs)
        raise ValueError(
            f"runtime coverage matrix is incomplete; missing={missing} extra={extra}"
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
    return FactBundle(FACT_SCHEMA_VERSION, [source], facts, errors)
