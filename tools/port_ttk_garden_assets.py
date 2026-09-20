"""Copy only resources for the requested garden items; no release ZIP."""
from pathlib import Path
from zipfile import ZipFile
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'mods/mod_steam/3235319974'
DEST = ROOT / 'mods/PhamNhanTuTien'
ANIMS = {
    'xd_trees': 'ttk_trees', 'xd_flowers': 'ttk_flowers',
    'xd_gj': 'ttk_gj', 'xd_huapen': 'ttk_huapen',
    'xd_tree_ls': 'ttk_tree_ls',
    'xd_luoshen_hua': 'ttk_luoshen_hua',
    'xd_luoshen_huazhong': 'ttk_luoshen_huazhong',
    'xd_luoshen_huayin': 'ttk_luoshen_huayin',
    'xd_lbx': 'ttk_lbx', 'xd_lgzbh': 'ttk_lgzbh', 'xd_mg': 'ttk_mg',
    'xd_lunar_fx': 'ttk_lunar_fx',
    'xd_sj_kls': 'ttk_sj_kls', 'xd_lbjlt': 'ttk_lbjlt',
    'xd_ui_4x5': 'ttk_ui_4x5',
}
ICONS = {
    'xd_tree_yhs': 'ttk_tree_yhs', 'xd_tree_ls': 'ttk_tree_ls',
    'xd_tree_yxs': 'ttk_tree_yxs',
    'xd_flower_bh': 'ttk_flower_bh', 'xd_flower_bmg': 'ttk_flower_bmg',
    'xd_flower_pgy': 'ttk_flower_pgy', 'xd_flower_ll': 'ttk_flower_ll',
    'xd_flower_md': 'ttk_flower_md', 'xd_flower_mlh': 'ttk_flower_mlh',
    'xd_gj': 'ttk_gj', 'xd_huapen': 'ttk_huapen',
    'xd_luoshen_hua': 'ttk_luoshen_hua',
    'xd_luoshen_huazhong': 'ttk_luoshen_huazhong',
    'xd_luoshen_huayin': 'ttk_luoshen_huayin',
    'xd_lbx': 'ttk_lbx', 'xd_lgzbh': 'ttk_lgzbh', 'xd_mg': 'ttk_mg',
    'xd_sj_kls': 'ttk_sj_kls', 'xd_lbjlt': 'ttk_lbjlt',
}

for old, new in ANIMS.items():
    source = SOURCE / f'anim/{old}.zip'
    with ZipFile(source) as z:
        assert z.testzip() is None
    (DEST / 'anim').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, DEST / f'anim/{new}.zip')

for old, new in ICONS.items():
    for folder in ['images/inventoryimages', 'images/map_icons']:
        source = SOURCE / folder / (old + '.xml')
        if not source.exists():
            continue
        target = DEST / folder
        target.mkdir(parents=True, exist_ok=True)
        xml = source.read_text(encoding='utf-8').replace(old, new)
        (target / (new + '.xml')).write_text(xml, encoding='utf-8', newline='\n')
        shutil.copyfile(source.with_suffix('.tex'), target / (new + '.tex'))
print(f'Copied {len(ANIMS)} original animation archives and available inventory/map icons; embedded banks unchanged.')
