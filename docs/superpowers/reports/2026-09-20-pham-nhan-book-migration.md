# Phàm Nhân Tu Tiên — chuyển sách hướng dẫn sang web

- Trang đích: `/pham-nhan-tu-tien/huong-dan`.
- Dữ liệu gốc chuyển vào `app/data/pham-nhan-book.json`, 6 mục; công cụ `publish_guides()` nhập lại các mục này mỗi lần cập nhật.
- 143 đoạn chữ literal, 80 thuộc tính được tính bằng Lua từ enums hiện tại, toàn bộ MOD_INFO, UI_ITEMS, CHANCE_TEXT, UPDATE_VISION và Wiki.txt.
- Wiki giữ nguyên văn trong trường `originalText` để đối chiếu; phần hiển thị chuyển tiêu đề và bảng tỉ lệ sang Markdown, bỏ chỉ thị dựng widget/ảnh của game.
- Giữ nguyên ghi chú phiên bản cũ, kèm chú thích nhận diện để không trình bày phím cũ như thiết lập hiện tại.
- Đã xóa `scripts/widgets/hh_help_ui.lua`, `Wiki.txt` và đoạn đọc Wiki trong `main/ttk_solo_source.lua`. Icon/khởi tạo sách đã gỡ trước đó. Các hàm khóa giao diện dùng chung vẫn tồn tại tương thích nhưng không còn mở sách.
- Sao lưu nguồn và SHA-256: `.superpowers/pham-nhan-book-migration/`.
- Kiểm chứng: nguyên văn Wiki khớp, 143 đoạn và 80 mô tả không thất lạc; chạy hàm publish thực tế giữ đủ 6 mục; Lua 5.1 parse thành công; kiểm thử component hướng dẫn thành công.
- Chưa deploy website hoặc chạy client game. Phác thảo bảng chung nằm trong `artifacts/pham-nhan-unified-ui/`; chưa triển khai UI.
