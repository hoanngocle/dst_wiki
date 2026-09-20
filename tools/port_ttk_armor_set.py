"""Port base armour assets and decoded source without modifying Workshop copies."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'mods/mod_steam/3235319974'
DECODED = ROOT / 'mods/eva-assets-work/skill-audit/decoded/scripts/prefabs'
DST = ROOT / 'mods/PhamNhanTuTien'
for old in ('xd_zcmj', 'xd_xshj', 'xd_yunxiao_ymsz'):
    new = old.replace('xd_', 'ttk_', 1)
    code = (DECODED / (old + '.lua')).read_text(encoding='utf-8')
    # Drop source comments, including disabled legacy resistance and undecoded bytes.
    code = re.sub(r'--[^\n]*', '', code)
    code = code.replace('xd_', 'ttk_').replace('FORGEMATERIALS.XD_XSHJ', 'FORGEMATERIALS.TTK_XSHJ')
    code = re.sub(r'    inst.XD_TRADER_STR = "XD_REPAIR"\n', '', code)
    # Preserve embedded animation bank/build names; file paths and prefabs are namespaced.
    code = re.sub(r'(SetBank\("|SetBuild\("|OverrideSymbol\("(?:swap_hat|swap_body)", ")(ttk_[^"]+)',
                  lambda m: m[1] + m[2].replace('ttk_', 'xd_', 1), code)
    code = code.replace('Asset("ATLAS", "images/inventoryimages/' + new + '.xml"),',
                        'Asset("ATLAS", "images/inventoryimages/' + new + '.xml"),\n    Asset("IMAGE", "images/inventoryimages/' + new + '.tex"),')
    if old in ('xd_zcmj', 'xd_xshj'):
        code = code.replace('SetAcceptTest(ShouldAcceptItem)', 'SetAbleToAcceptTest(ShouldAcceptItem)')
        start = code.index('local function ShouldAcceptItem(')
        end = code.index('\nlocal function OnGetItemFromPlayer', start)
        code = code[:start] + '''local function ShouldAcceptItem(inst, item, giver, count)
    return item ~= nil and item.prefab == "ttk_lingshi2"
        and (count == nil or count == 1) and inst.components.armor:GetPercent() < 1
end
''' + code[end:]
        code = code.replace('if inst._task == nil and\n        not data.redirected',
                            'if inst._task == nil and\n        data ~= nil and not data.redirected')
    else:
        code = code.replace('"yellowamuletlight"', '"minerhatlight"')
        code = code.replace('inst._light = SpawnPrefab("minerhatlight")',
                            'inst._light = SpawnPrefab("minerhatlight")\n        inst._light.Light:SetRadius(5)')
        code = code.replace('    MakeHauntableLaunch(inst)', '''    -- A destroyed or removed coat must not leave a light attached to its owner.
    inst.OnRemoveEntity = function(coat)
        if coat._light ~= nil and coat._light:IsValid() then coat._light:Remove() end
        coat._light = nil
    end
    inst.components.equippable:SetOnEquipToModel(onunequip)
    MakeHauntableLaunch(inst)''')
        code = code.replace('Prefab("ttk_yunxiao_ymsz", fn, assets)',
                            'Prefab("ttk_yunxiao_ymsz", fn, assets, {"minerhatlight"})')
    if old == 'xd_zcmj':
        code = code.replace('Prefab("ttk_zcmj", fn, assets)', 'Prefab("ttk_zcmj", fn, assets, {"ttk_zcmj_forcefield"})')
    code = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', code)
    (DST / f'scripts/prefabs/{new}.lua').write_text(code, encoding='utf-8')
    shutil.copyfile(SRC / f'anim/{old}.zip', DST / f'anim/{new}.zip')
    for extension in ('xml', 'tex'):
        source = SRC / f'images/inventoryimages/{old}.{extension}'
        target = DST / f'images/inventoryimages/{new}.{extension}'
        if extension == 'xml':
            target.write_text(source.read_text().replace(old, new), encoding='utf-8')
        else:
            shutil.copyfile(source, target)
shutil.copyfile(SRC / 'anim/xd_zcmj_forcefield.zip', DST / 'anim/ttk_zcmj_forcefield.zip')
print('Ported three armour prefabs, shield FX and their original assets.')
