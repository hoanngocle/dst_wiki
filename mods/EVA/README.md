# EVA

Phiên bản hiện tại: **1.2.0**. Thư mục luôn là `EVA`; số phiên bản nằm trong
`modinfo.lua`, lịch sử thay đổi trong `CHANGELOG.md`. Mỗi bản phát hành mới tăng
phiên bản: sửa lỗi/ảnh nhỏ tăng patch, thêm hoặc nâng cấp tính năng tăng minor.
Đóng gói bằng `mods/eva-assets-work/release_eva.py`, tạo `EVA_v<version>.zip`
với thư mục bên trong là `EVA`. Công cụ từ chối ghi đè bản cùng số có nội dung khác.

Chỉ tạo thế giới mới với bản này. Mã nhân vật hiện tại là `eva`.

EVA là nhân vật độc lập cho Don't Starve Together, giữ prefab nội bộ
`eva` làm mã kỹ thuật. Chỉ hỗ trợ world mới; không có skin riêng.

Bảng kỹ năng ở góc phải dưới mặc định thu gọn vào nút pháp ấn tím bạc; bấm nút để mở/đóng
cả năm biểu tượng, không chiếm ô hành trang. Từ trái sang phải theo cấp mở khóa:
**Sinh Chi Hoa (10)**, **Tử Phong Tụ Linh (20)**, **Tinh Vũ Nguyệt Dực (30)**,
**Dạ Du (50)**, **Trảm Linh (100)**. Kỹ năng chưa đủ cấp vẫn hiện mờ khi mở bảng.
Sinh Chi Hoa và Cánh kích hoạt ngay; ba kỹ năng còn lại mở tâm ngắm rồi chỉ thi triển khi xác nhận trên thế giới. Có thể hủy
tâm ngắm miễn phí. Phím G/H/J cũ vẫn là lối tắt tùy chọn.

- **Sinh Chi Hoa**: tốn 10 Hồn Lực mỗi lần bật thành công; nhấn G mặc định, tồn tại 15 giây, hồi chiêu 60 giây
  tính từ lúc kích hoạt. Kỹ năng có đạn 80 sát thương mỗi 0,2 giây trong
  phạm vi 12, hào quang 67 sát thương mỗi 0,5 giây trong bán kính 6, hồi 5%
  máu tối đa ở giây 0/3/6/9/12 và khiên hữu hạn bằng 25% máu tối đa.
- **Tinh Vũ Nguyệt Dực**: nhấn H mặc định để bật/tắt cánh bạc–tím với họa tiết trăng sao. Mỗi lần
  bật thành công tốn đúng 100 Hồn Lực, không tốn duy trì; tăng 8% tốc độ và cho
  phép đi trên biển. Không thể tự tắt khi đang trên biển mà không có thuyền.
- **Huyền Thiên Trảm Linh Kiếm**: nhấn J mặc định để dựng năm lưỡi hái tím
  quanh vị trí con trỏ và một lưỡi hái lớn ở tâm. Kỹ năng mở ở cấp 100;
  mỗi lần thi triển thành công tốn 100 Hồn Lực và hồi chiêu 60 giây. Kẻ địch trong ngũ giác bị trói;
  đòn tâm gây 734 sát thương và tia sáng gây 200 sát thương mỗi 0,5 giây.
- **Hồ Ảnh**: nhấp chuột phải lên mặt đất trống trong 20 đơn vị để lướt tới
  điểm đã chọn. Kỹ năng miễn phí, hồi chiêu 12 giây. Tương tác với vật thể,
  vật phẩm đang cầm, xây dựng, cưỡi và tâm ngắm đang mở luôn được ưu tiên.
- **Tử Phong Tụ Linh**: chọn biểu tượng rồi xác nhận điểm trong tầm 12. Tốn
  3 Hồn Lực, hồi chiêu 10 giây; trong 7 giây thu hoạch/chặt/đào hợp lệ và kéo
  vật phẩm rời về tâm trong bán kính 8 nhưng không đưa vào hành trang. Không
  nhổ cây trồng, không tác động vật đang được cầm, hòm, nơi giao dịch hay công trình.
- **Dạ Du**: chọn biểu tượng rồi xác nhận điểm trong tầm 12. Kỹ năng
  tìm kẻ địch hợp lệ gần nhất trong bán kính 2; nếu không có mục tiêu thì không
  tốn Hồn Lực. Lần dùng hợp lệ tốn 5 Hồn Lực, hồi chiêu 15 giây. Đạn không gây
  sát thương trực tiếp; khi trúng sẽ khiến mục tiêu chịu thêm 10% sát thương
  trong 5 giây. Dùng lại chỉ làm mới thời gian, không cộng dồn.
- **Kiếm khí cận chiến**: mỗi hai đòn đánh cận chiến bằng vũ khí trúng hợp lệ
  tạo một kiếm khí tím miễn phí gây 50 sát thương. Đánh tay không, làm việc,
  đánh hụt, đòn tầm xa và sát thương do kỹ năng tạo ra không được tính.
- **Hồn Lực**: EVA nhận +1 từ mục tiêu thường, +10 từ ghost và +30 từ
  mục tiêu epic. Hồn Lực không tăng sát thương, không tạo chí mạng và không
  tự hao; tốn 100 khi bật Tinh Vũ Nguyệt Dực, 3 khi dùng Tử Phong Tụ Linh, 5 khi
  dùng Dạ Du và 100 khi thi triển kiếm trận.
- **Cấp EVA**: lưu riêng trong save, tăng theo cấp nhân vật của Achievement &
  Level; tự nhận cấp hiện tại khi tải. Tắt/reset mod Level không làm mất cấp EVA
  đã ghi nhận. Không có thanh kinh nghiệm riêng; nhân vật mới chưa có nguồn cấp
  bắt đầu từ cấp 1.
- **Sức chứa Hồn Lực**: `min(1000, 100 + 6 × (cấp EVA − 1))`, đạt 1000 ở
  cấp 151. Nhân vật mới bắt đầu với 100/100 Hồn Lực. Đã bỏ tùy chọn giới hạn cũ trong cấu hình.
- **Hồi Hồn Lực**: từ cấp 101, hồi 1 mỗi giây khi còn sống; dừng ở giới hạn.
- **Khi chết**: giữ 10% Hồn Lực hiện có, làm tròn xuống (257 còn 25). Tải lại
  save dạng hồn ma không bị trừ lần nữa; hồn ma không tự hồi Hồn Lực.
- **Lưỡi hái EVA**: vũ khí cận chiến thường với sát thương, độ bền và công
  thức có thể cấu hình.

Các kỹ năng cũ của EVA như Soul Strike, chí mạng theo Hồn Lực, hồi máu khi
hạ mục tiêu, bất tử/ngủ hồi phục và hiệu ứng sanity đặc biệt không thuộc EVA.
Đã loại bỏ hoàn toàn mũ, kazoo và rượu EVA cùng tài nguyên liên quan.
Các vật phẩm cũ này không còn được hỗ trợ trong save. Icon chế tạo dùng chân dung EVA.

EVA chạy độc lập, không import runtime Tu Tiên và không yêu cầu Solo Leveling. Xem
[README_EVA.md](README_EVA.md) để biết đầy đủ quy tắc mục tiêu, thứ tự khiên,
cài đặt, kiểm tra tự động và checklist kiểm tra trong game.

Khi dùng cùng Solo Leveling, đạn/vùng sát thương/kiếm khí EVA vẫn hưởng chỉ số
sát thương và chí mạng Solo, nhưng không kích hoạt đánh lan cận chiến của Solo.
Đòn chém thường vẫn đánh lan bình thường. Hồi chiêu EVA giữ nguyên các mốc trên.

Chưa kiểm thử trong game hoặc multiplayer.

## Mốc mở kỹ năng

| Cấp EVA | Kỹ năng |
|---:|---|
| 1 | Hồ Ảnh (chuột phải), nội tại Kiếm khí |
| 10 | Sinh Chi Hoa |
| 20 | Tử Phong Tụ Linh |
| 30 | Tinh Vũ Nguyệt Dực |
| 50 | Dạ Du |
| 100 | Huyền Thiên Trảm Linh Kiếm |

Biểu tượng chưa mở được làm mờ và ghi cấp yêu cầu. Server kiểm tra cấp ở mọi
đường dùng kỹ năng, bao gồm phím tắt và RPC. Ultimate gây tối đa 2934 sát thương
cơ sở nếu một mục tiêu trúng cả đòn tâm và 11 nhịp; vẫn áp dụng quy tắc sát thương
Solo hiện có. Không thêm Diệt Chi Hoa. Cấp 70 không mở kỹ năng mới.
