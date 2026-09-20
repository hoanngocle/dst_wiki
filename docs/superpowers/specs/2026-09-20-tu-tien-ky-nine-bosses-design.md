# Chuyển 9 boss Tu Tiên sang Phàm Nhân Tu Tiên

Ngày: 2026-09-20.

Trạng thái: người dùng đã chốt nhóm 6 boss mỗi lần rơi 1 món ăn + 1 phù, mỗi loại món ăn tăng chỉ số trong 10 lần đầu; từ lần 11 chỉ hồi máu/no/tinh thần. Người dùng đã yêu cầu tăng gấp đôi bonus chỉ số, thêm miễn nóng khi đủ 10 Phượng Tủy và miễn lạnh khi đủ 10 món Kỳ Lân. Người dùng đã đồng ý tiếp tục hoàn thiện tích hợp và kiểm tra theo thiết kế bên dưới. Mod hiện tên Phàm Nhân Tu Tiên 2.0, Solo đã tích hợp. Đã triển khai bộ boss và kiểm tra máy chủ; phạm vi đã kiểm chứng và giới hạn client được ghi tại `docs/superpowers/reports/2026-09-20-pham-nhan-boss-audit.md`.

## Yêu cầu đã chốt

- Chuyển đủ 9 boss đã đối chiếu với nguồn Tu Tiên trong dự án sang Phàm Nhân Tu Tiên.
- Cả 9 boss xuất hiện tự nhiên lần đầu trên map.
- Thanh Tụ Đan Tiên, Ma Tướng Phù Đồ và Tử Vân Ma Quân là boss duy nhất, không chủ động đánh người chơi, chết không tái sinh và có phần thưởng lớn.
- Sáu boss còn lại mỗi lần chết cuối cùng rơi chắc chắn 1 món ăn đặc trưng và 1 phù triệu hồi đúng boss, kể cả lần tự nhiên đầu tiên và các lần triệu hồi lại. Đây là tổng drop mỗi boss, không phải một bộ cho mỗi người tham gia.
- Mỗi người chơi chỉ nhận tăng chỉ số từ mỗi loại món ăn tối đa 10 lần (6 bộ đếm độc lập, tổng 60 lần tăng). Từ lần ăn thứ 11 của một loại, món đó chỉ hồi máu, no và tinh thần. Không dùng món ăn làm nguyên liệu phù.
- Ngoài sáu vật phẩm đặc biệt đã được yêu cầu công dụng, ghi chú các chiến lợi phẩm chưa có công dụng để người dùng quyết định sau; không tự thêm hệ trang bị hoặc công thức khác từ chúng.
- Boss phải có hành vi chiến đấu thực tế: AI, stategraph, giai đoạn, hiệu ứng và thực thể phụ trợ cần thiết; chỉ có hình ảnh hoặc prefab sinh được chưa được tính là chuyển xong.

## Danh sách bàn giao

| Boss | Prefab nguồn | Prefab đích | Vật phẩm triệu hồi |
|---|---|---|---|
| Tàn Khu Bạch Hổ | `xd_baihu` | `ttk_baihu` | `ttk_summon_baihu` |
| Kim Phượng Thần Niệm | `xd_jfsn` | `ttk_jfsn` | `ttk_summon_jfsn` |
| Kỳ Lân Tàn Hồn | `xd_qlch` | `ttk_qlch` | `ttk_summon_qlch` |
| Thanh Tụ Đan Tiên | `xd_qxdx` | `ttk_qxdx` | Không có; duy nhất, chết không tái sinh |
| Ma Tướng Phù Đồ | `xd_futu` | `ttk_futu` | Không có; duy nhất, chết không tái sinh |
| Tà Sát Thù Vương | `xd_spiderqueen` | `ttk_spiderqueen` | `ttk_summon_spiderqueen` |
| Tử Vân Ma Quân | `xd_ziyunboss` | `ttk_ziyunboss` | Không có; duy nhất, chết không tái sinh |
| Thượng Cổ Hắc Ám | `xd_stalke_fuben` | `ttk_stalke_fuben` | `ttk_summon_stalke_fuben` |
| Hồn Phách Tinh Thể Hươu Một Mắt | `xd_deerclops_ziyun` | `ttk_deerclops_ziyun` | `ttk_summon_deerclops_ziyun` |

Thực thể phụ trợ, phân thân và quái do kỹ năng gọi ra thuộc phạm vi phụ thuộc của 9 boss, không cộng thành boss thứ 10. Tâm Ma và các nhân vật/đồng hành khác không nằm trong đợt này.

## Sinh tự nhiên và tính duy nhất

Phần này thay thế hoàn toàn thiết kế cũ chỉ dùng phù để xuất hiện lần đầu.

- Mỗi loại sinh một cá thể tự nhiên trên đất liền của shard Master, cả thế giới mới lẫn thế giới đang chơi chưa có sổ theo dõi boss. Không sinh thêm bản sao ở Caves.
- Bộ quản lý chạy sau khi các entity cũ đã tải xong; lưu trạng thái theo từng loại gồm chưa sinh, đang sống, đã chết, cùng liên kết entity còn sống. Việc sinh lần đầu và hoàn tất cái chết phải cập nhật sổ theo dõi, không dựa vào việc quét thấy/không thấy boss ở gần người chơi.
- Lưu/tải, restart, đổi mùa và người chơi vào lại không tạo thêm boss hay làm sống lại loại đã chết. Rollback đưa cả boss và sổ về cùng thời điểm của save, không dùng dấu vết ngoài save để khóa boss sau rollback.
- Khi chưa sinh được vì thiếu vị trí hợp lệ, giữ trạng thái chưa sinh và thử lại có giới hạn; không đánh dấu đã sinh khi SpawnPrefab thất bại. Một boss đang được khôi phục liên kết không được coi là chưa từng sinh.
- Chọn điểm có khoảng trống phù hợp kích thước/chiêu của boss, ưu tiên các vùng khác nhau; tránh nước, thuyền, đảo đặc biệt, Thiên Cơ Ốc, cổng hồi sinh, người chơi và công trình. Khoảng cách mặc định đề xuất: ít nhất 60 với cổng/người chơi, 40 với công trình, 100 giữa hai boss tự nhiên. Map quá chật giữ loại đó ở trạng thái chờ, không tự giảm khoảng cách và đặt vào căn cứ.
- Sau khi đã sinh, remove/despawn không tự kích hoạt một lần sinh tự nhiên khác. Boss cần tắt cơ chế despawn nguồn phụ thuộc phó bản/owner không tồn tại; trường hợp mất entity bất thường phải có log để kiểm tra, không âm thầm tạo lại.
- Chỉ boss chính tự nhiên hoặc được triệu hồi bằng phù tham gia sổ theo dõi và phần thưởng chính. Bản phụ của Hươu Một Mắt trong trận Tử Vân, phân thân Kỳ Lân và các quái kỹ năng có định danh vai trò riêng, không chiếm suất sinh lần đầu của boss độc lập.

### Ba boss duy nhất, trung lập

Áp dụng cho Thanh Tụ Đan Tiên, Ma Tướng Phù Đồ và Tử Vân Ma Quân.

- Mỗi loại chỉ có một cá thể chính tự nhiên trong một thế giới. Không có recipe/phù triệu hồi lại cho ba loại này, theo xác nhận của người dùng.
- Không chọn người chơi làm mục tiêu chỉ vì đến gần; không khởi động đòn, aura sát thương hoặc gọi lính gây hấn với người chơi khi chưa bị khiêu chiến.
- Bắt đầu chiến đấu khi bị người chơi hoặc đồng hành thuộc người chơi tấn công. Bẫy/projectile có chủ phải quy trách nhiệm đúng; sát thương môi trường không khiến boss tự tìm người chơi không liên quan để trả đũa.
- Khi đã vào giao chiến, giữ đầy đủ bộ chiêu và chuyển giai đoạn. Quái phụ và hiệu ứng không được tự gây hấn trước boss chính. Lưu trạng thái giao chiến hoặc quy tắc reset rõ ràng khi tải; không biến boss trung lập thành thù địch chỉ do restart.
- Chết thật ở giai đoạn cuối khóa trạng thái đã chết vĩnh viễn trong save và trả phần thưởng lớn đúng một lần. Không chạy bộ đếm hồi sinh theo ngày/mùa của nguồn.

## Triệu hồi lại sáu boss còn lại

Các lựa chọn dưới đây là mặc định đề xuất để bản port dùng được ngay, chưa phải cân bằng cuối cùng do người dùng chỉ định.

- Tên vật phẩm: “Phù Triệu Hồi — <tên boss>”, tên hành động: “Triệu hồi”. Mỗi loại có icon riêng, tận dụng tài nguyên có sẵn được kiểm tra trong nguồn.
- Sáu loại gồm Tà Sát Thù Vương, Thượng Cổ Hắc Ám, Hồn Phách Tinh Thể Hươu Một Mắt, Tàn Khu Bạch Hổ, Kim Phượng Thần Niệm và Kỳ Lân Tàn Hồn. Chúng chỉ sinh tự nhiên một lần mỗi loại; các trận tiếp theo phải dùng phù, không tự hồi sinh.
- Mỗi boss chính rơi đúng 1 món ăn `ttk_boss_core_<hậu tố boss>` và 1 phù `ttk_summon_<hậu tố boss>`. Hai vật phẩm tách biệt, mỗi loại 100% ở cái chết cuối cùng; phase/phân thân/quái phụ không phát cặp thưởng này.
- Áp dụng cả lần tự nhiên đầu tiên và mỗi lần gọi lại. Phù rơi trực tiếp thay thế phương án chế phù trong các bản thiết kế trước; không thêm công thức chế phù trong bản này. Không tự phát phù bù khi người chơi làm mất.
- Mỗi phù chỉ gọi lại đúng boss đã rơi nó, tiêu hao một lần. Phù không ăn được; món ăn không dùng triệu hồi. Boss chính còn sống thì không gọi thêm cùng loại.
- Phù có thể xếp chồng, nhặt, cất và lưu theo cơ chế vật phẩm chuẩn của DST.
- Người chơi đang sống sử dụng phù trong túi; máy chủ tìm điểm trống trên đất cách người dùng khoảng 8–12 đơn vị và tạo đúng boss tương ứng.
- Không triệu hồi trên thuyền, mặt nước hoặc bên trong Thiên Cơ Ốc. Bản đầu cho phép ở mặt đất của shard Master; ở Caves trả thông báo rõ ràng và giữ nguyên vật phẩm, tránh đưa các trận đánh ngoài trời vào môi trường chưa được kiểm tra.
- Không gọi thêm cùng loại khi boss chính loại đó còn sống trên shard Master; dùng sổ theo dõi thay vì chỉ quét bán kính gần. Bản phụ trong kỹ năng của boss khác không chặn trận độc lập.
- Kiểm tra quyền sở hữu vật phẩm, số lượng, trạng thái người chơi, shard và vị trí ở máy chủ khi thực thi. Chỉ trừ đúng 1 phù sau khi boss được tạo và khởi tạo hợp lệ. Yêu cầu lặp/đồng thời không được sinh boss miễn phí hoặc trừ đồ hai lần.
- Thất bại phải có lời nhắn tiếng Việt và không mất phù.
- Sáu boss này giữ hành vi gây hấn của nguồn, không tự áp dụng chế độ trung lập của ba boss duy nhất. Boss triệu hồi không là thú theo người gọi.
- Không đưa boss, phù hay chiến lợi phẩm ăn được vào máy quay thưởng trong đợt này.

### Ăn chiến lợi phẩm để tăng chỉ số tối đa

Đây là thay đổi công dụng do người dùng yêu cầu, thay thế mô tả sáu vật phẩm chỉ là nguyên liệu triệu hồi.

- Dùng hành động ăn chuẩn, tiêu hao đúng 1 vật phẩm trong stack khi ăn thành công và áp dụng thay đổi chỉ số ở máy chủ.
- Đề xuất 4 trần tài nguyên và 2 chỉ số chiến đấu cộng cố định, phù hợp các hệ đang có trong Solo. Đây không phải 6 điểm STR/AGI/VIT/SEN/INT: Solo hiện chỉ có 5 thuộc tính cộng điểm, và mỗi thuộc tính có thể tác động nhiều hiệu ứng.
- Từ lần ăn 1 đến 10 của mỗi loại, nhận bonus tương ứng bên dưới; lần 11 trở đi không tăng chỉ số nữa nhưng vẫn ăn được. Bộ đếm bão hòa ở 10, không phụ thuộc người nào giết boss.
- Đề xuất tất cả các lần ăn hồi cơ sở 50 máu, 75 no và 50 tinh thần; không hồi mana. Các giới hạn và biến đổi hồi phục của nhân vật/Solo vẫn được tôn trọng. Đây là mức hồi cơ sở, không hứa mọi nhân vật đều nhận đúng lượng đó trong mọi trạng thái.
- Đề xuất bonus vĩnh viễn, giữ qua chết/hồi sinh và save/load/reconnect; lưu bộ đếm cùng nhân vật. Không tự mở lại 10 lượt bằng hồi sinh hoặc cổng đổi nhân vật; nếu hỗ trợ đổi nhân vật phải chuyển cả bonus và bộ đếm bằng cơ chế lưu của người chơi.
- Tăng trần tài nguyên không tự đầy thanh hoặc hồi theo tỷ lệ: giữ lượng hiện tại rồi áp dụng mức hồi cơ sở đã nêu, tôn trọng health penalty. Không biến thao tác tính lại max thành cách lặp hồi máu miễn phí.
- Bonus phải tương thích chỉ số gốc/biến hình, trang bị, lên cấp và hệ thay đổi max stat của Solo; không ghi đè cứng tổng chỉ số nhân vật.
- Mô tả vật phẩm phải nêu rõ chỉ số, lượng tăng và giới hạn; không ghi công dụng chế phù hoặc “chờ công dụng” cho sáu vật phẩm này.
- Kiểm tra hành động ăn của từng nhân vật với hạn chế khẩu phần ăn trong DST; không mặc định vật phẩm dùng được cho tất cả nhân vật chỉ vì có component edible.

### Đề xuất sáu món ăn và chỉ số

| Boss | Tên món ăn đề xuất | Bonus mỗi lần trong 10 lần đầu | Tổng tối đa từ loại này |
|---|---|---|---|
| Tàn Khu Bạch Hổ | Bạch Hổ Huyết Tủy | +4 sát thương xuyên giáp của Solo | +40 xuyên giáp |
| Kim Phượng Thần Niệm | Phượng Tủy | +20 máu tối đa | +200 máu tối đa |
| Kỳ Lân Tàn Hồn | Kỳ Lân Linh Đan | +20 mana tối đa | +200 mana tối đa |
| Tà Sát Thù Vương | Ma Thù Nội Đan | +20 no tối đa | +200 no tối đa |
| Thượng Cổ Hắc Ám | Hắc Ám Hồn Tinh | +2 phòng thủ cố định của Solo | +20 phòng thủ |
| Hồn Phách Tinh Thể Hươu Một Mắt | Băng Phách Tinh Tủy | +20 tinh thần tối đa | +200 tinh thần tối đa |

Tất cả là tên và số cân bằng mới đề xuất, không phải drop/chỉ số trích nguyên bản. Bạch Hổ thiên công kích, Kim Phượng sinh lực, Kỳ Lân linh lực, Ma Thù sức chứa thức ăn, Hắc Ám phòng hộ và Băng Phách ổn định tinh thần. Phòng thủ +20 là giảm số sát thương cố định theo đường xử lý của Solo, không phải giảm 20% mọi loại sát thương.

### Đặc tính nhận một lần khi đạt 10/10

Hai đặc tính đã được người dùng yêu cầu:

- Phượng Tủy: miễn nhiễm nóng (`immuneHot`). Chống quá nhiệt; không đồng nghĩa miễn sát thương lửa hoặc không bị cháy.
- Kỳ Lân Linh Đan: miễn nhiễm lạnh (`immuneCold`). Chống hạ thân nhiệt; không tự kèm miễn hiệu ứng đóng băng của đòn đánh.

Bốn đặc tính đề xuất:

- Bạch Hổ Huyết Tủy — **Hổ Uy**: +10 điểm phần trăm tỷ lệ chí mạng qua `criticalHitRate`; không tự tăng sát thương chí mạng và vẫn tuân thủ cách giới hạn xác suất của Solo.
- Ma Thù Nội Đan — **Bách Độc Bất Xâm**: miễn nhiễm độc qua `immunePoison`, áp dụng các hiệu ứng độc đi qua cơ chế Solo tích hợp; không hứa miễn mọi debuff của mod ngoài.
- Hắc Ám Hồn Tinh — **Bất Miên**: miễn bị cưỡng ép ngủ qua `immunitySleep`; vẫn cho người chơi chủ động ngủ bằng giường/túi ngủ nếu cơ chế gốc cho phép, kiểm tra riêng để không khóa nhầm hành động hồi phục.
- Băng Phách Tinh Tủy — **Băng Tâm**: miễn bị đóng băng qua `immuneFreeze`. Bổ sung cho chống lạnh của Kỳ Lân, không trùng chức năng.

Đặc tính bật ở lần hấp thu thứ 10, không cộng lại ở lần 11 hoặc khi load/respawn. Dùng modifier/nguồn đóng góp riêng để tháo trang bị có cùng hiệu ứng không xóa đặc tính từ món ăn, và để hồi sinh/load không nhân đôi bonus chí mạng.

Bonus cơ bản đã tăng gấp đôi theo yêu cầu mới. Mức hồi cơ sở của món ăn vẫn là đề xuất 50 máu, 75 no, 50 tinh thần; yêu cầu tăng gấp đôi được áp dụng cho bonus chỉ số, không tự tăng cả phần hồi phục hoặc gói thưởng của ba boss duy nhất.

### Căn cứ và cách tích hợp Solo Leveling

- Đã đối chiếu bản Solo Leveling 2.2.7 nguồn và xác nhận mã đã tích hợp tại `mods/PhamNhanTuTien` (Phàm Nhân 2.0). Từ giờ phát triển trên bản tích hợp, không sửa bản Solo nguồn hoặc tích hợp lại. `scripts/components/hh_leveling.lua` dùng `trueDamageNum` cho STR và `reduceAttackedDamage` cho VIT; `main/hh_tunning.lua` đặt mỗi điểm đều +1, trần điểm STR 200 và VIT 40. Bonus sau khi tăng gấp đôi là +40 xuyên giáp và +20 phòng thủ là bonus riêng, không sửa điểm AP/STR/VIT hay tự đổi trần cộng điểm.
- `hh_mana:RecalculateMax` tính lại mana từ `BASE_MAX + INT * MAX_PER_INT`. Bản đang có là 100 + INT × 20, INT tối đa 15; vì vậy mana cơ sở tối đa từ INT là 400 và món Kỳ Lân nâng thêm 200 (tổng 600 nếu INT đạt 15 và không có nguồn bonus khác). Chỉ tăng max mana, không tăng INT, tốc độ hồi mana hoặc giảm hồi chiêu kỹ năng.
- `main/hh_api.lua` đã bọc `health:SetMaxHealth` và lưu `hh_base_max`; adapter phải phân biệt base với bonus và dùng vòng đời khởi tạo của Solo đã tích hợp. Không chỉ cộng vào maxhealth một lần rồi để Solo ghi đè hoặc cộng lại.
- Component riêng của Phàm Nhân Tu Tiên lưu sáu bộ đếm. Từ bộ đếm tính ra bonus mong muốn; tích hợp combat qua các khóa hiệu ứng Solo và tính chênh lệch giữa bonus mong muốn với bonus đã áp dụng, không gọi AddEffect lặp toàn bộ mỗi lần refresh/load.
- Khi Solo xây lại bảng hiệu ứng, bonus phải được áp dụng lại đúng một lần; không sửa trực tiếp tệp của mod Solo để thêm phần thưởng boss. Có kiểm tra capability, không chỉ dựa vào tên Workshop.
- Solo là phần tích hợp của Phàm Nhân 2.0, không còn nhánh yêu cầu cài/bật Solo riêng. Kiểm tra component đã khởi tạo trước khi hấp thu; nếu thiếu bất thường thì báo lỗi và giữ món, không làm mất lượt hoặc đồ.
- Hiển thị tiến độ trên mô tả khi kiểm tra, ví dụ “Hấp thu: 4/10 — lần tới +20 máu tối đa”; khi 10/10 hiển thị “Đã hấp thu tối đa — ăn chỉ hồi máu, no và tinh thần”.

## Chuyển cơ chế chiến đấu

Nguồn chính: `mods/mod_steam/3235319974` (Tu Tiên 19.7), đích: `mods/PhamNhanTuTien`.

Áp dụng cách trích tĩnh và chuyển namespace hiện có trong `tools/port_ttk_batch19_houses.py` và `tools/port_ttk_buildings.py`. Không chạy loader của mod nguồn. Byte không giải mã được trong mã thực thi phải được giải quyết bằng bằng chứng nguồn trước khi port; không thay bằng giá trị đoán.

Giữ chỉ số cơ sở, thời gian chiêu, animation, đòn đánh và chuyển giai đoạn gốc. Thay điều kiện gây hấn của ba boss duy nhất và điều kiện sinh/hồi sinh/chiến lợi phẩm theo yêu cầu mới ở trên. Ghi lại mọi thay đổi bắt buộc khi tách khỏi mod nguồn trong tài liệu boss. Cấp thế giới/tu luyện chưa có ở Phàm Nhân Tu Tiên dùng cấu hình cơ sở của nguồn, không giả lập một hệ tu luyện mới.

Chuyển các hàm tính sát thương, lọc mục tiêu, tìm vị trí và hiệu ứng phụ thuộc thành helper riêng của boss Phàm Nhân Tu Tiên. Không dùng hàm rỗng để bỏ qua chiêu hoặc import toàn bộ mã tu luyện. Sát thương và thay đổi trạng thái chỉ chạy trên máy chủ; phần hình ảnh dùng entity mạng theo mẫu hiện có.

Kiểm kê đệ quy từ prefab đến brain, stategraph, component, projectile, buff, quái phụ, asset, âm thanh và giá trị TUNING. Mỗi phụ thuộc phải được: tái sử dụng từ Phàm Nhân Tu Tiên nếu tương đương; chuyển có namespace; hoặc thay bằng API DST tương đương có mô tả rõ. Không để đường thực thi gọi prefab hay component không tồn tại.

Các điểm đã thấy trong nguồn cần kiểm tra riêng:

- Bạch Hổ: hai brain, theo dõi hướng đầu, trạng thái rình và chuỗi hiệu ứng riêng.
- Kim Phượng: projectile/lửa/thiên thạch, chỉ số TUNING, thành phần kỹ năng; thay bộ sinh/hồi sinh nguồn bằng sổ theo dõi của bản port.
- Kỳ Lân: phân thân, địa hình/đòn gai/cát/thiên thạch và debuff; thay bộ sinh nguồn, phân thân không được rơi món ăn/phù hoặc đánh dấu boss chính đã chết.
- Thanh Tụ: ít nhất hai bộ animation giai đoạn, vũ khí, kỹ năng diện rộng và nhánh NPC/UI. Chuyển đầy đủ phần cần cho trận đánh; người chơi tấn công để khiêu chiến, không cần UI trao đổi của nguồn.
- Phù Đồ: ma ngẫu, nhện, đá/gai/hố và tìm điểm trên mặt đất.
- Thù Vương: nhện phụ, mạng nhện, sóng tấn công và hiệu ứng trạng thái.
- Tử Vân: thực thể đồng minh/triệu hồi, Hươu Một Mắt, stategraph và hiệu ứng riêng. Boss và quái phụ phân biệt phe đúng như trận đánh nguồn.
- Thượng Cổ Hắc Ám: dùng brain/stategraph có tên Tử Vân trong nguồn, nhưng có prefab riêng; phải giữ biến thể trận đánh này, không nhầm với đồng hành `xd_stalker`.
- Hươu Một Mắt: có ngữ cảnh chủ sở hữu trong nguồn; phải vừa hoạt động khi triệu hồi độc lập vừa hoạt động trong trận Tử Vân, không truy cập owner nil.

Save/load phải giữ được boss và trạng thái cần thiết để tiếp tục trận đánh hoặc trở lại trạng thái an toàn có chủ đích. Chủ của quái phụ phải được khôi phục bằng liên kết lưu chuẩn; task và listener không nhân đôi sau tải. Hiệu ứng tạm dọn khi hết hạn/chủ bị xóa; không tùy tiện xóa quái phụ nếu nguồn cho phép chúng tồn tại độc lập.

## Chiến lợi phẩm và ghi chú công dụng

- Đối chiếu toàn bộ bảng rơi gốc, callback chết và component liên quan, không chỉ `SetSharedLootTable`. Giữ phần rơi gốc dùng được; thêm 1 món ăn và 1 phù cho sáu boss và gói thưởng lớn cho ba boss duy nhất theo yêu cầu mới. Tài liệu phải phân biệt drop gốc với phần thưởng thêm.
- Đồ DST giữ nguyên prefab. Đồ đã port dùng bản `ttk_` hiện có, không đổi hành vi đang được người chơi sử dụng.
- Đồ riêng chưa port được tạo thành vật phẩm có tên, icon, mô tả, physics, inventory, stack và save/load phù hợp. Công dụng mới được hoãn rõ ràng; không đưa các component kỹ năng nguồn vào chỉ vì vật phẩm có tên giống trang bị.
- Những vật phẩm khác chưa được quyết định công dụng có mô tả “Chiến lợi phẩm từ <boss>. Công dụng đang chờ bổ sung.” Sáu vật phẩm đặc biệt chỉ có công dụng ăn tăng chỉ số tối đa; không đánh dấu là chưa có công dụng.
- Sáu boss có thể triệu hồi lại giữ phần linh thạch chung 2–5 Thượng Phẩm một lần mỗi boss chính. Nếu bảng nguồn cũng rơi linh thạch thì hợp nhất, không phát hai lượt ngoài ý muốn.
- Ba boss duy nhất có gói thưởng cố định lớn thay phần linh thạch chung. Mức khởi điểm đề xuất cho mỗi boss: 10 Cực Phẩm Linh Thạch, 100 Thượng Phẩm Linh Thạch, mỗi loại 10 Ngọc Đỏ/Lam/Tím và mỗi loại 5 Ngọc Vàng/Cam/Lục, cộng chiến lợi phẩm riêng của nguồn. Các số lượng này là cân bằng đề xuất, không phải số liệu trích từ mod gốc hoặc con số người dùng đã chỉ định.
- Cờ đã trả thưởng lưu cùng trạng thái chết, kiểm tra tại sự kiện chết cuối cùng. Chuyển phase, phân thân, xóa entity và load xác không phát gói thưởng/món ăn/phù. Một boss phụ mang prefab giống boss chính không được nhận gói thưởng chính.
- Phân thân, phase trung gian và boss phụ do boss khác gọi không phát phần thưởng boss chính lặp lại. Phần rơi phụ hợp lệ theo nguồn được ghi và kiểm tra riêng.

Tạo `mods/PhamNhanTuTien/BOSS_DROPS_VI.md` với một mục cho mỗi boss: nhóm duy nhất/triệu hồi lại, bảng vật phẩm nguồn và đích, số lượng, xác suất, điều kiện rơi, tình trạng đã có/chỉ lưu trữ, công dụng hiện có và ghi chú cho phần chưa có công dụng. Sáu vật phẩm ăn được ghi hiệu ứng tăng max stat sau khi được chốt; gói thưởng lớn ghi là phần thưởng mới của Phàm Nhân Tu Tiên. Ghi rõ phù rơi trực tiếp từ boss, không cần chế tạo. Ghi riêng các khác biệt do gộp luật linh thạch hoặc loại phase/phân thân khỏi phần thưởng boss chính.

Không suy đoán tên tiếng Việt, tỷ lệ hay công dụng khi chưa đọc được nguồn. Nếu chưa xác minh được một trường phải hoàn tất việc đối chiếu trước khi báo port hoàn chỉnh.

## Tổ chức mã và tài liệu

- `main/ttk_bosses.lua`: đăng ký nội dung boss, tên tiếng Việt, giá trị cơ sở và assets. Được nạp từ `modmain.lua`.
- `scripts/ttk_boss_defs.lua`: danh sách 9 boss, nhóm duy nhất/triệu hồi lại, tính trung lập, 6 phù và 6 chiến lợi phẩm ăn được, tên hiển thị, bonus theo món ăn và gói thưởng.
- `scripts/components/ttk_bossregistry.lua`: lưu vòng đời và liên kết boss chính; sinh tự nhiên một lần sau khi tải thế giới; phối hợp khóa triệu hồi và chết/trả thưởng. Chỉ cài trên Master có `ismastersim`.
- `main/ttk_boss_summoning.lua`: đăng ký hành động triệu hồi, không đăng ký recipe phù.
- `scripts/components/ttk_bosssummoner.lua`: kiểm tra và thực thi triệu hồi phía máy chủ.
- `scripts/prefabs/ttk_boss_summons.lua`: 6 phù dùng chung bộ dựng vật phẩm.
- `scripts/prefabs/ttk_boss_cores.lua`: 6 vật phẩm đặc biệt có thể nhặt/cất/save và chỉ dùng ăn tăng max stat; không tham gia công thức phù.
- Thành phần lưu tăng chỉ số nhân vật riêng cho chiến lợi phẩm boss: lưu 6 bộ đếm từ 0 đến 10 và áp dụng bonus theo bảng đề xuất sau khi được duyệt. Không gộp bonus nhân vật vào sổ vòng đời boss của thế giới.
- Prefab, brain, stategraph và component chiến đấu tách theo boss/chức năng, dùng tiền tố `ttk_`.
- Helper chiến đấu dùng chung đặt trong `scripts/ttk_boss_common.lua`, không ghi đè helper toàn cục của game hay mod khác.
- Vật phẩm rơi mới dùng module riêng, chỉ tái sử dụng tài nguyên hiện có khi đúng vật phẩm.
- Archive/đường dẫn mới chuyển namespace; bank/build/sound event bên trong giữ tên nguồn khi đó là định danh thực tế của asset.
- `BOSSES_VI.md`: sinh tự nhiên, 3 boss duy nhất trung lập, phù triệu hồi của 6 boss còn lại, chiến lợi phẩm ăn tăng max stat, thông số cơ sở, kỹ năng, thay đổi so với nguồn và giới hạn shard của bản đầu.
- Cập nhật `README_VI.md`, `CHANGELOG.md`, `CREDITS.md` và phiên bản mod phù hợp. Không thay đổi bảng thưởng máy quay; tài liệu máy quay phải phân biệt “đã có boss trong mod” với “có trong bảng quay”.

## Kiểm chứng và điều kiện hoàn thành

1. Kiểm tra tĩnh toàn bộ Lua mới/sửa biên dịch được, prefab được đăng ký, assets tồn tại và ZIP hợp lệ; không có tên nguồn chưa giải quyết trong đường chạy.
2. Test sinh tự nhiên: đủ 9 loại trong map hợp lệ; thế giới cũ được thêm đúng một lần; save/restart/đổi mùa không sinh lại; mất vị trí giữ trạng thái chờ; chưa khôi phục GUID không bị tạo bản sao; boss phụ không chiếm suất boss chính.
3. Test trung lập của 3 boss: đứng gần không bị đánh/aura/quái phụ tấn công; đánh bằng người chơi/đồng hành/bẫy có chủ bắt đầu giao chiến đúng; sát thương môi trường không kéo người vô can vào trận. Chết cuối cùng khóa vĩnh viễn qua save/load, không có recipe/phù gọi lại.
4. Test triệu hồi: 6 ánh xạ đúng, không có recipe phù, sử dụng stack trừ một; thất bại giữ phù; người chết/vị trí sai/shard sai/boss chính còn sống bị chặn; hai yêu cầu cạnh tranh chỉ tạo một boss. Giết boss tự nhiên hoặc gọi lại đều rơi đúng 1 món ăn và 1 phù tương ứng.
5. Test bảng rơi: đúng ánh xạ/số lượng/xác suất, đủ gói thưởng lớn, vật phẩm đều sinh được; không nhân đôi linh thạch hoặc thưởng phase/phân thân; bản Hươu Một Mắt phụ không phát món ăn/phù của boss chính.
6. Chạy máy chủ DST cục bộ trong thư mục audit và thế giới riêng, không dùng save người chơi. Tạo đủ 9 boss và toàn bộ phụ thuộc; đưa mỗi boss vào chiến đấu, kích hoạt từng nhóm chiêu và giai đoạn được kiểm kê từ nguồn, rồi kiểm tra chết/loot/dọn hiệu ứng.
7. Kiểm tra riêng Hươu Một Mắt không có owner, liên kết quái phụ của Tử Vân và phân thân Kỳ Lân.
8. Lưu/tải một trận có boss và quái phụ; bảo đảm boss tiếp tục hợp lệ, không nhân bản thưởng hoặc task. Kiểm tra phù, món ăn và chiến lợi phẩm trong túi/kho sau tải.
9. Kiểm tra client vào server có mod: tên/icon phù, action, animation, hiệu ứng và chỉ báo boss. Kết quả headless không thay thế kiểm tra hiển thị; nếu môi trường không kiểm tra được client phải báo rõ giới hạn.
10. Chạy lại các kiểm tra hiện có liên quan loot, prefab sào huyệt và chỉ báo boss khi sửa mã dùng chung. Không mở rộng sang thay đổi website.
11. Test ăn tăng chỉ số tối đa theo chính sách được chốt: ăn từ stack trừ đúng một; tăng đúng max stat thay vì chỉ hồi giá trị hiện tại; lần ăn thứ 10 còn cộng bonus, lần 11 chỉ hồi 3 thanh; sáu bộ đếm và từng người chơi độc lập; save/load/reconnect không mất hay nhân đôi; chết/hồi sinh đúng chính sách; tương tác với thay đổi hình dạng/chỉ số gốc của nhân vật không làm ghi đè bonus khác.
12. Test mốc 10/10: từng đặc tính bật đúng một lần; ăn thêm chỉ hồi phục, không cộng thêm chí mạng. Kiểm tra nóng/lạnh nhiệt độ khác với lửa/đóng băng; miễn độc đúng cơ chế Solo; cưỡng ép ngủ bị chặn nhưng chủ động ngủ vẫn hoạt động; save/load/respawn và thay trang bị cùng hiệu ứng không làm mất hoặc nhân đôi đặc tính.

Được tính hoàn thành khi đủ 9 boss chạy và sinh tự nhiên lần đầu, 3 boss duy nhất trung lập chỉ có một lượt đánh, 6 boss triệu hồi lại bằng phù rơi trực tiếp và rơi 1 món ăn tăng chỉ số tối đa 10 lần mỗi loại cho mỗi người, có bảng drop kiểm chứng và tài liệu ghi chú công dụng còn lại; không chỉ đếm số tệp đã chép. Báo cáo phải phân biệt kiểm tra tĩnh, runtime máy chủ và kiểm tra client thực sự đã chạy.

## Rủi ro đã nhận diện

- Mã nguồn mã hóa và một phần mapping cần bổ sung: giải mã bằng bằng chứng cú pháp/API và so sánh nguồn, không thực thi loader.
- Boss phụ thuộc hệ kỹ năng/tu luyện toàn cục: cần adapter hẹp, giữ cơ chế trận đánh và mô tả mọi khác biệt.
- Hai boss có chung thực thể hoặc đồ đã dùng bởi sào huyệt: không thay hành vi prefab hiện có; tạo biến thể phụ trợ riêng nếu yêu cầu chiến đấu khác.
- Tài nguyên đã dùng cho trang trí (`ttk_skin_spirit`, Bạch Ngọc Kinh) không được đổi thành boss hoặc thay hành vi khi thêm prefab chiến đấu.
- Mức bonus và hồi phục món ăn là đề xuất cân bằng ban đầu, chưa xác nhận qua playtest; có thể điều chỉnh sau mà không đổi ID vật phẩm/save.
