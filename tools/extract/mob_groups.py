from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


JsonObject = Dict[str, Any]
ALLOWED_CATEGORIES = {"mob", "boss"}
ALLOWED_ROLES = {"phase", "variant", "summon", "post_defeat"}


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"mob group {field} must be a non-empty string")
    return value


def _validated_group(group: Any) -> JsonObject:
    if not isinstance(group, dict):
        raise ValueError("mob group must be an object")
    canonical_id = _required_string(group.get("canonicalId"), "canonicalId")
    category = _required_string(group.get("category"), "category")
    if category not in ALLOWED_CATEGORIES:
        raise ValueError(f"mob group {canonical_id} category is invalid")
    members = group.get("members")
    if not isinstance(members, list):
        raise ValueError(f"mob group {canonical_id} members must be an array")
    validated_members = []
    for member in members:
        if not isinstance(member, dict):
            raise ValueError(f"mob group {canonical_id} member must be an object")
        member_id = _required_string(member.get("id"), "member id")
        role = _required_string(member.get("role"), "member role")
        order = member.get("order")
        if role not in ALLOWED_ROLES:
            raise ValueError(f"mob group member {member_id} role is invalid")
        if not isinstance(order, int) or isinstance(order, bool) or order < 0:
            raise ValueError(f"mob group member {member_id} order is invalid")
        validated_members.append({"id": member_id, "role": role, "order": order})
    return {
        "canonicalId": canonical_id,
        "category": category,
        "members": sorted(
            validated_members, key=lambda value: (value["order"], value["id"])
        ),
    }


def load_mob_groups(path: Path) -> List[JsonObject]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 1
        or not isinstance(payload.get("groups"), list)
    ):
        raise ValueError("mob groups must use schema version 1")
    groups = [_validated_group(group) for group in payload["groups"]]
    return sorted(groups, key=lambda value: value["canonicalId"])


def _empty_mob_details() -> JsonObject:
    return {
        "stats": [],
        "mechanics": [],
        "lootStatus": "unknown",
        "loot": [],
        "variants": [],
    }


def _variant_reference(item: JsonObject, member: JsonObject) -> JsonObject:
    return {
        "id": str(item["id"]),
        "prefabId": str(item.get("prefabId") or ""),
        "name": str(item.get("name") or item.get("prefabId") or item["id"]),
        "role": member["role"],
        "order": member["order"],
        "sprite": deepcopy(item.get("sprite")),
    }


def apply_mob_groups(
    items: Sequence[JsonObject], groups: Sequence[JsonObject]
) -> Tuple[List[JsonObject], List[JsonObject]]:
    public = [deepcopy(item) for item in items]
    by_id = {str(item["id"]): item for item in public}
    membership: Dict[str, str] = {}
    hidden = set()
    audit: List[JsonObject] = []

    for raw_group in sorted(groups, key=lambda value: str(value.get("canonicalId"))):
        group = _validated_group(raw_group)
        canonical_id = group["canonicalId"]
        if canonical_id not in by_id:
            raise ValueError(f"missing canonical mob group member: {canonical_id}")
        canonical = by_id[canonical_id]
        current_mob = canonical.get("mob")
        existing_variants = (
            current_mob.get("variants") if isinstance(current_mob, dict) else []
        )
        existing_variants_by_id = {
            str(variant["id"]): variant
            for variant in existing_variants
            if isinstance(variant, dict) and isinstance(variant.get("id"), str)
        }
        variants = []
        for member in group["members"]:
            member_id = member["id"]
            if member_id in membership:
                raise ValueError(f"{member_id} belongs to multiple mob groups")
            if member_id not in by_id:
                raise ValueError(f"missing mob group member: {member_id}")
            membership[member_id] = canonical_id
            source = by_id[member_id]
            variant = _variant_reference(source, member)
            existing_variant = existing_variants_by_id.get(member_id)
            if isinstance(existing_variant, dict):
                variant["sprite"] = deepcopy(existing_variant.get("sprite"))
            variants.append(variant)
            action = "keep" if member_id == canonical_id else "merge"
            if action == "merge":
                hidden.add(member_id)
            audit.append(
                {
                    "id": member_id,
                    "canonicalId": canonical_id,
                    "action": action,
                    "role": member["role"],
                    "order": member["order"],
                    "originalCategory": source.get("category"),
                    "finalCategory": group["category"],
                    "reason": (
                        "Giữ làm record Mob/Boss chính."
                        if action == "keep"
                        else "Gộp vào record Mob/Boss chính theo manifest biến thể."
                    ),
                }
            )
        canonical["category"] = group["category"]
        mob = deepcopy(current_mob) if isinstance(current_mob, dict) else _empty_mob_details()
        mob["variants"] = variants
        canonical["mob"] = mob

    filtered = [item for item in public if str(item["id"]) not in hidden]
    return (
        sorted(filtered, key=lambda value: str(value["id"])),
        sorted(audit, key=lambda value: str(value["id"])),
    )
