import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from tools.extract.assets import index_mod_assets
from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef
from tools.extract.exclusions import NON_ENTITY_PREFAB_IDS
from tools.extract.lua_strings import (
    parse_character_metadata_assignments,
    parse_simple_names_table,
    parse_string_assignments,
)
from tools.extract.po_strings import load_po_by_context


VERSION = re.compile(r'^\s*version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
CONTEXT_PREFIX = {
    "name": "STRINGS.NAMES.",
    "recipe_description": "STRINGS.RECIPE_DESC.",
    "description": "STRINGS.CHARACTERS.GENERIC.DESCRIBE.",
}
PLAYABLE_CHARACTER_PREFAB_IDS = {
    "xd_hantianzun",
    "xd_jingwei",
    "xd_longtaizi",
    "xd_luoshen",
    "xd_shiji",
    "xd_sudaji",
    "xd_wangmazi",
    "xd_wukong",
    "xd_yunxiao",
    "xd_zuichunyan",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    parts = path.resolve().parts
    for marker in ("mod", "data"):
        indices = [index for index, part in enumerate(parts) if part == marker]
        if indices:
            return Path(*parts[indices[-1] :]).as_posix()
    for marker in ("scripts", "images"):
        indices = [index for index, part in enumerate(parts) if part == marker]
        if indices:
            return Path(*parts[indices[-1] :]).as_posix()
    return path.name


def _source(path: Path, source_id: str, kind: str, version: str) -> SourceRef:
    return SourceRef(source_id, kind, _display_path(path), version, _sha256(path))


def _version_from_modinfo(path: Path, fallback: str = "unknown") -> str:
    if not path.is_file():
        return fallback
    match = VERSION.search(path.read_text(encoding="utf-8-sig"))
    return match.group(1) if match else fallback


def _mod_version(mod_root: Path) -> str:
    return _version_from_modinfo(mod_root / "modinfo.lua")


def _version_for_external_source(path: Path, fallback: str) -> str:
    return _version_from_modinfo(path.parent / "modinfo.lua", fallback)


def _relative_to_mod(path: Path, mod_root: Path) -> str:
    return path.relative_to(mod_root).as_posix()


def _fact_for_row(row: Dict[str, object], source: SourceRef) -> Optional[Fact]:
    prefab_id = str(row["prefab_id"])
    locator = f"line:{row['line']}"
    value = row.get("value")
    if value is not None:
        field = str(row["field"])
        if field == "name":
            return Fact(
                "name",
                EntityKey("tu_tien", prefab_id),
                {"lang": "vi", "value": value},
                source,
                1.0,
                locator,
            )
        return Fact(
            "description",
            EntityKey("tu_tien", prefab_id),
            {
                "lang": "vi",
                "value": value,
                "description_type": "recipe" if field == "recipe_description" else "generic",
            },
            source,
            1.0,
            locator,
        )
    alias = row.get("alias_prefab_id")
    if alias is not None:
        return Fact(
            "relation",
            EntityKey("tu_tien", prefab_id),
            {
                "relation": "string_alias",
                "field": row["field"],
                "target_prefab_id": alias,
                "dependency_candidate": True,
                "resolution": "unresolved",
            },
            source,
            0.5,
            locator,
        )
    return None


def _entity_fact(
    prefab_id: str,
    source: SourceRef,
    locator: str,
    discovered_by: str,
    entity_type: str = "unknown",
    confidence: float = 0.9,
) -> Fact:
    return Fact(
        "entity",
        EntityKey("tu_tien", prefab_id),
        {"entity_type": entity_type, "discovered_by": discovered_by},
        source,
        confidence,
        locator,
    )


def extract_mod_static(
    mod_root: Path, tu_tien_translation: Path, base_translation_po: Path
) -> FactBundle:
    """Return sorted static facts; never execute Lua and never modify ``mod_root``."""

    mod_root = Path(mod_root)
    tu_tien_translation = Path(tu_tien_translation)
    base_translation_po = Path(base_translation_po)
    version = _mod_version(mod_root)
    sources: Dict[str, SourceRef] = {}
    facts: List[Fact] = []
    errors: List[Dict[str, object]] = []

    po_values: Dict[str, str] = {}
    po_source: Optional[SourceRef] = None
    if base_translation_po.is_file():
        po_source = _source(
            base_translation_po,
            "base-translation-po",
            "mod_translation",
            _version_for_external_source(base_translation_po, version),
        )
        sources[po_source.source_id] = po_source
        try:
            po_values = load_po_by_context(base_translation_po)
        except ValueError as exc:
            errors.append({"code": "invalid_po", "path": _display_path(base_translation_po), "detail": str(exc)})
    else:
        errors.append({"code": "missing_source", "path": _display_path(base_translation_po), "role": "base_translation_po"})

    string_inputs: List[Tuple[Path, str, str, bool]] = [
        (mod_root / "scripts/main/strings.lua", "mod-strings", "mod_static", False),
        (tu_tien_translation, "tu-tien-translation", "mod_translation", True),
    ]
    for path, source_id, kind, include_names_table in string_inputs:
        if not path.is_file():
            errors.append({"code": "missing_source", "path": _display_path(path), "role": source_id})
            continue
        source_version = (
            _version_for_external_source(path, version)
            if kind == "mod_translation"
            else version
        )
        source = _source(path, source_id, kind, source_version)
        sources[source.source_id] = source
        rows = parse_string_assignments(path)
        if include_names_table:
            rows.extend(parse_simple_names_table(path))
        for metadata in parse_character_metadata_assignments(path):
            prefab_id = str(metadata["prefab_id"])
            locator = f"line:{metadata['line']}"
            value = metadata.get("value")
            if value is None:
                errors.append(
                    {
                        "code": "unparsed_character_metadata_expression",
                        "path": source.path,
                        "line": metadata["line"],
                        "field": metadata["field"],
                        "expression": metadata.get("unparsed_expression"),
                    }
                )
                continue
            facts.append(
                _entity_fact(
                    prefab_id,
                    source,
                    locator,
                    "character_metadata",
                    "character",
                    1.0,
                )
            )
            if metadata["field"] == "character_description":
                facts.append(
                    Fact(
                        "description",
                        EntityKey("tu_tien", prefab_id),
                        {
                            "lang": "vi",
                            "value": value,
                            "description_type": "character_profile",
                        },
                        source,
                        1.0,
                        locator,
                    )
                )
            else:
                facts.append(
                    Fact(
                        "effect",
                        EntityKey("tu_tien", prefab_id),
                        {
                            "trigger": "character_profile",
                            "effect_key": metadata["field"],
                            "value": value,
                        },
                        source,
                        1.0,
                        locator,
                    )
                )
        for row in rows:
            prefab_id = str(row["prefab_id"])
            if prefab_id in NON_ENTITY_PREFAB_IDS:
                continue
            locator = f"line:{row['line']}"
            facts.append(_entity_fact(prefab_id, source, locator, "strings", confidence=0.9))
            fact = _fact_for_row(row, source)
            if fact is not None:
                facts.append(fact)
            elif "unparsed_expression" in row:
                errors.append(
                    {
                        "code": "unparsed_string_expression",
                        "path": source.path,
                        "line": row["line"],
                        "expression": row["unparsed_expression"],
                    }
                )
            alias = row.get("alias_prefab_id")
            if alias and po_source is not None:
                context = CONTEXT_PREFIX[str(row["field"])] + str(alias).upper()
                translated = po_values.get(context)
                if translated:
                    alias_row = dict(row)
                    alias_row.pop("alias_prefab_id", None)
                    alias_row["value"] = translated
                    translated_fact = _fact_for_row(alias_row, po_source)
                    if translated_fact is not None:
                        facts.append(
                            Fact(
                                translated_fact.kind,
                                translated_fact.subject,
                                translated_fact.payload,
                                translated_fact.source,
                                translated_fact.confidence,
                                f"context:{context}",
                            )
                        )

    prefab_root = mod_root / "scripts/prefabs"
    if prefab_root.is_dir():
        for path in sorted(prefab_root.glob("*.lua")):
            relative = _relative_to_mod(path, mod_root)
            source = _source(path, f"mod-prefab:{relative}", "mod_static", version)
            sources[source.source_id] = source
            prefab_id = path.stem.lower()
            facts.append(
                _entity_fact(
                    prefab_id,
                    source,
                    "filename",
                    "prefab_filename",
                    "character" if prefab_id in PLAYABLE_CHARACTER_PREFAB_IDS else "prefab",
                    1.0 if prefab_id in PLAYABLE_CHARACTER_PREFAB_IDS else 0.9,
                )
            )
    else:
        errors.append({"code": "missing_source", "path": _display_path(prefab_root), "role": "prefab_directory"})

    inventory_root = mod_root / "images/inventoryimages"
    if not inventory_root.is_dir():
        errors.append({"code": "missing_source", "path": _display_path(inventory_root), "role": "inventory_directory"})
    asset_bundle = index_mod_assets(mod_root, version)
    sources.update((source.source_id, source) for source in asset_bundle.sources)
    facts.extend(asset_bundle.facts)
    errors.extend(asset_bundle.errors)
    for asset_fact in asset_bundle.facts:
        if asset_fact.payload.get("asset_type") == "inventory":
            facts.append(
                _entity_fact(
                    asset_fact.subject.prefab_id,
                    asset_fact.source,
                    asset_fact.locator,
                    "inventory_atlas",
                    "item",
                    0.9,
                )
            )

    facts.sort(
        key=lambda fact: (
            fact.subject.namespace,
            fact.subject.prefab_id,
            fact.kind,
            fact.source.source_id,
            fact.locator,
        )
    )
    return FactBundle(1, sorted(sources.values()), facts, errors)
