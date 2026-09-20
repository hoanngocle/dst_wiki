"""Port the local Tu Tien 19.7 umbrella without executing its loader."""
from pathlib import Path
import re
import shutil
from port_vanhonphien import MAPPING

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'mods/mod_steam/3235319974'
DEST = ROOT / 'mods/PhamNhanTuTien'
NAME = 'nhatvuphuonghoa'
MAPPING.update({0x9B: ord('9'), 0xEA: ord('J')})
raw = (SOURCE/'scripts/prefabs/xd_sudaji_ywfh.lua').read_bytes()
text = ''.join(chr(MAPPING[c]) if c in MAPPING else '<%02X>' % c for c in raw[::-1])
text = text.replace('\r\n','\n').replace('\r','\n')
text = re.sub(r'--\[\[.*?\]\]', '', text, flags=re.S)
text = re.sub(r'--[^\n]*', '', text)
text = re.sub(r'XD_SAY\(caster,"[^"\n]*"\)', 'if caster.components.talker then caster.components.talker:Say("Ô cần ít nhất 25% độ bền.") end', text)
assert not re.search(r'<[0-9A-F]{2}>',text), 'Incomplete source decoding'
text = text.replace('xd_sudaji_ywfh', NAME).replace('xd_ywfhbuff', NAME+'_buff')
# Keep the bank/build/symbol names embedded inside original animation archives.
text = text.replace('SetBank("'+NAME+'")', 'SetBank("xd_sudaji_ywfh")')
text = text.replace('SetBuild("'+NAME+'")', 'SetBuild("xd_sudaji_ywfh")')
text = text.replace('SetBuild("'+NAME+'_fx")', 'SetBuild("xd_sudaji_ywfh_fx")')
text = text.replace('skin_build or "'+NAME+'"', 'skin_build or "xd_sudaji_ywfh"')
text = text.replace('"XD_KEEPDRY"', '"NHATVU_KEEPDRY"')
text = text.replace('local prefabs = {\n\n}', 'local prefabs = { "nhatvuphuonghoa_buff" }')
text = text.replace('    inst.components.inventoryitem.atlasname', '    inst.components.inventoryitem.imagename = "nhatvuphuonghoa"\n    inst.components.inventoryitem.atlasname')
# Empty equipped umbrellas must retain their broken marker too.
text = text.replace('local function OnPerish(inst)\n', 'local function OnPerish(inst)\n    inst:AddTag("broken")\n')
text = text.replace('    inst.components.fueled.fueltype = FUELTYPE.SUDAJI_SOUL', '    inst.components.fueled.fueltype = "NHATVU_DURABILITY"')
text = text.replace('    inst.components.fueled.accepting = true', '''    inst.components.fueled.accepting = false

    inst:AddComponent("trader")
    inst.components.trader:SetAbleToAcceptTest(function(item, stone, giver, count)
        return stone ~= nil and stone.prefab == "ttk_lingshi1"
            and (count == nil or count == 1)
            and item.components.fueled:GetPercent() < 1
    end)
    inst.components.trader.onaccept = function(item, giver)
        item.components.fueled:DoDelta(item.components.fueled.maxfuel * 0.05)
        OnAddFuelItem(item, nil, nil, giver)
    end''')
# The source's only remaining character subsystem is a visual skin lookup;
# standard DST provides it. Spell targets use standard player/debuff components.
text = text.replace('return target and target:HasTag("player")', 'return target and target:HasTag("player") and not target:HasTag("playerghost")')
text = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n',text)
(DEST/'scripts/prefabs'/f'{NAME}.lua').write_text('-- Adapted from Tu Tien 19.7; see CREDITS.md.\n'+text,encoding='utf-8')
for suffix in ('','_fx'):
    shutil.copyfile(SOURCE/f'anim/xd_sudaji_ywfh{suffix}.zip',DEST/f'anim/{NAME}{suffix}.zip')
shutil.copyfile(SOURCE/'images/inventoryimages/xd_sudaji_ywfh.tex',DEST/f'images/inventoryimages/{NAME}.tex')
xml=(SOURCE/'images/inventoryimages/xd_sudaji_ywfh.xml').read_text()
(DEST/f'images/inventoryimages/{NAME}.xml').write_text(xml.replace('xd_sudaji_ywfh',NAME),encoding='utf-8')
print('Ported original umbrella logic, animations and inventory icon.')
