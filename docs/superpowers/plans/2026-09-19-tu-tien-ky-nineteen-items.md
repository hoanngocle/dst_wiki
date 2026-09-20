# Tu Tiên Ký: đợt 18 công trình và phụ thuộc (bỏ Tinh Thối Đan Phủ)

**Yêu cầu đã duyệt:** chuyển 18 món (người dùng vừa loại `xd_xcdf` Tinh Thối Đan Phủ), mọi sản vật/vật phẩm liên quan và skin của các món đã chuyển; giữ công năng nguồn, hoạt động độc lập và tránh xung đột với Solo. Không nhập Thiên Cơ Ốc Dị Hóa, hai đèn và ba mỏ đã loại, Sa Đường; không ghi đè đợt 11 món đang triển khai.

**Nguồn:** `mods/mod_steam/3235319974`. **Đích:** `mods/TuTienKy`, web `/tu-tien-ky`. Custom prefab/component/action dùng namespace `ttk_`; bank/build nguồn được giữ trong tài nguyên. Không import Solo hoặc loader nguồn; tương thích qua API game và nhận diện component/tag tùy chọn.

## Phân công, tránh sửa trùng

- [x] Agent houses: nhóm nhà gồm `xd_zzxhcx`, `xd_lycx`, `xd_spiderden`, `xd_pog_house`, `xd_tianjiwu`, `xd_stool`. Tạo riêng `main/ttk_batch19_houses.lua`, prefab/brain/SG/phụ thuộc; xuất metadata web.
- [x] Agent herbs: `xd_ylxc`, `xd_ylxq`. Tạo riêng `main/ttk_batch19_herbs.lua` và toàn bộ linh thảo/hạt/đầu ra bắt buộc; xuất metadata web.
- [x] Parent: `xd_qljq`, `xd_sgc`, `xd_qwsk`, `xd_flower_sfr`, `xd_flower_zyh`, `xd_crc`, `xd_flower_yl`, `xd_yunxiao_portable_spicer`, `xd_wsjx`, `xd_tree_yls`. Tạo `main/ttk_batch19_misc.lua` và các prefab riêng.
- [x] Parent: nhập module sau khi ba nhóm xong; cập nhật skin, generator web, tài liệu, phiên bản theo bản mới nhất; giữ mọi thay đổi hợp lệ từ tác vụ khác.

## Tiêu chí triển khai và xác minh

- [x] Đọc nguồn thực tế: recipe/station, loot/spawn, container/action, save/load, quyền sở hữu, sản vật và skin; bảng phụ thuộc phải liệt kê cả tên ghép động.
- [x] Giữ phạm vi đèn Quỳnh Lâu là 6, intensity/falloff 0,8; chưa được yêu cầu tăng.
- [x] Kho không lấy vũ khí đã khóa/bind Solo; không giả định damage là số nếu weapon dùng hàm; không áp đặt stack lên vật phẩm không stack được.
- [x] Trạm gia vị phải xử lý batch nguyên liệu theo stack thật, giữ phần dư, save/load số mẻ, không tạo phần thưởng hai lần hoặc gọi doer nil.
- [x] Nhà và cơ chế linh thảo phải hoạt động với nhân vật vanilla; nếu bảo toàn nguồn bắt buộc nhập phần bị loại, báo chính xác xung đột thay vì lén nhập lại.
- [x] Lua compile, tài nguyên animation CRC/atlas, require/prefab registration, links/icons web, TypeScript và ESLint. Không tự mở game hoặc chạy test suite trái lựa chọn trước; không tuyên bố bảo đảm runtime chỉ từ kiểm tra tĩnh.
- [x] Không ZIP phát hành, commit/push/deploy hoặc sửa mod nguồn. Ghi kết quả thật và mọi khác biệt nguồn trong báo cáo batch.

## Bàn giao

Hoàn tất triển khai và kiểm tra tĩnh; xem `mods/TuTienKy/BATCH18_VERIFICATION_VI.md`. Chưa xác minh toàn bộ đợt trong phiên game cùng Solo.
