# Bàn giao đợt 18 công trình

Đã loại Tinh Thối Đan Phủ theo xác nhận cuối; không nhập Đan Lô để phục vụ nó. Đã nhập 18 công trình của ba ảnh, kèm sản vật, linh thảo/hạt, thú, vật liệu, hiệu ứng và skin tương ứng. Web `/tu-tien-ky` có liên kết sản vật và cách thu được.

Chi tiết hành vi và những điều chỉnh cần thiết để dùng độc lập nằm trong `BATCH19_MISC_VI.md`, `BATCH19_HERBS_VI.md` và `BATCH19_HOUSES_VI.md`. Tên tệp giữ “19” theo tên đợt ban đầu.

## Kết quả kiểm tra ngày 19/09/2026

- Biên dịch cú pháp 154 tệp Lua bằng LuaJIT (Lua 5.1): không lỗi.
- Kiểm tra CRC 143 gói animation: không lỗi; 167 atlas XML đều có texture tham chiếu.
- Đủ 18 mã công trình trong Lua và dữ liệu web; tổng skin của mod là 31.
- Các đường dẫn `modimport` tồn tại; không thấy đăng ký những prefab đã bị loại trong đợt này.
- Generator sinh 158 mục và 366 tham chiếu hỗ trợ, kiểm tra liên kết sản vật thành công.
- TypeScript `--noEmit --incremental false` và ESLint ba tệp web liên quan: đạt.

## Solo và giới hạn xác minh

Các phần mới dùng namespace riêng, không import Solo. Bộ nhặt vũ khí bỏ qua đồ có chủ hoặc buff bind của Solo; tích hợp quyền sở hữu là tùy chọn. Thiên Cơ Ốc kiểm tra cả diện tích phòng để tránh vùng bản đồ nhân tạo đã tồn tại và chuyển tiếp API bản đồ ngoài phòng của mình. Trạm gia vị dùng bảng công thức riêng, không sửa cooker chung.

Đây là kết quả kiểm tra mã và tài nguyên. Chưa chơi thử toàn bộ đợt 18 món với Solo, nhiều người chơi và save/load trong game, nên chưa thể khẳng định tuyệt đối không crash. Không tạo ZIP phát hành, commit, push hoặc deploy.
