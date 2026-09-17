import unittest
from pathlib import Path

from tools.extract.build_solo_leveling_data import build_data, parse_table, tuning_tables


ROOT = Path(__file__).resolve().parents[2]


class SoloLevelingDataTests(unittest.TestCase):
    def test_item_catalogue_removes_internal_entries_and_preserves_useful_objects(self):
        data = build_data(ROOT / 'solo_leveling')
        entries = next(g for g in data['groups'] if g['id'] == 'items')['entries']
        ids = {e['id'] for e in entries}
        for prefab in ('hh_true_damage', 'hh_ui_container', 'hh_turret', 'hh_daogam6_sword', 'hh_treasure_tally_b', 'hh_igris_shadow'):
            self.assertNotIn('item-' + prefab, ids)
        for prefab in ('hh_effect_stone', 'hh_effect_tally', 'hh_essence', 'hh_daogam', 'hh_daogam6', 'hh_suit_build', 'hh_corpse_igris', 'hh_dungeon_spider'):
            self.assertIn('item-' + prefab, ids)
        forms = next(e for e in entries if e['id'] == 'item-hh_daogam6')
        self.assertIn('Các dạng biến đổi: Kiếm, Rìu, Cuốc, Cúp và Xẻng.', forms['lines'])
        self.assertTrue(all(f'luck-potion-{i}' in ids for i in (1, 2, 3)))

    def test_visual_recipes_and_dungeon_products_use_actual_mod_icons(self):
        data = build_data(ROOT / "solo_leveling")
        groups = {g['id']: g for g in data['groups']}
        gem = next(e for e in groups['crafting']['entries'] if e['id'] == 'recipe-wb_enhancegem')
        self.assertEqual(gem['recipe']['amount'], 8)
        self.assertEqual([(i['prefab'], i['amount']) for i in gem['recipe']['ingredients']], [('opalpreciousgem', 1), ('hh_essence', 8)])
        self.assertTrue(gem['sprite']['src'].startswith('/solo-leveling/icons/'))
        potion = next(e for e in groups['dungeon-shop']['entries'] if e['id'] == 'dungeon-shop-dp_player_power')
        self.assertEqual(potion['shop']['prefab'], 'hh_thuoc_suc_manh')
        self.assertEqual(potion['shop']['currency'], 'Xu Hầm Ngục')
        self.assertIsNotNone(potion['shop']['sprite'])
        shadows = groups['shadows']['entries']
        self.assertTrue(all(e['sprite'] and len(e['talents']) == 6 for e in shadows))
        self.assertTrue(all(e.get('category') for g in data['groups'] for e in g['entries']))

    def test_parser_does_not_split_strings_or_function_bodies(self):
        value = parse_table('{name="A, B", run=function() if true then f(1, 2) end end, target=3, nested={a=true}}')
        self.assertEqual(value, {"name": "A, B", "target": 3, "nested": {"a": True}})

    def test_final_tuning_overrides_and_exp_remapping(self):
        source = (ROOT / "solo_leveling/main/hh_tunning.lua").read_text(encoding="utf-8-sig")
        tables = tuning_tables(source, {})
        self.assertEqual(tables["HH_MOB_EXP"]["hh_igris_dungeon"], 800)
        self.assertEqual(tables["HH_MOB_EXP"]["bee"], 5)
        self.assertEqual(tables["HH_MOB_RECOMMENDED_LEVEL"]["bee"], 5)
        self.assertEqual(tables["HH_DEATH_THRESHOLD"]["TRIGGER_HEALTH_RATIO"], .90)
        self.assertEqual(tables["HH_RULER"]["BASE_COST"], 100)
        self.assertEqual(tables["HH_HACANH_SHADOW"]["RECOVERY"], 480)
        self.assertEqual(tables["HH_SHADOW_PROGRESSION"]["GROWTH"]["hh_igris_shadow"]["HEALTH_PER_LEVEL"], .025)

    def test_all_daily_quests_and_actual_crafting_are_published(self):
        data = build_data(ROOT / "solo_leveling")
        groups = {group["id"]: group for group in data["groups"]}
        quests = groups["daily"]["entries"][1:]
        self.assertEqual(groups['daily']['title'], 'Daily Quest')
        self.assertEqual(len(quests), 60)
        self.assertEqual({entry["id"] for entry in quests}, {f"daily-{i}" for i in range(1, 61)})
        mining = next(entry for entry in quests if entry["id"] == "daily-2")
        self.assertIn("10 EXP", mining["lines"])
        recipes = groups["crafting"]["entries"]
        pond = next(entry for entry in recipes if entry["id"] == "recipe-hh_hac_nguyet_ho")
        self.assertIn("10 × Đá cẩm thạch (marble)", pond["lines"])
        gems = next(entry for entry in recipes if entry["id"] == "recipe-wb_enhancegem")
        self.assertIn("Nhận được: 8 × Đá Cường Hoá", gems["lines"])
        self.assertTrue(all(entry["source"] for group in data["groups"] for entry in group["entries"]))

    def test_configuration_does_not_apply_inactive_difficulty_branches(self):
        source = (ROOT / "solo_leveling/main/hh_config.lua").read_text(encoding="utf-8-sig")
        config = tuning_tables(source, {}, top_level_only=True)["HH_CHANCE_CONFIG"]
        self.assertEqual(config["MONSTER_EFFECT_NUM"]["base_num"], 2)
        self.assertEqual(config["MONSTER_EFFECT_NUM"]["boss_monster"], 7)
        self.assertEqual(config["MONSTER_ADD_EFFECT_DATE"], 10)
        self.assertEqual(config["DROP_EQUIP_CHANCE"]["common_monster"], .1)
        data = build_data(ROOT / "solo_leveling")
        settings = next(group for group in data["groups"] if group["id"] == "config")
        key_setting = next(entry for entry in settings["entries"] if entry["title"] == "Phím Tắt")
        self.assertIn("X", key_setting["lines"][-1])

    def test_wiki_tables_and_every_non_image_line_are_retained(self):
        data = build_data(ROOT / "solo_leveling")
        wiki = next(group for group in data["groups"] if group["id"] == "wiki")
        published = "\n".join("\n".join(entry["lines"]) + str(entry["tables"]) for entry in wiki["entries"])
        for line in (ROOT / "solo_leveling/Wiki.txt").read_text(encoding="utf-8-sig").splitlines():
            if line.startswith(("-", "  •")):
                self.assertIn(line.strip(), published)
        tables = [table for entry in wiki["entries"] for table in entry["tables"]]
        success = next(table for table in tables if "Tỉ Lệ Thành Công" in table["headers"])
        self.assertEqual(len(success["rows"]), 13)

    def test_guild_shop_keeps_purchase_fields_and_resolves_existing_icons(self):
        data = build_data(ROOT / "solo_leveling")
        shop = next(group for group in data["groups"] if group["id"] == "guild-shop")
        grass = next(entry for entry in shop["entries"] if entry["id"] == "guild-shop-1")["shop"]
        self.assertEqual((grass["rank"], grass["price"], grass["amount"], grass["stock"]), ("E", 2, 6, 10))
        self.assertEqual(grass["sprite"]["src"], "/assets/game/7fe94715ca23b6fb030cf809b42792625c64511198813952f2acd200927422fb.png")
        football = next(entry for entry in shop["entries"] if entry["id"] == "guild-shop-21")["shop"]
        self.assertEqual(football["prefab"], "footballhat")
        self.assertEqual(football["sprite"]["src"], "/assets/wiki/d20c77969773d5ec97540486873a1cb670abca53e3a585f0a01a088c0dde71e3.png")
        staff = next(entry for entry in shop["entries"] if entry["id"] == "guild-shop-74")["shop"]
        self.assertEqual(staff["sprite"]["src"], "/assets/wiki/540276069a613c7cbde635afc471bf6fa53777752a7cdb1afb0bee78e58eb07f.png")
        for entry in shop["entries"]:
            sprite = entry["shop"]["sprite"]
            if sprite:
                self.assertTrue((ROOT / "public" / sprite["src"].lstrip("/")).is_file())


if __name__ == "__main__":
    unittest.main()
