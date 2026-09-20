"""Copy the staff's own resources and statically decode only its particle FX."""
import shutil
from zipfile import ZipFile
from port_vanhonphien import SOURCE, DEST, decode

old, new = 'xd_yunxiao_fysz', 'thanhiquangtruong'
for source, target in [
    (f'anim/{old}.zip', f'anim/{new}.zip'),
    (f'images/inventoryimages/{old}.tex', f'images/inventoryimages/{new}.tex'),
    (f'fx/{old}fx.tex', f'fx/{new}fx.tex'),
]:
    (DEST / target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / source, DEST / target)
with ZipFile(DEST / f'anim/{new}.zip') as z:
    assert z.testzip() is None
xml = (SOURCE / f'images/inventoryimages/{old}.xml').read_text().replace(old, new)
(DEST / f'images/inventoryimages/{new}.xml').write_text(xml, encoding='utf-8', newline='\n')

source = decode(f'scripts/prefabs/{old}.lua')
fx = source[source.index('local function IntColour'):source.index('return  Prefab')]
fx = fx.replace(old, new).replace('effect:InitEmitters(6)', 'effect:InitEmitters(3)')
fx += '\nreturn Prefab("thanhiquangtruongfx", fxfn, fxassets)\n'
(DEST / f'scripts/prefabs/{new}fx.lua').write_text(
    '-- Particle visuals adapted from Tu Tien 19.7; see CREDITS.md.\n' + fx,
    encoding='utf-8', newline='\n')
print('Copied staff animation, inventory atlas/texture and particle texture; extracted isolated particle FX.')
