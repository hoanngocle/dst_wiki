# Tế Đàn cho Phàm Nhân Tu Tiên — thiết kế

> **Điều chỉnh mới nhất:** đã bỏ công tắc `ttk_jitan_solo_bosses` theo yêu cầu người dùng. Boss Solo mặc định tham gia Tế Đàn vì Solo đã tích hợp trong Phàm Nhân; chỉ lọc theo năng lực đã nạp, prefab và điều kiện encounter. Các mô tả bật/tắt Solo bên dưới là lịch sử, được thay thế bởi điều chỉnh này.

Ngày: 19/09/2026; cập nhật 20/09/2026. Trạng thái: đã triển khai bởi GPT-5.6 Sol High, review máy chủ và chuyển vào `mods/TuTienKy`; kiểm tra khởi tạo 51 encounter đạt. Chưa xác nhận toàn bộ gameplay/client.

## Mục tiêu và phạm vi

**Cập nhật dự án 20/09/2026:** mod hiện tại là Phàm Nhân Tu Tiên 2.0, tiếp nối Tu Tiên Ký ở nguyên đường dẫn `mods/TuTienKy`. Solo đã tích hợp đầy đủ; các mô tả Solo ngoài tùy chọn bên dưới thuộc thiết kế lịch sử, được thay bằng kiểm tra năng lực của hệ tích hợp. Giữ toàn bộ định danh và dữ liệu save/RPC. Không bật thêm mod Solo nguồn. Phạm vi Tế Đàn và danh mục boss đã duyệt tiếp tục trên bản tích hợp.

Chuyển Tế Đàn, hai lễ vật linh thạch, mọi boss tương thích của DST và Solo Leveling, cùng rương thưởng riêng sang Tu Tiên Ký. Boss Solo chỉ xuất hiện khi bật Solo. Tai họa Tế Đàn, hai boss riêng Tu Tiên, Kỳ Lân Nhung/Phượng Tủy, đảo thử luyện và hệ cảnh giới để ngoài phạm vi đợt này.

## Cập nhật phạm vi đã duyệt — 20/09/2026

**Quy tắc bật/tắt boss Solo đã chốt:** bản tích hợp hiện không có công tắc tắt toàn bộ Solo. Tế Đàn dùng tùy chọn riêng `ttk_jitan_solo_bosses` (mặc định bật), kết hợp kiểm tra hệ Solo đã nạp thành công. Tắt tùy chọn loại toàn bộ encounter nguồn Solo và biến thể treasure Solo khỏi pool Tế Đàn; không tắt hệ Solo của Phàm Nhân. Ma trận kiểm thử dùng HUD tích hợp bật/tắt và boss Solo bật/tắt; không bật mod Solo nguồn cùng bản tích hợp.

Phạm vi boss mở rộng thành **mọi boss tương thích trong DST gốc và Solo Leveling; boss Solo chỉ xuất hiện khi bật Solo** và đủ dependency. Danh sách boss của Tế Đàn nguồn chỉ là điểm xuất phát. Phải audit đủ họ boss, biến thể, pha, boss biển và dungeon; ghi rõ lý do cho từng encounter chưa tương thích. Pha nối tiếp không tính là nhiều chiến thắng. Giới hạn nhóm 3 bên dưới được thay bằng phân nhóm của manifest đã audit. Vẫn không thêm hai boss riêng Tu Tiên, tai họa hoặc hệ cảnh giới. Triển khai đang tiến hành trong bản cô lập, chưa xác nhận tương thích gameplay hoàn toàn.

## Bằng chứng đã đọc

- `mods/mod_steam/3235319974/scripts/prefabs/xd_jitan.lua` và bản Việt hóa `3721846643`: cùng SHA-256 `E4AD44A85C307A81D44FC93C12BF9F1069CBA019D7E61C9FA0BE7C84F7A9D69A` tại thời điểm khảo sát. Bản đọc: `mods/eva-assets-work/skill-audit/decoded/scripts/prefabs/xd_jitan.lua`.
- Bản đọc trên thuộc bộ giải mã 18.1.0; chỉ file Tế Đàn đã được xác minh bằng hash với bản gốc. Mọi phụ thuộc khác phải đối chiếu bản gốc 19.7 trước khi chuyển; chuỗi `<XX>` chưa giải không được đưa vào sản phẩm.
- `scripts/main/prefabpostInit.lua` trong bộ giải mã có xử lý defeat của Daywalker/Sharkboi và kết thúc Celestial Champion. Sao chép riêng prefab Tế Đàn sẽ thiếu các xử lý này.
- `mods/TuTienKy/scripts/ttk_loot.lua`: phát linh thạch qua `entity_death`, có chốt chống trả hai lần và reset khi hồi sinh. `ttk_defs.lua`: boss hiện rơi 2–5 Thượng Phẩm Linh Thạch.
- `mods/TuTienKy/scripts/ttk_enemy_rules.lua`: loại pet/bóng Solo, nhận boss qua `epic`, `boss` hoặc `hh_tags`.
- Solo thực tế: `mods/mod_steam/3780347550`. `main/hh_api.lua:519` chỉnh máu/sát thương qua zero-delay task; `main/hh_world_rank.lua:189` áp World Rank sau đó; `scripts/components/hh_world.lua` giữ máu nền và xử lý nguồn sát thương.
- `scripts/utils/hh_utils.lua` của Solo có chuyển kill credit về người chơi; `hh_player.lua` nghe `killed`. Không tự phát lại sự kiện này để trao thưởng Tế Đàn.
- `mods/SoloCombatHUD` là mod HUD riêng, không phải Solo Leveling. Cần thử cả khi bật và tắt HUD.

## Hướng tích hợp

Chọn **module thử luyện độc lập dùng combat chuẩn DST**, kèm adapter theo từng boss. Giữ bộ lễ vật, xác suất và đồ họa nguồn; đổi namespace runtime sang `ttk_*`. Không `require` hoặc `modimport` Solo, không tạo component Solo bằng tay, không thay hook toàn cục health/combat/loot của Solo.

Đã chọn bản giới hạn theo ý kiến người dùng. Chép cả hệ thống gốc kéo theo cảnh giới và hook toàn cục; chuyển thêm boss riêng tăng khối lượng kiểm thử nên để đợt sau.

### Luồng sử dụng và tiếp cận

- Công trình chế tạo, dùng được trong save cũ; không sửa địa hình và không cần worldgen. Công thức đề xuất: Tế Đàn tại Máy Luyện Kim, 12 Đá Cắt + 6 Vàng + 2 Thượng Phẩm Linh Thạch; Linh Lung Bảo Sương: 6 Ván + 4 Vàng + 1 Thượng Phẩm Linh Thạch. Đây là cân bằng mới, không phải công thức nguồn.
- Cần rương trong bán kính 32 hoặc liên kết còn hợp lệ. Thiếu rương/vị trí sinh boss/phụ thuộc thì từ chối trước khi tiêu hao lễ vật. Một lượt hoạt động mỗi Tế Đàn; từ chối vùng thử luyện chồng nhau trong khoảng 128 đơn vị. Không mở trong nội thất Thiên Cơ Ốc hoặc dungeon Solo.
- Nộp đúng một món, đếm ngược 5 giây; bán kính chuẩn bị 32, thi đấu 60. Giữ 11 lần kiểm tra ngoài vùng cộng dồn như nguồn, không reset khi quay lại. Không giới hạn thời gian toàn trận.
- Bảng lễ vật giữ xác suất nguồn: `ttk_lingshi2`: điểm 2/3/4 = 35/35/30%; `ttk_lingshi3`: điểm 4/5/6 = 10/45/45%; từ chối mọi lễ vật khác.
- Không phụ thuộc world-level Tu Tiên: bộ ba bóng tối được đưa vào nhóm boss khó khi nhánh điểm chọn nhóm 3; ghi rõ bỏ điều kiện world-level >= 9 của nguồn. Điểm 2–6 chọn nhóm boss và thưởng; độ khó thấp hơn nguồn vì chưa có tai họa. Loại hai boss riêng khỏi nhóm 3; nhóm này còn Klaus và bộ ba bóng tối. Không áp thêm bộ kỹ năng quái ngẫu nhiên Tu Tiên lên boss DST; khi có Solo, Solo giữ hệ buff quái của nó.

### Vòng đời và tương thích

- Máy chủ quản lý `idle -> countdown -> active -> settling -> idle`, với `run_id`, `owner_userid`, danh sách boss và chốt quyết toán. Máy khách chỉ hiển thị.
- Lưu chủ sở hữu bằng userid, không bằng tham chiếu player. Khi thắng, thưởng thuộc người nộp dù người khác hoặc bóng Solo kết liễu. EXP/nhiệm vụ Solo vẫn do Solo quyết định theo nguồn đòn đánh.
- Boss chết thật đi qua event chuẩn. Với defeat/chuyển pha: adapter kiểm tra trạng thái cuối, tránh tính Klaus pha một hay entity biến hình thành chiến thắng. Không giả `death`, `killed` hoặc `entity_death` để hoàn tất lượt.
- Không ghi đè máu sau post-init Solo, không gọi scaling lần hai hoặc gắn cờ dungeon. Giữ prefab DST chuẩn để Solo nhận diện EXP/nhiệm vụ; không đăng ký boss mới và không tạo component Solo bằng tay.
- Giữ combat, attacker/weapon, armor và planar chuẩn DST. Không nhập sát thương thần thức hoặc API damage riêng của Tu Tiên gốc trong đợt này.
- Chết/rời shard/disconnect: kết thúc thất bại, không thưởng. Rời vùng đủ ngưỡng: phạt 40% maxhealth qua health API, không bỏ qua bảo vệ sinh tồn của Solo. Hủy do lỗi spawn: hoàn lễ vật đúng một lần.
- Dọn theo run_id: chỉ boss, minion và FX thuộc lượt; không xóa boss tự nhiên, bóng Solo, corpse hợp lệ sau chiến thắng. Hủy task theo dõi và đếm ngược khi kết thúc. Boss DST giữ kỹ năng vốn có; Tế Đàn không bổ sung tai họa.
- Save giữa countdown/active: ghi trạng thái đã thu phí; khi load hủy trận không phạt, không hoàn phí, không tạo lại boss hoặc thưởng. Countdown bị hủy do người chơi rời vùng cũng không hoàn phí, như nguồn. Save sau thắng giữ phần thưởng chưa nhận; không reroll. Đây là lựa chọn chống nhân thưởng, cần ghi rõ trong hướng dẫn.

### Thưởng và chống lặp

- Giữ tỷ lệ nhóm 1/2/3 và linh thạch bonus nguồn. Giữ loot chết bình thường do DST/Solo quản lý; thưởng thử luyện là phần bổ sung độc lập.
- Không gọi `GenerateLoot()` nhiều lần trên boss đã bị Solo bọc: 2–3 lượt loot bổ sung dùng bảng snapshot tĩnh của boss được audit từ nguồn, chỉ gồm loot DST/Tu Tiên Ký đã đăng ký, không gồm loot Solo hoặc linh thạch từ hook toàn cục.
- Loại boss thử luyện khỏi hook phát linh thạch chung Tu Tiên Ký bằng tag riêng, chỉ trong `ttk_loot.lua`. Không sửa bộ phân loại chung vì HUD và hệ khác vẫn cần nhận boss. Điều này tránh phí 1 viên nhưng mỗi boss tự trả thêm 2–5 viên ngoài bảng thưởng.
- Rương mỗi userid, lưu cả vật phẩm có độ bền/phụ ma bằng save record chuẩn. Rương đầy: giữ queue thưởng đã roll, nhận sau; không xóa, reroll hoặc thả vào rương người khác. Không cộng EXP hay tiến độ Solo thủ công.

## Điều kiện nghiệm thu

Đủ hai lễ vật linh thạch, mọi boss DST được chọn đều tạo được, thắng/thua chỉ quyết toán một lần, không mất thưởng rương đầy, tải save không nhân vật phẩm. Tu Tiên Ký chạy khi Solo tắt và khi Solo bật, có/không Solo Combat HUD; không cần bật Tu Tiên gốc. Không thay balance hoặc stategraph của boss tự nhiên. Kiểm thử phải có runtime DST và phiên game thực tế; kiểm tra Lua/stub không đủ để tuyên bố tương thích hoàn toàn.

