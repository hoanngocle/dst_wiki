# EVA — tính năng và lệnh kiểm thử

Ngày xuất: 21/09/2026. Mốc phát hành EVA: **1.2.1**, đã tích hợp trong **Phàm Nhân Tu Tiên**. Tài liệu phục vụ chuyển sang máy khác để thử trực tiếp trong Don't Starve Together (DST).

## 1. Mang sang máy khác

- Mang theo file Markdown này và bản mod đang muốn kiểm thử.
- Gói Phàm Nhân đã đóng ở topic EVA: `PhamNhanTuTien_v2.0.3_EVA_VI.zip`. Đây là bản chụp tại lúc đóng gói; các phần ngoài EVA trong workspace đã có thay đổi sau đó. Nếu cần thử Phàm Nhân mới nhất, dùng bản đóng gói mới nhất của Phàm Nhân.
- Gói EVA riêng: `EVA_v1.2.1.zip`. Chỉ dùng nếu muốn chạy EVA độc lập.
- Khi dùng bản tích hợp: bật **Phàm Nhân + Achievement & Level**, tắt EVA độc lập. Không bật cả hai bản EVA.
- Giải nén để thư mục mod chứa trực tiếp `modinfo.lua` và `modmain.lua`, tránh lồng hai thư mục. Bật mod trong cấu hình world trên máy đích.
- Tạo **world mới**, chọn nhân vật **EVA**. Không cần chuyển save cũ cho đợt test này.
- Để thử nhiều người chơi, host/server phải bật cùng bản mod; kiểm tra thêm từ máy client tham gia.

## 2. Nhân vật, ngoại hình và giao diện

- EVA là nhân vật riêng, prefab `eva`, một ngoại hình mặc định, không có hai skin veil/no veil.
- Tóc bạc, mắt tím, vương miện, váy mới và lưỡi hái tím bạc; các icon kỹ năng cùng tông EVA, có khung tròn.
- Máu/đói/tinh thần nền mặc định: **125/125/200**. Cấu hình và hệ thống tích hợp có thể thay đổi chỉ số thực tế; xem lệnh in thông số bên dưới.
- Lưỡi Hái EVA: prefab `eva_scythe`; sát thương nền mặc định **68**, độ bền **666**, có thể đổi bằng cấu hình. Sát thương thực tế còn chịu hệ thống Phàm Nhân.
- Có thể được phát lưỡi hái lúc bắt đầu nếu cấu hình đồ khởi đầu bật. Mũ, kazoo và rượu cũ đã bỏ.
- Bảng kỹ năng mặc định thu gọn. Bấm pháp ấn mở/đóng 5 icon theo cấp: **Sinh Chi Hoa → Tử Phong Tụ Linh → Tinh Vũ Nguyệt Dực → Dạ Du → Trảm Linh**. Kỹ năng chưa đủ cấp vẫn có trạng thái khóa.
- **Hồ Ảnh dùng chuột phải trên đất trống**, không có icon trên bảng. Phím G/H/J là lối tắt tùy cấu hình; khi test giao diện nên dùng bảng và chuột phải.
- Mô tả, thông báo và bộ thoại EVA dùng tiếng Việt. Thoại xem nhân vật mang giọng dịu dàng, bảo hộ; thoại đồ vật giữ nền Việt hóa.
- **Chưa thêm thoại khi tự bấm xem chính mình**. DST mặc định bỏ qua tự xem; các câu tự giới thiệu đã thảo luận chỉ là đề xuất.

## 3. Cấp EVA và Hồn Lực

EVA có cấp riêng được lưu trong save. Khi chơi bình thường, đọc `components.levelsystem.level` từ Achievement & Level và giữ cấp cao nhất đã đạt; không lấy cấp `hh_leveling` của Phàm Nhân. Tắt/reset Achievement & Level không tự xóa cấp EVA đã ghi nhận.

Sức chứa = `min(1000, 100 + 6 × (cấp EVA − 1))`.

| Cấp | Sức chứa Hồn Lực | Mở khóa |
| --- | ---: | --- |
| 1 | 100 | Hồ Ảnh, nội tại kiếm khí |
| 10 | 154 | Sinh Chi Hoa |
| 20 | 214 | Tử Phong Tụ Linh |
| 30 | 274 | Tinh Vũ Nguyệt Dực |
| 50 | 394 | Dạ Du |
| 100 | 694 | Trảm Linh |
| 101 | 700 | Bắt đầu tự hồi 1 Hồn Lực/giây |
| 150 | 994 | Đã mở toàn bộ kỹ năng |
| 151 trở lên | 1000 | Chạm trần sức chứa |

- Nhân vật mới bắt đầu với **100/100 Hồn Lực**.
- Lên cấp tăng sức chứa, **không mặc định nạp đầy Hồn Lực**. Lệnh chuẩn bị test ở dưới chủ động nạp đầy.
- Tự hồi chỉ khi cấp **>100**, còn sống, chưa đầy; không hồi khi là hồn ma.
- Chết mất **90% Hồn Lực**, phần còn lại làm tròn xuống: 257 còn 25.
- Giết mục tiêu hợp lệ: thông thường +1, hồn ma +10, mục tiêu epic +30; không vượt sức chứa.
- Giới hạn Hồn Lực không có tùy chọn cấu hình riêng.

## 4. Bộ kỹ năng

EVA có **6 kỹ năng chủ động + 1 nội tại**. Các sát thương dưới đây là **cơ sở**, trước giảm sát thương, buff, kháng và luật của boss.

| Kỹ năng | Cấp | Hồn Lực | Hồi chiêu | Tầm/phạm vi |
| --- | ---: | ---: | ---: | --- |
| Hồ Ảnh | 1 | 0 | 15 giây | Dịch chuyển tối đa 20; lôi kích dọc đường rộng 1 |
| Sinh Chi Hoa | 10 | 10 | 60 giây | Tìm mục tiêu 12; vùng quanh người bán kính 6 |
| Tử Phong Tụ Linh | 20 | 3 | 10 giây | Chọn điểm trong 12; xoáy bán kính 8 |
| Tinh Vũ Nguyệt Dực | 30 | 100 mỗi lần bật | Bật/tắt | Tác dụng lên EVA |
| Dạ Du | 50 | 5 | 15 giây | Chọn điểm trong 12; tìm địch quanh điểm bán kính 2 |
| Trảm Linh | 100 | 100 | 60 giây | Chọn điểm trong 12; trận bán kính 5, sát thương bán kính 6 |

Khoảng cách dùng đơn vị thế giới DST, không phải pixel màn hình. Camera/zoom làm kích thước nhìn thấy thay đổi.

### Hồ Ảnh

- Chuột phải lên vị trí hợp lệ để thi triển. Máy chủ kiểm tra điểm ban đầu và kiểm tra lại sau 0,25 giây; điểm sai địa hình, ngoài tầm hoặc bị luật dịch chuyển chặn không gây sát thương, không mất tài nguyên và không vào hồi chiêu.
- EVA giữ nguyên ngoại hình trong toàn bộ kỹ năng: không hóa cáo, không ẩn nhân vật và không tạo hoa/lửa ở hai đầu.
- Dịch chuyển tới con trỏ tối đa 20 đơn vị, đồng thời tạo hiệu ứng lôi thương Trần Bình An ở giữa đường và điểm đến.
- Mỗi sinh vật còn sống có thành phần chiến đấu trên đường đi chịu đúng một lần **600 sát thương cơ bản**, qua hệ thống sát thương Phàm Nhân; không cần đang thù địch và chim đang bay vẫn có thể trúng. Bề rộng đường đánh là 1 cộng bán kính vật lý của mục tiêu; EVA, đồng minh, companion/pet được bảo vệ và người chơi khi tắt PvP không bị đánh.
- Hồi chiêu **15 giây** chỉ bắt đầu sau khi máy chủ dịch chuyển thành công. Hồ Ảnh vẫn không tốn Hồn Lực.

### Sinh Chi Hoa

- Trạng thái kéo dài **15 giây**.
- Tự tìm mục tiêu hợp lệ trong 12 đơn vị; bắn **80/đạn mỗi 0,2 giây** khi có mục tiêu.
- Vùng quanh người bán kính 6 gây **67 mỗi 0,5 giây**.
- Hồi **5% máu tối đa mỗi lần** tại giây 0/3/6/9/12, tổng tối đa 25% nếu đủ năm lần.
- Lá chắn bằng **25% máu tối đa**, hết khi tiêu hao hoặc trạng thái kết thúc.
- Hiệu ứng hoa tím bạc. Không thêm gây buồn ngủ cho EVA.

### Tử Phong Tụ Linh

- Xoáy tím bạc tồn tại **7 giây**, hồi chiêu **10 giây**.
- Thu hoạch vật hợp lệ, chặt cây/khai thác và gom vật phẩm về vùng xoáy; không đồng nghĩa tự đưa tất cả vào túi.
- Nhịp xử lý thu hoạch 0,5 giây; lượng work 3; nhịp kéo đồ 0,1 giây.
- Có bộ lọc bảo vệ công trình, đồ sở hữu, cây trồng và vật phẩm đặc biệt. Đào áp dụng theo kiểm tra gốc cây, không cào sạch mọi thực thể có thể đào.

### Tinh Vũ Nguyệt Dực

- Bật/tắt cánh bạc tím; bật thành công tốn **100 Hồn Lực**.
- **Không hao duy trì**, tắt miễn phí; tăng tốc di chuyển **8%**, có cơ chế đi trên mặt nước.
- Không yêu cầu cấp tu luyện nội bộ; chỉ cần cấp EVA 30 và đủ Hồn Lực.
- Không phải bay xuyên mọi chướng ngại.
- Khi đang ngoài biển, thao tác tắt thủ công bị chặn; về đất liền hoặc thuyền trước khi tắt.

### Dạ Du

- Phóng lưỡi hái tím tới mục tiêu hợp lệ, gắn dấu khiến mục tiêu nhận **×1,10 sát thương trong 5 giây**.
- **Không có sát thương trực tiếp ban đầu** trong phiên bản này. Dùng đòn đánh/kỹ năng khác để kiểm tra dấu.

### Trảm Linh

- Chiêu cấp 100, tên trên giao diện không có chữ Ultimate.
- Năm lưỡi hái dựng trận theo ngũ giác; giữ chân mục tiêu hợp lệ bên trong, tùy điều kiện/kháng của mục tiêu.
- Gọi lưỡi hái giữa trận khoảng 1,3 giây; đòn chính ở khoảng 1,8 giây gây **734**.
- Cột công kích gây **200 mỗi 0,5 giây**, **11 nhịp**, từ khoảng giây 2,9; trận kết thúc khoảng giây 7,9.
- Tổng cơ sở lý thuyết **2.934/mục tiêu** nếu nhận đủ đòn chính và 11 nhịp; không bảo đảm sát thương thực tế bằng số này.

### Nội tại kiếm khí

- Mỗi **hai đòn cận chiến bằng vũ khí trúng hợp lệ** phóng kiếm khí cơ sở **50 sát thương**.
- Có thể dùng vũ khí khác, không bắt buộc Lưỡi Hái EVA.
- Đạn/kỹ năng/đánh hụt không được tính để tự kích hoạt dây chuyền.

### Tương thích sát thương

- Dùng cơ chế sát thương tích hợp Phàm Nhân; không bổ sung giảm hồi chiêu theo INT.
- Không thay luật boss chặn đòn từ xa. Tầm thi triển lớn không bảo đảm vượt được luật chặn của boss.
- Khi kiểm tra sát thương nên bắt đầu bằng quái thường; ghi rõ boss, khoảng cách và trang bị nếu chỉ boss bị mất sát thương.

## 5. Lệnh console chuẩn bị test

Mở console bằng **~**, chọn chế độ **Remote/server**, dùng tài khoản host/admin. Chạy khi đang điều khiển EVA còn sống. Mỗi khối là một lệnh có thể dán riêng. `ConsoleCommandPlayer()` chọn người gửi lệnh; tránh dùng `AllPlayers[1]` vì có thể trỏ nhầm người trong multiplayer.

Các lệnh thay cấp/Hồn Lực có thể được lưu vào save. Dùng world test mới. Chúng không giả lập toàn bộ quá trình lên cấp thật của Achievement & Level.

### Xem cấp, Hồn Lực và chỉ số hiện tại

```lua
local p = ConsoleCommandPlayer(); local s = p and p.components.eva_souls; if s then s:RefreshLevel(); print("EVA level:", s.level, "Soul:", s.current, "/", s.max, "External level:", p.components.levelsystem and p.components.levelsystem.level or "none"); print("HP:", p.components.health.currenthealth, "/", p.components.health:GetMaxWithPenalty(), "Hunger:", p.components.hunger.current, "Sanity:", p.components.sanity.current) else print("Player is not EVA or console is not Remote") end
```

### Cấp 150 và nạp đầy 994 Hồn Lực

```lua
local p = ConsoleCommandPlayer(); local s = p and p.components.eva_souls; if s then s.level = 150; s:RefreshLevel(); s:DoDelta(s.max); print("EVA level:", s.level, "Soul:", s.current, "/", s.max) end
```

### Cấp 151 và nạp đầy 1.000 Hồn Lực

```lua
local p = ConsoleCommandPlayer(); local s = p and p.components.eva_souls; if s then s.level = 151; s:RefreshLevel(); s:DoDelta(s.max); print("EVA level:", s.level, "Soul:", s.current, "/", s.max) end
```

Thay số cấp để thử các mốc 9/10, 19/20, 29/30, 49/50, 99/100 và 100/101. **Nếu Achievement & Level hiện cao hơn cấp muốn thử, EVA sẽ lấy lại cấp cao hơn.** Để kiểm tra khóa cấp thấp chính xác, dùng nhân vật/world mới có cấp ngoài còn thấp. Các lệnh trên không đổi cấp mod ngoài và không hạ cấp đã có ở mod ngoài.

### Nạp đầy Hồn Lực, không đổi cấp

```lua
local p = ConsoleCommandPlayer(); local s = p and p.components.eva_souls; if s then s:RefreshLevel(); s:SetPercent(1) end
```

### Đặt Hồn Lực về 0 để thử thiếu tài nguyên

```lua
local p = ConsoleCommandPlayer(); local s = p and p.components.eva_souls; if s then s:SetPercent(0) end
```

Ở cấp 101 trở lên sẽ tự hồi ngay theo nhịp 1 giây; không nhầm đó là lỗi của lệnh.

### Cấp một Lưỡi Hái EVA vào túi

```lua
local p = ConsoleCommandPlayer(); if p and p.components.inventory then p.components.inventory:GiveItem(SpawnPrefab("eva_scythe")) end
```

Trang bị bằng giao diện túi để đồng thời kiểm tra icon, hình cầm tay và thao tác trang bị.

### Hồi đầy máu, đói và tinh thần

```lua
local p = ConsoleCommandPlayer(); if p and p.components.health then p.components.health:SetPercent(1); p.components.hunger:SetPercent(1); p.components.sanity:SetPercent(1) end
```

### Đặt máu còn 50% để thử hồi phục

```lua
local p = ConsoleCommandPlayer(); if p and p.components.health then p.components.health:SetPercent(0.5) end
```

### Bật/tắt bất tử để quan sát hiệu ứng

Bật:

```lua
local p = ConsoleCommandPlayer(); if p and p.components.health then p.components.health:SetInvincible(true) end
```

Tắt:

```lua
local p = ConsoleCommandPlayer(); if p and p.components.health then p.components.health:SetInvincible(false) end
```

Tắt bất tử khi thử khiên, nhận sát thương hoặc mất Hồn Lực khi chết. Đừng đánh giá các cơ chế đó trong lúc bất tử.

### Xóa hồi chiêu để thử lại nhanh

```lua
local p = ConsoleCommandPlayer(); if p and p.components.eva_souls then for _, k in ipairs({"eva_life", "eva_harvest", "eva_daydu", "eva_scythe_array", "eva_fox_blink"}) do local s = p.components[k]; if s then s.cooldown_end = 0 end end end
```

Chỉ dùng sau khi hiệu ứng trước đã kết thúc, ở trạng thái đứng bình thường. Lệnh không hủy hiệu ứng đang chạy và không phải bài test thời gian hồi thật. Nếu bảng chưa cập nhật tức thì, đóng/mở lại bảng rồi thử. Cánh là bật/tắt, không nằm trong lệnh này.

### In thời gian hồi chiêu còn lại

```lua
local p = ConsoleCommandPlayer(); if p and p.components.eva_souls then for _, k in ipairs({"eva_life", "eva_harvest", "eva_daydu", "eva_scythe_array", "eva_fox_blink"}) do local s = p.components[k]; if s then print(k, math.max(0, s.cooldown_end - GetTime())) end end end
```

### Tạo một nhện gần EVA để thử giao chiến

```lua
local p = ConsoleCommandPlayer(); if p then local x,y,z = p.Transform:GetWorldPosition(); local t = SpawnPrefab("spider"); if t then t.Transform:SetPosition(x + 5, y, z) end end
```

Nhện có thể tấn công và chết nhanh. Tạo từng con trong world test; không dùng nó để suy ra trần sát thương boss.

## 6. Checklist test bằng giao diện thật

1. **Vào world:** EVA hiện trong màn chọn; đúng tóc, mắt, miệng, vương miện, váy ở các hướng; không chồng váy. Avatar, minimap, icon chế tạo, lưỡi hái và ảnh hồn ma đúng EVA.
2. **Bảng kỹ năng:** thu gọn/mở hoạt động, thứ tự cấp đúng, không có icon Hồ Ảnh, không chiếm ô túi. Thử khóa cấp bằng nhân vật mới trước khi nâng lên 150.
3. **Sinh Chi Hoa:** trừ 10 Hồn Lực, có hoa/đạn/vòng tím bạc; thử địch ở gần và xa; kiểm tra 5 lần hồi, khiên hết đúng lúc, hồi chiêu 60 giây.
4. **Tử Phong Tụ Linh:** trừ 3, xoáy tồn tại 7 giây, hồi 10 giây; thử riêng cây, đá, bụi thu hoạch và đồ rơi. Theo dõi đồ gom lại và tài sản cần được bảo vệ.
5. **Cánh:** bật trừ đúng 100, đứng chờ không mất thêm do cánh. Ở cấp cao có thể thấy Hồn Lực tăng do tự hồi. Đi trên biển, quay về đất, tắt; thử tắt ngoài biển phải bị chặn. Kiểm tra sau reconnect.
6. **Dạ Du:** trừ 5, dấu tồn tại 5 giây, dùng đòn khác so sánh sát thương trước/trong/sau dấu; không đòi sát thương ngay lúc phóng.
7. **Trảm Linh:** trừ 100, thấy đủ 5 lưỡi hái, đòn giữa và các nhịp sau; hết trận không sót thực thể/khống chế; hồi 60 giây.
8. **Hồ Ảnh:** chuột phải điểm hợp lệ trong tầm; sau 0,25 giây EVA giữ nguyên hình và dịch chuyển, có lôi quang giữa đường/điểm đến, không có hoa/lửa. Xếp nhiều sinh vật dọc đường, gồm quái thù địch, chim trung lập dưới đất và chim đang bay, để xác nhận mỗi con chỉ nhận một lần sát thương cơ bản 600. Thử điểm xa quá tầm, điểm bị chặn, sát bờ biển, PvP/đồng minh/pet, khi bật cánh và sau khi thi triển liên tục; lần lỗi không được vào hồi chiêu.
9. **Kiếm khí:** dùng lưỡi hái rồi một vũ khí cận chiến khác, mỗi hai đòn hợp lệ sinh kiếm khí; đánh hụt và kỹ năng không tự nhân vòng kích hoạt.
10. **Cấp/Hồn Lực:** 150 có 994, 151 có 1000; cấp 100 chưa tự hồi, 101 bắt đầu hồi. Test tăng cấp thật qua Achievement & Level riêng với lệnh tăng cấp EVA.
11. **Chết/hồi sinh/save:** ghi Hồn Lực trước chết, tắt bất tử, thử chết tự nhiên; còn 10% làm tròn xuống, không bị trừ lần hai do reload. Lưu, thoát, vào lại để kiểm tra cấp và tài nguyên.
12. **Multiplayer:** host và client cùng thấy hiệu ứng/cánh, bảng đúng cấp, không nhân chi phí hay nhân đạn; đặc biệt thử Hồ Ảnh với độ trễ thực tế.
13. **Thoại:** EVA xem người chơi khác/hồn ma; không còn giọng tự nhận nhà khoa học. Tự bấm bản thân không có thoại là hành vi hiện tại.

## 7. Tình trạng kiểm chứng và báo lỗi

- Lượt kiểm tra cuối topic: **22/22 bộ test đạt**, cú pháp Lua hợp lệ, 3.974 mục thoại; 90 file runtime EVA khớp nguồn, bản tích hợp và gói phát hành EVA đã chốt.
- Đã có lượt chạy dedicated server offline kiểm tra kỹ năng, tài nguyên, sát thương và cleanup. Đây không phải chứng nhận FPS, giao diện hay độ trễ multiplayer.
- Tài liệu này không thay đổi code, không thêm kỹ năng/thoại tự bấm bản thân. Các lệnh được đối chiếu API trong mã; vẫn cần chạy trên server game của máy đích.
- Khi báo bug, gửi: phiên bản mod, host hay client, cấp EVA/cấp Achievement & Level, Hồn Lực, tên kỹ năng, thao tác tái hiện, mục tiêu, khoảng cách, ảnh/video và log.
- Log thường ở thư mục dữ liệu `Klei/DoNotStarveTogether`: `client_log.txt` phía client và `server_log.txt` trong thư mục shard `Master`/`Caves` của cluster. Vị trí gốc phụ thuộc hệ điều hành, tài khoản và cách khởi chạy server.
- Giữ lại log ngay sau lỗi; ghi rõ có dùng lệnh bất tử/xóa hồi chiêu trong lần test đó hay không.

## 8. File mã để tham chiếu khi sửa lỗi

Các đường dẫn sau là tương đối trong thư mục mod EVA hoặc Phàm Nhân:

- `scripts/components/eva_souls.lua`: cấp, sức chứa, hồi Hồn Lực, chết/save.
- `scripts/util/eva_progression.lua`: mốc mở khóa.
- `scripts/components/eva_life.lua`, `eva_wings.lua`, `eva_harvest.lua`, `eva_daydu.lua`, `eva_scythe_array.lua`, `eva_fox_blink.lua`: điều khiển kỹ năng.
- `scripts/util/eva_life_common.lua`, `eva_fox_common.lua`, `eva_harvest_common.lua`, `eva_combat_common.lua`, `eva_scythe_array_common.lua`: thông số dùng chung.
- `scripts/prefabs/eva.lua`, `eva_scythe.lua`: nhân vật, vũ khí và dependency hiệu ứng lôi thương Hồ Ảnh.
- `scripts/speech_eva.lua`: thoại.
- Riêng Phàm Nhân: `main/ttk_eva.lua`, `main/ttk_eva_source.lua`, `provenance/eva-assets.json`.
