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
        "is_inventory_item": entity_type in {"item", "dependency", "inventory_item"},
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
                    "primaryImageTitle": "Celestial Champion Phase 3.png",
                    "variantImageTitles": {
                        "alterguardian_phase3": "Celestial Champion Phase 3.png",
                        "alterguardian_phase3dead": "Defeated Celestial Champion.png",
                    },
                    "mechanics": ["It summons Enlightening Snares."],
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
        self.assertEqual(
            details["variants"][2]["sprite"]["src"],
            "https://dontstarve.wiki.gg/wiki/Special:Redirect/file/Celestial_Champion_Phase_3.png",
        )
        self.assertEqual(details["stats"][0]["label"], "Máu tối đa")
        self.assertEqual(details["stats"][0]["sourceVariant"], "base_game:alterguardian_phase3")
        self.assertEqual(details["mechanics"][0]["text"], "Trạng thái đặc biệt: summon, spin")
        self.assertEqual(details["mechanics"][1]["text"], "It summons Enlightening Snares.")
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
                "evidence": [
                    {
                        "source": "public/data/catalog.json",
                        "locator": (
                            "base_game:alterguardianhat:acquisition:"
                            "base_game:alterguardian_phase3dead"
                        ),
                    }
                ],
            },
        )

    def test_unobserved_empty_loot_remains_unknown(self):
        items = [catalog_item("base_game:spider", "mob", "Spider")]
        entities = [entity("base_game:spider", "mob")]

        details = build_mob_details(items, entities, {}, [], [])

        self.assertEqual(details["base_game:spider"]["lootStatus"], "unknown")
        self.assertEqual(details["base_game:spider"]["loot"], [])

    def test_ignores_visual_effects_spawned_by_reward_callbacks(self):
        items, entities = self.fixtures()
        items.append(catalog_item("base_game:collapse_big", "effect", "Collapse FX"))
        entities.append(
            entity(
                "base_game:collapse_big",
                "effect",
                acquisition=[
                    {
                        "type": "drop",
                        "source": "base_game:alterguardian_phase3dead",
                        "chance": 1,
                        "min_count": 1,
                        "max_count": 1,
                        "method": "mine_post_defeat",
                        "conditions": {"callback": "dead_onwork"},
                    }
                ],
            )
        )

        detail = build_mob_details(items, entities, {}, [], [CELESTIAL_GROUP])[
            "base_game:alterguardian_phase3"
        ]

        self.assertNotIn(
            "base_game:collapse_big",
            [reward["item"]["id"] for reward in detail["loot"]],
        )

    def test_preserves_conditional_reward_method_from_normalized_conditions(self):
        items = [
            catalog_item("base_game:guardian", "boss", "Guardian"),
            catalog_item("base_game:ornament", "item", "Ornament"),
        ]
        entities = [
            entity("base_game:guardian", "boss"),
            entity(
                "base_game:ornament",
                "item",
                acquisition=[
                    {
                        "type": "drop",
                        "source": "base_game:guardian",
                        "chance": None,
                        "min_count": 1,
                        "max_count": 1,
                        "conditions": {
                            "method": "conditional",
                            "event": "WINTERS_FEAST",
                            "callback": "dropLootFn",
                        },
                    }
                ],
            ),
        ]

        reward = build_mob_details(items, entities, {}, [], [])["base_game:guardian"][
            "loot"
        ][0]

        self.assertEqual(reward["method"], "conditional")
        self.assertEqual(reward["conditions"], "Sự kiện: WINTERS_FEAST")

    def test_sorts_same_reward_with_known_and_unknown_chances(self):
        items = [
            catalog_item("base_game:guardian", "boss", "Guardian"),
            catalog_item("base_game:ornament", "item", "Ornament"),
        ]
        entities = [
            entity("base_game:guardian", "boss"),
            entity(
                "base_game:ornament",
                "item",
                acquisition=[
                    {
                        "type": "drop",
                        "source": "base_game:guardian",
                        "chance": None,
                        "conditions": {"event": "WINTERS_FEAST"},
                    },
                    {
                        "type": "drop",
                        "source": "base_game:guardian",
                        "chance": 0.25,
                        "conditions": {"loot_table": "guardian"},
                    },
                ],
            ),
        ]

        rewards = build_mob_details(items, entities, {}, [], [])["base_game:guardian"][
            "loot"
        ]

        self.assertEqual(len(rewards), 2)
        self.assertEqual({reward["chance"] for reward in rewards}, {None, "25%"})

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
        defeated = next(
            row
            for row in audit["rows"]
            if row["id"] == "base_game:alterguardian_phase3dead"
        )
        self.assertEqual(defeated["role"], "post_defeat")
        self.assertEqual(defeated["rewardCount"], 1)
        self.assertIn("missing_image", defeated["unresolvedReasons"])


if __name__ == "__main__":
    unittest.main()
