# Tế Đàn Phàm Nhân Tu Tiên — Implementation Plan

> **Điều chỉnh mới nhất:** đã bỏ công tắc `ttk_jitan_solo_bosses` theo yêu cầu người dùng. Boss Solo mặc định tham gia Tế Đàn vì Solo đã tích hợp trong Phàm Nhân; chỉ lọc theo năng lực đã nạp, prefab và điều kiện encounter. Các mô tả bật/tắt Solo bên dưới là lịch sử, được thay thế bởi điều chỉnh này.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển Tế Đàn, mọi boss tương thích của DST và hệ Solo đã tích hợp, cùng rương thưởng riêng sang Phàm Nhân Tu Tiên 2.0.

**Cập nhật dự án 20/09/2026:** Phàm Nhân Tu Tiên là tên mới của cùng mod ở `mods/TuTienKy`; Solo đã tích hợp đầy đủ và chạy cùng mod. Quy tắc này thay thế mô hình Solo ngoài tùy chọn trong các bước lịch sử bên dưới. Không tích hợp lại, không bật bản Solo nguồn cùng mod hiện tại, không đổi `ttk_`/`hh_` hay khóa save/RPC và không hạ phiên bản 2.0. Kiểm tra khả năng boss dựa trên prefab/component của bản tích hợp sau khi nạp xong. Ma trận runtime hiện tại: bản tích hợp, bản tích hợp + HUD, nâng cấp các save thử cũ. Các thử nghiệm thiếu năng lực Solo chỉ là kiểm tra phòng lỗi, không phải cấu hình phát hành hiện tại.

**Architecture:** Module máy chủ độc lập quản lý lượt, adapter boss kết thúc khác nhau, kho thưởng theo userid. Combat và sự kiện chết chuẩn DST được giữ để Solo xử lý scaling, EXP, nhiệm vụ và HUD.

**Tech Stack:** DST Lua 5.1, prefab/component/netvar, tài nguyên anim/atlas nguồn, Python + lupa.lua51 và runtime DST đang có trong máy.

**Spec:** `docs/superpowers/specs/2026-09-19-tu-tien-ky-te-dan-design.md`.

**Trạng thái:** Người dùng đã duyệt triển khai và chỉ định GPT-5.6 Sol, reasoning High. Thực hiện trong bản mod cô lập `.superpowers/te-dan-sol-high/TuTienKy`; nhật ký tại `.superpowers/te-dan-sol-high/progress.md`. Người dùng đã chọn chỉ boss DST và rương thưởng trước; hai boss riêng, lễ vật riêng và tai họa Tế Đàn để đợt sau. Công thức mới và quy tắc save được ghi trong spec.

## Cập nhật phạm vi đã duyệt — 20/09/2026

**Quy tắc bật/tắt boss Solo đã chốt:** bản tích hợp hiện không có công tắc tắt toàn bộ Solo. Tế Đàn dùng tùy chọn riêng `ttk_jitan_solo_bosses` (mặc định bật), kết hợp kiểm tra hệ Solo đã nạp thành công. Tắt tùy chọn loại toàn bộ encounter nguồn Solo và biến thể treasure Solo khỏi pool Tế Đàn; không tắt hệ Solo của Phàm Nhân. Ma trận kiểm thử dùng HUD tích hợp bật/tắt và boss Solo bật/tắt; không bật mod Solo nguồn cùng bản tích hợp.

Người dùng chốt: **đưa mọi boss tương thích của DST gốc và Solo Leveling vào thử luyện; boss Solo chỉ xuất hiện khi bật Solo**. Cập nhật này thay thế giới hạn danh sách nguồn và giới hạn nhóm 3 ở các bước bên dưới. Hai boss riêng Tu Tiên và tai họa vẫn ngoài phạm vi.

- [ ] Lập catalog có bằng chứng mã nguồn cho mọi họ boss, biến thể, pha, bộ boss và boss dungeon/đại dương; phân biệt minion và thực thể sau chiến thắng. Mỗi mục có quyết định hỗ trợ hoặc lý do chưa tương thích cụ thể.
- [ ] Dùng manifest encounter tập trung: id, prefab bắt đầu, nguồn DST/Solo, nhóm độ khó, adapter, dependency, điều kiện vị trí và cách xác nhận thắng. Pha nối tiếp thuộc cùng lượt, chỉ thưởng một lần.
- [ ] Mở rộng pool theo manifest đã audit; giữ xác suất điểm lễ vật, ghi lý do phân nhóm boss mới. Chỉ chọn encounter đủ prefab và dependency trên máy chủ; không chỉ dựa tên thư mục Workshop.
- [ ] Boss Solo không lọt pool khi Solo tắt. Encounter thiếu cấu hình hoặc cần arena chưa được hỗ trợ bị loại với lý do; không còn lựa chọn hợp lệ thì từ chối trước thu lễ vật.
- [ ] Boss cần arena, biển, manager hoặc phase successor phải có adapter được kiểm thử trước khi bật. Không bỏ cơ chế combat cốt lõi chỉ để spawn được, không kích hoạt tiến trình thế giới tự nhiên.
- [ ] Kiểm thử độ phủ catalog/pool, bật/tắt Solo, prefab thiếu, từng encounter hỗ trợ, chuyển pha và cleanup. Báo rõ mục chưa tương thích và giới hạn runtime; không gọi danh sách con là toàn bộ.

Catalog audit tại `.superpowers/te-dan-sol-high/boss-catalog-review.md`. GPT-5.6 Sol High tiếp tục triển khai; hạ tầng rương và quyết toán tiến hành trong khi hoàn tất catalog.

## Kết quả triển khai — 20/09/2026

Đã thực thi bằng GPT-5.6 Sol High, qua review máy chủ độc lập và đưa 34 file mới/thay đổi từ staging vào `mods/TuTienKy`, không xung đột với công việc khác. Asset/metadata/README cũ được backup trước khi chuyển.

- [x] Catalog 51 encounter và adapter theo mã nguồn; điều kiện prefab, địa hình, số vị trí và mùa được lọc trước lễ vật.
- [x] Tế Đàn, vòng đời lượt, namespace/save, rương riêng và thưởng snapshot có chống lặp.
- [x] Tùy chọn `ttk_jitan_solo_bosses` lọc đúng 13 encounter Solo; giữ nguyên hệ Solo tích hợp.
- [x] Sáu suite Tế Đàn đạt; 460 Lua biên dịch được. Máy chủ thật: 51 encounter khởi tạo đạt; tắt boss Solo: 38 đạt/13 bị loại. Phase chain, Twins loot, quyền rương hai người đạt.
- [x] Tắt HUD và hai cụm save thử cũ khởi động/tắt sạch. Đây là kiểm tra tải, không phải chơi hết trận.
- [ ] Playtest client thật: widget/animation, hai người nhận rương, trọn trận từng họ boss, lưu/tải giữa trận.

Audit và hướng dẫn hiện hành: `mods/TuTienKy/AUDIT_JITAN_VI.md`, `mods/TuTienKy/README_VI.md`. Catalog: `docs/superpowers/reports/2026-09-20-pham-nhan-te-dan-boss-catalog.md`. Hai lỗi audit nền đã ghi rõ; không sửa asset lò rèn hoặc brain Solo cũ ngoài phạm vi. Các checkbox trong phần kế hoạch gốc bên dưới được giữ làm lịch sử; trạng thái nghiệm thu nằm ở mục này.

## Global Constraints

- Không `require` hoặc `modimport` Solo, không tạo component Solo bằng tay, không thay hook toàn cục health/combat/loot của Solo.
- Máy chủ quyết định trận và thưởng; namespace mới `ttk_*`; giữ bank/build gốc chỉ khi asset cần.
- Không nhập hệ cảnh giới hoặc tăng cảnh giới sau thử luyện.
- Không sửa địa hình, không cần world mới; không tự mở game chính, ghi đè save thật hoặc phát hành bản thử chưa qua kiểm tra.
- Mọi nguồn khác `xd_jitan.lua` phải đối chiếu bản gốc 19.7 trước khi chuyển; không dùng chuỗi `<XX>` chưa giải.
- Chỉ boss thử luyện bị thay đổi; không sửa mã nguồn Solo, EVA hoặc các thay đổi web đang có trong workspace.

## Review Focus

1. Boss chuyển pha/defeat và event remove đến sau death: chỉ ghi một kết quả cuối — Task 3.
2. Solo zero-delay scaling và đổi World Rank: không nhân máu hoặc damage hai lần — Task 5.
3. Bóng Solo giết boss, người nộp khác người giết: đúng người nhận thưởng, không thêm kill credit — Task 5.
4. Rương đầy, disconnect, save/load sau thắng: không mất hoặc nhân thưởng — Task 4 và 6.
5. Dọn trận khi minion/FX tồn tại cạnh boss tự nhiên hoặc dungeon: chỉ dọn thực thể có run_id — Task 3 và 6.

Lưu ý môi trường: shell hiện không có lệnh `python` trên PATH. Khi triển khai, xác định executable Python có `lupa.lua51` bằng runtime dependency của workspace rồi thay `python` trong các lệnh dưới bằng đường dẫn đó; không cài lại dependency khi chưa kiểm tra runtime sẵn có.

## Task 1 — Chốt manifest nguồn và module đăng ký

**Files:** tạo `tools/port_ttk_jitan_assets.py`, `mods/TuTienKy/main/ttk_jitan.lua`, `mods/TuTienKy/scripts/ttk_jitan_defs.lua`, `mods/TuTienKy/tools/test_jitan.py`; sửa `mods/TuTienKy/modmain.lua`; tạo báo cáo `docs/superpowers/reports/2026-09-19-tu-tien-ky-te-dan-source.md`.

**Interfaces:** defs xuất `offerings`, `boss_pools`, `reward_pools`, `recipe_ingredients`. Module đăng ký dùng `table.insert(PrefabFiles, name)` theo pattern `main/ttk_rituals.lua`.

- [ ] Ghi hash/version Solo, Tu Tiên Ký, nguồn Tu Tiên và HUD; lưu bản sao chỉ các file sẽ sửa. Không reset workspace đang có thay đổi.
- [ ] Truy toàn bộ SpawnPrefab/require/component/SG/brain/FX/tuning của Tế Đàn, rương và adapter boss DST. Mỗi dependency có source path, tên đích và quyết định giữ/thay/bỏ; cả loot table cũng phải resolve được.
- [ ] Loại hai boss riêng, lễ vật riêng và tai họa khỏi manifest; đối chiếu phụ thuộc 19.7 trước tái dùng bộ decoded.
- [ ] Tách chọn boss khỏi môi trường. Nhóm boss theo điểm: 2 -> nhóm 1; 3 -> nhóm 1/2 tỷ lệ 50/50%; 4 -> nhóm 1/3/2 tỷ lệ 34/33/33%; 5 -> nhóm 2/3 tỷ lệ 50/50%; 6 -> nhóm 3. Mỗi nhóm chọn đều các mục còn hỗ trợ; nhóm 3 chỉ Klaus và bộ ba bóng tối. Ghi nhận lỗi nguồn dùng num1 thay num2 cho môi trường nhưng không port phần môi trường đợt này.
- [ ] Tạo audit lỗi trước khi đăng ký: thiếu asset/prefab, tham chiếu `XD_GETWOLRDLEVEL`, `XD_GONGGAO`, `xd_level` hoặc import Solo phải fail. Bản cuối có đủ atlas/minimap/animation và chuỗi Việt hóa.
- [ ] Chạy `python mods/TuTienKy/tools/audit_registration.py`; xử lý lỗi mới và ghi riêng lỗi baseline nếu có. Mốc này chỉ xong khi manifest không còn dependency chưa xác định.

## Task 2 — Tế Đàn và vòng đời máy chủ

**Files:** tạo `scripts/prefabs/ttk_jitan.lua`, `scripts/components/ttk_jitan_trial.lua`, `scripts/ttk_jitan_rules.lua` dưới `mods/TuTienKy`; cập nhật `tools/test_jitan.py` và module đăng ký.

**Interfaces:** `trial:CanStart(player,item) -> boolean,reason`; `trial:Start(player,offering_prefab) -> boolean,reason`; `trial:Finish(run_id,outcome,reason) -> boolean`. `outcome` chỉ `won`, `lost`, `cancelled`; run_id không tái sử dụng khi load.

- [ ] Dùng Trader thật từ DST scripts.zip trong fixture Lua 5.1 như `test_ngulongdang.py`. Kiểm thử lễ vật sai, stack 120, thiếu rương, người chết, hai người nộp cùng tick; chỉ lượt được nhận mất đúng một món.
- [ ] Kiểm thử quy tắc bằng RNG được truyền vào; xét chính xác biên 0.7 và 0.1 thay vì test thống kê dễ chập chờn.
- [ ] Viết component theo trạng thái spec; kiểm tra vị trí passable, shard/nội thất/dungeon và vùng chồng lấn trước nhận phí. Dùng marker của vùng dungeon đã xác minh từ Solo; nếu không xác định được vùng an toàn thì từ chối với lý do tiếng Việt, không đoán bằng tên prefab.
- [ ] Gắn netvar trước `SetPristine`, component chỉ sau kiểm tra `ismastersim`; thông báo qua talker hoặc event/netvar namespace riêng.
- [ ] Kiểm thử đếm ngược 5 giây; ngưỡng 32/60; ngoài vùng cộng dồn 11 tick; death/disconnect; gọi Finish lặp phải trả false và không thưởng/phạt thêm.

Hợp đồng Lua dùng trong fixture (biến trial/player/stone do fixture dựng):

```lua
assert(trial:CanStart(player, stone))
assert(trial:Start(player, stone.prefab))
local run = trial.run_id
assert(trial:Finish(run, "lost", "owner_left"))
assert(not trial:Finish(run, "won", "late_death"))
assert(trial.state == "idle")
```

Run: `python mods/TuTienKy/tools/test_jitan.py`. Chạy test mới trước và sau implementation; xác nhận lần đầu fail đúng chức năng chưa có.

## Task 3 — Boss DST và bộ nhận diện kết thúc

**Files:** tạo `scripts/ttk_jitan_bosses.lua`, `scripts/ttk_jitan_boss_adapters.lua`, `tools/test_jitan_bosses.py`; sửa component thử luyện.

**Interfaces:** `Bosses.Spawn(trial,boss_id) -> entities,error`; `Adapters.Attach(entity,trial,run_id)`; `trial:MarkBossDefeated(run_id,entity) -> boolean`; `trial:TrackEntity(run_id,entity)`.

- [ ] Đưa các boss DST nguồn và nhóm nhiều boss vào defs. Tạo spy kiểm chứng đủ 3 Spider Queen/2 Mutated Warg/bộ ba bóng tối; spawn nil phải dọn phần đã sinh và hoàn phí một lần.
- [ ] Mark boss/minion bằng run_id, theo dõi entity thuộc lượt; không dùng quét rồi xóa mọi entity theo tên trong bán kính.
- [ ] Adapter riêng cho Klaus hai pha, Daywalker defeat, Sharkboi minhealth/defeat, Celestial Champion và Shadow Thralls. Kiểm tra runtime stategraph hiện tại trước khi chọn event; mọi wrapper gọi lại hàm trước đó và chỉ đổi hành vi khi marker thử luyện tồn tại.
- [ ] Test chuỗi death -> onremove, defeat -> onremove, boss pha một -> pha hai, minion chết trước boss. Chỉ cuối nhóm mới thắng, boss tự nhiên giữ toàn bộ hành vi gốc.
- [ ] Dọn thất bại bằng Remove không giả chết; kiểm tra không phát EXP, loot hoặc linh thạch vì thao tác dọn. Sau thắng không xóa corpse Solo hợp lệ.

Run: `python mods/TuTienKy/tools/test_jitan_bosses.py`.

## Task 4 — Rương riêng và giao dịch thưởng

**Files:** tạo `scripts/prefabs/ttk_llbx.lua`, `scripts/components/ttk_jitan_rewards.lua`, `scripts/ttk_jitan_rewards.lua`, `tools/test_jitan_rewards.py`; sửa `scripts/ttk_loot.lua` với guard marker nhỏ.

**Interfaces:** component `rewards:Queue(run_id,userid,records) -> boolean`, `rewards:Claim(player) -> delivered_count`; module dữ liệu `Rewards.Roll(score,rng,boss_id) -> item_records`. `records` đã cố định, không roll lại khi nhận.

- [ ] Tạo rương theo userid, server kiểm tra người mở, client không được chỉ định userid khác. Dùng container/save-record chuẩn để giữ trang bị Solo; không dựng lại vật phẩm chỉ bằng prefab khi nó đã có dữ liệu.
- [ ] Chuyển đủ bảng nhóm thưởng và số lượng nguồn; alias `xd_lingshi*` sang `ttk_lingshi*`. Audit mọi item tồn tại trước commit kết quả.
- [ ] Thêm guard `inst:HasTag("ttk_jitan_boss")` trong hook linh thạch chung trước `_ttk_death_paid`; không đổi classifier chung. Đảm bảo boss tự nhiên vẫn nhận 2–5 viên như trước.
- [ ] Chọn loot bổ sung 2–3 lượt từ bảng tĩnh đã audit; spy xác nhận `GenerateLoot` của boss không bị gọi thêm bởi phần thưởng Tế Đàn. Giữ loot chết tự nhiên do Solo/DST xử lý.
- [ ] Test A nộp B giết, full container, stack gần đầy, queue sau load, gọi Queue cùng run_id hai lần, nhiều lượt chưa claim và trang bị phụ ma save/load. Không tạo chest mới để né queue hoặc mất đồ.

Run: `python mods/TuTienKy/tools/test_jitan_rewards.py`.

## Task 5 — Hợp đồng tương thích Solo cho boss DST

**Files:** tạo `mods/TuTienKy/tools/test_jitan_solo.py`; chỉ sửa adapter thử luyện khi có lỗi đã xác minh. Không sửa mã Solo hoặc tạo bridge đăng ký boss mới.

**Interfaces:** dùng `Bosses.Spawn`, `Adapters.Attach`, `trial:MarkBossDefeated` từ Task 3, không thêm API Solo riêng.

- [ ] Đọc luồng `hh_monster`, `hh_world`, `hh_player`, `hh_utils`; fixture kiểm tra hook thật, không đoán event EXP.
- [ ] So sánh boss tự nhiên với boss thử luyện cùng prefab sau zero-delay task: cùng hệ số Solo, đổi World Rank không nhân lặp. Không sửa cờ balance hoặc máu nền World Rank.
- [ ] Test người chơi/bóng Solo kết liễu, vũ khí cường hóa, Lục Mạch/Vạn Hồn Phiên, armor/planar và bảo vệ chết Solo. Không tự phát `killed`; EXP/nhiệm vụ như boss đối chứng.
- [ ] Boss defeat không giả death để ép EXP. Test loot/corpse/rút bóng nếu boss đối chứng hỗ trợ; giữ corpse hợp lệ sau thắng, không tạo loot/corpse khi hủy.
- [ ] Test Solo tắt, Solo bật không HUD và bật cả HUD; health bar/chỉ báo đọc máu thật, không nhân UI.

Run: `python mods/TuTienKy/tools/test_jitan_solo.py`. Fixture không thay thế runtime Task 6.

## Task 6 — Save, runtime và bàn giao

**Files:** tạo `tools/test_jitan_save.py`, `tools/test_jitan_runtime.py` trong mod; tạo báo cáo `mods/TuTienKy/AUDIT_JITAN_VI.md`; cập nhật `README_VI.md`, `modinfo.lua` sau khi đạt kiểm thử.

- [ ] Save ở idle/countdown/active/settling và khi có queue: load hủy lượt đang chạy không phạt/không hoàn/không thưởng, giữ queue đã quyết toán. Boss không persist; không để minion/FX mồ côi.
- [ ] Không tháo rương có đồ/queue; test hammer/burn/despawn và save cũ chưa có trường dữ liệu. Nếu rương bị mất ngoài ý muốn, lưu queue tại authority thử luyện còn tồn tại, không âm thầm xóa.
- [ ] Chạy toàn bộ test mới, audit registration và các hồi quy liên quan: `test_inventory45.py`, `test_ngulongdang.py`, `test_tinhlakiem.py`; test loot/classifier sẵn có phải được tìm và chạy ở bước thực hiện.
- [ ] Tạo cluster thử riêng bằng pattern `.superpowers/run_dst_audit.py`; không dùng save đang chơi. Chạy 3 cấu hình: Tu Tiên Ký; Tu Tiên Ký + Solo; Tu Tiên Ký + Solo + HUD. Mỗi cấu hình thử host và dedicated + client, save cũ, reconnect và chuyển hang.
- [ ] Với Solo thử ít nhất World Rank thấp và cao; boss DST bình thường, boss chuyển pha và nhóm nhiều boss. Ghi maxhealth sau init, sát thương thực, số event kill/reward, rương và log lỗi.
- [ ] Chạy game xác nhận thao tác nộp lễ vật/rương, animation, minimap, HUD, bóng kết liễu và không chồng UI. Nếu thiếu môi trường game, báo chính xác phần chưa kiểm tra; không ghi “đã tương thích hoàn toàn”.
- [ ] Ghi README: công thức, vật phẩm, phạm vi thử luyện, thưởng, khác biệt với nguồn và quy tắc save. Tăng version sau kiểm tra, lưu danh sách file/backup để rollback. Không đóng gói hoặc cài đè thư mục game nếu chưa được yêu cầu.

## Mốc bàn giao

1. Task 1–4: thử luyện boss DST + thưởng riêng, chạy độc lập.
2. Task 5: hợp đồng Solo cho boss DST được kiểm thử.
3. Task 6: bản đủ điều kiện đưa vào save chơi, có bằng chứng runtime và danh sách giới hạn còn lại.

Kế hoạch ưu tiên thực hiện tuần tự trong task hiện tại khi được yêu cầu triển khai. Chưa có bước nào được đánh dấu hoàn thành chỉ dựa trên việc đã viết kế hoạch.



