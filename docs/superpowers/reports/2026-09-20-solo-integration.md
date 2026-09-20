# Tu Tiên Ký 0.10.0: tích hợp toàn bộ Solo Leveling

## Kết quả

TuTienKy chứa toàn bộ bản Solo Leveling 2.2.7 trong repository. Chỉ bật Tu Tiên Ký để nạp cả hai hệ thống; không có dependency vào mod Solo riêng. Gói nguồn Solo và save người dùng không bị sửa.

660 file Solo được giữ nguyên bytes và ghi lại SHA-256 trong `mods/TuTienKy/SOLO_SOURCE_MANIFEST.json`. Runtime Solo được chuyển sang `main/ttk_solo_source.lua`, worldgen sang `main/ttk_solo_worldgen.lua`. Metadata và manifest nhị phân nguồn nằm trong provenance; manifest của gói Solo cũ không được dùng cho gói kết hợp.

Bootstrap giữ prefab/asset Tu Tiên Ký trước khi nạp Solo và hợp nhất lại sau khi Solo gán các bảng của nó. Cấu hình giữ nguyên khóa, options và giá trị mặc định, chỉ thêm tiền tố nhãn `Solo:`. Tu Tiên Ký giữ tên và tăng phiên bản từ 0.9.0 lên 0.10.0.

## Bằng chứng kiểm thử

- `tools/test_ttk_solo_integration.py`: 7/7 đạt; 423 file Lua biên dịch bằng Lua 5.1. Kiểm tra source checksum, metadata sandbox, chống nạp trùng theo ID/tên mod, bootstrap một lần, asset/prefab gốc hoặc engine và texture của atlas.
- Lua hồi quy hiện có: `test_inventorysort.lua`, `test_inventory45_compat.lua`, `test_bossindicators.lua`: đạt cả ba.
- DST build 747465, server offline trong `.superpowers/ttk-solo-integration/server`, không kết nối người chơi thật. Chỉ bật TuTienKy.
- Tạo thế giới Forest có node `SoloLeveling:DungeonArena`, component `hh_world`/`dungeon_manager`, RPC Solo. Sinh `hh_daogam`, `hh_daogam2`, `hh_lo_ren`, `hh_hac_nguyet_ho`, `ttk_lucnguyenkiemdong`, `ttk_hhlmz` và linh thạch.
- Wilson có `hh_player`, `hh_leveling`, `hh_mana`, `hh_shadow_manager`, `hh_daily_quest` và túi 45 ô. Save-record roundtrip giữ cấp 7/EXP 23; đây không phải thử nghiệm đăng nhập tài khoản hoặc chuyển shard.
- `server/create.log`: `TTK_SOLO_CREATE_PASS`; `server/reload.log`: `TTK_SOLO_RELOAD_PASS`. Sau khi restart, dao Solo vẫn cường hóa cấp 3, linh thạch vẫn có 7 viên.
- `server-migration/legacy_create.log`: tạo save thật bằng bản TuTienKy 0.9.0 từ backup và SoloLeveling riêng, `TTK_SOLO_CREATE_PASS`.
- `server-migration/reload.log`: cùng save đó, chỉ bật TuTienKy 0.10.0, `TTK_SOLO_RELOAD_PASS`; arena và các vật phẩm đã lưu còn nguyên.
- Các lần chạy cuối không có `LUA ERROR`. Cảnh báo mạng Klei trong sandbox và cảnh báo build/giải phóng resource của nguồn không được coi là kiểm chứng client hoặc hiệu năng.

## Phát hiện và xử lý

- Lần worldgen đầu thất bại do guard gọi `GetModsToLoad()` cần `TheSim`. Đã đối chiếu engine và đổi sang `GetModsToLoad(true)`, cùng cách loader dùng trong worldgen; regression yêu cầu cached flag thất bại trước sửa và đạt sau sửa.
- Fixture rương ban đầu tìm theo component `named` thêm động, nhưng prefab treasurechest không tái tạo component đó khi load. Sửa harness nhận diện bằng vật phẩm trong rương; không sửa production để phục vụ test.
- Hai server thử chạy đồng thời trùng cổng mặc định do cấu hình shard tắt. Runner bổ sung `-port` riêng và phát hiện lỗi khởi động sớm. Chỉ dừng tiến trình thử nghiệm do tác vụ này tạo.
- Rà soát độc lập: không còn lỗi tích hợp material; giới hạn dungeon của save không có `dungeon_exit` được ghi rõ.

## Bảo toàn workspace và quyết định

- Backup trước sửa: `mods/backups/TuTienKy_before_solo_20260920_155105.zip` (975 file ban đầu). Không dùng worktree Git vì toàn bộ thư mục mod hiện là dữ liệu untracked; worktree mới sẽ thiếu nguồn đang được chỉnh.
- Trong lúc chạy có thay đổi ngoài tác vụ tích hợp ở `scripts/prefabs/ttk_zcmj.lua`, `scripts/ttk_skin_data.lua`, `scripts/ttk_skins.lua`, `skins_manifest.json`, `tools/test_armor_set.py`, `tools/test_owned_skins_runtime.py`. Đã giữ nguyên, không hoàn nguyên về backup. Hash quan sát nằm trong `.superpowers/ttk-solo-integration/concurrent_changes.json`; bản kiểm thử migration cuối dùng thư mục TuTienKy hiện hành.
- Giữ các ID/khóa dữ liệu gốc thay vì đổi toàn bộ namespace, để bảo toàn serialization và giảm phạm vi thay đổi. Cấu hình riêng trong modindex Solo cũ cần người dùng đặt lại ở TuTienKy vì không có cấu hình thực tế được cung cấp.
- SoloCombatHUD giữ là tiện ích độc lập tùy chọn theo spec đã duyệt. UI đi kèm Solo Leveling được gộp đầy đủ.

## Giới hạn và bàn giao

Chưa kiểm tra client đồ họa, multiplayer, Master–Caves, mọi kỹ năng hoặc save tài khoản thật. Save mẫu migration xác nhận arena và vật phẩm; không suy rộng thành bảo đảm mọi dạng save. Thế giới cũ không có đấu trường không được sửa địa hình tự động.

Gói cuối: `mods/dist/TuTienKy_v0.10.0.zip`, một thư mục gốc `TuTienKy`. Hướng dẫn người dùng: `mods/TuTienKy/SOLO_INTEGRATION_VI.md`. ZIP được kiểm tra CRC và đối chiếu nội dung từng file với thư mục nguồn sau đóng gói.

Release verification: 1659 files, 139088480 bytes. SHA-256: 7ab513c6446be0832fdd397b740e38b985bcd5717328b7459603828246472db3
