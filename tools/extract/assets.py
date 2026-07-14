from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef


UvCoordinates = Tuple[float, float, float, float]
BASE_INVENTORY_ATLASES = tuple(
    f"images/inventoryimages{suffix}.xml"
    for suffix in ("", "1", "2", "3", "4")
)


@dataclass(frozen=True)
class Atlas:
    texture: str
    elements: Dict[str, UvCoordinates]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    parts = Path(path).resolve().parts
    for marker in ("mod", "data"):
        indices = [index for index, part in enumerate(parts) if part == marker]
        if indices:
            return Path(*parts[indices[-1] :]).as_posix()
    return Path(path).name


def parse_atlas_bytes(data: bytes) -> Atlas:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"invalid atlas XML: {exc}") from exc
    texture_node = root.find("Texture")
    if texture_node is None or not texture_node.attrib.get("filename"):
        raise ValueError("atlas is missing Texture filename")
    elements_node = root.find("Elements")
    if elements_node is None:
        raise ValueError("atlas is missing Elements")
    elements: Dict[str, UvCoordinates] = {}
    for node in elements_node.findall("Element"):
        name = node.attrib.get("name")
        if not name:
            raise ValueError("atlas Element is missing name")
        try:
            elements[name] = tuple(
                float(node.attrib[key]) for key in ("u1", "u2", "v1", "v2")
            )
        except (KeyError, ValueError) as exc:
            raise ValueError(f"atlas Element {name!r} has invalid UV coordinates") from exc
    return Atlas(texture_node.attrib["filename"], elements)


def parse_atlas(path: Path) -> Atlas:
    return parse_atlas_bytes(Path(path).read_bytes())


def _uv_payload(uv: UvCoordinates) -> Dict[str, float]:
    return dict(zip(("u1", "u2", "v1", "v2"), uv))


def _fact_sort_key(fact: Fact) -> Tuple[str, str, str, str, str]:
    return (
        fact.subject.namespace,
        fact.subject.prefab_id,
        fact.kind,
        fact.source.source_id,
        fact.locator,
    )


def index_mod_assets(mod_root: Path, version: str) -> FactBundle:
    """Index direct Tu Tien inventory and handbook atlas pairs."""

    mod_root = Path(mod_root)
    inventory_root = mod_root / "images/inventoryimages"
    inputs = [
        (path, "inventory")
        for path in sorted(inventory_root.glob("*.xml"))
    ]
    inputs.extend(
        (path, "handbook_image")
        for path in sorted((mod_root / "images").glob("xd_info_*.xml"))
    )
    sources: List[SourceRef] = []
    facts: List[Fact] = []
    errors: List[Dict[str, object]] = []

    for xml_path, asset_type in inputs:
        relative = xml_path.relative_to(mod_root).as_posix()
        source = SourceRef(
            f"mod-asset:{relative}",
            "handbook_image" if asset_type == "handbook_image" else "mod_static",
            _display_path(xml_path),
            version,
            _sha256(xml_path),
        )
        sources.append(source)
        try:
            atlas = parse_atlas(xml_path)
        except (OSError, ValueError) as exc:
            errors.append(
                {
                    "code": "invalid_atlas_xml",
                    "path": source.path,
                    "detail": str(exc),
                }
            )
            continue

        texture_path = xml_path.parent / atlas.texture
        texture_relative = texture_path.relative_to(mod_root).as_posix()
        available = texture_path.is_file()
        if not available:
            errors.append(
                {
                    "code": "missing_asset_texture",
                    "path": source.path,
                    "missing": _display_path(texture_path),
                }
            )
        if not atlas.elements:
            errors.append({"code": "empty_atlas", "path": source.path})
        for position, (element, uv) in enumerate(sorted(atlas.elements.items()), 1):
            payload: Dict[str, object] = {
                "asset_type": asset_type,
                "atlas": relative,
                "texture": texture_relative,
                "element": element,
                "uv": _uv_payload(uv),
                "available": available,
            }
            if available:
                payload["texture_sha256"] = _sha256(texture_path)
            facts.append(
                Fact(
                    "asset",
                    EntityKey("tu_tien", PurePosixPath(element).stem.lower()),
                    payload,
                    source,
                    1.0 if available else 0.7,
                    f"element:{position}:{element}",
                )
            )

    facts.sort(key=_fact_sort_key)
    errors.sort(key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True))
    return FactBundle(1, sorted(sources), facts, errors)


def add_base_game_asset_facts(
    bundle: FactBundle, images_archive: Path, manifest_path: Path
) -> FactBundle:
    """Attach icons from the five canonical DST atlases to selected base entities."""

    # Import locally so atlas parsing remains independent from the Lua source parser.
    from tools.extract.base_game import verify_snapshot_archive

    images_archive = Path(images_archive)
    verify_snapshot_archive(images_archive, manifest_path)
    source = SourceRef(
        "base-game-images",
        "base_game_source",
        _display_path(images_archive),
        "snapshot",
        _sha256(images_archive),
    )
    selected = {
        fact.subject.prefab_id
        for fact in bundle.facts
        if fact.kind == "entity" and fact.subject.namespace == "base_game"
    }
    new_facts: List[Fact] = []
    new_errors: List[Dict[str, object]] = []

    with ZipFile(images_archive) as archive:
        members = set(archive.namelist())
        for atlas_member in BASE_INVENTORY_ATLASES:
            if atlas_member not in members:
                new_errors.append(
                    {"code": "missing_base_inventory_atlas", "path": atlas_member}
                )
                continue
            try:
                atlas = parse_atlas_bytes(archive.read(atlas_member))
            except ValueError as exc:
                new_errors.append(
                    {
                        "code": "invalid_atlas_xml",
                        "path": atlas_member,
                        "detail": str(exc),
                    }
                )
                continue
            texture_member = str(PurePosixPath(atlas_member).parent / atlas.texture)
            available = texture_member in members
            if not available:
                new_errors.append(
                    {
                        "code": "missing_asset_texture",
                        "path": atlas_member,
                        "missing": texture_member,
                    }
                )
            texture_hash = (
                hashlib.sha256(archive.read(texture_member)).hexdigest()
                if available
                else None
            )
            for position, (element, uv) in enumerate(
                sorted(atlas.elements.items()), 1
            ):
                prefab_id = PurePosixPath(element).stem.lower()
                if prefab_id not in selected:
                    continue
                payload: Dict[str, object] = {
                    "asset_type": "inventory",
                    "atlas": atlas_member,
                    "texture": texture_member,
                    "element": element,
                    "uv": _uv_payload(uv),
                    "available": available,
                }
                if texture_hash is not None:
                    payload["texture_sha256"] = texture_hash
                new_facts.append(
                    Fact(
                        "asset",
                        EntityKey("base_game", prefab_id),
                        payload,
                        source,
                        1.0 if available else 0.7,
                        f"{atlas_member}:element:{position}:{element}",
                    )
                )

    sources = {
        item.source_id: item
        for item in bundle.sources
        if item.source_id != source.source_id
    }
    sources[source.source_id] = source
    facts = [
        fact
        for fact in bundle.facts
        if not (fact.kind == "asset" and fact.source.source_id == source.source_id)
    ]
    facts.extend(new_facts)
    facts.sort(key=_fact_sort_key)
    errors = list(bundle.errors)
    errors.extend(new_errors)
    errors.sort(key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True))
    return FactBundle(bundle.schema_version, sorted(sources.values()), facts, errors)
