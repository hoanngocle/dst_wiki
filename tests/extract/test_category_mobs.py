import json
import unittest

from tools.crawl_wiki.category_config import CategoryConfig
from tools.extract.category_mobs import extract_mob_page


def animals_config():
    return CategoryConfig(
        key="animals",
        source_url="https://dontstarve.fandom.com/wiki/Category:Animals",
        category_title="Category:Animals",
        expected_direct_pages=1,
        expected_published_pages=1,
        allowed_namespaces=(0,),
        excluded_titles=(),
        game="DST",
        item_type="mob",
        tags=("Animals",),
    )


def page(page_id, title, wikitext):
    return {
        "schema_version": 1,
        "page_id": page_id,
        "namespace": 0,
        "title": title,
        "display_title": title,
        "canonical_url": "https://dontstarve.fandom.com/wiki/{}".format(
            title.replace(" ", "_")
        ),
        "revision": {
            "id": 1000 + page_id,
            "timestamp": "2026-07-21T00:00:00Z",
            "sha1": "sha1-{}".format(page_id),
        },
        "wikitext": wikitext,
        "html": "<p>{}</p>".format(title),
        "plain_text": title,
        "images": ["File:{}.png".format(title)],
    }


def fact(mob, section, key):
    return next(value for value in mob[section]["values"] if value["key"] == key)


class CategoryMobTests(unittest.TestCase):
    def test_normalizes_only_dst_values_from_multi_game_infobox(self):
        beefalo = page(
            101,
            "Beefalo",
            """
{{Mob Infobox
|spawnCode = beefalo
|health = {{DS|500}}{{DST|1000}}
|damage = {{DS|34}}{{DST|34}}
|attackPeriod = 4
|attackRange = 3
|walkSpeed = 1.5
|runSpeed = {{DST|7}}
|specialAbility = Becomes hostile periodically; Can be tamed
|loot = {{DST|Beefalo Wool x4; Meat x3}}
|shipwreckedLoot = {{Shipwrecked|Tar}}
}}
""",
        )

        mob = extract_mob_page(beefalo, animals_config(), mappings={})

        self.assertEqual(mob["identity"]["primaryCode"], "beefalo")
        self.assertEqual(
            mob["classification"],
            {"type": "mob", "tags": ["Animals"], "game": "DST"},
        )
        self.assertEqual(fact(mob, "stats", "max_health")["value"], 1000)
        self.assertEqual(fact(mob, "combat", "attack_damage")["value"], 34)
        self.assertEqual(fact(mob, "movement", "run_speed")["value"], 7)
        self.assertNotIn("Shipwrecked", json.dumps(mob))

    def test_keeps_dst_loot_and_bunnyman_transformation_trait(self):
        bunnyman = page(
            208,
            "Bunnyman",
            """
{{Mob Infobox
|spawnCode = bunnyman
|health = {{DST|200}}
|sanityAura = {{DST|25/min}}
|damage = {{DST|40}}
|attackPeriod = 2
|attackRange = 3
|walkSpeed = 3
|runSpeed = 6
|specialAbility = Turns into a Beardlord when the player's Sanity is below 40%.
|loot = {{DST|Carrot x2; Beard Hair 75%; Bunny Puff 25%}}
}}
""",
        )

        mob = extract_mob_page(bunnyman, animals_config(), mappings={})

        self.assertEqual(fact(mob, "effects", "sanity_aura")["value"], "25/min")
        self.assertEqual(mob["traits"]["status"], "known")
        self.assertTrue(
            any("Beardlord" in value["text"] for value in mob["traits"]["values"])
        )
        self.assertTrue(all(drop["game"] == "DST" for drop in mob["loot"]["values"]))

    def test_groups_verified_prefab_variants_on_one_page(self):
        koalefant = page(
            303,
            "Koalefant",
            "{{Mob Infobox|health={{DST|1000}}|damage={{DST|50}}}}",
        )
        mappings = {
            303: {
                "primaryCode": "koalefant_summer",
                "prefabCodes": ["koalefant_summer", "koalefant_winter"],
                "variants": [
                    {"code": "koalefant_summer", "label": "Summer Koalefant"},
                    {"code": "koalefant_winter", "label": "Winter Koalefant"},
                ],
            }
        }

        mob = extract_mob_page(koalefant, animals_config(), mappings)

        self.assertEqual(
            mob["identity"]["prefabCodes"],
            ["koalefant_summer", "koalefant_winter"],
        )
        self.assertEqual(
            [value["code"] for value in mob["variants"]],
            ["koalefant_summer", "koalefant_winter"],
        )

    def test_marks_ambiguous_unlabelled_multi_game_value_unknown(self):
        ambiguous = page(
            404,
            "Ambiguous Animal",
            """
{{Mob Infobox
|spawnCode = ambiguous_animal
|damage = 20 / 40 (Don't Starve / Don't Starve Together)
}}
""",
        )

        mob = extract_mob_page(ambiguous, animals_config(), mappings={})

        self.assertEqual(mob["combat"]["status"], "unknown")
        self.assertEqual(mob["combat"]["reason"], "ambiguous_game_version")


if __name__ == "__main__":
    unittest.main()
