-- Staged candidate integration. Nothing imports this from the production mod.
local FacingAlias = require "util/eva_facing_alias"

local M = {}

function M.AttachPlayer(inst, net)
    if net ~= nil and net:IsDedicated() then
        return nil
    end
    if inst._eva_facing_alias_controller ~= nil then
        return inst._eva_facing_alias_controller
    end

    local controller, task = FacingAlias.Attach(inst)
    inst._eva_facing_alias_controller = controller
    inst._eva_facing_alias_task = task

    inst:ListenForEvent("onremove", function()
        if inst._eva_facing_alias_controller ~= controller then
            return
        end
        controller:Clear()
        if task ~= nil and task.Cancel ~= nil then
            task:Cancel()
        end
        inst._eva_facing_alias_controller = nil
        inst._eva_facing_alias_task = nil
    end)

    return controller
end

function M.AttachPuppet(puppet)
    if puppet._eva_facing_alias_controller ~= nil then
        return puppet._eva_facing_alias_controller
    end

    local controller = FacingAlias.MakeController({ AnimState = puppet.animstate })
    puppet._eva_facing_alias_controller = controller

    local native_set_skins = puppet.SetSkins
    puppet.SetSkins = function(self, ...)
        native_set_skins(self, ...)
        controller:Update()
    end

    local native_emote_update = puppet.EmoteUpdate
    puppet.EmoteUpdate = function(self, ...)
        native_emote_update(self, ...)
        if self.sitting then
            controller:Clear()
        else
            controller:Update()
        end
    end

    local native_sit = puppet.Sit
    puppet.Sit = function(self, ...)
        native_sit(self, ...)
        -- Native SkinsPuppet:Sit keeps the wilson bank and EmoteUpdate exits
        -- early, so bank gating alone cannot suspend the aliases.
        controller:Clear()
    end

    local native_kill = puppet.Kill
    puppet.Kill = function(self, ...)
        controller:Clear()
        self._eva_facing_alias_controller = nil
        return native_kill(self, ...)
    end

    controller:Update()
    return controller
end

function M.InstallSkinsPuppet(add_class_post_construct)
    add_class_post_construct("widgets/skinspuppet", function(puppet)
        M.AttachPuppet(puppet)
    end)
end

return M
