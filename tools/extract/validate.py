"""Hard integrity checks and soft catalog coverage reporting."""

import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Any, Dict, Iterable, List, Optional

from tools.extract.source_manifest import ARCHIVES


URL_PATTERN = re.compile(r"(?i)\b(?:https?://|www\.)[^\s\"'<>]+")


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
) -> Dict[str, List[Dict[str, Any]]]:
    rows = db.execute(
        "select source_id,path,sha256 from sources where kind='base_game_source' order by path,source_id"
    ).fetchall()
    archives = {Path(row["path"]).name: row for row in rows if Path(row["path"]).name in ARCHIVES}
    if not archives:
        return {"checks": [], "errors": []}

    project_root = db_path.resolve().parents[2] if db_path.parent.name == "generated" else db_path.resolve().parent
    manifest = Path(manifest_path) if manifest_path is not None else project_root / "data/sources/game/manifest.json"
    errors: List[Dict[str, Any]] = []
    checks: List[Dict[str, Any]] = []
    try:
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "checks": checks,
            "errors": [{"code": "invalid_source_manifest", "path": str(manifest), "detail": str(exc)}],
        }
    files = manifest_data.get("files", {})
    for name in ARCHIVES:
        source = archives.get(name)
        expected = files.get(name)
        if source is None or not isinstance(expected, dict):
            errors.append({"code": "missing_source_archive", "archive": name})
            continue
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
    return {"checks": checks, "errors": errors}


def _error_subject(payload: Dict[str, Any], locator: str) -> Optional[str]:
    for field in ("prefab", "prefab_id", "source_prefab_id", "recipe", "path"):
        value = payload.get(field)
        if isinstance(value, str) and value:
            return value
    return locator or None


def _urls(values: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    found = []
    for value in values:
        for match in URL_PATTERN.findall(value["value"]):
            found.append({"location": value["location"], "url": match.rstrip(".,);]")})
    return sorted(found, key=lambda row: (row["location"], row["url"]))


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
        url_values = [
            {"location": "source:" + row["source_id"], "value": row["path"]}
            for row in db.execute("select source_id,path from sources order by source_id")
        ]
        url_values.extend(
            {"location": "evidence:" + row["evidence_id"], "value": row["raw_value_json"]}
            for row in db.execute("select evidence_id,raw_value_json from evidence order by evidence_id")
        )
        wiki_urls = _urls(url_values)
        archive = _archive_report(db, db_path, manifest_path)
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
        "unresolved_dependencies": unresolved,
        "foreign_key_errors": foreign_keys,
        "runtime_errors": runtime_errors,
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
