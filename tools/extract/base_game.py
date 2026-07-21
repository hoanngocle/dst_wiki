from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple
from zipfile import ZipFile

from tools.extract.contracts import EntityKey, Fact, FactBundle, SourceRef
from tools.extract.lua_strings import decode_lua_string_literal
from tools.extract.po_strings import load_po_by_context


VERSION = re.compile(r'^\s*version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)
PREFAB_CATEGORIES = (
    "item",
    "mob",
    "boss",
    "character",
    "structure",
    "effect",
    "other",
)


def discover_prefab_modules(members: Iterable[str]) -> Dict[str, str]:
    """Return one stable prefab ID for every direct prefab Lua module."""

    discovered: Dict[str, str] = {}
    for member in sorted(members):
        path = PurePosixPath(member)
        if path.parent.as_posix() != "scripts/prefabs" or path.suffix != ".lua":
            continue
        prefab_id = path.stem.lower()
        if prefab_id in discovered:
            raise ValueError(f"duplicate prefab module id {prefab_id}")
        discovered[prefab_id] = member
    return discovered


def _version_from_modinfo(path: Path, fallback: str) -> str:
    if not path.is_file():
        return fallback
    match = VERSION.search(path.read_text(encoding="utf-8-sig"))
    return match.group(1) if match else fallback


@dataclass(frozen=True, order=True)
class DependencyRequest:
    prefab_id: str
    relation: str
    requested_by: str
    fact_kind: str = ""
    locator: str = ""
    confidence: float = 0.0
    source_id: str = ""
    source_kind: str = ""
    source_path: str = ""
    source_version: str = ""
    source_sha256: str = ""


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
    warnings: Tuple[Tuple[int, str], ...] = ()


@dataclass(frozen=True)
class FunctionScope:
    name: str
    source: str
    line: int


@dataclass(frozen=True)
class ConstructorBinding:
    member: str
    line: int
    expression: str


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
    if start >= len(source) or source[start] != "[":
        return None
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


def _code_mask(source: str) -> str:
    """Return same-length Lua with strings/comments blanked and newlines kept."""

    masked = list(source)
    index = 0
    while index < len(source):
        skipped = _skip_string_or_comment(source, index)
        if skipped is None:
            index += 1
            continue
        for position in range(index, skipped):
            if masked[position] not in "\r\n":
                masked[position] = " "
        index = skipped
    return "".join(masked)


def _code_end_before_comment(source: str, start: int, end: int) -> int:
    """Return the first real Lua comment offset, ignoring comment text in strings."""

    index = start
    while index < end:
        if source.startswith("--", index):
            return index
        skipped = _skip_string_or_comment(source, index)
        if skipped is not None:
            index = min(skipped, end)
        else:
            index += 1
    return end


def _function_end(masked: str, function_offset: int) -> Optional[int]:
    tokens = list(re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", masked))
    start_index = next(
        (index for index, token in enumerate(tokens) if token.start() == function_offset),
        None,
    )
    if start_index is None:
        return None
    stack: List[Dict[str, Any]] = [{"kind": "function", "awaiting_do": False}]
    for token in tokens[start_index + 1 :]:
        word = token.group(0)
        if word == "function":
            stack.append({"kind": "function", "awaiting_do": False})
        elif word == "if":
            stack.append({"kind": "if", "awaiting_do": False})
        elif word in ("for", "while"):
            stack.append({"kind": word, "awaiting_do": True})
        elif word == "repeat":
            stack.append({"kind": "repeat", "awaiting_do": False})
        elif word == "do":
            pending = next(
                (
                    entry
                    for entry in reversed(stack)
                    if entry.get("awaiting_do") is True
                ),
                None,
            )
            if pending is not None:
                pending["awaiting_do"] = False
            else:
                stack.append({"kind": "do", "awaiting_do": False})
        elif word == "until":
            if stack and stack[-1]["kind"] == "repeat":
                stack.pop()
        elif word == "end":
            if stack:
                stack.pop()
            if not stack:
                return token.end()
    return None


def _function_scopes(source: str) -> Dict[str, FunctionScope]:
    masked = _code_mask(source)
    definitions = re.compile(
        r"\blocal\s+(?:function\s+([A-Za-z_][A-Za-z0-9_]*)|"
        r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*function)\s*\("
    )
    result: Dict[str, FunctionScope] = {}
    for match in definitions.finditer(masked):
        name = match.group(1) or match.group(2)
        function_offset = masked.find("function", match.start(), match.end())
        end = _function_end(masked, function_offset)
        if end is None:
            continue
        result[name] = FunctionScope(
            name,
            source[function_offset:end],
            source.count("\n", 0, function_offset) + 1,
        )
    return result


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


def classify_prefab_module(prefab_id: str, source: str) -> str:
    """Classify a prefab module using deterministic literal source signals."""

    normalized_id = prefab_id.lower()
    if (
        "_fx" in normalized_id
        or normalized_id.endswith("fx")
        or any(
            marker in normalized_id
            for marker in (
                "_projectile",
                "_placer",
                "_classified",
                "_marker",
            )
        )
    ):
        return "effect"

    calls = list(_iter_calls(source, ("MakePlayerCharacter", "AddTag", "AddComponent")))
    if any(call.name == "MakePlayerCharacter" for call in calls):
        return "character"

    tags = {
        value.lower()
        for call in calls
        if call.name == "AddTag" and call.arguments
        for value in [_literal_string(call.arguments[0])]
        if value is not None
    }
    if "epic" in tags:
        return "boss"

    components = {
        value.lower()
        for call in calls
        if call.name == "AddComponent" and call.arguments
        for value in [_literal_string(call.arguments[0])]
        if value is not None
    }
    masked = _code_mask(source)
    for component in ("health", "combat", "locomotor", "inventoryitem", "workable"):
        if re.search(rf"\.components\.{component}\b", masked):
            components.add(component)

    if tags.intersection({"animal", "character", "hostile", "monster", "smallcreature"}) or {
        "health",
        "combat",
    }.issubset(components):
        return "mob"
    if "inventoryitem" in components:
        return "item"
    if "structure" in tags or "workable" in components:
        return "structure"
    if re.search(r"\bpersists\s*=\s*false\b", masked):
        return "effect"
    return "other"


def _reachable_function_scopes(
    initial: FunctionScope, functions: Dict[str, FunctionScope]
) -> List[FunctionScope]:
    ordered: List[FunctionScope] = []
    visited = set()

    def visit(scope: FunctionScope) -> None:
        if scope.name in visited:
            return
        visited.add(scope.name)
        ordered.append(scope)
        for call in _iter_calls(scope.source, tuple(functions)):
            target = functions.get(call.name)
            if target is not None:
                visit(target)

    visit(initial)
    return ordered


def _prefab_constructor_bindings(source: str) -> Dict[str, str]:
    bindings: Dict[str, str] = {}
    for call in _iter_calls(source, ("Prefab",)):
        if len(call.arguments) < 2:
            continue
        prefab_id = _literal_string(call.arguments[0])
        constructor = call.arguments[1].strip()
        if prefab_id is None or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*", constructor
        ):
            continue
        bindings[prefab_id.lower()] = constructor
    return bindings


def classify_prefabs_in_module(source: str) -> Dict[str, str]:
    """Classify named Prefab returns from their reachable constructor scopes."""

    functions = _function_scopes(source)
    result: Dict[str, str] = {}
    for prefab_id, constructor in sorted(_prefab_constructor_bindings(source).items()):
        initial = functions.get(constructor)
        if initial is None:
            continue
        scoped_source = "\n".join(
            scope.source for scope in _reachable_function_scopes(initial, functions)
        )
        result[prefab_id] = classify_prefab_module(prefab_id, scoped_source)
    return result


def _shared_loot_tables(source: str) -> Dict[str, List[Tuple[str, Any]]]:
    tables: Dict[str, List[Tuple[str, Any]]] = {}
    for call in _iter_calls(source, ("SetSharedLootTable",)):
        if len(call.arguments) < 2:
            continue
        table_name = _literal_string(call.arguments[0])
        raw_table = call.arguments[1].strip()
        if table_name is None or not (
            raw_table.startswith("{") and raw_table.endswith("}")
        ):
            continue
        entries: List[Tuple[str, Any]] = []
        for raw_entry in _split_top_level(raw_table[1:-1]):
            guaranteed_target = _literal_string(raw_entry)
            if guaranteed_target is not None:
                entries.append((guaranteed_target.lower(), 1))
                continue
            if not (raw_entry.startswith("{") and raw_entry.endswith("}")):
                continue
            values = _split_top_level(raw_entry[1:-1])
            if len(values) < 2:
                continue
            target = _literal_string(values[0])
            chance = _literal_number(values[1])
            if target is not None and chance is not None:
                entries.append((target.lower(), chance))
        tables[table_name.lower()] = entries
    return tables


def _named_string_tables(source: str) -> Dict[str, List[str]]:
    masked = _code_mask(source)
    pattern = re.compile(
        r"\b(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{"
    )
    result: Dict[str, List[str]] = {}
    for match in pattern.finditer(masked):
        opening = masked.find("{", match.start(), match.end())
        if opening < 0:
            continue
        try:
            closing = _matching_delimiter(source, opening)
        except ValueError:
            continue
        values = [
            value.lower()
            for entry in _split_top_level(source[opening + 1 : closing])
            for value in [_literal_string(entry)]
            if value is not None
        ]
        if values:
            result[match.group(1)] = values
    return result


def _reward_method(constructor_source: str) -> str:
    masked = _code_mask(constructor_source)
    return (
        "mine_post_defeat"
        if re.search(r"SetWorkAction\s*\(\s*ACTIONS\.MINE\s*\)", masked)
        else "kill"
    )


def extract_prefab_rewards(prefab_id: str, source: str) -> List[Dict[str, Any]]:
    """Extract deterministic static rewards for one named prefab constructor."""

    normalized_id = prefab_id.lower()
    functions = _function_scopes(source)
    constructor_name = _prefab_constructor_bindings(source).get(normalized_id)
    constructor = functions.get(constructor_name or "")
    if constructor is None:
        return []
    constructor_scopes = _reachable_function_scopes(constructor, functions)
    constructor_source = "\n".join(scope.source for scope in constructor_scopes)
    method = _reward_method(constructor_source)
    shared_tables = _shared_loot_tables(source)
    raw_rewards: List[Dict[str, Any]] = []

    def add_reward(
        target: str,
        chance: Any,
        count: int,
        conditions: Dict[str, Any],
        reward_method: Optional[str] = None,
    ) -> None:
        raw_rewards.append(
            {
                "target": target.lower(),
                "chance": chance,
                "count": count,
                "method": reward_method or method,
                "source_prefab_id": normalized_id,
                "conditions": conditions,
            }
        )

    for scope in constructor_scopes:
        for call in _iter_calls(
            scope.source,
            ("SetLoot", "AddChanceLoot", "SetChanceLootTable"),
        ):
            if call.name == "SetLoot" and call.arguments:
                raw_table = call.arguments[0].strip()
                if raw_table.startswith("{") and raw_table.endswith("}"):
                    values = [
                        value.lower()
                        for entry in _split_top_level(raw_table[1:-1])
                        for value in [_literal_string(entry)]
                        if value is not None
                    ]
                    for target, count in Counter(values).items():
                        add_reward(target, 1, count, {})
            elif call.name == "AddChanceLoot" and len(call.arguments) >= 2:
                target = _literal_string(call.arguments[0])
                chance = _literal_number(call.arguments[1])
                if target is not None and chance is not None:
                    add_reward(target, chance, 1, {})
            elif call.name == "SetChanceLootTable" and call.arguments:
                table_name = _literal_string(call.arguments[0])
                if table_name is None:
                    continue
                for target, chance in shared_tables.get(table_name.lower(), []):
                    add_reward(
                        target,
                        chance,
                        1,
                        {"loot_table": table_name.lower()},
                    )

    callback_names = set()
    for scope in constructor_scopes:
        for call in _iter_calls(scope.source, ("SetOnWorkCallback",)):
            if call.arguments:
                callback = call.arguments[0].strip()
                if callback in functions:
                    callback_names.add(callback)
    named_tables = _named_string_tables(source)
    for callback_name in sorted(callback_names):
        callback = functions[callback_name]
        callback_mask = _code_mask(callback.source)
        loop_tables = {
            match.group(1): match.group(2)
            for match in re.finditer(
                r"\bfor\s+(?:[A-Za-z_][A-Za-z0-9_]*\s*,\s*)?"
                r"([A-Za-z_][A-Za-z0-9_]*)\s+in\s+ipairs\s*\(\s*"
                r"([A-Za-z_][A-Za-z0-9_]*)\s*\)",
                callback_mask,
            )
        }
        for call in _iter_calls(callback.source, ("SpawnPrefab",)):
            if not call.arguments:
                continue
            target = _literal_string(call.arguments[0])
            if target is not None:
                add_reward(target, 1, 1, {"callback": callback_name})
                continue
            argument = call.arguments[0].strip()
            table_name = loop_tables.get(argument)
            if table_name is None:
                continue
            for table_target in named_tables.get(table_name, []):
                add_reward(
                    table_target,
                    1,
                    1,
                    {"callback": callback_name, "source_table": table_name},
                )

    loot_setup_callbacks = set()
    for scope in constructor_scopes:
        for call in _iter_calls(scope.source, ("SetLootSetupFn",)):
            if call.arguments:
                callback_name = call.arguments[0].strip()
                if callback_name in functions:
                    loot_setup_callbacks.add(callback_name)
    for callback_name in sorted(loot_setup_callbacks):
        callback = functions[callback_name]
        callback_mask = _code_mask(callback.source)
        variable_tables = {
            match.group(1): match.group(2)
            for match in re.finditer(
                r"\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*"
                r"([A-Za-z_][A-Za-z0-9_]*)\s*\[",
                callback_mask,
            )
        }
        event_match = re.search(
            r"SPECIAL_EVENTS\.([A-Z][A-Z0-9_]*)",
            callback_mask,
        )
        event = event_match.group(1) if event_match is not None else None
        reward_method = "conditional" if event is not None else method
        for call in _iter_calls(callback.source, ("AddChanceLoot",)):
            if len(call.arguments) < 2:
                continue
            target = _literal_string(call.arguments[0])
            chance = _literal_number(call.arguments[1])
            base_conditions: Dict[str, Any] = {"callback": callback_name}
            if event is not None:
                base_conditions["event"] = event
            if target is not None:
                add_reward(
                    target,
                    chance,
                    1,
                    base_conditions,
                    reward_method,
                )
                continue
            table_name = variable_tables.get(call.arguments[0].strip())
            if table_name is None:
                continue
            conditions = {**base_conditions, "source_table": table_name}
            for table_target in named_tables.get(table_name, []):
                add_reward(
                    table_target,
                    None,
                    1,
                    conditions,
                    reward_method,
                )

    grouped: Dict[Tuple[str, Any, str, str], Dict[str, Any]] = {}
    for reward in raw_rewards:
        conditions_key = json.dumps(
            reward["conditions"], ensure_ascii=False, sort_keys=True
        )
        key = (
            reward["target"],
            reward["chance"],
            reward["method"],
            conditions_key,
        )
        current = grouped.setdefault(key, {**reward, "count": 0})
        current["count"] += reward["count"]
    return [grouped[key] for key in sorted(grouped, key=lambda value: (value[0], value[1], value[2], value[3]))]


def _literal_number(expression: str) -> Optional[Any]:
    expression = expression.strip()
    if not re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", expression):
        return None
    value = float(expression)
    return int(value) if value.is_integer() and not any(c in expression for c in ".eE") else value


def _find_assignment_table(source: str, table_name: str) -> Optional[int]:
    masked = _code_mask(source)
    tokens = list(re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]*\b", masked))
    delimiters: List[str] = []
    blocks: List[Dict[str, Any]] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    scan_offset = 0
    previous_word = ""
    previous_was_top_level = False

    for token in tokens:
        for char in masked[scan_offset : token.start()]:
            if char in pairs:
                delimiters.append(pairs[char])
            elif char in ")]}":
                if delimiters and char == delimiters[-1]:
                    delimiters.pop()

        word = token.group(0)
        is_top_level = not blocks and not delimiters
        if (
            word == table_name
            and is_top_level
            and not (previous_word == "local" and previous_was_top_level)
        ):
            cursor = token.end()
            while cursor < len(masked) and masked[cursor].isspace():
                cursor += 1
            if masked[cursor : cursor + 1] == "=":
                cursor += 1
                while cursor < len(masked) and masked[cursor].isspace():
                    cursor += 1
                if masked[cursor : cursor + 1] == "{":
                    return cursor

        if word == "function":
            blocks.append({"kind": "function", "awaiting_do": False})
        elif word == "if":
            blocks.append({"kind": "if", "awaiting_do": False})
        elif word in ("for", "while"):
            blocks.append({"kind": word, "awaiting_do": True})
        elif word == "repeat":
            blocks.append({"kind": "repeat", "awaiting_do": False})
        elif word == "do":
            pending = next(
                (
                    entry
                    for entry in reversed(blocks)
                    if entry.get("awaiting_do") is True
                ),
                None,
            )
            if pending is not None:
                pending["awaiting_do"] = False
            else:
                blocks.append({"kind": "do", "awaiting_do": False})
        elif word == "until":
            if blocks and blocks[-1]["kind"] == "repeat":
                blocks.pop()
        elif word == "end":
            if blocks:
                blocks.pop()

        previous_word = word
        previous_was_top_level = is_top_level
        scan_offset = token.end()
    return None


def _find_direct_child_table(
    source: str, parent_opening: int, parent_closing: int, child_name: str
) -> Optional[int]:
    index = parent_opening + 1
    while index < parent_closing:
        skipped = _skip_string_or_comment(source, index)
        if skipped is not None:
            index = skipped
            continue
        if source[index].isalpha() or source[index] == "_":
            end = index + 1
            while end < parent_closing and (
                source[end].isalnum() or source[end] == "_"
            ):
                end += 1
            cursor = end
            while cursor < parent_closing and source[cursor].isspace():
                cursor += 1
            if source[index:end] == child_name and source[cursor : cursor + 1] == "=":
                cursor += 1
                while cursor < parent_closing and source[cursor].isspace():
                    cursor += 1
                if source[cursor : cursor + 1] == "{":
                    return cursor
            index = end
            continue
        if source[index] in "{([":
            try:
                index = _matching_delimiter(source, index) + 1
            except ValueError:
                return None
            continue
        index += 1
    return None


def _table_string_entries(source: str, table_name: str) -> Dict[str, Tuple[str, int]]:
    root_opening = _find_assignment_table(source, "STRINGS")
    if root_opening is None:
        return {}
    try:
        root_closing = _matching_delimiter(source, root_opening)
    except ValueError:
        return {}
    opening = _find_direct_child_table(
        source, root_opening, root_closing, table_name
    )
    if opening is None:
        return {}
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


def _child_table_string_entries(
    source: str, parent_opening: int, parent_closing: int, table_name: str
) -> Dict[str, Tuple[str, int]]:
    opening = _find_direct_child_table(
        source, parent_opening, parent_closing, table_name
    )
    if opening is None:
        return {}
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
        if entry_match is None:
            continue
        value = _literal_string(entry_match.group(3))
        if value is None:
            continue
        key = (entry_match.group(1) or entry_match.group(2)).lower()
        local = body.find(entry, cursor)
        cursor = max(cursor, local + len(entry))
        line = source.count("\n", 0, opening + 1 + max(local, 0)) + 1
        result[key] = (value, line)
    return result


def _returned_child_table_strings(
    source: str, table_name: str
) -> Dict[str, Tuple[str, int]]:
    masked = _code_mask(source)
    match = re.search(r"\breturn\s*\{", masked)
    if match is None:
        return {}
    opening = masked.find("{", match.start(), match.end())
    try:
        closing = _matching_delimiter(source, opening)
    except ValueError:
        return {}
    return _child_table_string_entries(source, opening, closing, table_name)


def _has_receiver(source: str, call: LuaCall, receiver: str) -> bool:
    line_start = source.rfind("\n", 0, call.offset) + 1
    return source[line_start : call.offset].rstrip().endswith(receiver)


def _assigned_strings(source: str, prefix: str) -> Dict[str, Tuple[str, int]]:
    masked = _code_mask(source)
    pattern = re.compile(
        rf'^[\t ]*{re.escape(prefix)}\.([A-Z0-9_]+)[\t ]*=',
        re.MULTILINE,
    )
    result: Dict[str, Tuple[str, int]] = {}
    for match in pattern.finditer(masked):
        line_end = source.find("\n", match.end())
        if line_end < 0:
            line_end = len(source)
        expression = source[match.end() : line_end].strip()
        value = _literal_string(expression)
        if value is not None:
            result[match.group(1).lower()] = (
                value,
                source.count("\n", 0, match.start()) + 1,
            )
    return result


def _numeric_table_entries(source: str) -> Dict[str, Any]:
    masked = _code_mask(source)
    pattern = re.compile(
        r"^[\t ]*([A-Z][A-Z0-9_]*)[\t ]*=[\t ]*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*,?",
        re.MULTILINE,
    )
    return {
        match.group(1): value
        for match in pattern.finditer(masked)
        for value in [_literal_number(match.group(2))]
        if value is not None
    }


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
    warnings: List[Tuple[int, str]] = []
    table_offset = call.expression.find(ingredient_table)
    table_line_offset = call.expression[: max(table_offset, 0)].count("\n")
    for ingredient_call in _iter_calls(ingredient_table[1:-1], ("Ingredient",)):
        ingredient_line = call.line + table_line_offset + ingredient_call.line - 1
        if len(ingredient_call.arguments) < 2:
            warnings.append((ingredient_line, ingredient_call.expression))
            continue
        prefab_id = _literal_string(ingredient_call.arguments[0])
        if prefab_id is None:
            warnings.append(
                (ingredient_line, ingredient_call.arguments[0].strip())
            )
            continue
        ingredients.append((prefab_id.lower(), ingredient_call.arguments[1].strip()))
    return RecipeRecord(
        product.lower(),
        tuple(ingredients),
        call.arguments[2].strip(),
        call.arguments[3].strip() if len(call.arguments) > 3 else "{}",
        call.expression,
        call.line,
        tuple(warnings),
    )


class ScriptIndex:
    def __init__(self, archive: Path):
        self.archive = Path(archive)
        with ZipFile(self.archive) as handle:
            self.members = tuple(sorted(handle.namelist()))
            prefab_members = tuple(
                name
                for name in self.members
                if name.startswith("scripts/prefabs/") and name.endswith(".lua")
            )
            cached_members = set(prefab_members)
            cached_members.update(
                {
                    "scripts/strings.lua",
                    "scripts/tuning.lua",
                    "scripts/recipes.lua",
                    "scripts/speech_wilson.lua",
                }
            )
            source_cache = {
                name: handle.read(name).decode("utf-8-sig")
                for name in sorted(cached_members)
                if name in self.members
            }
        self.prefab_members = discover_prefab_modules(prefab_members)
        self.prefab_sources: Dict[str, str] = {
            name: source_cache[name] for name in prefab_members
        }
        self.strings_source = source_cache.get("scripts/strings.lua", "")
        self.tuning_values = _numeric_table_entries(
            source_cache.get("scripts/tuning.lua", "")
        )
        self.recipes_source = source_cache.get("scripts/recipes.lua", "")
        self.names = _assigned_strings(self.strings_source, "STRINGS.NAMES")
        self.names.update(_table_string_entries(self.strings_source, "NAMES"))
        self.recipe_descriptions = _assigned_strings(
            self.strings_source, "STRINGS.RECIPE_DESC"
        )
        self.recipe_descriptions.update(
            _table_string_entries(self.strings_source, "RECIPE_DESC")
        )
        self.generic_descriptions: Dict[str, Tuple[str, int]] = {}
        if "scripts/speech_wilson.lua" in source_cache:
            self.generic_descriptions = _returned_child_table_strings(
                source_cache["scripts/speech_wilson.lua"], "DESCRIBE"
            )
        self.recipes: Dict[str, RecipeRecord] = {}
        for call in _iter_calls(self.recipes_source, ("Recipe2",)):
            record = _recipe_record(call)
            if record is not None and record.product not in self.recipes:
                self.recipes[record.product] = record
        self.prefab_declarations: Dict[str, ConstructorBinding] = {}
        self.function_scopes: Dict[str, Dict[str, FunctionScope]] = {}
        for member in prefab_members:
            source = self.prefab_sources[member]
            self.function_scopes[member] = _function_scopes(source)
            for call in _iter_calls(source, ("Prefab",)):
                if len(call.arguments) < 2:
                    continue
                prefab_id = _literal_string(call.arguments[0])
                if prefab_id is not None:
                    self.prefab_declarations.setdefault(
                        prefab_id.lower(),
                        ConstructorBinding(
                            member, call.line, call.arguments[1].strip()
                        ),
                    )

    def _read_optional(self, member: str) -> str:
        return self.read(member) if member in self.members else ""

    def read(self, member: str) -> str:
        if member in self.prefab_sources:
            return self.prefab_sources[member]
        with ZipFile(self.archive) as handle:
            return handle.read(member).decode("utf-8-sig")

    def resolution(self, prefab_id: str) -> Optional[Tuple[str, str]]:
        prefab_id = prefab_id.lower()
        if prefab_id in self.prefab_members:
            return ("prefab_filename", f"{self.prefab_members[prefab_id]}:filename")
        if prefab_id in self.prefab_declarations:
            binding = self.prefab_declarations[prefab_id]
            return (
                "prefab_declaration",
                f"{binding.member}:line:{binding.line}",
            )
        if prefab_id in self.recipes:
            return ("recipe_product", f"scripts/recipes.lua:line:{self.recipes[prefab_id].line}")
        if prefab_id in self.names:
            return ("string_registry", f"scripts/strings.lua:line:{self.names[prefab_id][1]}")
        return None

    def constructor_scopes(
        self, prefab_id: str
    ) -> Tuple[Optional[str], List[FunctionScope], Optional[Dict[str, Any]]]:
        binding = self.prefab_declarations.get(prefab_id)
        if binding is None:
            return (
                self.prefab_members.get(prefab_id),
                [],
                {
                    "code": "unsupported_constructor_binding",
                    "prefab_id": prefab_id,
                    "expression": "missing exact Prefab declaration",
                    "path": self.prefab_members.get(prefab_id, ""),
                },
            )
        expression = binding.expression.strip()
        functions = self.function_scopes[binding.member]
        initial: Optional[FunctionScope] = None
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expression):
            initial = functions.get(expression)
        elif expression.startswith("function"):
            initial = FunctionScope(
                "<inline>", expression, binding.line
            )
        if initial is None:
            return (
                binding.member,
                [],
                {
                    "code": "unsupported_constructor_binding",
                    "prefab_id": prefab_id,
                    "expression": expression,
                    "path": binding.member,
                    "line": binding.line,
                },
            )

        ordered: List[FunctionScope] = []
        visited = set()

        def visit(scope: FunctionScope) -> None:
            if scope.name in visited:
                return
            visited.add(scope.name)
            ordered.append(scope)
            for call in _iter_calls(scope.source, tuple(functions)):
                target = functions.get(call.name)
                if target is not None:
                    visit(target)

        visit(initial)
        return binding.member, ordered, None


def _direct_request_evidence(
    requests: Iterable[DependencyRequest],
) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for request in sorted(set(requests)):
        record: Dict[str, Any] = {
            "relation": request.relation,
            "subject": request.requested_by,
        }
        if request.fact_kind:
            record["fact_kind"] = request.fact_kind
        if request.locator:
            record["locator"] = request.locator
        if request.confidence:
            record["confidence"] = request.confidence
        if request.source_id:
            record["source"] = {
                "source_id": request.source_id,
                "kind": request.source_kind,
                "path": request.source_path,
                "version": request.source_version,
                "sha256": request.source_sha256,
            }
        result.append(record)
    return result


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
            relation = fact.kind
            if fact.kind == "relation" and isinstance(fact.payload.get("relation"), str):
                relation = fact.payload["relation"]
            elif fact.kind == "acquisition" and isinstance(fact.payload.get("type"), str):
                relation = fact.payload["type"]
            for prefab_id in _walk_dependency_markers(fact.payload):
                requests.add(
                    DependencyRequest(
                        prefab_id,
                        relation,
                        requested_by,
                        fact.kind,
                        fact.locator,
                        fact.confidence,
                        fact.source.source_id,
                        fact.source.kind,
                        fact.source.path,
                        fact.source.version,
                        fact.source.sha256,
                    )
                )
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
    member, scopes, binding_warning = index.constructor_scopes(prefab_id)
    subject = EntityKey("base_game", prefab_id)
    facts: List[Fact] = []
    errors: List[Dict[str, Any]] = []
    if binding_warning is not None:
        errors.append(binding_warning)
    if member is None or not scopes:
        return facts, errors

    def stat_expression_payload(expression: str) -> Dict[str, Any]:
        payload = _expression_payload(expression)
        if "value" in payload:
            return payload
        match = re.fullmatch(
            r"(-?)TUNING\.([A-Z][A-Z0-9_]*)",
            expression.strip(),
        )
        if match is None or match.group(2) not in index.tuning_values:
            return payload
        value = index.tuning_values[match.group(2)]
        payload["value"] = -value if match.group(1) else value
        return payload

    stat_calls = {
        "SetDamage": (("damage", 0),),
        "InitCondition": (("armor_condition", 0), ("armor_absorption", 1)),
        "SetMaxUses": (("max_uses", 0),),
        "SetMaxHealth": (("max_health", 0),),
        "SetDefaultDamage": (("attack_damage", 0),),
        "SetAttackPeriod": (("attack_period", 0),),
        "SetRange": (("attack_range", 0), ("hit_range", 1)),
        "SetBaseDamage": (("planar_damage", 0),),
    }
    for scope in scopes:
        source = scope.source
        line_offset = scope.line - 1
        for call in _iter_calls(source, tuple(stat_calls)):
            expected_receiver = {
                "SetDamage": "inst.components.weapon:",
                "InitCondition": "inst.components.armor:",
                "SetMaxUses": "inst.components.finiteuses:",
                "SetMaxHealth": "inst.components.health:",
                "SetDefaultDamage": "inst.components.combat:",
                "SetAttackPeriod": "inst.components.combat:",
                "SetRange": "inst.components.combat:",
                "SetBaseDamage": "inst.components.planardamage:",
            }[call.name]
            if not _has_receiver(source, call, expected_receiver):
                continue
            positions = stat_calls[call.name]
            if any(position >= len(call.arguments) for _, position in positions):
                errors.append(
                    {
                        "code": "unsupported_base_source_pattern",
                        "path": member,
                        "line": line_offset + call.line,
                        "expression": call.expression,
                    }
                )
                continue
            for key, position in positions:
                facts.append(
                    Fact(
                        "stat",
                        subject,
                        {"key": key, **stat_expression_payload(call.arguments[position])},
                        source_ref,
                        0.9,
                        f"{member}:line:{line_offset + call.line}",
                    )
                )

        edible = re.compile(
            r"^[\t ]*inst\.components\.edible\.(healthvalue|hungervalue|sanityvalue)[\t ]*=[\t ]*",
            re.MULTILINE,
        )
        edible_keys = {"healthvalue": "health", "hungervalue": "hunger", "sanityvalue": "sanity"}
        masked_scope = _code_mask(source)
        for match in edible.finditer(masked_scope):
            line = line_offset + source.count("\n", 0, match.start()) + 1
            line_end = source.find("\n", match.end())
            if line_end < 0:
                line_end = len(source)
            expression_end = _code_end_before_comment(
                source, match.end(), line_end
            )
            expression = source[match.end() : expression_end].strip()
            facts.append(
                Fact(
                    "stat",
                    subject,
                    {"key": edible_keys[match.group(1)], **stat_expression_payload(expression)},
                    source_ref,
                    0.9,
                    f"{member}:line:{line}",
                )
            )

        component_assignments = {
            ("locomotor", "walkspeed"): "walk_speed",
            ("locomotor", "runspeed"): "run_speed",
            ("sanityaura", "aura"): "sanity_aura",
        }
        assignment_pattern = re.compile(
            r"^[\t ]*inst\.components\.([a-z_][a-z0-9_]*)\."
            r"([a-z_][a-z0-9_]*)[\t ]*=[\t ]*",
            re.MULTILINE,
        )
        for match in assignment_pattern.finditer(masked_scope):
            key = component_assignments.get((match.group(1), match.group(2)))
            if key is None:
                continue
            line = line_offset + source.count("\n", 0, match.start()) + 1
            line_end = source.find("\n", match.end())
            if line_end < 0:
                line_end = len(source)
            expression_end = _code_end_before_comment(
                source, match.end(), line_end
            )
            expression = source[match.end() : expression_end].strip()
            facts.append(
                Fact(
                    "stat",
                    subject,
                    {"key": key, **stat_expression_payload(expression)},
                    source_ref,
                    0.9,
                    f"{member}:line:{line}",
                )
            )

    return facts, errors


def _reverse_acquisition_facts(
    index: ScriptIndex, selected_ids: Iterable[str], source_ref: SourceRef
) -> Tuple[List[Fact], List[Dict[str, Any]]]:
    selected = set(selected_ids)
    facts: List[Fact] = []
    errors: List[Dict[str, Any]] = []
    seen = set()
    for source_prefab in sorted(index.prefab_declarations):
        member, scopes, warning = index.constructor_scopes(source_prefab)
        if member is None:
            continue
        if warning is not None:
            # Emit reverse-index binding warnings only when this member contains a
            # selected literal and could therefore hide a relevant acquisition.
            member_source = index.read(member)
            if any(
                re.search(rf'["\']{re.escape(prefab_id)}["\']', member_source)
                for prefab_id in selected
            ):
                errors.append({**warning, "stage": "reverse_acquisition"})
            continue
        member_source = index.read(member)
        for reward in extract_prefab_rewards(source_prefab, member_source):
            conditions = reward.get("conditions")
            if not isinstance(conditions, dict) or not conditions:
                continue
            target = reward["target"]
            if target not in selected:
                continue
            key = (
                source_prefab,
                target,
                reward["method"],
                json.dumps(conditions, sort_keys=True),
            )
            if key in seen:
                continue
            seen.add(key)
            facts.append(
                Fact(
                    "acquisition",
                    EntityKey("base_game", target),
                    {
                        "type": "drop",
                        "source": {
                            "namespace": "base_game",
                            "prefab_id": source_prefab,
                            "resolution": (
                                "resolved"
                                if source_prefab in selected
                                else "evidence_only"
                            ),
                        },
                        "target": {
                            "namespace": "base_game",
                            "prefab_id": target,
                            "resolution": "resolved",
                        },
                        "chance": reward["chance"],
                        "count": reward["count"],
                        "method": reward["method"],
                        "conditions": conditions,
                        "source_member": member,
                        "source_expression": "static reward extraction",
                    },
                    source_ref,
                    0.9,
                    f"{member}:reward:{source_prefab}:{target}",
                )
            )
        for scope in scopes:
            line_offset = scope.line - 1
            for call in _iter_calls(
                scope.source,
                ("SetLoot", "AddChanceLoot", "AddRandomLoot", "SetUp"),
            ):
                loot_call = call.name in (
                    "SetLoot",
                    "AddChanceLoot",
                    "AddRandomLoot",
                )
                receiver = (
                    "inst.components.lootdropper:"
                    if loot_call
                    else "inst.components.pickable:"
                )
                if not _has_receiver(scope.source, call, receiver):
                    continue
                line = line_offset + call.line
                candidates: List[Tuple[str, Dict[str, Any]]] = []
                def warn(expression: str) -> None:
                    errors.append(
                        {
                            "code": "unsupported_base_source_subexpression",
                            "path": member,
                            "line": line,
                            "expression": expression.strip(),
                            "source_prefab_id": source_prefab,
                            "call": call.name,
                        }
                    )

                if call.name == "SetLoot" and call.arguments:
                    table = call.arguments[0].strip()
                    if table.startswith("{") and table.endswith("}"):
                        values = []
                        for entry in _split_top_level(table[1:-1]):
                            value = _literal_string(entry)
                            if value is None:
                                if entry.strip():
                                    warn(entry)
                            else:
                                values.append(value.lower())
                        for target, count in sorted(Counter(values).items()):
                            candidates.append(
                                (target, {"chance": 1, "count": count})
                            )
                    else:
                        warn(table)
                elif call.name in ("AddChanceLoot", "AddRandomLoot") and len(call.arguments) >= 2:
                    target = _literal_string(call.arguments[0])
                    if target is not None:
                        value = _expression_payload(call.arguments[1])
                        key = "chance" if call.name == "AddChanceLoot" else "weight"
                        detail: Dict[str, Any] = {
                            "count": 1,
                            f"{key}_expression": value["source_expression"],
                        }
                        if "value" in value:
                            detail[key] = value["value"]
                        candidates.append((target.lower(), detail))
                    else:
                        warn(call.arguments[0])
                elif call.name == "SetUp" and len(call.arguments) >= 2:
                    target = _literal_string(call.arguments[0])
                    if target is not None:
                        regrow = _expression_payload(call.arguments[1])
                        detail = {
                            "chance": 1,
                            "count": 1,
                            "regrow_expression": regrow["source_expression"],
                        }
                        if "value" in regrow:
                            detail["regrow_time"] = regrow["value"]
                        candidates.append((target.lower(), detail))
                    else:
                        warn(call.arguments[0])
                else:
                    warn(call.expression)

                for target, detail in candidates:
                    if target not in selected:
                        continue
                    key = (source_prefab, target, call.name, member, line)
                    if key in seen:
                        continue
                    seen.add(key)
                    facts.append(
                        Fact(
                            "acquisition",
                            EntityKey("base_game", target),
                            {
                                "type": "harvest" if call.name == "SetUp" else "drop",
                                "source": {
                                    "namespace": "base_game",
                                    "prefab_id": source_prefab,
                                    "resolution": (
                                        "resolved"
                                        if source_prefab in selected
                                        else "evidence_only"
                                    ),
                                },
                                "target": {
                                    "namespace": "base_game",
                                    "prefab_id": target,
                                    "resolution": "resolved",
                                },
                                "conditions": {},
                                "source_member": member,
                                "source_expression": call.expression,
                                **detail,
                            },
                            source_ref,
                            0.9,
                            f"{member}:line:{line}",
                        )
                    )
    return facts, errors


def classify_public_prefabs(index: ScriptIndex) -> Dict[str, str]:
    """Classify direct modules plus named Mob/Boss declarations they contain."""

    scoped_categories = {
        member: classify_prefabs_in_module(index.prefab_sources[member])
        for member in sorted(set(index.prefab_members.values()))
    }
    categories = {
        prefab_id: scoped_categories[member].get(
            prefab_id,
            classify_prefab_module(prefab_id, index.prefab_sources[member]),
        )
        for prefab_id, member in index.prefab_members.items()
    }
    for prefab_id, binding in sorted(index.prefab_declarations.items()):
        declared_categories = scoped_categories.get(binding.member)
        if declared_categories is None:
            continue
        declared_category = declared_categories.get(prefab_id)
        if prefab_id in index.names and declared_category in {"mob", "boss"}:
            categories.setdefault(prefab_id, declared_category)
    return categories


def enrich_dependencies(
    archive: Path,
    requests: Iterable[DependencyRequest],
    base_translation_po: Path,
    *,
    include_all_modules: bool = False,
) -> FactBundle:
    """Resolve requested IDs, optionally including every prefab module."""

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
            _version_from_modinfo(po_path.parent / "modinfo.lua", "unknown"),
            _sha256(po_path),
        )
        sources.append(po_source)

    direct: Dict[str, List[DependencyRequest]] = {}
    for request in requests:
        normalized = DependencyRequest(
            request.prefab_id.lower(),
            request.relation,
            request.requested_by,
            request.fact_kind,
            request.locator,
            request.confidence,
            request.source_id,
            request.source_kind,
            request.source_path,
            request.source_version,
            request.source_sha256,
        )
        direct.setdefault(normalized.prefab_id, []).append(normalized)

    selected: Dict[str, List[Dict[str, Any]]] = {
        prefab_id: _direct_request_evidence(values)
        for prefab_id, values in direct.items()
    }
    module_categories: Dict[str, str] = {}
    if include_all_modules:
        module_categories = classify_public_prefabs(index)
        for prefab_id in module_categories:
            selected.setdefault(prefab_id, [])

        for source_prefab in sorted(index.prefab_declarations):
            binding = index.prefab_declarations[source_prefab]
            member_source = index.read(binding.member)
            for reward in extract_prefab_rewards(source_prefab, member_source):
                target = reward["target"]
                if index.resolution(target) is None:
                    continue
                evidence = selected.setdefault(target, [])
                marker = {
                    "relation": "drop_reward",
                    "subject": f"base_game:{source_prefab}",
                }
                if marker not in evidence:
                    evidence.append(marker)

    direct_resolved = {
        prefab_id for prefab_id in direct if index.resolution(prefab_id) is not None
    }
    recipe_roots = (
        set(index.prefab_members)
        if include_all_modules
        else direct_resolved
    )
    for prefab_id in sorted(recipe_roots):
        recipe = index.recipes.get(prefab_id)
        if recipe is None:
            continue
        roots = _direct_request_evidence(direct.get(prefab_id, []))
        for ingredient_id, _amount in recipe.ingredients:
            if index.resolution(ingredient_id) is None:
                continue
            evidence = selected.setdefault(ingredient_id, [])
            for root in roots:
                record = {
                    "relation": "recipe_ingredient",
                    "subject": f"base_game:{prefab_id}",
                    "root_requested_by": root["subject"],
                    "root_evidence": root,
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
                    "entity_type": module_categories.get(
                        prefab_id,
                        "dependency" if include_all_modules else "unknown",
                    ),
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
        if prefab_id in index.generic_descriptions:
            value, line = index.generic_descriptions[prefab_id]
            facts.append(
                Fact(
                    "description",
                    subject,
                    {"lang": "en", "value": value, "description_type": "generic"},
                    scripts_source,
                    1.0,
                    f"scripts/speech_wilson.lua:line:{line}",
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

        if prefab_id in index.recipes and (
            prefab_id in direct_resolved or prefab_id in module_categories
        ):
            recipe = index.recipes[prefab_id]
            for warning_line, warning_expression in recipe.warnings:
                errors.append(
                    {
                        "code": "unsupported_base_source_subexpression",
                        "path": "scripts/recipes.lua",
                        "line": warning_line,
                        "expression": warning_expression,
                        "recipe": prefab_id,
                    }
                )
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

    acquisition_facts, acquisition_errors = _reverse_acquisition_facts(
        index, selected, scripts_source
    )
    facts.extend(acquisition_facts)
    errors.extend(acquisition_errors)

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


def enrich_prefab_modules(
    archive: Path,
    requests: Iterable[DependencyRequest],
    base_translation_po: Path,
) -> FactBundle:
    """Enrich every prefab module while preserving dependency evidence."""

    return enrich_dependencies(
        archive,
        requests,
        base_translation_po,
        include_all_modules=True,
    )


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
