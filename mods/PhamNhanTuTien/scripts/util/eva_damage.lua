-- Keep weapon.damage numeric: Solo enhances it through SetDamage. Critical
-- multipliers belong to an individual hit, never to the saved/base damage.
local Damage = {}

function Damage.GetStrikeDamage(inst)
    local weapon = inst.components.weapon
    local base = weapon and weapon.damage
    if type(base) ~= 'number' then
        base = TUNING.EVA_SCYTHE_DMG
    end
    return base * TUNING.EVA_SCYTHE_CRITDMG
end

local function IsCritical(attacker, target)
    if attacker == nil or target == nil or not attacker:HasTag('eva') then
        return false
    end
    if target:HasTag('ghost') then
        return true
    end
    local souls = attacker.components.eva_souls
    if souls == nil or souls.max <= 0 then
        return false
    end
    local chance = math.min(1, math.max(0,
        souls.current / souls.max * TUNING.EVA_SCYTHE_CRITRATE / 100))
    return chance > 0 and math.random() < chance
end

function Damage.Install(inst)
    local weapon = inst.components.weapon
    local get_damage = weapon.GetDamage
    weapon.GetDamage = function(self, attacker, target, ...)
        local damage, special = get_damage(self, attacker, target, ...)
        local critical = IsCritical(attacker, target)
        -- This record is only for the hit's visual effects. It never changes
        -- SetDamage, Solo's original_damage, or the Soul Strike calculation.
        inst._eva_hit = {attacker = attacker, target = target, critical = critical}
        return critical and damage * TUNING.EVA_SCYTHE_CRITDMG or damage, special
    end
end

function Damage.ConsumeCritical(inst, attacker, target)
    local hit = inst._eva_hit
    inst._eva_hit = nil
    return hit ~= nil and hit.attacker == attacker and hit.target == target and hit.critical
end

return Damage
