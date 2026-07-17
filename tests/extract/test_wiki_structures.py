import unittest

from tools.extract.wiki_structures import normalize_structure_page


def wiki_page(title: str, wikitext: str) -> dict:
    return {
        "page_id": 10,
        "title": title,
        "canonical_url": (
            "https://dontstarve.wiki.gg/wiki/" + title.replace(" ", "_")
        ),
        "categories": [
            "Category:Structures",
            "Category:Don't Starve Together",
        ],
        "wikitext": wikitext,
        "revision": {
            "id": 20,
            "sha1": "abc",
            "timestamp": "2026-07-17T00:00:00Z",
        },
    }


class WikiStructureTests(unittest.TestCase):
    def test_normalizes_natural_indestructible_structure(self):
        result = normalize_structure_page(
            wiki_page(
                "Ancient Statue/DST",
                "{{Object Infobox\n"
                "|image=Ancient Statue DST.png\n"
                "|renewable=Yes\n"
                "|tool=Can't Be Destroyed\n"
                "|spawnCode=atrium_statue\n"
                "}}\n"
                "Found naturally in the [[Atrium]] Biome and respawned after "
                "the Ancient Fuelweaver is killed.",
            )
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertIs(result["origin"]["naturallySpawned"], True)
        self.assertIs(result["origin"]["renewable"], True)
        self.assertIs(result["destruction"]["destroyable"], False)
        self.assertEqual(
            result["visual_candidates"][0]["title"],
            "File:Ancient Statue DST.png",
        )

    def test_normalizes_fueled_functional_structure(self):
        result = normalize_structure_page(
            wiki_page(
                "Fire Pit/DST",
                "{{Object Infobox\n"
                "|image=Fire Pit.png\n"
                "|fuel=Fire Fuel\n"
                "|renewable=Yes\n"
                "|spawnCode=firepit\n"
                "}}\n"
                "The Fire Pit provides light and warmth and can be refueled.",
            )
        )

        self.assertIsNotNone(result)
        assert result is not None
        keys = {fact["key"] for fact in result["functions"]["facts"]}
        self.assertTrue({"fuel", "light", "warmth"}.issubset(keys))

    def test_normalizes_spawner_and_storage_facts_without_duplicates(self):
        result = normalize_structure_page(
            wiki_page(
                "Pig House/DST",
                "{{Object Infobox|image=Pig House.png|spawns=[[Pig]]|storage=4}}\n"
                "A Pig House spawns a Pig and has 4 storage slots.",
            )
        )

        self.assertIsNotNone(result)
        assert result is not None
        facts = result["functions"]["facts"]
        self.assertEqual([fact["key"] for fact in facts], ["spawns", "storage"])
        self.assertEqual(facts[0]["value"], "Pig")
        self.assertEqual(facts[1]["value"], "4")

    def test_returns_none_for_non_structure_page(self):
        value = wiki_page("Gold Nugget", "{{Object Infobox|stack=40}}")
        value["categories"] = ["Category:Items"]

        self.assertIsNone(normalize_structure_page(value))


if __name__ == "__main__":
    unittest.main()
