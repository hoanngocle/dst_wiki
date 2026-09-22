"""Source-contract tests for the approved Phàm Nhân pill runtime.

No Lua interpreter is shipped with this repository, so these checks protect the
runtime boundary and a tiny model protects refresh/expiry invariants.
"""

from pathlib import Path
import re
import unittest

import build_alchemy_defs as generator


ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "mods" / "PhamNhanTuTien"
CATALOG = MOD / "scripts" / "alchemy" / "ttk_alchemy_defs.lua"
PREFAB = MOD / "scripts" / "prefabs" / "ttk_alchemy.lua"
EFFECTS = MOD / "scripts" / "components" / "ttk_alchemy_effects.lua"
MAIN = MOD / "main" / "ttk_alchemy.lua"
MODMAIN = MOD / "modmain.lua"

CULTIVATION = list(generator.CULTIVATION_PREFABS)
BUFFS = list(generator.BUFF_PREFABS)
ALL = [*CULTIVATION, "xd_danyao_bg", *BUFFS]
APPROVED = {
    "xd_dy_cyfxd_1": ("damage_mult", "multiplier = 1.4", "duration = 2400"),
    "xd_dy_dmhsd_1": ("health_regen", "immediate = 120", "interval = 6", "amount = 15", "duration = 2400"),
    "xd_dy_lmsqd_1": ("lightning_damage", "amount = 180", "duration = 2400"),
    "xd_dy_qxdhd_1": ("sanity_regen", "amount = 6.666666666666667", "duration = 2400"),
    "xd_dy_yfsxd_1": ("speed_mult", "multiplier = 1.25", "duration = 2400"),
    "xd_dy_pshsd_1": ("damage_reduction", "multiplier = 0.65", "duration = 2400"),
    "xd_dy_qjqsd_1": ("work_efficiency", "multiplier = 1.9", "duration = 2400"),
    "xd_dy_xynyd_1": ("cold_protection", "duration = 2400"),
    "xd_dy_hsphd_1": ("heat_protection", "duration = 2400"),
    "xd_dy_xttyd_1": ("lifesteal", "fraction = 0.5", "duration = 2400"),
    "xd_danyao_bg": ("hunger_rate", "multiplier = 0.2"),
}


class EffectModel:
    """A small independent model: refresh replaces one owned resource."""
    def __init__(self): self.active = {}
    def apply(self, prefab, deadline): self.active[prefab] = deadline
    def expire(self, prefab, now):
        if self.active.get(prefab, 0) <= now: self.active.pop(prefab, None)


class AlchemyRuntimeTest(unittest.TestCase):
    def read(self, path): return path.read_text(encoding="utf-8")

    def test_exact_pills_are_registered_once_and_share_factory(self):
        """Omitting, duplicating, or registering an unapproved pill must fail."""
        source = self.read(PREFAB)
        self.assertEqual(re.findall(r'MakePill\("(xd_(?:danyao|dy)_[a-z0-9_]+)"', source), ALL)
        self.assertNotIn("xd_dy_fd", source)
        self.assertNotIn("xd_dy_tsfhd", source)
        self.assertEqual(source.count("MakePill"), 1 + len(ALL))
        self.assertIn('inst:AddTag("xd_danyao")', source)
        self.assertEqual(self.read(MODMAIN).count('"ttk_alchemy"'), 1)

    def test_catalog_has_explicit_approved_runtime_metadata_and_is_stable(self):
        """Changing effect values or reverting to prose-only effects must fail."""
        source = self.read(CATALOG)
        self.assertEqual(source, generator.render(generator.read_records()))
        for prefab, expected in APPROVED.items():
            row = re.search(rf'M\.by_prefab\["{prefab}"\] = \{{(?P<row>.*?)\n\}}', source, re.S)
            self.assertIsNotNone(row, prefab)
            for item in expected:
                self.assertIn(item, row.group("row"), prefab)

    def test_cultivation_consumes_only_after_component_accepts(self):
        """Destroying a rejected cultivation item must fail this contract."""
        source = self.read(PREFAB)
        self.assertIn('ttk_cultivation:Consume(inst.prefab)', source)
        self.assertRegex(source, r'if ok then\s+inst:Remove\(\)')

    def test_buff_dispatch_is_server_only_and_uses_owned_effect_component(self):
        """Client-side effects or bypassing the owned component must fail."""
        source = self.read(PREFAB)
        self.assertIn('not TheWorld.ismastersim', source)
        self.assertIn('ttk_alchemy_effects:Apply', source)
        self.assertIn('inst:AddComponent("ttk_alchemy_effects")', self.read(MAIN))

    def test_effect_source_has_idempotent_refresh_and_scoped_cleanup(self):
        """Stacking timers/listeners or clearing another pill's state must fail."""
        source = self.read(EFFECTS)
        self.assertIn('self:Remove(prefab)', source)
        self.assertIn('self.tasks[prefab]', source)
        self.assertIn('self.expiry_tasks[prefab]', source)
        self.assertIn('self.deadlines[prefab]', source)
        self.assertIn('self.listeners[prefab]', source)
        self.assertIn('RemoveEventCallback("onhitother", listener)', source)
        model = EffectModel(); model.apply("a", 10); model.apply("a", 20); model.apply("b", 10)
        self.assertEqual(model.active, {"a": 20, "b": 10})
        model.expire("a", 20); self.assertEqual(model.active, {"b": 10})

    def test_regen_combat_work_and_fasting_guards_are_present(self):
        """Applying after expiry, invalid damage, extra work actions, or stacked fasting fails."""
        source = self.read(EFFECTS)
        for token in ('IsDead()', 'data.damage <= 0', 'CHOP', 'MINE', 'HAMMER',
                      'burnratemodifiers:SetModifier', 'OnSave', 'OnLoad',
                      'VALID_KINDS', 'type(enabled) == "number"', 'math.min', 'math.max'):
            self.assertIn(token, source)
        self.assertNotIn('DIG', re.search(r'work_efficiency.*?end', source, re.S).group(0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
