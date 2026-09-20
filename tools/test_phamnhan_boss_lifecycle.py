"""Reward and neutral-boss integration contracts, executed in Lua 5.1."""
import unittest
from test_phamnhan_boss_registry import make_lua


def runtime():
    lua = make_lua()
    lua.execute('''
defs=require('ttk_boss_defs'); lifecycle=require('ttk_boss_lifecycle')
function Boss(key)
 local b=Entity(defs.bosses[key].prefab);b.drops={};b.calls=0
 b.components.lootdropper.SpawnLootPrefab=function(_,name)
  b.drops[name]=(b.drops[name] or 0)+1; return Entity(name)
 end
 local function call() b.calls=b.calls+1;return true end
 b.components.combat={GetAttacked=call,SetTarget=call,DoAttack=call,CanTarget=call}
 b.components.sanityaura={GetAura=function() return -100 end}
 lifecycle.Install(b,defs.bosses[key]);return b
end
''')
    return lua


class LifecycleTests(unittest.TestCase):
    def test_main_death_pays_once_and_aux_never_pays(self):
        runtime().execute('''
local r=NewRegistry();local b=Boss('baihu');assert(r:Register('baihu',b))
assert(lifecycle.OnDeath(b,defs.bosses.baihu));assert(not lifecycle.OnDeath(b,defs.bosses.baihu))
assert(b.drops.ttk_boss_core_baihu==1 and b.drops.ttk_summon_baihu==1)
assert(b.drops.ttk_lingshi3>=2 and b.drops.ttk_lingshi3<=5)
local aux=Boss('baihu');aux._ttk_boss_auxiliary=true
assert(not lifecycle.OnDeath(aux,defs.bosses.baihu));assert(next(aux.drops)==nil)
''')

    def test_unique_phase_death_does_not_finish_registry(self):
        runtime().execute('''
local r=NewRegistry();local b=Boss('ziyunboss');assert(r:Register('ziyunboss',b));b.mode=1
assert(not lifecycle.OnDeath(b,defs.bosses.ziyunboss));assert(r.entries.ziyunboss.status=='alive')
assert(next(b.drops)==nil);b.mode=3
assert(lifecycle.OnDeath(b,defs.bosses.ziyunboss));assert(r.entries.ziyunboss.status=='dead')
assert(b.drops.ttk_lingshi4==10 and b.drops.ttk_lingshi3==100)
assert(b.drops.redgem==10 and b.drops.yellowgem==5)
assert(not lifecycle.OnDeath(b,defs.bosses.ziyunboss))
''')

    def test_unique_stays_neutral_until_player_or_owned_follower_attacks(self):
        runtime().execute('''
local r=NewRegistry();local b=Boss('qxdx');assert(r:Register('qxdx',b))
local c=b.components.combat;assert(not c:CanTarget());assert(not c:DoAttack())
assert(not c:SetTarget(Entity('pigman')));assert(b.components.sanityaura:GetAura()==0)
c:GetAttacked(Entity('lightning'));assert(not b._ttk_boss_provoked)
local p=Entity('wilson');p:AddTag('player');local follower=Entity('pigman')
follower.components.follower={leader=p};c:GetAttacked(follower)
assert(b._ttk_boss_provoked);assert(c:CanTarget());assert(c:DoAttack())
assert(b.components.sanityaura:GetAura()==-100)
local data={};b:OnSave(data);local loaded=Boss('qxdx');loaded:OnLoad(data)
assert(loaded._ttk_boss_provoked and loaded._ttk_boss_main)
''')

    def test_managed_boss_excluded_from_generic_lingshi_award(self):
        runtime().execute('''
package.loaded.ttk_defs={drop_min=2,drop_max=5}
package.loaded.ttk_enemy_rules={Classify=function() return 'boss' end}
local callback;TheWorld.ListenForEvent=function(_,event,fn) callback=fn end
require('ttk_loot').Install(TheWorld)
local b=Boss('baihu');callback(TheWorld,{inst=b});assert(next(b.drops)==nil)
local aux=Entity('aux');aux._ttk_boss_auxiliary=true
callback(TheWorld,{inst=aux});assert(not aux._ttk_death_paid)
b._ttk_boss_managed=nil;callback(TheWorld,{inst=b});assert(b.drops.ttk_lingshi3>=2)
''')


if __name__ == '__main__':
    unittest.main(verbosity=2)
