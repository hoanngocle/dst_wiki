# Tu Tiên Game-Facing Text Export Design

## Mục tiêu

Xuất toàn bộ text hiển thị cho người chơi của mod Tu Tiên thành Markdown
tiếng Việt, trong đó mọi công thức đã đăng ký lúc chạy game được viết lại theo
dạng dễ đọc. Lời thoại nhân vật chuyên biệt không thuộc lần xuất này vì sẽ
được gắn với trang nhân vật ở giai đoạn sau.

## Phạm vi dữ liệu

- `data/raw/runtime.json` là nguồn chính xác cho công thức đang hiển thị trong
  game. Nó chứa 112 công thức của mod phiên bản 18.0.10.
- `public/data/catalog.json` cung cấp tên và mô tả Việt hoá cho đầu ra lẫn
  nguyên liệu, kể cả dependency của game gốc.
- Các gán `STRINGS.*` trong `mod/3721846643` và `mod/3721859355` cung cấp text
  UI, thao tác, trạng thái và thông báo. Các file `scripts/speech_*.lua` bị
  loại trừ có chủ đích.
- `modinfo.lua` được trích các nhãn và lựa chọn cấu hình hiển thị trong game.

`scripts/main/recipes.lua` không được parse trực tiếp vì đây là dữ liệu nhị
phân/đã bảo vệ; không suy đoán công thức từ file đó.

## Đầu ra

Thư mục `docs/mod-text/` có ba file tái lập được:

1. `README.md` — phiên bản nguồn, phạm vi, số lượng và giới hạn.
2. `crafting-recipes.md` — mỗi công thức gồm ID, công thức toán học, diễn giải
   tiếng Việt, điều kiện công nghệ/nhân vật và mô tả vật phẩm khi có.
3. `game-text.md` — toàn bộ chuỗi `STRINGS.*` trực tiếp và chuỗi trong bảng
   `STRINGS.*`, cùng nhãn cấu hình `modinfo.lua`, có key và locator nguồn.

## Quy tắc diễn giải công thức

- Thành phần được ghi theo thứ tự game đã đăng ký: `a × A + b × B → c × C`.
- Tên Việt có ưu tiên; khi không có, dùng tên Anh rồi tới prefab ID để không
  làm mất dữ liệu.
- `NONE`, `SCIENCE_ONE`, `SCIENCE_TWO` và `LOST` được giữ nguyên mã game trong
  trường điều kiện, không tự gán sai tên trạm.
- Chi phí nhân vật được dịch rõ: `decrease_health` là giảm máu,
  `decrease_sanity` là giảm tỉnh táo; chi phí 0 không hiển thị.
- Builder tag được hiển thị vừa dưới dạng tên nhân vật nếu resolve được, vừa
  kèm ID kỹ thuật.

## Kiểm chứng

Generator cần deterministic: chạy hai lần trên cùng input phải cho byte giống
nhau. Test fixture phải chứng minh công thức, fallback tên và chuỗi bảng được
render; lần xuất thật được kiểm tra về số lượng công thức và sự vắng mặt của
speech source.
