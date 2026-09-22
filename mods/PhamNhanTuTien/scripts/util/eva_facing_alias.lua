-- Staged candidate module. It is not installed in the production mod.
local M = {}

local TARGETS = {
    "skirt", "arm_lower", "hairpigtails", "arm_upper", "hand",
}

local FACING_VIEWS = {
    [FACING_RIGHT or 0] = "profile",
    [FACING_UP or 1] = "rear",
    [FACING_LEFT or 2] = "profile",
    [FACING_DOWN or 3] = "front",
    [FACING_UPRIGHT or 4] = "rear",
    [FACING_UPLEFT or 5] = "rear",
    [FACING_DOWNRIGHT or 6] = "front",
    [FACING_DOWNLEFT or 7] = "front",
}

function M.FacingVariant(facing)
    return FACING_VIEWS[facing]
end

local function CurrentOverride(animstate, target)
    local build, symbol = animstate:GetSymbolOverride(target)
    return build, symbol
end

function M.MakeController(inst, config)
    config = config or {}
    local build = config.build or "eva"
    local build_hash = hash(build)
    local targets = config.targets or TARGETS
    local bank_hashes = config.bank_hashes or {
        [hash("wilson")] = true,
        [hash("wilsonbeefalo")] = true,
    }
    local owned = {}
    local current_view = nil

    local controller = {}

    local function IsOwned(source_build, source_symbol, expected)
        return expected ~= nil
            and (source_build == build_hash or source_build == build)
            and (source_symbol == expected.hash or source_symbol == expected.name)
    end

    local function ClearOwned()
        local animstate = inst.AnimState
        for _, target in ipairs(targets) do
            local expected = owned[target]
            if expected ~= nil then
                local source_build, source_symbol = CurrentOverride(animstate, target)
                if IsOwned(source_build, source_symbol, expected) then
                    animstate:ClearOverrideSymbol(target)
                end
                owned[target] = nil
            end
        end
        current_view = nil
    end

    function controller:Clear()
        ClearOwned()
    end

    function controller:Update()
        local animstate = inst.AnimState
        local view = M.FacingVariant(animstate:GetCurrentFacing())
        local skin_build = animstate.GetSkinBuild ~= nil
            and animstate:GetSkinBuild()
            or nil
        if animstate:GetBuild() ~= build
            or (skin_build ~= nil and skin_build ~= "" and skin_build ~= build)
            or not bank_hashes[animstate:GetBankHash()]
            or view == nil then
            ClearOwned()
            return false
        end

        -- Never steal a controlled target from skin, wardrobe, or another mod.
        local complete = current_view == view
        for _, target in ipairs(targets) do
            local source_build, source_symbol = CurrentOverride(animstate, target)
            local expected = owned[target]
            if source_build ~= nil
                and not IsOwned(source_build, source_symbol, expected) then
                ClearOwned()
                return false
            end
            if not IsOwned(source_build, source_symbol, expected) then
                complete = false
            end
        end

        if complete then
            return true
        end

        for _, target in ipairs(targets) do
            local source = target .. "__eva_" .. view
            animstate:OverrideSymbol(target, build, source)
            owned[target] = { name = source, hash = hash(source) }
        end
        current_view = view
        return true
    end

    return controller
end

function M.Attach(inst, config)
    local controller = M.MakeController(inst, config)
    controller:Update()
    local interval = config ~= nil and config.interval or FRAMES or (1 / 30)
    local task = inst:DoPeriodicTask(interval, function() controller:Update() end)
    return controller, task
end

return M
