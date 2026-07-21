import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.mob_wiki import load_mob_wiki_details


class MobWikiTests(unittest.TestCase):
    def test_matches_spawn_code_before_display_name_and_normalizes_summary(self):
        pages = [
            {
                "schema_version": 1,
                "namespace": 0,
                "page_id": 10,
                "title": "Wrong Display Name",
                "canonical_url": "https://dontstarve.wiki.gg/wiki/Celestial_Champion",
                "categories": ["Category:Boss_Monsters"],
                "plain_text": "The Celestial Champion is a Boss Monster.\nMore detail.",
                "wikitext": (
                    '{{Mob Infobox|image = Celestial Champion.png|'
                    'spawnCode = "alterguardian_phase3"}}'
                ),
                "images": ["File:Celestial Champion.png"],
            },
            {
                "schema_version": 1,
                "namespace": 0,
                "page_id": 11,
                "title": "Celestial Champion",
                "canonical_url": "https://dontstarve.wiki.gg/wiki/Ambiguous",
                "categories": [],
                "plain_text": "Wrong page.",
                "wikitext": "",
                "images": [],
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pages.jsonl"
            path.write_text(
                "".join(json.dumps(page) + "\n" for page in pages),
                encoding="utf-8",
            )

            details = load_mob_wiki_details(
                path,
                [
                    {
                        "id": "base_game:alterguardian_phase3",
                        "prefabId": "alterguardian_phase3",
                        "name": "Chiến Binh Thiên Hà",
                        "englishName": "Celestial Champion",
                    }
                ],
            )

        self.assertEqual(
            details["base_game:alterguardian_phase3"]["canonicalUrl"],
            "https://dontstarve.wiki.gg/wiki/Celestial_Champion",
        )
        self.assertEqual(
            details["base_game:alterguardian_phase3"]["summary"],
            "The Celestial Champion is a Boss Monster.",
        )
        self.assertEqual(
            details["base_game:alterguardian_phase3"]["imageTitles"],
            ["Celestial Champion.png"],
        )
        self.assertEqual(
            details["base_game:alterguardian_phase3"]["primaryImageTitle"],
            "Celestial Champion.png",
        )
        self.assertEqual(
            details["base_game:alterguardian_phase3"]["variantImageTitles"],
            {"alterguardian_phase3": "Celestial Champion.png"},
        )

    def test_leaves_ambiguous_title_unmatched(self):
        pages = [
            {
                "schema_version": 1,
                "namespace": 0,
                "page_id": page_id,
                "title": "Spider",
                "canonical_url": f"https://example.test/{page_id}",
                "categories": [],
                "plain_text": "Spider.",
                "wikitext": "",
                "images": [],
            }
            for page_id in (1, 2)
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pages.jsonl"
            path.write_text(
                "".join(json.dumps(page) + "\n" for page in pages),
                encoding="utf-8",
            )
            details = load_mob_wiki_details(
                path,
                [
                    {
                        "id": "base_game:spider",
                        "prefabId": "spider",
                        "name": "Nhện",
                        "englishName": "Spider",
                    }
                ],
            )

        self.assertEqual(details, {})

    def test_maps_multi_phase_page_to_the_canonical_group_member(self):
        page = {
            "schema_version": 1,
            "namespace": 0,
            "page_id": 30811,
            "title": "Celestial Champion",
            "canonical_url": "https://dontstarve.wiki.gg/wiki/Celestial_Champion",
            "categories": ["Category:Boss_Monsters"],
            "plain_text": (
                "The Celestial Champion is a Boss Monster. "
                "It is spawned after assembling the Lunar Siphonator. "
                "It summons Enlightening Snares during phase three."
            ),
            "wikitext": (
                '{{Object Infobox|image = Phase 1.png|spawnCode = "alterguardian_phase1"}}\n'
                '{{Object Infobox|image = Phase 2.png|spawnCode = "alterguardian_phase2"}}\n'
                '{{Object Infobox|image = Phase 3.png|spawnCode = "alterguardian_phase3"}}\n'
                '{{Object Infobox|image = Defeated.png|spawnCode = "alterguardian_phase3dead"}}'
            ),
            "images": ["File:Celestial_Champion_Phase_3.png"],
        }
        items = [
            {
                "id": f"base_game:alterguardian_phase{suffix}",
                "prefabId": f"alterguardian_phase{suffix}",
                "name": "Chiến Binh Thiên Hà",
                "englishName": (
                    "Defeated Celestial Champion"
                    if suffix == "3dead"
                    else "Celestial Champion"
                ),
            }
            for suffix in ("1", "2", "3", "3dead")
        ]
        group = {
            "canonicalId": "base_game:alterguardian_phase3",
            "members": [
                {"id": item["id"], "role": "phase", "order": index}
                for index, item in enumerate(items, 1)
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pages.jsonl"
            path.write_text(json.dumps(page) + "\n", encoding="utf-8")

            details = load_mob_wiki_details(path, items, [group])

        self.assertEqual(
            details["base_game:alterguardian_phase3"]["pageId"],
            30811,
        )
        self.assertEqual(
            details["base_game:alterguardian_phase3"]["variantImageTitles"][
                "alterguardian_phase3dead"
            ],
            "Defeated.png",
        )
        self.assertEqual(
            details["base_game:alterguardian_phase3"]["mechanics"],
            ["It summons Enlightening Snares during phase three."],
        )


if __name__ == "__main__":
    unittest.main()
