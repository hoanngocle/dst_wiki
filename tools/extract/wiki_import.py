"""Import a completed selective wiki crawl into the audit SQLite database."""

import hashlib
import json
import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from tools.extract.wiki_mapping import build_entity_index, map_page
from tools.extract.wiki_structures import normalize_structure_page


DATASET_FILES = ("pages.jsonl", "recipes.jsonl", "images.jsonl")
WIKI_TABLES = (
    "wiki_recipe_ingredients",
    "wiki_recipes",
    "wiki_structure_details",
    "wiki_entity_mappings",
    "wiki_images",
    "wiki_pages",
    "wiki_import_runs",
)

WIKI_SCHEMA = (
    """CREATE TABLE wiki_import_runs (
      run_id TEXT PRIMARY KEY,
      source_path TEXT NOT NULL,
      manifest_sha256 TEXT NOT NULL,
      imported_at TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status = 'complete'),
      pages_count INTEGER NOT NULL,
      recipes_count INTEGER NOT NULL,
      ingredients_count INTEGER NOT NULL,
      images_count INTEGER NOT NULL,
      mapped_count INTEGER NOT NULL,
      unmatched_count INTEGER NOT NULL
    )""",
    """CREATE TABLE wiki_pages (
      page_id INTEGER PRIMARY KEY,
      title TEXT NOT NULL UNIQUE,
      display_title TEXT,
      canonical_url TEXT NOT NULL,
      revision_id INTEGER NOT NULL,
      revision_timestamp TEXT NOT NULL,
      revision_sha1 TEXT NOT NULL,
      content_model TEXT NOT NULL,
      html TEXT NOT NULL,
      wikitext TEXT NOT NULL,
      plain_text TEXT NOT NULL,
      categories_json TEXT NOT NULL,
      redirect_target TEXT,
      fetched_at TEXT NOT NULL,
      source_schema_version INTEGER NOT NULL
    )""",
    """CREATE TABLE wiki_images (
      title TEXT PRIMARY KEY,
      mediawiki_page_id INTEGER NOT NULL,
      original_url TEXT NOT NULL,
      local_path TEXT NOT NULL,
      mime TEXT NOT NULL,
      byte_size INTEGER NOT NULL,
      sha256 TEXT NOT NULL,
      mediawiki_sha1 TEXT,
      width INTEGER,
      height INTEGER,
      fetched_at TEXT NOT NULL,
      published_path TEXT,
      source_schema_version INTEGER NOT NULL
    )""",
    """CREATE TABLE wiki_entity_mappings (
      page_id INTEGER PRIMARY KEY,
      entity_namespace TEXT,
      entity_prefab_id TEXT,
      method TEXT NOT NULL,
      confidence REAL NOT NULL,
      evidence_json TEXT NOT NULL,
      selected INTEGER NOT NULL CHECK(selected IN (0, 1)),
      FOREIGN KEY(page_id) REFERENCES wiki_pages(page_id),
      FOREIGN KEY(entity_namespace, entity_prefab_id)
        REFERENCES entities(namespace, prefab_id),
      CHECK((selected = 1 AND entity_namespace IS NOT NULL AND entity_prefab_id IS NOT NULL)
         OR (selected = 0 AND entity_namespace IS NULL AND entity_prefab_id IS NULL))
    )""",
    """CREATE TABLE wiki_recipes (
      recipe_id TEXT PRIMARY KEY,
      page_id INTEGER NOT NULL,
      result_title TEXT NOT NULL,
      source_template TEXT NOT NULL,
      station TEXT,
      tab TEXT,
      tier TEXT,
      character TEXT,
      dlc TEXT,
      variant TEXT,
      note TEXT,
      source_schema_version INTEGER NOT NULL,
      FOREIGN KEY(page_id) REFERENCES wiki_pages(page_id)
    )""",
    """CREATE TABLE wiki_recipe_ingredients (
      recipe_id TEXT NOT NULL,
      position INTEGER NOT NULL,
      ingredient_title TEXT NOT NULL,
      amount REAL NOT NULL CHECK(amount != 0),
      amount_text TEXT,
      PRIMARY KEY(recipe_id, position),
      FOREIGN KEY(recipe_id) REFERENCES wiki_recipes(recipe_id)
    )""",
    """CREATE TABLE wiki_structure_details (
      page_id INTEGER PRIMARY KEY,
      details_json TEXT NOT NULL,
      source_schema_version INTEGER NOT NULL,
      FOREIGN KEY(page_id) REFERENCES wiki_pages(page_id)
    )""",
    "CREATE INDEX wiki_mapping_entity_idx ON wiki_entity_mappings(entity_namespace, entity_prefab_id)",
    "CREATE INDEX wiki_recipe_page_idx ON wiki_recipes(page_id)",
    "CREATE INDEX wiki_image_sha_idx ON wiki_images(sha256)",
)


@dataclass(frozen=True)
class ImportSummary:
    pages: int
    recipes: int
    ingredients: int
    images: int
    mapped: int
    unmatched: int


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _load_object(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"required crawl file is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON at {path}: {error.msg}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return value


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"required crawl dataset is missing: {path}")
    rows = []
    with path.open("r", encoding="utf-8") as source:
        for line_number, raw in enumerate(source, 1):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"invalid JSONL at {path}:{line_number}: {error.msg}"
                ) from error
            if not isinstance(value, dict):
                raise ValueError(
                    f"JSONL row must be an object at {path}:{line_number}"
                )
            rows.append(value)
    return rows


def _required_int(row: Mapping[str, Any], field: str, context: str) -> int:
    value = row.get(field)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{context}.{field} must be an integer")
    return value


def _required_string(row: Mapping[str, Any], field: str, context: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{field} must be a non-empty string")
    return value


def _optional_string(row: Mapping[str, Any], field: str, context: str) -> Optional[str]:
    value = row.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{context}.{field} must be a string or null")
    return value


def _validate_manifest(crawl_root: Path) -> Tuple[Dict[str, Any], str]:
    manifest_path = crawl_root / "manifest.json"
    manifest = _load_object(manifest_path)
    if manifest.get("schema_version") != 1:
        raise ValueError("crawl manifest schema_version must be 1")
    if manifest.get("status") != "complete":
        raise ValueError("crawl manifest status must be complete")
    options = manifest.get("options")
    if not isinstance(options, dict) or options.get("profile") != "items":
        raise ValueError("crawl manifest must use the items profile")
    counts = manifest.get("counts")
    checksums = manifest.get("checksums")
    if not isinstance(counts, dict) or not isinstance(checksums, dict):
        raise ValueError("crawl manifest counts and checksums must be objects")
    for field in ("failures", "pending_pages", "pending_images"):
        if counts.get(field, 0) != 0:
            raise ValueError(f"crawl manifest {field} must be zero")
    for filename in DATASET_FILES:
        expected = checksums.get(filename)
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError(f"crawl manifest checksum is missing for {filename}")
        actual = _sha256(crawl_root / filename)
        if actual != expected:
            raise ValueError(
                f"checksum mismatch for {filename}: expected {expected}, got {actual}"
            )
    index = _load_object(crawl_root / "index.json")
    if index.get("schema_version") != 1:
        raise ValueError("crawl index schema_version must be 1")
    if not isinstance(index.get("pages"), dict) or not isinstance(index.get("images"), dict):
        raise ValueError("crawl index pages and images must be objects")
    return manifest, _sha256(manifest_path)


def _validate_pages(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    page_ids = set()
    titles = set()
    for position, row in enumerate(rows):
        context = f"pages[{position}]"
        if row.get("schema_version") != 1:
            raise ValueError(f"{context}.schema_version must be 1")
        page_id = _required_int(row, "page_id", context)
        title = _required_string(row, "title", context)
        if page_id in page_ids:
            raise ValueError(f"duplicate wiki page_id {page_id}")
        if title in titles:
            raise ValueError(f"duplicate wiki title {title}")
        revision = row.get("revision")
        if not isinstance(revision, dict):
            raise ValueError(f"{context}.revision must be an object")
        categories = row.get("categories")
        if not isinstance(categories, list) or not all(
            isinstance(category, str) and category.strip() for category in categories
        ):
            raise ValueError(f"{context}.categories must contain strings")
        page_ids.add(page_id)
        titles.add(title)
        result.append(
            {
                "page_id": page_id,
                "title": title,
                "display_title": _optional_string(row, "display_title", context),
                "canonical_url": _required_string(row, "canonical_url", context),
                "revision_id": _required_int(revision, "id", context + ".revision"),
                "revision_timestamp": _required_string(
                    revision, "timestamp", context + ".revision"
                ),
                "revision_sha1": _required_string(
                    revision, "sha1", context + ".revision"
                ),
                "content_model": _required_string(row, "content_model", context),
                "html": row.get("html") if isinstance(row.get("html"), str) else "",
                "wikitext": row.get("wikitext")
                if isinstance(row.get("wikitext"), str)
                else "",
                "plain_text": row.get("plain_text")
                if isinstance(row.get("plain_text"), str)
                else "",
                "categories_json": _canonical_json(sorted(set(categories))),
                "redirect_target": _optional_string(row, "redirect_target", context),
                "fetched_at": _required_string(row, "fetched_at", context),
                "source_schema_version": 1,
                "mapping_input": row,
            }
        )
    return sorted(result, key=lambda value: value["page_id"])


def _recipe_id(row: Mapping[str, Any], occurrence: int) -> str:
    digest = hashlib.sha256(_canonical_json(row).encode("utf-8")).hexdigest()
    return f"wiki-recipe:{digest}:{occurrence}"


def _ingredient_amount(value: Any, context: str) -> Tuple[float, Optional[str]]:
    raw_text = value if isinstance(value, str) else None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        amount = float(value)
    elif isinstance(value, str):
        match = re.match(r"^\s*\(?\s*(-?\d+(?:\.\d+)?)", value)
        if match is None:
            raise ValueError(f"{context}.count must start with a number")
        amount = float(match.group(1))
    else:
        raise ValueError(f"{context}.count must be numeric")
    if not math.isfinite(amount) or amount == 0:
        raise ValueError(f"{context}.count must be non-zero")
    return amount, raw_text


def _validate_recipes(
    rows: Sequence[Dict[str, Any]], page_ids: Iterable[int]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    known_pages = set(page_ids)
    recipes = []
    ingredients = []
    occurrences: Dict[str, int] = {}
    for row_number, row in enumerate(rows):
        context = f"recipes[{row_number}]"
        if row.get("schema_version") != 1:
            raise ValueError(f"{context}.schema_version must be 1")
        page_id = _required_int(row, "page_id", context)
        if page_id not in known_pages:
            raise ValueError(f"recipe references unknown page_id {page_id}")
        result_title = _required_string(row, "result", context)
        source_template = _required_string(row, "source", context)
        raw_ingredients = row.get("ingredients")
        if not isinstance(raw_ingredients, list):
            raise ValueError(f"{context}.ingredients must be a list")
        canonical = _canonical_json(row)
        occurrence = occurrences.get(canonical, 0)
        occurrences[canonical] = occurrence + 1
        recipe_id = _recipe_id(row, occurrence)
        recipes.append(
            {
                "recipe_id": recipe_id,
                "page_id": page_id,
                "result_title": result_title,
                "source_template": source_template,
                "station": _optional_string(row, "station", context),
                "tab": _optional_string(row, "tab", context),
                "tier": _optional_string(row, "tier", context),
                "character": _optional_string(row, "character", context),
                "dlc": _optional_string(row, "dlc", context),
                "variant": _optional_string(row, "variant", context),
                "note": _optional_string(row, "note", context),
                "source_schema_version": 1,
            }
        )
        for position, ingredient in enumerate(raw_ingredients):
            if not isinstance(ingredient, dict):
                raise ValueError(f"{context}.ingredients[{position}] must be an object")
            amount, amount_text = _ingredient_amount(
                ingredient.get("count"), f"{context}.ingredients[{position}]"
            )
            ingredients.append(
                {
                    "recipe_id": recipe_id,
                    "position": position,
                    "ingredient_title": _required_string(
                        ingredient, "title", f"{context}.ingredients[{position}]"
                    ),
                    "amount": amount,
                    "amount_text": amount_text,
                }
            )
    return (
        sorted(recipes, key=lambda value: value["recipe_id"]),
        sorted(
            ingredients,
            key=lambda value: (value["recipe_id"], value["position"]),
        ),
    )


def _validate_images(
    rows: Sequence[Dict[str, Any]], crawl_root: Path
) -> List[Dict[str, Any]]:
    result = []
    titles = set()
    root = crawl_root.resolve()
    for position, row in enumerate(rows):
        context = f"images[{position}]"
        if row.get("schema_version") != 1:
            raise ValueError(f"{context}.schema_version must be 1")
        title = _required_string(row, "title", context)
        if title in titles:
            raise ValueError(f"duplicate wiki image title {title}")
        local_path = _required_string(row, "local_path", context)
        relative = Path(local_path)
        if relative.is_absolute():
            raise ValueError(f"{context}.local_path must be relative")
        source = (root / relative).resolve()
        try:
            source.relative_to(root)
        except ValueError as error:
            raise ValueError(f"{context}.local_path escapes crawl root") from error
        if not source.is_file():
            raise ValueError(f"referenced wiki image is missing: {local_path}")
        expected_sha = _required_string(row, "sha256", context)
        actual_sha = _sha256(source)
        if actual_sha != expected_sha:
            raise ValueError(f"wiki image checksum mismatch: {local_path}")
        byte_size = _required_int(row, "byte_size", context)
        if source.stat().st_size != byte_size:
            raise ValueError(f"wiki image byte_size mismatch: {local_path}")
        width = row.get("width")
        height = row.get("height")
        for field, value in (("width", width), ("height", height)):
            if value is not None and (
                not isinstance(value, int) or isinstance(value, bool) or value <= 0
            ):
                raise ValueError(f"{context}.{field} must be a positive integer or null")
        titles.add(title)
        result.append(
            {
                "title": title,
                "mediawiki_page_id": _required_int(row, "page_id", context),
                "original_url": _required_string(row, "original_url", context),
                "local_path": relative.as_posix(),
                "mime": _required_string(row, "mime", context),
                "byte_size": byte_size,
                "sha256": expected_sha,
                "mediawiki_sha1": _optional_string(row, "mediawiki_sha1", context),
                "width": width,
                "height": height,
                "fetched_at": _required_string(row, "fetched_at", context),
                "published_path": None,
                "source_schema_version": 1,
            }
        )
    return sorted(result, key=lambda value: value["title"])


def _insert_rows(
    connection: sqlite3.Connection,
    table: str,
    columns: Sequence[str],
    rows: Iterable[Mapping[str, Any]],
) -> None:
    names = ",".join(columns)
    placeholders = ",".join("?" for _ in columns)
    connection.executemany(
        f"INSERT INTO {table} ({names}) VALUES ({placeholders})",
        ([row[column] for column in columns] for row in rows),
    )


def import_wiki(database_path: Path, crawl_root: Path) -> ImportSummary:
    database_path = Path(database_path)
    crawl_root = Path(crawl_root)
    if not database_path.is_file():
        raise ValueError(f"database does not exist: {database_path}")
    manifest, manifest_sha = _validate_manifest(crawl_root)
    raw_pages = read_jsonl(crawl_root / "pages.jsonl")
    raw_recipes = read_jsonl(crawl_root / "recipes.jsonl")
    raw_images = read_jsonl(crawl_root / "images.jsonl")
    counts = manifest["counts"]
    for name, rows in (
        ("pages", raw_pages),
        ("recipes", raw_recipes),
        ("images", raw_images),
    ):
        if counts.get(name) != len(rows):
            raise ValueError(
                f"manifest {name} count mismatch: expected {counts.get(name)}, got {len(rows)}"
            )
    pages = _validate_pages(raw_pages)
    structure_details = [
        {
            "page_id": page["page_id"],
            "details_json": _canonical_json(details),
            "source_schema_version": 1,
        }
        for page in pages
        for details in [normalize_structure_page(page["mapping_input"])]
        if details is not None
    ]
    recipes, ingredients = _validate_recipes(
        raw_recipes, (page["page_id"] for page in pages)
    )
    images = _validate_images(raw_images, crawl_root)

    connection = sqlite3.connect(database_path)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        entity_rows = connection.execute(
            "select namespace,prefab_id,name_en from entities order by namespace,prefab_id"
        ).fetchall()
        entity_index = build_entity_index(
            {
                "namespace": namespace,
                "prefab_id": prefab_id,
                "name_en": name_en,
            }
            for namespace, prefab_id, name_en in entity_rows
        )
        mappings = []
        for page in pages:
            decision = map_page(page["mapping_input"], entity_index)
            namespace = None
            prefab_id = None
            if decision.entity_key is not None:
                namespace, prefab_id = decision.entity_key.split(":", 1)
            mappings.append(
                {
                    "page_id": page["page_id"],
                    "entity_namespace": namespace,
                    "entity_prefab_id": prefab_id,
                    "method": decision.method,
                    "confidence": decision.confidence,
                    "evidence_json": _canonical_json(decision.evidence),
                    "selected": int(decision.entity_key is not None),
                }
            )
        summary = ImportSummary(
            pages=len(pages),
            recipes=len(recipes),
            ingredients=len(ingredients),
            images=len(images),
            mapped=sum(mapping["selected"] for mapping in mappings),
            unmatched=sum(not mapping["selected"] for mapping in mappings),
        )
        connection.execute("BEGIN IMMEDIATE")
        for table in WIKI_TABLES:
            connection.execute(f"DROP TABLE IF EXISTS {table}")
        for statement in WIKI_SCHEMA:
            connection.execute(statement)
        _insert_rows(
            connection,
            "wiki_pages",
            (
                "page_id", "title", "display_title", "canonical_url",
                "revision_id", "revision_timestamp", "revision_sha1",
                "content_model", "html", "wikitext", "plain_text",
                "categories_json", "redirect_target", "fetched_at",
                "source_schema_version",
            ),
            pages,
        )
        _insert_rows(
            connection,
            "wiki_images",
            (
                "title", "mediawiki_page_id", "original_url", "local_path",
                "mime", "byte_size", "sha256", "mediawiki_sha1", "width",
                "height", "fetched_at", "published_path", "source_schema_version",
            ),
            images,
        )
        _insert_rows(
            connection,
            "wiki_entity_mappings",
            (
                "page_id", "entity_namespace", "entity_prefab_id", "method",
                "confidence", "evidence_json", "selected",
            ),
            mappings,
        )
        _insert_rows(
            connection,
            "wiki_structure_details",
            ("page_id", "details_json", "source_schema_version"),
            structure_details,
        )
        _insert_rows(
            connection,
            "wiki_recipes",
            (
                "recipe_id", "page_id", "result_title", "source_template",
                "station", "tab", "tier", "character", "dlc", "variant",
                "note", "source_schema_version",
            ),
            recipes,
        )
        _insert_rows(
            connection,
            "wiki_recipe_ingredients",
            (
                "recipe_id", "position", "ingredient_title", "amount",
                "amount_text",
            ),
            ingredients,
        )
        imported_at = manifest.get("completed_at")
        if not isinstance(imported_at, str) or not imported_at:
            raise ValueError("crawl manifest completed_at must be a string")
        connection.execute(
            "insert into wiki_import_runs values(?,?,?,?,?,?,?,?,?,?,?)",
            (
                manifest_sha,
                str(crawl_root.resolve()),
                manifest_sha,
                imported_at,
                "complete",
                summary.pages,
                summary.recipes,
                summary.ingredients,
                summary.images,
                summary.mapped,
                summary.unmatched,
            ),
        )
        failures = connection.execute("PRAGMA foreign_key_check").fetchall()
        if failures:
            raise ValueError(f"wiki database foreign key validation failed: {failures}")
        connection.commit()
        return summary
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()
