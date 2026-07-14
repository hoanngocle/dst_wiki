from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple
from zipfile import ZipFile

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef
from tools.extract.lua_strings import decode_lua_string_literal
from tools.extract.po_strings import load_po_by_context


@dataclass(frozen=True, order=True)
class DependencyRequest:
    prefab_id: str
    relation: str
    requested_by: str


@dataclass(frozen=True)
class LuaCall:
    name: str
    arguments: Tuple[str, ...]
    expression: str
    line: int
    offset: int


@dataclass(frozen=True)
class RecipeRecord:
    product: str
    ingredients: Tuple[Tuple[str, str], ...]
    tech_expression: str
    config_expression: str
    expression: str
    line: int


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    parts = Path(path).resolve().parts
    if "data" in parts:
        index = len(parts) - 1 - list(reversed(parts)).index("data")
        return Path(*parts[index:]).as_posix()
    if "mod" in parts:
        index = len(parts) - 1 - list(reversed(parts)).index("mod")
        return Path(*parts[index:]).as_posix()
    return Path(path).name


def verify_snapshot_archive(archive: Path, manifest_path: Path) -> Dict[str, Any]:
    """Verify a copied archive against the colocated snapshot manifest."""

    archive = Path(archive).resolve()
    manifest_path = Path(manifest_path).resolve()
    if archive.parent != manifest_path.parent:
        raise ValueError("archive and manifest must be in the same snapshot directory")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = manifest.get("files", {}).get(archive.name)
    if not isinstance(record, dict):
        raise ValueError(f"manifest has no record for {archive.name}")
    actual_size = archive.stat().st_size
    actual_hash = _sha256(archive)
    if record.get("size") != actual_size or record.get("sha256") != actual_hash:
        raise ValueError(f"snapshot checksum mismatch for {archive.name}")
    return record


def _long_bracket_end(source: str, start: int) -> Optional[int]:
    match = re.match(r"\[(=*)\[", source[start:])
    if match is None:
        return None
    closing = "]" + match.group(1) + "]"
    end = source.find(closing, start + len(match.group(0)))
    return len(source) if end < 0 else end + len(closing)


def _skip_string_or_comment(source: str, index: int) -> Optional[int]:
    if source.startswith("--", index):
        long_start = index + 2
        long_end = _long_bracket_end(source, long_start)
        if long_end is not None:
            return long_end
        end = source.find("\n", index + 2)
        return len(source) if end < 0 else end + 1
    if source[index] in ('"', "'"):
        quote = source[index]
        index += 1
        while index < len(source):
            if source[index] == "\\":
                index += 2
            elif source[index] == quote:
                return index + 1
            else:
                index += 1
        return len(source)
    return _long_bracket_end(source, index)


def _matching_delimiter(source: str, opening: int) -> int:
    pairs = {"(": ")", "{": "}", "[": "]"}
    stack = [pairs[source[opening]]]
    index = opening + 1
    while index < len(source):
        skipped = _skip_string_or_comment(source, index)
        if skipped is not None:
            index = skipped
            continue
        char = source[index]
        if char in pairs:
            stack.append(pairs[char])
        elif char in ")}]":
            if not stack or char != stack[-1]:
                raise ValueError(f"unbalanced Lua delimiter at offset {index}")
            stack.pop()
            if not stack:
                return index
        index += 1
    raise ValueError(f"unterminated Lua delimiter at offset {opening}")


def _split_top_level(source: str) -> List[str]:
    values: List[str] = []
    start = 0
    index = 0
    pairs = {"(": ")", "{": "}", "[": "]"}
    stack: List[str] = []
    while index < len(source):
        skipped = _skip_string_or_comment(source, index)
        if skipped is not None:
            index = skipped
            continue
        char = source[index]
        if char in pairs:
            stack.append(pairs[char])
        elif char in ")}]":
            if stack and char == stack[-1]:
                stack.pop()
        elif char == "," and not stack:
            values.append(source[start:index].strip())
            start = index + 1
        index += 1
    tail = source[start:].strip()
    if tail:
        values.append(tail)
    return values


def _iter_calls(source: str, names: Sequence[str]) -> Iterator[LuaCall]:
    wanted = set(names)
    index = 0
    while index < len(source):
        skipped = _skip_string_or_comment(source, index)
        if skipped is not None:
            index = skipped
            continue
        if source[index].isalpha() or source[index] == "_":
            end = index + 1
            while end < len(source) and (
                source[end].isalnum() or source[end] == "_"
            ):
                end += 1
            name = source[index:end]
            cursor = end
            while cursor < len(source) and source[cursor].isspace():
                cursor += 1
            if name in wanted and cursor < len(source) and source[cursor] == "(":
                try:
                    closing = _matching_delimiter(source, cursor)
                except ValueError:
                    index = end
                    continue
                expression = source[index : closing + 1]
                yield LuaCall(
                    name,
                    tuple(_split_top_level(source[cursor + 1 : closing])),
                    expression.strip(),
                    source.count("\n", 0, index) + 1,
                    index,
                )
                index = closing + 1
                continue
            index = end
            continue
        index += 1


def _literal_string(expression: str) -> Optional[str]:
    expression = expression.strip()
    if len(expression) < 2 or expression[0] not in ('"', "'"):
        return None
    try:
        return decode_lua_string_literal(expression)
    except ValueError:
        return None


def _literal_number(expression: str) -> Optional[Any]:
    expression = expression.strip()
    if not re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", expression):
        return None
    value = float(expression)
    return int(value) if value.is_integer() and not any(c in expression for c in ".eE") else value


def _table_string_entries(source: str, table_name: str) -> Dict[str, Tuple[str, int]]:
    index = 0
    while index < len(source):
        skipped = _skip_string_or_comment(source, index)
        if skipped is not None:
            index = skipped
            continue
        if source[index].isalpha() or source[index] == "_":
            end = index + 1
            while end < len(source) and (
                source[end].isalnum() or source[end] == "_"
            ):
                end += 1
            if source[index:end] != table_name:
                index = end
                continue
            cursor = end
            while cursor < len(source) and source[cursor].isspace():
                cursor += 1
            if cursor >= len(source) or source[cursor] != "=":
                index = end
                continue
            cursor += 1
            while cursor < len(source) and source[cursor].isspace():
                cursor += 1
            if cursor >= len(source) or source[cursor] != "{":
                index = end
                continue
            opening = cursor
        else:
            index += 1
            continue
        try:
            closing = _matching_delimiter(source, opening)
        except ValueError:
            return {}
        body = source[opening + 1 : closing]
        result: Dict[str, Tuple[str, int]] = {}
        cursor = 0
        for entry in _split_top_level(body):
            entry_match = re.match(
                r'^\s*(?:\[\s*["\']([A-Za-z0-9_]+)["\']\s*\]|([A-Za-z0-9_]+))\s*=\s*(.+?)\s*$',
                entry,
                re.DOTALL,
            )
            if entry_match:
                key = (entry_match.group(1) or entry_match.group(2)).lower()
                value = _literal_string(entry_match.group(3))
                if value is not None:
                    local = body.find(entry, cursor)
                    cursor = max(cursor, local + len(entry))
                    line = source.count("\n", 0, opening + 1 + max(local, 0)) + 1
                    result[key] = (value, line)
        return result
    return {}


def _has_receiver(source: str, call: LuaCall, receiver: str) -> bool:
    line_start = source.rfind("\n", 0, call.offset) + 1
    return source[line_start : call.offset].rstrip().endswith(receiver)


def _assigned_strings(source: str, prefix: str) -> Dict[str, Tuple[str, int]]:
    pattern = re.compile(
        rf'^\s*{re.escape(prefix)}\.([A-Z0-9_]+)\s*=\s*((?:"(?:\\.|[^"])*")|(?:\'(?:\\.|[^\'])*\'))\s*$',
        re.MULTILINE,
    )
    result: Dict[str, Tuple[str, int]] = {}
    for match in pattern.finditer(source):
        value = _literal_string(match.group(2))
        if value is not None:
            result[match.group(1).lower()] = (
                value,
                source.count("\n", 0, match.start()) + 1,
            )
    return result


def _table_fields(expression: str) -> Dict[str, str]:
    expression = expression.strip()
    if not (expression.startswith("{") and expression.endswith("}")):
        return {}
    result: Dict[str, str] = {}
    for entry in _split_top_level(expression[1:-1]):
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$", entry, re.DOTALL)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def _recipe_record(call: LuaCall) -> Optional[RecipeRecord]:
    if len(call.arguments) < 3:
        return None
    product = _literal_string(call.arguments[0])
    ingredient_table = call.arguments[1].strip()
    if product is None or not (
        ingredient_table.startswith("{") and ingredient_table.endswith("}")
    ):
        return None
    ingredients: List[Tuple[str, str]] = []
    for ingredient_call in _iter_calls(ingredient_table[1:-1], ("Ingredient",)):
        if len(ingredient_call.arguments) < 2:
            continue
        prefab_id = _literal_string(ingredient_call.arguments[0])
        if prefab_id is not None:
            ingredients.append((prefab_id.lower(), ingredient_call.arguments[1].strip()))
    return RecipeRecord(
        product.lower(),
        tuple(ingredients),
        call.arguments[2].strip(),
        call.arguments[3].strip() if len(call.arguments) > 3 else "{}",
        call.expression,
        call.line,
    )


class ScriptIndex:
    def __init__(self, archive: Path):
        self.archive = Path(archive)
        with ZipFile(self.archive) as handle:
            self.members = tuple(sorted(handle.namelist()))
        self.prefab_members = {
            Path(name).stem.lower(): name
            for name in self.members
            if name.startswith("scripts/prefabs/") and name.endswith(".lua")
        }
        self.strings_source = self._read_optional("scripts/strings.lua")
        self.recipes_source = self._read_optional("scripts/recipes.lua")
        self.names = _assigned_strings(self.strings_source, "STRINGS.NAMES")
        self.names.update(_table_string_entries(self.strings_source, "NAMES"))
        self.recipe_descriptions = _assigned_strings(
            self.strings_source, "STRINGS.RECIPE_DESC"
        )
        self.recipe_descriptions.update(
            _table_string_entries(self.strings_source, "RECIPE_DESC")
        )
        self.recipes: Dict[str, RecipeRecord] = {}
        for call in _iter_calls(self.recipes_source, ("Recipe2",)):
            record = _recipe_record(call)
            if record is not None and record.product not in self.recipes:
                self.recipes[record.product] = record
        self.prefab_declarations: Dict[str, Tuple[str, int]] = {}
        for member in self.members:
            if not member.startswith("scripts/prefabs/") or not member.endswith(".lua"):
                continue
            source = self.read(member)
            for call in _iter_calls(source, ("Prefab",)):
                if not call.arguments:
                    continue
                prefab_id = _literal_string(call.arguments[0])
                if prefab_id is not None:
                    self.prefab_declarations.setdefault(
                        prefab_id.lower(), (member, call.line)
                    )

    def _read_optional(self, member: str) -> str:
        return self.read(member) if member in self.members else ""

    def read(self, member: str) -> str:
        with ZipFile(self.archive) as handle:
            return handle.read(member).decode("utf-8-sig")

    def resolution(self, prefab_id: str) -> Optional[Tuple[str, str]]:
        prefab_id = prefab_id.lower()
        if prefab_id in self.prefab_members:
            return ("prefab_filename", f"{self.prefab_members[prefab_id]}:filename")
        if prefab_id in self.prefab_declarations:
            member, line = self.prefab_declarations[prefab_id]
            return ("prefab_declaration", f"{member}:line:{line}")
        if prefab_id in self.recipes:
            return ("recipe_product", f"scripts/recipes.lua:line:{self.recipes[prefab_id].line}")
        if prefab_id in self.names:
            return ("string_registry", f"scripts/strings.lua:line:{self.names[prefab_id][1]}")
        return None


def _direct_request_evidence(requests: Iterable[DependencyRequest]) -> List[Dict[str, str]]:
    return [
        {"relation": request.relation, "subject": request.requested_by}
        for request in sorted(set(requests))
    ]


def _walk_dependency_markers(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        if (
            value.get("dependency_candidate") is True
            and value.get("resolution") == "unresolved"
        ):
            prefab_id = value.get("prefab_id") or value.get("target_prefab_id")
            if isinstance(prefab_id, str) and prefab_id:
                yield prefab_id.lower()
        for nested in value.values():
            yield from _walk_dependency_markers(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_dependency_markers(nested)


def derive_dependency_requests(*bundles: FactBundle) -> List[DependencyRequest]:
    """Collect only explicit unresolved dependency markers from Tu Tiên facts."""

    requests = set()
    for bundle in bundles:
        for fact in bundle.facts:
            if fact.subject.namespace != "tu_tien":
                continue
            requested_by = f"tu_tien:{fact.subject.prefab_id}"
            for prefab_id in _walk_dependency_markers(fact.payload):
                requests.add(DependencyRequest(prefab_id, fact.kind, requested_by))
    return sorted(requests)


def _expression_payload(expression: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"source_expression": expression.strip()}
    value = _literal_number(expression)
    if value is not None:
        payload["value"] = value
    return payload


def _source_facts(
    index: ScriptIndex, prefab_id: str, source_ref: SourceRef
) -> Tuple[List[Fact], List[Dict[str, Any]]]:
    member = index.prefab_members.get(prefab_id)
    if member is None:
        return [], []
    source = index.read(member)
    subject = EntityKey("base_game", prefab_id)
    facts: List[Fact] = []
    errors: List[Dict[str, Any]] = []

    stat_calls = {
        "SetDamage": (("damage", 0),),
        "InitCondition": (("armor_condition", 0), ("armor_absorption", 1)),
        "SetMaxUses": (("max_uses", 0),),
    }
    for call in _iter_calls(source, tuple(stat_calls)):
        expected_receiver = {
            "SetDamage": "inst.components.weapon:",
            "InitCondition": "inst.components.armor:",
            "SetMaxUses": "inst.components.finiteuses:",
        }[call.name]
        if not _has_receiver(source, call, expected_receiver):
            continue
        positions = stat_calls[call.name]
        if any(position >= len(call.arguments) for _, position in positions):
            errors.append(
                {
                    "code": "unsupported_base_source_pattern",
                    "path": member,
                    "line": call.line,
                    "expression": call.expression,
                }
            )
            continue
        for key, position in positions:
            facts.append(
                Fact(
                    "stat",
                    subject,
                    {"key": key, **_expression_payload(call.arguments[position])},
                    source_ref,
                    0.9,
                    f"{member}:line:{call.line}",
                )
            )

    edible = re.compile(
        r"^\s*inst\.components\.edible\.(healthvalue|hungervalue|sanityvalue)\s*=\s*(.+?)\s*$",
        re.MULTILINE,
    )
    edible_keys = {"healthvalue": "health", "hungervalue": "hunger", "sanityvalue": "sanity"}
    for match in edible.finditer(source):
        line = source.count("\n", 0, match.start()) + 1
        facts.append(
            Fact(
                "stat",
                subject,
                {"key": edible_keys[match.group(1)], **_expression_payload(match.group(2))},
                source_ref,
                0.9,
                f"{member}:line:{line}",
            )
        )

    for call in _iter_calls(source, ("SetLoot", "AddChanceLoot", "SetUp")):
        expected_receiver = (
            "inst.components.pickable:"
            if call.name == "SetUp"
            else "inst.components.lootdropper:"
        )
        if not _has_receiver(source, call, expected_receiver):
            continue
        if call.name == "SetLoot" and call.arguments:
            table = call.arguments[0].strip()
            if table.startswith("{") and table.endswith("}"):
                loot = [
                    value
                    for value in (_literal_string(entry) for entry in _split_top_level(table[1:-1]))
                    if value is not None
                ]
                for target, count in sorted(Counter(value.lower() for value in loot).items()):
                    facts.append(
                        Fact(
                            "acquisition",
                            subject,
                            {
                                "type": "drop",
                                "source": {"namespace": "base_game", "prefab_id": prefab_id},
                                "target": {"prefab_id": target, "resolution": "not_imported"},
                                "count": count,
                                "chance": 1,
                                "conditions": {},
                                "source_expression": call.expression,
                            },
                            source_ref,
                            0.9,
                            f"{member}:line:{call.line}",
                        )
                    )
                if loot:
                    continue
        elif call.name == "AddChanceLoot" and len(call.arguments) >= 2:
            target = _literal_string(call.arguments[0])
            if target is not None:
                chance_payload = _expression_payload(call.arguments[1])
                facts.append(
                    Fact(
                        "acquisition",
                        subject,
                        {
                            "type": "drop",
                            "source": {"namespace": "base_game", "prefab_id": prefab_id},
                            "target": {"prefab_id": target.lower(), "resolution": "not_imported"},
                            "count": 1,
                            "chance_expression": chance_payload["source_expression"],
                            **({"chance": chance_payload["value"]} if "value" in chance_payload else {}),
                            "conditions": {},
                            "source_expression": call.expression,
                        },
                        source_ref,
                        0.9,
                        f"{member}:line:{call.line}",
                    )
                )
                continue
        elif call.name == "SetUp" and len(call.arguments) >= 2:
            target = _literal_string(call.arguments[0])
            if target is not None:
                regrow = _expression_payload(call.arguments[1])
                facts.append(
                    Fact(
                        "acquisition",
                        subject,
                        {
                            "type": "harvest",
                            "source": {"namespace": "base_game", "prefab_id": prefab_id},
                            "target": {"prefab_id": target.lower(), "resolution": "not_imported"},
                            "chance": 1,
                            "count": 1,
                            "conditions": {},
                            "regrow_expression": regrow["source_expression"],
                            **({"regrow_time": regrow["value"]} if "value" in regrow else {}),
                            "source_expression": call.expression,
                        },
                        source_ref,
                        0.9,
                        f"{member}:line:{call.line}",
                    )
                )
                continue
        errors.append(
            {
                "code": "unsupported_base_source_pattern",
                "path": member,
                "line": call.line,
                "expression": call.expression,
            }
        )
    return facts, errors


def enrich_dependencies(
    archive: Path,
    requests: Iterable[DependencyRequest],
    base_translation_po: Path,
) -> FactBundle:
    """Resolve exact requested IDs and enrich only them plus one recipe level."""

    archive = Path(archive)
    index = ScriptIndex(archive)
    scripts_source = SourceRef(
        "base-game-scripts",
        "base_game_source",
        _display_path(archive),
        "snapshot",
        _sha256(archive),
    )
    sources = [scripts_source]
    po_values: Dict[str, str] = {}
    po_source: Optional[SourceRef] = None
    po_path = Path(base_translation_po)
    if po_path.is_file():
        po_values = load_po_by_context(po_path)
        po_source = SourceRef(
            "base-game-vi-translation",
            "mod_translation",
            _display_path(po_path),
            "snapshot",
            _sha256(po_path),
        )
        sources.append(po_source)

    direct: Dict[str, List[DependencyRequest]] = {}
    for request in requests:
        normalized = DependencyRequest(
            request.prefab_id.lower(), request.relation, request.requested_by
        )
        direct.setdefault(normalized.prefab_id, []).append(normalized)

    selected: Dict[str, List[Dict[str, str]]] = {
        prefab_id: _direct_request_evidence(values)
        for prefab_id, values in direct.items()
    }
    direct_resolved = {
        prefab_id for prefab_id in direct if index.resolution(prefab_id) is not None
    }
    for prefab_id in sorted(direct_resolved):
        recipe = index.recipes.get(prefab_id)
        if recipe is None:
            continue
        roots = sorted({request.requested_by for request in direct[prefab_id]})
        for ingredient_id, _amount in recipe.ingredients:
            if index.resolution(ingredient_id) is None:
                continue
            evidence = selected.setdefault(ingredient_id, [])
            for root in roots:
                record = {
                    "relation": "recipe_ingredient",
                    "subject": f"base_game:{prefab_id}",
                    "root_requested_by": root,
                }
                if record not in evidence:
                    evidence.append(record)

    facts: List[Fact] = []
    errors: List[Dict[str, Any]] = []
    for prefab_id in sorted(direct):
        if index.resolution(prefab_id) is None:
            errors.append(
                {
                    "code": "unresolved_base_game_dependency",
                    "prefab_id": prefab_id,
                    "requested_by": _direct_request_evidence(direct[prefab_id]),
                }
            )

    for prefab_id in sorted(selected):
        resolution = index.resolution(prefab_id)
        if resolution is None:
            continue
        discovered_by, locator = resolution
        subject = EntityKey("base_game", prefab_id)
        facts.append(
            Fact(
                "entity",
                subject,
                {
                    "entity_type": "unknown",
                    "discovered_by": discovered_by,
                    "requested_by": sorted(
                        selected[prefab_id], key=lambda value: json.dumps(value, sort_keys=True)
                    ),
                },
                scripts_source,
                1.0,
                locator,
            )
        )
        if prefab_id in index.names:
            value, line = index.names[prefab_id]
            facts.append(
                Fact(
                    "name",
                    subject,
                    {"lang": "en", "value": value},
                    scripts_source,
                    1.0,
                    f"scripts/strings.lua:line:{line}",
                )
            )
        if prefab_id in index.recipe_descriptions:
            value, line = index.recipe_descriptions[prefab_id]
            facts.append(
                Fact(
                    "description",
                    subject,
                    {"lang": "en", "value": value, "description_type": "recipe"},
                    scripts_source,
                    1.0,
                    f"scripts/strings.lua:line:{line}",
                )
            )
        if po_source is not None:
            for context, kind, description_type in (
                (f"STRINGS.NAMES.{prefab_id.upper()}", "name", None),
                (f"STRINGS.RECIPE_DESC.{prefab_id.upper()}", "description", "recipe"),
                (
                    f"STRINGS.CHARACTERS.GENERIC.DESCRIBE.{prefab_id.upper()}",
                    "description",
                    "generic",
                ),
            ):
                translated = po_values.get(context)
                if translated:
                    payload: Dict[str, Any] = {"lang": "vi", "value": translated}
                    if description_type is not None:
                        payload["description_type"] = description_type
                    facts.append(
                        Fact(
                            kind,
                            subject,
                            payload,
                            po_source,
                            0.9,
                            f"context:{context}",
                        )
                    )

        if prefab_id in direct_resolved and prefab_id in index.recipes:
            recipe = index.recipes[prefab_id]
            config = _table_fields(recipe.config_expression)
            output_count_expression = config.get("numtogive", "1")
            output_count = _literal_number(output_count_expression)
            recipe_payload: Dict[str, Any] = {
                "tech_expression": recipe.tech_expression,
                "config_expression": recipe.config_expression,
                "source_expression": recipe.expression,
                "output_count_expression": output_count_expression,
            }
            if output_count is not None:
                recipe_payload["output_count"] = output_count
            facts.append(
                Fact(
                    "recipe",
                    subject,
                    recipe_payload,
                    scripts_source,
                    0.9,
                    f"scripts/recipes.lua:line:{recipe.line}",
                )
            )
            for position, (ingredient_id, amount_expression) in enumerate(
                recipe.ingredients
            ):
                if index.resolution(ingredient_id) is None:
                    errors.append(
                        {
                            "code": "unresolved_recipe_ingredient",
                            "prefab_id": ingredient_id,
                            "recipe": prefab_id,
                            "line": recipe.line,
                        }
                    )
                    continue
                amount_payload = _expression_payload(amount_expression)
                payload: Dict[str, Any] = {
                    "position": position,
                    "ingredient": {
                        "namespace": "base_game",
                        "prefab_id": ingredient_id,
                        "resolution": "resolved",
                    },
                    "amount_expression": amount_payload["source_expression"],
                }
                if "value" in amount_payload:
                    payload["amount"] = amount_payload["value"]
                facts.append(
                    Fact(
                        "ingredient",
                        subject,
                        payload,
                        scripts_source,
                        0.9,
                        f"scripts/recipes.lua:line:{recipe.line}:ingredient:{position}",
                    )
                )

        new_facts, new_errors = _source_facts(index, prefab_id, scripts_source)
        facts.extend(new_facts)
        errors.extend(new_errors)

    facts.sort(
        key=lambda fact: (
            fact.kind,
            fact.subject.namespace,
            fact.subject.prefab_id,
            fact.locator,
            json.dumps(fact.payload, ensure_ascii=False, sort_keys=True),
        )
    )
    errors.sort(key=lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True))
    return FactBundle(1, sorted(sources), facts, errors)


def extract_base_game_dependencies(
    static_bundle: FactBundle,
    runtime_bundle: FactBundle,
    scripts_archive: Path,
    base_translation_po: Path,
) -> FactBundle:
    return enrich_dependencies(
        scripts_archive,
        derive_dependency_requests(static_bundle, runtime_bundle),
        base_translation_po,
    )
