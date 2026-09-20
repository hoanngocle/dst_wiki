# Phàm Nhân Tu Tiên 2.0 — kiểm tra tích hợp 9 boss

Ngày kiểm tra: 2026-09-20. Thư mục hoạt động: `mods/PhamNhanTuTien`.

## Kết quả kiểm tra tĩnh

- 32/32 kiểm thử boss đạt: combat, dependency/asset, thức ăn, lưu tiến độ, chỉ báo, vòng đời và giao dịch triệu hồi.
- 5/5 file kiểm thử HUD đạt; 569 file Lua biên dịch được bằng Lua 5.1.
- Manifest combat: 96 module Lua và 198 tài nguyên nguồn. Kiểm tra closure stategraph/brain, ZIP/XML và prefab chính/phụ đều đạt.
- Bộ kiểm thử tích hợp nền đạt 5/7 ở lượt cuối (trước thay đổi cấu hình đồng thời là 6/7). Check đối chiếu nguyên bản vẫn báo sai khác **có trước tác vụ boss** tại `anim/lo_ren.zip`: SHA-256 nguồn `f592b921b79d532bdbb2c4d631e9bd2c3fa7407b587bb8fe7223e1f55ff993a0`, bản hiện tại `02fd23f5a02b48812a6938f1540c393192d8fde61291789c518ab97a8197e190`. Không hoàn nguyên tài nguyên đang dùng, không sửa checksum để che kết quả này.
- Check metadata thứ hai không còn khớp bản cấu hình chuẩn cũ: `ttk_inv45_size` đã được bỏ khỏi `modinfo.lua`, trong khi `main/ttk_inventory45.lua` hiện cố định 45 ô. Thay đổi cấu hình xuất hiện đồng thời với tác vụ này; tác vụ **Mod Config** vẫn đang hoạt động. Không hoàn nguyên phần cấu hình hoặc nới assertion để làm báo cáo xanh. Đây là kết quả đối chiếu metadata, không phải lỗi khởi tạo boss; runtime dùng bản sao mod hiện tại vẫn được kiểm tra riêng.

## Runtime server

Dùng DST dedicated server build 747465 với null-renderer, một bản sao của mod và cluster offline riêng `.superpowers/pham-nhan-boss-audit/storage/audit/Cluster_BossAudit`. Không đọc/ghi save người chơi hoặc thư mục mod Steam. Server chạy ẩn và được tắt sau mỗi lượt.

Lượt tạo thế giới mới đã đạt `PHAM_NHAN_BOSS_CREATE_PASS`, exit code 0:

- Cả chín boss tự sinh trên map nhỏ, không dùng `c_spawn` hoặc ép đặt thay cho quá trình sinh tự nhiên.
- 268 prefab hỗ trợ khởi tạo và xóa được; bao gồm quái phụ, hiệu ứng, linh vật và chiến lợi phẩm.
- Đủ sáu bộ đếm 10/10; lần thứ 11 không cộng bonus; netvar chứa đúng 10. Max máu/no/tinh thần/mana và current đầy giữ đúng qua `GetSaveRecord` / `SpawnSaveRecord`, tính đến mức hao tự nhiên trong thời gian chờ.
- Chín boss vào giao chiến và tick AI; kích hoạt các kỹ năng đại diện, kiểm tra ba boss duy nhất trả đũa sau khi bị đánh.
- Sáu boss rơi chính xác một linh vật và một phù ở lần chết chính. Bạch Hổ được gọi lại bằng chính phù rơi ra, phù bị tiêu hao, boss mới đăng ký đúng và chết được lần nữa.
- Chín boss có dữ liệu HP trong save. Quái Hươu phụ bị từ chối đăng ký thành boss độc lập.
- Tử Vân chết pha đầu chuyển sang pha 2, tạo Hươu phụ; sổ vẫn ghi sống và chưa trả phần thưởng boss duy nhất.

Lượt tải lại snapshot cuối đạt `PHAM_NHAN_BOSS_RELOAD_PASS`, exit code 0:

- Tám loại đã chết giữ trạng thái chết và không có boss chính sống lại.
- Tử Vân vẫn chỉ có một cá thể chính, phục hồi pha 2 và Hươu phụ. Hạ Hươu chuyển sang pha 3 và tạo channeler; hạ channeler ghi nhận cái chết cuối cùng.
- Phép spawn HT riêng đạt `PHAM_NHAN_BOSS_HT_ASSETS_PASS`; log reload không còn cảnh báo thiếu animation/build sau khi thêm tài nguyên bị bỏ sót.

Lượt tải thế giới lần cuối đạt `PHAM_NHAN_BOSS_FINAL_RELOAD_PASS`, exit code 0:

- Sổ lưu cả chín loại ở trạng thái chết; không có cá thể boss chính sống lại.
- Xác Tử Vân không dựng lại Hươu phụ hoặc channeler.

Cả ba lệnh server chốt đều kết thúc sạch với exit code 0. Không có Lua error hoặc mod bị vô hiệu hóa trong các log chốt. Lượt create ghi hai warning build HT trước bản sửa cuối; phép spawn HT trên snapshot đã sửa trong reload xác nhận chúng đã hết. Không dùng kết quả này để tuyên bố đã kiểm tra hình ảnh/âm thanh trên client.

Các log: `.superpowers/pham-nhan-boss-audit/create.log`, `reload.log`, `final_reload.log`.

## Những lỗi đã sửa qua kiểm thử và review

- API component hậu tải dùng đúng `LoadPostPass`; phục hồi liên kết GUID và giữ trạng thái boss chết/mất thực thể.
- Không trả linh thạch trùng với hệ thưởng chung; không trả thưởng chính cho quái phụ hoặc pha hồi sinh.
- Phù chỉ đưa action vào chuột phải, giữ nguyên vật phẩm khi triệu hồi thất bại, không cho gọi trùng boss sống.
- Bộ đếm mạng dùng `net_smallbyte`, đủ miền 0–10.
- Tách bonus vĩnh viễn khỏi các lần Solo tính lại max; không đoán ý nghĩa đối số bằng giá trị số. Bảo toàn current qua thứ tự tải component khác nhau.
- DST bỏ dữ liệu hunger khi đang đầy: bổ sung save tuyệt đối cho người có bonus độ no từ linh vật; không phát sinh hồi phục lại từ dữ liệu cũ.
- Bỏ override nguồn làm mất HP của boss khi lưu. Giữ save references, trạng thái quái phụ theo pha và chặn xác boss đã trả thưởng dựng lại pha/quái phụ.
- Bổ sung stategraph nhện, callback hỗ trợ bị thiếu, namespace đúng tiền tố, danh sách đan ngẫu nhiên và tài nguyên animation/âm thanh được dùng gián tiếp.
- Các warning animation trong lượt đầu được truy đến dependency thực tế. Lượt create chốt không còn warning từ Phượng Tủy, Tử Vân hay các FX đã sửa; hai warning của HT được sửa bằng `xdswhs_tiaopi_fx.zip` và có phép spawn riêng trong lượt reload cuối để kiểm chứng.

## Giới hạn kiểm chứng

Đây là kiểm tra máy chủ và các hợp đồng Lua, không thay cho playtest toàn bộ mọi tổ hợp chiêu/giai đoạn hoặc cân bằng boss. Chưa chạy client đồ họa để xác nhận hình ảnh, âm thanh nghe được, thao tác chuột và trải nghiệm nhiều người chơi. Log `Invalid RPC sender list` phát sinh từ nhân vật giả dùng trong server offline; không dùng nó làm bằng chứng RPC trên client đã được kiểm tra.

Các cảnh báo trùng tên build từ những gói animation đã tích hợp và orphaned resources lúc tắt server vẫn hiện; không ghi nhận là lỗi Lua mới của bộ boss. Kiểm tra đồ họa thực tế còn cần client DST.

## Chạy lại

Dùng Python runtime của workspace và các lệnh:

```text
python -m unittest discover -s tools -p "test_phamnhan_boss_*.py"
python tools/test_ttk_combat_hud.py
python tools/test_ttk_solo_integration.py
python tools/run_phamnhan_boss_smoke.py --reset
python tools/run_phamnhan_boss_smoke.py --reload
python tools/run_phamnhan_boss_smoke.py --final-reload
```

Lệnh `--reset` chỉ xóa cluster audit đã kiểm tra đường dẫn. Hai lệnh sau dùng đúng thế giới audit đã lưu từ lượt trước. Chạy theo thứ tự.

Luật gameplay: `mods/PhamNhanTuTien/BOSSES_VI.md`. Toàn bộ drop, đối chiếu nguồn và công dụng còn chờ người dùng quyết định: `mods/PhamNhanTuTien/BOSS_DROPS_VI.md`.

## Cập nhật linh vật và Tàn Hồn ba linh thú — 2026-09-20

Theo yêu cầu mới, bỏ hai Da Bạch Hổ / Phượng Tủy Cổ / Kỳ Lân Nhục khỏi bảng rơi tương ứng. Giữ đúng bộ thưởng do lifecycle cấp: một Bạch Hổ Huyết Tủy / Kim Phượng Tinh Huyết / Kỳ Lân Linh Đan và một Tàn Hồn tương ứng. Không cộng thêm bộ 1+1 vào bảng loot nguồn. Các prefab món ăn, triệu hồi và tiến độ cũ giữ nguyên ID. Prefab đồ sưu tầm cũ vẫn tải được trong save, không tự chuyển đổi.

Bốn PNG nền trong suốt tạo bằng ImageGen tích hợp: Huyết Tủy và ba linh thú nhỏ. Kim Phượng Tinh Huyết dùng nguyên texture `xd_fs`; Kỳ Lân Linh Đan dùng `xd_dy_lmsqd_5`. Đã biên dịch sáu icon TEX/XML và sáu gói sprite trên đất bằng `build_boss_relic_assets.py`, kiểm tra alpha 0–255, tên atlas/build/animation, xem bản giải mã icon sau nén. Prompt và nguồn: `mods/PhamNhanTuTien/assets/source/boss_relics/README.md`.

Kiểm tra mới nhất cho thay đổi này:

- `python -m unittest discover -s tools -p "test_phamnhan_boss_*.py"`: **35/35 đạt**. Gồm kiểm tra tái tạo source loại loot cũ, trả 1+1 đúng một lần, tương thích prefab cũ và sáu bộ asset.
- `python tools/test_ttk_combat_hud.py`: **572 Lua biên dịch được**, 5/6 file test HUD đạt. File mới `tests/hud/test_hover_readability.lua` lỗi `Class` nil trong test harness; không thuộc thay đổi linh vật.
- `python tools/run_phamnhan_boss_smoke.py --reset`: **chưa chạy tới boss**. Bootstrap dừng ở `main/hh_ui.lua:1122` vì require `widgets/hh_ui/hh_forge_ui` nhưng file đã bị xóa trong công việc giao diện/công trình đang diễn ra song song. Không khôi phục file của task khác. Các lần server đạt ghi ở phần trên là kết quả trước thay đổi lần này, không dùng làm bằng chứng runtime cho asset mới.
- Chưa kiểm tra đồ họa trên client DST. Đã bổ sung kiểm tra runtime không còn rơi ba collectible cũ vào `tools/boss_smoke.lua` để chạy tiếp khi bootstrap ổn định.


## Hoàn thiện ba cặp Hắc Ám, Hươu Một Mắt và Ma Thù — 2026-09-20

- Hắc Ám Hồn Tinh dùng icon tinh thạch `images/dyc_gem_purple`; Tâm Nhĩ Hắc Ám dùng icon và animation `shadowheart` của DST.
- Băng Phách Tinh Tủy dùng mảnh băng `xd_hxyp`; Hồn Phách triệu hồi dùng `xd_sudaji_soul`.
- Ma Thù Nội Đan dùng đan dược đỏ `xd_dy_xynyd_5`; Huyết Ngọc Tri Thù Noãn dùng đúng icon `xd_htz_xyzzl` được yêu cầu.
- Giữ ID `ttk_boss_core_*` và `ttk_summon_*`, không đổi tiến độ ăn hoặc chỉ số. Chỉ nhập hình từ nguồn; không nhập cơ chế vật phẩm nguồn. Hình trên đất của năm món tái sử dụng được đóng gói thành sprite cùng hình icon; Tâm Nhĩ dùng animation DST.
- Biên dịch asset thành công; **36/36 test boss đạt**, toàn bộ **572 Lua** biên dịch được.
- Lỗi thiếu `hh_forge_ui.lua` nêu ở lượt trước đã được sửa trong workspace bởi công việc khác. Chạy lại `python tools/run_phamnhan_boss_smoke.py --reset`: **exit 0, PHAM_NHAN_BOSS_CREATE_PASS ở 00:02:35**. Có chín boss tự sinh, 268 prefab hỗ trợ tạo được, sáu lượt thưởng 1+1, ba collectible đã bỏ không xuất hiện, giao dịch triệu hồi Bạch Hổ thành công và không trả thưởng sớm ở pha một Tử Vân. Kiểm tra ăn/save-load nằm trong cùng lượt này và đạt.
- Kết quả mới này thay thế trạng thái bị chặn bootstrap ở mục trước. Không chạy lại hai pha reload thế giới vì thay đổi lần này chỉ tên/hình vật phẩm; không coi kết quả reload lịch sử là lần kiểm tra mới. Chưa kiểm tra hình ảnh trên client DST.


## Ba Lô Tiên Hà 18 ô — tích hợp theo yêu cầu người dùng

`ttk_boss_back_xh` chuyển từ collectible sang prefab ba lô độc lập, giữ ID/save và tỉ lệ rơi 10% của Thanh Tụ Đan Tiên. Tên hiển thị sửa thành Ba Lô Tiên Hà. Dùng hình gốc `xd_back_xh` và UI gốc 3 cột × 6 hàng; đăng ký container cho client/server. Trang bị ở EQUIPSLOTS.BACK, tương thích overflow 45 ô và lớp bảo vệ hình giáp hiện có. Không stack, không nhét vào container khác, không thêm giáp/bảo quản/tốc độ hay công thức mới.

Save cũ có stack được chuyển thành từng túi: giữ túi gốc và sinh các túi dư cạnh chủ sở hữu sau khi tải; số túi đang chờ tách cũng được lưu để không mất nếu lưu trước tác vụ. Container DST lưu nội dung 18 ô bình thường. Factory collectible bỏ qua ID này, không đăng ký prefab trùng. Công cụ port cập nhật tên và hai asset UI để không ghi đè ngược khi tái tạo.

Kiểm tra mới: 38/38 test boss đạt; test inventory45 compatibility đạt; 618 Lua trong workspace biên dịch được. Máy chủ thật `run_phamnhan_boss_smoke.py --reset` exit 0: PHAM_NHAN_BACKPACK_PASS tại 00:01:17 (18 ô, đeo/overflow, tháo, lưu/tải đủ đồ trong 18 ô, tách stack cũ 3 thành 3); PHAM_NHAN_BOSS_CREATE_PASS tại 00:02:42. Chưa xem UI 18 ô trên client đồ họa.


## Trồng hạt cây và phần thưởng hạt cố định — 2026-09-20

Tích hợp `ttk_boss_zcyseed` thành hạt ăn được (5 máu/12 no/2 tinh thần), trồng trực tiếp xuống đất, ngẫu nhiên xanh hoặc tím. Giữ ID cũ, stack và các món đã tồn tại. Chuyển cây và cây non từ source Tu Tiên 19.7 bằng công cụ tĩnh `tools/port_phamnhan_seed_tree.py`: animation, minimap, timer bén rễ 960 giây, sinh trưởng, lưu/tải, chặt/đào/cháy và hiệu ứng lá. Thu hoạch cây nhỏ 2 gỗ + 1 hạt; cây lớn 3 gỗ + 2 hạt và 17% thêm Gỗ Sống; đào gốc +1 gỗ. Không nhập hệ linh thảo khác.

Thanh Tụ Đan Tiên được đổi thành 2 hạt cây + mỗi loại trong sáu hạt linh thảo một hạt, tổng tám hạt chắc chắn. Bỏ cả hai lượt chọn đan và hai lượt chọn hạt ngẫu nhiên cũ; giữ đồ cổ đã có trong save và phần thưởng khác. Bộ hạt có cờ chống trả trùng trong một lần chết; generator combat giữ thay đổi này khi tái tạo.

41/41 test boss đạt; 619 Lua biên dịch được ở thời điểm kiểm tra. Lượt server đầu bị lỗi test harness `workable:Destroy(nil)` vì DST yêu cầu worker; đã sửa để dùng nhân vật thử. Lượt chạy lại `run_phamnhan_boss_smoke.py --reset` exit 0, PHAM_NHAN_SEED_TREE_PASS tại 00:01:37, PHAM_NHAN_FIXED_SEEDS_PASS tại 00:02:15, PHAM_NHAN_BOSS_CREATE_PASS tại 00:03:02. Kiểm tra thực tế cả hai màu: trồng tiêu hao một hạt, save/load cây non giữ timer, cây lớn giữ stage, chặt được 3 gỗ/2 hạt và đào thêm 1 gỗ. Boss thực tế rơi đúng tám hạt và không rơi các đan cổ đã bỏ. Không ghi nhận lỗi Lua hoặc thiếu animation/build/texture trong lượt đạt. Chưa xem trực tiếp cây/placer trên client đồ họa.

Hướng dẫn hiện tại: `mods/PhamNhanTuTien/SEED_TREE_VI.md` và `BOSS_DROPS_VI.md`.
