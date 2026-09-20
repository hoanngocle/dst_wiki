local Life = require "util/eva_life_common"

local Fox = {}

Fox.COOLDOWN = 12
Fox.CAST_RANGE = 20
Fox.FADE_TIME = 0.5
Fox.TELEPORT_TIME = 1.75
Fox.RESTORE_TIME = 2.0
Fox.FINISH_TIME = 2.2
Fox.FIRE_DAMAGE = 266.7
Fox.FIRE_RADIUS = 4
Fox.FIRE_PERIOD = 0.2
Fox.FIRE_TICKS = 3
Fox.FIRE_LIFETIME = 1.5
Fox.HEAL_FRACTION = 0.033
Fox.SLEEPINESS = 0.8
Fox.SLEEP_DURATION = 3

local TARGET_MUST_TAGS = {"_combat"}
local TARGET_CANT_TAGS = {
    "INLIMBO", "NOCLICK", "notarget", "noattack", "playerghost",
    "flight", "invisible", "companion", "wall",
}

function Fox.IsFiniteNumber(value)
    return type(value) == "number"
        and value == value
        and value > -math.huge
        and value < math.huge
end

local function HasStateTag(owner, tag)
    return owner.sg ~= nil and owner.sg:HasStateTag(tag)
end

local function IsMountedOrTransitioning(owner)
    local components = owner.components or {}
    return (components.rider ~= nil and components.rider:IsRiding())
        or (components.locomotor ~= nil and (components.locomotor.hopping == true
            or (components.locomotor.IsHopping ~= nil and components.locomotor:IsHopping())))
        or (components.freezable ~= nil and components.freezable:IsFrozen())
        or HasStateTag(owner, "knockout")
        or HasStateTag(owner, "frozen")
        or HasStateTag(owner, "hopping")
        or HasStateTag(owner, "jumping")
        or HasStateTag(owner, "mounting")
        or HasStateTag(owner, "dismounting")
end

function Fox.CanActivate(owner)
    return owner ~= nil
        and Life.CanActivate(owner)
        and not IsMountedOrTransitioning(owner)
end

function Fox.CanContinueCast(owner)
    return owner ~= nil
        and Life.CanRemainActive(owner)
        and not IsMountedOrTransitioning(owner)
end

function Fox.CanOwnerRemain(owner)
    return Life.CanRemainActive(owner)
end

local function HasActiveWings(owner)
    local wings = owner.components ~= nil and owner.components.eva_wings or nil
    return wings ~= nil and wings.IsActive ~= nil and wings:IsActive()
end

function Fox.ValidateDestination(owner, x, z, origin_x, origin_z)
    if not Fox.IsFiniteNumber(x) or not Fox.IsFiniteNumber(z) then
        return false, "invalid_coordinates"
    end
    if not Fox.IsFiniteNumber(origin_x) or not Fox.IsFiniteNumber(origin_z) then
        return false, "invalid_origin"
    end
    local dx, dz = x - origin_x, z - origin_z
    if dx * dx + dz * dz > Fox.CAST_RANGE * Fox.CAST_RANGE then
        return false, "out_of_range"
    end

    local map = TheWorld ~= nil and TheWorld.Map or nil
    if map == nil then return false, "invalid_terrain" end
    local width, height = map:GetSize()
    local scale = TILE_SCALE or 4
    if type(width) ~= "number" or type(height) ~= "number"
        or math.abs(x) >= width * scale / 2
        or math.abs(z) >= height * scale / 2 then
        return false, "out_of_bounds"
    end

    local point = Vector3(x, 0, z)
    if map:IsGroundTargetBlocked(point) then return false, "ground_blocked" end

    local platform = map:GetPlatformAtPoint(x, z)
    local passable = map:IsPassableAtPoint(x, 0, z, false)
    local is_ocean = map:IsOceanAtPoint(x, 0, z, false)
    if platform == nil and not passable then
        if not is_ocean or (TheWorld.HasTag ~= nil and TheWorld:HasTag("cave")) then
            return false, "invalid_terrain"
        end
        if not HasActiveWings(owner) then return false, "ocean_requires_wings" end
    end

    local source_x, source_y, source_z = owner.Transform:GetWorldPosition()
    if IsTeleportingPermittedFromPointToPoint == nil
        or not IsTeleportingPermittedFromPointToPoint(
            source_x, source_y, source_z, x, 0, z) then
        return false, "teleport_not_permitted"
    end
    return true
end

function Fox.FindTargetsAt(owner, x, z)
    if not Life.CanRemainActive(owner) then return {} end
    local found = TheSim:FindEntities(
        x, 0, z, Fox.FIRE_RADIUS, TARGET_MUST_TAGS, TARGET_CANT_TAGS)
    local targets = {}
    for _, target in ipairs(found) do
        if Life.IsValidTarget(owner, target, nil) then
            local tx, _, tz = target.Transform:GetWorldPosition()
            local dx, dz = tx - x, tz - z
            if dx * dx + dz * dz <= Fox.FIRE_RADIUS * Fox.FIRE_RADIUS then
                targets[#targets + 1] = target
            end
        end
    end
    return targets
end

function Fox.IsValidTarget(owner, target)
    return Life.IsValidTarget(owner, target, nil)
end

function Fox.CanSleep(target)
    local components = target.components or {}
    return not (components.freezable ~= nil and components.freezable:IsFrozen())
        and not (components.pinnable ~= nil and components.pinnable:IsStuck())
        and not (components.fossilizable ~= nil and components.fossilizable:IsFossilized())
end

return Fox
