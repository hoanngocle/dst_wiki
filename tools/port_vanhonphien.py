"""Static, reproducible port of the local Tu Tien 19.7 soul banner.

Never executes the source mod's loader. Gameplay adaptations live below;
the source animation geometry and textures are preserved.
"""
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'mods/mod_steam/3235319974'
DEST = ROOT / 'mods/PhamNhanTuTien'
MAPPING = {int(k): v for k, v in json.loads(
    (ROOT / 'mods/mod_steam/.tu-tien-extraction/byte_mapping.json').read_text()).items()}
# Unambiguous Lua tokens: EQUIPSLOTS, comparisons, numeric literals.
MAPPING.update({0x97: 86, 0xA5: 55, 0x43: 42, 0xD1: 43, 0x3C: 85,
                0x0F: 90, 0x4D: 89, 0xE7: 62, 0x88: 56, 0x26: 81, 0x39: 60})
RENAMES = {
    'xd_wmz_zhf': 'vanhonphien',
    'xd_wmz_soulfx': 'vanhonphien_soulfx',
    'xd_wmzsoulbrain': 'vanhonphienbrain',
    'xd_zhf_vortexfx': 'vanhonphien_vortexspawner',
    'xd_vortex_fx': 'vanhonphien_vortexfx',
    'wmx_nosoultask': '_vanhonphien_nosoultask',
    '_xd_weapon_fx': '_vanhonphien_fx',
    'spwanentity': 'banner',
}


def rename(text):
    for old, new in RENAMES.items():
        text = text.replace(old, new)
    return text


def decode(path):
    raw = (SOURCE / path).read_bytes()
    text = ''.join(chr(MAPPING[c]) if c in MAPPING else '<%02X>' % c for c in raw[::-1])
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'--\[\[.*?\]\]', '', text, flags=re.S)
    text = re.sub(r'--[^\n]*', '', text)
    assert not re.search(r'<[0-9A-F]{2}>', text), path
    return re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', rename(text))


def write(path, text):
    path = DEST / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def replace(text, old, new):
    assert text.count(old) == 1, (text.count(old), old[:100])
    return text.replace(old, new)


def section(text, start, end, value):
    a, b = text.index(start), text.index(end, text.index(start))
    return text[:a] + value + '\n\n' + text[b:]


def main():
    backup = ROOT / 'mods/backups/TuTienKy_v0.2.0_before_vanhonphien.zip'
    if not backup.exists():
        with ZipFile(backup, 'w', ZIP_DEFLATED) as z:
            for p in DEST.rglob('*'):
                if p.is_file():
                    z.write(p, 'TuTienKy/' + p.relative_to(DEST).as_posix())

    text = decode('scripts/prefabs/xd_wmz_zhf.lua')
    text = 'local rules = require("vanhonphien_rules")\n\n' + text
    text = replace(text, 'local function ondeploy(inst, pt, deployer)', '''local function SaveBanner(inst, data)
    data.soul_count = inst.soul_count or 0
    data.userid = inst._userid
end

local function LoadBanner(inst, data)
    if data ~= nil then
        inst.soul_count = math.max(0, math.min(2, tonumber(data.soul_count) or 0))
        inst._userid = data.userid
    end
end

local function TransferState(inst, other)
    local data = {}
    SaveBanner(inst, data)
    LoadBanner(other, data)
    local timers = inst.components.timer:OnSave()
    if timers ~= nil then
        other.components.timer:OnLoad(timers)
    end
end

local function ondeploy(inst, pt, deployer)''')
    text = section(text, '    item._userid = deployer.userid', '    inst:Remove()', '''    TransferState(inst, item)
    item._userid = deployer ~= nil and deployer.userid or nil
    if rules.IsLivingPlayer(deployer) then
        if deployer.components.timer == nil then
            deployer:AddComponent("timer")
        end
        local timer = deployer.components.timer
        if not timer:TimerExists("vanhonphien_soul_cd")
            and not item.components.timer:TimerExists("initial_cd") then
            for _ = 1, 2 do
                item:SpawnPet(deployer)
            end
            timer:StartTimer("vanhonphien_soul_cd", 60)
            item.components.timer:StartTimer("initial_cd", 60)
        end
    end''')
    text = section(text, '    local save = inst.components.timer:OnSave()', '\nend\n', '    TransferState(inst, item)')
    text = replace(text, '    inst.components.deployable.restrictedtag = "xd_wangmazi"', '''    inst.components.deployable:SetDeployMode(DEPLOYMODE.DEFAULT)
    inst.OnSave = SaveBanner
    inst.OnLoad = LoadBanner
    inst.soul_count = 0''')
    text = replace(text, '    local victim = data.inst', '    local victim = data ~= nil and data.inst or nil')
    text = replace(text, '    local shouldspawn = victim == inst\n', '')
    text = replace(text, '        local fx = SpawnAt("vanhonphien_soulfx",victim)', '''        local fx = SpawnAt("vanhonphien_soulfx", victim)
        if fx ~= nil then
            fx.owner = inst
            fx.dofind = false
        end''')
    text = replace(text, 'local function SpawnPet(inst,player)\n', '''local function SpawnPet(inst,player)
    if not rules.IsLivingPlayer(player) then
        return
    end
''')
    text = replace(text, '            local player = inst._userid ~= nil and UserToPlayer(inst._userid) or nil',
                   '            local player = rules.FindOwner(inst._userid)')
    text = replace(text, '            if player and player:IsValid() and player:IsNear(inst,16) then',
                   '            if rules.IsLivingPlayer(player) and player:IsNear(inst,16) then')
    text = replace(text, '\t\tk:Kill()', '\t\tif k:IsValid() then k:Kill() end')
    text = section(text, '    inst.OnSave = function(inst,data)', '    return inst\nend', '''    inst.OnSave = SaveBanner
    inst.OnLoad = LoadBanner
    inst:ListenForEvent("timerdone", function(_, data)
        if data ~= nil and string.match(data.name, "^cd%d$")
            and inst.soul_count >= 2 then
            inst:AddSoul()
        end
    end)''')
    text = replace(text, 'owner:IsValid() and XD_CanAttackTrget(inst,guy)', 'rules.CanAttack(inst, guy)')
    text = section(text, 'local function OnAttacked(inst, data)', 'local function KeepTargetFn', '''local function OnAttacked(inst, data)
    if data ~= nil and rules.CanAttack(inst, data.attacker) then
        inst.components.combat:SuggestTarget(data.attacker)
    end
end
''')
    text = replace(text, 'return target and target:IsValid() and  inst.components.combat:CanTarget(target)',
                   'return rules.CanAttack(inst, target) and inst.components.combat:CanTarget(target)')
    # Original owner CalcDamage override uses combat.defaultdamage (20), ignoring weapon's 33.
    text = replace(text, 'weapon.components.weapon:SetDamage(33)', 'weapon.components.weapon:SetDamage(20)')
    text = replace(text, '    XD_Get_OwnerCalcDamage(inst)', '''    -- Independent base damage; no cultivation or Solo component is required.
    inst:ListenForEvent("onremove", function() inst:Kill() end, owner)
    inst:ListenForEvent("death", function() inst:Kill() end, owner)''')
    text = replace(text, 'return XD_CanAttackTrget(inst,ent)', 'return rules.CanAttack(inst, ent)')
    text = text.replace('function(self,target, range, weapon, validfn, stimuli, excludetags)',
                        'function(self,target, range, weapon, validfn, stimuli, excludetags, ...)')
    text = text.replace('old_DoAreaAttack(self,target, range, weapon, validfn, stimuli, excludetags)',
                        'old_DoAreaAttack(self,target, range, weapon, validfn, stimuli, excludetags, ...)')
    text = replace(text, '        inst.components.projectile.range = 30', '''        inst.components.projectile.range = 30
        local original_hit = inst.components.projectile.Hit
        inst.components.projectile.Hit = function(self, target)
            local weapon = self.owner
            local attacker = weapon ~= nil and weapon:IsValid()
                and weapon.components.inventoryitem ~= nil
                and weapon.components.inventoryitem.owner or nil
            if attacker == nil or not attacker:IsValid()
                or attacker.components.health:IsDead()
                or not rules.CanAttack(attacker, target) then
                self:Miss(target)
                return
            end
            return original_hit(self, target)
        end''')
    text = text.replace('    inst:AddTag("xd_skill_pet")\n', '').replace('    inst:AddTag("no_drop_xdlingshi")\n', '')
    # Carry an actual follower relationship so standard combat knows the player's allies.
    text = replace(text, '    inst:AddComponent("entitytracker")', '    inst:AddComponent("entitytracker")\n    inst:AddComponent("follower")')
    text = replace(text, '    inst.owner = owner', '    inst.owner = owner\n    inst.components.follower:SetLeader(owner)')
    text = replace(text, 'inst.owner:IsValid() and inst:IsNear(inst.owner,8)', 'inst.owner:IsValid() and inst:IsNear(inst.owner,18)')
    # Assets and dependencies must be on the prefabs that actually use them.
    text = replace(text, '    Asset("ATLAS", "images/inventoryimages/vanhonphien.xml") ,',
                   '    Asset("ATLAS", "images/inventoryimages/vanhonphien.xml"),\n    Asset("IMAGE", "images/inventoryimages/vanhonphien.tex"),')
    text = replace(text, 'Prefab("vanhonphien",itemfn,assets)', 'Prefab("vanhonphien",itemfn,assets,{"vanhonphien_ground"})')
    text = replace(text, 'Prefab("vanhonphien_ground", groundfn,assets)', 'Prefab("vanhonphien_ground", groundfn,assets,{"vanhonphien", "vanhonphien_soul", "vanhonphien_soulfx", "vanhonphien_vortexspawner", "collapse_small"})')
    text = replace(text, 'Prefab("vanhonphien_soul", soulfn,assets)', 'Prefab("vanhonphien_soul", soulfn,assets,{"vanhonphien_projectile"})')
    text = replace(text, 'Prefab("vanhonphien_soulfx", fxfn, soulassets, prefabs)', 'Prefab("vanhonphien_soulfx", fxfn, soulassets, {"vanhonphien_soulfx_in"})')
    # Retain embedded bank/build resource names; gameplay IDs remain independent.
    text = text.replace('SetBank("vanhonphien")', 'SetBank("xd_wmz_zhf")')
    text = text.replace('SetBuild("vanhonphien")', 'SetBuild("xd_wmz_zhf")')
    text = text.replace('SetBuild("vanhonphien_soul")', 'SetBuild("xd_wmz_zhf_soul")')
    text = text.replace('"vanhonphien_placer", "vanhonphien", "vanhonphien"',
                        '"vanhonphien_placer", "xd_wmz_zhf", "xd_wmz_zhf"')
    write('scripts/prefabs/vanhonphien.lua', '-- Adapted from Tu Tien 19.7; see CREDITS.md.\n' + text)

    brain = decode('scripts/brains/xd_wmzsoulbrain.lua')
    brain = ('require "behaviours/leash"\nrequire "behaviours/follow"\n'
             'require "behaviours/wander"\n' + brain)
    write('scripts/brains/vanhonphienbrain.lua', brain)
    write('scripts/stategraphs/SGvanhonphien_soul.lua', decode('scripts/stategraphs/SGxd_wmz_zhf_soul.lua'))

    for old, new in [('xd_wmz_zhf', 'vanhonphien'), ('xd_wmz_zhf_soul', 'vanhonphien_soul'),
                     ('xd_vortex_fx', 'vanhonphien_vortexfx'), ('cloak_fx', 'vanhonphien_cloakfx')]:
        with ZipFile(SOURCE / f'anim/{old}.zip') as z:
            assert z.testzip() is None
        shutil.copyfile(SOURCE / f'anim/{old}.zip', DEST / f'anim/{new}.zip')
    shutil.copyfile(SOURCE / 'images/inventoryimages/xd_wmz_zhf.tex', DEST / 'images/inventoryimages/vanhonphien.tex')
    write('images/inventoryimages/vanhonphien.xml', rename((SOURCE / 'images/inventoryimages/xd_wmz_zhf.xml').read_text()))
    print('Ported banner, brain, stategraph, 4 verified animation archives and inventory icon.')


if __name__ == '__main__':
    main()
