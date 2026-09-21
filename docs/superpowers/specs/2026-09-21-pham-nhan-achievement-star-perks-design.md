# Thiết kế hợp nhất Thành Tựu, Star và Perk vào Phàm Nhân

## 1. Bối cảnh

Nguồn Workshop gốc của **Achievement & Level** nằm tại `mods/2937640068` và chỉ dùng để đối chiếu. Bản sao làm việc hiện tại nằm tại `mods/AchievementLevel`. Runtime đích là **Phàm Nhân Tu Tiên 2.0** tại `mods/PhamNhanTuTien`.

Phàm Nhân đã tích hợp Solo Leveling và đã có hệ cấp chính thức `hh_leveling`. Vì vậy lần hợp nhất này chỉ lấy ba phần còn phù hợp từ Achievement & Level:

- Thành Tựu và phần thưởng Star;
- Perk tiêu Star;
- Nhiệm vụ mùa trao EXP.

Hệ Level riêng của Achievement & Level, toàn bộ UI Level cũ và hệ điểm thuộc tính cũ không được nhập vào Phàm Nhân.

Các tài liệu đã chốt trước đó vẫn là ràng buộc đầu vào:

- `docs/superpowers/specs/2026-09-21-seasonal-task-redesign-design.md`;
- `docs/superpowers/plans/2026-09-21-seasonal-task-redesign.md`;
- `docs/superpowers/specs/2026-09-21-pham-nhan-unified-level-progression-design.md`;
- `docs/superpowers/plans/2026-09-21-pham-nhan-unified-level-progression.md`.

Nếu tài liệu cũ còn gọi mod là Tu Tiên Ký hoặc coi Solo Leveling là mod ngoài, quy tắc đặt tên hiện hành của repository được ưu tiên: đây là Phàm Nhân Tu Tiên 2.0 và Solo đã được tích hợp.

## 2. Mục tiêu

- Đưa Thành Tựu, Star, Perk và nhiệm vụ mùa vào chính `mods/PhamNhanTuTien`.
- Chỉ có một hệ Level/EXP: `hh_leveling` của Phàm Nhân.
- Có 231 thành tựu hoạt động đã duyệt; không còn mục `NEED`/tương lai ẩn trong catalog này.
- 231 thành tựu cho đúng 1.000 Star khi claim hết.
- Có 39 Perk được giữ lại: 7 chỉ số lặp, 14 khả năng một lần và 18 gói chế tạo một lần.
- Tổng chi phí mua tối đa hiện tại là 945 Star, để lại 55 Star dư sau khi hoàn thành mọi thành tựu hoạt động.
- Nhiệm vụ mùa có bốn catalog khác nhau, mỗi mùa 50 nhiệm vụ và rút cố định 20 nhiệm vụ khi bắt đầu mùa.
- Wiki không còn route độc lập `/achievement-level`; nội dung mới nằm trong khu vực Phàm Nhân.
- Hệ thống chạy server-authoritative, lưu/đọc ổn định và không thể nhận Star/EXP hai lần do spam RPC hoặc reload.

## 3. Ngoài phạm vi

- Không thay EXP curve, nguồn EXP, AP hay quy tắc lên cấp đã chốt trong task unified progression.
- Không thêm lại perk đã bị loại trong phiên duyệt.
- Không hỗ trợ chạy đồng thời mod Achievement & Level độc lập với Phàm Nhân.
- Không chỉnh nguồn Workshop gốc `mods/2937640068`.
- Không tự động nhập Level, EXP, attribute point hoặc perk cũ từ save của mod Achievement & Level độc lập.

## 4. Quyết định kiến trúc

### 4.1. Một runtime Phàm Nhân, không phụ thuộc mod ngoài

Phàm Nhân sở hữu toàn bộ định nghĩa, component, RPC, widget và save state mới. Không `require`, `modimport` hay kiểm tra phụ thuộc runtime vào `mods/AchievementLevel`.

Chỉ port các hàm, asset và prefab thực sự còn được dùng. Mỗi phần được port phải giữ provenance/license phù hợp. Không sao chép toàn bộ mod cũ vì phần lớn code thuộc Level cũ, perk đã loại, character-specific task và content không còn cần thiết.

### 4.2. `hh_leveling` là chủ sở hữu Level duy nhất

- Không attach component `levelsystem`.
- Không khai báo netvar Level/EXP cũ.
- Không port `main_levelpostInits.lua`, `leveldata.lua`, `levelfunctions.lua` hay UI Level cũ.
- Không có thanh Level thứ hai và không có nút Level trong cửa sổ Thành Tựu.
- Achievement completion chỉ mở Claim Star, không trao EXP.
- Seasonal Claim XP gọi API progression chính thức của Phàm Nhân.
- Perk XP Multiplier được áp dụng trong pipeline EXP chính thức, không bọc trực tiếp `hh_leveling:AddExp` bằng một hệ song song.

### 4.3. Một component server-authoritative

Một component mới thuộc Phàm Nhân quản lý:

- tiến độ và claim của Thành Tựu;
- số Star kiếm được/đã tiêu;
- cấp hoặc trạng thái unlock của Perk;
- trạng thái nhiệm vụ mùa;
- phiên bản save và migration nội bộ của hệ thống mới.

Client chỉ nhận snapshot cần hiển thị và gửi yêu cầu claim/mua. Server luôn tự kiểm tra điều kiện, giá, giới hạn cấp và trạng thái claim trước khi thay đổi dữ liệu.

Logic thuần không phụ thuộc DST entity được tách khỏi component để kiểm thử catalog, claim, giá và state transition bằng Lua harness.

### 4.4. Tu luyện và luyện đan là tiến trình riêng, không phải Level thứ hai

Việc đưa đan dược Tu Tiên trở lại không khôi phục `levelsystem` của Achievement & Level. Phàm Nhân có hai khái niệm độc lập:

- `hh_leveling` tiếp tục là Level/EXP chính duy nhất, dùng cho Level 1–100, AP và hạng thợ săn;
- cảnh giới Tu Tiên là một tiến trình tuần tự riêng gồm 15 lần dùng đan, không có EXP bar, AP hay level component thứ hai.

Đan tăng cảnh giới chỉ dùng được đúng ở cảnh giới liền trước. Dùng đúng đan thì thăng cảnh giới chắc chắn; dùng sai thứ tự bị từ chối và không tiêu hao vật phẩm. Không có xác suất thất bại khi luyện đan hoặc khi đột phá.

Đan Lô `xd_liandanlu` được đưa vào Phàm Nhân với công thức 5 Cục Vàng + 3 Đá Cắt + 3 Đá Lửa + 5 Hạ Phẩm Linh Thạch. Một mẻ hợp lệ hoàn thành sau 180 giây và luôn trả đúng thành phẩm. Không port Thế Tử Phản Hồn Đan, Phế Đan hay nhánh kết quả thất bại.

## 5. Catalog Thành Tựu

### 5.1. Nguồn sự thật

Danh sách đã duyệt trong phiên làm việc này được mã hóa thành một catalog Lua duy nhất trong Phàm Nhân. Không tự động trộn lại 169 thành tựu cũ và không suy ra danh sách mới lúc runtime.

Mỗi định nghĩa có tối thiểu:

```lua
{
    id = "stable_snake_case_id",
    group = "food",
    name = "Tên hiển thị",
    description = "Điều kiện hoàn thành",
    tracker = "eat_prefabs",
    target = 1,
    reward = 3,
    status = "active", -- active hoặc future
    visibility = "visible", -- visible hoặc hidden
    params = {...},
}
```

ID là khóa save ổn định và không đổi khi sửa tên hiển thị. `tracker + params + target` là chữ ký ngữ nghĩa dùng để phát hiện thành tựu trùng lặp.

### 5.2. Số lượng cố định

- Tổng định nghĩa: 231.
- Hoạt động, hiển thị và claim được: 231.
- Tương lai ẩn: 0.
- Nhóm: 13 nhóm đã duyệt.
- Mỗi thành tựu chỉ thuộc một nhóm.

| Nhóm | Tổng | Active | Future ẩn |
|---|---:|---:|---:|
| Sinh tồn | 10 | 10 | 0 |
| Ẩm thực | 40 | 40 | 0 |
| Thu thập | 33 | 33 | 0 |
| Lao động | 11 | 11 | 0 |
| Chế tạo | 20 | 20 | 0 |
| Nông nghiệp | 15 | 15 | 0 |
| Chiến đấu | 14 | 14 | 0 |
| Boss | 33 | 33 | 0 |
| Cấp và hạng | 13 | 13 | 0 |
| Cường hóa | 12 | 12 | 0 |
| Hầm ngục và Hiệp hội | 12 | 12 | 0 |
| Nhiệm vụ mùa | 8 | 8 | 0 |
| Gacha và cửa hàng | 10 | 10 | 0 |
| **Tổng** | **231** | **231** | **0** |

Ba nhóm cũ bị xóa hoàn toàn, không chỉ ẩn: Khám phá và Hang động; Bóng Ma và Đệ Tử; Đại dương và Hàng hải.

Toàn bộ 22 mục từng được để `NEED` đã có quyết định sản phẩm: 19 mục Ẩm thực được đóng đinh tại mục 5.4, một mục Chế tạo là Đan Lô, và hai mục Cấp/Hạng là SS cùng SSS. Catalog phát hành không còn placeholder `future`.

### 5.3. Phân phối đúng 1.000 Star

| Độ khó | Số lượng | Star/mục | Thành tiền |
|---|---:|---:|---:|
| Dễ | 71 | 2 | 142 |
| Thường | 57 | 3 | 171 |
| Khó | 55 | 5 | 275 |
| Tinh Anh | 34 | 8 | 272 |
| Huyền Thoại | 14 | 10 | 140 |
| **Tổng** | **231** |  | **1.000** |

Catalog validator phải fail nếu lệch bất kỳ số lượng hoặc tổng nào.

### 5.4. Nội dung bắt buộc đã chốt

Catalog cuối phải phản ánh toàn bộ lựa chọn đã duyệt, gồm các ràng buộc nổi bật sau:

- Nhóm ẩm thực có các nội dung Phàm Nhân/Tu Tiên, vật phẩm boss và đan dược; có một thành tựu uống đủ `nn_liquidluck`, `nn_liquidluck_2`, `nn_liquidluck_3`.
- Đan dược Thao Thiết chỉ dùng cấp đầu tiên nhưng tên hiển thị bỏ chữ “Nhất Phẩm”.
- Nhóm thu thập có các mốc sở hữu 10.000 linh thạch hạ phẩm, 10.000 trung phẩm, 1.000 thượng phẩm và 100 cực phẩm.
- Không có thành tựu hoàn thành bộ Dreadstone/Lunarplant/Voidcloth.
- Không có các thành tựu bắt Ice Bream, Scorching Sunfish, Bloomfin Tuna hoặc Fallounder.
- Không có thành tựu thuần hóa Beefalo, nhận nuôi năm Critter, hoàn thành chu kỳ ba chuồng, Hoán Nguyệt Trì hoặc đủ sáu linh thảo.
- Không có nhóm 7 đã bị loại.
- Không có các thành tựu bẫy/sát thương gián tiếp, thiêu cháy, đóng băng, điện, sáu Nguyên Kiếm hoặc tay không đã bị loại.
- Boss chỉ giữ boss có ý nghĩa; loại boss cấp thấp và boss có chuỗi nhiệm vụ/triệu hồi quá phức tạp theo danh sách đã duyệt.
- Mốc Level là 10, 20, 30, 50 và 100.
- Hạng thợ săn là E, D, C, B, A, S, SS và SSS. Mốc cấp tương ứng là 1/10/20/30/40/50/70/100. SS và SSS tạm thời chỉ đổi tên hạng và hoàn thành thành tựu, không tăng chỉ số, EXP multiplier, shop tier hay quyền gameplay khác.
- Nhóm nhiệm vụ mùa giữ “Nhiệm Vụ Đầu Tiên”, không có “Trọn Bộ Nhiệm Vụ Mùa”.

### 5.5. Danh sách chính xác 19 mục Ẩm thực từng để TODO

19 mục sau là thành tựu hoạt động, không còn là placeholder:

| ID ổn định | Tên hiển thị | Điều kiện |
|---|---|---|
| `food_liquid_luck_trinity` | Phúc Lạc Tam Dược | Uống đủ Phúc Lạc Dược I, II và III. |
| `food_cultivation_pill_path` | Đan Đạo Thông Huyền | Dùng đủ 15 đan tăng cảnh giới theo đúng tiến trình từ Tụ Khí Hoàn đến Khấu Hư Đan. |
| `food_fasting_pill` | Tịch Cốc | Dùng một Tịch Cốc Đan. |
| `food_buff_cyfxd` | Xích Dương Phần Huyết Đan | Dùng `xd_dy_cyfxd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_dmhsd` | Địa Mạch Hồi Sinh Đan | Dùng `xd_dy_dmhsd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_lmsqd` | Lôi Minh Sát Khí Đan | Dùng `xd_dy_lmsqd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_qxdhd` | Thanh Tâm Địch Hồn Đan | Dùng `xd_dy_qxdhd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_yfsxd` | Ngự Phong Thần Hành Đan | Dùng `xd_dy_yfsxd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_pshsd` | Bàn Thạch Hộ Thân Đan | Dùng `xd_dy_pshsd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_qjqsd` | Thiên Cơ Xảo Thủ Đan | Dùng `xd_dy_qjqsd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_xynyd` | Huyền Dương Noãn Ngọc Đan | Dùng `xd_dy_xynyd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_hsphd` | Hàn Tủy Tịch Hỏa Đan | Dùng `xd_dy_hsphd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_buff_xttyd` | Huyết Thao Thiết Nguyên Đan | Dùng `xd_dy_xttyd_1`; tên hiển thị bỏ “Nhất Phẩm”. |
| `food_boss_baihu` | Bạch Hổ Huyết Tủy | Ăn một `ttk_boss_core_baihu`. |
| `food_boss_jfsn` | Kim Phượng Tinh Huyết | Ăn một `ttk_boss_core_jfsn`. |
| `food_boss_qlch` | Kỳ Lân Linh Đan | Ăn một `ttk_boss_core_qlch`. |
| `food_boss_spiderqueen` | Ma Thù Nội Đan | Ăn một `ttk_boss_core_spiderqueen`. |
| `food_boss_stalke` | Hắc Ám Hồn Tinh | Ăn một `ttk_boss_core_stalke_fuben`. |
| `food_boss_deerclops` | Băng Phách Tinh Tủy | Ăn một `ttk_boss_core_deerclops_ziyun`. |

Sáu vật phẩm Boss trên đã có prefab và logic ăn trong Phàm Nhân; ghi chú cũ nói chúng chưa có prefab là sai và bị loại khỏi đặc tả.

15 đan tăng cảnh giới của `food_cultivation_pill_path` là: Tụ Khí Hoàn, Đoán Thể Hoàn, Trúc Cơ Đan, Tẩy Tủy Hoàn, Hóa Tinh Đan, Vân Trung Đan, Sơ Mạch Hoàn, Dung Linh Hoàn, Kết Anh Đan, Uẩn Huyết Hoàn, Ngưng Thần Hoàn, Hóa Thần Đan, Hồi Nguyên Hoàn, Hợp Linh Hoàn và Khấu Hư Đan.

### 5.6. Claim Star

Hoàn thành và nhận thưởng là hai trạng thái khác nhau:

```text
locked -> completed_unclaimed -> claimed
```

- Thành tựu hoàn thành chỉ bật nút Claim.
- Claim hợp lệ cộng Star đúng một lần rồi lưu `claimed` ngay trong cùng transaction.
- Reload, double-click hoặc gửi lại RPC không thể cộng lần hai.
- Thành tựu đã claim vẫn hiện là hoàn thành nhưng nút Claim biến mất.

## 6. Star và Perk

### 6.1. Kinh tế tổng

| Hạng mục | Chi phí tối đa |
|---|---:|
| 7 perk chỉ số | 560 |
| 14 perk khả năng | 179 |
| 18 perk chế tạo | 206 |
| **Tổng** | **945** |

Với 1.000 Star kiếm được, người chơi có thể max toàn bộ hệ thống hiện tại và còn 55 Star. Khoản dư được giữ có chủ đích cho nội dung sau này.

### 6.2. Nhóm Chỉ Số

Cả bảy perk có cấp tối đa 25 và dùng cùng biểu giá theo cấp được mua:

| Cấp được mua | Giá mỗi cấp | Chi phí đoạn | Lũy kế |
|---|---:|---:|---:|
| 1–10 | 2 | 20 | 20 |
| 11–15 | 3 | 15 | 35 |
| 16–20 | 4 | 20 | 55 |
| 21–25 | 5 | 25 | 80 |

| Perk | Hiệu quả mỗi cấp | Tối đa cấp 25 |
|---|---:|---:|
| Planar Defense + | +0,5 phòng thủ planar | +12,5 |
| Planar Damage + | +1 sát thương planar | +25 |
| Critical Hit + | +1% chí mạng | +25% |
| Critical Damage + | +2% sát thương chí mạng | +50% |
| Lifesteal + | +1% hút máu | +25% |
| Scale + | +1% kích thước EVA | +25% |
| XP Multiplier + | +5% EXP hợp lệ | +125% |

Quy tắc tích hợp:

- Critical Hit và Critical Damage ghi vào effect key hiện có `criticalHitRate` và `criticalHitEffect`.
- Lifesteal ghi vào `bloodSuck` và vẫn chịu các giới hạn an toàn/heal budget của combat pipeline hiện có.
- Planar Damage/Defense dùng component planar hiện có, không tạo damage pipeline mới.
- Scale thay đổi kích thước hiển thị của EVA; không tăng tầm đánh, collision hoặc bán kính tương tác.
- XP Multiplier là modifier vĩnh viễn do progression API đọc. Không có trần tổng EXP multiplier. Pipeline nhân toàn bộ modifier hợp lệ rồi nhân hệ số perk `1 + 0,05 × cấp`; cấp 25 riêng perk này cho 2,25×. Nó không áp dụng cho Achievement Star và không nhân Star.
- Mua cấp mới phải reapply hiệu ứng ngay; load/respawn dựng lại hiệu ứng từ save mà không cộng chồng.

### 6.3. Nhóm Khả Năng — mua một lần

| Perk | Giá Star | Hiệu quả giữ lại |
|---|---:|---|
| Tay Nhanh | 8 | Nhặt và chế tạo nhanh hơn |
| Búa Tạ | 6 | Đào đá ngay lập tức |
| Máy Cưa | 6 | Chặt cây ngay lập tức |
| Ngư Thần | 6 | Bắt cá ngay lập tức |
| Siêu Đầu Bếp | 6 | Hoàn thành nấu nồi hầm ngay lập tức |
| Michelin 5 Sao | 8 | Dùng bộ đồ nhà bếp màu đỏ |
| Enchantmemento | 12 | Trang bị trinket để nhận năng lực tương ứng |
| Trị Liệu Sư | 15 | Nhân đôi hiệu quả vật phẩm hồi máu |
| Thu Hoạch | 20 | Nhân đôi sản lượng thu hoạch hợp lệ |
| Khát Máu | 30 | Nhân đôi chiến lợi phẩm quái hợp lệ |
| Bậc Thầy Chế Tác | 35 | Giảm một nửa nguyên liệu chế tạo theo quy tắc an toàn |
| Phước Lành Fawkes | 5 | Chim trong lồng không chết |
| Phân Bón Tốt | 12 | Tăng khả năng cây trồng thành nông sản khổng lồ |
| Icy-Breezy | 10 | Có cơ hội sinh Icy Tumbleweed từ cây/gốc cây mùa đông |

Ba perk cuối được chuyển từ nhóm Global cũ vào Khả Năng. Không còn nhóm Global riêng.

Các hiệu ứng nhân đôi hoặc giảm nguyên liệu phải chạy server-side, chỉ áp dụng lên hành động thành công và có chống callback trùng. Bậc Thầy Chế Tác không được tạo công thức giá 0: mỗi loại nguyên liệu dương sau giảm vẫn cần ít nhất 1.

### 6.4. Nhóm Chế Tạo — mua một lần

#### 11 gói giữ từ mod gốc — 104 Star

| Perk | Giá |
|---|---:|
| Ancient Builder | 15 |
| Kỵ Sĩ Ánh Trăng | 10 |
| Pearl BFF | 8 |
| Benevolent Mind | 8 |
| Nhà Khoa Học Điên | 10 |
| Celebrate! | 5 |
| Festive! | 5 |
| Quà Giáng Sinh | 8 |
| Thợ Rèn Huyền Thoại | 15 |
| Pokeball | 12 |
| Antique Shop | 8 |

#### 7 gói truyền thừa nhân vật — 102 Star

| Perk | Số công thức | Giá |
|---|---:|---:|
| Truyền Thừa Lạc Thần | 10 | 20 |
| Truyền Thừa Tam Tiêu | 7 | 14 |
| Truyền Thừa Thạch Cơ | 8 | 16 |
| Truyền Thừa Tinh Vệ | 7 | 14 |
| Truyền Thừa Tô Đát Kỷ | 5 | 10 |
| Truyền Thừa Hàn Thiên Tôn | 3 | 8 |
| Truyền Thừa Vương Ma Tử | 10 | 20 |

Không có Truyền Thừa Đại Thánh. Không port hai công thức chuyển đổi Sinh Chi Hoa ↔ Diệt Chi Hoa.

Các công thức đã mở sẵn trong Phàm Nhân tiếp tục mở sẵn. Gói truyền thừa chỉ khóa nội dung từng là đồ chế riêng của nhân vật nguồn và nay được chuyển cho EVA.

Mỗi gói dùng một builder tag riêng. Chỉ EVA được add tag sau khi mua. Tag được dựng lại từ save khi spawn/load, và menu chế tạo được refresh ngay để công thức xuất hiện mà không cần relog.

Danh sách prefab được chốt:

- Lạc Thần: `fence_gate_luoshen_item`, `xd_luoshen_jihuaze`, `xd_luoshen_jiangren`, `xd_luoshen_huazhong`, `xd_luoshen_liuguanghuafen`, `xd_luoshen_yin`, `xd_luoshen_huaxia`, `fence_luoshen_item`, `wall_luoshen_item`, `xd_luoshen_dinghunxianglu`.
- Tam Tiêu: `xd_yunxiao_hyjditem`, `xd_yunxiao_fgfq`, `xd_yunxiao_fls`, `xd_yunxiao_fysz`, `xd_yunxiao_ymsz`, `xd_yunxiao_hyjdyqd`, `xd_yunxiao_portable_spicer`.
- Thạch Cơ: `xd_sj_bglxp`, `xd_sj_bgygp`, `xd_sj_by_builder`, `xd_sj_kls`, `xd_sj_tlsq`, `xd_sj_cy_builder`, `xd_sj_sxz`, `xd_sj_xsydz`.
- Tinh Vệ: `xd_xuanyu`, `xd_jingwei_blowdart`, `xd_jingwei_fenice_builder`, `xd_jingwei_fan`, `xd_jingwei_hat`, `turf_jingweitile`, `xd_qianyu`.
- Tô Đát Kỷ: `xd_sudaji_redlantern`, `xd_sudaji_ywfh`, `xd_qwsk`, `xd_sudaji_sjpn`, `xd_sudaji_tsmd`.
- Hàn Thiên Tôn: `xd_htz_xyzzl`, `xd_htz_sjcx`, `xd_htz_tlz`.
- Vương Ma Tử: `xd_wmz_kjb`, `xd_wmz_slxj`, `xd_wmz_md1` đến `xd_wmz_md8`.

`xd_sj_kls` (Khô Lâu Sơn) được giữ trong gói Thạch Cơ theo quyết định mới nhất. Nhóm `xd_wmz_md1..8` phải được audit dependency trước khi đăng ký; mục nào không hoạt động độc lập với nhân vật nguồn thì bị giữ khỏi runtime cho đến khi adapter EVA hoàn tất, nhưng catalog perk vẫn giữ đúng gói đã duyệt.

## 7. Những Perk bị loại

Không đưa vào runtime mới:

- Hunger/Health/Sanity max, regen và Hunger Rate;
- tự sửa trang bị, hồi độ tươi thức ăn, Sack Seeker và Dim Light;
- Speed, Defense và Damage ẩn;
- kháng mưa/lạnh/nóng, Effective Worker, Super Pet, Human Cartographer/Smelter/Garbage Disposal/Navigator, Strong Grip, Ornamemento;
- toàn bộ 44 Expert perk;
- Orphanage, Cluster Constructor, Duplicraft, Pet Not Included, Carpentry Expert;
- toàn bộ nhóm Single;
- tủ lạnh hồi tươi, Thermal Stone, Beefalo Educator, Reign of Giants, Infinite Stack/Insight, Trophy, Rift Manager;
- To Hơn, Mạnh Hơn, Merm Trỗi Dậy và Nhện Phá Hoại.

Phàm Nhân đã có World Rank tự động nên không dựng thêm hệ tăng sức mạnh thế giới từ perk.

## 8. Nhiệm vụ mùa

### 8.1. Catalog và lượt rút

- Bốn mùa: xuân, hạ, thu, đông.
- Mỗi mùa đúng 50 nhiệm vụ: 40 một lần và 10 lặp.
- Toàn bộ 200 ID là duy nhất; một nhiệm vụ chỉ thuộc một mùa.
- Đầu mỗi mùa, server rút không hoàn lại 20 nhiệm vụ: 16 một lần và 4 lặp.
- Danh sách 20 nhiệm vụ được khóa đến khi đổi mùa; không có reroll thủ công.
- Không có pool nhân vật, pool `other` hoặc điều kiện phụ thuộc người chơi khác.

### 8.2. Claim EXP

- Nhiệm vụ một lần có một lần Claim EXP.
- Nhiệm vụ lặp có tối đa năm chu kỳ; mỗi chu kỳ hoàn thành mở đúng một Claim EXP.
- Khi đang chờ claim, tiến độ dừng ở target để sự kiện thừa không xếp hàng phần thưởng ẩn.
- Mỗi claim gọi progression API với source dành cho seasonal task và một claim key idempotent.
- Số EXP nằm trong tuning/progression task riêng; catalog chỉ giữ reward key, không hardcode curve thứ hai.

### 8.3. Mốc rương và phần thưởng đã chốt

Mốc là 5, 10, 15 và 20 nhiệm vụ khác nhau đã có ít nhất một claim. Các lần lặp thứ 2–5 không tăng tiến độ rương.

Mỗi mùa dùng một linh thảo đặc trưng và một bộ vật phẩm cuối mùa. Bốn rương của mùa đang chạy trao thưởng như sau:

| Mùa | Linh thảo/hạt đặc trưng | Mốc 5 | Mốc 10 | Mốc 15 | Mốc 20 |
|---|---|---|---|---|---|
| Xuân | Lôi Minh Quả — `ttk_lc_lmg_seed` | 3 hạt | 5 hạt + 10 `ttk_lingshi1` | 2 `ttk_lingshi2` + 1 Ngọc Vàng | 1 `ttk_lingshi3` + 1 Lông Moose/Goose |
| Hạ | Xích Viêm Hoa — `ttk_lc_cyh_seed` | 3 hạt | 5 hạt + 10 `ttk_lingshi1` | 2 `ttk_lingshi2` + 1 Ngọc Cam | 1 `ttk_lingshi3` + 1 Vảy Rồng |
| Thu | Thanh Phong Tiên — `ttk_lc_qfx_seed` | 3 hạt | 5 hạt + 10 `ttk_lingshi1` | 2 `ttk_lingshi2` + 1 Ngọc Lục | 1 `ttk_lingshi3` + 1 Lông Bearger |
| Đông | Hàn Sương Thảo — `ttk_lc_hsc_seed` | 3 hạt | 5 hạt + 10 `ttk_lingshi1` | 2 `ttk_lingshi2` + 1 Ngọc Lam | 1 `ttk_lingshi3` + 1 Nhãn Cầu Deerclops |

Prefab vanilla tương ứng là `yellowgem`, `orangegem`, `greengem`, `bluegem`, `goose_feather`, `dragon_scales`, `bearger_fur` và `deerclops_eyeball`.

Mỗi rương chỉ claim một lần trong mùa. Server kiểm tra mốc, mùa hiện tại, reward definition và `chest_claimed[index]`, trao toàn bộ bundle rồi mới ghi trạng thái đã nhận. Nếu một prefab không tạo được, transaction không đánh dấu đã claim và báo lỗi rõ ràng; không trao một phần bundle.

### 8.4. Trạng thái lưu

```lua
seasonal = {
    version = 2,
    season = "spring",
    slots = {
        {
            task_id = "...",
            progress = 0,
            ready = false,
            claims = 0,
            counted_for_chest = false,
            closed = false,
        },
    },
    chest_claimed = { false, false, false, false },
}
```

Đúng 20 slot được save. Đổi mùa tạo một lượt rút mới cho mùa mới. Load giữa mùa giữ nguyên lượt rút và tiến độ.

## 9. Save, migration và tính toàn vẹn

Save envelope mới có version rõ ràng:

```lua
{
    version = 1,
    achievements = {
        [id] = { progress = 0, completed = false, claimed_reward = nil },
    },
    stars = { earned = 0, spent = 0 },
    perks = { levels = {}, unlocked = {} },
    cultivation = { stage = 0, consumed = {} },
    seasonal = {...},
}
```

Quy tắc:

- `balance = earned - spent`; không lưu một balance thứ ba dễ lệch.
- `claimed_reward` lưu đúng lượng Star đã trao ở thời điểm claim để lần đổi balance sau không sửa ngược save cũ.
- Load kẹp số âm, số không hữu hạn, cấp perk vượt max và ID lạ.
- Purchase kiểm tra giá hiện tại, max level và balance rồi cập nhật spent/perk trong một thao tác server.
- Nếu apply effect thất bại, purchase không trừ Star.
- Load/respawn reapply effect idempotently từ state, không cộng delta lặp lại.
- Save Phàm Nhân hiện có vẫn giữ nguyên `hh_leveling`, AP, rank, kỹ năng và các component khác.
- Không nhập dữ liệu `levelsystem` cũ. Đây là chủ đích để tránh hai nguồn Level và tránh chuyển các perk đã bị loại.
- `cultivation.stage` chỉ lưu tiến trình cảnh giới Tu Tiên 0–15; không chứa EXP, Level hoặc AP. `consumed` là bitset phục vụ thành tựu dùng đủ 15 đan.

## 10. Theo dõi sự kiện

Không tạo một listener riêng cho từng thành tựu. Catalog được biên dịch thành index theo loại sự kiện:

```text
DST event -> tracker adapter -> candidate achievement IDs -> validate params -> advance once
```

Tracker adapter phải:

- chạy trên master simulation;
- xác định đúng chủ sở hữu solo cho pet/shadow/follower;
- chống một death/action callback bị xử lý hai lần;
- không credit client prediction, hành động hủy hoặc hành động thất bại;
- hỗ trợ kiểm tra sở hữu vật phẩm/currency theo snapshot inventory khi mở UI hoặc khi inventory thay đổi;
- dùng component/API hiện có của Phàm Nhân cho level, rank, boss và seasonal task thay vì tạo bộ đếm song song.

Các thành tựu dạng “đủ bộ” lưu bitset/set prefab đã thấy, không chỉ một counter mù. Thành tựu “sở hữu N” kiểm tra số lượng hiện tại và không trừ vật phẩm.

## 11. UI và RPC

Một nút tiến trình Phàm Nhân mở cửa sổ có ba tab:

1. **Thành Tựu** — lọc theo 13 nhóm, hiển thị progress, Star và nút Claim;
2. **Nhiệm Vụ Mùa** — 20 dòng có progress/claim, repeat count và bốn mốc rương;
3. **Perk** — ba nhóm Chỉ Số, Khả Năng, Chế Tạo; hiển thị cấp, giá kế tiếp, hiệu quả và nút mua.

Star balance luôn hiển thị trong header cửa sổ. Không có tab Level.

RPC tối thiểu:

- claim một Achievement theo ID;
- claim một seasonal slot theo slot index + task ID;
- mua một cấp/unlock Perk theo ID;
- yêu cầu snapshot khi mở UI nếu replica chưa sẵn sàng.

Server không tin reward, price, level hoặc progress do client gửi. Snapshot dùng compact fields/net events; không khai báo hàng trăm netvar cố định cho 231 thành tựu.

## 12. Wiki

Route `/achievement-level` bị xóa, không giữ trang độc lập.

Tạo trang con trong khu vực Phàm Nhân:

```text
/pham-nhan-tu-tien/tien-trinh
```

`PhamNhanNav` thêm mục **Tiến trình**. Trang này trình bày:

- 231 thành tựu hoạt động theo nhóm;
- quy tắc 1.000 Star;
- 39 Perk và bảng giá;
- nhiệm vụ mùa 4 × 50, cách rút 20 và claim EXP;
- xác nhận Level dùng `hh_leveling` của Phàm Nhân.

Xóa link Achievement & Level khỏi header chung và sửa mọi copy cũ nói EVA “dùng cấp từ Achievement & Level”. Dữ liệu wiki phải được export từ cùng catalog Lua hoặc artifact được validator đối chiếu, không tiếp tục hardcode các tổng cũ 763/169/128.

Các file route, parser, component, test và `data/manual/achievement-level.json` cũ chỉ bị xóa sau khi trang Phàm Nhân mới và test thay thế đã pass.

## 13. Chiến lược triển khai

Thực hiện trong worktree riêng bằng sub-agent-driven development. Mỗi task có một implementer và một reviewer mới; các task có file giao nhau chạy tuần tự.

Thứ tự kỹ thuật dự kiến:

1. Đóng băng catalog Thành Tựu/Perk bằng validator và artifact review.
2. Port Đan Lô, 15 đan cảnh giới, Tịch Cốc Đan và 10 đan buff cấp đầu; thêm tiến trình cảnh giới tuần tự.
3. Hoàn tất catalog + state machine nhiệm vụ mùa cùng bốn bảng reward đã chốt.
4. Mở rộng hạng thợ săn SS ở Level 70 và SSS ở Level 100 nhưng chưa gắn bonus mới.
5. Tạo component save/state/RPC server-authoritative trong Phàm Nhân.
6. Nối tracker Thành Tựu với các event/API Phàm Nhân.
7. Nối Star claim và transaction mua perk.
8. Port 7 perk chỉ số vào combat/progression hiện có.
9. Port 14 perk khả năng với test chống duplicate.
10. Port 11 gói craft gốc và 7 gói truyền thừa EVA.
11. Xây UI ba tab, smoke test host/dedicated/client.
12. Chuyển wiki vào `/pham-nhan-tu-tien/tien-trinh` và xóa route cũ.
13. Chạy full regression, audit save/load, provenance và cleanup phần AchievementLevel không còn dùng.

Worktree hiện tại có nhiều thay đổi chưa commit trong Phàm Nhân. Trước khi triển khai, plan phải lập manifest các file đụng nhau và chọn một baseline có đủ thay đổi hợp lệ; không được tạo worktree sạch rồi vô tình xây trên code cũ, cũng không được copy nguyên cả working tree bẩn.

## 14. Kiểm thử và tiêu chí nghiệm thu

### 14.1. Catalog

- Đúng 231 định nghĩa active, 0 future hidden, 13 nhóm.
- Không trùng ID hoặc chữ ký ngữ nghĩa.
- Phân phối Star đúng 71/57/55/34/14 và tổng đúng 1.000.
- Mọi prefab/hook active tồn tại; không có placeholder hoặc tracker giả.

### 14.2. Star và Perk

- Double-click/replay RPC không nhận Star hoặc mua perk hai lần.
- Bảy perk chỉ số max 25, giá từng đoạn đúng và mỗi perk tốn 80.
- Tổng tối đa đúng 945 và balance còn 55 sau full completion/full purchase.
- Reconnect/respawn không cộng chồng stat/effect.
- Không perk bị loại nào xuất hiện trong data, UI hoặc hook.

### 14.3. Combat/progression

- Crit, lifesteal và planar dùng đúng effect/component hiện có.
- XP Multiplier đi qua progression API không có trần tổng; cấp 25 thực sự cho hệ số perk 2,25× và không có cấp mua vô dụng.
- Achievement claim không tăng EXP.
- Seasonal claim tăng EXP đúng một lần vào `hh_leveling`.
- Không có component/netvar/UI/save của `levelsystem` cũ.

### 14.4. Nhiệm vụ mùa

- Mỗi mùa 50 = 40 once + 10 repeat; 200 ID duy nhất.
- Lượt rút luôn 20 = 16 once + 4 repeat, không trùng và không đổi khi reload.
- Repeat claim đúng năm lần; lần thứ sáu bị từ chối.
- Mốc rương đúng 5/10/15/20 distinct task.
- Bốn mùa trao đúng bundle riêng tại mốc 5/10/15/20; claim lỗi không trao một phần và không đánh dấu đã nhận.

### 14.5. Chế tạo

- Đan Lô luôn trả thành phẩm hợp lệ sau 180 giây; không có Phế Đan hoặc roll thất bại.
- 15 đan cảnh giới chỉ dùng đúng thứ tự và tăng chắc chắn một bậc; không tạo Level/EXP thứ hai.
- Không đăng ký Thế Tử Phản Hồn Đan hoặc Phế Đan.
- Unlock gói làm công thức xuất hiện ngay cho EVA.
- Chưa unlock thì EVA không thấy/không craft được công thức gói.
- Nhân vật khác không nhận builder tag.
- Thạch Cơ có `xd_sj_kls`.
- Không có Truyền Thừa Đại Thánh hoặc hai conversion Sinh/Diệt Chi Hoa.
- `xd_wmz_md1..8` chỉ active khi dependency audit chứng minh dùng được với EVA.

### 14.6. Wiki và regression

- `/achievement-level` không còn page/nav entry.
- `/pham-nhan-tu-tien/tien-trinh` hiển thị đúng số liệu mới.
- Không còn câu nói Phàm Nhân/EVA dùng Level từ Achievement & Level.
- Toàn bộ test Phàm Nhân, test wiki liên quan và Lua/Python harness mới pass.
- Dedicated server không load widget client; client không chạy logic thưởng server.

## 15. Định nghĩa hoàn tất

Tính năng hoàn tất khi một save solo Phàm Nhân có thể theo dõi và claim 231 thành tựu để nhận đúng 1.000 Star, dùng Star mua đúng 39 Perk với trần chi 945, luyện đan và thăng 15 bậc cảnh giới không tạo Level thứ hai, chơi vòng nhiệm vụ mùa 20/50 cùng bốn mốc thưởng đã chốt, claim EXP vào `hh_leveling`, mở công thức truyền thừa cho EVA ngay sau khi mua, reload không mất hoặc nhân đôi dữ liệu, và wiki chỉ còn nội dung tiến trình bên trong khu vực Phàm Nhân.
