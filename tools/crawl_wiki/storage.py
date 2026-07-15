import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from tools.crawl_wiki.item_seeds import ItemSeed
from tools.crawl_wiki.models import CrawlSummary, SCHEMA_VERSION
from tools.crawl_wiki.parser import normalize_base_url, safe_image_extension


class StorageError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def encode_json_line(record: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


class CrawlStorage:
    JSONL_NAMES = (
        "seeds.jsonl",
        "pages.jsonl",
        "recipes.jsonl",
        "images.jsonl",
        "links.jsonl",
        "errors.jsonl",
    )

    def __init__(
        self,
        output: Path,
        base_url: str,
        namespaces: Sequence[int],
        fresh: bool = False,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        self.output = Path(output)
        self.base_url = normalize_base_url(base_url)
        self.namespaces = tuple(int(value) for value in namespaces)
        self.clock = clock
        self.state_path = self.output / "state.sqlite"
        if fresh and self.state_path.exists():
            raise StorageError(
                "--fresh requires an output directory without an existing crawl"
            )
        self.output.mkdir(parents=True, exist_ok=True)
        self.originals_dir = self.output / "images" / "original"
        self.parts_dir = self.output / "images" / ".parts"
        self.originals_dir.mkdir(parents=True, exist_ok=True)
        self.parts_dir.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.state_path))
        self.connection.row_factory = sqlite3.Row
        try:
            self._initialize_database()
            self._verify_configuration()
            self._recover()
        except Exception:
            self.connection.close()
            raise

    def __enter__(self) -> "CrawlStorage":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        del exc_type, exc_value, traceback
        self.close()

    def close(self) -> None:
        if getattr(self, "connection", None) is not None:
            self.connection.close()
            self.connection = None

    def _initialize_database(self) -> None:
        self.connection.executescript(
            """
            pragma journal_mode = wal;
            pragma synchronous = full;
            create table if not exists metadata (
                key text primary key,
                value text not null
            );
            create table if not exists page_queue (
                page_id integer primary key,
                namespace integer not null,
                title text not null,
                status text not null default 'pending',
                attempts integer not null default 0,
                record_offset integer,
                last_error text
            );
            create unique index if not exists page_queue_title on page_queue(title);
            create table if not exists image_queue (
                title text primary key,
                page_id integer,
                status text not null default 'pending',
                attempts integer not null default 0,
                record_offset integer,
                last_error text
            );
            create table if not exists seed_metadata (
                title text primary key,
                href text not null,
                icon_title text,
                icon_thumbnail_url text,
                source_sections text not null
            );
            create table if not exists errors (
                stage text not null,
                subject text not null,
                url text,
                attempts integer not null,
                error_type text not null,
                message text not null,
                status integer,
                code text,
                retryable integer not null,
                timestamp text not null,
                primary key(stage, subject)
            );
            create table if not exists compaction_offsets (
                kind text not null,
                record_key text not null,
                sort_key text not null,
                source_offset integer not null,
                primary key(kind, record_key)
            );
            """
        )
        self.connection.commit()

    def _metadata(self, key: str) -> Optional[str]:
        row = self.connection.execute(
            "select value from metadata where key=?", (key,)
        ).fetchone()
        return row[0] if row else None

    def _set_metadata(self, key: str, value: str) -> None:
        self.connection.execute(
            "insert into metadata(key,value) values(?,?) "
            "on conflict(key) do update set value=excluded.value",
            (key, value),
        )

    def _verify_configuration(self) -> None:
        expected = {
            "schema_version": str(SCHEMA_VERSION),
            "base_url": self.base_url,
            "namespaces": json.dumps(list(self.namespaces), separators=(",", ":")),
        }
        for key, value in expected.items():
            current = self._metadata(key)
            if current is not None and current != value:
                raise StorageError(
                    "existing crawl {} is incompatible (expected {!r}, found {!r})".format(
                        key, value, current
                    )
                )
            self._set_metadata(key, value)
        if self._metadata("started_at") is None:
            self._set_metadata("started_at", self.clock())
        self.connection.commit()

    def _recover(self) -> None:
        self.connection.execute(
            "update page_queue set status='pending' where status='processing'"
        )
        self.connection.execute(
            "update image_queue set status='pending' where status='processing'"
        )
        self.connection.commit()
        for name in self.JSONL_NAMES:
            self._truncate_incomplete_tail(self.output / name)
        for part in self.parts_dir.glob("*.part"):
            part.unlink()

    @staticmethod
    def _truncate_incomplete_tail(path: Path) -> None:
        if not path.exists() or path.stat().st_size == 0:
            return
        with path.open("r+b") as handle:
            handle.seek(-1, os.SEEK_END)
            if handle.read(1) == b"\n":
                return
            position = handle.tell() - 1
            last_newline = -1
            while position >= 0:
                start = max(0, position - 65535)
                handle.seek(start)
                block = handle.read(position - start + 1)
                found = block.rfind(b"\n")
                if found >= 0:
                    last_newline = start + found
                    break
                position = start - 1
            handle.truncate(last_newline + 1)
            handle.flush()
            os.fsync(handle.fileno())

    def enqueue_pages(self, pages: Iterable[Mapping[str, Any]]) -> int:
        inserted = 0
        with self.connection:
            for page in pages:
                page_id = page.get("pageid")
                namespace = page.get("ns")
                title = page.get("title")
                if not isinstance(page_id, int) or not isinstance(namespace, int) or not isinstance(title, str):
                    raise StorageError("discovered page has invalid ID, namespace, or title")
                cursor = self.connection.execute(
                    "insert or ignore into page_queue(page_id,namespace,title) values(?,?,?)",
                    (page_id, namespace, title),
                )
                inserted += cursor.rowcount
        return inserted

    def page_count(self) -> int:
        return int(
            self.connection.execute("select count(*) from page_queue").fetchone()[0]
        )

    def pending_page_count(self) -> int:
        return int(
            self.connection.execute(
                "select count(*) from page_queue where status='pending'"
            ).fetchone()[0]
        )

    def pending_image_count(self) -> int:
        return int(
            self.connection.execute(
                "select count(*) from image_queue where status='pending'"
            ).fetchone()[0]
        )

    def save_seeds(self, seeds: Iterable[ItemSeed]) -> None:
        with self.connection:
            for seed in seeds:
                self.connection.execute(
                    "insert into seed_metadata(title,href,icon_title,icon_thumbnail_url,source_sections) "
                    "values(?,?,?,?,?) on conflict(title) do update set "
                    "href=excluded.href,icon_title=excluded.icon_title,"
                    "icon_thumbnail_url=excluded.icon_thumbnail_url,"
                    "source_sections=excluded.source_sections",
                    (
                        seed.title,
                        seed.href,
                        seed.icon_title,
                        seed.icon_thumbnail_url,
                        json.dumps(
                            list(seed.source_sections),
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                    ),
                )
        self._write_seeds()

    def seed_for_title(self, title: str) -> Optional[Dict[str, Any]]:
        row = self.connection.execute(
            "select title,href,icon_title,icon_thumbnail_url,source_sections "
            "from seed_metadata where title=?",
            (title,),
        ).fetchone()
        if row is None:
            return None
        record = dict(row)
        record["schema_version"] = SCHEMA_VERSION
        record["source_sections"] = json.loads(record["source_sections"])
        return record

    def _write_seeds(self) -> None:
        path = self.output / "seeds.jsonl"
        temporary = path.with_name(path.name + ".tmp")
        rows = self.connection.execute(
            "select title,href,icon_title,icon_thumbnail_url,source_sections "
            "from seed_metadata order by title collate nocase,title"
        )
        with temporary.open("wb") as handle:
            for row in rows:
                record = dict(row)
                record["schema_version"] = SCHEMA_VERSION
                record["source_sections"] = json.loads(
                    record["source_sections"]
                )
                handle.write(encode_json_line(record))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))

    def _claim(self, table: str, order_by: str) -> Optional[Dict[str, Any]]:
        try:
            self.connection.execute("begin immediate")
            row = self.connection.execute(
                "select * from {} where status='pending' order by {} limit 1".format(
                    table, order_by
                )
            ).fetchone()
            if row is None:
                self.connection.commit()
                return None
            key_name = "page_id" if table == "page_queue" else "title"
            self.connection.execute(
                "update {} set status='processing',attempts=attempts+1 where {}=?".format(
                    table, key_name
                ),
                (row[key_name],),
            )
            self.connection.commit()
            result = dict(row)
            result["attempts"] = int(result["attempts"]) + 1
            result["status"] = "processing"
            return result
        except Exception:
            self.connection.rollback()
            raise

    def claim_page(self) -> Optional[Dict[str, Any]]:
        return self._claim("page_queue", "page_id")

    def enqueue_images(
        self, titles: Iterable[str], page_id: Optional[int] = None
    ) -> int:
        inserted = 0
        with self.connection:
            for title in sorted(set(titles), key=lambda value: (value.casefold(), value)):
                cursor = self.connection.execute(
                    "insert into image_queue(title,page_id) values(?,?) "
                    "on conflict(title) do update set page_id=coalesce(image_queue.page_id,excluded.page_id)",
                    (title, page_id),
                )
                inserted += int(cursor.rowcount > 0)
        return inserted

    def claim_image(self) -> Optional[Dict[str, Any]]:
        return self._claim("image_queue", "title collate nocase, title")

    def _append_record(self, filename: str, record: Mapping[str, Any]) -> int:
        path = self.output / filename
        with path.open("ab") as handle:
            offset = handle.tell()
            handle.write(encode_json_line(record))
            handle.flush()
            os.fsync(handle.fileno())
        return offset

    def complete_page(
        self,
        page_id: int,
        page_record: Mapping[str, Any],
        link_records: Iterable[Mapping[str, Any]],
        image_titles: Set[str],
        recipe_records: Iterable[Mapping[str, Any]] = (),
    ) -> None:
        page_offset = self._append_record("pages.jsonl", page_record)
        for record in link_records:
            self._append_record("links.jsonl", record)
        for record in recipe_records:
            self._append_record("recipes.jsonl", record)
        with self.connection:
            for title in sorted(image_titles, key=lambda value: (value.casefold(), value)):
                self.connection.execute(
                    "insert into image_queue(title,page_id) values(?,?) "
                    "on conflict(title) do update set page_id=coalesce(image_queue.page_id,excluded.page_id)",
                    (title, page_id),
                )
            self.connection.execute(
                "update page_queue set status='done',record_offset=?,last_error=null where page_id=?",
                (page_offset, page_id),
            )
            self.connection.execute(
                "delete from errors where stage='page' and subject=?",
                (str(page_id),),
            )

    def complete_image(
        self, title: str, image_record: Mapping[str, Any]
    ) -> None:
        offset = self._append_record("images.jsonl", image_record)
        with self.connection:
            self.connection.execute(
                "update image_queue set status='done',record_offset=?,last_error=null where title=?",
                (offset, title),
            )
            self.connection.execute(
                "delete from errors where stage='image' and subject=?", (title,)
            )

    def _fail(
        self,
        table: str,
        key_name: str,
        key_value: Any,
        error: Mapping[str, Any],
    ) -> None:
        row = self.connection.execute(
            "select attempts from {} where {}=?".format(table, key_name),
            (key_value,),
        ).fetchone()
        attempts = int(row[0]) if row else 1
        stage = str(error["stage"])
        subject = str(error["subject"])
        message = str(error["message"])
        with self.connection:
            self.connection.execute(
                "update {} set status='failed',last_error=? where {}=?".format(
                    table, key_name
                ),
                (message, key_value),
            )
            self.connection.execute(
                "insert into errors(stage,subject,url,attempts,error_type,message,status,code,retryable,timestamp) "
                "values(?,?,?,?,?,?,?,?,?,?) "
                "on conflict(stage,subject) do update set "
                "url=excluded.url,attempts=excluded.attempts,error_type=excluded.error_type,"
                "message=excluded.message,status=excluded.status,code=excluded.code,"
                "retryable=excluded.retryable,timestamp=excluded.timestamp",
                (
                    stage,
                    subject,
                    error.get("url"),
                    attempts,
                    str(error.get("error_type", "Error")),
                    message,
                    error.get("status"),
                    error.get("code"),
                    int(bool(error.get("retryable", False))),
                    str(error.get("timestamp", self.clock())),
                ),
            )

    def fail_page(self, page_id: int, error: Mapping[str, Any]) -> None:
        self._fail("page_queue", "page_id", page_id, error)

    def fail_image(self, title: str, error: Mapping[str, Any]) -> None:
        self._fail("image_queue", "title", title, error)

    def retry_errors(self) -> None:
        with self.connection:
            self.connection.execute(
                "update page_queue set status='pending',last_error=null where status='failed'"
            )
            self.connection.execute(
                "update image_queue set status='pending',last_error=null where status='failed'"
            )
            self.connection.execute("delete from errors")

    def get_discovery_token(self, namespace: int) -> Optional[str]:
        return self._metadata("discovery:{}:token".format(namespace))

    def is_discovery_complete(self, namespace: int) -> bool:
        return self._metadata("discovery:{}:complete".format(namespace)) == "1"

    def set_discovery_token(self, namespace: int, token: str) -> None:
        with self.connection:
            self._set_metadata("discovery:{}:token".format(namespace), token)

    def mark_discovery_complete(self, namespace: int) -> None:
        with self.connection:
            self.connection.execute(
                "delete from metadata where key=?",
                ("discovery:{}:token".format(namespace),),
            )
            self._set_metadata("discovery:{}:complete".format(namespace), "1")

    def is_item_discovery_complete(self) -> bool:
        return self._metadata("items:discovery:complete") == "1"

    def mark_item_discovery_complete(self) -> None:
        with self.connection:
            self._set_metadata("items:discovery:complete", "1")

    def new_image_part(self) -> Path:
        file_descriptor, name = tempfile.mkstemp(
            prefix="image-", suffix=".part", dir=str(self.parts_dir)
        )
        os.close(file_descriptor)
        return Path(name)

    def commit_image_file(
        self,
        part_path: Path,
        sha256: str,
        url: str,
        mime: Optional[str],
    ) -> str:
        if len(sha256) != 64 or any(
            character not in "0123456789abcdef" for character in sha256
        ):
            raise StorageError("image SHA-256 must be 64 lowercase hex characters")
        part_path = Path(part_path)
        extension = safe_image_extension(url, mime)
        destination = self.originals_dir / (sha256 + extension)
        if destination.exists():
            part_path.unlink(missing_ok=True)
        else:
            os.replace(str(part_path), str(destination))
        return destination.relative_to(self.output).as_posix()

    @staticmethod
    def _record_keys(
        filename: str, record: Mapping[str, Any]
    ) -> Tuple[str, str]:
        if filename == "pages.jsonl":
            page_id = int(record["page_id"])
            return str(page_id), "{:020d}".format(page_id)
        if filename == "images.jsonl":
            title = str(record["title"])
            return title, title.casefold() + "\0" + title
        if filename == "links.jsonl":
            source_page_id = int(record["source_page_id"])
            target_namespace = int(record["target_namespace"])
            target_title = str(record["target_title"])
            identity = json.dumps(
                [source_page_id, target_namespace, target_title],
                ensure_ascii=False,
                separators=(",", ":"),
            )
            sort_key = "{:020d}\0{:010d}\0{}\0{}".format(
                source_page_id,
                target_namespace,
                target_title.casefold(),
                target_title,
            )
            return identity, sort_key
        if filename == "seeds.jsonl":
            title = str(record["title"])
            return title, title.casefold() + "\0" + title
        if filename == "recipes.jsonl":
            page_id = int(record["page_id"])
            identity = json.dumps(
                record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            result = str(record["result"])
            source = str(record["source"])
            variant = str(record["variant"])
            sort_key = "{:020d}\0{}\0{}\0{}\0{}".format(
                page_id,
                result.casefold(),
                source.casefold(),
                variant.casefold(),
                identity,
            )
            return identity, sort_key
        stage = str(record["stage"])
        subject = str(record["subject"])
        identity = json.dumps(
            [stage, subject], ensure_ascii=False, separators=(",", ":")
        )
        return identity, stage.casefold() + "\0" + stage + "\0" + subject

    def _compact(
        self, filename: str
    ) -> Tuple[int, Dict[str, Dict[str, int]]]:
        path = self.output / filename
        path.touch(exist_ok=True)
        with self.connection:
            self.connection.execute(
                "delete from compaction_offsets where kind=?", (filename,)
            )

        scanned = 0
        with path.open("rb") as handle:
            line_number = 0
            while True:
                source_offset = handle.tell()
                line = handle.readline()
                if not line:
                    break
                line_number += 1
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise StorageError(
                        "{} line {} is invalid JSON: {}".format(
                            filename, line_number, error
                        )
                    )
                if not isinstance(record, dict):
                    raise StorageError(
                        "{} line {} must contain an object".format(
                            filename, line_number
                        )
                    )
                record_key, sort_key = self._record_keys(filename, record)
                self.connection.execute(
                    "insert into compaction_offsets(kind,record_key,sort_key,source_offset) "
                    "values(?,?,?,?) on conflict(kind,record_key) do update set "
                    "sort_key=excluded.sort_key,source_offset=excluded.source_offset",
                    (filename, record_key, sort_key, source_offset),
                )
                scanned += 1
                if scanned % 5000 == 0:
                    self.connection.commit()
        self.connection.commit()

        temporary = path.with_name(path.name + ".tmp")
        index_data: Dict[str, Dict[str, int]] = {}
        count = 0
        with path.open("rb") as source, temporary.open("wb") as output:
            rows = self.connection.execute(
                "select source_offset from compaction_offsets where kind=? "
                "order by sort_key,record_key",
                (filename,),
            )
            for row in rows:
                source.seek(int(row["source_offset"]))
                line = source.readline()
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise StorageError(
                        "{} changed during compaction: {}".format(
                            filename, error
                        )
                    )
                final_offset = output.tell()
                output.write(encode_json_line(record))
                count += 1
                if filename == "pages.jsonl":
                    index_data.setdefault("by_id", {})[
                        str(record["page_id"])
                    ] = final_offset
                    index_data.setdefault("by_title", {})[
                        str(record["title"])
                    ] = final_offset
                elif filename == "images.jsonl":
                    index_data.setdefault("by_title", {})[
                        str(record["title"])
                    ] = final_offset
            output.flush()
            os.fsync(output.fileno())
        os.replace(str(temporary), str(path))
        return count, index_data

    def _write_errors(self) -> None:
        path = self.output / "errors.jsonl"
        temporary = path.with_name(path.name + ".tmp")
        rows = self.connection.execute(
            "select stage,subject,url,attempts,error_type,message,status,code,retryable,timestamp "
            "from errors order by stage,subject"
        ).fetchall()
        with temporary.open("wb") as handle:
            for row in rows:
                record = dict(row)
                record["schema_version"] = SCHEMA_VERSION
                record["retryable"] = bool(record["retryable"])
                handle.write(encode_json_line(record))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(64 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
        temporary = path.with_name(path.name + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary), str(path))

    def finalize(self, options: Mapping[str, Any]) -> CrawlSummary:
        self._write_seeds()
        self._write_errors()
        seed_count, _ = self._compact("seeds.jsonl")
        page_count, page_index = self._compact("pages.jsonl")
        recipe_count, _ = self._compact("recipes.jsonl")
        image_count, image_index = self._compact("images.jsonl")
        link_count, _ = self._compact("links.jsonl")
        error_count, _ = self._compact("errors.jsonl")

        index = {
            "schema_version": SCHEMA_VERSION,
            "pages": {
                "by_id": page_index.get("by_id", {}),
                "by_title": page_index.get("by_title", {}),
            },
            "images": {"by_title": image_index.get("by_title", {})},
        }
        self._write_json_atomic(self.output / "index.json", index)
        checksums = {
            name: self._sha256(self.output / name) for name in self.JSONL_NAMES
        }
        pending_pages = self.pending_page_count()
        pending_images = self.pending_image_count()
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "base_url": self.base_url,
            "namespaces": list(self.namespaces),
            "started_at": self._metadata("started_at"),
            "completed_at": self.clock(),
            "status": (
                "partial" if pending_pages or pending_images else "complete"
            ),
            "options": dict(options),
            "counts": {
                "seeds": seed_count,
                "pages": page_count,
                "recipes": recipe_count,
                "images": image_count,
                "links": link_count,
                "failures": error_count,
                "pending_pages": pending_pages,
                "pending_images": pending_images,
            },
            "unresolved_errors": error_count,
            "checksums": checksums,
        }
        self._write_json_atomic(self.output / "manifest.json", manifest)
        return CrawlSummary(
            pages=page_count,
            images=image_count,
            links=link_count,
            failures=error_count,
            pending_pages=pending_pages,
            pending_images=pending_images,
        )
