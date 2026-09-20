name = "EVA"
description = [[
EVA — Linh Hồn Tử Sắc, nhân vật mới với lưỡi hái tím bạc và Hồn Lực.
Một ngoại hình mặc định, không có skin riêng. Chỉ dùng cho world mới.
Cấp EVA lấy từ Achievement & Level, mở kỹ năng ở cấp 1/10/20/30/50/100.
Khởi đầu 100 Hồn Lực; mỗi cấp tăng sức chứa 6, tối đa 1000 ở cấp 151.
Từ cấp 101 hồi 1 Hồn Lực mỗi giây; khi chết mất 90% Hồn Lực.

Sinh Chi Hoa: cấp 10, tốn 10 Hồn Lực, tồn tại 15 giây, hồi 60 giây; tấn công, hồi máu và tạo khiên.
Tử Phong Tụ Linh: cấp 20, tốn 3 Hồn Lực, xoáy thu hoạch/gom đồ 7 giây, hồi 10 giây.
Tinh Vũ Nguyệt Dực: cấp 30, bật tốn 100 Hồn Lực, tăng tốc 8% và đi trên biển; không hao duy trì.
Dạ Du: cấp 50, tốn 5 Hồn Lực, khiến mục tiêu chịu thêm 10% sát thương trong 5 giây, hồi 15 giây.
Trảm Linh: cấp 100, tốn 100 Hồn Lực, triệu hồi trận năm lưỡi hái, hồi 60 giây.
Hồ Ảnh: có từ cấp 1, chuột phải lên đất trống để dịch chuyển tối đa 20 đơn vị, miễn phí, hồi 12 giây.
Nội tại: mỗi hai đòn cận chiến bằng vũ khí trúng hợp lệ phóng kiếm khí cơ sở 50 sát thương.
Bấm pháp ấn để mở/đóng năm biểu tượng kỹ năng; phím G/H/J là lối tắt tùy chọn.
]]

author = "ZeroRyuk"
version = "1.2.1"
api_version = 10

dst_compatible = true
dont_starve_compatible = false
reign_of_giants_compatible = false
shipwrecked_compatible = false
all_clients_require_mod = true

icon_atlas = "modicon.xml"
icon = "modicon.tex"
server_filter_tags = {"character", "EVA", "Sinh Chi Hoa", "Hồ Ảnh"}

local function Title(title)
    return {
        name = title,
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

configuration_options = {
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
