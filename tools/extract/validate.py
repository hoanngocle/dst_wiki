"""Hard integrity checks and soft catalog coverage reporting."""

import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, Iterable, Iterator, List, Optional

from tools.extract.source_manifest import ARCHIVES


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


def validate_catalog(db_path: Path, manifest_path: Optional[Path] = None) -> Dict[str, Any]:
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
        archive = _archive_report(db, db_path, manifest_path)
        wiki_urls = _urls(
            _provenance_strings(
                db, archive["manifest_path"], archive["manifest_data"]
            )
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
        "low_confidence_fields": low_confidence_fields,
        "extraction_errors": extraction_errors,
        "conflicts": conflicts,
        "wiki_urls": wiki_urls,
        "archive_checksums": archive["checks"],
        "archive_checksum_errors": archive["errors"],
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
