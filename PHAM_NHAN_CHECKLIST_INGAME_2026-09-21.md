# Phàm Nhân Tu Tiên — bàn giao kiểm tra trực tiếp trong game

**Ngày xuất:** 21/09/2026, khoảng 05:55 (UTC+7).  
**Mod hiện tại:** Phàm Nhân Tu Tiên; `modinfo.lua` đang ghi phiên bản **2.0.3**.  
**Thư mục mod:** `mods/PhamNhanTuTien`. Đây là bản tiếp nối Tu Tiên Ký đã tích hợp Solo, không phải ba mod cần bật cùng nhau.  
**Mục đích:** File độc lập để mang sang máy khác, ghi nhận phần đã làm và đánh dấu kết quả kiểm tra native.

> “Đã triển khai” dưới đây nghĩa là có code/báo cáo triển khai trong workspace, không đồng nghĩa đã nghiệm thu trực tiếp trên client DST. Task Mod Config vẫn được công cụ báo active lúc xuất; đây là bản chụp trạng thái, các sửa đổi sau mốc này chưa nằm trong tài liệu.

## 1. Mang gì sang máy khác

- [ ] Sao chép **toàn bộ thư mục `mods/PhamNhanTuTien` hiện tại**, gồm Lua, ảnh `.xml/.tex`, animation, font và metadata; đặt vào thư mục `mods/PhamNhanTuTien` của bản DST trên máy đích.
- [ ] Mang theo file Markdown này. Nếu muốn xem bằng chứng và ảnh, mang thêm `docs/superpowers/reports/`, `docs/superpowers/plans/2026-09-21-pham-nhan-unified-ui-sol.md` và `artifacts/pham-nhan-unified-ui/`.
- [ ] Đồng bộ cùng bản mod trên server và client. Tránh bật đồng thời bản local cũ TuTienKy hoặc bản tích hợp cũ trùng với Phàm Nhân.
- [ ] Nếu tiếp tục save cũ, sao chép/backup cluster save riêng theo cách bạn đang vận hành server. File Markdown và thư mục mod không chứa tiến độ người chơi.
- [ ] Dùng world thử hoặc bản sao save cho bài thử tiêu hao đồ, thất bại cường hóa và save/load.

**Lưu ý chuyển máy:** HEAD tại thời điểm xuất là `c641eb9`, nhưng workspace có thay đổi ngoài commit. Chỉ checkout/pull commit đó không bảo đảm mang đủ các sửa UI mới. File này là checklist, không phải gói cài mod hoặc bản export save.

## 2. Tổng hợp các hạng mục đã làm

| Hạng mục | Trạng thái ghi nhận | Cần nghiệm thu trong game |
|---|---|---|
| Tên/thư mục mod | Đã chuyển sang Phàm Nhân Tu Tiên, thư mục `PhamNhanTuTien`; giữ identifier `hh_`/`ttk_` | Load mod/save cũ, không thiếu prefab hoặc font |
| Phụ Ma | Đã gỡ chế độ riêng; giữ Cường Hóa và migration save cũ; cap +13 | Không còn chọn Phụ Ma; đồ cũ giữ trạng thái hợp lệ |
| Thần Binh Phổ | Đã làm khung bạc–tím, font Noto Serif Medium, 3 tab Thanh Tẩy / Đúc Linh / Kế Thừa, ghost nguyên liệu và bộ lọc slot | Chữ Việt, kéo/thả, lựa chọn thuộc tính, chi phí và kết quả |
| Lam Phượng Luyện Khí Đài | Đã làm UI cường hóa bạc–xanh; preview cấp hiện tại/kế tiếp, chỉ số, đá, xác suất, bùa và hậu quả thất bại | Giao diện client, đồng bộ trạng thái, thao tác với đồ thật |
| Bảng Tổng Hợp | Đã làm Tái Chế 24 ô bên trái; Hợp Thành / Khảm tách tab bên phải; xác nhận thao tác | Slot đúng tab, không nhận click khi ẩn, không thao tác nhầm đồ |
| Bảng chung 6 tab | Đã có shell Nhân vật / Trang bị / Nhiệm vụ / Quân đoàn / Cửa hàng / Kho và đường mở chung | Mở/đóng, phím tắt, chuyển tab, input túi đồ và focus |
| Nhân vật | Đã nhúng UI trạng thái; nút Nhiệm vụ/Quân Đoàn chuyển tab | Chỉ số thật và nút điều hướng |
| Trang bị | Đã nhúng container thật cho Tổng Hợp và Thần Binh Phổ | Chuyển container, item đang cầm, túi/equipment/backpack |
| Nhiệm vụ | Đã thêm Hằng ngày / Hiệp Hội / Thăng hạng, dùng dữ liệu và RPC hiện hữu | Nhận/hủy/hoàn thành/nhận thưởng, chống nhấn lặp |
| Quân đoàn | Đã đổi presentation bạc–tím, giữ 5 tab đệ tử, hồ sơ trái, 6 kỹ năng phải và tiểu sử; dùng UIAnim thật | Cả 5 đệ tử, cấp/EXP/kỹ năng, model và dirty event |
| Cửa hàng Hầm Ngục | Đã đưa vào tab Cửa hàng, đổi theme/layout, 4 nhóm hàng; giữ giá/tồn kho/tiền/RPC | Mua thật, thiếu tiền, hết hàng, nhấn nhanh/đổi tab |
| Kho Quân Vương | Đã nhúng container thật vào tab Kho; giữ giao diện nội bộ, 120 ô và save; scale đồng đều 0.69 | Đủ ô, khóa ô, gửi/rút, stack, reconnect và save/load |

**Phạm vi chưa được xác nhận mới:** Tài liệu này không xác nhận một lần thay assets thế giới của Lam Phượng hoặc sửa Linh Bảo Tế Luyện Đài trong đợt UI hợp nhất. Không coi các ý tưởng trước đây là đã triển khai nếu chưa có bằng chứng tương ứng.

## 3. Chuẩn bị và đường mở

- [ ] Ghi phiên bản game, host/client, độ phân giải và UI scale ở mục kết quả cuối file.
- [ ] Vào bằng EVA và nhân vật/save có các tính năng cần thử; chuẩn bị trang bị, nguyên liệu Thần Binh Phổ/cường hóa, tiền shop và một vài vật phẩm stack được.
- [ ] Mở bảng nhân vật bằng **B** theo binding hiện tại. Mở Cửa hàng bằng **J** theo binding hiện tại. Nếu đã đổi hotkey, dùng binding thực tế.
- [ ] Thử điểm mở Bảng Tổng Hợp, nhân viên Hiệp Hội và kỹ năng Kho hiện có: phải dẫn vào đúng tab của bảng chung, không chồng nhiều screen.
- [ ] Kiểm tra đủ sáu tab, dấu tiếng Việt, icon, tooltip, font, nút đóng và vị trí panel.

## 4. Checklist nghiệm thu

### A. Shell, điều hướng và input — ưu tiên kiểm tra trước

- [ ] Mở/đóng bảng 10 lần; Esc và nút đóng đều hoạt động, không kẹt điều khiển.
- [ ] Chuyển liên tục qua 6 tab rồi trở lại; không trùng panel, nhấp vào tab ẩn hoặc hiện cửa sổ cũ chồng lên.
- [ ] Khi đang ở Trang bị/Kho, kéo đồ giữa panel và inventory/equipment/backpack vẫn đi qua thao tác native.
- [ ] Giữ một item trên con trỏ rồi chuyển tab/đóng bảng: không mất, nhân đôi hoặc mắc item.
- [ ] Chuyển nhanh Trang bị ↔ Kho và đóng ngay khi đang mở container: không xuất hiện container cũ đến muộn.
- [ ] Thử ở 1920×1080 và viewport nhỏ hơn/UI scale khác: không tràn màn hình, chữ đè nhau hoặc slot lệch vị trí click.
- [ ] Nếu dùng controller: chuyển tab, chọn item, quay lại và đóng bảng đúng focus.

### B. Nhân vật và Nhiệm vụ

- [ ] Chỉ số Nhân vật khớp tình trạng thật; nút Quân Đoàn/Nhiệm vụ chuyển đúng tab.
- [ ] Nhiệm vụ có Hằng ngày / Hiệp Hội / Thăng hạng và dữ liệu thật, không chỉ dữ liệu minh họa.
- [ ] Thử nhận, hủy, làm đủ điều kiện và nhận thưởng theo chức năng đang có.
- [ ] Nhấn nhận thưởng/thăng hạng liên tiếp: chỉ xử lý một giao dịch hợp lệ.
- [ ] Đổi tab/đóng bảng trong lúc chờ phản hồi: không crash, không nhận thưởng đôi, mở lại thấy trạng thái đúng.

### C. Trang bị → Tổng Hợp

- [ ] Bên trái luôn có 24 ô Tái Chế. Bên phải có đúng Hợp Thành / Khảm.
- [ ] Hợp Thành hiện các ô chức năng tương ứng; Khảm hiện ô trang bị riêng. Slot tab ẩn không nhận item/click.
- [ ] Thử đưa từ túi, chọn vật liệu, thao tác hợp thành/đổi trị số/khảm bằng đồ thử hợp lệ.
- [ ] Hộp xác nhận hiển thị đúng thao tác; Hủy không tiêu hao; nhấn Xác nhận liên tiếp không gửi lặp.
- [ ] Thay đồ trước khi xác nhận không được áp dụng nhầm thao tác cho item khác.
- [ ] Danh sách châu báu phân trang, tên/số lượng và tooltip khớp đồ đang có.

### D. Trang bị → Thần Binh Phổ

- [ ] Có đúng Thanh Tẩy / Đúc Linh / Kế Thừa; không còn chữ Ngẫu Luyện.
- [ ] Cả 3 tab dùng chữ Việt dễ đọc; checkbox/hàng thuộc tính/nút không bị cắt hoặc thiếu glyph.
- [ ] Ô nguyên liệu cố định khi trống hiện icon mờ; chỉ nhận đúng item, thử nhét sai item phải bị từ chối.
- [ ] Thanh Tẩy: chọn đúng thuộc tính, kể cả ở trang 2; thao tác thật xóa đúng thuộc tính và trừ đúng chi phí.
- [ ] Đúc Linh: đủ/thiếu nguyên liệu cho trạng thái nút đúng; kết quả và tiêu hao khớp cơ chế hiện hữu.
- [ ] Kế Thừa: phân biệt đồ cho/đồ nhận; thuộc tính không tương thích bị từ chối trước khi mất đồ.
- [ ] Chuyển tab với item trong container: item được trả lại an toàn; khi túi đầy kiểm tra đồ rơi gần người chơi, không mất.
- [ ] Nhấn nhanh hoặc đóng khi đang chờ xử lý không nhân đôi thao tác.

**Nguyên liệu dễ nhầm:** Linh Thạch ở đây là `hh_essence`, không phải `ttk_lingshi1`. Bùa Tẩy là số dư ảo `ad_cleanStone`, không phải ô nhét vật phẩm. Nếu shift-transfer bị từ chối, thử kéo trực tiếp vào slot đúng loại.

### E. Quân Đoàn

- [ ] Năm tab: Igris / Beru / Fruitfly / Mặc Ảnh / Hắc Ảnh.
- [ ] Bố cục giữ nguyên: hồ sơ và mô hình bên trái; 6 hàng kỹ năng bên phải; tiểu sử phía dưới.
- [ ] Dùng mô hình động trong game; không dùng tranh Igris của concept làm dữ liệu/mô hình production.
- [ ] Tên, cấp, EXP, chỉ số, kỹ năng đã mở và trạng thái khóa khớp save.
- [ ] Thử đệ tử chưa sở hữu, cấp 1, cấp vừa mở kỹ năng và cấp tối đa 30 nếu save thử cho phép.
- [ ] Tăng EXP/mở kỹ năng khi bảng đang mở: thông tin cập nhật đúng. Đổi đệ tử không giữ nhầm dữ liệu/model cũ.
- [ ] Chữ kỹ năng đã mở màu tím tĩnh; kỹ năng khóa mờ nhưng vẫn đọc được.

### F. Cửa hàng Hầm Ngục

- [ ] Shop ở trong tab Cửa hàng, dùng layout/theme mới; bốn nhóm Thuốc Thợ Săn / Thuốc Đệ Tử / Vật Phẩm / Vũ Khí.
- [ ] Sản phẩm, mô tả, số tiền, giá và tồn kho hiển thị đúng; không thay dữ liệu thành ví dụ trong concept.
- [ ] Mua một món hợp lệ: tiền giảm và item tăng đúng một lần.
- [ ] Thử thiếu tiền, hết hàng và túi đầy; không mất tiền vô lý hoặc tạo item đôi.
- [ ] Double-click mua, đổi nhóm hoặc đóng tab lúc chờ: không lặp giao dịch, không crash, mở lại đồng bộ đúng.

### G. Kho Quân Vương — yêu cầu giữ nguyên UI nội bộ

- [ ] Kho hiện ngay trong tab Kho, không chỉ có nút bật cửa sổ cũ.
- [ ] Khung/nền nội bộ và thứ tự slot giống Kho cũ; chỉ dịch vị trí hoặc scale đồng đều để vừa bảng.
- [ ] Đủ **120 ô**; vị trí kéo/thả khớp hình slot; trạng thái khóa giữ đúng.
- [ ] Gửi/rút item, tách/gộp stack, thay trang bị và túi đầy hoạt động như trước.
- [ ] Đổi tab/đóng bảng rồi mở lại: không có slot ẩn nhận click, không tự mở lại container đã đóng.
- [ ] Lưu, thoát, vào lại/reconnect: item, stack, ô khóa vẫn đúng và thuộc đúng người chơi.
- [ ] Nếu có hai người thử: Kho cá nhân không bị lẫn đồ giữa hai owner.

### H. Lam Phượng Luyện Khí Đài / Cường Hóa

- [ ] Mở công trình: UI bạc–xanh, font Việt; slot nhận trang bị và kéo/thả đúng.
- [ ] Đồ chưa cường hóa có preview ngay trước lần bấm đầu.
- [ ] Cấp hiện tại/kế tiếp, chỉ số, xác suất, đá có/cần và tác dụng bùa khớp trạng thái thật.
- [ ] Trống slot, thiếu đá, đang xử lý hoặc +13: nút không cho gửi thao tác không hợp lệ.
- [ ] Thử thành công và thất bại bằng đồ/save thử; kiểm tra tiêu hao, tụt cấp/mất đồ và bảo vệ theo luật đang có.
- [ ] Không còn lựa chọn Phụ Ma; đồ từ save cũ đọc được và chuyển về Cường Hóa hợp lệ.

## 5. Bằng chứng đã có và giới hạn

Các kết quả dưới đây được ghi lại từ báo cáo hiện có, **không phải các test được chạy lại trong lượt xuất Markdown**:

- Unified UI: Lua syntax 19 file; lifecycle, request gate, late-response/native bridge, shell 6 tab, entry point, native panel, inventory input whitelist, quest subtab và shop open-sync gate: PASS theo báo cáo.
- Tổng Hợp và Thần Binh Phổ: widget regression checks PASS.
- Suite web: 34 file, 233 test PASS theo báo cáo; không thay thế test client DST.
- Thần Binh Phổ, cường hóa và bỏ Phụ Ma có test backend/dedicated-server smoke từ các lượt trước. Dedicated server không xác minh hình ảnh và input trên client.
- Có 7 ảnh tại `artifacts/pham-nhan-unified-ui/acceptance/`: đây là **render kỹ thuật/composite**, không phải screenshot trong game. Ảnh Quân Đoàn dùng concept trong phần nội dung; production dùng UIAnim.
- Chưa có xác nhận native tổng thể về kéo/thả giữa container nhúng và HUD, controller, các độ phân giải, mua/nhận thưởng thực, Kho reconnect/save-load và dirty event của cả 5 đệ tử.

Tài liệu nguồn trong repo:

- `docs/superpowers/reports/2026-09-21-pham-nhan-unified-ui.md`
- `docs/superpowers/reports/2026-09-20-than-binh-pho.md`
- `docs/superpowers/reports/2026-09-20-bang-tong-hop-ui.md`
- `docs/superpowers/reports/2026-09-20-lam-phuong-ui.md`
- `artifacts/pham-nhan-remove-phu-ma/README.md` — đường dẫn TuTienKy trong tài liệu này là lịch sử; khi làm tiếp dùng PhamNhanTuTien.

## 6. Mẫu ghi kết quả trên máy đích

**Ngày/giờ test:**  
**Máy / phiên bản DST:**  
**Bản mod đã copy lúc:**  
**Host hay client / số người chơi:**  
**World/save thử:**  
**Độ phân giải / UI scale / chuột hay controller:**

| Mục | PASS / FAIL / Chưa thử | Hiện tượng / ảnh / log |
|---|---|---|
| A. Shell và input | Chưa thử | |
| B. Nhân vật/Nhiệm vụ | Chưa thử | |
| C. Tổng Hợp | Chưa thử | |
| D. Thần Binh Phổ | Chưa thử | |
| E. Quân Đoàn | Chưa thử | |
| F. Cửa hàng | Chưa thử | |
| G. Kho | Chưa thử | |
| H. Cường Hóa | Chưa thử | |

Khi báo lỗi, ghi: **tab/công trình → đồ và điều kiện ban đầu → các bước bấm/kéo → kết quả mong đợi → kết quả thực tế**. Kèm screenshot và đoạn log thời điểm lỗi; với lỗi item/tiền cần ghi số lượng trước–sau và cho biết thao tác ở host hay client. Thường log client là `Documents/Klei/DoNotStarveTogether/client_log.txt`; log server nằm trong thư mục cluster/shard đang sử dụng (vị trí có thể khác nếu đã cấu hình riêng).
