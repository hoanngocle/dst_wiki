from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef


SOURCE_PRIORITY = {
    "runtime_probe": 400,
    "mod_static": 300,
    "base_game_source": 300,
    "handbook_image": 300,
    "mod_translation": 200,
    "manual_review": 100,
}


def _json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _identifier(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _entity_id(key: EntityKey) -> str:
    return f"{key.namespace}:{key.prefab_id}"


def fact_rank(fact: Fact) -> Tuple[int, float, str, str, str]:
    return (
        SOURCE_PRIORITY.get(fact.source.kind, 0),
        fact.confidence,
        fact.source.source_id,
        fact.locator,
        _json(fact.payload),
    )


@dataclass
class NormalizedCatalog:
    sources: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    recipes: List[Dict[str, Any]] = field(default_factory=list)
    recipe_ingredients: List[Dict[str, Any]] = field(default_factory=list)
    acquisition_sources: List[Dict[str, Any]] = field(default_factory=list)
    stats: List[Dict[str, Any]] = field(default_factory=list)
    effects: List[Dict[str, Any]] = field(default_factory=list)
    runtime_coverage: List[Dict[str, Any]] = field(default_factory=list)
    entity_relations: List[Dict[str, Any]] = field(default_factory=list)
    assets: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    extraction_errors: List[Dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class _Candidate:
    index: int
    fact: Fact


def _fact_sort_key(fact: Fact) -> Tuple[str, ...]:
    return (
        fact.subject.namespace,
        fact.subject.prefab_id,
        fact.kind,
        fact.source.source_id,
        fact.source.kind,
        fact.locator,
        _json(fact.payload),
        str(fact.confidence),
    )


def _choose(candidates: Sequence[_Candidate]) -> _Candidate:
    return max(candidates, key=lambda candidate: fact_rank(candidate.fact))


def _candidate_description(candidate: _Candidate, value: Any) -> Dict[str, Any]:
    fact = candidate.fact
    return {
        "value": value,
        "source_id": fact.source.source_id,
        "source_kind": fact.source.kind,
        "locator": fact.locator,
        "confidence": fact.confidence,
    }


def _add_conflict(
    catalog: NormalizedCatalog,
    subject: EntityKey,
    field_key: str,
    candidates: Sequence[_Candidate],
    selected: _Candidate,
    value_for,
) -> None:
    values = {_json(value_for(candidate.fact)) for candidate in candidates}
    if len(values) < 2:
        return
    candidate_rows = [
        _candidate_description(candidate, value_for(candidate.fact))
        for candidate in sorted(candidates, key=lambda item: fact_rank(item.fact))
    ]
    selected_row = _candidate_description(selected, value_for(selected.fact))
    conflict_key = {
        "subject": _entity_id(subject),
        "field": field_key,
        "candidates": candidate_rows,
        "selected": selected_row,
    }
    catalog.conflicts.append(
        {
            "conflict_id": _identifier(conflict_key),
            "subject_key": _entity_id(subject),
            "field_key": field_key,
            "candidates_json": _json(candidate_rows),
            "selected_json": _json(selected_row["value"]),
        }
    )


def _reference_payload(payload: Dict[str, Any], field: str) -> Optional[Dict[str, Any]]:
    value = payload.get(field)
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        return {"prefab_id": value}
    if field == "target" and isinstance(payload.get("target_prefab_id"), str):
        return {
            "prefab_id": payload["target_prefab_id"],
            "dependency_candidate": payload.get("dependency_candidate"),
            "resolution": payload.get("resolution"),
        }
    return None


def _resolve_reference(
    reference: Dict[str, Any],
    entities: Iterable[EntityKey],
    context: str,
) -> EntityKey:
    entity_set = set(entities)
    prefab_id = reference.get("prefab_id") or reference.get("target_prefab_id")
    if not isinstance(prefab_id, str) or not prefab_id:
        raise ValueError(f"{context} has no prefab_id")
    prefab_id = prefab_id.lower()
    namespace = reference.get("namespace")
    if namespace is not None:
        key = EntityKey(str(namespace), prefab_id)
        if key not in entity_set:
            raise ValueError(f"{context} does not resolve existing entity {_entity_id(key)}")
        return key
    matches = sorted(key for key in entity_set if key.prefab_id == prefab_id)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        preferred = EntityKey("tu_tien", prefab_id)
        if prefab_id.startswith("xd_") and preferred in matches:
            return preferred
        raise ValueError(f"{context} is ambiguous for prefab_id {prefab_id}")
    raise ValueError(f"{context} does not resolve existing entity {prefab_id}")


def _optional_reference(
    reference: Optional[Dict[str, Any]], entities: Iterable[EntityKey]
) -> Optional[EntityKey]:
    if reference is None:
        return None
    if reference.get("resolution") == "evidence_only":
        return None
    return _resolve_reference(reference, entities, "acquisition source")


def _stat_value(payload: Dict[str, Any]) -> Dict[str, Any]:
    value = payload.get("value")
    if value is None and "source_expression" in payload:
        value = payload["source_expression"]
    return {"value": value, "unit": payload.get("unit")}


def _ingredient_value(fact: Fact) -> Dict[str, Any]:
    return {
        "ingredient": _reference_payload(fact.payload, "ingredient"),
        "amount": fact.payload.get("amount"),
    }


def _entity_type(value: Any) -> str:
    return "inventory_item" if value == "item" else str(value or "unknown")


def _bundle_identifier(index: int, bundle: FactBundle) -> str:
    return _identifier(
        {
            "index": index,
            "schema_version": bundle.schema_version,
            "sources": [
                {
                    "source_id": source.source_id,
                    "kind": source.kind,
                    "path": source.path,
                    "version": source.version,
                    "sha256": source.sha256,
                }
                for source in sorted(bundle.sources)
            ],
        }
    )


def _error_source(
    error: Dict[str, Any], sources: Sequence[SourceRef]
) -> Optional[SourceRef]:
    source_id = error.get("source_id")
    if isinstance(source_id, str):
        matches = [source for source in sources if source.source_id == source_id]
        if len(matches) == 1:
            return matches[0]
    path = error.get("path")
    if isinstance(path, str):
        matches = [source for source in sources if source.path == path]
        if len(matches) == 1:
            return matches[0]
    if len(sources) == 1:
        return sources[0]
    return None


def _error_locator(error: Dict[str, Any]) -> str:
    locator = error.get("locator")
    if isinstance(locator, str):
        return locator
    path = error.get("path")
    line = error.get("line")
    if isinstance(path, str) and isinstance(line, (int, str)) and not isinstance(line, bool):
        return f"{path}:line:{line}"
    return path if isinstance(path, str) else ""


def normalize(bundles: Sequence[FactBundle]) -> NormalizedCatalog:
    """Merge extractor facts without discarding provenance or conflicts."""

    catalog = NormalizedCatalog()
    source_map: Dict[str, SourceRef] = {}
    all_facts: List[Fact] = []
    error_rows: List[Tuple[str, Sequence[SourceRef], Dict[str, Any]]] = []
    for bundle_index, bundle in enumerate(bundles):
        if bundle.schema_version != 1:
            raise ValueError(f"unsupported fact schema_version {bundle.schema_version!r}")
        for source in bundle.sources:
            previous = source_map.get(source.source_id)
            if previous is not None and previous != source:
                raise ValueError(f"conflicting source metadata for {source.source_id}")
            source_map[source.source_id] = source
        for fact in bundle.facts:
            previous = source_map.get(fact.source.source_id)
            if previous is not None and previous != fact.source:
                raise ValueError(f"conflicting source metadata for {fact.source.source_id}")
            source_map[fact.source.source_id] = fact.source
            all_facts.append(fact)
        bundle_id = _bundle_identifier(bundle_index, bundle)
        for error in bundle.errors:
            error_rows.append((bundle_id, tuple(sorted(bundle.sources)), dict(error)))

    catalog.sources = [
        {
            "source_id": source.source_id,
            "kind": source.kind,
            "path": source.path,
            "version": source.version,
            "sha256": source.sha256,
        }
        for source in sorted(source_map.values())
    ]

    sorted_facts = sorted(all_facts, key=_fact_sort_key)
    candidates = [_Candidate(index, fact) for index, fact in enumerate(sorted_facts)]
    supported = {
        "entity",
        "name",
        "description",
        "recipe",
        "ingredient",
        "acquisition",
        "stat",
        "effect",
        "coverage",
        "relation",
        "asset",
    }
    unknown = sorted({candidate.fact.kind for candidate in candidates} - supported)
    if unknown:
        raise ValueError(f"unsupported fact kinds: {unknown}")

    entity_keys = {
        candidate.fact.subject
        for candidate in candidates
        if not (
            candidate.fact.kind == "asset"
            and candidate.fact.payload.get("asset_type") == "handbook_image"
        )
    }
    selected: Dict[int, bool] = {candidate.index: False for candidate in candidates}
    evidence_record: Dict[int, Tuple[str, str]] = {}

    by_subject: Dict[EntityKey, List[_Candidate]] = {}
    for candidate in candidates:
        by_subject.setdefault(candidate.fact.subject, []).append(candidate)

    entity_type_groups: Dict[EntityKey, List[_Candidate]] = {}
    name_groups: Dict[Tuple[EntityKey, str], List[_Candidate]] = {}
    description_groups: Dict[Tuple[EntityKey, str], List[_Candidate]] = {}
    chosen_names: Dict[Tuple[EntityKey, str], Any] = {}
    chosen_descriptions: Dict[Tuple[EntityKey, str], Any] = {}
    chosen_types: Dict[EntityKey, str] = {}

    for candidate in candidates:
        fact = candidate.fact
        record_id = _entity_id(fact.subject)
        if fact.kind == "entity":
            entity_type_groups.setdefault(fact.subject, []).append(candidate)
            evidence_record[candidate.index] = ("entity", record_id)
        elif fact.kind == "name":
            lang = str(fact.payload.get("lang", ""))
            name_groups.setdefault((fact.subject, lang), []).append(candidate)
            evidence_record[candidate.index] = ("name", record_id)
        elif fact.kind == "description":
            lang = str(fact.payload.get("lang", ""))
            description_groups.setdefault((fact.subject, lang), []).append(candidate)
            evidence_record[candidate.index] = ("description", record_id)

    for key, group in entity_type_groups.items():
        winner = _choose(group)
        selected[winner.index] = True
        chosen_types[key] = _entity_type(winner.fact.payload.get("entity_type"))
        _add_conflict(
            catalog,
            key,
            "entity_type",
            group,
            winner,
            lambda fact: _entity_type(fact.payload.get("entity_type")),
        )
    for (key, lang), group in name_groups.items():
        winner = _choose(group)
        selected[winner.index] = True
        chosen_names[(key, lang)] = winner.fact.payload.get("value")
        _add_conflict(catalog, key, f"name:{lang}", group, winner, lambda fact: fact.payload.get("value"))
    for (key, lang), group in description_groups.items():
        winner = _choose(group)
        selected[winner.index] = True
        chosen_descriptions[(key, lang)] = winner.fact.payload.get("value")
        _add_conflict(catalog, key, f"description:{lang}", group, winner, lambda fact: fact.payload.get("value"))

    inventory_assets = {
        candidate.fact.subject
        for candidate in candidates
        if candidate.fact.kind == "asset"
        and candidate.fact.payload.get("asset_type") == "inventory"
        and candidate.fact.payload.get("available", True)
    }
    for key in sorted(entity_keys):
        entity_type = chosen_types.get(key, "unknown")
        is_inventory = entity_type == "inventory_item" or key in inventory_assets
        if is_inventory and entity_type == "unknown":
            entity_type = "inventory_item"
        confidence = max(
            (candidate.fact.confidence for candidate in by_subject.get(key, [])),
            default=0.0,
        )
        catalog.entities.append(
            {
                "namespace": key.namespace,
                "prefab_id": key.prefab_id,
                "entity_type": entity_type,
                "is_inventory_item": int(is_inventory),
                "name_vi": chosen_names.get((key, "vi")),
                "name_en": chosen_names.get((key, "en")),
                "description_vi": chosen_descriptions.get((key, "vi")),
                "description_en": chosen_descriptions.get((key, "en")),
                "icon_key": _entity_id(key) if key in inventory_assets else None,
                "confidence": confidence,
            }
        )

    recipe_groups: Dict[EntityKey, List[_Candidate]] = {}
    ingredient_groups: Dict[Tuple[EntityKey, int], List[_Candidate]] = {}
    stat_groups: Dict[Tuple[EntityKey, str], List[_Candidate]] = {}
    for candidate in candidates:
        fact = candidate.fact
        if fact.kind == "recipe":
            recipe_groups.setdefault(fact.subject, []).append(candidate)
        elif fact.kind == "ingredient":
            position = fact.payload.get("position")
            if (
                not isinstance(position, int)
                or isinstance(position, bool)
                or position < 0
            ):
                raise ValueError(
                    f"recipe ingredient for {_entity_id(fact.subject)} "
                    "requires a non-negative integer position"
                )
            ingredient_groups.setdefault((fact.subject, position), []).append(candidate)
        elif fact.kind == "stat":
            stat_key = fact.payload.get("key")
            if not isinstance(stat_key, str) or not stat_key:
                raise ValueError(f"stat for {_entity_id(fact.subject)} has no key")
            stat_groups.setdefault((fact.subject, stat_key), []).append(candidate)

    for key, group in sorted(recipe_groups.items()):
        winner = _choose(group)
        selected[winner.index] = True
        payload = winner.fact.payload
        output_count = payload.get("output_count", 1)
        if (
            not isinstance(output_count, int)
            or isinstance(output_count, bool)
            or output_count <= 0
        ):
            raise ValueError(
                f"recipe {_entity_id(key)} requires a positive integer output_count"
            )
        recipe_id = _entity_id(key)
        restrictions = {
            field: value
            for field, value in payload.items()
            if field not in {"output_count", "tech", "tech_expression"}
        }
        catalog.recipes.append(
            {
                "recipe_id": recipe_id,
                "product_namespace": key.namespace,
                "product_id": key.prefab_id,
                "output_count": output_count,
                "tech": payload.get("tech") or payload.get("tech_expression"),
                "restrictions_json": _json(restrictions),
            }
        )
        for candidate in group:
            evidence_record[candidate.index] = ("recipe", recipe_id)
        _add_conflict(catalog, key, "recipe", group, winner, lambda fact: fact.payload)

    recipe_ids = {row["recipe_id"] for row in catalog.recipes}
    for (product, position), group in sorted(ingredient_groups.items()):
        recipe_id = _entity_id(product)
        if recipe_id not in recipe_ids:
            raise ValueError(f"recipe ingredient exists without recipe {recipe_id}")
        winner = _choose(group)
        reference = _reference_payload(winner.fact.payload, "ingredient")
        if reference is None:
            raise ValueError(f"recipe ingredient for {recipe_id} has no ingredient reference")
        try:
            ingredient = _resolve_reference(reference, entity_keys, "recipe ingredient")
        except ValueError as exc:
            raw_id = reference.get("prefab_id") or reference.get("target_prefab_id")
            raw_namespace = reference.get("namespace")
            label = f"{raw_namespace}:{raw_id}" if raw_namespace else str(raw_id)
            raise ValueError(f"recipe ingredient {label} for {recipe_id} does not resolve") from exc
        amount = winner.fact.payload.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError(f"recipe ingredient {_entity_id(ingredient)} for {recipe_id} has non-numeric amount")
        selected[winner.index] = True
        record_id = f"{recipe_id}:{position}"
        catalog.recipe_ingredients.append(
            {
                "recipe_id": recipe_id,
                "position": position,
                "ingredient_namespace": ingredient.namespace,
                "ingredient_id": ingredient.prefab_id,
                "amount": amount,
            }
        )
        for candidate in group:
            evidence_record[candidate.index] = ("recipe_ingredient", record_id)
        _add_conflict(catalog, product, f"ingredient:{position}", group, winner, _ingredient_value)

    for (key, stat_key), group in sorted(stat_groups.items()):
        winner = _choose(group)
        selected[winner.index] = True
        semantic = _stat_value(winner.fact.payload)
        value = semantic["value"]
        value_num = None
        value_text = None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            value_num = value
        elif value is not None:
            value_text = value if isinstance(value, str) else _json(value)
        record_id = f"{_entity_id(key)}:stat:{stat_key}"
        catalog.stats.append(
            {
                "namespace": key.namespace,
                "prefab_id": key.prefab_id,
                "stat_key": stat_key,
                "value_num": value_num,
                "value_text": value_text,
                "unit": semantic["unit"],
                "confidence": winner.fact.confidence,
            }
        )
        for candidate in group:
            evidence_record[candidate.index] = ("stat", record_id)
        _add_conflict(catalog, key, f"stat:{stat_key}", group, winner, lambda fact: _stat_value(fact.payload))

    semantic_groups: Dict[Tuple[str, str], List[_Candidate]] = {}
    semantic_rows: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for candidate in candidates:
        fact = candidate.fact
        if fact.kind == "acquisition":
            target_ref = _reference_payload(fact.payload, "target")
            target = (
                _resolve_reference(target_ref, entity_keys, "acquisition target")
                if target_ref is not None
                else fact.subject
            )
            if target not in entity_keys:
                raise ValueError(f"acquisition target {_entity_id(target)} is not selected")
            source_ref = _reference_payload(fact.payload, "source")
            source_key = _optional_reference(source_ref, entity_keys)
            conditions = dict(fact.payload.get("conditions") or {})
            fixed = {"type", "source", "target", "chance", "count", "min_count", "max_count", "conditions"}
            for field, value in fact.payload.items():
                if field not in fixed:
                    conditions[field] = value
            if source_ref is not None and source_key is None:
                conditions["source_identity"] = source_ref
            count = fact.payload.get("count")
            row = {
                "target_namespace": target.namespace,
                "target_id": target.prefab_id,
                "source_type": str(fact.payload.get("type") or "unknown"),
                "source_namespace": source_key.namespace if source_key else None,
                "source_id": source_key.prefab_id if source_key else None,
                "chance": fact.payload.get("chance"),
                "min_count": fact.payload.get("min_count", count),
                "max_count": fact.payload.get("max_count", count),
                "conditions_json": _json(conditions),
            }
            semantic = _json(row)
            semantic_groups.setdefault(("acquisition", semantic), []).append(candidate)
            semantic_rows[("acquisition", semantic)] = row
        elif fact.kind == "relation":
            target_ref = _reference_payload(fact.payload, "target")
            if target_ref is None:
                raise ValueError(f"relation for {_entity_id(fact.subject)} has no target")
            target = _resolve_reference(target_ref, entity_keys, "relation target")
            relation_type = fact.payload.get("relation")
            if not isinstance(relation_type, str) or not relation_type:
                raise ValueError(f"relation for {_entity_id(fact.subject)} has no relation type")
            metadata = {
                field: value
                for field, value in fact.payload.items()
                if field not in {"relation", "target", "target_prefab_id"}
            }
            row = {
                "from_namespace": fact.subject.namespace,
                "from_id": fact.subject.prefab_id,
                "relation_type": relation_type,
                "to_namespace": target.namespace,
                "to_id": target.prefab_id,
                "metadata_json": _json(metadata),
            }
            semantic = _json(row)
            semantic_groups.setdefault(("relation", semantic), []).append(candidate)
            semantic_rows[("relation", semantic)] = row
        elif fact.kind == "asset":
            linked = fact.subject if fact.subject in entity_keys else None
            payload = fact.payload
            row = {
                "namespace": fact.subject.namespace,
                "prefab_id": linked.prefab_id if linked else None,
                "asset_type": str(payload.get("asset_type") or "unknown"),
                "atlas": payload.get("atlas"),
                "texture": str(payload.get("texture") or ""),
                "element": payload.get("element"),
                "uv_json": _json(payload["uv"]) if payload.get("uv") is not None else None,
            }
            semantic = _json(row)
            semantic_groups.setdefault(("asset", semantic), []).append(candidate)
            semantic_rows[("asset", semantic)] = row
        elif fact.kind == "effect":
            payload = fact.payload
            effect_key = payload.get("effect_key") or payload.get("key")
            if not isinstance(effect_key, str) or not effect_key:
                raise ValueError(f"effect for {_entity_id(fact.subject)} has no effect key")
            value = payload.get("value", payload.get("value_json"))
            row = {
                "namespace": fact.subject.namespace,
                "prefab_id": fact.subject.prefab_id,
                "trigger_name": payload.get("trigger") or payload.get("trigger_name"),
                "effect_key": effect_key,
                "value_json": value if isinstance(value, str) and payload.get("value_json") is not None else _json(value),
                "duration": payload.get("duration"),
            }
            semantic = _json(row)
            semantic_groups.setdefault(("effect", semantic), []).append(candidate)
            semantic_rows[("effect", semantic)] = row
        elif fact.kind == "coverage":
            payload = fact.payload
            category = payload.get("category")
            status = payload.get("status")
            reason = payload.get("reason")
            details = payload.get("details", {})
            if not isinstance(category, str) or not category:
                raise ValueError(
                    f"coverage for {_entity_id(fact.subject)} has no category"
                )
            if status not in {"observed", "unobserved", "unsupported"}:
                raise ValueError(
                    f"coverage for {_entity_id(fact.subject)} has invalid status"
                )
            if not isinstance(reason, str) or not reason:
                raise ValueError(
                    f"coverage for {_entity_id(fact.subject)} has no reason"
                )
            if not isinstance(details, dict):
                raise ValueError(
                    f"coverage for {_entity_id(fact.subject)} details must be an object"
                )
            row = {
                "namespace": fact.subject.namespace,
                "prefab_id": fact.subject.prefab_id,
                "category": category,
                "status": status,
                "reason": reason,
                "details_json": _json(details),
            }
            semantic = _json(row)
            semantic_groups.setdefault(("coverage", semantic), []).append(candidate)
            semantic_rows[("coverage", semantic)] = row

    for semantic_key, group in sorted(semantic_groups.items()):
        kind, semantic = semantic_key
        row = dict(semantic_rows[semantic_key])
        record_id = _identifier({"kind": kind, "row": row})
        if kind == "acquisition":
            row["acquisition_id"] = record_id
            catalog.acquisition_sources.append(row)
        elif kind == "relation":
            row["relation_id"] = record_id
            catalog.entity_relations.append(row)
        elif kind == "asset":
            row["asset_id"] = record_id
            catalog.assets.append(row)
        elif kind == "coverage":
            row["coverage_id"] = record_id
            catalog.runtime_coverage.append(row)
        else:
            row["effect_id"] = record_id
            catalog.effects.append(row)
        for candidate in group:
            selected[candidate.index] = True
            evidence_record[candidate.index] = (kind, record_id)

    signature_counts: Dict[str, int] = {}
    for candidate in candidates:
        fact = candidate.fact
        record = evidence_record.get(candidate.index)
        if record is None:
            raise ValueError(f"fact kind {fact.kind} has no normalized evidence record")
        signature = _json(
            {
                "kind": fact.kind,
                "subject": {"namespace": fact.subject.namespace, "prefab_id": fact.subject.prefab_id},
                "payload": fact.payload,
                "source_id": fact.source.source_id,
                "locator": fact.locator,
                "confidence": fact.confidence,
            }
        )
        duplicate = signature_counts.get(signature, 0)
        signature_counts[signature] = duplicate + 1
        catalog.evidence.append(
            {
                "evidence_id": _identifier({"signature": signature, "duplicate": duplicate}),
                "record_type": record[0],
                "record_id": record[1],
                "source_id": fact.source.source_id,
                "locator": fact.locator,
                "raw_value_json": _json(fact.payload),
                "confidence": fact.confidence,
                "selected": int(selected[candidate.index]),
            }
        )

    error_occurrences: Dict[Tuple[str, str], int] = {}
    for bundle_id in sorted({row[0] for row in error_rows}):
        signatures = sorted(
            {
                _json(error)
                for row_bundle_id, _sources, error in error_rows
                if row_bundle_id == bundle_id
            }
        )
        for occurrence, signature in enumerate(signatures):
            error_occurrences[(bundle_id, signature)] = occurrence

    normalized_errors: Dict[str, Dict[str, Any]] = {}
    for bundle_id, sources, error in sorted(
        error_rows, key=lambda row: (row[0], _json(row[2]))
    ):
        payload_json = _json(error)
        source = _error_source(error, sources)
        source_id = source.source_id if source is not None else None
        source_kind = source.kind if source is not None else "bundle"
        locator = _error_locator(error)
        occurrence = error_occurrences[(bundle_id, payload_json)]
        error_id = _identifier(
            {
                "bundle_id": bundle_id,
                "source_id": source_id,
                "locator": locator,
                "occurrence": occurrence,
                "payload": error,
            }
        )
        normalized_errors[error_id] = {
            "error_id": error_id,
            "bundle_id": bundle_id,
            "source_id": source_id,
            "source_kind": source_kind,
            "locator": locator,
            "occurrence": occurrence,
            "code": str(error.get("code") or "unknown"),
            "payload_json": payload_json,
        }
    catalog.extraction_errors.extend(normalized_errors.values())

    for field_name in (
        "entities",
        "recipes",
        "recipe_ingredients",
        "acquisition_sources",
        "stats",
        "effects",
        "runtime_coverage",
        "entity_relations",
        "assets",
        "evidence",
        "conflicts",
        "extraction_errors",
    ):
        rows = getattr(catalog, field_name)
        rows.sort(key=lambda row: _json(row))
    return catalog
