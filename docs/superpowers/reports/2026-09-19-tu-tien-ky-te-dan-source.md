# Báo cáo nguồn Tế Đàn Tu Tiên Ký — Task 1

Ngày audit: 19/09/2026. Phạm vi của mốc này chỉ gồm manifest, dữ liệu thuần, tài nguyên Tế Đàn/rương và nền đăng ký. Chưa có prefab Tế Đàn, rương, component vòng đời, adapter boss hoặc logic phát thưởng chạy trong game.

## Bản nguồn đã chốt

| Gói | Phiên bản | Tệp nhận diện | SHA-256 |
|---|---:|---|---|
| Tu Tiên gốc, Workshop `3235319974` | 19.7 | `modinfo.lua` | `4FEAA63BAC5CA0205D804F05FB3D030C768236C37E21E051CC3162B16E15713A` |
| Tu Tiên Ký | 0.9.0 | `modinfo.lua` | `8EA5B9FEDD059761E4318C338C99EC07624C6E6B4ED7F860C5E14AD886480CEF` |
| Solo Leveling, Workshop `3780347550` | 2.2.7 | `modinfo.lua` | `C56BD66382BD50BE1009FF90DFC3A7FE24D54957E8B9B15A1FDBBE4F670E8575` |
| Solo Combat HUD | 1.0.0 | `modinfo.lua` | `8E8B557036496846745A0EFF1E53769A27C5440DFD7B05E799E65F7E0ECF9342` |

`modmain.lua` của bản Tu Tiên Ký trước Task 1 có SHA-256 `6CBC613D7E6276B044E7880120F3FB05B0B1221EF43D0AC68FCAB7B6AA5E2C71`; bản sao rollback nằm tại `.superpowers/te-dan-sol-high/backups/task1/modmain.lua.before`. Workspace sống có thay đổi đồng thời nên Task 1 chỉ sửa bản staging `.superpowers/te-dan-sol-high/TuTienKy`.

Mã 19.7 trong `3235319974` được mã hóa theo byte. Bản giải mã ở `mods/eva-assets-work/skill-audit/decoded` chỉ được dùng để đọc/audit. Các tệp hành vi trực tiếp sau có ciphertext giống tuyệt đối giữa bản gốc 19.7 và bản Việt hóa `3721846643`, nên bản giải mã tương ứng có nguồn gốc xác định:

| Tệp hành vi | SHA-256 của cả `3235319974` và `3721846643` | Quyết định |
|---|---|---|
| `scripts/prefabs/xd_jitan.lua` | `E4AD44A85C307A81D44FC93C12BF9F1069CBA019D7E61C9FA0BE7C84F7A9D69A` | đọc bảng boss/thưởng và luồng nguồn; viết lại độc lập |
| `scripts/prefabs/xd_llbx.lua` | `88A0C521031C0CC64C23D6E26220D413B931501C27D4972BEB6BF6625534CF46` | đọc hợp đồng rương theo userid/save record; viết lại ở Task 4 |
| `scripts/components/xd_llbx_container.lua` | `CEDAD396FCF71DD0E3783BDBEDE6D3920B3B1733D7D4673F0917A6EC18A1393E` | bỏ component nguồn; thay bằng component `ttk_` ở Task 4 |
| `scripts/main/prefabpostInit.lua` | `DC981DEF36FF76034F32EEB2B727FD7DF81005B9A86DE5AD101E16CC8F1EC1F8` | chỉ dùng làm bằng chứng về defeat của boss; adapter riêng ở Task 3 |

`containers.lua`, `strings.lua` và `import.lua` không giống byte giữa hai Workshop. Task 1 không tái dùng mã từ các tệp này: layout container được hoãn đến Task 4, chuỗi Việt hóa được viết mới, và danh sách import nguồn bị loại.

## Manifest tài nguyên nhập

Công cụ `.superpowers/te-dan-sol-high/port_ttk_jitan_assets.py` kiểm tra hash trước khi sao chép. Các zip giữ bank/build gốc `xd_jitan` và `xd_llbx`; chỉ đường dẫn file dùng namespace `ttk_`. Hai XML atlas được đổi tên texture sang `ttk_`.

| Nguồn 19.7 | SHA-256 nguồn | Đích staging | Dùng cho |
|---|---|---|---|
| `anim/xd_jitan.zip` | `D2CCC37728B85AB458F24738A899478442325992228393CAD948702B2D348853` | `anim/ttk_jitan.zip` | animation Tế Đàn |
| `anim/xd_llbx.zip` | `8CD8C1864BDDF800587BCF3E848797B410BA18A69F9CB4679A73E540A4C1C75E` | `anim/ttk_llbx.zip` | animation rương |
| `anim/xd_ui_llbx.zip` | `2D8A5974BF352F3B3D0675A9B560898E5D3CE3E9FEEB1E625EE5862932DA9D91` | `anim/ttk_ui_llbx.zip` | giao diện container rương |
| `images/map_icons/xd_jitan.tex` | `216D667E993512E057653E0D9583952E48757AE3809328E7E101BC7B7EC975CC` | `images/map_icons/ttk_jitan.tex` | minimap/inventory atlas |
| `images/map_icons/xd_jitan.xml` | `3946FC4C7912FC5F0DCD9ACE8C1D4903FDBDA27CAD7891CC2ED9521A8B360733` | `images/map_icons/ttk_jitan.xml` | atlas Tế Đàn; XML viết lại tên tex |
| `images/map_icons/xd_llbx.tex` | `365B314A9258FDB0B9F6F02B669207AE2D57BDBFF9EA952C4BFD78FE5B25821C` | `images/map_icons/ttk_llbx.tex` | minimap/inventory atlas |
| `images/map_icons/xd_llbx.xml` | `FB3A54941561976953D50A2F0B50C50E463E80564F34D1EDA5C883EE6681A0DC` | `images/map_icons/ttk_llbx.xml` | atlas rương; XML viết lại tên tex |

Không nhập `xd_jitan_antlion_sinkhole`, FX tế luyện, asset boss riêng, worldgen, brain hoặc stategraph nào từ Tu Tiên. Boss trong manifest đều là prefab DST của runtime đã cài; asset/brain/stategraph của chúng do DST sở hữu.

## Dữ liệu đầu ra `ttk_jitan_defs`

Module xuất bốn interface bắt buộc: `offerings`, `boss_pools`, `reward_pools`, `recipe_ingredients`. `score_groups` là bảng bổ sung để tách lựa chọn boss khỏi môi trường.

### Lễ vật và điểm

- `ttk_lingshi2`: điểm 2/3/4 với xác suất 35/35/30%.
- `ttk_lingshi3`: điểm 4/5/6 với xác suất 10/45/45%.
- Loại `xd_qlr` và `xd_fs`; không có alias hoặc công thức cho hai lễ vật riêng này.

### Nhóm boss

- Nhóm 1: 3 Spider Queen, Ancient Guardian (`minotaur`), Bearger, Deerclops, Dragonfly.
- Nhóm 2: Sharkboi, Mutated Bearger, Bee Queen, Daywalker, bộ ba Shadow Thralls, Celestial Champion pha 3, Mutated Deerclops, 2 Mutated Warg.
- Nhóm 3: Klaus và bộ ba Shadow Chess (`shadow_knight`, `shadow_bishop`, `shadow_rook`). Hai boss riêng `xd_jfsn` và `xd_qlch` đã bị loại.

Phân nhóm theo điểm là: 2 → nhóm 1; 3 → nhóm 1/2 bằng nhau; 4 → nhóm 1/3/2 với 34/33/33%; 5 → nhóm 2/3 bằng nhau; 6 → nhóm 3. Mỗi encounter trong nhóm có trọng số như nhau khi Task 2 triển khai RNG.

Nguồn `getrandomboss(num1,num2)` dùng `num1` cả lúc lọc bảng môi trường `tianqis` (`xd_jitan.lua:906-909`), bỏ qua `num2`. Đây là lỗi nguồn. Port không có bảng môi trường nên không mang lỗi này sang.

### Bảng thưởng tĩnh đã resolve

Mỗi dòng là một lựa chọn có trọng số; số trong ngoặc là số lượng record cố định.

- Bậc 1: `perogies` (8) + `dragonpie` (8), `armormarble` (5), `armorruins` (5), `nightsword` (10), `amulet` (4, trọng số 0,5), `armorsnurtleshell` (5).
- Bậc 2: `jellybean_spice_chili` + `voltgoatjelly`, `voltgoatjelly` (4), bộ `armorskeleton` + `hivehat` (3) + `panflute` + `alterguardianhat` (trọng số 0,2), `armor_sanity` (7), `ruinshat` (7).
- Bậc 3: `armordreadstone` + `dreadstonehat` (0,2), `lunarplant_kit` (3), `lunarplanthat` + `armor_lunarplant` + `lunarplant_kit` (2) (0,2), `armor_voidcloth` + `voidclothhat` + `voidcloth_kit` (2) (0,2), `voidcloth_kit` (3), `armorwagpunk` + `wagpunkhat` + `wagpunkbits_kit` (2) (0,15), `wagpunkbits_kit` (3, trọng số 0,75).

Các alias gói thưởng Trung văn trong nguồn (`shuijiaohuolongguopai`, `latangdoufuteyangroudong`, `erdangxiyou`, `juewangshitaozhuang`, `liangqietaozhuang`, `xukongtaozhuang`, `warbistaozhuang`) đã được bung thành prefab DST cụ thể. Test quét `scripts.zip` và tìm thấy toàn bộ boss, item thưởng và nguyên liệu DST. Bonus linh thạch theo điểm sẽ dùng alias `ttk_lingshi*` khi Task 4 hiện thực hóa; Task 1 chưa roll hoặc spawn thưởng.

### Công thức đã chốt

- `ttk_jitan`: 12 Đá Cắt (`cutstone`) + 6 Vàng (`goldnugget`) + 2 Thượng Phẩm Linh Thạch (`ttk_lingshi3`).
- `ttk_llbx`: 6 Ván (`boards`) + 4 Vàng + 1 Thượng Phẩm Linh Thạch.

## Phụ thuộc runtime trực tiếp và quyết định

| Phụ thuộc nguồn | Nơi thấy | Đích/quyết định |
|---|---|---|
| `trader`, `inspectable` | `xd_jitan.lua` | dùng component DST chuẩn trong Task 2 |
| `lootdropper`, `temperatureoverrider` | `xd_jitan.lua` | bỏ khỏi nền Task 1; không cần cho altar không có tai họa |
| `container`, save record | `xd_llbx.lua` | giữ cơ chế DST chuẩn; component thưởng `ttk_` ở Task 4 |
| `xd_llbx_container`, `xd_use_inventory` | `xd_llbx.lua` | bỏ, không nhập component Tu Tiên |
| `SpawnPrefab` reward/boss | `xd_jitan.lua` | dữ liệu prefab đã resolve; spawn thuộc Task 3/4 |
| `collapse_small`, âm thanh chest | `xd_jitan.lua`, `xd_llbx.lua` | prefab/âm thanh DST, giữ khi prefab được viết |
| `xd_lbjlt_fx5` | `xd_jitan.lua` | bỏ; FX riêng ngoài phạm vi |
| `XD_GETWOLRDLEVEL` | `xd_jitan.lua` | bỏ; không có world-level Tu Tiên |
| `XD_GONGGAO` | `xd_jitan.lua` | bỏ; Task 2 dùng talker hoặc event/netvar `ttk_` |
| `xd_level` | `xd_jitan.lua`, `xd_llbx.lua` | bỏ; không tăng cảnh giới |
| `xd_choujiang_creature` | `xd_jitan.lua`, `prefabpostInit.lua` | bỏ; Task 3 dùng marker/run_id riêng |
| `TUNING.XD_FORCE_SGRATE` | `xd_jitan.lua` | bỏ; không đổi scaling boss toàn cục |
| `tffn`, `xd_jitan_antlion_sinkhole`, weather FX/tuning | `xd_jitan.lua` | bỏ toàn bộ tai họa môi trường |
| hook Daywalker `MakeDefeated`, Sharkboi `minhealth`/SG defeat, Celestial Champion SG death | `prefabpostInit.lua` | không nhập hook toàn cục; Task 3 viết adapter chỉ tác động entity có marker |
| Klaus `SpawnDeer`, `knownlocations`, `spawnfader` | `xd_jitan.lua` | adapter spawn riêng ở Task 3 |
| Solo/HUD | không có trong module mới | không require/modimport và không tạo component của mod khác |

Task 1 không đăng ký `ttk_jitan` hoặc `ttk_llbx` trong `PrefabFiles`, vì prefab tương ứng chưa tồn tại. `main/ttk_jitan.lua` chỉ đăng ký bảy asset và chuỗi Việt hóa. Vòng `table.insert(PrefabFiles, name)` đã có với manifest rỗng; Task 2/4 chỉ thêm tên sau khi tệp prefab tồn tại.

## Kiểm chứng Task 1

- `tools/test_jitan.py`: kiểm tra xác suất, danh sách boss/count, pool 3, toàn bộ bảng thưởng, công thức, prefab DST có trong `scripts.zip`, manifest copy/hash, atlas đã đổi tên, chuỗi Việt hóa, không đăng ký prefab sớm và cấm `XD_GETWOLRDLEVEL`, `XD_GONGGAO`, `xd_level`, `<XX>`, require/modimport Solo.
- `tools/audit_registration.py` trên staging: 60 cấu hình hợp lệ; 156 Lua không thiếu require/modimport tĩnh; 169 tham chiếu texture; 146 zip animation không lỗi CRC; kiểm tra mạng bốn bếp cũ vẫn đạt.
- Baseline sống trước Task 1: 60 cấu hình, 154 Lua, 167 atlas, 143 animation. Phần tăng chính xác là 2 Lua, 2 atlas và 3 animation của Task 1.

Chưa có kiểm thử runtime DST hay phiên game ở Task 1. Các adapter boss, snapshot loot tự nhiên 2–3 lượt, chest riêng theo userid và save/load thuộc Task 3/4/6.
