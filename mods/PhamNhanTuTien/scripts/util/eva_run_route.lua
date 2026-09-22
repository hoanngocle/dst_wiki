-- Staged live-game experiment. Nothing imports this from the production mod.
local M = {}

local NATIVE_BANK_HASH = 0x04844EF8 -- SDBM("wilson")
local NATIVE_RUN = "run_loop"
local EVA_RUN = "ttk_eva_run_loop"
local METHODS = { "PlayAnimation", "PushAnimation", "IsCurrentAnimation" }

local function DefaultLogger(message)
    print("[EVA run route] " .. message)
end

local function Pack(...)
    return { n = select("#", ...), ... }
end

local function Unpack(values)
    return unpack(values, 1, values.n)
end

local function Read(animstate, name)
    return pcall(function() return animstate[name] end)
end

local function Eligible(animstate)
    local get_build = animstate.GetBuild
    local get_bank_hash = animstate.GetBankHash
    local get_skin_build = animstate.GetSkinBuild
    if type(get_build) ~= "function"
            or type(get_bank_hash) ~= "function"
            or type(get_skin_build) ~= "function" then
        return false
    end
    local build_ok, build = pcall(get_build, animstate)
    local bank_ok, bank = pcall(get_bank_hash, animstate)
    local skin_ok, skin = pcall(get_skin_build, animstate)
    return build_ok and build == "eva"
        and bank_ok and bank == NATIVE_BANK_HASH
        and skin_ok and (skin == nil or skin == "" or skin == "eva")
end

local function Rollback(animstate, originals, wrappers, installed)
    local complete = true
    for index = #installed, 1, -1 do
        local name = installed[index]
        local read_ok, current = Read(animstate, name)
        if read_ok and current == wrappers[name] then
            local restore_ok = pcall(function()
                animstate[name] = originals[name]
            end)
            local verify_ok, restored = Read(animstate, name)
            if not restore_ok or not verify_ok or restored == wrappers[name] then
                complete = false
            end
        elseif not read_ok then
            complete = false
        end
    end
    return complete
end

local function MakeWrappers(animstate, originals, state)
    local wrappers = {}

    wrappers.PlayAnimation = function(self, name, ...)
        if self ~= animstate then
            return originals.PlayAnimation(self, name, ...)
        end
        if state.active and name == NATIVE_RUN and Eligible(animstate) then
            name = EVA_RUN
        end
        return originals.PlayAnimation(self, name, ...)
    end

    wrappers.PushAnimation = function(self, name, ...)
        if self ~= animstate then
            return originals.PushAnimation(self, name, ...)
        end
        if state.active and name == NATIVE_RUN and Eligible(animstate) then
            name = EVA_RUN
        end
        return originals.PushAnimation(self, name, ...)
    end

    wrappers.IsCurrentAnimation = function(self, name, ...)
        if self ~= animstate then
            return originals.IsCurrentAnimation(self, name, ...)
        end
        if not state.active or name ~= NATIVE_RUN or not Eligible(animstate) then
            return originals.IsCurrentAnimation(self, name, ...)
        end
        local native = Pack(originals.IsCurrentAnimation(self, NATIVE_RUN, ...))
        if native[1] then
            return Unpack(native)
        end
        return originals.IsCurrentAnimation(self, EVA_RUN, ...)
    end

    return wrappers
end

function M.Attach(inst, config)
    if inst == nil or inst.AnimState == nil then
        return nil
    end
    if inst._eva_run_route_adapter ~= nil then
        return inst._eva_run_route_adapter
    end

    local logger = config ~= nil and config.logger or DefaultLogger
    local animstate = inst.AnimState
    local originals = {}
    for _, name in ipairs(METHODS) do
        local ok, value = Read(animstate, name)
        if not ok or type(value) ~= "function" then
            logger("EVA run retarget unavailable; native motion may mismatch (missing callable "
                .. name .. ")")
            return nil
        end
        originals[name] = value
    end

    local state = { active = false }
    local wrappers = MakeWrappers(animstate, originals, state)
    local installed = {}
    for _, name in ipairs(METHODS) do
        local assign_ok = pcall(function()
            animstate[name] = wrappers[name]
        end)
        local read_ok, current = Read(animstate, name)
        if not assign_ok or not read_ok or current ~= wrappers[name] then
            state.active = false
            local rollback_complete = Rollback(
                animstate, originals, wrappers, METHODS
            )
            if rollback_complete then
                logger("EVA run retarget unavailable; native motion may mismatch")
            else
                logger("EVA run retarget install failed and rollback is incomplete; "
                    .. "native motion may mismatch")
            end
            return nil
        end
        table.insert(installed, name)
    end

    local adapter = {
        animstate = animstate,
        originals = originals,
        wrappers = wrappers,
        logger = logger,
        state = state,
    }
    function adapter:Remove()
        self.state.active = false
        local complete = Rollback(
            self.animstate, self.originals, self.wrappers, METHODS
        )
        if inst._eva_run_route_adapter == self then
            inst._eva_run_route_adapter = nil
        end
        if not complete then
            self.logger("EVA run retarget removal incomplete; native motion may mismatch")
        end
        return complete
    end

    state.active = true
    inst._eva_run_route_adapter = adapter
    if type(inst.ListenForEvent) == "function" then
        inst:ListenForEvent("onremove", function()
            if inst._eva_run_route_adapter == adapter then
                adapter:Remove()
            end
        end)
    end
    logger("EVA run retarget installed for this AnimState")
    return adapter
end

M.Eligible = Eligible
M.NATIVE_RUN = NATIVE_RUN
M.EVA_RUN = EVA_RUN

return M
