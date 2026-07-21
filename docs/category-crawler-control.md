# Category crawler control

Registry máy đọc/ghi nằm tại `<git-common-dir>/category-crawler/`; file
`data/crawled/fandom-url-registry.json` và MD này chỉ là snapshot/bảng review.
Trạng thái chỉ gồm `New`, `Doing`, `Done`: URL mới/`New` được lấy tiếp, còn
`Doing` và `Done` phải skip network fetch.

> **Live audit 2026-07-21:** 729 URL hợp lệ, 706 `Done`, 23 `New`, 0 `Doing`,
> 0 artifact lỗi. 559 URL mới của batch 2 đã hoàn tất; 23 URL `New` còn lại chỉ
> thuộc Animals và chưa được yêu cầu crawl lại.

## Category queue

| Category | Source | Direct | Child category | Excluded | Publish candidates | Registry Done | Status |
|---|---|---:|---:|---:|---:|---:|---|
| animals | [Category:Animals](https://dontstarve.fandom.com/wiki/Category:Animals) | 35 | 4 | 6 | 29 | 6 | Partial |
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

## Shared item URLs

| Item URL | Status | Categories |
|---|---|---|
| [Abigail's Flower](https://dontstarve.fandom.com/wiki/Abigail's_Flower) | Done | craftable_items |
| [Accomploshrine](https://dontstarve.fandom.com/wiki/Accomploshrine) | Done | craftable_structures |
| [Ageless Watch](https://dontstarve.fandom.com/wiki/Ageless_Watch) | Done | craftable_items |
| [Alarming Clock](https://dontstarve.fandom.com/wiki/Alarming_Clock) | Done | craftable_items, equipable_items |
| [Alchemy Engine](https://dontstarve.fandom.com/wiki/Alchemy_Engine) | Done | craftable_structures |
| [Amberosia](https://dontstarve.fandom.com/wiki/Amberosia) | Done | crock_pot_recipes |
| [Anchor](https://dontstarve.fandom.com/wiki/Anchor) | Done | craftable_items, craftable_structures |
| [Ancient Anchor](https://dontstarve.fandom.com/wiki/Ancient_Anchor) | Done | events |
| [Ancient Brickwork](https://dontstarve.fandom.com/wiki/Ancient_Brickwork) | Done | craftable_items |
| [Ancient Flooring](https://dontstarve.fandom.com/wiki/Ancient_Flooring) | Done | craftable_items |
| [Ancient Key](https://dontstarve.fandom.com/wiki/Ancient_Key) | Done | boss_dropped_items |
| [Ancient Pseudoscience Station](https://dontstarve.fandom.com/wiki/Ancient_Pseudoscience_Station) | Done | crafting_stations |
| [Ancient Stonework](https://dontstarve.fandom.com/wiki/Ancient_Stonework) | Done | craftable_items |
| [Ancient Tilework](https://dontstarve.fandom.com/wiki/Ancient_Tilework) | Done | craftable_items |
| [Arboretum Experiment](https://dontstarve.fandom.com/wiki/Arboretum_Experiment) | Done | craftable_items, events |
| [Armermry](https://dontstarve.fandom.com/wiki/Armermry) | Done | craftable_structures |
| [Art?](https://dontstarve.fandom.com/wiki/Art%3F) | Done | craftable_items, decorations_filter |
| [Asparagus](https://dontstarve.fandom.com/wiki/Asparagus) | Done | food |
| [Asparagus Soup](https://dontstarve.fandom.com/wiki/Asparagus_Soup) | Done | crock_pot_recipes |
| [Astral Detector](https://dontstarve.fandom.com/wiki/Astral_Detector) | Done | craftable_items |
| [Astroggles](https://dontstarve.fandom.com/wiki/Astroggles) | Done | craftable_items, equipable_items |
| [Axe](https://dontstarve.fandom.com/wiki/Axe) | Done | celestial_tab, craftable_items, equipable_items |
| [Axe](https://dontstarve.fandom.com/wiki/Pick/Axe) | Done | craftable_items, equipable_items |
| [Backpack](https://dontstarve.fandom.com/wiki/Backpack) | Done | backpacks, containers, craftable_items, equipable_items |
| [Backstep Watch](https://dontstarve.fandom.com/wiki/Backstep_Watch) | Done | craftable_items |
| [Backtrek Watch](https://dontstarve.fandom.com/wiki/Backtrek_Watch) | Done | craftable_items |
| [Bacon and Eggs](https://dontstarve.fandom.com/wiki/Bacon_and_Eggs) | Done | craftable_items, crock_pot_recipes, eggs |
| [Banana](https://dontstarve.fandom.com/wiki/Banana) | Done | food |
| [Banana Pop](https://dontstarve.fandom.com/wiki/Banana_Pop) | Done | cooling, crock_pot_recipes, food |
| [Banana Shake](https://dontstarve.fandom.com/wiki/Banana_Shake) | Done | crock_pot_recipes, food |
| [Barnacle Linguine](https://dontstarve.fandom.com/wiki/Barnacle_Linguine) | Done | crock_pot_recipes, food |
| [Barnacle Pita](https://dontstarve.fandom.com/wiki/Barnacle_Pita) | Done | crock_pot_recipes, food |
| [Barnacles](https://dontstarve.fandom.com/wiki/Barnacles) | Done | food |
| [Bat Bat](https://dontstarve.fandom.com/wiki/Bat_Bat) | Done | craftable_items, equipable_items |
| [Bath Bomb](https://dontstarve.fandom.com/wiki/Bath_Bomb) | Done | celestial_filter, craftable_items |
| [Batilisk](https://dontstarve.fandom.com/wiki/Batilisk) | Done | cave_creatures |
| [Batilisk Wing](https://dontstarve.fandom.com/wiki/Batilisk_Wing) | Done | food |
| [Battle Call Canister](https://dontstarve.fandom.com/wiki/Battle_Call_Canister) | Done | craftable_items |
| [Battle Helm](https://dontstarve.fandom.com/wiki/Battle_Helm) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Battle Paddle](https://dontstarve.fandom.com/wiki/Battle_Paddle) | Done | equipable_items |
| [Battle Rönd](https://dontstarve.fandom.com/wiki/Battle_R%C3%B6nd) | Done | armour_filter, craftable_items |
| [Battle Spear](https://dontstarve.fandom.com/wiki/Battle_Spear) | Done | craftable_items, equipable_items, fight_tab |
| [Battlemaster Pugna](https://dontstarve.fandom.com/wiki/Battlemaster_Pugna) | Done | events |
| [Beard Hair](https://dontstarve.fandom.com/wiki/Beard_Hair) | Done | craftable_items |
| [Beard Hair Rug](https://dontstarve.fandom.com/wiki/Beard_Hair_Rug) | Done | craftable_items |
| [Bed Roll](https://dontstarve.fandom.com/wiki/Bed_Roll) | Done | craftable_items |
| [Bee](https://dontstarve.fandom.com/wiki/Bee) | New | animals |
| [Bee Box](https://dontstarve.fandom.com/wiki/Bee_Box) | Done | craftable_structures |
| [Bee Mine](https://dontstarve.fandom.com/wiki/Bee_Mine) | Done | craftable_items, fight_tab |
| [Bee Queen Crown](https://dontstarve.fandom.com/wiki/Bee_Queen_Crown) | Done | boss_dropped_items, equipable_items |
| [Beefalo](https://dontstarve.fandom.com/wiki/Beefalo) | New | animals |
| [Beefalo Bell](https://dontstarve.fandom.com/wiki/Beefalo_Bell) | Done | craftable_items |
| [Beefalo Gloom Bell](https://dontstarve.fandom.com/wiki/Beefalo_Gloom_Bell) | Done | craftable_items |
| [Beefalo Grooming Station](https://dontstarve.fandom.com/wiki/Beefalo_Grooming_Station) | Done | craftable_structures, decorations_filter |
| [Beefalo Hat](https://dontstarve.fandom.com/wiki/Beefalo_Hat) | Done | clothing_filter, craftable_items, equipable_items |
| [Beefalo Treats](https://dontstarve.fandom.com/wiki/Beefalo_Treats) | Done | beefalo_foods, crock_pot_recipes |
| [Beefalo Wool](https://dontstarve.fandom.com/wiki/Beefalo_Wool) | Done | craftable_items |
| [Beefy Greens](https://dontstarve.fandom.com/wiki/Beefy_Greens) | Done | crock_pot_recipes, food |
| [Beekeeper Hat](https://dontstarve.fandom.com/wiki/Beekeeper_Hat) | Done | armour_filter, craftable_items, equipable_items |
| [Beeswax](https://dontstarve.fandom.com/wiki/Beeswax) | Done | craftable_items |
| [Belt of Hunger](https://dontstarve.fandom.com/wiki/Belt_of_Hunger) | Done | craftable_items, equipable_items |
| [Benevolent Rabbit King](https://dontstarve.fandom.com/wiki/Benevolent_Rabbit_King) | Done | crafting_stations |
| [Bernie](https://dontstarve.fandom.com/wiki/Bernie) | Done | equipable_items |
| [Berries](https://dontstarve.fandom.com/wiki/Berries) | Done | food |
| [Billy](https://dontstarve.fandom.com/wiki/Billy) | Done | events |
| [Bio Scanalyzer](https://dontstarve.fandom.com/wiki/Bio_Scanalyzer) | Done | craftable_items |
| [Birchnut](https://dontstarve.fandom.com/wiki/Birchnut) | Done | food |
| [Bird Trap](https://dontstarve.fandom.com/wiki/Bird_Trap) | Done | craftable_items |
| [Birdcage](https://dontstarve.fandom.com/wiki/Birdcage) | Done | craftable_structures |
| [Blood Shot](https://dontstarve.fandom.com/wiki/Blood_Shot) | Done | craftable_items |
| [Blue Cap](https://dontstarve.fandom.com/wiki/Blue_Cap) | Done | boss_dropped_items, food |
| [Blue Gem](https://dontstarve.fandom.com/wiki/Blue_Gem) | Done | boss_dropped_items, craftable_items |
| [Blueprint](https://dontstarve.fandom.com/wiki/Blueprint) | Done | boss_dropped_items, craftable_items |
| [Boards](https://dontstarve.fandom.com/wiki/Boards) | Done | craftable_items |
| [Boarilla](https://dontstarve.fandom.com/wiki/Boarilla) | Done | events |
| [Boat](https://dontstarve.fandom.com/wiki/Boat) | Done | craftable_items, craftable_structures |
| [Boat Patch](https://dontstarve.fandom.com/wiki/Boat_Patch) | Done | craftable_items |
| [Bone Armor](https://dontstarve.fandom.com/wiki/Bone_Armor) | Done | boss_dropped_items, equipable_items |
| [Bone Helm](https://dontstarve.fandom.com/wiki/Bone_Helm) | Done | boss_dropped_items, equipable_items |
| [Bone Shards](https://dontstarve.fandom.com/wiki/Bone_Shards) | Done | craftable_items |
| [Bookcase](https://dontstarve.fandom.com/wiki/Bookcase) | Done | craftable_structures |
| [Boomerang](https://dontstarve.fandom.com/wiki/Boomerang) | Done | craftable_items, equipable_items, fight_tab |
| [Booster Shot](https://dontstarve.fandom.com/wiki/Booster_Shot) | Done | craftable_items |
| [Bramble Husk](https://dontstarve.fandom.com/wiki/Bramble_Husk) | Done | armour_filter, craftable_items, equipable_items |
| [Bramble Trap](https://dontstarve.fandom.com/wiki/Bramble_Trap) | Done | craftable_items |
| [Brambleshade Armor](https://dontstarve.fandom.com/wiki/Brambleshade_Armor) | Done | craftable_items |
| [Breakfast Skillet](https://dontstarve.fandom.com/wiki/Breakfast_Skillet) | Done | crock_pot_recipes, food |
| [Breezy Vest](https://dontstarve.fandom.com/wiki/Breezy_Vest) | Done | craftable_items, equipable_items |
| [Bright-Eyed Frog](https://dontstarve.fandom.com/wiki/Bright-Eyed_Frog) | New | animals |
| [Brightshade Armor](https://dontstarve.fandom.com/wiki/Brightshade_Armor) | Done | armour_filter, craftable_items |
| [Brightshade Bomb](https://dontstarve.fandom.com/wiki/Brightshade_Bomb) | Done | craftable_items |
| [Brightshade Helm](https://dontstarve.fandom.com/wiki/Brightshade_Helm) | Done | armour_filter, craftable_items |
| [Brightshade Shoevel](https://dontstarve.fandom.com/wiki/Brightshade_Shoevel) | Done | craftable_items |
| [Brightshade Smasher](https://dontstarve.fandom.com/wiki/Brightshade_Smasher) | Done | craftable_items |
| [Brightshade Staff](https://dontstarve.fandom.com/wiki/Brightshade_Staff) | Done | craftable_items |
| [Brightshade Sword](https://dontstarve.fandom.com/wiki/Brightshade_Sword) | Done | craftable_items |
| [Brightsmithy](https://dontstarve.fandom.com/wiki/Brightsmithy) | Done | celestial_filter, craftable_items, craftable_structures, crafting_stations |
| [Brilliant Mudslinger](https://dontstarve.fandom.com/wiki/Brilliant_Mudslinger) | Done | craftable_items |
| [Brush](https://dontstarve.fandom.com/wiki/Brush) | Done | craftable_items, equipable_items |
| [Bucket-o-poop](https://dontstarve.fandom.com/wiki/Bucket-o-poop) | Done | craftable_items, fertilizer |
| [Bug Net](https://dontstarve.fandom.com/wiki/Bug_Net) | Done | craftable_items, equipable_items |
| [Bulbous Lightbug](https://dontstarve.fandom.com/wiki/Bulbous_Lightbug) | Done | animals, cave_creatures |
| [Bull Kelp](https://dontstarve.fandom.com/wiki/Bull_Kelp) | Done | equipable_items |
| [Bumpers](https://dontstarve.fandom.com/wiki/Bumpers) | Done | craftable_items, craftable_structures |
| [Bundling Wrap](https://dontstarve.fandom.com/wiki/Bundling_Wrap) | Done | containers, craftable_items |
| [Bunny Stew](https://dontstarve.fandom.com/wiki/Bunny_Stew) | Done | crock_pot_recipes, food |
| [Bunnyman](https://dontstarve.fandom.com/wiki/Bunnyman) | Done | animals, cave_creatures |
| [Burrowing Horn](https://dontstarve.fandom.com/wiki/Burrowing_Horn) | Done | craftable_items, equipable_items |
| [Bush Hat](https://dontstarve.fandom.com/wiki/Bush_Hat) | Done | craftable_items, equipable_items |
| [Butter Muffin](https://dontstarve.fandom.com/wiki/Butter_Muffin) | Done | crock_pot_recipes, food |
| [Butterfly](https://dontstarve.fandom.com/wiki/Butterfly) | New | animals |
| [Buzzard](https://dontstarve.fandom.com/wiki/Buzzard) | New | animals |
| [Cactus Flesh](https://dontstarve.fandom.com/wiki/Cactus_Flesh) | Done | food |
| [Cactus Flower](https://dontstarve.fandom.com/wiki/Cactus_Flower) | Done | food |
| [California Roll](https://dontstarve.fandom.com/wiki/California_Roll) | Done | crock_pot_recipes, food |
| [Campfire](https://dontstarve.fandom.com/wiki/Campfire) | Done | cooking_filter, craftable_structures |
| [Cannon](https://dontstarve.fandom.com/wiki/Cannon) | Done | craftable_items, craftable_structures |
| [Cannonball](https://dontstarve.fandom.com/wiki/Cannonball) | Done | craftable_items |
| [Captain's Tricorn](https://dontstarve.fandom.com/wiki/Captain's_Tricorn) | Done | equipable_items |
| [Carpeted Flooring](https://dontstarve.fandom.com/wiki/Carpeted_Flooring) | Done | craftable_items, decorations_filter |
| [Carrot](https://dontstarve.fandom.com/wiki/Carrot) | Done | food |
| [Cartographer's Desk](https://dontstarve.fandom.com/wiki/Cartographer's_Desk) | Done | craftable_structures, crafting_stations |
| [Cat Cap](https://dontstarve.fandom.com/wiki/Cat_Cap) | Done | craftable_items, equipable_items |
| [Catcoon](https://dontstarve.fandom.com/wiki/Catcoon) | New | animals |
| [Cave Rock Turf](https://dontstarve.fandom.com/wiki/Cave_Rock_Turf) | Done | craftable_items, decorations_filter |
| [Cave Spider](https://dontstarve.fandom.com/wiki/Cave_Spider) | Done | cave_creatures |
| [Celestial Orb](https://dontstarve.fandom.com/wiki/Celestial_Orb) | Done | crafting_stations |
| [Celestial Portal](https://dontstarve.fandom.com/wiki/Celestial_Portal) | Done | craftable_structures |
| [Ceviche](https://dontstarve.fandom.com/wiki/Ceviche) | Done | cooling, crock_pot_recipes, food |
| [Charcoal](https://dontstarve.fandom.com/wiki/Charcoal) | Done | boss_dropped_items |
| [Checkerboard Flooring](https://dontstarve.fandom.com/wiki/Checkerboard_Flooring) | Done | craftable_items, decorations_filter |
| [Chef Pouch](https://dontstarve.fandom.com/wiki/Chef_Pouch) | Done | backpacks, containers, cooking_filter, craftable_items, equipable_items |
| [Chest](https://dontstarve.fandom.com/wiki/Chest) | Done | containers, craftable_structures |
| [Chester](https://dontstarve.fandom.com/wiki/Chester) | Done | containers |
| [Chili Flakes](https://dontstarve.fandom.com/wiki/Chili_Flakes) | Done | craftable_items |
| [Chilled Amulet](https://dontstarve.fandom.com/wiki/Chilled_Amulet) | Done | cooling, craftable_items, equipable_items |
| [Circuit Extractor](https://dontstarve.fandom.com/wiki/Circuit_Extractor) | Done | craftable_items |
| [Clean Sweeper](https://dontstarve.fandom.com/wiki/Clean_Sweeper) | Done | craftable_items, decorations_filter, equipable_items |
| [Clever Disguise](https://dontstarve.fandom.com/wiki/Clever_Disguise) | Done | craftable_items, equipable_items |
| [Clockmaker's Tools](https://dontstarve.fandom.com/wiki/Clockmaker's_Tools) | Done | craftable_items |
| [Clockwork Bishop](https://dontstarve.fandom.com/wiki/Clockwork_Bishop) | Done | cave_creatures |
| [Coaching Whistle](https://dontstarve.fandom.com/wiki/Coaching_Whistle) | Done | craftable_items |
| [Coat of Carrots](https://dontstarve.fandom.com/wiki/Coat_of_Carrots) | Done | craftable_items, craftable_structures, equipable_items |
| [Cobblestones](https://dontstarve.fandom.com/wiki/Cobblestones) | Done | craftable_items, decorations_filter |
| [Codex Umbra](https://dontstarve.fandom.com/wiki/Codex_Umbra) | Done | craftable_items, crafting_stations |
| [Collected Dust](https://dontstarve.fandom.com/wiki/Collected_Dust) | Done | craftable_items |
| [Commander's Helm](https://dontstarve.fandom.com/wiki/Commander's_Helm) | Done | armour_filter, craftable_items |
| [Communal Kelp Dish](https://dontstarve.fandom.com/wiki/Communal_Kelp_Dish) | Done | craftable_structures |
| [Compass](https://dontstarve.fandom.com/wiki/Compass) | Done | craftable_items, equipable_items |
| [Compost](https://dontstarve.fandom.com/wiki/Compost) | Done | fertilizer |
| [Compost Wrap](https://dontstarve.fandom.com/wiki/Compost_Wrap) | Done | craftable_items, fertilizer |
| [Composting Bin](https://dontstarve.fandom.com/wiki/Composting_Bin) | Done | craftable_structures |
| [Construction Amulet](https://dontstarve.fandom.com/wiki/Construction_Amulet) | Done | craftable_items, equipable_items |
| [Cookbook](https://dontstarve.fandom.com/wiki/Cookbook) | Done | cooking_filter, craftable_items |
| [Cookie Cutter Cap](https://dontstarve.fandom.com/wiki/Cookie_Cutter_Cap) | Done | armour_filter, craftable_items, equipable_items |
| [Corn](https://dontstarve.fandom.com/wiki/Corn) | Done | food |
| [Crab Meat](https://dontstarve.fandom.com/wiki/Crab_Meat) | Done | events, food |
| [Crabby Hermit](https://dontstarve.fandom.com/wiki/Crabby_Hermit) | Done | crafting_stations |
| [Craftsmerm House](https://dontstarve.fandom.com/wiki/Craftsmerm_House) | Done | craftable_structures |
| [Cratered Moonrock](https://dontstarve.fandom.com/wiki/Cratered_Moonrock) | Done | craftable_items |
| [Creamy Potato Purée](https://dontstarve.fandom.com/wiki/Creamy_Potato_Pur%C3%A9e) | Done | crock_pot_recipes, food |
| [Crock Pot](https://dontstarve.fandom.com/wiki/Crock_Pot) | Done | containers, cooking_filter, craftable_structures |
| [Crocommander](https://dontstarve.fandom.com/wiki/Crocommander) | Done | events |
| [Cut Grass](https://dontstarve.fandom.com/wiki/Cut_Grass) | Done | beefalo_foods |
| [Cut Reeds](https://dontstarve.fandom.com/wiki/Cut_Reeds) | Done | beefalo_foods |
| [Cut Stone](https://dontstarve.fandom.com/wiki/Cut_Stone) | Done | craftable_items |
| [Cutless](https://dontstarve.fandom.com/wiki/Cutless) | Done | equipable_items |
| [Dangling Depth Dweller](https://dontstarve.fandom.com/wiki/Dangling_Depth_Dweller) | Done | cave_creatures |
| [Dapper Vest](https://dontstarve.fandom.com/wiki/Dapper_Vest) | Done | craftable_items, equipable_items |
| [Dark Sword](https://dontstarve.fandom.com/wiki/Dark_Sword) | Done | boss_dropped_items, craftable_items, equipable_items |
| [Dark Tatters](https://dontstarve.fandom.com/wiki/Dark_Tatters) | Done | boss_dropped_items |
| [Deciduous Turf](https://dontstarve.fandom.com/wiki/Deciduous_Turf) | Done | craftable_items, decorations_filter |
| [Deck Illuminator](https://dontstarve.fandom.com/wiki/Deck_Illuminator) | Done | craftable_items |
| [Deconstruction Staff](https://dontstarve.fandom.com/wiki/Deconstruction_Staff) | Done | craftable_items, equipable_items |
| [Deerclops Eyeball](https://dontstarve.fandom.com/wiki/Deerclops_Eyeball) | Done | boss_dropped_items, food |
| [Den Decorating Set](https://dontstarve.fandom.com/wiki/Den_Decorating_Set) | Done | craftable_items |
| [Depths Worm](https://dontstarve.fandom.com/wiki/Depths_Worm) | Done | cave_creatures |
| [Desert Stone](https://dontstarve.fandom.com/wiki/Desert_Stone) | Done | boss_dropped_items |
| [Directional Sign](https://dontstarve.fandom.com/wiki/Directional_Sign) | Done | craftable_structures, decorations_filter |
| [Dock Kit](https://dontstarve.fandom.com/wiki/Dock_Kit) | Done | craftable_items, decorations_filter |
| [Dock Piling Kit](https://dontstarve.fandom.com/wiki/Dock_Piling_Kit) | Done | craftable_items, decorations_filter |
| [Down Feather](https://dontstarve.fandom.com/wiki/Down_Feather) | Done | boss_dropped_items |
| [Dragon Fruit](https://dontstarve.fandom.com/wiki/Dragon_Fruit) | Done | food |
| [Dragonpie](https://dontstarve.fandom.com/wiki/Dragonpie) | Done | crock_pot_recipes, food |
| [Dreaded Mudslinger](https://dontstarve.fandom.com/wiki/Dreaded_Mudslinger) | Done | craftable_items |
| [Dreadstone](https://dontstarve.fandom.com/wiki/Dreadstone) | Done | craftable_items |
| [Dreadstone Armor](https://dontstarve.fandom.com/wiki/Dreadstone_Armor) | Done | armour_filter, craftable_items |
| [Dreadstone Helm](https://dontstarve.fandom.com/wiki/Dreadstone_Helm) | Done | armour_filter, craftable_items |
| [Dreadstone Wall](https://dontstarve.fandom.com/wiki/Dreadstone_Wall) | Done | craftable_items |
| [Drumstick](https://dontstarve.fandom.com/wiki/Drumstick) | Done | boss_dropped_items, food |
| [Drying Rack](https://dontstarve.fandom.com/wiki/Drying_Rack) | Done | cooking_filter, craftable_structures |
| [Durian](https://dontstarve.fandom.com/wiki/Durian) | Done | food |
| [Dust Moth](https://dontstarve.fandom.com/wiki/Dust_Moth) | Done | animals, cave_creatures |
| [Eel](https://dontstarve.fandom.com/wiki/Eel) | Done | fishes, food |
| [Egg](https://dontstarve.fandom.com/wiki/Egg) | Done | eggs, food |
| [Eggplant](https://dontstarve.fandom.com/wiki/Eggplant) | Done | food |
| [Elastispacer](https://dontstarve.fandom.com/wiki/Elastispacer) | Done | craftable_items |
| [Elding Spear](https://dontstarve.fandom.com/wiki/Elding_Spear) | Done | craftable_items |
| [Electric Milk](https://dontstarve.fandom.com/wiki/Electric_Milk) | Done | food |
| [Electrical Doodad](https://dontstarve.fandom.com/wiki/Electrical_Doodad) | Done | craftable_items |
| [Embalming Spritz](https://dontstarve.fandom.com/wiki/Embalming_Spritz) | Done | craftable_items |
| [Empty Bottle](https://dontstarve.fandom.com/wiki/Empty_Bottle) | Done | craftable_items |
| [Empty Frame](https://dontstarve.fandom.com/wiki/Empty_Frame) | Done | craftable_items, decorations_filter |
| [Endothermic Fire](https://dontstarve.fandom.com/wiki/Endothermic_Fire) | Done | cooling, craftable_structures |
| [Enlightened Crown](https://dontstarve.fandom.com/wiki/Enlightened_Crown) | Done | boss_dropped_items, equipable_items |
| [Ewecus](https://dontstarve.fandom.com/wiki/Ewecus) | New | animals |
| [Eye Mask](https://dontstarve.fandom.com/wiki/Eye_Mask) | Done | boss_dropped_items, equipable_items |
| [Eyebrella](https://dontstarve.fandom.com/wiki/Eyebrella) | Done | cooling, craftable_items, equipable_items |
| [Fancy Spiralled Tubers](https://dontstarve.fandom.com/wiki/Fancy_Spiralled_Tubers) | Done | crock_pot_recipes, food |
| [Fashion Melon](https://dontstarve.fandom.com/wiki/Fashion_Melon) | Done | cooling, craftable_items, equipable_items |
| [Feather Hat](https://dontstarve.fandom.com/wiki/Feather_Hat) | Done | craftable_items, equipable_items |
| [Feather Pencil](https://dontstarve.fandom.com/wiki/Feather_Pencil) | Done | craftable_items, decorations_filter |
| [Feathery Canvas](https://dontstarve.fandom.com/wiki/Feathery_Canvas) | Done | craftable_items |
| [Fencing Sword](https://dontstarve.fandom.com/wiki/Fencing_Sword) | Done | craftable_items |
| [Fertilizzzer](https://dontstarve.fandom.com/wiki/Fertilizzzer) | Done | craftable_items, fertilizer |
| [Fiery Pen](https://dontstarve.fandom.com/wiki/Fiery_Pen) | Done | equipable_items |
| [Fig](https://dontstarve.fandom.com/wiki/Fig) | Done | food |
| [Fig-Stuffed Trunk](https://dontstarve.fandom.com/wiki/Fig-Stuffed_Trunk) | Done | crock_pot_recipes, food |
| [Figatoni](https://dontstarve.fandom.com/wiki/Figatoni) | Done | craftable_items, crock_pot_recipes, food |
| [Figgy Frogwich](https://dontstarve.fandom.com/wiki/Figgy_Frogwich) | Done | crock_pot_recipes, food |
| [Figkabab](https://dontstarve.fandom.com/wiki/Figkabab) | Done | crock_pot_recipes, food |
| [Fire Pump](https://dontstarve.fandom.com/wiki/Fire_Pump) | Done | craftable_items, craftable_structures |
| [Fire Staff](https://dontstarve.fandom.com/wiki/Fire_Staff) | Done | craftable_items, equipable_items |
| [Fireflies](https://dontstarve.fandom.com/wiki/Fireflies) | Done | cave_creatures |
| [Fish](https://dontstarve.fandom.com/wiki/Fish) | Done | fishes, food |
| [Fish Food](https://dontstarve.fandom.com/wiki/Fish_Food) | Done | craftable_items |
| [Fish Morsel](https://dontstarve.fandom.com/wiki/Fish_Morsel) | Done | fishes, food |
| [Fish Scale-O-Matic](https://dontstarve.fandom.com/wiki/Fish_Scale-O-Matic) | Done | craftable_structures, decorations_filter |
| [Fish Tacos](https://dontstarve.fandom.com/wiki/Fish_Tacos) | Done | crock_pot_recipes, food |
| [Fishing Rod](https://dontstarve.fandom.com/wiki/Fishing_Rod) | Done | craftable_items, equipable_items |
| [Fishsticks](https://dontstarve.fandom.com/wiki/Fishsticks) | Done | crock_pot_recipes, food |
| [Fist Full of Jam](https://dontstarve.fandom.com/wiki/Fist_Full_of_Jam) | Done | craftable_items, crock_pot_recipes, food |
| [Flare](https://dontstarve.fandom.com/wiki/Flare) | Done | craftable_items |
| [Fleshy Bulb](https://dontstarve.fandom.com/wiki/Fleshy_Bulb) | Done | craftable_items |
| [Flint](https://dontstarve.fandom.com/wiki/Flint) | Done | craftable_items |
| [Floating Lantern](https://dontstarve.fandom.com/wiki/Floating_Lantern) | Done | craftable_items |
| [Floral Shirt](https://dontstarve.fandom.com/wiki/Floral_Shirt) | Done | cooling, craftable_items, equipable_items |
| [Flower Salad](https://dontstarve.fandom.com/wiki/Flower_Salad) | Done | crock_pot_recipes, food |
| [Football Helmet](https://dontstarve.fandom.com/wiki/Football_Helmet) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Forest Turf](https://dontstarve.fandom.com/wiki/Forest_Turf) | Done | craftable_items, decorations_filter |
| [Forge Portal](https://dontstarve.fandom.com/wiki/Forge_Portal) | Done | events |
| [Fossils](https://dontstarve.fandom.com/wiki/Fossils) | Done | boss_dropped_items |
| [Fresh Fruit Crepes](https://dontstarve.fandom.com/wiki/Fresh_Fruit_Crepes) | Done | food |
| [Friendly Fruit Fly Fruit](https://dontstarve.fandom.com/wiki/Friendly_Fruit_Fly_Fruit) | Done | boss_dropped_items |
| [Friendly Scarecrow](https://dontstarve.fandom.com/wiki/Friendly_Scarecrow) | Done | craftable_structures |
| [Frog](https://dontstarve.fandom.com/wiki/Frog) | New | animals |
| [Frog Legs](https://dontstarve.fandom.com/wiki/Frog_Legs) | Done | boss_dropped_items, food |
| [Froggle Bunwich](https://dontstarve.fandom.com/wiki/Froggle_Bunwich) | Done | crock_pot_recipes |
| [Frozen Banana Daiquiri](https://dontstarve.fandom.com/wiki/Frozen_Banana_Daiquiri) | Done | cooling, crock_pot_recipes, food |
| [Fruit Medley](https://dontstarve.fandom.com/wiki/Fruit_Medley) | Done | cooling, crock_pot_recipes |
| [Funcap](https://dontstarve.fandom.com/wiki/Funcap) | Done | clothing_filter, craftable_items, equipable_items |
| [Fungal Turf](https://dontstarve.fandom.com/wiki/Fungal_Turf) | Done | craftable_items |
| [Fur Tuft](https://dontstarve.fandom.com/wiki/Fur_Tuft) | Done | boss_dropped_items |
| [Garden Digamajig](https://dontstarve.fandom.com/wiki/Garden_Digamajig) | Done | craftable_items |
| [Garden Hoe](https://dontstarve.fandom.com/wiki/Garden_Hoe) | Done | craftable_items, equipable_items |
| [Gardeneer Hat](https://dontstarve.fandom.com/wiki/Gardeneer_Hat) | Done | craftable_items, equipable_items |
| [Garland](https://dontstarve.fandom.com/wiki/Garland) | Done | craftable_items, equipable_items |
| [Garlic](https://dontstarve.fandom.com/wiki/Garlic) | Done | events, food |
| [Garlic Powder](https://dontstarve.fandom.com/wiki/Garlic_Powder) | Done | craftable_items |
| [Gears](https://dontstarve.fandom.com/wiki/Gears) | Done | food |
| [Gem Deer](https://dontstarve.fandom.com/wiki/Gem_Deer) | New | animals |
| [Glass Cutter](https://dontstarve.fandom.com/wiki/Glass_Cutter) | Done | celestial_filter, celestial_tab, craftable_items, equipable_items |
| [Glommer](https://dontstarve.fandom.com/wiki/Glommer) | New | animals |
| [Glommer's Goop](https://dontstarve.fandom.com/wiki/Glommer's_Goop) | Done | fertilizer, food |
| [Gloomerang](https://dontstarve.fandom.com/wiki/Gloomerang) | Done | craftable_items, equipable_items |
| [Glow Berry](https://dontstarve.fandom.com/wiki/Glow_Berry) | Done | food |
| [Glow Berry Mousse](https://dontstarve.fandom.com/wiki/Glow_Berry_Mousse) | Done | craftable_items, food |
| [Goat Milk](https://dontstarve.fandom.com/wiki/Goat_Milk) | Done | events |
| [Gobbler](https://dontstarve.fandom.com/wiki/Gobbler) | New | animals |
| [Gold Flooring](https://dontstarve.fandom.com/wiki/Gold_Flooring) | Done | craftable_items, decorations_filter |
| [Gold Nugget](https://dontstarve.fandom.com/wiki/Gold_Nugget) | Done | boss_dropped_items, craftable_items |
| [Goose Egg](https://dontstarve.fandom.com/wiki/Moose/Goose_Egg) | Done | eggs |
| [Gourmet Salt Lick](https://dontstarve.fandom.com/wiki/Gourmet_Salt_Lick) | Done | craftable_structures |
| [Gramophone](https://dontstarve.fandom.com/wiki/Gramophone) | Done | craftable_items, decorations_filter |
| [Grand Forge Boarrior](https://dontstarve.fandom.com/wiki/Grand_Forge_Boarrior) | Done | events |
| [Grass Gator](https://dontstarve.fandom.com/wiki/Grass_Gator) | New | animals |
| [Grass Raft](https://dontstarve.fandom.com/wiki/Grass_Raft) | Done | craftable_items, craftable_structures |
| [Grass Suit](https://dontstarve.fandom.com/wiki/Grass_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Grass Turf](https://dontstarve.fandom.com/wiki/Grass_Turf) | Done | craftable_items, decorations_filter |
| [Great Depths Worm](https://dontstarve.fandom.com/wiki/Great_Depths_Worm) | Done | cave_creatures |
| [Green Cap](https://dontstarve.fandom.com/wiki/Green_Cap) | Done | boss_dropped_items, food |
| [Green Gem](https://dontstarve.fandom.com/wiki/Green_Gem) | Done | boss_dropped_items, craftable_items |
| [Grim Galette](https://dontstarve.fandom.com/wiki/Grim_Galette) | Done | food |
| [Growth Formula Starter](https://dontstarve.fandom.com/wiki/Growth_Formula_Starter) | Done | craftable_items, fertilizer |
| [Guacamole](https://dontstarve.fandom.com/wiki/Guacamole) | Done | crock_pot_recipes, food |
| [Guano](https://dontstarve.fandom.com/wiki/Guano) | Done | fertilizer |
| [Guano Turf](https://dontstarve.fandom.com/wiki/Guano_Turf) | Done | craftable_items, decorations_filter |
| [Guardian's Horn](https://dontstarve.fandom.com/wiki/Guardian's_Horn) | Done | boss_dropped_items, food |
| [Gunpowder](https://dontstarve.fandom.com/wiki/Gunpowder) | Done | craftable_items |
| [Hallowed Nights](https://dontstarve.fandom.com/wiki/Hallowed_Nights) | Done | events |
| [Ham Bat](https://dontstarve.fandom.com/wiki/Ham_Bat) | Done | craftable_items, equipable_items, fight_tab |
| [Hammer](https://dontstarve.fandom.com/wiki/Hammer) | Done | craftable_items, equipable_items |
| [Handy Remote](https://dontstarve.fandom.com/wiki/Handy_Remote) | Done | craftable_items |
| [Hardwood Hat](https://dontstarve.fandom.com/wiki/Hardwood_Hat) | Done | armour_filter, craftable_items |
| [Hay Wall](https://dontstarve.fandom.com/wiki/Hay_Wall) | Done | craftable_items, craftable_structures, decorations_filter |
| [Healing Glop](https://dontstarve.fandom.com/wiki/Healing_Glop) | Done | craftable_items |
| [Healing Salve](https://dontstarve.fandom.com/wiki/Healing_Salve) | Done | craftable_items |
| [Hermit Home](https://dontstarve.fandom.com/wiki/Hermit_Home) | Done | craftable_structures |
| [Hibearnation Vest](https://dontstarve.fandom.com/wiki/Hibearnation_Vest) | Done | craftable_items, equipable_items |
| [Honey](https://dontstarve.fandom.com/wiki/Honey) | Done | boss_dropped_items, food |
| [Honey Crystals](https://dontstarve.fandom.com/wiki/Honey_Crystals) | Done | craftable_items |
| [Honey Ham](https://dontstarve.fandom.com/wiki/Honey_Ham) | Done | crock_pot_recipes, food |
| [Honey Nuggets](https://dontstarve.fandom.com/wiki/Honey_Nuggets) | Done | crock_pot_recipes |
| [Honey Poultice](https://dontstarve.fandom.com/wiki/Honey_Poultice) | Done | craftable_items |
| [Honeycomb](https://dontstarve.fandom.com/wiki/Honeycomb) | Done | boss_dropped_items |
| [Hostile Flare](https://dontstarve.fandom.com/wiki/Hostile_Flare) | Done | craftable_items |
| [Hound's Tooth](https://dontstarve.fandom.com/wiki/Hound's_Tooth) | Done | craftable_items |
| [Houndius Shootius](https://dontstarve.fandom.com/wiki/Houndius_Shootius) | Done | craftable_items, craftable_structures |
| [Howlitzer](https://dontstarve.fandom.com/wiki/Howlitzer) | Done | craftable_items, equipable_items |
| [Humble Lamb Idol](https://dontstarve.fandom.com/wiki/Humble_Lamb_Idol) | Done | cooking_filter, craftable_structures |
| [Hutch](https://dontstarve.fandom.com/wiki/Hutch) | Done | cave_creatures, containers |
| [Ice](https://dontstarve.fandom.com/wiki/Ice) | Done | cooling, food |
| [Ice Box](https://dontstarve.fandom.com/wiki/Ice_Box) | Done | containers, cooking_filter, craftable_structures |
| [Ice Cream](https://dontstarve.fandom.com/wiki/Ice_Cream) | Done | cooling, craftable_items, crock_pot_recipes |
| [Ice Crystaleyezer](https://dontstarve.fandom.com/wiki/Ice_Crystaleyezer) | Done | cooling, craftable_items, craftable_structures |
| [Ice Cube](https://dontstarve.fandom.com/wiki/Ice_Cube) | Done | cooling, craftable_items, equipable_items |
| [Ice Flingomatic](https://dontstarve.fandom.com/wiki/Ice_Flingomatic) | Done | craftable_structures |
| [Ice Staff](https://dontstarve.fandom.com/wiki/Ice_Staff) | Done | craftable_items, equipable_items |
| [Icker](https://dontstarve.fandom.com/wiki/Icker) | Done | cave_creatures |
| [Icker Preserve](https://dontstarve.fandom.com/wiki/Icker_Preserve) | Done | craftable_items, craftable_structures |
| [Infernal Swineclops](https://dontstarve.fandom.com/wiki/Infernal_Swineclops) | Done | events |
| [Infused Moon Shard](https://dontstarve.fandom.com/wiki/Infused_Moon_Shard) | Done | boss_dropped_items, craftable_items |
| [Ink Blight](https://dontstarve.fandom.com/wiki/Ink_Blight) | Done | cave_creatures |
| [Inspectacles](https://dontstarve.fandom.com/wiki/Inspectacles) | Done | clothing_filter, craftable_items |
| [Insulated Pack](https://dontstarve.fandom.com/wiki/Insulated_Pack) | Done | backpacks, containers, cooking_filter, craftable_items, equipable_items |
| [Iridescent Gem](https://dontstarve.fandom.com/wiki/Iridescent_Gem) | Done | craftable_items |
| [Jelly Salad](https://dontstarve.fandom.com/wiki/Jelly_Salad) | Done | crock_pot_recipes |
| [Jellybeans](https://dontstarve.fandom.com/wiki/Jellybeans) | Done | crock_pot_recipes, food |
| [Jerky](https://dontstarve.fandom.com/wiki/Jerky) | Done | craftable_items |
| [Juicy Berries](https://dontstarve.fandom.com/wiki/Juicy_Berries) | Done | food |
| [Juicy Berry Bush](https://dontstarve.fandom.com/wiki/Juicy_Berry_Bush) | Done | craftable_items |
| [Kabobs](https://dontstarve.fandom.com/wiki/Kabobs) | Done | craftable_items, crock_pot_recipes |
| [Kelp Fronds](https://dontstarve.fandom.com/wiki/Kelp_Fronds) | Done | food |
| [Kelp Patch](https://dontstarve.fandom.com/wiki/Kelp_Patch) | Done | craftable_items |
| [Key](https://dontstarve.fandom.com/wiki/Key) | Done | events |
| [Kitschy Idols](https://dontstarve.fandom.com/wiki/Kitschy_Idols) | Done | craftable_items |
| [Klaus](https://dontstarve.fandom.com/wiki/Klaus) | Done | events |
| [Koalefant](https://dontstarve.fandom.com/wiki/Koalefant) | New | animals |
| [Koalefant Trunk](https://dontstarve.fandom.com/wiki/Koalefant_Trunk) | Done | food |
| [Krampus Sack](https://dontstarve.fandom.com/wiki/Krampus_Sack) | Done | backpacks, boss_dropped_items, containers |
| [Lantern](https://dontstarve.fandom.com/wiki/Lantern) | Done | craftable_items, equipable_items |
| [Lavae Egg](https://dontstarve.fandom.com/wiki/Lavae_Egg) | Done | boss_dropped_items |
| [Leafy Meat](https://dontstarve.fandom.com/wiki/Leafy_Meat) | Done | food |
| [Leafy Meatloaf](https://dontstarve.fandom.com/wiki/Leafy_Meatloaf) | Done | crock_pot_recipes, food |
| [Lesser Glow Berry](https://dontstarve.fandom.com/wiki/Lesser_Glow_Berry) | Done | food |
| [Lichen](https://dontstarve.fandom.com/wiki/Lichen) | Done | food |
| [Life Giving Amulet](https://dontstarve.fandom.com/wiki/Life_Giving_Amulet) | Done | craftable_items, equipable_items |
| [Light Bulb](https://dontstarve.fandom.com/wiki/Light_Bulb) | Done | food |
| [Lightning Conductor](https://dontstarve.fandom.com/wiki/Lightning_Conductor) | Done | craftable_items |
| [Lightning Rod](https://dontstarve.fandom.com/wiki/Lightning_Rod) | Done | craftable_structures |
| [Lil' Itchy](https://dontstarve.fandom.com/wiki/Lil'_Itchy) | Done | craftable_items |
| [Living Log](https://dontstarve.fandom.com/wiki/Living_Log) | Done | boss_dropped_items, craftable_items |
| [Log](https://dontstarve.fandom.com/wiki/Log) | Done | craftable_items |
| [Log Suit](https://dontstarve.fandom.com/wiki/Log_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Loot Stash](https://dontstarve.fandom.com/wiki/Loot_Stash) | Done | events |
| [Lucky Beast](https://dontstarve.fandom.com/wiki/Lucky_Beast) | Done | craftable_items, equipable_items |
| [Lucy the Axe](https://dontstarve.fandom.com/wiki/Lucy_the_Axe) | Done | equipable_items |
| [Lunar Altars](https://dontstarve.fandom.com/wiki/Lunar_Altars) | Done | crafting_stations |
| [Lunar Experiment](https://dontstarve.fandom.com/wiki/Lunar_Experiment) | Done | craftable_items, events |
| [Lunar Funcap](https://dontstarve.fandom.com/wiki/Lunar_Funcap) | Done | celestial_filter, craftable_items, equipable_items |
| [Lunar Siphonator](https://dontstarve.fandom.com/wiki/Lunar_Siphonator) | Done | craftable_structures |
| [Lune Tree Blossom](https://dontstarve.fandom.com/wiki/Lune_Tree_Blossom) | Done | food |
| [Lurking Nightmare](https://dontstarve.fandom.com/wiki/Lurking_Nightmare) | Done | cave_creatures |
| [Lush Carpet](https://dontstarve.fandom.com/wiki/Lush_Carpet) | Done | craftable_items |
| [Luxury Fan](https://dontstarve.fandom.com/wiki/Luxury_Fan) | Done | cooling, craftable_items |
| [Magician's Chest](https://dontstarve.fandom.com/wiki/Magician's_Chest) | Done | craftable_structures |
| [Magician's Top Hat](https://dontstarve.fandom.com/wiki/Magician's_Top_Hat) | Done | craftable_items |
| [Magiluminescence](https://dontstarve.fandom.com/wiki/Magiluminescence) | Done | craftable_items, equipable_items |
| [Magma Golem](https://dontstarve.fandom.com/wiki/Magma_Golem) | Done | events |
| [Malbatross Bill](https://dontstarve.fandom.com/wiki/Malbatross_Bill) | Done | boss_dropped_items, equipable_items |
| [Malbatross Feather](https://dontstarve.fandom.com/wiki/Malbatross_Feather) | Done | boss_dropped_items |
| [Mandrake](https://dontstarve.fandom.com/wiki/Mandrake) | Done | food |
| [Mandrake Soup](https://dontstarve.fandom.com/wiki/Mandrake_Soup) | Done | craftable_items, crock_pot_recipes, food |
| [Mannequin](https://dontstarve.fandom.com/wiki/Mannequin) | Done | craftable_structures |
| [Manure](https://dontstarve.fandom.com/wiki/Manure) | Done | craftable_items, fertilizer |
| [Map Scroll](https://dontstarve.fandom.com/wiki/Map_Scroll) | Done | craftable_items |
| [Marble](https://dontstarve.fandom.com/wiki/Marble) | Done | craftable_items |
| [Marble Bean](https://dontstarve.fandom.com/wiki/Marble_Bean) | Done | craftable_items |
| [Marble Suit](https://dontstarve.fandom.com/wiki/Marble_Suit) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Marsh Turf](https://dontstarve.fandom.com/wiki/Marsh_Turf) | Done | craftable_items |
| [Mast](https://dontstarve.fandom.com/wiki/Mast) | Done | craftable_items |
| [Mealing Stone](https://dontstarve.fandom.com/wiki/Mealing_Stone) | Done | events |
| [Meat](https://dontstarve.fandom.com/wiki/Meat) | Done | boss_dropped_items, food |
| [Meat Effigy](https://dontstarve.fandom.com/wiki/Meat_Effigy) | Done | craftable_structures |
| [Meatballs](https://dontstarve.fandom.com/wiki/Meatballs) | Done | crock_pot_recipes, food |
| [Meaty Stew](https://dontstarve.fandom.com/wiki/Meaty_Stew) | Done | craftable_items, crock_pot_recipes |
| [Melonsicle](https://dontstarve.fandom.com/wiki/Melonsicle) | Done | cooling, crock_pot_recipes, food |
| [Merm Flort-ifications](https://dontstarve.fandom.com/wiki/Merm_Flort-ifications) | Done | craftable_structures |
| [Midsummer Cawnival](https://dontstarve.fandom.com/wiki/Midsummer_Cawnival) | Done | events |
| [Mighty Gym](https://dontstarve.fandom.com/wiki/Mighty_Gym) | Done | craftable_structures |
| [Milkmade Hat](https://dontstarve.fandom.com/wiki/Milkmade_Hat) | Done | crock_pot_recipes, equipable_items, food |
| [Milky Whites](https://dontstarve.fandom.com/wiki/Milky_Whites) | Done | boss_dropped_items |
| [Mimicreep](https://dontstarve.fandom.com/wiki/Mimicreep) | Done | cave_creatures |
| [Miner Hat](https://dontstarve.fandom.com/wiki/Miner_Hat) | Done | craftable_items, equipable_items |
| [Mini Sign](https://dontstarve.fandom.com/wiki/Mini_Sign) | Done | craftable_items, craftable_structures, decorations_filter |
| [Moggles](https://dontstarve.fandom.com/wiki/Moggles) | Done | craftable_items, equipable_items |
| [Moleworm](https://dontstarve.fandom.com/wiki/Moleworm) | Done | animals, cave_creatures |
| [Monster Jerky](https://dontstarve.fandom.com/wiki/Monster_Jerky) | Done | craftable_items, food |
| [Monster Lasagna](https://dontstarve.fandom.com/wiki/Monster_Lasagna) | Done | crock_pot_recipes |
| [Monster Meat](https://dontstarve.fandom.com/wiki/Monster_Meat) | Done | boss_dropped_items, food |
| [Monster Tartare](https://dontstarve.fandom.com/wiki/Monster_Tartare) | Done | food |
| [Moon Caller's Staff](https://dontstarve.fandom.com/wiki/Moon_Caller's_Staff) | Done | cooling, equipable_items |
| [Moon Crater Turf](https://dontstarve.fandom.com/wiki/Moon_Crater_Turf) | Done | celestial_tab, craftable_items |
| [Moon Dial](https://dontstarve.fandom.com/wiki/Moon_Dial) | Done | craftable_structures |
| [Moon Glass Saw Blade](https://dontstarve.fandom.com/wiki/Moon_Glass_Saw_Blade) | Done | celestial_filter, craftable_items |
| [Moon Quay Beach Turf](https://dontstarve.fandom.com/wiki/Moon_Quay_Beach_Turf) | Done | craftable_items, decorations_filter |
| [Moon Quay Pirate Banner](https://dontstarve.fandom.com/wiki/Moon_Quay_Pirate_Banner) | Done | craftable_structures, decorations_filter |
| [Moon Rock](https://dontstarve.fandom.com/wiki/Moon_Rock) | Done | boss_dropped_items, craftable_items |
| [Moon Rock Idol](https://dontstarve.fandom.com/wiki/Moon_Rock_Idol) | Done | celestial_tab, craftable_items |
| [Moon Rock Wall](https://dontstarve.fandom.com/wiki/Moon_Rock_Wall) | Done | craftable_items |
| [Moon Shard](https://dontstarve.fandom.com/wiki/Moon_Shard) | Done | boss_dropped_items |
| [Moon Shroom](https://dontstarve.fandom.com/wiki/Moon_Shroom) | Done | food |
| [Moonlens](https://dontstarve.fandom.com/wiki/Moonlens) | Done | craftable_items |
| [Morning Star](https://dontstarve.fandom.com/wiki/Morning_Star) | Done | craftable_items, equipable_items, fight_tab |
| [Morsel](https://dontstarve.fandom.com/wiki/Morsel) | Done | food |
| [Mosaic Flooring](https://dontstarve.fandom.com/wiki/Mosaic_Flooring) | Done | craftable_items |
| [Mosling](https://dontstarve.fandom.com/wiki/Mosling) | New | animals |
| [Mosquito](https://dontstarve.fandom.com/wiki/Mosquito) | New | animals |
| [Mud Turf](https://dontstarve.fandom.com/wiki/Mud_Turf) | Done | craftable_items, decorations_filter |
| [Mumsy](https://dontstarve.fandom.com/wiki/Mumsy) | Done | events |
| [Mush Gnome](https://dontstarve.fandom.com/wiki/Mush_Gnome) | Done | cave_creatures |
| [Mushroom Planter](https://dontstarve.fandom.com/wiki/Mushroom_Planter) | Done | craftable_structures |
| [Mushrooms](https://dontstarve.fandom.com/wiki/Mushrooms) | Done | boss_dropped_items |
| [Mushy Cake](https://dontstarve.fandom.com/wiki/Mushy_Cake) | Done | crock_pot_recipes, food |
| [Mutated Fungal Turf](https://dontstarve.fandom.com/wiki/Mutated_Fungal_Turf) | Done | celestial_tab, craftable_items |
| [Naked Mole Bat](https://dontstarve.fandom.com/wiki/Naked_Mole_Bat) | Done | cave_creatures |
| [Naked Nostrils](https://dontstarve.fandom.com/wiki/Naked_Nostrils) | Done | food |
| [Napsack](https://dontstarve.fandom.com/wiki/Napsack) | Done | craftable_items, equipable_items |
| [Nautopilot](https://dontstarve.fandom.com/wiki/Nautopilot) | Done | craftable_items, craftable_structures |
| [Night Armor](https://dontstarve.fandom.com/wiki/Night_Armor) | Done | armour_filter, boss_dropped_items, craftable_items, equipable_items |
| [Night Light](https://dontstarve.fandom.com/wiki/Night_Light) | Done | craftable_structures |
| [Nightberry](https://dontstarve.fandom.com/wiki/Nightberry) | Done | food |
| [Nightmare Amulet](https://dontstarve.fandom.com/wiki/Nightmare_Amulet) | Done | craftable_items, equipable_items |
| [Nightmare Fuel](https://dontstarve.fandom.com/wiki/Nightmare_Fuel) | Done | boss_dropped_items, craftable_items |
| [Nightmare Saddle](https://dontstarve.fandom.com/wiki/Nightmare_Saddle) | Done | craftable_items |
| [Nitre](https://dontstarve.fandom.com/wiki/Nitre) | Done | craftable_items |
| [No-Eyed Deer](https://dontstarve.fandom.com/wiki/No-Eyed_Deer) | New | animals |
| [Oar](https://dontstarve.fandom.com/wiki/Oar) | Done | craftable_items, equipable_items |
| [Ocean Trawler Kit](https://dontstarve.fandom.com/wiki/Ocean_Trawler_Kit) | Done | craftable_items |
| [Ocuvigil](https://dontstarve.fandom.com/wiki/Ocuvigil) | Done | craftable_structures |
| [Old Beefalo](https://dontstarve.fandom.com/wiki/Old_Beefalo) | Done | events |
| [One-man Band](https://dontstarve.fandom.com/wiki/One-man_Band) | Done | craftable_items, equipable_items |
| [Onion](https://dontstarve.fandom.com/wiki/Onion) | Done | events, food |
| [Orange Gem](https://dontstarve.fandom.com/wiki/Orange_Gem) | Done | boss_dropped_items, craftable_items |
| [Ornate Chest](https://dontstarve.fandom.com/wiki/Ornate_Chest) | Done | boss_dropped_items, containers |
| [Packet of Seeds](https://dontstarve.fandom.com/wiki/Packet_of_Seeds) | Done | events |
| [Pan Flute](https://dontstarve.fandom.com/wiki/Pan_Flute) | Done | craftable_items |
| [Papyrus](https://dontstarve.fandom.com/wiki/Papyrus) | Done | craftable_items |
| [Parrot Pirate](https://dontstarve.fandom.com/wiki/Parrot_Pirate) | New | animals |
| [Pearl's Pearl](https://dontstarve.fandom.com/wiki/Pearl's_Pearl) | Done | boss_dropped_items |
| [Pebble Crab](https://dontstarve.fandom.com/wiki/Pebble_Crab) | Done | events |
| [Pengull](https://dontstarve.fandom.com/wiki/Pengull) | New | animals |
| [Pepper](https://dontstarve.fandom.com/wiki/Pepper) | Done | food |
| [Phasmo-Encapsulator](https://dontstarve.fandom.com/wiki/Phasmo-Encapsulator) | Done | craftable_items |
| [Phlegm](https://dontstarve.fandom.com/wiki/Phlegm) | Done | food |
| [Phobic Experiment](https://dontstarve.fandom.com/wiki/Phobic_Experiment) | Done | craftable_items, events |
| [Pickaxe](https://dontstarve.fandom.com/wiki/Pickaxe) | Done | craftable_items, equipable_items |
| [Pierogi](https://dontstarve.fandom.com/wiki/Pierogi) | Done | crock_pot_recipes, food |
| [Pig](https://dontstarve.fandom.com/wiki/Pig) | New | animals |
| [Pig House](https://dontstarve.fandom.com/wiki/Pig_House) | Done | craftable_structures |
| [Piggyback](https://dontstarve.fandom.com/wiki/Piggyback) | Done | backpacks, clothing_filter, containers, craftable_items, equipable_items |
| [Pile o' Balloons](https://dontstarve.fandom.com/wiki/Pile_o'_Balloons) | Done | craftable_items |
| [Pinchin' Winch](https://dontstarve.fandom.com/wiki/Pinchin'_Winch) | Done | craftable_structures |
| [Pinetree Pioneer Hat](https://dontstarve.fandom.com/wiki/Pinetree_Pioneer_Hat) | Done | craftable_items, equipable_items |
| [Pipton](https://dontstarve.fandom.com/wiki/Pipton) | Done | events |
| [Pit Pig](https://dontstarve.fandom.com/wiki/Pit_Pig) | Done | events |
| [Pitchfork](https://dontstarve.fandom.com/wiki/Pitchfork) | Done | craftable_items, equipable_items |
| [Plain Omelette](https://dontstarve.fandom.com/wiki/Plain_Omelette) | Done | crock_pot_recipes, eggs, food |
| [Pleasant Portrait](https://dontstarve.fandom.com/wiki/Pleasant_Portrait) | Done | craftable_items, decorations_filter |
| [Pocket Scale](https://dontstarve.fandom.com/wiki/Pocket_Scale) | Done | craftable_items, equipable_items |
| [Polar Bearger Bin](https://dontstarve.fandom.com/wiki/Polar_Bearger_Bin) | Done | containers, craftable_items |
| [Polly Roger's Hat](https://dontstarve.fandom.com/wiki/Polly_Roger's_Hat) | Done | craftable_items |
| [Pomegranate](https://dontstarve.fandom.com/wiki/Pomegranate) | Done | food |
| [Portable Crock Pot](https://dontstarve.fandom.com/wiki/Portable_Crock_Pot) | Done | containers, cooking_filter, craftable_items |
| [Portable Grinding Mill](https://dontstarve.fandom.com/wiki/Portable_Grinding_Mill) | Done | cooking_filter, craftable_items, crafting_stations |
| [Portable Seasoning Station](https://dontstarve.fandom.com/wiki/Portable_Seasoning_Station) | Done | cooking_filter, craftable_items |
| [Portal Paraphernalia](https://dontstarve.fandom.com/wiki/Portal_Paraphernalia) | Done | celestial_filter, craftable_items |
| [Portasol](https://dontstarve.fandom.com/wiki/Portasol) | Done | clothing_filter, craftable_items |
| [Potato](https://dontstarve.fandom.com/wiki/Potato) | Done | events, food |
| [Potted Fern](https://dontstarve.fandom.com/wiki/Potted_Fern) | Done | craftable_structures, decorations_filter |
| [Potted Succulent](https://dontstarve.fandom.com/wiki/Potted_Succulent) | Done | craftable_structures, decorations_filter |
| [Potter's Wheel](https://dontstarve.fandom.com/wiki/Potter's_Wheel) | Done | craftable_structures, crafting_stations, decorations_filter |
| [Powder Monkey](https://dontstarve.fandom.com/wiki/Powder_Monkey) | New | animals |
| [Powdercake](https://dontstarve.fandom.com/wiki/Powdercake) | Done | crock_pot_recipes |
| [Prestihatitator](https://dontstarve.fandom.com/wiki/Prestihatitator) | Done | craftable_structures |
| [Pretty Parasol](https://dontstarve.fandom.com/wiki/Pretty_Parasol) | Done | craftable_items, equipable_items |
| [Prize Booth](https://dontstarve.fandom.com/wiki/Midsummer_Cawnival/Prize_Booth) | Done | events |
| [Produce Scale](https://dontstarve.fandom.com/wiki/Produce_Scale) | Done | craftable_structures, decorations_filter |
| [Psychosis Experiment](https://dontstarve.fandom.com/wiki/Psychosis_Experiment) | Done | craftable_items, events |
| [Puffy Vest](https://dontstarve.fandom.com/wiki/Puffy_Vest) | Done | craftable_items, equipable_items |
| [Pumpkin](https://dontstarve.fandom.com/wiki/Pumpkin) | Done | food |
| [Pumpkin Cookies](https://dontstarve.fandom.com/wiki/Pumpkin_Cookies) | Done | crock_pot_recipes, food |
| [Pumpkin Lantern](https://dontstarve.fandom.com/wiki/Pumpkin_Lantern) | Done | craftable_items |
| [Punching Bag](https://dontstarve.fandom.com/wiki/Punching_Bag) | Done | craftable_structures |
| [Pure Brilliance](https://dontstarve.fandom.com/wiki/Pure_Brilliance) | Done | craftable_items |
| [Pure Horror](https://dontstarve.fandom.com/wiki/Pure_Horror) | Done | boss_dropped_items, craftable_items |
| [Purple Gem](https://dontstarve.fandom.com/wiki/Purple_Gem) | Done | boss_dropped_items, craftable_items |
| [Rabbit](https://dontstarve.fandom.com/wiki/Rabbit) | New | animals |
| [Rabbit Earmuffs](https://dontstarve.fandom.com/wiki/Rabbit_Earmuffs) | Done | craftable_items, equipable_items |
| [Rabbit Hutch](https://dontstarve.fandom.com/wiki/Rabbit_Hutch) | Done | craftable_structures |
| [Rain Coat](https://dontstarve.fandom.com/wiki/Rain_Coat) | Done | craftable_items, equipable_items |
| [Rain Hat](https://dontstarve.fandom.com/wiki/Rain_Hat) | Done | craftable_items, equipable_items |
| [Rainometer](https://dontstarve.fandom.com/wiki/Rainometer) | Done | craftable_structures |
| [Ratatouille](https://dontstarve.fandom.com/wiki/Ratatouille) | Done | crock_pot_recipes |
| [Raw Fish](https://dontstarve.fandom.com/wiki/Raw_Fish) | Done | boss_dropped_items, fishes, food |
| [Razor](https://dontstarve.fandom.com/wiki/Razor) | Done | craftable_items |
| [Reanimated Skeleton](https://dontstarve.fandom.com/wiki/Reanimated_Skeleton) | Done | cave_creatures |
| [Record](https://dontstarve.fandom.com/wiki/Record) | Done | craftable_items, decorations_filter |
| [Red Cap](https://dontstarve.fandom.com/wiki/Red_Cap) | Done | boss_dropped_items, food |
| [Red Firecrackers](https://dontstarve.fandom.com/wiki/Red_Firecrackers) | Done | craftable_items |
| [Red Gem](https://dontstarve.fandom.com/wiki/Red_Gem) | Done | boss_dropped_items, craftable_items |
| [Red Lantern](https://dontstarve.fandom.com/wiki/Red_Lantern) | Done | craftable_items, equipable_items |
| [Reinforced Support Pillar](https://dontstarve.fandom.com/wiki/Reinforced_Support_Pillar) | Done | craftable_structures |
| [Relic](https://dontstarve.fandom.com/wiki/Relic) | Done | craftable_structures, decorations_filter |
| [Resting Horror](https://dontstarve.fandom.com/wiki/Resting_Horror) | Done | cave_creatures |
| [Rhinocebro](https://dontstarve.fandom.com/wiki/Rhinocebro) | Done | events |
| [Riled Lucy](https://dontstarve.fandom.com/wiki/Riled_Lucy) | Done | events |
| [Rock Den](https://dontstarve.fandom.com/wiki/Rock_Den) | Done | crafting_stations |
| [Rock Lobster](https://dontstarve.fandom.com/wiki/Rock_Lobster) | Done | animals, cave_creatures |
| [Rocks](https://dontstarve.fandom.com/wiki/Rocks) | Done | craftable_items |
| [Rocky Beach Turf](https://dontstarve.fandom.com/wiki/Rocky_Beach_Turf) | Done | craftable_items, decorations_filter |
| [Rocky Turf](https://dontstarve.fandom.com/wiki/Rocky_Turf) | Done | craftable_items, decorations_filter |
| [Rope](https://dontstarve.fandom.com/wiki/Rope) | Done | craftable_items |
| [Rose-Colored Glasses](https://dontstarve.fandom.com/wiki/Rose-Colored_Glasses) | Done | clothing_filter, craftable_items |
| [Rot](https://dontstarve.fandom.com/wiki/Rot) | Done | craftable_items, fertilizer |
| [Rotten Egg](https://dontstarve.fandom.com/wiki/Rotten_Egg) | Done | eggs, fertilizer |
| [Royal Jelly](https://dontstarve.fandom.com/wiki/Royal_Jelly) | Done | boss_dropped_items |
| [Royal Tapestry](https://dontstarve.fandom.com/wiki/Royal_Tapestry) | Done | craftable_structures |
| [Rudder Kit](https://dontstarve.fandom.com/wiki/Rudder_Kit) | Done | craftable_items |
| [Saddle](https://dontstarve.fandom.com/wiki/Saddle) | Done | craftable_items |
| [Saddlehorn](https://dontstarve.fandom.com/wiki/Saddlehorn) | Done | craftable_items, equipable_items |
| [Safe](https://dontstarve.fandom.com/wiki/Safe) | Done | events |
| [Salmon](https://dontstarve.fandom.com/wiki/Salmon) | Done | events, food |
| [Salsa Fresca](https://dontstarve.fandom.com/wiki/Salsa_Fresca) | Done | crock_pot_recipes, food |
| [Salt Box](https://dontstarve.fandom.com/wiki/Salt_Box) | Done | cooking_filter, craftable_structures |
| [Salt Crystals](https://dontstarve.fandom.com/wiki/Salt_Crystals) | Done | events, food |
| [Salt Lick](https://dontstarve.fandom.com/wiki/Salt_Lick) | Done | craftable_structures |
| [Salt Pond](https://dontstarve.fandom.com/wiki/Salt_Pond) | Done | events |
| [Salt Rack](https://dontstarve.fandom.com/wiki/Salt_Rack) | Done | events |
| [Sammy](https://dontstarve.fandom.com/wiki/Sammy) | Done | events |
| [Sandy Turf](https://dontstarve.fandom.com/wiki/Sandy_Turf) | Done | craftable_items, decorations_filter |
| [Sanguine Experiment](https://dontstarve.fandom.com/wiki/Sanguine_Experiment) | Done | craftable_items, events |
| [Sap](https://dontstarve.fandom.com/wiki/Sap) | Done | events |
| [Savanna Turf](https://dontstarve.fandom.com/wiki/Savanna_Turf) | Done | craftable_items, decorations_filter |
| [Sawhorse](https://dontstarve.fandom.com/wiki/Sawhorse) | Done | craftable_items, craftable_structures |
| [Scaled Chest](https://dontstarve.fandom.com/wiki/Scaled_Chest) | Done | containers, craftable_structures |
| [Scaled Flooring](https://dontstarve.fandom.com/wiki/Scaled_Flooring) | Done | craftable_items, decorations_filter |
| [Scaled Furnace](https://dontstarve.fandom.com/wiki/Scaled_Furnace) | Done | cooking_filter, craftable_structures |
| [Scalemail](https://dontstarve.fandom.com/wiki/Scalemail) | Done | armour_filter, craftable_items, equipable_items, fight_tab |
| [Scales](https://dontstarve.fandom.com/wiki/Scales) | Done | boss_dropped_items |
| [Science Machine](https://dontstarve.fandom.com/wiki/Science_Machine) | Done | craftable_structures, crafting_stations |
| [Scorpeon](https://dontstarve.fandom.com/wiki/Scorpeon) | Done | events |
| [Scrap Wall](https://dontstarve.fandom.com/wiki/Scrap_Wall) | Done | decorations_filter |
| [Scrappy Chapauldron](https://dontstarve.fandom.com/wiki/Scrappy_Chapauldron) | Done | equipable_items |
| [Sea Fishing Rod](https://dontstarve.fandom.com/wiki/Sea_Fishing_Rod) | Done | craftable_items, equipable_items |
| [Seafood Gumbo](https://dontstarve.fandom.com/wiki/Seafood_Gumbo) | Done | crock_pot_recipes, food |
| [Seasoning Salt](https://dontstarve.fandom.com/wiki/Seasoning_Salt) | Done | craftable_items |
| [Seawreath](https://dontstarve.fandom.com/wiki/Seawreath) | Done | craftable_items, equipable_items |
| [Second Chance Watch](https://dontstarve.fandom.com/wiki/Second_Chance_Watch) | Done | craftable_items |
| [Seed Pack-It](https://dontstarve.fandom.com/wiki/Seed_Pack-It) | Done | backpacks, craftable_items, equipable_items |
| [Seeds](https://dontstarve.fandom.com/wiki/Seeds) | Done | food |
| [Seedshell](https://dontstarve.fandom.com/wiki/Seedshell) | Done | equipable_items |
| [Serving](https://dontstarve.fandom.com/wiki/Serving) | Done | events |
| [Sewing Kit](https://dontstarve.fandom.com/wiki/Sewing_Kit) | Done | craftable_items |
| [Shadow Atrium](https://dontstarve.fandom.com/wiki/Shadow_Atrium) | Done | boss_dropped_items |
| [Shadow Manipulator](https://dontstarve.fandom.com/wiki/Shadow_Manipulator) | Done | craftable_structures |
| [Shadow Maul](https://dontstarve.fandom.com/wiki/Shadow_Maul) | Done | craftable_items |
| [Shadow Reaper](https://dontstarve.fandom.com/wiki/Shadow_Reaper) | Done | craftable_items |
| [Shadow Thurible](https://dontstarve.fandom.com/wiki/Shadow_Thurible) | Done | boss_dropped_items |
| [Shadowcraft Plinth](https://dontstarve.fandom.com/wiki/Shadowcraft_Plinth) | Done | craftable_items |
| [Shell Beach Turf](https://dontstarve.fandom.com/wiki/Shell_Beach_Turf) | Done | craftable_items, decorations_filter |
| [Shelmet](https://dontstarve.fandom.com/wiki/Shelmet) | Done | equipable_items |
| [Shield of Terror](https://dontstarve.fandom.com/wiki/Shield_of_Terror) | Done | boss_dropped_items, equipable_items |
| [Shoddy Tool Shed](https://dontstarve.fandom.com/wiki/Shoddy_Tool_Shed) | Done | craftable_structures |
| [Shoo Box](https://dontstarve.fandom.com/wiki/Shoo_Box) | Done | craftable_items |
| [Shovel](https://dontstarve.fandom.com/wiki/Shovel) | Done | craftable_items, equipable_items |
| [Shroom Skin](https://dontstarve.fandom.com/wiki/Shroom_Skin) | Done | boss_dropped_items |
| [Siesta Lean-to](https://dontstarve.fandom.com/wiki/Siesta_Lean-to) | Done | cooling, craftable_structures |
| [Sign](https://dontstarve.fandom.com/wiki/Sign) | Done | craftable_structures, decorations_filter |
| [Silk](https://dontstarve.fandom.com/wiki/Silk) | Done | boss_dropped_items |
| [Sisturn](https://dontstarve.fandom.com/wiki/Sisturn) | Done | craftable_structures |
| [Skeeter Bomb](https://dontstarve.fandom.com/wiki/Skeeter_Bomb) | Done | craftable_items |
| [Sketch](https://dontstarve.fandom.com/wiki/Sketch) | Done | boss_dropped_items, celestial_tab |
| [Slimy Salve](https://dontstarve.fandom.com/wiki/Slimy_Salve) | Done | craftable_items |
| [Slimy Turf](https://dontstarve.fandom.com/wiki/Slimy_Turf) | Done | craftable_items, decorations_filter |
| [Slurper](https://dontstarve.fandom.com/wiki/Slurper) | Done | equipable_items |
| [Slurtle](https://dontstarve.fandom.com/wiki/Slurtle) | Done | animals, cave_creatures |
| [Snortoise](https://dontstarve.fandom.com/wiki/Snortoise) | Done | events |
| [Snurtle Shell Armor](https://dontstarve.fandom.com/wiki/Snurtle_Shell_Armor) | Done | equipable_items |
| [Soothing Tea](https://dontstarve.fandom.com/wiki/Soothing_Tea) | Done | crock_pot_recipes, food |
| [Spark Ark](https://dontstarve.fandom.com/wiki/Spark_Ark) | Done | boss_dropped_items |
| [Spear](https://dontstarve.fandom.com/wiki/Spear) | Done | craftable_items, equipable_items, fight_tab |
| [Spelunker's Bridge Kit](https://dontstarve.fandom.com/wiki/Spelunker's_Bridge_Kit) | Done | craftable_items |
| [Spicy Chili](https://dontstarve.fandom.com/wiki/Spicy_Chili) | Done | crock_pot_recipes, food |
| [Spicy Vegetable Stinger](https://dontstarve.fandom.com/wiki/Spicy_Vegetable_Stinger) | Done | crock_pot_recipes, food |
| [Spider](https://dontstarve.fandom.com/wiki/Spider) | Done | cave_creatures |
| [Spider Eggs](https://dontstarve.fandom.com/wiki/Spider_Eggs) | Done | boss_dropped_items, craftable_items, eggs |
| [Spider Queen](https://dontstarve.fandom.com/wiki/Spider_Queen) | Done | cave_creatures |
| [Spider Warrior](https://dontstarve.fandom.com/wiki/Spider_Warrior) | Done | cave_creatures |
| [Spiderhat](https://dontstarve.fandom.com/wiki/Spiderhat) | Done | boss_dropped_items, equipable_items |
| [Spitter](https://dontstarve.fandom.com/wiki/Spitter) | Done | cave_creatures |
| [Splumonkey](https://dontstarve.fandom.com/wiki/Splumonkey) | New | animals |
| [Spoiled Fish](https://dontstarve.fandom.com/wiki/Spoiled_Fish) | Done | fertilizer |
| [Spotty Shrub](https://dontstarve.fandom.com/wiki/Spotty_Shrub) | Done | events |
| [Spotty Sprig](https://dontstarve.fandom.com/wiki/Spotty_Sprig) | Done | events |
| [Stag Antler](https://dontstarve.fandom.com/wiki/Stag_Antler) | Done | boss_dropped_items |
| [Stagehand](https://dontstarve.fandom.com/wiki/Stagehand) | Done | craftable_structures, decorations_filter |
| [Star Caller's Staff](https://dontstarve.fandom.com/wiki/Star_Caller's_Staff) | Done | craftable_items, equipable_items |
| [Steamed Twigs](https://dontstarve.fandom.com/wiki/Steamed_Twigs) | Done | beefalo_foods, crock_pot_recipes |
| [Steering Wheel](https://dontstarve.fandom.com/wiki/Steering_Wheel) | Done | craftable_items |
| [Stinger](https://dontstarve.fandom.com/wiki/Stinger) | Done | boss_dropped_items |
| [Stone Fruit](https://dontstarve.fandom.com/wiki/Stone_Fruit) | Done | food |
| [Stone Wall](https://dontstarve.fandom.com/wiki/Stone_Wall) | Done | craftable_items |
| [Straw Hat](https://dontstarve.fandom.com/wiki/Straw_Hat) | Done | craftable_items, equipable_items |
| [Strident Trident](https://dontstarve.fandom.com/wiki/Strident_Trident) | Done | craftable_items, equipable_items |
| [Stuffed Eggplant](https://dontstarve.fandom.com/wiki/Stuffed_Eggplant) | Done | crock_pot_recipes, food |
| [Stuffed Fish Heads](https://dontstarve.fandom.com/wiki/Stuffed_Fish_Heads) | Done | crock_pot_recipes, food |
| [Stuffed Night Cap](https://dontstarve.fandom.com/wiki/Stuffed_Night_Cap) | Done | food |
| [Stuffed Pepper Poppers](https://dontstarve.fandom.com/wiki/Stuffed_Pepper_Poppers) | Done | crock_pot_recipes, food |
| [Sugarwood Tree](https://dontstarve.fandom.com/wiki/Sugarwood_Tree) | Done | events |
| [Sulfuric Experiment](https://dontstarve.fandom.com/wiki/Sulfuric_Experiment) | Done | craftable_items, events |
| [Summer Frest](https://dontstarve.fandom.com/wiki/Summer_Frest) | Done | cooling, craftable_items, equipable_items |
| [Surf 'n' Turf](https://dontstarve.fandom.com/wiki/Surf_'n'_Turf) | Done | crock_pot_recipes, food |
| [Swamp Pig](https://dontstarve.fandom.com/wiki/Swamp_Pig) | Done | events |
| [Swamp Pig Elder](https://dontstarve.fandom.com/wiki/Swamp_Pig_Elder) | Done | events |
| [Switcherdoodle](https://dontstarve.fandom.com/wiki/Switcherdoodle) | Done | craftable_items, food |
| [Syrup](https://dontstarve.fandom.com/wiki/Syrup) | Done | events |
| [Syrup of Ipecaca](https://dontstarve.fandom.com/wiki/Syrup_of_Ipecaca) | Done | craftable_items |
| [Table Lamp](https://dontstarve.fandom.com/wiki/Table_Lamp) | Done | craftable_items, decorations_filter |
| [Table Vase](https://dontstarve.fandom.com/wiki/Table_Vase) | Done | craftable_items, decorations_filter |
| [Tackle Box](https://dontstarve.fandom.com/wiki/Tackle_Box) | Done | craftable_items |
| [Tackle Receptacle](https://dontstarve.fandom.com/wiki/Tackle_Receptacle) | Done | craftable_structures |
| [Taffy](https://dontstarve.fandom.com/wiki/Taffy) | Done | crock_pot_recipes, food |
| [Tail o' Three Cats](https://dontstarve.fandom.com/wiki/Tail_o'_Three_Cats) | Done | craftable_items, equipable_items, fight_tab |
| [Tall Scotch Eggs](https://dontstarve.fandom.com/wiki/Tall_Scotch_Eggs) | Done | crock_pot_recipes, food |
| [Tallbird Egg](https://dontstarve.fandom.com/wiki/Tallbird_Egg) | Done | eggs, food |
| [Tam o' Shanter](https://dontstarve.fandom.com/wiki/Tam_o'_Shanter) | Done | equipable_items |
| [Telelocator Focus](https://dontstarve.fandom.com/wiki/Telelocator_Focus) | Done | craftable_structures |
| [Telelocator Staff](https://dontstarve.fandom.com/wiki/Telelocator_Staff) | Done | craftable_items, equipable_items |
| [Teletransport Station](https://dontstarve.fandom.com/wiki/Teletransport_Station) | Done | craftable_items, craftable_structures |
| [Telltale Heart](https://dontstarve.fandom.com/wiki/Telltale_Heart) | Done | craftable_items |
| [Tent](https://dontstarve.fandom.com/wiki/Tent) | Done | craftable_structures |
| [Tent Roll](https://dontstarve.fandom.com/wiki/Tent_Roll) | Done | craftable_items, craftable_structures |
| [Tentacle](https://dontstarve.fandom.com/wiki/Tentacle) | Done | cave_creatures |
| [Tentacle Spike](https://dontstarve.fandom.com/wiki/Tentacle_Spike) | Done | equipable_items |
| [Terra Firma Tamper](https://dontstarve.fandom.com/wiki/Terra_Firma_Tamper) | Done | craftable_structures, decorations_filter |
| [The Altar of Gnaw](https://dontstarve.fandom.com/wiki/The_Altar_of_Gnaw) | Done | events |
| [The Forge](https://dontstarve.fandom.com/wiki/The_Forge) | Done | events |
| [The Gnaw](https://dontstarve.fandom.com/wiki/The_Gnaw) | Done | events |
| [The Gorge](https://dontstarve.fandom.com/wiki/The_Gorge) | Done | events |
| [The Gorge Recipes](https://dontstarve.fandom.com/wiki/The_Gorge_Recipes) | Done | events |
| [The Gorge Seeds](https://dontstarve.fandom.com/wiki/The_Gorge_Seeds) | Done | events |
| [The Lazy Deserter](https://dontstarve.fandom.com/wiki/The_Lazy_Deserter) | Done | craftable_structures |
| [The Lazy Explorer](https://dontstarve.fandom.com/wiki/The_Lazy_Explorer) | Done | craftable_items, equipable_items |
| [The Lazy Forager](https://dontstarve.fandom.com/wiki/The_Lazy_Forager) | Done | craftable_items, equipable_items |
| [Thermal Measurer](https://dontstarve.fandom.com/wiki/Thermal_Measurer) | Done | craftable_structures |
| [Thermal Stone](https://dontstarve.fandom.com/wiki/Thermal_Stone) | Done | cooling, craftable_items |
| [Thick Fur](https://dontstarve.fandom.com/wiki/Thick_Fur) | Done | boss_dropped_items, craftable_items |
| [Think Tank](https://dontstarve.fandom.com/wiki/Think_Tank) | Done | craftable_structures |
| [Thulecite](https://dontstarve.fandom.com/wiki/Thulecite) | Done | craftable_items |
| [Thulecite Bug Net](https://dontstarve.fandom.com/wiki/Thulecite_Bug_Net) | Done | craftable_items |
| [Thulecite Club](https://dontstarve.fandom.com/wiki/Thulecite_Club) | Done | craftable_items, equipable_items |
| [Thulecite Crown](https://dontstarve.fandom.com/wiki/Thulecite_Crown) | Done | craftable_items, equipable_items |
| [Thulecite Medallion](https://dontstarve.fandom.com/wiki/Thulecite_Medallion) | Done | craftable_items |
| [Thulecite Suit](https://dontstarve.fandom.com/wiki/Thulecite_Suit) | Done | craftable_items, equipable_items |
| [Tillweed Salve](https://dontstarve.fandom.com/wiki/Tillweed_Salve) | Done | craftable_items |
| [Tin Fishin' Bin](https://dontstarve.fandom.com/wiki/Tin_Fishin'_Bin) | Done | craftable_structures |
| [Toadstool](https://dontstarve.fandom.com/wiki/Toadstool) | Done | cave_creatures |
| [Toma Root](https://dontstarve.fandom.com/wiki/Toma_Root) | Done | food |
| [Tooth Trap](https://dontstarve.fandom.com/wiki/Tooth_Trap) | Done | craftable_items, fight_tab |
| [Top Hat](https://dontstarve.fandom.com/wiki/Top_Hat) | Done | craftable_items, equipable_items |
| [Torch](https://dontstarve.fandom.com/wiki/Torch) | Done | craftable_items, equipable_items |
| [Trail Mix](https://dontstarve.fandom.com/wiki/Trail_Mix) | Done | crock_pot_recipes, food |
| [Trap](https://dontstarve.fandom.com/wiki/Trap) | Done | craftable_items |
| [Tree Jam](https://dontstarve.fandom.com/wiki/Tree_Jam) | Done | craftable_items, fertilizer |
| [Treeguard](https://dontstarve.fandom.com/wiki/Treeguard) | Done | cave_creatures |
| [Treeguard Idol](https://dontstarve.fandom.com/wiki/Treeguard_Idol) | Done | craftable_items |
| [Trusty Slingshot](https://dontstarve.fandom.com/wiki/Trusty_Slingshot) | Done | craftable_items, equipable_items |
| [Trusty Tape](https://dontstarve.fandom.com/wiki/Trusty_Tape) | Done | craftable_items |
| [Turf-Raiser Helm](https://dontstarve.fandom.com/wiki/Turf-Raiser_Helm) | Done | clothing_filter, craftable_items |
| [Turkey Dinner](https://dontstarve.fandom.com/wiki/Turkey_Dinner) | Done | crock_pot_recipes, food |
| [Turnip](https://dontstarve.fandom.com/wiki/Turnip) | Done | events, food |
| [Twigs](https://dontstarve.fandom.com/wiki/Twigs) | Done | beefalo_foods, craftable_items |
| [Umbralla](https://dontstarve.fandom.com/wiki/Umbralla) | Done | craftable_items |
| [Umbrella](https://dontstarve.fandom.com/wiki/Umbrella) | Done | clothing_filter, craftable_items, equipable_items |
| [Unagi](https://dontstarve.fandom.com/wiki/Unagi) | Done | craftable_items, crock_pot_recipes, food |
| [Veggie Burger](https://dontstarve.fandom.com/wiki/Veggie_Burger) | Done | crock_pot_recipes, food |
| [Void Cowl](https://dontstarve.fandom.com/wiki/Void_Cowl) | Done | craftable_items |
| [Void Robe](https://dontstarve.fandom.com/wiki/Void_Robe) | Done | craftable_items |
| [Volt Goat](https://dontstarve.fandom.com/wiki/Volt_Goat) | New | animals |
| [W.A.R.B.I.S. Armor](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Armor) | Done | armour_filter, craftable_items |
| [W.A.R.B.I.S. Head Gear](https://dontstarve.fandom.com/wiki/W.A.R.B.I.S._Head_Gear) | Done | armour_filter, craftable_items |
| [Waffles](https://dontstarve.fandom.com/wiki/Waffles) | Done | crock_pot_recipes, food |
| [Walking Cane](https://dontstarve.fandom.com/wiki/Walking_Cane) | Done | craftable_items, equipable_items |
| [Wardrobe](https://dontstarve.fandom.com/wiki/Wardrobe) | Done | craftable_structures, decorations_filter |
| [Warren Wreath](https://dontstarve.fandom.com/wiki/Warren_Wreath) | Done | craftable_items, equipable_items |
| [Water Balloon](https://dontstarve.fandom.com/wiki/Water_Balloon) | Done | craftable_items, equipable_items |
| [Watering Can](https://dontstarve.fandom.com/wiki/Watering_Can) | Done | craftable_items, equipable_items |
| [Watermelon](https://dontstarve.fandom.com/wiki/Watermelon) | Done | cooling, food |
| [Wax Paper](https://dontstarve.fandom.com/wiki/Wax_Paper) | Done | craftable_items |
| [Weather Pain](https://dontstarve.fandom.com/wiki/Weather_Pain) | Done | craftable_items, equipable_items, fight_tab |
| [Webby Whistle](https://dontstarve.fandom.com/wiki/Webby_Whistle) | Done | craftable_items |
| [Wet Goop](https://dontstarve.fandom.com/wiki/Wet_Goop) | Done | crock_pot_recipes |
| [Wheat](https://dontstarve.fandom.com/wiki/Wheat) | Done | events |
| [Whirly Fan](https://dontstarve.fandom.com/wiki/Whirly_Fan) | Done | clothing_filter, cooling, craftable_items, equipable_items |
| [Willow's Lighter](https://dontstarve.fandom.com/wiki/Willow's_Lighter) | Done | cooking_filter, craftable_items, equipable_items |
| [Winona's Catapult](https://dontstarve.fandom.com/wiki/Winona's_Catapult) | Done | craftable_items, craftable_structures |
| [Winona's G.E.M.erator](https://dontstarve.fandom.com/wiki/Winona's_G.E.M.erator) | Done | craftable_items, craftable_structures |
| [Winona's Generator](https://dontstarve.fandom.com/wiki/Winona's_Generator) | Done | craftable_items, craftable_structures |
| [Winona's Spotlight](https://dontstarve.fandom.com/wiki/Winona's_Spotlight) | Done | craftable_structures |
| [Winter Hat](https://dontstarve.fandom.com/wiki/Winter_Hat) | Done | craftable_items, equipable_items |
| [Winter's Feast](https://dontstarve.fandom.com/wiki/Winter's_Feast) | Done | events |
| [Wobster](https://dontstarve.fandom.com/wiki/Wobster) | Done | fishes, food |
| [Wobster Bisque](https://dontstarve.fandom.com/wiki/Wobster_Bisque) | Done | cooling, crock_pot_recipes, food |
| [Wobster Dinner](https://dontstarve.fandom.com/wiki/Wobster_Dinner) | Done | craftable_items, crock_pot_recipes, fishes |
| [Wood Fence](https://dontstarve.fandom.com/wiki/Wood_Fence) | Done | craftable_items, craftable_structures, decorations_filter |
| [Wood Gate](https://dontstarve.fandom.com/wiki/Wood_Gate) | Done | craftable_items, decorations_filter |
| [Wood Wall](https://dontstarve.fandom.com/wiki/Wood_Wall) | Done | craftable_items, craftable_structures, decorations_filter |
| [Wooden Flooring](https://dontstarve.fandom.com/wiki/Wooden_Flooring) | Done | craftable_items, decorations_filter |
| [Wooden Walking Stick](https://dontstarve.fandom.com/wiki/Wooden_Walking_Stick) | Done | clothing_filter, craftable_items |
| [Year of the Beefalo](https://dontstarve.fandom.com/wiki/Year_of_the_Beefalo) | Done | events |
| [Year of the Bunnyman](https://dontstarve.fandom.com/wiki/Year_of_the_Bunnyman) | Done | events |
| [Year of the Carrat](https://dontstarve.fandom.com/wiki/Year_of_the_Carrat) | Done | events |
| [Year of the Catcoon](https://dontstarve.fandom.com/wiki/Year_of_the_Catcoon) | Done | events |
| [Year of the Dragonfly](https://dontstarve.fandom.com/wiki/Year_of_the_Dragonfly) | Done | events |
| [Year of the Gobbler](https://dontstarve.fandom.com/wiki/Year_of_the_Gobbler) | Done | events |
| [Year of the Pig King](https://dontstarve.fandom.com/wiki/Year_of_the_Pig_King) | Done | events |
| [Year of the Varg](https://dontstarve.fandom.com/wiki/Year_of_the_Varg) | Done | events |
| [Yellow Gem](https://dontstarve.fandom.com/wiki/Yellow_Gem) | Done | boss_dropped_items, craftable_items |

Khi thêm Category khác, crawler tự thêm URL/category/status vào live registry.
Sau mỗi batch đã review, export JSON snapshot rồi cập nhật bảng MD này để handoff.
