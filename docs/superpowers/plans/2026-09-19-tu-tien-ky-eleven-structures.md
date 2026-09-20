# Tu Tiên Ký — chuyển 11 món từ hai ảnh

> **For agentic workers:** Use `superpowers:executing-plans` to implement this plan task-by-task. User explicitly assigned execution to GPT-5.6; use GPT-5.6 Sol. Check off completed steps and record verification evidence. Do not request another approval for the already-authorized transfer.

**Goal:** Chuyển đủ 11 món được chọn, toàn bộ sản vật/phụ thuộc và skin của chúng vào Tu Tiên Ký; đồng bộ `/tu-tien-ky`.

**Architecture:** Dùng các factory cây/hoa, đăng ký recipe, container và skin hiện có. Tách các cơ chế đặc thù thành module `ttk_`; chuyển đủ các đầu ra cần thiết để vật phẩm hoạt động độc lập, không nạp toàn bộ mod nguồn.

**Tech Stack:** DST Lua 5.1, Python để chuyển tài nguyên/kiểm tra tĩnh, Next.js/TypeScript cho web.

**Spec:** Yêu cầu đã xác nhận trong cuộc trò chuyện: lấy sáu món còn lại ở ảnh 1, năm món ở ảnh 2; nhập skin của món được chuyển; giữ đủ sản vật/thực thể; loại hai đèn, ba mỏ và Sa Đường. Bảng dưới là phạm vi thực thi đã chốt.

## Phạm vi chính xác

| Ảnh | Tên | Nguồn | ID đích |
|---|---|---|---|
| 1 | Khô Lâu Sơn | `xd_sj_kls` | `ttk_sj_kls` |
| 1 | Lạc Thần Hoa | `xd_luoshen_hua` | `ttk_luoshen_hua` |
| 1 | Lam Sam | `xd_tree_ls` | `ttk_tree_ls` |
| 1 | Linh Bảo Sương | `xd_lbx` | `ttk_lbx` |
| 1 | Linh Bảo Tế Luyện Đài | `xd_lbjlt` | `ttk_lbjlt` |
| 1 | Linh Lan | `xd_flower_ll` | `ttk_flower_ll` |
| 2 | Lưu Quang Châu Bảo Hạp | `xd_lgzbh` | `ttk_lgzbh` |
| 2 | Mật Quán | `xd_mg` | `ttk_mg` |
| 2 | Mẫu Đơn | `xd_flower_md` | `ttk_flower_md` |
| 2 | Mộc Lê Hoa | `xd_flower_mlh` | `ttk_flower_mlh` |
| 2 | Ngân Hạnh | `xd_tree_yxs` | `ttk_tree_yxs` |

## Global Constraints

- Nguồn: `mods/mod_steam/3235319974`; đích duy nhất: `mods/TuTienKy`. Không sửa mod nguồn, Calliope Mori hoặc EVA.
- Không nhập `xd_jwtcd` (Kim Ô Đằng Thải Đăng), `xd_lyd` (Liên Diệp Đồng), `xd_rock1`, `xd_rock2`, `xd_rock3`, skin hoặc bộ sinh mỏ của chúng. Giữ các vật phẩm linh thạch hiện có.
- Sa Đường đã bị gỡ: không đăng ký lại cây/hạt/nhánh/quả, skin hoặc hiệu ứng đi nước. Đan Lô/hệ luyện đan vẫn hoãn; Linh Bảo Tế Luyện Đài là món được cho phép riêng, không được đánh đồng với Đan Lô.
- Skin: lấy tất cả skin của các món có trong Tu Tiên Ký, kèm hiệu ứng/thực thể phụ trợ. Không nhập nhân vật/công trình không liên quan chỉ để dùng skin.
- Giữ tương thích Solo tùy chọn hiện có, không `require`/`modimport` Solo; không nhập toàn bộ hệ tu luyện hoặc nhân vật nguồn.
- Giữ mọi thay đổi hiện có về túi 45 ô, ô trang bị, stack 120, sort bằng G, bếp, cổng và pháp bảo. Có thể có tác vụ khác sửa chung thư mục: đọc lại file trước khi chỉnh; không reset, ghi đè toàn bộ hoặc commit thay đổi không thuộc tác vụ.
- Không đóng gói ZIP phát hành, không tự mở game. Quyết định trước đó của người dùng là không viết/chạy test suite cho mod; thực hiện compile Lua, kiểm tra tĩnh và TypeScript/ESLint, báo rõ chưa kiểm chứng in-game/multiplayer.
- Bản gần nhất khi lập kế hoạch là 0.8.3; đọc lại version/changelog trước khi tăng phiên bản, không giảm số phiên bản.

## Review Focus

1. Mọi `SpawnPrefab`, loot, harvest, recipe output và tên prefab được ghép động đều phải có đường đăng ký và tài nguyên; không dùng prefab trống để che phụ thuộc thiếu.
2. Chuyển đổi/thu hồi công trình và save/load phải giữ inventory, quyền sở hữu, bộ đếm giới hạn, timer, skin và nâng cấp.
3. Thực thể phía client không truy cập component server; action/RPC phải kiểm tra người dùng, khoảng cách, item và điều kiện trên server.
4. Linh Bảo Sương có mô tả giới hạn ba chiếc: đọc nguồn để xác định giới hạn theo world/shard/player trước khi triển khai; không bịa cơ chế và không làm mất đồ khi tháo.
5. Đài tế luyện và hoa đặc thù phải có thao tác thực tế dùng được khi không bật nhân vật/mod gốc; nếu phụ thuộc đòi quyết định thay đổi gameplay lớn, hỏi đúng điểm đó nhưng tiếp tục chuyển các món độc lập.

## Task 1 — Lập bản đồ phụ thuộc có bằng chứng

**Files:** tạo `mods/TuTienKy/PORT_BATCH_11_VI.md`; đọc nguồn `scripts/main/{recipes,containers,components,actions,stategraph,prefabpostInit,fabao}.lua`, các prefab và component liên quan.

- [ ] Trích xuất tĩnh từng món bằng các helper trong `tools/port_ttk_buildings.py` và `tools/port_vanhonphien.py`; không chạy loader mã hóa nguồn.
- [ ] Tìm `xd_luoshen_hua` trong các file prefab chung/nhân vật; đừng kết luận thiếu chỉ vì không có file trùng tên.
- [ ] Ghi bảng cho mỗi món: file nguồn, action/cách sử dụng, recipe/trạm, điều kiện nhân vật, sản vật, loot, FX, component/replica, timer/save-load, skin. Liệt kê cả phụ thuộc tên ghép động.
- [ ] Đối chiếu prefab game chuẩn bằng archive game cục bộ: `C:/Program Files (x86)/Steam/steamapps/common/Don't Starve Together/data/databundles/scripts.zip`.
- [ ] Dữ kiện sơ bộ: `xd_lbx.lua` tạo `xd_hyf_frontfx`, `xd_hyf_fullfx`; `xd_lbjlt.lua` không khai báo hết kết quả bằng SpawnPrefab trực tiếp, phải đọc action/component/global table. `xd_trees.lua`, `xd_flowers.lua` chứa factory dùng chung.
- [ ] Với Lạc Thần Hoa không có recipe trong catalog, tìm đường tạo nguồn trước. Nếu cần recipe độc lập, chọn nguyên liệu vanilla/`ttk_lingshi*` phù hợp nguồn và ghi rõ thay đổi, không để chỉ spawn bằng console.

## Task 2 — Cây và hoa

**Files:** sửa `mods/TuTienKy/scripts/prefabs/ttk_garden.lua`, `mods/TuTienKy/main/ttk_garden.lua`, `tools/port_ttk_garden_assets.py`; tạo `scripts/prefabs/ttk_luoshen_hua.lua` nếu cơ chế hoa cần factory riêng.

- [ ] Thêm Lam Sam, Ngân Hạnh, Linh Lan, Mẫu Đơn, Mộc Lê Hoa vào factory có sẵn; tham số hóa sản vật/chế độ khí hậu theo đúng nhánh nguồn, không để mọi cây mới cùng sinh Ngọc Tím.
- [ ] Chuyển Lạc Thần Hoa cùng đường tạo, thu hoạch, hạt/hoa con/buff/FX thực sự liên quan. Tách điều kiện nhân vật nguồn thành hành vi độc lập có giải thích; không tự nhập nhân vật Lạc Thần.
- [ ] Recipe ban đầu theo ảnh/catalog: Lam Sam `livinglog×4, bluegem×2, ttk_lingshi1×1`; Ngân Hạnh `livinglog×4, orangegem×2, ttk_lingshi1×1`; Linh Lan `butterfly×2, twigs×15, ttk_lingshi1×1`; Mẫu Đơn `butterfly×2, redgem×3, ttk_lingshi1×1`; Mộc Lê Hoa `butterfly×2, greengem×1, ttk_lingshi1×1`. Trạm và sản vật xác nhận từ nguồn.
- [ ] Rà tên bank/build trong archive animation, atlas/image/minimap, recipe placer, hammer loot, chu kỳ mùa/ngày/hang và lưu dữ liệu.

## Task 3 — Ba kho

**Files:** tạo `scripts/prefabs/ttk_lbx.lua`, `ttk_lgzbh.lua`, `ttk_mg.lua` và module phụ thuộc cần thiết; sửa `main/ttk_buildings.lua`; dùng `scripts/ttk_chestupgrade.lua` khi nguồn có nâng cấp tương ứng.

- [ ] Chuyển container, slot filter, stack/preservation, trang trí và FX theo nguồn. Tên ID đích riêng; vanilla prefab giữ nguyên.
- [ ] Linh Bảo Sương: recipe `cutstone×10, boards×5, ttk_lingshi1×20`; giữ giới hạn đúng phạm vi nguồn, có khôi phục bộ đếm khi tải/phá, giữ nội dung rương.
- [ ] Lưu Quang Châu Bảo Hạp: recipe `goldnugget×10, marble×4, ttk_lingshi1×4`; đối chiếu filter đá quý và việc loại Ngọc Lấp Lánh bằng code nguồn.
- [ ] Mật Quán: recipe `butterfly×10, rocks×5, rope×2, ttk_lingshi1×10`; đối chiếu các loại mật/kẹo được chấp nhận và tác dụng bảo quản.
- [ ] Kiểm tra tương thích sorter G, stack 120 và nâng cấp kho nếu có; không thêm nâng cấp vô hạn chỉ vì kho khác có.

## Task 4 — Khô Lâu Sơn và Linh Bảo Tế Luyện Đài

**Files:** tạo `scripts/prefabs/ttk_sj_kls.lua`, `ttk_lbjlt.lua`, module `main/ttk_rituals.lua` và component/action phụ trợ có trách nhiệm rõ ràng; đăng ký qua `modmain.lua`.

- [ ] Khô Lâu Sơn: recipe `cutstone×6, boneshard×3, purplegem×1, ttk_lingshi2×1`; chuyển cơ chế thực tế trong source, toàn bộ summon/loot/entry/owner/cooldown phụ thuộc cần thiết.
- [ ] Đài tế luyện: recipe `flint×3, cutstone×6, ttk_lingshi2×1`; trích danh sách nguyên liệu, điều kiện, kết quả và xác suất từ nguồn, chuyển kết quả đó thành vật phẩm có chức năng, không chỉ icon.
- [ ] Loại coupling tới nhân vật/cultivation khi có thể thay bằng điều kiện item/action tương đương; ghi rõ mỗi thay đổi. Không tự dựng hệ tu luyện mới hoặc đem cả mod nguồn vào.
- [ ] Nếu kết quả bắt buộc là một trong các món người dùng đã loại, không lén nhập lại. Ghi xung đột và hỏi phạm vi kết quả đó, đồng thời hoàn thành các nhánh không bị chặn.
- [ ] Lưu inventory/timer/owner và chống kích hoạt lặp, tiêu nguyên liệu hai lần, gửi RPC từ xa hoặc tạo phần thưởng khi thất bại.

## Task 5 — Toàn bộ skin của 11 món mới

**Files:** sửa `tools/port_ttk_owned_item_skins.py`, `scripts/ttk_skin_data.lua`, `scripts/ttk_skins.lua`, `scripts/ttk_skin_effects.lua`, `skins_manifest.json`; tài nguyên trong `anim`, `images`.

- [ ] Mở rộng BASES trong script theo 11 ID nguồn. Kiểm tra cả tên skin/build không cùng mẫu tiền tố; ví dụ Ngân Hạnh có tài nguyên tên `xd_tree_yx_skins_jqs` và `xd_tree_yxs_skins_jqs`, cần xác nhận cặp build/skin đúng thay vì đăng ký hai bản trùng.
- [ ] Chuyển animation, atlas, texture, icon, skin init/clear và các FX/pet/buff đi kèm. Không mất 14 skin đã có.
- [ ] Thêm dữ liệu base bank/build đúng cho cây/hoa hoặc prefab đặc thù; kiểm tra đổi về mặc định và cleanup hiệu ứng cũ.
- [ ] Compile tất cả Lua và kiểm CRC/atlas trước khi xác nhận phần này hoàn thành.

## Task 6 — Web, tài liệu và bàn giao

**Files:** sửa `tools/build_tu_tien_ky_web.py`, sinh `app/data/tu-tien-ky.ts`, icons trong `public/tu-tien-ky/icons`, cập nhật `app/tu-tien-ky/page.tsx` nếu ghi số skin cố định; cập nhật README, CREDITS, CHANGELOG, modinfo và báo cáo phụ thuộc.

- [ ] Thêm 11 món, công thức, tác dụng, cách dùng, nguồn nhận, sản vật/thực thể, skin và liên kết hai chiều. Nội dung web phải mô tả bản đã port, không lấy mô tả nguồn nếu cơ chế đã đổi.
- [ ] Không hiển thị recipe/source link tới `tu_tien:xd_*` khi bản đích đã dùng `ttk_*`; mọi sản vật custom phải có trang chi tiết.
- [ ] Dùng lại GameSprite và detail sections; đọc guide Next.js cục bộ trước khi sửa giao diện: `node_modules/next/dist/docs/01-app/03-api-reference/03-file-conventions/page.md`.
- [ ] Chạy generator bằng Python cục bộ; compile Lua với `lupa.luajit21` có ở `mods/mod_steam/.fasttravel-test-runtime` theo cách `loadstring` chỉ biên dịch, không thực thi prefab.
- [ ] Kiểm tra toàn bộ tài nguyên ZIP animation bằng CRC, atlas trỏ texture có thật, imports/prefab registration và links/sprite web. Xác nhận 5 món loại trừ và toàn bộ Sa Đường không bị đăng ký lại.
- [ ] Chạy `node node_modules/typescript/bin/tsc --noEmit --incremental false` và ESLint trên file TS/TSX đã sửa. Không tự chạy test suite/game trái lựa chọn trước đó.
- [ ] Rà lại kế hoạch, đánh dấu việc đã hoàn thành, ghi rõ mọi khác biệt với nguồn và giới hạn xác minh. Báo số item phụ, skin và sản vật thực tế. Không tuyên bố runtime/multiplayer đã đạt nếu chỉ kiểm tra tĩnh.

## Cách thực thi

Thực thi trực tiếp trong workspace hiện tại vì các phần mod đang là thay đổi chưa commit; không tạo worktree từ HEAD rồi làm mất nền đã chuyển. Không tự commit/push/deploy. Người dùng đã yêu cầu lập kế hoạch rồi giao GPT-5.6 xử lý: bắt đầu thực hiện sau khi đọc kế hoạch, không dừng chỉ để hỏi lại có muốn làm hay không.
