"""Static package validation; run from the SoloCombatHUD directory."""
from pathlib import Path
import re
import zipfile

root = Path(__file__).resolve().parents[1]
lua_files = list(root.rglob("*.lua"))
missing = []

for path in lua_files:
    text = path.read_text(encoding="utf-8")
    for rel in re.findall(r'Asset\("(?:ATLAS|IMAGE|ANIM)",\s*"([^"]+)"', text):
        if not (root / rel).exists() and not rel.startswith("anim/quagmire_hangry_bar"):
            missing.append(f"{path.relative_to(root)} -> {rel}")

for atlas in (root / "images").glob("*.xml"):
    text = atlas.read_text(encoding="utf-8")
    match = re.search(r'<Texture filename="([^"]+)"', text)
    if match and not (atlas.parent / match.group(1)).exists():
        missing.append(f"{atlas.relative_to(root)} -> {match.group(1)}")

if missing:
    raise SystemExit("Missing package assets:\n" + "\n".join(missing))

assert (root / "scripts/widgets/schud_epichealthbar.lua").exists()
assert (root / "scripts/prefabs/schud_epichealth_proxy.lua").exists()

game_zip = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data\databundles\scripts.zip")
with zipfile.ZipFile(game_zip) as archive:
    game_modules = {name.removeprefix("scripts/").removesuffix(".lua") for name in archive.namelist()
                    if name.startswith("scripts/") and name.endswith(".lua")}
local_modules = {str(path.relative_to(root / "scripts")).replace("\\", "/").removesuffix(".lua")
                 for path in (root / "scripts").rglob("*.lua")}
missing_modules = []
for path in lua_files:
    text = path.read_text(encoding="utf-8")
    for module in re.findall(r'require\s*\(?\s*["\']([^"\']+)["\']', text):
        if module not in local_modules and module not in game_modules:
            missing_modules.append(f"{path.relative_to(root)} -> require {module}")
if missing_modules:
    raise SystemExit("Missing Lua dependencies:\n" + "\n".join(missing_modules))
print(f"asset validation: {len(lua_files)} Lua files and all local asset references OK")
