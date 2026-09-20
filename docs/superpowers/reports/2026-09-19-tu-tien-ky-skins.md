# Tu Tiên Ký 0.1.1 — chọn skin khi chế tạo

## Yêu cầu và phạm vi

Tích hợp các skin có sẵn của Hoàng Hoa Lê Mộc Trác vào bộ chọn skin ở công thức chế tạo của game. Giữ nguyên công thức, 8 ô đồ ăn, bảo quản, nâng cấp rương và hệ linh thạch của 0.1.0. Bản nguồn làm việc là `mods/mod_steam`; mod xuất ra là `mods/TuTienKy`. Không sửa bản Workshop đang cài trong Steam.

## Tài nguyên đã xác định

- `3773896514` tự khai báo là Unlock Skin 1.1 và không có thư mục hình ảnh/hoạt ảnh; không sao chép hoặc chạy loader của mod này.
- Bản Tu Tiên gốc `3235319974` có đầy đủ hai bộ tài nguyên `xd_hhlmz_skins_htjc` và `xd_hhlmz_skins_wfz`.
- Mỗi bộ có animation ZIP và inventory atlas XML/TEX. Đọc trực tiếp `anim.bin`/`build.bin` xác nhận bank/build là tên riêng của skin, có animation `idle` và các symbol thức ăn.
- Tên prefab/đường dẫn mới dùng `ttk_hhlmz_skins_*`; tên bank/build nhúng trong tài nguyên giữ nguyên `xd_hhlmz_skins_*`.
- Nhãn giao diện dùng “Mẫu HTJC” và “Mẫu WFZ”; chưa xác minh bản dịch tên skin gốc.

## Thiết kế tích hợp

1. Đăng ký đúng hai prefab skin, danh sách `PREFAB_SKINS` và bảng chỉ số tương ứng cho `ttk_hhlmz`.
2. Bộ chọn skin có sẵn của DST đọc danh sách này và truyền skin qua luồng chế tạo chuẩn. Không thêm công thức trùng lặp hoặc RPC riêng.
3. Chỉ cấp khả năng sử dụng cho hai skin cục bộ của Tu Tiên Ký; các truy vấn skin khác chuyển tiếp tới hàm đã tồn tại.
4. Khi áp skin, đổi cả bank và build. Mẫu mặc định khôi phục cả hai về `xd_hhlmz`.
5. Áp dụng cùng skin cho hình xem trước khi đặt bàn. Luồng lưu game chuẩn lưu `skinname` và `skin_id`, rồi đưa lại vào `SpawnPrefab` khi tải.
6. Đóng gói đầy đủ tài nguyên vào bản 0.1.1; host, client, Master và Caves cần cùng phiên bản.

## Căn cứ rà mã

Đọc bản game đã cài trong `data/databundles/scripts.zip`: `widgets/redux/craftingmenu_skinselector.lua`, `components/playercontroller.lua`, `components/builder.lua`, `networking.lua`, `prefabskin.lua`, `skinsutils.lua`, `entityscript.lua`, `mainfunctions.lua`. Đối chiếu cơ chế skin tùy chỉnh với `scripts/main/xd_pi.lua` của bản Tu Tiên được sao chép.

## Giới hạn xác nhận

Không chạy test suite hoặc mở game theo yêu cầu người dùng. Việc rà mã và kiểm tra cấu trúc, tài nguyên, CRC của ZIP không thay thế việc xác nhận giao diện, multiplayer và save/load trong game. Không tuyên bố đã thử thành công những luồng đó. Bộ chọn skin tuân theo khả năng hỗ trợ skin offline của game.

## Gói bàn giao

- ZIP: `mods/dist/TuTienKy_v0.1.1.zip`
- 34 file, trong đó 11 file Lua; dung lượng 723149 byte.
- SHA256: `a456981f6182e612083fb302f79af6a3e57817ef5060ad9ef8aa18c6cbb0576a`
- Đã đối chiếu nguyên byte tài nguyên skin với bản nguồn, tham chiếu XML, toàn bộ file trong ZIP và CRC.
- Giữ nguyên ZIP 0.1.0. Chưa compile Lua hoặc chạy game.
