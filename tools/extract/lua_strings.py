import re
from pathlib import Path
from typing import Dict, List


PATTERNS = (
    ("name", re.compile(r"^STRINGS\.NAMES\.([A-Z0-9_]+)\s*=\s*(.+?)\s*$")),
    (
        "recipe_description",
        re.compile(r"^STRINGS\.RECIPE_DESC\.([A-Z0-9_]+)\s*=\s*(.+?)\s*$"),
    ),
    (
        "description",
        re.compile(
            r"^STRINGS\.CHARACTERS\.GENERIC\.DESCRIBE\.([A-Z0-9_]+)\s*=\s*(.+?)\s*$"
        ),
    ),
)
ALIAS = re.compile(
    r"^STRINGS\.(?:NAMES|RECIPE_DESC|CHARACTERS\.GENERIC\.DESCRIBE)\.([A-Z0-9_]+)$"
)
TABLE_START = re.compile(r"^\s*local\s+names\s*=\s*\{\s*$")
TABLE_ENTRY = re.compile(r'^\s*\["([A-Za-z0-9_]+)"\]\s*=\s*(.+?)\s*,?\s*$')
CHARACTER_METADATA = re.compile(
    r'^STRINGS\.(CHARACTER_TITLES|CHARACTER_SURVIVABILITY|'
    r'CHARACTER_DESCRIPTIONS|CHARACTER_QUOTES)\s*'
    r'\[\s*["\']([A-Za-z0-9_]+)["\']\s*\]\s*=\s*(.+?)\s*$'
)


ESCAPES = {
    "a": b"\a",
    "b": b"\b",
    "f": b"\f",
    "n": b"\n",
    "r": b"\r",
    "t": b"\t",
    "v": b"\v",
    "\\": b"\\",
    '"': b'"',
    "'": b"'",
}


def decode_lua_string_literal(expression: str) -> str:
    """Decode one Lua short-string literal without evaluating Lua code.

    Lua decimal escapes represent bytes rather than Python's octal escapes. The
    resulting byte sequence is decoded as UTF-8, matching the encoding used by
    the mod sources. Long-bracket strings and expressions are intentionally out
    of scope.
    """

    if len(expression) < 2 or expression[0] not in ('"', "'"):
        raise ValueError("not a Lua short-string literal")
    quote = expression[0]
    if expression[-1] != quote:
        raise ValueError("unterminated Lua short-string literal")

    body = expression[1:-1]
    output = bytearray()
    index = 0
    while index < len(body):
        char = body[index]
        if char != "\\":
            output.extend(char.encode("utf-8"))
            index += 1
            continue

        index += 1
        if index >= len(body):
            raise ValueError("trailing backslash in Lua string")
        escaped = body[index]
        if escaped in ESCAPES:
            output.extend(ESCAPES[escaped])
            index += 1
            continue
        if escaped.isdigit() and escaped.isascii():
            end = index
            while (
                end < len(body)
                and end < index + 3
                and body[end].isdigit()
                and body[end].isascii()
            ):
                end += 1
            value = int(body[index:end], 10)
            if value > 255:
                raise ValueError("Lua decimal escape exceeds one byte")
            output.append(value)
            index = end
            continue
        if escaped == "x":
            digits = body[index + 1 : index + 3]
            if len(digits) != 2 or not all(
                value in "0123456789abcdefABCDEF" for value in digits
            ):
                raise ValueError("invalid Lua hexadecimal escape")
            output.append(int(digits, 16))
            index += 3
            continue
        if escaped == "z":
            index += 1
            while index < len(body) and body[index].isspace():
                index += 1
            continue
        if escaped == "\n":
            output.append(10)
            index += 1
            continue
        if escaped == "\r":
            output.append(10)
            index += 1
            if index < len(body) and body[index] == "\n":
                index += 1
            continue
        raise ValueError(f"unsupported Lua escape: \\{escaped}")

    try:
        return output.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Lua string bytes are not valid UTF-8") from exc


def _literal(expression: str):
    try:
        return decode_lua_string_literal(expression)
    except ValueError:
        return None


def parse_string_assignments(path: Path) -> List[Dict[str, object]]:
    """Parse a deliberately restricted subset of top-level DST string assignments.

    Expressions outside string literals and direct ``STRINGS`` aliases are retained
    as ``unparsed_expression`` rather than evaluated as Lua.
    """

    rows: List[Dict[str, object]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        for field, pattern in PATTERNS:
            match = pattern.match(line.strip())
            if not match:
                continue
            prefab_id, expression = match.groups()
            row: Dict[str, object] = {
                "field": field,
                "prefab_id": prefab_id.lower(),
                "line": line_number,
            }
            alias = ALIAS.match(expression)
            if alias:
                row["alias_prefab_id"] = alias.group(1).lower()
            elif expression.startswith(('"', "'")):
                value = _literal(expression)
                if value is None:
                    row["unparsed_expression"] = expression
                else:
                    row["value"] = value
            else:
                row["unparsed_expression"] = expression
            rows.append(row)
            break
    return rows


def parse_simple_names_table(path: Path) -> List[Dict[str, object]]:
    """Parse the translation mod's bounded ``local names = {...}`` table.

    This handles the table-loop idiom used by the supplied language mod without
    executing arbitrary Lua. Other tables and non-literal values are ignored.
    """

    rows: List[Dict[str, object]] = []
    in_names = False
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        if not in_names:
            in_names = bool(TABLE_START.match(line))
            continue
        if line.strip() == "}":
            break
        match = TABLE_ENTRY.match(line)
        if not match:
            continue
        prefab_id, expression = match.groups()
        value = _literal(expression)
        row: Dict[str, object] = {
            "field": "name",
            "prefab_id": prefab_id.lower(),
            "line": line_number,
        }
        if value is None:
            row["unparsed_expression"] = expression
        else:
            row["value"] = value
        rows.append(row)
    return rows


def parse_character_metadata_assignments(path: Path) -> List[Dict[str, object]]:
    """Parse exact literal character-profile assignments from a language mod.

    Only a quoted prefab key and a Lua short-string value on the same line are
    accepted. Comments, computed keys and function calls are never evaluated.
    """

    field_names = {
        "CHARACTER_TITLES": "character_title",
        "CHARACTER_SURVIVABILITY": "character_survivability",
        "CHARACTER_DESCRIPTIONS": "character_description",
        "CHARACTER_QUOTES": "character_quote",
    }
    rows: List[Dict[str, object]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), 1
    ):
        match = CHARACTER_METADATA.match(line.strip())
        if match is None:
            continue
        table_name, prefab_id, expression = match.groups()
        value = _literal(expression)
        row: Dict[str, object] = {
            "field": field_names[table_name],
            "prefab_id": prefab_id.lower(),
            "line": line_number,
        }
        if value is None:
            row["unparsed_expression"] = expression
        else:
            row["value"] = value
        rows.append(row)
    return rows
