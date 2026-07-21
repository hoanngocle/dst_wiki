import unittest

from tools.crawl_wiki.category_config import CategoryConfig
from tools.crawl_wiki.category_seeds import normalize_category_members


def category_config(
    expected_direct_pages=2,
    expected_published_pages=2,
    excluded_titles=None,
):
    return CategoryConfig(
        key="animals",
        source_url="https://dontstarve.fandom.com/wiki/Category:Animals",
        category_title="Category:Animals",
        expected_direct_pages=expected_direct_pages,
        expected_published_pages=expected_published_pages,
        allowed_namespaces=(0,),
        excluded_titles=tuple(sorted((excluded_titles or {}).items())),
        game="DST",
        item_type="mob",
        tags=("Animals",),
    )


class CategorySeedTests(unittest.TestCase):
    def test_accepts_pages_and_audits_subcategories_without_recursing(self):
        seeds = normalize_category_members(
            category_config(),
            [
                {"pageid": 1, "ns": 0, "title": "Beefalo"},
                {"pageid": 2, "ns": 14, "title": "Category:Birds"},
                {"pageid": 3, "ns": 0, "title": "Bunnyman"},
            ],
        )

        self.assertEqual(
            [seed.title for seed in seeds if seed.accepted],
            ["Beefalo", "Bunnyman"],
        )
        self.assertEqual(
            [(seed.title, seed.reason) for seed in seeds if not seed.accepted],
            [("Category:Birds", "excluded_namespace:14")],
        )

    def test_excludes_reviewed_non_dst_pages_before_detail_queueing(self):
        seeds = normalize_category_members(
            category_config(
                expected_direct_pages=3,
                expected_published_pages=1,
                excluded_titles={
                    "Blue Whale": "non_dst:shipwrecked",
                    "Peagawk": "non_dst:hamlet",
                },
            ),
            [
                {"pageid": 1, "ns": 0, "title": "Beefalo"},
                {"pageid": 2, "ns": 0, "title": "Blue Whale"},
                {"pageid": 3, "ns": 0, "title": "Peagawk"},
            ],
        )

        self.assertEqual(
            [seed.title for seed in seeds if seed.accepted],
            ["Beefalo"],
        )
        self.assertEqual(
            [(seed.title, seed.reason) for seed in seeds if not seed.accepted],
            [
                ("Blue Whale", "non_dst:shipwrecked"),
                ("Peagawk", "non_dst:hamlet"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
