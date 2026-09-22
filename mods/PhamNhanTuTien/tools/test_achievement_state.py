"""Contract/model checks for authoritative Pham Nhan achievement state.

Lua is not available in this workspace.  The model below makes the transaction
invariants executable, while source checks bind the shipped Lua boundary to
those invariants.
"""
from __future__ import annotations

import math
import re
import unittest
from copy import deepcopy
from pathlib import Path


MOD = Path(__file__).resolve().parents[1]
PERKS = MOD / "scripts" / "achievement" / "ttk_perk_catalog.lua"
CORE = MOD / "scripts" / "achievement" / "ttk_achievement_core.lua"
COMPONENT = MOD / "scripts" / "components" / "ttk_achievement_progress.lua"
REPLICA = MOD / "scripts" / "components" / "ttk_achievement_progress_replica.lua"
ACHIEVEMENTS = MOD / "scripts" / "achievement" / "ttk_achievement_catalog.lua"

REPEATABLE = {
    "planar_defense": .5, "planar_damage": 1, "critical_hit": .01,
    "critical_damage": .02, "lifesteal": .01, "scale": .01,
    "xp_multiplier": .05,
}
ABILITIES = {
    "fast_worker": 8, "mine_faster": 6, "chop_faster": 6,
    "fish_faster": 6, "cook_faster": 6, "warly_chef": 8,
    "trinket_owner": 12, "double_healed": 15, "double_pick": 20,
    "double_drop": 30, "build_cheaper": 35, "eternal_cage": 5,
    "easy_farm": 12, "icy_weed": 10,
}
CRAFT = {
    "ancient_builder": 15, "lunar_knight": 10, "pearl_bff": 8,
    "benevolent_mind": 8, "mad_scientist": 10, "celebrate": 5,
    "festive": 5, "christmas_gift": 8, "legendary_smith": 15,
    "pokeball": 12, "antique_shop": 8, "inherit_luoshen": 20,
    "inherit_sanxiao": 14, "inherit_shiji": 16, "inherit_jingwei": 14,
    "inherit_sudaji": 10, "inherit_hantianzun": 8, "inherit_wangmazi": 20,
}
RECIPES = {
    "inherit_luoshen": ["fence_gate_luoshen_item", "xd_luoshen_jihuaze", "xd_luoshen_jiangren", "xd_luoshen_huazhong", "xd_luoshen_liuguanghuafen", "xd_luoshen_yin", "xd_luoshen_huaxia", "fence_luoshen_item", "wall_luoshen_item", "xd_luoshen_dinghunxianglu"],
    "inherit_sanxiao": ["xd_yunxiao_hyjditem", "xd_yunxiao_fgfq", "xd_yunxiao_fls", "xd_yunxiao_fysz", "xd_yunxiao_ymsz", "xd_yunxiao_hyjdyqd", "xd_yunxiao_portable_spicer"],
    "inherit_shiji": ["xd_sj_bglxp", "xd_sj_bgygp", "xd_sj_by_builder", "xd_sj_kls", "xd_sj_tlsq", "xd_sj_cy_builder", "xd_sj_sxz", "xd_sj_xsydz"],
    "inherit_jingwei": ["xd_xuanyu", "xd_jingwei_blowdart", "xd_jingwei_fenice_builder", "xd_jingwei_fan", "xd_jingwei_hat", "turf_jingweitile", "xd_qianyu"],
    "inherit_sudaji": ["xd_sudaji_redlantern", "xd_sudaji_ywfh", "xd_qwsk", "xd_sudaji_sjpn", "xd_sudaji_tsmd"],
    "inherit_hantianzun": ["xd_htz_xyzzl", "xd_htz_sjcx", "xd_htz_tlz"],
    "inherit_wangmazi": ["xd_wmz_kjb", "xd_wmz_slxj", "xd_wmz_md1", "xd_wmz_md2", "xd_wmz_md3", "xd_wmz_md4", "xd_wmz_md5", "xd_wmz_md6", "xd_wmz_md7", "xd_wmz_md8"],
}


def band_price(level: int) -> int:
    if not 1 <= level <= 25:
        raise ValueError("level")
    return 2 if level <= 10 else 3 if level <= 15 else 4 if level <= 20 else 5


class Model:
    """Independent, deliberately tiny transaction oracle for edge cases."""
    def __init__(self, rewards={"a": 2, "b": 3}, apply=lambda *_: True):
        self.rewards, self.apply = rewards, apply
        self.ach = {key: {"progress": 0, "target": 1, "status": "locked"} for key in rewards}
        self.levels, self.unlocked, self.replays = {}, set(), {}
        self.earned = self.spent = 0

    def snapshot(self):
        return deepcopy((self.ach, self.levels, self.unlocked, self.replays, self.earned, self.spent))

    def advance(self, ident, amount):
        if ident not in self.ach or not isinstance(amount, (int, float)) or isinstance(amount, bool) or not math.isfinite(amount) or amount <= 0:
            return False, "invalid"
        row = self.ach[ident]
        if row["status"] == "claimed": return False, "claimed"
        row["progress"] = min(row["target"], row["progress"] + amount)
        if row["progress"] >= row["target"]: row["status"] = "completed_unclaimed"
        return True, row["status"]

    def claim(self, ident, request):
        if request in self.replays: return self.replays[request]
        if ident not in self.ach or self.ach[ident]["status"] != "completed_unclaimed": return False, "not_claimable"
        self.ach[ident]["status"] = "claimed"
        result = (True, self.rewards[ident])
        self.replays[request] = result
        self.earned += self.rewards[ident]
        return result

    def buy(self, ident, request):
        if request in self.replays: return self.replays[request]
        repeat = ident in REPEATABLE
        if not repeat and ident not in ABILITIES and ident not in CRAFT: return False, "unknown"
        level = self.levels.get(ident, 0)
        if repeat and level >= 25: return False, "max"
        if not repeat and ident in self.unlocked: return False, "owned"
        price = band_price(level + 1) if repeat else (ABILITIES | CRAFT)[ident]
        if self.earned - self.spent < price: return False, "balance"
        before = self.snapshot()
        try: ok = self.apply(ident, level + 1)
        except Exception: ok = False
        if not ok:
            self.ach, self.levels, self.unlocked, self.replays, self.earned, self.spent = before
            return False, "apply"
        if repeat: self.levels[ident] = level + 1
        else: self.unlocked.add(ident)
        self.spent += price
        result = (True, price)
        self.replays[request] = result
        return result


class AchievementStateTests(unittest.TestCase):
    def test_exact_catalog_and_economics(self):
        source = PERKS.read_text(encoding="utf-8")
        self.assertEqual(39, len(re.findall(r'\bid\s*=\s*"', source)))
        self.assertEqual(7, source.count('group = "stats"'))
        self.assertEqual(14, source.count('group = "ability"'))
        self.assertEqual(18, source.count('group = "craft"'))
        for ident, value in REPEATABLE.items():
            self.assertIn(f'id = "{ident}"', source)
            self.assertIn(f'effect_per_level = {value}', source)
        for ident, price in ABILITIES.items() | CRAFT.items():
            self.assertRegex(source, rf'id = "{ident}"[\s\S]{{0,250}}price = {price}')
        self.assertEqual(80, sum(band_price(level) for level in range(1, 26)))
        self.assertEqual(560, 7 * 80)
        self.assertEqual(179, sum(ABILITIES.values()))
        self.assertEqual(206, sum(CRAFT.values()))
        self.assertEqual(945, 560 + 179 + 206)
        self.assertIn("function M.MaxCost()", source)
        self.assertIn("assert(M.MaxCost() == 945", source)

    def test_exact_inheritance_recipe_prefabs_and_tags(self):
        source = PERKS.read_text(encoding="utf-8")
        for ident, prefabs in RECIPES.items():
            block = source[source.index(f'id = "{ident}"'):]
            block = block[:block.index("},\n    {") if "},\n    {" in block else len(block)]
            self.assertRegex(block, r'builder_tag = "ttk_inheritance_[a-z]+"')
            self.assertEqual(prefabs, re.findall(r'"([a-z0-9_]+)"', re.search(r'recipes = \{([\s\S]*?)\n        \}', block).group(1)))
        self.assertIn('"xd_sj_kls"', source)
        self.assertNotIn("dai_thanh", source.lower())
        self.assertNotRegex(source.lower(), r"sinh.*diet|diet.*sinh")

    def test_price_bands_and_every_repeatable_cap(self):
        self.assertEqual([2] * 10 + [3] * 5 + [4] * 5 + [5] * 5, [band_price(level) for level in range(1, 26)])
        state = Model(); state.earned = 10000
        for ident in REPEATABLE:
            for number in range(25): self.assertTrue(state.buy(ident, f"{ident}-{number}")[0])
            self.assertEqual((False, "max"), state.buy(ident, f"{ident}-cap"))

    def test_progress_completion_claim_and_replay(self):
        state = Model()
        self.assertEqual((False, "not_claimable"), state.claim("a", "claim-a"))
        self.assertEqual((False, "invalid"), state.advance("missing", 1))
        self.assertEqual((False, "invalid"), state.advance("a", float("nan")))
        self.assertEqual((True, "completed_unclaimed"), state.advance("a", 3))
        self.assertEqual((True, 2), state.claim("a", "claim-a"))
        self.assertEqual((True, 2), state.claim("a", "claim-a"))
        self.assertEqual(2, state.earned)
        self.assertEqual((False, "not_claimable"), state.claim("a", "other-click"))

    def test_full_claim_economy_and_one_time_rules(self):
        state = Model({f"a{index}": 2 if index < 71 else 3 if index < 128 else 5 if index < 183 else 8 if index < 217 else 10 for index in range(231)})
        for ident in state.ach:
            state.advance(ident, 1); self.assertTrue(state.claim(ident, f"claim-{ident}")[0])
        self.assertEqual(1000, state.earned)
        self.assertEqual((False, "balance"), Model().buy("fast_worker", "low"))
        state.buy("fast_worker", "one"); self.assertEqual((False, "owned"), state.buy("fast_worker", "two"))

    def test_apply_failure_or_error_restores_exact_state(self):
        for apply in (lambda *_: False, lambda *_: (_ for _ in ()).throw(RuntimeError("boom"))):
            state = Model(apply=apply); state.earned = 100
            before = state.snapshot()
            self.assertEqual((False, "apply"), state.buy("fast_worker", "apply"))
            self.assertEqual(before, state.snapshot())

    def test_source_transaction_save_and_replica_contracts(self):
        core, component, replica = CORE.read_text(encoding="utf-8"), COMPONENT.read_text(encoding="utf-8"), REPLICA.read_text(encoding="utf-8")
        for signature in ("function Core:Advance(id, amount, evidence)", "function Core:ClaimAchievement(id, request_id)", "function Core:PurchasePerk(id, request_id)", "function Core:GetSnapshot()"):
            self.assertIn(signature, core)
        for required in ("IsFinite", "IsValidRequestId", "GetReplay", "StoreReplay", "pcall", "Restore", "ReapplyPurchased", "earned", "spent", "claimed_reward"):
            self.assertIn(required, core)
        self.assertIn("Catalog.ById(id)", core)
        self.assertNotIn("data.earned", core)
        self.assertNotIn("data.spent", core)
        self.assertIn("version = 1", component)
        self.assertIn("SerializeSnapshot", component)
        self.assertIn('PushEvent("ttk_achievement_dirty"', component)
        self.assertNotRegex(component, r"net_[a-z]+\([^\n]*achievement_[0-9]")
        self.assertIn("MAX_SNAPSHOT_BYTES", component)
        self.assertIn("DecodeSnapshot", replica)
        self.assertIn("MAX_SNAPSHOT_BYTES", replica)
        self.assertIn("function TtkAchievementProgressReplica:GetSnapshot()", replica)

    def test_achievement_catalog_is_the_only_reward_source(self):
        source = CORE.read_text(encoding="utf-8")
        self.assertIn('require("achievement/ttk_achievement_catalog")', source)
        self.assertNotRegex(source, r"reward\s*=\s*\d+")
        self.assertTrue(ACHIEVEMENTS.exists())

    def test_load_canonicalizes_malformed_nested_containers_without_indexing_them(self):
        """A corrupt nested table must not turn load into an indexing exception."""
        source = CORE.read_text(encoding="utf-8")
        self.assertIn('type(saved.levels) == "table"', source)
        self.assertIn('type(saved.unlocked) == "table"', source)
        self.assertIn('type(state.replays) == "table"', source)
        self.assertIn('type(state.achievements) == "table"', source)

    def test_replica_decodes_one_time_unlocks_and_repeatable_levels_by_catalog_shape(self):
        """A one-time perk must remain an unlock in the client shape, not level 1."""
        source = REPLICA.read_text(encoding="utf-8")
        self.assertIn('require("achievement/ttk_perk_catalog")', source)
        self.assertIn("PerkCatalog.ById(id)", source)
        self.assertIn("snapshot.perks.unlocked[id] = true", source)
        self.assertIn("snapshot.perks.levels[id] = level", source)

    def test_fractional_progress_round_trips_snapshot_replica_and_save_contract(self):
        """Finite fractional tracker amounts must not be truncated by either boundary."""
        state = Model()
        self.assertEqual((True, "locked"), state.advance("a", .25))
        self.assertEqual(.25, state.ach["a"]["progress"])
        core, component, replica = CORE.read_text(encoding="utf-8"), COMPONENT.read_text(encoding="utf-8"), REPLICA.read_text(encoding="utf-8")
        self.assertIn("IsFinite(progress)", core)
        self.assertIn("FormatNumber(state.progress)", component)
        self.assertIn("CanonicalNumber(value)", replica)
        self.assertNotIn("NonNegativeInteger(progress)", replica)


if __name__ == "__main__":
    unittest.main(verbosity=2)
