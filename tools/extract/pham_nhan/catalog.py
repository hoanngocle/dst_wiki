from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path

from .recipes import normalize_recipes


_EXCLUDED = re.compile(r"(?:_placer$|_fx$|^fx_|^hh_fx$|_projectile$|_shadow$|^ttk_boss|^hh_boss|^dungeon_|_brain$|_controller$)")


def _evidence(root: Path, relative: str, locator: str) -> dict:
    return {"path": relative, "locator": locator, "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(), "kind": "runtime"}


def _category(prefab: str) -> str:
    if "skin" in prefab:
        return "skin"
    if prefab.endswith(("_blueprint", "_token", "_tally")) or prefab in {"nkGem", "wb_enhancegem"}:
        return "blueprint-token"
    if any(word in prefab for word in ("seed", "huazhong", "huayin")):
        return "seed"
    if any(word in prefab for word in ("food", "luoshen", "pengrou", "qingshu", "drug", "potion")):
        return "food"
    if any(word in prefab for word in ("armor", "hat", "sword", "scythe", "weapon", "jian", "staff", "amulet")):
        return "equipment"
    if any(word in prefab for word in ("pond", "garden", "house", "jitan", "portal", "building", "lo_ren")):
        return "structure"
    return "material"


def _active_prefabs(root: Path, registrations: dict) -> tuple[dict[str, dict], list[dict]]:
    candidates: dict[str, dict] = {}
    excluded: list[dict] = []
    sources = set(registrations["loadedSources"])
    # Prefab providers explicitly listed by an active module are active.  Their
    # constructor files may otherwise not be reachable through Lua require().
    loaded_text = "\n".join((root / relative).read_text(encoding="utf-8", errors="replace") for relative in sources)
    provider_names = set(re.findall(r"(?:PrefabFiles\s*=\s*\{|table\.insert\s*\(\s*PrefabFiles\s*,)\s*['\"]([\w_]+)", loaded_text))
    for relative in sorted(sources):
        source = (root / relative).read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\bPrefab\s*\(\s*['\"]([\w_]+)['\"]", source):
            prefab = match.group(1)
            if _EXCLUDED.search(prefab):
                excluded.append({"prefab": prefab, "reason": "runtime helper or creature", "evidence": [_evidence(root, relative, f"Prefab@{match.start()}")]})
            else:
                candidates.setdefault(prefab, {"evidence": [_evidence(root, relative, f"Prefab@{match.start()}")]})
    for name in provider_names:
        provider = root / "scripts" / "prefabs" / f"{name}.lua"
        if not provider.is_file():
            continue
        relative = provider.relative_to(root).as_posix()
        source = provider.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\b(?:Prefab|MakePlacer)\s*\(\s*['\"]([\w_]+)['\"]", source):
            prefab = match.group(1)
            if _EXCLUDED.search(prefab):
                excluded.append({"prefab": prefab, "reason": "runtime helper or creature", "evidence": [_evidence(root, relative, f"Prefab@{match.start()}")]})
            else:
                candidates.setdefault(prefab, {"evidence": [_evidence(root, relative, f"Prefab@{match.start()}")]})
    # Active item/enchant tables and prize definitions contain legitimate
    # inventory identities that do not always own a standalone constructor.
    for relative in ("scripts/enums/hh_items.lua", "scripts/ttk_slot_prizes.lua", "main/ttk_eva_source.lua"):
        path = root / relative
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\[?['\"]([A-Za-z][\w_]+)['\"]\]?\s*=|\b(?:goods|gear)\s*\(\s*['\"]([\w_]+)['\"]", source):
            prefab = next(value for value in match.groups() if value)
            if not _EXCLUDED.search(prefab):
                candidates.setdefault(prefab, {"evidence": [_evidence(root, relative, f"item@{match.start()}")]})
    return candidates, excluded


def _cooking(root: Path) -> list[dict]:
    path = root / "scripts" / "ttk_luoshen_fooddefs.lua"
    if not path.is_file():
        return []
    source = path.read_text(encoding="utf-8", errors="replace")
    results: list[dict] = []
    for match in re.finditer(r"\b(ttk_luo(?:shen|xiang)_[\w_]+)\s*=\s*\{(.*?)(?=\n\s*}\s*,|\n}\s*$)", source, re.DOTALL):
        prefab, body = match.groups()
        condition = "có Lạc Thần Hoa Nhân và không có thịt" if "not tags.meat" in body else "có Lạc Thần Hoa Nhân và thịt > 0"
        results.append({"id": f"cooking:{prefab}", "kind": "cooking", "product": prefab, "amount": 1,
                        "ingredients": [], "station": "Nồi nấu", "conditions": [condition],
                        "evidence": [_evidence(root, "scripts/ttk_luoshen_fooddefs.lua", f"{prefab} test")]})
    return results


def _fusion(root: Path) -> list[dict]:
    relative = "main/ttk_solo_source.lua"
    path = root / relative
    if not path.is_file():
        return []
    source = path.read_text(encoding="utf-8", errors="replace")
    results = []
    pattern = re.compile(r'Has\("([\w_]+)",\s*(\d+)\)\s+and\s+[^\n]*Has\("([\w_]+)",\s*(\d+)\).*?SpawnPrefab"\]\("([\w_]+)"', re.DOTALL)
    for match in pattern.finditer(source):
        left, left_amount, right, right_amount, product = match.groups()
        if product not in {"nn_liquidluck_2", "nn_liquidluck_3"}:
            continue
        results.append({"id": f"fusion:{product}", "kind": "fusion", "product": product, "amount": 1,
                        "ingredients": [{"prefab": left, "amount": int(left_amount)}, {"prefab": right, "amount": int(right_amount)}],
                        "station": "Bảng Tổng Hợp", "conditions": [], "evidence": [_evidence(root, relative, f"fusion {product}")]})
    return results


def build_catalog(mod_root: Path, registrations: dict) -> tuple[list[dict], dict]:
    root = mod_root.resolve()
    recipes = normalize_recipes(registrations) + _cooking(root) + _fusion(root)
    by_product: dict[str, list[dict]] = defaultdict(list)
    for recipe in recipes:
        by_product[recipe["product"]].append(recipe)
    candidates, excluded = _active_prefabs(root, registrations)
    for recipe in recipes:
        candidates.setdefault(recipe["product"], {"evidence": recipe["evidence"]})
    # Mod-altered vanilla and known shop/drop identities have source evidence.
    for prefab in ("yellowgem", "ttk_xshj_blueprint", "eva_scythe", "nkGem"):
        candidates.setdefault(prefab, {"evidence": [_evidence(root, "main/ttk_solo_source.lua" if prefab == "eva_scythe" else "scripts/enums/hh_items.lua", f"active identity {prefab}")]})
    items: list[dict] = []
    for prefab, facts in sorted(candidates.items()):
        if _EXCLUDED.search(prefab):
            continue
        own_recipes = by_product.get(prefab, [])
        items.append({"id": f"item:{prefab}", "prefab": prefab, "name": registrations["names"].get(prefab, prefab.replace("_", " ").title()),
                      "sprite": None, "category": _category(prefab), "description": registrations["descriptions"].get(prefab, "Thông tin lấy từ source Phàm Nhân hiện hành."),
                      "details": [], "recipeStatus": "known" if own_recipes else "none", "recipes": own_recipes,
                      "acquisition": [], "relatedIds": [], "evidence": facts["evidence"]})
    coverage = {"candidates": len(candidates), "included": len(items), "excluded": excluded, "unresolved": [],
                "recipes": {"total": len(recipes), "byKind": {kind: sum(recipe["kind"] == kind for recipe in recipes) for kind in sorted({recipe["kind"] for recipe in recipes})}}}
    return items, coverage
