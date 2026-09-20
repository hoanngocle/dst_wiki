"""Static dependency/asset contracts and real Lua 5.1 private combat helper tests."""
import json
import re
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mods/PhamNhanTuTien'
sys.path.insert(0,str(ROOT/'.superpowers/ttk-solo-integration/lua-runtime'))
from lupa.lua51 import LuaRuntime

class BossCombatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((MOD/'scripts/ttk_boss_combat_manifest.json').read_text())

    def test_lua51_and_namespaced_dependency_closure(self):
        lua=LuaRuntime()
        compile_=lua.eval('function(s,n) local f,e=loadstring(s,n); return e end')
        self.assertEqual([],self.manifest['unresolved'])
        for rel in self.manifest['lua']+['scripts/ttk_boss_util.lua','scripts/prefabs/ttk_boss_collectibles.lua']:
            text=(MOD/rel).read_text(encoding='utf8')
            self.assertIsNone(compile_(text,rel),rel)
            for dep in re.findall(r'require\s*\(?["\']([^"\']*ttk_[^"\']+)',text):
                self.assertTrue((MOD/'scripts'/(dep+'.lua')).exists(),(rel,dep))
            for dep in re.findall(r'["\'](SGttk_\w+)["\']',text):
                self.assertTrue((MOD/'scripts/stategraphs'/(dep+'.lua')).exists(),(rel,dep))

    def test_all_manifest_assets_exist_and_archives_are_sound(self):
        for rel in self.manifest['assets']:
            path=MOD/rel
            self.assertTrue(path.is_file(),rel)
            if path.suffix=='.zip':
                with ZipFile(path) as archive:self.assertIsNone(archive.testzip(),rel)
            if path.suffix=='.xml':
                for tex in re.findall(r'filename="([^"]+)"',path.read_text()):
                    self.assertTrue((path.parent/tex).is_file(),(rel,tex))

    def test_collectible_fallback_uses_existing_meat_animation(self):
        rows=LuaRuntime().execute((MOD/'scripts/ttk_boss_collectible_defs.lua').read_text(encoding='utf8'))
        for _,row in rows.items():
            if row[3]=='meat':
                self.assertEqual('raw',row[4],row[1])

    def test_shadow_weapon_symbol_build_is_declared(self):
        source=(MOD/'scripts/prefabs/ttk_boss_gongdeshadow.lua').read_text(encoding='utf8')
        self.assertIn('Asset("ANIM", Boss.ArtPath("anim/xd_tssyq.zip"))',source)
        self.assertIn('local mychars = {"xd_longtaizi"',source)

    def test_source_shared_cast_assets_and_sound_banks_are_loaded(self):
        main=(MOD/'main/ttk_boss_combat.lua').read_text(encoding='utf8')
        self.assertIn('Asset("ANIM", "anim/player_xd_staff.zip")',main)
        self.assertIn('Asset("ANIM", "anim/xd_zhf.zip")',main)
        self.assertIn('Asset("ANIM", "anim/xdswhs_tiaopi_fx.zip")',main)
        self.assertIn('Asset("SOUNDPACKAGE", "sound/xd_jfsnsound.fev")',main)
        sg=(MOD/'scripts/stategraphs/SGttk_jfsn.lua').read_text(encoding='utf8')
        self.assertIn('"xd_jfsnsound/xd_jfsnsound/jiao"',sg)
        collectibles=(MOD/'scripts/prefabs/ttk_boss_collectibles.lua').read_text(encoding='utf8')
        self.assertNotIn('and "feather"',collectibles)

    def utility(self):
        lua=LuaRuntime()
        lua.execute('''
            TUNING={ELECTRIC_DAMAGE_MULT=1.5,ELECTRIC_WET_DAMAGE_MULT=1}
            STRINGS={NAMES={}};TheWorld={ismastersim=false}
            function Prefab(name,fn,assets,deps) return {name=name,fn=fn} end
        ''')
        lua.globals().Boss=lua.execute((MOD/'scripts/ttk_boss_util.lua').read_text(encoding='utf8'))
        return lua

    def test_main_and_aux_roles_before_postinit_and_private_art(self):
        lua=self.utility()
        lua.execute('''
            local main=Boss.Prefab("ttk_deerclops_ziyun",function() return {} end).fn()
            local aux=Boss.Prefab("ttk_boss_deerclops_ziyun_aux",function() return {} end).fn()
            assert(not main._ttk_boss_auxiliary)
            assert(aux._ttk_boss_auxiliary)
            assert(Boss.Art("ttk_boss_sword_red")=="xd_sword_red")
            assert(Boss.ArtPath("anim/ttk_boss_qlch_charge.zip")=="anim/xd_qlch_charge.zip")
            assert(TUNING.XD_QLCH_HEALTH==nil)
            assert(Boss.TUNING.XD_QLCH_HEALTH==28000)
        ''')

    def test_damage_multipliers_and_neutral_owner_gate(self):
        lua=self.utility()
        lua.execute('''
            local inst={prefab="ttk_qxdx",_ttk_boss_main=true,components={}}
            inst.HasTag=function() return false end
            inst.components.combat={defaultdamage=100,damagemultiplier=2,
                playerdamagepercent=.5,pvp_damagemod=.5,externaldamagemultipliers={Get=function() return 1.5 end}}
            local target={components={},HasTag=function(_,tag) return tag=="player" end,GetIsWet=function() return true end}
            assert(Boss.Xd_CalcDamage(inst,100,target)==0)
            local helper={owner=inst,components={}}
            assert(Boss.IsDormant(helper))
            local projectile={owner=helper,components={}}
            assert(Boss.IsDormant(projectile))
            inst._ttk_boss_provoked=true
            assert(not Boss.IsDormant(helper))
            assert(Boss.Xd_CalcDamage(inst,100,target)==150)
            inst.components.electricattacks={}
            assert(Boss.Xd_CalcDamage(inst,100,target)==375)
            assert(Boss.Xd_CalcDamage(inst,100,target,2,1)==375)
        ''')

    def test_phase_save_preserves_refs_and_marks_lethal_transition(self):
        lua=self.utility()
        lua.execute('''
            TheWorld.ismastersim=true
            local inst={mode=1,components={knownlocations={}},sg={currentstate={name="idle"}}}
            inst.DoTaskInTime=function() end
            inst.OnSave=function(self,data) data.original=true;return {11,22} end
            inst.components.health={currenthealth=10,DoDelta=function(h,n) h.currenthealth=h.currenthealth+n end,
                Kill=function(h) h.currenthealth=0 end}
            inst=Boss.Prefab("ttk_ziyunboss",function() return inst end).fn()
            local data={};local refs=inst:OnSave(data)
            assert(data.original and refs[1]==11 and refs[2]==22)
            inst.components.health:DoDelta(-10)
            assert(inst._ttk_boss_phase_transition)
            inst.mode=3;inst._ttk_boss_phase_transition=nil
            data={};inst:OnSave(data)
            assert(data.ttk_boss_mode==3 and data.ttk_boss_phase_alive==false)
            assert(data.ttk_boss_phase_pending==false)
            inst.sg.currentstate.name="fly_down"
            data={};inst:OnSave(data)
            assert(data.ttk_boss_phase_pending)
        ''')

    def test_original_combat_graphs_and_standalone_owner_adaptation(self):
        for name in ['baihu','jfsn','qlch','qxdx','futu','spiderqueen','ziyunboss']:
            path=MOD/f'scripts/stategraphs/SGttk_{name}.lua'
            self.assertGreater(len(re.findall(r'\bState\s*{',path.read_text(encoding='utf8'))),5,name)
            prefab=(MOD/f'scripts/prefabs/ttk_{name}.lua').read_text(encoding='utf8')
            self.assertNotRegex(prefab,r'health\.OnSave\s*=')
        deer=(MOD/'scripts/prefabs/ttk_boss_deerclops_ziyun_aux.lua').read_text(encoding='utf8')
        self.assertIn('owner == nil or owner:IsValid()',deer)
        self.assertIn('Prefab("ttk_deerclops_ziyun"',deer)
        self.assertNotRegex(deer,r'health\.OnSave\s*=')
        stalker=(MOD/'scripts/prefabs/ttk_stalke_fuben.lua').read_text(encoding='utf8')
        self.assertNotRegex(stalker,r'health\.OnSave\s*=')
        qxdx=(MOD/'scripts/stategraphs/SGttk_qxdx.lua').read_text(encoding='utf8')
        self.assertNotIn('SpawnAt("ttk_boss_qxdx_npc"',qxdx)

    def test_rewarded_corpse_does_not_restore_phase_or_rebuild_helpers(self):
        lua=self.utility()
        lua.execute('''
            TheWorld.ismastersim=true
            for _,name in ipairs({"ttk_ziyunboss","ttk_qlch"}) do
                local tasks={}
                local inst={mode=3,components={knownlocations={},health={DoDelta=function() end,Kill=function() end}}}
                inst.DoTaskInTime=function(_,_,fn) tasks[#tasks+1]=fn end
                inst=Boss.Prefab(name,function() return inst end).fn()
                tasks={}
                inst:OnLoad({ttk_boss_rewarded=true,ttk_boss_mode=3,ttk_boss_phase_alive=true,
                    ttk_boss_combatstate={soldiers={{skillnum=1,health=.5}}}})
                assert(#tasks==0, "Final corpse must not revive or rebuild a phase helper")
            end
        ''')

if __name__=='__main__':unittest.main(verbosity=2)
