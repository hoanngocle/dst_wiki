# Rà soát Tu Tiên Ký 0.8.4 — 19/09/2026

## Phạm vi và cách kiểm tra

Rà toàn bộ mod hiện tại và chạy bản sao bằng máy chủ DST thật, bản dựng **747465**.
Thế giới ngoại tuyến, dữ liệu lưu, bản chạy thử và log đều nằm trong
`.superpowers/dst-runtime-audit` của workspace. Không dùng save cá nhân.

## Lỗi đã sửa

1. **Lỗi nạp cấu hình:** `modinfo.lua` gọi `ipairs`, nhưng môi trường đọc metadata
   của game không cung cấp hàm này. Máy chủ thật dừng nạp với thông báo
   `attempt to call global 'ipairs' (a nil value)`. Đổi sang vòng lặp số;
   bổ sung kiểm thử nạp metadata trong môi trường hạn chế.
2. **Khởi tạo mạng của bếp:** đưa `SetPristine()` lên trước nhánh trả về máy khách
   cho cả bốn bếp, bỏ lời gọi lặp ở hai ngôi sao.
3. **Ánh sáng Thần Hỏa:** mức nhiên liệu thứ tư nay nhân đúng hệ số phạm vi sáng.
4. **Ô trang bị riêng:** giữ hình áo giáp khi đeo/tháo ba lô hoặc bùa; khôi phục
   hình món còn trang bị khi tháo áo giáp/ba lô. Sửa chỉ báo giảm nguyên liệu
   của bùa xanh ở hai giao diện chế tạo. Không gọi lại callback trang bị áo giáp.
5. **Hồi sinh cũ:** bỏ hook vào component `resurrectable` không tồn tại trong DST
   hiện tại và nhánh stategraph đi kèm; bùa đỏ giữ cơ chế ám để hồi sinh của game.

## Bằng chứng đã đạt

- Máy chủ nạp Lua, đăng ký mod, tạo thế giới, tải lại save thử nghiệm và tắt sạch
  với mã thoát 0.
- **80 thực thể và 14 biến thể skin được tạo thành công** bằng `SpawnPrefab`
  trong game thật: `TTK_SMOKE_DONE 94 0`.
- **24 công thức** được đối chiếu sản phẩm, vật đặt trước khi xây và toàn bộ
  nguyên liệu với bảng prefab thật: `TTK_RECIPES_OK 24`.
- **Trang bị trong game thật:** túi 45 ô nhận được đồ tại ô 45, stack Gỗ có giới
  hạn 120; áo giáp, ba lô và bùa xanh chiếm đúng ba ô riêng; ba lô được nhận là
  kho phụ; đeo/tháo bùa không thay hình áo giáp: `TTK_GEAR_OK`.
- Lượt chạy cuối không có lỗi Lua hoặc ca kiểm tra thất bại; mã Lua trong bản
  chạy thử trùng từng byte với bản mod giao. Log rút gọn: `tests/runtime_evidence.txt`.
- **60 cấu hình** hợp lệ trong môi trường metadata hạn chế, không trùng tên.
- **81 tệp Lua** đúng cú pháp; không thiếu đường dẫn `require`/`modimport` tĩnh.
- **64 tham chiếu texture atlas** có đích; **56 gói hoạt ảnh** không lỗi CRC.
- Kiểm thử túi 15/25/45 ô ở máy chủ/máy khách, ô ba lô và dây chuyền luôn bật,
  nguyên liệu từ ba lô, bố cục ba lô 8/40 ô, bảo toàn giao diện gốc.
- Kiểm thử sắp xếp bằng G, kho mở, ô khóa, stack vô hạn, sự kiện replica,
  tương thích máy phóng băng và cả bốn bếp.

Các bộ kiểm thử nằm trong `tools/audit_registration.py`, `tools/test_inventory45.py`,
`tools/test_vinhhang.py`, `tools/test_flingomatic.py` và `tests/test_*.lua`.
Python cần thư viện `lupa`; các kiểm thử dùng Lua 5.1.

## Giới hạn còn lại

Máy chủ không có giao diện đồ họa. Chưa xác nhận hình ảnh trên màn hình người chơi,
thao tác tay cầm, hai người chơi qua mạng hoặc mọi tình huống chiến đấu/đổi shard.
Kiểm tra tạo prefab không thay thế kiểm tra đầy đủ mọi hành vi sau nhiều ngày chơi.
Thử nghiệm chạy Tu Tiên Ký độc lập, không kết luận tương thích với mọi mod bên ngoài.

Khi dùng bản tích hợp, tắt các bản độc lập đã gộp có cùng vật phẩm hoặc chức năng,
đặc biệt Vĩnh Hằng Thần Hỏa/2422129165 và túi 45 ô/3075429483.
Các cảnh báo Steam, token và kết nối thống kê trong log của thử nghiệm ngoại tuyến
không phải lỗi đăng ký của Tu Tiên Ký. Một số lần sinh bản đồ nhỏ được game tự thử lại;
thế giới cuối đã tạo và tải lại thành công.
