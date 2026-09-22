# Phàm Nhân Tu Tiên — wiki item từ source hiện hành

## Yêu cầu đã chốt

Người dùng yêu cầu tổng hợp toàn bộ item đã thêm và đã sửa, cùng công thức chế tạo, vào wiki Phàm Nhân. Được đọc source, docs và lịch sử task liên quan. Người dùng chọn extractor làm nguồn chuẩn, yêu cầu viết plan chi tiết và giao GPT-5.6 Terra thực hiện.

Chỉ tái sử dụng layout của Solo Leveling và Linh Giới. Dữ liệu Phàm Nhân phải được dựng mới từ `mods/PhamNhanTuTien`, không ghép snapshot Solo cũ vào catalog. Không giữ khung Phàm Nhân hiện tại. Không cần mockup hoặc thiết kế mỹ thuật mới.

## Route và giao diện

- Trang chính: `/pham-nhan-tu-tien`.
- Gỡ các route Phàm Nhân cũ `/pham-nhan-tu-tien/huong-dan`, `/pham-nhan-tu-tien/config` và alias `/tu-tien-ky`; gỡ redirect của alias trong `next.config.ts` để các URL này trả 404.
- Giữ các trang độc lập `/solo-leveling`, `/linh-gioi`, `/tu-tien`, `/tu-tien-crafting` và trang wiki DST chung.
- Dùng shell/layout đúng mẫu Solo/Linh Giới: SiteHeader, DstPageShell, DstHero của trang mới, sidebar sticky 220px và nội dung bên phải; sidebar cuộn ngang ở mobile.
- Không còn PhamNhanNav hoặc khối Affix độc lập phía trên browser.
- Chủ đề chính là Item, Affix, Hướng dẫn, Config trong cùng browser. Item mở mặc định. Hướng dẫn và Config được dựng lại/đối chiếu theo nguồn hiện hành và hiển thị trong trang chính, không tạo route phụ thay thế.
- Item dùng card kiểu Solo: icon, tên, prefab; nguyên liệu bằng icon và số lượng; nhiều công thức trong cùng card; không thêm lại ô “Sản phẩm nhận được” đã được người dùng bỏ ở Solo. Số lượng đầu ra khác 1 vẫn cần được diễn đạt gọn trong thông tin công thức.
- Tái sử dụng màu, typography, spacing, trạng thái và component hiện có. Lưới công thức hai cột như Solo; chi tiết và liên kết nội dung có thể dùng dialog/hash của Linh Giới.
- Hỗ trợ tìm không dấu, filter loại item, phân trang, URL hash và điều hướng keyboard. Một item chỉ có một bản ghi theo prefab; skin và affix có identity riêng.

## Nội dung trong phạm vi

Item người chơi dùng/nhận được: trang bị, vật phẩm, nguyên liệu, thức ăn/đan dược, hạt/sản vật, bản vẽ/token, công trình và skin chọn được. Bao gồm item kế thừa từ Solo và EVA đã tích hợp, cũng như item vanilla có công thức/công dụng được mod thay đổi.

Boss, mob, nhân vật, FX, projectile, placer và helper không trộn vào Item. Boss/mob vẫn có thể là nguồn nhận, hình tham chiếu hoặc nội dung hướng dẫn. Các vật phẩm không có công thức nhưng có nguồn rơi, cửa hàng, thưởng, thu hoạch hoặc cấp lúc bắt đầu vẫn thuộc catalog. Không coi mọi asset trong thư mục là item đang hoạt động.

## Nguồn dữ liệu

Ưu tiên source Phàm Nhân hiện hành, rồi docs trong mod, báo cáo/spec đã đối chiếu, lịch sử task, cuối cùng mô tả wiki cũ. Giữ bằng chứng theo trường và hash nguồn để xác định snapshot cũ. Lịch sử chat và spec chỉ là bằng chứng quyết định, không chứng minh một tính năng đã triển khai.

Trang Hướng dẫn cũ có 19 chủ đề trong `app/data/pham-nhan-guides.json`. Đọc và tận dụng thông tin hợp lệ trước khi gỡ route. Các nhóm `book-*` là tài liệu lịch sử: phải đối chiếu với source, đặc biệt các affix và cơ chế chiến đấu đã bị bỏ ngày 2026-09-21. Không công bố lại Phản Chấn +7, Ban Phúc, Hồi Não và các set đã bị xóa chỉ vì sách cũ còn mô tả.

## Extractor

1. Bắt đầu từ `modmain.lua`, theo `modimport`/module trong mod; ghi nhận thứ tự nạp, điều kiện cấu hình mặc định và những module không giải quyết được.
2. Dùng Lua sandbox hạn chế để thực thi các đoạn đăng ký/definition và thu `AddRecipe2`, `AddCookerRecipe`, atlas, strings, prefab/skin registration. Cấm I/O, process và network trong Lua. Không chạy gameplay callbacks bằng proxy giả rồi coi kết quả là runtime thật.
3. Recipe động/loop phải được mở rộng; cùng recipe ID bị ghi đè thì lấy trạng thái cuối. Hai recipe ID khác nhau cùng product vẫn là hai phương án. Giữ `product`, `numtogive`, `builder_tag`, `nounlock`, điều kiện blueprint, trạm và bằng chứng.
4. Thu riêng nguồn dung hợp/custom crafting, shop/loot/starting inventory, cooking predicates và skin. Công thức nấu theo tag/điều kiện phải hiển thị đúng điều kiện, không bịa bộ nguyên liệu cố định.
5. Phân loại dựa trên registration, inventory/equipment/edible/building facts và danh sách ngoại lệ có lý do/bằng chứng. Prefab đang hoạt động nhưng chưa phân loại phải xuất hiện trong báo cáo audit; không âm thầm bỏ.
6. Icon lấy từ atlas và image được đăng ký, hỗ trợ tên image khác prefab và atlas nhiều phần tử; dùng asset base game đã có cho nguyên liệu vanilla. Dữ liệu mới không phụ thuộc snapshot Solo cũ. Không tạo ảnh bằng AI.
7. Tạo snapshot JSON deterministic và coverage report. Tách bước build thuần đọc/kiểm định khỏi publish. Build thất bại không làm hỏng snapshot đã xuất. Báo lỗi rõ các module/công thức không hỗ trợ.

## Trạng thái và kiểm chứng

Phân biệt “không có công thức” (đã kiểm chứng), “chưa xác định công thức” (nguồn chưa đủ) và công thức đặc biệt. Không được dùng một trong ba trạng thái để che lỗi extractor.

Coverage có tổng candidate, included, excluded kèm lý do, unresolved, công thức theo từng nguồn, icon thiếu và conflict tài liệu/runtime. Nghiệm thu yêu cầu mọi registration và nhóm nguồn liên quan đã được kiểm kê; unresolved đáng kể phải được xử lý hoặc báo là chưa hoàn tất. Không đặt số item mục tiêu dựa trên snapshot cũ 360 mục/80 công thức.

Các ca bắt buộc: Tầm Bảo Quyển Trục hai công thức một product; Đá Cường Hóa đầu ra 8; Hắc Nguyệt Hồ dùng marble; hai giáp khóa blueprint; EVA dùng recipe hiện hành và builder tag; nấu Lạc Thần theo điều kiện thịt; item rơi không có recipe; skin không phải prefab inventory độc lập; item vanilla bị sửa; affix đã loại không quay lại từ sách cũ.

## An toàn workspace và ranh giới

Workspace có nhiều thay đổi của các task khác, gồm cả task Achievement đang chạy. Làm việc trên source hiện tại, lưu hash/snapshot baseline những file sẽ sửa, kiểm tra lại trước khi ghi. Không sửa runtime mod để làm extractor chạy được; không thay source lịch sử, không reset/clean/stage toàn repo. Không commit, push hoặc deploy trong nhiệm vụ này.

Chỉ xóa file route/navigation cũ đã xác định. Giữ docs, source và icon dùng chung làm bằng chứng/tài nguyên. File dữ liệu cũ có thể giữ để tham chiếu lịch sử nhưng không được là đầu vào quyết định membership/recipe của snapshot mới. Không chạy builder cũ làm ghi đè thay đổi Config/EVA đồng thời.

Đọc tài liệu Next đang cài trước khi sửa frontend. Kiểm chứng extractor, contract dữ liệu, UI behavior, TypeScript, lint, build và browser desktop/mobile theo khả năng môi trường. Báo riêng điều chưa kiểm chứng, không gọi task hoàn tất nếu còn thiếu coverage quan trọng.
