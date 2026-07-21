# Category crawler control

Registry máy đọc/ghi nằm tại `<git-common-dir>/category-crawler/`; file
`data/crawled/fandom-url-registry.json` và MD này chỉ là snapshot/bảng review.
Trạng thái chỉ gồm `New`, `Doing`, `Done`: URL mới/`New` được lấy tiếp, còn
`Doing` và `Done` phải skip network fetch.

> **Live audit 2026-07-21:** 1.153 URL hợp lệ, 1.153 `Done`, 0 `New`, 0
> `Doing`, 0 artifact lỗi. Toàn bộ URL đã duyệt và aggregate DST đã hoàn tất.

## Category queue

| Category | Source | Direct | Child category | Excluded | Publish candidates | Registry Done | Status |
|---|---|---:|---:|---:|---:|---:|---|
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
không còn `New`/`Doing`. `Animals` tái sử dụng config đã duyệt; `Parrot Pirate`
được giữ như ngoại lệ DST trong cả Animals và Birds. Sáu alias màu Moonlens bị
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

## Shared item URLs

| Item URL | Status | Categories |
|---|---|---|
| [A Little Drama and QOL](https://dontstarve.fandom.com/wiki/A_Little_Drama_and_QOL) | Done | dont_starve_together |
| [A New Reign](https://dontstarve.fandom.com/wiki/A_New_Reign) | Done | dont_starve_together |
| [Abandoned Junk](https://dontstarve.fandom.com/wiki/Abandoned_Junk) | Done | dont_starve_together, from_beyond |
| [Abigail](https://dontstarve.fandom.com/wiki/Abigail) | Done | followers |
| [Abigail's Flower](https://dontstarve.fandom.com/wiki/Abigail's_Flower) | Done | craftable_items |
| [Accomploshrine](https://dontstarve.fandom.com/wiki/Accomploshrine) | Done | craftable_structures |
| [Accursed Trinket](https://dontstarve.fandom.com/wiki/Accursed_Trinket) | Done | dont_starve_together |
| [Acid Rain](https://dontstarve.fandom.com/wiki/Acid_Rain) | Done | dont_starve_together, from_beyond |
| [Ageless Watch](https://dontstarve.fandom.com/wiki/Ageless_Watch) | Done | craftable_items, dont_starve_together |
| [Alarming Clock](https://dontstarve.fandom.com/wiki/Alarming_Clock) | Done | craftable_items, dont_starve_together, equipable_items |
| [Alchemy Engine](https://dontstarve.fandom.com/wiki/Alchemy_Engine) | Done | craftable_structures |
| [Amberosia](https://dontstarve.fandom.com/wiki/Amberosia) | Done | crock_pot_recipes, dont_starve_together |
| [An Eye for An Eye](https://dontstarve.fandom.com/wiki/An_Eye_for_An_Eye) | Done | dont_starve_together |
| [Anchor](https://dontstarve.fandom.com/wiki/Anchor) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Ancient Anchor](https://dontstarve.fandom.com/wiki/Ancient_Anchor) | Done | dont_starve_together, events |
| [Ancient Archive](https://dontstarve.fandom.com/wiki/Ancient_Archive) | Done | dont_starve_together |
| [Ancient Beacon](https://dontstarve.fandom.com/wiki/Ancient_Beacon) | Done | a_new_reign, dont_starve_together |
| [Ancient Brickwork](https://dontstarve.fandom.com/wiki/Ancient_Brickwork) | Done | craftable_items, dont_starve_together |
| [Ancient Chest](https://dontstarve.fandom.com/wiki/Ancient_Chest) | Done | dont_starve_together |
| [Ancient Fence](https://dontstarve.fandom.com/wiki/Ancient_Fence) | Done | a_new_reign, dont_starve_together |
| [Ancient Flooring](https://dontstarve.fandom.com/wiki/Ancient_Flooring) | Done | craftable_items, dont_starve_together |
| [Ancient Gateway](https://dontstarve.fandom.com/wiki/Ancient_Gateway) | Done | a_new_reign, dont_starve_together |
| [Ancient Guard Post](https://dontstarve.fandom.com/wiki/Ancient_Guard_Post) | Done | dont_starve_together |
| [Ancient Guardian](https://dontstarve.fandom.com/wiki/Ancient_Guardian) | Done | boss_monsters |
| [Ancient Key](https://dontstarve.fandom.com/wiki/Ancient_Key) | Done | a_new_reign, boss_dropped_items, dont_starve_together |
| [Ancient Kiln](https://dontstarve.fandom.com/wiki/Ancient_Kiln) | Done | dont_starve_together |
| [Ancient Lunarune Stone](https://dontstarve.fandom.com/wiki/Ancient_Lunarune_Stone) | Done | dont_starve_together |
| [Ancient Moon Statue](https://dontstarve.fandom.com/wiki/Ancient_Moon_Statue) | Done | dont_starve_together |
| [Ancient Mural](https://dontstarve.fandom.com/wiki/Ancient_Mural) | Done | a_new_reign, dont_starve_together |
| [Ancient Obelisk](https://dontstarve.fandom.com/wiki/Ancient_Obelisk) | Done | a_new_reign, dont_starve_together |
| [Ancient Pseudoscience Filter](https://dontstarve.fandom.com/wiki/Ancient_Pseudoscience_Filter) | Done | dont_starve_together |
| [Ancient Pseudoscience Station](https://dontstarve.fandom.com/wiki/Ancient_Pseudoscience_Station) | Done | ancient_tab, crafting_stations |
| [Ancient Sentrypede](https://dontstarve.fandom.com/wiki/Ancient_Sentrypede) | Done | dont_starve_together |
| [Ancient Statue](https://dontstarve.fandom.com/wiki/Ancient_Statue) | Done | a_new_reign, dont_starve_together |
| [Ancient Stonework](https://dontstarve.fandom.com/wiki/Ancient_Stonework) | Done | craftable_items, dont_starve_together |
| [Ancient Tilework](https://dontstarve.fandom.com/wiki/Ancient_Tilework) | Done | craftable_items, dont_starve_together |
| [Anenemy](https://dontstarve.fandom.com/wiki/Anenemy) | Done | dont_starve_together |
| [Antlion](https://dontstarve.fandom.com/wiki/Antlion) | Done | a_new_reign, boss_monsters, dont_starve_together |
| [Arboretum Experiment](https://dontstarve.fandom.com/wiki/Arboretum_Experiment) | Done | craftable_items, dont_starve_together, events, fuel |
| [Archaic Boat](https://dontstarve.fandom.com/wiki/Archaic_Boat) | Done | dont_starve_together, from_beyond |
| [Archive Chandelier](https://dontstarve.fandom.com/wiki/Archive_Chandelier) | Done | dont_starve_together |
| [Archive Orchestrina](https://dontstarve.fandom.com/wiki/Archive_Orchestrina) | Done | dont_starve_together |
| [Archive Switch](https://dontstarve.fandom.com/wiki/Archive_Switch) | Done | dont_starve_together |
| [Armermry](https://dontstarve.fandom.com/wiki/Armermry) | Done | craftable_structures, dont_starve_together |
| [Armored Bearger](https://dontstarve.fandom.com/wiki/Armored_Bearger) | Done | boss_monsters, dont_starve_together, from_beyond |
| [Armour Filter](https://dontstarve.fandom.com/wiki/Armour_Filter) | Done | dont_starve_together |
| [Art?](https://dontstarve.fandom.com/wiki/Art%3F) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Asparagazpacho](https://dontstarve.fandom.com/wiki/Asparagazpacho) | Done | dont_starve_together |
| [Asparagus](https://dontstarve.fandom.com/wiki/Asparagus) | Done | dont_starve_together, food |
| [Asparagus Soup](https://dontstarve.fandom.com/wiki/Asparagus_Soup) | Done | crock_pot_recipes, dont_starve_together |
| [Astral Detector](https://dontstarve.fandom.com/wiki/Astral_Detector) | Done | craftable_items, dont_starve_together |
| [Astroggles](https://dontstarve.fandom.com/wiki/Astroggles) | Done | craftable_items, dont_starve_together, equipable_items |
| [Atrium](https://dontstarve.fandom.com/wiki/Atrium) | Done | a_new_reign, dont_starve_together |
| [Axe](https://dontstarve.fandom.com/wiki/Axe) | Done | celestial_tab, craftable_items, dont_starve_together, equipable_items |
| [Baby Spider](https://dontstarve.fandom.com/wiki/Baby_Spider) | Done | dont_starve_together |
| [Backpack](https://dontstarve.fandom.com/wiki/Backpack) | Done | backpacks, containers, craftable_items, equipable_items |
| [Backstep Watch](https://dontstarve.fandom.com/wiki/Backstep_Watch) | Done | craftable_items, dont_starve_together |
| [Backtrek Watch](https://dontstarve.fandom.com/wiki/Backtrek_Watch) | Done | craftable_items, dont_starve_together |
| [Bacon and Eggs](https://dontstarve.fandom.com/wiki/Bacon_and_Eggs) | Done | craftable_items, crock_pot_recipes, eggs |
| [Balloonomancy Tab](https://dontstarve.fandom.com/wiki/Balloonomancy_Tab) | Done | dont_starve_together |
| [Banana](https://dontstarve.fandom.com/wiki/Banana) | Done | dont_starve_together, food, fruits |
| [Banana Bush](https://dontstarve.fandom.com/wiki/Banana_Bush) | Done | dont_starve_together |
| [Banana Pop](https://dontstarve.fandom.com/wiki/Banana_Pop) | Done | cooling, crock_pot_recipes, dont_starve_together, food |
| [Banana Shake](https://dontstarve.fandom.com/wiki/Banana_Shake) | Done | crock_pot_recipes, dont_starve_together, food |
| [Barnacle Linguine](https://dontstarve.fandom.com/wiki/Barnacle_Linguine) | Done | crock_pot_recipes, dont_starve_together, food |
| [Barnacle Nigiri](https://dontstarve.fandom.com/wiki/Barnacle_Nigiri) | Done | dont_starve_together |
| [Barnacle Pita](https://dontstarve.fandom.com/wiki/Barnacle_Pita) | Done | crock_pot_recipes, dont_starve_together, food |
| [Barnacles](https://dontstarve.fandom.com/wiki/Barnacles) | Done | dont_starve_together, food |
| [Bat Bat](https://dontstarve.fandom.com/wiki/Bat_Bat) | Done | craftable_items, equipable_items |
| [Bat Cave](https://dontstarve.fandom.com/wiki/Bat_Cave) | Done | dont_starve_together |
| [Bath Bomb](https://dontstarve.fandom.com/wiki/Bath_Bomb) | Done | celestial_filter, craftable_items, dont_starve_together |
| [Batilisk](https://dontstarve.fandom.com/wiki/Batilisk) | Done | cave_creatures, flying_creatures |
| [Batilisk Wing](https://dontstarve.fandom.com/wiki/Batilisk_Wing) | Done | food |
| [Battle Call Canister](https://dontstarve.fandom.com/wiki/Battle_Call_Canister) | Done | craftable_items, dont_starve_together |
| [Battle Helm](https://dontstarve.fandom.com/wiki/Battle_Helm) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, fight_tab |
| [Battle Paddle](https://dontstarve.fandom.com/wiki/Battle_Paddle) | Done | dont_starve_together, equipable_items |
| [Battle Rönd](https://dontstarve.fandom.com/wiki/Battle_R%C3%B6nd) | Done | armour_filter, craftable_items, dont_starve_together |
| [Battle Songs](https://dontstarve.fandom.com/wiki/Battle_Songs) | Done | dont_starve_together |
| [Battle Spear](https://dontstarve.fandom.com/wiki/Battle_Spear) | Done | craftable_items, dont_starve_together, equipable_items, fight_tab |
| [Battlemaster Pugna](https://dontstarve.fandom.com/wiki/Battlemaster_Pugna) | Done | dont_starve_together, events |
| [Beard Hair](https://dontstarve.fandom.com/wiki/Beard_Hair) | Done | craftable_items, fuel |
| [Beard Hair Rug](https://dontstarve.fandom.com/wiki/Beard_Hair_Rug) | Done | craftable_items, dont_starve_together, fuel |
| [Beards](https://dontstarve.fandom.com/wiki/Beards) | Done | dont_starve_together |
| [Bearger](https://dontstarve.fandom.com/wiki/Bearger) | Done | boss_monsters, dont_starve_together |
| [Bed Roll](https://dontstarve.fandom.com/wiki/Bed_Roll) | Done | craftable_items, fuel |
| [Bee](https://dontstarve.fandom.com/wiki/Bee) | Done | animals, flying_creatures |
| [Bee Box](https://dontstarve.fandom.com/wiki/Bee_Box) | Done | craftable_structures, food_gardening_filter, food_tab |
| [Bee Mine](https://dontstarve.fandom.com/wiki/Bee_Mine) | Done | craftable_items, fight_tab |
| [Bee Queen](https://dontstarve.fandom.com/wiki/Bee_Queen) | Done | a_new_reign, boss_monsters, dont_starve_together, flying_creatures |
| [Bee Queen Crown](https://dontstarve.fandom.com/wiki/Bee_Queen_Crown) | Done | a_new_reign, boss_dropped_items, dont_starve_together, equipable_items |
| [Beefalo](https://dontstarve.fandom.com/wiki/Beefalo) | Done | animals, followers |
| [Beefalo Bell](https://dontstarve.fandom.com/wiki/Beefalo_Bell) | Done | craftable_items, dont_starve_together |
| [Beefalo Gloom Bell](https://dontstarve.fandom.com/wiki/Beefalo_Gloom_Bell) | Done | craftable_items, dont_starve_together, from_beyond |
| [Beefalo Grooming Station](https://dontstarve.fandom.com/wiki/Beefalo_Grooming_Station) | Done | craftable_structures, decorations_filter, dont_starve_together |
| [Beefalo Hat](https://dontstarve.fandom.com/wiki/Beefalo_Hat) | Done | clothing_filter, craftable_items, equipable_items |
| [Beefalo Riding Filter](https://dontstarve.fandom.com/wiki/Beefalo_Riding_Filter) | Done | dont_starve_together |
| [Beefalo Treats](https://dontstarve.fandom.com/wiki/Beefalo_Treats) | Done | beefalo_foods, crock_pot_recipes, dont_starve_together |
| [Beefalo Wool](https://dontstarve.fandom.com/wiki/Beefalo_Wool) | Done | craftable_items, fuel |
| [Beefy Greens](https://dontstarve.fandom.com/wiki/Beefy_Greens) | Done | crock_pot_recipes, dont_starve_together, food |
| [Beekeeper Hat](https://dontstarve.fandom.com/wiki/Beekeeper_Hat) | Done | armour_filter, craftable_items, equipable_items |
| [Beeswax](https://dontstarve.fandom.com/wiki/Beeswax) | Done | craftable_items |
| [Belongings](https://dontstarve.fandom.com/wiki/Belongings) | Done | dont_starve_together |
| [Belt of Hunger](https://dontstarve.fandom.com/wiki/Belt_of_Hunger) | Done | craftable_items, equipable_items |
| [Benevolent Rabbit King](https://dontstarve.fandom.com/wiki/Benevolent_Rabbit_King) | Done | crafting_stations, dont_starve_together, from_beyond |
| [Bernie](https://dontstarve.fandom.com/wiki/Bernie) | Done | dont_starve_together, equipable_items |
| [Berries](https://dontstarve.fandom.com/wiki/Berries) | Done | food |
| [Berry Bush](https://dontstarve.fandom.com/wiki/Berry_Bush) | Done | fuel |
| [Billy](https://dontstarve.fandom.com/wiki/Billy) | Done | dont_starve_together, events |
| [Bio Data](https://dontstarve.fandom.com/wiki/Bio_Data) | Done | dont_starve_together |
| [Bio Scanalyzer](https://dontstarve.fandom.com/wiki/Bio_Scanalyzer) | Done | craftable_items, dont_starve_together |
| [Birchnut](https://dontstarve.fandom.com/wiki/Birchnut) | Done | dont_starve_together, food |
| [Birchnut Tree](https://dontstarve.fandom.com/wiki/Birchnut_Tree) | Done | dont_starve_together |
| [Birchnutter](https://dontstarve.fandom.com/wiki/Birchnutter) | Done | dont_starve_together |
| [Bird Trap](https://dontstarve.fandom.com/wiki/Bird_Trap) | Done | craftable_items, food_gardening_filter |
| [Birdcage](https://dontstarve.fandom.com/wiki/Birdcage) | Done | craftable_structures, food_gardening_filter |
| [Birds](https://dontstarve.fandom.com/wiki/Birds) | Done | a_new_reign, birds, flying_creatures |
| [Black Flag](https://dontstarve.fandom.com/wiki/Black_Flag) | Done | dont_starve_together |
| [Blood Shot](https://dontstarve.fandom.com/wiki/Blood_Shot) | Done | craftable_items, dont_starve_together |
| [Blue Cap](https://dontstarve.fandom.com/wiki/Blue_Cap) | Done | boss_dropped_items, food |
| [Blue Gem](https://dontstarve.fandom.com/wiki/Blue_Gem) | Done | boss_dropped_items, craftable_items |
| [Blueprint](https://dontstarve.fandom.com/wiki/Blueprint) | Done | a_new_reign, ancient_tier_1, boss_dropped_items, craftable_items, dont_starve_together, fuel |
| [Boards](https://dontstarve.fandom.com/wiki/Boards) | Done | craftable_items, fuel |
| [Boarilla](https://dontstarve.fandom.com/wiki/Boarilla) | Done | dont_starve_together, events |
| [Boat](https://dontstarve.fandom.com/wiki/Boat) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Boat Fragment](https://dontstarve.fandom.com/wiki/Boat_Fragment) | Done | dont_starve_together |
| [Boat Patch](https://dontstarve.fandom.com/wiki/Boat_Patch) | Done | craftable_items, dont_starve_together |
| [Bone Armor](https://dontstarve.fandom.com/wiki/Bone_Armor) | Done | a_new_reign, boss_dropped_items, dont_starve_together, equipable_items |
| [Bone Bouillon](https://dontstarve.fandom.com/wiki/Bone_Bouillon) | Done | dont_starve_together |
| [Bone Helm](https://dontstarve.fandom.com/wiki/Bone_Helm) | Done | a_new_reign, boss_dropped_items, dont_starve_together, equipable_items |
| [Bone Shards](https://dontstarve.fandom.com/wiki/Bone_Shards) | Done | craftable_items |
| [Bookcase](https://dontstarve.fandom.com/wiki/Bookcase) | Done | craftable_structures, dont_starve_together |
| [Boomerang](https://dontstarve.fandom.com/wiki/Boomerang) | Done | craftable_items, equipable_items, fight_tab |
| [Booster Shot](https://dontstarve.fandom.com/wiki/Booster_Shot) | Done | craftable_items, dont_starve_together |
| [Bootleg Getaway](https://dontstarve.fandom.com/wiki/Bootleg_Getaway) | Done | dont_starve_together |
| [Bottle Exchange Filter](https://dontstarve.fandom.com/wiki/Bottle_Exchange_Filter) | Done | dont_starve_together |
| [Boulder](https://dontstarve.fandom.com/wiki/Boulder) | Done | a_new_reign |
| [Bramble Husk](https://dontstarve.fandom.com/wiki/Bramble_Husk) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, fuel |
| [Bramble Trap](https://dontstarve.fandom.com/wiki/Bramble_Trap) | Done | craftable_items, dont_starve_together |
| [Brambleshade Armor](https://dontstarve.fandom.com/wiki/Brambleshade_Armor) | Done | craftable_items, dont_starve_together, from_beyond |
| [Breakfast Skillet](https://dontstarve.fandom.com/wiki/Breakfast_Skillet) | Done | crock_pot_recipes, dont_starve_together, food |
| [Breezy Vest](https://dontstarve.fandom.com/wiki/Breezy_Vest) | Done | craftable_items, equipable_items |
| [Briar Wolf](https://dontstarve.fandom.com/wiki/Briar_Wolf) | Done | dont_starve_together |
| [Bright-Eyed Frog](https://dontstarve.fandom.com/wiki/Bright-Eyed_Frog) | Done | animals, dont_starve_together, from_beyond |
| [Brightshade Armor](https://dontstarve.fandom.com/wiki/Brightshade_Armor) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond |
| [Brightshade Bomb](https://dontstarve.fandom.com/wiki/Brightshade_Bomb) | Done | craftable_items, dont_starve_together, from_beyond |
| [Brightshade Gestalt](https://dontstarve.fandom.com/wiki/Brightshade_Gestalt) | Done | dont_starve_together, from_beyond |
| [Brightshade Helm](https://dontstarve.fandom.com/wiki/Brightshade_Helm) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond |
| [Brightshade Husk](https://dontstarve.fandom.com/wiki/Brightshade_Husk) | Done | from_beyond |
| [Brightshade Shoevel](https://dontstarve.fandom.com/wiki/Brightshade_Shoevel) | Done | craftable_items, dont_starve_together, from_beyond |
| [Brightshade Smasher](https://dontstarve.fandom.com/wiki/Brightshade_Smasher) | Done | craftable_items, dont_starve_together, from_beyond |
| [Brightshade Staff](https://dontstarve.fandom.com/wiki/Brightshade_Staff) | Done | craftable_items, dont_starve_together, from_beyond |
| [Brightshade Sword](https://dontstarve.fandom.com/wiki/Brightshade_Sword) | Done | craftable_items, dont_starve_together, from_beyond |
| [Brightsmithy](https://dontstarve.fandom.com/wiki/Brightsmithy) | Done | celestial_filter, craftable_items, craftable_structures, crafting_stations, dont_starve_together, from_beyond |
| [Brightsmithy Filter](https://dontstarve.fandom.com/wiki/Brightsmithy_Filter) | Done | dont_starve_together |
| [Brilliant Mudslinger](https://dontstarve.fandom.com/wiki/Brilliant_Mudslinger) | Done | craftable_items, dont_starve_together |
| [Broken Machinery](https://dontstarve.fandom.com/wiki/Broken_Machinery) | Done | dont_starve_together |
| [Brush](https://dontstarve.fandom.com/wiki/Brush) | Done | a_new_reign, craftable_items, equipable_items |
| [Bucket-o-poop](https://dontstarve.fandom.com/wiki/Bucket-o-poop) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter, food_tab |
| [Bug Net](https://dontstarve.fandom.com/wiki/Bug_Net) | Done | craftable_items, equipable_items |
| [Bulbous Lightbug](https://dontstarve.fandom.com/wiki/Bulbous_Lightbug) | Done | animals, cave_creatures, dont_starve_together, followers |
| [Bull Kelp](https://dontstarve.fandom.com/wiki/Bull_Kelp) | Done | dont_starve_together, equipable_items, fuel |
| [Bumpers](https://dontstarve.fandom.com/wiki/Bumpers) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Bundling Wrap](https://dontstarve.fandom.com/wiki/Bundling_Wrap) | Done | containers, craftable_items, dont_starve_together, fuel |
| [Bunny Stew](https://dontstarve.fandom.com/wiki/Bunny_Stew) | Done | crock_pot_recipes, dont_starve_together, food |
| [Bunnyman](https://dontstarve.fandom.com/wiki/Bunnyman) | Done | animals, cave_creatures, followers |
| [Burrow](https://dontstarve.fandom.com/wiki/Burrow) | Done | dont_starve_together |
| [Burrowing Horn](https://dontstarve.fandom.com/wiki/Burrowing_Horn) | Done | craftable_items, dont_starve_together, equipable_items, from_beyond |
| [Bush Hat](https://dontstarve.fandom.com/wiki/Bush_Hat) | Done | craftable_items, equipable_items |
| [Butter Muffin](https://dontstarve.fandom.com/wiki/Butter_Muffin) | Done | crock_pot_recipes, food |
| [Butterfly](https://dontstarve.fandom.com/wiki/Butterfly) | Done | animals, flying_creatures |
| [Buzzard](https://dontstarve.fandom.com/wiki/Buzzard) | Done | animals, birds, dont_starve_together, flying_creatures |
| [Cachebox](https://dontstarve.fandom.com/wiki/Cachebox) | Done | dont_starve_together |
| [Cactus](https://dontstarve.fandom.com/wiki/Cactus) | Done | a_new_reign, dont_starve_together |
| [Cactus Flesh](https://dontstarve.fandom.com/wiki/Cactus_Flesh) | Done | dont_starve_together, food |
| [Cactus Flower](https://dontstarve.fandom.com/wiki/Cactus_Flower) | Done | dont_starve_together, food |
| [Calibrated Perceiver](https://dontstarve.fandom.com/wiki/Calibrated_Perceiver) | Done | dont_starve_together |
| [California Roll](https://dontstarve.fandom.com/wiki/California_Roll) | Done | crock_pot_recipes, dont_starve_together, food |
| [Campfire](https://dontstarve.fandom.com/wiki/Campfire) | Done | cooking_filter, craftable_structures |
| [Cannon](https://dontstarve.fandom.com/wiki/Cannon) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Cannonball](https://dontstarve.fandom.com/wiki/Cannonball) | Done | craftable_items, dont_starve_together |
| [Captain's Tricorn](https://dontstarve.fandom.com/wiki/Captain's_Tricorn) | Done | dont_starve_together, equipable_items |
| [Carpentry Filter](https://dontstarve.fandom.com/wiki/Carpentry_Filter) | Done | dont_starve_together, from_beyond |
| [Carpeted Flooring](https://dontstarve.fandom.com/wiki/Carpeted_Flooring) | Done | craftable_items, decorations_filter, fuel |
| [Carrat](https://dontstarve.fandom.com/wiki/Carrat) | Done | dont_starve_together |
| [Carrot](https://dontstarve.fandom.com/wiki/Carrot) | Done | dont_starve_together, food |
| [Cartographer's Desk](https://dontstarve.fandom.com/wiki/Cartographer's_Desk) | Done | a_new_reign, craftable_structures, crafting_stations, dont_starve_together |
| [Cartography Filter](https://dontstarve.fandom.com/wiki/Cartography_Filter) | Done | dont_starve_together |
| [Cat Cap](https://dontstarve.fandom.com/wiki/Cat_Cap) | Done | craftable_items, dont_starve_together, equipable_items |
| [Cat Tail](https://dontstarve.fandom.com/wiki/Cat_Tail) | Done | dont_starve_together |
| [Catcoon](https://dontstarve.fandom.com/wiki/Catcoon) | Done | animals, dont_starve_together, followers |
| [Cave Hole](https://dontstarve.fandom.com/wiki/Cave_Hole) | Done | a_new_reign, dont_starve_together |
| [Cave Rock Turf](https://dontstarve.fandom.com/wiki/Cave_Rock_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Cave Spider](https://dontstarve.fandom.com/wiki/Cave_Spider) | Done | cave_creatures, followers |
| [Cawnival Creation Filter](https://dontstarve.fandom.com/wiki/Cawnival_Creation_Filter) | Done | dont_starve_together |
| [Celestial Champion](https://dontstarve.fandom.com/wiki/Celestial_Champion) | Done | boss_monsters, dont_starve_together |
| [Celestial Filter](https://dontstarve.fandom.com/wiki/Celestial_Filter) | Done | dont_starve_together |
| [Celestial Fissure](https://dontstarve.fandom.com/wiki/Celestial_Fissure) | Done | dont_starve_together |
| [Celestial Orb](https://dontstarve.fandom.com/wiki/Celestial_Orb) | Done | crafting_stations, dont_starve_together |
| [Celestial Portal](https://dontstarve.fandom.com/wiki/Celestial_Portal) | Done | craftable_structures, dont_starve_together |
| [Ceviche](https://dontstarve.fandom.com/wiki/Ceviche) | Done | cooling, crock_pot_recipes, dont_starve_together, food |
| [Chairs](https://dontstarve.fandom.com/wiki/Chairs) | Done | dont_starve_together, from_beyond |
| [Charcoal](https://dontstarve.fandom.com/wiki/Charcoal) | Done | boss_dropped_items, fuel |
| [Charged Glassy Rock](https://dontstarve.fandom.com/wiki/Charged_Glassy_Rock) | Done | dont_starve_together |
| [Checkerboard Flooring](https://dontstarve.fandom.com/wiki/Checkerboard_Flooring) | Done | craftable_items, decorations_filter, fuel |
| [Chef Pouch](https://dontstarve.fandom.com/wiki/Chef_Pouch) | Done | backpacks, containers, cooking_filter, craftable_items, dont_starve_together, equipable_items |
| [Chess Pieces](https://dontstarve.fandom.com/wiki/Chess_Pieces) | Done | dont_starve_together |
| [Chest](https://dontstarve.fandom.com/wiki/Chest) | Done | containers, craftable_structures, dont_starve_together |
| [Chester](https://dontstarve.fandom.com/wiki/Chester) | Done | containers, followers |
| [Chili Flakes](https://dontstarve.fandom.com/wiki/Chili_Flakes) | Done | craftable_items, dont_starve_together |
| [Chilled Amulet](https://dontstarve.fandom.com/wiki/Chilled_Amulet) | Done | cooling, craftable_items, equipable_items |
| [Chilled Lavae](https://dontstarve.fandom.com/wiki/Chilled_Lavae) | Done | a_new_reign, dont_starve_together |
| [Circuit Extractor](https://dontstarve.fandom.com/wiki/Circuit_Extractor) | Done | craftable_items, dont_starve_together |
| [Circuits](https://dontstarve.fandom.com/wiki/Circuits) | Done | dont_starve_together, food_gardening_filter |
| [Clean Sweeper](https://dontstarve.fandom.com/wiki/Clean_Sweeper) | Done | craftable_items, decorations_filter, dont_starve_together, equipable_items |
| [Clever Disguise](https://dontstarve.fandom.com/wiki/Clever_Disguise) | Done | craftable_items, dont_starve_together, equipable_items |
| [Clockmaker's Tools](https://dontstarve.fandom.com/wiki/Clockmaker's_Tools) | Done | craftable_items, dont_starve_together |
| [Clocksmithy Tab](https://dontstarve.fandom.com/wiki/Clocksmithy_Tab) | Done | dont_starve_together |
| [Clockwork Bishop](https://dontstarve.fandom.com/wiki/Clockwork_Bishop) | Done | cave_creatures, clockwork_monsters, followers |
| [Clockwork Knight](https://dontstarve.fandom.com/wiki/Clockwork_Knight) | Done | clockwork_monsters, followers |
| [Clockwork Rook](https://dontstarve.fandom.com/wiki/Clockwork_Rook) | Done | clockwork_monsters, followers |
| [Clothing Filter](https://dontstarve.fandom.com/wiki/Clothing_Filter) | Done | dont_starve_together |
| [Clout Snout](https://dontstarve.fandom.com/wiki/Clout_Snout) | Done | dont_starve_together |
| [Coaching Whistle](https://dontstarve.fandom.com/wiki/Coaching_Whistle) | Done | craftable_items, dont_starve_together |
| [Coat of Carrots](https://dontstarve.fandom.com/wiki/Coat_of_Carrots) | Done | craftable_items, craftable_structures, dont_starve_together, equipable_items, from_beyond |
| [Cobblestones](https://dontstarve.fandom.com/wiki/Cobblestones) | Done | craftable_items, decorations_filter, dont_starve_together, fuel |
| [Codex Umbra](https://dontstarve.fandom.com/wiki/Codex_Umbra) | Done | craftable_items, crafting_stations, followers, fuel |
| [Codex Umbra Filter](https://dontstarve.fandom.com/wiki/Codex_Umbra_Filter) | Done | dont_starve_together |
| [Coin](https://dontstarve.fandom.com/wiki/Coin) | Done | dont_starve_together |
| [Collected Dust](https://dontstarve.fandom.com/wiki/Collected_Dust) | Done | craftable_items, dont_starve_together |
| [Commander's Helm](https://dontstarve.fandom.com/wiki/Commander's_Helm) | Done | armour_filter, craftable_items, dont_starve_together |
| [Communal Kelp Dish](https://dontstarve.fandom.com/wiki/Communal_Kelp_Dish) | Done | craftable_structures, dont_starve_together |
| [Compass](https://dontstarve.fandom.com/wiki/Compass) | Done | craftable_items, equipable_items |
| [Compendium](https://dontstarve.fandom.com/wiki/Compendium) | Done | dont_starve_together |
| [Compost](https://dontstarve.fandom.com/wiki/Compost) | Done | dont_starve_together, fertilizer |
| [Compost Wrap](https://dontstarve.fandom.com/wiki/Compost_Wrap) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter, fuel |
| [Composting Bin](https://dontstarve.fandom.com/wiki/Composting_Bin) | Done | craftable_structures, dont_starve_together, food_gardening_filter |
| [Don't Starve Together Commands](https://dontstarve.fandom.com/wiki/Console/Don't_Starve_Together_Commands) | Done | dont_starve_together |
| [Conspicuous Chest](https://dontstarve.fandom.com/wiki/Conspicuous_Chest) | Done | dont_starve_together |
| [Construction Amulet](https://dontstarve.fandom.com/wiki/Construction_Amulet) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items |
| [Cookbook](https://dontstarve.fandom.com/wiki/Cookbook) | Done | cooking_filter, craftable_items, dont_starve_together |
| [Cookie Cutter](https://dontstarve.fandom.com/wiki/Cookie_Cutter) | Done | dont_starve_together |
| [Cookie Cutter Cap](https://dontstarve.fandom.com/wiki/Cookie_Cutter_Cap) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items |
| [Cookie Cutter Shell](https://dontstarve.fandom.com/wiki/Cookie_Cutter_Shell) | Done | dont_starve_together |
| [Cooking Filter](https://dontstarve.fandom.com/wiki/Cooking_Filter) | Done | dont_starve_together |
| [Corn](https://dontstarve.fandom.com/wiki/Corn) | Done | food |
| [Costumes](https://dontstarve.fandom.com/wiki/Costumes) | Done | dont_starve_together |
| [Crab Guard](https://dontstarve.fandom.com/wiki/Crab_Guard) | Done | dont_starve_together |
| [Crab King](https://dontstarve.fandom.com/wiki/Crab_King) | Done | boss_monsters, dont_starve_together |
| [Crab Meat](https://dontstarve.fandom.com/wiki/Crab_Meat) | Done | dont_starve_together, events, food |
| [Crabby Hermit](https://dontstarve.fandom.com/wiki/Crabby_Hermit) | Done | crafting_stations, dont_starve_together |
| [Cracked Pillar](https://dontstarve.fandom.com/wiki/Cracked_Pillar) | Done | dont_starve_together |
| [Craftsmerm House](https://dontstarve.fandom.com/wiki/Craftsmerm_House) | Done | craftable_structures, dont_starve_together |
| [Cratered Moonrock](https://dontstarve.fandom.com/wiki/Cratered_Moonrock) | Done | a_new_reign, craftable_items, dont_starve_together |
| [Creamy Potato Purée](https://dontstarve.fandom.com/wiki/Creamy_Potato_Pur%C3%A9e) | Done | crock_pot_recipes, dont_starve_together, food |
| [Critters](https://dontstarve.fandom.com/wiki/Critters) | Done | a_new_reign, dont_starve_together, followers |
| [Critters Filter](https://dontstarve.fandom.com/wiki/Critters_Filter) | Done | dont_starve_together |
| [Crock Pot](https://dontstarve.fandom.com/wiki/Crock_Pot) | Done | containers, cooking_filter, craftable_structures, food_tab |
| [Crocommander](https://dontstarve.fandom.com/wiki/Crocommander) | Done | dont_starve_together, events |
| [Crumpled Package](https://dontstarve.fandom.com/wiki/Crumpled_Package) | Done | a_new_reign, dont_starve_together |
| [Crustashine](https://dontstarve.fandom.com/wiki/Crustashine) | Done | dont_starve_together |
| [Crystal Deerclops](https://dontstarve.fandom.com/wiki/Crystal_Deerclops) | Done | boss_monsters, dont_starve_together, from_beyond |
| [Cult of the Lamb Crossover](https://dontstarve.fandom.com/wiki/Cult_of_the_Lamb_Crossover) | Done | dont_starve_together |
| [Curio Cabinet](https://dontstarve.fandom.com/wiki/Curio_Cabinet) | Done | dont_starve_together |
| [Cut Grass](https://dontstarve.fandom.com/wiki/Cut_Grass) | Done | beefalo_foods, fuel |
| [Cut Reeds](https://dontstarve.fandom.com/wiki/Cut_Reeds) | Done | beefalo_foods, fuel |
| [Cut Stone](https://dontstarve.fandom.com/wiki/Cut_Stone) | Done | craftable_items |
| [Cutless](https://dontstarve.fandom.com/wiki/Cutless) | Done | dont_starve_together, equipable_items, fuel |
| [Dairy](https://dontstarve.fandom.com/wiki/Dairy) | Done | dont_starve_together |
| [Damaged Bishop](https://dontstarve.fandom.com/wiki/Damaged_Bishop) | Done | clockwork_monsters, followers |
| [Damaged Knight](https://dontstarve.fandom.com/wiki/Damaged_Knight) | Done | clockwork_monsters, followers |
| [Damaged Rook](https://dontstarve.fandom.com/wiki/Damaged_Rook) | Done | clockwork_monsters, followers |
| [Dangling Depth Dweller](https://dontstarve.fandom.com/wiki/Dangling_Depth_Dweller) | Done | cave_creatures, followers |
| [Dapper Vest](https://dontstarve.fandom.com/wiki/Dapper_Vest) | Done | craftable_items, equipable_items |
| [Dark Sword](https://dontstarve.fandom.com/wiki/Dark_Sword) | Done | boss_dropped_items, craftable_items, equipable_items |
| [Dark Tatters](https://dontstarve.fandom.com/wiki/Dark_Tatters) | Done | boss_dropped_items, dont_starve_together, from_beyond |
| [Dart](https://dontstarve.fandom.com/wiki/Dart) | Done | dont_starve_together |
| [Deadly Brightshade](https://dontstarve.fandom.com/wiki/Deadly_Brightshade) | Done | dont_starve_together, from_beyond |
| [Deciduous Forest](https://dontstarve.fandom.com/wiki/Deciduous_Forest) | Done | dont_starve_together |
| [Deciduous Turf](https://dontstarve.fandom.com/wiki/Deciduous_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, fuel |
| [Deck Illuminator](https://dontstarve.fandom.com/wiki/Deck_Illuminator) | Done | craftable_items, dont_starve_together |
| [Deconstruction Staff](https://dontstarve.fandom.com/wiki/Deconstruction_Staff) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items |
| [Decorations Filter](https://dontstarve.fandom.com/wiki/Decorations_Filter) | Done | dont_starve_together |
| [Deer Antler](https://dontstarve.fandom.com/wiki/Deer_Antler) | Done | a_new_reign, dont_starve_together |
| [Deerclops](https://dontstarve.fandom.com/wiki/Deerclops) | Done | boss_monsters |
| [Deerclops Eyeball](https://dontstarve.fandom.com/wiki/Deerclops_Eyeball) | Done | boss_dropped_items, food |
| [Den Decorating Set](https://dontstarve.fandom.com/wiki/Den_Decorating_Set) | Done | craftable_items, dont_starve_together |
| [Depths Worm](https://dontstarve.fandom.com/wiki/Depths_Worm) | Done | cave_creatures |
| [Desert](https://dontstarve.fandom.com/wiki/Desert) | Done | dont_starve_together |
| [Desert Stone](https://dontstarve.fandom.com/wiki/Desert_Stone) | Done | a_new_reign, boss_dropped_items, dont_starve_together |
| [Directional Sign](https://dontstarve.fandom.com/wiki/Directional_Sign) | Done | craftable_structures, decorations_filter, dont_starve_together |
| [Disease](https://dontstarve.fandom.com/wiki/Disease) | Done | dont_starve_together |
| [Dock Kit](https://dontstarve.fandom.com/wiki/Dock_Kit) | Done | craftable_items, decorations_filter, dont_starve_together |
| [Dock Piling Kit](https://dontstarve.fandom.com/wiki/Dock_Piling_Kit) | Done | craftable_items, decorations_filter, dont_starve_together |
| [Don't Starve Together](https://dontstarve.fandom.com/wiki/Don't_Starve_Together) | Done | dont_starve_together |
| [Doohickey](https://dontstarve.fandom.com/wiki/Doohickey) | Done | dont_starve_together |
| [Down Feather](https://dontstarve.fandom.com/wiki/Down_Feather) | Done | boss_dropped_items, dont_starve_together |
| [Dragon Fruit](https://dontstarve.fandom.com/wiki/Dragon_Fruit) | Done | food |
| [Dragonfly](https://dontstarve.fandom.com/wiki/Dragonfly) | Done | boss_monsters, dont_starve_together, flying_creatures |
| [Dragonpie](https://dontstarve.fandom.com/wiki/Dragonpie) | Done | crock_pot_recipes, food, fruits |
| [Dreaded Mudslinger](https://dontstarve.fandom.com/wiki/Dreaded_Mudslinger) | Done | craftable_items, dont_starve_together |
| [Dreadstone](https://dontstarve.fandom.com/wiki/Dreadstone) | Done | craftable_items, dont_starve_together, from_beyond |
| [Dreadstone Armor](https://dontstarve.fandom.com/wiki/Dreadstone_Armor) | Done | armour_filter, craftable_items, dont_starve_together |
| [Dreadstone Helm](https://dontstarve.fandom.com/wiki/Dreadstone_Helm) | Done | armour_filter, craftable_items, dont_starve_together |
| [Dreadstone Outcrop](https://dontstarve.fandom.com/wiki/Dreadstone_Outcrop) | Done | dont_starve_together, from_beyond |
| [Dreadstone Wall](https://dontstarve.fandom.com/wiki/Dreadstone_Wall) | Done | craftable_items, dont_starve_together |
| [Dried Kelp Fronds](https://dontstarve.fandom.com/wiki/Dried_Kelp_Fronds) | Done | dont_starve_together |
| [Driftwood](https://dontstarve.fandom.com/wiki/Driftwood) | Done | dont_starve_together |
| [Driftwood Piece](https://dontstarve.fandom.com/wiki/Driftwood_Piece) | Done | dont_starve_together, fuel |
| [Drumstick](https://dontstarve.fandom.com/wiki/Drumstick) | Done | boss_dropped_items, food |
| [Drying Rack](https://dontstarve.fandom.com/wiki/Drying_Rack) | Done | cooking_filter, craftable_structures, food_tab |
| [Dumbbells](https://dontstarve.fandom.com/wiki/Dumbbells) | Done | dont_starve_together |
| [Durian](https://dontstarve.fandom.com/wiki/Durian) | Done | food |
| [Dust Moth](https://dontstarve.fandom.com/wiki/Dust_Moth) | Done | animals, cave_creatures, dont_starve_together |
| [Ectoherbology Tab](https://dontstarve.fandom.com/wiki/Ectoherbology_Tab) | Done | dont_starve_together |
| [Eel](https://dontstarve.fandom.com/wiki/Eel) | Done | fishes, food |
| [Egg](https://dontstarve.fandom.com/wiki/Egg) | Done | eggs, food |
| [Eggplant](https://dontstarve.fandom.com/wiki/Eggplant) | Done | food |
| [Elastispacer](https://dontstarve.fandom.com/wiki/Elastispacer) | Done | craftable_items, dont_starve_together, from_beyond |
| [Elding Spear](https://dontstarve.fandom.com/wiki/Elding_Spear) | Done | craftable_items, dont_starve_together |
| [Electric Milk](https://dontstarve.fandom.com/wiki/Electric_Milk) | Done | dont_starve_together, food |
| [Electrical Doodad](https://dontstarve.fandom.com/wiki/Electrical_Doodad) | Done | craftable_items |
| [Embalming Spritz](https://dontstarve.fandom.com/wiki/Embalming_Spritz) | Done | craftable_items, dont_starve_together, from_beyond |
| [Emotes](https://dontstarve.fandom.com/wiki/Emotes) | Done | dont_starve_together |
| [Emoticons](https://dontstarve.fandom.com/wiki/Emoticons) | Done | dont_starve_together |
| [Empty Bottle](https://dontstarve.fandom.com/wiki/Empty_Bottle) | Done | craftable_items, dont_starve_together |
| [Empty Frame](https://dontstarve.fandom.com/wiki/Empty_Frame) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Endothermic Fire](https://dontstarve.fandom.com/wiki/Endothermic_Fire) | Done | cooling, craftable_structures, dont_starve_together |
| [Engineering Tab](https://dontstarve.fandom.com/wiki/Engineering_Tab) | Done | dont_starve_together |
| [Enlightened Crown](https://dontstarve.fandom.com/wiki/Enlightened_Crown) | Done | boss_dropped_items, dont_starve_together, equipable_items |
| [Enlightened Shard](https://dontstarve.fandom.com/wiki/Enlightened_Shard) | Done | dont_starve_together |
| [Enlightenment](https://dontstarve.fandom.com/wiki/Enlightenment) | Done | dont_starve_together |
| [Ethereal Embers](https://dontstarve.fandom.com/wiki/Ethereal_Embers) | Done | dont_starve_together |
| [Ewecus](https://dontstarve.fandom.com/wiki/Ewecus) | Done | animals |
| [Extra-Adorable Lavae](https://dontstarve.fandom.com/wiki/Extra-Adorable_Lavae) | Done | dont_starve_together, followers |
| [Eye Mask](https://dontstarve.fandom.com/wiki/Eye_Mask) | Done | boss_dropped_items, dont_starve_together, equipable_items |
| [Eye of Terror](https://dontstarve.fandom.com/wiki/Eye_of_Terror) | Done | boss_monsters, dont_starve_together |
| [Eyebrella](https://dontstarve.fandom.com/wiki/Eyebrella) | Done | cooling, craftable_items, dont_starve_together, equipable_items |
| [Fancy Spiralled Tubers](https://dontstarve.fandom.com/wiki/Fancy_Spiralled_Tubers) | Done | crock_pot_recipes, dont_starve_together, food |
| [Farm Plant](https://dontstarve.fandom.com/wiki/Farm_Plant) | Done | dont_starve_together |
| [Farm Soil](https://dontstarve.fandom.com/wiki/Farm_Soil) | Done | dont_starve_together |
| [Fashion Melon](https://dontstarve.fandom.com/wiki/Fashion_Melon) | Done | cooling, craftable_items, dont_starve_together, equipable_items |
| [Feather](https://dontstarve.fandom.com/wiki/Feather) | Done | a_new_reign, dont_starve_together, fuel |
| [Feather Hat](https://dontstarve.fandom.com/wiki/Feather_Hat) | Done | craftable_items, equipable_items |
| [Feather Pencil](https://dontstarve.fandom.com/wiki/Feather_Pencil) | Done | a_new_reign, craftable_items, decorations_filter |
| [Feathery Canvas](https://dontstarve.fandom.com/wiki/Feathery_Canvas) | Done | craftable_items, dont_starve_together |
| [Fencing Sword](https://dontstarve.fandom.com/wiki/Fencing_Sword) | Done | craftable_items, dont_starve_together |
| [Fertilizzzer](https://dontstarve.fandom.com/wiki/Fertilizzzer) | Done | craftable_items, dont_starve_together, fertilizer, from_beyond, fuel |
| [Fiery Pen](https://dontstarve.fandom.com/wiki/Fiery_Pen) | Done | dont_starve_together, equipable_items |
| [Fig](https://dontstarve.fandom.com/wiki/Fig) | Done | dont_starve_together, food, fruits |
| [Fig-Stuffed Trunk](https://dontstarve.fandom.com/wiki/Fig-Stuffed_Trunk) | Done | crock_pot_recipes, dont_starve_together, food |
| [Figatoni](https://dontstarve.fandom.com/wiki/Figatoni) | Done | craftable_items, crock_pot_recipes, dont_starve_together, food |
| [Figgy Frogwich](https://dontstarve.fandom.com/wiki/Figgy_Frogwich) | Done | crock_pot_recipes, dont_starve_together, food |
| [Figkabab](https://dontstarve.fandom.com/wiki/Figkabab) | Done | crock_pot_recipes, dont_starve_together, food |
| [Fire Nettle Fronds](https://dontstarve.fandom.com/wiki/Fire_Nettle_Fronds) | Done | dont_starve_together |
| [Fire Pump](https://dontstarve.fandom.com/wiki/Fire_Pump) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Fire Staff](https://dontstarve.fandom.com/wiki/Fire_Staff) | Done | craftable_items, equipable_items |
| [Fireflies](https://dontstarve.fandom.com/wiki/Fireflies) | Done | cave_creatures, fuel |
| [Fish](https://dontstarve.fandom.com/wiki/Fish) | Done | fishes, food |
| [Fish Cordon Bleu](https://dontstarve.fandom.com/wiki/Fish_Cordon_Bleu) | Done | dont_starve_together |
| [Fish Food](https://dontstarve.fandom.com/wiki/Fish_Food) | Done | craftable_items, dont_starve_together |
| [Fish Morsel](https://dontstarve.fandom.com/wiki/Fish_Morsel) | Done | dont_starve_together, fishes, food |
| [Fish Scale-O-Matic](https://dontstarve.fandom.com/wiki/Fish_Scale-O-Matic) | Done | craftable_structures, decorations_filter, dont_starve_together |
| [Fish Tacos](https://dontstarve.fandom.com/wiki/Fish_Tacos) | Done | crock_pot_recipes, food |
| [Fishing Filter](https://dontstarve.fandom.com/wiki/Fishing_Filter) | Done | dont_starve_together |
| [Fishing Rod](https://dontstarve.fandom.com/wiki/Fishing_Rod) | Done | craftable_items, equipable_items |
| [Fishing Tab](https://dontstarve.fandom.com/wiki/Fishing_Tab) | Done | dont_starve_together |
| [Fishsticks](https://dontstarve.fandom.com/wiki/Fishsticks) | Done | crock_pot_recipes, food |
| [Fist Full of Jam](https://dontstarve.fandom.com/wiki/Fist_Full_of_Jam) | Done | craftable_items, crock_pot_recipes, food |
| [Flare](https://dontstarve.fandom.com/wiki/Flare) | Done | craftable_items, dont_starve_together |
| [Fleshy Bulb](https://dontstarve.fandom.com/wiki/Fleshy_Bulb) | Done | craftable_items, fuel |
| [Flint](https://dontstarve.fandom.com/wiki/Flint) | Done | craftable_items |
| [Floating Lantern](https://dontstarve.fandom.com/wiki/Floating_Lantern) | Done | craftable_items, dont_starve_together |
| [Floats](https://dontstarve.fandom.com/wiki/Floats) | Done | dont_starve_together |
| [Floral Shirt](https://dontstarve.fandom.com/wiki/Floral_Shirt) | Done | cooling, craftable_items, dont_starve_together, equipable_items |
| [Florid Postern](https://dontstarve.fandom.com/wiki/Florid_Postern) | Done | dont_starve_together |
| [Flower](https://dontstarve.fandom.com/wiki/Flower) | Done | a_new_reign, dont_starve_together |
| [Flower Salad](https://dontstarve.fandom.com/wiki/Flower_Salad) | Done | crock_pot_recipes, dont_starve_together, food |
| [Food & Gardening Filter](https://dontstarve.fandom.com/wiki/Food_%26_Gardening_Filter) | Done | dont_starve_together |
| [Football Helmet](https://dontstarve.fandom.com/wiki/Football_Helmet) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Forest Turf](https://dontstarve.fandom.com/wiki/Forest_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Forge Portal](https://dontstarve.fandom.com/wiki/Forge_Portal) | Done | dont_starve_together, events |
| [Forget-Me-Lots](https://dontstarve.fandom.com/wiki/Forget-Me-Lots) | Done | dont_starve_together |
| [Forging Hammer](https://dontstarve.fandom.com/wiki/Forging_Hammer) | Done | dont_starve_together |
| [Fossils](https://dontstarve.fandom.com/wiki/Fossils) | Done | boss_dropped_items, dont_starve_together |
| [Fountain of Knowledge](https://dontstarve.fandom.com/wiki/Fountain_of_Knowledge) | Done | dont_starve_together |
| [Fresh Fruit Crepes](https://dontstarve.fandom.com/wiki/Fresh_Fruit_Crepes) | Done | dont_starve_together, food |
| [Friendly Fruit Fly Fruit](https://dontstarve.fandom.com/wiki/Friendly_Fruit_Fly_Fruit) | Done | boss_dropped_items, dont_starve_together, followers |
| [Friendly Scarecrow](https://dontstarve.fandom.com/wiki/Friendly_Scarecrow) | Done | a_new_reign, craftable_structures, dont_starve_together |
| [Frog](https://dontstarve.fandom.com/wiki/Frog) | Done | animals |
| [Frog Legs](https://dontstarve.fandom.com/wiki/Frog_Legs) | Done | boss_dropped_items, food |
| [Frog Rain](https://dontstarve.fandom.com/wiki/Frog_Rain) | Done | dont_starve_together |
| [Froggle Bunwich](https://dontstarve.fandom.com/wiki/Froggle_Bunwich) | Done | crock_pot_recipes |
| [From Beyond](https://dontstarve.fandom.com/wiki/From_Beyond) | Done | dont_starve_together, from_beyond |
| [Frostjaw](https://dontstarve.fandom.com/wiki/Frostjaw) | Done | boss_monsters, dont_starve_together |
| [Frozen Banana Daiquiri](https://dontstarve.fandom.com/wiki/Frozen_Banana_Daiquiri) | Done | cooling, crock_pot_recipes, dont_starve_together, food |
| [Fruit Medley](https://dontstarve.fandom.com/wiki/Fruit_Medley) | Done | cooling, crock_pot_recipes |
| [Funcap](https://dontstarve.fandom.com/wiki/Funcap) | Done | a_new_reign, clothing_filter, craftable_items, dont_starve_together, equipable_items |
| [Fungal Turf](https://dontstarve.fandom.com/wiki/Fungal_Turf) | Done | craftable_items, fuel |
| [Fur Tuft](https://dontstarve.fandom.com/wiki/Fur_Tuft) | Done | boss_dropped_items, dont_starve_together, fuel |
| [Fused Shadeling](https://dontstarve.fandom.com/wiki/Fused_Shadeling) | Done | dont_starve_together, from_beyond |
| [Garden Detritus](https://dontstarve.fandom.com/wiki/Garden_Detritus) | Done | dont_starve_together |
| [Garden Digamajig](https://dontstarve.fandom.com/wiki/Garden_Digamajig) | Done | craftable_items, dont_starve_together, food_gardening_filter |
| [Garden Hoe](https://dontstarve.fandom.com/wiki/Garden_Hoe) | Done | craftable_items, dont_starve_together, equipable_items, food_gardening_filter |
| [Gardeneer Hat](https://dontstarve.fandom.com/wiki/Gardeneer_Hat) | Done | ancient_tier_1, craftable_items, dont_starve_together, equipable_items, food_gardening_filter |
| [Garland](https://dontstarve.fandom.com/wiki/Garland) | Done | craftable_items, equipable_items |
| [Garlic](https://dontstarve.fandom.com/wiki/Garlic) | Done | dont_starve_together, events, food |
| [Garlic Powder](https://dontstarve.fandom.com/wiki/Garlic_Powder) | Done | craftable_items, dont_starve_together |
| [Gears](https://dontstarve.fandom.com/wiki/Gears) | Done | food |
| [Gem Deer](https://dontstarve.fandom.com/wiki/Gem_Deer) | Done | a_new_reign, animals, dont_starve_together |
| [Geode Fruit](https://dontstarve.fandom.com/wiki/Geode_Fruit) | Done | dont_starve_together, from_beyond |
| [Gestalt](https://dontstarve.fandom.com/wiki/Gestalt) | Done | dont_starve_together |
| [Ghost Characters](https://dontstarve.fandom.com/wiki/Ghost_Characters) | Done | dont_starve_together |
| [Ghostly Elixir](https://dontstarve.fandom.com/wiki/Ghostly_Elixir) | Done | dont_starve_together |
| [Giant Crops](https://dontstarve.fandom.com/wiki/Giant_Crops) | Done | dont_starve_together |
| [Gigantic Beehive](https://dontstarve.fandom.com/wiki/Gigantic_Beehive) | Done | a_new_reign, dont_starve_together |
| [Gizmo](https://dontstarve.fandom.com/wiki/Gizmo) | Done | dont_starve_together |
| [Glass Cutter](https://dontstarve.fandom.com/wiki/Glass_Cutter) | Done | celestial_filter, celestial_tab, craftable_items, dont_starve_together, equipable_items |
| [Glass Sculptures](https://dontstarve.fandom.com/wiki/Glass_Sculptures) | Done | a_new_reign, dont_starve_together |
| [Glommer](https://dontstarve.fandom.com/wiki/Glommer) | Done | animals, dont_starve_together, flying_creatures, followers |
| [Glommer's Flower](https://dontstarve.fandom.com/wiki/Glommer's_Flower) | Done | dont_starve_together, fuel |
| [Glommer's Goop](https://dontstarve.fandom.com/wiki/Glommer's_Goop) | Done | dont_starve_together, fertilizer, food, fuel |
| [Glommer's Statue](https://dontstarve.fandom.com/wiki/Glommer's_Statue) | Done | dont_starve_together |
| [Glommer's Wings](https://dontstarve.fandom.com/wiki/Glommer's_Wings) | Done | dont_starve_together, fuel |
| [Gloomerang](https://dontstarve.fandom.com/wiki/Gloomerang) | Done | craftable_items, dont_starve_together, equipable_items, from_beyond |
| [Gloomthorn](https://dontstarve.fandom.com/wiki/Gloomthorn) | Done | dont_starve_together, from_beyond |
| [Glow Berry](https://dontstarve.fandom.com/wiki/Glow_Berry) | Done | food, fruits |
| [Glow Berry Mousse](https://dontstarve.fandom.com/wiki/Glow_Berry_Mousse) | Done | craftable_items, dont_starve_together, food |
| [Gnarwail](https://dontstarve.fandom.com/wiki/Gnarwail) | Done | dont_starve_together |
| [Gnarwail Horn](https://dontstarve.fandom.com/wiki/Gnarwail_Horn) | Done | dont_starve_together |
| [Goat Milk](https://dontstarve.fandom.com/wiki/Goat_Milk) | Done | dont_starve_together, events |
| [Gobbler](https://dontstarve.fandom.com/wiki/Gobbler) | Done | animals, birds |
| [Goggles](https://dontstarve.fandom.com/wiki/Goggles) | Done | dont_starve_together |
| [Gold Flooring](https://dontstarve.fandom.com/wiki/Gold_Flooring) | Done | craftable_items, decorations_filter, dont_starve_together, fuel |
| [Gold Nugget](https://dontstarve.fandom.com/wiki/Gold_Nugget) | Done | boss_dropped_items, craftable_items |
| [Gourmet Salt Lick](https://dontstarve.fandom.com/wiki/Gourmet_Salt_Lick) | Done | craftable_structures, dont_starve_together, from_beyond |
| [Gramophone](https://dontstarve.fandom.com/wiki/Gramophone) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Grand Forge Boarrior](https://dontstarve.fandom.com/wiki/Grand_Forge_Boarrior) | Done | boss_monsters, dont_starve_together, events |
| [Grass Gator](https://dontstarve.fandom.com/wiki/Grass_Gator) | Done | animals, dont_starve_together |
| [Grass Gekko](https://dontstarve.fandom.com/wiki/Grass_Gekko) | Done | a_new_reign, dont_starve_together |
| [Grass Raft](https://dontstarve.fandom.com/wiki/Grass_Raft) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Grass Suit](https://dontstarve.fandom.com/wiki/Grass_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab, fuel |
| [Grass Tuft](https://dontstarve.fandom.com/wiki/Grass_Tuft) | Done | fuel |
| [Grass Turf](https://dontstarve.fandom.com/wiki/Grass_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Grazer](https://dontstarve.fandom.com/wiki/Grazer) | Done | dont_starve_together, from_beyond |
| [Great Depths Worm](https://dontstarve.fandom.com/wiki/Great_Depths_Worm) | Done | boss_monsters, cave_creatures, dont_starve_together, from_beyond |
| [Great Tree Trunk](https://dontstarve.fandom.com/wiki/Great_Tree_Trunk) | Done | dont_starve_together |
| [Green Cap](https://dontstarve.fandom.com/wiki/Green_Cap) | Done | boss_dropped_items, food |
| [Green Gem](https://dontstarve.fandom.com/wiki/Green_Gem) | Done | boss_dropped_items, craftable_items |
| [Grim Galette](https://dontstarve.fandom.com/wiki/Grim_Galette) | Done | dont_starve_together, food |
| [Growth Formula Starter](https://dontstarve.fandom.com/wiki/Growth_Formula_Starter) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter |
| [Grumble Bee](https://dontstarve.fandom.com/wiki/Grumble_Bee) | Done | a_new_reign, dont_starve_together, flying_creatures |
| [Guacamole](https://dontstarve.fandom.com/wiki/Guacamole) | Done | crock_pot_recipes, dont_starve_together, food |
| [Guano](https://dontstarve.fandom.com/wiki/Guano) | Done | fertilizer, fuel |
| [Guano Turf](https://dontstarve.fandom.com/wiki/Guano_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Guardian's Horn](https://dontstarve.fandom.com/wiki/Guardian's_Horn) | Done | boss_dropped_items, food |
| [Don’t Starve Together Dedicated Servers](https://dontstarve.fandom.com/wiki/Guides/Don%E2%80%99t_Starve_Together_Dedicated_Servers) | Done | dont_starve_together |
| [Gunpowder](https://dontstarve.fandom.com/wiki/Gunpowder) | Done | craftable_items |
| [Hallowed Nights](https://dontstarve.fandom.com/wiki/Hallowed_Nights) | Done | dont_starve_together, events |
| [Ham Bat](https://dontstarve.fandom.com/wiki/Ham_Bat) | Done | craftable_items, equipable_items, fight_tab |
| [Hammer](https://dontstarve.fandom.com/wiki/Hammer) | Done | craftable_items, equipable_items |
| [Handy Remote](https://dontstarve.fandom.com/wiki/Handy_Remote) | Done | craftable_items, dont_starve_together |
| [Hardwood Hat](https://dontstarve.fandom.com/wiki/Hardwood_Hat) | Done | armour_filter, craftable_items, dont_starve_together |
| [Hay Wall](https://dontstarve.fandom.com/wiki/Hay_Wall) | Done | craftable_items, craftable_structures, decorations_filter |
| [Healing Filter](https://dontstarve.fandom.com/wiki/Healing_Filter) | Done | dont_starve_together |
| [Healing Glop](https://dontstarve.fandom.com/wiki/Healing_Glop) | Done | craftable_items, dont_starve_together |
| [Healing Salve](https://dontstarve.fandom.com/wiki/Healing_Salve) | Done | craftable_items |
| [Hermit Home](https://dontstarve.fandom.com/wiki/Hermit_Home) | Done | craftable_structures, dont_starve_together |
| [Hermit Island](https://dontstarve.fandom.com/wiki/Hermit_Island) | Done | dont_starve_together |
| [Hibearnation Vest](https://dontstarve.fandom.com/wiki/Hibearnation_Vest) | Done | craftable_items, dont_starve_together, equipable_items |
| [Hollow Stump](https://dontstarve.fandom.com/wiki/Hollow_Stump) | Done | dont_starve_together |
| [Honey](https://dontstarve.fandom.com/wiki/Honey) | Done | boss_dropped_items, food |
| [Honey Crystals](https://dontstarve.fandom.com/wiki/Honey_Crystals) | Done | craftable_items, dont_starve_together |
| [Honey Ham](https://dontstarve.fandom.com/wiki/Honey_Ham) | Done | crock_pot_recipes, food |
| [Honey Nuggets](https://dontstarve.fandom.com/wiki/Honey_Nuggets) | Done | crock_pot_recipes |
| [Honey Poultice](https://dontstarve.fandom.com/wiki/Honey_Poultice) | Done | craftable_items |
| [Honeycomb](https://dontstarve.fandom.com/wiki/Honeycomb) | Done | boss_dropped_items |
| [Horizon Expandinator](https://dontstarve.fandom.com/wiki/Horizon_Expandinator) | Done | dont_starve_together, from_beyond |
| [Horror Hound](https://dontstarve.fandom.com/wiki/Horror_Hound) | Done | dont_starve_together |
| [Hostile Flare](https://dontstarve.fandom.com/wiki/Hostile_Flare) | Done | craftable_items, dont_starve_together |
| [Hot Dragon Chili Salad](https://dontstarve.fandom.com/wiki/Hot_Dragon_Chili_Salad) | Done | dont_starve_together |
| [Hot Spring](https://dontstarve.fandom.com/wiki/Hot_Spring) | Done | dont_starve_together |
| [Hound's Tooth](https://dontstarve.fandom.com/wiki/Hound's_Tooth) | Done | craftable_items |
| [Houndius Shootius](https://dontstarve.fandom.com/wiki/Houndius_Shootius) | Done | ancient_tab, craftable_items, craftable_structures |
| [Howlitzer](https://dontstarve.fandom.com/wiki/Howlitzer) | Done | craftable_items, dont_starve_together, equipable_items |
| [Humble Lamb Idol](https://dontstarve.fandom.com/wiki/Humble_Lamb_Idol) | Done | cooking_filter, craftable_structures, dont_starve_together |
| [Hutch](https://dontstarve.fandom.com/wiki/Hutch) | Done | cave_creatures, containers, dont_starve_together, followers |
| [Ice](https://dontstarve.fandom.com/wiki/Ice) | Done | cooling, food |
| [Ice Box](https://dontstarve.fandom.com/wiki/Ice_Box) | Done | containers, cooking_filter, craftable_structures, food_tab |
| [Ice Cream](https://dontstarve.fandom.com/wiki/Ice_Cream) | Done | cooling, craftable_items, crock_pot_recipes, dont_starve_together |
| [Ice Crystaleyezer](https://dontstarve.fandom.com/wiki/Ice_Crystaleyezer) | Done | cooling, craftable_items, craftable_structures, dont_starve_together, from_beyond |
| [Ice Cube](https://dontstarve.fandom.com/wiki/Ice_Cube) | Done | cooling, craftable_items, dont_starve_together, equipable_items |
| [Ice Fishing Hole](https://dontstarve.fandom.com/wiki/Ice_Fishing_Hole) | Done | dont_starve_together |
| [Ice Flingomatic](https://dontstarve.fandom.com/wiki/Ice_Flingomatic) | Done | craftable_structures, dont_starve_together |
| [Ice Floe](https://dontstarve.fandom.com/wiki/Ice_Floe) | Done | dont_starve_together, from_beyond |
| [Ice Spike](https://dontstarve.fandom.com/wiki/Ice_Spike) | Done | dont_starve_together |
| [Ice Staff](https://dontstarve.fandom.com/wiki/Ice_Staff) | Done | craftable_items, equipable_items |
| [Icker](https://dontstarve.fandom.com/wiki/Icker) | Done | cave_creatures, dont_starve_together, from_beyond |
| [Icker Jar](https://dontstarve.fandom.com/wiki/Icker_Jar) | Done | dont_starve_together, from_beyond |
| [Icker Preserve](https://dontstarve.fandom.com/wiki/Icker_Preserve) | Done | craftable_items, craftable_structures, dont_starve_together, from_beyond |
| [Infernal Swineclops](https://dontstarve.fandom.com/wiki/Infernal_Swineclops) | Done | boss_monsters, dont_starve_together, events |
| [Infused Moon Shard](https://dontstarve.fandom.com/wiki/Infused_Moon_Shard) | Done | boss_dropped_items, craftable_items, dont_starve_together |
| [Ink Blight](https://dontstarve.fandom.com/wiki/Ink_Blight) | Done | cave_creatures, dont_starve_together, from_beyond |
| [Insight](https://dontstarve.fandom.com/wiki/Insight) | Done | dont_starve_together |
| [Inspectacles](https://dontstarve.fandom.com/wiki/Inspectacles) | Done | clothing_filter, craftable_items, dont_starve_together |
| [Insulated Pack](https://dontstarve.fandom.com/wiki/Insulated_Pack) | Done | backpacks, containers, cooking_filter, craftable_items, dont_starve_together, equipable_items |
| [Inviting Formation](https://dontstarve.fandom.com/wiki/Inviting_Formation) | Done | dont_starve_together |
| [Iridescent Gem](https://dontstarve.fandom.com/wiki/Iridescent_Gem) | Done | a_new_reign, craftable_items, dont_starve_together |
| [Items Don't Starve Together](https://dontstarve.fandom.com/wiki/Items_Don't_Starve_Together) | Done | dont_starve_together |
| [Jelly Salad](https://dontstarve.fandom.com/wiki/Jelly_Salad) | Done | crock_pot_recipes, dont_starve_together |
| [Jellybeans](https://dontstarve.fandom.com/wiki/Jellybeans) | Done | a_new_reign, crock_pot_recipes, dont_starve_together, food |
| [Jerky](https://dontstarve.fandom.com/wiki/Jerky) | Done | craftable_items |
| [Juicy Berries](https://dontstarve.fandom.com/wiki/Juicy_Berries) | Done | a_new_reign, dont_starve_together, food, fruits |
| [Juicy Berry Bush](https://dontstarve.fandom.com/wiki/Juicy_Berry_Bush) | Done | a_new_reign, craftable_items, dont_starve_together, fuel |
| [Junk Pile](https://dontstarve.fandom.com/wiki/Junk_Pile) | Done | dont_starve_together, from_beyond |
| [Junk Yard](https://dontstarve.fandom.com/wiki/Junk_Yard) | Done | dont_starve_together, from_beyond |
| [Junky Fence](https://dontstarve.fandom.com/wiki/Junky_Fence) | Done | dont_starve_together, from_beyond |
| [Kabobs](https://dontstarve.fandom.com/wiki/Kabobs) | Done | craftable_items, crock_pot_recipes |
| [Kelp Fronds](https://dontstarve.fandom.com/wiki/Kelp_Fronds) | Done | dont_starve_together, food |
| [Kelp Patch](https://dontstarve.fandom.com/wiki/Kelp_Patch) | Done | craftable_items, dont_starve_together, from_beyond, fuel |
| [Key](https://dontstarve.fandom.com/wiki/Key) | Done | dont_starve_together, events |
| [King of the Merms](https://dontstarve.fandom.com/wiki/King_of_the_Merms) | Done | dont_starve_together |
| [Kitschy Idols](https://dontstarve.fandom.com/wiki/Kitschy_Idols) | Done | craftable_items, dont_starve_together |
| [Klaus](https://dontstarve.fandom.com/wiki/Klaus) | Done | a_new_reign, boss_monsters, dont_starve_together, events |
| [Knobbly Tree](https://dontstarve.fandom.com/wiki/Knobbly_Tree) | Done | dont_starve_together |
| [Knockback](https://dontstarve.fandom.com/wiki/Knockback) | Done | dont_starve_together |
| [Koalefant](https://dontstarve.fandom.com/wiki/Koalefant) | Done | animals |
| [Koalefant Carcass](https://dontstarve.fandom.com/wiki/Koalefant_Carcass) | Done | dont_starve_together |
| [Koalefant Trunk](https://dontstarve.fandom.com/wiki/Koalefant_Trunk) | Done | food |
| [Krampus](https://dontstarve.fandom.com/wiki/Krampus) | Done | dont_starve_together |
| [Krampus Sack](https://dontstarve.fandom.com/wiki/Krampus_Sack) | Done | backpacks, boss_dropped_items, containers |
| [Lake](https://dontstarve.fandom.com/wiki/Lake) | Done | a_new_reign, dont_starve_together |
| [Landscaping Tab](https://dontstarve.fandom.com/wiki/Landscaping_Tab) | Done | dont_starve_together |
| [Lantern](https://dontstarve.fandom.com/wiki/Lantern) | Done | craftable_items, equipable_items |
| [Lavae](https://dontstarve.fandom.com/wiki/Lavae) | Done | dont_starve_together |
| [Lavae Egg](https://dontstarve.fandom.com/wiki/Lavae_Egg) | Done | boss_dropped_items, dont_starve_together |
| [Lavae Tooth](https://dontstarve.fandom.com/wiki/Lavae_Tooth) | Done | dont_starve_together |
| [Leafy Meat](https://dontstarve.fandom.com/wiki/Leafy_Meat) | Done | food |
| [Leafy Meatloaf](https://dontstarve.fandom.com/wiki/Leafy_Meatloaf) | Done | crock_pot_recipes, dont_starve_together, food |
| [Lesser Glow Berry](https://dontstarve.fandom.com/wiki/Lesser_Glow_Berry) | Done | dont_starve_together, food, fruits |
| [Lichen](https://dontstarve.fandom.com/wiki/Lichen) | Done | food |
| [Lichen Meadow](https://dontstarve.fandom.com/wiki/Lichen_Meadow) | Done | dont_starve_together |
| [Life Giving Amulet](https://dontstarve.fandom.com/wiki/Life_Giving_Amulet) | Done | craftable_items, dont_starve_together, equipable_items |
| [Light Bulb](https://dontstarve.fandom.com/wiki/Light_Bulb) | Done | food, fuel |
| [Light Sources Filter](https://dontstarve.fandom.com/wiki/Light_Sources_Filter) | Done | dont_starve_together |
| [Lightning Conductor](https://dontstarve.fandom.com/wiki/Lightning_Conductor) | Done | craftable_items, dont_starve_together |
| [Lightning Rod](https://dontstarve.fandom.com/wiki/Lightning_Rod) | Done | craftable_structures |
| [Lil' Itchy](https://dontstarve.fandom.com/wiki/Lil'_Itchy) | Done | craftable_items, dont_starve_together |
| [Living Log](https://dontstarve.fandom.com/wiki/Living_Log) | Done | boss_dropped_items, craftable_items, fuel |
| [Log](https://dontstarve.fandom.com/wiki/Log) | Done | craftable_items, fuel |
| [Log Suit](https://dontstarve.fandom.com/wiki/Log_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab, fuel |
| [Loot Stash](https://dontstarve.fandom.com/wiki/Loot_Stash) | Done | a_new_reign, dont_starve_together, events |
| [Lord of the Fruit Flies](https://dontstarve.fandom.com/wiki/Lord_of_the_Fruit_Flies) | Done | boss_monsters, dont_starve_together |
| [Lost Scrapbook Page](https://dontstarve.fandom.com/wiki/Lost_Scrapbook_Page) | Done | dont_starve_together, from_beyond, fuel |
| [Loyal Merm Guard](https://dontstarve.fandom.com/wiki/Loyal_Merm_Guard) | Done | dont_starve_together, followers |
| [Lucky Beast](https://dontstarve.fandom.com/wiki/Lucky_Beast) | Done | craftable_items, dont_starve_together, equipable_items |
| [Lucky Gold Nugget](https://dontstarve.fandom.com/wiki/Lucky_Gold_Nugget) | Done | dont_starve_together |
| [Lucy the Axe](https://dontstarve.fandom.com/wiki/Lucy_the_Axe) | Done | equipable_items |
| [Lunar Aligned](https://dontstarve.fandom.com/wiki/Lunar_Aligned) | Done | dont_starve_together |
| [Lunar Altars](https://dontstarve.fandom.com/wiki/Lunar_Altars) | Done | crafting_stations, dont_starve_together |
| [Lunar Archipelago](https://dontstarve.fandom.com/wiki/Lunar_Archipelago) | Done | dont_starve_together |
| [Lunar Baths](https://dontstarve.fandom.com/wiki/Lunar_Baths) | Done | dont_starve_together |
| [Lunar Experiment](https://dontstarve.fandom.com/wiki/Lunar_Experiment) | Done | craftable_items, dont_starve_together, events, fuel |
| [Lunar Forest](https://dontstarve.fandom.com/wiki/Lunar_Forest) | Done | dont_starve_together |
| [Lunar Funcap](https://dontstarve.fandom.com/wiki/Lunar_Funcap) | Done | celestial_filter, craftable_items, dont_starve_together, equipable_items, from_beyond |
| [Lunar Grotto](https://dontstarve.fandom.com/wiki/Lunar_Grotto) | Done | dont_starve_together |
| [Lunar Hail](https://dontstarve.fandom.com/wiki/Lunar_Hail) | Done | dont_starve_together, from_beyond |
| [Lunar Island](https://dontstarve.fandom.com/wiki/Lunar_Island) | Done | dont_starve_together |
| [Lunar Mine](https://dontstarve.fandom.com/wiki/Lunar_Mine) | Done | dont_starve_together |
| [Lunar Mushtree](https://dontstarve.fandom.com/wiki/Lunar_Mushtree) | Done | dont_starve_together |
| [Lunar Siphonator](https://dontstarve.fandom.com/wiki/Lunar_Siphonator) | Done | craftable_structures, dont_starve_together |
| [Lunar Spore](https://dontstarve.fandom.com/wiki/Lunar_Spore) | Done | dont_starve_together |
| [Lunar Wobster](https://dontstarve.fandom.com/wiki/Lunar_Wobster) | Done | dont_starve_together |
| [Lune Tree](https://dontstarve.fandom.com/wiki/Lune_Tree) | Done | dont_starve_together |
| [Lune Tree Blossom](https://dontstarve.fandom.com/wiki/Lune_Tree_Blossom) | Done | dont_starve_together, food |
| [Lures](https://dontstarve.fandom.com/wiki/Lures) | Done | dont_starve_together |
| [Lurking Nightmare](https://dontstarve.fandom.com/wiki/Lurking_Nightmare) | Done | cave_creatures, dont_starve_together, from_beyond |
| [Lush Carpet](https://dontstarve.fandom.com/wiki/Lush_Carpet) | Done | craftable_items, dont_starve_together |
| [Luxury Fan](https://dontstarve.fandom.com/wiki/Luxury_Fan) | Done | cooling, craftable_items, dont_starve_together |
| [Magician's Chest](https://dontstarve.fandom.com/wiki/Magician's_Chest) | Done | craftable_structures, dont_starve_together |
| [Magician's Top Hat](https://dontstarve.fandom.com/wiki/Magician's_Top_Hat) | Done | craftable_items, dont_starve_together |
| [Magiluminescence](https://dontstarve.fandom.com/wiki/Magiluminescence) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items |
| [Magma](https://dontstarve.fandom.com/wiki/Magma) | Done | dont_starve_together |
| [Magma Golem](https://dontstarve.fandom.com/wiki/Magma_Golem) | Done | dont_starve_together, events, followers |
| [Malbatross](https://dontstarve.fandom.com/wiki/Malbatross) | Done | birds, boss_monsters, dont_starve_together, flying_creatures |
| [Malbatross Bill](https://dontstarve.fandom.com/wiki/Malbatross_Bill) | Done | boss_dropped_items, dont_starve_together, equipable_items |
| [Malbatross Feather](https://dontstarve.fandom.com/wiki/Malbatross_Feather) | Done | boss_dropped_items, dont_starve_together, fuel |
| [Mandrake](https://dontstarve.fandom.com/wiki/Mandrake) | Done | followers, food |
| [Mandrake Soup](https://dontstarve.fandom.com/wiki/Mandrake_Soup) | Done | craftable_items, crock_pot_recipes, food |
| [Mannequin](https://dontstarve.fandom.com/wiki/Mannequin) | Done | craftable_structures, dont_starve_together |
| [Manure](https://dontstarve.fandom.com/wiki/Manure) | Done | craftable_items, fertilizer, fuel |
| [Map Scroll](https://dontstarve.fandom.com/wiki/Map_Scroll) | Done | a_new_reign, craftable_items, dont_starve_together |
| [Marble](https://dontstarve.fandom.com/wiki/Marble) | Done | craftable_items |
| [Marble Bean](https://dontstarve.fandom.com/wiki/Marble_Bean) | Done | a_new_reign, craftable_items, dont_starve_together |
| [Marble Sculptures](https://dontstarve.fandom.com/wiki/Marble_Sculptures) | Done | a_new_reign, dont_starve_together |
| [Marble Shrub](https://dontstarve.fandom.com/wiki/Marble_Shrub) | Done | a_new_reign, dont_starve_together |
| [Marble Statues](https://dontstarve.fandom.com/wiki/Marble_Statues) | Done | a_new_reign, dont_starve_together |
| [Marble Suit](https://dontstarve.fandom.com/wiki/Marble_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Marotter](https://dontstarve.fandom.com/wiki/Marotter) | Done | dont_starve_together, from_beyond |
| [Marotter Den](https://dontstarve.fandom.com/wiki/Marotter_Den) | Done | dont_starve_together, from_beyond |
| [Marsh Turf](https://dontstarve.fandom.com/wiki/Marsh_Turf) | Done | craftable_items, fuel |
| [Mast](https://dontstarve.fandom.com/wiki/Mast) | Done | craftable_items, dont_starve_together |
| [Maxwell Statue](https://dontstarve.fandom.com/wiki/Maxwell_Statue) | Done | dont_starve_together |
| [Mealing Stone](https://dontstarve.fandom.com/wiki/Mealing_Stone) | Done | dont_starve_together, events |
| [Meat](https://dontstarve.fandom.com/wiki/Meat) | Done | boss_dropped_items, food |
| [Meat Effigy](https://dontstarve.fandom.com/wiki/Meat_Effigy) | Done | craftable_structures |
| [Meatballs](https://dontstarve.fandom.com/wiki/Meatballs) | Done | crock_pot_recipes, food |
| [Meaty Stew](https://dontstarve.fandom.com/wiki/Meaty_Stew) | Done | craftable_items, crock_pot_recipes |
| [Melonsicle](https://dontstarve.fandom.com/wiki/Melonsicle) | Done | cooling, crock_pot_recipes, dont_starve_together, food, fruits |
| [Merm](https://dontstarve.fandom.com/wiki/Merm) | Done | followers |
| [Merm Flort-ifications](https://dontstarve.fandom.com/wiki/Merm_Flort-ifications) | Done | craftable_structures, dont_starve_together |
| [Message in a Bottle](https://dontstarve.fandom.com/wiki/Message_in_a_Bottle) | Done | dont_starve_together |
| [Meteor](https://dontstarve.fandom.com/wiki/Meteor) | Done | dont_starve_together |
| [Miasma](https://dontstarve.fandom.com/wiki/Miasma) | Done | dont_starve_together, from_beyond |
| [Midsummer Cawnival](https://dontstarve.fandom.com/wiki/Midsummer_Cawnival) | Done | dont_starve_together, events |
| [Prize Booth](https://dontstarve.fandom.com/wiki/Midsummer_Cawnival/Prize_Booth) | Done | events |
| [Mighty Gym](https://dontstarve.fandom.com/wiki/Mighty_Gym) | Done | craftable_structures, dont_starve_together |
| [Milkmade Hat](https://dontstarve.fandom.com/wiki/Milkmade_Hat) | Done | crock_pot_recipes, dont_starve_together, equipable_items, food |
| [Milky Whites](https://dontstarve.fandom.com/wiki/Milky_Whites) | Done | boss_dropped_items, dont_starve_together |
| [Mimicreep](https://dontstarve.fandom.com/wiki/Mimicreep) | Done | cave_creatures, dont_starve_together, from_beyond |
| [Miner Hat](https://dontstarve.fandom.com/wiki/Miner_Hat) | Done | craftable_items, equipable_items |
| [Mini Glacier](https://dontstarve.fandom.com/wiki/Mini_Glacier) | Done | dont_starve_together |
| [Mini Sign](https://dontstarve.fandom.com/wiki/Mini_Sign) | Done | a_new_reign, craftable_items, craftable_structures, decorations_filter, fuel |
| [Misshapen Bird](https://dontstarve.fandom.com/wiki/Misshapen_Bird) | Done | birds, dont_starve_together |
| [Moggles](https://dontstarve.fandom.com/wiki/Moggles) | Done | craftable_items, dont_starve_together, equipable_items |
| [Moleworm](https://dontstarve.fandom.com/wiki/Moleworm) | Done | animals, cave_creatures, dont_starve_together |
| [Monkey Hut](https://dontstarve.fandom.com/wiki/Monkey_Hut) | Done | dont_starve_together |
| [Monkeytails](https://dontstarve.fandom.com/wiki/Monkeytails) | Done | dont_starve_together |
| [Monster Jerky](https://dontstarve.fandom.com/wiki/Monster_Jerky) | Done | craftable_items, food |
| [Monster Lasagna](https://dontstarve.fandom.com/wiki/Monster_Lasagna) | Done | crock_pot_recipes |
| [Monster Meat](https://dontstarve.fandom.com/wiki/Monster_Meat) | Done | boss_dropped_items, food |
| [Monster Tartare](https://dontstarve.fandom.com/wiki/Monster_Tartare) | Done | dont_starve_together, food |
| [Moon Caller's Staff](https://dontstarve.fandom.com/wiki/Moon_Caller's_Staff) | Done | a_new_reign, cooling, dont_starve_together, equipable_items |
| [Moon Crater Turf](https://dontstarve.fandom.com/wiki/Moon_Crater_Turf) | Done | celestial_tab, craftable_items, dont_starve_together, fuel |
| [Moon Dial](https://dontstarve.fandom.com/wiki/Moon_Dial) | Done | a_new_reign, craftable_structures, dont_starve_together |
| [Moon Glass](https://dontstarve.fandom.com/wiki/Moon_Glass) | Done | dont_starve_together |
| [Moon Glass Mound](https://dontstarve.fandom.com/wiki/Moon_Glass_Mound) | Done | dont_starve_together |
| [Moon Glass Saw Blade](https://dontstarve.fandom.com/wiki/Moon_Glass_Saw_Blade) | Done | celestial_filter, craftable_items, dont_starve_together, from_beyond |
| [Moon Moth](https://dontstarve.fandom.com/wiki/Moon_Moth) | Done | dont_starve_together |
| [Moon Moth Wings](https://dontstarve.fandom.com/wiki/Moon_Moth_Wings) | Done | dont_starve_together |
| [Moon Quay](https://dontstarve.fandom.com/wiki/Moon_Quay) | Done | dont_starve_together |
| [Moon Quay Beach Turf](https://dontstarve.fandom.com/wiki/Moon_Quay_Beach_Turf) | Done | craftable_items, decorations_filter, dont_starve_together |
| [Moon Quay Pirate Banner](https://dontstarve.fandom.com/wiki/Moon_Quay_Pirate_Banner) | Done | craftable_structures, decorations_filter, dont_starve_together |
| [Moon Rock](https://dontstarve.fandom.com/wiki/Moon_Rock) | Done | a_new_reign, boss_dropped_items, craftable_items, dont_starve_together |
| [Moon Rock Idol](https://dontstarve.fandom.com/wiki/Moon_Rock_Idol) | Done | celestial_tab, craftable_items, dont_starve_together |
| [Moon Rock Wall](https://dontstarve.fandom.com/wiki/Moon_Rock_Wall) | Done | craftable_items, dont_starve_together |
| [Moon Shard](https://dontstarve.fandom.com/wiki/Moon_Shard) | Done | boss_dropped_items, dont_starve_together |
| [Moon Shroom](https://dontstarve.fandom.com/wiki/Moon_Shroom) | Done | dont_starve_together, food |
| [Moon Stone](https://dontstarve.fandom.com/wiki/Moon_Stone) | Done | a_new_reign, dont_starve_together |
| [Moonblind Crow](https://dontstarve.fandom.com/wiki/Moonblind_Crow) | Done | dont_starve_together |
| [Moongleam](https://dontstarve.fandom.com/wiki/Moongleam) | Done | dont_starve_together |
| [Moonlens](https://dontstarve.fandom.com/wiki/Moonlens) | Done | a_new_reign, craftable_items, dont_starve_together |
| [Moonrock Pengull](https://dontstarve.fandom.com/wiki/Moonrock_Pengull) | Done | dont_starve_together |
| [Moonstorm](https://dontstarve.fandom.com/wiki/Moonstorm) | Done | dont_starve_together |
| [Goose](https://dontstarve.fandom.com/wiki/Moose/Goose) | Done | birds, boss_monsters, dont_starve_together |
| [Goose Egg](https://dontstarve.fandom.com/wiki/Moose/Goose_Egg) | Done | dont_starve_together, eggs |
| [Moqueca](https://dontstarve.fandom.com/wiki/Moqueca) | Done | dont_starve_together |
| [Morning Star](https://dontstarve.fandom.com/wiki/Morning_Star) | Done | craftable_items, dont_starve_together, equipable_items, fight_tab |
| [Morsel](https://dontstarve.fandom.com/wiki/Morsel) | Done | food |
| [Mosaic Flooring](https://dontstarve.fandom.com/wiki/Mosaic_Flooring) | Done | craftable_items, dont_starve_together |
| [Mosling](https://dontstarve.fandom.com/wiki/Mosling) | Done | animals, birds, dont_starve_together |
| [Mosquito](https://dontstarve.fandom.com/wiki/Mosquito) | Done | animals, flying_creatures |
| [Mossy Vine](https://dontstarve.fandom.com/wiki/Mossy_Vine) | Done | dont_starve_together |
| [Mourning Glory](https://dontstarve.fandom.com/wiki/Mourning_Glory) | Done | dont_starve_together |
| [Mud Biome](https://dontstarve.fandom.com/wiki/Mud_Biome) | Done | dont_starve_together |
| [Mud Turf](https://dontstarve.fandom.com/wiki/Mud_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Mumsy](https://dontstarve.fandom.com/wiki/Mumsy) | Done | dont_starve_together, events |
| [Mush Gnome](https://dontstarve.fandom.com/wiki/Mush_Gnome) | Done | cave_creatures, dont_starve_together |
| [Mushroom Lights](https://dontstarve.fandom.com/wiki/Mushroom_Lights) | Done | dont_starve_together |
| [Mushroom Planter](https://dontstarve.fandom.com/wiki/Mushroom_Planter) | Done | a_new_reign, craftable_structures, dont_starve_together, food_gardening_filter, food_tab |
| [Mushroom Spore](https://dontstarve.fandom.com/wiki/Mushroom_Spore) | Done | a_new_reign, dont_starve_together |
| [Mushrooms](https://dontstarve.fandom.com/wiki/Mushrooms) | Done | boss_dropped_items |
| [Mushtree](https://dontstarve.fandom.com/wiki/Mushtree) | Done | dont_starve_together |
| [Mushy Cake](https://dontstarve.fandom.com/wiki/Mushy_Cake) | Done | crock_pot_recipes, dont_starve_together, food |
| [Mutated Fungal Turf](https://dontstarve.fandom.com/wiki/Mutated_Fungal_Turf) | Done | celestial_tab, craftable_items, dont_starve_together |
| [Mutated Merm](https://dontstarve.fandom.com/wiki/Mutated_Merm) | Done | dont_starve_together, followers |
| [Mysterious Energy](https://dontstarve.fandom.com/wiki/Mysterious_Energy) | Done | dont_starve_together |
| [Mysterious Plant](https://dontstarve.fandom.com/wiki/Mysterious_Plant) | Done | dont_starve_together |
| [Naked Mole Bat](https://dontstarve.fandom.com/wiki/Naked_Mole_Bat) | Done | cave_creatures, dont_starve_together |
| [Naked Mole Bat Burrow](https://dontstarve.fandom.com/wiki/Naked_Mole_Bat_Burrow) | Done | dont_starve_together |
| [Naked Nostrils](https://dontstarve.fandom.com/wiki/Naked_Nostrils) | Done | dont_starve_together, food |
| [Napsack](https://dontstarve.fandom.com/wiki/Napsack) | Done | a_new_reign, craftable_items, dont_starve_together, equipable_items |
| [Nautopilot](https://dontstarve.fandom.com/wiki/Nautopilot) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Night Armor](https://dontstarve.fandom.com/wiki/Night_Armor) | Done | armour_filter, boss_dropped_items, craftable_items, equipable_items |
| [Night Light](https://dontstarve.fandom.com/wiki/Night_Light) | Done | craftable_structures |
| [Nightberry](https://dontstarve.fandom.com/wiki/Nightberry) | Done | dont_starve_together, food, from_beyond |
| [Nightmare Amulet](https://dontstarve.fandom.com/wiki/Nightmare_Amulet) | Done | craftable_items, equipable_items |
| [Nightmare Fuel](https://dontstarve.fandom.com/wiki/Nightmare_Fuel) | Done | boss_dropped_items, craftable_items, fuel |
| [Nightmare Light](https://dontstarve.fandom.com/wiki/Nightmare_Light) | Done | dont_starve_together |
| [Nightmare Saddle](https://dontstarve.fandom.com/wiki/Nightmare_Saddle) | Done | craftable_items, dont_starve_together, from_beyond |
| [Nightmare Werepig](https://dontstarve.fandom.com/wiki/Nightmare_Werepig) | Done | boss_monsters, dont_starve_together |
| [Nitre](https://dontstarve.fandom.com/wiki/Nitre) | Done | craftable_items, fuel |
| [Nitre Formation](https://dontstarve.fandom.com/wiki/Nitre_Formation) | Done | dont_starve_together, from_beyond |
| [No-Eyed Deer](https://dontstarve.fandom.com/wiki/No-Eyed_Deer) | Done | a_new_reign, animals, dont_starve_together |
| [Nurse Spider](https://dontstarve.fandom.com/wiki/Nurse_Spider) | Done | dont_starve_together, followers |
| [Nutrient](https://dontstarve.fandom.com/wiki/Nutrient) | Done | dont_starve_together |
| [Oar](https://dontstarve.fandom.com/wiki/Oar) | Done | craftable_items, dont_starve_together, equipable_items, fuel |
| [Ocean Debris](https://dontstarve.fandom.com/wiki/Ocean_Debris) | Done | dont_starve_together |
| [Ocean Fishes](https://dontstarve.fandom.com/wiki/Ocean_Fishes) | Done | dont_starve_together |
| [Ocean Trawler Kit](https://dontstarve.fandom.com/wiki/Ocean_Trawler_Kit) | Done | craftable_items, dont_starve_together, food_gardening_filter |
| [Ocuvigil](https://dontstarve.fandom.com/wiki/Ocuvigil) | Done | a_new_reign, craftable_structures, dont_starve_together |
| [Offerings Filter](https://dontstarve.fandom.com/wiki/Offerings_Filter) | Done | dont_starve_together |
| [Old Beefalo](https://dontstarve.fandom.com/wiki/Old_Beefalo) | Done | dont_starve_together, events |
| [One-man Band](https://dontstarve.fandom.com/wiki/One-man_Band) | Done | craftable_items, equipable_items, food_gardening_filter |
| [Onion](https://dontstarve.fandom.com/wiki/Onion) | Done | dont_starve_together, events, food |
| [Orange Gem](https://dontstarve.fandom.com/wiki/Orange_Gem) | Done | boss_dropped_items, craftable_items |
| [Ornate Chest](https://dontstarve.fandom.com/wiki/Ornate_Chest) | Done | boss_dropped_items, containers |
| [Ornery Chest](https://dontstarve.fandom.com/wiki/Ornery_Chest) | Done | dont_starve_together |
| [Overheating](https://dontstarve.fandom.com/wiki/Overheating) | Done | dont_starve_together |
| [Packet of Seeds](https://dontstarve.fandom.com/wiki/Packet_of_Seeds) | Done | dont_starve_together, events |
| [Palmcone Scale](https://dontstarve.fandom.com/wiki/Palmcone_Scale) | Done | dont_starve_together |
| [Palmcone Sprout](https://dontstarve.fandom.com/wiki/Palmcone_Sprout) | Done | dont_starve_together |
| [Palmcone Tree](https://dontstarve.fandom.com/wiki/Palmcone_Tree) | Done | dont_starve_together |
| [Pan Flute](https://dontstarve.fandom.com/wiki/Pan_Flute) | Done | craftable_items |
| [Papyrus](https://dontstarve.fandom.com/wiki/Papyrus) | Done | craftable_items, fuel |
| [Parasitic Shadeling](https://dontstarve.fandom.com/wiki/Parasitic_Shadeling) | Done | dont_starve_together |
| [Parrot Pirate](https://dontstarve.fandom.com/wiki/Parrot_Pirate) | Done | animals, birds, flying_creatures |
| [Pearl's Pearl](https://dontstarve.fandom.com/wiki/Pearl's_Pearl) | Done | boss_dropped_items, dont_starve_together |
| [Pebble Crab](https://dontstarve.fandom.com/wiki/Pebble_Crab) | Done | dont_starve_together, events |
| [Pengull](https://dontstarve.fandom.com/wiki/Pengull) | Done | animals, birds |
| [Pepper](https://dontstarve.fandom.com/wiki/Pepper) | Done | dont_starve_together, food |
| [Petals](https://dontstarve.fandom.com/wiki/Petals) | Done | a_new_reign, dont_starve_together, fuel |
| [Petrified Tree](https://dontstarve.fandom.com/wiki/Petrified_Tree) | Done | a_new_reign, dont_starve_together |
| [Phasmo-Encapsulator](https://dontstarve.fandom.com/wiki/Phasmo-Encapsulator) | Done | craftable_items |
| [Phlegm](https://dontstarve.fandom.com/wiki/Phlegm) | Done | a_new_reign, dont_starve_together, food |
| [Phobic Experiment](https://dontstarve.fandom.com/wiki/Phobic_Experiment) | Done | craftable_items, dont_starve_together, events, fuel |
| [Axe](https://dontstarve.fandom.com/wiki/Pick/Axe) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items |
| [Pickaxe](https://dontstarve.fandom.com/wiki/Pickaxe) | Done | craftable_items, equipable_items |
| [Pierogi](https://dontstarve.fandom.com/wiki/Pierogi) | Done | crock_pot_recipes, food |
| [Pig](https://dontstarve.fandom.com/wiki/Pig) | Done | animals, followers |
| [Pig House](https://dontstarve.fandom.com/wiki/Pig_House) | Done | craftable_structures |
| [Piggyback](https://dontstarve.fandom.com/wiki/Piggyback) | Done | backpacks, clothing_filter, containers, craftable_items, equipable_items |
| [Pile o' Balloons](https://dontstarve.fandom.com/wiki/Pile_o'_Balloons) | Done | craftable_items |
| [Pillars](https://dontstarve.fandom.com/wiki/Pillars) | Done | a_new_reign, dont_starve_together |
| [Pinchin' Winch](https://dontstarve.fandom.com/wiki/Pinchin'_Winch) | Done | craftable_structures, dont_starve_together |
| [Pine Cone](https://dontstarve.fandom.com/wiki/Pine_Cone) | Done | fuel |
| [Pinetree Pioneer Hat](https://dontstarve.fandom.com/wiki/Pinetree_Pioneer_Hat) | Done | craftable_items, dont_starve_together, equipable_items |
| [Pipspook](https://dontstarve.fandom.com/wiki/Pipspook) | Done | dont_starve_together, followers |
| [Pipton](https://dontstarve.fandom.com/wiki/Pipton) | Done | dont_starve_together, events |
| [Pirate Map](https://dontstarve.fandom.com/wiki/Pirate_Map) | Done | dont_starve_together |
| [Pirate Raid](https://dontstarve.fandom.com/wiki/Pirate_Raid) | Done | dont_starve_together |
| [Pirate Sloop](https://dontstarve.fandom.com/wiki/Pirate_Sloop) | Done | dont_starve_together |
| [Pirate's Bandana](https://dontstarve.fandom.com/wiki/Pirate's_Bandana) | Done | dont_starve_together |
| [Pit Pig](https://dontstarve.fandom.com/wiki/Pit_Pig) | Done | dont_starve_together, events |
| [Pitchfork](https://dontstarve.fandom.com/wiki/Pitchfork) | Done | craftable_items, dont_starve_together, equipable_items |
| [Plain Omelette](https://dontstarve.fandom.com/wiki/Plain_Omelette) | Done | crock_pot_recipes, dont_starve_together, eggs, food |
| [Planar Entity Protection](https://dontstarve.fandom.com/wiki/Planar_Entity_Protection) | Done | dont_starve_together, from_beyond |
| [Pleasant Portrait](https://dontstarve.fandom.com/wiki/Pleasant_Portrait) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Plugged Fissure](https://dontstarve.fandom.com/wiki/Plugged_Fissure) | Done | dont_starve_together |
| [Pocket Scale](https://dontstarve.fandom.com/wiki/Pocket_Scale) | Done | craftable_items, dont_starve_together, equipable_items |
| [Polar Bearger Bin](https://dontstarve.fandom.com/wiki/Polar_Bearger_Bin) | Done | containers, craftable_items, dont_starve_together, from_beyond |
| [Polly Roger's Hat](https://dontstarve.fandom.com/wiki/Polly_Roger's_Hat) | Done | craftable_items, dont_starve_together |
| [Pomegranate](https://dontstarve.fandom.com/wiki/Pomegranate) | Done | food |
| [Portable Crock Pot](https://dontstarve.fandom.com/wiki/Portable_Crock_Pot) | Done | containers, cooking_filter, craftable_items, dont_starve_together, food_tab |
| [Portable Grinding Mill](https://dontstarve.fandom.com/wiki/Portable_Grinding_Mill) | Done | cooking_filter, craftable_items, crafting_stations, dont_starve_together, food_tab |
| [Portable Seasoning Station](https://dontstarve.fandom.com/wiki/Portable_Seasoning_Station) | Done | cooking_filter, craftable_items, dont_starve_together |
| [Portal Paraphernalia](https://dontstarve.fandom.com/wiki/Portal_Paraphernalia) | Done | celestial_filter, craftable_items, dont_starve_together |
| [Portasol](https://dontstarve.fandom.com/wiki/Portasol) | Done | clothing_filter, craftable_items, dont_starve_together |
| [Portrait Frames](https://dontstarve.fandom.com/wiki/Portrait_Frames) | Done | dont_starve_together |
| [Possessed Varg](https://dontstarve.fandom.com/wiki/Possessed_Varg) | Done | boss_monsters, dont_starve_together, from_beyond |
| [Potato](https://dontstarve.fandom.com/wiki/Potato) | Done | dont_starve_together, events, food |
| [Potato Sack](https://dontstarve.fandom.com/wiki/Potato_Sack) | Done | dont_starve_together |
| [Potted Fern](https://dontstarve.fandom.com/wiki/Potted_Fern) | Done | craftable_structures, decorations_filter |
| [Potted Succulent](https://dontstarve.fandom.com/wiki/Potted_Succulent) | Done | a_new_reign, craftable_structures, decorations_filter, dont_starve_together |
| [Potter's Wheel](https://dontstarve.fandom.com/wiki/Potter's_Wheel) | Done | a_new_reign, craftable_structures, crafting_stations, decorations_filter, dont_starve_together |
| [Powder Monkey](https://dontstarve.fandom.com/wiki/Powder_Monkey) | Done | animals, dont_starve_together |
| [Powdercake](https://dontstarve.fandom.com/wiki/Powdercake) | Done | crock_pot_recipes |
| [Prestihatitator](https://dontstarve.fandom.com/wiki/Prestihatitator) | Done | craftable_structures |
| [Pretty Parasol](https://dontstarve.fandom.com/wiki/Pretty_Parasol) | Done | craftable_items, equipable_items, fuel |
| [Prime Mate](https://dontstarve.fandom.com/wiki/Prime_Mate) | Done | dont_starve_together |
| [Produce Scale](https://dontstarve.fandom.com/wiki/Produce_Scale) | Done | craftable_structures, decorations_filter, dont_starve_together, food_gardening_filter |
| [Profile Icons](https://dontstarve.fandom.com/wiki/Profile_Icons) | Done | dont_starve_together |
| [Prototypers & Stations Filter](https://dontstarve.fandom.com/wiki/Prototypers_%26_Stations_Filter) | Done | dont_starve_together |
| [Psychosis Experiment](https://dontstarve.fandom.com/wiki/Psychosis_Experiment) | Done | craftable_items, dont_starve_together, events, fuel |
| [Puffed Potato Soufflé](https://dontstarve.fandom.com/wiki/Puffed_Potato_Souffl%C3%A9) | Done | dont_starve_together |
| [Puffy Vest](https://dontstarve.fandom.com/wiki/Puffy_Vest) | Done | craftable_items, equipable_items |
| [Pumpkin](https://dontstarve.fandom.com/wiki/Pumpkin) | Done | food |
| [Pumpkin Cookies](https://dontstarve.fandom.com/wiki/Pumpkin_Cookies) | Done | crock_pot_recipes, food |
| [Pumpkin Lantern](https://dontstarve.fandom.com/wiki/Pumpkin_Lantern) | Done | craftable_items |
| [Punching Bag](https://dontstarve.fandom.com/wiki/Punching_Bag) | Done | craftable_structures, from_beyond |
| [Pure Brilliance](https://dontstarve.fandom.com/wiki/Pure_Brilliance) | Done | craftable_items, dont_starve_together, from_beyond |
| [Pure Horror](https://dontstarve.fandom.com/wiki/Pure_Horror) | Done | boss_dropped_items, craftable_items, dont_starve_together, fuel |
| [Purple Gem](https://dontstarve.fandom.com/wiki/Purple_Gem) | Done | boss_dropped_items, craftable_items |
| [Queen of Moon Quay](https://dontstarve.fandom.com/wiki/Queen_of_Moon_Quay) | Done | dont_starve_together |
| [Rabbit](https://dontstarve.fandom.com/wiki/Rabbit) | Done | animals |
| [Rabbit Earmuffs](https://dontstarve.fandom.com/wiki/Rabbit_Earmuffs) | Done | craftable_items, equipable_items |
| [Rabbit Hutch](https://dontstarve.fandom.com/wiki/Rabbit_Hutch) | Done | craftable_structures |
| [Rabbit King Cudgel](https://dontstarve.fandom.com/wiki/Rabbit_King_Cudgel) | Done | dont_starve_together, from_beyond |
| [Rain Coat](https://dontstarve.fandom.com/wiki/Rain_Coat) | Done | craftable_items, dont_starve_together, equipable_items |
| [Rain Gear Filter](https://dontstarve.fandom.com/wiki/Rain_Gear_Filter) | Done | dont_starve_together |
| [Rain Hat](https://dontstarve.fandom.com/wiki/Rain_Hat) | Done | craftable_items, dont_starve_together, equipable_items |
| [Rainometer](https://dontstarve.fandom.com/wiki/Rainometer) | Done | craftable_structures |
| [Ratatouille](https://dontstarve.fandom.com/wiki/Ratatouille) | Done | crock_pot_recipes |
| [Raw Fish](https://dontstarve.fandom.com/wiki/Raw_Fish) | Done | boss_dropped_items, dont_starve_together, fishes, food |
| [Razor](https://dontstarve.fandom.com/wiki/Razor) | Done | craftable_items |
| [Reanimated Skeleton](https://dontstarve.fandom.com/wiki/Reanimated_Skeleton) | Done | a_new_reign, boss_monsters, cave_creatures, dont_starve_together |
| [Recipe Card](https://dontstarve.fandom.com/wiki/Recipe_Card) | Done | dont_starve_together |
| [Record](https://dontstarve.fandom.com/wiki/Record) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Red Cap](https://dontstarve.fandom.com/wiki/Red_Cap) | Done | boss_dropped_items, food |
| [Red Firecrackers](https://dontstarve.fandom.com/wiki/Red_Firecrackers) | Done | craftable_items, dont_starve_together |
| [Red Gem](https://dontstarve.fandom.com/wiki/Red_Gem) | Done | boss_dropped_items, craftable_items |
| [Red Lantern](https://dontstarve.fandom.com/wiki/Red_Lantern) | Done | craftable_items, dont_starve_together, equipable_items |
| [Refined Materials Filter](https://dontstarve.fandom.com/wiki/Refined_Materials_Filter) | Done | dont_starve_together |
| [Regrowth](https://dontstarve.fandom.com/wiki/Regrowth) | Done | dont_starve_together |
| [Reinforced Support Pillar](https://dontstarve.fandom.com/wiki/Reinforced_Support_Pillar) | Done | craftable_structures, dont_starve_together, from_beyond |
| [Relic](https://dontstarve.fandom.com/wiki/Relic) | Done | a_new_reign, craftable_structures, decorations_filter |
| [Repair Kits](https://dontstarve.fandom.com/wiki/Repair_Kits) | Done | dont_starve_together, from_beyond |
| [Research Notes](https://dontstarve.fandom.com/wiki/Research_Notes) | Done | dont_starve_together, from_beyond, fuel |
| [Resting Horror](https://dontstarve.fandom.com/wiki/Resting_Horror) | Done | cave_creatures, dont_starve_together, from_beyond |
| [Restrained Static](https://dontstarve.fandom.com/wiki/Restrained_Static) | Done | dont_starve_together |
| [Return of Them](https://dontstarve.fandom.com/wiki/Return_of_Them) | Done | dont_starve_together |
| [Rhinocebro](https://dontstarve.fandom.com/wiki/Rhinocebro) | Done | dont_starve_together, events |
| [Riled Lucy](https://dontstarve.fandom.com/wiki/Riled_Lucy) | Done | dont_starve_together, events |
| [Rock Den](https://dontstarve.fandom.com/wiki/Rock_Den) | Done | a_new_reign, crafting_stations, dont_starve_together |
| [Rock Lobster](https://dontstarve.fandom.com/wiki/Rock_Lobster) | Done | animals, cave_creatures, dont_starve_together, followers |
| [Rockjaw](https://dontstarve.fandom.com/wiki/Rockjaw) | Done | dont_starve_together |
| [Rocks](https://dontstarve.fandom.com/wiki/Rocks) | Done | craftable_items |
| [Rocky Beach](https://dontstarve.fandom.com/wiki/Rocky_Beach) | Done | dont_starve_together |
| [Rocky Beach Turf](https://dontstarve.fandom.com/wiki/Rocky_Beach_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, fuel |
| [Rocky Turf](https://dontstarve.fandom.com/wiki/Rocky_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Rope](https://dontstarve.fandom.com/wiki/Rope) | Done | craftable_items, fuel |
| [Rose-Colored Glasses](https://dontstarve.fandom.com/wiki/Rose-Colored_Glasses) | Done | clothing_filter, craftable_items, dont_starve_together |
| [Rot](https://dontstarve.fandom.com/wiki/Rot) | Done | craftable_items, fertilizer, fuel |
| [Rotten Egg](https://dontstarve.fandom.com/wiki/Rotten_Egg) | Done | eggs, fertilizer, fuel |
| [Royal Jelly](https://dontstarve.fandom.com/wiki/Royal_Jelly) | Done | a_new_reign, boss_dropped_items, dont_starve_together |
| [Royal Rabbit Enforcer](https://dontstarve.fandom.com/wiki/Royal_Rabbit_Enforcer) | Done | dont_starve_together, from_beyond |
| [Royal Tapestry](https://dontstarve.fandom.com/wiki/Royal_Tapestry) | Done | craftable_structures, dont_starve_together |
| [Rudder Kit](https://dontstarve.fandom.com/wiki/Rudder_Kit) | Done | craftable_items, dont_starve_together |
| [Ryftstal](https://dontstarve.fandom.com/wiki/Ryftstal) | Done | dont_starve_together, from_beyond |
| [Saddle](https://dontstarve.fandom.com/wiki/Saddle) | Done | a_new_reign, craftable_items, dont_starve_together |
| [Saddlehorn](https://dontstarve.fandom.com/wiki/Saddlehorn) | Done | craftable_items, equipable_items |
| [Safe](https://dontstarve.fandom.com/wiki/Safe) | Done | dont_starve_together, events |
| [Saladmander](https://dontstarve.fandom.com/wiki/Saladmander) | Done | dont_starve_together |
| [Salmon](https://dontstarve.fandom.com/wiki/Salmon) | Done | dont_starve_together, events, food |
| [Salsa Fresca](https://dontstarve.fandom.com/wiki/Salsa_Fresca) | Done | crock_pot_recipes, dont_starve_together, food |
| [Salt Box](https://dontstarve.fandom.com/wiki/Salt_Box) | Done | cooking_filter, craftable_structures, dont_starve_together, food_tab |
| [Salt Crystals](https://dontstarve.fandom.com/wiki/Salt_Crystals) | Done | dont_starve_together, events, food |
| [Salt Formation](https://dontstarve.fandom.com/wiki/Salt_Formation) | Done | dont_starve_together |
| [Salt Lick](https://dontstarve.fandom.com/wiki/Salt_Lick) | Done | a_new_reign, craftable_structures |
| [Salt Pond](https://dontstarve.fandom.com/wiki/Salt_Pond) | Done | dont_starve_together, events |
| [Salt Rack](https://dontstarve.fandom.com/wiki/Salt_Rack) | Done | dont_starve_together, events |
| [Sammy](https://dontstarve.fandom.com/wiki/Sammy) | Done | dont_starve_together, events |
| [Sandstorm](https://dontstarve.fandom.com/wiki/Sandstorm) | Done | a_new_reign, dont_starve_together |
| [Sandy Turf](https://dontstarve.fandom.com/wiki/Sandy_Turf) | Done | craftable_items, decorations_filter, dont_starve_together, fuel |
| [Sanguine Experiment](https://dontstarve.fandom.com/wiki/Sanguine_Experiment) | Done | craftable_items, dont_starve_together, events, fuel |
| [Sap](https://dontstarve.fandom.com/wiki/Sap) | Done | dont_starve_together, events |
| [Sapling](https://dontstarve.fandom.com/wiki/Sapling) | Done | dont_starve_together, fuel |
| [Savanna Turf](https://dontstarve.fandom.com/wiki/Savanna_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Sawhorse](https://dontstarve.fandom.com/wiki/Sawhorse) | Done | craftable_items, craftable_structures, dont_starve_together, from_beyond |
| [Scaled Chest](https://dontstarve.fandom.com/wiki/Scaled_Chest) | Done | containers, craftable_structures, dont_starve_together |
| [Scaled Flooring](https://dontstarve.fandom.com/wiki/Scaled_Flooring) | Done | craftable_items, decorations_filter, dont_starve_together, fuel |
| [Scaled Furnace](https://dontstarve.fandom.com/wiki/Scaled_Furnace) | Done | a_new_reign, cooking_filter, craftable_structures, dont_starve_together |
| [Scalemail](https://dontstarve.fandom.com/wiki/Scalemail) | Done | armour_filter, craftable_items, dont_starve_together, equipable_items, fight_tab |
| [Scales](https://dontstarve.fandom.com/wiki/Scales) | Done | boss_dropped_items, dont_starve_together |
| [Science Machine](https://dontstarve.fandom.com/wiki/Science_Machine) | Done | craftable_structures, crafting_stations |
| [Scorpeon](https://dontstarve.fandom.com/wiki/Scorpeon) | Done | dont_starve_together, events |
| [Scrap](https://dontstarve.fandom.com/wiki/Scrap) | Done | dont_starve_together, from_beyond |
| [Scrap Wall](https://dontstarve.fandom.com/wiki/Scrap_Wall) | Done | decorations_filter, dont_starve_together |
| [Scrapbooking](https://dontstarve.fandom.com/wiki/Scrapbooking) | Done | dont_starve_together |
| [Scrappy Chapauldron](https://dontstarve.fandom.com/wiki/Scrappy_Chapauldron) | Done | dont_starve_together, equipable_items, from_beyond |
| [Scrappy Werepig](https://dontstarve.fandom.com/wiki/Scrappy_Werepig) | Done | boss_monsters, dont_starve_together, from_beyond |
| [Sculptures Filter](https://dontstarve.fandom.com/wiki/Sculptures_Filter) | Done | dont_starve_together |
| [Sea Bones](https://dontstarve.fandom.com/wiki/Sea_Bones) | Done | dont_starve_together |
| [Sea Fishing Rod](https://dontstarve.fandom.com/wiki/Sea_Fishing_Rod) | Done | craftable_items, dont_starve_together, equipable_items |
| [Sea Sprout Starter](https://dontstarve.fandom.com/wiki/Sea_Sprout_Starter) | Done | dont_starve_together |
| [Sea Stack](https://dontstarve.fandom.com/wiki/Sea_Stack) | Done | dont_starve_together |
| [Sea Strider](https://dontstarve.fandom.com/wiki/Sea_Strider) | Done | dont_starve_together, followers |
| [Sea Strider Nest](https://dontstarve.fandom.com/wiki/Sea_Strider_Nest) | Done | dont_starve_together |
| [Sea Weed](https://dontstarve.fandom.com/wiki/Sea_Weed) | Done | dont_starve_together |
| [Seafaring Filter](https://dontstarve.fandom.com/wiki/Seafaring_Filter) | Done | dont_starve_together |
| [Seafood Gumbo](https://dontstarve.fandom.com/wiki/Seafood_Gumbo) | Done | crock_pot_recipes, dont_starve_together, food |
| [Sealed Portal](https://dontstarve.fandom.com/wiki/Sealed_Portal) | Done | dont_starve_together |
| [Seasoning Salt](https://dontstarve.fandom.com/wiki/Seasoning_Salt) | Done | craftable_items, dont_starve_together |
| [Seasonings Filter](https://dontstarve.fandom.com/wiki/Seasonings_Filter) | Done | dont_starve_together |
| [Seasons](https://dontstarve.fandom.com/wiki/Seasons) | Done | dont_starve_together |
| [Autumn](https://dontstarve.fandom.com/wiki/Seasons/Autumn) | Done | dont_starve_together |
| [Spring](https://dontstarve.fandom.com/wiki/Seasons/Spring) | Done | dont_starve_together |
| [Summer](https://dontstarve.fandom.com/wiki/Seasons/Summer) | Done | dont_starve_together |
| [Seawreath](https://dontstarve.fandom.com/wiki/Seawreath) | Done | craftable_items, dont_starve_together, equipable_items |
| [Second Chance Watch](https://dontstarve.fandom.com/wiki/Second_Chance_Watch) | Done | craftable_items, dont_starve_together |
| [Seed Pack-It](https://dontstarve.fandom.com/wiki/Seed_Pack-It) | Done | backpacks, craftable_items, dont_starve_together, equipable_items, food_gardening_filter, food_tab |
| [Seeds](https://dontstarve.fandom.com/wiki/Seeds) | Done | food |
| [Seedshell](https://dontstarve.fandom.com/wiki/Seedshell) | Done | dont_starve_together, equipable_items |
| [Serving](https://dontstarve.fandom.com/wiki/Serving) | Done | dont_starve_together, events |
| [Set Piece](https://dontstarve.fandom.com/wiki/Set_Piece) | Done | dont_starve_together |
| [Sewing Kit](https://dontstarve.fandom.com/wiki/Sewing_Kit) | Done | craftable_items |
| [Shadow Aligned](https://dontstarve.fandom.com/wiki/Shadow_Aligned) | Done | dont_starve_together |
| [Shadow Atrium](https://dontstarve.fandom.com/wiki/Shadow_Atrium) | Done | a_new_reign, boss_dropped_items, dont_starve_together, from_beyond |
| [Shadow Magic Filter](https://dontstarve.fandom.com/wiki/Shadow_Magic_Filter) | Done | dont_starve_together |
| [Shadow Manipulator](https://dontstarve.fandom.com/wiki/Shadow_Manipulator) | Done | craftable_structures |
| [Shadow Maul](https://dontstarve.fandom.com/wiki/Shadow_Maul) | Done | craftable_items, dont_starve_together, from_beyond |
| [Shadow Merm](https://dontstarve.fandom.com/wiki/Shadow_Merm) | Done | dont_starve_together, followers |
| [Shadow Pieces](https://dontstarve.fandom.com/wiki/Shadow_Pieces) | Done | a_new_reign, boss_monsters, dont_starve_together |
| [Shadow Reaper](https://dontstarve.fandom.com/wiki/Shadow_Reaper) | Done | craftable_items, dont_starve_together, from_beyond |
| [Shadow Thurible](https://dontstarve.fandom.com/wiki/Shadow_Thurible) | Done | a_new_reign, boss_dropped_items, dont_starve_together |
| [Shadow Traps](https://dontstarve.fandom.com/wiki/Shadow_Traps) | Done | dont_starve_together |
| [Shadowcraft Filter](https://dontstarve.fandom.com/wiki/Shadowcraft_Filter) | Done | dont_starve_together |
| [Shadowcraft Plinth](https://dontstarve.fandom.com/wiki/Shadowcraft_Plinth) | Done | ancient_tier_2, craftable_items, dont_starve_together, from_beyond |
| [Shattered Spider](https://dontstarve.fandom.com/wiki/Shattered_Spider) | Done | dont_starve_together |
| [Shattered Spider Hole](https://dontstarve.fandom.com/wiki/Shattered_Spider_Hole) | Done | dont_starve_together |
| [Shell Beach Turf](https://dontstarve.fandom.com/wiki/Shell_Beach_Turf) | Done | craftable_items, decorations_filter, dont_starve_together |
| [Shell Bells](https://dontstarve.fandom.com/wiki/Shell_Bells) | Done | dont_starve_together |
| [Shell Cluster](https://dontstarve.fandom.com/wiki/Shell_Cluster) | Done | dont_starve_together |
| [Shelmet](https://dontstarve.fandom.com/wiki/Shelmet) | Done | equipable_items |
| [Shield of Terror](https://dontstarve.fandom.com/wiki/Shield_of_Terror) | Done | boss_dropped_items, dont_starve_together, equipable_items |
| [Shoddy Tool](https://dontstarve.fandom.com/wiki/Shoddy_Tool) | Done | dont_starve_together |
| [Shoddy Tool Shed](https://dontstarve.fandom.com/wiki/Shoddy_Tool_Shed) | Done | craftable_structures, dont_starve_together |
| [Shoo Box](https://dontstarve.fandom.com/wiki/Shoo_Box) | Done | craftable_items, dont_starve_together |
| [Shovel](https://dontstarve.fandom.com/wiki/Shovel) | Done | craftable_items, equipable_items |
| [Shroom Skin](https://dontstarve.fandom.com/wiki/Shroom_Skin) | Done | a_new_reign, boss_dropped_items, dont_starve_together |
| [Siesta Lean-to](https://dontstarve.fandom.com/wiki/Siesta_Lean-to) | Done | cooling, craftable_structures, dont_starve_together |
| [Sign](https://dontstarve.fandom.com/wiki/Sign) | Done | craftable_structures, decorations_filter |
| [Silk](https://dontstarve.fandom.com/wiki/Silk) | Done | boss_dropped_items |
| [Silken Grand Armor](https://dontstarve.fandom.com/wiki/Silken_Grand_Armor) | Done | dont_starve_together |
| [Sisturn](https://dontstarve.fandom.com/wiki/Sisturn) | Done | craftable_structures, dont_starve_together |
| [Skeeter Bomb](https://dontstarve.fandom.com/wiki/Skeeter_Bomb) | Done | craftable_items, dont_starve_together, from_beyond |
| [Skeleton](https://dontstarve.fandom.com/wiki/Skeleton) | Done | dont_starve_together |
| [Sketch](https://dontstarve.fandom.com/wiki/Sketch) | Done | a_new_reign, boss_dropped_items, celestial_tab, dont_starve_together, fuel |
| [Skill Spotlight Update](https://dontstarve.fandom.com/wiki/Skill_Spotlight_Update) | Done | dont_starve_together |
| [Skins](https://dontstarve.fandom.com/wiki/Skins) | Done | dont_starve_together |
| [Skittersquid](https://dontstarve.fandom.com/wiki/Skittersquid) | Done | dont_starve_together |
| [Slimy Biome](https://dontstarve.fandom.com/wiki/Slimy_Biome) | Done | dont_starve_together |
| [Slimy Salve](https://dontstarve.fandom.com/wiki/Slimy_Salve) | Done | craftable_items, dont_starve_together, from_beyond |
| [Slimy Turf](https://dontstarve.fandom.com/wiki/Slimy_Turf) | Done | craftable_items, decorations_filter, fuel |
| [Slingshot Ammo](https://dontstarve.fandom.com/wiki/Slingshot_Ammo) | Done | dont_starve_together |
| [Slingshot Ammo Tab](https://dontstarve.fandom.com/wiki/Slingshot_Ammo_Tab) | Done | dont_starve_together |
| [Slurper](https://dontstarve.fandom.com/wiki/Slurper) | Done | equipable_items |
| [Slurtle](https://dontstarve.fandom.com/wiki/Slurtle) | Done | animals, cave_creatures |
| [Slurtle Slime](https://dontstarve.fandom.com/wiki/Slurtle_Slime) | Done | fuel |
| [Snortoise](https://dontstarve.fandom.com/wiki/Snortoise) | Done | dont_starve_together, events |
| [Snurtle Shell Armor](https://dontstarve.fandom.com/wiki/Snurtle_Shell_Armor) | Done | equipable_items |
| [Soothing Tea](https://dontstarve.fandom.com/wiki/Soothing_Tea) | Done | crock_pot_recipes, dont_starve_together, food |
| [Soul](https://dontstarve.fandom.com/wiki/Soul) | Done | dont_starve_together |
| [Spark Ark](https://dontstarve.fandom.com/wiki/Spark_Ark) | Done | boss_dropped_items, dont_starve_together, from_beyond |
| [Spear](https://dontstarve.fandom.com/wiki/Spear) | Done | craftable_items, equipable_items, fight_tab |
| [Special Event Filter](https://dontstarve.fandom.com/wiki/Special_Event_Filter) | Done | dont_starve_together |
| [Spelunker's Bridge Kit](https://dontstarve.fandom.com/wiki/Spelunker's_Bridge_Kit) | Done | craftable_items |
| [Spicy Chili](https://dontstarve.fandom.com/wiki/Spicy_Chili) | Done | crock_pot_recipes, dont_starve_together, food |
| [Spicy Vegetable Stinger](https://dontstarve.fandom.com/wiki/Spicy_Vegetable_Stinger) | Done | crock_pot_recipes, dont_starve_together, food |
| [Spider](https://dontstarve.fandom.com/wiki/Spider) | Done | cave_creatures, followers |
| [Spider Care Tab](https://dontstarve.fandom.com/wiki/Spider_Care_Tab) | Done | dont_starve_together |
| [Spider Eggs](https://dontstarve.fandom.com/wiki/Spider_Eggs) | Done | boss_dropped_items, craftable_items, eggs, fuel |
| [Spider Queen](https://dontstarve.fandom.com/wiki/Spider_Queen) | Done | boss_monsters, cave_creatures |
| [Spider Warrior](https://dontstarve.fandom.com/wiki/Spider_Warrior) | Done | cave_creatures, followers |
| [Spiderhat](https://dontstarve.fandom.com/wiki/Spiderhat) | Done | boss_dropped_items, equipable_items |
| [Spiky Bush](https://dontstarve.fandom.com/wiki/Spiky_Bush) | Done | fuel |
| [Spitter](https://dontstarve.fandom.com/wiki/Spitter) | Done | cave_creatures, followers |
| [Splumonkey](https://dontstarve.fandom.com/wiki/Splumonkey) | Done | animals |
| [Spoiled Fish](https://dontstarve.fandom.com/wiki/Spoiled_Fish) | Done | dont_starve_together, fertilizer, fuel |
| [Spools](https://dontstarve.fandom.com/wiki/Spools) | Done | dont_starve_together |
| [Spotty Shrub](https://dontstarve.fandom.com/wiki/Spotty_Shrub) | Done | dont_starve_together, events |
| [Spotty Sprig](https://dontstarve.fandom.com/wiki/Spotty_Sprig) | Done | dont_starve_together, events |
| [Sprouting Stone Fruit](https://dontstarve.fandom.com/wiki/Sprouting_Stone_Fruit) | Done | dont_starve_together |
| [Sproutrock](https://dontstarve.fandom.com/wiki/Sproutrock) | Done | dont_starve_together, from_beyond |
| [Stag Antler](https://dontstarve.fandom.com/wiki/Stag_Antler) | Done | a_new_reign, boss_dropped_items, dont_starve_together |
| [Stage](https://dontstarve.fandom.com/wiki/Stage) | Done | dont_starve_together |
| [Stagecraft Tab](https://dontstarve.fandom.com/wiki/Stagecraft_Tab) | Done | dont_starve_together |
| [Stagehand](https://dontstarve.fandom.com/wiki/Stagehand) | Done | a_new_reign, craftable_structures, decorations_filter, dont_starve_together |
| [Star Caller's Staff](https://dontstarve.fandom.com/wiki/Star_Caller's_Staff) | Done | ancient_tab, ancient_tier_1, craftable_items, equipable_items |
| [Star-Sky](https://dontstarve.fandom.com/wiki/Star-Sky) | Done | dont_starve_together |
| [Steamed Twigs](https://dontstarve.fandom.com/wiki/Steamed_Twigs) | Done | beefalo_foods, crock_pot_recipes, dont_starve_together |
| [Steel Wool](https://dontstarve.fandom.com/wiki/Steel_Wool) | Done | a_new_reign, dont_starve_together, fuel |
| [Steering Wheel](https://dontstarve.fandom.com/wiki/Steering_Wheel) | Done | craftable_items, dont_starve_together |
| [Stinger](https://dontstarve.fandom.com/wiki/Stinger) | Done | boss_dropped_items |
| [Stone Fruit](https://dontstarve.fandom.com/wiki/Stone_Fruit) | Done | dont_starve_together, food |
| [Stone Fruit Bush](https://dontstarve.fandom.com/wiki/Stone_Fruit_Bush) | Done | dont_starve_together |
| [Stone Wall](https://dontstarve.fandom.com/wiki/Stone_Wall) | Done | craftable_items |
| [Storage Solutions Filter](https://dontstarve.fandom.com/wiki/Storage_Solutions_Filter) | Done | dont_starve_together |
| [Straw Hat](https://dontstarve.fandom.com/wiki/Straw_Hat) | Done | craftable_items, equipable_items |
| [Strident Trident](https://dontstarve.fandom.com/wiki/Strident_Trident) | Done | craftable_items, dont_starve_together, equipable_items |
| [Strongman Tab](https://dontstarve.fandom.com/wiki/Strongman_Tab) | Done | dont_starve_together |
| [Structures Filter](https://dontstarve.fandom.com/wiki/Structures_Filter) | Done | dont_starve_together |
| [Stuffed Eggplant](https://dontstarve.fandom.com/wiki/Stuffed_Eggplant) | Done | crock_pot_recipes, food |
| [Stuffed Fish Heads](https://dontstarve.fandom.com/wiki/Stuffed_Fish_Heads) | Done | crock_pot_recipes, dont_starve_together, food |
| [Stuffed Night Cap](https://dontstarve.fandom.com/wiki/Stuffed_Night_Cap) | Done | dont_starve_together, food, from_beyond |
| [Stuffed Pepper Poppers](https://dontstarve.fandom.com/wiki/Stuffed_Pepper_Poppers) | Done | crock_pot_recipes, dont_starve_together, food |
| [Sugarwood Tree](https://dontstarve.fandom.com/wiki/Sugarwood_Tree) | Done | dont_starve_together, events |
| [Sulfuric Experiment](https://dontstarve.fandom.com/wiki/Sulfuric_Experiment) | Done | craftable_items, dont_starve_together, events, fuel |
| [Summer Frest](https://dontstarve.fandom.com/wiki/Summer_Frest) | Done | cooling, craftable_items, dont_starve_together, equipable_items |
| [Summer Items Filter](https://dontstarve.fandom.com/wiki/Summer_Items_Filter) | Done | dont_starve_together |
| [Sunken Chest](https://dontstarve.fandom.com/wiki/Sunken_Chest) | Done | dont_starve_together |
| [Surf 'n' Turf](https://dontstarve.fandom.com/wiki/Surf_'n'_Turf) | Done | crock_pot_recipes, dont_starve_together, food |
| [Surprising Seed](https://dontstarve.fandom.com/wiki/Surprising_Seed) | Done | dont_starve_together, from_beyond |
| [Survivor Items Filter](https://dontstarve.fandom.com/wiki/Survivor_Items_Filter) | Done | dont_starve_together |
| [Suspicious Marble](https://dontstarve.fandom.com/wiki/Suspicious_Marble) | Done | a_new_reign, dont_starve_together |
| [Suspicious Moonrock](https://dontstarve.fandom.com/wiki/Suspicious_Moonrock) | Done | a_new_reign, dont_starve_together |
| [Swamp Brawler Helmet](https://dontstarve.fandom.com/wiki/Swamp_Brawler_Helmet) | Done | dont_starve_together |
| [Swamp Pig](https://dontstarve.fandom.com/wiki/Swamp_Pig) | Done | dont_starve_together, events |
| [Swamp Pig Elder](https://dontstarve.fandom.com/wiki/Swamp_Pig_Elder) | Done | dont_starve_together, events |
| [Switcherdoodle](https://dontstarve.fandom.com/wiki/Switcherdoodle) | Done | craftable_items, dont_starve_together, food |
| [Syrup](https://dontstarve.fandom.com/wiki/Syrup) | Done | dont_starve_together, events |
| [Syrup of Ipecaca](https://dontstarve.fandom.com/wiki/Syrup_of_Ipecaca) | Done | craftable_items, dont_starve_together |
| [Table Lamp](https://dontstarve.fandom.com/wiki/Table_Lamp) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Table Vase](https://dontstarve.fandom.com/wiki/Table_Vase) | Done | craftable_items, decorations_filter, dont_starve_together, from_beyond |
| [Tables](https://dontstarve.fandom.com/wiki/Tables) | Done | dont_starve_together, from_beyond |
| [Tackle Box](https://dontstarve.fandom.com/wiki/Tackle_Box) | Done | craftable_items, dont_starve_together |
| [Tackle Receptacle](https://dontstarve.fandom.com/wiki/Tackle_Receptacle) | Done | craftable_structures, dont_starve_together |
| [Taffy](https://dontstarve.fandom.com/wiki/Taffy) | Done | crock_pot_recipes, food |
| [Tail o' Three Cats](https://dontstarve.fandom.com/wiki/Tail_o'_Three_Cats) | Done | a_new_reign, craftable_items, dont_starve_together, equipable_items, fight_tab |
| [Tall Scotch Eggs](https://dontstarve.fandom.com/wiki/Tall_Scotch_Eggs) | Done | crock_pot_recipes, dont_starve_together, food |
| [Tallbird](https://dontstarve.fandom.com/wiki/Tallbird) | Done | birds |
| [Tallbird Egg](https://dontstarve.fandom.com/wiki/Tallbird_Egg) | Done | eggs, food |
| [Tam o' Shanter](https://dontstarve.fandom.com/wiki/Tam_o'_Shanter) | Done | equipable_items |
| [Telelocator Focus](https://dontstarve.fandom.com/wiki/Telelocator_Focus) | Done | craftable_structures |
| [Telelocator Staff](https://dontstarve.fandom.com/wiki/Telelocator_Staff) | Done | craftable_items, equipable_items |
| [Teletransport Station](https://dontstarve.fandom.com/wiki/Teletransport_Station) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Telltale Heart](https://dontstarve.fandom.com/wiki/Telltale_Heart) | Done | craftable_items, dont_starve_together |
| [Tent](https://dontstarve.fandom.com/wiki/Tent) | Done | craftable_structures |
| [Tent Roll](https://dontstarve.fandom.com/wiki/Tent_Roll) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Tentacle](https://dontstarve.fandom.com/wiki/Tentacle) | Done | cave_creatures |
| [Tentacle Spike](https://dontstarve.fandom.com/wiki/Tentacle_Spike) | Done | equipable_items |
| [Tentacle Spots](https://dontstarve.fandom.com/wiki/Tentacle_Spots) | Done | fuel |
| [Terra Firma Tamper](https://dontstarve.fandom.com/wiki/Terra_Firma_Tamper) | Done | craftable_structures, decorations_filter, dont_starve_together |
| [Terrarium](https://dontstarve.fandom.com/wiki/Terrarium) | Done | dont_starve_together |
| [The Altar of Gnaw](https://dontstarve.fandom.com/wiki/The_Altar_of_Gnaw) | Done | dont_starve_together, events |
| [The Curse of Moon Quay](https://dontstarve.fandom.com/wiki/The_Curse_of_Moon_Quay) | Done | dont_starve_together |
| [The Forge](https://dontstarve.fandom.com/wiki/The_Forge) | Done | dont_starve_together, events |
| [The Gnaw](https://dontstarve.fandom.com/wiki/The_Gnaw) | Done | dont_starve_together, events |
| [The Gorge](https://dontstarve.fandom.com/wiki/The_Gorge) | Done | dont_starve_together, events |
| [The Gorge Recipes](https://dontstarve.fandom.com/wiki/The_Gorge_Recipes) | Done | dont_starve_together, events |
| [The Gorge Seeds](https://dontstarve.fandom.com/wiki/The_Gorge_Seeds) | Done | dont_starve_together, events |
| [The Lazy Deserter](https://dontstarve.fandom.com/wiki/The_Lazy_Deserter) | Done | a_new_reign, craftable_structures, dont_starve_together |
| [The Lazy Explorer](https://dontstarve.fandom.com/wiki/The_Lazy_Explorer) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items |
| [The Lazy Forager](https://dontstarve.fandom.com/wiki/The_Lazy_Forager) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items |
| [Thermal Measurer](https://dontstarve.fandom.com/wiki/Thermal_Measurer) | Done | craftable_structures |
| [Thermal Stone](https://dontstarve.fandom.com/wiki/Thermal_Stone) | Done | cooling, craftable_items |
| [Thick Fur](https://dontstarve.fandom.com/wiki/Thick_Fur) | Done | boss_dropped_items, craftable_items, dont_starve_together |
| [Think Tank](https://dontstarve.fandom.com/wiki/Think_Tank) | Done | craftable_structures, dont_starve_together |
| [Thulecite](https://dontstarve.fandom.com/wiki/Thulecite) | Done | ancient_tab, ancient_tier_1, craftable_items |
| [Thulecite Bug Net](https://dontstarve.fandom.com/wiki/Thulecite_Bug_Net) | Done | craftable_items |
| [Thulecite Club](https://dontstarve.fandom.com/wiki/Thulecite_Club) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items |
| [Thulecite Crown](https://dontstarve.fandom.com/wiki/Thulecite_Crown) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items |
| [Thulecite Medallion](https://dontstarve.fandom.com/wiki/Thulecite_Medallion) | Done | ancient_tab, ancient_tier_1, craftable_items |
| [Thulecite Suit](https://dontstarve.fandom.com/wiki/Thulecite_Suit) | Done | ancient_tab, ancient_tier_2, craftable_items, equipable_items |
| [Thulecite Wall](https://dontstarve.fandom.com/wiki/Thulecite_Wall) | Done | ancient_tier_1 |
| [Tidy Hidey-Hole](https://dontstarve.fandom.com/wiki/Tidy_Hidey-Hole) | Done | dont_starve_together |
| [Tillweed Salve](https://dontstarve.fandom.com/wiki/Tillweed_Salve) | Done | craftable_items, dont_starve_together |
| [Tillweeds](https://dontstarve.fandom.com/wiki/Tillweeds) | Done | dont_starve_together |
| [Time Pieces](https://dontstarve.fandom.com/wiki/Time_Pieces) | Done | dont_starve_together |
| [Tin Fishin' Bin](https://dontstarve.fandom.com/wiki/Tin_Fishin'_Bin) | Done | craftable_structures, dont_starve_together |
| [Toadstool](https://dontstarve.fandom.com/wiki/Toadstool) | Done | a_new_reign, boss_monsters, cave_creatures, dont_starve_together |
| [Toma Root](https://dontstarve.fandom.com/wiki/Toma_Root) | Done | dont_starve_together, food |
| [Tools Filter](https://dontstarve.fandom.com/wiki/Tools_Filter) | Done | dont_starve_together |
| [Tooth Trap](https://dontstarve.fandom.com/wiki/Tooth_Trap) | Done | craftable_items, fight_tab |
| [Top Hat](https://dontstarve.fandom.com/wiki/Top_Hat) | Done | craftable_items, equipable_items |
| [Torch](https://dontstarve.fandom.com/wiki/Torch) | Done | craftable_items, equipable_items |
| [Touch Stone](https://dontstarve.fandom.com/wiki/Touch_Stone) | Done | dont_starve_together |
| [Trade Inn](https://dontstarve.fandom.com/wiki/Trade_Inn) | Done | dont_starve_together |
| [Trading Hutch Filter](https://dontstarve.fandom.com/wiki/Trading_Hutch_Filter) | Done | dont_starve_together, from_beyond |
| [Trail Mix](https://dontstarve.fandom.com/wiki/Trail_Mix) | Done | crock_pot_recipes, dont_starve_together, food |
| [Trap](https://dontstarve.fandom.com/wiki/Trap) | Done | craftable_items, food_gardening_filter |
| [Treasury](https://dontstarve.fandom.com/wiki/Treasury) | Done | dont_starve_together |
| [Tree Jam](https://dontstarve.fandom.com/wiki/Tree_Jam) | Done | craftable_items, dont_starve_together, fertilizer, food_gardening_filter |
| [Treeguard](https://dontstarve.fandom.com/wiki/Treeguard) | Done | boss_monsters, cave_creatures |
| [Treeguard Idol](https://dontstarve.fandom.com/wiki/Treeguard_Idol) | Done | craftable_items, dont_starve_together |
| [Trinkets](https://dontstarve.fandom.com/wiki/Trinkets) | Done | a_new_reign, dont_starve_together |
| [Trusty Slingshot](https://dontstarve.fandom.com/wiki/Trusty_Slingshot) | Done | craftable_items, dont_starve_together, equipable_items |
| [Trusty Tape](https://dontstarve.fandom.com/wiki/Trusty_Tape) | Done | craftable_items, dont_starve_together |
| [Tumbleweed](https://dontstarve.fandom.com/wiki/Tumbleweed) | Done | dont_starve_together |
| [Turf-Raiser Helm](https://dontstarve.fandom.com/wiki/Turf-Raiser_Helm) | Done | clothing_filter, craftable_items, dont_starve_together |
| [Turkey Dinner](https://dontstarve.fandom.com/wiki/Turkey_Dinner) | Done | crock_pot_recipes, food |
| [Turnip](https://dontstarve.fandom.com/wiki/Turnip) | Done | dont_starve_together, events, food |
| [Twiggy Tree](https://dontstarve.fandom.com/wiki/Twiggy_Tree) | Done | a_new_reign, dont_starve_together |
| [Twiggy Tree Cone](https://dontstarve.fandom.com/wiki/Twiggy_Tree_Cone) | Done | a_new_reign, dont_starve_together, fuel |
| [Twigs](https://dontstarve.fandom.com/wiki/Twigs) | Done | beefalo_foods, craftable_items, fuel |
| [Umbralla](https://dontstarve.fandom.com/wiki/Umbralla) | Done | craftable_items, dont_starve_together, from_beyond |
| [Umbrella](https://dontstarve.fandom.com/wiki/Umbrella) | Done | clothing_filter, craftable_items, equipable_items, fuel |
| [Unagi](https://dontstarve.fandom.com/wiki/Unagi) | Done | craftable_items, crock_pot_recipes, food |
| [Underwater Salvageable](https://dontstarve.fandom.com/wiki/Underwater_Salvageable) | Done | dont_starve_together |
| [Unnatural Portal](https://dontstarve.fandom.com/wiki/Unnatural_Portal) | Done | dont_starve_together |
| [Unstable Transmission](https://dontstarve.fandom.com/wiki/Unstable_Transmission) | Done | dont_starve_together |
| [Varg](https://dontstarve.fandom.com/wiki/Varg) | Done | dont_starve_together |
| [Varglet](https://dontstarve.fandom.com/wiki/Varglet) | Done | dont_starve_together |
| [Veggie Burger](https://dontstarve.fandom.com/wiki/Veggie_Burger) | Done | crock_pot_recipes, dont_starve_together, food |
| [Vignettes](https://dontstarve.fandom.com/wiki/Vignettes) | Done | dont_starve_together |
| [Vitreoasis](https://dontstarve.fandom.com/wiki/Vitreoasis) | Done | dont_starve_together |
| [Void Cowl](https://dontstarve.fandom.com/wiki/Void_Cowl) | Done | craftable_items, dont_starve_together, from_beyond |
| [Void Robe](https://dontstarve.fandom.com/wiki/Void_Robe) | Done | craftable_items, dont_starve_together, from_beyond |
| [Volt Goat](https://dontstarve.fandom.com/wiki/Volt_Goat) | Done | animals, dont_starve_together |
| [Volt Goat Chaud-Froid](https://dontstarve.fandom.com/wiki/Volt_Goat_Chaud-Froid) | Done | dont_starve_together |
| [Volt Goat Horn](https://dontstarve.fandom.com/wiki/Volt_Goat_Horn) | Done | dont_starve_together |
| [W.A.R.B.I.S. Armor](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Armor) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond |
| [W.A.R.B.I.S. Head Gear](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Head_Gear) | Done | armour_filter, craftable_items, dont_starve_together, from_beyond |
| [W.A.R.B.O.T.](https://dontstarve.fandom.com/wiki/W.A.R.B.O.T.) | Done | boss_monsters, dont_starve_together |
| [W.I.N.bot](https://dontstarve.fandom.com/wiki/W.I.N.bot) | Done | dont_starve_together |
| [W.O.B.O.T.](https://dontstarve.fandom.com/wiki/W.O.B.O.T.) | Done | dont_starve_together, from_beyond |
| [Waffles](https://dontstarve.fandom.com/wiki/Waffles) | Done | crock_pot_recipes, food, fruits |
| [Grainy Transmission](https://dontstarve.fandom.com/wiki/Wagstaff/Grainy_Transmission) | Done | dont_starve_together |
| [Walking Cane](https://dontstarve.fandom.com/wiki/Walking_Cane) | Done | craftable_items, equipable_items |
| [Wall](https://dontstarve.fandom.com/wiki/Wall) | Done | dont_starve_together, fuel |
| [Walter](https://dontstarve.fandom.com/wiki/Walter) | Done | dont_starve_together |
| [Wanda](https://dontstarve.fandom.com/wiki/Wanda) | Done | dont_starve_together |
| [Wanda clothes](https://dontstarve.fandom.com/wiki/Wanda_clothes) | Done | dont_starve_together |
| [Wardrobe](https://dontstarve.fandom.com/wiki/Wardrobe) | Done | craftable_structures, decorations_filter, dont_starve_together |
| [Warly](https://dontstarve.fandom.com/wiki/Warly) | Done | dont_starve_together |
| [Warren Wreath](https://dontstarve.fandom.com/wiki/Warren_Wreath) | Done | craftable_items, equipable_items, from_beyond |
| [Water Balloon](https://dontstarve.fandom.com/wiki/Water_Balloon) | Done | craftable_items, dont_starve_together, equipable_items |
| [Watering Can](https://dontstarve.fandom.com/wiki/Watering_Can) | Done | craftable_items, dont_starve_together, equipable_items, food_gardening_filter |
| [Waterlogged](https://dontstarve.fandom.com/wiki/Waterlogged) | Done | dont_starve_together |
| [Watermelon](https://dontstarve.fandom.com/wiki/Watermelon) | Done | cooling, dont_starve_together, food, fruits |
| [Waves](https://dontstarve.fandom.com/wiki/Waves) | Done | dont_starve_together |
| [Wax Paper](https://dontstarve.fandom.com/wiki/Wax_Paper) | Done | craftable_items, fuel |
| [Weapons Filter](https://dontstarve.fandom.com/wiki/Weapons_Filter) | Done | dont_starve_together |
| [Weather Pain](https://dontstarve.fandom.com/wiki/Weather_Pain) | Done | craftable_items, dont_starve_together, equipable_items, fight_tab |
| [Webber](https://dontstarve.fandom.com/wiki/Webber) | Done | dont_starve_together |
| [Webby Whistle](https://dontstarve.fandom.com/wiki/Webby_Whistle) | Done | craftable_items, dont_starve_together |
| [Weeds](https://dontstarve.fandom.com/wiki/Weeds) | Done | dont_starve_together |
| [Weight](https://dontstarve.fandom.com/wiki/Weight) | Done | dont_starve_together |
| [Wet Goop](https://dontstarve.fandom.com/wiki/Wet_Goop) | Done | crock_pot_recipes |
| [Wetness](https://dontstarve.fandom.com/wiki/Wetness) | Done | dont_starve_together |
| [Wheat](https://dontstarve.fandom.com/wiki/Wheat) | Done | dont_starve_together, events |
| [Whirly Fan](https://dontstarve.fandom.com/wiki/Whirly_Fan) | Done | clothing_filter, cooling, craftable_items, dont_starve_together, equipable_items |
| [Whispering Grand Armor](https://dontstarve.fandom.com/wiki/Whispering_Grand_Armor) | Done | dont_starve_together |
| [Wigfrid](https://dontstarve.fandom.com/wiki/Wigfrid) | Done | dont_starve_together |
| [Reign of Giants](https://dontstarve.fandom.com/wiki/Wigfrid/Reign_of_Giants) | Done | dont_starve_together |
| [Wild Rift Cycle](https://dontstarve.fandom.com/wiki/Wild_Rift_Cycle) | Done | dont_starve_together, from_beyond |
| [Willow's Lighter](https://dontstarve.fandom.com/wiki/Willow's_Lighter) | Done | cooking_filter, craftable_items, equipable_items |
| [Don't Starve Together](https://dontstarve.fandom.com/wiki/Wilson/Don't_Starve_Together) | Done | dont_starve_together |
| [Winona](https://dontstarve.fandom.com/wiki/Winona) | Done | dont_starve_together |
| [Winona clothes](https://dontstarve.fandom.com/wiki/Winona_clothes) | Done | dont_starve_together |
| [Winona's Catapult](https://dontstarve.fandom.com/wiki/Winona's_Catapult) | Done | craftable_items, craftable_structures, dont_starve_together, followers |
| [Winona's G.E.M.erator](https://dontstarve.fandom.com/wiki/Winona's_G.E.M.erator) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Winona's Generator](https://dontstarve.fandom.com/wiki/Winona's_Generator) | Done | craftable_items, craftable_structures, dont_starve_together |
| [Winona's Spotlight](https://dontstarve.fandom.com/wiki/Winona's_Spotlight) | Done | craftable_structures, dont_starve_together |
| [Winter Hat](https://dontstarve.fandom.com/wiki/Winter_Hat) | Done | craftable_items, equipable_items |
| [Winter Items Filter](https://dontstarve.fandom.com/wiki/Winter_Items_Filter) | Done | dont_starve_together |
| [Winter's Feast](https://dontstarve.fandom.com/wiki/Winter's_Feast) | Done | dont_starve_together, events |
| [Wobster](https://dontstarve.fandom.com/wiki/Wobster) | Done | dont_starve_together, fishes, food |
| [Wobster Bisque](https://dontstarve.fandom.com/wiki/Wobster_Bisque) | Done | cooling, crock_pot_recipes, dont_starve_together, food |
| [Wobster Dinner](https://dontstarve.fandom.com/wiki/Wobster_Dinner) | Done | craftable_items, crock_pot_recipes, dont_starve_together, fishes |
| [Wobster Mound](https://dontstarve.fandom.com/wiki/Wobster_Mound) | Done | dont_starve_together |
| [Woby](https://dontstarve.fandom.com/wiki/Woby) | Done | dont_starve_together |
| [Wonkey](https://dontstarve.fandom.com/wiki/Wonkey) | Done | dont_starve_together |
| [Wood Fence](https://dontstarve.fandom.com/wiki/Wood_Fence) | Done | a_new_reign, craftable_items, craftable_structures, decorations_filter |
| [Wood Gate](https://dontstarve.fandom.com/wiki/Wood_Gate) | Done | a_new_reign, craftable_items, decorations_filter |
| [Wood Wall](https://dontstarve.fandom.com/wiki/Wood_Wall) | Done | craftable_items, craftable_structures, decorations_filter |
| [Wooden Flooring](https://dontstarve.fandom.com/wiki/Wooden_Flooring) | Done | craftable_items, decorations_filter, fuel |
| [Wooden Walking Stick](https://dontstarve.fandom.com/wiki/Wooden_Walking_Stick) | Done | clothing_filter, craftable_items, dont_starve_together |
| [Don't Starve Together](https://dontstarve.fandom.com/wiki/World_Customization/Don't_Starve_Together) | Done | dont_starve_together |
| [Wormwood](https://dontstarve.fandom.com/wiki/Wormwood) | Done | dont_starve_together |
| [Wortox](https://dontstarve.fandom.com/wiki/Wortox) | Done | dont_starve_together |
| [Wortox clothes](https://dontstarve.fandom.com/wiki/Wortox_clothes) | Done | dont_starve_together |
| [Woven Shadow](https://dontstarve.fandom.com/wiki/Woven_Shadow) | Done | a_new_reign, dont_starve_together |
| [Wurt](https://dontstarve.fandom.com/wiki/Wurt) | Done | dont_starve_together |
| [Wurt clothes](https://dontstarve.fandom.com/wiki/Wurt_clothes) | Done | dont_starve_together |
| [Year of the Beefalo](https://dontstarve.fandom.com/wiki/Year_of_the_Beefalo) | Done | dont_starve_together, events |
| [Year of the Bunnyman](https://dontstarve.fandom.com/wiki/Year_of_the_Bunnyman) | Done | dont_starve_together, events |
| [Year of the Carrat](https://dontstarve.fandom.com/wiki/Year_of_the_Carrat) | Done | dont_starve_together, events |
| [Year of the Catcoon](https://dontstarve.fandom.com/wiki/Year_of_the_Catcoon) | Done | dont_starve_together, events |
| [Year of the Dragonfly](https://dontstarve.fandom.com/wiki/Year_of_the_Dragonfly) | Done | dont_starve_together, events |
| [Year of the Gobbler](https://dontstarve.fandom.com/wiki/Year_of_the_Gobbler) | Done | dont_starve_together, events |
| [Year of the Pig King](https://dontstarve.fandom.com/wiki/Year_of_the_Pig_King) | Done | dont_starve_together, events |
| [Year of the Varg](https://dontstarve.fandom.com/wiki/Year_of_the_Varg) | Done | dont_starve_together, events |
| [Yellow Gem](https://dontstarve.fandom.com/wiki/Yellow_Gem) | Done | boss_dropped_items, craftable_items |

Khi thêm Category khác, crawler tự thêm URL/category/status vào live registry.
Sau mỗi batch đã review, export JSON snapshot rồi cập nhật bảng MD này để handoff.
