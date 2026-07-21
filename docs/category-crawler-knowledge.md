# Shared Category Crawler Knowledge

Tài liệu này là contract dùng chung cho mọi crawler Category của DST Wiki. Một
Category mới phải tái sử dụng discovery, URL registry, shared page cache,
checkpoint, retry, note review, merge và validation; không tạo crawler riêng.

## Shared URL registry

File vận hành dùng chung:

```text
data/crawled/fandom-url-registry.json
data/crawled/fandom-url-registry.lock
data/crawled/fandom-shared-pages/<sha256-canonical-url>.json
```

Registry là danh sách URL item chuẩn hóa trên cùng origin MediaWiki. Mỗi row có:

- `url`: canonical HTTPS URL, là khóa duy nhất;
- `status`: chỉ nhận `New`, `Doing`, hoặc `Done`;
- `categories`: các category key đã phát hiện URL này;
- `workerId`: worker đang giữ row khi trạng thái là `Doing`;
- `attempts`, `createdAt`, `updatedAt`, `claimedAt`, `completedAt`;
- `artifactPath`: shared payload khi `Done`;
- `lastError`: lỗi gần nhất nếu một lần crawl được trả về `New`.

File JSON dành cho người vận hành đọc và review. Sidecar `.lock` dùng advisory
file lock; mọi read-modify-write đều giữ exclusive lock và thay file bằng
`os.replace`, nên hai Category chạy song song không thể cùng claim một URL.

## State machine

```text
URL chưa tồn tại -> thêm New -> claim -> Doing -> complete -> Done
                                  |
                                  +-> lỗi đã bắt -> New
```

Quy tắc nhận URL:

1. Chuẩn hóa URL trước khi lookup; fragment bị bỏ, host/scheme/title được
   canonical hóa và URL ngoài Fandom origin bị từ chối.
2. URL chưa tồn tại được thêm với `New`, category hiện tại được gắn vào
   `categories`, rồi worker có thể claim trong cùng critical section.
3. URL đã `New` được chuyển nguyên tử sang `Doing` và được crawl.
4. URL đã `Doing` hoặc `Done` không được fetch lại; category mới chỉ được thêm
   vào `categories`.
5. Khi `Done`, category consumer đọc `artifactPath` từ shared cache thay vì gọi
   Fandom lại.
6. Lỗi được crawler bắt sẽ release `Doing -> New`, tăng `attempts` và giữ
   `lastError` để lần chạy sau retry.
7. Nếu process chết đột ngột, row có thể còn `Doing`. Crawler không tự lấy lại
   row này vì contract yêu cầu `Doing` phải skip. Operator phải review rồi dùng
   lệnh requeue/reset có chủ đích.

`Done` không có nghĩa item đã được publish. Nó chỉ chứng minh raw page payload
đã crawl xong và có trong shared cache. Mỗi Category vẫn phải chạy normalizer,
DST filter, prefab-code merge, note review và validation riêng.

## Category isolation and overlap

Mỗi Category có config và checkpoint riêng dưới
`data/crawled/fandom-categories/<key>/`. Discovery evidence, exclusion reasons,
normalization và audit không dùng chung. Chỉ network page fetch và raw normalized
page payload được deduplicate qua registry/cache.

Nếu hai Category cùng phát hiện Beefalo:

- worker đầu tiên claim URL và thấy `Doing` trong registry;
- worker thứ hai ghi thêm category của nó rồi skip fetch;
- sau khi worker đầu hoàn tất, shared payload chuyển thành `Done`;
- lần chạy tiếp theo của category thứ hai materialize payload từ cache và tiếp
  tục pipeline của chính nó.

Vì vậy skip không được coi là đã hoàn thành Category hiện tại; nó chỉ tránh
request trùng trong lúc owner khác đang xử lý.

## Adding another Category

1. Tạo một config reviewable trong `data/config/wiki-categories/<key>.json`.
2. Khai báo URL nguồn, expected direct members, expected published members,
   namespace, game, item type, tags và mọi excluded title có lý do.
3. Chạy category discovery. Mọi direct item URL sẽ được register vào shared URL
   registry với category key.
4. Chạy lại cho đến khi không còn URL `New` thuộc Category và mọi URL `Doing`
   đã được owner hoàn tất hoặc operator review/requeue.
5. Chạy normalizer, note review, prefab mapping, merge, export và validation.

Không sửa count guard hoặc exclusion list chỉ để làm crawl xanh. Mọi membership
drift phải dừng pipeline và được review như một thay đổi dữ liệu.
