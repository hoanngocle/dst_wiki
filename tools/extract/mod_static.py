import hashlib
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef
from tools.extract.lua_strings import parse_simple_names_table, parse_string_assignments
from tools.extract.po_strings import load_po_by_context


VERSION = re.compile(r'^\s*version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
CONTEXT_PREFIX = {
    "name": "STRINGS.NAMES.",
    "recipe_description": "STRINGS.RECIPE_DESC.",
    "description": "STRINGS.CHARACTERS.GENERIC.DESCRIBE.",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


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
                "target_namespace": "base_game",
                "target_prefab_id": alias,
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


def _xml_asset_facts(
    xml_path: Path,
    mod_root: Path,
    version: str,
    asset_type: str,
) -> Tuple[List[SourceRef], List[Fact], List[Dict[str, object]]]:
    relative = _relative_to_mod(xml_path, mod_root)
    source = _source(xml_path, f"mod-asset:{relative}", "handbook_image" if asset_type == "handbook" else "mod_static", version)
    facts: List[Fact] = []
    errors: List[Dict[str, object]] = []
    try:
        root = ET.fromstring(xml_path.read_text(encoding="utf-8-sig"))
    except (OSError, ET.ParseError) as exc:
        errors.append({"code": "invalid_atlas_xml", "path": _display_path(xml_path), "detail": str(exc)})
        return [source], facts, errors

    texture_node = root.find("Texture")
    texture_name = texture_node.attrib.get("filename", "") if texture_node is not None else ""
    texture_path = xml_path.parent / texture_name if texture_name else xml_path.with_suffix(".tex")
    texture_available = texture_path.is_file()
    if not texture_available:
        errors.append(
            {
                "code": "missing_asset_pair",
                "path": _display_path(xml_path),
                "missing": _display_path(texture_path),
            }
        )

    element_nodes = list(root.findall("./Elements/Element"))
    if not element_nodes:
        element_nodes = [None]
    for index, element in enumerate(element_nodes):
        element_name = element.attrib.get("name", "") if element is not None else ""
        fallback = xml_path.stem + ".tex"
        prefab_id = Path(element_name or fallback).stem.lower()
        payload: Dict[str, object] = {
            "asset_type": asset_type,
            "atlas": relative,
            "texture": _relative_to_mod(texture_path, mod_root),
            "element": element_name or fallback,
            "available": texture_available,
        }
        if texture_available:
            payload["texture_sha256"] = _sha256(texture_path)
        if element is not None:
            uv = {key: element.attrib[key] for key in ("u1", "u2", "v1", "v2") if key in element.attrib}
            if uv:
                payload["uv"] = uv
        locator = f"element:{index + 1}"
        facts.append(Fact("asset", EntityKey("tu_tien", prefab_id), payload, source, 1.0 if texture_available else 0.7, locator))
        if asset_type == "inventory":
            facts.append(_entity_fact(prefab_id, source, locator, "inventory_atlas", "item", 0.9))
    return [source], facts, errors


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
        for row in rows:
            prefab_id = str(row["prefab_id"])
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
            facts.append(_entity_fact(path.stem.lower(), source, "filename", "prefab_filename", "prefab", 0.9))
    else:
        errors.append({"code": "missing_source", "path": _display_path(prefab_root), "role": "prefab_directory"})

    inventory_root = mod_root / "images/inventoryimages"
    if inventory_root.is_dir():
        for path in sorted(inventory_root.glob("*.xml")):
            new_sources, new_facts, new_errors = _xml_asset_facts(path, mod_root, version, "inventory")
            sources.update((source.source_id, source) for source in new_sources)
            facts.extend(new_facts)
            errors.extend(new_errors)
    else:
        errors.append({"code": "missing_source", "path": _display_path(inventory_root), "role": "inventory_directory"})

    for path in sorted((mod_root / "images").glob("xd_info_*.xml")):
        new_sources, new_facts, new_errors = _xml_asset_facts(path, mod_root, version, "handbook")
        sources.update((source.source_id, source) for source in new_sources)
        facts.extend(new_facts)
        errors.extend(new_errors)

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
