import unittest

from tools.extract.category_merge import merge_category_mobs


def _fact(section, key):
    return next(value for value in section["values"] if value["key"] == key)


def _mob(page_id=10, code="beefalo", damage=40):
    evidence = [{"source": "fandom", "pageId": page_id, "revisionId": 99, "game": "DST"}]
    empty = {"status": "none", "values": [], "reason": "source_has_no_values", "evidence": evidence}
    return {
        "schemaVersion": 1,
        "identity": {
            "id": "base_game:" + code,
            "name": "Beefalo",
            "englishName": "Beefalo",
            "primaryCode": code,
            "prefabCodes": [code],
            "sourcePageId": page_id,
            "sourceUrl": "https://dontstarve.fandom.com/wiki/Beefalo",
            "revisionId": 99,
        },
        "classification": {"type": "mob", "tags": ["Animals"], "game": "DST"},
        "visual": None,
        "summary": "A herd animal.",
        "stats": empty,
        "effects": empty,
        "combat": {
            "status": "known",
            "values": [{"key": "attack_damage", "label": "Damage", "value": damage, "unit": None, "evidence": evidence}],
            "reason": None,
            "evidence": evidence,
        },
        "movement": empty,
        "traits": empty,
        "loot": empty,
        "spawnsFrom": empty,
        "notes": {"status": "none", "values": [], "reason": "source_has_no_notes", "evidence": evidence},
        "variants": [{"code": code, "label": "Beefalo", "order": 0, "sprite": None}],
        "evidence": evidence,
    }


def _artifact(*pages):
    return {
        "schemaVersion": 1,
        "category": "animals",
        "game": "DST",
        "pages": list(pages),
        "discovery": {"seeds": []},
    }


class CategoryMergeTests(unittest.TestCase):
    def test_merges_by_code_without_changing_canonical_id(self):
        items = [{
            "id": "base_game:beefalo",
            "prefabId": "beefalo",
            "namespace": "base_game",
            "category": "mob",
            "name": "Bò Lai",
            "englishName": "Beefalo",
            "description": None,
            "sprite": None,
            "mob": None,
        }]

        result = merge_category_mobs(items, _artifact(_mob()), [])

        beefalo = result.items[0]
        self.assertEqual(beefalo["id"], "base_game:beefalo")
        self.assertEqual(beefalo["mob"]["classification"]["tags"], ["Animals"])
        self.assertEqual(result.audit["rows"][0]["action"], "merged")

    def test_runtime_fact_wins_over_wiki_presentation_value(self):
        items = [{
            "id": "base_game:beefalo", "prefabId": "beefalo", "namespace": "base_game",
            "category": "mob", "name": "Beefalo", "sprite": None, "mob": None,
        }]
        entities = [{
            "key": "base_game:beefalo", "prefab_id": "beefalo",
            "stats": [{"key": "attack_damage", "value": 34, "unit": None}],
        }]

        result = merge_category_mobs(items, _artifact(_mob(damage=40)), entities)
        fact = _fact(result.items[0]["mob"]["combat"], "attack_damage")

        self.assertEqual(fact["value"], 34)
        self.assertEqual(fact["evidence"][0]["source"], "runtime:normalized_catalog")

    def test_hides_duplicate_code_and_flags_empty_orphan(self):
        items = [
            {"id": "base_game:beefalo", "prefabId": "beefalo", "namespace": "base_game", "category": "mob", "name": "Beefalo", "sprite": {}, "mob": {}},
            {"id": "base_game:beefalo_copy", "prefabId": "beefalo", "namespace": "base_game", "category": "mob", "name": "Copy", "sprite": None, "mob": None},
            {"id": "base_game:unknown_mob", "prefabId": "unknown_mob", "namespace": "base_game", "category": "mob", "name": "Unknown", "sprite": None, "mob": None},
        ]

        result = merge_category_mobs(items, _artifact(_mob()), [])

        self.assertEqual([item["id"] for item in result.items].count("base_game:beefalo"), 1)
        rows = {row["recordId"]: row for row in result.audit["rows"]}
        self.assertEqual(rows["base_game:beefalo_copy"]["action"], "duplicate_hidden")
        self.assertIn("empty_details", rows["base_game:unknown_mob"]["flags"])
        self.assertIn("orphan_record", rows["base_game:unknown_mob"]["flags"])


if __name__ == "__main__":
    unittest.main()
