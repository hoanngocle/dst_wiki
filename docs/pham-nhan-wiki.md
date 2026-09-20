# Phàm Nhân Tu Tiên — dữ liệu Wiki

- Danh mục: `/pham-nhan-tu-tien`.
- Hướng dẫn: `/pham-nhan-tu-tien/huong-dan`.
- Config: `/pham-nhan-tu-tien/config`.
- URL `/tu-tien-ky` chuyển hướng 308; giữ nguyên URL ảnh `/tu-tien-ky/icons/`.

Chạy `python tools/build_pham_nhan_wiki.py` sau khi cập nhật mod. Công cụ cần Pillow và Lua 5.1 từ gói Lupa cục bộ tại `mods/mod_steam/.fasttravel-test-runtime`.

Công cụ cập nhật danh mục hiện có (giữ nội dung của các task khác), bổ sung các bản ghi đã đối chiếu, đồng bộ skin từ `skins_manifest.json`, giải mã icon, xuất hướng dẫn từ tài liệu mod và đọc `configuration_options` bằng môi trường Lua không có I/O. `app/data/pham-nhan-config.json` lưu hash nguồn để đối chiếu. Dữ liệu này là mặc định trong mod, không đọc cấu hình máy chủ hoặc save người chơi.

Các trang dùng dữ liệu tĩnh. Sau khi chạy công cụ cần build/deploy web để công bố dữ liệu mới. Không chạy riêng công cụ cũ `build_tu_tien_ky_web.py` để làm mới toàn bộ Wiki: công cụ đó chỉ chứa danh mục nền, không bao quát các phần được bổ sung bởi những task sau.
