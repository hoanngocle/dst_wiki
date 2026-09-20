"""Static validation for the batch-19 house port; never runs prefab code."""
from pathlib import Path
from zipfile import ZipFile
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "mods/mod_steam/.fasttravel-test-runtime"))
from lupa import LuaRuntime

NAMES = {
    "ttk_batch19_houses.lua", "ttk_zzxhcx.lua", "ttk_lycx.lua", "ttk_spiderden.lua",
    "ttk_pog.lua", "ttk_stool.lua", "ttk_bearger.lua", "ttk_dragonfly.lua", "ttk_spider.lua",
    "ttk_batch19_houseitems.lua", "ttk_tianjiwu.lua", "ttk_tianji_items.lua",
    "ttk_house_interior.lua", "ttk_batch19_houseutil.lua", "ttk_house_map.lua",
    "ttk_house_return.lua", "ttk_house_registry.lua", "ttk_house_teleporter.lua",
    "ttk_drangonflybrain.lua", "ttk_spiderbrain.lua", "ttk_pogbrain.lua",
    "ttk_tianji_byj.lua",
    "SGttk_bearger.lua", "SGttk_dragonfly.lua", "SGttk_spider.lua", "SGttk_pog.lua",
}

files = [p for base in (ROOT / "mods/PhamNhanTuTien/main", ROOT / "mods/PhamNhanTuTien/scripts")
         for p in base.rglob("*.lua") if p.name in NAMES]
lua = LuaRuntime(unpack_returned_tuples=True)
load = lua.eval("load")
errors = []
for path in files:
    result = load(path.read_text(encoding="utf-8"), str(path))
    if isinstance(result, tuple) and result[0] is None:
        errors.append(f"{path}: {result[1]}")

for path in (ROOT / "mods/PhamNhanTuTien/anim").glob("ttk_*.zip"):
    if any(part in path.name for part in ("tianji", "floor", "wall", "door", "futu", "pog", "spider", "zzxhcx", "lycx", "stool")):
        try:
            with ZipFile(path) as archive:
                bad = archive.testzip()
                if bad:
                    errors.append(f"{path}: bad member {bad}")
        except Exception as exc:
            errors.append(f"{path}: {exc}")

owned_text = "\n".join(path.read_text(encoding="utf-8") for path in files)
for forbidden in ("xd_ziyun_house", "xd_jwtcd", "xd_lyd", "xd_rock1", "xd_rock2", "xd_rock3", "xd_sudaji_controller", "XD_GetGroundPoints"):
    if forbidden in owned_text:
        errors.append(f"forbidden/unresolved reference: {forbidden}")

print(f"checked {len(files)} Lua files")
print("errors:", len(errors))
for error in errors:
    print(error)
raise SystemExit(1 if errors else 0)
