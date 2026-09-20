"""Port the requested lantern and its base assets; preserve original animation banks."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'mods/mod_steam/3721846643'
DST = ROOT / 'mods/PhamNhanTuTien'
old, new = 'xd_sudaji_redlantern', 'ttk_ngulongdang'
source = ROOT / 'mods/eva-assets-work/skill-audit/decoded/scripts/prefabs/xd_sudaji_redlantern.lua'
code = source.read_text(encoding='utf-8')
code = '\n'.join(line for line in code.splitlines() if '_zyx' not in line) + '\n'
code = code.replace(old, new)
# Archive filenames are namespaced; the embedded original bank/build is unchanged.
code = code.replace(f'SetBank("{new}")', f'SetBank("{old}")')
code = code.replace(f'SetBuild("{new}")', f'SetBuild("{old}")')
code = code.replace(f'or "{new}"', f'or "{old}"')
code = code.replace('FUELTYPE.SUDAJI_SOUL --no associated fuel, and not burnable fuel, since we want this item to be lit on fire', '"TTK_NGULONGDANG"')
code = code.replace('inst.components.fueled.accepting = true', '''inst.components.fueled.accepting = false

    inst:AddComponent("trader")
    inst.components.trader:SetAbleToAcceptTest(function(lantern, stone, giver, count)
        return stone ~= nil and stone.prefab == "ttk_lingshi1"
            and (count == nil or count == 1)
            and lantern.components.fueled:GetPercent() < 1
    end)
    inst.components.trader.onaccept = function(lantern, giver)
        lantern.components.fueled:DoDelta(lantern.components.fueled.maxfuel * 0.10)
        OnAddFuelItem(lantern, nil, nil, giver)
    end''')
(DST / f'scripts/prefabs/{new}.lua').write_text(code, encoding='utf-8')
for prefix in ['', 'swap_']:
    shutil.copyfile(SRC / f'anim/{prefix}{old}.zip', DST / f'anim/{prefix}{new}.zip')
folder = 'images/inventoryimages'
shutil.copyfile(SRC / f'{folder}/{old}.tex', DST / f'{folder}/{new}.tex')
(DST / f'{folder}/{new}.xml').write_text((SRC / f'{folder}/{old}.xml').read_text().replace(old, new), encoding='utf-8')
print('Ported lantern prefab, base animation/swap archives and inventory icon.')
