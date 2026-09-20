"""Reproducible resources and direct source ports for batch 19 miscellaneous items."""
from pathlib import Path
import re, shutil, json
from zipfile import ZipFile
import port_ttk_buildings as src

ROOT, SOURCE, DEST = src.ROOT, src.SOURCE, src.DEST
IDS = ['qljq','sgc','qwsk','flower_sfr','flower_zyh','crc','flower_yl',
       'yunxiao_portable_spicer','wsjx','tree_yls']

def write(path,text):
    p=DEST/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

def renamed(t):
    for old in IDS+['yunxiao_portableslot']:
        t=t.replace('xd_'+old,'ttk_'+old)
    # Embedded source banks/builds stay unchanged.
    t=re.sub(r'(SetBank|SetBuild)\("ttk_([^\"]+)"\)',r'\1("xd_\2")',t)
    return t

def main():
    for name in ['qljq','sgc','qwsk','crc','yunxiao_portable_spicer','wsjx','ui_4x5','ui_6x6']:
        p=SOURCE/f'anim/xd_{name}.zip'
        with ZipFile(p) as z:assert z.testzip() is None
        shutil.copyfile(p,DEST/f'anim/ttk_{name}.zip')
    for name in IDS+['yunxiao_portableslot']:
        for folder in ['images/inventoryimages','images/map_icons']:
            p=SOURCE/folder/f'xd_{name}.xml'
            if not p.exists():
                assert folder.endswith('map_icons'),str(p)
                continue
            write(f'{folder}/ttk_{name}.xml',p.read_text().replace('xd_'+name,'ttk_'+name))
            shutil.copyfile(p.with_suffix('.tex'),DEST/folder/f'ttk_{name}.tex')

    t=src.read('scripts/prefabs/xd_cangku.lua')
    t=t.replace('XD_MORESTACK(inst)','require("ttk_chestupgrade")(inst)')
    t=renamed(t).replace('anim/xd_ui_6x6.zip','anim/ttk_ui_6x6.zip')
    t=t.replace('SetBank(name)','SetBank(string.gsub(name, "^ttk_", "xd_"))').replace('SetBuild(name)','SetBuild(string.gsub(name, "^ttk_", "xd_"))')
    t=t.replace('MakePlacer(v.."_placer", v, v, "idle")','MakePlacer(v.."_placer", string.gsub(v, "^ttk_", "xd_"), string.gsub(v, "^ttk_", "xd_"), "idle")')
    t=t.replace('"collapse_small",','"collapse_small", "collapsed_treasurechest", "chestupgrade_stacksize_fx",')
    write('scripts/prefabs/ttk_foodstores.lua',t)

    t=renamed(src.read('scripts/prefabs/xd_wsjx.lua'))
    t=t.replace('anim/xd_ui_3x5.zip','anim/ttk_ui_4x5.zip').replace('"xd_storeitem"','"ttk_weaponstore"')
    t=t.replace('"ttk_wsjx_placer", "ttk_wsjx", "ttk_wsjx"','"ttk_wsjx_placer", "xd_wsjx", "xd_wsjx"')
    t=t.replace('local prefabs = {','local prefabs = { "collapse_small", "sand_puff",')
    t=t.replace('inst.MiniMapEntity:SetIcon("ttk_wsjx.tex")', 'inst.MiniMapEntity:SetIcon("ttk_wsjx.tex")\n    inst:AddTag("structure")')
    write('scripts/prefabs/ttk_wsjx.lua',t)

    items=json.loads((ROOT/'public/data/items.json').read_text(encoding='utf-8'))['items']
    metadata = ROOT/'tools/ttk_batch19_misc.json'
    previous = {r['id']: r for r in json.loads(metadata.read_text(encoding='utf-8'))} if metadata.exists() else {}
    records=[]
    for name in IDS:
        e=next(e for e in items if e['prefabId']=='xd_'+name)
        recipes=[]
        if e.get('recipe'):
            for i in e['recipe']['ingredients']:
                code=i['id'].split(':')[-1].replace('xd_lingshi','ttk_lingshi')
                recipes.append([code,i['amount']])
        record = previous.get('ttk_'+name, {}).copy()
        record.update(id='ttk_'+name,name=e['name'],source='xd_'+name,recipe=recipes)
        records.append(record)
    (ROOT/'tools/ttk_batch19_misc.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Ported resources, food stores, weapon chest and recipe metadata for 10 items.')

if __name__=='__main__':main()
