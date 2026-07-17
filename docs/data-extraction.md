# Làm mới catalog dữ liệu DST Tu Tiên

Tài liệu này là runbook cho pipeline offline `static extractor -> runtime extractor -> SQLite có provenance -> import Wiki chọn lọc -> JSON tìm kiếm`. Chạy mọi lệnh từ thư mục gốc repository với Python 3.9+; extractor chỉ dùng standard library.

## Nguồn dữ liệu và nguyên tắc

- `mod/3721846643` là mod nội dung Tu Tiên, hiện tại version `18.0.10`.
- `mod/3721859355` là bản dịch Tu Tiên, hiện tại version `1.0.11`.
- `mod/3731181944` là bản dịch DST gốc, hiện tại version `2026.1.3`.
- Không sửa ba thư mục mod trên. Nếu cần cập nhật, thay cả bản tải riêng rồi chạy lại toàn bộ pipeline.
- Nhập đúng một prefab `base_game` cho mỗi file `.lua` trực tiếp dưới `scripts/prefabs/`; ID là tên file bỏ đuôi và chuyển lowercase. Không mở rộng các lời gọi `Prefab(...)` phụ trong cùng file.
- Entity base-game phụ thuộc vẫn nằm trong audit database với type `dependency`. Dependency inventory chỉ được xuất như item DST khi một công thức đã publish tham chiếu tới nó, để mọi nguyên liệu trong modal có ID resolve được; dependency không được tham chiếu vẫn không xuất hiện trong payload tìm kiếm.
- Fact game canonical chỉ lấy từ ba mod cục bộ, archive game đã snapshot và runtime probe cục bộ. Crawl chọn lọc `dontstarve.wiki.gg` được lưu trong các bảng `wiki_*` riêng để bổ sung bài viết, ảnh và công thức; dữ liệu Wiki không được ghi đè fact game có confidence cao hơn.

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

Probe hiện ghi **runtime schema version 2** với các khóa bắt buộc `schema_version`, `mod_version`, `targets`, `recipes`, `prefabs`, `coverage` và `errors`. Probe dừng với lỗi nếu dedicated server thoát trước sentinel, quá timeout, không tạo đúng một `runtime.json`, hoặc JSON sai schema. Các lỗi inspect/spawn từng prefab bên trong một run thành công không làm mất toàn bộ run; chúng được giữ làm extraction error để hiện trong coverage.

Importer yêu cầu một coverage row cho mỗi cặp `target × category` của chín category: `buff_debuff`, `cooldown_recharge`, `craft`, `drop`, `harvest`, `progression`, `start_gift`, `trade_shop`, `world_spawn`. Trạng thái có ba giá trị:

- `observed`: probe thu được fact cụ thể và giữ evidence của quan sát đó.
- `unobserved`: probe hỗ trợ kiểm tra category nhưng không thấy dữ liệu ở prefab/run hiện tại; đây không phải bằng chứng rằng cơ chế không tồn tại ở mọi trạng thái game.
- `unsupported`: probe không có reverse registry hoặc cách quan sát an toàn/chính xác cho category đó. Giá trị này biểu thị giới hạn extractor, **không** có nghĩa item chắc chắn không có cơ chế tương ứng.

## 3. Chạy pipeline offline

Sau khi có snapshot và `data/raw/runtime.json` đúng version:

```bash
python3 -m tools.extract.cli all \
  --static data/raw/mod_static.json
```

`import-runtime`, `enrich-base`, `build-db` và `all` đều có hai hard gate lấy từ static bundle: `runtime.mod_version` phải khớp chính xác, đồng thời `runtime.targets` phải chứa toàn bộ tập entity `tu_tien` static đã sắp xếp. Sai version hoặc thiếu dù chỉ một static target sẽ dừng pipeline trước normalize/downstream write; không sửa tay capture hoặc tái sử dụng capture cũ. `--static` của `all` mặc định là `data/raw/mod_static.json`, nên lệnh ngắn `python3 -m tools.extract.cli all` vẫn giữ nguyên hành vi.

`all` dùng các default sau và chạy tuần tự:

1. `extract-static`: `mod/3721846643`, `mod/3721859355/modmain.lua`, `mod/3731181944/viethoa.po` -> `data/raw/mod_static.json`.
2. `import-runtime`: validate `data/raw/runtime.json`; không khởi chạy server.
3. `enrich-base`: đọc bản copy `data/sources/game/scripts.zip`, `images.zip` và manifest; phân loại toàn bộ module prefab thành `item`, `mob`, `boss`, `character`, `structure`, `effect` hoặc `other` -> `data/raw/base_game.json`.
4. `build-db`: normalize ba raw bundle -> `data/generated/wiki.sqlite`.
5. `import-wiki`: validate manifest/checksum và import `data/crawled/dontstarve-items` vào các bảng `wiki_*` trong SQLite.
6. `export`: -> `public/data/catalog.json`, `public/data/assets.json`, `public/data/items.json`, `public/data/wiki/pages`, `public/assets/wiki` và `data/generated/item-textures.json`.
7. `validate`: -> `data/generated/coverage.json`.

Các stage có thể chạy riêng; xem argument/default chính xác bằng `python3 -m tools.extract.cli <stage> --help`. Khi refresh chính thức, luôn chạy `all` để tránh trộn output cũ và mới.

Nếu database game đã có sẵn và chỉ muốn nạp lại crawl Wiki:

```bash
python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export
```

`import-wiki` mặc định đọc `data/crawled/dontstarve-items` và cập nhật transactionally các bảng Wiki trong `data/generated/wiki.sqlite`. Chạy lại cùng manifest không nhân đôi record. Import báo số page, recipe, ingredient, image, mapping và page chưa map; lỗi checksum/foreign key không làm mất batch thành công trước đó.

### Làm mới và duyệt dữ liệu Công trình

Khi crawl Wiki và database game/mod đã sẵn sàng, chạy đúng vòng đời sau để tái tạo phần Công trình cho cả DST và Tu Tiên:

```bash
python3 -m tools.extract.cli import-wiki
python3 -m tools.extract.cli export
python3 -m tools.extract.cli validate
jq '.summary, .rows[] | select(.action != "keep")' \
  data/generated/structure-icon-audit.json
```

Mỗi công trình publish phải có `structureDetails` gồm nguồn xuất hiện, công thức xây dựng, công dụng, toàn bộ vật phẩm chế tạo tại công trình, phá huỷ/thu hồi và visual. Wiki là provenance/bài viết, không còn là group hiển thị: record Wiki hợp lệ được publish trong nhóm DST; Tu Tiên giữ namespace riêng.

`data/generated/structure-icon-audit.json` ghi đúng một row cho mỗi công trình vốn không có inventory icon trước khi resolve:

- `natural_structure`: công trình thật tự sinh trong thế giới, không thể chế tạo; giữ lại và hiển thị ghi chú rõ ràng.
- `craftable_wiki_visual`: công trình chế tạo được, không có inventory icon local nhưng đã resolve đúng ảnh Wiki; giữ lại.
- `world_asset_only`: công trình thật chỉ có world/map asset phù hợp; giữ lại với lý do và evidence.
- `technical_prefab`: wrapper, spawner, helper, FX hoặc prefab kỹ thuật; loại khỏi payload công khai nhưng giữ nguyên raw row, SQLite provenance và audit evidence.
- `unverified`: lookup một lượt không xác lập được identity chính xác; loại khỏi payload công khai, không đoán dữ liệu.

Action `repair` phải về 0 trước khi bàn giao. Visual ưu tiên inventory/build icon, sau đó ảnh Wiki chính xác, cuối cùng world/map asset xác minh được; pipeline không tạo ảnh giả hoặc dùng texture không liên quan. Công trình tự sinh hợp lệ có thể không có inventory icon, vì vậy trường hợp này không phải lỗi nếu audit, origin note và visual status thống nhất.

`all` không gọi decoder ảnh ngoài. Sau khi refresh JSON, publish các texture web bằng một bản `ktech` đã được review và cài rõ ràng:

```bash
python3 -m tools.extract.cli publish-assets --decoder "$(command -v ktech)"
```

Lệnh này chỉ đọc texture được `item-textures.json` tham chiếu, verify `images.zip` trước khi mở, decode toàn bộ vào staging và chỉ thay `public/assets/game` khi cả batch thành công.

## 4. Đọc lỗi và coverage

`python3 -m tools.extract.cli validate` trả exit code khác 0 nếu có hard failure. `data/generated/coverage.json` là nguồn chẩn đoán chính:

- `unresolved_dependencies`: ID được Tu Tiên tham chiếu nhưng không resolve trong registry/prefab/recipe/string của `scripts.zip`. Đây là hard failure; kiểm tra version runtime/snapshot và evidence locator, không tạo entity giả.
- `foreign_key_errors`: ingredient/source/relation không resolve entity. Đây là hard failure.
- `archive_checksum_errors`: ZIP thực tế, manifest và SHA lưu trong database không khớp. Đây là hard failure; snapshot lại nguyên archive.
- `wiki_urls`: URL phát hiện trong source/evidence/manifest của fact game canonical. Đây vẫn là hard failure để ngăn fact game vô tình lấy từ web; các bảng `wiki_*` có provenance riêng và không nằm trong phép kiểm tra này.
- `runtime_coverage_errors`: mỗi entity `tu_tien` phải có đúng một row cho từng category runtime bắt buộc. Category thiếu, ngoài allowlist hoặc bị lặp đều là hard failure.
- `prefab_export_coverage_errors`: tập prefab game canonical phải phủ tập stem của file trực tiếp trong `scripts/prefabs/`, trừ technical prefab đã audit/exclude. Entry `wiki:<page_id>` được bỏ qua; dependency inventory chỉ được phép xuất thêm khi một công thức publish thực sự tham chiếu tới nó. ID game thiếu hoặc ID thừa không có lý do vẫn là hard failure.
- `conflicts`: nhiều fact khác nhau cho cùng field. Normalizer vẫn chọn giá trị theo ưu tiên source/confidence, giữ mọi candidate và đánh dấu evidence thắng; conflict là warning cần review, không bị ghi đè im lặng.
- `runtime_errors`: lỗi probe theo prefab/locator. Chúng vẫn hiện cả khi pipeline có thể hoàn tất; review trước khi coi field liên quan là đầy đủ.
- `low_confidence_fields`: evidence có confidence `< 0.7`, gồm record/source/locator và trạng thái `selected`. Đây là danh sách cần manual review, đồng thời sinh warning `low_confidence_fields_present`.
- `coverage` và warning `optional_coverage_incomplete`: tỷ lệ entity có tên Việt, icon, recipe, acquisition và stats. Thiếu field tùy chọn là warning, không phải lý do tạo dữ liệu suy đoán.
- `missing_inventory_names`: danh sách sắp xếp ổn định chứa **mọi** entity `tu_tien` có `is_inventory_item = 1` nhưng `name_vi` null/rỗng; warning cùng tên ghi count. Invariant hoàn tất là mỗi inventory item hoặc có `name_vi`, hoặc xuất hiện đúng trong danh sách này. Đây là soft coverage gate, không phải lý do đoán tên hoặc hard-fail pipeline.

`extraction_errors` chứa toàn bộ lỗi parser/probe; `warnings` tóm tắt coverage thiếu, extraction errors, conflicts và low-confidence fields. Chỉ `hard_failures` quyết định exit code của `validate`/`all`.

## 5. Artefact được tạo

- `data/generated/wiki.sqlite`: database chuẩn hóa có entities, recipes, ingredients, acquisition, stats/effects/relations/assets, evidence, conflicts, extraction errors và các bảng `wiki_import_runs`, `wiki_pages`, `wiki_recipes`, `wiki_recipe_ingredients`, `wiki_images`, `wiki_entity_mappings`. Đây là nguồn audit/provenance đầy đủ.
- `public/data/catalog.json`: JSON entity đã nest, sắp xếp ổn định; là input chính cho tìm kiếm và trang chi tiết của wiki tương lai.
- `public/data/assets.json`: asset map và provenance cho icon/atlas; là input asset của wiki tương lai.
- `public/data/items.json`: payload schema version 6 cho màn tìm kiếm Prefabs, gồm category, tên, công thức runtime/Wiki, `craftingNote`, sprite descriptor, metadata Wiki và `structureDetails`. Entity map chắc chắn được enrich tại ID game cũ; page chưa map dùng ID `wiki:<page_id>` nhưng luôn có namespace `base_game` để xuất hiện trong nhóm DST. Namespace Tu Tiên chỉ công bố entity có tên tiếng Việt. `craftingNote` chỉ là ghi chú trong menu chế tạo, không được dùng để suy đoán nguyên liệu hoặc số lượng.
- `public/data/wiki/pages/<page_id>.json`: detail article đã sanitize và loại navigation/template lặp; HTML/wikitext/plain text gốc đầy đủ vẫn nằm trong SQLite.
- `public/assets/wiki/*`: ảnh gốc được detail/list tham chiếu, đặt tên content-addressed theo SHA-256.
- `data/generated/item-textures.json`: manifest texture tối thiểu cần decode cho `items.json`.
- `public/assets/game/*.png`: texture trình duyệt dùng được, tên file theo SHA-256 và được tạo bởi `publish-assets`.
- `data/generated/coverage.json`: quality gate và danh sách việc cần review; không phải payload hiển thị chính.
- `data/generated/structure-icon-audit.json`: audit deterministic cho toàn bộ công trình vốn thiếu icon, gồm classification, reason, evidence và action `keep`/`repair`/`exclude`.
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

Kết quả hợp lệ phải có cả `base_game` và `tu_tien`, selected evidence lớn hơn 0, foreign-key check không in dòng nào, `hard_failures` rỗng và `git diff --check` im lặng. `validate` cũng phải xác nhận tập prefab DST export khớp chính xác tập file nguồn. Trước khi ký duyệt, còn phải xác nhận mọi ingredient resolve, không có URL HTTP trong source/evidence/manifest, checksum/size archive khớp manifest, và ba thư mục mod giống byte-for-byte với bản tải gốc.
