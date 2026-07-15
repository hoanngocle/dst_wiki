# Thiết kế lọc item Tu Tiên và bổ sung ghi chú chế tạo

**Ngày:** 2026-07-15  
**Trạng thái:** Đã thống nhất thiết kế hội thoại, chờ duyệt đặc tả

## Mục tiêu

Làm sạch danh sách Tu Tiên được công bố cho frontend và tận dụng các chuỗi
`STRINGS.RECIPE_DESC.*` đã lưu trong SQLite để bổ sung ngữ cảnh chế tạo cho
item. Công thức nguyên liệu chỉ được hiển thị khi có dữ liệu runtime; hệ thống
không suy đoán nguyên liệu từ văn bản mô tả.

## Phạm vi dữ liệu

- SQLite tiếp tục giữ nguyên toàn bộ 647 entity Tu Tiên để phục vụ kiểm tra và
  truy nguyên nguồn.
- `public/data/items.json` chỉ công bố entity Tu Tiên có `name.vi` là chuỗi
  không rỗng. Theo snapshot hiện tại, danh sách Tu Tiên giảm từ 647 xuống 381.
- Không dùng blacklist theo mẫu tên như `*_items`. Các prefab kỹ thuật như
  `xd_items`, `xd_danyao_items`, `xd_itemskin_prefabs`, `xd_luoshen_items` và
  `xd_tianji_items` bị loại vì không có tên tiếng Việt. Cách này tránh loại nhầm
  prefab hợp lệ có chữ `item` trong ID.
- Quy tắc lọc không áp dụng cho namespace `base_game`; invariant một entry cho
  mỗi module prefab DST gốc vẫn được giữ nguyên.

## Ghép ghi chú chế tạo

Trong bước `export`, đọc các hàng `game_text` có khóa
`STRINGS.RECIPE_DESC.<PREFAB_ID>`. Phần sau tiền tố được chuẩn hóa chữ hoa/thường
và ghép chính xác với `entities.prefab_id` trong namespace `tu_tien`.

Các hàng cùng `text_key` được nhóm trước khi ghép:

- Nếu mọi hàng có cùng `value_vi`, xuất một ghi chú duy nhất và tiếp tục giữ
  mọi hàng nguồn trong SQLite.
- Nếu cùng khóa nhưng có nhiều `value_vi` khác nhau, dừng export với lỗi xung
  đột có tên khóa; không tự chọn theo thứ tự file.

Snapshot hiện tại có 106 hàng `RECIPE_DESC` nhưng chỉ 105 khóa duy nhất. Khóa
`STRINGS.RECIPE_DESC.XD_SJ_TLSQ` xuất hiện tại dòng 1075 và 1079 với cùng nội
dung, nên tạo đúng một ghi chú.

## Hợp đồng item

Nâng schema `items.json` từ version 2 lên version 3. Mỗi item có thêm trường:

```json
{
  "craftingNote": "Mô tả trong menu chế tạo hoặc null"
}
```

`craftingNote` là chuỗi tiếng Việt không rỗng hoặc `null`. Trường hiện tại
`description` được giữ nguyên; ghi chú chế tạo không ghi đè lời mô tả quan sát
hoặc mô tả nhân vật.

Frontend parser phải kiểm tra trường mới. Tìm kiếm bao gồm `craftingNote` để
người dùng có thể tìm item bằng công dụng được mô tả trong menu chế tạo.

## Trình bày trong chi tiết item

- Item có công thức runtime: giữ khối **Công thức** với nguyên liệu và số lượng
  thật; nếu có `craftingNote`, hiển thị ghi chú trong cùng khối.
- Item không có công thức runtime nhưng có `craftingNote`: hiển thị khối
  **Cách tạo / ghi chú chế tạo** chỉ chứa văn bản.
- Item không có cả hai: không hiển thị khối chế tạo.

Theo snapshot hiện tại, sau khi lọc tên Việt có 104 item chứa công thức runtime,
105 item ghép được ghi chú chế tạo và 7 item chỉ có ghi chú mà không có công
thức nguyên liệu runtime.

## Luồng xử lý

1. `build-db` tiếp tục thu thập toàn bộ `game_text` và entity như hiện tại.
2. `export` đọc SQLite, dựng lookup ghi chú chế tạo đã kiểm tra xung đột.
3. Item exporter lọc Tu Tiên theo `name.vi`, ghép `craftingNote`, dựng công thức
   runtime và xuất schema version 3.
4. Frontend parser xác thực payload; tìm kiếm và modal sử dụng trường mới.

Việc lọc chỉ xảy ra ở hợp đồng công bố cho frontend, không xóa dữ liệu thô,
entity, source hoặc evidence trong SQLite/catalog kiểm toán.

## Xử lý lỗi và tính xác định

- Database thiếu bảng `game_text` hoặc truy vấn thất bại làm lệnh export thất
  bại rõ ràng.
- Khóa `RECIPE_DESC` trùng nhưng khác nội dung làm export thất bại.
- Khóa không ghép được với prefab vẫn được giữ trong SQLite nhưng không tạo item
  giả.
- Danh sách item và lookup ghi chú được sắp xếp ổn định; chạy export lặp lại tạo
  byte output giống nhau.
- Việc lọc Tu Tiên không được làm thay đổi tập prefab `base_game` mà validator
  đang kiểm tra.

## Kiểm thử

Triển khai theo TDD, bao gồm:

1. Item Tu Tiên thiếu tên Việt bị loại; item có tên Việt được giữ.
2. Prefab kỹ thuật như `xd_items` bị loại bởi cùng quy tắc dữ liệu, không cần
   blacklist.
3. Item base game không tên Việt vẫn được giữ theo hợp đồng hiện hành.
4. `RECIPE_DESC` ghép chính xác, không ghép gần đúng hoặc theo substring.
5. Hai hàng cùng khóa/cùng nội dung tạo một `craftingNote`.
6. Hai hàng cùng khóa/khác nội dung làm export thất bại.
7. Parser chấp nhận schema version 3 và từ chối payload thiếu hoặc sai kiểu
   `craftingNote`.
8. Tìm kiếm khớp nội dung `craftingNote`.
9. Modal hiển thị ghi chú đúng với item có và không có công thức runtime.
10. Full extractor, frontend tests, typecheck/lint và validator đều vượt qua.

## Ngoài phạm vi

- Không suy đoán nguyên liệu hoặc số lượng từ câu văn.
- Không gắn lời thoại nhân vật vào item trong thay đổi này.
- Không xóa entity khỏi SQLite hoặc catalog kiểm toán.
- Không đổi nội dung bản dịch tiếng Việt gốc.
