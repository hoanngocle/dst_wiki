local Screen = require("widgets/screen")
local Widget = require("widgets/widget")
local Image = require("widgets/image")
local Text = require("widgets/text")
local TextButton = require("widgets/textbutton")
local Controller = require("ui/ttk_unified_controller")
local Registry = require("ui/ttk_unified_registry")
local NativeBridge = require("ui/ttk_native_bridge")
local NativeInput = require("ui/ttk_native_input")
local Theme = require("widgets/hh_ui/ttk_unified_theme")

local TABS = {
    { id = "character", label = "Nhân vật" },
    { id = "equipment", label = "Trang bị" },
    { id = "quests", label = "Nhiệm vụ" },
    { id = "army", label = "Quân đoàn" },
    { id = "shop", label = "Cửa hàng" },
    { id = "storage", label = "Kho" },
}

local function Tint(image, colour)
    image:SetTint(unpack(colour))
end

local function AddRect(parent, width, height, x, y, colour)
    local image = parent:AddChild(Image("images/global.xml", "square.tex"))
    image:SetSize(width, height)
    image:SetPosition(x or 0, y or 0, 0)
    Tint(image, colour)
    return image
end

local function Embedded(child)
    return {
        child = child,
        ShowPanel = function(self)
            self.child:Show()
            if self.child.ShowPanel ~= nil then self.child:ShowPanel() end
        end,
        HidePanel = function(self)
            if self.child.HidePanel ~= nil then self.child:HidePanel() end
            self.child:Hide()
        end,
        DisposePanel = function(self)
            if self.child.DisposePanel ~= nil then self.child:DisposePanel() else self.child:Kill() end
        end,
    }
end

local function CreateNativePanel(owner, shell, panel_id, modes)
    local NativePanel = require("widgets/hh_ui/ttk_native_panel")
    return shell.content_root:AddChild(NativePanel(owner, shell, panel_id, modes))
end

local function DefaultFactories(owner, shell)
    return {
        character = function()
            local UI = require("widgets/hh_status_ui")
            local child = shell.content_root:AddChild(UI(owner, nil, {
                embedded = true,
                content_mode = "character",
                select_tab = function(id) shell:SelectTab(id) end,
            }))
            return Embedded(child)
        end,
        equipment = function()
            return CreateNativePanel(owner, shell, "equipment", {
                {
                    id = "summary", label = "Tổng Hợp", prefab = "hh_ui_container",
                    open = function(_, request_id)
                        SendModRPCToServer(MOD_RPC.hh_rpc.hh_ui_container, "ui_container", request_id)
                    end,
                },
                {
                    id = "forge", label = "Thần Binh Phổ", prefab = "hh_forge_container",
                    open = function(_, request_id)
                        SendModRPCToServer(MOD_RPC.hh_rpc.hh_ui_container, "forge_container", request_id)
                    end,
                },
            })
        end,
        quests = function()
            local UI = require("widgets/hh_ui/ttk_quest_panel")
            return shell.content_root:AddChild(UI(owner))
        end,
        army = function()
            local UI = require("screens/hh_shadow_upgrade_screen")
            return Embedded(shell.content_root:AddChild(UI(owner, { embedded = true })))
        end,
        shop = function()
            local ShopDefs = require("dungeon_shop/hh_dungeon_shop_defs")
            local UI = require("screens/hh_dungeon_shop_screen")
            return Embedded(shell.content_root:AddChild(UI(owner, ShopDefs, nil, { embedded = true })))
        end,
        storage = function()
            return CreateNativePanel(owner, shell, "storage", {
                {
                    id = "storage", label = "Kho Quân Vương", prefab = "hh_monarch_storage_container",
                    waiting = "Đang mở Kho Quân Vương theo quyền sở hữu hiện tại…",
                    open = function(_, request_id)
                        SendModRPCToServer(MOD_RPC.hh_rpc.hh_monarch_storage_open, request_id)
                    end,
                },
            })
        end,
    }
end

local TTKUnifiedScreen = Class(Screen, function(self, owner, options)
    Screen._ctor(self, "TTKUnifiedScreen")
    options = options or {}
    self.owner = owner
    self.tab_order = TABS
    self.active_tab = nil
    self.native_token = nil
    self.native_widget = nil
    self.closed = false

    self.root = self:AddChild(Widget("ttk_unified_root"))
    self.root:SetScaleMode(SCALEMODE_PROPORTIONAL)
    self.root:SetHAnchor(ANCHOR_MIDDLE)
    self.root:SetVAnchor(ANCHOR_MIDDLE)
    self.root:SetScale(Theme.shell.scale)

    AddRect(self.root, Theme.shell.width, Theme.shell.height, 0, 0, Theme.colours.backdrop)
    AddRect(self.root, Theme.shell.width - 18, Theme.shell.height - 18, 0, 0, Theme.colours.silver_dim)
    AddRect(self.root, Theme.shell.width - 26, Theme.shell.height - 26, 0, 0, Theme.colours.panel)
    AddRect(self.root, Theme.content.width + 12, Theme.content.height + 12, 0, Theme.content.y, Theme.colours.silver_dim)
    AddRect(self.root, Theme.content.width, Theme.content.height, 0, Theme.content.y, Theme.colours.backdrop)

    self.title = self.root:AddChild(Text(Theme.font, 38, "PHÀM NHÂN TU TIÊN"))
    self.title:SetPosition(0, 377, 0)
    self.title:SetColour(unpack(Theme.colours.silver))

    self.content_root = self.root:AddChild(Widget("ttk_unified_content"))
    self.content_root:SetPosition(0, Theme.content.y, 1)

    self.close_button = self.root:AddChild(TextButton())
    self.close_button:SetPosition(685, 377, 2)
    self.close_button:SetFont(Theme.font)
    self.close_button:SetTextSize(24)
    self.close_button:SetText("Đóng")
    self.close_button:SetTextColour(unpack(Theme.colours.text))
    self.close_button:SetTextFocusColour(unpack(Theme.colours.purple_soft))
    self.close_button.text:SetRegionSize(90, 40)
    self.close_button:SetOnClick(function() self:Close() end)

    self.tab_buttons = {}
    for index, tab in ipairs(TABS) do
        local button = self.root:AddChild(TextButton())
        button:SetPosition(-575 + (index - 1) * 230, 322, 2)
        button:SetFont(Theme.font)
        button:SetTextSize(25)
        button:SetText(tab.label)
        button:SetTextColour(unpack(Theme.colours.text))
        button:SetTextFocusColour(unpack(Theme.colours.purple_soft))
        button:SetTextSelectedColour(unpack(Theme.colours.purple_soft))
        button.text:SetRegionSize(220, 48)
        button:SetOnClick(function() self:SelectTab(tab.id) end)
        self.tab_buttons[index] = button
    end
    for index, button in ipairs(self.tab_buttons) do
        if self.tab_buttons[index - 1] ~= nil then
            button:SetFocusChangeDir(MOVE_LEFT, self.tab_buttons[index - 1])
        end
        if self.tab_buttons[index + 1] ~= nil then
            button:SetFocusChangeDir(MOVE_RIGHT, self.tab_buttons[index + 1])
        end
    end
    self.default_focus = self.tab_buttons[1]

    local factories = options.factories or DefaultFactories(owner, self)
    self.controller = Controller(factories)
    Registry.Set(owner, self)
    self:SelectTab(options.initial_tab or "character")
end)

function TTKUnifiedScreen:SelectTab(id)
    if self.closed or id == self.active_tab then return false end
    self.controller:CloseNative()
    self.native_token = nil
    local previous_tab = self.active_tab
    self.active_tab = id
    if not self.controller:Show(id) then
        self.active_tab = previous_tab
        return false
    end
    for index, tab in ipairs(self.tab_order) do
        self.tab_buttons[index]:SetTextColour(unpack(tab.id == id and Theme.colours.purple_soft or Theme.colours.text))
    end
    return true
end

function TTKUnifiedScreen:BeginNativeOpen(panel_id, prefab)
    local should_send, request_id = Registry.BeginNative(self.owner, self, prefab)
    if not should_send then
        self.native_token = nil
        self.controller:CancelNativeOpen()
        return false
    end
    self.native_token = self.controller:BeginNativeOpen(panel_id, prefab)
    return true, request_id
end

function TTKUnifiedScreen:CancelNativeOpen()
    self.native_token = nil
    self.controller:CancelNativeOpen()
    return Registry.CancelNative(self.owner, self)
end

function TTKUnifiedScreen:WantsNativeContainer(prefab)
    return self.controller:AcceptNativeOpen(self.native_token, self.active_tab, prefab)
end

function TTKUnifiedScreen:RejectNativeContainer(prefab)
    local resolved, queued_screen = Registry.ResolveNative(self.owner, self, prefab)
    local rejected = NativeBridge.Reject(prefab)
    if resolved and rejected and queued_screen ~= nil
        and queued_screen == Registry.Get(self.owner)
        and queued_screen.OnNativeRequestResolved ~= nil then
        queued_screen:OnNativeRequestResolved(prefab)
    end
    return rejected
end

function TTKUnifiedScreen:OnNativeRequestResolved(prefab)
    local panel = self.controller ~= nil and self.controller.active_panel or nil
    if panel ~= nil and panel.OnNativeRequestResolved ~= nil then
        return panel:OnNativeRequestResolved(prefab)
    end
    return false
end

function TTKUnifiedScreen:HandleNativeOpenFailure(prefab, request_id, reason)
    local resolved, target_screen = Registry.FailNative(self.owner, prefab, request_id)
    if not resolved then return false end
    if target_screen == Registry.Get(self.owner) and target_screen.OnNativeOpenFailed ~= nil then
        target_screen:OnNativeOpenFailed(prefab, reason)
    end
    return true
end

function TTKUnifiedScreen:OnNativeOpenFailed(prefab, reason)
    self.native_token = nil
    self.controller:CancelNativeOpen()
    local panel = self.controller.active_panel
    if panel ~= nil and panel.OnNativeOpenFailed ~= nil then
        return panel:OnNativeOpenFailed(prefab, reason)
    end
    return false
end

function TTKUnifiedScreen:AttachNativeContainer(widget, prefab)
    if not self:WantsNativeContainer(prefab) then
        return false
    end
    Registry.ResolveNative(self.owner, self, prefab)

    local old_parent = widget.GetParent ~= nil and widget:GetParent() or widget.parent
    if old_parent ~= nil and old_parent ~= self.content_root and old_parent.RemoveChild ~= nil then
        old_parent:RemoveChild(widget)
    end
    local current_parent = widget.GetParent ~= nil and widget:GetParent() or widget.parent
    if current_parent ~= self.content_root then
        self.content_root:AddChild(widget)
    end
    widget:SetHAnchor(ANCHOR_MIDDLE)
    widget:SetVAnchor(ANCHOR_MIDDLE)
    widget:SetScaleMode(SCALEMODE_PROPORTIONAL)
    local scale = prefab == "hh_monarch_storage_container" and .69 or .88
    widget:SetScale(scale, scale, 1)
    widget:SetPosition(0, prefab == "hh_monarch_storage_container" and -30 or -18, 5)
    widget:Show()
    widget:MoveToFront()
    self.native_widget = widget

    local panel = self.controller.active_panel
    if panel ~= nil and panel.AttachNative ~= nil then
        panel:AttachNative(widget)
        if panel.MoveToFront ~= nil then panel:MoveToFront() end
    end
    self.controller:SetNativeCloser(function()
        if widget ~= nil and widget.isopen ~= false and widget.Close ~= nil then widget:Close() end
        if prefab == "hh_monarch_storage_container" then
            SendModRPCToServer(MOD_RPC.hh_rpc.hh_monarch_storage_close)
        elseif prefab == "hh_forge_container" then
            SendModRPCToServer(MOD_RPC.hh_rpc.hh_ui_container, "forge_container")
        else
            SendModRPCToServer(MOD_RPC.hh_rpc.hh_ui_container)
        end
    end)
    return true
end

function TTKUnifiedScreen:DetachNativeContainer(widget)
    if self.native_widget ~= widget then return false end
    self.native_widget = nil
    self.native_token = nil
    self.controller:NativeClosed()
    local panel = self.controller.active_panel
    if panel ~= nil and panel.DetachNative ~= nil then panel:DetachNative(widget) end
    return true
end

function TTKUnifiedScreen:CloseNative()
    return self.controller:CloseNative()
end

function TTKUnifiedScreen:Close()
    if self.closed then return end
    self.closed = true
    self:CancelNativeOpen()
    TheFrontEnd:PopScreen(self)
end

function TTKUnifiedScreen:OnDestroy()
    Registry.Clear(self.owner, self)
    if self.controller ~= nil then self.controller:Dispose() end
    TTKUnifiedScreen._base.OnDestroy(self)
end

function TTKUnifiedScreen:OnControl(control, down)
    if self.native_widget ~= nil and (self.active_tab == "equipment" or self.active_tab == "storage")
        and NativeInput.IsControlInputAllowed(self.owner, control) then
        return NativeInput.ForwardControl(self.owner, control, down)
    end
    if TTKUnifiedScreen._base.OnControl(self, control, down) then return true end
    if not down and control == CONTROL_CANCEL then
        self:Close()
        return true
    end
end

function TTKUnifiedScreen:OnMouseButton(button, down, x, y)
    if self.native_widget ~= nil and (self.active_tab == "equipment" or self.active_tab == "storage")
        and NativeInput.IsMouseInputAllowed(self.owner) then
        return NativeInput.ForwardMouse(self.owner, button, down, x, y)
    end
    if TTKUnifiedScreen._base.OnMouseButton(self, button, down, x, y) then return true end
    return false
end

function TTKUnifiedScreen:GetHelpText()
    return string.format("%s Đóng", TheInput:GetLocalizedControl(TheInput:GetControllerID(), CONTROL_CANCEL))
end

return TTKUnifiedScreen
