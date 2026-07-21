"""Hard integrity checks and soft catalog coverage reporting."""

import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, Iterable, Iterator, List, Optional
from zipfile import ZipFile

from tools.extract.base_game import discover_prefab_modules
from tools.extract.source_manifest import ARCHIVES
from tools.extract.runtime_import import COVERAGE_CATEGORIES


URL_PATTERN = re.compile(
    r"(?ix)\b(?:"
    r"https?://[^\s\"'<>]+|"
    r"www\.[^\s\"'<>]+|"
    r"(?:[a-z0-9-]+\.)*wiki\.[a-z]{2,}(?:/[^\s\"'<>]*)?"
    r")"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _loads(value: str) -> Any:
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def _coverage(db: sqlite3.Connection, predicate: str) -> float:
    total = db.execute("select count(*) from entities").fetchone()[0]
    if not total:
        return 0.0
    covered = db.execute(
        "select count(*) from entities e where " + predicate
    ).fetchone()[0]
    return round(covered / total, 6)


def _archive_report(
    db: sqlite3.Connection, db_path: Path, manifest_path: Optional[Path]
) -> Dict[str, Any]:
    rows = db.execute(
        "select source_id,kind,path,version,sha256 from sources order by path,source_id"
    ).fetchall()
    archives: Dict[str, List[sqlite3.Row]] = {name: [] for name in ARCHIVES}
    for row in rows:
        basename = Path(row["path"]).name
        if basename in archives:
            archives[basename].append(row)
    base_count = db.execute(
        "select count(*) from entities where namespace='base_game'"
    ).fetchone()[0]
    required = bool(manifest_path is not None or base_count or any(archives.values()))
    if not required:
        return {
            "checks": [],
            "errors": [],
            "manifest_path": None,
            "manifest_data": None,
        }

    resolved_db = db_path.resolve()
    project_root = (
        resolved_db.parents[2]
        if resolved_db.parent.name == "generated"
        and resolved_db.parent.parent.name == "data"
        else resolved_db.parent
    )
    manifest = (
        Path(manifest_path)
        if manifest_path is not None
        else project_root / "data/sources/game/manifest.json"
    )
    errors: List[Dict[str, Any]] = []
    checks: List[Dict[str, Any]] = []
    for name in ARCHIVES:
        if not archives[name]:
            errors.append({"code": "missing_source_archive", "archive": name})
    try:
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "checks": checks,
            "errors": errors
            + [
                {
                    "code": "invalid_source_manifest",
                    "path": str(manifest),
                    "detail": str(exc),
                }
            ],
            "manifest_path": str(manifest),
            "manifest_data": None,
        }
    if not isinstance(manifest_data, dict):
        errors.append(
            {
                "code": "invalid_source_manifest",
                "path": str(manifest),
                "detail": "manifest root must be an object",
            }
        )
        files = {}
    else:
        files = manifest_data.get("files", {})
        if not isinstance(files, dict):
            errors.append(
                {
                    "code": "invalid_source_manifest",
                    "path": str(manifest),
                    "detail": "manifest files must be an object",
                }
            )
            files = {}
    for name in ARCHIVES:
        candidates = archives[name]
        expected = next(
            (
                value
                for key, value in files.items()
                if Path(str(key)).name == name and isinstance(value, dict)
            ),
            None,
        )
        if expected is None:
            errors.append({"code": "missing_manifest_archive", "archive": name})
            continue
        if not candidates:
            continue
        source = next(
            (
                candidate
                for candidate in candidates
                if candidate["sha256"] == expected.get("sha256")
            ),
            candidates[0],
        )
        source_path = Path(source["path"])
        if not source_path.is_absolute():
            source_path = project_root / source_path
        try:
            actual_hash = _sha256(source_path)
            actual_size = source_path.stat().st_size
        except OSError as exc:
            errors.append({"code": "unreadable_source_archive", "archive": name, "path": str(source_path), "detail": str(exc)})
            continue
        check = {
            "archive": name,
            "source_id": source["source_id"],
            "source_kind": source["kind"],
            "path": source["path"],
            "size": actual_size,
            "sha256": actual_hash,
            "manifest_sha256": expected.get("sha256"),
            "database_sha256": source["sha256"],
        }
        checks.append(check)
        if (
            actual_hash != expected.get("sha256")
            or actual_hash != source["sha256"]
            or actual_size != expected.get("size")
        ):
            errors.append({"code": "source_archive_checksum_mismatch", **check})
    return {
        "checks": checks,
        "errors": errors,
        "manifest_path": str(manifest),
        "manifest_data": manifest_data,
    }


def _error_subject(payload: Dict[str, Any], locator: str) -> Optional[str]:
    for field in ("prefab", "prefab_id", "source_prefab_id", "recipe", "path"):
        value = payload.get(field)
        if isinstance(value, str) and value:
            return value
    return locator or None


def _recursive_strings(value: Any, location: str) -> Iterator[Dict[str, str]]:
    if isinstance(value, dict):
        for key in sorted(value, key=lambda item: str(item)):
            key_text = str(key)
            yield {"location": location + ".key", "value": key_text}
            yield from _recursive_strings(value[key], location + "." + key_text)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _recursive_strings(item, f"{location}[{index}]")
    elif isinstance(value, str):
        yield {"location": location, "value": value}


def _provenance_strings(
    db: sqlite3.Connection, manifest_path: Optional[str], manifest_data: Any
) -> Iterator[Dict[str, str]]:
    table_specs = (
        ("sources", "source_id", "source", ()),
        ("evidence", "evidence_id", "evidence", ("raw_value_json",)),
        (
            "extraction_errors",
            "error_id",
            "extraction_error",
            ("payload_json",),
        ),
        (
            "conflicts",
            "conflict_id",
            "conflict",
            ("candidates_json", "selected_json"),
        ),
    )
    for table, id_column, prefix, json_columns in table_specs:
        for row in db.execute(f"select * from {table} order by {id_column}"):
            row_id = str(row[id_column])
            for column in row.keys():
                value = row[column]
                if column in json_columns and isinstance(value, str):
                    value = _loads(value)
                yield from _recursive_strings(
                    value, f"{prefix}:{row_id}.{column}"
                )
    if manifest_data is not None:
        yield from _recursive_strings(
            manifest_data, "manifest:" + str(manifest_path or "manifest.json")
        )


def _urls(values: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    found = set()
    for value in values:
        for match in URL_PATTERN.findall(value["value"]):
            found.add((value["location"], match.rstrip(".,);]")))
    return [
        {"location": location, "url": url}
        for location, url in sorted(found)
    ]


def _prefab_export_coverage(
    scripts_path: Optional[Path],
    items_path: Optional[Path],
    structure_audit_path: Optional[Path] = None,
    effect_other_audit_path: Optional[Path] = None,
    mob_boss_audit_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    if scripts_path is None or items_path is None:
        return []
    with ZipFile(Path(scripts_path)) as archive:
        expected = set(discover_prefab_modules(archive.namelist()))
    payload = json.loads(Path(items_path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 6 or not isinstance(payload.get("items"), list):
        return [{"code": "invalid_prefab_export_payload"}]
    if structure_audit_path is not None:
        audit = json.loads(Path(structure_audit_path).read_text(encoding="utf-8"))
        rows = audit.get("rows") if isinstance(audit, dict) else None
        if (
            not isinstance(audit, dict)
            or audit.get("schema_version") != 1
            or not isinstance(rows, list)
        ):
            return [{"code": "invalid_structure_audit_payload"}]
        expected -= {
            row.get("prefabId")
            for row in rows
            if isinstance(row, dict)
            and row.get("namespace") == "base_game"
            and row.get("action") == "exclude"
            and isinstance(row.get("prefabId"), str)
        }
    if effect_other_audit_path is not None:
        audit = json.loads(
            Path(effect_other_audit_path).read_text(encoding="utf-8")
        )
        rows = audit.get("rows") if isinstance(audit, dict) else None
        if (
            not isinstance(audit, dict)
            or audit.get("schema_version") != 1
            or not isinstance(rows, list)
        ):
            return [{"code": "invalid_effect_other_audit_payload"}]
        expected -= {
            row.get("prefabId")
            for row in rows
            if isinstance(row, dict)
            and row.get("namespace") == "base_game"
            and row.get("action") == "exclude"
            and isinstance(row.get("prefabId"), str)
        }
    if mob_boss_audit_path is not None:
        audit = json.loads(Path(mob_boss_audit_path).read_text(encoding="utf-8"))
        rows = audit.get("rows") if isinstance(audit, dict) else None
        if (
            not isinstance(audit, dict)
            or audit.get("schema_version") != 1
            or not isinstance(rows, list)
        ):
            return [{"code": "invalid_mob_boss_audit_payload"}]
        expected -= {
            str(row["id"]).split(":", 1)[1]
            for row in rows
            if isinstance(row, dict)
            and isinstance(row.get("id"), str)
            and str(row["id"]).startswith("base_game:")
            and row.get("action") in {"merge", "exclude"}
        }
    actual = {
        item.get("prefabId")
        for item in payload["items"]
        if isinstance(item, dict)
        and item.get("namespace") == "base_game"
        and not str(item.get("id", "")).startswith("wiki:")
        and isinstance(item.get("prefabId"), str)
    }
    referenced_dependencies = set()

    def collect_recipe_dependencies(value: Any) -> None:
        if isinstance(value, list):
            for entry in value:
                collect_recipe_dependencies(entry)
            return
        if not isinstance(value, dict):
            return
        ingredients = value.get("ingredients")
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                ingredient_id = (
                    ingredient.get("id")
                    if isinstance(ingredient, dict)
                    else None
                )
                if isinstance(ingredient_id, str) and ingredient_id.startswith(
                    "base_game:"
                ):
                    referenced_dependencies.add(ingredient_id.split(":", 1)[1])
        for nested in value.values():
            collect_recipe_dependencies(nested)

    collect_recipe_dependencies(payload["items"])
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected - referenced_dependencies)
    return [{"missing": missing, "unexpected": unexpected}] if missing or unexpected else []


def _structure_export_errors(
    items_path: Optional[Path], structure_audit_path: Optional[Path]
) -> List[Dict[str, Any]]:
    if items_path is None or structure_audit_path is None:
        return []
    payload = json.loads(Path(items_path).read_text(encoding="utf-8"))
    audit = json.loads(Path(structure_audit_path).read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else None
    rows = audit.get("rows") if isinstance(audit, dict) else None
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 6
        or not isinstance(items, list)
    ):
        return [{"code": "invalid_structure_items_payload"}]
    if (
        not isinstance(audit, dict)
        or audit.get("schema_version") != 1
        or not isinstance(rows, list)
    ):
        return [{"code": "invalid_structure_audit_payload"}]

    errors: List[Dict[str, Any]] = []
    items_by_id = {
        item.get("id"): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    audit_by_id: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append({"code": "invalid_structure_audit_row"})
            continue
        row_id = row["id"]
        if row_id in audit_by_id:
            errors.append({"code": "duplicate_structure_audit_row", "id": row_id})
        audit_by_id[row_id] = row
        if row.get("action") not in {"keep", "repair", "exclude"}:
            errors.append({"code": "invalid_structure_audit_action", "id": row_id})
        if row.get("classification") not in {
            "natural_structure",
            "craftable_missing_asset",
            "craftable_wiki_visual",
            "world_asset_only",
            "technical_prefab",
            "unverified",
        }:
            errors.append(
                {"code": "invalid_structure_audit_classification", "id": row_id}
            )
        reason = row.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append({"code": "invalid_structure_audit_reason", "id": row_id})
        evidence = row.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(
                {"code": "invalid_structure_audit_evidence", "id": row_id}
            )

    valid_statuses = {"known", "none", "unknown"}
    required_sections = (
        "origin",
        "construction",
        "functions",
        "craftables",
        "destruction",
        "visual",
    )
    for item_id in sorted(items_by_id):
        item = items_by_id[item_id]
        details = item.get("structureDetails")
        if item.get("namespace") == "wiki":
            errors.append({"code": "wiki_source_group_not_removed", "id": item_id})
        if item.get("category") != "structure":
            if details is not None:
                errors.append(
                    {"code": "non_structure_has_structure_details", "id": item_id}
                )
            continue
        if not isinstance(details, dict):
            errors.append({"code": "missing_structure_details", "id": item_id})
            continue
        for section_name in required_sections:
            section = details.get(section_name)
            if not isinstance(section, dict):
                errors.append(
                    {
                        "code": "missing_structure_detail_section",
                        "id": item_id,
                        "section": section_name,
                    }
                )
            elif section.get("status") not in valid_statuses:
                errors.append(
                    {
                        "code": "invalid_structure_detail_status",
                        "id": item_id,
                        "section": section_name,
                    }
                )
        origin = details.get("origin")
        construction = details.get("construction")
        visual = details.get("visual")
        craftable = isinstance(item.get("recipe"), dict) or (
            isinstance(origin, dict) and origin.get("craftable") is True
        )
        if (
            craftable
            and isinstance(construction, dict)
            and construction.get("status") != "known"
        ):
            errors.append(
                {
                    "code": "craftable_structure_missing_construction",
                    "id": item_id,
                }
            )
        visual_resolved = item.get("sprite") is not None or (
            isinstance(visual, dict)
            and visual.get("status") == "known"
            and (
                isinstance(visual.get("sprite"), dict)
                or (
                    isinstance(visual.get("image"), dict)
                    and isinstance(visual["image"].get("src"), str)
                )
            )
        )
        if craftable and not visual_resolved:
            errors.append(
                {"code": "craftable_structure_missing_visual", "id": item_id}
            )
        if (
            item.get("sprite") is None
            and isinstance(origin, dict)
            and origin.get("naturallySpawned") is True
            and origin.get("craftable") is False
            and (
                not isinstance(origin.get("note"), str)
                or not origin["note"].strip()
            )
        ):
            errors.append({"code": "natural_structure_missing_note", "id": item_id})
        craftables = details.get("craftables")
        recipes = craftables.get("recipes") if isinstance(craftables, dict) else None
        if isinstance(recipes, list):
            for recipe in recipes:
                if not isinstance(recipe, dict):
                    continue
                result = recipe.get("result")
                result_id = result.get("id") if isinstance(result, dict) else None
                if isinstance(result_id, str) and result_id not in items_by_id:
                    errors.append(
                        {
                            "code": "unresolved_structure_craftable_result",
                            "id": item_id,
                            "result": result_id,
                        }
                    )
                ingredients = recipe.get("ingredients")
                if not isinstance(ingredients, list):
                    continue
                for ingredient in ingredients:
                    ingredient_id = (
                        ingredient.get("id")
                        if isinstance(ingredient, dict)
                        else None
                    )
                    if (
                        isinstance(ingredient_id, str)
                        and ingredient_id not in items_by_id
                    ):
                        errors.append(
                            {
                                "code": "unresolved_structure_craftable_ingredient",
                                "id": item_id,
                                "ingredient": ingredient_id,
                                "result": result_id,
                            }
                        )
        if item.get("sprite") is None and item_id not in audit_by_id:
            errors.append({"code": "unaudited_iconless_structure", "id": item_id})

    for item_id in sorted(audit_by_id):
        row = audit_by_id[item_id]
        action = row.get("action")
        item = items_by_id.get(item_id)
        if action == "exclude":
            if item is not None:
                errors.append({"code": "excluded_structure_is_public", "id": item_id})
            continue
        if item is None:
            errors.append({"code": "audited_structure_not_public", "id": item_id})
            continue
        if action == "repair":
            details = item.get("structureDetails")
            visual = details.get("visual") if isinstance(details, dict) else None
            if not isinstance(visual, dict) or visual.get("status") != "known":
                errors.append(
                    {"code": "unresolved_structure_visual_repair", "id": item_id}
                )
    return errors


def _effect_other_audit_errors(
    items_path: Optional[Path], audit_path: Optional[Path]
) -> List[Dict[str, Any]]:
    if items_path is None or audit_path is None:
        return []
    payload = json.loads(Path(items_path).read_text(encoding="utf-8"))
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else None
    rows = audit.get("rows") if isinstance(audit, dict) else None
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 6
        or not isinstance(items, list)
    ):
        return [{"code": "invalid_effect_other_items_payload"}]
    if (
        not isinstance(audit, dict)
        or audit.get("schema_version") != 1
        or not isinstance(rows, list)
    ):
        return [{"code": "invalid_effect_other_audit_payload"}]

    public_items = {
        item.get("id"): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    public_in_scope = {
        item_id
        for item_id, item in public_items.items()
        if item.get("category") in {"effect", "other"}
    }
    errors: List[Dict[str, Any]] = []
    audit_by_id: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append({"code": "invalid_effect_other_audit_row"})
            continue
        row_id = row["id"]
        if row_id in audit_by_id:
            errors.append(
                {"code": "duplicate_effect_other_audit_row", "id": row_id}
            )
        audit_by_id[row_id] = row
        if row.get("category") not in {"effect", "other"}:
            errors.append(
                {"code": "invalid_effect_other_audit_category", "id": row_id}
            )
        action = row.get("action")
        if action not in {"keep", "exclude"}:
            errors.append(
                {"code": "invalid_effect_other_audit_action", "id": row_id}
            )
        elif action == "keep" and row_id not in public_items:
            errors.append(
                {"code": "audited_effect_other_not_public", "id": row_id}
            )
        elif action == "exclude" and row_id in public_items:
            errors.append(
                {"code": "excluded_effect_other_is_public", "id": row_id}
            )
        if row.get("reasonCode") not in {
            "positive_signal",
            "reverse_reference",
            "empty_unreferenced",
        }:
            errors.append(
                {"code": "invalid_effect_other_audit_reason_code", "id": row_id}
            )
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            errors.append(
                {"code": "invalid_effect_other_audit_reason", "id": row_id}
            )
        signals = row.get("signals")
        if not isinstance(signals, dict) or not all(
            isinstance(value, bool) for value in signals.values()
        ):
            errors.append(
                {"code": "invalid_effect_other_audit_signals", "id": row_id}
            )
        elif action == "exclude" and any(signals.values()):
            errors.append(
                {
                    "code": "excluded_effect_other_has_positive_signal",
                    "id": row_id,
                }
            )
        references = row.get("references")
        if not isinstance(references, list) or not all(
            isinstance(reference, dict)
            and isinstance(reference.get("source"), str)
            and isinstance(reference.get("kind"), str)
            for reference in references
        ):
            errors.append(
                {"code": "invalid_effect_other_audit_references", "id": row_id}
            )
        elif action == "exclude" and references:
            errors.append(
                {"code": "excluded_effect_other_is_referenced", "id": row_id}
            )

    for item_id in sorted(public_in_scope - set(audit_by_id)):
        errors.append({"code": "unaudited_effect_other_item", "id": item_id})

    expected_summary = {
        "total": len(rows),
        "keep": sum(
            isinstance(row, dict) and row.get("action") == "keep" for row in rows
        ),
        "exclude": sum(
            isinstance(row, dict) and row.get("action") == "exclude"
            for row in rows
        ),
        "categories": {
            category: sum(
                isinstance(row, dict) and row.get("category") == category
                for row in rows
            )
            for category in ("effect", "other")
        },
    }
    if audit.get("summary") != expected_summary:
        errors.append({"code": "effect_other_audit_summary_mismatch"})
    return errors


def _mob_boss_audit_errors(
    items_path: Optional[Path],
    audit_path: Optional[Path],
    groups_path: Optional[Path],
) -> List[Dict[str, Any]]:
    if items_path is None or audit_path is None or groups_path is None:
        return []
    payload = json.loads(Path(items_path).read_text(encoding="utf-8"))
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    groups_payload = json.loads(Path(groups_path).read_text(encoding="utf-8"))
    items = payload.get("items") if isinstance(payload, dict) else None
    rows = audit.get("rows") if isinstance(audit, dict) else None
    groups = groups_payload.get("groups") if isinstance(groups_payload, dict) else None
    if payload.get("schema_version") != 6 or not isinstance(items, list):
        return [{"code": "invalid_mob_boss_items_payload"}]
    if audit.get("schema_version") != 1 or not isinstance(rows, list):
        return [{"code": "invalid_mob_boss_audit_payload"}]
    if groups_payload.get("schema_version") != 1 or not isinstance(groups, list):
        return [{"code": "invalid_mob_groups_payload"}]

    errors: List[Dict[str, Any]] = []
    public = {
        item.get("id"): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    membership: Dict[str, str] = {}
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("canonicalId"), str):
            errors.append({"code": "invalid_mob_group"})
            continue
        canonical_id = group["canonicalId"]
        members = group.get("members")
        if not isinstance(members, list):
            errors.append({"code": "invalid_mob_group_members", "id": canonical_id})
            continue
        for member in members:
            member_id = member.get("id") if isinstance(member, dict) else None
            if not isinstance(member_id, str):
                errors.append({"code": "invalid_mob_group_member", "id": canonical_id})
                continue
            if member_id in membership:
                errors.append({"code": "duplicate_mob_group_member", "id": member_id})
            membership[member_id] = canonical_id

    audit_by_id: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            errors.append({"code": "invalid_mob_boss_audit_row"})
            continue
        row_id = row["id"]
        if row_id in audit_by_id:
            errors.append({"code": "duplicate_mob_boss_audit_row", "id": row_id})
        audit_by_id[row_id] = row
        action = row.get("action")
        canonical_id = row.get("canonicalId")
        if action not in {"keep", "merge", "exclude"}:
            errors.append({"code": "invalid_mob_boss_audit_action", "id": row_id})
            continue
        if not isinstance(canonical_id, str):
            errors.append({"code": "invalid_mob_boss_canonical_id", "id": row_id})
            continue
        if action == "merge" and row_id in public:
            errors.append({"code": "merged_mob_member_is_public", "id": row_id})
        if action == "exclude" and row_id in public:
            errors.append({"code": "excluded_mob_member_is_public", "id": row_id})
        if action == "keep" and row_id not in public:
            errors.append({"code": "audited_mob_boss_not_public", "id": row_id})
        if canonical_id not in public:
            errors.append({"code": "missing_canonical_mob_boss", "id": row_id, "canonicalId": canonical_id})

    expected_audited = {
        item_id
        for item_id, item in public.items()
        if item.get("category") in {"mob", "boss"}
    } | set(membership)
    for item_id in sorted(expected_audited - set(audit_by_id)):
        errors.append({"code": "unaudited_mob_boss_item", "id": item_id})

    allowed_methods = {"kill", "mine_post_defeat", "harvest", "conditional"}
    for item_id, item in sorted(public.items()):
        if item.get("category") not in {"mob", "boss"}:
            continue
        mob = item.get("mob")
        if not isinstance(mob, dict):
            errors.append({"code": "missing_mob_boss_details", "id": item_id})
            continue
        loot = mob.get("loot")
        if not isinstance(loot, list):
            errors.append({"code": "invalid_mob_loot", "id": item_id})
            continue
        if mob.get("lootStatus") == "known" and not loot:
            errors.append({"code": "known_mob_loot_is_empty", "id": item_id})
        variant_ids = {
            variant.get("id")
            for variant in mob.get("variants", [])
            if isinstance(variant, dict) and isinstance(variant.get("id"), str)
        } if isinstance(mob.get("variants"), list) else set()
        for reward in loot:
            if not isinstance(reward, dict):
                errors.append({"code": "invalid_mob_reward", "id": item_id})
                continue
            reference = reward.get("item")
            reward_id = reference.get("id") if isinstance(reference, dict) else None
            if not isinstance(reward_id, str) or reward_id not in public:
                errors.append({"code": "missing_mob_reward_reference", "id": item_id, "reward": reward_id})
            if reward.get("method") not in allowed_methods:
                errors.append({"code": "invalid_mob_reward_method", "id": item_id, "reward": reward_id})
            minimum = reward.get("minimum")
            maximum = reward.get("maximum")
            if (
                not isinstance(minimum, (int, float))
                or isinstance(minimum, bool)
                or not isinstance(maximum, (int, float))
                or isinstance(maximum, bool)
                or minimum < 0
                or maximum < minimum
            ):
                errors.append({"code": "invalid_mob_reward_quantity", "id": item_id, "reward": reward_id})
            if reward.get("sourceVariant") not in variant_ids:
                errors.append({"code": "invalid_mob_reward_source_variant", "id": item_id, "reward": reward_id})

    expected_summary = {
        "total": len(rows),
        "keep": sum(isinstance(row, dict) and row.get("action") == "keep" for row in rows),
        "merge": sum(isinstance(row, dict) and row.get("action") == "merge" for row in rows),
        "exclude": sum(isinstance(row, dict) and row.get("action") == "exclude" for row in rows),
    }
    if audit.get("summary") != expected_summary:
        errors.append({"code": "mob_boss_audit_summary_mismatch"})
    return errors


def validate_catalog(
    db_path: Path,
    manifest_path: Optional[Path] = None,
    prefab_scripts_path: Optional[Path] = None,
    items_path: Optional[Path] = None,
    structure_audit_path: Optional[Path] = None,
    effect_other_audit_path: Optional[Path] = None,
    mob_boss_audit_path: Optional[Path] = None,
    mob_groups_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Return deterministic hard failures, extraction diagnostics and coverage."""

    db_path = Path(db_path)
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    try:
        counts = {"base_game": 0, "tu_tien": 0}
        for row in db.execute("select namespace,count(*) count from entities group by namespace order by namespace"):
            counts[row["namespace"]] = row["count"]
        coverage = {
            "name_vi": _coverage(db, "e.name_vi is not null and e.name_vi<>''"),
            "icon": _coverage(db, "e.icon_key is not null and e.icon_key<>''"),
            "recipe": _coverage(db, "exists(select 1 from recipes r where r.product_namespace=e.namespace and r.product_id=e.prefab_id)"),
            "acquisition": _coverage(db, "exists(select 1 from acquisition_sources a where a.target_namespace=e.namespace and a.target_id=e.prefab_id)"),
            "stats": _coverage(db, "exists(select 1 from stats s where s.namespace=e.namespace and s.prefab_id=e.prefab_id)"),
        }
        missing_inventory_names = [
            row[0]
            for row in db.execute(
                "select prefab_id from entities "
                "where namespace='tu_tien' and is_inventory_item=1 "
                "and (name_vi is null or name_vi='') order by prefab_id"
            )
        ]
        foreign_keys = [
            {"table": row[0], "rowid": row[1], "parent": row[2], "foreign_key": row[3]}
            for row in db.execute("pragma foreign_key_check")
        ]

        extraction_errors = []
        unresolved = []
        runtime_errors = []
        for row in db.execute(
            "select error_id,source_kind,locator,code,payload_json from extraction_errors order by source_kind,code,locator,error_id"
        ):
            payload = _loads(row["payload_json"])
            if not isinstance(payload, dict):
                payload = {"raw": payload}
            error = {
                "error_id": row["error_id"],
                "source_kind": row["source_kind"],
                "code": row["code"],
                "subject": _error_subject(payload, row["locator"]),
                "locator": row["locator"],
                "detail": payload,
            }
            extraction_errors.append(error)
            if row["code"] == "unresolved_base_game_dependency":
                unresolved.append(error)
            if row["source_kind"] == "runtime_probe":
                runtime_errors.append(error)

        low_confidence_fields = [
            {
                "evidence_id": row["evidence_id"],
                "record_type": row["record_type"],
                "record_id": row["record_id"],
                "source_id": row["source_id"],
                "source_kind": row["source_kind"],
                "locator": row["locator"],
                "confidence": row["confidence"],
                "selected": bool(row["selected"]),
            }
            for row in db.execute(
                "select e.evidence_id,e.record_type,e.record_id,e.source_id,"
                "s.kind source_kind,e.locator,e.confidence,e.selected "
                "from evidence e join sources s on s.source_id=e.source_id "
                "where e.confidence < 0.7 "
                "order by e.confidence,e.record_type,e.record_id,e.source_id,"
                "e.locator,e.evidence_id"
            )
        ]

        conflicts = [
            {
                "conflict_id": row["conflict_id"],
                "subject": row["subject_key"],
                "field": row["field_key"],
                "candidates": _loads(row["candidates_json"]),
                "selected": _loads(row["selected_json"]),
            }
            for row in db.execute("select * from conflicts order by subject_key,field_key,conflict_id")
        ]
        runtime_coverage = [
            {
                "coverage_id": row["coverage_id"],
                "namespace": row["namespace"],
                "prefab_id": row["prefab_id"],
                "category": row["category"],
                "status": row["status"],
                "reason": row["reason"],
                "details": _loads(row["details_json"]),
            }
            for row in db.execute(
                "select * from runtime_coverage "
                "order by namespace,prefab_id,category,coverage_id"
            )
        ]
        runtime_coverage_summary: Dict[str, int] = {}
        for row in runtime_coverage:
            status = row["status"]
            runtime_coverage_summary[status] = (
                runtime_coverage_summary.get(status, 0) + 1
            )
        runtime_coverage_errors = []
        expected_categories = set(COVERAGE_CATEGORIES)
        for entity in db.execute(
            "select distinct prefab_id from runtime_coverage "
            "where namespace='tu_tien' order by prefab_id"
        ):
            prefab_id = entity["prefab_id"]
            category_counts = {
                row["category"]: row["count"]
                for row in db.execute(
                    "select category,count(*) count from runtime_coverage "
                    "where namespace='tu_tien' and prefab_id=? "
                    "group by category order by category",
                    (prefab_id,),
                )
            }
            actual_categories = set(category_counts)
            missing_categories = sorted(expected_categories - actual_categories)
            unexpected_categories = sorted(actual_categories - expected_categories)
            duplicate_categories = sorted(
                category
                for category, count in category_counts.items()
                if count != 1
            )
            if missing_categories or unexpected_categories or duplicate_categories:
                runtime_coverage_errors.append(
                    {
                        "namespace": "tu_tien",
                        "prefab_id": prefab_id,
                        "missing_categories": missing_categories,
                        "unexpected_categories": unexpected_categories,
                        "duplicate_categories": duplicate_categories,
                    }
                )
        archive = _archive_report(db, db_path, manifest_path)
        wiki_urls = _urls(
            _provenance_strings(
                db, archive["manifest_path"], archive["manifest_data"]
            )
        )
        prefab_export_coverage_errors = _prefab_export_coverage(
            prefab_scripts_path,
            items_path,
            structure_audit_path,
            effect_other_audit_path,
            mob_boss_audit_path,
        )
        structure_detail_errors = _structure_export_errors(
            items_path, structure_audit_path
        )
        effect_other_audit_errors = _effect_other_audit_errors(
            items_path, effect_other_audit_path
        )
        mob_boss_audit_errors = _mob_boss_audit_errors(
            items_path, mob_boss_audit_path, mob_groups_path
        )
    finally:
        db.close()

    warnings = []
    for field, value in coverage.items():
        if value < 1.0:
            warnings.append({"code": "optional_coverage_incomplete", "field": field, "coverage": value})
    if extraction_errors:
        warnings.append({"code": "extraction_errors_present", "count": len(extraction_errors)})
    if conflicts:
        warnings.append({"code": "conflicts_present", "count": len(conflicts)})
    if low_confidence_fields:
        warnings.append(
            {
                "code": "low_confidence_fields_present",
                "count": len(low_confidence_fields),
            }
        )
    if missing_inventory_names:
        warnings.append(
            {
                "code": "missing_inventory_names",
                "count": len(missing_inventory_names),
            }
        )
    runtime_gaps = sum(
        count
        for status, count in runtime_coverage_summary.items()
        if status != "observed"
    )
    if runtime_gaps:
        warnings.append({"code": "runtime_coverage_gaps", "count": runtime_gaps})
    hard_failures = []
    if foreign_keys:
        hard_failures.append("foreign_key_errors")
    if unresolved:
        hard_failures.append("unresolved_dependencies")
    if archive["errors"]:
        hard_failures.append("archive_checksum_errors")
    if wiki_urls:
        hard_failures.append("wiki_urls")
    if runtime_coverage_errors:
        hard_failures.append("runtime_coverage_errors")
    if prefab_export_coverage_errors:
        hard_failures.append("prefab_export_coverage_errors")
    if structure_detail_errors:
        hard_failures.append("structure_detail_errors")
    if effect_other_audit_errors:
        hard_failures.append("effect_other_audit_errors")
    if mob_boss_audit_errors:
        hard_failures.append("mob_boss_audit_errors")
    return {
        "schema_version": 1,
        "entity_counts": counts,
        "coverage": coverage,
        "missing_inventory_names": missing_inventory_names,
        "unresolved_dependencies": unresolved,
        "foreign_key_errors": foreign_keys,
        "runtime_errors": runtime_errors,
        "runtime_coverage": runtime_coverage,
        "runtime_coverage_summary": runtime_coverage_summary,
        "runtime_coverage_errors": runtime_coverage_errors,
        "low_confidence_fields": low_confidence_fields,
        "extraction_errors": extraction_errors,
        "conflicts": conflicts,
        "wiki_urls": wiki_urls,
        "archive_checksums": archive["checks"],
        "archive_checksum_errors": archive["errors"],
        "prefab_export_coverage_errors": prefab_export_coverage_errors,
        "structure_detail_errors": structure_detail_errors,
        "effect_other_audit_errors": effect_other_audit_errors,
        "mob_boss_audit_errors": mob_boss_audit_errors,
        "warnings": warnings,
        "hard_failures": hard_failures,
    }


def write_validation_report(path: Path, report: Dict[str, Any]) -> None:
    """Atomically write a deterministic validation report."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp")
    try:
        temporary.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    except BaseException:
        if temporary.exists():
            temporary.unlink()
        raise
