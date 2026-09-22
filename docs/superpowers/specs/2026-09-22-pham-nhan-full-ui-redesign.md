# Phàm Nhân Tu Tiên — Full UI Redesign

## Mục tiêu

Thay toàn bộ lớp trình bày của giao diện Phàm Nhân bằng visual language trong `artifacts/`, đồng thời giữ nguyên cơ chế gameplay, dữ liệu, RPC, container, save và quyền sở hữu hiện có. Kết quả phải giống concept về khung bạc trắng, ngọc tím, nền tối, typography và phân cấp nội dung; giao diện phải tự co theo độ phân giải như UI Solo gốc và không bị phóng lớn, cắt mép hoặc bung popup.

## Source of truth

Các artifact mới nhất là chuẩn thiết kế:

- Shell sáu tab: `artifacts/pham-nhan-unified-ui/trang-bi-phac-thao.png`
- Yêu cầu shell và Kho: `artifacts/pham-nhan-unified-ui/README.md`
- Bảng Tổng Hợp: `artifacts/bang-tong-hop/v3/hop-thanh.png` và `kham.png`
- Thần Binh Phổ: `artifacts/than-binh-pho/v4/thanh-tay.png`, `duc-linh.png`, `ke-thua.png`, `dong-thuoc-tinh.png`
- Lâm Phượng Luyện Khí Đài: toàn bộ `artifacts/lam-phuong-ui/`
- Tham chiếu Nhiệm vụ và Quân đoàn: `artifacts/current-quests/` và `artifacts/current-army/`
- Tham chiếu widget, slot và texture gốc: `artifacts/forge-ui-preview/`

Ảnh concept mô tả bố cục và phong cách, không định nghĩa cơ chế, vật phẩm hoặc chỉ số mới. Khi nhiều phiên bản cùng tồn tại, thư mục phiên bản cao nhất thắng.

## Ràng buộc phạm vi

Đây là thay đổi UI. Không thay đổi:

- Prefab, component, netvar, RPC hoặc payload hiện có.
- Luật nhận vật phẩm, chi phí, xác suất, kết quả cường hóa, khảm, tái chế, đúc linh, kế thừa hoặc thanh tẩy.
- Quy tắc quyền sở hữu Kho, khóa ô, gửi/rút hoặc cấu trúc save.
- Dữ liệu nhiệm vụ, quân đoàn, cửa hàng, cấp độ, kỹ năng hoặc thành tựu.
- Các mã `ttk_` và `hh_` cần giữ để tương thích save và tooling.

Không đưa sách hướng dẫn hoặc cấu hình tooltip vào shell chung. Không dùng ảnh concept nguyên khối làm UI tương tác.

## Kiến trúc hiển thị

### Scale và anchor

Ảnh 1536×1024 chỉ là tài liệu bố cục, không phải canvas runtime cố định.

UI tuân theo mẫu Solo gốc trong mod `3780347550`:

- Root của mỗi surface neo giữa màn hình bằng `ANCHOR_MIDDLE`.
- Mỗi surface chỉ có một root `SCALEMODE_PROPORTIONAL`.
- DST tự co giao diện theo độ phân giải và HUD scale.
- Không tự nhân scale theo kích thước ảnh concept và không cho scale runtime vượt `1`.
- Không re-parent `ContainerWidget` vào một proportional root khác.
- Scale slot Thần Binh Phổ bắt đầu từ baseline Solo gốc `0.7`; thay đổi cục bộ chỉ được phép khi artifact yêu cầu và phải có test chống phóng lớn.

Hiện trạng đổi scale container Thần Binh Phổ từ `0.7` thành `1.05` và re-parent vào shell proportional là nguyên nhân trực tiếp gây phóng sai và popup lệch anchor. Thiết kế mới loại bỏ cả hai yếu tố này.

### Shell chung

`TTKUnifiedScreen` chịu trách nhiệm:

- Vẽ khung, tiêu đề, nút đóng và sáu tab.
- Chọn panel đang hoạt động.
- Quản lý focus/controller và phím đóng.
- Theo dõi native container đang mở để chuyển input và đóng lifecycle đúng lúc.

Shell không chứa business logic và không sở hữu slot của native container. Native container giữ parent/lifecycle như Solo gốc; bridge chỉ đồng bộ panel đang chọn, visibility, input và close state.

### Theme và widget dùng chung

Một theme chung định nghĩa font, màu, kích thước chữ, spacing, divider và trạng thái focus/disabled/active. Các primitive dùng chung gồm:

- Khung ngoài và góc lá bạc.
- Ngọc tím giữa cạnh và góc dưới.
- Tab chính, tab phụ và primary action button.
- Slot vuông, divider và diamond marker.
- Tiêu đề, nhãn, mô tả, cảnh báo và trạng thái rỗng.

Các primitive chỉ xử lý trình bày. Callback và dữ liệu được truyền từ panel hiện có.

## Các panel

### Nhân vật

Giữ nguồn dữ liệu, cấp độ, chỉ số và kỹ năng của `hh_status_ui`. Chuyển bố cục sang theme chung và đảm bảo trạng thái character hiện tại vẫn cập nhật theo netvar/event cũ.

### Trang bị — Tổng hợp

Giữ `hh_ui_container`, 28 slot, luật slot, RPC và dialog xác nhận. Bố cục theo `bang-tong-hop/v3`:

- 24 slot tái chế ở cột trái.
- Hai subtab Hợp Thành và Khảm.
- Slot thao tác, số dư, trạng thái và nút ở vùng phải.
- Dialog xác nhận nằm trong cùng hệ tọa độ panel, không dùng anchor màn hình độc lập.

### Trang bị — Thần Binh Phổ

Giữ `hh_forge_container`, `ttk_forge_rules`, state đồng bộ và RPC hiện tại. Ba mode Thanh Tẩy, Đúc Linh và Kế Thừa dùng layout `than-binh-pho/v4`. Popup chọn dòng và xác nhận là child cục bộ của panel.

### Nhiệm vụ

Giữ nhiệm vụ ngày, nhiệm vụ rank, Guild Quest và thao tác Hiệp Hội từ xa. Chỉ thay khung, typography, tab và spacing. Không phát sinh nhiệm vụ hay phần thưởng mới.

### Quân đoàn

Giữ lựa chọn bóng, cấp, EXP, talent, chỉ số và các thao tác triệu hồi/nâng cấp hiện có. Trình bày lại trên khung chung; animation/model có thể tiếp tục do widget hiện có cung cấp.

### Cửa hàng

Giữ category, chu kỳ hàng, stock, xu, trạng thái thiếu xu và RPC mua. Thay panel, card, tab và trạng thái selected/focus theo theme chung.

### Kho

Hiển thị đầy đủ container 120 ô trong panel Kho, bao gồm khóa ô, gửi/rút, quyền sở hữu và save hiện có. Không thay Kho bằng một nút mở bảng cũ và không sao chép dữ liệu vật phẩm sang state UI riêng.

### Lâm Phượng Luyện Khí Đài

Đây vẫn là UI riêng của công trình. Bốn trạng thái rỗng, có thể cường hóa, có bảo vệ và tối đa lấy từ `artifacts/lam-phuong-ui/`. Logic xác suất, chi phí, bùa và RPC không đổi.

## Luồng dữ liệu và lifecycle

1. Người chơi mở shell hoặc một UI công trình qua entry point hiện có.
2. Panel đọc replica/netvar/component qua adapter hiện có.
3. Widget render state nhưng không tự suy diễn cơ chế gameplay.
4. Thao tác người chơi gọi callback/RPC hiện có.
5. Event/netvar dirty làm mới panel tương ứng.
6. Đổi tab đóng native container của tab cũ trước khi mở tab mới.
7. Đóng shell hoặc container dọn focus, registry, input forwarding và cờ open theo đúng thứ tự hiện tại.

Yêu cầu open bị từ chối hoặc dữ liệu chưa đồng bộ hiển thị trạng thái chờ/lỗi trong panel. Không để native widget mồ côi hoặc item bị khóa sau khi panel đóng.

## Asset pipeline

Artifact PNG là nguồn tham chiếu bất biến. Script build sẽ tạo asset runtime riêng:

- Cắt hoặc tái dựng frame, góc, tab, button, slot, divider và marker thành texture có nền trong suốt.
- Đóng texture vào atlas DST bằng công cụ hiện có của dự án.
- Ghi nhận kích thước vùng và tên texture ổn định để widget không phụ thuộc tọa độ crop ngầm.
- Không chỉnh trực tiếp file `.tex` bằng tay.
- Renderer artifact tiếp tục dùng được để tạo preview so sánh.

Asset runtime phải được đăng ký trước khi widget tham chiếu tới atlas.

## Font tiếng Việt

Font serif Việt được build lại từ source đã cấp phép và dùng metadata tương thích font Klei:

- `alphaChnl=1`.
- Các kênh `redChnl`, `greenChnl`, `blueChnl` theo font game (`0`).
- Alias chỉ được công bố sau khi `LoadFont` thành công.
- Widget lấy font tại thời điểm dựng UI, không cache fallback trước khi font được nạp.
- Nếu load thất bại, UI dùng font DST hỗ trợ tiếng Việt và ghi log chẩn đoán một lần; không hiển thị glyph thành ô trắng.

## Kiểm thử

### Tự động

- Test shell có đúng sáu tab, focus và lifecycle đóng/mở.
- Test không re-parent native container.
- Test mỗi surface không tạo proportional root lồng nhau.
- Test baseline scale của Thần Binh Phổ không lớn hơn Solo gốc.
- Test slot mapping, visibility và callback/RPC không đổi.
- Test font asset, metadata channel, thứ tự load và fallback.
- Test đóng shell/container dọn registry, focus và cờ open.
- Chạy toàn bộ test suite của mod sau các test mục tiêu.

### Visual regression

Renderer Lua tạo ảnh ở:

- 1920×1080.
- 1366×768.
- 1024×768.

Mỗi ảnh phải chứng minh frame, tab, chữ, slot, dialog và nút hành động nằm trong viewport, không chồng nhau và không vượt biên. So sánh trực tiếp với artifact mới nhất cho Tổng hợp, Thần Binh Phổ và Lâm Phượng.

### Smoke test trong game

Mở lần lượt sáu tab, mọi subtab Trang bị, bốn trạng thái Lâm Phượng, dialog xác nhận và Kho 120 ô. Kiểm tra chuột, controller, tooltip, đóng bằng nút/phím hủy và chuyển tab khi native container đang mở. Client log không được có lỗi font, atlas, widget hoặc RPC mới.

## Tiêu chí hoàn thành

- Full UI dùng visual language của artifact mới nhất.
- UI nhỏ lại đúng theo cơ chế proportional của Solo gốc trên màn hình thấp hơn.
- Không còn glyph dạng khối trắng.
- Không còn popup hoặc native container bung khỏi khung.
- Toàn bộ thao tác gameplay hiện có vẫn hoạt động và dữ liệu/save không đổi.
- Test tự động, visual regression và smoke test đạt yêu cầu.

