# Category crawler control

Registry máy đọc/ghi nằm tại `<git-common-dir>/category-crawler/`; file
`data/crawled/fandom-url-registry.json` và MD này chỉ là snapshot/bảng review.
Trạng thái chỉ gồm `New`, `Doing`, `Done`: URL mới/`New` được lấy tiếp, còn
`Doing` và `Done` phải skip network fetch.

> **Cache audit blocker (2026-07-21):** 29 row đang ghi `Done`, nhưng các file
> raw shared payload tương ứng không còn sau khi worktree cũ được dọn. Không
> được coi các row snapshot này là reusable; lúc init live state, chúng phải
> được import thành `New` và crawl lại vào Git-common storage.

## Category queue

| Category | Source | Direct | Child category | Excluded | Publish candidates | Registry Done | Status |
|---|---|---:|---:|---:|---:|---:|---|
| animals | [Category:Animals](https://dontstarve.fandom.com/wiki/Category:Animals) | 35 | 4 | 6 | 29 | 29 | Done |
| armour_filter | [Category:Armour Filter](https://dontstarve.fandom.com/wiki/Category:Armour_Filter) | 19 | 0 | 0 | 19 | 0 | New |
| beefalo_foods | [Category:Beefalo Foods](https://dontstarve.fandom.com/wiki/Category:Beefalo_Foods) | 5 | 0 | 0 | 5 | 0 | New |
| boss_dropped_items | [Category:Boss Dropped Items](https://dontstarve.fandom.com/wiki/Category:Boss_Dropped_Items) | 75 | 0 | 12 | 63 | 0 | New |
| backpacks | [Category:Backpacks](https://dontstarve.fandom.com/wiki/Category:Backpacks) | 10 | 0 | 4 | 6 | 0 | New |
| clothing_filter | [Category:Clothing Filter](https://dontstarve.fandom.com/wiki/Category:Clothing_Filter) | 10 | 0 | 0 | 10 | 0 | New |
| cave_creatures | [Category:Cave Creatures](https://dontstarve.fandom.com/wiki/Category:Cave_Creatures) | 32 | 1 | 3 | 29 | 6 | New |
| celestial_filter | [Category:Celestial Filter](https://dontstarve.fandom.com/wiki/Category:Celestial_Filter) | 6 | 0 | 0 | 6 | 0 | New |
| celestial_tab | [Category:Celestial Tab](https://dontstarve.fandom.com/wiki/Category:Celestial_Tab) | 6 | 0 | 0 | 6 | 0 | New |
| containers | [Category:Containers](https://dontstarve.fandom.com/wiki/Category:Containers) | 28 | 1 | 13 | 15 | 0 | New |

Batch mới có 191 direct memberships, 174 title duy nhất. Sau review còn 147 URL
hợp lệ: registry đang ghi 6 URL overlap là `Done` và 141 URL là `New`, nhưng sáu
row `Done` chưa thể reuse vì cache audit blocker ở trên. Hai Category con bị bỏ,
24 title độc quyền game khác bị loại trên toàn batch, cùng ba trang tổng quan
không đại diện prefab.

`https://dontstarve.fandom.com/wiki/Celestial_Filter` là article, không phải
Category. Nguồn crawler đã sửa thành
`https://dontstarve.fandom.com/wiki/Category:Celestial_Filter`.

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

- Keep (6): Glass Cutter, Moon Crater Turf, Moon Glass Axe, Moon Rock Idol, Mutated Fungal Turf, Sketch.

### Category:Containers

- Keep (15): Backpack, Bundling Wrap, Chef Pouch, Chest, Chester, Crock Pot, Hutch, Ice Box, Insulated Pack, Krampus Sack, Ornate Chest, Piggyback, Polar Bearger Bin, Portable Crock Pot, Scaled Chest.
- Exclude trước detail (13): Booty Bag (`non_dst:shipwrecked`), Cargo Boat (`non_dst:shipwrecked`), Cork Barrel (`non_dst:hamlet`), Octopus Chest (`non_dst:shipwrecked`), Packim Baggims (`non_dst:shipwrecked`), Ro Bin (`non_dst:hamlet`), Sea Chest (`non_dst:shipwrecked`), Sea Sack (`non_dst:shipwrecked`), Steamer Trunk (`non_dst:shipwrecked`), Thatch Pack (`non_dst:shipwrecked`), Trawl Net (`non_dst:shipwrecked`), Vortex Cloak (`non_dst:hamlet`), Wooden Thing (`non_dst:dont_starve`).
- Bỏ Category con, không đệ quy: Category:Backpacks.

## Shared item URLs

| Item URL | Status | Categories |
|---|---|---|
| [Ancient Key](https://dontstarve.fandom.com/wiki/Ancient_Key) | New | boss_dropped_items |
| [Backpack](https://dontstarve.fandom.com/wiki/Backpack) | New | backpacks, containers |
| [Bath Bomb](https://dontstarve.fandom.com/wiki/Bath_Bomb) | New | celestial_filter |
| [Batilisk](https://dontstarve.fandom.com/wiki/Batilisk) | New | cave_creatures |
| [Battle Helm](https://dontstarve.fandom.com/wiki/Battle_Helm) | New | armour_filter |
| [Battle Rönd](https://dontstarve.fandom.com/wiki/Battle_R%C3%B6nd) | New | armour_filter |
| [Bee](https://dontstarve.fandom.com/wiki/Bee) | Done | animals |
| [Bee Queen Crown](https://dontstarve.fandom.com/wiki/Bee_Queen_Crown) | New | boss_dropped_items |
| [Beefalo](https://dontstarve.fandom.com/wiki/Beefalo) | Done | animals |
| [Beefalo Hat](https://dontstarve.fandom.com/wiki/Beefalo_Hat) | New | clothing_filter |
| [Beefalo Treats](https://dontstarve.fandom.com/wiki/Beefalo_Treats) | New | beefalo_foods |
| [Beekeeper Hat](https://dontstarve.fandom.com/wiki/Beekeeper_Hat) | New | armour_filter |
| [Blue Cap](https://dontstarve.fandom.com/wiki/Blue_Cap) | New | boss_dropped_items |
| [Blue Gem](https://dontstarve.fandom.com/wiki/Blue_Gem) | New | boss_dropped_items |
| [Blueprint](https://dontstarve.fandom.com/wiki/Blueprint) | New | boss_dropped_items |
| [Bone Armor](https://dontstarve.fandom.com/wiki/Bone_Armor) | New | boss_dropped_items |
| [Bone Helm](https://dontstarve.fandom.com/wiki/Bone_Helm) | New | boss_dropped_items |
| [Bramble Husk](https://dontstarve.fandom.com/wiki/Bramble_Husk) | New | armour_filter |
| [Bright-Eyed Frog](https://dontstarve.fandom.com/wiki/Bright-Eyed_Frog) | Done | animals |
| [Brightshade Armor](https://dontstarve.fandom.com/wiki/Brightshade_Armor) | New | armour_filter |
| [Brightshade Helm](https://dontstarve.fandom.com/wiki/Brightshade_Helm) | New | armour_filter |
| [Brightsmithy](https://dontstarve.fandom.com/wiki/Brightsmithy) | New | celestial_filter |
| [Bulbous Lightbug](https://dontstarve.fandom.com/wiki/Bulbous_Lightbug) | Done | animals, cave_creatures |
| [Bundling Wrap](https://dontstarve.fandom.com/wiki/Bundling_Wrap) | New | containers |
| [Bunnyman](https://dontstarve.fandom.com/wiki/Bunnyman) | Done | animals, cave_creatures |
| [Butterfly](https://dontstarve.fandom.com/wiki/Butterfly) | Done | animals |
| [Buzzard](https://dontstarve.fandom.com/wiki/Buzzard) | Done | animals |
| [Catcoon](https://dontstarve.fandom.com/wiki/Catcoon) | Done | animals |
| [Cave Spider](https://dontstarve.fandom.com/wiki/Cave_Spider) | New | cave_creatures |
| [Charcoal](https://dontstarve.fandom.com/wiki/Charcoal) | New | boss_dropped_items |
| [Chef Pouch](https://dontstarve.fandom.com/wiki/Chef_Pouch) | New | backpacks, containers |
| [Chest](https://dontstarve.fandom.com/wiki/Chest) | New | containers |
| [Chester](https://dontstarve.fandom.com/wiki/Chester) | New | containers |
| [Clockwork Bishop](https://dontstarve.fandom.com/wiki/Clockwork_Bishop) | New | cave_creatures |
| [Commander's Helm](https://dontstarve.fandom.com/wiki/Commander's_Helm) | New | armour_filter |
| [Cookie Cutter Cap](https://dontstarve.fandom.com/wiki/Cookie_Cutter_Cap) | New | armour_filter |
| [Crock Pot](https://dontstarve.fandom.com/wiki/Crock_Pot) | New | containers |
| [Cut Grass](https://dontstarve.fandom.com/wiki/Cut_Grass) | New | beefalo_foods |
| [Cut Reeds](https://dontstarve.fandom.com/wiki/Cut_Reeds) | New | beefalo_foods |
| [Dangling Depth Dweller](https://dontstarve.fandom.com/wiki/Dangling_Depth_Dweller) | New | cave_creatures |
| [Dark Sword](https://dontstarve.fandom.com/wiki/Dark_Sword) | New | boss_dropped_items |
| [Dark Tatters](https://dontstarve.fandom.com/wiki/Dark_Tatters) | New | boss_dropped_items |
| [Deerclops Eyeball](https://dontstarve.fandom.com/wiki/Deerclops_Eyeball) | New | boss_dropped_items |
| [Depths Worm](https://dontstarve.fandom.com/wiki/Depths_Worm) | New | cave_creatures |
| [Desert Stone](https://dontstarve.fandom.com/wiki/Desert_Stone) | New | boss_dropped_items |
| [Down Feather](https://dontstarve.fandom.com/wiki/Down_Feather) | New | boss_dropped_items |
| [Dreadstone Armor](https://dontstarve.fandom.com/wiki/Dreadstone_Armor) | New | armour_filter |
| [Dreadstone Helm](https://dontstarve.fandom.com/wiki/Dreadstone_Helm) | New | armour_filter |
| [Drumstick](https://dontstarve.fandom.com/wiki/Drumstick) | New | boss_dropped_items |
| [Dust Moth](https://dontstarve.fandom.com/wiki/Dust_Moth) | Done | animals, cave_creatures |
| [Enlightened Crown](https://dontstarve.fandom.com/wiki/Enlightened_Crown) | New | boss_dropped_items |
| [Ewecus](https://dontstarve.fandom.com/wiki/Ewecus) | Done | animals |
| [Eye Mask](https://dontstarve.fandom.com/wiki/Eye_Mask) | New | boss_dropped_items |
| [Fireflies](https://dontstarve.fandom.com/wiki/Fireflies) | New | cave_creatures |
| [Football Helmet](https://dontstarve.fandom.com/wiki/Football_Helmet) | New | armour_filter |
| [Fossils](https://dontstarve.fandom.com/wiki/Fossils) | New | boss_dropped_items |
| [Friendly Fruit Fly Fruit](https://dontstarve.fandom.com/wiki/Friendly_Fruit_Fly_Fruit) | New | boss_dropped_items |
| [Frog](https://dontstarve.fandom.com/wiki/Frog) | Done | animals |
| [Frog Legs](https://dontstarve.fandom.com/wiki/Frog_Legs) | New | boss_dropped_items |
| [Funcap](https://dontstarve.fandom.com/wiki/Funcap) | New | clothing_filter |
| [Fur Tuft](https://dontstarve.fandom.com/wiki/Fur_Tuft) | New | boss_dropped_items |
| [Gem Deer](https://dontstarve.fandom.com/wiki/Gem_Deer) | Done | animals |
| [Glass Cutter](https://dontstarve.fandom.com/wiki/Glass_Cutter) | New | celestial_filter, celestial_tab |
| [Glommer](https://dontstarve.fandom.com/wiki/Glommer) | Done | animals |
| [Gobbler](https://dontstarve.fandom.com/wiki/Gobbler) | Done | animals |
| [Gold Nugget](https://dontstarve.fandom.com/wiki/Gold_Nugget) | New | boss_dropped_items |
| [Grass Gator](https://dontstarve.fandom.com/wiki/Grass_Gator) | Done | animals |
| [Grass Suit](https://dontstarve.fandom.com/wiki/Grass_Suit) | New | armour_filter |
| [Great Depths Worm](https://dontstarve.fandom.com/wiki/Great_Depths_Worm) | New | cave_creatures |
| [Green Cap](https://dontstarve.fandom.com/wiki/Green_Cap) | New | boss_dropped_items |
| [Green Gem](https://dontstarve.fandom.com/wiki/Green_Gem) | New | boss_dropped_items |
| [Guardian's Horn](https://dontstarve.fandom.com/wiki/Guardian's_Horn) | New | boss_dropped_items |
| [Hardwood Hat](https://dontstarve.fandom.com/wiki/Hardwood_Hat) | New | armour_filter |
| [Honey](https://dontstarve.fandom.com/wiki/Honey) | New | boss_dropped_items |
| [Honeycomb](https://dontstarve.fandom.com/wiki/Honeycomb) | New | boss_dropped_items |
| [Hutch](https://dontstarve.fandom.com/wiki/Hutch) | New | cave_creatures, containers |
| [Ice Box](https://dontstarve.fandom.com/wiki/Ice_Box) | New | containers |
| [Icker](https://dontstarve.fandom.com/wiki/Icker) | New | cave_creatures |
| [Infused Moon Shard](https://dontstarve.fandom.com/wiki/Infused_Moon_Shard) | New | boss_dropped_items |
| [Ink Blight](https://dontstarve.fandom.com/wiki/Ink_Blight) | New | cave_creatures |
| [Inspectacles](https://dontstarve.fandom.com/wiki/Inspectacles) | New | clothing_filter |
| [Insulated Pack](https://dontstarve.fandom.com/wiki/Insulated_Pack) | New | backpacks, containers |
| [Koalefant](https://dontstarve.fandom.com/wiki/Koalefant) | Done | animals |
| [Krampus Sack](https://dontstarve.fandom.com/wiki/Krampus_Sack) | New | backpacks, boss_dropped_items, containers |
| [Lavae Egg](https://dontstarve.fandom.com/wiki/Lavae_Egg) | New | boss_dropped_items |
| [Living Log](https://dontstarve.fandom.com/wiki/Living_Log) | New | boss_dropped_items |
| [Log Suit](https://dontstarve.fandom.com/wiki/Log_Suit) | New | armour_filter |
| [Lunar Funcap](https://dontstarve.fandom.com/wiki/Lunar_Funcap) | New | celestial_filter |
| [Lurking Nightmare](https://dontstarve.fandom.com/wiki/Lurking_Nightmare) | New | cave_creatures |
| [Malbatross Bill](https://dontstarve.fandom.com/wiki/Malbatross_Bill) | New | boss_dropped_items |
| [Malbatross Feather](https://dontstarve.fandom.com/wiki/Malbatross_Feather) | New | boss_dropped_items |
| [Marble Suit](https://dontstarve.fandom.com/wiki/Marble_Suit) | New | armour_filter |
| [Meat](https://dontstarve.fandom.com/wiki/Meat) | New | boss_dropped_items |
| [Milky Whites](https://dontstarve.fandom.com/wiki/Milky_Whites) | New | boss_dropped_items |
| [Mimicreep](https://dontstarve.fandom.com/wiki/Mimicreep) | New | cave_creatures |
| [Moleworm](https://dontstarve.fandom.com/wiki/Moleworm) | Done | animals, cave_creatures |
| [Monster Meat](https://dontstarve.fandom.com/wiki/Monster_Meat) | New | boss_dropped_items |
| [Moon Crater Turf](https://dontstarve.fandom.com/wiki/Moon_Crater_Turf) | New | celestial_tab |
| [Moon Glass Axe](https://dontstarve.fandom.com/wiki/Moon_Glass_Axe) | New | celestial_tab |
| [Moon Glass Saw Blade](https://dontstarve.fandom.com/wiki/Moon_Glass_Saw_Blade) | New | celestial_filter |
| [Moon Rock](https://dontstarve.fandom.com/wiki/Moon_Rock) | New | boss_dropped_items |
| [Moon Rock Idol](https://dontstarve.fandom.com/wiki/Moon_Rock_Idol) | New | celestial_tab |
| [Moon Shard](https://dontstarve.fandom.com/wiki/Moon_Shard) | New | boss_dropped_items |
| [Mosling](https://dontstarve.fandom.com/wiki/Mosling) | Done | animals |
| [Mosquito](https://dontstarve.fandom.com/wiki/Mosquito) | Done | animals |
| [Mush Gnome](https://dontstarve.fandom.com/wiki/Mush_Gnome) | New | cave_creatures |
| [Mushrooms](https://dontstarve.fandom.com/wiki/Mushrooms) | New | boss_dropped_items |
| [Mutated Fungal Turf](https://dontstarve.fandom.com/wiki/Mutated_Fungal_Turf) | New | celestial_tab |
| [Naked Mole Bat](https://dontstarve.fandom.com/wiki/Naked_Mole_Bat) | New | cave_creatures |
| [Night Armor](https://dontstarve.fandom.com/wiki/Night_Armor) | New | armour_filter, boss_dropped_items |
| [Nightmare Fuel](https://dontstarve.fandom.com/wiki/Nightmare_Fuel) | New | boss_dropped_items |
| [No-Eyed Deer](https://dontstarve.fandom.com/wiki/No-Eyed_Deer) | Done | animals |
| [Orange Gem](https://dontstarve.fandom.com/wiki/Orange_Gem) | New | boss_dropped_items |
| [Ornate Chest](https://dontstarve.fandom.com/wiki/Ornate_Chest) | New | boss_dropped_items, containers |
| [Parrot Pirate](https://dontstarve.fandom.com/wiki/Parrot_Pirate) | Done | animals |
| [Pearl's Pearl](https://dontstarve.fandom.com/wiki/Pearl's_Pearl) | New | boss_dropped_items |
| [Pengull](https://dontstarve.fandom.com/wiki/Pengull) | Done | animals |
| [Pig](https://dontstarve.fandom.com/wiki/Pig) | Done | animals |
| [Piggyback](https://dontstarve.fandom.com/wiki/Piggyback) | New | backpacks, clothing_filter, containers |
| [Polar Bearger Bin](https://dontstarve.fandom.com/wiki/Polar_Bearger_Bin) | New | containers |
| [Portable Crock Pot](https://dontstarve.fandom.com/wiki/Portable_Crock_Pot) | New | containers |
| [Portal Paraphernalia](https://dontstarve.fandom.com/wiki/Portal_Paraphernalia) | New | celestial_filter |
| [Portasol](https://dontstarve.fandom.com/wiki/Portasol) | New | clothing_filter |
| [Powder Monkey](https://dontstarve.fandom.com/wiki/Powder_Monkey) | Done | animals |
| [Pure Horror](https://dontstarve.fandom.com/wiki/Pure_Horror) | New | boss_dropped_items |
| [Purple Gem](https://dontstarve.fandom.com/wiki/Purple_Gem) | New | boss_dropped_items |
| [Rabbit](https://dontstarve.fandom.com/wiki/Rabbit) | Done | animals |
| [Raw Fish](https://dontstarve.fandom.com/wiki/Raw_Fish) | New | boss_dropped_items |
| [Reanimated Skeleton](https://dontstarve.fandom.com/wiki/Reanimated_Skeleton) | New | cave_creatures |
| [Red Cap](https://dontstarve.fandom.com/wiki/Red_Cap) | New | boss_dropped_items |
| [Red Gem](https://dontstarve.fandom.com/wiki/Red_Gem) | New | boss_dropped_items |
| [Resting Horror](https://dontstarve.fandom.com/wiki/Resting_Horror) | New | cave_creatures |
| [Rock Lobster](https://dontstarve.fandom.com/wiki/Rock_Lobster) | Done | animals, cave_creatures |
| [Rose-Colored Glasses](https://dontstarve.fandom.com/wiki/Rose-Colored_Glasses) | New | clothing_filter |
| [Royal Jelly](https://dontstarve.fandom.com/wiki/Royal_Jelly) | New | boss_dropped_items |
| [Scaled Chest](https://dontstarve.fandom.com/wiki/Scaled_Chest) | New | containers |
| [Scalemail](https://dontstarve.fandom.com/wiki/Scalemail) | New | armour_filter |
| [Scales](https://dontstarve.fandom.com/wiki/Scales) | New | boss_dropped_items |
| [Seed Pack-It](https://dontstarve.fandom.com/wiki/Seed_Pack-It) | New | backpacks |
| [Shadow Atrium](https://dontstarve.fandom.com/wiki/Shadow_Atrium) | New | boss_dropped_items |
| [Shadow Thurible](https://dontstarve.fandom.com/wiki/Shadow_Thurible) | New | boss_dropped_items |
| [Shield of Terror](https://dontstarve.fandom.com/wiki/Shield_of_Terror) | New | boss_dropped_items |
| [Shroom Skin](https://dontstarve.fandom.com/wiki/Shroom_Skin) | New | boss_dropped_items |
| [Silk](https://dontstarve.fandom.com/wiki/Silk) | New | boss_dropped_items |
| [Sketch](https://dontstarve.fandom.com/wiki/Sketch) | New | boss_dropped_items, celestial_tab |
| [Slurtle](https://dontstarve.fandom.com/wiki/Slurtle) | Done | animals, cave_creatures |
| [Spark Ark](https://dontstarve.fandom.com/wiki/Spark_Ark) | New | boss_dropped_items |
| [Spider](https://dontstarve.fandom.com/wiki/Spider) | New | cave_creatures |
| [Spider Eggs](https://dontstarve.fandom.com/wiki/Spider_Eggs) | New | boss_dropped_items |
| [Spider Queen](https://dontstarve.fandom.com/wiki/Spider_Queen) | New | cave_creatures |
| [Spider Warrior](https://dontstarve.fandom.com/wiki/Spider_Warrior) | New | cave_creatures |
| [Spiderhat](https://dontstarve.fandom.com/wiki/Spiderhat) | New | boss_dropped_items |
| [Spitter](https://dontstarve.fandom.com/wiki/Spitter) | New | cave_creatures |
| [Splumonkey](https://dontstarve.fandom.com/wiki/Splumonkey) | Done | animals |
| [Stag Antler](https://dontstarve.fandom.com/wiki/Stag_Antler) | New | boss_dropped_items |
| [Steamed Twigs](https://dontstarve.fandom.com/wiki/Steamed_Twigs) | New | beefalo_foods |
| [Stinger](https://dontstarve.fandom.com/wiki/Stinger) | New | boss_dropped_items |
| [Tentacle](https://dontstarve.fandom.com/wiki/Tentacle) | New | cave_creatures |
| [Thick Fur](https://dontstarve.fandom.com/wiki/Thick_Fur) | New | boss_dropped_items |
| [Toadstool](https://dontstarve.fandom.com/wiki/Toadstool) | New | cave_creatures |
| [Treeguard](https://dontstarve.fandom.com/wiki/Treeguard) | New | cave_creatures |
| [Turf-Raiser Helm](https://dontstarve.fandom.com/wiki/Turf-Raiser_Helm) | New | clothing_filter |
| [Twigs](https://dontstarve.fandom.com/wiki/Twigs) | New | beefalo_foods |
| [Umbrella](https://dontstarve.fandom.com/wiki/Umbrella) | New | clothing_filter |
| [Volt Goat](https://dontstarve.fandom.com/wiki/Volt_Goat) | Done | animals |
| [W.A.R.B.I.S. Armor](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Armor) | New | armour_filter |
| [W.A.R.B.I.S. Head Gear](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Head_Gear) | New | armour_filter |
| [Whirly Fan](https://dontstarve.fandom.com/wiki/Whirly_Fan) | New | clothing_filter |
| [Wooden Walking Stick](https://dontstarve.fandom.com/wiki/Wooden_Walking_Stick) | New | clothing_filter |
| [Yellow Gem](https://dontstarve.fandom.com/wiki/Yellow_Gem) | New | boss_dropped_items |

Khi thêm Category khác, crawler tự thêm URL/category/status vào JSON registry.
Sau mỗi batch đã review, cập nhật bảng MD này từ registry để dùng làm handoff.
