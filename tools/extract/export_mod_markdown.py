"""Render the player-facing Tu Tiên reference from extracted game data."""

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

from tools.extract.contracts import SourceRef


_DIRECT_STRING = re.compile(
    r'^\s*(STRINGS(?:\.[A-Z0-9_]+)+)\s*=\s*("(?:[^"\\]|\\.)*")\s*$'
)
_TABLE_START = re.compile(r"^\s*(STRINGS(?:\.[A-Z0-9_]+)+)\s*=\s*\{")
_TABLE_MEMBER_START = re.compile(
    r"^\s*(?:([A-Z0-9_]+)|\[([0-9]+)\])\s*=\s*\{"
)
_TABLE_MEMBER_STRING = re.compile(
    r'^\s*(?:([A-Z0-9_]+)|\[([0-9]+)\])\s*=\s*("(?:[^"\\]|\\.)*")\s*,?\s*$'
)
_TABLE_LIST_STRING = re.compile(r'^\s*("(?:[^"\\]|\\.)*")\s*,?\s*$')
_MODINFO_STRING = re.compile(
    r'^\s*(name|label|description)\s*=\s*("(?:[^"\\]|\\.)*")\s*,?\s*$'
)
_MOD_VERSION = re.compile(r'^\s*version\s*=\s*"([^"\\]+)"\s*$')


def _lua_string(value: str) -> str:
    """Decode the quoted literal subset shared by Lua and Python strings."""

    return ast.literal_eval(value)


def extract_game_strings(paths: Iterable[Path]) -> List[Dict[str, object]]:
    """Return direct and nested table ``STRINGS`` values with locators."""

    rows: List[Dict[str, object]] = []
    for path in sorted((Path(path) for path in paths), key=lambda value: str(value)):
        tables = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            direct = _DIRECT_STRING.match(line)
            if direct:
                rows.append(
                    {
                        "key": direct.group(1),
                        "value": _lua_string(direct.group(2)),
                        "source": path.name,
                        "line": number,
                    }
                )
                continue

            table = _TABLE_START.match(line)
            if table:
                tables.append({"key": table.group(1), "next_index": 1})
                continue

            if tables:
                current = tables[-1]
                nested_table = _TABLE_MEMBER_START.match(line)
                nested = _TABLE_MEMBER_STRING.match(line)
                list_value = _TABLE_LIST_STRING.match(line)
                if nested_table:
                    name, index = nested_table.groups()
                    suffix = f".{name}" if name else f"[{index}]"
                    tables.append({"key": f"{current['key']}{suffix}", "next_index": 1})
                elif nested:
                    name, index, value = nested.groups()
                    suffix = f".{name}" if name else f"[{index}]"
                    rows.append(
                        {
                            "key": f"{current['key']}{suffix}",
                            "value": _lua_string(value),
                            "source": path.name,
                            "line": number,
                        }
                    )
                elif list_value:
                    index = current["next_index"]
                    current["next_index"] = index + 1
                    rows.append(
                        {
                            "key": f"{current['key']}[{index}]",
                            "value": _lua_string(list_value.group(1)),
                            "source": path.name,
                            "line": number,
                        }
                    )
                for _ in range(line.count("}")):
                    if tables:
                        tables.pop()

    return sorted(rows, key=lambda row: (str(row["key"]), str(row["source"]), int(row["line"])))


def _entity_index(catalog: Mapping[str, object]) -> Dict[str, Mapping[str, object]]:
    entities = catalog.get("entities", [])
    if not isinstance(entities, list):
        raise ValueError("catalog.entities must be a list")
    index = {}
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        key = entity.get("key")
        if isinstance(key, str):
            index[key] = entity
    return index


def _name(entity: Mapping[str, object], fallback: str) -> str:
    names = entity.get("name", {})
    if isinstance(names, dict):
        for language in ("vi", "en"):
            value = names.get(language)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return fallback


def _resolve_entity(
    prefab: str,
    entities: Mapping[str, Mapping[str, object]],
    mod_prefabs: Sequence[str],
) -> Mapping[str, object]:
    namespace = "tu_tien" if prefab in mod_prefabs else "base_game"
    return entities.get(f"{namespace}:{prefab}") or entities.get(f"tu_tien:{prefab}") or entities.get(f"base_game:{prefab}") or {}


def _character_cost(row: Mapping[str, object]) -> str:
    amount = row.get("amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        return ""
    number = str(int(amount)) if float(amount).is_integer() else str(amount)
    kind = row.get("type")
    labels = {
        "decrease_health": "máu",
        "decrease_sanity": "tỉnh táo",
    }
    return f"giảm {number} {labels.get(kind, str(kind))}"


def render_crafting_recipes(catalog: Mapping[str, object], runtime: Mapping[str, object]) -> str:
    """Render runtime recipes as Vietnamese formulas without guessing game data."""

    recipes = runtime.get("recipes", [])
    targets = runtime.get("targets", [])
    if not isinstance(recipes, list) or not isinstance(targets, list):
        raise ValueError("runtime recipes and targets must be lists")
    mod_prefabs = [value for value in targets if isinstance(value, str)]
    entities = _entity_index(catalog)

    def product_name(recipe: Mapping[str, object]) -> str:
        product = str(recipe.get("product", ""))
        return _name(_resolve_entity(product, entities, mod_prefabs), product)

    ordered = sorted(
        (recipe for recipe in recipes if isinstance(recipe, dict)),
        key=lambda recipe: (product_name(recipe).casefold(), str(recipe.get("product", ""))),
    )
    lines = [
        "# Công thức chế tạo Tu Tiên",
        "",
        f"Nguồn runtime ghi nhận **{len(ordered)}** công thức đang đăng ký trong game.",
        "",
    ]
    for recipe in ordered:
        product = str(recipe.get("product", ""))
        output = recipe.get("output_count", 1)
        output_count = int(output) if isinstance(output, (int, float)) and float(output).is_integer() else output
        product_entity = _resolve_entity(product, entities, mod_prefabs)
        display_product = _name(product_entity, product)
        ingredients = recipe.get("ingredients", [])
        formula_parts = []
        if isinstance(ingredients, list):
            for ingredient in ingredients:
                if not isinstance(ingredient, dict):
                    continue
                prefab = str(ingredient.get("prefab", ""))
                amount = ingredient.get("amount", 1)
                count = int(amount) if isinstance(amount, (int, float)) and float(amount).is_integer() else amount
                formula_parts.append(f"{count} × {_name(_resolve_entity(prefab, entities, mod_prefabs), prefab)}")
        formula = " + ".join(formula_parts) if formula_parts else "Không cần vật phẩm"

        conditions = [f"Công nghệ: `{recipe.get('tech') or 'không rõ'}`"]
        builders = recipe.get("builder_tags", [])
        if isinstance(builders, list) and builders:
            builder_labels = [
                f"{_name(_resolve_entity(str(builder), entities, mod_prefabs), str(builder))} (`{builder}`)"
                for builder in builders
            ]
            conditions.append("Nhân vật: " + ", ".join(builder_labels))
        costs = [
            _character_cost(cost)
            for cost in recipe.get("character_ingredients", [])
            if isinstance(cost, dict)
        ]
        costs = [cost for cost in costs if cost]
        if costs:
            conditions.append("Chi phí: " + "; ".join(costs))

        lines.extend(
            [
                f"### {display_product} — `{product}`",
                "",
                f"**Công thức:** {formula} → {output_count} × {display_product}",
                "",
                "**Điều kiện:** " + "; ".join(conditions),
            ]
        )
        description = product_entity.get("description", {}) if isinstance(product_entity, dict) else {}
        if isinstance(description, dict):
            text = description.get("vi") or description.get("en")
            if isinstance(text, str) and text.strip():
                lines.extend(["", f"**Mô tả:** {text.strip()}"])
        lines.append("")
    return "\n".join(lines)


def _modinfo_strings(paths: Iterable[Path]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for path in sorted((Path(path) for path in paths), key=lambda value: str(value)):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = _MODINFO_STRING.match(line)
            if not match:
                continue
            rows.append(
                {
                    "key": f"MODINFO.{match.group(1).upper()}.{number}",
                    "value": _lua_string(match.group(2)),
                    "source": path.name,
                    "line": number,
                }
            )
    return rows


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def render_game_text(rows: Iterable[Mapping[str, object]]) -> str:
    ordered = sorted(
        rows,
        key=lambda row: (str(row["key"]), str(row["source"]), int(row["line"])),
    )
    lines = [
        "# Text hiển thị trong game",
        "",
        "Các dòng dưới đây giữ key kỹ thuật và vị trí nguồn để đối chiếu khi gắn vào wiki.",
        "",
        "| Key | Text Việt hoá | Nguồn |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| `{_markdown_cell(row['key'])}` | {_markdown_cell(row['value'])} | `{_markdown_cell(row['source'])}:{row['line']}` |"
        for row in ordered
    )
    lines.append("")
    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _source_files(mod_roots: Iterable[Path]) -> List[Path]:
    paths = []
    for root in sorted((Path(root) for root in mod_roots), key=lambda value: str(value)):
        for path in root.rglob("*.lua"):
            if path.name.startswith("speech_"):
                continue
            try:
                source = path.read_bytes().decode("utf-8")
            except UnicodeDecodeError:
                continue
            if "STRINGS" in source or path.name == "modinfo.lua":
                paths.append(path)
    return sorted(paths, key=lambda value: str(value))


def _source_root(path: Path, roots: Sequence[Path]) -> Path:
    matches = [root for root in roots if path.is_relative_to(root)]
    if len(matches) != 1:
        raise ValueError(f"game text path does not belong to exactly one mod root: {path}")
    return matches[0]


def _mod_version(root: Path) -> str:
    info = root / "modinfo.lua"
    if not info.is_file():
        return "unknown"
    for line in info.read_text(encoding="utf-8").splitlines():
        match = _MOD_VERSION.match(line)
        if match:
            return match.group(1)
    return "unknown"


def collect_game_text(mod_roots: Iterable[Path]):
    """Collect queryable game text and its per-file source provenance."""

    roots = [Path(root) for root in mod_roots]
    versions = {root: _mod_version(root) for root in roots}
    sources = []
    rows = []
    for path in _source_files(roots):
        root = _source_root(path, roots)
        relative_path = path.relative_to(root.parent).as_posix()
        source = SourceRef(
            f"game-text:{relative_path}",
            "mod_translation" if root.name == "3721859355" else "mod_static",
            relative_path,
            versions[root],
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        sources.append(source)
        parsed = extract_game_strings([path])
        if path.name == "modinfo.lua":
            parsed.extend(_modinfo_strings([path]))
        for value in parsed:
            locator = f"line:{value['line']}"
            identity = f"{source.source_id}\0{value['key']}\0{locator}"
            rows.append(
                {
                    "text_id": hashlib.sha256(identity.encode("utf-8")).hexdigest(),
                    "text_key": value["key"],
                    "value_vi": value["value"],
                    "source_id": source.source_id,
                    "locator": locator,
                }
            )
    return sorted(sources), sorted(rows, key=lambda row: row["text_id"])


def _render_readme(
    runtime: Mapping[str, object], recipe_count: int, string_count: int, mod_roots: Iterable[Path]
) -> str:
    version = runtime.get("mod_version", "không rõ")
    sources = ", ".join(f"`{Path(root)}`" for root in mod_roots)
    return "\n".join(
        [
            "# Text game-facing của mod Tu Tiên",
            "",
            f"- Phiên bản mod runtime: **{version}**.",
            f"- Đã xuất: **{recipe_count} công thức** và **{string_count} chuỗi hiển thị**.",
            f"- Nguồn chuỗi: {sources}.",
            "- Lời thoại nhân vật trong `scripts/speech_*.lua` được loại trừ có chủ đích; chúng sẽ được gắn vào trang nhân vật ở giai đoạn sau.",
            "- Công thức lấy từ `data/raw/runtime.json`; không suy đoán từ `scripts/main/recipes.lua` vì file này đã được bảo vệ/biên dịch.",
            "",
            "## Tệp",
            "",
            "- [Công thức chế tạo](crafting-recipes.md)",
            "- [Text UI và thông báo](game-text.md)",
            "",
        ]
    )


def export_mod_markdown(
    catalog_path: Path,
    runtime_path: Path,
    mod_roots: Iterable[Path],
    output_dir: Path,
) -> None:
    """Write the deterministic, non-dialogue Markdown reference set."""

    catalog = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
    runtime = json.loads(Path(runtime_path).read_text(encoding="utf-8"))
    if not isinstance(catalog, dict) or not isinstance(runtime, dict):
        raise ValueError("catalog and runtime inputs must be JSON objects")
    roots = [Path(root) for root in mod_roots]
    text_sources, text_rows = collect_game_text(roots)
    source_by_id = {source.source_id: source for source in text_sources}
    string_rows = [
        {
            "key": row["text_key"],
            "value": row["value_vi"],
            "source": source_by_id[row["source_id"]].path,
            "line": int(str(row["locator"]).removeprefix("line:")),
        }
        for row in text_rows
    ]
    recipes = runtime.get("recipes", [])
    if not isinstance(recipes, list):
        raise ValueError("runtime.recipes must be a list")
    output = Path(output_dir)
    _atomic_write(output / "crafting-recipes.md", render_crafting_recipes(catalog, runtime))
    _atomic_write(output / "game-text.md", render_game_text(string_rows))
    _atomic_write(output / "README.md", _render_readme(runtime, len(recipes), len(string_rows), roots))
