# Bàn giao rà soát Solo Leveling trong Phàm Nhân

Ngày cập nhật: 2026-09-22

## Mục tiêu và phạm vi

- Rà lần lượt toàn bộ chức năng Solo Leveling đã được tích hợp vào **Phàm Nhân Tu Tiên 2.0**.
- Chỉ sửa bản đang dùng tại `mods/PhamNhanTuTien` và test liên quan.
- Không sửa nguồn đối chiếu `mods/3780347550`, `mods/2937640068` hoặc `mods/AchievementLevel`.
- Giữ nguyên các ID `hh_`/`ttk_`, save, RPC và route hiện có.
- Solo Leveling đã được tích hợp hoàn toàn; không coi Solo là dependency tùy chọn của Phàm Nhân.

## Danh sách 12 mục rà soát

1. Cấp độ, EXP, điểm tiềm năng, 5 chỉ số và Mana.
2. Chiến đấu: sát thương thường, chí mạng, xuyên giáp, né, giảm thương và hồi máu.
3. Kỹ năng Thợ Săn: Thánh Vực Hồi Phục, Diệt Thần, Kẻ Thống Trị, Nhà Vua, Ngưỡng Sinh Tử, Siêu Tăng Trưởng.
4. Nhiệm vụ ngày: 61 định nghĩa, thưởng EXP và hình phạt thất bại.
5. Hiệp Hội: Rank E–S, 6 kỳ thi Rank, 60 nhiệm vụ, điểm tín dụng và cửa hàng.
6. Quân Đoàn Bóng Tối: trích xuất, triệu hồi, thu hồi, hoán đổi và Mana duy trì.
7. Tiến trình đệ tử: cấp, EXP, điểm tài năng và nâng cấp riêng.
8. Hầm Ngục: đấu trường, quái, boss Igris/Beru/Sharkboi, tiền và cửa hàng.
9. Trang bị: thuộc tính ngẫu nhiên, khảm, tẩy, kế thừa và bộ trang bị.
10. Cường hóa: Lam Phượng Luyện Khí Đài, đá cường hóa, bùa bảo vệ và thuốc may mắn.
11. Vũ khí, vật phẩm và công thức.
12. UI, HUD chiến đấu, RPC, lưu dữ liệu, worldgen và tương thích save.

Kho nội dung đã thống kê: 30 mục vật phẩm/sinh vật chính, 17 công thức/dung hợp, 167 thuộc tính/hiệu ứng trang bị, 53 sản phẩm Hầm Ngục (15 thuốc người chơi, 14 thuốc đệ tử, 7 vũ khí, 17 tiện ích), 90 sản phẩm Hiệp Hội và 5 đệ tử.

## Mục 1 — lịch sử đợt rà trước Mục 2

Các sửa lỗi Mana/transfer dưới đây là kết quả đợt rà trước. Thông tin Level/EXP ở thời điểm đó không phải đặc tả hợp nhất mới: Achievement chưa merge, việc hợp nhất Level/EXP thuộc kế hoạch/task riêng; thành tựu thưởng Star, không thưởng EXP. Chơi world mới, không yêu cầu migration save. Các dòng STR/VIT phẳng cũ đã được Mục 2 thay thế bằng phần trăm.

Hành vi của đợt rà trước, giữ để đối chiếu lịch sử (không phải hướng dẫn tiến trình hiện hành):

- EXP lên cấp: `100 + 25n + 5n²`, `n = cấp - 1`.
- Cơ chế chia EXP cũ đã bị người dùng loại khỏi thiết kế chơi đơn; không dùng nó làm yêu cầu triển khai hợp nhất Level/EXP.
- EXP quái thường giảm còn 75/50/25/10% khi người chơi vượt cấp 10/20/30/40; boss không giảm.
- Mỗi cấp nhận 2 AP, cấp chia hết cho 10 nhận thêm 2 AP.
- Cap: STR 200, AGI 50, VIT 40, SEN 50, INT 15.
- Hiện tại sau Mục 2: STR cho +0,1% Xuyên Giáp mỗi điểm; AGI cho né; VIT cho +1% pool giảm thương mỗi điểm; SEN tăng tỉ lệ và hiệu quả Bạo Kích; INT tăng Mana, hồi Mana, giảm hồi chiêu và thời gian hồi đệ tử.
- Mana cơ sở 100 và hồi 1/giây; INT tối đa cho 400 Mana và 3,25 Mana/giây.
- Không thêm trần level/AP vì chưa có yêu cầu thiết kế; AP vẫn có thể tích lũy sau khi đủ cap chỉ số.

Các lỗi đã sửa:

- Mana dùng xong nay chờ đúng `HH_MANA.REGEN_DELAY = 3` giây mới hồi.
- `HHLeveling:TransferComponent()` nay chuyển level, EXP, AP, năm chỉ số và phong ấn EXP.
- `HHMana:TransferComponent()` nay chuyển Mana hiện tại và phần thời gian chờ hồi còn lại.
- `HHLeveling:OnLoad()` ép kiểu, loại NaN/vô cực, chặn âm, ép số nguyên và clamp chỉ số theo cap.
- Xóa `AGI_CAP = 60` dư và mâu thuẫn với cap thực tế 50.
- Sửa chú thích số thuốc đệ tử từ 15 thành 14.
- Khôi phục `mods/PhamNhanTuTien/Wiki.txt` đúng hash nguồn.
- Cập nhật test tích hợp theo version 2.0.x, ba config Solo còn giữ, và giao diện trợ giúp đã được thay bằng màn hình hợp nhất.

File đã đổi cho mục 1:

- `mods/PhamNhanTuTien/scripts/components/hh_leveling.lua`
- `mods/PhamNhanTuTien/scripts/components/hh_mana.lua`
- `mods/PhamNhanTuTien/main/hh_tunning.lua`
- `mods/PhamNhanTuTien/scripts/dungeon_shop/hh_dungeon_shop_defs.lua`
- `mods/PhamNhanTuTien/Wiki.txt` (file mới trong working tree)
- `mods/PhamNhanTuTien/tools/test_solo_progression.py` (test mới)
- `tools/test_ttk_solo_integration.py`

TDD đã thực hiện: ba test hồi quy ban đầu đều đỏ, sau bản vá đều xanh. Kiểm tra cuối:

```powershell
& 'C:\Users\hoanc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' mods/PhamNhanTuTien/tools/test_solo_progression.py
# 3/3 OK

& 'C:\Users\hoanc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools/test_ttk_solo_integration.py
# 7/7 OK; biên dịch 634 file Lua
```

`git diff --check` đạt. Hash `Wiki.txt` của nguồn và Phàm Nhân trùng nhau. `git diff -- mods/mod_steam/3780347550` không có thay đổi.

## Mục 2 — đã triển khai, chưa đạt toàn bộ cổng xác minh

Người dùng đã duyệt thiết kế và yêu cầu triển khai. Task 1–5.2 đã đưa pipeline, trạng thái, catalog, kiểm thử server thật, cổng tích hợp và các sửa hậu kiểm vào bản tích hợp; không sửa nguồn lịch sử. Mismatch provenance cũ đã được xác định là hai hash metadata lỗi thời và được đối chiếu byte-for-byte với bản Steam Workshop đang cài. Cổng tích hợp hiện PASS 13/13. Báo cáo chi tiết: `.superpowers/sdd/2026-09-21-pham-nhan-combat-pipeline/task-5-report.md`, `task-5-1-report.md` và `task-5-2-report.md` cùng thư mục.

Contract đã đưa vào code:

- Né trước mọi offensive RNG; chuẩn hóa 1–100 cho người chơi, quái và follower.
- Đòn chính giữ đủ sát thương thường; Xuyên Giáp là gói cộng thêm riêng, không phải chia tách.
- `B = base + flat`; Công Kích tăng đòn chính và lan; Nghịch Cảnh chỉ tăng đòn chính. Crit/Bạo Phát tăng đòn chính và lan. Độc/Xuyên chỉ dùng `B`.
- Player pool giảm thường tối đa 80%, né 70%, Xuyên 40%, lan 60%; hút máu giới hạn 15% mỗi event và 90% mỗi cửa sổ một giây.
- Xuyên bỏ player pool/giáp thường, giữ non-armor defenses và phòng thủ quái. Độc bỏ giáp thường nhưng vẫn chịu player pool. Planar giữ cơ chế riêng.
- Packet phụ không kích hoạt proc/counter Lục Nguyên; đòn tầm xa vẫn được lan.
- Bạo Phát I–IV đều chỉ ở pool đá huyền thoại cực hiếm. Đã xóa các cơ chế/set được duyệt bỏ, gồm cả custom Phản Chấn giáp +7; generic `ontakedamage` của Bất Diệt và gai vanilla không bị xóa.

File chính: `scripts/combat/hh_combat_math.lua`, `hh_combat_context.lua`, `hh_combat_status.lua`; `components/hh_player.lua`, `hh_monster.lua`, `hh_leveling.lua`; `main/hh_api.lua`; `enums/hh_enchant.lua`, `hh_effects.lua`; `scripts/ttk_elemental_combat.lua` trong `mods/PhamNhanTuTien`.

Các lỗi ban đầu đã xử lý:

1. Guard thiếu `health`/đã chết thoát sớm, không dereference nil.
2. Bỏ miền crit 0–100 có 101 kết quả; test biên 0/1/100% ở cả ba đường.
3. Xóa `soakStrike` theo quyết định bỏ cơ chế, không vá ngưỡng ướt từ 50 xuống 0,5.
4. Test số cố định khóa thứ tự né → attacker math → world rank/defense/vanilla → HP thực mất → trạng thái/lan/hút máu; không giảm pool hoặc world rank hai lần, không cho packet phụ sinh proc.

### Quyết định thiết kế đã duyệt — crit thường và Bạo Phát

Các quyết định dưới đây là contract đã duyệt và đã triển khai; những ghi chú “khi triển khai” là lịch sử thiết kế, không còn lệnh tạm dừng. Các hiệu chỉnh nguồn sát thương và bằng chứng Task 4.5/4.6/5 ở đầu mục này được ưu tiên nếu mô tả cũ còn khái quát.

- Giữ hướng chiến đấu Solo/ARPG với các con số sát thương lớn để tương xứng quái
  và boss có hàng triệu máu.
- Bốn proc cũ trở thành bốn affix vũ khí thật:
  - Bạo Phát I: 30% gây x1.5 sát thương.
  - Bạo Phát II: 20% gây x2 sát thương.
  - Bạo Phát III: 10% gây x3 sát thương.
  - Bạo Phát IV: 8% gây x5 sát thương.
- Chỉ vũ khí được mang Bạo Phát. Một vũ khí chỉ có tối đa một trong bốn cấp
  Bạo Phát; không cộng nhiều cấp trên cùng vũ khí.
- Bạo Phát và crit thường là hai lần kiểm tra độc lập. Nếu cùng kích hoạt, hai
  hệ số được nhân nối tiếp; ví dụ crit x3.5 cùng Bạo Phát IV tạo tổng x17.5.
- Crit thường giữ công thức hiện có: `x(2 + criticalHitEffect / 100)`.
- Tỷ lệ crit hiệu dụng bị chặn trong khoảng 0–100%; phần vượt 100% không đổi
  thành siêu crit hoặc một tầng crit khác.
- Chưa đặt trần cứng cho hệ số sát thương crit; nguồn chỉ số hiện tại hữu hạn
  và sẽ được cân bằng qua nguồn affix/chỉ số.
- Phép quay crit phải dùng miền 1–100 với điều kiện
  `roll <= clamp(criticalHitRate, 0, 100)`. Cách cũ `math.random(0, 100)` có
  101 kết quả và làm sai xác suất.
- Quy tắc tỷ lệ crit 0–100% phải được áp dụng thống nhất cho người chơi và các
  follower/đệ tử dùng pipeline crit Solo.
- Registry hiệu ứng phải bổ sung `moreDamage30To150`, vốn có nhánh xử lý trong
  code Solo cũ nhưng thiếu định nghĩa effect; ba key còn lại tiếp tục được giữ
  để không phá ID hiện có.
- Tên hiển thị của bốn proc phải đổi từ “Chí mạng x…” sang “Bạo Phát I–IV” để
  phân biệt rõ với crit thường.
- Việc tạo nguồn roll/ghép affix Bạo Phát thật thuộc phần trang bị, nhưng contract
  chiến đấu và kiểm tra độc quyền affix phải được test ngay trong kế hoạch mục 2.

Mốc tham chiếu cân bằng đã duyệt:

- 50 SEN tự cung cấp 50% tỷ lệ crit và +100% hiệu quả crit, tương đương crit x3.
- Nếu cộng thêm Bạo Kích IV tối đa +50 cho cả hai chỉ số: 100% crit, x3.5.
- Khi đồng thời nổ Bạo Phát IV: x3.5 x x5 = x17.5; đây là đỉnh bùng nổ được chủ
  đích cho phép trong hướng Solo/ARPG.

### Quyết định thiết kế đã duyệt — Xuyên Giáp

- Bỏ mô hình `trueDamageNum` là một lượng sát thương thật phẳng. Với STR tối đa
  chỉ thêm 200 và Xuyên Giáp IV hiện chỉ thêm 80–240, mô hình cũ không còn ý
  nghĩa trước quái/boss có hàng triệu máu.
- Giữ key/ID nội bộ hiện có để tránh phá save và dữ liệu trang bị, nhưng đổi ý
  nghĩa gameplay sang tỷ lệ phần trăm sát thương thật.
- Xuyên là gói bổ sung từ `pierce_base = sát thương gốc + cộng phẳng`, không nhận Công Kích, Nghịch Cảnh, crit hoặc Bạo Phát; không tách khỏi sát thương thường của đòn chính.
- Mỗi điểm STR cho `+0,1%` xuyên giáp; 200 STR cho 20%.
- Bốn affix vũ khí Xuyên Giáp dùng khoảng giá trị:
  - Xuyên Giáp I: 3–5%.
  - Xuyên Giáp II: 6–10%.
  - Xuyên Giáp III: 11–15%.
  - Xuyên Giáp IV: 16–20%.
- Tổng tỷ lệ xuyên giáp từ mọi nguồn bị chặn tối đa 40%.
- Sát thương xuyên giáp chỉ phát sinh khi đòn chính thực sự đánh trúng; đòn bị
  né, bị vô hiệu hoặc không gây sát thương không được tạo gói sát thương thật.
- Mục tiêu có hiệu ứng `immuneTrue` tiếp tục miễn nhiễm sát thương xuyên giáp.
- Các nguồn cũ ngoài STR/affix đang cộng số phẳng (ví dụ buff +100 và set +50)
  phải được quy đổi sang giá trị phần trăm trong kế hoạch triển khai; không được
  giữ nguyên số cũ dưới ngữ nghĩa mới.

### Quyết định thiết kế đã duyệt — Né

- Giữ quy đổi `1 AGI = 1% né`; 50 AGI cung cấp 50% né.
- Gộp nguồn né còn lại từ AGI, trang bị và buff vào một tỷ lệ hiệu dụng duy nhất; bộ Phi Vân đã xóa.
- Trần tổng tỷ lệ né hiệu dụng là **70%**.
- Phép quay né dùng miền 1–100 sau khi clamp tỷ lệ vào 0–70%.
- Kiểm tra né phải diễn ra trước crit thường và Bạo Phát để không tiêu proc hoặc
  hiện FX chí mạng cho một đòn đã bị né.
- Đòn bị né không gây sát thương thường, sát thương xuyên giáp, hiệu ứng đánh
  trúng, hút máu hoặc phản sát thương.
- Chỉ đòn đi qua pipeline `Combat:GetAttacked` được né. Đói, nóng/lạnh, độc và
  sát thương môi trường không được né.
- Pipeline để ngỏ một cờ/stimulus “không thể né” cho các kỹ năng boss đặc biệt
  cần ép người chơi xử lý cơ chế; không mặc định biến mọi đòn boss thành không
  thể né.

### Đối chiếu cơ chế giáp DST

- Đề xuất trần giảm sát thương 50% đã bị loại vì không phù hợp mục tiêu phòng
  thủ endgame của Phàm Nhân.
- Kiểm tra trực tiếp bản DST đang cài cho thấy hai món giáp vanilla không nhân
  nối tiếp tỷ lệ hấp thụ: `Inventory:ApplyDamage` dùng
  `absorbed_percent = math.max(amt, absorbed_percent)`. Vì vậy mũ 80% + áo 80%
  vẫn chỉ giảm 80% sát thương; tổng absorption chỉ dùng để chia hao độ bền giữa
  các món. Mốc 96% từ hai giáp 80% là cơ chế của Don't Starve bản đơn, không
  phải DST hiện tại.
- Pipeline Phàm Nhân hiện có thể đạt 96% theo cách khác: `absorbDamage` 80% của
  mod chạy trước giáp DST 80%, nên sát thương còn lại là `20% x 20% = 4%`.
- Phàm Nhân chủ đích giữ lớp giảm riêng của mod nhân với lớp giáp cao nhất của
  DST để có thể đạt ngưỡng 96%; đây là luật của mod, không được mô tả nhầm là
  hai món giáp vanilla DST cộng dồn.

### Quyết định thiết kế đã duyệt — VIT và giảm sát thương

- Đổi VIT từ trừ sát thương phẳng sang tỷ lệ: `1 VIT = 1%` giảm sát thương
  thường; 40 VIT cung cấp 40%.
- VIT và các nguồn giảm thương đã chuyển sang `absorbDamage`, cộng vào một pool tối đa 80%; bỏ cơ chế/nguồn giảm phẳng `reduceAttackedDamage` phía người chơi.
- Giáp DST giữ đúng cơ chế vanilla: nếu có nhiều món giáp, chỉ tỷ lệ hấp thụ cao
  nhất được dùng cho máu; các món chia hao độ bền, không nhân tỷ lệ mũ với áo.
- Pool Phàm Nhân là một lớp riêng và được nhân với lớp giáp DST:
  `damage_taken = damage x (1 - pham_nhan_reduction) x (1 - dst_armor)`.
- Ví dụ pool Phàm Nhân 80% cùng giáp DST 80% khiến người chơi nhận 4% sát thương ban đầu, tức giảm 96%. Runtime chặn pool Phàm Nhân ở 80% và giữ lớp giáp vanilla; không đặt một clamp 96% toàn cục lên mọi cơ chế miễn/giảm sát thương khác.
- Bỏ phép trừ phẳng sau giáp để không triệt tiêu hoàn toàn các đòn nhỏ ngoài né
  hoặc miễn nhiễm.
- Riêng packet Xuyên Giáp bỏ cả player pool và giáp vật lý; packet Độc bỏ giáp vật lý nhưng vẫn chịu player pool. Không gọi chung mọi packet đặc biệt là “sát thương thật”. Planar dùng phòng thủ planar riêng, không giảm bởi pool này.

### Quyết định thiết kế tạm duyệt — Hút Máu

- Hút Máu tính trên lượng máu mục tiêu thực sự mất bởi đòn hợp lệ, nên crit
  thường và Bạo Phát được phép làm tăng lượng hồi.
- Không hút máu từ sát thương xuyên giáp, sát thương theo phần trăm máu, độc,
  đốt, phản đòn, tự sát thương, đồng minh hoặc sinh vật triệu hồi thuộc sở hữu
  người chơi.
- Đánh lan được phép hút máu từ các mục tiêu hợp lệ.
- Mỗi lần gây sát thương chỉ được hồi tối đa 15% máu tối đa của người chơi.
- Tổng Hút Máu được hồi tối đa **90% máu tối đa trong mỗi cửa sổ một giây**, kể
  cả khi đánh nhanh hoặc trúng nhiều mục tiêu. Đây là thông số tạm thời, sẽ cân
  bằng lại bằng test mô phỏng/thực chiến nếu cần.
- Hiệu ứng cấm hoặc giảm hồi máu áp dụng sau khi tính các giới hạn trên.
- Đòn bị né, miễn nhiễm hoặc không làm mục tiêu mất máu không tạo hồi phục.

### Quyết định thiết kế đã duyệt — Trọng Thương và Kết Liễu

- `targetPercentDamage` được chuẩn hóa thành sát thương theo phần trăm **máu hiện
  tại** của mục tiêu trên mỗi đòn đánh trực tiếp hợp lệ.
- Trọng Thương gây tối đa 3% máu hiện tại mỗi đòn lên quái thường và tối đa 1%
  máu hiện tại mỗi đòn lên boss.
- Phần Trọng Thương được tính từ trạng thái mục tiêu sau khi xác nhận đòn đánh
  trúng, nhưng không được nhân bởi crit thường hoặc Bạo Phát.
- Trọng Thương vẫn chịu giáp và các lớp giảm sát thương của mục tiêu; đây không
  phải sát thương thật.
- Chỉ đòn đánh trực tiếp được kích hoạt Trọng Thương. Sát thương lan, độc, đốt,
  phản đòn và các tick sát thương gián tiếp không kích hoạt.
- Trọng Thương không tạo Hút Máu.
- Mục tiêu có `immuneTearing` miễn nhiễm hoàn toàn với Trọng Thương.
- `killUnderThreshold` giữ ngưỡng Kết Liễu 15%, nhưng chỉ áp dụng cho quái
  thường; boss và endgame boss không thể bị kết liễu bởi cơ chế này.

### Quyết định thiết kế đã duyệt — loại bỏ `soakStrike`

- Bỏ hoàn toàn cơ chế tăng sát thương theo độ ướt `soakStrike`; không sửa lại,
  đổi tên hoặc tái sử dụng thành một hiệu ứng chiến đấu mới.
- Khi triển khai, xóa nhánh runtime và nội dung hiển thị/đăng ký liên quan để
  tránh để lại một thuộc tính không thể nhận nhưng vẫn xuất hiện trong hệ thống.
- Không cần migration dữ liệu hoặc save cũ vì phạm vi hiện tại là lượt chơi mới.

### Quyết định thiết kế đã duyệt — nhóm Nghịch Cảnh

- Giữ ba dòng thuộc tính vũ khí hiện có: Thanh Long–Máu (`bloodOutburst`),
  Thanh Long–Não (`spiritFade`) và Thanh Long–Đói (`hungerAssault`).
- Xếp cả ba vào cùng một nhóm loại trừ mang tên **Nghịch Cảnh**; mỗi vũ khí chỉ
  được có tối đa một trong ba dòng này.
- Mỗi dòng tăng sát thương tuyến tính theo phần tài nguyên tương ứng mà người
  chơi đã mất: `bonus = 50% x (1 - tỷ lệ tài nguyên hiện tại)`, tối đa +50%.
- Trạng thái được đọc từ người chơi tấn công, không phải mục tiêu.
- Bonus đi vào nhóm cộng sát thương phần trăm trước crit thường và Bạo Phát;
  không khuếch đại Xuyên Giáp, Trọng Thương hoặc sát thương gián tiếp.
- Nhóm Nghịch Cảnh và nhóm Bạo Phát là hai nhóm độc lập, nên một vũ khí có thể
  đồng thời có một dòng Nghịch Cảnh và một dòng Bạo Phát.

### Quyết định thiết kế đã duyệt — loại bỏ sát thương điều kiện cũ

- Bỏ toàn bộ các dòng cộng sát thương theo thời điểm Sáng, Chiều và Tối:
  `sunlightStrike`, `afterglowStrike`, `nightMenace`.
- Bỏ toàn bộ các dòng cộng sát thương theo chủng mục tiêu, gồm Heo, Cá, Khỉ,
  Đồng Hồ, Nhện, Sói, Ếch, Côn Trùng, Bóng Tối, Boss/endgame boss và Thực Vật.
- Việc loại bỏ bao gồm cả dòng cường hóa/trang bị lẫn châu báu hoặc nguồn khác
  cấp các hiệu ứng tương ứng; không giữ riêng Boss hay Bóng Tối.
- Khi triển khai, xóa các nhánh runtime, đăng ký, mô tả và nguồn sinh tương ứng
  để chúng không tiếp tục làm loãng bảng thuộc tính hoặc rơi thành phần thưởng
  vô dụng.
- Không cần migration save cũ. Nhóm sát thương tổng quát `addComDamage` và các
  cấp Thanh Long I–IV là vấn đề riêng, chưa bị quyết định này loại bỏ.

### Quyết định thiết kế đã duyệt — Thanh Long I–IV

- Giữ bốn cấp dòng sát thương tổng quát Thanh Long trên vũ khí, nhưng đổi từ
  cộng sát thương phẳng sang cộng phần trăm sát thương đòn chính.
- Khoảng giá trị mới:
  - Thanh Long I: +3–5%.
  - Thanh Long II: +6–10%.
  - Thanh Long III: +11–15%.
  - Thanh Long IV: +16–20%, đồng thời giữ Trọng Thương theo luật đã duyệt.
- Bốn cấp thuộc cùng một họ loại trừ; mỗi vũ khí chỉ được có tối đa một cấp
  Thanh Long.
- Bonus Thanh Long áp dụng lên sát thương đòn chính trước crit thường và Bạo
  Phát; không khuếch đại Xuyên Giáp hoặc Trọng Thương.
- Giữ key/ID hiện có nếu cần để tránh phá registry nội bộ, nhưng nội dung hiển
  thị và ngữ nghĩa gameplay phải phản ánh giá trị phần trăm mới.

### Quyết định thiết kế đã duyệt — loại bỏ Đá Sát Thương

- Bỏ Đá Sát Thương (`damageBoostGem`) đang cộng `+20` sát thương phẳng.
- Khi triển khai, xóa hiệu ứng runtime, nguồn sinh/rơi, đăng ký và nội dung mô
  tả liên quan; không quy đổi viên đá này sang phần trăm.
- Tiếp tục giữ Đá Sức Mạnh `+10%` làm nguồn châu báu tăng Công Kích cơ bản.
- Quyết định này chưa thay đổi Bảo★Sát (`treasure_atk`) hoặc Siêu★Sát
  (`baconOmeletteBlessAtk`); hai nguồn đó được cân bằng riêng.

### Quyết định thiết kế đã duyệt — Bảo★Sát và Siêu★Sát

- Đổi Bảo★Sát (`treasure_atk`) từ `+50` sát thương phẳng thành `+15%` sát
  thương đòn chính.
- Đổi Siêu★Sát (`baconOmeletteBlessAtk`) từ `+100` sát thương phẳng thành
  `+20%` sát thương đòn chính.
- Hai nguồn này cộng vào cùng pool Công Kích với Đá Sức Mạnh và Thanh Long,
  áp dụng trước crit thường và Bạo Phát.
- Bảo★Sát và Siêu★Sát tăng đòn chính và lan; không khuếch đại Xuyên, Độc hoặc Trọng Thương.

### Quyết định thiết kế đã duyệt — cho phép build Công Kích dị

- Không tạo nhóm loại trừ giữa Đá Sức Mạnh, Bảo★Sát và Siêu★Sát.
- Cho phép khảm lặp cùng một loại châu báu Công Kích trên một trang bị và trên
  nhiều trang bị; giới hạn tự nhiên vẫn là số lỗ khảm hiện có của từng món.
- Không đặt thêm trần riêng cho tổng pool Công Kích ở giai đoạn thiết kế này.
  Người chơi được phép hy sinh các lựa chọn phòng thủ/tiện ích để dồn toàn bộ lỗ
  khảm vào một build sát thương cực đoan.

### Quyết định thiết kế đã duyệt — Siêu★Lan và sát thương lan

- Giữ châu báu Siêu★Lan (`baconOmeletteAOE`) ở mức 20% sát thương lan mỗi
  viên; mỗi trang bị chỉ được khảm một viên, nên ba món trang bị chuẩn cho tối
  đa 60%.
- Vùng lan có bán kính 3 và lấy tâm tại mục tiêu chính bị đánh, không lấy tâm
  tại người chơi.
- Kích hoạt với cả đòn đánh trực tiếp cận chiến và tầm xa, nhưng chỉ khi đòn
  chính thực sự đánh trúng và gây sát thương.
- Sát thương lan lấy theo sát thương đòn chính sau Công Kích, crit thường và
  Bạo Phát; từng mục tiêu phụ vẫn áp dụng giáp và giảm sát thương của chính nó.
- Gói sát thương lan không quay thêm crit/Bạo Phát và không kích hoạt Xuyên
  Giáp, Trọng Thương, Kết Liễu hoặc các hiệu ứng on-hit khác.
- Sát thương lan là nguồn Hút Máu hợp lệ theo các giới hạn Hút Máu đã duyệt.
- Chỉ gây sát thương lên mục tiêu thù địch hợp lệ; loại người chơi, đồng minh và
  sinh vật triệu hồi thuộc sở hữu người chơi. Không được phản ứng đệ quy để tạo
  thêm một vòng sát thương lan.

### Quyết định thiết kế đã duyệt — loại bỏ Phản Kích

- Bỏ toàn bộ hệ Phản Kích/phản sát thương tùy biến của Phàm Nhân, không quy đổi
  các giá trị phẳng cũ sang phần trăm.
- Xóa các dòng Phản Kích I–IV (`reflexiveInjury`), Đá Phản Đòn
  (`retaliateGem`), các thuộc tính phản sát thương của quái
  (`reboundDamageNum`, `reboundDamagePercent`) và nguồn sinh/rơi/mô tả liên
  quan.
- Loại các miễn nhiễm phản đòn riêng của hệ này khi chúng không còn công dụng.
- Task 5 đã xóa cả `BUFFS_CONFIG.reflect` / Phản Chấn +7 trong `wb_strengthen`: không còn producer, bind callback hoặc mô tả. Giữ generic `ontakedamage` vì `absorb_head` / `absorb_body` còn dùng, không renumber các mốc cường hóa khác.
- Quyết định không can thiệp cơ chế gai/phản sát thương vanilla của DST nếu một
  vật phẩm vanilla tự sở hữu cơ chế độc lập.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — loại bỏ Lá Chắn tinh thần

- Bỏ toàn bộ Lá Chắn I–II và hiệu ứng `sanReplaceDamageChance`.
- Không giữ cơ chế xác suất triệt tiêu toàn bộ sát thương rồi chuyển chi phí sang
  tinh thần; không sửa thành một lớp né hoặc khiên mới.
- Khi triển khai, xóa dòng thuộc tính, runtime, đăng ký, nguồn sinh/rơi và mô tả
  liên quan để tránh chồng thêm một tầng miễn sát thương lên Né và giảm thương.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — làm lại Độc tấn công

- Giữ cơ chế người chơi gây Độc và làm lại nhánh `atkAddPoisonChance` /
  `monster_poison`; không dùng sát thương phẳng `-5 HP / 2 giây` cũ.
- Một lần kích hoạt Hạ Độc từ đòn đánh trực tiếp đặt 1 tầng Độc, tối đa 5 tầng.
- Mỗi tầng tồn tại 10 giây và gây sát thương một lần mỗi 2 giây. Khi mục tiêu đã
  đủ 5 tầng, lần Hạ Độc tiếp theo làm mới thời gian của hiệu ứng.
- Mỗi tầng gây sát thương bằng 20% sát thương đòn chính trước Bạo Kích và Bạo
  Phát ở mỗi nhịp. Đủ 5 tầng gây tổng cộng 100% sát thương đòn nền mỗi 2 giây.
- Các tầng cộng tuyến tính, không nhân lũy tiến và có thể gộp thành một con số sát
  thương Độc mỗi nhịp. Nếu đủ 5 tầng trong trọn chu kỳ 10 giây thì có 5 nhịp,
  tổng sát thương Độc bằng 500% một đòn nền; khi tiếp tục làm mới hiệu ứng, mức
  duy trì là 100% một đòn nền mỗi 2 giây.
- Độc bỏ qua giáp thường để tạo một hướng build sát thương theo thời gian riêng.
- Sát thương Độc không Bạo Kích, không Bạo Phát, không kích hoạt Xuyên Giáp,
  Trọng Thương hoặc Kết Liễu và không cho hút máu.
- Hạ Độc là affix chỉ xuất hiện trên vũ khí; mỗi vũ khí chỉ có tối đa một cấp:
  Hạ Độc I `10%`, Hạ Độc II `20%`, Hạ Độc III `30%`, Hạ Độc IV `40%` tỷ lệ
  kích hoạt trên đòn đánh trực tiếp.
- Mỗi lần Hạ Độc thành công thêm 1 tầng và làm mới thời gian 10 giây của toàn bộ
  hiệu ứng; khi đã đủ 5 tầng, lần kích hoạt tiếp theo chỉ làm mới thời gian.
- Hạ Độc được phép cùng tồn tại với Bạo Phát, Thanh Long và Xuyên Giáp trên cùng
  một vũ khí. Giới hạn một cấp chỉ áp dụng riêng trong từng họ affix; Độc không
  hưởng hệ số của Bạo Kích, Bạo Phát hoặc Xuyên Giáp nên không tạo chuỗi nhân
  sát thương giữa các họ này.
- Xóa hai nhánh Độc cũ phía người chơi là `atkChanceAddPoison` và
  `hitChanceAddPoison`/Giáp Độc. Chúng dùng buff Độc phẳng cũ, trùng chức năng
  với Hạ Độc mới và không có nguồn cấp người chơi còn hoạt động.
- Chỉ hợp nhất nhánh Độc của người chơi ở mục này; các thuộc tính quái gây Độc
  lên người chơi vẫn được giữ để thiết kế ở phần quái.
- Không cần migration save cũ.

### Quyết định tên gọi đã duyệt — Giảm Hồi Máu

- Hiệu ứng chống hồi phục của ★Chu Tước-TM dùng tên hiển thị **Giảm Hồi Máu**.
- Không tiếp tục gọi hiệu ứng này là “Thiêu Đốt” vì nó không gây sát thương theo
  thời gian; cũng không dùng tên “Cấm Hồi” để người chơi hiểu ngay tác dụng.
- Đòn đánh trực tiếp lên mục tiêu chính áp dụng hiệu ứng: mục tiêu nhận ít hơn 90%
  từ mọi lượng hồi máu dương trong 5 giây; đòn đánh trực tiếp tiếp theo làm mới
  thời gian.
- Hiệu ứng không cộng tầng, không gây sát thương, có tác dụng với boss và không
  lan qua Siêu★Lan/AoE.
- Dùng `addSuppressAddHealth` làm nhánh kích hoạt duy nhất phía người chơi:
  Chu Tước-TĐ giữ tỷ lệ ngẫu nhiên 10–50%, còn ★Chu Tước-TM luôn kích hoạt 100%.
  Cả hai đều áp dụng đúng hiệu ứng 90% trong 5 giây đã duyệt.
- Bỏ `hitSuppressAddHealth`/Giáp Đốt và `healthSuppressNum`/Trừng Phạt phía người
  chơi; không giữ các bản phản ứng hoặc proc 20 giây trùng chức năng.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — loại bỏ Ban Phúc

- Bỏ toàn bộ Ban Phúc `attackToAddHealth` và buff `buff_10s_1_health`.
- Không giữ cơ chế 10% khi tấn công để hồi `1 máu/giây` trong 120 giây; hiệu ứng
  này gần như hồi phục thụ động vĩnh viễn khi đánh liên tục, không đáng kể ở cuối
  game nhưng quá miễn phí ở đầu game và trùng vai trò với Hút Máu.
- Khi triển khai, xóa runtime, đăng ký thuộc tính, nguồn cấp, buff và mô tả liên
  quan; không tạo cơ chế thay thế.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — loại bỏ Hồi Não

- Bỏ toàn bộ cơ chế Hồi Não `restoreSpirit`; không chuyển sang hồi theo phần trăm
  tinh thần tối đa hoặc tạo cơ chế thay thế.
- Bỏ dòng/affix Chu Tước-HN và các nguồn riêng chỉ cấp Hồi Não.
- Gỡ Hồi Não khỏi ★Chu Tước-TM; trang bị này vẫn giữ Hút Máu và Giảm Hồi Máu
  theo các quyết định đã duyệt.
- Khi triển khai, xóa runtime, đăng ký thuộc tính, nguồn cấp và mô tả liên quan.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — làm lại Đóng Băng

- Giữ `atkChanceAddFreeze` và làm lại thành affix Đóng Băng chỉ có trên vũ khí;
  bỏ nhánh bị động `hitChanceAddFreeze`/Giáp Băng phía người chơi.
- Chỉ đòn đánh trực tiếp lên mục tiêu chính mới có thể kích hoạt; AoE, Độc và các
  proc sát thương phụ không kích hoạt Đóng Băng.
- Khi kích hoạt, quái thường bị đóng băng 2 giây. Boss không bị đóng băng hoàn
  toàn mà bị làm chậm 20% trong 2 giây.
- Sau khi hiệu ứng kích hoạt, chính mục tiêu đó có hồi chiêu 5 giây trước khi có
  thể nhận một lần Đóng Băng/làm chậm mới; hồi chiêu này ngăn khóa cứng nhưng
  không ngăn người chơi kích hoạt lên mục tiêu khác.
- Đóng Băng là affix chỉ xuất hiện trên vũ khí; mỗi vũ khí có tối đa một cấp:
  Đóng Băng I `5%`, Đóng Băng II `10%`, Đóng Băng III `15%`, Đóng Băng IV
  `20%` tỷ lệ kích hoạt trên đòn đánh trực tiếp.
- Các proc Đóng Băng của quái chưa bị xóa hoặc thay đổi tại mục này.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — chuẩn hóa Liên Kích

- Giữ Liên Kích làm affix tốc đánh chỉ có trên vũ khí; mỗi vũ khí có tối đa một
  cấp: Liên Kích I `5–10%`, II `15–25%`, III `30–45%`, IV `50–70%`.
- Các khoảng mới không chồng lấn để affix cấp cao luôn mạnh hơn cấp thấp.
- Tổng thưởng tốc đánh từ hệ Phàm Nhân bị chặn ở `+100%`, tương đương tối đa
  `×2` tốc đánh; hệ số tác động cả animation tấn công và khoảng nghỉ tối thiểu
  giữa hai đòn.
- Liên Kích được phép cùng tồn tại với các affix sát thương và trạng thái khác.
- Xóa khóa lỗi/không dùng `atkSpeedatkSpeed`, chỉ giữ khóa runtime `atk_speed`.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — giới hạn tốc chạy

- Giữ affix Nhanh Nhẹn trên vũ khí và chuẩn hóa khoảng giá trị thành `5–25%` tốc
  chạy; giữ các nguồn ngọc `+3%` và `+6%` hiện có.
- Tất cả nguồn `addSpeedPercent` thuộc Phàm Nhân cộng chung và bị chặn ở tổng
  `+50%` tốc chạy.
- Trang bị, mặt đường và các multiplier vanilla của DST vẫn áp dụng độc lập sau
  pool Phàm Nhân; không gộp chúng vào trần `+50%` này.
- Tốc chạy không làm tăng tốc đánh, tốc làm việc hoặc animation hành động.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — loại bỏ set Bạch Hổ Thiên Cương

- Bỏ toàn bộ `suit_bhtg` và ba dấu set `z_suit_bhtg_hand`,
  `z_suit_bhtg_body`, `z_suit_bhtg_hat`.
- Xóa công thức tạo ba dấu, đăng ký/tên set, kiểm tra kích hoạt, set bonus và nhánh
  runtime khiến người mặc nhận thêm 20% sát thương.
- Vì xóa cả set, không cần chuyển đổi các bonus cũ gồm Trọng Thương, Hồi Não,
  `+50` sát thương phẳng, `+10%` sát thương và Giảm Hồi Máu.
- Không xóa Hợp Thành Đài `hh_suit_build`, Đá Thuộc Tính hoặc asset dùng chung vì
  các set/effect khác vẫn sử dụng chúng.
- Không xóa `special_bhtg`: tên nội bộ gây nhầm này hiện đại diện cho ★Thanh Long
  IV và được xử lý theo quyết định Thanh Long đã duyệt.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — loại bỏ set Phi Vân Dật Ảnh

- Xóa toàn bộ `suit_fyyy` và ba khóa thừa `z_suit_fyyy_hand`,
  `z_suit_fyyy_body`, `z_suit_fyyy_hat`.
- Xóa tên/cấu hình set và nhánh runtime cho thêm một lần né độc lập 30%.
- Lý do: set không có định nghĩa hoàn chỉnh hoặc công thức tạo ba dấu nên hiện
  không thể kích hoạt; nếu được phục hồi, lần né riêng còn phá quy tắc một lần
  roll và trần Né 70% đã duyệt.
- Không cần migration save cũ.

### Quyết định thiết kế đã duyệt — loại bỏ set Thánh Quang Tí Hựu

- Xóa toàn bộ `suit_yhby` và ba dấu set `z_suit_yhby_hand`,
  `z_suit_yhby_body`, `z_suit_yhby_hat`.
- Xóa công thức tạo ba dấu, tên/cấu hình set, kiểm tra kích hoạt và toàn bộ nhánh
  runtime của set.
- Không giữ lại các hiệu ứng cũ: miễn Giảm Hồi Máu, miễn Ẩm Ướt, miễn Độc,
  giảm phẳng `10` sát thương nhận vào, hoặc proc hồi `1 HP/giây` trong `10` giây
  khi bị đánh với hồi chiêu `20` giây.
- Xóa buff ẩn và listener `attacked` chỉ phục vụ set; không chuyển proc hồi máu
  diện rộng bán kính `10` sang hệ khác vì Phàm Nhân được cân bằng cho chơi đơn.
- Không cần migration save cũ.

### Kết luận kỹ thuật đã triển khai — bốn điểm kiểm chứng cuối của pipeline

1. **Hai guard `health` đã sửa.** `HHPlayer:DoAttackDamage()` và `GetBlockDamage()` thoát sớm nếu thiếu health hoặc đã chết; test đủ trường hợp thiếu component, đã chết và còn sống.
2. **Miền quay crit 0–100 là lỗi thật ở cả ba đường đánh.** Người chơi trong
   `HHPlayer:DoAttackDamage()`, quái/đệ tử có `hh_monster` trong
   `HHMonster:DoAttackDamage()`, và đệ tử không có `hh_monster` trong
   `ApplyFollowerCritical()` trước đây dùng `math.random(0, 100) <= rate`.
   Đã chuẩn hóa cả ba sang `roll = math.random(1, 100)` và
   `roll <= clamp(rate, 0, 100)`. Test biên: 0% không bao giờ nổ, 1% chỉ nổ ở
   roll 1, 100% luôn nổ.
3. **Đã xóa `soakStrike`.** Nhánh cũ so
   `GetMoisturePercent() >= 50` dù API này dùng tỷ lệ chuẩn hóa. Tuy nhiên cơ chế
   tăng sát thương theo độ ướt đã được duyệt bỏ hoàn toàn, nên đã xóa nhánh
   runtime, key registry và mọi nguồn cấp; không vá ngưỡng thành
   `0.5`.
4. **Đã khóa thứ tự pipeline bằng test trước khi thay code.** Code cũ tính crit/Bạo Phát trước Né; code hiện tại áp dụng thứ tự:
   - kiểm tra attacker/target hợp lệ và còn sống;
   - quay đúng một lần Né; nếu né thì dừng toàn bộ đòn và không quay proc;
   - dựng sát thương đòn chính trước crit từ sát thương gốc và các bonus hợp lệ;
   - quay crit thường và đúng một affix Bạo Phát, độc lập với nhau;
   - áp dụng Xuyên Giáp, pool giảm thương Phàm Nhân và cơ chế giáp/kháng vanilla;
   - ghi nhận lượng HP mục tiêu thực sự mất;
   - sau khi đòn chính trúng mới xử lý các gói riêng như Trọng Thương, Độc,
     Giảm Hồi Máu, Đóng Băng, sát thương lan và Kết Liễu theo đúng contract riêng;
   - Hút Máu chỉ lấy từ sát thương thực tế của các gói được phép, không lấy từ
     Trọng Thương/Độc/Kết Liễu và vẫn chịu trần đã duyệt.
5. Test pipeline dùng các con số cố định để phát hiện đổi thứ tự, đồng thời
   chứng minh: VIT/pool Phàm Nhân chỉ giảm đúng một lần; world-rank chỉ nhân đúng
   một lần; giáp/kháng vanilla vẫn chạy; Bạo Phát và crit không quay khi né; các
   gói phụ không tự sinh proc dây chuyền; Hút Máu dùng delta HP sau mitigation
   thay vì damage đầu vào.
6. Live smoke bắt được khác biệt engine: `Freezable:Freeze(2)` chuyển sang THAWING sau 2 giây nhưng vẫn đóng băng. Task 5 thay timer wear-off của lần proc bằng `Unfreeze()` đúng 2 giây; native Freeze về sau hoặc component removal vẫn hủy timer cũ, boss slow/ICD không đổi. Test dùng Freezable thật của build DST đang cài.

### Bằng chứng Task 5 — 2026-09-22

- Combat math 6, pipeline 26, status 29, catalog 31, elemental 3, boss-food 9: tổng 104 unittest PASS. Lục Nguyên, armor, weapon Solo, strengthen và forge: các block PASS. Vitest: 34 file / 233 test PASS. Biên dịch 641 file Lua đạt.
- Live DST build 747465: `PHAM_NHAN_COMBAT_SMOKE_PASS` tại `[00:01:23]`, runner exit 0; log `.superpowers/pham-nhan-combat-runtime/run-848a598df4b1/combat.log`. PID 28504 shutdown sạch, không còn process audit thuộc sáu lượt chạy. Đã chứng minh né trước RNG, crit ×17,5, Xuyên cộng thêm 40%, giảm thường 96%, lan 60%, hút máu 15%/90%, Trọng Thương 3%/1%, boss không Kết Liễu, freeze/slow/ICD và Độc 5 tầng hết hạn sau refresh.
- Tại thời điểm Task 5, cổng tích hợp còn một FAIL do metadata ghi `59adb770...` trong khi source thực tế là `fe66a958...`. Corrective Task 5.2 đã chứng minh source repo và source Steam Workshop giống byte tuyệt đối 660/660 file, rồi sửa đúng hai hash metadata lỗi thời. Cổng hiện PASS 13/13; xem phần Task 5.2 bên dưới.
- Full-tree SHA256 trước/sau khớp tuyệt đối: Solo 660 file, `2937640068` 2006 file, AchievementLevel 2012 file; xem `task-5-source-before.json` / `task-5-source-after.json` cùng thư mục report. Lệnh kiểm kê exit 0, marker `HISTORICAL_SOURCE_TREES_UNCHANGED`.
- HUD runner có sẵn còn một lỗi fixture `tests/hud/test_hover_readability.lua:3`, global `Class` nil; sáu file HUD khác đạt. Không sửa các file đó trong Task 5. `git diff --check` toàn workspace còn whitespace có sẵn tại `hh_leveling.lua:349`; diff Task 5 so 10 snapshot có 0 chẩn đoán whitespace, hai file mới cũng sạch. Chưa có kiểm thử client đồ họa.
- File Task 5: `tools/run_phamnhan_combat_smoke.py`, `tools/test_ttk_solo_integration.py`; trong mod: `tools/combat_smoke.lua`, `tools/boss_smoke.lua`, `tools/test_strengthen_only.py`, `tools/test_combat_status.py`, `scripts/components/wb_strengthen.lua`, `scripts/combat/hh_combat_status.lua`, `main/hh_tunning.lua`, `README_VI.md`, `Wiki.txt`; và handoff này. Không commit/stage/reset/clean.

Lệnh acceptance chính (lệnh matrix đầy đủ, RED/GREEN và aggregate hashes nằm trong [report Task 5](.superpowers/sdd/2026-09-21-pham-nhan-combat-pipeline/task-5-report.md)):

```powershell
& 'C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/run_phamnhan_combat_smoke.py --timeout 240
# exit 0; PHAM_NHAN_COMBAT_SMOKE_PASS
& 'C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' tools/test_ttk_solo_integration.py
# exit 0; 13/13 top-level tests, nested combat 95, compile 641 Lua
& 'C:/Users/NYX/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' .superpowers/sdd/2026-09-21-pham-nhan-combat-pipeline/task-5-source-hashes.py after
# exit 0; HISTORICAL_SOURCE_TREES_UNCHANGED
```

### Bằng chứng corrective Task 5.1 — 2026-09-22

- Đã sửa lỗi phòng thủ quái: `GetBlockDamage()` chỉ chạy **một lần** cho phần sát thương thường; tỷ lệ có chặn `post / pre` được chặn trong `0..1` và tái sử dụng đúng một lần cho `hh_armor_pierce`. Chặn toàn phần, chặn phẳng, phần trăm, thời gian/tầm đánh và cap vì vậy cho normal/Xuyên cùng một kết quả, không quay RNG hay phát block FX lần hai. Các gói `hh_*` khác giữ cách giảm phần trăm cũ; Xuyên bị loại khỏi loop đó để không giảm hai lần.
- Đã dành riêng đúng stimulus `hh_unavoidable` để bỏ qua Né. Mọi stimulus khác vẫn Né được; boss thông thường không tự có quyền bỏ Né. Test giữ nguyên argument/vararg và return tuple của `Combat:GetAttacked`.
- RED 3/3 đúng regression; GREEN: pipeline 29, math 6, status 29, catalog 31, nested integration 95; biên dịch 641 Lua đạt. Live cluster `.superpowers/pham-nhan-combat-runtime/run-4a91559767db` dùng Wilson và hound thật, phát marker `real hh_monster full block zeros normal and piercing`, sau đó `PHAM_NHAN_COMBAT_SMOKE_PASS`, exit 0.
- Exact destination pin `main/hh_api.lua` đã cập nhật thành SHA256 `2ace97ef4727fac788066545f0f16d76b2130498d8c38d304f1b93c1db398b41`; không thêm wildcard hay nới allowlist. Ở thời điểm Task 5.1, cổng vẫn còn mismatch metadata lịch sử; Task 5.2 đã giải quyết mismatch này bằng đối chiếu source Workshop và cổng hiện PASS.
- Ba cây nguồn lịch sử vẫn khớp đủ 660 / 2006 / 2012 file, marker `HISTORICAL_SOURCE_TREES_UNCHANGED`; scoped whitespace sạch. Báo cáo chi tiết: `.superpowers/sdd/2026-09-21-pham-nhan-combat-pipeline/task-5-1-report.md`.

### Bằng chứng corrective Task 5.2 — 2026-09-22

- Đối chiếu toàn bộ `mods/3780347550` với `C:/Program Files (x86)/Steam/steamapps/workshop/content/322330/3780347550`: mỗi bên 660 file, không thiếu/thừa và không có file khác byte. `main/hh_tunning.lua` ở cả hai bên có SHA256 `fe66a9583fe344681f58dc97a13238ac05a02a34c283db2ca259b26e51f71d72`.
- Hash `59adb770...` cũ chỉ tồn tại trong `SOLO_SOURCE_MANIFEST.json` và baseline kiểm thử. Đã sửa đúng hai trường metadata sang hash source Workshop hiện hành; không sửa bất kỳ file source lịch sử nào, không nới allowlist và không đổi aggregate source tree.
- Cổng tích hợp fresh hiện exit 0: 13/13 top-level PASS, nested combat 95 PASS, compile 641 Lua. Báo cáo: `.superpowers/sdd/2026-09-21-pham-nhan-combat-pipeline/task-5-2-report.md`.

## Trạng thái workspace và cảnh báo bàn giao

- Working tree đang có nhiều thay đổi/untracked từ các task khác (UI hợp nhất, wiki web, boss indicator, font forge, ảnh và artifact). Không reset, checkout, clean hoặc hoàn nguyên chúng.
- Chỉ stage/commit đúng các file của task này nếu người dùng yêu cầu. Kiểm tra diff từng file vì có nhiều công việc chạy chung một thư mục.
- Hai file của task này hiện là untracked: `mods/PhamNhanTuTien/Wiki.txt` và `mods/PhamNhanTuTien/tools/test_solo_progression.py`.
- `scripts/widgets/hh_help_ui.lua` của Solo cũ đã được thay có chủ đích bằng `scripts/screens/ttk_unified_screen.lua`; test tích hợp có mapping replacement.
- Workspace hiện tại: `C:\Users\NYX\company\dst_wiki`; các lệnh `hoanc` ở phần lịch sử trên thuộc host cũ.

## Yêu cầu tiếp theo của người dùng

Người dùng đã yêu cầu “Làm đi” cho Mục 2; Mục 2 hiện đã triển khai và xác minh xong. Phần Achievement/chuyên sâu nhân vật khác vẫn giao task khác. Điểm rà tiếp theo trong danh sách là Mục 3 — Kỹ năng Thợ Săn, không tự mở rộng triển khai ngoài yêu cầu.
