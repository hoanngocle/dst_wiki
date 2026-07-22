# Category crawler control

Registry máy đọc/ghi nằm tại `<git-common-dir>/category-crawler/`; file
`data/crawled/fandom-url-registry.json` và MD này chỉ là snapshot/bảng review.
Trạng thái chỉ gồm `New`, `Doing`, `Done`: URL mới/`New` được lấy tiếp, còn
`Doing` và `Done` phải skip network fetch.

> **Live audit 2026-07-22:** 1.310 URL hợp lệ, 1.310 `Done`, 0 `New`, 0
> `Doing`, 0 artifact lỗi. Toàn bộ URL đã duyệt và aggregate DST đã hoàn tất.

## Category queue

| Category | Source | Direct | Child category | Excluded | Publish candidates | Registry Done | Status |
|---|---|---:|---:|---:|---:|---:|---|
| guides | [Category:Guides](https://dontstarve.fandom.com/wiki/Category:Guides) | 105 | 1 | 101 | 4 | 4 | Done |
| shadow_magic_filter | [Category:Shadow Magic Filter](https://dontstarve.fandom.com/wiki/Category:Shadow_Magic_Filter) | 31 | 0 | 0 | 31 | 31 | Done |
| spiders | [Category:Spiders](https://dontstarve.fandom.com/wiki/Category:Spiders) | 14 | 0 | 1 | 13 | 13 | Done |
| structures | [Category:Structures](https://dontstarve.fandom.com/wiki/Category:Structures) | 278 | 4 | 123 | 155 | 155 | Done |
| survival_tab | [Category:Survival Tab](https://dontstarve.fandom.com/wiki/Category:Survival_Tab) | 34 | 0 | 10 | 24 | 24 | Done |
| survivor_items_filter | [Category:Survivor Items Filter](https://dontstarve.fandom.com/wiki/Category:Survivor_Items_Filter) | 21 | 0 | 0 | 21 | 21 | Done |
| tools_filter | [Category:Tools Filter](https://dontstarve.fandom.com/wiki/Category:Tools_Filter) | 38 | 0 | 0 | 38 | 38 | Done |
| tools_tab | [Category:Tools Tab](https://dontstarve.fandom.com/wiki/Category:Tools_Tab) | 12 | 0 | 2 | 10 | 10 | Done |
| turf_items | [Category:Turf Items](https://dontstarve.fandom.com/wiki/Category:Turf_Items) | 50 | 0 | 18 | 32 | 32 | Done |
| trees | [Category:Trees](https://dontstarve.fandom.com/wiki/Category:Trees) | 27 | 0 | 10 | 17 | 17 | Done |
| treasure_hunting_tab | [Category:Treasure Hunting Tab](https://dontstarve.fandom.com/wiki/Category:Treasure_Hunting_Tab) | 4 | 0 | 4 | 0 | 0 | Skipped: Hamlet-only |
| vegetables | [Category:Vegetables](https://dontstarve.fandom.com/wiki/Category:Vegetables) | 33 | 1 | 7 | 26 | 26 | Done |
| wall | [Wall](https://dontstarve.fandom.com/wiki/Wall) | 0 | 0 | 1 | 0 | 0 | Skipped: overview article |
| weapons | [Category:Weapons](https://dontstarve.fandom.com/wiki/Category:Weapons) | 58 | 3 | 23 | 35 | 35 | Done |
| weather | [Category:Weather](https://dontstarve.fandom.com/wiki/Category:Weather) | 11 | 0 | 4 | 7 | 7 | Done |
| plants | [Category:Plants](https://dontstarve.fandom.com/wiki/Category:Plants) | 66 | 1 | 29 | 37 | 37 | Done |
| portal | [Category:Portal](https://dontstarve.fandom.com/wiki/Category:Portal) | 9 | 0 | 7 | 2 | 2 | Done |
| ranged_weapons | [Category:Ranged Weapons](https://dontstarve.fandom.com/wiki/Category:Ranged_Weapons) | 15 | 0 | 8 | 7 | 7 | Done |
| rare_blueprint_exclusive | [Category:Rare Blueprint Exclusive](https://dontstarve.fandom.com/wiki/Category:Rare_Blueprint_Exclusive) | 38 | 0 | 3 | 35 | 35 | Done |
| refine_tab | [Category:Refine Tab](https://dontstarve.fandom.com/wiki/Category:Refine_Tab) | 20 | 0 | 5 | 15 | 15 | Done |
| resources | [Category:Resources](https://dontstarve.fandom.com/wiki/Category:Resources) | 106 | 3 | 27 | 79 | 79 | Done |
| resurrection | [Category:Resurrection](https://dontstarve.fandom.com/wiki/Category:Resurrection) | 11 | 0 | 3 | 8 | 8 | Done |
| ruins_creatures | [Category:Ruins Creatures](https://dontstarve.fandom.com/wiki/Category:Ruins_Creatures) | 13 | 1 | 2 | 11 | 11 | Done |
| science | [Category:Science](https://dontstarve.fandom.com/wiki/Category:Science) | 99 | 0 | 14 | 85 | 85 | Done |
| science_tier_2 | [Category:Science Tier 2](https://dontstarve.fandom.com/wiki/Category:Science_Tier_2) | 147 | 0 | 51 | 96 | 96 | Done |
| science_tier_1 | [Category:Science Tier 1](https://dontstarve.fandom.com/wiki/Category:Science_Tier_1) | 117 | 0 | 54 | 63 | 63 | Done |
| seafaring_filter | [Category:Seafaring Filter](https://dontstarve.fandom.com/wiki/Category:Seafaring_Filter) | 14 | 0 | 1 | 13 | 13 | Done |
| light_sources | [Category:Light Sources](https://dontstarve.fandom.com/wiki/Category:Light_Sources) | 94 | 0 | 28 | 66 | 66 | Done |
| magic_tab | [Category:Magic Tab](https://dontstarve.fandom.com/wiki/Category:Magic_Tab) | 30 | 0 | 10 | 20 | 20 | Done |
| magic_tier_1 | [Category:Magic Tier 1](https://dontstarve.fandom.com/wiki/Category:Magic_Tier_1) | 19 | 0 | 5 | 14 | 14 | Done |
| magic_tier_2 | [Category:Magic Tier 2](https://dontstarve.fandom.com/wiki/Category:Magic_Tier_2) | 14 | 0 | 5 | 9 | 9 | Done |
| meats | [Category:Meats](https://dontstarve.fandom.com/wiki/Category:Meats) | 48 | 1 | 15 | 33 | 33 | Done |
| melee_weapons | [Category:Melee Weapons](https://dontstarve.fandom.com/wiki/Category:Melee_Weapons) | 38 | 0 | 15 | 23 | 23 | Done |
| mineable_objects | [Category:Mineable Objects](https://dontstarve.fandom.com/wiki/Category:Mineable_Objects) | 32 | 0 | 9 | 23 | 23 | Done |
| mob_dropped_items | [Category:Mob Dropped Items](https://dontstarve.fandom.com/wiki/Category:Mob_Dropped_Items) | 205 | 3 | 63 | 142 | 142 | Done |
| mob_housing | [Category:Mob Housing](https://dontstarve.fandom.com/wiki/Category:Mob_Housing) | 52 | 0 | 29 | 23 | 23 | Done |
| mob_spawning_entities | [Category:Mob Spawning Entities](https://dontstarve.fandom.com/wiki/Category:Mob_Spawning_Entities) | 124 | 2 | 47 | 77 | 77 | Done |
| mobs | [Category:Mobs](https://dontstarve.fandom.com/wiki/Category:Mobs) | 279 | 22 | 105 | 174 | 174 | Done |
| mods | [Category:Mods](https://dontstarve.fandom.com/wiki/Category:Mods) | 3 | 0 | 3 | 0 | 0 | Skipped: community mods/overview |
| monster_foods | [Category:Monster Foods](https://dontstarve.fandom.com/wiki/Category:Monster_Foods) | 9 | 0 | 3 | 6 | 6 | Done |
| monsters | [Category:Monsters](https://dontstarve.fandom.com/wiki/Category:Monsters) | 64 | 4 | 24 | 40 | 40 | Done |
| neutral_creatures | [Category:Neutral Creatures](https://dontstarve.fandom.com/wiki/Category:Neutral_Creatures) | 36 | 2 | 14 | 22 | 22 | Done |
| nightmare_state_indicator | [Category:Nightmare State Indicator](https://dontstarve.fandom.com/wiki/Category:Nightmare_State_Indicator) | 9 | 0 | 0 | 9 | 9 | Done |
| nocturnals | [Category:Nocturnals](https://dontstarve.fandom.com/wiki/Category:Nocturnals) | 23 | 0 | 6 | 17 | 17 | Done |
| ocean | [Category:Ocean](https://dontstarve.fandom.com/wiki/Category:Ocean) | 64 | 0 | 33 | 31 | 31 | Done |
| passive_creatures | [Category:Passive Creatures](https://dontstarve.fandom.com/wiki/Category:Passive_Creatures) | 63 | 1 | 33 | 30 | 30 | Done |
| innocents | [Category:Innocents](https://dontstarve.fandom.com/wiki/Category:Innocents) | 30 | 0 | 14 | 16 | 16 | Done |
| items | [Category:Items](https://dontstarve.fandom.com/wiki/Category:Items) | 987 | 32 | 306 | 681 | 681 | Done |
| gameplay | [Category:Gameplay](https://dontstarve.fandom.com/wiki/Category:Gameplay) | 112 | 24 | 32 | 80 | 80 | Done |
| gems | [Gems](https://dontstarve.fandom.com/wiki/Gems) | 0 | 0 | 1 | 0 | 0 | Skipped: article/disambiguation |
| hats | [Category:Hats](https://dontstarve.fandom.com/wiki/Category:Hats) | 63 | 0 | 23 | 40 | 40 | Done |
| healing | [Category:Healing](https://dontstarve.fandom.com/wiki/Category:Healing) | 192 | 2 | 53 | 139 | 139 | Done |
| health_loss | [Category:Health Loss](https://dontstarve.fandom.com/wiki/Category:Health_Loss) | 51 | 0 | 14 | 37 | 37 | Done |
| hostile_creatures | [Category:Hostile Creatures](https://dontstarve.fandom.com/wiki/Category:Hostile_Creatures) | 112 | 4 | 40 | 72 | 72 | Done |
| indestructible_object | [Category:Indestructible Object](https://dontstarve.fandom.com/wiki/Category:Indestructible_Object) | 87 | 0 | 48 | 39 | 39 | Done |
| infobox_missing_crafting_description | [Category:Infobox missing crafting description](https://dontstarve.fandom.com/wiki/Category:Infobox_missing_crafting_description) | 52 | 0 | 0 | 52 | 52 | Done |
| flying_creatures | [Category:Flying Creatures](https://dontstarve.fandom.com/wiki/Category:Flying_Creatures) | 16 | 1 | 4 | 12 | 12 | Done |
| followers | [Category:Followers](https://dontstarve.fandom.com/wiki/Category:Followers) | 42 | 1 | 7 | 35 | 35 | Done |
| food_gardening_filter | [Category:Food & Gardening Filter](https://dontstarve.fandom.com/wiki/Category:Food_%26_Gardening_Filter) | 19 | 0 | 0 | 19 | 19 | Done |
| food_tab | [Category:Food Tab](https://dontstarve.fandom.com/wiki/Category:Food_Tab) | 15 | 0 | 5 | 10 | 10 | Done |
| from_beyond | [Category:From Beyond](https://dontstarve.fandom.com/wiki/Category:From_Beyond) | 105 | 0 | 1 | 104 | 104 | Done |
| fruits | [Category:Fruits](https://dontstarve.fandom.com/wiki/Category:Fruits) | 12 | 1 | 3 | 9 | 9 | Done |
| fuel | [Category:Fuel](https://dontstarve.fandom.com/wiki/Category:Fuel) | 119 | 2 | 30 | 89 | 89 | Done |
| dont_starve_together | [Category:Don't Starve Together](https://dontstarve.fandom.com/wiki/Category:Don%27t_Starve_Together) | 878 | 12 | 6 | 872 | 872 | Done |
| a_new_reign | [Category:A New Reign](https://dontstarve.fandom.com/wiki/Category:A_New_Reign) | 110 | 2 | 18 | 92 | 92 | Done |
| ancient_tab | [Category:Ancient Tab](https://dontstarve.fandom.com/wiki/Category:Ancient_Tab) | 15 | 0 | 1 | 14 | 14 | Done |
| ancient_tier_1 | [Category:Ancient Tier 1](https://dontstarve.fandom.com/wiki/Category:Ancient_Tier_1) | 10 | 0 | 1 | 9 | 9 | Done |
| ancient_tier_2 | [Category:Ancient Tier 2](https://dontstarve.fandom.com/wiki/Category:Ancient_Tier_2) | 7 | 0 | 0 | 7 | 7 | Done |
| animals | [Category:Animals](https://dontstarve.fandom.com/wiki/Category:Animals) | 35 | 4 | 6 | 29 | 29 | Done |
| birds | [Category:Birds](https://dontstarve.fandom.com/wiki/Category:Birds) | 17 | 0 | 7 | 10 | 10 | Done |
| boss_monsters | [Category:Boss Monsters](https://dontstarve.fandom.com/wiki/Category:Boss_Monsters) | 37 | 0 | 9 | 28 | 28 | Done |
| clockwork_monsters | [Category:Clockwork Monsters](https://dontstarve.fandom.com/wiki/Category:Clockwork_Monsters) | 8 | 0 | 2 | 6 | 6 | Done |
| armour_filter | [Category:Armour Filter](https://dontstarve.fandom.com/wiki/Category:Armour_Filter) | 19 | 0 | 0 | 19 | 19 | Done |
| beefalo_foods | [Category:Beefalo Foods](https://dontstarve.fandom.com/wiki/Category:Beefalo_Foods) | 5 | 0 | 0 | 5 | 5 | Done |
| boss_dropped_items | [Category:Boss Dropped Items](https://dontstarve.fandom.com/wiki/Category:Boss_Dropped_Items) | 75 | 0 | 12 | 63 | 63 | Done |
| backpacks | [Category:Backpacks](https://dontstarve.fandom.com/wiki/Category:Backpacks) | 10 | 0 | 4 | 6 | 6 | Done |
| clothing_filter | [Category:Clothing Filter](https://dontstarve.fandom.com/wiki/Category:Clothing_Filter) | 10 | 0 | 0 | 10 | 10 | Done |
| cave_creatures | [Category:Cave Creatures](https://dontstarve.fandom.com/wiki/Category:Cave_Creatures) | 32 | 1 | 3 | 29 | 29 | Done |
| celestial_filter | [Category:Celestial Filter](https://dontstarve.fandom.com/wiki/Category:Celestial_Filter) | 6 | 0 | 0 | 6 | 6 | Done |
| celestial_tab | [Category:Celestial Tab](https://dontstarve.fandom.com/wiki/Category:Celestial_Tab) | 6 | 0 | 0 | 6 | 6 | Done |
| containers | [Category:Containers](https://dontstarve.fandom.com/wiki/Category:Containers) | 28 | 1 | 13 | 15 | 15 | Done |
| cooking_filter | [Category:Cooking Filter](https://dontstarve.fandom.com/wiki/Category:Cooking_Filter) | 15 | 0 | 1 | 14 | 14 | Done |
| crock_pot_recipes | [Category:Crock Pot Recipes](https://dontstarve.fandom.com/wiki/Category:Crock_Pot_Recipes) | 83 | 0 | 15 | 68 | 68 | Done |
| cooling | [Category:Cooling](https://dontstarve.fandom.com/wiki/Category:Cooling) | 26 | 1 | 4 | 22 | 22 | Done |
| craftable_items | [Category:Craftable Items](https://dontstarve.fandom.com/wiki/Category:Craftable_Items) | 496 | 5 | 137 | 359 | 359 | Done |
| craftable_structures | [Category:Craftable Structures](https://dontstarve.fandom.com/wiki/Category:Craftable_Structures) | 165 | 2 | 72 | 93 | 93 | Done |
| crafting_stations | [Category:Crafting Stations](https://dontstarve.fandom.com/wiki/Category:Crafting_Stations) | 15 | 1 | 3 | 12 | 12 | Done |
| decorations_filter | [Category:Decorations Filter](https://dontstarve.fandom.com/wiki/Category:Decorations_Filter) | 52 | 0 | 3 | 49 | 49 | Done |
| eggs | [Category:Eggs](https://dontstarve.fandom.com/wiki/Category:Eggs) | 8 | 0 | 1 | 7 | 7 | Done |
| equipable_items | [Category:Equipable Items](https://dontstarve.fandom.com/wiki/Category:Equipable_Items) | 198 | 5 | 67 | 131 | 131 | Done |
| events | [Category:Events](https://dontstarve.fandom.com/wiki/Category:Events) | 68 | 0 | 0 | 68 | 68 | Done |
| fertilizer | [Category:Fertilizer](https://dontstarve.fandom.com/wiki/Category:Fertilizer) | 13 | 0 | 1 | 12 | 12 | Done |
| food | [Category:Food](https://dontstarve.fandom.com/wiki/Category:Food) | 184 | 10 | 62 | 122 | 122 | Done |
| fight_tab | [Category:Fight Tab](https://dontstarve.fandom.com/wiki/Category:Fight_Tab) | 32 | 0 | 17 | 15 | 15 | Done |
| fishes | [Category:Fishes](https://dontstarve.fandom.com/wiki/Category:Fishes) | 20 | 0 | 14 | 6 | 6 | Done |

Batch 1 có 191 direct memberships, 174 title duy nhất. Sau review còn 147 URL
hợp lệ và toàn bộ đã `Done`. Snapshot sau batch 1 có 170 URL vì còn 23
Animals-only URL được giữ `New` sau khi import snapshot mất raw cache. Hai
Category con bị bỏ,
24 title độc quyền game khác bị loại trên toàn batch, cùng ba trang tổng quan
không đại diện prefab.

`https://dontstarve.fandom.com/wiki/Celestial_Filter` là article, không phải
Category. Nguồn crawler đã sửa thành
`https://dontstarve.fandom.com/wiki/Category:Celestial_Filter`.

Batch 2 có 1.375 direct memberships và 906 canonical title duy nhất. Sau review
DST-only còn 647 URL hợp lệ: 88 URL tái sử dụng và 559 URL mới. Cả 647 URL hiện
đều `Done`; registry toàn cục có 729 URL gồm 706 `Done` và 23 Animals-only
`New`. Có 383 membership trùng giữa các Category trong batch; canonical URL
registry bảo đảm mỗi detail chỉ fetch một lần.

Batch 3 có 292 direct memberships và 201 canonical page trước review. Sau lọc còn
195 accepted memberships tương ứng 166 canonical URL: 77 URL được tái sử dụng,
89 URL được crawl mới (gồm 23 Animals `New` và 66 URL chưa có), 29 lượt trùng
chéo giữa Category. Cả 195 membership hiện `Done`; registry toàn cục có 795 URL,
không còn `New`/`Doing`. `Animals` tái sử dụng config đã duyệt. Batch 7 xác minh
lại `Parrot Pirate` là Shipwrecked-only; URL `Done` từ batch cũ được gắn cờ dữ
liệu nhiễm để dọn sau và không được đưa vào output mới. Sáu alias màu Moonlens bị
loại trước resolve để chỉ register canonical `Moonlens` một lần.

Category tổng hợp `Don't Starve Together` đã đi hết hai trang API và kiểm đủ 899
member: 878 article namespace 0, 12 Category con và 9 User/User blog. Không crawl
đệ quy và không lấy namespace ngoài 0. Sáu alias màu Moonlens bị loại, nên còn
872 canonical URL để publish; 523 URL đã `Done` được reuse/skip network và chỉ
349 URL chưa có trong registry được crawl detail. Output hoàn tất với 872 page,
644 image, không có failure/pending; registry toàn cục tăng lên 1.144 URL và tất
cả đều `Done`.

Batch 4 có 512 direct memberships, trong đó 184 direct member của `Food` đã có
config; sau review còn 400 accepted memberships và 375 canonical URL.
Trong đó 366 URL đã `Done` được tái sử dụng và 9 URL DST mới đã crawl; 25 lượt
membership trùng chéo được canonical registry dedupe. `Food` giữ nguyên config
184/122 và output `Done`, không crawl lại. Bảy output mới đều hoàn tất, không có
failure/pending; registry toàn cục tăng lên 1.153 URL và tất cả đều `Done`.

Batch 5 có 669 direct namespace-0 memberships từ bảy Category hợp lệ. Sau review
DST-only còn 459 accepted memberships tương ứng 443 canonical URL: 373 URL đã
`Done` được tái sử dụng, 70 URL mới đã crawl và 16 lượt trùng chéo được registry
dedupe. Bốn URL mới Bridge, Charlie, Fire, Freezing cùng xuất hiện ở hai Category.
`Gems` bị bỏ vì là article/disambiguation; `Category:Gems` cũng chỉ redirect
ngược về article đó. Bảy output hoàn tất với 0 failure/pending; registry toàn cục
tăng lên 1.223 URL và tất cả đều `Done`.

Batch 6 có 1.017 direct namespace-0 memberships từ `Innocents` và `Items`. Sau review DST-only còn 697 accepted memberships tương ứng 692 canonical URL: 647 URL đã `Done` được reuse, 45 URL mới đã crawl và năm membership trùng chéo được registry dedupe. `Items` đi hết ba trang API; 32 Category con và một User page chỉ được ghi audit, không crawl đệ quy. Output `Innocents` hoàn tất 16 page/15 image; `Items` hoàn tất 681 page/598 image, đều 0 failure/pending. Registry toàn cục tăng lên 1.268 URL và tất cả đều `Done`.

Batch 7 có 1.206 direct namespace-0 memberships từ 19 nguồn. `Mods` bị bỏ toàn
bộ vì chỉ gồm overview/community mods; 18 Category hữu ích còn 759 accepted
memberships tương ứng 491 canonical URL. Registry reuse 462 URL `Done` và chỉ
fetch 29 URL mới; 199 URL xuất hiện ở ít nhất hai Category, tương ứng 268 lượt
membership trùng được canonical registry dedupe. Không crawl 35 Category con và
sáu member ngoài namespace 0. Cả 18 output hoàn tất với 759 page, 0
failure/pending; registry toàn cục tăng lên 1.297 URL và tất cả đều `Done`.

Batch 8 có 718 direct namespace-0 memberships từ 13 nguồn. `Passive
Creatures` khớp nguyên config/output 63/30 đã `Done` nên chỉ drift-check và
reuse; 12 config mới có 451 accepted memberships. Toàn batch còn 481 accepted
memberships tương ứng 362 canonical URL: 357 URL đã `Done` được reuse và chỉ
fetch năm URL mới. Có 109 URL xuất hiện ở ít nhất hai Category, tương ứng 119
lượt membership trùng được registry dedupe. Không crawl sáu Category con và
sáu member ngoài namespace 0. Mười hai output mới hoàn tất với 451 page, 404
image, 0 failure/pending; registry tăng lên 1.302 URL và tất cả đều `Done`.

Batch 9 audit 14 nguồn, gồm 611 direct namespace-0 memberships từ 13 Category
và một overview article. `Treasure Hunting Tab` bị bỏ vì cả bốn direct member
đều Hamlet-only; `Wall` bị bỏ vì là trang tổng hợp nhiều loại tường, không phải
một entity. Mười hai config còn lại có 409 accepted memberships tương ứng 358
canonical URL: 355 URL `Done` được reuse và chỉ fetch ba URL mới (`Merm Head`,
`Pig Head`, `Quagmire Firepit`). Có 50 canonical URL xuất hiện ở ít nhất hai
Category, tương ứng 51 lượt membership trùng được dedupe. Không crawl tám
Category con và tám member ngoài namespace 0. Mười hai output hoàn tất với 409
page, 334 image, 292.986 link, 0 failure/pending; registry tăng lên 1.305 URL và
tất cả đều `Done`.

Guide review kiểm 107 direct members: 105 article namespace 0, một Board Thread
và `Category:Dedicated Servers`. Không crawl đệ quy hoặc namespace ngoài 0. Chỉ
giữ bốn bài có phạm vi DST rõ ràng, nội dung đủ dùng và ảnh cover trong chính
bài (cạnh ngắn tối thiểu 80 px, cạnh dài tối thiểu 96 px ở bản render):
`How to Kill the Giants in DST`, `Maximum Efficiency Day 13 Base DST Guide`,
`Slurtle Slime Guide`, `Taming a Beefalo`. `Survive and Thrive` có 12 icon nhỏ
nhưng không có ảnh cover phù hợp nên bị loại sau crawl. Một trăm lẻ một bài
còn lại bị loại vì thuộc game/DLC khác, trộn phạm vi không thể xuất bản nguyên
bài cho wiki DST, đã lỗi thời, quá thiếu nội dung hoặc không có ảnh phù hợp.
Crawl hoàn tất với 4 page, 4 cover, 421 link và 0 failure/pending. URL registry
tăng lên 1.310 URL, toàn bộ ở trạng thái `Done`.

Giữ đủ 14 Category vì chúng bổ sung tag phân loại. `Craftable Items`, `Craftable
Structures`, `Events` và `Food` mang phần lớn URL riêng. `Cooking Filter`,
`Cooling`, `Fight Tab`, `Fishes` không có URL riêng so với các Category khác
trong batch, nhưng vẫn cần để gắn tag; chúng không làm phát sinh fetch lặp.

## Quyết định giữ/bỏ

- Giữ cả `Backpacks` và `Containers`: Backpacks cung cấp riêng `Seed Pack-It`;
  các URL còn lại được registry dedupe.
- Giữ cả `Celestial Filter` và `Celestial Tab`: Tab cũ vẫn có năm direct item
  không nằm trong Category Filter hiện tại; `Glass Cutter` được dedupe.
- `Boss Dropped Items`, `Backpacks`, `Containers` là Category trộn game; chỉ
  register trang có DST, bỏ Shipwrecked/Hamlet/Don't Starve-only trước detail.
- `Cave Creatures` bỏ `Mobs`, `Shadow Creature`, `Spiders` vì là trang
  overview/group; bỏ `Category:Spiders` vì không crawl đệ quy.

## Direct member review

### Category:Innocents

- Keep (16): Bee, Beefalo, Birds, Bunnyman, Butterfly, Catcoon, Dust Moth,
  Glommer, Moleworm, Moonrock Pengull, Mosling, Pengull, Pig, Rabbit, Tallbird,
  Volt Goat; toàn bộ đã `Done` trước batch.
- Exclude (14): sáu mob Shipwrecked-only và tám mob Hamlet-only. Mapping đầy đủ
  nằm trong `data/config/wiki-categories/innocents.json`.
- Không có Category con hay namespace ngoài 0.

### Category:Items

- Đi hết ba trang API: 987 direct namespace-0 page, 32 Category con và
  `User:Bluegeist/Sandbox5`.
- Keep (681): 636 URL đã `Done`; 45 URL DST mới gồm tám item base/shared, 27
  item The Forge và mười item The Gorge.
- Exclude (306): 139 Shipwrecked-only, 95 Hamlet-only, 12 Don't Starve-only,
  hai Reign of Giants-only, mười redirect alias, 30 overview/group page và 15
  category mismatch. Mapping đầy đủ nằm trong
  `data/config/wiki-categories/items.json`.
- 45 URL mới: Ashes, Barbed Helm, Beefalo Horn, Blacksmith's Edge, Blossomed
  Wreath, Broken Shell, Bunny Puff, Clairvoyant Crown, Cookpot, Crab Trap,
  Crystal Tiara, Darts, Feathered Reed Tunic, Feathered Wreath, Flour, Flower
  Headband, Hearthsfire Crystals, Infernal Staff, Iron Key Gorge, Jagged Grand
  Armor, Jagged Wood Armor, Large Casserole Dish, Large Cookpot, Living Staff,
  Molten Darts, Nox Helm, Petrifying Tome, Pig Skin, Pith Pike, Reed Tunic,
  Resplendent Nox Helm, Slaughter Tools, Slurper Pelt, Small Casserole Dish,
  Spiral Spear, Steadfast Grand Armor, Steadfast Stone Armor, Stone Splint Mail,
  Syrup Pot, Thulecite Fragments, Tome of Beckoning, Tree Tapping Kit, Walrus
  Tusk, Wood Armor, Woven Garland.
- Bỏ 32 Category con, không đệ quy: Armor, Boss Dropped Items,
  Character-Specific, Craftable Items, Crock Pot Recipes, Dairy, Eggs,
  Equipable Items, Fertilizer, Fishes, Food, Fruits, Fuel, Hats, Limited use,
  Meats, Melee Weapons, Minerals, Mob Dropped Items, Mob Spawning Entities,
  Monster Foods, Non-Renewable, Perishables, Portable Crock Pot Recipes,
  Ranged Weapons, Science, Sweeteners, Turf Items, Unstealable Object,
  Vegetables, Warmth, Weapons.

### Category:Gameplay

- Keep (80): 29 URL đã `Done` và 51 trang mechanic/content có nội dung DST.
- Exclude (32): các trang độc quyền Don't Starve/Reign of Giants/Shipwrecked/
  Hamlet cùng hai trang disambiguation/overview Beard và Fog; mapping đầy đủ nằm
  trong `data/config/wiki-categories/gameplay.json`.
- Bỏ 24 Category con, không đệ quy: Adventure Mode, Area of Effect,
  Character-Specific, Cooling, Earthshakers, Fire Starter, Healing, Health Loss,
  Interface, Light Sources, Mods, Nightmare State Indicator, Non-Flammable,
  Non-Renewable, Periodic Threat, Resurrection, Sanity Boost, Sanity Loss,
  Seasons, Speed Boost, Speed Loss, Warmth, Water Resistant, Weather.
- Bỏ namespace ngoài 0: `User:Queron/Caves`.

### Gems

- Skip: URL được đưa là article/disambiguation namespace 0, không phải Category.
- `Category:Gems` tồn tại nhưng redirect về `Gems`, không có direct member để
  crawl. Các trang gem riêng lẻ đã có trong registry nên không tạo config giả.

### Category:Hats

- Keep (40): toàn bộ đã `Done`.
- Exclude (23): Brain of Thought, Captain Hat, Cork Candle Hat, Cowl, Dumbrella,
  Fancy Helmet, Fryfocals, Gas Mask, Horned Helmet, Lucky Hat, Mant Mask,
  Particulate Purifier, Pirate Hat, Pith Hat, Royal Crown, Shamlet Mask, Shark
  Tooth Crown, Sleek Hat, Snakeskin Hat, Spectoggles, Swashy Hat, Thunderhat,
  Visor; tất cả là nội dung Shipwrecked/Hamlet/single-player-only.

### Category:Healing

- Keep (139): 134 URL đã `Done`; năm URL mới hợp lệ DST là Butter, Butterfly
  Wings, Mosquito Sack, Small Jerky, Spider Gland.
- Exclude (53): 52 item độc quyền Shipwrecked/Hamlet và Crop Seeds
  (`non_item:overview`); mapping đầy đủ nằm trong config.
- Bỏ Category con, không đệ quy: Category:Crock Pot Recipes,
  Category:Resurrection.

### Category:Health Loss

- Keep (37): 34 URL đã `Done`; ba URL mới hợp lệ DST là Charlie, Fire, Freezing.
- Exclude (14): 13 nội dung độc quyền game khác và Monster Food
  (`non_item:overview`).

### Category:Hostile Creatures

- Keep (72): 68 URL đã `Done`; bốn URL mới hợp lệ DST là Ghost, Hound,
  Suspicious Peeper, Werepig.
- Exclude (40): creature độc quyền Shipwrecked/Hamlet, các group/overview Mobs,
  MacTusk N' Son, Shadow Creature, Spiders; Blue Hound và Red Hound là redirect
  trùng canonical Hound.
- Bỏ Category con, không đệ quy: Category:Boss Monsters, Category:Clockwork
  Monsters, Category:Followers, Category:Spiders.

### Category:Indestructible Object

- Keep (39): 28 URL đã `Done`; 11 URL mới hợp lệ DST là Bones, Bridge, Cave
  Light, Eye Bone, Grave, Obelisk, Pig King, Pond, Sinkhole, Walrus Camp, Worm
  Hole.
- Exclude (48): object Adventure Mode/Pocket Edition/Shipwrecked/Hamlet-only;
  mapping đầy đủ nằm trong config.

### Category:Infobox missing crafting description

- Keep đủ 52 direct namespace-0 page; toàn bộ đã `Done` trước batch.
- Đây là Category bảo trì, chỉ giữ membership provenance; không dùng làm tag
  hiển thị chính cho người đọc.
- Bỏ bảy User/Talk/Board Thread member ngoài namespace 0.

### Category:Flying Creatures

- Keep (12); danh sách authoritative nằm trong `Shared item URLs` theo category.
- Exclude (4): Mobs (`non_item:overview`), Packim Baggims, Poison Mosquito,
  Stink Ray (`non_dst:shipwrecked`).
- Bỏ Category con, không đệ quy: Category:Birds.

### Category:Followers

- Keep (35), gồm hai URL mới hợp lệ DST: Abigail, Merm.
- Exclude (7): Bottlenose Ballphin, Packim Baggims, Prime Ape, Wildbore
  (`non_dst:shipwrecked`); Pog, Ro Bin (`non_dst:hamlet`); Spiders
  (`non_item:overview`).
- Bỏ Category con, không đệ quy: Category:Spiders.

### Category:Food & Gardening Filter

- Keep đủ 19 direct item; toàn bộ đã `Done` trước batch.

### Category:Food Tab

- Keep 10 direct item; toàn bộ đã `Done` trước batch.
- Exclude (5): Farm (`non_dst:dont_starve`), Fish Farm, Mussel Bed, Mussel
  Stick (`non_dst:shipwrecked`), Sprinkler (`non_dst:hamlet`).

### Category:From Beyond

- Keep (104), gồm URL mới Brightshade Husk đã xác nhận bằng wikitext DST.
- Exclude: Combat (`non_item:overview`).

### Category:Fruits

- Keep 9 direct food; toàn bộ đã `Done` trước batch.
- Exclude (3): Coconut, Coffee Beans (`non_dst:shipwrecked`), Fruit
  (`non_item:overview`).
- Bỏ Category con, không đệ quy: Category:Crock Pot Recipes.

### Category:Fuel

- Keep (89), gồm sáu URL mới có bằng chứng DST: Berry Bush, Grass Tuft, Pine
  Cone, Slurtle Slime, Spiky Bush, Tentacle Spots.
- Exclude (30): Turfs (`non_item:overview`); 19 Shipwrecked-only và 10
  Hamlet-only title được liệt kê đầy đủ trong review spec/config.
- Bỏ Category con, không đệ quy: Category:Fertilizer, Category:Turf Items.

### Category:Don't Starve Together

- Keep: 872 canonical article; danh sách đầy đủ nằm trong bảng `Shared item URLs`
  sau khi snapshot hoàn tất.
- Exclude trước detail (6): Blue Moonlens, Green Moonlens, Orange Moonlens,
  Purple Moonlens, Red Moonlens, Yellow Moonlens (đều
  `duplicate:canonical_redirect`; giữ canonical `Moonlens`).
- Bỏ 12 Category con, không đệ quy: Category:A New Reign, Category:Aquatic Mobs,
  Category:Cartography Tab, Category:Celestial Tab, Category:Curios,
  Category:Engineering Tab, Category:Events, Category:Portable Crock Pot Recipes,
  Category:Rare Blueprint Exclusive, Category:Return of Them,
  Category:Seafaring Tab, Category:Shadow Tab.
- Bỏ 9 trang ngoài namespace 0: User:Aviivix, User:Mahskie/Sandbox,
  User blog:Mewk, spot, and socks/PVP, User:Queron/Caves,
  User:Robyn Grayson/Willow, User:Robyn Grayson/Willow's Lighter,
  User blog:Sybastion/Farming in alphabetical order, User:Synthetic ivy/sandbox,
  User blog:WX-100/Don't Starve Together's farm.

### Category:Armour Filter

- Keep (19): Battle Helm, Battle Rönd, Beekeeper Hat, Bramble Husk, Brightshade Armor, Brightshade Helm, Commander's Helm, Cookie Cutter Cap, Dreadstone Armor, Dreadstone Helm, Football Helmet, Grass Suit, Hardwood Hat, Log Suit, Marble Suit, Night Armor, Scalemail, W.A.R.B.I.S. Armor, W.A.R.B.I.S. Head Gear.

### Category:Beefalo Foods

- Keep (5): Beefalo Treats, Cut Grass, Cut Reeds, Steamed Twigs, Twigs.

### Category:Boss Dropped Items

- Keep (63): Ancient Key, Bee Queen Crown, Blue Cap, Blue Gem, Blueprint, Bone Armor, Bone Helm, Charcoal, Dark Sword, Dark Tatters, Deerclops Eyeball, Desert Stone, Down Feather, Drumstick, Enlightened Crown, Eye Mask, Fossils, Friendly Fruit Fly Fruit, Frog Legs, Fur Tuft, Gold Nugget, Green Cap, Green Gem, Guardian's Horn, Honey, Honeycomb, Infused Moon Shard, Krampus Sack, Lavae Egg, Living Log, Malbatross Bill, Malbatross Feather, Meat, Milky Whites, Monster Meat, Moon Rock, Moon Shard, Mushrooms, Night Armor, Nightmare Fuel, Orange Gem, Ornate Chest, Pearl's Pearl, Pure Horror, Purple Gem, Raw Fish, Red Cap, Red Gem, Royal Jelly, Scales, Shadow Atrium, Shadow Thurible, Shield of Terror, Shroom Skin, Silk, Sketch, Spark Ark, Spider Eggs, Spiderhat, Stag Antler, Stinger, Thick Fur, Yellow Gem.
- Exclude trước detail (12): Booty Bag (`non_dst:shipwrecked`), Chest of the Depths (`non_dst:shipwrecked`), Coconut (`non_dst:shipwrecked`), Eye of the Tiger Shark (`non_dst:shipwrecked`), Magic Seal (`non_dst:shipwrecked`), Petrifying Bones (`non_dst:hamlet`), Pugalisk Skull (`non_dst:hamlet`), Quacken Beak (`non_dst:shipwrecked`), Seed of Ruin (`non_dst:dont_starve`), Shark Gills (`non_dst:shipwrecked`), Snake Bone (`non_dst:hamlet`), Turbine Blades (`non_dst:shipwrecked`).

### Category:Backpacks

- Keep (6): Backpack, Chef Pouch, Insulated Pack, Krampus Sack, Piggyback, Seed Pack-It.
- Exclude trước detail (4): Booty Bag (`non_dst:shipwrecked`), Sea Sack (`non_dst:shipwrecked`), Thatch Pack (`non_dst:shipwrecked`), Vortex Cloak (`non_dst:hamlet`).

### Category:Clothing Filter

- Keep (10): Beefalo Hat, Funcap, Inspectacles, Piggyback, Portasol, Rose-Colored Glasses, Turf-Raiser Helm, Umbrella, Whirly Fan, Wooden Walking Stick.

### Category:Cave Creatures

- Keep (29): Batilisk, Bulbous Lightbug, Bunnyman, Cave Spider, Clockwork Bishop, Dangling Depth Dweller, Depths Worm, Dust Moth, Fireflies, Great Depths Worm, Hutch, Icker, Ink Blight, Lurking Nightmare, Mimicreep, Moleworm, Mush Gnome, Naked Mole Bat, Reanimated Skeleton, Resting Horror, Rock Lobster, Slurtle, Spider, Spider Queen, Spider Warrior, Spitter, Tentacle, Toadstool, Treeguard.
- Reuse `Done` (6): Bulbous Lightbug, Bunnyman, Dust Moth, Moleworm, Rock Lobster, Slurtle.
- Exclude trước detail (3): Mobs (`non_item:overview`), Shadow Creature (`non_item:overview`), Spiders (`non_item:overview`).
- Bỏ Category con, không đệ quy: Category:Spiders.

### Category:Celestial Filter

- Keep (6): Bath Bomb, Brightsmithy, Glass Cutter, Lunar Funcap, Moon Glass Saw Blade, Portal Paraphernalia.

### Category:Celestial Tab

- Keep (6): Glass Cutter, Moon Crater Turf, Moon Glass Axe → Axe (canonical redirect), Moon Rock Idol, Mutated Fungal Turf, Sketch.

### Category:Containers

- Keep (15): Backpack, Bundling Wrap, Chef Pouch, Chest, Chester, Crock Pot, Hutch, Ice Box, Insulated Pack, Krampus Sack, Ornate Chest, Piggyback, Polar Bearger Bin, Portable Crock Pot, Scaled Chest.
- Exclude trước detail (13): Booty Bag (`non_dst:shipwrecked`), Cargo Boat (`non_dst:shipwrecked`), Cork Barrel (`non_dst:hamlet`), Octopus Chest (`non_dst:shipwrecked`), Packim Baggims (`non_dst:shipwrecked`), Ro Bin (`non_dst:hamlet`), Sea Chest (`non_dst:shipwrecked`), Sea Sack (`non_dst:shipwrecked`), Steamer Trunk (`non_dst:shipwrecked`), Thatch Pack (`non_dst:shipwrecked`), Trawl Net (`non_dst:shipwrecked`), Vortex Cloak (`non_dst:hamlet`), Wooden Thing (`non_dst:dont_starve`).
- Bỏ Category con, không đệ quy: Category:Backpacks.

### Category:Cooking Filter

- Keep (14): Campfire, Chef Pouch, Cookbook, Crock Pot, Drying Rack, Humble Lamb Idol, Ice Box,
  Insulated Pack, Portable Crock Pot, Portable Grinding Mill, Portable Seasoning Station, Salt Box,
  Scaled Furnace, Willow's Lighter.

- Exclude trước detail (1): Winter's Feast (`non_item:category_mismatch`).

### Category:Crock Pot Recipes

- Keep (68): Amberosia, Asparagus Soup, Bacon and Eggs, Banana Pop, Banana Shake, Barnacle Linguine,
  Barnacle Pita, Beefalo Treats, Beefy Greens, Breakfast Skillet, Bunny Stew, Butter Muffin,
  California Roll, Ceviche, Creamy Potato Purée, Dragonpie, Fancy Spiralled Tubers, Fig-Stuffed
  Trunk, Figatoni, Figgy Frogwich, Figkabab, Fish Tacos, Fishsticks, Fist Full of Jam, Flower Salad,
  Froggle Bunwich, Frozen Banana Daiquiri, Fruit Medley, Guacamole, Honey Ham, Honey Nuggets, Ice
  Cream, Jelly Salad, Jellybeans, Kabobs, Leafy Meatloaf, Mandrake Soup, Meatballs, Meaty Stew,
  Melonsicle, Milkmade Hat, Monster Lasagna, Mushy Cake, Pierogi, Plain Omelette, Powdercake,
  Pumpkin Cookies, Ratatouille, Salsa Fresca, Seafood Gumbo, Soothing Tea, Spicy Chili, Spicy
  Vegetable Stinger, Steamed Twigs, Stuffed Eggplant, Stuffed Fish Heads, Stuffed Pepper Poppers,
  Surf 'n' Turf, Taffy, Tall Scotch Eggs, Trail Mix, Turkey Dinner, Unagi, Veggie Burger, Waffles,
  Wet Goop, Wobster Bisque, Wobster Dinner.

- Exclude trước detail (15): Bisque (`non_dst:shipwrecked`), Caviar (`non_dst:shipwrecked`), Coffee
  (`non_dst:shipwrecked`), Feijoada (`non_dst:hamlet`), Gummy Cake (`non_dst:hamlet`), Hard Shell
  Tacos (`non_dst:hamlet`), Iced Tea (`non_dst:hamlet`), Jelly-O Pop (`non_dst:shipwrecked`), Meated
  Nettles (`non_dst:hamlet`), Nettle Rolls (`non_dst:hamlet`), Shark Fin Soup
  (`non_dst:shipwrecked`), Snake Bone Soup (`non_dst:hamlet`), Steamed Ham Sandwich
  (`non_dst:hamlet`), Tea (`non_dst:hamlet`), Tropical Bouillabaisse (`non_dst:shipwrecked`).

### Category:Cooling

- Keep (22): Banana Pop, Ceviche, Chilled Amulet, Endothermic Fire, Eyebrella, Fashion Melon, Floral
  Shirt, Frozen Banana Daiquiri, Fruit Medley, Ice, Ice Cream, Ice Crystaleyezer, Ice Cube, Luxury
  Fan, Melonsicle, Moon Caller's Staff, Siesta Lean-to, Summer Frest, Thermal Stone, Watermelon,
  Whirly Fan, Wobster Bisque.

- Exclude trước detail (4): Dumbrella (`non_dst:shipwrecked`), Jelly-O Pop (`non_dst:shipwrecked`),
  Palm Leaf Hut (`non_dst:shipwrecked`), Tropical Fan (`non_dst:shipwrecked`).

- Bỏ Category con, không đệ quy: Category:Winter.

### Category:Craftable Items

- Keep (359): Abigail's Flower, Ageless Watch, Alarming Clock, Anchor, Ancient Brickwork, Ancient
  Flooring, Ancient Stonework, Ancient Tilework, Arboretum Experiment, Art?, Astral Detector,
  Astroggles, Axe, Backpack, Backstep Watch, Backtrek Watch, Bacon and Eggs, Bat Bat, Bath Bomb,
  Battle Call Canister, Battle Helm, Battle Rönd, Battle Spear, Beard Hair, Beard Hair Rug, Bed
  Roll, Bee Mine, Beefalo Bell, Beefalo Gloom Bell, Beefalo Hat, Beefalo Wool, Beekeeper Hat,
  Beeswax, Belt of Hunger, Bio Scanalyzer, Bird Trap, Blood Shot, Blue Gem, Blueprint, Boards, Boat,
  Boat Patch, Bone Shards, Boomerang, Booster Shot, Bramble Husk, Bramble Trap, Brambleshade Armor,
  Breezy Vest, Brightshade Armor, Brightshade Bomb, Brightshade Helm, Brightshade Shoevel,
  Brightshade Smasher, Brightshade Staff, Brightshade Sword, Brightsmithy, Brilliant Mudslinger,
  Brush, Bucket-o-poop, Bug Net, Bumpers, Bundling Wrap, Burrowing Horn, Bush Hat, Cannon,
  Cannonball, Carpeted Flooring, Cat Cap, Cave Rock Turf, Checkerboard Flooring, Chef Pouch, Chili
  Flakes, Chilled Amulet, Circuit Extractor, Clean Sweeper, Clever Disguise, Clockmaker's Tools,
  Coaching Whistle, Coat of Carrots, Cobblestones, Codex Umbra, Collected Dust, Commander's Helm,
  Compass, Compost Wrap, Construction Amulet, Cookbook, Cookie Cutter Cap, Cratered Moonrock, Cut
  Stone, Dapper Vest, Dark Sword, Deciduous Turf, Deck Illuminator, Deconstruction Staff, Den
  Decorating Set, Dock Kit, Dock Piling Kit, Dreaded Mudslinger, Dreadstone, Dreadstone Armor,
  Dreadstone Helm, Dreadstone Wall, Elastispacer, Elding Spear, Electrical Doodad, Embalming Spritz,
  Empty Bottle, Empty Frame, Eyebrella, Fashion Melon, Feather Hat, Feather Pencil, Feathery Canvas,
  Fencing Sword, Fertilizzzer, Figatoni, Fire Pump, Fire Staff, Fish Food, Fishing Rod, Fist Full of
  Jam, Flare, Fleshy Bulb, Flint, Floating Lantern, Floral Shirt, Football Helmet, Forest Turf,
  Funcap, Fungal Turf, Garden Digamajig, Garden Hoe, Gardeneer Hat, Garland, Garlic Powder, Glass
  Cutter, Gloomerang, Glow Berry Mousse, Gold Flooring, Gold Nugget, Gramophone, Grass Raft, Grass
  Suit, Grass Turf, Green Gem, Growth Formula Starter, Guano Turf, Gunpowder, Ham Bat, Hammer, Handy
  Remote, Hardwood Hat, Hay Wall, Healing Glop, Healing Salve, Hibearnation Vest, Honey Crystals,
  Honey Poultice, Hostile Flare, Hound's Tooth, Houndius Shootius, Howlitzer, Ice Cream, Ice
  Crystaleyezer, Ice Cube, Ice Staff, Icker Preserve, Infused Moon Shard, Inspectacles, Insulated
  Pack, Iridescent Gem, Jerky, Juicy Berry Bush, Kabobs, Kelp Patch, Kitschy Idols, Lantern, Life
  Giving Amulet, Lightning Conductor, Lil' Itchy, Living Log, Log, Log Suit, Lucky Beast, Lunar
  Experiment, Lunar Funcap, Lush Carpet, Luxury Fan, Magician's Top Hat, Magiluminescence, Mandrake
  Soup, Manure, Map Scroll, Marble, Marble Bean, Marble Suit, Marsh Turf, Mast, Meaty Stew, Miner
  Hat, Mini Sign, Moggles, Monster Jerky, Moon Crater Turf, Moon Glass Saw Blade, Moon Quay Beach
  Turf, Moon Rock, Moon Rock Idol, Moon Rock Wall, Moonlens, Morning Star, Mosaic Flooring, Mud
  Turf, Mutated Fungal Turf, Napsack, Nautopilot, Night Armor, Nightmare Amulet, Nightmare Fuel,
  Nightmare Saddle, Nitre, Oar, Ocean Trawler Kit, One-man Band, Orange Gem, Pan Flute, Papyrus,
  Phasmo-Encapsulator, Phobic Experiment, Pick/Axe, Pickaxe, Piggyback, Pile o' Balloons, Pinetree
  Pioneer Hat, Pitchfork, Pleasant Portrait, Pocket Scale, Polar Bearger Bin, Polly Roger's Hat,
  Portable Crock Pot, Portable Grinding Mill, Portable Seasoning Station, Portal Paraphernalia,
  Portasol, Pretty Parasol, Psychosis Experiment, Puffy Vest, Pumpkin Lantern, Pure Brilliance, Pure
  Horror, Purple Gem, Rabbit Earmuffs, Rain Coat, Rain Hat, Razor, Record, Red Firecrackers, Red
  Gem, Red Lantern, Rocks, Rocky Beach Turf, Rocky Turf, Rope, Rose-Colored Glasses, Rot, Rudder
  Kit, Saddle, Saddlehorn, Sandy Turf, Sanguine Experiment, Savanna Turf, Sawhorse, Scaled Flooring,
  Scalemail, Sea Fishing Rod, Seasoning Salt, Seawreath, Second Chance Watch, Seed Pack-It, Sewing
  Kit, Shadow Maul, Shadow Reaper, Shadowcraft Plinth, Shell Beach Turf, Shoo Box, Shovel, Skeeter
  Bomb, Slimy Salve, Slimy Turf, Spear, Spelunker's Bridge Kit, Spider Eggs, Star Caller's Staff,
  Steering Wheel, Stone Wall, Straw Hat, Strident Trident, Sulfuric Experiment, Summer Frest,
  Switcherdoodle, Syrup of Ipecaca, Table Lamp, Table Vase, Tackle Box, Tail o' Three Cats,
  Telelocator Staff, Teletransport Station, Telltale Heart, Tent Roll, The Lazy Explorer, The Lazy
  Forager, Thermal Stone, Thick Fur, Thulecite, Thulecite Bug Net, Thulecite Club, Thulecite Crown,
  Thulecite Medallion, Thulecite Suit, Tillweed Salve, Tooth Trap, Top Hat, Torch, Trap, Tree Jam,
  Treeguard Idol, Trusty Slingshot, Trusty Tape, Turf-Raiser Helm, Twigs, Umbralla, Umbrella, Unagi,
  Void Cowl, Void Robe, W.A.R.B.I.S. Armor, W.A.R.B.I.S. Head Gear, Walking Cane, Warren Wreath,
  Water Balloon, Watering Can, Wax Paper, Weather Pain, Webby Whistle, Whirly Fan, Willow's Lighter,
  Winona's Catapult, Winona's G.E.M.erator, Winona's Generator, Winter Hat, Wobster Dinner, Wood
  Fence, Wood Gate, Wood Wall, Wooden Flooring, Wooden Walking Stick, Yellow Gem.

- Exclude trước detail (137): Anti Venom (`non_dst:shipwrecked`), Armor (`non_item:overview`),
  Armor/DS (`non_item:overview`), Ball Pein Hammer (`non_dst:hamlet`), Battle Songs
  (`non_item:overview`), Bird Whistle (`non_dst:hamlet`), Blubber Suit (`non_dst:shipwrecked`),
  Blunderbuss (`non_dst:hamlet`), Boat Cannon (`non_dst:shipwrecked`), Boat Lantern
  (`non_dst:shipwrecked`), Boat Repair Kit (`non_dst:shipwrecked`), Boat Torch
  (`non_dst:shipwrecked`), Boats (`non_dst:shipwrecked`), Books (`non_item:overview`), Bottle
  Lantern (`non_dst:shipwrecked`), Brain of Thought (`non_dst:shipwrecked`), Bug B'Gone
  (`non_dst:hamlet`), Cactus Armor (`non_dst:shipwrecked`), Captain Hat (`non_dst:shipwrecked`),
  Circuits (`non_item:overview`), Claw Palm Sapling (`non_dst:hamlet`), Cloth
  (`non_dst:shipwrecked`), Coconade (`non_dst:shipwrecked`), Coral Nubbin (`non_dst:shipwrecked`),
  Cork Bat (`non_dst:hamlet`), Cork Bowl Canoe (`non_dst:hamlet`), Cork Candle Hat
  (`non_dst:hamlet`), Cowl (`non_dst:hamlet`), Crabby Hermit (`non_item:category_mismatch`),
  Cultivated Turf (`non_dst:hamlet`), Cutlass Supreme (`non_dst:shipwrecked`), Dart
  (`non_item:overview`), Demolition Permit (`non_dst:hamlet`), Dense Turf (`non_dst:hamlet`),
  Disarming Tools (`non_dst:hamlet`), Divining Rod (`non_dst:dont_starve`), Dripple Pipes
  (`non_dst:shipwrecked`), Dumbbells (`non_item:overview`), Dumbrella (`non_dst:shipwrecked`), Fancy
  Helmet (`non_dst:hamlet`), Flat Stone Turf (`non_dst:hamlet`), Floats (`non_item:overview`),
  Fryfocals (`non_dst:dont_starve`), Gas Mask (`non_dst:hamlet`), Ghostly Elixir
  (`non_item:overview`), Goggles (`non_item:overview`), Gold Pan (`non_dst:hamlet`), Halberd
  (`non_dst:hamlet`), Hallowed Nights (`non_item:category_mismatch`), Hedge (`non_dst:hamlet`),
  Horned Helmet (`non_dst:shipwrecked`), House Expansion Permit (`non_dst:hamlet`), Howling Conch
  (`non_dst:shipwrecked`), Ice (`non_dst:shipwrecked`), Infroggles (`non_dst:dont_starve`), Jelly-O
  Pop (`non_dst:shipwrecked`), Lawn Turf (`non_dst:hamlet`), Life Jacket (`non_dst:shipwrecked`),
  Limestone (`non_dst:shipwrecked`), Limestone Suit (`non_dst:shipwrecked`), Limestone Wall
  (`non_dst:shipwrecked`), Living Artifact (`non_dst:hamlet`), Lucky Hat (`non_dst:shipwrecked`),
  Lures (`non_item:overview`), Machete (`non_dst:shipwrecked`), Magnifying Glass (`non_dst:hamlet`),
  Mant Mask (`non_dst:hamlet`), Mant Suit (`non_dst:hamlet`), Meated Nettles (`non_dst:hamlet`),
  Midsummer Cawnival (`non_item:category_mismatch`), Midsummer Cawnival/Games
  (`non_item:category_mismatch`), Midsummer Cawnival/Prize Booth (`non_item:category_mismatch`),
  Mussel Bed (`non_dst:shipwrecked`), Mussel Stick (`non_dst:shipwrecked`), Nightmarish Bird Whistle
  (`non_dst:hamlet`), Obsidian Armor (`non_dst:shipwrecked`), Obsidian Spear
  (`non_dst:shipwrecked`), Old Bell (`non_dst:reign_of_giants`), Palm Leaf Hut
  (`non_dst:shipwrecked`), Particulate Purifier (`non_dst:shipwrecked`), Pirate Hat
  (`non_dst:shipwrecked`), Pith Hat (`non_dst:hamlet`), Poison Balm (`non_dst:hamlet`), Poison Spear
  (`non_dst:shipwrecked`), Pugalisk Wand (`non_dst:hamlet`), Quacken Drill (`non_dst:shipwrecked`),
  Quackering Ram (`non_dst:shipwrecked`), Repair Kits (`non_item:overview`), Sail
  (`non_dst:shipwrecked`), Sail Stick (`non_dst:shipwrecked`), Sandbag (`non_dst:shipwrecked`), Sea
  Sack (`non_dst:shipwrecked`), Sea Trap (`non_dst:shipwrecked`), Sea Wall (`non_dst:shipwrecked`),
  Seashell Suit (`non_dst:shipwrecked`), Security Contract (`non_dst:hamlet`), Shamlet Mask
  (`non_dst:hamlet`), Shark Fin Soup (`non_dst:shipwrecked`), Shark Tooth Crown
  (`non_dst:shipwrecked`), Shears (`non_dst:hamlet`), Silly Monkey Ball (`non_dst:shipwrecked`),
  Sleek Hat (`non_dst:shipwrecked`), Slingshot Ammo (`non_item:overview`), Snakeskin Hat
  (`non_dst:shipwrecked`), Snakeskin Jacket (`non_dst:shipwrecked`), Snakeskin Rug
  (`non_dst:shipwrecked`), Spear Gun (`non_dst:shipwrecked`), Spectoggles (`non_dst:dont_starve`),
  Spyglass (`non_dst:shipwrecked`), Stone Road Turf (`non_dst:hamlet`), Surfboard
  (`non_dst:shipwrecked`), Tar Lamp (`non_dst:shipwrecked`), Tar Suit (`non_dst:shipwrecked`),
  Telebrella (`non_dst:dont_starve`), Thatch Pack (`non_dst:shipwrecked`), Thunderhat
  (`non_dst:hamlet`), Time Pieces (`non_item:overview`), Tin Suit (`non_dst:hamlet`), Trawl Net
  (`non_dst:shipwrecked`), Tropical Fan (`non_dst:shipwrecked`), Tropical Parasol
  (`non_dst:shipwrecked`), Venom Gland (`non_dst:shipwrecked`), Visor (`non_dst:dont_starve`),
  Volcano Staff (`non_dst:shipwrecked`), Vortex Cloak (`non_dst:hamlet`), Wall
  (`non_item:overview`), Weevole Mantle (`non_dst:hamlet`), Windbreaker (`non_dst:shipwrecked`),
  Winter's Feast (`non_item:category_mismatch`), Year of the Beefalo (`non_item:category_mismatch`),
  Year of the Bunnyman (`non_item:category_mismatch`), Year of the Carrat
  (`non_item:category_mismatch`), Year of the Catcoon (`non_item:category_mismatch`), Year of the
  Dragonfly (`non_item:category_mismatch`), Year of the Gobbler (`non_item:category_mismatch`), Year
  of the Pig King (`non_item:category_mismatch`), Year of the Varg (`non_item:category_mismatch`).

- Bỏ Category con, không đệ quy: Category:Armor, Category:Crafting Stations, Category:Equipable
  Items, Category:Ranged Weapons, Category:Weapons.

### Category:Craftable Structures

- Keep (93): Accomploshrine, Alchemy Engine, Anchor, Armermry, Bee Box, Beefalo Grooming Station,
  Birdcage, Boat, Bookcase, Brightsmithy, Bumpers, Campfire, Cannon, Cartographer's Desk, Celestial
  Portal, Chest, Coat of Carrots, Communal Kelp Dish, Composting Bin, Craftsmerm House, Crock Pot,
  Directional Sign, Drying Rack, Endothermic Fire, Fire Pump, Fish Scale-O-Matic, Friendly
  Scarecrow, Gourmet Salt Lick, Grass Raft, Hay Wall, Hermit Home, Houndius Shootius, Humble Lamb
  Idol, Ice Box, Ice Crystaleyezer, Ice Flingomatic, Icker Preserve, Lightning Rod, Lunar
  Siphonator, Magician's Chest, Mannequin, Meat Effigy, Merm Flort-ifications, Mighty Gym, Mini
  Sign, Moon Dial, Moon Quay Pirate Banner, Mushroom Planter, Nautopilot, Night Light, Ocuvigil, Pig
  House, Pinchin' Winch, Potted Fern, Potted Succulent, Potter's Wheel, Prestihatitator, Produce
  Scale, Punching Bag, Rabbit Hutch, Rainometer, Reinforced Support Pillar, Relic, Royal Tapestry,
  Salt Box, Salt Lick, Sawhorse, Scaled Chest, Scaled Furnace, Science Machine, Shadow Manipulator,
  Shoddy Tool Shed, Siesta Lean-to, Sign, Sisturn, Stagehand, Tackle Receptacle, Telelocator Focus,
  Teletransport Station, Tent, Tent Roll, Terra Firma Tamper, The Lazy Deserter, Thermal Measurer,
  Think Tank, Tin Fishin' Bin, Wardrobe, Winona's Catapult, Winona's G.E.M.erator, Winona's
  Generator, Winona's Spotlight, Wood Fence, Wood Wall.

- Exclude trước detail (72): 'The Sty' Oddities Emporium (`non_dst:hamlet`), Armored Boat
  (`non_dst:shipwrecked`), Ballphin Palace (`non_dst:shipwrecked`), Buoy (`non_dst:shipwrecked`),
  Buoyant Chiminea (`non_dst:shipwrecked`), Cargo Boat (`non_dst:shipwrecked`), Chairs
  (`non_item:overview`), Chess Pieces (`non_item:overview`), Chiminea (`non_dst:shipwrecked`), Cork
  Barrel (`non_dst:hamlet`), Curly Tails Mud Spa (`non_dst:hamlet`), Doydoy Nest
  (`non_dst:shipwrecked`), Dragoon Den (`non_dst:shipwrecked`), Encrusted Boat
  (`non_dst:shipwrecked`), Farm (`non_dst:dont_starve`), Fish Farm (`non_dst:shipwrecked`), Hallowed
  Nights (`non_item:category_mismatch`), Hogus Porkusator (`non_dst:hamlet`), Ice Maker 3000
  (`non_dst:shipwrecked`), Lamp Post (`non_dst:hamlet`), Lawn Decoration (`non_dst:hamlet`), Log
  Raft (`non_dst:shipwrecked`), Midsummer Cawnival/Games (`non_item:category_mismatch`), Midsummer
  Cawnival/Prize Booth (`non_item:category_mismatch`), Miss Sow's Floral Arrangements
  (`non_dst:hamlet`), Mushroom Lights (`non_item:overview`), Obsidian Fire Pit
  (`non_dst:shipwrecked`), Oscillating Fan (`non_dst:hamlet`), Palm Leaf Hut
  (`non_dst:shipwrecked`), Pigg and Pigglet's General Store (`non_dst:hamlet`), Piratihatitator
  (`non_dst:shipwrecked`), Prime Ape Hut (`non_dst:shipwrecked`), Raft (`non_dst:shipwrecked`), Root
  Trunk (`non_dst:hamlet`), Row Boat (`non_dst:shipwrecked`), Sand Castle (`non_dst:shipwrecked`),
  Sandbag (`non_dst:shipwrecked`), Sea Chest (`non_dst:shipwrecked`), Sea Lab
  (`non_dst:shipwrecked`), Sea Yard (`non_dst:shipwrecked`), Seaworthy (`non_dst:shipwrecked`),
  Shadow Traps (`non_item:overview`), Skyworthy (`non_dst:hamlet`), Slanty Shanty
  (`non_dst:hamlet`), Smelter (`non_dst:hamlet`), Sprinkler (`non_dst:hamlet`), Swinesbury City Hall
  (`non_dst:hamlet`), Swinesbury Fine Grocer's (`non_dst:hamlet`), Swinesbury Mineral Exchange
  (`non_dst:hamlet`), Tables (`non_item:overview`), Tar Extractor (`non_dst:shipwrecked`), Telipad
  (`non_dst:dont_starve`), The 'Sea Legs' (`non_dst:shipwrecked`), The Boar's Tusk Weapon Shop
  (`non_dst:hamlet`), The Flying Pig Arcane Shop (`non_dst:hamlet`), The Sow's Ear Hat Shop
  (`non_dst:hamlet`), The Sterling Trough Deli (`non_dst:hamlet`), The Tinkerer's Tower
  (`non_dst:hamlet`), Thumper (`non_dst:dont_starve`), Town House (`non_dst:hamlet`), Wall
  (`non_item:overview`), Watch Tower (`non_dst:hamlet`), Wildbore House (`non_dst:shipwrecked`),
  Winter's Feast (`non_item:category_mismatch`), Year of the Beefalo (`non_item:category_mismatch`),
  Year of the Bunnyman (`non_item:category_mismatch`), Year of the Carrat
  (`non_item:category_mismatch`), Year of the Catcoon (`non_item:category_mismatch`), Year of the
  Dragonfly (`non_item:category_mismatch`), Year of the Gobbler (`non_item:category_mismatch`), Year
  of the Pig King (`non_item:category_mismatch`), Year of the Varg (`non_item:category_mismatch`).

- Bỏ Category con, không đệ quy: Category:Crafting Stations, Category:Structures.

### Category:Crafting Stations

- Keep (12): Ancient Pseudoscience Station, Benevolent Rabbit King, Brightsmithy, Cartographer's
  Desk, Celestial Orb, Codex Umbra, Crabby Hermit, Lunar Altars, Portable Grinding Mill, Potter's
  Wheel, Rock Den, Science Machine.

- Exclude trước detail (3): Hallowed Nights (`non_item:category_mismatch`), Key to the City
  (`non_dst:hamlet`), Obsidian Workbench (`non_dst:shipwrecked`).

- Bỏ Category con, không đệ quy: Category:Structures.

### Category:Decorations Filter

- Keep (49): Art?, Beefalo Grooming Station, Carpeted Flooring, Cave Rock Turf, Checkerboard
  Flooring, Clean Sweeper, Cobblestones, Deciduous Turf, Directional Sign, Dock Kit, Dock Piling
  Kit, Empty Frame, Feather Pencil, Fish Scale-O-Matic, Forest Turf, Gold Flooring, Gramophone,
  Grass Turf, Guano Turf, Hay Wall, Mini Sign, Moon Quay Beach Turf, Moon Quay Pirate Banner, Mud
  Turf, Pleasant Portrait, Potted Fern, Potted Succulent, Potter's Wheel, Produce Scale, Record,
  Relic, Rocky Beach Turf, Rocky Turf, Sandy Turf, Savanna Turf, Scaled Flooring, Scrap Wall, Shell
  Beach Turf, Sign, Slimy Turf, Stagehand, Table Lamp, Table Vase, Terra Firma Tamper, Wardrobe,
  Wood Fence, Wood Gate, Wood Wall, Wooden Flooring.

- Exclude trước detail (3): Chairs (`non_item:overview`), Tables (`non_item:overview`), Wall
  (`non_item:overview`).

### Category:Eggs

- Keep (7): Bacon and Eggs, Egg, Moose/Goose Egg, Plain Omelette, Rotten Egg, Spider Eggs, Tallbird
  Egg.

- Exclude trước detail (1): Doydoy Egg (`non_dst:shipwrecked`).

### Category:Equipable Items

- Keep (131): Alarming Clock, Astroggles, Axe, Backpack, Bat Bat, Battle Helm, Battle Paddle, Battle
  Spear, Bee Queen Crown, Beefalo Hat, Beekeeper Hat, Belt of Hunger, Bernie, Bone Armor, Bone Helm,
  Boomerang, Bramble Husk, Breezy Vest, Brush, Bug Net, Bull Kelp, Burrowing Horn, Bush Hat,
  Captain's Tricorn, Cat Cap, Chef Pouch, Chilled Amulet, Clean Sweeper, Clever Disguise, Coat of
  Carrots, Compass, Construction Amulet, Cookie Cutter Cap, Cutless, Dapper Vest, Dark Sword,
  Deconstruction Staff, Enlightened Crown, Eye Mask, Eyebrella, Fashion Melon, Feather Hat, Fiery
  Pen, Fire Staff, Fishing Rod, Floral Shirt, Football Helmet, Funcap, Garden Hoe, Gardeneer Hat,
  Garland, Glass Cutter, Gloomerang, Grass Suit, Ham Bat, Hammer, Hibearnation Vest, Howlitzer, Ice
  Cube, Ice Staff, Insulated Pack, Lantern, Life Giving Amulet, Log Suit, Lucky Beast, Lucy the Axe,
  Lunar Funcap, Magiluminescence, Malbatross Bill, Marble Suit, Milkmade Hat, Miner Hat, Moggles,
  Moon Caller's Staff, Morning Star, Napsack, Night Armor, Nightmare Amulet, Oar, One-man Band,
  Pick/Axe, Pickaxe, Piggyback, Pinetree Pioneer Hat, Pitchfork, Pocket Scale, Pretty Parasol, Puffy
  Vest, Rabbit Earmuffs, Rain Coat, Rain Hat, Red Lantern, Saddlehorn, Scalemail, Scrappy
  Chapauldron, Sea Fishing Rod, Seawreath, Seed Pack-It, Seedshell, Shelmet, Shield of Terror,
  Shovel, Slurper, Snurtle Shell Armor, Spear, Spiderhat, Star Caller's Staff, Straw Hat, Strident
  Trident, Summer Frest, Tail o' Three Cats, Tam o' Shanter, Telelocator Staff, Tentacle Spike, The
  Lazy Explorer, The Lazy Forager, Thulecite Club, Thulecite Crown, Thulecite Suit, Top Hat, Torch,
  Trusty Slingshot, Umbrella, Walking Cane, Warren Wreath, Water Balloon, Watering Can, Weather
  Pain, Whirly Fan, Willow's Lighter, Winter Hat.

- Exclude trước detail (67): Amulet (`non_item:overview`), Armor (`non_item:overview`), Armor/DS
  (`non_item:overview`), Ball Pein Hammer (`non_dst:hamlet`), Blubber Suit (`non_dst:shipwrecked`),
  Booty Bag (`non_dst:shipwrecked`), Bottle Lantern (`non_dst:shipwrecked`), Brain of Thought
  (`non_dst:shipwrecked`), Cactus Armor (`non_dst:shipwrecked`), Cactus Spike
  (`non_dst:shipwrecked`), Clothes (`non_item:overview`), Cork Bat (`non_dst:hamlet`), Cork Candle
  Hat (`non_dst:hamlet`), Cutlass Supreme (`non_dst:shipwrecked`), Dart (`non_item:overview`),
  Divining Rod (`non_dst:dont_starve`), Dumbrella (`non_dst:shipwrecked`), Executive Hammer
  (`non_dst:hamlet`), Eyeshot (`non_dst:shipwrecked`), Fancy Helmet (`non_dst:hamlet`), Goggles
  (`non_item:overview`), Gold Pan (`non_dst:hamlet`), Halberd (`non_dst:hamlet`), Horned Helmet
  (`non_dst:shipwrecked`), Life Jacket (`non_dst:shipwrecked`), Limestone Suit
  (`non_dst:shipwrecked`), Lucky Hat (`non_dst:shipwrecked`), Machete (`non_dst:shipwrecked`),
  Magnifying Glass (`non_dst:hamlet`), Mant Mask (`non_dst:hamlet`), Mant Suit (`non_dst:hamlet`),
  Obsidian Armor (`non_dst:shipwrecked`), Obsidian Spear (`non_dst:shipwrecked`), Particulate
  Purifier (`non_dst:shipwrecked`), Peg Leg (`non_dst:shipwrecked`), Pew-matic Horn
  (`non_dst:hamlet`), Pirate Hat (`non_dst:shipwrecked`), Pith Hat (`non_dst:hamlet`), Poison Spear
  (`non_dst:shipwrecked`), Pugalisk Wand (`non_dst:hamlet`), Rawling (`non_dst:shipwrecked`), Sea
  Sack (`non_dst:shipwrecked`), Seashell Suit (`non_dst:shipwrecked`), Shamlet Mask
  (`non_dst:hamlet`), Shark Tooth Crown (`non_dst:shipwrecked`), Shears (`non_dst:hamlet`), Sleek
  Hat (`non_dst:shipwrecked`), Snakeskin Hat (`non_dst:shipwrecked`), Snakeskin Jacket
  (`non_dst:shipwrecked`), Spear Gun (`non_dst:shipwrecked`), Spectoggles (`non_dst:dont_starve`),
  Stalking Stick (`non_dst:hamlet`), Swashy Hat (`non_dst:hamlet`), Tar Lamp
  (`non_dst:shipwrecked`), Tar Suit (`non_dst:shipwrecked`), Telebrella (`non_dst:dont_starve`),
  Thatch Pack (`non_dst:shipwrecked`), Thunderhat (`non_dst:hamlet`), Tin Suit (`non_dst:hamlet`),
  Trident (`non_dst:shipwrecked`), Tropical Parasol (`non_dst:shipwrecked`), Visor
  (`non_dst:dont_starve`), Volcano Staff (`non_dst:shipwrecked`), Vortex Cloak (`non_dst:hamlet`),
  Weapon (`non_item:overview`), Weevole Mantle (`non_dst:hamlet`), Windbreaker
  (`non_dst:shipwrecked`).

- Bỏ Category con, không đệ quy: Category:Armor, Category:Hats, Category:Melee Weapons,
  Category:Ranged Weapons, Category:Weapons.

### Category:Events

- Keep (68): Ancient Anchor, Arboretum Experiment, Battlemaster Pugna, Billy, Boarilla, Crab Meat,
  Crocommander, Onion, Riled Lucy, Forge Portal, Garlic, Goat Milk, Grand Forge Boarrior, Hallowed
  Nights, Infernal Swineclops, Key, Klaus, Loot Stash, Lunar Experiment, Magma Golem, Mealing Stone,
  Midsummer Cawnival, Midsummer Cawnival/Prize Booth, Mumsy, Old Beefalo, Packet of Seeds, Pebble
  Crab, Phobic Experiment, Pipton, Pit Pig, Potato, Psychosis Experiment, Rhinocebro, Safe, Salmon,
  Salt Crystals, Salt Pond, Salt Rack, Sammy, Sanguine Experiment, Sap, Scorpeon, Serving,
  Snortoise, Spotty Shrub, Spotty Sprig, Sugarwood Tree, Sulfuric Experiment, Swamp Pig, Swamp Pig
  Elder, Syrup, The Altar of Gnaw, The Forge, The Gnaw, The Gorge, The Gorge Recipes, The Gorge
  Seeds, Turnip, Wheat, Winter's Feast, Year of the Beefalo, Year of the Bunnyman, Year of the
  Carrat, Year of the Catcoon, Year of the Dragonfly, Year of the Gobbler, Year of the Pig King,
  Year of the Varg.

### Category:Fertilizer

- Keep (12): Bucket-o-poop, Compost, Compost Wrap, Fertilizzzer, Glommer's Goop, Growth Formula
  Starter, Guano, Manure, Rot, Rotten Egg, Spoiled Fish, Tree Jam.

- Exclude trước detail (1): Nutrient (`non_item:overview`).

### Category:Food

- Keep (122): Asparagus, Banana, Banana Pop, Banana Shake, Barnacle Linguine, Barnacle Pita,
  Barnacles, Batilisk Wing, Beefy Greens, Berries, Birchnut, Blue Cap, Breakfast Skillet, Bunny
  Stew, Butter Muffin, Cactus Flesh, Cactus Flower, California Roll, Carrot, Ceviche, Corn, Crab
  Meat, Creamy Potato Purée, Deerclops Eyeball, Dragon Fruit, Dragonpie, Drumstick, Durian, Eel,
  Egg, Eggplant, Electric Milk, Fancy Spiralled Tubers, Fig, Fig-Stuffed Trunk, Figatoni, Figgy
  Frogwich, Figkabab, Fish, Fish Morsel, Fish Tacos, Fishsticks, Fist Full of Jam, Flower Salad,
  Fresh Fruit Crepes, Frog Legs, Frozen Banana Daiquiri, Garlic, Gears, Glommer's Goop, Glow Berry,
  Glow Berry Mousse, Green Cap, Grim Galette, Guacamole, Guardian's Horn, Honey, Honey Ham, Ice,
  Jellybeans, Juicy Berries, Kelp Fronds, Koalefant Trunk, Leafy Meat, Leafy Meatloaf, Lesser Glow
  Berry, Lichen, Light Bulb, Lune Tree Blossom, Mandrake, Mandrake Soup, Meat, Meatballs,
  Melonsicle, Milkmade Hat, Monster Jerky, Monster Meat, Monster Tartare, Moon Shroom, Morsel, Mushy
  Cake, Naked Nostrils, Nightberry, Onion, Pepper, Phlegm, Pierogi, Plain Omelette, Pomegranate,
  Potato, Pumpkin, Pumpkin Cookies, Raw Fish, Red Cap, Salmon, Salsa Fresca, Salt Crystals, Seafood
  Gumbo, Seeds, Soothing Tea, Spicy Chili, Spicy Vegetable Stinger, Stone Fruit, Stuffed Eggplant,
  Stuffed Fish Heads, Stuffed Night Cap, Stuffed Pepper Poppers, Surf 'n' Turf, Switcherdoodle,
  Taffy, Tall Scotch Eggs, Tallbird Egg, Toma Root, Trail Mix, Turkey Dinner, Turnip, Unagi, Veggie
  Burger, Waffles, Watermelon, Wobster, Wobster Bisque.

- Exclude trước detail (62): "Ballphin Free" Tuna (`non_dst:shipwrecked`), Aloe (`non_dst:hamlet`),
  Bean Bugs (`non_dst:hamlet`), Bile-Covered Slop (`non_dst:shipwrecked`), Bisque
  (`non_dst:shipwrecked`), Brainy Matter (`non_dst:shipwrecked`), Caviar (`non_dst:shipwrecked`),
  Clippings (`non_dst:hamlet`), Coconut (`non_dst:shipwrecked`), Coffee (`non_dst:shipwrecked`),
  Coffee Beans (`non_dst:shipwrecked`), Cooking (`non_item:overview`), Crop Seeds
  (`non_item:overview`), Dead Jellyfish (`non_dst:shipwrecked`), Dead Rainbow Jellyfish
  (`non_dst:shipwrecked`), Dogfish (`non_dst:shipwrecked`), Doydoy Egg (`non_dst:shipwrecked`),
  Dried Jellyfish (`non_dst:shipwrecked`), Dried Seaweed (`non_dst:shipwrecked`), Eye of the Tiger
  Shark (`non_dst:shipwrecked`), Farm Plant (`non_item:overview`), Farming (`non_item:overview`),
  Feijoada (`non_dst:hamlet`), Food (`non_item:overview`), Food/Table (`non_item:overview`), Fruit
  (`non_item:overview`), Guides/Mushroom Guide (`non_item:overview`), Guides/Vegetarian Food
  (`non_item:overview`), Gummy Slug (`non_dst:hamlet`), Hallowed Nights
  (`non_item:category_mismatch`), Hard Shell Tacos (`non_dst:hamlet`), Iced Tea (`non_dst:hamlet`),
  Jelly-O Pop (`non_dst:shipwrecked`), Limpets (`non_dst:shipwrecked`), Lotus Flower
  (`non_dst:hamlet`), Magic Water (`non_dst:hamlet`), Meats (`non_item:overview`), Monster Food
  (`non_item:overview`), Mushroom (`non_item:overview`), Mussel (`non_dst:shipwrecked`), Mussel
  Bouillabaise (`non_dst:shipwrecked`), Nectar (`non_dst:hamlet`), Neon Quattro
  (`non_dst:shipwrecked`), Nettle Rolls (`non_dst:hamlet`), Ocean Fishes (`non_item:overview`),
  Pierrot Fish (`non_dst:shipwrecked`), Poison Dartfrog Legs (`non_dst:hamlet`), Purple Grouper
  (`non_dst:shipwrecked`), Radish (`non_dst:hamlet`), Roe (`non_dst:shipwrecked`), Seaweed
  (`non_dst:shipwrecked`), Seed Pod (`non_dst:hamlet`), Seeds Chance (`non_item:overview`), Shark
  Fin Soup (`non_dst:shipwrecked`), Sweet Potato (`non_dst:shipwrecked`), Sweet Potato Souffle
  (`non_dst:shipwrecked`), Swordfish (`non_dst:shipwrecked`), Tropical Fish (`non_dst:shipwrecked`),
  Tuber (`non_dst:hamlet`), Vegetable (`non_item:overview`), Winter's Feast
  (`non_item:category_mismatch`), Year of the Pig King (`non_item:category_mismatch`).

- Bỏ Category con, không đệ quy: Category:Crock Pot Recipes, Category:Dairy, Category:Eggs,
  Category:Fishes, Category:Fruits, Category:Meats, Category:Monster Foods, Category:Portable Crock
  Pot Recipes, Category:Sweeteners, Category:Vegetables.

### Category:Fight Tab

- Keep (15): Battle Helm, Battle Spear, Bee Mine, Boomerang, Football Helmet, Grass Suit, Ham Bat,
  Log Suit, Marble Suit, Morning Star, Scalemail, Spear, Tail o' Three Cats, Tooth Trap, Weather
  Pain.

- Exclude trước detail (17): Blunderbuss (`non_dst:hamlet`), Cactus Armor (`non_dst:shipwrecked`),
  Coconade (`non_dst:shipwrecked`), Cork Bat (`non_dst:hamlet`), Cutlass Supreme
  (`non_dst:shipwrecked`), Dart (`non_item:overview`), Fancy Helmet (`non_dst:hamlet`), Halberd
  (`non_dst:hamlet`), Horned Helmet (`non_dst:shipwrecked`), Limestone Suit (`non_dst:shipwrecked`),
  Mant Mask (`non_dst:hamlet`), Mant Suit (`non_dst:hamlet`), Poison Spear (`non_dst:shipwrecked`),
  Seashell Suit (`non_dst:shipwrecked`), Spear Gun (`non_dst:shipwrecked`), Tin Suit
  (`non_dst:hamlet`), Weevole Mantle (`non_dst:hamlet`).

### Category:Fishes

- Keep (6): Eel, Fish, Fish Morsel, Raw Fish, Wobster, Wobster Dinner.

- Exclude trước detail (14): Dead Jellyfish (`non_dst:shipwrecked`), Dead Rainbow Jellyfish
  (`non_dst:shipwrecked`), Dogfish (`non_dst:shipwrecked`), Dried Jellyfish (`non_dst:shipwrecked`),
  Limpets (`non_dst:shipwrecked`), Mussel (`non_dst:shipwrecked`), Neon Quattro
  (`non_dst:shipwrecked`), Pierrot Fish (`non_dst:shipwrecked`), Purple Grouper
  (`non_dst:shipwrecked`), Roe (`non_dst:shipwrecked`), Shark Fin (`non_dst:shipwrecked`), Shark Fin
  Soup (`non_dst:shipwrecked`), Swordfish (`non_dst:shipwrecked`), Tropical Fish
  (`non_dst:shipwrecked`).

### Category:A New Reign

- Keep (92): Ancient Beacon, Ancient Fence, Ancient Gateway, Ancient Key, Ancient Mural, Ancient
  Obelisk, Ancient Statue, Antlion, Atrium, Bee Queen, Bee Queen Crown, Birds, Blueprint, Bone
  Armor, Bone Helm, Boulder, Brush, Cactus, Cartographer's Desk, Cave Hole, Chilled Lavae, Cratered
  Moonrock, Critters, Crumpled Package, Deer Antler, Desert Stone, Feather, Feather Pencil, Flower,
  Friendly Scarecrow, Funcap, Gem Deer, Gigantic Beehive, Glass Sculptures, Grass Gekko, Grumble
  Bee, Iridescent Gem, Jellybeans, Juicy Berries, Juicy Berry Bush, Klaus, Lake, Loot Stash, Map
  Scroll, Marble Bean, Marble Sculptures, Marble Shrub, Marble Statues, Mini Sign, Moon Caller's
  Staff, Moon Dial, Moon Rock, Moon Stone, Moonlens, Mushroom Planter, Mushroom Spore, Napsack, No-
  Eyed Deer, Ocuvigil, Petals, Petrified Tree, Phlegm, Pillars, Potted Succulent, Potter's Wheel,
  Reanimated Skeleton, Relic, Rock Den, Royal Jelly, Saddle, Salt Lick, Sandstorm, Scaled Furnace,
  Shadow Atrium, Shadow Pieces, Shadow Thurible, Shroom Skin, Sketch, Stag Antler, Stagehand, Steel
  Wool, Suspicious Marble, Suspicious Moonrock, Tail o' Three Cats, The Lazy Deserter, Toadstool,
  Trinkets, Twiggy Tree, Twiggy Tree Cone, Wood Fence, Wood Gate, Woven Shadow.

- Exclude trước detail (18): A New Reign (`non_item:overview`), Blue Moonlens
  (`duplicate:canonical_redirect`), Cartography Filter (`non_item:overview`), Chess Pieces
  (`non_item:overview`), Critters Filter (`non_item:overview`), Dart (`non_item:overview`), Disease
  (`non_item:category_mismatch`), Goggles (`non_item:overview`), Green Moonlens
  (`duplicate:canonical_redirect`), Mushroom Lights (`non_item:overview`), Orange Moonlens
  (`duplicate:canonical_redirect`), Purple Moonlens (`duplicate:canonical_redirect`), Red Moonlens
  (`duplicate:canonical_redirect`), Sculptures Filter (`non_item:overview`), Wall
  (`non_item:overview`), Winter's Feast (`non_item:category_mismatch`), Year of the Gobbler
  (`non_item:category_mismatch`), Yellow Moonlens (`duplicate:canonical_redirect`).

- Bỏ Category con, không đệ quy: Category:Events, Category:Rare Blueprint Exclusive.

### Category:Ancient Tab

- Keep (14): Ancient Pseudoscience Station, Construction Amulet, Deconstruction Staff, Houndius
  Shootius, Magiluminescence, Pick/Axe, Star Caller's Staff, The Lazy Explorer, The Lazy Forager,
  Thulecite, Thulecite Club, Thulecite Crown, Thulecite Medallion, Thulecite Suit.

- Exclude trước detail (1): Wall (`non_item:overview`).

### Category:Ancient Tier 1

- Keep (9): Blueprint, Construction Amulet, Deconstruction Staff, Gardeneer Hat, Magiluminescence,
  Star Caller's Staff, Thulecite, Thulecite Medallion, Thulecite Wall.

- Exclude trước detail (1): Slingshot Ammo (`non_item:overview`).

- Bỏ namespace khác: ns=2 User:Bluegeist/Sandbox5, ns=2 User:Dark Clefita/Sandbox.

### Category:Ancient Tier 2

- Keep (7): Pick/Axe, Shadowcraft Plinth, The Lazy Explorer, The Lazy Forager, Thulecite Club,
  Thulecite Crown, Thulecite Suit.

### Category:Animals

- Keep (29): Bee, Beefalo, Bright-Eyed Frog, Bulbous Lightbug, Bunnyman, Butterfly, Buzzard,
  Catcoon, Dust Moth, Ewecus, Frog, Gem Deer, Glommer, Gobbler, Grass Gator, Koalefant, Moleworm,
  Mosling, Mosquito, No-Eyed Deer, Parrot Pirate, Pengull, Pig, Powder Monkey, Rabbit, Rock Lobster,
  Slurtle, Splumonkey, Volt Goat.

- Exclude trước detail (6): Blue Whale (`non_dst:shipwrecked`), Glowfly (`non_dst:hamlet`), Peagawk
  (`non_dst:hamlet`), Pog (`non_dst:hamlet`), White Whale (`non_dst:shipwrecked`), Wildbore
  (`non_dst:shipwrecked`).

- Bỏ Category con, không đệ quy: Category:Birds, Category:Followers, Category:Neutral Creatures,
  Category:Passive Creatures.

### Category:Birds

- Keep (10): Birds, Buzzard, Gobbler, Malbatross, Misshapen Bird, Moose/Goose, Mosling, Parrot
  Pirate, Pengull, Tallbird.

- Exclude trước detail (7): BFB (`non_dst:hamlet`), Birdcage (`non_item:category_mismatch`), Doydoy
  (`non_dst:shipwrecked`), Peagawk (`non_dst:hamlet`), Ro Bin (`non_dst:hamlet`), Sunken Boat
  (`non_dst:dont_starve`), Thunderbird (`non_dst:hamlet`).

### Category:Boss Monsters

- Keep (28): Ancient Guardian, Antlion, Armored Bearger, Bearger, Bee Queen, Celestial Champion,
  Crab King, Crystal Deerclops, Deerclops, Dragonfly, Eye of Terror, Frostjaw, Grand Forge Boarrior,
  Great Depths Worm, Infernal Swineclops, Klaus, Lord of the Fruit Flies, Malbatross, Moose/Goose,
  Nightmare Werepig, Possessed Varg, Reanimated Skeleton, Scrappy Werepig, Shadow Pieces, Spider
  Queen, Toadstool, Treeguard, W.A.R.B.O.T..

- Exclude trước detail (9): Ancient Herald (`non_dst:hamlet`), Iron Hulk (`non_dst:hamlet`), Mobs
  (`non_item:overview`), Palm Treeguard (`non_dst:shipwrecked`), Pugalisk (`non_dst:hamlet`),
  Quacken (`non_dst:shipwrecked`), Queen Womant (`non_dst:hamlet`), Sealnado
  (`non_dst:shipwrecked`), Tiger Shark (`non_dst:shipwrecked`).

### Category:Clockwork Monsters

- Keep (6): Clockwork Bishop, Clockwork Knight, Clockwork Rook, Damaged Bishop, Damaged Knight,
  Damaged Rook.

- Exclude trước detail (2): Floaty Boaty Knight (`non_dst:shipwrecked`), Flower
  (`non_item:category_mismatch`).

## Batch 7 direct member review

| Category | Direct | Child | Other namespace | Excluded | Publish |
|---|---:|---:|---:|---:|---:|
| Light Sources | 94 | 0 | 0 | 28 | 66 |
| Magic Tab | 30 | 0 | 0 | 10 | 20 |
| Magic Tier 1 | 19 | 0 | 1 | 5 | 14 |
| Magic Tier 2 | 14 | 0 | 0 | 5 | 9 |
| Meats | 48 | 1 | 0 | 15 | 33 |
| Melee Weapons | 38 | 0 | 0 | 15 | 23 |
| Mineable Objects | 32 | 0 | 0 | 9 | 23 |
| Mob Dropped Items | 205 | 3 | 0 | 63 | 142 |
| Mob Housing | 52 | 0 | 0 | 29 | 23 |
| Mob Spawning Entities | 124 | 2 | 1 | 47 | 77 |
| Mobs | 279 | 22 | 0 | 105 | 174 |
| Mods | 3 | 0 | 0 | 3 | 0 |
| Monster Foods | 9 | 0 | 0 | 3 | 6 |
| Monsters | 64 | 4 | 4 | 24 | 40 |
| Neutral Creatures | 36 | 2 | 0 | 14 | 22 |
| Nightmare State Indicator | 9 | 0 | 0 | 0 | 9 |
| Nocturnals | 23 | 0 | 0 | 6 | 17 |
| Ocean | 64 | 0 | 0 | 33 | 31 |
| Passive Creatures | 63 | 1 | 0 | 33 | 30 |

- Mapping keep/exclude authoritative nằm trong 18 file config và bản review
  `docs/superpowers/specs/2026-07-22-category-crawler-batch-7-review.md`.
- `Mods`, `The Lost Fragment`, `The Screecher` bị bỏ vì overview/community mod,
  không phải entity DST chính thức.
- `Spider Eggs` được giữ vì page có nội dung/variant DST dù category metadata
  thiếu; `Parrot Pirate` bị loại khỏi output batch 7 vì Shipwrecked-only.
- URL `Parrot Pirate` còn trong shared registry do batch cũ và được gắn cờ để
  xoá/recrawl có kiểm soát sau; không được xem là dữ liệu DST hợp lệ.
- 35 Category con và sáu member namespace khác chỉ được audit, không crawl đệ quy.

## Batch 8 direct member review

| Category | Direct | Child | Other namespace | Excluded | Publish | Action |
|---|---:|---:|---:|---:|---:|---|
| Plants | 66 | 1 | 0 | 29 | 37 | Done |
| Passive Creatures | 63 | 1 | 0 | 33 | 30 | Reuse previous Done |
| Portal | 9 | 0 | 0 | 7 | 2 | Done |
| Ranged Weapons | 15 | 0 | 0 | 8 | 7 | Done |
| Rare Blueprint Exclusive | 38 | 0 | 0 | 3 | 35 | Done |
| Refine Tab | 20 | 0 | 0 | 5 | 15 | Done |
| Resources | 106 | 3 | 0 | 27 | 79 | Done |
| Resurrection | 11 | 0 | 0 | 3 | 8 | Done |
| Ruins Creatures | 13 | 1 | 0 | 2 | 11 | Done |
| Science | 99 | 0 | 0 | 14 | 85 | Done |
| Science Tier 2 | 147 | 0 | 5 | 51 | 96 | Done |
| Science Tier 1 | 117 | 0 | 1 | 54 | 63 | Done |
| Seafaring Filter | 14 | 0 | 0 | 1 | 13 | Done |

- Mapping keep/exclude authoritative nằm trong 12 file config mới và
  `docs/superpowers/specs/2026-07-22-category-crawler-batch-8-review.md`.
- Năm canonical URL mới duy nhất: `Cave Banana Tree`, `Cave Lichen`, `Reeds`,
  `Spiky Tree`, `Totally Normal Tree`; các membership sau đó đều reuse.
- 109 canonical URL bị trùng giữa các nguồn; registry chỉ lưu/fetch một detail
  theo URL/code nhưng vẫn gắn đủ category membership.
- `Passive Creatures` không chạy lại vì config live vẫn khớp 63 direct/30
  publish; `Parrot Pirate` tiếp tục bị loại là Shipwrecked-only.
- Sáu Category con và sáu row User/Board/Talk/Thread chỉ được audit, không crawl
  đệ quy hoặc đưa vào seed namespace 0.

## Batch 9 direct member review

| Category | Direct | Child | Other namespace | Excluded | Publish | Action |
|---|---:|---:|---:|---:|---:|---|
| Shadow Magic Filter | 31 | 0 | 0 | 0 | 31 | Done |
| Spiders | 14 | 0 | 1 | 1 | 13 | Done |
| Structures | 278 | 4 | 3 | 123 | 155 | Done |
| Survival Tab | 34 | 0 | 0 | 10 | 24 | Done |
| Survivor Items Filter | 21 | 0 | 0 | 0 | 21 | Done |
| Tools Filter | 38 | 0 | 2 | 0 | 38 | Done |
| Tools Tab | 12 | 0 | 1 | 2 | 10 | Done |
| Turf Items | 50 | 0 | 0 | 18 | 32 | Done |
| Trees | 27 | 0 | 0 | 10 | 17 | Done |
| Treasure Hunting Tab | 4 | 0 | 0 | 4 | 0 | Skip: Hamlet-only |
| Vegetables | 33 | 1 | 1 | 7 | 26 | Done |
| Wall | 0 | 0 | 0 | 1 | 0 | Skip: overview article |
| Weapons | 58 | 3 | 0 | 23 | 35 | Done |
| Weather | 11 | 0 | 0 | 4 | 7 | Done |

- Mapping keep/exclude authoritative nằm trong 12 file config mới và
  `docs/superpowers/specs/2026-07-22-category-crawler-batch-9-review.md`.
- `Merm Head`, `Pig Head`, `Quagmire Firepit` là ba canonical URL DST mới duy
  nhất; 406 membership còn lại chỉ materialize từ shared cache.
- `Floor` redirect về overview `Turfs` nên bị loại trước registry. `Snow`
  resolve về canonical `Seasons/Winter`, có section DST và được giữ đúng một
  identity.
- `Structures` loại page độc quyền game khác, overview/sự kiện và hai mob
  category-mismatch; bốn Category con cùng ba namespace khác chỉ được audit.
- `Obsidian Axe` và `Obsidian Machete` bị loại là Shipwrecked-only dù redirect
  của wiki có thể trỏ sang page canonical rộng hơn.

## Shared item URLs

| Item URL | Status | Categories |
|---|---|---|
| [A Little Drama and QOL](https://dontstarve.fandom.com/wiki/A_Little_Drama_and_QOL) | Done | dont_starve_together |
| [A New Reign](https://dontstarve.fandom.com/wiki/A_New_Reign) | Done | dont_starve_together |
| [Abandoned Junk](https://dontstarve.fandom.com/wiki/Abandoned_Junk) | Done | dont_starve_together, from_beyond |
| [Abigail](https://dontstarve.fandom.com/wiki/Abigail) | Done | followers, light_sources, mobs, neutral_creatures |
| [Abigail's Flower](https://dontstarve.fandom.com/wiki/Abigail's_Flower) | Done | craftable_items, indestructible_object, items, magic_tab, mob_dropped_items, shadow_magic_filter, survivor_items_filter |
| [Abyss](https://dontstarve.fandom.com/wiki/Abyss) | Done | gameplay |
| [Accomploshrine](https://dontstarve.fandom.com/wiki/Accomploshrine) | Done | craftable_structures, science, science_tier_2, structures |
| [Accursed Trinket](https://dontstarve.fandom.com/wiki/Accursed_Trinket) | Done | dont_starve_together, items, mob_dropped_items |
| [Acid Rain](https://dontstarve.fandom.com/wiki/Acid_Rain) | Done | dont_starve_together, from_beyond, gameplay, health_loss, weather |
| [Ageless Watch](https://dontstarve.fandom.com/wiki/Ageless_Watch) | Done | craftable_items, dont_starve_together, items |
| [Alarming Clock](https://dontstarve.fandom.com/wiki/Alarming_Clock) | Done | craftable_items, dont_starve_together, equipable_items, items, magic_tier_2, melee_weapons, shadow_magic_filter, weapons |
| [Alchemy Engine](https://dontstarve.fandom.com/wiki/Alchemy_Engine) | Done | craftable_structures, science, science_tier_1, structures |
| [Amberosia](https://dontstarve.fandom.com/wiki/Amberosia) | Done | crock_pot_recipes, dont_starve_together, items |
| [An Eye for An Eye](https://dontstarve.fandom.com/wiki/An_Eye_for_An_Eye) | Done | dont_starve_together |
| [Anchor](https://dontstarve.fandom.com/wiki/Anchor) | Done | craftable_items, craftable_structures, dont_starve_together, items, seafaring_filter, structures |
| [Ancient Anchor](https://dontstarve.fandom.com/wiki/Ancient_Anchor) | Done | dont_starve_together, events, indestructible_object |
| [Ancient Archive](https://dontstarve.fandom.com/wiki/Ancient_Archive) | Done | dont_starve_together |
| [Ancient Beacon](https://dontstarve.fandom.com/wiki/Ancient_Beacon) | Done | a_new_reign, dont_starve_together, indestructible_object, light_sources, structures |
| [Ancient Brickwork](https://dontstarve.fandom.com/wiki/Ancient_Brickwork) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive, turf_items |
| [Ancient Chest](https://dontstarve.fandom.com/wiki/Ancient_Chest) | Done | dont_starve_together, indestructible_object, structures |
| [Ancient Fence](https://dontstarve.fandom.com/wiki/Ancient_Fence) | Done | a_new_reign, dont_starve_together, indestructible_object, structures |
| [Ancient Flooring](https://dontstarve.fandom.com/wiki/Ancient_Flooring) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive, turf_items |
| [Ancient Gateway](https://dontstarve.fandom.com/wiki/Ancient_Gateway) | Done | a_new_reign, dont_starve_together, indestructible_object, structures |
| [Ancient Guard Post](https://dontstarve.fandom.com/wiki/Ancient_Guard_Post) | Done | dont_starve_together, indestructible_object |
| [Ancient Guardian](https://dontstarve.fandom.com/wiki/Ancient_Guardian) | Done | boss_monsters, hostile_creatures, mobs, monsters, ruins_creatures |
| [Ancient Key](https://dontstarve.fandom.com/wiki/Ancient_Key) | Done | a_new_reign, boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Ancient Kiln](https://dontstarve.fandom.com/wiki/Ancient_Kiln) | Done | dont_starve_together, structures |
| [Ancient Lunarune Stone](https://dontstarve.fandom.com/wiki/Ancient_Lunarune_Stone) | Done | dont_starve_together, structures |
| [Ancient Moon Statue](https://dontstarve.fandom.com/wiki/Ancient_Moon_Statue) | Done | dont_starve_together, structures |
| [Ancient Mural](https://dontstarve.fandom.com/wiki/Ancient_Mural) | Done | a_new_reign, dont_starve_together, indestructible_object, structures |
| [Ancient Obelisk](https://dontstarve.fandom.com/wiki/Ancient_Obelisk) | Done | a_new_reign, dont_starve_together, indestructible_object |
| [Ancient Pseudoscience Filter](https://dontstarve.fandom.com/wiki/Ancient_Pseudoscience_Filter) | Done | dont_starve_together |
| [Ancient Pseudoscience Station](https://dontstarve.fandom.com/wiki/Ancient_Pseudoscience_Station) | Done | ancient_tab, crafting_stations, light_sources, mob_spawning_entities, structures |
| [Ancient Sentrypede](https://dontstarve.fandom.com/wiki/Ancient_Sentrypede) | Done | dont_starve_together, hostile_creatures, mobs |
| [Ancient Statue](https://dontstarve.fandom.com/wiki/Ancient_Statue) | Done | a_new_reign, dont_starve_together, indestructible_object, light_sources, mineable_objects, mob_spawning_entities, nightmare_state_indicator, resources, structures |
| [Ancient Stonework](https://dontstarve.fandom.com/wiki/Ancient_Stonework) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive, turf_items |
| [Ancient Tilework](https://dontstarve.fandom.com/wiki/Ancient_Tilework) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive, turf_items |
| [Anenemy](https://dontstarve.fandom.com/wiki/Anenemy) | Done | dont_starve_together |
| [Antlion](https://dontstarve.fandom.com/wiki/Antlion) | Done | a_new_reign, boss_monsters, dont_starve_together, health_loss, hostile_creatures, mobs, neutral_creatures |
| [Arboretum Experiment](https://dontstarve.fandom.com/wiki/Arboretum_Experiment) | Done | craftable_items, dont_starve_together, events, fuel, items |
| [Archaic Boat](https://dontstarve.fandom.com/wiki/Archaic_Boat) | Done | dont_starve_together, from_beyond, items, structures |
| [Archive Chandelier](https://dontstarve.fandom.com/wiki/Archive_Chandelier) | Done | dont_starve_together |
| [Archive Orchestrina](https://dontstarve.fandom.com/wiki/Archive_Orchestrina) | Done | dont_starve_together |
| [Archive Switch](https://dontstarve.fandom.com/wiki/Archive_Switch) | Done | dont_starve_together, indestructible_object |
| [Armermry](https://dontstarve.fandom.com/wiki/Armermry) | Done | craftable_structures, dont_starve_together, structures |
| [Armor](https://dontstarve.fandom.com/wiki/Armor) | Done | gameplay |
| [Armored Bearger](https://dontstarve.fandom.com/wiki/Armored_Bearger) | Done | boss_monsters, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Armour Filter](https://dontstarve.fandom.com/wiki/Armour_Filter) | Done | dont_starve_together |
| [Art?](https://dontstarve.fandom.com/wiki/Art%3F) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items |
| [Ashes](https://dontstarve.fandom.com/wiki/Ashes) | Done | items, mob_dropped_items |
| [Asparagazpacho](https://dontstarve.fandom.com/wiki/Asparagazpacho) | Done | dont_starve_together, items |
| [Asparagus](https://dontstarve.fandom.com/wiki/Asparagus) | Done | dont_starve_together, food, healing, items, vegetables |
| [Asparagus Soup](https://dontstarve.fandom.com/wiki/Asparagus_Soup) | Done | crock_pot_recipes, dont_starve_together, healing, items |
| [Astral Detector](https://dontstarve.fandom.com/wiki/Astral_Detector) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive, structures, tools_filter |
| [Astroggles](https://dontstarve.fandom.com/wiki/Astroggles) | Done | craftable_items, dont_starve_together, equipable_items, hats, items, rare_blueprint_exclusive |
| [Atrium](https://dontstarve.fandom.com/wiki/Atrium) | Done | a_new_reign, dont_starve_together |
| [Axe](https://dontstarve.fandom.com/wiki/Axe) | Done | celestial_tab, craftable_items, dont_starve_together, equipable_items, items, light_sources, science_tier_2, tools_filter, tools_tab |
| [Baby Spider](https://dontstarve.fandom.com/wiki/Baby_Spider) | Done | dont_starve_together, mobs |
| [Backpack](https://dontstarve.fandom.com/wiki/Backpack) | Done | backpacks, containers, craftable_items, equipable_items, items, science, science_tier_1, survival_tab |
| [Backstep Watch](https://dontstarve.fandom.com/wiki/Backstep_Watch) | Done | craftable_items, dont_starve_together, items |
| [Backtrek Watch](https://dontstarve.fandom.com/wiki/Backtrek_Watch) | Done | craftable_items, dont_starve_together, items, magic_tier_1 |
| [Bacon and Eggs](https://dontstarve.fandom.com/wiki/Bacon_and_Eggs) | Done | craftable_items, crock_pot_recipes, eggs, healing, items, meats |
| [Balloonomancy Tab](https://dontstarve.fandom.com/wiki/Balloonomancy_Tab) | Done | dont_starve_together |
| [Banana](https://dontstarve.fandom.com/wiki/Banana) | Done | dont_starve_together, food, fruits, healing, items, mob_dropped_items |
| [Banana Bush](https://dontstarve.fandom.com/wiki/Banana_Bush) | Done | dont_starve_together |
| [Banana Pop](https://dontstarve.fandom.com/wiki/Banana_Pop) | Done | cooling, crock_pot_recipes, dont_starve_together, food, healing, items |
| [Banana Shake](https://dontstarve.fandom.com/wiki/Banana_Shake) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, mob_dropped_items |
| [Barbed Helm](https://dontstarve.fandom.com/wiki/Barbed_Helm) | Done | items |
| [Barnacle Linguine](https://dontstarve.fandom.com/wiki/Barnacle_Linguine) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Barnacle Nigiri](https://dontstarve.fandom.com/wiki/Barnacle_Nigiri) | Done | dont_starve_together, items |
| [Barnacle Pita](https://dontstarve.fandom.com/wiki/Barnacle_Pita) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Barnacles](https://dontstarve.fandom.com/wiki/Barnacles) | Done | dont_starve_together, food |
| [Bat Bat](https://dontstarve.fandom.com/wiki/Bat_Bat) | Done | craftable_items, equipable_items, healing, items, magic_tab, magic_tier_2, melee_weapons, shadow_magic_filter, weapons |
| [Bat Cave](https://dontstarve.fandom.com/wiki/Bat_Cave) | Done | dont_starve_together, indestructible_object, mob_spawning_entities |
| [Bath Bomb](https://dontstarve.fandom.com/wiki/Bath_Bomb) | Done | celestial_filter, craftable_items, dont_starve_together, items |
| [Batilisk](https://dontstarve.fandom.com/wiki/Batilisk) | Done | cave_creatures, flying_creatures, hostile_creatures, mobs, monsters, nocturnals |
| [Batilisk Wing](https://dontstarve.fandom.com/wiki/Batilisk_Wing) | Done | food, healing, items, meats, mob_dropped_items |
| [Battle Call Canister](https://dontstarve.fandom.com/wiki/Battle_Call_Canister) | Done | craftable_items, dont_starve_together, items |
| [Battle Helm](https://dontstarve.fandom.com/wiki/Battle_Helm) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, fight_tab, hats, items, survivor_items_filter |
| [Battle Paddle](https://dontstarve.fandom.com/wiki/Battle_Paddle) | Done | dont_starve_together, equipable_items, items, melee_weapons, mob_dropped_items, weapons |
| [Battle Rönd](https://dontstarve.fandom.com/wiki/Battle_R%C3%B6nd) | Done | armour_filter, craftable_items, dont_starve_together, items |
| [Battle Songs](https://dontstarve.fandom.com/wiki/Battle_Songs) | Done | dont_starve_together, survivor_items_filter |
| [Battle Spear](https://dontstarve.fandom.com/wiki/Battle_Spear) | Done | craftable_items, dont_starve_together, equipable_items, fight_tab, items, melee_weapons, survivor_items_filter, weapons |
| [Battlemaster Pugna](https://dontstarve.fandom.com/wiki/Battlemaster_Pugna) | Done | dont_starve_together, events |
| [Beard Hair](https://dontstarve.fandom.com/wiki/Beard_Hair) | Done | craftable_items, fuel, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Beard Hair Rug](https://dontstarve.fandom.com/wiki/Beard_Hair_Rug) | Done | craftable_items, dont_starve_together, fuel, items, turf_items |
| [Beards](https://dontstarve.fandom.com/wiki/Beards) | Done | dont_starve_together |
| [Bearger](https://dontstarve.fandom.com/wiki/Bearger) | Done | boss_monsters, dont_starve_together, hostile_creatures, mobs |
| [Bed Roll](https://dontstarve.fandom.com/wiki/Bed_Roll) | Done | craftable_items, fuel, healing, items, science_tier_1, science_tier_2, survival_tab |
| [Bee](https://dontstarve.fandom.com/wiki/Bee) | Done | animals, flying_creatures, hostile_creatures, innocents, items, mob_dropped_items, mobs, neutral_creatures |
| [Bee Box](https://dontstarve.fandom.com/wiki/Bee_Box) | Done | craftable_structures, food_gardening_filter, food_tab, mob_housing, mob_spawning_entities, science, science_tier_2, structures |
| [Bee Mine](https://dontstarve.fandom.com/wiki/Bee_Mine) | Done | craftable_items, fight_tab, items, mob_spawning_entities, science, science_tier_1, weapons |
| [Bee Queen](https://dontstarve.fandom.com/wiki/Bee_Queen) | Done | a_new_reign, boss_monsters, dont_starve_together, flying_creatures, hostile_creatures, mob_spawning_entities, mobs |
| [Bee Queen Crown](https://dontstarve.fandom.com/wiki/Bee_Queen_Crown) | Done | a_new_reign, boss_dropped_items, dont_starve_together, equipable_items, hats, items, mob_dropped_items |
| [Beefalo](https://dontstarve.fandom.com/wiki/Beefalo) | Done | animals, followers, hostile_creatures, innocents, mob_spawning_entities, mobs, neutral_creatures |
| [Beefalo Bell](https://dontstarve.fandom.com/wiki/Beefalo_Bell) | Done | craftable_items, dont_starve_together, items, science_tier_1, tools_filter |
| [Beefalo Gloom Bell](https://dontstarve.fandom.com/wiki/Beefalo_Gloom_Bell) | Done | craftable_items, dont_starve_together, from_beyond, items |
| [Beefalo Grooming Station](https://dontstarve.fandom.com/wiki/Beefalo_Grooming_Station) | Done | craftable_structures, decorations_filter, dont_starve_together, science_tier_2, structures |
| [Beefalo Hat](https://dontstarve.fandom.com/wiki/Beefalo_Hat) | Done | clothing_filter, craftable_items, equipable_items, hats, items, science, science_tier_1 |
| [Beefalo Horn](https://dontstarve.fandom.com/wiki/Beefalo_Horn) | Done | items, mob_dropped_items |
| [Beefalo Riding Filter](https://dontstarve.fandom.com/wiki/Beefalo_Riding_Filter) | Done | dont_starve_together |
| [Beefalo Treats](https://dontstarve.fandom.com/wiki/Beefalo_Treats) | Done | beefalo_foods, crock_pot_recipes, dont_starve_together, items |
| [Beefalo Wool](https://dontstarve.fandom.com/wiki/Beefalo_Wool) | Done | craftable_items, fuel, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Beefy Greens](https://dontstarve.fandom.com/wiki/Beefy_Greens) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, meats |
| [Beehive](https://dontstarve.fandom.com/wiki/Beehive) | Done | mob_housing, mob_spawning_entities, structures |
| [Beekeeper Hat](https://dontstarve.fandom.com/wiki/Beekeeper_Hat) | Done | armour_filter, craftable_items, equipable_items, hats, items, science, science_tier_2 |
| [Beeswax](https://dontstarve.fandom.com/wiki/Beeswax) | Done | craftable_items, items, refine_tab |
| [Belongings](https://dontstarve.fandom.com/wiki/Belongings) | Done | dont_starve_together |
| [Belt of Hunger](https://dontstarve.fandom.com/wiki/Belt_of_Hunger) | Done | craftable_items, equipable_items, items, magic_tab, magic_tier_2, shadow_magic_filter |
| [Benevolent Rabbit King](https://dontstarve.fandom.com/wiki/Benevolent_Rabbit_King) | Done | crafting_stations, dont_starve_together, from_beyond, hostile_creatures, mob_spawning_entities, mobs, passive_creatures |
| [Bernie](https://dontstarve.fandom.com/wiki/Bernie) | Done | dont_starve_together, equipable_items, mobs, survivor_items_filter |
| [Berries](https://dontstarve.fandom.com/wiki/Berries) | Done | food, healing, items |
| [Berry Bush](https://dontstarve.fandom.com/wiki/Berry_Bush) | Done | fuel, items, mob_housing, mob_spawning_entities, plants |
| [Billy](https://dontstarve.fandom.com/wiki/Billy) | Done | dont_starve_together, events, mobs, passive_creatures |
| [Bio Data](https://dontstarve.fandom.com/wiki/Bio_Data) | Done | dont_starve_together, items |
| [Bio Scanalyzer](https://dontstarve.fandom.com/wiki/Bio_Scanalyzer) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Biomes](https://dontstarve.fandom.com/wiki/Biomes) | Done | gameplay |
| [Birchnut](https://dontstarve.fandom.com/wiki/Birchnut) | Done | dont_starve_together, food, healing, items, mob_dropped_items, plants |
| [Birchnut Tree](https://dontstarve.fandom.com/wiki/Birchnut_Tree) | Done | dont_starve_together, mob_spawning_entities, mobs, monsters, plants, resources, trees |
| [Birchnutter](https://dontstarve.fandom.com/wiki/Birchnutter) | Done | dont_starve_together, hostile_creatures, mobs, monsters, plants |
| [Bird Trap](https://dontstarve.fandom.com/wiki/Bird_Trap) | Done | craftable_items, food_gardening_filter, items, science, science_tier_1, survival_tab |
| [Birdcage](https://dontstarve.fandom.com/wiki/Birdcage) | Done | craftable_structures, food_gardening_filter, science, science_tier_2, structures |
| [Birds](https://dontstarve.fandom.com/wiki/Birds) | Done | a_new_reign, birds, flying_creatures, innocents, items, mobs, passive_creatures |
| [Black Flag](https://dontstarve.fandom.com/wiki/Black_Flag) | Done | dont_starve_together, items, resources |
| [Blacksmith's Edge](https://dontstarve.fandom.com/wiki/Blacksmith's_Edge) | Done | items |
| [Blood Shot](https://dontstarve.fandom.com/wiki/Blood_Shot) | Done | craftable_items, dont_starve_together, healing, items |
| [Blossomed Wreath](https://dontstarve.fandom.com/wiki/Blossomed_Wreath) | Done | items |
| [Blue Cap](https://dontstarve.fandom.com/wiki/Blue_Cap) | Done | boss_dropped_items, food, healing, health_loss, mob_dropped_items, vegetables |
| [Blue Gem](https://dontstarve.fandom.com/wiki/Blue_Gem) | Done | boss_dropped_items, craftable_items, infobox_missing_crafting_description, items, resources |
| [Blueprint](https://dontstarve.fandom.com/wiki/Blueprint) | Done | a_new_reign, ancient_tier_1, boss_dropped_items, craftable_items, dont_starve_together, fuel, infobox_missing_crafting_description, items, mob_dropped_items |
| [Boaraudience](https://dontstarve.fandom.com/wiki/Boaraudience) | Done | mobs |
| [Boards](https://dontstarve.fandom.com/wiki/Boards) | Done | craftable_items, fuel, items, refine_tab, science, science_tier_1 |
| [Boarilla](https://dontstarve.fandom.com/wiki/Boarilla) | Done | dont_starve_together, events, hostile_creatures, mobs |
| [Boat](https://dontstarve.fandom.com/wiki/Boat) | Done | craftable_items, craftable_structures, dont_starve_together, items, seafaring_filter, structures |
| [Boat Fragment](https://dontstarve.fandom.com/wiki/Boat_Fragment) | Done | dont_starve_together, ocean |
| [Boat Patch](https://dontstarve.fandom.com/wiki/Boat_Patch) | Done | craftable_items, dont_starve_together, items, seafaring_filter |
| [Bone Armor](https://dontstarve.fandom.com/wiki/Bone_Armor) | Done | a_new_reign, boss_dropped_items, dont_starve_together, equipable_items, items, mob_dropped_items |
| [Bone Bouillon](https://dontstarve.fandom.com/wiki/Bone_Bouillon) | Done | dont_starve_together, items, meats |
| [Bone Helm](https://dontstarve.fandom.com/wiki/Bone_Helm) | Done | a_new_reign, boss_dropped_items, dont_starve_together, equipable_items, hats, items, mob_dropped_items |
| [Bone Shards](https://dontstarve.fandom.com/wiki/Bone_Shards) | Done | craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Bones](https://dontstarve.fandom.com/wiki/Bones) | Done | indestructible_object |
| [Bookcase](https://dontstarve.fandom.com/wiki/Bookcase) | Done | craftable_structures, dont_starve_together, science_tier_1, structures |
| [Boomerang](https://dontstarve.fandom.com/wiki/Boomerang) | Done | craftable_items, equipable_items, fight_tab, items, ranged_weapons, science, science_tier_2, weapons |
| [Booster Shot](https://dontstarve.fandom.com/wiki/Booster_Shot) | Done | craftable_items, dont_starve_together, healing, items, science, science_tier_2, survival_tab |
| [Bootleg Getaway](https://dontstarve.fandom.com/wiki/Bootleg_Getaway) | Done | dont_starve_together, items |
| [Bottle Exchange Filter](https://dontstarve.fandom.com/wiki/Bottle_Exchange_Filter) | Done | dont_starve_together |
| [Boulder](https://dontstarve.fandom.com/wiki/Boulder) | Done | a_new_reign, mineable_objects, resources |
| [Bramble Husk](https://dontstarve.fandom.com/wiki/Bramble_Husk) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, fuel, items |
| [Bramble Trap](https://dontstarve.fandom.com/wiki/Bramble_Trap) | Done | craftable_items, dont_starve_together, health_loss, items |
| [Brambleshade Armor](https://dontstarve.fandom.com/wiki/Brambleshade_Armor) | Done | craftable_items, dont_starve_together, from_beyond, items |
| [Breakfast Skillet](https://dontstarve.fandom.com/wiki/Breakfast_Skillet) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Breezy Vest](https://dontstarve.fandom.com/wiki/Breezy_Vest) | Done | craftable_items, equipable_items, items, science, science_tier_2 |
| [Briar Wolf](https://dontstarve.fandom.com/wiki/Briar_Wolf) | Done | dont_starve_together, mobs |
| [Bridge](https://dontstarve.fandom.com/wiki/Bridge) | Done | gameplay, indestructible_object |
| [Bright-Eyed Frog](https://dontstarve.fandom.com/wiki/Bright-Eyed_Frog) | Done | animals, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Brightshade Armor](https://dontstarve.fandom.com/wiki/Brightshade_Armor) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Brightshade Bomb](https://dontstarve.fandom.com/wiki/Brightshade_Bomb) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items, weapons |
| [Brightshade Gestalt](https://dontstarve.fandom.com/wiki/Brightshade_Gestalt) | Done | dont_starve_together, from_beyond, mobs |
| [Brightshade Helm](https://dontstarve.fandom.com/wiki/Brightshade_Helm) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Brightshade Husk](https://dontstarve.fandom.com/wiki/Brightshade_Husk) | Done | from_beyond, items |
| [Brightshade Shoevel](https://dontstarve.fandom.com/wiki/Brightshade_Shoevel) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Brightshade Smasher](https://dontstarve.fandom.com/wiki/Brightshade_Smasher) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items, tools_filter |
| [Brightshade Staff](https://dontstarve.fandom.com/wiki/Brightshade_Staff) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Brightshade Sword](https://dontstarve.fandom.com/wiki/Brightshade_Sword) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Brightsmithy](https://dontstarve.fandom.com/wiki/Brightsmithy) | Done | celestial_filter, craftable_items, craftable_structures, crafting_stations, dont_starve_together, from_beyond, infobox_missing_crafting_description, items, structures |
| [Brightsmithy Filter](https://dontstarve.fandom.com/wiki/Brightsmithy_Filter) | Done | dont_starve_together |
| [Brilliant Mudslinger](https://dontstarve.fandom.com/wiki/Brilliant_Mudslinger) | Done | craftable_items, dont_starve_together, items |
| [Broken Clockworks](https://dontstarve.fandom.com/wiki/Broken_Clockworks) | Done | mob_spawning_entities, structures |
| [Broken Machinery](https://dontstarve.fandom.com/wiki/Broken_Machinery) | Done | dont_starve_together, structures |
| [Broken Shell](https://dontstarve.fandom.com/wiki/Broken_Shell) | Done | items, mob_dropped_items, resources |
| [Brush](https://dontstarve.fandom.com/wiki/Brush) | Done | a_new_reign, craftable_items, equipable_items, items, science_tier_2, tools_filter, tools_tab |
| [Bucket-o-poop](https://dontstarve.fandom.com/wiki/Bucket-o-poop) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter, food_tab, items, science_tier_2 |
| [Bug Net](https://dontstarve.fandom.com/wiki/Bug_Net) | Done | craftable_items, equipable_items, items, science, science_tier_1, survival_tab, tools_filter |
| [Bulbous Lightbug](https://dontstarve.fandom.com/wiki/Bulbous_Lightbug) | Done | animals, cave_creatures, dont_starve_together, followers, items, light_sources, mobs, passive_creatures |
| [Bull Kelp](https://dontstarve.fandom.com/wiki/Bull_Kelp) | Done | dont_starve_together, equipable_items, fuel, items, melee_weapons, ocean, plants, weapons |
| [Bumpers](https://dontstarve.fandom.com/wiki/Bumpers) | Done | craftable_items, craftable_structures, dont_starve_together, items, seafaring_filter, structures |
| [Bundling Wrap](https://dontstarve.fandom.com/wiki/Bundling_Wrap) | Done | containers, craftable_items, dont_starve_together, fuel, infobox_missing_crafting_description, items, rare_blueprint_exclusive, survival_tab |
| [Bunny Puff](https://dontstarve.fandom.com/wiki/Bunny_Puff) | Done | items, meats, mob_dropped_items, resources |
| [Bunny Stew](https://dontstarve.fandom.com/wiki/Bunny_Stew) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Bunnyman](https://dontstarve.fandom.com/wiki/Bunnyman) | Done | animals, cave_creatures, followers, innocents, mobs, neutral_creatures, nocturnals |
| [Burrow](https://dontstarve.fandom.com/wiki/Burrow) | Done | dont_starve_together, mob_housing, mob_spawning_entities |
| [Burrowing Horn](https://dontstarve.fandom.com/wiki/Burrowing_Horn) | Done | craftable_items, dont_starve_together, equipable_items, from_beyond, items |
| [Bush Hat](https://dontstarve.fandom.com/wiki/Bush_Hat) | Done | craftable_items, equipable_items, hats, items, science, science_tier_2 |
| [Butter](https://dontstarve.fandom.com/wiki/Butter) | Done | healing, items, mob_dropped_items |
| [Butter Muffin](https://dontstarve.fandom.com/wiki/Butter_Muffin) | Done | crock_pot_recipes, food, healing, items |
| [Butterfly](https://dontstarve.fandom.com/wiki/Butterfly) | Done | animals, flying_creatures, innocents, items, mob_dropped_items, mobs, passive_creatures |
| [Butterfly Wings](https://dontstarve.fandom.com/wiki/Butterfly_Wings) | Done | healing, items |
| [Buzzard](https://dontstarve.fandom.com/wiki/Buzzard) | Done | animals, birds, dont_starve_together, flying_creatures, mobs, neutral_creatures |
| [Cachebox](https://dontstarve.fandom.com/wiki/Cachebox) | Done | dont_starve_together |
| [Cactus](https://dontstarve.fandom.com/wiki/Cactus) | Done | a_new_reign, dont_starve_together, plants |
| [Cactus Flesh](https://dontstarve.fandom.com/wiki/Cactus_Flesh) | Done | dont_starve_together, food, healing, health_loss, items, vegetables |
| [Cactus Flower](https://dontstarve.fandom.com/wiki/Cactus_Flower) | Done | dont_starve_together, food, healing, items, resources |
| [Calibrated Perceiver](https://dontstarve.fandom.com/wiki/Calibrated_Perceiver) | Done | dont_starve_together, items |
| [California Roll](https://dontstarve.fandom.com/wiki/California_Roll) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Campfire](https://dontstarve.fandom.com/wiki/Campfire) | Done | cooking_filter, craftable_structures, light_sources, structures |
| [Cannon](https://dontstarve.fandom.com/wiki/Cannon) | Done | craftable_items, craftable_structures, dont_starve_together, items, rare_blueprint_exclusive, seafaring_filter, structures |
| [Cannonball](https://dontstarve.fandom.com/wiki/Cannonball) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive |
| [Captain's Tricorn](https://dontstarve.fandom.com/wiki/Captain's_Tricorn) | Done | dont_starve_together, equipable_items, hats, items, mob_dropped_items |
| [Carpentry Filter](https://dontstarve.fandom.com/wiki/Carpentry_Filter) | Done | dont_starve_together, from_beyond |
| [Carpeted Flooring](https://dontstarve.fandom.com/wiki/Carpeted_Flooring) | Done | craftable_items, decorations_filter, fuel, items, science_tier_2, turf_items |
| [Carrat](https://dontstarve.fandom.com/wiki/Carrat) | Done | dont_starve_together, mobs, passive_creatures |
| [Carrot](https://dontstarve.fandom.com/wiki/Carrot) | Done | dont_starve_together, food, healing, items, mob_dropped_items, plants, vegetables |
| [Cartographer's Desk](https://dontstarve.fandom.com/wiki/Cartographer's_Desk) | Done | a_new_reign, craftable_structures, crafting_stations, dont_starve_together, science_tier_1, structures |
| [Cartography Filter](https://dontstarve.fandom.com/wiki/Cartography_Filter) | Done | dont_starve_together |
| [Cat Cap](https://dontstarve.fandom.com/wiki/Cat_Cap) | Done | craftable_items, dont_starve_together, equipable_items, hats, items, science, science_tier_2 |
| [Cat Tail](https://dontstarve.fandom.com/wiki/Cat_Tail) | Done | dont_starve_together, items, mob_dropped_items, resources |
| [Catcoon](https://dontstarve.fandom.com/wiki/Catcoon) | Done | animals, dont_starve_together, followers, innocents, mob_spawning_entities, mobs, neutral_creatures |
| [Cave Banana Tree](https://dontstarve.fandom.com/wiki/Cave_Banana_Tree) | Done | plants, resources, trees |
| [Cave Hole](https://dontstarve.fandom.com/wiki/Cave_Hole) | Done | a_new_reign, dont_starve_together, indestructible_object |
| [Cave Lichen](https://dontstarve.fandom.com/wiki/Cave_Lichen) | Done | plants |
| [Cave Light](https://dontstarve.fandom.com/wiki/Cave_Light) | Done | indestructible_object, light_sources |
| [Cave Rock Turf](https://dontstarve.fandom.com/wiki/Cave_Rock_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Cave Spider](https://dontstarve.fandom.com/wiki/Cave_Spider) | Done | cave_creatures, followers, hostile_creatures, mobs, monsters, nocturnals, spiders |
| [Caves](https://dontstarve.fandom.com/wiki/Caves) | Done | gameplay |
| [Cawnival Creation Filter](https://dontstarve.fandom.com/wiki/Cawnival_Creation_Filter) | Done | dont_starve_together |
| [Celestial Champion](https://dontstarve.fandom.com/wiki/Celestial_Champion) | Done | boss_monsters, dont_starve_together, hostile_creatures, light_sources, mobs, monsters |
| [Celestial Filter](https://dontstarve.fandom.com/wiki/Celestial_Filter) | Done | dont_starve_together |
| [Celestial Fissure](https://dontstarve.fandom.com/wiki/Celestial_Fissure) | Done | dont_starve_together |
| [Celestial Orb](https://dontstarve.fandom.com/wiki/Celestial_Orb) | Done | crafting_stations, dont_starve_together, items |
| [Celestial Portal](https://dontstarve.fandom.com/wiki/Celestial_Portal) | Done | craftable_structures, dont_starve_together, infobox_missing_crafting_description, light_sources, resurrection, structures |
| [Ceviche](https://dontstarve.fandom.com/wiki/Ceviche) | Done | cooling, crock_pot_recipes, dont_starve_together, food, healing, items |
| [Chairs](https://dontstarve.fandom.com/wiki/Chairs) | Done | dont_starve_together, from_beyond |
| [Character quotes](https://dontstarve.fandom.com/wiki/Character_quotes) | Done | gameplay |
| [Characters](https://dontstarve.fandom.com/wiki/Characters) | Done | gameplay |
| [Charcoal](https://dontstarve.fandom.com/wiki/Charcoal) | Done | boss_dropped_items, fuel, items, mob_dropped_items, resources |
| [Charged Glassy Rock](https://dontstarve.fandom.com/wiki/Charged_Glassy_Rock) | Done | dont_starve_together, mineable_objects |
| [Charlie](https://dontstarve.fandom.com/wiki/Charlie) | Done | gameplay, health_loss, mobs |
| [Checkerboard Flooring](https://dontstarve.fandom.com/wiki/Checkerboard_Flooring) | Done | craftable_items, decorations_filter, fuel, items, science, science_tier_2, turf_items |
| [Chef Pouch](https://dontstarve.fandom.com/wiki/Chef_Pouch) | Done | backpacks, containers, cooking_filter, craftable_items, dont_starve_together, equipable_items, items, survival_tab, survivor_items_filter |
| [Chess Pieces](https://dontstarve.fandom.com/wiki/Chess_Pieces) | Done | dont_starve_together |
| [Chest](https://dontstarve.fandom.com/wiki/Chest) | Done | containers, craftable_structures, dont_starve_together, infobox_missing_crafting_description, science, science_tier_1, structures |
| [Chester](https://dontstarve.fandom.com/wiki/Chester) | Done | containers, followers, light_sources, mobs, passive_creatures |
| [Chili Flakes](https://dontstarve.fandom.com/wiki/Chili_Flakes) | Done | craftable_items, dont_starve_together, items |
| [Chilled Amulet](https://dontstarve.fandom.com/wiki/Chilled_Amulet) | Done | cooling, craftable_items, equipable_items, items, magic_tab, magic_tier_1, shadow_magic_filter |
| [Chilled Lavae](https://dontstarve.fandom.com/wiki/Chilled_Lavae) | Done | a_new_reign, dont_starve_together, items, mob_dropped_items |
| [Circuit Extractor](https://dontstarve.fandom.com/wiki/Circuit_Extractor) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Circuits](https://dontstarve.fandom.com/wiki/Circuits) | Done | dont_starve_together, food_gardening_filter, infobox_missing_crafting_description, survivor_items_filter |
| [Clairvoyant Crown](https://dontstarve.fandom.com/wiki/Clairvoyant_Crown) | Done | items |
| [Clean Sweeper](https://dontstarve.fandom.com/wiki/Clean_Sweeper) | Done | craftable_items, decorations_filter, dont_starve_together, equipable_items, items, science_tier_2, tools_filter |
| [Clever Disguise](https://dontstarve.fandom.com/wiki/Clever_Disguise) | Done | craftable_items, dont_starve_together, equipable_items, hats, items, survivor_items_filter |
| [Clockmaker's Tools](https://dontstarve.fandom.com/wiki/Clockmaker's_Tools) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Clocksmithy Tab](https://dontstarve.fandom.com/wiki/Clocksmithy_Tab) | Done | dont_starve_together |
| [Clockwork Bishop](https://dontstarve.fandom.com/wiki/Clockwork_Bishop) | Done | cave_creatures, clockwork_monsters, followers, hostile_creatures, mobs, monsters, ruins_creatures |
| [Clockwork Knight](https://dontstarve.fandom.com/wiki/Clockwork_Knight) | Done | clockwork_monsters, followers, hostile_creatures, mobs, monsters, ruins_creatures |
| [Clockwork Rook](https://dontstarve.fandom.com/wiki/Clockwork_Rook) | Done | clockwork_monsters, followers, hostile_creatures, mobs, monsters, ruins_creatures |
| [Clothes](https://dontstarve.fandom.com/wiki/Clothes) | Done | gameplay |
| [Clothing Filter](https://dontstarve.fandom.com/wiki/Clothing_Filter) | Done | dont_starve_together |
| [Clout Snout](https://dontstarve.fandom.com/wiki/Clout_Snout) | Done | dont_starve_together, items, mobs |
| [Coaching Whistle](https://dontstarve.fandom.com/wiki/Coaching_Whistle) | Done | craftable_items, dont_starve_together, items, survivor_items_filter |
| [Coat of Carrots](https://dontstarve.fandom.com/wiki/Coat_of_Carrots) | Done | craftable_items, craftable_structures, dont_starve_together, equipable_items, from_beyond, items, structures |
| [Cobblestones](https://dontstarve.fandom.com/wiki/Cobblestones) | Done | craftable_items, decorations_filter, dont_starve_together, fuel, items, science, science_tier_2, turf_items |
| [Codex Umbra](https://dontstarve.fandom.com/wiki/Codex_Umbra) | Done | craftable_items, crafting_stations, followers, fuel, health_loss, items, mob_spawning_entities, shadow_magic_filter |
| [Codex Umbra Filter](https://dontstarve.fandom.com/wiki/Codex_Umbra_Filter) | Done | dont_starve_together |
| [Coin](https://dontstarve.fandom.com/wiki/Coin) | Done | dont_starve_together, items |
| [Collected Dust](https://dontstarve.fandom.com/wiki/Collected_Dust) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive |
| [Combat](https://dontstarve.fandom.com/wiki/Combat) | Done | gameplay |
| [Commander's Helm](https://dontstarve.fandom.com/wiki/Commander's_Helm) | Done | armour_filter, craftable_items, dont_starve_together, items |
| [Communal Kelp Dish](https://dontstarve.fandom.com/wiki/Communal_Kelp_Dish) | Done | craftable_structures, dont_starve_together, structures |
| [Compass](https://dontstarve.fandom.com/wiki/Compass) | Done | craftable_items, equipable_items, items, science, survival_tab, tools_filter |
| [Compendium](https://dontstarve.fandom.com/wiki/Compendium) | Done | dont_starve_together |
| [Compost](https://dontstarve.fandom.com/wiki/Compost) | Done | dont_starve_together, fertilizer, items |
| [Compost Wrap](https://dontstarve.fandom.com/wiki/Compost_Wrap) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter, fuel, healing, items |
| [Composting Bin](https://dontstarve.fandom.com/wiki/Composting_Bin) | Done | craftable_structures, dont_starve_together, food_gardening_filter, science_tier_2, structures |
| [Commands](https://dontstarve.fandom.com/wiki/Console/Commands) | Done | gameplay |
| [Don't Starve Together Commands](https://dontstarve.fandom.com/wiki/Console/Don't_Starve_Together_Commands) | Done | dont_starve_together, gameplay |
| [Conspicuous Chest](https://dontstarve.fandom.com/wiki/Conspicuous_Chest) | Done | dont_starve_together, structures |
| [Construction Amulet](https://dontstarve.fandom.com/wiki/Construction_Amulet) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items, items |
| [Cookbook](https://dontstarve.fandom.com/wiki/Cookbook) | Done | cooking_filter, craftable_items, dont_starve_together, items, science_tier_1 |
| [Cookie Cutter](https://dontstarve.fandom.com/wiki/Cookie_Cutter) | Done | dont_starve_together, mobs, monsters, neutral_creatures, ocean |
| [Cookie Cutter Cap](https://dontstarve.fandom.com/wiki/Cookie_Cutter_Cap) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, hats, items, science_tier_2 |
| [Cookie Cutter Shell](https://dontstarve.fandom.com/wiki/Cookie_Cutter_Shell) | Done | dont_starve_together, items, mob_dropped_items, resources |
| [Cooking](https://dontstarve.fandom.com/wiki/Cooking) | Done | gameplay |
| [Cooking Filter](https://dontstarve.fandom.com/wiki/Cooking_Filter) | Done | dont_starve_together |
| [Cookpot](https://dontstarve.fandom.com/wiki/Cookpot) | Done | items |
| [Corn](https://dontstarve.fandom.com/wiki/Corn) | Done | food, healing |
| [Costumes](https://dontstarve.fandom.com/wiki/Costumes) | Done | dont_starve_together, items, mob_dropped_items |
| [Crab Guard](https://dontstarve.fandom.com/wiki/Crab_Guard) | Done | dont_starve_together, hostile_creatures, structures |
| [Crab King](https://dontstarve.fandom.com/wiki/Crab_King) | Done | boss_monsters, dont_starve_together, mobs, ocean |
| [Crab Meat](https://dontstarve.fandom.com/wiki/Crab_Meat) | Done | dont_starve_together, events, food |
| [Crab Trap](https://dontstarve.fandom.com/wiki/Crab_Trap) | Done | items |
| [Crabby Hermit](https://dontstarve.fandom.com/wiki/Crabby_Hermit) | Done | crafting_stations, dont_starve_together |
| [Cracked Pillar](https://dontstarve.fandom.com/wiki/Cracked_Pillar) | Done | dont_starve_together |
| [Crafting](https://dontstarve.fandom.com/wiki/Crafting) | Done | gameplay |
| [Craftsmerm House](https://dontstarve.fandom.com/wiki/Craftsmerm_House) | Done | craftable_structures, dont_starve_together, mob_housing, science_tier_1, structures, survivor_items_filter |
| [Cratered Moonrock](https://dontstarve.fandom.com/wiki/Cratered_Moonrock) | Done | a_new_reign, craftable_items, dont_starve_together, items, refine_tab, science_tier_2 |
| [Crawling Horror](https://dontstarve.fandom.com/wiki/Crawling_Horror) | Done | mobs |
| [Creamy Potato Purée](https://dontstarve.fandom.com/wiki/Creamy_Potato_Pur%C3%A9e) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, vegetables |
| [Critters](https://dontstarve.fandom.com/wiki/Critters) | Done | a_new_reign, dont_starve_together, followers, light_sources, mobs, passive_creatures |
| [Critters Filter](https://dontstarve.fandom.com/wiki/Critters_Filter) | Done | dont_starve_together |
| [Crock Pot](https://dontstarve.fandom.com/wiki/Crock_Pot) | Done | containers, cooking_filter, craftable_structures, food_tab, light_sources, science_tier_1, structures |
| [Crocommander](https://dontstarve.fandom.com/wiki/Crocommander) | Done | dont_starve_together, events, hostile_creatures, mobs |
| [Crumpled Package](https://dontstarve.fandom.com/wiki/Crumpled_Package) | Done | a_new_reign, dont_starve_together, items |
| [Crustashine](https://dontstarve.fandom.com/wiki/Crustashine) | Done | dont_starve_together, items, mob_dropped_items, mobs |
| [Crystal Deerclops](https://dontstarve.fandom.com/wiki/Crystal_Deerclops) | Done | boss_monsters, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Crystal Tiara](https://dontstarve.fandom.com/wiki/Crystal_Tiara) | Done | items |
| [Cult of the Lamb Crossover](https://dontstarve.fandom.com/wiki/Cult_of_the_Lamb_Crossover) | Done | dont_starve_together |
| [Curio Cabinet](https://dontstarve.fandom.com/wiki/Curio_Cabinet) | Done | dont_starve_together |
| [Cut Grass](https://dontstarve.fandom.com/wiki/Cut_Grass) | Done | beefalo_foods, fuel, items, mob_dropped_items, mob_spawning_entities, resources |
| [Cut Reeds](https://dontstarve.fandom.com/wiki/Cut_Reeds) | Done | beefalo_foods, fuel, items, resources |
| [Cut Stone](https://dontstarve.fandom.com/wiki/Cut_Stone) | Done | craftable_items, items, refine_tab, science_tier_1 |
| [Cutless](https://dontstarve.fandom.com/wiki/Cutless) | Done | dont_starve_together, equipable_items, fuel, items, melee_weapons, mob_dropped_items, weapons |
| [Dairy](https://dontstarve.fandom.com/wiki/Dairy) | Done | dont_starve_together, mob_dropped_items |
| [Damaged Bishop](https://dontstarve.fandom.com/wiki/Damaged_Bishop) | Done | clockwork_monsters, followers, hostile_creatures, mobs, monsters, ruins_creatures |
| [Damaged Knight](https://dontstarve.fandom.com/wiki/Damaged_Knight) | Done | clockwork_monsters, followers, hostile_creatures, mobs, monsters, ruins_creatures |
| [Damaged Rook](https://dontstarve.fandom.com/wiki/Damaged_Rook) | Done | clockwork_monsters, followers, hostile_creatures, mobs, monsters, ruins_creatures |
| [Dangling Depth Dweller](https://dontstarve.fandom.com/wiki/Dangling_Depth_Dweller) | Done | cave_creatures, followers, hostile_creatures, mobs, monsters, ruins_creatures, spiders |
| [Dapper Vest](https://dontstarve.fandom.com/wiki/Dapper_Vest) | Done | craftable_items, equipable_items, items, science, science_tier_2 |
| [Dark Sword](https://dontstarve.fandom.com/wiki/Dark_Sword) | Done | boss_dropped_items, craftable_items, equipable_items, items, magic_tab, magic_tier_2, melee_weapons, mob_dropped_items, shadow_magic_filter, weapons |
| [Dark Tatters](https://dontstarve.fandom.com/wiki/Dark_Tatters) | Done | boss_dropped_items, dont_starve_together, from_beyond, items, mob_dropped_items |
| [Dart](https://dontstarve.fandom.com/wiki/Dart) | Done | dont_starve_together, weapons |
| [Darts](https://dontstarve.fandom.com/wiki/Darts) | Done | items |
| [Day-Night Cycle](https://dontstarve.fandom.com/wiki/Day-Night_Cycle) | Done | gameplay |
| [Deadly Brightshade](https://dontstarve.fandom.com/wiki/Deadly_Brightshade) | Done | dont_starve_together, from_beyond, mobs |
| [Death](https://dontstarve.fandom.com/wiki/Death) | Done | gameplay |
| [Deciduous Forest](https://dontstarve.fandom.com/wiki/Deciduous_Forest) | Done | dont_starve_together |
| [Deciduous Turf](https://dontstarve.fandom.com/wiki/Deciduous_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, fuel, items, turf_items |
| [Deck Illuminator](https://dontstarve.fandom.com/wiki/Deck_Illuminator) | Done | craftable_items, dont_starve_together, items, light_sources |
| [Deconstruction Staff](https://dontstarve.fandom.com/wiki/Deconstruction_Staff) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items, items |
| [Decorations Filter](https://dontstarve.fandom.com/wiki/Decorations_Filter) | Done | dont_starve_together |
| [Deer Antler](https://dontstarve.fandom.com/wiki/Deer_Antler) | Done | a_new_reign, dont_starve_together, items, mob_dropped_items |
| [Deerclops](https://dontstarve.fandom.com/wiki/Deerclops) | Done | boss_monsters, hostile_creatures, mobs |
| [Deerclops Eyeball](https://dontstarve.fandom.com/wiki/Deerclops_Eyeball) | Done | boss_dropped_items, food, healing, items, meats, mob_dropped_items |
| [Den Decorating Set](https://dontstarve.fandom.com/wiki/Den_Decorating_Set) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Depths Worm](https://dontstarve.fandom.com/wiki/Depths_Worm) | Done | cave_creatures, hostile_creatures, light_sources, mobs, monsters, nightmare_state_indicator, ruins_creatures |
| [Desert](https://dontstarve.fandom.com/wiki/Desert) | Done | dont_starve_together |
| [Desert Stone](https://dontstarve.fandom.com/wiki/Desert_Stone) | Done | a_new_reign, boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Directional Sign](https://dontstarve.fandom.com/wiki/Directional_Sign) | Done | craftable_structures, decorations_filter, dont_starve_together, science_tier_1, structures |
| [Disease](https://dontstarve.fandom.com/wiki/Disease) | Done | dont_starve_together, gameplay |
| [Dock Kit](https://dontstarve.fandom.com/wiki/Dock_Kit) | Done | craftable_items, decorations_filter, dont_starve_together, items, rare_blueprint_exclusive |
| [Dock Piling Kit](https://dontstarve.fandom.com/wiki/Dock_Piling_Kit) | Done | craftable_items, decorations_filter, dont_starve_together, items, rare_blueprint_exclusive, structures |
| [Don't Starve Together](https://dontstarve.fandom.com/wiki/Don't_Starve_Together) | Done | dont_starve_together |
| [Doohickey](https://dontstarve.fandom.com/wiki/Doohickey) | Done | dont_starve_together, items |
| [Down Feather](https://dontstarve.fandom.com/wiki/Down_Feather) | Done | boss_dropped_items, dont_starve_together, items, mob_dropped_items, resources |
| [Dragon Fruit](https://dontstarve.fandom.com/wiki/Dragon_Fruit) | Done | food, healing, items |
| [Dragonfly](https://dontstarve.fandom.com/wiki/Dragonfly) | Done | boss_monsters, dont_starve_together, flying_creatures, hostile_creatures, light_sources, mob_spawning_entities, mobs |
| [Dragonpie](https://dontstarve.fandom.com/wiki/Dragonpie) | Done | crock_pot_recipes, food, fruits, healing, items |
| [Dreaded Mudslinger](https://dontstarve.fandom.com/wiki/Dreaded_Mudslinger) | Done | craftable_items, dont_starve_together, items |
| [Dreadstone](https://dontstarve.fandom.com/wiki/Dreadstone) | Done | craftable_items, dont_starve_together, from_beyond, items, resources |
| [Dreadstone Armor](https://dontstarve.fandom.com/wiki/Dreadstone_Armor) | Done | armour_filter, craftable_items, dont_starve_together, infobox_missing_crafting_description, items, rare_blueprint_exclusive, shadow_magic_filter |
| [Dreadstone Helm](https://dontstarve.fandom.com/wiki/Dreadstone_Helm) | Done | armour_filter, craftable_items, dont_starve_together, infobox_missing_crafting_description, items, rare_blueprint_exclusive, shadow_magic_filter |
| [Dreadstone Outcrop](https://dontstarve.fandom.com/wiki/Dreadstone_Outcrop) | Done | dont_starve_together, from_beyond |
| [Dreadstone Wall](https://dontstarve.fandom.com/wiki/Dreadstone_Wall) | Done | craftable_items, dont_starve_together, items, rare_blueprint_exclusive |
| [Dried Kelp Fronds](https://dontstarve.fandom.com/wiki/Dried_Kelp_Fronds) | Done | dont_starve_together, healing, items, vegetables |
| [Driftwood](https://dontstarve.fandom.com/wiki/Driftwood) | Done | dont_starve_together, resources |
| [Driftwood Piece](https://dontstarve.fandom.com/wiki/Driftwood_Piece) | Done | dont_starve_together, fuel, items, resources |
| [Drumstick](https://dontstarve.fandom.com/wiki/Drumstick) | Done | boss_dropped_items, food, healing, items, meats, mob_dropped_items |
| [Drying Rack](https://dontstarve.fandom.com/wiki/Drying_Rack) | Done | cooking_filter, craftable_structures, food_tab, science, science_tier_1, structures |
| [Dumbbells](https://dontstarve.fandom.com/wiki/Dumbbells) | Done | dont_starve_together, infobox_missing_crafting_description |
| [Durability](https://dontstarve.fandom.com/wiki/Durability) | Done | gameplay |
| [Durian](https://dontstarve.fandom.com/wiki/Durian) | Done | food, health_loss, monster_foods |
| [Dust Moth](https://dontstarve.fandom.com/wiki/Dust_Moth) | Done | animals, cave_creatures, dont_starve_together, innocents, mobs, passive_creatures |
| [Earthquake](https://dontstarve.fandom.com/wiki/Earthquake) | Done | gameplay |
| [Ectoherbology Tab](https://dontstarve.fandom.com/wiki/Ectoherbology_Tab) | Done | dont_starve_together |
| [Eel](https://dontstarve.fandom.com/wiki/Eel) | Done | fishes, food, healing, items, meats |
| [Egg](https://dontstarve.fandom.com/wiki/Egg) | Done | eggs, food, items, mob_dropped_items |
| [Eggplant](https://dontstarve.fandom.com/wiki/Eggplant) | Done | food, healing, vegetables |
| [Elastispacer](https://dontstarve.fandom.com/wiki/Elastispacer) | Done | craftable_items, dont_starve_together, from_beyond, items |
| [Elding Spear](https://dontstarve.fandom.com/wiki/Elding_Spear) | Done | craftable_items, dont_starve_together, items, melee_weapons, weapons |
| [Electric Milk](https://dontstarve.fandom.com/wiki/Electric_Milk) | Done | dont_starve_together, food, healing, items, mob_dropped_items |
| [Electrical Doodad](https://dontstarve.fandom.com/wiki/Electrical_Doodad) | Done | craftable_items, items, mob_dropped_items, science, science_tier_1 |
| [Embalming Spritz](https://dontstarve.fandom.com/wiki/Embalming_Spritz) | Done | craftable_items, dont_starve_together, from_beyond, items |
| [Emotes](https://dontstarve.fandom.com/wiki/Emotes) | Done | dont_starve_together |
| [Emoticons](https://dontstarve.fandom.com/wiki/Emoticons) | Done | dont_starve_together |
| [Empty Bottle](https://dontstarve.fandom.com/wiki/Empty_Bottle) | Done | craftable_items, dont_starve_together, items, mob_dropped_items, ocean, refine_tab, resources, science_tier_2 |
| [Empty Frame](https://dontstarve.fandom.com/wiki/Empty_Frame) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items |
| [Endothermic Fire](https://dontstarve.fandom.com/wiki/Endothermic_Fire) | Done | cooling, craftable_structures, dont_starve_together, light_sources, science, science_tier_1, science_tier_2, structures |
| [Engineering Tab](https://dontstarve.fandom.com/wiki/Engineering_Tab) | Done | dont_starve_together |
| [Enlightened Crown](https://dontstarve.fandom.com/wiki/Enlightened_Crown) | Done | boss_dropped_items, dont_starve_together, equipable_items, hats, items, light_sources, mob_dropped_items |
| [Enlightened Shard](https://dontstarve.fandom.com/wiki/Enlightened_Shard) | Done | dont_starve_together, items, light_sources |
| [Enlightenment](https://dontstarve.fandom.com/wiki/Enlightenment) | Done | dont_starve_together, gameplay |
| [Ethereal Embers](https://dontstarve.fandom.com/wiki/Ethereal_Embers) | Done | dont_starve_together, items |
| [Evergreen](https://dontstarve.fandom.com/wiki/Evergreen) | Done | mob_spawning_entities, plants, resources, trees |
| [Ewecus](https://dontstarve.fandom.com/wiki/Ewecus) | Done | animals, hostile_creatures, mobs |
| [Extra-Adorable Lavae](https://dontstarve.fandom.com/wiki/Extra-Adorable_Lavae) | Done | dont_starve_together, followers, light_sources, mobs, passive_creatures |
| [Eye Bone](https://dontstarve.fandom.com/wiki/Eye_Bone) | Done | indestructible_object, items, mob_spawning_entities |
| [Eye Mask](https://dontstarve.fandom.com/wiki/Eye_Mask) | Done | boss_dropped_items, dont_starve_together, equipable_items, hats, items, mob_dropped_items |
| [Eye of Terror](https://dontstarve.fandom.com/wiki/Eye_of_Terror) | Done | boss_monsters, dont_starve_together, mobs |
| [Eyebrella](https://dontstarve.fandom.com/wiki/Eyebrella) | Done | cooling, craftable_items, dont_starve_together, equipable_items, hats, items, science, science_tier_2 |
| [Fancy Spiralled Tubers](https://dontstarve.fandom.com/wiki/Fancy_Spiralled_Tubers) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, vegetables |
| [Farm Plant](https://dontstarve.fandom.com/wiki/Farm_Plant) | Done | dont_starve_together, gameplay |
| [Farm Soil](https://dontstarve.fandom.com/wiki/Farm_Soil) | Done | dont_starve_together, items, turf_items |
| [Farming](https://dontstarve.fandom.com/wiki/Farming) | Done | gameplay |
| [Fashion Melon](https://dontstarve.fandom.com/wiki/Fashion_Melon) | Done | cooling, craftable_items, dont_starve_together, equipable_items, hats, items, science_tier_1 |
| [Feather](https://dontstarve.fandom.com/wiki/Feather) | Done | a_new_reign, dont_starve_together, fuel, items, mob_dropped_items, resources |
| [Feather Hat](https://dontstarve.fandom.com/wiki/Feather_Hat) | Done | craftable_items, equipable_items, hats, items, science, science_tier_2 |
| [Feather Pencil](https://dontstarve.fandom.com/wiki/Feather_Pencil) | Done | a_new_reign, craftable_items, decorations_filter, items, science_tier_1, tools_filter, tools_tab |
| [Feathered Reed Tunic](https://dontstarve.fandom.com/wiki/Feathered_Reed_Tunic) | Done | items |
| [Feathered Wreath](https://dontstarve.fandom.com/wiki/Feathered_Wreath) | Done | items |
| [Feathery Canvas](https://dontstarve.fandom.com/wiki/Feathery_Canvas) | Done | craftable_items, dont_starve_together, items, refine_tab, science_tier_2 |
| [Fencing Sword](https://dontstarve.fandom.com/wiki/Fencing_Sword) | Done | craftable_items, dont_starve_together, items, melee_weapons, science_tier_2, weapons |
| [Fertilizzzer](https://dontstarve.fandom.com/wiki/Fertilizzzer) | Done | craftable_items, dont_starve_together, fertilizer, from_beyond, fuel, items |
| [Fiery Pen](https://dontstarve.fandom.com/wiki/Fiery_Pen) | Done | dont_starve_together, equipable_items, items, ranged_weapons, weapons |
| [Fig](https://dontstarve.fandom.com/wiki/Fig) | Done | dont_starve_together, food, fruits, healing |
| [Fig-Stuffed Trunk](https://dontstarve.fandom.com/wiki/Fig-Stuffed_Trunk) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Figatoni](https://dontstarve.fandom.com/wiki/Figatoni) | Done | craftable_items, crock_pot_recipes, dont_starve_together, food, healing, items |
| [Figgy Frogwich](https://dontstarve.fandom.com/wiki/Figgy_Frogwich) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Figkabab](https://dontstarve.fandom.com/wiki/Figkabab) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Fire](https://dontstarve.fandom.com/wiki/Fire) | Done | gameplay, health_loss, light_sources |
| [Fire Nettle Fronds](https://dontstarve.fandom.com/wiki/Fire_Nettle_Fronds) | Done | dont_starve_together, items |
| [Fire Pump](https://dontstarve.fandom.com/wiki/Fire_Pump) | Done | craftable_items, craftable_structures, dont_starve_together, items, seafaring_filter, structures |
| [Fire Staff](https://dontstarve.fandom.com/wiki/Fire_Staff) | Done | craftable_items, equipable_items, items, magic_tab, magic_tier_2, ranged_weapons, shadow_magic_filter, weapons |
| [Fireflies](https://dontstarve.fandom.com/wiki/Fireflies) | Done | cave_creatures, fuel, items, light_sources, mob_dropped_items, mobs, nocturnals, passive_creatures |
| [Fish](https://dontstarve.fandom.com/wiki/Fish) | Done | fishes, food, healing, items, mob_dropped_items |
| [Fish Cordon Bleu](https://dontstarve.fandom.com/wiki/Fish_Cordon_Bleu) | Done | dont_starve_together, healing, items, meats |
| [Fish Food](https://dontstarve.fandom.com/wiki/Fish_Food) | Done | craftable_items, dont_starve_together, items |
| [Fish Morsel](https://dontstarve.fandom.com/wiki/Fish_Morsel) | Done | dont_starve_together, fishes, food, healing, items, meats, mob_dropped_items |
| [Fish Scale-O-Matic](https://dontstarve.fandom.com/wiki/Fish_Scale-O-Matic) | Done | craftable_structures, decorations_filter, dont_starve_together, science_tier_2, structures |
| [Fish Tacos](https://dontstarve.fandom.com/wiki/Fish_Tacos) | Done | crock_pot_recipes, food, healing, items |
| [Fishing Filter](https://dontstarve.fandom.com/wiki/Fishing_Filter) | Done | dont_starve_together |
| [Fishing Rod](https://dontstarve.fandom.com/wiki/Fishing_Rod) | Done | craftable_items, equipable_items, items, science, science_tier_1, survival_tab, tools_filter |
| [Fishing Tab](https://dontstarve.fandom.com/wiki/Fishing_Tab) | Done | dont_starve_together |
| [Fishsticks](https://dontstarve.fandom.com/wiki/Fishsticks) | Done | crock_pot_recipes, food, healing, items, meats |
| [Fist Full of Jam](https://dontstarve.fandom.com/wiki/Fist_Full_of_Jam) | Done | craftable_items, crock_pot_recipes, food, healing, items |
| [Flare](https://dontstarve.fandom.com/wiki/Flare) | Done | craftable_items, dont_starve_together, items, survival_tab, tools_filter |
| [Fleshy Bulb](https://dontstarve.fandom.com/wiki/Fleshy_Bulb) | Done | craftable_items, fuel, infobox_missing_crafting_description, items, mob_dropped_items, mob_spawning_entities, plants |
| [Flint](https://dontstarve.fandom.com/wiki/Flint) | Done | craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Floating Lantern](https://dontstarve.fandom.com/wiki/Floating_Lantern) | Done | craftable_items, dont_starve_together, items |
| [Floats](https://dontstarve.fandom.com/wiki/Floats) | Done | dont_starve_together |
| [Floral Shirt](https://dontstarve.fandom.com/wiki/Floral_Shirt) | Done | cooling, craftable_items, dont_starve_together, equipable_items, items, science, science_tier_2 |
| [Florid Postern](https://dontstarve.fandom.com/wiki/Florid_Postern) | Done | dont_starve_together, indestructible_object, light_sources, resurrection, structures |
| [Flour](https://dontstarve.fandom.com/wiki/Flour) | Done | items |
| [Flower](https://dontstarve.fandom.com/wiki/Flower) | Done | a_new_reign, dont_starve_together, health_loss, nightmare_state_indicator, plants |
| [Flower Headband](https://dontstarve.fandom.com/wiki/Flower_Headband) | Done | items |
| [Flower Salad](https://dontstarve.fandom.com/wiki/Flower_Salad) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Food & Gardening Filter](https://dontstarve.fandom.com/wiki/Food_%26_Gardening_Filter) | Done | dont_starve_together |
| [Football Helmet](https://dontstarve.fandom.com/wiki/Football_Helmet) | Done | armour_filter, craftable_items, equipable_items, fight_tab, hats, items, science, science_tier_2 |
| [Forest Turf](https://dontstarve.fandom.com/wiki/Forest_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Forge Portal](https://dontstarve.fandom.com/wiki/Forge_Portal) | Done | dont_starve_together, events, indestructible_object, mob_spawning_entities |
| [Forget-Me-Lots](https://dontstarve.fandom.com/wiki/Forget-Me-Lots) | Done | dont_starve_together, items |
| [Forging Hammer](https://dontstarve.fandom.com/wiki/Forging_Hammer) | Done | dont_starve_together, items |
| [Fossils](https://dontstarve.fandom.com/wiki/Fossils) | Done | boss_dropped_items, dont_starve_together, items, mob_dropped_items, mob_spawning_entities, structures |
| [Fountain of Knowledge](https://dontstarve.fandom.com/wiki/Fountain_of_Knowledge) | Done | dont_starve_together, items, structures |
| [Freezing](https://dontstarve.fandom.com/wiki/Freezing) | Done | gameplay, health_loss, weather |
| [Fresh Fruit Crepes](https://dontstarve.fandom.com/wiki/Fresh_Fruit_Crepes) | Done | dont_starve_together, food, healing, items |
| [Friendly Fruit Fly Fruit](https://dontstarve.fandom.com/wiki/Friendly_Fruit_Fly_Fruit) | Done | boss_dropped_items, dont_starve_together, followers, items, mob_dropped_items, mobs |
| [Friendly Scarecrow](https://dontstarve.fandom.com/wiki/Friendly_Scarecrow) | Done | a_new_reign, craftable_structures, dont_starve_together, mob_spawning_entities, science_tier_1, structures |
| [Frog](https://dontstarve.fandom.com/wiki/Frog) | Done | animals, hostile_creatures, mobs |
| [Frog Legs](https://dontstarve.fandom.com/wiki/Frog_Legs) | Done | boss_dropped_items, food, healing, items, meats, mob_dropped_items |
| [Frog Rain](https://dontstarve.fandom.com/wiki/Frog_Rain) | Done | dont_starve_together, gameplay |
| [Froggle Bunwich](https://dontstarve.fandom.com/wiki/Froggle_Bunwich) | Done | crock_pot_recipes, healing, items, meats |
| [From Beyond](https://dontstarve.fandom.com/wiki/From_Beyond) | Done | dont_starve_together, from_beyond |
| [Frostjaw](https://dontstarve.fandom.com/wiki/Frostjaw) | Done | boss_monsters, dont_starve_together, mobs |
| [Frozen Banana Daiquiri](https://dontstarve.fandom.com/wiki/Frozen_Banana_Daiquiri) | Done | cooling, crock_pot_recipes, dont_starve_together, food, healing, items |
| [Fruit Medley](https://dontstarve.fandom.com/wiki/Fruit_Medley) | Done | cooling, crock_pot_recipes, healing, items |
| [Funcap](https://dontstarve.fandom.com/wiki/Funcap) | Done | a_new_reign, clothing_filter, craftable_items, dont_starve_together, equipable_items, hats, items, rare_blueprint_exclusive |
| [Fungal Turf](https://dontstarve.fandom.com/wiki/Fungal_Turf) | Done | craftable_items, fuel, items, turf_items |
| [Fur Tuft](https://dontstarve.fandom.com/wiki/Fur_Tuft) | Done | boss_dropped_items, dont_starve_together, fuel, items, mob_dropped_items |
| [Fused Shadeling](https://dontstarve.fandom.com/wiki/Fused_Shadeling) | Done | dont_starve_together, from_beyond, mobs, monsters |
| [Garden Detritus](https://dontstarve.fandom.com/wiki/Garden_Detritus) | Done | dont_starve_together |
| [Garden Digamajig](https://dontstarve.fandom.com/wiki/Garden_Digamajig) | Done | craftable_items, dont_starve_together, food_gardening_filter, items, science_tier_1, structures |
| [Garden Hoe](https://dontstarve.fandom.com/wiki/Garden_Hoe) | Done | craftable_items, dont_starve_together, equipable_items, food_gardening_filter, items, science_tier_1, science_tier_2, tools_filter |
| [Gardeneer Hat](https://dontstarve.fandom.com/wiki/Gardeneer_Hat) | Done | ancient_tier_1, craftable_items, dont_starve_together, equipable_items, food_gardening_filter, hats, items, science_tier_1 |
| [Garland](https://dontstarve.fandom.com/wiki/Garland) | Done | craftable_items, equipable_items, hats, items, science |
| [Garlic](https://dontstarve.fandom.com/wiki/Garlic) | Done | dont_starve_together, events, food, healing, vegetables |
| [Garlic Powder](https://dontstarve.fandom.com/wiki/Garlic_Powder) | Done | craftable_items, dont_starve_together, items |
| [Gears](https://dontstarve.fandom.com/wiki/Gears) | Done | food, healing, items, mob_dropped_items |
| [Gem Deer](https://dontstarve.fandom.com/wiki/Gem_Deer) | Done | a_new_reign, animals, dont_starve_together, hostile_creatures, mobs |
| [Geode Fruit](https://dontstarve.fandom.com/wiki/Geode_Fruit) | Done | dont_starve_together, from_beyond, items, structures |
| [Gestalt](https://dontstarve.fandom.com/wiki/Gestalt) | Done | dont_starve_together, hostile_creatures, mobs |
| [Ghost](https://dontstarve.fandom.com/wiki/Ghost) | Done | hostile_creatures, light_sources, mobs, monsters |
| [Ghost Characters](https://dontstarve.fandom.com/wiki/Ghost_Characters) | Done | dont_starve_together, light_sources |
| [Ghostly Elixir](https://dontstarve.fandom.com/wiki/Ghostly_Elixir) | Done | dont_starve_together, healing, survivor_items_filter |
| [Giant Crops](https://dontstarve.fandom.com/wiki/Giant_Crops) | Done | dont_starve_together |
| [Gigantic Beehive](https://dontstarve.fandom.com/wiki/Gigantic_Beehive) | Done | a_new_reign, dont_starve_together, mob_housing, mob_spawning_entities |
| [Gizmo](https://dontstarve.fandom.com/wiki/Gizmo) | Done | dont_starve_together, items |
| [Glass Cutter](https://dontstarve.fandom.com/wiki/Glass_Cutter) | Done | celestial_filter, celestial_tab, craftable_items, dont_starve_together, equipable_items, items, melee_weapons, weapons |
| [Glass Sculptures](https://dontstarve.fandom.com/wiki/Glass_Sculptures) | Done | a_new_reign, dont_starve_together, structures |
| [Glommer](https://dontstarve.fandom.com/wiki/Glommer) | Done | animals, dont_starve_together, flying_creatures, followers, innocents, mobs, passive_creatures |
| [Glommer's Flower](https://dontstarve.fandom.com/wiki/Glommer's_Flower) | Done | dont_starve_together, fuel, items, light_sources, plants |
| [Glommer's Goop](https://dontstarve.fandom.com/wiki/Glommer's_Goop) | Done | dont_starve_together, fertilizer, food, fuel, healing, items, mob_dropped_items |
| [Glommer's Statue](https://dontstarve.fandom.com/wiki/Glommer's_Statue) | Done | dont_starve_together, indestructible_object, mineable_objects, mob_spawning_entities, structures |
| [Glommer's Wings](https://dontstarve.fandom.com/wiki/Glommer's_Wings) | Done | dont_starve_together, fuel, items, mob_dropped_items |
| [Gloomerang](https://dontstarve.fandom.com/wiki/Gloomerang) | Done | craftable_items, dont_starve_together, equipable_items, from_beyond, items, ranged_weapons, weapons |
| [Gloomthorn](https://dontstarve.fandom.com/wiki/Gloomthorn) | Done | dont_starve_together, from_beyond, plants, trees |
| [Glossary](https://dontstarve.fandom.com/wiki/Glossary) | Done | gameplay |
| [Glow Berry](https://dontstarve.fandom.com/wiki/Glow_Berry) | Done | food, fruits, healing, items, light_sources, mob_dropped_items |
| [Glow Berry Mousse](https://dontstarve.fandom.com/wiki/Glow_Berry_Mousse) | Done | craftable_items, dont_starve_together, food, items |
| [Gnarwail](https://dontstarve.fandom.com/wiki/Gnarwail) | Done | dont_starve_together, mobs, ocean |
| [Gnarwail Horn](https://dontstarve.fandom.com/wiki/Gnarwail_Horn) | Done | dont_starve_together, items, mob_dropped_items |
| [Goat Milk](https://dontstarve.fandom.com/wiki/Goat_Milk) | Done | dont_starve_together, events, items |
| [Gobbler](https://dontstarve.fandom.com/wiki/Gobbler) | Done | animals, birds, mobs, passive_creatures |
| [Goggles](https://dontstarve.fandom.com/wiki/Goggles) | Done | dont_starve_together, hats |
| [Gold Flooring](https://dontstarve.fandom.com/wiki/Gold_Flooring) | Done | craftable_items, decorations_filter, dont_starve_together, fuel, items, turf_items |
| [Gold Nugget](https://dontstarve.fandom.com/wiki/Gold_Nugget) | Done | boss_dropped_items, craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, refine_tab, resources |
| [Gourmet Salt Lick](https://dontstarve.fandom.com/wiki/Gourmet_Salt_Lick) | Done | craftable_structures, dont_starve_together, from_beyond, science_tier_2, structures |
| [Gramophone](https://dontstarve.fandom.com/wiki/Gramophone) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items, science, science_tier_2 |
| [Grand Forge Boarrior](https://dontstarve.fandom.com/wiki/Grand_Forge_Boarrior) | Done | boss_monsters, dont_starve_together, events, hostile_creatures, mobs |
| [Grass Gator](https://dontstarve.fandom.com/wiki/Grass_Gator) | Done | animals, dont_starve_together, mobs, ocean |
| [Grass Gekko](https://dontstarve.fandom.com/wiki/Grass_Gekko) | Done | a_new_reign, dont_starve_together, mobs, passive_creatures, resources |
| [Grass Raft](https://dontstarve.fandom.com/wiki/Grass_Raft) | Done | craftable_items, craftable_structures, dont_starve_together, items, seafaring_filter, structures |
| [Grass Suit](https://dontstarve.fandom.com/wiki/Grass_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab, fuel, items, science |
| [Grass Tuft](https://dontstarve.fandom.com/wiki/Grass_Tuft) | Done | fuel, items, mob_spawning_entities, plants, resources |
| [Grass Turf](https://dontstarve.fandom.com/wiki/Grass_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Grave](https://dontstarve.fandom.com/wiki/Grave) | Done | indestructible_object, mob_spawning_entities |
| [Graveyard](https://dontstarve.fandom.com/wiki/Graveyard) | Done | gameplay |
| [Grazer](https://dontstarve.fandom.com/wiki/Grazer) | Done | dont_starve_together, from_beyond, mobs |
| [Great Depths Worm](https://dontstarve.fandom.com/wiki/Great_Depths_Worm) | Done | boss_monsters, cave_creatures, dont_starve_together, from_beyond, hostile_creatures, mobs, monsters |
| [Great Tree Trunk](https://dontstarve.fandom.com/wiki/Great_Tree_Trunk) | Done | dont_starve_together, indestructible_object, ocean |
| [Green Cap](https://dontstarve.fandom.com/wiki/Green_Cap) | Done | boss_dropped_items, food, health_loss, mob_dropped_items, vegetables |
| [Green Gem](https://dontstarve.fandom.com/wiki/Green_Gem) | Done | boss_dropped_items, craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Grim Galette](https://dontstarve.fandom.com/wiki/Grim_Galette) | Done | dont_starve_together, food, healing, health_loss, items |
| [Growth Formula Starter](https://dontstarve.fandom.com/wiki/Growth_Formula_Starter) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter, items, science_tier_2 |
| [Grumble Bee](https://dontstarve.fandom.com/wiki/Grumble_Bee) | Done | a_new_reign, dont_starve_together, flying_creatures, hostile_creatures, mobs |
| [Guacamole](https://dontstarve.fandom.com/wiki/Guacamole) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, meats |
| [Guano](https://dontstarve.fandom.com/wiki/Guano) | Done | fertilizer, fuel, items, mob_dropped_items, resources |
| [Guano Turf](https://dontstarve.fandom.com/wiki/Guano_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Guardian's Horn](https://dontstarve.fandom.com/wiki/Guardian's_Horn) | Done | boss_dropped_items, food, healing, items, meats, mob_dropped_items |
| [Don’t Starve Together Dedicated Servers](https://dontstarve.fandom.com/wiki/Guides/Don%E2%80%99t_Starve_Together_Dedicated_Servers) | Done | dont_starve_together |
| [Gunpowder](https://dontstarve.fandom.com/wiki/Gunpowder) | Done | craftable_items, health_loss, items, science, science_tier_2, weapons |
| [Hallowed Nights](https://dontstarve.fandom.com/wiki/Hallowed_Nights) | Done | dont_starve_together, events, healing |
| [Ham Bat](https://dontstarve.fandom.com/wiki/Ham_Bat) | Done | craftable_items, equipable_items, fight_tab, items, melee_weapons, science, science_tier_2, weapons |
| [Hammer](https://dontstarve.fandom.com/wiki/Hammer) | Done | craftable_items, equipable_items, items, science, tools_filter, tools_tab |
| [Handy Remote](https://dontstarve.fandom.com/wiki/Handy_Remote) | Done | craftable_items, dont_starve_together, items |
| [Hardwood Hat](https://dontstarve.fandom.com/wiki/Hardwood_Hat) | Done | armour_filter, craftable_items, dont_starve_together, items |
| [Harp Statue](https://dontstarve.fandom.com/wiki/Harp_Statue) | Done | mineable_objects, resources, structures |
| [Hay Wall](https://dontstarve.fandom.com/wiki/Hay_Wall) | Done | craftable_items, craftable_structures, decorations_filter, items, science, science_tier_1, structures |
| [Healing Filter](https://dontstarve.fandom.com/wiki/Healing_Filter) | Done | dont_starve_together |
| [Healing Glop](https://dontstarve.fandom.com/wiki/Healing_Glop) | Done | craftable_items, dont_starve_together, items |
| [Healing Salve](https://dontstarve.fandom.com/wiki/Healing_Salve) | Done | craftable_items, healing, items, science, science_tier_1, survival_tab |
| [Health](https://dontstarve.fandom.com/wiki/Health) | Done | gameplay |
| [Hearthsfire Crystals](https://dontstarve.fandom.com/wiki/Hearthsfire_Crystals) | Done | items |
| [Hermit Home](https://dontstarve.fandom.com/wiki/Hermit_Home) | Done | craftable_structures, dont_starve_together, infobox_missing_crafting_description, structures |
| [Hermit Island](https://dontstarve.fandom.com/wiki/Hermit_Island) | Done | dont_starve_together, ocean |
| [Hibearnation Vest](https://dontstarve.fandom.com/wiki/Hibearnation_Vest) | Done | craftable_items, dont_starve_together, equipable_items, items, science_tier_2 |
| [Hollow Stump](https://dontstarve.fandom.com/wiki/Hollow_Stump) | Done | dont_starve_together, mob_housing, mob_spawning_entities, structures |
| [Honey](https://dontstarve.fandom.com/wiki/Honey) | Done | boss_dropped_items, food, healing, items, mob_dropped_items |
| [Honey Crystals](https://dontstarve.fandom.com/wiki/Honey_Crystals) | Done | craftable_items, dont_starve_together, items |
| [Honey Ham](https://dontstarve.fandom.com/wiki/Honey_Ham) | Done | crock_pot_recipes, food, healing, items, meats |
| [Honey Nuggets](https://dontstarve.fandom.com/wiki/Honey_Nuggets) | Done | crock_pot_recipes, healing, items |
| [Honey Poultice](https://dontstarve.fandom.com/wiki/Honey_Poultice) | Done | craftable_items, healing, items, science_tier_2, survival_tab |
| [Honeycomb](https://dontstarve.fandom.com/wiki/Honeycomb) | Done | boss_dropped_items, items, mob_dropped_items |
| [Horizon Expandinator](https://dontstarve.fandom.com/wiki/Horizon_Expandinator) | Done | dont_starve_together, from_beyond, items, mob_dropped_items |
| [Horror Hound](https://dontstarve.fandom.com/wiki/Horror_Hound) | Done | dont_starve_together, hostile_creatures, mobs, monsters |
| [Hostile Flare](https://dontstarve.fandom.com/wiki/Hostile_Flare) | Done | craftable_items, dont_starve_together, items |
| [Hot Dragon Chili Salad](https://dontstarve.fandom.com/wiki/Hot_Dragon_Chili_Salad) | Done | dont_starve_together, health_loss, items |
| [Hot Spring](https://dontstarve.fandom.com/wiki/Hot_Spring) | Done | dont_starve_together |
| [Hound](https://dontstarve.fandom.com/wiki/Hound) | Done | hostile_creatures, mob_spawning_entities, mobs, monsters |
| [Hound's Tooth](https://dontstarve.fandom.com/wiki/Hound's_Tooth) | Done | craftable_items, infobox_missing_crafting_description, items, mob_dropped_items |
| [Hound Mound](https://dontstarve.fandom.com/wiki/Hound_Mound) | Done | mob_housing, mob_spawning_entities |
| [Houndius Shootius](https://dontstarve.fandom.com/wiki/Houndius_Shootius) | Done | ancient_tab, craftable_items, craftable_structures, items, light_sources, mobs, structures |
| [Howlitzer](https://dontstarve.fandom.com/wiki/Howlitzer) | Done | craftable_items, dont_starve_together, equipable_items, items, ranged_weapons, weapons |
| [Humble Lamb Idol](https://dontstarve.fandom.com/wiki/Humble_Lamb_Idol) | Done | cooking_filter, craftable_structures, dont_starve_together, light_sources, rare_blueprint_exclusive, structures |
| [Hunger](https://dontstarve.fandom.com/wiki/Hunger) | Done | gameplay |
| [Hutch](https://dontstarve.fandom.com/wiki/Hutch) | Done | cave_creatures, containers, dont_starve_together, followers, light_sources, mobs, passive_creatures |
| [Ice](https://dontstarve.fandom.com/wiki/Ice) | Done | cooling, food, healing, items, refine_tab, resources, science_tier_2 |
| [Ice Box](https://dontstarve.fandom.com/wiki/Ice_Box) | Done | containers, cooking_filter, craftable_structures, food_tab, science, science_tier_2, structures |
| [Ice Cream](https://dontstarve.fandom.com/wiki/Ice_Cream) | Done | cooling, craftable_items, crock_pot_recipes, dont_starve_together, items |
| [Ice Crystaleyezer](https://dontstarve.fandom.com/wiki/Ice_Crystaleyezer) | Done | cooling, craftable_items, craftable_structures, dont_starve_together, from_beyond, items, structures |
| [Ice Cube](https://dontstarve.fandom.com/wiki/Ice_Cube) | Done | cooling, craftable_items, dont_starve_together, equipable_items, hats, items, science, science_tier_2 |
| [Ice Fishing Hole](https://dontstarve.fandom.com/wiki/Ice_Fishing_Hole) | Done | dont_starve_together, mob_spawning_entities |
| [Ice Flingomatic](https://dontstarve.fandom.com/wiki/Ice_Flingomatic) | Done | craftable_structures, dont_starve_together, light_sources, science, science_tier_2, structures |
| [Ice Floe](https://dontstarve.fandom.com/wiki/Ice_Floe) | Done | dont_starve_together, from_beyond, ocean |
| [Ice Spike](https://dontstarve.fandom.com/wiki/Ice_Spike) | Done | dont_starve_together |
| [Ice Staff](https://dontstarve.fandom.com/wiki/Ice_Staff) | Done | craftable_items, equipable_items, items, magic_tab, magic_tier_1, ranged_weapons, shadow_magic_filter, weapons |
| [Icker](https://dontstarve.fandom.com/wiki/Icker) | Done | cave_creatures, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Icker Jar](https://dontstarve.fandom.com/wiki/Icker_Jar) | Done | dont_starve_together, from_beyond, items, resources |
| [Icker Preserve](https://dontstarve.fandom.com/wiki/Icker_Preserve) | Done | craftable_items, craftable_structures, dont_starve_together, from_beyond, items, structures |
| [Infernal Staff](https://dontstarve.fandom.com/wiki/Infernal_Staff) | Done | items |
| [Infernal Swineclops](https://dontstarve.fandom.com/wiki/Infernal_Swineclops) | Done | boss_monsters, dont_starve_together, events, mobs |
| [Infused Moon Shard](https://dontstarve.fandom.com/wiki/Infused_Moon_Shard) | Done | boss_dropped_items, craftable_items, dont_starve_together, infobox_missing_crafting_description, items |
| [Ink Blight](https://dontstarve.fandom.com/wiki/Ink_Blight) | Done | cave_creatures, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Insight](https://dontstarve.fandom.com/wiki/Insight) | Done | dont_starve_together, gameplay |
| [Inspectacles](https://dontstarve.fandom.com/wiki/Inspectacles) | Done | clothing_filter, craftable_items, dont_starve_together, items |
| [Insulated Pack](https://dontstarve.fandom.com/wiki/Insulated_Pack) | Done | backpacks, containers, cooking_filter, craftable_items, dont_starve_together, equipable_items, items, science, science_tier_2, survival_tab |
| [Inventory](https://dontstarve.fandom.com/wiki/Inventory) | Done | gameplay |
| [Inviting Formation](https://dontstarve.fandom.com/wiki/Inviting_Formation) | Done | dont_starve_together, mineable_objects |
| [Iridescent Gem](https://dontstarve.fandom.com/wiki/Iridescent_Gem) | Done | a_new_reign, craftable_items, dont_starve_together, infobox_missing_crafting_description, items, resources |
| [Iron Key Gorge](https://dontstarve.fandom.com/wiki/Iron_Key_Gorge) | Done | items |
| [Items](https://dontstarve.fandom.com/wiki/Items) | Done | gameplay |
| [Items Don't Starve Together](https://dontstarve.fandom.com/wiki/Items_Don't_Starve_Together) | Done | dont_starve_together |
| [Jagged Grand Armor](https://dontstarve.fandom.com/wiki/Jagged_Grand_Armor) | Done | items |
| [Jagged Wood Armor](https://dontstarve.fandom.com/wiki/Jagged_Wood_Armor) | Done | items |
| [Jelly Salad](https://dontstarve.fandom.com/wiki/Jelly_Salad) | Done | crock_pot_recipes, dont_starve_together, items |
| [Jellybeans](https://dontstarve.fandom.com/wiki/Jellybeans) | Done | a_new_reign, crock_pot_recipes, dont_starve_together, food, healing, items |
| [Jerky](https://dontstarve.fandom.com/wiki/Jerky) | Done | craftable_items, healing, items |
| [Juicy Berries](https://dontstarve.fandom.com/wiki/Juicy_Berries) | Done | a_new_reign, dont_starve_together, food, fruits, healing, items |
| [Juicy Berry Bush](https://dontstarve.fandom.com/wiki/Juicy_Berry_Bush) | Done | a_new_reign, craftable_items, dont_starve_together, fuel, items, mob_spawning_entities, plants |
| [Junk Pile](https://dontstarve.fandom.com/wiki/Junk_Pile) | Done | dont_starve_together, from_beyond |
| [Junk Yard](https://dontstarve.fandom.com/wiki/Junk_Yard) | Done | dont_starve_together, from_beyond |
| [Junky Fence](https://dontstarve.fandom.com/wiki/Junky_Fence) | Done | dont_starve_together, from_beyond |
| [Kabobs](https://dontstarve.fandom.com/wiki/Kabobs) | Done | craftable_items, crock_pot_recipes, healing, items |
| [Kelp Fronds](https://dontstarve.fandom.com/wiki/Kelp_Fronds) | Done | dont_starve_together, food, health_loss, vegetables |
| [Kelp Patch](https://dontstarve.fandom.com/wiki/Kelp_Patch) | Done | craftable_items, dont_starve_together, from_beyond, fuel, items, seafaring_filter |
| [Key](https://dontstarve.fandom.com/wiki/Key) | Done | dont_starve_together, events, items |
| [King of the Merms](https://dontstarve.fandom.com/wiki/King_of_the_Merms) | Done | dont_starve_together, mobs |
| [Kitschy Idols](https://dontstarve.fandom.com/wiki/Kitschy_Idols) | Done | craftable_items, dont_starve_together, health_loss, items, shadow_magic_filter, survivor_items_filter |
| [Klaus](https://dontstarve.fandom.com/wiki/Klaus) | Done | a_new_reign, boss_monsters, dont_starve_together, events, hostile_creatures, mob_spawning_entities, mobs |
| [Knobbly Tree](https://dontstarve.fandom.com/wiki/Knobbly_Tree) | Done | dont_starve_together, ocean |
| [Knockback](https://dontstarve.fandom.com/wiki/Knockback) | Done | dont_starve_together, gameplay |
| [Koalefant](https://dontstarve.fandom.com/wiki/Koalefant) | Done | animals, mobs, neutral_creatures |
| [Koalefant Carcass](https://dontstarve.fandom.com/wiki/Koalefant_Carcass) | Done | dont_starve_together |
| [Koalefant Trunk](https://dontstarve.fandom.com/wiki/Koalefant_Trunk) | Done | food, healing, items, meats, mob_dropped_items |
| [Krampus](https://dontstarve.fandom.com/wiki/Krampus) | Done | dont_starve_together, mobs, neutral_creatures |
| [Krampus Sack](https://dontstarve.fandom.com/wiki/Krampus_Sack) | Done | backpacks, boss_dropped_items, containers, items, mob_dropped_items |
| [Lake](https://dontstarve.fandom.com/wiki/Lake) | Done | a_new_reign, dont_starve_together |
| [Landscaping Tab](https://dontstarve.fandom.com/wiki/Landscaping_Tab) | Done | dont_starve_together |
| [Lantern](https://dontstarve.fandom.com/wiki/Lantern) | Done | craftable_items, equipable_items, items, light_sources, science, science_tier_2 |
| [Large Casserole Dish](https://dontstarve.fandom.com/wiki/Large_Casserole_Dish) | Done | items |
| [Large Cookpot](https://dontstarve.fandom.com/wiki/Large_Cookpot) | Done | items |
| [Lavae](https://dontstarve.fandom.com/wiki/Lavae) | Done | dont_starve_together, light_sources, mobs |
| [Lavae Egg](https://dontstarve.fandom.com/wiki/Lavae_Egg) | Done | boss_dropped_items, dont_starve_together, items, mob_dropped_items, mob_spawning_entities |
| [Lavae Tooth](https://dontstarve.fandom.com/wiki/Lavae_Tooth) | Done | dont_starve_together, indestructible_object, items |
| [Leafy Meat](https://dontstarve.fandom.com/wiki/Leafy_Meat) | Done | food, healing, meats, mob_dropped_items |
| [Leafy Meatloaf](https://dontstarve.fandom.com/wiki/Leafy_Meatloaf) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, meats |
| [Lesser Glow Berry](https://dontstarve.fandom.com/wiki/Lesser_Glow_Berry) | Done | dont_starve_together, food, fruits, healing, items, light_sources |
| [Lichen](https://dontstarve.fandom.com/wiki/Lichen) | Done | food, healing, items, vegetables |
| [Lichen Meadow](https://dontstarve.fandom.com/wiki/Lichen_Meadow) | Done | dont_starve_together |
| [Life Giving Amulet](https://dontstarve.fandom.com/wiki/Life_Giving_Amulet) | Done | craftable_items, dont_starve_together, equipable_items, healing, items, magic_tab, magic_tier_1, resurrection, shadow_magic_filter |
| [Light Bulb](https://dontstarve.fandom.com/wiki/Light_Bulb) | Done | food, fuel, healing, items, light_sources, mob_dropped_items |
| [Light Flower](https://dontstarve.fandom.com/wiki/Light_Flower) | Done | light_sources, plants |
| [Light Sources Filter](https://dontstarve.fandom.com/wiki/Light_Sources_Filter) | Done | dont_starve_together |
| [Lightning](https://dontstarve.fandom.com/wiki/Lightning) | Done | gameplay, weather |
| [Lightning Conductor](https://dontstarve.fandom.com/wiki/Lightning_Conductor) | Done | craftable_items, dont_starve_together, items, light_sources |
| [Lightning Rod](https://dontstarve.fandom.com/wiki/Lightning_Rod) | Done | craftable_structures, light_sources, science, science_tier_1, structures |
| [Lil' Itchy](https://dontstarve.fandom.com/wiki/Lil'_Itchy) | Done | craftable_items, dont_starve_together, items |
| [Living Log](https://dontstarve.fandom.com/wiki/Living_Log) | Done | boss_dropped_items, craftable_items, fuel, items, mob_dropped_items, resources |
| [Living Staff](https://dontstarve.fandom.com/wiki/Living_Staff) | Done | items |
| [Log](https://dontstarve.fandom.com/wiki/Log) | Done | craftable_items, fuel, infobox_missing_crafting_description, items, resources |
| [Log Suit](https://dontstarve.fandom.com/wiki/Log_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab, fuel, items, science, science_tier_1 |
| [Loot Stash](https://dontstarve.fandom.com/wiki/Loot_Stash) | Done | a_new_reign, dont_starve_together, events, mob_spawning_entities |
| [Lord of the Fruit Flies](https://dontstarve.fandom.com/wiki/Lord_of_the_Fruit_Flies) | Done | boss_monsters, dont_starve_together, mobs |
| [Lost Scrapbook Page](https://dontstarve.fandom.com/wiki/Lost_Scrapbook_Page) | Done | dont_starve_together, from_beyond, fuel, items |
| [Loyal Merm Guard](https://dontstarve.fandom.com/wiki/Loyal_Merm_Guard) | Done | dont_starve_together, followers, hostile_creatures, mobs, nocturnals |
| [Lucky Beast](https://dontstarve.fandom.com/wiki/Lucky_Beast) | Done | craftable_items, dont_starve_together, equipable_items, hats, items |
| [Lucky Gold Nugget](https://dontstarve.fandom.com/wiki/Lucky_Gold_Nugget) | Done | dont_starve_together, items |
| [Lucy the Axe](https://dontstarve.fandom.com/wiki/Lucy_the_Axe) | Done | equipable_items, items, melee_weapons |
| [Lumpy Evergreen](https://dontstarve.fandom.com/wiki/Lumpy_Evergreen) | Done | mob_spawning_entities, plants, resources, trees |
| [Lunar Aligned](https://dontstarve.fandom.com/wiki/Lunar_Aligned) | Done | dont_starve_together, gameplay |
| [Lunar Altars](https://dontstarve.fandom.com/wiki/Lunar_Altars) | Done | crafting_stations, dont_starve_together, structures |
| [Lunar Archipelago](https://dontstarve.fandom.com/wiki/Lunar_Archipelago) | Done | dont_starve_together |
| [Lunar Baths](https://dontstarve.fandom.com/wiki/Lunar_Baths) | Done | dont_starve_together |
| [Lunar Experiment](https://dontstarve.fandom.com/wiki/Lunar_Experiment) | Done | craftable_items, dont_starve_together, events, fuel, items |
| [Lunar Forest](https://dontstarve.fandom.com/wiki/Lunar_Forest) | Done | dont_starve_together |
| [Lunar Funcap](https://dontstarve.fandom.com/wiki/Lunar_Funcap) | Done | celestial_filter, craftable_items, dont_starve_together, equipable_items, from_beyond, hats, items |
| [Lunar Grotto](https://dontstarve.fandom.com/wiki/Lunar_Grotto) | Done | dont_starve_together |
| [Lunar Hail](https://dontstarve.fandom.com/wiki/Lunar_Hail) | Done | dont_starve_together, from_beyond, gameplay |
| [Lunar Island](https://dontstarve.fandom.com/wiki/Lunar_Island) | Done | dont_starve_together, ocean |
| [Lunar Mine](https://dontstarve.fandom.com/wiki/Lunar_Mine) | Done | dont_starve_together |
| [Lunar Mushtree](https://dontstarve.fandom.com/wiki/Lunar_Mushtree) | Done | dont_starve_together, light_sources, plants, trees |
| [Lunar Siphonator](https://dontstarve.fandom.com/wiki/Lunar_Siphonator) | Done | craftable_structures, dont_starve_together, rare_blueprint_exclusive, structures |
| [Lunar Spore](https://dontstarve.fandom.com/wiki/Lunar_Spore) | Done | dont_starve_together |
| [Lunar Wobster](https://dontstarve.fandom.com/wiki/Lunar_Wobster) | Done | dont_starve_together, mobs, ocean |
| [Lune Tree](https://dontstarve.fandom.com/wiki/Lune_Tree) | Done | dont_starve_together, trees |
| [Lune Tree Blossom](https://dontstarve.fandom.com/wiki/Lune_Tree_Blossom) | Done | dont_starve_together, food, healing, items |
| [Lureplant](https://dontstarve.fandom.com/wiki/Lureplant) | Done | mob_spawning_entities, mobs, plants |
| [Lures](https://dontstarve.fandom.com/wiki/Lures) | Done | dont_starve_together |
| [Lurking Nightmare](https://dontstarve.fandom.com/wiki/Lurking_Nightmare) | Done | cave_creatures, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Lush Carpet](https://dontstarve.fandom.com/wiki/Lush_Carpet) | Done | craftable_items, dont_starve_together, items, science_tier_2, turf_items |
| [Luxury Fan](https://dontstarve.fandom.com/wiki/Luxury_Fan) | Done | cooling, craftable_items, dont_starve_together, items, science, science_tier_2, survival_tab |
| [Magician's Chest](https://dontstarve.fandom.com/wiki/Magician's_Chest) | Done | craftable_structures, dont_starve_together, infobox_missing_crafting_description, structures |
| [Magician's Top Hat](https://dontstarve.fandom.com/wiki/Magician's_Top_Hat) | Done | craftable_items, dont_starve_together, infobox_missing_crafting_description, items |
| [Magiluminescence](https://dontstarve.fandom.com/wiki/Magiluminescence) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items, items, light_sources |
| [Magma](https://dontstarve.fandom.com/wiki/Magma) | Done | dont_starve_together, health_loss, indestructible_object, light_sources, mob_spawning_entities |
| [Magma Golem](https://dontstarve.fandom.com/wiki/Magma_Golem) | Done | dont_starve_together, events, followers, mobs |
| [Malbatross](https://dontstarve.fandom.com/wiki/Malbatross) | Done | birds, boss_monsters, dont_starve_together, flying_creatures, mobs, neutral_creatures, ocean |
| [Malbatross Bill](https://dontstarve.fandom.com/wiki/Malbatross_Bill) | Done | boss_dropped_items, dont_starve_together, equipable_items, items, mob_dropped_items |
| [Malbatross Feather](https://dontstarve.fandom.com/wiki/Malbatross_Feather) | Done | boss_dropped_items, dont_starve_together, fuel, items, mob_dropped_items, resources |
| [Mandrake](https://dontstarve.fandom.com/wiki/Mandrake) | Done | followers, food, healing, items, mob_dropped_items, mobs, nocturnals, passive_creatures, plants |
| [Mandrake Soup](https://dontstarve.fandom.com/wiki/Mandrake_Soup) | Done | craftable_items, crock_pot_recipes, food, healing, items |
| [Mannequin](https://dontstarve.fandom.com/wiki/Mannequin) | Done | craftable_structures, dont_starve_together, science_tier_1, structures |
| [Manure](https://dontstarve.fandom.com/wiki/Manure) | Done | craftable_items, fertilizer, fuel, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Map](https://dontstarve.fandom.com/wiki/Map) | Done | gameplay |
| [Map Scroll](https://dontstarve.fandom.com/wiki/Map_Scroll) | Done | a_new_reign, craftable_items, dont_starve_together, items |
| [Marble](https://dontstarve.fandom.com/wiki/Marble) | Done | craftable_items, infobox_missing_crafting_description, items, resources |
| [Marble Bean](https://dontstarve.fandom.com/wiki/Marble_Bean) | Done | a_new_reign, craftable_items, dont_starve_together, items, refine_tab, science_tier_2 |
| [Marble Pillar](https://dontstarve.fandom.com/wiki/Marble_Pillar) | Done | mineable_objects, resources, structures |
| [Marble Sculptures](https://dontstarve.fandom.com/wiki/Marble_Sculptures) | Done | a_new_reign, dont_starve_together, mineable_objects, mob_spawning_entities, structures |
| [Marble Shrub](https://dontstarve.fandom.com/wiki/Marble_Shrub) | Done | a_new_reign, dont_starve_together, mineable_objects, plants |
| [Marble Statues](https://dontstarve.fandom.com/wiki/Marble_Statues) | Done | a_new_reign, dont_starve_together, mineable_objects |
| [Marble Suit](https://dontstarve.fandom.com/wiki/Marble_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab, items, science, science_tier_2 |
| [Marble Tree](https://dontstarve.fandom.com/wiki/Marble_Tree) | Done | mineable_objects, resources, structures |
| [Marotter](https://dontstarve.fandom.com/wiki/Marotter) | Done | dont_starve_together, from_beyond, mobs |
| [Marotter Den](https://dontstarve.fandom.com/wiki/Marotter_Den) | Done | dont_starve_together, from_beyond, mob_housing, mob_spawning_entities |
| [Marsh Turf](https://dontstarve.fandom.com/wiki/Marsh_Turf) | Done | craftable_items, fuel, items, survivor_items_filter, turf_items |
| [Mast](https://dontstarve.fandom.com/wiki/Mast) | Done | craftable_items, dont_starve_together, items, seafaring_filter, structures |
| [Maxwell Statue](https://dontstarve.fandom.com/wiki/Maxwell_Statue) | Done | dont_starve_together, mineable_objects, mob_spawning_entities, resources, structures |
| [Mealing Stone](https://dontstarve.fandom.com/wiki/Mealing_Stone) | Done | dont_starve_together, events, indestructible_object, structures |
| [Meat](https://dontstarve.fandom.com/wiki/Meat) | Done | boss_dropped_items, food, healing, items, meats, mob_dropped_items |
| [Meat Effigy](https://dontstarve.fandom.com/wiki/Meat_Effigy) | Done | craftable_structures, health_loss, magic_tab, magic_tier_1, resurrection, shadow_magic_filter, structures |
| [Meatballs](https://dontstarve.fandom.com/wiki/Meatballs) | Done | crock_pot_recipes, food, healing, items, meats |
| [Meaty Stew](https://dontstarve.fandom.com/wiki/Meaty_Stew) | Done | craftable_items, crock_pot_recipes, healing, items |
| [Melonsicle](https://dontstarve.fandom.com/wiki/Melonsicle) | Done | cooling, crock_pot_recipes, dont_starve_together, food, fruits, healing, items, vegetables |
| [Merm](https://dontstarve.fandom.com/wiki/Merm) | Done | followers, hostile_creatures, mobs, nocturnals |
| [Merm Flort-ifications](https://dontstarve.fandom.com/wiki/Merm_Flort-ifications) | Done | craftable_structures, dont_starve_together, mob_housing, science_tier_2, structures, survivor_items_filter |
| [Merm Head](https://dontstarve.fandom.com/wiki/Merm_Head) | Done | structures |
| [Mermhouse](https://dontstarve.fandom.com/wiki/Mermhouse) | Done | mob_housing, mob_spawning_entities, structures |
| [Message in a Bottle](https://dontstarve.fandom.com/wiki/Message_in_a_Bottle) | Done | dont_starve_together, items |
| [Meteor](https://dontstarve.fandom.com/wiki/Meteor) | Done | dont_starve_together, health_loss, resources |
| [Miasma](https://dontstarve.fandom.com/wiki/Miasma) | Done | dont_starve_together, from_beyond |
| [Midsummer Cawnival](https://dontstarve.fandom.com/wiki/Midsummer_Cawnival) | Done | dont_starve_together, events |
| [Prize Booth](https://dontstarve.fandom.com/wiki/Midsummer_Cawnival/Prize_Booth) | Done | events |
| [Mighty Gym](https://dontstarve.fandom.com/wiki/Mighty_Gym) | Done | craftable_structures, dont_starve_together, science_tier_1, structures |
| [Milkmade Hat](https://dontstarve.fandom.com/wiki/Milkmade_Hat) | Done | crock_pot_recipes, dont_starve_together, equipable_items, food, items |
| [Milky Whites](https://dontstarve.fandom.com/wiki/Milky_Whites) | Done | boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Mimicreep](https://dontstarve.fandom.com/wiki/Mimicreep) | Done | cave_creatures, dont_starve_together, from_beyond, mobs, passive_creatures |
| [Miner Hat](https://dontstarve.fandom.com/wiki/Miner_Hat) | Done | craftable_items, equipable_items, hats, items, light_sources, science, science_tier_2 |
| [Mini Glacier](https://dontstarve.fandom.com/wiki/Mini_Glacier) | Done | dont_starve_together, mineable_objects |
| [Mini Sign](https://dontstarve.fandom.com/wiki/Mini_Sign) | Done | a_new_reign, craftable_items, craftable_structures, decorations_filter, fuel, items, science_tier_1, structures |
| [Misshapen Bird](https://dontstarve.fandom.com/wiki/Misshapen_Bird) | Done | birds, dont_starve_together, hostile_creatures, items, mobs, monsters |
| [Mods](https://dontstarve.fandom.com/wiki/Mods) | Done | gameplay |
| [Moggles](https://dontstarve.fandom.com/wiki/Moggles) | Done | craftable_items, dont_starve_together, equipable_items, hats, items, light_sources, science, science_tier_2 |
| [Moleworm](https://dontstarve.fandom.com/wiki/Moleworm) | Done | animals, cave_creatures, dont_starve_together, innocents, items, mobs, passive_creatures |
| [Molten Darts](https://dontstarve.fandom.com/wiki/Molten_Darts) | Done | items |
| [Monkey Hut](https://dontstarve.fandom.com/wiki/Monkey_Hut) | Done | dont_starve_together |
| [Monkeytails](https://dontstarve.fandom.com/wiki/Monkeytails) | Done | dont_starve_together, plants, resources |
| [Monster Jerky](https://dontstarve.fandom.com/wiki/Monster_Jerky) | Done | craftable_items, food, health_loss, items, monster_foods |
| [Monster Lasagna](https://dontstarve.fandom.com/wiki/Monster_Lasagna) | Done | crock_pot_recipes, health_loss, items, monster_foods |
| [Monster Meat](https://dontstarve.fandom.com/wiki/Monster_Meat) | Done | boss_dropped_items, food, health_loss, items, mob_dropped_items, monster_foods |
| [Monster Tartare](https://dontstarve.fandom.com/wiki/Monster_Tartare) | Done | dont_starve_together, food, healing, items, monster_foods |
| [Moon Caller's Staff](https://dontstarve.fandom.com/wiki/Moon_Caller's_Staff) | Done | a_new_reign, cooling, dont_starve_together, equipable_items, items, light_sources |
| [Moon Crater Turf](https://dontstarve.fandom.com/wiki/Moon_Crater_Turf) | Done | celestial_tab, craftable_items, dont_starve_together, fuel, items, turf_items |
| [Moon Cycle](https://dontstarve.fandom.com/wiki/Moon_Cycle) | Done | gameplay |
| [Moon Dial](https://dontstarve.fandom.com/wiki/Moon_Dial) | Done | a_new_reign, craftable_structures, dont_starve_together, light_sources, magic_tab, magic_tier_1, shadow_magic_filter, structures |
| [Moon Glass](https://dontstarve.fandom.com/wiki/Moon_Glass) | Done | dont_starve_together, mineable_objects, resources |
| [Moon Glass Mound](https://dontstarve.fandom.com/wiki/Moon_Glass_Mound) | Done | dont_starve_together, ocean |
| [Moon Glass Saw Blade](https://dontstarve.fandom.com/wiki/Moon_Glass_Saw_Blade) | Done | celestial_filter, craftable_items, dont_starve_together, from_beyond, items |
| [Moon Moth](https://dontstarve.fandom.com/wiki/Moon_Moth) | Done | dont_starve_together, items, mob_dropped_items, mobs, passive_creatures |
| [Moon Moth Wings](https://dontstarve.fandom.com/wiki/Moon_Moth_Wings) | Done | dont_starve_together, healing, items |
| [Moon Quay](https://dontstarve.fandom.com/wiki/Moon_Quay) | Done | dont_starve_together, ocean |
| [Moon Quay Beach Turf](https://dontstarve.fandom.com/wiki/Moon_Quay_Beach_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, items, rare_blueprint_exclusive, turf_items |
| [Moon Quay Pirate Banner](https://dontstarve.fandom.com/wiki/Moon_Quay_Pirate_Banner) | Done | craftable_structures, decorations_filter, dont_starve_together, rare_blueprint_exclusive, structures |
| [Moon Rock](https://dontstarve.fandom.com/wiki/Moon_Rock) | Done | a_new_reign, boss_dropped_items, craftable_items, dont_starve_together, infobox_missing_crafting_description, items, resources |
| [Moon Rock Idol](https://dontstarve.fandom.com/wiki/Moon_Rock_Idol) | Done | celestial_tab, craftable_items, dont_starve_together, items |
| [Moon Rock Wall](https://dontstarve.fandom.com/wiki/Moon_Rock_Wall) | Done | craftable_items, dont_starve_together, items, science_tier_2 |
| [Moon Shard](https://dontstarve.fandom.com/wiki/Moon_Shard) | Done | boss_dropped_items, dont_starve_together, items |
| [Moon Shroom](https://dontstarve.fandom.com/wiki/Moon_Shroom) | Done | dont_starve_together, food, items |
| [Moon Stone](https://dontstarve.fandom.com/wiki/Moon_Stone) | Done | a_new_reign, dont_starve_together, indestructible_object, mineable_objects, mob_spawning_entities |
| [Moonblind Crow](https://dontstarve.fandom.com/wiki/Moonblind_Crow) | Done | dont_starve_together, items, mobs |
| [Moongleam](https://dontstarve.fandom.com/wiki/Moongleam) | Done | dont_starve_together, items |
| [Moonlens](https://dontstarve.fandom.com/wiki/Moonlens) | Done | a_new_reign, craftable_items, dont_starve_together, infobox_missing_crafting_description, items |
| [Moonrock Pengull](https://dontstarve.fandom.com/wiki/Moonrock_Pengull) | Done | dont_starve_together, hostile_creatures, innocents, mobs |
| [Moonstorm](https://dontstarve.fandom.com/wiki/Moonstorm) | Done | dont_starve_together, gameplay |
| [Goose](https://dontstarve.fandom.com/wiki/Moose/Goose) | Done | birds, boss_monsters, dont_starve_together, hostile_creatures, mobs, monsters |
| [Goose Egg](https://dontstarve.fandom.com/wiki/Moose/Goose_Egg) | Done | dont_starve_together, eggs, mob_housing, mob_spawning_entities |
| [Moqueca](https://dontstarve.fandom.com/wiki/Moqueca) | Done | dont_starve_together, healing, items |
| [Morning Star](https://dontstarve.fandom.com/wiki/Morning_Star) | Done | craftable_items, dont_starve_together, equipable_items, fight_tab, items, light_sources, melee_weapons, science, science_tier_2, weapons |
| [Morsel](https://dontstarve.fandom.com/wiki/Morsel) | Done | food, healing, items, meats, mob_dropped_items |
| [Mosaic Flooring](https://dontstarve.fandom.com/wiki/Mosaic_Flooring) | Done | craftable_items, dont_starve_together, items, science_tier_2, turf_items |
| [Mosling](https://dontstarve.fandom.com/wiki/Mosling) | Done | animals, birds, dont_starve_together, innocents, mob_spawning_entities, mobs |
| [Mosquito](https://dontstarve.fandom.com/wiki/Mosquito) | Done | animals, flying_creatures, hostile_creatures, items, mob_dropped_items, mobs, nocturnals |
| [Mosquito Sack](https://dontstarve.fandom.com/wiki/Mosquito_Sack) | Done | healing, items, mob_dropped_items |
| [Mossy Vine](https://dontstarve.fandom.com/wiki/Mossy_Vine) | Done | dont_starve_together |
| [Mourning Glory](https://dontstarve.fandom.com/wiki/Mourning_Glory) | Done | dont_starve_together, items, mob_dropped_items |
| [Mud Biome](https://dontstarve.fandom.com/wiki/Mud_Biome) | Done | dont_starve_together |
| [Mud Turf](https://dontstarve.fandom.com/wiki/Mud_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Mumsy](https://dontstarve.fandom.com/wiki/Mumsy) | Done | dont_starve_together, events, mobs |
| [Mush Gnome](https://dontstarve.fandom.com/wiki/Mush_Gnome) | Done | cave_creatures, dont_starve_together, light_sources, mobs, monsters, neutral_creatures, passive_creatures |
| [Mushroom Lights](https://dontstarve.fandom.com/wiki/Mushroom_Lights) | Done | dont_starve_together |
| [Mushroom Planter](https://dontstarve.fandom.com/wiki/Mushroom_Planter) | Done | a_new_reign, craftable_structures, dont_starve_together, food_gardening_filter, food_tab, science_tier_1, structures |
| [Mushroom Spore](https://dontstarve.fandom.com/wiki/Mushroom_Spore) | Done | a_new_reign, dont_starve_together, items, light_sources |
| [Mushrooms](https://dontstarve.fandom.com/wiki/Mushrooms) | Done | boss_dropped_items, healing, health_loss, mob_dropped_items, vegetables |
| [Mushtree](https://dontstarve.fandom.com/wiki/Mushtree) | Done | dont_starve_together, light_sources, mob_spawning_entities, plants, resources, trees |
| [Mushy Cake](https://dontstarve.fandom.com/wiki/Mushy_Cake) | Done | crock_pot_recipes, dont_starve_together, food, items, vegetables |
| [Mutated Fungal Turf](https://dontstarve.fandom.com/wiki/Mutated_Fungal_Turf) | Done | celestial_tab, craftable_items, dont_starve_together, items, turf_items |
| [Mutated Merm](https://dontstarve.fandom.com/wiki/Mutated_Merm) | Done | dont_starve_together, followers, hostile_creatures, mobs, nocturnals |
| [Mysterious Energy](https://dontstarve.fandom.com/wiki/Mysterious_Energy) | Done | dont_starve_together |
| [Mysterious Plant](https://dontstarve.fandom.com/wiki/Mysterious_Plant) | Done | dont_starve_together |
| [Naked Mole Bat](https://dontstarve.fandom.com/wiki/Naked_Mole_Bat) | Done | cave_creatures, dont_starve_together, hostile_creatures, mobs, monsters |
| [Naked Mole Bat Burrow](https://dontstarve.fandom.com/wiki/Naked_Mole_Bat_Burrow) | Done | dont_starve_together |
| [Naked Nostrils](https://dontstarve.fandom.com/wiki/Naked_Nostrils) | Done | dont_starve_together, food, items, mob_dropped_items |
| [Napsack](https://dontstarve.fandom.com/wiki/Napsack) | Done | a_new_reign, craftable_items, dont_starve_together, equipable_items, items, rare_blueprint_exclusive |
| [Nautopilot](https://dontstarve.fandom.com/wiki/Nautopilot) | Done | craftable_items, craftable_structures, dont_starve_together, items, seafaring_filter, structures |
| [Night Armor](https://dontstarve.fandom.com/wiki/Night_Armor) | Done | armour_filter, boss_dropped_items, craftable_items, equipable_items, items, magic_tab, magic_tier_2, mob_dropped_items, shadow_magic_filter |
| [Night Hand](https://dontstarve.fandom.com/wiki/Night_Hand) | Done | mobs |
| [Night Light](https://dontstarve.fandom.com/wiki/Night_Light) | Done | craftable_structures, light_sources, magic_tab, magic_tier_1, shadow_magic_filter, structures |
| [Nightberry](https://dontstarve.fandom.com/wiki/Nightberry) | Done | dont_starve_together, food, from_beyond, health_loss, items |
| [Nightmare Amulet](https://dontstarve.fandom.com/wiki/Nightmare_Amulet) | Done | craftable_items, equipable_items, items, magic_tab, magic_tier_2, shadow_magic_filter |
| [Nightmare Cycle](https://dontstarve.fandom.com/wiki/Nightmare_Cycle) | Done | gameplay |
| [Nightmare Fuel](https://dontstarve.fandom.com/wiki/Nightmare_Fuel) | Done | boss_dropped_items, craftable_items, fuel, items, magic_tier_1, mob_dropped_items, refine_tab, resources, shadow_magic_filter |
| [Nightmare Light](https://dontstarve.fandom.com/wiki/Nightmare_Light) | Done | dont_starve_together, indestructible_object, light_sources, mob_spawning_entities, nightmare_state_indicator |
| [Nightmare Saddle](https://dontstarve.fandom.com/wiki/Nightmare_Saddle) | Done | craftable_items, dont_starve_together, from_beyond, items |
| [Nightmare Werepig](https://dontstarve.fandom.com/wiki/Nightmare_Werepig) | Done | boss_monsters, dont_starve_together, mobs, monsters |
| [Nitre](https://dontstarve.fandom.com/wiki/Nitre) | Done | craftable_items, fuel, infobox_missing_crafting_description, items, resources |
| [Nitre Formation](https://dontstarve.fandom.com/wiki/Nitre_Formation) | Done | dont_starve_together, from_beyond, mineable_objects, resources |
| [No-Eyed Deer](https://dontstarve.fandom.com/wiki/No-Eyed_Deer) | Done | a_new_reign, animals, dont_starve_together, mob_spawning_entities, mobs, passive_creatures |
| [Non-renewable resources](https://dontstarve.fandom.com/wiki/Non-renewable_resources) | Done | gameplay |
| [Nox Helm](https://dontstarve.fandom.com/wiki/Nox_Helm) | Done | items |
| [Nurse Spider](https://dontstarve.fandom.com/wiki/Nurse_Spider) | Done | dont_starve_together, followers, mobs, spiders |
| [Nutrient](https://dontstarve.fandom.com/wiki/Nutrient) | Done | dont_starve_together, gameplay |
| [Oar](https://dontstarve.fandom.com/wiki/Oar) | Done | craftable_items, dont_starve_together, equipable_items, fuel, items |
| [Obelisk](https://dontstarve.fandom.com/wiki/Obelisk) | Done | indestructible_object, structures |
| [Ocean](https://dontstarve.fandom.com/wiki/Ocean) | Done | gameplay, mob_spawning_entities, ocean |
| [Ocean Debris](https://dontstarve.fandom.com/wiki/Ocean_Debris) | Done | dont_starve_together, ocean |
| [Ocean Fishes](https://dontstarve.fandom.com/wiki/Ocean_Fishes) | Done | dont_starve_together |
| [Ocean Trawler Kit](https://dontstarve.fandom.com/wiki/Ocean_Trawler_Kit) | Done | craftable_items, dont_starve_together, food_gardening_filter, items, structures |
| [Ocuvigil](https://dontstarve.fandom.com/wiki/Ocuvigil) | Done | a_new_reign, craftable_structures, dont_starve_together, magic_tab, magic_tier_1, shadow_magic_filter, structures, tools_filter |
| [Offerings Filter](https://dontstarve.fandom.com/wiki/Offerings_Filter) | Done | dont_starve_together |
| [Old Beefalo](https://dontstarve.fandom.com/wiki/Old_Beefalo) | Done | dont_starve_together, events, mobs, passive_creatures |
| [One-man Band](https://dontstarve.fandom.com/wiki/One-man_Band) | Done | craftable_items, equipable_items, food_gardening_filter, items, magic_tab, magic_tier_1, shadow_magic_filter |
| [Onion](https://dontstarve.fandom.com/wiki/Onion) | Done | dont_starve_together, events, food, healing, vegetables |
| [Orange Gem](https://dontstarve.fandom.com/wiki/Orange_Gem) | Done | boss_dropped_items, craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Ornate Chest](https://dontstarve.fandom.com/wiki/Ornate_Chest) | Done | boss_dropped_items, containers, mob_spawning_entities, structures |
| [Ornery Chest](https://dontstarve.fandom.com/wiki/Ornery_Chest) | Done | dont_starve_together, mobs |
| [Overheating](https://dontstarve.fandom.com/wiki/Overheating) | Done | dont_starve_together, gameplay, health_loss |
| [Packet of Seeds](https://dontstarve.fandom.com/wiki/Packet_of_Seeds) | Done | dont_starve_together, events, items |
| [Palmcone Scale](https://dontstarve.fandom.com/wiki/Palmcone_Scale) | Done | dont_starve_together, items |
| [Palmcone Sprout](https://dontstarve.fandom.com/wiki/Palmcone_Sprout) | Done | dont_starve_together, items |
| [Palmcone Tree](https://dontstarve.fandom.com/wiki/Palmcone_Tree) | Done | dont_starve_together, trees |
| [Pan Flute](https://dontstarve.fandom.com/wiki/Pan_Flute) | Done | craftable_items, items, magic_tab, magic_tier_1, shadow_magic_filter |
| [Papyrus](https://dontstarve.fandom.com/wiki/Papyrus) | Done | craftable_items, fuel, items, refine_tab, science, science_tier_1 |
| [Parasitic Shadeling](https://dontstarve.fandom.com/wiki/Parasitic_Shadeling) | Done | dont_starve_together, mobs |
| [Parrot Pirate](https://dontstarve.fandom.com/wiki/Parrot_Pirate) | Done | animals, birds, flying_creatures, items |
| [Pearl's Pearl](https://dontstarve.fandom.com/wiki/Pearl's_Pearl) | Done | boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Pebble Crab](https://dontstarve.fandom.com/wiki/Pebble_Crab) | Done | dont_starve_together, events, items, mob_dropped_items, mobs, passive_creatures |
| [Pengull](https://dontstarve.fandom.com/wiki/Pengull) | Done | animals, birds, innocents, mobs, neutral_creatures |
| [Pepper](https://dontstarve.fandom.com/wiki/Pepper) | Done | dont_starve_together, food, health_loss, vegetables |
| [Petals](https://dontstarve.fandom.com/wiki/Petals) | Done | a_new_reign, dont_starve_together, fuel, healing, items, resources, vegetables |
| [Petrified Tree](https://dontstarve.fandom.com/wiki/Petrified_Tree) | Done | a_new_reign, dont_starve_together, structures, trees |
| [Petrifying Tome](https://dontstarve.fandom.com/wiki/Petrifying_Tome) | Done | items |
| [Phasmo-Encapsulator](https://dontstarve.fandom.com/wiki/Phasmo-Encapsulator) | Done | craftable_items, items, tools_filter |
| [Phlegm](https://dontstarve.fandom.com/wiki/Phlegm) | Done | a_new_reign, dont_starve_together, food, items, mob_dropped_items |
| [Phobic Experiment](https://dontstarve.fandom.com/wiki/Phobic_Experiment) | Done | craftable_items, dont_starve_together, events, fuel, items |
| [Axe](https://dontstarve.fandom.com/wiki/Pick/Axe) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items, items |
| [Pickaxe](https://dontstarve.fandom.com/wiki/Pickaxe) | Done | craftable_items, equipable_items, items, science_tier_2, tools_filter, tools_tab |
| [Pierogi](https://dontstarve.fandom.com/wiki/Pierogi) | Done | crock_pot_recipes, food, healing, items |
| [Pig](https://dontstarve.fandom.com/wiki/Pig) | Done | animals, followers, innocents, mobs, neutral_creatures |
| [Pig Head](https://dontstarve.fandom.com/wiki/Pig_Head) | Done | structures |
| [Pig House](https://dontstarve.fandom.com/wiki/Pig_House) | Done | craftable_structures, mob_housing, mob_spawning_entities, science, science_tier_2, structures |
| [Pig King](https://dontstarve.fandom.com/wiki/Pig_King) | Done | indestructible_object |
| [Pig Skin](https://dontstarve.fandom.com/wiki/Pig_Skin) | Done | items, meats, mob_dropped_items, resources |
| [Pig Torch](https://dontstarve.fandom.com/wiki/Pig_Torch) | Done | light_sources, mob_spawning_entities, structures |
| [Pig Village](https://dontstarve.fandom.com/wiki/Pig_Village) | Done | gameplay |
| [Piggyback](https://dontstarve.fandom.com/wiki/Piggyback) | Done | backpacks, clothing_filter, containers, craftable_items, equipable_items, items, science_tier_2, survival_tab |
| [Pile o' Balloons](https://dontstarve.fandom.com/wiki/Pile_o'_Balloons) | Done | craftable_items, hats, items, survival_tab, tools_filter |
| [Pillars](https://dontstarve.fandom.com/wiki/Pillars) | Done | a_new_reign, dont_starve_together, indestructible_object, nightmare_state_indicator, structures |
| [Pinchin' Winch](https://dontstarve.fandom.com/wiki/Pinchin'_Winch) | Done | craftable_structures, dont_starve_together, rare_blueprint_exclusive, seafaring_filter, structures |
| [Pine Cone](https://dontstarve.fandom.com/wiki/Pine_Cone) | Done | fuel, items, plants, trees |
| [Pinetree Pioneer Hat](https://dontstarve.fandom.com/wiki/Pinetree_Pioneer_Hat) | Done | craftable_items, dont_starve_together, equipable_items, hats, items |
| [Pipspook](https://dontstarve.fandom.com/wiki/Pipspook) | Done | dont_starve_together, followers, mobs, passive_creatures |
| [Pipton](https://dontstarve.fandom.com/wiki/Pipton) | Done | dont_starve_together, events, mobs |
| [Pirate's Bandana](https://dontstarve.fandom.com/wiki/Pirate's_Bandana) | Done | dont_starve_together, items, mob_dropped_items |
| [Pirate Map](https://dontstarve.fandom.com/wiki/Pirate_Map) | Done | dont_starve_together, items |
| [Pirate Raid](https://dontstarve.fandom.com/wiki/Pirate_Raid) | Done | dont_starve_together, gameplay |
| [Pirate Sloop](https://dontstarve.fandom.com/wiki/Pirate_Sloop) | Done | dont_starve_together, structures |
| [Pit Pig](https://dontstarve.fandom.com/wiki/Pit_Pig) | Done | dont_starve_together, events, hostile_creatures, mobs |
| [Pitchfork](https://dontstarve.fandom.com/wiki/Pitchfork) | Done | craftable_items, dont_starve_together, equipable_items, items, science, science_tier_1, science_tier_2, tools_filter, tools_tab |
| [Pith Pike](https://dontstarve.fandom.com/wiki/Pith_Pike) | Done | items |
| [Plain Omelette](https://dontstarve.fandom.com/wiki/Plain_Omelette) | Done | crock_pot_recipes, dont_starve_together, eggs, food, healing, items |
| [Planar Entity Protection](https://dontstarve.fandom.com/wiki/Planar_Entity_Protection) | Done | dont_starve_together, from_beyond, gameplay |
| [Pleasant Portrait](https://dontstarve.fandom.com/wiki/Pleasant_Portrait) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items |
| [Plugged Fissure](https://dontstarve.fandom.com/wiki/Plugged_Fissure) | Done | dont_starve_together |
| [Pocket Scale](https://dontstarve.fandom.com/wiki/Pocket_Scale) | Done | craftable_items, dont_starve_together, equipable_items, items, science_tier_1, tools_filter |
| [Polar Bearger Bin](https://dontstarve.fandom.com/wiki/Polar_Bearger_Bin) | Done | containers, craftable_items, dont_starve_together, from_beyond, items |
| [Polly Roger's Hat](https://dontstarve.fandom.com/wiki/Polly_Roger's_Hat) | Done | craftable_items, dont_starve_together, items, mobs, rare_blueprint_exclusive |
| [Pomegranate](https://dontstarve.fandom.com/wiki/Pomegranate) | Done | food, healing, items |
| [Pond](https://dontstarve.fandom.com/wiki/Pond) | Done | indestructible_object, mob_housing, mob_spawning_entities |
| [Portable Crock Pot](https://dontstarve.fandom.com/wiki/Portable_Crock_Pot) | Done | containers, cooking_filter, craftable_items, dont_starve_together, food_tab, items, survivor_items_filter |
| [Portable Grinding Mill](https://dontstarve.fandom.com/wiki/Portable_Grinding_Mill) | Done | cooking_filter, craftable_items, crafting_stations, dont_starve_together, food_tab, items, survivor_items_filter |
| [Portable Seasoning Station](https://dontstarve.fandom.com/wiki/Portable_Seasoning_Station) | Done | cooking_filter, craftable_items, dont_starve_together, items |
| [Portal Paraphernalia](https://dontstarve.fandom.com/wiki/Portal_Paraphernalia) | Done | celestial_filter, craftable_items, dont_starve_together, items |
| [Portasol](https://dontstarve.fandom.com/wiki/Portasol) | Done | clothing_filter, craftable_items, dont_starve_together, items |
| [Portrait Frames](https://dontstarve.fandom.com/wiki/Portrait_Frames) | Done | dont_starve_together |
| [Possessed Varg](https://dontstarve.fandom.com/wiki/Possessed_Varg) | Done | boss_monsters, dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Potato](https://dontstarve.fandom.com/wiki/Potato) | Done | dont_starve_together, events, food, healing, health_loss, vegetables |
| [Potato Sack](https://dontstarve.fandom.com/wiki/Potato_Sack) | Done | dont_starve_together |
| [Potted Fern](https://dontstarve.fandom.com/wiki/Potted_Fern) | Done | craftable_structures, decorations_filter, science, science_tier_2, structures |
| [Potted Succulent](https://dontstarve.fandom.com/wiki/Potted_Succulent) | Done | a_new_reign, craftable_structures, decorations_filter, dont_starve_together, science_tier_2, structures |
| [Potter's Wheel](https://dontstarve.fandom.com/wiki/Potter's_Wheel) | Done | a_new_reign, craftable_structures, crafting_stations, decorations_filter, dont_starve_together, science_tier_1, structures |
| [Powder Monkey](https://dontstarve.fandom.com/wiki/Powder_Monkey) | Done | animals, dont_starve_together, hostile_creatures, mobs, neutral_creatures |
| [Powdercake](https://dontstarve.fandom.com/wiki/Powdercake) | Done | crock_pot_recipes, health_loss, items, vegetables |
| [Prestihatitator](https://dontstarve.fandom.com/wiki/Prestihatitator) | Done | craftable_structures, magic_tab, mob_spawning_entities, science_tier_1, shadow_magic_filter, structures |
| [Pretty Parasol](https://dontstarve.fandom.com/wiki/Pretty_Parasol) | Done | craftable_items, equipable_items, fuel, items, science, survival_tab |
| [Prime Mate](https://dontstarve.fandom.com/wiki/Prime_Mate) | Done | dont_starve_together, mobs |
| [Produce Scale](https://dontstarve.fandom.com/wiki/Produce_Scale) | Done | craftable_structures, decorations_filter, dont_starve_together, food_gardening_filter, science_tier_2, structures |
| [Profile Icons](https://dontstarve.fandom.com/wiki/Profile_Icons) | Done | dont_starve_together |
| [Prototypers & Stations Filter](https://dontstarve.fandom.com/wiki/Prototypers_%26_Stations_Filter) | Done | dont_starve_together |
| [Psychosis Experiment](https://dontstarve.fandom.com/wiki/Psychosis_Experiment) | Done | craftable_items, dont_starve_together, events, fuel, items |
| [Puffed Potato Soufflé](https://dontstarve.fandom.com/wiki/Puffed_Potato_Souffl%C3%A9) | Done | dont_starve_together, healing, items |
| [Puffy Vest](https://dontstarve.fandom.com/wiki/Puffy_Vest) | Done | craftable_items, equipable_items, items, science, science_tier_2 |
| [Pumpkin](https://dontstarve.fandom.com/wiki/Pumpkin) | Done | food, healing, vegetables |
| [Pumpkin Cookies](https://dontstarve.fandom.com/wiki/Pumpkin_Cookies) | Done | crock_pot_recipes, food, items, vegetables |
| [Pumpkin Lantern](https://dontstarve.fandom.com/wiki/Pumpkin_Lantern) | Done | craftable_items, items, light_sources, science, science_tier_2 |
| [Punching Bag](https://dontstarve.fandom.com/wiki/Punching_Bag) | Done | craftable_structures, from_beyond, magic_tier_1, science_tier_1, shadow_magic_filter, structures |
| [Pure Brilliance](https://dontstarve.fandom.com/wiki/Pure_Brilliance) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items, resources |
| [Pure Horror](https://dontstarve.fandom.com/wiki/Pure_Horror) | Done | boss_dropped_items, craftable_items, dont_starve_together, fuel, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Purple Gem](https://dontstarve.fandom.com/wiki/Purple_Gem) | Done | boss_dropped_items, craftable_items, items, magic_tier_1, mob_dropped_items, refine_tab, resources, shadow_magic_filter |
| [Quagmire Firepit](https://dontstarve.fandom.com/wiki/Quagmire_Firepit) | Done | structures |
| [Queen of Moon Quay](https://dontstarve.fandom.com/wiki/Queen_of_Moon_Quay) | Done | dont_starve_together, structures |
| [Rabbit](https://dontstarve.fandom.com/wiki/Rabbit) | Done | animals, innocents, items, mob_dropped_items, mobs, passive_creatures |
| [Rabbit Earmuffs](https://dontstarve.fandom.com/wiki/Rabbit_Earmuffs) | Done | craftable_items, equipable_items, hats, items, science, science_tier_1 |
| [Rabbit Hole](https://dontstarve.fandom.com/wiki/Rabbit_Hole) | Done | mob_housing, mob_spawning_entities |
| [Rabbit Hutch](https://dontstarve.fandom.com/wiki/Rabbit_Hutch) | Done | craftable_structures, mob_housing, mob_spawning_entities, science, science_tier_2, structures |
| [Rabbit King Cudgel](https://dontstarve.fandom.com/wiki/Rabbit_King_Cudgel) | Done | dont_starve_together, from_beyond, items, mob_dropped_items, weapons |
| [Rain](https://dontstarve.fandom.com/wiki/Rain) | Done | gameplay, weather |
| [Rain Coat](https://dontstarve.fandom.com/wiki/Rain_Coat) | Done | craftable_items, dont_starve_together, equipable_items, items, science, science_tier_1 |
| [Rain Gear Filter](https://dontstarve.fandom.com/wiki/Rain_Gear_Filter) | Done | dont_starve_together |
| [Rain Hat](https://dontstarve.fandom.com/wiki/Rain_Hat) | Done | craftable_items, dont_starve_together, equipable_items, hats, items, science, science_tier_2 |
| [Rainometer](https://dontstarve.fandom.com/wiki/Rainometer) | Done | craftable_structures, science, science_tier_1, structures, weather |
| [Ratatouille](https://dontstarve.fandom.com/wiki/Ratatouille) | Done | crock_pot_recipes, healing, items |
| [Raw Fish](https://dontstarve.fandom.com/wiki/Raw_Fish) | Done | boss_dropped_items, dont_starve_together, fishes, food, healing, items, meats, mob_dropped_items |
| [Razor](https://dontstarve.fandom.com/wiki/Razor) | Done | craftable_items, items, science, science_tier_1, tools_filter, tools_tab |
| [Reanimated Skeleton](https://dontstarve.fandom.com/wiki/Reanimated_Skeleton) | Done | a_new_reign, boss_monsters, cave_creatures, dont_starve_together, hostile_creatures, mob_spawning_entities, mobs, passive_creatures |
| [Recipe Card](https://dontstarve.fandom.com/wiki/Recipe_Card) | Done | dont_starve_together, items |
| [Record](https://dontstarve.fandom.com/wiki/Record) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items, science, science_tier_2 |
| [Red Cap](https://dontstarve.fandom.com/wiki/Red_Cap) | Done | boss_dropped_items, food, healing, health_loss, mob_dropped_items, vegetables |
| [Red Firecrackers](https://dontstarve.fandom.com/wiki/Red_Firecrackers) | Done | craftable_items, dont_starve_together, items |
| [Red Gem](https://dontstarve.fandom.com/wiki/Red_Gem) | Done | boss_dropped_items, craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Red Lantern](https://dontstarve.fandom.com/wiki/Red_Lantern) | Done | craftable_items, dont_starve_together, equipable_items, items, light_sources |
| [Reed Tunic](https://dontstarve.fandom.com/wiki/Reed_Tunic) | Done | items |
| [Reeds](https://dontstarve.fandom.com/wiki/Reeds) | Done | plants, resources |
| [Refined Materials Filter](https://dontstarve.fandom.com/wiki/Refined_Materials_Filter) | Done | dont_starve_together |
| [Regrowth](https://dontstarve.fandom.com/wiki/Regrowth) | Done | dont_starve_together, gameplay |
| [Reinforced Support Pillar](https://dontstarve.fandom.com/wiki/Reinforced_Support_Pillar) | Done | craftable_structures, dont_starve_together, from_beyond, rare_blueprint_exclusive, structures |
| [Relic](https://dontstarve.fandom.com/wiki/Relic) | Done | a_new_reign, craftable_structures, decorations_filter, infobox_missing_crafting_description, mob_spawning_entities, rare_blueprint_exclusive, structures |
| [Repair Kits](https://dontstarve.fandom.com/wiki/Repair_Kits) | Done | dont_starve_together, from_beyond, tools_filter |
| [Research Notes](https://dontstarve.fandom.com/wiki/Research_Notes) | Done | dont_starve_together, from_beyond, fuel, items |
| [Resplendent Nox Helm](https://dontstarve.fandom.com/wiki/Resplendent_Nox_Helm) | Done | items |
| [Resting Horror](https://dontstarve.fandom.com/wiki/Resting_Horror) | Done | cave_creatures, dont_starve_together, from_beyond, mobs, passive_creatures |
| [Restrained Static](https://dontstarve.fandom.com/wiki/Restrained_Static) | Done | dont_starve_together, items |
| [Return of Them](https://dontstarve.fandom.com/wiki/Return_of_Them) | Done | dont_starve_together |
| [Rhinocebro](https://dontstarve.fandom.com/wiki/Rhinocebro) | Done | dont_starve_together, events, mobs |
| [Riled Lucy](https://dontstarve.fandom.com/wiki/Riled_Lucy) | Done | dont_starve_together, events, items |
| [Road](https://dontstarve.fandom.com/wiki/Road) | Done | gameplay |
| [Rock Den](https://dontstarve.fandom.com/wiki/Rock_Den) | Done | a_new_reign, crafting_stations, dont_starve_together, indestructible_object |
| [Rock Lobster](https://dontstarve.fandom.com/wiki/Rock_Lobster) | Done | animals, cave_creatures, dont_starve_together, followers, mob_spawning_entities, mobs, neutral_creatures |
| [Rockjaw](https://dontstarve.fandom.com/wiki/Rockjaw) | Done | dont_starve_together, mobs, monsters, ocean |
| [Rocks](https://dontstarve.fandom.com/wiki/Rocks) | Done | craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Rocky Beach](https://dontstarve.fandom.com/wiki/Rocky_Beach) | Done | dont_starve_together |
| [Rocky Beach Turf](https://dontstarve.fandom.com/wiki/Rocky_Beach_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, fuel, items, turf_items |
| [Rocky Turf](https://dontstarve.fandom.com/wiki/Rocky_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Rope](https://dontstarve.fandom.com/wiki/Rope) | Done | craftable_items, fuel, items, refine_tab, science_tier_1 |
| [Rose-Colored Glasses](https://dontstarve.fandom.com/wiki/Rose-Colored_Glasses) | Done | clothing_filter, craftable_items, dont_starve_together, items, resurrection |
| [Rot](https://dontstarve.fandom.com/wiki/Rot) | Done | craftable_items, fertilizer, fuel, health_loss, items |
| [Rotten Egg](https://dontstarve.fandom.com/wiki/Rotten_Egg) | Done | eggs, fertilizer, fuel, healing, health_loss, items |
| [Royal Jelly](https://dontstarve.fandom.com/wiki/Royal_Jelly) | Done | a_new_reign, boss_dropped_items, dont_starve_together, healing, items, mob_dropped_items |
| [Royal Rabbit Enforcer](https://dontstarve.fandom.com/wiki/Royal_Rabbit_Enforcer) | Done | dont_starve_together, from_beyond, hostile_creatures, mobs |
| [Royal Tapestry](https://dontstarve.fandom.com/wiki/Royal_Tapestry) | Done | craftable_structures, dont_starve_together, infobox_missing_crafting_description, science_tier_1, structures, survivor_items_filter |
| [Rudder Kit](https://dontstarve.fandom.com/wiki/Rudder_Kit) | Done | craftable_items, dont_starve_together, items, structures |
| [Ruins](https://dontstarve.fandom.com/wiki/Ruins) | Done | gameplay |
| [Runic Turf](https://dontstarve.fandom.com/wiki/Runic_Turf) | Done | nightmare_state_indicator, turf_items |
| [Ryftstal](https://dontstarve.fandom.com/wiki/Ryftstal) | Done | dont_starve_together, from_beyond |
| [Saddle](https://dontstarve.fandom.com/wiki/Saddle) | Done | a_new_reign, craftable_items, dont_starve_together, items, science_tier_2 |
| [Saddlehorn](https://dontstarve.fandom.com/wiki/Saddlehorn) | Done | craftable_items, equipable_items, items, science_tier_2, tools_filter, tools_tab |
| [Safe](https://dontstarve.fandom.com/wiki/Safe) | Done | dont_starve_together, events, structures |
| [Saladmander](https://dontstarve.fandom.com/wiki/Saladmander) | Done | dont_starve_together, mobs, neutral_creatures |
| [Salmon](https://dontstarve.fandom.com/wiki/Salmon) | Done | dont_starve_together, events, food |
| [Salsa Fresca](https://dontstarve.fandom.com/wiki/Salsa_Fresca) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, vegetables |
| [Salt Box](https://dontstarve.fandom.com/wiki/Salt_Box) | Done | cooking_filter, craftable_structures, dont_starve_together, food_tab, science_tier_2, structures |
| [Salt Crystals](https://dontstarve.fandom.com/wiki/Salt_Crystals) | Done | dont_starve_together, events, food, items |
| [Salt Formation](https://dontstarve.fandom.com/wiki/Salt_Formation) | Done | dont_starve_together, mineable_objects, ocean |
| [Salt Lick](https://dontstarve.fandom.com/wiki/Salt_Lick) | Done | a_new_reign, craftable_structures, science_tier_2, structures, tools_tab |
| [Salt Pond](https://dontstarve.fandom.com/wiki/Salt_Pond) | Done | dont_starve_together, events |
| [Salt Rack](https://dontstarve.fandom.com/wiki/Salt_Rack) | Done | dont_starve_together, events, items, structures |
| [Sammy](https://dontstarve.fandom.com/wiki/Sammy) | Done | dont_starve_together, events, mobs |
| [Sandstorm](https://dontstarve.fandom.com/wiki/Sandstorm) | Done | a_new_reign, dont_starve_together, gameplay |
| [Sandy Turf](https://dontstarve.fandom.com/wiki/Sandy_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, fuel, items, turf_items |
| [Sanguine Experiment](https://dontstarve.fandom.com/wiki/Sanguine_Experiment) | Done | craftable_items, dont_starve_together, events, fuel, items |
| [Sanity](https://dontstarve.fandom.com/wiki/Sanity) | Done | gameplay |
| [Sap](https://dontstarve.fandom.com/wiki/Sap) | Done | dont_starve_together, events, items |
| [Sapling](https://dontstarve.fandom.com/wiki/Sapling) | Done | dont_starve_together, fuel, plants, resources |
| [Savanna Turf](https://dontstarve.fandom.com/wiki/Savanna_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Saving](https://dontstarve.fandom.com/wiki/Saving) | Done | gameplay |
| [Sawhorse](https://dontstarve.fandom.com/wiki/Sawhorse) | Done | craftable_items, craftable_structures, dont_starve_together, from_beyond, items, rare_blueprint_exclusive, structures |
| [Scaled Chest](https://dontstarve.fandom.com/wiki/Scaled_Chest) | Done | containers, craftable_structures, dont_starve_together, infobox_missing_crafting_description, science, science_tier_2, structures |
| [Scaled Flooring](https://dontstarve.fandom.com/wiki/Scaled_Flooring) | Done | craftable_items, decorations_filter, dont_starve_together, fuel, items, science_tier_2, turf_items |
| [Scaled Furnace](https://dontstarve.fandom.com/wiki/Scaled_Furnace) | Done | a_new_reign, cooking_filter, craftable_structures, dont_starve_together, light_sources, rare_blueprint_exclusive, structures |
| [Scalemail](https://dontstarve.fandom.com/wiki/Scalemail) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, fight_tab, items, science, science_tier_2 |
| [Scales](https://dontstarve.fandom.com/wiki/Scales) | Done | boss_dropped_items, dont_starve_together, items, mob_dropped_items, resources |
| [Science Machine](https://dontstarve.fandom.com/wiki/Science_Machine) | Done | craftable_structures, crafting_stations, science, structures |
| [Scorpeon](https://dontstarve.fandom.com/wiki/Scorpeon) | Done | dont_starve_together, events, hostile_creatures, mobs |
| [Scrap](https://dontstarve.fandom.com/wiki/Scrap) | Done | dont_starve_together, from_beyond, items |
| [Scrap Wall](https://dontstarve.fandom.com/wiki/Scrap_Wall) | Done | decorations_filter, dont_starve_together, items, science, science_tier_2, structures |
| [Scrapbooking](https://dontstarve.fandom.com/wiki/Scrapbooking) | Done | dont_starve_together, gameplay |
| [Scrappy Chapauldron](https://dontstarve.fandom.com/wiki/Scrappy_Chapauldron) | Done | dont_starve_together, equipable_items, from_beyond, hats, items, mob_dropped_items |
| [Scrappy Werepig](https://dontstarve.fandom.com/wiki/Scrappy_Werepig) | Done | boss_monsters, dont_starve_together, from_beyond, mobs, monsters |
| [Sculptures Filter](https://dontstarve.fandom.com/wiki/Sculptures_Filter) | Done | dont_starve_together |
| [Sea Bones](https://dontstarve.fandom.com/wiki/Sea_Bones) | Done | dont_starve_together |
| [Sea Fishing Rod](https://dontstarve.fandom.com/wiki/Sea_Fishing_Rod) | Done | craftable_items, dont_starve_together, equipable_items, items, science_tier_1, tools_filter |
| [Sea Sprout Starter](https://dontstarve.fandom.com/wiki/Sea_Sprout_Starter) | Done | dont_starve_together, items, mob_dropped_items |
| [Sea Stack](https://dontstarve.fandom.com/wiki/Sea_Stack) | Done | dont_starve_together, ocean |
| [Sea Strider](https://dontstarve.fandom.com/wiki/Sea_Strider) | Done | dont_starve_together, followers, mobs, ocean, spiders |
| [Sea Strider Nest](https://dontstarve.fandom.com/wiki/Sea_Strider_Nest) | Done | dont_starve_together, ocean |
| [Sea Weed](https://dontstarve.fandom.com/wiki/Sea_Weed) | Done | dont_starve_together, mobs, ocean |
| [Seafaring Filter](https://dontstarve.fandom.com/wiki/Seafaring_Filter) | Done | dont_starve_together |
| [Seafood Gumbo](https://dontstarve.fandom.com/wiki/Seafood_Gumbo) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Sealed Portal](https://dontstarve.fandom.com/wiki/Sealed_Portal) | Done | dont_starve_together |
| [Seasoning Salt](https://dontstarve.fandom.com/wiki/Seasoning_Salt) | Done | craftable_items, dont_starve_together, items |
| [Seasonings Filter](https://dontstarve.fandom.com/wiki/Seasonings_Filter) | Done | dont_starve_together |
| [Seasons](https://dontstarve.fandom.com/wiki/Seasons) | Done | dont_starve_together, gameplay |
| [Autumn](https://dontstarve.fandom.com/wiki/Seasons/Autumn) | Done | dont_starve_together, gameplay |
| [Spring](https://dontstarve.fandom.com/wiki/Seasons/Spring) | Done | dont_starve_together, gameplay |
| [Summer](https://dontstarve.fandom.com/wiki/Seasons/Summer) | Done | dont_starve_together, gameplay |
| [Winter](https://dontstarve.fandom.com/wiki/Seasons/Winter) | Done | gameplay, weather |
| [World](https://dontstarve.fandom.com/wiki/Seasons/World) | Done | gameplay |
| [Seawreath](https://dontstarve.fandom.com/wiki/Seawreath) | Done | craftable_items, dont_starve_together, equipable_items, hats, items |
| [Second Chance Watch](https://dontstarve.fandom.com/wiki/Second_Chance_Watch) | Done | craftable_items, dont_starve_together, items, resurrection |
| [Seed Pack-It](https://dontstarve.fandom.com/wiki/Seed_Pack-It) | Done | backpacks, craftable_items, dont_starve_together, equipable_items, food_gardening_filter, food_tab, items, science_tier_2 |
| [Seeds](https://dontstarve.fandom.com/wiki/Seeds) | Done | food, healing, items, mob_dropped_items |
| [Seedshell](https://dontstarve.fandom.com/wiki/Seedshell) | Done | dont_starve_together, equipable_items, items, mob_dropped_items |
| [Serving](https://dontstarve.fandom.com/wiki/Serving) | Done | dont_starve_together, events, items |
| [Set Piece](https://dontstarve.fandom.com/wiki/Set_Piece) | Done | dont_starve_together, gameplay |
| [Sewing Kit](https://dontstarve.fandom.com/wiki/Sewing_Kit) | Done | craftable_items, items, science, science_tier_2, tools_filter |
| [Shadow Aligned](https://dontstarve.fandom.com/wiki/Shadow_Aligned) | Done | dont_starve_together, gameplay |
| [Shadow Atrium](https://dontstarve.fandom.com/wiki/Shadow_Atrium) | Done | a_new_reign, boss_dropped_items, dont_starve_together, from_beyond, items, mob_dropped_items, mobs |
| [Shadow Magic Filter](https://dontstarve.fandom.com/wiki/Shadow_Magic_Filter) | Done | dont_starve_together |
| [Shadow Manipulator](https://dontstarve.fandom.com/wiki/Shadow_Manipulator) | Done | craftable_structures, magic_tab, magic_tier_1, shadow_magic_filter, structures |
| [Shadow Maul](https://dontstarve.fandom.com/wiki/Shadow_Maul) | Done | craftable_items, dont_starve_together, from_beyond, healing, items |
| [Shadow Merm](https://dontstarve.fandom.com/wiki/Shadow_Merm) | Done | dont_starve_together, followers, hostile_creatures, mobs, nocturnals |
| [Shadow Pieces](https://dontstarve.fandom.com/wiki/Shadow_Pieces) | Done | a_new_reign, boss_monsters, dont_starve_together, hostile_creatures, mobs, monsters |
| [Shadow Reaper](https://dontstarve.fandom.com/wiki/Shadow_Reaper) | Done | craftable_items, dont_starve_together, from_beyond, items, melee_weapons, weapons |
| [Shadow Tentacle](https://dontstarve.fandom.com/wiki/Shadow_Tentacle) | Done | mobs |
| [Shadow Thurible](https://dontstarve.fandom.com/wiki/Shadow_Thurible) | Done | a_new_reign, boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Shadow Traps](https://dontstarve.fandom.com/wiki/Shadow_Traps) | Done | dont_starve_together, infobox_missing_crafting_description |
| [Shadow Watcher](https://dontstarve.fandom.com/wiki/Shadow_Watcher) | Done | mobs |
| [Shadowcraft Filter](https://dontstarve.fandom.com/wiki/Shadowcraft_Filter) | Done | dont_starve_together |
| [Shadowcraft Plinth](https://dontstarve.fandom.com/wiki/Shadowcraft_Plinth) | Done | ancient_tier_2, craftable_items, dont_starve_together, from_beyond, items, structures |
| [Shattered Spider](https://dontstarve.fandom.com/wiki/Shattered_Spider) | Done | dont_starve_together, hostile_creatures, mobs, monsters, nocturnals, spiders |
| [Shattered Spider Hole](https://dontstarve.fandom.com/wiki/Shattered_Spider_Hole) | Done | dont_starve_together, mineable_objects, mob_housing, mob_spawning_entities, spiders |
| [Shell Beach Turf](https://dontstarve.fandom.com/wiki/Shell_Beach_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, items, rare_blueprint_exclusive, turf_items |
| [Shell Bells](https://dontstarve.fandom.com/wiki/Shell_Bells) | Done | dont_starve_together, items, resources |
| [Shell Cluster](https://dontstarve.fandom.com/wiki/Shell_Cluster) | Done | dont_starve_together, ocean |
| [Shelmet](https://dontstarve.fandom.com/wiki/Shelmet) | Done | equipable_items, hats, items, mob_dropped_items |
| [Shield of Terror](https://dontstarve.fandom.com/wiki/Shield_of_Terror) | Done | boss_dropped_items, dont_starve_together, equipable_items, items, melee_weapons, mob_dropped_items, weapons |
| [Shoddy Tool](https://dontstarve.fandom.com/wiki/Shoddy_Tool) | Done | dont_starve_together, items |
| [Shoddy Tool Shed](https://dontstarve.fandom.com/wiki/Shoddy_Tool_Shed) | Done | craftable_structures, dont_starve_together, structures |
| [Shoo Box](https://dontstarve.fandom.com/wiki/Shoo_Box) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Shovel](https://dontstarve.fandom.com/wiki/Shovel) | Done | craftable_items, equipable_items, items, science, science_tier_1, science_tier_2, tools_filter, tools_tab |
| [Shroom Skin](https://dontstarve.fandom.com/wiki/Shroom_Skin) | Done | a_new_reign, boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Siesta Lean-to](https://dontstarve.fandom.com/wiki/Siesta_Lean-to) | Done | cooling, craftable_structures, dont_starve_together, healing, science_tier_2, structures, survival_tab |
| [Sign](https://dontstarve.fandom.com/wiki/Sign) | Done | craftable_structures, decorations_filter, science_tier_1, structures |
| [Silk](https://dontstarve.fandom.com/wiki/Silk) | Done | boss_dropped_items, items, mob_dropped_items, resources |
| [Silken Grand Armor](https://dontstarve.fandom.com/wiki/Silken_Grand_Armor) | Done | dont_starve_together, items |
| [Sinkhole](https://dontstarve.fandom.com/wiki/Sinkhole) | Done | indestructible_object, mineable_objects, mob_housing, mob_spawning_entities, portal, resources |
| [Sisturn](https://dontstarve.fandom.com/wiki/Sisturn) | Done | craftable_structures, dont_starve_together, structures, survivor_items_filter |
| [Skeeter Bomb](https://dontstarve.fandom.com/wiki/Skeeter_Bomb) | Done | craftable_items, dont_starve_together, from_beyond, items, weapons |
| [Skeleton](https://dontstarve.fandom.com/wiki/Skeleton) | Done | dont_starve_together |
| [Sketch](https://dontstarve.fandom.com/wiki/Sketch) | Done | a_new_reign, boss_dropped_items, celestial_tab, dont_starve_together, fuel, items, mob_dropped_items |
| [Skill Spotlight Update](https://dontstarve.fandom.com/wiki/Skill_Spotlight_Update) | Done | dont_starve_together |
| [Skins](https://dontstarve.fandom.com/wiki/Skins) | Done | dont_starve_together |
| [Skittersquid](https://dontstarve.fandom.com/wiki/Skittersquid) | Done | dont_starve_together, mobs, neutral_creatures |
| [Slaughter Tools](https://dontstarve.fandom.com/wiki/Slaughter_Tools) | Done | items |
| [Sleeping](https://dontstarve.fandom.com/wiki/Sleeping) | Done | gameplay |
| [Slimy Biome](https://dontstarve.fandom.com/wiki/Slimy_Biome) | Done | dont_starve_together |
| [Slimy Salve](https://dontstarve.fandom.com/wiki/Slimy_Salve) | Done | craftable_items, dont_starve_together, from_beyond, items, science_tier_2 |
| [Slimy Turf](https://dontstarve.fandom.com/wiki/Slimy_Turf) | Done | craftable_items, decorations_filter, fuel, items, turf_items |
| [Slingshot Ammo](https://dontstarve.fandom.com/wiki/Slingshot_Ammo) | Done | dont_starve_together, survivor_items_filter |
| [Slingshot Ammo Tab](https://dontstarve.fandom.com/wiki/Slingshot_Ammo_Tab) | Done | dont_starve_together |
| [Slurper](https://dontstarve.fandom.com/wiki/Slurper) | Done | equipable_items, hats, hostile_creatures, items, light_sources, mobs, nightmare_state_indicator, ruins_creatures |
| [Slurper Pelt](https://dontstarve.fandom.com/wiki/Slurper_Pelt) | Done | items, meats, mob_dropped_items |
| [Slurtle](https://dontstarve.fandom.com/wiki/Slurtle) | Done | animals, cave_creatures, mobs, neutral_creatures |
| [Slurtle Mound](https://dontstarve.fandom.com/wiki/Slurtle_Mound) | Done | mob_housing, mob_spawning_entities, structures |
| [Slurtle Slime](https://dontstarve.fandom.com/wiki/Slurtle_Slime) | Done | fuel, items, mob_dropped_items, resources |
| [Small Casserole Dish](https://dontstarve.fandom.com/wiki/Small_Casserole_Dish) | Done | items |
| [Small Jerky](https://dontstarve.fandom.com/wiki/Small_Jerky) | Done | healing, items, meats |
| [Snortoise](https://dontstarve.fandom.com/wiki/Snortoise) | Done | dont_starve_together, events, hostile_creatures, mobs |
| [Snurtle Shell Armor](https://dontstarve.fandom.com/wiki/Snurtle_Shell_Armor) | Done | equipable_items, items, mob_dropped_items |
| [Soothing Tea](https://dontstarve.fandom.com/wiki/Soothing_Tea) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Soul](https://dontstarve.fandom.com/wiki/Soul) | Done | dont_starve_together, items |
| [Soundtrack](https://dontstarve.fandom.com/wiki/Soundtrack) | Done | gameplay |
| [Spark Ark](https://dontstarve.fandom.com/wiki/Spark_Ark) | Done | boss_dropped_items, dont_starve_together, from_beyond, items |
| [Spear](https://dontstarve.fandom.com/wiki/Spear) | Done | craftable_items, equipable_items, fight_tab, items, melee_weapons, mob_dropped_items, science, science_tier_1, weapons |
| [Special Event Filter](https://dontstarve.fandom.com/wiki/Special_Event_Filter) | Done | dont_starve_together |
| [Spelunker's Bridge Kit](https://dontstarve.fandom.com/wiki/Spelunker's_Bridge_Kit) | Done | craftable_items, items, science_tier_2 |
| [Spicy Chili](https://dontstarve.fandom.com/wiki/Spicy_Chili) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, meats |
| [Spicy Vegetable Stinger](https://dontstarve.fandom.com/wiki/Spicy_Vegetable_Stinger) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Spider](https://dontstarve.fandom.com/wiki/Spider) | Done | cave_creatures, followers, hostile_creatures, mobs, monsters, nocturnals, spiders |
| [Spider Care Tab](https://dontstarve.fandom.com/wiki/Spider_Care_Tab) | Done | dont_starve_together |
| [Spider Den](https://dontstarve.fandom.com/wiki/Spider_Den) | Done | mob_housing, mob_spawning_entities, spiders, structures |
| [Spider Eggs](https://dontstarve.fandom.com/wiki/Spider_Eggs) | Done | boss_dropped_items, craftable_items, eggs, fuel, items, mob_dropped_items |
| [Spider Gland](https://dontstarve.fandom.com/wiki/Spider_Gland) | Done | healing, items, mob_dropped_items |
| [Spider Queen](https://dontstarve.fandom.com/wiki/Spider_Queen) | Done | boss_monsters, cave_creatures, hostile_creatures, mob_spawning_entities, mobs, monsters, spiders |
| [Spider Warrior](https://dontstarve.fandom.com/wiki/Spider_Warrior) | Done | cave_creatures, followers, hostile_creatures, mobs, monsters, nocturnals, spiders |
| [Spiderhat](https://dontstarve.fandom.com/wiki/Spiderhat) | Done | boss_dropped_items, equipable_items, hats, items, mob_dropped_items |
| [Spiky Bush](https://dontstarve.fandom.com/wiki/Spiky_Bush) | Done | fuel, health_loss, plants, resources |
| [Spiky Tree](https://dontstarve.fandom.com/wiki/Spiky_Tree) | Done | plants, resources, trees |
| [Spilagmite](https://dontstarve.fandom.com/wiki/Spilagmite) | Done | mineable_objects, mob_housing, mob_spawning_entities, spiders, structures |
| [Spiral Spear](https://dontstarve.fandom.com/wiki/Spiral_Spear) | Done | items |
| [Spitter](https://dontstarve.fandom.com/wiki/Spitter) | Done | cave_creatures, followers, hostile_creatures, mobs, monsters, nocturnals, spiders |
| [Splumonkey](https://dontstarve.fandom.com/wiki/Splumonkey) | Done | animals, hostile_creatures, mobs, neutral_creatures, nightmare_state_indicator, nocturnals, ruins_creatures |
| [Splumonkey Pod](https://dontstarve.fandom.com/wiki/Splumonkey_Pod) | Done | mob_housing, mob_spawning_entities, structures |
| [Spoiled Fish](https://dontstarve.fandom.com/wiki/Spoiled_Fish) | Done | dont_starve_together, fertilizer, fuel, health_loss, items, mob_dropped_items |
| [Spools](https://dontstarve.fandom.com/wiki/Spools) | Done | dont_starve_together |
| [Spotty Shrub](https://dontstarve.fandom.com/wiki/Spotty_Shrub) | Done | dont_starve_together, events, plants |
| [Spotty Sprig](https://dontstarve.fandom.com/wiki/Spotty_Sprig) | Done | dont_starve_together, events, items |
| [Sprouting Stone Fruit](https://dontstarve.fandom.com/wiki/Sprouting_Stone_Fruit) | Done | dont_starve_together, items, plants |
| [Sproutrock](https://dontstarve.fandom.com/wiki/Sproutrock) | Done | dont_starve_together, from_beyond, plants, trees |
| [Stag Antler](https://dontstarve.fandom.com/wiki/Stag_Antler) | Done | a_new_reign, boss_dropped_items, dont_starve_together, items, mob_dropped_items |
| [Stage](https://dontstarve.fandom.com/wiki/Stage) | Done | dont_starve_together, mobs, structures |
| [Stagecraft Tab](https://dontstarve.fandom.com/wiki/Stagecraft_Tab) | Done | dont_starve_together |
| [Stagehand](https://dontstarve.fandom.com/wiki/Stagehand) | Done | a_new_reign, craftable_structures, decorations_filter, dont_starve_together, indestructible_object, mobs, rare_blueprint_exclusive, structures |
| [Stalagmite](https://dontstarve.fandom.com/wiki/Stalagmite) | Done | mineable_objects, resources |
| [Star-Sky](https://dontstarve.fandom.com/wiki/Star-Sky) | Done | dont_starve_together, indestructible_object, items, mob_spawning_entities |
| [Star Caller's Staff](https://dontstarve.fandom.com/wiki/Star_Caller's_Staff) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items, items, light_sources |
| [Steadfast Grand Armor](https://dontstarve.fandom.com/wiki/Steadfast_Grand_Armor) | Done | items |
| [Steadfast Stone Armor](https://dontstarve.fandom.com/wiki/Steadfast_Stone_Armor) | Done | items |
| [Steamed Twigs](https://dontstarve.fandom.com/wiki/Steamed_Twigs) | Done | beefalo_foods, crock_pot_recipes, dont_starve_together, items |
| [Steel Wool](https://dontstarve.fandom.com/wiki/Steel_Wool) | Done | a_new_reign, dont_starve_together, fuel, items, mob_dropped_items, resources |
| [Steering Wheel](https://dontstarve.fandom.com/wiki/Steering_Wheel) | Done | craftable_items, dont_starve_together, items |
| [Stinger](https://dontstarve.fandom.com/wiki/Stinger) | Done | boss_dropped_items, items, mob_dropped_items |
| [Stone Fruit](https://dontstarve.fandom.com/wiki/Stone_Fruit) | Done | dont_starve_together, food, healing, items, mineable_objects, vegetables |
| [Stone Fruit Bush](https://dontstarve.fandom.com/wiki/Stone_Fruit_Bush) | Done | dont_starve_together, plants |
| [Stone Splint Mail](https://dontstarve.fandom.com/wiki/Stone_Splint_Mail) | Done | items |
| [Stone Wall](https://dontstarve.fandom.com/wiki/Stone_Wall) | Done | craftable_items, items, science_tier_2 |
| [Storage Solutions Filter](https://dontstarve.fandom.com/wiki/Storage_Solutions_Filter) | Done | dont_starve_together |
| [Straw Hat](https://dontstarve.fandom.com/wiki/Straw_Hat) | Done | craftable_items, equipable_items, hats, items, science |
| [Strident Trident](https://dontstarve.fandom.com/wiki/Strident_Trident) | Done | craftable_items, dont_starve_together, equipable_items, items, melee_weapons, weapons |
| [Strongman Tab](https://dontstarve.fandom.com/wiki/Strongman_Tab) | Done | dont_starve_together |
| [Structures](https://dontstarve.fandom.com/wiki/Structures) | Done | gameplay |
| [Structures Filter](https://dontstarve.fandom.com/wiki/Structures_Filter) | Done | dont_starve_together |
| [Stuffed Eggplant](https://dontstarve.fandom.com/wiki/Stuffed_Eggplant) | Done | crock_pot_recipes, food, healing, items |
| [Stuffed Fish Heads](https://dontstarve.fandom.com/wiki/Stuffed_Fish_Heads) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Stuffed Night Cap](https://dontstarve.fandom.com/wiki/Stuffed_Night_Cap) | Done | dont_starve_together, food, from_beyond, items, meats |
| [Stuffed Pepper Poppers](https://dontstarve.fandom.com/wiki/Stuffed_Pepper_Poppers) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, meats |
| [Sugarwood Tree](https://dontstarve.fandom.com/wiki/Sugarwood_Tree) | Done | dont_starve_together, events, plants, trees |
| [Sulfuric Experiment](https://dontstarve.fandom.com/wiki/Sulfuric_Experiment) | Done | craftable_items, dont_starve_together, events, fuel, items |
| [Summer Frest](https://dontstarve.fandom.com/wiki/Summer_Frest) | Done | cooling, craftable_items, dont_starve_together, equipable_items, items, science, science_tier_1 |
| [Summer Items Filter](https://dontstarve.fandom.com/wiki/Summer_Items_Filter) | Done | dont_starve_together |
| [Sunken Chest](https://dontstarve.fandom.com/wiki/Sunken_Chest) | Done | dont_starve_together, ocean |
| [Sunken Forest](https://dontstarve.fandom.com/wiki/Sunken_Forest) | Done | gameplay |
| [Surf 'n' Turf](https://dontstarve.fandom.com/wiki/Surf_'n'_Turf) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Surface World](https://dontstarve.fandom.com/wiki/Surface_World) | Done | gameplay |
| [Surprising Seed](https://dontstarve.fandom.com/wiki/Surprising_Seed) | Done | dont_starve_together, from_beyond, items, trees |
| [Survivor Items Filter](https://dontstarve.fandom.com/wiki/Survivor_Items_Filter) | Done | dont_starve_together |
| [Survivor Speed](https://dontstarve.fandom.com/wiki/Survivor_Speed) | Done | gameplay |
| [Suspicious Dirt Pile](https://dontstarve.fandom.com/wiki/Suspicious_Dirt_Pile) | Done | mob_spawning_entities, structures |
| [Suspicious Marble](https://dontstarve.fandom.com/wiki/Suspicious_Marble) | Done | a_new_reign, dont_starve_together, indestructible_object |
| [Suspicious Moonrock](https://dontstarve.fandom.com/wiki/Suspicious_Moonrock) | Done | a_new_reign, dont_starve_together, mineable_objects, mob_spawning_entities |
| [Suspicious Peeper](https://dontstarve.fandom.com/wiki/Suspicious_Peeper) | Done | hostile_creatures, mobs, monsters |
| [Swamp Brawler Helmet](https://dontstarve.fandom.com/wiki/Swamp_Brawler_Helmet) | Done | dont_starve_together, items |
| [Swamp Pig](https://dontstarve.fandom.com/wiki/Swamp_Pig) | Done | dont_starve_together, events, mobs |
| [Swamp Pig Elder](https://dontstarve.fandom.com/wiki/Swamp_Pig_Elder) | Done | dont_starve_together, events, mobs |
| [Switcherdoodle](https://dontstarve.fandom.com/wiki/Switcherdoodle) | Done | craftable_items, dont_starve_together, food, health_loss, items, meats, monster_foods, survivor_items_filter |
| [Syrup](https://dontstarve.fandom.com/wiki/Syrup) | Done | dont_starve_together, events, items |
| [Syrup of Ipecaca](https://dontstarve.fandom.com/wiki/Syrup_of_Ipecaca) | Done | craftable_items, dont_starve_together, items |
| [Syrup Pot](https://dontstarve.fandom.com/wiki/Syrup_Pot) | Done | items |
| [Table Lamp](https://dontstarve.fandom.com/wiki/Table_Lamp) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items, light_sources |
| [Table Vase](https://dontstarve.fandom.com/wiki/Table_Vase) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond, items, light_sources |
| [Tables](https://dontstarve.fandom.com/wiki/Tables) | Done | dont_starve_together, from_beyond |
| [Tackle Box](https://dontstarve.fandom.com/wiki/Tackle_Box) | Done | craftable_items, dont_starve_together, items |
| [Tackle Receptacle](https://dontstarve.fandom.com/wiki/Tackle_Receptacle) | Done | craftable_structures, dont_starve_together, science_tier_1, structures |
| [Taffy](https://dontstarve.fandom.com/wiki/Taffy) | Done | crock_pot_recipes, food, health_loss, items |
| [Tail o' Three Cats](https://dontstarve.fandom.com/wiki/Tail_o'_Three_Cats) | Done | a_new_reign, craftable_items, dont_starve_together, equipable_items, fight_tab, items, melee_weapons, science_tier_2, weapons |
| [Tall Scotch Eggs](https://dontstarve.fandom.com/wiki/Tall_Scotch_Eggs) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Tallbird](https://dontstarve.fandom.com/wiki/Tallbird) | Done | birds, hostile_creatures, innocents, mobs, passive_creatures |
| [Tallbird Egg](https://dontstarve.fandom.com/wiki/Tallbird_Egg) | Done | eggs, food, healing, items, mob_dropped_items, mob_spawning_entities |
| [Tallbird Nest](https://dontstarve.fandom.com/wiki/Tallbird_Nest) | Done | mob_spawning_entities |
| [Tam o' Shanter](https://dontstarve.fandom.com/wiki/Tam_o'_Shanter) | Done | equipable_items, hats, items, mob_dropped_items |
| [Telelocator Focus](https://dontstarve.fandom.com/wiki/Telelocator_Focus) | Done | craftable_structures, magic_tab, magic_tier_2, shadow_magic_filter, structures |
| [Telelocator Staff](https://dontstarve.fandom.com/wiki/Telelocator_Staff) | Done | craftable_items, equipable_items, items, magic_tab, magic_tier_2, shadow_magic_filter |
| [Teletransport Station](https://dontstarve.fandom.com/wiki/Teletransport_Station) | Done | craftable_items, craftable_structures, dont_starve_together, items, structures |
| [Telltale Heart](https://dontstarve.fandom.com/wiki/Telltale_Heart) | Done | craftable_items, dont_starve_together, health_loss, items, resurrection, survival_tab |
| [Tent](https://dontstarve.fandom.com/wiki/Tent) | Done | craftable_structures, healing, science, science_tier_2, structures, survival_tab |
| [Tent Roll](https://dontstarve.fandom.com/wiki/Tent_Roll) | Done | craftable_items, craftable_structures, dont_starve_together, healing, items, science_tier_1 |
| [Tentacle](https://dontstarve.fandom.com/wiki/Tentacle) | Done | cave_creatures, hostile_creatures, mob_spawning_entities, mobs, monsters |
| [Tentacle Spike](https://dontstarve.fandom.com/wiki/Tentacle_Spike) | Done | equipable_items, items, melee_weapons, mob_dropped_items, weapons |
| [Tentacle Spots](https://dontstarve.fandom.com/wiki/Tentacle_Spots) | Done | fuel, items, mob_dropped_items |
| [Terra Firma Tamper](https://dontstarve.fandom.com/wiki/Terra_Firma_Tamper) | Done | craftable_structures, decorations_filter, dont_starve_together, rare_blueprint_exclusive, structures |
| [Terrarium](https://dontstarve.fandom.com/wiki/Terrarium) | Done | dont_starve_together, items |
| [Terrorbeak](https://dontstarve.fandom.com/wiki/Terrorbeak) | Done | mobs |
| [Terrorclaw](https://dontstarve.fandom.com/wiki/Terrorclaw) | Done | mobs |
| [The Altar of Gnaw](https://dontstarve.fandom.com/wiki/The_Altar_of_Gnaw) | Done | dont_starve_together, events, indestructible_object, structures |
| [The Curse of Moon Quay](https://dontstarve.fandom.com/wiki/The_Curse_of_Moon_Quay) | Done | dont_starve_together |
| [The Forge](https://dontstarve.fandom.com/wiki/The_Forge) | Done | dont_starve_together, events |
| [The Gnaw](https://dontstarve.fandom.com/wiki/The_Gnaw) | Done | dont_starve_together, events |
| [The Gorge](https://dontstarve.fandom.com/wiki/The_Gorge) | Done | dont_starve_together, events |
| [The Gorge Recipes](https://dontstarve.fandom.com/wiki/The_Gorge_Recipes) | Done | dont_starve_together, events |
| [The Gorge Seeds](https://dontstarve.fandom.com/wiki/The_Gorge_Seeds) | Done | dont_starve_together, events |
| [The Lazy Deserter](https://dontstarve.fandom.com/wiki/The_Lazy_Deserter) | Done | a_new_reign, craftable_structures, dont_starve_together, rare_blueprint_exclusive, shadow_magic_filter, structures |
| [The Lazy Explorer](https://dontstarve.fandom.com/wiki/The_Lazy_Explorer) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items, items |
| [The Lazy Forager](https://dontstarve.fandom.com/wiki/The_Lazy_Forager) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items, items |
| [Thermal Measurer](https://dontstarve.fandom.com/wiki/Thermal_Measurer) | Done | craftable_structures, science, science_tier_1, structures, weather |
| [Thermal Stone](https://dontstarve.fandom.com/wiki/Thermal_Stone) | Done | cooling, craftable_items, items, light_sources, science, science_tier_2, survival_tab |
| [Thick Fur](https://dontstarve.fandom.com/wiki/Thick_Fur) | Done | boss_dropped_items, craftable_items, dont_starve_together, infobox_missing_crafting_description, items, mob_dropped_items, refine_tab, resources, science_tier_2 |
| [Think Tank](https://dontstarve.fandom.com/wiki/Think_Tank) | Done | craftable_structures, dont_starve_together, science_tier_1, seafaring_filter, structures |
| [Thulecite](https://dontstarve.fandom.com/wiki/Thulecite) | Done | ancient_tab, ancient_tier_1, craftable_items, items, resources |
| [Thulecite Bug Net](https://dontstarve.fandom.com/wiki/Thulecite_Bug_Net) | Done | craftable_items, items, rare_blueprint_exclusive, tools_filter |
| [Thulecite Club](https://dontstarve.fandom.com/wiki/Thulecite_Club) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items, items, melee_weapons, mob_spawning_entities, weapons |
| [Thulecite Crown](https://dontstarve.fandom.com/wiki/Thulecite_Crown) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items, hats, items, light_sources |
| [Thulecite Fragments](https://dontstarve.fandom.com/wiki/Thulecite_Fragments) | Done | items, mob_dropped_items, resources |
| [Thulecite Medallion](https://dontstarve.fandom.com/wiki/Thulecite_Medallion) | Done | ancient_tab, ancient_tier_1, craftable_items, items, nightmare_state_indicator |
| [Thulecite Suit](https://dontstarve.fandom.com/wiki/Thulecite_Suit) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items, items |
| [Thulecite Wall](https://dontstarve.fandom.com/wiki/Thulecite_Wall) | Done | ancient_tier_1 |
| [Tidy Hidey-Hole](https://dontstarve.fandom.com/wiki/Tidy_Hidey-Hole) | Done | dont_starve_together, structures |
| [Tillweed Salve](https://dontstarve.fandom.com/wiki/Tillweed_Salve) | Done | craftable_items, dont_starve_together, healing, items, science_tier_2 |
| [Tillweeds](https://dontstarve.fandom.com/wiki/Tillweeds) | Done | dont_starve_together, healing, items |
| [Time Pieces](https://dontstarve.fandom.com/wiki/Time_Pieces) | Done | dont_starve_together |
| [Tin Fishin' Bin](https://dontstarve.fandom.com/wiki/Tin_Fishin'_Bin) | Done | craftable_structures, dont_starve_together, seafaring_filter, structures |
| [Toadstool](https://dontstarve.fandom.com/wiki/Toadstool) | Done | a_new_reign, boss_monsters, cave_creatures, dont_starve_together, mobs |
| [Toma Root](https://dontstarve.fandom.com/wiki/Toma_Root) | Done | dont_starve_together, food, healing, vegetables |
| [Tome of Beckoning](https://dontstarve.fandom.com/wiki/Tome_of_Beckoning) | Done | items |
| [Tools Filter](https://dontstarve.fandom.com/wiki/Tools_Filter) | Done | dont_starve_together |
| [Tooth Trap](https://dontstarve.fandom.com/wiki/Tooth_Trap) | Done | craftable_items, fight_tab, items, science, science_tier_2, weapons |
| [Top Hat](https://dontstarve.fandom.com/wiki/Top_Hat) | Done | craftable_items, equipable_items, hats, items, science, science_tier_1 |
| [Torch](https://dontstarve.fandom.com/wiki/Torch) | Done | craftable_items, equipable_items, items, light_sources, science |
| [Totally Normal Tree](https://dontstarve.fandom.com/wiki/Totally_Normal_Tree) | Done | plants, resources, trees |
| [Touch Stone](https://dontstarve.fandom.com/wiki/Touch_Stone) | Done | dont_starve_together, resurrection, structures |
| [Trade Inn](https://dontstarve.fandom.com/wiki/Trade_Inn) | Done | dont_starve_together |
| [Trading Hutch Filter](https://dontstarve.fandom.com/wiki/Trading_Hutch_Filter) | Done | dont_starve_together, from_beyond |
| [Trail Mix](https://dontstarve.fandom.com/wiki/Trail_Mix) | Done | crock_pot_recipes, dont_starve_together, food, healing, items |
| [Trap](https://dontstarve.fandom.com/wiki/Trap) | Done | craftable_items, food_gardening_filter, items, science, survival_tab, tools_filter |
| [Treasury](https://dontstarve.fandom.com/wiki/Treasury) | Done | dont_starve_together |
| [Tree Jam](https://dontstarve.fandom.com/wiki/Tree_Jam) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter, items, science_tier_2 |
| [Tree Tapping Kit](https://dontstarve.fandom.com/wiki/Tree_Tapping_Kit) | Done | items |
| [Treeguard](https://dontstarve.fandom.com/wiki/Treeguard) | Done | boss_monsters, cave_creatures, mobs, monsters, neutral_creatures |
| [Treeguard Idol](https://dontstarve.fandom.com/wiki/Treeguard_Idol) | Done | craftable_items, dont_starve_together, items, shadow_magic_filter |
| [Trinkets](https://dontstarve.fandom.com/wiki/Trinkets) | Done | a_new_reign, dont_starve_together, items |
| [Trusty Slingshot](https://dontstarve.fandom.com/wiki/Trusty_Slingshot) | Done | craftable_items, dont_starve_together, equipable_items, items |
| [Trusty Tape](https://dontstarve.fandom.com/wiki/Trusty_Tape) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Tumbleweed](https://dontstarve.fandom.com/wiki/Tumbleweed) | Done | dont_starve_together, mob_spawning_entities, plants |
| [Turf-Raiser Helm](https://dontstarve.fandom.com/wiki/Turf-Raiser_Helm) | Done | clothing_filter, craftable_items, dont_starve_together, infobox_missing_crafting_description, items, rare_blueprint_exclusive, shadow_magic_filter, tools_filter |
| [Turkey Dinner](https://dontstarve.fandom.com/wiki/Turkey_Dinner) | Done | crock_pot_recipes, food, healing, items, meats |
| [Turnip](https://dontstarve.fandom.com/wiki/Turnip) | Done | dont_starve_together, events, food |
| [Twiggy Tree](https://dontstarve.fandom.com/wiki/Twiggy_Tree) | Done | a_new_reign, dont_starve_together, plants, trees |
| [Twiggy Tree Cone](https://dontstarve.fandom.com/wiki/Twiggy_Tree_Cone) | Done | a_new_reign, dont_starve_together, fuel, items |
| [Twigs](https://dontstarve.fandom.com/wiki/Twigs) | Done | beefalo_foods, craftable_items, fuel, infobox_missing_crafting_description, items, mob_dropped_items, resources |
| [Umbralla](https://dontstarve.fandom.com/wiki/Umbralla) | Done | craftable_items, dont_starve_together, from_beyond, items |
| [Umbrella](https://dontstarve.fandom.com/wiki/Umbrella) | Done | clothing_filter, craftable_items, equipable_items, fuel, items, melee_weapons, science, science_tier_1, survival_tab, weapons |
| [Unagi](https://dontstarve.fandom.com/wiki/Unagi) | Done | craftable_items, crock_pot_recipes, food, healing, items |
| [Underwater Salvageable](https://dontstarve.fandom.com/wiki/Underwater_Salvageable) | Done | dont_starve_together, ocean |
| [Unnatural Portal](https://dontstarve.fandom.com/wiki/Unnatural_Portal) | Done | dont_starve_together, structures |
| [Unstable Transmission](https://dontstarve.fandom.com/wiki/Unstable_Transmission) | Done | dont_starve_together, items |
| [Varg](https://dontstarve.fandom.com/wiki/Varg) | Done | dont_starve_together, hostile_creatures, mob_spawning_entities, mobs, monsters |
| [Varglet](https://dontstarve.fandom.com/wiki/Varglet) | Done | dont_starve_together, mobs |
| [Veggie Burger](https://dontstarve.fandom.com/wiki/Veggie_Burger) | Done | crock_pot_recipes, dont_starve_together, food, healing, items, meats |
| [Vignettes](https://dontstarve.fandom.com/wiki/Vignettes) | Done | dont_starve_together |
| [Vitreoasis](https://dontstarve.fandom.com/wiki/Vitreoasis) | Done | dont_starve_together |
| [Void Cowl](https://dontstarve.fandom.com/wiki/Void_Cowl) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Void Robe](https://dontstarve.fandom.com/wiki/Void_Robe) | Done | craftable_items, dont_starve_together, from_beyond, infobox_missing_crafting_description, items |
| [Volt Goat](https://dontstarve.fandom.com/wiki/Volt_Goat) | Done | animals, dont_starve_together, hostile_creatures, innocents, light_sources, mobs, neutral_creatures |
| [Volt Goat Chaud-Froid](https://dontstarve.fandom.com/wiki/Volt_Goat_Chaud-Froid) | Done | dont_starve_together, items |
| [Volt Goat Horn](https://dontstarve.fandom.com/wiki/Volt_Goat_Horn) | Done | dont_starve_together, items, mob_dropped_items, resources |
| [W.A.R.B.I.S. Armor](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Armor) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond, items, rare_blueprint_exclusive |
| [W.A.R.B.I.S. Head Gear](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Head_Gear) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond, items, rare_blueprint_exclusive |
| [W.A.R.B.O.T.](https://dontstarve.fandom.com/wiki/W.A.R.B.O.T.) | Done | boss_monsters, dont_starve_together |
| [W.I.N.bot](https://dontstarve.fandom.com/wiki/W.I.N.bot) | Done | dont_starve_together, items, mobs |
| [W.O.B.O.T.](https://dontstarve.fandom.com/wiki/W.O.B.O.T.) | Done | dont_starve_together, from_beyond, items, mobs |
| [Waffles](https://dontstarve.fandom.com/wiki/Waffles) | Done | crock_pot_recipes, food, fruits, healing, items |
| [Grainy Transmission](https://dontstarve.fandom.com/wiki/Wagstaff/Grainy_Transmission) | Done | dont_starve_together, items, mobs |
| [Walking Cane](https://dontstarve.fandom.com/wiki/Walking_Cane) | Done | craftable_items, equipable_items, items, melee_weapons, science, science_tier_2, tools_filter, weapons |
| [Wall](https://dontstarve.fandom.com/wiki/Wall) | Done | dont_starve_together, fuel |
| [Walrus Camp](https://dontstarve.fandom.com/wiki/Walrus_Camp) | Done | indestructible_object, light_sources, mob_housing, mob_spawning_entities, structures |
| [Walrus Tusk](https://dontstarve.fandom.com/wiki/Walrus_Tusk) | Done | items, mob_dropped_items, resources |
| [Walter](https://dontstarve.fandom.com/wiki/Walter) | Done | dont_starve_together |
| [Wanda](https://dontstarve.fandom.com/wiki/Wanda) | Done | dont_starve_together |
| [Wanda clothes](https://dontstarve.fandom.com/wiki/Wanda_clothes) | Done | dont_starve_together |
| [Wardrobe](https://dontstarve.fandom.com/wiki/Wardrobe) | Done | craftable_structures, decorations_filter, dont_starve_together, science_tier_2, structures |
| [Warly](https://dontstarve.fandom.com/wiki/Warly) | Done | dont_starve_together |
| [Warren Wreath](https://dontstarve.fandom.com/wiki/Warren_Wreath) | Done | craftable_items, equipable_items, from_beyond, items |
| [Water Balloon](https://dontstarve.fandom.com/wiki/Water_Balloon) | Done | craftable_items, dont_starve_together, equipable_items, items, science, science_tier_1 |
| [Watering Can](https://dontstarve.fandom.com/wiki/Watering_Can) | Done | craftable_items, dont_starve_together, equipable_items, food_gardening_filter, items, science_tier_1, science_tier_2, tools_filter |
| [Waterlogged](https://dontstarve.fandom.com/wiki/Waterlogged) | Done | dont_starve_together, ocean |
| [Watermelon](https://dontstarve.fandom.com/wiki/Watermelon) | Done | cooling, dont_starve_together, food, fruits, healing, items, resources |
| [Waves](https://dontstarve.fandom.com/wiki/Waves) | Done | dont_starve_together, gameplay, ocean |
| [Wavey Jones](https://dontstarve.fandom.com/wiki/Wavey_Jones) | Done | mobs |
| [Wax Paper](https://dontstarve.fandom.com/wiki/Wax_Paper) | Done | craftable_items, fuel, items, refine_tab, science_tier_1, science_tier_2 |
| [Weapons Filter](https://dontstarve.fandom.com/wiki/Weapons_Filter) | Done | dont_starve_together |
| [Weather Pain](https://dontstarve.fandom.com/wiki/Weather_Pain) | Done | craftable_items, dont_starve_together, equipable_items, fight_tab, items, ranged_weapons, weapons |
| [Webber](https://dontstarve.fandom.com/wiki/Webber) | Done | dont_starve_together, monsters, spiders |
| [Webby Whistle](https://dontstarve.fandom.com/wiki/Webby_Whistle) | Done | craftable_items, dont_starve_together, items, tools_filter |
| [Weeds](https://dontstarve.fandom.com/wiki/Weeds) | Done | dont_starve_together |
| [Weight](https://dontstarve.fandom.com/wiki/Weight) | Done | dont_starve_together, gameplay |
| [Werepig](https://dontstarve.fandom.com/wiki/Werepig) | Done | hostile_creatures, mobs, monsters, nocturnals |
| [Wet Goop](https://dontstarve.fandom.com/wiki/Wet_Goop) | Done | crock_pot_recipes, items |
| [Wetness](https://dontstarve.fandom.com/wiki/Wetness) | Done | dont_starve_together, gameplay |
| [Wheat](https://dontstarve.fandom.com/wiki/Wheat) | Done | dont_starve_together, events, items |
| [Whirly Fan](https://dontstarve.fandom.com/wiki/Whirly_Fan) | Done | clothing_filter, cooling, craftable_items, dont_starve_together, equipable_items, items, melee_weapons, survival_tab |
| [Whispering Grand Armor](https://dontstarve.fandom.com/wiki/Whispering_Grand_Armor) | Done | dont_starve_together, items |
| [Wigfrid](https://dontstarve.fandom.com/wiki/Wigfrid) | Done | dont_starve_together |
| [Reign of Giants](https://dontstarve.fandom.com/wiki/Wigfrid/Reign_of_Giants) | Done | dont_starve_together |
| [Wild Rift Cycle](https://dontstarve.fandom.com/wiki/Wild_Rift_Cycle) | Done | dont_starve_together, from_beyond, gameplay, light_sources, mob_spawning_entities |
| [Willow's Lighter](https://dontstarve.fandom.com/wiki/Willow's_Lighter) | Done | cooking_filter, craftable_items, equipable_items, items, light_sources, survivor_items_filter |
| [Don't Starve Together](https://dontstarve.fandom.com/wiki/Wilson/Don't_Starve_Together) | Done | dont_starve_together |
| [Winona](https://dontstarve.fandom.com/wiki/Winona) | Done | dont_starve_together |
| [Winona's Catapult](https://dontstarve.fandom.com/wiki/Winona's_Catapult) | Done | craftable_items, craftable_structures, dont_starve_together, followers, items, structures |
| [Winona's G.E.M.erator](https://dontstarve.fandom.com/wiki/Winona's_G.E.M.erator) | Done | craftable_items, craftable_structures, dont_starve_together, items, structures |
| [Winona's Generator](https://dontstarve.fandom.com/wiki/Winona's_Generator) | Done | craftable_items, craftable_structures, dont_starve_together, items, structures |
| [Winona's Spotlight](https://dontstarve.fandom.com/wiki/Winona's_Spotlight) | Done | craftable_structures, dont_starve_together, structures |
| [Winona clothes](https://dontstarve.fandom.com/wiki/Winona_clothes) | Done | dont_starve_together |
| [Winter's Feast](https://dontstarve.fandom.com/wiki/Winter's_Feast) | Done | dont_starve_together, events |
| [Winter Hat](https://dontstarve.fandom.com/wiki/Winter_Hat) | Done | craftable_items, equipable_items, hats, items, science, science_tier_2 |
| [Winter Items Filter](https://dontstarve.fandom.com/wiki/Winter_Items_Filter) | Done | dont_starve_together |
| [Wobster](https://dontstarve.fandom.com/wiki/Wobster) | Done | dont_starve_together, fishes, food, healing, items, mob_dropped_items, mobs, nocturnals, ocean, passive_creatures |
| [Wobster Bisque](https://dontstarve.fandom.com/wiki/Wobster_Bisque) | Done | cooling, crock_pot_recipes, dont_starve_together, food, healing, items |
| [Wobster Dinner](https://dontstarve.fandom.com/wiki/Wobster_Dinner) | Done | craftable_items, crock_pot_recipes, dont_starve_together, fishes, healing, items, meats |
| [Wobster Mound](https://dontstarve.fandom.com/wiki/Wobster_Mound) | Done | dont_starve_together, ocean |
| [Woby](https://dontstarve.fandom.com/wiki/Woby) | Done | dont_starve_together, mobs |
| [Wonkey](https://dontstarve.fandom.com/wiki/Wonkey) | Done | dont_starve_together |
| [Wood Armor](https://dontstarve.fandom.com/wiki/Wood_Armor) | Done | items |
| [Wood Fence](https://dontstarve.fandom.com/wiki/Wood_Fence) | Done | a_new_reign, craftable_items, craftable_structures, decorations_filter, items, science_tier_1, structures |
| [Wood Gate](https://dontstarve.fandom.com/wiki/Wood_Gate) | Done | a_new_reign, craftable_items, decorations_filter, items, science_tier_2 |
| [Wood Wall](https://dontstarve.fandom.com/wiki/Wood_Wall) | Done | craftable_items, craftable_structures, decorations_filter, items, science, science_tier_1, structures |
| [Wooden Flooring](https://dontstarve.fandom.com/wiki/Wooden_Flooring) | Done | craftable_items, decorations_filter, fuel, items, science, science_tier_2, turf_items |
| [Wooden Walking Stick](https://dontstarve.fandom.com/wiki/Wooden_Walking_Stick) | Done | clothing_filter, craftable_items, dont_starve_together, items, tools_filter |
| [World Customization](https://dontstarve.fandom.com/wiki/World_Customization) | Done | gameplay |
| [Don't Starve Together](https://dontstarve.fandom.com/wiki/World_Customization/Don't_Starve_Together) | Done | dont_starve_together, gameplay |
| [World Generation](https://dontstarve.fandom.com/wiki/World_Generation) | Done | gameplay |
| [World Generation Screen](https://dontstarve.fandom.com/wiki/World_Generation_Screen) | Done | gameplay |
| [World Retrofit](https://dontstarve.fandom.com/wiki/World_Retrofit) | Done | gameplay |
| [Worm Hole](https://dontstarve.fandom.com/wiki/Worm_Hole) | Done | indestructible_object, portal, structures |
| [Wormwood](https://dontstarve.fandom.com/wiki/Wormwood) | Done | dont_starve_together |
| [Wortox](https://dontstarve.fandom.com/wiki/Wortox) | Done | dont_starve_together, monsters |
| [Wortox clothes](https://dontstarve.fandom.com/wiki/Wortox_clothes) | Done | dont_starve_together |
| [Woven Garland](https://dontstarve.fandom.com/wiki/Woven_Garland) | Done | items |
| [Woven Shadow](https://dontstarve.fandom.com/wiki/Woven_Shadow) | Done | a_new_reign, dont_starve_together, mobs, passive_creatures |
| [Wurt](https://dontstarve.fandom.com/wiki/Wurt) | Done | dont_starve_together |
| [Wurt clothes](https://dontstarve.fandom.com/wiki/Wurt_clothes) | Done | dont_starve_together |
| [Year of the Beefalo](https://dontstarve.fandom.com/wiki/Year_of_the_Beefalo) | Done | dont_starve_together, events |
| [Year of the Bunnyman](https://dontstarve.fandom.com/wiki/Year_of_the_Bunnyman) | Done | dont_starve_together, events, infobox_missing_crafting_description |
| [Year of the Carrat](https://dontstarve.fandom.com/wiki/Year_of_the_Carrat) | Done | dont_starve_together, events |
| [Year of the Catcoon](https://dontstarve.fandom.com/wiki/Year_of_the_Catcoon) | Done | dont_starve_together, events |
| [Year of the Dragonfly](https://dontstarve.fandom.com/wiki/Year_of_the_Dragonfly) | Done | dont_starve_together, events |
| [Year of the Gobbler](https://dontstarve.fandom.com/wiki/Year_of_the_Gobbler) | Done | dont_starve_together, events |
| [Year of the Pig King](https://dontstarve.fandom.com/wiki/Year_of_the_Pig_King) | Done | dont_starve_together, events |
| [Year of the Varg](https://dontstarve.fandom.com/wiki/Year_of_the_Varg) | Done | dont_starve_together, events |
| [Yellow Gem](https://dontstarve.fandom.com/wiki/Yellow_Gem) | Done | boss_dropped_items, craftable_items, infobox_missing_crafting_description, items, mob_dropped_items, resources |
