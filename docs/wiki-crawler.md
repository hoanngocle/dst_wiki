# Don't Starve Wiki crawler

Crawler này dùng MediaWiki Action API công khai, không cần tài khoản, API key
hoặc OAuth. Nó lấy revision mới nhất của toàn bộ trang thuộc Main (`0`),
Category (`14`) và File (`6`), lưu wikitext + HTML + plain text, ghi đồ thị
internal link và tải file ảnh gốc.

## Yêu cầu

- Python 3.9 trở lên.
- Kết nối HTTPS tới `dontstarve.wiki.gg` và host CDN có trong `imageinfo`.
- Đủ dung lượng đĩa cho toàn bộ ảnh gốc. Crawl đầy đủ có thể tạo dữ liệu lớn;
  nên kiểm tra bằng smoke run trước.

Crawler chỉ dùng Python standard library, không cần `pip install`.

## Crawl Category dùng chung

Mỗi Category dùng config `data/config/wiki-categories/<key>.json` và checkpoint
riêng dưới `data/crawled/fandom-categories/<key>/`, nhưng dùng chung registry
`data/crawled/fandom-url-registry.json` cùng shared page cache. URL chưa có hoặc
đang `New` được claim; URL `Doing`/`Done` được skip network fetch. Crawler không
mở rộng đệ quy category con.

```bash
python3 -m tools.crawl_wiki.cli \
  --profile category \
  --category animals \
  --page-budget 100
```

Chạy lại đến khi `pending_pages=0`, `pending_images=0`, `failures=0`. Animals có
guard đúng 35 trang namespace 0, loại sáu trang không thuộc DST trước detail và
image crawl, bỏ bốn category con, chỉ queue 29 Mob DST. Count/membership drift
phải dừng để review. Danh sách URL/status nằm trong
`docs/category-crawler-control.md`; contract đầy đủ nằm trong
`docs/category-crawler-knowledge.md`.

Category mới chỉ cần thêm config, ví dụ `birds.json`, rồi chạy với
`--category birds`; không copy crawler.

## Crawl chọn lọc item (khuyến nghị)

Profile `items` chỉ lấy các link có icon nằm trong năm section đã chốt:

- `Items#Resources-0`
- `Items#Craftable_Items-0`
- `Items#Food-0`
- `Items#By_Crock_Pot_Value-0`
- `Plants#DST-0`

Mỗi lần chạy mặc định xử lý tối đa 100 detail page rồi tự dừng:

```bash
python3 -m tools.crawl_wiki.cli \
  --profile items \
  --item-budget 100
```

Output mặc định là `data/crawled/dontstarve-items/`. Chạy lại nguyên lệnh trên
để xử lý 100 item kế tiếp. Lần đầu crawler tải hai source page, tạo seed list,
resolve page ID rồi checkpoint discovery; các lần sau không discovery lại.

Profile này lưu revision mới nhất, HTML, wikitext, category và link của từng
item nhưng không mở rộng đệ quy từ link trong detail. Nó chỉ tải ảnh gốc của
icon được chọn trong source list; ảnh gallery và navbox không được đưa vào hàng
đợi. `recipes.jsonl` chứa nguyên liệu từ `Object Infobox` và các template
`Recipe` có `result` trùng với item hiện tại.

Nếu server đóng kết nối, timeout hoặc reset request, crawler retry với backoff.
Sau khi hết số lần thử, page/image lỗi được ghi vào `errors.jsonl`; checkpoint
của các item đã hoàn thành vẫn được giữ. Dùng `--retry-errors` để đưa các entry
lỗi trở lại queue.

## Chạy đầy đủ

Từ thư mục gốc repository:

```bash
python3 -m tools.crawl_wiki.cli \
  --base-url https://dontstarve.wiki.gg/ \
  --output data/crawled/dontstarve-wiki
```

Giá trị mặc định đã trùng với lệnh trên, nên có thể chạy ngắn gọn:

```bash
python3 -m tools.crawl_wiki.cli
```

Crawler chạy tuần tự, cách request tối thiểu `0.5` giây, dùng `maxlag=5`, timeout
30 giây và tối đa 5 lần thử cho lỗi tạm thời. Không nên giảm `--delay` khi crawl
toàn site.

## Smoke test ba trang

```bash
python3 -m tools.crawl_wiki.cli \
  --output /tmp/dontstarve-wiki-smoke \
  --max-pages 3 \
  --skip-images \
  --fresh
```

`--max-pages` giới hạn tổng số page ID được đưa vào queue. `--skip-images` vẫn
ghi danh sách ảnh trong page record nhưng chưa tải binary; chạy lại cùng output
mà bỏ cờ này sẽ xử lý image queue còn lại.

## Resume và retry lỗi

`state.sqlite` lưu continuation token, page/image queue, attempts và trạng thái.
Nếu tiến trình bị dừng, chạy lại đúng lệnh cũ để tiếp tục. Các record append trùng
do gián đoạn được compact theo khóa logic khi finalization hoàn tất.

Item lỗi vĩnh viễn được giữ ở trạng thái `failed`, ghi vào `errors.jsonl`, và làm
process trả exit code `1`. Sau khi nguyên nhân bên ngoài đã được xử lý:

```bash
python3 -m tools.crawl_wiki.cli \
  --output data/crawled/dontstarve-wiki \
  --retry-errors
```

`--fresh` chỉ dành cho một output chưa có `state.sqlite`; crawler không âm thầm
xóa hoặc ghi đè một crawl đang tồn tại. Muốn tạo snapshot mới, hãy chọn output
directory mới.

## Output

```text
data/crawled/dontstarve-wiki/
├── seeds.jsonl
├── pages.jsonl
├── recipes.jsonl
├── images.jsonl
├── links.jsonl
├── errors.jsonl
├── index.json
├── manifest.json
├── state.sqlite
└── images/original/<sha256>.<extension>
```

- `pages.jsonl`: revision metadata, wikitext, rendered HTML, normalized plain
  text, categories, internal links, images, redirect target và canonical URL.
- `seeds.jsonl`: ở profile `items`, lưu title, href, icon đã chọn và tất cả
  source section chứa item đó; full profile để file này rỗng.
- `recipes.jsonl`: công thức đã chuẩn hóa theo item; full profile để file này
  rỗng.
- `images.jsonl`: File title/page ID, original URL, MIME, kích thước, MediaWiki
  SHA-1, SHA-256 local, và đường dẫn binary.
- `links.jsonl`: mỗi edge `source → target`, kể cả red link và target namespace
  ngoài phạm vi crawl.
- `errors.jsonl`: lỗi chưa giải quyết sau retry.
- `index.json`: title/page ID tới byte offset trong JSONL để seek trực tiếp.
- `manifest.json`: cấu hình, trạng thái `partial`/`complete`, queue còn lại,
  counts và SHA-256 của các file JSONL.
- `state.sqlite`: checkpoint phục vụ resume; không phải public export contract.

Ảnh được content-address theo SHA-256. Hai File title có cùng binary dùng chung
một file local, nhưng vẫn có metadata record riêng.

## Đọc JSONL theo streaming

```python
import json
from pathlib import Path

with Path("data/crawled/dontstarve-wiki/pages.jsonl").open(
    encoding="utf-8"
) as handle:
    for line in handle:
        page = json.loads(line)
        print(page["page_id"], page["title"], page["revision"]["id"])
```

Không nên dùng `json.load()` cho JSONL; mỗi dòng là một JSON object độc lập.

## Tùy chọn chính

```text
--profile full|items|category
--category <config-key>
--namespaces 0,14,6
--delay 0.5
--timeout 30
--max-attempts 5
--user-agent <descriptive value>
--max-pages <positive integer>
--item-budget <positive integer>
--skip-images
--fresh
--retry-errors
--log-level DEBUG|INFO|WARNING|ERROR
```

Chỉ namespace `0`, `6`, `14` được hỗ trợ. Có thể truyền một subset, ví dụ
`--namespaces 0,14`.

`--max-pages` chỉ dùng với profile `full`; `--item-budget` chỉ dùng với profile
`items`; `--page-budget` chỉ dùng với profile `category`. Các profile dùng
output và SQLite state riêng, không trộn với crawl toàn site cũ.

## Exit codes

- `0`: mọi item đã lên lịch hoàn tất, không còn lỗi.
- `1`: crawl hoàn tất nhưng còn page/image lỗi trong `errors.jsonl`.
- `2`: tham số không hợp lệ, state không tương thích hoặc lỗi setup/fatal.
- `130`: người dùng ngắt bằng `Ctrl+C`; checkpoint đã được giữ để resume.
