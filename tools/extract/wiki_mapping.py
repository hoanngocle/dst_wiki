"""Deterministic, conservative mapping from wiki pages to game entities."""

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple


@dataclass(frozen=True)
class MappingDecision:
    entity_key: Optional[str]
    method: str
    confidence: float
    evidence: Dict[str, Any]


@dataclass(frozen=True)
class EntityIndex:
    by_prefab: Dict[str, Tuple[str, ...]]
    by_name: Dict[str, Tuple[str, ...]]
    names_by_key: Dict[str, str]


def normalize_identity(value: str) -> str:
    """Normalize a human-facing title for exact identity comparison."""

    folded = unicodedata.normalize("NFKD", value)
    ascii_value = folded.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.casefold()).strip()


def canonical_title(title: str) -> str:
    return re.sub(r"/DST$", "", title, flags=re.IGNORECASE).strip()


def extract_spawn_codes(wikitext: str) -> Tuple[str, ...]:
    values = re.findall(
        r"\|\s*spawnCode\s*=\s*['\"]?([^\n|'\"}]+)",
        wikitext,
        re.IGNORECASE,
    )
    return tuple(
        dict.fromkeys(
            value.strip().casefold()
            for value in values
            if value.strip()
        )
    )


def build_entity_index(rows: Iterable[Mapping[str, Any]]) -> EntityIndex:
    by_prefab: Dict[str, list] = {}
    by_name: Dict[str, list] = {}
    names_by_key: Dict[str, str] = {}
    for row in rows:
        if row.get("namespace") != "base_game":
            continue
        prefab_id = row.get("prefab_id")
        if not isinstance(prefab_id, str) or not prefab_id.strip():
            continue
        prefab_id = prefab_id.strip().casefold()
        key = f"base_game:{prefab_id}"
        by_prefab.setdefault(prefab_id, []).append(key)
        name = row.get("name_en")
        if isinstance(name, str) and normalize_identity(name):
            normalized_name = normalize_identity(name)
            by_name.setdefault(normalized_name, []).append(key)
            names_by_key[key] = normalized_name
    return EntityIndex(
        by_prefab={
            value: tuple(sorted(set(keys)))
            for value, keys in sorted(by_prefab.items())
        },
        by_name={
            value: tuple(sorted(set(keys)))
            for value, keys in sorted(by_name.items())
        },
        names_by_key=dict(sorted(names_by_key.items())),
    )


def _selected(
    key: str,
    method: str,
    confidence: float,
    evidence: Dict[str, Any],
) -> MappingDecision:
    return MappingDecision(key, method, confidence, evidence)


def map_page(page: Mapping[str, Any], index: EntityIndex) -> MappingDecision:
    title = page.get("title")
    if not isinstance(title, str) or not title.strip():
        return MappingDecision(None, "unmatched", 0.0, {"reason": "missing_title"})

    raw_wikitext = page.get("wikitext")
    wikitext = raw_wikitext if isinstance(raw_wikitext, str) else ""
    spawn_codes = extract_spawn_codes(wikitext)
    spawn_candidates = tuple(
        sorted(
            {
                candidate
                for code in spawn_codes
                for candidate in index.by_prefab.get(code, ())
            }
        )
    )
    if len(spawn_candidates) == 1:
        return _selected(
            spawn_candidates[0],
            "spawn_code",
            1.0,
            {"spawn_codes": list(spawn_codes)},
        )
    if len(spawn_candidates) > 1:
        normalized_title = normalize_identity(canonical_title(title))
        named_candidates = tuple(
            key
            for key in spawn_candidates
            if index.names_by_key.get(key) == normalized_title
        )
        if len(named_candidates) == 1:
            return _selected(
                named_candidates[0],
                "spawn_code_title",
                0.99,
                {
                    "spawn_codes": list(spawn_codes),
                    "candidates": list(spawn_candidates),
                    "normalized_title": normalized_title,
                },
            )
        return MappingDecision(
            None,
            "ambiguous_spawn_code",
            0.0,
            {
                "spawn_codes": list(spawn_codes),
                "candidates": list(spawn_candidates),
            },
        )

    has_dst_suffix = bool(re.search(r"/DST$", title, flags=re.IGNORECASE))
    normalized_title = normalize_identity(canonical_title(title))
    name_candidates = index.by_name.get(normalized_title, ())
    if len(name_candidates) == 1:
        return _selected(
            name_candidates[0],
            "canonical_alias" if has_dst_suffix else "english_name",
            0.94 if has_dst_suffix else 0.97,
            {
                "normalized_title": normalized_title,
                "source_title": title,
            },
        )
    if len(name_candidates) > 1:
        return MappingDecision(
            None,
            "ambiguous_name",
            0.0,
            {
                "normalized_title": normalized_title,
                "candidates": list(name_candidates),
            },
        )
    return MappingDecision(
        None,
        "unmatched",
        0.0,
        {
            "normalized_title": normalized_title,
            "spawn_codes": list(spawn_codes),
        },
    )
