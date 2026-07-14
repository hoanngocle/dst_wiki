import ast
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


def _literal(expression: str):
    try:
        value = ast.literal_eval(expression)
    except (SyntaxError, ValueError):
        return None
    return value if isinstance(value, str) else None


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
