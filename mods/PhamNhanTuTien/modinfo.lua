name = "Phàm Nhân Tu Tiên"
description = "Thêm nhân vật EVA với bộ kỹ năng tím bạc và Hồn Lực (cấp từ Achievement & Level). Pháp bảo, linh thạch, công trình và 179 skin; cây hoa, linh thảo và hạt giống, chuồng nuôi và sào huyệt, kho chuyên dụng, Thiên Cơ Ốc, trạm gia vị, Truyền Tống Trận và Vĩnh Hằng Thần Hỏa. Tích hợp đầy đủ Solo Leveling cùng HUD chiến đấu: chỉ số, kỹ năng, nhiệm vụ, quân đoàn, hầm ngục, thanh máu và số sát thương."
author = "Phàm Nhân Tu Tiên; Solo Leveling: Saikuno"
version = "2.0.3"

api_version = 10
dst_compatible = true
client_only_mod = false
all_clients_require_mod = true
server_only_mod = false

configuration_options = {}

-- Thần Hỏa dùng thiết lập cố định trong main/ttk_vinhhangthanhoa.lua.

-- Solo Leveling 2.2.7 configuration (original keys and defaults).
local function SoloOptions()
local a = {
    {["description"] = "G", ["data"] = 103},
    {["description"] = "H", ["data"] = 104},
    {["description"] = "I", ["data"] = 105},
    {["description"] = "J", ["data"] = 106},
    {["description"] = "K", ["data"] = 107},
    {["description"] = "L", ["data"] = 108},
    {["description"] = "N", ["data"] = 110},
    {["description"] = "O", ["data"] = 111},
    {["description"] = "P", ["data"] = 112},
    {["description"] = "R", ["data"] = 114},
    {["description"] = "T", ["data"] = 116},
    {["description"] = "X", ["data"] = 120},
    {["description"] = "Z", ["data"] = 122},
    {["description"] = "F1", ["data"] = 282},
    {["description"] = "F2", ["data"] = 283},
    {["description"] = "F3", ["data"] = 284},
    {["description"] = "F4", ["data"] = 285},
    {["description"] = "F5", ["data"] = 286},
    {["description"] = "F6", ["data"] = 287},
    {["description"] = "F7", ["data"] = 288},
    {["description"] = "F8", ["data"] = 289},
    {["description"] = "F9", ["data"] = 290},
    {["description"] = "F10", ["data"] = 291},
    {["description"] = "F11", ["data"] = 292},
    {["description"] = "F12", ["data"] = 293}
}
local configuration_options = {
    {name = "key_config", label = "Phím Tắt", hover = "phím tắt để mở Bảng Tổng Hợp", options = a, default = 120},
    {
        name = "monster_day",
        label = "Giới Hạn",
        hover = "Giới hạn về số ngày mà lượng máu hàng ngày của quái có thể tăng lên",
        options = {
            {description = "Bật", data = false, hover = "Máu quái tăng đến giới hạn sẽ dừng"},
            {description = "Tắt", data = true, hover = "Máu quái tăng vô hạn theo thời gian"}
        },
        default = false
    },
    {
        name = "can_show_equip",
        label = "Chỉ Số",
        hover = "Hiện thông tin trang bị cho người khác thấy khi ping đồ\nPhím tắt: Shift + Alt + chuột trái",
        options = {
            {description = "Tắt", data = false, hover = ""},
            {description = "Bật", data = true, hover = "Khuyên dùng"}
        },
        default = true
    },
}

return configuration_options
end
local solo_options = SoloOptions()
for i = 1, #solo_options do
    local option = solo_options[i]
    option.label = "Solo: " .. option.label
    configuration_options[#configuration_options + 1] = option
end



-- Cấu hình nhân vật EVA.
local function EvaOptions()
local function Title(title)
    return {
        name = "eva_section_" .. title,
        hover = "",
        options = {{description = "", data = 0}},
        default = 0,
    }
end

local function NumberOptions(values, default)
    local options = {}
    for index = 1, #values do
        local value = values[index]
        local description = "" .. value
        if value == default then description = description .. " (Mặc định)" end
        options[#options + 1] = {description = description, data = value}
    end
    return options
end

local function MultiplierOptions()
    local values = {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
        1, 1.1, 1.25, 1.5, 1.75, 2, 3, 4, 5}
    local options = NumberOptions(values, 1)
    for index = 1, #options do
        options[index].description = "x" .. options[index].description
    end
    return options
end

local stat_values = {50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 666}

local configuration_options = {
    Title("Chỉ số EVA"),
    {
        name = "eva_health",
        label = "Máu 󰀍",
        hover = "Máu tối đa của EVA.",
        options = NumberOptions(stat_values, 125),
        default = 125,
    },
    {
        name = "eva_hunger",
        label = "Độ no 󰀎",
        hover = "Độ no tối đa của EVA.",
        options = NumberOptions(stat_values, 125),
        default = 125,
    },
    {
        name = "eva_sanity",
        label = "Tinh thần 󰀓",
        hover = "Tinh thần tối đa của EVA.",
        options = NumberOptions(stat_values, 200),
        default = 200,
    },
    {
        name = "eva_hunger_rate",
        label = "Tốc độ tiêu hao độ no",
        hover = "Hệ số tiêu hao độ no của EVA.",
        options = MultiplierOptions(),
        default = 1,
    },
    {
        name = "eva_speed",
        label = "Tốc độ di chuyển",
        hover = "Hệ số tốc độ di chuyển của EVA.",
        options = MultiplierOptions(),
        default = 1,
    },
    {
        name = "eva_dmg",
        label = "Hệ số sát thương",
        hover = "Hệ số sát thương đòn đánh thường của EVA. Sinh Chi Hoa dùng sát thương cơ sở ghi trong kỹ năng.",
        options = MultiplierOptions(),
        default = 1,
    },

    Title("Sinh Chi Hoa"),
    {
        name = "eva_life_key",
        label = "Phím Sinh Chi Hoa",
        hover = "Phím dùng Sinh Chi Hoa. Vào lại world sau khi đổi phím.",
        options = {
            {description = "Tắt", data = 0},
            {description = "G (Mặc định)", data = 103},
            {description = "H", data = 104},
            {description = "J", data = 106},
            {description = "K", data = 107},
            {description = "L", data = 108},
        },
        default = 103,
    },

    Title("Tinh Vũ Nguyệt Dực"),
    {
        name = "eva_wings_key",
        label = "Phím Tinh Vũ Nguyệt Dực",
        hover = "Bật/tắt Tinh Vũ Nguyệt Dực. Bật tốn 100 Hồn Lực, không hao duy trì. Nếu trùng phím, ưu tiên Sinh Chi Hoa.",
        options = {
            {description = "Tắt", data = 0},
            {description = "G", data = 103},
            {description = "H (Mặc định)", data = 104},
            {description = "J", data = 106},
            {description = "K", data = 107},
            {description = "L", data = 108},
        },
        default = 104,
    },

    Title("Huyền Thiên Trảm Linh Kiếm"),
    {
        name = "eva_scythe_array_key",
        label = "Phím Trảm Linh",
        hover = "Trảm Linh cấp 100 tại con trỏ: tốn 100 Hồn Lực, hồi 60 giây. Nếu trùng phím, ưu tiên Sinh Chi Hoa và cánh.",
        options = {
            {description = "Tắt", data = 0},
            {description = "G", data = 103},
            {description = "H", data = 104},
            {description = "J (Mặc định)", data = 106},
            {description = "K", data = 107},
            {description = "L", data = 108},
        },
        default = 106,
    },

    Title("Lưỡi Hái EVA"),
    {
        name = "eva_scythe_dmg",
        label = "Sát thương lưỡi hái",
        hover = "Sát thương cận chiến cơ sở của lưỡi hái EVA.",
        options = {
            {description = "34", data = 34},
            {description = "51", data = 51},
            {description = "68 (Mặc định)", data = 68},
            {description = "102", data = 102},
        },
        default = 68,
    },
    {
        name = "eva_scythe_recipe",
        label = "Công thức lưỡi hái",
        hover = "Nguyên liệu chế tạo lưỡi hái EVA.",
        options = {
            {description = "Ít nguyên liệu", data = 0},
            {description = "Thông thường (Mặc định)", data = 1},
            {description = "Nhiều nguyên liệu", data = 2},
        },
        default = 1,
    },
    {
        name = "eva_scythe_durability",
        label = "Độ bền lưỡi hái",
        hover = "Số đòn đánh thường trước khi lưỡi hái hỏng.",
        options = NumberOptions({100, 150, 200, 300, 400, 500, 666, 700, 800, 900, 1000, 9999}, 666),
        default = 666,
    },

    Title("Hồn Lực"),
    {
        name = "eva_hud",
        label = "Khung hiển thị Hồn Lực",
        hover = "Hiện đồng hồ Hồn Lực với khung tối.",
        options = {
            {description = "Bật (Mặc định)", data = true},
            {description = "Tắt", data = false},
        },
        default = true,
    },

    Title("Ngoại hình"),
    {
        name = "eva_clothes",
        label = "Ẩn hình trang bị",
        hover = "Giữ hình váy EVA khi mặc giáp và đội mũ.",
        options = {
            {description = "Bật", data = true},
            {description = "Tắt (Mặc định)", data = false},
        },
        default = false,
    },
}

return configuration_options
end
local eva_options = EvaOptions()
for i = 1, #eva_options do
 local option = eva_options[i]
 option.label = "EVA: " .. (option.label or option.name)
 configuration_options[#configuration_options + 1] = option
end
