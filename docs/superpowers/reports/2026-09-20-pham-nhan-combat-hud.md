# Phàm Nhân Tu Tiên 2.0 — tích hợp HUD chiến đấu

## Bàn giao

HUD chiến đấu đã được đưa trực tiếp vào `mods/TuTienKy`, sau bước khởi tạo gameplay tích hợp. Người dùng bật **Phàm Nhân Tu Tiên** và tắt Solo Combat HUD, Simple Health Bar DST, Epic Healthbar riêng. Không cần mod Solo Leveling riêng. Thư mục `mods/SoloCombatHUD` được giữ làm bản tham chiếu, không bị xóa.

- Entry point: `main/ttk_combat_hud.lua`.
- Module, widget, prefab, RPC và cấu hình HUD dùng nhóm tên `ttk_hud_*` / `TTK_HUD`.
- Helper Epic dùng môi trường con, danh sách asset/prefab và bảng callback riêng trước khi hợp nhất vào mod chính. Chỉ báo hướng boss hiện có được giữ.
- HUD bật mặc định; khi bật tự tắt chữ chiến đấu cũ và phục hồi thông báo EXP/nhiệm vụ/lên cấp. Tắt HUD giữ cấu hình chữ người dùng đã chọn.
- Giữ đường dẫn TuTienKy, phiên bản 2.0 và các định danh `ttk_`/`hh_` hiện có; không chỉnh công thức sát thương hay dữ liệu save.
- Có chặn nạp trùng giữa bản tích hợp và bản HUD độc lập theo thứ tự nạp.

## Kiểm tra

- `tools/test_ttk_combat_hud.py`: 5/5 file test HUD đạt; 446 file Lua của toàn mod biên dịch được bằng Lua 5.1.
- `tools/test_ttk_solo_integration.py`: 6/7 kiểm tra đạt cả trước và sau thay đổi. Kiểm tra checksum nguồn cũ thất bại sẵn tại `anim/lo_ren.zip` (nguồn `f592b921…`, hiện tại `02fd23f5…`); không hoàn nguyên thay đổi tài nguyên không thuộc tác vụ HUD.
- `tools/run_ttk_combat_hud_smoke.py`: dùng bản sao mod và server DST offline trong `.superpowers/pham-nhan-hud-smoke`, không dùng thư mục mod/save đang chơi. Đã kiểm tra khởi động, đăng ký prefab/RPC HUD, vật phẩm `ttk_lingshi1`, component nhân vật tích hợp, gói sát thương thường 13, xuyên giáp 7, nhánh crit qua `Combat:GetAttacked` thực và gắn proxy thanh máu sau đòn đánh.
- Kiểm tra runtime bắt gói RPC phía server để xác nhận dữ liệu; không phải kiểm tra nhận gói trên client thật.
- Review độc lập: không còn lỗi tích hợp nghiêm trọng; đã sửa đọc cấu hình `false` và giữ riêng môi trường helper.

## Giới hạn đã xác định

Chưa xác nhận hình ảnh/HUD scale bằng client đồ họa, mạng nhiều người hay đồng thời Master–Caves trong tác vụ này. Kiểm tra server offline không chứng minh các phần đó. Không cài mod vào game, không xuất bản Workshop và không thay đổi save đang dùng.

## Nguồn

Kế thừa gói Solo Combat HUD trong dự án: giao diện/phase boss Epic Healthbar v102 (Tykvesh), tài nguyên và hành vi thanh máu Simple Health Bar DST 2.16 (DYC). Ghi công trong `mods/TuTienKy/CREDITS.md`.
