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

    def test_rejects_template_fragment_as_prefab_code_until_explicitly_mapped(self):
        pengull = page(
            19330,
            "Pengull",
            """
{{Mob Infobox
|spawnCode = {{HoverOver|text="penguin"|hover=Can only be spawned during Winter}}
|health = {{DST|150}}
}}
""",
        )

        with self.assertRaisesRegex(ValueError, "no verified prefab code"):
            extract_mob_page(pengull, animals_config(), mappings={})

        mob = extract_mob_page(
            pengull,
            animals_config(),
            mappings={
                19330: {
                    "primaryCode": "penguin",
                    "prefabCodes": ["penguin"],
                    "variants": [],
                }
            },
        )
        self.assertEqual(mob["identity"]["primaryCode"], "penguin")

    def test_summary_drops_non_dst_sentences(self):
        frog = page(
            2554,
            "Frog",
            "{{Mob Infobox|spawnCode=frog|health={{DST|100}}}}",
        )
        frog["plain_text"] = (
            "Frogs knock an item from the player's inventory when attacking. "
            "In Shipwrecked, Poison Frogs use a different attack. "
            "Frog Rain can overwhelm nearby enemies."
        )

        mob = extract_mob_page(frog, animals_config(), mappings={})

        self.assertIn("knock an item", mob["summary"])
        self.assertIn("Frog Rain", mob["summary"])
        self.assertNotIn("Shipwrecked", mob["summary"])

    def test_extracts_multiple_quoted_prefabs_from_one_spawn_code_field(self):
        koalefant = page(
            9368,
            "Koalefant",
            """
{{Mob Infobox
|spawnCode = "koalefant_summer"<br>"koalefant_winter"
|health = {{DST|1000}}
}}
""",
        )

        mob = extract_mob_page(koalefant, animals_config(), mappings={})

        self.assertEqual(
            mob["identity"]["prefabCodes"],
            ["koalefant_summer", "koalefant_winter"],
        )

    def test_parses_live_infobox_picture_loot_and_primary_image(self):
        gem_deer = page(
            166761,
            "Gem Deer",
            """
{{Mob Infobox
|image = <gallery>
Red Gem Deer.png|Red
Blue Gem Deer.png|Blue
</gallery>
|spawnCode = "deer_red"<br>"deer_blue"
|health = {{DST|700}}
|drops = {{pic|32|Meat}} '''x2'''<br>{{pic|32|Red Gem}} '''x1''' (Red Gem Deer)<br>{{pic|32|Blue Gem}} '''x1''' (Blue Gem Deer)
}}
""",
        )

        mob = extract_mob_page(gem_deer, animals_config(), mappings={})

        self.assertEqual(mob["visual"]["sourceTitle"], "File:Red Gem Deer.png")
        self.assertEqual(
            [value["itemTitle"] for value in mob["loot"]["values"]],
            ["Meat", "Red Gem", "Blue Gem"],
        )
        self.assertEqual(
            [value["quantity"] for value in mob["loot"]["values"]],
            ["2", "1", "1"],
        )

    def test_parses_file_link_loot_chance_and_capture_condition(self):
        parrot = page(
            136122,
            "Parrot Pirate",
            """
{{Mob Infobox
|image = Parrot Pirate.png
|spawnCode = "parrot_pirate"
|drops = [[File:Morsel.png|24px|link=Morsel]] 50%<br>[[File:Crimson Feather.png|24px|link=Crimson Feather]] 50%<br>[[File:Parrot Pirate.png|24px|link=Parrot Pirate]] ([[File:Bird Trap.png|24px|link=Bird Trap]])
}}
""",
        )

        mob = extract_mob_page(parrot, animals_config(), mappings={})

        self.assertEqual(mob["loot"]["values"][0]["itemTitle"], "Morsel")
        self.assertEqual(mob["loot"]["values"][0]["chance"], "50%")
        self.assertEqual(mob["loot"]["values"][2]["itemTitle"], "Parrot Pirate")
        self.assertEqual(mob["loot"]["values"][2]["conditions"], "Bird Trap")
        self.assertEqual(mob["loot"]["values"][2]["method"], "conditional")


if __name__ == "__main__":
    unittest.main()
