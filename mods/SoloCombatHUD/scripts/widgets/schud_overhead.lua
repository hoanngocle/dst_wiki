local Widget = require("widgets/widget")
local Image = require("widgets/image")
local Text = require("widgets/text")

local Bar = Class(Widget, function(self, proxy)
    Widget._ctor(self, "SCHUDOverheadBar")
    self:SetClickable(false)
    self:SetScaleMode(SCALEMODE_PROPORTIONAL)
    self:SetMaxPropUpscale(MAX_HUD_SCALE)
    self:SetHAnchor(ANCHOR_LEFT)
    self:SetVAnchor(ANCHOR_BOTTOM)
    self.proxy = proxy
    self.bg = self:AddChild(Image("images/schud_overhead.xml", "dycghb_round_22.tex"))
    self.bg:SetSize(132, 18)
    self.bg:SetTint(0.08, 0.08, 0.08, 0.85)
    self.fill = self:AddChild(Image("images/schud_overhead.xml", "dycghb_round_22.tex"))
    self.text = self:AddChild(Text(NUMBERFONT, 16, ""))
    self.inst:ListenForEvent("schud_overhead_dirty", function()
        if proxy._visible:value() then self:StartUpdating() end
    end, proxy)
    self.inst:ListenForEvent("onremove", function() self:Kill() end, proxy)
    self:StartUpdating()
end)

function Bar:OnUpdate()
    local proxy = self.proxy
    if proxy == nil or not proxy:IsValid() then self:Kill() return end
    if not proxy._visible:value() then self:Hide(); self:StopUpdating(); return end
    local parent = proxy.entity:GetParent()
    if parent == nil or not parent:IsValid() then self:Hide() return end
    local epic = ThePlayer ~= nil and ThePlayer.HUD ~= nil and ThePlayer.HUD.controls ~= nil
        and ThePlayer.HUD.controls.epichealthbar or nil
    local epic_displayed = epic ~= nil and epic.target == parent and epic.shown
        and (epic.active or (type(epic.IsMoving) == "function" and epic:IsMoving()))
    if TUNING.SCHUD.HIDE_BOSS_OVERHEAD and epic_displayed then
        self:Hide()
        return
    end
    if ThePlayer == nil or parent:GetDistanceSqToInst(ThePlayer) > 1225 then self:Hide(); self:StopUpdating(); return end
    self:Show()
    local current, maximum = proxy._current:value(), math.max(1, proxy._maximum:value())
    local pct = math.max(0, math.min(1, current / maximum))
    self.fill:SetSize(math.max(1, 124 * pct), 12)
    self.fill:SetPosition(-62 + 62 * pct, 0)
    self.fill:SetTint(1 - pct * 0.7, 0.2 + pct * 0.7, 0.12, 0.95)
    self.text:SetString(TUNING.SCHUD.SHOW_VALUES and string.format("%d/%d", current, maximum) or "")
    local x, y, z = parent.Transform:GetWorldPosition()
    local sx, sy = TheSim:GetScreenPos(x, y + 2.7, z)
    local width, height = TheSim:GetScreenSize()
    if sx == nil or sy == nil or sx < -80 or sy < -80 or sx > width + 80 or sy > height + 80 then
        self:Hide()
        return
    end
    self:SetPosition(sx, sy, 0)
end

return Bar
