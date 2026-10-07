# Linh Giới: nhập dữ liệu và Việt hóa

- Trang: `/linh-gioi`; hỗ trợ `#sec=jingjie` và `#item=realm_system`.
- Nguồn: https://eyanhuahu.github.io/lingjie/ và https://github.com/eyanhuahu/lingjie.
- Tác giả: JinYan và BigXian. Chủ dự án xác nhận trong cuộc hội thoại rằng tác giả đã đồng ý cho sử dụng và dịch nội dung.
- Snapshot: `app/data/ling-gioi/source.json`; danh sách ảnh và SHA-256: `source-manifest.json` cùng thư mục.
- Bản dịch: `part-a.json`, `part-b.json`, `part-c.json`; ghép theo ID gốc trong `index.ts`.
- 97 mục, 13 chuyên mục, 161 ảnh được tham chiếu. Giữ cả mục nguồn đánh dấu ẩn/chưa triển khai với cảnh báo trên giao diện. Không tự tạo nội dung cho chuyên mục trống.

## Cập nhật

Tool nhập và audit nguồn được duy trì ngoài repo web. Khi cập nhật snapshot, đối chiếu bản nguồn và bản dịch theo ID; kiểm tra thay đổi trong từng bài và các số liệu theo ngữ cảnh.

Chạy `node node_modules/vitest/vitest.mjs run app/lib/ling-gioi.test.ts app/components/ling-gioi-browser.test.tsx app/components/site-header.test.tsx` để kiểm tra độ phủ, ảnh cục bộ, tìm kiếm và điều hướng.

## Những chỗ bản nguồn chưa rõ

- Dẫn Khí Đan ghi Tịch Cốc → Nhập Vi trong phần chi tiết. Bản dịch giữ nguyên, không tự thay đổi cơ chế.
- Cuồng Tông Diễm ghi giảm sát thương thêm 15 nhưng không ghi đơn vị; ví dụ bên cạnh là 20 → 17. Bản dịch không tự thêm ký hiệu phần trăm.
- Tóm tắt Sí Nham Hạt Long nói triệu hồi sau nửa trận, trong khi chi tiết nêu mỗi khi mất 10000 sinh lực. Giữ cả hai nội dung theo nguồn để đối chiếu.
- Thuật ngữ 位面 được dịch thống nhất thành “vị diện”, phân biệt với sát thương cố định.

Phạm vi quét Tailwind trong `app/globals.css` được giới hạn vào thư mục app, tránh đi theo thư mục dữ liệu mod liên kết sang Steam khiến Turbopack gặp lỗi.
