# Phàm Nhân Tu Tiên Runtime Wiki Implementation Plan

> **For agentic workers:** Execute task-by-task using the applicable `superpowers:executing-plans` workflow. The user explicitly selected GPT-5.6 Terra as implementer. The parent agent reviews the resulting work. Steps use checkbox syntax for tracking.

**Goal:** Xuất bản catalog item/công thức Phàm Nhân đầy đủ từ source hiện hành trong một trang dùng layout Solo Leveling/Linh Giới, gỡ route Phàm Nhân cũ.

**Architecture:** Extractor Python/Lua thu registrations và facts từ mod tích hợp, enrichment có bằng chứng, rồi xuất JSON deterministic. React đọc snapshot mới; browser dùng layout và component của Solo/Linh Giới, không đọc catalog/Solo snapshot cũ làm dữ liệu chuẩn.

**Tech Stack:** Python, Lupa Lua 5.1/LuaJIT có sẵn, Pillow/KTEX decoder có sẵn, Next.js 16.2.10, React 19, TypeScript, Tailwind 4, Vitest.

**Spec:** `docs/superpowers/specs/2026-09-22-pham-nhan-runtime-wiki-design.md`.

## Global Constraints

- Tên Phàm Nhân Tu Tiên; mod `mods/PhamNhanTuTien`; giữ prefab/component/save identifiers.
- Layout lấy từ Solo Leveling/Linh Giới. Dữ liệu mới lấy từ Phàm Nhân tích hợp.
- Gỡ `/pham-nhan-tu-tien/huong-dan`, `/pham-nhan-tu-tien/config`, `/tu-tien-ky` và redirect alias; giữ `/pham-nhan-tu-tien`.
- Không sửa các route wiki/mod khác. Không xóa source docs/icon được dùng chung.
- Giữ nguyên thay đổi concurrent; không sửa gameplay, không commit/push/deploy.
- Không dùng `app/data/tu-tien-ky.ts` hoặc `data/generated/solo-leveling.json` để quyết định catalog/recipes mới.
- Nội dung cũ chỉ làm enrichment sau khi kiểm chứng, có provenance và giải quyết conflict.
- Trước khi locate/read code dùng CodeGraph nếu `.codegraph` tồn tại; khi kết quả không đủ thì đọc file cụ thể.
- Đọc guide Next đang cài trước khi sửa frontend, đặc biệt layouts/pages và server/client components.
- Cập nhật ledger sau từng task: `docs/superpowers/reports/2026-09-22-pham-nhan-runtime-wiki-progress.md`.

## Review Focus

1. Recipe alias/overrides: cùng product không tạo item trùng, cùng recipe ID ghi đè đúng thứ tự (Task 2).
2. Loop, callback, disabled branch và module lạ: không rơi mất dữ liệu dưới dạng thành công giả (Tasks 1–3).
3. Cooking tag predicates, builder tag và blueprint: không biến điều kiện thành công thức số lượng sai (Task 3).
4. Docs cũ/affix bị xóa: không tái công bố đồ/cơ chế chỉ còn trong sách cũ (Task 4).
5. Deep-link, keyboard tooltip, trang cuối khi filter và route cũ 404 (Tasks 5–6).

## File boundaries và contract

Tạo package `tools/extract/pham_nhan/` gồm `__init__.py`, `discovery.py`, `sandbox.py`, `recipes.py`, `catalog.py`, `enrichment.py`, `assets.py`, `export.py`. Chia module nhỏ theo chức năng; thêm Lua shim `registration.lua` nếu cần để giữ Python readable.

CLI mới: `tools/build_pham_nhan_items.py`.

Đầu ra: `data/generated/pham-nhan-items.json`, `data/generated/pham-nhan-items-report.json`, icon dưới `public/pham-nhan/icons/`.

Metadata chọn lọc có kiểm chứng: `data/manual/pham-nhan-item-enrichment.json`. File này không được là danh sách item source of truth.

Frontend mới: `app/lib/pham-nhan.ts`, `app/components/pham-nhan-browser.tsx`, `app/components/pham-nhan-item-card.tsx`, `app/components/pham-nhan-item-detail.tsx`. Có thể tách thêm component cho topic theo độ dài.

Contract JSON (giữ tên trường thống nhất Python/TS):

```ts
type Evidence = { path: string; locator: string; sha256: string; kind: "runtime" | "doc" | "history" };
type Ref = { id: string; prefab: string | null; name: string; sprite: SpriteDescriptor | null };
type Recipe = {
  id: string; kind: "crafting" | "fusion" | "cooking" | "special";
  product: string; amount: number;
  ingredients: { prefab: string; name: string; amount: number; sprite: SpriteDescriptor | null }[];
  station: string; conditions: string[]; evidence: Evidence[];
};
type Item = Ref & {
  category: "equipment" | "material" | "food" | "seed" | "blueprint-token" | "structure" | "skin";
  description: string; details: string[];
  recipeStatus: "known" | "none" | "unknown"; recipes: Recipe[];
  acquisition: { text: string; source: Ref | null; evidence: Evidence[] }[];
  relatedIds: string[]; evidence: Evidence[];
};
type DocumentEntry = { id: string; title: string; text: string; evidence: Evidence[] };
type ConfigEntry = { key: string; label: string; description: string; default: string | number | boolean;
  choices: { label: string; value: string | number | boolean }[]; evidence: Evidence[] };
type AffixEntry = { id: string; name: string; description: string; details: string[];
  rarity: string; sprite: SpriteDescriptor | null; evidence: Evidence[] };
type Snapshot = {
  schemaVersion: 1; meta: { name: string; version: string; sourceHash: string };
  items: Item[]; references: Ref[]; affixes: AffixEntry[];
  guides: DocumentEntry[]; config: ConfigEntry[];
};
```

Identity: item thường `item:<prefab>`, skin `skin:<registered skin name>`; recipe ID giữ runtime registration ID; affix giữ key runtime. `SpriteDescriptor` dùng contract sẵn trong `app/lib/item-catalog.ts`. Không thay identifiers trong mod.

### Task 1: Kiểm kê source và lập bản đồ registration

**Files:** tạo `discovery.py`, `tests/extract/test_pham_nhan_discovery.py`, ledger. Đọc `modmain.lua`, `main/ttk_solo_bootstrap.lua`, `main/ttk_solo_source.lua`, `main/ttk_eva.lua`, `main/ttk_eva_source.lua`, `scripts/ttk_registration.lua`, `modinfo.lua`.

**Interfaces:** `discover_sources(mod_root: Path) -> dict` trả `entrypoint`, `modules`, `registrationFiles`, `prefabFiles`, `unresolved`, `sourceHashes`; module có `path`, `parent`, `order`, `status`, `reason`.

- [ ] Lưu baseline hash các file web định sửa và trạng thái git theo phạm vi; không in toàn bộ dirty tree.
- [ ] Đọc docs/source được chỉ ra; phát hiện modimport cả dạng dấu ngoặc, chuỗi trần, alias; require module chỉ trong mod và game module phân loại riêng. Dùng nhận diện Lua đủ để bỏ comments/string literals không phải code; không bắt mọi regex match như thực thi.
- [ ] Viết fixture temporary mod có nested imports, loop registration, chuỗi comment chứa import giả, nhánh `if false`, require chu kỳ và module không tồn tại. Assert comment không thành cạnh nạp, chu kỳ kết thúc, unknown nằm trong báo cáo.

```python
def test_missing_module_is_diagnostic(tmp_mod):
    result = discover_sources(tmp_mod)
    assert any(row["path"] == "main/missing.lua" for row in result["unresolved"])
```

- [ ] Chạy `python -m unittest discover -s tests/extract -p test_pham_nhan_discovery.py` ở trạng thái thiếu implementation rồi sau khi triển khai. Dùng `unittest.TestCase`/TemporaryDirectory cho fixture, không thêm pytest.
- [ ] Đối chiếu mọi callsite register recipe và mọi PrefabFiles provider của mod với discovery; ghi ngoại lệ khi static traversal chưa quyết định được. Ghi Task 1 và số coverage vào ledger.

### Task 2: Sandbox thu công thức thường và strings/atlas

**Files:** tạo `sandbox.py`, `recipes.py`, `registration.lua`, `tests/extract/test_pham_nhan_recipes.py`.

**Interfaces:** `collect_registrations(mod_root: Path, discovery: dict) -> dict` trả `recipes`, `names`, `descriptions`, `atlases`, `prefabs`, `diagnostics`, `loadedSources`. `normalize_recipes(registrations: dict) -> list[dict]` xuất Recipe contract.

- [ ] Xây env Lua chỉ có hàm toán/chuỗi/bảng và API ghi nhận; remove `os`, `io`, `package`, `dofile`, `loadfile`, Python bridge. Chỉ Python loader được đọc file đã validate nằm trong mod. Bound execution bằng instruction budget/hook hoặc process timeout; thiếu API phải có diagnostic.
- [ ] No-op chỉ hook game không cần cho đăng ký và đã biết semantics; thu callback đăng ký để xử lý khi có lý do. Không dùng blanket proxy trả mọi giá trị hoặc try/except nuốt module fail. Definition module cần thực thi theo thứ tự nguồn thật.
- [ ] Ghi `AddRecipe2` vào registry theo recipe ID rồi áp dụng cập nhật cuối; Ingredient thu amount/atlas/image. Giữ tech, output product/count, blueprint/nounlock/builder_tag.
- [ ] Test fixture `AddRecipe2("variant_a",...,{product="target"})` và `variant_b` thành hai recipes cùng product; `variant_a` bị override chỉ giữ bản cuối. Test loop tạo 3 recipe. Test unsafe I/O và infinite loop thất bại có tên file.
- [ ] Test source thật:

```python
recipes = normalize_recipes(collect_registrations(mod_root, discover_sources(mod_root)))
tally = [r for r in recipes if r["product"] == "hh_treasure_tally"]
self.assertEqual(len(tally), 2)
self.assertEqual(next(r for r in recipes if r["product"] == "wb_enhancegem")["amount"], 8)
pond = next(r for r in recipes if r["product"] == "hh_hac_nguyet_ho")
self.assertIn({"prefab": "marble", "amount": 10},
              [{"prefab": i["prefab"], "amount": i["amount"]} for i in pond["ingredients"]])
```

- [ ] Chạy suite Task 2. Đối chiếu `main/hh_recipe.lua`, `scripts/util/eva_recipes.lua`, `main/ttk_armor_set.lua`, `main/ttk_tinhlakiem.lua`, `main/ttk_elemental_swords.lua`, `main/ttk_vinhhangthanhoa.lua`, `scripts/ttk_registration.lua` và các batch garden/building/houses/rituals. Log mọi callsite chưa xử lý.

### Task 3: Catalog toàn bộ item, custom recipe và nguồn nhận

**Files:** tạo `catalog.py`, bổ sung `recipes.py`, `tests/extract/test_pham_nhan_catalog.py`.

**Interfaces:** `build_catalog(mod_root: Path, registrations: dict) -> tuple[list[dict], dict]` trả items sơ bộ + coverage. Thu cả prefab variants tạo bằng factory, blueprint và skins registry.

- [ ] Kiểm kê candidate từ registered prefab constructors/factories, product/ingredient, inventory facts, shops, drops, rewards, starting items và skins. Có active provider và bằng chứng trước khi đưa item vào; ingredient base game thu vào references nếu không có thay đổi mod.
- [ ] Phân loại Item contract, excluded có lý do. Không bỏ cả họ `hh_`/`wb_`/`nn_`/`ttk_` chỉ vì tên lạ; không biến mọi icon/STRINGS thành item. Mobs/bosses chỉ source refs.
- [ ] Đọc custom dung hợp trong `main/ttk_solo_source.lua` (callback quanh dòng 1115–1125, điều kiện Has/ConsumeByName/GiveItem) và wiring container liên quan; thu hai Phúc Lạc Dược nâng cấp từ code. Không hardcode công thức dựa trên Solo JSON hoặc Wiki.txt.
- [ ] Thu `scripts/ttk_luoshen_fooddefs.lua`, `main/ttk_luoshen_food.lua`, spice/cooker registrations. Giữ predicate dạng điều kiện đọc được và bằng chứng; recipe cooking không gán số lượng giả cho chất thịt.
- [ ] Nguồn nhận: `scripts/ttk_boss_defs.lua`, `scripts/ttk_boss_collectible_defs.lua`, loot/reward tables, `scripts/enums/hh_items.lua`, guild/dungeon shop defs và starting inventory EVA. Special shop tokens có key riêng phải có ID/key minh bạch, không giả làm prefab spawnable.
- [ ] Skin dựa vào registered `skins_manifest.json`/`scripts/ttk_skin_data.lua` và active base; liên kết base item, phân biệt cosmetic khỏi craftable product.
- [ ] Test item rơi không recipe vẫn có mặt; `yellowgem` có mod recipe; `ttk_xshj_blueprint` và boss core/summon có mặt; `eva_scythe` có builder condition; hai món Lạc Thần khác điều kiện thịt; helpers/placer/boss không nằm Item; skin không trùng item base; recipe ingredients đều resolve.
- [ ] Chạy suite catalog, đối chiếu báo cáo candidate từng họ. Membership không được đọc legacy TS. Lưu danh sách unresolved cụ thể để Task 4 xử lý.

### Task 4: Enrichment có bằng chứng, affix/config mới và icon

**Files:** tạo `enrichment.py`, `assets.py`, metadata manual, `tests/extract/test_pham_nhan_enrichment.py`, `tests/extract/test_pham_nhan_assets.py`.

**Interfaces:** `enrich_catalog(mod_root: Path, items: list[dict], registrations: dict) -> dict` trả `items`, `references`, `affixes`, `guides`, `config`, `diagnostics`. `resolve_assets(mod_root: Path, payload: dict) -> tuple[dict, dict]` trả payload sprite + mapping output PNG tới texture bytes/path.

- [ ] Đọc 19 chủ đề ở `app/data/pham-nhan-guides.json` và các source docs tương ứng. Dùng nguyên liệu/công dụng từ docs chỉ sau đối chiếu source. Ưu tiên boss drops, seed-tree, mines, garden, armor, herbs, houses, structures; lưu history evidence chỉ cho quyết định đã xác nhận.
- [ ] Kiểm tra tên/mô tả từ STRINGS.NAMES runtime rồi bổ sung mô tả người chơi. Metadata override ghi prefab, trường, giá trị, evidence file/locator/hash; không giữ các con số cũ nếu hash nguồn đổi.
- [ ] Affix đọc `scripts/enums/hh_enchant.lua`, `scripts/combat/` và tuning hiện hành. Phân biệt registry key và tên dịch: chỉ loại cơ chế/key đã bị gỡ, không loại item đang hoạt động chỉ vì tên giống cơ chế cũ (ví dụ `nkGem` có tên “ban phúc” trong registry châu báu cần kiểm tác dụng thực). Config đọc `modinfo.lua` trong sandbox. Chỉ xuất options thật; không tái thêm option EVA đã bị gỡ. Không gọi `buildPhamNhanAffixes(soloLevelingData)`.
- [ ] Hướng dẫn mới có ID trong sidebar/hash của trang chính. Text `book-*` chỉ đưa phần đã kiểm chứng; loại mẫu markup `[ITEM]`/`[TABLE]` khỏi bản trình bày thô bằng cấu trúc/render phù hợp. Ghi conflict report cho bất đồng chưa giải quyết.
- [ ] Icon resolve exact atlas path + element name; image alias có bằng chứng; dùng decoder `tools/extract/publish_solo_leveling_assets.py` và parser atlas sẵn. Không dùng phần tử đầu atlas cho mọi item. Namespace PNG mới `/pham-nhan/icons/<content hash>.png`; vanilla dùng local sprites đã có.
- [ ] Test atlas hai phần tử khác UV, image không trùng prefab, missing asset vẫn giữ item + diagnostic; removed affix/set không quay lại từ docs; phantom doc-only item không thành active item; enrichment không thay ingredient runtime.
- [ ] Chạy hai suite. Tổng hợp riêng icon thật sự không tồn tại và icon extractor chưa resolve; loại thứ hai phải sửa trước nghiệm thu.

### Task 5: Export deterministic, validation và CLI

**Files:** tạo `export.py`, `tools/build_pham_nhan_items.py`, snapshots, `tests/extract/test_pham_nhan_export.py`; cập nhật `docs/pham-nhan-wiki.md`.

**Interfaces:** `build_snapshot(mod_root: Path) -> tuple[dict, dict, dict]` trả Snapshot, report, assets. `validate_snapshot(snapshot: dict, report: dict) -> None`. CLI `--mod-root`, `--output`, `--report`, `--check`; defaults source/dest như file boundaries. `--check` không ghi file.

- [ ] Build thuần đọc trả objects; validate trước ghi. Report gồm active source hashes, loaded/unsupported modules, candidate/included/excluded/unresolved, recipe counts theo file/kind, missing sprites, conflicts. Không có timestamp biến động phá deterministic output.
- [ ] Validate duplicate IDs, dangling ingredient/related refs, số lượng >0, evidence tồn tại, sprite path tồn tại sau publication, JSON không NaN. Phân biệt status unknown với none. Fail nếu unresolved registration làm coverage không chứng minh được; chỉ chấp nhận ngoại lệ explicit kèm lý do.
- [ ] Publish asset/snapshot/report qua tệp staging và atomic replace trong filesystem cùng volume. `--check` so bytes kỳ vọng với hiện tại và nonzero nếu stale. Tệp source thay đổi giữa build/publish làm build thất bại rõ ràng.
- [ ] Test build hai lần ra bytes giống nhau; corrupt input không ghi đè snapshot hợp lệ; `--check` không đổi mtime; thêm recipe fixture làm stale check thất bại; legacy data không được import; source hash thay đổi được phản ánh.
- [ ] Chạy `python -m unittest discover -s tests/extract -p test_pham_nhan_*.py`, publish source thực rồi chạy `--check`. Báo tổng item/công thức/icon lấy từ output thật.
- [ ] Docs ghi nguồn chuẩn, lệnh build/check, cách bổ sung metadata, xử lý unresolved; nói rõ builder cũ không cập nhật catalog mới. Không chạy builder cũ lên Config/Hướng dẫn concurrent.

### Task 6: Browser theo layout Solo/Linh Giới và xóa route cũ

**Files:** tạo TS/component trong file boundaries và tests tương ứng; sửa `app/pham-nhan-tu-tien/page.tsx`, `page.test.tsx`, `next.config.ts`, docs. Xóa chính xác `app/pham-nhan-tu-tien/huong-dan/page.tsx`, `app/pham-nhan-tu-tien/config/page.tsx`, `app/tu-tien-ky/page.tsx`, `app/tu-tien-ky/page.test.tsx`, `app/components/pham-nhan-nav.tsx` sau kiểm tra references. Component/data cũ chỉ gỡ nếu không còn consumer; không cascade xóa công việc khác.

**Interfaces:** `PhamNhanBrowser({data}: {data: Snapshot})`; `filterPhamNhanItems(items, query, category)`; hash `#sec=items&item=<encoded ID>`, `#sec=affixes`, `#sec=guides`, `#sec=config`. Item mặc định, unknown hash fallback an toàn. Sidebar đề mục cùng dữ liệu mới; guides/config không link route đã gỡ.

- [ ] Đọc `node_modules/next/dist/docs/01-app/01-getting-started/03-layouts-and-pages.md` và `05-server-and-client-components.md` trước khi viết JSX.
- [ ] Dùng shell/page của Solo làm khung, sidebar 220px, responsive ngang mobile; giữ DstHero style nhưng copy/stats dữ liệu mới. Không PhamNhanNav/banner cũ/Affix strip.
- [ ] Browser có Item/Affix/Hướng dẫn/Config. Item filter theo category contract; tìm không dấu trong tên, prefab, mô tả, ingredient và nguồn nhận. Page size 12 như Solo; reset trang khi filter đổi.
- [ ] Card Item bắt chước `SoloLevelingContentCard` cùng `GameSprite` và `RecipeIngredients`; tên/prefab header, recipe options và nơi chế tạo. Với cooking conditions hiển thị phần điều kiện; không có recipe vs unknown khác copy. Output >1 ghi cạnh nhãn công thức, không thêm result box.
- [ ] Chi tiết/dialog theo Linh Giới, reference ingredient/related item mở đúng mục, Escape đóng và focus trở về opener. Tooltip tên hỗ trợ focus thật; span chỉ `title` không đáp ứng keyboard nên dùng button/reference hoặc focusable element scoped, tránh làm hỏng Solo.
- [ ] Page chỉ import JSON mới và lib mới. Affix lấy data.affixes, Config data.config, Hướng dẫn data.guides. Không import legacy TS/Solo JSON/guide snapshot cũ lúc render.
- [ ] Xóa file route và redirect alias bằng apply_patch, cập nhật active links/test. URL asset `/tu-tien-ky/icons/` không phải route page: giữ asset đang dùng bởi các phần khác.
- [ ] Behavior tests: mặc định Item; search `ha pham linh thach`; hai công thức cùng Tầm Bảo Quyển Trục; output 8; unknown vs none; tìm item không recipe; filter về trang 1; deep link item ở trang sau; invalid hash; keyboard tooltip/dialog/focus; Affix không nguồn Solo cũ; không link 3 route đã bỏ.

```tsx
render(<PhamNhanBrowser data={fixture} />);
fireEvent.change(screen.getByRole("searchbox", { name: "Tìm trong Phàm Nhân" }),
  { target: { value: "ha pham linh thach" } });
expect(screen.getByRole("heading", { name: "Hạ Phẩm Linh Thạch" })).toBeDefined();
expect(screen.queryByText("Sản phẩm nhận được")).toBeNull();
```

- [ ] Tests route kiểm absence file và redirect config; HTTP smoke build/serve ở Task 7 phải xác nhận 404 thực. Không sửa header key cũ chỉ vì nó tên `tu-tien-ky` nếu href vẫn đúng; chỉ đổi khi cần và có scope rõ.

### Task 7: Nghiệm thu coverage, regression và bàn giao

**Files:** báo cáo `docs/superpowers/reports/2026-09-22-pham-nhan-runtime-wiki-acceptance.md`, ledger và plan checkboxes.

- [ ] Tự đối chiếu mọi recipe registration file tìm được với report. Chọn mẫu từng nguồn TTK, Solo tích hợp, EVA, cooking, fusion, skin, modified vanilla, drop/shop để kiểm chính xác source → snapshot → UI. Không dùng một danh sách seed tự đặt làm bằng chứng “toàn bộ”.
- [ ] Chạy extractor suite và `python tools/build_pham_nhan_items.py --check`.
- [ ] Chạy `npm test -- --run`, `npx tsc --noEmit`, `npm run lint`, `npm run build` theo môi trường. Nếu baseline test lỗi không liên quan, chỉ rõ tên và evidence; không sửa ngoài scope.
- [ ] Browser desktop/mobile bằng công cụ browser có sẵn: Item/Affix/guide/config, nhiều công thức, focus, dialog, ảnh crop/UV, search không dấu, pagination, deep link. Xác nhận 3 route cũ HTTP 404 và hai trang Solo/Linh Giới vẫn hoạt động. Nếu không có browser khả dụng, ghi QA visual chưa chạy.
- [ ] `git diff --check` trong đúng file task; đọc diff, so baseline để bảo toàn concurrent work. Không stage/commit/push.
- [ ] Báo cáo số liệu thật: items theo loại, recipes theo kind/file, skins, affixes, missing icons, excluded/unresolved và cách xử lý từng loại; kèm test commands/results, file list và các hạn chế còn lại.
- [ ] Terra gửi report cho parent để review. Parent xác nhận coverage + behavior trước khi tuyên bố hoàn tất.

## Handoff đã chọn

Người dùng đã chọn Terra; không cần hỏi lại model hoặc xin duyệt lại các lựa chọn đã chốt. Terra triển khai tuần tự các task, báo milestone/khó khăn với parent, không tạo task Codex mới và không tự spawn thêm agent. Parent xử lý review và quyết định cần sửa theo spec.

Plan được viết dựa trên source đang có tại thời điểm khảo sát. Nếu source concurrent thay đổi, cập nhật hash/discovery và ghi quyết định vào ledger, không đóng băng dữ liệu vào snapshot cũ.
