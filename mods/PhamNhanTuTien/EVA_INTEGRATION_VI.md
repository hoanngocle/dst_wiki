# Phàm Nhân Tu Tiên — tích hợp nhân vật EVA

EVA là nhân vật độc lập trong màn chọn nhân vật của Phàm Nhân 2.0.3, có một ngoại hình mặc định; không có hệ skin riêng. Dùng cho world mới theo yêu cầu người dùng. Đã bỏ hook giao diện skin, RPC đổi skin và alias shadow kế thừa. Tên prefab kỹ thuật vẫn là `eva`; `eva_none` chỉ mô tả ngoại hình mặc định của engine, không phải skin thứ hai.

## Sử dụng

- Bật Phàm Nhân; tắt bản EVA độc lập. Phàm Nhân tự nạp toàn bộ mã/tài nguyên EVA.
- EVA dùng chung cấp nhân vật `hh_leveling` đã tích hợp trong Phàm Nhân.
- Giữ toàn bộ Hồn Lực, mốc mở kỹ năng, giá kỹ năng và HUD đã duyệt. Bảng mặc định thu gọn; mở theo cấp 10/20/30/50/100. Hồ Ảnh ở chuột phải.
- Cấu hình EVA được thêm vào menu Phàm Nhân. Không thay đổi cấu hình Solo tích hợp.

## Các sửa chữa khi kiểm tra

- Cánh/Hồ Ảnh đọc `locomotor.hopping`; không gọi bắt buộc `IsHopping()` vì DST đang cài không có phương thức đó.
- Hồ Ảnh giữ action/component cũ để tương thích save nhưng nay dịch chuyển sau 0,25 giây, hồi 15 giây và gây một lần 600 sát thương cơ bản dọc đường qua pipeline Phàm Nhân. EVA không hóa cáo/ẩn hình, không sinh hoa/lửa; hiệu ứng dùng `spear_wathgrithr_lightning_lunge_fx` đã precache theo dependency nhân vật.
- Tuning chi phí cánh thống nhất 100 Hồn Lực.
- Bỏ cơ chế skin nhân vật cũ cũ và hỗ trợ alias save cũ theo yêu cầu mới.
- Bộ kiểm tra cập nhật tên Dạ Du, giá cánh và cấp mở kỹ năng để kiểm tra đúng hành vi hiện tại.

## Kiểm chứng và giới hạn

22/22 bộ kiểm tra Python/Lua đạt, gồm sát thương, Hồn Lực/cấp, sáu kỹ năng chủ động, kiếm khí, targeting, host/client giả lập, cleanup và đối chiếu một số API engine cài trên máy. 90 file runtime EVA trong Phàm Nhân khớp bản độc lập đã kiểm tra.

Chạy DST dedicated offline trong `.superpowers/eva-vietnamese/fresh-server`, dùng world kiểm thử riêng, không đụng save thật/Steam mods. Script `tools/eva_integration_smoke.lua` kiểm tra sinh EVA cùng component Phàm Nhân, trang bị lưỡi hái, 5 chiêu trên bảng, Hồ Ảnh, hai đòn đánh sinh kiếm khí, sát thương, Hồn Lực và kết thúc hiệu ứng. Chạy bằng `tools/run_eva_integration_smoke.py` ở gốc workspace.

Dedicated server không render giao diện nên kết quả không chứng minh FPS, hình ảnh trên client hay độ trễ nhiều người chơi. Các mục đó cần duyệt trực tiếp trong game. Log còn có cảnh báo tài nguyên của các phần Phàm Nhân khác; không quy chúng thành lỗi EVA và không sửa ngoài phạm vi.

Nguồn và hash tài nguyên: `provenance/eva-assets.json`. Báo cáo test chi tiết: `mods/eva-assets-work/audit-integration/verified-tests.json` ở workspace.

## Việt hóa EVA 1.2.1

Toàn bộ tên hiển thị, mô tả nhân vật/vũ khí, cấu hình và thông báo EVA dùng tiếng Việt. Bộ thoại có 3974 mục, gồm nền Việt hóa và các câu bổ sung; ghi công tại CREDITS_EVA_VI.md. Prefab, component, cấu hình và tài nguyên đã đổi sang mã eva. Đây là bản dành cho thế giới mới.

Thoại tương tác nhân vật đã được biên tập riêng cho EVA; thoại đồ vật giữ nguyên.
