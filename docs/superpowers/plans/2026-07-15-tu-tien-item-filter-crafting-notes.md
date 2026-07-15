# Tu Tiên Item Filter and Crafting Notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chỉ công bố item Tu Tiên có tên tiếng Việt và bổ sung ghi chú chế tạo từ `game_text` mà không suy đoán nguyên liệu.

**Architecture:** SQLite vẫn là kho kiểm toán đầy đủ. Bước export đọc `STRINGS.RECIPE_DESC.*`, khử bản ghi trùng đồng giá trị, từ chối xung đột, rồi truyền lookup vào item exporter; exporter lọc riêng namespace Tu Tiên và phát hành schema version 3. Frontend xác thực trường `craftingNote`, đưa nó vào tìm kiếm và trình bày khác nhau tùy item có công thức runtime hay không.

**Tech Stack:** Python 3, SQLite, `unittest`, TypeScript, React 19, Next.js 16, Vitest, Testing Library.

## Global Constraints

- Không xóa entity, source, evidence hoặc `game_text` khỏi SQLite.
- Chỉ lọc namespace `tu_tien`; tập prefab `base_game` phải giữ nguyên.
- Chỉ công thức runtime được hiển thị dạng nguyên liệu và số lượng.
- `RECIPE_DESC` là ghi chú chế tạo, không được dùng để suy đoán nguyên liệu.
- Khóa trùng/cùng nội dung được gom; khóa trùng/khác nội dung phải làm export thất bại.
- Không gắn lời thoại nhân vật trong thay đổi này.

---

### Task 1: Lọc item Tu Tiên và ghép ghi chú từ SQLite

**Files:**
- Modify: `tests/extract/test_export_items.py`
- Modify: `tools/extract/export_items.py`
- Modify: `tools/extract/cli.py`

**Interfaces:**
- Produces: `load_crafting_notes(database_path: Path) -> Dict[str, str]`, khóa là `prefab_id` chữ thường.
- Produces: `build_item_export(catalog, assets, crafting_notes=None) -> Tuple[dict, dict]`.
- Produces: `export_items(database_path, catalog_path, assets_path, items_path, textures_path) -> None`.

- [ ] **Step 1: Viết test đỏ cho bộ lọc và hợp đồng schema 3**

Trong fixture, thêm `crafting_notes={"xd_sword": "Rèn một thanh kiếm thử"}` và kỳ vọng:

```python
items, textures = build_item_export(catalog, assets, crafting_notes)
self.assertEqual(items["schema_version"], 3)
self.assertNotIn("tu_tien:xd_special", {item["id"] for item in items["items"]})
self.assertNotIn("tu_tien:xd_fallback", {item["id"] for item in items["items"]})
self.assertIn("base_game:deerclops", {item["id"] for item in items["items"]})
self.assertEqual(
    next(item for item in items["items"] if item["id"] == "tu_tien:xd_sword")["craftingNote"],
    "Rèn một thanh kiếm thử",
)
```

- [ ] **Step 2: Chạy test để xác nhận đỏ**

Run: `python3 -m unittest tests.extract.test_export_items -v`

Expected: FAIL vì `build_item_export` chưa nhận lookup, schema vẫn là 2 và item thiếu tên Việt vẫn được xuất.

- [ ] **Step 3: Viết test đỏ cho khử trùng và xung đột SQLite**

Tạo SQLite tạm với bảng `game_text`, chèn hai hàng cùng khóa/cùng nội dung và xác nhận một lookup; sau đó chèn giá trị khác và kỳ vọng lỗi:

```python
self.assertEqual(load_crafting_notes(database), {"xd_sj_tlsq": note})
with self.assertRaisesRegex(ValueError, "STRINGS.RECIPE_DESC.XD_SJ_TLSQ"):
    load_crafting_notes(conflicting_database)
```

- [ ] **Step 4: Chạy test để xác nhận đỏ đúng nguyên nhân**

Run: `python3 -m unittest tests.extract.test_export_items.ExportItemsTests.test_loads_deduplicated_crafting_notes -v`

Expected: FAIL vì `load_crafting_notes` chưa tồn tại.

- [ ] **Step 5: Cài đặt loader, bộ lọc và schema 3 tối thiểu**

Trong `tools/extract/export_items.py`:

```python
RECIPE_DESC_PREFIX = "STRINGS.RECIPE_DESC."

def load_crafting_notes(database_path: Path) -> Dict[str, str]:
    grouped: Dict[str, set[str]] = {}
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "select text_key, value_vi from game_text "
            "where text_key like 'STRINGS.RECIPE_DESC.%' order by text_key, value_vi"
        )
        for text_key, value_vi in rows:
            grouped.setdefault(text_key, set()).add(value_vi)
    conflicts = [key for key, values in grouped.items() if len(values) > 1]
    if conflicts:
        raise ValueError(f"conflicting crafting note for {conflicts[0]}")
    return {
        key[len(RECIPE_DESC_PREFIX):].lower(): next(iter(values))
        for key, values in sorted(grouped.items())
    }
```

Thêm helper kiểm tra riêng `name.vi`, lọc `tu_tien` trước khi `_build_item_entry`, truyền lookup vào builder, thêm `craftingNote`, đổi `schema_version` thành 3 và để CLI truyền `database` vào `export_items`.

- [ ] **Step 6: Chạy test exporter đến xanh**

Run: `python3 -m unittest tests.extract.test_export_items -v`

Expected: PASS.

- [ ] **Step 7: Commit task**

```bash
git add tests/extract/test_export_items.py tools/extract/export_items.py tools/extract/cli.py
git commit -m "feat: filter Tu Tien item export and attach crafting notes"
```

### Task 2: Nâng hợp đồng frontend và tìm kiếm

**Files:**
- Modify: `app/lib/item-catalog.test.ts`
- Modify: `app/lib/item-catalog.ts`
- Modify: `app/lib/wiki-search.test.ts`
- Modify: `app/lib/wiki-search.ts`
- Modify: `app/components/wiki-search.test.tsx`

**Interfaces:**
- Consumes: item payload schema version 3 với `craftingNote: string | null`.
- Produces: `ItemListEntry.craftingNote: string | null` và tìm kiếm toàn văn bao gồm trường này.

- [ ] **Step 1: Viết test đỏ cho parser schema 3**

Đổi fixture sang schema 3, thêm `craftingNote`, xác nhận giá trị được parse; thêm case thiếu/sai kiểu và schema 2 bị từ chối:

```typescript
expect(parseItemPayload(validPayload)[0].craftingNote).toBe("Rèn một thanh kiếm thử");
expect(() => parseItemPayload({ ...validPayload, schema_version: 2 })).toThrow(
  /schema version 3/i,
);
```

- [ ] **Step 2: Chạy parser test để xác nhận đỏ**

Run: `npm test -- app/lib/item-catalog.test.ts`

Expected: FAIL vì parser chỉ nhận schema 2 và chưa có `craftingNote`.

- [ ] **Step 3: Cài đặt trường và validation tối thiểu**

Trong `ItemListEntry`, thêm:

```typescript
craftingNote: string | null;
```

Trong `parseItem`, dùng `nullableString(value.craftingNote, ...)`; trong `parseItemPayload`, yêu cầu `schema_version === 3`.

- [ ] **Step 4: Chạy parser test đến xanh**

Run: `npm test -- app/lib/item-catalog.test.ts`

Expected: PASS.

- [ ] **Step 5: Viết test đỏ cho tìm kiếm bằng ghi chú**

Thêm `craftingNote` vào toàn bộ fixtures `ItemListEntry` và kỳ vọng truy vấn chỉ có trong ghi chú trả về item Tu Tiên:

```typescript
expect(filterItems(items, "rèn một thanh kiếm", "all", "all").map((item) => item.id))
  .toEqual(["tu_tien:xd_sword"]);
```

- [ ] **Step 6: Chạy search test để xác nhận đỏ**

Run: `npm test -- app/lib/wiki-search.test.ts app/components/wiki-search.test.tsx`

Expected: FAIL vì `filterItems` chưa nối `craftingNote` vào searchable text.

- [ ] **Step 7: Cài đặt tìm kiếm và sửa fixtures TypeScript**

Thêm `item.craftingNote ?? ""` vào mảng searchable text trong `filterItems`; thêm `craftingNote: null` vào các fixture còn lại.

- [ ] **Step 8: Chạy test task đến xanh và commit**

Run: `npm test -- app/lib/item-catalog.test.ts app/lib/wiki-search.test.ts app/components/wiki-search.test.tsx`

Expected: PASS.

```bash
git add app/lib/item-catalog.ts app/lib/item-catalog.test.ts app/lib/wiki-search.ts app/lib/wiki-search.test.ts app/components/wiki-search.test.tsx
git commit -m "feat: parse and search crafting notes"
```

### Task 3: Trình bày ghi chú chế tạo trong modal

**Files:**
- Modify: `app/components/item-detail-modal.test.tsx`
- Modify: `app/components/item-detail-modal.tsx`

**Interfaces:**
- Consumes: `ItemListEntry.recipe` và `ItemListEntry.craftingNote`.
- Produces: ghi chú trong khối **Công thức** nếu có recipe; khối **Cách tạo / ghi chú chế tạo** nếu chỉ có note.

- [ ] **Step 1: Viết test đỏ cho cả hai trạng thái**

```typescript
it("shows the crafting note inside a runtime recipe panel", () => {
  render(<ItemDetailModal item={{ ...item, craftingNote: "Rèn bằng linh lực." }} onClose={vi.fn()} />);
  expect(screen.getByRole("heading", { name: "Công thức" })).toBeDefined();
  expect(screen.getByText("Rèn bằng linh lực.")).toBeDefined();
});

it("shows a note-only crafting panel without inventing ingredients", () => {
  render(<ItemDetailModal item={{ ...item, recipe: null, craftingNote: "Tiêu hao 10 điểm máu." }} onClose={vi.fn()} />);
  expect(screen.getByRole("heading", { name: "Cách tạo / ghi chú chế tạo" })).toBeDefined();
  expect(screen.queryByText("=")).toBeNull();
});
```

- [ ] **Step 2: Chạy modal test để xác nhận đỏ**

Run: `npm test -- app/components/item-detail-modal.test.tsx`

Expected: FAIL vì modal chưa render `craftingNote`.

- [ ] **Step 3: Cài đặt hai nhánh hiển thị tối thiểu**

Giữ nguyên công thức runtime hiện tại, thêm paragraph ghi chú trong khối nếu có. Sau khối recipe, render section note-only khi `!item.recipe && item.craftingNote`, với heading chính xác **Cách tạo / ghi chú chế tạo**.

- [ ] **Step 4: Chạy modal test đến xanh và commit**

Run: `npm test -- app/components/item-detail-modal.test.tsx`

Expected: PASS.

```bash
git add app/components/item-detail-modal.tsx app/components/item-detail-modal.test.tsx
git commit -m "feat: show crafting notes in item details"
```

### Task 4: Phát hành artifact, tài liệu và kiểm chứng toàn bộ

**Files:**
- Modify: `docs/data-extraction.md`
- Regenerate: `public/data/items.json`
- Regenerate if changed: `data/generated/item-textures.json`

**Interfaces:**
- Produces: payload schema version 3 có 381 item Tu Tiên được đặt tên và 105 ghi chú chế tạo.

- [ ] **Step 1: Cập nhật tài liệu hợp đồng**

Đổi mô tả `items.json` sang schema version 3, ghi rõ lọc Tu Tiên theo tên Việt, giữ nguyên base game, và mô tả `craftingNote`/quy tắc không suy đoán nguyên liệu.

- [ ] **Step 2: Chạy export**

Run: `python3 -m tools.extract.cli export`

Expected: `public/data/items.json` được tạo thành công, không có lỗi xung đột.

- [ ] **Step 3: Kiểm tra invariant dữ liệu**

Run:

```bash
node -e "const p=require('./public/data/items.json');const tt=p.items.filter(x=>x.namespace==='tu_tien');if(p.schema_version!==3||tt.length!==381||tt.some(x=>!x.name?.trim())||tt.filter(x=>x.craftingNote).length!==105)process.exit(1);console.log({schema:p.schema_version,tuTien:tt.length,notes:tt.filter(x=>x.craftingNote).length,recipes:tt.filter(x=>x.recipe).length})"
```

Expected: `{ schema: 3, tuTien: 381, notes: 105, recipes: 104 }`.

- [ ] **Step 4: Chạy toàn bộ kiểm thử và validator**

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS.

Run: `npm test`

Expected: PASS.

Run: `npm run lint`

Expected: PASS.

Run: `npm run build`

Expected: PASS.

Run: `python3 -m tools.extract.cli validate`

Expected: `hard_failures=0`.

- [ ] **Step 5: Kiểm tra diff và commit artifact**

Run: `git diff --check`

Expected: không có output.

```bash
git add docs/data-extraction.md public/data/items.json data/generated/item-textures.json
git commit -m "data: publish curated Tu Tien crafting notes"
```
