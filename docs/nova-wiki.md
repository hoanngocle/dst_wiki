# NOVA wiki snapshot

Nguồn chuẩn của trang `/nova` là mod đã cài tại `Don't Starve Together/mods/NOVA`, phiên bản 2.0.3. Dữ liệu phát hành nằm trong `data/generated/nova-items.json`; báo cáo kiểm kê nằm cạnh đó tại `data/generated/nova-items-report.json`.

Snapshot hiện có 298 item duy nhất. Phạm vi gồm các prefab inventory đang được provider hoạt động đăng ký, cùng item xuất hiện qua recipe, reward hoặc đăng ký virtual. Creature, FX, placer, projectile, controller nội bộ và prefab helper không thể nhặt làm item bị loại; danh sách loại trừ được ghi trong báo cáo.

Repo wiki chỉ lưu snapshot tĩnh, không chứa source runtime hoặc builder của mod. Khi NOVA thay đổi, cần kiểm kê lại thư mục mod bên ngoài rồi cập nhật snapshot và báo cáo. Metadata chỉ bổ sung tên/mô tả cho item đã có bằng chứng; không quyết định membership.

Item chưa resolve được sprite vẫn được giữ và liệt kê trong `missingSprites`; thiếu icon không phải lý do loại item khỏi wiki.
