# Publication Quality Review — 2026-07-22

## Kết quả

Pipeline repair-first đã xử lý 2.428 item công khai và 4 Guide DST. Output cuối
có 1.979 item, 4 Guide, 1.979 ID/code duy nhất, 100% ảnh local hợp lệ, 100% có
nội dung và 100% đạt detail contract theo loại. Final audit có 0 repair, 0
merge, 0 remove và 0 hard failure.

| Loại | Trước | Sau | Không thể phục hồi |
|---|---:|---:|---:|
| boss | 35 | 25 | 10 |
| character | 30 | 19 | 11 |
| effect | 53 | 27 | 26 |
| item | 966 | 856 | 110 |
| mob | 325 | 163 | 162 |
| other | 634 | 539 | 95 |
| pill | 68 | 68 | 0 |
| structure | 317 | 282 | 35 |
| **Tổng** | **2.428** | **1.979** | **449** |

## Repair và removal

- Giữ nguyên 1.781 item đã đạt chuẩn.
- Repair thành công 198 item từ đúng reviewed Category page: 184 sprite, 82 mô
  tả và 10 title hồ sơ Character; một item có thể sửa nhiều field.
- 84 asset SHA-256 duy nhất trong `public/assets/quality/` đang được tham chiếu;
  không có orphan.
- Loại 449 item chỉ sau năm attempt đã ghi trong report. Trong đó 434 vẫn thiếu
  ảnh, 153 thiếu nội dung và 163 thiếu detail; các issue có thể chồng nhau.
- 31 removal có canonical source nhưng source không cung cấp đủ dữ liệu/ảnh;
  418 removal còn lại chủ yếu là prefab kỹ thuật/wrapper không có canonical page
  để phục hồi. Không có duplicate ID hoặc prefab code.

Quyết định đầy đủ cho từng identity nằm trong
`data/generated/publication-quality-report.json`, gồm URL, issue ban đầu, thứ tự
evidence đã thử, thay đổi và issue cuối. Không có ảnh giả hoặc placeholder.

## Guide

Category Guides có 107 direct member: 105 article namespace 0, một Board Thread
và một Category con. Không crawl đệ quy. Bốn bài DST đủ cover/nội dung được xuất
bản; 101 article bị loại theo review scope/content. Crawl cuối có 4 page, 4 ảnh,
421 link, 0 failure/pending. `/guides` là catalog riêng và
`/guides/[slug]` là trang đọc riêng, không dùng side peek.

## Bằng chứng kiểm tra

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
npm test
npx tsc --noEmit
npm run lint
npm run build
python3 -m tools.extract.cli publication-quality \
  --items public/data/items.json --guides public/data/guides \
  --public-root public --category-root data/crawled/fandom-categories \
  --report /private/tmp/dst-wiki-publication-quality-final-audit.json
```

Independent scan kiểm tra trực tiếp file và JSON, không dựa vào report: 1.979
item, 1.979 ID, 1.979 normalized code, 4 Guide slug, 84/84 quality asset được
tham chiếu, 0 orphan và 0 publication issue.
