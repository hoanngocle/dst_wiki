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
                "wikitext": '{{Mob Infobox|spawnCode = "alterguardian_phase3"}}',
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


if __name__ == "__main__":
    unittest.main()
