import json
import tempfile
import unittest
from pathlib import Path

from tools.crawl_wiki.category_config import (
    CategoryConfigError,
    load_category_config,
)


class CategoryConfigTests(unittest.TestCase):
    def test_loads_animals_category_with_reviewed_scope(self):
        config = load_category_config("animals")

        self.assertEqual(config.category_title, "Category:Animals")
        self.assertEqual(config.expected_direct_pages, 34)
        self.assertEqual(config.expected_published_pages, 28)
        self.assertEqual(config.allowed_namespaces, (0,))
        self.assertEqual(
            dict(config.excluded_titles),
            {
                "Blue Whale": "non_dst:shipwrecked",
                "White Whale": "non_dst:shipwrecked",
                "Wildbore": "non_dst:shipwrecked",
                "Peagawk": "non_dst:hamlet",
                "Pog": "non_dst:hamlet",
                "Glowfly": "non_dst:hamlet",
            },
        )
        self.assertEqual(config.game, "DST")
        self.assertEqual(config.item_type, "mob")
        self.assertEqual(config.tags, ("Animals",))
        self.assertEqual(
            config.output_path,
            Path("data/crawled/fandom-categories/animals"),
        )

    def test_rejects_exclusion_count_that_does_not_match_publication_count(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            payload = {
                "schema_version": 1,
                "key": "animals",
                "sourceUrl": "https://dontstarve.fandom.com/wiki/Category:Animals",
                "categoryTitle": "Category:Animals",
                "expectedDirectPages": 3,
                "expectedPublishedPages": 2,
                "allowedNamespaces": [0],
                "excludedTitles": {},
                "game": "DST",
                "itemType": "mob",
                "tags": ["Animals"],
            }
            (root / "animals.json").write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(CategoryConfigError, "difference"):
                load_category_config("animals", root)


if __name__ == "__main__":
    unittest.main()
