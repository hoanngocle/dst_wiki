# Game-Facing Text Database Design

## Mục tiêu

Lưu 1.010 chuỗi game-facing đã xuất của Tu Tiên vào `data/generated/wiki.sqlite`
theo dạng có thể truy vấn, tái lập và truy nguyên nguồn. Công thức, tên và mô
tả item hiện đã ở các bảng `recipes`, `recipe_ingredients` và `entities`; thay
đổi này chỉ xử lý text UI/thông báo chưa có chỗ lưu.

## Schema

Thêm bảng `game_text`:

| Cột | Ý nghĩa |
| --- | --- |
| `text_id` | Khóa chính SHA-256 ổn định từ source, key và locator. |
| `text_key` | Key Lua đầy đủ, ví dụ `STRINGS.XD_USE_INVENTORY.OPEN`. |
| `value_vi` | Chuỗi Việt hoá hiển thị trong game. |
| `source_id` | FK tới `sources`; mỗi file input có hash và version riêng. |
| `locator` | `line:<n>` trong file nguồn. |

`UNIQUE(source_id, text_key, locator)` bảo vệ một lần build không sinh dòng
trùng. Bảng không có FK tới `entities`: đa số key UI, thông báo và lựa chọn
cấu hình không thuộc một prefab duy nhất.

## Luồng dữ liệu

1. Một collector dùng cùng parser hiện đang xuất Markdown để đọc Lua UTF-8 có
   `STRINGS` và `modinfo.lua`; bỏ qua Lua bytecode và `scripts/speech_*.lua`.
2. Collector trả về record text cùng source metadata/hash theo file; không
   parse ngược Markdown.
3. `build-db` ghép source collector với catalog chuẩn hoá, rồi ghi schema và
   `game_text` trong cùng transaction/atomic replace của SQLite.
4. `export-markdown` dùng chính collector, bảo đảm DB và Markdown luôn có cùng
   tập text.

## Kiểm chứng

- Unit test parser/collector bao phủ key trực tiếp, bảng lồng nhau, mảng và
  loại bỏ bytecode/lời thoại.
- Database test xác nhận row `game_text`, FK source và tính deterministic.
- Build thực kiểm tra 1.010 record, không có locator từ `speech_*.lua`, và
  `PRAGMA foreign_key_check` sạch.
