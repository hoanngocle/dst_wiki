# Solo Combat HUD 1.0.0

Mod cá nhân này gom hai cách hiển thị vào một gói độc lập:

- thanh boss, màu chủ đề, mốc phase, hiệu ứng kháng sát thương và chọn mục tiêu từ **Epic Healthbar v102**;
- thanh máu trên đầu khi giao chiến, tự ẩn sau 8 giây, đổi màu theo tỷ lệ máu và số HP từ hành vi của **Simple Health Bar DST 2.16**;
- một luồng số sát thương duy nhất do server xác nhận: thường màu trắng, chí mạng vàng/cam lớn hơn 20%, xuyên giáp xanh cyan. Nếu một đòn vừa chí mạng vừa có phần xuyên giáp, hai phần hiện riêng.

Số hiển thị lấy chênh lệch HP thật tại `health:SetVal`, nên đòn kết liễu không hiện quá lượng máu còn lại; né, chặn hoàn toàn và đòn 0 sát thương không tạo số.

## Cài đặt

1. Chép nguyên thư mục `SoloCombatHUD` vào `Don't Starve Together/mods/`.
2. Tắt **Simple Health Bar DST** và **Epic Healthbar** trong danh sách mod để tránh hai HUD cũ cùng chạy.
3. Bật **Solo Combat HUD** cho server và tất cả client. Mod cần được cài ở cả server lẫn client.
4. Giữ **Solo Leveling** bật và đặt `can_show_text_fx` / hiệu ứng chữ thành **Tắt**. Bridge phục hồi riêng thông báo EXP, nhiệm vụ và cấp độ; chữ chiến đấu/buff cũ vẫn tắt.

Với `HH_CAN_SHOW_TEXT_FX = false`, bridge chỉ cho các chuỗi có `EXP`, `NHIỆM VỤ`, `LEVEL` hoặc `CẤP` đi qua hàm gốc và phục hồi riêng kênh `SpawnClientLevelUpFx`. Năm nhãn chí mạng đã biết vẫn được dùng làm metadata nội bộ rồi bị chặn; chữ xuyên giáp, né và buff cũ không hiện.

## Tùy chọn

- **Thanh máu boss**: Epic HUD và phase.
- **Thanh máu trên đầu**: thanh mob thường.
- **Ẩn thanh phụ của boss**: mặc định bật; boss có Epic HUD không thêm thanh trên đầu.
- **Số HP**: hiện `hiện tại/tối đa` trên thanh đầu.
- **Số sát thương**: bật/tắt hệ số popup thống nhất.
- **Sát thương đồng đội gần**: mặc định tắt; khi bật, hiện đòn của người chơi khác trong bán kính 35 đơn vị. Đòn của bản thân và follower luôn được gửi về client của chủ nhân.

## Checklist playtest

1. Đánh quái thường: chỉ một số trắng và một thanh trên đầu xuất hiện; thanh tự ẩn.
2. Đánh boss: Epic HUD có mốc phase; mặc định không có thanh nhỏ trên đầu.
3. Gây chí mạng Solo: số vàng/cam lớn hơn; không còn chữ `chí mạng` cũ.
4. Gây xuyên giáp: phần đó màu cyan. Với đòn có cả hai phần, kiểm tra hai số riêng.
5. Kết liễu quái ít máu, đánh mục tiêu chặn hoàn toàn và né: số lần lượt bằng HP còn lại, không hiện, không hiện.
6. Triệu hồi đánh mục tiêu: số được gửi về client của chủ nhân. Nhánh crit của `hh_monster` được đánh dấu khi Solo đọc `criticalHitEffect`; ba shadow không có component này được đánh dấu từ kết quả của hàm `ApplyFollowerCritical` chuyên biệt.
7. Nhận EXP, hoàn thành nhiệm vụ và lên cấp: chữ Solo tương ứng vẫn xuất hiện.

## Nguồn và phạm vi

- Epic Healthbar v102 — Tykvesh: tái sử dụng widget, proxy, định nghĩa boss/phase và atlas HUD; helper đã đổi sang namespace `SCHUDCore`, không sửa `package.path` và không ghi vào global `Tykvesh`.
- Simple Health Bar DST 2.16 — DYC: tham chiếu hành vi và kèm atlas thanh round đã đổi tên. Runtime bị làm rối, hook chat/network và lệnh debug của bản gốc không được mang sang.
- Solo Leveling (Workshop 3780347550): không sửa file nguồn. Bridge chỉ bọc API runtime khi cả hai mod đang bật.

Đây là bản staging chưa được chạy trong game. Các test Lua mock kiểm tra ledger, bridge nhãn crit, return value, lethal/dodge và số RPC; vẫn cần playtest DST thực tế theo checklist trên.

Về hiệu năng, mod không quét toàn bộ entity mỗi frame: proxy trên đầu chỉ được tạo khi mục tiêu thật sự bị đánh và cập nhật theo `SetVal`; số sát thương dùng cùng hook đó thay vì nghe đồng thời `attacked`, `healthdelta` và popup của hai mod cũ. Widget Epic vẫn giữ nhịp cập nhật gốc của nó.
Client chỉ tạo tối đa 32 thanh trên đầu trong bán kính 35 đơn vị. Thanh ngoài phạm vi dừng cập nhật; proxy/widget được dọn khi entity biến mất.
