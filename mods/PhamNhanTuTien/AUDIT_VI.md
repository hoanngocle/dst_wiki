# Rà soát Tu Tiên Ký 0.6.2 — 19/09/2026

Đây là báo cáo lịch sử của bản 0.6.2. Kết quả rà soát mới, có chạy máy chủ DST thật,
nằm trong [AUDIT_RUNTIME_VI.md](AUDIT_RUNTIME_VI.md). Chuỗi Sa Đường nêu dưới đây đã
được gỡ ở bản 0.8.3; không còn thuộc danh sách đăng ký hiện tại.

> Đây là báo cáo lịch sử 0.6.2. Từ 0.8.3, Sa Đường đã bị gỡ; skin và tích hợp Solo của Phiên được ghi trong README_VI.md.

## Kết luận và phạm vi

Đã đối chiếu mã nguồn, sản vật và phụ thuộc của các phần đã gộp vào **Tu Tiên Ký**. Không phát hiện thêm prefab sản vật custom bị thiếu sau khi bổ sung chuỗi Quả Sa Đường ở 0.6.1. Tìm thấy và sửa ba vấn đề trong luồng hoạt động ở 0.6.2, ghi bên dưới.

**Chưa thể xác nhận toàn bộ hoạt động trong game/multiplayer:** đây là rà soát tĩnh, compile cú pháp Lua và đối chiếu API với bản DST cài trên máy; không mở game, không chạy test suite. nhân vật cũ Mori v2.0 và các mod độc lập khác nằm ngoài phạm vi theo yêu cầu mới nhất.

## Bảng sản vật và thực thể

“Có mã/phụ thuộc” trong bảng nghĩa là đã tìm thấy đường tạo, prefab/component và tài nguyên tương ứng; không có nghĩa đã chơi thử thành công.

| Nội dung | Sinh ra / thu hoạch / biến đổi | Mã và phụ thuộc đã đối chiếu |
|---|---|---|
| Linh thạch | Quái đủ điều kiện → 2–5 Hạ Phẩm; boss → 2–5 Thượng Phẩm. 100 Hạ → 1 Trung; 10 Trung → 1 Thượng; 10 Thượng → 1 Cực | Có đủ `ttk_lingshi1..4`, hook chết, lọc đồng hành và recipe đổi phẩm; Solo chỉ là nhận diện tùy chọn |
| Hoàng Hoa Lê Mộc Trác | Cất/trưng bày món ăn, hồi độ tươi; trả đồ khi đập. Nâng cấp có FX, trả mảnh vương miện; quá nhiều đồ dùng rương sập chuẩn | Có container 8 ô, preserver, hai skin, `ttk_chestupgrade`, `collapsed_treasurechest`, `alterguardianhatshard`, FX chuẩn |
| Lục Mạch Thần Kiếm | Sáu loại phi kiếm đỏ/xanh/tím/cam/vàng/lục, vệt kiếm, tia sáng; ngọc nâng cấp, cầu vồng và ×2 sát thương một lần | Có sáu định nghĩa và factory phi kiếm, ember/sparkle FX, các bộ anim, action/RPC; carrier sát thương Solo tùy chọn, không import Solo |
| Cửu Thiên Tinh Thần Phiên | Dạng cầm ↔ dựng đất; Hồn Vệ, hồn bay vào Phiên, đạn, hiệu ứng trúng, xoáy | Có `vanhonphien_ground/soul/soulfx/soulfx_in/projectile/hit_fx/vortexspawner/vortexfx`, brain, stategraph, owner/target rules, lưu hồn và timer |
| Thần Hi Quang Trượng | Hạt sáng khi cầm; hiệu ứng dịch chuyển. Đá Sa Mạc → 15 lượt, tối đa 30; hết lượt trượng mất | Có `thanhiquangtruongfx`, blinkstaff/finiteuses/rechargeable, action bản đồ và FX chuẩn. Task blink gắn với người dùng nên lượt cuối không hủy việc dịch chuyển |
| Truyền Tống Trận | Chuyển người chơi, follower/đệ đi theo đồ trong túi và đồ nặng gần cổng; không tự tạo sản vật | Có homesign/arrowsign tùy chọn, classified, component/replica, màn hình đích, RPC và tài nguyên cổng; cùng shard |
| Anh Đào Thụ | 2 Ngọc Tím mỗi khoảng 7 ngày + 0–100 giây; tháo bằng búa trả vật liệu theo lootdropper/recipe | Có periodicspawner, `purplegem` chuẩn, nhiệt độ/shelter, recipe |
| Đan Phong | 4 Ngọc Đỏ cùng chu kỳ; tháo bằng búa | Có cùng factory cây, `redgem` chuẩn, nhiệt độ/shelter, recipe |
| Bách Hợp | Bướm: 40% ở bình minh ngoài mùa đông, ngoài hang; aura tinh thần | Có `butterfly` chuẩn và callback bình minh; không có loại quả/hoa thu hoạch custom riêng trong nhánh nguồn được chọn |
| Bạch Mân Côi | Bướm và aura như trên | Có cùng factory hoa, asset/icon riêng |
| Bồ Công Anh | Bướm và aura như trên | Có cùng factory hoa, asset/icon riêng |
| Cam Tỉnh | Nạp nước cho bình tưới, không tạo chai nước mới | Có tag/component `watersource` dùng action chuẩn của DST |
| Chậu Hoa Uẩn Linh | Hạt → cây nông nghiệp/cỏ dại → sản phẩm và hạt; cây lớn/khổng lồ hoặc thối theo game; chậu trống đập trả 1 Đá Cắt + 1 Hạ Phẩm | Có luồng farmplantable, liên kết entitytracker, chuyển mầm `grew_into`, tiêu lượt, nạp linh lực, stress hook. Sản phẩm/giống/cỏ dại là prefab của DST |
| Hạt Sa Đường và cây thường | Hạt → cây; chặt → 6 Gỗ + 1 Hạt; nhánh đã chín → quả rơi khi chặt | Có `ttk_shatangshunut`, `ttk_shatangshu_normal`, deploy/chop, nhánh gắn childspawner, không cần Chưởng Thiên Bình |
| Nhánh và Quả Sa Đường | Tối đa 2 nhánh, mỗi nhánh hái 1 quả; quả hỏng → thức ăn thối | Có `ttk_shatangshuvine`, `ttk_stg`, `spoiled_food`; 3 máu/47,5 no/7 tinh thần; đi nước 480 giây, chờ ăn 960 giây, timer lưu và netvar cho client |
| Chuồng Bò Lai | Tối đa 2 `ttk_beefalo`; đủ đàn 3 kỳ ngày → 8 lông, 50% thêm sừng; thú chết → 1 thịt | Có prefab, brain/stategraph, anim sừng; `beefalowool`, `horn`, `meat`; inventory và thao tác Thu hoạch |
| Chuồng Dê Điện | Tối đa 2 `ttk_lightninggoat`; mỗi kỳ ngày đủ đàn → 1 sữa, 25% thêm sừng; thú chết → 1 thịt | Có prefab, brain/stategraph, anim; `goatmilk`, `lightninggoathorn`, `meat`; inventory và Thu hoạch |
| Chuồng Voi Koala | Tối đa 2 `ttk_koalefant`; đủ đàn 3 kỳ ngày → 1 vòi hè/đông ngẫu nhiên; thú chết → 1 thịt | Có prefab, brain/stategraph, anim; `trunk_summer`, `trunk_winter`, `meat`; inventory và Thu hoạch |
| Công Cụ Hạp | Tự thu công cụ vô chủ trong bán kính 8; trả đồ khi đập; nâng cấp sức chứa | Có container 36 ô, bộ lọc tool/umbrella, `ttk_storeitem`, `sand_puff`, luồng rương sập và shard/FX chuẩn |
| Đa Bảo Các | Cất 36 ô/trưng tám ô đầu, khôi phục hiển thị sau load; trả đồ khi đập; nâng cấp sức chứa | Có container, symbol cập nhật itemget/itemlose, LoadPostPass và rương sập chuẩn |
| Cửu U Xích Linh Đăng | Tiêu Hạ Phẩm Linh Thạch để sáng ban đêm, trả linh thạch còn trong ô khi đập | Có container, timer lưu, ánh sáng radius 3,5; 3.360 giây sáng/viên, tạm dừng ban ngày/hết nhiên liệu |

## Lỗi đã sửa trong đợt rà soát

1. **Tải nhân vật đang đạp nước:** hook `ShouldDrown` chưa bao phủ `player_common.OnLoad`, vốn đọc thẳng `drownable.enabled` rồi đưa người đứng ngoài đất về cổng. Nay đồng bộ timer trước OnLoad và tạm khóa riêng bước kiểm tra này, khôi phục cờ ngay sau tải. Giữ timer và vị trí khi hiệu lực còn.
2. **Phá chuồng ban đêm:** `childspawner:ReleaseAllChildren()` vẫn gọi `CanSpawn()` và bị `not isnight` chặn. Nay chỉ bỏ khóa ngày trong lúc tháo chuồng. Nếu không tìm được chỗ thả hết, giữ lại chuồng/số thú còn trong đó, chưa phát loot tháo dỡ. Bổ sung khai báo trực tiếp các sản vật chuồng để nạp phụ thuộc rõ ràng.
3. **Cổng sát bờ/hố:** trước đây kiểm tra `(xf,zf)` nhưng đưa người/thú tới `(xf±1,zf±1)`. Nay tìm một điểm hợp lệ sau khi đếm ngược kết thúc, dùng điểm đã kiểm tra cho cả người/thú/đồ; nếu không có điểm thì hủy trước khi trừ chi phí. Kiểm tra lại quyền điểm đến và component còn tồn tại.

## Những phần cố ý chưa chuyển / đã đổi

- **Đan Lô và hệ luyện đan:** hoãn theo lựa chọn của người dùng; không đăng ký recipe/prefab giả.
- **Nhà trong đại thụ:** không nhập. Cơ chế kết quả được chuyển sang cây thường; hạt có recipe và trồng trực tiếp. Chưởng Thiên Bình đã được bổ sung theo yêu cầu mới, xem README.
- **Hệ tu luyện/cấp nhân vật/skin đặc quyền của nguồn:** không nhập. Phiên dùng nền sát thương độc lập; trượng dùng state dịch chuyển chuẩn. Kho không nhập hiệu ứng thú cảnh riêng của skin chưa chuyển.
- **Solo:** tùy chọn cho cường hóa Lục Mạch; không nhập hệ khảm hoặc mọi hiệu ứng Solo vào từng phi kiếm. Phiên chưa có nâng cấp Solo riêng.
- **Cổng:** chưa đi xuyên shard mặt đất–hang. Khi dùng bản gộp phải tắt bản cổng riêng trùng namespace.
- **Thú chuồng:** giữ hành vi riêng của nguồn, không suy ra đầy đủ thuần hóa/cưỡi/đẻ tự nhiên của thú vanilla chỉ vì cùng hình dáng.

## Bằng chứng kiểm tra và giới hạn

- Compile tất cả 59 file Lua bằng Lua 5.1 có sẵn; không thực thi loader mod gốc.
- Kiểm tra CRC 38 archive animation đã có trong mod. Đây là tài nguyên game `.zip`, không phải tạo ZIP phát hành.
- Duyệt XML atlas và đối chiếu texture đích; không có texture được XML trỏ tới bị thiếu.
- Duyệt require, đường dẫn asset tĩnh và lời gọi component; đối chiếu với script/asset DST cài trên máy. Các tên được tạo động như bốn linh thạch, ba hoa và sáu phi kiếm được đọc riêng từ factory/định nghĩa.
- `collapsed_treasurechest` được xác nhận là prefab chuẩn sinh từ factory của DST; không phải phụ thuộc mod bị thiếu. Tên bank/build `xd_` nằm trong asset gốc không đồng nghĩa cần bật Tu Tiên gốc.
- Không chạy game/test suite, không sửa save, không tạo gói ZIP và không thay đổi nhân vật cũ Mori trong đợt rà soát này.

## Các tình huống còn cần xác nhận trong game

1. Host và một client: chế tạo/đặt/dùng mỗi món; thử Tu Tiên Ký riêng rồi với Solo cho Lục Mạch.
2. Chậu: hạt thường → mầm thay loại → cây lớn → thu hoạch; save/load giữa vụ; cây khổng lồ, thối, đào và nạp lại.
3. Sa Đường: sinh/hái hai nhánh, chặt và trồng lại; ăn, chuyển bờ–nước, save/load giữa nước, hết hiệu lực và chết.
4. Chuồng: sản xuất, thu hoạch, đàn về nhà ban đêm, đập lúc đang nhốt thú; tải lại kho/đàn.
5. Kho/bàn: đồ đầy, nâng cấp, quá tải tạo rương sập, đập/giải thể và tải lại; biểu tượng trưng bày trên client.
6. Phiên: thu hồn, gọi hồn, đạn trúng đúng đối tượng, thu/đặt, người sở hữu chết/rời shard.
7. Trượng: dịch chuyển gần/bản đồ, lượt cuối, nạp đá và hồi chiêu sau load. Cổng: hết đếm ngược, đích bị phá, đích sát bờ, follower/đồ nặng.
8. Đèn: nạp/chuyển stack nhiên liệu, ngày–đêm, hết viên cuối, load ban đêm và đập thu hồi nhiên liệu.

Những mục này là danh sách kiểm chứng còn lại, **chưa được đánh dấu đã chạy**.
