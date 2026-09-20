"""Guaranteed boss blueprints and knowledge-gated armor recipes."""
import unittest
from pathlib import Path
from test_phamnhan_boss_lifecycle import runtime

MOD=Path(__file__).resolve().parents[1]/'mods/PhamNhanTuTien'

class BlueprintTests(unittest.TestCase):
    def test_source_loot_does_not_add_second_blueprint(self):
        for boss,blueprint,start,end in [
            ('futu','ttk_xshj_blueprint','local loot =','for k = 1, 25'),
            ('ziyunboss','ttk_zcmj_blueprint','SetSharedLootTable(', 'local brain ='),
        ]:
            code=(MOD/'scripts/prefabs'/('ttk_'+boss+'.lua')).read_text(encoding='utf8')
            self.assertNotIn(blueprint,code[code.index(start):code.index(end)])
            self.assertIn(blueprint,code[:code.index(start)])

    def test_blueprints_drop_once_and_only_on_final_main_death(self):
        runtime().execute('''
local r=NewRegistry()
for key,blueprint in pairs({futu='ttk_xshj_blueprint',ziyunboss='ttk_zcmj_blueprint'}) do
 local def=defs.bosses[key];local b=Boss(key);assert(r:Register(key,b))
 if key=='ziyunboss' then
  b.mode=1;assert(not lifecycle.OnDeath(b,def));assert(b.drops[blueprint]==nil)
  b.mode=3
 end
 assert(lifecycle.OnDeath(b,def));assert(b.drops[blueprint]==1)
 assert(not lifecycle.OnDeath(b,def));assert(b.drops[blueprint]==1)
 local aux=Boss(key);aux._ttk_boss_auxiliary=true;aux.mode=3
 assert(not lifecycle.OnDeath(aux,def));assert(aux.drops[blueprint]==nil)
 local data={};b:OnSave(data);local loaded=Boss(key);loaded:OnLoad(data);loaded.mode=3
 assert(not lifecycle.OnDeath(loaded,def));assert(loaded.drops[blueprint]==nil)
end
''')

    def test_only_two_armor_recipes_require_blueprints(self):
        lua=runtime()
        lua.execute('''
GLOBAL=_G;TECH={NONE={},LOST={SCIENCE=10}}
STRINGS={NAMES={},RECIPE_DESC={},CHARACTERS={GENERIC={DESCRIBE={}}}}
PrefabFiles={};recipes={}
function RegisterInventoryItemAtlas() end
function Ingredient(name,count) return {name=name,count=count} end
function AddRecipe2(name,ingredients,tech,config,filters) recipes[name]={tech=tech,ingredients=ingredients,config=config} end
function AddComponentPostInit() end
''')
        lua.execute((MOD/'main/ttk_armor_set.lua').read_text(encoding='utf8'))
        lua.execute('''
assert(recipes.ttk_zcmj.tech==TECH.LOST)
assert(recipes.ttk_xshj.tech==TECH.LOST)
assert(recipes.ttk_yunxiao_ymsz.tech==TECH.NONE)
assert(not recipes.ttk_zcmj.config.nounlock and not recipes.ttk_xshj.config.nounlock)
''')

if __name__=='__main__':unittest.main()
