"""Static asset/code extraction for the Tu Tien Ky batch-19 houses.

The source loader is never executed.  Lua is decoded with the established
byte map, namespaced, and then reviewed/patched in the destination.
"""
from pathlib import Path
import re
import shutil

import port_ttk_buildings as base


SOURCE = base.SOURCE
DEST = base.DEST
base.source.MAPPING[0x03] = ord("%")


LUA_PORTS = {
    "scripts/prefabs/xd_zzxhcx.lua": "scripts/prefabs/ttk_zzxhcx.lua",
    "scripts/prefabs/xd_lycx.lua": "scripts/prefabs/ttk_lycx.lua",
    "scripts/prefabs/xd_spiderden.lua": "scripts/prefabs/ttk_spiderden.lua",
    "scripts/prefabs/xd_pog.lua": "scripts/prefabs/ttk_pog.lua",
    "scripts/prefabs/xd_bearger.lua": "scripts/prefabs/ttk_bearger.lua",
    "scripts/prefabs/xd_dragonfly.lua": "scripts/prefabs/ttk_dragonfly.lua",
    "scripts/prefabs/xd_spider.lua": "scripts/prefabs/ttk_spider.lua",
    "scripts/prefabs/xd_chairs.lua": "scripts/prefabs/ttk_stool.lua",
    "scripts/brains/xd_drangonflybrain.lua": "scripts/brains/ttk_drangonflybrain.lua",
    "scripts/brains/xd_spiderbrain.lua": "scripts/brains/ttk_spiderbrain.lua",
    "scripts/brains/xd_pogbrain.lua": "scripts/brains/ttk_pogbrain.lua",
    "scripts/stategraphs/SGxd_bearger.lua": "scripts/stategraphs/SGttk_bearger.lua",
    "scripts/stategraphs/SGxd_dragonfly.lua": "scripts/stategraphs/SGttk_dragonfly.lua",
    "scripts/stategraphs/SGxd_spider.lua": "scripts/stategraphs/SGttk_spider.lua",
    "scripts/stategraphs/SGxd_pog.lua": "scripts/stategraphs/SGttk_pog.lua",
}

ANIMS = (
    "zzxhcx", "lycx", "spiderden", "pog_house", "stool",
    "pog_basic", "pog_actions", "pog", "pog_fire", "pog_firefire",
    "pog_tail", "spider", "spider_pro", "slow_buff_ent", "spider_puff",
    "spider_leg", "npxsz",
    "tianjiwu_skins_byj", "floortjw_byj", "walltjw_byj",
    "wall_decals_tjw_byj", "door_exittjw_byj", "door_exittjw_heng_byj", "futu",
)

ICONS = {
    "images/inventoryimages": (
        "zzxhcx", "lycx", "pog_house", "stool", "pog_tail", "spider_leg", "npxsz",
        "tianjiwu_skins_byj",
    ),
    "images/map_icons": ("zzxhcx", "lycx", "spiderden", "pog_house"),
}


def write(relative: str, text: str) -> None:
    path = DEST / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def namespace_lua(text: str) -> str:
    text = text.replace("xd_", "ttk_")
    text = text.replace("XD_SHUOHUO", "TTK_HARVEST_HOUSE")
    text = text.replace("XD_EMPTY_CATCOONDEN", "TTK_EMPTY_HOUSE")
    text = text.replace("XD_CanAttackTrget", "TTK_CanAttackTarget")
    text = text.replace("XD_GetDamageTargets", "TTK_GetDamageTargets")
    text = text.replace("XD_RECORDCOMBAT(inst)", "")
    # The physical archive is namespaced; Spriter banks/builds inside it retain
    # the source name and therefore must not be renamed.
    text = re.sub(
        r'(SetBank|SetBuild|AddOverrideBuild)\("ttk_([^\"]+)"\)',
        r'\1("xd_\2")', text,
    )
    text = re.sub(
        r'MakePlacer\("ttk_([^\"]+)_placer", "ttk_([^\"]+)", "ttk_([^\"]+)"',
        r'MakePlacer("ttk_\1_placer", "xd_\2", "xd_\3"', text,
    )
    text = text.replace("ttk_pog_sound/ttk_pog_sound/", "xd_pog_sound/xd_pog_sound/")
    return text


def copy_lua() -> None:
    for source, dest in LUA_PORTS.items():
        write(dest, namespace_lua(base.read(source)))


def copy_assets() -> None:
    for name in ANIMS:
        source = SOURCE / f"anim/xd_{name}.zip"
        if not source.exists():
            raise FileNotFoundError(source)
        target = DEST / f"anim/ttk_{name}.zip"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    for folder, names in ICONS.items():
        for name in names:
            source_xml = SOURCE / folder / f"xd_{name}.xml"
            source_tex = source_xml.with_suffix(".tex")
            write(f"{folder}/ttk_{name}.xml", source_xml.read_text().replace(f"xd_{name}", f"ttk_{name}"))
            shutil.copyfile(source_tex, DEST / folder / f"ttk_{name}.tex")

    for extension in ("fev", "fsb"):
        source = SOURCE / f"sound/xd_pog_sound.{extension}"
        if source.exists():
            target = DEST / f"sound/ttk_pog_sound.{extension}"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

    # The source has a map icon but no recipe icon for this den.
    map_xml = DEST / "images/map_icons/ttk_spiderden.xml"
    map_tex = map_xml.with_suffix(".tex")
    write("images/inventoryimages/ttk_spiderden.xml", map_xml.read_text())
    shutil.copyfile(map_tex, DEST / "images/inventoryimages/ttk_spiderden.tex")


if __name__ == "__main__":
    copy_lua()
    copy_assets()
    print("Ported five standalone houses, creatures, stategraphs, effects, and item art.")
