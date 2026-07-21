import unittest

from tools.extract.mob_details import build_mob_boss_audit, build_mob_details


CELESTIAL_GROUP = {
    "canonicalId": "base_game:alterguardian_phase3",
    "category": "boss",
    "members": [
        {"id": "base_game:alterguardian_phase1", "role": "phase", "order": 1},
        {"id": "base_game:alterguardian_phase2", "role": "phase", "order": 2},
        {"id": "base_game:alterguardian_phase3", "role": "phase", "order": 3},
        {
            "id": "base_game:alterguardian_phase3dead",
            "role": "post_defeat",
            "order": 4,
        },
    ],
}


def catalog_item(item_id: str, category: str, name: str) -> dict:
    return {
        "id": item_id,
        "prefabId": item_id.split(":", 1)[1],
        "name": name,
        "category": category,
        "sprite": None,
    }


def entity(item_id: str, entity_type: str, **values) -> dict:
    return {
        "key": item_id,
        "namespace": item_id.split(":", 1)[0],
        "prefab_id": item_id.split(":", 1)[1],
        "type": entity_type,
        "stats": [],
        "effects": [],
        "relations": [],
        "acquisition": [],
        **values,
    }


class MobDetailTests(unittest.TestCase):
    def fixtures(self):
        items = [
            catalog_item("base_game:alterguardian_phase1", "effect", "Phase 1"),
            catalog_item("base_game:alterguardian_phase2", "boss", "Phase 2"),
            catalog_item("base_game:alterguardian_phase3", "boss", "Celestial Champion"),
            catalog_item(
                "base_game:alterguardian_phase3dead", "structure", "Defeated Champion"
            ),
            catalog_item("base_game:alterguardianhat", "item", "Enlightened Crown"),
        ]
        entities = [
            entity("base_game:alterguardian_phase1", "boss"),
            entity("base_game:alterguardian_phase2", "boss"),
            entity(
                "base_game:alterguardian_phase3",
                "boss",
                stats=[
                    {"key": "max_health", "value": 14000, "unit": "hp"},
                    {
                        "key": "special_states",
                        "value": "summon, spin",
                        "unit": "state_names",
                    },
                ],
            ),
            entity("base_game:alterguardian_phase3dead", "structure"),
            entity(
                "base_game:alterguardianhat",
                "item",
                acquisition=[
                    {
                        "type": "drop",
                        "source": "base_game:alterguardian_phase3dead",
                        "chance": 1,
                        "min_count": 1,
                        "max_count": 1,
                        "method": "mine_post_defeat",
                        "conditions": {"loot_table": "alterguardian_phase3dead"},
                    }
                ],
            ),
        ]
        return items, entities

    def test_builds_phase_aware_stats_appearance_mechanics_and_rewards(self):
        items, entities = self.fixtures()

        details = build_mob_details(
            items,
            entities,
            {
                "base_game:alterguardian_phase3": {
                    "canonicalUrl": "https://dontstarve.wiki.gg/wiki/Celestial_Champion",
                    "summary": "The Celestial Champion is a Boss Monster.",
                    "sources": ["Được triệu hồi tại Mysterious Energy"],
                    "evidence": [
                        {"source": "data/crawled/dontstarve-wiki/pages.jsonl", "locator": "page:10"}
                    ],
                }
            },
            [],
            [CELESTIAL_GROUP],
        )["base_game:alterguardian_phase3"]

        self.assertEqual(details["appearance"]["status"], "known")
        self.assertEqual(
            details["appearance"]["sources"],
            ["Được triệu hồi tại Mysterious Energy"],
        )
        self.assertEqual(
            [variant["role"] for variant in details["variants"]],
            ["phase", "phase", "phase", "post_defeat"],
        )
        self.assertEqual(details["stats"][0]["label"], "Máu tối đa")
        self.assertEqual(details["stats"][0]["sourceVariant"], "base_game:alterguardian_phase3")
        self.assertEqual(details["mechanics"][0]["text"], "Trạng thái đặc biệt: summon, spin")
        self.assertEqual(details["lootStatus"], "known")
        self.assertEqual(
            details["loot"][0],
            {
                "item": {
                    "id": "base_game:alterguardianhat",
                    "name": "Enlightened Crown",
                    "sprite": None,
                },
                "minimum": 1,
                "maximum": 1,
                "chance": "100%",
                "method": "mine_post_defeat",
                "sourceVariant": "base_game:alterguardian_phase3dead",
                "lootTable": "alterguardian_phase3dead",
                "conditions": "Bảng rơi: alterguardian_phase3dead",
                "evidence": [],
            },
        )

    def test_unobserved_empty_loot_remains_unknown(self):
        items = [catalog_item("base_game:spider", "mob", "Spider")]
        entities = [entity("base_game:spider", "mob")]

        details = build_mob_details(items, entities, {}, [], [])

        self.assertEqual(details["base_game:spider"]["lootStatus"], "unknown")
        self.assertEqual(details["base_game:spider"]["loot"], [])

    def test_audit_covers_group_members_and_ordinary_mobs(self):
        items, entities = self.fixtures()
        items.append(catalog_item("base_game:spider", "mob", "Spider"))
        details = build_mob_details(items, entities + [entity("base_game:spider", "mob")], {}, [], [CELESTIAL_GROUP])

        audit = build_mob_boss_audit(items, details, [CELESTIAL_GROUP])

        self.assertEqual(audit["schema_version"], 1)
        self.assertEqual(audit["summary"], {"total": 5, "keep": 2, "merge": 3, "exclude": 0})
        self.assertEqual(
            [row["id"] for row in audit["rows"]],
            sorted(row["id"] for row in audit["rows"]),
        )


if __name__ == "__main__":
    unittest.main()
