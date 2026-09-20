"""Copy the audited Tu Tien 19.7 altar/chest art into Pham Nhan (or an explicit target)."""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sys


WORKSPACE = Path(__file__).resolve().parents[1]
SOURCE = WORKSPACE / "mods" / "mod_steam" / "3235319974"
DEFAULT_TARGET = WORKSPACE / "mods" / "PhamNhanTuTien"

# target path: (source path, source SHA-256)
MANIFEST = {
    "anim/ttk_jitan.zip": ("anim/xd_jitan.zip", "D2CCC37728B85AB458F24738A899478442325992228393CAD948702B2D348853"),
    "anim/ttk_llbx.zip": ("anim/xd_llbx.zip", "8CD8C1864BDDF800587BCF3E848797B410BA18A69F9CB4679A73E540A4C1C75E"),
    "anim/ttk_ui_llbx.zip": ("anim/xd_ui_llbx.zip", "2D8A5974BF352F3B3D0675A9B560898E5D3CE3E9FEEB1E625EE5862932DA9D91"),
    "images/map_icons/ttk_jitan.tex": ("images/map_icons/xd_jitan.tex", "216D667E993512E057653E0D9583952E48757AE3809328E7E101BC7B7EC975CC"),
    "images/map_icons/ttk_jitan.xml": ("images/map_icons/xd_jitan.xml", "3946FC4C7912FC5F0DCD9ACE8C1D4903FDBDA27CAD7891CC2ED9521A8B360733"),
    "images/map_icons/ttk_llbx.tex": ("images/map_icons/xd_llbx.tex", "365B314A9258FDB0B9F6F02B669207AE2D57BDBFF9EA952C4BFD78FE5B25821C"),
    "images/map_icons/ttk_llbx.xml": ("images/map_icons/xd_llbx.xml", "FB3A54941561976953D50A2F0B50C50E463E80564F34D1EDA5C883EE6681A0DC"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def port_assets(target_root: Path = DEFAULT_TARGET) -> list[str]:
    copied: list[str] = []
    for target_name, (source_name, expected_hash) in MANIFEST.items():
        source = SOURCE / source_name
        actual_hash = digest(source)
        if actual_hash != expected_hash:
            raise RuntimeError(f"Nguồn 19.7 đổi hash: {source_name}: {actual_hash}")
        target = target_root / target_name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.suffix == ".xml":
            text = source.read_text(encoding="utf-8-sig")
            text = text.replace("xd_jitan.tex", "ttk_jitan.tex").replace("xd_llbx.tex", "ttk_llbx.tex")
            target.write_text(text, encoding="utf-8", newline="")
        else:
            shutil.copyfile(source, target)
        copied.append(target_name)
    return copied


if __name__ == "__main__":
    destination = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_TARGET
    for relative in port_assets(destination):
        print(relative)

