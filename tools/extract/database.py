import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, Iterable, Sequence

from tools.extract.normalize import NormalizedCatalog


SCHEMA = (
    """CREATE TABLE sources (
      source_id TEXT PRIMARY KEY,
      kind TEXT NOT NULL,
      path TEXT NOT NULL,
      version TEXT NOT NULL,
      sha256 TEXT NOT NULL
    )""",
    """CREATE TABLE entities (
      namespace TEXT NOT NULL,
      prefab_id TEXT NOT NULL,
      entity_type TEXT NOT NULL,
      is_inventory_item INTEGER NOT NULL,
      name_vi TEXT,
      name_en TEXT,
      description_vi TEXT,
      description_en TEXT,
      icon_key TEXT,
      confidence REAL NOT NULL,
      PRIMARY KEY(namespace, prefab_id)
    )""",
    """CREATE TABLE recipes (
      recipe_id TEXT PRIMARY KEY,
      product_namespace TEXT NOT NULL,
      product_id TEXT NOT NULL,
      output_count INTEGER NOT NULL,
      tech TEXT,
      restrictions_json TEXT NOT NULL,
      FOREIGN KEY(product_namespace, product_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE recipe_ingredients (
      recipe_id TEXT NOT NULL,
      position INTEGER NOT NULL,
      ingredient_namespace TEXT NOT NULL,
      ingredient_id TEXT NOT NULL,
      amount REAL NOT NULL,
      PRIMARY KEY(recipe_id, position),
      FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),
      FOREIGN KEY(ingredient_namespace, ingredient_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE acquisition_sources (
      acquisition_id TEXT PRIMARY KEY,
      target_namespace TEXT NOT NULL,
      target_id TEXT NOT NULL,
      source_type TEXT NOT NULL,
      source_namespace TEXT,
      source_id TEXT,
      chance REAL,
      min_count REAL,
      max_count REAL,
      conditions_json TEXT NOT NULL,
      FOREIGN KEY(target_namespace, target_id) REFERENCES entities(namespace, prefab_id),
      FOREIGN KEY(source_namespace, source_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE stats (
      namespace TEXT NOT NULL,
      prefab_id TEXT NOT NULL,
      stat_key TEXT NOT NULL,
      value_num REAL,
      value_text TEXT,
      unit TEXT,
      confidence REAL NOT NULL,
      PRIMARY KEY(namespace, prefab_id, stat_key),
      FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE effects (
      effect_id TEXT PRIMARY KEY,
      namespace TEXT NOT NULL,
      prefab_id TEXT NOT NULL,
      trigger_name TEXT,
      effect_key TEXT NOT NULL,
      value_json TEXT NOT NULL,
      duration REAL,
      FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE entity_relations (
      relation_id TEXT PRIMARY KEY,
      from_namespace TEXT NOT NULL,
      from_id TEXT NOT NULL,
      relation_type TEXT NOT NULL,
      to_namespace TEXT NOT NULL,
      to_id TEXT NOT NULL,
      metadata_json TEXT NOT NULL,
      FOREIGN KEY(from_namespace, from_id) REFERENCES entities(namespace, prefab_id),
      FOREIGN KEY(to_namespace, to_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE assets (
      asset_id TEXT PRIMARY KEY,
      namespace TEXT NOT NULL,
      prefab_id TEXT,
      asset_type TEXT NOT NULL,
      atlas TEXT,
      texture TEXT NOT NULL,
      element TEXT,
      uv_json TEXT,
      FOREIGN KEY(namespace, prefab_id) REFERENCES entities(namespace, prefab_id)
    )""",
    """CREATE TABLE evidence (
      evidence_id TEXT PRIMARY KEY,
      record_type TEXT NOT NULL,
      record_id TEXT NOT NULL,
      source_id TEXT NOT NULL,
      locator TEXT NOT NULL,
      raw_value_json TEXT NOT NULL,
      confidence REAL NOT NULL,
      selected INTEGER NOT NULL,
      FOREIGN KEY(source_id) REFERENCES sources(source_id)
    )""",
    """CREATE TABLE conflicts (
      conflict_id TEXT PRIMARY KEY,
      subject_key TEXT NOT NULL,
      field_key TEXT NOT NULL,
      candidates_json TEXT NOT NULL,
      selected_json TEXT NOT NULL
    )""",
    """CREATE TABLE extraction_errors (
      error_id TEXT PRIMARY KEY,
      source_kind TEXT NOT NULL,
      code TEXT NOT NULL,
      payload_json TEXT NOT NULL
    )""",
)


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys=ON")
    for statement in SCHEMA:
        connection.execute(statement)


def _insert_rows(
    connection: sqlite3.Connection,
    table: str,
    columns: Sequence[str],
    rows: Iterable[Dict[str, Any]],
) -> None:
    names = ",".join(columns)
    placeholders = ",".join("?" for _ in columns)
    connection.executemany(
        f"INSERT INTO {table} ({names}) VALUES ({placeholders})",
        ([row[column] for column in columns] for row in rows),
    )


def write_database(path: Path, catalog: NormalizedCatalog) -> None:
    """Write a catalog in one transaction, then atomically replace the output."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    try:
        connection.execute("PRAGMA page_size=4096")
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("BEGIN IMMEDIATE")
        create_schema(connection)
        table_columns = (
            ("sources", ("source_id", "kind", "path", "version", "sha256"), ("source_id",)),
            ("entities", ("namespace", "prefab_id", "entity_type", "is_inventory_item", "name_vi", "name_en", "description_vi", "description_en", "icon_key", "confidence"), ("namespace", "prefab_id")),
            ("recipes", ("recipe_id", "product_namespace", "product_id", "output_count", "tech", "restrictions_json"), ("recipe_id",)),
            ("recipe_ingredients", ("recipe_id", "position", "ingredient_namespace", "ingredient_id", "amount"), ("recipe_id", "position")),
            ("acquisition_sources", ("acquisition_id", "target_namespace", "target_id", "source_type", "source_namespace", "source_id", "chance", "min_count", "max_count", "conditions_json"), ("acquisition_id",)),
            ("stats", ("namespace", "prefab_id", "stat_key", "value_num", "value_text", "unit", "confidence"), ("namespace", "prefab_id", "stat_key")),
            ("effects", ("effect_id", "namespace", "prefab_id", "trigger_name", "effect_key", "value_json", "duration"), ("effect_id",)),
            ("entity_relations", ("relation_id", "from_namespace", "from_id", "relation_type", "to_namespace", "to_id", "metadata_json"), ("relation_id",)),
            ("assets", ("asset_id", "namespace", "prefab_id", "asset_type", "atlas", "texture", "element", "uv_json"), ("asset_id",)),
            ("evidence", ("evidence_id", "record_type", "record_id", "source_id", "locator", "raw_value_json", "confidence", "selected"), ("evidence_id",)),
            ("conflicts", ("conflict_id", "subject_key", "field_key", "candidates_json", "selected_json"), ("conflict_id",)),
            ("extraction_errors", ("error_id", "source_kind", "code", "payload_json"), ("error_id",)),
        )
        for table, columns, primary_key in table_columns:
            rows = sorted(
                getattr(catalog, table),
                key=lambda row: tuple(row[column] for column in primary_key),
            )
            _insert_rows(connection, table, columns, rows)
        failures = connection.execute("PRAGMA foreign_key_check").fetchall()
        if failures:
            raise ValueError(f"database foreign key validation failed: {failures}")
        connection.commit()
    except BaseException:
        connection.rollback()
        connection.close()
        if temporary.exists():
            temporary.unlink()
        raise
    else:
        connection.close()
    os.replace(temporary, path)
