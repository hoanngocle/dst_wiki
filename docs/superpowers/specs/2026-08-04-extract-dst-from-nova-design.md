# Tách DST Wiki khỏi Nova — Thiết kế

**Ngày:** 2026-08-04

**Repository đích:** `/Users/nyx/company/dst_wiki`

**Repository cần dọn sau cutover:** `/Users/nyx/company/nova`

## Bối cảnh

`dst_wiki` ban đầu là ứng dụng Next.js đọc các JSON và asset đã publish. Pipeline
Python dùng SQLite để chuẩn hóa, lưu provenance và audit dữ liệu, nhưng SQLite
không phải dependency của runtime Vercel.

DST sau đó được port vào Nova thành một miền Laravel/Inertia hoàn chỉnh. Bản
Nova bổ sung giao diện dark-theme đã tối ưu, character dossier, guide, catalog,
Wiki detail và một màn admin chỉnh character guide. Dữ liệu runtime của bản này
được đọc từ các bảng PostgreSQL `dst_*`.

Mục tiêu hiện tại là đảo chiều việc gộp: đưa trải nghiệm public đã tối ưu trở lại
`dst_wiki`, deploy độc lập trên Vercel, rồi xóa toàn bộ miền DST khỏi Nova.

## Quyết định đã duyệt

- `dst_wiki` là ứng dụng public-only; không có đăng nhập hoặc trang admin.
- Production dùng Next.js và static JSON; không dùng database runtime.
- SQLite chỉ tồn tại trong pipeline local để crawl, chuẩn hóa và audit.
- Ứng dụng độc lập dùng URL gốc, không giữ prefix `/dst`.
- Chỉ port phần nội dung DST đã tối ưu; không port Nova sidebar, game header,
  auth wrapper, Zustand store hoặc các miền Game/Library khác.
- Sau cutover, Nova xóa hoàn toàn URL `/dst...`; không redirect sang site mới.
- Chỉ xóa DST khỏi Nova sau khi `dst_wiki` vượt qua toàn bộ quality gate.

## Mục tiêu

1. Giữ nguyên hành vi và chất lượng giao diện public DST hiện có trong Nova.
2. Khôi phục `dst_wiki` thành source of truth độc lập cho code, dữ liệu và asset.
3. Cho phép Vercel phục vụ site mà không cần filesystem bền vững hoặc database.
4. Giữ pipeline crawl/import hiện có có thể tái chạy và sinh output xác định.
5. Xóa route, code, data, asset và database DST khỏi Nova sau khi cutover an toàn.

## Ngoài phạm vi

- Không port admin character-guide editor.
- Không hỗ trợ chỉnh sửa dữ liệu trực tiếp trên production.
- Không port tài khoản, session, authorization hoặc navigation của Nova.
- Không dùng Nova làm nguồn dữ liệu ở build-time sau cutover.
- Không xây API search hoặc API Wiki detail động.
- Không giữ redirect hoặc compatibility route `/dst...` trong Nova.
- Không refactor các miền Nova không liên quan.

## Kiến trúc đích

```text
Nguồn game / Wiki / dữ liệu thủ công
                 |
                 v
       Pipeline Python local
                 |
                 v
      SQLite + báo cáo audit local
                 |
                 v
  JSON + asset đã publish trong public/
                 |
                 v
  Next.js build-time parsing/rendering
                 |
                 v
      Vercel CDN + React client islands
```

Next.js Server Components đọc JSON khi build để tạo các trang catalog,
characters và guide. Component tương tác phía client xử lý tìm kiếm, filter,
modal và retry. Chi tiết Wiki được tải lười từ file JSON tĩnh qua CDN thay vì
gọi controller hoặc database.

Không có connection string, migration hoặc SQLite file trong runtime bundle.
`data/generated/wiki.sqlite`, crawl state và raw artifacts tiếp tục bị loại bởi
Git/Vercel ignore như hiện tại.

## URL và điều hướng

| URL đích | Chức năng |
|---|---|
| `/` | Catalog vật phẩm, tìm kiếm, filter và item detail |
| `/characters` | Character gallery và dossier modal |
| `/guides` | Danh mục guide |
| `/guides/[slug]` | Guide reader |
| `/guides/canh-gioi-tu-tien` | Bảng cảnh giới Tu Tiên |

Chi tiết item tiếp tục dùng modal. Nội dung Wiki liên kết với item được tải từ
`/data/wiki/pages/{pageId}.json`. Dynamic guide routes phải được tạo từ guide
index bằng `generateStaticParams()` và trả 404 cho slug không được publish.

Mọi internal link được port từ Nova phải bỏ prefix `/dst`. Source URL trỏ tới
Wiki ngoài hệ thống không bị thay đổi.

## Phạm vi giao diện

### Giữ từ `dst_wiki`

- Next.js App Router và cấu trúc route độc lập.
- Header đơn giản chỉ phục vụ Items, Characters và Guides.
- Pipeline Python, JSON contracts, generated reports và asset publication.
- Vitest, Testing Library và các test Python hiện có.

### Port chọn lọc từ Nova

- Shared DST primitives: hero, panel, state, field và page shell.
- Catalog search, filters, result cards và item detail modal.
- Recipe, mob, structure, Tu Tiên và structured Wiki renderers.
- Character gallery, cards và dossier modal.
- Guide browser, guide reader và cultivation table.
- DST-specific responsive behavior, keyboard/focus behavior và empty/error states.
- Dark content palette và các Nova tokens tối thiểu mà component DST sử dụng.

### Không port từ Nova

- `GameLayout`, shared Nova header/sidebar và auth wrapper.
- Inertia, Laravel route helpers và `Head`.
- Shared stores hoặc navigation state.
- Admin editor và Form Request contracts.
- Generic Nova components không được DST sử dụng trực tiếp.

`dst_wiki` có một root wrapper áp dụng dark DST content tokens và background,
nhưng header vẫn là header đơn giản của ứng dụng độc lập. Các token được chép
thành contract CSS cục bộ; component DST không phụ thuộc stylesheet của Nova.

## Dữ liệu và contracts

### Output production

- `public/data/items.json`: catalog public và payload chi tiết.
- `public/data/guides/index.json`: metadata guide dùng cho listing và static params.
- `public/data/guides/pages/*.json`: nội dung từng guide.
- `public/data/wiki/pages/*.json`: nội dung Wiki tải lười.
- `public/assets/**`: sprites, ảnh item, character, guide và Wiki đã publish.

### Adapter thay Laravel

| Nova | `dst_wiki` đích |
|---|---|
| `WikiCatalogService::items()` | parser và selector TypeScript trên `items.json` |
| `WikiCatalogService::guides()` | parser guide index |
| `WikiCatalogService::guide()` | lookup guide detail tĩnh theo slug |
| `WikiCatalogService::wikiPage()` | fetch JSON tĩnh theo page ID |
| `CharacterCatalogService` | selector/DTO builder TypeScript chạy build-time |
| Inertia page props | JSON import trong Server Components |
| Inertia `Head` | Next.js metadata APIs |

Parser phải kiểm tra schema version, required fields, enum, duplicate identity,
duplicate slug và đường dẫn asset. Các selector tạo dữ liệu theo thứ tự xác định
để cùng input luôn sinh cùng UI/output.

Character adapter phải giữ fallback Việt/Anh, source ordering, search text,
profile, guide, equipment icons và loại bỏ evidence nội bộ khỏi DTO public giống
hành vi Nova hiện tại.

## Luồng lỗi

- JSON contract không hợp lệ hoặc duplicate identity/slug làm build thất bại.
- Guide slug không tồn tại trả Next.js 404.
- Wiki page JSON không tồn tại hoặc tải lỗi hiển thị `DstState` danger và nút
  thử lại; item modal vẫn mở và phần còn lại vẫn sử dụng được.
- Asset bắt buộc bị thiếu làm publication audit hoặc test contract thất bại.
- Asset Wiki tùy chọn bị thiếu dùng trạng thái nội dung không có ảnh, không dùng
  placeholder giả.
- Nội dung HTML Wiki tiếp tục qua parser/sanitization contract hiện có; không
  render markup chưa được kiểm tra từ request runtime.

## Testing và quality gate của `dst_wiki`

### Automated

- Port/adapt test của Nova cho DST primitives, search, item detail, Wiki content,
  structured sections, character gallery/dossier và guides.
- Page tests kiểm tra route mới, metadata, props và không còn internal URL `/dst`.
- Parser tests kiểm tra happy path, malformed payload, duplicate ID/slug và asset
  reference.
- Python tests kiểm tra pipeline vẫn sinh JSON/asset xác định và SQLite chỉ là
  local artifact.
- Chạy `npm test`, `npm run lint`, TypeScript check và `npm run build`.
- Chạy nhóm Python test bị ảnh hưởng bởi exporter/contracts.

Trước khi viết code framework-facing, phải đọc guide tương ứng trong
`node_modules/next/dist/docs/` theo quy tắc của repository.

### Visual và hành vi

Kiểm tra desktop và mobile cho:

- catalog hero, counters, filters và empty state;
- mở/đóng item modal, keyboard focus và Wiki lazy loading;
- character filters, cards và dossier;
- guide listing, guide reader và cultivation table;
- loading, error, retry và reduced-motion behavior;
- không tràn viewport và không có internal link mang prefix `/dst`.

### Cutover gate

Chỉ được bắt đầu xóa Nova khi:

1. Toàn bộ automated checks ở trên pass.
2. `next build` thành công mà không có database environment variables.
3. Vercel Preview phục vụ được mọi route đích và asset chính.
4. Desktop/mobile smoke test đạt parity chức năng với Nova.
5. Kiểm tra source/runtime xác nhận không phụ thuộc Inertia, Laravel endpoint,
   Nova repository hoặc database production.

## Dọn DST khỏi Nova

Việc dọn Nova là phase riêng và commit riêng sau cutover gate.

### Xóa route và backend

- Xóa mọi import/controller route `/dst...` và `/admin/dst...`.
- Xóa mọi link/menu entry trỏ tới DST.
- Xóa DST controllers, requests, resources, models, policies nếu có, services,
  import/integrity commands, factories và seeders chỉ dùng cho DST.

### Xóa frontend

- Xóa `resources/js/pages/dst`, trang admin DST, DST-only components, libraries,
  types và tests.
- Xóa nhánh DST khỏi Inertia layout resolution.
- Giữ Nova theme tokens và shared components nếu CodeGraph impact cho thấy Game,
  Library hoặc auth vẫn sử dụng.

### Xóa data và assets

- Xóa asset/data DST trong Nova sau khi xác minh bản tương ứng đã tồn tại và được
  reference hợp lệ trong `dst_wiki`.
- Không chạm asset của Game/Library hoặc thay đổi không liên quan đang có trong
  worktree Nova.

### Xóa database

- Xóa các migration lịch sử chỉ tạo/sửa miền DST khỏi source tree Nova.
- Thêm một migration cleanup mới dùng `Schema::dropIfExists()` theo thứ tự đảo
  dependency để xóa toàn bộ bảng `dst_*` trên database đã deploy.
- Migration cleanup phải an toàn cho cả database có DST tables và fresh database
  không còn chạy migration tạo DST.
- Xóa model/import code chỉ sau khi migration cleanup không cần gọi chúng.

### Verification của Nova

- Pest test xác nhận route DST/admin DST không còn được đăng ký và URL trả 404.
- Migration test xác nhận không còn bảng `dst_*` sau khi migrate.
- Jest/layout tests xác nhận việc bỏ nhánh DST không ảnh hưởng Game/Library.
- Chạy affected Pest/Jest tests, `vendor/bin/pint --dirty`, frontend type/lint
  checks liên quan và production build.
- Dùng CodeGraph impact trước khi xóa symbol/file dùng chung.

## Trình tự commit và khả năng phục hồi

1. Các commit port UI/data adapter trong `dst_wiki`.
2. Commit quality fixes và Vercel readiness trong `dst_wiki`.
3. Xác minh Vercel Preview.
4. Commit xóa code/routes/assets DST trong Nova.
5. Commit migration cleanup và verification trong Nova nếu cần tách review.

Không stage thay đổi Nova không liên quan. Mọi phần xóa đều có thể phục hồi từ
Git; không dùng reset hoặc lệnh xóa diện rộng. Nếu cutover gate thất bại, dừng ở
`dst_wiki` và giữ Nova nguyên trạng.

## Tiêu chí hoàn thành

- `dst_wiki` giữ giao diện nội dung DST tối ưu từ Nova với header độc lập đơn giản.
- Catalog, characters, guides, cultivation và Wiki detail hoạt động ở URL gốc.
- Production Vercel chỉ dùng static JSON/assets và không cần database.
- Pipeline Python/SQLite local vẫn tái tạo và audit được output publish.
- Không còn internal URL `/dst` trong runtime `dst_wiki`.
- Nova không còn route, UI, backend, data, asset hoặc bảng database DST.
- `/dst...` và `/admin/dst...` trên Nova trả 404, không redirect.
- Các miền Game, Library và auth của Nova tiếp tục pass test/build liên quan.
