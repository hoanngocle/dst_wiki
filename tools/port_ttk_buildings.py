"""Static port of selected Tu Tien structures and livestock. Never runs its loader."""
from pathlib import Path
import re
import shutil
from zipfile import ZipFile
import port_vanhonphien as source

ROOT, SOURCE, DEST = source.ROOT, source.SOURCE, source.DEST
source.MAPPING.update({0x89: 39, 0xEA: 74, 0x9B: 57, 0x13: 35, 0x51: 94})

def read(path):
    raw = (SOURCE / path).read_bytes()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = source.decode(path)
    text = re.sub(r'--\[\[.*?\]\]', '', text, flags=re.S)
    text = re.sub(r'--[^\n]*', '', text)
    assert not re.search(r'<[0-9A-F]{2}>', text), path
    return text

def write(path, text):
    target = DEST / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8', newline='\n')

ANIMS = ['pflnw', 'ftys', 'klxw', 'gjx', 'dbg', 'dc', 'ui_6x6', 'ui_1x1',
         'beefalo_antler', 'lightning_goat', 'koalefant']
ICONS = ['pflnw', 'ftys', 'klxw', 'gjx', 'dbg', 'dc', 'tree_df']

def main():
    for suffix in ANIMS:
        src = SOURCE / f'anim/xd_{suffix}.zip'
        with ZipFile(src) as archive:
            assert archive.testzip() is None
        shutil.copyfile(src, DEST / f'anim/ttk_{suffix}.zip')
    for suffix in ICONS:
        for folder in ['images/inventoryimages', 'images/map_icons']:
            src = SOURCE / folder / f'xd_{suffix}.xml'
            assert src.exists(), src
            write(f'{folder}/ttk_{suffix}.xml', src.read_text().replace('xd_'+suffix, 'ttk_'+suffix))
            shutil.copyfile(src.with_suffix('.tex'), DEST / folder / f'ttk_{suffix}.tex')

    animals = ['beefalo', 'lightninggoat', 'koalefant']
    for suffix in ['pflnw', 'ftys', 'klxw'] + animals:
        text = read(f'scripts/prefabs/xd_{suffix}.lua')
        for name in ['beefalobrain'] + animals + ['pflnw', 'ftys', 'klxw']:
            text = text.replace('xd_'+name, 'ttk_'+name)
        # Archive filenames are private; embedded art banks/builds stay original.
        text = re.sub(r'(SetBank|SetBuild|AddOverrideBuild)\("ttk_([^\"]+)"\)',
                      r'\1("xd_\2")', text)
        text = re.sub(r'MakePlacer\("ttk_(\w+)_placer", "ttk_\1", "ttk_\1"',
                      r'MakePlacer("ttk_\1_placer", "xd_\1", "xd_\1"', text)
        text = text.replace('anim/xd_lightning_goat.zip', 'anim/ttk_lightning_goat.zip')
        text = text.replace('XD_SHUOHUO', 'TTK_HARVEST_HOUSE').replace('XD_EMPTY_CATCOONDEN', 'TTK_EMPTY_HOUSE')
        if suffix in ['pflnw', 'ftys', 'klxw']:
            child = {'pflnw':'beefalo','ftys':'lightninggoat','klxw':'koalefant'}[suffix]
            products = {'pflnw':['beefalowool','horn'], 'ftys':['goatmilk','lightninggoathorn'],
                        'klxw':['trunk_summer','trunk_winter']}[suffix]
            dependencies = ['ttk_'+child, 'collapse_small'] + products
            text = text.replace('local prefabs = {', 'local prefabs = { '+', '.join('"'+name+'"' for name in dependencies)+',')
            text = text.replace('inst.entity:SetPristine()', 'inst:AddTag("structure")\n    inst.entity:SetPristine()')
            text = text.replace('inst.components.childspawner:ReleaseAllChildren()', '''local spawner = inst.components.childspawner
        local old_can_spawn = spawner.canspawnfn
        spawner.canspawnfn = nil -- demolition must also release livestock at night
        spawner:ReleaseAllChildren()
        spawner.canspawnfn = old_can_spawn
        if spawner.childreninside > 0 then
            -- No valid exit: keep the house and remaining animals for another try.
            inst.components.workable:SetWorkLeft(1)
            return
        end''')
        if suffix == 'koalefant':
            text = text.replace('"beefalo_body"', '"koalefant_body"')
        write(f'scripts/prefabs/ttk_{suffix}.lua', text)
    for animal in animals:
        text = read(f'scripts/stategraphs/SGxd_{animal}.lua').replace('xd_'+animal, 'ttk_'+animal)
        write(f'scripts/stategraphs/SGttk_{animal}.lua', text)
    text = read('scripts/brains/xd_beefalobrain.lua')
    text = 'require "behaviours/runaway"\nrequire "behaviours/doaction"\n' + text
    write('scripts/brains/ttk_beefalobrain.lua', text)

    for suffix in ['gjx','dbg']:
        text = read(f'scripts/prefabs/xd_{suffix}.lua')
        text = text.replace('xd_'+suffix, 'ttk_'+suffix)
        text = text.replace('SetBank("ttk_'+suffix+'")','SetBank("xd_'+suffix+'")')
        text = text.replace('SetBuild("ttk_'+suffix+'")','SetBuild("xd_'+suffix+'")')
        text = text.replace(f'"ttk_{suffix}_placer", "ttk_{suffix}", "ttk_{suffix}"',
                            f'"ttk_{suffix}_placer", "xd_{suffix}", "xd_{suffix}"')
        text = re.sub(r'anim/xd_ui_[^\"]+\.zip', 'anim/ttk_ui_6x6.zip', text)
        text = text.replace('XD_MORESTACK(inst)', 'require("ttk_chestupgrade")(inst)')
        text = text.replace('"xd_storeitem"', '"ttk_storeitem"')
        text = text.replace('inst.entity:SetPristine()', 'inst:AddTag("structure")\n    inst.entity:SetPristine()')
        if suffix == 'dbg':
            start, end = text.index('local function timerdone'), text.index('local function fn()')
            text = text[:start] + text[end:]
            text = text.replace('    inst:ListenForEvent("timerdone", timerdone)', '')
            text = text.replace('local function fn()', '''local function RefreshDecor(inst)
    for slot = 1, 8 do
        inst.AnimState:ClearOverrideSymbol("slot_" .. slot)
        local item = inst.components.container:GetItemInSlot(slot)
        if item ~= nil then AddDecor(inst, {slot = slot, item = item}) end
    end
end

local function fn()''')
            text = text.replace('    MakeSnowCovered(inst)', '''    inst.OnLoadPostPass = RefreshDecor
    inst:ListenForEvent("restoredfromcollapsed", RefreshDecor)
    MakeSnowCovered(inst)''')
        text = text.replace('local prefabs = {', 'local prefabs = { "collapse_small", "sand_puff", "collapsed_treasurechest", "chestupgrade_stacksize_fx",')
        write(f'scripts/prefabs/ttk_{suffix}.lua', text)
    text = read('scripts/components/xd_storeitem.lua')
    a, b = text.index('local function CanStoreItem'), text.index('local function pickup')
    text = text[:a] + '''local function CanStoreItem(inst, item)
    local permission = item.components.playerserver_permission
    return not HasPersonalOwner(item) and not (permission and permission.owner)
end

''' + text[b:]
    text = text.replace('xd_storeitem', 'ttk_storeitem')
    write('scripts/components/ttk_storeitem.lua', text)
    print('Ported livestock, housing, storage, and 11 animation archives; no release ZIP.')

if __name__ == '__main__':
    main()
