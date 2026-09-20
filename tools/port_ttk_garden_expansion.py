"""Copy the four selected garden assets and adapt two source prefabs statically."""
import sys
import shutil
from zipfile import ZipFile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import port_ttk_buildings as source

def main():
    for suffix in ('yhsyz', 'hyc', 'hmsw'):
        src = source.SOURCE/f'anim/xd_{suffix}.zip'
        with ZipFile(src) as z:
            assert z.testzip() is None
        shutil.copyfile(src, source.DEST/f'anim/ttk_{suffix}.zip')
    for suffix in ('yhsyz', 'hyc', 'tree_xhs', 'hmsw'):
        for folder in ('images/inventoryimages', 'images/map_icons'):
            if suffix == 'yhsyz' and folder.endswith('map_icons'):
                continue
            xml = source.SOURCE/f'{folder}/xd_{suffix}.xml'
            assert xml.exists(), xml
            (source.DEST/f'{folder}/ttk_{suffix}.xml').write_text(
                xml.read_text().replace('xd_'+suffix, 'ttk_'+suffix), encoding='utf-8')
            shutil.copyfile(xml.with_suffix('.tex'), source.DEST/f'{folder}/ttk_{suffix}.tex')

    t = source.read('scripts/prefabs/xd_yhsyz.lua')
    t = t.replace('xd_yhsyz', 'ttk_yhsyz')
    t = t.replace('SetBank("ttk_yhsyz")', 'SetBank("xd_yhsyz")').replace('SetBuild("ttk_yhsyz")', 'SetBuild("xd_yhsyz")')
    t = t.replace('skin_build or "ttk_yhsyz"', 'skin_build or "xd_yhsyz"')
    t = t.replace('inst:AddTag("ttk_yhsyz")', 'inst:AddTag("ttk_herbtool")')
    t = t.replace('    inst:AddComponent("xd_pick_plant")', '    -- Mature TTK herbs consume one use through their standard PICK callback.')
    (source.DEST/'scripts/prefabs/ttk_yhsyz.lua').write_text(t, encoding='utf-8')

    t = source.read('scripts/prefabs/xd_hmsw.lua').replace('xd_hmsw', 'ttk_hmsw')
    t = t.replace('SetBank("ttk_hmsw")', 'SetBank("xd_hmsw")').replace('SetBuild("ttk_hmsw")', 'SetBuild("xd_hmsw")')
    t = t.replace('"ttk_hmsw_placer", "ttk_hmsw", "ttk_hmsw"', '"ttk_hmsw_placer", "xd_hmsw", "xd_hmsw"')
    t = t.replace('"XD_SHUOHUO"', '"TTK_CAT_GIFTS"')
    t = t.replace('    inst.entity:SetPristine()', '    inst:AddTag("structure")\n    inst.entity:SetPristine()')
    t = t.replace('local prefabs = {', 'local prefabs = {"catcoon", "collapse_small",')
    (source.DEST/'scripts/prefabs/ttk_hmsw.lua').write_text(t, encoding='utf-8')
    print('Copied four item icon sets, three animations and two standalone prefabs; reused ttk_trees animation.')

if __name__ == '__main__':
    main()
