import unittest

from tools.extract.wiki_mapping import build_entity_index, map_page


class WikiMappingTests(unittest.TestCase):
    def setUp(self):
        self.index = build_entity_index(
            [
                {
                    "namespace": "base_game",
                    "prefab_id": "goldnugget",
                    "name_en": "Gold Nugget",
                },
                {
                    "namespace": "base_game",
                    "prefab_id": "fish_raw_small",
                    "name_en": "Fish Morsel",
                },
                {
                    "namespace": "base_game",
                    "prefab_id": "fish_raw_small_cooked",
                    "name_en": "Cooked Fish Morsel",
                },
            ]
        )

    def test_exact_spawn_code_has_highest_precedence(self):
        page = {
            "page_id": 1,
            "title": "Gold",
            "wikitext": '|spawnCode = "goldnugget"',
        }

        decision = map_page(page, self.index)

        self.assertEqual(decision.entity_key, "base_game:goldnugget")
        self.assertEqual(decision.method, "spawn_code")
        self.assertEqual(decision.confidence, 1.0)

    def test_unique_normalized_english_name_maps(self):
        decision = map_page(
            {"page_id": 2, "title": "Fish_Morsel", "wikitext": ""},
            self.index,
        )

        self.assertEqual(decision.entity_key, "base_game:fish_raw_small")
        self.assertEqual(decision.method, "english_name")

    def test_dst_suffix_is_a_canonical_alias(self):
        decision = map_page(
            {"page_id": 3, "title": "Fish Morsel/DST", "wikitext": ""},
            self.index,
        )

        self.assertEqual(decision.entity_key, "base_game:fish_raw_small")
        self.assertEqual(decision.method, "canonical_alias")

    def test_title_disambiguates_multiple_infobox_spawn_codes(self):
        decision = map_page(
            {
                "page_id": 4,
                "title": "Fish Morsel",
                "wikitext": (
                    '|spawnCode = "fish_raw_small"\n'
                    '|spawnCode = "fish_raw_small_cooked"\n'
                ),
            },
            self.index,
        )

        self.assertEqual(decision.entity_key, "base_game:fish_raw_small")
        self.assertEqual(decision.method, "spawn_code_title")

    def test_ambiguous_name_is_not_selected(self):
        index = build_entity_index(
            [
                {
                    "namespace": "base_game",
                    "prefab_id": "one",
                    "name_en": "Shared",
                },
                {
                    "namespace": "base_game",
                    "prefab_id": "two",
                    "name_en": "Shared",
                },
            ]
        )

        decision = map_page(
            {"page_id": 5, "title": "Shared", "wikitext": ""},
            index,
        )

        self.assertIsNone(decision.entity_key)
        self.assertEqual(decision.method, "ambiguous_name")
        self.assertEqual(
            decision.evidence["candidates"],
            ["base_game:one", "base_game:two"],
        )

    def test_unmatched_page_is_explicit(self):
        decision = map_page(
            {"page_id": 6, "title": "Unknown Thing", "wikitext": ""},
            self.index,
        )

        self.assertIsNone(decision.entity_key)
        self.assertEqual(decision.method, "unmatched")
        self.assertEqual(decision.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
