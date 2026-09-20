local Common = require "util/eva_fox_common"

local MOVEMENT_KEY = "eva_fox_blink"

local EvaFoxBlink = Class(function(self, inst)
    self.inst = inst
    self.active = false
    self.cooldown_end = 0
    self.tasks = {}
    self.fires = {}
    self.cast_token = nil
    self.protection_token = nil
    self.protection_wrapper = nil
    self.previous_is_invincible = nil
    self.hide_token = nil
    self.fade_token = nil
    self.movement_locked = false
    self.cast_state = nil
    self.fade_colour = nil
    self.previous_hide = nil
    self.previous_show = nil
    self.hide_wrapper = nil
    self.show_wrapper = nil
    self.foreign_hide_count = 0
    self.visibility_internal = false

    self._ondeath = function() self:Stop("death") end
    self._onghost = function() self:Stop("ghost") end
    self._onremove = function() self:Stop("remove") end
    self._onnewstate = function()
        if self.active and ((self.cast_state ~= nil
                and self.inst.sg ~= nil
                and self.inst.sg.currentstate ~= self.cast_state)
            or not Common.CanContinueCast(self.inst)) then
            self:Stop("interrupted")
        end
    end
    inst:ListenForEvent("death", self._ondeath)
    inst:ListenForEvent("ms_becameghost", self._onghost)
    inst:ListenForEvent("onremove", self._onremove)
    inst:ListenForEvent("newstate", self._onnewstate)
end)

local function CancelTask(task)
    if task ~= nil then task:Cancel() end
end

local function RemoveEntity(entity)
    if entity ~= nil and entity:IsValid() then entity:Remove() end
end

function EvaFoxBlink:GetCooldownRemaining()
    return math.max(0, self.cooldown_end - GetTime())
end

function EvaFoxBlink:IsActive()
    return self.active
end

function EvaFoxBlink:_Say(message)
    local talker = self.inst.components ~= nil and self.inst.components.talker or nil
    if talker ~= nil then talker:Say(message) end
end

function EvaFoxBlink:_Schedule(name, delay, fn)
    self.tasks[name] = self.inst:DoTaskInTime(delay, function()
        self.tasks[name] = nil
        if self.active then fn() end
    end)
end

function EvaFoxBlink:_SpawnAt(name, x, z)
    local fx = SpawnPrefab(name)
    if fx ~= nil then fx.Transform:SetPosition(x, 0, z) end
    return fx
end

function EvaFoxBlink:_LockMovement()
    local locomotor = self.inst.components ~= nil and self.inst.components.locomotor or nil
    if locomotor ~= nil then
        locomotor:Stop()
        locomotor:SetExternalSpeedMultiplier(self.inst, MOVEMENT_KEY, 0)
        self.movement_locked = true
    end
end

function EvaFoxBlink:_UnlockMovement()
    if not self.movement_locked then return end
    local locomotor = self.inst.components ~= nil and self.inst.components.locomotor or nil
    if locomotor ~= nil then
        locomotor:RemoveExternalSpeedMultiplier(self.inst, MOVEMENT_KEY)
    end
    self.movement_locked = false
end

function EvaFoxBlink:_InstallProtection()
    local health = self.inst.components ~= nil and self.inst.components.health or nil
    if health == nil or self.protection_wrapper ~= nil then return end
    local previous, token = health.IsInvincible, {}
    local wrapper
    wrapper = function(component, ...)
        return (previous ~= nil and previous(component, ...))
            or (self.active and self.protection_token == token)
    end
    self.protection_token = token
    self.protection_wrapper = wrapper
    self.previous_is_invincible = previous
    health.IsInvincible = wrapper
    self.inst:PushEvent("invincibletoggle", {invincible = true})
end

function EvaFoxBlink:_ReleaseProtection()
    local health = self.inst.components ~= nil and self.inst.components.health or nil
    if health ~= nil and health.IsInvincible == self.protection_wrapper then
        health.IsInvincible = self.previous_is_invincible
        self.inst:PushEvent("invincibletoggle", {
            invincible = health.IsInvincible ~= nil and health:IsInvincible() or false,
        })
    end
    self.protection_token = nil
    self.protection_wrapper = nil
    self.previous_is_invincible = nil
end

function EvaFoxBlink:_StartFade()
    local entity = self.inst.entity
    if entity == nil or entity.IsVisible == nil or not entity:IsVisible() then return end
    local token = {}
    self.fade_token = token
    self.inst._eva_fox_fade_token = token
    local r, g, b, a = 1, 1, 1, 1
    if self.inst.AnimState ~= nil and self.inst.AnimState.GetMultColour ~= nil then
        local cr, cg, cb, ca = self.inst.AnimState:GetMultColour()
        r, g, b, a = cr or r, cg or g, cb or b, ca or a
    end
    self.fade_colour = {r, g, b, a}
    for step = 1, 5 do
        self:_Schedule("fade_" .. tostring(step), step * 0.1, function()
            if self.fade_token == token and self.inst._eva_fox_fade_token == token
                and self.inst.AnimState ~= nil then
                self.inst.AnimState:SetMultColour(r, g, b, a * (1 - step / 5))
            end
        end)
    end
end

function EvaFoxBlink:_Hide()
    self:_InstallProtection()
    local entity = self.inst.entity
    if entity ~= nil and entity.IsVisible ~= nil and entity:IsVisible()
        and self.inst._eva_fox_hide_token == nil then
        local token = {}
        self.hide_token = token
        self.inst._eva_fox_hide_token = token
        local previous_hide, previous_show = self.inst.Hide, self.inst.Show
        local hide_wrapper, show_wrapper
        hide_wrapper = function(inst, ...)
            if not self.visibility_internal then
                self.foreign_hide_count = self.foreign_hide_count + 1
            end
            return previous_hide(inst, ...)
        end
        show_wrapper = function(inst, ...)
            if not self.visibility_internal then
                if self.foreign_hide_count > 0 then
                    self.foreign_hide_count = self.foreign_hide_count - 1
                end
                if self.active and self.hide_token == token then return end
            end
            return previous_show(inst, ...)
        end
        self.previous_hide, self.previous_show = previous_hide, previous_show
        self.hide_wrapper, self.show_wrapper = hide_wrapper, show_wrapper
        self.inst.Hide, self.inst.Show = hide_wrapper, show_wrapper
        self.visibility_internal = true
        self.inst:Hide()
        self.visibility_internal = false
        local shadow = self.inst.DynamicShadow
        if shadow ~= nil then
            local enabled = shadow.IsEnabled == nil or shadow:IsEnabled()
            if enabled then
                self.inst._eva_fox_shadow_token = token
                shadow:Enable(false)
            end
        end
    end
end

function EvaFoxBlink:_RestorePresentation()
    self:_ReleaseProtection()
    local fade_token = self.fade_token
    if fade_token ~= nil and self.inst._eva_fox_fade_token == fade_token then
        self.inst._eva_fox_fade_token = nil
        if self.inst.AnimState ~= nil and self.fade_colour ~= nil then
            self.inst.AnimState:SetMultColour(unpack(self.fade_colour))
        end
    end
    self.fade_token = nil
    self.fade_colour = nil
    local hide_token = self.hide_token
    if hide_token ~= nil then
        local owns_token = self.inst._eva_fox_hide_token == hide_token
        if owns_token then self.inst._eva_fox_hide_token = nil end
        local owns_methods = self.inst.Hide == self.hide_wrapper
            and self.inst.Show == self.show_wrapper
        if self.inst.Hide == self.hide_wrapper then self.inst.Hide = self.previous_hide end
        if self.inst.Show == self.show_wrapper then self.inst.Show = self.previous_show end
        if self.inst:IsValid() and owns_token and owns_methods
            and self.foreign_hide_count == 0 then
            self.previous_show(self.inst)
        end
        if self.inst._eva_fox_shadow_token == hide_token then
            self.inst._eva_fox_shadow_token = nil
            if self.inst.DynamicShadow ~= nil then self.inst.DynamicShadow:Enable(true) end
        end
    end
    self.hide_token = nil
    self.previous_hide, self.previous_show = nil, nil
    self.hide_wrapper, self.show_wrapper = nil, nil
    self.foreign_hide_count = 0
    self.visibility_internal = false
end

function EvaFoxBlink:_OnFireRemoved(fire)
    self.fires[fire] = nil
end

function EvaFoxBlink:_SpawnFire(x, z)
    local fire = self:_SpawnAt("eva_fox_fire_fx", x, z)
    if fire == nil or fire.Start == nil then
        RemoveEntity(fire)
        return nil
    end
    self.fires[fire] = true
    if not fire:Start(self.inst, self) then
        self.fires[fire] = nil
        RemoveEntity(fire)
        return nil
    end
    return fire
end

function EvaFoxBlink:_FinishCast(reason)
    if not self.active then return false end
    self.active = false
    self.cast_token = nil
    self.inst:RemoveTag("eva_fox_casting")
    for key, task in pairs(self.tasks) do
        CancelTask(task)
        self.tasks[key] = nil
    end
    self:_RestorePresentation()
    self:_UnlockMovement()
    local cast_state = self.cast_state
    self.cast_state = nil
    if (reason == "finished" or reason == "destination_invalid")
        and self.inst.sg ~= nil and self.inst.sg.currentstate == cast_state
        and self.inst.sg.GoToState ~= nil then
        self.inst.sg:GoToState("idle")
    end
    return true, reason
end

function EvaFoxBlink:CastAt(x, z)
    if self.active then return false, "active" end
    local remaining = self:GetCooldownRemaining()
    if remaining > 0 then
        self:_Say("Hồ Ảnh hồi sau " .. tostring(math.ceil(remaining)) .. " giây.")
        return false, "cooldown"
    end
    if not Common.CanActivate(self.inst) then return false, "invalid_state" end
    local origin_x, _, origin_z = self.inst.Transform:GetWorldPosition()
    local valid, reason = Common.ValidateDestination(self.inst, x, z, origin_x, origin_z)
    if not valid then return false, reason end

    self.active = true
    self.cast_token = {}
    self.cast_state = self.inst.sg ~= nil and self.inst.sg.currentstate or nil
    self.cooldown_end = GetTime() + Common.COOLDOWN
    self.inst:AddTag("eva_fox_casting")
    self:_LockMovement()
    self:_StartFade()
    self:_Schedule("hide", Common.FADE_TIME, function() self:_Hide() end)
    self:_Schedule("fox", 1.4, function()
        local px, _, pz = self.inst.Transform:GetWorldPosition()
        self:_SpawnAt("eva_fox_depart_fx", px, pz)
    end)
    self:_Schedule("teleport", Common.TELEPORT_TIME, function()
        if not Common.CanContinueCast(self.inst) then self:Stop("interrupted"); return end
        local ok = Common.ValidateDestination(self.inst, x, z, origin_x, origin_z)
        if not ok then self:Stop("destination_invalid"); return end
        self.inst.Physics:Teleport(x, 0, z)
        self:_SpawnAt("eva_fox_arrive_fx", x, z)
    end)
    self:_Schedule("restore", Common.RESTORE_TIME, function()
        self:_RestorePresentation()
        self:_SpawnFire(x, z)
    end)
    self:_Schedule("finish", Common.FINISH_TIME, function() self:_FinishCast("finished") end)
    self:_Say("Hồ Ảnh!")
    return true, "cast"
end

function EvaFoxBlink:Stop(reason)
    local changed = self:_FinishCast(reason)
    for fire in pairs(self.fires) do
        RemoveEntity(fire)
        self.fires[fire] = nil
        changed = true
    end
    return changed == true, reason
end

function EvaFoxBlink:OnSave()
    local remaining = self:GetCooldownRemaining()
    return remaining > 0 and {cooldown = remaining} or nil
end

function EvaFoxBlink:OnLoad(data)
    self:Stop("load")
    local remaining = data ~= nil and tonumber(data.cooldown) or 0
    if not Common.IsFiniteNumber(remaining) then remaining = 0 end
    self.cooldown_end = GetTime()
        + math.max(0, math.min(Common.COOLDOWN, remaining or 0))
end

function EvaFoxBlink:OnRemoveFromEntity()
    self:Stop("component_removed")
    self.inst:RemoveEventCallback("death", self._ondeath)
    self.inst:RemoveEventCallback("ms_becameghost", self._onghost)
    self.inst:RemoveEventCallback("onremove", self._onremove)
    self.inst:RemoveEventCallback("newstate", self._onnewstate)
end

return EvaFoxBlink
