# Menu Achievement & Level

## Mục tiêu

Thêm một mục điều hướng `Achievement & Level` ngay sau `Cảnh giới Tu Tiên` và một trang tra cứu độc lập cho toàn bộ dữ liệu của mod Steam Workshop `2937640068` (Achievement & Level, phiên bản đã phân tích là `7.3.4`). Trang phải công bố đủ ba nhóm nội dung đã trích xuất: nhiệm vụ, thành tựu và perk/kỹ năng, đồng thời dùng đúng chuỗi bản địa hóa mà mod cung cấp.

## Hành vi sản phẩm đã duyệt

- Header chung có thêm link `Achievement & Level` ngay sau `Cảnh giới Tu Tiên`.
- Link mới trỏ tới `/achievement-level` và được đánh dấu active trên route đó.
- Trang có ba tab: `Nhiệm vụ`, `Thành tựu`, `Kỹ năng`.
- `Nhiệm vụ` là tab mặc định.
- Phần đầu trang hiển thị nguồn mod, phiên bản dữ liệu và các tổng số:
  - 763 lượt nhiệm vụ trong 28 pool;
  - 169 thành tựu;
  - 128 perk/kỹ năng;
  - 18 nhóm nhiệm vụ riêng theo nhân vật.
- Trang có phần tóm tắt hệ thống Level và điểm thuộc tính được trích từ mod.
- Dữ liệu được đóng gói trong repository để production build không phụ thuộc Steam, thư mục game hoặc máy đã cài mod.

## Nguồn dữ liệu và tính toàn vẹn

Nguồn chuẩn là dữ liệu Lua của mod tại Workshop ID `2937640068`, đã được giải mã và đối chiếu trong báo cáo `mod-achievement-level-2937640068.md`.

Tạo artifact dữ liệu có cấu trúc, ưu tiên JSON dưới `data/manual/`, để giao diện không phải parse Markdown hoặc Lua khi chạy. Artifact phải giữ các khóa nguồn cần thiết để truy vết về pool, category và prefab/nhân vật trong mod.

Quy tắc dữ liệu:

- Giữ nguyên chuỗi bản địa hóa Việt mà mod trả về. Nếu file locale Việt của mod vẫn chứa một chuỗi tiếng Anh, hiển thị đúng chuỗi nguồn; không tự dịch hoặc suy diễn nội dung.
- Mỗi lượt nhiệm vụ được định danh bằng pool và vị trí trong pool. Một hành động xuất hiện ở nhiều mùa hoặc nhiều nhân vật vẫn được giữ ở từng ngữ cảnh, không gộp làm mất điều kiện.
- Tổng số trong artifact phải được validate khi load hoặc trong test. Build không được âm thầm công bố dữ liệu thiếu.
- Báo cáo Markdown được giữ làm tài liệu audit có thể đọc; UI chỉ đọc artifact có cấu trúc.

## Mô hình dữ liệu

### Nhiệm vụ

Mỗi nhiệm vụ chứa tối thiểu:

- khóa ổn định;
- slot nhiệm vụ (`1`, `2–4` hoặc `5–6`);
- pool và mùa;
- nhân vật yêu cầu nếu có;
- mô tả/cách thực hiện theo chuỗi nguồn;
- hành động và mục tiêu nguồn nếu có;
- số lượng yêu cầu;
- số lần lặp (`1` hoặc `10`);
- nhãn nhóm hiển thị.

Các pool được trình bày theo ba khối nghiệp vụ:

1. Nhiệm vụ nhân vật ở slot 1.
2. Nhiệm vụ theo mùa ở slot 2–4.
3. Nhiệm vụ đếm/lặp ở slot 5–6.

### Thành tựu

Mỗi thành tựu chứa tối thiểu khóa nguồn, tên, mô tả/cách hoàn thành, mục tiêu số lượng và category. Giữ đủ 169 bản ghi trong 16 category của báo cáo, bao gồm nhóm nhiệm vụ mùa.

### Kỹ năng

Mỗi perk/kỹ năng chứa tối thiểu khóa nguồn, tên, mô tả hiệu ứng, giá Sao, category và yêu cầu nhân vật nếu có. Giữ đủ 128 bản ghi trong sáu nhóm: thuộc tính, khả năng, chuyên môn nhân vật, mở khóa chế tạo, dùng một lần và toàn shard.

Thông tin thưởng nhiệm vụ theo nhân vật ở mốc 2 và mốc 4 được hiển thị cùng phần kỹ năng, nhưng tách nhãn khỏi danh sách perk đổi bằng Sao để không làm sai tổng 128 perk.

## Thiết kế giao diện

Route mới dùng cùng shell, palette, typography, focus treatment và chiều rộng nội dung với `/tu-tien`.

### Hero và tổng quan Level

- Eyebrow nêu rõ mod `2937640068`.
- Tiêu đề `Achievement & Level`.
- Mô tả ngắn giải thích đây là dữ liệu tra cứu nhiệm vụ, thành tựu và kỹ năng.
- Bốn chỉ số tổng quan dùng component hero hiện có.
- Khối Level tóm tắt quy tắc XP, điểm thuộc tính, Sao và các mốc thưởng bằng nội dung đã trích từ mod.

### Tab Nhiệm vụ

- Thanh tìm kiếm khớp không phân biệt hoa thường với mô tả, hành động, mục tiêu và tên nhân vật.
- Bộ lọc: loại slot, mùa và nhân vật.
- Mặc định không có filter, vì vậy toàn bộ 763 lượt nhiệm vụ đều nằm trong kết quả.
- Kết quả nhóm theo khối nghiệp vụ rồi theo mùa/nhân vật, với số lượng của từng nhóm.
- Mỗi dòng/thẻ nêu rõ cách làm, số lượng, số lần lặp và nhân vật yêu cầu. Trường không áp dụng không được hiện dưới dạng giá trị giả.

### Tab Thành tựu

- Thanh tìm kiếm theo tên, mô tả và khóa nguồn.
- Bộ lọc category.
- Mỗi dòng/thẻ nêu tên, cách hoàn thành, tiến độ yêu cầu và category.
- Không phân trang; mặc định có đủ 169 bản ghi trong kết quả.

### Tab Kỹ năng

- Thanh tìm kiếm theo tên, mô tả, khóa nguồn và nhân vật.
- Bộ lọc category và nhân vật yêu cầu.
- Mỗi dòng/thẻ nêu tác dụng, giá Sao, category và điều kiện nhân vật.
- Phần thưởng nhiệm vụ theo nhân vật được đặt trong section riêng sau danh sách perk.

### Responsive và accessibility

- Desktop dùng hàng dữ liệu hoặc grid đủ rộng để quét nhanh; mobile chuyển thành card một cột mà không tạo scroll ngang toàn trang.
- Tab, input, select và nút xóa filter phải dùng được bằng bàn phím, có accessible name và focus ring hiện hữu.
- Mỗi trạng thái không có kết quả có thông báo rõ ràng và nút `Xóa bộ lọc`.
- Tổng số kết quả thay đổi theo filter được thông báo bằng vùng status phù hợp.

## Kiến trúc triển khai

- `app/components/site-header.tsx`: mở rộng `SiteSection` và danh sách link.
- `app/achievement-level/page.tsx`: Server Component đọc artifact, render metadata, hero và truyền dữ liệu đã validate vào trình duyệt tương tác.
- `app/components/achievement-level-browser.tsx`: Client Component quản lý tab, tìm kiếm và filter.
- `app/lib/achievement-level.ts`: type, parser/validator, normalization, filter và group selector thuần.
- `data/manual/achievement-level.json`: toàn bộ dữ liệu có cấu trúc đã trích từ mod.

Selector và parser không phụ thuộc React để có thể kiểm thử đầy đủ. Toàn bộ filter chạy phía client trên dữ liệu tĩnh; quy mô 763 + 169 + 128 bản ghi không cần backend, network request hoặc pagination.

## Trạng thái lỗi

- Artifact sai schema, trùng khóa trong cùng ngữ cảnh hoặc sai tổng số chuẩn làm test/build thất bại.
- Nếu filter không có kết quả, UI hiển thị empty state; đây không phải lỗi dữ liệu.
- Không có fallback đọc trực tiếp file Markdown hoặc đường dẫn Steam trong production.

## Kiểm thử

Thực hiện theo TDD:

1. Parser chấp nhận artifact chuẩn và trả đúng 763 nhiệm vụ, 169 thành tựu, 128 perk, 28 pool và 18 nhóm nhân vật.
2. Parser từ chối schema sai, khóa trùng hoặc tổng số không khớp.
3. Selector nhiệm vụ lọc đúng theo từ khóa, slot, mùa và nhân vật mà không làm mất bản ghi trùng ngữ cảnh.
4. Selector thành tựu lọc đúng từ khóa và category.
5. Selector kỹ năng lọc đúng category và nhân vật.
6. Header có link `Achievement & Level` sau `Cảnh giới Tu Tiên` và đánh dấu active đúng.
7. Route render đủ ba tab, tổng số và phần tóm tắt Level.
8. UI đổi tab, lọc, hiển thị số kết quả và xóa filter đúng.
9. Chạy toàn bộ Vitest, ESLint, TypeScript và production build.
10. Kiểm tra trực quan desktop/mobile cho `/achievement-level` và kiểm tra header không tràn ở viewport hẹp.

## Tiêu chí nghiệm thu

- Menu `Achievement & Level` xuất hiện ngay sau `Cảnh giới Tu Tiên`.
- `/achievement-level` hoạt động và link active đúng.
- Ba tab công bố đủ dữ liệu chuẩn, không bỏ hoặc gộp sai ngữ cảnh.
- Người dùng tìm kiếm/lọc được theo các chiều đã duyệt và có thể quay lại toàn bộ kết quả.
- Nội dung dùng chuỗi locale nguồn của mod và ghi rõ mod ID/phiên bản.
- Trang hoạt động độc lập với cài đặt Steam.
- Test, lint, typecheck và production build đều thành công.

## Triển khai Git

- Commit đặc tả riêng trước khi lập kế hoạch triển khai.
- Sau khi code được review và xác minh, commit toàn bộ feature trên `master` hiện tại.
- Push trực tiếp `master` lên remote theo yêu cầu của người dùng.

## Ngoài phạm vi

- Không sửa hoặc ghi ngược vào mod Workshop.
- Không tự động cập nhật dữ liệu khi Workshop phát hành phiên bản mới.
- Không thêm đăng nhập, lưu tiến độ cá nhân hoặc đồng bộ trạng thái nhiệm vụ trong game.
- Không dịch lại các chuỗi mà locale Việt của mod vẫn để tiếng Anh.
- Không thay đổi các trang Vật phẩm, Nhân vật, Cảnh giới Tu Tiên hoặc design system ngoài việc thêm mục điều hướng mới.
