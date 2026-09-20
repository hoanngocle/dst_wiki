# Tu Tiên Ký v0.1.0 — báo cáo triển khai

Ngày: 2026-09-19

## Phạm vi

- Project: `C:/Users/hoanc/company/dst_wiki`
- Source chỉ đọc: `mods/mod_steam/3235319974`, `mods/mod_steam/3780347550`, cùng `scripts.zip` của game để đối chiếu API.
- Source mới: `mods/TuTienKy`
- Artifact: `mods/dist/TuTienKy_v0.1.0.zip`
- Plan: `docs/superpowers/plans/2026-09-19-tu-tien-ky-v0.1.0.md`
- Spec: `docs/superpowers/specs/2026-09-19-tu-tien-ky-v0.1.0.md`

Không sửa mod nguồn, Steam Workshop đang hoạt động, Solo Leveling, FastTravel, website, save hoặc file game. `mods/` đã là untracked trước task; không git add, commit, clean hoặc reset.

## Trạng thái task

- Task 1 — hoàn tất: đọc AGENTS/plan/spec, xác nhận output cũ không tồn tại, kiểm kê và hash 14 asset nguồn.
- Task 2 — hoàn tất: metadata, tài nguyên đổi path, defs và bốn prefab linh thạch.
- Task 3 — hoàn tất: atlas/minimap/container/strings, ba recipe nâng phẩm và recipe bàn.
- Task 4 — hoàn tất: prefab bàn, trang trí món, preserver, hammer, nâng cấp/save/load/collapsed chest.
- Task 5 — hoàn tất: phân loại và thưởng loot phía server qua world `entity_death`.
- Task 6 — hoàn tất bàn giao: tài liệu, rà mã và ZIP đã xong; compile cú pháp chưa hoàn tất và không chạy game/test suite.

## Provenance tài nguyên nguồn

| File nguồn dưới `3235319974` | Bytes | SHA256 |
|---|---:|---|
| `anim/xd_hhlmz.zip` | 158063 | `EAD5B88B1569349BDF44E5CCFB1B88497E5D2AFA7CCB31F9D1E21CC2E428A253` |
| `anim/xd_lingshi.zip` | 39724 | `DA4D05CF50A47290EBADBEEFD1392F6CD0C781C7F8BE2F7726D9AE059B00FC46` |
| `images/inventoryimages/xd_hhlmz.xml` | 162 | `BB208274F031FD53CA32C3FFFA7819D12570D96B05C5C34B0C803216B7BC92F8` |
| `images/inventoryimages/xd_hhlmz.tex` | 5566 | `06B5DD709B69F2063AC566A2D08E027E3B4BAD706E2920FCC028E5531D221F53` |
| `images/inventoryimages/xd_lingshi1.xml` | 168 | `9A7AA7EC45027EA285762517E73AE8F8D6B38CE427B0B464388FDD54DE55E950` |
| `images/inventoryimages/xd_lingshi1.tex` | 5566 | `67EF5F850C6E54B4EFD567FFEC21720CCEDC95C8278021A9CED90CB8F242D5A5` |
| `images/inventoryimages/xd_lingshi2.xml` | 168 | `34A4F8D96E1D061EB305D9DA3F9021ECE9A4D3E4525BA3F9694C607117DDE425` |
| `images/inventoryimages/xd_lingshi2.tex` | 5566 | `9EC60AF9ACA24E84B281545829DE3B4B72800822876AFF21EDECA46D90628436` |
| `images/inventoryimages/xd_lingshi3.xml` | 168 | `A376B418006BF5948031D89D160F6218D549E263F9983FA8E937EBC4E9BC35D4` |
| `images/inventoryimages/xd_lingshi3.tex` | 5566 | `5EC7B115A325E6192423A0076923B6ABDA91759FC5866851827C74D09B4335F9` |
| `images/inventoryimages/xd_lingshi4.xml` | 168 | `6483CCA23DEBEDAF495093A40ABC8F9F2B6343DC9609F8CF39D72D924E25316C` |
| `images/inventoryimages/xd_lingshi4.tex` | 5566 | `81898A6AAE288FC236EF13F22F3B7A311427902E51BD8F7636F2FD2D81D58717` |
| `images/map_icons/xd_hhlmz.xml` | 162 | `BB208274F031FD53CA32C3FFFA7819D12570D96B05C5C34B0C803216B7BC92F8` |
| `images/map_icons/xd_hhlmz.tex` | 5566 | `06B5DD709B69F2063AC566A2D08E027E3B4BAD706E2920FCC028E5531D221F53` |

Đối chiếu copy: hai anim ZIP và sáu TEX đầu ra giữ nguyên SHA256/byte; XML mới chỉ đổi Texture filename và Element name từ `xd_` sang `ttk_`.

## Rulings

- Ruling: không tạo worktree — `mods/` chứa nguồn copy untracked và output là folder mới; worktree sẽ không mang nguồn này sang. Chi phí nếu sai: cách ly dựa vào đường dẫn/allowlist thay vì Git, nên mọi bước copy và ZIP phải kiểm tra đích tuyệt đối.
- Ruling: không áp dụng TDD/test suite — người dùng yêu cầu rõ không viết/chạy test, được plan ghi là override. Chi phí nếu sai: không có bằng chứng runtime/gameplay tự động; chỉ có rà tĩnh, parse cú pháp nếu runtime sẵn và kiểm tra archive.
- Ruling: dùng một listener `entity_death` trên world thay cho `AddPrefabPostInitAny` + listener từng prefab — `health.lua` phát world event trước entity event vì entity có thể bị listener khác xóa; `explosive.lua` cũng phát world event trước remove. Bỏ `cause == "file_load"` vì `health:OnLoad` có thể phát death. Chi phí nếu sai: một nguồn death modded không phát world event sẽ không được thưởng, nhưng không có periodic scan hoặc global component patch.
- Ruling: mở lại chốt thưởng bằng `pre_health_setval` chỉ trên nạn nhân đã được thưởng khi `old_health <= 0` và `val > 0` — sự kiện này bao phủ cả hồi sinh dùng SetVal trực tiếp, trong khi `healthdelta` chỉ phát từ DoDelta. Chi phí nếu sai: cơ chế hồi sinh custom bỏ qua Health:SetVal sẽ cần tích hợp riêng.
- Ruling: không thêm bảng tên boss Solo dự phòng — các boss Solo quan sát được (`hh_beru_dungeon`, `minotau`) có `epic`, và Beru còn có `hh_tags.boss_monster`; không đoán prefab chưa có bằng chứng. Chi phí nếu sai: boss custom không mang bất kỳ tag/field đã hỗ trợ sẽ được phân loại theo tag quái thường hoặc không được thưởng.
- Ruling: thêm allowlist quái thường `killerbee` và `mosquito` — source vanilla xác nhận cả hai có health/combat và hành vi thù địch nhưng không có tag `monster`/`hostile`; không mở rộng theo tag insect/animal để tránh thưởng sinh vật trung lập. Chi phí nếu sai: các prefab vanilla/modded thù địch khác cũng thiếu tag sẽ cần bổ sung có bằng chứng.
- Ruling: khi bàn overstack nằm ở điểm không passable, mỗi lần đập/giải thể chỉ drop số stack có giới hạn rồi giữ lại bàn bằng `workleft=1`/`no_delete_on_deconstruct` nếu còn đồ — tránh cả mất phần còn lại kiểu nhánh ocean vanilla và vòng spawn hàng triệu entity. Chi phí nếu sai: người chơi phải giải phóng đồ theo nhiều lượt hoặc đưa bàn về vị trí hợp lệ trước khi collapsed chest có thể chứa phần dư.

## Đối chiếu Review Focus

1. Registry chạy ở cả client/server trước mọi master guard; loot installer tự thoát ở non-master và chạy trên world master của từng shard, không dùng `GetIsMasterShard`.
2. Classifier xét boss trước quái thường, loại companion/follower/shadow/structure và phase 1–2 của Alter Guardian; mỗi death có một chốt duy nhất trước khi spawn.
3. Component container/upgradeable chịu trách nhiệm save/load. `OnLoad` của bàn áp lại infinite stack sau component load; `OnLoadPostPass` dựng lại food symbols. Loot bỏ death do `file_load`; hồi sinh thật mở chốt từ `pre_health_setval`.
4. Chi phí đổi nằm ở một bảng `100/10/10`. Vanilla builder dùng `inventory:Has(..., true)` và `GetCraftingIngredient`, nên lượng 100 trải nhiều stack không cần hook; ingredient modifier chuẩn của game vẫn có thể áp dụng như recipe bình thường.
5. Lookup trang trí xử lý recipe nil và spice suffix, món không biết build chỉ bỏ hình. Nhánh overstack dùng `DropEverything(nil,true)`, `DropEverythingUpToMaxStacks` và `collapsed_treasurechest:SetChest`; không dùng animation open/close/hit/rebuild không tồn tại trong build bàn.

## File tạo/thay đổi

- Toàn bộ file mới dưới `mods/TuTienKy`.
- Báo cáo mới `docs/superpowers/reports/2026-09-19-tu-tien-ky-progress.md`.
- Artifact mới `mods/dist/TuTienKy_v0.1.0.zip`.

Không có file nào trong `mods/mod_steam`, Steam Workshop thật, Solo, FastTravel, website hoặc save được thay đổi.

## Xác nhận và giới hạn

- Static review: Sol High triển khai; coordinator đọc độc lập và yêu cầu sửa các lỗi env Lua, MAXITEMSLOTS, overflow và nhận diện quái. Các sửa đổi đã được đọc lại.
- Lua syntax-only: chưa hoàn tất; không có kết quả compile để tuyên bố hợp lệ. Không cài dependency.
- ZIP root/allowlist/traversal/CRC: 26 file, một root TuTienKy, CRC hợp lệ, nội dung từng file khớp source; sáu XML trỏ đúng TEX.
- Không chạy game, không chạy test suite và không xác nhận runtime multiplayer/Solo trong game theo yêu cầu người dùng.

### Artifact cuối

- Path: `mods/dist/TuTienKy_v0.1.0.zip`
- Size: 221294 bytes
- SHA256: `456d49cc5c5276f02863998c8452550041c8b5a5087a3e935e0be03bae4f0bcc`

## Phân công cuối

GPT-5.6 Sol (high) triển khai mã nguồn và tài liệu. Coordinator lập plan, đối chiếu API game, rà mã độc lập và hoàn tất ZIP/report sau khi dừng bước xác nhận cú pháp chưa hoàn tất. Không nhận định rằng mod đã chạy thành công trong game.
