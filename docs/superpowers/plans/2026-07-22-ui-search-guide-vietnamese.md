# UI, Search, and Vietnamese Guide Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện UI trên desktop/mobile, bảo đảm search theo tên Việt, tên Anh và code, hiển thị đủ nhân vật DST/Tu Tiên, đồng thời Việt hóa nội dung Guide.

**Architecture:** Giữ nguyên bộ lọc tuyến tính hiện tại vì 1.979 bản ghi chưa cần search index. Tách việc chọn nhân vật thành hàm thuần có test, mở rộng phần highlight đúng trường khớp, chuẩn hóa mục lục Guide ở parser để UI không nhận liên kết mồ côi, và lưu bản dịch tiếng Việt trực tiếp trong dữ liệu Guide đã xuất bản.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, Vitest, Testing Library.

## Global Constraints

- Search không dấu/có dấu phải khớp tên Việt, tên Anh và `prefabId`.
- `code/prefabId` tiếp tục là khóa định danh duy nhất của item.
- Nội dung Guide hiển thị bằng tiếng Việt; giữ nguyên tên riêng, tên item và thuật ngữ DST cần thiết.
- Không hiển thị mục lục trỏ tới section không tồn tại.
- Không thêm dependency mới.

---

### Task 1: Search fields and complete character catalog

**Files:**
- Create: `app/lib/character-catalog.ts`
- Create: `app/lib/character-catalog.test.ts`
- Modify: `app/characters/page.tsx`
- Modify: `app/components/item-result.tsx`
- Modify: `app/components/item-result.test.tsx`
- Modify: `app/components/wiki-search.tsx`

**Interfaces:**
- Produces: `selectCharacters(items: readonly ItemListEntry[]): ItemListEntry[]`.
- Preserves: `filterItems(...)` public behavior and normalized Vietnamese matching.

- [ ] **Step 1: Write failing tests**

Add tests proving `selectCharacters` returns both `base_game` and `tu_tien` characters, and proving `ItemResult` renders `<mark>` inside both the English-name line and prefab-code line when those fields match.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `npm test -- app/lib/character-catalog.test.ts app/components/item-result.test.tsx`

Expected: FAIL because `selectCharacters` does not exist and English/code fields are not highlighted.

- [ ] **Step 3: Implement minimal behavior**

Implement the selector as `items.filter((item) => item.category === "character")`, use `HighlightedText` for `englishName` and `prefabId`, and change the visible search copy to `Tìm theo tên Việt, tên Anh hoặc code...`.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `npm test -- app/lib/character-catalog.test.ts app/components/item-result.test.tsx app/lib/wiki-search.test.ts`

Expected: all selected tests PASS.

### Task 2: Clean and localize Guide presentation

**Files:**
- Modify: `app/lib/guide-catalog.ts`
- Modify: `app/lib/guide-catalog.test.ts`
- Modify: `app/components/guide-reader.tsx`
- Modify: `app/components/guide-reader.test.tsx`
- Modify: `public/data/guides/pages/how-to-kill-the-giants-in-dst.json`
- Modify: `public/data/guides/pages/maximum-efficiency-day-13-base-dst-guide.json`
- Modify: `public/data/guides/pages/slurtle-slime-guide.json`
- Modify: `public/data/guides/pages/taming-a-beefalo.json`

**Interfaces:**
- `parseGuideDetail(value)` returns only TOC rows whose anchors exist in parsed sections or section HTML.
- Guide JSON retains schema version 1 and source attribution.

- [ ] **Step 1: Write failing parser and reader tests**

Add a parser test with `Contents`, a trailing `[]`, and an orphan anchor; expect only real anchors with cleaned Vietnamese labels. Add a reader test requiring a minimum 44px TOC target and hiding the TOC when it is empty.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `npm test -- app/lib/guide-catalog.test.ts app/components/guide-reader.test.tsx`

Expected: FAIL on orphan/noisy TOC behavior and mobile target styling.

- [ ] **Step 3: Implement parser and reader behavior**

Normalize labels by removing trailing `[]`, discard `Contents`, filter anchors against section ids/HTML ids, conditionally render the TOC, and apply `min-h-11` to TOC links.

- [ ] **Step 4: Translate published Guide content**

Replace English prose and headings in all four detail JSON files with concise Vietnamese translations while preserving safe HTML, DST names, links, image paths, ids and source metadata.

- [ ] **Step 5: Run focused tests and validate data**

Run: `npm test -- app/lib/guide-catalog.test.ts app/components/guide-reader.test.tsx`

Expected: all selected tests PASS and all four JSON payloads parse.

### Task 3: Resolve remaining UI warnings and verify all routes

**Files:**
- Modify: `app/base/page.tsx`
- Modify: `app/base/page.test.tsx`
- Modify: `app/layout.tsx`

**Interfaces:**
- Base images above the fold use Next Image eager loading.
- Root metadata uses `NEXT_PUBLIC_SITE_URL` when available and a deterministic localhost fallback.

- [ ] **Step 1: Write failing UI tests**

Require above-the-fold Base images to render with eager priority semantics and require metadata to expose `metadataBase`.

- [ ] **Step 2: Run tests and verify RED**

Run: `npm test -- app/base/page.test.tsx`

Expected: FAIL because images are currently lazy and metadata has no base URL.

- [ ] **Step 3: Implement minimal warning fixes**

Mark visible Base images eager and add `metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000")`.

- [ ] **Step 4: Run complete verification**

Run: `npm test`, `npm run lint`, and `npm run build`.

Expected: all commands exit 0 with no test failures, ESLint errors, type errors, or build failures.

- [ ] **Step 5: Browser regression audit**

Check `/`, `/characters`, `/base`, `/guides`, and all four Guide detail routes at 1440×900 and 390×844. Verify no broken images/horizontal overflow, all 19 character cards are searchable, and Vietnamese/English/code searches each return the expected item.
