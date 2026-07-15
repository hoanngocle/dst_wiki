import unittest

from tools.crawl_wiki.item_seeds import (
    ItemSeed,
    extract_item_seeds,
    merge_item_seeds,
)


class ItemSeedTests(unittest.TestCase):
    def test_extracts_only_visual_links_inside_approved_section(self):
        html = """
        <a href="/wiki/Outside" title="Outside">
          <img alt="Outside.png" src="/images/Outside.png">
        </a>
        <article id="Resources-0">
          <a href="/wiki/Cut_Grass" title="Cut Grass">
            <img alt="Cut Grass.png" src="/images/thumb/Cut_Grass.png/40px-Cut_Grass.png">
          </a>
          <a href="/wiki/Tools_Filter" title="Tools Filter">
            <img alt="Tools Filter.png" src="/images/Tools_Filter.png">
          </a>
          <a href="/wiki/Text_Only" title="Text Only">Text only</a>
          <a href="/wiki/File:Not_An_Item.png" title="File:Not An Item.png">
            <img alt="Not An Item.png" src="/images/Not_An_Item.png">
          </a>
        </article>
        """

        seeds = extract_item_seeds(
            "Items", html, "https://dontstarve.wiki.gg/"
        )

        self.assertEqual([seed.title for seed in seeds], ["Cut Grass"])
        self.assertEqual(seeds[0].href, "/wiki/Cut_Grass")
        self.assertEqual(seeds[0].icon_title, "File:Cut Grass.png")
        self.assertEqual(
            seeds[0].icon_thumbnail_url,
            "https://dontstarve.wiki.gg/images/thumb/Cut_Grass.png/40px-Cut_Grass.png",
        )
        self.assertEqual(
            seeds[0].source_sections, ("Items#Resources-0",)
        )

    def test_merges_duplicate_links_and_preserves_sections(self):
        merged = merge_item_seeds(
            [
                [
                    ItemSeed(
                        "Berry",
                        "/wiki/Berry",
                        "File:Berry.png",
                        "/thumb-a",
                        ("Items#Food-0",),
                    )
                ],
                [
                    ItemSeed(
                        "Berry",
                        "/wiki/Berry",
                        "File:Berry.png",
                        "/thumb-b",
                        ("Items#By_Crock_Pot_Value-0",),
                    )
                ],
            ]
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(
            merged[0].source_sections,
            (
                "Items#By_Crock_Pot_Value-0",
                "Items#Food-0",
            ),
        )
        self.assertEqual(merged[0].icon_thumbnail_url, "/thumb-a")

    def test_uses_only_approved_sections_for_each_source_page(self):
        html = """
        <article id="Resources-0">
          <a href="/wiki/Log" title="Log"><img alt="Log.png"></a>
        </article>
        <article id="DST-0">
          <a href="/wiki/Grass/DST" title="Grass/DST"><img alt="Grass.png"></a>
        </article>
        """

        item_titles = [
            seed.title
            for seed in extract_item_seeds(
                "Items", html, "https://dontstarve.wiki.gg/"
            )
        ]
        plant_titles = [
            seed.title
            for seed in extract_item_seeds(
                "Plants", html, "https://dontstarve.wiki.gg/"
            )
        ]

        self.assertEqual(item_titles, ["Log"])
        self.assertEqual(plant_titles, ["Grass/DST"])


if __name__ == "__main__":
    unittest.main()
