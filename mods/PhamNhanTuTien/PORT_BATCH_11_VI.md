# Báo cáo chuyển 11 món: cây, hoa, kho và nghi thức

## Phạm vi và nguồn đối chiếu

Đợt này chỉ chuyển 11 món đã chốt từ `mods/mod_steam/3235319974`. Hai đèn
`xd_jwtcd`, `xd_lyd`, ba mỏ `xd_rock1..3`, Sa Đường và Đan Lô không thuộc
phạm vi. Các tệp nguồn chính đã đọc/trích tĩnh là:

- `scripts/prefabs/xd_trees.lua`, `xd_flowers.lua`, `xd_luoshen_flower.lua`,
  `xd_luoshen_items.lua`, `xd_lbx.lua`, `xd_lgzbh.lua`, `xd_mg.lua`,
  `xd_sj_kls.lua`, `xd_lbjlt.lua`;
- `scripts/main/recipes.lua`, `containers.lua`, `actions.lua`, `components.lua`,
  `stategraph.lua`, `prefabpostInit.lua`, `fabao.lua`, `import.lua`;
- bảng skin từ `scripts/main/xd_skin_license_v2.lua`,
  `xd_skin_license_v3.lua` và tài nguyên `anim/`, `images/` của mod nguồn;
- prefab/component chuẩn DST được đối chiếu trong
  `data/databundles/scripts.zip` của bản game cục bộ.

Không chạy loader mã hóa của mod nguồn. Mọi hành vi bên dưới được chuyển
thành prefab/module `ttk_` độc lập và không `require` mod nguồn hay Solo.

## Bản đồ phụ thuộc và thay đổi khi chuyển

| Món đích | Nguồn và cách dùng | Recipe/trạm | Sản vật, FX và lưu trạng thái |
|---|---|---|---|
| `ttk_tree_ls` Lam Sam | Factory `xd_trees.lua`; che mưa, nhiệt vùng | Gỗ Sống 4, Ngọc Xanh Dương 2, Hạ Phẩm 1; Máy Luyện Kim | 1 Ngọc Xanh Dương sau 3.360 giây + 0–100 giây; chu kỳ dùng `periodicspawner` |
| `ttk_tree_yxs` Ngân Hạnh | Factory `xd_trees.lua`; cùng nhánh cây ngọc | Gỗ Sống 4, Ngọc Cam 2, Hạ Phẩm 1; Máy Luyện Kim | 1 Ngọc Cam mỗi chu kỳ; có skin JQS |
| `ttk_flower_ll` Linh Lan | Factory `xd_flowers.lua`; aura và gọi bướm | Bướm 2, Cành Cây 15, Hạ Phẩm 1; Máy Khoa Học | 40% sinh 1 bướm mỗi bình minh ngoài mùa đông/hang |
| `ttk_flower_md` Mẫu Đơn | Factory `xd_flowers.lua` | Bướm 2, Ngọc Đỏ 3, Hạ Phẩm 1; Máy Khoa Học | Cùng aura/bướm; có skin RJFG |
| `ttk_flower_mlh` Mộc Lê Hoa | Factory `xd_flowers.lua` | Bướm 2, Ngọc Xanh Lá 1, Hạ Phẩm 1; Máy Khoa Học | Cùng aura/bướm |
| `ttk_luoshen_hua` Lạc Thần Hoa | `xd_luoshen_flower.lua`, `xd_luoshen_items.lua`; năm giai đoạn | Hạt: Cánh Hoa 60, Thịt Lá 3, Trung Phẩm 1; Máy Luyện Kim | Dùng Hạ Phẩm để tăng giai đoạn; giai đoạn 3 có nhiệt 25/bán kính 15 và aura; giai đoạn 5 có kho 3×3, sinh Lạc Thần Hoa Nhân (`ttk_luoshen_huayin`) mỗi ngày. Đào trả 10 Cành Cây + 8 Cánh Hoa. Lưu giai đoạn, lượt hái lại và kho |
| `ttk_lbx` Linh Bảo Sương | `xd_lbx.lua`; kho 20 ô nhân bản | Đá Cắt 10, Ván 5, Hạ Phẩm 20; Máy Khoa Học | Khi có ≥12 ô và còn chỗ, mỗi 15 ngày sao một món ngẫu nhiên, chồng sao tối đa 20. Giới hạn nguồn là 3 chiếc theo shard/world; bộ đếm phục hồi theo vòng đời prefab. FX `ttk_hyf_fullfx`, `ttk_hyf_frontfx`; bản nhỏ được đăng ký để công trình khác dùng |
| `ttk_lgzbh` Lưu Quang Châu Bảo Hạp | `xd_lgzbh.lua`, filter trong `containers.lua`; kho 20 ô | Vàng 10, Cẩm Thạch 4, Hạ Phẩm 4; Máy Khoa Học | Nhận tag `gem` (nên Ngọc Lấp Lánh vẫn hợp lệ), bốn phẩm linh thạch và `hermit_cracked_pearl`; hiệu ứng `ttk_lgzbh_fx`; nâng chồng một lần bằng mảnh vương miện; lưu kho theo component chuẩn |
| `ttk_mg` Mật Quán | `xd_mg.lua`, filter trong `containers.lua`; kho 20 ô | Bướm 10, Đá 5, Dây 2, Hạ Phẩm 10; Máy Khoa Học | Chỉ nhận `bandage`, `bee`, `beeswax`, `royal_jelly`, `spice_sugar`, `honey`, `honeycomb`, `jellybean`; `preserver = -0.2`; nâng chồng một lần |
| `ttk_sj_kls` Khô Lâu Sơn | `xd_sj_kls.lua` và nhánh action/map; nguồn gắn điều kiện nhân vật | Đá Cắt 6, Mảnh Xương 3, Ngọc Tím 1, Trung Phẩm 1; Shadow Manipulator | Bản độc lập cho mọi nhân vật: trả 25 tinh thần, vào trạng thái 20 giây rồi chọn điểm đã khám phá trên bản đồ. Máy chủ kiểm tra đúng công trình, khoảng cách, đích cùng shard và passable; không nhập nhân vật/triệu hồi không liên quan |
| `ttk_lbjlt` Linh Bảo Tế Luyện Đài | `xd_lbjlt.lua`, `fabao.lua`, `components.lua`; nguồn tăng `xd_level` cho pháp bảo nguồn | Đá Lửa 3, Đá Cắt 6, Trung Phẩm 1; Shadow Manipulator | Một ô chỉ nhận `lucmachthankiem`/`vanhonphien`; 100% thành công, chi phí Thượng Phẩm cấp 0–8: 1/1/1/3/6/12/33/99/300. Mỗi cấp +5% sát thương, tối đa 9; lưu trên chính pháp bảo. FX `ttk_lbjlt_fx` |

### Lạc Thần Hoa và phụ thuộc thực phẩm

Nguồn tạo ban đầu của Lạc Thần Hoa phụ thuộc nhân vật Lạc Thần, nên bản chuyển
thêm recipe hạt độc lập; không nhập nhân vật. `ttk_luoshen_huayin` là thực phẩm
đủ chức năng: +10 máu, +5 no, +10 tinh thần, `PERISH_FAST`, nhận tag cắm bình
và đồ chơi mèo. Hoa Nhân cũng được đăng ký làm nguyên liệu Nồi Hầm: hỗn hợp
không thịt tạo `ttk_luoshen_qingshu` (+200 máu, +42,5 no, +80 tinh thần), còn
hỗn hợp có thịt tạo `ttk_luoxiang_pengrou` (+10 máu, +75 no, +62,5 tinh thần).
Phanh Nhục cho buff 480 giây, hồi 2 máu mỗi lần đánh trúng mục tiêu còn sống.
Các recipe nhân vật khác chỉ dùng Hoa Nhân làm nguyên liệu (`xd_luoshen_yin`,
`xd_luoshen_jiangren` và đồ Lạc Thần khác) không phải sản vật của cây nên không
được kéo vào. Không có prefab rỗng thay cho sản vật.

### Tế luyện và tương thích Solo

Nguồn chỉ nhận hai pháp bảo riêng của nguồn thông qua component cấp nhân vật.
Bản chuyển gắn cấp nghi thức vào hai pháp bảo đã có trong Tu Tiên Ký. Lục Mạch
Thần Kiếm tính lại sát thương vật lý và planar khi gọi kiếm; Vạn Hồn Phiên áp
hệ số vào sát thương Hồn Vệ. Các adapter không gọi Solo, nên hành vi có hiệu lực
cả khi Solo không cài; carrier Solo hiện có vẫn được giữ nếu mod đó đang bật.

## Skin thuộc 11 món

Sáu skin thực sự đăng ký cho các base trong đợt này đã được chuyển; năm món còn
lại không có skin nguồn:

| Skin đích | Base | Build nguồn |
|---|---|---|
| `ttk_lbjlt_skins_zgrpt` | `ttk_lbjlt` | `xd_lbjlt_skins_zgrpt` |
| `ttk_lgzbh_skins_jlyc` | `ttk_lgzbh` | `xd_lgzbh_skins_jlyc` |
| `ttk_lgzbh_skins_lz` | `ttk_lgzbh` | `xd_lgzbh_skins_lz` |
| `ttk_mg_skins_qwg` | `ttk_mg` | `xd_mg_skins_qwg` |
| `ttk_flower_md_skins_rjfg` | `ttk_flower_md` | `xd_flower_md_skins_rjfg` |
| `ttk_tree_yxs_skins_jqs` | `ttk_tree_yxs` | `xd_tree_yxs_skins_jqs` |

Ngân Hạnh có hai archive tên gần giống trong nguồn. Chỉ
`xd_tree_yxs_skins_jqs` khớp khai báo skin/build; archive
`xd_tree_yx_skins_jqs` không được đăng ký thêm. Không thấy callback gameplay
riêng trong định nghĩa sáu skin trên; chúng đổi build và giữ nguyên cơ chế base.

## Ghi chú kiểm chứng

Các atlas/icon, animation ZIP, prefab registration, recipe output và tên
`SpawnPrefab` của đợt này được kiểm tra tĩnh. Lua được compile bằng Lua 5.1
runtime cục bộ; web được sinh lại từ `tools/build_tu_tien_ky_web.py` rồi kiểm
TypeScript/ESLint. Theo yêu cầu, chưa mở game, chưa chạy multiplayer và chưa
đóng gói ZIP phát hành; cần smoke test trong DST trước khi phát hành chính thức.
