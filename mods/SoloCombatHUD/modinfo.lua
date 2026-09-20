name = "Solo Combat HUD"
description = "Unified overhead health bars, Epic boss phases, and authoritative damage numbers for Solo Leveling."
author = "Personal integration; DYC/Tykvesh sources credited in README"
version = "1.0.0"
priority = -20 -- load after Solo Leveling (-10), so this wrapper is outermost
api_version = 10
dst_compatible = true
client_only_mod = false
all_clients_require_mod = true
server_only_mod = false

local function toggle(label, default)
    return { label = label, options = {
        { description = "Tắt", data = false },
        { description = "Bật", data = true },
    }, default = default }
end

configuration_options = {
    { name = "BOSS_BAR", hover = "Thanh boss kiểu Epic Healthbar, gồm các mốc phase.",
      label = "Thanh máu boss", options = toggle("", true).options, default = true },
    { name = "OVERHEAD_BAR", hover = "Thanh máu trên đầu quái thường khi giao chiến.",
      label = "Thanh máu trên đầu", options = toggle("", true).options, default = true },
    { name = "HIDE_BOSS_OVERHEAD", hover = "Không vẽ thanh trên đầu nếu boss đang có thanh lớn.",
      label = "Ẩn thanh phụ của boss", options = toggle("", true).options, default = true },
    { name = "SHOW_VALUES", hover = "Hiện HP hiện tại / tối đa.",
      label = "Số HP", options = toggle("", true).options, default = true },
    { name = "DAMAGE_NUMBERS", hover = "Trắng: thường; vàng: chí mạng; xanh: xuyên giáp.",
      label = "Số sát thương", options = toggle("", true).options, default = true },
    { name = "SHOW_OTHERS", hover = "Hiện đòn của người chơi khác trong phạm vi gần.",
      label = "Sát thương đồng đội gần", options = toggle("", false).options, default = false },
}
