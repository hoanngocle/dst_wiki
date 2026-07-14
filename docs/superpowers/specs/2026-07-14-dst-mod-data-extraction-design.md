# DST Tu Tiên Data Extraction Design

## Mục tiêu

Xây dựng pipeline có thể tái chạy để thu toàn bộ dữ liệu hữu ích của mod Tu Tiên `3721846643`, bổ sung đúng những prefab DST gốc mà mod tham chiếu, ghi dữ liệu chuẩn hóa vào SQLite kèm provenance, rồi xuất JSON phục vụ tìm kiếm. Giao diện wiki không thuộc phạm vi của thiết kế này.

## Phạm vi

Pipeline phải thu được:

- Thực thể mod: item, vật liệu, công trình, sinh vật, nhân vật, kỹ năng và vật thể liên quan.
- Tên/mô tả tiếng Việt từ mod Tu Tiên và hai mod ngôn ngữ.
- Công thức, nguyên liệu, số lượng, trạm chế tạo và điều kiện mở khóa.
- Nguồn nhận: chế tạo, loot, thu hoạch, trade/shop, world spawn, quà khởi đầu và tiến trình đặc biệt.
- Chỉ số/effect phổ biến: damage, armor, durability, food values, cooldown, buff/debuff và thời lượng.
- Icon inventory, atlas metadata và 39 trang Tu Tiên Mật Quyển.
- Mọi prefab DST gốc được mod tham chiếu, gắn namespace `base_game` và được làm giàu từ source game.

Không thu toàn bộ DST nếu một prefab không liên quan tới mod. Không crawler wiki hoặc dùng nội dung wiki làm nguồn dữ liệu.

## Ràng buộc nguồn

- `mod/3721846643` là nguồn mod nội dung; không sửa các file trong thư mục này.
- `mod/3721859355` và `mod/3731181944` chỉ là nguồn dịch/alias.
- File game cần dùng phải được copy nguyên file vào `data/sources/game/` trước khi extractor đọc.
- Hai archive game tối thiểu là `scripts.zip` và `images.zip`; bản copy phải có SHA-256, kích thước và thời gian copy trong manifest.
- Runtime probe dùng dedicated server trong world thử nghiệm, với persistent storage đặt trong workspace. Không dùng save game thật.
- Mỗi giá trị trong database phải chỉ ra nguồn tĩnh, nguồn runtime hoặc ghi chú xác minh thủ công.

## Kiến trúc

```text
mod/* -----------------------+
                              +--> raw facts --> normalizer --> wiki.sqlite --> catalog.json
copied scripts.zip/images.zip +        ^              |               |
                                       |              +--> QA report  +--> asset map
dedicated-server runtime probe --------+
```

Pipeline viết bằng Python 3.9 standard library để không phụ thuộc dịch vụ ngoài. Runtime probe là một mod Lua nhỏ và một runner Python điều khiển dedicated server. Các parser chỉ tạo raw facts; normalizer là nơi duy nhất gộp nguồn, phân namespace và ghi database.

## Bố cục file

```text
tools/extract/
  contracts.py          # TypedDict/dataclass dùng chung cho raw facts
  source_manifest.py    # Copy/verify archive game
  lua_strings.py        # Parse STRINGS.NAMES, DESCRIBE, RECIPE_DESC
  mod_static.py         # Inventory mod entities, assets và literal references
  base_game.py          # Enrich dependency từ scripts.zip/images.zip
  runtime_import.py     # Validate/import output của runtime probe
  normalize.py          # Merge facts và tính confidence
  database.py           # Schema SQLite và deterministic writes
  export_json.py        # JSON phục vụ tìm kiếm
  validate.py           # Referential integrity và coverage report
  cli.py                # Entry point cho từng stage và full pipeline

tools/runtime_mod/
  modinfo.lua
  modmain.lua
  scripts/exporter.lua  # Recipes, prefab components, loot và provenance runtime

tests/extract/
  fixtures/             # Lua/JSON/ZIP nhỏ, không dùng archive game thật
  test_*.py

data/sources/game/
  scripts.zip           # Local-only source archive
  images.zip            # Local-only source archive
  manifest.json         # Tracked metadata/checksum

data/raw/
  mod_static.json
  base_game.json
  runtime.json

data/generated/
  wiki.sqlite
  coverage.json

public/data/
  catalog.json
  assets.json
```

Archive nguồn và output runtime dung lượng lớn là local-only; manifest, schema, extractor, test và output công bố cho frontend được version-control.

## Mô hình dữ liệu

### `sources`

Lưu `source_id`, loại nguồn, đường dẫn tương đối, version, SHA-256 và metadata. Các loại nguồn là `mod_static`, `mod_translation`, `base_game_source`, `runtime_probe`, `handbook_image` và `manual_review`.

### `entities`

Khóa chính là cặp `(namespace, prefab_id)`, trong đó namespace là `tu_tien` hoặc `base_game`. Trường chính: loại thực thể, tên Việt/Anh, mô tả Việt/Anh, item flag, icon key và confidence tổng hợp.

### Quan hệ

- `recipes` và `recipe_ingredients` cho crafting.
- `acquisition_sources` cho craft/drop/harvest/trade/world/start/progression.
- `stats` cho giá trị dạng key/value/unit.
- `effects` cho trigger, effect, value và duration.
- `entity_relations` cho spawn, upgrade, transforms và produces.
- `evidence` nối từng record nghiệp vụ với source, locator, raw value và confidence.

Không lưu danh sách nguyên liệu hay nguồn nhận dưới dạng chuỗi ghép; mọi quan hệ phải có foreign key tới `entities`.

## Quy tắc nhận diện dependency DST gốc

1. Mọi prefab có prefix `xd_` hoặc được khai báo trong registry runtime của mod thuộc `tu_tien`.
2. Mọi ID xuất hiện trong ingredient, loot, spawn, trade hoặc relation của Tu Tiên nhưng không nằm trong registry mod trở thành dependency candidate.
3. Candidate chỉ được gắn `base_game` khi tồn tại trong recipe/prefab/string registry của bản `scripts.zip` đã copy.
4. Candidate không resolve được vẫn được giữ trong coverage report, không âm thầm tạo entity giả.
5. Enrichment chạy theo closure: nếu công thức base item được chọn để hiển thị thì nguyên liệu của công thức đó được thêm làm reference tối thiểu, nhưng không tiếp tục mở rộng vô hạn.

## Static extraction

Static extractor đọc `strings.lua`, inventory atlas XML, tên file prefab/asset và mod metadata. Nó phải xử lý assignment trực tiếp, string escape, alias tới STRINGS gốc và các table-loop đơn giản. Raw fact giữ nguyên file và line locator.

Vì phần lớn Lua Tu Tiên bị đóng gói, static output được xem là baseline chứ không phải dữ liệu hoàn chỉnh.

## Runtime extraction

Runtime probe chạy sau khi Tu Tiên đăng ký prefab/recipe. Probe:

- Enumerate `AllRecipes` để xuất product, ingredients, tech, filters và builder restrictions.
- Enumerate prefab registry; spawn trong `pcall` ở world thử nghiệm để đọc component values.
- Đọc lootdropper tables, pickable products, trader data và các component phổ biến.
- Ghi lỗi spawn/inspection theo từng prefab thay vì dừng toàn pipeline.
- Xuất JSON có schema version và sentinel trong log để runner biết đã hoàn thành.

Probe không gọi combat, không sinh world thật và không ghi vào mod source.

## Base-game enrichment

Base extractor chỉ đọc bản copy `scripts.zip`/`images.zip`. Nó xây index tên file và identifier một lần, sau đó xử lý tập dependency candidate:

- Tên/mô tả Anh từ `scripts/strings.lua`.
- Tên/mô tả Việt từ `mod/3731181944/viethoa.po` nếu có key tương ứng.
- Công thức từ `scripts/recipes.lua`.
- Common stats và acquisition evidence từ prefab source.
- Icon atlas entry từ năm inventory atlas trong `images.zip`.

Runtime values được ưu tiên cho số đã evaluate; source expression vẫn được giữ làm evidence.

## Merge, precedence và confidence

Thứ tự ưu tiên cho cùng một trường:

1. Giá trị runtime đúng version hiện tại.
2. Literal source cùng version.
3. Bản dịch mod.
4. Manual review.

Mâu thuẫn không bị ghi đè im lặng. Normalizer chọn giá trị thắng, đồng thời giữ tất cả evidence và thêm conflict vào `coverage.json`.

Confidence:

- `1.0`: exact runtime registry hoặc literal assignment trực tiếp.
- `0.9`: parsed common source pattern có locator.
- `0.7`: suy luận từ filename/atlas/quan hệ.
- `0.5`: alias hoặc ghi chú cần xác minh.

## Output và tính tái lập

- SQLite bật foreign keys và ghi theo thứ tự ổn định.
- JSON sắp theo `(namespace, prefab_id)` và không chứa timestamp biến động.
- `coverage.json` báo số entity, tỷ lệ có tên/icon/recipe/acquisition/stats, unresolved dependency, runtime errors và conflicts.
- Chạy lại với cùng input checksum phải sinh JSON giống byte-for-byte và SQLite có cùng tập record.

## Kiểm thử và tiêu chí hoàn thành

- Unit test parser bằng fixture nhỏ có assignment, alias, recipe, loot và malformed input.
- Integration test tạo archive game giả, raw runtime giả, SQLite và JSON hoàn chỉnh.
- Foreign-key check phải sạch.
- Mọi ingredient/source/relation phải resolve entity.
- Mọi entity `tu_tien` inventory phải có tên Việt hoặc xuất hiện trong missing-name report.
- Mọi dependency `base_game` phải có evidence chứng minh nó được Tu Tiên tham chiếu.
- Không có URL wiki hoặc dữ liệu crawler trong source manifest/evidence.

## Ngoài phạm vi

- Thiết kế hoặc triển khai giao diện wiki.
- Crawl/scrape bất kỳ website nào.
- Dịch lại toàn bộ DST.
- Reverse-engineer thủ công mọi file Lua đã đóng gói nếu runtime registry đã cung cấp đủ dữ liệu.
