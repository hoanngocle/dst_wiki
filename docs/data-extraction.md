# Làm mới catalog dữ liệu DST Tu Tiên

Tài liệu này là runbook cho pipeline offline `static extractor -> runtime extractor -> SQLite có provenance -> JSON tìm kiếm`. Chạy mọi lệnh từ thư mục gốc repository với Python 3.9+; extractor chỉ dùng standard library.

## Nguồn dữ liệu và nguyên tắc

- `mod/3721846643` là mod nội dung Tu Tiên, hiện tại version `18.0.10`.
- `mod/3721859355` là bản dịch Tu Tiên, hiện tại version `1.0.11`.
- `mod/3731181944` là bản dịch DST gốc, hiện tại version `2026.1.3`.
- Không sửa ba thư mục mod trên. Nếu cần cập nhật, thay cả bản tải riêng rồi chạy lại toàn bộ pipeline.
- Chỉ nhập prefab `base_game` khi có fact Tu Tiên yêu cầu nó; không nhập toàn bộ catalog DST.
- **Nghiêm cấm crawl, scrape hoặc nhập dữ liệu từ wiki/website vào dataset này.** Nguồn hợp lệ chỉ là ba mod cục bộ, archive game đã snapshot và runtime probe cục bộ.

Kiểm tra version trước mỗi lần refresh:

```bash
rg -n '^version[[:space:]]*=' \
  mod/3721846643/modinfo.lua \
  mod/3721859355/modinfo.lua \
  mod/3731181944/modinfo.lua
```

Nếu version Tu Tiên thay đổi, phải snapshot lại source game phù hợp và chạy runtime probe mới. Không tái sử dụng `data/raw/runtime.json` của version khác.

## 1. Snapshot source game

Extractor không đọc trực tiếp archive trong thư mục cài game. Lệnh sau copy **nguyên file** `scripts.zip` và `images.zip` vào workspace, kiểm tra size/SHA-256 của bản nguồn với bản copy, rồi ghi `data/sources/game/manifest.json`:

```bash
GAME_CONTENTS="/Users/nyx/Library/Application Support/Steam/steamapps/common/Don't Starve Together/dontstarve_steam.app/Contents"

python3 -m tools.extract.cli snapshot-game \
  --game-data "$GAME_CONTENTS/data" \
  --destination data/sources/game
```

`--game-data` là bắt buộc và phải trỏ tới thư mục chứa `databundles/`. `--destination` mặc định là `data/sources/game`. Hai ZIP là local-only theo `.gitignore`; manifest size/checksum được version-control. Không sửa hoặc giải nén rồi đóng gói lại ZIP snapshot.

## 2. Runtime probe có phê duyệt rõ ràng

`all` **không tự chạy runtime probe**. Probe cần quyền ghi tạm vào thư mục `mods` của bản game đã cài và khởi chạy dedicated server, vì vậy operator phải xin/chấp nhận quyền ghi đó một cách rõ ràng trước khi chạy.

```bash
WORKSPACE="$(pwd -P)"
GAME_CONTENTS="/Users/nyx/Library/Application Support/Steam/steamapps/common/Don't Starve Together/dontstarve_steam.app/Contents"

python3 -m tools.extract.cli run-runtime \
  --server-bin "$GAME_CONTENTS/MacOS/dontstarve_dedicated_server_nullrenderer" \
  --game-mods-dir "$GAME_CONTENTS/mods" \
  --workspace "$WORKSPACE" \
  --timeout 180
```

Các argument `--server-bin` và `--game-mods-dir` là bắt buộc. `--workspace` mặc định là `.` nhưng nên truyền đường dẫn tuyệt đối như trên; `--timeout` mặc định là 180 giây.

Runner tạo hai bản copy mod có tên ngẫu nhiên trong `--game-mods-dir`, từ chối ghi đè thư mục đã tồn tại và xóa đúng hai bản copy này trong `finally`. Dedicated server luôn nhận `-persistent_storage_root` là `data/runtime/probe-<run-id>` nằm dưới workspace. Đây là cluster offline/isolated mới; runner không mở hoặc ghi vào save thật. Log và world thử nghiệm nằm trong `data/runtime/` (local-only). Output hợp lệ được thay atomically vào `data/raw/runtime.json` (local-only).

Probe dừng với lỗi nếu dedicated server thoát trước sentinel, quá timeout, không tạo đúng một `runtime.json`, hoặc JSON sai schema. Các lỗi inspect/spawn từng prefab bên trong một run thành công không làm mất toàn bộ run; chúng được giữ làm extraction error để hiện trong coverage.

## 3. Chạy pipeline offline

Sau khi có snapshot và `data/raw/runtime.json` đúng version:

```bash
python3 -m tools.extract.cli all
```

`all` dùng các default sau và chạy tuần tự:

1. `extract-static`: `mod/3721846643`, `mod/3721859355/modmain.lua`, `mod/3731181944/viethoa.po` -> `data/raw/mod_static.json`.
2. `import-runtime`: validate `data/raw/runtime.json`; không khởi chạy server.
3. `enrich-base`: đọc bản copy `data/sources/game/scripts.zip`, `images.zip` và manifest -> `data/raw/base_game.json`.
4. `build-db`: normalize ba raw bundle -> `data/generated/wiki.sqlite`.
5. `export`: -> `public/data/catalog.json` và `public/data/assets.json`.
6. `validate`: -> `data/generated/coverage.json`.

Các stage có thể chạy riêng; xem argument/default chính xác bằng `python3 -m tools.extract.cli <stage> --help`. Khi refresh chính thức, luôn chạy `all` để tránh trộn output cũ và mới.

## 4. Đọc lỗi và coverage

`python3 -m tools.extract.cli validate` trả exit code khác 0 nếu có hard failure. `data/generated/coverage.json` là nguồn chẩn đoán chính:

- `unresolved_dependencies`: ID được Tu Tiên tham chiếu nhưng không resolve trong registry/prefab/recipe/string của `scripts.zip`. Đây là hard failure; kiểm tra version runtime/snapshot và evidence locator, không tạo entity giả.
- `foreign_key_errors`: ingredient/source/relation không resolve entity. Đây là hard failure.
- `archive_checksum_errors`: ZIP thực tế, manifest và SHA lưu trong database không khớp. Đây là hard failure; snapshot lại nguyên archive.
- `wiki_urls`: URL phát hiện trong source/evidence/manifest. Đây là hard failure vì dataset cấm nguồn web.
- `conflicts`: nhiều fact khác nhau cho cùng field. Normalizer vẫn chọn giá trị theo ưu tiên source/confidence, giữ mọi candidate và đánh dấu evidence thắng; conflict là warning cần review, không bị ghi đè im lặng.
- `runtime_errors`: lỗi probe theo prefab/locator. Chúng vẫn hiện cả khi pipeline có thể hoàn tất; review trước khi coi field liên quan là đầy đủ.
- `low_confidence_fields`: evidence có confidence `< 0.7`, gồm record/source/locator và trạng thái `selected`. Đây là danh sách cần manual review, đồng thời sinh warning `low_confidence_fields_present`.
- `coverage` và warning `optional_coverage_incomplete`: tỷ lệ entity có tên Việt, icon, recipe, acquisition và stats. Thiếu field tùy chọn là warning, không phải lý do tạo dữ liệu suy đoán.

`extraction_errors` chứa toàn bộ lỗi parser/probe; `warnings` tóm tắt coverage thiếu, extraction errors, conflicts và low-confidence fields. Chỉ `hard_failures` quyết định exit code của `validate`/`all`.

## 5. Artefact được tạo

- `data/generated/wiki.sqlite`: database chuẩn hóa có entities, recipes, ingredients, acquisition, stats/effects/relations/assets, evidence, conflicts và extraction errors. Đây là nguồn audit/provenance đầy đủ.
- `public/data/catalog.json`: JSON entity đã nest, sắp xếp ổn định; là input chính cho tìm kiếm và trang chi tiết của wiki tương lai.
- `public/data/assets.json`: asset map và provenance cho icon/atlas; là input asset của wiki tương lai.
- `data/generated/coverage.json`: quality gate và danh sách việc cần review; không phải payload hiển thị chính.
- `data/raw/mod_static.json`, `data/raw/runtime.json`, `data/raw/base_game.json`: raw facts để tái hiện normalize. Runtime JSON, source ZIP và `data/runtime/` là local-only.

## 6. Kiểm tra trước khi bàn giao

```bash
python3 -m unittest discover -s tests/extract -v
python3 -m tools.extract.cli validate
sqlite3 data/generated/wiki.sqlite \
  'select namespace, count(*) from entities group by namespace order by namespace;'
sqlite3 data/generated/wiki.sqlite \
  'select count(*) from evidence where selected = 1;'
sqlite3 data/generated/wiki.sqlite 'pragma foreign_key_check;'
git diff --check
```

Kết quả hợp lệ phải có cả `base_game` và `tu_tien`, selected evidence lớn hơn 0, foreign-key check không in dòng nào, `hard_failures` rỗng và `git diff --check` im lặng. Trước khi ký duyệt, còn phải xác nhận mọi base-game entity có `requested_by`/root evidence từ Tu Tiên, mọi ingredient resolve, không có URL HTTP trong source/evidence/manifest, checksum/size archive khớp manifest, và ba thư mục mod giống byte-for-byte với bản tải gốc.
