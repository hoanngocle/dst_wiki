# Gộp Solo Leveling vào Tu Tiên Ký

Trạng thái: người dùng đã duyệt và yêu cầu triển khai; đã tích hợp, xem báo cáo `docs/superpowers/reports/2026-09-20-solo-integration.md`.

## Mục tiêu

Chỉ cần bật Tu Tiên Ký để sử dụng toàn bộ nội dung Solo Leveling đang có trong repository. Solo trở thành phần tích hợp mặc định, không cần cài hoặc bật một mod Solo riêng.

## Nguồn đã kiểm tra

- Đích: `mods/TuTienKy`, phiên bản 0.9.0.
- Nguồn: `mods/mod_steam/3780347550`, Solo Leveling 2.2.7, tác giả Saikuno; 660 file, khoảng 167 MB.
- Hai đường dẫn trùng hiện tại là `modmain.lua` và `modinfo.lua`.
- Solo có `modworldgenmain.lua` để tạo khu vực đấu trường/hầm ngục. Tu Tiên Ký đang có cầu nối sát thương Solo và các hệ thống túi đồ, trang bị, công trình riêng.

## Phương án

Khuyến nghị nhúng đầy đủ mã và tài nguyên Solo vào gói Tu Tiên Ký, giữ module nội bộ để dễ bảo trì nhưng chỉ công bố một mod. Chuyển entrypoint Solo thành module được bootstrap chung gọi; gộp danh sách prefab, asset và cấu hình thay vì ghi đè. Đối chiếu thứ tự đăng ký hook combat, inventory, UI và RPC để từng hệ thống chỉ được cài một lần.

Hai lựa chọn khác không phù hợp bằng: giữ Solo làm dependency vẫn bắt người dùng bật hai mod; viết lại toàn bộ Solo làm tăng rủi ro thiếu tính năng và hỏng dữ liệu mà không phục vụ mục tiêu gộp gói.

## Phạm vi chức năng

Bao gồm toàn bộ mã và tài nguyên runtime Solo: cấp độ/chỉ số, kỹ năng, nhiệm vụ, hiệp hội, quân đoàn/bóng ma, hầm ngục, boss, vật phẩm, chế tạo/cường hóa, UI, hotkey, mạng và tạo thế giới. Giữ các tính năng Tu Tiên Ký hiện tại. Bảo toàn tác giả và thông tin nguồn.

Gộp các tùy chọn Solo vào cấu hình Tu Tiên Ký, giữ giá trị mặc định gốc khi không xung đột. Kiểm tra tên cấu hình trùng trước khi chọn namespace; nếu đổi khóa phải cập nhật mọi nơi đọc khóa. Không tự chuyển giá trị cấu hình của mod cũ khi chưa có nguồn cấu hình thực tế.

`SoloCombatHUD` là một gói độc lập trong repository, không đồng nhất với Solo Leveling; phương án này gộp UI đi kèm Solo Leveling và giữ tương thích với gói HUD đó. Website không phải nội dung của bản gộp runtime này.

## Dữ liệu và tương thích

Giữ tên prefab, component, replica và khóa save hiện có của Solo. Rà soát namespace RPC, đường dẫn tài nguyên, MODROOT, kiểm tra Workshop ID và dữ liệu lưu theo modname; chuyển các phụ thuộc vào mod riêng sang gói Tu Tiên Ký. Không hứa save cũ tương thích chỉ dựa trên tên prefab: cần kiểm thử lưu/tải và xác định dữ liệu nào phụ thuộc định danh mod.

Gộp entrypoint worldgen cho thế giới mới. Không tự tái tạo hoặc ghi đè bản đồ save cũ; xác minh cơ chế hầm ngục của nguồn khi tải thế giới có sẵn và ghi rõ giới hạn nếu thiếu địa hình.

Khi phát hiện người dùng bật đồng thời Solo gốc và bản tích hợp, báo lỗi hướng dẫn tắt Solo gốc trước khi cài hook; không âm thầm chạy hai bản. Bản nguồn và save đang dùng được giữ nguyên; sao lưu gói đích trước khi tích hợp.

## Kiểm chứng và bàn giao

Kiểm kê đầy đủ file nguồn, so sánh mọi thay đổi có chủ ý; kiểm tra Lua syntax và dependency/asset. Kiểm thử bootstrap hai phía client/server, hợp nhất cấu hình/prefab/asset, RPC, hook sát thương và trang bị; kiểm tra worldgen và lưu/tải bằng công cụ runtime sẵn có nếu phù hợp. Các thử nghiệm giả lập không thay thế kiểm thử DST thật.

Bàn giao thư mục TuTienKy đã gộp, gói ZIP và hướng dẫn bật một mod, chuyển cấu hình, kiểm thử save sao chép. Báo rõ những bước đã chạy và những bước cần kiểm tra trong game; không tuyên bố multiplayer hoặc save migration đã đạt nếu chưa thực sự kiểm chứng.
