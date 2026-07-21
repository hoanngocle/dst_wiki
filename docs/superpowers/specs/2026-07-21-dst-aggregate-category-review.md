# DST Aggregate Category Review

## Source

- URL: `https://dontstarve.fandom.com/wiki/Category:Don%27t_Starve_Together`
- Category title: `Category:Don't Starve Together`
- Discovery completed after two MediaWiki `categorymembers` pages.

## Count reconciliation

The source exposes exactly 899 members:

- 878 namespace-0 articles.
- 12 child categories, ignored because crawling is non-recursive.
- Nine User/User blog pages, ignored because only namespace 0 is allowed.
- The 878 direct titles resolve to 872 canonical URLs because seven Moonlens titles collapse to one canonical page.

Before this batch, the 872 canonical publications contain 523 URLs already `Done`, zero `Doing`/`New`, and 349 URLs absent from the shared registry. Existing `Done` pages must be reused; only the 349 missing URLs may perform detail network fetches.

## Canonical duplicate exclusions

Keep `Moonlens` and exclude these six redirect aliases with `duplicate:canonical_redirect`:

- Blue Moonlens
- Green Moonlens
- Orange Moonlens
- Purple Moonlens
- Red Moonlens
- Yellow Moonlens

## Ignored child categories

- Category:A New Reign
- Category:Aquatic Mobs
- Category:Cartography Tab
- Category:Celestial Tab
- Category:Curios
- Category:Engineering Tab
- Category:Events
- Category:Portable Crock Pot Recipes
- Category:Rare Blueprint Exclusive
- Category:Return of Them
- Category:Seafaring Tab
- Category:Shadow Tab

## Ignored non-content namespaces

- User:Aviivix
- User:Mahskie/Sandbox
- User blog:Mewk, spot, and socks/PVP
- User:Queron/Caves
- User:Robyn Grayson/Willow
- User:Robyn Grayson/Willow's Lighter
- User blog:Sybastion/Farming in alphabetical order
- User:Synthetic ivy/sandbox
- User blog:WX-100/Don't Starve Together's farm

## Publication contract

- Config key: `dont_starve_together`
- Game: `DST`
- Item type: `content`
- Tag: `Don't Starve Together`
- Expected direct namespace-0 titles: 878
- Expected published canonical pages: 872
- Recursive category traversal: disabled
- Notes: preserve raw HTML and wikitext through the standard crawler artifacts.
