import fcntl
import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Mapping, Optional, Tuple
from urllib.parse import quote, unquote, urlsplit

from tools.crawl_wiki.storage import _utc_now


SCHEMA_VERSION = 1
STATUSES = ("New", "Doing", "Done")
DECISIONS = ("crawl", "busy", "reuse")


class UrlRegistryError(RuntimeError):
    pass


def normalize_crawler_url(url: str, allowed_origin: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise UrlRegistryError("crawler URL must be a non-empty string")
    if not isinstance(allowed_origin, str) or not allowed_origin.strip():
        raise UrlRegistryError("allowed origin must be a non-empty string")

    origin = urlsplit(allowed_origin.strip())
    if origin.scheme != "https" or not origin.hostname:
        raise UrlRegistryError("allowed origin must be an HTTPS origin")
    if origin.path not in ("", "/") or origin.query or origin.fragment:
        raise UrlRegistryError("allowed origin must not include a path")

    parsed = urlsplit(url.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise UrlRegistryError("crawler URL must use HTTPS")
    if (parsed.hostname.casefold(), parsed.port) != (
        origin.hostname.casefold(),
        origin.port,
    ):
        raise UrlRegistryError("crawler URL origin is not allowed")
    if not parsed.path.startswith("/wiki/"):
        raise UrlRegistryError("crawler URL must be a /wiki/ page URL")

    title = unquote(parsed.path[len("/wiki/") :]).strip().replace(" ", "_")
    if not title:
        raise UrlRegistryError("crawler URL must include a page title")
    encoded_title = quote(title, safe="/:()_-'!,$*+.~")
    netloc = origin.hostname.casefold()
    if origin.port is not None:
        netloc = "{}:{}".format(netloc, origin.port)
    return "https://{}/wiki/{}".format(netloc, encoded_title)


@dataclass(frozen=True)
class UrlRecord:
    url: str
    status: str
    categories: Tuple[str, ...]
    worker_id: Optional[str]
    attempts: int
    created_at: str
    updated_at: str
    claimed_at: Optional[str]
    completed_at: Optional[str]
    artifact_path: Optional[str]
    artifact_sha256: Optional[str]
    last_error: Optional[str]


@dataclass(frozen=True)
class UrlClaim:
    decision: str
    record: UrlRecord

    def with_worker(self, worker_id: str) -> "UrlClaim":
        return replace(self, record=replace(self.record, worker_id=worker_id))


@dataclass(frozen=True)
class RegistryAudit:
    url: str
    status: str
    issue: Optional[str]


class UrlRegistry:
    def __init__(
        self,
        path: Path,
        cache_root: Path,
        allowed_origin: str,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        self.path = Path(path)
        self.cache_root = Path(cache_root)
        self.allowed_origin = allowed_origin
        self.clock = clock
        self.lock_path = self.path.with_suffix(".lock")

    def register(self, url: str, category: str) -> UrlRecord:
        canonical_url = normalize_crawler_url(url, self.allowed_origin)
        category_key = self._category_key(category)
        with self._locked():
            payload = self._read()
            row = self._find(payload, canonical_url)
            if row is None:
                row = self._new_row(canonical_url, category_key)
                payload["items"].append(row)
            else:
                self._add_category(row, category_key)
            self._write(payload)
            return self._to_record(row)

    def claim(self, url: str, category: str, worker_id: str) -> UrlClaim:
        canonical_url = normalize_crawler_url(url, self.allowed_origin)
        category_key = self._category_key(category)
        worker = self._worker_id(worker_id)
        with self._locked():
            payload = self._read()
            row = self._find(payload, canonical_url)
            if row is None:
                row = self._new_row(canonical_url, category_key)
                payload["items"].append(row)
            else:
                self._add_category(row, category_key)

            if row["status"] == "New":
                now = self.clock()
                row.update(
                    {
                        "status": "Doing",
                        "workerId": worker,
                        "attempts": int(row["attempts"]) + 1,
                        "updatedAt": now,
                        "claimedAt": now,
                        "completedAt": None,
                    }
                )
                decision = "crawl"
            elif row["status"] == "Doing":
                decision = "busy"
            elif row["status"] == "Done":
                if not row.get("artifactPath"):
                    raise UrlRegistryError("Done URL has no shared artifact")
                decision = "reuse"
            else:
                raise UrlRegistryError("unsupported URL status")

            self._write(payload)
            return UrlClaim(decision, self._to_record(row))

    def complete(self, claim: UrlClaim, payload: Mapping[str, Any]) -> UrlRecord:
        if claim.decision != "crawl":
            raise UrlRegistryError("only a crawl claim can be completed")
        with self._locked():
            registry = self._read()
            row = self._owned_doing_row(registry, claim)
            cache_path = self._cache_path(row["url"])
            payload_sha256 = self._write_cache(cache_path, payload)
            now = self.clock()
            row.update(
                {
                    "status": "Done",
                    "workerId": None,
                    "updatedAt": now,
                    "completedAt": now,
                    "artifactPath": self._artifact_path(cache_path),
                    "artifactSha256": payload_sha256,
                    "lastError": None,
                }
            )
            self._write(registry)
            return self._to_record(row)

    def release(self, claim: UrlClaim, error: str) -> UrlRecord:
        if claim.decision != "crawl":
            raise UrlRegistryError("only a crawl claim can be released")
        if not isinstance(error, str) or not error.strip():
            raise UrlRegistryError("release error must be non-empty")
        with self._locked():
            payload = self._read()
            row = self._owned_doing_row(payload, claim)
            row.update(
                {
                    "status": "New",
                    "workerId": None,
                    "updatedAt": self.clock(),
                    "completedAt": None,
                    "lastError": error.strip(),
                }
            )
            self._write(payload)
            return self._to_record(row)

    def requeue(
        self, url: str, expected_worker_id: Optional[str] = None
    ) -> UrlRecord:
        canonical_url = normalize_crawler_url(url, self.allowed_origin)
        expected = (
            self._worker_id(expected_worker_id)
            if expected_worker_id is not None
            else None
        )
        with self._locked():
            payload = self._read()
            row = self._find(payload, canonical_url)
            if row is None:
                raise UrlRegistryError("URL is not registered")
            if expected is not None and row.get("workerId") != expected:
                raise UrlRegistryError("URL claim owner does not match")
            row.update(
                {
                    "status": "New",
                    "workerId": None,
                    "updatedAt": self.clock(),
                    "claimedAt": None,
                    "completedAt": None,
                    "artifactPath": None,
                    "artifactSha256": None,
                    "lastError": "manually requeued",
                }
            )
            self._write(payload)
            return self._to_record(row)

    def load_payload(self, record: UrlRecord) -> Dict[str, Any]:
        if record.status != "Done" or not record.artifact_path:
            raise UrlRegistryError("shared payload is only available for Done URLs")
        artifact = Path(record.artifact_path)
        if not artifact.is_absolute():
            artifact = self.path.parent / artifact
        try:
            raw = artifact.read_bytes()
        except OSError as error:
            raise UrlRegistryError("shared artifact cannot be read") from error
        if record.artifact_sha256:
            actual = hashlib.sha256(raw).hexdigest()
            if actual != record.artifact_sha256:
                raise UrlRegistryError("shared artifact checksum mismatch")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise UrlRegistryError("shared artifact is invalid JSON") from error
        if not isinstance(payload, dict):
            raise UrlRegistryError("shared artifact must contain an object")
        return payload

    def audit(self) -> Tuple[RegistryAudit, ...]:
        with self._locked():
            payload = self._read()
            return tuple(self._audit_row(row) for row in payload["items"])

    def initialize_from_snapshot(self, snapshot: Path) -> int:
        snapshot_path = Path(snapshot)
        with self._locked():
            if self.path.exists():
                raise UrlRegistryError("live URL registry already exists")
            source = self._read_path(snapshot_path, allow_missing=False)
            now = self.clock()
            imported = []
            for row in source["items"]:
                record = self._to_record(row)
                canonical_url = normalize_crawler_url(
                    record.url,
                    self.allowed_origin,
                )
                if canonical_url != record.url:
                    raise UrlRegistryError("snapshot URL is not canonical")
                categories = [self._category_key(value) for value in record.categories]
                if len(set(categories)) != len(categories):
                    raise UrlRegistryError("snapshot categories contain duplicates")
                imported.append(
                    {
                        "url": canonical_url,
                        "status": "New",
                        "categories": sorted(
                            categories,
                            key=lambda value: (value.casefold(), value),
                        ),
                        "workerId": None,
                        "attempts": record.attempts,
                        "createdAt": record.created_at,
                        "updatedAt": now,
                        "claimedAt": None,
                        "completedAt": None,
                        "artifactPath": None,
                        "artifactSha256": None,
                        "lastError": "imported from snapshot without raw artifact",
                    }
                )
            self._write({"schemaVersion": SCHEMA_VERSION, "items": imported})
            return len(imported)

    def repair_invalid_done(self) -> Tuple[UrlRecord, ...]:
        with self._locked():
            payload = self._read()
            repaired = []
            for row in payload["items"]:
                audit = self._audit_row(row)
                if row["status"] != "Done" or audit.issue is None:
                    continue
                row.update(
                    {
                        "status": "New",
                        "workerId": None,
                        "updatedAt": self.clock(),
                        "claimedAt": None,
                        "completedAt": None,
                        "artifactPath": None,
                        "artifactSha256": None,
                        "lastError": "requeued invalid Done: {}".format(
                            audit.issue
                        ),
                    }
                )
                repaired.append(self._to_record(row))
            if repaired:
                self._write(payload)
            return tuple(repaired)

    def export_snapshot(self, target: Path) -> int:
        with self._locked():
            payload = self._read()
            payload["items"].sort(
                key=lambda row: (row["url"].casefold(), row["url"])
            )
            self._atomic_json(Path(target), payload)
            return len(payload["items"])

    @contextmanager
    def _locked(self) -> Iterator[None]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _read(self) -> Dict[str, Any]:
        return self._read_path(self.path, allow_missing=True)

    def _read_path(self, path: Path, allow_missing: bool) -> Dict[str, Any]:
        if not path.exists():
            if not allow_missing:
                raise UrlRegistryError("URL registry snapshot does not exist")
            return {"schemaVersion": SCHEMA_VERSION, "items": []}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise UrlRegistryError("URL registry is not valid JSON") from error
        if not isinstance(payload, dict) or payload.get("schemaVersion") != SCHEMA_VERSION:
            raise UrlRegistryError("URL registry schemaVersion is invalid")
        items = payload.get("items")
        if not isinstance(items, list):
            raise UrlRegistryError("URL registry items must be a list")
        seen = set()
        for row in items:
            record = self._to_record(row)
            if record.url in seen:
                raise UrlRegistryError("URL registry contains a duplicate URL")
            seen.add(record.url)
        return payload

    def _audit_row(self, row: Mapping[str, Any]) -> RegistryAudit:
        record = self._to_record(row)
        if record.status == "New":
            invalid = (
                record.worker_id is not None
                or record.completed_at is not None
                or record.artifact_path is not None
                or record.artifact_sha256 is not None
            )
            return RegistryAudit(
                record.url,
                record.status,
                "invalid_state" if invalid else None,
            )
        if record.status == "Doing":
            invalid = (
                not record.worker_id
                or not record.claimed_at
                or record.completed_at is not None
                or record.artifact_path is not None
                or record.artifact_sha256 is not None
            )
            return RegistryAudit(
                record.url,
                record.status,
                "invalid_state" if invalid else None,
            )

        if (
            record.worker_id is not None
            or not record.completed_at
            or not record.artifact_path
            or not record.artifact_sha256
        ):
            return RegistryAudit(record.url, record.status, "invalid_state")

        relative = Path(record.artifact_path)
        if relative.is_absolute():
            return RegistryAudit(record.url, record.status, "invalid_state")
        root = self.path.parent.resolve()
        artifact = (self.path.parent / relative).resolve()
        try:
            artifact.relative_to(root)
        except ValueError:
            return RegistryAudit(record.url, record.status, "invalid_state")
        if not artifact.is_file():
            return RegistryAudit(record.url, record.status, "missing")
        try:
            raw = artifact.read_bytes()
        except OSError:
            return RegistryAudit(record.url, record.status, "missing")
        if hashlib.sha256(raw).hexdigest() != record.artifact_sha256:
            return RegistryAudit(record.url, record.status, "checksum_error")
        try:
            artifact_payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return RegistryAudit(record.url, record.status, "invalid_json")
        if not isinstance(artifact_payload, dict):
            return RegistryAudit(record.url, record.status, "invalid_json")
        return RegistryAudit(record.url, record.status, None)

    def _write(self, payload: Dict[str, Any]) -> None:
        payload["items"].sort(key=lambda row: (row["url"].casefold(), row["url"]))
        self._atomic_json(self.path, payload)

    def _write_cache(self, path: Path, payload: Mapping[str, Any]) -> str:
        if not isinstance(payload, Mapping):
            raise UrlRegistryError("shared payload must be an object")
        normalized = dict(payload)
        self._atomic_json(path, normalized)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def _atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".{}-".format(path.name),
            suffix=".tmp",
            dir=str(path.parent),
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as target:
                json.dump(
                    payload,
                    target,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                target.write("\n")
                target.flush()
                os.fsync(target.fileno())
            os.replace(str(temporary), str(path))
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

    def _new_row(self, url: str, category: str) -> Dict[str, Any]:
        now = self.clock()
        return {
            "url": url,
            "status": "New",
            "categories": [category],
            "workerId": None,
            "attempts": 0,
            "createdAt": now,
            "updatedAt": now,
            "claimedAt": None,
            "completedAt": None,
            "artifactPath": None,
            "artifactSha256": None,
            "lastError": None,
        }

    @staticmethod
    def _find(payload: Mapping[str, Any], url: str) -> Optional[Dict[str, Any]]:
        return next((row for row in payload["items"] if row.get("url") == url), None)

    @staticmethod
    def _add_category(row: Dict[str, Any], category: str) -> None:
        categories = set(row["categories"])
        categories.add(category)
        row["categories"] = sorted(categories, key=lambda value: (value.casefold(), value))

    def _owned_doing_row(
        self, payload: Mapping[str, Any], claim: UrlClaim
    ) -> Dict[str, Any]:
        row = self._find(payload, claim.record.url)
        if row is None or row.get("status") != "Doing":
            raise UrlRegistryError("URL claim is no longer Doing")
        if row.get("workerId") != claim.record.worker_id:
            raise UrlRegistryError("URL claim owner does not match")
        return row

    def _cache_path(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.cache_root / "{}.json".format(digest)

    def _artifact_path(self, path: Path) -> str:
        try:
            return path.relative_to(self.path.parent).as_posix()
        except ValueError:
            return str(path.resolve())

    @staticmethod
    def _category_key(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise UrlRegistryError("category key must be non-empty")
        key = value.strip().casefold()
        if not all(character.isalnum() or character in "-_" for character in key):
            raise UrlRegistryError("category key contains unsupported characters")
        return key

    @staticmethod
    def _worker_id(value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise UrlRegistryError("worker ID must be non-empty")
        return value.strip()

    @staticmethod
    def _to_record(row: Any) -> UrlRecord:
        if not isinstance(row, dict):
            raise UrlRegistryError("URL registry row must be an object")
        status = row.get("status")
        if status not in STATUSES:
            raise UrlRegistryError("URL registry status is invalid")
        categories = row.get("categories")
        if (
            not isinstance(categories, list)
            or not categories
            or not all(isinstance(value, str) and value for value in categories)
        ):
            raise UrlRegistryError("URL registry categories are invalid")
        attempts = row.get("attempts")
        if not isinstance(attempts, int) or attempts < 0:
            raise UrlRegistryError("URL registry attempts are invalid")
        required_strings = ("url", "createdAt", "updatedAt")
        if not all(isinstance(row.get(key), str) and row[key] for key in required_strings):
            raise UrlRegistryError("URL registry row identity is invalid")
        optional_strings = (
            "workerId",
            "claimedAt",
            "completedAt",
            "artifactPath",
            "artifactSha256",
            "lastError",
        )
        if not all(row.get(key) is None or isinstance(row.get(key), str) for key in optional_strings):
            raise UrlRegistryError("URL registry row metadata is invalid")
        return UrlRecord(
            url=row["url"],
            status=status,
            categories=tuple(categories),
            worker_id=row.get("workerId"),
            attempts=attempts,
            created_at=row["createdAt"],
            updated_at=row["updatedAt"],
            claimed_at=row.get("claimedAt"),
            completed_at=row.get("completedAt"),
            artifact_path=row.get("artifactPath"),
            artifact_sha256=row.get("artifactSha256"),
            last_error=row.get("lastError"),
        )
