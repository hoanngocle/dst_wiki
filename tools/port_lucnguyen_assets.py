"""Copy Lục Nguyên Kiếm Đồng art from the local Tu Tiên 19.7 source.

Only package paths are namespaced. Embedded Klei bank/build/symbol names stay
unchanged so the original silhouettes render byte-for-byte.
"""
from pathlib import Path
from zipfile import ZipFile
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mods/mod_steam/3235319974"
DEST = ROOT / "mods/PhamNhanTuTien"

ANIMS = {
    "xd_jingwei_blowdart": "ttk_lucnguyen_weapon",
    "xd_wxj": "ttk_lucnguyen_kim",
    "xd_htz_qzj": "ttk_lucnguyen_moc",
    "xd_xlj": "ttk_lucnguyen_thuy",
    "xd_ftj": "ttk_lucnguyen_hoa",
    "xd_sword_red": "ttk_lucnguyen_tho",
    "xd_sword_mo": "ttk_lucnguyen_loi",
}

HELD_SWAP_SYMBOLS = {
    "xd_wxj": b"swap",
    "xd_htz_qzj": b"swap",
    "xd_ftj": b"png",
    # These two source swords were autonomous entities. Their build archives
    # expose `png` as the representative sword symbol rather than `swap`.
    "xd_sword_red": b"png",
    "xd_sword_mo": b"png",
}

HELD_ICONS = {
    "xd_wxj": "ttk_votuongkiem",
    "xd_htz_qzj": "ttk_thanhtrucphongvankiem",
    "xd_ftj": "ttk_phanthienkiem",
    # The autonomous red/purple swords have no inventory atlases. Their
    # original builder items are the source mod's intended inventory art.
    "xd_xianjian_builder": "ttk_tienkiem",
    "xd_mo_builder": "ttk_makiem",
}


def inspect_archive(path: Path, expected: bytes) -> None:
    with ZipFile(path) as archive:
        assert archive.testzip() is None, f"corrupt archive: {path}"
        names = set(archive.namelist())
        assert {"anim.bin", "build.bin"}.issubset(names), (path, names)
        metadata = archive.read("anim.bin") + archive.read("build.bin")
        assert expected in metadata, f"missing bank/build metadata {expected!r}: {path}"


def main() -> None:
    for source_name, dest_name in ANIMS.items():
        source = SOURCE / "anim" / f"{source_name}.zip"
        inspect_archive(source, source_name.encode("ascii"))
        if source_name in HELD_SWAP_SYMBOLS:
            with ZipFile(source) as archive:
                assert HELD_SWAP_SYMBOLS[source_name] in archive.read("build.bin"), (
                    source_name,
                    HELD_SWAP_SYMBOLS[source_name],
                )
        target = DEST / "anim" / f"{dest_name}.zip"
        shutil.copyfile(source, target)
        inspect_archive(target, source_name.encode("ascii"))

    source_icon = SOURCE / "images/inventoryimages/xd_jingwei_blowdart.tex"
    target_icon = DEST / "images/inventoryimages/ttk_lucnguyenkiemdong.tex"
    shutil.copyfile(source_icon, target_icon)
    source_xml = (SOURCE / "images/inventoryimages/xd_jingwei_blowdart.xml").read_text(
        encoding="utf-8"
    )
    assert 'name="xd_jingwei_blowdart.tex"' in source_xml
    target_xml = source_xml.replace(
        'name="xd_jingwei_blowdart.tex"',
        'name="ttk_lucnguyenkiemdong.tex"',
    )
    (DEST / "images/inventoryimages/ttk_lucnguyenkiemdong.xml").write_text(
        target_xml, encoding="utf-8"
    )
    for source_name, dest_name in HELD_ICONS.items():
        source_tex = SOURCE / "images/inventoryimages" / f"{source_name}.tex"
        target_tex = DEST / "images/inventoryimages" / f"{dest_name}.tex"
        shutil.copyfile(source_tex, target_tex)
        source_xml = (SOURCE / "images/inventoryimages" / f"{source_name}.xml").read_text(
            encoding="utf-8"
        )
        assert f'name="{source_name}.tex"' in source_xml
        (DEST / "images/inventoryimages" / f"{dest_name}.xml").write_text(
            source_xml.replace(f'name="{source_name}.tex"', f'name="{dest_name}.tex"'),
            encoding="utf-8",
        )
    print("Copied and inspected 7 animation archives plus 6 inventory atlases.")


if __name__ == "__main__":
    main()
