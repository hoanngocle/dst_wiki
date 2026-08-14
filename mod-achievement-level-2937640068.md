# Achievement & Level — toàn bộ dữ liệu mod 2937640068

- Mod: **Achievement & Level**, phiên bản **7.3.4**.
- Nguồn: **Steam Workshop 2937640068** (`steamapps/workshop/content/322330/2937640068`).
- Tổng cộng: **169 thành tựu**, **128 perk/kỹ năng**, **763 lượt nhiệm vụ trong các pool**.
- Nội dung tên và mô tả được giữ nguyên từ `main_strings_vi.lua`. File tiếng Việt của mod vẫn còn khá nhiều dòng tiếng Anh; báo cáo không tự dịch hay sửa nội dung nguồn.

## Cách hệ thống nhiệm vụ mùa hoạt động

- Mỗi nhân vật nhận 6 nhiệm vụ ngẫu nhiên khi pool được tạo/làm mới.
- Nhiệm vụ 1 lấy từ pool riêng của nhân vật. Nếu nhân vật không có pool riêng, code fallback về pool theo mùa.
- Nhiệm vụ 2–4 lấy từ pool một-lần của mùa hiện tại.
- Nhiệm vụ 5–6 lấy từ pool đếm; mỗi nhiệm vụ phải thực hiện 10 lần.
- Chuỗi UI nói nhiệm vụ/phần thưởng được làm mới khi đổi mùa, nhưng code không đăng ký listener đổi mùa. Pool tra cứu đổi theo mùa hiện tại; việc reroll và xóa bốn cờ thưởng chỉ xảy ra khi gọi RPC `refreshSeasonalTask` (UI gọi khi mã nhiệm vụ hiện tại không còn hợp lệ trong pool mới). Vì vậy không nên mặc định rằng cứ đổi mùa là mọi nhiệm vụ chắc chắn được reroll.
- Mốc thưởng dựa trên tổng số nhiệm vụ đã hoàn thành: 1 nhiệm vụ hồi 50 Máu/Đói/Sanity; 2 nhiệm vụ nhận hiệu ứng nhân vật tức thời; 3 nhiệm vụ nhận 1 Sao; 4 nhiệm vụ nhận 200 XP và bật kỹ năng mùa của nhân vật nếu code có triển khai.
- Số lượng trong các bảng dưới đây đếm từ entry thực tế. Một số comment số lượng trong Lua đã cũ; ví dụ pool mùa đông ghi `--70` nhưng chỉ có 68 entry.

## Kỹ năng/phần thưởng nhiệm vụ theo nhân vật

### Mốc 2 nhiệm vụ — hiệu ứng tức thời

| Nhân vật | Hiệu ứng |
|---|---|
| Wilson | Nhận ngẫu nhiên 1 gem: tím 20%, xanh dương 25%, đỏ 25%, xanh lá 10%, vàng 10%, cam 10%. |
| Willow | Nhận 5 Willow Ember. |
| Wendy | Đặt liên kết Abigail lên cấp tối đa. |
| Wolfgang | Hồi đầy máu. |
| Woodie | Nhận ngẫu nhiên 1 Kitschy Idol (mỗi dạng thường 33%, Leif Idol 1%). |
| Wickerbottom | Hồi đầy Sanity. |
| WX-78 | Thêm 6 charge module. |
| Wes | Không có nhánh riêng; nhận 50 XP. |
| Maxwell | Không có nhánh riêng; nhận 50 XP. |
| Wigfrid | Sửa đầy độ bền các trang bị có component giáp. |
| Webber | Không có nhánh riêng; nhận 50 XP. |
| Winona | Tháo rã một vật phẩm hợp lệ trong túi. |
| Wortox | Sinh Krampus gần đó; Krampus nhắm vào người chơi và có bonus XP 6.66. |
| Wormwood | Trồng ngẫu nhiên 1–5 cây mùa vụ quanh người chơi và kích tăng trưởng phép. |
| Warly | Hồi đầy Đói. |
| Wurt | Nhận ngẫu nhiên 1 loại cá biển. |
| Walter | Nhận 2 thịt khô ngẫu nhiên; loại thịt người có xác suất 1%. |
| Wanda | Không có nhánh riêng; nhận 50 XP. |
| Wonkey | Không có nhánh riêng; nhận 50 XP. |

### Mốc 4 nhiệm vụ — 200 XP và kỹ năng mùa

| Nhân vật | Kỹ năng được triển khai trong code |
|---|---|
| Willow | Dùng Willow Ember thành công: +25% sát thương trong 30 giây. |
| Wendy | Khi Abigail chết: sát thương x2 trong 1 ngày game; mất buff khi triệu hồi Abigail lại. |
| Wolfgang | Khi nhận sát thương: nhận XP bằng `floor(sát thương / 2)`. |
| Woodie | Hoàn tất một thao tác lao động: sát thương x2 trong 60 giây. |
| Wigfrid | Giết mục tiêu hợp lệ cộng dồn +0,5% sát thương trong 15 giây; giết boss cộng +5% trong 5 phút. |
| Wickerbottom | Đọc sách thành công: 50% cơ hội hoàn lại 1 lần dùng và nhận 5 XP. |
| WX-78 | Giết boss: rơi thêm 1 Gears tại vị trí boss. |
| Winona | Công trình trong bán kính 12 được bảo vệ khỏi phá/đốt bởi nguồn không phải người chơi. |
| Warly | Tự ăn: chia sẻ phần hồi Máu/Đói/Sanity dương và hiệu ứng OnEaten cho người chơi trong bán kính 12. |
| Walter | 80% cơ hội không tiêu hao đạn ná khi bắn. |
| Wilson, Wes, Webber, Wormwood, Wortox, Wurt, Wanda, Maxwell, Wonkey | Không thấy kỹ năng riêng trong `main_taskskillpostInits.lua`; vẫn nhận 200 XP và cờ thưởng mốc 4. |

## Toàn bộ nhiệm vụ

### Nhiệm vụ 2–4 — Mùa xuân (một lần, mọi nhân vật) — 70 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat a Butter Muffin | Ăn vật phẩm có prefab `butterflymuffin`. | `oneat` | `eat_a_butter_muffin` |
| 2 | Eat a California Roll | Ăn vật phẩm có prefab `californiaroll`. | `oneat` | `eat_a_california_roll` |
| 3 | Eat Ceviche | Ăn vật phẩm có prefab `ceviche`. | `oneat` | `eat_ceviche` |
| 4 | Eat a Figgy Frogwich | Ăn vật phẩm có prefab `frognewton`. | `oneat` | `eat_a_figgy_frogwich` |
| 5 | Eat Fish Tacos | Ăn vật phẩm có prefab `fishtacos`. | `oneat` | `eat_fish_tacos` |
| 6 | Eat Fishsticks | Ăn vật phẩm có prefab `fishsticks`. | `oneat` | `eat_fishsticks` |
| 7 | Eat a Froggle Bunwich | Ăn vật phẩm có prefab `frogglebunwich`. | `oneat` | `eat_a_froggle_bunwich` |
| 8 | Eat a Fruit Medley | Ăn vật phẩm có prefab `fruitmedley`. | `oneat` | `eat_a_fruit_medley` |
| 9 | Eat a Leafy Meatloaf | Ăn vật phẩm có prefab `leafloaf`. | `oneat` | `eat_a_leafy_meatloaf` |
| 10 | Eat a Seafood Gumbo | Ăn vật phẩm có prefab `seafoodgumbo`. | `oneat` | `eat_a_seafood_gumbo` |
| 11 | Drink a Soothing Tea | Ăn vật phẩm có prefab `sweettea`. | `oneat` | `drink_a_soothing_tea` |
| 12 | Eat Unagi | Ăn vật phẩm có prefab `unagi`. | `oneat` | `eat_unagi` |
| 13 | Eat Something While Fully Wet | Thực hiện khi độ ẩm đang tối đa. | `oneat` | `eat_something_while_fully_wet` |
| 14 | Eat Something While Fully Dry | Thực hiện khi độ ẩm bằng 0. | `oneat` | `eat_something_while_fully_dry` |
| 15 | Eat a Mushy Cake | Ăn vật phẩm có prefab `shroomcake`. | `oneat` | `eat_a_mushy_cake` |
| 16 | Kill a Batilisk | Tiêu diệt sinh vật có prefab `bat`. | `killed` | `kill_a_batilisk` |
| 17 | Kill a Baby Beefalo | Tiêu diệt sinh vật có prefab `babybeefalo`. | `killed` | `kill_a_baby_beefalo` |
| 18 | Kill a Bunnyman | Tiêu diệt sinh vật có prefab `bunnyman`. | `killed` | `kill_a_bunnyman` |
| 19 | Kill a Depths Worm | Tiêu diệt sinh vật có prefab `worm`. | `killed` | `kill_a_depths_worm` |
| 20 | Kill a Blue Hound | Tiêu diệt sinh vật có prefab `icehound`. | `killed` | `kill_a_blue_hound` |
| 21 | Kill a Merm | Tiêu diệt sinh vật có prefab `merm`. | `killed` | `kill_a_merm` |
| 22 | Kill a Lureplant | Tiêu diệt sinh vật có prefab `lureplant`. | `killed` | `kill_a_lureplant` |
| 23 | Kill a Rabbit | Tiêu diệt sinh vật có prefab `rabbit`. | `killed` | `kill_a_rabbit` |
| 24 | Kill a Terrorbeak | Tiêu diệt sinh vật có prefab `terrorbeak`. | `killed` | `kill_a_terrorbeak` |
| 25 | Kill a Slurtle | Tiêu diệt sinh vật có prefab `slurtle`. | `killed` | `kill_a_slurtle` |
| 26 | Kill a Snurtle | Tiêu diệt sinh vật có prefab `snurtle`. | `killed` | `kill_a_snurtle` |
| 27 | Kill a Sea Strider | Tiêu diệt sinh vật có prefab `spider_water`. | `killed` | `kill_a_sea_strider` |
| 28 | Kill a Spider Warrior | Tiêu diệt sinh vật có prefab `spider_warrior`. | `killed` | `kill_a_spider_warrior` |
| 29 | Kill a Dangling Depth Dweller | Tiêu diệt sinh vật có prefab `spider_dropper`. | `killed` | `kill_a_dangling_depth_dweller` |
| 30 | Kill a Tentacle | Tiêu diệt sinh vật có prefab `tentacle`. | `killed` | `kill_a_tentacle` |
| 31 | Kill a Mosling | Tiêu diệt sinh vật có prefab `mossling`. | `killed` | `kill_a_mosling` |
| 32 | Kill a Volt Goat | Tiêu diệt sinh vật có prefab `lightninggoat`. | `killed` | `kill_a_volt_goat` |
| 33 | Kill a Grass Gekko | Tiêu diệt sinh vật có prefab `grassgekko`. | `killed` | `kill_a_grass_gekko` |
| 34 | Kill Something While Fully Wet | Thực hiện khi độ ẩm đang tối đa. | `killed` | `kill_something_while_fully_wet` |
| 35 | Kill Something While Fully Dry | Thực hiện khi độ ẩm bằng 0. | `killed` | `kill_something_while_fully_dry` |
| 36 | Craft a Pretty Parasol | Chế tạo/nhận vật phẩm có prefab `grass_umbrella`. | `builditem` | `craft_a_pretty_parasol` |
| 37 | Craft an Umbrella | Chế tạo/nhận vật phẩm có prefab `umbrella`. | `builditem` | `craft_an_umbrella` |
| 38 | Craft a Rain Coat | Chế tạo/nhận vật phẩm có prefab `raincoat`. | `builditem` | `craft_a_rain_coat` |
| 39 | Craft an Eyebrella | Chế tạo/nhận vật phẩm có prefab `eyebrellahat`. | `builditem` | `craft_an_eyebrella` |
| 40 | Craft a Rain Hat | Chế tạo/nhận vật phẩm có prefab `rainhat`. | `builditem` | `craft_a_rain_hat` |
| 41 | Craft an Item While Fully Wet | Thực hiện khi độ ẩm đang tối đa. | `builditem` | `craft_an_item_while_fully_wet` |
| 42 | Craft an Item While Fully Dry | Thực hiện khi độ ẩm bằng 0. | `builditem` | `craft_an_item_while_fully_dry` |
| 43 | Catch a Bee | Thực hiện thao tác `NET` lên prefab `bee`. | `finishedwork` | `catch_a_bee` |
| 44 | Catch a Killer Bee | Thực hiện thao tác `NET` lên prefab `killerbee`. | `finishedwork` | `catch_a_killer_bee` |
| 45 | Dig Up a Berry Bush | Thực hiện thao tác `DIG` lên prefab `berrybush`. | `finishedwork` | `dig_up_a_berry_bush` |
| 46 | Dig Up Garden Detritus | Thực hiện thao tác `DIG` lên prefab `farm_soil_debris`. | `finishedwork` | `dig_up_garden_detritus` |
| 47 | Catch a Moon Moth | Thực hiện thao tác `NET` lên prefab `moonbutterfly`. | `finishedwork` | `catch_a_moon_moth` |
| 48 | Chop Down a Lune Tree | Hoàn tất thao tác `CHOP` trên prefab `moon_tree`. | `working` | `chop_down_a_lune_tree` |
| 49 | Chop Down a Green Mushtree | Hoàn tất thao tác `CHOP` trên prefab `mushtree_small`. | `working` | `chop_down_a_green_mushtree` |
| 50 | Catch a Green Mushroom Spore | Thực hiện thao tác `NET` lên prefab `spore_small`. | `finishedwork` | `catch_a_green_mushroom_spore` |
| 51 | Dig Up a Sapling | Thực hiện thao tác `DIG` lên prefab `sapling`. | `finishedwork` | `dig_up_a_sapling` |
| 52 | Pick a Composting Bin | Thu hoạch đối tượng có prefab `compostingbin`. | `picksomething` | `pick_a_composting_bin` |
| 53 | Pick a Green Mushroom | Thu hoạch đối tượng có prefab `green_mushroom`. | `picksomething` | `pick_a_green_mushroom` |
| 54 | Pick an Eggplant Stalk | Thu hoạch đối tượng có prefab `farm_plant_eggplant`. | `picksomething` | `pick_an_eggplant_stalk` |
| 55 | Pick a Durian Vine | Thu hoạch đối tượng có prefab `farm_plant_durian`. | `picksomething` | `pick_a_durian_vine` |
| 56 | Pick a Mysterious Plant | Thu hoạch đối tượng có prefab `wormlight_plant`. | `picksomething` | `pick_a_mysterious_plant` |
| 57 | Harvest from a Bee Box | Thu hoạch đối tượng có prefab `beebox`. | `harvestsomething` | `harvest_from_a_bee_box` |
| 58 | Plant a Flower | Đặt vật phẩm có prefab `butterfly`. | `deployitem` | `plant_a_flower` |
| 59 | Deploy a Garden Digamajig | Đặt vật phẩm có prefab `farm_plow_item`. | `deployitem` | `deploy_a_garden_digamajig` |
| 60 | Plant a Fleshy Bulb | Đặt vật phẩm có prefab `lureplantbulb`. | `deployitem` | `plant_a_fleshy_bulb` |
| 61 | Plant a Lune Tree | Đặt vật phẩm có prefab `moonbutterfly`. | `deployitem` | `plant_a_lune_tree` |
| 62 | Plant a Normal Berry Bush | Đặt vật phẩm có prefab `dug_berrybush`. | `deployitem` | `plant_a_normal_berry_bush` |
| 63 | Check Crops With Gardeneer Hat Vision | Sự kiện phải có cờ `enabled = true`. | `nutrientsvision` | `check_crops_with_gardeneer_hat_vision` |
| 64 | Start Going Insane | Kích hoạt sự kiện game `goinsane` một lần. | `goinsane` | `start_going_insane` |
| 65 | Start Becoming Enlightened | Kích hoạt sự kiện game `goenlightened` một lần. | `goenlightened` | `start_becoming_enlightened` |
| 66 | Enter Lunar Territory | Đổi trạng thái sanity sang `SANITY_MODE_LUNACY`. | `sanitymodechanged` | `enter_lunar_territory` |
| 67 | Drown | Kích hoạt sự kiện game `on_washed_ashore` một lần. | `on_washed_ashore` | `drown` |
| 68 | Heal Using a Mosquito Sack | Nhận thay đổi máu với nguyên nhân `mosquitosack`. | `healthdelta` | `heal_using_a_mosquito_sack` |
| 69 | Heal Using a Spider Gland | Nhận thay đổi máu với nguyên nhân `spidergland`. | `healthdelta` | `heal_using_a_spider_gland` |
| 70 | Avoid Lightning Damage Using Insulation | Kích hoạt sự kiện game `lightningdamageavoided` một lần. | `lightningdamageavoided` | `avoid_lightning_damage_using_insulation` |

### Nhiệm vụ 2–4 — Mùa đông (một lần, mọi nhân vật) — 68 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat an Asparagus Soup | Ăn vật phẩm có prefab `asparagussoup`. | `oneat` | `eat_an_asparagus_soup` |
| 2 | Eat a Creamy Potato Purée | Ăn vật phẩm có prefab `mashedpotatoes`. | `oneat` | `eat_a_creamy_potato_purée` |
| 3 | Eat Fancy Spiralled Tubers | Ăn vật phẩm có prefab `potatotornado`. | `oneat` | `eat_fancy_spiralled_tubers` |
| 4 | Eat Guacamole | Ăn vật phẩm có prefab `guacamole`. | `oneat` | `eat_guacamole` |
| 5 | Eat Ratatouille | Ăn vật phẩm có prefab `ratatouille`. | `oneat` | `eat_ratatouille` |
| 6 | Eat Jellybeans | Ăn vật phẩm có prefab `jellybean`. | `oneat` | `eat_jellybeans` |
| 7 | Eat a Monster Lasagna | Ăn vật phẩm có prefab `monsterlasagna`. | `oneat` | `eat_a_monster_lasagna` |
| 8 | Eat a Plain Omelette | Ăn vật phẩm có prefab `justeggs`. | `oneat` | `eat_a_plain_omelette` |
| 9 | Eat Pumpkin Cookies | Ăn vật phẩm có prefab `pumpkincookie`. | `oneat` | `eat_pumpkin_cookies` |
| 10 | Eat a Stuffed Eggplant | Ăn vật phẩm có prefab `stuffedeggplant`. | `oneat` | `eat_a_stuffed_eggplant` |
| 11 | Eat Spicy Chili | Ăn vật phẩm có prefab `hotchili`. | `oneat` | `eat_spicy_chili` |
| 12 | Eat Tall Scotch Eggs | Ăn vật phẩm có prefab `talleggs`. | `oneat` | `eat_tall_scotch_eggs` |
| 13 | Eat Something While Freezing | Thực hiện khi nhiệt độ từ 0 trở xuống. | `oneat` | `eat_something_while_freezing` |
| 14 | Kill a Batilisk | Tiêu diệt sinh vật có prefab `bat`. | `killed` | `kill_a_batilisk_2` |
| 15 | Kill a Beefalo | Tiêu diệt sinh vật có prefab `beefalo`. | `killed` | `kill_a_beefalo` |
| 16 | Kill a Bunnyman | Tiêu diệt sinh vật có prefab `bunnyman`. | `killed` | `kill_a_bunnyman_2` |
| 17 | Kill a Depths Worm | Tiêu diệt sinh vật có prefab `worm`. | `killed` | `kill_a_depths_worm_2` |
| 18 | Kill a Frog | Tiêu diệt sinh vật có prefab `frog`. | `killed` | `kill_a_frog` |
| 19 | Kill a Blue Hound | Tiêu diệt sinh vật có prefab `icehound`. | `killed` | `kill_a_blue_hound_2` |
| 20 | Kill a Winter Koalefant | Tiêu diệt sinh vật có prefab `koalefant_winter`. | `killed` | `kill_a_winter_koalefant` |
| 21 | Kill Krampus | Tiêu diệt sinh vật có prefab `krampus`. | `killed` | `kill_krampus` |
| 22 | Kill MacTusk | Tiêu diệt sinh vật có prefab `walrus`. | `killed` | `kill_mactusk` |
| 23 | Kill a Wee MacTusk | Tiêu diệt sinh vật có prefab `little_walrus`. | `killed` | `kill_a_wee_mactusk` |
| 24 | Kill a No-Eyed Deer | Tiêu diệt sinh vật có prefab `deer`. | `killed` | `kill_a_no_eyed_deer` |
| 25 | Kill a Moon Moth | Tiêu diệt sinh vật có prefab `moonbutterfly`. | `killed` | `kill_a_moon_moth` |
| 26 | Kill a Naked Mole Bat | Tiêu diệt sinh vật có prefab `molebat`. | `killed` | `kill_a_naked_mole_bat` |
| 27 | Kill Something While Freezing | Thực hiện khi nhiệt độ từ 0 trở xuống. | `killed` | `kill_something_while_freezing` |
| 28 | Craft a Thermal Stone | Chế tạo/nhận vật phẩm có prefab `heatrock`. | `builditem` | `craft_a_thermal_stone` |
| 29 | Craft a Dapper Vest | Chế tạo/nhận vật phẩm có prefab `sweatervest`. | `builditem` | `craft_a_dapper_vest` |
| 30 | Craft a Puffy Vest | Chế tạo/nhận vật phẩm có prefab `trunkvest_winter`. | `builditem` | `craft_a_puffy_vest` |
| 31 | Craft a Hibearnation Vest | Chế tạo/nhận vật phẩm có prefab `beargervest`. | `builditem` | `craft_a_hibearnation_vest` |
| 32 | Craft Rabbit Earmuffs | Chế tạo/nhận vật phẩm có prefab `earmuffshat`. | `builditem` | `craft_rabbit_earmuffs` |
| 33 | Craft a Winter Hat | Chế tạo/nhận vật phẩm có prefab `winterhat`. | `builditem` | `craft_a_winter_hat` |
| 34 | Craft a Beefalo Hat | Chế tạo/nhận vật phẩm có prefab `beefalohat`. | `builditem` | `craft_a_beefalo_hat` |
| 35 | Craft a Campfire | Xây công trình có prefab `campfire`. | `buildstructure` | `craft_a_campfire` |
| 36 | Craft a Tent | Xây công trình có prefab `tent`. | `buildstructure` | `craft_a_tent` |
| 37 | Mine a Tidy Hidey-Hole | Thực hiện thao tác `MINE` lên prefab `dustmothden`. | `finishedwork` | `mine_a_tidy_hidey_hole` |
| 38 | Mine a Hot Spring | Thực hiện thao tác `MINE` lên prefab `hotspring`. | `finishedwork` | `mine_a_hot_spring` |
| 39 | Dig Up a Spiky Bush | Thực hiện thao tác `DIG` lên prefab `marsh_bush`. | `finishedwork` | `dig_up_a_spiky_bush` |
| 40 | Chop Down a Blue Mushtree | Hoàn tất thao tác `CHOP` trên prefab `mushtree_tall`. | `working` | `chop_down_a_blue_mushtree` |
| 41 | Catch a Blue Mushroom Spore | Thực hiện thao tác `NET` lên prefab `spore_tall`. | `finishedwork` | `catch_a_blue_mushroom_spore` |
| 42 | Hammer a Pig House | Thực hiện thao tác `HAMMER` lên prefab `pighouse`. | `finishedwork` | `hammer_a_pig_house` |
| 43 | Mine a Meteor Boulder | Thực hiện thao tác `MINE` lên prefab `rock_moon`. | `finishedwork` | `mine_a_meteor_boulder` |
| 44 | Pick Bull Kelp | Thu hoạch đối tượng có prefab `bullkelp_plant`. | `picksomething` | `pick_bull_kelp` |
| 45 | Pick a Blue Mushroom | Thu hoạch đối tượng có prefab `blue_mushroom`. | `picksomething` | `pick_a_blue_mushroom` |
| 46 | Pick a Stone Fruit Bush | Thu hoạch đối tượng có prefab `rock_avocado_bush`. | `picksomething` | `pick_a_stone_fruit_bush` |
| 47 | Pick a Tallbird Nest | Thu hoạch đối tượng có prefab `tallbirdnest`. | `picksomething` | `pick_a_tallbird_nest` |
| 48 | Pick a Tumbleweed | Thu hoạch đối tượng có prefab `tumbleweed`. | `picksomething` | `pick_a_tumbleweed` |
| 49 | Pick a Potato Plant | Thu hoạch đối tượng có prefab `farm_plant_potato`. | `picksomething` | `pick_a_potato_plant` |
| 50 | Pick a Carrot Plant | Thu hoạch đối tượng có prefab `farm_plant_carrot`. | `picksomething` | `pick_a_carrot_plant` |
| 51 | Pick a Pumpkin Plant | Thu hoạch đối tượng có prefab `farm_plant_pumpkin`. | `picksomething` | `pick_a_pumpkin_plant` |
| 52 | Pick an Asparagus Fern | Thu hoạch đối tượng có prefab `farm_plant_asparagus`. | `picksomething` | `pick_an_asparagus_fern` |
| 53 | Pick a Garlic Plant | Thu hoạch đối tượng có prefab `farm_plant_garlic`. | `picksomething` | `pick_a_garlic_plant` |
| 54 | Craft an item that costs health | Kích hoạt sự kiện game `consumehealthcost` một lần. | `consumehealthcost` | `craft_an_item_that_costs_health` |
| 55 | Place Down Carpeted Flooring | Đặt vật phẩm có prefab `turf_carpetfloor`. | `deployitem` | `place_down_carpeted_flooring` |
| 56 | Plant a Marble Bean | Đặt vật phẩm có prefab `marblebean`. | `deployitem` | `plant_a_marble_bean` |
| 57 | Plant a Pine Cone | Đặt vật phẩm có prefab `pinecone`. | `deployitem` | `plant_a_pine_cone` |
| 58 | Plant a Spiky Bush | Đặt vật phẩm có prefab `dug_marsh_bush`. | `deployitem` | `plant_a_spiky_bush` |
| 59 | Catch an Ocean Fish | Kích hoạt sự kiện game `fishcaught` một lần. | `fishcaught` | `catch_an_ocean_fish` |
| 60 | Attacked By Charlie | Kích hoạt sự kiện game `attackedbygrue` một lần. | `attackedbygrue` | `attacked_by_charlie` |
| 61 | Take Damage From Starving | Kích hoạt sự kiện game `stopstarving` một lần. | `stopstarving` | `take_damage_from_starving` |
| 62 | Bucked by Mount | Kích hoạt sự kiện game `bucked` một lần. | `bucked` | `bucked_by_mount` |
| 63 | Failed to Mount | Kích hoạt sự kiện game `refusedmount` một lần. | `refusedmount` | `failed_to_mount` |
| 64 | Ride a Mount | Kích hoạt sự kiện game `mounted` một lần. | `mounted` | `ride_a_mount` |
| 65 | Go To Sleep | Kích hoạt sự kiện game `gotosleep` một lần. | `gotosleep` | `go_to_sleep` |
| 66 | Slip On Ice | Kích hoạt sự kiện game `feetslipped` một lần. | `feetslipped` | `slip_on_ice` |
| 67 | Catch Fire | Kích hoạt sự kiện game `onignite` một lần. | `onignite` | `catch_fire` |
| 68 | Get Frozen | Kích hoạt sự kiện game `freeze` một lần. | `freeze` | `get_frozen` |

### Nhiệm vụ 2–4 — Mùa hè (một lần, mọi nhân vật) — 70 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat a Banana Pop | Ăn vật phẩm có prefab `bananapop`. | `oneat` | `eat_a_banana_pop` |
| 2 | Drink a Banana Shake | Ăn vật phẩm có prefab `bananajuice`. | `oneat` | `drink_a_banana_shake` |
| 3 | Eat a Dragonpie | Ăn vật phẩm có prefab `dragonpie`. | `oneat` | `eat_a_dragonpie` |
| 4 | Eat a Jelly Salad | Ăn vật phẩm có prefab `leafymeatsouffle`. | `oneat` | `eat_a_jelly_salad` |
| 5 | Eat Stuffed Pepper Poppers | Ăn vật phẩm có prefab `pepperpopper`. | `oneat` | `eat_stuffed_pepper_poppers` |
| 6 | Eat Taffy | Ăn vật phẩm có prefab `taffy`. | `oneat` | `eat_taffy` |
| 7 | Eat a Flower Salad | Ăn vật phẩm có prefab `flowersalad`. | `oneat` | `eat_a_flower_salad` |
| 8 | Eat Ice Cream | Ăn vật phẩm có prefab `icecream`. | `oneat` | `eat_ice_cream` |
| 9 | Eat a Melonsicle | Ăn vật phẩm có prefab `watermelonicle`. | `oneat` | `eat_a_melonsicle` |
| 10 | Eat a Wobster Bisque | Ăn vật phẩm có prefab `lobsterbisque`. | `oneat` | `eat_a_wobster_bisque` |
| 11 | Eat Something While Overheating | Thực hiện khi nhiệt độ từ 70 trở lên. | `oneat` | `eat_something_while_overheating` |
| 12 | Kill a Batilisk | Tiêu diệt sinh vật có prefab `bat`. | `killed` | `kill_a_batilisk_3` |
| 13 | Kill a Baby Beefalo | Tiêu diệt sinh vật có prefab `babybeefalo`. | `killed` | `kill_a_baby_beefalo_2` |
| 14 | Kill a Bunnyman | Tiêu diệt sinh vật có prefab `bunnyman`. | `killed` | `kill_a_bunnyman_3` |
| 15 | Kill a Depths Worm | Tiêu diệt sinh vật có prefab `worm`. | `killed` | `kill_a_depths_worm_3` |
| 16 | Kill a Frog | Tiêu diệt sinh vật có prefab `frog`. | `killed` | `kill_a_frog_2` |
| 17 | Kill a Red Hound | Tiêu diệt sinh vật có prefab `firehound`. | `killed` | `kill_a_red_hound` |
| 18 | Kill a Koalefant | Tiêu diệt sinh vật có prefab `koalefant_summer`. | `killed` | `kill_a_koalefant` |
| 19 | Kill a Slurper | Tiêu diệt sinh vật có prefab `slurper`. | `killed` | `kill_a_slurper` |
| 20 | Kill a Tallbird | Tiêu diệt sinh vật có prefab `tallbird`. | `killed` | `kill_a_tallbird` |
| 21 | Kill a Moleworm | Tiêu diệt sinh vật có prefab `mole`. | `killed` | `kill_a_moleworm` |
| 22 | Kill a Cookie Cutter | Tiêu diệt sinh vật có prefab `cookiecutter`. | `killed` | `kill_a_cookie_cutter` |
| 23 | Kill a Crustashine | Tiêu diệt sinh vật có prefab `lightcrab`. | `killed` | `kill_a_crustashine` |
| 24 | Kill a Skittersquid | Tiêu diệt sinh vật có prefab `squid`. | `killed` | `kill_a_skittersquid` |
| 25 | Kill a Suspicious Peeper | Tiêu diệt sinh vật có prefab `eyeofterror_mini`. | `killed` | `kill_a_suspicious_peeper` |
| 26 | Kill Something While Overheating | Thực hiện khi nhiệt độ từ 70 trở lên. | `killed` | `kill_something_while_overheating` |
| 27 | Craft a Thermal Stone | Chế tạo/nhận vật phẩm có prefab `heatrock`. | `builditem` | `craft_a_thermal_stone_2` |
| 28 | Craft a Chilled Amulet | Chế tạo/nhận vật phẩm có prefab `blueamulet`. | `builditem` | `craft_a_chilled_amulet` |
| 29 | Craft a Whirly Fan | Chế tạo/nhận vật phẩm có prefab `minifan`. | `builditem` | `craft_a_whirly_fan` |
| 30 | Craft a Luxury Fan | Chế tạo/nhận vật phẩm có prefab `featherfan`. | `builditem` | `craft_a_luxury_fan` |
| 31 | Craft a Summer Frest | Chế tạo/nhận vật phẩm có prefab `reflectivevest`. | `builditem` | `craft_a_summer_frest` |
| 32 | Craft a Floral Shirt | Chế tạo/nhận vật phẩm có prefab `hawaiianshirt`. | `builditem` | `craft_a_floral_shirt` |
| 33 | Craft a Fashion Melon | Chế tạo/nhận vật phẩm có prefab `watermelonhat`. | `builditem` | `craft_a_fashion_melon` |
| 34 | Craft Desert Goggles | Chế tạo/nhận vật phẩm có prefab `deserthat`. | `builditem` | `craft_desert_goggles` |
| 35 | Craft an Ice Cube | Chế tạo/nhận vật phẩm có prefab `icehat`. | `builditem` | `craft_an_ice_cube` |
| 36 | Craft an Endothermic Fire | Xây công trình có prefab `coldfire`. | `buildstructure` | `craft_an_endothermic_fire` |
| 37 | Craft a Siesta Lean-to | Xây công trình có prefab `siestahut`. | `buildstructure` | `craft_a_siesta_lean_to` |
| 38 | Catch Fireflies | Thực hiện thao tác `NET` lên prefab `fireflies`. | `finishedwork` | `catch_fireflies` |
| 39 | Chop Down a Red Mushtree | Hoàn tất thao tác `CHOP` trên prefab `mushtree_medium`. | `working` | `chop_down_a_red_mushtree` |
| 40 | Catch a Red Mushroom Spore | Thực hiện thao tác `NET` lên prefab `spore_medium`. | `finishedwork` | `catch_a_red_mushroom_spore` |
| 41 | Chop Down a Palmcone Tree | Hoàn tất thao tác `CHOP` trên prefab `palmconetree`. | `working` | `chop_down_a_palmcone_tree` |
| 42 | Hammer a Player Skeleton | Thực hiện thao tác `HAMMER` lên prefab `skeleton_player`. | `finishedwork` | `hammer_a_player_skeleton` |
| 43 | Pick a Cave Banana Tree | Thu hoạch đối tượng có prefab `cave_banana_tree`. | `picksomething` | `pick_a_cave_banana_tree` |
| 44 | Pick a Red Mushroom | Thu hoạch đối tượng có prefab `red_mushroom`. | `picksomething` | `pick_a_red_mushroom` |
| 45 | Pick a Mossy Vine | Thu hoạch đối tượng có prefab `oceanvine`. | `picksomething` | `pick_a_mossy_vine` |
| 46 | Pick a Succulent | Thu hoạch đối tượng có prefab `succulent_plant`. | `picksomething` | `pick_a_succulent` |
| 47 | Pick a Toma Root Plant | Thu hoạch đối tượng có prefab `farm_plant_tomato`. | `picksomething` | `pick_a_toma_root_plant` |
| 48 | Pick a Dragon Fruit Vine | Thu hoạch đối tượng có prefab `farm_plant_dragonfruit`. | `picksomething` | `pick_a_dragon_fruit_vine` |
| 49 | Pick a Pepper Plant | Thu hoạch đối tượng có prefab `farm_plant_pepper`. | `picksomething` | `pick_a_pepper_plant` |
| 50 | Pick an Onion Plant | Thu hoạch đối tượng có prefab `farm_plant_onion`. | `picksomething` | `pick_an_onion_plant` |
| 51 | Pick Pomegranate Branch | Thu hoạch đối tượng có prefab `farm_plant_pomegranate`. | `picksomething` | `pick_pomegranate_branch` |
| 52 | Pick a Corn Stalk | Thu hoạch đối tượng có prefab `farm_plant_corn`. | `picksomething` | `pick_a_corn_stalk` |
| 53 | Pick a Watermelon Plant | Thu hoạch đối tượng có prefab `farm_plant_watermelon`. | `picksomething` | `pick_a_watermelon_plant` |
| 54 | Harvest Sea Weed | Thu hoạch đối tượng có prefab `waterplant`. | `harvestsomething` | `harvest_sea_weed` |
| 55 | Place Down Scaled Flooring | Đặt vật phẩm có prefab `turf_dragonfly`. | `deployitem` | `place_down_scaled_flooring` |
| 56 | Deploy a Dock Kit | Đặt vật phẩm có prefab `dock_kit`. | `deployitem` | `deploy_a_dock_kit` |
| 57 | Deploy a Grass Raft Kit | Đặt vật phẩm có prefab `boat_grass_item`. | `deployitem` | `deploy_a_grass_raft_kit` |
| 58 | Plant a Palmcone Sprout | Đặt vật phẩm có prefab `palmcone_seed`. | `deployitem` | `plant_a_palmcone_sprout` |
| 59 | Plant Monkeytails | Đặt vật phẩm có prefab `dug_monkeytail`. | `deployitem` | `plant_monkeytails` |
| 60 | Deploy an Anenemy Trap | Đặt vật phẩm có prefab `dug_trap_starfish`. | `deployitem` | `deploy_an_anenemy_trap` |
| 61 | Plant a Bull Kelp Stalk | Đặt vật phẩm có prefab `bullkelp_root`. | `deployitem` | `plant_a_bull_kelp_stalk` |
| 62 | Catch a Pond Fish | Kích hoạt sự kiện game `fishingcatch` một lần. | `fishingcatch` | `catch_a_pond_fish` |
| 63 | Take Fire Damage | Kích hoạt sự kiện game `startfiredamage` một lần. | `startfiredamage` | `take_fire_damage` |
| 64 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die` |
| 65 | Burnt From Smolders | Kích hoạt sự kiện game `burnt` một lần. | `burnt` | `burnt_from_smolders` |
| 66 | Catch Fire | Kích hoạt sự kiện game `onignite` một lần. | `onignite` | `catch_fire_2` |
| 67 | Get Frozen | Kích hoạt sự kiện game `freeze` một lần. | `freeze` | `get_frozen_2` |
| 68 | Hopping | Kích hoạt sự kiện game `onhop` một lần. | `onhop` | `hopping` |
| 69 | Use Goggle | Sự kiện phải có cờ `enabled = true`. | `gogglevision` | `use_goggle` |
| 70 | Perform On Stage | Kích hoạt sự kiện game `acting` một lần. | `acting` | `perform_on_stage` |

### Nhiệm vụ 2–4 — Mùa thu (một lần, mọi nhân vật) — 71 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat Bacon and Eggs | Ăn vật phẩm có prefab `baconeggs`. | `oneat` | `eat_bacon_and_eggs` |
| 2 | Eat Barnacle Linguine | Ăn vật phẩm có prefab `barnaclinguine`. | `oneat` | `eat_barnacle_linguine` |
| 3 | Eat Barnacle Nigiri | Ăn vật phẩm có prefab `barnaclesushi`. | `oneat` | `eat_barnacle_nigiri` |
| 4 | Eat Barnacle Pita | Ăn vật phẩm có prefab `barnaclepita`. | `oneat` | `eat_barnacle_pita` |
| 5 | Eat a Breakfast Skillet | Ăn vật phẩm có prefab `veggieomlet`. | `oneat` | `eat_a_breakfast_skillet` |
| 6 | Eat a Bunny Stew | Ăn vật phẩm có prefab `bunnystew`. | `oneat` | `eat_a_bunny_stew` |
| 7 | Eat a Fig-Stuffed Trunk | Ăn vật phẩm có prefab `koalefig_trunk`. | `oneat` | `eat_a_fig_stuffed_trunk` |
| 8 | Eat a Figatoni | Ăn vật phẩm có prefab `figatoni`. | `oneat` | `eat_a_figatoni` |
| 9 | Eat a Figkabab | Ăn vật phẩm có prefab `figkabab`. | `oneat` | `eat_a_figkabab` |
| 10 | Eat Stuffed Fish Heads | Ăn vật phẩm có prefab `barnaclestuffedfishhead`. | `oneat` | `eat_stuffed_fish_heads` |
| 11 | Eat Surf 'n' Turf | Ăn vật phẩm có prefab `surfnturf`. | `oneat` | `eat_surf_n_turf` |
| 12 | Eat a Turkey Dinner | Ăn vật phẩm có prefab `turkeydinner`. | `oneat` | `eat_a_turkey_dinner` |
| 13 | Eat a Veggie Burger | Ăn vật phẩm có prefab `leafymeatburger`. | `oneat` | `eat_a_veggie_burger` |
| 14 | Eat Beefy Greens | Ăn vật phẩm có prefab `meatysalad`. | `oneat` | `eat_beefy_greens` |
| 15 | Eat a Salsa Fresca | Ăn vật phẩm có prefab `salsa`. | `oneat` | `eat_a_salsa_fresca` |
| 16 | Eat Waffles | Ăn vật phẩm có prefab `waffles`. | `oneat` | `eat_waffles` |
| 17 | Eat Something While Enlightened | Thực hiện khi đang Enlightened. | `oneat` | `eat_something_while_enlightened` |
| 18 | Eat Something While Insane | Thực hiện khi đang Insane. | `oneat` | `eat_something_while_insane` |
| 19 | Kill a Batilisk | Tiêu diệt sinh vật có prefab `bat`. | `killed` | `kill_a_batilisk_4` |
| 20 | Kill a Beefalo | Tiêu diệt sinh vật có prefab `beefalo`. | `killed` | `kill_a_beefalo_2` |
| 21 | Kill a Bunnyman | Tiêu diệt sinh vật có prefab `bunnyman`. | `killed` | `kill_a_bunnyman_4` |
| 22 | Kill a Depths Worm | Tiêu diệt sinh vật có prefab `worm`. | `killed` | `kill_a_depths_worm_4` |
| 23 | Kill a Frog | Tiêu diệt sinh vật có prefab `frog`. | `killed` | `kill_a_frog_3` |
| 24 | Kill a Red Hound | Tiêu diệt sinh vật có prefab `firehound`. | `killed` | `kill_a_red_hound_2` |
| 25 | Kill a Merm | Tiêu diệt sinh vật có prefab `merm`. | `killed` | `kill_a_merm_2` |
| 26 | Kill a Rock Lobster | Tiêu diệt sinh vật có prefab `rocky`. | `killed` | `kill_a_rock_lobster` |
| 27 | Kill a Splumonkey | Tiêu diệt sinh vật có prefab `monkey`. | `killed` | `kill_a_splumonkey` |
| 28 | Kill a Spider Warrior | Tiêu diệt sinh vật có prefab `spider_warrior`. | `killed` | `kill_a_spider_warrior_2` |
| 29 | Kill a Spider Spitter | Tiêu diệt sinh vật có prefab `spider_spitter`. | `killed` | `kill_a_spider_spitter` |
| 30 | Kill a Nurse Spider | Tiêu diệt sinh vật có prefab `spider_healer`. | `killed` | `kill_a_nurse_spider` |
| 31 | Kill a Cave Spider | Tiêu diệt sinh vật có prefab `spider_hider`. | `killed` | `kill_a_cave_spider` |
| 32 | Kill a Shattered Spider | Tiêu diệt sinh vật có prefab `spider_moon`. | `killed` | `kill_a_shattered_spider` |
| 33 | Kill a Buzzard | Tiêu diệt sinh vật có prefab `buzzard`. | `killed` | `kill_a_buzzard` |
| 34 | Kill a Catcoon | Tiêu diệt sinh vật có prefab `catcoon`. | `killed` | `kill_a_catcoon` |
| 35 | Kill a Birchnutter | Tiêu diệt sinh vật có prefab `birchnutdrake`. | `killed` | `kill_a_birchnutter` |
| 36 | Craft a Garland | Chế tạo/nhận vật phẩm có prefab `flowerhat`. | `builditem` | `craft_a_garland` |
| 37 | Craft a Rope | Chế tạo/nhận vật phẩm có prefab `rope`. | `builditem` | `craft_a_rope` |
| 38 | Craft Boards | Chế tạo/nhận vật phẩm có prefab `boards`. | `builditem` | `craft_boards` |
| 39 | Craft a Cut Stone | Chế tạo/nhận vật phẩm có prefab `cutstone`. | `builditem` | `craft_a_cut_stone` |
| 40 | Craft a Papyrus | Chế tạo/nhận vật phẩm có prefab `papyrus`. | `builditem` | `craft_a_papyrus` |
| 41 | Dig Up a Birchnut Tree | Hoàn tất thao tác `DIG` trên prefab `deciduoustree`. | `working` | `dig_up_a_birchnut_tree` |
| 42 | Chop Down a Twiggy Tree | Hoàn tất thao tác `CHOP` trên prefab `twiggytree`. | `working` | `chop_down_a_twiggy_tree` |
| 43 | Dig Up Grass | Thực hiện thao tác `DIG` lên prefab `grass`. | `finishedwork` | `dig_up_grass` |
| 44 | Mine a Marble Shrub | Thực hiện thao tác `MINE` lên prefab `marbleshrub`. | `finishedwork` | `mine_a_marble_shrub` |
| 45 | Chop Down a Normal Sporecap | Hoàn tất thao tác `CHOP` trên prefab `mushroomsprout`. | `working` | `chop_down_a_normal_sporecap` |
| 46 | Chop Down a Lunar Mushtree | Hoàn tất thao tác `CHOP` trên prefab `mushtree_moon`. | `working` | `chop_down_a_lunar_mushtree` |
| 47 | Catch a Lunar Spore | Thực hiện thao tác `NET` lên prefab `spore_moon`. | `finishedwork` | `catch_a_lunar_spore` |
| 48 | Dig Up a Moon Sapling | Thực hiện thao tác `DIG` lên prefab `sapling_moon`. | `finishedwork` | `dig_up_a_moon_sapling` |
| 49 | Catch a Bulbous Lightbug | Thực hiện thao tác `NET` lên prefab `lightflier`. | `finishedwork` | `catch_a_bulbous_lightbug` |
| 50 | Catch a Mosquito | Thực hiện thao tác `NET` lên prefab `mosquito`. | `finishedwork` | `catch_a_mosquito` |
| 51 | Pick a Junk Pile | Thu hoạch đối tượng có prefab `junk_pile`. | `picksomething` | `pick_a_junk_pile` |
| 52 | Pick a Teetering Junk Pile | Thu hoạch đối tượng có prefab `junk_pile_big`. | `picksomething` | `pick_a_teetering_junk_pile` |
| 53 | Pick Ocean Debris | Thu hoạch đối tượng có prefab `oceanfishableflotsam`. | `picksomething` | `pick_ocean_debris` |
| 54 | Pick a Moon Sapling | Thu hoạch đối tượng có prefab `sapling_moon`. | `picksomething` | `pick_a_moon_sapling` |
| 55 | Pick Forget-Me-Lots | Thu hoạch đối tượng có prefab `weed_forgetmelots`. | `picksomething` | `pick_forget_me_lots` |
| 56 | Harvest a Mushroom Planter | Thu hoạch đối tượng có prefab `mushroom_farm`. | `harvestsomething` | `harvest_a_mushroom_planter` |
| 57 | Broke Your Armor | Kích hoạt sự kiện game `armorbroke` một lần. | `armorbroke` | `broke_your_armor` |
| 58 | Place down Cobblestones | Đặt vật phẩm có prefab `turf_road`. | `deployitem` | `place_down_cobblestones` |
| 59 | Deploy a Fossil Fragment | Đặt vật phẩm có prefab `fossil_piece`. | `deployitem` | `deploy_a_fossil_fragment` |
| 60 | Plant a Twiggy Tree Cone | Đặt vật phẩm có prefab `twiggy_nut`. | `deployitem` | `plant_a_twiggy_tree_cone` |
| 61 | Plant a Sapling | Đặt vật phẩm có prefab `dug_sapling`. | `deployitem` | `plant_a_sapling` |
| 62 | Plant a Moon Sapling | Đặt vật phẩm có prefab `dug_sapling_moon`. | `deployitem` | `plant_a_moon_sapling` |
| 63 | Plant Grass | Đặt vật phẩm có prefab `dug_grass`. | `deployitem` | `plant_grass` |
| 64 | Deploy a Tooth Trap | Đặt vật phẩm có prefab `trap_teeth`. | `deployitem` | `deploy_a_tooth_trap` |
| 65 | Plant a Banana Bush | Đặt vật phẩm có prefab `dug_bananabush`. | `deployitem` | `plant_a_banana_bush` |
| 66 | Exit Lunar Territory | Đổi trạng thái sanity sang `SANITY_MODE_INSANITY`. | `sanitymodechanged` | `exit_lunar_territory` |
| 67 | Heal Using a Honey Poultice | Nhận thay đổi máu với nguyên nhân `bandage`. | `healthdelta` | `heal_using_a_honey_poultice` |
| 68 | Heal Using a Healing Salve | Nhận thay đổi máu với nguyên nhân `healingsalve`. | `healthdelta` | `heal_using_a_healing_salve` |
| 69 | Get Hit by a Spider | Nhận thay đổi máu với nguyên nhân `spider`. | `healthdelta` | `get_hit_by_a_spider` |
| 70 | Get A Monkey Trinket | Nhận lời nguyền khỉ. | `monkeycursehit` | `get_a_monkey_trinket` |
| 71 | Lose A Monkey Trinket | Giải lời nguyền khỉ. | `monkeycursehit` | `lose_a_monkey_trinket` |

### Nhiệm vụ 2–4 — Ngoài mùa / fallback (một lần, mọi nhân vật) — 71 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat Bacon and Eggs | Ăn vật phẩm có prefab `baconeggs`. | `oneat` | `eat_bacon_and_eggs` |
| 2 | Eat Barnacle Linguine | Ăn vật phẩm có prefab `barnaclinguine`. | `oneat` | `eat_barnacle_linguine` |
| 3 | Eat Barnacle Nigiri | Ăn vật phẩm có prefab `barnaclesushi`. | `oneat` | `eat_barnacle_nigiri` |
| 4 | Eat Barnacle Pita | Ăn vật phẩm có prefab `barnaclepita`. | `oneat` | `eat_barnacle_pita` |
| 5 | Eat a Breakfast Skillet | Ăn vật phẩm có prefab `veggieomlet`. | `oneat` | `eat_a_breakfast_skillet` |
| 6 | Eat a Bunny Stew | Ăn vật phẩm có prefab `bunnystew`. | `oneat` | `eat_a_bunny_stew` |
| 7 | Eat a Fig-Stuffed Trunk | Ăn vật phẩm có prefab `koalefig_trunk`. | `oneat` | `eat_a_fig_stuffed_trunk` |
| 8 | Eat a Figatoni | Ăn vật phẩm có prefab `figatoni`. | `oneat` | `eat_a_figatoni` |
| 9 | Eat a Figkabab | Ăn vật phẩm có prefab `figkabab`. | `oneat` | `eat_a_figkabab` |
| 10 | Eat Stuffed Fish Heads | Ăn vật phẩm có prefab `barnaclestuffedfishhead`. | `oneat` | `eat_stuffed_fish_heads` |
| 11 | Eat Surf 'n' Turf | Ăn vật phẩm có prefab `surfnturf`. | `oneat` | `eat_surf_n_turf` |
| 12 | Eat a Turkey Dinner | Ăn vật phẩm có prefab `turkeydinner`. | `oneat` | `eat_a_turkey_dinner` |
| 13 | Eat a Veggie Burger | Ăn vật phẩm có prefab `leafymeatburger`. | `oneat` | `eat_a_veggie_burger` |
| 14 | Eat Beefy Greens | Ăn vật phẩm có prefab `meatysalad`. | `oneat` | `eat_beefy_greens` |
| 15 | Eat a Salsa Fresca | Ăn vật phẩm có prefab `salsa`. | `oneat` | `eat_a_salsa_fresca` |
| 16 | Eat Waffles | Ăn vật phẩm có prefab `waffles`. | `oneat` | `eat_waffles` |
| 17 | Eat Something While Enlightened | Thực hiện khi đang Enlightened. | `oneat` | `eat_something_while_enlightened` |
| 18 | Eat Something While Insane | Thực hiện khi đang Insane. | `oneat` | `eat_something_while_insane` |
| 19 | Kill a Batilisk | Tiêu diệt sinh vật có prefab `bat`. | `killed` | `kill_a_batilisk_4` |
| 20 | Kill a Beefalo | Tiêu diệt sinh vật có prefab `beefalo`. | `killed` | `kill_a_beefalo_2` |
| 21 | Kill a Bunnyman | Tiêu diệt sinh vật có prefab `bunnyman`. | `killed` | `kill_a_bunnyman_4` |
| 22 | Kill a Depths Worm | Tiêu diệt sinh vật có prefab `worm`. | `killed` | `kill_a_depths_worm_4` |
| 23 | Kill a Frog | Tiêu diệt sinh vật có prefab `frog`. | `killed` | `kill_a_frog_3` |
| 24 | Kill a Red Hound | Tiêu diệt sinh vật có prefab `firehound`. | `killed` | `kill_a_red_hound_2` |
| 25 | Kill a Merm | Tiêu diệt sinh vật có prefab `merm`. | `killed` | `kill_a_merm_2` |
| 26 | Kill a Rock Lobster | Tiêu diệt sinh vật có prefab `rocky`. | `killed` | `kill_a_rock_lobster` |
| 27 | Kill a Splumonkey | Tiêu diệt sinh vật có prefab `monkey`. | `killed` | `kill_a_splumonkey` |
| 28 | Kill a Spider Warrior | Tiêu diệt sinh vật có prefab `spider_warrior`. | `killed` | `kill_a_spider_warrior_2` |
| 29 | Kill a Spider Spitter | Tiêu diệt sinh vật có prefab `spider_spitter`. | `killed` | `kill_a_spider_spitter` |
| 30 | Kill a Nurse Spider | Tiêu diệt sinh vật có prefab `spider_healer`. | `killed` | `kill_a_nurse_spider` |
| 31 | Kill a Cave Spider | Tiêu diệt sinh vật có prefab `spider_hider`. | `killed` | `kill_a_cave_spider` |
| 32 | Kill a Shattered Spider | Tiêu diệt sinh vật có prefab `spider_moon`. | `killed` | `kill_a_shattered_spider` |
| 33 | Kill a Buzzard | Tiêu diệt sinh vật có prefab `buzzard`. | `killed` | `kill_a_buzzard` |
| 34 | Kill a Catcoon | Tiêu diệt sinh vật có prefab `catcoon`. | `killed` | `kill_a_catcoon` |
| 35 | Kill a Birchnutter | Tiêu diệt sinh vật có prefab `birchnutdrake`. | `killed` | `kill_a_birchnutter` |
| 36 | Craft a Garland | Chế tạo/nhận vật phẩm có prefab `flowerhat`. | `builditem` | `craft_a_garland` |
| 37 | Craft a Rope | Chế tạo/nhận vật phẩm có prefab `rope`. | `builditem` | `craft_a_rope` |
| 38 | Craft Boards | Chế tạo/nhận vật phẩm có prefab `boards`. | `builditem` | `craft_boards` |
| 39 | Craft a Cut Stone | Chế tạo/nhận vật phẩm có prefab `cutstone`. | `builditem` | `craft_a_cut_stone` |
| 40 | Craft a Papyrus | Chế tạo/nhận vật phẩm có prefab `papyrus`. | `builditem` | `craft_a_papyrus` |
| 41 | Dig Up a Birchnut Tree | Hoàn tất thao tác `DIG` trên prefab `deciduoustree`. | `working` | `dig_up_a_birchnut_tree` |
| 42 | Chop Down a Twiggy Tree | Hoàn tất thao tác `CHOP` trên prefab `twiggytree`. | `working` | `chop_down_a_twiggy_tree` |
| 43 | Dig Up Grass | Thực hiện thao tác `DIG` lên prefab `grass`. | `finishedwork` | `dig_up_grass` |
| 44 | Mine a Marble Shrub | Thực hiện thao tác `MINE` lên prefab `marbleshrub`. | `finishedwork` | `mine_a_marble_shrub` |
| 45 | Chop Down a Normal Sporecap | Hoàn tất thao tác `CHOP` trên prefab `mushroomsprout`. | `working` | `chop_down_a_normal_sporecap` |
| 46 | Chop Down a Lunar Mushtree | Hoàn tất thao tác `CHOP` trên prefab `mushtree_moon`. | `working` | `chop_down_a_lunar_mushtree` |
| 47 | Catch a Lunar Spore | Thực hiện thao tác `NET` lên prefab `spore_moon`. | `finishedwork` | `catch_a_lunar_spore` |
| 48 | Dig Up a Moon Sapling | Thực hiện thao tác `DIG` lên prefab `sapling_moon`. | `finishedwork` | `dig_up_a_moon_sapling` |
| 49 | Catch a Bulbous Lightbug | Thực hiện thao tác `NET` lên prefab `lightflier`. | `finishedwork` | `catch_a_bulbous_lightbug` |
| 50 | Catch a Mosquito | Thực hiện thao tác `NET` lên prefab `mosquito`. | `finishedwork` | `catch_a_mosquito` |
| 51 | Pick a Junk Pile | Thu hoạch đối tượng có prefab `junk_pile`. | `picksomething` | `pick_a_junk_pile` |
| 52 | Pick a Teetering Junk Pile | Thu hoạch đối tượng có prefab `junk_pile_big`. | `picksomething` | `pick_a_teetering_junk_pile` |
| 53 | Pick Ocean Debris | Thu hoạch đối tượng có prefab `oceanfishableflotsam`. | `picksomething` | `pick_ocean_debris` |
| 54 | Pick a Moon Sapling | Thu hoạch đối tượng có prefab `sapling_moon`. | `picksomething` | `pick_a_moon_sapling` |
| 55 | Pick Forget-Me-Lots | Thu hoạch đối tượng có prefab `weed_forgetmelots`. | `picksomething` | `pick_forget_me_lots` |
| 56 | Harvest a Mushroom Planter | Thu hoạch đối tượng có prefab `mushroom_farm`. | `harvestsomething` | `harvest_a_mushroom_planter` |
| 57 | Broke Your Armor | Kích hoạt sự kiện game `armorbroke` một lần. | `armorbroke` | `broke_your_armor` |
| 58 | Place down Cobblestones | Đặt vật phẩm có prefab `turf_road`. | `deployitem` | `place_down_cobblestones` |
| 59 | Deploy a Fossil Fragment | Đặt vật phẩm có prefab `fossil_piece`. | `deployitem` | `deploy_a_fossil_fragment` |
| 60 | Plant a Twiggy Tree Cone | Đặt vật phẩm có prefab `twiggy_nut`. | `deployitem` | `plant_a_twiggy_tree_cone` |
| 61 | Plant a Sapling | Đặt vật phẩm có prefab `dug_sapling`. | `deployitem` | `plant_a_sapling` |
| 62 | Plant a Moon Sapling | Đặt vật phẩm có prefab `dug_sapling_moon`. | `deployitem` | `plant_a_moon_sapling` |
| 63 | Plant Grass | Đặt vật phẩm có prefab `dug_grass`. | `deployitem` | `plant_grass` |
| 64 | Deploy a Tooth Trap | Đặt vật phẩm có prefab `trap_teeth`. | `deployitem` | `deploy_a_tooth_trap` |
| 65 | Plant a Banana Bush | Đặt vật phẩm có prefab `dug_bananabush`. | `deployitem` | `plant_a_banana_bush` |
| 66 | Exit Lunar Territory | Đổi trạng thái sanity sang `SANITY_MODE_INSANITY`. | `sanitymodechanged` | `exit_lunar_territory` |
| 67 | Heal Using a Honey Poultice | Nhận thay đổi máu với nguyên nhân `bandage`. | `healthdelta` | `heal_using_a_honey_poultice` |
| 68 | Heal Using a Healing Salve | Nhận thay đổi máu với nguyên nhân `healingsalve`. | `healthdelta` | `heal_using_a_healing_salve` |
| 69 | Get Hit by a Spider | Nhận thay đổi máu với nguyên nhân `spider`. | `healthdelta` | `get_hit_by_a_spider` |
| 70 | Get A Monkey Trinket | Nhận lời nguyền khỉ. | `monkeycursehit` | `get_a_monkey_trinket` |
| 71 | Lose A Monkey Trinket | Giải lời nguyền khỉ. | `monkeycursehit` | `lose_a_monkey_trinket` |

### Nhiệm vụ 5–6 — Mùa xuân (lặp 10 lần, mọi nhân vật) — 17 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat 10 Wet Goops | Ăn vật phẩm có prefab `wetgoop`. | `oneat` | `eat_10_wet_goops` |
| 2 | Eat 10 Foods While Starving | Thực hiện khi đói bằng 0. | `oneat` | `eat_10_foods_while_starving` |
| 3 | Kill 10 Bees | Tiêu diệt sinh vật có prefab `bee`. | `killed` | `kill_10_bees` |
| 4 | Kill 10 Killer Bees | Tiêu diệt sinh vật có prefab `killerbee`. | `killed` | `kill_10_killer_bees` |
| 5 | Kill 10 Butterflies | Tiêu diệt sinh vật có prefab `butterfly`. | `killed` | `kill_10_butterflies` |
| 6 | Kill 10 Frogs | Tiêu diệt sinh vật có prefab `frog`. | `killed` | `kill_10_frogs` |
| 7 | Kill 10 Hounds | Tiêu diệt sinh vật có prefab `hound`. | `killed` | `kill_10_hounds` |
| 8 | Kill 10 Crawling Horrors | Tiêu diệt sinh vật có prefab `crawlinghorror`. | `killed` | `kill_10_crawling_horrors` |
| 9 | Kill 10 Canaries | Tiêu diệt sinh vật có prefab `canary`. | `killed` | `kill_10_canaries` |
| 10 | Catch 10 Butterflies | Thực hiện thao tác `NET` lên prefab `butterfly`. | `finishedwork` | `catch_10_butterflies` |
| 11 | Catch 10 Things Using a Net | Thực hiện thao tác `NET`. | `finishedwork` | `catch_10_things_using_a_net` |
| 12 | Shovel 10 Things | Hoàn tất thao tác `DIG`. | `working` | `shovel_10_things` |
| 13 | Pick 10 Normal Berry Bushes | Thu hoạch đối tượng có prefab `berrybush`. | `picksomething` | `pick_10_normal_berry_bushes` |
| 14 | Pick 10 Flowers | Thu hoạch đối tượng có prefab `flower`. | `picksomething` | `pick_10_flowers` |
| 15 | Pick 10 Light Flowers | Thu hoạch đối tượng có prefab `flower_cave`. | `picksomething` | `pick_10_light_flowers` |
| 16 | Till Soil 10 Times Using a Hoe | Kích hoạt sự kiện game `tilling` một lần. | `tilling` | `till_soil_10_times_using_a_hoe` |
| 17 | Craft 10 Items | Kích hoạt sự kiện game `builditem` một lần. | `builditem` | `craft_10_items` |

### Nhiệm vụ 5–6 — Mùa đông (lặp 10 lần, mọi nhân vật) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat 10 Kabobs | Ăn vật phẩm có prefab `kabobs`. | `oneat` | `eat_10_kabobs` |
| 2 | Eat 10 Meatballs | Ăn vật phẩm có prefab `meatballs`. | `oneat` | `eat_10_meatballs` |
| 3 | Eat 10 Meaty Stews | Ăn vật phẩm có prefab `bonestew`. | `oneat` | `eat_10_meaty_stews` |
| 4 | Kill 10 Snowbirds | Tiêu diệt sinh vật có prefab `robin_winter`. | `killed` | `kill_10_snowbirds` |
| 5 | Kill 10 Puffins | Tiêu diệt sinh vật có prefab `puffin`. | `killed` | `kill_10_puffins` |
| 6 | Kill 10 Hounds | Tiêu diệt sinh vật có prefab `hound`. | `killed` | `kill_10_hounds_2` |
| 7 | Kill 10 Pengulls | Tiêu diệt sinh vật có prefab `penguin`. | `killed` | `kill_10_pengulls` |
| 8 | Kill 10 Pigs | Tiêu diệt sinh vật có prefab `pigman`. | `killed` | `kill_10_pigs` |
| 9 | Kill 10 Spiders | Tiêu diệt sinh vật có prefab `spider`. | `killed` | `kill_10_spiders` |
| 10 | Chop Down 10 Evergreens | Hoàn tất thao tác `CHOP` trên prefab `evergreen`. | `working` | `chop_down_10_evergreens` |
| 11 | Chop Down 10 Lumpy Evergreens | Hoàn tất thao tác `CHOP` trên prefab `evergreen_sparse`. | `working` | `chop_down_10_lumpy_evergreens` |
| 12 | Mine 10 Mini Glaciers | Thực hiện thao tác `MINE` lên prefab `rock_ice`. | `finishedwork` | `mine_10_mini_glaciers` |
| 13 | Mine Things 10 Times | Thực hiện thao tác `MINE`. | `finishedwork` | `mine_things_10_times` |
| 14 | Pick 10 Ferns | Thu hoạch đối tượng có prefab `cave_fern`. | `picksomething` | `pick_10_ferns` |
| 15 | Pick 10 Lichens | Thu hoạch đối tượng có prefab `lichen`. | `picksomething` | `pick_10_lichens` |
| 16 | Pick 10 Spiky Bushes | Thu hoạch đối tượng có prefab `marsh_bush`. | `picksomething` | `pick_10_spiky_bushes` |
| 17 | Eat Things 10 Times | Kích hoạt sự kiện game `oneat` một lần. | `oneat` | `eat_things_10_times` |
| 18 | Get Fed By Another Player 10 Times | Được một người chơi khác cho ăn. | `oneat` | `get_fed_by_another_player_10_times` |

### Nhiệm vụ 5–6 — Mùa hè (lặp 10 lần, mọi nhân vật) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat 10 Fists Full of Jam | Ăn vật phẩm có prefab `jammypreserves`. | `oneat` | `eat_10_fists_full_of_jam` |
| 2 | Eat 10 Pierogies | Ăn vật phẩm có prefab `perogies`. | `oneat` | `eat_10_pierogies` |
| 3 | Kill 10 Butterflies | Tiêu diệt sinh vật có prefab `butterfly`. | `killed` | `kill_10_butterflies_2` |
| 4 | Kill 10 Canaries | Tiêu diệt sinh vật có prefab `canary`. | `killed` | `kill_10_canaries_2` |
| 5 | Kill 10 Hounds | Tiêu diệt sinh vật có prefab `hound`. | `killed` | `kill_10_hounds_3` |
| 6 | Kill 10 Mosquitos | Tiêu diệt sinh vật có prefab `mosquito`. | `killed` | `kill_10_mosquitos` |
| 7 | Kill 10 Spiders | Tiêu diệt sinh vật có prefab `spider`. | `killed` | `kill_10_spiders_2` |
| 8 | Mine 10 Stone Fruits | Thực hiện thao tác `MINE` lên prefab `rock_avocado_fruit`. | `finishedwork` | `mine_10_stone_fruits` |
| 9 | Hammer Things 10 Times | Thực hiện thao tác `HAMMER`. | `finishedwork` | `hammer_things_10_times` |
| 10 | Pick 10 Banana Bushes | Thu hoạch đối tượng có prefab `bananabush`. | `picksomething` | `pick_10_banana_bushes` |
| 11 | Pick 10 Monkeytails | Thu hoạch đối tượng có prefab `monkeytail`. | `picksomething` | `pick_10_monkeytails` |
| 12 | Pick 10 Cacti | Thu hoạch đối tượng có prefab `cactus`. | `picksomething` | `pick_10_cacti` |
| 13 | Pick 10 Oasis Cacti | Thu hoạch đối tượng có prefab `oasis_cactus`. | `picksomething` | `pick_10_oasis_cacti` |
| 14 | Row 10 Times | Kích hoạt sự kiện game `rowing` một lần. | `rowing` | `row_10_times` |
| 15 | Terraform 10 Times Using a Pitchfork | Kích hoạt sự kiện game `onterraform` một lần. | `onterraform` | `terraform_10_times_using_a_pitchfork` |
| 16 | Eat Something 10 Times | Kích hoạt sự kiện game `oneat` một lần. | `oneat` | `eat_something_10_times` |
| 17 | Get Fed By Another Player 10 Times | Được một người chơi khác cho ăn. | `oneat` | `get_fed_by_another_player_10_times_2` |
| 18 | Do an Emote 10 Times | Kích hoạt sự kiện game `emote` một lần. | `emote` | `do_an_emote_10_times` |

### Nhiệm vụ 5–6 — Mùa thu (lặp 10 lần, mọi nhân vật) — 17 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat 10 Honey Hams | Ăn vật phẩm có prefab `honeyham`. | `oneat` | `eat_10_honey_hams` |
| 2 | Eat 10 Honey Nuggets | Ăn vật phẩm có prefab `honeynuggets`. | `oneat` | `eat_10_honey_nuggets` |
| 3 | Eat 10 Trail Mixes | Ăn vật phẩm có prefab `trailmix`. | `oneat` | `eat_10_trail_mixes` |
| 4 | Kill 10 Crows | Tiêu diệt sinh vật có prefab `crow`. | `killed` | `kill_10_crows` |
| 5 | Kill 10 Red Birds | Tiêu diệt sinh vật có prefab `robin`. | `killed` | `kill_10_red_birds` |
| 6 | Kill 10 Canaries | Tiêu diệt sinh vật có prefab `canary`. | `killed` | `kill_10_canaries_3` |
| 7 | Kill 10 Puffins | Tiêu diệt sinh vật có prefab `puffin`. | `killed` | `kill_10_puffins_2` |
| 8 | Kill 10 Hounds | Tiêu diệt sinh vật có prefab `hound`. | `killed` | `kill_10_hounds_4` |
| 9 | Kill 10 Pigs | Tiêu diệt sinh vật có prefab `pigman`. | `killed` | `kill_10_pigs_2` |
| 10 | Kill 10 Spiders | Tiêu diệt sinh vật có prefab `spider`. | `killed` | `kill_10_spiders_3` |
| 11 | Chop Down 10 Birchnut Trees | Hoàn tất thao tác `CHOP` trên prefab `deciduoustree`. | `working` | `chop_down_10_birchnut_trees` |
| 12 | Chop Down Something 10 Times | Hoàn tất thao tác `CHOP`. | `working` | `chop_down_something_10_times` |
| 13 | Pick 10 Grass | Thu hoạch đối tượng có prefab `grass`. | `picksomething` | `pick_10_grass` |
| 14 | Pick 10 Saplings | Thu hoạch đối tượng có prefab `sapling`. | `picksomething` | `pick_10_saplings` |
| 15 | Pick 10 Reeds | Thu hoạch đối tượng có prefab `reeds`. | `picksomething` | `pick_10_reeds` |
| 16 | Plant 10 Birchnuts | Đặt vật phẩm có prefab `acorn`. | `deployitem` | `plant_10_birchnuts` |
| 17 | Craft Item | Kích hoạt sự kiện game `builditem` một lần. | `builditem` | `craft_item` |

### Nhiệm vụ 5–6 — Ngoài mùa / fallback (lặp 10 lần, mọi nhân vật) — 17 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat 10 Honey Hams | Ăn vật phẩm có prefab `honeyham`. | `oneat` | `eat_10_honey_hams` |
| 2 | Eat 10 Honey Nuggets | Ăn vật phẩm có prefab `honeynuggets`. | `oneat` | `eat_10_honey_nuggets` |
| 3 | Eat 10 Trail Mixes | Ăn vật phẩm có prefab `trailmix`. | `oneat` | `eat_10_trail_mixes` |
| 4 | Kill 10 Crows | Tiêu diệt sinh vật có prefab `crow`. | `killed` | `kill_10_crows` |
| 5 | Kill 10 Red Birds | Tiêu diệt sinh vật có prefab `robin`. | `killed` | `kill_10_red_birds` |
| 6 | Kill 10 Canaries | Tiêu diệt sinh vật có prefab `canary`. | `killed` | `kill_10_canaries_3` |
| 7 | Kill 10 Puffins | Tiêu diệt sinh vật có prefab `puffin`. | `killed` | `kill_10_puffins_2` |
| 8 | Kill 10 Hounds | Tiêu diệt sinh vật có prefab `hound`. | `killed` | `kill_10_hounds_4` |
| 9 | Kill 10 Pigs | Tiêu diệt sinh vật có prefab `pigman`. | `killed` | `kill_10_pigs_2` |
| 10 | Kill 10 Spiders | Tiêu diệt sinh vật có prefab `spider`. | `killed` | `kill_10_spiders_3` |
| 11 | Chop Down 10 Birchnut Trees | Hoàn tất thao tác `CHOP` trên prefab `deciduoustree`. | `working` | `chop_down_10_birchnut_trees` |
| 12 | Chop Down Something 10 Times | Hoàn tất thao tác `CHOP`. | `working` | `chop_down_something_10_times` |
| 13 | Pick 10 Grass | Thu hoạch đối tượng có prefab `grass`. | `picksomething` | `pick_10_grass` |
| 14 | Pick 10 Saplings | Thu hoạch đối tượng có prefab `sapling`. | `picksomething` | `pick_10_saplings` |
| 15 | Pick 10 Reeds | Thu hoạch đối tượng có prefab `reeds`. | `picksomething` | `pick_10_reeds` |
| 16 | Plant 10 Birchnuts | Đặt vật phẩm có prefab `acorn`. | `deployitem` | `plant_10_birchnuts` |
| 17 | Craft Item | Kích hoạt sự kiện game `builditem` một lần. | `builditem` | `craft_item` |

### Nhiệm vụ 1 — Wilson (yêu cầu nhân vật Wilson) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat Something | Kích hoạt sự kiện game `oneat` một lần. | `oneat` | `eat_something` |
| 2 | Craft an Item | Kích hoạt sự kiện game `builditem` một lần. | `builditem` | `craft_an_item` |
| 3 | Shave Beard | Kích hoạt sự kiện game `shaved` một lần. | `shaved` | `shave_beard` |
| 4 | Shave Beard | Kích hoạt sự kiện game `shaved` một lần. | `shaved` | `shave_beard_2` |
| 5 | Shave Beard | Kích hoạt sự kiện game `shaved` một lần. | `shaved` | `shave_beard_3` |
| 6 | Craft a Torch | Chế tạo/nhận vật phẩm có prefab `torch`. | `builditem` | `craft_a_torch` |
| 7 | Craft a Log | Chế tạo/nhận vật phẩm có prefab `log`. | `builditem` | `craft_a_log` |
| 8 | Craft a Twig | Chế tạo/nhận vật phẩm có prefab `twigs`. | `builditem` | `craft_a_twig` |
| 9 | Craft a Flint | Chế tạo/nhận vật phẩm có prefab `flint`. | `builditem` | `craft_a_flint` |
| 10 | Craft a Rock | Chế tạo/nhận vật phẩm có prefab `rocks`. | `builditem` | `craft_a_rock` |
| 11 | Craft a Blue Gem | Chế tạo/nhận vật phẩm có prefab `bluegem`. | `builditem` | `craft_a_blue_gem` |
| 12 | Craft a Red Gem | Chế tạo/nhận vật phẩm có prefab `redgem`. | `builditem` | `craft_a_red_gem` |
| 13 | Craft a Meat | Chế tạo/nhận vật phẩm có prefab `meat`. | `builditem` | `craft_a_meat` |
| 14 | Craft a Morsel | Chế tạo/nhận vật phẩm có prefab `smallmeat`. | `builditem` | `craft_a_morsel` |
| 15 | Craft a Campfire | Xây công trình có prefab `campfire`. | `buildstructure` | `craft_a_campfire_2` |
| 16 | Craft a Science Machine | Xây công trình có prefab `researchlab`. | `buildstructure` | `craft_a_science_machine` |
| 17 | Craft a Meat Effigy | Xây công trình có prefab `resurrectionstatue`. | `buildstructure` | `craft_a_meat_effigy` |
| 18 | Place down a Beard Hair Rug | Đặt vật phẩm có prefab `turf_beard_hair`. | `deployitem` | `place_down_a_beard_hair_rug` |

### Nhiệm vụ 1 — Willow (yêu cầu nhân vật Willow) — 13 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Run Out Of Willow's Lighter Fuel | Dùng cạn vật phẩm `lighter`. | `itemranout` | `run_out_of_willows_lighter_fuel` |
| 2 | Get Frozen | Kích hoạt sự kiện game `freeze` một lần. | `freeze` | `get_frozen_3` |
| 3 | Attack Using Willow's Lighter | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `lighter`. | `onhitother` | `attack_using_willows_lighter` |
| 4 | Attack Using Willow's Lighter | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `lighter`. | `onhitother` | `attack_using_willows_lighter_2` |
| 5 | Burn Something | Kích hoạt sự kiện game `onstartedfire` một lần. | `onstartedfire` | `burn_something` |
| 6 | Burn Something | Kích hoạt sự kiện game `onstartedfire` một lần. | `onstartedfire` | `burn_something_2` |
| 7 | Burn Something | Kích hoạt sự kiện game `onstartedfire` một lần. | `onstartedfire` | `burn_something_3` |
| 8 | Burn Something | Kích hoạt sự kiện game `onstartedfire` một lần. | `onstartedfire` | `burn_something_4` |
| 9 | Burn a Cut Grass | Châm lửa đối tượng `cutgrass`. | `onstartedfire` | `burn_a_cut_grass` |
| 10 | Burn a Twig | Châm lửa đối tượng `twigs`. | `onstartedfire` | `burn_a_twig` |
| 11 | Burn an Evergreen | Châm lửa đối tượng `evergreen`. | `onstartedfire` | `burn_an_evergreen` |
| 12 | Burn a Lumpy Evergreen | Châm lửa đối tượng `evergreen_sparse`. | `onstartedfire` | `burn_a_lumpy_evergreen` |
| 13 | Burn a Birchnut Tree | Châm lửa đối tượng `deciduoustree`. | `onstartedfire` | `burn_a_birchnut_tree` |

### Nhiệm vụ 1 — Wendy (yêu cầu nhân vật Wendy) — 13 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_2` |
| 2 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_3` |
| 3 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_4` |
| 4 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_5` |
| 5 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_6` |
| 6 | Level Up Abigail | Tăng liên kết với Abigail lên cấp lớn hơn 1. | `ghostlybond_level_change` | `level_up_abigail` |
| 7 | Level Up Abigail | Tăng liên kết với Abigail lên cấp lớn hơn 1. | `ghostlybond_level_change` | `level_up_abigail_2` |
| 8 | Craft Revenant Restorative | Chế tạo/nhận vật phẩm có prefab `ghostlyelixir_slowregen`. | `builditem` | `craft_revenant_restorative` |
| 9 | Craft Spectral Cure-All | Chế tạo/nhận vật phẩm có prefab `ghostlyelixir_fastregen`. | `builditem` | `craft_spectral_cure_all` |
| 10 | Craft Unyielding Draught | Chế tạo/nhận vật phẩm có prefab `ghostlyelixir_shield`. | `builditem` | `craft_unyielding_draught` |
| 11 | Craft Distilled Vengeance | Chế tạo/nhận vật phẩm có prefab `ghostlyelixir_retaliation`. | `builditem` | `craft_distilled_vengeance` |
| 12 | Craft Nightshade Nostrum | Chế tạo/nhận vật phẩm có prefab `ghostlyelixir_attack`. | `builditem` | `craft_nightshade_nostrum` |
| 13 | Craft Vigor Mortis | Chế tạo/nhận vật phẩm có prefab `ghostlyelixir_speed`. | `builditem` | `craft_vigor_mortis` |

### Nhiệm vụ 1 — Wolfgang (yêu cầu nhân vật Wolfgang) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Coaching | Kích hoạt sự kiện game `coach` một lần. | `coach` | `coaching` |
| 2 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked` |
| 3 | Attack a Level 3 Spider Den | Đánh `spiderden_3`, sát thương lớn hơn 0, bằng vũ khí `undefined`. | `onhitother` | `attack_a_level_3_spider_den` |
| 4 | Become Mighty | Đổi trạng thái Mightiness sang `mighty`. | `mightiness_statechange` | `become_mighty` |
| 5 | Become Wimpy | Đổi trạng thái Mightiness sang `wimpy`. | `mightiness_statechange` | `become_wimpy` |
| 6 | Use a Dumbbell | Kích hoạt sự kiện game `stopliftingdumbbell` một lần. | `stopliftingdumbbell` | `use_a_dumbbell` |
| 7 | Fail To Lift at The Gym | Hoàn tất tập gym với kết quả `fail`. | `lift_gym` | `fail_to_lift_at_the_gym` |
| 8 | Work While Mighty | Thực hiện khi Wolfgang đang Mighty. | `working` | `work_while_mighty` |
| 9 | Till Soil Using a Hoe While Mighty | Thực hiện khi Wolfgang đang Mighty. | `tilling` | `till_soil_using_a_hoe_while_mighty` |
| 10 | Row While Mighty | Thực hiện khi Wolfgang đang Mighty. | `rowing` | `row_while_mighty` |
| 11 | Lower a Sail While Mighty | Thực hiện khi Wolfgang đang Mighty. | `on_lower_sail_boost` | `lower_a_sail_while_mighty` |
| 12 | Terraform Using a Pitchfork While Mighty | Thực hiện khi Wolfgang đang Mighty. | `onterraform` | `terraform_using_a_pitchfork_while_mighty` |
| 13 | Work While Wimpy | Thực hiện khi Wolfgang đang Wimpy. | `working` | `work_while_wimpy` |
| 14 | Till Soil Using a Hoe While Wimpy | Thực hiện khi Wolfgang đang Wimpy. | `tilling` | `till_soil_using_a_hoe_while_wimpy` |
| 15 | Row While Wimpy | Thực hiện khi Wolfgang đang Wimpy. | `rowing` | `row_while_wimpy` |
| 16 | Lower a Sail While Wimpy | Thực hiện khi Wolfgang đang Wimpy. | `on_lower_sail_boost` | `lower_a_sail_while_wimpy` |
| 17 | Terraform Using a Pitchfork While Wimpy | Thực hiện khi Wolfgang đang Wimpy. | `onterraform` | `terraform_using_a_pitchfork_while_wimpy` |
| 18 | Eat a Roasted Potato | Ăn vật phẩm có prefab `potato_cooked`. | `oneat` | `eat_a_roasted_potato` |

### Nhiệm vụ 1 — WX-78 (yêu cầu nhân vật WX-78) — 21 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Struck By Lightning | Nhận thay đổi máu với nguyên nhân `lightning`. | `healthdelta` | `struck_by_lightning` |
| 2 | Short Circuited By Moisture | Kích hoạt sự kiện game `do_robot_spark` một lần. | `do_robot_spark` | `short_circuited_by_moisture` |
| 3 | Increase Charges | Làm mức điện WX-78 tăng. | `energylevelupdate` | `increase_charges` |
| 4 | Decrease Charges | Làm mức điện WX-78 giảm. | `energylevelupdate` | `decrease_charges` |
| 5 | Harvest The Bio Scanalyzer | Thu hoạch đối tượng có prefab `wx78_scanner_succeeded`. | `harvestsomething` | `harvest_the_bio_scanalyzer` |
| 6 | Eat Gears | Ăn vật phẩm có prefab `gears`. | `oneat` | `eat_gears` |
| 7 | Take Damage or Heal While a Hardy Circuit Is Active | Thực hiện khi đang lắp ít nhất một module loại `maxhealth`. | `healthdelta` | `take_damage_or_heal_while_a_hardy_circuit_is_active` |
| 8 | Take Damage or Heal While a Super-Hardy Circuit Is Active | Thực hiện khi đang lắp ít nhất một module loại `maxhealth2`. | `healthdelta` | `take_damage_or_heal_while_a_super_hardy_circuit_is_active` |
| 9 | Have a Processing Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `maxsanity1`. | `newstate` | `have_a_processing_circuit_active` |
| 10 | Have a Super-Processing Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `maxsanity`. | `newstate` | `have_a_super_processing_circuit_active` |
| 11 | Have a Beanbooster Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `bee`. | `newstate` | `have_a_beanbooster_circuit_active` |
| 12 | Have a Chorusbox Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `music`. | `newstate` | `have_a_chorusbox_circuit_active` |
| 13 | Eat While a Gastrogain Circuit Is Active | Thực hiện khi đang lắp ít nhất một module loại `maxhunger1`. | `oneat` | `eat_while_a_gastrogain_circuit_is_active` |
| 14 | Eat While a Super-Gastrogain Circuit Is Active | Thực hiện khi đang lắp ít nhất một module loại `maxhunger1`. | `oneat` | `eat_while_a_super_gastrogain_circuit_is_active` |
| 15 | Have an Acceleration Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `movespeed`. | `newstate` | `have_an_acceleration_circuit_active` |
| 16 | Have a Super-Acceleration Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `movespeed2`. | `newstate` | `have_a_super_acceleration_circuit_active` |
| 17 | Have a Thermal Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `heat`. | `newstate` | `have_a_thermal_circuit_active` |
| 18 | Have a Refrigerant Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `cold`. | `newstate` | `have_a_refrigerant_circuit_active` |
| 19 | Attacked While an Electrification Circuit is Active | Thực hiện khi đang lắp ít nhất một module loại `taser`. | `attacked` | `attacked_while_an_electrification_circuit_is_active` |
| 20 | Have an Optoelectronic Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `nightvision`. | `newstate` | `have_an_optoelectronic_circuit_active` |
| 21 | Have an Illumination Circuit Active | Thực hiện khi đang lắp ít nhất một module loại `light`. | `newstate` | `have_an_illumination_circuit_active` |

### Nhiệm vụ 1 — Wes (yêu cầu nhân vật Wes) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat Fresh Fruit Crepes | Ăn vật phẩm có prefab `freshfruitcrepes`. | `oneat` | `eat_fresh_fruit_crepes` |
| 2 | Do Mime (Tryng to talk) | Kích hoạt sự kiện game `ontalk` một lần. | `ontalk` | `do_mime_tryng_to_talk` |
| 3 | Do Mime (Tryng to talk) | Kích hoạt sự kiện game `ontalk` một lần. | `ontalk` | `do_mime_tryng_to_talk_2` |
| 4 | Do Mime (Tryng to talk) | Kích hoạt sự kiện game `ontalk` một lần. | `ontalk` | `do_mime_tryng_to_talk_3` |
| 5 | Struck By Lightning | Nhận thay đổi máu với nguyên nhân `lightning`. | `healthdelta` | `struck_by_lightning_2` |
| 6 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_7` |
| 7 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_2` |
| 8 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_3` |
| 9 | Get Attacked By a Frog | Bị `frog` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_by_a_frog` |
| 10 | Get Attacked By a Mosquito | Bị `mosquito` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_by_a_mosquito` |
| 11 | Kill a Boss/Mini Boss | Tiêu diệt boss (tag `epic`) đồng thời thỏa điều kiện `nocheckfn`. | `killed` | `kill_a_boss_mini_boss` |
| 12 | Kill a Boss/Mini Boss While Having Full Health | Tiêu diệt boss (tag `epic`) đồng thời thỏa điều kiện `whiledyingfn, sai`. | `killed` | `kill_a_boss_mini_boss_while_having_full_health` |
| 13 | Perform Mime On Stage | Kích hoạt sự kiện game `acting` một lần. | `acting` | `perform_mime_on_stage` |
| 14 | Free Task For Wes | Kích hoạt sự kiện game `newstate` một lần. | `newstate` | `free_task_for_wes` |
| 15 | Free Task For Wes | Kích hoạt sự kiện game `newstate` một lần. | `newstate` | `free_task_for_wes_2` |
| 16 | Free Task For Wes | Kích hoạt sự kiện game `newstate` một lần. | `newstate` | `free_task_for_wes_3` |
| 17 | Free Task For Wes | Kích hoạt sự kiện game `newstate` một lần. | `newstate` | `free_task_for_wes_4` |
| 18 | Free Task For Wes | Kích hoạt sự kiện game `newstate` một lần. | `newstate` | `free_task_for_wes_5` |

### Nhiệm vụ 1 — Warly (yêu cầu nhân vật Warly) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Deploy a Portable Crock Pot | Đặt vật phẩm có prefab `portablecookpot_item`. | `deployitem` | `deploy_a_portable_crock_pot` |
| 2 | Deploy a Portable Seasoning Station | Đặt vật phẩm có prefab `portablespicer_item`. | `deployitem` | `deploy_a_portable_seasoning_station` |
| 3 | Deploy a Portable Grinding Mill | Đặt vật phẩm có prefab `portableblender_item`. | `deployitem` | `deploy_a_portable_grinding_mill` |
| 4 | Eat a Grim Galette | Ăn vật phẩm có prefab `nightmarepie`. | `oneat` | `eat_a_grim_galette` |
| 5 | Eat a Volt Goat Chaud-Froid | Ăn vật phẩm có prefab `voltgoatjelly`. | `oneat` | `eat_a_volt_goat_chaud_froid` |
| 6 | Eat a Glow Berry Mousse | Ăn vật phẩm có prefab `glowberrymousse`. | `oneat` | `eat_a_glow_berry_mousse` |
| 7 | Eat a Fish Cordon Bleu | Ăn vật phẩm có prefab `frogfishbowl`. | `oneat` | `eat_a_fish_cordon_bleu` |
| 8 | Eat a Hot Dragon Chili Salad | Ăn vật phẩm có prefab `dragonchilisalad`. | `oneat` | `eat_a_hot_dragon_chili_salad` |
| 9 | Eat an Asparagazpacho | Ăn vật phẩm có prefab `gazpacho`. | `oneat` | `eat_an_asparagazpacho` |
| 10 | Eat a Puffed Potato Soufflé | Ăn vật phẩm có prefab `potatosouffle`. | `oneat` | `eat_a_puffed_potato_soufflé` |
| 11 | Eat a Monster Tartare | Ăn vật phẩm có prefab `monstertartare`. | `oneat` | `eat_a_monster_tartare` |
| 12 | Eat Fresh Fruit Crepes | Ăn vật phẩm có prefab `freshfruitcrepes`. | `oneat` | `eat_fresh_fruit_crepes_2` |
| 13 | Eat a Bone Bouillon | Ăn vật phẩm có prefab `bonesoup`. | `oneat` | `eat_a_bone_bouillon` |
| 14 | Eat a Moqueca | Ăn vật phẩm có prefab `moqueca`. | `oneat` | `eat_a_moqueca` |
| 15 | Refuse To Eat Something | Kích hoạt sự kiện game `wonteatfood` một lần. | `wonteatfood` | `refuse_to_eat_something` |
| 16 | Eat Something | Kích hoạt sự kiện game `oneat` một lần. | `oneat` | `eat_something_2` |
| 17 | Eat Something | Kích hoạt sự kiện game `oneat` một lần. | `oneat` | `eat_something_3` |
| 18 | Eat Something | Kích hoạt sự kiện game `oneat` một lần. | `oneat` | `eat_something_4` |

### Nhiệm vụ 1 — Walter (yêu cầu nhân vật Walter) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Deploy a Tent Roll | Đặt vật phẩm có prefab `portabletent_item`. | `deployitem` | `deploy_a_tent_roll` |
| 2 | Ride a Mount | Kích hoạt sự kiện game `mounted` một lần. | `mounted` | `ride_a_mount_2` |
| 3 | Ride Woby | Cưỡi vật có prefab `undefined`. | `mounted` | `ride_woby` |
| 4 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_4` |
| 5 | Get Attacked By a Bee | Bị `bee` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_by_a_bee` |
| 6 | Get Attacked By a Killer Bee | Bị `killerbee` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_by_a_killer_bee` |
| 7 | Kill a Bee | Tiêu diệt sinh vật có prefab `bee`. | `killed` | `kill_a_bee` |
| 8 | Kill a Killer Bee | Tiêu diệt sinh vật có prefab `killerbee`. | `killed` | `kill_a_killer_bee` |
| 9 | Catch a Bee | Thực hiện thao tác `NET` lên prefab `bee`. | `finishedwork` | `catch_a_bee` |
| 10 | Catch a Killer Bee | Thực hiện thao tác `NET` lên prefab `killerbee`. | `finishedwork` | `catch_a_killer_bee` |
| 11 | Harvest a Bee Box | Thu hoạch đối tượng có prefab `beebox`. | `harvestsomething` | `harvest_a_bee_box` |
| 12 | Heal Using a Mosquito Sack | Nhận thay đổi máu với nguyên nhân `mosquitosack`. | `healthdelta` | `heal_using_a_mosquito_sack_2` |
| 13 | Eat Trail Mix | Ăn vật phẩm có prefab `trailmix`. | `oneat` | `eat_trail_mix` |
| 14 | Tell a Campfire Story | Kích hoạt sự kiện game `singsong` một lần. | `singsong` | `tell_a_campfire_story` |
| 15 | Tell a Campfire Story While Insane | Thực hiện khi đang Insane. | `singsong` | `tell_a_campfire_story_while_insane` |
| 16 | Tell a Campfire Story While Almost Dead | Thực hiện khi máu dưới 10%. | `singsong` | `tell_a_campfire_story_while_almost_dead` |
| 17 | Put Ammo Into a Slingshot | Kích hoạt sự kiện game `ammoloaded` một lần. | `ammoloaded` | `put_ammo_into_a_slingshot` |
| 18 | Remove Ammo From a Slingshot | Kích hoạt sự kiện game `ammounloaded` một lần. | `ammounloaded` | `remove_ammo_from_a_slingshot` |

### Nhiệm vụ 1 — Webber (yêu cầu nhân vật Webber) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Deploy Spider Eggs | Đặt vật phẩm có prefab `spidereggsack`. | `deployitem` | `deploy_spider_eggs` |
| 2 | Walk On Sticky Webbing | Kích hoạt sự kiện game `walkoncreep` một lần. | `walkoncreep` | `walk_on_sticky_webbing` |
| 3 | Heal Using Healing Glop | Nhận thay đổi máu với nguyên nhân `spider_healer_item`. | `healthdelta` | `heal_using_healing_glop` |
| 4 | Shave Beard | Kích hoạt sự kiện game `shaved` một lần. | `shaved` | `shave_beard_4` |
| 5 | Eat a Warrior Switcherdoodle | Ăn vật phẩm có prefab `mutator_warrior`. | `oneat` | `eat_a_warrior_switcherdoodle` |
| 6 | Eat a Dangler Switcherdoodle | Ăn vật phẩm có prefab `mutator_dropper`. | `oneat` | `eat_a_dangler_switcherdoodle` |
| 7 | Eat a Cave Switcherdoodle | Ăn vật phẩm có prefab `mutator_hider`. | `oneat` | `eat_a_cave_switcherdoodle` |
| 8 | Eat a Spitter Switcherdoodle | Ăn vật phẩm có prefab `mutator_spitter`. | `oneat` | `eat_a_spitter_switcherdoodle` |
| 9 | Eat a Shatter Switcherdoodle | Ăn vật phẩm có prefab `mutator_moon`. | `oneat` | `eat_a_shatter_switcherdoodle` |
| 10 | Eat a Nurse Switcherdoodle | Ăn vật phẩm có prefab `mutator_healer`. | `oneat` | `eat_a_nurse_switcherdoodle` |
| 11 | Eat a Strider Switcherdoodle | Ăn vật phẩm có prefab `mutator_water`. | `oneat` | `eat_a_strider_switcherdoodle` |
| 12 | Eat a Monster Lasagna | Ăn vật phẩm có prefab `monsterlasagna`. | `oneat` | `eat_a_monster_lasagna_2` |
| 13 | Eat a Monster Jerky | Ăn vật phẩm có prefab `monstermeat_dried`. | `oneat` | `eat_a_monster_jerky` |
| 14 | Eat a Cooked Monster Meat | Ăn vật phẩm có prefab `cookedmonstermeat`. | `oneat` | `eat_a_cooked_monster_meat` |
| 15 | Eat a Monster Meat | Ăn vật phẩm có prefab `monstermeat`. | `oneat` | `eat_a_monster_meat` |
| 16 | Attack a Level 3 Spider Den | Đánh `spiderden_3`, sát thương lớn hơn 0, bằng vũ khí `undefined`. | `onhitother` | `attack_a_level_3_spider_den_2` |
| 17 | Kill a Pig | Tiêu diệt sinh vật có prefab `pigman`. | `killed` | `kill_a_pig` |
| 18 | Kill a Catcoon | Tiêu diệt sinh vật có prefab `catcoon`. | `killed` | `kill_a_catcoon` |

### Nhiệm vụ 1 — Wormwood (yêu cầu nhân vật Wormwood) — 25 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Deploy a Bramble Trap | Đặt vật phẩm có prefab `trap_bramble`. | `deployitem` | `deploy_a_bramble_trap` |
| 2 | Heal Using a Manure | Nhận thay đổi máu với nguyên nhân `poop`. | `healthdelta` | `heal_using_a_manure` |
| 3 | Heal Using a Bucket-o-poop | Nhận thay đổi máu với nguyên nhân `fertilizer`. | `healthdelta` | `heal_using_a_bucket_o_poop` |
| 4 | Heal Using a Guano | Nhận thay đổi máu với nguyên nhân `guano`. | `healthdelta` | `heal_using_a_guano` |
| 5 | Enter Lunar Territory | Đổi trạng thái sanity sang `SANITY_MODE_LUNACY`. | `sanitymodechanged` | `enter_lunar_territory_2` |
| 6 | Plant a Flower | Đặt vật phẩm có prefab `butterfly`. | `deployitem` | `plant_a_flower_2` |
| 7 | Plant a Pine Cone | Đặt vật phẩm có prefab `pinecone`. | `deployitem` | `plant_a_pine_cone_2` |
| 8 | Plant a Moon Sapling | Đặt vật phẩm có prefab `dug_sapling_moon`. | `deployitem` | `plant_a_moon_sapling_2` |
| 9 | Plant a Stone Fruit Bush | Đặt vật phẩm có prefab `dug_rock_avocado_bush`. | `deployitem` | `plant_a_stone_fruit_bush_2` |
| 10 | Plant a Sprouting Stone Fruit | Đặt vật phẩm có prefab `rock_avocado_fruit_sprout`. | `deployitem` | `plant_a_sprouting_stone_fruit` |
| 11 | Plant Normal Seeds | Đặt vật phẩm có prefab `seeds`. | `deployitem` | `plant_normal_seeds` |
| 12 | Plant Eggplant Seeds | Đặt vật phẩm có prefab `eggplant_seeds`. | `deployitem` | `plant_eggplant_seeds` |
| 13 | Plant Durian Seeds | Đặt vật phẩm có prefab `durian_seeds`. | `deployitem` | `plant_durian_seeds` |
| 14 | Plant Potato Seeds | Đặt vật phẩm có prefab `potato_seeds`. | `deployitem` | `plant_potato_seeds` |
| 15 | Plant Carrot Seeds | Đặt vật phẩm có prefab `carrot_seeds`. | `deployitem` | `plant_carrot_seeds` |
| 16 | Plant Pumpkin Seeds | Đặt vật phẩm có prefab `pumpkin_seeds`. | `deployitem` | `plant_pumpkin_seeds` |
| 17 | Plant Asparagus Seeds | Đặt vật phẩm có prefab `asparagus_seeds`. | `deployitem` | `plant_asparagus_seeds` |
| 18 | Plant Garlic Seeds | Đặt vật phẩm có prefab `garlic_seeds`. | `deployitem` | `plant_garlic_seeds` |
| 19 | Plant Toma Root Seeds | Đặt vật phẩm có prefab `tomato_seeds`. | `deployitem` | `plant_toma_root_seeds` |
| 20 | Plant Dragon Fruit Seeds | Đặt vật phẩm có prefab `dragonfruit_seeds`. | `deployitem` | `plant_dragon_fruit_seeds` |
| 21 | Plant Pepper Seeds | Đặt vật phẩm có prefab `pepper_seeds`. | `deployitem` | `plant_pepper_seeds` |
| 22 | Plant Onion Seeds | Đặt vật phẩm có prefab `onion_seeds`. | `deployitem` | `plant_onion_seeds` |
| 23 | Plant Pomegranate Seeds | Đặt vật phẩm có prefab `pomegranate_seeds`. | `deployitem` | `plant_pomegranate_seeds` |
| 24 | Plant Corn Seeds | Đặt vật phẩm có prefab `corn_seeds`. | `deployitem` | `plant_corn_seeds` |
| 25 | Plant Watermelon Seeds | Đặt vật phẩm có prefab `watermelon_seeds`. | `deployitem` | `plant_watermelon_seeds` |

### Nhiệm vụ 1 — Winona (yêu cầu nhân vật Winona) — 13 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Dodge Charlie's Attack | Kích hoạt sự kiện game `resistedgrue` một lần. | `resistedgrue` | `dodge_charlies_attack` |
| 2 | Dodge Charlie's Attack | Kích hoạt sự kiện game `resistedgrue` một lần. | `resistedgrue` | `dodge_charlies_attack_2` |
| 3 | Attacked By Charlie | Kích hoạt sự kiện game `attackedbygrue` một lần. | `attackedbygrue` | `attacked_by_charlie_2` |
| 4 | Craft an Item | Kích hoạt sự kiện game `builditem` một lần. | `builditem` | `craft_an_item_2` |
| 5 | Craft an Item | Kích hoạt sự kiện game `builditem` một lần. | `builditem` | `craft_an_item_3` |
| 6 | Craft an Item While Starving | Thực hiện khi đói bằng 0. | `builditem` | `craft_an_item_while_starving` |
| 7 | Craft an Item While Starving | Thực hiện khi đói bằng 0. | `builditem` | `craft_an_item_while_starving_2` |
| 8 | Craft an Item While Having Full Hunger | Thực hiện khi no 100%. | `builditem` | `craft_an_item_while_having_full_hunger` |
| 9 | Craft an Item While Having Full Hunger | Thực hiện khi no 100%. | `builditem` | `craft_an_item_while_having_full_hunger_2` |
| 10 | Build an Item | Kích hoạt sự kiện game `buildstructure` một lần. | `buildstructure` | `build_an_item` |
| 11 | Build a Structure | Kích hoạt sự kiện game `buildstructure` một lần. | `buildstructure` | `build_a_structure` |
| 12 | Build a Structure While Starving | Thực hiện khi đói bằng 0. | `buildstructure` | `build_a_structure_while_starving` |
| 13 | Build a Structure While Having Full Hunger | Thực hiện khi no 100%. | `buildstructure` | `build_a_structure_while_having_full_hunger` |

### Nhiệm vụ 1 — Wigfrid (yêu cầu nhân vật Wigfrid) — 23 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Attempt to Parry an Attack | Kích hoạt sự kiện game `combat_parry` một lần. | `combat_parry` | `attempt_to_parry_an_attack` |
| 2 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_5` |
| 3 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_6` |
| 4 | Attack Something | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `undefined`. | `onhitother` | `attack_something` |
| 5 | Attack Something | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `undefined`. | `onhitother` | `attack_something_2` |
| 6 | Attack Something | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `undefined`. | `onhitother` | `attack_something_3` |
| 7 | Broke Your Armor | Kích hoạt sự kiện game `armorbroke` một lần. | `armorbroke` | `broke_your_armor_2` |
| 8 | Broke Your Battle Helm | Làm vỡ/hết độ bền giáp `wathgrithrhat`. | `armorbroke` | `broke_your_battle_helm` |
| 9 | Kill Something | Kích hoạt sự kiện game `killed` một lần. | `killed` | `kill_something` |
| 10 | Kill Something | Kích hoạt sự kiện game `killed` một lần. | `killed` | `kill_something_2` |
| 11 | Kill Something While Almost Dead | Thực hiện khi máu dưới 10%. | `killed` | `kill_something_while_almost_dead` |
| 12 | Kill Something While Having Full Health | Thực hiện khi máu 100%. | `killed` | `kill_something_while_having_full_health` |
| 13 | Kill Something While Having Full Inspiration | Thực hiện khi Inspiration đạt 100%. | `killed` | `kill_something_while_having_full_inspiration` |
| 14 | Kill Something While Having 0 Song Active | Thực hiện khi có đúng 0 bài hát đang hoạt động. | `killed` | `kill_something_while_having_0_song_active` |
| 15 | Kill Something While Having 1 Song Active | Thực hiện khi có đúng 1 bài hát đang hoạt động. | `killed` | `kill_something_while_having_1_song_active` |
| 16 | Kill Something While Having 2 Song Active | Thực hiện khi có đúng 2 bài hát đang hoạt động. | `killed` | `kill_something_while_having_2_song_active` |
| 17 | Kill Something While Having 3 Song Active | Thực hiện khi có đúng 3 bài hát đang hoạt động. | `killed` | `kill_something_while_having_3_song_active` |
| 18 | Kill a Boss/Mini Boss | Tiêu diệt boss (tag `epic`) đồng thời thỏa điều kiện `nocheckfn`. | `killed` | `kill_a_boss_mini_boss_2` |
| 19 | Have a Weaponized Warble Active | Thực hiện khi buff bài hát `battlesong_durability` đang hoạt động. | `newstate` | `have_a_weaponized_warble_active` |
| 20 | Have a Heartrending Ballad Active | Thực hiện khi buff bài hát `battlesong_healthgain` đang hoạt động. | `newstate` | `have_a_heartrending_ballad_active` |
| 21 | Have a Clear Minded Cadenza Active | Thực hiện khi buff bài hát `battlesong_sanitygain` đang hoạt động. | `newstate` | `have_a_clear_minded_cadenza_active` |
| 22 | Have a Bel Canto of Courage Active | Thực hiện khi buff bài hát `battlesong_sanityaura` đang hoạt động. | `newstate` | `have_a_bel_canto_of_courage_active` |
| 23 | Have a Fireproof Falsetto Active | Thực hiện khi buff bài hát `battlesong_fireresistance` đang hoạt động. | `newstate` | `have_a_fireproof_falsetto_active` |

### Nhiệm vụ 1 — Woodie (yêu cầu nhân vật Woodie) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Attemp To Betray Lucy | Kích hoạt sự kiện game `possessedaxe` một lần. | `possessedaxe` | `attemp_to_betray_lucy` |
| 2 | Chop Down a Palmcone Tree | Hoàn tất thao tác `CHOP` trên prefab `palmconetree`. | `working` | `chop_down_a_palmcone_tree_2` |
| 3 | Chop Down a Twiggy Tree | Hoàn tất thao tác `CHOP` trên prefab `twiggytree`. | `working` | `chop_down_a_twiggy_tree_2` |
| 4 | Chop Down a Lunar Mushtree | Hoàn tất thao tác `CHOP` trên prefab `mushtree_moon`. | `working` | `chop_down_a_lunar_mushtree_2` |
| 5 | Chop Down an Evergreen | Hoàn tất thao tác `CHOP` trên prefab `evergreen`. | `working` | `chop_down_an_evergreen` |
| 6 | Chop Down a Lumpy Evergreen | Hoàn tất thao tác `CHOP` trên prefab `evergreen_sparse`. | `working` | `chop_down_a_lumpy_evergreen` |
| 7 | Chop Down a Birchnut Tree | Hoàn tất thao tác `CHOP` trên prefab `deciduoustree`. | `working` | `chop_down_a_birchnut_tree_2` |
| 8 | Chop Down Something | Hoàn tất thao tác `CHOP`. | `working` | `chop_down_something` |
| 9 | Chop Down Something | Hoàn tất thao tác `CHOP`. | `working` | `chop_down_something_2` |
| 10 | Gnaw Something While in Beaver Form | Thực hiện khi Woodie ở dạng `beaver`. | `finishedwork` | `gnaw_something_while_in_beaver_form` |
| 11 | Kill Something While in Moose Form | Thực hiện khi Woodie ở dạng `weremoose`. | `killed` | `kill_something_while_in_moose_form` |
| 12 | Kill a Spider While in Moose Form | Tiêu diệt `spider` đồng thời thỏa điều kiện `whileweremodefn, weremoose`. | `killed` | `kill_a_spider_while_in_moose_form` |
| 13 | Transform Into a Were-Moose | Biến hình sang dạng `moose`. | `transform_wereplayer` | `transform_into_a_were_moose` |
| 14 | Transform Into a Were-Goose | Biến hình sang dạng `goose`. | `transform_wereplayer` | `transform_into_a_were_goose` |
| 15 | Transform Into a Were-Beaver | Biến hình sang dạng `beaver`. | `transform_wereplayer` | `transform_into_a_were_beaver` |
| 16 | Revert From a Were-Moose | Biến hình sang dạng `moose`. | `transform_person` | `revert_from_a_were_moose` |
| 17 | Revert From a Were-Goose | Biến hình sang dạng `goose`. | `transform_person` | `revert_from_a_were_goose` |
| 18 | Revert From a Were-Beaver | Biến hình sang dạng `beaver`. | `transform_person` | `revert_from_a_were_beaver` |

### Nhiệm vụ 1 — Wortox (yêu cầu nhân vật Wortox) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat a Soul | Kích hoạt sự kiện game `oneatsoul` một lần. | `oneatsoul` | `eat_a_soul` |
| 2 | Heal Using a Soul | Nhận thay đổi máu với nguyên nhân `wortox_soul`. | `healthdelta` | `heal_using_a_soul` |
| 3 | Heal Using a Soul | Nhận thay đổi máu với nguyên nhân `wortox_soul`. | `healthdelta` | `heal_using_a_soul_2` |
| 4 | Eat a Sliced Pomegranate | Ăn vật phẩm có prefab `pomegranate_cooked`. | `oneat` | `eat_a_sliced_pomegranate` |
| 5 | Eat a Pomegranate | Ăn vật phẩm có prefab `pomegranate`. | `oneat` | `eat_a_pomegranate` |
| 6 | Plant a Flower | Đặt vật phẩm có prefab `butterfly`. | `deployitem` | `plant_a_flower_3` |
| 7 | Kill a Butterfly | Tiêu diệt sinh vật có prefab `butterfly`. | `killed` | `kill_a_butterfly` |
| 8 | Kill a Butterfly | Tiêu diệt sinh vật có prefab `butterfly`. | `killed` | `kill_a_butterfly_2` |
| 9 | Murder a Butterfly | Tiêu diệt sinh vật có prefab `butterfly`. | `murdered` | `murder_a_butterfly` |
| 10 | Get Overloaded By a Soul | Kích hoạt sự kiện game `souloverload` một lần. | `souloverload` | `get_overloaded_by_a_soul` |
| 11 | Lose All Souls | Kích hoạt sự kiện game `soulempty` một lần. | `soulempty` | `lose_all_souls` |
| 12 | Get a Soul From a Trap | Kích hoạt sự kiện game `harvesttrapsouls` một lần. | `harvesttrapsouls` | `get_a_soul_from_a_trap` |
| 13 | Do a Soul Hop | Kích hoạt sự kiện game `soulhop` một lần. | `soulhop` | `do_a_soul_hop` |
| 14 | Do a Soul Hop | Kích hoạt sự kiện game `soulhop` một lần. | `soulhop` | `do_a_soul_hop_2` |
| 15 | Do a Soul Hop | Kích hoạt sự kiện game `soulhop` một lần. | `soulhop` | `do_a_soul_hop_3` |
| 16 | Kill Krampus | Tiêu diệt sinh vật có prefab `krampus`. | `killed` | `kill_krampus_2` |
| 17 | Get Charcoal From Another Player | Nhận `charcoal` do người chơi khác đưa. | `trade` | `get_charcoal_from_another_player` |
| 18 | Get Pumpkin Cookies From Another Player | Nhận `pumpkincookie` do người chơi khác đưa. | `trade` | `get_pumpkin_cookies_from_another_player` |

### Nhiệm vụ 1 — Wurt (yêu cầu nhân vật Wurt) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat a Raw Durian | Ăn vật phẩm có prefab `durian`. | `oneat` | `eat_a_raw_durian` |
| 2 | Catch an Ocean Fish | Kích hoạt sự kiện game `fishcaught` một lần. | `fishcaught` | `catch_an_ocean_fish_2` |
| 3 | Catch a Pond Fish | Kích hoạt sự kiện game `fishingcatch` một lần. | `fishingcatch` | `catch_a_pond_fish` |
| 4 | Catch a Pond Fish | Kích hoạt sự kiện game `fishingcatch` một lần. | `fishingcatch` | `catch_a_pond_fish_2` |
| 5 | Kill a Tentacle | Tiêu diệt sinh vật có prefab `tentacle`. | `killed` | `kill_a_tentacle` |
| 6 | Kill a Tentacle | Tiêu diệt sinh vật có prefab `tentacle`. | `killed` | `kill_a_tentacle_2` |
| 7 | Kill a Pig | Tiêu diệt sinh vật có prefab `pigman`. | `killed` | `kill_a_pig_2` |
| 8 | Kill a Pig | Tiêu diệt sinh vật có prefab `pigman`. | `killed` | `kill_a_pig_3` |
| 9 | Get Fully Dried | Độ ẩm đổi thành `0`. | `moisturedelta` | `get_fully_dried` |
| 10 | Get Fully Wet | Độ ẩm đổi thành `inst.components.moisture and inst.components.moisture.maxmoisture or 100`. | `moisturedelta` | `get_fully_wet` |
| 11 | Get Fully Wet | Độ ẩm đổi thành `inst.components.moisture and inst.components.moisture.maxmoisture or 100`. | `moisturedelta` | `get_fully_wet_2` |
| 12 | Eat Something While Fully Wet | Thực hiện khi độ ẩm đang tối đa. | `oneat` | `eat_something_while_fully_wet_2` |
| 13 | Kill Something While Fully Wet | Thực hiện khi độ ẩm đang tối đa. | `killed` | `kill_something_while_fully_wet_2` |
| 14 | Rowing | Kích hoạt sự kiện game `rowing` một lần. | `rowing` | `rowing` |
| 15 | Dig a Spiky Bush | Thực hiện thao tác `DIG` lên prefab `marsh_bush`. | `finishedwork` | `dig_a_spiky_bush` |
| 16 | Plant a Spiky Bush | Đặt vật phẩm có prefab `dug_marsh_bush`. | `deployitem` | `plant_a_spiky_bush_2` |
| 17 | Pick a Spiky Bush | Thu hoạch đối tượng có prefab `marsh_bush`. | `picksomething` | `pick_a_spiky_bush` |
| 18 | Place Down Marsh Turf | Đặt vật phẩm có prefab `turf_marsh`. | `deployitem` | `place_down_marsh_turf` |

### Nhiệm vụ 1 — Wickerbottom (yêu cầu nhân vật Wickerbottom) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Fail To Read A Book | Đọc sách với kết quả success = `sai`, sách `undefined`. | `chasni_readbook` | `fail_to_read_a_book` |
| 2 | Read Birds of the World | Đọc sách với kết quả success = `đúng`, sách `book_birds`. | `chasni_readbook` | `read_birds_of_the_world` |
| 3 | Read Sleepytime Stories | Đọc sách với kết quả success = `đúng`, sách `book_sleep`. | `chasni_readbook` | `read_sleepytime_stories` |
| 4 | Read On Tentacles | Đọc sách với kết quả success = `đúng`, sách `book_tentacles`. | `chasni_readbook` | `read_on_tentacles` |
| 5 | Read The End is Nigh! | Đọc sách với kết quả success = `đúng`, sách `book_brimstone`. | `chasni_readbook` | `read_the_end_is_nigh` |
| 6 | Read Horticulture, Abridged | Đọc sách với kết quả success = `đúng`, sách `book_horticulture`. | `chasni_readbook` | `read_horticulture_abridged` |
| 7 | Read Horticulture, Expanded | Đọc sách với kết quả success = `đúng`, sách `book_horticulture_upgraded`. | `chasni_readbook` | `read_horticulture_expanded` |
| 8 | Read Applied Silviculture | Đọc sách với kết quả success = `đúng`, sách `book_silviculture`. | `chasni_readbook` | `read_applied_silviculture` |
| 9 | Read The Angler's Survival Guide | Đọc sách với kết quả success = `đúng`, sách `book_fish`. | `chasni_readbook` | `read_the_anglers_survival_guide` |
| 10 | Read Pyrokinetics Explained | Đọc sách với kết quả success = `đúng`, sách `book_fire`. | `chasni_readbook` | `read_pyrokinetics_explained` |
| 11 | Read Overcoming Arachnophobia | Đọc sách với kết quả success = `đúng`, sách `book_web`. | `chasni_readbook` | `read_overcoming_arachnophobia` |
| 12 | Read Tempering Temperatures | Đọc sách với kết quả success = `đúng`, sách `book_temperature`. | `chasni_readbook` | `read_tempering_temperatures` |
| 13 | Read Lux Aeterna | Đọc sách với kết quả success = `đúng`, sách `book_light_upgraded`. | `chasni_readbook` | `read_lux_aeterna` |
| 14 | Read Lux Aeterna Redux | Đọc sách với kết quả success = `đúng`, sách `book_temperature`. | `chasni_readbook` | `read_lux_aeterna_redux` |
| 15 | Read Practical Rain Rituals | Đọc sách với kết quả success = `đúng`, sách `book_rain`. | `chasni_readbook` | `read_practical_rain_rituals` |
| 16 | Read Lunar Grimoire | Đọc sách với kết quả success = `đúng`, sách `book_moon`. | `chasni_readbook` | `read_lunar_grimoire` |
| 17 | Read Apicultural Notes | Đọc sách với kết quả success = `đúng`, sách `book_bees`. | `chasni_readbook` | `read_apicultural_notes` |
| 18 | Read The Everything Encyclopedia | Đọc sách với kết quả success = `đúng`, sách `book_research_station`. | `chasni_readbook` | `read_the_everything_encyclopedia` |

### Nhiệm vụ 1 — Wanda (yêu cầu nhân vật Wanda) — 20 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Warp Back Using Watch | Kích hoạt sự kiện game `onwarpback` một lần. | `onwarpback` | `warp_back_using_watch` |
| 2 | Warp Back Using Watch | Kích hoạt sự kiện game `onwarpback` một lần. | `onwarpback` | `warp_back_using_watch_2` |
| 3 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_8` |
| 4 | Die | Kích hoạt sự kiện game `death` một lần. | `death` | `die_9` |
| 5 | Ressurected using Second Chance Watch | Hồi sinh bằng nguồn có prefab `pocketwatch_revive`. | `respawnfromghost` | `ressurected_using_second_chance_watch` |
| 6 | Ressurected using Second Chance Watch | Hồi sinh bằng nguồn có prefab `pocketwatch_revive`. | `respawnfromghost` | `ressurected_using_second_chance_watch_2` |
| 7 | Attack Using an Alarming Clock | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `pocketwatch_weapon`. | `onhitother` | `attack_using_an_alarming_clock` |
| 8 | Attack Using an Alarming Clock | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 0, bằng vũ khí `pocketwatch_weapon`. | `onhitother` | `attack_using_an_alarming_clock_2` |
| 9 | deal_150 | Đánh bất kỳ mục tiêu nào, sát thương lớn hơn 150, bằng vũ khí `pocketwatch_weapon`. | `onhitother` | `deal_150` |
| 10 | Get Attacked | Bị `bất kỳ` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_7` |
| 11 | Get Attacked By a Crawling Horror | Bị `crawlinghorror` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_by_a_crawling_horror` |
| 12 | Get Attacked By a Terrorbeak | Bị `terrorbeak` đánh với sát thương lớn hơn 0. | `attacked` | `get_attacked_by_a_terrorbeak` |
| 13 | Kill Something While Old | Thực hiện khi Wanda ở trạng thái tuổi `old`. | `killed` | `kill_something_while_old` |
| 14 | Kill Something While Young | Thực hiện khi Wanda ở trạng thái tuổi `young`. | `killed` | `kill_something_while_young` |
| 15 | Kill a Terrorbeak | Tiêu diệt sinh vật có prefab `terrorbeak`. | `killed` | `kill_a_terrorbeak_2` |
| 16 | Kill a Terrorbeak While Old | Tiêu diệt `terrorbeak` đồng thời thỏa điều kiện `whileagefn, old`. | `killed` | `kill_a_terrorbeak_while_old` |
| 17 | Kill a Terrorbeak While Young | Tiêu diệt `terrorbeak` đồng thời thỏa điều kiện `whileagefn, young`. | `killed` | `kill_a_terrorbeak_while_young` |
| 18 | Kill a Crawling Horror | Tiêu diệt sinh vật có prefab `crawlinghorror`. | `killed` | `kill_a_crawling_horror` |
| 19 | Kill a Crawling Horror While Old | Tiêu diệt `crawlinghorror` đồng thời thỏa điều kiện `whileagefn, old`. | `killed` | `kill_a_crawling_horror_while_old` |
| 20 | Kill a Crawling Horror While Young | Tiêu diệt `crawlinghorror` đồng thời thỏa điều kiện `whileagefn, young`. | `killed` | `kill_a_crawling_horror_while_young` |

### Nhiệm vụ 1 — Maxwell (yêu cầu nhân vật Maxwell) — 18 mục

| # | Nhiệm vụ (chuỗi nguồn VI) | Cách làm theo code | Event | ID |
|---:|---|---|---|---|
| 1 | Eat a Lobster Dinner | Ăn vật phẩm có prefab `lobsterdinner`. | `oneat` | `eat_a_lobster_dinner` |
| 2 | Kill a Terrorbeak | Tiêu diệt sinh vật có prefab `terrorbeak`. | `killed` | `kill_a_terrorbeak_3` |
| 3 | Kill a Crawling Horror | Tiêu diệt sinh vật có prefab `crawlinghorror`. | `killed` | `kill_a_crawling_horror_2` |
| 4 | Kill a Shadow Worker | Tiêu diệt sinh vật có prefab `shadowworker`. | `killed` | `kill_a_shadow_worker` |
| 5 | Kill a Shadow Worker | Tiêu diệt sinh vật có prefab `shadowworker`. | `killed` | `kill_a_shadow_worker_2` |
| 6 | Kill a Shadow Duelist | Tiêu diệt sinh vật có prefab `shadowprotector`. | `killed` | `kill_a_shadow_duelist` |
| 7 | Eat Something While Insane | Thực hiện khi đang Insane. | `oneat` | `eat_something_while_insane_2` |
| 8 | Eat Something While Insane | Thực hiện khi đang Insane. | `oneat` | `eat_something_while_insane_3` |
| 9 | Equip a Level 1 Or Higher Shadow Equipment | Trang bị đồ bóng tối có cấp lớn hơn 0. | `equip` | `equip_a_level_1_or_higher_shadow_equipment` |
| 10 | Equip a Level 1 Or Higher Shadow Equipment | Trang bị đồ bóng tối có cấp lớn hơn 0. | `equip` | `equip_a_level_1_or_higher_shadow_equipment_2` |
| 11 | Equip a Level 2 Or Higher Shadow Equipment | Trang bị đồ bóng tối có cấp lớn hơn 1. | `equip` | `equip_a_level_2_or_higher_shadow_equipment` |
| 12 | Equip a Level 2 Or Higher Shadow Equipment | Trang bị đồ bóng tối có cấp lớn hơn 1. | `equip` | `equip_a_level_2_or_higher_shadow_equipment_2` |
| 13 | Equip a Level 3 Or Higher Shadow Equipment | Trang bị đồ bóng tối có cấp lớn hơn 2. | `equip` | `equip_a_level_3_or_higher_shadow_equipment` |
| 14 | Equip a Level 4 Or Higher Shadow Equipment | Trang bị đồ bóng tối có cấp lớn hơn 3. | `equip` | `equip_a_level_4_or_higher_shadow_equipment` |
| 15 | Kill Something While Insane | Thực hiện khi đang Insane. | `killed` | `kill_something_while_insane` |
| 16 | Kill a Rabbit While Insane | Tiêu diệt `rabbit` đồng thời thỏa điều kiện `whilecrazy, sai`. | `killed` | `kill_a_rabbit_while_insane` |
| 17 | Kill a Bunnyman While Insane | Tiêu diệt `bunnyman` đồng thời thỏa điều kiện `whilecrazy, sai`. | `killed` | `kill_a_bunnyman_while_insane` |
| 18 | Kill a Crawling Horror While Insane | Tiêu diệt `crawlinghorror` đồng thời thỏa điều kiện `whilecrazy, sai`. | `killed` | `kill_a_crawling_horror_while_insane` |

## Toàn bộ thành tựu

“Sao” là `coinget` trong bảng dữ liệu. “Mục tiêu” là `current`; mục không có `current` chỉ cần kích hoạt điều kiện một lần.

### Ăn uống — 14 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `eatcold` | Ngày Nắng Nóng | Ăn một món ăn để hạ nhiệt | 1 lần | 1 | Mọi nhân vật |
| `eatfavourite` | Ngon vãi | Ăn 5 món ăn yêu thích của nhân vật | 5 | 2 | Mọi nhân vật |
| `eatgear` | Nâng cấp | Ăn 5 Gears | 5 | 7 | WX-78 |
| `eatguardianhorn` | Hụt tay hở? | Ăn sừng của Guardian's | 1 lần | 2 | Mọi nhân vật |
| `eathot` | Đêm Gió Lạnh | Ăn một món ăn để tăng nhiệt | 1 lần | 1 | Mọi nhân vật |
| `eatkitschyidol` | Đồ ăn tẩm đớ | Ăn tất cả Kitschy Idols | Đủ danh sách (3) | 7 | Woodie |
| `eatmandrake` | Bú cần time 420 | Ăn Nhân Săm nấu chín | 1 lần | 3 | Mọi nhân vật |
| `eatmonsterlasagna` | Ngấu nghiến | Ăn 10 monster lasagna trong 60 giây | 10 | 3 | Mọi nhân vật |
| `eatnightberry` | Why Am I Not Glowing? | Eat a cooked nightberry | 1 lần | 4 | Mọi nhân vật |
| `feedlivinglog` | Tormented Scream | Feed Living Log to Cookie Cutter | 1 lần | 2 | Mọi nhân vật |
| `feedplayer` | Đút cho tớ ăn đi | Đút cho người khác 15 lần với món ăn | 15 | 2 | Mọi nhân vật |
| `feedwebber` | Búp bê tình cho bé | Cho nhện lang thang ăn tất cả Switcherdoodle | Đủ danh sách (7) | 14 | Mọi nhân vật |
| `foodwarly` | 5-Star Fine Dining | Cook all of Warly's special dishes | Đủ danh sách (7) | 14 | Warly |
| `supereat` | Sành ăn | Đớp 500 đồ ăn | 500 | 5 | Mọi nhân vật |

### Sinh tồn / hồi sinh — 11 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `death` | Thần chết quá quen | Chết 5.0 lần | 5 | 2 | Mọi nhân vật |
| `diecharlie` | Ma mới? | Chết bởi bóng tối | 1 lần | 1 | Mọi nhân vật |
| `diemeteor` | Meteor Doom | Get killed by a meteor shower | 1 lần | 2 | Mọi nhân vật |
| `diepoison` | Cái chết tiều tụy | Mục nát trong một đám mây bào tử | 1 lần | 2 | Mọi nhân vật |
| `dierose` | Beautiful Goodbye | Die from a rose | 1 lần | 3 | Mọi nhân vật |
| `healtillweed` | Phương thuốc ĐẦU ĐẤT | Chữa bệnh bằng Bông Tillweed | 1 lần | 3 | Mọi nhân vật |
| `healwortox` | Máu từ địa ngục | Hồi máu với Linh Hồn Wortox 30.0 lần | 30 | 10 | Mọi nhân vật; cần Wortox hồi máu |
| `revive` | ĐẤNG!!! | Hồi sinh người khác 2.0 lần | 2 | 3 | Mọi nhân vật |
| `reviveamulet` | Hồi quang phản chiếu | Hồi sinh 2.0lần với một dây chuyền | 2 | 3 | Mọi nhân vật |
| `reviveeffigy` | Bù nhìn ma ám | Hồi sinh với một bù nhìn thịt | 1 lần | 2 | Mọi nhân vật |
| `revivewanda` | Cơ hội thứ 2 | Hồi sinh với một Second Chance Watch | 1 lần | 8 | Mọi nhân vật; cần Wanda hồi sinh |

### Sát thương — 8 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `burn` | Nóng cháy đít | Bắt lửa | 1 lần | 1 | Mọi nhân vật |
| `damagedeal` | Độc ác | Gây 100000.0 sát thương | 100000 | 8 | Mọi nhân vật |
| `dmgnodmg` | Thánh né | Gây 5.0k sát thương khi không nhận sát thương | 5000 | 13 | Mọi nhân vật |
| `drown` | Sung quanh toàn là nước Êi | Thử bơi ngoài biển | 1 lần | 1 | Mọi nhân vật |
| `freeze` | Lạnh thấu xương | Bị đóng băng | 1 lần | 1 | Mọi nhân vật |
| `lightning` | Trời đánh | Bị đánh trúng bởi sấm sét | 1 lần | 2 | Mọi nhân vật |
| `pacifist` | Hòa Bình | Không nhận sát thương trong 100.0 phút | 6000 | 7 | Mọi nhân vật |
| `tank` | Da dày | Nhận 10000.0 sát thương | 10000 | 10 | Mọi nhân vật |

### Lao động — 14 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `buildmaster` | Nghệ nhân | Chế tạo 200.0 lần | 200 | 6 | Mọi nhân vật |
| `chopmaster` | Bổ củi | Bổ hoặc đào 60.0 cây | 60 | 2 | Mọi nhân vật |
| `cookmaster` | Bếp trưởng | Làm 100.0 món ăn nồi hầm | 100 | 4 | Mọi nhân vật |
| `fertilizebigmaster` | Bón cây to | Bón phân cho cây lớn 2.0 lần | 2 | 10 | Mọi nhân vật |
| `fertilizemaster` | Bón cây | Bón phân cho cây 30.0 lần | 30 | 4 | Mọi nhân vật |
| `fishmaster` | Ngư ông | Bắt 10.0 cá | 10 | 2 | Mọi nhân vật |
| `flowermaster` | Gái bán hoa | Trồng hoa 12.0 lần | 12 | 1 | Mọi nhân vật |
| `honeymaster` | Nuôi ong | Thu hoạch mật ong từ một hộp ong đầy 40.0 lần | 40 | 6 | Mọi nhân vật |
| `jerkymaster` | Sunbather | Harvest drying rack 50.0 times | 50 | 5 | Mọi nhân vật |
| `minemaster` | Đập đá | Đập đá 50.0 lần | 50 | 2 | Mọi nhân vật |
| `pickmaster` | Tích trữ | Thu hoạch 200.0 lần | 200 | 2 | Mọi nhân vật |
| `picktumbleweed` | Tấn công trại cỏ | nhặt 20.0 Tumbleweed | 20 | 4 | Mọi nhân vật |
| `plantmaster` | Làm vườn | Trồng 60.0 cây hoặc hạt giống | 60 | 3 | Mọi nhân vật |
| `wallmaster` | Chủ tịch | Xây tường 50.0 lần | 50 | 3 | Mọi nhân vật |

### Sở hữu / sưu tập — 13 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `craftnet` | High Net Worth | Craft a thulecite bug net | 1 lần | 7 | Mọi nhân vật |
| `cursedtrinket` | HÚ Hú KHẸC Khẹc | Có 10.0 Accursed Trinket | 10 | 10 | Mọi nhân vật |
| `darkheart` | Hollow Heart | Have a possessed shadow atrium | 1 lần | 12 | Mọi nhân vật |
| `equipingkrampussack` | Phú bà phú ông | Có một Krampus Sack | 1 lần | 8 | Mọi nhân vật |
| `equipingskin` | Nạp lần đầu | Sử dụng vật phẩm skin | 1 lần | 2 | Mọi nhân vật |
| `giantplant` | Bàn tay xanh lá | Giữ toàn bộ các cây khổng lồ trên lưng | Đủ danh sách (14) | 20 | Mọi nhân vật |
| `glassmaker` | Glassblower | Hold all glass spikes and castle in your hands | Đủ danh sách (4) | 11 | Mọi nhân vật |
| `havebird` | Aviculturist | Put each species of bird in cage | Đủ danh sách (8) | 30 | Mọi nhân vật |
| `iridescentgems` | 7 Sắc cầu vồng | Chế tạo gem 7 màu | 1 lần | 7 | Mọi nhân vật |
| `luckyrabbit` | Oswald the Lucky Rabbit | Have a fortuitous rabbit | 1 lần | 12 | Mọi nhân vật |
| `oceanfish` | Aquarists | Fish over 16.0 different ocean fish | Đủ danh sách (16) | 25 | Mọi nhân vật |
| `spore` | Phê đến ngày mai | Có 3.0 red, green and blue spores | 3 | 8 | Mọi nhân vật |
| `wickerbook` | Librarian | Craft all Wickerbottom books | Đủ danh sách (17) | 9 | Wickerbottom |

### Trạng thái — 11 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `firebody` | Quá Nhiệt | Quá nhiệt trong 50.0 phút | 3000 | 12 | Mọi nhân vật |
| `fullhunger` | Đầy bụng | Có trên 95% hunger trong 300.0 phút | 18000 | 10 | Mọi nhân vật |
| `fullmighty` | Thể thao | Có trên 95% mightiness trong 60.0 phút | 3600 | 10 | Wolfgang |
| `fullsanity` | Thông thái | Có trên 95% sanity trong 300.0 phút | 18000 | 10 | Mọi nhân vật |
| `fullsinginsp` | Ca sĩ hàng hiệu | Có trên 95% Inspiration trong 60.0 phút | 3600 | 10 | Wigfrid |
| `icebody` | Cô bé bán diêm | Đóng băng trong 50.0 phút | 3000 | 12 | Mọi nhân vật |
| `lunacy` | Giác ngộ | Lunatic trong 100.0 phút | 6000 | 12 | Mọi nhân vật |
| `moistbody` | Con mèo ướt át | Bị ướt trong 100.0 phút | 6000 | 12 | Mọi nhân vật |
| `nosanity` | Bại não | Điên trong 100.0 phút | 6000 | 12 | Mọi nhân vật |
| `sanitymaxwell` | Tâm thần | Giảm tối đa 50% sanity trong 10.0 phút | 600 | 10 | Maxwell |
| `starve` | Chết đói cùng nhau | Đói trong 50.0 phút | 3000 | 12 | Mọi nhân vật |

### Kết bạn — 9 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `friendbunny` | Đại đội thỏ | Làm bạn với 5.0 bunnymen | 5 | 1 | Mọi nhân vật |
| `friendcat` | Băng đảng mèo | Làm bạn với 6.0 catcoons | 6 | 4 | Mọi nhân vật |
| `friendclockwork` | Thuần hóa Xe Tăng | Làm bạn với 3.0 Damaged Clockwork Rook | 3 | 7 | Mọi nhân vật |
| `friendlylavae` | Coi chừng cháy nhà | Ấp trứng dung nham nóng | 1 lần | 11 | Mọi nhân vật |
| `friendmerm` | Đại ka lũ cá | Làm bạn với 5.0 Merm | 5 | 8 | Mọi nhân vật |
| `friendrocky` | Đội trưởng đá thủ | Làm bạn với 5.0 rock lobsters | 5 | 1 | Mọi nhân vật |
| `mandrake` | Người buôn đớ | Làm bạn với 2.0 mandrakes | 2 | 3 | Mọi nhân vật |
| `smallbird` | Trẻ trâu | Ấp trứng chim cao | 1 lần | 8 | Mọi nhân vật |
| `snowchester` | Lạnh như tủ lạnh | Biến chester thành tủ đông | 1 lần | 1 | Mọi nhân vật |

### Tương tác — 10 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `buygears` | Pedlar of Wares | Buy Gears from Wandering Trader | 1 lần | 3 | Mọi nhân vật |
| `dance` | Ngôi sao nhảy múa | Vui vẻ cùng bạn bè (Chat Wheel) | 5 | 1 | Mọi nhân vật |
| `dodgecharlie` | Chị chị em em | Né 7.0 Charlie Attack bằng Winona | 7 | 7 | Winona |
| `floatparty` | Skinny Deep | Floating on the ocean with your friends | 1 lần | 1 | Mọi nhân vật |
| `icetrading` | Trader But Cold | Give 2.0 big fish to Frostjaw | 2 | 12 | Mọi nhân vật |
| `pearlparty` | Pool Party | Soaking in a pool with Pearl | 1 lần | 4 | Mọi nhân vật |
| `pearltrading` | She Sells Seashells | Give 2.0 stuff other than fish to Pearl | 2 | 4 | Mọi nhân vật |
| `pigkingtrading` | Trader | Give 3.0 trinkets to Pig King | 3 | 1 | Mọi nhân vật |
| `pipspook` | Linh hồn Siêu Thoát | Giúp 5.0 Pipspooks | 5 | 10 | Mọi nhân vật |
| `wagstafftrading` | Reliable Assistant | Give 2.0 tools to Grainy Transmission | 2 | 7 | Mọi nhân vật |

### Hành vi xấu — 13 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `hauntpig` | Người Sói biến hình | Ám 10.0 Pigman | 10 | 2 | Mọi nhân vật |
| `hitstagehand` | Oh No.. Our Table, It's Broken | Hits Stagehand till it gave up | 1 lần | 1 | Mọi nhân vật |
| `killbird` | Chim thuyệt chủng | Giết 15.0 chim không thù địch | 15 | 1 | Mọi nhân vật |
| `killbutterfly` | Diệt cả lò Bướm | Giết 50.0 bướm | 50 | 5 | Mọi nhân vật |
| `killchester` | Double Kill | Giết Chester | 1 lần | 1 | Mọi nhân vật |
| `killfriendlyfruitfly` | Ultra Kill | giết Friendly Fruit Fly | 1 lần | 6 | Mọi nhân vật |
| `killgloomer` | First Blood | Giết Glommer | 1 lần | 2 | Mọi nhân vật |
| `killhutch` | Tripple Kill | Giết Fugu Hutch trong khi chết | 1 lần | 7 | Mọi nhân vật |
| `killotterhouse` | Home Wrecker | Destroy marotter den | 1 lần | 2 | Mọi nhân vật |
| `passtrinket` | Trăn trối | Chuyển Cursed trinket cho người chơi khác | 1 lần | 8 | Mọi nhân vật |
| `playwes` | Chúa Hề | Chơi nhân vật wes | 1 lần | 6 | Wes |
| `vilewormwood` | Chơi khăm | Phá hủy 15.0 cây gần WormWood | 15 | 10 | Mọi nhân vật; cần Wormwood ở gần |
| `waterballoon` | Cuộc chiến ướt át | Ném 5.0 bóng nước cho người chơi khác | 5 | 2 | Mọi nhân vật |

### Tiêu diệt — 10 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `beardlord` | Phản Quốc | Giết 5.0 Beardlords | 5 | 1 | Mọi nhân vật |
| `beefalo` | Khát máu | Giết 5.0 Bò đít đỏ | 5 | 1 | Mọi nhân vật |
| `birchnut` | Bóng cười | Chặt 2.0 poison birchnut trees | 2 | 2 | Mọi nhân vật |
| `horrorhound` | Xác sống | Giết 8.0 chó luna | 8 | 3 | Mọi nhân vật |
| `koalefant` | Săn ngà | Giết 2.0 winter Koalefants | 2 | 2 | Mọi nhân vật |
| `lightninggoat` | 100 ngàn Volt | Giết 5.0 charged volt goats | 5 | 3 | Mọi nhân vật |
| `mosling` | Gà quay | Giết 5.0 Enraged Moslings | 5 | 2 | Mọi nhân vật |
| `saladmander` | Hoa quả nổi giận | Giết 4.0 thạch sùng đỏ | 4 | 2 | Mọi nhân vật |
| `snurtle` | Shell Cracker | Kill 2.0 Snurtle | 2 | 2 | Mọi nhân vật |
| `werepig` | Người Sói | Giết 5.0 heo sói | 5 | 1 | Mọi nhân vật |

### Tiêu diệt 2 — 4 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `cavemite` | Mite Bite | Kill 2.0 Geothermite that imbued with Miasma | 2 | 7 | Mọi nhân vật |
| `darkcentipede` | Dollarpede | Kill Mega Blight with more than 15 body segments | 1 lần | 15 | Mọi nhân vật |
| `moonfrog` | Dead in the Water | Kill 5.0 Bright-Eyed Frog | 5 | 5 | Mọi nhân vật |
| `vulture` | Death from above | Kill 3.0 Crystal-Crested Buzzard | 3 | 6 | Mọi nhân vật |

### Solo / săn — 12 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `bigworm` | Alaskan Bull Worm | Solo kill a great depths worm | 1 lần | 9 | Mọi nhân vật |
| `ewecus` | Cái gì dính thế? | Một mình đánh bại an Ewecus | 1 lần | 5 | Mọi nhân vật |
| `ghost` | Thợ Săn Ma | Một mình đánh bại a Ghost | 1 lần | 1 | Mọi nhân vật |
| `gnarwail` | Hỏny | Một mình đánh bại a Gnarwail | 1 lần | 8 | Mọi nhân vật |
| `grassgator` | Chinh phục Florida | Một mình đánh bại 3.0 Grass Gator | 3 | 2 | Mọi nhân vật |
| `lavae` | Đùa với lửa | Một mình đánh bại 8.0 lavaes | 8 | 3 | Mọi nhân vật |
| `pengul` | Xác sống 2 | Một mình đánh bại 7.0 Moonrock Pengull | 7 | 2 | Mọi nhân vật |
| `rockjaw` | Tiệc cá mập | Một mình đánh bại a Rockjaw | 1 lần | 8 | Mọi nhân vật |
| `seaweed` | Cưới nước | Một mình đánh bại 6.0 Sea Weed | 6 | 5 | Mọi nhân vật |
| `soloyourself` | Refflection | Solo kill your own Deadelgänger | 1 lần | 10 | Mọi nhân vật |
| `spiderqueen` | Chúa nhện | Một mình đánh bại 4.0 spiderqueens | 4 | 3 | Mọi nhân vật |
| `tentapillar` | Bộ sưu tập Hentai | Một mình đánh bại 4.0 tentapillars | 4 | 2 | Mọi nhân vật |

### Boss — 13 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `ancientguardianancientfuelweaver` | Ancient Killer | Defeat ancient bosses | 1 lần | 25 | Mọi nhân vật |
| `celestialchampion` | Nhật Thực | Giết the Celestial Champion | 1 lần | 40 | Mọi nhân vật |
| `celestialscion` | Total Moon Eclipse | Defeat the Celestial Scion | 1 lần | 75 | Mọi nhân vật |
| `dragonflybeequeen` | Insecticide | Defeat insect bosses | 1 lần | 26 | Mọi nhân vật |
| `guardtower` | Short Circuit | Kill 4.0 Ancient Guard Tower | 4 | 114 | Mọi nhân vật |
| `malbatrosscrabking` | Watery Grave | Defeat ocean bosses | 1 lần | 60 | Mọi nhân vật |
| `mutationboss` | Mutational Fighter | Kill all mutated bosses | 1 lần | 42 | Mọi nhân vật |
| `santaklaus` | Nghiến Răng | Giết Klaus | 1 lần | 19 | Mọi nhân vật |
| `seasonboss` | Chiến binh thực thụ | Giết all seasonal bosses | 1 lần | 28 | Mọi nhân vật |
| `shadowpieche` | Chinh phục bóng tối | Giết all the level 3 Shadow Knight, Bishop and Rook | 1 lần | 27 | Mọi nhân vật |
| `toadstool` | Con cóc ghẻ | Giết Misery Toadstool | 1 lần | 15 | Mọi nhân vật |
| `twinterror` | TERRARIA!! | Giết Retinazor and Spazmatism | 1 lần | 9 | Mọi nhân vật |
| `werepigs` | Homo Troglodytes | Defeat the werepigs | 1 lần | 17 | Mọi nhân vật |

### Khác — 9 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `aquarium` | Functional Aquarium | Fill icker preserve with usefull fish | 1 lần | 5 | Mọi nhân vật |
| `bernie` | Búp bê Asley | Biến bernie thành bernie lớn | 1 lần | 7 | Willow |
| `minemoon` | Mine Moon | Mine 3.0 glassed hot spring | 3 | 3 | Mọi nhân vật |
| `opentreasure` | Kho báu X | Mở một Sunken Chest | 1 lần | 6 | Mọi nhân vật |
| `piratechest` | X marks the spot | Dig a Pirate Stash | 1 lần | 11 | Mọi nhân vật |
| `sacrificecotl` | Cult Member | Cook rabit in Lamb Idol | 1 lần | 1 | Mọi nhân vật |
| `sewing` | Thợ may? | Sử dụng Sewing Kit | 1 lần | 1 | Mọi nhân vật |
| `sitting` | Witnessing Chair | Sit | 1 lần | 2 | Mọi nhân vật |
| `wither` | Bông hoa bị lãng quên | Nhặt 3.0 Withered Flowers | 3 | 3 | Mọi nhân vật |

### Quãng đường / thời gian — 12 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `caveage` | Gái cave | Ở 500.0 phút trong hang | 30000 | 10 | Mọi nhân vật |
| `complete` | Tốt nghiệp | Hoàn thành tất cả các thành tựu | 0 | 100 | Mọi nhân vật |
| `didtask` | Super Star | Finish 40.0 seasonal task achievements | 40 | 8 | Mọi nhân vật |
| `intogame` | Khởi đầu mới | Bước vào thế giới | 1 lần | 10 | Mọi nhân vật |
| `oldage` | Sống lâu trăm tuổi | Sống 1000.0 ngày | 1000 | 25 | Mọi nhân vật |
| `rider` | Cao bồi | Cưỡi bò trong 30.0 phút | 1800 | 11 | Mọi nhân vật |
| `riderwoby` | Con chó này lớn quá | Cưỡi Woby trong 30.0 phút | 1800 | 8 | Walter |
| `starspent` | Siêu Sao | Xài 500.0 sao | 500 | 20 | Mọi nhân vật |
| `stopalot` | TƯỢNG! | Đứng im trong 1000.0 phút | 60000 | 10 | Mọi nhân vật |
| `walkalot` | Leo núi | Đi bộ 1000.0 phút | 60000 | 10 | Mọi nhân vật |
| `walkturf` | Nhà thám hiểm | Đi được 30.0 turfs khác nhau | Đủ danh sách (30) | 15 | Mọi nhân vật |
| `waterage` | Thủy thủ | Ở 500.0 phút không trên đất liền | 30000 | 10 | Mọi nhân vật |

### Nhiệm vụ mùa — 6 thành tựu

| ID | Tên | Cách hoàn thành / mô tả | Mục tiêu | Sao | Nhân vật yêu cầu |
|---|---|---|---:|---:|---|
| `task1` | Seasonal task 1 | 1 | 1 lần | 0 | Mọi nhân vật |
| `task2` | Seasonal task 2 | 2 | 1 lần | 0 | Mọi nhân vật |
| `task3` | Seasonal task 3 | 3 | 1 lần | 0 | Mọi nhân vật |
| `task4` | Seasonal task 4 | 4 | 1 lần | 0 | Mọi nhân vật |
| `task5` | Seasonal task 5 | 5 | 10 | 0 | Mọi nhân vật |
| `task6` | Seasonal task 6 | 6 | 10 | 0 | Mọi nhân vật |

## Toàn bộ perk/kỹ năng đổi bằng Sao

Chi phí dưới đây là chi phí gốc trước khi áp dụng cấu hình `Perk Cost Modifier`. Perk có `multi` tăng giá theo số lần đã mua.

### Thuộc tính — 21 perk

| ID | Tên | Hiệu ứng (chuỗi nguồn VI) | Giá gốc | Nhân vật/phạm vi | Ghi chú dữ liệu |
|---|---|---|---:|---|---|
| `absorbup` | Defense + | Tăng defense lên 3% | 5 | Mọi nhân vật | multi=2; custom=absorbuppick |
| `criticaldmgup` | Critical Damage + | Increase critical damage by 1% | 1 | Mọi nhân vật | multi=10 |
| `criticalup` | Critical Hit + | Tăng tỉ lệ nhân đôi damage lên 1% | 1 | Mọi nhân vật | multi=10; custom=criticaluppick |
| `damageup` | Damage + | Tăng damage lên 1% | 5 | Mọi nhân vật | multi=2 |
| `fireflylightup` | Dim Light + | Tỏa ánh sáng xung quanh bạn với bán kính ngày càng tăng. | 10 | Mọi nhân vật | multi=100 |
| `healthregenup` | Health Regen + | Tăng health regen lên 0.1/s | 3 | Mọi nhân vật | multi=10 |
| `healthup` | Health + | Tăng health lên 3 | 1 | Mọi nhân vật | multi=20 |
| `hungerrateup` | Hunger Rate - | Giảm hunger rate xuống 1% | 2 | Mọi nhân vật | multi=10; custom=hungerrateuppick |
| `hungerup` | Hunger + | Tăng hunger lên 3 | 1 | Mọi nhân vật | multi=20 |
| `krampussackup` | Sack Seeker | Increase the drop chance of Krampus Sack by 5% | 3 | Mọi nhân vật | multi=100 |
| `lifestealup` | Lifesteal + | Tăng lifesteal lên 0.5% of your damage | 5 | Mọi nhân vật | multi=2 |
| `planarabsorbup` | Planar Defense + | Increase planar defense by 0.25 | 2 | Mọi nhân vật | multi=4 |
| `planardamageup` | Planar Damage + | Increase planar damage by 0.5 | 3 | Mọi nhân vật | multi=5 |
| `repairfoodup` | Tinh linh | spoilage items in your inventory slowly refreshed | 15 | Mọi nhân vật | multi=100 |
| `repairitemup` | Giả kim | Vũ khí, áo giáp và quần áo được trang bị dần được sửa chữa | 25 | Mọi nhân vật | multi=100 |
| `repairmagiup` | Pháp sư | Các vật phẩm ma thuật được trang bị dần được sửa chữa | 20 | Mọi nhân vật | multi=100 |
| `sanityregenup` | Sanity Regen + | Tăng sanity regen lên 0.1/s | 3 | Mọi nhân vật | multi=10 |
| `sanityup` | Sanity + | Tăng sanity lên 3 | 1 | Mọi nhân vật | multi=20 |
| `scaleup` | Scale + | Tăng kích thước của nhân vật lên 1% | 5 | Mọi nhân vật | multi=100 |
| `speedup` | Speed + | Tăng movement speed lên 1% | 5 | Mọi nhân vật | multi=2 |
| `xpmultup` | XP Multiplier + | Increase the XP gained by 5% | 1 | Mọi nhân vật | multi=2 |

### Khả năng — 22 perk

| ID | Tên | Hiệu ứng (chuỗi nguồn VI) | Giá gốc | Nhân vật/phạm vi | Ghi chú dữ liệu |
|---|---|---|---:|---|---|
| `blueprintextractor` | Human Cartographer | Able to deconstructs some paper into some materials | 15 | Mọi nhân vật | — |
| `buildcheaper` | Bậc thầy chế tác | Chế tạo vật phẩm yêu cầu một nửa nguyên liệu | 100 | Mọi nhân vật | — |
| `chopfaster` | Máy cưa | Chặt cây ngay lập tức | 10 | Mọi nhân vật | — |
| `christmastbulb` | Ornamemento | Able to ornament to gain certain special abilities | 15 | Mọi nhân vật | — |
| `cookfaster` | Siêu đầu bếp | làm món ăn trên nồi hầm lập tức | 5 | Mọi nhân vật | — |
| `doubledrop` | Khát máu | Nhận gấp đôi chiến lợi phẩm khi tiêu diệt quái vật | 100 | Mọi nhân vật | — |
| `doublehealed` | Trị liệu Sư | Vật phẩm hồi máu, hồi máu x2 | 25 | Mọi nhân vật | — |
| `doublepick` | Thu hoạch | Vật phẩm thu hoạch được gấp đôi | 40 | Mọi nhân vật | — |
| `doubleworkdrop` | Effective worker | Gain double loot from tree and boulders | 25 | Mọi nhân vật | — |
| `fastworker` | Tay nhanh | Nhặt và chế tạo nhanh hơn | 30 | Mọi nhân vật | — |
| `firemaster` | Kháng nóng | Miễn nhiễm với quá nhiệt | 50 | Mọi nhân vật | — |
| `fishfaster` | Ngư thần | Bắt cá ngay lập tức | 10 | Mọi nhân vật | — |
| `icemaster` | Kháng lạnh | Miễn nhiễm với lạnh | 50 | Mọi nhân vật | — |
| `itemcleaner` | Human Garbage Disposal | Active : Clean up the world to get XP | 5 | Mọi nhân vật | — |
| `itemmerger` | Human Smelter | Active : Merge inventory items durability | 5 | Mọi nhân vật | — |
| `minefaster` | Búa tạ | Đào đá ngay lập tức | 5 | Mọi nhân vật | — |
| `nomoist` | Kháng mưa | Không bị ướt từ mưa | 40 | Mọi nhân vật | — |
| `sharemap` | Human Navigator | Active : Share map progress to other player | 5 | Mọi nhân vật | — |
| `strongergrip` | Strong Grip | Stronger grip, Cannot be disarmed | 10 | Mọi nhân vật | — |
| `supercritter` | Super Pet | Critter following you will gain additional passives | 20 | Mọi nhân vật | — |
| `trinketowner` | Enchantmemento | Able to equip trinkets to gain ability | 15 | Mọi nhân vật | — |
| `warlychef` | Michelin 5 Sao | Có được khả năng sử dụng đồ dùng nhà bếp màu đỏ | 10 | Mọi nhân vật | — |

### Chuyên môn nhân vật — 44 perk

| ID | Tên | Hiệu ứng (chuỗi nguồn VI) | Giá gốc | Nhân vật/phạm vi | Ghi chú dữ liệu |
|---|---|---|---:|---|---|
| `expertwalter1` | Sức mạnh Tình bạn | Woby lớn mãi mãi (?) | 5 | Walter | — |
| `expertwalter3` | Hermes Blessing | Có thể chế tạo các vật phẩm đặc biệt | 25 | Walter | — |
| `expertwalter4` | Projectile Prodigy | Can craft special slingshot ammo | 55 | Walter | — |
| `expertwanda1` | Giờ giải lao | Có thể chế tạo thêm đồng hồ | 100 | Wanda | — |
| `expertwanda2` | Thêm giờ nghỉ | Túi đồng hồ mạnh hơn | 20 | Wanda | — |
| `expertwarly3` | Đầu bếp kỹ tính | Có thể chế tạo vũ khí đặc biệt | 65 | Warly | — |
| `expertwarly4` | Cultured Chef | Can craft new portable griller that can cook new stuff | 50 | Warly | — |
| `expertwathg1` | Phước lành Zeus | Có thể chế tạo vật phẩm đặc biệt | 65 | Wigfrid | — |
| `expertwathg2` | Diva hàng hiệu | Có thể chế tạo thêm sách chiến đấu | 60 | Wigfrid | — |
| `expertwaxwell2` | Quỷ dữ | Gây - Nhận ít sát thương         từ bóng tối, nhưng... | 5 | Maxwell | — |
| `expertwaxwell3` | Phước lành Erebus | Có thể chế tạo những công cụ đặc biệt | 5 | Maxwell | — |
| `expertwaxwell4` | Cursed knowledge | Can use codex umbra to cast new spells | 20 | Maxwell | — |
| `expertwebber1` | Crawlers Caller | Spawns Random Spider         while using Spiderhat | 15 | Webber | — |
| `expertwebber2` | Fluffy Whisperer | Can craft Fluffy house       and befriend Fluffy | 15 | Webber | — |
| `expertwebber3` | Arachne Blessing | Can craft special masks | 30 | Webber | — |
| `expertwendy1` | (Un)Stable Concoction | Stronger ghostly elixirs | 65 | Wendy | — |
| `expertwendy2` | José Valim | Can craft new elixirs | 50 | Wendy | — |
| `expertwendy3` | Ghostly Bond | Sisturn gain additional          effects | 30 | Wendy | — |
| `expertwes1` | Nhân vật chúa hề | Nhận 100% Thêm XP | 20 | Wes | — |
| `expertwes2` | Đùa không vui | Có thể chế tạo thêm bong bóng | 25 | Wes | — |
| `expertwicker2` | Ma pháp chương I | Sách ma pháp mạnh hơn | 45 | Wickerbottom | — |
| `expertwicker3` | Ma pháp chương II | Có thể chế tạo sách mới | 65 | Wickerbottom | — |
| `expertwillow3` | Phước lành Hephaestus | Có thể chế tạo vật phẩm đặc biệt | 65 | Willow | — |
| `expertwillow4` | Ember Spirit | Can use Ethereal Embers to cast new spells | 50 | Willow | — |
| `expertwilson1` | Kẻ ăn Moonlens | Có thể ăn Moonlens để nhận           vĩnh viễn chỉ số | 25 | Wilson | — |
| `expertwilson2` | Đá vô cực | Có đá quý trong kho đồ            mang lại lợi ích | 35 | Wilson | — |
| `expertwinona1` | Thợ xây Bob | Có thể xây công trình nâng cấp | 125 | Winona | — |
| `expertwinona2` | Flagbearer | Can build Flags banners structure | 50 | Winona | — |
| `expertwolf1` | Giga Chad | Dễ dàng trở nên khỏe mạnh | 5 | Wolfgang | — |
| `expertwolf2` | Phước lành Ares | Có thể chế tạo các vật phẩm đặc biệt | 65 | Wolfgang | — |
| `expertwonk1` | Vuốt khỉ | Wonkey có thể đào và di chuyển dưới            lòng đất | 30 | Wonkey | — |
| `expertwonk2` | Sức mạnh thực thụ | Wonkey mạnh hơn mỗi             Accursed Trinket trong kho đồ | 30 | Wonkey | — |
| `expertwoodie1` | Thuần Thú | Kiểm soát hoàn toàn con thú trong người | 65 | Woodie | — |
| `expertwoodie2` | Người Bearver | Có thể ăn các loại gỗ để nhận chỉ số | 40 | Woodie | — |
| `expertwoodie3` | Dạng kích thích | Những dạng biến hình mạnh hơn | 40 | Woodie | — |
| `expertworm1` | Phước lành Persephone | Có thể chế tạo những công cụ đặc biệt | 40 | Wormwood | — |
| `expertworm2` | Bàn tay cứt | Có thể bón cây bằng tay | 25 | Wormwood | — |
| `expertwortox1` | Tốc biến | Soul-hopping bản đồ luôn luôn                 tốn tối đa 5 | 5 | Wortox | — |
| `expertwortox3` | Phước lành Hades | Can craft special weapon | 55 | Wortox | — |
| `expertwurt1` | Phước lành Poseidon | Có thể chế tạo vũ khí đặc biệt | 55 | Wurt | — |
| `expertwurt2` | Nữ hoàng Merm | Hiệu ứng của King mạnh hơn và             có vệ sĩ | 25 | Wurt | — |
| `expertwx1` | WX-12 | Tăng lượng pin module lên 12 | 120 | WX-78 | — |
| `expertwx2` | WX-99 | Độ bền của các mạch vĩnh viễn | 55 | WX-78 | — |
| `expertwx4` | J4-M5 | Can craft upgraded J1-M1 that can scan new creature data | 45 | WX-78 | — |

### Mở khóa chế tạo — 16 perk

| ID | Tên | Hiệu ứng (chuỗi nguồn VI) | Giá gốc | Nhân vật/phạm vi | Ghi chú dữ liệu |
|---|---|---|---:|---|---|
| `ancientstation` | Ancient Builder | Có thể chế tạo vật phẩm The Ancient Pseudoscience | 30 | Mọi nhân vật | — |
| `bossitemcraft` | Thợ rèn huyền thoại | Có thể chế tạo vật phẩm Bosses | 25 | Mọi nhân vật | — |
| `carnivalcraft` | Festive! | Có thể chế tạo vật phẩm Carnival event | 10 | Mọi nhân vật | — |
| `carpentercraft` | Carpentry Expert | Able to craft Sawhorse items | 5 | Mọi nhân vật | — |
| `clustercraft` | Cluster Constructor | Able to craft cluster of items | 20 | Mọi nhân vật | — |
| `crittercraft` | Orphanage | Able to adopt pets | 5 | Mọi nhân vật | — |
| `dencraft` | Pokeball | Có thể chế tạo animal den và nest | 50 | Mọi nhân vật | — |
| `duppercritter` | Pet Not Included | Able to adopt Companion that can be leveled up and upgraded | 25 | Mọi nhân vật | — |
| `eventcraft` | Celebrate! | Có thể chế tạo vật phẩm new year event | 10 | Mọi nhân vật | — |
| `klaussackbuilder` | Quà giáng sinh | Có thể chế tạo Loot Stash và Deer Antler | 20 | Mọi nhân vật | — |
| `lunarcraft` | Kỵ sĩ ánh trăng | Có thể chế tạo vật phẩm tab Lunar | 10 | Mọi nhân vật | — |
| `madsciencecraft` | Nhà khoa học điên | Có thể chế tạo vật phẩm tab Experiments | 10 | Mọi nhân vật | — |
| `multicraft` | Duplicraft | Able to craft multiple ingredients | 5 | Mọi nhân vật | — |
| `pearlcraft` | Pearl BFF | Có thể chế tạo vật phẩm tab Pearls trading | 10 | Mọi nhân vật | — |
| `rabbitkingcraft` | Benevolent Mind | Able to craft Benevolent Rabbit King items | 5 | Mọi nhân vật | — |
| `trinketcraft` | Antique Shop | Able to craft trinkets (vanilla, DLC, and New one) | 15 | Mọi nhân vật | — |

### Dùng một lần — 10 perk

| ID | Tên | Hiệu ứng (chuỗi nguồn VI) | Giá gốc | Nhân vật/phạm vi | Ghi chú dữ liệu |
|---|---|---|---:|---|---|
| `addstat` | Khởi đầu thuận lợi | Đặt Hunger, Health, và Sanity lên tối đa | 1 | Mọi nhân vật | dùng một lần |
| `givestar` | Star Gift | Give 1 Stars to nearest player | 1 | Mọi nhân vật | dùng một lần |
| `killhound` | Hound Be Gone! | Kill all nearby hounds | 1 | Mọi nhân vật | dùng một lần |
| `levelup` | Mạo hiểm giả kinh nghiệm | Ngay lập tức nhận 500 XP | 1 | Mọi nhân vật | dùng một lần |
| `material` | Mạo hiểm giả dày dặn | Nhận những nguyên liệu cơ bản và thức ăn. | 1 | Mọi nhân vật | dùng một lần |
| `openrift` | The Other Dimension | Spawn a rift | 2 | Mọi nhân vật | dùng một lần |
| `pickallup` | Vacuum Cleaner | Collect all dropped inventory item in the world | 1 | Mọi nhân vật | dùng một lần |
| `reviveall` | Triệu hồi | Hồi sinh toàn bộ người chơi | 1 | Mọi nhân vật | dùng một lần |
| `robinegg` | Filial Imprinting | Get robin egg | 2 | Mọi nhân vật | dùng một lần |
| `sharestar` | Star Share | Give 1 Stars to other players | 1 | Mọi nhân vật | dùng một lần |

### Toàn shard — 15 perk

| ID | Tên | Hiệu ứng (chuỗi nguồn VI) | Giá gốc | Nhân vật/phạm vi | Ghi chú dữ liệu |
|---|---|---|---:|---|---|
| `bossdmg` | Mạnh hơn | Bosses Damage chia tỷ lệ theo ngày sống được | 10 | Toàn shard | — |
| `bosshp` | To hơn | Bosses HP chia tỷ lệ theo ngày sống được | 20 | Toàn shard | — |
| `bosshunting` | Reign of Giants | Suspicious dirt pile now can track new special boss | 50 | Toàn shard | — |
| `easybeef` | Beefalo Educator | Beefalos are easier to be tamed | 40 | Toàn shard | — |
| `easyfarm` | Phân bón tốt | Cây trồng dễ trở thành khổng lồ hơn | 60 | Toàn shard | — |
| `eternalcage` | Phước lành Fawkes | Chim trong lồng bất tử | 15 | Toàn shard | — |
| `eternalicebox` | Tủ lạnh ngưng đọng | Thực phẩm trong tủ lạnh lấy lại độ tươi | 90 | Toàn shard | — |
| `eternalthermal` | Đá thuần khiết | (Gần như) Sử dụng đá nhiệt không giới hạn | 5 | Toàn shard | — |
| `groundedscream` | Honorary Trophies | Potter's Wheel's Chess Pieces gives global buffs | 25 | Toàn shard | — |
| `icyweed` | Icy-Breezy | Spawn Icy Tumbleweed randomly from tree/stump on winter | 35 | Toàn shard | — |
| `insightinfinite` | Infinite Insight | All Players have 99 Insight Points | 70 | Toàn shard | — |
| `mermbuff` | Merm Trỗi dậy | Merms HP và Damage chia tỷ lệ theo ngày sống được | 30 | Toàn shard | — |
| `riftcontroller` | Rift Manager | World behave like a there are rifts open | 60 | Toàn shard | — |
| `spiderbuff` | Nhện phá hoại | Spiders HP và Damage chia tỷ lệ theo ngày sống được | 30 | Toàn shard | — |
| `stackinfinite` | Infinite Stack | Stackable item can Stack infinitely | 100 | Toàn shard | — |

## Hệ thống Level và điểm thuộc tính

- Mặc định bắt đầu cấp 1. Mỗi lần lên cấp nhận 1 điểm thuộc tính (`LEVELPOINTS = 1`); giới hạn cấp mặc định là vô hạn.
- XP mặc định nhận từ ăn, chế tạo, giết, làm việc, nấu, trồng/chăm cây, câu cá và thu hoạch; hệ số XP mặc định là 1x.
- Mỗi điểm có chi phí ban đầu 1; giá tăng dần và tối đa 3 theo trường `multi` của thuộc tính.

| Thuộc tính người chơi | Tăng mặc định mỗi điểm | Chu kỳ tăng giá (`multi`) |
|---|---:|---:|
| Hunger tối đa | +3 | 100 |
| Sanity tối đa | +3 | 100 |
| Health tối đa | +3 | 100 |
| Tốc độ | +0,1% | 25 |
| Phòng thủ | +0,25%, tối đa mặc định 50% | 30 |
| Sát thương | +0,05% | 25 |

| Thuộc tính pet | Tăng/ý nghĩa trong code | Chu kỳ tăng giá (`multi`) |
|---|---|---:|
| Tốc độ pet | +5% mỗi điểm | 100 |
| Sát thương pet | +1 mỗi điểm | 100 |
| Hồi đòn đánh pet | Thuộc tính `petattackspeedlevel` | 100 |
| Hồi kỹ năng pet | Thuộc tính `petcooldownlevel` | 10 |
| Sức mạnh phép pet | Thuộc tính `petspelllevel` | 20 |
| Nội tại pet | Thuộc tính `petpassivelevel` | 20 |

## File nguồn chính

- `main_strings_vi.lua`: tên/mô tả tiếng Việt và các chuỗi nhiệm vụ.
- `scripts/constants/seasonaltaskdata.lua`: toàn bộ pool nhiệm vụ và điều kiện code.
- `scripts/constants/achievementdata.lua` + `scripts/constants/achievements/*.lua`: mục tiêu và thưởng Sao.
- `scripts/constants/perkdata.lua` + `scripts/constants/perks/*.lua`: giá, phạm vi và điều kiện nhân vật của perk.
- `scripts/components/allachivevent.lua`: chọn nhiệm vụ, ghi nhận thành tựu và trao thưởng.
- `main_taskskillpostInits.lua`: kỹ năng mùa ở mốc 4.
- `scripts/components/levelsystem.lua` và `scripts/constants/leveldata.lua`: Level, XP và thuộc tính.
