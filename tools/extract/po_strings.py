import ast
import re
from pathlib import Path
from typing import Dict, Optional


FIELD = re.compile(r'^(msgctxt|msgid|msgstr(?:\[0\])?)\s+(".*")\s*$')
CONTINUED = re.compile(r'^\s*(".*")\s*$')


def _decode_po_string(value: str) -> str:
    try:
        decoded = ast.literal_eval(value)
    except (SyntaxError, ValueError) as exc:
        raise ValueError(f"invalid PO string literal: {value}") from exc
    if not isinstance(decoded, str):
        raise ValueError(f"PO value is not a string: {value}")
    return decoded


def load_po_by_context(path: Path) -> Dict[str, str]:
    """Map exact PO contexts to translated text, falling back to ``msgid``.

    Standard continued quoted lines are concatenated. Empty header entries and
    entries without a context are intentionally excluded.
    """

    result: Dict[str, str] = {}
    entry: Dict[str, str] = {}
    active: Optional[str] = None

    def flush() -> None:
        context = entry.get("msgctxt")
        if context:
            result[context] = entry.get("msgstr") or entry.get("msgid", "")

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines() + [""]:
        line = raw_line.strip()
        if not line:
            flush()
            entry = {}
            active = None
            continue
        if line.startswith("#"):
            continue
        match = FIELD.match(line)
        if match:
            field, encoded = match.groups()
            active = "msgstr" if field.startswith("msgstr") else field
            entry[active] = _decode_po_string(encoded)
            continue
        match = CONTINUED.match(line)
        if match and active:
            entry[active] = entry.get(active, "") + _decode_po_string(match.group(1))
    return result
