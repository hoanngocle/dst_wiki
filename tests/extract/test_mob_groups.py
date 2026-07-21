import json
import tempfile
import unittest
from pathlib import Path

from tools.extract.mob_groups import apply_mob_groups, load_mob_groups


def item(item_id: str, category: str) -> dict:
    prefab_id = item_id.split(":", 1)[1]
    return {
        "id": item_id,
        "prefabId": prefab_id,
        "name": prefab_id,
        "category": category,
        "sprite": None,
        "mob": None,
    }


def celestial_group() -> dict:
    return {
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


class MobGroupTests(unittest.TestCase):
    def test_loads_schema_one_groups_in_canonical_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "groups.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "groups": [
                            {"canonicalId": "tu_tien:z", "category": "mob", "members": []},
                            {"canonicalId": "base_game:a", "category": "boss", "members": []},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            groups = load_mob_groups(path)

        self.assertEqual(
            [group["canonicalId"] for group in groups],
            ["base_game:a", "tu_tien:z"],
        )

    def test_merges_members_into_existing_canonical_record(self):
        items = [
            item("base_game:alterguardian_phase1", "effect"),
            item("base_game:alterguardian_phase2", "boss"),
            item("base_game:alterguardian_phase3", "boss"),
            item("base_game:alterguardian_phase3dead", "structure"),
        ]
        items[2]["mob"] = {
            "variants": [
                {
                    "id": "base_game:alterguardian_phase1",
                    "sprite": {"src": "https://example.test/phase-1.png"},
                }
            ]
        }

        public, audit = apply_mob_groups(items, [celestial_group()])

        self.assertEqual(
            [value["id"] for value in public],
            ["base_game:alterguardian_phase3"],
        )
        canonical = public[0]
        self.assertEqual(canonical["category"], "boss")
        self.assertEqual(
            [value["id"] for value in canonical["mob"]["variants"]],
            [
                "base_game:alterguardian_phase1",
                "base_game:alterguardian_phase2",
                "base_game:alterguardian_phase3",
                "base_game:alterguardian_phase3dead",
            ],
        )
        self.assertEqual(
            [value["role"] for value in canonical["mob"]["variants"]],
            ["phase", "phase", "phase", "post_defeat"],
        )
        self.assertEqual(
            canonical["mob"]["variants"][0]["sprite"],
            {"src": "https://example.test/phase-1.png"},
        )
        self.assertEqual(
            [(row["id"], row["action"]) for row in audit],
            [
                ("base_game:alterguardian_phase1", "merge"),
                ("base_game:alterguardian_phase2", "merge"),
                ("base_game:alterguardian_phase3", "keep"),
                ("base_game:alterguardian_phase3dead", "merge"),
            ],
        )

    def test_rejects_member_in_multiple_groups(self):
        duplicate = celestial_group()
        duplicate["canonicalId"] = "base_game:alterguardian_phase2"

        with self.assertRaisesRegex(ValueError, "multiple mob groups"):
            apply_mob_groups(
                [
                    item("base_game:alterguardian_phase1", "boss"),
                    item("base_game:alterguardian_phase2", "boss"),
                    item("base_game:alterguardian_phase3", "boss"),
                    item("base_game:alterguardian_phase3dead", "structure"),
                ],
                [celestial_group(), duplicate],
            )

    def test_rejects_missing_group_member(self):
        with self.assertRaisesRegex(ValueError, "missing mob group member"):
            apply_mob_groups(
                [item("base_game:alterguardian_phase3", "boss")],
                [celestial_group()],
            )


if __name__ == "__main__":
    unittest.main()
