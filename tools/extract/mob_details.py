"""Build complete, phase-aware Mob and Boss detail contracts."""

from __future__ import annotations

import json
from typing import Any, Dict, Mapping, Optional, Sequence


JsonObject = Dict[str, Any]
STAT_LABELS = {
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
    "armor_absorption": "Giảm sát thương",
}
STAT_ORDER = {key: index for index, key in enumerate(STAT_LABELS)}


def _source_id(acquisition: Mapping[str, Any]) -> Optional[str]:
    source = acquisition.get("source")
    if isinstance(source, str):
        return source
    if isinstance(source, Mapping):
        namespace = source.get("namespace")
        prefab_id = source.get("prefab_id")
        if isinstance(namespace, str) and isinstance(prefab_id, str):
            return f"{namespace}:{prefab_id}"
    return None


def _format_number(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _format_chance(value: Any) -> Optional[str]:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    percent = float(value) * 100
    return f"{_format_number(round(percent, 4))}%"


def _group_index(groups: Sequence[JsonObject]) -> tuple[Dict[str, str], Dict[str, JsonObject]]:
    membership: Dict[str, str] = {}
    by_canonical: Dict[str, JsonObject] = {}
    for group in groups:
        canonical_id = str(group["canonicalId"])
        by_canonical[canonical_id] = group
        for member in group.get("members", []):
            membership[str(member["id"])] = canonical_id
    return membership, by_canonical


def _variant(item: JsonObject, role: str, order: int) -> JsonObject:
    return {
        "id": str(item["id"]),
        "prefabId": str(item.get("prefabId") or ""),
        "name": str(item.get("name") or item.get("prefabId") or item["id"]),
        "role": role,
        "order": order,
        "sprite": item.get("sprite"),
    }


def _evidence(value: Mapping[str, Any]) -> list[JsonObject]:
    evidence = value.get("evidence")
    return [dict(entry) for entry in evidence if isinstance(entry, Mapping)] if isinstance(evidence, list) else []


def build_mob_details(
    items: Sequence[JsonObject],
    entities: Sequence[JsonObject],
    wiki_details: Mapping[str, JsonObject],
    runtime_coverage: Sequence[JsonObject],
    groups: Sequence[JsonObject],
) -> Dict[str, JsonObject]:
    del runtime_coverage  # Absence is intentionally conservative until proven.
    item_by_id = {str(item["id"]): item for item in items}
    entity_by_id = {
        str(entity["key"]): entity
        for entity in entities
        if isinstance(entity, dict) and isinstance(entity.get("key"), str)
    }
    membership, groups_by_canonical = _group_index(groups)
    canonical_ids = {
        membership.get(str(item["id"]), str(item["id"]))
        for item in items
        if item.get("category") in ("mob", "boss") or str(item["id"]) in membership
    }
    output: Dict[str, JsonObject] = {}
    for canonical_id in sorted(canonical_ids):
        group = groups_by_canonical.get(canonical_id)
        if group is None:
            members = [{"id": canonical_id, "role": "variant", "order": 0}]
        else:
            members = sorted(
                group.get("members", []),
                key=lambda value: (value.get("order", 0), str(value.get("id"))),
            )
        member_ids = [str(member["id"]) for member in members]
        variants = [
            _variant(item_by_id[member_id], str(member["role"]), int(member["order"]))
            for member, member_id in zip(members, member_ids)
            if member_id in item_by_id
        ]
        stats = []
        mechanics = []
        for member_id in member_ids:
            entity = entity_by_id.get(member_id, {})
            for stat in entity.get("stats", []):
                if not isinstance(stat, Mapping):
                    continue
                key = stat.get("key")
                value = stat.get("value")
                if key == "special_states" and isinstance(value, str) and value.strip():
                    mechanics.append(
                        {
                            "text": "Trạng thái đặc biệt: " + value.strip(),
                            "sourceVariant": member_id,
                            "evidence": _evidence(stat),
                        }
                    )
                    continue
                if key not in STAT_LABELS or not isinstance(value, (str, int, float)) or isinstance(value, bool):
                    continue
                stats.append(
                    {
                        "key": str(key),
                        "label": STAT_LABELS[str(key)],
                        "value": value,
                        "unit": stat.get("unit") if isinstance(stat.get("unit"), str) else None,
                        "sourceVariant": member_id,
                        "evidence": _evidence(stat),
                    }
                )
        stats.sort(key=lambda value: (STAT_ORDER[value["key"]], value["sourceVariant"]))
        mechanics.sort(key=lambda value: (value["sourceVariant"], value["text"]))

        grouped_rewards: Dict[tuple[str, str, str, Any, str], JsonObject] = {}
        for target_id, target in entity_by_id.items():
            for acquisition in target.get("acquisition", []):
                if not isinstance(acquisition, Mapping) or acquisition.get("type") != "drop":
                    continue
                source_variant = _source_id(acquisition)
                if source_variant not in member_ids:
                    continue
                conditions = acquisition.get("conditions")
                conditions = dict(conditions) if isinstance(conditions, Mapping) else {}
                member = next(value for value in members if str(value["id"]) == source_variant)
                method = acquisition.get("method")
                if method not in {"kill", "mine_post_defeat", "harvest", "conditional"}:
                    method = "mine_post_defeat" if member.get("role") == "post_defeat" else "kill"
                minimum = acquisition.get("min_count", acquisition.get("count", 1))
                maximum = acquisition.get("max_count", minimum)
                minimum = minimum if isinstance(minimum, (int, float)) else 1
                maximum = maximum if isinstance(maximum, (int, float)) else minimum
                chance = acquisition.get("chance")
                loot_table = conditions.get("loot_table")
                conditions_text = f"Bảng rơi: {loot_table}" if isinstance(loot_table, str) else None
                key = (
                    target_id,
                    str(method),
                    source_variant,
                    chance if isinstance(chance, (int, float)) else None,
                    json.dumps(conditions, ensure_ascii=False, sort_keys=True),
                )
                row = grouped_rewards.setdefault(
                    key,
                    {
                        "item": {
                            "id": target_id,
                            "name": str(item_by_id.get(target_id, {}).get("name") or target.get("name", {}).get("vi") or target.get("prefab_id") or target_id),
                            "sprite": item_by_id.get(target_id, {}).get("sprite"),
                        },
                        "minimum": 0,
                        "maximum": 0,
                        "chance": _format_chance(chance),
                        "method": method,
                        "sourceVariant": source_variant,
                        "lootTable": loot_table if isinstance(loot_table, str) else None,
                        "conditions": conditions_text,
                        "evidence": _evidence(acquisition),
                    },
                )
                row["minimum"] += minimum
                row["maximum"] += maximum
        loot = [grouped_rewards[key] for key in sorted(grouped_rewards)]
        wiki = wiki_details.get(canonical_id, {})
        sources = wiki.get("sources") if isinstance(wiki, Mapping) else None
        sources = [str(value) for value in sources if isinstance(value, str)] if isinstance(sources, list) else []
        output[canonical_id] = {
            "appearance": {
                "status": "known" if sources else "unknown",
                "sources": sources,
                "spawnCodes": [item_by_id[member_id]["prefabId"] for member_id in member_ids if member_id in item_by_id],
                "renewable": None,
                "respawn": None,
                "wikiUrl": wiki.get("canonicalUrl") if isinstance(wiki, Mapping) else None,
                "evidence": _evidence(wiki) if isinstance(wiki, Mapping) else [],
            },
            "variants": variants,
            "stats": stats,
            "mechanics": mechanics,
            "lootStatus": "known" if loot else "unknown",
            "loot": loot,
        }
    return output


def build_mob_boss_audit(
    candidates: Sequence[JsonObject],
    details: Mapping[str, JsonObject],
    groups: Sequence[JsonObject],
) -> JsonObject:
    membership, _ = _group_index(groups)
    relevant = {
        str(item["id"]): item
        for item in candidates
        if item.get("category") in ("mob", "boss") or str(item["id"]) in membership
    }
    rows = []
    for item_id, item in sorted(relevant.items()):
        canonical_id = membership.get(item_id, item_id)
        action = "keep" if canonical_id == item_id else "merge"
        detail = details.get(canonical_id, {})
        rows.append(
            {
                "id": item_id,
                "canonicalId": canonical_id,
                "action": action,
                "originalCategory": item.get("category"),
                "finalCategory": item_by_category(canonical_id, candidates),
                "hasStats": bool(detail.get("stats")),
                "hasMechanics": bool(detail.get("mechanics")),
                "lootStatus": detail.get("lootStatus", "unknown"),
                "reason": "Giữ làm record Mob/Boss chính." if action == "keep" else "Gộp vào record Mob/Boss chính theo manifest biến thể.",
            }
        )
    summary = {
        "total": len(rows),
        "keep": sum(row["action"] == "keep" for row in rows),
        "merge": sum(row["action"] == "merge" for row in rows),
        "exclude": sum(row["action"] == "exclude" for row in rows),
    }
    return {"schema_version": 1, "summary": summary, "rows": rows}


def item_by_category(item_id: str, items: Sequence[JsonObject]) -> Optional[str]:
    return next(
        (str(item.get("category")) for item in items if item.get("id") == item_id),
        None,
    )
