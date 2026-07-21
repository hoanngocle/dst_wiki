# Durable Category Crawler State Design

## Goal

Giữ registry URL và shared page payload bền vững qua nhiều Git worktree, để
`Done` luôn có artifact đọc được, nhiều Category có thể chạy song song mà không
fetch trùng, và raw crawl data không bị commit/deploy.

## Approved approach

Live operational state nằm trong Git common directory, dùng chung cho mọi
worktree của repository:

```text
<git-common-dir>/category-crawler/fandom-url-registry.json
<git-common-dir>/category-crawler/fandom-url-registry.lock
<git-common-dir>/category-crawler/shared-pages/<sha256-url>.json
```

`git rev-parse --git-common-dir` là nguồn xác định root. Trong normal checkout
và linked worktree, mọi crawler process của cùng repository đều resolve tới
cùng một directory. Không dùng `$HOME`, thư mục tạm hay path ngoài repository.

Hai file trong worktree chỉ là snapshot reviewable:

```text
data/crawled/fandom-url-registry.json
docs/category-crawler-control.md
```

Snapshot không được dùng làm live lock/state khi crawler chạy. Raw payload vẫn
không được track trong Git.

## Components

### State path resolver

`tools/crawl_wiki/state_paths.py` trả về Git common directory và các path live.
CLI cho phép truyền path explicit để tests hoặc operator dùng storage khác;
khi không truyền, crawler dùng common-state paths ở trên.

Resolver hard-fail nếu không ở trong Git repository, `git rev-parse` lỗi, hoặc
resolved common directory không tồn tại. Không âm thầm quay về worktree-local.

### Live registry and cache

`UrlRegistry` tiếp tục sở hữu state machine `New -> Doing -> Done`, advisory
lock, atomic JSON replacement và checksum payload. Interface nhận explicit
registry/cache paths vẫn giữ nguyên để unit tests độc lập.

Một row chỉ hợp lệ ở `Done` khi:

- có `artifactPath` tương đối dưới live state root;
- artifact tồn tại và là regular file;
- SHA-256 khớp `artifactSha256`;
- payload decode thành JSON object đúng contract.

### Audit and explicit repair

Thêm audit read-only để phân loại từng row: `valid`, `missing`, `checksum_error`,
`invalid_json`, hoặc `invalid_state`. Crawler không tự đổi `Doing`/`Done` trong
startup vì contract yêu cầu skip hai trạng thái này.

Operator chạy repair explicit cho các row `Done` không hợp lệ. Repair dùng
`UrlRegistry.requeue`, xóa artifact metadata, chuyển về `New`, giữ categories,
attempt history và ghi `lastError` có lý do. Row `Doing` không tự requeue; vẫn
cần owner guard hoặc quyết định thủ công.

Batch hiện tại sẽ audit 29 row cũ, requeue toàn bộ row có artifact mất, rồi cập
nhật snapshot trước khi crawl. Sáu URL overlap của Cave Creatures sau đó được
crawl lại như `New`, không được reuse giả.

### Snapshot export

Sau mỗi batch hoặc repair, CLI xuất bản copy canonical, stable-sorted của live
registry sang `data/crawled/fandom-url-registry.json` bằng atomic replace. File
control MD được cập nhật từ snapshot và category audits; nó không điều khiển
claim trực tiếp.

Snapshot export không copy raw payload vào worktree và không thay đổi live
state. Nếu snapshot khác live registry, live registry là operational source of
truth, snapshot chỉ phục vụ review/commit/handoff.

## Category batch decisions

- Crawl direct namespace-0 pages, không đệ quy Category con.
- Chỉ register 147 unique DST candidates đã review trong control MD.
- Loại 24 unique Shipwrecked/Hamlet/Don't Starve-only pages trước detail.
- Loại `Mobs`, `Shadow Creature`, `Spiders` bằng lý do
  `non_item:overview`; mở rộng config reason enum đúng nghĩa, không giả thành
  non-DST.
- Giữ `Backpacks` cùng `Containers`; registry dedupe overlap và Backpacks bổ
  sung `Seed Pack-It`.
- Giữ `Celestial Filter` cùng legacy `Celestial Tab`; hai nguồn có item riêng và
  overlap `Glass Cutter` được dedupe.

## Data flow

1. Resolve Git common-state paths.
2. Nếu live registry chưa tồn tại, operator chạy init explicit từ tracked
   snapshot. Init chỉ import URL, categories và attempts; mọi row được đưa về
   `New`, bỏ owner/artifact metadata và ghi lý do import vì raw payload không
   nằm trong Git. Init không overwrite live state hiện hữu.
3. Audit live registry và dừng crawl nếu có invalid `Done` rows.
4. Operator chạy repair explicit cho live state cũ; export snapshot.
5. Category discovery áp count guard, namespace guard và exclusion list.
6. Accepted canonical URL được register/claim trong live registry.
7. `New` được fetch và lưu content-addressed payload; `Doing` skip; valid `Done`
   load từ shared cache.
8. Hoàn tất batch thì export registry snapshot và cập nhật control MD.

## Errors and recovery

- Missing/corrupt `Done` artifact: audit hard-fail trước network crawl; repair
  explicit chuyển row về `New`.
- Snapshot có `Done` nhưng live store chưa tồn tại: init import row thành `New`;
  không tin status thiếu raw artifact.
- Live registry malformed hoặc duplicate URL: hard-fail, không dùng snapshot
  ghi đè.
- Worker chết ở `Doing`: giữ nguyên để operator review owner và requeue.
- Detail fetch lỗi: hành vi hiện tại release `Doing -> New`, tăng attempts và
  giữ `lastError`.
- Snapshot export lỗi: live state không đổi; batch báo lỗi handoff.

## Verification

- Unit tests resolver cho normal checkout, linked worktree, explicit override
  và failure ngoài Git repository.
- Registry tests cho audit valid/missing/checksum/JSON, explicit repair và
  bảo toàn categories/attempts.
- Integration test chứng minh hai simulated worktrees dùng chung một live
  registry/cache và chỉ một worker fetch URL overlap.
- Regression test chứng minh snapshot có `Done` nhưng thiếu artifact không được
  reuse hoặc âm thầm crawl.
- Config tests chấp nhận `non_item:overview`, vẫn từ chối reason tùy ý.
- Chạy toàn bộ Python tests, frontend tests, TypeScript, lint và production
  build trước khi hoàn tất batch.

## Out of scope

- Commit raw Fandom payload vào Git.
- Đồng bộ live state giữa hai clone repository hoặc hai máy.
- Tự động requeue row `Doing` theo timeout.
- Đệ quy Category con.
- Thay đổi UI side peek trong batch này.
