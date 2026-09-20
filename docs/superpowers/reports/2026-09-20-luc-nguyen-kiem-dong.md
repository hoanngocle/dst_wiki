# Báo cáo kiểm chứng Lục Nguyên Kiếm Đồng

Ngày kiểm chứng: 2026-09-20.

## Phạm vi đã triển khai

- Prefab độc lập `ttk_lucnguyenkiemdong`, sát thương nền 50, tầm 8, 1.000 lượt bắn và công thức Science Two đúng đặc tả.
- Phi tiêu chính mang snapshot sát thương đã cường hóa tại lúc phóng. Mỗi lần phóng thành công trừ đúng một lượt; phát cuối vẫn được phóng, phát đã xếp hàng sau khi cạn bị hủy.
- Bridge Solo chỉ đánh dấu crit từ đúng lời gọi `hh_player:DoAttackDamage` đang xử lý phát chính. Không suy luận từ damage và không gieo lại tỷ lệ crit.
- Loạt 1–6 kiếm chọn mẫu không lặp, mỗi kiếm bốc riêng 10–50% snapshot trước crit. Kiếm phụ gọi trực tiếp đường `GetAttacked` của mục tiêu, giữ giáp/phòng thủ và nguồn hạ gục, đồng thời chặn chính xác callback tấn công phụ, crit, godslayer và hệ số world-rank phía người đánh.
- Sáu kiếm bay theo góc tỏa ban đầu rồi đổi hướng có giới hạn về mục tiêu sống đang di chuyển. Mỗi kiếm đánh tối đa một lần; timeout 3 giây, giới hạn 30 đơn vị và dọn khi chủ/mục tiêu chết, thành ma, vào limbo hoặc bị xóa.
- Tài nguyên hình ảnh được sao chép từ Tu Tiên 19.7 với đường dẫn đóng gói riêng. Bank/build/symbol nhị phân giữ nguyên.

## Kiểm chứng tự động

- `python -X utf8 mods/TuTienKy/tools/test_lucnguyen.py` — đạt: toán loạt kiếm, chọn không lặp, damage độc lập, steering/timeout, cô lập phát bắn đồng thời và lồng nhau, crit thật qua `hh_player:DoAttackDamage` bản Solo cài sẵn ở 100%/0%, chặn proc phụ chính xác.
- `python -X utf8 mods/TuTienKy/tools/test_lucnguyen_prefab.py` — đạt: lượt đầu/cuối/cạn, một viên trong stack hồi +100 và chặn khi đầy, save/load finiteuses, snapshot damage cường hóa, đường cong lệch khỏi đường thẳng rồi hội tụ/đánh đúng một lần/dọn đủ sáu mẫu, dọn khi chủ chết, nhánh server/client và cú pháp Lua 5.1 của toàn mod.
- `python -X utf8 mods/TuTienKy/tools/test_weapon_solo.py` — đạt cả ba nhóm regression cường hóa Solo hiện có.
- `python -X utf8 mods/TuTienKy/tools/audit_registration.py` — đạt: 60 cấu hình, 182 tệp Lua không thiếu require/modimport tĩnh, 181 atlas và 158 archive animation hợp lệ.
- `python -X utf8 tools/run_lucnguyen_smoke.py` — đạt, exit 0; log `.superpowers/lucnguyen-audit/lucnguyen_smoke.log` dòng 1176 ghi `TTK_LUCNGUYEN_SMOKE_PASS`. Server nullrenderer đã nạp toàn bộ mod hiện tại và chạy phát chính bay/trúng thật, lượt 2→1→0 mà không xóa vật phẩm, Trader thật hồi +100 từ một viên, save/load và đủ sáu kiếm đánh rồi dọn.

## Giới hạn xác nhận

- Chưa mở client đồ họa và chưa xác nhận trực quan kích thước, hướng mặt, màu/trail hoặc điểm gắn tay trong game. Kiểm chứng tài nguyên chỉ gồm CRC, metadata bank/build/symbol và khởi tạo headless.
- Tương thích crit phụ thuộc chuỗi thông báo `chí mạng*` được phát đồng bộ từ `hh_player:DoAttackDamage` của Solo Leveling 2.2.7 đang cài. Nếu Solo đổi hoặc bỏ điểm phát này, vũ khí vẫn bắn bình thường nhưng loạt kiếm crit sẽ không kích hoạt cho tới khi adapter được cập nhật.
- Solo bị tắt trong server smoke; đường crit được kiểm riêng bằng chính hàm `hh_player:DoAttackDamage` của bản Solo cài sẵn ở tỷ lệ xác định 100% và 0%.
- Tiên Kiếm và Ma Kiếm dùng archive runtime thực tế do hai prefab builder nguồn triệu hồi: `xd_sword_red` và `xd_sword_mo`.

## Tệp tính năng

- `mods/TuTienKy/modmain.lua`
- `mods/TuTienKy/main/ttk_lucnguyenkiemdong.lua`
- `mods/TuTienKy/scripts/prefabs/ttk_lucnguyenkiemdong.lua`
- `mods/TuTienKy/scripts/ttk_lucnguyen_rules.lua`
- `mods/TuTienKy/scripts/ttk_lucnguyen_combat.lua`
- `mods/TuTienKy/tools/test_lucnguyen.py`
- `mods/TuTienKy/tools/test_lucnguyen_prefab.py`
- `mods/TuTienKy/tools/lucnguyen_smoke.lua`
- `mods/TuTienKy/anim/ttk_lucnguyen_weapon.zip`
- `mods/TuTienKy/anim/ttk_lucnguyen_{kim,moc,thuy,hoa,tho,loi}.zip`
- `mods/TuTienKy/images/inventoryimages/ttk_lucnguyenkiemdong.{xml,tex}`
- `tools/port_lucnguyen_assets.py`
- `tools/run_lucnguyen_smoke.py`
- `mods/TuTienKy/README_VI.md`, `mods/TuTienKy/CREDITS.md`
- `tools/build_tu_tien_ky_web.py`, `app/data/tu-tien-ky.ts`, `public/tu-tien-ky/icons/ttk_lucnguyenkiemdong.png`
