# Category crawler control

Registry máy đọc/ghi là `data/crawled/fandom-url-registry.json`; file MD này là
bảng review nhanh. Trạng thái chỉ gồm `New`, `Doing`, `Done`: URL mới/`New` được
lấy tiếp, còn `Doing` và `Done` phải skip network fetch.

## Category queue

| Category | Source | Direct | Excluded | Published | Status |
|---|---|---:|---:|---:|---|
| animals | [Category:Animals](https://dontstarve.fandom.com/wiki/Category:Animals) | 35 | 6 | 29 | Done |

Animals còn loại bốn category con theo namespace. Sáu trang ngoài DST là Blue
Whale, White Whale, Wildbore, Peagawk, Pog và Glowfly; chúng không được thêm vào
registry detail URL.

## Shared item URLs

| Item URL | Status | Categories |
|---|---|---|
| [Bee](https://dontstarve.fandom.com/wiki/Bee) | Done | animals |
| [Beefalo](https://dontstarve.fandom.com/wiki/Beefalo) | Done | animals |
| [Bright-Eyed Frog](https://dontstarve.fandom.com/wiki/Bright-Eyed_Frog) | Done | animals |
| [Bulbous Lightbug](https://dontstarve.fandom.com/wiki/Bulbous_Lightbug) | Done | animals |
| [Bunnyman](https://dontstarve.fandom.com/wiki/Bunnyman) | Done | animals |
| [Butterfly](https://dontstarve.fandom.com/wiki/Butterfly) | Done | animals |
| [Buzzard](https://dontstarve.fandom.com/wiki/Buzzard) | Done | animals |
| [Catcoon](https://dontstarve.fandom.com/wiki/Catcoon) | Done | animals |
| [Dust Moth](https://dontstarve.fandom.com/wiki/Dust_Moth) | Done | animals |
| [Ewecus](https://dontstarve.fandom.com/wiki/Ewecus) | Done | animals |
| [Frog](https://dontstarve.fandom.com/wiki/Frog) | Done | animals |
| [Gem Deer](https://dontstarve.fandom.com/wiki/Gem_Deer) | Done | animals |
| [Glommer](https://dontstarve.fandom.com/wiki/Glommer) | Done | animals |
| [Gobbler](https://dontstarve.fandom.com/wiki/Gobbler) | Done | animals |
| [Grass Gator](https://dontstarve.fandom.com/wiki/Grass_Gator) | Done | animals |
| [Koalefant](https://dontstarve.fandom.com/wiki/Koalefant) | Done | animals |
| [Moleworm](https://dontstarve.fandom.com/wiki/Moleworm) | Done | animals |
| [Mosling](https://dontstarve.fandom.com/wiki/Mosling) | Done | animals |
| [Mosquito](https://dontstarve.fandom.com/wiki/Mosquito) | Done | animals |
| [No-Eyed Deer](https://dontstarve.fandom.com/wiki/No-Eyed_Deer) | Done | animals |
| [Parrot Pirate](https://dontstarve.fandom.com/wiki/Parrot_Pirate) | Done | animals |
| [Pengull](https://dontstarve.fandom.com/wiki/Pengull) | Done | animals |
| [Pig](https://dontstarve.fandom.com/wiki/Pig) | Done | animals |
| [Powder Monkey](https://dontstarve.fandom.com/wiki/Powder_Monkey) | Done | animals |
| [Rabbit](https://dontstarve.fandom.com/wiki/Rabbit) | Done | animals |
| [Rock Lobster](https://dontstarve.fandom.com/wiki/Rock_Lobster) | Done | animals |
| [Slurtle](https://dontstarve.fandom.com/wiki/Slurtle) | Done | animals |
| [Splumonkey](https://dontstarve.fandom.com/wiki/Splumonkey) | Done | animals |
| [Volt Goat](https://dontstarve.fandom.com/wiki/Volt_Goat) | Done | animals |

Khi thêm Category khác, crawler tự thêm URL/category/status vào JSON registry.
Sau mỗi batch đã review, cập nhật bảng MD này từ registry để dùng làm handoff.
