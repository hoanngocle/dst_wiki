# Danh mục chế tạo Tu Tiên của Hàn Lập

## Mục tiêu

Thay toàn bộ mục điều hướng và trang “Nhân vật” bằng một danh mục chuyên biệt cho những vật phẩm Hàn Lập thực sự có thể tạo trong mod Tu Tiên. Danh mục phải ưu tiên độ tin cậy: chỉ công bố món có cách tạo và công dụng đã được xác thực từ dữ liệu hoặc mã nguồn mod.

Hai món “Thân Ngoại Hoá Thân” và “Thiên Cơ Ốc” là ví dụ đại diện cho phạm vi cần tìm, không phải ngoại lệ hoặc danh sách cố định. Chúng phải đi qua cùng quy trình xác minh như mọi món khác.

## Phạm vi giao diện

- Xóa route `/characters`; không redirect. Truy cập URL cũ trả về trang 404 theo cơ chế của Next.js.
- Xóa link “Nhân vật” khỏi header và thay bằng link “Chế tạo Tu Tiên”.
- Route mới là `/tu-tien-crafting` với tiêu đề “Đồ chế Tu Tiên của Hàn Lập”.
- Trang chỉ hiển thị nguồn Tu Tiên nên không có bộ lọc DST/Tu Tiên.
- Giữ tìm kiếm theo tên Việt, tên Anh và prefab code; giữ bộ lọc loại vật phẩm khi loại đó có kết quả.
- Mỗi kết quả hiển thị ảnh, tên, prefab code, loại, công thức/cách tạo và ghi chú điều kiện cần thiết.
- Bấm thẻ kết quả mở modal chi tiết hiện có.

Không xóa các entity nhân vật khỏi dữ liệu nền hoặc các type dùng chung. Chỉ xóa bề mặt sản phẩm dành cho danh mục nhân vật: route, link điều hướng, selector và test không còn được sử dụng.

## Quy tắc chọn vật phẩm

Một món được đưa vào danh mục khi thỏa toàn bộ điều kiện sau:

1. Thuộc namespace `tu_tien`.
2. Hàn Lập có thể tạo món đó trong một lượt chơi hợp lệ ở bất kỳ giai đoạn tiến triển nào.
3. Có bằng chứng về cách tạo.
4. Có bằng chứng về công dụng sau khi tạo.
5. Mọi nguyên liệu được hiển thị đều phân giải được tới một entry chi tiết trong catalog đầy đủ.

### Quyền chế tạo của Hàn Lập

Các công thức hợp lệ gồm:

- Không giới hạn nhân vật.
- Giới hạn cho mọi `player`.
- Giới hạn bởi builder tag `xd_hantianzun`.
- Công thức hoặc cơ chế tạo qua trạm, bí quyển, cảnh giới hay tiến trình mà Hàn Lập có thể tiếp cận.

Loại công thức yêu cầu builder tag riêng của nhân vật khác. Yêu cầu công nghệ, cảnh giới, trạm hoặc vật phẩm mở khóa không làm món bị loại; chúng được hiển thị như điều kiện chế tạo.

### Bằng chứng cách tạo

Ít nhất một trong các nguồn sau phải tồn tại và nêu được đầu vào cùng điều kiện tạo:

- Recipe tĩnh đã parse.
- Công thức của trạm chế tạo hoặc luyện đan.
- Quan hệ tạo vật phẩm đã trích xuất từ mã nguồn mod, chẳng hạn hành động, bí quyển hoặc cơ chế đặc biệt.

Tên hoặc prefab tồn tại đơn lẻ không được coi là công thức. Không dùng allowlist để ép một món xuất hiện.

### Bằng chứng công dụng

Ít nhất một trong các nguồn sau phải mô tả được hành vi của món:

- Hiệu ứng khi dùng, trang bị hoặc kích hoạt.
- Vai trò làm nguyên liệu cho một công thức khác.
- Chức năng công trình/trạm.
- Cơ chế triệu hồi, điều khiển hoặc tương tác đã được trích xuất.

Món không có hành vi xác thực hoặc chỉ là prefab nội bộ không sử dụng được sẽ bị loại.

### Dữ liệu chưa đầy đủ

Nếu recipe tĩnh chưa có nhưng mã nguồn cho thấy món được tạo bằng cơ chế khác, bổ sung extraction hoặc dữ liệu chi tiết có dẫn chứng trước khi đưa món lên trang. Nếu không xác minh được cách tạo hoặc công dụng, món không xuất hiện và được ghi vào báo cáo audit thay vì được thêm thủ công.

## Kiến trúc dữ liệu

Tạo một selector chuyên biệt nhận catalog entity cùng danh sách `ItemListEntry` và trả về các entry Hàn Lập có thể chế tạo. Selector chịu trách nhiệm:

- Hợp nhất recipe tĩnh, recipe qua trạm/luyện đan và quan hệ tạo đặc biệt.
- Đánh giá builder tag và loại công thức của nhân vật khác.
- Kiểm tra bằng chứng công dụng.
- Kiểm tra toàn bộ ingredient reference có thể phân giải.
- Sắp xếp kết quả ổn định theo nhóm điều kiện chế tạo rồi theo tên.

Selector không chứa danh sách ID dành riêng cho Thân Ngoại Hoá Thân, Thiên Cơ Ốc hoặc bất kỳ ví dụ cụ thể nào. Nếu extractor hiện tại chưa biểu diễn đủ quan hệ tạo đặc biệt, mở rộng contract dữ liệu với một kiểu creation method có nguồn dẫn chứng thay vì gán recipe giả.

Trang truyền hai tập dữ liệu riêng biệt cho UI:

- `items`: danh sách rút gọn chỉ gồm kết quả Hàn Lập chế được.
- `referenceItems`: toàn bộ catalog DST và Tu Tiên dùng để phân giải nguyên liệu và nội dung modal.

Việc tách này ngăn nguyên liệu biến mất khỏi khả năng tương tác chỉ vì nó không nằm trong danh sách kết quả của trang.

## Tương tác modal nguyên liệu

Tất cả nơi dùng renderer công thức chung, bao gồm các công thức trong phần nội dung liên quan đến “Cảnh giới tu tiên”, phải nhận `itemsById` của catalog đầy đủ và `onSelectItem`.

- Bấm nguyên liệu mở `ItemDetailPeek` cho đúng item.
- Nếu modal đã mở, bấm nguyên liệu thay nội dung trong cùng một dialog; không tạo modal lồng nhau.
- Nội dung modal cuộn về đầu khi item thay đổi.
- Escape, nút đóng, click backdrop và focus trap tiếp tục hoạt động như hiện tại.
- Mọi chip nguyên liệu trên trang mới phải là button có accessible name chứa tên và số lượng.

Dữ liệu xuất bản phải bảo đảm ingredient reference phân giải được. Trạng thái nguyên liệu không tương tác không được phép xuất hiện trong danh mục mới.

## Trạng thái lỗi và rỗng

- Nếu chưa có kết quả sau khi lọc, hiển thị empty state và nút xóa bộ lọc.
- Nếu toàn bộ dữ liệu đầu vào không hợp lệ, quá trình build/test phải thất bại thay vì xuất bản một trang trống gây hiểu nhầm.
- Các món bị loại vì thiếu recipe, công dụng hoặc ingredient reference được thống kê trong audit dành cho dữ liệu, không hiển thị cho người dùng cuối.

## Kiểm thử

Thực hiện theo TDD với các nhóm test sau:

1. Selector giữ công thức phổ thông, `player` và `xd_hantianzun`.
2. Selector loại công thức khóa bởi nhân vật khác.
3. Selector giữ công thức qua trạm/cơ chế đặc biệt khi có đầy đủ bằng chứng.
4. Selector loại prefab thiếu cách tạo, thiếu công dụng hoặc có ingredient reference không phân giải được.
5. Thân Ngoại Hoá Thân và Thiên Cơ Ốc xuất hiện khi dữ liệu nguồn của chúng thỏa cùng contract chung; test không bypass selector bằng allowlist.
6. Header có “Chế tạo Tu Tiên” và không còn “Nhân vật”.
7. Route mới render đúng danh sách; module route `/characters` không còn tồn tại.
8. Bấm nguyên liệu trên card mở modal đúng item.
9. Bấm nguyên liệu trong nội dung công thức/cảnh giới khi modal đang mở thay nội dung modal đúng item.
10. Tất cả nguyên liệu của mọi kết quả trên trang đều có target trong `referenceItems`.
11. Chạy toàn bộ Vitest, ESLint và production build.

## Tiêu chí nghiệm thu

- Không còn link hoặc trang `/characters`.
- Có trang `/tu-tien-crafting` dành riêng cho đồ Hàn Lập có thể tạo.
- Không hiển thị món không có cách tạo xác thực hoặc không có công dụng xác thực.
- Không hiển thị công thức độc quyền của nhân vật khác.
- Thân Ngoại Hoá Thân và Thiên Cơ Ốc được xử lý như ví dụ bình thường của quy tắc dữ liệu, không bằng ngoại lệ hard-code.
- Mọi nguyên liệu công thức đều bấm được và mở modal chi tiết đúng item, kể cả trong phần liên quan đến cảnh giới tu tiên.
- Test, lint và build đều thành công.

## Ngoài phạm vi

- Không làm lại toàn bộ giao diện hoặc design system.
- Không xóa entity nhân vật khỏi dữ liệu thô.
- Không thêm lựa chọn nhân vật khác ngoài Hàn Lập trong phiên bản này.
- Không hiển thị prefab nội bộ chỉ để tăng số lượng kết quả.
