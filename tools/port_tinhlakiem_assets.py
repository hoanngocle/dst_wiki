"""Copy original Tu Tien 19.7 sword assets, preserving embedded bank/build."""
from pathlib import Path
import shutil
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'mods/mod_steam/3235319974'
DST=ROOT/'mods/PhamNhanTuTien'
with ZipFile(SRC/'anim/xd_xlj.zip') as archive:
    assert archive.testzip() is None
shutil.copyfile(SRC/'anim/xd_xlj.zip',DST/'anim/ttk_tinhlakiem.zip')
shutil.copyfile(SRC/'images/inventoryimages/xd_xlj.tex',DST/'images/inventoryimages/ttk_tinhlakiem.tex')
text=(SRC/'images/inventoryimages/xd_xlj.xml').read_text()
(DST/'images/inventoryimages/ttk_tinhlakiem.xml').write_text(text.replace('xd_xlj','ttk_tinhlakiem'),encoding='utf-8')
print('Copied original sword animation and icon.')
