"""Statically port source Zuichunyan trees/saplings; never run source loaders."""
import re
import shutil
import port_phamnhan_boss_combat as source

DEST=source.DEST

def tree_code():
    t=source.read('scripts/prefabs/xd_zuichunyan.lua')
    t=t.replace('xd_zuichunyan','ttk_zuichunyan').replace('"xd_zcyseed"','"ttk_boss_zcyseed"')
    t=t.replace('anim/ttk_zuichunyan','anim/xd_zuichunyan')
    t=re.sub(r'(file\s*=\s*"|file_bank\s*=\s*")ttk_',r'\1xd_',t)
    t=re.sub(r'"ttk_zuichunyan_(green|purple)_leaves_(fall|chop)"',r'"ttk_boss_zuichunyan_\1_leaves_\2"',t)
    t=t.replace('    "small_puff",','''    "small_puff", "ttk_boss_zcyseed",
    "ttk_boss_zuichunyan_green_leaves_fall", "ttk_boss_zuichunyan_green_leaves_chop",
    "ttk_boss_zuichunyan_purple_leaves_fall", "ttk_boss_zuichunyan_purple_leaves_chop",''')
    return '-- Tree lifecycle and harvest ported from Tu Tien 19.7 by tools/port_phamnhan_seed_tree.py.\n'+t

def sapling_code():
    t=source.read('scripts/prefabs/xd_planted_tree.lua').replace('xd_zuichunyan','ttk_zuichunyan')
    t=t.replace('anim/ttk_zuichunyan','anim/xd_zuichunyan')
    t=t.replace('Asset("ANIM", "anim/xd_zuichunyan_green.zip"),','Asset("ANIM", "anim/xd_zuichunyan_green.zip"),\n    Asset("ANIM", "anim/xd_zuichunyan_purple.zip"),')
    t=t.replace('sapling_fn("ttk_zuichunyan','sapling_fn("xd_zuichunyan')
    t=t.replace('"ttk_zuichunyan_green"))','"xd_zuichunyan_green"))')
    lines=t.splitlines()
    for i,line in enumerate(lines):
        if line.strip().startswith('Prefab('):
            # Source omitted the asset list; explicitly preload both builds.
            suffix=',' if line.endswith(',') else ''
            lines[i]=line.rstrip(',')[:-1]+', pinecone_assets, {"ttk_zuichunyan_green_short", "ttk_zuichunyan_purple_short"})'+suffix
    return '-- Source sapling growth: 960 seconds, timer persists across saves.\n'+'\n'.join(lines)+'\n'

def main():
    for name,code in [('ttk_zuichunyan',tree_code()),('ttk_zuichunyan_saplings',sapling_code())]:
        source.write('scripts/prefabs/'+name+'.lua',code)
    for colour in ['green','purple']:
        asset='anim/xd_zuichunyan_'+colour+'.zip'
        shutil.copyfile(source.SOURCE/asset,DEST/asset)
    for variant in ['green','purple','stump','burnt']:
        original='xd_zuichunyan_'+variant;target='ttk_zuichunyan_'+variant
        folder=DEST/'images/map_icons';folder.mkdir(exist_ok=True)
        shutil.copyfile(source.SOURCE/'images/map_icons'/(original+'.tex'),folder/(target+'.tex'))
        (folder/(target+'.xml')).write_text((source.SOURCE/'images/map_icons'/(original+'.xml')).read_text().replace(original,target))
    print('Ported source trees, saplings, two animation builds and four minimap icons.')

if __name__=='__main__':main()
